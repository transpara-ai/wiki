---
entity: Owain Lewis Work System (Blueprint & Factory)
aliases:
  - owainlewis
  - Blueprint
  - Factory (owainlewis)
  - Neo (owainlewis)
  - the minimalist solo software factory
tier: investigation
status: compiled
last_compiled: 2026-07-06
civilization_contribution: "Pattern-only; no ADR. Contributes six mineable patterns — review-capacity throttle, definition-of-ready as Factory Order lint, density-over-length gate prose, audit→objective compiler, single-mover/stale-claim label invariants, Neo's runtime cage as worked example — and the strongest independent confirmation yet of the dev-arc's two-human-gate topology. Blueprint/Factory/Neo are never eligible as runtime, gate authority, certification, or truth store."
sources:
  - "raw/civilization/external-landscape/tai-res-2026-006-owainlewis-evaluation.md"  # TAI-RES-2026-006 v1.0.0, code-anchored evaluation (this page's primary source)
  - https://github.com/owainlewis/blueprint/tree/3815669  # evaluated commit, 2026-07-05 — read in full from local clone
  - https://github.com/owainlewis/factory/tree/8b346d7  # evaluated commit, 2026-07-05 — all ~1,895 Go lines read as ground truth
  - https://github.com/owainlewis/neo/tree/022d001  # evaluated commit — harness/orchestrator; the code-enforced "cage"
  - "raw/inbox/2026-06-24/solo-orchestrator/TAI-RES-2026-005-v1.1.0-Solo-Orchestrator-Evaluation-959878a544d6.md"  # TAI-RES-2026-005 — the session-hook-vs-sovereign-record precedent this eval extends
current_research_version: 1.0.0
confidence:
  enforcement_posture: high — every enforcement claim is code- or prompt-text-anchored (exec lines, prompt wrapper, audit heuristics, cage constants read directly)
  methodology_read: high — all 17 Blueprint skills, guides, Factory PRD/standard/spec, and dogfood files read in full
  author_background: high — Oracle OCI Director-of-Engineering role verified 3–0 by the deep-research sweep (archived GitHub profile snapshots + leaddev.com bio); current roles from self-published materials
  reception: medium — the deep-research sweep confirmed the negative definitively: no substantive third-party critiques, reviews, or adoption case studies of blueprint/factory surfaced under adversarial verification; traction evidence is stars/forks and his own channels
  civilization_baseline: high — quoted from the accepted v4.0 doctrine set and shipped gate tool; Level 0 state taken from doc 06's own gate table
  learning_opportunities: medium-high — patterns are text-verifiable; the hive review-capacity-throttle gap should be re-verified before implementation
raw_documents:
  - "raw/civilization/external-landscape/tai-res-2026-006-owainlewis-evaluation.md"  # sha256 38b8d05a519ca5321a826c9be406182dea7cb695a6c65ff12f250aee55913e90; session-authored (PR #49) Civilization external-landscape research, placed outside the browser-ingest inbox by design — provenance is git history + this frontmatter; wiki#50 tracks a sanctioned ingest path for session-authored docs
---

# Owain Lewis Work System (Blueprint & Factory)

**Owain Lewis is building, solo and in public, a minimalist system aimed at the Dark Factory's own goal — "The objective is not to automate coding. The objective is to automate software engineering" — and TAI-RES-2026-006 finds him independently converged on the dev-arc's control points while standing on the opposite side of its load-bearing seam.** His stack: **Blueprint** (211★; 17 markdown skills — spec/plan/implement/review/task-to-pr — plus an unattended GitHub-label loop layer), **Factory** (early Go runner executing repo-owned `.factory/` process: standards, workflows, *objectives* — literally "repo-owned work orders" — and a journal), **Neo** (a minimalist agent harness whose orchestrator enforces depth/fanout/count/time budgets in code), plus a cross-agent skills installer, all under the published creed: *"Blueprint fixes the process and trusts the intelligence… Bet on the model."*

## The finding in one line

**Lewis writes the factory's discipline as prompts an agent is trusted to follow; the Civilization writes the same discipline as records a kernel cannot certify around.**

## Convergences (structural, not cosmetic)

- **Two human gates in the same places:** spec approval before code (`needs:spec` → `agent:ready` is a human flip) and human-only merge ("Merging is always a human decision") — the same topology as TLC's Human Design Review and Human Review/merge.
- **Adversarial review before PR:** his `code-reviewer` agent is a working IAR — "You did not write this change and owe it nothing: review to disprove, not to approve."
- **Deterministic orchestration / agent reasoning split**, stated on both sides in near-identical words ("Factory performs deterministic orchestration. Agents perform reasoning" / Neo: "agents decide, code constrains, code never interprets").
- **Work orders, evidence culture, risk-graded autonomy, WIP/attention limits** — Factory objectives ≈ small Factory Orders; "Agents should not only say a repo is healthy. They should show evidence"; unattended loops claim `risk:low` only; the work loop throttles on human review capacity.

## The seam

Everything in his system that is not a human click or a narrow code cage is **advisory**: safety rules are prompt text around `claude -p --permission-mode auto`; "success" in a run record is an exit code; review evidence binds to no SHA; the adversarial reviewer shares the author's model family (fresh **context**, not independent **family**); intake readiness is agent-judged where the hive requires a human-set label; and where he does gate in code (Neo's dangerous-bash check) it is a **denylist** — the construction the fail-safe doctrine forbids. He knows and prices this ("risk:high waits for an attended session"; "the model is partly grading its own work"). Fail-open at the trust boundary is not an oversight of his system — it *is* his system, rational at solo blast radius and disqualifying at industrial blast radius.

The deepest split is the truth object: for Lewis, running code + tests is truth and "Once the code is right, the spec's job is done"; for the Civilization the *record* is truth — the packet at its blob SHA, the gate result, the authority decision — because its founding problem is that confident summaries cannot be trusted at scale.

## Determination (TAI-RES-2026-006 §4.4)

1. **ADR exists?** No — no *pre-existing* ADR, decision row, or doctrine text named owainlewis, Blueprint, Factory, or Neo before this evaluation landed (2026-07-06 search of docs + wiki; this eval and its article are, by design, the first mentions).
2. **Create one?** No ADR: nothing is adopted as a dependency or control-plane component (same disposition as Solo Orchestrator). Durable record = the eval + a per-item crosswalk row via the docs process; any pursued learning gets its own TLC arc.
3. **Contribution?** **Pattern-only.** Six learnings, led by the **review-capacity throttle** ("finishing reviewed work beats starting new work") as a fail-closed WIP gate on the human review queue, plus the five-predicate definition-of-ready as a Factory Order lint and a density pass over gate prose. High value as a mirror; never a component.

## What his system cannot take from prompts alone (the inverse)

Proof that review happened to *this* code (exact-head binding); independence that survives correlated model failure (cross-family floor); fail-closed protected actions (allowlist policy, `PolicyMissing` → `Forbidden` for high-risk and critical actions); typed authority with scope/expiry/quorum; an append-only record that outlives the session; an institution that outlives its single human.

## Placement

Civilization external-landscape research (same placement class as Sakana/Hermes/OKF/MemPalace/Solo Orchestrator): the subject concerns agent workflow, governance, verification, and autonomous-development capability — not Platform competitive intelligence. It activates nothing: no Lewis component gains work, gate, release, or truth roles.
