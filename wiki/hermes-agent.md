---
entity: Hermes Agent
aliases:
  - hermes-agent
  - Hermes
  - the Hermes Agent family
  - transpara-ai/hermes-agent
  - hermes-agent-self-evolution
  - hermes-example-plugins
  - Hermes Self-Evolution
  - Hermes Agent Self-Evolution Evaluation
  - TAI-RES-2026-002 Hermes
  - the agent that grows with you
tier: investigation
status: compiled; unified article
last_compiled: 2026-06-24
investigation_topic: Hermes Agent
civilization_contribution: "Contributed the governed optimizer pattern behind U7 CapabilityArtifact governance and U8 CapabilityEvolution sequencing; Hermes itself remains deferred and pattern-only."
raw_documents:
  - raw/inbox/2026-06-24/hermes-agent/TAI-RES-2026-002-v1.0.0-Hermes-Agent-Self-Evolution-Evaluation-a7b119333702.md
  - "raw/inbox/2026-07-07/hermes-agent/tai-res-2026-002-v1.0.1-hermes-agent-self-evolution-evaluation.md"
  - /Transpara/transpara-ai/repos/docs/dark-factory/v3.9/implementation/epics/02-technology-decision-crosswalk-v3.9.md
  - /Transpara/transpara-ai/repos/docs/dark-factory/research/checkpoints/2026-05-13-05-phase-4-batch-c-agent-execution-orchestration.md
  - /Transpara/transpara-ai/repos/docs/dark-factory/research/checkpoints/2026-05-13-06-phase-4-batch-d-governance-self-evolution-platform-tooling.md
  - /Transpara/transpara-ai/repos/docs/dark-factory/research/checkpoints/2026-05-13-07-phase-5-inclusion-marginal-contribution-matrix.md
  - /Transpara/transpara-ai/repos/docs/dark-factory/research/checkpoints/2026-05-13-10-civilization-landscape-investigation-closeout.md
sources:
  - /Transpara/transpara-ai/repos/docs/dark-factory/v3.9/implementation/epics/02-technology-decision-crosswalk-v3.9.md  # v3.9.1 crosswalk; Hermes decision row (L80) + per-item note "governed optimizer pattern only" (L163-167); freeze/reopen policy (L41-68)
  - raw/transpara/dark-factory/v3.9/01-unified-architecture-decisions-v3.9.md  # Decision 15: external frameworks stay outside control roles
  - raw/transpara/dark-factory/archive/v3/adrs/ADR-0010-hermes-self-evolution-governed-optimizer.md  # ADR-0010: Hermes self-evolution governed optimizer posture
  - /Transpara/transpara-ai/repos/docs/dark-factory/research/checkpoints/2026-05-13-05-phase-4-batch-c-agent-execution-orchestration.md  # Batch C — repo-grounded analysis of hermes-agent (L532-655) and hermes-example-plugins (L657+); README-only evidence
  - /Transpara/transpara-ai/repos/docs/dark-factory/research/checkpoints/2026-05-13-06-phase-4-batch-d-governance-self-evolution-platform-tooling.md  # Batch D — repo-grounded analysis of hermes-agent-self-evolution (L75-208); evidence = README.md + PLAN.md
  - /Transpara/transpara-ai/repos/docs/dark-factory/research/checkpoints/2026-05-13-07-phase-5-inclusion-marginal-contribution-matrix.md  # Phase 5 inclusion matrix — three distinct Hermes rows (L130, L131, L135); specific rejections (L302, L309)
  - /Transpara/transpara-ai/repos/docs/dark-factory/research/checkpoints/2026-05-13-10-civilization-landscape-investigation-closeout.md  # closeout — Hermes self-evolution feeds U7/U8 capability-evolution updates (via investigation article cross-ref)
  - "GitHub API: repos/transpara-ai/hermes-agent (fork metadata, 2026-06-13 live)"  # isFork=true, parent=NousResearch/hermes-agent, createdAt 2026-05-11T11:32:53Z, description "The agent that grows with you", MIT
  - "GitHub API: repos/transpara-ai/hermes-agent-self-evolution (fork metadata, 2026-06-13 live)"  # isFork=true, parent=NousResearch/hermes-agent-self-evolution, createdAt 2026-05-11T11:32:06Z, description "Evolutionary self-improvement … DSPy + GEPA"
  - "GitHub API: repos/transpara-ai/hermes-example-plugins (fork metadata, 2026-06-13 live)"  # isFork=true, parent=NousResearch/hermes-example-plugins, createdAt 2026-05-13T03:42:39Z, MIT
  - raw/inbox/2026-06-24/hermes-agent/TAI-RES-2026-002-v1.0.0-Hermes-Agent-Self-Evolution-Evaluation-a7b119333702.md  # repo-local copy of released internal research report; advisory, not doctrine
  - "raw/inbox/2026-07-07/hermes-agent/tai-res-2026-002-v1.0.1-hermes-agent-self-evolution-evaluation.md"  # added via gated supersession PR 2026-07-07 (wiki#52 path A); note: classification corrected for the record; supersedes: raw/inbox/2026-06-24/hermes-agent/TAI-RES-2026-002-v1.0.0-Hermes-Agent-Self-Evolution-Evaluation-a7b119333702.md
  - /Transpara/transpara-ai/repos/docs/civilization/v4.1/implementation/epics/epic-15-institutional-substrate-doctrine/corpus/copied/civilization/knowledge/external-landscape/hermes-agent-self-evolution/TAI-RES-2026-002-v1.0.0-Hermes-Agent-Self-Evolution-Evaluation.md  # original Stage 0 copied-corpus path; provenance context only
  - "Upstream context only (not re-published): github.com/NousResearch/hermes-agent (+ -self-evolution, -example-plugins)"  # cited as context for why we forked to read; never mirrored
confidence:
  decision_row: medium — the v3.9.1 crosswalk has ONE row labelled "pattern-only / deferred" for "Hermes" (L80), but the investigation's own Phase 5 matrix records THREE distinct Hermes rows with three different decisions (runtime-adapter / plugin-reference / capability-optimizer). The crosswalk row collapses them; both are stated below, neither silently picked.
  fork_date_and_identity: high — confirmed live via GitHub fork metadata (the two named upstreams forked 2026-05-11; the example-plugins fork 2026-05-13)
  repo_internals: thin — the investigation inspected only README.md (hermes-agent, hermes-example-plugins) and README.md + PLAN.md (hermes-agent-self-evolution). No code-level inspection. Every internal claim is README/PLAN-grounded, not code-verified.
  dspy_gepa_claim: medium — "DSPy + GEPA" is the self-evolution repo's own description (live) and the Batch D analysis (README/PLAN); it is the upstream's self-description, not independently verified behaviour.
  license: high for hermes-agent / hermes-example-plugins (MIT, live + README badge); medium for self-evolution — README says MIT but PLAN flags an AGPL-v3 "Darwinian Evolver" path that must stay external-CLI-only (Batch D L194)
  self_evolution_risk: asserted, not proven — "self-improvement loop can become autonomous capability promotion" is the investigation's risk assessment, not an observed failure
  article_unification: this page supersedes the prior separate Hermes Agent, Hermes Self-Evolution, and Hermes evaluation wiki surfaces; they overlap but do not materially contradict
---

# Hermes Agent

**A forked public-project *family* the [[civilization-landscape-investigation]] evaluated — three NousResearch repos read as ground-truth source, and declined for any control role.** "Hermes Agent" in this wiki names a cluster of three forks Transpara pulled into the `transpara-ai` org so they could be inspected as code rather than from marketing pages: `hermes-agent` (the self-improving agent runtime — "the agent that grows with you"), `hermes-agent-self-evolution` (an external optimizer pipeline that evolves Hermes's skills/prompts/tools using **DSPy + GEPA**), and `hermes-example-plugins` (reference plugins). The two named repos were forked from the public upstream `NousResearch/hermes-agent` (+ `-self-evolution`) on **2026-05-11**; the example-plugins fork followed on **2026-05-13** (live GitHub fork metadata). During the [[dark-factory]] landscape investigation (Phase 4, **2026-05-13**) the family was assessed against the then-canonical v3.8 design and recorded — under the later v3.9.1 *External Technology Decision Crosswalk* — for **Hermes** as **"governed optimizer pattern only / deferred":** Hermes-style self-evolution "must not become a continuous production loop in v3.9," gated to a capability-evolution epic (Epic 8 or later).

This article is about **our investigation and decision**, not a mirror of the upstream's documentation. The NousResearch repos are public OSS; they are cited here only as context for *why we forked them to read them*, never re-published.

> ⚠ **Fail-legible note (one row vs. three).** The compile request, following the v3.9.1 crosswalk, treats "Hermes" as a single item with one decision ("pattern-only / deferred"). The investigation's own **Phase 5 inclusion matrix** is more granular: it records **three separate rows** with **three different decisions** — and the crosswalk collapses them into one "Hermes" line. This article keeps both layers visible and does not silently pick one. See "Where it sits in the decision crosswalk" and "The three forks, three decisions" below.

## Why this is one article

Run-6 briefly exposed three Hermes pages as peers: the original Hermes Agent
family page, a Hermes Self-Evolution optimizer page, and the released internal
Hermes self-evolution evaluation. That was structurally misleading. They are not
three independent research efforts.

They are three evidence layers about one topic:

| Layer | What it contributes | Does it contradict the others? |
| --- | --- | --- |
| `hermes-agent` / `hermes-example-plugins` / `hermes-agent-self-evolution` survey evidence | The 2026-05-13 landscape investigation: runtime adapter, plugin reference, and optimizer pattern decisions | No. It explains the original fork-family decision. |
| Hermes Self-Evolution technical reading | The DSPy + GEPA optimizer mechanics: trace-driven mutation, candidate variants, tests, PR output, guardrails | No. It is the detailed optimizer slice of the same family. |
| `TAI-RES-2026-002-v1.0.0-Hermes-Agent-Self-Evolution-Evaluation.md` | The 2026-06-24 internal research report comparing Hermes to the Civilization Capability Evolution chain | No. It confirms the deferral and adds the "same loop, different leash" analysis. |

The only tension is resolution, not substance. The crosswalk collapses Hermes
into one row; the investigation matrix splits the family into three repos; the
new evaluation compares the optimizer to the native [[capability-evolution]]
chain. The unified reading is: **Hermes is one external family with three useful
facets, all advisory and all outside control roles.**

This article therefore supersedes the prior separate Hermes wiki leaves. Search
terms for "Hermes Self-Evolution" and "Hermes evaluation" resolve here.

## Where it sits in the decision crosswalk

The accepted-canonical *per-item* register is the v3.9.1 crosswalk. Its single Hermes row:

| Field | Value (per v3.9.1 crosswalk, L80 / L163-167) |
|---|---|
| Item | **Hermes** |
| Current decision | **pattern-only / deferred** |
| ADR / doc ref | v3.9 Decision 12; capability-evolution rules |
| Integration mode | **governed optimizer pattern only** |
| Owning epic | **Epic 8 or later capability packet** |
| Fork / adapter / pattern / exclude | **pattern** |
| Main risk | "self-evolution loop without governance" |
| PR #61 change required? | "yes: name deferral and monitoring gate" |

The per-item note is the binding constraint, and it is terse:

> "Decision: governed optimizer pattern only. Hermes-style self-evolution must not become a continuous production loop in v3.9."

The crosswalk's own freeze policy applies: pattern-only adoptions are **frozen at the v3.9 reference point** and do not track upstream behaviour unless an epic explicitly reopens them — and reopening Hermes would require recording the upstream commit reviewed, which pattern changed, and whether Dark Factory adopts, rejects, or defers it. The Open Brain adversarial-review capture on PR #61 (2026-05-18) flagged Hermes specifically as one of the pattern-only adoptions that landed **with no upstream-refresh mechanism documented** — so the freeze is the default-frozen policy, not a recorded per-item cadence.

The single ratified rule above all of this is v3.9 **Decision 15: external frameworks stay outside control roles** (see [[civilization-landscape-investigation]]); the crosswalk row detail is `status: review`, the routing rule is the law.

## The three forks, three decisions

Read at the resolution the investigation actually worked at, the family splits cleanly. From the **Phase 5 inclusion matrix** (verbatim decisions):

| Repo | Batch | Phase-5 decision | Mapped pattern | Recommendation (Phase 5) |
|---|---|---|---|---|
| `hermes-agent` | C | **Optional future runtime adapter** | RuntimeBroker adapter candidate | "Defer until RuntimeBroker/policy/eval; not Base Slice 0." |
| `hermes-example-plugins` | C | **Pattern / reference only** | CapabilityArtifact design | "Reference only for plugin/capability policy." |
| `hermes-agent-self-evolution` | D | **Optional capability-evolution pattern** | Capability evolution | "High-priority governed optimizer pattern; no activation authority." |

The crosswalk's one "Hermes / governed optimizer pattern only / deferred" line is closest to the **self-evolution** repo's decision; the runtime-adapter status of `hermes-agent` itself is recorded only in the matrix and in Batch C, not in the crosswalk's collapsed row. Treat the crosswalk as the ratified-but-coarse register and the matrix/batches as the fine-grained evidence.

## How it entered the arc

The Hermes family was on the investigation's fixed **22-item candidate list** (kickoff, 2026-05-13), pinned to exact `transpara-ai/<name>` paths. The investigation ran under one hard rule from the operator: *no aspirational claims accepted without code or canonical-document evidence; if access to a repo is missing, stop — do not substitute upstreams or marketing pages* (see [[civilization-landscape-investigation]]). The forks into `transpara-ai` existed precisely so the repos could be read as source under that rule. Two of the three landed in **Batch C** ("agent execution / orchestration"): `hermes-agent` and `hermes-example-plugins`. The third, `hermes-agent-self-evolution`, landed in **Batch D** ("governance, self-evolution, and platform-tooling") alongside [[paperclip|Paperclip]], the Microsoft Agent Governance Toolkit, and gStack.

## What the investigation found each to be

### hermes-agent — the self-improving runtime (evidence: README only)

Batch C describes it as *"a self-improving AI agent from Nous Research"* with *"a terminal interface, messaging gateway, built-in learning loop, skills system, persistent memory/user modeling, cron scheduler, subagents, RPC/scripts, multiple terminal backends, model-provider flexibility, batch trajectory generation, and RL/training integrations."* Its terminal backends are enumerated — local, Docker, SSH, Singularity, Modal, Daytona, Vercel Sandbox — and it supports migration from OpenClaw. The verdict was that it is the **strongest Batch C candidate for a future runtime adapter** "because it already addresses skills, memory, terminal backends, cron, subagents, migration, and trajectory generation."

What it explicitly **is not**, per the analysis: *"not v3.8 EventGraph truth, Work DAG, authority model, release certification, or capability governance. Its self-improvement loop is not sufficient for v3.8 capability promotion."* Its documented command-approval, DM-pairing, and container-isolation surfaces "are not v3.8 AuthorityRequest/AuthorityDecision/ExecutionReceipt." The recommendation: include as an **optional future bounded-runtime adapter and capability-evolution inspiration**, never in [[base-slice-0|Base Slice 0]], and only behind a RuntimeEnvelope, protected-action policy, MemoryReference/KnowledgeReference, [[capability-evolution|CapabilityArtifact governance]], and rollback. (See [[runtime-broker|RuntimeBroker]] for the adapter boundary this would have to pass.)

### hermes-agent-self-evolution — the DSPy/GEPA optimizer (evidence: README + PLAN)

This is the repo the prompt's theme foregrounds, and the one the crosswalk's "governed optimizer pattern only" line is really about. Batch D describes it as *"a standalone optimization pipeline that operates on `hermes-agent`, not inside it. It uses DSPy + GEPA to evolve Hermes skills, prompts, tool descriptions, and later code. It produces candidate variants, evaluates them, applies constraint gates, and opens PRs for human review."* Its README loop, quoted:

```
Read current skill/prompt/tool
Generate eval dataset
Run GEPA optimizer using execution traces
Produce candidate variants
Evaluate
Apply constraint gates
Open PR against hermes-agent
```

The PLAN adds a five-tier staging — Tier 1 skill files, Tier 2 tool descriptions, Tier 3 system-prompt components, Tier 4 code evolution, **Tier 5 continuous self-improvement loop**. Phase 1 (skill evolution) is marked implemented; later tiers are planned.

The investigation's headline judgement is unusually warm: it is *"the most concrete candidate for how governed self-improvement can work in practice: offline optimization, benchmark comparison, PR output, human review, rollback, and staged expansion."* Critically, the investigation noted its loop **already maps onto v3.8's own capability-evolution chain** — *"v3.8 already includes EvolutionOrder, CapabilityArtifact, EvalDataset, OptimizationRun, CandidateVariant, BenchmarkResult, HumanReview, CapabilityVersion, ActivationPolicy, and RollbackRecord."* In other words, the native [[capability-evolution|Capability Evolution]] pipeline and the Hermes optimizer describe the same shape; Hermes is read as a reference implementation of a pattern Dark Factory already owns.

What it **is not**, per Batch D: *"not a promoter, release authority, runtime, or rollback authority. It optimizes artifacts; v3.8 must decide whether to accept them."* The recommendation: include as a concrete pattern and likely source material for the [[capability-evolution|Capability Evolution]] MVP, but *"do not allow it to merge or activate anything without v3.8 EvolutionOrder, BenchmarkResult, HumanReview, CapabilityVersion, ActivationPolicy, and RollbackRecord."*

### hermes-example-plugins — the plugin-boundary reference (evidence: README only)

A small repo of reference plugins for Hermes, demonstrating plugin surfaces (host-owned structured LLM calls, async LLM access, dashboard plugin tabs/routes, reskin/slot themes). The README states the plugins are **not bundled** with `hermes-agent` — they exist for plugin authors to read, copy, install, or ignore. The investigation kept it as **pattern/reference only** for *"plugin/capability policy"* — i.e. as input to how Dark Factory should govern skills and plugins as [[capability-evolution|CapabilityArtifacts]], with the named risk being "ungoverned plugins."

## Why deferred / pattern-only, and not adopted

The investigation's containment logic is the same one it applied to every external control-plane or self-modifying candidate: mine the pattern, refuse the authority. The specific recorded rejections (Phase 5, §10):

> "Hermes must not become self-authorizing runtime or capability promoter."
> "Hermes self-evolution must not auto-promote or auto-activate capabilities."

The risks behind those lines, from Batch C / Batch D:

- **Self-improvement can bypass capability governance** — a loop that promotes its own outputs is the precise failure [[capability-evolution|Capability Evolution]] exists to prevent (an optimizer's authority must end at `CandidateVariant`).
- **SessionDB mining can leak or overfit private data** — the optimizer uses session history as evaluation data, which under v3.9 must be governed memory/evidence, not unreviewed private context (see [[memory-knowledge-advisory]]).
- **LLM-as-judge and synthetic evals can reward prompt gaming** — eval-gaming is the named risk on the self-evolution row.
- **Tool/backend blast radius** — multiple terminal backends, cron, messaging, and subagents can each trigger protected actions or bypass the [[work|Work]] DAG if unconstrained.
- **A continuous improvement loop must not auto-activate in production** — Tier 5 of the PLAN is exactly the "continuous self-improvement loop" the crosswalk forbids as a v3.9 production loop.

The deferral is therefore not a rejection of the *idea* — the investigation calls the self-evolution pipeline "high-priority" — but a refusal to let it run **before** the governing controls exist. That gating is what "Epic 8 or later capability packet" encodes.

## What Hermes actually contributed to v3.9

Unlike a pure reject, the Hermes family left a mark on the native design. The investigation's real product was eight gaps and a **U1–U10 update set** folded into [[v3-9]] (see [[civilization-landscape-investigation]]); two of those updates name Hermes as their inspiration:

- **U7 — `CapabilityArtifact` governance for skills/plugins/workflow packs**, credited to "gStack, Hermes plugins."
- **U8 — `CapabilityEvolution` MVP sequencing**, credited to "Hermes self-evolution, Autoresearch."

So the Hermes optimizer is, in a real sense, one of the reference patterns behind the shape of the native [[capability-evolution|Capability Evolution]] chain — adopted as *inspiration for a governed native pattern*, never as a dependency or a promoter. That chain was then built (and twice adversarially hardened) in `transpara-ai/eventgraph` as the E2 capability-evolution MVP — see [[capability-evolution]] for how the "optimizer cannot self-promote" intent fared in real code.

## What the 2026-06-24 evaluation adds

The released internal evaluation
`TAI-RES-2026-002-v1.0.0-Hermes-Agent-Self-Evolution-Evaluation.md` does not
reverse the prior Hermes decision. It sharpens it.

Its core finding is that Hermes Self-Evolution and the native Capability
Evolution chain describe almost the same loop:

```text
Hermes: read -> eval dataset -> optimize -> candidate -> evaluate -> gate -> PR

Civilization: EvolutionOrder -> EvalDataset -> OptimizationRun ->
CandidateVariant -> BenchmarkResult -> HumanReview -> CapabilityVersion ->
ActivationPolicy -> FactoryRuntimeVersion -> RollbackRecord
```

The difference is where authority stops. Hermes stops at "open a PR" and relies
on human review. The Civilization makes the leash part of the substrate:
optimizer actors cannot promote their own output, only the release role may
promote, global activation is disabled for the MVP, review evidence must bind to
the promoted candidate and benchmark result, and activation is a governed edge.

So the new evaluation confirms the prior posture:

| Prior item | Unified reading |
| --- | --- |
| v3.9 crosswalk | "governed optimizer pattern only / deferred" remains correct. |
| Three Hermes forks | runtime adapter, plugin-reference, and optimizer facets remain distinct but belong in one article. |
| ADR-0010 | proposed governed-optimizer posture is consistent with the native chain. |
| U7 / U8 | CapabilityArtifact governance and CapabilityEvolution sequencing remain the right native learning path. |
| Decision 15 | external frameworks stay outside control roles. |

The learning opportunities remain advisory and bounded:

| Opportunity | Boundary |
| --- | --- |
| Use GEPA for `OptimizationRun -> CandidateVariant` | optimizer creates candidates only |
| Govern SessionDB-style trace mining as EvalDataset input | no raw private-context shortcut |
| Add size-limit and caching-compatibility predicates | native validation, not Hermes authority |
| Mine Hermes Agent backends as RuntimeBroker reference | deferred Epic 6+ adapter work |
| Use Hermes plugins as CapabilityArtifact checklist | U7 governance input only |
| Execute one end-to-end governed EvolutionOrder | Epic 8-style canary, with rollback |

## Fail-legible notes

- **One crosswalk row, three real decisions (stated, not resolved).** The v3.9.1 crosswalk has a single "Hermes / pattern-only / deferred" row (L80). The investigation's Phase 5 matrix has three rows: `hermes-agent` = optional future **runtime adapter** (RuntimeBroker candidate), `hermes-example-plugins` = **pattern/reference only**, `hermes-agent-self-evolution` = optional **capability-evolution** pattern. These are not contradictory — they are different repos — but the crosswalk's collapse loses the runtime-adapter and plugin-reference facets. Both layers are above; neither is silently chosen.
- **Thin internal evidence.** The investigation inspected **README only** for `hermes-agent` and `hermes-example-plugins`, and **README + PLAN** for `hermes-agent-self-evolution`. No code-level inspection occurred. Every claim about internals — the learning loop, backend list, DSPy/GEPA mechanics, the five-tier plan, plugin surfaces — is README/PLAN-grounded, not code-verified. Mark repo-internals confidence **thin**.
- **DSPy + GEPA is the upstream's self-description.** "Evolutionary self-improvement … using DSPy + GEPA" is the live repo description and the Batch D README/PLAN reading; it is corroborated across our notes but traces to the upstream's own framing, not independently verified behaviour. Carried as medium-confidence context.
- **License nuance.** `hermes-agent` and `hermes-example-plugins` are MIT (live fork metadata + README badges). The **self-evolution** repo's README says MIT, but its PLAN flags a **"Darwinian Evolver" path that is AGPL v3** and "should be external CLI only" (Batch D L194). The investigation's licensing line records "Hermes self-evolution MIT with AGPL external code option." If this is ever reopened, the AGPL boundary is a supply-chain gate, not a footnote.
- **Self-evolution risk is asserted, not observed.** "The self-improvement loop can become autonomous capability promotion if not constrained" is the investigation's risk assessment — the reason the decision is fenced to pattern-only and deferred — not a record of an observed failure in the Hermes code.
- **The 2026-06-24 evaluation confirms; it does not activate.** The evaluation's main contribution is the "same loop, different leash" comparison. It does not promote Hermes into the kernel, truth source, Work replacement, policy owner, release authority, certification authority, capability promoter, factory controller, or Site replacement.
- **Fork dates differ across the three repos.** The two repos the prompt names (`hermes-agent`, `hermes-agent-self-evolution`) were forked **2026-05-11** (matching the prompt). The third, `hermes-example-plugins`, was forked **2026-05-13** — two days later, the same day as the investigation. Low-stakes; noted for completeness.
- **Upstream cited, never re-published.** Per org rule, `NousResearch/hermes-agent` (and the two sibling repos) are public OSS. Their descriptions ("The agent that grows with you"; the DSPy/GEPA self-evolution line) and MIT licensing are corroborated live as context for *why we forked them to read them*, not as content to mirror. The wiki subject is our investigation and our decision.

## Sources & provenance

- v3.9.1 **External Technology Decision Crosswalk** — `/Transpara/transpara-ai/repos/docs/dark-factory/v3.9/implementation/epics/02-technology-decision-crosswalk-v3.9.md` (Hermes decision row L80; per-item note "governed optimizer pattern only" L163-167; freeze/reopen policy L41-68). The authoritative — but coarse, single-row — decision record.
- **Phase 4 Batch C** candidate analysis — `…/research/checkpoints/2026-05-13-05-phase-4-batch-c-agent-execution-orchestration.md` (`hermes-agent` section L532-655, `hermes-example-plugins` section from L657). Primary evidence for the runtime and plugin repos; explicitly README-only.
- **Phase 4 Batch D** candidate analysis — `…/research/checkpoints/2026-05-13-06-phase-4-batch-d-governance-self-evolution-platform-tooling.md` (`hermes-agent-self-evolution` section L75-208, inclusion-matrix line L589). Primary evidence for the optimizer; evidence inspected = README.md + PLAN.md; DSPy/GEPA loop L96-108, five-tier PLAN L112-118, risks L184-190, license/AGPL note L194.
- **Phase 5 inclusion matrix** — `…/research/checkpoints/2026-05-13-07-phase-5-inclusion-marginal-contribution-matrix.md` (the three distinct Hermes rows L130/L131/L135; the specific rejections L302 and L309). The investigation's own source for the per-item decisions the crosswalk later collapsed.
- **Investigation closeout** — `…/research/checkpoints/2026-05-13-10-civilization-landscape-investigation-closeout.md` (U7/U8 update set crediting Hermes plugins and Hermes self-evolution; routed through [[civilization-landscape-investigation]] this run).
- **Fork metadata (live, 2026-06-13)** — GitHub API: `repos/transpara-ai/hermes-agent` (`isFork=true`, `parent=NousResearch/hermes-agent`, `createdAt=2026-05-11T11:32:53Z`, `description="The agent that grows with you"`, MIT); `repos/transpara-ai/hermes-agent-self-evolution` (`parent=NousResearch/hermes-agent-self-evolution`, `createdAt=2026-05-11T11:32:06Z`, `description="… Evolutionary self-improvement for Hermes Agent — optimize skills, prompts, and code using DSPy + GEPA"`); `repos/transpara-ai/hermes-example-plugins` (`parent=NousResearch/hermes-example-plugins`, `createdAt=2026-05-13T03:42:39Z`, MIT).
- **Upstream (context only, not re-published)** — `github.com/NousResearch/hermes-agent`, `…/hermes-agent-self-evolution`, `…/hermes-example-plugins` (https://github.com/NousResearch/hermes-agent) — descriptions and MIT licensing corroborated via the fork metadata above, cited as context for the fork, not mirrored.
- **Released internal evaluation** — `/Transpara/transpara-ai/repos/docs/civilization/v4.1/implementation/epics/epic-15-institutional-substrate-doctrine/corpus/copied/civilization/knowledge/external-landscape/hermes-agent-self-evolution/TAI-RES-2026-002-v1.0.0-Hermes-Agent-Self-Evolution-Evaluation.md` — confirms prior decisions and adds the Capability Evolution comparison; advisory, not accepted doctrine.
- **Open Brain** — adversarial-review capture on docs PR #61 (2026-05-18) recording that the pattern-only adoptions including Hermes landed with **no upstream-refresh mechanism documented** (only Karpathy LLM Wiki had a freshness cadence).

**Conflicts / open items.** (1) *One row vs. three decisions* — the crosswalk's single "Hermes / pattern-only / deferred" row vs. the Phase 5 matrix's three distinct rows (runtime-adapter / plugin-reference / capability-optimizer); stated, not resolved. (2) *License* — README-MIT vs. PLAN's AGPL-v3 "Darwinian Evolver" path in the self-evolution repo; both stated. (3) *Fork date* — 2026-05-11 for the two named repos vs. 2026-05-13 for example-plugins. (4) *Repo-internals confidence is thin* — README/PLAN only, no code read, this run or in the original investigation. `[[civilization-landscape-investigation]]`, `[[dark-factory]]`, `[[capability-evolution]]`, `[[runtime-broker]]`, `[[work]]`, `[[base-slice-0]]`, `[[paperclip]]`, `[[memory-knowledge-advisory]]`, and `[[event-graph]]` resolve to compiled articles; `[[v3-9]]` likewise.
