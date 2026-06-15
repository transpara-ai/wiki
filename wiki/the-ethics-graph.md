---
entity: The Ethics Graph
aliases: [ethics graph, EthicsGraph, Layer 7 ethics, harm detection graph, accountability graph]
tier: foundational
status: compiled
last_compiled: "2026-06-14"
sources:
  - raw/searles/all-posts-1.md  # layer spec "Layer 7: Ethics", following Post 19 marker, lines ~3852–3965 — derivation, primitives, completeness argument, product graph declaration
  - raw/searles/all-posts-1.md  # post 11, "Thirteen Graphs, One Infrastructure", 2026-03-01 [Searles-13Graphs] — Civilisational tier overview; Ethics as Layer 7; freelancer example
  - raw/searles/all-posts-1.md  # post 6, "Fourteen Layers, A Hundred Problems" [Searles-14Layers] — Layer 7 problem statement: what's broken, existing institutions, event graph version; lines ~2255–2285
  - raw/searles/all-posts-1.md  # post 28, "The Weight", 2026-03 [Searles-P28] — "The Ethics Graph doesn't exist. Here's what that looks like." lines ~5022–5030
  - raw/searles/all-posts-1.md  # post 29, "The Transition" [Searles-P29] — Ethics Graph bootstrap as monitoring layer, line ~5223
confidence:
  sources: primary
  claims: grounded
  primitive_table: high — quoted verbatim from the layer spec in the source
  layer_numbering: contested — see note below; Ethics is consistently Layer 7 across all schemes
  product_graph_scope: asserted as horizon — the same caveat from [[thirteen-graphs]] applies; the Ethics Graph is not described as shipped
---

# The Ethics Graph

**The layer where structural facts meet moral values.** The Ethics Graph is the seventh layer in the Searles thirteen-graph framework — the first of the Civilisational tier — and the graph where harm detection, accountability, and verifiable moral reasoning move onto the [[event-graph]]. Its subtitle, from the layer spec, is *"The leap from is to ought; where structural facts meet moral values."*

It is introduced in overview form in Post 11 (*"Thirteen Graphs, One Infrastructure"*, 2026-03-01) as the lens that surfaces ethical patterns from events already recorded by lower graphs, and is fleshed out in a layer-specification document (from `github.com/lovyou-ai/eventgraph/blob/main/docs/layers/07-ethics.md`, appearing in the corpus following Post 19). A standalone high-level treatment appears in Post 6 (*"Fourteen Layers, A Hundred Problems"*).

> ⚠ **Fail-legible note (layer number).** The Ethics Graph is consistently numbered Layer 7 in all sources — the Post 11 "Civilisational tier (Layers 7–10)" table, the layer spec heading, and Post 6. However, the total count of layers varies by scheme (see [[thirteen-graphs]] for the roster conflict). Layer 7 for Ethics is the one stable datum across both naming schemes.

## The gap Ethics fills

The layer spec frames each graph around what the previous layer *cannot* do. Layer 6 ([[the-knowledge-graph-searles|the Knowledge Graph]]) can model information, data, and computation but cannot distinguish *is* from *ought*:

> "A system can process data about an action and compute its effects, but it cannot reason about whether the action itself is right."

The spec provides a test: can you express "The rule is being followed correctly, but the rule itself is unfair to group X, and the person who enforced it meant well but caused disproportionate harm" in Layer 6? You can encode facts about the rule and its enforcement — but *unfair* (evaluating justice), *meant well* (assessing motive), and *disproportionate harm* (weighing consequences against values) have no Layer 6 representation. **Information is not wisdom.**

The transition is labelled **Is → Ought**. The new capacity Ethics adds: reasoning about what *should* be done, not just what is or was done — evaluating actions against moral standing, weighing duties against consequences, and holding actors morally accountable.

## Base operations

Four things an ethical reasoner can do that an information processor cannot:

1. **Evaluate** — assess actions against moral standing
2. **Detect harm** — identify when actions cause damage
3. **Weigh** — balance competing duties and consequences
4. **Hold accountable** — assign moral responsibility

## The twelve primitives

The layer spec decomposes twelve primitives across three groups, with four semantic dimensions (focus, valence, temporality, scope) cross-cutting them.

**Group 0 — Moral Standing** (who and what matters):

| Primitive | What it does |
|-----------|--------------|
| **MoralStatus** | Whether an entity's experience matters morally |
| **Dignity** | The inherent worth of every moral subject |
| **Autonomy** | The right to self-determination |
| **Flourishing** | The conditions for a good life |

The lifecycle of moral standing: whether experience matters is established (MoralStatus) → inherent worth is recognised (Dignity) → self-determination is protected (Autonomy) → conditions for thriving are promoted (Flourishing). The spec notes that MoralStatus is an *irreducible recognition* — it cannot be derived from information alone, which is precisely why Ethics is a separate layer.

**Group 1 — Moral Obligation** (what should be done):

| Primitive | What it does |
|-----------|--------------|
| **Duty** | What one is morally required to do |
| **Harm** | Damage caused to a moral subject |
| **Care** | Prioritising another's wellbeing |
| **Justice** | Fair treatment and equitable distribution |

The lifecycle of moral obligation: duties are identified (Duty) → harm is detected when they're violated (Harm) → wellbeing is actively prioritised (Care) → systemic fairness is assessed (Justice). The soul statement of the whole LovYou project — *"take care of your human, humanity, and yourself"* — flows through Care.

**Group 2 — Moral Agency** (answering for what was done):

| Primitive | What it does |
|-----------|--------------|
| **Conscience** | The inner sense of right and wrong |
| **Virtue** | Stable disposition toward good action |
| **Responsibility** | Who is morally responsible |
| **Motive** | The purpose behind an action |

The lifecycle of moral agency: conscience guides action (Conscience) → virtuous character develops over time (Virtue) → moral responsibility is assigned (Responsibility) → the purpose behind action is assessed (Motive). Together, Motive and Responsibility capture the agent-focused dimensions of moral reasoning.

### Coverage argument

The spec claims completeness across three axes:

1. **Dimensional coverage** — the {focus, valence, temporality, scope} space is covered. The three ethical traditions are all represented through the focus dimension: virtue ethics (agent-focused), deontological ethics (action-focused), and consequentialism (outcome-focused).
2. **Ethical theory coverage** — MoralStatus and Dignity cover moral standing; Duty and Justice cover deontological and consequentialist ethics; Conscience, Virtue, and Motive cover moral psychology; Care covers care ethics.
3. **Layer boundary** — none of the twelve primitives require concepts from Layer 8 (Identity). Ethics reasons about what should be done but treats actors as *interchangeable moral agents*. The concept of an actor's unique character, personal history, and sense of self is Layer 8's gap.

Cross-layer compositions the spec names: *Ethical AI audit* = Justice + Dignity + Layer 6 data; *Restorative justice* = Harm + Responsibility + Care; *Whistleblower protection* = Conscience + Duty + Layer 4 Right.

## What it monitors: a layer above the other graphs

The Ethics Graph is not a stand-alone record of ethical facts — it is a *monitoring layer* running across the lower graphs. Post 6 frames this explicitly:

> "Compliance isn't self-reported. It's verifiable. Every decision an AI makes is an event on the graph with a causal chain showing what inputs it received, what values informed the decision, what authority approved it, and what the outcome was. The regulator doesn't need to trust the company's report — they can verify the chain independently."

The proposed contrast with current institutions is sharp: existing ethics infrastructure is *advisory*, not structural. Ethics review boards have no enforcement power. ESG ratings are paid for by the companies being rated. Regulators are underfunded and subject to revolving-door incentives. Violations are found *after harm has occurred*, and penalties are typically priced in as costs of doing business.

The ethics-as-infrastructure argument: the same way financial auditing does not mean the government reads every transaction — it means the transactions are recorded in a way that *can* be audited — the Ethics Graph provides a verifiable record that the right processes were followed, the right constraints were applied, and the right humans were in the loop.

From Post 11's multi-graph freelancer example: when a regulatory body takes note of a market-payment dispute, "the regulatory body takes note on the Ethics Graph" — it is the lens that activates when patterns of harm, power abuse, or systematic exclusion emerge from events on other graphs.

Post 16's Social Graph deep dive describes the relationship explicitly: **"Ethics Graph (Layer 7): Is the community behaving ethically? Are its norms protecting dignity? Are its sanctions proportionate? The Ethics Graph monitors the Social Graph for patterns of harm — harassment campaigns, exclusion patterns, power abuse — that the community might not see from inside."** A moderation dispute on Discord is simultaneously a Social Graph event (norm violation), a potential Justice Graph event (if it escalates to adjudication), and a potential Ethics Graph event (if the moderation pattern constitutes systematic harm). Same events; different lenses; different primitive clusters activated.

## AI alignment as an Ethics Graph application

The Governance Graph post (Post 24) names the Ethics Graph explicitly as the monitoring partner to AI governance: *"Every AI governance decision on the chain. The Ethics Graph (Layer 7) monitors the patterns. The Justice Graph (Layer 4) handles disputes. The Governance Graph holds the meta-structure: who has authority over this AI, what rules constrain it, and are those rules being followed?"*

AI alignment specifically is framed as a structural problem that current approaches cannot solve: training-time alignment is a one-time property, but alignment is an ongoing state — a model that behaves well in testing may behave differently in production when inputs change. The Ethics Graph addresses this by making the decision chain verifiable in real time: what inputs did it receive, what values informed the decision, what authority approved it, what was the outcome, was the outcome consistent with the values the AI was supposed to embody?

From the layer spec's gap analysis:

| Behaviour | Primitive mapping |
|-----------|-------------------|
| "AI systems have moral status" | MoralStatus |
| "Every participant deserves respect" | Dignity |
| "She has the right to make her own choices" | Autonomy |
| "We have a duty to protect user data" | Duty |
| "This action caused real damage to Alice" | Harm |
| "Group X receives 30% fewer approvals" | Justice |
| "The decision-maker is accountable for this outcome" | Responsibility |

## The cost of its absence

Post 28 (*"The Weight"*) is the most direct statement of what the Ethics Graph's non-existence looks like in practice. The phrase appears twice:

> "The Ethics Graph doesn't exist. Here's what that looks like."

> "The Ethics Graph doesn't exist, so the pattern repeats: harm identified, evidence present, accountability absent."

Post 29 (*"The Transition"*) describes how it begins once built: **"The Ethics Graph begins as a monitoring layer across the lower graphs. Pattern detection for harm. When events on the Work Graph correlate with negative outcomes on other layers — environmental damage, health impacts, safety failures — the correlation surfaces automatically. Not as judgement. As information. The humans decide what to do about it. The graph makes sure they can see it."**

## Trust as a derived property

A recurring theme is that trust on the Ethics Graph is not a rating or a star score — it is derived from behaviour across all the other graphs:

> "Did this entity fulfil its agreements (Market Graph)? Did this employer treat workers with dignity (Work Graph)? Did this community welcome newcomers or harass them (Social Graph)? Did this source's claims hold up over time (Knowledge Graph)? Trust emerges from the chain. Not what people say about you. What the graph shows you did."

The Identity Graph (Layer 8) inherits this: a person's trustworthiness on the Identity Graph is partially constituted by their record on the Ethics Graph, alongside Work, Market, Social, Justice, and Research histories.

> ⚠ **Fail-legible note (product scope — horizon, not shipped).** The Ethics Graph is described across the corpus as a *product horizon*, classified by the [[dark-factory]] synthesis as "product horizon and analogy set, not current implementation scope." The layer spec's claim that "Layer 7 maps to the Ethics Graph — AI alignment with transparent moral reasoning. See `docs/product-layers.md`" is a product-layer mapping, not a deployment claim. The only graph stated to be actively in build as of the corpus is the Work Graph. Treat the Ethics Graph as motivating vision plus structural specification, not a shipped system.

## Relationship to the arc

- **Substrate:** the Ethics Graph is a *view* over [[event-graph]] — every ethical event, harm detection, and accountability record is an append-only, hash-chained entry on the same shared store.
- **Below it:** [[the-knowledge-graph-searles|the Knowledge Graph]] (Layer 6) supplies the information that Ethics evaluates; without provenance-tracked claims, ethical evaluation runs on unverifiable inputs.
- **Adjacent:** [[the-justice-graph]] (Layer 4) handles adjudication of disputes once harm is detected; the Ethics Graph is the monitoring layer that surfaces patterns *before* (and beyond) individual disputes reach adjudication.
- **Above it:** [[the-identity-graph]] (Layer 8) inherits ethical track record as a component of portable identity; [[the-governance-graph]] uses the Ethics Graph as the pattern-monitoring partner for governance accountability.
- **Overview:** [[thirteen-graphs]] for the full schema and naming-scheme conflicts.

## Sources & provenance

Compiled from `raw/searles/all-posts-1.md`:
- Layer spec, *"Layer 7: Ethics"*, from `github.com/lovyou-ai/eventgraph/blob/main/docs/layers/07-ethics.md`, appearing in the corpus at lines ~3852–3965 (following the Post 19 footer) — derivation, gap statement ("Is → Ought"), base operations, twelve primitives with full tables, completeness argument, cross-layer compositions, product graph declaration.
- Post 11, *"Thirteen Graphs, One Infrastructure"*, 2026-03-01 · [Searles-13Graphs] · https://mattsearles2.substack.com/p/thirteen-graphs-one-infrastructure — the Civilisational tier (Layers 7–10), the freelancer regulatory example naming the Ethics Graph, and the "views, not products" thesis.
- Post 6, *"Fourteen Layers, A Hundred Problems"* · [Searles-14Layers] · https://mattsearles2.substack.com/p/fourteen-layers-a-hundred-problems — Layer 7 problem statement: what exists (regulatory bodies, ESG ratings, ethics review boards), why it's broken (advisory not structural, revolving door, after-the-fact), the event graph version (compliance as verifiable, trust derived from chain behaviour); lines ~2255–2285.
- Post 16, *"The Social Graph"*, Layer 3 deep dive — the Ethics Graph's monitoring role over the Social Graph; harassment/exclusion/power-abuse detection; lines ~3318–3320.
- Post 24, *"The Governance Graph"*, Layer 11 deep dive — Ethics Graph named as the pattern-monitoring partner to AI governance; line ~4460.
- Post 28, *"The Weight"* · lines ~5022–5030 — "The Ethics Graph doesn't exist. Here's what that looks like."
- Post 29, *"The Transition"* · line ~5223 — Ethics Graph as Phase 3 monitoring layer; harm correlation surfacing automatically.

**Conflicts stated, not resolved:** (1) **layer numbering** — Ethics is consistently Layer 7 in all sources, though the total frame varies by scheme (see [[thirteen-graphs]]). (2) **product scope** — all thirteen graphs, including Ethics, are classified as product horizon by the [[dark-factory]] docs; nothing in the corpus asserts the Ethics Graph is shipped. (3) **repo identity** — the layer spec cites `github.com/lovyou-ai/eventgraph`; the [[dark-factory]] docs distinguish `transpara-ai/eventgraph` as the selected native core; this conflict is inherited from [[event-graph]] and not adjudicated here. `[[wikilinks]]` are forward references.
