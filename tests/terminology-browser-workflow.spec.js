const {test, expect} = require('@playwright/test');
const crypto = require('node:crypto');
const {snapshot} = require('./fixtures/terminology');

function fixture() {
  const data = {...snapshot(), browser_service:true};
  return {data, proposals:[], releases:[], calls:[], published:false,
    stage:null,
    state() {return {proposals:this.proposals, releases:this.releases,
      capabilities:{publication:true,passkey_enrolled:true,scan:true}};}};
}
async function routes(page, f) {
  await page.route('**/api/terminology/**', async route => {
    const request = route.request();
    const path = new URL(request.url()).pathname.replace('/api/terminology/', '');
    const body = request.method() === 'POST' ? request.postDataJSON() : null;
    f.calls.push({method:request.method(), path, body});
    if (path === 'snapshot') return route.fulfill({json:f.data});
    if (path === 'state') return route.fulfill({json:f.state()});
    if (path === 'proposals') {
      f.proposals.push({id:'proposal-one',state:'pending',proposal:body.proposal});
      return route.fulfill({json:{id:'proposal-one'}});
    }
    if (path === 'prepare') {
      const source = 'Complete dictionary document\n<script>window.stagePwned=true</script>\nflux adapter · 🙂';
      f.stage = {id:'e'.repeat(32),actor:'verified-human',source,
        digest:crypto.createHash('sha256').update(source).digest('hex'),
        base_digest:'a'.repeat(64),version:'0.2.0',scope:{repo:'transpara-ai/wiki',product:'Wiki'},
        expires_at:2000000000,nonce:Buffer.alloc(32,7).toString('base64url'),
        diff:'+ flux adapter\n+ An example product component.'};
      return route.fulfill({json:{stage:f.stage}});
    }
    if (path === 'approval/options') {
      const {diff,...stage} = f.stage;
      function stable(value) {
        if (Array.isArray(value)) return '[' + value.map(stable).join(',') + ']';
        if (value && typeof value === 'object') return '{' + Object.keys(value).sort().map(key => JSON.stringify(key) + ':' + stable(value[key])).join(',') + '}';
        return JSON.stringify(value);
      }
      const challenge = crypto.createHash('sha256').update('transpara-dictionary-browser-approval-v2\0' + stable(stage) + '\n').digest('base64url');
      return route.fulfill({json:{stage_id:stage.id,publicKey:{challenge:f.tamperChallenge ? 'Y2hhbGxlbmdl' : challenge,
        rpId:'127.0.0.1',allowCredentials:[{id:'a2V5',type:'public-key'}],userVerification:'required'}}});
    }
    if (path === 'publish') {
      f.published = true;
      f.proposals[0].state = 'published'; f.data.dictionary_version = '0.2.0';
      f.releases.push({revision:1,version:'0.2.0',digest:'c'.repeat(64),
        human_identity:'human-maintainer',workload_identity:'independent-publisher'});
      return route.fulfill({json:{published:true}});
    }
    if (path === 'scan' && request.method() === 'POST') {
      f.scan = body; return route.fulfill({status:202,json:{job:{id:'scan-one',state:'queued'}}});
    }
    if (path === 'scan') return route.fulfill({json:{job:{id:'scan-one',state:'complete',report:{
      conformance:'not_assessed',source:{kind:'repo',commit:'d'.repeat(40)},coverage:{complete:false},
      documents:[{label:'README.md'}],findings:[{label:'README.md',message:'Review vocabulary: utilize.'}],
      rewrite:{status:'draft',documents:[{label:'README.md',original:'Utilize the valve.',draft:'Use the valve.',diff:'-Utilize the valve.\n+Use the valve.'}],remaining_deviations:[]}}}}});
    return route.fulfill({status:404,json:{error:'Fixture route not found.'}});
  });
}

// This test verifies browser wiring, exact displayed bytes, and the user's
// deliberate approval gesture. Cryptographic verification is tested separately
// in the authority service with real disposable keys; this fixture grants none.
test('browser submits, reviews complete bytes, uses a passkey and publishes', async ({page}) => {
  const f = fixture(); await routes(page, f);
  await page.addInitScript(() => {
    Object.defineProperty(navigator, 'credentials', {value:{get:async options => {
      window.passkeyRequest = {uv:options.publicKey.userVerification,
        challenge:Array.from(new Uint8Array(options.publicKey.challenge))};
      return {id:'key',rawId:Uint8Array.of(1,2).buffer,type:'public-key',response:{
        authenticatorData:Uint8Array.of(3).buffer,clientDataJSON:Uint8Array.of(4).buffer,
        signature:Uint8Array.of(5).buffer,userHandle:null},getClientExtensionResults:()=>({})};
    }}});
  });
  await page.goto('/terminology.html');
  await page.getByRole('button', {name:'flux adapter',exact:false}).click();
  await page.getByLabel('Classification', {exact:true}).selectOption('immutable');
  await page.getByLabel('Definition and meaning boundaries').fill('An example product component.');
  await page.getByRole('button', {name:'Submit proposal',exact:true}).click();
  await expect(page.getByRole('status').first()).toContainText('Proposal submitted');
  expect(f.proposals[0].proposal).toMatchObject({candidate_id:'candidate-one',term:'flux adapter',
    expected_dictionary_digest:'a'.repeat(64),context_digests:['b'.repeat(64)]});
  await page.getByRole('button', {name:'Contributions',exact:true}).click();
  await page.locator('[data-proposal-id]').check();
  await page.getByRole('button', {name:'Review selected proposals for publication'}).click();
  await expect(page.locator('#term-stage-diff')).toContainText('+ flux adapter');
  await expect(page.locator('#term-stage-source')).toContainText('<script>');
  expect(await page.evaluate(() => window.stagePwned)).toBeUndefined();
  await expect(page.getByRole('button', {name:'Approve with passkey and publish'})).toBeDisabled();
  expect(f.published).toBe(false);
  await page.getByLabel('I reviewed the complete document and authorize this publication.').check();
  await page.screenshot({path:test.info().outputPath('terminology-publication-desktop.png'),fullPage:true});
  await page.getByRole('button', {name:'Approve with passkey and publish'}).click();
  await expect(page.getByRole('status').first()).toContainText('Dictionary published');
  expect(f.published).toBe(true);
  expect(await page.evaluate(() => window.passkeyRequest.uv)).toBe('required');
  expect(f.calls.find(call => call.path === 'publish').body).toMatchObject({
    stage_id:'e'.repeat(32),credential:{type:'public-key',response:{signature:'BQ'}}});
  await page.getByRole('button', {name:'Source revision',exact:true}).click();
  await expect(page.locator('#term-release-history')).toContainText('human-maintainer');
  await expect(page.locator('#term-release-history')).toContainText('independent-publisher');
});

test('repository rewrite retains originals, records commit and incomplete coverage on mobile', async ({page}) => {
  const f = fixture(); await routes(page, f);
  await page.setViewportSize({width:390,height:844});
  await page.goto('/terminology.html');
  await page.getByRole('button', {name:'Scan and rewrite',exact:true}).click();
  await page.getByLabel('Source', {exact:true}).selectOption('repo');
  await page.getByLabel('URL', {exact:true}).fill('https://github.com/transpara-ai/example');
  await page.getByLabel('Branch, tag or commit (optional)').fill('main');
  await page.getByLabel('Paths to include, one pattern per line (optional)').fill('docs/**\nREADME.md');
  await page.getByLabel('Result', {exact:true}).selectOption('rewrite');
  await page.getByRole('button', {name:'Run scanner',exact:true}).click();
  await expect(page.locator('#term-scan-status')).toContainText('Scan complete');
  expect(f.scan).toEqual({source:{type:'repo',url:'https://github.com/transpara-ai/example',ref:'main',paths:['docs/**','README.md']},rewrite:true});
  await expect(page.locator('#term-scan-report')).toContainText('Coverage is incomplete');
  await expect(page.locator('#term-scan-report')).toContainText('Repository commit: ' + 'd'.repeat(40));
  await expect(page.locator('#term-scan-report')).toContainText('Utilize the valve.');
  await expect(page.locator('#term-scan-report')).toContainText('Use the valve.');
  await expect(page.getByRole('button', {name:'Download report',exact:true})).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.screenshot({path:test.info().outputPath('terminology-scanner-mobile.png'),fullPage:true});
});

test('browser can submit a new technical term without a scanner candidate', async ({page}) => {
  const f = fixture(); await routes(page, f);
  await page.goto('/terminology.html');
  await page.getByRole('button', {name:'Propose a new technical term',exact:true}).click();
  await page.getByLabel('Canonical term', {exact:true}).fill('PulseStore');
  await page.getByLabel('Definition and meaning boundaries').fill('The storage component for this example.');
  await page.getByLabel('Approved forms, one per line').fill('PulseStore');
  await page.getByLabel('Repository scope', {exact:true}).fill('transpara-ai/example');
  await page.getByLabel('Product scope', {exact:true}).fill('example');
  await page.getByRole('button', {name:'Submit proposal',exact:true}).click();
  await expect(page.getByRole('status').first()).toContainText('Proposal submitted');
  expect(f.proposals[0].proposal).toMatchObject({candidate_id:null,term:'PulseStore',decision:'immutable',context_digests:[]});
});

test('cancelling the browser passkey prompt cannot call publication', async ({page}) => {
  const f = fixture(); f.proposals.push({id:'one',state:'pending',term:'valve',scope:{repo:'example',product:'example'}});
  await routes(page, f);
  await page.addInitScript(() => Object.defineProperty(navigator, 'credentials', {value:{get:async () => {
    throw new DOMException('Cancelled', 'NotAllowedError');
  }}}));
  await page.goto('/terminology.html');
  await page.getByRole('button', {name:'Contributions',exact:true}).click();
  await page.locator('[data-proposal-id]').check();
  await page.getByRole('button', {name:'Review selected proposals for publication'}).click();
  await page.getByLabel('I reviewed the complete document and authorize this publication.').check();
  await page.getByRole('button', {name:'Approve with passkey and publish'}).click();
  await expect(page.getByRole('status').first()).toContainText('Passkey approval was cancelled');
  expect(f.calls.filter(call => call.path === 'publish')).toEqual([]);
  await expect(page.getByLabel('I reviewed the complete document and authorize this publication.')).not.toBeChecked();
});


test('browser rejects a publication challenge for different hidden bytes before asking a passkey', async ({page}) => {
  const f = fixture(); f.tamperChallenge = true;
  f.proposals.push({id:'one',state:'pending',term:'valve',scope:{repo:'example',product:'example'}});
  await routes(page, f);
  await page.addInitScript(() => Object.defineProperty(navigator, 'credentials', {value:{get:async () => {
    window.passkeyWasRequested = true;
    throw new Error('Must never reach a passkey for mismatched bytes.');
  }}}));
  await page.goto('/terminology.html');
  await page.getByRole('button', {name:'Contributions',exact:true}).click();
  await page.locator('[data-proposal-id]').check();
  await page.getByRole('button', {name:'Review selected proposals for publication'}).click();
  await page.getByLabel('I reviewed the complete document and authorize this publication.').check();
  await page.getByRole('button', {name:'Approve with passkey and publish'}).click();
  await expect(page.getByRole('status')).toContainText('does not match the displayed document');
  expect(await page.evaluate(() => window.passkeyWasRequested)).toBeUndefined();
  expect(f.calls.filter(call => call.path === 'publish')).toEqual([]);
});
