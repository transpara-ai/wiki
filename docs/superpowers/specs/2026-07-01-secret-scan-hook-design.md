---
doc_id: TAI-WIKI-SECRET-SCAN-HOOK
title: Secret-Scan Pre-Commit Hook + CI Gate — Design Packet
doc_type: design
version: 0.3.0
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
- **`--changed-against <base>`** — scans **every blob introduced anywhere in the PR's commit history**, not just the final diff; used by the **CI job** in `.github/workflows/ci.yml` (the enforced gate). CI has no staged index, so it never assumes one. Exact git semantics (CFADA-r2 B1):
  - **Base ref**: CI passes the PR base explicitly (`origin/${{ github.base_ref }}`); the scan domain is `merge-base(<base>, HEAD) .. HEAD`.
  - **Blob enumeration**: for **every commit** in that range, `git diff-tree -r --no-renames` (rename detection **off**) collects every added/modified blob SHA; the scanner scans the **union of all distinct blobs**, so a secret committed then removed before the final diff is still caught (named test `test_secret_added_then_removed_in_history_blocked`).
  - **Fetch requirement**: the CI job checks out with `fetch-depth: 0`. If the base ref, the merge-base, or any enumerated blob is unresolvable (shallow clone, missing ref, failed `cat-file`) ⇒ **block** (AC9), never a reduced-domain scan.

Both modes **fail closed on any `git` subprocess error** (a failed `diff`/`cat-file` ⇒ block, never pass). The scanner reads a **fail-closed fingerprint allowlist** (§3.1). **Outcome vocabulary is closed and enumerated**: every scanned blob resolves to exactly `pass` (scanned clean), `allowlisted` (every finding cleared by a valid §3.1 fingerprint), or `block`. There is **no `skip` outcome** anywhere in the scanner (CFADA-r2 B3 removed the last one); any input the scanner cannot positively scan is `block`.

**Alternative considered — vendoring the `gitleaks` binary:** a more battle-tested
ruleset, but it is not installed and needs per-platform air-gap vendoring. Deferred
as a future *complement*, not the primary. This scanner is an explicit **minimum
guard (§3.2), not a gitleaks-equivalent.** (Reverses the Item-3 memo's initial
gitleaks lean on the finding that gitleaks is absent and the repo is stdlib-Python.)

### 3.1 Allowlist model (fail-closed — no ignore lanes, no skip outcome)

Per CFADA-r1 C3 and CFADA-r2 B2/B3/M1, there are **no blanket path ignores for
tracked text**, **no skip outcome for any input class**, and the fingerprint
clears **exactly one finding**, never a blob.

- **False positives** are cleared **only** by a **per-finding fingerprint** entry in `compile/.secretsallow`. The key is `rule_id + canonical_path + blob_sha256 + match_sha256` where `match_sha256` is the SHA-256 of the **exact matched byte span** (CFADA-r2 B2). One entry clears one finding: a second finding of the *same rule in the same blob* has a different `match_sha256` and **stays blocking** (named test `test_allowlist_entry_does_not_cover_sibling_findings`). Because the entry also pins the blob SHA, **editing the file re-flags everything** — the allowlist can never silently cover new content.
- **Allowlist governance (CFADA-r2 M1)**: every entry additionally requires `reason + owner + reviewed_by + reviewed_on + expires_on` (ISO dates; max validity 180 days, renewable only by re-review). The scanner **validates the schema on every run**: a malformed, incomplete, or **expired** entry ⇒ the scan **blocks** with an allowlist-validation error (an entry that cannot be proven valid clears nothing *and* is never silently dropped; named test `test_allowlist_schema_and_expiry_enforced`, AC10).
- **Binary blobs** (null-byte detected) **block by default** (CFADA-r2 B3): binary content cannot be positively text-scanned, and a reasoned skip is a fail-open lane — a null-byte file with an embedded token would escape. Message: *"binary content cannot be text-scanned — review manually and clear by fingerprint"*. Clearance is only a §3.1 fingerprint entry (per-blob `match_sha256` = SHA-256 of the whole blob, since no text span exists); any new binary content re-flags. The scanner still pattern-scans binary bytes and **reports** what it finds as reviewer evidence, but the report is advisory — the outcome is `block` regardless.
- **Oversized blobs** (> 1 MiB) **block**: "too large to scan — review manually and clear by fingerprint" (same per-blob fingerprint clearance as binary).
- Generated files (e.g. `package-lock.json`) **are scanned**; a real false positive there is cleared by fingerprint, not by ignoring the path.
- The **entropy heuristic is conservative** (min length + high threshold, defined in §3.2) and always subordinate to the explicit pattern rules — patterns are the primary signal, entropy is a backstop.
- **CI is the enforcement of record**; the local hook is fast feedback. A contributor who has not run the hooks-setup is still gated by CI.

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

| Rule id | Exact grammar (Python `re`) | Positive fixture (runtime-generated **from this grammar**) | Negative (stated near-miss) |
|---|---|---|---|
| `private-key` | `-----BEGIN [A-Z ]*PRIVATE KEY( BLOCK)?-----` (multi-line) | generated PEM header + base64 body | prose containing "private key" (no armor) |
| `aws-access-key-id` | `\b(AKIA\|ASIA)[0-9A-Z]{16}\b` | `"AKIA"` + 16 chars from `[0-9A-Z]` | 20-char uppercase word failing the prefix |
| `github-token` | classic `\bgh[pousr]_[A-Za-z0-9]{36,255}\b` **and** fine-grained `\bgithub_pat_[A-Za-z0-9_]{22,255}\b` | one of each, generated per branch | `ghp_short`, bare `github_pat` in prose |
| `slack-token` | `\bxox[baprs]-[A-Za-z0-9-]{10,}\b` | `"xoxb-"` + 24 valid chars | `xox` substring, `xoxq-…` (invalid class) |
| `openai-sk-key` | `\bsk-(proj-\|svcacct-\|admin-)?[A-Za-z0-9_-]{20,}\b` | `"sk-proj-"` + 32 valid chars | `sk-` + 8 chars (below floor) |
| `gcp-sa-json` | `"type"\s*:\s*"service_account"` **and** `"private_key"\s*:\s*"` in the same blob (whitespace/newline tolerant) | synthetic pretty-printed **and** minified SA JSON | config JSON with `service_account` but no `private_key` |
| `jwt` | `\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b` | three generated base64url segments | base64 text without the two dots |
| `generic-assignment` | `(?i)\b(api[_-]?key\|secret\|token\|passwd\|password)\b\s*[:=]\s*["']?` + **candidate**: length ≥ 16, charset `[A-Za-z0-9+/=_-]`, Shannon entropy ≥ 3.5 bits/char, and **not a placeholder** (empty, `<…>`, `$VAR`, `{{…}}`, `changeme`, `example`, `xxx…`) | `api_key = "` + random 24-char base64 | `password = ""`, `token = "$TOKEN"`, `secret: changeme` |
| `high-entropy` (backstop) | token length ≥ 32, charset `[A-Za-z0-9+/=_-]`, Shannon entropy ≥ 4.5 bits/char, not matched by any rule above | random 40-char base64 (entropy ≈ 6) | UUID / 40-hex git SHA (hex charset caps at 4.0 bits/char) |

**Coverage claim (honest scope):** each rule detects exactly its grammar column.
Token formats outside these grammars (e.g. Azure, Stripe, Twilio) are **not
covered** in this minimum guard — that residual stays named in §7(b).

## 4. Acceptance Criteria

Each carries a `verification_method` and `risk_class`.

| # | Criterion | verification_method | risk_class |
|---|-----------|---------------------|------------|
| AC1 | Staged file with a planted secret → pre-commit exits non-zero, commit blocked | test: plant a runtime-synthetic key, attempt commit, assert blocked | high (security) |
| AC2 | Clean staged content → hook passes, commit succeeds | test: clean content commits | low |
| AC3 | A PR **any of whose commits** introduced a secret → CI job fails, **even if the final diff no longer contains it** (`--changed-against` scans the union of blobs across `merge-base..HEAD`, §3) | ci job + tests: runtime fixture in final diff **and** the added-then-removed history case | high (security) |
| AC4 | Scanner missing / errors / times out → **fail-closed** (block) | test: simulate missing/erroring scanner, assert block | high (fail-safe) |
| AC5 | Scan runs with no network (stdlib only) | test/inspection: stdlib-only imports; no sockets | medium (air-gap) |
| AC6 | Allowlist clears **exactly one finding**: a sibling finding (same rule, same blob, different match) **stays blocking**; editing an allowlisted blob re-flags it; scanner + config secret-free | multi-hit test (two findings in one blob, allowlist one, assert other blocks); edit-reflag test; scanner scans its own tree clean | high (security) |
| AC7 | Edge inputs fail-closed: empty stage passes only as provably-empty domain; binary, oversized, unreadable blob → **block** (clearable only by fingerprint). **No skip outcome exists**; outcome domain = {pass, allowlisted, block} | domain tests over every input class → assert block or proven-pass, never a reasoned skip | high (fail-safe) |
| AC8 | Every §3.2 rule has a passing positive AND negative fixture, **generated from that rule's stated grammar** — a fixture satisfied via a different rule does not count | per-rule tests asserting the finding's `rule_id` equals the rule under test | high (security) |
| AC9 | Any `git` subprocess error (in either mode: unresolvable base/merge-base, shallow history, failed `cat-file`/`diff-tree`) → **fail closed** (block), never a reduced-domain scan | test: simulate `git` failure + shallow-clone case, assert block | high (fail-safe) |
| AC10 | Allowlist schema is validated on every run: malformed, incomplete, or **expired** entry → scan **blocks** with a validation error (invalid entries can neither clear findings nor be silently dropped) | test: malformed + expired entries each assert block | high (fail-safe) |

## 5. Named TestCases

`test_planted_secret_blocked` · `test_clean_passes` · `test_scanner_error_fails_closed` ·
`test_allowlist_fingerprint_reflags_on_edit` · `test_ci_changed_against_blocks_on_secret` ·
`test_secret_added_then_removed_in_history_blocked` ·
`test_allowlist_entry_does_not_cover_sibling_findings` ·
`test_binary_blob_blocks` · `test_allowlist_schema_and_expiry_enforced` ·
`test_edge_cases_fail_safe` · `test_git_error_fails_closed` · `test_each_rule_positive_and_negative`
(stdlib-assert style, matching `compile/test_*.py`; gated in `npm run verify` + CI).

**Test-data self-trip avoidance:** test secrets are synthetic and **generated at
test runtime** (never committed), so the scanner never flags its own fixtures and
there is no fixture-path ignore lane (avoids both the circular self-block and a
fail-open ignored path).

## 6. Gate — "satisfied only when"

Satisfied **only when**: AC1–AC10 all pass with committed test evidence, **and** the
scanner runs clean over the existing repo tree (every finding either removed or a
fingerprint allowlist entry), **and** the CI job is demonstrably green on clean
input and red on a planted secret. Any unproven criterion ⇒ not satisfied
(fail-closed rollup).

## 7. Authorization packet (for the AuthorityDecision gate — grants nothing yet)

- **Bounded scope:** add `compile/secret_scan.py`, `compile/.secretsallow` (fingerprint format), `.githooks/pre-commit`, its tests, a one-line hooks-setup step, and a `secret-scan` job in `.github/workflows/ci.yml` — in **transpara-ai/wiki only**.
- **Allowed repo:** `transpara-ai/wiki`. **Forbidden:** every other repo; branch-protection / ruleset / settings changes; git-history rewrite; remediation of any *pre-existing* secret (separate concern).
- **Autonomy level:** propose — **draft PR only**; no merge; no push without an explicit ask.
- **Stop conditions:** if a fail-closed *offline* scanner cannot be achieved; if the false-positive rate forces a blanket disable to keep commits workable.
- **Residual-risk disposition:** (a) local hooks bypassable (`--no-verify`) → **CI is the real gate**, documented; (b) hand-maintained ruleset may miss novel patterns; coverage is **exactly the §3.2 grammars** (Azure/Stripe/Twilio-class formats not covered) → minimum-guard, extensible, gitleaks-complement deferred; (c) existing repo history **not** retro-scanned in this scope (the CI scan domain starts at each PR's merge-base) → follow-up; (d) **allowlist erosion** → governed by schema: mandatory `reviewed_by`/`reviewed_on`/`expires_on` (≤ 180 days), expiry **fails closed** (AC10), renewal only by re-review; (e) a scanner **cannot prove liveness or full secret absence** — it is a guard, not a proof.

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

> Reviewer family: Codex/OpenAI. Reviewed head `524fc13` (v0.2.0). Verdict: **FAIL — 4 blockers, 1 major** (C1 verified; C2/C3/C4 partial). Root class across all four: an outcome lane not provably deny-by-default. v0.3.0 fixes the class — the outcome vocabulary is closed to {pass, allowlisted, block}; `skip` no longer exists. Re-review pending on v0.3.0.

| # | Finding | Disposition (v0.3.0) |
|---|---------|----------------------|
| B1 | CI scan domain lets PR-history secrets escape (add-then-remove before final diff) | **FIXED** — §3: scan domain = union of blobs across every commit in `merge-base(<base>, HEAD)..HEAD`, rename detection off, `fetch-depth: 0`, unresolvable ⇒ block; AC3 + `test_secret_added_then_removed_in_history_blocked` |
| B2 | Fingerprint keyed per blob, not per finding — one allowed false positive covers an unreviewed sibling secret | **FIXED** — §3.1: key gains `match_sha256` (SHA-256 of the exact matched byte span); AC6 + `test_allowlist_entry_does_not_cover_sibling_findings` |
| B3 | Binary "skip-with-reason" is a reasoned pass — fail-open input class | **FIXED** — §3.1: binary blobs **block** by default, clearable only by fingerprint after manual review; pattern-scan output is advisory evidence, never an outcome; AC7 + `test_binary_blob_blocks`; `skip` removed from the outcome domain entirely |
| B4 | Detector contract imprecise — AC8 passable while claimed coverage misses real formats | **FIXED** — §3.2: exact anchored regexes, normalization rules, whitespace-tolerant JSON, honest rule names (`aws-access-key-id`, `github-token`, `openai-sk-key`), defined entropy thresholds, grammar-bound fixtures (AC8), explicit coverage claim + §7(b) residual |
| M1 | Allowlist erosion named but ungoverned | **FIXED** — §3.1: mandatory `reviewed_by`/`reviewed_on`/`expires_on` (≤ 180 days), schema validated every run, malformed/expired ⇒ block; AC10 + `test_allowlist_schema_and_expiry_enforced` |
