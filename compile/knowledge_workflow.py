"""Application operations shared by HTTP, the worker and scoped local integrations."""
import datetime as dt
import difflib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time

from knowledge_store import Store, Conflict, canonical, digest, identity, host_json
from knowledge_sources import Collector, Deferred, validate_config, extract
from knowledge_review import (SCHEMAS, PROFILES, WEIGHTS, Reviewer, validate, check_citations)
from knowledge_structure import STRUCTURE
from document_control import controlled, version_after, set_field, utc_date


class Workflow:
    def __init__(self, root, store=None, fetch=None, model=None):
        self.root=Path(root); self.store=store or Store(root)
        self.collector=Collector(self.store,fetch); self.model=model or self.call_model

    def provider_config(self):
        path=os.environ.get('KNOWLEDGE_HUB_REVIEW_CONFIG')
        if not path:
            raise Deferred('Host model configuration is required; review remains incomplete',delay=3600)
        value=host_json(path)
        if set(value)!={'author','reviewers'}:
            raise ValueError('Invalid host review configuration')
        return value

    def call_model(self, stage, context, spec):
        import ask
        from ask_common import MAX_CONTEXT
        if len(canonical(context))>MAX_CONTEXT:
            raise Deferred('Model context budget exceeded; narrow or split the bundle',delay=3600)
        payload={'question':'Review or synthesize this authorized knowledge workflow.', 'space':'workflow',
                 'provider':spec['provider'],'model':spec['model'],'stage':stage,'context':[context],'timeout':120}
        if 'effort' in spec: payload['effort']=spec['effort']
        # Interactive Ask reservations win admission over background work. Each call releases it.
        started=time.time()
        try:
            with ask.admission('knowledge-background',spec['provider']):
                result=ask.service('/complete',payload,timeout=120)
            self.store.put('metric',{'type':'model','stage':stage,'provider':spec['provider'],'model':spec['model'],'seconds':time.time()-started,'input_characters':len(canonical(context)),'output_characters':len(canonical(result)),'at':time.time()})
            return result
        except Exception:
            self.store.put('metric',{'type':'model failure','stage':stage,'provider':spec['provider'],'seconds':time.time()-started,'at':time.time()})
            raise

    def monitor(self, action, payload):
        if action=='add':
            c=validate_config(payload['config'])
            return self.store.put('monitor',{'config':c,'state':'disabled','preview':None,'checkpoint':{},'pending':0,'next_check':None})
        if action=='import-preview':
            configs=[validate_config(c,imported=True) for c in payload['configs']]
            if not 1<=len(configs)<=100: raise ValueError('Import between one and 100 sources')
            previews=[self.collector.preview(c) for c in configs]
            return self.store.put('import',{'configs':configs,'previews':previews,'expires':time.time()+3600})
        if action=='import':
            batch=self.store.get('import',payload['id'])
            if batch.get('consumed') or batch['expires']<time.time(): raise Conflict('Import preview expired or consumed')
            with self.store.connect() as db:
                db.execute('BEGIN IMMEDIATE')
                batch=self.store.get('import',payload['id'],db)
                if batch.get('consumed'): raise Conflict('Import already consumed')
                monitors=[self.store.put('monitor',{'config':c,'state':'disabled','preview':p,'checkpoint':{},'pending':0,'next_check':None},db=db)
                          for c,p in zip(batch['configs'],batch['previews'])]
                batch['consumed']=True; self.store.put('import',batch,batch['revision'],db)
            return {'monitors':monitors}
        m=self.store.get('monitor',payload['id'])
        if payload.get('revision')!=m['revision']: raise Conflict('Monitor changed; reload')
        if action=='edit':
            c=validate_config(payload['config']); previous=m['config']
            m.update(config=c,state='disabled',preview=None)
            # Preserve evidence and tracked identities, but invalidate in-flight scope and conditional caches.
            cp=m.get('checkpoint',{}); cp.pop('tasks',None); cp['cache']={}; cp['links']={}; cp['tracked']={}; cp['parents']={}; cp['members']={}; cp['page_members']={}; cp['backfilled']=False
            if (c['kind'],c['target'])!=(previous['kind'],previous['target']):
                m['previous_identity']=m.get('checkpoint',{}).get('identity')
                cp={}
            m['checkpoint']=cp
        elif action=='preview':
            m['preview']=self.collector.preview(m['config'])
        elif action=='enable':
            if not m.get('preview') or m['preview']['config_hash']!=digest(m['config']) or time.time()-m['preview']['at']>3600:
                raise Conflict('Preview this exact configuration before enabling')
            if m.get('audience_review_required'):
                if payload.get('audience_acknowledged') is not True: raise Conflict('Review the changed source access and audience before enabling')
                m['audience_decision']={'at':time.time(),'by':payload.get('_actor','local-operator'),'classification':m['config']['classification']}
            m.update(state='enabled',next_check=time.time(),error=None,audience_review_required=False)
        elif action in ('pause','retire'):
            m['state']='paused' if action=='pause' else 'retired'
        elif action=='run':
            if m['state']!='enabled': raise Conflict('Enable the previewed monitor before running')
            m['next_check']=time.time()
        else: raise ValueError('Unknown monitor action')
        return self.store.put('monitor',m,payload['revision'])

    def submission(self,payload,actor):
        text=payload['text']
        if not isinstance(text,str) or not text.strip() or len(text)>200000: raise ValueError('Submit nonempty UTF-8 text up to 200,000 characters')
        space=payload['space']
        if space not in STRUCTURE.space_map: raise ValueError('Unknown destination space')
        classification=payload.get('classification','internal')
        if classification not in STRUCTURE.classification_keys: raise ValueError('Unknown evidence classification')
        name=payload.get('name','Human submission')
        if not isinstance(name,str) or not 1<=len(name)<=200: raise ValueError('A short source name is required')
        source=payload.get('source') or 'submission:'+digest(text)
        if not isinstance(source,str) or len(source)>2048: raise ValueError('Invalid source identity')
        origin_id=payload.get('investigation') or identity('submission')
        if payload.get('investigation'): self.investigation_access(origin_id,actor)
        with self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            key,changed=self.store.capture(source,text.encode(),text,{'name':name,'classification':classification,'space':space,
                                          'origin':'human','submitted_by':actor},origin_id,db)
            job=self.store.enqueue('draft',digest([key,origin_id]),{'evidence':[key],'origin':origin_id,'space':space},50,db) if payload.get('propose',True) else None
        return {'evidence':key,'job':job,'changed':changed}

    def investigation_access(self,key,actor):
        i=self.store.get('investigation',key)
        if i['owner']!=actor: raise KeyError('Investigation not found')
        return i

    def investigate(self,action,payload,actor):
        if action=='start':
            if payload['space'] not in STRUCTURE.space_map or not isinstance(payload['question'],str) or not 2<=len(payload['question'])<=4000:
                raise ValueError('A question and registered space are required')
            from ingest_ops import quarantine_payload
            quarantine_payload(payload['question'].encode())
            return self.store.put('investigation',{'owner':actor,'question':payload['question'],'space':payload['space'],
                        'status':'active','findings':[],'answer':'','created':time.time()})
        i=self.investigation_access(payload['id'],actor)
        if action=='capture':
            from knowledge_sources import validate_url
            url=validate_url(payload['url'])
            c=validate_config({'name':'Research source','kind':'page','target':url,'steward':actor,'organization':'shared','space':i['space']})
            return {'job':self.store.enqueue('research-capture',identity('request'),{'investigation':i['id'],'config':c},10)}
        if action=='search':
            query=payload.get('query',i['question'])
            if not isinstance(query,str) or not 2<=len(query)<=2000: raise ValueError('Invalid research query')
            return {'job':self.store.enqueue('research-search',identity('request'),{'investigation':i['id'],'query':query},10)}
        if action=='run':
            return {'job':self.store.enqueue('research',identity('request'),{'investigation':i['id']},10)}
        if action=='propose':
            evidence=self.store.search(origin=i['id'])
            return {'job':self.store.enqueue('draft',digest([i['id'],[e['id'] for e in evidence]]),
                    {'origin':i['id'],'evidence':[e['id'] for e in evidence],'space':i['space']},30)}
        if action=='save':
            return self.store.put('save',{'owner':actor,'investigation':i['id'],'snapshot':i,'at':time.time()})
        if action=='close':
            i['status']='closed'; return self.store.put('investigation',i,i['revision'])
        raise ValueError('Unknown investigation action')

    def articles(self,space):
        from article_catalog import load_catalog
        return [a for a in load_catalog(root=self.root) if space in [p.split('/')[0] for p in a.placements] and not a.retired_on]

    def relevant(self,evidence,space):
        terms=set(re.findall(r'[a-z][a-z0-9-]{3,}', ' '.join(e['text'] for e in evidence).lower()))
        ranked=[]
        for a in self.articles(space):
            audiences={'internal':0,'company-internal':1,'public-candidate':2}
            if any(audiences.get(e['metadata'].get('classification','internal'),0)<audiences[a.classification] for e in evidence): continue
            score=len(terms & set(re.findall(r'[a-z][a-z0-9-]{3,}',(a.title+' '+a.body).lower())))
            dependencies=any(e['source'] in a.sources or e['metadata'].get('url') in a.sources for e in evidence)
            if score or dependencies:
                ranked.append((score+10000*dependencies,a))
        ranked.sort(key=lambda pair:(-pair[0],pair[1].slug))
        selected=[a for _,a in ranked[:12]]
        # Include explicit outgoing article links where capacity permits.
        all_articles={a.slug:a for a in self.articles(space)}
        for a in selected[:]:
            for slug in re.findall(r'\]\((?:\.\./)?([a-z0-9-]+)\.md(?:#[^)]*)?\)',a.body):
                if slug in all_articles and all_articles[slug] not in selected and len(selected)<12:
                    selected.append(all_articles[slug])
        return selected,len(ranked)>len(selected)

    def draft(self,payload):
        evidence=[self.store.evidence(k) for k in payload['evidence']]
        # Old queued evidence is replaced with current heads before synthesis.
        with self.store.connect() as db:
            keys=[db.execute('SELECT evidence FROM heads WHERE source=?',(e['source'],)).fetchone()[0] for e in evidence]
        evidence=[self.store.evidence(k) for k in dict.fromkeys(keys)]
        if not evidence: raise ValueError('No retained evidence to synthesize')
        candidates,limited=self.relevant(evidence,payload['space'])
        context={'evidence':evidence,'articles':[{'slug':a.slug,'title':a.title,'body':a.body} for a in candidates],
                 'coverage_limitations':'Dependency, full-text and link retrieval; at most 12 articles. Coverage may be incomplete.'}
        result=validate(SCHEMAS['draft'],self.model('draft',context,self.provider_config()['author']))
        check_citations(result,evidence)
        result['findings']=list({canonical(f):f for f in result['findings']}.values())
        proposal={'space':payload['space'],'origin':payload['origin'],'evidence_ids':[e['id'] for e in evidence],
                  **result,'state':'draft','review':None,'repair_count':0,'created':time.time(),
                  'coverage_incomplete':limited,'article_revisions':{},'placements':{}}
        for change in result['changes']:
            path=self.article_path(change['slug']); proposal['article_revisions'][change['slug']]=digest(path.read_bytes()) if path.exists() else None
            space=STRUCTURE.space_map[payload['space']]
            proposal['placements'][change['slug']]=space.key+'/'+('concept' if 'concept' in space.section_keys else space.sections[0].key)
        self.check_proposal(proposal,evidence)
        # Retry idempotency: stable grouped source/head identity.
        proposal['id']='proposal-'+digest([payload['space'], sorted((e['text_hash'],e['metadata'].get('classification','internal')) for e in evidence)])[:32]
        try:
            existing=self.store.get('proposal',proposal['id'])
            self.store.put('proposal-discovery',{'proposal':existing['id'],'origin':payload['origin'],'evidence_ids':proposal['evidence_ids'],'at':time.time()})
            return existing
        except KeyError: pass
        saved=self.store.put('proposal',proposal,0)
        self.store.enqueue('review',saved['id']+':'+str(saved['revision']),{'id':saved['id'],'revision':saved['revision']},80)
        return saved

    def article_path(self,slug):
        if not isinstance(slug,str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,149}',slug): raise ValueError('Invalid article slug')
        path=self.root/'wiki'/(slug+'.md')
        if path.is_symlink(): raise ValueError('Article symlinks are not writable')
        return path

    def check_proposal(self,p,evidence):
        from ingest_ops import quarantine_payload
        validate(SCHEMAS['draft'],{k:p[k] for k in ('findings','changes','coverage_limitations')})
        check_citations(p,evidence)
        if not self.store.current(evidence): raise Conflict('Source evidence changed; draft and review again')
        for item in evidence:
            for origin_id in self.store.evidence(item['id'])['origins']:
                if origin_id.startswith('monitor-'):
                    monitor=self.store.get('monitor',origin_id)
                    if monitor.get('audience_review_required'): raise Conflict('Source access changed; an audience review is required before publication')
        if len({c['slug'] for c in p['changes']})!=len(p['changes']): raise ValueError('Duplicate article changes')
        bumps=p.get('version_bumps',{})
        if not isinstance(bumps,dict) or set(bumps)-{c['slug'] for c in p['changes']} or any(v not in ('major','minor','patch') for v in bumps.values()):
            raise ValueError('Invalid document version changes')
        lookup={a.slug:a for a in self.articles(p['space'])}
        from ingest_server import check_new_article_absent,collision_key
        new_identities=set()
        for c in p['changes']:
            path=self.article_path(c['slug'])
            if not path.exists():
                check_new_article_absent(c['slug'],c['title'],wiki=self.root/'wiki')
                identities={collision_key(c['slug']),collision_key(c['title'])}
                if identities & new_identities: raise ValueError('Proposed article identities collide')
                new_identities.update(identities)
            placement=p.get('placements',{}).get(c['slug'])
            if placement and STRUCTURE.split_placement(placement)[0]!=p['space']: raise ValueError('Placement outside proposed space')
            revision=digest(path.read_bytes()) if path.exists() else None
            if revision!=p['article_revisions'].get(c['slug']): raise Conflict('Article changed; draft and review again')
            if path.exists() and c['slug'] not in lookup: raise ValueError('Article outside selected space or retired')
            # Internal evidence cannot be laundered into a wider publication profile.
            audiences={'internal':0,'company-internal':1,'public-candidate':2}
            article_audience=audiences[lookup[c['slug']].classification] if path.exists() else 0
            if any(audiences.get(e['metadata'].get('classification','internal'),0)<article_audience for e in evidence if e['id'] in c['evidence_ids']):
                raise ValueError('Evidence classification does not permit this article audience')
            if not c['body'].strip() or c['body'].lstrip().startswith('---') or '<' in c['body']:
                raise ValueError('Article body must be Markdown prose without frontmatter or HTML')
            quarantine_payload(c['body'].encode())
            markers=re.findall(r'\[evidence:([a-f0-9]{64})\]',c['body'])
            if not markers or set(markers)-set(c['evidence_ids']): raise ValueError('Article changes require valid evidence markers')
            # Disallow executable/remote image links; ordinary HTTPS citations and local wiki links remain supported.
            if re.search(r'!\[|\]\((?!https://|(?:\.\./)?[a-z0-9-]+\.md(?:#|\)))[^)]*\)',c['body']):
                raise ValueError('Unsupported article link')
            for target in re.findall(r'\]\((?:\.\./)?([a-z0-9-]+)\.md(?:#[^)]*)?\)',c['body']):
                if not self.article_path(target).exists() and target not in {x['slug'] for x in p['changes']}:
                    raise ValueError('Article link does not resolve')

    def article_document(self,p,c,original,date):
        """Render the same controlled bytes for review and publication."""
        from ingest_server import split_fm, fm_list
        space=STRUCTURE.space_map[p['space']]
        if original:
            fm,_,_=split_fm(original)
        else:
            placement=p.get('placements',{}).get(c['slug'],space.key+'/'+('concept' if 'concept' in space.section_keys else space.sections[0].key))
            fm='\n'.join(['entity: '+json.dumps(c['title']),'org: '+space.steward,'primary_placement: '+placement,
                         'placements: ['+placement+']','classification: internal','tier: concept',
                         'status: reviewed','source_authority: [mixed-provenance]'])
        version=version_after(fm,p.get('version_bumps',{}).get(c['slug'],'minor'))
        fm=controlled(fm,identifier='TAI-WIKI-'+c['slug'].upper(),title=c['title'],kind='article',
                      date=date,owner=space.steward,version=version,existing=bool(original))
        for field,value in (('status','reviewed'),('reviewed_on',date),('last_compiled',date)):
            fm=set_field(fm,field,value)
        refs=fm_list(fm,'raw_documents')
        refs+=['raw/inbox/discovery/'+k+'.md' for k in c['evidence_ids'] if 'raw/inbox/discovery/'+k+'.md' not in refs]
        fm=re.sub(r'^raw_documents:[^\n]*(?:\n[ \t]+-[^\n]*)*\n?', '',fm,flags=re.M).rstrip()
        fm+='\nraw_documents:\n'+''.join('  - '+r+'\n' for r in refs)
        body=re.sub(r'\[evidence:([a-f0-9]{64})\]',r'[captured evidence](../raw/inbox/discovery/\1.md)',c['body'])
        return '---\n'+fm+'---\n\n'+body+'\n'

    def frozen(self,p):
        evidence=[self.store.evidence(k) for k in p['evidence_ids']]
        for item in evidence: item.pop('origins',None)
        self.check_proposal(p,evidence)
        profiles={}
        for org,profile in PROFILES.items():
            path=self.root/profile['reference']; text=path.read_text() if path.exists() else profile['purpose']
            profiles[org]={**profile,'text':text,'revision':digest(text),'weights':WEIGHTS[org]}
        articles=[]
        date=utc_date(p.get('document_date',p.get('created',max(e['captured'] for e in evidence))))
        for c in p['changes']:
            path=self.article_path(c['slug']); original=path.read_text() if path.exists() else ''
            document=self.article_document(p,c,original,date)
            articles.append({'slug':c['slug'],'revision':p['article_revisions'][c['slug']], 'original':original,
                             'proposed':c,'document':document,'placement':p.get('placements',{}).get(c['slug']),'diff':'\n'.join(difflib.unified_diff(original.splitlines(),document.splitlines(),fromfile=c['slug'],tofile=c['slug']))})
        return {'evidence':evidence,'findings':p['findings'],'articles':articles,'profiles':profiles,'rubric_version':1,
                'coverage_limitations':p['coverage_limitations']}

    def review(self,key,revision):
        p=self.store.get('proposal',key)
        if p['revision']!=revision or p['state'] in ('published','rejected'): return p
        frozen=self.frozen(p)
        try:
            config=self.provider_config(); result=Reviewer(self.model,config['reviewers']).run(frozen)
        except (Deferred,ValueError):
            result={'state':'Review incomplete','errors':['Two configured, available model families are required'],'frozen_hash':digest(frozen),'scores':[]}
        p.update(review=result,state=result['state'],frozen=frozen)
        saved=self.store.put('proposal',p,revision)
        # One bounded repair cycle; original assessments remain in immutable history.
        if result['state'] in ('Needs a decision','Needs more evidence') and p['repair_count']==0:
            self.store.enqueue('repair',key,{'id':key,'revision':saved['revision']},85)
        return saved

    def repair(self,payload):
        p=self.store.get('proposal',payload['id'])
        if p['revision']!=payload['revision'] or p['repair_count']!=0: return
        result=validate(SCHEMAS['draft'],self.model('draft',{'frozen':p['frozen'],'review':p['review'],'instruction':'One bounded repair. Preserve uncertainties.'},self.provider_config()['author']))
        p.update(result); p.update(repair_count=1,state='draft',review=None)
        for c in p['changes']:
            path=self.article_path(c['slug'])
            p['article_revisions'].setdefault(c['slug'],digest(path.read_bytes()) if path.exists() else None)
        self.check_proposal(p,[self.store.evidence(k) for k in p['evidence_ids']])
        saved=self.store.put('proposal',p,payload['revision'])
        self.store.enqueue('review',saved['id']+':'+str(saved['revision']),{'id':saved['id'],'revision':saved['revision']},80)

    def proposal_action(self,action,payload,actor):
        p=self.store.get('proposal',payload['id'])
        if p['revision']!=payload['revision']: raise Conflict('Proposal changed; inspect the latest diff')
        if p['state']=='published': raise Conflict('Published proposals are immutable')
        if action=='edit':
            p.update({k:payload[k] for k in ('findings','changes','coverage_limitations')})
            p.update(state='draft',review=None,repair_count=0)
            if 'placements' in payload: p['placements']=payload['placements']
            if 'version_bumps' in payload: p['version_bumps']=payload['version_bumps']
            p['document_date']=time.time()
            for c in p['changes']:
                path=self.article_path(c['slug'])
                p['article_revisions'].setdefault(c['slug'],digest(path.read_bytes()) if path.exists() else None)
            self.check_proposal(p,[self.store.evidence(k) for k in p['evidence_ids']])
        elif action=='review':
            self.store.enqueue('review',p['id']+':'+str(p['revision']),{'id':p['id'],'revision':p['revision']},30)
            return p
        elif action in ('defer','reject','request-revision'):
            p.update(state={'defer':'deferred','reject':'rejected','request-revision':'revision requested'}[action],decision={'actor':actor,'reason':payload.get('reason',''),'at':time.time()})
        elif action=='approve':
            return self.publish(p,actor,payload.get('manual_reason'))
        else: raise ValueError('Unknown proposal action')
        return self.store.put('proposal',p,payload['revision'])

    def publish(self,p,actor,manual_reason=None,builder=None):
        from ingest_server import wiki_write_lock
        from site_publication import staged_publication
        from ingest_ops import atomic_write_text, ledger_preflight, load_edge_states
        if not p['changes']: raise ValueError('There are no article changes to publish')
        with wiki_write_lock():
            self.recover_publications()
            ledger_preflight(self.root/'compile/ingest-ledger.jsonl')
            load_edge_states(self.root/'compile/edge-states.json')
            latest=self.store.get('proposal',p['id'])
            if latest['revision']!=p['revision']: raise Conflict('Proposal changed before approval')
            frozen=self.frozen(p)
            if not manual_reason and (not p.get('review') or p['review']['state']!='Ready for approval' or p['review']['frozen_hash']!=digest(frozen)):
                raise Conflict('Current complete review required, or record a manual review decision')
            if manual_reason and (not isinstance(manual_reason,str) or len(manual_reason.strip())<20):
                raise ValueError('Manual review requires an explicit substantive rationale')
            approval={'actor':actor,'at':time.time(),'frozen_hash':digest(frozen),'manual_reason':manual_reason,'proposal_revision':p['revision']}
            originals={}; replacements={}; manifests=[]; ledger_rows=[]
            timestamp=dt.datetime.fromtimestamp(approval['at'],dt.timezone.utc).isoformat()
            for e in frozen['evidence']:
                rel='raw/inbox/discovery/'+e['id']+'.md'; path=self.root/rel
                originals[rel]=path.read_text() if path.exists() else None
                # Published snapshots are immutable; later observation times stay in private state.
                fm=controlled('status: retained\nclassification: '+e['metadata'].get('classification','internal'),
                              identifier='TAI-EVIDENCE-'+e['id'],title='Captured evidence',kind='evidence',
                              date=utc_date(e['captured']),owner=STRUCTURE.space_map[p['space']].steward,version='1.0.0')
                replacements[rel]=originals[rel] if originals[rel] is not None else '---\n'+fm+'\n---\n\n# Captured evidence\n\n'+canonical({k:e[k] for k in ('id','source','hash','captured','metadata')})+'\n\n'+e['text']
            documents={a['slug']:a['document'] for a in frozen['articles']}
            for c in p['changes']:
                rel='wiki/'+c['slug']+'.md'; path=self.root/rel
                original=path.read_text() if path.exists() else None; originals[rel]=original
                replacements[rel]=documents[c['slug']]
                for evidence_id in c['evidence_ids']:
                    source_ref='raw/inbox/discovery/'+evidence_id+'.md'
                    manifests.append({'ingested_at':timestamp,'mode':'reviewed-discovery','target_slug':c['slug'],'source_path':source_ref,
                        'sha256':digest(replacements[source_ref].encode()),'original_name':evidence_id+'.md','note':'Accepted bundle '+p['id'],'supersedes':''})
                ledger_rows.append({'ts':timestamp,'operation':'add','slug':c['slug'],'sources':['raw/inbox/discovery/'+k+'.md' for k in c['evidence_ids']],
                                    'created':original is None,'rebuild':'ok'})
            journal=self.store.put('publication',{'proposal':p['id'],'state':'preparing','originals':originals,'approval':approval,'manifest_rows':manifests,'ledger_rows':ledger_rows,'at':time.time()})
            stage=Path(tempfile.mkdtemp(prefix='dist-reviewed-',dir=self.root))
            try:
                for rel,text in replacements.items():
                    path=self.root/rel; path.parent.mkdir(parents=True,exist_ok=True); atomic_write_text(path,text)
                if builder:
                    builder(stage)
                else:
                    result=subprocess.run([sys.executable,str(self.root/'compile/build_site.py'),'--profile','authoring-local','--output',str(stage)],
                                          cwd=self.root,capture_output=True,timeout=240)
                    if result.returncode: raise ValueError('Publication validation failed; previous articles and served site retained')
                from shadow_verify import assert_links_resolve
                assert_links_resolve(stage)
                (stage/'knowledge-publication.json').write_text(canonical({'id':journal['id']}))
                # Prevent capture or edits from slipping between final validation and directory exchange.
                with self.store.connect() as db:
                    db.execute('BEGIN IMMEDIATE')
                    current=self.store.get('proposal',p['id'],db)
                    if current['revision']!=p['revision']: raise Conflict('Proposal changed during build')
                    for rel,expected_text in replacements.items():
                        if (self.root/rel).read_text()!=expected_text: raise Conflict('Staged article or provenance changed during build')
                    for e in frozen['evidence']:
                        monitor_rows=db.execute("SELECT data FROM objects WHERE kind='monitor' AND id IN (SELECT origin FROM discoveries WHERE evidence=?)",(e['id'],)).fetchall()
                        if any(json.loads(row[0]).get('audience_review_required') for row in monitor_rows):
                            raise Conflict('Source access changed during build; audience review required')
                        if (db.execute('SELECT evidence FROM heads WHERE source=?',(e['source'],)).fetchone()[0]!=e['id']
                            or db.execute('SELECT MAX(id) FROM observations WHERE source=?',(e['source'],)).fetchone()[0]!=e['observed_revision']):
                            raise Conflict('Evidence changed during build')
                    with staged_publication(self.root/'dist',preserve=('deploy-status.json','inflight.json')) as target:
                        shutil.copytree(stage,target,dirs_exist_ok=True)
                    self.finish_publication_audit(journal)
                    p.update(state='published',approval=approval,publication=journal['id'])
                    saved=self.store.put('proposal',p,p['revision'],db)
                    self.store.put('metric',{'type':'publication','proposal':p['id'],'manual_override':bool(manual_reason),'rework':p['repair_count'],'queue_seconds':time.time()-p.get('created',approval['at']),'at':time.time()},db=db)
                    journal['state']='published'; self.store.put('publication',journal,journal['revision'],db)
                return saved
            except Exception:
                self.recover_publications()
                raise
            finally:
                shutil.rmtree(stage,ignore_errors=True)
                (stage.parent/(stage.name+'-publish.lock')).unlink(missing_ok=True)

    def finish_publication_audit(self,journal):
        """Append existing manifest/operation formats only after successful exchange; replay safely."""
        import hashlib
        from ingest_ops import ledger_preflight,append_ledger,write_manifest_shard
        ledger_path=self.root/'compile/ingest-ledger.jsonl'
        existing=ledger_preflight(ledger_path)
        for row in journal.get('manifest_rows',[]):
            suffix=hashlib.sha256(json.dumps(row,sort_keys=True).encode()).hexdigest()[:12]
            matches=list((self.root/'raw/inbox/manifest.d').glob('*-'+suffix+'.jsonl'))
            if not any(json.loads(path.read_text())==row for path in matches):
                write_manifest_shard(self.root,row,row['ingested_at'])
        for row in journal.get('ledger_rows',[]):
            if row not in existing:
                append_ledger(ledger_path,row);existing.append(row)

    def recover_publications(self):
        from ingest_ops import atomic_write_text
        marker=self.root/'dist/knowledge-publication.json'
        try: served=json.loads(marker.read_text())['id']
        except (OSError,ValueError,KeyError): served=None
        for j in self.store.list('publication'):
            if j['state']!='preparing': continue
            if served==j['id']:
                self.finish_publication_audit(j)
                p=self.store.get('proposal',j['proposal'])
                p.update(state='published',approval=j['approval'],publication=j['id'])
                self.store.put('proposal',p,p['revision']); j['state']='published'
            else:
                for rel,original in j['originals'].items():
                    path=self.root/rel
                    if original is None: path.unlink(missing_ok=True)
                    else: atomic_write_text(path,original)
                j['state']='rolled back'
            self.store.put('publication',j,j['revision'])

    def execute(self,job):
        payload=job['payload']; kind=job['kind']
        if kind in ('monitor-preview','monitor-import-preview'):
            result=self.monitor(kind.removeprefix('monitor-'),payload)
            self.store.put('activity',{'type':kind,'result':result,'status':'preview complete','at':time.time()})
        elif kind=='scan': self.collector.scan(payload['id'])
        elif kind=='draft': self.draft(payload)
        elif kind=='review': self.review(payload['id'],payload['revision'])
        elif kind=='repair': self.repair(payload)
        elif kind=='research-capture':
            i=self.store.get('investigation',payload['investigation']); c=payload['config']
            _,h,raw,url=self.collector.request(c['target'],c,allowed={__import__('knowledge_sources').origin(c['target'])})
            text,status=extract(raw,h.get('content-type',''))
            self.store.capture(url,raw,text,{'url':url,'extraction':status,'classification':'internal','space':i['space']},i['id'])
        elif kind=='research-search':
            self.research_search(payload)
        elif kind=='research':
            i=self.store.get('investigation',payload['investigation'])
            evidence=self.store.search(origin=i['id'])
            # Existing retained material can supplement explicitly captured research, within the selected space.
            evidence += [e for e in self.store.search(i['question']) if e['metadata'].get('space')==i['space'] and e['id'] not in {x['id'] for x in evidence}]
            if not evidence: raise ValueError('Capture sources before running research')
            result=validate(SCHEMAS['research'],self.model('research',{'question':i['question'],'evidence':evidence},self.provider_config()['author']))
            check_citations(result,evidence)
            i['findings']+= [f for f in result['findings'] if f not in i['findings']]
            i.update(answer=result['answer'],open_questions=result['open_questions'])
            self.store.put('investigation',i,i['revision'])
        else: raise ValueError('Unsupported job kind')


    def research_search(self,payload):
        from urllib.parse import urlencode,urlsplit,urlunsplit
        from knowledge_sources import validate_url,origin
        setting=os.environ.get('KNOWLEDGE_HUB_RESEARCH_SEARCH')
        if not setting: raise Deferred('Requested web research requires an approved host search adapter; capture specific URLs in the meantime',delay=3600)
        spec=host_json(setting)
        if set(spec)-{'endpoint','credential_ref','allowed_origins'} or 'endpoint' not in spec: raise ValueError('Invalid host search adapter')
        endpoint=validate_url(spec['endpoint']); split=urlsplit(endpoint)
        query=urlencode({'q':payload['query']})
        url=urlunsplit((split.scheme,split.netloc,split.path,split.query+('&' if split.query else '')+query,''))
        i=self.store.get('investigation',payload['investigation'])
        c=validate_config({'name':'Requested research search','kind':'page','target':url,'steward':i['owner'],'organization':'shared','space':i['space'],'credential_ref':spec.get('credential_ref','')})
        _,headers,raw,_=self.collector.request(url,c,allowed={origin(endpoint)})
        results=json.loads(raw)
        if not isinstance(results,dict) or not isinstance(results.get('results'),list): raise ValueError('Search adapter must return a results array')
        self.store.capture(url,raw,raw.decode('utf-8'),{'url':url,'type':'search discovery, not primary evidence','classification':'internal','space':i['space']},i['id'])
        failures=[]
        for result in results['results'][:5]:
            try:
                target=validate_url(result['url'])
                if spec.get('allowed_origins') and origin(target) not in spec['allowed_origins']: continue
                page={**c,'target':target,'credential_ref':''}
                _,h,body,actual=self.collector.request(target,page,allowed={origin(target)})
                text,status=extract(body,h.get('content-type',''))
                self.store.capture(actual,body,text,{'url':actual,'type':'research search result','extraction':status,'classification':'internal','space':i['space']},i['id'])
            except (Deferred,ValueError,KeyError): failures.append('A discovered source could not be captured')
        self.store.put('activity',{'type':'research search','owner':i['owner'],'investigation':i['id'],'status':'Search captured'+(' with incomplete sources' if failures else ''),'errors':failures,'at':time.time()})
