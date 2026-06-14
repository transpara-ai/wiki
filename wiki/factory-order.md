---
entity: FactoryOrder (Durable Unit of Work)
aliases: [factory order, FactoryOrder, the order, the durable starting object, the unit of cooperation, OrderKind]
tier: architecture
status: compiled
last_compiled: 2026-06-13
sources:
  - raw/transpara/dark-factory/Dark Factory - Motive, Goal, Approach.md  # §"Description of Approach" steps 1–3; "Top-Level Goal"; "Expected Flow"; cites DF-V3.9-SPEC-004:L38-L69 (FactoryOrder contract)
  - raw/transpara/dark-factory/reunification/2026-06-05-slice-1-first-reunified-order-design.md  # "the order is the unit of cooperation"; working design, not accepted doctrine
  - raw/open-brain  # Open Brain thoughts 2026-06-05..06-10 on work/factory_order.go, SeedFactoryOrder, OrderKind, the cmd/hive factory order mechanism, and Slice-1 run results
confidence:
  doctrinal_contract: high (Motive doc is first-party synthesis; cites the v3.9 spec line range, but the spec file itself was not read this run — see note below)
  field_list: medium — sources phrase the field set two slightly different ways; reconciled explicitly below, not silently merged
  unit_of_cooperation_framing: working design only — the reunification slice-1 doc states it is "not accepted doctrine," graduating into v4.0 only after a real run
  as_built_struct: high for what it is (traced to code via Open Brain captures) but it diverges from the doctrinal contract — flagged below
---

# FactoryOrder (Durable Unit of Work)

The **FactoryOrder** is the durable starting object for product work in the [[dark-factory]]. It is the first thing created when a human goal enters the factory: it captures and preserves the human's intent, then decomposes into Requirements, AcceptanceCriteria, and Tasks that the rest of the system fulfils. In the *Dark Factory - Motive, Goal, Approach* orientation, every successful run begins `human intent -> FactoryOrder -> Requirements and AcceptanceCriteria -> Work tasks -> ...` — the order is the root of the causal chain that the [[event-graph]] makes inspectable.

It appears in two registers that this article keeps separate, because they are at different levels of authority:

- The **v3.9 doctrinal contract** — the durable starting object inside the accountability pipeline, defined in the dark-factory v3.9 specification and summarised in the orientation doc (created 2026-06-04, updated 2026-06-12). This is the operative baseline.
- The **reunification reframing** (design dated 2026-06-05) — the same `FactoryOrder` recast as *the unit of cooperation that the civic roles fulfil*, so the factory becomes "the civilization at work." This is explicitly a **working design, not accepted doctrine**; it graduates into v4.0 only after a slice actually runs.

There is also an **as-built Go type** (`work.FactoryOrder`) whose shape diverges from the doctrinal contract. All three are covered below; where they disagree, the disagreement is named rather than resolved.

## What it is for (the doctrinal contract)

The orientation doc's approach lists the order as step 2 of the run, immediately after preserving human intent (step 1):

> "A FactoryOrder is the durable starting object for product work. It records source intent, requester, scope, constraints, release policy, risk class, and source references."
> "The factory should not begin work until scope, exclusions, release policy, and risk class are explicit enough to support review."

Two design intents are encoded here:

1. **Durability and provenance.** The order is durable and records *source references* — it is not an ephemeral prompt. Step 1 ("Preserve Human Intent") requires that source intent be "non-empty, preserved by reference or hash, and not silently rewritten," with inferred requirements marked as inferred. The FactoryOrder is where that preserved intent lives, so the model cannot quietly substitute its own preferred interpretation for the user's request.
2. **A readiness precondition.** Work must **not begin** until scope, exclusions, release policy, and risk class are explicit enough to support review. The order is a gate as much as a record: an under-specified order is not yet ready to decompose. This is the [[dark-factory]]'s fail-closed posture applied at the very front of the pipeline.

### Note on the field list (sources phrase it two ways)

The one-line summary for this entity lists the fields as *source intent, requester, scope, exclusions, constraints, release policy, risk class, and source references*. The orientation doc's defining sentence (quoted above) lists *source intent, requester, scope, constraints, release policy, risk class, and source references* — it does **not** include "exclusions" in that enumeration. "Exclusions" appears in the **next** sentence, as part of the readiness precondition ("scope, exclusions, release policy, and risk class … explicit enough to support review").

So the two phrasings are consistent but not identical: the orientation doc treats *exclusions* as something the order must make explicit before work starts, without listing it as a named record field in the same breath as the others. The authoritative field-by-field contract is cited as **DF-V3.9-SPEC-004:L38-L69 ("FactoryOrder contract and invariants")**, a file that was **not read in this compile** — so the exact, normative field roster is asserted via the orientation doc's summary, not verified here. Treat the precise field set as **medium-confidence** pending a read of the v3.9 spec.

## How it decomposes (Requirements, AcceptanceCriteria, Tasks)

The order is the unit that the rest of the pipeline expands. Step 3 of the approach:

> "A planner proposes requirements, acceptance criteria, assumptions, ambiguities, options, task drafts, risk notes, and human-review flags. [[work|Work]] turns accepted pieces into tasks and manages the operational DAG."

So the decomposition is a two-actor move: a **planner** proposes the requirements / [[acceptance-criteria|AcceptanceCriteria]] / task drafts (with ambiguities and risk flags surfaced, not buried), and **[[work|Work]]** — the production-DAG layer — turns the *accepted* pieces into tasks and dependencies. The orientation doc is explicit that "unrelated tests do not satisfy acceptance criteria" and that "manual verification is limited by risk class unless explicitly waived" — the order's declared risk class therefore propagates downstream into how rigorously the resulting tasks must be verified.

The "Base Slice 0" control-plane proof shows the full decomposition chain the order seeds:

```text
FactoryOrder -> Requirement -> AcceptanceCriterion -> Task -> local deterministic worker
  -> Artifact -> TestCase -> TestRun -> GateResult -> TraceCompletenessGate
  -> FactoryRuntimeVersion -> ReleaseCandidate -> Certification or Rejection -> AuditReport
```

The order also reappears as a **certification gate input**: the orientation doc states that `TraceCompletenessGate` blocks certification when the FactoryOrder (among other evidence) is missing (cited to DF-V3.9-EVAL-005). The order is thus both the *root* of the run and one of the *provenance paths* the release gate later checks for.

## The "unit of cooperation" reframing (working design, not doctrine)

The reunification slice-1 design (2026-06-05) reframes the order. Its first of "five inversions" is:

> "**The order is the unit of cooperation.** A `FactoryOrder` enters as Work; the civic roles fulfill it by emitting events on the shared graph, instead of an epic running as a closed fixture."

The motivation is a diagnosed drift: the project had built two systems on one [[event-graph]] substrate — a living [[hive-governance|Hive]] civilization with an emergent growth loop, and a dark-factory accountability pipeline that ran *beside* it rather than *through* it. In the slice-1 framing, the order becomes the thing the civic roles **cooperate to fulfil**, coordinating only through graph events (no direct agent-to-agent messaging), with the accountability machinery acting as a *membrane* around their work rather than as a separate pipeline. The intended flow:

```text
order injected as a Work task
  -> strategist decomposes the order  (/task create)
  -> planner attaches the contract    (definition_of_done, acceptance_criteria, test_plan)  [readiness gate]
  -> implementer builds the artifact   (CodeChange, proposal-only, on a codex/* branch)
  -> reviewer reviews                  (approve / return)                                    [acceptance-criteria check]
  -> guardian raises an AuthorityRequest -> escalates to the human via Site  [[authority-layer|authority gate]]
```

> ⚠ **Fail-legible note.** This framing is **not accepted doctrine.** The slice-1 doc opens by calling itself a "Working design, not accepted doctrine" that "graduates into v4.0 doctrine only *after* the slice actually runs, so that the doctrine is extracted from a real run rather than written ahead of one." It is the *aspirational* role of the FactoryOrder, distinct from the v3.9 contract that is actually operative. Do not cite it as the platform's settled position.

## As-built: the `work.FactoryOrder` Go type

Beyond the docs, an implementation exists and **diverges from the doctrinal field contract** — a gap worth naming. The following is sourced from Open Brain captures dated 2026-06-05 (work commits `a0a20d1` / `c2ff19f`, branch `feat/df-reunification-slice-1`), recorded as grounded against the real code:

- The type lives in `work/factory_order.go` as a `FactoryOrder` **input value** plus an `OrderKind` enum: `OrderSoftwarePR` (`software_pr`), `OrderGovernanceDeliberation` (`governance_deliberation`), and `OrderResearch` (`research`). **Only `software_pr` is wired**; the other two kinds exist as constants but are not exercised.
- A `SeedFactoryOrder` adapter maps an order onto a readiness-gated Work task.
- **Grounding correction recorded at the time:** `work`'s `validateTaskCreateOptions` (store.go) requires that when a `FactoryOrderID` is set, the task **also** carry a `Cell`, a `RiskClass`, at least one `RequirementID` (`req_` prefix), and at least one `AcceptanceCriterionID` (`ac_` prefix). The validator checks **prefix format only, not record existence** (`validateV39Reference`). So `SeedFactoryOrder` gained a `Cell` field (default `"implementation"`) and an `AcceptanceCriterionIDs` field, and **synthesises** `req_<suffix>` / `ac_<suffix>` from the order-ID suffix when those slices are empty (e.g. `fo_civic_roles -> req_civic_roles`, `ac_civic_roles`).

> ⚠ **Fail-legible note (doctrine vs as-built).** The doctrinal contract says the order "records source intent, requester, scope, constraints, release policy, risk class, and source references." The as-built `work.FactoryOrder` carries `OrderKind`, `Cell`, `RiskClass`, `RequirementIDs`, `AcceptanceCriterionIDs`, and (per later captures) `ExpectedOutputs` — and it **synthesises** requirement/criterion IDs from the order-ID stem when the caller omits them. The synthesis works in slice-1 *only because there is no existence check on those references* (an acknowledged shortcut, not a guarantee). The richer "scope / exclusions / release policy / source references" record described in doctrine is **not** evidenced as concrete struct fields by anything read this run. Treat the doctrinal field roster as the *intended* contract and the Go struct as the *current, narrower* reality. (The driving file `work/factory_order.go` was not opened directly in this compile — these facts come from the Open Brain capture, which states it was grounded against the code.)

### The order mechanism (CLI)

A separate capture (2026-06-07, verified against `cmd/hive/factory.go`) records how an order is actually launched:

- `hive factory order --spec <file.md> --human <name> --repo <path> [--id fo_...] [--store dsn]` reads the spec markdown as the order's **Intent**, derives an order ID `fo_<spec-filename-stem>`, and calls `work.SeedFactoryOrder{Kind: OrderSoftwarePR}`.
- `parseOrderGateSections` extracts **optional** `## Definition of Done` / `## Acceptance Criteria` / `## Test Plan` sections from the spec; **if absent, the Planner attaches them later.**
- The full governed path is four subcommands: `order` (seed) → society runs → `request-pr` (raises the draft-PR `AuthorityRequest`; the gate *holds by design*) → `create-pr` (the [[authority-layer|authorized]] live GitHub draft-PR creation, `GITHUB_TOKEN` from env with no fallback).

A deliberate design choice is recorded here: the order spec **omits** a detailed acceptance rubric *on purpose*, so that the rigor is supplied by the society's own strengthened Planner/Reviewer contracts rather than hand-fed by the human — the demonstration is meant to test whether the Planner attaches sufficient rigor *itself*.

## What the run actually showed (thin, and partly negative)

The slice-1 order has been run, and the captures are candid that it has **not yet fully succeeded** — important to record so the "unit of cooperation" framing is not read as already-proven:

- A 2026-06-08 run *did* drive `strategist -> planner -> implementer` to commit a multi-hundred-line artifact, and containment held (no escaped commits). But the artifact **failed the zero-blocker acceptance bar** and never reached the [[site|Gate-E]] approval surface — it over-enumerated roles and broke several acceptance criteria.
- A root-cause finding from that run: the **implementer Operated *blind* to its acceptance criteria** — the Operate instruction was built only from the task title and description, so the rigorous criteria the Planner attached reached the readiness gate and the reviewer but **never the producer**. This is a concrete instance of the order's contract not propagating where it was needed.

> ⚠ **Evidence is thin on the cooperative path.** As of the captures read here (through 2026-06-10), the FactoryOrder-as-unit-of-cooperation has been *exercised* but not *closed*: no run reported a clean pass through Gate-E to a real draft PR. The doctrinal `FactoryOrder -> ... -> certification` chain is specified; the lived end-to-end success is not yet evidenced in the sources read this run. Later captures (e.g. the 2026-06-09 deployment arc) treat "close slice 1" as still-pending work.

## How it relates to the rest of the system

- It is the **root that [[work|Work]] expands**: Work owns "FactoryOrder-to-Task operational flow," readiness, blocking, and repair — but Work is explicitly *flow, not truth*.
- Its durable record lives in the **[[event-graph|Event Graph]]**, the sovereign truth layer; the order is one of the provenance paths the `TraceCompletenessGate` later checks before certification.
- Its tasks execute only inside a **[[runtime-broker|RuntimeBroker]]** envelope that names the task provenance and authority decision.
- Protected actions reached while fulfilling an order (e.g. opening a real PR) require the **[[authority-layer|authority layer]]**: an `AuthorityRequest` → `AuthorityDecision` → `ExecutionReceipt` chain, fail-closed.
- In the reunification framing, the order is fulfilled by the civic roles of the **[[hive-governance|Hive]]**, with the human as the top authority tier approving through the **[[site|Site]]** console.
- Conceptually it descends from **[[the-20-primitives|the 20 primitives]]**: the orientation doc states that "explicit criteria become AcceptanceCriteria and gates," and the order is where source intent first becomes a typed, traceable node rather than a conversation.

## Sources & provenance

Compiled from:

- `Dark Factory - Motive, Goal, Approach.md` (orientation draft v0.1.5, created 2026-06-04, updated 2026-06-12) — the FactoryOrder definition (Description of Approach §§1–3), the `human intent -> FactoryOrder -> ...` top-level goal chain, Base Slice 0 flow, and the citation handle **DF-V3.9-SPEC-004:L38-L69 ("FactoryOrder contract and invariants")**. The cited v3.9 spec file itself was **not** read in this compile; its line range is reported via the orientation doc's summary.
- `dark-factory/reunification/2026-06-05-slice-1-first-reunified-order-design.md` (design v0.1.2, status: review, `canonical: false`) — the "order is the unit of cooperation" inversion and the civic-role cooperative flow. Self-labelled **"Working design, not accepted doctrine."**
- **Open Brain** thoughts (captured 2026-06-05 through 2026-06-10) for the as-built `work.FactoryOrder` struct, the `OrderKind` enum, the `SeedFactoryOrder` adapter and its `req_`/`ac_` synthesis, the `validateTaskCreateOptions` requirements, the `hive factory order` CLI mechanism (verified against `cmd/hive/factory.go`), and the 2026-06-08 run result (artifact failed the acceptance bar; implementer Operated blind to acceptance criteria). These describe code/runs grounded against the repos but the underlying Go files were **not** opened directly in this compile.

Durable external reference (from the citation table inside the orientation doc): the failure-tracing origin and the 20 primitives that motivate the order trace to **Matt Searles, "20 Primitives and a Late Night"** · `Searles-P1` · https://mattsearles2.substack.com/p/20-primitives-and-a-late-night.

`[[wikilinks]]` are forward references; several targets (e.g. `dark-factory`, `acceptance-criteria`) may not yet be compiled. **Conflicts surfaced, not resolved:** (1) the field roster is phrased two ways across the summary and the orientation doc — reconciled in "Note on the field list," not silently merged; (2) the doctrinal contract and the as-built Go struct describe different field sets — both stated. No source read this run proves the cooperative end-to-end run has closed.
