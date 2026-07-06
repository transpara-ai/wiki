---
doc_id: TAI-WIKI-ARC-DATA-DEADKEYS
title: Arc data dead-keys removal — retire executionPlan + legendItems (TLC Factory Order + Design Packet)
doc_type: design
version: 0.1.0
status: draft
canonical: false
created: 2026-07-06
updated: 2026-07-06
owner: Michael Saucier
steward: Claude (Fable 5)
authority: planning
tlc_stage: design
source_of_intent:
  - docs/superpowers/specs/2026-07-01-arc-metrics-redesign-design.md §4 (blob 883e7f50586b12ca38901436bb3af5daeeb37cd5, canonical on main) — "The `executionPlan`, `liveReaderEvidence`, and gate-specific status fields are removed."
  - docs/superpowers/specs/2026-07-03-arc-2b-visual-packet.md §4 residual (a) (blob e275de214eb17b2958de76c5285bcbca94b67649) — "executionPlan/legendItems remain in the data file as dead keys — follow-up data-side cleanup"
  - Michael, in-session 2026-07-06 — "Can you fix the nits you note without my involvement?" — where "the nits" were enumerated one message earlier as exactly this cleanup (item 2 of the remaining-work table)
intake_channel: A (owner-directed session 2026-07-06)
---

# Arc data dead-keys removal — TLC Factory Order + Design Packet

> One governed doc carries both the Factory Order (§1) and the design (§2–§4);
> both are pinned by this file's single blob SHA. Proportionality choice for a
> ~370-line pure-deletion change, recorded here per the mechanical-edit rule:
> this is NOT classified mechanical (it deletes keys from a runtime-loaded data
> file and closes a recorded residual risk), so the full gate chain runs.
> **Human Design Review (stage 6) evidence:** the owner's in-session
> instruction above names this exact change and grants the no-involvement
> lifecycle to a ready PR; stage 12 (merge) remains the owner's backstop.

## 1. Factory Order (FO-WIKI-ARC-DEADKEYS, embedded)

Requirements, each individually verifiable:

- **R1** — `CIVILIZATION_ARC_DATA` in `compile/assets/civilizationArcData.js`
  carries neither an `executionPlan` nor a `legendItems` key.
  *Rationale:* both fed the six-mode engine retired by PR #47; the canonical
  metrics spec §4 already ordered `executionPlan` removed (PR #45 kept it with
  a drift-mirror test as a stopgap); `legendItems` was superseded by the
  static legend the builder emits.
- **R2** — no test, module, or builder references the removed keys except as
  historical prose in specs/plans; the drift-mirror test
  (`executionPlan row statuses mirror canonical item statuses`,
  tests/ontology.test.js) is retired WITH its subject.
  *Rationale:* a test whose subject is deleted either throws (fail-open noise)
  or silently no-ops; neither is honest.
- **R3** — a named regrowth guard prevents the keys from returning.
  *Rationale:* same guard class as the retired-asset regrowth guard in
  `compile/test_build_site_arc.py` (2b-visual AC4): deletion without a guard
  invites silent reintroduction.

Non-goals: no `items[]` change, no ontology/validator change, no view change,
no builder change, no CSS change. The rendered page is byte-identical except
for the smaller data asset.

Constraints: `transpara-ai/wiki` only; branch `feat/arc-data-dead-keys` off
main @ `ca23a85`; lifecycle stops at ready PR (no merge — stage 12 is
Michael's).

## 2. Survey — measured, not assumed (wiki main @ ca23a85)

- Data file blob `697002a4bf3a703a4d7cd1b9eead3e8084fd758b`, 3011 lines.
  `legendItems` spans lines 2645–2658; `executionPlan` spans 2660–3009 (the
  object's final key). Two stale comments (lines ~2314–2315, ~2460–2461) say
  item blocks "mirror the rows in executionPlan.*" — with the key gone these
  comments would lie; they are rewritten to stand alone.
- Full-repo grep for readers: the ONLY live reader is
  `tests/ontology.test.js:266–276` (the drift-mirror test — it would throw
  `TypeError` on `data.executionPlan[section]` after removal, so it retires
  with the key). `tests/ontology.test.js:256` mentions executionPlan only in
  an assertion MESSAGE string while reading `items[]` — the assertion stays,
  its message is reworded. No JS module, no `build_site.py`, no
  `ingest_server.py`, no CSS selector reads either key. Spec/plan prose
  references are historical record and stay untouched.
- `CivOntology.validateItems` validates ITEM keys (allowlist at
  civilizationOntology.js:109); it does not constrain top-level
  `CIVILIZATION_ARC_DATA` keys — removal cannot trip the validator.
- The arc page's authority-boundary note and legend are emitted statically by
  `arc_page()` (2b-visual contract §2.3) — the `executionPlan`
  non-authorization strings and `legendItems` entries feed nothing rendered.

## 3. The contract

| Action | File | Change |
|---|---|---|
| EDIT | `compile/assets/civilizationArcData.js` | delete `legendItems` (2645–2658) + `executionPlan` (2660–3009); rewrite the two stale mirror comments to describe the item blocks without referencing the retired key |
| EDIT | `tests/ontology.test.js` | delete the drift-mirror test (266–276); reword the line-256 assertion message (`'keep executionPlan work'` → `'keep derived worklist items'`); ADD named regrowth guard `data carries no retired render-support keys` asserting `'executionPlan' in d === false` and `'legendItems' in d === false` |
| UNTOUCHED | everything else | items[], ontology, view, builder, server, CSS, specs |

## 4. Acceptance criteria & named tests

| # | Criterion (risk) | Verification — named test |
|---|---|---|
| AC1 | Both keys absent from the loaded data object (low) | unit: `data carries no retired render-support keys` (tests/ontology.test.js) — written FIRST, verified RED at the pre-change tree, GREEN after |
| AC2 | No live reader remains; the drift-mirror test is retired with its subject (low) | procedural: `grep -rn "executionPlan\|legendItems" --include="*.js" --include="*.py"` over `compile/ tests/` returns zero hits post-change (recorded in PR body); the full unit suite passes with the mirror test deleted |
| AC3 | Nothing user-visible changes (low) | `npm run verify` green: build, node --check, unit, py (incl. `test_build_site_arc.py` regrowth guards), dom-smoke, Playwright — the view renders identically from `items[]`/`sprints[]` alone |

Gate satisfied-only-when: AC1–AC3 all green at the reviewed head AND
CI-equivalent `npm run verify` exits 0. Any unproven criterion ⇒ not satisfied.

## 5. Authorization packet

- **Bounded scope:** the §3 file plan, `transpara-ai/wiki` only, branch
  `feat/arc-data-dead-keys` off main @ `ca23a85`; lifecycle ends at ready PR.
- **Forbidden:** any change to `items[]` content, `civilizationOntology.js`,
  `civilizationArcView.js`, `build_site.py`, `ingest_server.py`, CSS, other
  repos; no merge; no push beyond the PR branch.
- **Residual risks:** none new. This arc CLOSES 2b-visual residual (a);
  residuals (b)/(c) of that packet (detail-on-click retired, repo filter
  unbuilt) are design decisions on record, untouched here.
