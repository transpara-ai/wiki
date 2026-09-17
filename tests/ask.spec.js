const { test, expect } = require('@playwright/test');

const models = {defaults: {provider: 'codex', codex: 'gpt-5.6-sol', claude: 'claude-sonnet-5'}, models: [
  {id: 'gpt-5.6-sol', provider: 'codex', enabled: true},
  {id: 'claude-sonnet-5', provider: 'claude', enabled: true},
  {id: 'claude-opus-5', provider: 'claude', enabled: false},
]};

test.beforeEach(async ({page}) => {
  await page.route('**/api/ask/models', route => route.fulfill({json: models}));
});

test('Ask defaults, scoped submission, safe answer and canonical citations', async ({page}) => {
  let submitted;
  await page.route('**/api/ask', async route => {
    submitted = route.request().postDataJSON();
    await route.fulfill({json: {model: 'gpt-5.6-sol', answer: 'Context matters.',
      paragraphs: [{text: 'Context matters. <img src=x onerror=alert(1)>', article_ids: ['competitor-cognite-data-fusion']}],
      citations: [{id: 'competitor-cognite-data-fusion', title: 'Cognite profile', href: '/competitor-cognite-data-fusion.html'}],
      insufficient_evidence: true}});
  });
  await page.goto('/competition/index.html');
  await expect(page.locator('#wiki-query-mode')).toHaveValue('ask');
  await page.locator('#wiki-search').fill('Who is our closest competitor?');
  await expect(page.locator('#wiki-ask-submit')).toBeEnabled();
  await page.locator('#wiki-search').press('Enter');
  await expect(page.locator('#wiki-ask-answer')).toContainText('Context matters.');
  expect(submitted).toEqual({question: 'Who is our closest competitor?', space: 'competition', provider: 'codex', model: 'gpt-5.6-sol'});
  await expect(page.locator('#wiki-ask-answer img')).toHaveCount(0);
  await expect(page.locator('#wiki-ask-answer a')).toHaveAttribute('href', '/competitor-cognite-data-fusion.html');
  await page.locator('#wiki-query-mode').selectOption('search');
  await page.locator('#wiki-search').fill('Cognite');
  await expect(page.locator('#search-results .search-result').first()).toContainText('Cognite');
});

test('provider/model choices persist and unavailable models cannot be selected', async ({page}) => {
  await page.goto('/');
  await expect(page.locator('#wiki-ask-submit')).toBeEnabled();
  await page.locator('#wiki-ask-provider').selectOption('claude');
  await expect(page.locator('#wiki-ask-model')).toHaveValue('claude-sonnet-5');
  await expect(page.locator('option[value="claude-opus-5"]')).toBeDisabled();
  await page.reload();
  await expect(page.locator('#wiki-ask-provider')).toHaveValue('claude');
  await expect(page.locator('#wiki-ask-model')).toHaveValue('claude-sonnet-5');
});

test('busy, authentication, provider failures and changed scope do not show a stale answer', async ({page}) => {
  let release;
  await page.route('**/api/ask', async route => {
    await new Promise(resolve => { release = resolve; });
    await route.fulfill({status: 429, json: {error: 'Subscription usage limit reached. Retry later.'}});
  });
  await page.goto('/');
  await expect(page.locator('#wiki-ask-submit')).toBeEnabled();
  await page.locator('#wiki-search').fill('Explain the platform');
  await page.locator('#wiki-ask-submit').click();
  await expect(page.locator('#wiki-ask-submit')).toBeDisabled();
  await expect(page.locator('#wiki-ask-answer')).toContainText('Reading');
  release();
  await expect(page.locator('#wiki-ask-answer')).toContainText('Subscription usage limit');
  await expect(page.locator('#wiki-ask-submit')).toBeEnabled();
  await page.locator('#wiki-search-scope').selectOption('competition');
  await expect(page.locator('#wiki-ask-answer')).toBeHidden();
  await page.route('**/api/ask/models', route => route.fulfill({status: 401, json: {error: 'Sign in to ask the wiki a question.'}}));
  await page.reload();
  await expect(page.locator('#wiki-ask-answer')).toContainText('Sign in');
  await page.locator('#wiki-query-mode').selectOption('search');
  await page.locator('#wiki-search').fill('Cognite');
  await expect(page.locator('#search-results .search-result').first()).toBeVisible();
});
