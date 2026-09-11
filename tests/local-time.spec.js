const { test, expect } = require("@playwright/test");

const WINTER = "2026-01-15T23:45:00Z";
const SUMMER = "2026-07-15T23:45:00Z";

async function stampPages(page, timestamp) {
  await page.route(/\.html(?:\?.*)?$/, async (route) => {
    const response = await route.fetch();
    let body = await response.text();
    // Use the real generated markup and context data, with a fixed instant so
    // expected dates/offsets do not depend on the machine running the build.
    const match = body.match(/<time datetime="([^"]+)" data-local-time>/);
    if (match) body = body.split(match[1]).join(timestamp());
    await route.fulfill({ response, body });
  });
  await page.route("**/api/articles", (route) => route.fulfill({ json: { articles: [] } }));
}

for (const scenario of [
  { zone: "America/Chicago", winter: "Jan 15, 2026, 5:45 PM CST", summer: "Jul 15, 2026, 6:45 PM CDT" },
  { zone: "Asia/Kathmandu", winter: "Jan 16, 2026, 5:30 AM GMT+5:45", summer: "Jul 16, 2026, 5:30 AM GMT+5:45" },
  { zone: "Pacific/Auckland", winter: "Jan 16, 2026, 12:45 PM GMT+13", summer: "Jul 16, 2026, 11:45 AM GMT+12" },
]) {
  test.describe(scenario.zone, () => {
    test.use({ timezoneId: scenario.zone, locale: "en-US" });

    test("freshness follows the reader across pages and space changes", async ({ page }) => {
      const errors = [];
      page.on("pageerror", (error) => errors.push(String(error)));
      let stamp = WINTER;
      await stampPages(page, () => stamp);
      for (const [instant, expected] of [[WINTER, scenario.winter], [SUMMER, scenario.summer]]) {
        stamp = instant;
        for (const route of ["/index.html", "/devops/index.html", "/ingest.html?space=competition"]) {
          await page.goto(route);
          const time = page.locator(".space-freshness time");
          await expect(time).toHaveText(expected);
          await expect(time).toHaveAttribute("datetime", instant);
          // Intl may return the older IANA alias Asia/Katmandu.
          const zoneName = scenario.zone === "Asia/Kathmandu" ? "Asia/Kat[h]?mandu" : scenario.zone;
          await expect(time).toHaveAttribute("title", new RegExp(zoneName));
        }
        await page.locator("#ingest-space").selectOption("platform");
        await expect(page.locator(".space-freshness")).toContainText("Transpara Platform");
        await expect(page.locator(".space-freshness time")).toHaveText(expected);
      }
      const unchanged = await page.evaluate(() => ["2026-01-15", "unknown", "2026-01-15 23:45", "not a date"]
        .map((value) => window.KnowledgeTime.format(value)));
      expect(unchanged).toEqual(["2026-01-15", "unknown", "2026-01-15 23:45", "not a date"]);
      expect(errors).toEqual([]);
    });
  });
}

test.describe("Chicago daylight saving and asynchronous status", () => {
  test.use({ timezoneId: "America/Chicago", locale: "en-US" });

  test("spring transition skips the nonexistent hour and fall hours retain their offsets", async ({ page }) => {
    let stamp = "2026-03-08T07:30:00Z";
    await stampPages(page, () => stamp);
    for (const [instant, expected] of [
      ["2026-03-08T07:30:00Z", "Mar 8, 2026, 1:30 AM CST"],
      ["2026-03-08T08:30:00Z", "Mar 8, 2026, 3:30 AM CDT"],
      ["2026-11-01T06:30:00Z", "Nov 1, 2026, 1:30 AM CDT"],
      ["2026-11-01T07:30:00Z", "Nov 1, 2026, 1:30 AM CST"],
    ]) {
      stamp = instant;
      await page.goto("/index.html");
      await expect(page.locator(".space-freshness time")).toHaveText(expected);
    }
  });

  test("deployment and activity timestamps use local time after their data loads", async ({ page }) => {
    await page.route("**/deploy-status.json", (route) => route.fulfill({ json: {
      deployed_sha: "abcdef123456", checked: SUMMER, blocked: true, since: WINTER, reason: "Test pause",
    } }));
    await page.route("**/inflight.json", (route) => route.fulfill({ json: {
      generated: SUMMER, window_days: 30, repos: [], errors: [], items: [],
    } }));
    await page.goto("/civilization-arc.html");
    await expect(page.locator("#deploy-foot")).toContainText("Jul 15, 2026, 6:45 PM CDT");
    await expect(page.locator("#deploy-banner")).toContainText("Jan 15, 2026, 5:45 PM CST");
    await expect(page.locator(".arc-live-chip")).toContainText("Jul 15, 2026, 6:45 PM CDT");
    await expect(page.locator(".arc-progress-metrics").first()).toContainText("Jun 20, 2026, 7:00 PM CDT");
    await expect(page.locator(".arc-live-reader-correction .arc-progress-metrics"))
      .toContainText("Jun 22, 2026, 10:10 AM CDT");
  });
});
