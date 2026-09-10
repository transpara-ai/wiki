---
entity: The Justice Graph
org: transpara-ai
primary_placement: civilization/foundational
placements:
  - civilization/foundational
classification: internal
aliases: [justice graph, JusticeGraph, Layer 4, the dispute layer, evidence-assembly layer]
tier: foundational
status: compiled
last_compiled: "2026-06-14"
sources:
  - raw/searles/all-posts-1.md  # post 17, "The Justice Graph", 2026-03-01 [Searles-JusticeGraph] — the full Layer 4 deep dive (lines ~3361–3529)
  - raw/searles/all-posts-1.md  # post 11, "Thirteen Graphs, One Infrastructure", 2026-03-01 [Searles-13Graphs] — overview table and freelancer multi-graph example
  - raw/searles/all-posts-1.md  # post 16, "The Social Graph", 2026-03-01 [Searles-SocialGraph] — Social-to-Justice escalation description and cross-graph references
confidence:
  sources: primary
  claims: grounded
---

# The Justice Graph

**The layer that resolves disputes when the evidence is already on the chain.** The Justice Graph is Layer 4 in the [[thirteen-graphs]] architecture — the Institutional tier's first graph — and its central claim is an inversion of how justice currently works: instead of assembling evidence after a dispute arises, the evidence exists before the dispute is filed, because all the underlying interactions happened on hash-chained lower-layer graphs.

The argument is not that the Justice Graph replaces judges. It is that it replaces the $200-billion-a-year global evidence-assembly industry that exists because interactions are not recorded properly in the first place. That industry is the post's explicit target.

The deep-dive post (Post 17, *"The Justice Graph"*, 2026-03-01) was authored by Matt Searles (+Claude) and published at https://mattsearles2.substack.com/p/the-justice-graph. Its subtitle states the thesis: *"Justice is expensive because evidence is expensive. What if the evidence already existed?"*

## The primitives

Layer 4 contains twelve primitives ([Searles-JusticeGraph]):

> Sovereignty, Authority, Law, Rights, Adjudication, Punishment, Restitution, Precedent, Jurisdiction, Due Process, Evidence, Testimony.

The post frames these as universal — every civilisation has built Layer 4 infrastructure, from courts to councils of elders to religious arbitration — and notes that the digital world has "almost none of this." The specific form varies; the function is invariant: an authoritative third party examines evidence, applies rules, and produces a binding resolution. Layer 4 is what happens when Layers 1–3 break: work not done as agreed, value not exchanged as promised, social norms violated or enforced unjustly.

## The $200 billion problem

The post's opening economic argument: the global legal services market is worth over $1 trillion annually, of which roughly $200 billion is spent on discovery — finding, collecting, and presenting evidence. A civil lawsuit proceeds by having lawyers spend months reconstructing a timeline of events from fragmentary, contradictory, and often deliberately incomplete records. The vast majority of legal cost is in assembly, not adjudication.

The source's diagnosis of *why* this persists as a structural feature, not merely a technical lag ([Searles-JusticeGraph]):

> "The perverse incentive: the legal profession profits from complexity. Every hour spent on discovery is a billable hour. Every procedural motion is a billable event… The people who would need to implement these changes are the people whose livelihood depends on the current system's inefficiency."

The same pattern holds for platform dispute resolution (Uber, Airbnb, Amazon, PayPal): "This isn't dispute resolution. It's dispute management — minimising the platform's costs while creating the appearance of fairness." Evidence reviewed is "whatever each party typed into a text box." The standard of proof is "which outcome costs the platform least?"

Small disputes are effectively unresolvable: someone owed $500 has no economic recourse because the cost of accessing justice exceeds the claim. The source estimates that for most people in most disputes below a few thousand dollars, no functioning justice system exists.

## The event-graph version

The Justice Graph's solution depends on the lower layers ([Searles-JusticeGraph]):

> "If the work was done on the Work Graph, the payment was on the Market Graph, and the agreement was recorded as events — then when a dispute arises, the evidence already exists. The complete causal chain is there. The Justice Graph doesn't need to *find* the evidence. It needs to *adjudicate* it. That cuts 80% of the cost and time out of dispute resolution."

### Disputes as events

A dispute is itself an event — one party claims the other has breached an obligation, violated a norm, or caused unjustified harm. The dispute event links to the evidence: relevant events on the [[the-work-graph|Work Graph]], [[the-market-graph|Market Graph]], or [[the-social-graph|Social Graph]] that show what happened. Neither party assembles evidence; they point to the chain.

Both parties and the adjudicator look at the same chain — not competing narratives, not reconstructed timelines, but actual events in order with causal links, cryptographically verified.

### Tiered adjudication

The post specifies four tiers ([Searles-JusticeGraph]):

**Tier 1 — automatic resolution.** If the agreement event has clear conditions and the fulfilment events either meet them or do not, resolution is mechanical. "The contract said 'deliver by March 5.' The delivery event timestamp is March 7. Breach is a fact, not a judgment. The restitution terms specified in the agreement activate automatically. No human required."

**Tier 2 — AI arbitration.** For disputes requiring interpretation ("the deliverable didn't meet the quality standard"), an AI arbitrator examines the evidence chain, agreement terms, and precedent events from similar disputes, and proposes a resolution. Both parties can accept or escalate.

**Tier 3 — human adjudication.** For genuine ambiguity, ethical complexity, or high stakes — a human arbitrator or panel with the same evidence the AI had, plus the AI's analysis, plus the ability to exercise judgment the post acknowledges AI currently cannot match.

**Tier 4 — formal legal proceedings.** For disputes exceeding the Justice Graph's jurisdiction or requiring state enforcement power — the event-graph evidence package can be exported for use in traditional courts. "The hash-chained record is more trustworthy than the evidence courts currently receive, and the assembly cost is zero."

The stated insight: most disputes are small with clear evidence pointing to obvious resolution. The Justice Graph handles the 80% of disputes that are straightforward, cheaply and quickly, "so that the 20% that require human judgment get the attention they deserve."

### Precedent on the chain

Every resolution is an event linking to the dispute, the evidence, the reasoning, and the outcome. Over time the Justice Graph accumulates machine-readable common law: "Judges decide cases. The decisions become precedent. Future judges apply precedent to similar cases. The Justice Graph makes this process explicit and machine-readable." The precedent is transparent — both parties can see what prior decisions are being cited and can challenge their relevance.

### Jurisdiction

The Justice Graph's authority is initially only what parties grant it — voluntary submission analogous to a private arbitration clause (JAMS, AAA, ICC). The post frames this as the same mechanism that already underpins commercial arbitration, "with better evidence, lower costs, and transparent precedent." Over time, if outcomes are consistently fair and cheaper than courts, governments might recognise its decisions as enforceable, as many jurisdictions already recognise private arbitration outcomes.

> ⚠ **Fail-legible note (government recognition is speculative).** The post describes state recognition of Justice Graph decisions as a possible long-run trajectory, not a current or near-term fact. "That's a long road."

## The $500 dispute, worked through

The post gives a concrete worked example ([Searles-JusticeGraph]):

> "Someone owes you $500 and won't pay. On the Justice Graph: The agreement is on the Market Graph. The work is on the Work Graph. The delivery is verified. The non-payment is a fact — the payment event didn't occur within the obligation window. You file a dispute event. The system checks the chain: agreement, fulfilment, non-payment. The case is Tier 1 — the evidence is unambiguous. The restitution terms from the agreement activate. If the respondent doesn't comply, the dispute escalates to Tier 2… The ruling becomes a precedent event. The respondent's non-compliance becomes an event on their Identity Graph — visible to anyone they transact with in the future. Total cost: near zero. Time to resolution: hours, not months."

## AI agents and the authority chain

The post addresses a scenario "coming whether we're ready or not": an AI agent operating on a human's behalf makes an unauthorised commitment. Current legal frameworks have no answer because they were not designed for non-human actors.

The Justice Graph handles this via the authority model already on the chain: every AI agent operates within defined authority bounds — events showing what it is permitted to do, who authorised those permissions, and what escalation rules apply. If the AI exceeded its authority, the chain shows exactly where. Liability follows the authority chain:

- Human set authority bounds too loosely → human decision (an event) with foreseeable consequences.
- AI operated within bounds but outcome was harmful → authority-granting event is the point of accountability.
- AI exceeded bounds due to a bug → liability may shift to the builder.

"The chain makes the analysis possible. Without it, you're just arguing about whose fault it is with no evidence."

## What the Justice Graph does not do

The post is explicit about scope boundaries ([Searles-JusticeGraph]):

**Does not prevent disputes.** Prevention is the job of well-designed agreements (Market Graph), well-governed communities (Social Graph), and well-bounded authority models. The Justice Graph is what happens when prevention fails.

**Does not replace criminal justice.** Criminal law involves state power — the authority to deprive people of liberty. The Justice Graph has no police, no prisons, and no enforcement mechanism beyond reputation consequences and voluntary compliance. It handles civil disputes between parties who have agreed to its jurisdiction.

**Does not guarantee fairness.** A Tier 2 AI arbitrator might be biased. A Tier 3 human panel might make a bad call. Precedent might encode historical unfairness. The Justice Graph makes *process* transparent and *evidence* complete; whether the *judgment* is fair depends on the adjudicators and the rules they apply. "Better evidence and transparent process improve the odds. They don't guarantee the outcome."

## Relationship to the other graphs

- **Below (Layers 1–3):** the Justice Graph is the "failure mode" of the lower layers. Disputes arise when the [[the-work-graph|Work Graph]], [[the-market-graph|Market Graph]], or [[the-social-graph|Social Graph]] produce unresolved conflicts. Its evidence is drawn from those chains.
- **Above (Layers 5–13):** outcomes of Justice Graph proceedings become events that feed the [[the-identity-graph|Identity Graph]] (reputation consequences), the [[the-ethics-graph|Ethics Graph]] (patterns of systematic harm), and the Governance Graph (meta-rules about who decides).
- **Substrate:** like all thirteen graphs, it is a view over the [[event-graph]], not a separate system. "Same events. Same hash chains. Same causal links. Different primitives foregrounded."

In the overview post's freelancer example ([Searles-13Graphs]): when the client did not pay, "that's a Justice Graph event" — but the work (Work Graph), the transaction (Market Graph), the social discussion (Social Graph), and the regulatory note (Ethics Graph) are all also active simultaneously from the same underlying events. The Justice Graph is the lens, not a separate database.

> ⚠ **Fail-legible note (the "views, not products" universality is vision, not shipped fact).** The [[dark-factory]] synthesis classifies the entire thirteen-graphs set as "product horizon and analogy set, not current implementation scope." As of the corpus, only the [[the-work-graph|Work Graph]] is described as being actively built. The Justice Graph is described at the design level; there is no corpus evidence of a deployed Justice Graph instance.

## Sources & provenance

Compiled from `raw/searles/all-posts-1.md`:
- Post 17, *"The Justice Graph"*, 2026-03-01 · [Searles-JusticeGraph] · https://mattsearles2.substack.com/p/the-justice-graph — the full Layer 4 deep dive: primitives list, the $200 billion evidence problem, "why current digital justice is broken," the event-graph version (disputes as events, tiered adjudication, precedent on the chain, jurisdiction), the $500 dispute worked example, AI agents and the authority chain, and the explicit scope boundaries (no criminal justice, no fairness guarantee). Approximate lines 3361–3529.
- Post 11, *"Thirteen Graphs, One Infrastructure"*, 2026-03-01 · [Searles-13Graphs] · https://mattsearles2.substack.com/p/thirteen-graphs-one-infrastructure — the overview table placing Justice at Layer 4 (Institutional tier), the freelancer multi-graph worked example, and the "views, not products" substrate claim. Approximate lines 2055–2500.
- Post 16, *"The Social Graph"*, 2026-03-01 — the Social-to-Justice escalation paragraph: "When social norms are violated and the community's own mechanisms can't resolve it, the dispute escalates to the Justice Graph." Approximate lines 3316–3320.

Post series framing: the footer of Post 18 (*"The Research Graph"*) at line 3680 confirms the Justice Graph is Post 17 ("Previous: The Justice Graph (Layer 4 deep dive)"), clarifying corpus position. `[[wikilinks]]` are forward references; most targets are not yet compiled.
