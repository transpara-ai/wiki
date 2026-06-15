---
entity: Work (Production DAG and Task Lifecycle)
aliases: [work, the work repo, transpara-ai/work, the flow system, Work DAG, the production DAG]
tier: architecture
status: compiled
last_compiled: 2026-06-15
sources:
  - raw/transpara/dark-factory/Dark Factory - Motive, Goal, Approach.md  # §5 "Use Work for Flow, not Truth"; responsibility map; register entry B/Work
  - raw/transpara/dark-factory/reunification/2026-06-09-deployment-arc.md  # as-built review of the work repo, 2026-06-09
  - Open Brain captures (2026-06-05 .. 2026-06-10)  # as-built code detail: store.go readiness gates, SeedFactoryOrder, Epic 11 client, SSE — see provenance footer
confidence:
  role_separation_doctrine: high (stated identically in two first-party docs)
  as_built_code_detail: medium — drawn from dated Open Brain captures that cite specific files/lines, not from reading the work repo this run; treat file:line references as reported, not re-verified here
  rebuildable_or_evidence_backed_constraint: stated as a doctrine constraint, partially demonstrated — see "The rebuildable-or-evidence-backed rule"
---

# Work (Production DAG and Task Lifecycle)

**Work** is one of the native-core systems of the [[dark-factory]] (repo `transpara-ai/work`). It owns the *operational* side of a factory run: the production DAG, task lifecycle, readiness/blocking/repair, and the flow from a FactoryOrder to executable Tasks. Its single most important boundary — repeated verbatim across the first-party docs — is that **it manages production flow but is explicitly not the truth kernel.** The kernel is [[event-graph]]; Work coordinates work, it does not certify it.

Work is not a freshly-introduced idea with a single origin date the way [[the-20-primitives]] is. It is the production-flow surface that the Dark Factory architecture has carried since at least the v3.9 baseline, and it has running code: the deployment-arc review of 2026-06-09 describes a working task lifecycle, FactoryOrder adapter, and live SSE telemetry already shipped in the repo.

## What Work is for

The Dark Factory orientation doc states Work's responsibility in one sentence and then guards it:

> "Work owns task lifecycle, Work DAG projections, readiness, blocking, repair, and FactoryOrder-to-Task operational flow. It does not become the truth kernel." (`Dark Factory - Motive, Goal, Approach.md` §5)

The responsibility map in the same document classifies it as **Selected native core**, with the boundary "Owns operational flow, not certification truth," and the decision register restates the reason: *"Production DAG and task lifecycle are needed, but operational flow must be separate from truth."* The constraint attached there — **"Work state must be rebuildable or evidence-backed"** — is the architectural price of letting Work hold operational state at all.

Within the end-to-end product flow, Work is step 5: after a human submits intent, the command layer creates a FactoryOrder, and a planner proposes requirements/acceptance-criteria/task-drafts, **Work creates the tasks and their dependencies** and manages the DAG that the rest of the run executes against. Two adjacent constraints from the same flow matter for Work's correctness: *unrelated tests do not satisfy acceptance criteria*, and *manual verification is limited by risk class unless explicitly waived* — Work tracks the tasks, but acceptance is judged against the declared criteria, not against whatever happened to pass.

## Flow, not truth — the load-bearing separation

The separation between Work (flow) and [[event-graph]] (truth) is the spine of the whole architecture, not a stylistic preference. The orientation doc's one-line architecture summary puts it plainly: *"The sovereign truth layer is EventGraph. Work schedules and coordinates production."* EventGraph is the sovereign source of truth for durable facts, causality, audit evidence, identity, authority, lifecycle, provenance, certification, and capability-evolution records; **no other system supersedes it for authority or certification** — and the responsibility map names Work first among the systems forbidden to bypass it ("Owns durable truth; must not be bypassed by Work, Site, Hive, Git, CI, memory, or external tools").

The document's own review questions make the failure mode explicit and treat it as a thing reviewers must actively catch:

> "Does it accidentally grant authority to Work, Site, Hive, memory, Git, CI, or external tools?"

So the doctrine is not "Work is unimportant" — it is "Work is the engine, EventGraph is the record, and the engine must never be mistaken for the record." Certification (whether a [[release-candidate]] is good) runs through the truth/gate path — TraceCompletenessGate, product gates, security gates, audit evidence — never through Work declaring a task done.

## The rebuildable-or-evidence-backed rule

The register's constraint — *Work state must be rebuildable or evidence-backed* — is what reconciles "Work holds operational state" with "EventGraph is the only truth." Two readings are consistent with the source, and the source does not fully disambiguate them:

1. **Rebuildable:** Work's DAG/readiness state is a *projection* that can be reconstructed from the events on EventGraph, so losing Work's local store loses no truth.
2. **Evidence-backed:** where Work holds state that is not a pure projection, every material fact it acts on must trace to an EventGraph record.

> ⚠ **Fail-legible note.** As written, the rule is a *doctrine constraint*, and the first-party docs assert it rather than prove it. The deployment-arc as-built review (2026-06-09) shows the proof is **partial in practice**: it flags that Slice-1 run dynamics lived in *per-run throwaway local databases* (`hive_df_slice1_v4..v7`) plus operator observation, and lists a **"durable run substrate"** as still-missing Phase-2 work — i.e. at the time of that review, run-level Work state was *not yet* reliably rebuildable from a durable shared event store. The constraint is the target; full rebuildability across restarts is explicitly future work, not a demonstrated property.

## As-built: what the work repo actually contains

The richest description of Work-as-code is the deployment-arc review's repo table (2026-06-09). Reported there, and corroborated by dated Open Brain captures that cite specific files:

- **Task lifecycle with v3.9 states + readiness gates** (`store.go`). Readiness is computed from required gate-artifact labels; an Open Brain capture (2026-06-05) reports `store.go` requires exactly three artifact labels — `definition_of_done`, `acceptance_criteria`, `test_plan` — for a task to be ready, and that `validateTaskCreateOptions` additionally requires, when a `FactoryOrderID` is set, a `Cell`, a `RiskClass`, and at least one `req_`-prefixed RequirementID and one `ac_`-prefixed AcceptanceCriterionID.
- **FactoryOrder adapter** (`work#44`): a `FactoryOrder` type with `OrderKind` constants — `OrderSoftwarePR`, `OrderGovernanceDeliberation`, `OrderResearch` — of which only `software_pr` is wired; the other two are stubbed. `SeedFactoryOrder` maps an order into a readiness-gated task.
- **Phase-gate approve/reject endpoints.**
- **SSE already shipped** (`cmd/work-server`): `/telemetry/sse` and `/events/subscribe?types=work.*,hive.*` over a Postgres poll bridge. The deployment arc notes this is the transport a future live Site visualization would consume — and that, as of the review, *Site consumed no stream at all.*
- **Epic 11 fail-closed GitHub draft-PR creator** (`work#43` / `work#45`): described as the **only live mutation path** in the whole dark-factory stack. It implements the `Epic11PullRequestCreator` interface over GitHub's REST API (`POST /repos/{owner}/{repo}/pulls` with `draft:true`), records an `ExecutionReceipt` only *after* GitHub confirms the open draft PR, and fails closed on every guard mismatch (authority-request↔decision field equality, single-use nonce, remote-head preflight). Gate F (LLM proposal) and Gate H (issue→PR) remain fixture-only by design.

> ⚠ **Fail-legible note (provenance of code detail).** The file/line/PR specifics above come from the deployment-arc doc and dated Open Brain captures (2026-06-05 .. 2026-06-10) that *claim* to be grounded against the real `work` repo. They were **not re-verified against the repo in this compile run.** Treat them as reported as-built, accurate as of early-to-mid June 2026, and subject to drift — the deployment arc itself pins the repo to a specific main (`work` at `45e7a1f`, later `26b7d80`-era hive, etc.). Code is truth; this article is a synthesis over docs and captures, not a fresh read of the code.

## Readiness, blocking, repair

Work owns the machinery that decides whether a task may be picked up:

- **Readiness** gates a task on the presence of its required gate artifacts (the three labels above); an Open Brain capture (2026-06-10) reports `Ready=false` is also set on *missing facts*, not only missing gates (`store.go:1301`).
- **Blocking** is the natural consequence: a task whose readiness conditions are unmet is not assignable, and the run does not advance past it.
- **Repair** is the loop that drives a blocked/incomplete artifact back to ready — and the deployment arc identifies this loop as the **binding constraint** for the whole reunification effort. Two open findings frame it:
  - **F7 — single-Operate producer variance:** every acceptance criterion has passed in *some* run, but no single Operate has passed all of them at once, and fresh re-runs do not converge.
  - **F8 — the review→fix loop does not engage after a restart:** the recovery re-check was scoped to `CanOperate` agents only (`hive/pkg/loop/loop.go:147`), so a keepalive Reviewer stranded on historical events.
  The recorded design bet is that *convergence comes from the review→fix loop, not from more contract text or a perfect single shot* — which makes Work's repair/readiness behavior, together with [[hive-governance]]'s loop, the thing that has to converge before the factory can be called operational.

Note these last two findings live mostly in [[hive-governance]] (the loop that *wakes* the roles), with Work supplying the readiness/assignability gate that the loop checks against. The repair *loop* is a Work-plus-Hive property, not Work alone.

## Boundaries with the rest of the stack

- **vs. [[event-graph]] (kernel):** Work coordinates; EventGraph records and certifies. Work must be rebuildable-or-evidence-backed and must not be bypassed-around-or-substituted-for as truth.
- **vs. [[hive-governance]] / governance:** Hive evaluates authority and protected actions and (later) coordinates multi-agent work; the runtime loop that wakes roles lives in Hive. Work does not decide authority — it surfaces tasks; protected actions (e.g. opening the draft PR) route through Hive's authority decision and Work's fail-closed Epic 11 creator only *after* an approved decision exists.
- **vs. RuntimeBroker / worker:** Work schedules the task; the bounded worker executes it inside a [[runtime-broker]] envelope and returns `RuntimeResult`/`Artifact`/`CodeChange`/`Failure`. Work does not execute code directly.
- **vs. Site:** Site is a read-only console; it consumes Work's evidence/telemetry (the SSE bridge) and forwards governed decisions, but does not execute work or hold truth.

## Where Work sits in the deployment arc

The 2026-06-09 deployment arc (a **proposal-only** planning document — it authorizes no implementation) is the clearest forward-looking placement of Work. Work appears across nearly every phase as the flow substrate:

- **Phase 1 (close Slice 1):** Work's Epic 11 fail-closed creator opens the draft PR as the governed terminal step; `ExecutionReceipt` only after GitHub confirms; merge only on explicit human instruction.
- **Phase 2 (always-on substrate):** the durable run substrate that makes Work state actually rebuildable across restarts (the gap flagged above).
- **Phase 3 (traceability to GitHub):** `CodeChange` carrying commit SHAs and `ExecutionReceipt` carrying the PR URL as queryable provenance; the doc notes that because EventGraph ships no HTTP surface, a GitHub-event bridge "plausibly lands in `work`."
- **Phases 4–6:** Work's phase-gate endpoints feed the unified decision queue; Work's SSE bridge is the transport the live society/factory-floor visualization would consume.
- **Phase 7:** parallel FactoryOrders (Work + Hive `RunConcurrent`), and order kinds beyond docs — `OrderSoftwarePR` against a code repo, then the stubbed `OrderGovernanceDeliberation` / `OrderResearch` (`work/factory_order.go`).

None of these are authorized by being listed; each needs its own design and authorization packet. The deployment arc is held to the corpus bar ("runtime claims cite a source path or merged PR") and explicitly is *not* implementation authority.

## Sources & provenance

- **Primary doctrine:** `Dark Factory - Motive, Goal, Approach.md` (DF-MOTIVE-GOAL-APPROACH, v0.1.5, draft, 2026-06-12) — §5 "Use Work for Flow, not Truth"; §"Repository and System Responsibility Map" (Work = Selected native core, "Owns operational flow, not certification truth"); §"Technology, Repo, Product, and Research Decision Register" B (Work, "Work state must be rebuildable or evidence-backed"); §"Expected Flow" (Work = step 5, creates tasks and dependencies); §"Review Questions" #3 (the no-authority-to-Work guard). This doc is itself a *first-read orientation draft* and not canonical; the operative baseline it points to is Dark Factory v3.9.
- **As-built + forward placement:** `dark-factory/reunification/2026-06-09-deployment-arc.md` (DF-REUNIFY-2026-06-09-DEPLOYMENT-ARC, v0.1.4, status review, `authority: planning`, `canonical: false`) — repo as-built table (the `work` row: task lifecycle + readiness gates `store.go`, FactoryOrder adapter `work#44`, phase-gate endpoints, shipped SSE on `cmd/work-server`, Epic 11 draft-PR creator `work#43/#45` as the only live mutation path); pillar scorecard; findings F7/F8; Phases 1–8 and the pillar-thread table. Proposal-only; authorizes nothing.
- **As-built code detail (reported, not re-verified this run):** Open Brain captures dated 2026-06-05 through 2026-06-10 grounding `transpara-ai/work`: `SeedFactoryOrder` + `FactoryOrder`/`OrderKind` (`factory_order.go`, work#44, commit a0a20d1); the three readiness gate-artifact labels and `validateTaskCreateOptions` requirements (`store.go`); `Ready=false` on missing facts (`store.go:1301`); the production GitHub draft-PR client (`epic11_github_client.go`, work#43/#45, status-before-decode, single-use-nonce/remote-head preflight guards). These captures cite file/line/PR specifics but were not opened against the repo during this compile.
- **Durable external URLs:** the philosophical lineage Work inherits (traceability → kernel; explicit criteria → gates) traces to Matt Searles, "20 Primitives and a Late Night" (`Searles-P1` · https://mattsearles2.substack.com/p/20-primitives-and-a-late-night), cited inside `Dark Factory - Motive, Goal, Approach.md`. Searles is *source philosophy only*, never implementation authority for Work.

No source conflict was found on Work's core doctrine (flow-not-truth, native-core, rebuildable-or-evidence-backed): the orientation doc and the deployment arc agree. The one tension surfaced above is **doctrine vs. as-built** on rebuildability — the constraint is asserted; the deployment arc shows it not yet fully demonstrated across restarts. `[[wikilinks]]` are forward references; several targets ([[dark-factory]], [[hive-governance]], [[runtime-broker]], [[release-candidate]]) are not yet compiled.

## Run-3 update (2026-06-14)

**v16-F1 — WorkDir/Reason cwd defect** (discovered slice-1 round 6, 2026-06-12; documented in `dark-factory/reunification/2026-06-12-arc-state.md`).

In `eventgraph/claude_cli.go`, the `Operate` code path correctly fails closed when `WorkDir` is not set — it refuses to run unless a working directory is explicitly provided. However, the `Reason` code path in the same file sets **no `cmd.Dir`**, meaning the reviewer subprocess inherits the daemon's current working directory rather than the task's designated workspace.

The practical consequence is significant: throughout slice-1 round 6, every review was executed in the daemon's cwd (the wrong repository) rather than in the deliverable's actual workspace. The six reviews that round 6 produced — including the catalog deliverable review on `codex/fo-roles-catalog-v16` — were all premised on the wrong directory. The arc-state doc records this directly: "Still unreviewed in the FO's sense — all six reviews were premised on the wrong repo (v16-F1)."

**Fix candidate (not yet implemented):** thread `WorkDir` into the `Reason` call through both the hive `pkg/loop` layer and the eventgraph provider, mirroring the behavior that `Operate` already enforces. The fix scope also includes an F2 spec-diff gate at subtask creation and an F3 quiescence detector, but the WorkDir threading is the load-bearing correctness fix.

**Architectural implication:** this defect means Work's task assignability and the review→fix loop — the convergence mechanism identified as the binding constraint for the reunification effort — operated without the correct source context for an entire arc round. Readiness gates and repair cycles that depended on reviewer output in round 6 must be treated as unverified. The v16-F1 fix set was at Gate-E pending Michael's authorization; that hard stop resolved on 2026-06-15 toward **Event-1 / Gate-K** (`transpara-ai/docs#132`), and absent a separate new slice-1 grant the v16-F1 fix set remains unauthorized.

**Source:** `dark-factory/reunification/2026-06-12-arc-state.md` (DF-REUNIFY-2026-06-12-ARC-STATE, v0.3.0) — v16 findings table (F1 entry); "Catalog deliverable" row ("Still unreviewed in the FO's sense — all six reviews were premised on the wrong repo (v16-F1)"); v16 fix-set scope ("F1 WorkDir threading (hive `pkg/loop` + eventgraph provider)").
