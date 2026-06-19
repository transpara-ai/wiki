const { test, expect } = require("@playwright/test");

test("homepage arc renders with tracks structure", async ({ page }) => {
  await page.goto("/index.html");

  const nav = page.locator(".civilization-arc-nav");
  await expect(nav).toBeVisible();
  await expect(page.locator("h1.page-title")).toHaveText("Civilization Wiki");

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

test("marker click populates the detail panel", async ({ page }) => {
  await page.goto("/index.html");

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
  await page.goto("/index.html");

  const nav = page.locator(".civilization-arc-nav");
  await expect(nav).toBeVisible();
  const overflow = await nav.evaluate((el) => el.scrollWidth - el.clientWidth);
  expect(overflow).toBeLessThanOrEqual(1);
});

test("narrow viewport: the arc fits the frame at default zoom (no internal or page scroll)", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 800 });
  await page.goto("/index.html");

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

  // Wide viewport → wide fit viewBox (the arc fills the frame).
  await page.setViewportSize({ width: 1300, height: 900 });
  await expect.poll(viewBoxWidth, { timeout: 5000 }).toBeGreaterThan(1000);
  const wide = await viewBoxWidth();

  // Narrow viewport → the fit viewBox reflows smaller to track the frame.
  await page.setViewportSize({ width: 520, height: 900 });
  await expect.poll(viewBoxWidth, { timeout: 5000 }).toBeLessThan(wide);
  const narrow = await viewBoxWidth();

  expect(narrow).toBeLessThan(wide); // viewBox recomputed for the new container
  const bodyScrollsX = await page.evaluate(() => document.body.scrollWidth > window.innerWidth + 1);
  expect(bodyScrollsX).toBeFalsy();
});
