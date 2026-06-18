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

test("narrow viewport: chart scrolls inside frame, not the page", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 800 });
  await page.goto("/index.html");

  const nav = page.locator(".civilization-arc-nav");
  await expect(nav).toBeVisible();
  await expect(page.locator("svg.arc-svg")).toBeVisible();

  // The .arc-frame must overflow internally (svg wider than frame).
  const frameOverflows = await page.locator(".arc-frame").evaluate(function (el) {
    return el.scrollWidth > el.clientWidth;
  });
  expect(frameOverflows).toBeTruthy();

  // The document body must NOT scroll horizontally.
  const bodyScrollsX = await page.evaluate(function () {
    return document.body.scrollWidth > window.innerWidth + 1;
  });
  expect(bodyScrollsX).toBeFalsy();

  // The SVG must be rendered at content width (well above the 390px viewport).
  const svgWidth = await page.locator("svg.arc-svg").evaluate(function (el) {
    return el.getBoundingClientRect().width;
  });
  expect(svgWidth).toBeGreaterThan(390);
});

test('reflows on resize without horizontal page scroll', async ({ page }) => {
  await page.route('**/inflight.json', route => route.fulfill({ status: 404, body: '' }));
  await page.goto('/civilization-arc.html');
  const svg = page.locator('.arc-svg');
  await expect(svg).toBeVisible();

  const viewBoxWidth = async () => {
    const vb = await svg.getAttribute('viewBox');
    return vb ? parseFloat(vb.split(' ')[2]) : 0;
  };

  // The live in-flight overlay can add many derived PR markers, so the content
  // floor is data-dependent. Measure it at a narrow viewport instead of
  // hardcoding the baked 109-item value.
  await page.setViewportSize({ width: 390, height: 900 });
  await expect.poll(viewBoxWidth, { timeout: 5000 }).toBeGreaterThan(390);
  const minContent = await viewBoxWidth();

  // Wide viewport (> current minContent): poll until the reflow produces the
  // frame-driven viewBox. Condition-based wait, not a fixed delay — the resize
  // -> ResizeObserver -> requestAnimationFrame chain lands when it lands.
  await page.setViewportSize({ width: Math.ceil(minContent + 800), height: 900 });
  await expect.poll(viewBoxWidth, { timeout: 5000 }).toBeGreaterThan(minContent);
  const wide = await svg.getAttribute('viewBox');
  const wideWidth = await viewBoxWidth();

  // Narrow viewport (< minContent): poll until the reflow shrinks the viewBox below the wide
  // width (it clamps back to the minContent floor). Proves the resize recomputed the viewBox,
  // and waiting for "shrank below wide" ignores any stale wide-era value.
  await page.setViewportSize({ width: Math.max(390, Math.floor(minContent - 800)), height: 900 });
  await expect.poll(viewBoxWidth, { timeout: 5000 }).toBeLessThan(wideWidth);
  const narrow = await svg.getAttribute('viewBox');

  expect(narrow).not.toBe(wide); // viewBox width recomputed for the new container
  // the chart frame scrolls horizontally, never the document body
  const bodyScrollsX = await page.evaluate(() => document.body.scrollWidth > window.innerWidth + 1);
  expect(bodyScrollsX).toBeFalsy();
});
