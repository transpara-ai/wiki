---
entity: Gates (Verification, Trace, and Release Gates)
aliases: [gates, the gate system, product gate minimum, TraceCompletenessGate, trace-completeness gate, release gates, gates A-J, gate minimum]
tier: architecture
status: compiled
last_compiled: 2026-06-13
sources:
  - raw/transpara/dark-factory/Dark Factory - Motive, Goal, Approach.md  # principle 8 "Verify Before Certifying" (L175-185), expected flow (L215-251), gate-class register E (L424-442), v4.0 future gates (L203-210), citation handles (L505-569)
  - raw/transpara/dark-factory/reunification/2026-06-05-slice-1-first-reunified-order-design.md  # gates as role-enforced checks; membrane (§3); "Gates A-J"/"Gate F-J epics" framing
  - Open Brain (mcp__open-brain__search_thoughts, queried 2026-06-13)  # gate lettering map (E-J fixtures), eventgraph#34 implementation of TraceCompletenessGate/BOM, Gate K/L are v4.0-only
confidence:
  product_gate_minimum_list: high (verbatim from primary source L181 and gate-class register L428-442)
  trace_completeness_score_1.0: high (primary source L440; corroborated by eventgraph#34 review in Open Brain)
  gate_lettering_A_through_J: medium — the lettered sequence (Gate E…J) and its PR provenance come from Open Brain notes and the slice-1 doc, NOT from the primary orientation doc, which only names Gates K and L
  reviewer_guardian_enforcement: medium — the reunified "role-enforced checks applied by Reviewer and Guardian" framing is a working design (slice-1, status: review), not accepted doctrine
  v4.0_status: the v4.0 future gates (K, L) are scoped, partially planned, and explicitly not satisfied; v4.0 is not accepted canonical
---

# Gates (Verification, Trace, and Release Gates)

In the [[dark-factory]] architecture, **gates** are the verification checks that must produce passing evidence before a `ReleaseCandidate` can be **certified**. They are the operational form of one of the platform's invariants — *"No release without verification"* (*Dark Factory - Motive, Goal, Approach*, L100). A gate is not an opinion: a release "cannot be certified merely because a model, worker, or human says it is good. Certification requires trace completeness, product gates, security gates, runtime BOM evidence, and audit evidence" (L177).

Gates are the architectural descendant of the late-night seed: when the [[the-20-primitives|20 primitives]] were converted into a governed production architecture, *"explicit criteria become AcceptanceCriteria and gates"* (L127). They are the point where the abstract demand for traceability becomes a concrete pass/fail with recorded evidence.

## Where gates sit in the flow

Gates run near the end of the product work flow, after artifacts and code changes exist and before the release decision (L215-230):

```
... worker returns RuntimeResult / Artifact / CodeChange ...
  9.  GateRunner emits TestRun and GateResult evidence.
 10.  TraceCompletenessGate evaluates required paths.
 11.  Security gates and proof-of-work packet assemble review evidence.
 12.  ReleaseCandidate is certified or rejected.
 13.  AuditReport records the run.
```

The same ordering appears in the mandatory **Base Slice 0** control-plane proof — the minimum end-to-end chain that must pass before any higher autonomy — which threads `TestRun → GateResult → TraceCompletenessGate → FactoryRuntimeVersion → ReleaseCandidate → Certification or Rejection → AuditReport` (L236-251).

## The product gate minimum

Every product `ReleaseCandidate` "must run the product gate minimum" (L181). The primary source lists it as one block:

> unit, integration, e2e, build, migration, secret scan, dependency vulnerability/license, SAST, auth-flow security, configuration security, container/build-artifact scan **when applicable**, trace completeness, FactoryRuntimeBOM check, and audit report check.

The gate-class register (Section E, L428-442) classifies each one and records its constraint:

| Gate | Class | Constraint (from source) |
|---|---|---|
| Unit / integration / e2e | Selected gate class | Must map to `TestRun`/`GateResult`; e2e required for product RC |
| Build | Selected gate class | CI/build output is evidence, **not** certification alone |
| Migration check | Selected gate class | Required for DB template changes (SaaS Template v1) |
| Secret scan | Selected **security** gate class | Open critical findings **block certification** |
| Dependency vulnerability scan | Selected **security** gate class | Scanner versions recorded in BOM where applicable |
| Dependency license scan | Selected **security** gate class | Missing/failing evidence blocks as policy requires |
| SAST | Selected **security** gate class | Required product gate |
| Auth-flow security check | Selected gate class | Required for product RC |
| Configuration security check | Selected gate class | Required for product RC |
| Container/build-artifact scan | **Conditional** gate class | Required only when a build/container artifact exists |
| TraceCompletenessGate | Selected **release** gate | Certified release requires **score 1.0** |
| FactoryRuntimeVersion / BOM check | Selected **release** gate | Missing BOM **blocks certification** |
| AuditReport check | Selected **release** gate | Required **before** certification |

> Note on framing. The one-line summary that seeded this article separates "the product gate minimum (…container scan)" from "the TraceCompletenessGate, the FactoryRuntimeBOM check, and the AuditReport check." The source does **not** draw that line — it lists trace completeness, FactoryRuntimeBOM, and audit-report check as members of the product gate minimum (L181), and the register marks them as the three **release gates** within the same gate-class table. They are the same set, classified into product, security, and release tiers.

## The release gates in detail

Three gates do the certification gatekeeping proper:

- **TraceCompletenessGate.** Blocks certification when the `FactoryOrder`, `FactoryRuntimeVersion`, acceptance evidence, required gate evidence, certification evidence is missing, or when there is unresolved high/critical failure (L179). A **certified** release requires a trace-completeness **score of 1.0** (L440) — i.e. every required provenance path must exist; partial provenance does not certify. This is fail-closed by design: an incomplete or unverifiable trace denies certification rather than waving it through.
- **FactoryRuntimeVersion / BOM check.** Captures the active capabilities, runtimes, policies, templates, and commits in force for the run. A missing BOM blocks certification (L441).
- **AuditReport check.** Ensures final audit evidence exists before certification (L442); the `AuditReport` is the last recorded step of the run (L229, L250).

Release certification itself is a **protected action** — it requires authority, not a model's say-so (L171, see [[authority-layer]]).

### How the release gates are enforced (implementation)

The TraceCompletenessGate, FactoryRuntimeVersion/BOM enforcement, and certification-eligibility check were implemented in the `eventgraph` repo (Dark Factory v3.9 "Stage 5", PR #34, reviewed 2026-05-14), in `go/pkg/darkfactory/v39/{query.go,schema.go}` as `EvaluateTraceCompletenessGate`, `RecordFactoryRuntimeVersionBOM` / `FactoryRuntimeBOMEvidencePath`, and `EvaluateCertificationEligibility`. A load-bearing architectural choice surfaced in that review: **BOM evidence is enforced at the evaluation layer (the gate + cert-eligibility), not at the schema layer** — a bare `FactoryRuntimeVersion` with empty `RuntimeRefs` can still be stored; only the recording wrapper and the gate check the refs. This is the v3.9 *"store records facts, gate evaluates evidence chains"* model. (Source: Open Brain note on eventgraph#34, read this run; the underlying code was not opened in this compilation.)

## The lettered gate sequence (Gates A–J) vs. the v4.0 gates (K, L)

There are **two distinct gate vocabularies** in the corpus, and conflating them is a common error:

1. **The lettered accountability-pipeline gates, A through J.** These are the v3.9 build milestones — each delivered as a *bounded fixture* in the `work` and `site` repos, not yet a live product run. The slice-1 design doc calls them "Gates A–J" and "the Gate F–J epics" ([[the-reunification|slice-1 design]], L43-46, L81). Open Brain records their PR provenance: Gate E = `site#62`, F = `work#38`, G = `work#39`, H = `work#40`, I = `work#41`, J = `work#42`, with Gate J being the "golden PRD product-factory run," plus a separate "Residual Closure" of R-001/R-002/R-003. **These letters do not appear in the primary orientation doc** — they are reconstructed here from Open Brain notes and the slice-1 doc.
2. **The v4.0 future gates, K and L** (L203-210):
   - *Gate K* — interim development loop hardened.
   - *Gate L* — v3.9-to-v4.0 reconciliation certified.
   Both are *"scoped and partially planned, not satisfied"* (L210). Open Brain confirms they are **v4.0-only** program gates (defined in the v4.0 integration arc) and are **not** part of the v3.9 epic arc, which stops at J + Residual Closure.

> ⚠ **Fail-legible note.** The full A–J lettering and its per-gate PR mapping is **medium-confidence**: it traces to Open Brain review notes and the slice-1 doc, both of which I read this run, but **not** to the primary orientation document, which only names K and L. Treat the A–J sequence as build-history reconstruction, not as a claim from the canonical orientation source. The "satisfied" status of A–J is itself narrow: Open Brain repeatedly records them as satisfied *"only for the bounded fixture,"* not for a real product run.

## Gates in the reunified model — checks applied by roles

The 2026-06-05 reunification design proposes inverting how gates run. Today the Dark Factory accountability pipeline (gates A–J) "runs *beside* the civilization, not *through* it" — the gate epics use their own `maintainer` / `recorded_llm` actors and contain "zero references to `guardian`/`cto`/`spawner`/`strategist`" ([[the-reunification|slice-1 design]], L42-48). The drift the doc diagnoses: *"The cage was perfected; the inhabitants never moved in."*

The second of its five inversions is: **"Gates become role-enforced checks, applied inside the cooperative flow by Reviewer and Guardian. Evidence is a *byproduct* of roles working"** (L55-58). In the proposed Slice 1 "membrane," each gate is owned by a civic role rather than a separate pipeline (§3, L145-182):

- **Readiness gate** — owned by the **Planner** (its three artifacts: `definition_of_done`, `acceptance_criteria`, `test_plan`).
- **Trace-completeness** — verified by the **Reviewer**, reusing the darkfactory `TraceCompleteness` record concept.
- **Authority gate** — the **Guardian** raises an `AuthorityRequest` that escalates to the human via the [[site|Site]] decision surface; the protected action (here, opening a real draft PR) stays fail-closed.

Slice 1 deliberately runs only a **minimal membrane** — readiness + trace-completeness + one authority gate — *"Not all of Gates A–J"* (L81), with an explicit "resist membrane creep" warning (L283).

> ⚠ **Fail-legible note.** The "role-enforced checks applied by Reviewer and Guardian" model is a **working design, not accepted doctrine.** The slice-1 doc is `status: review`, `canonical: false`, and states it "graduates into v4.0 doctrine only *after* the slice actually runs." So the assignment of gates to Reviewer/Guardian is a proposal that the orientation doc's gate-class register (which is technology-neutral about *who* runs each gate) does not yet ratify.

## Why gates fail closed

Gates embody the platform's fail-closed posture. Several checks are written so that *absence* of evidence denies certification rather than permitting it: TraceCompletenessGate requires score 1.0 (anything less blocks), a missing BOM blocks, open critical secret findings block, and the AuditReport must exist *before* certification. This matches the broader Dark Factory rule that "unknown high-risk actions deny or require approval" (L171) and the system-level invariants "No release without verification" and "No hidden state that cannot be audited or rebuilt" (L100, L105). The implementation review of the trace/BOM gates (eventgraph#34) found these were *genuinely* enforced at the evaluation layer, not faked — though it also noted thin test coverage on some negative branches (failure/repair/waiver paths unexercised in the fixture).

## Related entities

- [[event-graph]] — the sovereign substrate; `TestRun`, `GateResult`, and the trace/BOM/certification records all live here.
- [[authority-layer]] — release certification and other gate-adjacent protected actions require authority decisions.
- [[work]] — owns the Work DAG and the readiness gate (operational flow, not certification truth).
- [[runtime-broker]] — bounded execution that produces the artifacts the gates then verify.
- [[site]] — the governed console where an authority gate's escalation surfaces for human approval.
- [[the-20-primitives]] — origin: "explicit criteria become AcceptanceCriteria and gates."
- [[acceptance-criteria]] · [[release-candidate]] · [[audit-report]] · [[factory-order]] — the surrounding evidence objects (forward references).

## Sources & provenance

- **Primary:** `Dark Factory - Motive, Goal, Approach.md` — principle 8 *"Verify Before Certifying"* (L175-185), the expected product/Base-Slice-0 flows (L215-251), the verification/audit/security gate-class register, Section E (L424-442), the v4.0 future gates K and L (L203-210), and the citation handles mapping each claim to its v3.9 source spec (notably `DF-V3.9-EVAL-005:L43-L105` = `dark-factory/v3.9/05-verification-audit-risk-eval-v3.9.md`, TraceCompletenessGate; `DF-V3.9-EVAL-005:L153-L195` = product gate minimum; `DF-V4.0-ARC:L115-L149` = Gate K/L definitions). The underlying v3.9 spec files were *not* opened this run — the line-level claims rest on the orientation doc's quotations and its citation table.
- **Reunification design:** `dark-factory/reunification/2026-06-05-slice-1-first-reunified-order-design.md` (`status: review`, `canonical: false`) — gates-as-role-enforced-checks inversion, the "Gates A–J" / "Gate F–J epics" framing, and the Slice 1 minimal membrane (§3).
- **Open Brain** (`mcp__open-brain__search_thoughts`, queried 2026-06-13) — the Gate E–J PR provenance and "satisfied only for the bounded fixture" status; confirmation that Gates K and L are v4.0-only; and the eventgraph#34 (2026-05-14) implementation of `EvaluateTraceCompletenessGate`, `RecordFactoryRuntimeVersionBOM`, and `EvaluateCertificationEligibility` with the "store records facts, gate evaluates evidence chains" enforcement model.
- No durable external (Searles) URL applies to this entity — gates are a Dark Factory engineering construct, not a Searles-post concept; the only Searles thread upstream of it is the primitives→criteria→gates lineage cited via `[Searles-P1]` in the primary doc.

`[[wikilinks]]` are forward references where targets are not yet compiled.
