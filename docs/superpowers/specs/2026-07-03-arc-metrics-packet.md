---
doc_id: TAI-WIKI-ARC-METRICS
title: Arc Metrics Redesign — TLC Design Packet (Item 2b)
doc_type: design
version: 0.3.0
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
- Rollup is a **total function** over valid inputs (CFADA-r1 B3): `criteria[]` must be non-empty and every criterion status must be one of the four lifecycle values — anything else (unknown, absent, empty list) is a **validation error**, never a derived value. Then: all `done` ⇒ `done`; else any `active` ⇒ `active`; else any `planned` ⇒ `planned`; else `future`. Overlay independent: `blocked: true` propagates if any criterion carries it; `blocked_reason` stays **enum** `{gate, resource, authority, recovery, dependency}`; `blocked_criterion` names the criterion id. The AC3 test domain is bounded: all (status × blocked) combinations for one- and two-criterion gates — (4×2) + (4×2)² = 72 cases — plus the invalid-input cases.
- The stored gate `status`/`blocked` **must equal** the rollup — mismatch is a validation error (derived, fail-closed; the data file may cache the value but can never contradict it).
- **Gate-K corrected by SPLIT (CFADA-r1 B1 — the packet's original recession claim was factually wrong: live `deriveNow` is 14.36 with 35 settled items after seq 13.9, so re-statusing Gate-K in place would violate past-items-settled and the done-only-date rule):
  - `gate-k` stays **done** at seq 13.9 with its date — the pre-live closeout genuinely happened (waiver `docs#138`); label reworded to say exactly that; criteria = `[{id:"prelive-closeout", status:"done", ref:"docs#138"}]`; the `boundary_status`/`go_live_revalidation` fields are deleted.
  - a NEW `gate-k-go-live` gate is added **right of the live frontier** (seq 14.8, no date, `deps:["gate-k"]`): criteria = `[{id:"go-live-revalidation", label:"go-live boundary revalidation", status:"planned", blocked:true, blocked_reason:"gate"}]` ⇒ rollup `status:"planned", blocked:true, blocked_reason:"gate", blocked_criterion:"go-live-revalidation"`. The unmet scope renders ahead of the frontier in the blocked lane — the honest picture, with no frontier surgery and no history rewrite.
- Backfill: every other `type:"gate"` item gets a single criterion mirroring its current settled state (`{id:"closeout", status:<current>, ...}`) — no invented history, and the rollup equality holds trivially.

### 2.2 Payload scope (CFADA-r1 B2 — the survey conflated payloads)
The `evidence_state`/`freshness_state` fields live in the **live-reader
correction payload** (`CIVILIZATION_LIVE_READER_CORRECTION`), a separate
schema in the same file — **no arc item carries them**. This packet's schema
work applies to **`CIVILIZATION_ARC_DATA.items` only**; the correction and
progress-evidence payloads keep their existing shapes and are **explicitly
out of scope** (their own validation story is follow-up work, noted in §4
residuals — not silently absorbed, not silently broken).

### 2.3 Validator tightening (deny-by-default)
- **Item-key allowlist** (enumerated from the live data, CFADA-r1 M1): the arc item schema set is exactly `{id, code, ref, date, type, label, status, blocked, blocked_reason, blocked_criterion, criteria, provenance, seq, repo, sprint, gate, goal, family, deps, note, href, evidence_links, author}` — `blocked_criterion`/`criteria` are this packet's additions; `author` is carried by runtime-merged inflight items and validated with the same schema; `boundary_status`/`go_live_revalidation` are deliberately NOT in the set (the migration deletes them). Any other key ⇒ validation **error**.
- **Null convention (CFADA-r1 M2)**: `blocked_reason` may be present-and-`null` on unblocked items (all 120 live items carry `blocked_reason: null`); it must be **non-null exactly when `blocked: true`**, and `blocked_criterion` may be non-null only alongside a non-null `blocked_reason` on a gate.
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
| AC5 | the split Gate-K pair models the honest state: `gate-k` done at 13.9 with date; `gate-k-go-live` planned+blocked right of the frontier with `deps:["gate-k"]`; frontier value unchanged (no history rewrite) | `gate-k split is honest and frontier stable` |
| AC6 | the shipped `CIVILIZATION_ARC_DATA` (all 120+1 items, 69+1 gates with backfilled criteria) passes the tightened validator | `real arc data passes the tightened validator` |
| AC7 | no parallel-status field remains anywhere in the data (grep-level regression) | `parallel status vocabulary is gone` (python: extend `compile/test_build_site_*` arc check or js test reading the raw file) |
| AC8 | the now/detail render paths that read `go_live_revalidation`/`boundary_status` are **updated in-scope** to derive the hard-stop display from `blocked`/`criteria` (CFADA-r1 N1 — the renderer is affected); site build + arc DOM smoke + arc tests stay green | existing `test:js`, `test:unit`, `test:dom` suites + updated assertions |

Gate: AC1–AC8 green + CI-equivalent verify green. Any unproven criterion ⇒ not satisfied.

## 4. Authorization packet
- **Bounded scope:** `compile/assets/civilizationArcData.js`, `compile/assets/civilizationOntology.js`, arc render assets only if criteria display is trivial, `tests/ontology.test.js` (+ sibling arc tests as needed) — **transpara-ai/wiki only**.
- **Authority:** operator directive 2026-07-02 (marker `wiki-refactor-overnight-GO`); merge-when-green per the program grant.
- **Forbidden:** front page/board surfaces, ingest machinery, any status semantics beyond the canonical spec, other repos.
- **Residual risks:** (a) the Gate-K split adds a visible blocked gate ahead of the frontier — the honest picture, owner reviews live; (b) criteria backfill for the 69 historical gates is single-criterion minimal — richer criteria can be authored later without schema change; (c) `blocked_criterion` is this packet's concretization of the spec's "separate field/evidence pointer"; (d) the correction/progress payloads (`evidence_state`, `authority_state`, `freshness_state`, …) remain UNVALIDATED separate schemas — explicitly out of scope here, flagged as follow-up work rather than silently absorbed.

## Appendix — IADA (self-directed, v0.2.0)
| # | Finding | Disposition |
|---|---|---|
| I1 | validating rollup equality only for Gate-K would be instance-fixing | **FIXED in design** — AC3 runs the whole criterion-state domain; AC1 closes the unknown-key class |
| I2 | deleting `evidence_state` data would lose correction-lifecycle truth | **FIXED** — §2.2 amendment path (validated facets), per the canonical spec's own instruction |
| I3 | frontier recession could strand `planned` items left of `now` | checked: `deriveNow` recomputes from settled items and the past-items-settled rule re-validates; AC6 asserts the real data passes post-change |

## Appendix — CFADA round 1 (Codex) → repaired at v0.3.0

> Reviewed head `edf0405` (v0.2.0). Verdict: **FAIL — 3 blockers, 2 majors, 1 minor**. Codex SIMULATED the proposed change against the live data and disproved the packet's frontier claim.

| # | Finding | Disposition (v0.3.0) |
|---|---|---|
| B1 | frontier-recession claim factually wrong (deriveNow=14.36; 35 settled items after 13.9; date rule breaks) | Gate-K SPLIT: pre-live gate stays done at 13.9; new `gate-k-go-live` planned+blocked right of the frontier |
| B2 | evidence/freshness enums don't fit — those fields live in the correction payload, not arc items | §2.2 rescoped: arc items[] only; correction/progress payloads explicitly out of scope + residual (d) |
| B3 | rollup not total (all-future/planned+future/unknown undefined); AC3 domain unbounded | total function adopted verbatim; invalid input ⇒ validation error; AC3 domain bounded (72 + invalid cases) |
| M1 | key allowlist unspecified; would break live fields (`author` from inflight merge, etc.) | schema set enumerated from live data (23 keys incl. additions) |
| M2 | 120 items carry `blocked_reason: null` — only-on-blocked reading would reject them | null convention: present-and-null allowed; non-null exactly when blocked |
| N1 | renderer reads the deleted fields — "unaffected" was wrong | AC8 corrected: render paths updated in-scope |
