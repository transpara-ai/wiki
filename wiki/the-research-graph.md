---
entity: The Research Graph
org: transpara-ai
primary_placement: civilization/foundational
placements:
  - civilization/foundational
classification: internal
aliases: [Research Graph, Layer 5 Research Graph, the provenance layer, the replication fix]
tier: foundational
status: compiled
last_compiled: "2026-06-14"
sources:
  - raw/searles/all-posts-1.md  # post 18, "The Research Graph", 2026-03-01 [Searles-Research] — full deep dive: provenance crisis, event-chain research model, replication as structural property, open collaboration, mind-zero as first project
  - raw/searles/all-posts-1.md  # post 11, "Thirteen Graphs, One Infrastructure", 2026-03-01 [Searles-13Graphs] — Layer 5 compact statement (L2199-2225): primitives, what-exists, why-broken, event-graph version
confidence:
  sources: primary
  claims: grounded
  replication_crisis_figures: source-internal — "50% to 90%" range for failed replications in psychology, biomedicine, economics is the author's stated figure; underlying citations not listed in the corpus
  mind_zero_as_first_project: grounded — author's own claim about his series; not independently verifiable from this corpus
  research_graph_as_built: thin — asserted design, not a shipped product; no Open Brain operational record exists for it
---

# The Research Graph

**Layer 5 of the arc — the provenance layer.** The Research Graph is the proposed view of an [[event-graph]] in which the scientific process — hypothesis, method, data collection, analysis, result, peer review, replication — is recorded as a causally linked, hash-chained sequence of events rather than described in prose after the fact. Its central argument, stated in the subtitle of the dedicated deep-dive post, is that *"science has a replication crisis because it has a provenance crisis"* ([Searles-Research]).

It enters the arc in two passes: first as a compact statement inside the [[thirteen-graphs]] survey (**Post 11, 2026-03-01**), then as a full deep dive in **Post 18, *"The Research Graph"* (2026-03-01)** ([Searles-Research]), which is Post 17's trailing announcement: *"Next deep dive: the Research Graph — what happens when scientific knowledge is created, validated, and challenged on the event graph."*

> ⚠ **Fail-legible note (status).** The Research Graph is a design, not a deployment. The author frames the mind-zero series itself as an imperfect proto-instance ("on Substack, which is a blog, not infrastructure"), and the post ends with a commitment to migrate it to the graph once built. There is no Open Brain operational record for a Research Graph implementation. Treat every mechanism below as asserted design, not shipped fact.

## What it is a view of

The Research Graph is not new infrastructure. It is the [[event-graph]] — the same append-only, SHA-256 hash-chained, causally-linked directed acyclic graph — with **Layer 5 (Technology) primitives foregrounded**: *Tool, Technique, Invention, Method, Standard, Efficiency, Automation, Infrastructure, Discovery, Hypothesis, Experiment, Replication* ([Searles-Research], [Searles-13Graphs]).

The post distinguishes Layer 5 carefully from Layer 6: "This is the Technology layer — not technology as gadgets, but technology as the systematic process of turning questions into reliable answers." The primitives describe the scientific method's own operations — how a question becomes a hypothesis, a hypothesis becomes an experiment, an experiment becomes a result, and a result becomes knowledge that others can replicate or challenge.

## The provenance crisis thesis

The post's structural argument is that the replication crisis is misdiagnosed. The standard explanation — p-hacking, HARKing (Hypothesising After Results are Known), small sample sizes, publication bias — treats these as researcher failures. The post argues they are **structural** failures enabled by an infrastructure that lets research proceed without recording its own provenance.

The core statement ([Searles-Research]):

> "The deeper issue: you can't verify what a researcher actually did. A published paper describes a method in prose… But between the description and the reality, there are hundreds of decisions that the paper doesn't record."

The paper is "testimony, not evidence" — a narrative written after the fact by the party with the strongest incentive to present results favourably. The post claims that if every decision in the research process were recorded as an immutable event before results are seen, "the most common forms of research fraud and self-deception would be architecturally impossible. Not prevented by rules. Prevented by structure." This is the same move the [[event-graph]] makes at the level of accountability generally: structural enforcement over policy enforcement.

> ⚠ **Fail-legible note (replication figures).** The post states that "somewhere between 50% and 90% of published findings in psychology, biomedicine, and economics don't replicate." This is the author's figure, cited without a primary source in the corpus. The general existence and severity of the replication crisis is widely documented; the specific range is the author's characterisation.

## The publishing trap

The post draws a parallel with the rent-extraction diagnosis common to the other institutional-tier graphs. Academic publishing is characterised as a system where publishers achieve 30–40% profit margins (the post names Elsevier, Springer, and Wiley; "higher than Apple, higher than Google") for formatting and distribution that are "essentially free in 2026." The perverse incentive stack:

- **Publishers** profit from gatekeeping access; open distribution eliminates their model.
- **Journals** profit from prestige; selectivity is the moat.
- **Researchers** profit from publication count and journal prestige; careers depend on *where* you publish, not on whether findings replicate. "A novel finding in Nature advances your career. A replication study in a minor journal does nothing."
- **Nobody** profits from making research reproducible, data accessible, or methods verifiable.

The open access movement's preprint servers (arXiv, bioRxiv) are acknowledged as progress, but the structural incentive toward novelty over truth remains.

## The event graph version

The post gives a concrete event-chain model for the research process:

**Hypothesis event.** Before data collection begins, the hypothesis is registered as an immutable, timestamped, hash-chained event. Pre-registration becomes a structural property of the graph, not a voluntary practice — you cannot change the hypothesis after seeing results because the hypothesis event precedes the data events on the chain.

**Method event.** The analysis plan is registered before data collection: which tests will be run, what the outcome variables are, what would count as confirmation or disconfirmation.

**Data collection events.** Every participant recruited, every exclusion (with a reason linked to a pre-specified criterion), every data point collected is an event. The dataset is a chain with complete provenance, not a file on a hard drive.

**Analysis events.** Every statistical test run is an event — not just the test reported, but every test. "If the researcher ran twelve tests and reported the one that was significant, the other eleven are on the chain too. p-hacking becomes visible because the full analysis history is transparent."

**Result event.** Findings linked to analysis events, linked to data events, linked to method events, linked to the hypothesis event: the complete causal chain from question to answer, verifiable by anyone.

**Peer review events.** Reviewer comments, author responses, and editorial decisions are all events, linked causally. Anonymous review (the post explicitly endorses its legitimacy) coexists with transparency of content. Over time, review quality becomes a visible track record.

### Replication as structural property

The post distinguishes the current replication process — *"read the prose description of the method, try to reproduce what you think they did"* — from replication on the Research Graph: *"take the method event chain, apply it to new data, and compare results."* The replicator can follow the exact chain and diverge only where they choose to. Failed replications become unambiguous about *where* the chains diverged, separating genuine failures to replicate from method differences that were invisible in prose.

## Open collaborative research

The post argues the Research Graph changes the incentive for data sharing. Under the current system, sharing data before publication risks being scooped, while the credit mechanism (citation norms) is weak. On the Research Graph, sharing data creates a permanent, causal link between the contributor and everything built on that contribution: "Sharing becomes advantageous because the attribution is guaranteed by architecture, not by norms."

The cross-institutional collaboration scenario is stated: a researcher in Tokyo contributes data, one in Nairobi contributes analysis, one in São Paulo contributes theoretical framing — each is a verifiable event chain; the causal contribution of each is precisely recorded regardless of author-order conventions. "There isn't a paper. There's a chain."

## What this costs (infrastructure)

The post notes that the Research Graph sits on the same [[event-graph]] infrastructure as the other layers. If Layers 1–4 are built, Layer 5 adds new event types: Hypothesis, Method, DataCollection, Analysis, Result, Review, Replication. The hash-chaining, causal linking, and authority model are already there.

The tooling named: pre-registration forms (creating hypothesis events); adapters for survey tools, lab instruments, and data pipelines; analysis-logging integrations with R, Python, and Jupyter notebooks; review submission and tracking. "None of this requires fundamental new technology. Pre-registration platforms exist (OSF, AsPredicted). Data repositories exist (Zenodo, Dryar). Analysis logging tools exist (various reproducibility packages). The Research Graph unifies them on a single chain with verifiable provenance across the entire pipeline."

## Mind-zero as the first project

The post explicitly claims the mind-zero series itself as the Research Graph's first project, "whether we intended it or not" ([Searles-Research]). The derivation is documented; the autonomous run is described in Post 1; the Claude session is described in Post 2; the convergence claim is stated and limitations are acknowledged; the formal analysis in Post 12 identified specific weaknesses. It is not yet on a hash-chained graph ("on Substack, which is a blog, not infrastructure"), but "the method is visible. The reasoning is traceable. The claims are falsifiable." The commitment: "when the Research Graph is built, this project will be the first thing migrated onto it."

## Relationship to the rest of the arc

- **Substrate:** the Research Graph is a view over [[event-graph]] — the same append-only, hash-chained store the other graphs use. The event types are new; the infrastructure is shared.
- **Layer 6 sequel:** the Research Graph produces findings; the [[the-knowledge-graph-searles|Knowledge Graph]] (Layer 6) tracks what happens to those findings after they enter public discourse. The post ends: *"Next deep dive: the Knowledge Graph — what happens when claims, sources, and truth itself move onto the event graph."*
- **Layer 4 predecessor:** the Research Graph sits on top of the Justice Graph (Layer 4) in the bootstrapping sequence — "Layer 5 rides on Layers 1-4." Disputes about research findings can, in principle, draw on the causal chain of events already on the graph.
- **Thirteen-graph frame:** the Research Graph is Layer 5 of the [[thirteen-graphs]] — the institutional tier, alongside Justice (Layer 4) and Knowledge (Layer 6). It is one of the thirteen views over one substrate, not a separate product.
- **Structural enforcement theme:** the same principle the [[event-graph]] applies to accountability (append-only, no `Update()`, no `Delete()`) and the [[authority-layer]] applies to permissions is here applied to epistemics: provenance enforced by structure, not by norms.

> ⚠ **Fail-legible note (building sequence).** The thirteen-graphs post is explicit that only the Work Graph is described as being built ("this week"). The Research Graph is Layer 5; the post's own bootstrapping logic has Layer 5 riding on Layers 1–4. The dark-factory docs classify the full thirteen-graph set as "product horizon and analogy set, not current implementation scope." The Research Graph's build date is unknown from this corpus.

## Sources & provenance

Compiled from `raw/searles/all-posts-1.md`:
- Post 18, *"The Research Graph"*, 2026-03-01 · [Searles-Research] · https://mattsearles2.substack.com/p/the-research-graph — the full deep dive: provenance crisis thesis, publishing trap analysis, event-chain research model (hypothesis/method/data/analysis/result events), structural replication, open collaboration, mind-zero as first project, infrastructure cost. Approximately lines 3534–3681.
- Post 11, *"Thirteen Graphs, One Infrastructure"*, 2026-03-01 · [Searles-13Graphs] · https://mattsearles2.substack.com/p/thirteen-graphs-one-infrastructure — Layer 5 compact statement: primitives, "what exists," "why it's broken," "event graph version" (L2199-2225 approximately). Overview context and "views, not products" thesis.

**Conflicts stated, not resolved:** (1) The replication-crisis figures (50–90% range) are the author's, uncited to primary sources in the corpus. (2) The Research Graph is asserted design, not deployment; no operational record exists in Open Brain. (3) The "trivial technology" framing inherited from the thirteen-graphs post is complicated by the operational concurrency cost documented in [[event-graph]] (see that article's "fail-legible note on trivial technology"). (4) Repo identity conflicts (mind-zero-five vs. transpara-ai/eventgraph vs. lovyou-ai/eventgraph) from [[event-graph]] apply here equally. `[[wikilinks]]` are forward references; [[the-knowledge-graph-searles]] is the direct sequel compiled in the same session.
