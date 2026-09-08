const fs = require("fs");
const path = require("path");
const { test, expect } = require("@playwright/test");

// Thousands of full-document trace snapshots obscure the useful evidence here:
// each failed assertion already reports the route and measured viewport.
test.use({ trace: "off" });

const dist = path.resolve(__dirname, "..", process.env.KNOWLEDGE_HUB_BROWSER_DIST || "dist");
function htmlRoutes(dir = dist) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const file = path.join(dir, entry.name);
    return entry.isDirectory() ? htmlRoutes(file) : entry.name.endsWith(".html")
      ? ["/" + path.relative(dist, file).split(path.sep).join("/")] : [];
  });
}
const routes = htmlRoutes().sort();
const representativeRoutes = [
  "/index.html", "/civilization/index.html", "/platform/index.html", "/competition/index.html", "/devops/index.html",
  "/event-graph.html", "/platform-transpara-mcp-boundary.html", "/civilization-arc.html",
  "/competitor-cognite-data-fusion.html",
  "/civilization_arc.html", "/repos.html", "/sources.html", "/ingest.html",
  ...routes.filter((route) => route.startsWith("/repo-")).slice(0, 2),
  ...routes.filter((route) => route.startsWith("/source/")).slice(0, 2),
];

async function pageWidth(page) {
  return page.evaluate(() => ({
    viewport: document.documentElement.clientWidth,
    content: document.documentElement.scrollWidth,
  }));
}
async function expectContained(page) {
  const size = await pageWidth(page);
  expect(size.content, `${page.url()} at ${size.viewport}px`).toBeLessThanOrEqual(size.viewport + 1);
}

test("published version matches package metadata and every page family links to it", async ({ page, request }) => {
  const { version } = require("../package.json");
  const lock = require("../package-lock.json");
  expect(lock.version).toBe(version);
  expect(lock.packages[""].version).toBe(version);
  const response = await request.get("/version.json");
  expect(response.ok()).toBe(true);
  expect(await response.json()).toEqual({ version });
  const plain = await request.get("/VERSION");
  expect(plain.ok()).toBe(true);
  expect(await plain.text()).toBe(version + "\n");
  for (const route of representativeRoutes) {
    await page.goto(route);
    await expect(page.locator(".brand-version")).toBeVisible();
    await expect(page.locator(".brand-version")).toHaveText("v" + version);
    const link = page.locator(".page-foot .site-version");
    await expect(link).toHaveText("v" + version);
    expect(await link.evaluate((el) => new URL(el.href).pathname)).toBe("/version.json");
  }
});

// Exercise the real corpus: README and source pages bring their own long paths,
// tables and code, which a handful of hand-picked articles cannot cover.
for (const width of [320, 768, 1280]) {
  test(`all generated pages fit a ${width}px viewport`, async ({ page }) => {
    test.setTimeout(180000);
    await page.setViewportSize({ width, height: 900 });
    const failures = [];
    for (const route of routes) {
      const response = await page.goto(route);
      expect(response.ok(), route).toBeTruthy();
      const size = await pageWidth(page);
      if (size.content > size.viewport + 1) failures.push({ route, ...size });
    }
    expect(failures).toEqual([]);
  });
}

for (const theme of ["light", "dark"]) {
  test(`page families reflow between breakpoints in ${theme} theme`, async ({ page }) => {
    test.setTimeout(90000);
    await page.addInitScript((value) => localStorage.setItem("civwiki-theme", value), theme);
    for (const width of [280, 390, 600, 720, 721, 1024, 1025, 1100, 1101, 1440, 2560]) {
      await page.setViewportSize({ width, height: 900 });
      for (const route of representativeRoutes) {
        await page.goto(route);
        await expectContained(page);
        // Controls must not overlap even when the document itself fits.
        const boxes = await page.locator(".brand,.search,.space-switcher,.top-links,.theme-toggle").evaluateAll(
          (els) => els.map((el) => {
            const { x, y, width, height } = el.getBoundingClientRect();
            return { name: el.className, x, y, width, height };
          })
        );
        for (let i = 0; i < boxes.length; i++) {
          for (const other of boxes.slice(i + 1)) {
            const a = boxes[i];
            const overlap = Math.min(a.x + a.width, other.x + other.width) - Math.max(a.x, other.x) > 1
              && Math.min(a.y + a.height, other.y + other.height) - Math.max(a.y, other.y) > 1;
            expect(overlap, `${route} at ${width}px: ${a.name} overlaps ${other.name}`).toBe(false);
          }
        }
      }
    }
  });
}

test("compact navigation supports keyboard use and viewport changes", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/event-graph.html");
  const panel = page.locator(".sidebar-panel");
  const toggle = page.locator(".sidebar-toggle");
  await expect(panel).not.toHaveAttribute("open");
  await expect(page.locator("h1.page-title")).toBeInViewport();
  await toggle.focus();
  await page.keyboard.press("Enter");
  await expect(panel).toHaveAttribute("open");
  await expect(page.locator('.sidebar a.current[href="event-graph.html"]')).toBeVisible();
  await page.locator("#side-toggle-all").click();
  await expect(page.locator(".side-group[open]")).toHaveCount(0);
  await toggle.click();
  await expect(panel).not.toHaveAttribute("open");
  await page.setViewportSize({ width: 1440, height: 900 });
  await expect(panel).toHaveAttribute("open");
  await expect(toggle).toBeHidden();
  await page.setViewportSize({ width: 768, height: 1024 });
  await expect(panel).not.toHaveAttribute("open");
  await toggle.click();
  await page.locator('.side-home a').click();
  await expect(page).toHaveURL(/civilization\/index\.html$/);
});

test("saved wide sidebar cannot squeeze articles or the arc at laptop sizes", async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem("civwiki-sidebar-width", "560"));
  await page.setViewportSize({ width: 1100, height: 900 });
  await page.goto("/civilization-arc.html");
  expect(await page.locator("main").evaluate((el) => el.clientWidth)).toBeGreaterThan(700);
  await expectContained(page);
  expect(await page.locator(".infobox").evaluate((el) => getComputedStyle(el).float)).toBe("none");
  expect(await page.locator(".arc-now-columns").evaluate((el) => getComputedStyle(el).gridTemplateColumns.split(" ").length)).toBe(1);
  const grip = page.locator(".sidebar-resizer");
  await grip.focus();
  await page.keyboard.press("End");
  expect(await page.locator(".sidebar").evaluate((el) => el.getBoundingClientRect().width)).toBeLessThanOrEqual(385);
  await page.setViewportSize({ width: 1025, height: 900 });
  await expectContained(page);
});

test("wide tables and code scroll locally with keyboard access", async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 740 });
  await page.goto("/repos.html");
  const table = page.locator(".table-scroll").first();
  expect(await table.evaluate((el) => el.scrollWidth > el.clientWidth)).toBe(true);
  await expect(table.locator("table thead th")).toHaveCount(4);
  await table.focus();
  await page.keyboard.press("ArrowRight");
  await expect.poll(() => table.evaluate((el) => el.scrollLeft)).toBeGreaterThan(0);
  await expectContained(page);

  await page.goto("/event-graph.html");
  await page.locator("article.body").evaluate((el) => {
    const pre = document.createElement("pre");
    pre.tabIndex = 0;
    pre.textContent = "long_code_identifier ".repeat(80);
    el.prepend(pre);
    const p = document.createElement("p");
    p.textContent = "https://example.test/" + "longpath".repeat(80);
    el.prepend(p);
    const img = document.createElement("img");
    img.src = "data:image/svg+xml," + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="600"></svg>');
    img.width = 1800;
    img.height = 600;
    el.prepend(img);
  });
  const pre = page.locator("article.body pre").first();
  await pre.focus();
  await page.keyboard.press("ArrowRight");
  await expect.poll(() => pre.evaluate((el) => el.scrollLeft)).toBeGreaterThan(0);
  await expectContained(page);
});

test("search stays in a short viewport and keeps the keyboard selection visible", async ({ page }) => {
  await page.setViewportSize({ width: 568, height: 320 });
  await page.goto("/index.html");
  await page.locator("#wiki-search").fill("graph");
  const results = page.locator("#search-results");
  await expect(results).toBeVisible();
  const box = await results.boundingBox();
  expect(box.y + box.height).toBeLessThanOrEqual(320);
  for (let n = 0; n < 7; n++) await page.keyboard.press("ArrowDown");
  const active = results.locator('[aria-selected="true"]');
  const selected = await active.boundingBox();
  expect(selected.y + selected.height).toBeLessThanOrEqual(box.y + box.height + 1);
  await expectContained(page);
  await page.keyboard.press("Escape");
  await expect(results).toBeHidden();
});

test.describe("touch devices", () => {
  test.use({ hasTouch: true, isMobile: true, viewport: { width: 320, height: 740 } });
  test("ingest modes, fields and status remain usable", async ({ page }) => {
    await page.goto("/ingest.html");
    await expect(page.locator("#new-investigation-name-row")).toBeHidden();
    await page.locator("#new-investigation").check();
    await expect(page.locator("#new-investigation-name-row")).toBeVisible();
    await page.locator("#new-investigation").uncheck();
    await expect(page.locator("#new-investigation-name-row")).toBeHidden();
    for (const mode of ["add", "replace", "remove"]) {
      await page.locator(`input[name="ingest-mode"][value="${mode}"]`).check();
      const panel = page.locator(`[data-mode-panel="${mode}"]`);
      await expect(panel).toBeVisible();
      const fields = await panel.locator('input:not([type="checkbox"]), select, textarea').evaluateAll((els) =>
        els.filter((el) => el.getBoundingClientRect().width).map((el) => ({
          width: el.getBoundingClientRect().width,
          font: parseFloat(getComputedStyle(el).fontSize),
        })));
      for (const field of fields) {
        expect(field.width).toBeGreaterThan(220);
        expect(field.font).toBeGreaterThanOrEqual(16);
      }
      await expectContained(page);
    }
    await expect(page.locator("#rm-submit")).toBeDisabled();
    for (const control of [".theme-toggle", '.top-links a[href*="sources.html"]', '.space-switcher a.current']) {
      expect((await page.locator(control).boundingBox()).height).toBeGreaterThanOrEqual(44);
    }
    await page.setViewportSize({ width: 844, height: 390 });
    await expectContained(page);
  });
});

test("compact navigation still works without JavaScript", async ({ browser }) => {
  const context = await browser.newContext({ javaScriptEnabled: false, viewport: { width: 390, height: 844 } });
  const page = await context.newPage();
  await page.goto(test.info().project.use.baseURL + "/event-graph.html");
  await expect(page.locator(".sidebar-panel")).toHaveAttribute("open");
  await page.locator(".sidebar-toggle").click();
  await expect(page.locator(".sidebar-panel")).not.toHaveAttribute("open");
  await expect(page.locator("h1.page-title")).toBeInViewport();
  await context.close();
});
