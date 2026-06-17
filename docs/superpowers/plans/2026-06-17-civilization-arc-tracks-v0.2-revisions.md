# Civilization Arc — Tracks v0.2 Revisions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Re-encode the chronological-tracks arc x-axis as ordinal rank (not `seq` magnitude), annotate it with sprint start-ticks (not months), enrich marker tooltips, and make the chart reflow responsively — per spec `docs/superpowers/specs/2026-06-17-civilization-arc-chronological-tracks-design.md` v0.2.

**Architecture:** Three pure-ish browser modules already exist and stay split: `civilizationArcLayout.js` (pure geometry, Node-testable) → `civilizationArcDraw.js` (pure SVG construction) → `civilizationArcNav.js` (controller: state, events, responsive). All changes preserve that boundary: geometry/scale changes land in Layout, rendering changes in Draw, interaction/resize in Nav, theming in `style.css`.

**Tech Stack:** Vanilla ES5-style IIFE modules (no build step for JS), SVG, `node:test` unit tests, jsdom DOM-smoke tests, Playwright browser tests, Python `build_site.py` for asset injection.

## Global Constraints

- **Branch:** `claude/elegant-swanson-965269`. Operate cross-worktree via `git -C <elegant-swanson-worktree>` if your session is rooted elsewhere. **No push, no PR, no merge.**
- **No new data:** every item already carries `seq, status, type, sprint, family, code, provenance, deps, href, note`; `data.sprints` is 15 `{id,label}`. Do **not** add a `date` field in this plan (date backfill is a deferred follow-up).
- **Keep modules pure:** Layout and Draw must not read globals, mutate state, or attach events. Only Nav owns state/events.
- **ES5 idiom:** `var`, function declarations, no arrow functions / template literals in the shipped assets (match existing files). Tests may use modern Node JS.
- **Status palette (unchanged):** done `#1D9E75` · active `#BA7517` · blocked `#E24B4A` · planned `#378ADD` · future `#888780`.
- **Geometry is shared:** `CivArcLayout.GEOM` is imported by Draw — change it in Layout only.
- **Run from the worktree root.** Commands below assume cwd = the elegant-swanson worktree.

## File Structure

- `compile/assets/civilizationArcLayout.js` — replace linear `scaleX` with an ordinal **rank scale**; emit `layout.sprintTicks`; compute overflow `contentWidth` from a minimum column width. (MODIFY)
- `compile/assets/civilizationArcDraw.js` — `drawAxis` renders sprint start-ticks instead of era ticks/labels; bump sub-row/track label legibility. (MODIFY)
- `compile/assets/civilizationArcNav.js` — build `ordinalById`/`sprintLabelById` maps; enriched tooltip; `ResizeObserver` reflow. (MODIFY)
- `compile/assets/style.css` — horizontal scroll on `.arc-frame`; sprint-tick label style. (MODIFY)
- `tests/arcLayout.test.js` — rank-scale, sprint-ticks, min-column-width tests; fix the old endpoint test. (MODIFY)
- `tests/arc-dom-smoke.test.js` — assert sprint ticks render, no era labels, enriched tooltip. (MODIFY)
- `tests/arc-nav.spec.js` — drop era-label expectations; add a reflow check. (MODIFY)

---

### Task 0: Green the tracks test baseline (finish the un-done T9/T10)

**Why:** The committed renderer is the tracks model, but `tests/arc-dom-smoke.test.js` is still the OLD swimlane test — it loads only ontology+data+nav (NOT the new `civilizationArcLayout.js`/`civilizationArcDraw.js`, so `render()` hits `if (!CivArcLayout || !CivArcDraw) return;` and nothing mounts) and asserts obsolete `.arc-swimlane`/`.arc-current-line` structure. `npm run verify` is therefore red at `test:dom` before any v0.2 change. Green the baseline against the CURRENT renderer first. (Validated: loading all 5 modules → nav mounts, 3 `.arc-track-band`, 3 `.arc-track-label`, 4 `.arc-subrow-label`, 109 `.arc-item-group`, `.arc-now-line` present.)

**Files:**
- Modify: `tests/arc-dom-smoke.test.js` (rewrite `assertRenderedDom`; delete swimlane sub-row/packing assertions; KEEP `assertData` contract checks)
- Modify: `tests/arc-nav.spec.js` (update Playwright selectors for tracks)

**Interfaces:** none (tests only).

- [ ] **Step 1: Confirm the red baseline**

Run: `npm run test:dom`
Expected: FAIL — `arc nav did not mount`.

- [ ] **Step 2: Fix module loading + rewrite DOM assertions.** Keep `assertData` (lines ~20-75) untouched. Delete the swimlane-packing assertion block (the code asserting `.arc-swimlane`, `.arc-swimlane-label`, sub-row overlap/packing). Replace `assertRenderedDom()` with:

```js
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
  assert.strictEqual(nav.getAttribute("data-expanded"), "false", "default nav should be compact");
  assert(nav.querySelector("svg.arc-svg"), "SVG not rendered");
  assert.strictEqual(nav.querySelectorAll(".arc-track-band").length, 3, "expected 3 track bands");
  assert.strictEqual(nav.querySelectorAll(".arc-track-label").length, 3, "expected 3 track labels");
  assert(nav.querySelectorAll(".arc-subrow-label").length >= 4, "expected >=4 gate-family sub-row labels");
  assert(nav.querySelectorAll(".arc-item-group").length > 0, "no item node groups produced");
  assert(nav.querySelectorAll(".arc-marker").length > 0, "no item shapes produced");
  assert(nav.querySelector(".arc-now-line"), "now-line element missing");
}
```

  Do NOT assert era labels here — v0.2 Task 4 removes them. Assert only structure stable across v0.2 (mount, tracks, markers, now-line) so later tasks don't fight this one.

- [ ] **Step 3: Run to verify green**

Run: `npm run test:dom`
Expected: PASS.

- [ ] **Step 4: Update the Playwright spec.** Read `tests/arc-nav.spec.js` (predates the tracks rewrite). Replace old selectors (`.arc-swimlane*`, `.arc-current-line`, era/month text) with tracks selectors (`.arc-track-band`, `.arc-now-line`, `.arc-item-group`). Keep assertions that still hold (page loads, `svg.arc-svg` present, marker click → `.arc-detail-panel` populates). Drop any assertion with no tracks equivalent.

Run: `npm run test:browser`
Expected: PASS.

- [ ] **Step 5: Full verify**

Run: `npm run verify`
Expected: build → test:js → test:dom → test:browser all PASS.

- [ ] **Step 6: Commit**

```bash
git add tests/arc-dom-smoke.test.js tests/arc-nav.spec.js
git commit -m "test(arc): rewrite dom-smoke + playwright for tracks renderer (green verify)"
```

---

### Task 1: Layout — ordinal rank scale

**Files:**
- Modify: `compile/assets/civilizationArcLayout.js` (the `scaleX` function, lines 21-24; `buildLayout` scale wiring, lines 27-34)
- Test: `tests/arcLayout.test.js`

**Interfaces:**
- Produces: `CivArcLayout.buildRankScale(items, plotLeft, plotRight) -> sx` where `sx(seq)->x`, `sx.distinctCount:number`, `sx.rankOf(seq)->number|undefined`. `buildLayout(...)` keeps exposing the built scale as `layout.scaleX` and `layout.nowX === layout.scaleX(layout.nowSeq)`.

- [ ] **Step 1: Write the failing tests** (replace the obsolete endpoint test in `tests/arcLayout.test.js`)

```js
// Replace the existing 'scaleX maps domain endpoints to the plot edges' test with:
test('buildRankScale spaces distinct seqs equidistantly across the plot', () => {
  const sx = L.buildRankScale(
    [{ seq: 0 }, { seq: 5 }, { seq: 5 }, { seq: 99 }], // 3 distinct: 0,5,99
    100, 400
  );
  assert.strictEqual(sx.distinctCount, 3);
  assert.strictEqual(sx(0), 100);    // first column at plotLeft
  assert.strictEqual(sx(99), 400);   // last column at plotRight
  assert.strictEqual(sx(5), 250);    // middle column — equidistant, NOT proportional to value
});

test('items sharing a seq share an x-column', () => {
  const sx = L.buildRankScale([{ seq: 1 }, { seq: 2 }, { seq: 2 }], 0, 200);
  assert.strictEqual(sx(2), sx(2));
  assert.strictEqual(sx.rankOf(2), 1);
});
```

- [ ] **Step 2: Run to verify they fail**

Run: `node --test tests/arcLayout.test.js`
Expected: FAIL — `L.buildRankScale is not a function`.

- [ ] **Step 3: Implement the rank scale** — in `civilizationArcLayout.js`, replace the linear `scaleX` (lines 21-24) with:

```js
  // Ordinal rank scale: distinct seq values are placed at equidistant columns
  // (NOT proportional to seq magnitude). Items sharing a seq share a column.
  function buildRankScale(items, plotLeft, plotRight) {
    var seqs = [];
    for (var i = 0; i < items.length; i++) {
      var s = items[i] && items[i].seq;
      if (typeof s === "number" && !isNaN(s)) seqs.push(s);
    }
    seqs.sort(function (a, b) { return a - b; });
    var distinct = [];
    for (var j = 0; j < seqs.length; j++) {
      if (j === 0 || seqs[j] !== seqs[j - 1]) distinct.push(seqs[j]);
    }
    var n = distinct.length;
    var rankOf = {};
    for (var k = 0; k < n; k++) rankOf[distinct[k]] = k;
    var span = (n > 1) ? (n - 1) : 1;
    function sx(seq) {
      var r = rankOf[seq];
      if (r === undefined) { // value not in the placed set: fall to nearest lower rank
        r = 0;
        for (var m = 0; m < n; m++) { if (distinct[m] <= seq) r = m; else break; }
      }
      return plotLeft + (r / span) * (plotRight - plotLeft);
    }
    sx.distinctCount = n;
    sx.rankOf = function (seq) { return rankOf[seq]; };
    return sx;
  }
```

- [ ] **Step 4: Wire `buildLayout` to the rank scale** — in `buildLayout`, replace `var sx = scaleX(domain, plotLeft, plotRight);` (line 34) with:

```js
    var sx = buildRankScale(items, plotLeft, plotRight);
```

  (Leave `domain` in the returned object for back-compat, but it no longer drives x.) Update the exports object (line 75) — replace `scaleX: scaleX,` with `buildRankScale: buildRankScale,`.

- [ ] **Step 5: Run to verify pass** (and that the unchanged tests 2,3,5,6 still pass)

Run: `node --test tests/arcLayout.test.js`
Expected: PASS — all tests green (the `nowX === scaleX(deriveNow)` test still holds because `layout.scaleX` is the built `sx`).

- [ ] **Step 6: Commit**

```bash
git add compile/assets/civilizationArcLayout.js tests/arcLayout.test.js
git commit -m "feat(arc): ordinal rank x-scale (equidistant by distinct seq)"
```

---

### Task 2: Layout — sprint start-ticks + overflow width

**Files:**
- Modify: `compile/assets/civilizationArcLayout.js` (`GEOM`, `ERAS` removal, `buildLayout` return)
- Test: `tests/arcLayout.test.js`

**Interfaces:**
- Produces: `layout.sprintTicks: Array<{id, label, x, startSeq}>` (ordered by `x`, one per sprint that has ≥1 item); `layout.contentWidth >= plotLeft + (distinctCount-1)*MIN_COL + marginRight`. Removes `layout.eras`.

- [ ] **Step 1: Write the failing tests** (add to `tests/arcLayout.test.js`)

```js
test('sprintTicks: one ordered tick per sprint, first is origin at plotLeft', () => {
  const data = loadData();
  const lay = L.buildLayout(data, { width: 1600 });
  assert.strictEqual(lay.sprintTicks.length, 15);
  for (let i = 1; i < lay.sprintTicks.length; i++) {
    assert.ok(lay.sprintTicks[i].x >= lay.sprintTicks[i - 1].x);
  }
  assert.strictEqual(lay.sprintTicks[0].id, 'origin');
  assert.strictEqual(lay.sprintTicks[0].x, lay.plotLeft);
  assert.strictEqual(lay.eras, undefined);
});

test('narrow width forces horizontal overflow via MIN_COL', () => {
  const data = loadData();
  const lay = L.buildLayout(data, { width: 300 });
  const n = lay.scaleX.distinctCount;
  assert.ok(lay.contentWidth >= lay.plotLeft + (n - 1) * 14 + L.GEOM.marginRight);
  assert.ok(lay.contentWidth > 300);
});
```

- [ ] **Step 2: Run to verify they fail**

Run: `node --test tests/arcLayout.test.js`
Expected: FAIL — `lay.sprintTicks` is undefined.

- [ ] **Step 3: Add sprint-tick + overflow geometry.** In `civilizationArcLayout.js`:

  (a) Add `MIN_COL` to `GEOM` and widen the gutter for legible labels (Task 5 depends on it). Replace the `GEOM` line (14) with:

```js
  var GEOM = { gutter: 190, marginRight: 28, rowH: 30, trackPad: 8, trackGap: 10, top: 64, axisH: 34, minCol: 14 };
```

  (b) Delete the `ERAS` constant (lines 16-19) and its use in the return (`eras: ERAS.map(...)`, line 70).

  (c) Add a sprint-tick builder above `buildLayout`:

```js
  function buildSprintTicks(data, items, sx) {
    var sprints = (data && data.sprints) || [];
    var minSeq = {};
    items.forEach(function (it) {
      if (!it || it.sprint == null || typeof it.seq !== "number") return;
      if (minSeq[it.sprint] === undefined || it.seq < minSeq[it.sprint]) minSeq[it.sprint] = it.seq;
    });
    var ticks = [];
    sprints.forEach(function (sp) {
      var ms = minSeq[sp.id];
      if (ms === undefined) return; // sprint with no items → no tick
      ticks.push({ id: sp.id, label: sp.label, x: sx(ms), startSeq: ms });
    });
    ticks.sort(function (a, b) { return a.x - b.x; });
    return ticks;
  }
```

  (d) In `buildLayout`, compute overflow width BEFORE building the scale so the scale spans the full content. Replace lines 33-34 (`var plotLeft = ...; var sx = ...`) with:

```js
    var plotLeft = GEOM.gutter;
    // distinct seq count drives the minimum content width (horizontal overflow).
    var seqSet = {};
    items.forEach(function (it) { if (it && typeof it.seq === "number") seqSet[it.seq] = 1; });
    var distinctN = Object.keys(seqSet).length;
    var minContent = plotLeft + Math.max(0, distinctN - 1) * GEOM.minCol + GEOM.marginRight;
    var contentWidth = Math.max(width, minContent);
    var plotRight = contentWidth - GEOM.marginRight;
    var sx = buildRankScale(items, plotLeft, plotRight);
```

  (e) In the return object (lines 67-72), remove the `eras:` line, add `sprintTicks:`, and set `contentWidth` to the computed value:

```js
    return {
      tracks: tracks, scaleX: sx, domain: domain, plotLeft: plotLeft, plotRight: plotRight,
      nowSeq: nowSeq, nowX: sx(nowSeq),
      sprintTicks: buildSprintTicks(data, items, sx),
      width: width, contentWidth: contentWidth, contentHeight: y + GEOM.axisH,
    };
```

  (f) Add `buildSprintTicks` to the exports (optional) — not required by tests.

- [ ] **Step 4: Run to verify pass**

Run: `node --test tests/arcLayout.test.js`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add compile/assets/civilizationArcLayout.js tests/arcLayout.test.js
git commit -m "feat(arc): sprint start-ticks + min-column overflow width; drop eras"
```

---

### Task 3: Draw — render sprint start-ticks, drop era ticks

**Files:**
- Modify: `compile/assets/civilizationArcDraw.js` (`drawAxis`, lines 76-100 — the era block)
- Test: `tests/arc-dom-smoke.test.js`

**Interfaces:**
- Consumes: `layout.sprintTicks` (Task 2). Renders `<line class="arc-sprint-tick">` + `<text class="arc-sprint-tick-label">` per tick; no longer emits `.arc-era-tick`/`.arc-era-label`.

- [ ] **Step 1: Write the failing test** (add to `tests/arc-dom-smoke.test.js`, matching its existing render harness — locate the `render`/`buildLayout` call it already uses and add near the other axis assertions)

```js
test('axis renders 15 sprint start-ticks and no era labels', () => {
  const { svg } = renderArc(); // use this file's existing render helper
  assert.strictEqual(svg.querySelectorAll('.arc-sprint-tick-label').length, 15);
  assert.strictEqual(svg.querySelectorAll('.arc-era-label').length, 0);
  assert.ok(svg.querySelector('.arc-now-line')); // now-line preserved
});
```

  (If the file's render helper has a different name, use that — Step 0: read the top of `tests/arc-dom-smoke.test.js` to find how it builds an `svg` from the layout, and mirror it.)

- [ ] **Step 2: Run to verify it fails**

Run: `node --test tests/arc-dom-smoke.test.js`
Expected: FAIL — finds 0 `.arc-sprint-tick-label` (still rendering eras).

- [ ] **Step 3: Replace the era block in `drawAxis`** — in `civilizationArcDraw.js`, replace lines 76-100 (the `// Era ticks + labels.` block, from `var eras = layout.eras || [];` through the closing `});`) with:

```js
    // Sprint start-ticks: a short tick + rotated label at each sprint's first item.
    var ticks = layout.sprintTicks || [];
    ticks.forEach(function (t) {
      var tx = num(t.x);
      svg.appendChild(svgEl(doc, "line", {
        "class": "arc-sprint-tick",
        x1: tx, y1: baseY, x2: tx, y2: baseY + 5,
        stroke: "var(--color-text-tertiary)", "stroke-width": 1,
        "vector-effect": "non-scaling-stroke",
      }));
      var label = svgEl(doc, "text", {
        "class": "arc-sprint-tick-label",
        x: tx, y: baseY + 9,
        "text-anchor": "end",
        "font-size": 9,
        fill: "var(--color-text-tertiary)",
        transform: "rotate(-40 " + tx + " " + (baseY + 9) + ")",
      });
      label.textContent = t.label == null ? "" : String(t.label);
      svg.appendChild(label);
    });
```

- [ ] **Step 4: Run to verify pass**

Run: `node --test tests/arc-dom-smoke.test.js`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add compile/assets/civilizationArcDraw.js tests/arc-dom-smoke.test.js
git commit -m "feat(arc): draw sprint start-ticks on the axis (replaces era labels)"
```

---

### Task 4: Draw + CSS — legible track & sub-row labels (point 3)

**Files:**
- Modify: `compile/assets/civilizationArcDraw.js` (`drawTracks`: track label font 12→13 line 173; sub-row label font 9→11 + fill tertiary→secondary, lines 189-190)
- Modify: `compile/assets/style.css` (ensure no CSS overrides shrink them)
- Test: `tests/arc-dom-smoke.test.js`

**Interfaces:** none new — pure styling.

- [ ] **Step 1: Write the failing test** (add to `tests/arc-dom-smoke.test.js`)

```js
test('gate sub-row labels are legible (>=11px) and present for 4 families', () => {
  const { svg } = renderArc();
  const subs = [...svg.querySelectorAll('.arc-subrow-label')];
  assert.ok(subs.length >= 4);
  subs.forEach(t => assert.ok(Number(t.getAttribute('font-size')) >= 11));
});
```

- [ ] **Step 2: Run to verify it fails**

Run: `node --test tests/arc-dom-smoke.test.js`
Expected: FAIL — sub-row `font-size` is `9`.

- [ ] **Step 3: Bump label sizes/contrast** in `civilizationArcDraw.js`:
  - Track label (line 173): change `"font-size": 12,` → `"font-size": 13,`.
  - Sub-row label (lines 189-190): change `"font-size": 9,` → `"font-size": 11,` and `fill: "var(--color-text-tertiary)",` → `fill: "var(--color-text-secondary)",`.

- [ ] **Step 4: Confirm no CSS shrink override.** In `compile/assets/style.css`, the only rule for these is `.arc-track-label,.arc-track-chevron{cursor:pointer}` (line ~1087) and `.arc-subrow-label` has none — so the SVG `font-size` attributes win. Add an explicit safety rule after line 1087:

```css
.arc-track-label{font-weight:600}
.arc-subrow-label{fill:var(--color-text-secondary)}
```

- [ ] **Step 5: Run to verify pass**

Run: `node --test tests/arc-dom-smoke.test.js`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add compile/assets/civilizationArcDraw.js compile/assets/style.css tests/arc-dom-smoke.test.js
git commit -m "fix(arc): legible track and gate-family labels (size + contrast)"
```

---

### Task 5: Nav — enriched marker tooltip (point 2: time/context in mouseover)

**Files:**
- Modify: `compile/assets/civilizationArcNav.js` (`showTooltip` lines 172-182; build maps in `render`)
- Test: `tests/arc-dom-smoke.test.js`

**Interfaces:**
- Consumes: `data.sprints`, `data.items[].sprint`. State gains `s.ordinalById`, `s.sprintLabelById`, `s.itemCount`.

- [ ] **Step 1: Write the failing test** (add to `tests/arc-dom-smoke.test.js`; reuse the file's render helper, then simulate a hover and read the tooltip)

```js
test('tooltip shows sprint + ordinal step + provenance', () => {
  const { root, svg } = renderArc();
  const marker = svg.querySelector('[data-arc-item]');
  marker.dispatchEvent(new root.ownerDocument.defaultView.MouseEvent('mouseover', { bubbles: true }));
  const tip = root.querySelector('.arc-tooltip');
  assert.strictEqual(tip.hidden, false);
  assert.match(tip.textContent, /step \d+ of 109/);
  assert.match(tip.textContent, /sprint ·/);
});
```

- [ ] **Step 2: Run to verify it fails**

Run: `node --test tests/arc-dom-smoke.test.js`
Expected: FAIL — tooltip text is `code — label · status` (no "step"/"sprint").

- [ ] **Step 3: Build the lookup maps once.** In `civilizationArcNav.js` `render`, right after `var s = ensureScaffold(root);` (line 407), add:

```js
    if (!s.ordinalById) {
      s.ordinalById = {};
      s.sprintLabelById = {};
      var sorted = ((data.items) || []).slice().sort(function (a, b) {
        return (a.seq || 0) - (b.seq || 0);
      });
      for (var oi = 0; oi < sorted.length; oi++) {
        if (sorted[oi].id != null) s.ordinalById[sorted[oi].id] = oi + 1;
      }
      s.itemCount = sorted.length;
      ((data.sprints) || []).forEach(function (sp) {
        if (sp && sp.id != null) s.sprintLabelById[sp.id] = sp.label;
      });
    }
```

- [ ] **Step 4: Rewrite `showTooltip`** (lines 172-182) to build structured content:

```js
  function showTooltip(root, item, event) {
    var s = root._arc;
    var tip = s && s.tooltip;
    if (!tip || !item) return;
    clearNode(tip);
    var type = item.type == null ? "" : String(item.type);
    var status = item.blocked ? "blocked" : (item.status == null ? "" : String(item.status));
    tip.appendChild(htmlEl("div", "arc-tooltip-eyebrow", (type + " · " + status).replace(/^ · | · $/g, "")));
    tip.appendChild(htmlEl("strong", "", item.label == null ? "" : String(item.label)));
    if (item.code != null) tip.appendChild(htmlEl("span", "arc-tooltip-code", String(item.code)));
    var sprintLabel = s.sprintLabelById && s.sprintLabelById[item.sprint];
    if (sprintLabel) tip.appendChild(htmlEl("div", "arc-tooltip-meta", "sprint · " + sprintLabel));
    var ord = s.ordinalById && s.ordinalById[item.id];
    if (ord) tip.appendChild(htmlEl("div", "arc-tooltip-meta", "step " + ord + " of " + s.itemCount));
    if (item.date) tip.appendChild(htmlEl("div", "arc-tooltip-meta", "date · " + item.date)); // reserved for date-backfill follow-up
    if (item.provenance) tip.appendChild(htmlEl("div", "arc-tooltip-meta", "provenance · " + item.provenance));
    if (item.href) {
      var a = htmlEl("a", "arc-tooltip-link", "open article →");
      a.href = item.href;
      if (/^https?:\/\//.test(item.href)) { a.target = "_blank"; a.rel = "noopener"; }
      tip.appendChild(a);
    }
    tip.hidden = false;
    positionTooltip(root, tip, event);
  }
```

- [ ] **Step 5: Add tooltip meta styling.** In `style.css`, after the `.arc-tooltip-code` rule (~line 765) add:

```css
.arc-tooltip-meta{font-size:11px;color:var(--color-text-secondary);margin-top:2px}
```

- [ ] **Step 6: Run to verify pass**

Run: `node --test tests/arc-dom-smoke.test.js`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add compile/assets/civilizationArcNav.js compile/assets/style.css tests/arc-dom-smoke.test.js
git commit -m "feat(arc): enriched tooltip (sprint, ordinal step, provenance, link)"
```

---

### Task 6: Nav + CSS — responsive reflow on resize (point 1)

**Files:**
- Modify: `compile/assets/civilizationArcNav.js` (`render` — attach a `ResizeObserver` once)
- Modify: `compile/assets/style.css` (`.arc-tracks-nav .arc-frame` — horizontal scroll)
- Test: `tests/arc-nav.spec.js` (Playwright)

**Interfaces:** none new. `render` becomes idempotent under repeated resize-driven calls (it already is).

- [ ] **Step 1: Add horizontal scroll to the frame.** In `style.css`, the `.arc-tracks-nav .arc-frame` block is at line ~1049. Add `overflow-x:auto;` and `overflow-y:hidden;` to that rule (read lines 1049-1056 first, then append the two declarations inside the block).

- [ ] **Step 2: Attach the ResizeObserver** in `civilizationArcNav.js` `render`, after the maps block from Task 5 (still inside `render`, before computing `width`):

```js
    if (typeof ResizeObserver !== "undefined" && !s.resizeObserver) {
      s.lastWidth = Math.round(s.frame.getBoundingClientRect().width) || 0;
      s.resizeObserver = new ResizeObserver(function () {
        var w = Math.round(s.frame.getBoundingClientRect().width);
        if (!w || Math.abs(w - s.lastWidth) < 2) return; // ignore sub-pixel / height-only changes
        s.lastWidth = w;
        if (s.raf && typeof cancelAnimationFrame !== "undefined") cancelAnimationFrame(s.raf);
        var schedule = (typeof requestAnimationFrame !== "undefined")
          ? requestAnimationFrame : function (fn) { return setTimeout(fn, 16); };
        s.raf = schedule(function () { render(root, data); });
      });
      s.resizeObserver.observe(s.frame); // observe the FRAME (container), not the svg, to avoid feedback
    }
```

- [ ] **Step 3: Update/add the Playwright reflow test.** Read `tests/arc-nav.spec.js`; remove or fix any assertion referencing era/month labels (e.g. text `Feb`/`Mar`/era classes). Then add:

```js
test('reflows on resize without horizontal page scroll', async ({ page }) => {
  await page.goto('/civilization-arc.html');
  await page.setViewportSize({ width: 1400, height: 900 });
  const wide = await page.locator('.arc-svg').getAttribute('viewBox');
  await page.setViewportSize({ width: 760, height: 900 });
  await page.waitForTimeout(120); // allow rAF reflow
  const narrow = await page.locator('.arc-svg').getAttribute('viewBox');
  expect(narrow).not.toBe(wide); // viewBox width recomputed for the new container
  // the chart frame scrolls horizontally, never the document body
  const bodyScrollsX = await page.evaluate(() => document.body.scrollWidth > window.innerWidth + 1);
  expect(bodyScrollsX).toBeFalsy();
});
```

- [ ] **Step 4: Run the browser test**

Run: `npm run test:browser`
Expected: PASS (the reflow test plus the existing, era-free suite).

- [ ] **Step 5: Commit**

```bash
git add compile/assets/civilizationArcNav.js compile/assets/style.css tests/arc-nav.spec.js
git commit -m "feat(arc): responsive ResizeObserver reflow + horizontal frame scroll"
```

---

### Task 7: Full verify + deploy preview

**Files:** none (build + test only)

- [ ] **Step 1: Rebuild the site** (re-injects versioned assets into `dist/`)

Run: `npm run build`
Expected: completes; `dist/civilization-arc.html` references the updated `civilizationArc*.js?v=...` hashes.

- [ ] **Step 2: Run the full verify chain**

Run: `npm run verify`
Expected: build OK → `node --check` OK → jsdom DOM-smoke PASS → Playwright PASS.

- [ ] **Step 3: Visual confirm on the live preview** — reload `http://192.168.20.184:8791/civilization-arc.html` and verify: markers evenly spaced (no early gaps, no "now" pile-up); sprint start-tick labels along the axis; readable track/family labels; hover shows the enriched tooltip; resizing the window reflows the chart.

- [ ] **Step 4: Commit any build artifacts** (if `dist/` is tracked)

```bash
git add dist
git commit -m "build(arc): rebuild dist with tracks v0.2 renderer"
```

---

## Self-Review

**Spec coverage:** §2 ordinal axis → Task 1; §2 sprint start-ticks → Tasks 2,3; §5 enriched tooltip → Task 5; §6 reflow + min-col/horizontal-scroll → Tasks 2,6; §6 legible gutter labels → Task 4; §8/§10 no date field / backfill deferred → honored (Task 5 reads `item.date` only, never writes it). All v0.2 requirements map to a task.

**Type consistency:** `buildRankScale(items, plotLeft, plotRight)` defined in Task 1, consumed in Task 2; `layout.sprintTicks[{id,label,x,startSeq}]` produced in Task 2, consumed in Task 3; `s.ordinalById`/`s.sprintLabelById`/`s.itemCount` produced and consumed within Task 5. `GEOM.minCol` added in Task 2, used in Task 2.

**Open items the implementer must resolve by reading (flagged, not placeholders):**
- `tests/arc-dom-smoke.test.js` render helper name — Tasks 3/4/5 assume a `renderArc()`-style helper returning `{root, svg}`; confirm the actual helper at the top of that file and adapt the three added tests to it.
- `tests/arc-nav.spec.js` era assertions — Task 6 Step 3 requires removing existing era/month-label expectations; grep the file (`grep -nE "Feb|Mar|era" tests/arc-nav.spec.js`) and fix before adding the reflow test.
