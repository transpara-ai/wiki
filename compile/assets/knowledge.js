(function () {
  'use strict';
  const $ = id => document.getElementById(id);
  if (!$('knowledge-workspace')) return;
  let state, editing = null, dirty = false;
  $('knowledge-workspace').addEventListener('input', () => { dirty = true; });
  const notice = text => { $('notice').textContent = text; };
  function el(tag, text, parent) { const node = document.createElement(tag); if (text !== undefined) node.textContent = text; if (parent) parent.append(node); return node; }
  async function api(route, data) {
    const headers = { 'Accept': 'application/json', 'X-Wiki-Profile-Action': '1' };
    const token = $('workflow-token').value;
    if (token) headers['X-CivWiki-Authoring-Token'] = token;
    if (data !== undefined) headers['Content-Type'] = 'application/json';
    const response = await fetch('/api/knowledge/' + route, { method: data === undefined ? 'GET' : 'POST', headers, credentials: 'same-origin', cache: 'no-store', redirect: 'error', body: data === undefined ? undefined : JSON.stringify(data) });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Request failed');
    return result;
  }
  async function perform(fn) { try { await fn(); } catch (error) { notice(error.message); } }
  function button(parent, label, fn) { const node = el('button', label, parent); node.type = 'button'; node.addEventListener('click', () => perform(async () => { node.disabled = true; try { await fn(); } finally { node.disabled = false; } })); return node; }
  function card(parent, title) { const node = el('article', undefined, parent); node.className = 'work-card'; el('h3', title, node); return node; }
  function details(parent, title, text) { const node = el('details', undefined, parent); el('summary', title, node); el('pre', typeof text === 'string' ? text : JSON.stringify(text, null, 2), node); return node; }
  const date = value => value ? new Date(value * 1000).toLocaleString() : 'Not yet';
  function download(name, value) { const url = URL.createObjectURL(new Blob([JSON.stringify(value, null, 2)], {type:'application/json'})); const a = el('a'); a.href = url; a.download = name; a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000); }
  async function evidence(id) { const e = await api('evidence?raw=1&id=' + encodeURIComponent(id)); $('evidence-text').textContent = JSON.stringify({ source:e.source, captured:date(e.captured), metadata:e.metadata, origins:e.origins }, null, 2) + '\n\nExtracted content:\n' + e.text + '\n\nOriginal response:\n' + (e.original || 'Unavailable'); $('evidence-dialog').showModal(); }
  function evidenceButtons(parent, ids) { [...new Set(ids)].forEach(id => button(parent, 'Evidence ' + id.slice(0, 10), () => evidence(id))); }
  function tab(name) { ['monitors','research','review','activity'].forEach(id => { $(id).hidden = id !== name; }); document.querySelectorAll('[data-tab]').forEach(n => n.setAttribute('aria-pressed', String(n.dataset.tab === name))); }
  document.querySelectorAll('[data-tab]').forEach(n => n.addEventListener('click', () => tab(n.dataset.tab)));
  function renderMonitors() {
    $('monitor-list').replaceChildren();
    for (const m of state.monitors) {
      const c = card($('monitor-list'), m.config.name);
      el('p', m.config.target + ' · ' + m.state + ' · ' + m.config.organization, c);
      el('p', 'Last attempt: ' + date(m.last_attempt) + ' · Successful: ' + date(m.last_success) + ' · Next: ' + date(m.next_check) + ' · Retained versions: ' + (m.retained_versions || 0) + ' · Pending: ' + (m.pending || 0), c);
      if (m.error) el('p', m.error, c).className = 'work-warning';
      if (m.preview) details(c, 'Preview: target, accessible artifacts and sample', m.preview);
      details(c, 'Collection scope', m.config);
      let audience; if(m.audience_review_required) { const label=el('label',undefined,c); audience=el('input',undefined,label);audience.type='checkbox';el('span','I reviewed the changed source access and permitted publication audience',label); }
      const actions = el('div', undefined, c); actions.className = 'actions';
      for (const [action,label] of [['preview','Preview'],['enable','Enable'],['pause','Pause'],['run','Run now'],['retire','Retire']]) {
        const b = button(actions,label,async () => { const r = await api('monitors/'+action,{id:m.id,revision:m.revision,audience_acknowledged:!!audience?.checked}); await refresh(); notice(r.job ? 'Preview queued. The workspace will update when it completes.' : 'Source updated.'); });
        if (action === 'enable') b.disabled = !m.preview;
      }
      button(actions,'Edit',() => openSource(m));
      button(actions,'Guided explanation',async () => { const guide=await api('explain?id='+encodeURIComponent(m.id)); if(guide.edges.length) { const list=el('ul',undefined,c); for(const edge of guide.edges) { const target=guide.nodes.find(n=>n.id===edge.to); const row=el('li',guide.scope+' → '+target.label+' ('+edge.relationship+')',list); evidenceButtons(row,[edge.evidence_id]); } } details(c,'Export diagram (Mermaid)',guide.diagram); el('p',guide.limitation,c); for(const step of guide.guide) { el('p',step.step+' · '+(step.revision||'observed snapshot')+' · '+step.limit,c); evidenceButtons(c,[step.evidence_id]); } });
      button(actions,'History',async () => details(c,'Configuration revisions',await api('history?kind=monitor&id='+encodeURIComponent(m.id))));
    }
    if (!state.monitors.length) el('p', 'No sources configured. Add a source to preview it; nothing is enrolled automatically.', $('monitor-list'));
  }
  function openSource(m) {
    editing = m; $('source-form').reset(); $('source-form').hidden = false;
    $('source-heading').textContent = m ? 'Edit source (disables collection until previewed)' : 'Add source';
    const defaults = {kind:'github',interval:1800,fetch_budget:40,byte_budget:2000000,synthesis_budget:1,artifacts:['issues','pulls','comments','reviews','diffs'],filters:{}};
    const c = m ? m.config : defaults;
    for (const [key,value] of Object.entries(c)) { const n = $('source-form').elements.namedItem(key); if (n && key !== 'artifacts') n.value = Array.isArray(value) ? value.join(', ') : value; }
    for (const [key,value] of Object.entries(c.filters || {})) $('source-form').elements.namedItem(key).value = value.join(', ');
    $('artifact-options').querySelectorAll('input').forEach(n => { n.checked = c.artifacts.includes(n.value); });
    $('source-form').elements.namedItem('name').focus();
  }
  for (const name of ['issues','pulls','comments','reviews','diffs','releases','paths']) { const label = el('label',undefined,$('artifact-options')); const input = el('input',undefined,label); input.type='checkbox'; input.value=name; el('span',name,label); }
  $('add-source').onclick = () => openSource(null);
  $('cancel-source').onclick = () => { $('source-form').hidden = true; editing = null; };
  $('source-form').elements.namedItem('kind').onchange = e => { $('source-form').elements.namedItem('interval').value = e.target.value === 'github' ? 1800 : 21600; };
  $('source-form').onsubmit = e => { e.preventDefault(); perform(async () => {
    const f = Object.fromEntries(new FormData(e.target)); const list = text => text.split(',').map(x=>x.trim()).filter(Boolean);
    const config = {name:f.name,kind:f.kind,target:f.target,steward:f.steward,organization:f.organization,space:f.space,topic:f.topic,credential_ref:f.credential_ref,classification:f.classification,interval:Number(f.interval),fetch_budget:Number(f.fetch_budget),byte_budget:Number(f.byte_budget),synthesis_budget:Number(f.synthesis_budget),allowed_origins:list(f.allowed_origins),filters:{},artifacts:[]};
    for (const key of ['labels','states','base_branches','include_paths','exclude_paths']) config.filters[key]=list(f[key]);
    if (f.kind === 'github') config.artifacts=[...$('artifact-options').querySelectorAll('input:checked')].map(n=>n.value);
    await api('monitors/'+(editing?'edit':'add'),{config,...(editing?{id:editing.id,revision:editing.revision}:{})}); $('source-form').hidden=true; editing=null; await refresh(); notice('Saved disabled. Preview the exact target before enabling.');
  }); };
  $('preview-import').onclick = () => perform(async () => { const batch=JSON.parse($('import-json').value); await api('monitors/import-preview',{configs:batch.configs}); notice('Import preview queued. Inspect its result in Activity before importing.'); });
  $('export-config').onclick = () => perform(async () => download('monitor-configurations.json',await api('export')));
  $('export-portable').onclick = () => perform(async () => download('accepted-knowledge.json',await api('portable')));
  $('research-form').onsubmit = e => { e.preventDefault(); perform(async () => { await api('research/start',Object.fromEntries(new FormData(e.target))); e.target.reset(); await refresh(); }); };
  $('submission-file').onchange = e => perform(async () => { const file=e.target.files[0]; if (!file) return; if(file.size>200000) throw new Error('Choose a UTF-8 text document under 200 KB'); $('submission-form').elements.namedItem('text').value=await file.text(); $('submission-form').elements.namedItem('name').value=file.name; });
  $('submission-form').onsubmit = e => { e.preventDefault(); perform(async () => { await api('submit',Object.fromEntries(new FormData(e.target))); e.target.reset(); await refresh(); notice('Evidence retained; drafting queued.'); }); };
  function renderResearch() {
    $('investigation-list').replaceChildren(); $('saved-list').replaceChildren();
    for (const i of state.investigations) {
      const c=card($('investigation-list'),i.question); el('p',i.space+' · '+i.status,c);
      const label=el('label','Capture a specific HTTPS source',c); const url=el('input',undefined,label); url.type='url'; url.placeholder='https://…';
      button(c,'Capture source',async () => { await api('research/capture',{id:i.id,url:url.value}); notice('Source capture queued; evidence is retained before synthesis.'); });
      const note=el('label','Add observed evidence or a document excerpt',c); const text=el('textarea',undefined,note);
      button(c,'Retain evidence',async () => { await api('submit',{text:text.value,name:'Research observation',space:i.space,investigation:i.id,propose:false}); text.value=''; notice('Evidence retained.'); });
      for (const [action,labelText] of [['search','Search the web for this question'],['run','Investigate captured sources'],['propose','Propose article changes'],['save','Save research snapshot'],['close','Close investigation']]) button(c,labelText,async () => { await api('research/'+action,{id:i.id}); await refresh(); notice('Research action recorded.'); });
      button(c,'Inspect retained sources',async () => { const r=await api('evidence?origin='+encodeURIComponent(i.id)); evidenceButtons(c,r.evidence.map(e=>e.id)); });
      if (i.answer) el('p',i.answer,c);
      for (const f of i.findings) { el('p',f.kind+': '+f.text,c); evidenceButtons(c,f.citations.map(x=>x.evidence_id)); }
      if (i.open_questions) details(c,'Open questions',i.open_questions);
    }
    for (const s of state.saved) details($('saved-list'),'Saved '+date(s.at),s.snapshot);
  }
  function scoreTable(parent, organizations) {
    for(const [org,assessment] of Object.entries(organizations)) {
      el('h4',(org==='transpara'?'Transpara':'Transpara-AI')+' · Philosophy: '+assessment.philosophy_relationship,parent);
      const wrap=el('div',undefined,parent);wrap.className='work-table-wrap';const table=el('table',undefined,wrap);table.className='work-score';
      const header=el('tr',undefined,el('thead',undefined,table));for(const title of ['Dimension','Score','Rationale','Evidence']) el('th',title,header).scope='col';
      const body=el('tbody',undefined,table);
      for(const [dimension,value] of Object.entries(assessment.dimensions)) {
        const row=el('tr',undefined,body);el('th',dimension.replaceAll('_',' '),row).scope='row';el('td',value.score===null?'Unknown':value.score+' / 4',row);el('td',value.rationale,row);evidenceButtons(el('td',undefined,row),value.evidence_ids);
      }
    }
  }
  function ranking(p) { const scores=p.review && p.review.combined || {}; return Math.max(0,...Object.values(scores).map(v=>v.low)); }
  function renderProposals() {
    $('proposal-list').replaceChildren();
    for (const p of [...state.proposals].sort((a,b)=>(['published','rejected'].includes(a.state)-['published','rejected'].includes(b.state)) || ranking(b)-ranking(a))) {
      const c=card($('proposal-list'),p.changes.map(x=>x.title).join(' · ') || 'No durable article change');
      el('p',p.state+(p.stale?' · Evidence changed — fresh review required':''),c);
      if(p.review && p.review.combined) el('p',Object.entries(p.review.combined).map(([org,s])=>org+': '+s.low+(s.complete?'':'–'+s.high)+' / 100 · '+s.band).join(' | '),c);
      if (p.review) for (let i=0;i<(p.review.scores||[]).length;i++) { const score=p.review.scores[i]; if(score) el('p','Reviewer '+(i+1)+': '+Object.entries(score).map(([org,s])=>org+' '+s.low+(s.complete?'':'–'+s.high)+' / 100 ('+s.band+')').join(' · '),c); }
      button(c,'Inspect evidence, objections and diff',() => openProposal(p.id));
    }
    if(!state.proposals.length) el('p','No proposals yet. Offer evidence or complete a source scan to start drafting.',$('proposal-list'));
  }
  async function openProposal(id) {
    const p=await api('proposal?id='+encodeURIComponent(id)); const parent=$('proposal-detail'); parent.replaceChildren(); parent.hidden=false;
    el('h3','Review bundle · '+p.state,parent); el('p',p.coverage_limitations,parent);
    evidenceButtons(parent,p.evidence_ids);
    if(p.review) {
      for (const [index,r] of (p.review.initial||[]).entries()) if(r) details(parent,'Independent reviewer '+(index+1)+' — '+r.readiness,r);
      for (const [index,r] of (p.review.final||[]).entries()) if(r) { el('h4','Final reviewer '+(index+1)+': '+r.readiness,parent); for(const o of r.objections) el('p',(o.material?'Material objection: ':'Observation: ')+o.text,parent); scoreTable(parent,r.organizations); }
      if(p.review.errors && p.review.errors.length) el('p',p.review.errors.join('; '),parent);
    }
    if(p.frozen) for(const article of p.frozen.articles) details(parent,'Diff: '+article.slug,article.diff);
    if(p.state==='published') { el('p','Published '+date(p.approval.at)+'. This accepted bundle is immutable.',parent); return; }
    const editors=[], placements={...(p.placements||{})}, version_bumps={...(p.version_bumps||{})};
    for(const change of p.changes) { const label=el('label',change.title+' ('+change.slug+')',parent); const text=el('textarea',undefined,label); text.rows=12; text.value=change.body; editors.push({change,text});
      if(p.article_revisions && p.article_revisions[change.slug]===null) { const placeLabel=el('label','Article placement',parent); const select=el('select',undefined,placeLabel); for(const section of state.sections[p.space]) { const option=el('option',section,select);option.value=p.space+'/'+section; } select.value=placements[change.slug]||select.options[0].value; select.onchange=()=>{placements[change.slug]=select.value;}; }
      else { const versionLabel=el('label','Document version change',parent); const select=el('select',undefined,versionLabel); for(const [value,label] of [['minor','Minor — added knowledge or workflow detail'],['major','Major — changed architecture or obligations'],['patch','Patch — correction or clarification']]) { const option=el('option',label,select); option.value=value; } select.value=version_bumps[change.slug]||'minor'; select.onchange=()=>{version_bumps[change.slug]=select.value;}; }
    }
    button(parent,'Save edits and invalidate review',async () => { await api('proposals/edit',{id:p.id,revision:p.revision,changes:editors.map(({change,text})=>({...change,body:text.value})),findings:p.findings,coverage_limitations:p.coverage_limitations,placements,version_bumps}); await refresh(); await openProposal(id); });
    const reasonLabel=el('label','Decision or revision-request rationale',parent); const reason=el('textarea',undefined,reasonLabel);
    for(const [action,label] of [['review','Run fresh review'],['request-revision','Request revision'],['defer','Defer'],['reject','Reject']]) button(parent,label,async () => { await api('proposals/'+action,{id:p.id,revision:p.revision,reason:reason.value}); await refresh(); await openProposal(id); });
    const manualLabel=el('label','Manual review: explain your publication decision if automated review is incomplete or unresolved',parent); const manual=el('textarea',undefined,manualLabel);
    button(parent,'Approve reviewed bundle and publish',async () => { const data={id:p.id,revision:p.revision}; if(manual.value.trim()) data.manual_reason=manual.value; await api('proposals/approve',data); await refresh(); await openProposal(id); notice('Validated bundle published.'); });
    parent.scrollIntoView({block:'start'});
  }
  function renderActivity() {
    $('activity-list').replaceChildren(); $('job-list').replaceChildren();
    for(const a of state.activity) { const c=card($('activity-list'),a.status || a.type); if(a.evidence) evidenceButtons(c,a.evidence); if(a.result) details(c,'Preview result',a.result); if(a.type==='monitor-import-preview' && !a.result.consumed) button(c,'Import this preview as disabled sources',async () => { await api('monitors/import',{id:a.result.id}); await refresh(); }); }
    for(const j of state.jobs) { const c=card($('job-list'),j.kind+' · '+j.state); if(j.error) el('p',j.error,c); if(j.state==='queued') el('p','Eligible: '+date(j.available),c); if(j.state==='failed') button(c,'Retry after resolving the problem',async () => { await api('jobs/retry',{id:j.id}); await refresh(); }); }
  }
  async function refresh() {
    state=await api('state');
    $('health').textContent='Source failures: '+state.health.source_failures+' · Semantic review debt: '+state.health.semantic_debt+' · Publication: '+(state.health.publication[0]?.state || 'No workflow publications');
    document.querySelectorAll('select.spaces').forEach(select=>{ if(!select.options.length) state.spaces.forEach(space=>{ const option=el('option',space,select); option.value=space; }); });
    $('repository-suggestions').replaceChildren(); state.suggestions.forEach(repo=>{const option=el('option',undefined,$('repository-suggestions'));option.value=repo;});
    renderMonitors(); renderResearch(); renderProposals(); renderActivity(); dirty=false; notice('Workspace updated.');
  }
  $('refresh').onclick=()=>perform(refresh); $('connect').onclick=()=>perform(refresh);
  perform(refresh);
  setInterval(() => { if(state && !dirty && !document.hidden && $('source-form').hidden && $('proposal-detail').hidden && state.jobs.some(j=>j.state==='queued'||j.state==='running')) perform(refresh); },5000);
})();
