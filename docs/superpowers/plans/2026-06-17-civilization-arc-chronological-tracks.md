# Civilization Arc — Chronological Tracks (renderer v2) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the Projection-1 arc renderer as an accuracy-first **chronological-tracks** view — x = development timeline, y = track/category (construction arc · gates by family · worklist) — replacing the failed swimlane/horizontal-flow renderer.

**Architecture:** Keep the validated data + ontology contract (`civilizationArcData.js`, `civilizationOntology.js`). Rebuild the renderer as three focused, no-build-step browser modules: `civilizationArcLayout.js` (pure geometry, Node-testable), `civilizationArcDraw.js` (pure DOM/SVG construction from a layout), and `civilizationArcNav.js` (thin controller: state, interaction, responsive, composition). Spec: `docs/superpowers/specs/2026-06-17-civilization-arc-chronological-tracks-design.md`. Visual reference: the approved `direction_c_full_composition` mockup.

**Tech Stack:** Vanilla ES5-style browser JS (IIFE globals, no bundler — matches existing assets), `node:test`/`node:assert` for unit tests, jsdom for the DOM smoke test, `compile/build_site.py` for the build, Playwright for the browser spec.

**Controller/subagent rule (carried from this session):** the **controller makes every git commit** via `git -C <worktree>`; subagents edit + test only. Worktree: `…/.claude/worktrees/elegant-swanson-965269` (branch `claude/elegant-swanson-965269`). No push/PR/merge.

---

## File Structure

- **Keep (validated contract — do not modify):** `compile/assets/civilizationArcData.js`, `compile/assets/civilizationOntology.js`, `tests/ontology.test.js`.
- **Create:** `compile/assets/civilizationArcLayout.js` — pure geometry: `scaleX`, `buildLayout` (tracks, gate family sub-rows, marker x/y, collapse-aware heights, now-x, era ticks). `window.CivArcLayout` + `module.exports`. No DOM.
- **Create:** `tests/arcLayout.test.js` — `node:test` unit tests for the pure module.
- **Create:** `compile/assets/civilizationArcDraw.js` — pure DOM/SVG construction from a layout: axis + now-line, track bands + gutter labels + chevrons, markers (beats/gates/worklist) by type+status. `window.CivArcDraw`. No event wiring/state.
- **Rewrite:** `compile/assets/civilizationArcNav.js` — thin controller: render state (collapsed, selectedId, viewBox), `render(root,data)`, interaction (hover/click/collapse/zoom/pan), responsive (ResizeObserver/resize), now/focus + detail panels, the `[data-civilization-arc-nav]` bootstrap.
- **Rewrite:** `tests/arc-dom-smoke.test.js` — jsdom render of the new tracks view (replaces the swimlane asserts).
- **Modify:** `compile/build_site.py` — `copy_asset` the two new scripts and inject them in order (`ontology → data → layout → draw → nav`).
- **Modify:** `.github/workflows/ci.yml` — Node step running the unit + DOM tests.
- **Update:** `tests/arc-nav.spec.js` — Playwright assertions to the tracks model (Task 10).

---

## Task 0: Clean base (controller prep, no commit)

The rejected experiment files (horizontal-flow + fit-to-width) are uncommitted on top of `80d29d4`. Discard them so the rebuild starts from the committed gate-landscape state.

- [ ] **Step 1: Discard the rejected renderer experiments**

```bash
W=…/worktrees/elegant-swanson-965269
git -C "$W" checkout -- compile/assets/civilizationArcNav.js compile/assets/style.css tests/arc-dom-smoke.test.js
```

- [ ] **Step 2: Verify clean base**

Run: `git -C "$W" status --short` → expect empty. `node --test "$W/tests/ontology.test.js"` → 18 pass. `python3 "$W/compile/build_site.py"` → builds.
Expected: clean tree at `80d29d4`, tests green, build OK.

---

## Task 1: `civilizationArcLayout.js` — pure geometry + tests

**Files:** Create `compile/assets/civilizationArcLayout.js`, `tests/arcLayout.test.js`.

- [ ] **Step 1: Write the failing tests**

```js
// tests/arcLayout.test.js
const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const L = require('../compile/assets/civilizationArcLayout.js');

function loadData() {
  const code = fs.readFileSync(path.join(__dirname, '../compile/assets/civilizationArcData.js'), 'utf8');
  const w = {}; new Function('window', code)(w); return w.CIVILIZATION_ARC_DATA;
}

test('scaleX maps domain endpoints to the plot edges', () => {
  const sx = L.scaleX({ start: 0, end: 15 }, 100, 1000);
  assert.strictEqual(sx(0), 100);
  assert.strictEqual(sx(15), 1000);
});

test('buildLayout yields 3 tracks; gates expands into 4 family rows', () => {
  const lay = L.buildLayout(loadData(), { width: 1600 });
  assert.deepStrictEqual(lay.tracks.map(t => t.id), ['construction', 'gates', 'worklist']);
  assert.strictEqual(lay.tracks.find(t => t.id === 'gates').rows.length, 4);
});

test('every gate lands in exactly one family row (none dropped)', () => {
  const data = loadData();
  const lay = L.buildLayout(data, { width: 1600 });
  const placed = lay.tracks.find(t => t.id === 'gates').rows.reduce((n, r) => n + r.items.length, 0);
  assert.strictEqual(placed, data.items.filter(i => i.type === 'gate').length);
});

test('nowX === scaleX(deriveNow); frontier is 13.9', () => {
  const lay = L.buildLayout(loadData(), { width: 1600 });
  assert.ok(Math.abs(lay.nowSeq - 13.9) < 1e-9);
  assert.strictEqual(lay.nowX, lay.scaleX(lay.nowSeq));
});

test('collapsing the gates track reduces contentHeight', () => {
  const data = loadData();
  const full = L.buildLayout(data, { width: 1600 });
  const coll = L.buildLayout(data, { width: 1600, collapsed: { gates: true } });
  assert.ok(coll.contentHeight < full.contentHeight);
});

test('markers within a row are placed in non-decreasing seq order', () => {
  const xs = L.buildLayout(loadData(), { width: 1600 }).tracks[0].rows[0].items.map(p => p.x);
  for (let i = 1; i < xs.length; i++) assert.ok(xs[i] >= xs[i - 1]);
});
```

- [ ] **Step 2: Run; verify fail** — `node --test tests/arcLayout.test.js` → FAIL (`Cannot find module '../compile/assets/civilizationArcLayout.js'`).

- [ ] **Step 3: Implement the module**

```js
// compile/assets/civilizationArcLayout.js
// Pure geometry for the chronological-tracks arc. Browser (window.CivArcLayout) + Node. No DOM.
(function (root) {
  "use strict";
  var O = (typeof require !== "undefined") ? require("./civilizationOntology.js") : (root && root.CivOntology);

  var GATE_FAMILIES = [
    "v3.9 milestones (A-J)",
    "Deployment register (G-0..G-8.4)",
    "v4.0 (K/L)",
    "Release & security gates (v3.9)",
  ];

  var GEOM = { gutter: 168, marginRight: 28, rowH: 30, trackPad: 8, trackGap: 10, top: 64, axisH: 34 };

  var ERAS = [
    { seq: 0.3, label: "Feb" }, { seq: 3, label: "Mar" }, { seq: 6, label: "Apr" },
    { seq: 9, label: "May" }, { seq: 13.9, label: "Jun · now" }, { seq: 15, label: "future" },
  ];

  function scaleX(domain, plotLeft, plotRight) {
    var span = (domain.end - domain.start) || 1;
    return function (seq) { return plotLeft + ((seq - domain.start) / span) * (plotRight - plotLeft); };
  }
  function bySeq(a, b) { return a.seq - b.seq; }

  function buildLayout(data, opts) {
    opts = opts || {};
    var width = opts.width || 1200;
    var collapsed = opts.collapsed || {};
    var items = data.items || [];
    var domain = data.domain || { start: 0, end: 15 };
    var plotLeft = GEOM.gutter, plotRight = width - GEOM.marginRight;
    var sx = scaleX(domain, plotLeft, plotRight);

    var beats = items.filter(function (i) { return i.type === "work" && i.provenance === "reconstructed"; });
    var decisions = items.filter(function (i) { return i.type === "decision"; });
    var goal = items.filter(function (i) { return i.type === "goal"; });
    var gates = items.filter(function (i) { return i.type === "gate"; });
    var work = items.filter(function (i) { return i.type === "work" && i.provenance === "derived"; });

    var defs = [
      { id: "construction", label: "construction arc", rows: [{ id: "beats", label: "", items: beats.concat(decisions, goal) }] },
      { id: "gates", label: "gates", rows: GATE_FAMILIES.map(function (f) {
          return { id: "gate:" + f, label: f, items: gates.filter(function (g) { return (g.family || null) === f; }) };
        }) },
      { id: "worklist", label: "worklist", rows: [{ id: "work", label: "", items: work }] },
    ];

    var y = GEOM.top;
    var tracks = defs.map(function (t) {
      var isColl = !!collapsed[t.id], top = y, rows = [];
      if (isColl) { y += GEOM.rowH; }
      else {
        rows = t.rows.map(function (r) {
          var cy = y + GEOM.trackPad + GEOM.rowH / 2;
          var placed = r.items.slice().sort(bySeq).map(function (it) { return { item: it, x: sx(it.seq), y: cy }; });
          y += GEOM.rowH + GEOM.trackPad;
          return { id: r.id, label: r.label, y: cy, items: placed };
        });
      }
      var height = y - top; y += GEOM.trackGap;
      return { id: t.id, label: t.label, collapsed: isColl, top: top, height: height, rows: rows };
    });

    var nowSeq = O.deriveNow(items);
    return {
      tracks: tracks, scaleX: sx, domain: domain, plotLeft: plotLeft, plotRight: plotRight,
      nowSeq: nowSeq, nowX: sx(nowSeq),
      eras: ERAS.map(function (e) { return { x: sx(e.seq), label: e.label }; }),
      width: width, contentWidth: width, contentHeight: y + GEOM.axisH,
    };
  }

  var api = { GEOM: GEOM, GATE_FAMILIES: GATE_FAMILIES, ERAS: ERAS, scaleX: scaleX, buildLayout: buildLayout };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (root) root.CivArcLayout = api;
})(typeof window !== "undefined" ? window : null);
```

- [ ] **Step 4: Run; verify pass** — `node --test tests/arcLayout.test.js` → all pass.

- [ ] **Step 5: Commit** (controller) — `git commit -m "feat(arc): pure chronological-tracks layout module + tests"`.

---

## Task 2: Wire the new assets into the build

**Files:** Modify `compile/build_site.py`.

- [ ] **Step 1:** In `build()`, after the existing `copy_asset(...)` calls, add the two new assets and capture their cache-bust versions:

```python
    ARC_LAYOUT_VER = copy_asset("civilizationArcLayout.js")
    ARC_DRAW_VER = copy_asset("civilizationArcDraw.js")
```
(Declare `ARC_LAYOUT_VER`/`ARC_DRAW_VER` in the `global` line alongside `ARC_NAV_VER`.)

- [ ] **Step 2:** In `arc_page()` (and anywhere the arc scripts are injected), emit the scripts in dependency order **before** `civilizationArcNav.js`:

```python
'<script defer src="civilizationOntology.js?v=%s"></script>'
'<script defer src="civilizationArcData.js?v=%s"></script>'
'<script defer src="civilizationArcLayout.js?v=%s"></script>'
'<script defer src="civilizationArcDraw.js?v=%s"></script>'
'<script defer src="civilizationArcNav.js?v=%s"></script>'
% (ONTO_VER, ARC_DATA_VER, ARC_LAYOUT_VER, ARC_DRAW_VER, ARC_NAV_VER)
```
(`civilizationArcDraw.js` is created in Task 3; until then it's an empty stub — create a one-line stub `window.CivArcDraw={};` now so the build/copy succeeds.)

- [ ] **Step 3: Run** — `python3 compile/build_site.py` → succeeds; confirm `dist/civilizationArcLayout.js` and `dist/civilizationArcDraw.js` exist and the arc page references all five scripts in order.

- [ ] **Step 4: Commit** — `git commit -m "build(arc): emit + inject layout/draw assets before nav"`.

---

## Task 3: `civilizationArcDraw.js` — axis, now-line, tracks

**Files:** Create/expand `compile/assets/civilizationArcDraw.js`. Visual reference: the approved `direction_c_full_composition` mockup.

`window.CivArcDraw` exposes pure builders that take `(svg, layout, state)` and append SVG elements (no event wiring). Use the existing `style.css` arc palette / CSS variables; status colors: done `#1D9E75`, active `#BA7517`, blocked `#E24B4A`, planned `#378ADD`, future `#888780`.

- [ ] **Step 1:** Implement `drawAxis(svg, layout)`:
  - a baseline `<line>` at `contentHeight - GEOM.axisH` from `plotLeft` to `plotRight`;
  - era ticks: for each `layout.eras`, a small tick + `<text>` label at `e.x`;
  - the **now-line**: a vertical dashed `<line class="arc-now-line">` at `layout.nowX` spanning the tracks, plus a "now" tag near the top.

- [ ] **Step 2:** Implement `drawTracks(svg, layout, state)`:
  - for each `track`: a faint band `<rect class="arc-track-band">` spanning `[0, contentWidth]` × `[track.top, track.top+track.height]`;
  - a gutter label `<text class="arc-track-label">` at `x = plotLeft - 12` (right-anchored) with a chevron marker (`data-arc-collapse="<track.id>"`, down = expanded / right = collapsed);
  - for each sub-row, a small indented `<text class="arc-subrow-label">` at the row's `y`.

- [ ] **Step 3:** Confirm it renders without error via the DOM smoke harness (Task 9 will assert; for now `node --check`).

- [ ] **Step 4: Commit** — `git commit -m "feat(arc): draw axis, now-line, track bands + gutter labels"`.

---

## Task 4: `civilizationArcDraw.js` — markers

**Files:** Expand `compile/assets/civilizationArcDraw.js`.

- [ ] **Step 1:** Implement `drawMarkers(svg, layout, state)` iterating every placed item across tracks/rows. Shape by `item.type`: construction beats → small `<circle r=4>`; gates → `<path>` diamond (~9px); decisions → small `<circle r=3>`; worklist (`type:work, provenance:derived`) → rounded `<rect>` bar (~width by a fixed span, height 10). Fill by status color (above); `item.blocked` adds a red stroke accent. Each element carries `data-arc-item="<id>"`, `tabindex="0"`, `role="button"`, and `aria-label="<code> — <label>"`. Position at the item's `{x, y}` from the layout. Apply the `arc-is-selected` class when `state.selectedId === item.id`.

- [ ] **Step 2:** Node-check the file; ensure `drawAxis`, `drawTracks`, `drawMarkers` are all on `window.CivArcDraw`.

- [ ] **Step 3: Commit** — `git commit -m "feat(arc): draw markers by type + status with selection hooks"`.

---

## Task 5: `civilizationArcNav.js` — controller, render, hover/select, panels  ⟶ RENDERABLE CHECKPOINT

**Files:** Rewrite `compile/assets/civilizationArcNav.js`.

- [ ] **Step 1:** Implement the controller:
  - `state = { collapsed: {}, selectedId: null, width: BASE_WIDTH }`.
  - `render(root, data)`: read width from the frame (`getBoundingClientRect().width`, fallback `BASE_WIDTH=1680`); `layout = CivArcLayout.buildLayout(data, { width, collapsed: state.collapsed })`; create the `<svg class="arc-svg">` sized `viewBox="0 0 contentWidth contentHeight"`, `style.height = contentHeight`; call `CivArcDraw.drawAxis/drawTracks/drawMarkers`; then wire interaction (Step 2); then render the panels (Step 3).
  - bootstrap: on `DOMContentLoaded`, for each `[data-civilization-arc-nav]`, `render(el, window.CIVILIZATION_ARC_DATA)`.

- [ ] **Step 2:** Interaction: delegate events on the SVG — `mouseover`/`focusin` on `[data-arc-item]` → tooltip (code+label); `click` on `[data-arc-item]` → `state.selectedId = id`; re-render markers + detail panel; click empty → clear.

- [ ] **Step 3:** Panels: `buildNowPanel(data)` (current gate = the blocked frontier item + its blocker worklist item + a near-term N summary) and `buildDetailPanel(item)` (full label, status badge, track+family, note, `href` link). Layout: full-width arc on top, panels below (grid) — matches the mockup; CSS in `style.css`.

- [ ] **Step 4: Build + verify render** — `python3 compile/build_site.py`; serve `dist/` and load `civilization-arc.html` headless: assert 0 console errors, the now-line is present, the 4 gate family sub-rows render, markers appear in seq order. Capture a screenshot.

- [ ] **Step 5: Commit** — `git commit -m "feat(arc): chronological-tracks controller + render + panels"`.

- [ ] **Step 6: ⟶ PAUSE for Michael** — present the rendered chart (screenshot, multiple widths). Do not proceed to Tasks 6–10 until he approves the look.

---

## Task 6: Collapse / expand tracks + family sub-rows

**Files:** Modify `compile/assets/civilizationArcNav.js`.

- [ ] **Step 1:** Delegate `click` on `[data-arc-collapse]` → toggle `state.collapsed[id]` → re-render (layout recomputes heights; chevron flips). Confirm collapsing the gates track shrinks the SVG height.
- [ ] **Step 2: Commit** — `git commit -m "feat(arc): collapsible tracks + gate family sub-rows"`.

---

## Task 7: Zoom / pan the timeline

**Files:** Modify `compile/assets/civilizationArcNav.js`.

- [ ] **Step 1:** Add `state.view = null` (full) or a `{x,w}` window over `contentWidth`. Zoom-in/out buttons + Ctrl±/0 + wheel adjust the viewBox window (clamp to content); drag pans; "fit" resets. The vertical extent stays full.
- [ ] **Step 2: Commit** — `git commit -m "feat(arc): viewBox zoom/pan over the timeline"`.

---

## Task 8: Responsive — reflow on resize

**Files:** Modify `compile/assets/civilizationArcNav.js`, `compile/assets/style.css`.

- [ ] **Step 1:** Install a debounced (~120ms) `window` `resize` listener **and** a `ResizeObserver` on `.arc-frame` (guarded by `typeof ResizeObserver === "function"`), torn down/re-installed once per render, that re-runs `render()` when the measured width changes. In `style.css`, make `.arc-frame` full-width (`max-width:none` for the standalone/expanded page; single-column unless an item is selected) with `overflow-x:auto`; `.arc-svg{width:100%}` when content fits, else px-width (mirror the layout's `contentWidth > width` branch) so wide content scrolls rather than downscaling.
- [ ] **Step 2: Verify** at 1280 / 1920 / 768 widths headless: full-width, reflow, no page horizontal overflow.
- [ ] **Step 3: Commit** — `git commit -m "feat(arc): responsive full-width + resize reflow"`.

---

## Task 9: Rewrite the DOM smoke test

**Files:** Rewrite `tests/arc-dom-smoke.test.js`.

- [ ] **Step 1: Write the test** (jsdom; loads ontology→data→layout→draw→nav, dispatches `DOMContentLoaded`):

```js
const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const { JSDOM } = require('jsdom');
const O = require('../compile/assets/civilizationOntology.js');

function render() {
  const A = p => fs.readFileSync(path.join(__dirname, '../compile/assets/', p), 'utf8');
  const dom = new JSDOM('<!doctype html><div data-civilization-arc-nav data-arc-expanded="true"></div>', { runScripts: 'outside-only', pretendToBeVisual: true });
  const w = dom.window;
  ['civilizationOntology.js','civilizationArcData.js','civilizationArcLayout.js','civilizationArcDraw.js','civilizationArcNav.js']
    .forEach(f => { w.eval(A(f)); });
  w.document.dispatchEvent(new w.Event('DOMContentLoaded'));
  return w;
}

test('renders tracks, family sub-rows, markers in seq order, and the now-line', () => {
  const w = render();
  const data = w.CIVILIZATION_ARC_DATA;
  assert.strictEqual(O.validateItems(data.items).ok, true);
  assert.ok(Math.abs(O.deriveNow(data.items) - 13.9) < 1e-9);
  assert.ok(w.document.querySelector('.arc-now-line'), 'now-line present');
  assert.ok(w.document.querySelectorAll('.arc-track-band').length >= 3, '3 tracks');
  assert.ok(w.document.querySelectorAll('.arc-subrow-label').length >= 4, '4 gate family rows');
  const codes = data.items.map(i => i.code);
  assert.strictEqual(new Set(codes).size, codes.length, 'codes unique');
  assert.ok(w.document.querySelectorAll('[data-arc-item]').length > 0, 'markers present');
  console.log('arc tracks smoke ok:', data.items.length, 'items, now=', O.deriveNow(data.items));
});

test('collapsing the gates track removes its family rows', () => {
  const w = render();
  const before = w.document.querySelectorAll('.arc-subrow-label').length;
  w.document.querySelector('[data-arc-collapse="gates"]').dispatchEvent(new w.Event('click', { bubbles: true }));
  assert.ok(w.document.querySelectorAll('.arc-subrow-label').length < before);
});
```

- [ ] **Step 2: Run; verify pass** — `node tests/arc-dom-smoke.test.js` (and confirm `jsdom` is a devDependency; `npm i -D jsdom` if missing).

- [ ] **Step 3: Commit** — `git commit -m "test(arc): jsdom smoke for the chronological-tracks renderer"`.

---

## Task 10: CI step + full verify + Playwright

**Files:** Modify `.github/workflows/ci.yml`, `tests/arc-nav.spec.js`.

- [ ] **Step 1:** In `ci.yml`, after the Python step, add a Node step:

```yaml
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - name: Arc unit + DOM tests
        run: |
          node --test tests/ontology.test.js tests/arcLayout.test.js
          npm ci
          node tests/arc-dom-smoke.test.js
```

- [ ] **Step 2:** Update `tests/arc-nav.spec.js` Playwright assertions to the tracks model: assert the now-line element, the gate family sub-row labels, and a marker click opening the detail panel (real updates, not skips).

- [ ] **Step 3: Run** `npm run verify` (build + checks + DOM + Playwright). Fix failures.

- [ ] **Step 4: Commit** — `git commit -m "test(arc): CI node step + Playwright suite on tracks model"`.

---

## Self-Review (completed at authoring)

- **Spec coverage:** axes/x=time+y=track (Tasks 1,3,4); construction/gates-families/worklist tracks (Task 1 `buildLayout`); now-line at frontier (Tasks 1,3); status colors + blocker accent (Task 4); hover/select/detail + now panel (Task 5); collapse (Task 6); zoom/pan (Task 7); responsive full-width + reflow (Task 8); keep contract + small modules (File Structure, Tasks 1/3/4); testing (Tasks 1,9,10); CI (Task 10). Deferred items (animation, Projection 2, real dates, dep-graph) are out of scope per spec §10 and intentionally absent.
- **Placeholders:** the only deferred code is the `civilizationArcDraw.js` stub in Task 2, explicitly created and then filled in Tasks 3–4.
- **Type consistency:** `buildLayout` shape (`tracks[].rows[].items[].{item,x,y}`, `nowX`, `contentHeight`, `scaleX`) is produced in Task 1 and consumed identically in Tasks 3–5; `data-arc-item` / `data-arc-collapse` / `.arc-now-line` / `.arc-track-band` / `.arc-subrow-label` are emitted in Tasks 3–4 and asserted in Task 9.
- **Renderable checkpoint:** Task 5 Step 6 pauses for Michael before the interaction/responsive/test tail.
