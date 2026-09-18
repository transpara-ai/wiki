"""Bounded read-only connectors. Transport is injectable; production DNS is pinned."""
from contextlib import contextmanager
import datetime as dt
import email.utils
import fcntl
import fnmatch
import http.client
from html.parser import HTMLParser
import ipaddress
import json
import os
from pathlib import Path
import re
import socket
import ssl
import time
from urllib.parse import urlsplit, urljoin, urlencode, parse_qsl
import xml.etree.ElementTree as ET

from knowledge_store import canonical, digest, Conflict, host_json
from knowledge_structure import STRUCTURE
from ingest_ops import OpRefused


class Deferred(Exception):
    def __init__(self, message, delay=60, pause=False):
        super().__init__(message)
        self.delay, self.pause = delay, pause


def origin(url):
    p = urlsplit(url)
    return f'{p.scheme}://{p.netloc.lower()}'


def validate_url(url):
    if not isinstance(url, str) or len(url) > 2048 or any(ord(c) < 33 for c in url):
        raise ValueError('A valid public HTTPS address is required')
    p = urlsplit(url)
    if any(key.lower().replace('-','_') in {'token','access_token','api_key','apikey','password','secret','signature','sig'} for key,_ in parse_qsl(p.query)):
        raise ValueError('Source URLs cannot carry credentials; use a host-managed reference')
    if p.scheme != 'https' or not p.hostname or p.username or p.password or p.port not in (None, 443) or p.fragment:
        raise ValueError('Only public HTTPS addresses without credentials or fragments are supported')
    if p.hostname.lower() in ('localhost', 'localhost.localdomain'):
        raise ValueError('Local destinations are not supported')
    try:
        if not ipaddress.ip_address(p.hostname).is_global:
            raise ValueError('Private destinations are not supported')
    except ValueError as exc:
        if 'Private' in str(exc):
            raise
    return url


def validate_config(data, imported=False):
    allowed = {'name','kind','target','steward','organization','space','topic','classification','credential_ref',
               'interval','artifacts','filters','allowed_origins','fetch_budget','byte_budget','synthesis_budget'}
    if not isinstance(data, dict) or set(data) - allowed:
        raise ValueError('Unknown source configuration fields')
    c = dict(data)
    if c.get('kind') not in ('github','page','feed'):
        raise ValueError('Choose GitHub, page or feed')
    if c['kind'] == 'github':
        if not isinstance(c.get('target'), str) or not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', c['target']):
            raise ValueError('Repository must be an explicit owner/name')
        if any(part in ('.','..') for part in c['target'].split('/')): raise ValueError('Invalid explicit repository identity')
        c['target'] = c['target'].lower()
    else:
        validate_url(c.get('target'))
    for key in ('name','steward'):
        if not isinstance(c.get(key), str) or not 1 <= len(c[key]) <= 200:
            raise ValueError('Name and responsible steward are required')
    if c.get('organization') not in ('transpara','transpara-ai','shared') or c.get('space') not in STRUCTURE.space_map:
        raise ValueError('Choose a registered organization and destination space')
    c.setdefault('classification', 'internal')
    # Authoring grants define a single internal curator cohort today. No implied wider distribution.
    if c['classification'] not in STRUCTURE.classification_keys:
        raise ValueError('Choose a registered permitted evidence classification')
    c.setdefault('topic','')
    c.setdefault('credential_ref','')
    if imported and c['credential_ref']:
        raise ValueError('Imports must omit credentials; assign a host reference after preview')
    if not re.fullmatch(r'[a-zA-Z0-9_.-]{0,80}', c['credential_ref']):
        raise ValueError('Use an approved credential reference, never a credential value')
    for key, default, low, high in (('interval',1800 if c['kind']=='github' else 21600,60,2592000),
                                   ('fetch_budget',40,1,1000),('byte_budget',2000000,1000,10000000),('synthesis_budget',1,0,10)):
        c.setdefault(key, default)
        if type(c[key]) is not int or not low <= c[key] <= high:
            raise ValueError('Invalid schedule or processing budget')
    c.setdefault('artifacts', ['issues','pulls','comments','reviews','diffs'] if c['kind']=='github' else [])
    if not isinstance(c['artifacts'], list) or set(c['artifacts']) - {'issues','pulls','comments','reviews','diffs','releases','paths'}:
        raise ValueError('Unknown artifact type')
    c.setdefault('filters', {})
    if not isinstance(c['filters'], dict) or set(c['filters']) - {'labels','states','base_branches','include_paths','exclude_paths'}:
        raise ValueError('Unknown collection filters')
    for values in c['filters'].values():
        if not isinstance(values, list) or len(values)>100 or not all(isinstance(v,str) and 0<len(v)<300 for v in values):
            raise ValueError('Filters must be short lists of strings')
    if 'paths' in c['artifacts'] and not c['filters'].get('include_paths'):
        raise ValueError('File watches require explicit repository paths')
    if 'paths' in c['artifacts'] and any(p.startswith('/') or any(part in ('.','..') for part in p.split('/')) or any(x in p for x in '*?[') for p in c['filters']['include_paths']):
        raise ValueError('Watched content paths must be exact paths; diff filters may use globs')
    c.setdefault('allowed_origins', [])
    if not isinstance(c['allowed_origins'], list) or len(c['allowed_origins'])>20:
        raise ValueError('Invalid followed origins')
    for value in c['allowed_origins']:
        validate_url(value)
        if origin(value) != value.rstrip('/'):
            raise ValueError('Additional destinations must be HTTPS origins')
    from ingest_ops import quarantine_payload
    quarantine_payload(canonical(c).encode())
    return c


class PinnedHTTPS(http.client.HTTPSConnection):
    def connect(self):
        addresses = socket.getaddrinfo(self.host, self.port, type=socket.SOCK_STREAM)
        if not addresses or any(not ipaddress.ip_address(a[4][0]).is_global for a in addresses):
            raise Deferred('Destination resolves to a non-public address', pause=True)
        sock = socket.create_connection((addresses[0][4][0], self.port), self.timeout)
        self.sock = self._context.wrap_socket(sock, server_hostname=self.host)


class Fetcher:
    def __init__(self, store):
        self.store = store

    def credential(self, ref, url):
        if not ref:
            return {}
        path = os.environ.get('KNOWLEDGE_HUB_CREDENTIALS')
        try:
            spec = host_json(path,private=True)[ref]
            if origin(url) not in spec['origins'] or spec['type'] not in ('github','bearer'):
                raise ValueError()
            if spec['type']=='github' and origin(url) != 'https://api.github.com':
                raise ValueError()
            value = os.environ[spec['environment']]
            if not value or '\n' in value or '\r' in value:
                raise ValueError()
            return {'Authorization': 'Bearer ' + value}
        except (TypeError, OSError, KeyError, ValueError):
            raise Deferred('Approved source credential is unavailable or not valid for this origin', pause=True) from None

    @contextmanager
    def serial(self, ref):
        directory = self.store.path.parent / 'fetch-locks'
        directory.mkdir(mode=0o700, exist_ok=True)
        with (directory / (digest(ref or 'anonymous-github') + '.lock')).open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            yield

    def __call__(self, url, config, conditional=None):
        validate_url(url)
        headers = {'User-Agent':'Transpara-Knowledge-Hub/1', 'Accept':'application/vnd.github+json' if urlsplit(url).hostname=='api.github.com' else '*/*'}
        headers.update(self.credential(config.get('credential_ref',''), url))
        for key, value in (conditional or {}).items():
            if key in ('If-None-Match','If-Modified-Since'):
                headers[key] = value
        # No automatic redirect following: caller controls destination policy, credentials never cross origins.
        p = urlsplit(url)
        with self.serial(headers.get('Authorization','anonymous')):
            connection = PinnedHTTPS(p.hostname, timeout=20, context=ssl.create_default_context())
            try:
                connection.request('GET', p.path + ('?' + p.query if p.query else ''), headers=headers)
                response = connection.getresponse()
                body = response.read(config['byte_budget'] + 1)
                if len(body)>config['byte_budget']:
                    raise Deferred('Response exceeds extraction budget; increase budget or narrow scope')
                result = (response.status, dict((k.lower(),v) for k,v in response.getheaders()), body)
            except (OSError, http.client.HTTPException):
                raise Deferred('Source request failed; prior evidence retained') from None
            finally:
                connection.close()
        status, meta, _ = result
        if status>=400 and ('retry-after' in meta or meta.get('x-ratelimit-remaining')=='0' or status==429 or status==403 and b'rate limit' in body.lower()):
            delay = 60
            try:
                delay = max(60, float(meta.get('retry-after', '0')), float(meta.get('x-ratelimit-reset','0'))-time.time())
            except ValueError:
                try:
                    delay = max(60,email.utils.parsedate_to_datetime(meta['retry-after']).timestamp()-time.time())
                except (ValueError, KeyError, TypeError):
                    pass
            raise Deferred('Source rate limit; scan remains incomplete', delay=delay)
        if status in (401,403,404,410):
            raise Deferred('Source unavailable or access changed; audience review required (not proof of deletion)', pause=True)
        if status>=400:
            raise Deferred('Source returned an error; prior evidence retained')
        return result


class TextHTML(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts=[]; self.hidden=0
    def handle_starttag(self, tag, attrs):
        if tag in ('script','style','noscript'):
            self.hidden+=1
    def handle_endtag(self, tag):
        if tag in ('script','style','noscript'):
            self.hidden=max(0,self.hidden-1)
    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def extract(raw, content_type):
    if len(raw)>10000000:
        raise Deferred('Extraction budget exceeded')
    if 'html' in content_type:
        parser=TextHTML(); parser.feed(raw.decode('utf-8','replace'))
        return ' '.join(' '.join(parser.parts).split()), 'extracted'
    if any(t in content_type for t in ('text/','json','xml')):
        return raw.decode('utf-8','replace').strip(), 'extracted'
    return '', 'unsupported'


def matching(item, config):
    filters=config['filters']
    labels={x['name'] if isinstance(x,dict) else x for x in item.get('labels',[])}
    state='merged' if item.get('merged_at') else 'draft' if item.get('draft') else item.get('state')
    return (not filters.get('labels') or bool(labels & set(filters['labels']))) and (
        not filters.get('states') or state in filters['states']) and (
        not item.get('pull_request') and 'base' not in item or not filters.get('base_branches') or item.get('base',{}).get('ref') in filters['base_branches'])


def path_matches(path, config):
    f=config['filters']
    return not any(fnmatch.fnmatchcase(path,p) for p in f.get('exclude_paths',[])) and (
        not f.get('include_paths') or any(fnmatch.fnmatchcase(path,p) for p in f['include_paths']))


class Collector:
    def __init__(self, store, fetch=None):
        self.store=store; self.fetch=fetch or Fetcher(store)

    def request(self, url, c, cache=None, allowed=None):
        for _ in range(5):
            if allowed is not None and origin(url) not in allowed:
                raise Deferred('Destination outside approved origins; configuration review required', pause=True)
            status, headers, raw=self.fetch(url,c,cache)
            if status in (301,302,303,307,308):
                target=urljoin(url,headers.get('location',''))
                validate_url(target)
                if c['kind']=='github' or origin(target)!=origin(url):
                    raise Deferred('Source redirect or ownership change requires preview', pause=True)
                url=target; cache=None; continue
            return status,headers,raw,url
        raise Deferred('Too many source redirects')

    def preview(self, config):
        c=validate_config(config)
        url='https://api.github.com/repos/'+c['target'] if c['kind']=='github' else c['target']
        _,h,b,actual=self.request(url,c,allowed={origin(url)})
        if c['kind']=='github':
            data=json.loads(b)
            if data.get('full_name','').lower()!=c['target']:
                raise Deferred('Repository target changed; review the canonical target',pause=True)
            status='metadata accessible'; sample=data.get('description',''); stable={'id':data['id'],'owner':data['owner']['id'],'private':data['private']}
        else:
            sample,status=extract(b,h.get('content-type','')); stable={'url':actual}
        return {'target':actual,'artifacts':c['artifacts'],'filters':c['filters'],'sample':(sample or '')[:2000],
                'identity':stable,'extraction':status,'config_hash':digest(c),'at':time.time()}

    def scan(self, key):
        m=self.store.get('monitor',key)
        if m['state']!='enabled':
            return
        c=m['config']; cp=m.get('checkpoint',{}); changed=set(); attempted=time.time()
        base='https://api.github.com/repos/'+c['target']
        if not cp.get('tasks'):
            since=dt.datetime.fromtimestamp(cp.get('since', attempted-30*86400)-300,dt.timezone.utc).isoformat()
            if c['kind']=='github':
                base='https://api.github.com/repos/'+c['target']
                tasks=[{'url':base,'kind':'identity'}]
                if {'issues','pulls'} & set(c['artifacts']):
                    tasks += [{'url':base+'/issues?'+urlencode({'state':'all','since':since,'per_page':100}),'kind':'issues'}]
                    if not cp.get('backfilled'):
                        tasks += [{'url':base+'/issues?state=open&per_page=100','kind':'issues'}]
                if 'comments' in c['artifacts']:
                    tasks += [{'url':base+'/issues/comments?'+urlencode({'since':since,'per_page':100}),'kind':'comments'}]
                # Poll tracked parents and child streams independently, even when parent updated_at is unchanged.
                for number, typ in cp.get('tracked',{}).items():
                    tasks += [{'url':base+'/'+typ+'/'+number,'kind':'pull' if typ=='pulls' else 'issue'}]
                if 'releases' in c['artifacts']:
                    tasks += [{'url':base+'/releases?per_page=100','kind':'releases'}]
                if 'paths' in c['artifacts']:
                    for path in c['filters'].get('include_paths',[]):
                        if path_matches(path,c) and not any(p in ('.','..') for p in path.split('/')):
                            from urllib.parse import quote
                            tasks.append({'url':base+'/contents/'+quote(path,safe='/'),'kind':'path','path':path})
            else:
                tasks=[{'url':c['target'],'kind':c['kind']}]
            cp.update(tasks=tasks,scan_started=attempted,seen=[],changed=[],members_next={},allowed=[],cache=cp.get('cache',{}))
        try:
            for _ in range(c['fetch_budget']):
                if not cp['tasks']:
                    break
                # A pause/edit made while the worker runs takes effect before the next request.
                current=self.store.get('monitor',key)
                if current['state']!='enabled' or current['config']!=c:
                    return
                task=cp['tasks'][0]; url=task['url']; kind=task['kind']
                allowed={'https://api.github.com'} if c['kind']=='github' else {origin(c['target']),*c['allowed_origins']}
                status,h,raw,actual=self.request(url,c,cp['cache'].get(url),allowed)
                records=[]; more=[]
                if status==304 and kind in ('issue','pull'):
                    parent=cp.get('parents',{}).get(url)
                    if parent:
                        cp.setdefault('allowed',[]).append(parent['number'])
                        more+=self.children(base,parent['number'],parent['type'],c)
                if status!=304:
                    if c['kind']=='github':
                        data=json.loads(raw)
                        if kind=='identity':
                            stable={'id':data['id'],'owner':data['owner']['id'],'private':data['private']}
                            if stable!=m['preview']['identity']:
                                raise Deferred('Repository ownership or visibility changed; audience review required',pause=True)
                            if data['full_name'].lower()!=c['target']:
                                raise Deferred('Repository renamed; edit target and preview to resume using stable identity',pause=True)
                        else:
                            items=data if isinstance(data,list) else [data]
                            for item in items:
                                number=str(item.get('number',''))
                                if kind in ('issues','issue','pull'):
                                    typ='pulls' if 'pull_request' in item or kind=='pull' else 'issues'
                                    if typ not in c['artifacts']:
                                        continue
                                    if kind=='issues':
                                        more.append({'url':base+'/'+typ+'/'+number,'kind':'pull' if typ=='pulls' else 'issue'}); continue
                                    if not matching(item,c):
                                        cp.setdefault('tracked',{}).pop(number,None)
                                        continue
                                    cp.setdefault('allowed',[]).append(number)
                                    cp.setdefault('tracked',{})[number]=typ
                                    if kind in ('issue','pull'): cp.setdefault('parents',{})[url]={'number':number,'type':typ}
                                    more+=self.children('https://api.github.com/repos/'+c['target'],number,typ,c)
                                elif kind=='comments':
                                    parent=item.get('issue_url','').rsplit('/',1)[-1]
                                    if parent not in cp.get('allowed',[]):
                                        continue
                                elif kind in ('diffs','inline') and not path_matches(item.get('filename') or item.get('path',''),c):
                                    continue
                                if kind=='path':
                                    import base64
                                    if item.get('type')!='file' or item.get('encoding')!='base64':
                                        raise Deferred('Watched path is not a supported file')
                                    body=base64.b64decode(item['content'],validate=False)
                                    content,status_extract=extract(body,'text/plain' if b'\x00' not in body else 'application/octet-stream')
                                else:
                                    body=canonical(item).encode(); content=canonical(item); status_extract='extracted'
                                stable_id=str(item.get('node_id') or item.get('id') or item.get('filename') or task.get('path'))
                                source_kind='comment' if kind in ('comments','thread') else kind
                                if kind=='diffs':
                                    stable_id=url.split('/pulls/',1)[1].split('/',1)[0]+':'+stable_id
                                source=f"github:{m['preview']['identity']['id']}:{source_kind}:{stable_id}"
                                # Parent and list endpoints resolve to one artifact identity.
                                if kind in ('issue','issues','pull'):
                                    source=f"github:{m['preview']['identity']['id']}:artifact:{stable_id}"
                                records.append((source,body,content,{'url':item.get('html_url',actual),'type':source_kind,
                                    'repository_revision':item.get('merge_commit_sha') or item.get('head',{}).get('sha') or next(iter(re.findall(r'/blob/([a-f0-9]{40})/',item.get('blob_url',''))),None),
                                    'blob_revision':item.get('sha'),
                                    'content_limitations':'Patch unavailable; file metadata is incomplete implementation evidence' if kind=='diffs' and 'patch' not in item else '',
                                    'path':task.get('path'),'base':item.get('base',{}).get('sha'),'state':item.get('state'),'merged_at':item.get('merged_at'),
                                    'extraction':status_extract,'classification':c['classification'],'space':c['space'],
                                    'evidentiary_limit':'Repository change is not deployment; closed issue is not implementation.'}))
                    elif kind=='feed':
                        raw.decode('utf-8',errors='strict')
                        if b'<!DOCTYPE' in raw.upper() or b'<!ENTITY' in raw.upper():
                            raise Deferred('Feed entities are unsupported')
                        tree=ET.fromstring(raw)
                        for entry in tree.iter():
                            if entry.tag.split('}')[-1] not in ('entry','item'):
                                continue
                            fields={e.tag.split('}')[-1]:e for e in entry}
                            published=next((fields[x].text for x in ('published','updated','pubDate') if x in fields),None)
                            try:
                                stamp=dt.datetime.fromisoformat(published.replace('Z','+00:00')).timestamp()
                            except (ValueError,AttributeError):
                                try: stamp=email.utils.parsedate_to_datetime(published).timestamp()
                                except (ValueError,TypeError,AttributeError): stamp=None
                            if not cp.get('backfilled') and (stamp is None or stamp<attempted-30*86400 or stamp>attempted+300):
                                continue
                            link=fields.get('link')
                            target=(link.get('href') or link.text) if link is not None else None
                            if target:
                                target=urljoin(actual,target)
                                if origin(target) in allowed:
                                    more.append({'url':validate_url(target),'kind':'entry'})
                        content,status_extract=extract(raw,'application/xml')
                        records.append((actual,raw,content,{'url':actual,'type':'feed','classification':c['classification'],'space':c['space'],'extraction':status_extract}))
                    else:
                        content,status_extract=extract(raw,h.get('content-type',''))
                        records.append((actual,raw,content,{'url':actual,'type':kind,'classification':c['classification'],'space':c['space'],'extraction':status_extract}))
                # Conditional pagination must still follow cached next pages after a 304.
                link=h.get('link',cp.get('links',{}).get(url,''))
                match=re.search(r'<([^>]+)>;\s*rel="next"',link)
                if match:
                    more.append({**task,'url':match[1]})
                cp.setdefault('links',{})[url]=link
                if status!=304:
                    cp['cache'][url]={k:v for k,v in [('If-None-Match',h.get('etag')),('If-Modified-Since',h.get('last-modified'))] if v}
                if kind in ('thread','reviews','inline','diffs'):
                    group=url.split('?',1)[0]
                    if status==304:
                        members=cp.get('page_members',{}).get(url,[])
                    else:
                        members=[r[0] for r in records]
                        cp.setdefault('page_members',{})[url]=members
                    cp.setdefault('members_next',{}).setdefault(group,[]).extend(members)
                cp['tasks'].pop(0); cp['seen'].append(url)
                queued={t['url'] for t in cp['tasks']}|set(cp['seen'])
                for candidate in more:
                    if candidate['url'] not in queued:
                        cp['tasks'].append(candidate); queued.add(candidate['url'])
                with self.store.connect() as db:
                    db.execute('BEGIN IMMEDIATE')
                    latest=self.store.get('monitor',key,db)
                    if latest['state']!='enabled' or latest['config']!=c:
                        return
                    for source,body,content,meta in records:
                        evidence,is_changed=self.store.capture(source,body,content,meta,key,db)
                        if is_changed and content and meta.get('type')!='feed':
                            cp['changed'].append(evidence); changed.add(evidence)
                    latest.update(checkpoint=cp,last_attempt=attempted,pending=len(cp['tasks']),error=None)
                    m=self.store.put('monitor',latest,latest['revision'],db)
            complete=not cp['tasks']
            with self.store.connect() as db:
                db.execute('BEGIN IMMEDIATE')
                m=self.store.get('monitor',key,db)
                if m['state']!='enabled' or m['config']!=c:
                    return
                if complete:
                    initial_complete=not cp.get('backfilled')
                    for group,members in cp.get('members_next',{}).items():
                        for absent in set(cp.get('members',{}).get(group,[]))-set(members):
                            event={'event':'no longer present in successful complete filtered listing; not proof of repository file deletion','source':absent,'listing':group,'at':cp['scan_started']}
                            evidence,_=self.store.capture(absent,canonical(event).encode(),canonical(event),{'type':'absence','classification':c['classification'],'space':c['space'],'url':group},key,db)
                            cp['changed'].append(evidence)
                    cp.setdefault('members',{}).update(cp.get('members_next',{}))
                    cp.update(since=cp['scan_started'],backfilled=True,last_reconciliation=time.time())
                    if cp['changed']:
                        self.store.put('activity',{'monitor':key,'evidence':sorted(set(cp['changed'])),'status':'new evidence','at':time.time()},db=db)
                        if c['synthesis_budget']:
                            self.store.enqueue('draft',digest([key,sorted(set(cp['changed']))]),{'origin':key,'evidence':sorted(set(cp['changed'])),'space':c['space']},70,db)
                    if initial_complete:
                        self.store.put('activity',{'monitor':key,'status':'Initial backfill completed','at':time.time()},db=db)
                    m['last_success']=time.time()
                m.update(checkpoint=cp,pending=len(cp['tasks']),last_attempt=attempted,
                         next_check=time.time()+(c['interval'] if complete else 60),
                         error=None if complete else 'Fetch budget exhausted; collection will resume')
                self.store.put('monitor',m,m['revision'],db)
        except (Deferred,ValueError,KeyError,ET.ParseError,OpRefused) as exc:
            m=self.store.get('monitor',key)
            m.update(last_attempt=attempted,error=str(exc) if isinstance(exc,(Deferred,OpRefused)) else 'Unsupported or malformed source response',
                     next_check=time.time()+getattr(exc,'delay',60))
            if getattr(exc,'pause',False) or isinstance(exc,OpRefused):
                m['state']='paused'; m['preview']=None
                if getattr(exc,'pause',False): m['audience_review_required']=True
            self.store.put('monitor',m,m['revision'])
            raise

    @staticmethod
    def children(base,number,typ,c):
        tasks=[]
        if 'comments' in c['artifacts']:
            tasks.append({'url':base+'/issues/'+number+'/comments?per_page=100','kind':'thread'})
        if typ=='pulls':
            for artifact,suffix,kind in [('reviews','reviews','reviews'),('reviews','comments','inline'),('diffs','files','diffs')]:
                if artifact in c['artifacts']:
                    tasks.append({'url':base+'/pulls/'+number+'/'+suffix+'?per_page=100','kind':kind})
        return tasks
