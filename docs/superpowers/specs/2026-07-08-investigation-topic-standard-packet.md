---
doc_id: TAI-WIKI-INVESTIGATION-STANDARD
title: One canonical page per investigation — Investigation Topic Standard (TLC Design Packet)
doc_type: design
version: 0.3.0
status: draft (IADA-passed; CFADA-r1 repaired; re-audit pending)
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
> (explicit new-investigation intent AND subject proven absent); every other
> path appends or refuses — never creates. The builder stays no-LLM,
> no-network. Two-phase delivery (one FO, §6): Phase 1 machinery (code PR),
> Phase 2 retrofit (data-only PR[s]). Repaired through IADA (v0.2.0) and CFADA
> round 1 (v0.3.0) — the fail-open lanes (fuzzy default-add, "MemPalace already
> conforms", the non-investigation-add regression, presence-only conformance)
> were removed.

## 1. Survey — measured, not assumed (file:line evidence)

- **Infobox** (`build_site.py:1504` `build_infobox`): rows Tier/Status/Last
  compiled/Also known as/Sources/**Raw docs** — the "Raw docs" label is a
  single literal at `:1530`; its list comes from `raw_doc_refs(fm)`
  (`:953`–`968`: `raw_documents` else local `sources`). R3's whole surface.
- **TOC** (`build_site.py:820` `build_toc`, threshold ≥3 headings at `:823`):
  injected for every non-home page — `toc = "" if is_home else
  build_toc(toc_tokens)` (`:2181`), placed at `:2211`. The **contribution box
  is already tier-gated** at `:2210` (`if meta.get("tier") ==
  "investigation"`); the TOC is NOT — R4's exact seam. MemPalace has 8 `##`
  headings, so it renders a TOC today; R4 removes it (the FO screenshot's
  struck-through Contents box).
- **Contribution box** (`build_site.py:1538`): from `civilization_contribution`
  frontmatter; investigation-tier only. This IS the R2 "Civilization
  Contribution" (a callout, not a `##` heading).
- **Lead paragraph** = the bold first paragraph, split at `:2208`–`:2209`.
  This IS the R2 "Summary" (no heading).
- **Ingest target list** (`ingest_server.py:143` `article_records`): the Add
  form/API offers EVERY non-retired article of ANY tier as a valid target
  (architecture/concept/foundational included). So the ADD-default change must
  NOT refuse non-investigation targets (CFADA-r1 #1) — those adds are
  legitimate source updates and keep today's behavior.
- **Ingest routing** (`ingest_server.py:802` `handle_ingest`): no
  `target_slug` → `create_article_from_source()` (`:865`–`867`) mints a slug
  from the doc **title** (`slugify`, `:602`), hardcodes `tier: investigation`
  (`:621`), and emits a `## Placement` / `## Source Access` stub with
  `investigation_topic: <title>` auto-set; a PROVIDED `target_slug` appends via
  `append_sources_to_article` (`:585`) + `append_raw_documents_to_article`
  (`:594`), dedup-safe through `append_frontmatter_list_items` (`:542`).
  `prospective_unassigned_slug` (`:116`) mirrors the creator.
- **stale_since** (`ingest_ops.py`): set only by `replace_source` at `:961`
  via `_set_scalar` (`:735`); cleared via `_drop_scalar` (`:743`, at `:976`);
  banner at `build_site.py:2200`–`2204`. Append helpers set nothing — R5's gap.
- **No-LLM/no-network builder**: `build_site.py:6` docstring; no HTTP/model
  client imported. R7's existing invariant.
- **Corpus**: 20 investigation pages — 19 active + the retired owainlewis
  tombstone. **None is literally conformant to the generalized standard** —
  MemPalace is the closest content model but its heading is the dated
  `## What Changed With TAI-RES-2026-004`, not the standard's
  `## What Changed with the Research` (R2/R8 gap; MemPalace is retrofitted in
  Phase 2 with the rest).

## 2. The contract

### 2.1 File plan

| Phase | Action | File | Change |
|---|---|---|---|
| 1 | EDIT | `compile/build_site.py` | **R3:** relabel infobox row `"Raw docs"` → `"Topic Details"` (`:1530`). **R4:** `toc = "" if is_home or meta.get("tier")=="investigation" else build_toc(...)` (`:2181`), mirroring the contribution gate at `:2210`. **R2 predicate:** `investigation_conformance(slug)` (pure, read-only; returns missing frontmatter keys + missing/out-of-order required headings + empty-lead; consumed by tests, not a build-fail). |
| 1 | EDIT | `compile/ingest_server.py` | **R5/R6/R1:** `handle_ingest` intent model + fail-closed guard (§2.4). Default lane requires an explicit resolvable `target_slug` (any tier); appends; stamps `stale_since` **only for investigation targets**; non-investigation adds keep today's behavior; creates nothing. Explicit new-investigation emits the R2 skeleton iff the subject is proven absent. `create_article_from_source` → canonical skeleton, no auto `investigation_topic`. Keep `prospective_unassigned_slug` (`:116`) in lockstep. |
| 1 | EDIT | `compile/ingest_ops.py` | `set_article_stale(root, slug, now)` wrapping `_set_scalar(..., "stale_since", ...)` — one primitive reused by ADD and Replace; no new op, no authorization contract (Q4). |
| 1 | EDIT | `ingest_page()` region in `compile/build_site.py` | A "This is a new investigation" toggle (default OFF) reveals a name field and is the ONLY path to creation; the default Add flow targets the selected existing page. House style, both themes. |
| 1 | ADD/EDIT | `compile/test_build_site*.py`, `compile/test_ingest_server.py`, `tests/*.spec.js` | AC1–AC5, AC6(P1), AC7–AC9 (§3). |
| 2 | EDIT | `wiki/<each active investigation>.md` (19, incl. MemPalace) | Retrofit to the R2 schema (incl. generalizing MemPalace's "What Changed" heading); `raw_documents` lists every raw file; `stale_since` where the summary needs re-derivation; Sakana pair conformed, `investigation_topic: Sakana AI` retained on both. Data-only. |
| 2 | EDIT | `compile/test_build_site*.py` | Flip AC6 to assert **every live-enumerated** active investigation page conforms (frontmatter + ordered headings). |
| — | UNTOUCHED | authorization artifact semantics, `secret_scan`, Replace/Remove/register op logic, **non-investigation source-add behavior**, arc view, board, engine, refresh timer, the retired tombstone | Forbidden §5. |

### 2.2 R3 — Topic Details (infobox rename)

`row("Raw docs", …)` → `row("Topic Details", …)` at `:1530`. Data source
unchanged (`raw_doc_refs` yields every `raw_documents` entry, all versions).
Grep-proven single occurrence. AC1 asserts the rendered investigation infobox
has a "Topic Details" row and that no "Raw docs" label survives in `dist/`.

### 2.3 R4 — No in-topic Table of Contents

One allowlist branch at `:2181`: investigation-tier → `toc = ""`; else →
`build_toc`. Non-investigation pages untouched. Sits beside the identical
contribution tier-gate at `:2210` so the two cannot drift. AC2: an
investigation page's HTML has no `.toc`; a ≥3-heading non-investigation page
still does.

### 2.4 R5/R6/R1 — Ingest ADD-default + canonical new-page + fail-closed guard

**FO deferred question resolved:** ADD is a **routing change in
`ingest_server.py`**, not a new `ingest_ops` op — Q4 keeps ADD unauthenticated,
so it must not enter the authorization-artifact contract every `ingest_ops` op
carries; the append machinery already lives in `ingest_server.py`. Only the
`stale_since` stamp reaches into `ingest_ops`, via the shared
`set_article_stale` helper (byte-identical to Replace's stamp).

**Intent model** — `handle_ingest` reads a `new_investigation` flag (default
false):

- **Default (add to an existing page).** REQUIRES an explicit `target_slug`
  naming an existing **active** page (any tier). On match: append
  `raw_documents` + `sources` (dedup via `append_frontmatter_list_items`); if
  the target is `tier: investigation`, also `set_article_stale`; rebuild —
  **create nothing**. Adds to existing **non-investigation** pages keep today's
  behavior exactly (no stale stamp, no investigation guard) — this FO is scoped
  to investigations (CFADA-r1 #1). On absent `target_slug`, or one naming a
  retired / non-existent page: **REFUSE** ("select an existing topic, or check
  'new investigation'"). IADA-I1: no fuzzy title auto-match — an explicit
  resolved target is strictly more fail-closed and cannot mis-route.
- **Explicit new-investigation.** `create_article_from_source` emits the R2
  skeleton, but **REFUSES** unless the subject is proven absent: refuse if the
  derived slug collides with any existing page (active OR retired tombstone),
  or the normalized entity/title/alias matches any existing **active**
  investigation page (case- and whitespace-insensitive). Otherwise create with
  `stale_since`, `status: browser-ingested source; awaiting synthesis`, and no
  auto `investigation_topic`. Sakana's two distinct entities never collide.

**Fail-safe statement.** The ONLY branch that creates a page is
`new_investigation == true` AND the subject is proven absent. The default lane
appends (any tier) or refuses (no resolvable target); ambiguous and colliding
inputs refuse. No `else`/fall-through creates. AC4 proves the whole domain.

**stale_since lifecycle (R7).** An investigation ADD stamps `stale_since`; the
banner renders "synthesis stale — re-derivation pending". A governed authoring
pass edits the page (re-derives Summary + affected sections) and drops
`stale_since` (same `_drop_scalar` path Replace uses at `:976`). No
automated/LLM regeneration — the builder has no model/network path (AC7).

### 2.5 R2/R8 — Canonical schema, the conformance predicate, corpus timing

**Normative schema (the "standard").** Required frontmatter keys:
`entity`, `aliases`, `tier: investigation`, `status`, `last_compiled`,
`civilization_contribution`, `raw_documents`, `current_research_version`,
`sources` (`investigation_topic` only for a declared cluster). Required body:
a **non-empty lead paragraph** before the first `##` (the Summary), and the
`##` headings `What Changed with the Research`, `The Boundary`,
`Capability Read`, `Benchmark Reality`, `Sources & Provenance`
(`Integration Packet` optional), rendered **in that canonical order**. The
Civilization Contribution renders from the `civilization_contribution` key
(not a heading).

**`investigation_conformance(slug)`** (concrete, so it is verifiable): returns
(missing required frontmatter keys) ∪ (missing required `##` headings) ∪
(empty-lead flag) ∪ (out-of-order flag). **Order (CFADA-r1 #3):** filter the
page's heading sequence to the required headings; they must appear as a
subsequence in the canonical order above (allowed-optional extras such as
`## Placement` / `## Decision Record` may be interspersed; `Integration Packet`
optional). Conformant ⟺ the returned set is empty. Heading match is exact on
the canonical strings (so MemPalace's dated heading is non-conformant until
Phase 2 generalizes it — IADA-I2).

**Corpus timing (no red merge).** Phase 1 asserts only that the predicate is
correct (a synthetic conformant fixture → empty; synthetic missing-key,
missing-heading, empty-lead, and **out-of-order** fixtures → the right
deficiency) and that the new-investigation skeleton is conformant. Phase 2
retrofits all pages (MemPalace included) and flips AC6 to assert every
**live-enumerated** active investigation page
(`glob wiki/*.md`, `tier==investigation`, not `retired_on`) conforms. The hard
corpus gate turns on only when the corpus can satisfy it. IADA-I6: enumeration
is live, never a hardcoded "19" or a page list.

## 3. Acceptance criteria & named tests

| # | Phase | Criterion (risk) | Verification — named test |
|---|---|---|---|
| AC1 | 1 | Infobox row reads "Topic Details" and lists every `raw_documents` entry; no "Raw docs" label survives in `dist/` (low) | py: `test_infobox_topic_details_label` |
| AC2 | 1 | Investigation-tier page renders no `.toc`; a ≥3-heading non-investigation page still renders one (med) | py: `test_investigation_pages_have_no_toc`; playwright: `investigation page has no contents box` |
| AC3 | 1 | Default ADD with a resolvable investigation `target_slug` appends `raw_documents`+`sources`, sets `stale_since`, leaves the `wiki/*.md` count unchanged, rebuilds; a non-investigation target appends WITHOUT a stale stamp (preserved behavior) (high) | server: `test_add_default_appends_and_flags_stale`, `test_add_to_non_investigation_preserves_behavior` |
| AC4 | 1 | Fail-closed guard, full domain — default ADD with (a) no `target_slug`, (b) a retired/nonexistent `target_slug` → REFUSE writing nothing; (c) an existing non-investigation target → APPENDS (no refuse, no stale); new-investigation with (d) slug collision (active or tombstone), (e) entity/title/alias collision incl. case/whitespace → REFUSE; (f) two distinct entities sharing `investigation_topic` (Sakana) → allowed; (g) genuinely-absent subject → created (high) | server: `test_ingest_guard_domain` (cases a–g) |
| AC5 | 1 | Explicit new-investigation emits the R2 skeleton with `stale_since` + `status: awaiting synthesis` + NO auto `investigation_topic`; the new-investigation toggle defaults OFF and is the only creation path; `prospective_unassigned_slug` stays consistent with the creator (high) | server: `test_new_investigation_emits_canonical_skeleton`, `test_prospective_slug_matches_creator`; py: `test_ingest_form_new_investigation_toggle_default_off` |
| AC6 | 1 → 2 | **P1:** `investigation_conformance` returns ∅ for a conformant fixture and the exact deficiency for missing-key / missing-heading / empty-lead / **out-of-order** fixtures; the skeleton is conformant. **P2:** every live-enumerated active investigation page conforms (frontmatter + ordered headings) (med) | py: `test_investigation_conformance_predicate` (P1); `test_all_active_investigations_conform` (P2) |
| AC7 | 1 | Builder imports no network/model client; a page with `stale_since` renders the stale banner until frontmatter clears it (med) | py: `test_builder_has_no_network_client`, `test_stale_since_banner_renders` |
| AC8 | 1 | MemPalace's rendered HTML changes in exactly two ways — the infobox label ("Raw docs"→"Topic Details") and the removed `.toc` — and in no other: all 8 section headings and the contribution box still present (med) | py: `test_mempalace_render_diff_is_label_and_toc_only` |
| AC9 | 1 & 2 | Full chain green; zero regression across the existing build/ingest/arc suites (low) | `npm run verify` exit 0 at each PR's reviewed head |

**Gate satisfied-only-when (allowlist, phase-total):** every AC is assigned to
exactly one phase (column above); no AC is optional. The Phase-1 code PR is
satisfied only when AC1–AC5, AC6(P1), AC7, AC8, AC9 are all green at its
reviewed head AND `npm run verify` exits 0. The Phase-2 PR is satisfied only
when AC6(P2) and AC9 are green at its reviewed head. The FO is satisfied only
when BOTH phases are satisfied. Any unproven assigned criterion ⇒ not
satisfied (IADA-I4: no PR may drop an AC to pass).

## 4. Fail-safe analysis (the §8 house rule, applied)

- **Page creation is the guarded act.** Allowlist: create ⟺
  `new_investigation` AND subject proven absent (§2.4). The default lane
  appends to an explicit existing target (any tier) or refuses; it can never
  create. No fall-through creates. AC4 proves cases a–g including the
  tombstone-slug and case/whitespace-variant collisions.
- **Non-investigation adds are untouched** — the guard is investigation-scoped;
  ordinary source updates to architecture/concept/foundational pages keep
  today's behavior (CFADA-r1 #1), so the FO's investigation scope does not
  regress unrelated tiers.
- **Unauthenticated ADD is safe here** because the danger is a wrong/duplicate
  page — gated above — not appending a doc (Q4). No fuzzy auto-match to
  mis-fire (IADA-I1).
- **stale_since is fail-VISIBLE.** An un-refreshed investigation summary shows
  the banner; a stale synthesis is never silently presented as fresh. Clearing
  is an explicit authoring edit.
- **No-LLM invariant preserved.** Summary regeneration is human/agent
  authoring; the builder has no model/network path (AC7 pins it).
- **Conformance gate cannot brick the live build.** It is a test, not a build
  refusal; Phase 2 turns on the live-enumerated corpus assertion only once the
  corpus satisfies it (§2.5).

## 5. Authorization packet

- **Bounded scope:** the §2.1 file plan; `transpara-ai/wiki` only; docs branch
  `feat/investigation-standard-design` (this FO+packet) off main @ `2c9e672`;
  Phase-1/Phase-2 code on their own `feat/` branches off `origin/main`;
  lifecycle to ready PR. **No code before Human Design Review approves this
  packet (stage 6).**
- **Forbidden:** any change to the authorization-artifact model or
  `secret_scan`; any change to Replace/Remove/register semantics; ADD entering
  the authorization contract (Q4); any change to non-investigation source-add
  behavior; LLM/network in the builder; reanimating the retired owainlewis
  tombstone; force-merging the Sakana pair; running any Phase-2 content edit
  before the Phase-1 machinery merges; autonomous issue/PR creation; merge.
- **Residual risks:** (a) IADA-I1/I7 — a subject that already exists under one
  name, re-ingested as a *declared* new investigation under a *genuinely
  different* name (different slug, different entity, no alias overlap), is not
  machine-detectable; the operator explicitly asserted "new." Mitigation: the
  collision check catches same/similar names; the explicit-intent gate + the
  existing retire path (as used 2026-07-07) recover the rare miss; fail-closed
  direction is deliberate. (b) Clearing `stale_since` is a manual authoring
  edit — nothing forces re-derivation; mitigated by the visible banner + the
  R8 conformance gate. (c) Phase-2 retrofit is judgment-heavy authoring; the
  predicate guards structure/order, not prose quality. (d) The ADD-default UX
  gains a new-investigation toggle; the flow change is documented and covered
  by AC5 + the AC2 render path.

## 6. Two-phase delivery (one FO)

- **Phase 1 — machinery (code PR).** R3 + R4 + R5 + R6 + the conformance
  predicate + AC1–AC5, AC6(P1), AC7–AC9. Server code changes ⇒ deploy = reset
  serving clone to main + `npm run build` + **restart** the service.
- **Phase 2 — retrofit (data-only PR[s]).** The 19 pages → R2 schema (R8),
  MemPalace heading generalized, `stale_since` where summaries need
  re-derivation, AC6(P2) flipped on. Data-only ⇒ `npm run build`, **no
  restart**. May split by cluster; each is independently gated.

Each PR runs stages 7→11 (IAR → CFAR at exact head → ready → fresh ready-state
CFAR). Merge is Michael's (stage 12).

## Appendix — IADA (self-directed, v0.1.0 → v0.2.0)

Assessor: Claude (Opus 4.8). Assessed: 2026-07-09. Branch:
`feat/investigation-standard-design`. Method: adversarial, against the whole
input domain.

| # | Finding (class) | Disposition (v0.2.0) |
|---|---|---|
| I1 | Default-ADD resolved the topic by fuzzy normalized match — fail-open: could not catch the real bug (two titles, one subject) and could mis-route a doc | FIXED — default-ADD REQUIRES an explicit resolvable `target_slug`; fuzzy auto-match removed (§2.4). |
| I2 | AC6(P1) claimed "MemPalace conforms," but its heading is dated `## What Changed With TAI-RES-2026-004` — the exemplar is not literally conformant | FIXED — Phase 1 asserts predicate + skeleton only; MemPalace generalized in Phase 2 (§2.5). |
| I3 | AC8 golden "byte-identical except the label" was wrong — R4 also removes MemPalace's TOC | FIXED — AC8: exactly two changes (label + removed `.toc`), all headings + box preserved. |
| I4 | Gate predicate let a PR cherry-pick a subset of ACs | FIXED — each AC bound to exactly one phase; FO satisfied only when both phases' full sets are green (§3). |
| I5 | Conformance predicate under-defined (Summary/Contribution are not `##` headings) | FIXED — §2.5 defines frontmatter keys ∪ required headings ∪ non-empty-lead. |
| I6 | AC6(P2) risked a hardcoded "19" — fail-open by omission | FIXED — the test enumerates live (glob + tier + not retired). |
| I7 | Residual (a) worded as a normalization limit; the real residual is declared-new-under-a-new-name | FIXED — residual (a) restated (§5). |
| I8 | AC4 missed the tombstone-slug and case/whitespace collisions | FIXED — AC4 cases enumerate them (§3). |

IADA verdict at v0.2.0: **PASS — 0 design blockers.** Ready for CFADA. This
IADA does not replace external CFADA.

## Appendix — CFADA round 1 (Codex) → FAIL, repaired at v0.3.0

> Reviewer: Codex (`codex-cli 0.142.5`, gpt-5.5, xhigh) — materially
> independent of the Claude (Opus 4.8) author family. `codex exec review
> --base origin/main`, bare, from the worktree, at v0.2.0 packet blob
> `c06d8126ff44feb03bcca8df9099fc9cdca665dc` (commit `c4f8e87`). Three P2
> findings, all accepted-repaired.

| # | Finding | Disposition (v0.3.0) |
|---|---|---|
| C1 | The ADD-default guard required every target to be an active investigation page, and AC4 refused non-investigation targets — but the Add form offers every non-retired article (any tier); this would REGRESS ordinary source updates to architecture/concept/foundational pages | FIXED — §2.4 scopes the guard to the investigation lane: a non-investigation existing target appends with today's behavior (no stale, no refuse); AC4 case (c) proves it; §2/§5 name it a non-goal/forbidden change; survey §1 cites `article_records` (`:143`). |
| C2 | FO said "MemPalace conforms" while the packet's IADA said it does not until Phase 2 — a normative contradiction that could make implementers skip the MemPalace retrofit | FIXED — FO bumped to v0.2.1 (blob `472bb1623cea3de7b0bf7e7389841affe3d3e589`): §1 R2/R8 and §3 corrected to "content exemplar, not literally conformant; generalized in Phase 2"; packet rebound to the new FO blob. |
| C3 | `investigation_conformance` checked heading presence but not ORDER — a page with `Sources & Provenance` before `The Boundary` would pass AC6 despite the R2 canonical order | FIXED — §2.5 predicate now returns an out-of-order flag (required headings must appear as a canonical-order subsequence); AC6(P1) adds an out-of-order fixture; AC6(P2) asserts frontmatter + ordered headings. |

Re-audit (CFADA round 2) pending at v0.3.0. No code before Human Design Review
(stage 6) approves.
