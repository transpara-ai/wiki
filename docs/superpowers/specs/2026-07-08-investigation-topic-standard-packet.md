---
doc_id: TAI-WIKI-INVESTIGATION-STANDARD
title: One canonical page per investigation — Investigation Topic Standard (TLC Design Packet)
doc_type: design
version: 0.6.0
status: draft (IADA-passed; CFADA r1-r4 repaired; re-audit pending)
canonical: false
created: 2026-07-09
updated: 2026-07-09
owner: Michael Saucier
steward: Claude (Opus 4.8)
authority: planning
tlc_stage: design
factory_order: FO-WIKI-INVESTIGATION-STANDARD v0.2.1 (blob 472bb1623cea3de7b0bf7e7389841affe3d3e589, confirmed channel-A 2026-07-09; v0.2.1 corrects the MemPalace-conformance claim)
source_of_intent:
  - the Factory Order above (its §4 archives Michael's request verbatim; §5 archives the intake answers)
  - wiki/mempalace.md (blob a9a9bc6bc83b01a9ba27776bb179e6d8b16de96c) — the content exemplar
  - docs/superpowers/specs/2026-07-03-per-ingestion-ops-packet.md (blob 48e330a27d8449c5c8ac0e412dcf6f7d98c23dfc) — governs the ingest ops this ADD lane extends
intake_channel: A (owner-directed session 2026-07-08; confirmed 2026-07-09)
---

# Investigation Topic Standard — TLC Design Packet

> Answers FO-WIKI-INVESTIGATION-STANDARD v0.2.1 (R1–R8) against measured live
> code (wiki main @ `2c9e672`, survey 2026-07-08/09). House rule inherited:
> the branch that CREATES a page renders only from a proven allowlist
> (explicit new-investigation intent AND subject proven absent, keyed on the
> operator-supplied name); every other path appends or refuses — never creates.
> The builder stays no-LLM, no-network. Two-phase delivery (one FO, §6): Phase
> 1 machinery (code PR), Phase 2 retrofit (data-only PR[s]). Repaired through
> IADA (v0.2.0) and CFADA rounds 1 (v0.3.0), 2 (v0.4.0), 3 (v0.5.0), 4 (v0.6.0).

## 1. Survey — measured, not assumed (file:line evidence)

- **Infobox** (`build_site.py:1504` `build_infobox`): the "Raw docs" label is a
  single literal at `:1530`; its list comes from `raw_doc_refs(fm)`
  (`:953`–`968`), which reads **only** `raw_documents` (else local `sources`)
  — NOT `superseded_raw_documents` (see below). R3's surface.
- **Supersession has two shapes.** (1) Add-with-supersedes keeps every version
  in `raw_documents` (MemPalace's three versions). (2) The Replace op
  (`replace_source`) MOVES the old ref into a separate
  `superseded_raw_documents` key (`ingest_ops.py:952`; `test_ingest_ops.py:279`
  asserts the move). So a Replace-superseded raw file is absent from
  `raw_doc_refs` and would vanish from Topic Details unless the union is read
  (CFADA-r3 #8). No active investigation page carries the key today, but the
  standard must handle it since Replace is supported and R3 promises all
  versions.
- **TOC** (`build_toc` `:820`, ≥3 headings `:823`): injected at `:2181`, placed
  at `:2211`; the contribution box is tier-gated at `:2210`, the TOC is not
  (R4's seam). MemPalace has 8 `##` headings → a TOC today; R4 removes it.
- **Contribution box** (`:1538`): from `civilization_contribution`,
  investigation-tier only. **Lead** = the **bold** first paragraph
  (`:2208`–`:2209`; MemPalace opens `**MemPalace is …**`) — R2 "Summary".
- **stale banner** (`:2200`–`:2204`): Replace-specific wording ("raw sources
  were replaced … pending authorization") — false for an unauthenticated ADD
  (CFADA-r2 #5).
- **Ingest target list** (`ingest_server.py:143` `article_records`): offers
  EVERY non-retired article of ANY tier (CFADA-r1 #1 — do not refuse
  non-investigation targets).
- **Ingest routing** (`handle_ingest` `:802`): no `target_slug` →
  `create_article_from_source()` (`:865`–`867`) derives slug + `entity` from
  the first raw doc's **title** (`:602`, `:621` hardcodes `tier:
  investigation`), auto-sets `investigation_topic`; a provided `target_slug`
  appends (`:585`/`:594` via `:542`). `prospective_unassigned_slug` (`:116`)
  mirrors the title-derivation R1 must end (CFADA-r2 #4).
- **stale_since** primitive: set by `replace_source` `:961` via `_set_scalar`
  `:735`; cleared via `_drop_scalar` `:743`. Append helpers set nothing.
- **Test wiring:** `package.json` `test:py` enumerates each Python test file
  **explicitly** (no glob) — a new `test_*.py` file is NOT run by
  `npm run verify` unless added, or unless the tests land in an already-wired
  module (CFADA-r3 #10). No-LLM/no-network builder: `build_site.py:6`.
- **Corpus**: 20 pages — 19 active + the retired owainlewis tombstone. None is
  literally conformant; MemPalace's heading is the dated
  `## What Changed With TAI-RES-2026-004` (generalized in Phase 2).

## 2. The contract

### 2.1 File plan

| Phase | Action | File | Change |
|---|---|---|---|
| 1 | EDIT | `compile/build_site.py` | **R3:** relabel `"Raw docs"` → `"Topic Details"` (`:1530`) AND source the list from `raw_documents` ∪ `superseded_raw_documents` (deduped, superseded marked, newest primary — CFADA-r3 #8). **R4:** tier-gate the TOC at `:2181`. **R7 banner:** reason-neutral `stale_since` text (`:2200`). **R2 predicate:** `investigation_conformance(slug)`. |
| 1 | EDIT | `compile/ingest_server.py` | **R5/R6/R1 (§2.4):** intent model + fail-closed guard; `create_article_from_source(name=…)` keyed on the operator name (CFADA-r2 #4); `prospective_unassigned_slug` in lockstep; collision set includes `investigation_topic` cluster labels (CFADA-r3 #9). Default lane appends (any tier), stamps `stale_since` only for investigation targets. |
| 1 | EDIT | `compile/ingest_ops.py` | `set_article_stale(root, slug, now)` wrapping `_set_scalar` — reused by ADD + Replace; no new op, no auth contract (Q4). |
| 1 | EDIT | `ingest_page()` region in `compile/build_site.py` | "New investigation" toggle (default OFF) reveals a **required name** field, the ONLY creation path; checking it ignores `target_slug`. Both themes. |
| 1 | ADD/EDIT | tests — land in already-wired modules (`test_build_site_nav.py`, `test_ingest_server.py`, `test_ingest_ops.py`, `test_ingest_ux.py`) OR add any new file to `package.json` `test:py` (CFADA-r3 #10); `tests/*.spec.js` for Playwright | AC1–AC5, AC6(P1), AC7–AC9. |
| 2 | EDIT | `wiki/<each active investigation>.md` (19, incl. MemPalace) | Retrofit to R2 (generalize MemPalace's "What Changed" heading; bold lead); `raw_documents` complete; `stale_since` where the summary needs re-derivation; Sakana pair conformed, `investigation_topic: Sakana AI` on both; remove stray/self `investigation_topic` from single-page investigations (CFADA-r4 #12). Data-only. |
| 2 | EDIT | wired `compile/test_build_site*.py` | Flip AC6 to assert every live-enumerated active investigation page conforms. |
| — | UNTOUCHED | authorization artifact semantics, `secret_scan`, Replace/Remove/register op logic, non-investigation source-add behavior, arc view, board, engine, refresh timer, the retired tombstone | Forbidden §5. |

### 2.2 R3 — Topic Details (infobox rename + superseded union)

`row("Raw docs", …)` → `row("Topic Details", …)` at `:1530`. The list is
sourced from `raw_documents` **∪** `superseded_raw_documents` (deduped, newest
primary, superseded entries marked), because the Replace op moves superseded
refs into the latter key (`ingest_ops.py:952`) and R3 requires all versions,
superseded included (CFADA-r3 #8). The existing local-`sources` fallback is
preserved when BOTH raw-doc keys are empty, so un-retrofitted pages (e.g.
bitsandpieces, ob1 — local `raw/*` only in `sources` today) keep their infobox
links until Phase 2 backfills `raw_documents` (CFADA-r4 #11). AC1 asserts the "Topic Details" row lists a
superseded entry and that no "Raw docs" label survives in `dist/`.

### 2.3 R4 — No in-topic Table of Contents

Allowlist branch at `:2181`: investigation → `toc = ""`; else → `build_toc`,
beside the contribution tier-gate at `:2210`. AC2 proves both directions.

### 2.4 R5/R6/R1 — Ingest ADD-default + canonical new-page + fail-closed guard

**FO deferred question resolved:** ADD is a **routing change in
`ingest_server.py`**, not a new `ingest_ops` op (Q4 keeps it unauthenticated).
Only the `stale_since` stamp reaches `ingest_ops`, via `set_article_stale`.

**Normalization (defined):** `norm(s)` = Unicode-casefold, collapse internal
whitespace to one space, strip surrounding whitespace/punctuation. A new name
**collides** when `norm(name)` equals `norm(x)` for x ∈ {an active investigation
page's `entity` ∪ its `aliases` ∪ its `investigation_topic` cluster label}, or
when `slugify(name)` equals any existing page's slug (active OR tombstone). The
cluster label is a collision surface even though it is neither a slug nor an
entity — else a new "Sakana AI" upload could spawn a spurious third cluster
member (CFADA-r3 #9).

**Intent model** — `handle_ingest` reads a `new_investigation` flag (default
false):

- **Default (add to an existing page).** REQUIRES an explicit `target_slug`
  naming an existing **active** page (any tier). On match: append
  `raw_documents` + `sources` (dedup); if `tier: investigation`, also
  `set_article_stale`; rebuild — **create nothing**. Non-investigation targets
  keep today's behavior (CFADA-r1 #1). Absent / retired / non-existent
  `target_slug` → **REFUSE**. No fuzzy title match (IADA-I1).
- **Explicit new-investigation.** Requires a non-empty operator **name**
  (empty → refuse). The name — not the doc title — drives the page:
  `slugify(name)` is the slug, `name` the `entity`;
  `create_article_from_source(name=…)` and `prospective_unassigned_slug` use it
  (CFADA-r2 #4). `target_slug` is ignored here. REFUSE unless the subject is
  proven absent (the collision rule above). Otherwise create with `stale_since`,
  `status: browser-ingested source; awaiting synthesis`, no auto
  `investigation_topic`.

**Fail-safe statement.** The ONLY branch that creates a page is
`new_investigation == true` AND a non-empty name AND the subject proven absent.
Every other path appends or refuses. No `else`/fall-through creates. AC4 proves
the domain.

**stale_since lifecycle (R7).** An investigation ADD stamps `stale_since`; the
banner (`:2200`) is genericized to reason-neutral text ("raw sources changed —
summary re-derivation pending"), correct for both Add and Replace (CFADA-r2 #5),
with a test. A governed authoring pass re-derives the Summary + sections and
drops `stale_since` (`_drop_scalar`, as Replace does at `:976`). No
automated/LLM regeneration (AC7).

### 2.5 R2/R8 — Canonical schema, the conformance predicate, corpus timing

**Normative schema (the "standard").** Required frontmatter keys: `entity`,
`aliases`, `tier: investigation`, `status`, `last_compiled`,
`civilization_contribution`, `raw_documents`, `current_research_version`,
`sources` (`investigation_topic` only for a declared cluster). Required body: a
**bold lead paragraph** before the first `##` (the Summary), then the `##`
headings `What Changed with the Research`, `The Boundary`, `Capability Read`,
`Benchmark Reality`, `Sources & Provenance` (`Integration Packet` optional),
rendered **in canonical order**. Civilization Contribution renders from
`civilization_contribution` (not a heading).

**`investigation_conformance(slug)`** returns (missing required frontmatter
keys) ∪ (missing required `##` headings) ∪ (non-bold-lead flag) ∪
(out-of-order flag):

- **Lead (CFADA-r2 #7):** the first paragraph before any `##` must be non-empty
  AND carry bold/`<strong>` emphasis.
- **Order (CFADA-r1 #3, CFADA-r2 #6):** from the page's heading sequence keep
  the STANDARD headings — the required set PLUS `Integration Packet` **when
  present** — and require them in canonical order (so a present
  `Integration Packet` must sit immediately before `Sources & Provenance`).
  Free extras (`## Placement`, `## Decision Record`) may be interspersed and
  are ignored by the order check.

Conformant ⟺ the returned set is empty. Heading match is exact on the canonical
strings (MemPalace's dated heading is non-conformant until Phase 2 — IADA-I2).

**Cluster invariant (CFADA-r4 #12).** `investigation_topic` is reserved for
genuine multi-page clusters. The corpus gate (AC6/P2) additionally requires
every `investigation_topic` value to be shared by ≥2 active investigation pages;
a lone/self-topic value (main today carries several, e.g. hermes-agent,
google-open-knowledge-format) is a deficiency, so Phase 2 removes stray topics.
This is corpus-level (it needs cross-page counts), distinct from the per-page
`investigation_conformance`.

**Corpus timing (no red merge).** Phase 1 asserts the predicate is correct
(a conformant fixture → ∅; missing-key, missing-heading, non-bold-lead,
out-of-order, and Integration-Packet-misordered fixtures → the right
deficiency) and that the new-investigation skeleton conforms. Phase 2 retrofits
all pages and flips AC6 to assert every **live-enumerated** active investigation
page conforms (IADA-I6). The hard corpus gate turns on only when satisfiable.

## 3. Acceptance criteria & named tests

| # | Phase | Criterion (risk) | Verification — named test (in a package.json-wired module) |
|---|---|---|---|
| AC1 | 1 | Topic Details row lists every `raw_documents` AND `superseded_raw_documents` entry (superseded included, marked), falling back to local `sources` when both are empty; no "Raw docs" label survives in `dist/` (low) | py: `test_topic_details_lists_all_versions_incl_superseded`, `test_topic_details_falls_back_to_local_sources` |
| AC2 | 1 | Investigation-tier page renders no `.toc`; a ≥3-heading non-investigation page still renders one (med) | py: `test_investigation_pages_have_no_toc`; playwright |
| AC3 | 1 | Default ADD with a resolvable investigation `target_slug` appends + sets `stale_since`, `wiki/*.md` count unchanged, rebuilds; a non-investigation target appends WITHOUT a stale stamp (preserved) (high) | server: `test_add_default_appends_and_flags_stale`, `test_add_to_non_investigation_preserves_behavior` |
| AC4 | 1 | Fail-closed guard, full domain — default ADD with (a) no target, (b) retired/nonexistent target → REFUSE; (c) non-investigation target → APPENDS (no refuse/stale); new-investigation with (d) empty name, (e) slug collision (active/tombstone), (f) name/entity/alias collision (case/whitespace), (g) name = an existing `investigation_topic` cluster label (e.g. "Sakana AI") → REFUSE; (h) doc title ≠ operator name → NAME drives slug/entity+guard (no bypass); (i) distinct entities sharing a cluster (Sakana) → allowed; (j) absent subject → created (high) | server: `test_ingest_guard_domain` (cases a–j) |
| AC5 | 1 | New-investigation builds FROM the operator name (not the doc title), emits the R2 skeleton (bold-lead placeholder + `stale_since` + `status: awaiting synthesis`, no auto `investigation_topic`); toggle defaults OFF, only creation path; `prospective_unassigned_slug` matches the creator (high) | server: `test_new_investigation_uses_operator_name`, `test_new_investigation_emits_canonical_skeleton`, `test_prospective_slug_matches_creator` |
| AC6 | 1 → 2 | **P1:** predicate → ∅ for a conformant fixture; exact deficiency for missing-key / missing-heading / non-bold-lead / out-of-order / Integration-Packet-misordered fixtures; skeleton conforms. **P2:** every live-enumerated active investigation page conforms AND every `investigation_topic` is shared by ≥2 active pages (no stray/self-topic) (med) | py: `test_investigation_conformance_predicate` (P1); `test_all_active_investigations_conform`, `test_investigation_topic_clusters_have_multiple_members` (P2) |
| AC7 | 1 | Builder imports no network/model client; a `stale_since` page renders the banner until cleared, with reason-neutral text (no Replace-specific "sources were replaced"/"authorization" wording) (med) | py: `test_builder_has_no_network_client`, `test_stale_banner_is_reason_neutral` |
| AC8 | 1 | MemPalace's rendered HTML changes in exactly two ways — the infobox label and the removed `.toc` — no other: all 8 headings + contribution box still present (med) | py: `test_mempalace_render_diff_is_label_and_toc_only` |
| AC9 | 1 & 2 | Every new/edited Python test above is wired into `package.json` `test:py` (or lands in an already-wired module); full chain green, zero regression (low) | `npm run verify` exit 0 at each PR's reviewed head; `test_py_targets_are_wired` asserts the module list runs the new tests |

**Gate satisfied-only-when (allowlist, phase-total):** every AC is assigned to
exactly one phase; no AC is optional. The Phase-1 PR is satisfied only when
AC1–AC5, AC6(P1), AC7, AC8, AC9 are green at its reviewed head AND
`npm run verify` exits 0. The Phase-2 PR is satisfied only when AC6(P2) and AC9
are green. The FO is satisfied only when BOTH phases are. Any unproven assigned
criterion ⇒ not satisfied (IADA-I4).

## 4. Fail-safe analysis (the §8 house rule, applied)

- **Page creation is the guarded act.** Allowlist: create ⟺ `new_investigation`
  AND non-empty name AND subject proven absent (§2.4), keyed on the operator
  name (CFADA-r2 #4) with the collision set spanning entity ∪ aliases ∪ cluster
  label ∪ all slugs (CFADA-r3 #9). Default lane appends or refuses; never
  creates. AC4 proves cases a–j.
- **Non-investigation adds untouched** (CFADA-r1 #1).
- **Unauthenticated ADD is safe** — the danger (wrong/duplicate page) is gated
  above, not the append (Q4). No fuzzy match.
- **stale is fail-VISIBLE and honestly worded** (CFADA-r2 #5).
- **Topic Details shows all versions** incl. Replace-superseded (CFADA-r3 #8) —
  no silent version loss.
- **No-LLM invariant preserved** (AC7). **Conformance gate cannot brick the
  build** — a test, corpus assertion turned on only when satisfiable.

## 5. Authorization packet

- **Bounded scope:** the §2.1 file plan; `transpara-ai/wiki` only; docs branch
  `feat/investigation-standard-design` off main @ `2c9e672`; Phase-1/2 code on
  their own `feat/` branches off `origin/main`; lifecycle to ready PR. **No
  code before Human Design Review approves this packet (stage 6).**
- **Forbidden:** any change to the authorization-artifact model or
  `secret_scan`; Replace/Remove/register semantics; non-investigation
  source-add behavior; ADD entering the authorization contract (Q4);
  LLM/network in the builder; reanimating the retired tombstone; force-merging
  Sakana; any Phase-2 content edit before Phase-1 merges; autonomous issue/PR
  creation; merge.
- **Residual risks:** (a) a subject already present under one name, re-ingested
  as a *declared* new investigation under a *genuinely different* name (no
  slug/entity/alias/cluster overlap), is not machine-detectable — the operator
  asserted "new"; the collision check catches same/similar names and cluster
  labels, and the retire path recovers the rare miss; fail-closed direction
  deliberate. (b) Clearing `stale_since` is a manual authoring edit; mitigated
  by the visible banner + R8. (c) Phase-2 retrofit is judgment-heavy; the
  predicate guards structure/order/bold-lead, not prose quality. (d) The
  bold-lead check keys on rendered `<strong>`/`**`; a non-`strong` visual
  emphasis is flagged — acceptable (the standard specifies bold).

## 6. Two-phase delivery (one FO)

- **Phase 1 — machinery (code PR).** R3 (incl. superseded union) + R4 + R5 + R6
  + R7 banner + the conformance predicate + AC1–AC5, AC6(P1), AC7–AC9. Server
  code ⇒ deploy = reset serving clone to main + `npm run build` + **restart**.
- **Phase 2 — retrofit (data-only PR[s]).** The 19 pages → R2 (R8), MemPalace
  heading generalized, bold leads, `stale_since` where needed, AC6(P2) on.
  Data-only ⇒ `npm run build`, **no restart**. May split by cluster.

Each PR runs stages 7→11 (IAR → CFAR at exact head → ready → fresh ready-state
CFAR). Merge is Michael's (stage 12).

## Appendix — IADA (self-directed, v0.1.0 → v0.2.0)

Assessor: Claude (Opus 4.8), 2026-07-09. Adversarial, whole-domain. Findings
I1–I8 (fuzzy match, MemPalace-conforms, golden TOC, AC cherry-pick, predicate
under-definition, hardcoded-19, residual wording, AC4 collision domain) all
FIXED. Verdict v0.2.0: PASS — 0 blockers. Does not replace external CFADA.

## Appendix — CFADA rounds (Codex, materially independent of the Claude author)

Reviewer: Codex (`codex-cli 0.142.5`, gpt-5.5, xhigh). `codex exec review
--base origin/main`, bare, from the worktree.

**Round 1 → FAIL, repaired v0.3.0** (packet blob `c06d8126ff44feb03bcca8df9099fc9cdca665dc`, commit `c4f8e87`):
| # | Finding | Disposition |
|---|---|---|
| C1 | Guard would regress non-investigation source adds | FIXED — investigation-scoped (§2.4, AC4c). |
| C2 | FO↔packet MemPalace-conformance contradiction | FIXED — FO → v0.2.1 (blob `472bb1623c…`); rebound. |
| C3 | Order not checked, only presence | FIXED — canonical-order subsequence (§2.5, AC6). |

**Round 2 → FAIL, repaired v0.4.0** (packet blob `b65d39413fce232b95adba2ebe56262f5be2d39a`, commit `153e839`):
| # | Finding | Disposition |
|---|---|---|
| C4 | Creation keyed on doc title, not the operator name → R1 bypass | FIXED — name-keyed creation + collision (§2.4, AC4d/g/h, AC5). |
| C5 | Replace-specific stale banner false for ADD | FIXED — reason-neutral banner (§2.4, AC7). |
| C6 | Optional Integration Packet not order-checked when present | FIXED — present optional headings ordered (§2.5, AC6). |
| C7 | Predicate allowed a non-bold lead | FIXED — bold-lead required (§2.5, AC6). |

**Round 3 → FAIL, repaired v0.5.0** (packet blob `9baa62c8cc1c6b6d25507dc7b0af334c3fa8989d`, commit `956e803`):
| # | Finding | Disposition |
|---|---|---|
| C8 | Topic Details missed Replace-`superseded_raw_documents` (R3 wants all versions) | FIXED — Topic Details unions both keys (§2.2, §2.1, AC1). |
| C9 | Collision check missed `investigation_topic` cluster labels (a new "Sakana AI" page could slip through) | FIXED — cluster label added to the collision set (§2.4, AC4g). |
| C10 (P3) | New Python test files not run by `npm run verify` (explicit enumeration) | FIXED — tests land in wired modules or `package.json` is updated; AC9 pins it (§2.1, AC9). |

**Round 4 → FAIL, repaired v0.6.0** (packet blob `e8d21fa9c24100e8604eb1ef5d749192e6693127`, commit `f88f2b8`):
| # | Finding | Disposition |
|---|---|---|
| C11 | Topic Details `raw_documents ∪ superseded_raw_documents` dropped the existing local-`sources` fallback — un-retrofitted pages (bitsandpieces, ob1, …) would lose infobox links in Phase 1 | FIXED — fallback preserved when both raw-doc keys empty (§2.2, AC1). |
| C12 | Conformance didn't reject stray `investigation_topic` on single-page investigations — the AC6/P2 corpus gate could pass them | FIXED — cluster invariant (topic shared by ≥2 active pages); Phase 2 removes strays (§2.5, §2.1, AC6). |

Re-audit (CFADA round 5) pending at v0.6.0. No code before Human Design Review
(stage 6) approves.
