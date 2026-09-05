---
entity: The Identity Graph
org: transpara-ai
primary_placement: civilization/foundational
placements:
  - civilization/foundational
classification: internal
aliases: [identity graph, IdentityGraph, Layer 8, self-sovereign identity, behaviour-first identity]
tier: foundational
status: compiled
last_compiled: "2026-06-14"
sources:
  - raw/searles/all-posts-1.md  # layer spec "Layer 8: Identity" sourced from github.com/lovyou-ai/eventgraph/blob/main/docs/layers/08-identity.md [Searles-L8Spec] — primitives decomposition, gap analysis, semantic dimensions (lines ~3969–4081)
  - raw/searles/all-posts-1.md  # post 11, "Thirteen Graphs, One Infrastructure", 2026-03-01 [Searles-13Graphs] — Layer 8 overview table entry, freelancer example, WorldID comparison (lines ~2287–2312)
  - raw/searles/all-posts-1.md  # post 22, "The Relationship Graph", 2026-03-01 — footer reference to "The Identity Graph (Layer 8 deep dive)" as Post 21 (line ~4236)
  - raw/searles/all-posts-1.md  # scattered cross-graph references: genocide resistance (~5779), refugee portability (~5713), hiring bias (~5669), Sybil resistance (~5494), identity politics (~5046), summary (~8170)
confidence:
  sources: thin
  claims: reconstructed
---

# The Identity Graph

> ⚠ **Thin coverage notice.** The dedicated deep-dive post for the Identity Graph (Post 21, *"The Identity Graph"*, https://mattsearles2.substack.com/p/the-identity-graph) is referenced in the corpus but **not included in it**. The footer of Post 22 (*"The Relationship Graph"*, line ~4236) names it as the immediately preceding post ("Previous: The Identity Graph (Layer 8 deep dive)"), confirming it exists and belongs to the series. What the corpus *does* contain is (a) the Layer 8 layer specification from the `lovyou-ai/eventgraph` GitHub documentation, (b) the overview table entry from Post 11, and (c) scattered cross-graph references throughout later posts. This article reconstructs from those sources. Claims drawn only from the layer spec are marked; claims from the overview post are grounded; claims from scattered references are noted.

**The layer where doing becomes being.** The Identity Graph is Layer 8 in the [[thirteen-graphs]] architecture — the second layer of the Civilisational tier, following the [[the-ethics-graph|Ethics Graph]] at Layer 7 and preceding the Relationship Graph at Layer 9. Its governing concept: identity is not a document you carry or a profile you curate, but the hash-chained record of what you have actually done across all the other graphs.

In the [[thirteen-graphs]] overview post, Layer 8 is positioned as "How Entities Are Verified" and its product graph is described as "self-sovereign identity with narrative and purpose" ([Searles-13Graphs]).

## What the layer is for

The layer spec (sourced from `lovyou-ai/eventgraph/blob/main/docs/layers/08-identity.md`) frames Layer 8 as answering a gap that Layer 7 cannot close ([Searles-L8Spec]):

> "Layer 7 reasons about what should be done, but treats actors as interchangeable moral agents… An actor can behave ethically without knowing *who they are*."

The test case given: "Can you express 'Alice has grown from her early mistakes into someone who values transparency above all, and this is fundamentally different from who she was three years ago, yet she's still recognisably Alice' in Layer 7? You can assess her actions ethically and track her moral responsibility. But 'who she is' (self-concept), 'fundamentally different yet recognisably the same' (continuity through transformation), and 'values transparency above all' (identity-defining commitment rather than abstract duty) have no Layer 7 representation."

The transition the spec names: **Doing → Being**. An actor that does things becomes an actor that *is* something. The four new capacities: Reflect (form an accurate picture of one's own nature), Persist (maintain identity through change), Express (manifest who one is through action), Grow (develop and transform over time).

## The primitives

Layer 8 contains twelve primitives organised in three groups ([Searles-L8Spec]):

**Group 0 — Self-knowledge** (who you are): Narrative, SelfConcept, Reflection, Memory.

**Group 1 — Self-direction** (where you're going): Purpose, Aspiration, Authenticity, Expression.

**Group 2 — Self-becoming** (how you change): Growth, Continuity, Integration, Crisis.

The overview post lists a shorter set — "Self-Concept, Narrative, Reflection, Authenticity, Expression, Growth, Integration, Crisis, Purpose, Aspiration" ([Searles-13Graphs]) — which maps to the same primitives minus the full decomposition. Both sources are consistent on what the layer covers.

The spec's semantic dimensions for organising the primitives ([Searles-L8Spec]):

| Dimension | Values | What it distinguishes |
|-----------|--------|-----------------------|
| Orientation | Inward / Outward | Knowing yourself vs. being known |
| Temporality | Synchronic / Diachronic | Who am I now vs. who have I been and will I be |
| Stability | Constant / Dynamic | Core identity vs. evolving self |
| Agency | Active / Passive | Self-defined vs. ascribed by others |

The spec explicitly claims completeness: three major theories of personal identity — psychological continuity (Continuity, Growth), narrative identity (Narrative, Memory), and recognition theory (Expression, Authenticity) — are all represented. "No gaps found."

## Why current digital identity is broken

The overview post's diagnosis ([Searles-13Graphs]):

> "Identity is fragmented, insecure, and you don't own it. Your government issues you identity documents that can be forged. Your bank runs a KYC process that every other bank also runs from scratch. Your professional reputation lives on LinkedIn, which you don't control. Your credit score is calculated by three companies using opaque algorithms on data that's frequently wrong, and correcting errors is deliberately difficult."

Digital identity is worse: "You prove who you are by knowing a password (which gets stolen), owning a phone (which gets lost), or showing your face (which gets deepfaked). Each platform maintains its own identity silo. None of them interoperate."

The perverse incentive: "identity providers profit from being the sole verifier. If your identity were portable and self-sovereign, you wouldn't need each platform to re-verify you. The current fragmentation isn't a technical limitation — it's a business model. Each identity silo is a captive audience."

## The event-graph version

From the overview post ([Searles-13Graphs]):

> "Identity isn't a document you carry or a profile you curate. It's the hash-chained record of what you've actually done across all the other graphs. Your work history (Work Graph). Your transaction history (Market Graph). Your social connections (Social Graph). Your dispute record (Justice Graph). Your contributions (Research Graph). Your trustworthiness (Ethics Graph)."

The key contrast with existing approaches is the distinction between biometrics-first and behaviour-first identity:

> "WorldID is reaching for this with biometrics-first (iris scans). The Identity Graph is behaviour-first — identity that emerges from what you've done, with biometrics as one verification layer among many. Not 'prove you have unique eyeballs.' Prove you're someone with a history of acting in the world in verifiable ways."

This makes identity portable — derived from the underlying event chains across all graphs, not owned by any single platform. When a user leaves a platform, the identity comes with them; when they join a new one, their history precedes them.

## Cross-graph connections and downstream uses

The corpus contains several scattered references to Identity Graph applications, compiled here:

**Reputation consequences from justice.** When a [[the-justice-graph|Justice Graph]] dispute resolves against someone, "the respondent's non-compliance becomes an event on their Identity Graph — visible to anyone they transact with in the future" ([Searles-JusticeGraph], line ~3495). The Identity Graph is the reputation layer that makes dispute outcomes consequential without requiring state enforcement.

**Hiring and bias reduction.** "Candidates have event-graph-verified track records — not self-reported CVs, but work histories with verifiable completions, skill demonstrations, and peer attestations. Employers see the chain, not the narrative. Bias is harder when the evidence is structural. The Identity Graph meets the Work Graph in the hiring process" (line ~5669).

**Refugee and cross-border portability.** "A portable Social Graph and Identity Graph for people who've been expelled from their Layer 3. Community participation, skills, work history — verifiable and portable across borders. The refugee who arrives in a new country isn't a blank slate. They have a track record" (line ~5713).

> ⚠ **Fail-legible note (refugee application flagged as high-stakes).** The source itself notes: "This requires partnerships with refugee organisations and significant trust in the privacy architecture. The panopticon friction is real here — get it wrong and you've built a tracking system for the most vulnerable people on earth."

**Genocide resistance.** "Every person on earth has an Identity Graph — derived from behaviour, rich, multi-dimensional, portable, theirs. No state can erase it. No platform owns it. No algorithm can flatten it. The mechanism of genocide — reduce to category, deny moral status — fails because identity resists flattening" (line ~5779).

> ⚠ **Fail-legible note (genocide-resistance claim is asserted, not demonstrated).** This is the post's most ambitious claim for the Identity Graph and is stated as an aspiration for the system at global adoption scale, not a property of any current implementation.

**Sybil resistance.** Because reputation on the Identity Graph is earned through behaviour over time, Sybil attacks — deploying many fake accounts to corrupt the reputation system — are claimed to be detectable: "You can create a million fake accounts but you can't create a million fake histories of meaningful interaction across multiple layers over years. The fake agents are identifiable by their shallow graphs" (line ~5494). The post characterises Sybil attacks as "a solved problem in systems where identity is derived from behaviour rather than from registration."

> ⚠ **Fail-legible note (Sybil claim is asserted for the proposed system, not tested at scale).** The source acknowledges insider threats are "genuinely unsolved, and likely unsolvable in the general case."

**Identity politics and complexity.** "Identity politics — on the left and the right — reduces every person to their most politically useful dimension… The Identity Graph that would show the full complexity of a person doesn't exist, so every system that touches identity reduces it to whatever serves the system's purpose" (line ~5046). The implicit claim: a behaviour-first, multi-dimensional Identity Graph structurally resists this reduction.

## Layer boundary with Layer 9

The spec is precise about what Layer 8 is *not* ([Searles-L8Spec]):

> "None of these require concepts from Layer 9 (Relationship). Identity is about individual actors' sense of self. Relationships as entities in their own right — with their own depth, repair cycles, and intimacy — are Layer 9's gap."

Knowing someone's identity (Layer 8) is different from knowing *them* (Layer 9). The [[the-relationship-graph|Relationship Graph]] requires Layer 8 as a prerequisite — you cannot have a relationship without each party having a self — but Layer 8 does not require Layer 9.

## Relationship to the other graphs

- **Below (Layers 1–7):** the Identity Graph is derived from all the lower layers. It is the aggregate view of what someone has done across Work, Market, Social, Justice, Research, Knowledge, and Ethics graphs.
- **Substrate:** a view over the [[event-graph]] — the same hash-chained, causally-linked, append-only store as all other graphs. "Same events. Same hash chains. Same causal links. Different primitives foregrounded."

In the overview post's freelancer example ([Searles-13Graphs]): "The freelancer's record of completing work despite non-payment strengthens their Identity Graph." This is a direct cross-graph dependency — a Work Graph completion event and a Market Graph breach event both become identity-strengthening events on Layer 8. Identity emerges from the chain; it is not separately maintained.

## What is not in the corpus

The dedicated Substack deep-dive post for the Identity Graph (Post 21) is absent from the corpus. The layer spec embedded in the corpus is drawn from the `lovyou-ai/eventgraph` GitHub documentation repository, not from the Searles blog. This spec covers the theoretical primitives decomposition in detail but does not contain the "why it's broken / event graph version / worked example / what it doesn't do" structure that the Justice Graph deep-dive provides. All detailed structural claims in this article derive from the layer spec and the Post 11 overview; the worked-example and deep-application-scenario content is sourced from scattered references across later posts.

> ⚠ **Fail-legible note (source format differs from other graph articles).** The Identity Graph section in `all-posts-1.md` (lines ~3969–4081) is a GitHub documentation file transcluded into the corpus, not a Substack narrative post. It provides richer formal structure (semantic dimensions, gap analysis, completeness argument) but less worked-example material than the Justice Graph post. Claims from the spec are grounded as spec-level design claims; they are not claims about deployed behaviour.

## Sources & provenance

Compiled from `raw/searles/all-posts-1.md`:
- Layer spec *"Layer 8: Identity"*, URL: https://github.com/lovyou-ai/eventgraph/blob/main/docs/layers/08-identity.md · [Searles-L8Spec] — the primitives decomposition (Self-Knowledge/Self-Direction/Self-Becoming groups, twelve primitives), semantic dimensions table, gap analysis, completeness argument, layer boundary statement. Approximate lines 3969–4081.
- Post 11, *"Thirteen Graphs, One Infrastructure"*, 2026-03-01 · [Searles-13Graphs] · https://mattsearles2.substack.com/p/thirteen-graphs-one-infrastructure — Layer 8 overview table entry ("How Entities Are Verified"), primitives shortlist, the broken-identity diagnosis, the WorldID vs. behaviour-first contrast, and the freelancer example (Identity Graph strengthened by cross-graph completion). Approximate lines 2287–2312 and 2065.
- Post 22, *"The Relationship Graph"*, 2026-03-01 · footer at line ~4236 — confirms Identity Graph is Post 21 in the series and was the immediately preceding deep dive.
- Scattered cross-graph references: reputation consequences via Justice Graph (line ~3495); hiring and bias (line ~5669); refugee portability (line ~5713); genocide resistance (line ~5779); Sybil resistance (line ~5494); identity politics (line ~5046); summary entry (line ~8170).

**Gap stated explicitly:** Post 21 (*"The Identity Graph"*, https://mattsearles2.substack.com/p/the-identity-graph) is known to exist but is absent from this corpus. Any future compilation should begin with that post, which likely contains the detailed narrative structure (broken-identity scenarios, worked examples, scope boundaries) comparable to what Post 17 provides for the Justice Graph. `[[wikilinks]]` are forward references; most targets are not yet compiled.
