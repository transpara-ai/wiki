---
entity: Searles Primitive Basis (Source Philosophy)
aliases: [primitive basis, source philosophy, the Searles corpus, source-philosophy basis, accepted philosophical basis]
tier: architecture
status: compiled
last_compiled: 2026-06-13
sources:
  - raw/searles/all-posts-1.md  # post 1, "20 Primitives and a Late Night", 2026-02-28 [Searles-P1] — https://mattsearles2.substack.com/p/20-primitives-and-a-late-night
  - raw/searles/all-posts-1.md  # post 2, "From 44 to 200", 2026-02-28 [Searles-P2] — https://mattsearles2.substack.com/p/from-44-to-200
  - raw/searles/all-posts-1.md  # post 3, "The Architecture of Accountable AI", 2026-02-28 [Searles-P3] — https://mattsearles2.substack.com/p/the-architecture-of-accountable-ai
  - raw/searles/all-posts-1.md  # post 9, "The Cult Test", 2026-03 [Searles-Cult-Test] — https://mattsearles2.substack.com/p/the-cult-test
  - raw/transpara/dark-factory/Dark Factory - Motive, Goal, Approach.md  # §"Source Philosophy", §"Motive", Decision Register A, Citation Handles
confidence:
  role_as_source_philosophy_only: high — both the Searles corpus and the first-party Dark Factory doc state this explicitly
  primitive_counts_and_groups: high (primary source) — the numbers (20 / 44 / 11 groups / 200 / 14 layers) are reported first-hand
  hive0_70-agent_autonomous_derivation: asserted, not proven — single-author testimony of an unattended run; the corpus itself flags it as repeatable-but-unreproduced ([[the-cult-test]])
  primitives_as_proven_ontology: explicitly NOT claimed — both sources treat the framework as research input / philosophical basis, never proven metaphysics
---

# Searles Primitive Basis (Source Philosophy)

This is the **source-philosophy foundation** that motivated the [[dark-factory]] — the Matt Searles / LovYou / mind-zero corpus, taken as **motive, vocabulary, and accountability premise only.** It is *not* the Dark Factory architecture and *not* implementation authority. The first-party orientation doc draws this line in its own words:

> *"Source philosophy — Ideas that motivated the system, especially the Matt Searles / LovYou / mind-zero / event graph corpus."* — distinct from *"Dark Factory architecture"* (the governed software-production system) and *"Implementation authority"* (human-accepted packets, gates, PRs).
> — `Dark Factory - Motive, Goal, Approach.md`

So this article catalogues **what the source says and how Dark Factory is permitted to use it** — not what is proven true. Every load-bearing claim below is labelled by what kind of claim it is.

## When and why it appeared

The corpus is a Substack series by Matt Searles (written "+Claude"), staged in the wiki as `raw/searles/all-posts-1.md`. The relevant posts are all dated **2026-02-28** (the Cult Test is dated **March 2026**). Post 1 is **day one of the entire arc** — it predates the first fork, the [[hive-governance]], and Dark Factory itself.

Dark Factory adopted this corpus as its stated origin: per the orientation doc, *"Dark Factory exists because AI-assisted software production creates a structural accountability problem,"* and *"the source philosophy behind Dark Factory starts with a failure-tracing question."* The corpus supplies the *why*; the Dark Factory specs supply the *what* and the gates supply the *whether*.

## The failure-tracing question (the root)

The whole arc descends from one narrow engineering question — not a vision, not metaphysics:

> *"how do you trace a bad outcome back to the thing that caused it? In any sufficiently complex system — a company, a piece of software, a conversation between two agents — … why did it happen, and where exactly did the chain break?"* — [Searles-P1]

Root-cause traceability is the genetic code of everything downstream. The orientation doc restates it verbatim as Dark Factory's motive: *"how can a complex system trace a bad outcome back to the exact source of failure?"*

The method that produced the answer was [[incremental-specification-loading]] — feed the model the vision one message at a time, each ending with *"Respond ok,"* loading full context before asking *"Decompose this into primitives and list them."* [Searles-P1] The technique outlived the post and became the house working method.

## The three-rung primitive ladder

The corpus reports a derivation ladder. The **counts and structure are first-hand primary-source claims**; the **autonomy of the middle rung is single-author testimony** (see fail-legible note).

### Rung 1 — the 20 primitives (the seed)

Twenty "irreducible concepts," claimed sufficient to model company structure, agent communication, software behaviour, UI correctness, logging, failure root-cause, path testing, and LLM-defined expansion — *"Everything else is composition."* [Searles-P1]

`Node` · `Edge` · `Input` · `Output` · `Operation` · `Event` · `Success Criteria` · `Failure Criteria` · `State` · `Predicate` · `Graph Definition` · `Execution Engine` · `Diagnostic Traversal` · `Correlation` · `Test Harness` · `Agent` · `Criteria` · `Trace` · `Source` · `Type System`

Full article: [[the-20-primitives]]. The corpus also records **seven insights** from the same session; the most load-bearing for Dark Factory is *"intelligence is just another operation type"* — keep the AI **inside** the graph, subject to the same criteria as every other node ([[intelligence-is-an-operation-type]]).

### Rung 2 — 44 primitives across 11 groups (the hive0 run)

Searles built the first LovYou, **hive0** — a multi-agent system on the 20 primitives. By the time he counted, there were *"roughly seventy agents,"* most of which he says he did not design — the hive *"had decided it needed them"* (PM, QA, DevOps, but also Philosopher, Critic, Gap-detector, Mediator, etc.). [Searles-P1]

He then reports leaving the hive *"running autonomously. For two days,"* discovered only when his API limit was exhausted, and on review found the system had derived **44 foundation primitives organised into 11 groups**: Foundation (Event, EventStore, Clock, Hash, Self), Causality, Identity, Expectations, Trust, Confidence, Instrumentation, Query, Integrity, Deception, Health. [Searles-P1] [Searles-P2] The full 44 are enumerated by group in [Searles-P2]. Full article: [[the-44-primitives]].

The significance the corpus draws: an AI hive, unprompted, decided it needed concepts for *self*, *trust*, *uncertainty*, *blind spots*, *deception*, and *health* — *"the irreducible concepts any system needs to operate in a world it can't fully trust or fully see."* [Searles-P2]

> ⚠ **Fail-legible note (the central caveat for this whole entity).** The claim that **~70 agents autonomously derived the 44 primitives during an unattended two-day run** is **asserted, not proven.** It is single-author testimony of one event; no run log, transcript, or independent reproduction is in the sources read this run. The Dark Factory doc classifies the hive0 run as *"Research input"* whose value is *"important, but not independently proven,"* and the corpus's own [[the-cult-test]] concedes the derivation *"could be repeated, and it might produce different results."* Treat the **number 44** as reported and the **autonomy of its derivation** as unverified.

### Rung 3 — 200 primitives across 14 layers (the product horizon)

Feeding the 44 to a Claude Opus instance as "Layer 0" and repeatedly asking *"what's the gap?"*, the corpus reports **156 additional primitives across 13 new layers** derived over a ~two-hour session — **200 total across 14 layers (0–13)**, Layer 0 Foundation up through Layer 13 Existence, *"each layer … exactly 12 primitives in 3 groups of 4 — a structure the model arrived at on its own."* [Searles-P2] Full article: [[the-200-primitives]] / [[fourteen-layers]].

Two structural features of the 200 matter downstream and are **explicitly hedged by the source itself**:

- **The strange loop** — Layer 13 ends with *Return*; Layer 0 begins with *Event*; the ontology curves back on itself ([[strange-loop]]). [Searles-P2]
- **Three irreducibles** the framework *cannot* derive: **Moral Status** (L7, can't derive ought from is), **Consciousness** (L12, can't derive qualia from function), **Being** (L13, can't derive existence) ([[three-irreducibles]]). [Searles-P2] The corpus calls these *"load-bearing admissions,"* not footnotes. [Searles-Cult-Test]

> ⚠ **Fail-legible note.** Dark Factory's own register lists the 200 primitives as *"Research input / product horizon"* and records, as an explicit open issue, *"Whether the 200 primitives are a true ontology or useful map … Open; source corpus flags this as unproven and subject to testing."* The corpus's "two independent derivations converge" argument is stated by the author as *"evidence, not proof."* [Searles-P2] Do not cite the 200 as a settled ontology.

## What the code demonstrated (mind-zero-five)

The corpus's third post grounds the philosophy in working Go code — **mind-zero-five** (`github.com/mattxo/mind-zero-five`), described as open source. [Searles-P3] Three components:

- an **[[event-graph]]** — an `Event` struct of twelve fields; **append-only, hash-chained (SHA-256), causally linked** via a `Causes` field; the `EventStore` interface has *no* `Update()` and *no* `Delete()` — *"structurally incapable of rewriting history … enforced by the interface itself."* This is the original *Diagnostic Traversal* primitive made concrete. [Searles-P3]
- an **[[authority-layer]]** — three Go `Level` constants: `Required` (blocks until human approves), `Recommended` (auto-approves after a 15-minute timeout — *"silence means consent"*), `Notification` (acts and informs); a `Policy` maps an action to an approver, and the mind self-approves **only** where an explicit policy grants it. [Searles-P3]
- a **mind loop** with **self-improvement behind a consent circuit breaker** and **crash-recovery treated as ethics** (clean orphaned state, rehydrate pending authority on restart). [Searles-P3] Full article: [[accountable-ai-architecture]].

> ⚠ **Fail-legible note.** The "running right now / working software" claims are **author testimony**, compiled from quoted Go excerpts in the post — not from a repository checkout performed this run. The Dark Factory doc is careful here: mind-zero-five is *"Prior implementation pattern … not imported into Dark Factory as a dependency,"* used *"as evidence that accountability architecture is implementable; informs but does not govern."* It is precedent, not a dependency.

## How Dark Factory is permitted to use it

The orientation doc maps the philosophy into the governed architecture — **as a conceptual crosswalk, not an import**:

```text
traceability        -> EventGraph
explicit criteria   -> AcceptanceCriteria and gates
agent action        -> bounded runtime invocation
authority           -> AuthorityRequest, AuthorityDecision, ExecutionReceipt
self-improvement    -> EvolutionOrder, eval, human review, activation policy, rollback
```

Concretely: traceability → [[event-graph]]; explicit criteria → [[factory-order]] acceptance criteria and [[gates]]; agent-as-operation → bounded [[runtime-broker]] invocation; authority/consent → [[authority-layer]] and [[hive-governance]]. The Dark Factory register classifies each source item precisely:

| Source item | Dark Factory category | What it is used for |
|---|---|---|
| Matt Searles Substack corpus | Source philosophy / research input | *"Informs purpose, vocabulary, and accountability premise."* |
| 20 primitives | **Accepted philosophical basis** | Conceptual basis for EventGraph, FactoryOrder, criteria, traceability, bounded agents. |
| hive0 seventy-agent run | Research input | Motivates trust, deception, blind spots, health as first-class concerns. |
| 44 primitives / 11 groups | Research input | Informs EventGraph invariants, trust model, adversarial review, contradiction handling. |
| 200 primitives / 14 layers | Research input / product horizon | High-level map for product-graph adjacency and long-range implications. |
| mind-zero-five | Prior implementation pattern | Evidence that the architecture is implementable; not a dependency. |

Note the asymmetry the doc draws on purpose: only the **20 primitives** are elevated to *"Accepted philosophical basis"*; everything past them (44, 200, the hive0 run, mind-zero-five) is *"Research input"* or *"prior pattern."* The further up the ladder, the weaker the claim Dark Factory will lean on.

## The guardrail against itself (the Cult Test)

Crucially, **the source corpus carries its own epistemic brake**, and Dark Factory inherits it rather than inventing it. In [[the-cult-test]] Searles warns that *"when a framework explains everything, you should be worried. That's what cults do,"* and lists the framework's own cult-symptoms before naming the defences:

- **Falsifiability** — *"If the framework can't be wrong, it isn't science."* The 44-primitive derivation *"could be repeated, and it might produce different results"*; the two-derivation convergence is *"evidence, not proof."*
- **Incompleteness** — the three irreducibles are *"load-bearing admissions … a hole at its centre."*
- **Permanent tensions** — Justice vs. Forgiveness, Tradition vs. Creativity, etc., which the framework insists *"cannot be resolved."*
- **The bias is named** — the author explicitly names his own non-neutral state and the helpful-AI collaboration bias.

[Searles-Cult-Test]

Dark Factory restates this as a hard line in its own *"What Dark Factory Is Not"*: it is *"not … a claim that philosophical primitives are proven metaphysics,"* and *"The Searles corpus itself includes a guardrail: the primitive framework is a tool, not a truth; the scientific method is the authority layer; and the framework must not become sacred."* This is the **accountability premise** the entity contributes: the framework is motive and vocabulary, and the authority layer — human review, gates, evidence, the scientific method — is what actually decides anything.

## Adjacent material in the corpus (referenced, not central)

The same series extends the basis into a **product horizon** that Dark Factory treats as *"adjacent product research … not current implementation scope"*:

- **[[thirteen-graphs]]** — Work, Market, Social, Justice, Research, Knowledge, Ethics, Identity, Population, Governance, Culture, Meta, Existence as **views over one event graph**, not separate products. [Searles-13Graphs]
- *The Four Strategies* / *What It's Like to Be a Node* / *The Same 200 Primitives, Weighted Differently* — the **edges-over-nodes / edge-weighting** model (everyone holds all 200 primitives; identity differs by edge weights, not node selection). *Not read in full this run* — flagged as thin here; see the dedicated articles when compiled.
- *The Moral Ledger* — the is-ought bridge argument; covered under [[three-irreducibles]]. [Searles-P2 for the irreducibles; the Moral Ledger URL is in the post's own header]

## Where the source and the platform diverge

Because this is **source philosophy, not implementation authority**, the platform deliberately departs from the corpus in places. State the disagreements rather than smoothing them:

- **Authority levels vs. outcomes.** The Searles corpus defines **three** authority *levels* — Required / Recommended (15-min timeout) / Notification. [Searles-P3] The first-party `Dark Factory - Motive, Goal, Approach.md` defines **four** authority *outcomes* — Autonomous, Notify, ApprovalRequired, **Forbidden** — with no `Forbidden` in Searles and no timeout-consent analogue for `Autonomous`. The wiki states both and does not silently reconcile them; the divergence is expected, since Dark Factory treats the corpus as motive, not spec. (See [[authority-layer]].)
- **Civilization vs. accountability machinery.** The corpus's hive0 is a *"society"* of cooperating and emergent agents. Internal Dark Factory analysis (Open Brain, 2026-06-05) found the platform's later v3.9/v4.0 work drifted toward accountability machinery (gates, evidence, bounded fixtures) with the living cooperating-agent civilization deferred — *"the factory perfected the cage and never moved the inhabitants in."* This is a **gap between the source philosophy and the as-built system**, not a property of the philosophy itself; tracked under [[the-civilization]] and [[civic-roles]]. (Confidence: this drift claim is from an internal diagnosis thought, not from the Searles corpus or the orientation doc — treat as platform-state context, not source-philosophy fact.)

## Sources & provenance

Compiled from `raw/searles/all-posts-1.md`:
- Post 1, *"20 Primitives and a Late Night"* (2026-02-28) · [Searles-P1] · https://mattsearles2.substack.com/p/20-primitives-and-a-late-night — failure-tracing origin, 20 primitives, seven insights, hive0/~70-agent origin, 44-primitive narrative.
- Post 2, *"From 44 to 200"* (2026-02-28) · [Searles-P2] · https://mattsearles2.substack.com/p/from-44-to-200 — the 44 by group, 200 primitives / 14 layers, strange loop, three irreducibles, two-derivation convergence ("evidence, not proof").
- Post 3, *"The Architecture of Accountable AI"* (2026-02-28) · [Searles-P3] · https://mattsearles2.substack.com/p/the-architecture-of-accountable-ai — mind-zero-five event graph, authority layer, mind loop, self-improvement circuit breaker, crash-recovery-as-ethics; repo `github.com/mattxo/mind-zero-five` [Searles-MindZeroRepo].
- Post 9, *"The Cult Test"* (March 2026) · [Searles-Cult-Test] · https://mattsearles2.substack.com/p/the-cult-test — epistemic guardrails: framework as tool not truth, scientific method as authority layer, falsifiability/incompleteness/permanent-tensions/named-bias.

And the first-party synthesis `Dark Factory - Motive, Goal, Approach.md` (DF-MOTIVE-GOAL-APPROACH, v0.1.5) — §"Reader Contract" (source-philosophy vs architecture vs implementation-authority table), §"Motive", §"What Dark Factory Is Not", Decision Register A ("Source Philosophy and Prior Research"), and the Citation Handles table (durable Searles URLs [Searles-P1]–[Searles-Cult-Test], [Searles-13Graphs], [Searles-MindZeroRepo]).

Durable thirteen-graphs URL referenced but **not read in full this run**: [Searles-13Graphs] · https://mattsearles2.substack.com/p/thirteen-graphs-one-infrastructure — content here is from the orientation doc's summary and the post heading map; the *Four Strategies* / *node's-eye-view* / *weighted-differently* posts are likewise flagged as thin and deferred to their own articles.

The 2026-06-05 civilization-drift point is from an internal Open Brain diagnosis thought, labelled as platform-state context, not source-philosophy fact. `[[wikilinks]]` are a mix of compiled siblings and forward references; forward references are expected per house style.
