---
entity: The Cognitive Grammar (Derive / Traverse / Need)
org: transpara-ai
primary_placement: civilization/foundational
placements:
  - civilization/foundational
classification: internal
aliases:
  - the cognitive grammar
  - cognitive grammar
  - Derive Traverse Need
  - the grammar of thinking about thinking
  - the three base operations
  - the 3x3 cognitive matrix
  - the nine cognitive operations
tier: foundational
status: compiled
last_compiled: 2026-06-13
sources:
  - raw/searles/all-posts-1.md  # post 43, "The Cognitive Grammar", 2026-03-22 [Searles-CogGrammar] — the three base operations, the 3x3 matrix, the nine operations, modifiers, named functions, completeness arguments, Bloom comparison, iterative convergence
  - raw/searles/all-posts-1.md  # post 44, "Higher-Order Operations", 2026-03-22 [Searles-HigherOrder] — the "Product" operation as the formal structure of why Blind needs two agents (Agent1.Need x Agent2.Need)
  - "[Searles-CogGrammar] https://mattsearles2.substack.com/p/the-cognitive-grammar"
  - "[Searles-HigherOrder] https://mattsearles2.substack.com/p/higher-order-operations"
  - raw/transpara/dark-factory/Dark Factory - Motive, Goal, Approach.md  # only a passing mention (a same-family critique notes "the LLM Researcher cares about cognitive grammars"); no first-party treatment of the grammar
  - Open Brain  # searched 2026-06-13 — no captured thoughts on the cognitive grammar, Derive/Traverse/Need, or Blind
confidence:
  three_base_operations_exhaustive: asserted, not proven — the source claims production / navigation / absence-detection are exhaustive ("there is no fourth relationship") by argument, not by a proof external to the framework
  nine_operations_complete: asserted by two arguments (candidate-elimination + fixed-point self-application), both internal to the grammar; not independently verified
  blind_unperformable_alone: load-bearing claim, grounded in the source and sharpened by the post-44 "Product" derivation; the impossibility is argued definitionally, not demonstrated empirically
  first_party_adoption: thin — the dark-factory docs and Open Brain do not use this grammar operationally as of 2026-06-13; it lives in the Searles corpus
  layer_0_has_blind: source-internal claim — the post says "Layer 0 already has Blind as a primitive," which refers to the 44-primitive Layer 0, not the five-primitive Foundation inventory in [[fourteen-layers]] (see note below)
---

# The Cognitive Grammar (Derive / Traverse / Need)

**The grammar that produces grammars.** The cognitive grammar is Matt Searles' (with Claude) attempt to name the irreducible operations of reasoning itself — not what an agent *does*, not what the graph *records*, but what a mind does when it produces, navigates, and detects the absence of knowledge. It appears as **Post 43, "The Cognitive Grammar"** (**2026-03-22**), subtitled *"Three operations. Nine compositions. The grammar of thinking about thinking."* It claims three base operations — **Derive**, **Traverse**, **Need** — that self-apply into a closed three-by-three matrix of nine, whose ninth cell, **Blind = Need(Need)**, is offered as the formal reason a single mind cannot audit itself.

The post frames itself as the fix for a real, embarrassing miss. The team had built a Work product — kanban board, tasks, comments, state transitions — and shipped it before noticing that the Work grammar specified twelve operations and the product implemented exactly one (Create). Per the source: *"We didn't even have a* word *for the operation that would have caught it. That's the problem this post solves."* The missing word turns out to be **Audit** — Need(Derive), checking what exists against what should exist.

This article is foundational because the post positions the grammar *above* the rest of the arc's derivations: the fifteen social operations (Post 35), the thirteen domain grammars (Post 36), the two hundred primitives across [[fourteen-layers]], and the twenty-eight agent primitives (Post 40) are all said to be **outputs** of these three operations. The closing claim: *"The cognitive grammar is not the fourteenth [grammar]. It's the grammar that produces grammars."*

## The gap it claims to fill

The post argues there was a hole between two existing inventories. The agent primitives describe what an entity *does* (Observe, Act, Decide, Communicate); Layer 0 describes what the graph *records* (Confidence, Evidence, Gap, Blind). Neither describes *"the operations of reasoning as a complete, derived set."* The agent primitives *include* some cognitive operations — Evaluate (judgement), Learn (acquisition), Introspect (self-examination) — but, the post says, they were derived as *agent* primitives, not *epistemic* ones, and *"the derivation never asked: is Evaluate the only assessment operation?"*

The deeper diagnosis is self-referential: the derivation method that produces completeness was never applied to itself. The post observes that the method's own eight steps **already are** the three operations in sequence — identify the gap (Need), name the transition and base operations (Derive), traverse the behaviour space and derive the axes (Traverse + Derive), fill the matrix (Derive), gap analysis (Need), verify completeness (Traverse + Need), document (Derive). *"Every step is Derive, Traverse, or Need. The method uses all three. But it treats them as methodology, not as primitives. This post promotes them."*

> Note (scope of the "gap"). The "we built one of twelve operations" story and the eight-step derivation method are reported first-hand in the Searles post. As of 2026-06-13 there is no dedicated wiki article for the social grammar (Post 35), the twenty-eight agent primitives (Post 40), or the derivation method; the relevant primitive inventories the post talks down to are covered in [[the-20-primitives]], [[the-primitives]], and [[fourteen-layers]]. Treat the "derivation-method.md" the post cites as a corpus artefact, not an independently verified document.

## The three base operations

The post strips reasoning to "what a mind does with knowledge that can't be decomposed further" and asserts exactly three relationships — have it, lack it, or be making it:

- **Derive** — *produce* new knowledge from existing knowledge. Takes dimensions and fills the matrix; takes premises and produces conclusions; takes examples and produces patterns. *"Without Derive, a mind can observe and navigate but never create understanding."*
- **Traverse** — *navigate* knowledge space. Move from one thing to another, follow connections, zoom in to detail, zoom out to landscape. *"Without Traverse, a mind can produce knowledge but never find its way through what it's produced."*
- **Need** — *detect* absence. Asks what's missing, what should be here that isn't, what hasn't been considered. *"Without Need, a mind can produce and navigate knowledge but never recognise that its understanding is incomplete."*

The irreducibility argument is that none composes from the other two, illustrated by the failure mode of each missing operation:

- *Derive without Traverse* → **blind** (generate in place, never check scope — fill cells without knowing it's the right matrix).
- *Traverse without Derive* → **sterile** (navigate endlessly, never synthesise — "a search engine without synthesis").
- *Need without Derive or Traverse* → **helpless** ("the feeling of wrongness with no capacity to respond").

> ⚠ **Fail-legible note (exhaustiveness is asserted, not proven).** The source states flatly: *"These aren't chosen — they're exhaustive. There is no fourth relationship."* That claim rests on the tripartition have / lack / produce, argued from within the framework. It is plausible and internally coherent, but the post offers no proof external to its own scheme, and the wiki carries it as **asserted, not proven.** This is the same epistemic status the corpus assigns to its other sufficiency claims (see [[the-20-primitives]], [[the-primitives]]), and the framework's own guardrail against treating such claims as truth is [[the-cult-test]].

## The self-application move

Where the social grammar applied **external** semantic dimensions (direction, weight, scope) to three graph operations to get fifteen, the cognitive grammar applies the operations **to each other**. The post's justification: graph operations don't carry their own semantics (*"create edge" says nothing about what kind of edge*), but *"'Derive' already contains everything about what Derive does."* So the right question is not "what dimensions does Derive have?" but "what happens when Derive operates on itself, and on the others?" — *"When the operations* are *the domain, self-application is the natural decomposition."*

Self-applying the three across inner and outer positions yields the nine, laid out by the source as a matrix (rows = outer operation, columns = inner argument):

```
              Derive       Traverse     Need
            ┌────────────┬────────────┬────────────┐
 Derive(x)  │ Formalize  │ Map        │ Catalog    │
            ├────────────┼────────────┼────────────┤
 Traverse(x)│ Trace      │ Zoom       │ Explore    │
            ├────────────┼────────────┼────────────┤
 Need(x)    │ Audit      │ Cover      │ Blind      │
            └────────────┴────────────┴────────────┘
```

The post notes a symmetry it treats as evidence the decomposition is natural: each **row** shares the outer operation's character (Derive's row produces structure; Traverse's row navigates; Need's row detects absence), and each **column** shares the inner argument's character (the Derive column concerns method and production; the Traverse column space and navigation; the Need column gaps and absence). *"Rows and columns mirror each other. The grammar has no preferred direction — no operation is more fundamental than any other."*

## The nine operations

Definitions and examples below are the source's; each is `Outer(Inner)`.

**Derive's row — produces structure**

- **Formalize** — Derive(Derive). Derive the method of derivation; produce the rules that produce knowledge. *"A chef who writes down a recipe is performing Formalize."* Every framework, documented method, or written-down process.
- **Map** — Derive(Traverse). Produce the *map* that makes navigation possible (not the navigation itself). Drawing how a codebase's packages connect; outlining a paper before writing. *"Orientation before exploration."*
- **Catalog** — Derive(Need). Produce a *taxonomy of absence* — the kinds of gaps that can exist (the post's list: unknown, uncertain, incomplete, wrong, outdated, irrelevant, inaccessible, unasked). A QA team's checklist of failure modes. *"Systematises what can go wrong before anything goes wrong."*

**Traverse's row — navigates**

- **Trace** — Traverse(Derive). Walk a derivation chain backward; follow provenance. Reading a paper's citations to check sources; `git blame` to learn why a line exists. *"The backward navigation through causality."* (This is the operation [[event-graph]] realises in a data structure via `Ancestors()`/`Descendants()` over the `Causes` field.)
- **Zoom** — Traverse(Traverse). Navigate navigation itself; change scale. Switch between *"this function has a bug"* and *"this architecture has a flaw."* Without it, *"you're locked at one level of abstraction."*
- **Explore** — Traverse(Need). *Move into* a gap (vs. merely pointing at it). A researcher picking up an unknown topic and reading; an agent reading an unrequested file because something feels incomplete. *"The difference between pointing at the dark and walking into it."*

**Need's row — detects absence**

- **Audit** — Need(Derive). Identify missing derivations: *"What should we have derived but haven't?"* Checking an implementation against a spec and finding eleven of twelve operations missing. The post is explicit that *"Audit without a reference is just Need. Audit with a reference — a grammar, a specification, a checklist — is Need with teeth."* **This is the operation they failed to perform on the Work product.**
- **Cover** — Need(Traverse). Identify unexplored *territory*: the unread file, the unconsidered dimension, the unsearched directory, the person not yet talked to. A gap in *exploration*, not in knowledge. The post claims *"Cover is the operation most AI systems lack entirely"* — a model *"will happily work within its context window… never noticing that the information it doesn't have would change everything."*
- **Blind** — Need(Need). Identify *unrecognised* gaps — the unknown unknowns. *"This is the hardest operation and the most important… Blind questions the boundary of visibility itself."*

## Blind = Need(Need): the formal reason one mind can't audit itself

The article exists, per the one-line brief, largely to ground this cell. The source's claim is structural, not motivational:

> *"Blind is structurally impossible to perform alone. You can't see what you can't see — that's what Blind means. This is why the operation requires* external input*… Blind is the formal reason the hive needs multiple agents instead of one brilliant one. No single mind can perform Blind on itself. The operation's definition includes its own limitation."*

The post then claims this *derives* something the framework had previously asserted as a standalone insight: *"Layer 0 already has Blind as a primitive. Layer 12 has Incompleteness — 'no system can fully describe itself from within.' The cognitive grammar gives these a derivation. Blind isn't an inspired observation about epistemology. It's Need(Need). It falls out of the matrix."*

**Post 44, "Higher-Order Operations" (2026-03-22), sharpens *why* Blind needs two minds** into a formal structure. It introduces the **Product** operation — applying two operations to the same target independently rather than composing them — and argues: *"Blind requires the product of at least two Need operations from different positions. One agent's gaps are another agent's coverage."* In its words, `Agent₁.Need × Agent₂.Need` *"produces a pair of gap-assessments that neither agent could produce alone… This is the formal structure of why the hive needs multiple agents. Not more compute — more* perspectives." This is corroborating, same-day, same-author material, and it is the strongest version of the load-bearing claim.

> ⚠ **Fail-legible note (Blind-unperformable-alone is argued, not demonstrated).** The impossibility is established **definitionally** ("you can't see what you can't see") and then reinforced by the Product structure in Post 44. It is internally rigorous but is not an empirical result; no experiment in the cited sources measures single-agent vs. multi-agent Blind-resolution. The wiki carries it as a **definitional argument with strong internal support**, not a proven theorem. It is, notably, the cognitive-grammar restatement of the multi-perspective rationale that also shows up across the corpus as the case for adversarial review and multiple agents.

> Note (which "Layer 0" has Blind). The post says Blind is "already a Layer 0 primitive." The [[fourteen-layers]] article documents Layer 0 = Foundation as five primitives (Event, EventStore, Clock, Hash, Self) — which does **not** contain Blind. The post is referring to the *44-primitive* Layer 0 (Confidence, Evidence, Gap, Blind, etc.), a different inventory than the five-primitive Foundation. Stated here rather than silently reconciled; both inventories coexist in the corpus.

## The completeness arguments (two, both internal)

The post offers two distinct arguments that the nine are complete, and is explicit that the second is the stronger:

1. **Candidate elimination.** It tests and "kills" plausible additions by decomposing each into the nine: *Decide* = Need(options) + Derive(selection); *Imagine* = Explore + Derive; *Remember* = Traverse(past); *Attend* = Zoom(in) + Traverse(local); *Doubt* = a specific application of Need; *Forget* = in an append-only system, "not an operation… the absence of Traverse." Verdict: *"No candidates survive. The nine are complete."*
2. **Fixed-point self-application.** Applying the nine to the nine, every composition collapses to one of the nine with a specific argument (e.g. Formalize(Formalize) = Formalize one level up; Blind(Blind) = deeper Blind; Audit(Formalize) = Audit with a target). *"The three-by-three matrix is a fixed point… The grammar is closed under its own operations."* The post calls this *"a stronger completeness argument than dimensional exhaustion"*: not "we checked all the boxes" but *"the grammar can reason about itself and finds nothing missing… There is nowhere else to look."*

> ⚠ **Fail-legible note (completeness is self-certified).** Both arguments are conducted *inside* the grammar — candidate decompositions are judged by the grammar's own author, and the fixed-point check uses the grammar to validate the grammar. This is internally consistent but circular by construction; it cannot, even in principle, surface an operation the framework's vocabulary can't already express. Carried as **asserted via internal argument, not independently verified** — consistent with how [[the-primitives]] treats the 200-primitive sufficiency claim ("The Audit" rates that soundness UNCERTAIN).

## Modifiers and named functions

**Three modifiers**, one per "aspect" of any operation (output / input / process), claimed orthogonal to all nine:

- **Tentative** (modifies output) — result is provisional, marked for verification. *"I think this is right, but I haven't checked."*
- **Exhaustive** (modifies input) — cover the complete space, don't sample. *"Don't stop until you've looked everywhere."*
- **Bounded** (modifies process) — limited in scope, depth, or time. *"This is how far you go."* The post notes Bounded is *"the pragmatic constraint on operations that could otherwise be infinite"* (Explore and Trace would run forever without it).

**Six named functions** — recurring compositions worth naming (the post notes Formalize and Catalog are *absent* here, as meta-operations that produce frameworks the others use):

- **Revise** = Need + Derive. Find what's wrong, produce the correction. *"Every bug fix is Revise."*
- **Hypothesize** = Explore + Tentative Derive. Venture into a gap, produce a candidate explanation. *"The Tentative modifier is critical: without it, you get premature certainty."*
- **Validate** = Trace + Audit. Follow provenance, then check against what should exist. *"Code review is Validate."*
- **Orient** = Map + Zoom. Produce a navigation structure, then set your scale. The join-a-new-project operation; *"without Orient, you start working immediately in whatever corner you happen to land in — which is what most AI agents do."*
- **Learn** = Explore + Derive + Need. Discover, produce, verify — a loop, repeating while Need finds gaps.
- **Calibrate** = Cover + Blind + Zoom. Check coverage at multiple scales, including for unknown unknowns. *"Calibrate is expensive and most systems skip it. The systems that skip it are the ones that fail catastrophically."* The post's "old world, translated" table pointedly leaves Calibrate's "common name" blank: *"Calibrate… has no common name because almost nobody does it."*

## Relationship to Bloom's Taxonomy

The post positions the grammar against Bloom's six levels (Remember, Understand, Apply, Analyze, Evaluate, Create), decomposing each into the matrix: Remember = Traverse(past), Understand = Derive(from observation), Apply = Derive(rules→cases), Analyze = Trace + Zoom, Evaluate = Audit, Create = Derive(novel). The claim is that *"Bloom's six are all Derive or Traverse variants… the entire taxonomy lives in two rows of the matrix,"* and crucially that Bloom **has no Need row**. The explanation is not that Bloom is deficient but that it is a taxonomy of *teaching objectives*: *"Teachers know what students don't know — that's why Bloom doesn't need a Need row. Autonomous minds don't have a teacher. They need Need."* The grammar's distinctive contribution, by its own account, is the Need row — operations for detecting the missing, the unexplored, and the unknown.

## Iterative convergence (the grammar as a quality function)

The post claims the grammar carries a working technique: apply all nine operations to any artefact, then to the result, repeating until a full pass produces no structural change. The post says it was written this way and *converged in four passes* (Audit found the modifiers underived; Trace found base operations ungrounded; Zoom found the matrix symmetry; Blind surfaced the epistemic framing assumption; the fourth pass found nothing). It generalises the move: applied to a spec you get grammar coverage + unexplored requirements + unknown unknowns; applied to a codebase you get missing tests (Audit) + unread files (Cover) + unquestioned assumptions (Blind). The termination condition is explicitly *Bounded, not Exhaustive*: *"when a full pass of all nine operations produces no structural changes, you're done. Not perfect. Done."* The post claims this works *"because all nine operations participate in every pass, not just Need… a complete quality function."*

This is the cognitive-grammar formulation of the iterate-to-fixed-point discipline that recurs in the arc (the same shape as the multi-round adversarial review the dark-factory process leans on; see [[dark-factory]] and [[gates]]). It is presented as method, demonstrated only on the post itself; treat the four-pass convergence as **a single reported instance, not a measured property**.

## Why it matters, by the source's account

The post's framing is explicitly engineering, not philosophy: *"Every AI agent in existence — including the ones building the hive — operates without a formal vocabulary for its own reasoning. It Derives without checking coverage. It Traverses without mapping. It needs without knowing how to Need. It is permanently Blind and has no operation for recognising that."* The three prescribed practices:

- **Before building a product**, run `Audit(grammar, implementation)` — the operation that would have shown "1 of 12 operations implemented" before a line was written.
- **Before any task**, run `Cover(context)` — what files weren't read, what docs weren't loaded — *"the operation that prevents the most common AI failure: confidently producing output from incomplete input."*
- **Periodically, invoke Blind** — structurally requiring external input. *"Blind is the formal reason multi-agent systems outperform single agents on complex tasks. Not because more agents means more compute. Because Blind can't be resolved from within."*

The post ends by turning the grammar on itself one last time: invoking Blind surfaced that *"the grammar assumes cognition operates on knowledge. But minds also operate on affect, intuition, felt sense. Is there a parallel grammar for those? This grammar can't answer that question. That's what Blind is for — it doesn't resolve; it marks the boundary."* The closing line: *"The mind has its vocabulary. It doesn't have all of them."*

## Where it sits in the arc

- **Above the derivations.** The grammar claims the fifteen social operations, the thirteen domain grammars, the two hundred primitives of [[fourteen-layers]], and the twenty-eight agent primitives are all *outputs* of Derive/Traverse/Need — *"whether or not anyone noticed at the time."* It is offered as the meta-layer over [[the-primitives]] and [[the-20-primitives]], not another sibling grammar.
- **Grounds a standing principle.** Blind = Need(Need) is the formal backing for the multi-agent / adversarial-review stance the rest of the arc assumes (see [[intelligence-is-an-operation-type]] for the related "keep the AI inside the accountability structure" thesis, and [[dark-factory]] / [[gates]] for fail-closed verification by separate parties).
- **Connects to the substrate.** Trace = Traverse(Derive) is the cognitive name for the backward causal walk that [[event-graph]] implements (`Ancestors()` over `Causes`), tying the grammar back to the late-night failure-tracing question that produced [[the-20-primitives]].
- **Echoes the strange loop.** The fixed-point/self-application argument ("the grammar's own operations, applied to the grammar, produce the grammar") rhymes structurally with the [[strange-loop]] that closes the fourteen-layer stack; the post does not assert they are the same construct, and neither does this article.

> ⚠ **Fail-legible note (thin first-party footprint).** As of 2026-06-13 the cognitive grammar is **not adopted operationally** in the first-party material. A search of the dark-factory docs turns up only a passing, skeptical mention (a same-family review remarks that *"the LLM Researcher cares about cognitive grammars; my plant cares about whether the alarm correlation actually correlates"*) plus a bare citation link to Post 43. Open Brain has **no** captured thoughts on the grammar, on Derive/Traverse/Need, or on Blind. This entity rests almost entirely on the two Searles posts; do not represent it as shipped Transpara practice.

## Sources & provenance

Compiled from `raw/searles/all-posts-1.md`:

- **Post 43, "The Cognitive Grammar", 2026-03-22** · [Searles-CogGrammar] · https://mattsearles2.substack.com/p/the-cognitive-grammar — the three base operations and their irreducibility; the self-application rationale; the 3×3 matrix and its nine operations (Formalize, Map, Catalog, Trace, Zoom, Explore, Audit, Cover, Blind); the Work-product gap; the row/column symmetry; the two completeness arguments (candidate elimination + fixed-point); the three modifiers; the six named functions; the Bloom's Taxonomy comparison and the "Need row"; the "old world, translated" table; iterative convergence (the four-pass account); and the "why this matters" practices. **Blind = Need(Need)** and "no single mind can perform Blind on itself" are quoted from this post.
- **Post 44, "Higher-Order Operations", 2026-03-22** · [Searles-HigherOrder] · https://mattsearles2.substack.com/p/higher-order-operations — the **Product** operation (`Agent₁.Need × Agent₂.Need`) as the formal structure of why Blind requires at least two minds; the depth/iteration axis and its three-to-four-level practical ceiling. Used here to sharpen, not to extend beyond, Post 43's Blind claim.

First-party material: `Dark Factory - Motive, Goal, Approach.md` and the wider dark-factory corpus contain **no treatment** of the cognitive grammar — only a passing critical mention and a citation link (noted in the thin-footprint flag above). Open Brain, searched 2026-06-13, returned **no** thoughts on the grammar, Derive/Traverse/Need, or Blind.

**Conflicts and unproven claims stated, not resolved:** (1) exhaustiveness of the three base operations — asserted by argument, not proven; (2) completeness of the nine — self-certified by two internal arguments; (3) Blind-unperformable-alone — a definitional argument with strong internal support (Post 44), not an empirical result; (4) "Layer 0 already has Blind" refers to the 44-primitive Layer 0, not the five-primitive Foundation inventory in [[fourteen-layers]]; (5) operational adoption — thin to absent in first-party sources. `[[wikilinks]]` are forward references; several targets (the social grammar, the agent primitives, the derivation method) are not yet compiled.
