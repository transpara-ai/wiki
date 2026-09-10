const { test, expect } = require("@playwright/test");

test("INC-001 operational wiki pages render locally", async ({ page }) => {
  await page.goto("/index.html");
  await expect(page.locator(".hub-hero h1")).toHaveText("Transpara Knowledge Hub");
  await expect(page.locator("article.body")).toBeVisible();
  await expect(page.locator("footer.page-foot")).toContainText("source systems retain authority");

  const pages = [
    ["the-observatory.html", "The Observatory"],
    ["civilization-wiki.html", "Transpara Knowledge Hub"],
    ["gate-k.html", "Gate K"],
    ["gate-l.html", "Gate L"],
    ["deployment-arc.html", "The Deployment Arc"],
    ["civilization-institutional-substrate.html", "Civilization Institutional Substrate"],
    ["stage-0-institutional-substrate.html", "Stage 0 Institutional Substrate"],
    ["dark-factory-lineage.html", "Dark Factory Lineage"],
    ["platform-transpara-mcp-boundary.html", "Platform and Transpara-MCP Boundary"],
    ["openbrain-wiki-knowledge-pipeline.html", "OpenBrain and Wiki Knowledge Pipeline"],
    ["external-research-placement.html", "External Research Placement"],
    ["sakana-ai-evaluation.html", "Sakana AI Capability Evaluation"],
    ["sakana-ai-adjacent-landscape.html", "Sakana AI Adjacent Technologies and Organisations"],
    ["hermes-agent.html", "Hermes Agent"],
    ["sources.html", "Source Index"],
    ["ingest.html", "Wiki Source Ingest"],
    ["repos.html", "Repositories"],
    ["repo-hive.html", "hive repository"],
    ["repo-transpara-mcp.html", "transpara-mcp repository"],
    ["hive-governance.html", "Hive / Governance Layer"],
    ["roles-catalog.html", "The Roles Catalog"],
    ["civic-roles.html", "Hive Civic Roles"],
    ["work.html", "Work (Production DAG and Task Lifecycle)"],
    ["site.html", "Site (Operator Console)"],
  ];

  for (const [route, heading] of pages) {
    const response = await page.goto(`/${route}`);
    expect(response && response.ok(), `${route} should resolve`).toBeTruthy();
    await expect(page.locator("h1.page-title")).toHaveText(heading);
    await expect(page.locator("article.body")).toBeVisible();
    if (await page.locator('[data-checkout-state="unavailable"]').count()) {
      await expect(page.locator("footer.page-foot")).toContainText("Published repository reference retained");
      await expect(page.locator("article.body a").first())
        .toHaveAttribute("href", /^https:\/\/github\.com\/transpara-ai\//);
    } else {
      await expect(page.locator("footer.page-foot")).toContainText("Generated from");
    }
  }
});

test("INC-001 arc routes render local browser visualization", async ({ page }) => {
  for (const route of ["/civilization-arc.html", "/civilization_arc.html"]) {
    await page.goto(route);
    await expect(page.locator(".civilization-arc-view")).toBeVisible();
    // Presentation smoke: the "where are we" view scaffolding.
    await expect(page.locator(".arc-now-panel")).toBeVisible();
    await expect(page.locator("[data-arc-phase]")).toHaveCount(15);
    await expect(page.locator(".arc-view-legend")).toBeVisible();
    // The retired chronological-tracks engine stays retired.
    await expect(page.locator("svg.arc-svg")).toHaveCount(0);
    await expect(page.locator(".arc-toolbar")).toHaveCount(0);
  }
});
