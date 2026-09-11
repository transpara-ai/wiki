// tests/ingest-ux.spec.js
// Browser E2E for the ingest operation selector + destructive-mode scaffold
// (fe-ux packet AC1/AC8): three modes render, destructive panels stay hidden
// until selected, submits are disabled at birth, both themes, zero console
// errors, plus Add/rebuild feedback across browser reloads. Destructive preview
// gate behavior lives in the dom-smoke test where fetch is stubbable.
const { test: base, expect } = require("@playwright/test");
const http = require("node:http");

const test = base.extend({
  ingestReceiver: async ({}, use) => {
    const requests = [];
    // Read the actual HTTP body. WebKit's intercepted request metadata omits
    // file bytes, so postDataBuffer() cannot verify a multipart upload there.
    const server = http.createServer(async (request, response) => {
      try {
        const chunks = [];
        for await (const chunk of request) chunks.push(chunk);
        const form = await new Request("http://localhost/api/ingest", {
          method: "POST", headers: request.headers, body: Buffer.concat(chunks),
        }).formData();
        const documents = await Promise.all(form.getAll("documents")
          .filter((file) => file.size).map(async (file) => ({
            name: file.name, type: file.type, text: await file.text(),
          })));
        requests.push({ documents, space: form.get("space"), section: form.get("section"),
          steward: form.get("steward"), urls: form.get("external_urls") });
        // A refusal keeps the form available for inspection and retry.
        response.writeHead(422, { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" });
        response.end(JSON.stringify({ error: "Test refusal; source kept for retry" }));
      } catch (error) {
        response.writeHead(500);
        response.end(String(error));
      }
    });
    await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
    try {
      await use({ requests, url: `http://127.0.0.1:${server.address().port}/api/ingest` });
    } finally {
      server.closeAllConnections();
      await new Promise((resolve) => server.close(resolve));
    }
  },
});

// The static test server has no authoring API: /api/articles 404s and the UI
// degrades honestly, same class as inflight/deploy-status (see arc-view.spec).
const BENIGN_404 = /\/(api\/articles|inflight\.json|deploy-status\.json|favicon\.ico)$/;

const ARTICLES = [
  { slug: "competition-competitor-index", org: "transpara", sources: [],
    primary_placement: "competition/competitors", placements: ["competition/competitors"] },
  { slug: "competition-rtoi-comparison", org: "transpara", sources: [],
    primary_placement: "competition/comparisons",
    placements: ["competition/comparisons", "platform/product-overview"] },
  { slug: "platform-transpara-mcp-boundary", org: "transpara", sources: [],
    primary_placement: "platform/development-apis",
    placements: ["platform/development-apis", "civilization/architecture"] },
];

async function stubArticles(page) {
  await page.route("**/api/articles", (route) => route.fulfill({ json: { articles: ARTICLES } }));
}

for (const viewport of [{ width: 1280, height: 800 }, { width: 390, height: 844 }]) {
  test(`rebuild feedback stays beside the button through reload at ${viewport.width}px`, async ({ page }) => {
    await page.setViewportSize(viewport);
    await stubArticles(page);
    let pending;
    const requests = [];
    await page.route("**/api/rebuild", (route) => {
      requests.push(route.request());
      pending = route;
    });
    await page.goto("/ingest.html?space=competition");
    await page.locator("#authoring-token").fill("test-authoring-token");
    // Required ingest fields are deliberately empty: rebuild is independent.
    const button = page.locator("#rebuild-now");
    const feedback = page.locator("#rebuild-status");
    await button.click();
    await expect(button).toBeDisabled();
    await expect(button).toHaveText("Rebuilding…");
    await expect(feedback).toContainText("Keep this page open");
    await expect(feedback).toBeInViewport();
    await expect(page.getByRole("button", { name: "Ingest and rebuild", exact: true })).toBeDisabled();
    await button.evaluate((element) => { element.click(); element.click(); });
    await expect.poll(() => requests.length).toBe(1);
    expect(requests[0].method()).toBe("POST");
    expect(requests[0].headers()["x-civwiki-authoring-token"]).toBe("test-authoring-token");
    await Promise.all([
      page.waitForEvent("load"),
      pending.fulfill({ json: { refresh: { ok: true } } }),
    ]);
    await expect(feedback).toHaveText("Rebuild completed.");
    await expect(feedback).toBeInViewport();
    await expect(page.locator("#ingest-status")).toContainText("Rebuild completed.");
    await expect(button).toBeEnabled();
    await expect(button).toHaveText("Refresh status and rebuild");
    await expect(page.locator("#authoring-token")).toHaveValue("");
    expect(requests).toHaveLength(1);
  });
}

for (const response of [
  { status: 403, json: { error: "Authoring token required" }, message: "Authoring token required" },
  { status: 500, json: { refresh: { ok: false, error: "Refresh timed out" } }, message: "Refresh timed out" },
  { networkFailure: true, message: "Rebuild failed:" },
]) {
  test(`failed rebuild shows a nearby error and allows retry (${response.status || "network"})`, async ({ page }) => {
    await stubArticles(page);
    await page.route("**/api/rebuild", (route) => response.networkFailure
      ? route.abort("failed") : route.fulfill({ status: response.status, json: response.json }));
    await page.goto("/ingest.html?space=competition");
    await page.locator("#authoring-token").fill("test-authoring-token");
    await page.locator("#rebuild-now").click();
    await expect(page.locator("#rebuild-status")).toContainText(response.message);
    await expect(page.locator("#rebuild-status")).toBeInViewport();
    await expect(page.locator("#rebuild-now")).toBeEnabled();
    await expect(page.getByRole("button", { name: "Ingest and rebuild", exact: true })).toBeEnabled();
    await expect(page.locator("#authoring-token")).toHaveValue("test-authoring-token");
  });
}

test("rebuild keeps its result visible when browser storage is unavailable", async ({ page }) => {
  await stubArticles(page);
  await page.addInitScript(() => {
    const setItem = Storage.prototype.setItem;
    Storage.prototype.setItem = function (key, value) {
      if (key === "civwiki-last-ingest-result") throw new DOMException("Storage unavailable", "SecurityError");
      return setItem.call(this, key, value);
    };
  });
  await page.route("**/api/rebuild", (route) => route.fulfill({ json: { refresh: { ok: true } } }));
  await page.goto("/ingest.html?space=competition");
  await page.locator("#rebuild-now").click();
  await expect(page.locator("#rebuild-status")).toHaveText("Rebuild completed.");
  await expect(page.locator("#rebuild-status")).toBeInViewport();
  await expect(page.locator("#ingest-status").getByRole("link", { name: "Reload page", exact: true })).toHaveAttribute(
    "href", /\/ingest.html\?space=competition$/);
  await expect(page.locator("#rebuild-now")).toBeEnabled();
});

test("successful ingest makes the pending article update clear after reload", async ({ page }) => {
  await stubArticles(page);
  await page.route("**/api/ingest", (route) => route.fulfill({ json: {
    article_href: "competition-competitor-index.html",
    article_sources_added: ["https://example.test/pricing"],
    source_hrefs: [{ source: "Pricing evidence", href: "https://example.test/pricing" }],
    refresh: { ok: true },
  } }));
  await page.goto("/ingest.html?space=competition");
  await expect(page.locator('[data-mode-panel="add"]')).toContainText(
    "The article text needs a separate update");
  await page.locator("#target-slug").selectOption("competition-competitor-index");
  await page.locator("#external-urls").fill("https://example.test/pricing");
  await Promise.all([
    page.waitForEvent("load"),
    page.getByRole("button", { name: "Ingest and rebuild", exact: true }).click(),
  ]);
  const status = page.locator("#ingest-status");
  await expect(status).toContainText("Last completed action");
  await expect(status).toContainText("This action does not rewrite the article text");
  await expect(status.getByRole("link", { name: "Open article", exact: true })).toBeVisible();
  await expect(status.getByRole("link", { name: "Pricing evidence", exact: true })).toBeVisible();
  await expect(status).not.toContainText("Open updated article");
});

test("Ingest carries each space and known article section into metadata", async ({ page }) => {
  await stubArticles(page);
  for (const [space, steward] of [
    ["competition", "transpara"], ["platform", "transpara"], ["civilization", "transpara-ai"], ["devops", "transpara"],
  ]) {
    await page.goto(`/${space}/index.html`);
    await page.getByRole("link", { name: "Ingest", exact: true }).click();
    await expect(page).toHaveURL(new RegExp(`/ingest.html\\?space=${space}$`));
    await expect(page.locator("#ingest-space")).toHaveValue(space);
    await expect(page.locator("#ingest-steward")).toHaveValue(steward);
    await expect(page.locator("#ingest-section")).toHaveValue("");
  }

  await page.goto("/competition-competitor-index.html");
  await page.getByRole("link", { name: "Ingest", exact: true }).click();
  await expect(page.locator("#ingest-space")).toHaveValue("competition");
  await expect(page.locator("#ingest-section")).toHaveValue("competitors");
  await expect(page.locator("#ingest-steward")).toHaveValue("transpara");

  await page.goto("/index.html");
  await page.getByRole("link", { name: "Ingest", exact: true }).click();
  await expect(page.locator("#ingest-space")).toHaveValue("competition");
  await expect(page.locator("#ingest-steward")).toHaveValue("transpara");
  await page.goto("/ingest.html?space=unknown&section=competitors");
  await expect(page.locator("#ingest-space")).toHaveValue("civilization");
  await expect(page.locator("#ingest-section")).toHaveValue("");
  await page.goto("/ingest.html?space=competition&section=architecture");
  await expect(page.locator("#ingest-space")).toHaveValue("competition");
  await expect(page.locator("#ingest-section")).toHaveValue("");
});

test("target selection respects shared placements and updates the steward", async ({ page }) => {
  await stubArticles(page);
  await page.goto("/ingest.html?space=platform");
  await page.locator("#target-slug").selectOption("competition-rtoi-comparison");
  await expect(page.locator("#ingest-space")).toHaveValue("platform");
  await expect(page.locator("#ingest-section")).toHaveValue("product-overview");
  await page.locator("#target-slug").selectOption("competition-competitor-index");
  await expect(page.locator("#ingest-space")).toHaveValue("competition");
  await expect(page.locator("#ingest-section")).toHaveValue("competitors");

  await page.goto("/ingest.html?space=civilization");
  await page.locator("#target-slug").selectOption("platform-transpara-mcp-boundary");
  await expect(page.locator("#ingest-space")).toHaveValue("civilization");
  await expect(page.locator("#ingest-section")).toHaveValue("architecture");
  await expect(page.locator("#ingest-steward")).toHaveValue("transpara");
  await page.locator("#target-slug").selectOption("");
  await page.locator("#ingest-space").selectOption("competition");
  await expect(page.locator("#ingest-section")).toHaveValue("");
  await expect(page.locator("#ingest-steward")).toHaveValue("transpara");
});

test("pasted email submits intact as a document, alone or with files and URLs", async ({ page, ingestReceiver }) => {
  await stubArticles(page);
  const { requests } = ingestReceiver;
  await page.route("**/api/ingest", (route) => route.continue({ url: ingestReceiver.url }));
  await page.goto("/ingest.html?space=competition");
  await page.locator("#target-slug").selectOption("competition-competitor-index");
  const email = "From: Research <research@example.test>\nSubject: Competitor update — café\n\n  First line\n> Quoted reply\n<script>untrusted()</script>\n";
  await page.getByLabel("Paste email or other text").fill(email);
  await page.getByRole("button", { name: "Ingest and rebuild", exact: true }).click();
  await expect.poll(() => requests.length).toBe(1);
  expect(requests[0]).toEqual({
    documents: [{ name: "pasted-text.txt", type: "text/plain;charset=utf-8", text: email }],
    space: "competition", section: "competitors", steward: "transpara", urls: "",
  });
  await expect(page.locator("#ingest-status")).toContainText("source kept for retry");
  await expect(page.locator("#pasted-text")).toHaveValue(email);

  await page.getByLabel("Source title (optional)").fill("Competitor update.txt");
  await page.locator("#documents").setInputFiles({
    name: "brief.md", mimeType: "text/markdown", buffer: Buffer.from("# Brief\n"),
  });
  await page.locator("#external-urls").fill("https://example.test/update");
  await page.getByRole("button", { name: "Ingest and rebuild", exact: true }).click();
  await expect.poll(() => requests.length).toBe(2);
  expect(requests[1].documents).toEqual([
    { name: "brief.md", type: "text/markdown", text: "# Brief\n" },
    { name: "Competitor update.txt", type: "text/plain;charset=utf-8", text: email },
  ]);
  expect(requests[1].urls).toBe("https://example.test/update");

  await page.locator("#pasted-text").fill(" \n\t ");
  await page.getByRole("button", { name: "Ingest and rebuild", exact: true }).click();
  await expect.poll(() => requests.length).toBe(3);
  expect(requests[2].documents).toEqual([
    { name: "brief.md", type: "text/markdown", text: "# Brief\n" },
  ]);
});

async function collectErrors(page) {
  const errors = [];
  page.on("console", (msg) => {
    if (msg.type() !== "error") return;
    const url = (msg.location() && msg.location().url) || "";
    if (BENIGN_404.test(url)) return;
    errors.push(`${msg.text()} (${url})`);
  });
  page.on("pageerror", (err) => errors.push(String(err)));
  return errors;
}

test("ingest selector renders with destructive modes gated", async ({ page }) => {
  const errors = await collectErrors(page);
  await page.goto("/ingest.html");

  await expect(page.locator('input[name="ingest-mode"]')).toHaveCount(3);
  await expect(page.locator('input[name="ingest-mode"][value="add"]')).toBeChecked();
  await expect(page.locator('[data-mode-panel="replace"]')).toBeHidden();
  await expect(page.locator('[data-mode-panel="remove"]')).toBeHidden();

  await page.locator('input[name="ingest-mode"][value="remove"]').check();
  await expect(page.locator('[data-mode-panel="remove"]')).toBeVisible();
  await expect(page.locator('[data-mode-panel="add"]')).toBeHidden();
  await expect(page.locator("#rm-submit")).toBeDisabled();
  await expect(page.locator("#rm-confirm")).toBeDisabled();
  await expect(page.locator('[data-mode-panel="remove"] .ingest-authority-note').first())
    .toContainText("never reads, checks, or transmits");

  await page.locator('input[name="ingest-mode"][value="replace"]').check();
  await expect(page.locator('[data-mode-panel="replace"]')).toBeVisible();
  await expect(page.locator("#rep-submit")).toBeDisabled();

  expect(errors, `console errors: ${errors.join("; ")}`).toHaveLength(0);
});

test("ingest selector renders in the light theme too", async ({ page }) => {
  await page.addInitScript(() => {
    try { window.localStorage.setItem("civwiki-theme", "light"); } catch (e) { /* ignore */ }
  });
  const errors = await collectErrors(page);
  await page.goto("/ingest.html");
  await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
  await expect(page.locator(".ingest-modes")).toBeVisible();
  await page.locator('input[name="ingest-mode"][value="remove"]').check();
  await expect(page.locator('[data-mode-panel="remove"]')).toBeVisible();
  await expect(page.locator("#rm-submit")).toBeDisabled();
  expect(errors, `console errors: ${errors.join("; ")}`).toHaveLength(0);
});
