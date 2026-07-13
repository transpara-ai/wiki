---
doc_id: FO-WIKI-RAW-AREA
version: "0.7.2"
status: "amended post-PR-review-r4 (wiki#80) — the CONFIRMED READING remains the v0.1.0 object (blob 7c10b2ffe4f9e6903328669baf68ab2ff004df86, confirmed verbatim 2026-07-13); Michael's explicit byte-confirmation of THIS v0.7.2 file is the NAMED PRECONDITION for Human Design Review entry (supersedes every prior pending status)"
factory: transpara-ai/wiki
author_family: claude
---

# Raw Area — Factory Order

> A visible, rendered "raw area" on the wiki: one global page listing every
> raw ingested research file, organized by ingestion date, each entry showing
> a unique identifier distinct from the document's original name.
> **v0.6.0** repairs CFADA-r4's findings: R1 no longer narrows browser
> ingests to Markdown (the upload machinery preserves ANY suffix —
> `<stem>-<sha12><suffix>`, `ingest_server.py:634`–`:666` — so a manifested
> `.txt` upload is research too); R2's tie rule is a total order; R3
> distinguishes shared RECORDED identity from identical CURRENT content;
> R6's reader contract is stated as design-local requirements derived from
> the production constructors. Intent unchanged from the confirmed v0.1.0
> reading; deltas in §5. **v0.6.1** added the metadata-visibility
> widening record (§5 item 8) and restored the three parse-level rejection
> lanes (CFADA-r5). **v0.6.2** was a reference-consistency repair
> (CFADA-r6). **v0.7.0** repaired the two wiki#80 PR-review r1 findings: the
> `raw` route reserved in the creation guard (denial-only §2 carve-out) and
> the within-group entry order made total via the source-path secondary key.

## 0. Source of intent (immutable citations)

- `artifacts/wiki/fo-raw-area/intake-2026-07-13.md`, sha256
  `9b440929479d5647ccb53c526ca50e3db5b3a3ada67f555304b5ebc82d4f1c75`.
- `artifacts/wiki/fo-raw-area/intake-confirmation-2026-07-13.md`, sha256
  `4b3fb4bd3058a28d818eb81ec1b35dd0d20114d2846739b400f6934ad50e8765` —
  verbatim "FO confirmed", bound to the v0.1.0 reading (blob
  `7c10b2ffe4f9e6903328669baf68ab2ff004df86`), Q1 default locked.
- Prior art: FO-WIKI-INVESTIGATION-STANDARD v0.3.1 + packet v0.10.2 (merged
  via wiki PR #70/#73/#74) — the raw-ingested-research class concept
  (`is_raw_ingested_research`, `build_site.py:1021`) and Topic Details.

## 1. Requirements (each individually verifiable)

- **R1 — One global Raw Area page; membership formula.** A regular on-disk
  file is a member iff:
  `regular ∧ not-control ∧ (inbox-ingestion-evidence ∨ TAI-RES)`, where
  - **control** (complete grammar, checked first): any `README.md`, any
    `.gitkeep`, `raw/inbox/manifest.jsonl`, anything under
    `raw/inbox/manifest.d/`;
  - **inbox-ingestion-evidence:** a file of ANY suffix under
    `raw/inbox/<YYYY-MM-DD>/**` that has a VALID file-shape manifest row
    (base ∪ shards, per R6) whose `source_path` matches, OR whose filename
    matches the browser-upload grammar `<stem>-<sha12><suffix>` (twelve hex
    before the final suffix; the upload writer preserves the original
    suffix, defaulting to `.md` only when absent);
  - **TAI-RES:** basename matching `tai-res-*.md` (case-insensitive)
    anywhere under `raw/`.
  An evidence-less file never lists by location alone. Verifiable: fixtures
  in both directions including an evidence-less dated `.md`, a manifested
  non-`.md` upload (member), an upload-grammar `.txt` (member), a control
  path that also carries evidence (excluded — control checked first), and
  every control class; live-corpus check (all 15 current inbox members carry
  manifest rows; all current members happen to be `.md`).
- **R2 — Organized by ingestion date, newest first; total deterministic
  order.** Groups by ingestion date, newest first; entries within a group by
  (original name, source path) — the second key makes the order total even
  for duplicate original names (live today: the owainlewis pair). Date source: valid file-shape manifest rows' `ingested_at`;
  members without a row fall back to their `raw/inbox/<YYYY-MM-DD>/` path
  date; otherwise the visible "date unknown" group. When multiple valid rows
  reference one `source_path`, the winning row is selected by the **total
  order**: (1) latest timezone-normalized `ingested_at`; (2) container rank
  (shards over base — shards are by construction later appends); (3)
  container filename descending; (4) line number descending; (5) canonical
  row digest — and any tie past step 1 is surfaced as an anomaly. Verifiable:
  fixtures for precedence, same-container and cross-container equal-time
  ties, and within-group ordering.
- **R3 — Unique identifier distinct from the original name; recorded vs
  current identity.** Each entry displays a stable identifier and the
  original name as two distinct fields. Identifier chain: (1) the winning
  manifest row's `sha256` (recorded ingest identity); (2) else the
  filename's sha12; (3) else the file's content sha256 computed at build,
  labeled "computed". 12-hex display prefixes; prefix collisions between
  distinct identities expand (64-hex sources) or append a labeled computed
  disambiguator (sha12 sources). **Shared recorded identity ≠ identical
  current content:** entries whose CURRENT computed hashes match render the
  "identical content ×N" cross-reference; entries sharing only a recorded
  manifest identity while current bytes diverge render the shared-recorded-
  identity note PLUS their per-entry "modified since ingest" marks — the two
  states are never conflated. Mismatches mark the entry AND count in the
  anomaly footer. Display-layer only. Verifiable: fixtures per identity
  source, per collision shape, current-identical twins, recorded-shared-but-
  diverged twins, and the mismatch mark + count.
- **R4 — Entries link forward and back.** Forward to the raw file (unservable
  members degrade visibly); back to **every topic page that references it** —
  active plainly, retired included and marked "(retired)". Unreferenced →
  "unassigned — no topic references". Reference domain: `raw_documents` ∪
  `superseded_raw_documents` ∪ `superseded_sources` ∪ class refs in
  `sources`. Superseded marking: the three article-side Topic Details edges
  plus valid manifest rows' `supersedes` (named extension). Verifiable:
  fixtures per field, per edge, retired mark, unreferenced note.
- **R5 — Reachable from the site navigation.** One nav entry; the permitted
  delta is exactly one anchor appended to each of the two shared top-links
  variants; article index rows, investigation nav semantics, and the bottom
  navbox unchanged. **The `raw` route is reserved against future
  article-slug collisions:** the page-creation guard's collision surface
  gains a constant reserved generated-route slug set (containing at least
  `raw`) so `subject_absent("Raw")` refuses — a DENIAL-ONLY addition (it can
  only refuse more, never permit more). The `raw` route also joins the
  existing builder-page classification (`BUILDER_PAGES`, which already
  names `sources`/`ingest`/`repos`) so article links to `raw.html` gate as
  a known page instead of downgrading — an additive classification entry.
  Verifiable: the nav test asserts exactly the named delta; a guard test
  proves reserved names are refused; a link-gate test proves `raw.html`
  classifies as a builder page.
- **R6 — Builder invariants; design-local manifest reader contract.** No
  LLM; no network-capable calls (imports AND call sites); air-gap-safe; both
  themes via the existing palette; degraded states visible. The reader
  enforces **design-local row requirements derived from the production
  constructors** (`ingest_ops.py:1226`–`:1244` key sets; duplicate-key
  rejection mirroring the stored-manifest read path `:1299`–`:1308`;
  timezone-aware `ingested_at` required by THIS design even though the
  writer validates only its own `now` argument): file rows exactly
  {`ingested_at`, `mode`, `target_slug`, `source_path`, `sha256`,
  `original_name`, `note`, `supersedes`}; URL rows exactly {`ingested_at`,
  `mode`, `target_slug`, `source_url`, `note`, `supersedes`};
  `note`/`supersedes`/`target_slug` blankable; other applicable strings
  non-blank; `sha256` 64-hex; set equality both ways; rejected rows are
  surfaced anomalies contributing nothing. The page renders `original_name`,
  `source_path` (anomaly contexts), and `source_url` (URL-ingest footer)
  escaped; `note` and `mode` are NEVER rendered. Tests wired through
  `package.json`, including a Raw Area render/DOM smoke. Verifiable:
  `npm run verify` green; per-key table-driven rejection tests for both
  shapes; escaping tests for every rendered manifest field.

## 2. Non-goals and constraints

Unchanged from v0.5.0 EXCEPT two narrow, named carve-outs: (1) the
page-creation guard (`ingest_server._investigation_collision_corpus`) may
gain a constant reserved generated-route slug set of EXACTLY {`raw`} for
this order (any wider set requires separate authorization) so the reserved
route refuses new-page creation — refusal-only; (2) `ingest_ops.BUILDER_PAGES` gains the
single entry `raw` so the existing link classifier treats the new route as
the known builder page it is — additive classification with no authority or
behavioral surface beyond link rendering; no other
ingest-op/authorization/scanner change (the reader's stricter
row requirements are design-local — strengthening `ingest_ops` itself would
be a separately authorized order); no `raw/**`
moves; no Topic Details changes; no RBAC; no public exposure; no content
transformation. Worktrees only; full TLC arc; merge remains Michael's;
hex-free session filenames; no high-entropy tracked fixture literals; F9
two-step if any pin needed; semver + blob-SHA truth rules.

## 3. Verification of the gap (measured 2026-07-13, repos/wiki @ origin/main 7bf5538)

- No date-organized, identity-bearing, back-linked global raw surface exists.
- Manifest: 9 base rows + 8 shards = 17 (modes across the 15 live inbox-member
  rows: 12 `browser-ingest`, 2 `corpus-copy`, 1 `session-author`; plus 1
  URL row and 1 out-of-inbox `session-author` row); every row carries
  `target_slug` (blankable).
- Live class: **20 documents** — 15 inbox members (all with rows; all
  currently `.md`) + 5 out-of-inbox `tai-res-*` (one with a shard row; 4
  computed-identity). Two members share one recorded sha256 AND identical
  git blobs (currently identical content).
- Upload machinery preserves arbitrary suffixes
  (`ingest_server.py:634`–`:666`): the class is not Markdown-only by
  construction.
- Retired pages render; search-indexing excluded only.

## 4. Intake confirmation — binding record

- **Confirmed:** the v0.1.0 reading (blob in §0), Michael, 2026-07-13,
  verbatim "FO confirmed"; Q1 default locked.
- Version chain: v0.2.0 confirmation record (blob `8c3c16e7…`) → v0.3.0
  CFADA-r1 (blob `806aabc9…`) → v0.4.0 CFADA-r2 (blob `9cc2fc69…`) →
  v0.5.0 CFADA-r3 (blob `9c2bc7e9…`) → v0.6.0 CFADA-r4 (blob `7fc03d97…`)
  → v0.6.1 CFADA-r5 (blob `c8c51d64…`) → v0.6.2 CFADA-r6 (blob
  `13786b7c…`) → v0.7.0 PR-review r1 (blob `dda6c425…`) → v0.7.1
  PR-review r2 (blob `f5825535…`) → **v0.7.2 PR-review r4 (this file)**.
- **Michael's explicit confirmation of the v0.7.2 bytes is a named
  precondition for Human Design Review entry.** Fail closed.

## 5. v0.1.0 → v0.7.2 delta record (what the byte-confirmation covers)

1. **R1:** membership = `regular ∧ not-control ∧ (evidence ∨ TAI-RES)`;
   evidence = valid row ∨ upload grammar `<stem>-<sha12><suffix>` (ANY
   suffix — the r3-repair's `.md`-only narrowing is reversed as unfaithful
   to the upload machinery); control grammar checked first (CFADA-r3 F1,
   r4 F1).
2. **R2:** total-order winner key for duplicate rows incl. same-container
   ties; within-group ordering named (CFADA-r2 F4, r3 F3, r4 F4).
3. **R3:** identity chain + computed fallback; per-source collision
   handling; recorded-vs-current identity distinguished — "identical
   content" only when current hashes match (CFADA-r1 F4, r2 F1/F6, r4 F3).
4. **R4:** retired back-links included+marked; four-field union; four
   supersession edges (CFADA-r1 F3, r2 F3).
5. **R5:** shared-nav delta named exactly (CFADA-r1 F8).
6. **R6:** design-local reader contract derived from production
   constructors (not overclaimed as "the writer's contract"); rendered-field
   enumeration with `note`/`mode` never emitted; network-capable-call
   inspection strengthened beyond imports (CFADA-r3 F2, r4 F2/F5); render
   smoke (r1 F7); fixture scan constraint.
7. **§3:** measurements corrected cumulatively.
9. **Route reservation + total entry order (v0.7.0, wiki#80 PR-review
   findings):** the `raw` route is reserved in the creation guard's
   collision surface (denial-only; §2 carve-out) so a future investigation
   named "Raw" cannot overwrite the tool page; `raw` joins
   `ingest_ops.BUILDER_PAGES` so article links to the route classify as a
   known page (r2 finding — `sources`/`ingest`/`repos` are ALREADY
   classified there; only the slug-reservation half of the class
   pre-exists); within-group entry ordering gains the source-path secondary
   key (the live corpus already holds two entries sharing one
   `original_name`). The pre-existing SLUG-RESERVATION exposure for
   `sources`/`ingest`/`repos` (equally unreserved in the creation guard
   today) is a named follow-up order, deliberately NOT folded into this
   one.
8. **Metadata-visibility widening (v0.6.1, CFADA-r5 F1) — for explicit HDR
   attention:** because ingestion evidence admits ANY suffix, a legitimate
   non-servable-suffix upload (e.g. `report-<sha12>.bin`) appears on the Raw
   Area by name/date/identifier with a visibly-unserved (non-clickable)
   entry, while the Source Index — which lists only servable extensions —
   omits it. The Raw Area therefore INTENTIONALLY widens metadata visibility
   for evidence-backed ingests relative to the Source Index; file CONTENT
   serving is unchanged (the serving allowlist is untouched). This is
   distinct from the crafted-evidence residual (deliberately staged names or
   rows), which remains a named residual risk.

This FO grants nothing and authorizes no code. Next: packet v0.7.3 → IADA r11
→ codex re-review at the PR head → Michael's v0.7.0 byte-confirmation +
Human Design Review.
