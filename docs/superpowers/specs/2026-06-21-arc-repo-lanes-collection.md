# Civilization Arc — Repo view: collection grouping + named outside bucket (design)

**Date:** 2026-06-21 · **Branch:** `claude/elegant-jang-3373f3` · **Status:** design, approved by Michael

## 1. Problem / context

The arc's **Repo view** lays out items in lanes by owning repo. Today the canonical set is a flat,
hardcoded list of the 6 dark-factory-topic'd repos (`civilizationOntology.js` `REPO_CANON =
["agent","docs","eventgraph","hive","site","work"]`); every other repo — and every repo-less item —
collapses into a single generic `(other)` lane. With the current data, `(other)` is dominated by the 24
`civilization-wiki` items (civ-wiki was never canonical).

Two problems: (a) the collection is incomplete — it omits the civilization repos; (b) `(other)` hides
*which* repo/object an item belongs to.

## 2. Goals / non-goals

**Goals**
- Expand the collection to **8 repos**, conceptually grouped: **Civilization** (the 6 operational repos) +
  **Governance** (the 2 civilization repos).
- Replace the generic `(other)` bucket with **named lanes** per actual outside repo/object.
- Add a **visual marker** (group-header rows) separating the groups, and an outside-collection section
  that appears only when populated.

**Non-goals**
- No change to other group dimensions (status / sprint / gate / actor).
- No GitHub repo-topic changes (civ-wiki / civ-operation stay un-topic'd; the collection is now a curated
  code list, intentionally decoupled from the live `dark-factory` topic query).
- No new live/network behavior; the data + build stay static and air-gap-safe.

## 3. Design

### 3.1 Collection model

Replace the flat `REPO_CANON` with an **ordered group structure**, and derive `REPO_CANON` from it:

```js
// All 8 repos are the Transpara-AI Civilization. The two display groups are:
//   "civilization" = the operational repos (agent…work)
//   "governance"   = the civilization-wiki/operation meta-layer OVER the civilization
//     (note: the repos NAMED civilization-* live in the GOVERNANCE group, by design —
//      do not "fix" this to match repo names.)
// Curated list — intentionally NOT the live `dark-factory` topic query (which returns only the 6).
var REPO_GROUPS = [
  { key: "civilization", label: "Civilization",
    repos: ["agent", "docs", "eventgraph", "hive", "site", "work"] },
  { key: "governance",   label: "Governance",
    repos: ["civilization-wiki", "civilization-operation"] },
];
var REPO_CANON = REPO_GROUPS.reduce(function (a, g) { return a.concat(g.repos); }, []);
```

Within-group order is **explicit** (the array order), not auto-sorted: `civilization-wiki` (24 items)
leads `civilization-operation` (0).

### 3.2 `groupByRepo` behavior

Returns an **ordered** array of lane objects, each tagged with its group:

```
{ lane: <repoName | "(no repo)">, items: [...],
  group: "civilization" | "governance" | "outside", groupLabel: <display label> }
```

Algorithm:
1. **Canonical lanes** — for each group, for each repo in `group.repos` (in order): always emit a lane
   (even empty), tagged with the group. An item appears in **each** canonical lane it belongs to
   (multi-membership preserved; dedupe repeated repos within one item).
2. **Outside lanes** — for each item, for each of its repos **not** in `REPO_CANON`: add to a named
   outside lane created on demand (keyed by repo name), `group:"outside"`. A **repo-less** item
   (`repo:[]`) goes to a `"(no repo)"` outside lane. Outside repos are multi-membership too. An item that
   is *partly* canonical and *partly* outside (e.g. `["docs","ghost"]`) appears in **both** the `docs`
   lane and the `ghost` outside lane.
3. **Ordering** — `civilization` group lanes, then `governance` group lanes, then (only if any outside
   lane is non-empty) outside lanes alphabetically by repo with `"(no repo)"` last.
4. The **outside group is omitted entirely when empty** (no outside lanes, no outside marker). Canonical
   lanes are always shown (the existing "complete enumeration" philosophy, scoped to the curated 8).

### 3.3 Marker rendering — group-header rows

When the renderer iterates lanes and `lane.group` differs from the previous lane's group, it emits a
**group-header row**: the `groupLabel` (CSS-uppercased) in the gutter, styled as a faint section label
distinct from the per-repo `arc-subrow-label`. Headers: `CIVILIZATION`, `GOVERNANCE`, and
`OUTSIDE COLLECTION` (only when the outside group is present).

- `civilizationArcLayout.js` accounts for header rows in vertical layout (each adds a small fixed height
  ahead of its group's first lane) so lanes don't overlap.
- `civilizationArcDraw.js` draws the header text + an optional hairline. A new `style.css` rule
  (`.arc-group-header`) provides the faint, uppercased, letter-spaced treatment in both themes.
- Other dimensions emit lanes without `group`, so **no header is drawn** for status/sprint/gate/actor.

### 3.4 Invariants (fail-closed — per the existing allowlist-not-denylist note)

- **No item is ever silently dropped.** Every item lands in ≥1 lane. Outside/repo-less items are *named*,
  never discarded. This is the load-bearing safety property; it is tested over the whole input domain
  (canonical, off-collection, mixed, repo-less), not just the happy path.
- Canonical membership is an **allowlist** (`REPO_CANON.indexOf(r) !== -1`); anything not on it routes to a
  named outside lane — the permissive "canonical" branch is the explicitly-proven one.

## 4. Files touched

| File | Change |
|---|---|
| `compile/assets/civilizationOntology.js` | `REPO_GROUPS` + derived `REPO_CANON`; rewrite `groupByRepo` (group-tagged lanes, named outside lanes, repo-less `(no repo)`, fail-closed); fix stale "resolved live / dark-factory topic" comment |
| `compile/assets/civilizationArcLayout.js` | reserve vertical space for group-header rows; pass group boundaries to draw |
| `compile/assets/civilizationArcDraw.js` | render group-header rows (label + hairline) on group change |
| `compile/assets/style.css` | `.arc-group-header` treatment (light + dark) |
| `tests/ontology.test.js` | grouping/tagging, civ-wiki + civ-operation lanes, outside-naming, **fail-closed no-drop over full domain** |
| `tests/arc-dom-smoke.test.js` | repo view renders `CIVILIZATION` + `GOVERNANCE` headers, 8 lanes, **no `(other)` lane** |

## 5. Testing

**Unit (`ontology.test.js`):**
- `REPO_CANON` = union of the two groups (8); group labels are `Civilization` / `Governance`.
- `groupByRepo(realItems)`: emits exactly the 8 canonical lanes in group order; `civilization-wiki` lane
  non-empty, `civilization-operation` lane present + empty; **no `(other)` / no outside group**.
- Multi-membership: an item in `["work","civilization-wiki"]` appears in both lanes.
- **Fail-closed domain sweep**: synthetic items — `["ghost-repo"]` → named `ghost-repo` outside lane
  (group `outside`); `[]` → `"(no repo)"` lane; `["docs","ghost-repo"]` → in **both** `docs` and
  `ghost-repo`. Assert: union of all lane memberships covers every input item id (no drops).

**DOM smoke (`arc-dom-smoke.test.js`):** switch to repo view; assert two `.arc-group-header`s
(`CIVILIZATION`, `GOVERNANCE`), 8 repo sub-rows, zero `(other)` labels.

**Full gate:** `npm run test:js`, `test:unit`, `test:dom`, and `python3 compile/build_site.py` all green.

## 6. Risks

- **Lane return-shape change** is additive (`group`/`groupLabel` added; `lane`/`items` unchanged) — existing
  consumers reading `.lane`/`.items` keep working. Verified by the DOM smoke + build.
- **Vertical space**: 2–3 header rows grow the repo view slightly; acceptable, and the view already
  scrolls/zooms.
- **Stale comment / mental model**: the curated list now diverges from the `dark-factory` topic; the code
  comment documents this explicitly to prevent a future "sync to topic" regression.

## 7. Out of scope (explicit)
- GitHub repo topics; live data; the deferred Tier-1 date backfill (separate, queued next per its own
  scoping report `2026-06-21-civilization-arc-date-ownership.md`).
