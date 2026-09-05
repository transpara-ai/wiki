---
entity: mind-zero-five
org: transpara-ai
primary_placement: civilization/architecture
placements:
  - civilization/architecture
classification: internal
aliases: [mind-zero-five, mind zero five, mindzerofive, the Go implementation, mind-zero-five repo]
tier: architecture
status: compiled
last_compiled: "2026-06-14"
sources:
  - raw/searles/all-posts-1.md  # post 3 "The Architecture of Accountable AI", 2026-02-28 [Searles-P3] — "open source, written in Go, running right now"; Event struct, EventStore interface, authority levels, mind loop, self-improvement circuit breaker, crash recovery
  - raw/searles/all-posts-1.md  # post 1 "20 Primitives and a Late Night", 2026-02-28 [Searles-P1] — "The code is open source: github.com/mattxo/mind-zero-five" (footer)
  - raw/searles/all-posts-1.md  # post 2 "From 44 to 200", 2026-02-28 [Searles-P2] — preview of the system in "What Comes Next" ~L462
  - raw/searles/all-posts-1.md  # post 5 "The Moral Ledger", 2026-02-28 [Searles-MoralLedger] — "the code runs. You can read it, audit it, fork it, improve it" ~L846
  - wiki/accountable-ai-architecture.md  # sibling article — quotes the Go code; entity notes it as "prior implementation pattern, not a dependency" per dark-factory
  - wiki/the-mind-loop.md  # sibling article — deep-dives the mind loop component
  - raw/open-brain/2026-06.md  # civilization-wiki seed scan ~L4060-4118; "mind-zero-five Go repo github.com/mattxo/mind-zero-five"; "running now = author testimony from quoted Go, not a repo checkout; DF treats it as prior implementation pattern"
  - "Dark Factory - Motive, Goal, Approach.md"  # "prior implementation pattern, not imported into Dark Factory as a dependency"
confidence:
  sources: primary
  claims: grounded
  repo_exists_and_runs: asserted — author testimony ("open source, written in Go, running right now"; "the code runs"); compiled from prose and Go excerpts quoted inside the posts, not from a repository checkout; the design is well-sourced, the operational claim is the author's, not independently verified
  dark_factory_relationship: grounded — first-party dark-factory doc is explicit that mind-zero-five is "prior implementation pattern, not a dependency"; not asserted to be the same codebase as transpara-ai/eventgraph or lovyou-ai/eventgraph
---

# mind-zero-five

**The open-source Go implementation that proves accountable AI is buildable.** mind-zero-five is a Go codebase by Matt Searles, published at `github.com/mattxo/mind-zero-five`, that implements the [[accountable-ai-architecture]] in working software. It first appears by name in the second Searles post (*"From 44 to 200,"* 2026-02-28), where it is previewed in a closing "What Comes Next" section as *"a hash-chained, append-only event graph where every action is causally linked. An authority layer where AI can't exceed its permissions without human consent. A self-improvement loop with a circuit breaker. Working software, open source, built to answer the question: what does accountable AI actually look like?"*

The third post, *"The Architecture of Accountable AI"* (2026-02-28 · [Searles-P3]), goes deep on the code itself. Its opening sentence is the repo's own thesis: *"This post is about the code. Not the philosophy. Not the theory. The actual working software that implements these ideas. Open source, written in Go, running right now. Because principles you can't implement aren't principles — they're wishes."*

> ⚠ **"Running right now" is author testimony.** The design and quoted Go code are well-sourced. That a deployed binary currently exhibits these properties is the author's claim, stated consistently across multiple posts. This article was compiled from prose and Go excerpts quoted inside the posts — the repository was not checked out or run independently. Treat operational claims as attested, not verified.

## What the repo implements

The post names three core components and two design properties that span all three:

**Core components:**

1. **The event graph** — a twelve-field Go `Event` struct, backed by an `EventStore` interface. Append-only (no `Update`, no `Delete`), SHA-256 hash-chained (every event carries its own hash and the previous event's hash, so `VerifyChain()` can audit the whole chain at any time), and causally linked (the `Causes` field is a list of prior event IDs, forming a DAG walkable via `Ancestors()` and `Descendants()`). See [[event-graph]].

2. **The authority layer** — a structural gate with exactly three `Level` constants: `Required` (blocks until a human explicitly approves), `Recommended` (auto-approves after a 15-minute timeout unless a human objects — "silence means consent"), and `Notification` (auto-approves immediately; acts and informs). A `Policy` struct maps an action string to an `ApproverID` and a default level. The mind self-approves only when an explicit policy sets `ApproverID == actorID` — an allowlist, not a denylist; the fail-closed branch is the default. See [[authority-layer]].

3. **The mind loop** — an autonomous agent that claims tasks, plans, implements, reviews, and finishes. Every step emits an event into the graph (`task.claimed`, `mind.claude.invoked` with the prompt, `mind.claude.completed`, `build.completed`, `code.committed`, `mind.claude.failed`, `build.failed`). Every event carries its `Causes`, so any commit traces back through the Claude invocation, the task, the authority request, and the original task creator. See [[the-mind-loop]].

**Cross-cutting design properties:**

- **Self-improvement with a circuit breaker.** When idle, the mind runs `maybeAssess`: it identifies an improvement (a refactor, a missing test, an architectural change), formulates a proposal, and submits it as a `Recommended`-level authority request — a 15-minute window in which the human can object. If no objection arrives, the mind creates a task, claims it, and runs it through the normal cycle, with every step logged. The self-improvement cannot skip the authority gate. The post's direct claim: *"Recursive self-improvement and human oversight are not mutually exclusive. You can have both. This code proves it."*

- **Crash recovery as ethics.** On startup, `recoverState` cleans orphaned file changes from any prior crash (preventing cross-task contamination), rehydrates pending authority requests from the event graph (re-arming `pendingRestart` and `pendingProposal`), and recovers stale in-progress tasks. Stale tasks (in progress >30 minutes) are requeued; blocked tasks retry with exponential backoff up to three times, after which the system halts and waits for human intervention rather than failing silently. The argument: *"The event graph can't have integrity if a crash can corrupt it."*

## The load-bearing principle

The post names one architectural commitment that the three components share: **the AI stays inside the graph.** *"Intelligence is just another operation type. Claude is invoked as a node in the system — it receives inputs, produces outputs, and is subject to the same success/failure criteria and authority requirements as everything else. It is not elevated above the accountability structure. It lives within it."* This principle is independently restated in the first-party [[dark-factory]] synthesis doc and is the through-line from the Searles philosophy to the dark-factory implementation.

## What the post says the code proves

The post closes with five explicit existence claims. Recorded as the author's claims:

1. **AI accountability is implementable** — *"not a policy document… a data structure and an API. You can build it. You can deploy it. You can verify it."*
2. **The AI stays inside the graph** — the load-bearing principle is structural, not voluntary.
3. **Self-improvement doesn't require unchecked autonomy** — demonstrated for this system by construction.
4. **Trust is graduated, not binary** — the three authority levels encode this.
5. **The complete history is verifiable** — by anyone, via the hash chain, *"trust that doesn't require trusting."*

> ⚠ **"You can verify it" and "the complete history is verifiable"** are design properties of the append-only hash chain and the `VerifyChain()` method. The design argument is sound; that these properties hold in a live deployment is attested by the author, not checked here.

> ⚠ **"Self-improvement doesn't require unchecked autonomy"** is demonstrated for this system's design, by construction. It is not a general theorem about all self-improving AI. The post presents mind-zero-five as one working existence proof, not a universal guarantee.

## Relationship to dark-factory

The first-party [[dark-factory]] synthesis document names mind-zero-five explicitly as a **"prior implementation pattern, not a dependency"**: *"open-source Go code with event graph, authority layer, and mind loop; not imported into Dark Factory as a dependency."* It is treated as *"evidence that accountability architecture is implementable; informs but does not govern."* The shared DNA is the load-bearing principle (intelligence as one operation type) and the event-graph + authority + trace spine — **not** shared code.

The dark-factory crosswalk maps components forward: "agent action becomes bounded runtime invocation" and "self-improvement becomes EvolutionOrder, eval, human review, activation policy, and rollback." These are successors that reimplemented the concepts, not imports of the original.

> ⚠ **Repo identity tension.** The Searles posts are consistent that the implementation is mind-zero-five at `github.com/mattxo/mind-zero-five`. Dark-factory docs and Open Brain operational records name `transpara-ai/eventgraph` (and `lovyou-ai/eventgraph`) as the live native core. The sources do **not** assert that mind-zero-five and eventgraph are the same codebase, and this article does not assert it either. What is consistent across all sources is the *shape*: Go, append-only, hash-chained, causally-linked store with `VerifyChain`, `Ancestors`, and `Descendants`. See [[the-lovyou-ai-fork]] and [[event-graph]] for the repo identity thread.

## What grew from it

- **Philosophy into code:** mind-zero-five is where [[the-20-primitives]] and [[accountable-ai-architecture]] became running software — the diagnostic-traversal primitive (late-night question: "how do you trace a failure back to its source?") realised as the `Causes` field and `Ancestors()`/`Descendants()`.
- **Into the arc:** the event graph is the substrate the [[event-graph]] article documents; the authority layer is the gate [[authority-layer]] goes deep on; the mind loop's behavior is the subject of [[the-mind-loop]]; the whole three-component system is [[accountable-ai-architecture]].
- **Into dark-factory:** the load-bearing principle and the accountability spine informed (not governed) the [[dark-factory]] design, which reimplemented rather than imported them.

## Sources & provenance

Compiled from `raw/searles/all-posts-1.md`:
- Post 1, *"20 Primitives and a Late Night"*, 2026-02-28 · [Searles-P1] · https://mattsearles2.substack.com/p/20-primitives-and-a-late-night — footer credits the repo: "The code is open source: github.com/mattxo/mind-zero-five."
- Post 2, *"From 44 to 200"*, 2026-02-28 · [Searles-P2] · https://mattsearles2.substack.com/p/from-44-to-200 — "What Comes Next" section (~L462) previews the system before post 3 describes it.
- Post 3, *"The Architecture of Accountable AI"*, 2026-02-28 · [Searles-P3] · https://mattsearles2.substack.com/p/the-architecture-of-accountable-ai — **primary source**. Opening: "open source, written in Go, running right now." Names the system "mind-zero-five." Full Go excerpts for `Event`, `EventStore`, authority levels, `MatchPolicy` branch, `maybeAssess`, crash recovery.
- Post 5, *"The Moral Ledger"*, 2026-02-28 · [Searles-MoralLedger] · https://mattsearles2.substack.com/p/the-moral-ledger — "the code exists. It's open source. It runs. You can read it, audit it, fork it, improve it." (~L846)

Sibling articles `wiki/accountable-ai-architecture.md` and `wiki/the-mind-loop.md` provided cross-checks on the component descriptions and the dark-factory crosswalk. `raw/open-brain/2026-06.md` (~L4060–4118) corroborated "running now = author testimony from quoted Go, not a repo checkout; DF treats it as prior implementation pattern." `Dark Factory - Motive, Goal, Approach.md` (first-party) is the source for "prior implementation pattern, not a dependency" and the motive crosswalk.

The repository `github.com/mattxo/mind-zero-five` was **not** checked out this run; all code references are to Go excerpts quoted inside the Searles posts. The "running right now" claim is the author's testimony. `[[wikilinks]]` are forward references; most targets are not yet compiled.
