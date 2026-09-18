#!/usr/bin/env python3
"""Publish through the real builder in an isolated copy, never the active corpus."""
import json,sys,tempfile,shutil,time
from pathlib import Path
from unittest.mock import patch
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'compile'))
from knowledge_workflow import Workflow
from knowledge_store import Store,digest
with tempfile.TemporaryDirectory(prefix='wiki-publication-integration-') as directory:
    project=Path(directory)
    for name in ('compile','wiki','spaces'):
        shutil.copytree(root/name,project/name,ignore=shutil.ignore_patterns('__pycache__','*.log','.wiki-write.lock'))
    for name in ('index.md','package.json','VERSION','README.md'):
        if (root/name).exists():shutil.copy2(root/name,project/name)
    (project/'dist').mkdir();(project/'dist/index.html').write_text('Previous served artifact')
    store=Store(project);w=Workflow(project,store)
    key,_=store.capture('fixture:research',b'Reviewing source evidence improves traceability.','Reviewing source evidence improves traceability.',{'classification':'internal','space':'civilization'},'integration')
    p=store.put('proposal',{'space':'civilization','origin':'integration','evidence_ids':[key],'findings':[{'kind':'observation','text':'Traceability improves','citations':[{'evidence_id':key,'quote':'improves traceability'}]}],
       'changes':[{'slug':'discovery-integration-fixture','title':'Discovery Integration Fixture','body':'# Discovery Integration Fixture\n\nReviewing source evidence improves traceability. [evidence:'+key+']','evidence_ids':[key]}],
       'coverage_limitations':'Integration fixture only','article_revisions':{'discovery-integration-fixture':None},'placements':{'discovery-integration-fixture':'civilization/concept'},'state':'draft','repair_count':0,'created':time.time()})
    frozen=w.frozen(p);p.update(frozen=frozen,review={'state':'Ready for approval','frozen_hash':digest(frozen)},state='Ready for approval');p=store.put('proposal',p,p['revision'])
    with patch('ingest_server.LOCK_PATH',project/'compile/.wiki-write.lock'):
        published=w.publish(p,'integration-curator')
    assert published['state']=='published'
    assert (project/'dist/discovery-integration-fixture.html').exists()
    assert (project/'wiki/discovery-integration-fixture.md').exists()
    assert not (project/'dist/.private').exists()
    index=json.loads((project/'dist/ask-index.json').read_text())
    assert any(a['id']=='discovery-integration-fixture' for a in index['articles'])
    from shadow_verify import assert_links_resolve
    assert_links_resolve(project/'dist')
    print('Real publication succeeded: canonical Markdown, provenance, scoped Ask index, validated links, atomic static exchange; isolated fixture removed.')
