const fs = require("fs");
const path = require("path");
const vm = require("vm");
const assert = require("assert");
const { JSDOM } = require("jsdom");

const root = path.resolve(__dirname, "..");
const O = require("../compile/assets/civilizationOntology.js");

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

// ── Reusable mount helper — eval all five modules into a JSDOM window and
//    dispatch DOMContentLoaded. Returns { nav, svg, dom } for test assertions.
function mountArc(options = {}) {
  const dom = new JSDOM('<!doctype html><div data-civilization-arc-nav></div>', {
    pretendToBeVisual: true, runScripts: "outside-only", url: "http://127.0.0.1:8787/index.html",
  });
  ["civilizationOntology.js", "civilizationArcData.js", "civilizationArcLayout.js",
   "civilizationArcDraw.js", "civilizationProgressEvidence.js", "civilizationArcNav.js"].forEach((f) => {
    dom.window.eval(fs.readFileSync(path.join(root, "compile/assets", f), "utf8"));
    if (f === "civilizationProgressEvidence.js" && options.beforeNav) options.beforeNav(dom.window);
  });
  dom.window.document.dispatchEvent(new dom.window.Event("DOMContentLoaded"));
  const nav = dom.window.document.querySelector(".civilization-arc-nav");
  const svg = nav ? nav.querySelector("svg.arc-svg") : null;
  return { nav, svg, dom };
}

// ── Data contract: items[] exists and passes the ontology allowlist gate ──
function assertData(data) {
  assert(data, "CIVILIZATION_ARC_DATA missing");
  assert(Array.isArray(data.items), "data.items must be an array");
  assert(data.items.length > 0, "data.items must not be empty");

  // Fail-closed allowlist gate — every item must validate.
  const r = O.validateItems(data.items);
  assert.strictEqual(r.ok, true, `validateItems failed:\n${(r.errors || []).join("\n")}`);

  // ── Code facet: every item carries a non-empty string short code ──
  // The default (clean) chart view renders item.code as the node text, so a
  // missing/empty code would leave a node unreadable.
  data.items.forEach((it) => {
    assert.strictEqual(
      typeof it.code,
      "string",
      `item '${it.id}' code must be a string, got ${typeof it.code}`
    );
    assert(it.code.trim().length > 0, `item '${it.id}' code must be non-empty`);
  });

  // ── Code uniqueness: codes label nodes and the code key, so they must be unique ──
  const codeCounts = new Map();
  data.items.forEach((it) => {
    codeCounts.set(it.code, (codeCounts.get(it.code) || 0) + 1);
  });
  const dupedCodes = Array.from(codeCounts.entries())
    .filter(([, n]) => n > 1)
    .map(([c]) => c);
  assert.strictEqual(
    dupedCodes.length,
    0,
    `every item.code must be unique; duplicates: ${dupedCodes.join(", ")}`
  );

  // ── Gate grouping lanes by family: the "family lanes, all gates" model ──
  // grouping="gate" lanes by item.family; the expanded gate landscape must
  // surface the three load-bearing gate families (ordered by GATE_FAMILIES).
  const gateLanes = O.groupBy(data.items, "gate").map((l) => l.lane);
  ["v3.9 milestones (A-J)", "Deployment register (G-0..G-8.4)", "v4.0 (K-V)"].forEach(
    (fam) => {
      assert(
        gateLanes.includes(fam),
        `grouping="gate" must include the '${fam}' lane; saw: ${gateLanes.join(" | ")}`
      );
    }
  );
  // GATE_FAMILIES ordering: the v3.9-milestones lane precedes the v4.0 lane.
  assert(
    gateLanes.indexOf("v3.9 milestones (A-J)") < gateLanes.indexOf("v4.0 (K-V)"),
    `gate lanes should follow GATE_FAMILIES order; saw: ${gateLanes.join(" | ")}`
  );

  // Derived "now" must be a finite, positive frontier.
  const now = O.deriveNow(data.items);
  assert(Number.isFinite(now), `deriveNow must be finite, got ${now}`);
  assert(now > 0, `deriveNow must be > 0, got ${now}`);

  // executionPlan is still present and consumed by the plan board.
  assert(data.executionPlan, "execution plan missing");
  assert(/^\d{4}-\d{2}-\d{2}$/.test(data.executionPlan.updated), "execution plan date must be ISO");

  // Gate K is closed by the pre-go-live waiver (docs#138) — done, not blocked —
  // while the go-live revalidation residual stays machine-readable on the dot.
  const gateK = data.items.find((it) => it.id === "gate-k");
  assert(gateK, "gate-k item missing");
  assert.strictEqual(gateK.status, "done");
  assert.strictEqual(gateK.blocked, false);
  assert.strictEqual(gateK.boundary_status, "pre-live-closed-go-live-blocked");
  assert.strictEqual(gateK.go_live_revalidation, "blocked");
  assert(
    O.groupBy(data.items, "status").some((lane) =>
      lane.lane === "done" && lane.items.some((it) => it.id === "gate-k")
    ),
    "gate-k (waiver-closed) must sit in the done lane, no longer blocked"
  );
}

// ── Rendered DOM: the new chart structure exists ──
function assertRenderedDom() {
  const { nav, svg } = mountArc();
  assert(nav, "arc nav did not mount");
  assert(svg, "SVG not rendered");
  assert.strictEqual(nav.querySelectorAll(".arc-track-band").length, 3, "expected 3 track bands");
  assert.strictEqual(nav.querySelectorAll(".arc-track-label").length, 3, "expected 3 track labels");
  assert(nav.querySelectorAll(".arc-subrow-label").length >= 4, "expected >=4 gate-family sub-row labels");
  assert(nav.querySelectorAll(".arc-item-group").length > 0, "no item node groups produced");
  assert(nav.querySelectorAll(".arc-marker").length > 0, "no item shapes produced");
  assert(nav.querySelector(".arc-now-line"), "now-line element missing");
  assert.match(nav.querySelector(".arc-now-panel").textContent, /Gate-K/);
  assert.match(nav.querySelector(".arc-now-panel").textContent, /blocked/i);
  assert.strictEqual(nav.querySelectorAll(".arc-now-blocker").length, 0, "now panel should degrade to gate-only focus when no blocked work item remains");
}

const { test } = require("node:test");

test('axis renders 15 sprint start-ticks and no era labels', () => {
  const { svg } = mountArc();
  assert.strictEqual(svg.querySelectorAll('.arc-sprint-tick-label').length, 15);
  assert.strictEqual(svg.querySelectorAll('.arc-era-label').length, 0);
  assert.ok(svg.querySelector('.arc-now-line')); // now-line preserved
});

test('gate sub-row labels are legible (>=11px) and present for 4 families', () => {
  const { svg } = mountArc();
  const subs = [...svg.querySelectorAll('.arc-subrow-label')];
  assert.ok(subs.length >= 4);
  subs.forEach(t => assert.ok(Number(t.getAttribute('font-size')) >= 11));
});

test('tooltip shows sprint + ordinal step + provenance', () => {
  const { nav: root, svg } = mountArc();
  const marker = svg.querySelector('[data-arc-item]');
  marker.dispatchEvent(new root.ownerDocument.defaultView.MouseEvent('mouseover', { bubbles: true }));
  const tip = root.querySelector('.arc-tooltip');
  assert.strictEqual(tip.hidden, false);
  assert.match(tip.textContent, /step \d+ of 120/);
  assert.match(tip.textContent, /sprint ·/);
});

// ── XSS hardening: javascript: hrefs must never be assigned to a rendered link ──
// Helper: mount a fresh JSDOM, inject custom hrefs onto items, fire DOMContentLoaded, return nav.
function mountWithInjectedHrefs(hrefMap, evidenceMap = {}) {
  const dom = new JSDOM('<!doctype html><div data-civilization-arc-nav></div>', {
    pretendToBeVisual: true, runScripts: "outside-only", url: "http://127.0.0.1:8787/index.html",
  });
  ["civilizationOntology.js", "civilizationArcData.js", "civilizationArcLayout.js",
   "civilizationArcDraw.js", "civilizationProgressEvidence.js"].forEach((f) =>
    dom.window.eval(fs.readFileSync(path.join(root, "compile/assets", f), "utf8")));
  const items = dom.window.CIVILIZATION_ARC_DATA.items;
  Object.keys(hrefMap).forEach((k) => { items[Number(k)].href = hrefMap[k]; });
  Object.keys(evidenceMap).forEach((k) => { items[Number(k)].evidence_links = evidenceMap[k]; });
  dom.window.eval(fs.readFileSync(path.join(root, "compile/assets/civilizationArcNav.js"), "utf8"));
  dom.window.document.dispatchEvent(new dom.window.Event("DOMContentLoaded"));
  const nav = dom.window.document.querySelector(".civilization-arc-nav");
  return { nav, items, dom };
}

function triggerItem(nav, item, dom) {
  const id = String(item.id);
  const marker = nav.querySelector('[data-arc-item="' + id + '"]');
  if (marker) {
    marker.dispatchEvent(new dom.window.MouseEvent('mouseover', { bubbles: true }));
    marker.dispatchEvent(new dom.window.MouseEvent('click', { bubbles: true }));
  }
  return marker;
}

test('javascript: href is never assigned to any rendered link (XSS hardening)', () => {
  // Test three malicious hrefs and two safe hrefs across different items.
  const { nav, items, dom } = mountWithInjectedHrefs({
    0: "javascript:alert(1)",           // MUST be rejected
    1: "//evil.example/x",              // protocol-relative — MUST be rejected
    2: "data:text/html,<script>xss</script>",  // data: — MUST be rejected
    3: "https://example.com/safe",      // MUST render as link
    4: "the-civilization.html",         // bare relative (real data format) — MUST render as link
  }, {
    5: [
      { href: "javascript:alert(2)" },
      { label: "bad evidence javascript", href: "javascript:alert(1)" },
      { label: "bad evidence data", href: "data:text/html,<script>xss</script>" },
      { label: "safe evidence", href: "https://example.com/evidence" },
    ],
  });
  assert(nav, "nav did not mount");

  // Trigger malicious items: hover + click each so both tooltip and detail panel are exercised.
  [0, 1, 2].forEach((idx) => triggerItem(nav, items[idx], dom));
  triggerItem(nav, items[5], dom);

  // Assert: no <a> in the nav has any dangerous href (malicious items active in detail panel).
  const dangLinks = [...nav.querySelectorAll("a")].filter((a) => {
    const h = (a.getAttribute("href") || "");
    return /^javascript:/i.test(h) || /^[\\/]{2}/.test(h) || /^data:/i.test(h);
  });
  assert.strictEqual(
    dangLinks.length, 0,
    "Dangerous links found: " + dangLinks.map((a) => a.getAttribute("href")).join(", ")
  );

  const safeEvidenceLinks = [...nav.querySelectorAll(".arc-detail-evidence-link")]
    .map((a) => a.getAttribute("href"));
  assert.deepStrictEqual(safeEvidenceLinks, ["https://example.com/evidence"]);
  assert.doesNotMatch(nav.querySelector(".arc-detail-panel").textContent, /evidence\s*·/i);

  // Assert happy path: safe https link renders (click item 3 to load it in detail panel).
  triggerItem(nav, items[3], dom);
  const safeLinks = [...nav.querySelectorAll("a")].filter((a) => (a.getAttribute("href") || "").startsWith("https://example.com/safe"));
  assert.ok(safeLinks.length >= 1, "Safe https href should render a link");

  // Assert happy path: bare relative (the-civilization.html) renders as a link — must NOT vanish.
  triggerItem(nav, items[4], dom);
  const relLinks = [...nav.querySelectorAll("a")].filter((a) => (a.getAttribute("href") || "") === "the-civilization.html");
  assert.ok(relLinks.length >= 1, "Bare relative href 'the-civilization.html' must render a link (safeHref must not reject it)");
});

// --- grouping toolbar (Task 5) ---
test('grouping toolbar: six group buttons render, Tracks active by default', () => {
  const { nav } = mountArc();
  const btns = [...nav.querySelectorAll('[data-arc-group]')];
  assert.deepStrictEqual(btns.map(b => b.getAttribute('data-arc-group')),
    ['tracks', 'status', 'repo', 'sprint', 'gate', 'actor']);
  assert.strictEqual(nav.querySelector('.arc-group-btn-active').getAttribute('data-arc-group'), 'tracks');
  assert.strictEqual(nav.querySelectorAll('.arc-track-band').length, 3); // default unchanged
});

test('clicking "Status" regroups the lanes and marks the button active', () => {
  const { nav, dom } = mountArc();
  nav.querySelector('[data-arc-group="status"]').dispatchEvent(new dom.window.MouseEvent('click', { bubbles: true }));
  const labels = [...nav.querySelectorAll('.arc-track-label')].map(t => t.textContent);
  assert.ok(labels.includes('done') && labels.includes('planned'), 'status lanes present; got ' + labels.join(' | '));
  assert.strictEqual(nav.querySelector('.arc-group-btn-active').getAttribute('data-arc-group'), 'status');
});

test('clicking "Gate" regroups the lanes by gate family (the dimension is reachable in the UI)', () => {
  const { nav, dom } = mountArc();
  nav.querySelector('[data-arc-group="gate"]').dispatchEvent(new dom.window.MouseEvent('click', { bubbles: true }));
  const labels = [...nav.querySelectorAll('.arc-track-label')].map(t => t.textContent);
  assert.ok(labels.includes('v4.0 (K-V)'), 'gate-family lanes present; got ' + labels.join(' | '));
  assert.strictEqual(nav.querySelector('.arc-group-btn-active').getAttribute('data-arc-group'), 'gate');
});

test('Repo view shows Civilization/Governance group headers, 8 named lanes, no (other)', () => {
  const { nav, dom } = mountArc();
  nav.querySelector('[data-arc-group="repo"]').dispatchEvent(new dom.window.MouseEvent('click', { bubbles: true }));
  const headers = [...nav.querySelectorAll('.arc-group-header')].map(h => h.textContent);
  assert.deepStrictEqual(headers, ['Civilization', 'Governance'],
    'in-collection groups are marked; got ' + headers.join(' | '));
  const labels = [...nav.querySelectorAll('.arc-track-label')].map(t => t.textContent);
  assert.deepStrictEqual(labels,
    ['agent', 'docs', 'eventgraph', 'hive', 'site', 'work', 'civilization-wiki', 'civilization-operation'],
    'all 8 collection repos render as named lanes; got ' + labels.join(' | '));
  assert.ok(!labels.includes('(other)'), 'the generic (other) bucket lane is gone');
});

// --- live overlay (Task 6) ---
// The live overlay is OPT-IN (it needs a host that generates inflight.json). These
// tests exercise the overlay itself, so they turn it on via window.CIV_ARC_LIVE.
function mountWithFetch(inflightPayload, opts) {
  const dom = new JSDOM('<!doctype html><div data-civilization-arc-nav></div>', {
    pretendToBeVisual: true, runScripts: "outside-only", url: "http://127.0.0.1:8787/index.html",
  });
  dom.window.CIV_ARC_LIVE = true;                 // enable the opt-in live overlay for these tests
  dom.window.fetch = function () {
    if (opts && opts.reject) return Promise.reject(new Error("network"));
    return Promise.resolve({ ok: true, json: function () { return Promise.resolve(inflightPayload); } });
  };
  ["civilizationOntology.js", "civilizationArcData.js", "civilizationArcLayout.js",
   "civilizationArcDraw.js", "civilizationProgressEvidence.js", "civilizationArcNav.js"].forEach((f) =>
    dom.window.eval(fs.readFileSync(path.join(root, "compile/assets", f), "utf8")));
  dom.window.document.dispatchEvent(new dom.window.Event("DOMContentLoaded"));
  return dom;
}

test('live overlay is OPT-IN: with no flag the fetch never fires and no chip appears', async () => {
  const dom = new JSDOM('<!doctype html><div data-civilization-arc-nav></div>', {
    pretendToBeVisual: true, runScripts: "outside-only", url: "http://127.0.0.1:8787/index.html",
  });
  let fetched = false;
  dom.window.fetch = function () { fetched = true; return Promise.resolve({ ok: false }); };
  // NOTE: window.CIV_ARC_LIVE intentionally unset → overlay disabled.
  ["civilizationOntology.js", "civilizationArcData.js", "civilizationArcLayout.js",
   "civilizationArcDraw.js", "civilizationProgressEvidence.js", "civilizationArcNav.js"].forEach((f) =>
    dom.window.eval(fs.readFileSync(path.join(root, "compile/assets", f), "utf8")));
  dom.window.document.dispatchEvent(new dom.window.Event("DOMContentLoaded"));
  await new Promise((r) => setTimeout(r, 0));
  const nav = dom.window.document.querySelector(".civilization-arc-nav");
  assert.strictEqual(fetched, false, "no inflight.json fetch when the overlay is not enabled");
  assert(!nav.querySelector(".arc-live-chip"), "no live chip when the overlay is disabled");
  assert(nav.querySelectorAll(".arc-item-group").length > 0, "the baked arc still renders on its own");
});

const LIVE_PR = {
  generated: "2026-06-17 14:00", window_days: 30, repos: ["hive"], errors: [],
  items: [{ id: "pr-hive-1", code: "hive#1", type: "work", label: "fix: live overlay",
    status: "active", blocked: false, provenance: "derived", repo: ["hive"],
    sprint: "stewardship", href: "https://github.com/transpara-ai/hive/pull/1",
    author: "msaucier", note: "open · @msaucier" }],
};

test('live overlay: stubbed fetch adds the PR marker and a freshness chip', async () => {
  const dom = mountWithFetch(LIVE_PR);
  await new Promise((r) => setTimeout(r, 0));
  const nav = dom.window.document.querySelector(".civilization-arc-nav");
  assert(nav.querySelector('[data-arc-item="pr-hive-1"]'), "live PR marker should render after overlay");
  const chip = nav.querySelector(".arc-live-chip");
  assert(chip && /updated 2026-06-17 14:00/.test(chip.textContent), "chip should show generated time");
});

test('live overlay: the live marker is interactive and shows its author', async () => {
  const dom = mountWithFetch(LIVE_PR);
  await new Promise((r) => setTimeout(r, 0));
  const nav = dom.window.document.querySelector(".civilization-arc-nav");
  const marker = nav.querySelector('[data-arc-item="pr-hive-1"]');
  marker.dispatchEvent(new dom.window.MouseEvent('mouseover', { bubbles: true }));
  const tip = nav.querySelector('.arc-tooltip');
  assert.strictEqual(tip.hidden, false);
  assert.match(tip.textContent, /actor · @msaucier/);
});

test('live overlay FAILS SAFE: a rejected fetch keeps the baked render, no live marker', async () => {
  const dom = mountWithFetch(null, { reject: true });
  await new Promise((r) => setTimeout(r, 0));
  const nav = dom.window.document.querySelector(".civilization-arc-nav");
  assert(!nav.querySelector('[data-arc-item="pr-hive-1"]'), "no live marker on fetch failure");
  assert(nav.querySelectorAll(".arc-item-group").length > 0, "baked render survives");
});

test('live overlay FAILS SAFE on invalid live data: merge rejected → baked kept + chip warns', async () => {
  // Valid fetch, but a live item with an invalid status → mergeInflight returns ok:false.
  const BAD = { generated: "g", window_days: 30, repos: ["hive"], errors: [],
    items: [{ id: "pr-bad-1", code: "bad#1", type: "work", label: "x", status: "merged", // ∉ STATUS_ORDER
      blocked: false, provenance: "derived", repo: ["hive"], sprint: "stewardship", author: "x", note: "x" }] };
  const dom = mountWithFetch(BAD);
  await new Promise((r) => setTimeout(r, 0));
  const nav = dom.window.document.querySelector(".civilization-arc-nav");
  assert(!nav.querySelector('[data-arc-item="pr-bad-1"]'), "invalid live item must not render");
  assert(nav.querySelectorAll(".arc-item-group").length > 0, "baked render survives");
  const chip = nav.querySelector(".arc-live-chip");
  assert(chip && /unavailable/.test(chip.textContent), "chip warns unavailable on rejected merge");
});

test('live overlay FAILS CLOSED on a degraded refresh: errors present → chip warns "stale", never "updated"', async () => {
  // inflight.py still writes a payload when a gh/network/auth call fails: errors[] is set
  // and items may be empty. mergeInflight treats empty items as ok, so without this guard
  // the chip would stamp a green "live · updated" on a failed refresh — hiding missing
  // live PRs while claiming the view is current. A degraded refresh must warn, not lie.
  const DEGRADED = { generated: "2026-06-17 14:00", window_days: 30, repos: ["hive"],
    errors: ["hive open: RuntimeError"], items: [] };
  const dom = mountWithFetch(DEGRADED);
  await new Promise((r) => setTimeout(r, 0));
  const nav = dom.window.document.querySelector(".civilization-arc-nav");
  const chip = nav.querySelector(".arc-live-chip");
  assert(chip, "a chip must render on a degraded refresh");
  assert.doesNotMatch(chip.textContent, /updated/, "a failed refresh must NOT claim 'live · updated'");
  assert.match(chip.textContent, /stale|source error/, "chip must signal the degraded refresh");
  assert(chip.classList.contains("arc-live-chip-warn"), "degraded chip must use the warn style");
  assert(nav.querySelectorAll(".arc-item-group").length > 0, "baked render survives a degraded refresh");
});

test('Gate K renders as cleared-by-waiver (done) with go-live residual surfaced and evidence links', () => {
  const { nav, svg, dom } = mountArc();
  const gate = svg.querySelector('[data-arc-item="gate-k"]');
  assert(gate, "gate-k marker missing");
  assert(gate.classList.contains("arc-status-done"), "gate-k must render done (pre-go-live waiver, docs#138)");
  assert(!gate.classList.contains("arc-blocked"), "gate-k is no longer blocked after the pre-go-live waiver");

  gate.dispatchEvent(new dom.window.MouseEvent('mouseover', { bubbles: true }));
  const tip = nav.querySelector('.arc-tooltip');
  assert.match(tip.textContent, /gate · done/i);

  gate.dispatchEvent(new dom.window.MouseEvent('click', { bubbles: true }));
  const detail = nav.querySelector('.arc-detail-panel');
  assert.match(detail.textContent, /Done/);
  // The waiver closed Gate K, but the go-live revalidation residual must still be surfaced.
  assert.match(detail.textContent, /go-live/i);
  assert.match(detail.textContent, /boundary/i);
  assert.match(detail.textContent, /pre live closed go live blocked/i);
  assert.match(detail.textContent, /go-live revalidation blocked/i);
  assert.match(detail.textContent, /private merge evidence was rechecked/i);
  assert.doesNotMatch(detail.textContent, /\b[0-9a-f]{40}\b/i);
  const evidenceHrefs = [...detail.querySelectorAll('.arc-detail-evidence-link')]
    .map((a) => a.getAttribute("href"));
  assert(evidenceHrefs.includes("gate-k.html"));
  assert(!evidenceHrefs.some((href) => href && href.includes("github.com/transpara-ai/docs")),
    "Gate K detail must not link private docs repo evidence");
});

test('operation progress evidence snapshot renders under the arc', () => {
  const { nav } = mountArc();
  const panel = nav.querySelector('.arc-progress-panel');
  assert(panel, 'progress evidence panel missing');
  assert.match(panel.textContent, /Progress evidence snapshot/);
  assert.match(panel.textContent, /snapshot2026-06-21T00:00:00Z/);
  assert.match(panel.textContent, /Test 001 Remains YELLOW/);
  assert.match(panel.textContent, /Omitted sources/);
  assert.match(panel.textContent, /not live truth/i);
  assert.doesNotMatch(panel.textContent, /operator_notes|raw_issue_body|Source notes are intentionally not exported|Raw issue text is not exported/);

  const hrefs = [...panel.querySelectorAll('a')].map((a) => a.getAttribute('href'));
  assert(hrefs.includes('https://github.com/transpara-ai/civilization-operation/pull/28'));
  assert(hrefs.includes('https://github.com/transpara-ai/civilization-operation/issues/26'));
  assert(!hrefs.some((href) => href && href.includes('github.com/transpara-ai/docs')),
    'progress panel must not link private docs repo evidence');
  assert.doesNotMatch(panel.textContent, /transpara-ai\/docs|docs#[0-9]+/i);
});

test('operation progress evidence fails closed without explicit public-safe metadata', () => {
  [
    ["public_safe false", (win) => { win.CIVILIZATION_PROGRESS_EVIDENCE.privacy.public_safe = false; }],
    ["missing privacy", (win) => { delete win.CIVILIZATION_PROGRESS_EVIDENCE.privacy; }],
    ["schema mismatch", (win) => { win.CIVILIZATION_PROGRESS_EVIDENCE.schema_version = 2; }],
  ].forEach(([label, beforeNav]) => {
    const { nav } = mountArc({ beforeNav });
    const panel = nav.querySelector('.arc-progress-panel');
    assert(panel, `progress evidence panel missing for ${label}`);
    assert.match(panel.textContent, /No public-safe progress evidence export is available/);
    assert.strictEqual(panel.querySelectorAll('.arc-progress-item').length, 0, label);
    assert.doesNotMatch(panel.textContent, /Test 001 Remains YELLOW/);
  });
});

test('operation progress evidence rejects unsafe progress links', () => {
  const { nav } = mountArc({
    beforeNav(win) {
      win.CIVILIZATION_PROGRESS_EVIDENCE_SOURCE.operation_pr_url = 'data:text/html,unsafe';
      win.CIVILIZATION_PROGRESS_EVIDENCE.items[0].source_url = 'javascript:alert(1)';
    },
  });
  const panel = nav.querySelector('.arc-progress-panel');
  assert(panel, 'progress evidence panel missing');
  const hrefs = [...panel.querySelectorAll('a')].map((a) => a.getAttribute('href'));
  assert(!hrefs.some((href) => href && /^(javascript:|data:|\/\/)/i.test(href)), 'unsafe progress href rendered');
  assert.match(panel.textContent, /transpara-ai\/civilization-operation#28/);
  assert.match(panel.textContent, /governing authority on file/);
});

test('operation progress evidence asset omits private governing-repo identifiers', () => {
  const asset = fs.readFileSync(path.join(root, "compile/assets/civilizationProgressEvidence.js"), "utf8");
  assert.doesNotMatch(asset, /github\.com\/transpara-ai\/docs|transpara-ai\/docs|docs#[0-9]+/i);
  assert.strictEqual(loadProgressEvidence().schema_version, 1);
});

test('selecting an item draws dashed dependency lines (both directions) + lists deps', () => {
  const { nav, svg, dom } = mountArc();
  const marker = svg.querySelector('[data-arc-item="civic-ai"]');
  assert(marker, "civic-ai marker missing");
  marker.dispatchEvent(new dom.window.MouseEvent('click', { bubbles: true }));
  assert(svg.querySelectorAll('.arc-dep-line').length > 0, "dependency lines must render on selection");
  assert(svg.querySelector('.arc-dep-precedent'), "a precedent (upstream) line must render");
  assert(svg.querySelector('.arc-dep-antecedent'), "an antecedent (downstream) line must render");
  const detail = nav.querySelector('.arc-detail-panel');
  assert.match(detail.textContent, /depends on/i);
  assert.match(detail.textContent, /depended on by/i);
  // Background click clears the selection and removes the lines.
  svg.dispatchEvent(new dom.window.MouseEvent('click', { bubbles: true }));
  assert.strictEqual(svg.querySelectorAll('.arc-dep-line').length, 0, "lines clear on deselect");
});

test('drawDeps anchors a line to EVERY placement of a duplicated multi-lane item (repo view)', () => {
  const D = require('../compile/assets/civilizationArcDraw.js');
  const doc = new JSDOM('<!doctype html>').window.document;
  const svg = doc.createElementNS('http://www.w3.org/2000/svg', 'svg');
  // Item X is rendered in TWO lanes (y=10 and y=50); item Y once (y=30). X depends on Y.
  const layout = { tracks: [
    { rows: [{ items: [{ item: { id: 'X' }, x: 100, y: 10 }, { item: { id: 'Y' }, x: 60, y: 30 }] }] },
    { rows: [{ items: [{ item: { id: 'X' }, x: 100, y: 50 }] }] },
  ] };
  D.drawDeps(svg, layout, [{ from: 'Y', to: 'X' }], 'X');
  const lines = [...svg.querySelectorAll('.arc-dep-line')];
  const ys = new Set(lines.flatMap(l => [Number(l.getAttribute('y1')), Number(l.getAttribute('y2'))]));
  assert.ok(ys.has(10) && ys.has(50),
    'a dep line must reach BOTH copies of X (y=10 and y=50), not just the last; got ' + [...ys].join(','));
});

test('now-panel surfaces the Gate-K go-live hard stop even though the gate is no longer blocked', () => {
  const { nav } = mountArc();
  const np = nav.querySelector('.arc-now-panel').textContent;
  assert.match(np, /Gate-K/, 'the go-live hard-stop gate is surfaced in the focus panel');
  assert.match(np, /go-live/i, 'the go-live revalidation residual is named, not hidden behind a click');
  assert.match(np, /2026-06-17/, 'the focus gate (Gate-K) date is shown in the now-panel, not just on hover');
});

test('standalone wheel: dominant-horizontal pans the frame (not hijacked into zoom); vertical zooms', () => {
  const dom = new JSDOM('<!doctype html><div data-civilization-arc-nav data-arc-standalone="true"></div>', {
    pretendToBeVisual: true, runScripts: "outside-only", url: "http://127.0.0.1:8787/civilization-arc.html",
  });
  ["civilizationOntology.js", "civilizationArcData.js", "civilizationArcLayout.js",
   "civilizationArcDraw.js", "civilizationArcNav.js"].forEach((f) =>
    dom.window.eval(fs.readFileSync(path.join(root, "compile/assets", f), "utf8")));
  dom.window.document.dispatchEvent(new dom.window.Event("DOMContentLoaded"));
  const svg = dom.window.document.querySelector(".civilization-arc-nav svg.arc-svg");
  // A dominant-horizontal trackpad gesture must fall through to scroll the frame, not zoom.
  const hEvt = new dom.window.WheelEvent('wheel', { deltaX: 140, deltaY: 0, bubbles: true, cancelable: true });
  svg.dispatchEvent(hEvt);
  assert.strictEqual(hEvt.defaultPrevented, false, 'dominant-horizontal wheel must pan the frame, not be hijacked into zoom');
  // At Fit, a zoom-out gesture cannot change zoom and must fall through so the page can scroll.
  const lowerBoundEvt = new dom.window.WheelEvent('wheel', { deltaX: 0, deltaY: 140, bubbles: true, cancelable: true });
  svg.dispatchEvent(lowerBoundEvt);
  assert.strictEqual(lowerBoundEvt.defaultPrevented, false, 'wheel down at Fit must scroll the page, not be swallowed');
  // A vertical wheel is still treated as zoom (prevents the page from scrolling).
  const vEvt = new dom.window.WheelEvent('wheel', { deltaX: 0, deltaY: -140, bubbles: true, cancelable: true });
  svg.dispatchEvent(vEvt);
  assert.strictEqual(vEvt.defaultPrevented, true, 'vertical wheel is treated as zoom');
});

test('a backfilled date shows in the tooltip + a STRUCTURED detail-panel date line (with ref)', () => {
  const { nav, svg, dom } = mountArc();
  const gate = svg.querySelector('[data-arc-item="gate-k"]');
  assert(gate, 'gate-k marker missing');
  gate.dispatchEvent(new dom.window.MouseEvent('mouseover', { bubbles: true }));
  assert.match(nav.querySelector('.arc-tooltip').textContent, /date · 2026-06-17/, 'tooltip shows the date');
  gate.dispatchEvent(new dom.window.MouseEvent('click', { bubbles: true }));
  // Target the dedicated date element, NOT the panel text (gate-k's prose note also
  // happens to mention the date/ref — a prose match would be a false positive).
  const dateLine = nav.querySelector('.arc-detail-date');
  assert(dateLine, 'detail panel must have a structured .arc-detail-date line');
  assert.match(dateLine.textContent, /date\b/, 'date line is labelled');
  assert.match(dateLine.textContent, /2026-06-17/, 'date line shows the ISO date');
  assert.match(dateLine.textContent, /docs#138/, 'date line carries the provenance ref');
});

test('an undated item shows NO date line in tooltip or detail — graceful absence', () => {
  const { nav, svg, dom } = mountArc();
  // origin-signal is a reconstructed beat with no date; its detail must not fabricate one.
  const m = svg.querySelector('[data-arc-item="origin-signal"]');
  m.dispatchEvent(new dom.window.MouseEvent('mouseover', { bubbles: true }));
  assert.doesNotMatch(nav.querySelector('.arc-tooltip').textContent, /date ·/, 'no tooltip date for an undated item');
  m.dispatchEvent(new dom.window.MouseEvent('click', { bubbles: true }));
  assert.strictEqual(nav.querySelector('.arc-detail-date'), null, 'no detail date line for an undated item');
});

test('Actor toggle is disabled when no item carries an author (live overlay parked)', () => {
  const { nav } = mountArc();
  const actor = nav.querySelector('[data-arc-group="actor"]');
  assert(actor, "actor button present");
  assert.strictEqual(actor.disabled, true, "actor button must be disabled with no actor data");
  assert(actor.classList.contains('arc-group-btn-disabled'), "disabled class applied");
});

const data = loadArcData();
assertData(data);
assertRenderedDom();

console.log(
  `arc DOM smoke ok: ${data.items.length} items, now=${O.deriveNow(data.items)}, ` +
    `${O.groupBy(data.items, "status").length} status lanes`
);
