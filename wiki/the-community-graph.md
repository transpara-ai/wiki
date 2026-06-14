---
entity: The Community Graph
aliases: [community graph, CommunityGraph, layer 10 community, belonging graph]
tier: foundational
status: compiled
last_compiled: "2026-06-14"
sources:
  - raw/searles/all-posts-1.md  # "Layer 10: Community" deep dive, line ~4241 [Searles-Community] — derivation, the relationship->belonging transition, base operations, semantic dimensions, the three primitive groups, gap analysis, completeness argument
  - raw/searles/all-posts-1.md  # Post 26 "The Weight", line ~5074 [Searles-Weight] — Layer 10 failure mode (belonging is binary; no gradient, memory, or portable history) in the suffering cascade
  - raw/searles/all-posts-1.md  # Post 11, "Thirteen Graphs, One Infrastructure", 2026-03-01 [Searles-13Graphs] — civilisational-tier framing and the Scheme A/B layer-roster conflict
confidence:
  sources: primary
  claims: grounded
---

# The Community Graph

**The transition from relationship to belonging: shared meaning, living practice, and communal experience on the event graph.** The Community Graph is **Layer 10** in the per-graph deep-dive series (Scheme B), specified in the source as *"Layer 10: Community."* It is one view over the single [[event-graph]], foregrounding the primitives of collective belonging — the capacities a community has that a mere collection of relationships does not.

> ⚠ **Naming conflict (Scheme A vs. Scheme B).** This article follows the **Scheme B** per-graph deep dive, where Layer 10 is the Community Graph (sitting above the [[the-relationship-graph|Relationship Graph]] at Layer 9 and below the Governance Graph at Layer 11). The **Scheme A** overview (Post 11 / the [[dark-factory]] synthesis) numbers the civilisational tier differently — there Layer 10 is the [[the-governance-graph|Governance Graph]], and the belonging / shared-meaning territory overlaps Scheme A's [[the-culture-graph|Culture Graph]] (Layer 12). The two rosters are reproduced in [[thirteen-graphs]]; this article carries the conflict forward rather than resolving it.

## The gap it fills

[[the-relationship-graph|Layer 9]] models dyadic bonds with depth, repair, and intimacy. But belonging to a community is *more than* having relationships with individuals — it is an emergent sense of home, of shared identity, of being part of something larger. The source's test: you can express bonds between individuals and loyalty in pairs at Layer 9, but *"traditions that define the community"* (collective practice), *"shared resources"* (commons), *"sense of home"* (belonging), and *"celebrated together"* (collective joy) have **no Layer 9 representation.** Relationship is between two; community is among many. The fundamental new capacity is **belonging to a collective that is more than the sum of its relationships.**

## The primitives

The source decomposes Layer 10 across a {orientation, temporality, flow, mode} semantic space into three groups:

- **Group 0 — Shared Meaning** (what binds us together): **Culture** (the shared way of life), **SharedNarrative** (the story a community tells about itself), **Ethos** (its guiding values), **Sacred** (what it holds inviolable). *Culture is the container; Sacred marks its deepest commitments.*
- **Group 1 — Living Practice** (how we live together): **Tradition** (practices passed down), **Ritual** (formalised practices marking significant moments), **Practice** (what members actually do together), **Place** (the physical or virtual space the community inhabits). *Place grounds community in the concrete.*
- **Group 2 — Communal Experience** (what it feels like to belong): **Belonging** (the sense of being part of something larger), **Solidarity** (mutual support and collective strength), **Voice** (the capacity to speak and be heard), **Welcome** (how newcomers are received). *Welcome closes the loop — it is how belonging begins for the next generation.*

The four base operations a community can perform that a collection of relationships cannot: **Belong, Practice, Share meaning, Welcome.**

## Why existing infrastructure fails

The source's cascade illustration (Post 26, *"The Weight"*) states the failure mode plainly: *"The Community Graph doesn't exist, so belonging is binary — you're in or you're out. There's no gradient. No memory. No portable history. When the community dies, everything it held dies with it."* Platforms model membership as a boolean (joined / not joined) and own the social fabric they host, so a community has no portable record of its own traditions, narrative, or shared resources — and no way to carry them when it migrates or when a platform fails.

## What the event graph version does differently

The Community Graph proposes to record belonging on the same append-only, hash-chained, causally-linked [[event-graph]] substrate, so the things that make a community real become first-class, portable, and inspectable: a tradition is a lineage of events, a ritual is a recurring event pattern, belonging is a gradient derived from participation rather than a boolean, and a community's narrative and sacred commitments are part of the chain it owns rather than data a platform holds. The source's completeness argument cross-checks the primitive set against community-studies scholarship — Tönnies' *Gemeinschaft* maps to Belonging and Culture, Ostrom's commons governance to shared resources (via the [[the-social-graph|Layer 3]] Commons), Turner's *communitas* to Ritual and Solidarity — and reports **no gaps found** at the layer boundary. A community *lives within* its practices; reflecting on *why* those practices exist (meta-awareness) is deferred upward to the Culture/meta tier.

## Buildability

As a civilisational-tier graph, the Community Graph is not positioned as immediately individually buildable. Per the Post 11 overview, the upper-tier graphs *"require adoption at scales that no individual can catalyse"* and *"grow organically from the lower layers"* — a community's collective record emerges from its members' [[the-relationship-graph|relationship]], [[the-social-graph|social]], and work activity rather than being instantiated top-down.

> ⚠ **Thin-spec note.** The Community Graph is specified primarily as a layer-derivation document (primitive groups, semantic dimensions, gap analysis) rather than a product essay. Structural claims here track that derivation; the deployment economics are less developed in the source than for the [[the-relationship-graph|Relationship Graph]].

## Relationship to adjacent graphs

- **Below:** [[the-relationship-graph]] (Layer 9) — dyadic bonds; community is the emergent whole that exceeds the sum of those bonds.
- **Foundation:** [[the-social-graph]] (Layer 3) supplies group membership and the Commons primitive the Community Graph builds on.
- **Above:** the [[the-governance-graph|Governance Graph]] — *who decides* the rules a community lives under (Layer 11 in Scheme B; Layer 10 in Scheme A).
- **Overlap:** [[the-culture-graph]] — in Scheme A the shared-meaning territory is carried by the Culture Graph (Layer 12); see [[thirteen-graphs]] for the roster reconciliation.
- **Substrate:** all events are views over the single [[event-graph]].

## Sources & provenance

Compiled from `raw/searles/all-posts-1.md`:
- *"Layer 10: Community"* deep dive · [Searles-Community] · source URL `https://github.com/lovyou-ai/eventgraph/blob/main/docs/layers/10-community.md` (the layer-spec document physically lives there; cited as factual provenance, not re-published) — derivation, the relationship→belonging transition, base operations, the {orientation, temporality, flow, mode} semantic dimensions, the three primitive groups with full decomposition tables, gap analysis, and completeness argument (line ~4241).
- Post 26, *"The Weight"* · [Searles-Weight] · https://mattsearles2.substack.com/p/the-weight — the Layer 10 failure mode in the suffering cascade (line ~5074): *"belonging is binary … no gradient. No memory. No portable history."*
- Post 11, *"Thirteen Graphs, One Infrastructure"*, 2026-03-01 · [Searles-13Graphs] · https://mattsearles2.substack.com/p/thirteen-graphs-one-infrastructure — civilisational-tier framing and the Scheme A/B roster conflict.

The Scheme A vs. Scheme B layer-numbering conflict is documented in [[thirteen-graphs]] and carried forward here without resolution.
