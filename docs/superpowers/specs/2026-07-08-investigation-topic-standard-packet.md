---
doc_id: TAI-WIKI-INVESTIGATION-STANDARD
title: One canonical page per investigation — Investigation Topic Standard (TLC Design Packet)
doc_type: design
version: 0.4.0
status: draft (IADA-passed; CFADA r1+r2 repaired; re-audit pending)
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
> IADA (v0.2.0) and CFADA rounds 1 (v0.3.0) and 2 (v0.4.0).

## 1. Survey — measured, not assumed (file:line evidence)

- **Infobox** (`build_site.py:1504` `build_infobox`): the "Raw docs" label is a
  single literal at `:1530`; its list comes from `raw_doc_refs(fm)`
  (`:953`–`968`). R3's surface.
- **TOC** (`build_site.py:820` `build_toc`, ≥3 headings at `:823`): injected
  for every non-home page at `:2181`, placed at `:2211`. The contribution box
  is tier-gated at `:2210`; the TOC is not — R4's seam. MemPalace has 8 `##`
  headings → a TOC today; R4 removes it.
- **Contribution box** (`build_site.py:1538`): from `civilization_contribution`;
  investigation-tier only (R2 "Civilization Contribution", a callout).
- **Lead paragraph** = the **bold** first paragraph, split at `:2208`–`:2209`
  (MemPalace's opens `**MemPalace is …**`). This is R2 "Summary".
- **stale banner** (`build_site.py:2200`–`2204`): the `stale_since` banner text
  is Replace-specific — "raw sources were replaced … prose re-derivation is
  pending authorization" — false for an unauthenticated ADD (CFADA-r2 #5).
- **Ingest target list** (`ingest_server.py:143` `article_records`): the Add
  form/API offers EVERY non-retired article of ANY tier as a target. The
  ADD-default change must NOT refuse non-investigation targets (CFADA-r1 #1).
- **Ingest routing** (`ingest_server.py:802` `handle_ingest`): no
  `target_slug` → `create_article_from_source()` (`:865`–`867`) derives BOTH
  slug and `entity` from the first raw doc's **title** (`:602`–`656`,
  `slugify`), hardcodes `tier: investigation` (`:621`), auto-sets
  `investigation_topic`; a PROVIDED `target_slug` appends via
  `append_sources_to_article` (`:585`) + `append_raw_documents_to_article`
  (`:594`), dedup-safe through `append_frontmatter_list_items` (`:542`).
  `prospective_unassigned_slug` (`:116`) mirrors the creator's title-derivation
  — the title-keying that R1 must end (CFADA-r2 #4).
- **stale_since** primitive: set by `replace_source` at `:961` via `_set_scalar`
  (`:735`); cleared via `_drop_scalar` (`:743`). Append helpers set nothing.
- **No-LLM/no-network builder**: `build_site.py:6`; no HTTP/model client.
- **Corpus**: 20 pages — 19 active + the retired owainlewis tombstone. None is
  literally conformant; MemPalace is the content model but its heading is the
  dated `## What Changed With TAI-RES-2026-004` (generalized in Phase 2).

## 2. The contract

### 2.1 File plan

| Phase | Action | File | Change |
|---|---|---|---|
| 1 | EDIT | `compile/build_site.py` | **R3:** relabel `"Raw docs"` → `"Topic Details"` (`:1530`). **R4:** `toc = "" if is_home or meta.get("tier")=="investigation" else build_toc(...)` (`:2181`). **R7 banner:** make the `stale_since` banner text reason-neutral (`:2200`), correct for both Add and Replace (CFADA-r2 #5). **R2 predicate:** `investigation_conformance(slug)` — missing frontmatter keys + missing/out-of-order required(+present-optional) headings + non-bold-lead. |
| 1 | EDIT | `compile/ingest_server.py` | **R5/R6/R1 (§2.4):** `handle_ingest` intent model + fail-closed guard. `create_article_from_source` gains an explicit `name` param so the **operator-supplied name** (not the doc title) drives slug/`entity` and the collision check (CFADA-r2 #4); `prospective_unassigned_slug` (`:116`) derives from the same name. Default lane requires a resolvable `target_slug` (any tier); appends; stamps `stale_since` only for investigation targets; non-investigation adds unchanged. |
| 1 | EDIT | `compile/ingest_ops.py` | `set_article_stale(root, slug, now)` wrapping `_set_scalar(..., "stale_since", ...)` — reused by ADD and Replace; no new op, no authorization contract (Q4). |
| 1 | EDIT | `ingest_page()` region in `compile/build_site.py` | "This is a new investigation" toggle (default OFF) reveals a **required name** field and is the ONLY creation path; checking it ignores `target_slug`. Default Add targets the selected existing page. Both themes. |
| 1 | ADD/EDIT | `compile/test_build_site*.py`, `compile/test_ingest_server.py`, `tests/*.spec.js` | AC1–AC5, AC6(P1), AC7–AC9. |
| 2 | EDIT | `wiki/<each active investigation>.md` (19, incl. MemPalace) | Retrofit to the R2 schema (generalize MemPalace's "What Changed" heading; bold lead); `raw_documents` complete; `stale_since` where the summary needs re-derivation; Sakana pair conformed, `investigation_topic: Sakana AI` on both. Data-only. |
| 2 | EDIT | `compile/test_build_site*.py` | Flip AC6 to assert every live-enumerated active investigation page conforms. |
| — | UNTOUCHED | authorization artifact semantics, `secret_scan`, Replace/Remove/register op logic, non-investigation source-add behavior, arc view, board, engine, refresh timer, the retired tombstone | Forbidden §5. |

### 2.2 R3 — Topic Details (infobox rename)

`row("Raw docs", …)` → `row("Topic Details", …)` at `:1530`; data source
unchanged. AC1 asserts the "Topic Details" row and no surviving "Raw docs".

### 2.3 R4 — No in-topic Table of Contents

Allowlist branch at `:2181`: investigation → `toc = ""`; else → `build_toc`.
Beside the contribution tier-gate at `:2210`. AC2 proves both directions.

### 2.4 R5/R6/R1 — Ingest ADD-default + canonical new-page + fail-closed guard

**FO deferred question resolved:** ADD is a **routing change in
`ingest_server.py`**, not a new `ingest_ops` op (Q4 keeps it unauthenticated).
Only the `stale_since` stamp reaches `ingest_ops`, via the shared
`set_article_stale` helper.

**Normalization (defined, so the guard is verifiable):** `norm(s)` =
Unicode-casefold, collapse internal whitespace to one space, strip surrounding
whitespace/punctuation. Two subjects "collide" when `norm(a) == norm(b)` for a
∈ {new name} and b ∈ {an active investigation page's `entity` ∪ its `aliases`},
or when `slugify(name)` equals an existing page's slug.

**Intent model** — `handle_ingest` reads a `new_investigation` flag (default
false):

- **Default (add to an existing page).** REQUIRES an explicit `target_slug`
  naming an existing **active** page (any tier). On match: append
  `raw_documents` + `sources` (dedup); if the target is `tier: investigation`,
  also `set_article_stale`; rebuild — **create nothing**. Non-investigation
  targets keep today's behavior (no stale, no guard — CFADA-r1 #1). Absent /
  retired / non-existent `target_slug` → **REFUSE**. No fuzzy title match
  (IADA-I1).
- **Explicit new-investigation.** Requires a non-empty operator **name**
  (empty name → refuse). The name — **not** the document title — drives the
  page: `slugify(name)` is the slug, `name` the `entity`;
  `create_article_from_source(name=…)` and `prospective_unassigned_slug` use it
  (CFADA-r2 #4), so a doc whose title differs from the subject can no longer be
  title-keyed around the guard. `target_slug` is ignored in this lane. REFUSE
  unless the subject is proven absent (the collision rule above, against active
  investigation entities/aliases and all existing slugs incl. tombstones).
  Otherwise create with `stale_since`, `status: browser-ingested source;
  awaiting synthesis`, and no auto `investigation_topic`. Sakana's two distinct
  entities never collide.

**Fail-safe statement.** The ONLY branch that creates a page is
`new_investigation == true` AND a non-empty name AND the subject proven absent.
The default lane appends (any tier) or refuses; ambiguous, empty-name, and
colliding inputs refuse. No `else`/fall-through creates. AC4 proves the domain.

**stale_since lifecycle (R7).** An investigation ADD stamps `stale_since`; the
banner (`build_site.py:2200`) is genericized — the current Replace-specific
wording ("raw sources were replaced … pending authorization") is false for an
unauthenticated ADD (CFADA-r2 #5), so it becomes reason-neutral ("raw sources
changed — summary re-derivation pending"), correct for both Add and Replace,
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
  AND carry bold/`<strong>` emphasis (the Summary). A plain unbolded lead is
  non-conformant.
- **Order (CFADA-r1 #3, CFADA-r2 #6):** from the page's heading sequence keep
  the STANDARD headings — the required set PLUS `Integration Packet` **when
  present** — and require them in the canonical order (so `Integration Packet`,
  if present, must sit immediately before `Sources & Provenance`; a page with
  `Sources & Provenance` before a present `Integration Packet` is
  non-conformant). Free extras (`## Placement`, `## Decision Record`) may be
  interspersed and are ignored by the order check.

Conformant ⟺ the returned set is empty. Heading match is exact on the canonical
strings (MemPalace's dated heading is non-conformant until Phase 2 — IADA-I2).

**Corpus timing (no red merge).** Phase 1 asserts the predicate is correct
(a conformant fixture → ∅; missing-key, missing-heading, non-bold-lead,
out-of-order, and Integration-Packet-misordered fixtures → the right
deficiency) and that the new-investigation skeleton is conformant. Phase 2
retrofits all pages and flips AC6 to assert every **live-enumerated** active
investigation page (`glob wiki/*.md`, `tier==investigation`, not `retired_on`)
conforms. The hard corpus gate turns on only when the corpus can satisfy it
(IADA-I6: live enumeration).

## 3. Acceptance criteria & named tests

| # | Phase | Criterion (risk) | Verification — named test |
|---|---|---|---|
| AC1 | 1 | Infobox row reads "Topic Details" and lists every `raw_documents` entry; no "Raw docs" label survives in `dist/` (low) | py: `test_infobox_topic_details_label` |
| AC2 | 1 | Investigation-tier page renders no `.toc`; a ≥3-heading non-investigation page still renders one (med) | py: `test_investigation_pages_have_no_toc`; playwright: `investigation page has no contents box` |
| AC3 | 1 | Default ADD with a resolvable investigation `target_slug` appends `raw_documents`+`sources`, sets `stale_since`, leaves `wiki/*.md` count unchanged, rebuilds; a non-investigation target appends WITHOUT a stale stamp (preserved) (high) | server: `test_add_default_appends_and_flags_stale`, `test_add_to_non_investigation_preserves_behavior` |
| AC4 | 1 | Fail-closed guard, full domain — default ADD with (a) no `target_slug`, (b) retired/nonexistent `target_slug` → REFUSE; (c) existing non-investigation target → APPENDS (no refuse/stale); new-investigation with (d) empty name → REFUSE, (e) slug collision (active or tombstone), (f) name/entity/alias collision incl. case/whitespace → REFUSE; (g) doc title ≠ operator name → the NAME drives slug/entity + guard (no title-keyed bypass); (h) two distinct entities sharing `investigation_topic` (Sakana) → allowed; (i) genuinely-absent subject → created (high) | server: `test_ingest_guard_domain` (cases a–i) |
| AC5 | 1 | Explicit new-investigation builds the page FROM the operator name (not the doc title), emits the R2 skeleton with bold-lead placeholder + `stale_since` + `status: awaiting synthesis` + NO auto `investigation_topic`; toggle defaults OFF and is the only creation path; `prospective_unassigned_slug` matches the creator (high) | server: `test_new_investigation_uses_operator_name`, `test_new_investigation_emits_canonical_skeleton`, `test_prospective_slug_matches_creator` |
| AC6 | 1 → 2 | **P1:** `investigation_conformance` returns ∅ for a conformant fixture and the exact deficiency for missing-key / missing-heading / non-bold-lead / out-of-order / Integration-Packet-misordered fixtures; the skeleton conforms. **P2:** every live-enumerated active investigation page conforms (med) | py: `test_investigation_conformance_predicate` (P1); `test_all_active_investigations_conform` (P2) |
| AC7 | 1 | Builder imports no network/model client; a page with `stale_since` renders the banner until frontmatter clears it, and the banner text is reason-neutral (no Replace-specific "sources were replaced"/"authorization" wording) so an ADD-stale page reads correctly (med) | py: `test_builder_has_no_network_client`, `test_stale_banner_is_reason_neutral` |
| AC8 | 1 | MemPalace's rendered HTML changes in exactly two ways — the infobox label and the removed `.toc` — and no other: all 8 section headings and the contribution box still present (med) | py: `test_mempalace_render_diff_is_label_and_toc_only` |
| AC9 | 1 & 2 | Full chain green; zero regression across the existing build/ingest/arc suites (low) | `npm run verify` exit 0 at each PR's reviewed head |

**Gate satisfied-only-when (allowlist, phase-total):** every AC is assigned to
exactly one phase; no AC is optional. The Phase-1 PR is satisfied only when
AC1–AC5, AC6(P1), AC7, AC8, AC9 are green at its reviewed head AND
`npm run verify` exits 0. The Phase-2 PR is satisfied only when AC6(P2) and AC9
are green at its reviewed head. The FO is satisfied only when BOTH phases are.
Any unproven assigned criterion ⇒ not satisfied (IADA-I4).

## 4. Fail-safe analysis (the §8 house rule, applied)

- **Page creation is the guarded act.** Allowlist: create ⟺ `new_investigation`
  AND non-empty name AND subject proven absent (§2.4), keyed on the operator
  name so the doc title cannot route around it (CFADA-r2 #4). The default lane
  appends to an explicit existing target or refuses; it never creates. No
  fall-through creates. AC4 proves cases a–i.
- **Non-investigation adds untouched** — the guard is investigation-scoped
  (CFADA-r1 #1); unrelated tiers keep today's append.
- **Unauthenticated ADD is safe** because the danger (a wrong/duplicate page)
  is gated above, not the act of appending (Q4). No fuzzy match to mis-fire.
- **stale is fail-VISIBLE and honestly worded** — the banner shows until an
  authoring edit clears it, with reason-neutral text (CFADA-r2 #5).
- **No-LLM invariant preserved** (AC7).
- **Conformance gate cannot brick the live build** — a test, not a build
  refusal; Phase 2 turns on the corpus assertion only once satisfiable.

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
  slug/entity/alias overlap), is not machine-detectable — the operator asserted
  "new"; the collision check catches same/similar names, and the retire path
  recovers the rare miss; fail-closed direction deliberate. (b) Clearing
  `stale_since` is a manual authoring edit; mitigated by the visible banner +
  R8. (c) Phase-2 retrofit is judgment-heavy; the predicate guards
  structure/order/bold-lead, not prose quality. (d) The bold-lead check keys on
  rendered `<strong>`/`**` in the lead; an author using a non-`strong` visual
  emphasis would be flagged — acceptable (the standard specifies bold).

## 6. Two-phase delivery (one FO)

- **Phase 1 — machinery (code PR).** R3 + R4 + R5 + R6 + R7 banner + the
  conformance predicate + AC1–AC5, AC6(P1), AC7–AC9. Server code ⇒ deploy =
  reset serving clone to main + `npm run build` + **restart**.
- **Phase 2 — retrofit (data-only PR[s]).** The 19 pages → R2 schema (R8),
  MemPalace heading generalized, bold leads, `stale_since` where needed,
  AC6(P2) on. Data-only ⇒ `npm run build`, **no restart**. May split by
  cluster; each independently gated.

Each PR runs stages 7→11 (IAR → CFAR at exact head → ready → fresh ready-state
CFAR). Merge is Michael's (stage 12).

## Appendix — IADA (self-directed, v0.1.0 → v0.2.0)

Assessor: Claude (Opus 4.8). Assessed 2026-07-09. Adversarial, whole-domain.

| # | Finding | Disposition |
|---|---|---|
| I1 | Fuzzy default-add match — fail-open (mis-route; misses the real bug) | FIXED — explicit resolvable `target_slug` required (§2.4). |
| I2 | "MemPalace conforms" false (dated heading) | FIXED — P1 predicate/skeleton only; MemPalace generalized in P2. |
| I3 | AC8 golden ignored the removed TOC | FIXED — AC8 = label + removed `.toc`, nothing else. |
| I4 | Gate predicate allowed AC cherry-pick | FIXED — each AC phase-bound; both phases required. |
| I5 | Conformance predicate under-defined | FIXED — §2.5 concrete. |
| I6 | AC6(P2) risked hardcoding "19" | FIXED — live enumeration. |
| I7 | Residual (a) mis-worded | FIXED — restated (§5). |
| I8 | AC4 missed tombstone/case-whitespace collisions | FIXED — AC4 cases. |

IADA verdict v0.2.0: PASS — 0 blockers. Does not replace external CFADA.

## Appendix — CFADA round 1 (Codex) → FAIL, repaired at v0.3.0

> Reviewer: Codex (`codex-cli 0.142.5`, gpt-5.5, xhigh), materially independent
> of the Claude (Opus 4.8) author. `codex exec review --base origin/main`, bare,
> at v0.2.0 packet blob `c06d8126ff44feb03bcca8df9099fc9cdca665dc`
> (commit `c4f8e87`). 3 P2 findings, all accepted-repaired.

| # | Finding | Disposition (v0.3.0) |
|---|---|---|
| C1 | Guard required an investigation target for ALL adds — would regress source updates to non-investigation pages (the form offers every tier) | FIXED — guard scoped to the investigation lane; non-investigation targets append unchanged (§2.4, AC4c, non-goal). |
| C2 | FO said "MemPalace conforms"; packet said it does not — normative contradiction | FIXED — FO → v0.2.1 (blob `472bb1623c…`); packet rebound. |
| C3 | Conformance checked heading presence, not order | FIXED — order (canonical subsequence) added (§2.5, AC6). |

## Appendix — CFADA round 2 (Codex) → FAIL, repaired at v0.4.0

> Same reviewer/command, at v0.3.0 packet blob
> `b65d39413fce232b95adba2ebe56262f5be2d39a` (commit `153e839`). 4 P2 findings,
> all accepted-repaired.

| # | Finding | Disposition (v0.4.0) |
|---|---|---|
| C4 | New-investigation UI added a name field, but `create_article_from_source` still keys slug/entity off the doc TITLE — a declared-new upload whose title differs from the subject bypasses the R1 duplicate guard | FIXED — the operator name drives slug/`entity` and the collision check; `create_article_from_source(name=…)` + `prospective_unassigned_slug` use it; empty name refuses; `target_slug` ignored in this lane (§2.4, §2.1, AC4d/g, AC5). |
| C5 | The reused `stale_since` banner text is Replace-specific ("sources were replaced … pending authorization") — false for an unauthenticated ADD | FIXED — banner genericized to reason-neutral text, correct for Add + Replace, with a test (§2.4, §2.1, AC7). |
| C6 | Order check treated the optional `Integration Packet` as a free extra, so `Sources & Provenance` before a present `Integration Packet` would pass | FIXED — present optional STANDARD headings are included in the order check; misordered fixture added (§2.5, AC6). |
| C7 | Predicate required only a non-empty lead, not the **bold** Summary the standard specifies | FIXED — the lead must carry bold/`<strong>`; non-bold-lead fixture added (§2.5, AC6). |

Re-audit (CFADA round 3) pending at v0.4.0. No code before Human Design Review
(stage 6) approves.
