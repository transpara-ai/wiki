---
doc_id: FO-WIKI-INVESTIGATION-STANDARD
title: One canonical page per investigation — the Investigation Topic Standard (Factory Order)
doc_type: factory-order
version: 0.2.0
status: confirmed (channel-A intake confirm, Michael, 2026-07-09 — answers archived in §5; R1–R8 confirmed as read; one FO / two phases; ADD unauthenticated + fail-closed duplicate guard)
canonical: false
created: 2026-07-08
updated: 2026-07-09
owner: Michael Saucier
steward: Claude (Opus 4.8)
authority: planning
tlc_stage: factory-order
source_of_intent:
  - Michael, in-session 2026-07-08 (archived verbatim in §4) — "establish a new standard for all Topics located under the INVESTIGATIONS heading … always a single entry per investigation … model … MemPalace … default is to ADD … regenerate the top-level summary … ALL raw ingested files … under a Topic Details section"
  - Plan-mode approved pre-design /home/transpara/.claude/plans/agile-coalescing-flask.md — content sha256 9d1638e1687cdc3eacd736f57cfc7a45ec52b70185b5865f3f9574e1a645a150 (channel-A ingested doc; approved 2026-07-08; the locked decisions archived in §5)
  - wiki/mempalace.md (blob a9a9bc6bc83b01a9ba27776bb179e6d8b16de96c, canonical on main @ 2c9e672) — the conformant exemplar the standard models
  - docs/superpowers/specs/2026-07-03-per-ingestion-ops-packet.md (blob 48e330a27d8449c5c8ac0e412dcf6f7d98c23dfc) — governs ingest_ops Add/Replace/Remove/register; R5/R6 extend its ADD lane
  - docs/superpowers/specs/2026-07-06-front-end-ux-packet.md (blob 90df72f4cc18166dab8a41302df9196bb6724e67) and its FO (blob 8beb807911f4b2c37c62b8a57fff2a7187b58657) — govern ingest.html UX + honest-state styling; R3/R4 touch the same infobox/rendering surface
  - Implementation anchors on main @ 2c9e672: compile/build_site.py (blob 0686663dbdd5a08bbcf2491c99899bb9c394b59a), compile/ingest_server.py (blob d4ebbe3990423aea8bca299e9fc6dc93b8b30cc3), compile/ingest_ops.py (blob 85681ba97043718f786fde37e929f8dcb27e4d38) — the "Today:" measurements below
intake_channel: A (owner-directed session 2026-07-08; confirmed 2026-07-09)
---

# Investigation Topic Standard — Factory Order

> Stage-2 TLC document. It states intent; it grants and closes nothing. The
> requirements below are the verifiable reading of "establish a new standard
> for all Topics under the INVESTIGATIONS heading … a single entry per
> investigation … model MemPalace … default is to ADD … regenerate the
> top-level summary … all raw ingested files under a Topic Details section",
> derived from the investigation-structure survey (2026-07-08, wiki main
> @ `2c9e672`). Root cause of today's drift: the ingest server's default is
> "spawn a new title-keyed page," so two concurrent ingests of one subject
> became two pages (the owainlewis duplicate, retired 2026-07-07), and no
> section schema is enforced.

## 1. Requirements (each individually verifiable)

- **R1 — One canonical page per investigation subject.** Each investigation
  subject is represented by exactly one active `tier: investigation` page. No
  ingest path may create a second page for a subject that already has one.
  *Verifiable:* a duplicate-subject guard refuses a second page; no two active
  investigation pages describe the same subject.
  *Today:* `handle_ingest()` (`ingest_server.py:865`) calls
  `create_article_from_source()` whenever `target_slug` is absent, minting a
  slug from the document **title** — two title variants → two pages (the
  owainlewis pair; redundant page retired 2026-07-07).

- **R2 — Canonical Topic Entry schema (frontmatter + sections).** An
  investigation page carries the required frontmatter (`entity`, `aliases`,
  `tier`, `status`, `last_compiled`, `civilization_contribution`,
  `raw_documents`, `current_research_version`, `sources`; `investigation_topic`
  reserved — set only for a genuine multi-investigation cluster) and renders,
  in this order: **Summary** (the bold lead paragraph, no heading) →
  **Civilization Contribution** (the callout box from
  `civilization_contribution`) → `## What Changed with the Research` →
  `## The Boundary` → `## Capability Read` → `## Benchmark Reality` →
  `## Integration Packet` (optional) → `## Sources & Provenance`. Modeled on
  MemPalace (blob a9a9bc6…). *Verifiable:* a conformance check asserts the
  required frontmatter keys and required section headings are present.
  *Today:* only MemPalace conforms; the new-page path emits a
  `## Placement` / `## Source Access` stub (`create_article_from_source()`,
  `ingest_server.py:602`).

- **R3 — Topic Details lists every raw ingested file.** The infobox field
  labeled "Raw docs" is relabeled **"Topic Details"** and lists every
  `raw_documents` entry (all versions, superseded included, newest linked
  primary). *Verifiable:* a rendered investigation page shows a "Topic Details"
  infobox row listing each `raw_documents` entry; no "Raw docs" label remains.
  *Today:* `build_infobox()` (`build_site.py:1530`) emits the label "Raw docs".

- **R4 — No in-topic Table of Contents.** `tier: investigation` pages render
  no auto TOC; other tiers keep theirs. *Verifiable:* a rendered investigation
  page contains no `.toc` element; a non-investigation page with ≥3 headings
  still does. *Today:* `build_toc()` (`build_site.py:820`) + `page()`
  (`build_site.py:2181`, injected at `:2211`) add a "Contents" box to any
  ≥3-heading page — investigations included; the contribution box is already
  tier-gated at `:2210`, the TOC is not.

- **R5 — Ingest default = ADD to the existing topic + flag the summary
  stale.** A browser ingest that does not explicitly declare a *new*
  investigation appends the raw doc to the existing topic page (`raw_documents`
  + `sources`, deduped) and sets `stale_since`, so the existing
  "synthesis stale — re-derivation pending" banner renders. It never spawns a
  second page for an existing subject. *Verifiable:* ingest without
  new-investigation intent appends, sets `stale_since`, and creates no page;
  an ambiguous/duplicate subject is refused (fail-closed). *Today:* the append
  helpers exist (`append_raw_documents_to_article()` `:594`,
  `append_sources_to_article()` `:585`) but are not the default and set no
  `stale_since`; only `replace_source()` sets it (`ingest_ops.py:961`).

- **R6 — New-investigation creation is explicit and emits the canonical
  skeleton.** Creating a genuinely new investigation is an explicit action
  that emits the R2 section skeleton with `stale_since` set and
  `status: browser-ingested source; awaiting synthesis`, and does **not**
  auto-populate `investigation_topic`. *Verifiable:* the new-investigation
  path yields a page matching R2; `investigation_topic` is absent unless a
  cluster is declared. *Today:* `create_article_from_source()`
  (`ingest_server.py:602`) emits the non-canonical stub and auto-sets
  `investigation_topic` to the title.

- **R7 — Summary regeneration is a visible, gated, no-LLM authoring step.**
  The "top-level summary" (the bold lead paragraph) is re-derived by a governed
  authoring pass (agent/human) that clears `stale_since`; the site builder
  performs no LLM or network work. *Verifiable:* the builder has no
  network/LLM call path (existing constraint, `build_site.py:6`); a page with
  `stale_since` shows the banner until an authoring pass clears it.
  *Today:* no regeneration exists; the `stale_since` banner
  (`build_site.py:2200`) is only ever set by Replace.

- **R8 — All active investigation pages conform.** Every active investigation
  page (currently 19, MemPalace included) satisfies R2 + R3 and lists all its
  raw docs under Topic Details. Sakana AI stays **two** distinct conformant
  pages under the single sanctioned `investigation_topic: Sakana AI` grouping;
  the retired owainlewis tombstone is left untouched. *Verifiable:* the
  conformance check (R2) passes for every active investigation page.
  *Today:* structures vary; only MemPalace fully conforms.

## 2. Non-goals and constraints

Non-goals: no LLM or network in the builder, ever; no public-internet exposure
of any wiki/Civilization surface; no change to the deny-by-default
ingest-authorization artifact model or the secret scanner; no removal or
reanimation of the retired owainlewis tombstone; no forced merge of the Sakana
pair; no change to Replace/Remove/register semantics beyond adding the ADD
lane; no arc/front-page/board changes; no batch/LLM re-synthesis of prose
(summaries are re-derived per topic by the authoring pass).

Confirmed 2026-07-09 (§5): ADD runs **unauthenticated** (like today's Add) and
never requires the authorization artifact; a **fail-closed** duplicate/ambiguity
guard is the sole gate on page creation/routing and never silently creates or
mis-routes a page. The standard's normative home is this FO + its design packet
(a browsable wiki meta-page is an optional later nicety, not part of this
order). **Deferred to the design packet (stage 3):** whether ADD is implemented
as a new governed op in `ingest_ops.py` or a routing change in
`ingest_server.py`.

Constraints: air-gap (no external assets); both themes via the existing
custom-property palette; fail-closed (duplicate/ambiguous subject refused;
unknown state renders degraded, never healthy); tests per the house pattern
(unit + dom-smoke + py builder guards + Playwright); **worktrees only** (the
serving clone `repos/wiki` is a live ingest-service state dir); **hex-free** raw
filenames (content-addressed sha12 names trip the non-clearable pathname rule);
CI secret-scan reads the allowlist from the **base** ref (F9 two-step — any
pins land in main first); `transpara-ai/wiki` only; lifecycle issue→ready-PR;
merge remains Michael's (stage 12).

## 3. Verification of the gap (measured 2026-07-08, main @ 2c9e672)

- `grep -n "Raw docs" compile/build_site.py` → `1530:` (R3).
- `build_toc()` output is injected for every non-home page at
  `build_site.py:2181`; the contribution box is tier-gated at `:2210` but the
  TOC is not (R4).
- `handle_ingest()` with no `target_slug` → `create_article_from_source()`
  (`ingest_server.py:865`–`867`) — the R1/R6 duplicate-spawning default.
- Append helpers set no `stale_since`; only `replace_source()` does
  (`ingest_ops.py:961`) — the R5 gap.
- Investigation tier: 20 pages (19 active + the retired owainlewis tombstone).
  Only MemPalace (blob a9a9bc6…) is fully schema-conformant — the R2/R8 gap.
  Sakana AI is the sole genuine multi-page subject (`sakana-ai-evaluation.md`
  + `sakana-ai-adjacent-landscape.md`, both active, shared `investigation_topic`).

## 4. Source-of-intent archive (channel A)

Michael, in-session 2026-07-08, verbatim:

> Use planning mode to establish a new standard for all Topics located under
> the INVESTIGATIONS heading. I want to refactor this list so that there is
> always a single entry per investigation. Model the refactoring to resemble
> the MemPalace result. When new documents are ingested the default is to ADD
> information about a topic, and to regenerate the top-level summary. ALL raw
> ingested files should be available under a Topic Details section like the one
> for MemPalace (screenshot).
>
> Format of a Topic Entry: --note that Table of Contents is NOT necessary
> within a single Topic (screenshot)
> Summary of the investigation / Civilization Contribution / What Changed with
> the Research / The Boundary / Capability Read / Benchmark Reality /
> Integration Packet (if needed) / Sources & Provenance

Two screenshots accompanied the request: (1) the MemPalace **infobox**
(Tier / Status / Last compiled / Also known as / Sources / Raw docs → the
Topic Details model); (2) the MemPalace **article layout** with the auto
"Contents" TOC struck through (the R4 basis).

Approved pre-design (plan mode, 2026-07-08):
`/home/transpara/.claude/plans/agile-coalescing-flask.md`, content sha256
`9d1638e1687cdc3eacd736f57cfc7a45ec52b70185b5865f3f9574e1a645a150` — the
verifiable requirements above are its Part 1/Part 2 re-expressed as a truth
object.

## 5. Intake confirmation — RECEIVED (Michael, 2026-07-09)

The stage-2 channel-A confirm was asked and answered in-session. Decisions
pre-locked in the plan-mode session (the reading basis):

- **Scope:** retrofit all 19 active investigation pages now (→ R8), delivered
  as a governed PR series.
- **Summary regeneration:** author pass gated by the existing `stale_since`
  banner; no LLM in the builder (→ R5/R7).
- **Topic Details:** the renamed infobox field (→ R3). Sakana AI stays two
  investigations (→ R8); Summary + Civilization Contribution map to MemPalace's
  existing bold-lead + callout rendering, not literal `##` headings (→ R2).

Confirm answers (2026-07-09):

- **Q1 — Is R1–R8 the order?** *Confirmed as read.* → FO confirmed.
- **Q2 — Decomposition?** *One Factory Order, two phases* — a machinery code
  PR (R2 template + R3 rename + R4 TOC suppression + R5/R6 ingest ADD-default +
  tests), then data-only retrofit PR(s) for the 19 pages (R8). One design
  packet answers this FO.
- **Q3 — Standard home?** Defaulted (uncontested): this FO + design packet are
  the normative standard; a wiki meta-page is an optional later nicety.
- **Q4 — ADD-lane authorization?** *Unauthenticated + fail-closed guard* — ADD
  never requires the authorization artifact; the fail-closed duplicate/ambiguity
  guard is the sole gate on page creation/routing (recorded in §2).

The arc proceeds: design packet → IADA → CFADA → **Human Design Review
(stage 6, Michael — required before any code)** → build → draft PR → IAR →
CFAR → ready. Merge remains stage 12, Michael only.
