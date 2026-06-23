---
entity: Hive / Governance Layer
aliases: [hive, the hive, transpara-ai/hive, the governance layer, the civilization runtime, the hive daemon, the civic roles]
tier: architecture
status: compiled
last_compiled: 2026-06-14
sources:
  - raw/transpara/dark-factory/Dark Factory - Motive, Goal, Approach.md  # responsibility map ("Hive / governance"); §7 "Govern Protected Actions Fail-Closed"; decision register B; v4.0 §12
  - raw/transpara/dark-factory/civic-roles.md  # the nine civic roles + governance section (status: superseded)
  - raw/transpara/dark-factory/reunification/2026-06-09-deployment-arc.md  # as-built review of the hive repo, 2026-06-09; the "civilization runtime" framing; Phases 1/2/7
  - Open Brain captures (2026-06-05 .. 2026-06-13)  # role-catalog chronology, CanOperate fact, guardian governance gap — see provenance footer
confidence:
  one_line_role: high (quoted verbatim from the first-party responsibility map)
  native_core_vs_governance_layer: contested — the same first-party doc files Hive under two different categories; stated below, not reconciled
  nine_civic_roles: high (one superseded source + ~8 corroborating Open Brain captures), but the source is status:superseded and its successor is status:draft/canonical:false
  invariant_count: contested — "Fourteen Invariants" (civic-roles.md) vs "Ten Invariants" (the same doc's authoring note); stated below
  twenty_six_protected_actions: medium — single as-built source (deployment-arc), a runtime count, not a doctrine count
---

# Hive / Governance Layer

**`transpara-ai/hive` is the governance layer of [[dark-factory]] — the native-core repo that evaluates authority and hosts the civic roles.** In the first-party orientation doc's words, its Dark Factory role is "Authority workflow, protected-action policy, later governed multi-agent coordination," with a hard boundary: it "does not replace [[event-graph]] truth" and is "not Base Slice 0 controller" (`Dark Factory - Motive, Goal, Approach.md`, Repository and System Responsibility Map). That one line is the spine of this entity: Hive decides *whether an action is permitted*; EventGraph remains the sovereign record of *what happened*.

The clean division of labour across the native-core repos is stated directly: "The sovereign truth layer is EventGraph. Work schedules and coordinates production. **Hive or governance evaluates authority.** RuntimeBroker confines execution. Site shows evidence to operators" (Executive Summary). Hive is the seat of *consent and policy*, not of truth ([[event-graph]]), flow ([[work]]), or execution (RuntimeBroker).

## Two roles in one repo

Hive carries two distinct functions, and the deployment-arc as-built review names both in one cell: **"Governance + civilization runtime."**

1. **Governance.** The authority workflow and protected-action policy — the fail-closed gate every consequential action must pass (see *Governing protected actions* below). This is the function the orientation doc's one-liner foregrounds.
2. **Civilization runtime.** Hive is also the process that *hosts the agent society* — the daemon that runs the civic roles, drives the concurrent loop, and (in the deployment plan) becomes "a continuously-running civilization (hive daemon + work-server + site + shared Postgres event store)" operating as a persistent installation (deployment-arc, The destination). The civic roles live in Hive's code (`pkg/hive/agentdef.go`), and the concurrent loop in `pkg/loop` (`RunConcurrent`).

> The entity name "Hive / Governance Layer" elides the second function. The runtime/host role is just as load-bearing as the policy role; the governance gate is *what the runtime enforces*, not the whole of what Hive is.

## What the boundary forbids

The responsibility map states Hive's constraint twice over, and the boundary is the point of the entity:

- **Hive is not the truth layer.** "Governance decisions must map to [[event-graph]] records" (decision register B). Hive evaluates and decides; the decision is only durable once it is an EventGraph record. Hive holds no authority that supersedes EventGraph for certification or authority.
- **Hive is not the Base Slice 0 controller.** Base Slice 0 — the mandatory control-plane proof before higher autonomy — explicitly "must not use … multi-agent orchestration" (Base Slice 0 Flow). The governed multi-agent civilization is a *later* capability; the floor of the system is proven without it. This is why the one-liner files multi-agent coordination under "later."
- The review-question checklist guards this directly: "Does it accidentally grant authority to Work, Site, **Hive**, memory, Git, CI, or external tools?" — Hive is named in the list of systems that must *not* quietly acquire truth/authority beyond their lane.

## Governing protected actions (fail-closed)

The governance function is the orientation doc's Approach step 7, "Govern Protected Actions Fail-Closed," and it is the clearest statement of what Hive does:

> "Protected actions are not model suggestions. They require authority. Unknown high-risk actions deny or require approval. Proposal artifacts are not approvals."

The named protected-action examples include production deployment, default-branch pushes, merges to main, secret access, repo creation/deletion, cross-repo mutation, policy changes, persistent agent spawning, capability promotion/activation/rollback, external runtime invocation, and release certification. **This is an illustrative list, not an exhaustive count.** The authority *outcomes* are canonical and fixed at four: **Autonomous, Notify, ApprovalRequired, Forbidden.** "ApprovalRequired blocks until an authorized decision grants approval. Forbidden means the actor must not proceed" (Approach §7, citing `DF-V3.9-SPEC-003`).

> ⚠ **Fail-legible — two authority models.** The four-outcome model above is the first-party Dark Factory model. The source-philosophy [[authority-layer]] (Searles' mind-zero-five) defines only **three** levels — Required / Recommended / Notification — with no `Forbidden` and a 15-minute "silence means consent" timeout that Dark Factory's `Autonomous` does not mirror. The two are not the same model; the Dark Factory doc treats the Searles corpus as source philosophy, not implementation authority. See [[authority-layer]] for the divergence in full. This article describes Hive as the *Dark Factory* governance layer (four outcomes).

The fail-closed posture is a load-bearing invariant, not a default: "No protected action without authority" and "Unknown high-risk actions deny or require approval." The as-built review records the runtime side of this: the hive repo has "**26 protected actions fail-closed**" wired today (deployment-arc, repo as-built summary).

> ⚠ **Fail-legible — the "26" is a runtime count, not a doctrine count.** The number 26 comes from a single as-built source (the 2026-06-09 deployment-arc), describing what the code wires at that commit; it is not the count of canonical protected actions in the v3.9 doctrine (the orientation doc gives examples, not a total). Treat 26 as point-in-time implementation state.

The human is the ceiling. Across all of this, "Protected actions remain fail-closed with **Michael Saucier as the top authority tier**" (deployment-arc, destination predicate 6), and his "explicit instruction always overrides civilizational consensus" (civic-roles.md, Governance).

## The civic roles (the society Hive hosts)

The runtime side of Hive is a society of cooperating agent roles that "coordinate exclusively through a shared, append-only event graph — no role communicates out-of-band or holds private state that isn't visible to the graph" (civic-roles.md). The superseded `civic-roles.md` enumerates **nine** civic roles, each a defined scope of authority plus an interface:

| Role | One-line responsibility (from `civic-roles.md`) |
|---|---|
| **strategist** | Owns the big picture; decomposes a Factory Order into high-level work units on the graph. |
| **planner** | Breaks work units into concrete tasks; attaches the readiness contract (definition of done, acceptance criteria, test plan) before any task is assigned. |
| **implementer** | The only civic role with direct filesystem access; reads the contract, writes the artifact, commits, records the commit hash. |
| **reviewer** | Quality + trace-completeness gate; checks acceptance criteria, traceability, and constitutional invariants before marking work accepted. |
| **guardian** | Integrity monitor *outside* the task hierarchy; watches the graph for invariant violations (secret exposure, unauthorized upstream pushes, privilege escalation) and either raises an authority request or halts the run. |
| **cto** | Technical leadership; identifies capability gaps, issues directives, escalates architecture decisions beyond autonomous authority. |
| **spawner** | Growth engine; proposes a new civic role when a capability gap appears, for human approval before instantiation. |
| **allocator** | Manages compute/token/quota budget; pauses or requests a budget increase before approved limits are exceeded. |
| **sysmon** | Health monitor; watches process liveness, graph integrity, chain continuity, dependency reachability; alerts or halts on degraded infrastructure. |

Two role facts are corroborated by code-grounded Open Brain captures (2026-06-05 .. 2026-06-13, sourced from `pkg/hive/agentdef.go` `StarterRoleDefinitions`/`StarterAgents`):

- **The implementer is the only role with `CanOperate=true`** — i.e. the only role permitted to take real, effecting action; the rest are governance/coordination roles. Spawned (emergent) roles "remain `CanOperate=false`, trust-gated" (deployment-arc, Phase 7).
- **The guardian sits outside the role hierarchy** and approves role proposals by default unless a policy is violated — an earlier gap where the Guardian's prompt lacked the `/approve`/`/reject` instructions it was supposed to use was fixed by adding a ROLE GOVERNANCE section (Open Brain, 2026-04-09, then on the upstream hive, pre-rebrand).

> ⚠ **Fail-legible — source status.** `civic-roles.md` is marked **`status: superseded`**; it points to `docs/roles-catalog.md` as a "strict superset covering both runtime civic roles and governance policy roles." That successor catalog is itself **`status: draft, canonical: false`** across every Open Brain capture of it (2026-06-08 .. 2026-06-13), pending Gate-E approval. So: the *nine runtime civic roles* are stable and well-attested, but the canonical catalog adds **15 governance policy roles** (Operator, Product, Architect, Planner, Engineer, QA, Security, Release, Auditor, MemoryCurator, KnowledgeCurator, EvalOwner, CapabilityOptimizer, CapabilityReviewer, CapabilityRelease) for **24 total**, with only the `planner`/`Planner` name matching exactly across layers. The 9 runtime roles are the ones Hive *runs*; the 15 governance roles are an authority-doctrine taxonomy, not separate running agents.

## The constitution

All civic roles operate inside the civilization's constitution: **the Soul** (ethical and priority ordering), **the Eight Agent Rights** (protections every agent is entitled to), and the hard behavioural invariants no role may violate (civic-roles.md, Governance). Every consequential decision is recorded on the append-only event graph "so the full audit trail is available for review."

> ⚠ **Fail-legible — invariant count conflicts.** `civic-roles.md` (the source as it stands today) says "the **Fourteen** Invariants." The Open Brain capture written *when that same file was first created* (2026-06-05) records it as "the Soul + Eight Agent Rights + **Ten** Invariants." The two disagree and this article does not pick a winner; the file's current text says fourteen, the authoring note said ten. The count of *agent rights* (eight) is consistent across both.

## Where Hive sits in the arc

Hive is one of the six [[dark-factory]] repos (live topic query: `agent`, `docs`, `eventgraph`, `hive`, `site`, `work`). The 2026-06-09 deployment arc — a **proposal-only** planning document that "authorizes no implementation, advances no gate, grants no autonomy level" — places Hive's runtime function at the centre of the path to a continuously operated factory:

- **Phase 1** (close Slice 1) turns on the review→fix *loop* inside Hive's `pkg/loop` (extending the periodic re-check beyond `CanOperate` agents so a keepalive reviewer picks up unreviewed work without a fresh wake event).
- **Phase 2** (always-on substrate) moves Hive from per-run throwaway databases to a durable shared store and persistent role identities, so the "civilization … stays up."
- **Phase 7** (growth) wires the *governed* growth loop — CTO → Spawner → Guardian → Allocator → `spawnDynamicAgent` — and replaces hand-edited role contracts with the governed capability-evolution chain. This is "later governed multi-agent coordination" from the one-liner, made concrete and still inside the membrane.

The as-built review (2026-06-09) records Hive's then-current state as: civic roles in `pkg/hive/agentdef.go`; the concurrent loop (`pkg/loop`, `RunConcurrent`); 26 protected actions fail-closed; factory-order entry (`cmd/hive factory`); a commit-verification gate; run-launch API; and dynamic model selection. **Telemetry → Postgres only; no Prometheus; in-process bus; no schema bootstrap/migrations.** The in-process bus is a deliberate constraint with a deployment consequence: "the hive daemon and its agents are one process by design … so exactly one replica" (deployment-arc, Phase 8) — a single-process civilization, not agents distributed across machines.

> ⚠ **Fail-legible — proposal-only.** Every phase claim above is from a planning document explicitly marked `authority: planning, canonical: false`; it "authorizes no implementation" and each phase "requires its own design packet, authorization packet, and explicit human authorization." These describe *intended* arc shape, not shipped, accepted behaviour. The as-built bullets are runtime state at one commit, not doctrine.

## Contested: native core vs governance layer

> ⚠ **Fail-legible — the source disagrees with itself on Hive's category.** Within the *same* first-party document (`Dark Factory - Motive, Goal, Approach.md`):
> - the **Repository and System Responsibility Map** lists `transpara-ai/hive / governance` with selected status **"Selected governance layer"**; while
> - the **Decision Register, table B (Native Dark Factory Systems)** lists `Hive / governance` with category **"Selected native core."**
>
> Both rows agree on the *function* (authority workflow + protected-action decisioning) and the *constraint* (governance decisions must map to EventGraph; Hive does not execute directly), so this is a label inconsistency, not a substantive one. This article uses **"governance layer"** in the lead because the entity slug and one-line brief do; it flags the "native core" label here rather than silently choosing. Note that EventGraph, Work, and Agent are unambiguously "Selected native core" in both places — Hive is the only repo with a split label.

## See also

- [[event-graph]] — the sovereign truth layer Hive's decisions must map onto; Hive never supersedes it.
- [[work]] — flow and task lifecycle; the sibling native-core repo Hive coordinates with (Work owns the DAG; Hive owns authority).
- [[authority-layer]] — the source-philosophy consent gate (Searles / mind-zero-five), with the three-vs-four-outcome divergence flagged above.
- [[accountable-ai-architecture]] — mind-zero-five, the prior pattern showing an event graph + authority layer + mind loop is implementable.
- [[dark-factory]] — the governed production system Hive is the governance/runtime layer of.
- [[the-20-primitives]] — the failure-tracing seed; "authority becomes AuthorityRequest, AuthorityDecision, and ExecutionReceipt" is the primitive line Hive implements.

## Run-3 update (2026-06-14)

Two changes shipped on 2026-06-14 that bear directly on model-policy correctness and the transparency surface.

**Observatory (`/ops/observatory`).** `site#76` (merged 2026-06-13) and `site#77` (merged 2026-06-13) together deliver a read-only transparency surface at `/ops/observatory` in the Site console. The observatory consumes the hive's `operator-projection` API alongside the work telemetry APIs (`/telemetry/status`, `/telemetry/agents/history`, `/telemetry/sse`) and renders civilization vitals, agent roster, spend-vs-cap, authority queue, and causal trace — all GET-only, all `effect=none`. This is the Gate-E "society view" surface anticipated in the deployment arc. See [[site]] for the full account; the Hive side is that its operator-projection API (`pkg/hive`) is the primary data source the observatory reads.

**hive#158 — catalog reload affects next spawn (test + fix).** A new integration test (`pkg/hive/runtime_test.go`, `TestRuntimeModelCatalogReloadAffectsNextSpawn`) proves that after a role-default catalog file is modified on disk and the configured `CatalogReloadInterval` fires, the *next* `SpawnAgent` call picks up the new model assignment. The same PR also fixed a latent bug: `runtime.go`'s reload path was registering duplicate resolver sets when the manager was already initialized; that is now guarded. Significance: catalog reload is now verifiable behavior, not assumed; dynamic model selection (`pkg/hive/agentdef.go`, used by `RunConcurrent`) is covered end-to-end.

**hive#159 — page role policy lookups fixed.** `pkg/hive/operator_model_policy_api.go`'s `latestModelRolePolicyUpdates` was using `readProjectionEvents` (a single-page helper) and could miss policy events that fell outside the first page of results. The fix replaces the single-page call with a paginated loop over `store.ByType(EventTypeModelRolePolicyUpdated, …)` that walks pages newest-first (chain order, not wall-clock), short-circuits once every starter role has a policy, and guards the `nil`-store and `limit ≤ 0` edge cases. A companion test covers malformed policy events. The fix closes a silent fail-open: an operator who set a model policy but had more than `defaultOperatorProjectionLimit` events in the store could see their policy silently ignored on the next projection load.

> **Fail-legible.** Both PRs are in the `transpara-ai/hive` repo (origin); any upstream equivalent is separate and is not referenced here.

## Sources & provenance

Compiled this run from:

- **`Dark Factory - Motive, Goal, Approach.md`** (first-party orientation, `transpara-ai/docs: dark-factory/`, v0.1.5, `status: draft`, `canonical: false`) — the entity one-liner (Repository and System Responsibility Map), Executive Summary role split, Approach §7 (protected actions fail-closed) and §12 (v4.0), Base Slice 0 Flow, the four authority outcomes, decision register B, and the review-question checklist. Local read path: `/Transpara/transpara-ai/repos/docs/dark-factory/Dark Factory - Motive, Goal, Approach.md`.
- **`civic-roles.md`** (`transpara-ai/docs: dark-factory/civic-roles.md`, **`status: superseded`** → `docs/roles-catalog.md`) — the nine civic roles, the constitution (Soul / Eight Agent Rights / Fourteen Invariants), and the human-as-top-authority-tier statement. Local read path: `/Transpara/transpara-ai/repos/docs/dark-factory/civic-roles.md`.
- **`reunification/2026-06-09-deployment-arc.md`** (`transpara-ai/docs`, v0.1.4, `status: review`, `authority: planning`, `canonical: false`) — the "Governance + civilization runtime" framing, the hive as-built summary (26 protected actions, `pkg/hive/agentdef.go`, `pkg/loop`/`RunConcurrent`, in-process bus, single-replica constraint), and Phases 1/2/7/8. Local read path: `/Transpara/transpara-ai/repos/docs/dark-factory/reunification/2026-06-09-deployment-arc.md`.
- **Open Brain captures (2026-06-05 .. 2026-06-13)** — roles-catalog chronology and the 9-runtime + 15-governance = 24-role enumeration with sources in `pkg/hive/agentdef.go` `StarterRoleDefinitions`/`StarterAgents`; the `implementer`-is-the-only-`CanOperate=true` fact; the catalog's persistent `status: draft, canonical: false`; and the earlier Guardian role-governance prompt gap (2026-04-09, upstream hive). The "Ten Invariants" vs "Fourteen Invariants" discrepancy comes from comparing the 2026-06-05 authoring capture with the current `civic-roles.md` text.

- **`pkg/hive/runtime_test.go` (hive#158, 2026-06-14)** — `TestRuntimeModelCatalogReloadAffectsNextSpawn`; proves catalog reload propagates to next spawn; also fixed duplicate resolver registration on reload in `pkg/hive/runtime.go`.
- **`pkg/hive/operator_model_policy_api.go` (hive#159, 2026-06-14)** — paginated `latestModelRolePolicyUpdates`; fixes page-boundary miss in role-policy lookups; companion test covers malformed events.
- **`site#76` / `site#77` (2026-06-13, merged)** — observatory (`/ops/observatory`), the Gate-E transparency surface; described in [[site]].

Durable external URL (for the [[authority-layer]] divergence referenced above): Matt Searles, "The Architecture of Accountable AI" — https://mattsearles2.substack.com/p/the-architecture-of-accountable-ai [Searles-P3].

`[[wikilinks]]` are forward references where the target is not yet compiled; `[[event-graph]]`, `[[work]]`, `[[authority-layer]]`, `[[accountable-ai-architecture]]`, and `[[the-20-primitives]]` are compiled siblings as of 2026-06-13. No `[[dark-factory]]` article exists yet. Contested claims (native-core-vs-governance-layer label, invariant count, the "26" runtime figure, the role-catalog status) are flagged inline rather than reconciled.
