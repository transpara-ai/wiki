---
entity: The Market Graph
aliases: [Market Graph, Layer 2 Market Graph, the exchange layer, the toll-booth economy]
tier: concept
status: compiled
last_compiled: 2026-06-13
sources:
  - raw/searles/all-posts-1.md  # post 15, "The Market Graph", 2026-03-01 [Searles-Market] — full deep dive: toll-booth economy, exchange primitives as events, portable reputation, escrow-as-event-pattern, AI market participants
  - raw/searles/all-posts-1.md  # post 9/"Thirteen Graphs, One Infrastructure" region, Layer 2 summary, L2115-2139 [Searles-13Graphs-L2] — the compact Layer 2 statement (primitives, what-exists, why-broken, event-graph version)
  - /Transpara/transpara-ai/repos/docs/dark-factory/all-posts 1.md  # first-party copy of the Searles corpus; same text + cross-graph references (escrow/reputation/identity touch-points; worked cross-graph dispute example L2065)
confidence:
  toll_booth_diagnosis: high for the descriptive claim (platforms charge X% to mediate trust); the take-rate figures themselves are the author's, uncited to primary platform data
  take_rate_numbers: source-internal conflict — subtitle says "25%"; body gives ranges (Uber 25-30%, Airbnb 14-20%, Upwork 10-20%); inflated-rating floor differs 4.7 vs 4.8 across the two passages (see "Source conflicts")
  market_graph_as_built: NOT built — asserted design, not shipped. Only the Work Graph is described as under construction; the Market Graph is "incremental on top of" it, "in days, not months." No Open Brain operational record exists for it.
  portable_reputation / escrow_without_third_party: asserted mechanism, not demonstrated — no implementation, benchmark, or live deployment cited
  trust_as_public_good: normative/economic claim by the author, unproven
---

# The Market Graph

**Layer 2 of the arc — the exchange layer.** The Market Graph is the proposed view of an [[event-graph]] in which every **offer, acceptance, delivery, and payment** is a causally linked, hash-chained event, so that *reputation* and *escrow* live in the event structure itself rather than being held by a rent-extracting platform. It is the direct sequel to [[the-work-graph|the Work Graph]] (Layer 1, Agency): "work doesn't exist in isolation… the moment value changes hands, you've crossed from Layer 1 (Agency) to Layer 2 (Exchange)" ([Searles-Market]).

It enters the arc as **Post 15, *"The Market Graph"* (2026-03-01)** ([Searles-Market]), trailed at the end of the Work Graph post — *"Next deep dive: the Market Graph — what happens when exchange, escrow, and reputation move onto the same event infrastructure"* — and stated in compact form inside the thirteen-graphs survey ([Searles-13Graphs-L2], L2115-2139). It is one of the [[thirteen-graphs]] that the corpus frames as **views over one substrate**, not separate products.

> ⚠ **Fail-legible note (status). The Market Graph is a design, not a deployment.** The source is explicit that the *Work* Graph is the thing being built ("I'm deploying this week"); the Market Graph is described only as *incremental* on top of it — "a developer who's built the Work Graph can add Market Graph capabilities in days, not months" ([Searles-Market]). There is **no Open Brain operational record** for a Market Graph (searched this run — none found), consistent with it being an unbuilt Layer 2 horizon. Treat every mechanism below as **asserted design**, not shipped fact.

## What it is a view of

The Market Graph is not new infrastructure. It is the [[event-graph]] — the same append-only, SHA-256 hash-chained, causally-linked store — with **Layer 2 (Exchange) primitives foregrounded**: *Offer, Acceptance, Obligation, Reciprocity, Property, Contract, Debt, Gift, Competition, Cooperation, Scarcity, Surplus* ([Searles-Market], [Searles-13Graphs-L2]). The post's framing: "the building blocks of every transaction that's ever happened between two entities… Humans have been doing this for ten thousand years. The primitives haven't changed. What's changed is who sits between the two parties and how much they charge for the privilege" ([Searles-Market]). The relationship to the underlying primitive ladder is [[the-20-primitives]] → … → the layered expansion ([[fourteen-layers]]); Exchange is the layer above Agency.

## The toll-booth economy (the problem it targets)

The diagnosis: "Every marketplace extracts rent for mediating trust" ([Searles-13Graphs-L2]). The two-sided platform sits between buyer and seller and takes a percentage for providing three things, of which the source argues **two are commodities**:

- **Discovery** — matching supply to demand. "In 2026 this is a solved problem. Any LLM can match supply to demand… not worth 25% of every transaction forever" ([Searles-Market]).
- **Payment processing** — "Stripe charges 2.9% + 30 cents… It is definitely not worth 25%" ([Searles-Market]).
- **Trust** — "the belief that the other party will do what they promised. **This is the real product.** Discovery and payments are the excuse. Trust is the moat" ([Searles-Market]).

The named take-rates (the author's figures): **Uber 25-30%, Airbnb 14-20% combined, Upwork 10-20%**, with "Fiverr, DoorDash, TaskRabbit, Etsy — the same model everywhere" ([Searles-Market]). The compact Layer 2 statement gives the same trio ([Searles-13Graphs-L2]).

> ⚠ **Fail-legible note (the numbers are the author's, and conflict internally).** The take-rate percentages are asserted by the author and are **not cited to primary platform disclosures**; treat as illustrative magnitudes, not audited rates. They also conflict *within the corpus* — see "Source conflicts" below.

### Why the trust layer is the weak point

The post argues the moat is also the most broken component, on four grounds ([Searles-Market]):

1. **Reviews are gamed.** A fake-review industry "worth hundreds of millions"; ratings degraded to where "sophisticated buyers ignore star ratings entirely." Reviews are "claims without chains" — opinions about past transactions with no verification that the account matches what happened.
2. **Reputation is captive.** "A driver with a 4.95 rating on Uber has that rating *on Uber*." A ban erases years of reputation overnight "because the reputation lives on the platform, not with the person." Non-portability is the lock-in: "The platform doesn't just mediate trust. It *holds trust hostage*."
3. **Dispute resolution favours the platform.** The arbiter is not neutral — it optimises for its own support costs and retention, "a thumb on the scale" ([Searles-Market]).
4. **The deeper perverse incentive.** Platforms "profit from being the *only* place buyers and sellers can trust each other… So every platform actively prevents trust from becoming portable. Not through conspiracy. Through architecture. They simply don't build the export function" ([Searles-Market], echoed [Searles-13Graphs-L2]).

## The event-graph version (the asserted mechanism)

The proposed collapse: "The Market Graph is Exchange primitives on the event graph. Every transaction element is an event with full causal provenance" ([Searles-Market]). Each primitive becomes an event linked to its cause:

- **Offer** — an event (what, price, conditions, expiry), hash-chained and timestamped; "it can't be edited silently — any change is a new event linked to the original."
- **Acceptance** — an event linked to *the specific offer version* accepted, so "disputes about what was agreed become trivially resolvable because the agreement is an immutable event."
- **Obligation** — events with conditions (deliver by date/spec; pay within a window after confirmation). The post calls these "the smart contract — but in human language, not Solidity code."
- **Fulfilment** — the delivery event can link back to the [[the-work-graph|Work Graph]] chain that produced the deliverable, so "provenance isn't a marketing claim. It's the chain."
- **Payment** — links to delivery → acceptance → offer, giving "a single walkable graph" from "I want this" to "I got it and paid for it."

### Portable, verifiable reputation

The load-bearing claim: reputation "isn't a star rating owned by a platform — it's the chain itself" ([Searles-Market]) — a **hash-chained history of actual transactions** ([Searles-13Graphs-L2]): completed-transaction count, fulfilment-vs-dispute ratio, median acceptance-to-delivery time, on-time-payment record. Because it is *derived from behaviour on the graph*, "you carry it wherever you go… A new marketplace can query your Market Graph history and see, with cryptographic certainty, that you've completed 500 transactions with a 98% fulfilment rate" (the 500/98%/3-day figures are illustrative, not measured). The asserted economic consequence: "**Portable, verifiable reputation kills the toll booth.** If trust is independent of the platform, the platform's only remaining value is discovery and payment processing — both commodities worth 3-5%, not 25%."

> ⚠ **Fail-legible note (mechanism unproven).** Portable reputation is an *asserted* design — no implementation, schema, or deployment is shown. The corpus elsewhere generalises the same idea to identity and credentials ("append-only… you can't delete your bad reviews, and the good ones are cryptographically linked to real transactions"; first-party copy, "all-posts 1.md" L1124-1128) — but that, too, is a "what this touches" horizon, not a built feature.

### Escrow without a third party

"On the Market Graph, escrow is an event pattern, not a third party" ([Searles-Market]). The buyer's payment event is created **conditional**, linked to an obligation event defining release conditions; when the delivery event matches, the payment event resolves; if not, it "remains pending and links to a dispute event." The claimed property: the escrow logic is "on the graph, visible to both parties, defined in the agreement, and enforced by the event structure. Not by a platform employee."

The post positions this explicitly against crypto: "This is what smart contracts were supposed to be. Crypto got the insight right (code-enforced agreements without intermediaries) and the implementation wrong (inflexible, written in programming languages non-developers can't read, running on blockchains with real environmental and scalability costs)" ([Searles-Market]). This mirrors the [[event-graph]]'s own self-description — "like a blockchain, but without the overhead."

> ⚠ **Fail-legible note (escrow is design, not code).** "Enforced by the event structure" is presented as analogous to the event graph's structural guarantee (no `Update`/`Delete` on the store — see [[event-graph]]). But conditional-payment resolution, dispute linkage, and condition-matching are *described*, not specified or implemented in any source read this run. Asserted, not proven.

## AI agents as market participants

The "2026 angle that makes this urgent" ([Searles-Market]): AI agents are becoming market participants in the mundane sense (booking flights, negotiating prices, running a freelance business), yet "current infrastructure assumes human buyers and human sellers" — an agent on Upwork is "technically a terms-of-service violation on most platforms." The Market Graph is claimed to handle this natively because "it doesn't distinguish between human and AI actors — it distinguishes between authority levels": an agent acts under a defined [[authority-layer]] threshold (accept jobs under a value, deliver certain types, invoice/collect) and escalates above it. The accountability claim: *"'My AI did it' is not an excuse on the Market Graph — it's a verifiable claim,"* because the chain shows what the agent agreed to and whether it stayed within bounds. This is the same authority-recording role the [[authority-layer]] plays for tasks, applied to deals.

## How it relates to the other graphs

The Market Graph is one lens among the [[thirteen-graphs]] over a single event substrate. The corpus repeatedly stitches it to its neighbours:

- It **sits on top of** [[the-work-graph|the Work Graph]]: Work records that work was done; Market records that value was exchanged for it (first-party copy L2986). "Payment and exchange — that's Layer 2."
- A **breach feeds the Justice Graph**: in the worked cross-graph example, a freelancer completes work (Work Graph), the client doesn't pay (a Market Graph **breach event**), and the Justice Graph "doesn't need to *find* the evidence… it needs to *adjudicate* it," cutting "80% of the cost and time out of dispute resolution" (first-party copy L2065, L2193-2195 — the 80% figure is the author's, uncited).
- It **strengthens the Identity Graph**: transaction history is one strand of the hash-chained record of "what you've actually done across all the other graphs" (first-party copy L2309).
- It is **buildable now** alongside Work and Social, per the corpus: "A Market Graph that uses the same infrastructure to track transactions with verifiable provenance" (first-party copy L2467) — though, again, only the Work Graph is described as actually under construction.

## The claimed end state

"The Market Graph makes trust infrastructure a public good rather than a private monopoly… What's left for the platform? Curation, community, user experience — the things that actually differentiate one marketplace from another… worth 3-5%, not 25%" ([Searles-Market]). The slogan-level summary: "Uber without the toll booth is a matching algorithm and a nice app… The platform earns what the platform is worth, not what the trust monopoly enables it to extract."

> ⚠ **Fail-legible note (normative claim).** "Trust as a public good" and the collapse of platform take-rates from ~25% to ~3-5% are the author's **economic and normative argument**, not a demonstrated outcome. No market, pilot, or measurement is cited. Carried here because the source carries it; labelled as a thesis.

## Source conflicts (stated, not resolved)

1. **Take-rate headline vs. body.** The post's subtitle says platforms charge "**25%**" to mediate trust; the body gives **ranges** (Uber 25-30%, Airbnb 14-20%, Upwork 10-20%) ([Searles-Market]). The "25%" is a round headline figure, not one of the per-platform numbers — noted so the discrepancy isn't read as a single asserted rate.
2. **Inflated-rating floor: 4.7 vs 4.8.** The compact Layer 2 statement says "Ratings are inflated (**4.7** is 'average' on Airbnb)" ([Searles-13Graphs-L2], L2131); the full post says "Airbnb reviews trend toward **4.8** stars as a floor" ([Searles-Market], L3069). Both passages make the same point (rating compression makes the system useless for distinguishing quality); the exact figure differs between them. Neither is sourced to Airbnb data.

These are *internal* inconsistencies within one author's corpus, not a conflict between independent sources. The Searles post and its first-party copy in the dark-factory `all-posts 1.md` are the **same text** — the dark-factory copy is not an independent corroboration, only a re-host plus the cross-graph references cited above.

## Sources & provenance

Compiled from `raw/searles/all-posts-1.md`:
- Post 15, *"The Market Graph"*, 2026-03-01 · [Searles-Market] · https://mattsearles2.substack.com/p/the-market-graph — the full deep dive (toll-booth economy; the three platform services with two as commodities; the four trust-layer failures; exchange primitives as events; portable reputation; escrow as event pattern; AI agents under authority; "the end of the toll booth").
- Layer 2 summary in the "Thirteen Graphs, One Infrastructure" region, L2115-2139 · [Searles-13Graphs-L2] · https://mattsearles2.substack.com/p/thirteen-graphs-one-infrastructure — the compact Layer 2 statement (primitives; what-exists; why-broken; the event-graph version).

First-party corpus: `/Transpara/transpara-ai/repos/docs/dark-factory/all-posts 1.md` — a re-host of the same Searles text (verified same wording), plus the cross-graph references used above: the "what this touches" marketplace/escrow passage (L1080), reputation/credentials (L1124-1128), the worked cross-graph dispute example (L2065, L2193-2195), Work↔Market boundary (L2986), Identity Graph strand (L2309), and "buildable now" (L2467). The dark-factory **normative** synthesis (`Dark Factory - Motive, Goal, Approach.md`) contains **no** Market Graph specification — searched this run, no hits — consistent with the Market Graph being an unbuilt Layer 2 product horizon rather than current implementation scope.

**Operational record:** none. Open Brain returned **no thoughts** for the Market Graph (searched this run), consistent with its unbuilt status.

**Conflicts stated, not resolved:** (1) take-rate headline "25%" vs. per-platform ranges; (2) inflated-rating floor 4.7 vs 4.8 across the two passages. **Asserted-but-unproven, flagged inline:** the entire mechanism (portable reputation, escrow-as-event-pattern, AI-agent authority), the take-rate numbers, the "80% dispute-cost reduction" figure, and the "trust as public good / take-rates collapse to 3-5%" thesis. `[[wikilinks]]` are forward references; targets not present in `wiki/` as of this compile include `the-work-graph` and `thirteen-graphs`.
