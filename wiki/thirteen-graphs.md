---
entity: Thirteen Graphs, One Infrastructure
org: transpara-ai
primary_placement: civilization/concept
placements:
  - civilization/concept
classification: internal
aliases: [thirteen graphs, 13 graphs, views not products, one substrate thirteen lenses, the thirteen product graphs]
tier: concept
status: compiled
last_compiled: 2026-06-13
sources:
  - raw/searles/all-posts-1.md  # post 11, "Thirteen Graphs, One Infrastructure", 2026-03-01 [Searles-13Graphs] — the thesis, "Views, Not Products", the thirteen layers, "The Pattern", "The Buildable Piece"
  - raw/searles/all-posts-1.md  # post 6, "Fourteen Layers, A Hundred Problems" [Searles-14Layers] — the layer naming the one-line uses (Relationship / Community / Emergence)
  - raw/searles/all-posts-1.md  # later deep-dive posts: "The Relationship Graph" (2026-03-01), "The Community Graph" — confirm the Relationship/Community naming and cite lovyou-ai/eventgraph
  - "Dark Factory - Motive, Goal, Approach.md"  # first-party: "Thirteen Graphs / product graph series" classified as product horizon, not implementation scope; Population/Meta naming; citation table
confidence:
  thesis: high — the "views, not products" claim is quoted verbatim from the primary source [Searles-13Graphs]
  thirteen_names: contested — the canonical post 11 names Population + Meta; the prompt one-line, the post-6 fourteen-layers list, and the later deep-dive posts name Relationship + Community (+ Emergence for Meta). Both naming schemes are in the corpus; this article states both and does not pick. See "What the thirteen actually are (the names conflict)".
  buildable_scope: asserted as horizon, not shipped — the dark-factory docs classify the whole set as "product horizon and analogy set, not current implementation scope"; the source itself says only the Work Graph is being built ("this week"). The deeper "infrastructure replaces all platforms" claim is unproven.
  trivial_technology_claim: asserted by the author ("hash chains are trivial… append-only stores are a solved problem"); the operational record on the real store contradicts the "trivial" framing (see [[event-graph]] on chain-integrity concurrency cost). Flagged below.
---

# Thirteen Graphs, One Infrastructure

**The thesis that you need one substrate and thirteen lenses, not thirteen startups.** It is the organising claim of the eleventh Searles post, *"Thirteen Graphs, One Infrastructure"* (**2026-03-01**), the companion to post 6's [[fourteen-layers]] survey of what's broken: post 6 asked *what breaks* at each layer of human coordination, and this post answers *what to build*. The argument is that thirteen domain products — Work, Market, Social, Justice, Research, Knowledge, Ethics, Identity, and four more (the names of which the corpus disputes — see below), up to Existence — are **not separate systems** but thirteen *views* of the same [[event-graph]]: "Same events. Same hash chains. Same causal links. Different primitives foregrounded. Different interfaces built on top. One infrastructure."

It is the product-horizon face of the same kernel the [[event-graph]] article describes as the substrate; this article is the catalogue of lenses, that one is the substrate they look through.

## The core move: views, not products

The source states the thesis directly ([Searles-13Graphs]):

> "These aren't thirteen separate systems. They're thirteen views of the same data."

The worked example in the post is a single freelance job seen through several graphs at once: doing the work is a **Work Graph** event; doing it *through a marketplace* is a **Market Graph** event; the client not paying is a **Justice Graph** event; the community discussing it is a **Social Graph** event; a journalist covering it is a **Knowledge Graph** event; the freelancer's record of completing work despite non-payment strengthens their **Identity Graph**; a regulator taking note is an **Ethics Graph** event. One sequence of real-world facts; seven lenses; one append-only, hash-chained, causally-linked store underneath.

The payoff claim, quoted verbatim:

> "You don't need thirteen databases, thirteen user accounts, thirteen trust systems. You need one substrate and thirteen lenses."

What distinguishes a "view" from a "product" here is foregrounding, not data: each graph elevates a different slice of [[the-200-primitives|the primitives]] to the front of its interface, but the underlying events, the SHA-256 hash chains, and the `Causes` edges are shared and identical. This is why the [[event-graph]] is described elsewhere as "the substrate everything else is a view of" — the thirteen graphs are that sentence's *everything else*.

## Why it matters (the source's argument)

The source is explicit that the point is not architectural tidiness:

> "The reason this matters isn't architectural elegance. It's that the problems at each layer are currently solved by separate platforms that can't talk to each other, that each extract rent for mediating trust they don't actually provide, and that each have perverse incentives to keep the problems unsolved."

This is the same diagnosis the post generalises in its closing section, *"The Pattern"*: every layer has a coordination problem; humans built an institution to solve it; that institution acquires a business model or power structure that requires the problem to stay *partly* unsolved; the gap between what it claims and what it does grows until it fails or is replaced. The event graph is claimed to break the pattern "because it's infrastructure, not an institution… It doesn't have a business model… It's a data structure." The reduced thesis, in the author's words:

> "Every coordination problem at every layer of human civilisation reduces to: we need to know what happened, and we need the record to be trustworthy. The event graph provides both."

> ⚠ **Fail-legible note (this is a sweeping reduction, asserted not proven).** "Every coordination problem reduces to a trustworthy record" is the post's strongest claim and is **asserted, not demonstrated**. The post offers one in-progress deployment as evidence (the Work Graph, below), not thirteen. Treat the universal reduction as the thesis being *argued*, not a result.

## What the thirteen actually are (the names conflict)

> ⚠ **Fail-legible note (source conflict — stated, not resolved).** The corpus contains **two different naming schemes for the thirteen**, and the one-line this article was commissioned from uses one of them while the canonical post uses the other. Both are reproduced; neither is silently chosen.

**Scheme A — the canonical post 11** (*"Thirteen Graphs, One Infrastructure"*, the article's primary subject) walks the thirteen as layers in four tiers ([Searles-13Graphs]):

| Tier | Layers | Graphs |
|---|---|---|
| Individual | 1–3 | Work, Market, Social |
| Institutional | 4–6 | Justice, Research, Knowledge |
| Civilisational | 7–10 | Ethics, Identity, **Population**, Governance |
| Universal | 11–13 | Culture, **Meta**, Existence |

**Scheme B — the post-6 fourteen-layers list and the later per-graph deep dives** use a different set of names for the same slots: Layer 9 is the **Relationship Graph** (not Population), Layer 10 is the **Community Graph** (not Governance), Layer 12 is **Emergence** (the deep-dive equivalent of Meta). The one-line for this article, and the [[dark-factory]] product-layer docs cited by the deep dives, follow Scheme B: *Work, Market, Social, Justice, Research, Knowledge, Ethics, Identity, **Relationship, Community**, Governance, Culture, Existence.*

These are not reconcilable by relabelling alone — the schemes disagree on *which concept sits at layers 9–10* (Population/Governance as a demographic-then-civic pair, vs. Relationship/Community as an intimate-then-belonging pair), and on the count of "Governance" (Scheme A makes Governance layer 10; Scheme B makes Community layer 10 and folds Governance differently). The first-party [[dark-factory]] synthesis adopts **Scheme A verbatim** in its citation table: "Work, Market, Social, Justice, Research, Knowledge, Ethics, Identity, Population, Governance, Culture, Meta, and Existence as views over one event graph." The thirteen are real as a *thesis*; the *roster* is genuinely unsettled in the source, and any downstream article ([[the-relationship-graph]], [[the-community-graph]], [[the-population-graph]], [[the-governance-graph]]) should carry this conflict forward, not erase it.

What is **consistent** across both schemes: the first eight (Work, Market, Social, Justice, Research, Knowledge, Ethics, Identity), Culture near the top, and Existence as the thirteenth/final layer "you deploy the others *in*."

## Why this is buildable now (the "why now" claim)

The post argues two things changed in roughly eighteen months to make this individual-scale rather than company-scale ([Searles-13Graphs]):

1. **AI agents became real participants.** "Claude, GPT-4, Gemma — any of these can operate as a node in a workflow, make decisions, explain their reasoning, and have that reasoning recorded… Now you need a prompt and an API key." (This is the same agent-as-node premise [[the-20-primitives]] encodes as the `Agent` primitive.)
2. **The infrastructure is off-the-shelf.** "Hash chains are trivial to implement. Append-only stores are a solved problem. Causal linking is graph database 101. The hard part was never the technology. It was knowing what to build and why. The 200 primitives provide the what. The 14 layers provide the why."

> ⚠ **Fail-legible note (the "trivial technology" claim is contested by the operational record).** The post's "hash chains are trivial / append-only is solved" framing is the author's, and it is the *motivating* simplification of the whole series. The operational record on the real store complicates it: per [[event-graph]] (Open Brain operational notes), the append-only hash chain has a **real concurrency cost** — chain integrity requires serialized appends, and a documented integrity violation occurred at event position 10842 from two uncoordinated processes writing to a shared store. "Trivial to implement" and "trivial to run correctly at scale" are not the same claim; the source makes the former, the record warns about the latter.

## The buildable piece (what's actually being built)

The post does **not** claim the thirteen are simultaneously shippable. Its closing section, *"The Buildable Piece"*, scopes hard ([Searles-13Graphs]):

- **Buildable now, by individuals:** the first three layers — Work, Market, Social. "A Work Graph on top of Claude's API with an event store and hash chains."
- **Each layer bootstraps the next:** "Layer 2 rides on Layer 1… Layer 4 rides on Layers 1-3." Disputes (Justice) become resolvable "with evidence already on the graph" only once the lower layers exist.
- **Far out / not individually catalysable:** "The Existence Graph is a decade out, at least. The Culture Graph and Governance Graph require adoption at scales that no individual can catalyse."

The single concrete commitment in the post is the Work Graph: *"I'm building the Work Graph this week, deploying it at a real company to replace hundreds of legacy apps."* The author frames verification the same structural way the [[event-graph]] does — *"If it works, I'll know because the event graph will show it working. If it fails, I'll know because the event graph will show where it failed and why… Not 'trust me, it's working.' Check the chain."*

> ⚠ **Fail-legible note (horizon vs. shipped — first-party scoping).** The [[dark-factory]] synthesis classifies the entire thirteen-graphs set as **"Product horizon and analogy set, not current implementation scope"** and as "adjacent product research," explicitly *not* a Dark Factory dependency. The [[event-graph]] article carries the same caution: only the Work Graph is described as being built. So the thirteen-graphs thesis is best read as **motivating vision plus one in-progress build (Work)**, not thirteen shipped systems. The "infrastructure replaces all the rent-extracting platforms" claim is, as of this corpus, **aspirational and unproven**.

## Relationship to the rest of the arc

- **Substrate:** the thirteen are views over [[event-graph]] — the append-only, hash-chained, causally-linked store. That article and this one are two faces of one claim: it names the substrate; this names the lenses.
- **Ontology:** the per-graph "primitives foregrounded" are drawn from [[the-200-primitives]]; the whole idea descends from [[the-20-primitives]] ("everything else is composition") via [[the-44-primitives]] and the [[fourteen-layers]].
- **Problem statement:** post 6 [[fourteen-layers]] is the explicit counterpart — what's broken at each layer — to this post's what-to-build.
- **Guardrail:** the universality of the framework is exactly what [[the-cult-test]] exists to keep honest ("framework as tool, not sacred"), and what the [[dark-factory]] docs invoke when they refuse to treat the primitives or the product graphs as implementation authority.

## Sources & provenance

Compiled primarily from `raw/searles/all-posts-1.md`:
- Post 11, *"Thirteen Graphs, One Infrastructure"*, 2026-03-01 · [Searles-13Graphs] · https://mattsearles2.substack.com/p/thirteen-graphs-one-infrastructure — the *"Views, Not Products"* thesis (quoted verbatim), the freelancer multi-graph example, *"Why Now"*, the four tiers and thirteen layers (Scheme A: Population, Governance, Meta), *"The Pattern"*, and *"The Buildable Piece"* (Work/Market/Social buildable now; Existence a decade out; only the Work Graph being built "this week"). *(Note: the post's own footer numbers it Post 11 of the series; the canonical URL is the durable handle above.)*
- Post 6, *"Fourteen Layers, A Hundred Problems"* · [Searles-14Layers] · https://mattsearles2.substack.com/p/fourteen-layers-hundred-problems — the problem-side counterpart, and the source of the **Scheme B** layer names (Layer 9 Relationship, Layer 10 Community, Layer 12 Emergence) that the one-line uses.
- Later per-graph deep dives in the same corpus — *"The Relationship Graph"* (2026-03-01, https://mattsearles2.substack.com/p/the-relationship-graph) and *"The Community Graph"* — which confirm the Scheme B naming. The Community deep dive cites `github.com/lovyou-ai/eventgraph/blob/main/docs/layers/10-community.md`, one of the contested repo identities noted in [[event-graph]].

First-party synthesis: `Dark Factory - Motive, Goal, Approach.md` — the "Thirteen Graphs / product graph series" row of its citation table, which (a) classifies the set as **"Product horizon and analogy set, not current implementation scope,"** (b) names the thirteen using **Scheme A** (Population, Governance, Meta), and (c) supplies the durable [Searles-13Graphs] URL.

**Conflicts stated, not resolved:** (1) **the roster of the thirteen** — Scheme A (post 11 + dark-factory: …Population, Governance, …Meta…) vs. Scheme B (post 6 + deep dives + this article's one-line: …Relationship, Community, …Emergence…); reproduced side by side above, not adjudicated. (2) **horizon vs. shipped** — the thesis is universal but only the Work Graph is claimed to be in build; the dark-factory docs scope the whole set as product horizon. (3) **"technology is trivial"** — asserted by the author, complicated by the operational concurrency cost documented in [[event-graph]]. (4) **repo identity** — `mind-zero-five` vs. `transpara-ai/eventgraph` vs. `lovyou-ai/eventgraph`, inherited from [[event-graph]] and surfaced again by the Community deep dive's citation. Open Brain holds no thought specific to the thirteen-graphs thesis (searched 2026-06-13); the one adjacent thought concerns a Dark Factory EventGraph-evidence visualization build and was not load-bearing here. `[[wikilinks]]` are forward references; most targets are not yet compiled.
