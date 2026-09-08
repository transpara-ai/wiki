const { test, expect } = require("@playwright/test");

async function expectSpace(page, space, sidebar = true) {
  await expect(page.locator("html")).toHaveAttribute("data-space", space);
  await expect(page.locator(".space-switcher a.current")).toHaveAttribute("data-space", space);
  await expect(page.locator("#wiki-search-scope")).toHaveValue(space);
  if (sidebar) {
    await expect(page.locator(".sidebar .side-home a")).toHaveAttribute("href", `${space}/index.html`);
  }
  for (const name of ["Repos", "Sources", "Ingest"]) {
    const href = await page.getByRole("link", { name, exact: true }).getAttribute("href");
    expect(new URL(href, page.url()).searchParams.get("space")).toBe(space);
  }
}

for (const space of ["competition", "platform", "civilization", "devops"]) {
  test(`${space} remains selected through tool navigation, details, and reloads`, async ({ page }) => {
    const errors = [];
    page.on("pageerror", (error) => errors.push(String(error)));
    await page.route("**/api/articles", (route) => route.fulfill({ json: { articles: [] } }));
    await page.goto("/index.html");
    await page.locator(`.space-switcher a[data-space="${space}"]`).click();
    await page.getByRole("link", { name: "Repos", exact: true }).click();
    await expectSpace(page, space);
    const groups = await page.locator(".repo-index [data-context-spaces]:visible")
      .evaluateAll((rows) => rows.map((row) => row.dataset.contextSpaces.split(" ")));
    expect(groups.length).toBeGreaterThan(0);
    expect(groups.every((spaces) => spaces.includes(space))).toBe(true);
    await page.locator(".repo-index-table:visible a").first().click();
    await expectSpace(page, space);

    await page.getByRole("link", { name: "Sources", exact: true }).click();
    await expectSpace(page, space);
    const sources = page.locator(".source-index > li:visible");
    const memberships = await sources.evaluateAll((rows) => rows.map((row) => row.dataset.contextSpaces.split(" ")));
    expect(memberships.every((spaces) => spaces.includes(space))).toBe(true);
    const localSource = sources.locator('a[href^="/source/"]');
    if (await localSource.count()) {
      await localSource.first().click();
      await expectSpace(page, space, false);
    } else if (!memberships.length) {
      await expect(page.locator("#space-context-empty")).toBeVisible();
    }
    await page.getByRole("link", { name: "Ingest", exact: true }).click();
    await expectSpace(page, space);
    await expect(page.locator("#ingest-space")).toHaveValue(space);
    await expect(page.locator("#ingest-steward")).toHaveValue(space === "civilization" ? "transpara-ai" : "transpara");
    await page.reload();
    await expectSpace(page, space);
    await expect(page.locator("#ingest-space")).toHaveValue(space);

    // Legacy/bookmarked tool URLs inherit the tab's current context too.
    await page.goto("/repos.html");
    await expectSpace(page, space);
    await page.goto("/sources.html");
    await expectSpace(page, space);
    await page.goto("/ingest.html");
    await expectSpace(page, space);
    await expect(page.locator("#ingest-space")).toHaveValue(space);
    expect(errors).toEqual([]);
  });
}

test("changing ingestion space updates context without discarding pasted text", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.route("**/api/articles", (route) => route.fulfill({ json: { articles: [] } }));
  await page.goto("/ingest.html?space=competition");
  await page.locator("#pasted-text").fill("Email evidence to keep while choosing a space.");
  for (const space of ["platform", "civilization", "competition"]) {
    await page.locator("#ingest-space").selectOption(space);
    await expectSpace(page, space);
    await expect(page.locator("#pasted-text")).toHaveValue("Email evidence to keep while choosing a space.");
    await page.locator(".sidebar-toggle").click();
    await expect(page.locator(".sidebar-panel")).toHaveAttribute("open", "");
    const toggle = page.locator("#side-toggle-all");
    await toggle.click();
    await expect(toggle).toHaveText("show");
    await toggle.click();
    await expect(toggle).toHaveText("hide");
  }
  await page.getByRole("link", { name: "Sources", exact: true }).click();
  await expectSpace(page, "competition");
});

test("explicit space links override remembered context and work without storage", async ({ page }) => {
  await page.addInitScript(() => {
    Object.defineProperty(window, "sessionStorage", { get() { throw new Error("Storage disabled"); } });
  });
  await page.goto("/competition/index.html");
  for (const name of ["Repos", "Sources", "Ingest"]) {
    await page.getByRole("link", { name, exact: true }).click();
    await expectSpace(page, "competition");
  }
  await page.goto("/ingest.html?space=platform");
  await expectSpace(page, "platform");
  await expect(page.locator("#ingest-space")).toHaveValue("platform");
  await page.goto("/ingest.html?space=__proto__");
  await expectSpace(page, "civilization");
  await expect(page.locator("#ingest-space")).toHaveValue("civilization");
});

test("the search space dropdown establishes tool context and keeps ingestion in sync", async ({ page }) => {
  await page.route("**/api/articles", (route) => route.fulfill({ json: { articles: [] } }));
  await page.goto("/event-graph.html");
  await page.locator("#wiki-search-scope").selectOption("competition");
  await expectSpace(page, "competition");
  for (const name of ["Repos", "Sources", "Ingest"]) {
    await page.getByRole("link", { name, exact: true }).click();
    await expectSpace(page, "competition");
  }
  await expect(page.locator("#ingest-space")).toHaveValue("competition");
  await page.locator("#pasted-text").fill("Evidence retained when changing context.");
  await page.locator("#wiki-search-scope").selectOption("platform");
  await expectSpace(page, "platform");
  await expect(page.locator("#ingest-space")).toHaveValue("platform");
  await expect(page.locator("#pasted-text")).toHaveValue("Evidence retained when changing context.");
  await page.locator("#wiki-search-scope").selectOption("all");
  await expect(page.locator("#wiki-search-scope")).toHaveValue("all");
  await expect(page.locator("#ingest-space")).toHaveValue("platform");
  await page.getByRole("link", { name: "Repos", exact: true }).click();
  await expectSpace(page, "platform");
});
