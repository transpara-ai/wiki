const { test, expect } = require("@playwright/test");

test("Cognite article incorporates pricing with its model scope and primary citation", async ({ page }) => {
  await page.goto("/competitor-cognite-data-fusion.html");
  const body = page.locator("article.body");
  await expect(body.getByRole("heading", { name: "Pricing and implementation costs", exact: true })).toBeVisible();
  const subscription = body.locator("table").filter({ hasText: "Year 1 — Quick Start" });
  await expect(subscription).toContainText("$175,000");
  await expect(subscription).toContainText("$1,200,000");
  await expect(subscription).toContainText("$2,000,000");
  await expect(subscription).toContainText("$3,375,000");
  await expect(subscription).toContainText("$3,712,500");
  await expect(body).toContainText("modeled costs for a composite organization");
  await expect(body).toContainText("$3,861,529");
  await expect(body).toContainText("$7,574,029");
  await expect(body).not.toContainText("This page does not assert price");
  await expect(body.getByRole("link", { name: "Subscription calculation, page 12", exact: true }))
    .toHaveAttribute("href", /8b9d78a6042b9871c63fccf21e5961d847c2e705\.pdf#page=12$/);
  await expect(page.locator('.toc a[href="#pricing-and-implementation-costs"]')).toBeVisible();
});

test("Cognite keeps its original web references visible alongside ingested evidence", async ({ page }) => {
  const originals = [
    "https://www.cognite.com/en/industrial-data-operations",
    "https://docs.cognite.com/cdf",
    "https://docs.cognite.com/",
  ];
  await page.goto("/competitor-cognite-data-fusion.html");
  const panel = page.locator("#article-sources");
  await expect(panel).toHaveAttribute("open", "");
  for (const href of originals) {
    const link = panel.locator(`a[href="${href}"]`);
    await expect(link).toHaveCount(1);
    await expect(link).toBeVisible();
  }
  const sourceCount = await panel.locator("li").count();
  await expect(panel.locator("summary")).toHaveText(`Article sources (${sourceCount})`);
  await expect(page.locator('.infobox a[href="#article-sources"]'))
    .toHaveText(`${sourceCount} total — view all`);
  const uploads = await page.locator(".infobox .raw-doc-links a").evaluateAll((links) =>
    links.map((link) => link.getAttribute("href")));
  for (const href of uploads) {
    await expect(panel.locator(`a[href="${href}"]`)).toBeVisible();
  }
  if (uploads.length) await expect(page.locator(".infobox")).toContainText("Ingested documents");

  await page.getByRole("link", { name: "Sources", exact: true }).click();
  await expect(page.locator("#wiki-search-scope")).toHaveValue("competition");
  for (const href of originals.concat(uploads)) {
    const link = page.locator(`.source-index a[href="${href}"]`);
    await expect(link).toHaveCount(1);
    await expect(link).toBeVisible();
  }
});
