const { test, expect } = require("@playwright/test");

test("INC-001 operational wiki pages render locally", async ({ page }) => {
  const pages = [
    ["index.html", "Civilization Wiki"],
    ["the-observatory.html", "The Observatory"],
    ["civilization-wiki.html", "The Civilization Wiki"],
    ["gate-k.html", "Gate K"],
    ["gate-l.html", "Gate L"],
    ["deployment-arc.html", "The Deployment Arc"],
    ["hive-governance.html", "Hive / Governance Layer"],
    ["roles-catalog.html", "The Roles Catalog"],
    ["civic-roles.html", "Hive Civic Roles"],
    ["work.html", "Work (Production DAG and Task Lifecycle)"],
    ["site.html", "Site (Operator Console)"],
  ];

  for (const [route, heading] of pages) {
    await page.goto(`/${route}`);
    await expect(page.locator("h1.page-title")).toHaveText(heading);
    await expect(page.locator("article.body")).toBeVisible();
    await expect(page.locator("footer.page-foot")).toContainText("Generated from");
  }
});

test("INC-001 arc routes render local browser visualization", async ({ page }) => {
  for (const route of ["/civilization-arc.html", "/civilization_arc.html"]) {
    await page.goto(route);
    await expect(page.locator(".civilization-arc-nav")).toBeVisible();
    await expect(page.locator("svg.arc-svg")).toBeVisible();
    // Presentation smoke: expected arc scaffolding for the current static view.
    await expect(page.locator(".arc-track-band")).toHaveCount(3);
    await expect(page.locator(".arc-now-line")).toHaveCount(1);
  }
});
