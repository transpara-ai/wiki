---
entity: Credit Stranding Under Branch Protection
aliases: [credit stranding, the stranded CFAR credit, head-delta vs strict protection, the fresh-head arc]
tier: arc
status: compiled
last_compiled: "2026-07-12"
civilization_contribution: "Process finding from live operation (2026-07-11/12): the gate standard's head-delta rule and GitHub's strict up-to-date branch protection interact so that long-lived reviewed PRs CANNOT merge on their reviewed head — the forced branch update strands exact-head review credit and requires a fresh review at the new head. Named, evidenced, and absorbed into merge planning; not a doctrine change."
raw_documents: []
sources:
  - /Transpara/transpara-ai/repos/docs/dark-factory/v4.0/07-cfar-cfada-dev-arc-gate-standard-v4.0.md  # the gate standard: CFAR credit binds to the exact head SHA; head-delta rule for ready-state review (4.2.0)
  - raw/open-brain/2026-07.md  # L3698 (the merge attempt evidence: admin GraphQL and REST both refuse with "required status checks are expected"), L3743 (both merges complete; the fresh-head arc summary and its meta-lessons)
  - /Transpara/transpara-ai/repos/hive/docs/factory-orders/FO-hive-265-lifecycle-skill-home-v0.58.0.md  # the fresh-head repair sections (bf–co) the stranding forced into existence
confidence:
  sources: primary for the hive events (session records with exact SHAs and API error strings); the branch-protection behavior is asserted from the live 405/GraphQL refusals observed, not from GitHub documentation.
  claims: grounded; the "effectively inexhaustible review stream" observation is an operational judgment from one 23-round sample, stated as such.
---

# Credit Stranding Under Branch Protection

**An investigation into why a fully-reviewed PR could not merge on its reviewed head — and what the forced re-review revealed.** On 2026-07-11, `transpara-ai/hive#267` held a cross-family review PASS at exact head `a90b1bde…` after a 29-round arc. The [[gates|gate standard]]'s head-delta rule (4.2.0) binds that credit to the exact SHA: merge on that head and the credit stands. But the hive repository's branch protection sets `strict: true` — branches must be up to date with main — and #267 was BEHIND after an intervening merge.

## The mechanism

On a BEHIND branch under strict protection, GitHub reports the *required status checks* as **"expected"** for the prospective merge — not failed, not pending, but unreported. In that state:

- `gh pr merge --admin` (GraphQL) refuses: *"2 of 2 required status checks are expected."*
- The REST merge endpoint refuses identically (HTTP 405).

There is no administrative bypass for *expected* checks the way there is for failing ones. The only path forward is `gh pr update-branch` — which mints a new head SHA, and by the head-delta rule **strands the exact-head review credit**. The two rules are individually sound and jointly guarantee that any PR whose base has moved must be re-reviewed before merge. For short-lived PRs this is invisible; for a PR carrying weeks of review investment, it converts one merge into a fresh review arc.

## What the forced re-review found

The fresh-head arc on the same content ran **23 rounds and surfaced 34 findings — essentially all real** (operational-safety defects in the lifecycle runbook: destructive-command guards, credential exposure via argv and xtrace, strict-shell semantics, systemd state adjudication). Two observations generalize:

1. **A fresh reviewer pass over a large operational document is effectively inexhaustible.** Zero-blocker verdicts certify a *pass*, not perfection; a re-review with new eyes will find new true findings. Review credit is therefore *economically* real — stranding it has a measurable cost (here: a full day of rounds) — and merge planning should treat BEHIND state on a reviewed PR as urgent.
2. **Convergence came from class-level contracts, not per-instance guards.** The arc closed only when repairs became categorical: a strict-shell contract per block instead of `|| true` per line; a whole-corpus `bash -n` audit instead of fixing the reported fence; database-adjudicated quiescence instead of an ever-growing process list; and outright deletion of review-grown machinery that later rounds attacked (the operator's convergence rule, applied four times).

## Disposition

Absorbed as practice, not doctrine change: merge reviewed PRs promptly or accept the fresh-head cost; when a base moves under a reviewed PR, prefer merging the *other* PR first only if it is CLEAN (as was done — `hive#272` merged before the update). The stranding also produced compounding value despite its cost: the follow-on hardening (`hive#275`–`#280`, including the tested unit-posture preflight the runbook had deferred) landed within a day, largely Codex-authored under the reversed review direction.
