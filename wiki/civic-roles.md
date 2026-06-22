---
entity: Hive Civic Roles
aliases: [civic roles, the civic roles, the nine civic roles, the society of roles, runtime civic roles, starter agents, StarterAgents]
tier: architecture
status: compiled
last_compiled: 2026-06-13
sources:
  - raw/transpara/dark-factory/civic-roles.md  # the nine civic roles + governance section (status: superseded → docs/roles-catalog.md)
  - raw/transpara/dark-factory/docs/roles-catalog.md  # canonical superset, v3.0.0, the code-sourced per-role facts (status: active, canonical: true)
  - raw/transpara/dark-factory/reunification/2026-06-05-slice-1-first-reunified-order-design.md  # origin: civic-roles.md as the artifact of the first reunified FactoryOrder run; the cooperative flow + membrane + growth-loop hook
  - Open Brain captures (2026-04-03 .. 2026-06-12)  # incremental build chronology, growth-loop wiring, first dynamic spawn (researcher), CanOperate fact, catalog supersession — see provenance footer
confidence:
  nine_roles: high — code-grounded in pkg/hive/agentdef.go StarterAgents()/StarterRoleDefinitions(), enumerated identically by the candidate source, the canonical catalog, and ~8 Open Brain captures
  per_role_code_facts: high — quoted from roles-catalog.md v3.0.0 with line citations into agentdef.go, but those are catalog-of-code, not the code read directly this run
  candidate_source_status: superseded — civic-roles.md is status:superseded; its successor roles-catalog.md was status:draft/canonical:false across every prior capture but is status:active/canonical:true in the copy read this run; see fail-legible note
  invariant_count: contested — "Fourteen Invariants" (civic-roles.md current text) vs "Ten Invariants" (the 2026-06-05 authoring capture of the same file); stated, not reconciled
  reunified_run_completed: thin/asserted — the slice-1 doc is a working design ("not accepted doctrine"); whether the run finished as specified is not established by the sources read this run
---

# Hive Civic Roles

**The civic roles are the society of cooperating agents the [[hive-governance]] runtime hosts** — nine bootstrap agents (strategist, planner, implementer, reviewer, guardian, cto, spawner, allocator, sysmon) that "coordinate exclusively through a shared, append-only event graph — no role communicates out-of-band or holds private state that isn't visible to the graph" (`civic-roles.md`). Each role has a defined scope of authority and a defined interface (tasks, phases, signals); together they form a complete production and governance loop, with the human — Michael Saucier — as the top authority tier who approves any protected action that cannot be delegated to the civilization itself.

The roles are not a paper taxonomy: they are the `AgentDef` structs registered by `StarterAgents()` in `pkg/hive/agentdef.go` in `transpara-ai/hive` — "the bootstrap agents the civilization actually runs" (`roles-catalog.md`). They were built incrementally through April 2026 (Guardian, Sysmon, Allocator, CTO, Spawner, then the work-tier roles; Open Brain, 2026-04-03 .. 2026-04-15) and first documented *as their own society* on **2026-06-05**, when the first reunified `FactoryOrder` asked the civilization to write `dark-factory/civic-roles.md` — "the civilization's first reunified act is to *document its own society*" (slice-1 design doc, §1).

## What "civic" means here

A civic role is a participant in a self-governing society, not a thread in a job runner. The defining property is the one the slice-1 design calls "the hive-mind property, obtained for free": **coordination is only through graph events** — "no direct communication — only events" (`hive/ARCHITECTURE.md`, quoted in the slice-1 doc, §2). Every consequential decision is recorded on the append-only event graph "so the full audit trail is available for review" (`civic-roles.md`, Governance). The roles share one substrate — the [[event-graph]] — and reading/writing that graph *is* how they collaborate; there is no side channel.

This is what distinguishes the civic roles from the **governance policy roles** (Operator, Product, Architect, …) that the canonical catalog enumerates alongside them. The nine civic roles are agents that *run* (code); the fifteen governance roles are a permission taxonomy that says *what is allowed* (doctrine). See *Two role layers, one catalog* below.

## The nine roles

The table below merges the candidate source's one-line responsibilities (`civic-roles.md`) with the code-sourced facts the canonical catalog records from `agentdef.go` (`roles-catalog.md`, v3.0.0). `CanOperate` decides whether the runtime loop calls `Operate()` (real filesystem action) or `Reason()` (propose-only) for that agent.

| Role | Category | CanOperate | Reports to | Responsibility (from the sources) |
|---|---|---|---|---|
| **strategist** | leadership | `false` | cto | Decomposes the seed idea (Factory Order) into top-level tasks; "the only agent that decomposes the seed idea." Creates tasks at the component level, observes completions, identifies what is missing next. Does not write code. |
| **planner** | technical | `false` | strategist | Breaks high-level tasks into concrete subtasks and attaches the **readiness contract** — `definition_of_done`, `acceptance_criteria`, `test_plan` — before any task is assigned. Does this in two phases (subtasks, then gates + dependency edges). |
| **implementer** | technical | **`true`** | strategist | The **only** civic role with direct filesystem access. Reads the contract, writes the artifact, runs tests, commits, and records the commit hash so reviewers can diff the exact change. Handles review feedback by fixing exactly the reported issues. |
| **reviewer** | technical | `false` | cto | Quality + trace-completeness gate. Checks the artifact against acceptance criteria and definition of done, verifies traceability to a task on the graph, and that no constitutional invariants are violated. Emits `approve` / `request_changes` / `reject`; cannot modify code. |
| **guardian** | process | `false` | **human** | Integrity monitor *outside* the task hierarchy. Watches **all** events (empty `WatchPatterns` = subscribes to `*`) for soul violations, authority overreach, and policy breaches; emits `ALERT` or `HALT`; evaluates role proposals via `/approve` and `/reject`. Reports directly to the human. |
| **cto** | leadership | `false` | **human** | Technical leadership. Identifies structural gaps in the role taxonomy, emits `/gap` and `/directive`, escalates existential concerns to the human via `/signal ESCALATE`. First 15 iterations are observe-only. |
| **spawner** | staffing | `false` | cto | Growth engine. Responds to `hive.gap.detected` by proposing a new role via `/spawn` — but does **not** spawn directly; proposals require guardian approval + allocator budget. Proposed roles must have `CanOperate: false` ("trust must be earned"). One proposal in flight at a time. |
| **allocator** | process | `false` | guardian | Resource manager. Redistributes token/iteration/duration budgets via `/budget`, under stabilization, cooldown, and floor/ceiling constraints. Its 12-hour `MaxDuration` "bounds the society's epoch and cannot be self-renewed." |
| **sysmon** | process | `false` | guardian | Health monitor. Emits `/health` reports (ok / warning / critical) on process liveness, graph integrity, chain continuity, dependency reachability. **Must never emit `HALT`** — it reports alarming conditions for the guardian to act on. |

Two facts are worth pulling out because they are load-bearing and code-grounded (corroborated by Open Brain captures sourced from `agentdef.go`, 2026-04-09 .. 2026-06-12):

- **The implementer is the only role with `CanOperate=true`.** Every other civic role is propose-only — it reasons and emits events, but cannot touch the filesystem. This is the runtime expression of least privilege: exactly one role can effect change, and it does so only against a readiness-gated task on a `codex/*` branch.
- **The guardian reports to the human and watches everything.** It sits outside the hierarchy the other roles form, and its escalation path is the human, not another agent. (An earlier gap — the Guardian's prompt lacked the `/approve`/`/reject` governance instructions it was supposed to use — was fixed by adding a role-governance section; Open Brain, 2026-04-09, on the upstream hive.)

> The boot order is intentional: integrity → health → budget → leadership → work (Open Brain, 2026-06-06). Guardian, Sysmon, and Allocator come up before the agents that produce work, so the monitors are already watching when production starts.

## The cooperative loop (one order, end to end)

The slice-1 design maps each step of fulfilling a `FactoryOrder` to a real agent and a real event (slice-1 doc, §2). This is the "complete production and governance loop" the lead refers to, made concrete:

1. **Order injected** as a Work task (`work.task.created`).
2. **strategist** decomposes it (`/task create`).
3. **planner** attaches the readiness contract — enforced by the **readiness gate** (`work/store.go:Readiness`).
4. **implementer** (`CanOperate=true`) builds the artifact on a `codex/*` branch (`/task artifact` + a proposal-only `CodeChange`).
5. **reviewer** approves or returns (`code.review.*`); the return path exercises the feedback loop.
6. **guardian** authorizes the protected action — raising an `AuthorityRequest` that **escalates to the human** via the Site Gate-E decision surface.

The membrane is deliberately minimal in slice 1: a **readiness gate** (the planner's three artifacts), a **trace-completeness** check (the reviewer verifies every material step left an event), and a single **authority gate** (creating a real draft PR is a protected action). Gates are "role-enforced checks, applied inside the cooperative flow by Reviewer and Guardian. Evidence is a *byproduct* of roles working" (slice-1 doc, "five inversions" #2) — not a separate pipeline running beside the society. The deeper fail-closed authority machinery this gate plugs into is the subject of [[hive-governance]] and [[authority-layer]].

## The growth loop (how the society staffs itself)

The civic roles are not a fixed cast. The **spawner** is "the civilization's growth engine" (`civic-roles.md`): when the **cto** (or another role) surfaces a capability gap no existing role can fill, the spawner proposes a new role definition for approval before instantiation. The full chain, wired in code (Open Brain, 2026-04-05 .. 2026-04-15; slice-1 doc, §4):

> **cto** `/gap` → `hive.gap.detected` → **spawner** `/spawn` → `hive.role.proposed` → **guardian** `/approve` → `hive.role.approved` → **allocator** `/budget` → `spawnDynamicAgent` (in `watch.go`, behind `authorizeProtectedAction`).

Dynamic agents always spawn `CanOperate=false` — "trust must be earned," enforced in code (`roles-catalog.md`, Dynamic Agents; slice-1 doc, §4). The first dynamically spawned agent in the hive's history was the **researcher** (2026-04-08): the CTO detected a gap, the Spawner proposed it, the human approved, and the watcher matched all three events and called `spawnDynamicAgent()` — "the first proof that the SELF-EVOLVE invariant works end-to-end" (Open Brain, 2026-04-09).

> ⚠ **Fail-legible — dynamic agents are not "civic roles" in the catalog sense.** Spawned agents "are not enumerated in this catalog because they are not registered `AgentDef` structs — they emerge at runtime" (`roles-catalog.md`). So the nine roles are the *bootstrap* society; the growth loop adds members the catalog deliberately does not list. The article's title entity is the nine, plus the mechanism by which more appear.

## Authority scope and the human ceiling

Every role "operates inside the civilization's constitution: the Soul (the ethical and priority ordering), the Eight Agent Rights (the protections every agent is entitled to), and the … Invariants (the hard behavioral rules no role may violate)" (`civic-roles.md`, Governance). "No role may act outside its defined authority scope." The human is the top authority tier — he "approves protected actions such as opening a pull request, merging work to main, or instantiating a new role, and his explicit instruction always overrides civilizational consensus" (`civic-roles.md`).

The canonical catalog adds a doctrine constraint that bounds even the policy layer: "LLM agents may not hold final release or capability-promotion authority in the MVP" (`roles-catalog.md`, quoting the v3.9 authority doctrine, line 269). So the ceiling is not only the human-as-approver pattern; certain authorities are reserved from agents entirely.

> ⚠ **Fail-legible — invariant count conflicts.** `civic-roles.md` as it stands today says "the **Fourteen** Invariants." The Open Brain capture written *when that same file was first created* (2026-06-05) records the constitution as "the Soul + Eight Agent Rights + **Ten** Invariants." The two disagree; this article does not pick a winner — the file's current text says fourteen, the authoring note said ten. The count of *agent rights* (eight) is consistent across both. (The same conflict is flagged in [[hive-governance]].)

## Two role layers, one catalog

The candidate source (`civic-roles.md`) describes **nine** runtime civic roles and is marked `status: superseded`, pointing to `docs/roles-catalog.md` as "a strict superset covering both runtime civic roles and governance policy roles." That successor catalog enumerates **24** roles in two layers:

- **Layer 1 — the nine runtime civic roles** above (sourced from `agentdef.go`).
- **Layer 2 — fifteen governance policy roles** (Operator, Product, Architect, Planner, Engineer, QA, Security, Release, Auditor, MemoryCurator, KnowledgeCurator, EvalOwner, CapabilityOptimizer, CapabilityReviewer, CapabilityRelease), sourced from the accepted v3.9 authority doctrine's `## Roles` table — "what each role is permitted to do," not separate running agents.

The catalog is explicit that the two layers come from separate sources and "neither source cross-references the other." Only one name appears in both: **Planner** (governance) and **planner** (runtime), both concerning task decomposition. The catalog refuses to invent the rest: "This catalog does not invent mappings where neither source establishes one."

> ⚠ **Fail-legible — source-status discrepancy across this run.** `civic-roles.md` is `status: superseded`. Its successor `roles-catalog.md` carried `status: draft, canonical: false` across **every** Open Brain capture of it (2026-06-08 .. 2026-06-12), pending Gate-E approval — yet the copy read this run is `status: active, canonical: true, version: 3.0.0`. Either the catalog was promoted after those captures, or the read copy is ahead of the captured history. This article treats the nine runtime civic roles as stable and well-attested (three independent sources agree on them); it treats the *promotion* of the catalog to canonical as the freshest single source, not yet cross-checked against a capture. Earlier captures also recorded **2–3** runtime↔governance correspondences (planner↔Planner, implementer↔Engineer, sometimes reviewer↔QA); the read copy of the catalog asserts only **one** (planner↔Planner). The conservative one-mapping claim is from the canonical document; the wider claims are from superseded drafts.

## Where the roles came from (chronology)

- **April 2026 — built incrementally.** Sysmon + Allocator (PRs #9 + early-April commits, ~2026-04-03/04), CTO (PRs #10/#12/#13, 2026-04-04), Spawner runtime hot-add with Guardian governance (PR #14, merged 2026-04-05). The nine starter agents are hardcoded in `agentdef.go` (Open Brain, 2026-04-09 .. 2026-04-15).
- **2026-04-08 — first emergent member.** The `researcher` becomes the first dynamically spawned agent, proving the growth loop end to end.
- **2026-06-05 — the drift, and the cure.** The reunification diagnosis finds the project built the living civic-role civilization *and* a separate accountability pipeline that "runs *beside* the civilization, not *through* it" — the gate epics "contain zero references to `guardian`/`cto`/`spawner`/`strategist`" and use their own `maintainer`/`recorded_llm` actors. "The cage was perfected; the inhabitants never moved in" (slice-1 doc). The fix: have the civic roles fulfill a real `FactoryOrder` — and the first order is to document themselves.
- **2026-06-05 / 2026-06-12 — the artifacts.** `civic-roles.md` (the prose enumeration, the candidate source) and then `roles-catalog.md` (the code-grounded 24-role superset) are produced.

> ⚠ **Fail-legible — "the society documented itself" is the *design*, not a verified outcome.** The slice-1 document is explicitly "Working design, not accepted doctrine … It graduates into v4.0 doctrine only *after* the slice actually runs." Whether the run completed exactly as specified — every step recorded by a named civic role, zero direct agent-to-agent messages — is a success *criterion* in that doc, not something the sources read this run confirm happened. The existence of `civic-roles.md` and `roles-catalog.md` shows artifacts were produced; it does not by itself prove the cooperative loop produced them autonomously and unaided. Treat the autonomous-self-documentation claim as thin until run evidence is folded into doctrine (the doc's own "Provenance" instruction).

## See also

- [[hive-governance]] — the runtime that *hosts* these roles and the fail-closed authority gate they pass protected actions through; this article is the focused view of the role society it tabulates.
- [[event-graph]] — the single append-only substrate the roles coordinate through; reading/writing it *is* their only channel.
- [[work]] — the Work DAG and readiness gate the planner attaches to and the strategist seeds.
- [[authority-layer]] — the source-philosophy consent gate (Searles / mind-zero-five); the guardian's `AuthorityRequest` is the Dark Factory realization of it.
- [[the-20-primitives]] — the seed where `Agent` is one of the twenty irreducibles; the civic roles are that primitive, specialized into a society.
- [[dark-factory]] — the governed production system the roles perform and govern.

## Sources & provenance

Compiled this run from:

- **`civic-roles.md`** (`transpara-ai/docs: dark-factory/civic-roles.md`, **`status: superseded`** → `docs/roles-catalog.md`) — the lead framing (society coordinating only through the append-only graph; defined authority scope + interface; human as top authority tier), the nine roles with one-line responsibilities, the implementer-only-filesystem-access fact, the guardian-outside-the-hierarchy fact, the spawner-as-growth-engine fact, and the constitution (Soul / Eight Agent Rights / Fourteen Invariants). Local read path: `/Transpara/transpara-ai/repos/docs/dark-factory/civic-roles.md`.
- **`roles-catalog.md`** (`transpara-ai/docs: docs/roles-catalog.md`, v3.0.0, **`status: active, canonical: true`** in the read copy; supersedes `civic-roles.md`) — the per-role code-sourced facts (`CanOperate`, `Category`, `ReportsTo`, `EscalationPath`, `WatchPatterns`, behavior), all cited to `pkg/hive/agentdef.go` `StarterAgents()`/`StarterRoleDefinitions()`; the two-layer structure (9 runtime + 15 governance = 24); the single planner↔Planner correspondence; the "LLM agents may not hold final release/capability-promotion authority" doctrine line; and the Dynamic Agents note. Local read path: `/Transpara/transpara-ai/repos/docs/docs/roles-catalog.md`.
- **`reunification/2026-06-05-slice-1-first-reunified-order-design.md`** (`transpara-ai/docs`, v0.1.2, `status: review`, `authority: planning`, `canonical: false`) — the origin (the first reunified `FactoryOrder` = "document its own society"), the cooperative-flow step→role→event table (§2), the minimal membrane (§3), the growth-loop hook (§4), the "no direct communication — only events" property, and the drift diagnosis. This is a working design, **not accepted doctrine**. Local read path: `/Transpara/transpara-ai/repos/docs/dark-factory/reunification/2026-06-05-slice-1-first-reunified-order-design.md`.
- **Open Brain captures (2026-04-03 .. 2026-06-12)** — the incremental April-2026 build chronology (Sysmon/Allocator/CTO/Spawner PRs), the intentional boot order, the growth-loop event chain, the `researcher` as the first dynamic spawn (2026-04-08), the implementer-only-`CanOperate=true` fact, the catalog's prior `status: draft, canonical: false` and the 2–3-correspondence drafts, and the earlier Guardian governance-prompt gap (2026-04-09). Used for chronology and code-fact corroboration.

No durable external (Searles) URL is load-bearing for this entity; the civic roles are a first-party Dark Factory construct. `[[wikilinks]]` to `[[event-graph]]`, `[[hive-governance]]`, `[[work]]`, and `[[authority-layer]]` are compiled siblings as of 2026-06-13; `[[the-20-primitives]]` is compiled; no `[[dark-factory]]` article exists yet. Contested or thin claims — invariant count, the catalog's canonical/draft status and correspondence count, and whether the reunified run actually executed as designed — are flagged inline rather than reconciled.
