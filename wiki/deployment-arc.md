---
entity: The Deployment Arc
aliases: [deployment arc, DF deployment arc, arc from Slice 1 to operated factory]
tier: arc
status: compiled
last_compiled: "2026-06-17"
sources:
  - docs/dark-factory/reunification/2026-06-09-deployment-arc.md  # DF-REUNIFY-2026-06-09-DEPLOYMENT-ARC v0.1.4 — arc structure, as-built review, phases, pillar scorecard
  - docs/dark-factory/reunification/2026-06-10-deployment-arc-execution-plan.md  # DF-REUNIFY-2026-06-10-DEPLOYMENT-ARC-EXECUTION v0.5.0 — execution model, packet register, conductor kickoff
  - docs/dark-factory/reunification/2026-06-11-arc-state.md  # DF-REUNIFY-2026-06-11-ARC-STATE v0.2.0 — Slice 1 round 4 state as of 2026-06-11
  - raw/transpara/dark-factory/implementation/overnight-2026-06-13-claude-checkpoint.md  # DF-CKPT-20260613-OVERNIGHT-CLAUDE v1.0.0 — observatory overnight shift, Phase 3 pre-work
confidence:
  sources: primary
  claims: grounded
---

# The Deployment Arc

**The program plan that takes the civilization from local scratch-space runs to a continuously operated production factory.** Drafted 2026-06-09 as a planning document inside the [[the-reunification|reunification workstream]], the Deployment Arc is the path from "mid-Slice-1 on a per-session local database" to a state where all eight destination criteria hold simultaneously on an installed system. It is `authority: planning`, `canonical: false`: it authorizes no implementation, advances no gate, and grants no autonomy level — each of its eight phases requires its own design packet and explicit human authorization before any code is written.

The arc was written the day after the Slice-1 run findings (2026-06-08), synthesized from the merged Slice-1 docs, the accepted v3.9 epic arc, the candidate [[v4-0]] integration arc, the visualization implementation plan, and a same-day as-built review of all six dark-factory repos (`agent`, `docs`, `eventgraph`, `hive`, `site`, `work`).

## Why this arc exists

[[the-reunification]] diagnosed that Dark Factory's previous development path had perfected bounded fixtures beside a civilization that never moved in. The arc's design alternatives section records the two paths that were rejected:

- **Continue the v3.9 epic-gate ladder** (Epics 12+, new gate letters) — rejected because bounded fixtures beside the civilization are exactly the drift the reunification diagnosed.
- **Four independent pillar roadmaps** (interaction, trace, observability, visualization) — rejected because it would build dashboards for a factory that does not yet run reliably, violating the reunification's demonstration-first rule.

The chosen spine is **the slice ladder**: each phase is anchored by a real society-run demonstration, and pillar tracks advance only as far as that run can exercise them. The shepherding operating model is preserved throughout — machinery, never the artifact.

## The destination

The arc defines "complete dark factory deployment" as a conjunction of eight criteria that must all hold simultaneously. Briefly:

1. A continuously-running civilization (hive daemon + work-server + site + shared Postgres) operating as a persistent installation, not a per-session process — proven by ≥72-hour uptime with restart-safe run identity.
2. Humans submit orders, approve protected actions, and allocate value through Site; nothing requires a terminal or daemon restart.
3. Every material action — order, role action, artifact, commit, PR, review, merge — is on the causal event graph, and a single query by FactoryOrder ID returns the full chain; removing any required link returns a named missing-path error, not a quieter answer.
4. Operators can see factory health without reading logs — per-agent state, error counts, budget burn, stuck-agent age, gate state — with induced failure fixtures each alerting within five minutes.
5. The Site console renders the society building orders as live, animated, evidence-anchored views — read-only by construction.
6. Protected actions remain fail-closed with Michael Saucier as the top authority tier; autonomy has expanded only where audit expanded first.
7. The growth loop and capability evolution improve the factory under governance.
8. Gates K and L are satisfied; [[v4-0]] (with reunification doctrine folded in) is accepted canonical.

Deploying the factory does **not** grant the factory deploy authority: production deployment of factory output remains an excluded, separately gated protected action throughout the arc.

## The eight phases

### Phase 1 — Close Slice 1

*Theme: parity.* The society drives one catalog (fo_roles_catalog) to zero blockers and through the governed terminal steps, without a daemon restart. This closes two open findings from the Slice-1 run: **F7** (single-Operate producer variance; the design bet is that the review→fix loop, not more contract text, provides convergence) and **F8** (governance re-check was CanOperate-only, so the Reviewer stranded on historical events after a restart). The terminal steps exercise Gate-E on the Site surface (effect=none preserved), assemble Epic 11 evidence, and open the draft PR only after GitHub confirms — never before. Slice-1 findings and run evidence fold into [[v4-0]] via the migration register.

**Satisfied only when:** a society-authored artifact merges to docs main with the full chain inspectable, no shepherd edits, no daemon restart required.

### Phase 1‖ — Gate K (parallel, early)

Branch protection on `docs` main; `npm run verify` as a required PR check; CODEOWNERS routing; injection-quarantine prompt rules; data-handling policy; the self-reported-validation-is-never-sufficient rule. This runs in parallel with Phase 1 because it is repo settings and policy, not runtime, and it is the prerequisite for any autonomy increase.

### Phase 2 — The always-on substrate

*Theme: from per-run throwaway databases to a civilization that stays up.* Four tracks:

1. **Durable run substrate** — shared durable event store with schema bootstrap/migrations; run dynamics graph-auditable instead of "operator observation on a local DB you know the name of."
2. **Restart-independence** — historical events are recoverable work; warm-start recovery exercised deliberately.
3. **Persistent production identities** — civic roles run on authority-gated `RegisterPersistentIdentity` keys (built in `agent` repo, deferred from Slice 1); PR provenance readable as "opened by `implementer@<key>`."
4. **Run economics instrumented** — per-run KPIs as events: rounds-to-zero-blockers, Operate acceptance-criteria completeness, overhead-vs-productive event ratio, cost per artifact.

### Phase 3 — Traceability spine reaches GitHub

*Theme: one chain from intent to merged PR, queryable in one place.* `CodeChange` carries commit SHAs; `ExecutionReceipt` carries the PR URL; PR lifecycle events (opened, review, merge) are ingested as graph events via a GitHub event bridge. A read-only projection surface is built — deciding whether it extends `work-server`'s SSE bridge or becomes a dedicated eventgraph query service resolves the visualization plan's open question.

**Satisfied only when:** the question "show every action, actor, authority decision, and artifact from this order to its merged PR" is answerable from the projection surface alone — no GitHub UI, no local logs — and a deliberately broken path renders as missing evidence, not as a pass.

### Phase 4 — Human interaction: from approval clicks to an operator console

*Theme: the human steers through Site, never through a terminal.* Unified pending-decisions queue; FactoryOrder intake from Site with contract preview; governed steering verbs (halt/pause/resume with evidence request); push notifications on ApprovalRequired and run-terminal events (replacing the current ~60-second Site poll).

### Phase 5 — Observability: the factory reports its own health

*Theme: operate it like a service.* Structured logging; Prometheus/OTLP metrics endpoints; alerting and SLOs routed through SysMon's escalation path; run-boundary summaries (the `runtime.go:525` TODO).

### Phase 6 — Live animated graphics (The Observatory)

*Theme: discharge the visualization rethink on real data.* Site consumes the SSE event stream (the work-server `/events/subscribe` bridge exists; Site today consumes nothing from it). The animated society view (site#73, currently a static render) becomes live: the order moving strategist → planner → implementer → reviewer → guardian → human, evidence attaching at each hop, in real time. The factory floor shows agents as entities with FSM-state timelines, orders in flight, authority requests pulsing, budget burn. The Evidence Console — specified in the ten-view plan inside `docs` — moves from docs prototype to a read-only Site surface.

The rendering technology is decided by a crosswalk packet (G-6.0) before any code: the options are server-rendered SVG over SSE via the existing templ+HTMX stack versus a JS rendering library.

**Satisfied only when:** a human watching Site sees a society run progress live, with role state, evidence counts, authority-request state, budget burn, and draft-PR event updating within five seconds of each source event; every displayed claim links to its graph record; no view exposes a mutation control.

This is the phase [[the-observatory]] belongs to.

### Phase 7 — Growth, parallelism, and autonomy graduation

*Theme: the civilization at scale, still inside the membrane.* Growth loop live end-to-end (CTO → Spawner → Guardian → Allocator → `spawnDynamicAgent`); contract self-evolution through the governed capability-evolution chain rather than shepherd edits; ≥2 concurrent FactoryOrders completing with isolated worktrees and no cross-contamination; bounded `OrderSoftwarePR` against a code repo; autonomy graduation recorded against the autonomy-level ladder with the audit evidence that preceded each change.

Every autonomy-graduation packet in this phase is M-ASK regardless of any standing merge authorization — autonomy changes are never batch-mergeable.

### Phase 8 — The factory as a persistent installation

*Theme: deployment of the factory itself.* Composed deployment (Compose first, then hardened manifests with an air-gap path); singleton constraint honored (exactly one hive daemon replica; work-server and site scale independently); config hygiene (retire stale `fly.toml` entries; secrets env-only with no fallbacks; production signing keys never derived from names); backup/restore of the event store with tested RPO/RTO targets; Gate L and v4.0 acceptance.

## The pillar threads

Four pillars run across all phases as parallel tracks that each phase advances only as far as the corresponding run can exercise them:

| Pillar | As-built today (2026-06-09) | Missing |
|---|---|---|
| Human interaction | Gate-E approve/deny; hive operator projection + decision API; work phase-gate approve/reject; run-launch API with model overrides | Unified decision queue; order intake UX; governed steering verbs; push notification on ApprovalRequired; value-allocation surface |
| Traceability | Hash-chained signed causal graph; required trace paths + TraceCompletenessGate; authority request→decision→receipt chain; commit-verification gate | Graph↔GitHub linkage; GitHub event bridge; durable run substrate; read-only projection surface |
| Observability | Telemetry writer → Postgres; work telemetry API + SSE; site `/ops` dashboards | Structured logging; metrics endpoints; alerting/SLOs; per-agent error counts; configurable daily caps; run-boundary summaries |
| Live animated graphics | Ten-view spec; static role-timeline (site#73); SSE transport on work-server | Site consumes no stream; no live animation; no live evidence binding |

## Execution model: the conductor

The companion execution plan (2026-06-10) defines a **conductor pattern**: one long-running Claude Code session owns the packet register, dispatches work in isolated `feat/` worktrees, runs cross-family adversarial review (codex CLI reviews every PR non-interactively), and brings findings to zero blockers before raising a READY-TO-MERGE gate message. The conductor works autonomously between gates; every moment requiring Michael is spelled out in a "human touch budget" table.

The packet register enumerates thirty-plus numbered goal packets (G-0 through G-8.4). G-0 and G-K are fully drafted and ready to execute on authorization; G-1.1 through G-1.4 are ready; G-2.1 through G-2.4 are medium-grain; G-3 through G-8 are drafted at phase entry.

**Merge modes** are M-ASK (stop at every READY-TO-MERGE, merge only on explicit "merge #N") or M-STANDING (a recorded standing AuthorityDecision with named scope, conditions, expiry, and hard exclusions). Hard exclusions regardless of mode: docs doctrine PRs; autonomy-level or protected-action vocabulary changes; anything touching `hive/pkg/loop`, `hive/pkg/safety`, hive authority/policy paths, or work's Epic 11 creator.

## State as of 2026-06-13 (overnight checkpoint)

As of the overnight shift (2026-06-12/13), the arc has not yet been formally authorized or kicked off. Progress since the arc was drafted:

- **Slice 1 take 4 (2026-06-11):** Round 4 closed in a fully-observable stall (8 duration-budget obituaries, implementer escalate-and-park); three findings fixed and merged (agent#25, hive#155, eventgraph#48 and #49). The power-loss event mid-flight proved the designed crash-recovery path (`checkpoint.RecoverAll`, role-only survival). Open: v14-F1 (reason calls blowing the 10-minute provider ceiling), v14-F2 (approve-doesn't-settle-task), v14-F3 (keepalive MaxDuration 30m as a built-in society lifespan ceiling). Shepherding state relocated to `/Transpara/transpara-ai/data/df-slice1/` (reboot-safe; /tmp is no longer trusted).

- **Phase 3 pre-work completed overnight (2026-06-13):** The visualization component ([[the-observatory]] slice 1) exists, is tested, and converged through three cross-family adversarial review rounds (r3: approve, zero findings). Recon proved the metrics/trace pipeline already ran end-to-end (hive telemetry → Postgres → work `/telemetry/*` → site fetchers) with no visualization anywhere. The overnight session produced: a transparency contract (T1–T7), a Phase-3 rendering plan, and the `/ops/observatory` surface in `site` (pure-Go `svgviz` SVG renderers, seven read-only panels). The observatory renders civilization vitals, spend-vs-cap gauge, agent roster with 24h state-timeline strips, pipeline phase costs, authority queue and decisions, actor lifecycle, and a causal trace explorer — all with fail-legible unavailable states and provenance footers, read-only by construction, zero new dependencies.

  ⚠ The observatory (site#76) and its supporting docs PRs (#128, #129) were open for Michael's merge decision as of 2026-06-13. Their merged status is not confirmed by these sources.

## Key risks

| Risk | Arc's disposition |
|---|---|
| Producer variance does not converge even with the loop engaged | Measured explicitly in Phase 1; reserves: blind A/B and model-tier escalation via the merged model-policy machinery. If three shepherded rounds fail, escalate — "the society isn't ready yet" is a valid outcome |
| Cost of an always-on society | Budget floors/caps; overhead-vs-productive KPI; per-phase spend ceilings set at phase-entry authorization; global daily stop; provider-failure policy: park on 3+ consecutive errors, never retry-spin |
| New network surfaces (GitHub bridge, projection/SSE, order intake, notifications, metrics endpoints) widen the attack area | Every packet introducing a network surface carries an explicit security-review section as a named acceptance criterion |
| In-process bus = single-process civilization | Accepted constraint; singleton deployment rule in Phase 8. Distribution would need a new kernel-adjacent packet — the transport interface exists in `eventgraph`, deliberately unshipped |
| Evidence split across graph and GitHub until Phase 3 lands | Explicitly named; claims about run dynamics stay labeled "operator observation" until then |
| Site drifts toward executor as interaction verbs grow | Every new verb forwards a governed decision with `effect=none` at the Site boundary; guard on every Site packet |
| Visualization overstates posture | Binding principles from the viz plan: no unscoped satisfied chips, candidate visibly distinct, fail-legible missing evidence, read-only by construction |

## Forbidden patterns (stated in the arc)

The arc enumerates these explicitly, carried here because they are load-bearing:

- Do not treat this arc as implementation authority — every phase needs packets.
- Do not start a phase's implementation before the prior predicate or an explicit human re-sequencing decision.
- Do not let shepherds touch a society artifact — machinery only, always.
- Do not weaken any fail-closed guard to make a run converge.
- Do not let Site execute work or assemble policy evidence (`effect=none` forever).
- Do not render an unscoped green checkmark in any view.
- Do not expand autonomy without expanded audit recorded first.
- Do not auto-merge — no merge executes without a recorded human authorization.
- Do not grant the factory production-deploy authority as a side effect of deploying the factory.

## Relationship to doctrine

- [[v3-9]] is accepted canonical. The arc cites its implementation material as current planning tracker evidence, not accepted doctrine. Its gates (A–J) are satisfied for their named bounded fixtures only.
- [[v4-0]] is candidate, not accepted. Gate K (interim loop hardening) is closed for pre-live sequencing by waiver, with production go-live/live-data revalidation still blocked; Gate L (final acceptance) remains defined and unsatisfied. The arc's Phase 8 closes Gate L.
- [[the-reunification]] is the spine. The arc extends the reunification's demonstration-first method to full deployment; it does not supersede v3.9 or accept v4.0.
- [[slice-1-completion]] ⚠ (not yet compiled) is what Phase 1 produces — the first society-built artifact merging to docs main with a complete inspectable chain.

## Sources & provenance

Compiled from four primary planning documents:

- `docs/dark-factory/reunification/2026-06-09-deployment-arc.md` (DF-REUNIFY-2026-06-09-DEPLOYMENT-ARC, v0.1.4, `authority: planning`, `canonical: false`) — lines 1–516: arc structure, eight phases, pillar scorecard, as-built review of six repos, alternatives considered, risks, forbidden patterns.
- `docs/dark-factory/reunification/2026-06-10-deployment-arc-execution-plan.md` (DF-REUNIFY-2026-06-10-DEPLOYMENT-ARC-EXECUTION, v0.5.0) — lines 1–579: execution model, conductor pattern, packet register, merge modes, human touch budget, G-0 through G-1.4 ready packet text.
- `docs/dark-factory/reunification/2026-06-11-arc-state.md` (DF-REUNIFY-2026-06-11-ARC-STATE, v0.2.0) — lines 1–59: Slice 1 take-4 round 4 state, crash register, standing changes (persistent shepherding state dir, reboot-safe round records).
- `raw/transpara/dark-factory/implementation/overnight-2026-06-13-claude-checkpoint.md` (DF-CKPT-20260613-OVERNIGHT-CLAUDE, v1.0.0) — lines 1–57: observatory overnight shift state, review convergence record, open decisions awaiting Michael.

All four sources carry `authority: planning` or `status: draft/complete` without `canonical: true`. No claim here is advanced beyond what the sources state. Cross-links to `[[the-reunification]]`, `[[the-observatory]]`, `[[v4-0]]`, `[[v3-9]]`, `[[slice-1-completion]]` are forward references to separately compiled or forthcoming articles.

## Live deploy status

<div id="live-deploy"></div>
<script>(function(){fetch("deploy-status.json",{cache:"no-store"}).then(function(r){return r.ok?r.json():null}).then(function(s){if(!s)return;var el=document.getElementById("live-deploy");if(!el)return;var rows=(s.recent||[]).slice().reverse().map(function(e){return e.at+" — "+String(e.sha).slice(0,7)+" ("+e.result+")"}).join("<br>");el.innerHTML="<strong>"+(s.blocked?"⚠ blocked: "+s.reason:"live: "+String(s.deployed_sha||"").slice(0,7))+"</strong><br>checked "+(s.checked||"")+"<br><br>recent:<br>"+rows;}).catch(function(){})})();</script>
