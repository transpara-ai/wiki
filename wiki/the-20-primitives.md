---
entity: The 20 Primitives
aliases: [20 primitives, the late-night seed, the primitive framework]
tier: foundational
status: compiled
last_compiled: 2026-06-13
sources:
  - raw/searles/all-posts-1.md  # post 1, "20 Primitives and a Late Night", 2026-02-28 [Searles-P1]
  - raw/transpara/dark-factory/Dark Factory - Motive, Goal, Approach.md
confidence:
  framework: high (primary source)
  sufficiency_claim: asserted, not proven — the source itself later guards against it ([[the-cult-test]])
---

# The 20 Primitives

**Day one of the entire arc.** On **2026-02-28**, in a post titled *"20 Primitives and a Late Night,"* Matt Searles (working with Claude) wrote down the seed every later layer grows from. This predates the first fork, the [[hive-governance]], and the [[dark-factory]] — and for now it survives only here, in the source corpus.

## The seed: failure-tracing

The origin was not a vision but a narrow engineering question:

> "How do you trace a bad outcome back to the thing that caused it? … *why did it happen, and where exactly did the chain break?*"

Root-cause traceability in arbitrarily complex systems — a company, a program, a conversation between agents — is the genetic code of everything downstream.

## The method

The primitives were produced with [[incremental-specification-loading]]: feed the model the vision one message at a time, each ending with *"Respond ok,"* loading the full context before asking for synthesis. The technique outlived the post — it became the house method for the whole effort.

## What was loaded

An [[event-graph]] modelling a company's operations: every node has an input, an operation, and an output, wired through a decision tree; a diagnostic agent can reverse-walk from any event back to the point of failure; node definitions are natural language, implemented by an LLM; **everything is traceable to its source.**

## The primitives

Twenty irreducible concepts, claimed sufficient to model company structure, agent communication, software behaviour, UI correctness, logging, failure root-cause, path testing, and LLM-defined expansion — *"everything else is composition"*:

`Node` · `Edge` · `Input` · `Output` · `Operation` · `Event` · `Success Criteria` · `Failure Criteria` · `State` · `Predicate` · `Graph Definition` · `Execution Engine` · `Diagnostic Traversal` · `Correlation` · `Test Harness` · `Agent` · `Criteria` · `Trace` · `Source` · `Type System`

> ⚠ **Fail-legible note.** The claim that 20 primitives are *sufficient to model everything* is **asserted, not proven.** Searles himself later builds a guardrail against treating it as truth ([[the-cult-test]]: *framework as tool, not sacred; the scientific method is the authority layer*). [[dark-factory]] adopts the primitives as **philosophical basis only**, never as implementation authority ([[dark-factory-motive-goal-approach]]).

## What grew from it

- **Into architecture:** traceability → [[event-graph]]; explicit criteria → [[acceptance-criteria]] and [[gates]]; agent action → [[bounded-runtime]]; authority → [[authority-layer]].
- **Into scale:** → [[the-44-primitives]] (the [[the-lovyou-ai-fork|hive0]] ~70-agent run) → [[the-200-primitives]] / [[fourteen-layers]] → the [[thirteen-graphs]].

## Sources & provenance

Compiled from `raw/searles/all-posts-1.md` (post 1, *"20 Primitives and a Late Night"*, 2026-02-28 · [Searles-P1] · https://mattsearles2.substack.com/p/20-primitives-and-a-late-night) and the first-party synthesis `Dark Factory - Motive, Goal, Approach.md`. No conflict between sources on this entity. `[[wikilinks]]` above are forward references; most target articles are not yet compiled.
