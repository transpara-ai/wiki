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
    pretendToBeVisual: true,
    runScripts: "outside-only",
    url: "http://127.0.0.1:8787/index.html",
  });

  // Load ontology first (the renderer reads window.CivOntology), then data, then renderer.
  dom.window.eval(fs.readFileSync(path.join(root, "compile/assets/civilizationOntology.js"), "utf8"));
  dom.window.eval(fs.readFileSync(path.join(root, "compile/assets/civilizationArcData.js"), "utf8"));
  dom.window.eval(fs.readFileSync(path.join(root, "compile/assets/civilizationArcNav.js"), "utf8"));
  dom.window.document.dispatchEvent(new dom.window.Event("DOMContentLoaded"));

  const nav = dom.window.document.querySelector(".civilization-arc-nav");
  assert(nav, "arc nav did not mount");
  assert.strictEqual(nav.getAttribute("data-expanded"), "false", "default nav should be compact");
  assert(nav.querySelector("svg.arc-svg"), "SVG not rendered");

  // Lanes/groups: at least one swimlane band produced from groupBy.
  assert(nav.querySelectorAll(".arc-swimlane").length > 0, "no swimlane/group elements produced");

  // Item nodes: at least one item node drawn (do not require >= items.length).
  assert(nav.querySelectorAll(".arc-item-group").length > 0, "no item node elements produced");
  assert(nav.querySelectorAll(".arc-item").length > 0, "no item shapes produced");

  // Now-line exists.
  assert(nav.querySelector(".arc-current-line"), "now-line element missing");

  // Blocker overlay: the data has at least one blocked item, so an overlay must render.
  const data = dom.window.CIVILIZATION_ARC_DATA;
  if (data.items.some((it) => it.blocked)) {
    assert(nav.querySelector(".arc-item-blocked"), "blocked items present but no blocker overlay rendered");
  }

  // Preserved scaffolding controls + plan board (executionPlan still consumed).
  assert(nav.textContent.includes("Open Full"), "full-tab control missing");
  assert(nav.textContent.includes("Fit full arc"), "fit control missing");
  assert(nav.textContent.includes("Zoom in"), "zoom-in control missing");
  assert(nav.textContent.includes("Zoom out"), "zoom-out control missing");
  assert(nav.textContent.includes("Export SVG"), "export control missing");
  assert(nav.textContent.includes("Civilization execution worklist"), "execution worklist missing");
  assert(nav.querySelectorAll(".arc-plan-table").length >= 2, "execution plan tables missing");
  assert(nav.querySelector("[data-arc-phase-select]"), "sprint selector missing");
  assert(nav.querySelector("[data-arc-close-details]"), "details close control missing");
  assert(nav.textContent.includes("Click an item for drill-down details"), "drill-down instruction missing");
}

const data = loadArcData();
assertData(data);
assertRenderedDom();

console.log(
  `arc DOM smoke ok: ${data.items.length} items, now=${O.deriveNow(data.items)}, ` +
    `${O.groupBy(data.items, "status").length} status lanes`
);
