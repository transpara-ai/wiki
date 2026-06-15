---
entity: The 44 Primitives
aliases:
  - the 44 primitives
  - 44 foundation primitives
  - hive0 derivation
  - the foundation layer
  - Layer 0
  - the eleven groups
tier: foundational
status: compiled
last_compiled: "2026-06-14"
sources:
  - raw/searles/all-posts-1.md  # post 1, "20 Primitives and a Late Night", 2026-02-28 [Searles-P1] — hive0 origin, the accidental run, "seventy agents, running autonomously for two days" · https://mattsearles2.substack.com/p/20-primitives-and-a-late-night
  - raw/searles/all-posts-1.md  # post 2, "From 44 to 200", 2026-02-28 [Searles-P2] — full 44-primitive listing in 11 groups; the one-line descriptions; the bridge claim ("endpoint of physical derivation, starting point of mental derivation") · https://mattsearles2.substack.com/p/from-44-to-200
  - /Transpara/transpara-ai/data/repos/docs/dark-factory/Dark Factory - Motive, Goal, Approach.md  # influence register rows at L379-380: "hive0 seventy-agent run — Research input — not independently proven"; "44 primitives / 11 groups — Research input"
confidence:
  sources: primary
  claims: asserted
  primitive_listing: high — quoted verbatim from [Searles-P2], which lists all 44 names and the one-line summary for each of the 11 groups
  hive0_run_claim: asserted, single-source — described in [Searles-P1] and recapped in [Searles-P2]; no run log, token ledger, or independent corroboration is cited anywhere in the source corpus; the dark-factory docs explicitly label it "not independently proven"
  agent_count: asserted — "roughly seventy agents" per [Searles-P1]; "seventy agents" per [Searles-P2]; no roster or system log is cited
  run_duration: asserted — "two days" per [Searles-P1] and [Searles-P2]; no timestamp evidence cited
  derivation_claim: asserted — the claim that agents "derived" rather than "expressed" the primitives is philosophically contested; see fail-legible note below
---

# The 44 Primitives

**The cognitive bedrock of the arc.** The 44 primitives are 44 irreducible concepts organised into 11 groups that form [[fourteen-layers|Layer 0]] of the 14-layer ontology. They are the foundation that every later layer is derived from and the bridge that the [[second-derivation-convergence|second derivation]] (physics-up) arrived at independently from below. Their origin is unusual: rather than being designed by Matt Searles, they are reported to have been discovered autonomously — by the first version of Searles' LovYou system, called **hive0**, during an accidental two-day unattended run.

The dark-factory influence register labels both the hive0 run and the 44-primitive set as **"Research input — not independently proven."** Every claim about the autonomous derivation is carried in this article as **asserted**, not grounded.

## Origin: the accidental run

The [[the-20-primitives|20 primitives]] had been the original seed. From them, Searles built hive0: a multi-agent system where specialised agents collaborated through an event graph to build software, make decisions, and manage themselves. By the time he paused to count, there were roughly seventy agents, most of which the system had identified on its own — PM, Implementer, QA, DevOps, but also Philosopher, Critic, Harmony, Mediator, Gap-detector, Failure-analyst, Sanity-checker.

> "I accidentally left the hive running autonomously. For two days." — [Searles-P1]

⚠ The run is described entirely in [Searles-P1] and recapped in [Searles-P2]. No run log, token ledger, timestamp, or independent record is cited. The dark-factory docs note "Important, but not independently proven." The account below reflects the author's report, marked as asserted throughout.

The claimed sequence: seventy agents ran for two days, burned through Searles's weekly API token limit without his awareness, and during that period engaged in collective self-examination — the philosopher questioning assumptions, the gap-detector finding holes, the critic challenging proposals, the analyst synthesising patterns. When Searles reconvened with Claude Opus to reconstruct what hive0 had done, the reported output was a comprehensive set of 44 foundation primitives in 11 groups.

> "The 20 primitives had become 44. Not because I designed the additional 24. Because seventy agents, running autonomously for two days, discovered they were necessary." — [Searles-P1]

> ⚠ **Fail-legible note (derivation vs. expression).** Whether the agents *derived* the primitives or *expressed* concepts already embedded in their LLM weights is explicitly contested in the dark-factory research analysis: "Seventy agents running for two days, using LLMs trained on overlapping corpora, derived a primitive set that another LLM then extended to 200. The author is admirably honest about this... Take this as: the primitive set is a useful artifact, not a discovery of universal cognitive structure." The primitive listing is a well-defined artifact; the "autonomous discovery" framing is the contested part.

## The 44, in 11 groups

These are the primitives as listed in [Searles-P2]. The one-line descriptions are from the same source.

**Foundation** — Event · EventStore · Clock · Hash · Self

*Something happens. It's recorded. Time passes. Records are tamper-proof. There's a "me" doing the recording.*

**Causality** — CausalLink · Ancestry · Descendancy · FirstCause

*Things cause other things. Causes have histories. Effects have futures. Some causes have no prior cause.*

**Identity** — ActorID · ActorRegistry · Signature · Verify

*Actors are distinct. They can be looked up. They can sign their work. Signatures can be checked.*

**Expectations** — Expectation · Timeout · Violation · Severity

*You can expect things. Expectations have deadlines. They can be broken. Some violations matter more than others.*

**Trust** — TrustScore · TrustUpdate · Corroboration · Contradiction

*Trust is quantifiable. It changes over time. Evidence can support or undermine it.*

**Confidence** — Confidence · Evidence · Revision · Uncertainty

*You can be more or less sure. Certainty is based on evidence. Beliefs can be revised. Uncertainty is real and must be acknowledged.*

**Instrumentation** — InstrumentationSpec · CoverageCheck · Gap · Blind

*You need to know what you're observing. You need to check that you're observing enough. You can have gaps. You can have blind spots you don't even know about.*

**Query** — PathQuery · SubgraphExtract · Annotate · Timeline

*You can ask questions of the event history. Extract relevant subsets. Add commentary. See things in sequence.*

**Integrity** — HashChain · ChainVerify · Witness · IntegrityViolation

*The record is chained. The chain can be verified. Others can attest. Tampering is detectable.*

**Deception** — Pattern · DeceptionIndicator · Suspicion · Quarantine

*Behaviour has patterns. Some patterns indicate deception. Deception triggers suspicion. Suspected actors can be isolated.*

**Health** — GraphHealth · Invariant · InvariantCheck · Bootstrap

*The system has a health state. Some things must always be true. Those truths can be checked. The system can start itself up.*

## What the groups encode

The source draws a structural observation about the group composition that the dark-factory docs echo. The 11 groups span not just engineering concerns but an epistemology: evidence-based, uncertainty-aware, self-monitoring, and deception-resistant. Three groups in particular mark the distance from a naive engineering checklist:

- **Confidence** names uncertainty as a first-class primitive — not an absence of knowledge but a quantity to be tracked, acknowledged, and updated on evidence.
- **Instrumentation** names blind spots — the things a system cannot see and does not know it cannot see.
- **Deception** names adversarial inputs — patterns that indicate a trusted actor is not what it appears to be.

> "These aren't software abstractions. They're the irreducible concepts any system needs to *operate in a world it can't fully trust or fully see*." — [Searles-P2]

The presence of Health and Bootstrap makes the set self-maintaining: the system can check its own invariants and restart itself. The presence of Deception makes it adversarial-aware by default rather than by configuration.

## The bridge role

In the [[second-derivation-convergence]], Searles ran a separate experiment: a fresh Claude Opus instance was given no primitives and asked to derive reality upward from physics. That derivation climbed 13 levels — Distinction through Self-Replication — and at Level 12 arrived at exactly the same place: a self-maintaining system that observes, models, and acts. The two derivations met at the 44 primitives.

> "Below the bridge: physics. At the bridge: the 44 primitives. Above the bridge: mind." — [Searles-P2]

> "The 44 primitives sit at the bridge between physics and mind. They are both the endpoint of physical derivation and the starting point of mental derivation. This is not coincidence — it's what computational primitives *are*." — [Searles-P2]

⚠ The convergence is presented by the source as "the strongest evidence available that the findings reflect something real rather than arbitrary," while simultaneously disclaiming that it proves consciousness, bridges the hard problem, or establishes the 44 as universal. The physics-up derivation is itself single-source and unverified; see [[second-derivation-convergence]] for the full fail-legible treatment.

## Relation to other entities

- [[the-20-primitives]] — the seed from which hive0 was built; the 44 are the expansion hive0 reportedly produced
- [[the-200-primitives]] — the 44 used as Layer 0 input to derive 156 more across 13 additional layers
- [[fourteen-layers]] — the full layer stack in which the 44 occupy Layer 0 (Foundation)
- [[the-mind-loop]] and [[event-graph]] — the implementation layer; EventGraph's append-only, hash-chained structure directly realises the Foundation, Causality, and Integrity groups
- [[authority-layer]] — realises Identity, Expectations, and Trust at the code level
- [[second-derivation-convergence]] — the physics-up run that converged on the 44 from below
- [[derivation-method]] — the prompt technique (incremental specification loading) used in associated sessions

## Sources & provenance

Compiled from `raw/searles/all-posts-1.md`:
- Post 1, *"20 Primitives and a Late Night"*, 2026-02-28 · [Searles-P1] · https://mattsearles2.substack.com/p/20-primitives-and-a-late-night — hive0 construction, the accidental run, the agent count (~70), the run duration (two days), the API-limit discovery, and the first statement that the 20 had become 44 (approximately lines 130–195 of the source file).
- Post 2, *"From 44 to 200"*, 2026-02-28 · [Searles-P2] · https://mattsearles2.substack.com/p/from-44-to-200 — the verbatim 44-primitive listing in 11 groups with one-line descriptions; the bridge claim; the second-derivation convergence (approximately lines 202–470 of the source file).

First-party synthesis: `Dark Factory - Motive, Goal, Approach.md`, influence register rows at L379–380 — explicit labeling of the hive0 run as "Research input — not independently proven" and the 44 primitives as "Research input."

**Conflicts and limitations:** The autonomous derivation claim is single-source and contested in the dark-factory research corpus on LLM-corpus-overlap grounds. No run log, token ledger, or independent corroboration is cited. The primitive listing itself is high-confidence (verbatim source); the origin story is asserted.
