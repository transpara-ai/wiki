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
test('javascript: href is never assigned to any rendered link (XSS hardening)', () => {
  // Mount fresh DOM but patch the data before DOMContentLoaded fires.
  const dom = new JSDOM('<!doctype html><div data-civilization-arc-nav></div>', {
    pretendToBeVisual: true, runScripts: "outside-only", url: "http://127.0.0.1:8787/index.html",
  });
  // Eval all modules except the controller so we can poison data first.
  ["civilizationOntology.js", "civilizationArcData.js", "civilizationArcLayout.js",
   "civilizationArcDraw.js"].forEach((f) =>
    dom.window.eval(fs.readFileSync(path.join(root, "compile/assets", f), "utf8")));

  // Inject a malicious href on the first item and a safe http href on the second.
  const items = dom.window.CIVILIZATION_ARC_DATA.items;
  const maliciousItem = items[0];
  const safeItem = items[1];
  maliciousItem.href = "javascript:alert(1)";
  safeItem.href = "https://example.com/safe";

  // Now eval the controller — DOMContentLoaded will fire synchronously in jsdom
  // after the next dispatchEvent call.
  dom.window.eval(fs.readFileSync(path.join(root, "compile/assets/civilizationArcNav.js"), "utf8"));
  dom.window.document.dispatchEvent(new dom.window.Event("DOMContentLoaded"));

  const nav = dom.window.document.querySelector(".civilization-arc-nav");
  assert(nav, "nav did not mount");

  // Simulate a click on the malicious item's marker to open the detail panel.
  const maliciousId = String(maliciousItem.id);
  const maliciousMarker = nav.querySelector('[data-arc-item="' + maliciousId + '"]');
  if (maliciousMarker) {
    maliciousMarker.dispatchEvent(new dom.window.MouseEvent('mouseover', { bubbles: true }));
    maliciousMarker.dispatchEvent(new dom.window.MouseEvent('click', { bubbles: true }));
  }

  // Simulate hovering the safe item to trigger the tooltip link.
  const safeId = String(safeItem.id);
  const safeMarker = nav.querySelector('[data-arc-item="' + safeId + '"]');
  if (safeMarker) {
    safeMarker.dispatchEvent(new dom.window.MouseEvent('mouseover', { bubbles: true }));
  }

  // Assert: no <a> anywhere in the nav has a javascript: href.
  const allLinks = [...nav.querySelectorAll("a")];
  const xssLinks = allLinks.filter((a) => /^javascript:/i.test(a.getAttribute("href") || ""));
  assert.strictEqual(
    xssLinks.length,
    0,
    `Found ${xssLinks.length} link(s) with javascript: href: ${xssLinks.map((a) => a.getAttribute("href")).join(", ")}`
  );

  // Assert happy path: the safe http item still renders its link (in tooltip or detail panel).
  // Click the safe marker to ensure the detail panel link is rendered.
  if (safeMarker) {
    safeMarker.dispatchEvent(new dom.window.MouseEvent('click', { bubbles: true }));
  }
  const safeLinks = [...nav.querySelectorAll("a")].filter(
    (a) => (a.getAttribute("href") || "").startsWith("https://example.com/safe")
  );
  assert.ok(safeLinks.length >= 1, "Safe http href should still render a link");
});

const data = loadArcData();
assertData(data);
assertRenderedDom();

console.log(
  `arc DOM smoke ok: ${data.items.length} items, now=${O.deriveNow(data.items)}, ` +
    `${O.groupBy(data.items, "status").length} status lanes`
);
