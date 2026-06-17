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
