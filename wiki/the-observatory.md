---
entity: The Observatory
aliases: [observatory, ops/observatory, civilization transparency surface, mission control read view]
tier: architecture
status: compiled
last_compiled: "2026-06-17"
sources:
  - repos/site/graph/observatory.go  # full implementation, lines 1–1063
  - repos/docs/dark-factory/implementation/visualization/site-observatory-phase3-plan.md  # route, slice plan, guardrails
  - repos/docs/dark-factory/implementation/visualization/transparency-contract-v0.1.0.md  # T1–T7 definitions
  - repos/docs/dark-factory/implementation/visualization/observability-as-built-recon-v0.1.0.md  # as-built API inventory
  - raw/transpara/dark-factory/implementation/overnight-2026-06-13-claude-checkpoint.md  # merge record, review convergence
confidence:
  sources: primary
  claims: grounded
---

# The Observatory

**The read-only civilization transparency surface.** The Observatory is the `/ops/observatory` route in [[site]] — a single tab inside the existing `/ops` operator shell that renders the live state of the [[hive-governance|hive]] and its agents for human oversight. It consumes egress APIs only, performs no writes, and is designed around a single engineering principle stated directly in the source code:

> *"Fail-open is the enemy here: an omitted JSON field must never render as a fact (0, false, 'no cost')."*

It shipped in two merged PRs on 2026-06-13/14: `transpara-ai/site#76` (SVG renderers + seven read-only panels, review-approved after three rounds of adversarial review) and `transpara-ai/site#77` (SSE live event pulse, civilization assembly view, model-selection-mode provenance, tri-state `CanOperate`). The surface is the concrete answer to the [[observability|Transparency Contract]] T1–T7 gap that the as-built recon documented: a metrics and trace pipeline that ran end-to-end but had zero visualization anywhere in the stack.

## What it shows

The Observatory renders seven panel groups, each backed by an explicit feeder API and carrying a provenance footer (feeder base, path, fetch timestamp, snapshot age). Unavailable data renders as an explicit "unavailable — reason" block, never silently as zero or blank.

**Civilization vitals (T5).** Chain length, chain-OK status, active agents, total actors, event rate, severity. All scalars are decoded as Go pointers (`*int`, `*int64`, `*bool`, `*float64`); nil renders as "unknown" or "—", never as zero. Chain integrity is stated loudly; absence renders as "not reported — treat as unverified."

**Spend vs cap (T3).** A gauge SVG drawn against the daily cap from hive snapshots. The gauge is withheld — with the true stated reason — whenever cost or cap is absent, negative, or non-positive. A present cap of ≤ 0 must not be reported as "cap unknown" (this was a specific review finding). The go logic in `buildObsSpend` returns an `ObsSpend` struct with exactly one of `{GaugeSVG+Text}` or `{Reason}` populated — the two branches cannot co-exist.

**Agent roster + 24-hour state timelines (T2).** One row per active agent, ordered by role then actor ID. Each row carries role, actor ID, state, model, iteration pair (n/m with "?" for absent halves), tokens, cost, trust score, errors, last event timestamp, and a 24-hour state-timeline SVG strip. Absent scalars render as "—"/"unknown"; the string "0" is never fabricated from a nil pointer.

**Pipeline phase costs.** Per-phase cost bars rendered as SVG. Withheld with explicit reason when phases are absent, when any cost is negative, or when the SVG renderer declines a non-zero series.

**Authority queue and decisions (T1).** Pending approvals, decided authority records, and actor lifecycle pulled from the hive operator projection (`GET /api/hive/operator-projection`). Outcomes are rendered with their exact canonical names — `Autonomous`, `Notify`, `ApprovalRequired`, `Forbidden` — and only those four. Any non-canonical value is flagged as such (see `authorityOutcomes` allowlist in observatory.go:249–258). The surface displays; it never decides.

**Causal trace explorer (T4).** On-demand per-task event chains via `GET /tasks/{id}/events`, triggered by a `?task=` query parameter. Task IDs are validated against an allowlist pattern (`^[A-Za-z0-9_.:-]{1,128}$`) before any request is built. The feeder response must echo the exact requested task ID back; an empty echo or a mismatch returns an explicit error — "feeder response did not echo a task id — trail unverifiable, withheld" — not a silently incorrect trace. Events render as a causal staircase SVG.

**Live event pulse (T5).** A Site-authenticated SSE proxy at `/ops/observatory/events` that connects server-side to [[work]]'s `GET /telemetry/sse` with a Work bearer token and exposes only the Site route to the browser. The upstream handshake is bounded by a 5-second response-header timeout; the body stream is deliberately left open for the browser's `EventSource`. Lines are forwarded if and only if they start with one of the standard SSE prefixes (`data:`, `id:`, `retry:`, `:`) or are blank separators — all other lines are dropped.

**Civilization assembly.** Role and agent topology derived from Work runtime telemetry, Hive lifecycle/model projection, and a Site fallback snapshot of the Hive bootstrap role registry. Four organization tiers (A: bootstrap/foundation, B: organic emergence, C: business operations, D: self-governance) with per-tier evidence labels. Model Selection Mode and provenance (explicit / override / default / inferred / not projected) are visible per role and globally. `CanOperate` is a tri-state capability flag (true / false / not projected), not a bootstrap-membership assertion.

## Read-only by construction

The Observatory has no POST handlers, no forms, and no calls to any write endpoint. The one mutating endpoint on the telemetry surface — `POST /telemetry/phases/{phase}` — must never be called from here. All fetches go through `obsGetJSON`, a single bounded HTTP client path with a 5-second timeout, Work bearer auth, and explicit error handling. Every panel explicitly states when its feeder is unavailable rather than falling through to a zero-state story.

The description string in the handler is the canonical summary of this constraint:

> *"Projection only — EventGraph remains truth; decisions happen on governed surfaces."*

## APIs consumed

Three [[work]] telemetry endpoints and one [[hive-governance|hive]] operator projection endpoint cover all panels:

| Endpoint | Panel |
|---|---|
| `GET /telemetry/status` | Vitals, spend vs cap |
| `GET /telemetry/agents/history?window=24h` | Agent roster, timeline strips |
| `GET /tasks/{id}/events` | Trace explorer |
| `GET /telemetry/sse` | Live event pulse (via Site SSE proxy) |
| `GET /api/hive/operator-projection` | Authority, lifecycle, civilization assembly |

The hive operator projection aggregates pending approvals, authority decisions, lifecycle state, and key audit traces in a single Bearer-protected read-only call. The Site fallback snapshot of Hive bootstrap role definitions (`obsStarterRoles`) is used when the projection is unavailable — with an explicit finding noting that only bootstrap definitions are visible and runtime activity is withheld.

## Engineering constraints inherited from the transparency contract

The implementation binds the nine visualization principles from the Phase 3 plan. The most operationally significant:

- **No color-only meaning.** Every SVG embeds `<title>` elements; every panel repeats values as text alongside the visual. This satisfies the air-gap and accessibility requirement that data survives without SVG rendering.
- **Static posture strip.** Gate K and L chips render bounded status, not a blanket success claim: Gate K can show closed-for-pre-live with go-live revalidation still blocked, while Gate L remains candidate/unsatisfied. The observatory shows intended posture without asserting production readiness.
- **Verbatim outcome names.** `Autonomous`/`Notify`/`ApprovalRequired`/`Forbidden` are rendered exactly as the DF-SPEC-0004 vocabulary specifies them, never paraphrased.
- **Provenance on everything.** The feeder base URL, endpoint path, and fetch timestamp appear on every panel.

## Implementation facts

- **Language / rendering:** Pure Go + templ + Tailwind + HTMX polling. SVGs are generated by the `graph/svgviz` pure-Go package (gauge, sparkline, bar chart, causal staircase), adding no new JavaScript dependencies and maintaining the air-gap posture.
- **HTTP clients:** Two separate clients — `obsWorkClient` (5-second full timeout for panel fetches) and `obsSSEClient` (dial/TLS/header bounded, body unbounded for the live stream).
- **Review record:** site#76 went through three rounds of adversarial review — 8 findings in round 1, 2 in round 2, approve in round 3. The core lesson: fail-closed must hold at every boundary, including the decode layer, not just the render layer.
- **Residual follow-up:** Last-Event-ID semantics, freshness alarms, state resync, replacing Site fallback role snapshots with live Hive-projected definitions, and ancestor-walk traces (eventgraph causal queries are library-only today — no HTTP endpoint exists yet).

> ⚠ **Thin-evidence note (civilization assembly tiers B–D).** Org levels B (organic emergence), C (business operations), and D (self-governance) are rendered with "not projected" status in the current implementation. The tier taxonomy exists and the code handles emergent roles that appear through Hive lifecycle projection, but no current projection evidence places any role in tiers C or D. The observatory correctly reflects this absence rather than inferring tier membership.

## Related

[[observability]] · [[site]] · [[work]] · [[hive-governance]] · [[event-graph]] · [[authority-layer]]

## Sources & provenance

- `/Transpara/transpara-ai/repos/site/graph/observatory.go` lines 1–1063 — full implementation: `OpsObservatoryData` struct, `handleOpsObservatory`, `buildObsSpend`, `fetchObservatoryTrace`, `buildObsCivilization`, `obsForwardableSSELine`, `phaseCostBars`, and all helper renderers. Primary source — all claims about pointer-type decoding, allowlists, SSE proxy logic, and authority outcome vocabulary are verified against this file.
- `/Transpara/transpara-ai/repos/docs/dark-factory/implementation/visualization/site-observatory-phase3-plan.md` lines 1–70 — route definition, data contract table, guardrail list, slice plan with PR head SHAs and merge SHAs.
- `/Transpara/transpara-ai/repos/docs/dark-factory/implementation/visualization/transparency-contract-v0.1.0.md` lines 1–70 — T1–T7 contract terms and satisfaction map.
- `/Transpara/transpara-ai/repos/docs/dark-factory/implementation/visualization/observability-as-built-recon-v0.1.0.md` lines 1–84 — as-built metrics/trace/API inventory; the "zero visualization" finding that motivated the component.
- `raw/transpara/dark-factory/implementation/overnight-2026-06-13-claude-checkpoint.md` lines 1–57 — review convergence record, open decisions, merge state (site#76 approved, site#77 merged).
