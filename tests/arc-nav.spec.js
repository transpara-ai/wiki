const { test, expect } = require("@playwright/test");

test("homepage is article-first and does not mount the progress chart", async ({ page }) => {
  await page.goto("/index.html");

  await expect(page.locator("h1.page-title")).toHaveText("Transpara-AI Civilization Wiki");
  const body = page.locator("article.body");
  await expect(body).toContainText("The Transpara-AI Civilization Wiki is the memory and interpretation layer");
  await expect(body).toContainText("The epiphany was this");
  await expect(body).toContainText("Front-page authority boundary");
  await expect(body.locator('a[href="primitive-basis.html"]').first()).toBeVisible();
  await expect(body.locator('a[href="the-20-primitives.html"]').first()).toBeVisible();
  await expect(body.locator('a[href="civilization-institutional-substrate.html"]')).toBeVisible();
  await expect(body.locator("table").first().locator('a[href="civilization-arc.html"]')).toHaveCount(0);
  await expect(body.locator("table").first().locator('a[href="sakana-ai-evaluation.html"]')).toHaveCount(0);
  await expect(body.locator("table").first().locator('a[href="hermes-agent.html"]')).toHaveCount(0);
  await expect(page.locator(".civilization-arc-nav")).toHaveCount(0);
});

test("topbar search finds visible research pages", async ({ page }) => {
  await page.goto("/index.html");

  await expect(page.locator(".brand")).toHaveText("Transpara-AI Civilization Wiki");
  const search = page.locator("#wiki-search");
  await expect(search).toBeVisible();

  await search.fill("Sakana adjacent landscape");
  await expect(page.locator('.search-results a[href="sakana-ai-adjacent-landscape.html"]')).toBeVisible();

  await search.fill("Hermes self-evolution evaluation");
  await expect(page.locator('.search-results a[href="hermes-agent.html"]')).toBeVisible();
});

test("topbar exposes source index and browser ingest surfaces", async ({ page }) => {
  await page.goto("/index.html");

  await expect(page.locator('.top-links a[href="sources.html"]')).toBeVisible();
  await expect(page.locator('.top-links a[href="ingest.html"]')).toBeVisible();
  await expect(page.locator('.top-links a[href="repos.html"]')).toBeVisible();

  await page.locator('.top-links a[href="ingest.html"]').click();
  await expect(page.locator("h1.page-title")).toHaveText("Wiki Source Ingest");
  await expect(page.locator("#documents")).toBeVisible();
  await expect(page.locator("#external-urls")).toBeVisible();
  await expect(page.locator("#target-slug")).toBeVisible();
  await expect(page.locator("#supersedes")).toBeVisible();
  await expect(page.locator("#authoring-token")).toBeVisible();
  await expect(page.locator('button:has-text("Ingest and rebuild")')).toBeVisible();
});

test("sidebar exposes Transpara-AI repo sections and repo README pages", async ({ page }) => {
  await page.goto("/index.html");

  const repos = page.locator('.repo-side-group[data-tier="repos"]');
  if (await repos.count() === 0) {
    test.skip(true, "sibling Transpara-AI repo tree is not available in this build");
  }
  await expect(repos.locator("summary")).toContainText("Transpara-AI Repos");
  await repos.locator("summary").click();

  await expect(repos.locator(".repo-nav-section h6").filter({ hasText: "Civilization" })).toBeVisible();
  await expect(repos.locator(".repo-nav-section h6").filter({ hasText: "Platform" })).toBeVisible();
  await expect(repos.locator(".repo-nav-section h6").filter({ hasText: "Other" })).toBeVisible();
  await expect(repos.locator('a[href="repo-hive.html"]')).toBeVisible();
  await expect(repos.locator('a[href="repo-platform.html"]')).toBeVisible();
  await expect(repos.locator('a[href="repo-transpara-mcp.html"]')).toBeVisible();
  const civilization = repos.locator(".repo-nav-section").filter({ hasText: "Civilization" });
  const platform = repos.locator(".repo-nav-section").filter({ hasText: "Platform" });
  const other = repos.locator(".repo-nav-section").filter({ hasText: "Other" });
  await expect(civilization.locator('a[href="repo-docs.html"]')).toBeVisible();
  await expect(civilization.locator('a[href="repo-agentic-dev-console.html"]')).toHaveCount(0);
  await expect(platform.locator('a[href="repo-agentic-dev-console.html"]')).toBeVisible();
  await expect(platform.locator('a[href="repo-upstream-fork-sync.html"]')).toHaveCount(0);
  await expect(other.locator('a[href="repo-upstream-fork-sync.html"]')).toBeVisible();

  await repos.locator('a[href="repo-transpara-mcp.html"]').click();
  await expect(page.locator("h1.page-title")).toHaveText("transpara-mcp repository");
  await expect(page.locator(".repo-side-group")).toHaveAttribute("open", "");
  await expect(page.locator('.repo-side-group a.current[href="repo-transpara-mcp.html"]')).toBeVisible();
  await expect(page.locator(".repo-infobox")).toContainText("Platform");
  await expect(page.locator(".repo-infobox")).toContainText("Fork tracks transpara/transpara-mcp");
  await expect(page.locator(".repo-infobox")).toContainText("Branches");
  await expect(page.locator(".repo-readme")).toContainText("Transpara MCP Server");

  await page.goto("/repo-wiki.html");
  await expect(page.locator(".repo-infobox")).toContainText("Transpara-AI native origin");
  await expect(page.locator(".repo-infobox")).toContainText(/branches; [0-9]+ total commits/);
});

test("article source references are clickable and open served source pages", async ({ page }) => {
  await page.goto("/sakana-ai-evaluation.html");

  const panel = page.locator(".source-panel");
  await expect(panel).toBeVisible();
  const updates = page.locator(".source-update-panel");
  await expect(updates).toBeVisible();
  await expect(updates).toContainText("Sakana AI Capability Evaluation v1.1.0");
  await expect(updates).not.toContainText("raw/inbox/");
  await expect(updates).not.toContainText("supersedes:");
  await expect(updates.locator('a[href^="source/"]').first()).toBeVisible();
  const updatesAfterArticle = await page.evaluate(() => {
    const article = document.querySelector("article.body");
    const panel = document.querySelector(".source-update-panel");
    return !!(article && panel && (article.compareDocumentPosition(panel) & Node.DOCUMENT_POSITION_FOLLOWING));
  });
  expect(updatesAfterArticle).toBe(true);
  await panel.locator("summary").click();
  const link = panel.locator('a[href^="source/"]').first();
  await expect(link).toBeVisible();
  const href = await link.getAttribute("href");
  expect(href).toMatch(/^source\/[a-f0-9]+\.html$/);

  await link.click();
  await expect(page.locator(".source-rendered-markdown")).toBeVisible();
  await expect(page.locator(".source-text")).toHaveCount(0);
  await expect(page.locator(".source-path code")).toContainText(/Sakana|raw\/civilization/);
});

test("investigation pages expose grouped raw documents and contribution boxes", async ({ page }) => {
  await page.goto("/sakana-ai-evaluation.html");

  const infobox = page.locator(".infobox");
  await expect(infobox).toContainText("Raw docs");
  await expect
    .poll(() => infobox.locator('a[href^="source/"]').count(), { timeout: 5000 })
    .toBeGreaterThanOrEqual(1);
  await expect(infobox.locator('a[href^="source/"]').filter({ hasText: /Sakana AI Capability Evaluation/ }).first()).toBeVisible();
  await expect(page.locator(".contribution-box")).toContainText("slated as potential future usage.");
  await expect(page.locator("article.body").locator("code").filter({ hasText: "raw/inbox/" })).toHaveCount(0);
  await expect(page.locator("article.body").locator("code").filter({ hasText: "corpus/copied" })).toHaveCount(0);
  const contributionBeforeContents = await page.evaluate(() => {
    const contribution = document.querySelector(".contribution-box");
    const toc = document.querySelector(".toc");
    return !!(contribution && toc && (contribution.compareDocumentPosition(toc) & Node.DOCUMENT_POSITION_FOLLOWING));
  });
  expect(contributionBeforeContents).toBe(true);

  const investigations = page.locator('.side-group[data-tier="investigation"]');
  await expect(investigations.locator("summary").first()).toContainText("18");
  await investigations.evaluate((el) => { el.open = true; });
  const sakana = investigations.locator(".nav-subgroup").filter({ hasText: "Sakana AI" });
  await expect(sakana.locator("summary")).toContainText(/[1-9][0-9]*/);
  await sakana.evaluate((el) => { el.open = true; });
  await expect(sakana.locator('a[href="sakana-ai-evaluation.html"]')).toBeVisible();
  await expect(sakana.locator('a[href="sakana-ai-adjacent-landscape.html"]')).toBeVisible();
  const openArrow = await sakana.locator("summary").evaluate((el) => getComputedStyle(el, "::before").content);
  await sakana.locator("summary").click();
  await expect(sakana).not.toHaveAttribute("open", "");
  const closedArrow = await sakana.locator("summary").evaluate((el) => getComputedStyle(el, "::before").content);
  expect(closedArrow).toContain("›");
  expect(closedArrow).not.toBe(openArrow);

  await expect(investigations.locator(".nav-subgroup").filter({ hasText: "Google Open Knowledge Format" })).toHaveCount(0);
  const okf = investigations.locator('.nav-article-row a[href="google-open-knowledge-format-capability-evaluation.html"]');
  await expect(okf).toHaveText("Google Open Knowledge Format");
  await expect(okf).toHaveAttribute("title", "Google Open Knowledge Format Capability Evaluation");
  await expect(okf.locator("xpath=..").locator("em")).toHaveText("1");

  await page.goto("/hermes-agent.html");
  await expect(page.locator("h1.page-title")).toHaveText("Hermes Agent");
  await expect(page.locator(".contribution-box")).toContainText("U7 CapabilityArtifact governance and U8 CapabilityEvolution sequencing");
  await expect
    .poll(() => page.locator(".infobox").locator('a[href^="source/"]').count(), { timeout: 5000 })
    .toBeGreaterThanOrEqual(1);
  await expect(page.locator('.side-group[data-tier="investigation"] .nav-subgroup').filter({ hasText: "Hermes Agent" })).toHaveCount(0);
  const hermes = page.locator('.side-group[data-tier="investigation"] .nav-article-row a[href="hermes-agent.html"]');
  await expect(hermes).toHaveText("Hermes Agent");
  await expect(hermes).toHaveAttribute("title", "Hermes Agent");
  await expect(hermes).toHaveClass(/current/);
  await expect(hermes.locator("xpath=..").locator("em")).toContainText(/[1-9][0-9]*/);
});

test("OKF browser-ingested research appears as a navigable investigation article", async ({ page }) => {
  await page.goto("/google-open-knowledge-format-capability-evaluation.html");

  await expect(page.locator("h1.page-title")).toHaveText("Google Open Knowledge Format Capability Evaluation");
  await expect(page.locator(".contribution-box")).toContainText("slated as potential future usage.");
  await expect(page.locator(".infobox").locator('a[href^="source/"]')).toHaveCount(1);
  await expect(page.locator(".infobox")).toContainText("Google Open Knowledge Format (OKF) Capability Evaluation v1.0.0");
  await expect(page.locator("article.body")).toContainText("OKF standardizes the envelope; the Civilization governs the contents.");

  const rawDoc = page.locator(".infobox").locator('a[href^="source/"]').first();
  await rawDoc.click();
  await expect(page.locator(".source-rendered-markdown")).toBeVisible();
  await expect(page.locator("h1.page-title")).toContainText("Google Open Knowledge Format (OKF) Capability Evaluation v1.0.0");
});

test("markdown source links render formatted markdown, not raw text", async ({ page }) => {
  await page.goto("/sakana-ai-evaluation.html");

  const rawDoc = page.locator(".infobox").locator('a[href^="source/"]').filter({ hasText: "Sakana AI Capability Evaluation" }).first();
  await expect(rawDoc).toBeVisible();
  await rawDoc.click();

  await expect(page.locator("h1.page-title")).toContainText("Sakana AI Capability Evaluation v1.1.0");
  await expect(page.locator(".source-meta-table")).toContainText("TAI-RES-2026-001");
  await expect(page.locator(".source-rendered-markdown")).toBeVisible();
  await expect(page.locator(".source-rendered-markdown h2").filter({ hasText: "Revision History" })).toBeVisible();
  await expect(page.locator(".source-text")).toHaveCount(0);
});

test("wiki sidebar is wider by default and supports persistent resizing", async ({ page }) => {
  await page.goto("/index.html");

  const sidebar = page.locator(".sidebar");
  const resizer = page.locator(".sidebar-resizer");
  await expect(sidebar).toBeVisible();
  await expect(resizer).toBeVisible();

  const defaultWidth = await sidebar.evaluate((el) => Math.round(el.getBoundingClientRect().width));
  expect(defaultWidth).toBeGreaterThanOrEqual(330);

  await resizer.focus();
  await page.keyboard.press("End");
  await expect
    .poll(() => sidebar.evaluate((el) => Math.round(el.getBoundingClientRect().width)), { timeout: 5000 })
    .toBeGreaterThan(500);

  await page.goto("/gate-k.html");
  const restored = await page.locator(".sidebar").evaluate((el) => Math.round(el.getBoundingClientRect().width));
  expect(restored).toBeGreaterThan(500);
});

test("arc page renders with tracks structure inside normalized wiki chrome", async ({ page }) => {
  await page.goto("/civilization-arc.html");

  const nav = page.locator(".civilization-arc-nav");
  await expect(nav).toBeVisible();
  await expect(page.locator("h1.page-title")).toHaveText("Civilization Progress Chart");
  await expect(page.locator(".topbar")).toBeVisible();
  await expect(page.locator(".sidebar")).toBeVisible();

  // SVG is rendered with the three track bands and now-line.
  await expect(page.locator("svg.arc-svg")).toBeVisible();
  await expect(page.locator(".arc-track-band")).toHaveCount(3);
  await expect(page.locator(".arc-now-line")).toHaveCount(1);

  // Item groups are drawn.
  const itemGroups = page.locator(".arc-item-group");
  await expect(itemGroups.first()).toBeVisible();
  const count = await itemGroups.count();
  expect(count).toBeGreaterThan(0);
});

test("wiki sidebar uses collapsible groups and preserves scroll across article clicks", async ({ page }) => {
  await page.goto("/index.html");

  const sidebar = page.locator(".sidebar");
  await expect(sidebar).toBeVisible();
  await expect(sidebar.locator(".side-tools")).toContainText("Contents");

  const architecture = sidebar.locator('.side-group[data-tier="architecture"]');
  await expect(architecture.locator("summary")).toBeVisible();
  await expect(architecture).not.toHaveAttribute("open", "");

  await architecture.locator("summary").click();
  await expect(architecture).toHaveAttribute("open", "");
  await expect(architecture.locator('a[href="gate-k.html"]')).toBeVisible();

  await sidebar.evaluate((el) => { el.scrollTop = 240; });
  await architecture.locator('a[href="gate-k.html"]').click();
  await expect(page.locator("h1.page-title")).toHaveText("Gate K");

  await expect(sidebar.locator('.side-group[data-tier="architecture"]')).toHaveAttribute("open", "");
  await expect(sidebar.locator('a.current[href="gate-k.html"]')).toBeVisible();
  const restored = await sidebar.evaluate((el) => el.scrollTop);
  expect(restored).toBeGreaterThan(100);
});

test("arc gutter labels stay inside the SVG viewBox", async ({ page }) => {
  await page.goto("/civilization-arc.html");
  await expect(page.locator("svg.arc-svg")).toBeVisible();

  async function clippedLabels() {
    return page.evaluate(() =>
      [...document.querySelectorAll(".arc-track-label, .arc-subrow-label")]
        .map((el) => ({ text: el.textContent, x: el.getBBox().x }))
        .filter((label) => label.x < -0.5)
    );
  }

  expect(await clippedLabels()).toEqual([]);
  await page.locator('[data-arc-group="repo"]').click();
  expect(await clippedLabels()).toEqual([]);
});

test("arc page displays operation progress evidence", async ({ page }) => {
  await page.goto("/civilization-arc.html");

  const panel = page.locator(".arc-progress-panel");
  await expect(panel).toBeVisible();
  await expect(panel).toContainText("Progress evidence snapshot");
  await expect(panel).toContainText("Test 001 Remains YELLOW");
  await expect(panel).toContainText("not live truth");
  await expect(panel).not.toContainText(/operator_notes|raw_issue_body/);
  await expect(panel).not.toContainText(/transpara-ai\/docs|docs#[0-9]+/i);

  await expect(panel.locator('a[href="https://github.com/transpara-ai/operation/pull/28"]')).toBeVisible();
  await expect(panel.locator('a[href="https://github.com/transpara-ai/operation/issues/26"]')).toBeVisible();
  await expect(panel.locator('a[href*="github.com/transpara-ai/docs"]')).toHaveCount(0);
});

test("marker click populates the detail panel", async ({ page }) => {
  await page.goto("/civilization-arc.html");

  const nav = page.locator(".civilization-arc-nav");
  await expect(nav).toBeVisible();
  await expect(page.locator("svg.arc-svg")).toBeVisible();

  // Click the first rendered item marker.
  const firstMarker = page.locator("[data-arc-item]").first();
  await expect(firstMarker).toBeVisible();
  await firstMarker.click();

  // Selection is reflected on the nav root.
  await expect(nav).toHaveAttribute("data-has-selection", "true");

  // Detail panel is populated (no longer shows the hint text).
  const detailPanel = nav.locator(".arc-detail-panel");
  await expect(detailPanel).toBeVisible();
  await expect(detailPanel).not.toContainText("Select a marker for details");

  // Detail panel shows a code and badge.
  await expect(detailPanel.locator(".arc-detail-code")).toBeVisible();
  await expect(detailPanel.locator(".arc-badge")).toBeVisible();
});

test("standalone arc page loads and mounts the nav", async ({ page }) => {
  await page.goto("/civilization-arc.html");

  const nav = page.locator(".civilization-arc-nav");
  await expect(nav).toBeVisible();
  await expect(page.locator("svg.arc-svg")).toBeVisible();
  await expect(page.locator(".arc-track-band")).toHaveCount(3);
  await expect(page.locator(".arc-now-line")).toHaveCount(1);
});

test("underscore standalone arc route remains available", async ({ page }) => {
  await page.goto("/civilization_arc.html");

  const nav = page.locator(".civilization-arc-nav");
  await expect(nav).toBeVisible();
  await expect(page.locator("svg.arc-svg")).toBeVisible();
});

test("arc remains inside the mobile viewport", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/civilization-arc.html");

  const nav = page.locator(".civilization-arc-nav");
  await expect(nav).toBeVisible();
  const overflow = await nav.evaluate((el) => el.scrollWidth - el.clientWidth);
  expect(overflow).toBeLessThanOrEqual(1);
});

test("narrow viewport: the arc fits the frame at default zoom (no internal or page scroll)", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 800 });
  await page.goto("/civilization-arc.html");

  const nav = page.locator(".civilization-arc-nav");
  await expect(nav).toBeVisible();
  await expect(page.locator("svg.arc-svg")).toBeVisible();

  // At the default zoom ("Fit") the whole arc fits the frame — no internal scroll.
  const frameOverflow = await page.locator(".arc-frame").evaluate(function (el) {
    return el.scrollWidth - el.clientWidth;
  });
  expect(frameOverflow).toBeLessThanOrEqual(1);

  // The document body must NOT scroll horizontally either.
  const bodyScrollsX = await page.evaluate(function () {
    return document.body.scrollWidth > window.innerWidth + 1;
  });
  expect(bodyScrollsX).toBeFalsy();
});

test("zooming in widens the arc past the frame (scroll for detail), page never scrolls X", async ({ page }) => {
  await page.setViewportSize({ width: 900, height: 800 });
  await page.goto("/civilization-arc.html");
  const svg = page.locator("svg.arc-svg");
  await expect(svg).toBeVisible();
  const fitWidth = await svg.evaluate((el) => el.getBoundingClientRect().width);

  // Zoom in a couple of steps via the toolbar "+".
  const zoomIn = page.locator('[data-arc-zoom="in"]');
  await zoomIn.click();
  await zoomIn.click();
  await expect
    .poll(async () => svg.evaluate((el) => el.getBoundingClientRect().width), { timeout: 5000 })
    .toBeGreaterThan(fitWidth);

  // The frame now scrolls internally; the document body still does not scroll X.
  const frameOverflows = await page.locator(".arc-frame").evaluate((el) => el.scrollWidth > el.clientWidth);
  expect(frameOverflows).toBeTruthy();
  const bodyScrollsX = await page.evaluate(() => document.body.scrollWidth > window.innerWidth + 1);
  expect(bodyScrollsX).toBeFalsy();
});

test('max zoom reaches chip-safe detail spacing even on a narrow frame', async ({ page }) => {
  // Regression guard (cross-family review): the fit model removed the old minCol
  // overflow, so max zoom must be derived from the chip footprint — on a 390px frame
  // it must still be able to widen the content far past the frame so ~100 columns get
  // >= the 30px worklist-chip footprint. Persist a huge zoom; render clamps it to the
  // derived max for the frame.
  await page.addInitScript(() => { try { localStorage.setItem('civ-arc-zoom', '16'); } catch (e) {} });
  await page.setViewportSize({ width: 390, height: 800 });
  await page.goto('/civilization-arc.html');
  const svg = page.locator('.arc-svg');
  await expect(svg).toBeVisible();
  const vbWidth = async () => {
    const vb = await svg.getAttribute('viewBox');
    return vb ? parseFloat(vb.split(' ')[2]) : 0;
  };
  // >=30px over ~100 distinct seqs is ~3200px of content; assert we blow well past
  // the 390px frame into chip-safe detail territory.
  await expect.poll(vbWidth, { timeout: 5000 }).toBeGreaterThan(3200);
});

test('reflows on resize: the fit viewBox tracks the frame width, page never scrolls X', async ({ page }) => {
  await page.goto('/civilization-arc.html');
  const svg = page.locator('.arc-svg');
  await expect(svg).toBeVisible();

  const viewBoxWidth = async () => {
    const vb = await svg.getAttribute('viewBox');
    return vb ? parseFloat(vb.split(' ')[2]) : 0;
  };
  const frameWidth = async () => page.locator(".arc-frame").evaluate((el) => Math.round(el.clientWidth));

  // Wide viewport -> the fit viewBox tracks the actual frame width. The frame is
  // narrower now because the article shell has a wider, resizable sidebar.
  await page.setViewportSize({ width: 1300, height: 900 });
  await expect.poll(frameWidth, { timeout: 5000 }).toBeGreaterThan(800);
  await expect.poll(viewBoxWidth, { timeout: 5000 }).toBeGreaterThan(800);
  const wide = await viewBoxWidth();
  const wideFrame = await frameWidth();
  expect(Math.abs(wide - wideFrame)).toBeLessThanOrEqual(4);

  // Narrow viewport → the fit viewBox reflows smaller to track the frame.
  await page.setViewportSize({ width: 520, height: 900 });
  await expect.poll(viewBoxWidth, { timeout: 5000 }).toBeLessThan(wide);
  const narrow = await viewBoxWidth();
  const narrowFrame = await frameWidth();

  expect(narrow).toBeLessThan(wide); // viewBox recomputed for the new container
  expect(Math.abs(narrow - narrowFrame)).toBeLessThanOrEqual(4);
  const bodyScrollsX = await page.evaluate(() => document.body.scrollWidth > window.innerWidth + 1);
  expect(bodyScrollsX).toBeFalsy();
});
