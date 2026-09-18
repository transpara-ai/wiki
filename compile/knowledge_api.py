"""Private authenticated workflow HTTP adapter; no private response is cacheable."""
import json
import time
from urllib.parse import parse_qs,urlsplit

import authoring_profile
from ask_common import AskError,read_json
from knowledge_store import Conflict
from knowledge_workflow import Workflow
from knowledge_sources import Deferred


def actor(handler):
    config=authoring_profile.settings()
    key=authoring_profile.principal(handler.headers,config) if config else None
    if key: return key
    import ipaddress
    if ipaddress.ip_address(handler.client_address[0]).is_loopback:
        return 'local-curator'
    raise AskError('Sign in to attribute research and publication decisions.',401)


def response(handler,status,data):
    body=json.dumps(data,ensure_ascii=False).encode()
    handler.send_response(status)
    handler.send_header('Content-Type','application/json; charset=utf-8')
    handler.send_header('Cache-Control','no-store, private')
    handler.send_header('X-Content-Type-Options','nosniff')
    handler.send_header('Content-Length',str(len(body)))
    handler.end_headers(); handler.wfile.write(body)


def handle(handler,root):
    # Called after host validation for GET/POST. Grant check precedes all state reads.
    route=urlsplit(handler.path).path.removeprefix('/api/knowledge/').strip('/')
    if route in ('reader/save','reader/feedback','reader/saves'):
        return reader_action(handler,root,route)
    if not handler.require_authoring(): return
    try:
        workflow=Workflow(root); store=workflow.store
        route=urlsplit(handler.path).path.removeprefix('/api/knowledge/').strip('/')
        params=parse_qs(urlsplit(handler.path).query)
        principal=actor(handler)
        if handler.command=='GET':
            if route=='state':
                proposals=store.list('proposal')
                for p in proposals:
                    p['stale']=not store.current(p.get('frozen',{}).get('evidence') or [store.evidence(k) for k in p['evidence_ids']])
                    if p['state']!='published':
                        try: workflow.frozen(p)
                        except (ValueError,KeyError): p['stale']=True
                    p.pop('frozen',None)
                routes=json.loads((root/'compile/repository_routes.json').read_text())['routes']
                result={'monitors':store.list('monitor'),'proposals':proposals,
                        'investigations':[i for i in store.list('investigation') if i['owner']==principal],
                        'saved':[i for i in store.list('save') if i['owner']==principal],
                        'activity':store.list('activity')[:100],'jobs':store.jobs(),
                        'suggestions':[r['origin'].removeprefix('https://github.com/') for r in routes.values()],
                        'spaces':list(__import__('knowledge_structure').STRUCTURE.space_map),
                        'sections':{s.key:list(s.section_keys) for s in __import__('knowledge_structure').STRUCTURE.spaces},
                        'health':{'source_failures':sum(bool(m.get('error')) for m in store.list('monitor')),
                                  'semantic_debt':sum(p['state'] not in ('published','rejected') for p in proposals),
                                  'publication':store.list('publication')[:5]}}
                with store.connect() as db:
                    for m in result['monitors']:
                        m['retained_versions']=db.execute('SELECT COUNT(*) FROM discoveries WHERE origin=?',(m['id'],)).fetchone()[0]
                # Journal originals are recovery data, not browser status.
                result['health']['publication']=[{k:j[k] for k in ('id','state','at')} for j in result['health']['publication']]
            elif route=='evidence':
                result=store.evidence(params['id'][0]) if 'id' in params else {'evidence':store.search(params.get('q',[''])[0],params.get('origin',[None])[0])}
                if 'id' in params and params.get('raw')==['1']:
                    with store.connect() as db:
                        result['original']=db.execute('SELECT body FROM blobs WHERE hash=?',(result['hash'],)).fetchone()[0].decode('utf-8')
            elif route=='proposal':
                result=store.get('proposal',params['id'][0])
                store.put('metric',{'type':'review opened','proposal':result['id'],'owner':principal,'at':time.time()})
            elif route=='export':
                result={'version':1,'configs':[{k:v for k,v in m['config'].items() if k!='credential_ref'} for m in store.list('monitor')]}
            elif route=='metrics':
                result={'metrics':store.list('metric')}
            elif route=='explain':
                m=store.get('monitor',params['id'][0]); evidence=store.search(origin=m['id'])
                from knowledge_explain import explain
                result=explain(m,evidence)
            elif route=='history':
                if params.get('kind',[''])[0] not in ('monitor','proposal'): raise ValueError('Unsupported history kind')
                with store.connect() as db:
                    result={'history':[dict(r) for r in db.execute('SELECT revision,data,at FROM history WHERE kind=? AND id=? ORDER BY revision DESC',(params['kind'][0],params['id'][0]))]}
            elif route=='portable':
                result={'version':1,'articles':[],'provenance':[]}
                for p in store.list('proposal'):
                    if p['state']=='published':
                        result['articles'] += [{'slug':c['slug'],'markdown':workflow.article_path(c['slug']).read_text()} for c in p['changes']]
                        result['provenance'].append({'proposal':p['id'],'approval':p['approval'],'evidence':[store.evidence(k) for k in p['evidence_ids']]})
            else: raise KeyError('Unknown workflow endpoint')
        else:
            payload=read_json(handler,limit=1000000)
            if not isinstance(payload,dict): raise ValueError('JSON object required')
            # Quarantine all persisted request content before validation or echo.
            from ingest_ops import quarantine_payload
            quarantine_payload(json.dumps(payload).encode())
            if route.startswith('monitors/'):
                action=route.split('/')[1]
                if action in ('preview','import-preview'):
                    result={'job':store.enqueue('monitor-'+action,__import__('knowledge_store').identity('request'),payload,10)}
                else: result=workflow.monitor(action,{**payload,'_actor':principal})
            elif route=='submit': result=workflow.submission(payload,principal)
            elif route.startswith('research/'): result=workflow.investigate(route.split('/')[1],payload,principal)
            elif route.startswith('proposals/'): result=workflow.proposal_action(route.split('/')[1],payload,principal)
            elif route=='feedback':
                if payload.get('space') not in __import__('knowledge_structure').STRUCTURE.space_map: raise ValueError('Unknown space')
                result=store.put('activity',{'type':'feedback','actor':principal,'payload':payload,'status':'needs attention','at':time.time()})
            elif route=='save': result=store.put('save',{'owner':principal,'snapshot':payload,'at':time.time()})
            elif route=='jobs/retry':
                with store.connect() as db:
                    changed=db.execute("UPDATE jobs SET state='queued',attempts=0,available=?,error=NULL WHERE id=? AND state='failed'",(time.time(),payload['id'])).rowcount
                result={'requeued':bool(changed)}
            else: raise KeyError('Unknown workflow endpoint')
        response(handler,200,result)
    except AskError as exc: response(handler,exc.status,{'error':str(exc)})
    except Conflict as exc: response(handler,409,{'error':str(exc)})
    except Deferred as exc: response(handler,503,{'error':str(exc)})
    except KeyError: response(handler,404,{'error':'Workflow record or endpoint not found'})
    except ValueError as exc: response(handler,422,{'error':str(exc)})
    except Exception:
        response(handler,503,{'error':'Workflow unavailable or input refused. Prior evidence and published articles are retained.'})


def reader_action(handler,root,route):
    try:
        config=authoring_profile.settings()
        if handler.command!='GET' and not authoring_profile.mutation_allowed(handler.headers,config):
            raise AskError('Same-origin signed-in request required.',403)
        principal=authoring_profile.principal(handler.headers,config)
        if not principal: raise AskError('Sign in to save or offer feedback.',401)
        workflow=Workflow(root)
        if route=='reader/saves' and handler.command=='GET':
            result={'saved':[s for s in workflow.store.list('save') if s['owner']==principal]}
        elif route in ('reader/save','reader/feedback') and handler.command=='POST':
            data=read_json(handler,limit=100000)
            if not isinstance(data,dict) or set(data)!={'question','space','answer'}: raise AskError('Invalid saved answer.',400)
            kind='save' if route.endswith('/save') else 'activity'
            result=workflow.store.put(kind,{'owner':principal,'snapshot':data,'type':'reader feedback' if kind=='activity' else 'saved answer','status':'needs review' if kind=='activity' else 'saved','at':time.time()})
        else: raise AskError('Unsupported reader operation.',405)
        response(handler,200,result)
    except AskError as exc: response(handler,exc.status,{'error':str(exc)})
    except Exception: response(handler,503,{'error':'Unable to save this request.'})
