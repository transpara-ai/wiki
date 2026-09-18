const {test,expect}=require('@playwright/test');

function state(extra={}) { return {monitors:[],proposals:[],investigations:[],saved:[],activity:[],jobs:[],suggestions:['transpara/example','transpara-ai/example','external/example'],spaces:['civilization','platform'],health:{source_failures:0,semantic_debt:0,publication:[]},...extra}; }

test('curator adds a disabled monitor, previews it and explicitly enables it',async({page})=>{
  let current=state(), requests=[];
  await page.route('**/api/knowledge/**',async route=>{
    const request=route.request(); const path=new URL(request.url()).pathname; const data=request.postDataJSON(); requests.push({path,data}); let result=current;
    if(path.endsWith('/monitors/add')) { const m={id:'monitor-one',revision:1,config:data.config,state:'disabled',pending:0,preview:null}; current.monitors=[m]; result=m; }
    if(path.endsWith('/monitors/preview')) { const m=current.monitors[0]; m.preview={target:m.config.target,sample:'A repository description',identity:{id:123}};m.revision++;result={job:'preview-one'}; }
    if(path.endsWith('/monitors/enable')) {current.monitors[0].state='enabled';current.monitors[0].revision++;result=current.monitors[0];}
    await route.fulfill({json:result});
  });
  await page.goto('/knowledge.html'); await expect(page.getByText('No sources configured.',{exact:false})).toBeVisible();
  await page.getByRole('button',{name:'Add source',exact:true}).click();
  await page.getByLabel('Name',{exact:true}).fill('Platform development');
  await page.getByLabel('Repository owner/name or HTTPS address').fill('transpara/example');
  await page.getByLabel('Responsible curator').fill('Curator');
  await page.getByRole('button',{name:'Save disabled source'}).click();
  await expect(page.getByRole('button',{name:'Enable',exact:true})).toBeDisabled();
  expect(current.monitors[0].state).toBe('disabled');expect(current.monitors[0].config.artifacts).toContain('reviews');
  await page.getByRole('button',{name:'Preview',exact:true}).click();
  await page.getByText('Preview: target, accessible artifacts and sample').click();
  await expect(page.getByText('A repository description',{exact:false})).toBeVisible();
  await page.getByRole('button',{name:'Enable',exact:true}).click();
  await expect(page.getByText('transpara/example · enabled · shared')).toBeVisible();
  expect(requests.filter(r=>r.path.endsWith('/enable')).length).toBe(1);
});

test('narrow-screen research captures explicitly and renders hostile source text safely',async({page})=>{
  await page.setViewportSize({width:390,height:844});
  let current=state(),calls=[];
  await page.route('**/api/knowledge/**',async route=>{
    const req=route.request();const path=new URL(req.url()).pathname;const data=req.postDataJSON();calls.push({path,data});let result=current;
    if(path.endsWith('/research/start')) {const i={id:'research-one',question:data.question,space:data.space,status:'active',findings:[],answer:''};current.investigations=[i];result=i;}
    if(path.endsWith('/research/capture'))result={job:'capture-one'};
    if(path.endsWith('/evidence'))result={evidence:[{id:'evidence-one'}]};
    await route.fulfill({json:result});
  });
  await page.goto('/knowledge.html');await page.getByRole('button',{name:'Research',exact:true}).click();
  await page.getByLabel('Question',{exact:true}).fill('How do we improve review?');
  await page.getByRole('button',{name:'Start investigation'}).click();
  await page.getByLabel('Capture a specific HTTPS source').fill('https://example.org/evidence');
  await page.getByRole('button',{name:'Capture source',exact:true}).click();
  await expect(page.getByRole('status')).toContainText('Source capture queued');
  expect(calls.some(c=>c.path.endsWith('/research/capture'))).toBe(true);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBe(true);
  await page.keyboard.press('Tab');expect(await page.evaluate(()=>document.activeElement.tagName)).not.toBe('BODY');
});

test('review shows objections and binds approval to the displayed revision',async({page})=>{
  const p={id:'proposal-one',revision:4,space:'civilization',state:'Review incomplete',findings:[],evidence_ids:['evidence-one'],coverage_limitations:'Limited evidence',changes:[{slug:'finding',title:'A finding',body:'Text <script>window.pwned=true</script>',evidence_ids:['evidence-one']}],review:{initial:[],final:[],scores:[],errors:['Reviewer unavailable']},frozen:{articles:[{slug:'finding',diff:'- Old\n+ New'}]}};
  let approved;
  await page.route('**/api/knowledge/**',async route=>{
    const req=route.request();const path=new URL(req.url()).pathname;
    if(path.endsWith('/proposals/approve')){approved=req.postDataJSON();return route.fulfill({status:409,json:{error:'Evidence changed; fresh review required'}});}
    await route.fulfill({json:path.endsWith('/proposal')?p:state({proposals:[p]})});
  });
  await page.goto('/knowledge.html');await page.getByRole('button',{name:'Review queue'}).click();await page.getByRole('button',{name:'Inspect evidence, objections and diff'}).click();
  await expect(page.getByText('Reviewer unavailable',{exact:true})).toBeVisible();
  expect(await page.evaluate(()=>window.pwned)).toBeUndefined();
  await page.getByRole('button',{name:'Approve reviewed bundle and publish'}).click();
  await expect(page.getByRole('status')).toContainText('Evidence changed');expect(approved.revision).toBe(4);
});

test('changed source access requires an explicit audience decision before resuming',async({page})=>{
  const monitor={id:'monitor-one',revision:3,state:'paused',audience_review_required:true,pending:0,preview:{sample:'Visibility changed'},config:{name:'Repository',target:'transpara/example',organization:'shared'}};
  await page.route('**/api/knowledge/**',async route=>{
    const path=new URL(route.request().url()).pathname;
    if(path.endsWith('/monitors/enable')) {
      const data=route.request().postDataJSON();
      if(!data.audience_acknowledged) return route.fulfill({status:409,json:{error:'Review the changed source access and audience before enabling'}});
      monitor.state='enabled';monitor.audience_review_required=false;monitor.revision++;
      return route.fulfill({json:monitor});
    }
    return route.fulfill({json:state({monitors:[monitor]})});
  });
  await page.goto('/knowledge.html');await page.getByRole('button',{name:'Enable',exact:true}).click();
  await expect(page.getByRole('status')).toContainText('audience before enabling');
  await page.getByLabel('I reviewed the changed source access and permitted publication audience').check();
  await page.getByRole('button',{name:'Enable',exact:true}).click();
  await expect(page.getByText('transpara/example · enabled · shared')).toBeVisible();
});

test('curator selects a document SemVer increment and invalidates review',async({page})=>{
  const p={id:'proposal-version',revision:2,space:'civilization',state:'Ready for approval',article_revisions:{finding:'existing-revision'},findings:[],evidence_ids:[],coverage_limitations:'Fixture',changes:[{slug:'finding',title:'Existing finding',body:'Updated knowledge',evidence_ids:[]}],frozen:{articles:[{slug:'finding',diff:'- version: 1.0.0\n+ version: 1.1.0'}]}};
  let edited;
  await page.route('**/api/knowledge/**',async route=>{
    const request=route.request();const path=new URL(request.url()).pathname;
    if(path.endsWith('/proposals/edit')) { edited=request.postDataJSON();p.version_bumps=edited.version_bumps;p.state='draft';p.review=null;p.revision++; }
    await route.fulfill({json:path.endsWith('/proposal')?p:state({proposals:[p]})});
  });
  await page.goto('/knowledge.html');
  await page.getByRole('button',{name:'Review queue',exact:true}).click();
  await page.getByRole('button',{name:'Inspect evidence, objections and diff'}).click();
  await expect(page.getByLabel('Document version change')).toHaveValue('minor');
  await page.getByLabel('Document version change').selectOption('major');
  await page.getByRole('button',{name:'Save edits and invalidate review'}).click();
  await expect.poll(()=>edited?.version_bumps).toEqual({finding:'major'});
  expect(p.state).toBe('draft');
});
