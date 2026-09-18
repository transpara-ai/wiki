---
doc_id: "TAI-WIKI-COMPARISON"
title: "Which wiki design wins? Karpathy vs Transpara vs Cortex"
doc_type: "analysis"
version: "0.1.1"
status: "draft"
created: "2026-09-18"
updated: "2026-09-18"
owner: "Transpara"
steward: "Codex"
author: "Codex"
reviewer: "Pending human review"
project: "wiki"
repo: "transpara-ai/wiki"
classification: "company-internal"
supersedes: []
canonical: false
version_history: "First controlled revision; prior unversioned content remains in Git history"
---

# Which wiki design wins? Karpathy vs Transpara vs Cortex

**Decision date: 2026-09-18. Overall winner: Cortex, narrowly, at 6.80/10.**
Karpathy scores 6.76 and Transpara 6.50 under the declared balanced weights.
That is a decision under stated preferences, not a statistically established
quality difference. Karpathy wins when synthesis dominates; Transpara wins when
enterprise publication dominates. The overall recommendation is especially
sensitive to how much credit a pattern receives for intended behavior.

## Reading map and evidence boundary

This document owns the comparative judgments, criteria, scoring, and decision.
Architecture descriptions, implementation evidence, limits, cost models,
and timing swim lanes belong to the three standalone dossiers:

| System | Complete dossier | Architecture | Ingest timing | Query timing |
| --- | --- | --- | --- | --- |
| Original Karpathy LLM Wiki | [Karpathy](karpathy.md) | [Explainer](karpathy.md#architecture) | [Swim lanes](karpathy.md#ingest-swim-lanes-and-timing-model) | [Swim lanes](karpathy.md#query-swim-lanes-and-timing-model) |
| Transpara Knowledge Hub | [Transpara](transpara.md) | [Explainer](transpara.md#architecture) | [Swim lanes](transpara.md#ingest-swim-lanes-and-timing-model) | [Swim lanes](transpara.md#query-swim-lanes-and-timing-model) |
| Obelyth Cortex | [Cortex](cortex.md) | [Explainer](cortex.md#architecture) | [Swim lanes](cortex.md#ingest-swim-lanes-and-timing-model) | [Swim lanes](cortex.md#query-swim-lanes-and-timing-model) |

The subsequent Hub implementation has a separate [CFAR ingestion/research timing model](../../compile/DISCOVERY.md#cfar-ingestion-and-research-swim-lanes),
including reviewer capabilities, challenge/repair and human publication. The KT
scores here remain the pinned baseline comparison; they do not claim validation
of the new workflow or its pilot targets.

Each dossier pins its primary sources and separates specified, implemented,
optional, and inferred behavior. The assessment compares an original pattern
with two concrete implementations. It credits the pattern's semantic goals
without pretending that those goals are tested runtime guarantees. Conversely,
implemented controls earn credit without proving factual accuracy or live-host
reliability. Roadmaps and proposed hybrids earn no current-feature points.

No common performance or accuracy benchmark was run. Timing diagrams are
explicit illustrative schedules; their totals are not inputs to the score.
Code timeouts are not measured latency, and citation verification is not truth
verification. All scores and rankings below are this review's judgments.

## Decision objective

Choose the strongest existing **wiki architecture** for durable, inspectable,
source-traceable knowledge that remains useful across questions and revisions,
with a reasonable path to team use and manageable operating cost.

The baseline assumes a small knowledge operation, an initially moderate corpus,
repeated questions, human ownership of curation, and no mandatory enterprise
identity/publication requirement. It evaluates architecture rather than a
procurement decision or a mandate to replace the existing Hub. If an enforced
multi-audience company publication boundary is mandatory, use the enterprise
scenario below and apply that requirement as a gate.

“Best” must reward synthesis, but it cannot reward synthesis so exclusively
that an unenforced instruction file automatically defeats tested persistence,
evidence, retrieval, and failure behavior. Equally, feature count cannot make
a sophisticated note server an automatic winner over a better learning loop.

## Philosophical axes: where each design places its bets

The cells below are comparative interpretations. Follow their dossier links
for the mechanics and evidence; this table does not duplicate the architectures.

| Axis and tension | Karpathy's bet | Transpara's bet | Cortex's bet | Comparative judgment |
| --- | --- | --- | --- | --- |
| Ingestion: understanding vs registration | [Semantic integration](karpathy.md#lifecycle-and-philosophical-axes) | [Curated separation of capture and synthesis](transpara.md#lifecycle-and-philosophical-axes) | [Explicit memory mutation](cortex.md#lifecycle-and-philosophical-axes) | Karpathy sets the highest knowledge-completion bar; neither other default path reaches it. |
| Storage: evidence vs interpretation vs working state | [Simple conceptual separation](karpathy.md#architecture) | [Publication-oriented canonical content](transpara.md#architecture) | [Durable memory plus operational state](cortex.md#architecture) | Karpathy is easiest to understand; Cortex has the most consequential backup distinction. |
| Indexing: semantic routing vs lexical precision | [Agent navigation](karpathy.md#efficiency-and-scaling) | [Reader navigation and model selection](transpara.md#efficiency-and-scaling) | [Inspectable bounded retrieval](cortex.md#efficiency-and-scaling) | Cortex offers the clearest retrieval accounting; no candidate establishes best recall. |
| LLM role: compiler vs service vs client | [Maintainer at the center](karpathy.md#philosophy-and-architectural-contract) | [Explicit curation and answering](transpara.md#philosophy-and-architectural-contract) | [Reader with client-owned authoring](cortex.md#philosophy-and-architectural-contract) | Karpathy most directly attacks wiki abandonment; the others constrain where inference runs. |
| Efficiency: amortize reasoning vs avoid unnecessary inference | [Compile reusable conclusions](karpathy.md#efficiency-and-scaling) | [Serve curated artifacts cheaply](transpara.md#efficiency-and-scaling) | [Bound and reuse retrieval work](cortex.md#efficiency-and-scaling) | Repeated research favors Karpathy; repeated identical questions favor Cortex; plain reading favors Transpara. |
| Performance: semantic completion vs response latency | [Agent/human critical path](karpathy.md#ingest-swim-lanes-and-timing-model) | [Publication and Ask have different bottlenecks](transpara.md#query-swim-lanes-and-timing-model) | [Deadline-aware reader pipeline](cortex.md#query-swim-lanes-and-timing-model) | There is no honest single “fastest” claim across these different completion events. |
| Trust: instruction vs publication authority vs evidence check | [Human and workflow discipline](karpathy.md#failure-modes-and-recovery) | [Audience and release boundaries](transpara.md#failure-modes-and-recovery) | [Commit-specific quotation evidence](cortex.md#failure-modes-and-recovery) | Transpara leads publication control; Cortex leads implemented quotation auditability. |
| Maintenance: semantic care vs structural care | [Semantic repair contract](karpathy.md#adversarial-assessment) | [Explicit curation backlog](transpara.md#adversarial-assessment) | [Memory and retrieval repair](cortex.md#adversarial-assessment) | Karpathy asks the right semantic question; the implementations make narrower guarantees observable. |

## Antagonistic comparison: the case against each candidate

### Karpathy must defend “the agent will maintain it”

Its strongest claim is also its least enforced: persistent synthesis should
improve as sources and questions accumulate. Against Cortex, it lacks a concrete
server contract proving which evidence was read and quoted. Against Transpara,
it lacks an implemented publication boundary. If “the model follows the schema”
is the only defense against inconsistent edits, the design has delegated its
hardest reliability problem rather than solved it.

Karpathy's counterattack is valid: neither good retrieval nor a governed website
constitutes learning. The [semantic workflow](karpathy.md#philosophy-and-architectural-contract)
is its real advantage. It receives the highest synthesis score and pays for
its unspecified operational controls elsewhere.

### Transpara must defend the gap between a healthy build and current knowledge

The Hub wins the company-publication argument but loses the default-compounding
argument. Against Karpathy, it explicitly leaves semantic updates to a separate
curation step. Against Cortex, Ask supplies weaker quotation checking and less
answer reuse. A polished, well-classified article can be stale; successful
rendering makes that article available rather than making it correct.

Transpara's counterattack is also valid: an enterprise needs control of what
is published and to whom. That is a stronger basis for team knowledge than
the other systems' baseline access models. The [implementation distinctions](transpara.md#three-distinctions-that-must-survive-any-comparison)
prevent us from awarding autonomous-synthesis points just because a hook exists.

### Cortex must defend the difference between verified memory and a good wiki

Cortex beats both on implemented quotation auditability and cross-client tool
access. But a correct quote from an unsynthesized note is still unsynthesized
memory. Against Karpathy, it externalizes the most important semantic workflow.
Against Transpara, its owner/trusted/guest model does not replace enterprise
publication governance. Its default short-answer contract also underserves
multi-source analytical essays.

Cortex's counterattack: disciplined persistence, bounded context, visible
omissions, and recoverable failure behavior matter even when a model is clever.
Those are concrete architectural merits. Its [retrieval limits](cortex.md#retrieval-details-that-affect-evaluation)
are why its retrieval score is 8 rather than a claim of perfect recall.

## KT decision method and mandatory requirements

This is a **Kepner–Tregoe-style decision analysis**: state the objective,
screen mandatory requirements, weight desirable outcomes, rate alternatives,
then examine adverse consequences and sensitivity. It is an adapted
architecture assessment, not a claim of formal KT certification.
The method follows the distinction between mandatory objectives, weighted
preferences, and adverse consequences described by
[Kepner–Tregoe](https://kepner-tregoe.com/blogs/improve-hiring-success-with-kepner-tregoe-decision-analysis/).

Mandatory requirements are binary and earn no points. “Eligible by contract”
means the original pattern provides a design basis; it does not mean runtime
acceptance testing passed. A mandatory implemented-control requirement would
exclude an unspecified pattern before scoring.

| MUST for this baseline | Karpathy | Transpara | Cortex |
| --- | --- | --- | --- |
| Durable, human-readable content with an exit path | Eligible by contract | Eligible in inspected code | Eligible in inspected code |
| Content can be revised and its history inspected | Eligible with specified Git workflow | Eligible with committed content/history | Eligible with Git-backed note mutations |
| Reader can inspect supporting material | Eligible by cited-source workflow | Eligible by article/source provenance, subject to profile | Eligible by source/commit/quote tooling, subject to access |
| A human can inspect and correct the knowledge | Eligible by workflow | Eligible through authoring/curation | Eligible through trusted note operations |

These gates assess architectural eligibility only. Original-source retention,
quote entailment, and complete semantic freshness are not magically certified
by passing them. Evidence resides in each dossier's lifecycle and failure
sections. All three remain eligible under this baseline.

## Weighted KT analysis

Weights total **100**. Scores range from **0** (absent or contrary to the
objective), through **5** (usable but partial/manual or carrying a major gap),
to **10** (strongest fit with few architectural qualifications for that
criterion). Intermediate scores express comparative judgment; they are not
measured percentages. A pattern can score well for a well-defined workflow
and poorly for its lack of implemented controls.

`Score (0–10) = sum(weight * score) / 100`.
The maximum unnormalized total is 1,000. A one-point change on a criterion
with weight 20 changes the final score by 0.20. Decimal precision is arithmetic,
not evidence precision.

| ID | WANT / assessment boundary | Weight | Karpathy | Transpara | Cortex | Why the scores differ |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| W1 | Compounding synthesis: ingest integration, semantic lint, reusable inquiry | 20 | 9 | 4 | 4 | [K](karpathy.md#lifecycle-and-philosophical-axes) specifies the complete loop; [T](transpara.md#lifecycle-and-philosophical-axes) and [C](cortex.md#lifecycle-and-philosophical-axes) need separate semantic authoring. K loses one point for underspecified execution. |
| W2 | Evidence auditability: provenance and answer support inspection | 13 | 5 | 7 | 9 | [C](cortex.md#retrieval-details-that-affect-evaluation) checks source quotations at a commit; [T](transpara.md#failure-modes-and-recovery) checks article membership and provenance; [K](karpathy.md#failure-modes-and-recovery) relies on workflow. C still cannot prove truth or raw-source preservation. |
| W3 | Team governance: audience, stewardship and publication controls | 12 | 3 | 9 | 6 | [T](transpara.md#philosophy-and-architectural-contract) has the strongest publication model; [C](cortex.md#lifecycle-and-philosophical-axes) separates trust classes; [K](karpathy.md#failure-modes-and-recovery) leaves enforcement open. |
| W4 | Retrieval design: useful context, inspectability and bounded selection | 10 | 7 | 7 | 8 | [C](cortex.md#retrieval-details-that-affect-evaluation) exposes omissions and ranks bodies; [K](karpathy.md#efficiency-and-scaling) permits flexible agent search; [T](transpara.md#efficiency-and-scaling) risks summary-routing misses. None has comparative recall evidence. |
| W5 | Operating efficiency: recurring work and infrastructure burden | 10 | 9 | 6 | 6 | [K](karpathy.md#efficiency-and-scaling) has the smallest required stack, though model/review spend persists; [T](transpara.md#efficiency-and-scaling) and [C](cortex.md#efficiency-and-scaling) have more services and operational state. No dollar estimates are assumed. |
| W6 | Portability and independent ownership of content | 8 | 10 | 8 | 8 | [K](karpathy.md#architecture) has minimal content machinery; [T](transpara.md#architecture) carries schema/host inputs; [C](cortex.md#architecture) needs separate database backup for full state. |
| W7 | Performance architecture: distribution, inference avoidance, explicit bounds | 7 | 6 | 8 | 8 | [T](transpara.md#efficiency-and-scaling) leads static reading; [C](cortex.md#efficiency-and-scaling) leads bounded/reused answers; [K](karpathy.md#query-swim-lanes-and-timing-model) leaves runtime bounds unspecified. This is not a latency ranking. |
| W8 | Maintaining correctness: correction workflow and visible maintenance debt | 6 | 7 | 5 | 7 | [K](karpathy.md#failure-modes-and-recovery) targets semantic repair but relies on discipline; [C](cortex.md#failure-modes-and-recovery) supplies precise edits and visible retrieval state; [T](transpara.md#failure-modes-and-recovery) has a weaker semantic-freshness signal. |
| W9 | Failure recovery and consistency behavior | 5 | 5 | 7 | 8 | [C](cortex.md#failure-modes-and-recovery) handles cache/mirror/deadline failures explicitly; [T](transpara.md#failure-modes-and-recovery) preserves published artifacts; [K](karpathy.md#failure-modes-and-recovery) leaves multi-file recovery to the implementer. |
| W10 | Adoption effort: first useful deployment and recurring user burden | 4 | 7 | 6 | 6 | [K](karpathy.md#adversarial-assessment) starts simply but needs curation discipline; [T](transpara.md#adversarial-assessment) and [C](cortex.md#adversarial-assessment) have heavier setup. No usability study was run. |
| W11 | Interoperability: clients and explicit machine interface | 3 | 4 | 6 | 9 | [C](cortex.md#architecture) has native multi-client MCP; [T](transpara.md#architecture) has authoring/Ask interfaces; [K](karpathy.md#architecture) leaves tools optional. |
| W12 | Operational observability | 2 | 3 | 7 | 9 | [C](cortex.md#architecture) emphasizes inspectable operations and retrieval; [T](transpara.md#lifecycle-and-philosophical-axes) exposes build/source state; [K](karpathy.md#lifecycle-and-philosophical-axes) specifies a human-readable log. |
| | **Total weight / weighted points** | **100** | **676** | **650** | **680** | |
| | **Normalized score / rank** | | **6.76 / 2nd** | **6.50 / 3rd** | **6.80 / 1st** | **Cortex wins by 0.04 over Karpathy.** |

W1 evaluates creation of useful synthesis; W8 evaluates correction and maintenance
after creation. W2 evaluates inspectable evidence, not access policy (W3).
W5 evaluates recurring cost/burden, not response speed (W7). These boundaries
reduce double counting, although architecture criteria cannot be wholly independent.

### Pairwise results under the baseline

| Contest | Winner | Margin | What decides it |
| --- | --- | ---: | --- |
| Cortex vs Karpathy | Cortex | 0.04 | Concrete evidence/retrieval/operations controls barely outweigh synthesis and simplicity. |
| Karpathy vs Transpara | Karpathy | 0.26 | The synthesis-centered contract and simpler ownership overcome governance disadvantages for this non-enterprise baseline. |
| Cortex vs Transpara | Cortex | 0.30 | Evidence checking and agent interoperability overcome Transpara's publication advantage. |

The scorecard also ranks each criterion individually; tied scores mean no
justified preference at this level of evidence. Counting criterion wins would
discard the weights and is not the decision method.

## Sensitivity: which assumptions can reverse the result?

Keep the same score judgments and change only the preference weights. The order
of each vector is **W1 through W12**; every vector totals 100, making the scenarios
fully reproducible rather than impressionistic exceptions.

| Scenario | Weight vector | Karpathy | Transpara | Cortex | Winner |
| --- | --- | ---: | ---: | ---: | --- |
| Balanced baseline | 20,13,12,10,10,8,7,6,5,4,3,2 | 6.76 | 6.50 | 6.80 | Cortex |
| Synthesis-first research | 35,10,5,10,10,10,5,5,3,3,2,2 | 7.55 | 5.95 | 6.33 | Karpathy |
| Enterprise publishing | 10,10,30,8,7,7,8,5,5,4,3,3 | 5.76 | 7.21 | 6.89 | Transpara |
| Agent memory across clients | 10,15,5,15,8,8,10,6,7,4,8,4 | 6.46 | 6.66 | 7.47 | Cortex |

The overall result is fragile in several explicit ways:

- Move **one weight point from W2 to W1**: Karpathy becomes **6.80**, Cortex
  **6.75**, Transpara **6.47**. The overall winner changes.
- Lower Cortex's W2 judgment from 9 to 8 because quote matching is too narrow
  a definition of evidence: Cortex becomes **6.67**, behind Karpathy.
- Lower Karpathy's W1 from 9 to 8 because a specified workflow deserves less
  credit without an implementation: Karpathy becomes **6.56**, widening Cortex's lead.
- Make implemented multi-audience publication a MUST: re-screen candidates;
  do not compensate for a failed mandatory requirement with unrelated strengths.

These are alternative judgments, not fabricated confidence intervals. There
is no statistical basis for interpreting 6.80 as distinguishable from 6.76.

## Adverse consequences and decision risks

KT analysis does not end with the highest sum. Likelihood and impact below are
qualitative scenario judgments, not incident statistics; they do not silently
subtract a second set of weights from the score.

| Candidate risk | Likelihood in baseline use | Impact | Evidence / mitigation needed before adoption |
| --- | --- | --- | --- |
| Karpathy: inconsistent interpretations spread across pages | Material, agent-dependent | High | [Failure analysis](karpathy.md#failure-modes-and-recovery); stage affected-page diffs, preserve source versions, inspect semantic corrections. |
| Transpara: build status mistaken for semantic currency | Material when sources change | High | [Freshness distinction](transpara.md#three-distinctions-that-must-survive-any-comparison); expose a separate synthesis backlog and review status. |
| Cortex: a verified quote is mistaken for a supported answer | Material with analytical questions | High | [Verifier scope](cortex.md#retrieval-details-that-affect-evaluation); assess entailment and multi-source coverage separately. |
| Cortex: Git backup mistaken for complete system backup | Conditional on optional database use | High | [Storage distinction](cortex.md#architecture); back up and restore working/operations state independently. |
| All: unrepresentative evaluation selects the wrong design | High without workload agreement | High | Agree on synthesis, publication and query workloads before committing to migration. |

For Cortex, these risks do not negate its baseline advantages, but they prevent
an unconditional rollout recommendation. A system needing broad publication
controls or autonomous synthesis should not adopt it on this score alone.

## Decision

**Cortex is the selected overall winner for the declared balanced wiki-design
objective.** Its advantage is the combination of durable accessible content and
concrete controls over retrieval, evidence inspection, and failure. It wins as
the evaluated system; no unimplemented hybrid is receiving its score.

**Karpathy is the best synthesis pattern. Transpara is the best enterprise
publication design.** Those are genuine preference reversals supported by the
explicit scenarios, not honorary prizes. For the existing Transpara deployment,
this comparison is a reason to improve its semantic loop and evidence checks,
not a sufficient reason to migrate to Cortex.

A future combined design could retain the Hub's publication model, implement
Karpathy's reviewed multi-page synthesis and answer promotion, and adopt
Cortex-like quote verification, retrieval diagnostics, and revision-aware
reuse. That is a proposed direction, outside this comparison's shipped scope.

## What would turn the judgment into an empirical decision?

Use one openly inspectable corpus and fixed questions, matched model/provider
settings, and identical access scope. Include facts hidden from summaries,
synonyms absent from lexical matches, conflicting dates, superseded notes,
and multi-source analytical questions. Include a small corpus and a larger one
to expose growth behavior. Preserve source and model-output snapshots.

Measure **semantic ingest completion** separately from source registration and
note persistence. Track factual/citation entailment, answerable-question recall,
correct abstention, correction propagation, model tokens, human review minutes,
and cold/warm/repeat-query p50/p95 latency. Measure successful-answer throughput
under concurrent readers and report rejection/timeout rates. A fast error is
not a fast answer. Record hardware, corpus size, cache state, and software SHA.

For costs, count first ingestion, recurring maintenance, external-client model
work, infrastructure, and human review—not just the server's reader invoice.
For recovery, test source deletion, interrupted multi-page updates, stale caches,
provider outages, and separate note/database restoration. Re-score only the
criteria supported by those results. Until then, the winner is an explicit,
auditable architectural judgment with a very narrow margin.

## Document revision history

| Version | Date | Change |
| --- | --- | --- |
| 0.1.1 | 2026-09-18 | Link subsequent CFAR timing without changing the historical KT assessment. |
| 0.1.0 | 2026-09-18 | Establish Transpara document control and a SemVer baseline for previously unversioned content. |
