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

// ── Reusable mount helper — eval all five modules into a JSDOM window and
//    dispatch DOMContentLoaded. Returns { nav, svg, dom } for test assertions.
function mountArc() {
  const dom = new JSDOM('<!doctype html><div data-civilization-arc-nav></div>', {
    pretendToBeVisual: true, runScripts: "outside-only", url: "http://127.0.0.1:8787/index.html",
  });
  ["civilizationOntology.js", "civilizationArcData.js", "civilizationArcLayout.js",
   "civilizationArcDraw.js", "civilizationArcNav.js"].forEach((f) =>
    dom.window.eval(fs.readFileSync(path.join(root, "compile/assets", f), "utf8")));
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
  ["v3.9 milestones (A-J)", "Deployment register (G-0..G-8.4)", "v4.0 (K/L)"].forEach(
    (fam) => {
      assert(
        gateLanes.includes(fam),
        `grouping="gate" must include the '${fam}' lane; saw: ${gateLanes.join(" | ")}`
      );
    }
  );
  // GATE_FAMILIES ordering: the v3.9-milestones lane precedes the v4.0 lane.
  assert(
    gateLanes.indexOf("v3.9 milestones (A-J)") < gateLanes.indexOf("v4.0 (K/L)"),
    `gate lanes should follow GATE_FAMILIES order; saw: ${gateLanes.join(" | ")}`
  );

  // Derived "now" must be a finite, positive frontier.
  const now = O.deriveNow(data.items);
  assert(Number.isFinite(now), `deriveNow must be finite, got ${now}`);
  assert(now > 0, `deriveNow must be > 0, got ${now}`);

  // executionPlan is still present and consumed by the plan board.
  assert(data.executionPlan, "execution plan missing");
  assert(/^\d{4}-\d{2}-\d{2}$/.test(data.executionPlan.updated), "execution plan date must be ISO");
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
  assert.match(tip.textContent, /step \d+ of 109/);
  assert.match(tip.textContent, /sprint ·/);
});

// ── XSS hardening: javascript: hrefs must never be assigned to a rendered link ──
// Helper: mount a fresh JSDOM, inject custom hrefs onto items, fire DOMContentLoaded, return nav.
function mountWithInjectedHrefs(hrefMap) {
  const dom = new JSDOM('<!doctype html><div data-civilization-arc-nav></div>', {
    pretendToBeVisual: true, runScripts: "outside-only", url: "http://127.0.0.1:8787/index.html",
  });
  ["civilizationOntology.js", "civilizationArcData.js", "civilizationArcLayout.js",
   "civilizationArcDraw.js"].forEach((f) =>
    dom.window.eval(fs.readFileSync(path.join(root, "compile/assets", f), "utf8")));
  const items = dom.window.CIVILIZATION_ARC_DATA.items;
  Object.keys(hrefMap).forEach((k) => { items[Number(k)].href = hrefMap[k]; });
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
  });
  assert(nav, "nav did not mount");

  // Trigger malicious items: hover + click each so both tooltip and detail panel are exercised.
  [0, 1, 2].forEach((idx) => triggerItem(nav, items[idx], dom));

  // Assert: no <a> in the nav has any dangerous href (malicious items active in detail panel).
  const dangLinks = [...nav.querySelectorAll("a")].filter((a) => {
    const h = (a.getAttribute("href") || "");
    return /^javascript:/i.test(h) || /^[\\/]{2}/.test(h) || /^data:/i.test(h);
  });
  assert.strictEqual(
    dangLinks.length, 0,
    "Dangerous links found: " + dangLinks.map((a) => a.getAttribute("href")).join(", ")
  );

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

// --- live overlay (Task 6) ---
function mountWithFetch(inflightPayload, opts) {
  const dom = new JSDOM('<!doctype html><div data-civilization-arc-nav></div>', {
    pretendToBeVisual: true, runScripts: "outside-only", url: "http://127.0.0.1:8787/index.html",
  });
  dom.window.fetch = function () {
    if (opts && opts.reject) return Promise.reject(new Error("network"));
    return Promise.resolve({ ok: true, json: function () { return Promise.resolve(inflightPayload); } });
  };
  ["civilizationOntology.js", "civilizationArcData.js", "civilizationArcLayout.js",
   "civilizationArcDraw.js", "civilizationArcNav.js"].forEach((f) =>
    dom.window.eval(fs.readFileSync(path.join(root, "compile/assets", f), "utf8")));
  dom.window.document.dispatchEvent(new dom.window.Event("DOMContentLoaded"));
  return dom;
}

const LIVE_PR = {
  generated: "2026-06-17 14:00", window_days: 7, repos: ["hive"], errors: [],
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

const data = loadArcData();
assertData(data);
assertRenderedDom();

console.log(
  `arc DOM smoke ok: ${data.items.length} items, now=${O.deriveNow(data.items)}, ` +
    `${O.groupBy(data.items, "status").length} status lanes`
);
