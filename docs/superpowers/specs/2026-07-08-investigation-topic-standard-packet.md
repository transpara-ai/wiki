---
doc_id: TAI-WIKI-INVESTIGATION-STANDARD
title: One canonical page per investigation — Investigation Topic Standard (TLC Design Packet)
doc_type: design
version: 0.10.0
status: AMENDED v0.10.0 — CFADA re-PASS (2026-07-09) — folds in R9 (single nav entry via `investigation_primary`) + revises R8 per Michael's Option-A nav decision; IADA + CFADA re-run (7 amendment rounds 17–23, findings C35–C46 all repaired) returned 0 design blockers at the round-23-audited blob f54544fa444774a2ea12e03843d426563afd9ce1. READY for Human Design Review (stage 6). No code before Michael approves.
canonical: false
created: 2026-07-09
updated: 2026-07-09
owner: Michael Saucier
steward: Claude (Opus 4.8)
authority: planning
tlc_stage: design
factory_order: FO-WIKI-INVESTIGATION-STANDARD v0.3.1 (blob 62abaf4e9a5909c8003379a95046bdc408402b25; supersedes v0.2.3 blob 20d4f35f89299e0da0f0d96cc8b65fb09fe5628e; v0.3.0 adds R9 + revises R8 per Michael's 2026-07-09 nav decision, v0.3.1 narrows the hex-free constraint per CFADA-r22 #46)
source_of_intent:
  - the Factory Order above (its §4 archives Michael's request verbatim; §5 archives the intake answers)
  - wiki/mempalace.md (blob a9a9bc6bc83b01a9ba27776bb179e6d8b16de96c) — the content exemplar
  - docs/superpowers/specs/2026-07-03-per-ingestion-ops-packet.md (blob 48e330a27d8449c5c8ac0e412dcf6f7d98c23dfc) — governs the ingest ops this ADD lane extends
intake_channel: A (owner-directed session 2026-07-08; confirmed 2026-07-09)
---

# Investigation Topic Standard — TLC Design Packet

> Answers FO-WIKI-INVESTIGATION-STANDARD v0.3.1 (R1–R9) against measured live
> code (wiki main @ `2c9e672`, survey 2026-07-08/09). House rule inherited:
> the branch that CREATES a page renders only from a proven allowlist
> (explicit new-investigation intent AND subject proven absent, keyed on the
> operator-supplied name); every other path appends or refuses — never creates.
> The builder stays no-LLM, no-network. Two-phase delivery (one FO, §6): Phase
> 1 machinery (code PR), Phase 2 retrofit (data-only PR[s]). Repaired through
> IADA (v0.2.0) and CFADA rounds 1 (v0.3.0), 2 (v0.4.0), 3 (v0.5.0), 4 (v0.6.0), 5 (v0.7.0), 6 (v0.8.0), 7 (v0.8.1, audit-trail), 8 (v0.9.0), 9 (v0.9.1), 10 (v0.9.2), 11 (v0.9.3), 12 (v0.9.4), 13 (v0.9.5), 14 (v0.9.6), 15 (v0.9.7), 16 (PASS at v0.9.7). **v0.10.0 (2026-07-09) is a post-PASS AMENDMENT** — it adds R9 (single nav entry via `investigation_primary`) and revises R8 per Michael's nav-semantics decision; this mutation strands the v0.9.7 CFADA credit and re-opens IADA → CFADA (see the Amendment log).

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
| 1 | EDIT | `compile/build_site.py` | **R3:** relabel `"Raw docs"` → `"Topic Details"` (`:1530`) AND source the list from `raw_documents` ∪ `superseded_raw_documents` (deduped, superseded marked, newest primary — CFADA-r3 #8), with the empty-both fallback scoped to raw-INGESTED RESEARCH refs (`raw/inbox/...` uploads ∪ `…/tai-res-*.md` evaluations wherever placed — CFADA-r17 #35), never doctrine citations (CFADA-r13 #30). **R4:** tier-gate the TOC at `:2181`. **R7 banner:** reason-neutral `stale_since` text (`:2200`). **R2 predicate:** `investigation_conformance(slug)`. **R9:** the single-primary collapse applies to BOTH investigation nav surfaces — the sidebar `build_investigation_nav` (`:1406`) AND the bottom index `build_navbox` (`:1489`, injected `:2185`, whose investigation row lists every active article flat at `:1497` — CFADA-r18 #38): a multi-page `investigation_topic` cluster with exactly one active `investigation_primary: true` shows ONE entry (the primary) on each surface, omitting the rest; zero active primaries → full group/list (fail-safe, non-lossy); ≥2 → full render + conformance failure (amendment 2026-07-09). |
| 1 | EDIT | `compile/ingest_server.py` | **R5/R6/R1 (§2.4):** intent model + fail-closed guard; `create_article_from_source(name=…)` keyed on the operator name (CFADA-r2 #4); `prospective_unassigned_slug` in lockstep; collision set includes `investigation_topic` cluster labels (CFADA-r3 #9), matched on the compact `collision_key` (CFADA-r5 #13, r8 #21, r9 #22); the operator name is quarantined pre-write (CFADA-r6 #16); ADD keeps `require_authoring` (CFADA-r6 #15). Default lane appends (any tier), stamps `stale_since` only for investigation targets. |
| 1 | EDIT | `compile/ingest_ops.py` | `set_article_stale(root, slug, now)` wrapping `_set_scalar` — reused by ADD + Replace; no new op, no auth contract (Q4). |
| 1 | EDIT | `ingest_page()` region in `compile/build_site.py` | "New investigation" toggle (default OFF) reveals a **required name** field, the ONLY creation path; checking it ignores `target_slug`. Both themes. |
| 1 | ADD/EDIT | tests — land in already-wired modules (`test_build_site_nav.py`, `test_ingest_server.py`, `test_ingest_ops.py`, `test_ingest_ux.py`) OR add any new file to `package.json` `test:py` (CFADA-r3 #10); `tests/*.spec.js` for Playwright | AC1–AC5, AC6(P1), AC7–AC9, AC10(P1) (AC10 nav single-entry lands in the wired `test_build_site_nav.py`). |
| 2 | EDIT | `wiki/<each active investigation>.md` (19, incl. MemPalace) | Retrofit to R2 (generalize MemPalace's "What Changed" heading; bold lead); `raw_documents` complete; `stale_since` where the summary needs re-derivation; Sakana pair conformed, `investigation_topic: Sakana AI` on both, **`investigation_primary: true` on `sakana-ai-evaluation.md`** plus an editorial cross-link from it to the companion `sakana-ai-adjacent-landscape.md` (R9 — companion reachable though off the top-level nav); remove stray/self `investigation_topic` from single-page investigations (CFADA-r4 #12). Data-only. |
| 2 | EDIT | wired `compile/test_build_site*.py` | Flip AC6 to assert every live-enumerated active investigation page conforms; AC10(P2) asserts Sakana renders as a single primary nav row with the companion cross-linked. |
| — | UNTOUCHED | authorization artifact semantics, `secret_scan`, Replace/Remove/register op logic, non-investigation source-add behavior, the browser Add/Replace upload filename naming (descriptive stem + sha12 — the FO's "hex-free raw filenames" line is a pre-existing environmental secret-scan hygiene note about bare-hex legacy names, NOT an R5/R6 deliverable of this FO; CFADA-r21 #42), arc view, board, engine, refresh timer, the retired tombstone | Forbidden §5. |

### 2.2 R3 — Topic Details (infobox rename + superseded union)

`row("Raw docs", …)` → `row("Topic Details", …)` at `:1530`. The list is
sourced from `raw_documents` **∪** `superseded_raw_documents` (deduped, newest
primary, superseded entries marked), because the Replace op moves superseded
refs into the latter key (`ingest_ops.py:952`) and R3 requires all versions,
superseded included (CFADA-r3 #8). For an ADD-with-supersedes topic that keeps
every version in `raw_documents` (e.g. MemPalace's three), the supersession /
newest-primary marking is derived from the `supersedes:` annotations carried in
the `sources`/`raw_documents` comments — NOT only from `superseded_raw_documents`
(which just the Replace op populates); so a topic whose supersession lives only
in comments still marks the superseded versions and links the newest as primary
(CFADA-r21 #43). The Topic Details renderer (Phase-1
machinery) filters its ENTIRE input — `raw_documents` ∪ `superseded_raw_documents`
AND the empty-both fallback — to raw-INGESTED RESEARCH refs: a browser-ingest
upload under `raw/inbox/...` OR a TAI-RES evaluation doc (`…/tai-res-*.md`)
wherever placed — e.g. `raw/civilization/external-landscape/tai-res-2026-007-pageindex-evaluation.md`,
which is `wiki/pageindex.md`'s primary source and sits OUTSIDE the inbox by design
(CFADA-r17 #35). Doctrine citations (`raw/transpara/...`, `raw/open-brain/...`),
provenance/index docs, absolute `/Transpara/...` paths, and external URLs NEVER
render as Topic Details wherever they sit (CFADA-r15 #32, r17 #35),
including a doctrine ref already mis-placed in `raw_documents` (e.g.
hermes-agent). So a support-only page has EMPTY Topic Details from Phase 1
onward, un-retrofitted pages keep only their ingested-file links, and Phase 2
stays data-only; the Phase-2 retrofit additionally moves mis-placed doctrine
refs out of `raw_documents` for hygiene, but the invariant does not depend on it
(CFADA-r4 #11, r10 #24, r12 #29, r13 #30, r15 #32). AC1 asserts the "Topic Details" row lists a
superseded entry and that no "Raw docs" label survives in `dist/`.

### 2.3 R4 — No in-topic Table of Contents

Allowlist branch at `:2181`: investigation → `toc = ""`; else → `build_toc`,
beside the contribution tier-gate at `:2210`. AC2 proves both directions.

### 2.4 R5/R6/R1 — Ingest ADD-default + canonical new-page + fail-closed guard

**FO deferred question resolved:** ADD is a **routing change in
`ingest_server.py`**, not a new `ingest_ops` op. ADD requires no single-use
authorization artifact (Q4) but KEEPS the existing `require_authoring()`
transport gate (loopback/same-origin or `CIVWIKI_AUTHORING_TOKEN`) —
"unauthenticated" never means dropping transport auth (CFADA-r6 #15).
Only the `stale_since` stamp reaches `ingest_ops`, via `set_article_stale`.

**Collision key (defined, distinct from `slugify`):** `collision_key(s)` =
Unicode-casefold `s`, then remove ALL non-alphanumeric characters (whitespace,
hyphens, punctuation, and parentheses — everything), giving a COMPACT form. The
compact form collapses every separator variant, including no-space vs space
(CFADA-r9 #22), which a hyphen-folding key would miss. Unlike `ingest_server.slugify`,
which drops parenthesized text before folding (CFADA-r8 #21), `collision_key`
never drops text. A new name **collides** when `collision_key(name)` equals
`collision_key(x)` for x ∈ {ANY investigation page's — active OR retired/tombstone — `entity` ∪
`aliases` ∪ `investigation_topic` cluster label ∪ slug} ∪ {any existing page's
slug, active OR tombstone}. Including RETIRED frontmatter blocks reanimating a
retired subject via its old entity/alias — e.g. the owainlewis tombstone's
`TAI-RES-2026-006` alias (CFADA-r12 #28; the no-reanimation constraint). So "MemPalace"/"Mem Palace"/"Mem-Palace" all key to `mempalace`, and
"Sakana AI"/"Sakana-AI"/"Sakana (AI)" all key to `sakanaai` — no separator
variant slips through (CFADA-r3 #9, r5 #13, r8 #21, r9 #22). Over-collision (two
genuinely distinct subjects sharing a compact form) is a deliberate fail-closed
stall, operator-recoverable (residual a).
The created page's slug still comes from `slugify(name)`; the collision test
uses `collision_key` **and** an explicit `slugify(name)`-against-all-slugs
check. Because `slugify` can DROP text ("Foo (Bar)" → `foo`), the compact key
may differ from an existing slug even though `slugify(name)` targets that same
file, so the guard ALSO refuses when `slugify(name)` equals any existing page's
slug (active OR tombstone) — the generated slug is the fail-closed ground truth
for which file a create would touch. Both checks must pass to create; either
collision refuses (CFADA-r10 #23). The
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
- **Explicit new-investigation.** Requires an operator **name** whose compact
  `collision_key` is non-empty AND whose `slugify(name)` does not fall back to a
  generic default (an empty name, or one with no slug/collision characters like
  "!!!" or "()", → refuse — else a create could mint a generic
  `document`/`ingested-document` page unrelated to the subject; CFADA-r11 #26). The name — not the doc title — drives the page:
  `slugify(name)` is the slug, `name` the `entity`;
  `create_article_from_source(name=…)` and `prospective_unassigned_slug` use it
  (CFADA-r2 #4). `target_slug` is ignored here. REFUSE unless the subject is
  proven absent (the collision rule above). Otherwise create with `stale_since`,
  `status: browser-ingested source; awaiting synthesis`, no auto
  `investigation_topic`.

**Quarantine (CFADA-r6 #16).** The operator `name` is a new persisted, echoed
field, so it is ADDED to the EXISTING pre-write quarantine set (which already covers the
upload payload bytes, filenames, `note`, `supersedes`, and `external_urls`) —
the set is EXTENDED, never narrowed (CFADA-r8 #19); `handle_ingest` quarantines
the full set
BEFORE any validation, slug/entity derivation, write, or refusal echo — a
secret-shaped name is refused with redacted spans and never reaches
`wiki/<slug>.md` or a response (the CFAR-r20 echo-quarantine lane).

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
keys) ∪ (empty required render-driving field flag) ∪ (missing required `##`
headings) ∪ (non-bold-lead flag) ∪ (out-of-order flag):

- **Lead (CFADA-r2 #7):** the first paragraph before any `##` must be non-empty
  AND carry bold/`<strong>` emphasis.
- **Order (CFADA-r1 #3, CFADA-r2 #6):** from the page's heading sequence keep
  the STANDARD headings — the required set PLUS `Integration Packet` **when
  present** — and require them in canonical order (so a present
  `Integration Packet` must sit immediately before `Sources & Provenance`).
  Free extras (`## Placement`, `## Decision Record`) may be interspersed and
  are ignored by the order check.
- **Empty render-driving fields (CFADA-r19 #40, r20 #41):** a required key that
  DRIVES a rendered surface must be present AND non-empty — presence ≠ non-empty.
  The non-empty set is exactly `civilization_contribution` (blank → NO
  contribution box), `entity`, `status`, and `last_compiled` (blank → broken
  infobox identity/rows). EXEMPT — legitimately empty on a conformant page, so
  NOT flagged: `raw_documents` (empty for a support-only page with no ingested
  research file — §2.2/AC6; requiring it non-empty would make AC6(P2)
  unsatisfiable) and `aliases` (a page may have none). The check targets this
  named render-driving set, not every required key.

Conformant ⟺ the returned set is empty. Heading match is exact on the canonical
strings (MemPalace's dated heading is non-conformant until Phase 2 — IADA-I2).

**Cluster invariant (CFADA-r4 #12).** `investigation_topic` is reserved for
genuine multi-page clusters. The corpus gate (AC6/P2) additionally requires
every `investigation_topic` value to be shared by ≥2 active investigation pages;
a lone/self-topic value (main today carries several, e.g. hermes-agent,
google-open-knowledge-format) is a deficiency, so Phase 2 removes stray topics.
This is corpus-level (it needs cross-page counts), distinct from the per-page
`investigation_conformance`. **Primary invariant (R9, amendment 2026-07-09).**
Every multi-page cluster additionally carries **exactly one active**
`investigation_primary: true` page (§2.6); zero (in the retrofitted end state) or
≥2 active primaries in a multi-page cluster is a deficiency. Single-page
investigations omit `investigation_primary` (inert there); like the topic-sharing
rule, the primary check is conditional on the cluster having ≥2 active members,
so a lone topic is never forced to declare a primary.

**Corpus timing (no red merge).** Phase 1 asserts the predicate is correct
(a conformant fixture → ∅; missing-key, missing-heading, non-bold-lead,
out-of-order, and Integration-Packet-misordered fixtures → the right
deficiency) and that the new-investigation skeleton conforms. Phase 2 retrofits
all pages and flips AC6 to assert every **live-enumerated** active investigation
page conforms (IADA-I6). The hard corpus gate turns on only when satisfiable.

### 2.6 R9 — Single nav entry per investigation (investigation_primary)

`build_investigation_nav` (`build_site.py:1406`) today groups by
`investigation_topic_for(slug)`: a one-member topic renders a flat row; a
≥2-member topic (only Sakana today) renders an expandable `<details>` group with
a child link per page. R9 adds primary-selection ON TOP of that grouping — it
refines the multi-member branch, it does not replace grouping:

- **Single active primary (the collapse):** a multi-member cluster in which
  **exactly one active** member carries `investigation_primary: true` renders as
  a **single flat row** (the existing one-member code path), linking the primary
  page and labeled with the `investigation_topic`; the non-primary active
  members are OMITTED from the investigation nav. This is the guarded, lossy act
  (a page leaves the nav) and fires only on an explicit, unique, active primary.
- **Zero active primaries (fail-safe fallback):** unchanged — the expandable
  group with every active member. No page is hidden without a designated
  primary. This is the render for un-retrofitted clusters and the safe default.
- **Two or more active primaries (fail-closed):** ambiguous authoring. The
  RENDER defensively falls back to the expandable group (show all — never pick
  one arbitrarily), and the corpus conformance gate FAILS (AC10/P2 + the cluster
  primary invariant, §2.5). The builder never bricks; the deficiency is caught
  by a test, matching the R8 corpus-gate pattern.
- **Retired / non-investigation edges:** retired pages already drop from nav, so
  a cluster whose only primary is retired has zero *active* primaries → safe
  fallback (and conformance flags "active cluster, no active primary"). An
  `investigation_primary` on a single-page topic or a non-investigation page is
  inert (grouping never triggers there).

**Both navigation surfaces (CFADA-r18 #38).** Investigation pages render TWO nav
surfaces: the sidebar `build_investigation_nav` (`:1406`, grouped) and the bottom
category index `build_navbox` (`:1489`, injected `:2185`), whose investigation-tier
row today lists EVERY active investigation article flat (`:1497`). R9's collapse
applies to BOTH: for a multi-page cluster with a single active
`investigation_primary`, each surface shows ONE entry (the primary) and omits the
non-primary members; zero → all shown (fail-safe), ≥2 → all shown + conformance
fail. A shared cluster-representative selection drives both surfaces so they
cannot diverge — a sidebar that collapsed while the navbox still listed both
pages would violate the one-entry standard. AC10 asserts BOTH surfaces on the
live corpus.

**Companion discoverability (Option A).** The omitted non-primary page stays a
full conformant page reachable by (i) site search, (ii) direct link, and (iii) a
required editorial cross-link from the primary page's body/Sources — a Phase-2
data-only retrofit detail, no new Phase-1 machinery. AC10(P2) asserts the
cross-link exists so the collapse never orphans the companion.

**Ingest untouched (R5/R6).** `investigation_primary` is an author-set
frontmatter key edited in the page (Phase-2 retrofit); it is never
operator-supplied at ingest and the new-investigation skeleton never emits it,
so the ingest fail-closed guard and its pre-write quarantine set are unchanged.

**Fail-safe statement (R9).** The ONLY branch that removes a page from the
investigation nav is a multi-member cluster with exactly one active
`investigation_primary`. Zero or ≥2 → show all. No `else`/fall-through hides a
page. `investigation_primary` is primary IFF its frontmatter scalar, stripped
and lowercased, equals `true` (so `true` or `"true"` qualify; `false`,
`"false"`, `no`, `0`, a blank value, or an absent key are all NOT primary). It
MUST be an explicit `== "true"` test, never naive string-truthiness on the
quote-stripping `fm_val` helper — a non-empty `"false"` string is truthy and
would wrongly hide the companion (CFADA-r19 #39). So a malformed flag can only
ever ADD to the zero-primary (show-all) tally — it can never hide a page. AC10
proves the domain.

## 3. Acceptance criteria & named tests

| # | Phase | Criterion (risk) | Verification — named test (in a package.json-wired module) |
|---|---|---|---|
| AC1 | 1 | Topic Details row lists every `raw_documents` AND `superseded_raw_documents` entry (superseded included, marked), falling back to raw-INGESTED RESEARCH refs (`raw/inbox/...` uploads ∪ `…/tai-res-*.md` evaluations wherever placed, e.g. pageindex's `raw/civilization/external-landscape/…` — CFADA-r17 #35) only when both are empty — doctrine/provenance/absolute citations render in the source panel, NOT Topic Details (CFADA-r14 #31); no "Raw docs" label survives in `dist/`; for an ADD-with-supersedes topic (MemPalace) the older versions render marked, the newest primary, from the `supersedes:` comments (CFADA-r21 #43) (low) | py: `test_topic_details_lists_all_versions_incl_superseded`, `test_topic_details_marks_add_supersedes_newest_primary`, `test_topic_details_fallback_is_raw_ingested_only` |
| AC2 | 1 | Investigation-tier page renders no `.toc`; a ≥3-heading non-investigation page still renders one (med) | py: `test_investigation_pages_have_no_toc`; playwright |
| AC3 | 1 | Default ADD with a resolvable investigation `target_slug` appends + sets `stale_since`, `wiki/*.md` count unchanged, rebuilds; a non-investigation target appends WITHOUT a stale stamp (preserved) (high) | server: `test_add_default_appends_and_flags_stale`, `test_add_to_non_investigation_preserves_behavior` |
| AC4 | 1 | Fail-closed guard, full domain — default ADD with (a) no target, (b) retired/nonexistent target → REFUSE; (c) non-investigation target → APPENDS (no refuse/stale); new-investigation with (d) empty name OR a name whose compact/slug-driving form is empty (e.g. "!!!", "()"), (e) `slugify(name)` collides with an existing slug (active/tombstone), INCLUDING when the compact key differs (e.g. "Foo (Bar)" → slug `foo` vs existing `foo.md`), (f) name/entity/alias/cluster collision via the compact `collision_key` incl. case/whitespace/no-space/punctuation/parenthesis variants (e.g. "Sakana-AI", "Sakana (AI)" vs "Sakana AI"; "Mem Palace" vs "MemPalace"), against ACTIVE and RETIRED pages (a name matching the owainlewis tombstone's `TAI-RES-2026-006` alias → REFUSE, no reanimation — CFADA-r12 #28), (g) name = an existing `investigation_topic` cluster label (e.g. "Sakana AI") → REFUSE; (h) doc title ≠ operator name → NAME drives slug/entity+guard (no bypass); (i) distinct entities sharing a cluster (Sakana) → allowed; (j) absent subject → created (high) | server: `test_ingest_guard_domain` (cases a–j) |
| AC5 | 1 | New-investigation builds FROM the operator name (not the doc title), emits the R2 skeleton (bold-lead placeholder + `stale_since` + the EXACT `status: browser-ingested source; awaiting synthesis` string from §2.4/R6, not an abbreviation — CFADA-r21 #44, no auto `investigation_topic`); toggle defaults OFF, only creation path; `prospective_unassigned_slug` matches the creator (high) | server: `test_new_investigation_uses_operator_name`, `test_new_investigation_emits_canonical_skeleton`, `test_new_investigation_name_is_quarantined`, `test_ingest_still_requires_authoring`, `test_prospective_slug_matches_creator` |
| AC6 | 1 → 2 | **P1:** predicate → ∅ for a conformant fixture AND for a support-only fixture with EMPTY `raw_documents` (the Topic Details exemption — CFADA-r20 #41); exact deficiency for missing-key / EMPTY render-driving field (blank `civilization_contribution`/`entity`/`status`/`last_compiled` — CFADA-r19 #40) / missing-heading / non-bold-lead / out-of-order / Integration-Packet-misordered fixtures; skeleton conforms. **P2:** every live-enumerated active investigation page (i) conforms (R2), (ii) carries NO `investigation_topic` UNLESS ≥2 active pages share that exact value — the check is conditional (single-page investigations omit the field; it is never forced onto a lone topic — CFADA-r11 #25), AND (iii) has Topic Details covering ALL raw versions — `raw_documents` ∪ `superseded_raw_documents` includes every RAW INGESTED file for the topic — the browser-ingest `raw/inbox/...` uploads and the topic's TAI-RES evaluation versions wherever placed (incl. pageindex's `raw/civilization/external-landscape/…` — CFADA-r17 #35) — so no ingested version is lost. Supporting doctrine citations (`raw/transpara/...`, `raw/open-brain/...`, absolute `/Transpara/...`) stay in `sources` and render via the source panel/links, NOT forced into Topic Details (R3 is scoped to raw ingested files, not every citation — CFADA-r10 #24); a page with no ingested research file has EMPTY Topic Details in the end state (its doctrine citations render via the source panel, not the fallback). The empty-both fallback is SCOPED in Phase-1 machinery to raw-INGESTED sources (§2.2), so support-only pages have empty Topic Details from Phase 1 onward — AC6(P2) is satisfiable while Phase 2 stays data-only, and it checks no active investigation page presents doctrine `sources` refs as Topic Details (CFADA-r12 #29, r13 #30) (R3/R8 completeness; CFADA-r6 #17, r8 #20) (med) | py: `test_investigation_conformance_predicate`, `test_support_only_empty_raw_documents_conforms` (P1); `test_all_active_investigations_conform`, `test_investigation_topic_clusters_have_multiple_members`, `test_all_active_investigations_topic_details_complete` (P2) |
| AC7 | 1 | Builder imports no network/model client; a `stale_since` page renders the banner until cleared, with reason-neutral text (no Replace-specific "sources were replaced"/"authorization" wording) (med) | py: `test_builder_has_no_network_client`, `test_stale_banner_is_reason_neutral` |
| AC8 | 1 | MemPalace's rendered HTML changes in exactly three ways — the infobox label, the removed `.toc`, and the Topic Details supersession markers (older versions marked, newest primary, per AC1/C43 — CFADA-r22 #45) — no other: all 8 headings + contribution box still present (med) | py: `test_mempalace_render_diff_is_label_toc_and_supersession` |
| AC9 | 1 & 2 | Every new/edited Python test above is wired into `package.json` `test:py` (or lands in an already-wired module); full chain green, zero regression (low) | `npm run verify` exit 0 at each PR's reviewed head; `test_py_targets_are_wired` asserts the module list runs the new tests |
| AC10 | 1 → 2 | **R9 nav single-entry (P1, in the wired `test_build_site_nav.py`):** a multi-member `investigation_topic` fixture with exactly one active `investigation_primary` renders ONE flat nav row (primary link, no child rows); a zero-primary multi-member fixture renders the expandable group with every active child (fail-safe); a two-primary fixture renders the group AND the corpus cluster primary-invariant check (§2.5) reports the ≥2-primary deficiency — a corpus/cluster check exercised on the fixture, NOT the per-page `investigation_conformance` predicate (CFADA-r17 #36); a cluster whose only primary is retired → zero active primaries → group fallback AND the same corpus check flags "active cluster, no active primary"; a stray `investigation_primary` on a single-page topic is inert; a quoted/non-boolean flag (`"true"`, `"false"`, `yes`, `1`, blank) is parsed by an explicit `== "true"` test, so only a real `true` is primary and `"false"` never hides a page (CFADA-r19 #39). The SAME single-entry collapse applies to the bottom `build_navbox` investigation row, not just the sidebar (CFADA-r18 #38). **P2 (live corpus):** every live-enumerated multi-page cluster (Sakana today: `sakana-ai-evaluation` primary, `sakana-ai-adjacent-landscape` omitted from BOTH the sidebar nav and the bottom navbox yet reachable) has exactly one active `investigation_primary`, renders as a single primary entry on both surfaces, and its primary carries the editorial cross-link to each companion (med) | py: `test_multipage_cluster_with_primary_renders_single_row`, `test_cluster_without_primary_falls_back_to_group`, `test_multiple_primaries_flagged_and_group_rendered`, `test_retired_primary_falls_back_and_is_flagged`, `test_stray_primary_on_single_page_is_inert`, `test_navbox_investigation_row_collapses_by_primary`, `test_investigation_primary_strict_boolean` (P1); `test_all_multipage_clusters_have_exactly_one_primary`, `test_sakana_renders_single_primary_row`, `test_sakana_single_entry_in_sidebar_and_navbox`, `test_sakana_companion_reachable_and_cross_linked` (P2) |

**Gate satisfied-only-when (allowlist, phase-total):** every AC carries an
explicit, mandatory obligation per phase (AC6 and AC10 split into P1/P2 halves;
AC9 runs in both PRs) — no AC is optional and no PR may drop its assigned
obligation (CFADA-r5 #14). The Phase-1 PR is satisfied only when
AC1–AC5, AC6(P1), AC7, AC8, AC9, AC10(P1) are green at its reviewed head AND
`npm run verify` exits 0. The FINAL Phase-2 PR is satisfied only when AC6(P2)
and AC10(P2) (all-corpus) and AC9 are green; an intermediate split-cluster PR
asserts only that ITS OWN pages conform + AC9 (CFADA-r15 #33). The FO is
satisfied only when BOTH phases are. Any unproven assigned criterion ⇒ not
satisfied (IADA-I4).

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
- **Nav collapse is a guarded act (R9).** Allowlist: drop a cluster member from
  the nav ⟺ its cluster has exactly one active `investigation_primary`. Zero →
  show the full group (nothing hidden); ≥2 → show the full group + conformance
  failure. No page leaves the nav without a unique, explicit, active primary
  (§2.6). AC10 proves the domain; R9 is nav-only — no page is merged or retired.

## 5. Authorization packet

- **Bounded scope:** the §2.1 file plan; `transpara-ai/wiki` only; docs branch
  `feat/investigation-standard-design` off main @ `2c9e672`; Phase-1/2 code on
  their own `feat/` branches off `origin/main`; lifecycle to ready PR. **No
  code before Human Design Review approves this packet (stage 6).**
- **Forbidden:** any change to the authorization-artifact model or
  `secret_scan`; Replace/Remove/register semantics; non-investigation
  source-add behavior; ADD entering the authorization contract (Q4);
  LLM/network in the builder; reanimating the retired tombstone; force-merging
  Sakana (R9 collapses its NAV entry only — both pages persist as conformant
  pages); any Phase-2 content edit before Phase-1 merges; autonomous issue/PR
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
  emphasis is flagged — acceptable (the standard specifies bold). (e) The R9
  primary page's companion has reduced NAV discoverability (off the top-level
  list); mitigated by search + direct link + the required editorial cross-link
  from the primary (AC10/P2), and fully reversible (drop `investigation_primary`
  to restore the expandable group). Owner-accepted: Michael chose Option A over
  the discoverability-preserving Option B (FO §5). Fail-closed direction: absent
  a primary the group shows all (amendment 2026-07-09).

## 6. Two-phase delivery (one FO)

- **Phase 1 — machinery (code PR).** R3 (superseded union + raw-ingested-RESEARCH-scoped fallback) + R4 + R5 + R6
  + R7 banner + the conformance predicate + R9 nav single-entry + AC1–AC5, AC6(P1), AC7–AC9, AC10(P1). Server
  code ⇒ deploy = reset serving clone to main + `npm run build` + **restart**.
- **Phase 2 — retrofit (data-only PR[s]).** The 19 pages → R2 (R8), MemPalace
  heading generalized, bold leads, `stale_since` where needed, Sakana's `investigation_primary` + companion cross-link (R9), AC6(P2) + AC10(P2) on.
  Data-only ⇒ `npm run build`, **no restart**. It may be ONE all-19-page PR, or split by cluster — if split, each intermediate PR asserts ITS OWN pages conform + AC9, and the FINAL Phase-2 PR flips AC6(P2) to the all-corpus assertion (that test-flip is a small test edit, the only non-data change in Phase 2); the all-corpus AC6(P2) gate is satisfied only at that final PR (CFADA-r15 #33).

Each PR runs stages 7→11 (IAR → CFAR at exact head → ready → fresh ready-state
CFAR). Merge is Michael's (stage 12).

## Appendix — IADA (self-directed, v0.1.0 → v0.2.0)

Assessor: Claude (Opus 4.8), 2026-07-09. Adversarial, whole-domain. Findings
I1–I8 (fuzzy match, MemPalace-conforms, golden TOC, AC cherry-pick, predicate
under-definition, hardcoded-19, residual wording, AC4 collision domain) all
FIXED. Verdict v0.2.0: PASS — 0 blockers. Does not replace external CFADA.

## Appendix — CFADA rounds (Codex, materially independent of the Claude author)

Reviewer: Codex (`codex-cli 0.142.5`, gpt-5.5, xhigh). `codex exec review
--base origin/main`, bare, from the worktree. Each round cites the blob/commit
it AUDITED (the previous version's committed state); the repair lands in the
NEXT commit and is re-audited by the following round.

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

**Round 5 → FAIL, repaired v0.7.0** (packet blob `a15dc23a04f6ce1cb313d53f181ce091f5c66098`, commit `ce0d750`):
| # | Finding | Disposition |
|---|---|---|
| C13 | `norm()` kept internal punctuation and `slugify(name)` was compared only with page slugs — a new "Sakana-AI" would not collide with the "Sakana AI" cluster, leaving a duplicate-page path | FIXED — collision now compares `slugify` forms across entity ∪ aliases ∪ cluster label ∪ slugs (folds punctuation/spacing); AC4 case (f) adds the variant (§2.4, AC4). |
| C14 (P3) | The gate said "every AC assigned to exactly one phase" but AC6 (1→2) and AC9 (1&2) span phases — self-contradictory as a literal checklist | FIXED — reworded to "explicit mandatory obligation per phase" (§3). |

**Round 6 → FAIL** — audited at packet blob `1dd15d7ef19a36c98f03762850bb6f3d77aebf9d` (commit `82858b3`, the v0.7.0 state round 6 reviewed); repaired to v0.8.0:
| # | Finding | Disposition |
|---|---|---|
| C15 | "ADD unauthenticated" could be misread as dropping `require_authoring`, exposing browser writes | FIXED — FO v0.2.2 + §2.4/§2.1 state ADD retains the transport gate; "unauthenticated" = no single-use artifact only (AC5 `test_ingest_still_requires_authoring`). |
| C16 | The new operator `name` field was not quarantined before write/echo — a secret-shaped name could reach `wiki/<slug>.md` or a response ahead of `secret_scan` | FIXED — `quarantine_fields` over `name` before any derivation/write/echo (§2.4, §2.1, AC5 `test_new_investigation_name_is_quarantined`). |
| C17 | AC6(P2) checked R2 + clusters but not R3, so a retrofit could pass with incomplete `raw_documents` | FIXED — AC6(P2)(iii) asserts Topic Details covers all raw versions (no page left on the sources fallback); `test_all_active_investigations_topic_details_complete`. |

**Round 7 → FAIL** — audited at packet blob `750a9c1a2002b986153ef8b0952400a1398bbde2` (commit `6f4ea5d`, the v0.8.0 state); repaired to v0.8.1:
| # | Finding | Disposition |
|---|---|---|
| C18 | The appendix duplicated the Round 5 block, and its round headers were ambiguous about whether the cited commit was the audited or the repaired state — an inaccurate CFADA evidence trail | FIXED — duplicate removed; a convention note states each round cites the AUDITED blob/commit; Round 6/7 headers reworded. Audit-trail only, no design change. |

**Round 8 → FAIL** — audited at packet blob `8d822fdc108eab37eb2820dba7c79bed3fe58b5a` (commit `8f42d28`, the v0.8.1 state); repaired to v0.9.0:
| # | Finding | Disposition |
|---|---|---|
| C19 (P1) | The quarantine spec `{name, target_slug, note}` would REPLACE the existing Add quarantine set (which also covers `supersedes`, `external_urls`, filenames, payload bytes) — narrowing a secret-leak guard | FIXED — `name` is ADDED to the existing set (extended, never narrowed); §2.4. |
| C20 | Topic Details completeness checked only `raw/*` sources, not the allowed absolute `/Transpara/...` local sources the fallback also serves — links could vanish when the fallback turns off | FIXED — AC6(P2)(iii) covers every safe local source ref `safe_source_path` admits (§3). |
| C21 | `slugify` drops parenthesized text, so "Sakana (AI)" slipped the collision guard | FIXED — a dedicated `collision_key` folds all punctuation incl. parentheses without dropping text; AC4(f) adds the parenthesis case (§2.4, AC4). |

**Round 9 → FAIL** — audited at packet blob `84a0cf9b2cf56b81de97eff6cdd18b17e584847d` (commit `e74b7af`, the v0.9.0 state); repaired to v0.9.1:
| # | Finding | Disposition |
|---|---|---|
| C22 | The hyphen-folding `collision_key` missed no-space/space variants ("Mem Palace" → `mem-palace` ≠ MemPalace's `mempalace`), leaving an R1 duplicate path | FIXED — `collision_key` is now the COMPACT alphanumeric-only form ("MemPalace"/"Mem Palace" → `mempalace`); AC4(f) adds the no-space case (§2.4, AC4). |

**Round 10 → FAIL** — audited at packet blob `59c91eb4f69ea8da625a2b8c9950a6b0a882d625` (commit `7650589`, the v0.9.1 state); repaired to v0.9.2:
| # | Finding | Disposition |
|---|---|---|
| C23 (P1) | The guard compared `collision_key` but the created file is `slugify(name)`, which drops text ("Foo (Bar)" → `foo`) — the compact key could differ while `slugify` targets an existing slug, a non-fail-closed create path | FIXED — the guard ALSO checks `slugify(name)` against all slugs (active + tombstone), the ground truth for the created file; either collision refuses (§2.4, AC4e). |
| C24 | Completeness demanded every local `sources` ref be in `raw_documents`, forcing supporting doctrine citations (e.g. `raw/open-brain/2026-06.md`) into Topic Details beyond R3's raw-ingested scope | FIXED — completeness scoped to RAW INGESTED files; supporting citations stay in `sources` and render via the source panel (§3). |

**Round 11 → FAIL** — audited at packet blob `242a054e918c81ca65d41b08194e6d455b18f15f` (commit `c8b4f85`, the v0.9.2 state); repaired to v0.9.3 (no P1 — the design is at zero blockers; these are refinements):
| # | Finding | Disposition |
|---|---|---|
| C25 | AC6(P2) could be read as "every page must have a shared `investigation_topic`," conflicting with R2/§2.5 (single-page investigations omit it) | FIXED — AC6(ii) made conditional: no page carries `investigation_topic` unless ≥2 pages share it (§3). |
| C26 | An explicit new-investigation name with no slug/collision characters ("!!!", "()") passed the non-empty check but `slugify` falls back to a generic page and `collision_key` is empty | FIXED — refuse when the compact `collision_key` is empty or `slugify` falls back to a default (§2.4, AC4d). |
| C27 | FO R3 verified only `raw_documents`, so an FO-keyed implementation could drop Replace-`superseded_raw_documents` from Topic Details | FIXED — FO v0.2.3 R3 covers `raw_documents` ∪ `superseded_raw_documents`; packet rebound to blob `20d4f35f…`. |

**Round 12 → FAIL** — audited at packet blob `7406d90ddd7fc2c83a45a82447fdebcc79f44b22` (commit `0ab7ccb`, the v0.9.3 state; no P1 — zero blockers, 3rd consecutive round); repaired to v0.9.4:
| # | Finding | Disposition |
|---|---|---|
| C28 | The collision set compared active entities/aliases but only tombstone SLUGS — a new investigation under a retired page's alias (owainlewis tombstone's `TAI-RES-2026-006`) could reanimate a retired subject | FIXED — the set now includes RETIRED pages' entity/aliases/cluster; AC4(f) covers it (§2.4, AC4). |
| C29 | A support-only page (no ingested file) on the `sources` fallback could surface doctrine citations in Topic Details while AC6 passed | FIXED — the fallback is Phase-1 transitional only; end-state Topic Details for support-only pages is empty (citations in the source panel); AC6(P2) checks it (§3). |

**Round 13 → FAIL** — audited at packet blob `e81f634d9aae78451d0fdb7b4168b41c878aef82` (commit `5eba92b`, the v0.9.4 state; no P1 — 4th consecutive zero-blocker round); repaired to v0.9.5:
| # | Finding | Disposition |
|---|---|---|
| C30 | The C29 wording made AC6(P2) unsatisfiable: it required support-only pages to have empty Topic Details, but the fallback is preserved in Phase-1 code and Phase 2 is data-only, so a data-only retrofit cannot stop the fallback rendering doctrine citations | FIXED — the fallback is SCOPED in Phase-1 machinery to raw-INGESTED sources only; support-only pages get empty Topic Details from Phase 1, so AC6(P2) is satisfiable with Phase 2 data-only (§2.1, §2.2, §3, §6). |

**Round 14 → FAIL** — audited at packet blob `93443287273846c16e01d370f382c15824c19b4f` (commit `6d988ed`, the v0.9.5 state; no P1 — 5th consecutive zero-blocker round); repaired to v0.9.6:
| # | Finding | Disposition |
|---|---|---|
| C31 | AC1 still said "fall back to local `sources`" (the old broad behavior), contradicting §2.2/AC6's raw-ingested-scoped fallback — an implementer following AC1 would reintroduce C29/C30 | FIXED — AC1 now specifies the raw-INGESTED-scoped fallback, consistent with §2.1/§2.2/§2.5/§6 (§3). |

**Round 15 → FAIL** — audited at packet blob `7ad1605220958fb39fb089d3010fa7265d0f51a7` (commit `8c2f82a`, the v0.9.6 state; no P1 — 5th consecutive zero-blocker round); repaired to v0.9.7:
| # | Finding | Disposition |
|---|---|---|
| C32 | The raw-ingested filter applied only to the fallback; `raw_documents` was taken verbatim, so a mis-placed doctrine ref (hermes-agent) would still render as Topic Details, breaking the invariant | FIXED — the Topic Details renderer filters its ENTIRE input (union + fallback) to raw-ingested refs; Phase-2 additionally tidies `raw_documents` (§2.2). |
| C33 | "Split by cluster" contradicted the all-corpus AC6(P2) gate and the data-only scope (a test-flip) | FIXED — the all-corpus AC6(P2) gate is final-Phase-2-PR only; intermediate cluster PRs assert their own pages; the test-flip is a named small edit (§3, §6). |

**Round 16 → audited at packet blob `4bd40ec07c17360328df9da5c8fead0bab890d83` (commit `3ac5ade`, the v0.9.7 state) — no P1; 6th consecutive zero-blocker round.** One P2 (C34), carried as a named residual:
| # | Finding | Disposition |
|---|---|---|
| C34 | The §2.2 raw-ingested classifier is stated as `raw/inbox/`; a TAI-RES evaluation doc relocated outside inbox (e.g. `raw/civilization/external-landscape/`) would be wrongly excluded from Topic Details | RESOLVED at v0.10.0 — re-raised with a live corpus case (`wiki/pageindex.md` → `raw/civilization/external-landscape/tai-res-2026-007-pageindex-evaluation.md`) in the amendment CFADA (r17 #35) and FIXED: the classifier is now the research-identity allowlist (`raw/inbox/...` uploads ∪ `…/tai-res-*.md` evaluations wherever placed), doctrine/provenance/absolute/URL excluded; pinned by AC1/AC6 against the real corpus. See the amendment CFADA rounds below. |

## Appendix — Amendment log (post-CFADA-PASS)

**v0.10.0 — 2026-07-09 — AMENDMENT (not a CFADA round).** After the v0.9.7 CFADA
PASS, Michael directed (channel-A, this session) that "a single entry per
investigation" be honored at the NAV layer for the sole multi-page cluster
(Sakana) via `investigation_primary` — the nav-semantics decision was **Option A**
(one primary row; companion reachable but off the top-level nav). This amendment:

- adds **R9** to the FO (v0.3.0) and this packet (§2.6, §2.1, §2.5) — the
  single nav-entry mechanism with fail-closed primary invariants;
- revises **R8** (FO + §2.1 Phase-2) — Sakana renders one primary nav row, both
  pages still conformant/reachable;
- adds **AC10** (P1 nav-logic on fixtures; P2 live Sakana), the cluster primary
  invariant (§2.5), and the §4 fail-safe bullet;
- supersedes the `investigation_primary` point-fix that was in flight as
  transpara-ai/wiki#71 (closed redundant 2026-07-09) — the standard now owns it.

**Truth-object consequence.** Per the TLC birth-and-mutation rule this edit
changes the packet blob, so the v0.9.7 CFADA PASS (blob
`4bd40ec07c17360328df9da5c8fead0bab890d83`) is STRANDED on the old bytes and does
NOT extend to v0.10.0. **v0.10.0 must re-run IADA → CFADA** (Claude author →
Codex reviewer, materially independent) to zero design blockers before returning
to Human Design Review (stage 6). No code before that re-audited packet is
human-approved.

### Amendment CFADA rounds (Codex, materially independent of the Claude author)

Reviewer: Codex (`codex-cli 0.142.5`, gpt-5.5, xhigh). `codex exec review --base origin/main`, bare, from the worktree.

**Round 17 → FAIL (amendment round 1)** — audited packet blob `19c3794c93036ef20661d7049b9d87f7a4e0a9ed` (HEAD `1df0074`, the v0.10.0 post-IADA state); repaired in the next commit:
| # | Finding | Disposition |
|---|---|---|
| C35 (P2) | The §2.2 raw-ingested classifier (`raw/inbox/` only) drops research docs stored elsewhere — live case `wiki/pageindex.md` → `raw/civilization/external-landscape/tai-res-2026-007-…`, making AC6(P2)(iii) unsatisfiable and stripping the page's primary research link | accepted-repaired — classifier broadened to the research-identity allowlist (`raw/inbox/...` uploads ∪ `…/tai-res-*.md` evaluations wherever placed); doctrine/provenance/absolute/URL still excluded (§2.2, §2.1, AC1, AC6). Closes the carried C34. |
| C36 (P2) | AC10/P1 routed the ≥2-primary deficiency through the per-page `investigation_conformance` predicate, but §2.5 keeps cluster invariants corpus-level — an implementer could not satisfy both | accepted-repaired — AC10 now routes the primary-count (and retired-primary) deficiency through the corpus cluster primary-invariant check (§2.5), exercised on the fixture; not the per-page predicate. |
| C37 (P3) | §6 phase summary still listed Phase-1 AC1–AC9 / Phase-2 AC6 only, omitting R9/AC10 — a team following §6 could skip the nav-collapse + live-Sakana tests | accepted-repaired — §6 now lists R9 + AC10(P1) in Phase 1 and Sakana `investigation_primary` + AC10(P2) in Phase 2. |

All three accepted-repaired (0 rejected, 0 waived); round 18 re-audited the new blob SHA.

**Round 18 → FAIL (amendment round 2)** — audited packet blob `4501955c836ecba65c72ce3dd60042a36e29641a` (HEAD `3f6c71f`, the r17-repaired state); repaired in the next commit:
| # | Finding | Disposition |
|---|---|---|
| C38 (P2) | R9 was scoped to the sidebar `build_investigation_nav` only; the bottom index `build_navbox` (`:1489`, injected `:2185`) lists every active investigation article flat (`:1497`), so Sakana would collapse in the sidebar but still show two entries in the footer navbox — the one-entry standard unmet across surfaces | accepted-repaired — R9 extended to BOTH nav surfaces via a shared cluster-representative selection (§2.6, §2.1); AC10 asserts both on the live corpus (`test_navbox_investigation_row_collapses_by_primary`, `test_sakana_single_entry_in_sidebar_and_navbox`). |

C38 accepted-repaired (0 rejected, 0 waived); round 19 re-audited the new blob SHA.

**Round 19 → FAIL (amendment round 3)** — audited packet blob `f720de0821b67b1efff8d0fb9495681d25c4b1db` (HEAD `200eb37`); repaired in the next commit:
| # | Finding | Disposition |
|---|---|---|
| C39 (P2) | The R9 fail-safe claim assumed `investigation_primary` parses strictly, but the existing `fm_val` helper returns quote-stripped STRINGS, so naive truthiness would read `"false"`/`no` as primary and hide the companion — fail-OPEN | accepted-repaired — §2.6 pins an explicit `== "true"` parse (only `true`/`"true"` qualify; `false`/`"false"`/`no`/`0`/blank/absent → not primary), never `fm_val` truthiness; AC10 test `test_investigation_primary_strict_boolean`. |
| C40 (P2) | `investigation_conformance` checked MISSING required keys but not EMPTY ones — a blank `civilization_contribution:` renders no contribution box yet passed the presence-only check, so AC6 could pass a non-rendering page (pre-existing predicate gap, surfaced by the full re-audit) | accepted-repaired — §2.5 predicate now flags empty required render-driving fields (presence ≠ non-empty); AC6(P1) adds the empty-field fixture. |

Both accepted-repaired (0 rejected, 0 waived); round 20 re-audited the new blob SHA.

**Round 20 → FAIL (amendment round 4)** — audited packet blob `32208c051a95d712069b80b731598ee9eb4dc675` (HEAD `bf0460d`); repaired in the next commit:
| # | Finding | Disposition |
|---|---|---|
| C41 (P2) | The r19 empty-field fix ("every required field non-empty") contradicted §2.2/AC6, which allow EMPTY Topic Details for support-only pages — since `raw_documents` is a required field, AC6(P2) became unsatisfiable for a page with no ingested research file (would force fake or doctrine refs) | accepted-repaired — the non-empty check is scoped to a named render-driving set (`civilization_contribution`, `entity`, `status`, `last_compiled`); `raw_documents` and `aliases` are EXEMPT (legitimately empty); AC6(P1) adds a support-only empty-`raw_documents` conformant fixture. |

C41 accepted-repaired (0 rejected, 0 waived); round 21 re-audited the new blob SHA.

**Round 21 → FAIL (amendment round 5)** — audited packet blob `92cbfd3a3543ed9fd12705c4d006179137dffb8d` (HEAD `fcc4a5e`); repaired in the next commit. All three are pre-existing v0.9.7 gaps surfaced by the full-packet re-audit (the v0.10.0 gate binds to the whole blob):
| # | Finding | Disposition |
|---|---|---|
| C42 (P2) | The FO "hex-free raw filenames" constraint isn't enforced by R5/R6, which still append a sha12 to browser uploads — no AC catches it | accepted-repaired (scope-clarified) — §2.1 UNTOUCHED row now states the constraint is a pre-existing environmental secret-scan hygiene note re: bare-hex legacy names, NOT an R5/R6 deliverable of this FO; browser upload naming is unchanged. |
| C43 (P2) | ADD-with-supersedes topics (MemPalace) keep every version in `raw_documents` with supersession only in `sources`/`raw_documents` comments, so a union-only renderer could pass AC1 while leaving older versions unmarked / not newest-primary | accepted-repaired — §2.2 pins that the marking is derived from the `supersedes:` annotations, not only `superseded_raw_documents`; AC1 adds `test_topic_details_marks_add_supersedes_newest_primary`. |
| C44 (P2) | AC5 abbreviated the skeleton status to `awaiting synthesis`, but §2.4/R6/FO require the exact `browser-ingested source; awaiting synthesis` — an implementation could satisfy AC5 yet violate R6 | accepted-repaired — AC5 now pins the exact status string. |

All three accepted-repaired (0 rejected, 0 waived); round 22 re-audited the new blob SHA.

**Round 22 → FAIL (amendment round 6)** — audited packet blob `bbaad7e48afcae42a41332cb106497cb86cf11cd` (HEAD `d3c5910`); both findings are consequences of the r21 repairs; repaired in the next commit:
| # | Finding | Disposition |
|---|---|---|
| C45 (P2) | The C43 MemPalace supersession-marking fix broke AC8's "exactly TWO render changes" claim — marking the older MemPalace versions is a THIRD change, so AC1 and AC8 could not both pass | accepted-repaired — AC8 now expects exactly three changes (label, `.toc` removal, supersession markers); test renamed `test_mempalace_render_diff_is_label_toc_and_supersession`. |
| C46 (P2) | C42 clarified the hex-free scope in the packet, but the FO constraint line still read as a normative sha12 ban; the FO binds, so implementers following it get contradictory instructions | accepted-repaired — the FO constraint narrowed to BARE-hex session-authored/renamed names; the browser descriptive-stem+sha12 scheme is named pre-existing and unchanged. FO → v0.3.0 rev (blob re-pinned). |

Both accepted-repaired (0 rejected, 0 waived); round 23 re-audited the new blob SHA.

**Round 23 → PASS (amendment round 7)** — audited packet blob `f54544fa444774a2ea12e03843d426563afd9ce1` (HEAD `45b1151`, the r22-repaired state): **0 design blockers** — Codex "did not find an actionable inconsistency or implementation-breaking issue introduced by these documents." The r22 repairs (AC8 three-way diff, FO hex-free narrow) are confirmed clean.

### Amendment CFADA VERDICT — PASS

**gate: CFADA — PASS, 0 design blockers** (the v0.10.0 amendment). Author family: **Claude (Opus 4.8)**. Reviewer family: **Codex** (`codex-cli 0.142.5`, gpt-5.5, xhigh) — materially independent of the author lineage (provider openai). Command: `codex exec review --base origin/main`, bare, from the worktree; **7 amendment rounds (17–23)**.

**Packet binding (gate credit):** the round-23-audited bytes — v0.10.0, packet blob `f54544fa444774a2ea12e03843d426563afd9ce1` (HEAD `45b1151`) — which returned **zero design blockers**. Any post-pass bookkeeping note is documentation; per the truth-object rule credit attaches to those audited bytes.

**FO binding:** FO-WIKI-INVESTIGATION-STANDARD v0.3.1, blob `62abaf4e9a5909c8003379a95046bdc408402b25`.

**Three fidelities:** internal coherence **PASS** (every contradiction found across rounds 17–23 repaired — the R9 nav mechanism, both nav surfaces, strict-boolean parse, the render-driving conformance set, ADD-supersedes marking, AC8/hex-free reconciliation); packet-vs-FO **PASS** (R9 traces to FO R9; R1–R8 unchanged in intent; the amendment names its new scope); FO-vs-source **PASS** (R9 derives from Michael's archived 2026-07-09 Option-A nav decision, FO §5).

**Journey:** IADA (6 repairs) → CFADA rounds 17–23. Findings **C35–C46** (12), all **accepted-repaired** (0 rejected, 0 waived); round 23 clean. Notable: C38 (a second nav surface, `build_navbox`), C39 (string-truthiness fail-open), and two fix-induced regressions caught and reconciled (C41, C45).

**Non-authorizations:** this CFADA PASS authorizes no code, grants no authority, marks no PR ready, closes no issue/risk, and does not substitute for Human Design Review. Code begins only after Human Design Review (stage 6, Michael) approves.

**Ready for Human Design Review (stage 6): YES** — 0 design blockers at the audited v0.10.0 bytes.

**Post-pass bookkeeping.** Recording this PASS (the status flip, this verdict, the banner) is documentation that changes the packet blob without changing the design. The confirming rounds 24–25 found the DESIGN and frontmatter clean at the post-pass bytes; their only findings were documentation-consistency fixes, all applied here — C47 (an unquoted `: ` in the `status:` scalar → invalid YAML, verified fixed via `yaml.safe_load` on both docs), C48 (a stale "re-audit pending" line in the historical v0.9.7 appendix), and C49 (this note must not self-claim an in-document exact-head confirmation). The design PASS credit binds to the round-23-audited design bytes `f54544f`. **Exact-head gate verification for the pushed head is the posted `cross-family-adversarial-review` commit status on PR #70 — not a claim inside this mutable document.**

## Appendix — CFADA VERDICT (v0.9.7, historical)

> ⚠️ **SUPERSEDED BY AMENDMENT v0.10.0 (2026-07-09).** The PASS recorded below
> binds to the **v0.9.7** bytes (blob `4bd40ec07c17360328df9da5c8fead0bab890d83`)
> and does **not** cover v0.10.0's R9/R8 amendment. It is retained as the
> historical gate record for v0.9.7; the amended packet re-runs IADA → CFADA
> (see the Amendment log above). Gate state at v0.10.0: **re-PASS — 0 blockers at the round-23 blob `f54544fa444774a2ea12e03843d426563afd9ce1`; see the Amendment CFADA VERDICT above.**

**gate: CFADA — PASS, 0 design blockers.** Author family: **Claude (Opus 4.8)**. Reviewer family: **Codex** (`codex-cli 0.142.5`, gpt-5.5, xhigh) — materially independent of the author lineage (independence floor satisfied; provider openai). Command: `codex exec review --base origin/main`, bare, from the worktree; **16 rounds**.

**Packet binding (gate credit):** the round-16-audited bytes — v0.9.7, blob `4bd40ec07c17360328df9da5c8fead0bab890d83`, commit `3ac5ade` — which returned **zero design blockers**. This v0.9.8 record is post-pass bookkeeping; per the truth-object rule credit attaches to those audited bytes, not to this note.

**FO binding:** FO-WIKI-INVESTIGATION-STANDARD v0.2.3, blob `20d4f35f89299e0da0f0d96cc8b65fb09fe5628e`, confirmed channel-A 2026-07-09.

**Three fidelities:** internal coherence **PASS** (test-first ACs with `risk_class` + named tests + allowlist gate predicate; every contradiction found across 16 rounds repaired); packet-vs-FO **PASS** (R1–R8 all trace to ACs; nothing material dropped; ADD-auth / superseded / MemPalace-conformance re-aligned to the FO); FO-vs-source **PASS** (the FO faithfully derives from Michael's archived 2026-07-08 request + the plan-mode pre-design content hash).

**Journey:** IADA (v0.2.0, 0 blockers) → CFADA rounds 1–16. **Two P1 blockers** — r8 C19 (a quarantine-set narrowing the fix itself introduced) and r10 C23 (a generated-slug collision gap) — were caught, fixed, and re-verified clean; **rounds 11–16 (six consecutive) returned zero blockers**. 34 findings (C1–C34), all accepted-repaired except the named residuals.

**Residual risks (named, non-blocking):** (a) [C34] the raw-ingested classifier's exact path-set (conceptual; pinned by tests); (b) operator-recoverable over-collision stall (§5a); (c) manual `stale_since` clearing (§5b); (d) Phase-2 prose quality is judgment, not gated (§5c).

**Non-authorizations:** this CFADA PASS authorizes no code, grants no authority, does not mark any PR ready, does not close any issue/risk, and does not substitute for Human Design Review. Code begins only after Human Design Review (stage 6, Michael) approves.

**Ready for Human Design Review (stage 6): YES** — 0 design blockers at the audited v0.9.7 bytes. *(Superseded by the v0.10.0 Amendment CFADA VERDICT above — re-PASS, 0 blockers at round 23; this appendix is the historical v0.9.7 record.)*
