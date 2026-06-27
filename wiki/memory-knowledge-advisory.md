---
entity: Memory and Knowledge (Advisory Layer)
aliases:
  - memory and knowledge
  - the advisory layer
  - advisory-only memory
  - MemPalace
  - MemoryReference
  - KnowledgeReference
  - LLM Wiki
  - compiled knowledge
tier: architecture
status: compiled
last_compiled: 2026-06-13
sources:
  - raw/transpara/dark-factory/Dark Factory - Motive, Goal, Approach.md  # §10 "Treat Memory and Knowledge as Advisory", exec summary, decision register [DF-MOTIVE-GOAL-APPROACH v0.1.5]
  - raw/transpara/dark-factory/v3.9/06-memory-knowledge-capability-v3.9.md  # normative spec cited line-by-line by §10 [DF-V3.9-SPEC-006, accepted/canonical]
  - raw/transpara/dark-factory/archive/v2/adrs/ADR-0006-karpathy-wiki-knowledge-substrate.md  # ADR-0006: historical predecessor in the supersedes chain
confidence:
  advisory_status: high (normative, accepted spec — DF-V3.9-SPEC-006 is canonical)
  implementation_state: thin — the spec is accepted, but the orientation doc records that Base Slice 0 forbids memory/knowledge use, so the advisory layer is specified rather than demonstrated in the proven control plane (see "Implementation status" below)
---

# Memory and Knowledge (Advisory Layer)

The advisory layer is the part of the [[dark-factory]] that lets prior context and compiled knowledge **inform** factory work without ever **governing** it. It covers MemPalace-style recall storage (verbatim or near-verbatim prior context) and an LLM Wiki of compiled, reusable knowledge pages. The governing rule, stated identically in the orientation doc and the spec, is that this layer "advise[s] but do[es] not govern": it is **not** [[event-graph|EventGraph]], not policy, not certification evidence, and not authority. ([DF-MOTIVE-GOAL-APPROACH], exec summary; [DF-V3.9-SPEC-006:L39])

It is one of the platform's "no X as authority" invariants. The orientation doc's success criteria list reads, among others, *"No memory or knowledge as certification authority,"* alongside the parallel rules that there is no release without verification and no protected action without authority. ([DF-MOTIVE-GOAL-APPROACH], Top-Level Goal)

## When and why it appeared in the arc

The advisory layer is **architecture, not a dated origin moment.** Its normative home is `06-memory-knowledge-capability-v3.9.md` (handle `DF-V3.9-SPEC-006`), an *accepted, canonical* spec created 2026-05-13 and last updated 2026-06-05. The spec's frontmatter shows it supersedes a long chain of earlier memory/knowledge/capability documents reaching back to v2's ADR-0006 and v3's memory-knowledge-recall and capability-evolution docs — so the "memory advises, never governs" idea predates v3.9 and was carried and tightened across versions. ([DF-V3.9-SPEC-006] frontmatter, L1-L29)

The first-read orientation doc (`DF-MOTIVE-GOAL-APPROACH`, draft v0.1.5, updated 2026-06-12) summarizes that spec as approach step 10, *"Treat Memory and Knowledge as Advisory."* The reason it exists is the same accountability motive behind the whole factory: an agent's recalled context or a reused knowledge page can be incomplete, stale, self-serving, or poisoned, so it must leave an explicit evidence reference before it is allowed to move work — never a silent influence. ([DF-MOTIVE-GOAL-APPROACH] §10, Motive)

## The core rule: influence only with an explicit reference

Memory and knowledge can influence work **only with explicit evidence references.** Concretely:

- A **MemoryReference** must be created when memory materially influences planning, generation, repair, release review, or capability evolution. ([DF-V3.9-SPEC-006:L41])
- A **KnowledgeReference** must be created when wiki, recipe, template, external-doc, or prior-runbook content materially influences planning, generation, repair, review, or evaluation. ([DF-V3.9-SPEC-006:L113])
- If advisory memory or knowledge materially affects factory work, the system must emit the reference **with an `influence_summary` before certification can pass.** ([DF-V3.9-SPEC-006:L43])

The spec enumerates what "material influence" covers: plan selection, requirement interpretation, artifact generation, test/gate definition, repair strategy, security decision, release recommendation, capability-evolution decision, policy decision, and operator decision. ([DF-V3.9-SPEC-006:L45-L58])

Each influence reference carries a fixed minimum field set — `reference_id`, `source_system`, `source_ref`, `source_hash` / immutable locator, `retrieved_at`, `used_by_actor`, `used_in_task`, `influence_summary`, `risk_scope`, `trust_level`, `freshness_status`, `redaction_state`, and `contradiction_refs`. This is what makes the influence auditable rather than a black box. ([DF-V3.9-SPEC-006:L60-L76])

This is the advisory analog of the platform's broader rule that intelligence is just one operation type inside the accountability system ([[intelligence-is-an-operation-type]]): a recall is allowed to feed work, but only as a recorded, traceable input — never as the truth or the decision.

## Three fail-closed guardrails

The one-line summary for this entity names three hard blocks. All three are in the spec, and all are written as DENY-by-default conditions (which matches the platform's fail-safe posture — see "Fail-legible notes"):

1. **Secret-bearing memory is quarantined; quarantined memory cannot be used.** "Quarantined" is a terminal trust level — memory carries trust levels `raw`, `user_confirmed`, `system_observed`, `reviewed`, `deprecated`, `quarantined`, and ingestion classes `public`, `internal`, `confidential`, `secret`. ([DF-V3.9-SPEC-006:L78-L98])
2. **Stale knowledge is blocked for high-risk planning.** Only `reviewed` or `active` knowledge may be used in medium-or-higher-risk planning, and stale knowledge is blocked for high-risk planning specifically. Staleness is defined by per-class freshness windows (e.g. `dependency_recipe` 30 days, `framework_recipe` 90 days, `architecture_pattern` 180 days, `security_recipe` 30 days). ([DF-V3.9-SPEC-006:L115, L128-L139])
3. **High/critical contradictions block high-risk advisory use.** Contradictions between memory, knowledge, and EventGraph must create a `ContradictionLog` (subject, EventGraph ref, memory/knowledge ref, severity `low|medium|high|critical`, status `open|resolved|accepted_conflict`, reviewer). **Open high or critical contradictions block use in high-risk decisions.** ([DF-V3.9-SPEC-006:L234-L250])

The spec also lists explicit "poisoning indicators" — memory contradicting EventGraph, retrieved memory requesting secrets or authority expansion, knowledge instructing gate bypass, an unattributable source, or content conflicting with active policy — which is the trigger set the quarantine/contradiction machinery is meant to catch. ([DF-V3.9-SPEC-006:L252-L258])

## Memory vs. knowledge

The spec separates two stores with different shapes:

- **Memory (MemPalace or equivalent recall storage)** holds verbatim or near-verbatim prior context. It is advisory; it is not EventGraph, policy, certification evidence, or authority. ([DF-V3.9-SPEC-006:L39])
- **Knowledge (LLM Wiki or equivalent)** is *compiled reusable knowledge* — pages such as `Recipe`, `Pattern`, `FailureTaxonomy`, `RepairPlaybook`, `BenchmarkLesson`, `TemplateDoc`, `ModelBehaviorNote`, `ToolUsageNote`, `ArchitectureNote`, `ContradictionLog`. Knowledge is "advisory unless validated by EventGraph evidence," with its own lifecycle (`draft -> reviewed -> active -> stale | retired`, `active -> quarantined`). ([DF-V3.9-SPEC-006:L109-L154, L224-L230])

Note the self-referential detail: this Civilization Wiki *is itself* an LLM Wiki of compiled knowledge in the sense the spec defines. The spec even prescribes the wiki layout (`index.md`, `log.md`, `concepts/`, `entities/`, etc.), required page frontmatter (`source_refs`, `validation_status`, `trust_scope`, `last_lint`), and required lint checks (orphan pages, missing source_refs, stale claims, contradictions, unsupported synthesis, missing cross-links). By the spec's own rule, anything in such a wiki is advisory unless validated by EventGraph evidence. ([DF-V3.9-SPEC-006:L180-L222])

## What it is not — and what it does not replace

The orientation doc is emphatic that Dark Factory is "not a memory system alone," and that the category system exists partly to stop "a memory substrate from becoming truth." In the responsibility map and decision register, EventGraph is the single sovereign truth/authority/certification substrate that "must not be bypassed by Work, Site, Hive, Git, CI, memory, or external tools." ([DF-MOTIVE-GOAL-APPROACH], What Dark Factory Is Not; Why These Categories; Responsibility Map)

Two adjacent optional patterns sit under this layer but are explicitly **not** authority either:

- **DocumentEvidenceRetriever** — an optional adapter for page/section/source-grounded evidence from long documents. It "does not create truth, certify releases, approve actions, or replace KnowledgePage." Its output is usable only once represented as a `KnowledgeReference`/`source_refs` and linked to EventGraph evidence. **PageIndex** is named only as an optional reference for it and is not required unless a later accepted decision adopts it. ([DF-V3.9-SPEC-006:L156-L178])

In the decision register, memory/knowledge sits in the **"Included advisory candidate"** category — *"May be used later for advisory influence, with evidence and quarantine rules"* — distinct from the "Selected native core" systems ([[event-graph|EventGraph]], [[work|Work]], [[hive-governance|Hive/governance]], [[runtime-broker|RuntimeBroker]], [[site|Site]]). ([DF-MOTIVE-GOAL-APPROACH], Decision Categories)

## Relationship to capability evolution

The advisory layer shares a spec file with [[capability-evolution]] (`DF-V3.9-SPEC-006` also defines `CapabilityArtifact`, `EvolutionOrder`, promotion gates, and rollback). The connection is that advisory memory/knowledge can *materially influence* a capability-evolution decision — and when it does, a MemoryReference/KnowledgeReference is required just as for planning or repair. Capability evolution itself is governed as production work (eval, human review, rollback), not as an uncontrolled self-improvement loop — but that is the subject of its own article. ([DF-V3.9-SPEC-006:L41, L45-L58]; [DF-MOTIVE-GOAL-APPROACH] §11)

## Implementation status

> ⚠ **Fail-legible note — specified, not yet demonstrated in the proven control plane.** The spec is *accepted and canonical*, but the orientation doc's mandatory control-plane proof, **Base Slice 0, explicitly forbids memory recall and knowledge reuse** (alongside LLM planning, real generation, external runtime, and capability evolution). So the advisory layer's guardrails are normatively specified and test-listed, but they are out of scope for the first proven slice — i.e. specified ahead of being exercised in the baseline. The spec lists the required tests (secret-bearing memory quarantined; stale knowledge not used in high-risk planning; raw memory cannot satisfy release evidence; contradiction blocks high-risk use; references record trust/validation), but this article does not assert those tests are passing in the current build. Treat live enforcement as **unverified from these two sources.** ([DF-MOTIVE-GOAL-APPROACH], Base Slice 0 Flow; [DF-V3.9-SPEC-006:L436-L450])

## Fail-legible notes

- **The advisory-only status is high-confidence.** It is stated identically in a *draft* orientation doc and an *accepted, canonical* normative spec, and the orientation doc cites the spec line-by-line for these exact claims. No conflict between the two sources was found on this entity.
- **The guardrails are written allowlist-style / fail-closed**, consistent with the platform's "default to DENY" posture: only `reviewed`/`active` knowledge may be used at medium+ risk; quarantined memory "cannot be used"; open high/critical contradictions "block use." This is a strength to preserve — none of these is phrased as a denylist of forbidden cases.
- **"Material influence" depends on a judgment call.** The spec defines *what* counts as material influence and *what fields* the reference needs, but whether a given recall "materially" influenced a decision is an actor/system determination; the sources do not specify an automated detector. This is a thin spot worth flagging for anyone implementing it.
- **Storage names are examples, not commitments.** "MemPalace," "LLM Wiki," "PageIndex," and "DocumentEvidenceRetriever" are named as *"or equivalent"* / *optional* — the spec binds the *rules* (advisory, referenced, quarantined, fresh, non-contradictory), not the specific products.

## Sources & provenance

- `raw/transpara/dark-factory/v3.9/06-memory-knowledge-capability-v3.9.md` — **`DF-V3.9-SPEC-006`**, *Dark Factory v3.9 Memory Knowledge And Capability Evolution* (status: accepted; canonical: true; created 2026-05-13, updated 2026-06-05). The normative source for every memory/knowledge/contradiction claim above; line citations (`:Lnn`) refer to this file as read this run.
- `raw/transpara/dark-factory/Dark Factory - Motive, Goal, Approach.md` — **`DF-MOTIVE-GOAL-APPROACH`**, first-read orientation draft v0.1.5 (status: draft, canonical: false; updated 2026-06-12). Source for §10 "Treat Memory and Knowledge as Advisory," the executive-summary "advise but do not govern" line, the "no memory or knowledge as certification authority" success criterion, Base Slice 0 exclusions, and the decision-register category.
- Open Brain was queried for chronology/history on this entity; no thought specifically about the advisory layer was found, so dates and lineage above rest on the two dark-factory docs' own frontmatter and bodies.

`[[wikilinks]]` are forward references; some targets (e.g. [[capability-evolution]], [[dark-factory]]) may not yet be compiled.
