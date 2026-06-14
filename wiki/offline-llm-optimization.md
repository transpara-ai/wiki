---
entity: Offline LLM Optimization
aliases:
  - offline LLM optimization
  - offline models
  - offline open-weight deployment
  - results-per-external-dollar
tier: concept
status: compiled
last_compiled: "2026-06-14"
sources:
  - raw/open-brain/2026-06.md  # 2026-06-01 thought (OB entry ~L201): "open-weight (and self-hostable) models are fundamental to the long-term ARC of the effort"; "maximize achievable results while minimizing EXTERNAL SPEND" — strategic framing correction capture
  - raw/open-brain/2026-06.md  # 2026-06-01 thought (~L195): DF-V3.9.3 open-weight/pi.dev/OpenRouter doc as context; air-gap fit and self-hostable models as cost + enterprise dimension; "open-weight integration is NOT due in any current Epic — it is strategic direction, not present scope"
  - raw/transpara/dark-factory/research/DF-V3.9-OPEN-WEIGHT-LLM-ROUTING-PI-HARNESS.md  # Background §, Definitions §, Non-Goals §, Route-by-Decision-Kind table, Risk Register — the implementation design doc that governs the first concrete step toward this future state
confidence:
  sources: thin
  claims: asserted
---

# Offline LLM optimization

**The long-arc strategic direction behind [[open-weight-llm-routing]].** Offline LLM optimization is the goal, not yet a milestone, of replacing hosted (API-paid) frontier models with locally-served open-weight models for the bounded sub-tasks they can handle at acceptable quality. The objective is systemic: *maximize achievable results while minimizing external spend.* Every LLM call that can be moved off a paid API endpoint and onto self-hosted infrastructure is a permanent reduction in per-unit cost that compounds as volume grows.

This entity is a **future-timeline concept**, not a shipped feature. The nearest concrete step toward it is the v3.9 [[open-weight-llm-routing]] harness (the `df-model-broker` + [[open-weight-llm-routing|Pi selector]] design). Offline model deployment is the horizon that router is aimed at, but the two are distinct: the router handles hosted open-weight routes first; fully offline (self-hosted on local infrastructure) is a later phase reached only after per-route evidence has accumulated.

> ⚠ **Evidence note.** The primary grounding for this entity is a single Open Brain strategic-framing capture from 2026-06-01 (OB ~L201) in which Michael Saucier corrected the planning direction for the `DF-V3.9-OPEN-WEIGHT-LLM-ROUTING-PI-HARNESS.md` work. The design doc itself (DF-V3.9-OPEN-WEIGHT-LLM-ROUTING-PI-HARNESS.md) treats self-hosting as a supporting option rather than the primary goal. No separate "offline LLM optimization" design document exists in the raw corpus as of this compile. Claims in this article are therefore **asserted** from primary-direction context, not grounded in a dedicated specification.

## The results-per-external-dollar principle

The organizing idea, stated directly in the Open Brain capture (2026-06-01): the production civilization's objective is *"to maximize achievable results while minimizing EXTERNAL SPEND, which is why open-weight (and self-hostable) models are fundamental to the long-term ARC of the effort."* This is distinct from the narrower performance question of which model is best — it is a unit-economics question about which model produces acceptable results at the lowest marginal cost at a given volume, with the explicit sub-goal of driving external cost toward zero for commodity sub-tasks.

The principle follows from a structural property of the civilization executor: it generates *many* LLM calls, and many of those calls are not complex enough to require frontier-model quality. If the sub-task is bounded — classify this, extract that, summarize this, pick the next tool — then a model that can do it adequately and runs on internal hardware dominates a frontier API call on every economic dimension: per-call cost, data-policy exposure, air-gap compatibility, and latency predictability.

## LLM assignments are pluggable

The design principle established by the [[open-weight-llm-routing]] architecture is that model assignments are **pluggable by route** rather than global. This makes offline optimization tractable: you do not need one open-weight model that beats Opus across the board. You need a candidate that beats the current route on its specific sub-task at the quality gate for that route. The boundary is: *can this model solve THIS sub-task at the required quality?*

The [[open-weight-llm-routing]] design formalizes this as decision kinds — `tool_call`, `plan`, `code_patch`, `validator`, `summarizer`, `extraction`, `classification` — each with its own promotion gate, risk tier, and fallback. An offline model can be promoted for `summarizer` while the same route's `code_patch` still runs on a frontier model. Progress is granular and reversible; offline deployment is the status a route reaches at the end of the broker's promotion pipeline, not a global switch.

## Gradient auto-research loop (future capability)

> ⚠ **Thin evidence.** The following is inferred from the design doc's evaluation architecture ([DF-V3.9-OPEN-WEIGHT-LLM-ROUTING-PI-HARNESS.md], Milestone 0–5 and Evaluation Design §), not described explicitly as an "auto-research loop" in any source document. Label: **reconstructed intent.**

The long-arc mechanism for finding offline candidates is the [[open-weight-llm-routing]] evaluation pipeline used continuously rather than once: the civilization records production traces → the [[open-weight-llm-routing|Pi harness]] replays those traces against new model candidates → promotion reports land in the registry → human-reviewed promotion or rejection closes the loop. Over time this becomes a research loop: workload traces accumulate, candidates are benchmarked against them, and the registry keeps pace with the open-weight model ecosystem as newer models clear bars that earlier ones did not.

The design doc is explicit that public benchmarks are *"useful for selection, insufficient for promotion"* — the loop must run on real Dark Factory workload traces, not synthetic benchmarks. This is the quality safeguard that separates continuous research from arbitrary model substitution.

## Early targets and protected routes

The [[open-weight-llm-routing]] route table identifies which decision kinds are most tractable for open-weight (and by extension offline) substitution:

**Tractable early targets:**
- Embedding generation — high-volume, well-specified, robust local solutions exist today
- Classification and routing — bounded-output, rule-checkable, low risk on wrong answer (can escalate)
- Summarization (`summarizer` route) — MiniMax, DeepSeek, and Qwen are first-wave candidates in shadow mode
- Extraction (`extraction` route) — Qwen and DeepSeek candidates identified
- Internal messaging and annotation — low-stakes, high-frequency, cost-sensitive

These are routes where quality is evaluable by schema validity and task-success metrics, risk of a wrong answer is contained (the system can detect and escalate), and volume is high enough for offline serving economics to dominate.

**Protected routes (not targets for offline substitution):**
- Safety gates and trust arbitration — require frontier-quality judgment with human-review paths; fail-closed posture means errors here have systemic consequences
- Complex multi-step reasoning — long-horizon planning, architecture decisions, authority evaluation; frontier fallback must remain available indefinitely
- Sensitive routes — data-policy and legal exposure; self-hosted is a *privacy improvement* here, but quality must still be frontier-class
- Validation and judging — must be a different family from the generator (cross-family judging mandate); offline judging is possible eventually but requires independent capability proof

The offline optimization arc is a one-directional migration of the tractable set toward local serving, while the protected set retains frontier-fallback routes indefinitely. The two never converge.

## Air-gap fit as a selection criterion

The Open Brain record (2026-06-01) notes that air-gap suitability was an explicit scoring dimension in the agent-pipeline ranking prior to the DF-V3.9 work: *"for air-gapped infra self-hostable open weights gain big on cost + enterprise/air-gap-fit dimensions."* This reflects a constraint shared across the Dark Factory stack — the [[dark-factory]] design principle that *"air-gap is the default constraint"* (CLAUDE.md infrastructure section) means that any model serving path that requires outbound API calls is an architectural dependency that must be eliminated before the system can operate in constrained environments.

For the offline LLM arc, air-gap is both a business requirement (certain deployment targets may prohibit cloud model calls) and a design constraint (the self-hosting infrastructure must be buildable with tools that have offline install paths). Self-hosted inference runtimes listed in the [[open-weight-llm-routing]] design — vLLM, SGLang, Ollama, LM Studio, KTransformers — all satisfy this requirement.

## What this is not

Offline LLM optimization is **not** any of the following:

- A current Epic or near-term deliverable. As of 2026-06-01, it is *"strategic direction, not present scope."* The first concrete step (the model broker and hosted open-weight evaluation) is itself in design/research phase, not implementation.
- A claim that open-weight models can replace frontier models globally. The design is explicit: *"this document does not propose immediate global replacement of frontier models"* (Non-Goals §, DF-V3.9-OPEN-WEIGHT-LLM-ROUTING-PI-HARNESS.md).
- A performance-maximization strategy. It is a unit-economics strategy conditioned on quality gates. A route is only moved offline if it passes the same quality gates it would need to pass for hosted open-weight promotion.
- Separate from [[capability-evolution]]. Model-route assignments, once promoted, are capability artifacts in the dark-factory sense — changing them is governed work flowing through the [[capability-evolution]] chain, with evaluation, human review, and rollback.

## Relationship to adjacent entities

- **[[open-weight-llm-routing]]** — the nearest concrete implementation: the v3.9 `df-model-broker` and Pi selector harness that routes between frontier and open-weight models. Offline LLM optimization is the long-arc goal; that routing infrastructure is the first step.
- **[[capability-evolution]]** — route promotions (including offline promotions) are governed capability changes, flowing through EvolutionOrder → BenchmarkResult → HumanReview → CapabilityVersion → ActivationPolicy → rollback.
- **[[runtime-broker]]** — the runtime envelope that confines execution. Self-hosted model calls run through the broker like any other provider; the broker's validation and policy enforcement apply regardless of whether the model is hosted or local.
- **[[dark-factory]]** — the parent system whose "results-per-external-dollar" objective motivates this arc.

## Sources & provenance

Primary grounding:
- `raw/open-brain/2026-06.md` approximately L195–L207 (2026-06-01 captures): strategic-framing correction ("open-weight (and self-hostable) models are fundamental to the long-term ARC"); air-gap-fit and cost-dimension scoring context; explicit scope statement ("NOT a current Epic — strategic direction, not present scope"); relationship of the periodic-run ranking tool as a *selection prior* to the DF-V3.9 *promotion authority*.
- `raw/transpara/dark-factory/research/DF-V3.9-OPEN-WEIGHT-LLM-ROUTING-PI-HARNESS.md` (DF-V3.9-OPEN-WEIGHT-LLM-ROUTING-PI-HARNESS, v3.9.3, status: review, canonical: false, created 2026-06-01) — Background §, Non-Goals §, Route-by-Decision-Kind table, self-host adapter stubs, Risk Register, Milestone 0–5 gates, Evaluation Design §. Read in full.
- Open Brain marker `OB1-OFFLINE-LLM-2026-06-14T00:00:00Z` — the thought that seeded this article's compile. The marker was provided as an instruction input; a live read-back via `list_thoughts` was not performed during this session. Treat as **asserted, not read-back-verified.**

**Confidence assessment:** `sources: thin` — no dedicated design specification for offline LLM optimization exists in the raw corpus. The article is synthesized from a single strategic-direction capture (Open Brain 2026-06-01), the related implementation doc (DF-V3.9-OPEN-WEIGHT-LLM-ROUTING-PI-HARNESS.md), and inference from the dark-factory infrastructure constraint. `claims: asserted` — the future-timeline framing, the gradient loop description, and the target/protected-route split are inferred from design intent, not documented as a separate plan.
