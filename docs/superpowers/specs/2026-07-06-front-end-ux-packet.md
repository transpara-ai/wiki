---
doc_id: TAI-WIKI-FRONTEND-UX
title: Front-end requirements completion — §7 ingest UX, honest-state styling, sanctioned session-author registration (TLC Design Packet)
doc_type: design
version: 0.3.1
status: draft
canonical: false
created: 2026-07-06
updated: 2026-07-06
owner: Michael Saucier
steward: Claude (Fable 5)
authority: planning
tlc_stage: design
factory_order: FO-WIKI-FRONTEND-UX v0.3.1 (blob 8beb807911f4b2c37c62b8a57fff2a7187b58657, confirmed channel-A 2026-07-06; R5 survey-corrected at v0.3.x)
source_of_intent:
  - the Factory Order above (its §5 archives Michael's intake answers verbatim)
  - docs/superpowers/specs/2026-07-01-per-ingestion-operations-design.md §7 (blob d21e2fef)
  - transpara-ai/wiki#50, #52 (R6 lineage)
intake_channel: A (owner-directed session 2026-07-06)
---

# Front-end requirements completion — TLC Design Packet

> Answers FO-WIKI-FRONTEND-UX v0.3.1 (R1–R6) against measured live code
> (wiki main @ `ca23a85`, survey 2026-07-06). Design rule inherited from the
> house: every state indicator renders from an allowlist; unknown, missing,
> or unreadable state renders degraded/explicit — never healthy.

## 1. Survey — measured, not assumed (file:line evidence)

- **Ingest page today** (`build_site.py:1787–1839`, `ingest_page(status)`):
  one Add form (`#ingest-form`) — authoring-token password field, target
  select (build-time from META, retired excluded), multi-file input,
  external-URLs textarea, supersedes select (repopulated from
  `/api/articles` sources on target change), note field. Inline JS POSTs
  FormData to `/api/ingest`, renders the JSON response, stores last result
  in sessionStorage, reloads on success. `POST /api/rebuild` behind a
  second button.
- **API surface** (`ingest_server.py:706–744`): GET `/api/health`,
  `/api/articles` (sources included only for loopback/token);
  POST `/api/rebuild`, `/api/ingest`, `/api/replace`, `/api/remove`.
  Refusal shapes: `AuthRefused`→403 `{"error"}`, `OpRefused`→422,
  generic→400. `require_authoring` (`:690–704`): token via
  `hmac.compare_digest` when configured; else loopback + same-origin
  (missing Origin treated same-origin, `:353–354`).
- **Remove consequence data exists server-side**:
  `find_inbound_edges(root, slug)` (`ingest_ops.py:987–1028`) scans
  wiki/*.md + index.md (wikilinks, `slug.html` links, board frontmatter
  refs) → sorted inbound slugs; `remove_topic` stores it as
  `affected_edges` and enqueues `dangling-pending` edges
  (`:1102–1125`). **Replace** preflights already compute the superseded
  ref + the shared/URL refusal lanes (`:817–831`).
- **The rebuild is synchronous inside the POST** (`run_refresh` /
  `rebuild_runner` under `wiki_write_lock`), so "recompiling" is precisely
  the in-flight-request state; there is no background job to poll.
- **edge-states.json** (`ingest_ops.py:45–46, 396–445`): entries
  `{state, since, reason, queued, enqueued_at}`, states allowlist
  `valid | cleanly-removed | dangling-pending`; strict parse REFUSES the
  build on corruption (`build_site.py:364–366`), so a built page's
  edge-state read is trustworthy at build time. Rendered today only as
  per-link dispositions (`link_state()`, `build_site.py:660–703`) — no
  aggregate indicator.
- **Freshness banner** (`build_site.py:1667–1700`): build-time from
  `refresh-status.json` (`synced`/`stale_articles`/`changed_articles`);
  `deploy_status_script()` (`:1703–1717`) client-fetches
  `deploy-status.json` into `#deploy-banner` (hidden unless
  `blocked===true`) and `#deploy-foot` ("live deploy: sha·checked").
  **`.deploy-foot` and the deploy blocked-banner have zero rules in
  `style.css`** (measured: grep = 0) — R4. **`.wl.wl-pending` is already
  styled** (`style.css:35`: muted + dashed underline + help cursor,
  palette-driven) — CFADA-FEUX-005 corrected the v0.2.0 misread; R5 is a
  coverage guard, not new styling (FO v0.3.0).
- **Two ledgers, distinct jobs**: `raw/inbox/manifest.jsonl` — browser
  ingest audit rows `{ingested_at, mode, target_slug, source_path, sha256,
  original_name, note, supersedes}` (`ingest_server.py:438–447`), appended
  at runtime by Add, committed later by a human; **nothing programmatic
  reads it** (audit surface only). `compile/ingest-ledger.jsonl` — Arc 1
  strict-shape ops ledger (`ingest_ops.py:55–63`), preflight-validated
  whole-file before append-last (`:325–378`).
- **Secret-scan F9 mechanic** (`secret_scan.py`, `compile/.secretsallow`):
  allowlist rows pin `(blob_sha256, match_sha256, byte_offset)`. ANY new
  blob of `manifest.jsonl` (runtime append or PR edit) re-trips findings on
  historical high-entropy rows because their clearances pin the OLD blob
  sha — the #50 trap. A PR cannot self-allowlist; and even runtime appends
  poison the NEXT human commit of the file.
- **Authorization artifact** (`ingest_ops.py:52–229`): exact 10-key set,
  `df:"ingest-authorization"`, operation ∈ {replace, remove} (closed
  allowlist), instance match on (operation, slug, source_ref), ≤24h window,
  atomic tombstone consumption before any mutation.

## 2. The contract

### 2.1 File plan

| Action | File | Change |
|---|---|---|
| EDIT | `compile/build_site.py` | `ingest_page()`: operation selector (Add default · Replace · Remove, destructive visually distinct); Replace/Remove forms; consequence-preview panel + confirm flow; in-flight "recompiling…" state; freshness banner gains the pending-edges chip (build-time, from the same strict edge-states load the build already performs); refusal rendering (escaped, honest) |
| EDIT | `compile/ingest_server.py` | `GET /api/preview` (strictly read-only, §2.3); `POST /api/register` (R6, §2.5) mirroring the replace/remove gate order |
| EDIT | `compile/ingest_ops.py` | `preview_remove()` / `preview_replace()` thin wrappers over the EXISTING op preflight helpers (no parallel logic — drift-proof by construction); `register_source()` (R6); `register` added to the artifact operation allowlist + `LEDGER_SHAPES`; manifest append helper with the sharded write path (§2.5) |
| EDIT | `compile/assets/style.css` | `.deploy-foot`, `.deploy-banner[data-blocked]`/`.deploy-blocked`, ingest mode selector + consequence-panel + destructive-accent rules — both themes via the existing custom-property palette (`.wl-pending` already styled at `:35`; covered by the R5 guard, not restyled) |
| EDIT | `compile/ingest-authorization.example.json` + its doc comments | `operation` allowlist gains `register`; register requires non-empty in-repo `source_ref` (documented alongside the replace/remove rules — IADA I6) |
| ADD | `compile/test_ingest_ux.py` (wired into `test:py`) | builder-side ACs: selector emitted, preview panel scaffold, pending-chip states incl. degraded, CSS classes present in the sheet |
| EDIT | `compile/test_ingest_ops.py`, `compile/test_ingest_server.py` | R6 register domain tests; preview read-only + parity tests |
| EDIT | `tests/inc001-render.spec.js` or ADD `tests/ingest-ux.spec.js` | Playwright: selector renders both themes; destructive mode shows preview scaffold; zero console errors |
| UNTOUCHED | authorization semantics, secret_scan rule/allowlist LOGIC, arc view, board, engine boundary, refresh timer | forbidden list §5 |

### 2.2 R1 — Operation selector

Segmented control `Add · Replace · Remove` (radio group, house style).
Add = default = the existing form unchanged. Replace and Remove forms render
only when selected, carry a shared `.ingest-destructive` accent (border +
label treatment, both themes), and each states in one line what the server
will require ("requires a pre-placed single-use authorization artifact on
the server; this page never handles authorization" — Q2 verbatim
constraint). Replace form: target select → source select (that article's
`sources` + `raw_documents`) → replacement file (exactly one) → note.
Remove form: target select only (the retirement rationale is bound to the
artifact's `reason` server-side — CFAR r26 lineage; the UI says so instead
of collecting a reason it would ignore).

The existing authoring-token password field (transport auth for
`require_authoring` when `CIVWIKI_AUTHORING_TOKEN` is configured) is shared
by all three modes exactly as today. This is NOT the authorization the Q2
constraint forbids the UI to handle — Q2's boundary is the single-use
**operation artifact** (`ingest-authorization.json`), which the UI never
reads, displays, checks, or transmits (IADA I4: the distinction stated so
the two auth layers cannot be conflated by a reviewer or a future editor).

### 2.3 R2 — Consequence preview (mandatory, fail-closed, drift-proof)

- **Endpoint:** `GET /api/preview?operation=remove&slug=X` and
  `GET /api/preview?operation=replace&slug=X&source_ref=S`, behind the
  existing `require_allowed_host` + `require_authoring` — deliberately
  STRICTER than live `GET /api/articles`, which is host-gated only with
  conditional source inclusion (`ingest_server.py:706,712` —
  CFADA-FEUX-006 corrected the "same posture" comparison). Strictly
  read-only: consumes no authorization, takes no lock, writes nothing —
  named tests prove the artifact is still valid and the tree unchanged
  after a preview.
- **Echo-quarantine first (IADA I1 — the CFAR-r20 lane, on the read path):**
  `quarantine_fields({operation, slug, source_ref})` runs BEFORE any
  validator or preflight whose refusal message would echo the submitted
  values — a finding refuses the preview with redacted spans, exactly as
  the mutation endpoints do. Nothing reaches an echoing code path
  unproven-secret-free.
- **Parity by construction:** the preview handlers call the SAME functions
  the operations use — `find_inbound_edges` for remove;
  the replace preflight helpers for shared-source/URL-source/unknown-ref
  lanes — never re-implementations. A named test asserts
  `preview_remove(slug).inbound == remove's affected_edges` computation on
  a fixture tree.
- **Response (allowlist of shapes):** remove →
  `{operation, slug, inbound: [slugs], edges_would_pend: N, tombstone:
  "slug.html", will_recompile: true}`; replace →
  `{operation, slug, source_ref, superseded: S, will_recompile: true}` or
  `{refuses: "<the exact OpRefused reason the POST would give>"}` — the
  preview of a doomed operation IS the refusal, shown before any confirm.
- **UI flow:** destructive mode + target selected → preview auto-fetches →
  consequence panel renders (Remove: full inbound-article list — every
  slug a link — + "N edges will mark pending reconciliation" + tombstone
  note; Replace: superseded ref + recompile note; either: the exact
  would-refuse reason) → **submit stays disabled until a preview for the
  CURRENT selection has rendered** (any selection change invalidates it) →
  confirm checkbox ("I have read the consequences") arms the submit.
  Preview fetch failure/timeout/non-200 → explicit "preview unavailable —
  destructive submit stays disabled" state; there is NO submit path without
  a rendered preview (the fail-closed lane).
- The server gate remains the enforcement; the preview/confirm is
  legibility, not authority (FO Q2).

### 2.4 R3 — Honest live state

- **Recompiling:** while a destructive POST (or Add) is in flight the form
  region renders an explicit `recompiling…` state (spinner + text, controls
  disabled); the response restores the normal state machine. Honest because
  the rebuild runs synchronously inside the request (§1). No fake progress.
- **Pending-edges chip:** `freshness(status)` gains one chip sourced from
  the strict edge-states load the build already performs: count of entries
  with `state=="dangling-pending"`. Allowlist rendering: count==0 → no chip;
  count>0 → `N edges pending reconciliation` (warn style); load
  error/unknown state cannot reach the renderer (strict parse refuses the
  build first — that existing gate is the fail-closed guarantee, and a
  builder unit test pins the degraded path by feeding a corrupt fixture and
  asserting the build refuses rather than rendering healthy).
- Tombstones + per-link `dangling-pending` markers stay as shipped; R5
  makes the marker visible.

### 2.5 R6 — Sanctioned session-author registration (issue #50)

- **Operation:** `register` joins the artifact operation allowlist.
  Artifact instance match: `(operation="register", slug=target_slug,
  source_ref=<in-repo raw path>)`; same 10-key schema, ≤24h window,
  tombstone consumption before mutation.
- **Preflights (deterministic, read-only, then consume):** `source_ref`
  matches `RAW_PATH` shape under `raw/`; the file EXISTS in the tree
  (session-authored docs arrive via gated PRs — the op registers, never
  writes content); sha256 computed from the file bytes;
  `quarantine_payload` over those bytes + `quarantine_fields` over metadata
  (reuse, not reimplementation — a finding refuses with redacted spans);
  target article exists and is not retired; ledger + edge-states strict
  preflights as in Replace/Remove.
- **Durable writes (under `wiki_write_lock`, in THIS order —
  CFADA-FEUX-001):** all preflights first (including the ledger
  appendability probe, Arc 1 ready-r4 lineage: an unauditable op refuses
  before ANY write) → artifact consumption → then:
  1. **Manifest shard** — row `{ingested_at, mode: "session-author",
     target_slug, source_path, sha256, original_name, note, supersedes}`
     written as a **single-row shard file**
     `raw/inbox/manifest.d/<UTC ISO-8601 basic, microsecond
     precision>Z-<sha256[:12]>.jsonl`, opened with exclusive create
     (`O_CREAT|O_EXCL`); an existing path REFUSES — never overwrite, never
     append (CFADA-FEUX-004: collision safety is bound to the syscall, not
     asserted; microsecond stamp + content hash make collision practically
     impossible, and the refusal lane exists anyway).
     `raw/inbox/manifest.jsonl` is frozen as the historical segment and
     never rewritten. Per-ROW files (not per-month — IADA I2: a month shard
     grows, so its blob changes on every append and merely narrows the F9
     window) close the #50 class absolutely: every manifest blob is
     immutable from birth, no clearance ever goes stale, no PR or runtime
     append can poison a later commit. Add's manifest writes move to the
     same helper — same class, same fix. The complete audit surface =
     frozen file + shards (`cat raw/inbox/manifest.jsonl
     raw/inbox/manifest.d/*.jsonl`); a doc comment at the top of the frozen
     file records this AND the incomplete-op audit rule below.
  2. **Article frontmatter** — `source_ref` + sha256 added to the
     article's `raw_documents` (atomic temp-file + `os.replace`, house
     pattern). **Already-registered refuses in preflight, BEFORE
     consumption** (IADA I3 — no idempotent lane: a re-register attempt
     leaves the artifact unconsumed, so a wasted grant is impossible).
  3. **Rebuild** (as Replace/Remove do).
  4. **Ledger row LAST** — `ingest-ledger.jsonl` strict shape `register:
     {ts, operation, slug, source_path, sha256, authorized_by,
     authorization_sha256, result, rebuild}`, appended only after every
     other durable effect succeeded (append-last preflight-first, the Arc 1
     invariant — ops packet AC7). **Partial-failure semantics, stated:** a
     failure after step 1/2 leaves durable artifacts WITHOUT a ledger row —
     the ledger never claims an op that did not complete (false audit truth
     is the failure CFADA-FEUX-001 named); a shard without a matching
     ledger row is the detectable signature of an incomplete op, documented
     in the frozen-file doc comment. No rollback fabrication. (The ops
     ledger keeps its existing single-file mechanics — pre-existing
     posture, residual (d).)
- **Endpoint:** `POST /api/register` (form: slug, source_ref, note),
  gate order identical to replace/remove: authoring → artifact gate FIRST →
  quarantine → preflights → consume → write → optional rebuild.
- **First consumer (post-merge, not in this PR):** the pending
  TAI-RES-2026-006 row pinned in #50 (source_path, sha256, target_slug) is
  registered on the live server under a Michael-placed artifact; the PR
  ships machinery only. #52's supersession option becomes runnable
  afterwards; its accept-as-historical alternative stays Michael's.

### 2.6 R4/R5 — Honest-state styling

House-palette rules, both themes: `.deploy-foot` (muted footer line),
deploy blocked banner (warn accent, visible only when the script un-hides
it). `.wl-pending` keeps its EXISTING rule (`style.css:35`, dashed
underline + muted tint, distinct from live links and plain text, tooltip
retained) — R5 is the coverage guard, no restyling (R2-002): a named test
asserts every emitted honest-state class has rules in the built sheet,
which is also R4's regression net.
Playwright asserts computed visibility in both themes; a py test asserts
the classes exist in the built sheet (regrowth guard for the styling gap).

## 3. Acceptance criteria & named tests

| # | Criterion (risk) | Verification — named test |
|---|---|---|
| AC1 | Selector renders 3 modes, Add default, destructive forms hidden until selected + visually distinct, Q2 line present (med) | py: `test_ingest_page_mode_selector`; playwright: `ingest selector both themes` |
| AC2 | Destructive submit is IMPOSSIBLE without a preview rendered FOR THE CURRENT SELECTION; any selection change re-disarms AND resets the confirm; a stale/out-of-order preview response never arms (high) | py: `test_preview_gate_scaffold_fail_closed` (emitted HTML: destructive submit carries `disabled` at birth; the ONLY enable site in the inline JS is the preview-success handler, guarded by a per-request sequence token); dom-smoke with stubbed fetch: `ingest preview gate state machine` over the domain {preview ok → armed, selection change → disarmed + confirm reset, STALE response for a superseded selection arrives late → stays disarmed (sequence-token mismatch — CFADA-FEUX-002), confirm checked before preview → still disabled, fetch error/non-200/parse error → disabled + explicit notice} (IADA I5: behavior domain in the dom-smoke harness where fetch is stubbable; playwright keeps the static-render + themes pass) |
| AC3 | Preview endpoint is strictly read-only and parity-locked to op logic (high) | server: `test_preview_consumes_nothing` (artifact still valid + tree hash unchanged after preview), `test_preview_remove_parity_with_find_inbound_edges`, `test_preview_replace_surfaces_exact_refusal` |
| AC4 | Refusals render honestly: 403/422/400 bodies shown escaped, never swallowed; in-flight = explicit recompiling state (med) | py: `test_ingest_page_renders_refusal_states`; playwright: console-error-free refusal render |
| AC5 | Pending-edges chip: 0 → absent; N>0 → warn chip with N; corrupt edge-states → build refuses (never healthy) (med) | py: `test_freshness_pending_chip_domain` (0, N, corrupt fixture) |
| AC6 | `register` op: full deny domain — missing/expired/wrong-instance/wrong-operation artifact, missing file, retired target, ALREADY-REGISTERED source_ref, secret-bearing payload, corrupt ledger → refuse writing NOTHING with the artifact unconsumed; happy path writes in the §2.5 order (shard → frontmatter → rebuild → ledger LAST), consumes the artifact exactly once (high) | server/ops: `test_register_authorization_domain` (incl. already-registered pre-consumption refusal), `test_register_writes_are_atomic_and_audited` (incl. ledger-row-is-last: a forced post-shard failure leaves NO ledger row), `test_register_quarantine_refusal_redacts`, `test_register_manifest_shard_only_appends` (historical manifest.jsonl byte-identical after op) |
| AC7 | Manifest sharding closes the F9 class: Add + register never rewrite ANY existing manifest file — one immutable single-row shard per row (high) | ops: `test_manifest_shard_never_mutates_existing_files` (property: after N sequential ops, every previously-existing shard + the frozen file are byte-identical; shard filenames collision-free) |
| AC8 | R4/R5 classes styled in both themes; no unstyled emitted class remains (low) | py: `test_style_sheet_covers_emitted_state_classes`; playwright theme pass |
| AC9 | Full chain green; zero regression in the 80 ingest-ops + 18 server + arc/board suites (low) | `npm run verify` exit 0 at the reviewed head |

Gate satisfied-only-when: AC1–AC9 all green at the reviewed head AND
`npm run verify` exits 0. Any unproven criterion ⇒ not satisfied.

## 4. Fail-safe analysis (the §8 house rule, applied)

- Preview gate: the ONLY path to an armed destructive submit is
  preview-rendered-for-current-selection AND confirm-checked. Mechanism
  (CFADA-FEUX-002): every preview fetch carries a monotonically increasing
  sequence token bound to the selection at request time; a response whose
  token is not the CURRENT token is discarded (never rendered, never arms);
  any selection change bumps the token, disarms the submit, and unchecks
  the confirm. Every other state (no preview, stale response, fetch error,
  non-200, parse error, confirm unchecked) keeps it disabled — allowlist,
  proven by AC2 across the state domain including the out-of-order race.
- Register authorization: single fully-proven grant branch (exact-instance,
  in-window, unconsumed artifact + all preflights); every other path
  refuses before any write (AC6 domain table).
- Pending chip: renders only from the strict-parsed allowlist state
  `dangling-pending`; corrupt state cannot render because the build refuses
  upstream (existing gate, pinned by test).
- Manifest sharding: immutability of historical blobs is the invariant
  (AC7), so the allowlist model is never weakened — no new clearance logic,
  no auto-allowlisting, no scanner change.

## 5. Authorization packet

- **Bounded scope:** the §2.1 file plan, `transpara-ai/wiki` only, branch
  `feat/front-end-ux` off main @ `ca23a85`; lifecycle to ready PR; **no
  code before Human Design Review approves this packet (stage 6)**.
- **Forbidden:** any change to authorization artifact semantics beyond
  adding `register` to the operation allowlist; any change to secret-scan
  rules or allowlist logic; any client-side authorization handling (Q2);
  any write path in `/api/preview`; touching the engine boundary, refresh
  timer, arc view, board, or other repos; running the #50 first-consumer
  registration inside the PR; deciding #52's alternative.
- **Residual risks:** (a) the frozen manifest + shards split the audit
  surface across files — mitigated by the doc comment and the reader being
  human/audit-only today; named so a future programmatic reader designs for
  it. (b) preview truthfulness is parity-locked to op helpers but a future
  op change could add a lane preview doesn't know — mitigated by AC3 parity
  tests living beside the op tests. (c) `recompiling` state covers the
  synchronous request only; if ops ever go async the state machine needs a
  design pass (named non-goal today). (d) the ops ledger
  (`ingest-ledger.jsonl`) keeps its pre-existing single-file append posture;
  the F9 class fix here covers the manifest surface named in #50 — extending
  sharding to the ops ledger is a named follow-up decision, not silently
  in-scope.

## Appendix — IADA (self-directed, v0.1.0 → v0.2.0)

| # | Finding | Disposition |
|---|---|---|
| I1 | Preview endpoint would echo un-quarantined query params in refusal messages — the exact lane CFAR r20 closed on the mutation path, reopened on the read path | FIXED — §2.3 quarantines `{operation, slug, source_ref}` before any echoing validator; named test in AC3's scope |
| I2 | Month-sharded manifest files GROW, so their blobs change on every append — the design merely narrowed the F9 window instead of closing the class | FIXED — one immutable single-row shard file per row; every manifest blob immutable from birth; AC7 restated as the byte-identity property |
| I3 | R6 said frontmatter add is "idempotent" AND "re-run refuses" — contradictory; and a consumed artifact on a no-op would waste a human grant | FIXED — already-registered refuses in PREFLIGHT, before consumption; no idempotent lane |
| I4 | Q2's "UI never handles authorization" could be read as contradicting the existing authoring-token field | FIXED — §2.2 states the two-layer distinction explicitly (transport token stays; operation artifact never touches the client) |
| I5 | AC2's "no bypass path in inline JS — asserted structurally" from Python is not a real verification method; playwright can't drive /api/preview against the static test server | FIXED — behavior domain moved to dom-smoke with stubbed fetch (existing loadInflight pattern); py asserts disabled-at-birth + single enable site; playwright keeps static render + themes |
| I6 | `ingest-authorization.example.json` documents the operation rules but wasn't in the file plan — the operator-facing schema doc would silently lag | FIXED — file plan row added |
| I7 (recorded) | Ops ledger single-file growth carries the same F9 shape as the manifest but is pre-existing posture and #50 names only the manifest | CARRIED — residual (d), explicit follow-up decision |

IADA verdict at v0.2.0: **PASS — 0 design blockers**, assessor claude
(Fable 5), 2026-07-06. This IADA does not replace external CFADA; no code
before Human Design Review (stage 6) approves.

## Appendix — CFADA round 1 (Codex) → FAIL, repaired at v0.3.0

> `CFADA_FEUX_R1 FAIL blockers=1 majors=3 minors=2` at v0.2.0 blob
> `0a786bb3` (2026-07-06). Fidelities: coherence FAIL; packet-vs-FO PASS;
> FO-vs-source PASS (Q2/Q3 bindings honored).

| # | Finding | Disposition (v0.3.0) |
|---|---|---|
| 001 (blocker) | Register write order (manifest → ledger → frontmatter) could leave a completed ledger row without the article mutation — false audit truth | FIXED — §2.5 order restated: preflights (incl. appendability probe) → consume → shard → frontmatter → rebuild → **ledger LAST** (Arc 1 append-last invariant); partial-failure semantics stated (shard-without-row = detectable incomplete op); AC6 gains the ledger-row-is-last forced-failure test |
| 002 (major) | AC2's domain missed the stale/out-of-order preview-response race and the pre-checked-confirm lane the §4 claim relied on | FIXED — per-request sequence token bound to selection; stale responses discarded; selection change disarms + resets confirm; both lanes named in AC2's dom-smoke domain and §4 |
| 003 (major) | AC6 still said "idempotent frontmatter" after §2.5 dropped the idempotent lane — the same fix-instance-not-class failure the dead-keys arc hit | FIXED — AC6 reworded (already-registered = pre-consumption refusal); whole-packet sweep for the term confirms only the IADA/CFADA historical records retain it |
| 004 (major) | Shard filename collision safety asserted, not bound | FIXED — microsecond UTC stamp + `O_CREAT\|O_EXCL` exclusive create; existing path refuses; named in AC6/AC7 |
| 005 (minor) | Survey claimed `.wl-pending` unstyled; it is styled at `style.css:35` | FIXED — survey corrected here AND in the FO (v0.3.0): R5 narrows to the emitted-state-class coverage guard; file plan no longer restyles it |
| 006 (minor) | "/api/preview same posture as /api/articles" — false comparison (articles is host-gated only) | FIXED — §2.3 states preview is deliberately stricter (host + authoring), with the live-code cite |

## Appendix — CFADA round 2 (Codex) → FAIL, repaired at v0.3.1

> `CFADA_FEUX_R2 FAIL blockers=0 majors=2 minors=0` at v0.3.0 blob
> `c4f383ae` (2026-07-06). All six r1 findings verified repaired; two NEW
> incoherences introduced by the repairs themselves.

| # | Finding | Disposition (v0.3.1) |
|---|---|---|
| R2-001 | Packet still bound source-of-intent to FO v0.2.0 blob `7d32e332` after the FO bumped to v0.3.0 — stale truth-chain link | FIXED — packet bound to the FO's CURRENT bytes: v0.3.1 blob `8beb8079` (computed via `git hash-object` on the co-committed file, so binding and bytes land in the same commit — the stale-binding lane is closed by procedure, not by luck) |
| R2-002 | R5 repair incoherent across surfaces: §2.6 still promised marker-glyph restyling; FO §3 still claimed grep → 0 | FIXED — §2.6 restated guard-only; FO §3 corrected to grep → 1 with the misread recorded; third instance-not-class failure this session — repair procedure now REQUIRES a whole-corpus grep sweep for the changed fact before every commit (applied here) |
