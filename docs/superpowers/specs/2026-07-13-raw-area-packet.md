---
doc_id: DF-DESIGN-WIKI-RAW-AREA
version: "0.7.6"
status: "draft — wiki#80 PR-review r7 repairs applied (manifested unservable-suffix case; FO chain full blobs); pre-final-review"
factory: transpara-ai/wiki
author_family: claude
factory_order: "FO-WIKI-RAW-AREA v0.7.4 (blob a594125d989df2c6b5df614cf903f10dc7424074; confirmed READING = v0.1.0 blob 7c10b2ffe4f9e6903328669baf68ab2ff004df86; byte-confirmation of the BOUND FO BLOB by Michael is a NAMED PRECONDITION for stage-6 entry)"
---

# Raw Area — TLC Design Packet

> Answers FO-WIKI-RAW-AREA v0.7.4 (R1–R6) against measured live state at
> `transpara-ai/wiki` origin/main `7bf55384da70a30f636ad661bb5129d704775180`.
> One new generated tools page, `raw.html`, in the Sources/Ingest pattern.
> Builder stays no-LLM/no-network. This packet authorizes nothing.
> Amended v0.1.0 → v0.7.5 across CFADA rounds 1–7 and wiki#80 PR-review
> rounds 1–6 (every finding accepted-repaired; the round-by-round record is
> `artifacts/wiki/fo-raw-area/iada/iada.result.md` and
> `cfada/codex-round*.out`). This header carries no per-version narrative
> (so it can never go stale); the FO's §5 delta record is the cumulative
> intent history.

## 1. Survey — measured, not assumed (file:line at main `7bf5538`)

- **Tools-page pattern.** `sources_page()` (`build_site.py:2153`),
  `ingest_page()`, `tool_page()` (`:2132`), written at `:2722`–`:2723`;
  shared top-links variants `:2103`–`:2104` and `:2120`.
- **Membership truth.** `is_raw_ingested_research` (`:1021`) accepts any
  `raw/inbox/**` reference — location alone over-matches (31 tree paths).
  The browser-upload writer preserves ARBITRARY suffixes:
  `dst = <stem>-<digest[:12]><suffix>` with `suffix = original's or ".md"`
  (`ingest_server.py:634`–`:666`) — the ingested class is NOT Markdown-only
  by construction. Membership therefore follows FO R1's formula
  `regular ∧ not-control ∧ (inbox-ingestion-evidence ∨ TAI-RES)` (D2a).
  Live membership: **20 documents** — 15 inbox members (all 15 with valid
  file-shape rows: 12 `browser-ingest`, 2 `corpus-copy`, 1 `session-author`;
  all currently `.md`) + 5 out-of-inbox `tai-res-*.md` (one `session-author`
  shard row; 4 computed-identity). Two members share one recorded sha256 AND
  are currently identical git blobs.
- **`sources.html` overlap.** The Source Index sweeps every servable
  `raw/**` file alphabetically (`:1503`–`:1507`) — undated, identity-less,
  topic-unlinked. The Raw Area is the dated, identity-bearing, back-linked
  complement; `sources_page` is not edited.
- **Manifest truth.** 9 base rows + 8 shards = 17. Row shapes and validation
  live in the production constructors (`ingest_ops.py:1226`–`:1244`): file
  rows carry exactly {`ingested_at`, `mode`, `target_slug`, `source_path`,
  `sha256`, `original_name`, `note`, `supersedes`}, URL rows exactly
  {`ingested_at`, `mode`, `target_slug`, `source_url`, `note`, `supersedes`};
  blankable {`note`, `supersedes`, `target_slug`}; 64-hex `sha256`.
  **Scope-precise:** duplicate-key rejection exists on the stored-manifest
  READ path (`:1299`–`:1308`), and the writer's timezone check validates its
  own `now` argument (`:1261`–`:1264`), not `row["ingested_at"]` — so this
  design imposes its reader requirements AS ITS OWN (D5), derived from those
  constructors, without claiming the writer enforces them row-wise.
  Same-instant distinct rows are permitted (`:1265`–`:1268`).
- **Serving.** `safe_source_path()` (`:971`) serves ROOT-relative
  {md,txt,json,yml,yaml,csv,toml}; every current member and any manifested
  upload of those suffixes is linkable via `source_href()` (`:996`); other
  suffixes degrade visibly (D4).
- **Back-link inputs.** `META` (`:352`–`:377`) minimal;
  `article_frontmatter()` (`:1183`–`:1188`) in the build loop supplies
  frontmatter for the ref→articles fold. `topic_details_refs` (`:1048`)
  treats `sources` as fallback (`:1059`–`:1069`); `topic_details_superseded`
  (`:1078`–`:1095`) recognizes `supersedes:` annotations.
- **Retired pages render** (`:2699`); search-excluded only (`:2656`–`:2661`).
- **Route integration surfaces (verified).** `ingest_ops.BUILDER_PAGES`
  (`:50`) = {`repos`, `sources`, `ingest`, `civilization-arc`,
  `civilization_arc`} feeds the link-target classifier (`:616`) — `raw` is
  absent, so article links to `raw.html` would classify unknown; and the
  creation guard's collision surface
  (`ingest_server._investigation_collision_corpus`, `:387`) is built from
  `wiki/*.md` only — no generated route is reserved, so
  `subject_absent("Raw")` would permit a colliding article. Both integrated
  by D7a.
- **Render smoke target set is memorized** (`tests/inc001-render.spec.js:4`–
  `:30`; DOM tests arc+ingest only, `package.json:10`) — D7 adds `raw.html`.
- **`dist/` untracked**; scanner rules `secret_scan.py:51`–`:54`
  (`CANDIDATE_RE {16,}` assignment-context ≥3.5 bits; `ENTROPY_TOKEN_RE
  {32,}` backstop ≥4.5 bits) — fixture policy stays below both.

## 2. Decisions

- **D2a — Membership formula (FO R1).** `raw_area_documents()` evaluates,
  in order: (1) regular file? (2) **control?** — any `README.md`, any
  `.gitkeep`, `raw/inbox/manifest.jsonl`, `raw/inbox/manifest.d/**` → OUT,
  even if evidence exists (control precedence); (3) **inbox-ingestion-
  evidence:** ANY-suffix file under `raw/inbox/<YYYY-MM-DD>/**` with a valid
  file-shape row (D5) whose `source_path` matches, OR a filename matching
  `<stem>-<12 hex><suffix>`; (4) **TAI-RES:** basename `tai-res-*.md`
  (case-insensitive) anywhere under `raw/`. Member iff (3) or (4) after
  passing (1)–(2). Defined once; used by the page and every fixture.
- **D2b — Corpus = on-disk filesystem state, evidence-gated; visibility
  relation to the Source Index stated exactly.** Untracked strays cannot
  list without evidence. Relative to the Source Index sweep the Raw Area is
  narrower for evidence-less files (they never list here, but a servable
  stray lists there) and **intentionally wider in one named way**: a
  legitimate evidence-backed ingest of a NON-servable suffix (e.g.
  `report-<sha12>.bin`) appears here by name/date/identifier as a visibly
  unserved entry while the Source Index omits it — metadata visibility only;
  the content-serving allowlist is untouched (FO §5 item 8, carried for
  HDR). Residual: crafted evidence (a faked upload-grammar name or manifest
  row) could stage a local listing — §5.
- **D2 — Date chain + total-order winner key.** Per member: (1) winning
  valid file-shape row's `ingested_at`; (2) else inbox path date ("inbox
  date"); (3) else visible "Date unknown" group. **Winner among multiple
  valid rows for one `source_path` (total order):** latest timezone-
  normalized `ingested_at`; then container rank (shards over base); then
  container filename descending; then line number descending; then canonical
  row digest (`sha256` of the canonical-JSON row). Any tie past the first
  key surfaces as an anomaly. **Grouping basis:** an entry's group is the
  UTC-normalized calendar date of its winning `ingested_at` (an offset
  timestamp near midnight groups by its UTC date, not its local date);
  inbox-path dates (chain step 2) are already calendar dates and group
  as-is. Groups newest-first; entries within a group by
  (original name, source path) — total even for duplicate original names
  (live: two 2026-07-07 entries share `original_name`).
- **D3 — Identity display; recorded vs current.** Fields per entry:
  **identifier** — (1) winning row `sha256` (recorded ingest identity);
  (2) else filename sha12; (3) else computed content sha256 labeled
  "computed" (4 of today's 20) — 12-hex prefix display; prefix collisions
  between distinct identities expand (64-hex sources) or append a labeled
  computed disambiguator (sha12 sources); and **original name** — the row's
  `original_name` when one exists; for a rowless upload-grammar member the
  deterministic reconstruction `<stem><suffix>` (sha12 infix stripped),
  visibly labeled "reconstructed from stored name"; plain basename only for
  lane-(b) members (their names are authored, not hashed) — a hashed
  storage basename is never presented as an original name (FO R3). **Recorded ≠ current:** the "identical
  content ×N" cross-reference renders ONLY when current computed hashes
  match; entries sharing a recorded identity with diverged current bytes
  render a "shared recorded identity" note plus their own "modified since
  ingest" marks — never conflated. Mismatches mark the entry AND count in
  the footer. Rendered manifest-derived fields are exactly
  {`original_name`; `source_path` in anomaly contexts; `source_url` in the
  URL-ingest footer}, all `html.escape`d; **`note` and `mode` are never
  emitted**. **URL-row scope:** URL rows NEVER produce a document entry;
  their `source_url` appears ONLY in the anomalies footer's URL-ingest
  count/listing (escaped) — "counted, not listed" means absent from the
  document-entry container, present in the footer.
- **D4 — Links, back-links, supersession, anomalies.** Forward via
  `source_href` (unservable → visible `.source-unserved`). Back-links folded
  in the article build loop from `article_frontmatter` bytes — four-field
  union (`raw_documents` ∪ `superseded_raw_documents` ∪ `superseded_sources`
  ∪ class refs in `sources`); EVERY referencing topic page lists: active
  pages as live links; retired pages as visibly marked NON-LINK references
  ("(retired)" text, no anchor) — conforming to the site's fail-closed link
  policy (`link_state`, `ingest_ops.py:563`, renders every retired target
  non-live; `gate_internal_links`, `build_site.py:800`, suppresses such
  anchors; this order changes no link policy); unreferenced → "unassigned —
  no topic references". Supersession — four edges (three article-side incl.
  `supersedes:` annotations; valid rows' `supersedes` as the named
  extension). Anomalies footer + one warning line each: absent targets;
  rejected rows (per D5 lane); URL rows (counted); prefix collisions;
  identical-content sets; shared-recorded-diverged sets; mismatch count;
  duplicate-row ties. One bad input never takes the build down.
- **D5 — Design-local manifest reader (default deny), derived from the
  production constructors.** Line-level JSON parse with three explicit
  **parse-level rejection lanes** preceding shape checks — an
  undecodable/malformed line, a blank line, and a decodable non-object
  top-level value (the production read path's distinct failure classes,
  `ingest_ops.py:1299`–`:1310`) — each a surfaced anomaly contributing
  nothing, never a crash. Duplicate keys reject (this design's own rule,
  mirroring the stored-manifest read path). Shape by key set alone: file row = the 8-key set exactly; URL row = the 6-key set
  exactly; set equality both ways; hybrids fit neither. Types: strings;
  blankable {`note`, `supersedes`, `target_slug`}; others non-blank where
  present; `sha256` 64-hex; `ingested_at` timezone-aware ISO-8601 (this
  design's requirement). Every rejection lane is a surfaced anomaly;
  rejected rows contribute nothing. All 17 live rows validate.
- **D5b — Chrome and invariants.** `tool_page` chrome; existing palette;
  lists and links only; no LLM; **no network-capable calls** (see AC-I1).
- **D6 — Named tests** (new `compile/test_build_site_raw_area.py` wired into
  `test:py`; plus the D7 spec edit). Fixture policy: tracked literals below
  both scanner rules; 64-hex values runtime-generated in temp trees.
  Composite tests enumerate **named parameterized cases** — each case is a
  separately reported subtest (pytest-style parametrization or explicit
  sub-asserts with case ids), so a failure names its case.
  1. `test_raw_page_lists_exactly_the_enumerated_class`
  2. `test_raw_page_membership_formula` — named cases: (a) evidence-less
     dated `.md` OUT; (b) manifested `.md` IN; (c) manifested `.txt` IN;
     (d) upload-grammar `.txt` without row IN; (e) upload-grammar `.md`
     without row IN; (f) out-of-inbox `tai-res-*.md` IN; (g) control paths
     OUT (manifest base, shard, shard-dir README, generic inbox README,
     `.gitkeep`); (h) control path WITH crafted evidence OUT (control
     precedence); (i) non-md non-evidence stray OUT; (j) rowless
     upload-grammar UNSERVABLE suffix (`report-<sha12>.bin`) IN — listed,
     visibly unserved; (k) mixed-case `TAI-RES-*.md` and `Tai-Res-*.md` IN
     (case-insensitive lane); (l) MANIFESTED custom-named unservable file
     (valid row, no sha12 name, e.g. `notes.docx`) IN — the manifest lane is
     suffix-agnostic (listed, visibly unserved)
  3. `test_raw_page_groups_by_date_newest_first` — incl. the UTC basis:
     an offset timestamp crossing midnight groups by its UTC date
  4. `test_raw_page_entries_order_total_within_group` — named cases:
     (a) original-name primary order; (b) the duplicate-original-name pair
     (live shape) orders by source path deterministically
  5. `test_raw_page_duplicate_row_winner_total_order` — named cases:
     (a) later `ingested_at` wins; (b) equal instant across containers →
     shard over base, then filename desc; (c) equal instant same container →
     line desc; (d) full tie → digest; each tie past case (a) surfaces the
     anomaly
  6. `test_raw_page_manifest_date_beats_inbox_dir_date`
  7. `test_raw_page_unknown_date_falls_safe`
  8. `test_raw_page_shard_manifest_rows_are_read`
  9. `test_raw_page_identity_chain_and_labels` — incl. the rowless
     upload-grammar case: original name shown as the labeled
     reconstruction, never the hashed storage basename
  10. `test_raw_page_prefix_collision_disambiguates` — cases: (a) 64-hex
      sources expand; (b) sha12 sources append the labeled computed
      disambiguator; both surface anomalies
  11. `test_raw_page_current_identical_twins_cross_referenced` — the live
      shape: two paths, equal current hashes → "identical content ×2"
  12. `test_raw_page_shared_recorded_identity_diverged_bytes` — equal row
      `sha256`, diverged current bytes → shared-recorded note + per-entry
      mismatch marks, NO "identical content" claim
  13. `test_raw_page_modified_since_ingest_mark_and_count`
  14. `test_raw_page_forward_links` — cases: (a) every servable fixture
      member carries an href; (b) an unservable-suffix member degrades to
      the visible unserved style
  15. `test_raw_page_backlink_union_all_four_fields`
  16. `test_raw_page_retired_backlinks_marked` — the retired reference
      renders as marked text with NO anchor element (policy-conformant)
  17. `test_raw_page_unreferenced_file_marked_unassigned`
  18. `test_raw_page_superseded_marking_all_edges` — four named edge cases
  19. `test_raw_page_manifest_rejection_lanes` — named cases: **parse-level
      lanes first — undecodable/malformed JSON line; blank JSONL line;
      decodable non-object top-level value (each surfaced once, contributes
      nothing, build exit 0)**; then each of the 8 file-row keys removed;
      each of the 6 URL-row keys removed; extra key; hybrid row; duplicate
      JSON keys; wrong-typed field; blank required field; non-64-hex sha;
      naive timestamp; malformed offset-bearing timestamp
      (`not-a-date+00:00`); invalid calendar date with valid offset; PLUS acceptance cases: valid file/URL rows with blank
      `note`/`supersedes`/`target_slug`; every rejection surfaced, build
      exit 0, no contribution
  20. `test_raw_page_url_rows_counted_not_listed` — asserts absence from
      the document-entry container AND presence (escaped) in the footer's
      URL-ingest listing (scope per D3; no conflict with D6.23c)
  21. `test_raw_page_absent_manifest_target_surfaced`
  22. `test_raw_page_anomaly_warnings_emitted` — one line per exercised lane
  23. `test_raw_page_rendered_fields_escaped_and_bounded` — named cases:
      (a) markup in `original_name` escapes; (b) markup in anomaly-listed
      `source_path` escapes; (c) markup in `source_url` escapes; (d) `note`
      and `mode` values never appear in the rendered page
  24. `test_raw_page_single_nav_entry_both_variants`
  25. `test_raw_route_reserved_in_creation_guard` — `subject_absent("Raw")`
      returns False after the reserved-set addition; the set equals exactly
      {`raw`} (scope assertion); a control name unaffected by the set still
      creates (the addition is denial-only)
  26. `test_raw_route_classified_as_builder_page` — the target classifier
      returns ("page", "raw") for `raw.html` (mirroring
      sources/ingest/repos), so article links gate as known-page, not
      unknown/downgraded
- **D7a — Route integration (the two FO §2 carve-outs).** (1) A constant
  reserved generated-route slug set of EXACTLY {`raw`} — this order
  authorizes no other member; widening it (e.g. to sources/ingest/repos,
  the deferred class) requires separate authorization — is added to
  `_investigation_collision_corpus`'s slug surface so `subject_absent`
  refuses the reserved name — DENIAL-ONLY: it can only refuse more, never
  permit more (test D6.25 includes the control case proving an unaffected
  name still creates, and asserts the set equals {`raw`}). (2) `raw` is added to `ingest_ops.BUILDER_PAGES` so
  the link-target classifier returns ("page", "raw") for `raw.html`,
  mirroring sources/ingest/repos — additive classification with no surface
  beyond link rendering (test D6.26).
- **D7 — File plan.** EDIT `compile/build_site.py` (membership formula,
  reader, folds, `raw_page()`, write at `:2722` block, one anchor per shared
  top-links variant); EDIT `compile/ingest_server.py` (ONE denial-only
  change: the D7a reserved-route slug set, exactly {`raw`} — FO §2
  carve-out 1); EDIT
  `compile/ingest_ops.py` (ONE additive entry: `raw` in `BUILDER_PAGES` —
  FO §2 carve-out 2); ADD `compile/test_build_site_raw_area.py` (26 named
  tests); EDIT `tests/inc001-render.spec.js` (add `raw.html`); EDIT
  `package.json` (wire test module). UNTOUCHED beyond those named
  single-line carve-outs: all other `ingest_server.py`/`ingest_ops.py`
  behavior, `secret_scan.py`, `sources_page`/`ingest_page` bodies,
  article/investigation nav semantics, navbox, arc/board/front page, all
  `raw/**` bytes.

## 3. Acceptance criteria — one criterion per verification item

Each AC-T*n* = named test D6.*n* green at the exact PR head (its named
parameterized cases all passing and individually reported); risk per row.

| AC | = | Criterion | Risk |
|---|---|---|---|
| AC-T1 | D6.1 | entry set == formula enumeration, both directions | med |
| AC-T2 | D6.2 | membership formula: all twelve named cases | high |
| AC-T3 | D6.3 | groups newest-first | low |
| AC-T4 | D6.4 | within-group order total: (original name, source path) | low |
| AC-T5 | D6.5 | duplicate-row winner total order: all four named cases + tie surfacing | med |
| AC-T6 | D6.6 | manifest date beats inbox-dir date | med |
| AC-T7 | D6.7 | unknown-date fail-safe group | med |
| AC-T8 | D6.8 | shard rows read (frozen-file law) | high |
| AC-T9 | D6.9 | identity chain order and labels | med |
| AC-T10 | D6.10 | prefix-collision handling per source shape | low |
| AC-T11 | D6.11 | current-identical twins cross-reference | med |
| AC-T12 | D6.12 | shared-recorded-identity with diverged bytes never claims identical content | med |
| AC-T13 | D6.13 | mismatch mark + footer count | med |
| AC-T14 | D6.14 | forward links serve; unservable degrades visibly | med |
| AC-T15 | D6.15 | back-link union covers all four fields | med |
| AC-T16 | D6.16 | retired references marked, non-link, never omitted | med |
| AC-T17 | D6.17 | unreferenced members carry the explicit note | low |
| AC-T18 | D6.18 | each of the four supersession edges marks; none hides | med |
| AC-T19 | D6.19 | every rejection lane rejects+surfaces; blank-optional rows accepted | high |
| AC-T20 | D6.20 | URL rows counted, never listed | low |
| AC-T21 | D6.21 | absent manifest targets surface | med |
| AC-T22 | D6.22 | one warning line per anomaly lane | low |
| AC-T23 | D6.23 | rendered-field escaping incl. `note`/`mode` never emitted | med |
| AC-T24 | D6.24 | exactly the named nav delta and no other | low |
| AC-T25 | D6.25 | the reserved set equals exactly {`raw`}; the reserved name refuses creation; denial-only control case | high |
| AC-T26 | D6.26 | `raw.html` classifies as a builder page for link gating | med |
| AC-S1 | D7 | `raw.html` in the render-smoke target set and green | med |
| AC-I1 | inspection | no network-capable call at the PR head: import sweep AND call-site sweep (`socket`, `http.client`, `urllib`, `requests`, subprocess-to-network tools) over the diff, recorded in review evidence | med |
| AC-I2 | inspection | no new subprocess use | med |
| AC-I3 | inspection | no LLM invocation | med |
| AC-I4 | inspection | chrome via `tool_page`; no bespoke page shell | low |
| AC-I5 | inspection | colors via existing custom properties only | low |

**FO trace:** R1 → AC-T1, T2 · R2 → AC-T3–T8 · R3 → AC-T9–T13 ·
R4 → AC-T14–T18, T20–T23 · R5 → AC-T24, AC-T25, AC-T26 · R6 → AC-T19,
AC-S1, AC-I1–I5.

**Gate satisfied-only-when (allowlist):** the code PR is satisfied only when
ALL thirty-two criteria (26 tests + 1 spec-edit + 5 inspections) are evidenced at
the exact PR head. Any unproven criterion — including any single named
parameterized case — ⇒ not satisfied. Default deny.

## 4. Fail-safe analysis

- **Membership:** evidence-gated formula, control-precedence, both-direction
  fixtures; location alone lists nothing.
- **Dates:** chain ends in the visible unknown group; duplicate-row
  selection is a total order with surfaced ties.
- **Reader:** design-local default-deny contract; rejected rows contribute
  nothing; every lane surfaces.
- **Identity:** recorded vs current never conflated; collisions
  expand/label; equal identities cross-reference; mismatches mark and count.
- **Rendering:** enumerated field set, escaped; `note`/`mode` never emitted;
  anomalies footer + warnings; unservable degrades visibly; one bad input
  never kills the build.
- **The page grants nothing.**

## 5. Residual risks (named, carried — left OPEN for Human Design Review)

- **Staged-evidence listing** on the live serving clone (a crafted
  upload-grammar name or manifest row) — deliberate action required;
  distinct from the INTENTIONAL metadata-visibility widening for legitimate
  non-servable-suffix ingests (FO §5 item 8, D2b), which is a design
  decision carried to HDR, not a risk.
- **Identifier display length grows** under collision/duplication handling.
- **"Date unknown" may be empty on today's corpus** — fixture-proven anyway.
- **Class-concept coupling** to `is_raw_ingested_research` where evidence
  lanes also match (deliberate, named).
- **Pre-existing reserved-route class (slug reservation only):**
  `sources`/`ingest`/`repos` routes are unreserved in the CREATION GUARD
  today (an investigation named "Sources" would collide the same way) — the
  class fix is a named follow-up order; this packet only refuses to add a
  fourth instance. Their LINK classification is already handled
  (`BUILDER_PAGES`), and `raw` joins it here.
- **Byte-confirmation of the bound FO pending:** the frontmatter's exact
  FO blob (`a594125d989df2c6b5df614cf903f10dc7424074`) — NAMED PRECONDITION for
  stage-6 entry.

## 6. Non-authorizations

No code (Human Design Review gates stage 7), no merge, no deploy, no
ingest-op change beyond the two named FO §2 carve-outs (reserved-route
denial set; the single additive `BUILDER_PAGES` entry)
(the reader contract is design-local; strengthening `ingest_ops` would be
its own order), no `raw/**` moves, no scope beyond
the bound FO's R1–R6.
