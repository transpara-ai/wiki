---
entity: The Roles Catalog
aliases: [roles catalog, 24-role catalog, dual-layer catalog, Hive Civilization Roles Catalog, DF-ROLES-CATALOG]
tier: architecture
status: compiled
last_compiled: "2026-06-14"
sources:
  - docs/docs/roles-catalog.md  # DF-ROLES-CATALOG v3.0.0, status:active, canonical:true — exhaustive per-role tables sourced from agentdef.go (Layer 1) and v3.9 authority doctrine (Layer 2)
  - docs/dark-factory/reunification/2026-06-12-arc-state.md  # G-1.2 round-6 close state; v16-F2 oscillation defect; catalog deliverable branch history
confidence:
  sources: primary
  claims: grounded
  layer_1_nine_roles: high — code-grounded in pkg/hive/agentdef.go StarterAgents()/StarterRoleDefinitions(); identical across civic-roles.md, roles-catalog.md, and arc-state branch history
  layer_2_fifteen_roles: high — sourced from v3.9 authority doctrine ## Roles block (line 247) and ## MVP Role Permissions table (line 308); not independently read this run but cited verbatim in the canonical catalog
  canonical_promotion: grounded — roles-catalog.md carries status:active, canonical:true, version:3.0.0 in the read copy (docs#126, 2026-06-14); prior captures show status:draft/canonical:false through 2026-06-12
  society_produced_claim: asserted — "produced by the society and reviewed (not authored) by the shepherds" (catalog Provenance section); whether the cooperative loop produced it fully autonomously is thin (see fail-legible note)
  oscillation_defect: asserted — arc-state records six oscillation commits on codex/fo-roles-catalog-v16; 24-role reading at b638a44, 9-role reading at HEAD 002bcf8; attributed to v16-F2 planner scope-narrowing (root cause inferred, not code-traced this run)
---

# The Roles Catalog

**The civilization's authoritative self-description: 24 roles in two layers, written by the society and confirmed canonical on 2026-06-14.** The Roles Catalog (document ID `DF-ROLES-CATALOG`, v3.0.0) is the artifact in which the [[hive-governance]] civilization enumerates every role it recognizes — the 9 runtime agents that actually run as code (Layer A, the `StarterAgents`) plus the 15 governance policy roles drawn from the accepted v3.9 authority doctrine (Layers B–D). It is the strict superset of [[civic-roles]], which covered only the 9-role runtime layer.

The catalog was produced during [[slice-1-completion]] in G-1.2 (the sixth and final round of slice 1), supersedes the earlier `dark-factory/civic-roles.md` (status: superseded), and was promoted to `status: active, canonical: true` by docs#126 on 2026-06-14. The catalog's own provenance section states it was "produced by the society and reviewed (not authored) by the shepherds (Claude and Codex)."

## What it is and what it is not

The catalog is explicitly **not** a roadmap, a design file, or a spawner-proposed growth document. Its sources are exhaustive and named in the Provenance section: Layer 1 rows come exclusively from `StarterAgents()` and `StarterRoleDefinitions()` in `pkg/hive/agentdef.go`; Layer 2 rows come exclusively from the `## Roles` heading and `## MVP Role Permissions` table in the accepted v3.9 authority-and-SOP doctrine. No role is drawn from any other source.

This matters because it separates the catalog from two adjacent artifacts:
- [[civic-roles]] — the superseded prose document that described only the 9 runtime roles; written first, now status:superseded, pointing here as its successor.
- The spawner's growth-loop proposals — dynamic agents that emerge at runtime are deliberately excluded ("they are not registered `AgentDef` structs — they emerge at runtime").

## The two layers

### Layer A — 9 runtime civic roles (StarterAgents)

These are the bootstrap agents the [[hive-governance]] runtime actually instantiates. Each is an `AgentDef` struct returned by `StarterAgents()`, derived from a `RoleDefinition` template in `StarterRoleDefinitions()`. The `CanOperate` flag is the runtime expression of least privilege: only the implementer is `true`; all others are propose-only.

| # | Role | Category | CanOperate | Reports to |
|---|------|----------|------------|------------|
| 1 | guardian | process | false | human |
| 2 | sysmon | process | false | guardian |
| 3 | allocator | process | false | guardian |
| 4 | cto | leadership | false | human |
| 5 | spawner | staffing | false | cto |
| 6 | reviewer | technical | false | cto |
| 7 | strategist | leadership | false | cto |
| 8 | planner | technical | false | strategist |
| 9 | implementer | technical | **true** | strategist |

The guardian and cto both report to the human — not to another agent — which places the human at the ceiling of two independent escalation paths. The implementer is the only role with `CanOperate: true`; the runtime loop calls `Operate()` (real filesystem access) only for it, and `Reason()` (propose-only) for every other agent.

Boot order is intentional: integrity → health → budget → leadership → work. Guardian, Sysmon, and Allocator are up before any production agents start.

The [[civic-roles]] article covers these nine roles in full, including per-role behavior, watch patterns, iteration and duration limits, and the cooperative flow that connects them. This catalog article records the structural fact that these nine constitute Layer A of the 24-role picture.

### Layers B–D — 15 governance policy roles

These roles define **what is permitted** within the policy framework. They are not running agents; they are authority-doctrine declarations sourced from the `## Roles` block (line 247) and `## MVP Role Permissions` table (line 308) of the accepted v3.9 authority-and-SOP doctrine. The catalog links to that source document rather than duplicating the full policy-rule definitions so the two cannot drift.

| # | Role | Allowed actions (from MVP Role Permissions) |
|---|------|---------------------------------------------|
| 10 | Operator | factory_order.create, factory_order.accept, release.reject, waiver.create, waiver.approve, audit.emit |
| 11 | Product | factory_order.create, factory_order.accept, requirement.accept, waiver.create |
| 12 | Architect | planning.propose, requirement.accept, work.task.create |
| 13 | Planner | planning.propose, work.task.create |
| 14 | Engineer | runtime.invoke, repair.create, work.task.transition |
| 15 | QA | gate.run, failure.classify, work.task.transition |
| 16 | Security | gate.run, failure.classify, waiver.approve |
| 17 | Release | release.create_candidate, release.certify, release.reject |
| 18 | Auditor | audit.emit, failure.classify |
| 19 | MemoryCurator | memory.ingest, memory.retrieve |
| 20 | KnowledgeCurator | knowledge.create, knowledge.activate |
| 21 | EvalOwner | gate.run, failure.classify, evolution_order.accept |
| 22 | CapabilityOptimizer | optimization.run |
| 23 | CapabilityReviewer | capability.review, failure.classify |
| 24 | CapabilityRelease | capability.promote, capability.activate, capability.rollback |

An MVP constraint runs across the Release, CapabilityOptimizer, and CapabilityRelease roles: "LLM agents may not hold final release or capability-promotion authority in the MVP" (v3.9 doctrine, line 269, as quoted in the catalog). This bounds what any agent can be assigned, regardless of how the spawner evolves the runtime society.

## The only cross-layer correspondence

The two layers were defined in separate sources that "neither cross-reference the other." The catalog identifies exactly one name shared by both layers: **Planner** (governance, `planning.propose` + `work.task.create`) and **planner** (runtime, decomposes strategist tasks into subtasks via `work.task.created` events). Both concern task decomposition and creation.

> ⚠ The catalog is explicit: "This catalog does not invent mappings where neither source establishes one." Earlier drafts (2026-06-08 through 2026-06-12 Open Brain captures, status:draft/canonical:false) recorded 2–3 runtime↔governance correspondences (planner↔Planner, implementer↔Engineer, sometimes reviewer↔QA). The canonical v3.0.0 document asserts only the single planner↔Planner mapping. The conservative single-correspondence claim is authoritative; the wider draft-era claims are superseded.

## Society-produced status

The catalog's Provenance section records: "This catalog was produced by the society and reviewed (not authored) by the shepherds (Claude and Codex)." It was the deliverable of the [[the-reunification]] G-1.2 slice-1 run — specifically, the sixth round (v16), where the first `FactoryOrder` of the reunified civilization asked the society to document its own roles.

> ⚠ "Produced by the society" is the design intent and the provenance claim, not an independently verified outcome this run. The [[slice-1-completion]] article captures the fuller arc. The existence of the catalog and its delivery branch corroborates production; whether the cooperative loop produced it fully autonomously and unaided is thin until run evidence is folded into accepted doctrine.

## The oscillation defect (v16-F2)

The round-6 arc-state records a structural defect in the v16 run that affected the catalog's production:

**v16-F2 (planner decomposition silently narrowed FO scope → dual-spec oscillation):** The planner, when decomposing the Factory Order, silently narrowed the 24-role scope to the 9 runtime roles. The result was a "24→9 role ping-pong" across six completion cycles — six oscillation commits on `codex/fo-roles-catalog-v16`. The 24-role reading is preserved at `b638a44` in history; the subtask-scoped 9-role reading is HEAD at `002bcf8`.

The arc-state ruling resolved it: the workspace is `transpara-ai/docs`; the Factory Order's 24-role scope governs; the subtask was mis-scoped. The fix-set for v16-F2 is a spec-diff gate at subtask creation — the planner must compare the subtask's scope against the Factory Order's scope before proceeding.

The oscillation defect is why all six round-6 reviews were premised on the wrong repo (v16-F1 is a distinct defect: Reason-phase cwd). The catalog's canonical promotion (docs#126) resolved the scope question on the human-authored artifact.

> ⚠ The canonical catalog (v3.0.0, status:active, canonical:true) is the version read directly from the filesystem at `/Transpara/transpara-ai/data/repos/docs/docs/roles-catalog.md`. Prior Open Brain captures from 2026-06-08 through 2026-06-12 consistently recorded status:draft/canonical:false, pending Gate-E approval. The promotion to canonical happened after those captures — confirmed by docs#126 on 2026-06-14, which is today. This article treats the promoted version as authoritative.

## Distinction from civic-roles

The [[civic-roles]] article (compiled 2026-06-13) covers the runtime bootstrap layer in depth: per-role behavior, system prompts, watch patterns, boot chronology, the cooperative flow, the growth loop, and the authority ceiling. This article records the wider 24-role picture and the catalog's own production history.

Navigational rule: if the question is "what does the guardian do?" or "how does the spawner propose a role?" — go to [[civic-roles]]. If the question is "what is the full set of roles the civilization recognizes?" or "what can the Release governance role certify?" — the answer is here.

## See also

- [[civic-roles]] — the 9-role runtime view; this article is the 24-role superset
- [[slice-1-completion]] — the G-1.2 arc that produced this catalog as its deliverable
- [[the-reunification]] — the overarching effort to reunify the civic-role society with the governance pipeline
- [[factory-order]] — the seed instruction the civilization fulfilled to produce this catalog
- [[hive-governance]] — the runtime that hosts Layer A agents and enforces the [[event-graph]]-only coordination property
- [[event-graph]] — the append-only substrate all Layer A agents coordinate through

## Sources & provenance

Compiled from:

- **`docs/docs/roles-catalog.md`** (`transpara-ai/docs`, `DF-ROLES-CATALOG`, v3.0.0, `status: active, canonical: true`, promoted by docs#126 2026-06-14) — the canonical 24-role dual-layer catalog; all per-role fields sourced from `pkg/hive/agentdef.go` (Layer 1) and v3.9 authority doctrine `## Roles` + `## MVP Role Permissions` (Layer 2); Provenance section ("produced by the society"); Dynamic Agents exclusion; single planner↔Planner correspondence; MVP LLM authority restriction. Local read path: `/Transpara/transpara-ai/data/repos/docs/docs/roles-catalog.md`.

- **`docs/dark-factory/reunification/2026-06-12-arc-state.md`** (`transpara-ai/docs`, `DF-REUNIFY-2026-06-12-ARC-STATE`, v0.3.0, `status: draft`, `canonical: false`) — round-6 (v16) close state; v16-F2 oscillation defect description (24→9 ping-pong, six completions, six oscillation commits); catalog deliverable branch (`codex/fo-roles-catalog-v16`, HEAD `002bcf8`, 24-role reading at `b638a44`); ruling that FO's 24-role scope governs; fix-set scope (spec-diff gate at subtask creation). Local read path: `/Transpara/transpara-ai/data/repos/docs/dark-factory/reunification/2026-06-12-arc-state.md`.

- **`wiki/civic-roles.md`** (this wiki, compiled 2026-06-13) — compiled sibling article covering the Layer A nine roles in depth; used to bound scope of this article (what is already covered vs. what is new here). Local read path: `/home/transpara/transpara-ai/repos/civilization-wiki/wiki/civic-roles.md`.

**Contested or thin claims flagged inline:** (1) autonomous-society-production claim is asserted/thin — corroborated by artifact existence, not by run evidence read this session; (2) the oscillation defect is grounded in the arc-state but the arc-state itself is `canonical:false/draft`; (3) docs#126 canonical promotion is asserted from the catalog's own frontmatter, not independently verified against the PR. `[[wikilinks]]` to `[[slice-1-completion]]`, `[[the-reunification]]`, and `[[factory-order]]` are forward references; targets not yet compiled as of 2026-06-14.
