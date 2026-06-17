---
entity: RuntimeBroker (Bounded Execution Envelope)
aliases: [RuntimeBroker, RuntimeEnvelope, runtime invocation envelope, bounded runtime, bounded execution envelope, BoundedWorker]
tier: architecture
status: compiled
last_compiled: 2026-06-13
sources:
  - raw/transpara/dark-factory/Dark Factory - Motive, Goal, Approach.md  # orientation synthesis, §6 + responsibility map
  - raw/transpara/dark-factory/v3.9/04-production-workflow-and-runtime-v3.9.md  # normative: Runtime Invocation Envelope L166-213, enforcement stages L215-231, RuntimeResult L233-272, selection progression L308-319 [DF-V3.9-SPEC-004]
  - raw/transpara/dark-factory/v3.9/01-unified-architecture-decisions-v3.9.md  # normative: Decision 6 (envelope) L95-99, Decision 7 (local-deterministic-first) L101-105, invariant #4 L204 [DF-V3.9-ADR-001]
confidence:
  envelope_fields_and_checklist: high (read directly from the v3.9 normative spec this run)
  "local deterministic worker is the first and only runtime": high for the design rule; the operational claim that no external adapter has yet been wired traces to Open Brain notes and v3.9 gate posture, not to a live cluster check this run
  adapter_conformance_status: thin — the docs prescribe the gate; whether any adapter has passed it is not asserted by the sources read this run, and the design says none is eligible until Base Slice 0 passes
---

# RuntimeBroker (Bounded Execution Envelope)

RuntimeBroker is the **execution-boundary system** of [[dark-factory]]. In the platform's one-line responsibility map it is the system that *"confines execution"* — the counterpart to [[event-graph]] (which holds truth), [[work]] (which schedules flow), and Hive/governance (which evaluates authority). Every runtime that does real work — a local script, a coding worker, a CI step, an LLM-backed agent, a future external backend — runs **inside** a RuntimeBroker envelope and **never governs**. The architectural slogan from the source doctrine is exact: *"Runtimes do not govern. They execute only through RuntimeBroker envelopes."* ([Dark Factory - Motive, Goal, Approach.md], §6; [DF-V3.9-ADR-001:L95-L99])

It exists to answer one structural problem: an AI agent can *claim* it edited only the right files, ran only safe commands, touched no secrets, and made no network calls — but a claim is not evidence. RuntimeBroker replaces the claim with a **declared, hashed envelope** plus a **post-run receipt**, so that what a runtime was *permitted* to do and what it *actually* did are both recorded in [[event-graph]] and replayable.

This article documents the RuntimeBroker design as written in Dark Factory v3.9 (the operative implementation baseline). It is a **specification entity**, not (yet) a fully-built production system — see *Build status* below for what is asserted versus proven.

## Where it sits in the arc

RuntimeBroker is not part of the originating philosophy. It is the engineering crystallisation of one of [[the-20-primitives]] — the primitive `Operation` / agent action — under the accountability premise. The Motive doc states the lineage directly: *"agent action becomes bounded runtime invocation."* ([Dark Factory - Motive, Goal, Approach.md], Motive section). The same source pairs it with the other primitive-to-architecture conversions: traceability → EventGraph, explicit criteria → AcceptanceCriteria and gates, authority → AuthorityRequest/Decision/Receipt.

It is one of Dark Factory's **selected native systems**, classified *"Selected execution boundary"* with the standing constraint *"Executes inside envelope; does not govern"* and *"External adapters deferred until conformance gates pass."* ([Dark Factory - Motive, Goal, Approach.md], responsibility map).

## The envelope (RuntimeEnvelope)

RuntimeBroker's input is a declared envelope. The exact field set, transcribed from the normative spec ([DF-V3.9-SPEC-004:L168-L190]):

```yaml
runtime_adapter_id: string
runtime_adapter_version: string
factory_runtime_version_ref: string
task_id: string
actor_id: string
authority_decision_ref: string
allowed_files: string[]
denied_files: string[]
allowed_commands: string[]
denied_commands: string[]
network_policy: disabled | restricted | allowed
secrets_policy: none | scoped | explicit
working_directory: string
timeout: string
resource_limits: object
expected_outputs: string[]
output_contract: object
trace_required_paths: string[]
post_run_validation_plan: string[]
```

Two properties make the envelope load-bearing rather than decorative:

- **It binds execution to provenance and authority.** `task_id`, `actor_id`, and `authority_decision_ref` mean a runtime cannot execute detached from the task that justifies it or the [[authority-layer]] decision that permits it.
- **The envelope hash is recorded before execution and is immutable after start.** ([DF-V3.9-SPEC-004:L192]) The permitted scope is frozen and witnessed before any command runs, so it cannot be retroactively widened to match whatever the runtime did.

The MVP defaults are deliberately restrictive: `network_policy` defaults to `disabled` and `secrets_policy` defaults to `none`; command policy must **allowlist** commands by explicit binary and allowed argument patterns. ([DF-V3.9-SPEC-004:L231]) This is the platform's fail-closed posture applied to execution — capability is the explicitly-granted branch, denial is the default.

## What comes back (RuntimeResult)

The broker normalises every runtime's output into a `RuntimeResult` / `BoundedWorker` record ([DF-V3.9-SPEC-004:L233-L253]) carrying `exit_status` (one of `succeeded | failed | timed_out | policy_blocked`, or an integer), `stdout_ref`/`stderr_ref`, `artifact_refs`, `changed_files`, and — crucially for audit — a `command_log`, `network_access_log`, `secret_access_log`, `policy_decision_refs`, and `post_run_validation_refs`. The result must write `ActorInvocationCompleted`, `Artifact`, `CodeChange`, and `Failure` records as appropriate, so execution leaves causal evidence in [[event-graph]].

Retry and repair are bounded by policy, not by the runtime's own judgement: `failed` retries at most 3 times then escalates to human review; `timed_out` gets one retry; **`policy_blocked` gets no auto-retry and requires review**; repair is capped at 3 attempts per task and 7 per release candidate. ([DF-V3.9-SPEC-004:L257-L272])

## The eleven enforcement stages

RuntimeBroker is specified to enforce a fixed pipeline rather than trust the runtime to self-police ([DF-V3.9-SPEC-004:L217-L229]): (1) preflight authorization, (2) envelope construction, (3) sandbox preparation, (4) execution monitoring, (5) file-system diff validation, (6) command audit, (7) network audit, (8) secret audit, (9) result normalization, (10) EventGraph recording, (11) post-run policy validation. The shape is *check the boundary going in, observe what happened, validate the boundary coming out, and record both* — the same evidence-over-trust move that defines Dark Factory.

## Local deterministic worker first — and, for now, only

The defining sequencing rule is **ADR Decision 7: "The First Runtime Is Local Deterministic Execution."** The base slice uses a local deterministic worker first; real Hermes, Codex, OpenManus, OpenHands, SWE-agent, Temporal, Dagger, LangGraph, OPA/Rego and other integrations are **deferred until the base slice proves traceability, policy, and audit.** ([DF-V3.9-ADR-001:L101-L105]) The Motive doc restates it: *"The first runtime is local deterministic execution. External runtimes are deferred until the local worker proves traceability, policy, and audit."* (§6)

This is gated by the **adapter conformance checklist**: *"No external runtime adapter is eligible until the local deterministic worker passes Base Slice 0,"* and every external adapter must then prove file-boundary enforcement, command-boundary enforcement, network denial, secret denial, timeout, artifact capture, nonzero-exit handling, EventGraph receipt emission, post-run validation, and replayability of evidence. ([DF-V3.9-SPEC-004:L194-L211]) Named external runtimes — *"Hermes, OpenManus, OpenClaw-like workers, Codex, CI, or future backends"* — are **references or adapters only; they do not own execution policy, Work flow, release authority, certification, or factory control.** ([DF-V3.9-SPEC-004:L213])

The planned runtime-selection progression makes the staging explicit ([DF-V3.9-SPEC-004:L308-L319]): Base Slice 0 (local deterministic worker) → Trial 1 (documentation-only patch proposal, local or Codex-generated, **behind RuntimeBroker**) → Trial 2 (bounded coding worker with real file changes) → Trials 3–5 (bugfix-with-tests, multi-repo with cross-repo approval, controlled self-improvement) → *later* Hermes/Codex/OpenManus/OpenHands/SWE-agent adapters behind the same envelope → *later still* CI and deployment dry-run adapters. The hard rule: *"No external runtime integration starts before RuntimeBroker, policy engine, trace completeness, and audit report work."*

> ⚠ **Fail-legible note on "the first and only runtime."** The *design* unambiguously makes the local deterministic worker the sole eligible runtime until conformance gates pass — that part is high-confidence and directly sourced. The stronger operational reading ("no other runtime has in fact been wired") is consistent with the v3.9 gate posture recorded in the Motive doc — *bounded completions through Gate J and Epic 10; Epic 11 selected for authorization review only; v4.0 Gate K / Gate L proposal-only as of that older source* ([Dark Factory - Motive, Goal, Approach.md], Autonomy and Gate Posture) — and with Open Brain notes that, in the hive runtime, only the `implementer` agent carries `CanOperate:true`. The later Gate K pre-live waiver does not authorize an external-runtime adapter or go-live. But the sources read this run do **not** include a live conformance-gate pass record or a cluster check, so treat "no adapter has yet cleared the checklist" as **strongly indicated, not independently proven here.** The orientation doc itself lists *"whether any external runtime should be integrated"* as an **open/deferred** issue.

## The boundary the design refuses to cross

RuntimeBroker enforces three non-negotiables for any runtime:

- **No runtime outside its envelope** — Dark Factory invariant #4. ([DF-V3.9-ADR-001:L204])
- **No runtime expands its own authority, self-approves protected actions, or directly certifies releases.** ([DF-V3.9-ADR-001:L97]) Protected actions (production deploy, default-branch push, merge to main, secret access, repo create/delete, cross-repo mutation, external-runtime invocation, release certification, …) route to the [[authority-layer]] for a fail-closed decision; a runtime cannot grant itself permission.
- **Execution is not certification.** A `RuntimeResult` is evidence fed into gates — TraceCompletenessGate, security gates, the proof-of-work packet — not a release verdict. Verification is the release authority, not the runtime.

This is the platform-wide *"intelligence is one operation type"* stance applied at the execution layer (see [[intelligence-is-an-operation-type]]): a model or coding agent is just another bounded `Operation` whose effects must leave evidence, never a controller.

## Build status (asserted vs. proven)

- **Specified in full** — envelope fields, enforcement stages, result schema, retry/repair policy, adapter checklist, and selection progression are all written in v3.9 normative docs read this run. High confidence that *this is the design.*
- **Partially exercised** — Open Brain session notes (Dark Factory "Slice 1") describe a working bounded execution path in the `transpara-ai/hive` runtime where spawned agents are forced `CanOperate:false` ("trust must be earned") and only the `implementer` runs; this is consistent with the local-deterministic-first rule but is *adjacent evidence*, not a RuntimeBroker conformance proof.
- **Not proven here** — that any external adapter has passed the conformance checklist (the design says none is eligible pre-Base-Slice-0), and the exact current implementation surface of RuntimeBroker as a named component. The responsibility map lists *"RuntimeBroker"* as a system rather than a single named repo, so its code home is **not pinned** by the sources read this run. Label these **thin**.

## Related entities

[[event-graph]] (where receipts and envelope hashes land) · [[work]] (supplies the `task_id` an envelope binds to) · [[authority-layer]] (supplies the `authority_decision_ref`; gates protected actions a runtime cannot self-grant) · [[dark-factory]] (the system RuntimeBroker is the execution boundary of) · [[the-20-primitives]] (the `Operation` primitive this realises) · [[intelligence-is-an-operation-type]] (the stance that a model is just another bounded operation) · [[gates]] and [[acceptance-criteria]] (consume RuntimeResult evidence; forward references).

## Sources & provenance

- **Primary normative source:** `Dark Factory - Motive, Goal, Approach.md`, §"Execute Only Through a Runtime Envelope" and the Repository and System Responsibility Map (`transpara-ai/docs`, draft v0.1.5, updated 2026-06-12). First-party synthesis; first-read orientation, explicitly *not* an implementation grant.
- **Normative spec (envelope, stages, result, progression):** `dark-factory/v3.9/04-production-workflow-and-runtime-v3.9.md` — Runtime Invocation Envelope (L166-213), enforcement stages and policy defaults (L215-231), RuntimeResult and retry/repair (L233-272), runtime-selection progression (L308-319). [DF-V3.9-SPEC-004]
- **Normative ADR (sequencing + invariants):** `dark-factory/v3.9/01-unified-architecture-decisions-v3.9.md` — Decision 6 bounded-runtime envelope and "no runtime expands its own authority" (L95-99), Decision 7 local-deterministic-first (L101-105), non-negotiable invariant #4 "No runtime outside its envelope" (L204). [DF-V3.9-ADR-001]
- **Lineage to the source philosophy:** the 20-primitives → architecture mapping in the Motive doc, traced to Matt Searles, *"20 Primitives and a Late Night"* (`https://mattsearles2.substack.com/p/20-primitives-and-a-late-night`, [Searles-P1]). Philosophical basis only — never implementation authority.
- **Operational context (adjacent, not a conformance proof):** Open Brain "Dark Factory Slice 1" session notes (2026-06-05 → 2026-06-10) recording the hive runtime's `CanOperate` posture and the v3.9 gate status (Gate J / Epic 10 bounded completions; Epic 11 authorization-review only). Open Brain returned no thought keyed directly to "RuntimeBroker"; per the task's fallback rule, chronology rests on the dark-factory docs.

No source conflict was found on this entity. The `[[wikilinks]]` above mix resolved articles ([[event-graph]], [[work]], [[authority-layer]], [[the-20-primitives]], [[intelligence-is-an-operation-type]]) with forward references ([[dark-factory]], [[gates]], [[acceptance-criteria]]) not yet compiled.
