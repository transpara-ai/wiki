---
entity: Site (Operator Console)
aliases: [site, the operator console, the governed console, the Site console, Gate-E surface, the society view]
tier: architecture
status: compiled
last_compiled: 2026-06-14
sources:
  - raw/transpara/dark-factory/Dark Factory - Motive, Goal, Approach.md  # §"Use Work for Flow", responsibility map, decision register B (Site = Selected operator console)
  - raw/transpara/dark-factory/reunification/2026-06-05-slice-1-first-reunified-order-design.md  # §3 membrane, §5 what you see, repo impact map, success criteria (Site = Gate-E + society-view, effect=none)
  - raw/transpara/dark-factory/reunification/2026-06-09-deployment-arc.md  # site as-built row, pillar scorecard, Phase 4/6, "Site drifts toward executor" risk
  - Open Brain (transpara-ai/site PR reviews + reunification + as-built captures, 2026-05-31 .. 2026-06-12)  # PR/commit-level provenance for the claims below
confidence:
  console_only_boundary: high (stated as a normative constraint in all three docs; PR #62 review records the proof-of-negatives test)
  live_visualization: contested / mostly aspirational — the live animated "society building the order" view is named as the destination (Phase 6) but the first-party Site runtime ships no streaming consumer as of 2026-06-13; see "What is and isn't built"
  deployed_and_useful_today: thin / negative — Open Brain (2026-06-09) records the live deployment renders the society/projection views EMPTY because the hive projection API is unconfigured
---

# Site (Operator Console)

**Site is the human window into the Dark Factory, by construction read-only.** It is one of the seven `transpara-ai` repos named as Dark Factory's native systems, classed as the **Selected operator console** ("UI/console") in the responsibility map of *Dark Factory - Motive, Goal, Approach* (DF-MOTIVE-GOAL-APPROACH, v0.1.5). Its job is to surface evidence to operators: projections of factory state, the authority/approval queue, the proof-of-work display, and — as the [[the-reunification]] arc matured — a live "society building the order" visualization. Its defining property is a boundary, not a feature: **Site must not execute work, and must never become a truth or authority source.** Truth lives in [[event-graph]]; authority is evaluated by [[hive-governance]]; Site only shows.

The entity's recent shape was set on **2026-06-05**, when the Slice-1 reunification design pulled Site into the first reunified order with a deliberately bounded blast radius (two seams: forward a human approval as a governed decision, and render the order trace). Earlier, on **2026-05-31**, the underlying Gate-E decision surface (`site#62`) had already been built and reviewed against the boundary. The live-visualization ambition was formalized later, as Phase 6 of the **2026-06-09** deployment arc, and a first SVG slice (`site#76`, the "civilization observatory") opened on **2026-06-12**.

## What Site is for (the four surfaces)

The Motive/Goal/Approach doc gives the one-line charter: *"Humans need evidence surfaces and authority queues."* Concretely the corpus names four console surfaces:

- **Evidence views** — operator projections of factory state and the causal chain, read off the event store. (`/ops/evidence` exists today per the deployment-arc as-built row.)
- **The authority/approval queue (the Gate-E decision surface)** — pending [[authority-request]]s that escalate to the human for approve / deny / request-more-evidence.
- **Proof-of-work display** — the proof-of-work packet / audit views (`/ops/evidence`), packaging work item, runtime invocation, changed files, tests, CI status, review feedback, and EventGraph references for human review.
- **The "society building the order" visualization** — the role-timeline view showing which civic role did what, the antidote to the abandoned "ten forensic tiers" design (reunification Slice-1 §5).

## The boundary: console only, fail-closed (`effect=none`)

This is the load-bearing claim and every source asserts it as a **constraint, not an aspiration**:

> "Site shows evidence to operators." … "Console only; not executor, truth source, or authority source." — DF-MOTIVE-GOAL-APPROACH, responsibility map and decision register B

The reunification design states the doctrine by name — *"Site is console, not executor or truth"* — and spells out the mechanism: Site renders the authority request and captures the human's decision, then **forwards it as a governed decision event with `effect=none` preserved**. Site does *not* assemble policy evidence and does *not* perform the GitHub mutation. The [[hive-governance]] orchestrator assembles the Epic 11 authority/policy evidence; [[work]]'s fail-closed Epic 11 creator performs the single mutation, only after an `AuthorityDecision`, and only after GitHub confirms (then emits the `ExecutionReceipt`).

**How `effect=none` is enforced in code (grounded, from the `site#62` review captured 2026-05-31):** the Gate-E surface is a GET-only `/ops/decision` route; `OpsDecisionData.Effect` is a hardcoded `"none"` struct literal with no alternate assignment anywhere; tests construct the handlers with `NewHandlers(nil,nil,nil)` — no Work/Hive/EventGraph backends — so there is no code path to an executor. The action vocabulary is allowlisted to exactly `approve` / `deny` / `request-more-evidence`; anything else fails closed. Critically, the no-mutation invariant is proven by **absence-assertions** — a test scopes to the rendered decision region and asserts the absence of `<form>`/`<button>`/`method="post"`/`hx-post|put|patch|delete` and of executor labels (Merge PR / Deploy / Access secret / Activate capability / Execute work). When the approval-forward POST seam was later added (`site#76`-era work, commit `2289ffd`, 2026-06-05), this invariant was deliberately **narrowed from a denylist to an allowlist** — every `action=`/`formaction=` must equal `/ops/decision` — so "Site is a console" is robust against *novel* executor controls, not just known-bad strings. This is the same fail-closed/allowlist discipline the arc demands platform-wide.

> Fail-legible note — a real bug here, caught in review (2026-06-05): the decision `<form>` emitted `value=approve|deny` while the handler switched on `approved|denied`, so a real Approve/Deny click fell through to local handling and **never reached hive**. Two string literals that had to agree across files drifted. Fixed with shared constants plus a round-trip drift-guard test. The boundary held (`effect=none` throughout), but the *function* was silently broken — a reminder that "console-only" proofs (negatives) and "the console actually works" proofs (positives) are different obligations.

The deployment arc carries this forward as a standing risk — **"Site drifts toward executor"** as interaction verbs grow (Phase 4: unified queue, intake, steering, notifications) — with the mitigation that *every* new verb forwards a governed decision with `effect=none` at the Site boundary, guarded in review on every Site packet. The forbidden-patterns block states it flatly: *"Do not let Site execute work or assemble policy evidence (effect=none forever)."*

## The "society building the order" view

The fifth of the reunification's **five inversions** is *"the visualization shows the society building the order"* — which role did what — replacing the abstract forensic tiers. In Slice 1 this is a **role-timeline trace** rendered in the Site console (`site/graph/views.templ`): the run's event chain grouped by civic role, showing the order move **strategist → planner → implementer → reviewer → guardian → human (Site approval) → draft PR**, evidence annotated at each hop, queried from the event store. The Slice-1 design calls this *"the first real version of the replacement visualization … rendered on real Slice 1 run data rather than an abstract redesign."*

It shipped (`site#73`, commit `6d8f6b9`) as the default `/ops/evidence` panel (`opsRoleTimeline`, "Society view"), built by `buildOpsRoleTimeline` from the hive operator-projection. The deployment arc is explicit that as of 2026-06-09 it is a **static render**, not animated; Phase 6 ("Live animated graphics") is where it becomes live.

## What is and isn't built (fail-legible as-built)

The deployment arc's own as-built review (2026-06-09) is the authoritative status, and it is candid about the gap between charter and reality:

| Surface | Built today | Not yet |
|---|---|---|
| Gate-E decision surface | Yes — `site#62`, `effect=none`; real request + governance POST forward (`site#73`/`2289ffd`) | Unified pending-decisions queue across hive+work (Phase 4) |
| Model-policy projection + controls | Yes — `site#74`/`#75` | — |
| Proof-of-work / audit views | Yes — `/ops/evidence` | — |
| Society view (role timeline) | Yes, but **static render** (`site#73`) | Live/animated (Phase 6) |
| Live factory visualization | **No** | EventSource/WebSocket consumer, canvas/d3/SVG live renderer |

The single most important fail-legible fact, stated verbatim in the arc's `site` as-built row:

> "**No first-party Site application-runtime code … opens EventSource/WebSocket connections or renders a live factory visualization with canvas, d3, or SVG** — polling and page-load reads only." (The pinned `third_party/hive` submodule is excluded from that claim.)

So the live, animated, evidence-anchored visualization in this entity's one-line description is **the destination, not the current state.** Two independent Open Brain assessments (2026-06-09) reinforce this and add detail the docs do not:

- **There is no streaming in first-party Site.** Liveness is HTMX polling (`every 5s/15s`) on `/hive` only; the `/ops` society + projection views are **not even polled** — one-shot render per page load. (The working SSE stream lives on `work-server`, a *different* binary: `GET /events/subscribe` / `/telemetry/sse`. Phase 6's first task is to make Site consume it.)
- **The deployed instance renders the society view EMPTY.** On the live box (nucbuntu, systemd `site.service`), `HIVE_OPS_API_BASE_URL` is unset, so the role-timeline and projection panels render their empty state ("Configure HIVE_OPS_API_BASE_URL"); the public `/hive` falls back to a stale (`May 10`) loop snapshot. The scaffolding is roughly 70% built; it is **not live**.
- **The UI is ahead of the runtime.** The named blocker to a live spectator view is not the viewer — it is the civilization reliably doing watchable work (Slice-1 findings F7/F8: single runs don't converge; the review→fix loop strands after a restart). *This is an Open Brain assessment, not a doc claim, and is labeled thin accordingly.*

A first step toward the live view did open on **2026-06-12**: `site#76` (`feat/civilization-observatory`, **not merged**) adds a pure-stdlib `graph/svgviz` package (server-rendered SVG: gauge / bars / span-strip / causal-staircase, fail-closed on undrawable input, HTML-escaping all labels, allowlisted state classes) and a `GET /ops/observatory` surface — still read-only, still `effect=none`, still server-rendered (no client stream). This is Slice 1 of the visualization plan's Phase 3, authorized by a 2026-06-12 overnight authorization. The choice of server-rendered SVG over a JS rendering library is consistent with the arc's Phase 6 rule that *"the rendering approach … gets a crosswalk entry and packet before code."*

## The visualization design kit (separate from Site)

Distinct from the Site runtime, the [[dark-factory]] `docs` repo holds a **static** Evidence Console design kit: ten specified views over three *fictional* runs (PR `docs#100`/`#102`, "console-complete" checkpoint 2026-06-04; `dark-factory/implementation/visualization/`). Open Brain is explicit that this is *"a STATIC architectural explainer … Not live (the 'live:' flag is a routing flag) … the design kit … for a future live /ops surface, NOT a live viewer."* The deployment arc plans to **port** these ten views into a read-only Site surface in Phase 6, live-bound where evidence exists and **fail-legible where it does not** (missing links render as missing, never blank). The design kit's binding principles — *no unscoped green checkmark, candidate content visibly distinct from accepted, missing evidence drawn as voids, read-only by construction* — are inherited by any Site visualization.

## How Site fits the layered model

The Motive/Goal/Approach doc's one-sentence architecture places Site precisely: *"EventGraph is the sovereign truth layer. Work schedules and coordinates production. Hive or governance evaluates authority. RuntimeBroker confines execution. **Site shows evidence to operators.** Memory and knowledge advise but do not govern."* Site is therefore downstream of everything and authoritative over nothing — it reads projections, it forwards decisions, it renders the chain. Its review-question in the doc is a guardrail aimed squarely at this entity: *"Does it accidentally grant authority to Work, Site, Hive, memory, Git, CI, or external tools?"* — the answer for Site must always be no.

## Cross-links

- [[event-graph]] — the sovereign truth Site reads but never writes.
- [[hive-governance]] — evaluates authority; assembles the Epic 11 evidence Site refuses to assemble; serves the operator-projection Site renders.
- [[work]] — owns the Work DAG and the fail-closed Epic 11 draft-PR creator that performs the mutation Site forwards approval for.
- [[authority-request]] / authority decision / [[execution-receipt]] — the governed-decision chain Site sits on the *display + forward* side of.
- proof-of-work packet — the human-review evidence Site displays.
- [[the-reunification]] — the workstream that pulled Site into the first reunified order; the five inversions; inversion #5 is Site's society view.
- [[deployment-arc]] — Phases 4 (interaction), 5 (observability), 6 (live graphics) are Site's roadmap.
- [[gates]] — Gate E is the decision surface Site renders.

## Run-3 update (2026-06-14)

Two PRs shipped on 2026-06-13 that together deliver the observatory — the first real instance of the Gate-E "society view" transparency surface described in the deployment arc and the transparency contract (DF-TRANSPARENCY-CONTRACT v0.1.0).

**site#76 — civilization observatory, slice 1 (`/ops/observatory`).** A new route `GET /ops/observatory` adds a read-only transparency surface satisfying the Civilization Transparency Contract terms T1–T7 (authority decisions, agent lifecycle, spend-vs-cap, causal traces, chain integrity, posture legibility, read-only construction). Implementation details of note:

- **`graph/svgviz`**: new pure-stdlib server-rendered SVG package (gauge, bars, span-strip, causal staircase). Every renderer fails **closed** on undrawable input — unknown cap, negative/NaN values, empty series — and emits an explicit unavailable block rather than a misleading visual. Unknown agent state kinds render the explicit `viz-unknown` CSS class (allowlisted, not fallback styling). All feeder-supplied labels are HTML-escaped.
- **Presence-aware decode**: every feeder scalar in vitals and agent snapshots is a pointer; an omitted JSON field renders as `not reported` / `—` / `unknown`, never as `0` / `false` facts. The transparency contract's own words apply: **"Fail-open is the enemy here: an omitted JSON field must never render as a fact."**
- **Read-only by construction**: GET handlers only; consumes `work /telemetry/status`, `/telemetry/agents/history?window=24h`, `/telemetry/sse` (SSE not consumed in slice 1 — see site#77), and the hive operator projection. No new write paths; `effect=none` invariant preserved throughout. Zero new third-party dependencies.
- **Allowlisted decision outcomes**: authority-decision outcome chips validate against the canonical DF-SPEC-0004 vocabulary (`Autonomous` / `Notify` / `ApprovalRequired` / `Forbidden`); non-canonical values render explicitly as non-canonical, not silently mapped or suppressed.
- **Bounded work-API fetches**: all work-API fetches in the `graph` package now use a bounded 5-second client (`obsWorkClient`); a hung feeder renders unavailable panels instead of hanging `/ops` pages.
- **Task ID allowlist**: task IDs are allowlist-validated (`^[A-Za-z0-9_.:-]{1,128}$`) before any outbound request is built; the feeder's task-id echo is verified against the requested ID (an empty echo is treated as unverifiable and the trail is withheld — fail-closed, not fail-open).

**site#77 — live pulse and civilization assembly.** Extends the observatory with two additions: (1) a **live event pulse** wired to the work-server SSE stream (`/telemetry/sse`), making the observatory a streaming consumer for the first time in first-party Site; and (2) a **civilization assembly panel** exposing the full agent-role roster as assembled by the hive, with model-mode inference and projection provenance. This is the first time first-party Site opens an `EventSource` connection — the gap noted in the 2026-06-09 as-built review ("no first-party Site EventSource/WebSocket") is now closed for the observatory surface.

**Status correction (as of 2026-06-14).** The "What is and isn't built" table below should be read with the following updates applied: the observatory (`/ops/observatory`) is now **merged and live** (not `not merged` as of the 2026-06-12 snapshot); first-party Site **does** now consume SSE (in the observatory surface only); the live pulse and civilization assembly panels are included. The `site#76`/`site#77` entry in the table replaces the earlier "not merged" note.

| Surface | Status (2026-06-14) |
|---|---|
| Gate-E decision surface | Yes — `site#62`, `effect=none`; real request + governance POST forward (`site#73`) |
| Model-policy projection + controls | Yes — `site#74`/`#75` |
| Proof-of-work / audit views | Yes — `/ops/evidence` |
| Society view (role timeline) | Yes, static render (`site#73`) |
| Observatory (`/ops/observatory`) | **Yes, merged** — `site#76`/`#77`; read-only; SSE pulse; civilization assembly |
| Full live/animated visualization | No — Phase 6 work outstanding |

## Sources & provenance

Compiled this run from:

- **`Dark Factory - Motive, Goal, Approach.md`** (DF-MOTIVE-GOAL-APPROACH, v0.1.5, updated 2026-06-12) — §"Use Work for Flow, not Truth" (the layer sentence), the Repository and System Responsibility Map ("Console only; not executor, truth source, or authority source"), Decision Register B ("Site … Selected operator console … Site must not execute work or become truth/authority"), and the Review Questions guardrail. No external durable URL — this is a first-party `transpara-ai/docs` source document.
- **`reunification/2026-06-05-slice-1-first-reunified-order-design.md`** (DF-REUNIFY-2026-06-05-SLICE-1-DESIGN, v0.1.2) — inversion #5; §3 (the authority gate, `effect=none`, Site forwards a governed decision and "stays a pure console"; Hive assembles evidence, Work mutates); §5 (the role-timeline "society building the order" view); the repo impact map and success criteria.
- **`reunification/2026-06-09-deployment-arc.md`** (DF-REUNIFY-2026-06-09-DEPLOYMENT-ARC, v0.1.4) — the `site` as-built row (Gate-E `effect=none`; static society view; the verbatim "no first-party Site … EventSource/WebSocket … live visualization" finding), the pillar scorecard, Phase 4 and Phase 6, and the "Site drifts toward executor" risk + the `effect=none` forbidden-pattern.
- **Open Brain captures** (transpara-ai/site, 2026-05-31 .. 2026-06-12), used for PR/commit-level provenance and as-built status that the docs summarize but do not enumerate: the `site#62` Gate-E review (GET-only, hardcoded `effect=none`, absence-assertion tests; 2026-05-31); the Slice-1 seam validation and the approve/deny constant-drift bug + allowlist narrowing (commit `2289ffd`, 2026-06-05); the 2026-06-09 spectator-UI assessment (no SSE in first-party Site; `HIVE_OPS_API_BASE_URL` unset → empty society view; stale loop snapshot; "the UI is ahead of the runtime"); and the `site#76` civilization-observatory SVG slice (2026-06-12, not merged). Open Brain claims about deployment liveness and the runtime-is-the-blocker conclusion are labeled thin/negative in the body because they are operator assessments, not accepted doctrine.

- **`site#76` commit `0dd73b5` (2026-06-13, merged)** — civilization observatory implementation in `graph/observatory.go`, `graph/svgviz/svgviz.go`, `graph/svgviz/svgviz_test.go`; GET-only `/ops/observatory` route; transparency contract T1–T7; adversarial review rounds r1/r2 (closed fail-open findings including presence-aware decode, task-id echo verification, renderer refusal wording, bounded HTTP client).
- **`site#77` commit `6554f71` (2026-06-13, merged)** — live event pulse (SSE consumer) and civilization assembly panel added to observatory (`graph/observatory.go`, `graph/observatory.templ`).
- **`transparency-contract-v0.1.0.md`** (`transpara-ai/docs: dark-factory/implementation/visualization/`, DF-TRANSPARENCY-CONTRACT v0.1.0, 2026-06-13, `status: draft`, `canonical: false`) — the T1–T7 terms the observatory is built against; satisfaction map as of 2026-06-13; the "fail-open is the enemy" principle quoted in the Run-3 section. Local read path: `/Transpara/transpara-ai/data/repos/docs/dark-factory/implementation/visualization/transparency-contract-v0.1.0.md`.

Durable Searles URLs are not cited here: this is an architecture/arc entity whose claims trace to the first-party dark-factory docs and to Open Brain, not to the Searles philosophy corpus. `[[wikilinks]]` are forward references; most target articles are not yet compiled.
