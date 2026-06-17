---
entity: The Civilization (One Civilization, One Business)
aliases:
  - the civilization
  - one civilization one business
  - the reunified factory
  - the north star
  - the factory is the civilization at work
tier: architecture
status: compiled
last_compiled: 2026-06-15
sources:
  - raw/transpara/dark-factory/reunification/README.md  # DF-REUNIFY-README v0.6.0, 2026-06-05..2026-06-10
  - raw/transpara/dark-factory/reunification/2026-06-05-slice-1-first-reunified-order-design.md  # DF-REUNIFY-2026-06-05-SLICE-1-DESIGN v0.1.2
  - raw/transpara/dark-factory/civic-roles.md  # superseded by docs/roles-catalog.md
  - raw/transpara/dark-factory/Dark Factory - Motive, Goal, Approach.md  # DF-MOTIVE-GOAL-APPROACH v0.1.5
  - Open Brain — reunification checkpoint (2026-06-05) and v4.0 doctrine-acceptance thought (2026-06-12)
confidence:
  north_star_as_doctrine: medium — agreed direction recorded 2026-06-05, but the reunification artifacts are authority:planning only; this is the *intended* model, demonstrated by one slice, not accepted v4.0 doctrine
  invariants_count: contested — civic-roles.md (current text) and the slice docs say "Fourteen Invariants"; the Open Brain capture of civic-roles.md's creation (2026-06-05) and the doc's own creation note say "Ten Invariants". Disagreement stated in-body; neither silently chosen.
  growth_loop_in_production: asserted, not proven — wired and observable but deliberately dormant in Slice 1; no source shows it firing on a real factory gap
---

# The Civilization (One Civilization, One Business)

**The north-star model for Dark Factory**, named and chosen on **2026-06-05**. Its one-line claim: *one civilization, one business* — the [[hive-governance]] civic roles and the growth loop *perform and govern* the factory, with the v3.9 accountability machinery acting as the **membrane** they work inside, **not** a separate pipeline running beside them. It is governed by a constitution — the **Soul**, the **Eight Agent Rights**, and the **Fourteen Invariants** (see the conflict flagged below) — with the human (Michael Saucier) as the **top authority tier**.

This is an *architecture-of-intent*, not (yet) accepted doctrine. The reunification artifacts that define it are explicitly `authority: planning` — "no implementation authority, no file relocation, no change to current v3.9 or v4.0 status." The model is being proven **demonstration-first** through running slices, then the corrected v4.0 doctrine is to be *extracted from what actually happened* rather than written ahead of a run.

## Why it appeared: the drift it corrects

The Civilization model exists as a correction. According to the reunification design ([DF-REUNIFY-2026-06-05-SLICE-1-DESIGN]) and the 2026-06-05 Open Brain reunification checkpoint, the project had built **two systems on one [[event-graph]] substrate that never connected**:

1. a **living [[hive-governance]] civilization** — a real, working emergent-agent growth loop (`hive/pkg/hive` + `pkg/loop`), with bootstrap civic roles; and
2. a **Dark Factory accountability pipeline** — the `work/epic*.go` Gate F–J fixtures.

The accountability pipeline ran *beside* the civilization, not *through* it. The diagnosis is **reproducible from source**: `grep -rnE 'guardian|cto|spawner|strategist' work/epic*.go` returns no civic-role references — the epics use their own `maintainer` / `recorded_llm` actors. The design states the consequence bluntly: "the accountability machinery (envelopes, authority, evidence, gates A–J) became the product; the civic roles survive only as a permission ACL in two spec files; v4.0 enthroned the human committee, not the Hive Mind." The Open Brain checkpoint records the same finding with a vocabulary count (in v3.9: `gate` ×1865, `evidence` ×1097 vs `civilization` ×8, `hive-mind` ×0) and the memorable summary: **"The factory perfected the cage and never moved the inhabitants in."**

So the membrane inversion is the whole point: accountability was *meant* to be the membrane the civilization acts within; it had become the product. Reunification re-centers the program on the civilization doing the work, with the gates folded back in as the membrane.

> ⚠ **Fail-legible note (drift evidence).** The drift diagnosis above traces to two sources I read this run: the slice-1 design's own "Provenance of the framing" (the `grep` is quoted there) and the 2026-06-05 Open Brain reunification checkpoint. The vocabulary counts (×1865 / ×8 / ×0) come from the Open Brain capture, not from a file I opened this run — treat the exact numbers as that capture's claim.

## The five inversions ("the factory is the civilization at work")

The slice-1 design states the destination as five inversions ([DF-REUNIFY-2026-06-05-SLICE-1-DESIGN], §"Destination"):

1. **The order is the unit of cooperation.** A `FactoryOrder` enters as [[the-work-graph|Work]]; the civic roles fulfill it by emitting events on the shared graph, instead of an epic running as a closed fixture.
2. **Gates become role-enforced checks**, applied inside the cooperative flow by Reviewer and Guardian. Evidence is a *byproduct* of roles working, not a separately-assembled product.
3. **The Hive Mind governs.** Guardian + council are the governance; the human is the **top authority tier** (Required actions escalate to a human), not the terminal doer.
4. **The growth loop runs in production.** A capability gap during an order triggers `CTO → Spawner → Guardian → Allocator → spawnDynamicAgent`.
5. **The visualization shows the society building the order** — which role did what — not abstract forensic tiers.

## The civic roles that perform the work

The civilization is "a society of cooperating agent roles that coordinate exclusively through a shared, append-only event graph — no role communicates out-of-band or holds private state that isn't visible to the graph" ([[civic-roles]], the superseded `civic-roles.md`). Coordination is **only through graph events**; there is no direct agent-to-agent messaging — the design cites `hive/ARCHITECTURE.md` ("No direct communication — only events") and calls this "the hive-mind property, obtained for free."

`civic-roles.md` enumerates **nine** runtime civic roles, each with a defined scope of authority and interface:

- **strategist** — owns the big picture; decomposes a Factory Order into high-level work units on the graph.
- **planner** — breaks work units into concrete tasks and attaches the **readiness contract** (definition of done, acceptance criteria, test plan) before any implementation begins.
- **implementer** — the **only** civic role with direct filesystem access; reads the readiness contract, writes the artifact, commits, records the commit hash. (Open Brain corroborates: only the implementer has `CanOperate=true`.)
- **reviewer** — the quality and **trace-completeness** gate between completed work and acceptance.
- **guardian** — an **integrity monitor outside the normal task hierarchy** that watches the graph for constitutional-invariant violations (secret exposure, unauthorized upstream pushes, privilege escalation) and either raises an authority request to the human or halts the run.
- **cto** — technical leadership; identifies capability gaps and issues directives that shape planner/implementer work.
- **spawner** — the **growth engine**; proposes a new civic-role definition (responsibility, authority scope, readiness contract) for human approval when no existing role can fill a gap.
- **allocator** — manages resources and budget (compute spend, token budgets, quotas); pauses or requests a budget increase before approved limits are exceeded.
- **sysmon** — health monitor of the running civilization (process liveness, event-graph integrity, chain continuity, dependency reachability); alerts or halts on degraded infrastructure.

> ⚠ **Fail-legible note (roster scope).** `civic-roles.md` is **superseded**. Its own front matter points to `docs/roles-catalog.md`, "a strict superset covering both runtime civic roles and governance policy roles." Per Open Brain (2026-06-11/06-12), the catalog enumerates **24** roles: these 9 runtime civic roles *plus* 15 governance policy roles from the v3.9 authority doctrine (Operator, Product, Architect, Planner, Engineer, QA, Security, Release, Auditor, MemoryCurator, KnowledgeCurator, EvalOwner, CapabilityOptimizer, CapabilityReviewer, CapabilityRelease). The roles-catalog file itself was not read this run — the 24-role figure and the governance-role list are the Open Brain capture's claim, not a file I opened. The "nine civic roles" here are the *runtime* society; the broader governance roster lives in [[roles-catalog]].

## The growth loop (wired, deliberately dormant)

The civilization's growth engine is a real loop in the running code, not a planned feature. The slice-1 design and the Open Brain checkpoint trace it as:

```
CTO /gap → hive.gap.detected → Spawner /spawn → hive.role.proposed
  → Guardian /approve → hive.role.approved → Allocator /budget
  → hive/pkg/hive/watch.go:spawnDynamicAgent  (behind authorizeProtectedAction)
```

New agents always spawn `CanOperate=false` (trust-gated), "as the code already enforces." In the first slice the loop is **wired and observable but dormant** — the design explicitly does *not* manufacture a capability gap; it only feeds the order's task flow into the CTO leadership briefing so the loop *can* see factory gaps. Inversion #4 ("the growth loop runs in production") is therefore the part of the north star most clearly **asserted but not yet demonstrated**.

## The membrane (v3.9 machinery, repurposed)

The defining structural claim — what makes this *one* civilization rather than two systems — is that the v3.9 accountability machinery becomes the **membrane** the roles act within, not a parallel pipeline. The reunification README states this directly: "the accountability machinery as the membrane they work inside, not a separate pipeline." The slice-1 design keeps the membrane **minimal** (three gates only), each owned by a role rather than a separate harness:

- **Readiness gate** — the Planner's three artifacts (definition of done, acceptance criteria, test plan), already enforced today in `work/store.go:Readiness` (invoked in `pkg/loop/tasks.go`).
- **Trace-completeness** — the Reviewer verifies every material step left an event, reusing the darkfactory `TraceCompleteness` record concept (`eventgraph/go/pkg/darkfactory/v39`).
- **Authority gate** — a protected action (creating a real draft PR) makes the **Guardian raise an `AuthorityRequest` that escalates to the human via the Site Gate-E decision surface**. Site stays a pure console: it forwards the approval as a governed decision with `effect=none` preserved and supplies *no* policy evidence; the **Hive orchestrator** assembles the Epic 11 evidence and **Work's fail-closed creator** performs the single GitHub mutation, re-validating the policy-bundle hash and `head_exists_on_origin` before the call.

This membrane reuses, rather than retires, the v3.9 evidence model. It is the same accountability substrate Dark Factory always required — [[event-graph]] as sovereign truth, explicit acceptance criteria and gates, bounded runtime, authority records — described in the orientation doc as the conversion of a failure-tracing philosophy into governed production (*Dark Factory - Motive, Goal, Approach*; [[the-20-primitives]]). The Civilization model does not replace that machinery; it puts the inhabitants inside it.

## Governance: the constitution and the human authority tier

All civic roles operate inside the civilization's **constitution**. `civic-roles.md` describes it as three parts:

- the **Soul** — the ethical and priority ordering;
- the **Eight Agent Rights** — the protections every agent is entitled to;
- the **Invariants** — the hard behavioral rules no role may violate (count contested — see below).

**Michael Saucier is the top authority tier.** He approves protected actions that cannot be delegated to the civilization — opening a pull request, merging to main, instantiating a new role — and "his explicit instruction always overrides civilizational consensus." Every consequential decision is recorded on the append-only event graph so the full audit trail is reviewable. This is inversion #3 made concrete: the Hive Mind governs day to day; the human is the escalation ceiling, not the terminal doer.

> ⚠ **Fail-legible note (contested: how many invariants).** Sources disagree on the count.
> - **"Fourteen Invariants"**: the current text of `civic-roles.md` (its Governance section), the reunification README's framing, and this entity's brief.
> - **"Ten Invariants"**: the Open Brain capture written *at the moment `civic-roles.md` was created* (2026-06-05) records the constitution as "the Soul + Eight Agent Rights + **Ten** Invariants," and the doc's own creation note says the same.
> The most likely reconciliation is that the file was revised from Ten to Fourteen after its initial creation, leaving the creation-time memory stale — but **no source I read this run states the revision explicitly**, so I am not asserting it as fact. Both counts are cited; neither is silently chosen. The authoritative current number should be confirmed against the live constitution doc / [[roles-catalog]], which were not read this run.

## Status: intent demonstrated, not doctrine

The Civilization model is the **agreed direction**, proven through slices — it is **not** accepted v4.0 doctrine. The distinctions, all traceable to sources read this run:

- The reunification workstream is `authority: planning`. It "does **not** supersede v3.9 (operative) or accept v4.0 (candidate)" ([DF-REUNIFY-README]).
- **v3.9 remains the operative implementation baseline.** The orientation doc and the 2026-06-12 Open Brain thought confirm it.
- **v4.0 seed doctrine *was* accepted** by the External Committee on 2026-06-12 (DF-V4.0-ADR-001 flipped review → accepted; checkpoint `checkpoint-2026-06-12-v4.0-doctrine-acceptance.md`). But the v4.0 *folder/integration program* remains a **candidate**, not canonical, "until the required reconciliation coverage matrix exists." v4.0's doctrine — "the development process itself must become a governed Civilization function: the factory builds the factory under the same accountability it imposes on what it builds" — is the doctrinal sibling of this north star. The program advances one bounded packet at a time — **Event 1 (Gate K) was granted on 2026-06-15** (docs#132) and later closed for pre-live sequencing by the 2026-06-17 docs#138 waiver; Event 2, live/go-live revalidation, and folder-canonical acceptance remain proposal-only or blocked.
- The slice-1 design is "**Working design, not accepted doctrine.**" It graduates into v4.0 doctrine only *after* the slice runs, "so that the doctrine is extracted from a real run rather than written ahead of one." When a slice runs and is accepted, results fold into v4.0 via the migration register (`reorganization/source-register.yaml`).

So the Civilization is best read as **the model the program is converging toward and actively demonstrating**, with the v3.9 membrane and the running [[hive-governance]] as the parts that already exist, and full Hive-Mind governance of the factory as the part still being earned slice by slice.

## What grew from it

- **The first reunified order:** Slice 1 had the civic roles document *their own society* — the [[hive-governance]] building `dark-factory/civic-roles.md` end-to-end (strategist → planner → implementer → reviewer → guardian → human approval → draft PR), "the civilization's first reunified act is to document its own society." That artifact is the seed of [[civic-roles]] / [[roles-catalog]].
- **The replacement visualization:** the "order built by the society" role-timeline view, the deliberate antidote to the "ten forensic tiers."
- **The deployment arc:** later reunification artifacts (2026-06-09 deployment arc, 2026-06-10 execution plan) carry the model forward from the Slice-1 frontier toward a continuously operated factory — proposal-only, one packet at a time.

## Sources & provenance

Compiled this run from:

- `dark-factory/reunification/README.md` (DF-REUNIFY-README, v0.6.0, 2026-06-05 → 2026-06-10) — the north-star statement ("one civilization, one business"), the membrane framing, demonstration-first approach, and the v3.9-operative / v4.0-candidate relationship.
- `dark-factory/reunification/2026-06-05-slice-1-first-reunified-order-design.md` (DF-REUNIFY-2026-06-05-SLICE-1-DESIGN, v0.1.2) — the drift diagnosis (with the reproducible `grep`), the five inversions, the cooperative flow, the three-gate membrane, the wired-but-dormant growth loop, and the "not accepted doctrine" status.
- `dark-factory/civic-roles.md` (superseded by `docs/roles-catalog.md`) — the nine civic roles, the events-only coordination property, and the constitution (Soul + Eight Agent Rights + Invariants) with the human as top authority tier.
- `dark-factory/Dark Factory - Motive, Goal, Approach.md` (DF-MOTIVE-GOAL-APPROACH, v0.1.5) — v3.9-as-operative-baseline, the v4.0 doctrine summary, and the accountability-machinery context the membrane reuses.
- **Open Brain** — the 2026-06-05 reunification checkpoint (north-star decision, drift diagnosis, vocabulary counts, growth-loop trace, the "perfected the cage" summary; *source of the Ten-Invariants reading*), the 2026-06-11/06-12 roles-catalog thoughts (24-role superset), and the 2026-06-12 v4.0 doctrine-acceptance thought (v4.0 seed accepted; folder still candidate; v3.9 operative).

Durable external reference for the underlying philosophy (via the citation table in *Dark Factory - Motive, Goal, Approach.md*): Matt Searles, *"20 Primitives and a Late Night"* — `https://mattsearles2.substack.com/p/20-primitives-and-a-late-night` [Searles-P1]; *"The Cult Test"* — `https://mattsearles2.substack.com/p/the-cult-test` [Searles-Cult-Test] (the guardrail that the framework is a tool, not truth — relevant to reading "one civilization" as a model, not a metaphysics).

Conflicts surfaced rather than resolved: the **Invariants count** (Fourteen vs Ten — see the governance note) and the **role-roster scope** (nine runtime roles in `civic-roles.md` vs 24 in the superseding catalog). `[[wikilinks]]` are forward references; several targets ([[hive-governance]], [[roles-catalog]], [[the-work-graph]], [[event-graph]]) may not yet be compiled.
