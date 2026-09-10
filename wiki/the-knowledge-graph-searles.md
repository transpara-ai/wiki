---
entity: The Knowledge Graph (Searles)
org: transpara-ai
primary_placement: civilization/foundational
placements:
  - civilization/foundational
classification: internal
aliases: [Knowledge Graph, Layer 6 Knowledge Graph, the provenance layer, the truth graph, the information layer, the claim-provenance layer]
tier: foundational
status: compiled
last_compiled: "2026-06-14"
sources:
  - raw/searles/all-posts-1.md  # post 19, "The Knowledge Graph", 2026-03-01 [Searles-Knowledge] — full deep dive: information crisis, claims as events, evidence chains, challenge events, source reputation, AI-generated content, democracy framing, where research meets knowledge
  - raw/searles/all-posts-1.md  # post 11, "Thirteen Graphs, One Infrastructure", 2026-03-01 [Searles-13Graphs] — Layer 6 compact statement (L2227-2252): primitives, what-exists, why-broken, event-graph version
confidence:
  sources: primary
  claims: grounded
  knowledge_graph_as_built: thin — asserted design, not a shipped product; no Open Brain operational record exists for it
  "democracy" claim: asserted — the "load-bearing layer of democratic governance" framing is normative, not demonstrated
  c2pa_description: grounded — the post's description of C2PA as file-level provenance matches public documentation
---

# The Knowledge Graph (Searles)

**Layer 6 of the arc — the claim-provenance layer.** Not to be confused with the general AI/graph-database concept of a "knowledge graph." In Searles' framework, the Knowledge Graph is the proposed view of an [[event-graph]] in which every **claim** — a news report, a political assertion, a scientific finding entering public discourse, a product claim, an AI-generated statement — is recorded as a causally linked, hash-chained event carrying its evidence, its source, and its challenge history. Its subtitle is blunt: *"Nobody agrees on what's real anymore. Not because people are stupid, but because the information layer has no accountability architecture"* ([Searles-Knowledge]).

It enters the arc in two passes: first as a compact statement in the [[thirteen-graphs]] survey (**Post 11, 2026-03-01**), then as a full deep dive in **Post 19, *"The Knowledge Graph"* (2026-03-01)** ([Searles-Knowledge]), trailed from Post 18: *"Next deep dive: the Knowledge Graph — what happens when claims, sources, and truth itself move onto the event graph."*

This article uses the slug `the-knowledge-graph-searles` to avoid confusion with the separate computer-science concept.

> ⚠ **Fail-legible note (status).** The Knowledge Graph is a design, not a deployment. The post ends with a "start small" programme — building claim provenance into individual tools people already use, not "fix the global information ecosystem" — and acknowledges the value compounds with adoption. There is no Open Brain operational record for a Knowledge Graph implementation. Treat every mechanism below as asserted design, not shipped fact.

## What it is a view of

The Knowledge Graph is not new infrastructure. It is the [[event-graph]] — the same append-only, SHA-256 hash-chained, causally-linked directed acyclic graph — with **Layer 6 (Information) primitives foregrounded**: *Symbol, Language, Encoding, Record, Channel, Copy, Data, Computation, Algorithm, Noise, Entropy, Measurement, Knowledge, Model, Abstraction* ([Searles-Knowledge], [Searles-13Graphs]).

The post distinguishes Layer 6 from Layer 5: "Layer 5 handles how knowledge gets created. Layer 6 handles something more fundamental: how information gets represented, transmitted, verified, and corrupted." The [[the-research-graph|Research Graph]] produces findings; the Knowledge Graph tracks what happens to those findings — and to every other claim — once they enter the information ecosystem.

The post notes that Layer 6 is *"perfectly neutral"* in the gender-dimension analysis from Post 7: "zero masculine, zero feminine. Pure computational substrate. Information doesn't care about anything. It just represents." The neutrality is the structural problem: information infrastructure has no built-in preference for truth over falsehood, so if you want systems that favour truth, "you have to build that preference into the architecture. Nobody has."

## The information crisis

The post's structural diagnosis focuses on what replaced editorial gatekeeping: algorithmic curation. Facebook, Google, Twitter, TikTok decide what you see based on engagement, and engagement "correlates with novelty, outrage, and tribal confirmation, not with accuracy." The result is that "the same event produces completely different informational realities depending on which algorithm feeds you. Not different interpretations of the same facts — different facts entirely."

The AI intensifier (described as the "urgent 2026 problem"): "the cost of producing convincing misinformation is approximately zero." AI can generate realistic text, images, audio, and video indistinguishable from human-created content. The asymmetry is structural: "Fabrication is cheap. Verification is expensive. In an information ecosystem optimised for speed and engagement, the cheap option wins." The platforms that distribute content are "legally and economically insulated from the accuracy of what they distribute. They're not publishers. They're pipes. If the pipe is full of poison, the pipe isn't liable."

## What has been tried

The post evaluates existing approaches before proposing its own:

**Fact-checking** (Snopes, PolitiFact, Full Fact): "valuable but fundamentally unscalable. The volume of claims circulating online exceeds the capacity of every fact-checking organisation on earth combined by orders of magnitude."

**Content moderation:** reactive (content has already spread before it's caught), inconsistent, opaque, and biased toward platform revenue interests. "Moderation doesn't address the root cause — it addresses individual pieces of content without touching the infrastructure that produces and distributes them."

**Content provenance standards (C2PA):** the post identifies C2PA as "the closest existing approach to what the Knowledge Graph proposes." C2PA adds cryptographic signatures to media files, establishing a chain of custody from creation to publication. The post's critique: "C2PA operates at the file level — was this image modified? Was this video AI-generated? The Knowledge Graph operates at the claim level — is this assertion supported by evidence? File-level provenance is necessary but insufficient. A genuine, unmodified photograph can be used to support a false claim simply by providing misleading context."

## The event graph version

The Knowledge Graph is not a truth engine. The post is emphatic: "It doesn't tell you what's true. It shows you the provenance of any claim — the complete chain from assertion to evidence — so you can make your own assessment with full visibility into the information supply chain." ([Searles-Knowledge].) The infrastructure is neutral; the assessment belongs to the viewer.

### Claims as events

A claim is an event on the Knowledge Graph. Someone asserted something, at a specific time, through a specific channel. The claim event records: who made the claim (linked to their Identity Graph), what they claimed, when, what evidence they cited, and what their stated basis was.

"Not every utterance needs to be a claim event. Casual conversation isn't on the Knowledge Graph. But claims that enter public discourse — news reports, policy statements, scientific findings, product claims, political assertions — these are events with provenance."

### Evidence chains

A claim event links to its evidence. *"The unemployment rate is 4.2%"* links to the Bureau of Labour Statistics data release event. *"This product cures cancer"* links to — what? If there is no evidence link, that is visible. The absence of evidence is information: *"This claim has been circulating for three weeks with no source ever attached"* is a useful signal, and the Knowledge Graph makes it visible.

Evidence can be primary (the researcher collected the data — a [[the-research-graph|Research Graph]] chain), secondary (a journalist reported on research — linking to the original), or absent. The post is explicit: absence is not proof of falsehood, but it is a signal.

### Challenge events

When someone disputes a claim, that is a challenge event: it links to the original claim and to the counter-evidence. The claim and its challenges coexist on the graph. "The Knowledge Graph doesn't resolve the dispute. It shows that a dispute exists, what each side argues, and what evidence each side cites. The viewer can assess."

Over time a claim accumulates a history: original assertion, supporting evidence, challenges, counter-evidence, responses to challenges, independent verification, replication (from the Research Graph). "The claim's provenance thickens. A heavily contested claim with strong evidence on both sides looks different from an uncontested claim with no challenges, which looks different from a claim that's been debunked by multiple independent sources."

### Source reputation

Just as the Market Graph derives reputation from transaction history, the Knowledge Graph derives source reputation from claim history. A source whose claims consistently survive challenges builds credibility on the graph. A source whose claims are frequently debunked loses it — not as a rating, but "as a verifiable track record." The mechanism applies to individuals, organisations, and AI systems equally.

The post's explicit limit: "The Knowledge Graph is not a ministry of truth. It doesn't adjudicate claims. It doesn't censor falsehoods. It doesn't rank sources authoritatively. It provides transparent provenance." ([Searles-Knowledge].) This is the key distinction from fact-checkers or trust-scorers that adjudicate.

## AI-generated content

The post frames AI-generated content as the Knowledge Graph's immediate application:

When an AI generates content, the Knowledge Graph records it as an event with specific provenance: which model, which prompt, which parameters, when, by whom. "If your AI-generated article has full provenance — here's the model, here's the prompt, here's the sources the model drew on — it enters the information ecosystem as a transparent AI contribution. It can be evaluated on its merits. It's honest about what it is."

Content without provenance becomes suspect by absence: "This image has no creation chain" functions the way "this $100 bill has no serial number" functions in financial systems — not proof of forgery, but a reason to look closer. The post acknowledges technical measures (watermarking, C2PA) help but are not foolproof; the Knowledge Graph adds a complementary layer through structural incentive rather than technical enforcement.

## The democracy claim

The post makes a stronger normative claim in its "Missing Infrastructure of Democracy" section:

> "Democracy requires informed citizens. Informed citizens require reliable information. Reliable information requires infrastructure that incentivises accuracy and makes provenance visible. None of that infrastructure exists at the level required for a functioning democracy in the age of AI-generated content and algorithmic curation."

The reduced framing: "A democracy where citizens can't agree on facts is a democracy where voting is based on which informational shard you happen to inhabit. That's not self-governance. It's algorithmic governance wearing the costume of democracy."

> ⚠ **Fail-legible note (democracy / normative claim).** The "load-bearing layer of democratic governance" characterisation is the post's strongest normative assertion. It is stated as a structural observation, not a partisan one, but it is **asserted, not demonstrated** — the connection from "information provenance" to "functional democracy" relies on premises about democratic epistemics that the post does not argue from first principles. Carried here because the source carries it; labelled as such.

## Where research meets knowledge (the pipeline)

The post describes the Layer 5-to-Layer 6 pipeline and its current breakage:

> "A nuanced finding gets summarised in a press release that loses the nuance. The press release becomes a headline that distorts the summary. The headline becomes a tweet that distorts the headline. By the time the finding reaches the public, it bears little resemblance to the original research."

On the event graph, the chain is traceable: "The public claim links to the news article, which links to the press release, which links to the paper, which links to the data. If the headline distorts the finding, you can walk the chain back to the original and see the distortion." The same logic applies to AI summaries: the summary event links to the paper event; if the summary distorts the finding, the distortion is traceable on the chain.

## What this actually looks like (stated buildable start)

The post commits to a "start small" programme rather than "fix the global information ecosystem":

- A Substack post where every factual claim links not to a URL (which may change) but to a hash-chained source event with its own provenance.
- A Twitter-like platform where claims from verified sources carry their evidence chain visibly.
- An AI chatbot that shows provenance of every assertion: "not 'according to my training data' but 'this claim traces to this specific source, published on this date, with this evidence base, challenged by these counter-claims.'"

"None of this requires everyone to adopt a new system simultaneously… The value compounds as adoption grows — the more claims have provenance, the more suspicious provenance-free claims become — but the starting point is individual tools."

## Relationship to the rest of the arc

- **Substrate:** the Knowledge Graph is a view over [[event-graph]] — the same append-only, hash-chained, causally-linked store. The claim/challenge/source-reputation event types are new; the infrastructure is shared.
- **Layer 5 predecessor:** the [[the-research-graph|Research Graph]] is Layer 5; the Knowledge Graph is Layer 6. Research Graph produces findings; Knowledge Graph tracks what happens to them in public discourse. The post explicitly positions them as deeply connected: "The pipeline from research to public knowledge is broken at every joint." A hash-chained link from public claim back to the original data is the stated fix.
- **Thirteen-graph frame:** the Knowledge Graph is Layer 6 of the [[thirteen-graphs]] — the institutional tier, alongside Justice (Layer 4) and Research (Layer 5). See [[thirteen-graphs]] for the naming-scheme conflict (Scheme A vs. Scheme B) that affects the roster but not Layer 6 itself, which is consistent across both schemes.
- **Work Graph connection:** the arc's bootstrapping logic has Layer 6 riding on Layers 1–5. The [[the-work-graph|Work Graph]] (Layer 1) is the only layer described as being built ("this week") at the time of the post.
- **C2PA relationship:** the post positions the Knowledge Graph as operating at a higher level of abstraction than C2PA: file-level provenance (C2PA) is necessary but insufficient; claim-level provenance (Knowledge Graph) is where trust actually lives.

> ⚠ **Fail-legible note (building sequence).** The thirteen-graphs post is explicit that only the Work Graph is described as being built. The dark-factory docs classify the full thirteen-graph set as "product horizon and analogy set, not current implementation scope." The Knowledge Graph's build date is unknown from this corpus. The "start small / individual tools" framing in the post suggests the author views Layer 6 as partially approachable without the full stack, but no implementation is documented.

## Sources & provenance

Compiled from `raw/searles/all-posts-1.md`:
- Post 19, *"The Knowledge Graph"*, 2026-03-01 · [Searles-Knowledge] · https://mattsearles2.substack.com/p/the-knowledge-graph — the full deep dive: information crisis, algorithmic curation diagnosis, AI intensifier, existing-approaches survey (fact-checking/moderation/C2PA), claims-as-events model, evidence chains, challenge events, source reputation, AI-generated-content provenance, democracy framing, research-to-knowledge pipeline, buildable start. Approximately lines 3685–3848.
- Post 11, *"Thirteen Graphs, One Infrastructure"*, 2026-03-01 · [Searles-13Graphs] · https://mattsearles2.substack.com/p/thirteen-graphs-one-infrastructure — Layer 6 compact statement: primitives, "what exists" (Reuters, AP, BBC, Wikipedia, Google News), "why it's broken," "event graph version" ("every claim has a source… not a truth engine that tells you what to believe. A truth graph that shows you the provenance") (L2227-2252 approximately). Overview context and "views, not products" thesis.

**Conflicts stated, not resolved:** (1) The Knowledge Graph is asserted design, not deployment; no operational record exists in Open Brain. (2) The "trivial technology" framing inherited from the thirteen-graphs post is complicated by the operational concurrency cost documented in [[event-graph]] (see that article's "fail-legible note on trivial technology"). (3) Repo identity conflicts (mind-zero-five vs. transpara-ai/eventgraph vs. lovyou-ai/eventgraph) from [[event-graph]] apply here equally. (4) The democracy / "load-bearing layer" claim is normative and asserted, not demonstrated. `[[wikilinks]]` are forward references; [[the-research-graph]] is the direct predecessor compiled in the same session.
