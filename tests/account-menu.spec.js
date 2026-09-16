const { test, expect } = require("@playwright/test");
const fs = require("node:fs");
const path = require("node:path");
const dist = process.env.KNOWLEDGE_HUB_BROWSER_DIST || "dist";
const source = fs.readdirSync(path.join(dist, "source")).find(name => name.endsWith(".html"));

async function signedIn(page, data = {}) {
  await page.route("**/oauth2/userinfo", route => route.fulfill({ json: {
    preferredUsername: "Pat Example", email: "pat@example.test", groups: ["wiki-contributors"], ...data
  } }));
}

for (const width of [280, 390, 1280]) {
  test(`profile menu fits, supports keyboard use and closes at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 800 });
    await signedIn(page);
    await page.goto("/index.html");
    const toggle = page.locator("#account-toggle");
    await expect(page.locator("#account-name")).toHaveText("Pat Example");
    await toggle.focus();
    await page.keyboard.press("Enter");
    await expect(page.locator(".account-panel")).toBeVisible();
    await expect(page.locator("#account-email")).toHaveText("pat@example.test");
    await expect(page.locator("#account-groups")).toHaveText("wiki-contributors");
    const box = await page.locator(".account-panel").boundingBox();
    expect(box.x).toBeGreaterThanOrEqual(0);
    expect(box.x + box.width).toBeLessThanOrEqual(width);
    await page.keyboard.press("Tab");
    await expect(page.locator("#account-settings")).toBeFocused();
    await page.keyboard.press("Escape");
    await expect(page.locator(".account-panel")).toBeHidden();
    await expect(toggle).toBeFocused();
    await toggle.click();
    await page.locator(".brand-title").click();
    await expect(page.locator(".account-panel")).toBeHidden();
  });
}

test("nested pages use the same session and logout endpoints", async ({ page }) => {
  await signedIn(page);
  for (const route of ["/devops/index.html", "/source/" + source, "/ingest.html"]) {
    await page.goto(route);
    await expect(page.locator("#account-name")).toHaveText("Pat Example");
    await page.locator("#account-toggle").click();
    await expect(page.locator("#account-logout")).toHaveAttribute("href", /^\/oauth2\/sign_out\?rd=https/);
    await expect(page.locator("#account-settings")).toHaveAttribute("href", /^https:\/\/borgdev\.transpara\.io\/tauth\/realms\/transpara\/account\/$/);
  }
});

test("logout leaves through the proxy and requests tAuth logout", async ({ page }) => {
  await signedIn(page);
  await page.route("**/api/articles", route => route.fulfill({ json: { articles: [] } }));
  await page.route("**/oauth2/sign_out?**", route => route.fulfill({ body: "Signed out" }));
  await page.goto("/ingest.html");
  await page.locator("#authoring-token").fill("example-editor-value");
  await page.locator("#account-toggle").click();
  const request = page.waitForRequest("**/oauth2/sign_out?**");
  await page.locator("#account-logout").click();
  const url = new URL((await request).url());
  expect(new URL(url.searchParams.get("rd")).pathname).toBe("/tauth/realms/transpara/protocol/openid-connect/logout");
  await expect(page.locator("body")).toHaveText("Signed out");
});

test("expired session offers sign-in and removes account actions", async ({ page }) => {
  await page.route("**/oauth2/userinfo", route => route.fulfill({ status: 401, body: "Unauthorized" }));
  await page.goto("/index.html");
  await page.locator("#account-toggle").click();
  await expect(page.locator("#account-status")).toHaveText("You are signed out.");
  await expect(page.locator("#account-login")).toBeVisible();
  await expect(page.locator("#account-logout")).toBeHidden();
});

test("static preview without an identity service hides the account integration", async ({ page }) => {
  await page.route("**/oauth2/userinfo", route => route.fulfill({ status: 404, body: "Not found" }));
  await page.goto("/index.html");
  await expect(page.locator("#account-menu")).toBeHidden();
  await expect(page.locator("#account-name")).toHaveText("Your profile");
  await expect(page.locator("#account-status")).toHaveText("Profile information is unavailable on this connection.");
  await expect(page.locator("#account-membership")).toBeHidden();
  await expect(page.locator("#account-login")).toBeHidden();
  await expect(page.locator("#account-settings")).toBeHidden();
  await expect(page.locator("#account-logout")).toBeHidden();
});

test("authoring is remembered for the account after reload and can be forgotten", async ({ page }) => {
  await signedIn(page);
  let saved = false;
  let registrations = 0;
  await page.route("**/api/articles", route => route.fulfill({ json: { articles: [] } }));
  await page.route("**/api/authoring-profile**", async route => {
    const request = route.request();
    if (request.method() === "POST") {
      expect(request.headers()["x-wiki-profile-action"]).toBe("1");
      if (request.url().endsWith("/forget")) saved = false;
      else {
        expect(request.headers()["x-civwiki-authoring-token"]).toBe("example-editor-value");
        registrations++;
        saved = true;
      }
    }
    await route.fulfill({ json: { enabled: true, signed_in: true, authoring: saved } });
  });
  await page.goto("/ingest.html");
  await expect(page.locator("#remember-authoring")).toBeVisible();
  await page.locator("#authoring-token").fill("example-editor-value");
  await page.locator("#remember-authoring").click();
  await expect(page.locator("#authoring-profile-status")).toContainText("saved to your wiki profile");
  await expect(page.locator("#authoring-token")).toHaveValue("");
  await expect(page.locator("#authoring-token-label")).toBeHidden();
  await page.reload();
  await expect(page.locator("#authoring-token-label")).toBeHidden();
  await expect(page.locator("#authoring-profile-status")).toContainText("saved to your wiki profile");
  expect(registrations).toBe(1);
  await page.route("**/api/rebuild", route => {
    expect(route.request().headers()["x-civwiki-authoring-token"]).toBeUndefined();
    expect(route.request().headers()["x-wiki-profile-action"]).toBe("1");
    return route.fulfill({ status: 500, json: { error: "Fixture response; request used account access" } });
  });
  await page.locator("#rebuild-now").click();
  await expect(page.locator("#rebuild-status")).toContainText("used account access");
  const storage = await page.evaluate(() => JSON.stringify({ local: { ...localStorage }, session: { ...sessionStorage }, cookie: document.cookie }));
  expect(storage).not.toContain("example-editor-value");
  await page.locator("#account-toggle").click();
  await expect(page.locator("#account-forget-authoring")).toBeVisible();
  await page.locator("#account-forget-authoring").click();
  await expect(page.locator("#authoring-token-label")).toBeVisible();
  await expect(page.locator("#account-forget-authoring")).toBeHidden();
  await page.reload();
  await expect(page.locator("#remember-authoring")).toBeVisible();
  expect(saved).toBe(false);
});

test("invalid authoring token is not remembered and remains available for correction", async ({ page }) => {
  await signedIn(page);
  await page.route("**/api/articles", route => route.fulfill({ json: { articles: [] } }));
  await page.route("**/api/authoring-profile", route => route.request().method() === "POST"
    ? route.fulfill({ status: 401, json: { error: "A valid authoring token is required once" } })
    : route.fulfill({ json: { enabled: true, signed_in: true, authoring: false } }));
  await page.goto("/ingest.html");
  await expect(page.locator("#remember-authoring")).toBeVisible();
  await page.locator("#authoring-token").fill("wrong-example");
  await page.locator("#remember-authoring").click();
  await expect(page.locator("#authoring-profile-status")).toContainText("valid authoring token");
  await expect(page.locator("#authoring-token")).toHaveValue("wrong-example");
  await expect(page.locator("#account-forget-authoring")).toBeHidden();
});
