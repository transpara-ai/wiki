const fs = require("fs");
const path = require("path");
const vm = require("vm");
const assert = require("assert");
const { JSDOM } = require("jsdom");

const root = path.resolve(__dirname, "..");

function loadArcData() {
  const context = { window: {} };
  vm.createContext(context);
  vm.runInContext(
    fs.readFileSync(path.join(root, "compile/assets/civilizationArcData.js"), "utf8"),
    context
  );
  return context.window.CIVILIZATION_ARC_DATA;
}

function assertData(data) {
  for (const key of [
    "phases",
    "markers",
    "dependencies",
    "gates",
    "risks",
    "decisions",
    "criticalPath",
    "legendItems",
    "swimlanes",
    "summaryRail",
  ]) {
    assert(Array.isArray(data[key]) && data[key].length > 0, `${key} missing or empty`);
  }

  assert.strictEqual(data.phases.length, 15, "expected 15 major phases");
  assert(data.executionPlan, "execution plan missing");
  assert(/^\d{4}-\d{2}-\d{2}$/.test(data.executionPlan.updated), "execution plan date must be ISO");
  assert(data.executionPlan.endGoal.includes("steady-state Transpara-AI civilization"));
  assert(
    Array.isArray(data.executionPlan.summary) && data.executionPlan.summary.length >= 4,
    "execution plan summary missing or too small"
  );
  assert(
    Array.isArray(data.executionPlan.nearTerm) && data.executionPlan.nearTerm.length >= 6,
    "near-term execution plan missing or too small"
  );
  assert(
    Array.isArray(data.executionPlan.complete) && data.executionPlan.complete.length >= 10,
    "complete execution plan missing or too small"
  );
  assert.strictEqual(data.executionPlan.nearTerm[0].order, "N1");
  assert.strictEqual(data.executionPlan.complete[0].order, "C1");

  const currentX = data.currentFocus && data.currentFocus.x;
  const stalePastStatuses = new Set(["conceptual", "designed", "unresolved", "future"]);
  const stalePastPhases = data.phases.filter(
    (phase) => phase.end <= currentX && stalePastStatuses.has(phase.status)
  );
  assert.strictEqual(
    stalePastPhases.length,
    0,
    `past phases cannot remain conceptual/designed/unresolved/future: ${stalePastPhases
      .map((phase) => `${phase.id}:${phase.status}`)
      .join(", ")}`
  );

  const phaseStatusById = new Map(data.phases.map((phase) => [phase.id, phase.status]));
  assert.strictEqual(phaseStatusById.get("primitive-basis"), "canonical");
  assert.strictEqual(phaseStatusById.get("civic-philosophy"), "canonical");
  assert.strictEqual(phaseStatusById.get("memory-context"), "canonical");
  assert.strictEqual(phaseStatusById.get("prompt-rituals"), "active");
  assert.strictEqual(phaseStatusById.get("deployment"), "planned");

  const markers = new Set(data.markers.map((marker) => marker.id));
  for (const markerId of data.criticalPath) {
    assert(markers.has(markerId), `critical path references missing marker ${markerId}`);
  }
  for (const dependency of data.dependencies) {
    assert(markers.has(dependency.from), `dependency references missing source ${dependency.from}`);
    assert(markers.has(dependency.to), `dependency references missing target ${dependency.to}`);
  }
  for (const markerId of data.summaryRail) {
    assert(markers.has(markerId), `summary rail references missing marker ${markerId}`);
  }

  const hrefs = new Set();
  for (const collection of [
    data.phases,
    data.markers,
    data.gates,
    data.risks,
    data.decisions,
    [data.currentFocus],
  ]) {
    for (const item of collection) {
      if (item && item.href) hrefs.add(item.href);
    }
  }

  for (const href of hrefs) {
    assert(fs.existsSync(path.join(root, "dist", href)), `linked page missing from dist: ${href}`);
  }
}

function assertRenderedDom() {
  const dom = new JSDOM('<!doctype html><div data-civilization-arc-nav></div>', {
    pretendToBeVisual: true,
    runScripts: "outside-only",
    url: "http://127.0.0.1:8787/index.html",
  });

  dom.window.eval(fs.readFileSync(path.join(root, "compile/assets/civilizationArcData.js"), "utf8"));
  dom.window.eval(fs.readFileSync(path.join(root, "compile/assets/civilizationArcNav.js"), "utf8"));
  dom.window.document.dispatchEvent(new dom.window.Event("DOMContentLoaded"));

  const nav = dom.window.document.querySelector(".civilization-arc-nav");
  assert(nav, "arc nav did not mount");
  assert.strictEqual(nav.getAttribute("data-expanded"), "false", "default nav should be compact");
  assert(nav.querySelector("svg.arc-svg"), "SVG not rendered");
  assert(nav.querySelectorAll(".arc-phase-group").length >= 15, "phase groups missing");
  assert(nav.querySelectorAll(".arc-compact-rail-item").length > 8, "compact summary rail missing");
  assert(nav.textContent.includes("Open Full"), "full-tab control missing");
  assert(nav.textContent.includes("Fit full arc"), "fit control missing");
  assert(nav.textContent.includes("Zoom in"), "zoom-in control missing");
  assert(nav.textContent.includes("Zoom out"), "zoom-out control missing");
  assert(nav.textContent.includes("Export SVG"), "export control missing");
  assert(nav.textContent.includes("Civilization execution worklist"), "execution worklist missing");
  assert(nav.querySelectorAll(".arc-plan-table").length >= 2, "execution plan tables missing");
  assert(nav.querySelector("[data-arc-phase-select]"), "phase selector missing");
  assert(nav.querySelector("[data-arc-deps-toggle]"), "dependency toggle missing");
  assert(nav.querySelector("[data-arc-labels-toggle]"), "dense-label toggle missing");
  assert(nav.querySelector("[data-arc-close-details]"), "details close control missing");
  assert(nav.textContent.includes("Click an item for drill-down details"), "drill-down instruction missing");
}

const data = loadArcData();
assertData(data);
assertRenderedDom();

console.log(
  `arc DOM smoke ok: ${data.phases.length} phases, ${data.markers.length} markers, ${data.swimlanes.length} swimlanes`
);
