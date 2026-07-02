---
doc_id: TAI-WIKI-ARC-METRICS
title: Arc Metrics Redesign — TLC Design Packet (Item 2b)
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
  - docs/superpowers/specs/2026-07-01-arc-metrics-redesign-design.md (canonical on main via PR #42)
  - operator directive 2026-07-02 — program-level AuthorityDecision (Open Brain marker wiki-refactor-overnight-GO)
intake_channel: A (human request)
---

# Arc Metrics Redesign — TLC Design Packet (Item 2b)

> Refines the canonical Item-2b spec into a buildable contract **against the
> post-refit codebase**. Live-state survey (2026-07-03): the unified `items[]`
> model, the single `STATUS_ORDER` lifecycle, blocked-as-overlay rendering, and
> the **derived** `deriveNow` frontier already exist — the July-1 diagnosis
> predates the institutional-substrate refit. What remains is exactly:

## 1. The remaining delta (surveyed, not assumed)

1. **The Gate-K smoking gun still lives** (`civilizationArcData.js` ~line 669):
   `status:"done"` + `boundary_status:"pre-live-closed-go-live-blocked"` +
   `go_live_revalidation:"blocked"` — a fail-open render (done/green while a
   real acceptance scope is unmet).
2. **Parallel-status remnants**: `boundary_status`, `go_live_revalidation`
   (Gate-K only), plus 4 items carrying `evidence_state` and
   `freshness_state` as unvalidated pass-through facets.
3. **Validator gaps** (`civilizationOntology.js`): no item-key **allowlist**
   (unknown fields pass silently — the exact lane parallel statuses snuck
   through); gates carry no `criteria[]`; no `blocked_reason` enum; no
   derived-rollup equality check.

## 2. The contract

### 2.1 Gates carry criteria; gate status is a validated fail-closed rollup
- Gate items gain `criteria: [{id, label, status, blocked, blocked_reason, blocked_criterion?, ref?}]` (per the canonical spec §2.4).
- Rollup (validated, not trusted): lifecycle `done` **only if every** criterion is `done`; `active` if any criterion `active`; else `planned`/`future`. Overlay: `blocked: true` propagates if any criterion carries it; `blocked_reason` stays **enum** `{gate, resource, authority, recovery, dependency}`; `blocked_criterion` names the criterion id.
- The stored gate `status`/`blocked` **must equal** the rollup — mismatch is a validation error (derived, fail-closed; the data file may cache the value but can never contradict it).
- **Gate-K corrected**: criteria = `prelive-closeout` (done, waiver `docs#138`) + `go-live-revalidation` (planned, blocked, reason `gate`). Rollup ⇒ `status: planned, blocked: true, blocked_reason: "gate", blocked_criterion: "go-live-revalidation"`. `boundary_status`/`go_live_revalidation` fields deleted; the prose note stays as narrative, no longer load-bearing. The **derived frontier moves automatically** (`deriveNow` = max settled seq; Gate-K at 13.9 stops being settled, so `now` recedes to the previous settled item and Gate-K renders ahead of the frontier in the blocked lane — the honest picture).
- Backfill: every other `type:"gate"` item gets a single criterion mirroring its current settled state (`{id:"closeout", status:<current>, ...}`) — no invented history, and the rollup equality holds trivially.

### 2.2 Ontology amendments (allowlisted facets, not deletions)
- `evidence_basis ∈ {source_recorded, superseded, corrected}` (renames `evidence_state`) and `freshness ∈ {fixture, live}` (renames `freshness_state`) become **validated ontology facets**, permitted only on items that carry `source_refs`. Unknown values fail validation.

### 2.3 Validator tightening (deny-by-default)
- **Item-key allowlist**: every item key must be in the schema set; an unknown key is a validation **error** (the lane the parallel statuses used is closed for the whole class, not the two instances).
- `blocked_reason` only on `blocked: true` items and enum-valued; `blocked_criterion` only alongside `blocked_reason` on gates.
- Every `type:"gate"` item must carry non-empty `criteria[]`; criterion statuses use the same single lifecycle; rollup equality enforced (2.1).
- Existing rules retained (sprint refs, date rules, past-items-settled, provenance enum).

### 2.4 Wiring
- `CivOntology.validateItems` remains the single validator; the arc unit tests (`tests/ontology.test.js`, `tests/arcLayout.test.js`) gain cases for every new rule **and the real data must pass** (`npm run test:unit` + `test:js` + DOM smoke stay green).
- Renderer: no new lanes needed — `STATUS_LANES` already renders `blocked`; gate detail popovers gain a criteria list (small, data-driven addition in `civilizationArcNav.js`/draw path only if already rendering notes; otherwise deferred — the model is the point, not new chrome).

## 3. Acceptance criteria & named tests (node --test, tests/ontology.test.js unless noted)

| # | Criterion | Named test |
|---|---|---|
| AC1 | unknown item key ⇒ validation error (whole-class lane closed) | `unknown item keys are rejected` |
| AC2 | a gate without `criteria[]` ⇒ error; criterion statuses validated | `gates require criteria` |
| AC3 | stored gate status/blocked must equal the fail-closed rollup; every mismatch combination over the criterion-state domain is rejected (incl. unknown/absent ⇒ not done) | `gate rollup equality is enforced across the domain` |
| AC4 | `blocked_reason` enum + only-on-blocked + `blocked_criterion` pairing rules | `blocked overlay facets are validated` |
| AC5 | `evidence_basis`/`freshness` validated enums, only with `source_refs`; old field names rejected (AC1 covers via allowlist; explicit negative case kept) | `evidence facets are validated` |
| AC6 | the shipped `CIVILIZATION_ARC_DATA` passes the tightened validator; Gate-K derives `planned+blocked` and the frontier recedes accordingly | `real arc data passes and Gate-K is honest` |
| AC7 | no parallel-status field remains anywhere in the data (grep-level regression) | `parallel status vocabulary is gone` (python: extend `compile/test_build_site_*` arc check or js test reading the raw file) |
| AC8 | site build + arc DOM smoke stay green (renderer unaffected by the model change) | existing `test:js`, `test:unit`, `test:dom` suites |

Gate: AC1–AC8 green + CI-equivalent verify green. Any unproven criterion ⇒ not satisfied.

## 4. Authorization packet
- **Bounded scope:** `compile/assets/civilizationArcData.js`, `compile/assets/civilizationOntology.js`, arc render assets only if criteria display is trivial, `tests/ontology.test.js` (+ sibling arc tests as needed) — **transpara-ai/wiki only**.
- **Authority:** operator directive 2026-07-02 (marker `wiki-refactor-overnight-GO`); merge-when-green per the program grant.
- **Forbidden:** front page/board surfaces, ingest machinery, any status semantics beyond the canonical spec, other repos.
- **Residual risks:** (a) Gate-K's corrected state changes the visible frontier — that is the *point* (fail-legible), but it is a visible behavior change the owner reviews live; (b) criteria backfill for historical gates is single-criterion minimal — richer criteria can be authored later without schema change; (c) `blocked_criterion` is this packet's concretization of the spec's "separate field/evidence pointer" — one-line rename if the owner prefers another.

## Appendix — IADA (self-directed, v0.2.0)
| # | Finding | Disposition |
|---|---|---|
| I1 | validating rollup equality only for Gate-K would be instance-fixing | **FIXED in design** — AC3 runs the whole criterion-state domain; AC1 closes the unknown-key class |
| I2 | deleting `evidence_state` data would lose correction-lifecycle truth | **FIXED** — §2.2 amendment path (validated facets), per the canonical spec's own instruction |
| I3 | frontier recession could strand `planned` items left of `now` | checked: `deriveNow` recomputes from settled items and the past-items-settled rule re-validates; AC6 asserts the real data passes post-change |
