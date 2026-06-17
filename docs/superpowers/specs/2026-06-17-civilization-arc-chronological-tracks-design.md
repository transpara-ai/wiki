# Civilization Arc — Chronological Tracks (Projection 1, renderer v2) — Design Spec

**Status:** draft v0.1 · **Date:** 2026-06-17 · **Owner:** Michael Saucier · **Authority:** planning (proposal, pending review) · **Repo/branch:** transpara-ai/civilization-wiki @ claude/elegant-swanson-965269

## 0. Context — why this exists

This redesigns **only the Projection-1 read-view renderer**. The data model and ontology contract are kept as-is.

- The ontology, the validated `items[]` model (109 items incl. 59 gates across families), and the derivation contract were locked in `docs/superpowers/specs/2026-06-16-civilization-ontology-design.md` and built in commits up to `80d29d4`. Those stay.
- The first renderer attempt (status swimlanes → vertical sub-lane packing → horizontal fit-to-width) failed: it crammed 109 items into lanes, was not responsive (boxed at 1220px, no resize reflow), and — in the "narrative arc" exploration — used a **decorative y-axis that encoded nothing**. Reviewed three directions with the owner; **Direction C (chronological tracks, accuracy-first)** was chosen.
- **This supersedes the renderer tasks (T7–T11) of `docs/superpowers/plans/2026-06-16-civilization-arc-projection-1.md`.** The data/contract tasks (T1–T6) remain done. A fresh implementation plan will be written from this spec.

## 1. Goal

An **accurate, responsive, and legible** chronological view of the civilization's construction: a real development-time x-axis, a few semantic tracks (y = category), every item at its true position, the full gate landscape visible, the live worklist on its own track, and density managed by **collapse + zoom** rather than by cramming or shrinking.

## 2. Axes — both carry meaning (the y-axis fix)

- **x = development sequence / time.** Driven by each item's `seq`, rendered left→right with era labels (Feb genesis … now … future). Monotonic and meaningful.
- **y = the track / category** an item belongs to (construction arc · gates [by family] · worklist). Categorical and meaningful. **There is no decorative vertical dimension** — nothing about a marker's height is arbitrary.

## 3. Tracks (the y categories)

Each track is a labeled, **collapsible** horizontal band. Within a track items sit at their true `seq` (x).

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

- **Hover** a marker → tooltip (code + label).
- **Click** a marker → **detail panel**: full label, status, the track + gate-family it belongs to, note, and a link to its wiki article. Click empty space → clear.
- **Collapse / expand** any track (and the gate family sub-rows).
- **Zoom / pan** the timeline — zoom into a time range (e.g. the future-gate cluster), fit-all to reset.
- A persistent **"now / current focus" panel**: current gate (Gate-K), its blocker (N5), and a near-term worklist summary.
- *(Optional, phase 2)* selecting an item reveals its dependencies (`CivOntology.visibleDeps`) as faint connectors.

## 6. Responsiveness

- **Full width.** The timeline uses the entire viewport width; the Feb→now span (most done work) gets the bulk of the room, the future region sits on the right.
- **Reflow on resize** via `ResizeObserver` / debounced `resize` — the layout recomputes for the new width (the v1 renderer never did this).
- **Density** is handled by collapsing tracks and zooming. The ~37 future deployment gates cluster on the right — but that is now *accurate* (they genuinely are near-future), and collapsible/zoomable rather than a layout artifact. If markers exceed the width at a given zoom, the **chart frame** scrolls horizontally — never the page.
- **Mobile / narrow:** tracks stack; gate sub-rows collapse by default; controls wrap; the timeline scrolls inside its frame.

## 7. Architecture — small focused modules (not one 1500-line file)

**Kept (the validated contract — do not rewrite):** `compile/assets/civilizationArcData.js` (`items[]`, `executionPlan`, `sprints`, gate `family`), `compile/assets/civilizationOntology.js` (`deriveNow`, `validateItems`, `groupBy`, `visibleDeps`, `STATUS_ORDER`, `GATE_FAMILIES`), and their tests (`tests/ontology.test.js`). The renderer reads **only** this contract, preserving the forward-compat guarantee (spec §3 of the ontology doc).

**Rebuilt:** the rotted ~1500-line `civilizationArcNav.js` is decomposed into focused browser modules (vanilla IIFE, no build step, matching existing assets; each ≈ ≤300 lines, one purpose):

- `arcLayout` — pure geometry: time-scale (`seq → x`), track + sub-row → y, marker placement, collapse-aware heights, content width. No DOM. Unit-tested.
- `arcTracks` — track bands, gutter labels, chevrons, family sub-rows.
- `arcMarkers` — marker rendering by type/status (beats, gates, worklist bars), blocker accent.
- `arcAxis` — the time axis (era labels) + now-line.
- `arcInteraction` — hover/select/collapse/zoom/pan + render state.
- `arcPanels` — the now/focus panel and the detail panel.
- `arcResponsive` — resize observer → relayout.
- `civilizationArcNav.js` becomes a thin composition root wiring these together.

(Module names are indicative; the plan finalizes the split. The key constraint: each unit has one purpose, a clear interface, and is testable in isolation.)

## 8. Data — no new data required

Every item already carries `seq, status, type, repo, sprint, gate, family, code, provenance, deps, href, note`, and `executionPlan` holds the worklist. Sufficient. Two small, optional tuning passes (not blockers):
- map `seq` ranges → era labels (Feb / Mar / … / now / future) for the axis;
- optionally even out `seq` spacing for a nicer time distribution.

Precise calendar dates are **not** introduced — `seq` + era labels are the timeline (much of the early history is reconstructed, so exact dates would be fake precision).

## 9. Testing

- **`arcLayout` (pure):** unit tests for time-scale mapping, track/sub-row assignment, no within-sub-row overlap at a given width, and that collapsing a track reduces height.
- **DOM smoke (jsdom):** tracks render; markers appear in `seq` order; the now-line sits at the frontier; the four gate family sub-rows are present; collapse toggles height; `validateItems(items).ok`; codes unique.
- **Contract:** `tests/ontology.test.js` stays green (unchanged).
- **CI:** a Node step runs the unit + DOM tests (carries over the intent of the old T10 CI task).

## 10. Out of scope (deferred)

- Animation / transition polish.
- Projection 2 (runtime view).
- Real calendar dates (use `seq` + era labels).
- Dependency-graph exploration beyond the optional selection reveal.

## 11. Supersedes

The renderer tasks **T7–T11** of `docs/superpowers/plans/2026-06-16-civilization-arc-projection-1.md`. Data/contract tasks **T1–T6** remain done. The next step is a fresh implementation plan derived from this spec.
