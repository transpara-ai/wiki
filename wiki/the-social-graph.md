---
entity: The Social Graph
org: transpara-ai
primary_placement: civilization/concept
placements:
  - civilization/concept
classification: internal
aliases: [social graph, the social graph, Layer 3, the society layer, the relationship layer]
tier: concept
status: compiled
last_compiled: 2026-06-13
sources:
  - raw/searles/all-posts-1.md  # "The Social Graph", 2026-03-01 [Searles-Social] — Layer 3 primitives, "most successful misalignment", event-graph version, free-rider, where-it-touches, the hard question
  - raw/searles/all-posts-1.md  # "The Justice Graph", 2026-03-01 [Searles-Justice] — lead only; cited for the Layer 4 escalation cross-link
  - Dark Factory - Motive, Goal, Approach.md  # treats Social as one of the thirteen product graphs — "product horizon and analogy set, not current implementation scope"
confidence:
  layer3_framework: high (primary source — the post enumerates the Layer 3 primitives and maps each critique onto one)
  misalignment_diagnosis: source-grounded as argument; the post itself claims the engagement-vs-wellbeing inverse correlation is "empirically demonstrated across multiple platforms in multiple studies" but cites no specific study — treated here as the author's asserted empirical claim, not independently verified
  event_graph_version: asserted design, not shipped — no Social Graph implementation is described anywhere in the sources read; the post explicitly contrasts itself with Mastodon/Bluesky/Nostr as not-yet-built
  implementation_scope: contested-by-framing — the dark-factory docs scope all thirteen product graphs (Social included) as "product horizon and analogy set, not current implementation scope"; only the Work Graph is ever described as being built
---

# The Social Graph

**Layer 3 of the thirteen-graph stack — the relationship-and-governance lens.** The Social Graph is the proposed view of the [[event-graph]] that activates when coordination moves from two parties exchanging value to three or more people forming groups, setting norms, and governing themselves. It appears as a standalone essay, *"The Social Graph"* (**2026-03-01**, subtitle *"You don't own your friends list."*), in the Searles post series, following [[the-work-graph|the Work Graph]] (Layer 1) and [[the-market-graph|the Market Graph]] (Layer 2) and announced at the end of the Work Graph piece as *"what happens when governance, consent, and community norms move onto the event graph."* Like every graph in the series it is framed as **a view, not a product**: "same event graph, same infrastructure, one more lens on the same data."

The one-line thesis: a social network is not a tool communities use but a government communities live under — one nobody voted for, nobody can vote out, and that has no obligation to represent its members. The fix is structural rather than regulatory: make the relationship graph user-owned and portable, make the feed a query instead of a mystery, let each community set and enforce its own norms as events, and make consent an architectural property rather than a click-through.

> ⚠ **Fail-legible note (status of the whole article).** Everything below the diagnosis is **asserted design, not shipped software.** No Social Graph implementation is described in any source read this run; the post explicitly positions itself against existing decentralised-social projects (Mastodon, Bluesky, Nostr) as the thing they have *not* built. The [[dark-factory]] first-party docs reinforce this: the thirteen product graphs, Social included, are "product horizon and analogy set, **not current implementation scope**," with only the Work Graph ever described as being built.

## The Layer 3 primitives

The post locates the Social Graph at **Layer 3 (Society)** and lists its twelve primitives: **Membership, Role, Norm, Status, Consent, Due Process, Legitimacy, Sanction, Commons, Public Good, Free Rider, Social Contract.** The argument is that these are not abstract political-science terms but the questions *every* group of three or more humans must negotiate — "a nation-state, a book club, or a Discord server":

- Who's in the group? — **Membership**
- What may they do? — **Role**
- What behaviour is expected? — **Norm**
- How are decisions made? — **Legitimacy, Due Process**
- What happens when rules break? — **Sanction**
- What do members get by belonging? — **Commons, Public Good**
- What do freeloaders cost? — **Free Rider**
- What's the implicit deal between individual and group? — **Social Contract**

The post's framing claim: every social platform is already an answer to these questions — "the problem is that the platform answers them unilaterally, opaquely, and in its own interest." These primitives are the Layer 3 cluster of the larger [[primitive-basis|primitive basis]] (the same lineage as [[the-20-primitives]] → [[fourteen-layers]] → [[thirteen-graphs]]).

## "The most successful misalignment in history"

The post's central diagnosis inverts the usual "social media is broken" critique: social networks are **not** broken — "they work exactly as designed." The misalignment is between what they are designed to do (maximise engagement, ad impressions, content interactions) and what users believe they are for (connection). The user's social need is the raw material; the product is the user's attention, sold to advertisers — "stated openly in every earnings call." The phrase "the most successful misalignment in history" names this: a working optimiser pointed at the wrong objective, at planetary scale.

The post maps each failure onto a Layer 3 primitive:

- **Membership → captivity.** You can join but can't really leave without losing your social infrastructure. "Membership that you can't leave… isn't membership. It's captivity with a logout button."
- **Norms → imposed, opaque, mutable.** Community Guidelines are *the platform's* norms applied to every community at once — "a knitting group and a political debate forum operate under the same rules" — unchosen, unmodifiable, enforced opaquely, and rewritten unilaterally whenever advertiser or political pressure shifts. "There was a Terms of Service, which is a different thing" from a Social Contract.
- **Status → algorithmic, not communal.** Who is seen, amplified, or buried is an engagement-optimised algorithmic decision, not the community's. A nuanced post "dies in silence" while an outrageous take is rewarded with visibility, selecting over time for engagement-maximising members — "the community didn't choose this selection pressure. The algorithm imposed it."
- **Consent → coercion in consent's clothing.** A Terms of Service is not consent: nobody reads it, nobody understands the implications, and declining means losing access. "'Agree or lose your friends' is not consent. It's coercion wearing the language of consent."

The post then states what it calls the perverse incentive plainly: **engagement-maximisation and user wellbeing are inversely correlated** — "a satisfied user closes the app; an anxious user keeps scrolling… The platform profits from your dissatisfaction."

> ⚠ **Fail-legible note (the "empirically demonstrated" claim).** The post asserts this inverse correlation "has been empirically demonstrated across multiple platforms in multiple studies" but **names no study, dataset, or citation.** Carried here because the source carries it; treated as the author's asserted empirical claim, **not** independently verified this run. The structural argument (the business model openly optimises engagement) is grounded in the post's own reasoning; the strength of the *wellbeing-harm* evidence base is **thin as cited** and should not be relayed as settled fact.

## Why it is a governance problem, not a tech problem

The post argues the conventional critique (mental health, misinformation, privacy) describes **symptoms**; the structural problem is that platforms have *captured the Layer 3 primitives* and operate them in the platform's interest rather than the community's. Hence: "Facebook isn't a tool that communities use. Facebook is a government that communities live under." The asserted analogy — "two billion people live under Facebook's governance," none of whom consented meaningfully, have representation, or can verify how decisions are made — is offered as "illegitimate governance… we just don't call it that because it's a company, not a country."

> ⚠ **Fail-legible note.** The "two billion people" figure and the "by any standard of political philosophy this is illegitimate" verdict are **rhetorical/asserted**, not sourced to a count or a named standard in the post. The *mechanism* (unilateral, unappealable, unrepresentative rule-setting) is argued from the primitives; the headline number and the philosophy verdict are the author's framing.

## The event-graph version (the proposed fix)

The post's constructive half re-derives a social network on top of the [[event-graph]], built by extending it with **Layer 3 event types** — connection events, group-membership events, norm-proposal and norm-adoption events, moderation events, role-assignment events — each "hash-chained, causally linked, and owned by the participants." Four shifts:

1. **Your graph is yours.** Your connections, interactions, and relationships are an event graph *you* own; the platform only provides the interface. If you dislike the platform you take your graph elsewhere — connections, interaction history, and group memberships travel with you. "No lock-in. No data hostage." This inverts the power dynamic: the platform "has to earn your continued use… not by making it impossible to leave."
2. **Communities set their own norms.** A community's norms are *events on the graph* — proposed, discussed, adopted (or not), enforced — all by the community, not the platform. Different communities carry different norms because they are different. Moderators can hold real, strict power, but "the power is granted by the community, visible to the community, and revocable by the community… **Due Process isn't a feature request. It's an architectural property.**"
3. **The feed is a query, not a mystery.** Instead of an opaque algorithm whose logic you cannot see or change, the feed is a *query against your own event graph* with visible, editable parameters: chronological → query by timestamp; close connections only → query by relationship weight; active communities → query by membership and activity. **The key shift:** "on current platforms, the algorithm serves the platform's interests and the user adapts. On the Social Graph, the query serves the user's interests and the platform adapts." (This is the same relationship-weight-as-parameter idea that [[edge-weights-as-personality]] explores elsewhere in the corpus.)
4. **Consent is structural, not performative.** When you post, the event specifies its visibility (these people, these communities, this access level). Access is itself an event — viewing your content creates an access event on the chain — so "you can see who's seen what… not because the system surveils them, but because access is an event like any other, and you own the events about your content."

This re-uses, at Layer 3, the foundational move of the [[event-graph]] and [[authority-layer]]: accountability and consent made **structural** (encoded in what the data model permits) rather than **voluntary** (promised by policy). It is the social-coordination instance of the same fail-closed logic [[dark-factory]] generalises into [[gates]].

## The free-rider inversion

Applying the **Free Rider** primitive, the post makes a pointed move: on current platforms "the biggest free rider is the platform itself" — it consumes the social graph (the commons) and extracts advertising value without sharing it with the users who created it. On the Social Graph, because contribution and consumption are *both events*, free riding becomes **visible** — "the same transparency that exists in any small group where everyone can see what everyone else is doing," extended to groups too large for direct observation. The point is explicitly *not* that free riding must be punished: communities can ignore lurkers, require minimum participation, or grant Roles by contribution — the gain is that extraction is no longer invisible.

## Where it touches the other graphs

The post uses the Social Graph to illustrate the "views, not products" principle — the same events seen through different primitive clusters ([[thirteen-graphs]]):

- **[[the-work-graph|Work Graph]] (Layer 1):** a team is a social group — Social governs *who's on the team, roles, and decision-making*; Work governs *what the team does*. Same event graph, different primitives active.
- **[[the-market-graph|Market Graph]] (Layer 2):** a marketplace is a social group — its norms (what may be sold, how disputes are handled, what gets you sanctioned) are Social primitives; the transactions are Market primitives. "You need both."
- **[[the-justice-graph|Justice Graph]] (Layer 4):** when a community's own mechanisms can't resolve a norm violation, the dispute escalates — the *evidence* lives on the Social Graph chain, the *adjudication* happens on the Justice Graph. (The Justice Graph post, also 2026-03-01, opens on exactly this: "the evidence is already there.")
- **[[the-ethics-graph|Ethics Graph]] (Layer 7):** monitors the Social Graph from outside for patterns a community can't see from within — harassment campaigns, exclusion patterns, power abuse.

A single Discord moderation dispute is "simultaneously a Social Graph event (norm violation), a potential Justice Graph event (if it escalates), and a potential Ethics Graph event (if the moderation pattern constitutes systematic harm). Same events, different lenses."

## What distinguishes it from existing decentralised social

The post pre-empts the obvious objection — decentralised social is "a category full of projects that promised revolution and delivered nothing" — and names the distinction as the **substrate**, not the vision:

- **Mastodon** (federated servers): the graph still lives on a server someone else runs; "the lock-in moved from one company to one admin."
- **Bluesky** (AT Protocol): closer — portable identity, data that follows you — but "the governance primitives aren't native… governance is still bolted on, not built in."
- **The Social Graph's claim:** the governance primitives (Membership, Norm, Role, Consent, Due Process, Sanction) are *native event types in the graph*, not features layered on top — "community governance isn't an add-on. It's what the graph does."

> ⚠ **Fail-legible note (comparison + "native" claim).** This is the post's **own argument**, written by the project proposing the alternative; the head-to-head with Mastodon/Bluesky/Nostr is asserted, not independently benchmarked. The "governance primitives are native event types" property is a **design claim about software that, per the sources read, does not yet exist.** Relay as the project's thesis, not as a demonstrated capability.

## The hard question (the source's own counter-argument)

To its credit the post raises the strongest objection itself: **self-governance is not automatically good governance** — some communities will adopt exclusionary norms, become echo chambers, or harbour abuse. Its answer is *not* "self-governance solves everything" but a narrower, structural claim: **bad self-governance that is transparent and escapable is structurally better than bad platform governance that is opaque and captive.** When a community governs badly on the Social Graph, the norms, the enforcement pattern, and the exclusion are all *on the chain* — visible to other communities, researchers, the Ethics Graph, and to members who can leave with their portable graph intact. The closing concession is the honest one and worth preserving verbatim: *"The event graph doesn't guarantee good governance. It guarantees that governance is visible, which is the precondition for governance being accountable."*

## Sources & provenance

Compiled from `raw/searles/all-posts-1.md`:
- *"The Social Graph"*, 2026-03-01 · [Searles-Social] · https://mattsearles2.substack.com/p/the-social-graph — the Layer 3 primitives; "the most successful misalignment in history"; the Membership/Norms/Status/Consent critique; the engagement-vs-wellbeing inverse-correlation claim; the "Facebook is a government" framing; the four event-graph shifts (your graph is yours / communities set norms / feed-as-query / structural consent); the free-rider inversion; the Work/Market/Justice/Ethics cross-links; the Mastodon/Bluesky/Nostr comparison; and "the hard question."
- *"The Justice Graph"*, 2026-03-01 · [Searles-Justice] · https://mattsearles2.substack.com/p/the-justice-graph — lead only, cited for the Layer 4 escalation ("the evidence is already there").

First-party synthesis: `Dark Factory - Motive, Goal, Approach.md` — lists the Social Graph among the thirteen product graphs treated as "views over one event graph," scoped as **"product horizon and analogy set, not current implementation scope"** (Citation Handle `Searles-13Graphs`). Open Brain returned **no** thoughts on the social graph, Layer 3, or portable social data when searched this run — there is no operational corroboration, consistent with this being design, not deployed software.

**Post-number note (minor):** the Work Graph post (Post 15) announces "Next deep dive: the Social Graph," but the Social Graph essay's own footer labels itself "Post 16," with the Market Graph named as its "Previous." Both are recorded here as written; the discrepancy does not affect content.

**Confidence summary.** The Layer 3 *framework* and the *diagnosis* are high-confidence as the source's argument. The *engagement-harms-wellbeing* evidence base is **thin as cited** (asserted "multiple studies," none named). The entire *event-graph version*, the *"native governance primitives"* claim, and the *comparison to existing decentralised social* are **asserted design about software not described as built** in any source read — and the dark-factory docs independently scope all thirteen product graphs (Social included) as horizon, not implementation. `[[wikilinks]]` are forward references; several targets ([[the-work-graph]], [[the-market-graph]], [[the-justice-graph]], [[the-ethics-graph]], [[thirteen-graphs]], [[primitive-basis]]) are not yet compiled.
