---
entity: The Drift (Two Systems on One Substrate)
aliases: [the drift, two systems on one substrate, the cage was perfected, lost the Mission]
tier: arc
status: compiled
last_compiled: 2026-06-13
sources:
  - raw/transpara/dark-factory/reunification/2026-06-05-slice-1-first-reunified-order-design.md  # primary: "Why this workstream exists (the drift, in one paragraph)"
  - raw/transpara/dark-factory/reunification/README.md  # workstream framing
  - raw/transpara/dark-factory/Dark Factory - Motive, Goal, Approach.md  # arc context, citation handles, v4.0 doctrine
  - Open Brain thoughts, 2026-06-05 "Dark Factory drift diagnosis" and "reunification workstream opened" (vocabulary-frequency evidence)
confidence:
  drift_diagnosis: high (reproducible by grep; recorded in primary design doc and Open Brain)
  vocabulary_counts: medium — single-run grep figures from one Open Brain capture (2026-06-05), not re-verified this run
  v4_status: contested across sources — see "A note on v4.0's status" below
---

# The Drift (Two Systems on One Substrate)

**The Drift is the diagnosed failure that the [[the-reunification]] workstream exists to correct.** On **2026-06-05**, Michael Saucier reported he had "lost the Mission." A three-agent research pass across the philosophy, build, and code strata produced an evidence-grounded diagnosis, recorded the same day in the primary design doc *"Slice 1 — The First Reunified Order"* and in Open Brain. The finding, in one sentence: **the project built two systems on one EventGraph substrate that never connected.**

This is not a Searles-philosophy entity and not a clean architecture entity — it is the **arc's turning point**, the moment the build noticed it had wandered off its own north star and named the wandering precisely enough to reverse it.

## The two systems

The diagnosis identifies two things sharing one [[event-graph]] substrate but running past each other:

1. **A living [[hive-governance]] civilization** — a real, working emergent-agent growth loop in `hive/pkg/hive` + `pkg/loop`, with nine bootstrap civic roles (guardian, sysmon, allocator, cto, spawner, reviewer, strategist, planner, implementer) and a functioning growth loop: `CTO /gap → hive.gap.detected → Spawner /spawn → hive.role.proposed → Guardian /approve → Allocator /budget → watch.go:spawnDynamicAgent`, with new agents spawned trust-gated (`CanOperate=false`).
2. **A standalone [[dark-factory]] accountability pipeline** — the `work/epic*.go` Gate F–J fixtures: envelopes, authority, evidence, and gates A–J. This pipeline runs **beside** the civilization, not **through** it.

The seam never closed. The Gate F–J epics contain **zero references** to `guardian`/`cto`/`spawner`/`strategist` and use their own `maintainer` / `recorded_llm` actors instead. The two systems coordinate through the same graph in principle, but the accountability machinery has no knowledge of the civic roles.

## How the drift is provable (not just asserted)

This entity is unusually well-grounded for an arc claim, because the diagnosis is **reproducible from source** rather than narrative. The primary design doc states the check directly:

> `grep -rnE 'guardian|cto|spawner|strategist' work/epic*.go` returns no civic-role references (the epics use `maintainer` / `recorded_llm` actors).

So the central claim — that the accountability pipeline has no civic-role awareness — is a grep, not an opinion. (This run did not re-execute the grep against the live `work` repo; the claim traces to the design doc's own provenance note and the matching Open Brain capture.)

The Open Brain drift-diagnosis capture (2026-06-05) adds vocabulary-frequency evidence from `dark-factory/v3.9/`: **"gate" ×1865, "evidence" ×1097, "bounded" ×680, "authority" ×639, "fixture" ×564 — vs "civilization" only ×8** (all referring to a one-time research process, not the operative concept) **and "hive mind" ×0.** The operative concept set had become `RuntimeEnvelope`, `AuthorityRequest/Decision/ExecutionReceipt`, `PolicyEngineAdapterDecision`, gates A–J, evidence chains, fail-closed, bounded fixtures.

> ⚠ **Fail-legible note (thin evidence).** The exact counts above come from a *single* Open Brain capture dated 2026-06-05 and were **not re-verified this run.** Treat the precise integers as indicative of magnitude (accountability vocabulary overwhelmingly dominant; civilization/hive-mind vocabulary nearly absent), not as audited figures.

## The three things that went wrong

The drift has three named symptoms, all from the primary design doc's one-paragraph statement:

1. **The accountability machinery became the product.** Envelopes, authority, evidence, gates A–J — the *membrane* the civilization was supposed to act *within* — became the thing being built, instead of the medium for building. (Open Brain states the root cause crisply: "accountability was meant to be the MEMBRANE the civilization acts within; it became the PRODUCT.")
2. **The civic roles survive only as a permission ACL.** The role taxonomy persists in just two v3.9 spec files (`03-authority-identity-and-sops`, `04-production-workflow`) as static role→allowed-action tables and separation-of-duties constraints. The roles are entirely absent from the operative implementation layer (the epic arc, the state-of-system proof, the milestones/gates doc) and from all ten visualization views.
3. **v4.0 enthroned the human committee, not the Hive Mind.** v4.0 ("development-process-as-governed-civilization-function") did not operationalize hive-mind governance. Per the Open Brain capture, v4.0's two gates re-label the same accountability machinery (Gate K = GitHub mechanics; Gate L = a documentation-coverage matrix), its "civilization" count (×47) co-occurs with "External Committee" — the humans — (×46), and "hive mind"/"emergent"/"cooperat" are all ×0. v4.0 Event 2 lists the ADR-0007 Civilization definition as **deferred** reconciliation work — the Civilization is something to carry forward later, not run now.

## The line that names it

The primary design doc closes the drift paragraph with the arc's defining image:

> **"The cage was perfected; the inhabitants never moved in."**

The Open Brain capture records a near-identical variant from the diagnosis session — *"The factory perfected the cage and never moved the inhabitants in."* The two phrasings agree; the design-doc form is the canonical one quoted in the entity's own one-line summary. The "cage" is the gates-and-evidence membrane; the "inhabitants" are the [[hive-governance]] civic roles and the growth loop. The membrane was built to near-completion; the society it was meant to contain never came to live inside it.

## Why this is the arc's turning point

The Drift is the diagnostic half of a before/after pair. Its corrective half is the [[the-reunification]] workstream and its first concrete step, [[slice-1-completion|the first reunified order]] — *"one civilization, one business,"* taken in **demonstration-first** mode: prove the reunion with one living run before rewriting any doctrine. The five inversions that slice proposes ("the factory is the civilization at work") are each a direct negation of a drift symptom — the order becomes the unit of cooperation, gates become role-enforced checks with evidence as a *byproduct*, the Hive Mind governs with the human as top authority tier, the growth loop runs in production, and the visualization shows the society building the order rather than abstract forensic tiers.

It also re-frames what the accountability work was *for*. The drift was not that the gates/evidence machinery was wrong — that machinery is reused as the membrane, not retired. The drift was a **category error**: building the membrane as the product. Naming it converted ~80% of the existing work from "the thing" into "the medium," which is why the corrective slice could be ~80% reuse plus a few new seams rather than a rewrite.

## A note on v4.0's status (sources disagree)

The drift diagnosis (2026-06-05) and the reunification README (updated 2026-06-10) both treat v4.0 as a **candidate / proposal-only** doctrine that "enthroned" the human committee and had not been accepted. However, the architecture doc *"Dark Factory — Motive, Goal, Approach"* states that **v4.0's seed doctrine was accepted on 2026-06-12** ("a doctrine shift whose seed doctrine was accepted on 2026-06-12 … the v4.0 integration program remains proposal-only, and v4.0 does not supersede v3.9 until the folder is accepted canonical under its coverage matrix"). These are **not in conflict on the drift itself** — both agree v4.0, as it stood when the drift was diagnosed, formalized the human committee rather than hive-mind governance. They differ on *timeline status*: the drift docs predate the 2026-06-12 seed-doctrine acceptance. The "enthroned the human committee" claim is a statement about v4.0's **content at diagnosis time**, and remains accurate as such; it is not a claim that v4.0 was rejected.

## Open / unproven edges

- **The grep is from the design doc, not re-run here.** The claim of "zero civic-role references in `work/epic*.go`" traces to the design doc's provenance note and Open Brain, not to a fresh grep this run. High confidence it held on 2026-06-05; not re-verified against the current `work` repo.
- **Vocabulary counts are single-capture and thin** (see fail-legible note above).
- **"Lost the Mission" is a reported subjective state**, attributed to Michael in the Open Brain capture. It is the *motive* for the diagnosis, not a measurable fact; treat it as honestly recorded context, not evidence.
- **The drift is a diagnosis, and the cure is in-progress.** As of the source dates, the reunification is demonstrated by living runs (the [[hive-governance]] civic roles produced a real `civic-roles.md` artifact coordinating only through the shared graph), but the corrected v4.0 doctrine and replacement visualization are extracted *from* those runs and remain planning-authority, not accepted canonical.

## Sources & provenance

Primary source: `raw/transpara/dark-factory/reunification/2026-06-05-slice-1-first-reunified-order-design.md`, specifically the section *"Why this workstream exists (the drift, in one paragraph)"* and its *"Provenance of the framing"* note (the grep is quoted there). Workstream framing from `raw/transpara/dark-factory/reunification/README.md`. Arc context, the v4.0 doctrine timeline, and the durable Searles citation handles from `Dark Factory - Motive, Goal, Approach.md` (durable URLs: `Searles-P1` https://mattsearles2.substack.com/p/20-primitives-and-a-late-night ; `Searles-Cult-Test` https://mattsearles2.substack.com/p/the-cult-test). Chronology, the "lost the Mission" framing, the vocabulary-frequency figures, and the alternate "factory perfected the cage" phrasing from two Open Brain captures dated 2026-06-05 ("Dark Factory drift diagnosis" and "Dark Factory 'reunification' workstream opened"). Sources agree on the substance of the drift; they differ only on v4.0's acceptance *timeline* (see "A note on v4.0's status"), cited on both sides. `[[wikilinks]]` are forward references; several target articles may not yet be compiled.
