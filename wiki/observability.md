---
entity: Observability
aliases: [transparency contract, T1–T7, civilization transparency, dark-factory observability, fail-legible]
tier: architecture
status: compiled
last_compiled: "2026-06-17"
sources:
  - repos/docs/dark-factory/implementation/visualization/transparency-contract-v0.1.0.md  # T1–T7 spec, satisfaction map
  - repos/docs/dark-factory/implementation/visualization/observability-as-built-recon-v0.1.0.md  # as-built API inventory
  - repos/docs/dark-factory/implementation/visualization/site-observatory-phase3-plan.md  # phase 3 plan, observatory as Mission Control read view
  - repos/site/graph/observatory.go  # implementation of T1–T7 in Go
  - raw/transpara/dark-factory/implementation/overnight-2026-06-13-claude-checkpoint.md  # shift context, authorization scope
confidence:
  sources: primary
  claims: grounded
---

# Observability

**The transparency commitment that makes autonomous operation trustworthy.** In the [[dark-factory]] arc, observability is not instrumentation in the engineering sense — it is the architectural contract that defines what a human overseer *must be able to see* for the hive/civilization to count as transparently self-governing. It is a precondition for sanctioned autonomy, not a monitoring afterthought.

The contract has seven terms, designated T1–T7. A surface that satisfies T1–T7 is called a *projection*. The [[event-graph]] remains truth; projections are read-only views over it and over the telemetry services that consume it.

## The transparency contract

The contract was documented as `DF-TRANSPARENCY-CONTRACT v0.1.0` (2026-06-13) and derives strictly from two accepted specs: DF-SPEC-0002 (EventGraph kernel API) and DF-SPEC-0004 (authority policy model). It introduces no new vocabulary — record and outcome names used throughout are verbatim from those specs.

### T1 — Every authority decision is legible

For each protected action: the `AuthorityRequest` (actor, action, target, risk class, scope, justification, causal event IDs) and its `AuthorityDecision` (outcome, decider, rationale, conditions, expiry) must be paired by request ID in a single view. Outcomes display with their exact canonical names — `Autonomous`, `Notify`, `ApprovalRequired`, `Forbidden` — and with their fail-closed semantics: unknown or missing outcome maps to `ApprovalRequired` or `Forbidden`, never to a permissive default. Pending items under `ApprovalRequired` form a visible queue. The transparency surface displays decisions; it never makes them.

### T2 — Every agent's lifecycle is legible

Birth → trial → persistence → retirement state per agent, including: trial expiry (a trial agent without a visible expiry is a violation), authority scope, and current runtime state (iteration, last event, errors). Persistent production agents must be visibly distinguishable from trial agents.

### T3 — Spend is legible against its grant

Cost per agent and per civilization-day, always rendered *against the applicable cap* — daily cap from hive snapshots, grant posture from the deployment arc. A spend figure displayed without its cap is a contract violation. Token usage accompanies cost.

### T4 — Any outcome can be traced to its causes

From any rendered decision, task, or event: reach the full causal chain (EventGraph `Causes`/`Ancestors`; `CausalEventIDs` on authority records; `work.task.*` audit trail per task). Trace completeness is explicit — a missing causal link renders as a missing-link marker, never silently dropped or faded out.

### T5 — The record's integrity is visible

Chain length and verification status (`VerifyChain()`), event counts, and snapshot freshness (when telemetry was last written). A stale dashboard must say it is stale — the hive telemetry writer's 60-second safety tick exists for this purpose.

### T6 — Posture is never overstated

Gate chips carry their bounded scope verbatim. Candidate gates (v4.0 / Gate K / Gate L at time of writing) render the precise boundary: Gate K may show closed-for-pre-live while still warning that go-live/live-data revalidation is blocked; Gate L remains unsatisfied. Static program posture and live runtime data are visually distinct.

### T7 — Read-only by construction

The transparency surface performs **no writes**. It consumes GET-only egress APIs: [[work]] `/telemetry/*`, `/tasks/*`; hive-ops-api `/api/hive/operator-projection`. It must never call the one mutating telemetry endpoint (`POST /telemetry/phases/{phase}`) nor any `/op` grammar route. Every panel carries a provenance footer: which API, fetched when.

## The gap that defined Phase 3

The as-built recon executed 2026-06-12 night by a 5-agent parallel sweep across hive, eventgraph, work, agent, and site found:

> *"The metrics/trace pipeline already exists end-to-end; the visualization layer does not."*

Hive was writing telemetry snapshots to Postgres. Work was serving them over HTTP. Site was fetching them. But there were zero chart, SVG, or canvas primitives anywhere in site — and no surface rendered a causal chain. The T1–T7 gap column was "gap" across all six terms that had data and APIs.

This finding was the direct input to Phase 3 of the visualization implementation plan: build a Site read-only projection surface that closes the gap. Phase 3 was authorized by Michael Saucier as an autonomous overnight grant (2026-06-12) and shipped as [[the-observatory]].

## Satisfaction map (as of 2026-06-13/14)

| Term | Data exists? | Served by API? | Visualized? |
|---|---|---|---|
| T1 authority | yes (operator projection) | yes | yes — site#76/77 |
| T2 lifecycle | yes (projection + snapshots) | yes | yes — site#76/77 |
| T3 spend vs cap | yes (hive snapshots) | yes (`/telemetry/status`) | yes — site#76 |
| T4 traces | yes (Causes, task events) | partial (task events yes; ancestor walk is library-only) | partial — task trail only |
| T5 integrity | yes (chain, snapshots) | partial (chain length in snapshots; VerifyChain library-only) | yes (chain length/OK from snapshots) |
| T6 posture | yes (state proof docs) | n/a (static) | static strip only |
| T7 read-only | — | — | enforced by construction |

The residual T4 gap (EventGraph ancestor-walk traces) and the T6 live-posture gap are follow-up work. The EventGraph causal query API is library-only today — no HTTP egress endpoint exists — so full causal ancestor walks cannot be served to the observatory without a new DF-SPEC-0002 extension.

## Fail-legible, not blank

The contract introduces a principle not stated in the earlier specs: *fail-legible, not blank*. A surface that omits a panel when data is unavailable converts undrawable state into a false story. The required behavior is an explicit "unavailable — reason" block with the attempted endpoint. The [[the-observatory]] implementation generalizes this: every withheld visual states its real reason.

The engineering realization of this principle is the nil-as-pointer pattern. Every scalar in `ObsVitals` and related structs is decoded as a Go pointer:

```go
type ObsVitals struct {
    ActiveAgents *int     `json:"active_agents"`
    ChainOK      *bool    `json:"chain_ok"`
    DailyCost    *float64 `json:"daily_cost"`
    DailyCap     *float64 `json:"daily_cap"`
    // ...
}
```

A nil pointer means the feeder omitted the field. It renders as "—" or "unknown". It never propagates as 0, false, or "no cost." The distinction between "field is zero" and "field is absent" is structurally enforced, not tested by convention.

## The vocabulary allowlist

T1 requires that authority outcomes render with their exact canonical names and that the surface not accept feeder-supplied strings outside that vocabulary. The implementation encodes this as an allowlist rather than a denylist:

```go
var authorityOutcomes = map[string]bool{
    "Autonomous":       true,
    "Notify":           true,
    "ApprovalRequired": true,
    "Forbidden":        true,
}
```

Any outcome not in this map is flagged as non-canonical. This is the standard fail-closed pattern from the arc's security standards: allowlist what is permitted; denylist silently permits everything you forgot and every value added later.

## What observability is not

The contract is careful about scope:

- The transparency surface is a **projection**. The [[event-graph]] remains truth. The surface never supersedes it, amends it, or substitutes for it.
- Visibility of an authority decision is **not** a decision. The surface displays; it never approves, denies, or routes governed actions.
- `CanOperate` (the tri-state capability flag visible in the civilization assembly view) is **not** bootstrap registry membership and **not** an authority grant. It is a posture projection.
- Model Selection Mode (`Auto`/`Manual`) is **not** a model-policy mutation. The observatory makes it inspectable; it cannot change it.

## Phase 3 as Mission Control

The Phase 3 plan names the observatory the "Mission Control read view" — the human oversight surface for a civilization that otherwise operates autonomously. The analogy is precise: a mission control room does not fly the spacecraft. It provides the full situational picture — vitals, spend, agent state, authority decisions, causal traces, live event stream — so that a human operator can monitor, intervene, or authorize the next action. The observatory is that room.

The overnight checkpoint (2026-06-13) summarizes the arc concisely: the goal was "a completely autonomous hive/civilization which self-governs and emits a transparent set of metrics and traces that can be visualized by a component that you write." Observability is the half of that goal that makes autonomy trustworthy rather than opaque.

> ⚠ **Thin-evidence note (T4 completeness).** The current observatory delivers per-task audit trails via `GET /tasks/{id}/events` but cannot walk the full EventGraph causal DAG (`Ancestors`/`Descendants`) because those queries are library-only — no HTTP egress endpoint exists. T4 is therefore partially satisfied. The Phase 3 plan records extending traces as follow-up work contingent on an EventGraph API extension under DF-SPEC-0002.

> ⚠ **Thin-evidence note (T5 VerifyChain).** Chain length and chain-OK are served via hive snapshots and are visible in the observatory. Full `VerifyChain()` execution is library-only. The observatory shows what the last telemetry write recorded, not an on-demand verification.

## Related

[[the-observatory]] · [[site]] · [[work]] · [[hive-governance]] · [[event-graph]] · [[authority-layer]]

## Sources & provenance

- `/Transpara/transpara-ai/repos/docs/dark-factory/implementation/visualization/transparency-contract-v0.1.0.md` lines 1–70 — canonical T1–T7 definitions, satisfaction map (as of 2026-06-13, pre-observatory), and the "projection / EventGraph remains truth" framing.
- `/Transpara/transpara-ai/repos/docs/dark-factory/implementation/visualization/observability-as-built-recon-v0.1.0.md` lines 1–84 — as-built metrics/trace/API inventory; the "zero visualization" finding that defined Phase 3; API-first deviation catalog; "where the visualization belongs" decision.
- `/Transpara/transpara-ai/repos/docs/dark-factory/implementation/visualization/site-observatory-phase3-plan.md` lines 1–70 — Phase 3 as Mission Control read view; data contract table; guardrail list; satisfaction status per slice.
- `/Transpara/transpara-ai/repos/site/graph/observatory.go` lines 97–106, 249–258 — `ObsVitals` pointer-typed struct; `authorityOutcomes` allowlist; nil rendering helpers (`obsInt`, `obsMoney`, `obsScore`, `obsIntPair`).
- `raw/transpara/dark-factory/implementation/overnight-2026-06-13-claude-checkpoint.md` lines 1–57 — authorization scope, overnight grant wording, TL;DR of the shift.

**Conflicts stated:** T4 and T5 satisfaction is partial — stated explicitly in the satisfaction map and in the fail-legible notes above. The contract pre-dates the observatory; the satisfaction column reflects the state after site#76/77 merged.
