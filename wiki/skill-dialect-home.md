---
entity: The Skill Dialect-Home Convention
aliases: [skill dialect home, dialect-home convention, skills/hive-lifecycle, the lifecycle skill home, hive#265]
tier: architecture
status: compiled
last_compiled: "2026-07-12"
sources:
  - /Transpara/transpara-ai/repos/hive/skills/README.md  # the convention itself: features own their skills; claude/ + codex/ dialect subfolders; repo is truth over installed copies
  - /Transpara/transpara-ai/repos/hive/skills/hive-lifecycle/README.md  # the first feature home: dialect layout, symlink rule for tooling-mandated discovery paths, post-merge install sync
  - /Transpara/transpara-ai/repos/hive/docs/factory-orders/FO-hive-265-lifecycle-skill-home-v0.58.0.md  # FO-HIVE-265 — seed pins (immutable blob SHAs), the enumerated repair sets (R7 a–q and fresh-head bf–co and successors), acceptance language
  - raw/open-brain/2026-07.md  # L3476 (arc + the symlink/single-copy IAR catch), L3482–L3572 (original CFAR rounds: credential-flow, fail-open-timeout, capture-before-parse lessons), L3662 (29-round completion at a90b1bde), L3743 (fresh-head arc and merge)
confidence:
  sources: primary — the merged convention documents, the Factory Order, and the session records of both review arcs.
  claims: grounded. Round counts and repair letters are taken from the FO's own versioned repair sections; the FO version cited (v0.58.0) is the file on hive main at compile time and continues to advance as later slices touch the dialects.
---

# The Skill Dialect-Home Convention

**Where agent skills live, and how multiple model dialects of one feature coexist.** Established by the operator's 2026-07-11 verdict and merged as `transpara-ai/hive#267` (closing hive#265): *skills live with their feature's repository*; when execution differs by model family, the feature's home carries **dialect subfolders** — today `claude/` and `codex/`, with future dialects joining as siblings; and **the repository is truth over installed copies**, which re-sync from the repo after merges (`rsync -a --delete` into `~/.claude` and `~/.codex`).

Two sharp edges make the convention non-trivial:

- **Exactly one physical copy.** Claude Code auto-discovers project skills at `.claude/skills/`, a tooling-mandated path. Moving the file out would silently break discovery (a fail-open failure mode), and committing a second copy under `skills/` would fork the truth. The rule that emerged: dialects with tooling-mandated discovery paths keep their physical file at the tooling path, and the feature home links to it — `skills/hive-lifecycle/claude` is a relative symlink into `.claude/skills/hive-lifecycle`.
- **Immutable seed pins.** The Factory Order pins each dialect's seed content by git blob SHA, not by mutable install paths — a "pin" naming a mutable location is not a pin, because post-merge re-syncs would make the seed-vs-delta verification unreproducible.

## The hardening arcs

The first inhabitant — the hive-lifecycle operations runbook — went through two review arcs whose lessons outgrew the skill itself. The original 29-round cross-family arc (rounds at L3482–L3572 of the July record) converted the runbook from a convenience document into a governed operational surface: credentials became name-only checks after full values were found printed into transcripts; the council/pipeline/civilization examples were discovered to default their API to production and interpolate ambient bearer tokens into agent prompts ("check where secrets *flow*, not just where requests *go*"); unbounded wait-loops gained bounded, operation-gating timeouts; and systemd posture checks moved from unit-file text to merged properties and `/proc` effective environments, captured-before-parsed so a failed read is never mistaken for a safe value.

When strict branch protection later stranded that arc's exact-head review credit (see [[credit-stranding-under-branch-protection]]), a second, 23-round fresh-head arc followed. Its durable outputs: mutating `docker compose` commands are `cd &&`-chained so a missing checkout cannot destroy the caller's project; destructive resets are gated on the *database's* own view of connected clients rather than process-name enumeration; bearers travel via curl's stdin config because `/proc` argv is world-readable; and every fenced block in both dialects is machine-verified valid bash. Machinery the review itself had grown — an auto-cancel for queued restarts, process kill-lists — was **deleted rather than hardened** when later rounds attacked it, per the operator's convergence rule.

## Follow-on

The runbook's repeated deferral — "a mechanical verifier belongs in a tested Go subcommand" — was honored the next morning: `hive factory preflight-hive-unit` merged as Codex-authored `transpara-ai/hive#277`, and a further slice wiring the runbooks to that verifier is in flight as hive#283. The convention's install-sync step and the [[hive-governance|hive]] run-target hardening continued advancing the FO past the versions either arc ended on.
