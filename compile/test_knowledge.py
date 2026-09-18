#!/usr/bin/env python3
"""Behavioral tests for retained evidence, collection, review and publication boundaries."""
import copy
import json
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

from knowledge_store import Store,Conflict,digest
from knowledge_sources import Collector,Deferred,validate_config,validate_url,matching,path_matches,Fetcher
from knowledge_review import DIMENSIONS,WEIGHTS,Reviewer,scorecard,check_citations
from knowledge_workflow import Workflow
from knowledge_worker import schedule,tick


def config(kind='page',**extra):
    return validate_config({'name':'Source','kind':kind,'target':'owner/repo' if kind=='github' else 'https://example.org/data',
         'steward':'curator','organization':'shared','space':'civilization',**extra})


def assessment(evidence,score=3):
    return {'readiness':'Ready for approval','organizations':{org:{'dimensions':{d:{'score':score,'rationale':'Documented evidence','evidence_ids':[evidence]} for d in DIMENSIONS},
          'philosophy_relationship':'Challenges'} for org in WEIGHTS},'objections':[],'evidence_quality':'Captured source with direct quotation'}


class KnowledgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name); (self.root/'wiki').mkdir(); (self.root/'compile').mkdir()
        self.store=Store(self.root); self.workflow=Workflow(self.root,self.store)
    def capture(self,source='source',text='Measured improvement of productivity.'):
        return self.store.capture(source,text.encode(),text,{'classification':'internal','space':'civilization'},'test')[0]
    def monitor(self,c=None,fetch=None):
        c=c or config(); w=Workflow(self.root,self.store,fetch)
        m=w.monitor('add',{'config':c}); m=w.monitor('preview',{'id':m['id'],'revision':m['revision']})
        return w,w.monitor('enable',{'id':m['id'],'revision':m['revision']})
    def proposal(self):
        e=self.capture(); body='Measured productivity improvement. [evidence:'+e+']'
        p={'space':'civilization','origin':'test','evidence_ids':[e],'findings':[{'kind':'observation','text':'Measured improvement',
           'citations':[{'evidence_id':e,'quote':'Measured improvement'}]}],
           'changes':[{'slug':'new-finding','title':'New Finding','body':body,'evidence_ids':[e]}],
           'coverage_limitations':'Limited to selected evidence','article_revisions':{'new-finding':None},'state':'draft','repair_count':0}
        p=self.store.put('proposal',p); frozen=self.workflow.frozen(p)
        p.update(frozen=frozen,review={'state':'Ready for approval','frozen_hash':digest(frozen)},state='Ready for approval')
        return self.store.put('proposal',p,p['revision'])
    def test_private_state_and_immutable_dedup_provenance(self):
        e=self.capture(); same,changed=self.store.capture('source',b'Measured improvement of productivity.','Measured improvement of productivity.',{'classification':'internal','space':'civilization'},'research')
        self.assertEqual(e,same); self.assertFalse(changed)
        self.assertEqual(set(self.store.evidence(e)['origins']),{'test','research'})
        self.assertEqual(self.store.path.stat().st_mode & 0o777,0o600)
        self.capture(text='Updated observation')
        self.assertFalse(self.store.current([self.store.evidence(e)]))
        self.assertEqual(self.store.evidence(e)['text'],'Measured improvement of productivity.')
    def test_cosmetic_raw_changes_retained_without_synthesis(self):
        first,_=self.store.capture('url',b'<p>same</p>','same',{},'monitor')
        second,changed=self.store.capture('url',b'<p class="a">same</p>','same',{},'monitor')
        self.assertNotEqual(first,second); self.assertFalse(changed)
    def test_job_priority_lease_and_retry(self):
        self.store.enqueue('scan','one',{},60); interactive=self.store.enqueue('research','two',{},10)
        j=self.store.claim('worker',lease=-1); self.assertEqual(j['id'],interactive)
        retry=self.store.claim('new-worker'); self.assertEqual(retry['id'],interactive)
        self.store.finish(j); self.assertEqual(self.store.jobs()[0]['state'],'running')
        self.store.finish(retry); self.assertEqual(self.store.claim('worker')['kind'],'scan')
    def test_config_requires_explicit_allowlist_and_preview(self):
        m=self.workflow.monitor('add',{'config':config()}); self.assertEqual(m['state'],'disabled')
        schedule(self.store); self.assertEqual(self.store.jobs(),[])
        with self.assertRaises(Conflict): self.workflow.monitor('enable',{'id':m['id'],'revision':m['revision']})
        for target in ('https://localhost/x','https://127.0.0.1/x','http://example.org','https://user:password@example.org','https://example.org:22'):
            with self.subTest(target=target),self.assertRaises(ValueError): validate_url(target)
        with self.assertRaises(ValueError): validate_config({**config(),'credential_ref':'production'},imported=True)
    def test_page_unchanged_never_queues_models_and_pause_retire(self):
        calls=[]
        def fetch(url,c,conditional):
            calls.append(url); return (304 if conditional else 200),{'content-type':'text/html','etag':'v1'},b'<p>Evidence</p>'
        w,m=self.monitor(fetch=fetch); w.collector.scan(m['id'])
        self.assertEqual(len([j for j in self.store.jobs() if j['kind']=='draft']),1)
        w.collector.scan(m['id']); self.assertEqual(len([j for j in self.store.jobs() if j['kind']=='draft']),1)
        m=self.store.get('monitor',m['id']); m=w.monitor('pause',{'id':m['id'],'revision':m['revision']})
        count=len(calls); w.collector.scan(m['id']); self.assertEqual(len(calls),count)
        w.monitor('retire',{'id':m['id'],'revision':m['revision']}); self.assertEqual(len(self.store.search()),1)
    def test_failed_fetch_does_not_replace_retained_evidence(self):
        w,m=self.monitor(fetch=lambda *a:(200,{'content-type':'text/plain'},b'Good content'))
        w.collector.scan(m['id']); old=self.store.search()[0]['id']
        def unavailable(*_): raise Deferred('Access changed',pause=True)
        w.collector.fetch=unavailable
        with self.assertRaises(Deferred): w.collector.scan(m['id'])
        self.assertEqual(self.store.search()[0]['id'],old)
        self.assertEqual(self.store.get('monitor',m['id'])['state'],'paused')
    def test_feed_origin_and_initial_history(self):
        stamp=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
        feed=('<feed><entry><published>'+stamp+'</published><link href="https://elsewhere.test/no"/></entry>'
              '<entry><published>'+stamp+'</published><link href="https://example.org/yes"/></entry></feed>').encode()
        calls=[]
        def fetch(url,*_):
            calls.append(url); return 200,{'content-type':'application/xml' if url.endswith('data') else 'text/plain'},feed if url.endswith('data') else b'Linked source'
        w,m=self.monitor(config('feed'),fetch); w.collector.scan(m['id'])
        self.assertIn('https://example.org/yes',calls); self.assertNotIn('https://elsewhere.test/no',calls)
    def test_github_backfill_budget_resume_dedup_reviews_and_states(self):
        calls=[]; version=[0]
        def fetch(url,*_):
            calls.append(url)
            if '?' not in url and url.endswith('/owner/repo'): data={'id':42,'owner':{'id':7},'full_name':'owner/repo','private':False}
            elif '/pulls/3/reviews' in url: data=[{'id':70,'body':'Review '+str(version[0])}]
            elif '/pulls/3/files' in url: data=[{'filename':'src/a.py','patch':'updated','sha':'abc'}]
            elif url.endswith('/pulls/3'): data={'id':3,'number':3,'state':'closed','merged_at':'2026-09-01','head':{'sha':'abc'},'base':{'sha':'def','ref':'main'},'title':'PR'}
            elif '/comments' in url: data=[]
            elif '/issues?' in url: data=[{'id':3,'number':3,'pull_request':{},'title':'PR','state':'closed'}]
            else: raise AssertionError(url)
            return 200,{},json.dumps(data).encode()
        w,m=self.monitor(config('github',fetch_budget=2),fetch)
        for _ in range(12):
            w.collector.scan(m['id'])
            if self.store.get('monitor',m['id']).get('last_success'): break
        current=self.store.get('monitor',m['id']); self.assertTrue(current['checkpoint']['backfilled']); self.assertEqual(current['pending'],0)
        self.assertTrue(any('state=open' in url for url in calls)); self.assertTrue(any('since=' in url for url in calls))
        artifacts=[e for e in self.store.search() if ':artifact:' in e['source']]; self.assertEqual(len(artifacts),1)
        self.assertIn('not deployment',artifacts[0]['metadata']['evidentiary_limit'])
        version[0]=1
        for _ in range(12):
            w.collector.scan(m['id'])
            if not self.store.get('monitor',m['id'])['pending']: break
        self.assertTrue(any('Review 1' in e['text'] for e in self.store.search()))
    def test_filters_and_exclusions(self):
        c=config('github',filters={'labels':['docs'],'states':['merged'],'base_branches':['main'],'include_paths':['docs/*'],'exclude_paths':['docs/private*']})
        self.assertTrue(matching({'labels':[{'name':'docs'}],'state':'closed','merged_at':'now','base':{'ref':'main'}},c))
        self.assertFalse(matching({'labels':[],'state':'closed'},c))
        self.assertTrue(path_matches('docs/a.md',c)); self.assertFalse(path_matches('docs/private.md',c))
    def test_score_unknown_is_interval_not_zero_and_opposition_relevant(self):
        a=assessment(self.capture(),4); a['organizations']['transpara']['dimensions']['technology_match']['score']=None
        s=scorecard(a); self.assertEqual((s['transpara']['low'],s['transpara']['high']),(75,100)); self.assertFalse(s['transpara']['complete'])
        self.assertEqual(s['transpara-ai']['low'],100)
    def test_blind_families_bounded_challenge_and_unavailable(self):
        e=self.capture(); frozen={'evidence':[self.store.evidence(e)]}; calls=[]
        def model(stage,context,spec):
            calls.append((stage,context,spec)); return assessment(e,4 if spec['provider']=='codex' else 1)
        reviewers=[{'provider':'codex','model':'a'},{'provider':'claude','model':'b'}]
        result=Reviewer(model,reviewers).run(frozen)
        self.assertEqual([x[0] for x in calls],['review','review','challenge','challenge'])
        self.assertEqual(calls[0][1],calls[1][1]); self.assertNotIn('other',calls[0][1]); self.assertEqual(result['state'],'Needs a decision')
        with self.assertRaises(ValueError): Reviewer(model,[reviewers[0],reviewers[0]])
        def fail(*_): raise OSError()
        self.assertEqual(Reviewer(fail,reviewers).run(frozen)['state'],'Review incomplete')
    def test_fabricated_quotes_and_stale_approval_fail(self):
        p=self.proposal(); e=self.store.evidence(p['evidence_ids'][0])
        bad={'findings':[{'kind':'observation','citations':[{'evidence_id':e['id'],'quote':'fabricated'}]}]}
        with self.assertRaises(ValueError): check_citations(bad,[e])
        self.capture(text='New source version')
        with self.assertRaises(Conflict): self.workflow.frozen(p)
    def test_publication_failure_restores_original_and_preserves_served(self):
        p=self.proposal(); (self.root/'dist').mkdir(); (self.root/'dist/index.html').write_text('old served')
        def build(_): raise ValueError('validation failure')
        with patch('ingest_server.LOCK_PATH',self.root/'compile/.wiki-write.lock'),self.assertRaises(ValueError): self.workflow.publish(p,'curator',builder=build)
        self.assertFalse((self.root/'wiki/new-finding.md').exists()); self.assertEqual((self.root/'dist/index.html').read_text(),'old served')
        self.assertEqual(self.store.list('publication')[0]['state'],'rolled back')
    def test_publication_binds_exact_review_and_exports_provenance(self):
        p=self.proposal();
        def build(stage): (stage/'index.html').write_text('new served')
        with patch('ingest_server.LOCK_PATH',self.root/'compile/.wiki-write.lock'): result=self.workflow.publish(p,'curator',builder=build)
        self.assertEqual(result['state'],'published'); self.assertIn('raw_documents:',(self.root/'wiki/new-finding.md').read_text())
        self.assertEqual((self.root/'wiki/new-finding.md').read_text(),p['frozen']['articles'][0]['document'])
        self.assertTrue((self.root/'raw/inbox/discovery'/ (p['evidence_ids'][0]+'.md')).is_file())
        from article_catalog import split_frontmatter, scalar
        fm,_=split_frontmatter((self.root/'wiki/new-finding.md').read_text())
        self.assertEqual(scalar(fm,'version'),'1.0.0')
        self.assertEqual(scalar(fm,'doc_id'),'TAI-WIKI-NEW-FINDING')
        evidence=(self.root/'raw/inbox/discovery'/ (p['evidence_ids'][0]+'.md')).read_text()
        efm,_=split_frontmatter(evidence)
        self.assertEqual(scalar(efm,'doc_type'),'evidence')
        self.assertEqual(scalar(efm,'version'),'1.0.0')

    def test_document_control_preserves_frontmatter_and_advances_semver(self):
        from article_catalog import split_frontmatter, scalar
        p=self.proposal(); c=p['changes'][0]
        original='''---
document_id: TAI-EXISTING
version: "2.3.4"
entity: Existing finding
owner: Human curator
author: Original author
created: 2025-03-01
classification: company-internal
placements:
  - civilization/concept
supersedes:
  - OLDER-DOCUMENT
custom_policy:
  unchanged: true
sources:
  - https://example.org/original
---
Old content
'''
        for bump,expected in [('major','3.0.0'),('minor','2.4.0'),('patch','2.3.5')]:
            p['version_bumps']={c['slug']:bump}
            document=self.workflow.article_document(p,c,original,'2026-09-18')
            fm,_=split_frontmatter(document)
            self.assertEqual(scalar(fm,'version'),expected)
            for key,value in [('document_id','TAI-EXISTING'),('owner','Human curator'),('author','Original author'),
                              ('created','2025-03-01'),('classification','company-internal')]:
                self.assertEqual(scalar(fm,key),value)
            self.assertNotIn('doc_id:',fm)
            for block in ['custom_policy:\n  unchanged: true','sources:\n  - https://example.org/original',
                          'supersedes:\n  - OLDER-DOCUMENT','placements:\n  - civilization/concept']:
                self.assertIn(block,fm)
        for invalid in [original.replace('2.3.4','not-semver'),original.replace('version: "2.3.4"','version: "2.3.4"\nversion: 2.3.5')]:
            with self.assertRaises(ValueError):
                self.workflow.article_document(p,c,invalid,'2026-09-18')
        legacy=original.replace('version: "2.3.4"\n','').replace('created: 2025-03-01\n','')
        fm,_=split_frontmatter(self.workflow.article_document(p,c,legacy,'2026-09-18'))
        self.assertEqual(scalar(fm,'version'),'1.0.0')
        self.assertEqual(scalar(fm,'created'),'unknown')
        self.assertIn('Prior document versions unknown',fm)

    def test_document_version_choice_invalidates_review(self):
        p=self.proposal()
        path=self.root/'wiki/new-finding.md'
        path.write_text(p['frozen']['articles'][0]['document'])
        p['article_revisions']['new-finding']=digest(path.read_bytes())
        frozen=self.workflow.frozen(p)
        p.update(frozen=frozen,review={'state':'Ready for approval','frozen_hash':digest(frozen)})
        p=self.store.put('proposal',p,p['revision'])
        changed=self.workflow.proposal_action('edit',{'id':p['id'],'revision':p['revision'],
            'changes':p['changes'],'findings':p['findings'],'coverage_limitations':p['coverage_limitations'],
            'version_bumps':{'new-finding':'major'}},'curator')
        self.assertIsNone(changed['review'])
        self.assertNotEqual(digest(self.workflow.frozen(changed)),digest(frozen))
        self.assertIn('version: "2.0.0"',self.workflow.frozen(changed)['articles'][0]['diff'])
        with patch('ingest_server.LOCK_PATH',self.root/'compile/.wiki-write.lock'),self.assertRaises(Conflict):
            self.workflow.publish(changed,'curator',builder=lambda stage:None)

    def test_reused_export_does_not_rewrite_source_document(self):
        p=self.proposal()
        def build(stage): (stage/'index.html').write_text('served')
        with patch('ingest_server.LOCK_PATH',self.root/'compile/.wiki-write.lock'):
            self.workflow.publish(p,'curator',builder=build)
            article=self.root/'wiki/new-finding.md'
            source=self.root/'raw/inbox/discovery'/(p['evidence_ids'][0]+'.md')
            original=source.read_bytes()
            self.capture()  # another observation of unchanged source bytes
            p.pop('id'); p.pop('revision')
            p['article_revisions']['new-finding']=digest(article.read_bytes())
            p['changes'][0]['body']+=' More context.'
            frozen=self.workflow.frozen(p)
            p.update(frozen=frozen,review={'state':'Ready for approval','frozen_hash':digest(frozen)})
            p=self.store.put('proposal',p)
            self.workflow.publish(p,'curator',builder=build)
            self.assertEqual(source.read_bytes(),original)
            self.assertIn('version: "1.1.0"',article.read_text())
    def test_research_capture_retained_before_model_and_saves_private(self):
        i=self.workflow.investigate('start',{'question':'What changed?','space':'civilization'},'alice')
        e=self.workflow.submission({'text':'Observed result','space':'civilization','investigation':i['id'],'propose':False},'alice')
        self.assertEqual(self.store.search(origin=i['id'])[0]['id'],e['evidence']); self.assertEqual(self.store.jobs(),[])
        with self.assertRaises(KeyError): self.workflow.investigation_access(i['id'],'bob')
        saved=self.workflow.investigate('save',{'id':i['id']},'alice'); self.assertEqual(saved['owner'],'alice')
    def test_backup_preserves_research_state(self):
        self.capture(); dest=self.root/'.private/backup/state.sqlite3'; self.store.backup(dest)
        self.assertEqual(len(Store(self.root,path=dest).search()),1)

    def test_dns_and_redirects_do_not_reach_private_or_unapproved_hosts(self):
        from knowledge_sources import PinnedHTTPS
        import socket
        with patch('knowledge_sources.socket.getaddrinfo',return_value=[(socket.AF_INET,socket.SOCK_STREAM,6,'',('127.0.0.1',443))]), patch('knowledge_sources.socket.create_connection') as connect:
            with self.assertRaises(Deferred): PinnedHTTPS('example.org').connect()
            connect.assert_not_called()
        calls=[]
        def redirect(url,*_): calls.append(url); return 302,{'location':'https://private.example/no'},b''
        with self.assertRaises(Deferred): Collector(self.store,redirect).request('https://example.org/start',config(),allowed={'https://example.org'})
        self.assertEqual(calls,['https://example.org/start'])
        with self.assertRaises(ValueError): validate_url('https://example.org/?api_key=not-a-real-key')

    def test_import_is_preview_bound_disabled_and_single_use(self):
        w=Workflow(self.root,self.store,lambda *a:(200,{'content-type':'text/plain'},b'Preview'))
        batch=w.monitor('import-preview',{'configs':[config()]})
        result=w.monitor('import',{'id':batch['id']})
        self.assertEqual(result['monitors'][0]['state'],'disabled')
        with self.assertRaises(Conflict): w.monitor('import',{'id':batch['id']})

    def test_audience_widening_and_unknown_links_refused(self):
        p=self.proposal(); path=self.root/'wiki/new-finding.md'
        path.write_text('---\nentity: Existing\norg: transpara-ai\nprimary_placement: civilization/concept\nplacements: [civilization/concept]\nclassification: company-internal\ntier: concept\n---\n\nExisting article')
        p['article_revisions']['new-finding']=digest(path.read_bytes())
        with self.assertRaisesRegex(ValueError,'classification'): self.workflow.frozen(p)
        path.unlink(); p['article_revisions']['new-finding']=None
        p['changes'][0]['body']+=' [Missing](missing-article.md)'
        with self.assertRaisesRegex(ValueError,'resolve'): self.workflow.frozen(p)

    def test_source_changes_during_build_abort_before_exchange(self):
        p=self.proposal(); (self.root/'dist').mkdir();(self.root/'dist/index.html').write_text('Previous artifact')
        def builder(stage):
            (stage/'index.html').write_text('Candidate artifact'); self.capture(text='New evidence while building')
        with patch('ingest_server.LOCK_PATH',self.root/'compile/.wiki-write.lock'),self.assertRaises(Conflict):
            self.workflow.publish(p,'curator',builder=builder)
        self.assertEqual((self.root/'dist/index.html').read_text(),'Previous artifact')
        self.assertFalse((self.root/'wiki/new-finding.md').exists())

    def test_crash_recovery_uses_served_marker(self):
        p=self.proposal()
        journal=self.store.put('publication',{'proposal':p['id'],'state':'preparing','originals':{'wiki/new-finding.md':None},'approval':{'actor':'curator'},'at':time.time()})
        (self.root/'wiki/new-finding.md').write_text('Accepted candidate')
        (self.root/'dist').mkdir(); (self.root/'dist/knowledge-publication.json').write_text(json.dumps({'id':journal['id']}))
        self.workflow.recover_publications()
        self.assertEqual(self.store.get('proposal',p['id'])['state'],'published')
        self.assertEqual((self.root/'wiki/new-finding.md').read_text(),'Accepted candidate')

    def test_capture_and_checkpoint_transaction_roll_back_together(self):
        m=self.workflow.monitor('add',{'config':config()})
        with self.assertRaises(RuntimeError),self.store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            self.store.capture('new',b'evidence','evidence',{},m['id'],db)
            m['checkpoint']={'position':1};self.store.put('monitor',m,m['revision'],db)
            raise RuntimeError('Crash before commit')
        self.assertEqual(self.store.search(),[]);self.assertEqual(self.store.get('monitor',m['id'])['checkpoint'],{})

    def test_host_credentials_require_exact_origin_and_private_registry(self):
        file=self.root/'.private/credentials.json';file.write_text(json.dumps({'approved':{'type':'github','origins':['https://api.github.com'],'environment':'KNOWLEDGE_TEST_CREDENTIAL'}}));file.chmod(0o600)
        fetch=Fetcher(self.store)
        with patch.dict(os.environ,{'KNOWLEDGE_HUB_CREDENTIALS':str(file),'KNOWLEDGE_TEST_CREDENTIAL':'fixture-only'}):
            self.assertEqual(fetch.credential('approved','https://api.github.com/repos/a/b')['Authorization'],'Bearer fixture-only')
            with self.assertRaises(Deferred): fetch.credential('approved','https://outside.example')
            file.chmod(0o644)
            with self.assertRaises(Deferred): fetch.credential('approved','https://api.github.com/repos/a/b')

    def test_mcp_read_scope_cannot_publish_or_read_private_material(self):
        from knowledge_mcp import Server
        (self.root/'package.json').write_text('{"version":"0.9.0"}')
        (self.root/'dist').mkdir(); (self.root/'dist/ask-index.json').write_text(json.dumps({'articles':[{'id':'allowed','title':'Allowed','spaces':['platform'],'href':'/allowed.html','text':'Published text'}, {'id':'other','title':'Other','spaces':['civilization'],'href':'/other.html','text':'Other scope'}]}))
        server=Server(self.root,self.root/'dist',['platform'])
        self.assertEqual(server.dispatch({'method':'initialize'})['serverInfo']['version'],'0.9.0')
        names=[t['name'] for t in server.dispatch({'method':'tools/list'})['tools']]
        self.assertNotIn('publish',names);self.assertNotIn('propose',names)
        with self.assertRaises(ValueError): server.dispatch({'method':'tools/call','params':{'name':'read','arguments':{'id':'other'}}})

    def test_http_authoring_denial_precedes_private_state_read(self):
        import ingest_server
        import http.client
        import threading
        from http.server import ThreadingHTTPServer
        (self.root/'compile/repository_routes.json').write_text('{"routes":{}}')
        with patch.object(ingest_server,'ROOT',self.root),patch.object(ingest_server.IngestHandler,'require_authoring',return_value=False),patch('knowledge_api.Workflow') as workflow:
            # Adapter does no work at all after an existing grant refusal.
            class Request:
                path='/api/knowledge/state'
                def require_authoring(self): return False
            import knowledge_api
            knowledge_api.handle(Request(),self.root);workflow.assert_not_called()
        with patch.object(ingest_server,'ROOT',self.root),patch.object(ingest_server.IngestHandler,'require_authoring',return_value=True),patch('knowledge_api.actor',return_value='alice'),patch.object(ingest_server.IngestHandler,'log_message'):
            server=ThreadingHTTPServer(('127.0.0.1',0),ingest_server.IngestHandler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            try:
                self.store.put('save',{'owner':'bob','snapshot':'private saved answer'})
                client=http.client.HTTPConnection('127.0.0.1',server.server_port)
                client.request('GET','/api/knowledge/state'); response=client.getresponse();body=json.loads(response.read())
                self.assertEqual(response.status,200);self.assertEqual(response.getheader('Cache-Control'),'no-store, private');self.assertEqual(body['saved'],[])
                client.close()
            finally: server.shutdown();server.server_close();thread.join()

    def test_observed_reversion_also_invalidates_frozen_review(self):
        p=self.proposal(); frozen=p['frozen']
        self.capture(text='Temporary different observation'); self.capture()
        self.assertFalse(self.store.current(frozen['evidence']))
        self.assertNotEqual(digest(self.workflow.frozen(p)),p['review']['frozen_hash'])

    def test_secret_quarantine_precedes_capture_and_binary_is_not_silent(self):
        from ingest_ops import OpRefused
        with self.assertRaises(OpRefused): self.store.capture('binary',b'\x00binary','',{},'test')
        self.assertEqual(self.store.search(),[])

    def test_manifest_diagram_has_only_captured_dependency_edges(self):
        from knowledge_explain import explain
        e=self.capture(text='{"dependencies":{"example-library":"1"}}')
        evidence=self.store.evidence(e);evidence['metadata'].update(path='package.json',type='path',repository_revision='revision')
        result=explain({'config':{'name':'Repository','target':'owner/repo'}},[evidence])
        self.assertEqual(len(result['edges']),1);self.assertEqual(result['edges'][0]['evidence_id'],e)
        self.assertIn('example-library',result['diagram'])

    def test_connected_submission_draft_review_and_human_publication(self):
        calls=[]
        def model(stage,context,spec):
            calls.append((stage,context))
            if stage=='draft':
                e=context['evidence'][0]
                return {'findings':[{'kind':'observation','text':'Recorded observation','citations':[{'evidence_id':e['id'],'quote':e['text']}]}],
                        'changes':[{'slug':'workflow-observation','title':'Workflow Observation','body':'Recorded observation [evidence:'+e['id']+']','evidence_ids':[e['id']]}],
                        'coverage_limitations':'Only the offered source'}
            return assessment(context['evidence'][0]['id'])
        workflow=Workflow(self.root,self.store,model=model)
        configuration={'author':{'provider':'codex','model':'author'},'reviewers':[{'provider':'codex','model':'review-a'},{'provider':'claude','model':'review-b'}]}
        workflow.submission({'text':'Measured observation','name':'Offered evidence','space':'civilization'},'curator')
        with patch.object(workflow,'provider_config',return_value=configuration):
            tick(workflow,'worker');tick(workflow,'worker')
        p=self.store.list('proposal')[0]
        self.assertEqual(p['state'],'Ready for approval');self.assertEqual([c[0] for c in calls],['draft','review','review'])
        self.assertEqual(calls[1][1],calls[2][1]);self.assertFalse(list((self.root/'wiki').iterdir()))
        with patch('ingest_server.LOCK_PATH',self.root/'compile/.wiki-write.lock'):
            workflow.publish(p,'curator',builder=lambda stage:(stage/'index.html').write_text('Approved'))
        from ingest_ops import ledger_preflight,manifest_registered_paths
        self.assertEqual(len(ledger_preflight(self.root/'compile/ingest-ledger.jsonl')),1)
        self.assertEqual(len(manifest_registered_paths(self.root)),1)
        workflow.recover_publications()
        self.assertEqual(len(ledger_preflight(self.root/'compile/ingest-ledger.jsonl')),1)

    def test_access_loss_blocks_approval_until_explicit_audience_review(self):
        w,m=self.monitor(fetch=lambda *a:(200,{'content-type':'text/plain'},b'Source'))
        p=self.proposal();e=self.store.evidence(p['evidence_ids'][0])
        self.store.capture(e['source'],e['text'].encode(),e['text'],e['metadata'],m['id'])
        m=self.store.get('monitor',m['id']);m.update(state='paused',audience_review_required=True)
        m=self.store.put('monitor',m,m['revision'])
        with self.assertRaisesRegex(Conflict,'audience'): w.frozen(p)
        with self.assertRaises(Conflict): w.monitor('enable',{'id':m['id'],'revision':m['revision']})
        w.monitor('enable',{'id':m['id'],'revision':m['revision'],'audience_acknowledged':True})
        w.frozen(p)


if __name__=='__main__': unittest.main()
