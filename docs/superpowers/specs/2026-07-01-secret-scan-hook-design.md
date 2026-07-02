---
doc_id: TAI-WIKI-SECRET-SCAN-HOOK
title: Secret-Scan Pre-Commit Hook + CI Gate — Design Packet
doc_type: design
version: 0.6.1
status: draft
canonical: false
created: 2026-07-01
updated: 2026-07-02
owner: Michael Saucier
steward: Claude (Opus 4.8)
authority: planning
tlc_stage: design
source_of_intent:
  - DESIGN.md §Ingestion — "Secret-scrub before any commit … nothing with live secrets is committed. Non-negotiable." (in-repo, durable)
  - PROVENANCE.md — records the corpus's config-laden sources (in-repo, durable)
  - operator directive 2026-07-01 (build order: hook first) + Item-3 tooling memo on branch feat/wiki-improvement-specs (out-of-branch; cited as intent only, not a canonical repo record)
intake_channel: A (human request)
---

# Secret-Scan Pre-Commit Hook + CI Gate — Design Packet

> **TLC design packet. Authorizes nothing.** No code until an External-Committee
> AuthorityDecision is recorded for the bounded scope in §7. Test-first: the
> AcceptanceCriteria and TestCases below are written before implementation.

## 1. Problem

The wiki ingests raw source material (`raw/inbox/`, browser-ingested drops) that
can carry secrets, and `PROVENANCE.md` records config-laden sources in the corpus.
Confirmed 2026-07-01: there is **no secret scan in `ci.yml` or in a pre-commit
hook** (`core.hooksPath` unset; only sample hooks). The secret-scrub is a
non-negotiable in `DESIGN.md` (§Ingestion — *"nothing with live secrets is
committed. Non-negotiable"*); the in-repo authority is DESIGN.md. This is a live
doctrine hole; the hook closes it.

## 2. Requirements

- **R1** — a pre-commit hook blocks committing detected secrets (fail-closed).
- **R2** — a CI job enforces the same scan on PRs (defense-in-depth; local hooks are bypassable with `--no-verify`).
- **R3** — offline / air-gap: no network, no per-platform binary vendoring friction.
- **R4** — fail-closed on scanner error, absence, timeout, git error, or ambiguous result.
- **R5** — an auditable, **fail-closed** allowlist for false positives (no blanket path disable).
- **R6** — the scanner and its config contain no secrets themselves.

## 3. Approach (recommended)

A **pure-Python stdlib secret scanner** (`compile/secret_scan.py`), zero-dependency
and air-gap-native, matching the repo's stdlib-Python + "no pytest, air-gap
friendly" pattern. It runs in two explicit **modes** and is wired to two surfaces:

- **`--staged`** — scans the staged index; used by the git hook `.githooks/pre-commit` (installed via `git config core.hooksPath .githooks`, documented in a one-line setup step + README), so the hook is shared and reviewable, not a private `.git/hooks` file.
- **`--changed-against <base>`** — scans **every (path, blob) occurrence introduced anywhere in the PR's commit history**, not just the final diff; used by **CI**. CI has no staged index, so it never assumes one. Exact git semantics (CFADA-r2 B1, r3 B1/B3/B6):
  - **Base ref, per trigger event (CFADA-r4 M2 — the required `Build & Test` job runs on both `pull_request` and `push`)**: on **`pull_request`** events CI passes the PR base explicitly (`origin/${{ github.base_ref }}`); the scan domain is `merge-base(<base>, HEAD) .. HEAD` — this is the **preventive** gate. On **`push`** events (`main`) the base is `${{ github.event.before }}`; if it is all-zeros or unresolvable ⇒ **block** (AC9). The push-path scan is **detective, not preventive** (the push has already landed; a red required check on `main` is the loud alarm) — stated honestly, with the admin direct-push residual named in §7(f).
  - **Occurrence enumeration**: for **every commit** in that range, `git diff-tree -r -m --no-renames <commit>` — `-m` diffs **merge commits against each parent**, so content introduced by a merge or conflict resolution is enumerated too (CFADA-r3 B1; named test `test_secret_in_merge_commit_blocked`); rename detection **off**. The scan/report unit is the **`(canonical_path, blob_sha256)` occurrence** — identical blob content at two paths is two findings, each needing its own §3.1 clearance; blob-level dedup is permitted only as an internal scanning optimization, never for finding identity or allowlist evaluation (CFADA-r3 B3). A secret committed then removed before the final diff is still caught (named test `test_secret_added_then_removed_in_history_blocked`).
  - **Non-blob entries deny by default (CFADA-r3 B6)**: a gitlink (mode `160000` submodule pointer) or any `.gitmodules` change ⇒ **block** — submodule content is not scannable by this design and is **not permitted** in this repo's scan domain (no clearance lane in v1; named tests `test_gitlink_blocks` + `test_gitmodules_change_blocks`, §5). Symlink entries (mode `120000`) are scanned as text (their blob is the target path).
  - **Fetch requirement**: the CI checkout uses `fetch-depth: 0`. If the base ref, the merge-base, or any enumerated blob is unresolvable (shallow clone, missing ref, failed `cat-file`) ⇒ **block** (AC9), never a reduced-domain scan.
  - **Enforcement wiring (CFADA-r3 B2, CFAR F3/F4)**: the scan runs as a **step inside the existing required `Build & Test` job** in `.github/workflows/ci.yml` — verified live 2026-07-02: `main` protection requires exactly `Build & Test` + `cross-family-adversarial-review`, so a *separate* job would not be a required check and could not block a merge. No branch-protection/settings change is needed or authorized (§7). The step executes a **scanner copy extracted from the trusted base ref** (`git show "$BASE":compile/secret_scan.py`), never the PR head's copy — a PR editing `secret_scan.py` must not be able to neuter the gate that scans it (bootstrap fallback to the head copy only when the base predates the scanner, i.e. before the introducing PR merges). The step runs **before any dependency install** (`pip install`, `npm ci`) so no untrusted install-time code executes ahead of the gate — the scanner is stdlib-only and needs no installs.

Both modes **fail closed on any `git` subprocess error** (a failed `diff`/`cat-file` ⇒ block, never pass) **and on timeout** (CFADA-r4 B2): the scanner enforces its own **in-process `--max-seconds` bound** (portable — the hook must not depend on the non-portable coreutils `timeout` binary, which would falsely block every commit on macOS/BSD clones; CFAR F5), and any abnormal termination is a **block**, never a pass (named test `test_scanner_timeout_fails_closed`; in CI, `timeout-minutes` on the step additionally makes a hang fail the required job by Actions semantics). The scanner reads a **fail-closed allowlist** (§3.1: text `fingerprint` + binary/oversized `blob_review`). **Outcome vocabulary is closed and enumerated**: every scanned `(canonical_path, blob_sha256)` occurrence resolves to exactly `pass` (scanned clean), `allowlisted` (cleared by a valid §3.1 entry of the applicable type), or `block`. There is **no `skip` outcome** anywhere in the scanner (CFADA-r2 B3 removed the last one); any input the scanner cannot positively scan is `block`.

**Alternative considered — vendoring the `gitleaks` binary:** a more battle-tested
ruleset, but it is not installed and needs per-platform air-gap vendoring. Deferred
as a future *complement*, not the primary. This scanner is an explicit **minimum
guard (§3.2), not a gitleaks-equivalent.** (Reverses the Item-3 memo's initial
gitleaks lean on the finding that gitleaks is absent and the repo is stdlib-Python.)

### 3.1 Allowlist model (fail-closed — no ignore lanes, no skip outcome)

Per CFADA-r1 C3, CFADA-r2 B2/B3/M1, CFADA-r3 B4, and CFADA-r4 B1, there are
**no blanket path ignores for tracked text** and **no skip outcome for any
input class**. Every enumerated occurrence is first assigned to exactly one
**input class by provable properties**, and each class has exactly one
clearance lane:

| Input class (decided in this order) | Definition (provable) | Outcome / clearance lane |
|---|---|---|
| **unreadable / unresolvable** | `cat-file` fails, object missing, hash unobtainable, any git error | **block — non-clearable** (AC9; nothing that cannot be read and hashed can ever be cleared; named test `test_unreadable_blob_non_clearable`) |
| **oversized** | readable, > 1 MiB (text **or** binary — size is checked before content) | **block**, clearable only by `blob_review` |
| **binary** | readable, ≤ 1 MiB, null byte detected | **block**, clearable only by `blob_review` |
| **scannable text** | readable, ≤ 1 MiB, no null byte → **text-scanned** | findings clearable only by per-finding `fingerprint`; `blob_review` is **rejected** for this class |

The governing principle (CFADA-r4 B1): **an attestation may never override a
performed scan** — `blob_review` exists only for readable content the scanner
**could not text-scan** (binary or oversized), and nothing unreadable is ever
clearable by anything. `compile/.secretsallow` holds exactly **two record types
with honestly distinct scopes**:

- **`fingerprint` (scannable-text findings only)**: clears one false positive. Key: `rule_id + canonical_path + blob_sha256 + match_sha256 + byte_offset` where `match_sha256` is the SHA-256 of the **exact matched byte span** (CFADA-r2 B2) and `byte_offset` is the match's **start offset within the blob** (CFADA-r5 B1 — offsets are stable because the entry pins the immutable blob SHA). One entry clears **exactly one occurrence of one finding**: a sibling finding of the *same rule in the same blob* — including the **identical matched bytes appearing at a second offset** — **stays blocking** (named tests `test_allowlist_entry_does_not_cover_sibling_findings`, `test_duplicate_identical_matches_need_separate_entries`); the same blob at a **different path** is a different occurrence and stays blocking (CFADA-r3 B3). Because the entry pins the blob SHA, **editing the file re-flags everything**.
- **`blob_review` (binary/oversized classes only — explicitly blob-scoped, CFADA-r3 B4)**: a human attestation *"I reviewed this exact blob at this path in full and it contains no secrets"*. Key: `canonical_path + blob_sha256`. It is **not** a per-finding fingerprint and the design does not pretend it is: its scope is the entire attested blob, which is precisely what the reviewer attests to. It is **rejected** for the scannable-text class (a text-scanned blob's findings can only be cleared finding-by-finding; named test `test_blob_review_rejected_for_text_blobs`) and can never clear the unreadable class. Any content change re-blocks (new blob SHA).
- **Allowlist governance (CFADA-r2 M1)**: **both** record types additionally require `reason + owner + reviewed_by + reviewed_on + expires_on` (ISO dates; max validity 180 days, renewable only by re-review). The scanner **validates the schema on every run**: a malformed, incomplete, unknown-type, or **expired** entry ⇒ the scan **blocks** with an allowlist-validation error (an entry that cannot be proven valid clears nothing *and* is never silently dropped; named test `test_allowlist_schema_and_expiry_enforced`, AC10).
- **Binary blobs** (null-byte detected) **block by default** (CFADA-r2 B3): binary content cannot be positively text-scanned, and a reasoned skip is a fail-open lane. Message: *"binary content cannot be text-scanned — review manually and attest with a blob_review entry"*. The scanner still pattern-scans binary bytes and **reports** what it finds as reviewer evidence, but the report is advisory — without a valid `blob_review` entry the outcome is `block` regardless.
- **Oversized blobs** (> 1 MiB) **block**: "too large to scan — review manually and attest with a blob_review entry".
- Generated files (e.g. `package-lock.json`) **are scanned**; a real false positive there is cleared by fingerprint, not by ignoring the path.
- The **entropy heuristic is conservative** (min length + high threshold, defined in §3.2) and always subordinate to the explicit pattern rules — patterns are the primary signal, entropy is a backstop.
- **CI is the enforcement of record**; the local hook is fast feedback. A contributor who has not run the hooks-setup is still gated by CI.

#### 3.1.1 `.secretsallow` concrete grammar & identity normalization (CFADA-r6 M1)

- **File syntax**: UTF-8 **JSON Lines** — one JSON object per non-empty line, parsed with stdlib `json`. Empty lines are permitted; **any other line that does not parse to an object of a known `type` ⇒ allowlist-validation error ⇒ block** (AC10). JSON has no comments; none are allowed.
- **Record shapes** (exact keys, no extras — an unknown or missing key ⇒ validation error):
  - `{"type":"fingerprint","rule_id":…,"canonical_path":…,"blob_sha256":…,"match_sha256":…,"byte_offset":…,"reason":…,"owner":…,"reviewed_by":…,"reviewed_on":…,"expires_on":…}`
  - `{"type":"blob_review","canonical_path":…,"blob_sha256":…,"reason":…,"owner":…,"reviewed_by":…,"reviewed_on":…,"expires_on":…}`
- **`canonical_path`**: the path exactly as git emits it with `-z` (raw, unquoted), decoded UTF-8 **strict** — a path that fails strict decoding ⇒ block; repo-root-relative, POSIX separators, no leading `./`.
- **Span convention** (deterministic across platforms): matching runs over `scan_text = blob_bytes.decode("utf-8", errors="replace")`; for a match at character span `[start, end)`, `match_sha256 = sha256(scan_text[start:end].encode("utf-8"))` and `byte_offset = len(scan_text[:start].encode("utf-8"))`.
- **Composite/predicate rules report one defined span each**: `gcp-sa-json` → the span of the `"private_key"\s*:\s*"` match (one finding per blob); `generic-assignment` and `high-entropy` → the span of the **candidate token**, not the key prefix.
- **Duplicate identity** (two records with the same full identity key) ⇒ validation error ⇒ block — duplicates are never silently tolerated.
- **Dates**: ISO-8601 `YYYY-MM-DD`, compared in UTC; `expires_on` earlier than the current UTC date ⇒ expired ⇒ block; **`reviewed_on` later than the current date ⇒ block** (CFAR F1: a future review date would extend the 180-day window arbitrarily far from today) (AC10).
- **Snapshot rule (CFAR F2)**: the allowlist is read from the **snapshot being scanned, never the working tree** — `--staged` reads the **index** copy (the review record must travel with the commit it clears), `--changed-against` reads `HEAD`'s copy, `--tree <rev>` reads `<rev>`'s copy. Absent from the snapshot = empty allowlist; a git error while reading ⇒ block. Named test `test_allowlist_snapshot_matches_scan_mode`.

### 3.2 Detector contract — minimum ruleset (test-first, concrete grammars)

Per CFADA-r1 C4 and CFADA-r2 B4, each detector is a **concrete anchored
grammar**, not a sketch; rule names claim **exactly** what the grammar covers,
nothing more. This is a **minimum guard, not gitleaks-equivalent**; it is
extensible.

**Normalization (applies to every rule):** blob bytes are decoded UTF-8 with
`errors="replace"` and scanned as one string; single-line rules also anchor on
`\b` word boundaries; multi-line rules (`private-key`, `gcp-sa-json`) match
across lines. JSON-shaped rules use **whitespace-tolerant** regexes (`\s*`
around `:`), never exact-fragment matching.

**Exact grammars (Python `re`, verbatim — this fenced block is the authoritative
contract; CFADA-r3 B5 moved it out of the markdown table, whose `\|` cell
escaping corrupted alternations):**

```text
private-key         -----BEGIN [A-Z ]*PRIVATE KEY( BLOCK)?-----
                    (re.MULTILINE; matches anywhere in the blob)
aws-access-key-id   \b(AKIA|ASIA)[0-9A-Z]{16}\b
github-token        \bgh[pousr]_[A-Za-z0-9]{36,255}\b
github-token        \bgithub_pat_[A-Za-z0-9_]{22,255}\b
slack-token         \bxox[baprs]-[A-Za-z0-9-]{10,}\b
openai-sk-key       \bsk-(proj-|svcacct-|admin-)?[A-Za-z0-9_-]{20,}\b
gcp-sa-json         "type"\s*:\s*"service_account"
                    AND (same blob)  "private_key"\s*:\s*"
jwt                 \beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b
generic-assignment  (?i)\b(api[_-]?key|secret|token|passwd|password)\b\s*[:=]\s*["']?
                    THEN candidate predicate on the following token:
                    len >= 16, charset [A-Za-z0-9+/=_-], Shannon entropy >= 3.5 bits/char,
                    not a placeholder (empty, <...>, $VAR, {{...}}, changeme, example, xxx...)
high-entropy        candidate token [A-Za-z0-9+/=_-]{32,} not matched by any rule above,
                    Shannon entropy >= 4.5 bits/char
```

A rule with two lines (`github-token`) is the union of both regexes under one
`rule_id`. `gcp-sa-json` fires only when **both** regexes match the same blob.

| Rule id | Positive fixture (runtime-generated **from the grammar above**) | Negative (stated near-miss) |
|---|---|---|
| `private-key` | generated PEM header + base64 body | prose containing "private key" (no armor) |
| `aws-access-key-id` | `"AKIA"` + 16 chars from `[0-9A-Z]` | 20-char uppercase word failing the prefix |
| `github-token` | one classic + one fine-grained, generated per branch | `ghp_short`, bare `github_pat` in prose |
| `slack-token` | `"xoxb-"` + 24 valid chars | `xox` substring, `xoxq-…` (invalid class) |
| `openai-sk-key` | `"sk-proj-"` + 32 valid chars | `sk-` + 8 chars (below floor) |
| `gcp-sa-json` | synthetic pretty-printed **and** minified SA JSON | config JSON with `service_account` but no `private_key` |
| `jwt` | three generated base64url segments | base64 text without the two dots |
| `generic-assignment` | `api_key = "` + random 24-char base64 | `password = ""`, `token = "$TOKEN"`, `secret: changeme` |
| `high-entropy` | random 40-char base64 (entropy ≈ 6) | UUID / 40-hex git SHA (hex charset caps at 4.0 bits/char) |

**Coverage claim (honest scope):** each rule detects exactly its grammar column.
Token formats outside these grammars (e.g. Azure, Stripe, Twilio) are **not
covered** in this minimum guard — that residual stays named in §7(b).

## 4. Acceptance Criteria

Each carries a `verification_method` and `risk_class`.

| # | Criterion | verification_method | risk_class |
|---|-----------|---------------------|------------|
| AC1 | Staged file with a planted secret → pre-commit exits non-zero, commit blocked | test: plant a runtime-synthetic key, attempt commit, assert blocked | high (security) |
| AC2 | Clean staged content → hook passes, commit succeeds | test: clean content commits | low |
| AC3 | A PR **any of whose commits — including merge commits** — introduced a secret → CI fails, **even if the final diff no longer contains it**; the scan runs as a **step inside the required `Build & Test` job**, so its failure blocks merge without any settings change (§3) | ci step in the required job + tests: final-diff fixture, added-then-removed history case, merge-commit case | high (security) |
| AC4 | Scanner missing / errors / **times out** → **fail-closed** (block) | tests: simulate missing scanner, erroring scanner, **and hung scanner under the bounded timeout** — each asserts block | high (fail-safe) |
| AC5 | Scan runs with no network (stdlib only) | test/inspection: stdlib-only imports; no sockets | medium (air-gap) |
| AC6 | A text `fingerprint` clears **exactly one occurrence of one finding at one path**: a sibling finding (same rule, same blob — different match **or identical match at a different offset**) **stays blocking**, and the same blob at a **different path** stays blocking; a `blob_review` never applies to a text blob; editing any allowlisted content re-flags it; scanner + config secret-free | multi-hit test; duplicate-identical-match test; different-path test; blob_review-on-text rejection test; edit-reflag test; scanner scans its own tree clean | high (security) |
| AC7 | Edge inputs fail-closed per the §3.1 input-class table: empty stage passes only as provably-empty domain; **binary / oversized** → block, clearable only by `blob_review`; **unreadable → block, non-clearable** (CFADA-r4 B1); **gitlink / `.gitmodules` change → block, no clearance lane**. **No skip outcome exists**; outcome domain = {pass, allowlisted, block} | domain tests over every §3.1 input class (incl. gitlink, unreadable-non-clearable) → assert block or proven-pass, never a reasoned skip | high (fail-safe) |
| AC8 | Every §3.2 rule has a passing positive AND negative fixture, **generated from that rule's stated grammar** — a fixture satisfied via a different rule does not count | per-rule tests asserting the finding's `rule_id` equals the rule under test | high (security) |
| AC9 | Any `git` subprocess error (in either mode: unresolvable base/merge-base, shallow history, failed `cat-file`/`diff-tree`) → **fail closed** (block), never a reduced-domain scan | test: simulate `git` failure + shallow-clone case, assert block | high (fail-safe) |
| AC10 | Allowlist schema is validated on every run: malformed, incomplete, or **expired** entry → scan **blocks** with a validation error (invalid entries can neither clear findings nor be silently dropped) | test: malformed + expired entries each assert block | high (fail-safe) |

## 5. Named TestCases — one-to-one AC map (CFADA-r3 M1)

Stdlib-assert style; all named tests live in **`compile/test_secret_scan.py`**,
which must be **explicitly enumerated in `package.json`'s `verify` script**
(the live script enumerates Python test files one by one — an un-enumerated
file silently never runs; CFADA-r6 M2). The wiring test
`test_scan_step_lives_in_required_build_and_test_job` asserts this enumeration
alongside the ci.yml assertions. **Every AC clause maps to a named test; a
clause without a test is an unproven gate (§6 rolls it up as not-satisfied).**

| AC | Named test(s) |
|---|---|
| AC1 | `test_planted_secret_blocked` |
| AC2 | `test_clean_passes` |
| AC3 | `test_ci_changed_against_blocks_on_secret` · `test_secret_added_then_removed_in_history_blocked` · `test_secret_in_merge_commit_blocked` · `test_scan_step_lives_in_required_build_and_test_job` (asserts the ci.yml wiring **including the `fetch-depth: 0` checkout and per-event base semantics**, CFADA-r4 M1/M2) |
| AC4 | `test_scanner_error_fails_closed` · `test_scanner_timeout_fails_closed` (CFADA-r4 B2) |
| AC5 | `test_stdlib_only_no_network` (import allowlist over `secret_scan.py`: stdlib modules only, no `socket`/`urllib`/`http` usage) |
| AC6 | `test_allowlist_entry_does_not_cover_sibling_findings` · `test_duplicate_identical_matches_need_separate_entries` (CFADA-r5 B1) · `test_allowlist_entry_does_not_cover_other_paths` · `test_blob_review_rejected_for_text_blobs` · `test_allowlist_fingerprint_reflags_on_edit` · `test_allowlist_snapshot_matches_scan_mode` (CFAR F2) · `test_scanner_tree_scans_clean` |
| AC7 | `test_edge_cases_fail_safe` (empty stage) · `test_binary_blob_blocks` · `test_oversized_blob_blocks` · `test_gitlink_blocks` (gitlink mode `160000` entries) · `test_gitmodules_change_blocks` (CFADA-r5 M1 — `.gitmodules` file changes, independently of any gitlink) · `test_unreadable_blob_non_clearable` (CFADA-r4 B1) |
| AC8 | `test_each_rule_positive_and_negative` (asserts the finding's `rule_id` equals the rule under test) |
| AC9 | `test_git_error_fails_closed` · `test_shallow_clone_or_missing_base_fails_closed` · `test_push_event_zero_base_blocks` (CFADA-r4 M2) |
| AC10 | `test_allowlist_schema_and_expiry_enforced` (incl. the future-dated `reviewed_on` case, CFAR F1) · `test_allowlist_dates_compared_in_utc` (CFAR F6) |

**Test-data self-trip avoidance:** test secrets are synthetic and **generated at
test runtime** (never committed), so the scanner never flags its own fixtures and
there is no fixture-path ignore lane (avoids both the circular self-block and a
fail-open ignored path).

## 6. Gate — "satisfied only when"

Satisfied **only when**: AC1–AC10 all pass with committed test evidence, **and** the
scanner runs clean over the existing repo tree (every finding or block either
removed or cleared by the **applicable valid §3.1 allowlist record** — text
`fingerprint` or binary/oversized `blob_review`; CFADA-r5 N1), **and** the
secret-scan step inside the required `Build & Test` job is demonstrably green on
clean input and red on a planted secret. Any unproven criterion ⇒ not satisfied
(fail-closed rollup).

## 7. Authorization packet (for the AuthorityDecision gate — grants nothing yet)

- **Bounded scope:** add `compile/secret_scan.py`, `compile/.secretsallow` (fingerprint + blob_review formats), `.githooks/pre-commit`, its tests, a one-line hooks-setup step, and — inside `.github/workflows/ci.yml` only — a **secret-scan step inside the existing required `Build & Test` job** (CFADA-r3 B2: a separate job would not be a required check and could not block a merge) **plus the checkout change to `fetch-depth: 0` and a `timeout-minutes` bound on the scan step** (CFADA-r4 M1/B2: the history scan needs full history; naming the edit here so the implementer is not trapped between a shallow-blocked scanner and reduced-domain temptation), **plus the one-line `package.json` `verify`-script enumeration of `compile/test_secret_scan.py`** (CFADA-r6 M2: the live verify script names test files explicitly — without this edit the new tests would silently never run) — in **transpara-ai/wiki only**.
- **Allowed repo:** `transpara-ai/wiki`. **Forbidden:** every other repo; branch-protection / ruleset / settings changes; git-history rewrite; remediation of any *pre-existing* secret (separate concern).
- **Autonomy level:** propose — **draft PR only**; no merge; no push without an explicit ask.
- **Stop conditions:** if a fail-closed *offline* scanner cannot be achieved; if the false-positive rate forces a blanket disable to keep commits workable.
- **Residual-risk disposition:** (a) local hooks bypassable (`--no-verify`) → **CI is the real gate**, documented; (b) hand-maintained ruleset may miss novel patterns; coverage is **exactly the §3.2 grammars** (Azure/Stripe/Twilio-class formats not covered) → minimum-guard, extensible, gitleaks-complement deferred; (c) existing repo history **not** retro-scanned in this scope (the CI scan domain starts at each PR's merge-base) → follow-up; (d) **allowlist erosion** → governed by schema: mandatory `reviewed_by`/`reviewed_on`/`expires_on` (≤ 180 days), expiry **fails closed** (AC10), renewal only by re-review; (e) a scanner **cannot prove liveness or full secret absence** — it is a guard, not a proof; (f) **admin direct-push bypass** (CFADA-r4 M2): `main` protection has `enforce_admins: false`, so an admin can push to `main` without the PR gate — the push-path scan (§3) turns that into a **red required check on `main`** (detective), but nothing in this scope can make it preventive; changing `enforce_admins` is a settings change, explicitly out of scope; (g) **ci.yml is PR-editable** (CFAR F3 residual): `pull_request` workflows run the PR head's workflow definition, so a PR can edit or delete the scan step itself — visible in review (and far more visible than a subtle scanner edit, which the trusted-copy extraction closes); the required-check model cannot self-protect beyond that without branch-protection changes (out of scope).

## 8. Non-authorizations

Authorizes nothing. No implementation before the AuthorityDecision. No CI/branch-protection change beyond the named `ci.yml` job. No merge. No history rewrite. No claim that the repo's existing history is secret-free, nor that any detected string is live.

## Appendix — IADA (Internal Adversarial Design Assessment · self-directed)

> Self-directed review per TLC. **Does not satisfy CFADA.** Blockers driven to 0 by design edits (v0.1.1).

| # | Finding | Severity | Disposition |
|---|---------|----------|-------------|
| I1 | No path/ignore model → entropy false-positive storm | blocker | Addressed v0.1.1; **superseded by CFADA C3** (path-ignores replaced by fingerprint allowlist) |
| I2 | Test fixtures with secrets self-trip the scanner | blocker | **FIXED** §5 — runtime-generated synthetic fixtures |
| I3 | Oversized blob could evade the scan | blocker | **FIXED** §3.1 — > 1 MiB fails closed |
| I4 | Fail-closed pre-commit could block all work on a scanner bug | accepted | `--no-verify` escape + CI-of-record + AC4/AC7/AC9 bound it |
| I5 | `core.hooksPath` not set per-clone | accepted | CI is enforcement of record |
| I6 | "Curated ruleset" underspecified | accepted then **superseded by CFADA C4** (§3.2 now enumerates it) |

## Appendix — CFADA round 1 (Codex · cross-family) → repaired at v0.2.0, completed at v0.3.0

> Reviewer family: Codex/OpenAI (independent of Anthropic author). Reviewed head `a96d50f`. Verdict: **4 blockers**. Round 2 (below) judged the C2/C3/C4 repairs **partial**; they are completed at v0.3.0.

| # | Blocker | Disposition |
|---|---------|-------------|
| C1 | Untraceable source-of-intent (`CLAUDE.md`/memo not in-repo) | **FIXED v0.2.0, r2-verified** — frontmatter + §1 cite in-repo `DESIGN.md §Ingestion` + `PROVENANCE.md`; out-of-repo intent labelled as such |
| C2 | CI scan domain ambiguous ("staged" vs PR) | v0.2.0 partial (modes split but git semantics undefined) → **completed v0.3.0 per r2-B1** (§3: merge-base domain, per-commit blob union, fetch-depth 0, fail-closed on unresolvable) |
| C3 | Ignore/allowlist model creates fail-open lanes | v0.2.0 partial (path ignores removed, but per-blob fingerprint + binary skip remained fail-open) → **completed v0.3.0 per r2-B2/B3** (§3.1: per-finding `match_sha256`; binary blocks) |
| C4 | Custom ruleset not test-first | v0.2.0 partial (rules named but grammars were sketches) → **completed v0.3.0 per r2-B4** (§3.2: anchored grammars, normalization, grammar-bound fixtures, honest coverage claim) |
| note | Residual should add allowlist erosion + "cannot prove absence" | **ADDED** §7 (d)/(e); (d) governance completed v0.3.0 per r2-M1 |

## Appendix — CFADA round 2 (Codex · cross-family) → repaired at v0.3.0

> Reviewer family: Codex/OpenAI. Reviewed head `524fc13` (v0.2.0). Verdict: **FAIL — 4 blockers, 1 major** (C1 verified; C2/C3/C4 partial). Root class across all four: an outcome lane not provably deny-by-default. v0.3.0 closed the outcome vocabulary to {pass, allowlisted, block}. Round 3 (below) judged the B1–B4 repairs still partial; completed at v0.4.0.

| # | Finding | Disposition (v0.3.0) |
|---|---------|----------------------|
| B1 | CI scan domain lets PR-history secrets escape (add-then-remove before final diff) | v0.3.0: history-union scan domain, `fetch-depth: 0`, unresolvable ⇒ block. *r3 judged partial (merge commits escaped `diff-tree`; blob dedup erased paths) → completed v0.4.0 per r3-B1/B3* |
| B2 | Fingerprint keyed per blob, not per finding — one allowed false positive covers an unreviewed sibling secret | v0.3.0: key gains `match_sha256` + sibling test. *r3 judged partial (blob-union dedup contradicted the path-bound key) → completed v0.4.0 per r3-B3* |
| B3 | Binary "skip-with-reason" is a reasoned pass — fail-open input class | v0.3.0: binary blocks by default; `skip` removed from the outcome domain. *r3 judged partial (whole-blob "fingerprint" clearance recreated the lane under a new name) → completed v0.4.0 per r3-B4 (`blob_review` record, honestly blob-scoped)* |
| B4 | Detector contract imprecise — AC8 passable while claimed coverage misses real formats | **FIXED** — §3.2: exact anchored regexes, normalization rules, whitespace-tolerant JSON, honest rule names (`aws-access-key-id`, `github-token`, `openai-sk-key`), defined entropy thresholds, grammar-bound fixtures (AC8), explicit coverage claim + §7(b) residual. *r3 judged the fix partial (table `\|` escapes corrupted the regexes) → completed v0.4.0 per r3-B5* |
| M1 | Allowlist erosion named but ungoverned | **FIXED, r3-verified** — §3.1: mandatory `reviewed_by`/`reviewed_on`/`expires_on` (≤ 180 days), schema validated every run, malformed/expired ⇒ block; AC10 + `test_allowlist_schema_and_expiry_enforced` |

## Appendix — CFADA round 3 (Codex · cross-family) → repaired at v0.4.0

> Reviewer family: Codex/OpenAI. Reviewed head `bcd040a` (v0.3.0). Verdict: **FAIL — 6 blockers, 1 major** (M1 verified; B1–B4 repairs judged partial). Round 3 verified claims against the **live repo** (branch protection, ci.yml). Round 4 (below) verified five of the seven v0.4.0 repairs; R3-B4 and R3-M1 completed at v0.5.0.

| # | Finding | Disposition (v0.4.0) |
|---|---------|----------------------|
| R3-B1 | Merge commits escape `git diff-tree -r` (emits no blobs without merge handling) — a secret introduced in a merge/conflict resolution evades AC3 | **FIXED** — §3: `-m` diffs merge commits against **each parent**; named test `test_secret_in_merge_commit_blocked` |
| R3-B2 | CI gate not actually enforced: §7 forbade settings changes, live `main` protection requires only `Build & Test` + `cross-family-adversarial-review`, so a *separate* `secret-scan` job could never block a merge | **FIXED** — §3/§7: the scan is a **step inside the required `Build & Test` job**; live protection verified 2026-07-02; wiring asserted by `test_scan_step_lives_in_required_build_and_test_job` |
| R3-B3 | Distinct-blob union contradicts path-bound allowlist keys — one reviewed path could cover identical content at an unreviewed path | **FIXED** — §3: scan/report unit = `(canonical_path, blob_sha256)` **occurrence**; blob dedup allowed only as internal optimization; AC6 + `test_allowlist_entry_does_not_cover_other_paths` |
| R3-B4 | Binary/oversized whole-blob "fingerprint" was the skip lane renamed — one entry cleared arbitrary unscanned blob content while claiming per-finding scope | v0.4.0: two distinct record types (`fingerprint` vs `blob_review`). *r4 judged partial (class boundaries contradictory: oversized text undefined, unreadable accidentally clearable) → completed v0.5.0 per r4-B1 (input-class table)* |
| R3-B5 | "Exact Python `re`" grammars contained markdown `\|` escapes = literal pipes — stated fixtures could not match the stated grammar | **FIXED** — §3.2: grammars moved verbatim into a fenced code block (the authoritative contract); table now carries fixtures only |
| R3-B6 | Gitlinks (mode `160000`) / `.gitmodules` are not blobs — a submodule pointer bypasses the blob scanner | **FIXED** — §3: gitlink or `.gitmodules` change ⇒ **block**, no clearance lane in v1; AC7 + `test_gitlink_blocks`; symlinks scanned as text |
| R3-M1 | AC5/AC7/AC9 clauses broader than the named tests — no one-to-one AC→test map | v0.4.0: §5 rebuilt as an AC→test table. *r4 judged partial (AC4's timeout clause still had no named test) → completed v0.5.0 per r4-B2* |

## Appendix — CFADA round 4 (Codex · cross-family) → repaired at v0.5.0

> Reviewer family: Codex/OpenAI. Reviewed head `1364d45` (v0.4.0). Verdict: **FAIL — 2 blockers, 2 majors** (R3-B1/B2/B3/B5/B6 verified; R3-B4 and R3-M1 partial). Re-review pending on v0.5.0.

| # | Finding | Disposition (v0.5.0) |
|---|---------|----------------------|
| R4-B1 | `blob_review` applicability internally contradictory: "binary/oversized only" vs "never applies to text blobs" left **oversized text** undefined, and AC7 made **unreadable** blobs clearable — a clearance lane for content nobody can read or hash | **FIXED** — §3.1 input-class table decided in order on provable properties: unreadable ⇒ **block, non-clearable**; oversized (text or binary — size checked before content) ⇒ `blob_review` lane; binary ⇒ `blob_review` lane; scannable text ⇒ `fingerprint` only. Governing principle stated: an attestation may never override a performed scan. AC7 corrected; `test_unreadable_blob_non_clearable` |
| R4-B2 | Timeout fail-closed claim (R4/AC4) unverifiable — no named timeout test, no mechanism | **FIXED** — §3: hook + CI step invoke the scanner under a bounded timeout; any abnormal termination incl. timeout kill ⇒ block; CI `timeout-minutes` fails the required job by Actions semantics; AC4 + `test_scanner_timeout_fails_closed` |
| R4-M1 | `fetch-depth: 0` required by §3 but not authorized by §7 — build trap between a shallow-blocked scanner and reduced-domain temptation | **FIXED** — §7 bounded scope names the checkout `fetch-depth: 0` edit + the `timeout-minutes` bound; wiring test asserts both |
| R4-M2 | `github.base_ref` is PR-only, but the required `Build & Test` job also runs on `push` to `main` — no scan domain defined for the push path | **FIXED** — §3: per-event base semantics — `pull_request` ⇒ `origin/${{ github.base_ref }}` (preventive); `push` ⇒ `${{ github.event.before }}`, all-zeros/unresolvable ⇒ block (detective, stated honestly); §7(f) names the `enforce_admins: false` admin direct-push residual; `test_push_event_zero_base_blocks` |

## Appendix — CFADA round 5 (Codex · cross-family) → repaired at v0.6.0

> Reviewer family: Codex/OpenAI. Reviewed head `6a84be4` (v0.5.0). Verdict: **FAIL — 1 blocker, 1 major, 1 minor**; all four round-4 repairs **verified**. Re-review pending on v0.6.0.

| # | Finding | Disposition (v0.6.0) |
|---|---------|----------------------|
| R5-B1 | Fingerprint key collapses **identical** sibling findings: the same matched bytes at two offsets in one blob share one `match_sha256`, so one entry cleared both — falsifying "exactly one finding" | **FIXED** — §3.1: key gains `byte_offset` (stable: the entry pins the immutable blob SHA); AC6 + `test_duplicate_identical_matches_need_separate_entries` |
| R5-M1 | `.gitmodules` block clause had no independent named test (§5 mapped AC7 only to `test_gitlink_blocks`) | **FIXED** — §5 AC7 row adds `test_gitmodules_change_blocks`, scoped independently of any gitlink entry |
| R5-N1 | §6 clean-tree rollup said "removed or a **fingerprint** allowlist entry", contradicting the valid `blob_review` lane for binary/oversized | **FIXED** — §6: "cleared by the applicable valid §3.1 allowlist record"; also names the required-job wiring explicitly |

## Appendix — CFADA round 6 (Codex · cross-family) → **PASS**, majors repaired at v0.6.1

> Reviewer family: Codex/OpenAI. Reviewed head `0fe9ef1` (v0.6.0). Verdict: **PASS — 0 blockers**, 2 majors, 1 minor; all round-5 repairs verified. The majors carry no fail-open lane; repaired at v0.6.1 anyway so the packet reaches the AuthorityDecision gate with nothing known-open.

| # | Finding | Disposition (v0.6.1) |
|---|---------|----------------------|
| R6-M1 | `.secretsallow` grammar and identity normalization under-specified (file syntax, duplicate records, path derivation, span convention for composite detectors) — no fail-open lane (invalid entries block) but AC6/AC10 too implementer-dependent | **FIXED** — §3.1.1: JSON-Lines grammar with exact record shapes (unknown/missing key ⇒ block), `-z` raw-path strict-UTF-8 derivation, deterministic char→byte span convention, per-composite-rule reported spans, duplicate identity ⇒ block, UTC date comparison |
| R6-M2 | `npm run verify` gating depended on an unnamed edit surface — live `package.json` enumerates test files explicitly, so the new tests could exist yet silently never run | **FIXED** — §5 names `compile/test_secret_scan.py` + the `verify`-script enumeration (asserted by the wiring test); §7 scope names the one-line `package.json` edit |
| R6-N1 | §3 non-blob parenthetical still named only `test_gitlink_blocks` | **FIXED** — §3 names both tests |
