---
entity: Gate L
aliases: [gate-l, Gate L, v4.0 reconciliation certified, v3.9-to-v4.0 reconciliation]
tier: architecture
status: compiled
last_compiled: "2026-06-15"
sources:
  - raw/open-brain/2026-06.md  # L76 (Integration Arc summary: Gate K + Gate L each with a "satisfied only when" predicate), L697, L817 (Gate L = documentation coverage matrix; ADR-0007 Civilization re-anchor deferred), L947/L969 (Gate L = epic-02 v3.9->v4.0 reconciliation; proposal-only; carries v3.9 into v4.0; completing it RETIRES v3.9 as active baseline; needs human authorization not a run)
  - wiki/gate-k.md  # compiled sibling (Gate K) — Integration Arc framing, sequencing rule, gate-failure rule, lettering note, house style
confidence:
  sources: secondary
  claims: grounded
---

# Gate L

**The second v4.0 program gate: certification that the v3.9-to-v4.0 reconciliation is complete.** Gate L is defined in the v4.0 Integration Arc (`DF-V4.0-INTEGRATION-ARC`, 00-integration-arc-v4.0.md) as **Event 2 — v4.0 Reconciliation Certified**, the companion to [[gate-k|Gate K]]. Where Gate K hardens the interim development loop, Gate L certifies that the accepted [[v3-9|v3.9]] baseline has been carried forward and reconciled into the [[v4-0|v4.0]] doctrine. As of **2026-06-15, Gate L is defined and unsatisfied.** It continues the [[gates|Gates A–J]] lettering as the second of the two v4.0 program gates (K and L), without altering any v3.9 gate.

> ⚠ v4.0, including the Integration Arc and Gate L, has `canonical: false`. [[v3-9|v3.9]] remains the operative baseline. Gate L is a candidate predicate, not an operative one — and uniquely among the gates, **satisfying it is what would retire v3.9 as the active baseline**, not what closes it out.

## Context: where Gate L fits

After the 2026-06-01 adversarial review of the development loop, the [[v4-0|v4.0]] doctrine established that the development process is itself a governed Civilization function (`DF-V4.0-ADR-001`). The v4.0 Integration Arc operationalizes this with two sequential program gates: [[gate-k|Gate K]] for interim-loop hardening (Event 1) and **Gate L** for reconciliation (Event 2). Gate L is the work of epic-02 in the integration arc — the deliberate folding of the v3.9 corpus, specs, and doctrine into the v4.0 frame.

## What Gate L requires

Open Brain records the Gate L predicate as a **documentation-coverage matrix**: a structured demonstration that every load-bearing v3.9 artifact (specs, ADRs, gate definitions, the accepted baseline) has a reconciled place in the v4.0 doctrine, with no orphaned or contradicted coverage. The reconciliation is explicitly **additive, not destructive**: it *carries v3.9 into v4.0* rather than discarding it. A named piece of that scope is **`ADR-0007` (the Civilization definition to re-anchor)**, which the v4.0 acceptance checkpoint logs as **deferred reconciliation work** — the Civilization definition is something the arc carries forward to settle under Gate L, not something it re-runs now.

The defining consequence, recorded plainly in Open Brain: *"completing it RETIRES v3.9 as active baseline — the opposite of closing v3.9."* Gate L is therefore the doctrinal hand-off point, not a capability milestone.

## Current status

The v4.0 doctrine-acceptance checkpoint (`DF-V4.0-CKPT-2026-06-12-ACCEPTANCE`, 2026-06-12) states in its "What This Acceptance Does Not Do" section: *"Gates K and L remain defined and unsatisfied. No gate advances."* (quoted via the compiled [[gate-k]] article). Gate L's epic (epic-02) is **proposal-only**, scoped by a packet whose AuthorityDecision is still pending — unlike Gate K (Event 1), whose authorization was granted on 2026-06-15 (`transpara-ai/docs#132`); Event 2 / Gate L carries no such grant yet. Crucially, Gate L *"needs human authorization, not a run"* — it is reconciliation work for the human External Committee to authorize and accept, not an autonomous build the Civilization executes.

## Sequencing and the no-autonomy property

Per the arc's sequencing rule (recorded in [[gate-k]]), **Gate L may proceed in parallel with Gate K** because, unlike Gate K, it *"carries no autonomy implication."* Operating Principle #10 — *autonomy expands only after audit expands* — gates Gate K ahead of any autonomy-raising step; Gate L raises no autonomy, so it is sequencing-independent. The same gate-failure discipline applies: allowed responses to failure are fix-within-scope, raise a precise blocker, record accepted risk with owner and rationale, or ask the External Committee to re-sequence; forbidden are silently advancing, renaming a failure as non-blocking without rationale, or weakening guardrails to force the gate to pass.

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

- **Secondary:** `raw/open-brain/2026-06.md` — the load-bearing source actually read this compilation. L76 (Integration Arc summary: Gate K and Gate L each carry a "satisfied only when" predicate); L817 (Gate L = a documentation coverage matrix; `ADR-0007` Civilization definition re-anchor logged as deferred reconciliation work); L947 / L969 (Gate L = epic-02 v3.9→v4.0 reconciliation, proposal-only, *"carries v3.9 INTO v4.0,"* *"completing it RETIRES v3.9 as active baseline,"* *"needs human authorization not a run,"* may run in parallel with Gate K).
- **Context (named in source, not directly read this compilation):** `DF-V4.0-INTEGRATION-ARC` (00-integration-arc-v4.0.md, the Event-2 / Gate L definition) and its epic-02 design packet, and `DF-V4.0-CKPT-2026-06-12-ACCEPTANCE` ("Gates K and L remain defined and unsatisfied"). These v4.0 epic files are mirrored locally but not committed to this repo (`raw/transpara/` is gitignored); their content is reached here via the compiled [[gate-k]] sibling and the Open Brain summary above rather than read directly — flagged fail-legibly.

> ⚠ This article is built from the Open Brain operational record and the compiled [[gate-k]] sibling rather than from the v4.0 epic documents directly (those are not in the committed corpus). Claims are grounded in what those sources state; the precise wording of the Gate L coverage-matrix predicate should be re-verified against `00-integration-arc-v4.0.md` / epic-02 when the v4.0 source tier is mirrored. `[[wikilinks]]` to v4.0 are forward/candidate references.
