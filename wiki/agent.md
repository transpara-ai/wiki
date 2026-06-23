---
entity: Agent (Identity and Lifecycle Core)
aliases: [agent, transpara-ai/agent, the agent package, identity and lifecycle core, agent repo]
tier: architecture
status: compiled
last_compiled: 2026-06-13
sources:
  - path: raw/transpara/dark-factory/Dark Factory - Motive, Goal, Approach.md  # responsibility map, "Selected native core", boundary
  - path: raw/transpara/dark-factory/reunification/2026-06-05-slice-1-first-reunified-order-design.md  # load-bearing-but-unchanged; agent.New/transitions/trust/identity_lifecycle; deferred persistent identity
  - path: /Transpara/transpara-ai/repos/agent/agent.go  # code-is-truth: New(), boot sequence, checkCanEmit, role-agnostic
  - path: /Transpara/transpara-ai/repos/agent/transitions.go  # FSM transitions, OBSERVABLE rollback, Suspend/Resume, ResetIfStuckProcessing
  - path: /Transpara/transpara-ai/repos/agent/trust.go  # RecordVerifiedWork trust accumulation
  - path: /Transpara/transpara-ai/repos/agent/identity_lifecycle.go  # persistent identity register/rotate/revoke, authority-gated, fail-closed
  - path: Open Brain  # chronology: 2026-04-04..06 emitter buildout; spawn lifecycle; first dynamic agent 2026-04-08
confidence:
  load_bearing_claim: high — hive/go.mod has `github.com/transpara-ai/agent => ../agent`; slice-1 design names agent as load-bearing
  no_execution_no_governance: high — confirmed by dark-factory responsibility map AND by the package code (no runtime/govern surface)
  CanOperate_attribution: high (negative) — CanOperate is a hive agentdef concept, NOT in the agent repo; see note
  persistent_identity_in_use: thin — the authority-gated production-identity path exists in code but slice-1 explicitly DEFERS it; not yet exercised in the reunification run
  fail_closed_emit_guard: contested — identity lifecycle is allowlist/fail-closed, but checkCanEmit() uses a denylist switch with default→allow; see note
---

# Agent (Identity and Lifecycle Core)

The **`transpara-ai/agent`** repo is the Go package that gives every civic role in the [[hive-governance]] runtime a single, uniform body: an identity, an operational state machine, trust-accumulation hooks, and helpers that emit causal lifecycle events onto the shared [[event-graph]]. Its own package doc states the scope plainly: *"Every agent — Mind, CTO, Guardian, Builder, etc. — is an Agent,"* and the type *"wraps EventGraph's AgentRuntime"* to add the state machine, causality tracking, trust hooks, budget emission, retirement lifecycle, and communication through the shared graph.

In the [[dark-factory]] map of who-owns-what, Agent is classified **"Selected native core"** with a hard boundary: *"Identity/lifecycle helpers and causal event emission helpers … Does not own direct execution authority."* The reunification slice-1 design echoes this — Agent is *"load-bearing-but-unchanged."* So the entity is foundational to how the civilization runs, yet deliberately small in authority: it does not execute work and it does not govern. Execution is the job of RuntimeBroker; governance/authority is the job of [[hive-governance]] and the [[authority-layer]].

## When and why it appeared in the arc

The buildout is recorded in Open Brain over **2026-04-04 → 2026-04-06**: in three days the agent repo gained typed event emitters covering the full lifecycle — health reports, budget allocation/adjustment, role proposed/approved/rejected, CTO gap detection and directives, knowledge insights/supersession/expiration, code reviews, and forced `ResetToIdle` recovery. Each role (SysMon, Allocator, Spawner, Guardian, CTO, Reviewer) got its own typed emitters, all following the same shape — a `checkCanEmit` guard followed by a `recordAndTrack` call — turning the package into an immutable audit log of agent decisions. The same window saw the CTO, Spawner, and Guardian agents land in the [[hive-governance]] runtime, and on **2026-04-08** the first dynamically spawned agent (a "researcher") went through the full birth lifecycle, proving the self-evolution loop end to end. (These dates are the emitter/role buildout; the agent *type* itself predates them. The earliest captured spawn-lifecycle thoughts name the repo as `lovyou-ai-hive` before the transpara-ai fork convention took hold.)

## What the package is (code-grounded)

- **One unified `Agent` type.** `agent.New(ctx, Config)` registers the agent in the actor store, generates an Ed25519 signing key by default, and emits the full boot sequence (identity, soul values, model, authority self-grant, and the transition to `Idle`) onto the graph. The package is explicitly **role-agnostic**: `Role` is just a string, and *"Constants are defined by the application layer (e.g. hive/pkg/roles), not here."* This is why the same code body serves strategist, planner, implementer, reviewer, guardian, cto, spawner, allocator, and sysmon.
- **An operational state machine.** `transitions.go` drives `Idle → Processing → Suspended → Retired` style states. State changes are atomic under the agent mutex and obey an **OBSERVABLE invariant**: if the `agent.state.changed` event cannot be recorded, the in-memory state is *rolled back* — an unrecorded transition is treated as no transition. `Suspend()`/`Resume()` model Guardian HALT and recovery.
- **Trust accumulation.** `trust.go`'s `RecordVerifiedWork` updates an actor's trust score after verified work (successful reviews, test passes) and emits a `TrustUpdated` event carrying previous/current scores and a causal pointer to the evidence. The agent package holds the trust *hooks*; the trust *model* lives in EventGraph (`eventgraph/go/pkg/trust`).
- **True causality.** Every emitted event is caused by *this agent's previous event* (`lastEvent`), not by whatever happens to sit at `store.Head()` — so an agent's own actions form a clean causal chain on the shared graph.
- **Persistent production identity (authority-gated).** `identity_lifecycle.go` provides `RegisterPersistentIdentity`, `RotatePersistentIdentity`, and `RevokePersistentIdentity`. These are **fail-closed**: each requires an explicit v3.9 `AuthorityRequest`/`AuthorityDecision` pair (`requireAuthority` rejects a missing decision, a mismatched action/target, or any decision that is not `Autonomous`/`Notify`), public-name-derived keys are blocked in production, and each action appends `ActorIdentity`, `LifecycleTransition`, and `ExecutionReceipt` records to EventGraph. The zero-value `Environment` is `production` "to fail closed," and `IdentityModeDeterministic` is rejected outside dev/test.

## The boundary: no execution authority, no governance

The defining negative claims in the one-liner are well supported:

- **No direct execution authority.** The dark-factory responsibility map states it ("Does not own direct execution authority"), and the code corroborates: the package has no runtime-broker, no command-execution, no file/network surface. It emits *events about* work; bounded execution belongs to RuntimeBroker under a declared envelope (*Dark Factory - Motive, Goal, Approach*, approach step 6).
- **Does not govern.** Authority decisions are consumed by Agent (as inputs to the identity lifecycle), not produced by it. Governance/protected-action decisioning is [[hive-governance]]'s job, and authority records must map back to [[event-graph]] ([[authority-layer]]).
- **Load-bearing but not in command.** [[hive-governance]] depends on the package directly — `hive/go.mod` carries `github.com/transpara-ai/agent => ../agent`, and the slice-1 design lists it imported across `pkg/hive/{identity,bridge,runtime}.go` and `pkg/loop/loop.go`. Removing it would break the runtime; it still holds no execution or governance authority.

## Role in the reunification slice

In the **2026-06-05 slice-1 design** ("the first reunified order"), Agent is *exercised, unchanged*: the civic roles run on their **bootstrap runtime identities** while one `FactoryOrder` flows strategist → planner → implementer → reviewer → guardian → human, coordinating only through graph events. Crucially, the slice **defers** the persistent production identity path:

> "Persistent production identity (`RegisterPersistentIdentity`, for 'opened by `implementer@<key>`' PR provenance) is deferred to a later slice."

So although the authority-gated identity lifecycle is fully present in the code, it is **not yet exercised** in a live reunified run — a gap worth flagging rather than implying the production-identity feature is in use today (**evidence: thin / deferred**).

## The growth loop it underpins

Agent is the substrate the [[hive-governance]]'s self-evolution loop runs on. Open Brain records the spawn lifecycle precisely: the **Spawner** proposes a role (`hive.role.proposed`), the **Guardian** approves or rejects (`hive.role.approved`), the **Allocator** adjusts budget (`agent.budget.adjusted`), and a watcher matching all three calls `spawnDynamicAgent` to hot-add the agent into a running loop without restart. The slice-1 design adds that newly spawned agents always start `CanOperate=false` (trust-gated) — but see the attribution note below: that flag is a **hive `agentdef.go`** property, not part of the agent repo.

## Fail-legible notes

- **`CanOperate` is NOT in the agent repo.** Sources (and the one-liner's neighborhood) associate Agent with trust-gating, and the slice-1 design says new agents spawn `CanOperate=false`. But a direct grep of `transpara-ai/agent/*.go` finds **no `CanOperate`** symbol; Open Brain places it in the [[hive-governance]] `agentdef.go` `StarterRoleDefinitions`, where only the *implementer* has `CanOperate=true`. Do not attribute `CanOperate` to this package — Agent supplies the *trust score* (`RecordVerifiedWork`); the operate gate is enforced one layer up in [[hive-governance]].
- **Two fail-safe postures coexist in the code.** The identity lifecycle is textbook fail-closed (allowlist of accepted authority decisions; everything else refused). But `checkCanEmit()` is written as a **denylist** `switch` — it blocks `Retired` and `Suspended` and lets the `default` case *return nil* (permit). For the current known state set this is benign, but a denylist with a permissive `default` is exactly the shape Michael's engineering standard warns against (it silently permits any state added later). Flagged as an inconsistency in posture, not as a present-day bug. (Source: `agent.go:292`.)
- **README is absent.** There is no `README*` in the agent repo, so every claim here is grounded in the package source and the two dark-factory docs, not in a repo overview — consistent with the "code is truth" hierarchy.
- **"Native-core" is a dark-factory classification, not a proof of completeness.** The orientation doc that supplies it is a *draft* ("status: draft, canonical: false") and explicitly does *not* authorize implementation; it records the intended boundary, which the code happens to honor.

## Related entities

[[hive-governance]] · [[event-graph]] · [[authority-layer]] · [[dark-factory]] · [[work]] · [[the-20-primitives]] (the `Agent` primitive — "intelligence as an operation type" — is the conceptual ancestor of this package) · [[intelligence-is-an-operation-type]]

## Sources & provenance

- `raw/transpara/dark-factory/Dark Factory - Motive, Goal, Approach.md` — Repository and System Responsibility Map (Agent = "Selected native core … Does not own direct execution authority"), and the broader execution/governance boundary (EventGraph kernel, RuntimeBroker execution, Hive/governance authority). First-party orientation draft (v0.1.5, status draft).
- `raw/transpara/dark-factory/reunification/2026-06-05-slice-1-first-reunified-order-design.md` — the repo-impact map row for `agent` ("load-bearing-but-unchanged"; `agent.New()`, `transitions.go`, `trust.go`, `identity_lifecycle.go`; `hive/go.mod` replace; deferred `RegisterPersistentIdentity`); the cooperative-flow and growth-loop context.
- `transpara-ai/agent` source (read this run): `agent.go` (package doc, `New()`, boot sequence, role-agnostic `Role`, `checkCanEmit`), `transitions.go` (FSM + OBSERVABLE rollback, Suspend/Resume, `ResetIfStuckProcessing`), `trust.go` (`RecordVerifiedWork`), `identity_lifecycle.go` (authority-gated, fail-closed persistent identity register/rotate/revoke).
- Open Brain captured thoughts — agent-repo emitter buildout 2026-04-04→06; dynamic-spawn lifecycle (Spawner→Guardian→Allocator→`spawnDynamicAgent`); first dynamically spawned agent 2026-04-08; `CanOperate=true` only for implementer (hive `agentdef.go`).

Searles source framing referenced indirectly via the dark-factory citation table (the `Agent` primitive and "intelligence is an operation type"): `Searles-P1` — "20 Primitives and a Late Night", `https://mattsearles2.substack.com/p/20-primitives-and-a-late-night`. The 954KB Searles corpus was **not** read for this architecture entity; the relevant philosophical lineage reaches it through `Dark Factory - Motive, Goal, Approach.md`.

`[[wikilinks]]` are forward references; several targets (e.g. [[hive-governance]], [[dark-factory]]) may not yet be compiled.
