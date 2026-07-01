---
doc_id: TAI-WIKI-SECRET-SCAN-HOOK
title: Secret-Scan Pre-Commit Hook + CI Gate — Design Packet
doc_type: design
version: 0.1.1
status: draft
canonical: false
created: 2026-07-01
owner: Michael Saucier
steward: Claude (Opus 4.8)
authority: planning
tlc_stage: design
source_of_intent:
  - Item 3 tooling advisory memo (this repo) — P0 recommendation
  - Michael directive 2026-07-01 (build order: hook first)
  - doctrine: CLAUDE.md secret-scrub (non-negotiable); wiki DESIGN.md §Ingestion
intake_channel: A (human request)
---

# Secret-Scan Pre-Commit Hook + CI Gate — Design Packet

> **TLC design packet. Authorizes nothing.** No code until an External-Committee
> AuthorityDecision is recorded for the bounded scope in §7. Test-first: the
> AcceptanceCriteria and TestCases below are written before implementation.

## 1. Problem

The wiki ingests raw source material (`raw/inbox/`, browser-ingested drops) that
can carry secrets; the corpus includes config-laden repos; and — confirmed
2026-07-01 — there is **no secret scan in `ci.yml` or in a pre-commit hook**.
The secret-scrub is a non-negotiable in both `CLAUDE.md` and `DESIGN.md`
(§Ingestion). This is a live doctrine hole; the hook closes it.

## 2. Requirements

- **R1** — a pre-commit hook blocks committing detected secrets (fail-closed).
- **R2** — a CI job enforces the same scan on PRs (defense-in-depth; local hooks are bypassable with `--no-verify`).
- **R3** — offline / air-gap: no network, no per-platform binary vendoring friction.
- **R4** — fail-closed on scanner error, absence, timeout, or ambiguous result.
- **R5** — an auditable allowlist for false positives (no blanket disable).
- **R6** — the scanner and its config contain no secrets themselves.

## 3. Approach (recommended)

A **pure-Python stdlib secret scanner** (`compile/secret_scan.py`), zero-dependency
and air-gap-native, matching the repo's existing stdlib-Python + "no pytest,
air-gap friendly" pattern. It carries a curated ruleset (private-key blocks,
AWS/GCP keys, JWTs, common token prefixes such as `ghp_`/`xox`/`sk-`, plus a
high-entropy heuristic) and reads an **auditable allowlist** (`compile/.secretsallow`,
path+digest entries with a reason). It is wired to:

- **(a)** a versioned git hook: `.githooks/pre-commit` + `git config core.hooksPath .githooks` (documented in a one-line setup step + README), so the hook is shared and reviewable, not a private `.git/hooks` file; and
- **(b)** a **CI job** in `.github/workflows/ci.yml` running the same scanner over the PR (the enforced gate).

### 3.1 Scope & ignore model (fail-safe against false-positive erosion)

- Scans **staged, text** blobs only; binary blobs (null-byte detected) are not entropy-scanned.
- **Ignored paths** (generated/vendored, high false-positive): `package-lock.json`, `dist/`, `node_modules/`, `.venv/`, `.git/`, `test-results/`, and declared test-fixture paths — a small, reviewed, in-repo list, **not** per-commit toggles.
- **Oversized blobs** (> 1 MiB) are **not silently skipped** — they **fail closed** ("too large to scan — review manually or allowlist"), so a giant blob cannot smuggle a secret past the scanner.
- The **entropy heuristic is conservative** (min length + high threshold, excluded on ignored paths) and always subordinate to the explicit pattern rules — patterns are the primary signal, entropy is a backstop.
- **CI is the enforcement of record**; the local hook is fast feedback. A contributor who has not run the hooks-setup is still gated by CI.

**Alternative considered — vendoring the `gitleaks` binary:** a more battle-tested
ruleset, but it is not installed and needs per-platform air-gap vendoring. Deferred
as a future *complement*, not the primary. (This reverses the Item 3 memo's initial
gitleaks lean, on the finding that gitleaks is absent and the repo is stdlib-Python.)

## 4. Acceptance Criteria

Each carries a `verification_method` and `risk_class`.

| # | Criterion | verification_method | risk_class |
|---|-----------|---------------------|------------|
| AC1 | A staged file with a planted secret → pre-commit exits non-zero, commit blocked | test: plant a synthetic key, attempt commit, assert blocked | high (security) |
| AC2 | Clean staged content → hook passes, commit succeeds | test: clean content commits | low |
| AC3 | A PR containing a secret → CI job fails | ci job + test invoking the scanner on a fixture | high (security) |
| AC4 | Scanner missing / errors / times out → **fail-closed** (block) | test: simulate missing binary + non-zero exit, assert block | high (fail-safe) |
| AC5 | Scan runs with no network (stdlib only) | test/inspection: no imports beyond stdlib; no sockets | medium (air-gap) |
| AC6 | Allowlist is auditable; scanner + config are secret-free | scanner scans its own tree clean; allowlist entries carry path+digest+reason | medium |
| AC7 | Edge inputs handled fail-safe: empty stage, binary files, oversized files, unreadable blob | domain tests over each edge → deny or skip-with-reason, never silent pass | high (fail-safe) |

## 5. Named TestCases

`test_planted_secret_blocked` · `test_clean_passes` · `test_scanner_error_fails_closed` ·
`test_allowlisted_false_positive_passes` · `test_ci_blocks_on_secret` · `test_edge_cases_fail_safe`
(stdlib-assert style, matching `compile/test_*.py`; gated in `npm run verify` + CI).

**Test-data self-trip avoidance:** test secrets are synthetic and either generated at test runtime or kept under an allowlisted `tests/fixtures/` path, so the scanner never flags its own fixtures (avoids the circular self-block).

## 6. Gate — "satisfied only when"

The hook gate is satisfied **only when**: AC1–AC7 all pass with committed test
evidence, **and** the scanner runs clean over the existing repo tree (every
finding either a true removal or an auditable allowlist entry), **and** the CI
job is demonstrably green on clean input and red on a planted secret. Any
unproven criterion ⇒ not satisfied (fail-closed rollup).

## 7. Authorization packet (for the AuthorityDecision gate — grants nothing yet)

- **Bounded scope:** add `compile/secret_scan.py`, `compile/.secretsallow`, `.githooks/pre-commit`, its tests, a one-line hooks-setup step, and a `secret-scan` job in `.github/workflows/ci.yml` — in **transpara-ai/wiki only**.
- **Allowed repo:** `transpara-ai/wiki`. **Forbidden:** every other repo; branch-protection / ruleset / settings changes; git-history rewrite; remediation of any *pre-existing* secret (separate concern).
- **Autonomy level:** propose — **draft PR only**; no merge; no push without an explicit ask.
- **Stop conditions:** if a fail-closed *offline* scanner cannot be achieved; if the false-positive rate forces a blanket disable to keep commits workable.
- **Residual-risk disposition:** (a) local hooks are bypassable (`--no-verify`) → **CI is the real gate**, documented; (b) hand-maintained ruleset may miss novel patterns → extensible, defense-in-depth, gitleaks-complement deferred; (c) existing repo history is **not** retroactively scanned in this scope → tracked as a follow-up.

## 8. Non-authorizations

Authorizes nothing. No implementation before the AuthorityDecision. No CI/branch-protection change beyond the named `ci.yml` job. No merge. No history rewrite. No claim that the repo's existing history is secret-free.

## Appendix — IADA (Internal Adversarial Design Assessment · self-directed)

> Self-directed review per TLC. **Does not satisfy CFADA** (that gate is cross-family / Codex). Blockers driven to 0 by design edits; this doc is `v0.1.1` post-IADA.

| # | Finding | Severity | Disposition |
|---|---------|----------|-------------|
| I1 | No path/ignore model → entropy false-positive storm on lockfiles/`dist/`/binaries erodes the gate | blocker | **FIXED** §3.1 — staged-text-only, ignore list, conservative entropy |
| I2 | Test fixtures containing secrets would self-trip the scanner (circular block) | blocker | **FIXED** §5 — synthetic, runtime-generated or allowlisted fixtures path |
| I3 | Oversized blob could evade the scan if silently skipped | blocker | **FIXED** §3.1 — > 1 MiB fails closed ("review manually"), never a silent skip |
| I4 | Fail-closed pre-commit could block all work on a scanner bug | accepted | fail-safe is correct; `--no-verify` escape + CI-of-record + AC4/AC7 tests bound it |
| I5 | `core.hooksPath` not set per-clone → some contributors lack the local hook | accepted | CI is enforcement of record (R2 / §3.1); local hook is fast feedback only |
| I6 | "Curated ruleset" underspecified | accepted | v0.1 ruleset enumerated at implementation (PEM/private-key, AWS `AKIA`, GitHub `ghp_`/`gho_`/`ghs_`, Slack `xox`, generic `key=secret` assignments, high-entropy backstop); extensible |

**Residual after IADA:** ruleset completeness (defense-in-depth + extensible), local-hook bypassability (CI-of-record), existing history not retro-scanned (follow-up). **No open blockers → ready for CFADA (Codex).**
