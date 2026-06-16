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

  // Derived "now" must be a finite, positive frontier.
  const now = O.deriveNow(data.items);
  assert(Number.isFinite(now), `deriveNow must be finite, got ${now}`);
  assert(now > 0, `deriveNow must be > 0, got ${now}`);

  // executionPlan is still present and consumed by the plan board.
  assert(data.executionPlan, "execution plan missing");
  assert(/^\d{4}-\d{2}-\d{2}$/.test(data.executionPlan.updated), "execution plan date must be ISO");
}

// Parse the drawn horizontal extent + sub-row y of one item-group's primary
// shape (rect | circle | gate diamond path), deterministically from attributes.
// Returns { cx, halfW, y } in viewBox units, or null if no shape is found.
function shapeExtent(group) {
  const rect = group.querySelector("rect.arc-item");
  if (rect) {
    const x = parseFloat(rect.getAttribute("x"));
    const w = parseFloat(rect.getAttribute("width"));
    const y = parseFloat(rect.getAttribute("y"));
    const h = parseFloat(rect.getAttribute("height"));
    return { cx: x + w / 2, halfW: w / 2, y: y + h / 2 };
  }
  const circle = group.querySelector("circle.arc-item");
  if (circle) {
    return {
      cx: parseFloat(circle.getAttribute("cx")),
      halfW: parseFloat(circle.getAttribute("r")),
      y: parseFloat(circle.getAttribute("cy")),
    };
  }
  const path = group.querySelector("path.arc-item");
  if (path) {
    const nums = (path.getAttribute("d") || "").match(/-?\d+(?:\.\d+)?/g);
    if (nums && nums.length >= 4) {
      const xs = [];
      const ys = [];
      for (let i = 0; i + 1 < nums.length; i += 2) {
        xs.push(parseFloat(nums[i]));
        ys.push(parseFloat(nums[i + 1]));
      }
      const minX = Math.min(...xs);
      const maxX = Math.max(...xs);
      const minY = Math.min(...ys);
      const maxY = Math.max(...ys);
      return { cx: (minX + maxX) / 2, halfW: (maxX - minX) / 2, y: (minY + maxY) / 2 };
    }
  }
  return null;
}

// ── Within-lane sub-row packing (collision avoidance) + lane-label gutter ──
// Asserts the core invariant Michael asked for: nodes never overlap, because
// each lane stacks its items into as many sub-rows as needed; and lane labels
// live in the left gutter, left of the plot area, not overlapping the nodes.
function assertPackingAndGutter(dom, nav) {
  const svg = nav.querySelector("svg.arc-svg");
  assert(svg, "SVG missing for packing assertions");

  // The viewBox height grows to fit the (variable-height) lane stack. Capture it
  // so we can assert packing made the chart taller than a single-row baseline.
  const vb = (svg.getAttribute("viewBox") || "").split(/\s+/).map(Number);
  assert.strictEqual(vb.length, 4, `viewBox must be 4 numbers, got '${svg.getAttribute("viewBox")}'`);
  const contentHeight = vb[3];
  assert(contentHeight > 0, `viewBox height must be positive, got ${contentHeight}`);

  const groups = Array.prototype.slice.call(nav.querySelectorAll(".arc-item-group"));
  const recs = groups.map((g) => shapeExtent(g)).filter(Boolean);
  assert(recs.length > 0, "no item shapes parsed for packing check");

  // Group items by their sub-row (quantised y) and assert NO two items on the
  // same sub-row have overlapping horizontal extents — the no-overlap invariant.
  const rows = new Map();
  recs.forEach((r) => {
    const key = r.y.toFixed(1);
    if (!rows.has(key)) rows.set(key, []);
    rows.get(key).push(r);
  });
  let lanesPacked = 0; // sub-rows holding more than one node
  rows.forEach((arr, key) => {
    if (arr.length > 1) lanesPacked += 1;
    const sorted = arr.slice().sort((a, b) => a.cx - b.cx);
    for (let i = 1; i < sorted.length; i++) {
      const prev = sorted[i - 1];
      const cur = sorted[i];
      const gap = cur.cx - cur.halfW - (prev.cx + prev.halfW);
      assert(
        gap >= -0.5,
        `sub-row y=${key}: nodes overlap (right edge ${(prev.cx + prev.halfW).toFixed(1)} > left edge ${(cur.cx - cur.halfW).toFixed(1)})`
      );
    }
  });

  // Packing actually occurred: the dense default (status) data forces ≥1 lane to
  // use multiple sub-rows, and the chart is taller than a flat single-row layout.
  const distinctSubRows = rows.size;
  assert(
    distinctSubRows > nav.querySelectorAll(".arc-swimlane").length,
    `expected more sub-rows (${distinctSubRows}) than lanes (${nav.querySelectorAll(".arc-swimlane").length}) — packing should split a dense lane`
  );
  assert(
    contentHeight > 420,
    `viewBox height should grow past the single-row baseline once packed, got ${contentHeight}`
  );

  // ── Lane-label gutter: a label per lane, all left of the plot's left edge ──
  // The plot's left edge is the min x among item-node centers minus their width;
  // every gutter label's x must be strictly left of every node's left extent.
  const labels = Array.prototype.slice.call(nav.querySelectorAll(".arc-swimlane-label"));
  const laneCount = nav.querySelectorAll(".arc-swimlane").length;
  assert.strictEqual(
    labels.length,
    laneCount,
    `expected one lane label per lane (${laneCount}), got ${labels.length}`
  );
  const plotLeftEdge = Math.min.apply(null, recs.map((r) => r.cx - r.halfW));
  labels.forEach((label) => {
    const lx = parseFloat(label.getAttribute("x"));
    assert(Number.isFinite(lx), "lane label missing numeric x");
    assert(
      lx < plotLeftEdge,
      `lane label x=${lx} must be left of the plot's left edge ${plotLeftEdge.toFixed(1)} (labels live in the gutter)`
    );
    // Each label is anchored to the right (so it hugs the gutter's inner edge)
    // and carries a <title> with the full, untruncated lane name for hover.
    assert.strictEqual(
      label.getAttribute("text-anchor"),
      "end",
      "lane label should be right-anchored in the gutter"
    );
    assert(label.querySelector("title"), "lane label should carry a <title> tooltip with the full name");
  });
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

  // ── Within-lane sub-row packing + lane-label gutter (run on the clean default
  // render, before any selection/zoom below mutates the layout). ──
  assertPackingAndGutter(dom, nav);

  const data = dom.window.CIVILIZATION_ARC_DATA;

  // ── Code labels: the DEFAULT render (denseLabels false) shows node codes ──
  // At least one node's visible text must equal a known short code. "Gate-K"
  // is deterministic: gate-k is the active/blocked frontier item, always drawn.
  const labelTexts = Array.prototype.slice
    .call(nav.querySelectorAll(".arc-item-label"))
    .map((el) => (el.textContent || "").trim());
  const knownCodes = ["N5", "HIVE", "Gate-K"];
  assert(
    knownCodes.some((c) => labelTexts.includes(c)),
    `default view should render at least one node code (looked for ${knownCodes.join(", ")}); saw: ${labelTexts.join(" | ")}`
  );
  assert(
    labelTexts.includes("Gate-K"),
    `expected a node labelled with the code 'Gate-K' in the default view; saw: ${labelTexts.join(" | ")}`
  );

  // ── Code KEY: a visible key maps codes → names in the default view ──
  const codeKey = nav.querySelector("[data-arc-code-key]");
  assert(codeKey, "code key element missing");
  const keyText = codeKey.textContent || "";
  // The N5 worklist code and its label, plus the Gate-K code, must be in the key.
  const n5 = data.items.find((it) => it.id === "n5");
  assert(n5 && n5.code === "N5", "fixture: n5 should carry code N5");
  assert(keyText.includes("N5"), "code key must include the 'N5' code");
  assert(
    keyText.includes(n5.label.slice(0, 24)),
    "code key must include the N5 worklist label"
  );
  assert(keyText.includes("Gate-K"), "code key must include the 'Gate-K' code");

  // Blocker overlay: the data has at least one blocked item, so an overlay must render.
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

  // ── T8: swimlane grouping toggle present ──
  assert(nav.querySelector("[data-arc-grouping]"), "grouping control missing");

  // ── T9: dependency edges are selection-scoped ──
  // Global deps-toggle was removed; no dependencies render until an item is selected.
  assert(!nav.querySelector("[data-arc-deps-toggle]"), "deps toggle should be removed");
  assert.strictEqual(
    nav.querySelectorAll(".arc-dependency").length,
    0,
    "no dependency edges should render without a selection"
  );

  // Pick a deterministic item that HAS dependencies, and confirm the contract
  // agrees the ontology would surface ≥1 edge for it.
  const withDeps = data.items.find((it) => Array.isArray(it.deps) && it.deps.length > 0);
  assert(withDeps, "expected at least one item with non-empty deps in the fixture");
  assert(
    O.visibleDeps(data.items, withDeps.id).length >= 1,
    "visibleDeps must return >=1 edge for an item with deps"
  );

  // Drive the SAME selection mechanism the click handler uses: each item node
  // is an [data-arc-item] element labelled by itemTitle(item). Find it by its
  // accessible name and dispatch a click, then assert its edges appear.
  const itemTitle = withDeps.label || withDeps.title || withDeps.code || withDeps.id;
  const nodes = Array.prototype.slice.call(nav.querySelectorAll("[data-arc-item]"));
  const node = nodes.find((el) => el.getAttribute("aria-label") === itemTitle);
  assert(node, `could not find rendered node for item '${withDeps.id}'`);
  node.dispatchEvent(
    new dom.window.MouseEvent("click", { bubbles: true, clientX: 24, clientY: 24 })
  );
  assert(
    nav.querySelectorAll(".arc-dependency").length >= 1,
    "selecting an item with deps must render at least one dependency edge"
  );
}

const data = loadArcData();
assertData(data);
assertRenderedDom();

console.log(
  `arc DOM smoke ok: ${data.items.length} items, now=${O.deriveNow(data.items)}, ` +
    `${O.groupBy(data.items, "status").length} status lanes`
);
