---
entity: The Derivation Method
org: transpara-ai
primary_placement: civilization/foundational
placements:
  - civilization/foundational
classification: internal
aliases: [derivation method, the method, the derivation, the grammar that produces grammars]
tier: foundational
status: compiled
last_compiled: 2026-06-13
sources:
  - raw/searles/all-posts-1.md  # post 35, "The Missing Social Grammar", 2026-03-06 [Searles-SocialGrammar] — the method's first run ("The Derivation"); base ops + six dimensions → fifteen operations
  - raw/searles/all-posts-1.md  # post 36, "One Grammar, Thirteen Languages", 2026-03-08 [Searles-13Languages] — "The Method" stated as four moves and re-run across thirteen domains
  - raw/searles/all-posts-1.md  # cognitive-grammar post, "The Cognitive Grammar", 2026-03-22 [Searles-Cognitive] — the eight steps, self-application, the method named and turned on itself
  - raw/transpara/dark-factory/Dark Factory - Motive, Goal, Approach.md  # first-party: primitive derivation treated as historical/contextual source, not a Dark Factory dependency; "do not adopt without repo/canonical evidence"
confidence:
  method_steps: high — quoted from the source; but see "How many steps?" — the source states the method at two granularities (four moves vs. eight steps) and gives two slightly different step→operation mappings. Both stated and cited below; not silently reconciled.
  produced_all_grammars_claim: medium — the corpus asserts one method produced the social grammar, the thirteen composition grammars, the 200 primitives, and the agent/code primitives. This is the author's own framing, consistent across posts, but it is a narrative claim about how artifacts were made, not an independently verifiable record.
  completeness_of_outputs: asserted, not proven — every grammar this method "completes" inherits the same sufficiency caveat the corpus itself guards against ([[the-cult-test]], [[primitive-basis]]). The method is a procedure for *claiming* completeness, not a proof of it.
  first_party_status: the Dark Factory canonical docs do NOT specify or endorse this method; they treat the primitive-derivation lineage as contextual source only. No Open Brain operational record exists for it (searched, none found).
---

# The Derivation Method

**The repeatable procedure behind every grammar and layer in the arc.** The derivation method is the step-by-step recipe Matt Searles (working with Claude) used to turn a domain into a finite, named, claimed-complete vocabulary of operations. It first runs explicitly in the post *"The Missing Social Grammar"* (**2026-03-06**), under the heading *"The Derivation,"* where it produces the [[social-grammar]]'s fifteen operations from three graph operations plus six semantic dimensions. Two days later, in *"One Grammar, Thirteen Languages"* (**2026-03-08**), the same procedure is named *"The Method"* and re-run across thirteen domains — "Thirteen domains. Thirteen grammars. One method." Finally, in *"The Cognitive Grammar"* (**2026-03-22**), the method is turned on itself: its steps are decomposed into three cognitive operations, and the cognitive grammar is reframed as "the grammar that produces grammars."

It is the *how* that connects the arc's two big *whats*: it is how the [[the-20-primitives|primitives]] became the [[fourteen-layers]] and the [[the-primitives|200-primitive ladder]], and how the fifteen social operations became thirteen domain languages. Where [[the-20-primitives]] is the seed and [[event-graph]] is the substrate, the derivation method is the **manufacturing process**.

## The method, as stated by the source

The corpus states the method at two levels of detail. They are the same procedure compressed and expanded — but the wiki notes the gap rather than papering over it (see "How many steps?").

**The compressed form — four moves** ([Searles-13Languages], the section literally titled *"The Method"*):

> "First, identify the base operations — what are the fundamental things you do in this domain? Then identify the semantic dimensions — what axes differentiate one operation from another? Apply the dimensions to the base operations, fill in the matrix. Finally, find the multi-step patterns that recur and give them names."

So: **(1) base operations → (2) semantic dimensions → (3) fill the matrix → (4) name the recurring patterns.** That last step produces the *named functions* — `Sprint`, `Trial`, `Auction`, `Farewell` — the domain words a developer or agent actually uses, each compiling down to a chain of base operations on the [[event-graph]].

**The expanded form — eight steps** ([Searles-Cognitive], in the section *"The Gap"*). The cognitive-grammar post enumerates eight steps and pairs each with the cognitive operation it performs:

1. Identify the gap — **Need**
2. Name the transition — **Derive**
3. Identify base operations — **Derive**
4. Identify semantic dimensions — **Traverse** the behaviour space, **Derive** the axes
5. Decompose systematically — **Derive** (fill the matrix)
6. Gap analysis — **Need** (what's missing from the candidates?)
7. Verify completeness — **Traverse** the full space, **Need** (what's uncovered?)
8. Document — **Derive** the method itself

The one-line summary the wiki was commissioned from ("identify the gap, name the transition, find base operations, identify semantic dimensions, decompose into a matrix, run gap analysis, verify completeness, document") is this eight-step list. The author also points to a file, `derivation-method.md`, as the place that "documents the eight steps" ([Searles-Cognitive]) — i.e. step 8 (Document) applied to the method is exactly the artifact this wiki entry stands in for.

## A worked example: the social grammar

The method's first run is the clearest specimen ([Searles-SocialGrammar], *"The Derivation"*):

- **Base operations (3):** create a vertex (content enters the graph), create an edge (structure changes), traverse (measure distance / navigate, read-only).
- **Semantic dimensions (6):** causality, content, temporality, visibility, direction, authorship — the axes pure graph theory cannot express, because graph theory is "content-agnostic" and "time-agnostic."
- **Decompose into the matrix:** "Every distinct combination of operation type and dimensional properties that corresponds to a real social behaviour is a primitive." This produced **eleven** operations.
- **Gap analysis / completeness:** then the question that "changed everything" — "what social interactions have humans *never* been able to express on a platform?" — surfaced four more (`Endorse`, `Delegate`, `Consent`, `Annotate`) plus `Merge`, the inverse of `Derive`. Result: **fifteen operations**, three modifiers, eight named functions.

The post is candid that the *first* attempt did not use the method at all — it used a garden metaphor ("root," "branch," "seed," "vine") and broke when formalised. The method is explicitly the corrective for naming-before-understanding: *"we were naming things before we understood what they were"* ([Searles-SocialGrammar]).

## The thirteen composition grammars

*"One Grammar, Thirteen Languages"* ([Searles-13Languages]) runs the same method across domain after domain. The recurring shape: pick ~4 base operations for the domain, pick ~4 dimensions, fill the matrix to get ~12–14 domain operations, then name the recurring multi-step patterns.

- **Work** — base: create / assign / track / complete work; dimensions: granularity, direction, actor, binding → twelve operations (`Intend`, `Decompose`, `Assign`, `Claim`, `Prioritize`, `Block`, `Unblock`, `Progress`, `Complete`, `Handoff`, `Scope`, `Review`) and six named functions (`Sprint`, `Standup`, `Retrospective`, `Triage`, `Escalate`, `Delegate-and-Verify`). Every operation maps back to a base grammar operation — e.g. `Handoff` *is* `Consent` (bilateral, dual-signed) because "you can't unilaterally dump your responsibilities on someone else." (See [[the-work-graph|Work]].)
- **Markets** — base: offer / negotiate / execute / assess; dimensions: phase, symmetry, commitment, value-flow → fourteen operations, seven named functions (`Auction`, `Barter`, `Subscription`, `Refund`, `Milestone`, `Reputation-Transfer`, `Arbitration`).
- **Justice** — base: make rules / bring disputes / judge / enforce; dimensions: actor, phase, direction, formality → twelve operations, six named functions (`Trial`, `Class Action`, `Constitutional Amendment`, `Injunction`, `Plea`, `Recall`).
- Plus **Knowledge, Alignment, Identity, Bond, Belonging, Meaning, Evolution, Existence** and the rest — the corpus tallies "~145 domain operations, 66 named functions, all composed from fifteen base operations. One method produced all of it" ([Searles-13Languages]).

The unifying claim: these are "not thirteen different systems. Thirteen vocabularies. One grammar." All thirteen write to the same [[event-graph]]; domain vocabulary makes a causal chain *legible* without sacrificing the structural properties that make it *verifiable*.

> ⚠ **Fail-legible note (the "thirteen" count and the headline op-count drift).** The post titled *"One Grammar, Thirteen Languages"* gives thirteen *domains/grammars* but its own opening says "**Fifteen** operations… every social interaction… is some combination of those fifteen," while the [[social-grammar]] article and source elsewhere settle on fifteen base operations. The exact domain list also varies between passages (e.g. "Trust" appears in one later recap where "Markets/Alignment/Bond" appear in another). The *method* is stable; the *enumerations it produced* drift slightly across posts. Treat "thirteen grammars / fifteen base operations" as the headline figures the author uses, not as a fixed registry.

## Self-application: the method derives itself

The most reflexive move in the arc. *"The Cognitive Grammar"* ([Searles-Cognitive]) observes that the method had a blind spot of exactly the kind it exists to find: *"The method that produces completeness was never applied to the method itself."* The trigger was concrete — the [[hive-governance]] shipped a Work product that implemented **one** of the Work grammar's twelve operations, and "nobody noticed the gap until we checked. We didn't even have a *word* for the operation that would have caught it."

Applying the method to the method yields its three irreducible operations — the cognitive grammar's base operations:

- **Derive** — produce new knowledge from existing knowledge (takes dimensions and fills the matrix; takes premises and produces conclusions).
- **Traverse** — navigate knowledge space (move, follow connections, zoom in/out).
- **Need** — assess knowledge for absence (what's missing? what have I not considered?).

The corpus argues these three are exhaustive ("a mind relates to knowledge in exactly three ways… there is no fourth relationship") and mutually irreducible (Derive-without-Traverse is "blind," Traverse-without-Derive is "sterile," Need-without-either is "helpless"). The eight steps of the derivation method, the post claims, *are* these three operations in sequence — which is why turning the method on itself recovers them.

Crucially, the cognitive grammar does **not** then use external semantic dimensions the way the social grammar did. It uses **self-application** — the operations applied to each other — producing a 3×3 matrix (`Formalize`, `Map`, `Catalog` / `Trace`, `Zoom`, `Explore` / `Audit`, `Cover`, `Blind`). The stated reason: *"When the operations are the domain, self-application is the natural decomposition"* — "Derive already contains everything about what Derive does," whereas "create edge" said nothing about what kind of edge ([Searles-Cognitive]). So the derivation method has *two* decomposition strategies, chosen by domain: **external dimensions** when the base operations are semantically empty (social, work, markets…), **self-application** when the base operations *are* the domain (cognition).

Two of the cognitive grammar's nine operations are explicitly the derivation method's own steps promoted to first-class operations:

- **Formalize** = `Derive(Derive)` — "derive the method of derivation itself… what Post 35 did when it derived the social grammar… what `derivation-method.md` does when it documents the eight steps."
- **Audit** = `Need(Derive)` — "the *gap analysis* step of the derivation method promoted to a first-class operation… this is the operation we failed to perform on the Work product."

## The method's own limit

The corpus draws a hard boundary, and it is one of the more interesting claims to carry: the derivation method cannot derive the layer that contains the deriver. From the Layer-13 / Existence discussion ([Searles-Cognitive] / the layers material in the same corpus):

> "This grammar has no successor. The derivation method presupposes a subject who notices gaps and seeks completeness — that subject is what Layer 13 is about. **You cannot derive the grammar of the deriver.**"

This dovetails with `Blind` = `Need(Need)` ("identify unrecognised gaps"), which the corpus says is *"structurally impossible to perform alone"* — the formal reason the [[hive-governance]] needs multiple agents rather than one brilliant one. The method's completeness check has a floor it cannot inspect from inside; closing it requires an outside perspective. (Compare [[strange-loop]]: the arc's self-referential top-meets-bottom structure.)

> ⚠ **Fail-legible note (the deepest caveat).** The derivation method is a procedure for *asserting* completeness, not a proof of it. Every artifact it produces inherits the sufficiency caveat the corpus itself flags repeatedly — the 20-primitives claim is "asserted, not proven" ([[the-20-primitives]]); the author concedes "both derivations used LLMs trained on overlapping corpora… true independence would require a non-AI derivation" (quoted in the [[civilization-landscape-investigation|landscape research]]). The method gives you a *reference to check against* (a matrix, a grammar) and a *vocabulary for absence* (`Need`/`Audit`/`Cover`/`Blind`) — its value is making incompleteness *visible*, not eliminating it. The "fixed-point" completeness argument the cognitive grammar offers (self-application produces no new operations) is a stronger internal check than dimensional exhaustion, but it is still an internal check — exactly what `Blind` warns cannot be trusted alone.

## How many steps? (source self-conflict, stated not resolved)

The wiki's commission says "eight-step method," which matches [Searles-Cognitive]. But the corpus is not perfectly self-consistent, and the rule here is to show both:

1. **Four vs. eight.** [Searles-13Languages] states the method as **four moves** under the heading *"The Method"*; [Searles-Cognitive] states it as **eight steps** under *"The Gap."* These are the same procedure at different granularity (the eight steps add the framing/gap-identification/verification/documentation scaffolding around the four-move core), not two different methods. No contradiction in substance — only in count.

2. **Two different step→operation mappings, both in the cognitive-grammar material.** The eight-step list quoted above (from *"The Gap"*) assigns: step 2 = Derive, step 4 = Traverse + Derive, step 6 = Need, step 7 = Traverse + Need. But a later passage in the same corpus recaps the *same eight steps* with a cleaner, slightly different assignment: *"Steps 1 and 6 are Need (identify the gap, gap analysis). Steps 4 and 7 are Traverse… Steps 2, 3, 5, and 8 are Derive. Need → Traverse → Derive."* The two mappings disagree on the inner operation of a couple of steps (notably whether steps 4 and 7 also involve Derive/Need, and the recap drops the compound assignments). The wiki does **not** pick one — both are the author's, both are cited, and the disagreement is minor (it concerns labelling steps with operations, not the steps themselves). The associated *pipeline ordering* the corpus prescribes for applying the operations is "Need row → Traverse row → Derive row" (Gap → Navigate → Produce), said to mirror the method's own step order.

## What grew from it

- **The grammars:** the [[social-grammar]] (fifteen operations) and the thirteen composition grammars (Work, Markets, Justice, Knowledge, Alignment, Identity, Bond, and the rest), all "outputs of the cognitive grammar, whether or not anyone noticed at the time" ([Searles-Cognitive]).
- **The layers and the ladder:** the corpus credits "the derivation method from posts 35–38" with producing the [[fourteen-layers|fourteen-layer]] primitives and, by the same recipe, the [[the-primitives|20 → 44 → 200 ladder]].
- **The agent and code primitives:** "fifteen social operations, thirteen grammars, two hundred primitives, twenty-eight agent primitives, sixty-five code graph primitives" — all attributed to "one method" ([Searles-Cognitive]).
- **Into first-party doctrine — with a firewall:** the [[dark-factory]] canonical docs treat this whole primitive-derivation lineage as **historical/contextual source only**, explicitly *not* a Dark Factory dependency, and direct that "Substack-derived primitives must not be adopted without repo/canonical evidence" and that the [[the-cult-test|Cult Test]] guardrail exists precisely to "prevent treating primitives as sacred truth." The method is studied, not inherited, by the first-party platform.

## Sources & provenance

Compiled from `raw/searles/all-posts-1.md`:
- Post 35, *"The Missing Social Grammar"*, 2026-03-06 · [Searles-SocialGrammar] · https://mattsearles2.substack.com/p/the-missing-social-grammar — the method's first explicit run (section *"The Derivation"* and *"The Derivation, Honestly"*): three base graph operations, six semantic dimensions, eleven→fifteen operations via the "what can no platform express?" gap question.
- Post 36, *"One Grammar, Thirteen Languages"*, 2026-03-08 · [Searles-13Languages] · https://mattsearles2.substack.com/p/one-grammar-thirteen-languages — the method stated as four moves (section *"The Method"*), re-run across thirteen domains; per-domain base operations / dimensions / named functions for Work, Markets, Justice and others; "~145 domain operations, 66 named functions… one method produced all of it."
- *"The Cognitive Grammar"*, 2026-03-22 · [Searles-Cognitive] · https://mattsearles2.substack.com/p/the-cognitive-grammar — the eight steps and their step→operation mapping (section *"The Gap"*); self-application and the 3×3 matrix; `Formalize`/`Audit` as the method's own steps promoted to operations; the reference to `derivation-method.md`; the "you cannot derive the grammar of the deriver" limit; the alternate step→operation recap and the Need→Traverse→Derive pipeline ordering.

First-party context: `Dark Factory - Motive, Goal, Approach.md` (Citation/Inclusion table) — the primitive-derivation repos are an "adjacent source ecosystem… not selected as Dark Factory dependency," and the Cult Test / Audit posts are cited as the guardrail against treating derived primitives as sacred. The Dark Factory canonical docs do **not** specify or endorse the eight-step method itself.

**Conflicts stated, not resolved:** (1) the method's step count — four moves ([Searles-13Languages]) vs. eight steps ([Searles-Cognitive]); same procedure, different granularity. (2) Two different step→operation mappings within the cognitive-grammar material — both quoted above, neither silently chosen. (3) The headline enumerations the method produced (fifteen base operations, thirteen grammars) drift slightly across posts; treated as the author's headline figures, not a fixed registry.

**Not corroborated by first party / operations:** no Open Brain thought records this method (searched 2026-06-13; none found), and the Dark Factory canon treats it as contextual source, not adopted procedure. Every claim above traces to a Searles post read this run; the completeness the method *claims* for its outputs is asserted by the author and is flagged throughout as unproven. `[[wikilinks]]` are forward references; several targets (`social-grammar`, `cognitive-grammar`, `the-cult-test`, `the-work-graph`, `hive`) are not yet compiled.
