---
entity: Gate L
aliases: [gate-l, Gate L, v4.0 reconciliation certification predicate, v3.9-to-v4.0 reconciliation]
tier: architecture
status: compiled
last_compiled: "2026-06-17"
sources:
  - DF-V4.0-INTEGRATION-ARC  # Event 2 / Gate L definition, sequencing rule, satisfied-only-when predicate, gate-failure rule, global guardrails
  - DF-V4.0-EPIC-002-OVERVIEW  # carry-forward set, proposal-only status, completion condition, validation guardrails
  - DF-V4.0-EPIC-002-DESIGN  # AC-L1..AC-L5, TC-L1..TC-L5, Gate L predicate, stop condition
  - DF-V4.0-EPIC-002-AUTHORIZATION  # PENDING AuthorityDecision, bounded scope, exclusions, validation requirements
  - DF-V4.0-README  # v4.0 candidate status, relationship to v3.9, reconciliation plan, folder-acceptance criteria
  - DF-V4.0-CKPT-2026-06-12-ACCEPTANCE  # doctrine accepted; folder not canonical; Event 2 unauthorized; v3.9 remains operative
  - raw/open-brain/2026-06.md  # Secondary operational summary: Gate L = coverage matrix; ADR-0007 re-anchor deferred; may run in parallel with Gate K but needs human authorization
  - wiki/gate-k.md  # compiled sibling (Gate K) — Integration Arc framing, sequencing rule, gate-failure rule, lettering note, house style
confidence:
  sources: primary
  claims: grounded
---

# Gate L

**The second v4.0 program gate: the certification predicate for v3.9-to-v4.0 reconciliation.** Gate L is defined in the v4.0 Integration Arc (`DF-V4.0-INTEGRATION-ARC`, 00-integration-arc-v4.0.md) as **Event 2 — v4.0 Reconciliation Certified**, the companion to [[gate-k|Gate K]]. Where Gate K hardens the interim development loop, Gate L is the predicate that would certify the accepted [[v3-9|v3.9]] baseline has been carried forward and reconciled into the [[v4-0|v4.0]] doctrine. As of **2026-06-17, Gate L is defined and unsatisfied**; Gate K is closed for pre-live sequencing only, with go-live revalidation still blocked. Gate L continues the [[gates|Gates A–J]] lettering as the second of the two v4.0 program gates (K and L), without altering any v3.9 gate.

> ⚠ v4.0, including the Integration Arc and Gate L, has `canonical: false`. [[v3-9|v3.9]] remains the operative baseline. Gate L is a candidate predicate, not an operative one — and uniquely among the gates, **satisfying it is what would retire v3.9 as the active baseline**, not what closes it out.

## Context: where Gate L fits

After the 2026-06-01 adversarial review of the development loop, the [[v4-0|v4.0]] doctrine established that the development process is itself a governed Civilization function (`DF-V4.0-ADR-001`). The v4.0 Integration Arc operationalizes this with two sequential program gates: [[gate-k|Gate K]] for interim-loop hardening (Event 1) and **Gate L** for reconciliation (Event 2). Gate L is the work of epic-02 in the integration arc — the deliberate folding of the v3.9 corpus, specs, and doctrine into the v4.0 frame.

## What Gate L requires

The primary Event 2 design packet states that its criteria **are the Gate L predicate**. In short, Gate L requires a v4.0 coverage matrix and standalone v4.0 content that carry every binding carry-forward-set obligation forward without loss:

1. **AC-L1 — coverage matrix per dependent v3.9 document.** For each v3.9 document in the Event 2 carry-forward set, the matrix maps each binding obligation to the v4.0 location that states it standalone.
2. **AC-L2 — obligation-class coverage.** Safety, authority, audit, runtime, schema, gate, risk, SOP, and capability obligations must exist as standalone v4.0 content; no v4.0 statement may require opening old source files such as v3.9 or archive/v2 files.
3. **AC-L3 — v3.9 untouched.** No v3.9 file is archived, deleted, or mutated by Event 2.
4. **AC-L4 — Civilization definition re-anchor.** The archive/v2 `ADR-0007` Civilization definition is re-anchored as standalone v4.0 content; any binding ADR-0007 obligation beyond the definition must have coverage-matrix rows or an explicit no-further-binding-obligations attestation that enumerates the ADR-0007 clauses reviewed.
5. **AC-L5 — human acceptance checkpoint.** v4.0 is not marked accepted canonical without a human acceptance checkpoint.

Partial coverage does not satisfy Gate L. The stop condition is also explicit: if any binding carry-forward-set obligation cannot be represented in v4.0 without change or loss, the correct response is to stop and report a blocking design finding, not to alter the obligation or publish a partial workaround.

## Current status

The v4.0 doctrine-acceptance checkpoint (`DF-V4.0-CKPT-2026-06-12-ACCEPTANCE`, 2026-06-12) accepts only the seed doctrine. It leaves folder acceptance criterion 2 — the reconciliation coverage matrix — open, records Event 2 as unauthorized, and keeps [[v3-9|v3.9]] as the operative baseline.

The Event 2 authorization packet is still **PROPOSED - NOT YET GRANTED**. Its AuthorityDecision is `ApprovalRequired`, with the human External Committee still the pending decider. Reconciliation may begin only after that human authority decision changes to `Autonomous` or `Notify` for the bounded docs-only scope. Gate K later received Event-1 authorization on 2026-06-15 (`transpara-ai/docs#132`) and a pre-live waiver on 2026-06-17 (`transpara-ai/docs#138`), but those do not grant Event 2 or satisfy Gate L.

## Sequencing and the no-autonomy property

Per the integration arc's sequencing rule, **Event 2 may proceed in parallel with Event 1** because documentation reconciliation carries no autonomy implication. That sequencing rule does not override the authorization gate: Gate L work still requires the human AuthorityDecision above before implementation. Operating Principle #10 — *autonomy expands only after audit expands* — gates Gate K ahead of any autonomy-raising step; Gate L raises no autonomy, so it is sequencing-independent once authorized. The same gate-failure discipline applies: allowed responses to failure are fix-within-scope, raise a precise blocker, record accepted risk with owner and rationale, or ask the External Committee to re-sequence; forbidden are silently advancing, renaming a failure as non-blocking without rationale, or weakening guardrails to force the gate to pass.

## Dependent carry-forward set

The Event 2 overview now partitions the carry-forward set into the v3.9 documents that AC-L1 / TC-L1 cover under the coverage matrix, plus the archive/v2 ADR-0007 re-anchor governed by AC-L4 / TC-L4.

The v3.9 documents are:

- `04-production-workflow-and-runtime-v3.9.md` — FactoryOrder, Work DAG, production cells.
- `03-authority-identity-and-sops-v3.9.md` — authority outcomes, protected actions, roles.
- `05-verification-audit-risk-eval-v3.9.md` — gates, risk register, audit, eval.
- `implementation/epics/00-epic-arc-v3.9.md` — capability epic arc.
- `implementation/epics/01-autonomy-levels-v3.9.md` — autonomy Level 0-5 vocabulary.
- `implementation/epics/04-milestones-gates-and-review-questions-v3.9.md` — Gates A-J.
- `implementation/as-built-stage-tracker-v3.9.md` — current-state record.
- `implementation/state-of-the-system-proof-v3.9.md` — state proof.

The archive/v2 re-anchor is `ADR-0007-civilization-hive-governance.md`, the Civilization definition that must become standalone v4.0 content. The source packet no longer treats that ADR as a ninth v3.9 document. That clarifies the count; it is not Gate L progress, does not start reconciliation, and does not satisfy AC-L1 or AC-L4.

## Lettering note

As [[gates]] flags, v3.9 uses letters A–J for its accountability-pipeline milestones; v4.0 adds **K and L** as program gates for a *different scope* — the integration arc, not factory-capability milestones. Open Brain records that this lettering collision was raised in same-family review and reviewed cross-family by Codex, which raised no finding. The two gate vocabularies coexist but are distinct in scope, predicate structure, and satisfaction criteria. See [[gate-k]] for the Event 1 companion.

## Related entities

- [[gate-k]] — the Event 1 companion gate (interim development-loop hardening); the two were introduced together.
- [[gates]] — the full gate system; Gates A–J are the v3.9 arc the K/L pair extends.
- [[v4-0]] — the v4.0 doctrine and Integration Arc that define Gate L. ⚠ candidate, `canonical: false`.
- [[v3-9]] — the operative baseline Gate L reconciles forward (and would retire as *active* on completion).
- [[the-reunification]] — the broader reunification of the development process into the Civilization, of which the v4.0 doctrine is the doctrinal arm.
- [[dark-factory]] — the governed-production system whose doctrine lineage Gate L reconciles.
- [[authority-layer]] — gate satisfaction is a protected action requiring authority evidence, not self-report.
- [[event-graph]] — remains the source of truth for evidence, authority, and gate state.

## Sources & provenance

- **Primary:** `DF-V4.0-INTEGRATION-ARC` (`00-integration-arc-v4.0.md`) — Event 2 definition, Gate L satisfied-only-when predicate, sequencing rule, deferred backlog, gate-failure rule, and global guardrails.
- **Primary:** `DF-V4.0-EPIC-002-OVERVIEW` — proposal-only Event 2 overview, carry-forward set partition, success criteria, out-of-scope list, and completion condition.
- **Primary:** `DF-V4.0-EPIC-002-DESIGN` (`01-reconciliation-design-v4.0.md`) — requirements R-L1..R-L3, acceptance criteria AC-L1..AC-L5, named test cases TC-L1..TC-L5, Gate L predicate, ADR-0007 evidence guardrail, target autonomy level, stop condition, and boundary.
- **Primary:** `DF-V4.0-EPIC-002-AUTHORIZATION` (`02-reconciliation-authorization-v4.0.md`) — proposed authorization packet, pending AuthorityDecision, bounded scope, exclusions, validation requirements, stop conditions, and post-grant handoff.
- **Primary:** `DF-V4.0-README` and `DF-V4.0-CKPT-2026-06-12-ACCEPTANCE` — v4.0 folder remains candidate, v3.9 remains operative, carry-forward coverage criterion open, and Event 2 unauthorized.
- **Secondary:** `raw/open-brain/2026-06.md` — operational summary corroborating Gate L as epic-02 coverage-matrix reconciliation, proposal-only, human-authorized, and parallelizable with Gate K because it carries no autonomy implication.

`[[wikilinks]]` to v4.0 remain forward/candidate references. This article describes Gate L's predicate and authorization boundary; it does not start Event 2, satisfy Gate L, mark v4.0 canonical, or retire v3.9 as the operative baseline.

> ⚠ Source reproducibility note: the `DF-V4.0-*` primary source identifiers above refer to a local mirror of the `transpara-ai/docs` source tier that is gitignored in this public wiki repository. They were read directly during this compilation, but neither the mirror paths nor private repo URLs or full private SHAs are published here. The article summarizes Gate L's non-secret predicate and authorization boundary; it does not publish the authority packet as a substitute for a future human grant.
