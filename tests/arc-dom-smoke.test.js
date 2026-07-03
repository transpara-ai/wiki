// tests/arc-dom-smoke.test.js
// DOM smoke tests for the arc page view (civilizationArcView.js) — the
// now-panel, phase spine, retired-engine absence, live overlay semantics,
// and the ported governance-honesty panels. Design packet:
// docs/superpowers/specs/2026-07-03-arc-2b-visual-packet.md (AC1–AC3, AC6–AC7).
const fs = require("fs");
const path = require("path");
const vm = require("vm");
const assert = require("assert");
const { JSDOM } = require("jsdom");

const root = path.resolve(__dirname, "..");
const O = require("../compile/assets/civilizationOntology.js");
const V = require("../compile/assets/civilizationArcView.js");

const VIEW_ASSETS = [
  "civilizationOntology.js",
  "civilizationArcData.js",
  "civilizationProgressEvidence.js",
  "civilizationArcView.js",
];

function loadArcData() {
  const context = { window: {} };
  vm.createContext(context);
  vm.runInContext(
    fs.readFileSync(path.join(root, "compile/assets/civilizationArcData.js"), "utf8"),
    context
  );
  return context.window.CIVILIZATION_ARC_DATA;
}

function loadProgressEvidence() {
  const context = { window: {} };
  vm.createContext(context);
  vm.runInContext(
    fs.readFileSync(path.join(root, "compile/assets/civilizationProgressEvidence.js"), "utf8"),
    context
  );
  return context.window.CIVILIZATION_PROGRESS_EVIDENCE;
}

// ── Reusable mount helper — eval the four modules into a JSDOM window and
//    dispatch DOMContentLoaded. options.beforeView(win) runs after the data
//    assets load and before the view module, to mutate payloads under test.
function mountArc(options = {}) {
  const dom = new JSDOM('<!doctype html><div data-civilization-arc></div>', {
    pretendToBeVisual: true, runScripts: "outside-only", url: "http://127.0.0.1:8787/index.html",
  });
  VIEW_ASSETS.forEach((f) => {
    if (f === "civilizationArcView.js" && options.beforeView) options.beforeView(dom.window);
    dom.window.eval(fs.readFileSync(path.join(root, "compile/assets", f), "utf8"));
  });
  dom.window.document.dispatchEvent(new dom.window.Event("DOMContentLoaded"));
  const view = dom.window.document.querySelector(".civilization-arc-view");
  return { view, dom };
}

// Live-overlay mount: the root opts in via data-arc-live and fetch is stubbed.
function mountWithFetch(payload, opts = {}) {
  const dom = new JSDOM('<!doctype html><div data-civilization-arc data-arc-live="true"></div>', {
    pretendToBeVisual: true, runScripts: "outside-only", url: "http://127.0.0.1:8787/index.html",
  });
  dom.window.fetch = function () {
    if (opts.reject) return Promise.reject(new Error("network down"));
    return Promise.resolve({ ok: true, json: () => Promise.resolve(payload) });
  };
  VIEW_ASSETS.forEach((f) =>
    dom.window.eval(fs.readFileSync(path.join(root, "compile/assets", f), "utf8")));
  dom.window.document.dispatchEvent(new dom.window.Event("DOMContentLoaded"));
  return dom;
}

// ── Data contract: items[] exists and passes the ontology allowlist gate ──
function assertData(data) {
  assert(data, "CIVILIZATION_ARC_DATA missing");
  assert(Array.isArray(data.items), "data.items must be an array");
  assert(data.items.length > 0, "data.items must not be empty");

  // Fail-closed allowlist gate — every item must validate.
  const r = O.validateItems(data.items);
  assert.strictEqual(r.ok, true, `validateItems failed:\n${(r.errors || []).join("\n")}`);

  // Code facet: the panel renders item.code as the row identifier.
  data.items.forEach((it) => {
    assert.strictEqual(typeof it.code, "string", `item '${it.id}' must carry a string code`);
    assert(it.code.trim().length > 0, `item '${it.id}' code must be non-empty`);
  });

  const now = O.deriveNow(data.items);
  assert(Number.isFinite(now), `deriveNow must be finite, got ${now}`);
  assert(now > 0, `deriveNow must be > 0, got ${now}`);

  // Item 2b split (unchanged data model): the honest Gate-K pair.
  const gateK = data.items.find((it) => it.id === "gate-k");
  assert(gateK, "gate-k item missing");
  assert.strictEqual(gateK.status, "done");
  assert.strictEqual(gateK.blocked, false);
  assert.strictEqual(gateK.boundary_status, undefined);
  const gateKGo = data.items.find((it) => it.id === "gate-k-go-live");
  assert(gateKGo, "gate-k-go-live item missing");
  assert.strictEqual(gateKGo.status, "planned");
  assert.strictEqual(gateKGo.blocked, true);
  assert.strictEqual(gateKGo.blocked_reason, "gate");
  assert(
    gateKGo.criteria.some((c) => c.blocked === true),
    "gate-k-go-live must carry a blocked criterion"
  );
}

const { test } = require("node:test");

test('arc data passes the ontology contract (data model unchanged)', () => {
  assertData(loadArcData());
});

// ── AC1 — now-panel ─────────────────────────────────────────────────────────

test('now panel names the current phase from baked frontier', () => {
  const { view } = mountArc();
  assert(view, "arc view did not mount");
  const panel = view.querySelector(".arc-now-panel");
  assert(panel, "now panel missing");
  const phase = panel.querySelector(".arc-now-phase");
  assert(phase, "current phase heading missing");
  assert.strictEqual(phase.textContent, "Deployment / Operations");
  assert.match(panel.querySelector(".arc-now-frontier").textContent, /frontier .*seq 14\.36.*derived/);
});

test('active-now rows each carry an evidence stamp', () => {
  const { view } = mountArc();
  const rows = [...view.querySelectorAll(".arc-now-item")];
  assert.strictEqual(rows.length, 9, "baked active work census (packet §1)");
  rows.forEach((row) => {
    const stamp = row.querySelector(".arc-evidence");
    assert(stamp, `row ${row.getAttribute("data-arc-active-item")} missing its evidence stamp`);
    assert(stamp.querySelector(".arc-evidence-prov"), "provenance badge must always show");
    assert(stamp.textContent.trim().length > 0, "stamp must never be blank");
    // absence renders honestly: no ref/date/href ⇒ the explicit placeholder
    const hasSource = stamp.querySelector(".arc-evidence-ref, .arc-evidence-date, .arc-evidence-link");
    if (!hasSource) {
      assert(stamp.querySelector(".arc-evidence-none"), "sourceless row must say 'no source ref'");
    }
  });
});

test('next gate is gate-k-go-live with criteria checklist and recomputed rollup', () => {
  const { view } = mountArc();
  const panel = view.querySelector(".arc-now-panel");
  assert.match(panel.querySelector(".arc-now-code").textContent, /Gate-K·go-live/);
  const badge = panel.querySelector(".arc-badge-blocked");
  assert(badge, "blocked badge missing");
  assert.match(badge.textContent, /blocked · gate/);
  // the gate's own provenance must render (its criterion carries no ref —
  // the gate-level ref docs#138 is the panel's only evidence pointer)
  const gateStamp = panel.querySelector(".arc-gate-evidence .arc-evidence");
  assert(gateStamp, "next-gate panel must stamp the gate's own evidence");
  assert.match(gateStamp.textContent, /docs#138/);
  const crits = [...panel.querySelectorAll(".arc-gate-criterion")];
  assert.strictEqual(crits.length, 1, "gate-k-go-live has one criterion");
  assert.match(crits[0].textContent, /go-live boundary revalidation/);
  assert(crits[0].classList.contains("arc-criterion-blocked"), "the blocked_criterion row is highlighted");
  assert.match(panel.querySelector(".arc-gate-rollup").textContent,
    /fail-closed rollup: planned · blocked/);
});

// ── AC2 — phase spine ───────────────────────────────────────────────────────

test('spine renders 15 phases with one derived frontier on deployment', () => {
  const { view } = mountArc();
  const phases = [...view.querySelectorAll("[data-arc-phase]")];
  assert.strictEqual(phases.length, 15);
  const now = [...view.querySelectorAll("[data-arc-phase-now]")];
  assert.strictEqual(now.length, 1, "exactly one frontier marker");
  assert.strictEqual(now[0].getAttribute("data-arc-phase"), "deployment");
  const stewardship = view.querySelector('[data-arc-phase="stewardship"]');
  assert(stewardship.classList.contains("arc-phase-blocked"), "stewardship carries the blocked ring");
  assert(!stewardship.classList.contains("arc-phase-collapsed"), "a blocked phase never collapses");
});

test('spine collapse tracks done-and-unblocked exactly', () => {
  const { view } = mountArc();
  const data = loadArcData();
  const model = V.spine(data.items, data.sprints);
  const byId = {};
  model.forEach((p) => { byId[p.id] = p; });
  const phases = [...view.querySelectorAll("[data-arc-phase]")];
  assert.strictEqual(phases.length, model.length);
  phases.forEach((el) => {
    const p = byId[el.getAttribute("data-arc-phase")];
    assert(p, `unexpected phase ${el.getAttribute("data-arc-phase")}`);
    const wantCollapsed = p.status === "done" && p.blocked === false;
    assert.strictEqual(el.classList.contains("arc-phase-collapsed"), wantCollapsed,
      `phase ${p.id}: collapse ⇔ done AND unblocked`);
    assert.strictEqual(el.getAttribute("data-arc-phase-status"), p.status, `phase ${p.id}: status class`);
  });
  assert.strictEqual(phases.filter((el) => el.classList.contains("arc-phase-collapsed")).length, 12,
    "snapshot anchor: 12 done phases collapse today");
});

// ── AC3 — retired engine is gone ────────────────────────────────────────────

test('retired engine artifacts are absent', () => {
  const { view, dom } = mountArc();
  const doc = dom.window.document;
  assert(view, "view mounts");
  ["svg.arc-svg", ".arc-toolbar", "[data-arc-group]", ".arc-zoom", ".arc-track-band",
   ".arc-tooltip", ".arc-detail-panel", "[data-arc-item]"].forEach((sel) => {
    assert.strictEqual(doc.querySelectorAll(sel).length, 0, `retired artifact rendered: ${sel}`);
  });
});

// ── AC6 — fail-closed display ───────────────────────────────────────────────

test('invalid baked data renders the error notice and no panel', () => {
  const { view, dom } = mountArc({
    beforeView(win) { win.CIVILIZATION_ARC_DATA.items[0].bogus_key = true; },
  });
  const doc = dom.window.document;
  const err = doc.querySelector(".arc-error");
  assert(err, "error notice missing on invalid data");
  assert.match(err.textContent, /fail-closed/i);
  assert.strictEqual(doc.querySelectorAll(".arc-now-panel").length, 0, "no partial render");
  assert.strictEqual(doc.querySelectorAll("[data-arc-phase]").length, 0, "no spine on invalid data");
});

// ── live overlay (AC1 stamps + AC6 fail-safe, semantics preserved) ──────────

test('live overlay is OPT-IN: with no flag the fetch never fires and no chip appears', async () => {
  const dom = new JSDOM('<!doctype html><div data-civilization-arc></div>', {
    pretendToBeVisual: true, runScripts: "outside-only", url: "http://127.0.0.1:8787/index.html",
  });
  let fetched = false;
  dom.window.fetch = function () { fetched = true; return Promise.resolve({ ok: false }); };
  VIEW_ASSETS.forEach((f) =>
    dom.window.eval(fs.readFileSync(path.join(root, "compile/assets", f), "utf8")));
  dom.window.document.dispatchEvent(new dom.window.Event("DOMContentLoaded"));
  await new Promise((r) => setTimeout(r, 0));
  const view = dom.window.document.querySelector(".civilization-arc-view");
  assert.strictEqual(fetched, false, "no inflight.json fetch when the overlay is not enabled");
  assert(!view.querySelector(".arc-live-chip"), "no live chip when the overlay is disabled");
  assert(view.querySelectorAll("[data-arc-phase]").length > 0, "the baked arc still renders on its own");
});

const LIVE_PR = {
  generated: "2026-06-17 14:00", window_days: 30, repos: ["hive"], errors: [],
  items: [{ id: "pr-hive-1", code: "hive#1", type: "work", label: "fix: live overlay",
    status: "active", blocked: false, provenance: "derived", repo: ["hive"],
    sprint: "stewardship", href: "https://github.com/transpara-ai/hive/pull/1",
    author: "msaucier", note: "open · @msaucier" }],
};

test('live overlay: the PR appears in active-now with a live evidence stamp', async () => {
  const dom = mountWithFetch(LIVE_PR);
  await new Promise((r) => setTimeout(r, 0));
  const view = dom.window.document.querySelector(".civilization-arc-view");
  const row = view.querySelector('[data-arc-active-item="pr-hive-1"]');
  assert(row, "live PR row should render in the active-now column");
  assert.match(row.textContent, /@msaucier/);
  const live = row.querySelector(".arc-evidence-live");
  assert(live, "live row must carry the observed stamp");
  assert.match(live.textContent, /observed 2026-06-17 14:00/);
  const chip = view.querySelector(".arc-live-chip");
  assert(chip && /updated 2026-06-17 14:00/.test(chip.textContent), "chip should show generated time");
});

test('live overlay never moves the frontier, phase, or next gate (baked anchor)', async () => {
  const dom = mountWithFetch(LIVE_PR);
  await new Promise((r) => setTimeout(r, 0));
  const view = dom.window.document.querySelector(".civilization-arc-view");
  // the live item merges ahead of the baked frontier and is tagged
  // "stewardship" — the phase read must stay anchored to baked items
  const now = [...view.querySelectorAll("[data-arc-phase-now]")];
  assert.strictEqual(now.length, 1);
  assert.strictEqual(now[0].getAttribute("data-arc-phase"), "deployment",
    "an open PR must not teleport the current phase to stewardship");
  assert.strictEqual(view.querySelector(".arc-now-phase").textContent, "Deployment / Operations");
  assert.match(view.querySelector(".arc-now-frontier").textContent, /seq 14\.36/);
  assert.match(view.querySelector(".arc-now-code").textContent, /Gate-K·go-live/);
});

test('live overlay FAILS SAFE: a rejected fetch keeps the baked render, no live row', async () => {
  const dom = mountWithFetch(null, { reject: true });
  await new Promise((r) => setTimeout(r, 0));
  const view = dom.window.document.querySelector(".civilization-arc-view");
  assert(!view.querySelector('[data-arc-active-item="pr-hive-1"]'), "no live row on fetch failure");
  assert(view.querySelectorAll("[data-arc-phase]").length > 0, "baked render survives");
  const chip = view.querySelector(".arc-live-chip");
  assert(chip && /unavailable/.test(chip.textContent), "chip warns unavailable");
});

test('live overlay FAILS SAFE on invalid live data: merge rejected → baked kept + chip warns', async () => {
  const BAD = { generated: "g", window_days: 30, repos: ["hive"], errors: [],
    items: [{ id: "pr-bad-1", code: "bad#1", type: "work", label: "x", status: "merged", // ∉ STATUS_ORDER
      blocked: false, provenance: "derived", repo: ["hive"], sprint: "stewardship", author: "x", note: "x" }] };
  const dom = mountWithFetch(BAD);
  await new Promise((r) => setTimeout(r, 0));
  const view = dom.window.document.querySelector(".civilization-arc-view");
  assert(!view.querySelector('[data-arc-active-item="pr-bad-1"]'), "invalid live item must not render");
  assert(view.querySelectorAll("[data-arc-phase]").length > 0, "baked render survives");
  const chip = view.querySelector(".arc-live-chip");
  assert(chip && /unavailable/.test(chip.textContent), "chip warns unavailable on rejected merge");
});

test('live overlay FAILS CLOSED on a degraded refresh: errors present → chip warns "stale", never "updated"', async () => {
  const DEGRADED = { generated: "2026-06-17 14:00", window_days: 30, repos: ["hive"],
    errors: ["hive open: RuntimeError"], items: [] };
  const dom = mountWithFetch(DEGRADED);
  await new Promise((r) => setTimeout(r, 0));
  const view = dom.window.document.querySelector(".civilization-arc-view");
  const chip = view.querySelector(".arc-live-chip");
  assert(chip, "a chip must render on a degraded refresh");
  assert.doesNotMatch(chip.textContent, /updated/, "a failed refresh must NOT claim 'live · updated'");
  assert.match(chip.textContent, /stale|source error/, "chip must signal the degraded refresh");
  assert(chip.classList.contains("arc-live-chip-warn"), "degraded chip must use the warn style");
  assert(view.querySelectorAll("[data-arc-phase]").length > 0, "baked render survives a degraded refresh");
});

test('a draft live PR renders with the blocked dot (blocked overlay honored)', async () => {
  const DRAFT = { generated: "g", window_days: 30, repos: ["hive"], errors: [],
    items: [Object.assign({}, LIVE_PR.items[0],
      { id: "pr-hive-2", code: "hive#2", blocked: true, blocked_reason: "gate" })] };
  const dom = mountWithFetch(DRAFT);
  await new Promise((r) => setTimeout(r, 0));
  const view = dom.window.document.querySelector(".civilization-arc-view");
  const row = view.querySelector('[data-arc-active-item="pr-hive-2"]');
  assert(row, "draft PR row renders");
  assert(row.querySelector(".arc-status-dot-blocked"), "draft PR shows the blocked overlay dot");
});

// ── XSS hardening (safeHref allowlist preserved) ────────────────────────────

test('javascript: href is never assigned to any rendered link (XSS hardening)', () => {
  const { view, dom } = mountArc({
    beforeView(win) {
      // poison an ACTIVE work item so the row renders in the panel
      const victim = win.CIVILIZATION_ARC_DATA.items.find(
        (it) => it.type === "work" && it.status === "active");
      victim.href = "javascript:alert(1)";
    },
  });
  const hrefs = [...dom.window.document.querySelectorAll("a")].map((a) => a.getAttribute("href"));
  assert(hrefs.length > 0, "sanity: some links render");
  assert(!hrefs.some((h) => h && /^(javascript:|data:|vbscript:)/i.test(h) || /^[\\/]{2}/.test(h || "")),
    "unsafe href rendered");
  assert(view.querySelectorAll(".arc-evidence-link[href^='javascript']").length === 0);
});

// ── AC7 — governance-honesty panels survive the engine retirement ───────────

test('operation progress evidence snapshot renders under the arc', () => {
  const { view } = mountArc();
  const panel = view.querySelector('.arc-progress-panel');
  assert(panel, 'progress evidence panel missing');
  assert.match(panel.textContent, /Progress evidence snapshot/);
  assert.match(panel.textContent, /snapshot2026-06-21T00:00:00Z/);
  assert.match(panel.textContent, /Test 001 Remains YELLOW/);
  assert.match(panel.textContent, /Omitted sources/);
  assert.match(panel.textContent, /not live truth/i);
  assert.doesNotMatch(panel.textContent, /operator_notes|raw_issue_body|Source notes are intentionally not exported|Raw issue text is not exported/);

  const hrefs = [...panel.querySelectorAll('a')].map((a) => a.getAttribute('href'));
  assert(hrefs.includes('https://github.com/transpara-ai/operation/pull/28'));
  assert(hrefs.includes('https://github.com/transpara-ai/operation/issues/26'));
  assert(!hrefs.some((href) => href && href.includes('github.com/transpara-ai/docs')),
    'progress panel must not link private docs repo evidence');
  assert.doesNotMatch(panel.textContent, /transpara-ai\/docs|docs#[0-9]+/i);
});

test('operation progress evidence fails closed without explicit public-safe metadata', () => {
  [
    ["public_safe false", (win) => { win.CIVILIZATION_PROGRESS_EVIDENCE.privacy.public_safe = false; }],
    ["missing privacy", (win) => { delete win.CIVILIZATION_PROGRESS_EVIDENCE.privacy; }],
    ["schema mismatch", (win) => { win.CIVILIZATION_PROGRESS_EVIDENCE.schema_version = 2; }],
  ].forEach(([label, beforeView]) => {
    const { view } = mountArc({ beforeView });
    const panel = view.querySelector('.arc-progress-panel');
    assert(panel, `progress evidence panel missing for ${label}`);
    assert.match(panel.textContent, /No public-safe progress evidence export is available/);
    assert.strictEqual(panel.querySelectorAll('.arc-progress-item').length, 0, label);
    assert.doesNotMatch(panel.textContent, /Test 001 Remains YELLOW/);
  });
});

test('operation progress evidence rejects unsafe progress links', () => {
  const { view } = mountArc({
    beforeView(win) {
      win.CIVILIZATION_PROGRESS_EVIDENCE_SOURCE.operation_pr_url = 'data:text/html,unsafe';
      win.CIVILIZATION_PROGRESS_EVIDENCE.items[0].source_url = 'javascript:alert(1)';
    },
  });
  const panel = view.querySelector('.arc-progress-panel');
  assert(panel, 'progress evidence panel missing');
  const hrefs = [...panel.querySelectorAll('a')].map((a) => a.getAttribute('href'));
  assert(!hrefs.some((href) => href && /^(javascript:|data:|\/\/)/i.test(href)), 'unsafe progress href rendered');
  assert.match(panel.textContent, /transpara-ai\/operation#28/);
  assert.match(panel.textContent, /governing authority on file/);
});

test('operation progress evidence asset omits private governing-repo identifiers', () => {
  const asset = fs.readFileSync(path.join(root, "compile/assets/civilizationProgressEvidence.js"), "utf8");
  assert.doesNotMatch(asset, /github\.com\/transpara-ai\/docs|transpara-ai\/docs|docs#[0-9]+/i);
  assert.strictEqual(loadProgressEvidence().schema_version, 1);
});

test('live-reader correction proof renders public-safe correction labels under the arc', () => {
  const { view } = mountArc();
  const panel = view.querySelector('.arc-live-reader-correction');
  assert(panel, 'live-reader correction panel missing');
  assert.match(panel.textContent, /Live Reader Correction Proof/);
  assert.match(panel.textContent, /source transpara-ai\/operation#30/);
  assert.match(panel.textContent, /generated2026-06-22T15:10:35Z/);
  assert.match(panel.textContent, /freshnessfixture/);
  assert.match(panel.textContent, /Test 001 Remains YELLOW/);
  assert.match(panel.textContent, /corrected \/ source_recorded/);
  assert.match(panel.textContent, /superseded \/ stale/);
  assert.match(panel.textContent, /Missing or unavailable sources/);
  assert.match(panel.textContent, /unavailable-source/);
  assert.match(panel.textContent, /not live truth/i);
  assert.match(panel.textContent, /not Gate X closure/i);
});

test('live-reader correction proof fails closed without valid public-safe metadata', () => {
  [
    ["public_safe false", (win) => { win.CIVILIZATION_LIVE_READER_CORRECTION.privacy.public_safe = false; }],
    ["network access", (win) => { win.CIVILIZATION_LIVE_READER_CORRECTION.privacy.network_access = "live"; }],
    ["schema mismatch", (win) => { win.CIVILIZATION_LIVE_READER_CORRECTION.schema_version = 2; }],
    ["empty items", (win) => { win.CIVILIZATION_LIVE_READER_CORRECTION.items = []; }],
  ].forEach(([label, beforeView]) => {
    const { view } = mountArc({ beforeView });
    const panel = view.querySelector('.arc-live-reader-correction');
    assert(panel, `correction panel missing for ${label}`);
    assert.match(panel.textContent, /No valid public-safe correction export is available/, label);
    assert.strictEqual(panel.querySelectorAll('.arc-progress-item').length, 0, label);
  });
});

test('live-reader correction proof rejects unsafe links', () => {
  const { view } = mountArc({
    beforeView(win) {
      win.CIVILIZATION_LIVE_READER_CORRECTION.source.operation_pr_url = 'javascript:alert(1)';
      win.CIVILIZATION_LIVE_READER_CORRECTION.items[0].source_refs = [
        { repo: "transpara-ai/operation", ref: "operation#30", url: "data:text/html,bad" },
      ];
    },
  });
  const panel = view.querySelector('.arc-live-reader-correction');
  const hrefs = [...panel.querySelectorAll('a')].map((a) => a.getAttribute('href'));
  assert(!hrefs.some((href) => href && /^(javascript:|data:|\/\/)/i.test(href)), 'unsafe correction href rendered');
});
