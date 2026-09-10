---
entity: Capability Evolution (Governed Self-Improvement)
org: transpara-ai
primary_placement: civilization/architecture
placements:
  - civilization/architecture
classification: internal
aliases: [capability evolution, governed self-improvement, CapabilityArtifact, EvolutionOrder, capability promotion, capability-evolution chain, optimizer constraints, OptimizationRun]
tier: architecture
status: compiled
last_compiled: 2026-06-13
sources:
  - raw/transpara/dark-factory/Dark Factory - Motive, Goal, Approach.md  # §11 "Treat Capability Evolution as Production Work" (L193-197), "Capability Evolution Flow" (L275-290), executive summary self-improvement line (L74), motive crosswalk (L130), goal invariant (L104, L108), Base Slice 0 exclusion (L253), eval-tooling register E + citation handles cite DF-V3.9-SPEC-006:L49-L302 and DF-V3.9-EVAL-005:L197-233
  - raw/searles/all-posts-1.md  # "The Architecture of Accountable AI" (2026-02-28) [Searles-P3] — mind-zero-five self-improvement circuit breaker, the philosophical ancestor
  - Open Brain (mcp__open-brain__search_thoughts, queried 2026-06-13)  # transpara-ai/eventgraph PRs #40, #45 — the E2 capability-evolution MVP implementation and two adversarial-review rounds; deployment-arc note (docs#114) on P7 contract self-evolution through the capability-evolution chain
confidence:
  doctrinal_chain_and_optimizer_constraints: high — the ten-stage chain and the six optimizer prohibitions are quoted near-verbatim from the primary orientation doc (L193-197, L275-290), which in turn cites the v3.9 spec DF-V3.9-SPEC-006
  v3.9_spec_line_citations: medium — the underlying spec file dark-factory/v3.9/06-memory-knowledge-capability-v3.9.md was NOT read this run; line ranges (e.g. SPEC-006:L272-302) are reproduced from the orientation doc's own citation handles, not verified against the spec
  implementation_status_eventgraph: medium — the claim that the chain is implemented (and twice adversarially hardened) in transpara-ai/eventgraph PRs #40/#45 comes from Open Brain review captures dated 2026-05-17, not from reading the eventgraph code this run; the captures are detailed and self-consistent but are one author's review notes
  text_only_MVP_scope: high — the MVP exclusion list (no runtime-code mutation, no auto-merge, no continuous loops) is stated directly in the primary doc (L290)
  gates_fail_open_in_practice: the doctrine says optimizers "may not" do six things; Open Brain shows the FIRST implementation let several of them through (helper-only gates bypassable via direct AppendRecord/AppendEdge), fixed only after adversarial review — so "cannot" is an achieved-then-hardened property of specific commits, not a free guarantee of the model
---

# Capability Evolution (Governed Self-Improvement)

**Capability Evolution** is [[dark-factory]]'s answer to the most dangerous thing an AI software factory can do: improve itself. The factory's tools are not frozen — its reusable skills, prompt sections, tool descriptions, runtime adapters, and policy bundles can change, and changing them changes how the whole factory behaves. The model treats every such change as **governed production work flowing through a chain of evidence**, not as an autonomous optimization loop. The one-line statement of intent from the orientation doctrine is exact: *"Capability evolution is production work, not an uncontrolled self-improvement loop."* ([Dark Factory - Motive, Goal, Approach.md], L74).

This is the [[dark-factory]] descendant of an idea that appears much earlier in the arc. On **2026-02-28**, in *"The Architecture of Accountable AI,"* Matt Searles described mind-zero-five's [[self-improvement-circuit-breaker]]: a mind that can identify its own deficiencies, propose fixes, and implement them, *"but it cannot skip the authority gate."* ([Searles-P3]; see [[accountable-ai-architecture]]). Dark Factory takes that single circuit breaker and expands it into a full production pipeline. In the motive crosswalk the lineage is written as a one-liner: *"self-improvement becomes EvolutionOrder, eval, human review, activation policy, and rollback"* (L130).

## What counts as a capability

The doctrine draws the boundary by **effect, not by file type.** Anything that *"can affect factory behavior"* is a **CapabilityArtifact** (L195). The enumerated set is broad:

> reusable skills, plugins, prompt sections, tool descriptions, workflow packs, schema instructions, evaluation prompts, runtime adapters, and policy bundles

The point of the wide net is that all of these are normally treated as "just configuration" or "just prompts" — the soft, editable parts of a system that people change without ceremony. Dark Factory's claim is that because they steer model behaviour, they deserve the same provenance, evaluation, and rollback discipline as code. A change to a tool description or an evaluation prompt is a change to the factory, and must leave evidence like any other.

## The ten-stage chain

When a capability is to be improved, the change moves through a fixed sequence of typed records. The orientation doc gives it as the **Capability Evolution Flow** (L275-290):

```
EvolutionOrder
  -> EvalDataset
  -> OptimizationRun
  -> CandidateVariant
  -> BenchmarkResult
  -> HumanReview
  -> CapabilityVersion
  -> ActivationPolicy
  -> FactoryRuntimeVersion
  -> RollbackRecord when needed
```

Read as a pipeline:

- **EvolutionOrder** — the durable starting object, the capability-side analogue of a [[factory-order|FactoryOrder]]. Nothing is improved without one.
- **EvalDataset** — the held evidence the candidate will be measured against, fixed *before* optimization so the target cannot be moved to fit the result.
- **OptimizationRun → CandidateVariant** — an optimizer proposes one or more candidate versions of the artifact. This is the only step an optimizer owns.
- **BenchmarkResult** — the candidate is scored against the EvalDataset. Benchmarks are the gate, not a courtesy.
- **HumanReview** — a human (in the implementation, an actor with the `CapabilityReviewer` role) must approve. This is the consent step inherited from the circuit breaker.
- **CapabilityVersion** — the approved, promoted version becomes a first-class, identity-bearing record.
- **ActivationPolicy** — scope of activation is itself a governed decision: a single order, a project, a canary percentage, or disabled — never silently global.
- **FactoryRuntimeVersion** — the active set of capabilities the factory is running, captured as a bill of materials (the same FRV that release certification checks; see [[gates]]).
- **RollbackRecord** — kept available so any activation can be reversed.

This chain is the capability-side mirror of the product work chain ([[factory-order]] → tasks → gates → [[release-candidate]] → certification): both refuse to let an output be trusted on assertion, and both make the [[event-graph]] the place where the evidence lives.

## The optimizer is on a leash

The load-bearing constraint is not the chain itself but **what the optimizer is forbidden to do.** The orientation doc states it as a flat prohibition list (L197):

> Optimizers may propose improvements, but may not merge, activate changes, bypass benchmarks, weaken security/policy gates, promote their own outputs, or become the factory controller.

This is the principle that keeps "self-improvement" from collapsing into "the optimizer rewrites the rules that constrain the optimizer." An optimizer's authority ends at **CandidateVariant**. Everything downstream — benchmarking, human review, promotion, activation scope — is outside its reach. It cannot grade its own homework (no promoting its own outputs), cannot lower the bar (no weakening gates, no bypassing benchmarks), and cannot seize the steering wheel (no becoming the controller). It is one operation type inside the accountability system, exactly as [[intelligence-is-an-operation-type|intelligence is treated as an operation type]] everywhere else in the factory.

Two platform-wide invariants in the goal section restate the same boundary from the outside (L104, L108):

> No capability promotion without eval, review, and rollback.
> No expanded autonomy unless audit and rollback improve with it.

The second is the more radical of the two: it says the factory may only grow more autonomous if its ability to *see and undo* what it did grows at least as fast. Autonomy is gated on reversibility.

## The MVP is deliberately small

The doctrine does not switch the whole loop on at once. The first version is **text-only** and excludes most of what makes self-improvement frightening (L290):

> The MVP allows text-only optimization first: skills, tool descriptions, and prompt sections. It excludes runtime code mutation, tool implementation mutation, policy changes, global prompt activation, auto-merge, automatic activation, and continuous loops.

So in the MVP an optimizer may rewrite *what a tool says it does* but not *what the tool's code does*; it may tune a prompt section but not change a policy; nothing activates globally, nothing merges itself, and nothing runs continuously. Capability evolution is also explicitly **forbidden in Base Slice 0**, the mandatory control-plane proof that must pass before any higher autonomy — that slice may not use *"memory recall, knowledge reuse, or capability evolution"* at all (L253). The capability loop is something the factory earns access to, not a starting condition.

## How the doctrine held up in real code (fail-legible)

The orientation doc says optimizers *"may not"* do six things. Whether they *can* is a property of the implementation, and the implementation history shows this is **earned, not free.**

The chain was built as the **E2 capability-evolution MVP** in `transpara-ai/eventgraph` and went through two rounds of adversarial review in May 2026 (Open Brain captures, 2026-05-17). The first version (PR #40, pre-hardening) implemented the gates as **helpers** — the checks lived inside `PromoteCapabilityVersion` / `ActivateCapabilityVersion`, but the underlying `Store.AppendRecord` and `Store.AppendEdge` had no type-aware predicates. The review's verdict: *"direct AppendRecord/AppendEdge bypasses every gate."* Concretely, the first cut let an attacker:

- **activate without promoting** — append a `CapabilityVersion` with status `approved` directly, and activation succeeded with no check that it had ever passed promotion;
- **reuse evidence** — gates resolved a version's candidate/benchmark/review by first-match type iteration, so once one clean evidence chain existed for an artifact, *every later version inherited it*;
- **forge a review** — a single fabricated "approved" review whose free-text source refs merely *contained* the artifact's ID satisfied the human-review gate forever;
- **synthesize governance edges** — there was no edge-type allowlist, so the `USED_CAPABILITY` / `PROMOTED_TO` / `ACTIVATED_BY` edges that record consent could be written directly.

That is the [[gates|fail-open]] failure mode the platform's own engineering standards warn about — a gate that lives in the helper instead of at the boundary silently permits every path that doesn't go through the helper. The hardening pass (PR #40 commit `a460ca9`, re-review verdict *"READY for E2 MVP scope"*) fixed the **class**, not the instances: explicit foreign-key fields on `CapabilityVersion` (so evidence cannot be reused across versions), governance-edge gating moved into the store (`AppendEdge` routes through a trusted-only path), activation made to require re-verified promotion evidence, `"active"` removed from the set of persistable statuses (activation became *the property of having an `ACTIVATED_BY` edge*, not a writable field), and `ActivationPolicy` validation made to reject `"global"` scope. A follow-up (PR #45) then bound capability promotion to the [[authority-layer|authority chain]] (`AuthorityRequest` → `AuthorityDecision` → `ExecutionReceipt`) — and that review *still* found two live bypasses (a self-granted `Autonomous` decision with no decider-≠-requester check, and an availability attack via a shadow `AuthorityRequest`), and returned a `REQUEST CHANGES` verdict.

The honest reading: **the doctrine's "optimizers cannot weaken gates or self-promote" is a design intent that took two-plus adversarial rounds to make true in one implementation, and the third round still found holes.** The chain is sound as a model; making it fail-closed in practice required treating every "may not" as something to be proven at the store boundary over the whole input domain, not asserted in a helper.

> ⚠ **Provenance note.** The eventgraph implementation history above is reconstructed from Open Brain review captures dated 2026-05-17, not from reading the `transpara-ai/eventgraph` code during this compile. The captures are detailed and internally consistent (they name commits, files, line numbers, and test names), but they are one reviewer's notes. The doctrine quotes are from the orientation doc, which itself cites `DF-V3.9-SPEC-006` line ranges that were **not** opened this run.

## Where it sits in the larger arc

Capability evolution is the seventh pillar of the **Dark Factory deployment arc** (docs PR #114, 2026-06-09): phase P7 makes the [[hive-governance|hive]] growth loop live and routes *"contract self-evolution through capability-evolution chain (replacing shepherd edits of agentdef.go)"* — i.e. the long-term goal is that the factory tunes its own agent contracts through this governed pipeline instead of a human hand-editing the role definitions (Open Brain, 2026-06-09). That is the [[strange-loop]] in its operational form: the factory improving the factory, but only ever through evidence, human review, and rollback. It is also exactly the move that **v4.0** generalizes — *"the factory builds the factory under the same accountability it imposes on what it builds"* (L201) — which is why v4.0's own goal invariant repeats the autonomy-gated-on-rollback rule.

## What this is not

Capability evolution is **not** an autonomous self-improving agent, a continuous optimization loop, or a path by which a model can rewrite its own constraints. The whole design exists to make those things impossible-by-construction:

- it is not auto-merge or auto-activation (both excluded from the MVP, L290);
- it is not a way for an optimizer to promote its own outputs or weaken gates (forbidden, L197);
- it is not exempt from human review (review is a required stage, L195);
- it is not reversible-by-hope — a `RollbackRecord` path is part of the chain, and autonomy may not expand unless rollback expands with it (L108);
- and it is not available before the factory has proven its base controls (excluded from Base Slice 0, L253).

## Sources & provenance

Primary source: `raw/transpara/dark-factory/Dark Factory - Motive, Goal, Approach.md` (first-party orientation synthesis, v0.1.5) — §11 *"Treat Capability Evolution as Production Work"* (L193-197), the *"Capability Evolution Flow"* (L275-290), the executive-summary self-improvement line (L74), the motive crosswalk (L130), the goal invariants (L104, L108), and the Base Slice 0 exclusion (L253). That doc attributes the underlying contract to `DF-V3.9-SPEC-006` (`dark-factory/v3.9/06-memory-knowledge-capability-v3.9.md`, capability-artifact model L272-302, material-influence list L49-64, optimizer constraints L105-118, MVP exclusions L49-103) and the eval gates to `DF-V3.9-EVAL-005:L197-233` — **those spec files were not read this run;** the line ranges are reproduced from the orientation doc's citation handles.

Philosophical ancestor: `raw/searles/all-posts-1.md` — *"The Architecture of Accountable AI"* (2026-02-28 · `[Searles-P3]` · https://mattsearles2.substack.com/p/the-architecture-of-accountable-ai), the mind-zero-five self-improvement circuit breaker, compiled separately as [[accountable-ai-architecture]] and [[self-improvement-circuit-breaker]].

Implementation history: Open Brain thoughts (queried via `mcp__open-brain__search_thoughts`, 2026-06-13) — adversarial reviews of `transpara-ai/eventgraph` PR #40 (E2 capability-evolution MVP, original + hardened) and PR #45 (authority binding, `REQUEST CHANGES`), all dated 2026-05-17; and the deployment-arc capture (docs PR #114, 2026-06-09) for the P7 contract-self-evolution role. These are review notes, not a code read of eventgraph this run — flagged inline.

`[[wikilinks]]` are forward references; several targets ([[release-candidate]], [[self-improvement-circuit-breaker]]) may not yet be compiled.
