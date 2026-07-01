---
doc_id: TAI-WIKI-SECRET-SCAN-HOOK
title: Secret-Scan Pre-Commit Hook + CI Gate — Design Packet
doc_type: design
version: 0.2.0
status: draft
canonical: false
created: 2026-07-01
updated: 2026-07-01
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
- **`--changed-against <base>`** — scans the blobs changed against a base ref; used by the **CI job** in `.github/workflows/ci.yml` (the enforced gate). CI has no staged index, so it never assumes one.

Both modes **fail closed on any `git` subprocess error** (a failed `diff`/`cat-file` ⇒ block, never pass). The scanner reads a **fail-closed fingerprint allowlist** (§3.1).

**Alternative considered — vendoring the `gitleaks` binary:** a more battle-tested
ruleset, but it is not installed and needs per-platform air-gap vendoring. Deferred
as a future *complement*, not the primary. This scanner is an explicit **minimum
guard (§3.2), not a gitleaks-equivalent.** (Reverses the Item-3 memo's initial
gitleaks lean on the finding that gitleaks is absent and the repo is stdlib-Python.)

### 3.1 Allowlist & skip model (fail-closed — no ignored text lanes)

Per CFADA B3, there are **no blanket path ignores for tracked text** — an ignored
text path would be a fail-open lane for a committed secret.

- **False positives** are cleared **only** by a per-finding **fingerprint** entry in `compile/.secretsallow`: `rule_id + canonical_path + blob_sha256 + reason + owner`. Because it is pinned to the exact blob SHA, **editing the file re-flags it** — the allowlist can never silently cover new content.
- The **only** things skipped, and each **skipped-with-reason (never silently)**: **binary** blobs (null-byte detected — not entropy-scanned, but still pattern-scanned for embedded PEM/keys) and **oversized** blobs (> 1 MiB → **fail closed**: block with "too large to scan — review manually or allowlist"). Generated files (e.g. `package-lock.json`) **are scanned**; a real false positive there is cleared by fingerprint, not by ignoring the path.
- The **entropy heuristic is conservative** (min length + high threshold) and always subordinate to the explicit pattern rules — patterns are the primary signal, entropy is a backstop.
- **CI is the enforcement of record**; the local hook is fast feedback. A contributor who has not run the hooks-setup is still gated by CI.

### 3.2 Detector contract — minimum ruleset (test-first)

Per CFADA B4, the minimum detectors are **enumerated here** and each carries a
positive **and** negative fixture (AC8). This is a **minimum guard, not
gitleaks-equivalent**; it is extensible.

| Rule id | Detects | Positive fixture (synthetic, runtime-generated) | Negative |
|---|---|---|---|
| `private-key` | PEM `-----BEGIN … PRIVATE KEY-----` blocks | a generated PEM header | prose containing "private key" |
| `aws-akia` | AWS access key id `AKIA[0-9A-Z]{16}` + secret | synthetic `AKIA…` | a random uppercase word |
| `github-pat` | `gh[pousr]_[A-Za-z0-9]{36,}` | synthetic `ghp_…` | `ghp` in text |
| `slack-token` | `xox[baprs]-…` | synthetic `xoxb-…` | `xox` substring |
| `openai-key` | `sk-[A-Za-z0-9]{20,}` | synthetic `sk-…` | `sk-` prefix in prose |
| `gcp-sa-json` | service-account JSON (`"type":"service_account"` + `"private_key"`) | synthetic JSON | a config JSON without a key |
| `jwt` | `eyJ…\.eyJ…\.…` three-part token | synthetic JWT | base64 text without dots |
| `generic-assignment` | `(api_key|secret|token|password)\s*[:=]\s*["']?<high-entropy>` | `api_key = "<entropy>"` | `password = ""` / placeholder |
| `high-entropy` (backstop) | long high-entropy strings on non-ignored text, not matched above | a random 40-char base64 | a UUID / git SHA (below threshold) |

## 4. Acceptance Criteria

Each carries a `verification_method` and `risk_class`.

| # | Criterion | verification_method | risk_class |
|---|-----------|---------------------|------------|
| AC1 | Staged file with a planted secret → pre-commit exits non-zero, commit blocked | test: plant a runtime-synthetic key, attempt commit, assert blocked | high (security) |
| AC2 | Clean staged content → hook passes, commit succeeds | test: clean content commits | low |
| AC3 | A PR with a secret → CI job fails (CI scans `--changed-against <base>`, not a staged index) | ci job + test invoking `--changed-against` on a runtime fixture | high (security) |
| AC4 | Scanner missing / errors / times out → **fail-closed** (block) | test: simulate missing/erroring scanner, assert block | high (fail-safe) |
| AC5 | Scan runs with no network (stdlib only) | test/inspection: stdlib-only imports; no sockets | medium (air-gap) |
| AC6 | Allowlist is fail-closed fingerprint; scanner + config secret-free | scanner scans its own tree clean; editing an allowlisted blob re-flags it | medium |
| AC7 | Edge inputs fail-safe: empty stage, binary, oversized, unreadable blob | domain tests → deny or skip-with-reason, never silent pass | high (fail-safe) |
| AC8 | **Every §3.2 detector rule has a passing positive AND negative fixture** | per-rule tests | high (security) |
| AC9 | Any `git` subprocess error (in either mode) → **fail closed** (block) | test: simulate `git` failure, assert block | high (fail-safe) |

## 5. Named TestCases

`test_planted_secret_blocked` · `test_clean_passes` · `test_scanner_error_fails_closed` ·
`test_allowlist_fingerprint_reflags_on_edit` · `test_ci_changed_against_blocks_on_secret` ·
`test_edge_cases_fail_safe` · `test_git_error_fails_closed` · `test_each_rule_positive_and_negative`
(stdlib-assert style, matching `compile/test_*.py`; gated in `npm run verify` + CI).

**Test-data self-trip avoidance:** test secrets are synthetic and **generated at
test runtime** (never committed), so the scanner never flags its own fixtures and
there is no fixture-path ignore lane (avoids both the circular self-block and a
fail-open ignored path).

## 6. Gate — "satisfied only when"

Satisfied **only when**: AC1–AC9 all pass with committed test evidence, **and** the
scanner runs clean over the existing repo tree (every finding either removed or a
fingerprint allowlist entry), **and** the CI job is demonstrably green on clean
input and red on a planted secret. Any unproven criterion ⇒ not satisfied
(fail-closed rollup).

## 7. Authorization packet (for the AuthorityDecision gate — grants nothing yet)

- **Bounded scope:** add `compile/secret_scan.py`, `compile/.secretsallow` (fingerprint format), `.githooks/pre-commit`, its tests, a one-line hooks-setup step, and a `secret-scan` job in `.github/workflows/ci.yml` — in **transpara-ai/wiki only**.
- **Allowed repo:** `transpara-ai/wiki`. **Forbidden:** every other repo; branch-protection / ruleset / settings changes; git-history rewrite; remediation of any *pre-existing* secret (separate concern).
- **Autonomy level:** propose — **draft PR only**; no merge; no push without an explicit ask.
- **Stop conditions:** if a fail-closed *offline* scanner cannot be achieved; if the false-positive rate forces a blanket disable to keep commits workable.
- **Residual-risk disposition:** (a) local hooks bypassable (`--no-verify`) → **CI is the real gate**, documented; (b) hand-maintained ruleset may miss novel patterns → minimum-guard, extensible, gitleaks-complement deferred; (c) existing repo history **not** retro-scanned in this scope → follow-up; (d) **allowlist erosion** (fingerprints accrete) → periodic review of `.secretsallow`; (e) a scanner **cannot prove liveness or full secret absence** — it is a guard, not a proof.

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

## Appendix — CFADA round 1 (Codex · cross-family) → repaired at v0.2.0

> Reviewer family: Codex/OpenAI (independent of Anthropic author). Reviewed head `a96d50f`. Verdict: **4 blockers**. All accepted and repaired; re-review pending on v0.2.0.

| # | Blocker | Disposition (v0.2.0) |
|---|---------|----------------------|
| C1 | Untraceable source-of-intent (`CLAUDE.md`/memo not in-repo) | **FIXED** — frontmatter + §1 cite in-repo `DESIGN.md §Ingestion` + `PROVENANCE.md`; out-of-repo intent labelled as such |
| C2 | CI scan domain ambiguous ("staged" vs PR) | **FIXED** — §3 explicit modes `--staged` (hook) / `--changed-against <base>` (CI); fail-closed on git error (AC9) |
| C3 | Ignore/allowlist model creates fail-open lanes | **FIXED** — §3.1 fingerprint allowlist (rule+path+blob-SHA+reason+owner); no path ignores for tracked text; only binary/oversized skipped, fail-closed |
| C4 | Custom ruleset not test-first | **FIXED** — §3.2 enumerated detector contract with positive+negative fixtures; AC8; labelled minimum-guard, not gitleaks-equivalent |
| note | Residual should add allowlist erosion + "cannot prove absence" | **ADDED** §7 (d)/(e) |
