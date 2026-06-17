# Civilization Arc — Chronological Tracks (Projection 1, renderer v2) — Design Spec

**Status:** draft v0.2 · **Date:** 2026-06-17 · **Owner:** Michael Saucier · **Authority:** planning (proposal, pending review) · **Repo/branch:** transpara-ai/civilization-wiki @ claude/elegant-swanson-965269

> **v0.2 (post-T5 visual review):** revises the x-axis encoding (§2), tooltip content (§5), responsiveness guardrails (§6), and data stance (§8). See §12 for the revision history and rationale.

## 0. Context — why this exists

This redesigns **only the Projection-1 read-view renderer**. The data model and ontology contract are kept as-is.

- The ontology, the validated `items[]` model (109 items incl. 59 gates across families), and the derivation contract were locked in `docs/superpowers/specs/2026-06-16-civilization-ontology-design.md` and built in commits up to `80d29d4`. Those stay.
- The first renderer attempt (status swimlanes → vertical sub-lane packing → horizontal fit-to-width) failed: it crammed 109 items into lanes, was not responsive (boxed at 1220px, no resize reflow), and — in the "narrative arc" exploration — used a **decorative y-axis that encoded nothing**. Reviewed three directions with the owner; **Direction C (chronological tracks, accuracy-first)** was chosen.
- **This supersedes the renderer tasks (T7–T11) of `docs/superpowers/plans/2026-06-16-civilization-arc-projection-1.md`.** The data/contract tasks (T1–T6) remain done. A fresh implementation plan will be written from this spec.

## 1. Goal

An **accurate, responsive, and legible** chronological view of the civilization's construction: a real development-**order** x-axis (ordinal — §2), a few semantic tracks (y = category), every item at its true position, the full gate landscape visible, the live worklist on its own track, and density managed by **collapse + zoom** rather than by cramming or shrinking.

## 2. Axes — both carry meaning (the y-axis fix)

- **x = ordinal position in the development/dependency order (v0.2).** Items are placed at their **rank among the distinct `seq` values**, spaced **equidistantly** — *not* proportional to `seq` magnitude. Consecutive distinct positions are the same width apart regardless of their numeric `seq` gap; items sharing a `seq` share an x-column (cross-track vertical alignment is preserved). This deliberately replaces v0.1's `seq`-proportional scale: the data clusters **45 of 109 items at `seq ≈ 14`**, so a magnitude scale produced large empty early stretches (no signal) and an unreadable pile-up at "now". Rank spacing allocates width by *item count*, dissolving both pathologies at once. The x-axis encodes **order**, which is real; it does **not** encode elapsed calendar time, which the data does not contain.
- **y = the track / category** an item belongs to (construction arc · gates [by family] · worklist). Categorical and meaningful. **There is no decorative vertical dimension** — nothing about a marker's height is arbitrary.
- **Axis annotation = sprint start-ticks, not months or bands (v0.2).** The v0.1 era labels (Feb/Mar/Apr/May/Jun·now/future) implied a calendar the data lacks and are **removed**. Sprints **cannot** be drawn as contiguous bands: they overlap in `seq` (validation 10.55–13.40, deployment 12.75–14.52, stewardship 13.90–14.90 ran concurrently; artifact-dashboard 8.34–8.90 nests inside governance 7.18–9.10). Instead, each of the **15 `sprints`** gets a small **start-tick** at its first item's x (its minimum ordinal rank) — an abbreviated/rotated label marking where that phase *began*, with no span claim. The full per-item sprint stays in the tooltip (§5). The **now-line** stays at `CivOntology.deriveNow(items)`, mapped through the rank scale.

## 3. Tracks (the y categories)

Each track is a labeled, **collapsible** horizontal band. Within a track items sit in `seq` order (x = ordinal rank, §2).

1. **Construction arc** — the ~28 reconstructed narrative beats (`provenance: reconstructed`, `type: work`) as points along the timeline. The story spine.
2. **Gates** — the full 59-gate landscape as **family sub-rows**, each a thin row with markers at `seq`, colored by status:
   - v3.9 milestones (A–J)
   - Deployment register (G-0…G-8.4)
   - v4.0 (K/L)
   - Release & security gates (v3.9)
3. **Worklist** — the live `executionPlan`: near-term **N1–N7** and delivery route **C1–C10** as bars/markers at `seq`, status-colored. N5 (Gate-K closeout) sits at the now-line, blocked.

Decisions render as small markers on the construction track (or fold into the detail panel) — not a separate track. Default expansion: all tracks expanded on desktop; the deep deployment-register sub-row is collapsible (and collapsed by default on narrow screens).

## 4. Now-line, status, frontier

- A vertical **now-line** at `CivOntology.deriveNow(items)` — the frontier (gate-k, seq 13.9) — with a "now · <frontier label>" tag.
- **Status by color:** done / active / blocked / planned / future, one consistent palette; blocked carries a red accent. The settled prefix (done/active) sits left of now, planned/future to the right — the allowlist invariant is visible, not just enforced.

## 5. Interaction

- **Hover / focus** a marker → tooltip (v0.2, enriched): **type · status** eyebrow, label, code, **sprint name**, **ordinal position** ("step N of 109"), the item's **real date if one exists** (no fabricated dates — most items have none yet; see §8), provenance, and a link to its wiki article.
- **Click** a marker → **detail panel**: full label, status, the track + gate-family it belongs to, note, and a link to its wiki article. Click empty space → clear.
- **Collapse / expand** any track (and the gate family sub-rows).
- **Zoom / pan** the timeline — zoom into a time range (e.g. the future-gate cluster), fit-all to reset.
- A persistent **"now / current focus" panel**: current gate (Gate-K), its blocker (N5), and a near-term worklist summary.
- *(Optional, phase 2)* selecting an item reveals its dependencies (`CivOntology.visibleDeps`) as faint connectors.

## 6. Responsiveness

- **Full width.** The timeline uses the entire viewport width; the Feb→now span (most done work) gets the bulk of the room, the future region sits on the right.
- **Reflow on resize** via `ResizeObserver` / debounced `resize` — the layout recomputes for the new width. *(v0.2: this was specified in v0.1 but is **not built at the T5 checkpoint** — the deployed page does not reflow and collapses in a wide/short window. It is now a required fix.)*
- **Density** is handled by collapsing tracks and zooming. With ordinal spacing (§2) markers are evenly distributed, so **no region is intrinsically crammed** (the v0.1 "future gates cluster on the right" was a magnitude-scale artifact, now gone).
- **Legibility guardrails (v0.2).** A **minimum per-column width**: if the ordinal columns can't all fit at that minimum, the **chart frame scrolls horizontally** (never the page) rather than overlapping markers. **Minimum track/row heights** so a wide-but-short window cannot compress the chart into an unreadable sliver (the failure in the T5 review screenshot). The **gutter labels** (the existing 168px `GEOM.gutter`) render at a size/contrast that stays legible on reflow — fixing the unreadable track names reported in review.
- **Mobile / narrow:** tracks stack; gate sub-rows collapse by default; controls wrap; the timeline scrolls inside its frame.

## 7. Architecture — small focused modules (not one 1500-line file)

**Kept (the validated contract — do not rewrite):** `compile/assets/civilizationArcData.js` (`items[]`, `executionPlan`, `sprints`, gate `family`), `compile/assets/civilizationOntology.js` (`deriveNow`, `validateItems`, `groupBy`, `visibleDeps`, `STATUS_ORDER`, `GATE_FAMILIES`), and their tests (`tests/ontology.test.js`). The renderer reads **only** this contract, preserving the forward-compat guarantee (spec §3 of the ontology doc).

**Rebuilt:** the rotted ~1500-line `civilizationArcNav.js` is decomposed into focused browser modules (vanilla IIFE, no build step, matching existing assets; each ≈ ≤300 lines, one purpose):

- `arcLayout` — pure geometry: time-scale (`seq → x`), track + sub-row → y, marker placement, collapse-aware heights, content width. No DOM. Unit-tested.
- `arcTracks` — track bands, gutter labels, chevrons, family sub-rows.
- `arcMarkers` — marker rendering by type/status (beats, gates, worklist bars), blocker accent.
- `arcAxis` — the axis (**sprint-band labels**, §2) + now-line.
- `arcInteraction` — hover/select/collapse/zoom/pan + render state.
- `arcPanels` — the now/focus panel and the detail panel.
- `arcResponsive` — resize observer → relayout.
- `civilizationArcNav.js` becomes a thin composition root wiring these together.

(Module names are indicative; the plan finalizes the split. The key constraint: each unit has one purpose, a clear interface, and is testable in isolation.)

## 8. Data — no new data required

Every item already carries `seq, status, type, repo, sprint, gate, family, code, provenance, deps, href, note`, and `executionPlan` holds the worklist. Sufficient for v0.2:
- **(v0.2, decided)** v0.1's optional "even out `seq` spacing" tuning pass is now the **ordinal-rank scale** in §2 — done in geometry, no data edit needed.
- **(v0.2, decided)** v0.1's "map `seq` → era/month labels" pass is **dropped** in favor of **sprint bands** (§2) — `sprints` already exists in the data.

Precise calendar dates remain **not** introduced into the axis (much of the early history is reconstructed, so exact dates would be fake precision). Tooltips (§5) show a **real date only when the item already has one** (~2 items today). Sourcing true ISO dates for the rest from git/PR history is a **separate, deferred follow-up** (see §10) and must not block the renderer fixes.

## 9. Testing

- **`arcLayout` (pure):** unit tests for time-scale mapping, track/sub-row assignment, no within-sub-row overlap at a given width, and that collapsing a track reduces height.
- **DOM smoke (jsdom):** tracks render; markers appear in `seq` order; the now-line sits at the frontier; the four gate family sub-rows are present; collapse toggles height; `validateItems(items).ok`; codes unique.
- **Contract:** `tests/ontology.test.js` stays green (unchanged).
- **CI:** a Node step runs the unit + DOM tests (carries over the intent of the old T10 CI task).

## 10. Out of scope (deferred)

- Animation / transition polish.
- Projection 2 (runtime view).
- Real calendar dates on the **axis** (the axis is ordinal order + sprint bands; dates would be fake precision).
- **Date backfill (deferred follow-up — not this plan):** sourcing true ISO timestamps for items from git/PR history to populate tooltips (§5). Tracked separately.
- Dependency-graph exploration beyond the optional selection reveal.

## 11. Supersedes

The renderer tasks **T7–T11** of `docs/superpowers/plans/2026-06-16-civilization-arc-projection-1.md`. Data/contract tasks **T1–T6** remain done. The next step is a fresh implementation plan derived from this spec.

## 12. Revision history

- **v0.2 — 2026-06-17 (post-T5 visual review with the owner).** The T5 checkpoint shipped and was reviewed against the live page. Three findings drove this revision:
  1. **Axis encoding** — the `seq`-proportional x-scale (with month/era labels) read as calendar time the data doesn't have; gaps carried no signal and "now" was an unreadable 45-item pile-up. → §2 now specifies **ordinal-rank spacing** and **sprint start-tick** annotation; timestamps move into the tooltip (§5). Diagnosis confirmed live: 102 distinct `seq` values, 45 items at `seq ≈ 14`, no `date` field, era labels placed at fixed `seq` positions. (Sprint *bands* were considered but rejected during planning: sprints overlap in `seq` — validation/deployment/stewardship ran concurrently — so they can't partition the axis; **start-ticks** mark phase starts without a false span claim.)
  2. **Responsiveness** — the deployed page does not reflow on resize (v0.1 §6 specified it, but the T5 build didn't implement it) and collapses in a wide/short window. → §6 reaffirms `ResizeObserver` reflow and adds **min-column-width / horizontal-scroll** and **min-height** guardrails.
  3. **Track-label legibility** — the gutter labels are unreadable. → §6 requires legible gutter labels; the 168px `GEOM.gutter` already exists, so this is a styling fix.
- **v0.1 — 2026-06-17.** Initial Direction-C (chronological tracks) design.
