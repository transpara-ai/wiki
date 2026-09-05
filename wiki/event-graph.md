---
entity: The Event Graph
org: transpara-ai
primary_placement: civilization/foundational
placements:
  - civilization/foundational
classification: internal
aliases: [event graph, EventGraph, the event store, the moral ledger, the sovereign truth layer, the kernel]
tier: foundational
status: compiled
last_compiled: 2026-06-13
sources:
  - raw/searles/all-posts-1.md  # post 3, "The Architecture of Accountable AI", 2026-02-28 [Searles-P3] — Event struct, EventStore interface, append-only/hash-chained/causal properties
  - raw/searles/all-posts-1.md  # post 5, "The Moral Ledger", 2026-02-28 [Searles-MoralLedger] — event graph as moral ledger at scale
  - raw/searles/all-posts-1.md  # post 9, "Thirteen Graphs, One Infrastructure", 2026-03-01 [Searles-13Graphs] — one substrate, thirteen views
  - raw/searles/all-posts-1.md  # post 1, "20 Primitives and a Late Night", 2026-02-28 [Searles-P1] — the failure-tracing origin the structure answers
  - raw/transpara/dark-factory/Dark Factory - Motive, Goal, Approach.md  # EventGraph as sovereign truth kernel; citation table
  - Open Brain  # operational facts on the real transpara-ai/eventgraph repo (chain integrity, pgstore, VerifyChain semantics)
confidence:
  data_structure_and_interface: high — quoted verbatim from the source code listings in [Searles-P3]
  repo_identity: contested — the Searles posts name the implementation `mind-zero-five` (github.com/mattxo/mind-zero-five); the dark-factory docs and Open Brain reference `transpara-ai/eventgraph` (Open Brain also says `lovyou-ai/eventgraph`). See "What the code actually is" below — these are related but not asserted to be the same repo.
  moral_ledger_claim: explicitly flagged by its own author as a hypothesis, not a proof
  thirteen_graphs_substrate_claim: product horizon / analogy, not implemented scope per the dark-factory docs
---

# The Event Graph

**The substrate everything else is a view of.** The event graph is the append-only, SHA-256 hash-chained, causally-linked directed acyclic graph of immutable events that sits at the foundation of every system in the arc. It first appears as working code in the third Searles post, *"The Architecture of Accountable AI"* (**2026-02-28**), as the foundational component of a Go system called **mind-zero-five**, alongside the [[authority-layer]] and the [[the-mind-loop]]. It is the direct answer to the late-night failure-tracing question that produced [[the-20-primitives]] the same day: *"how do you trace a failure back to its source?"*

In the [[dark-factory]] synthesis it is promoted from "a data structure" to the **kernel** — "the sovereign source of truth for durable facts, causality, audit evidence, identity records, authority records, lifecycle records, artifact provenance, certification evidence, and capability-evolution evidence," which no other system may supersede.

## The data structure

The source ([Searles-P3]) gives the structure verbatim — twelve fields:

```
type Event struct {
    ID             string         // UUID v7 (time-ordered)
    Type           string         // e.g. "trust.updated", "task.completed"
    Timestamp      time.Time      // when it happened
    Source         string         // who emitted it
    Content        map[string]any // the payload
    Causes         []string       // IDs of causing events
    ConversationID string         // groups related events
    Hash           string         // SHA-256 of canonical form
    PrevHash       string         // hash chain link
}
```

Three properties do the load-bearing work, and the post is explicit that each is an ethical commitment encoded in structure, not a database convenience:

- **Append-only.** Events are never modified or deleted; new events can supersede old ones, but history can never be rewritten. *"What happened, happened."*
- **Hash-chained.** Each event carries a SHA-256 hash of its own content plus the `PrevHash` of the prior event, so the entire history is cryptographically linked — "like a blockchain, but without the overhead." Tampering anywhere breaks the chain and is detectable; a `VerifyChain()` method validates the whole history.
- **Causally linked.** The `Causes` field is what makes this a *graph* rather than a log: every event records which prior events caused it, forming a DAG of causation you can walk forwards (`Descendants()`) or backwards (`Ancestors()`). This is the **diagnostic traversal** primitive from [[the-20-primitives]] realised in a data structure — *"every action has a receipt."*

## The interface that forbids rewriting

The structural guarantee lives in what the `EventStore` interface omits. The source lists it ([Searles-P3]):

```
type EventStore interface {
    Append(ctx, eventType, source, content, causes, conversationID)
    Get(ctx, id)
    Recent(ctx, limit)
    ByType(ctx, eventType, limit)
    BySource(ctx, source, limit)
    Since(ctx, afterID, limit)
    Count(ctx)
    VerifyChain(ctx)

    // Causal traversal
    Ancestors(ctx, id, maxDepth)
    Descendants(ctx, id, maxDepth)
    Search(ctx, query, limit)
}
```

There is **no `Update()` and no `Delete()`.** The post's exact claim: the event store is "structurally incapable of rewriting history… not enforced by policy or convention — enforced by the interface itself. If your code wants to modify the past, it simply can't." This is the foundational move of the whole arc — accountability made structural rather than voluntary, the same logic [[authority-layer]] applies to permission and the [[dark-factory]] generalises into fail-closed gates.

## Why it is the substrate, not a feature

By the ninth post, *"Thirteen Graphs, One Infrastructure"* ([Searles-13Graphs], 2026-03-01), the event graph is reframed as the single infrastructure under everything: thirteen proposed product graphs — Work, Market, Social, Justice, Research, Knowledge, Ethics, Identity, Population, Governance, Culture, Meta, Existence — are described as **views, not products**: "Same events. Same hash chains. Same causal links. Different primitives foregrounded… One infrastructure." (See [[thirteen-graphs]].) The argument is that the hard part was never the technology — "hash chains are trivial… append-only stores are a solved problem… causal linking is graph database 101" — but knowing what to build, which the primitives and layers supply.

The [[dark-factory]] docs adopt exactly this kernel role: EventGraph as "the sovereign truth layer," with Work scheduling production, governance evaluating authority, and the runtime confining execution — but "none supersede EventGraph for authority or certification." The kernel is specified to provide "append-only recording, deterministic canonical serialization, tamper evidence, idempotent writes, actor attribution, causal edges, queryable paths, replayable projections, and conformance tests without live LLM credentials or production side effects."

> ⚠ **Fail-legible note (substrate-of-everything claim).** "Thirteen graphs as views over one event graph" is presented by the dark-factory docs as a **product horizon and analogy set, not current implementation scope** — and only the [[the-work-graph|Work Graph]] is described as actually being built ("I'm building the Work Graph this week"). Treat the thirteen-graph universality as motivating vision, not shipped fact.

## The moral-ledger claim (explicitly a hypothesis)

The fifth post, *"The Moral Ledger"* ([Searles-MoralLedger]), pushes the event graph from audit trail to ethics. At institutional scale, complete causal visibility means *"'I didn't know' stops being a defence"* and "'trust us' becomes unnecessary, because the record is independently verifiable." The stronger move is the link to Hume's is–ought gap: *if* consciousness is fundamental, then the causal chain connects decisions not just to outcomes but to experiences, and the ledger makes the moral weight of decisions visible "by making the facts complete enough that the moral dimension is already there."

> ⚠ **Fail-legible note (moral-ledger / is–ought bridge).** The author flags this himself, and the wiki must too: *"It's not a proof. It's a hypothesis."* He writes plainly, *"I don't know if the is-ought bridge actually works,"* and *"I don't claim that the event graph solves ethics. It doesn't."* The audit-trail-at-scale observation is grounded; the metaphysical bridge from append-only causality to objective moral weight is **asserted, contested, and unproven** — carried here only because the source carries it, and labelled as such.

## What the code actually is (sources disagree on the repo)

The Searles posts are consistent that the implementation is **mind-zero-five**, "open source, written in Go, running right now," at `github.com/mattxo/mind-zero-five` ([Searles-P3], [Searles-MoralLedger]). The [[dark-factory]] docs treat `mind-zero-five` as a **prior pattern, not a dependency** ("not imported into Dark Factory as a dependency… evidence that accountability architecture is implementable; informs but does not govern"), and instead name `transpara-ai/eventgraph` as the **selected native core** that "owns durable truth; must not be bypassed."

> ⚠ **Fail-legible note (repo identity is contested).** Open Brain operational notes about the live implementation refer to both `transpara-ai/eventgraph` and `lovyou-ai/eventgraph`. The sources do **not** assert that `mind-zero-five` and `eventgraph` are the same codebase, and neither will this article. What is consistent across all of them is the *shape*: a Go, append-only, hash-chained, causally-linked store with a `VerifyChain` path and ancestor/descendant traversal.

The operational record (Open Brain) corroborates the architecture and adds gotchas that the prose doesn't:

- **Chain integrity requires serialized appends.** Each event must reference the *actual current chain head* as its cause. Two concurrent appends race: one succeeds, the other fails with a chain-integrity violation (*"expected hash X, got hash Y"*). This is by design — it is how the hash chain stays intact — but it means **the append-only hash chain has a real concurrency cost**. A documented violation occurred at event position 10842 from uncoordinated writes by two processes (hive runtime + work-server) against a shared Postgres store.
- **Best-effort vs. reliable emit.** In the [[hive-governance]], `Runtime.emit()` is best-effort and ignores errors; webhook dispatch needed a mutex to serialize appends. The mutex does *not* protect agent-emit races.
- **`VerifyChain` error semantics.** A pgstore refactor (2026-04-02) preserved a deliberate subtlety: reconstruction failures return `ChainVerifiedContent{Valid: false}` with a **nil error**, not an error — invalidity is a value, not an exception.
- **Canonical form is determinism-sensitive.** New event-type constructors sort their slices so the canonical form (and therefore the hash) is deterministic — a direct consequence of hashing the content.

## What grew from it

- **Within mind-zero-five:** the [[the-mind-loop]] lives on top of it — every action (`task.claimed`, `mind.claude.invoked`, `code.committed`, `build.failed`) is an event carrying its `Causes`, and [[crash-recovery-as-ethics|crash recovery]] exists precisely because *"the event graph can't have integrity if a crash can corrupt it."*
- **Into the arc:** it is the kernel the [[authority-layer]] records into, the substrate the [[thirteen-graphs]] are views over, and the "sovereign truth layer" the [[dark-factory]] builds its evidence-first production loop around.
- **From the seed:** it is the architectural realisation of the **traceability / diagnostic-traversal / source** strand of [[the-20-primitives]] — the late-night question, answered in twelve fields.

## Sources & provenance

Compiled from `raw/searles/all-posts-1.md`:
- Post 3, *"The Architecture of Accountable AI"*, 2026-02-28 · [Searles-P3] · https://mattsearles2.substack.com/p/the-architecture-of-accountable-ai — the `Event` struct, the `EventStore` interface (no `Update`/`Delete`), and the append-only / hash-chained / causally-linked properties.
- Post 5, *"The Moral Ledger"*, 2026-02-28 · [Searles-MoralLedger] · https://mattsearles2.substack.com/p/the-moral-ledger — the event graph as moral ledger at scale and the explicitly-hypothetical is–ought bridge.
- Post 9, *"Thirteen Graphs, One Infrastructure"*, 2026-03-01 · [Searles-13Graphs] · https://mattsearles2.substack.com/p/thirteen-graphs-one-infrastructure — one substrate, thirteen views; "views, not products."
- Post 1, *"20 Primitives and a Late Night"*, 2026-02-28 · [Searles-P1] · https://mattsearles2.substack.com/p/20-primitives-and-a-late-night — the failure-tracing origin the structure answers.

First-party synthesis: `Dark Factory - Motive, Goal, Approach.md` (EventGraph as sovereign truth kernel; `mind-zero-five` as prior pattern vs. `transpara-ai/eventgraph` as selected native core; durable Searles URLs from its Citation Handles table). Operational facts (chain-integrity races, pgstore `VerifyChain` semantics, canonical-form determinism, repo names `transpara-ai/eventgraph` and `lovyou-ai/eventgraph`) from Open Brain captured thoughts.

**Conflicts stated, not resolved:** (1) the implementation's repo identity — `mind-zero-five` (Searles) vs. `eventgraph` (dark-factory / Open Brain); (2) the moral-ledger / is–ought claim, flagged as a hypothesis by its own author; (3) the thirteen-graphs universality, scoped as product horizon rather than shipped fact by the dark-factory docs. `[[wikilinks]]` are forward references; most targets are not yet compiled.
