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
  const dom = new JSDOM('<!doctype html><div data-civilization-arc-nav></div>', {
    pretendToBeVisual: true, runScripts: "outside-only", url: "http://127.0.0.1:8787/index.html",
  });
  // Load order matters: ontology → data → layout → draw → nav.
  // render() bails without CivArcLayout + CivArcDraw, so all five must load.
  ["civilizationOntology.js", "civilizationArcData.js", "civilizationArcLayout.js",
   "civilizationArcDraw.js", "civilizationArcNav.js"].forEach((f) =>
    dom.window.eval(fs.readFileSync(path.join(root, "compile/assets", f), "utf8")));
  dom.window.document.dispatchEvent(new dom.window.Event("DOMContentLoaded"));

  const nav = dom.window.document.querySelector(".civilization-arc-nav");
  assert(nav, "arc nav did not mount");
  assert(nav.querySelector("svg.arc-svg"), "SVG not rendered");
  assert.strictEqual(nav.querySelectorAll(".arc-track-band").length, 3, "expected 3 track bands");
  assert.strictEqual(nav.querySelectorAll(".arc-track-label").length, 3, "expected 3 track labels");
  assert(nav.querySelectorAll(".arc-subrow-label").length >= 4, "expected >=4 gate-family sub-row labels");
  assert(nav.querySelectorAll(".arc-item-group").length > 0, "no item node groups produced");
  assert(nav.querySelectorAll(".arc-marker").length > 0, "no item shapes produced");
  assert(nav.querySelector(".arc-now-line"), "now-line element missing");
}

const data = loadArcData();
assertData(data);
assertRenderedDom();

console.log(
  `arc DOM smoke ok: ${data.items.length} items, now=${O.deriveNow(data.items)}, ` +
    `${O.groupBy(data.items, "status").length} status lanes`
);
