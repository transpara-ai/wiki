---
doc_id: TAI-WIKI-ARC-2B-VISUAL
title: Arc 2b-visual — Now-Panel + Phase Spine, Retire the Six-Mode Engine (TLC Design Packet)
doc_type: design
version: 0.2.0
status: draft
canonical: false
created: 2026-07-03
updated: 2026-07-03
owner: Michael Saucier
steward: Claude (Fable 5)
authority: planning
tlc_stage: design
source_of_intent:
  - transpara-ai/wiki#46 (cc:pr-ready, human-armed 2026-07-03)
  - docs/superpowers/specs/2026-07-01-arc-metrics-redesign-design.md §3–§4 (canonical on main via PR #42)
intake_channel: B (issue-scan; cc:pr-ready human-set)
---

# Arc 2b-visual — TLC Design Packet

> Builds the **visual half** of the Item-2b redesign that PR #45 (metrics half)
> did not ship. The data model and ontology validator are **unchanged** — PR #45's
> criteria rollup, `blocked_reason`, and the `gate-k`/`gate-k-go-live` split
> already feed everything the new view needs. This packet turns spec §3 into a
> buildable contract **against measured live data** (survey 2026-07-03, wiki
> main @ `a1cb326`).

## 1. Survey — measured, not assumed

- Baked `deriveNow` = **14.36**; the frontier item is **`g-5-2` (gate, done,
  sprint `deployment`)**. 121 items: 70 gates, 46 work, 4 decisions, 1 goal.
- 21 items are `active`: 8+1 work (incl. `goal-north-star`, perpetual at seq 0),
  12 gates. The only blocked gate is **`gate-k-go-live`** (planned+blocked,
  reason `gate`, criterion `go-live-revalidation`, seq 14.8, sprint
  `stewardship`).
- Per-phase rollup over `{work, gate}` items (excluding the perpetual goal):
  phases 1–12 (`origin`…`implementation`) roll up **done**; `validation` and
  `deployment` **active**; `stewardship` **active+blocked**. This is the honest
  one-glance picture the spine will render.
- Live overlay: `compile/inflight.py` emits open (`active`) **and ≤30-day
  merged (`done`)** PRs as `type:"work"` items, all tagged `sprint:
  "stewardship"` — by its own comment a **tooltip labeling convenience, not an
  arc-placement claim**. Any item-positional "current phase" rule computed over
  the *merged* set therefore teleports to `stewardship` whenever a PR is open
  or recently merged. The frontier/phase read must anchor to **baked** items.
- The page today also renders two governance-honesty sections **outside** the
  six-mode engine: the progress-evidence snapshot
  (`CIVILIZATION_PROGRESS_EVIDENCE`) and the live-reader correction panel.
  They must survive the deletion.
- `CIVILIZATION_ARC_DATA` still carries `executionPlan` and `legendItems` —
  render-support keys for the retired engine. The data model is pinned
  unchanged, so they become **unread** (residual, §4).

## 2. The contract

### 2.1 File plan (net deletion)

| Action | File | Notes |
|---|---|---|
| DELETE | `compile/assets/civilizationArcNav.js` (1286 ln) | six-mode controller, zoom, tooltip, SVG wiring |
| DELETE | `compile/assets/civilizationArcLayout.js` (194 ln) | SVG geometry engine |
| DELETE | `compile/assets/civilizationArcDraw.js` (402 ln) | SVG draw engine |
| DELETE | `tests/arcLayout.test.js`, `tests/arc-nav.spec.js` | tests of the retired engine |
| ADD | `compile/assets/civilizationArcView.js` | ONE module, isomorphic like the ontology (pure derivations exported for `node --test`; DOM render browser-only); target ≤ ~550 ln |
| ADD | `tests/arcView.test.js` (node --test), `tests/arc-view.spec.js` (Playwright) | |
| REWRITE | `tests/arc-dom-smoke.test.js` | panel/spine/absence assertions; data-contract block kept minus its `executionPlan` assertions (the key is unread by the view — the block asserts the view's actual contract) |
| REWIRE | `compile/build_site.py` `arc_page()` + asset copy list | 4 scripts (ontology, data, progress-evidence, view); static legend emitted by the builder |
| UPDATE | `package.json` (`test:js`, `test:unit` lists), `tests/inc001-render.spec.js` arc-routes block, `compile/assets/style.css` | CSS: add panel/spine/legend styles on the existing custom-property palette (both themes); delete engine-only selectors (`.arc-svg`, `.arc-toolbar`, `.arc-zoom*`, track/marker/tooltip) |
| UNTOUCHED | `civilizationArcData.js`, `civilizationOntology.js`, `civilizationProgressEvidence.js`, `compile/inflight.py`, `wiki/civilization-arc.md` (prose has no engine references — checked) | data model + validator pinned |

### 2.2 Derivations (pure, exported, fail-closed — the heart)

All consume `CivOntology` (`deriveNow`, `rollupCriteria`, `validateItems`,
`mergeInflight`); none re-implement ontology semantics; none read
`executionPlan`/`legendItems`.

- **D1 — `phaseRollup(phaseItems)`**: over the phase's `{work, gate}` items
  (goals excluded — the north-star goal is a perpetual banner at seq 0, not
  positional work; decisions/events likewise demoted per spec §2.2, but they
  are `done` beats and excluding them changes nothing today — the exclusion
  set is **allowlist `{work, gate}`**, the two first-class piece types).
  Measured: the allowlist yields the identical spine picture — all 4
  decisions live in phases that also hold done work/gates.
  **Empty set ⇒ `{status:"future", blocked:false}`** — explicit guard;
  `CivOntology.rollupCriteria([])` returns `done` (its `allDone` seed), which
  here would render an empty phase as complete: the named fail-open lane this
  packet closes. Non-empty ⇒ delegate to `rollupCriteria` verbatim. A phase
  holding only demoted types (measured absent today) renders `future` with a
  0-piece count chip — the spine claims piece status only, and claiming
  nothing beats an all-types fallback, which would reintroduce the
  perpetual-goal poison for goal-only phases.
- **D2 — `currentPhase(bakedItems, sprints)`**: the sprint of the
  **baked** frontier item (argmax seq over `SETTLED` status; ties → the first
  item at the max wins, the same strict-`>` scan `deriveNow` uses, so the two
  derivations can never disagree on the frontier). Anchored to baked items per §1;
  live overlay never moves the phase read. Frontier sprint not present in
  `sprints[]` ⇒ **deny-path**: return `null`; the panel renders an explicit
  "frontier phase unresolved" notice, never a guess (the validator does not
  enforce sprint membership — this is the display-side fail-closed net).
- **D3 — `nextBlockingGate(bakedItems)`** — computed over **baked** items
  only (both the gate candidates and the `deriveNow` frontier it compares
  against), consistent with D2's anchor; live items are always `type:"work"`
  and can move neither read: (1) gates with `blocked === true` → min
  seq (an existing hard stop outranks anything ahead, wherever it sits);
  (2) else `planned` gates with seq > baked `deriveNow` → min seq;
  (3) else `future` gates with seq > now → min seq; (4) else `null` → the
  panel renders an explicit "no blocking gate ahead — frontier open" state.
  Total over the whole domain; no fall-through that renders a healthy default.
  Measured result on live data: **`gate-k-go-live`**.
- **D4 — `activeWork(mergedItems)`**: `type === "work" && status === "active"`
  over the **merged** (baked + inflight, fail-closed `mergeInflight`) set,
  sorted seq descending. Empty ⇒ explicit "no active work items" line.
- **D5 — freshness**: "latest closed" = max ISO `date` among **baked** `done`
  items (existing `latestDated` semantics; merged-PR overlay items carry no
  `date`, but the anchor is explicit anyway); live stamp = the existing fail-closed
  chip states (`live · <generated>` / `live · degraded` / `live ·
  unavailable`) preserved verbatim from the current `loadInflight` behavior.

### 2.3 Render contract (what the page shows)

Builder (`arc_page()`) emits statically: the section shell, the authority-
boundary note (unchanged), the **one-status legend** (4 lifecycle values +
blocked overlay + the line "every status is evidence-derived or stamped"),
and one mount `<div data-civilization-arc data-arc-live="true">`.

`civilizationArcView.js` renders into the mount, **only after
`validateItems(baked)` passes** — invalid data ⇒ a visible `.arc-error`
notice and no partial render (fail loud, never a healthy-looking lie):

1. **Freshness header** — D5 stamps.
2. **Now-panel** — "You are here: <phase label>" (D2) + frontier note
   (`<code> · seq <n> · derived`); column **active now** (D4; each row:
   status dot + blocked ring, code, label, and an **evidence stamp**:
   provenance badge, `ref`/`href` link (safeHref-gated), `date`, `@author` +
   `observed <generated>` for live-overlay rows — a projection of existing
   fields `{provenance, ref, date, href, author}` + the inflight `generated`
   stamp; spec §2.6's `evidence{}` block is NOT in the shipped model and is
   not invented here); column **next gate** (D3; code, label,
   `blocked: <reason>` chip, the acceptance-criteria checklist — per-criterion
   status dot, label, safeHref'd `ref` — with the `blocked_criterion` row
   highlighted, and the rollup line **recomputed via
   `CivOntology.rollupCriteria` at render time**, never echoed from stored
   fields, captioned "fail-closed rollup").
3. **Phase spine** — all `sprints[]` in order; each phase colored by D1 with
   a count chip; blocked ⇒ ring; **collapse ⇔ rollup done** (position never
   collapses an unfinished phase); the D2 phase carries the "now" frontier
   marker (exactly one, or zero + notice on the D2 deny-path).
4. **Ported unchanged**: progress-evidence snapshot + live-reader correction
   panels (same DOM classes), `safeHref` allowlist, live overlay via
   `mergeInflight` with baked-first render (never blank).

Removed with the engine: the six-mode toolbar, zoom, SVG chart, tooltip,
marker detail-on-click. The optional lightweight filter (spec §3 "may
remain") is **not built** — minimum code; the spine is the view.
No new data keys, no network beyond the existing same-origin
`inflight.json` fetch, no external assets, no LLM in the path, both themes
via the existing custom-property palette.

## 3. Acceptance criteria & named tests

| # | Criterion (risk) | Verification — named test |
|---|---|---|
| AC1 | Now-panel renders the current phase, active work with per-piece evidence stamps, and the next blocking gate with its criteria checklist + rollup, all derived from live data functions, never hand-authored (med) | dom-smoke: `now panel names the current phase from baked frontier`, `active-now rows each carry an evidence stamp`, `next gate is gate-k-go-live with criteria checklist and recomputed rollup`; unit: `D3 selects gate-k-go-live on real data` |
| AC2 | Phase spine renders every phase with a fail-closed D1 rollup, exactly one derived frontier marker, done phases collapsed (med) | unit: `phaseRollup empty set is future never done`, `phaseRollup matches rollupCriteria across the status×blocked domain`, `currentPhase anchors to baked frontier under live overlay`, `currentPhase deny-path on unknown sprint`; dom-smoke: `spine collapse tracks the done rollup exactly` (structural: collapsed ⇔ rollup done, every phase) + snapshot anchors (15 phases, frontier on deployment, stewardship blocked ring) |
| AC3 | The six-mode toolbar, zoom, and SVG engine are gone; no parallel layout engine remains (low) | dom-smoke: `retired engine artifacts are absent` (no `.arc-toolbar`, `[data-arc-group]`, `.arc-zoom`, `svg.arc-svg`, `.arc-track-band`); py: `test_build_site_arc.py` asserts the arc page HTML carries the View script + static legend and none of Nav/Layout/Draw |
| AC4 | Net LOC deletion across `civilizationArc*.js` (low) | `git diff --stat` vs main recorded in the PR body (−1882 engine lines vs one new view module); `test:js` checks only the 4 surviving assets |
| AC5 | `npm run verify` green: build, `node --check`, unit, py, dom-smoke, Playwright — incl. rewritten `inc001` arc-routes block and new `arc-view.spec.js` (panel+spine visible on both arc routes and in BOTH themes, legend present, zero console errors) (low) | the verify chain itself |
| AC6 | Fail-closed display: invalid baked items ⇒ `.arc-error` notice, no partial render; degraded/unavailable inflight keeps baked render + honest chip (med) | dom-smoke: `invalid baked data renders the error notice and no panel`, `degraded inflight keeps baked view with honest live chip` |
| AC7 | Governance-honesty panels survive: progress-evidence + live-reader sections render as today; authority-boundary note unchanged (med) | dom-smoke: ported existing assertions for both panels |

Gate satisfied-only-when: AC1–AC7 all green at the reviewed head **and**
CI-equivalent `npm run verify` exits 0. Any unproven criterion ⇒ not satisfied.

## 4. Authorization packet

- **Bounded scope:** the §2.1 file plan, `transpara-ai/wiki` only, branch
  `feat/arc-2b-visual` off main @ `a1cb326`; issue→ready-PR lifecycle only
  (cc:pr-ready arming, 2026-07-03). No merge, no push beyond the PR branch.
- **Forbidden:** any change to `civilizationArcData.js`,
  `civilizationOntology.js`, `civilizationProgressEvidence.js`,
  `inflight.py`, the front page/board, ingestion, other repos; no new data
  keys; no external assets; no LLM in the arc path.
## Appendix — IADA (self-directed, v0.1.0 → v0.2.0)

| # | Finding | Disposition |
|---|---|---|
| I1 | D2 tie-break described as "later item wins, as in deriveNow" — factually wrong twice: `deriveNow`'s strict-`>` scan keeps the FIRST item at the max | FIXED — first-at-max, same scan, derivations cannot disagree |
| I2 | D3 left its item-set ambiguous; merged-set `deriveNow` (14.37) ≠ baked (14.36), so a gate between them would flip selection by call-site | FIXED — D3 pinned to baked items for candidates and frontier |
| I3 | "data-contract block kept" would keep asserting `executionPlan`, pinning a key the view no longer reads | FIXED — block keeps item-contract assertions, drops `executionPlan` |
| I4 | D1's `{work,gate}` allowlist differed from the survey simulation (which excluded goals only) — unverified against decisions | MEASURED — identical spine; decisions-only-phase edge documented with the future+0-chip rationale |
| I5 | D5 latest-closed unanchored (merged set could theoretically carry dated done items later) | FIXED — baked anchor explicit |
| I6 | AC2's spine test as written pinned only a snapshot; the invariant (collapse ⇔ done rollup) is the class | FIXED — structural assertion + snapshot anchors |
| I7 | "both themes" had no named verification | FIXED — AC5 Playwright asserts both themes |

- **Residual risks:** (a) `executionPlan`/`legendItems` remain in the data
  file as dead keys — follow-up data-side cleanup, deliberately out of scope
  (data model pinned); (b) item-level detail-on-click is retired with the
  engine — item `href`s in active-now/criteria rows and the wiki articles
  remain the drill-down path (spec Q3: history links out); (c) the optional
  repo filter is not built (spec allows omission); (d) D2 anchoring to baked
  items means an open PR no longer advances the rendered frontier — the live
  work still shows in active-now with live stamps (honest split: curated arc
  = baked, live overlay = evidence).
