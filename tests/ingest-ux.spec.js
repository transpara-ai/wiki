// tests/ingest-ux.spec.js
// Browser E2E for the ingest operation selector + destructive-mode scaffold
// (fe-ux packet AC1/AC8): three modes render, destructive panels stay hidden
// until selected, submits are disabled at birth, both themes, zero console
// errors. Behavior (preview gate state machine) lives in the dom-smoke test
// where fetch is stubbable; this spec covers the static render only.
const { test, expect } = require("@playwright/test");

// The static test server has no authoring API: /api/articles 404s and the UI
// degrades honestly, same class as inflight/deploy-status (see arc-view.spec).
const BENIGN_404 = /\/(api\/articles|inflight\.json|deploy-status\.json|favicon\.ico)$/;

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
