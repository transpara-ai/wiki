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

test("static preview explains missing profile without claiming an identity", async ({ page }) => {
  await page.route("**/oauth2/userinfo", route => route.fulfill({ status: 404, body: "Not found" }));
  await page.goto("/index.html");
  await page.locator("#account-toggle").click();
  await expect(page.locator("#account-name")).toHaveText("Your profile");
  await expect(page.locator("#account-status")).toHaveText("Profile information is unavailable on this connection.");
  await expect(page.locator("#account-membership")).toBeHidden();
  await expect(page.locator("#account-login")).toBeHidden();
});
