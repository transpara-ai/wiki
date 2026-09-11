const { test, expect } = require("@playwright/test");

const BENIGN_404 = /\/(api\/articles|inflight\.json|deploy-status\.json|favicon\.ico)$/;
const SPACE_HOMES = [
  ["civilization", "Transpara-AI Civilization Wiki — front page"],
  ["platform", "Transpara Platform Knowledge Base"],
  ["competition", "Competition Knowledge Base"],
  ["devops", "DevOps"],
];

function collectErrors(page) {
  const errors = [];
  page.on("console", (msg) => {
    if (msg.type() !== "error") return;
    const url = (msg.location() && msg.location().url) || "";
    if (BENIGN_404.test(url)) return;
    errors.push(`${msg.text()} (${url})`);
  });
  page.on("pageerror", (error) => errors.push(String(error)));
  return errors;
}

test("portal, space homes, canonical articles, and shared placement render", async ({ page }) => {
  const errors = collectErrors(page);
  await page.goto("/index.html");
  await expect(page.locator(".hub-hero h1")).toHaveText("Transpara Knowledge Hub");
  await expect(page.locator(".hub-space-card")).toHaveCount(SPACE_HOMES.length);

  for (const [space, heading] of SPACE_HOMES) {
    await page.goto("/index.html");
    await page.locator(`.hub-intro a[href="${space}/index.html"]`).click();
    await expect(page).toHaveURL(new RegExp(`/${space}/index.html$`));
    await expect(page.locator("h1.page-title")).toHaveText(heading);
    await expect(page.locator(`.space-switcher a[href="../${space}/index.html"]`))
      .toHaveClass(/current/);
  }

  await page.goto("/platform-transpara-mcp-boundary.html");
  await expect(page.locator("h1.page-title")).toHaveText("Platform and Transpara-MCP Boundary");
  await expect(page.locator(".infobox")).toContainText("Platform / Development & APIs");
  await expect(page.locator(".infobox")).toContainText("Civilization / Architecture");
  await expect(page.locator("article.body")).toContainText("a model request is never itself authorization");

  await page.goto("/event-graph.html");
  await expect(page.locator("h1.page-title")).toHaveText("The Event Graph");
  expect(errors, `console errors: ${errors.join("; ")}`).toHaveLength(0);
});

test("search enforces active-space scope and supports explicit all-space scope", async ({ page }) => {
  await page.goto("/platform/index.html");
  const input = page.locator("#wiki-search");
  const scope = page.locator("#wiki-search-scope");
  await expect(scope).toHaveValue("platform");
  await input.fill("11x");
  await expect(page.locator("#search-results .search-empty"))
    .toHaveText("No matches in this scope");
  await scope.selectOption("all");
  await expect(page.locator("#search-results a.search-result").first()).toContainText("11x");

  await page.goto("/competition/index.html");
  await expect(page.locator("#wiki-search-scope")).toHaveValue("competition");
  await page.locator("#wiki-search").fill("Cognite");
  await expect(page.locator("#search-results a.search-result").first())
    .toContainText("Cognite Data Fusion Competitive Profile");
});

test("portal and representative space content remain usable on mobile", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/index.html");
  await expect(page.locator(".hub-space-card")).toHaveCount(SPACE_HOMES.length);
  await expect(page.locator(".hub-space-card").first()).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth))
    .toBeLessThanOrEqual(391);

  await page.goto("/competition/index.html");
  await expect(page.locator("h1.page-title")).toBeVisible();
  await expect(page.locator("article.body")).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth))
    .toBeLessThanOrEqual(391);
});

test("static error states are honest", async ({ page }) => {
  const response = await page.goto("/this-route-does-not-exist.html");
  expect(response.status()).toBe(404);
  await expect(page.locator("body")).toContainText("File not found");
});
