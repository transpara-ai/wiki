---
entity: Base Slice 0 (Control-Plane Proof)
aliases: [base-slice-0, base slice 0, the control-plane proof, v3.9 base slice 0]
tier: arc
status: compiled
last_compiled: 2026-06-15
sources:
  - raw/transpara/dark-factory/Dark Factory - Motive, Goal, Approach.md  # "Base Slice 0 Flow", L232-253; orientation
  - raw/transpara/dark-factory/v3.9/README.md  # "Current First Implementation Target", L87-108; Base Rule, L66-85
  - raw/transpara/dark-factory/v3.9/04-production-workflow-and-runtime-v3.9.md  # "Base Slice 0", L143-164 (DF-V3.9-SPEC-004) — normative definition
  - Open Brain thought 2026-05-14  # eventgraph PR #34 — TraceCompletenessGate + FactoryRuntimeVersion/BOM implemented
  - Open Brain thought 2026-06-13  # civilization-wiki gates.md compilation note (gate-class synthesis)
confidence:
  flow_definition: high (three first-party docs agree on the node chain)
  exclusion_list_wording: medium — three sources phrase the exclusion list slightly differently; reconciled below
  pass_state_at_compile: thin — whether the local-worker Base Slice 0 has actually run green is not stated in the sources read this run; the gate machinery exists in code (eventgraph#34) but a passing Base-Slice-0 run is asserted-as-target, not proven-as-done here
---

# Base Slice 0 (Control-Plane Proof)

**Base Slice 0 is the floor of the [[dark-factory]] pyramid** — the mandatory end-to-end control-plane proof that must run *before* any higher autonomy is permitted. It is the first implementation target of Dark Factory v3.9, which "rationalized" it from the older v3.1 vertical slice (`Dark Factory - Motive, Goal, Approach.md`; `v3.9/README.md`, L87-89). v3.9 itself was accepted canonical on 2026-06-05 (`v3.9/README.md`, L38). Base Slice 0 is not a feature the factory ships to a customer; it is the factory proving, on itself, that the accountability chain holds before it is trusted with anything harder.

## What it is

Base Slice 0 is one full pass through the Dark Factory control plane, carrying a human goal from order to audit while leaving evidence at every step. The normative node chain (from `v3.9/04-production-workflow-and-runtime-v3.9.md`, the production-workflow spec, L143-164) is:

```text
FactoryOrder
  -> Requirement
  -> AcceptanceCriterion
  -> Task
  -> local deterministic worker
  -> Artifact
  -> TestCase
  -> TestRun
  -> GateResult
  -> TraceCompletenessGate
  -> FactoryRuntimeVersion
  -> ReleaseCandidate
  -> Certification or Rejection
  -> AuditReport
```

All three first-party documents read this run reproduce this exact chain — the orientation doc (L232-253), the v3.9 README's "Current First Implementation Target" (L87-108), and the production-workflow spec (L143-164). On the *shape of the flow* the sources do not conflict.

The point of the slice is to exercise the whole [[event-graph]] truth substrate, the [[acceptance-criteria]] decomposition, the [[bounded-runtime]] execution boundary, the verification [[gates]] (including [[trace-completeness-gate]]), and the certify-or-reject decision — with the simplest possible payload, so that any failure is a failure of the *control plane*, not of the work it is governing.

## Why it exists: prove the base before climbing

Dark Factory's governing rule is "build the base of the pyramid first" (`v3.9/README.md`, L66-85). The README lays out the layer order — document governance → EventGraph truth → authority/identity gates → FactoryOrder and Work DAG → bounded runtime → trace completeness → verification and audit → operator review → SaaS generation → memory and knowledge → governed capability evolution → broader autonomy — and states: **"No higher layer may start when its prerequisite control layer is incomplete."** Base Slice 0 is the proof that the lower control layers actually function, end to end, before the higher ones are switched on.

This is the same fail-safe-by-default posture the arc inherits from its origins: the permissive outcome (more autonomy, real generation, external runtimes) must be the *explicitly-proven* branch, never the default. Base Slice 0 is where that proof is paid.

## The seven prohibitions

Base Slice 0 is defined as much by what it must *not* do as by what it does. The production-workflow spec (L164) states the slice "must not use LLM planning, real SaaS generation, external runtimes, production deploy, multi-agent orchestration, memory recall, knowledge reuse, or capability evolution."

Each prohibition removes a source of non-determinism or unaccountable power so that the control plane can be proven in isolation:

- **No LLM planning** — planning is deterministic, so a failed trace is a control-plane bug, not a model's bad day.
- **No real SaaS generation** — the worker produces a trivial artifact, not a real product, so the slice tests provenance and gates, not code quality.
- **No external runtime** — execution runs only through the **local deterministic worker**. External runtimes (Hermes, OpenManus, Codex, CI, etc.) are deferred until this worker proves traceability, policy, and audit. The spec is explicit: "No external runtime adapter is eligible until the local deterministic worker passes Base Slice 0" (`v3.9/04`, L196; the local-deterministic-first rule also at orientation L167).
- **No production deploy** — deployment is a protected action requiring authority; it is excluded by default ([[authority-request|protected action]]).
- **No multi-agent orchestration** — a single bounded actor, so coordination cannot mask a broken trace.
- **No memory recall / knowledge reuse** — [[memory-knowledge-advisory]] is advisory-only and is kept out entirely, so nothing influences the run without leaving evidence.
- **No capability evolution** — the factory does not self-modify during the proof of its own floor ([[capability-evolution]]).

> ⚠ **Fail-legible note — exclusion-list wording differs across sources.** The three first-party docs phrase the prohibition list slightly differently, though they agree in substance:
> - **SPEC-004** (normative, L164): "LLM planning, real SaaS generation, external runtimes, production deploy, multi-agent orchestration, memory recall, knowledge reuse, or capability evolution."
> - **Orientation doc** (L253): same list, but "external runtime" (singular) and "production deployment."
> - **v3.9 README** (L108): a *shorter* list — "LLM calls, real SaaS generation, external runtime integration, production deploy, multi-agent planning, or capability self-evolution." The README **omits explicit memory recall and knowledge reuse**, and says "multi-agent **planning**" where the spec says "multi-agent **orchestration**."
> Treat the production-workflow spec (SPEC-004) as authoritative for the exclusion set, per the source hierarchy (code/spec > README). The README's omission of memory/knowledge is most likely abbreviation, not a deliberate relaxation, but it is a real wording gap and is flagged here rather than silently smoothed over.

## The gates at the end of the chain

The back half of the chain is the verification spine that turns work into a certifiable (or rejectable) release:

- **GateResult / TestRun** — every TestCase produces a TestRun and a GateResult; these are the raw evidence the release gates consume.
- **[[trace-completeness-gate]]** — blocks certification when FactoryOrder, FactoryRuntimeVersion, acceptance evidence, required gate evidence, unresolved high/critical failures, or certification evidence is missing (orientation L179). A certified release requires a trace score of 1.0 (orientation, Section E, L440).
- **FactoryRuntimeVersion / BOM** — records the active capabilities, runtimes, policies, templates, and commits behind the run; a missing BOM blocks certification (orientation L441).
- **ReleaseCandidate → Certification or Rejection** — a candidate is never certified merely because a model, worker, or human says it is good; certification requires trace completeness, gate evidence, runtime BOM evidence, and audit evidence (orientation L176-179).
- **AuditReport** — the final durable record of the run; it must exist before certification (orientation L442).

The decision is deliberately two-valued and fail-closed: **certify** is the proven branch; anything short of full evidence is a **rejection**, not a silent pass. This mirrors the broader [[gates]] design.

These gates are not just paper. The TraceCompletenessGate and FactoryRuntimeVersion/BOM enforcement were implemented in `transpara-ai/eventgraph` PR #34 (reviewed 2026-05-14, branch `stage-5-v39-trace-runtime-bom`), under a "store records facts, gate evaluates evidence chains" model — BOM evidence is checked at the evaluation layer, not the schema layer, so the store can hold a bare FactoryRuntimeVersion while the gate is what refuses to certify without the BOM. *(Source: Open Brain thought, 2026-05-14, eventgraph#34 review.)*

## Status: target asserted, full green run not proven here

Base Slice 0 is described in every source as the *first implementation target* and the *mandatory* precondition. What the sources read this run do **not** establish is that a local-deterministic Base Slice 0 has actually executed and certified green end to end.

- The gate machinery exists in code (eventgraph#34, above).
- The v3.9 orientation's autonomy register notes that v3.9 "records bounded completions through Gate J and Epic 10" with later epics still under review (`Dark Factory - Motive, Goal, Approach.md`, L351) — but those lettered Gates A-J are the v3.9 *accountability-pipeline build milestones delivered as bounded fixtures*, a **different** vocabulary from Base Slice 0 itself (see the [[gates]] article for the A-J vs K/L distinction). The orientation doc explicitly says it "is not the current-state register" and points to the state-of-the-system proof and as-built tracker for actual gate status (L350-351).

> ⚠ **Fail-legible note — do not conflate Base Slice 0 with "Slice 1".** Open Brain contains extensive 2026-06 history for a *"Reunification Slice 1 / Shepherd the Society"* effort in the `hive`, `work`, and `site` repos (FactoryOrder wiring, a roles-catalog production run, Gate-E draft-PR approval). That is a **separate** concrete build slice and is **not** the architectural Base Slice 0 (the control-plane proof) defined in the v3.9 spec. They share FactoryOrder/EventGraph vocabulary but are different objects; this article does **not** import Slice-1 run history as evidence about Base Slice 0's status. Treat any claim that "Base Slice 0 has run green" as **thin / unverified** until the state-of-the-system proof is read directly.

## What grows from it

Base Slice 0 is the gate to everything downstream. Only after it passes do the deferred capabilities unlock, in roughly the README's layer order:

- **Real generation** → the constrained SaaS Template v1 (Next.js + FastAPI + Postgres via Docker Compose, dry-run/preview only; production deploy and payments excluded) — see [[saas-template-v1]].
- **External execution** → RuntimeBroker adapters, each of which must pass its own conformance checklist (file/command/network/secret boundaries, artifact capture, receipt emission, replayability) before use ([[runtime-broker]]).
- **Higher autonomy** → multi-agent orchestration, advisory [[memory-knowledge-advisory]], and governed [[capability-evolution]] — and ultimately the v4.0 doctrine of the factory building the factory ([[v4-0|v4.0]]).

The asymmetry is deliberate: a stalled Base Slice 0 costs one recoverable unit of work; a Base Slice 0 waved through would let every higher, riskier layer run ungated. The arc pays the safe side.

## Run-3 update (2026-06-14)

**Round 6 result (v16) — "first society to finish", gate requirement not yet satisfied.**

Round 6 (`codex/fo-roles-catalog-v16`, HEAD `002bcf8`) closed 2026-06-12 as `finished-unsignalled`: the society ran 45 minutes unattended, sealed a 1128-event chain, and produced a 9-role v2.0.0 catalog deliverable. The arc recorded this as the first time the society reached terminal quiescence with a pushed artifact branch — milestone language: "first society to finish."

However, the gate requirement (zero-blocker delivery) is **not yet satisfied.** Finding F1 (`v16-F1`): all six reviews conducted during round 6 were premised on the wrong repo cwd — the reviewer (eventgraph `claude_cli.go` Operate path) verified in the daemon's working directory all round instead of the target workspace, so none of the six reviews count as the FO's zero-blocker gate in the FO's sense. The deliverable branch is pushed and the catalog is now canonical (`status: active` as of 2026-06-14), but the v16-F1 defect means the FO's review-gate was not cleared by round 6 itself.

Additional findings from v16: F2 — planner decomposition silently narrowed FO scope, causing a 24→9 role ping-pong across 6 completions; F3 — terminal quiescence has no exit/signal/run-completion, and escalations demand "Human/CTO judgment" with no channel to receive one.

**Gate-E hard stop resolved (2026-06-15).** After round 6 the arc reached its hard stop: Gate-E (or a new grant) awaited Michael's review. On 2026-06-15 the External Committee resolved it by granting **Event-1** (v4.0 Gate-K interim loop hardening; decision *Notify*, `transpara-ai/docs#132`), not a new slice-1 grant. Gate-K itself remains defined and unsatisfied (AC-K5 data-handling attestation pending — docs#137).

The v16 fix-set scope (candidate): F1 WorkDir threading (`hive pkg/loop` + eventgraph provider), F2 spec-diff gate at subtask creation, F3 quiescence detector → `hive.run.completed` + human-decision channel.

**Relationship to Base Slice 0.** The Reunification Slice-1 run history (rounds 1–6, grant-1 and grant-2) confirms that FactoryOrder wiring, EventGraph truth-substrate, and the GateResult/TraceCompletenessGate machinery are exercised in production. The fail-legible note below (do not conflate Slice-1 with architectural Base Slice 0) remains in force: round-6 completion is evidence that the vocabulary and infrastructure are live, not a proof that the minimal control-plane Base Slice 0 (no LLM, no external runtime, no SaaS generation) has run green end-to-end in its spec-defined form.

**Sources for this update:** `raw/transpara/dark-factory/reunification/2026-06-12-arc-state.md` (DF-REUNIFY-2026-06-12-ARC-STATE, v0.3.0).

## Sources & provenance

Compiled this run from first-party Dark Factory documents in `transpara-ai/docs`:

- **`Dark Factory - Motive, Goal, Approach.md`** — "Base Slice 0 Flow" (L232-253), product-work flow (L214-230), TraceCompletenessGate / gate-class register (L176-181, L424-442), autonomy/gate posture (L349-351), and the local-deterministic-first runtime rule (L167).
- **`dark-factory/v3.9/README.md`** — "Base Rule" / pyramid layer order (L66-85) and "Current First Implementation Target" (L87-108), with the v3.9 acceptance date (L38).
- **`dark-factory/v3.9/04-production-workflow-and-runtime-v3.9.md`** (DF-V3.9-SPEC-004) — the **normative** "Base Slice 0" definition and exclusion list (L143-164) and the RuntimeBroker adapter-eligibility rule (L196).
- **Open Brain** — thought of 2026-05-14 (eventgraph PR #34: TraceCompletenessGate + FactoryRuntimeVersion/BOM implementation) and thought of 2026-06-13 (the civilization-wiki `gates.md` compilation note on gate-class vocabulary). The Open Brain "Reunification Slice 1" thoughts were reviewed and **deliberately excluded** as evidence about Base Slice 0, per the fail-legible note above.

The originating failure-tracing philosophy behind the whole accountability chain traces to Matt Searles, "20 Primitives and a Late Night" (`Searles-P1`, https://mattsearles2.substack.com/p/20-primitives-and-a-late-night) — see [[the-20-primitives]]. No source conflict on the Base Slice 0 *flow*; the only discrepancy is the exclusion-list wording (flagged above). `[[wikilinks]]` are forward references; most targets are not yet compiled.
