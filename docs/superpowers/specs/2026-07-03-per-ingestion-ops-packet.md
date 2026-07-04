---
doc_id: TAI-WIKI-INGEST-OPS
title: Per-Ingestion Operations v1 — Deterministic Layer 1, Deny-by-Default Gate, Honest-Stale Engine Boundary (TLC Design Packet)
doc_type: design
version: 0.4.0
status: draft
canonical: false
created: 2026-07-03
updated: 2026-07-04
owner: Michael Saucier
steward: Claude (Fable 5)
authority: planning
tlc_stage: design
source_of_intent:
  - docs/superpowers/specs/2026-07-01-per-ingestion-operations-design.md (owner-brainstormed design, committed on main)
  - docs/superpowers/specs/2026-06-16-civilization-ontology-design.md §1.1/§1.6 (append-only substrate, revise = supersede)
intake_channel: A (owner-directed session 2026-07-01; program grant wiki-refactor-overnight-GO)
---

# Per-Ingestion Operations v1 — TLC Design Packet

> Turns the 2026-07-01 design spec ("Item 1": Add · Replace · Remove) into a
> buildable v1 contract against the live codebase (wiki main @ `d35cdd0`).
> **v1 = the full deterministic Layer 1, the deny-by-default authorization
> gate, and an engine boundary that degrades to honest-stale.** Nothing in v1
> depends on an LLM being reachable; everything an LLM would add is behind a
> gate that fails to a visibly-honest state.
>
> **Rebuild provenance.** This packet is a faithful rewrite of the v0.4.0
> packet whose branch was lost to a session teardown before first push
> (original CFADA history: r1 FAIL at `6b796bc` → repaired v0.3.0, r2 repairs
> → v0.4.0, r3 confirmation PASS at `e39bead`; OB markers
> `wiki-refactor-checkpoint-arc1-rebuild`, CFADA capture 2026-07-03). Those
> SHAs no longer resolve. All r1/r2 repairs are baked into this text
> (Appendix), and a fresh CFADA confirmation round runs at this head.

## 1. Survey — measured against live code

- `compile/ingest_server.py` (742 ln) serves `dist/` on loopback `:8787` with
  `POST /api/ingest` (Add) and `/api/rebuild`, both behind
  `require_allowed_host()` + `require_authoring()` (Host allowlist; token when
  `CIVWIKI_AUTHORING_TOKEN` is set, else loopback + same-origin). Writes go
  under `wiki_write_lock()` (flock on `compile/.wiki-write.lock`); rebuilds
  spawn `refresh.py` argv with a process-group kill on timeout. **Add today
  writes uploads to `raw/inbox/` and appends frontmatter with NO secret scan
  and NO ledger** — the commit-time scan fires only when a human later
  commits, but `dist/source/*.html` renders immediately.
- `compile/secret_scan.py` (663 ln) is the ratified fail-closed scanner:
  `scan_text()` (9 closed rule ids), input classes (§3.1: pathname, oversized
  > `MAX_BLOB_BYTES`, binary-NUL, text), `redact_spans()` so findings never
  echo secret bytes, strict-JSON allowlist parsing with
  `object_pairs_hook=_no_duplicate_keys`. The quarantine layer (§2.4) REUSES
  these primitives; it re-implements nothing.
- `compile/autodeploy.py` `authorized()` is the house deny-closed
  authorization shape this packet mirrors: exact artifact marker (`df`),
  required non-blank string fields, 40-hex/ISO validation, validity window,
  single fully-proven grant branch, every other path refuses with a reason.
  `compile/deploy-authorization.json` is git-ignored; an `.example.json` is
  committed.
- `compile/build_site.py` `to_html()` renders `[[wikilinks]]` two-state:
  `slug in SLUGS` → live `<a class="wl" href="slug.html">`, else `wl tbd`
  (non-live). **Two other link forms bypass this entirely and stay live:**
  markdown `[x](slug.html)` and raw inline-HTML `<a href="slug.html">` — both
  end up as plain hrefs that `sanitize_rendered_links()` passes (it checks URI
  *schemes* only). Markdown `extra` passes raw author HTML through, which is
  why the engine-output grammar (§2.6) forbids raw HTML outside fences.
- Authoring mutates tracked files in the serving clone already (browser Add
  appends to `wiki/<slug>.md`); the operator commits the authored state.
  `compile/ingest-ledger.jsonl` and `compile/edge-states.json` (both tracked)
  follow that same model. Only `compile/ingest-authorization.json` is
  git-ignored, exactly like `deploy-authorization.json`.
- Tests are stdlib scripts wired into `package.json` `test:py`
  (`compile/test_*.py`), asserting with plain `assert` + tempdir fixtures
  (`test_ingest_server.py`, `test_secret_scan.py` are the style anchors).

## 2. The contract

### 2.1 File plan

| Action | File | Notes |
|---|---|---|
| ADD | `compile/ingest_ops.py` | the whole v1 core: quarantine, authorization gate, ledger, edge-states, tombstones, replace/remove operations, engine boundary. Pure-logic functions take explicit paths/params (testable against tempdirs). |
| ADD | `compile/test_ingest_ops.py` | AC1–AC8, wired into `test:py` |
| ADD | `compile/ingest-authorization.example.json` | committed template, mirrors `deploy-authorization.example.json` |
| MODIFY | `compile/ingest_server.py` | `POST /api/replace`, `POST /api/remove` on the existing `require_allowed_host` + `require_authoring` path; Add (`handle_ingest`) gains quarantine + ledger |
| MODIFY | `compile/build_site.py` | three-state link rendering for ALL link forms (§2.7); retired articles drop from nav but stay reachable; stale/retired banner line on article pages |
| MODIFY | `package.json` | `test:py` gains `python3 compile/test_ingest_ops.py` |
| MODIFY | `.gitignore` | `compile/ingest-authorization.json` |

Out of v1 (explicit): `ingest.html` UI for the new operations (API-first;
curl is the v1 surface), Layer-2 per-edge reconciliation runs (§2.8 queue is
the durable work list), full-corpus recompile, EventGraph store, offline
model tier. The 15-minute refresh timer's behavior is untouched.

### 2.2 Operation model (from the ratified design, unchanged)

Per-ingestion operation mode `add | replace | remove` — never a stored
policy; no scheduler ever acts destructively. Every operation is append-only
supersession over the Event substrate: no `rm`, no in-place overwrite of
authoritative raw; tombstones, never deletes. Prime invariant: **maximum
referential integrity at all times** — integrity is what the graph *claims*;
a visibly-pending edge is honest, a live link resolving to nothing is the
thing forbidden.

### 2.3 The authorization gate — `compile/ingest-authorization.json` (deny-by-default, exact schema)

Loaded and validated on EVERY Replace/Remove request. Grant is the single
fully-proven branch; every other path refuses the operation with a reason and
**nothing written**. Add requires no authorization artifact (additive-only)
— it keeps the authoring-surface gates it has today.

Exact schema — key set must be exactly these seven keys (unknown keys
refuse; duplicate keys refuse via `object_pairs_hook`; wrong type of the
top-level document refuses):

```json
{
  "df": "ingest-authorization",
  "operations": {"replace": true, "remove": false},
  "authority": "name / role of the human authorizing",
  "authorized_at": "2026-07-04T00:00:00Z",
  "expires_at": "2026-07-11T00:00:00Z",
  "reason": "one-line note: why these operations are cleared",
  "engine_command": ["claude", "-p"],
  "engine_timeout_seconds": 300
}
```

Field law (each violation → refuse):
- `df` must equal `"ingest-authorization"` exactly.
- `operations` must be an object with EXACTLY the keys `replace` and
  `remove`, each a JSON boolean (`isinstance(v, bool)` — truthiness never
  grants). The requested operation's value must be exactly `true`.
- `authority`, `reason` non-empty strings; `authorized_at`/`expires_at`
  ISO-8601; grant only while `authorized_at <= now < expires_at`.
- `engine_command` must be a JSON array. `[]` means **engine disabled**
  (deterministic-only mode; Replace completes honest-stale). If non-empty,
  every element must be a non-empty string. It is executed as an **argv
  vector, never through a shell**.
- `engine_timeout_seconds` must be an int (bool explicitly rejected) with
  `1 <= v <= 3600`.
- File missing, unreadable, non-JSON, non-object → refuse. There is no
  `default:`/`else` that grants.

### 2.4 Quarantine — every byte scanned before any write

`compile/ingest_ops.py` exposes two functions built on `secret_scan`:

- **`quarantine_payload(data: bytes) -> refusal | None`** — classifies an
  in-memory payload by the scanner's input classes *before it exists on
  disk*: larger than `secret_scan.MAX_BLOB_BYTES` → refuse (oversized,
  unscannable at runtime — there is no runtime attestation path); contains
  NUL → refuse (binary, unscannable); otherwise decode
  (`utf-8`, `replace`) and `scan_text()` — any finding refuses.
- **`quarantine_fields(fields: dict[str, str]) -> refusal | None`** — runs
  `scan_text()` over EVERY string that will be persisted anywhere (slug,
  note, reason, source_ref, original filename, actor, authority — the caller
  passes the complete set; the function scans every value it is given).

Law:
- Quarantine runs **before any write** — nothing lands in `raw/`, `wiki/`,
  the ledger, or edge-states on refusal, and no rebuild is triggered.
- **Engine output is quarantined too** (§2.6): `quarantine_payload` over the
  produced article bytes plus the engine grammar check, before the atomic
  swap. A synthesis that embeds a credential is refused the same as an
  upload.
- There is **no allowlist clearance at quarantine time** — findings refuse,
  period. The ratified-fingerprint story lives at commit time
  (`.secretsallow`); the runtime surface takes no attestations.
- Refusal messages report rule id / redacted context only
  (`redact_spans`) — matched secret bytes are never echoed to the HTTP
  response, ledger, or logs.
- Add gains the same quarantine: every upload payload and every persisted
  form field is scanned before `save_uploads()` writes anything.

### 2.5 Replace — `POST /api/replace` `{slug, source_ref, upload}`

Request (multipart): `slug` (existing article), `source_ref` (the EXACT raw
source reference in that article's frontmatter to supersede), one `document`
upload (the replacement), optional `note`.

Order of operations (each step refuses → stop, nothing written):
1. Authoring-surface gates (identical to `/api/ingest`): allowed Host +
   `require_authoring`.
2. Authorization gate §2.3 with `operations.replace`.
3. Quarantine: `quarantine_fields({slug, source_ref, note, filename})`,
   `quarantine_payload(upload bytes)`.
4. Preflight (deterministic, read-only):
   - `slug` matches `SLUG_RE` and `wiki/<slug>.md` exists and is not retired;
   - `source_ref` is listed in that article's `sources`/`raw_documents`;
   - `source_ref` is a local `raw/` path. **URL sources are refused in v1**
     (`replace of an external URL source is not supported in v1`);
   - `source_ref` is not referenced by any OTHER article (**shared sources
     are refused in v1** — the multi-article recompile fan-out is exactly
     the economy/integrity trade the owner deferred; refusing is the only
     fail-safe v1 answer);
   - ledger preflight §2.9 (existing ledger must parse strictly).
5. Deterministic swap (Layer 1, under `wiki_write_lock`): save the new
   upload under `raw/inbox/<date>/<slug>/` (same naming as Add); rewrite
   the article file **frontmatter only** via temp-file + `os.replace` in the
   same directory: `source_ref` annotated superseded (`# superseded
   <date> by <new-ref>` comment retained in place — the old raw file is
   NEVER deleted), new ref appended to `sources` + `raw_documents`,
   `stale_since: "<ISO>"` set. **Body bytes are untouched by Layer 1.**
6. Engine boundary §2.6 (may be disabled/fail → article stays at step-5
   state: honest-stale).
7. Rebuild (`run_refresh_unlocked`, lock already held).
8. Ledger append §2.9 — the LAST mutation.

### 2.6 The engine boundary (authority-gated, atomic, degrades to honest-stale)

- Invocation: `subprocess` with the `engine_command` argv exactly as
  authorized (never `shell=True`), job JSON on stdin
  (`{"operation": "replace", "slug", "raw_documents", "sources"}`), complete
  replacement article markdown expected on stdout,
  `engine_timeout_seconds` enforced with process-group kill (the
  `run_refresh_unlocked` pattern).
- Output law — ALL must hold or the output is discarded:
  - non-zero exit, timeout, empty/whitespace stdout → discard;
  - output must parse as frontmatter + body (`split_fm` finds a block);
  - **no raw HTML outside fenced code blocks** (markdown `extra` passes raw
    HTML through to the rendered page — this grammar rule is the injection
    gate). Inline/backtick code spans do not count as fences;
  - `quarantine_payload(output bytes)` clean;
  - frontmatter must keep `entity` and drop `stale_since`.
- On success: the whole article file (frontmatter + body) is replaced via
  temp-file + `os.replace` (atomic; no reader ever sees a partial write).
- On ANY failure: **the article file's bytes are exactly the step-5
  deterministic state** — updated frontmatter with `stale_since`, body
  untouched. The banner renders the stale notice from `stale_since`. Never
  fabricate; never fail open; never partial-write.
- `engine_command: []` → the boundary is skipped entirely and the ledger
  records `"engine": "disabled"`; the article is honest-stale by
  construction.

### 2.7 Remove — `POST /api/remove` `{slug, reason}` and the edge-state law

Order: authoring gates → authorization (`operations.remove`) →
`quarantine_fields({slug, reason})` → preflight (slug exists, not already
retired, not `index`; ledger preflight) → Layer 1 under the lock →
rebuild → ledger append last.

Layer 1 (deterministic, atomic per file):
1. Rewrite `wiki/<slug>.md` as a **retired tombstone stub** via temp-file +
   `os.replace`: frontmatter keeps `entity`/`aliases` and gains
   `retired_on: "<YYYY-MM-DD>"`, `retired_reason: "<reason>"`; the body
   becomes the legible stub (`retired on DATE · reason`). The file is never
   deleted; raw sources are never deleted.
2. Enumerate EVERY inbound edge by scanning all `wiki/*.md` bodies for all
   three link forms targeting the slug (§2.7-forms): `[[slug]]` /
   `[[slug|alias]]`, markdown `[x](slug.html)`, raw `href="slug.html"`.
3. Write each inbound edge into `compile/edge-states.json` as
   `dangling-pending`, `queued: true`, `enqueued_at: now`.

**`compile/edge-states.json` exact schema** (tracked; committed truth — the
closure rule is testable from the repo alone, no git-ignored side queue):

```json
{
  "some-article->removed-topic": {
    "state": "dangling-pending",
    "since": "2026-07-04T09:00:00Z",
    "reason": "target retired: <reason>",
    "queued": true,
    "enqueued_at": "2026-07-04T09:00:00Z"
  }
}
```

- Key is `"<source-slug>-><target-slug>"`. `state` is the CLOSED vocabulary
  `valid | cleanly-removed | dangling-pending`. `since`/`reason` required.
  `queued` is a JSON bool; `queued: true` requires `enqueued_at` ISO string,
  `queued: false` requires `enqueued_at: null`. Exact key set per entry.
- **Closure invariant (tested, AC5):** after any Remove completes, there are
  ZERO entries with `state == "dangling-pending"` and `queued == false`.
  Every pending edge is on the committed work list. v1 enqueues all inbound
  edges; the queue drains through later authorized recompiles (Layer 2 runs
  are out of v1). A queued pending edge renders as pending — integrity holds
  the whole time.

**Rendering law (constitutional, fail-closed, ALL link forms):** a link to
an internal target renders LIVE only on the single proven branch:
*target exists AND target is not retired AND (no edge-state entry OR entry
state is exactly `valid`)*. Every other combination — retired target,
`dangling-pending`, `cleanly-removed` rendered as plain text, **any
unknown/future state value**, missing target — renders NON-live (`wl
tbd` for missing, `wl-pending` marker `<span class="wl wl-pending"
title="pending reconciliation">label</span>` for retired/dangling/unknown).
There is no fall-through that renders live. This applies uniformly to:
1. `[[slug]]` wikilinks — the third state added to `to_html()`'s `emit()`;
2. markdown `[x](slug.html)` links;
3. raw author-HTML `href="slug.html"` —
forms 2 and 3 are both plain hrefs after markdown conversion, gated in one
place by extending `sanitize_rendered_links()` (which already visits every
`href`) with the internal-target state check. Retired articles drop from the
nav but remain reachable (retired ≠ discoverable; never a 404); article
pages carry a banner line when `stale_since` or `retired_on` is set.

### 2.8 Add — gains quarantine + ledger (behavior otherwise unchanged)

`handle_ingest` calls `quarantine_fields({target_slug, note, supersedes,
external_urls, filenames})` and `quarantine_payload` per upload BEFORE
`save_uploads()`; on refusal nothing is saved, no manifest row, no rebuild,
HTTP 422 with redacted reason. After a successful Add, one ledger row
(`operation: "add"`) is appended. No authorization artifact required.

### 2.9 The ledger — `compile/ingest-ledger.jsonl` (strict JSONL, preflight-first, append-last)

- **Strict JSONL**: every line is a JSON object parsed with
  `object_pairs_hook` refusing duplicate keys; exact per-operation key sets
  (below); unknown `operation` → invalid line.
- **Preflight-first**: before ANY mutation, the existing ledger (if present)
  must parse strictly end-to-end. A corrupt/unparseable line → the operation
  is REFUSED (fail closed — an unauditable surface takes no new actions)
  until a human repairs the ledger.
- **Append-last**: the row is appended (single `write` of one line under the
  held lock) only after every other write of the operation succeeded. A
  refused operation appends nothing. Absent file = empty ledger (valid).
- Exact shapes (`ts` ISO-8601 UTC; all strings non-empty):
  - add: `{"ts", "operation": "add", "slug", "sources": [str], "created": bool}`
  - replace: `{"ts", "operation": "replace", "slug", "superseded": str,
    "replacement": str, "authorized_by": str, "engine":
    "ok"|"failed"|"disabled", "result": "completed"|"stale"}`
    (`result` is `"completed"` iff `engine == "ok"`)
  - remove: `{"ts", "operation": "remove", "slug", "reason": str,
    "authorized_by": str, "affected_edges": [str], "result": "completed"}`

## 3. Acceptance criteria — named tests in `compile/test_ingest_ops.py`

| AC | Law under test | Named test(s) |
|---|---|---|
| AC1 | Authorization gate refuses across the ENTIRE input domain — missing/unreadable/non-object file, wrong `df`, unknown key, duplicate key, `operations` wrong shape (missing/extra key, non-bool incl. truthy 1/"true"), op `false`, bad/blank strings, bad/expired/future window, `engine_command` non-list / non-string / empty-string element, `engine_timeout_seconds` bool/non-int/0/3601 — and grants ONLY the single fully-proven shape | `test_ac1_authorization_denies_entire_domain`, `test_ac1_authorization_single_proven_grant` |
| AC2 | Quarantine refuses oversized/binary/secret-bearing payloads and a planted secret in EVERY persisted field; refusal writes nothing anywhere; refusal output never contains the secret bytes | `test_ac2_quarantine_payload_input_classes`, `test_ac2_quarantine_every_persisted_field`, `test_ac2_refusal_writes_nothing_and_redacts` |
| AC3 | Replace deterministic swap: new raw saved, old ref superseded-annotated (file retained), frontmatter atomically updated, `stale_since` set, body bytes untouched; refusals (unknown slug, ref not in article, URL ref, shared ref, retired slug) write nothing | `test_ac3_replace_deterministic_swap`, `test_ac3_replace_refusals_write_nothing` |
| AC4 | Engine boundary: `[]` → disabled+stale; nonzero exit / timeout / empty stdout / no frontmatter / raw HTML outside fences / secret in output → article bytes IDENTICAL to post-swap state, `engine: "failed"`, `result: "stale"`; success replaces atomically, drops `stale_since`; argv exec, never shell | `test_ac4_engine_failure_domain_leaves_honest_stale`, `test_ac4_engine_success_atomic_swap`, `test_ac4_engine_argv_never_shell` |
| AC5 | Remove: tombstone stub written (never deletes files), all inbound edges across ALL THREE link forms discovered → `dangling-pending` queued; **closure: zero unqueued dangling-pending entries**; refusals write nothing | `test_ac5_remove_tombstone_and_edge_enumeration`, `test_ac5_closure_zero_unqueued_pending`, `test_ac5_remove_refusals_write_nothing` |
| AC6 | Rendering fail-closed over the whole edge-state domain: `valid` live; `cleanly-removed` plain text; `dangling-pending` pending marker; UNKNOWN state non-live; retired target non-live even with no entry; missing target `tbd`; live renders ONLY on the proven branch — for `[[slug]]`, `[x](slug.html)`, and raw href forms | `test_ac6_render_state_domain_all_link_forms` |
| AC7 | Ledger: strict JSONL, exact per-op shapes, duplicate-key line invalid; corrupt existing line → operation refused, nothing written; append is last (failed op appends nothing); Add appends an add row | `test_ac7_ledger_strict_jsonl_preflight_first_append_last` |
| AC8 | Endpoint parity: `/api/replace` + `/api/remove` behind the SAME Host + authoring gates as `/api/ingest` (token/loopback/same-origin matrix), plus the authorization gate; Add path now quarantines and ledgers | `test_ac8_endpoint_authoring_parity` |

## 4. Fail-safe analysis (CLAUDE.md doctrine, proven over the input space)

Every gate in this packet is an allowlist with a refusing fall-through:
authorization grants one proven shape (AC1 walks the domain); rendering has
one live branch (AC6 walks the states incl. unknown); the engine's output
has one acceptance conjunction (AC4 walks the failure modes); quarantine
refuses every non-clean class (AC2); the ledger refuses to act when it
cannot audit (AC7). Cost asymmetry: a wrongly-refused ingest stalls one
visible operation; a wrongly-permitted one writes a secret to a served page
or renders a lying link. Always pay the safe side.

### 4.4 ADR determination

No standalone ADR: the architectural decisions (append-only supersession,
two-layer integrity, one-click authority) were ratified in the 2026-07-01
design spec already on main; this packet only binds them to an exact v1
contract. Contribution = pattern-only (deny-by-default artifact gate reused
from autodeploy; quarantine reuses secret_scan primitives).

## Appendix — CFADA history baked into this text

**r1 (Codex, FAIL at lost head `6b796bc`, v0.2.0) → repaired:** AC7/8
authoring-gate wording now mirrors the LIVE gate matrix (token OR
loopback+same-origin — §2.5/§3 AC8); quarantine covers **Add** and is a
reusable in-memory classifier over secret_scan's input classes (§2.4, §2.8);
authorization schema is complete/exact and actually mirrors
deploy-authorization (§2.3); wl-pending rendering covers **all** link forms,
not only wikilinks (§2.7); closure is canonical/testable because the queue
lives in committed `edge-states.json` (`queued`/`enqueued_at`), no
git-ignored side file (§2.7). Majors: Layer-1-frontmatter vs engine-body
write separation + temp-file/`os.replace` atomicity stated exactly
(§2.5-5, §2.6); ledger got exact JSONL/dup-key/append rules (§2.9). Minor:
no cross-reference to unstated behavior remains.

**r2 (Codex) → repaired at v0.4.0:** Replace targets an explicit
`source_ref` with **URL and shared sources refused in v1** (§2.5-4);
`quarantine_fields` spans EVERY persisted metadata string AND engine output
is quarantined (§2.4, §2.6); ledger field shapes exact per operation (§2.9);
engine grammar: **no raw HTML outside fences** (§2.6); edge-state schema and
v1 scope aligned with the queued fields (§2.7).

**r3 (Codex, PASS at lost head `e39bead`):** fresh blocker-bar sweep found
no blockers; that confirmation is re-run at this rebuilt head before build.
