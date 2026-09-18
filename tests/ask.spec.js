const { test, expect } = require('@playwright/test');

const models = {defaults: {provider: 'codex', codex: 'gpt-5.6-sol', claude: 'claude-sonnet-5'}, models: [
  {id: 'gpt-5.6-sol', provider: 'codex', enabled: true, effort_levels: ['low', 'medium', 'high', 'xhigh', 'max'], default_effort: 'low'},
  {id: 'claude-sonnet-5', provider: 'claude', enabled: true, effort_levels: ['low', 'medium', 'high', 'xhigh', 'max'], default_effort: 'high'},
  {id: 'claude-opus-5', provider: 'claude', enabled: false, effort_levels: ['low', 'medium', 'high', 'xhigh', 'max'], default_effort: 'high'},
  {id: 'claude-haiku-4-5-20251001', provider: 'claude', enabled: true, effort_levels: ['not-supported'], default_effort: 'not-supported'},
]};

test.beforeEach(async ({page}) => {
  await page.route('**/api/ask/models', route => route.fulfill({json: models}));
});

test('Ask defaults, scoped submission, safe answer and canonical citations', async ({page}) => {
  let submitted;
  await page.route('**/api/ask', async route => {
    submitted = route.request().postDataJSON();
    await route.fulfill({json: {model: 'gpt-5.6-sol', effort: 'high', answer: 'Context matters.',
      paragraphs: [{text: 'Context matters. <img src=x onerror=alert(1)>', article_ids: ['competitor-cognite-data-fusion']}],
      citations: [{id: 'competitor-cognite-data-fusion', title: 'Cognite profile', href: '/competitor-cognite-data-fusion.html'}],
      insufficient_evidence: true}});
  });
  await page.goto('/competition/index.html');
  await expect(page.locator('#wiki-query-mode')).toHaveValue('ask');
  await page.locator('#wiki-search').fill('Who is our closest competitor?');
  await expect(page.locator('#wiki-ask-model')).toHaveValue('gpt-5.6-sol');
  await expect(page.locator('#wiki-ask-hint')).toHaveText('Press Enter to ask');
  await expect(page.locator('#wiki-ask-submit')).toHaveCount(0);
  await page.locator('#wiki-ask-effort').selectOption('high');
  await page.locator('#wiki-search').press('Enter');
  await expect(page.locator('#wiki-ask-answer')).toContainText('Effort: High');
  await expect(page.locator('#wiki-ask-answer')).toContainText('Context matters.');
  expect(submitted).toEqual({question: 'Who is our closest competitor?', space: 'competition', provider: 'codex', model: 'gpt-5.6-sol', effort: 'high'});
  await expect(page.locator('#wiki-ask-answer img')).toHaveCount(0);
  await expect(page.locator('#wiki-ask-answer a')).toHaveAttribute('href', '/competitor-cognite-data-fusion.html');
  await page.locator('#wiki-query-mode').selectOption('search');
  await page.locator('#wiki-search').fill('Cognite');
  await expect(page.locator('#search-results .search-result').first()).toContainText('Cognite');
});

test('provider/model choices persist and unavailable models cannot be selected', async ({page}) => {
  await page.goto('/');
  await expect(page.locator('#wiki-ask-model')).toHaveValue('gpt-5.6-sol');
  await page.locator('#wiki-ask-provider').selectOption('claude');
  await expect(page.locator('#wiki-ask-model')).toHaveValue('claude-sonnet-5');
  await expect(page.locator('option[value="claude-opus-5"]')).toBeDisabled();
  await page.locator('#wiki-ask-effort').selectOption('medium');
  await page.reload();
  await expect(page.locator('#wiki-ask-provider')).toHaveValue('claude');
  await expect(page.locator('#wiki-ask-effort')).toHaveValue('medium');
  await expect(page.locator('#wiki-ask-model')).toHaveValue('claude-sonnet-5');
  await page.locator('#wiki-ask-provider').selectOption('codex');
  await expect(page.locator('#wiki-ask-effort')).toHaveValue('low');
  await page.locator('#wiki-ask-provider').selectOption('claude');
  await expect(page.locator('#wiki-ask-effort')).toHaveValue('medium');
});

test('busy, authentication, provider failures and changed scope do not show a stale answer', async ({page}) => {
  let release, requests = 0;
  await page.route('**/api/ask', async route => {
    requests++;
    await new Promise(resolve => { release = resolve; });
    await route.fulfill({status: 429, json: {error: 'Subscription usage limit reached. Retry later.'}});
  });
  await page.goto('/');
  await expect(page.locator('#wiki-ask-model')).toHaveValue('gpt-5.6-sol');
  await page.locator('#wiki-search').fill('Explain the platform');
  await page.locator('#wiki-search').press('Enter');
  await expect(page.locator('#wiki-ask-submit')).toHaveCount(0);
  await expect(page.locator('#wiki-ask-answer')).toContainText('Reading');
  await page.locator('#wiki-search').press('Enter');
  expect(requests).toBe(1);
  release();
  await expect(page.locator('#wiki-ask-answer')).toContainText('Subscription usage limit');
  await expect(page.locator('#wiki-ask-model')).toHaveValue('gpt-5.6-sol');
  await page.locator('#wiki-search-scope').selectOption('competition');
  await expect(page.locator('#wiki-ask-answer')).toBeHidden();
  await page.route('**/api/ask/models', route => route.fulfill({status: 401, json: {error: 'Sign in to ask the wiki a question.'}}));
  await page.reload();
  await expect(page.locator('#wiki-ask-answer')).toContainText('Sign in');
  await page.locator('#wiki-query-mode').selectOption('search');
  await page.locator('#wiki-search').fill('Cognite');
  await expect(page.locator('#search-results .search-result').first()).toBeVisible();
});

test('an unavailable saved model requires an explicit choice without fallback', async ({page}) => {
  await page.addInitScript(() => {
    localStorage.setItem('wiki-ask-provider', 'claude');
    localStorage.setItem('wiki-ask-model-claude', 'claude-opus-5');
  });
  await page.goto('/');
  await expect(page.locator('#wiki-ask-answer')).toContainText('selected model is unavailable');
  await expect(page.locator('#wiki-ask-model')).toHaveValue('claude-opus-5');
  await expect(page.locator('#wiki-ask-submit')).toHaveCount(0);
  await page.locator('#wiki-ask-model').selectOption('claude-sonnet-5');
  await expect(page.locator('#wiki-ask-effort')).toHaveValue('high');
});

test('models without effort control show Not supported', async ({page}) => {
  await page.goto('/');
  await expect(page.locator('#wiki-ask-effort')).toHaveValue('low');
  await page.locator('#wiki-ask-provider').selectOption('claude');
  await page.locator('#wiki-ask-model').selectOption('claude-haiku-4-5-20251001');
  await expect(page.locator('#wiki-ask-effort')).toBeDisabled();
  await expect(page.locator('#wiki-ask-effort option')).toHaveText('Not supported');
  await page.locator('#wiki-ask-model').selectOption('claude-sonnet-5');
  await expect(page.locator('#wiki-ask-effort')).toBeEnabled();
  await expect(page.locator('#wiki-ask-effort')).toHaveValue('high');
});

test('explicit follow-ups are transient and saved answers require an explicit action', async ({page}) => {
  let calls=[];
  await page.route('**/api/ask/models',route=>route.fulfill({json:{defaults:{provider:'codex',codex:'gpt-5.6-sol'},models:[{id:'gpt-5.6-sol',provider:'codex',enabled:true,effort_levels:['low'],default_effort:'low'}]}}));
  await page.route('**/api/ask',route=>{calls.push(route.request().postDataJSON());return route.fulfill({json:{answer:'Retained publication says this.',paragraphs:[{text:'Retained publication says this.',article_ids:[]}],citations:[],model:'gpt-5.6-sol',effort:'low',insufficient_evidence:true}});});
  let saves=0;
  await page.route('**/api/knowledge/reader/save',route=>{saves++;return route.fulfill({json:{id:'saved'}});});
  await page.goto('/index.html');
  await page.locator('#wiki-search').fill('Explain the source');await page.locator('#wiki-search').press('Enter');
  await expect(page.getByRole('button',{name:'Ask a follow-up'})).toBeVisible();expect(saves).toBe(0);
  await page.getByRole('button',{name:'Ask a follow-up'}).click();await page.locator('#wiki-search').fill('What remains unknown?');await page.locator('#wiki-search').press('Enter');
  await expect(page.getByRole('button',{name:'Save answer'})).toBeVisible();expect(calls[1].history).toHaveLength(1);
  await page.getByRole('button',{name:'Save answer'}).click();await expect(page.locator('#wiki-ask-answer')).toContainText('saved to your account');expect(saves).toBe(1);
  const stored=await page.evaluate(()=>JSON.stringify(localStorage));expect(stored).not.toContain('Retained publication');
});
