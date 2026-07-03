// tests/arc-view.spec.js
// Browser E2E for the arc page view (Item 2b-visual, packet AC5): the
// now-panel, phase spine, and static legend render on both arc routes and in
// both themes, with zero console errors and no retired-engine artifacts.
const { test, expect } = require("@playwright/test");

// Known-benign local 404s: the live overlay fetches inflight.json and the
// shared page chrome fetches deploy-status.json — both best-effort files a
// serving host generates and a fresh local dist lacks (the UI degrades
// honestly); Chromium probes favicon.ico on its own. Everything else —
// script errors, other failed resources — stays fatal.
const BENIGN_404 = /\/(inflight\.json|deploy-status\.json|favicon\.ico)$/;

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

test("arc view renders the where-are-we read on both routes with no console errors", async ({ page }) => {
  for (const route of ["/civilization-arc.html", "/civilization_arc.html"]) {
    const errors = await collectErrors(page);
    await page.goto(route);

    // now-panel: current phase + active-now + next gate
    await expect(page.locator(".arc-now-phase")).toHaveText("Deployment / Operations");
    await expect(page.locator(".arc-now-item").first()).toBeVisible();
    await expect(page.locator(".arc-now-code")).toContainText("Gate-K·go-live");
    await expect(page.locator(".arc-gate-rollup")).toContainText("fail-closed rollup: planned · blocked");

    // spine: 15 phases, one frontier, blocked ring on stewardship
    await expect(page.locator("[data-arc-phase]")).toHaveCount(15);
    await expect(page.locator("[data-arc-phase-now]")).toHaveCount(1);
    await expect(page.locator('[data-arc-phase="stewardship"]')).toHaveClass(/arc-phase-blocked/);

    // static legend from the builder
    await expect(page.locator(".arc-view-legend")).toBeVisible();
    await expect(page.locator(".arc-view-legend")).toContainText("Every status is evidence-derived or stamped.");

    // retired engine absent
    await expect(page.locator("svg.arc-svg")).toHaveCount(0);
    await expect(page.locator(".arc-toolbar")).toHaveCount(0);
    await expect(page.locator("[data-arc-group]")).toHaveCount(0);

    // the live chip may read updated/stale/unavailable depending on the local
    // inflight.json — any of those is honest; a missing chip is not an error
    // here because the fetch is same-origin best-effort. Console must be clean.
    expect(errors, `console errors on ${route}: ${errors.join("; ")}`).toHaveLength(0);
  }
});

test("arc view renders in the light theme too", async ({ page }) => {
  await page.addInitScript(() => {
    try { window.localStorage.setItem("civwiki-theme", "light"); } catch (e) { /* ignore */ }
  });
  const errors = await collectErrors(page);
  await page.goto("/civilization-arc.html");
  await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
  await expect(page.locator(".arc-now-panel")).toBeVisible();
  await expect(page.locator("[data-arc-phase]")).toHaveCount(15);
  await expect(page.locator(".arc-view-legend")).toBeVisible();
  expect(errors, `console errors: ${errors.join("; ")}`).toHaveLength(0);
});
