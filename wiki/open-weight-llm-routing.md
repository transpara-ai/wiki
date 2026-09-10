---
entity: Open-Weight LLM Routing (v3.9 Pi/Selector Harness)
org: transpara-ai
primary_placement: civilization/architecture
placements:
  - civilization/architecture
classification: internal
aliases:
  - open-weight LLM routing
  - df-model-broker
  - model broker
  - Pi harness
  - pi.dev harness
  - model routing
  - DF-V3.9-OPEN-WEIGHT-LLM-ROUTING-PI-HARNESS
tier: architecture
status: compiled
last_compiled: "2026-06-14"
sources:
  - raw/transpara/dark-factory/research/DF-V3.9-OPEN-WEIGHT-LLM-ROUTING-PI-HARNESS.md  # full document read — doc_id DF-V3.9-OPEN-WEIGHT-LLM-ROUTING-PI-HARNESS, v3.9.3, status review, canonical false, created 2026-06-01; all sections
  - raw/open-brain/2026-06.md  # ~L195: "DF-V3.9.3 open-weight/pi.dev/OpenRouter doc governs how open-weight LLMs are added to Dark Factory" — summary capture 2026-06-01; ~L201: strategic framing correction (parallel task, not main line; strategic direction not current Epic); ~L486: "deferred DF-V3.9.3 open-weight hive harness arc ... scopes pi as an eval harness, explicitly 'not the primary production path'"
confidence:
  sources: primary
  claims: grounded
---

# Open-weight LLM routing (v3.9 Pi/selector harness)

**The architecture for introducing open-weight models into the Dark Factory civilization executor without replacing frontier routes wholesale.** The v3.9 open-weight LLM routing design, specified in `DF-V3.9-OPEN-WEIGHT-LLM-ROUTING-PI-HARNESS.md` (version 3.9.3, status: review, canonical: false, 2026-06-01), defines a three-layer system: a `df-model-broker` that owns runtime routing and policy; OpenRouter as the first hosted provider abstraction; and a `pi.dev` harness (`df-pi-harness`) for trace-replay evaluation, model sweeps, and promotion reporting. The central design decision — stated at the top of the document — is that open-weight models enter through the broker, not through direct call-site replacement.

This is the implementation architecture that the [[offline-llm-optimization]] long-arc goal depends on. It is **design-phase research, not an accepted implementation packet** — the document's own front matter sets `canonical: false` and `status: review`.

## The three-layer invariant

The load-bearing architecture is expressed as a single invariant:

```text
Production path:
  Dark Factory -> df-model-broker -> OpenRouter / direct provider / self-host / frontier fallback

Harness path:
  pi.dev -> Dark Factory replay package -> same model registry -> scorer -> promotion report
```

The three actors have distinct, non-overlapping roles and share one artifact: the model registry.

| Layer | Role | What it does NOT do |
|---|---|---|
| `df-model-broker` | Runtime owner: classify, route, validate, trace, escalate, promote | Does not run evaluation or sweeps |
| OpenRouter | Hosted provider abstraction: model discovery, shadow sweeps, canary routing, provider policy | Does not own runtime policy or promotion |
| `pi.dev` (`df-pi-harness`) | Harness: trace replay, model sweeps, CI evaluation, promotion reports | Is not the production hot path |

The registry (three files: `model-registry.dark-factory.json`, `route-policy.dark-factory.json`, `promotion-gates.dark-factory.json`) generates two artifacts: a production routes JSON consumed by the broker, and a Pi `models.json` consumed by the harness. This shared source ensures the harness evaluates the same route configuration that production runs.

## The model broker (`df-model-broker`)

The broker is the single call path for every Dark Factory LLM decision. Existing frontier routes (Opus, Sonnet, Haiku, GPT-5.5 Codex) are wrapped first so current behavior is preserved before candidates are introduced. Every request is classified on six dimensions before routing:

| Field | Examples |
|---|---|
| Decision kind | `tool_call`, `plan`, `code_patch`, `validator`, `summarizer`, `repair`, `classification`, `extraction` |
| Risk tier | `low`, `medium`, `high`, `sensitive` |
| Side-effect tier | `none`, `read`, `write`, `destructive` |
| Required capabilities | tools, structured output, long context, image input, reasoning, code execution |
| Budget | max cost, max latency, max tokens, max tool calls |
| Data policy | hosted allowed, ZDR required, self-host required, provider allowlist |

Routing is by **decision kind**, not by a global model ranking. A model that is strong for `summarizer` is evaluated separately from its performance on `code_patch` or `agent.long_horizon`. The broker also owns structured-output validation (strict JSON or tool-call schema, rejection of invalid tool arguments), retry and repair, escalation to frontier fallback, and full trace capture. Every response records model used, provider kind, token usage, latency, cost estimate, and validation result.

The broker request and response are strongly typed (TypeScript interfaces reproduced in the design doc). The request carries `trace_id`, `decision_kind`, `risk_tier`, `messages`, `tools`, `response_schema`, `constraints`, and `fallback_policy`. The response carries `route_id`, `model_used`, `provider_kind`, `provider_name`, `parsed_json`, `tool_calls`, `usage`, `latency_ms`, `validation`, and an `audit` block (prompt hash, tool schema hash, response schema hash, model registry version, timestamp).

### Route table (first wave)

The design specifies route-by-decision-kind, not a global preference:

| Decision kind | Primary open-weight candidates | Frontier fallback |
|---|---|---|
| Low-risk tool selection | DeepSeek, Qwen, MiniMax | Haiku or Sonnet |
| Long-horizon orchestration | Kimi, GLM, DeepSeek | Opus, Sonnet, or GPT-5.5 Codex route |
| Code patching | Qwen Coder, GLM, Kimi | GPT-5.5 Codex route or Sonnet |
| Summarization | MiniMax, Qwen, DeepSeek | Haiku |
| Extraction | Qwen, DeepSeek, MiniMax | Haiku or Sonnet |
| Validation / judging | Different family from generator | Frontier judge |
| Sensitive routes | Approved self-hosted or approved frontier | Human review |

All first-wave routes enter as `shadow` (candidate runs beside production, output does not affect state) before any canary or promotion. The five first-wave families are Kimi (Moonshot), DeepSeek, Qwen (Alibaba), GLM (Z.ai), and MiniMax.

## The Pi harness (`df-pi-harness`)

`pi.dev` is included as a **harness, not as the default execution mechanism**. The production civilization executor calls the broker directly; Pi is the evaluation plane that validates candidates before they reach the broker's canary or promotion stages.

Pi's defined uses:

| Use | Required behavior |
|---|---|
| Trace replay | Re-run recorded Dark Factory model calls with side effects mocked |
| Model sweeps | Run the same trace set across all candidate families |
| Prompt experiments | Compare system prompts, schemas, context-packing strategies |
| Coding-agent jobs | Sandboxed code-editing tasks against candidate models |
| CI evaluation | Machine-readable pass/fail output for promotion gates |
| Provider parity testing | Test OpenRouter, direct provider, and self-hosted routes through the same registry |
| Regression detection | Schema drift, invalid tool calls, cost/latency regressions, prompt drift |

The `df-pi-harness` package layout is specified in the design doc: a `skills/dark-factory-replay/` skill (with `replay-trace.ts`, `score-result.ts`, `compare-routes.ts`), prompt templates per decision kind, `src/` runners (load-trace, mock-tools, run-sweep, score-trace, emit-report, registry-to-pi-models), and a `fixtures/traces/` set (low-risk tool call, code patch, long-horizon agent).

Pi consumes generated `models.json` from the registry exporter, not a hand-edited list. This is the mechanism that keeps Pi and production in sync: the same registry entry that defines a route in the broker also generates the Pi model configuration.

## OpenRouter as the first hosted adapter

OpenRouter is specified as the first hosted routing layer because it provides a unified endpoint for many models plus provider-level routing controls (provider allowlists, data-collection policy, cost/latency sorting, tool-support filtering). Dark Factory uses it for:

- Hosted model discovery and fast model trials
- Shadow-mode sweeps and low-risk production canaries
- Provider fallback when allowed
- Data-policy restrictions (deny providers that may store prompts)
- Tool-support and structured-output enforcement

OpenRouter is not the only path — direct provider adapters (per-family) and self-hosted adapters (vLLM, SGLang, Ollama, LM Studio, KTransformers) remain available for cost, privacy, latency, redundancy, or air-gap reasons. For offline/self-hosted deployment (see [[offline-llm-optimization]]), the self-hosted adapter path is the production route.

### Required schema for tool decisions

The broker mandates a strict JSON schema for every tool decision output, with `additionalProperties: false` and a fixed required-field set: `decision_type` (enum: `call_tool`, `ask_clarification`, `skip`, `escalate`), `tool_name`, `arguments`, `expected_observation`, `confidence` (0–1), `risk_notes`, `escalation_reason`. Any output that fails schema validation, names an unavailable tool, or provides invalid arguments is rejected and triggers repair or escalation — it never reaches production state.

## Evaluation and promotion gates

Promotion follows a five-stage pipeline with hard gates:

| Stage | Minimum traces | Required scope |
|---|---:|---|
| Smoke | 25 | One route, low-risk only |
| Shadow Alpha | 100 | Representative traces, one decision kind |
| Shadow Beta | 500 | Multiple decision kinds, multiple families |
| Canary Readiness | 2,000 | Production-like mix, cost and latency included |
| Promotion Review | 5,000+ | Route-specific, including edge cases and failure traces |

A route may be promoted only if all of:

```text
success_rate(candidate) >= success_rate(frontier_baseline) - allowed_delta
schema_valid_rate >= 99.5%
invalid_tool_arg_rate <= 0.5%
safety_violation_rate == 0
cost_per_success <= 40% of current OR quality_delta is materially positive
p95_latency <= route latency budget
escalation_rate <= route escalation budget
regression_count == 0 for blocker regressions
```

Public benchmarks are *"useful for selection, insufficient for promotion."* Only trace-replay and shadow data authorize promotion. Cross-family judging is mandated — the judge model must come from a different family than the generator.

Promotion is **route-specific and reversible**: a model promoted for `tool_call.low_risk` is not thereby promoted for `agent.long_horizon`. The design calls the shared registry entry the carrier of promotion state; a canary route entry sets `canary_percent` low (starting at 1% or lower for low-risk routes) with a kill switch that can revert by route and provider immediately.

## Implementation milestones

The design defines five gated milestones:

| Milestone | Deliverable | Key gate condition |
|---|---|---|
| 0: Registry & trace normalization | Shared registry, route policy, trace schema, trace recorder | 100+ normalized historical traces; trace replay produces no real side effects |
| 1: Model broker skeleton | `df-model-broker` with OpenRouter, frontier, self-host adapters; validators; escalation engine | Frontier routes still work; OpenRouter runs in shadow; malformed JSON triggers repair; every response records model + provider + validation |
| 2: Pi harness package | `df-pi-harness` package, Pi skill, prompt templates, registry exporter, trace/sweep runners, report emitter | Pi can run one trace through OpenRouter and one through a local OpenAI-compatible endpoint; Pi and broker use same route IDs |
| 3: Shadow mode | Candidate execution beside production; cross-family judging; failure taxonomy | 500+ traces; three+ families per route; no candidate output affects production state |
| 4: Canary | Traffic allocation, kill switch, live monitoring, audit logging, human review queue | 1% or lower start; schema validity >= 99.5%; no blocker safety regressions |
| 5: Route promotion | Promotion decision per route, registry update, frontier fallback, drift monitor | Promotion is route-specific; frontier fallback remains; license and data-policy review complete |

As of the document date (2026-06-01) and the strategic-framing capture (2026-06-01), **this milestone sequence is design-phase.** No milestone is stated as complete. The Open Brain record is explicit: *"open-weight integration is NOT due in any current Epic — it is strategic direction, not present scope."*

## Risk register (key items)

| Risk | Mitigation |
|---|---|
| Invalid tool calls causing bad state | Strict schema, tool-arg validation, repair before state write, escalation |
| Tool-call loops exploding cost | Per-route tool budgets, loop detection, max-call-count enforcement, fallback |
| Benchmark illusion (public benchmarks overstate DF-trace value) | Promote only from trace-replay and shadow data, never from public benchmarks alone |
| Provider instability | OpenRouter fallback, direct adapters, self-host fallback, kill switch |
| Data-policy mismatch | Provider allowlists, data-collection controls, self-host routes, sensitive-route blocking |
| Licensing ambiguity | License verification gate before open-weight production classification |
| Self-host cost surprise | Measure cost per successful trace, not nominal hardware cost |

## Relationship to adjacent entities

- **[[offline-llm-optimization]]** — the long-arc future goal this routing architecture is the first step toward. Fully offline (local) deployment is the `self_hosted` provider kind in the broker, reached only after the hosted open-weight stages prove per-route quality.
- **[[capability-evolution]]** — model-route promotions are capability changes in the dark-factory sense; they flow through EvolutionOrder → BenchmarkResult → HumanReview → CapabilityVersion → ActivationPolicy → rollback.
- **[[runtime-broker]]** — the RuntimeBroker envelope that confines all execution, including model calls; the `df-model-broker` is the model-tier analogue of the broader RuntimeBroker concept, owning policy and validation for LLM calls specifically.
- **[[dark-factory]]** — the parent system that defines the "no artifact without provenance, no release without verification" chain; the broker's trace recorder and audit block are the evidence that LLM decisions leave in the [[event-graph]].

## Sources & provenance

Primary source: `raw/transpara/dark-factory/research/DF-V3.9-OPEN-WEIGHT-LLM-ROUTING-PI-HARNESS.md` (doc_id: `DF-V3.9-OPEN-WEIGHT-LLM-ROUTING-PI-HARNESS`, version 3.9.3, status: review, canonical: false, created 2026-06-01, updated 2026-06-01, owner: human, steward: assistant). Read in full this compile session. All TypeScript interfaces, route tables, evaluation sample sizes, promotion rules, milestone gate conditions, and risk register items are drawn from this document.

Supporting context: `raw/open-brain/2026-06.md` approximately L195 (DF-V3.9.3 governance framing, relationship to agent-pipeline-ranking as selection prior, core design recap), L201 (strategic-framing correction: "parallel task, not main line"; explicit "NOT due in any current Epic"), L486 ("deferred DF-V3.9.3 open-weight hive harness arc; Pi scoped as eval harness, not primary production path").

**Status qualification:** the design document's own front matter (`canonical: false`, `status: review`) means this architecture has not been accepted as an operative Dark Factory implementation packet. It is research-phase design. No implementation milestone is recorded as complete in the sources read this compile. `[[wikilinks]]` are forward references; [[runtime-broker]], [[capability-evolution]], [[dark-factory]], and [[offline-llm-optimization]] are compiled wiki entities; [[event-graph]] is the canonical foundational article.
