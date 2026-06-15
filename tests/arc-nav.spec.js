const { test, expect } = require("@playwright/test");

async function selectedPhaseWidthRatio(page) {
  return page.evaluate(() => {
    const svg = document.querySelector("svg.arc-svg");
    const selected = document.querySelector(".arc-phase-group.arc-is-selected rect.arc-phase");
    if (!svg || !selected) return 0;
    return selected.getBoundingClientRect().width / svg.getBoundingClientRect().width;
  });
}

test("homepage arc renders, expands, and exposes named swimlanes", async ({ page }) => {
  await page.goto("/index.html");

  const nav = page.locator(".civilization-arc-nav");
  await expect(nav).toBeVisible();
  await expect(nav).toHaveAttribute("data-expanded", "false");
  await expect(page.locator("h1.page-title")).toHaveText("Civilization Wiki");

  const navTop = await nav.evaluate((el) => el.getBoundingClientRect().top);
  const titleTop = await page.locator("h1.page-title").evaluate((el) => el.getBoundingClientRect().top);
  expect(navTop).toBeLessThan(titleTop);

  await expect(page.locator(".arc-phase-group")).toHaveCount(15);
  await expect(page.locator(".arc-compact-rail-item")).toHaveCount(16);
  await page.locator("svg.arc-svg").dispatchEvent("wheel", { deltaY: -260, clientX: 520, clientY: 90 });
  await expect(page.locator("[data-arc-zoom-readout]")).toContainText("zoom 1.00x");
  await page.locator('[aria-label="Memory / Context Advisory Layer"]').click();
  await expect(nav).toHaveAttribute("data-has-selection", "true");
  await expect(nav).toHaveAttribute("data-details-open", "true");
  await expect(nav.locator(".arc-selected")).toBeVisible();
  await expect(nav.locator(".arc-selected")).toContainText("Memory / Context Advisory Layer");
  await expect(nav.locator(".arc-selected")).toContainText("Inside phase");
  await expect(nav.locator(".arc-selected")).toContainText("MEM");
  await nav.getByRole("button", { name: "Close details" }).click();
  await expect(nav).toHaveAttribute("data-has-selection", "false");
  await expect(nav).toHaveAttribute("data-details-open", "false");
  await expect(nav.locator(".arc-selected")).toBeHidden();
  await page.getByRole("button", { name: "Expand Arc" }).click();
  await expect(nav).toHaveAttribute("data-expanded", "true");
  await expect(page.locator(".arc-swimlane-label", { hasText: "Phase" })).toBeVisible();
  await expect(page.locator(".arc-swimlane-label", { hasText: "Epic" })).toBeVisible();
  await expect(page.locator(".arc-swimlane-label", { hasText: "Stage" })).toBeVisible();
  await expect(page.locator(".arc-swimlane-label", { hasText: "Close" })).toBeVisible();
  await expect(page.locator(".arc-legend")).toBeVisible();
  await expect(page.locator(".arc-risk-group")).toHaveCount(4);
});

test("full arc page opens as a complete standalone view", async ({ page, context }) => {
  await page.goto("/index.html");

  const popupPromise = context.waitForEvent("page");
  await page.getByRole("link", { name: "Open Full" }).click();
  const full = await popupPromise;
  await full.waitForLoadState("domcontentloaded");

  await expect(full).toHaveURL(/civilization-arc\.html$/);
  const nav = full.locator(".civilization-arc-nav");
  await expect(nav).toBeVisible();
  await expect(nav).toHaveAttribute("data-standalone", "true");
  await expect(nav).toHaveAttribute("data-expanded", "true");
  await expect(full.locator(".arc-standalone-shell")).toBeVisible();
  await expect(full.getByRole("link", { name: "Back to Wiki" })).toBeVisible();
  await expect(full.getByRole("button", { name: "Fit full arc" })).toBeVisible();
  await expect(full.getByRole("button", { name: "Zoom in" })).toBeVisible();
  await expect(full.getByRole("button", { name: "Zoom out" })).toBeVisible();
  await expect(full.getByRole("button", { name: "Export SVG" })).toBeVisible();
  await expect(full.getByRole("combobox", { name: "Zoom to phase" })).toBeVisible();
  await expect(full.getByRole("checkbox", { name: "dependencies" })).toBeChecked();
  await expect(full.getByRole("checkbox", { name: "dense labels" })).toBeChecked();
  await expect(full.getByText("Click an item for drill-down details")).toBeVisible();
  await expect(full.getByRole("heading", { name: "Civilization execution worklist" })).toBeVisible();
  await expect(full.locator(".arc-plan-updated")).toHaveText(/^Updated \d{4}-\d{2}-\d{2}$/);
  await expect(full.getByRole("heading", { name: "Near-term execution" })).toBeVisible();
  await expect(full.getByRole("heading", { name: "Complete route to final end goal" })).toBeVisible();
  await expect(full.locator(".arc-plan-table").first().locator("tbody tr")).toHaveCount(6);
  await expect(full.locator(".arc-plan-table").nth(1).locator("tbody tr")).toHaveCount(10);
  await expect(full.getByText("Resolve Event-1 / Gate-E authority")).toBeVisible();
  await expect(full.getByText("Operate the dark factory on software and non-software tasks")).toBeVisible();

  const box = await full.locator("svg.arc-svg").boundingBox();
  expect(box.height).toBeGreaterThan(420);
  expect(box.width).toBeGreaterThan(900);

  const mainWidth = await full.locator(".arc-main").evaluate((el) => el.getBoundingClientRect().width);
  const viewportWidth = await full.evaluate(() => window.innerWidth);
  expect(mainWidth).toBeGreaterThan(viewportWidth - 50);

  await full.locator('[aria-label="Governance / Decision Structures"]').click();
  await expect(full.locator(".arc-selected")).toContainText("Governance / Decision Structures");
  await expect(full.locator(".arc-selected")).toContainText("Span");
  await expect(full.locator(".arc-phase-group.arc-is-selected")).toHaveCount(1);

  await expect.poll(() => selectedPhaseWidthRatio(full)).toBeGreaterThan(0.55);
  await full.getByRole("button", { name: "Close details" }).click();
  await expect(nav).toHaveAttribute("data-details-open", "false");
  await expect(nav).toHaveAttribute("data-has-selection", "false");
  await expect(full.locator(".arc-selected")).toBeHidden();
  await expect(full.locator(".arc-phase-group.arc-is-selected")).toHaveCount(0);

  const svg = full.locator("svg.arc-svg");
  await full.getByRole("button", { name: "Fit full arc" }).click();
  await expect(full.locator("[data-arc-zoom-readout]")).toContainText("zoom 1.00x");
  await svg.dispatchEvent("wheel", { deltaY: -260, clientX: 900, clientY: 220 });
  await expect(full.locator("[data-arc-zoom-readout]")).not.toContainText("zoom 1.00x");

  await full.keyboard.down("Control");
  await full.keyboard.press("0");
  await full.keyboard.up("Control");
  await expect(full.locator("[data-arc-zoom-readout]")).toContainText("zoom 1.00x");
  await full.keyboard.down("Control");
  await full.keyboard.press("=");
  await full.keyboard.up("Control");
  await expect(full.locator("[data-arc-zoom-readout]")).not.toContainText("zoom 1.00x");

  await full.keyboard.down("Control");
  await full.keyboard.press("-");
  await full.keyboard.up("Control");
  await expect(full.locator("[data-arc-zoom-readout]")).toContainText("zoom");

  await full.keyboard.down("Control");
  await full.keyboard.press("0");
  await full.keyboard.up("Control");
  await expect(full.locator("[data-arc-zoom-readout]")).toContainText("zoom 1.00x");

  await full.getByRole("combobox", { name: "Zoom to phase" }).selectOption("memory-context");
  await expect(nav).toHaveAttribute("data-details-open", "true");
  await expect(full.locator(".arc-selected")).toContainText("Memory / Context Advisory Layer");
  await expect(full.locator(".arc-selected")).toContainText("MEM");
  await expect.poll(() => selectedPhaseWidthRatio(full)).toBeGreaterThan(0.55);
  await full.keyboard.press("Escape");
  await expect(nav).toHaveAttribute("data-details-open", "false");
  await expect(full.locator(".arc-selected")).toBeHidden();

  const dependencyCount = await full.locator(".arc-dependency").count();
  expect(dependencyCount).toBeGreaterThan(0);
  await full.getByRole("checkbox", { name: "dependencies" }).uncheck();
  await expect(full.locator(".arc-dependency")).toHaveCount(0);

  const denseLabelCount = await full.locator(".arc-marker-label").count();
  expect(denseLabelCount).toBeGreaterThan(0);
  await full.getByRole("checkbox", { name: "dense labels" }).uncheck();
  const sparseLabelCount = await full.locator(".arc-marker-label").count();
  expect(sparseLabelCount).toBeLessThan(denseLabelCount);

  const downloadPromise = full.waitForEvent("download");
  await full.getByRole("button", { name: "Export SVG" }).click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toBe("civilization-arc.svg");
});

test("underscore standalone arc route remains available", async ({ page }) => {
  await page.goto("/civilization_arc.html");

  const nav = page.locator(".civilization-arc-nav");
  await expect(nav).toBeVisible();
  await expect(nav).toHaveAttribute("data-standalone", "true");
  await expect(nav).toHaveAttribute("data-expanded", "true");
  await expect(page.getByText("Click an item for drill-down details")).toBeVisible();
});

test("arc remains inside the mobile viewport", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/index.html");

  const nav = page.locator(".civilization-arc-nav");
  await expect(nav).toBeVisible();
  const overflow = await nav.evaluate((el) => el.scrollWidth - el.clientWidth);
  expect(overflow).toBeLessThanOrEqual(1);

  await page.getByRole("button", { name: "Expand Arc" }).click();
  const expandedOverflow = await nav.evaluate((el) => el.scrollWidth - el.clientWidth);
  expect(expandedOverflow).toBeLessThanOrEqual(1);
});
