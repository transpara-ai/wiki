---
doc_id: TAI-WIKI-ARC-DATA-DEADKEYS
title: Arc data dead-keys removal — retire executionPlan + legendItems (TLC Factory Order + Design Packet)
doc_type: design
version: 0.3.2
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
- **R2** — no test, module, or builder references the removed keys except (i)
  historical prose in specs/plans and (ii) the named regrowth guard itself,
  which must name the keys to assert their absence (IADA B1: a zero-reference
  claim that forgets the guard's self-reference is false by construction); the
  drift-mirror test (`executionPlan row statuses mirror canonical item
  statuses`, tests/ontology.test.js) is retired WITH its subject.
  *Rationale:* a test whose subject is deleted either throws (fail-open noise)
  or silently no-ops; neither is honest.
- **R3** — a named regrowth guard prevents the keys from returning.
  *Rationale:* same guard class as the retired-asset regrowth guard in
  `compile/test_build_site_arc.py` (2b-visual AC4): deletion without a guard
  invites silent reintroduction.

Non-goals: no `items[]` change, no ontology/validator change, no view change,
no builder change, no CSS change. User-visible rendering is identical; the
built artifacts differ ONLY in (i) the smaller `civilizationArcData.js` asset
and (ii) that asset's cache-busting `?v=` value in the arc page's script tag
(`build_site.py:2100` emits `civilizationArcData.js?v=%s` from
`copy_asset()` — IADA B2: a "byte-identical HTML" claim would be false).

Constraints: `transpara-ai/wiki` only; branch `feat/arc-data-dead-keys` off
main @ `ca23a85`; lifecycle stops at ready PR (no merge — stage 12 is
Michael's).

## 2. Survey — measured, not assumed (wiki main @ ca23a85)

- Data file blob `697002a4bf3a703a4d7cd1b9eead3e8084fd758b`, 3011 lines.
  `legendItems` spans lines 2645–2658; `executionPlan` spans 2660–2821, the
  LAST key of `CIVILIZATION_ARC_DATA`, whose literal closes at 2822. The file
  then carries a SECOND assignment in the same IIFE —
  `window.CIVILIZATION_LIVE_READER_CORRECTION` (lines 2824–3010, the
  live-reader correction fixture behind one of the ported governance-honesty
  panels) — which this arc must NOT touch. (v0.2.x wrongly gave the
  executionPlan extent as 2660–3009 by assuming the object close was the file
  tail — IADA r2 I5; the §3 contract is key-anchored, so implementation was
  unaffected, and the key-level ground-truth diff proves exactly
  `{legendItems, executionPlan}` removed with the correction fixture intact.)
  Two stale comments (lines ~2314–2315, ~2460–2461) say item blocks "mirror
  the rows in executionPlan.*" — with the key gone these comments would lie;
  they are rewritten to stand alone.
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
| EDIT | `compile/assets/civilizationArcData.js` | delete `legendItems` (2645–2658) + `executionPlan` (2660–2821 — NOT beyond: `window.CIVILIZATION_LIVE_READER_CORRECTION` at 2824–3010 is must-not-touch); rewrite the two stale mirror comments to describe the item blocks without referencing the retired key |
| EDIT | `tests/ontology.test.js` | delete the drift-mirror test (266–276); reword the line-256 assertion message (`'keep executionPlan work'` → `'keep derived worklist items'`); ADD named regrowth guard `data carries no retired render-support keys` asserting `'executionPlan' in d === false` and `'legendItems' in d === false` |
| UNTOUCHED | everything else | items[], ontology, view, builder, server, CSS, specs |

## 4. Acceptance criteria & named tests

| # | Criterion (risk) | Verification — named test |
|---|---|---|
| AC1 | Both keys absent from the loaded data object (low) | unit: `data carries no retired render-support keys` (tests/ontology.test.js) — written FIRST, verified RED at the pre-change tree, GREEN after |
| AC2 | No live reader remains; the drift-mirror test is retired with its subject (low) | procedural, recorded in the PR body: `grep -rn "executionPlan\|legendItems" --include="*.js" --include="*.py"` over `compile/` returns **zero** hits; over `tests/` every hit sits inside the single named regrowth guard test (the guard's self-reference is the one allowed reader — IADA B1); the full unit suite passes with the mirror test deleted |
| AC3 | Nothing user-visible changes; built output differs only in the data asset + its `?v=` cache-buster (low) | `npm run verify` green: build, node --check, unit, py (incl. `test_build_site_arc.py` regrowth guards), dom-smoke, Playwright — the view renders identically from `items[]`/`sprints[]` alone |

Gate satisfied-only-when: AC1–AC3 all green at the reviewed head AND
CI-equivalent `npm run verify` exits 0. Any unproven criterion ⇒ not satisfied.

## 5. Authorization packet

- **Bounded scope:** the §3 file plan, `transpara-ai/wiki` only, branch
  `feat/arc-data-dead-keys` off main @ `ca23a85`; lifecycle ends at ready PR.
- **Forbidden:** any change to `items[]` content, `civilizationOntology.js`,
  `civilizationArcView.js`, `build_site.py`, `ingest_server.py`, CSS, other
  repos; no merge; no push beyond the PR branch.
- **Residual risks:** none new. 2b-visual residual (a) closes **upon
  Michael's stage-12 merge of this arc's PR** — not by this packet's
  assertion (IADA m1); until merge the residual stands as recorded.
  Residuals (b)/(c) of that packet (detail-on-click retired, repo filter
  unbuilt) are design decisions on record, untouched here.

## Appendix — Source-of-intent archive (channel A, IADA M1)

Owner instruction, verbatim, Michael in-session 2026-07-06 (following an
assistant message whose remaining-work table named this cleanup as its item
2, "Dead data keys cleanup … `executionPlan` / `legendItems` in
`compile/assets/civilizationArcData.js`"):

> you are not leaving me in a clean state with explicit assistance.
> 1) Can you fix the nits you note without my involvement?
> 2) I thought issue #46 would be closed by closing the associated PR. If
> that is not the case then the PR was opened oddly. Help me fix this please.
> 3) Once 1 and 2 are complete we must immediately return to fixing the
> front-end of the Wiki and making the requirements met.

Item (1) is the order this packet answers; the interrogative phrasing sits in
a numbered work list whose item (3) presupposes completion of (1) and (2) —
read as an instruction, and archived here in full so the FO reading is
adjudicable from this blob alone.

## Appendix — IADA (self-directed, v0.1.0 → v0.2.0)

| # | Finding | Disposition |
|---|---|---|
| B1 | R2/AC2 claimed "zero references/hits" post-change — false by construction: the named regrowth guard must reference the key names to assert their absence | FIXED — R2 and AC2 both exempt the guard explicitly; grep verification split (compile/ zero; tests/ only inside the named guard) — the CLASS (every zero-reference claim in the packet) swept, both instances repaired |
| B2 | Non-goals claimed the rendered page "byte-identical except the data asset" — `build_site.py:2100` emits `civilizationArcData.js?v=%s` (cache-buster from `copy_asset()`), so the arc HTML changes with the asset | FIXED — non-goals + AC3 restated: rendering identical; artifacts differ only in the asset and its `?v=` value |
| M1 | Channel-A source-of-intent quoted one line of the owner's instruction; the FO contract requires archiving the ingested human doc so fidelity is adjudicable without the session | FIXED — full instruction archived verbatim in the appendix; this packet's blob SHA pins it |
| m1 | "This arc CLOSES residual (a)" closed a residual by author assertion | FIXED — closure bound to the stage-12 merge; residual stands until then |
| I5 (r2, v0.2.x → v0.3.0) | Survey gave executionPlan's extent as 2660–3009, silently attributing the trailing `window.CIVILIZATION_LIVE_READER_CORRECTION` assignment (2824–3010) to the retired key — an unverified inference from the file tail. Caught during implementation when the splice removed 183 lines, not ~366; resolved by key-level ground truth (`Object.keys` before/after: exactly the two keys removed) | FIXED — survey corrected with exact extents and the second assignment named as must-not-touch; lesson recorded: line-extent claims must be measured to their closing anchor, never inferred from "last key + file tail" |

IADA verdict at v0.2.0: **PASS — 0 design blockers**, assessor claude
(Fable 5), 2026-07-06. Scope audit: this packet authorizes no merge, no
deploy, no runtime execution, no issue mutation, no autonomy increase; the
lifecycle ends at ready PR. This IADA does not replace external CFADA.

## Appendix — CFADA round 1 (Codex) → PASS at v0.2.0

> `CFADA_DEADKEYS_R1 PASS blockers=0 majors=0 minors=0` — reviewer family
> codex (independent of author family claude), audited bytes = blob
> `4f2270ba14daa195bce64ca88db8a9c235525a63` (v0.2.0, commit 7f8407f),
> 2026-07-06. Zero findings. Fidelity verdicts: coherence PASS (ACs carry
> risk + verification; guard self-reference and cache-buster exceptions
> explicit; allowlist gate predicate); packet-vs-FO PASS (AC1↔R1, AC2↔R2,
> AC1/AC2↔R3; non-goals bound scope); FO-vs-source PASS (R1–R3 derive from
> metrics §4, 2b residual (a), archived owner instruction; the stage-6
> reading is faithful for the narrow ready-PR lifecycle with stage-12 merge
> reserved to Michael). This appendix is a record added after the audit; the
> gate credit binds to the audited blob above, not to this file's later SHAs.

## Appendix — CFADA round 2 (Codex) → FAIL, repaired at v0.3.1

> `CFADA_DEADKEYS_R2 FAIL blockers=1 majors=0 minors=0` at v0.3.0 blob
> `87028a4b` (2026-07-06). Codex independently re-measured the extents.

| # | Finding | Disposition (v0.3.1) |
|---|---|---|
| R2-B1 | The v0.3.0 survey correction (I5) fixed §2 but left the stale extent in the §3 contract row — the contract still "authorized" deletion into the must-not-touch `CIVILIZATION_LIVE_READER_CORRECTION` region. The implementation stayed narrow (key-anchored splice + ground-truth key diff), but the packet contract was stale — the same fix-the-instance-not-the-class failure I5 itself warned about | FIXED — §3 row corrected to 2660–2821 with the must-not-touch boundary named inline. Class assertion (CFADA r3 R3-B1 wording repair): every remaining occurrence of the stale end-line number in this packet sits inside a historical record of the error — §2's parenthetical, the I5 row, and this disposition row; the sole OPERATIVE extent (§3 contract row) is 2660–2821 and no operative extent crosses the must-not-touch boundary |
