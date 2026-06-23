# Civilization Arc — Projection 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the Civilization arc chart as **Projection 1** of the locked 15-type ontology — one unified `items[]` model, a swimlane toggle (default **Status**), a status-derived "now", decluttered dependencies, and an allowlist validation that fails closed.

**Architecture:** All pure logic (validation, derived-now, grouping, dependency declutter) lives in a new browser+Node module `compile/assets/civilizationOntology.js` — the stable *contract* the spec's forward-compat guarantee rests on. `civilizationArcData.js` becomes a single validated `items[]`. `civilizationArcNav.js` consumes the contract (it stops hand-positioning "now", groups lanes by the chosen dimension, and shows dependencies only for the selected item). The Node smoke test inverts its fail-open denylist to a fail-closed allowlist.

**Tech Stack:** Vanilla ES5-style browser JS (IIFE, no build step — matches the existing assets), Node's built-in `node:test`/`node:assert` for unit tests, python-markdown via `compile/build_site.py` for rendering, Playwright + jsdom for existing browser/DOM smoke.

**Spec:** `docs/superpowers/specs/2026-06-16-civilization-ontology-design.md` (§3 contract, §4 Projection 1, §1 ontology, §7 resolutions).

**Reference (current renderer map — read before touching it):** `compile/assets/civilizationArcNav.js`: `mapX` L65, `drawCurrent` L901–918 (now-line, reads `data.currentFocus.x`), `drawRisks` L871–884 (free-floating blocker chips), `drawDependencies` L671–691 (guarded by `state.showDependencies`), `drawSwimlanes` L558–592, `drawPhases` L594–669, `setupSvgInteraction` L1159–1261 (buttons/keys), `render` L1263–1397. Data shapes in `civilizationArcData.js`.

---

## File Structure

- **Create** `compile/assets/civilizationOntology.js` — pure contract: `STATUS_ORDER`, `NODE_TYPES`, `deriveNow`, `validateItems` (allowlist), `groupBy`, `visibleDeps`. Browser (`window.CivOntology`) + Node (`module.exports`). No DOM.
- **Create** `tests/ontology.test.js` — `node:test` unit tests for every pure function.
- **Modify** `compile/assets/civilizationArcData.js` — replace the 5 lists (`phases/markers/gates/risks/decisions`) with one `items[]`; keep `domain`, `title`, `subtitle`, `explanation`, `executionPlan`, `legendItems`. Each item carries the ontology facets.
- **Modify** `compile/assets/civilizationArcNav.js` — consume `CivOntology`; derive "now"; group lanes by dimension with a toggle (default Status); render blockers from `status`; declutter dependencies to the selected item.
- **Modify** `tests/arc-dom-smoke.test.js` — invert denylist → allowlist; assert migrated data passes `validateItems`; assert `deriveNow` is consistent.
- **Modify** `compile/build_site.py` — load the new asset (`copy_asset("civilizationOntology.js")`) and inject its `<script>` before `civilizationArcData.js` on the arc + index pages.
- **Modify** `.github/workflows/ci.yml` — add a Node step running the ontology + DOM smoke tests so the allowlist is enforced in CI (fail-closed).

---

## Task 1: Scaffold the ontology module + `deriveNow`

**Files:**
- Create: `compile/assets/civilizationOntology.js`
- Create: `tests/ontology.test.js`

- [ ] **Step 1: Write the failing test**

```js
// tests/ontology.test.js
const test = require('node:test');
const assert = require('node:assert');
const O = require('../compile/assets/civilizationOntology.js');

test('STATUS_ORDER is future→planned→active→done', () => {
  assert.deepStrictEqual(O.STATUS_ORDER, ['future', 'planned', 'active', 'done']);
});

test('deriveNow = max seq among done/active items', () => {
  const items = [
    { id: 'a', seq: 1, status: 'done' },
    { id: 'b', seq: 3, status: 'active' },
    { id: 'c', seq: 5, status: 'planned' },
  ];
  assert.strictEqual(O.deriveNow(items), 3);
});

test('deriveNow returns 0 when nothing is settled', () => {
  assert.strictEqual(O.deriveNow([{ id: 'a', seq: 4, status: 'planned' }]), 0);
});
```

- [ ] **Step 2: Run it; verify it fails**

Run: `node --test tests/ontology.test.js`
Expected: FAIL — `Cannot find module '../compile/assets/civilizationOntology.js'`.

- [ ] **Step 3: Create the module with constants + `deriveNow`**

```js
// compile/assets/civilizationOntology.js
// Pure contract for the Civilization arc. Browser (window.CivOntology) + Node (module.exports). No DOM.
(function (root) {
  "use strict";

  var STATUS_ORDER = ["future", "planned", "active", "done"];
  var SETTLED = { active: true, done: true };           // allowed left of "now"
  var NODE_TYPES = ["work", "goal", "order", "gate", "artifact", "surface",
    "actor", "phase", "event", "decision", "conflict",
    "policy", "invariant", "resource", "capability"];
  var PROVENANCE = ["reconstructed", "derived"];

  // "now" on the sequence axis = the frontier: the largest seq among settled (done/active) items.
  function deriveNow(items) {
    var now = -Infinity;
    for (var i = 0; i < items.length; i++) {
      if (SETTLED[items[i].status] && items[i].seq > now) now = items[i].seq;
    }
    return now === -Infinity ? 0 : now;
  }

  var api = {
    STATUS_ORDER: STATUS_ORDER, NODE_TYPES: NODE_TYPES, PROVENANCE: PROVENANCE,
    SETTLED: SETTLED, deriveNow: deriveNow,
  };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (root) root.CivOntology = api;
})(typeof window !== "undefined" ? window : null);
```

- [ ] **Step 4: Run tests; verify pass**

Run: `node --test tests/ontology.test.js`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
git add compile/assets/civilizationOntology.js tests/ontology.test.js
git commit -m "feat(arc): ontology module scaffold + deriveNow"
```

---

## Task 2: `validateItems` — the fail-closed allowlist

**Files:**
- Modify: `compile/assets/civilizationOntology.js`
- Modify: `tests/ontology.test.js`

- [ ] **Step 1: Write the failing tests**

```js
// append to tests/ontology.test.js
test('validateItems accepts a clean settled-prefix set', () => {
  const items = [
    { id: 'a', type: 'work', status: 'done', provenance: 'reconstructed', seq: 1, sprint: 'origin', repo: ['wiki'] },
    { id: 'b', type: 'work', status: 'active', provenance: 'derived', seq: 2, sprint: 'hive', repo: ['hive'] },
    { id: 'c', type: 'work', status: 'planned', provenance: 'derived', seq: 3, sprint: 'deploy', repo: ['site'] },
  ];
  assert.strictEqual(O.validateItems(items).ok, true);
});

test('validateItems FAILS CLOSED on a planned item left of now (the bug we are killing)', () => {
  const items = [
    { id: 'a', type: 'work', status: 'planned', provenance: 'derived', seq: 1, sprint: 'x', repo: ['r'] }, // left of now
    { id: 'b', type: 'work', status: 'done', provenance: 'derived', seq: 5, sprint: 'y', repo: ['r'] },
  ];
  const r = O.validateItems(items);
  assert.strictEqual(r.ok, false);
  assert.ok(r.errors.some(e => /left of now/.test(e)));
});

test('validateItems rejects invalid enum + duplicate id + missing fields', () => {
  const items = [
    { id: 'a', type: 'nope', status: 'weird', provenance: 'x', seq: 'NaN', repo: 'r' },
    { id: 'a', type: 'work', status: 'done', provenance: 'derived', seq: 1, sprint: 's', repo: ['r'] },
  ];
  const r = O.validateItems(items);
  assert.strictEqual(r.ok, false);
  assert.ok(r.errors.some(e => /invalid type/.test(e)));
  assert.ok(r.errors.some(e => /invalid status/.test(e)));
  assert.ok(r.errors.some(e => /duplicate id/.test(e)));
  assert.ok(r.errors.some(e => /seq must be a number/.test(e)));
});
```

- [ ] **Step 2: Run; verify fail**

Run: `node --test tests/ontology.test.js`
Expected: FAIL — `O.validateItems is not a function`.

- [ ] **Step 3: Implement `validateItems` (add to the module, before `var api`)**

```js
  // Allowlist, fail-closed. Returns { ok, errors:[...] }. ok only when zero errors.
  function validateItems(items) {
    var errors = [];
    if (!Array.isArray(items)) return { ok: false, errors: ["items is not an array"] };
    var now = deriveNow(items);
    var seen = {};
    items.forEach(function (it, idx) {
      var where = "item[" + idx + "] " + ((it && it.id) ? it.id : "(no id)");
      if (!it || typeof it !== "object") { errors.push(where + ": not an object"); return; }
      if (!it.id) errors.push(where + ": missing id");
      else if (seen[it.id]) errors.push(where + ": duplicate id");
      else seen[it.id] = true;
      if (NODE_TYPES.indexOf(it.type) === -1) errors.push(where + ": invalid type '" + it.type + "'");
      if (STATUS_ORDER.indexOf(it.status) === -1) errors.push(where + ": invalid status '" + it.status + "'");
      if (PROVENANCE.indexOf(it.provenance) === -1) errors.push(where + ": invalid provenance '" + it.provenance + "'");
      if (typeof it.seq !== "number" || isNaN(it.seq)) errors.push(where + ": seq must be a number");
      if (!it.sprint) errors.push(where + ": missing sprint");
      if (!Array.isArray(it.repo)) errors.push(where + ": repo must be an array");
      // THE allowlist gate (fail-closed): anything left of "now" must be settled.
      if (typeof it.seq === "number" && !isNaN(it.seq) && it.seq < now && !SETTLED[it.status]) {
        errors.push(where + ": status '" + it.status + "' at seq " + it.seq +
          " is left of now (" + now + ") — past items must be done/active");
      }
    });
    return { ok: errors.length === 0, errors: errors };
  }
```

Add `validateItems: validateItems,` to the `api` object.

- [ ] **Step 4: Run; verify pass**

Run: `node --test tests/ontology.test.js`
Expected: PASS (all tests).

- [ ] **Step 5: Commit**

```bash
git add compile/assets/civilizationOntology.js tests/ontology.test.js
git commit -m "feat(arc): validateItems allowlist (fail-closed, past must be settled)"
```

---

## Task 3: `groupBy` — the four swimlane dimensions

**Files:** Modify `compile/assets/civilizationOntology.js` + `tests/ontology.test.js`

- [ ] **Step 1: Failing tests**

```js
// append to tests/ontology.test.js
const G = [
  { id: 'a', type: 'work', status: 'done',    blocked: false, seq: 1, sprint: 'hive',   gate: 'v3.9',  repo: ['hive'] },
  { id: 'b', type: 'work', status: 'active',  blocked: true,  seq: 2, sprint: 'gov',    gate: 'gate-k', repo: ['docs'] },
  { id: 'c', type: 'work', status: 'planned', blocked: false, seq: 3, sprint: 'deploy',                 repo: ['site'] },
];

test('groupBy status uses fixed band order, blocked overrides', () => {
  const lanes = O.groupBy(G, 'status').map(l => l.lane);
  assert.deepStrictEqual(lanes, ['done', 'active', 'blocked', 'planned']);
});
test('groupBy repo uses repo[0]', () => {
  assert.deepStrictEqual(O.groupBy(G, 'repo').map(l => l.lane), ['docs', 'hive', 'site']);
});
test('groupBy gate puts gateless items in (ungated)', () => {
  const lanes = O.groupBy(G, 'gate').map(l => l.lane);
  assert.ok(lanes.includes('(ungated)'));
});
```

- [ ] **Step 2: Run; verify fail** — `node --test tests/ontology.test.js` → `O.groupBy is not a function`.

- [ ] **Step 3: Implement**

```js
  var STATUS_LANES = ["done", "active", "blocked", "planned", "future"];
  function laneOf(it, dim) {
    if (dim === "status") return it.blocked ? "blocked" : it.status;
    if (dim === "repo") return (it.repo && it.repo[0]) || "(none)";
    if (dim === "sprint") return it.sprint || "(none)";
    if (dim === "gate") return it.gate || "(ungated)";
    return "(none)";
  }
  function groupBy(items, dim) {
    var map = {}, order = [];
    items.forEach(function (it) {
      var lane = laneOf(it, dim);
      if (!map[lane]) { map[lane] = []; order.push(lane); }
      map[lane].push(it);
    });
    if (dim === "status") order = STATUS_LANES.filter(function (l) { return map[l]; });
    else order.sort();
    return order.map(function (l) { return { lane: l, items: map[l] }; });
  }
```

Add `groupBy: groupBy,` to `api`.

- [ ] **Step 4: Run; verify pass.**
- [ ] **Step 5: Commit** — `git commit -am "feat(arc): groupBy for repo/sprint/status/gate swimlanes"`

---

## Task 4: `visibleDeps` — dependency declutter

**Files:** Modify `compile/assets/civilizationOntology.js` + `tests/ontology.test.js`

- [ ] **Step 1: Failing tests**

```js
// append to tests/ontology.test.js
test('visibleDeps returns nothing when nothing selected', () => {
  assert.deepStrictEqual(O.visibleDeps([{ id: 'b', deps: ['a'] }], null), []);
});
test('visibleDeps returns only edges touching the selection', () => {
  const items = [{ id: 'b', deps: ['a'] }, { id: 'c', deps: ['b'] }, { id: 'd', deps: ['x'] }];
  const e = O.visibleDeps(items, 'b');
  assert.deepStrictEqual(e.sort((p, q) => (p.from + p.to).localeCompare(q.from + q.to)),
    [{ from: 'a', to: 'b' }, { from: 'b', to: 'c' }]);
});
```

- [ ] **Step 2: Run; verify fail.**

- [ ] **Step 3: Implement**

```js
  function visibleDeps(items, selectedId) {
    if (!selectedId) return [];
    var edges = [];
    items.forEach(function (it) {
      (it.deps || []).forEach(function (from) {
        if (it.id === selectedId || from === selectedId) edges.push({ from: from, to: it.id });
      });
    });
    return edges;
  }
```

Add `visibleDeps: visibleDeps,` to `api`.

- [ ] **Step 4: Run; verify pass.**
- [ ] **Step 5: Commit** — `git commit -am "feat(arc): visibleDeps (show deps only for selected item)"`

---

## Task 5: Migrate `civilizationArcData.js` to `items[]`

**Files:** Modify `compile/assets/civilizationArcData.js`; Modify `tests/ontology.test.js`

**Note:** This is a data transform, not new logic. Convert the 5 lists into one `items[]`. Mapping rules:
- Each `phases[]` entry → a `sprint` lane id (keep a `sprints[]` list: `{id,label}` from the old phases). Phases are *not* items.
- Each `markers[]` entry → item `{type:'work', provenance:'reconstructed', status:'done'}` unless it is part of live work (see executionPlan) — most are `done` narrative beats. Set `seq` from the old `x`. `repo` from the marker's domain (map known markers to repos; default `['wiki']`). `sprint` = the phase whose `[start,end)` contains `x`.
- Each `executionPlan.nearTerm`/`complete` entry → item `{type:'work', provenance:'derived'}` with `status` mapped: `done→done`, `active→active`, `blocked→active`+`blocked:true`+`blocked_reason`, `next/planned→planned`, `future→future`. `repo` = split the `surface` string on commas. `gate` from its `gate`/`href`. `seq` placed just right of the relevant phase.
- Each `gates[]` entry → item `{type:'gate'}`, `status` from old `status` (`closed→done`, `candidate→active`, `pending→active`+`blocked:true`). `seq` from `x`.
- Each `risks[]` entry → fold into the item it annotates as `blocked:true`+`note`, OR a `{type:'conflict'}` item if standalone; do NOT emit free-floating past blockers.
- Each `decisions[]` entry → item `{type:'decision', status:'done'}` at its `seq`.
- Add the north-star **Goal** item `{type:'goal', status:'active', seq:0, sprint:'origin', repo:['wiki']}` and link live work via `goal`.

**CRITICAL:** author the data so the settled prefix holds — every item with `seq < deriveNow(items)` is `done`/`active`. That is what makes `validateItems` pass.

- [ ] **Step 1: Add the data-integrity test FIRST (it will fail until migration is done)**

```js
// append to tests/ontology.test.js
const fs = require('node:fs');
const path = require('node:path');

test('migrated civilizationArcData passes the ontology allowlist', () => {
  // load the browser asset in a Node sandbox
  const code = fs.readFileSync(path.join(__dirname, '../compile/assets/civilizationArcData.js'), 'utf8');
  const sandbox = { window: {} };
  new Function('window', code)(sandbox.window);
  const data = sandbox.window.CIVILIZATION_ARC_DATA;
  assert.ok(Array.isArray(data.items), 'data.items must exist');
  const r = O.validateItems(data.items);
  assert.strictEqual(r.ok, true, 'validateItems errors:\n' + r.errors.join('\n'));
});

test('migrated data keeps the narrative beats (reconstructed) and live work (derived)', () => {
  const code = fs.readFileSync(path.join(__dirname, '../compile/assets/civilizationArcData.js'), 'utf8');
  const sandbox = { window: {} };
  new Function('window', code)(sandbox.window);
  const items = sandbox.window.CIVILIZATION_ARC_DATA.items;
  assert.ok(items.filter(i => i.provenance === 'reconstructed').length >= 20, 'keep ~28 narrative beats');
  assert.ok(items.filter(i => i.provenance === 'derived').length >= 10, 'keep executionPlan work');
  assert.ok(items.some(i => i.type === 'goal'), 'north-star Goal present');
});
```

- [ ] **Step 2: Run; verify fail** — `node --test tests/ontology.test.js` → `data.items must exist`.

- [ ] **Step 3: Rewrite `civilizationArcData.js`** — replace `phases/markers/gates/risks/decisions` with `items[]` per the mapping rules above; keep `domain`, `title`, `subtitle`, `explanation`, `executionPlan`, `legendItems`; add `sprints[]` (id+label from old phases). Each item shape:

```js
{ id, type, label, status, blocked: false, blocked_reason: null,
  provenance, seq, repo: [], sprint, gate: null, goal: null,
  deps: [], href: null, note: null }
```

(Author all items by hand from the existing data; this is mechanical. Use the old `dependencies[]` to populate each item's `deps`.)

- [ ] **Step 4: Run; verify pass.** Iterate on the data until `validateItems` is green (fix any item left of "now" that isn't done/active — that is a real data-correctness fix, not a test workaround).

- [ ] **Step 5: Commit** — `git commit -am "feat(arc): migrate arc data to unified items[] (15-type ontology)"`

---

## Task 6: Wire the ontology asset into the build

**Files:** Modify `compile/build_site.py`

- [ ] **Step 1:** In `build()` (around L291), after the existing `copy_asset(...)` calls, add:

```python
    ONTO_VER = copy_asset("civilizationOntology.js")
```

- [ ] **Step 2:** In `page()` and `arc_page()` script injection (where `civilizationArcData.js`/`civilizationArcNav.js` are emitted, ~L229–233 and ~L269–271), add the ontology script **before** the data script:

```python
'<script defer src="civilizationOntology.js?v=%s"></script>' % ONTO_VER
```

(Thread `ONTO_VER` through like `ARC_DATA_VER`.)

- [ ] **Step 3: Run the build** — `python3 compile/build_site.py`
Expected: `built N articles + index + arc -> .../dist`, and `dist/civilizationOntology.js` exists.

- [ ] **Step 4: Commit** — `git commit -am "build(arc): emit civilizationOntology.js asset"`

---

## Task 7: Renderer — derive "now" + render blockers from status

**Files:** Modify `compile/assets/civilizationArcNav.js`

- [ ] **Step 1:** Read `drawCurrent` (L901–918) and `drawRisks` (L871–884).

- [ ] **Step 2:** In `drawCurrent`, replace `mapX(data, data.currentFocus.x)` with the derived frontier:

```js
var nowSeq = window.CivOntology.deriveNow(data.items);
var x = mapX(data, nowSeq);
```

Keep the label, but source it from the frontier item (the highest-seq done/active item) rather than `currentFocus.label`.

- [ ] **Step 3:** Replace free-floating blocker chips: delete the `drawRisks` call from `drawSvg` (L940–968). Render `blocked` as an overlay on the item's own node instead (in the marker/item draw path, add a red ring when `item.blocked`). Blockers no longer float in the past.

- [ ] **Step 4: Verify** — `npm run build && npm run test:dom` (DOM smoke still renders), then load `dist/civilization-arc.html` and confirm the now-line sits at the done/active frontier and there are no past BLOCK chips.

- [ ] **Step 5: Commit** — `git commit -am "feat(arc): status-derived now-line; blockers as node overlay"`

---

## Task 8: Renderer — swimlane grouping toggle (default Status)

**Files:** Modify `compile/assets/civilizationArcNav.js`

- [ ] **Step 1:** Add render state: `state.grouping = state.grouping || 'status';` (default Status).

- [ ] **Step 2:** Replace the lane source in `drawSwimlanes`/`drawPhases` so lanes come from `window.CivOntology.groupBy(data.items, state.grouping)` — one swimlane per returned `{lane, items}` (label = `lane`), and each item is drawn at `y = laneCenter(thatLane)` and `x = mapX(seq)`.

- [ ] **Step 3:** Add a toggle control in `setupSvgInteraction` (near the existing buttons, L1159–1261): a segmented button cycling `status → repo → sprint → gate`, calling `state.grouping = next; drawSvg(root, svg, data);`.

- [ ] **Step 4: Verify** — `npm run build`, open `dist/civilization-arc.html`, click the toggle; confirm the same items regroup into Repo / Sprint / Status / Gate lanes with Status as the initial view.

- [ ] **Step 5: Commit** — `git commit -am "feat(arc): swimlane grouping toggle (status default; repo/sprint/gate)"`

---

## Task 9: Renderer — dependency declutter on selection

**Files:** Modify `compile/assets/civilizationArcNav.js`

- [ ] **Step 1:** Read `drawDependencies` (L671–691).

- [ ] **Step 2:** Replace its edge source with `window.CivOntology.visibleDeps(data.items, state.selectedId)` and draw only those edges. Remove the `state.showDependencies` global-on path (deps are now selection-scoped).

- [ ] **Step 3:** Ensure selecting an item (existing selection path, `updateSelectedPanel`/`isSelected`) triggers a redraw so its deps appear; deselect clears them.

- [ ] **Step 4: Verify** — `npm run build`, open the page, click an item → only its in/out dependency edges show; click empty space → none. The 25-edge spaghetti is gone.

- [ ] **Step 5: Commit** — `git commit -am "feat(arc): dependencies shown only for the selected item"`

---

## Task 10: Invert the smoke test to a fail-closed allowlist + CI

**Files:** Modify `tests/arc-dom-smoke.test.js`; Modify `.github/workflows/ci.yml`

- [ ] **Step 1:** Read `tests/arc-dom-smoke.test.js` (the past-phase validation, ~L54–65 — currently a denylist of `conceptual/designed/unresolved/future`).

- [ ] **Step 2:** Replace that block so it loads `items[]`, computes `deriveNow`, and asserts the **allowlist**: every item with `seq < now` has `status ∈ {done, active}` — reusing `require('../compile/assets/civilizationOntology.js').validateItems`. Assert `validateItems(data.items).ok === true` and print errors on failure.

- [ ] **Step 3:** In `.github/workflows/ci.yml`, after the Python step, add:

```yaml
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - name: Arc ontology + DOM smoke (allowlist, fail-closed)
        run: |
          node --test tests/ontology.test.js
          npm ci
          npm run test:dom
```

- [ ] **Step 4: Verify** — `node --test tests/ontology.test.js && npm run test:dom` pass locally. Temporarily flip one migrated item left of "now" to `planned`; confirm the allowlist FAILS; revert.

- [ ] **Step 5: Commit** — `git commit -am "test(arc): allowlist (fail-closed) past-item check + CI node step"`

---

## Task 11: Full build + browser verification

**Files:** none (verification only)

- [ ] **Step 1: Run the full verify** — `npm run verify` (build + `test:js` + `test:dom` + Playwright `test:browser`).
Expected: build succeeds; all suites pass. Fix any Playwright assertions in `tests/arc-nav.spec.js` that referenced the old `phases/markers/risks` counts — update them to the `items[]`/grouping model (real updates, not skips).

- [ ] **Step 2: Visual check** — serve `dist/` and open `civilization-arc.html`: Status default; toggle to Repo/Sprint/Gate; now-line at the frontier; no past blockers; deps only on selection; the ~28 narrative beats still present (the story).

- [ ] **Step 3: Commit any test updates** — `git commit -am "test(arc): update Playwright suite to items[] model"`

---

## Self-Review (completed at authoring)

- **Spec coverage:** items[] contract (§3) → Tasks 1–5; derived-now + allowlist (§1.5, §4) → Tasks 1,2,7,10; swimlane toggle default Status (§4) → Task 8; dependency declutter + blocker fix (§4) → Tasks 7,9; keep-story (§7.3) → Task 5 integrity test; build/CI wiring → Tasks 6,10. **Deferred (not in this plan, by spec §6):** runtime Projection 2, Update-Now (A), heavy layout + resizable columns + kanban toggle (B2).
- **Placeholders:** none — every code step has runnable code; migration rules are explicit.
- **Type consistency:** `deriveNow`, `validateItems`, `groupBy`, `visibleDeps`, `window.CivOntology`, and the item shape are used identically across tasks.
- **Known follow-up:** the 10-vs-14 invariant count (spec §8.3 [F7]) is a data-authoring input when Invariant items are added — not required for Projection 1's chart, which is work/goal/gate-centric.
