---
entity: OpenClaw
aliases: [openclaw, transpara-ai/openclaw, the personal AI assistant, the lobster, the local-first gateway]
tier: investigation
status: compiled
last_compiled: 2026-06-13
civilization_contribution: "Deferred adapter-or-UX-pattern candidate (stricter than pattern-only): a possible future RuntimeBroker adapter or operator-UX reference — gateway/session ergonomics, onboarding, channel patterns — gated until the local deterministic RuntimeBroker passes Base Slice 0 and adapter conformance; its gateway/session behavior must never own execution policy, Work flow, release authority, certification, or factory control."
raw_documents: []
current_research_version:
sources:
  - /Transpara/transpara-ai/repos/docs/dark-factory/v3.9/implementation/epics/02-technology-decision-crosswalk-v3.9.md  # v3.9.1 crosswalk; OpenClaw decision row (L81) + per-item note (L169-173); freeze/reopen policy (L41-68)
  - /Transpara/transpara-ai/repos/docs/dark-factory/v3.9/09-legacy-coverage-matrix-v3.9.md  # ratified grouped line — OpenManus/OpenClaw/Hermes "bounded runtime references/adapters only … Deferred" (L254)
  - /Transpara/transpara-ai/repos/docs/dark-factory/v3.9/04-production-workflow-and-runtime-v3.9.md  # external-runtimes-are-references-or-adapters-only rule (L213)
  - /Transpara/transpara-ai/repos/docs/dark-factory/research/checkpoints/2026-05-13-05-phase-4-batch-c-agent-execution-orchestration.md  # Phase 4 Batch C — OpenClaw candidate 6 deep-dive, README-only (L208-313); Batch C inclusion-matrix row (L1102)
  - /Transpara/transpara-ai/repos/docs/dark-factory/research/checkpoints/2026-05-13-07-phase-5-inclusion-marginal-contribution-matrix.md  # Phase 5 inclusion matrix — openclaw row (L127); specific rejection (L301)
  - /Transpara/transpara-ai/repos/docs/dark-factory/research/checkpoints/2026-05-13-10-civilization-landscape-investigation-closeout.md  # closeout — OpenClaw in BOTH "pattern/reference only" (L139) and "defer until prerequisite controls exist" (L155)
  - /Transpara/transpara-ai/repos/docs/dark-factory/research/checkpoints/2026-05-13-civilization-landscape-investigation-kickoff.md  # ground rules + scope; OpenClaw is candidate 7 (L170-171); Batch C roster (L415); access note (L273)
  - "/Transpara/transpara-ai/repos/docs/dark-factory/research/openclaw-architectural-analysis - Claude.html"  # separate research artifact, dated 2026-05-11, "OpenClaw — A Skeptical Architectural Analysis" of OpenClaw v2026.5.7 (richer secondary context, NOT the investigation's README-only evidence base)
  - "GitHub API: repos/transpara-ai/openclaw (fork metadata, 2026-06-13 live)"  # isFork=true, parent=openclaw/openclaw, createdAt 2026-05-13T08:36:56Z, license=MIT, description "Your own personal AI assistant. Any OS. Any Platform. The lobster way."
  - "Upstream context only (not re-published): github.com/openclaw/openclaw — fork parent, fetched 2026-06-13"
  - Open Brain  # investigation-disposition synthesis (deferred bucket for OpenClaw), 2026-06-13
confidence:
  decision_row: high — OpenClaw has a complete row in the v3.9.1 crosswalk (deferred, adapter/pattern) plus a per-item note; corroborated by the ratified legacy-coverage matrix line
  fork_date_and_identity: high — confirmed live via GitHub fork metadata (createdAt 2026-05-13T08:36:56Z, parent openclaw/openclaw, MIT)
  investigation_repo_internals: thin — the investigation inspected ONLY the README ("Primary evidence inspected: README.md"); no code was read for the decision
  architectural_analysis: medium / context-only — the rich "Skeptical Architectural Analysis" (v2026.5.7) is a separate research artifact that did a repo-anchored pass, but it is NOT what the v3.9 decision rests on, and it self-flags many claims as docs/secondary/unverified
  security_incident_figures: contested/context-only — ClawBleed CVE-2026-25253, the ~40k exposed instances, and the 12–20% malicious-skill rate come from the architectural analysis citing secondary sources (advisories, blogs); carried as context, never load-bearing on the decision
---

# OpenClaw

**A forked public project the [[civilization-landscape-investigation]] evaluated and recorded as deferred.** OpenClaw is a local-first, channel-first *personal AI assistant* — a long-lived gateway you run on your own devices that fronts many messaging surfaces (WhatsApp, Telegram, Slack, Signal, iMessage, and others) and companion apps, routing inbound messages to agent sessions that can execute tools on the host. Transpara forked it into the `transpara-ai` org on **2026-05-13** (`transpara-ai/openclaw`, forked from the public upstream `openclaw/openclaw`) so it could be read as ground-truth source rather than from a project page. That fork happened on the **same day** as the [[dark-factory]] landscape investigation's 2026-05-13 sweep, where it was assessed (Phase 4, Batch C) against the canonical design and recorded in the v3.9.1 technology-decision crosswalk as **deferred** — a *possible* future [[runtime-broker|RuntimeBroker]] adapter or operator-UX reference, but never a runtime, control plane, or truth/authority layer the factory may depend on today.

This article is about **our investigation and decision**, not a mirror of the upstream's documentation. The upstream is public OSS; it is cited here only as context, never re-published.

## Where it sits in the decision crosswalk

The authoritative record is the row in the v3.9.1 *External Technology Decision Crosswalk* (the document the compile was told to ground in). Unlike some siblings, OpenClaw **does** have its own complete row:

| Field | Value (per crosswalk, L81) |
|---|---|
| Current decision | **deferred** |
| ADR / doc ref | legacy coverage matrix / runtime adapter references |
| Integration mode | possible RuntimeBroker adapter or UX reference |
| Owning epic | **Epic 6 or later external-runtime packet** |
| Fork / adapter / pattern / exclude | **adapter / pattern** |
| Main risk | "local gateway could become hidden controller" |
| PR #61 change required? | "yes: name deferral and conformance gate" |

The per-item note is the binding constraint (crosswalk L169–173):

> **Decision: deferred adapter or UX pattern candidate.** "OpenClaw-like gateway/session behavior must not own execution policy, Work flow, release authority, certification, or factory control."

In the canonical decision-category vocabulary this lands as **deferred** (with an adapter-or-pattern shape, the same family as [[openmanus]] and the [[hermes-agent|Hermes]] runtime side). The crosswalk's own freeze/reopen policy applies: pattern-only adoptions are frozen at the v3.9 reference point and do not track upstream behaviour unless an epic explicitly reopens them; for the *adapter* path the gate is harder still — see "What 'deferred' actually gates" below.

The grouped, ratified statement that backs the row lives in the v3.9 **Legacy Coverage Matrix** (L254):

> `OpenManus/OpenClaw/Hermes` → "bounded runtime references/adapters only" · **"Deferred until local deterministic RuntimeBroker passes Base Slice 0 and adapter conformance."**

And the v3.9 production-workflow-and-runtime doc states the law it is an instance of (L213): "External runtimes such as Hermes, OpenManus, OpenClaw-like workers, Codex, CI, or future backends are references or adapters only. They do not own execution policy, Work flow, release authority, certification, or factory control."

## What Changed with the Research

No released TAI-RES evaluation targets OpenClaw — this is a support-only investigation page, so Topic Details is empty by design. The research record is two-layered and the layers must not be conflated: the v3.9 *decision* rests on the README-only Phase 4 Batch C inspection (2026-05-13), while the richer *Skeptical Architectural Analysis* (2026-05-11, reviewing v2026.5.7) is a separate, context-only artifact that self-flags much of its detail as secondary/unverified. Nothing has moved since the 2026-06-13 compile; the deferral stands at the v3.9 reference point, gated as described below.

## The Boundary

The binding constraint is the crosswalk's per-item note: *"OpenClaw-like gateway/session behavior must not own execution policy, Work flow, release authority, certification, or factory control."* The ratified backing is the Legacy Coverage Matrix line — bounded runtime references/adapters only, **"deferred until local deterministic RuntimeBroker passes Base Slice 0 and adapter conformance"** — and the v3.9 runtime law that external runtimes are references or adapters only. The single load-bearing collision is trust-model: OpenClaw's documented default is host execution for the main session, the exact inverse of the bounded, policy-enforced [[runtime-broker|RuntimeBroker]] envelope the factory requires; its session/workspace state can become parallel truth outside [[event-graph|EventGraph]], and hot-loaded skills bypass [[capability-evolution|CapabilityArtifact]] governance. Until the adapter conformance checklist exists and is passed, no runtime path opens.

## How it entered the arc

OpenClaw was **candidate 7** of the [[civilization-landscape-investigation]] source list — the one-time 2026-05-13 sweep that evaluated each external tool against the then-canonical Dark Factory v3.8 design for marginal contribution, under a hard operator rule: *no aspirational claims accepted without code or canonical-document evidence; if access to a repo is missing, stop — do not substitute upstreams or marketing pages.* The fork into `transpara-ai` existed so the project could be read as source under that rule. (The kickoff notes that `transpara-ai/openclaw` "initially returned 404 but later recheck succeeded; treat accessible now" — the fork and the survey were effectively simultaneous.)

It was analysed in **Phase 4, Batch C** ("agent execution and orchestration"), alongside `OB1`, `MetaGPT`, `OpenManus`, the [[hermes-agent|Hermes]] family, [[multica]], [[solo-orchestrator|Solo Orchestrator]], and [[symphony|Symphony]]. The investigation closeout placed OpenClaw in **two lists at once** — **pattern / reference only** (L139) *and* **defer until prerequisite controls exist** (L155) — the same dual placement it gave [[paperclip|Paperclip]]: useful as a design/UX reference now, not integrable as a runtime until the kernel-level boundaries it could violate are enforced.

## The employee to Paperclip's company

The cleanest way the investigation framed OpenClaw is by its contrast with [[paperclip|Paperclip]], the sibling fork evaluated in the same survey. Paperclip's own self-description, quoted in the Batch D analysis, draws the line: **"If OpenClaw is an employee, Paperclip is the company."** OpenClaw is the *individual* agent shell — one person's local-first assistant with channels, sessions, skills, and host tools — whereas Paperclip is the org-chart control plane above many such agents. Both were declined for the same reason from opposite ends: neither may become the factory's control plane or truth source. OpenClaw's risk is the worker that quietly starts driving; Paperclip's is the org chart that quietly becomes the controller.

## Capability Read

From the Batch C candidate analysis (evidence inspected: **README only**), OpenClaw is:

> "A personal AI assistant/gateway you run on your own devices. It is local-first and channel-first, supporting many messaging surfaces and companion apps. It has a Gateway control plane for sessions, channels, tools, and events, multi-agent routing, workspace skills, DM pairing, optional sandboxing, and host execution for the main session by default."

The core primitives the investigation recorded:

> "local-first gateway · multi-channel inbox · agent sessions · workspace root · AGENTS.md / SOUL.md / TOOLS.md · skills · session tools · DM pairing · sandbox modes · companion apps · voice/canvas/nodes."

What it explicitly **is not**, per the same analysis: *"not a production Work DAG. It is not EventGraph truth. It is not v3.8 release authority. It is not a fail-closed runtime envelope system by default. It is not a factory controller."* Its governance surfaces — "DM pairing, allowlists, sandbox options, and doctor warnings" — "are not v3.8 protected-action authority records," and its data model is "Workspace/session/config state, not EventGraph kernel state." The investigation rated it "large and operationally rich. But its default trust model is personal/single-user, not industrial fail-closed factory execution."

## Benchmark Reality

No benchmark or performance number played any part in the decision — the evidence base was the README alone, and the decision turned on architecture posture (host execution, session-as-truth, untrusted channels, ungoverned skills). The quantitative claims that exist in the record are the *security* record from the separate architectural analysis, and they are secondary-sourced context only: CVE-2026-25253 ("ClawBleed," CVSS 8.8, a one-click RCE via cross-site WebSocket hijacking), "~40,000 OpenClaw instances publicly exposed and 63% vulnerable" at disclosure, and a reported 12–20% malicious-skill rate on the ClawHub marketplace — advisory/blog-sourced figures, never load-bearing, though consistent with the risks the investigation flagged independently. The one claim closed as fact by live metadata is the MIT license.

## Why deferred, and not adopted

The marginal-contribution verdict was genuinely positive on *ergonomics*: "OpenClaw provides strong channel, gateway, onboarding, session, and operator-ergonomic patterns." But the recorded risks are all about a personal-trust system colliding with an industrial fail-closed one:

- "**Default host execution conflicts with v3.8 RuntimeEnvelope requirements**" — the single load-bearing objection. OpenClaw's documented default is that tools run on the host for the main session; the arc requires every execution to pass through a bounded, policy-enforced [[runtime-broker|RuntimeBroker]] envelope.
- "Channel input is **untrusted** and can carry prompt-injection risk" — 20+ messaging surfaces are 20+ injection vectors into a privileged local process.
- "Session/workspace state can become **parallel truth**" — a Markdown/session store that the kernel never sees is authority-shaped evidence outside [[event-graph|EventGraph]].
- "Skills can become **ungoverned capability artifacts**" — hot-loaded community skills bypass [[capability-evolution|CapabilityArtifact]] governance.

The Batch C recommendation followed directly: *"Include as benchmark/comparison and possible UX/runtime reference only. Do not adopt as factory runtime unless wrapped behind v3.8 RuntimeBroker with network/secrets/command/file policies."* The Phase 5 matrix recorded the same disposition in one line (L127): Batch C, *"Pattern / runtime reference … Host execution, session-as-truth … UX/runtime reference only; no controller role,"* and the closeout's specific rejection is blunt (L301): **"OpenClaw must not become the control plane or truth source."** This is the containment logic the arc applies to every external runtime/control-plane candidate — absorb the useful surfaces, cede no authority.

## What "deferred" actually gates

OpenClaw's deferral is not a soft "maybe later" — it is bound to a concrete future gate. The investigation's gap summary names the open work directly: *"RuntimeBroker adapter contract is under-specified for future Hermes/OpenManus/OpenClaw-like runtimes"* (closeout Gap 2), and lists as a high-priority design decision the *"RuntimeBroker adapter checklist for Hermes/OpenManus/OpenClaw-like runtimes."* The legacy-coverage line ties the unlock to a precise condition: **deferred until the local deterministic [[runtime-broker|RuntimeBroker]] passes [[base-slice-0|Base Slice 0]] and adapter conformance.** Until that checklist exists and an OpenClaw-style adapter passes it, OpenClaw cannot be wired in as a runtime — and the crosswalk binds any such work to **Epic 6 or later** as the only owning epic. As of this compile, no epic has reopened it; the decision stands at the v3.9 reference point.

If its *ideas* are borrowed before then, they are pointed at operator UX (gateway/session ergonomics, onboarding, channel patterns) as a **pattern**, not at execution as a runtime — which is exactly why it sits in both closeout buckets at once.

## A richer, separate architectural analysis (context, not the decision)

There is a much deeper local artifact on OpenClaw — *"OpenClaw — A Skeptical Architectural Analysis"* (dated **2026-05-11**, two days before the survey, reviewing **OpenClaw v2026.5.7**). It is an eight-persona panel review that did a repo-anchored verification pass against `github.com/openclaw/openclaw`. It is worth reading for color, but it is **not the evidence the v3.9 decision rests on** — the investigation's own Batch C entry is explicit that "Primary evidence inspected: README.md." Treat the analysis as context, and note that it self-flags much of its own detail as `docs` / `secondary` / `unverified`. The non-load-bearing highlights:

- **It is a gateway around an embedded SDK, not a monolith.** OpenClaw embeds `pi.dev`'s MIT-licensed coding-agent SDK (**Pi**) in-process via `createAgentSession()`; Pi owns the agent loop (ReAct), the ~15-provider model abstraction, and the `AGENTS.md` convention. OpenClaw wraps it with channels, routing, a marketplace (ClawHub), the `SOUL.md` identity layer, and customized tools. The analysis's own load-bearing correction: *"Pi is an embedded SDK, not an OpenClaw module"* — so a reader betting on OpenClaw is implicitly betting on Pi, and a fork has **two upstreams to pin**.
- **The committed bets** the analysis names line up exactly with the investigation's objections: *Markdown is the source of truth* (SQLite is an index over it), *the LLM is the orchestrator* ("no graph DAG, no checkpointed state machine" — "exactly the opposite of LangGraph's bet"), *channels are first-class*, *sandbox is opt-in* (the README's verbatim default: "tools run on the host for the main session, so the agent has full access when it is just you"), and a *daily release cadence* (`YYYY.M.D`, latest v2026.5.7, no LTS).
- **The security record (context only).** The analysis cites, from secondary sources, that Q1 2026 "validated the cost of these choices": CVE-2026-25253 ("ClawBleed," CVSS 8.8) — a one-click RCE via cross-site WebSocket hijacking with "~40,000 OpenClaw instances publicly exposed and 63% vulnerable" at disclosure — and a reported 12–20% malicious-skill rate on the ClawHub marketplace. These figures are advisory/blog-sourced and carried here strictly as context; they are *not* what made the decision, but they are consistent with why the investigation flagged "untrusted channel input" and "ungoverned skills" as risks.

## Fail-legible notes

- **Two evidence bases, not one — do not conflate them.** The v3.9 *decision* rests on a **README-only** Batch C inspection. The richer *architectural analysis* (v2026.5.7, repo-anchored) is a separate research artifact and is **not** the decision's evidence base. Every concrete internal claim sourced from the analysis (Pi-as-embedded-SDK, the seven-stage loop, SQLite/sqlite-vec/FTS5 memory backing, the CVE/marketplace figures) is **context-only** here, and the analysis itself flags much of it as `docs`/`secondary`/`unverified`. The decision turned on architecture posture (host execution, session-as-truth, untrusted channels, ungoverned skills), not on those specifics.
- **Thin investigation internals.** Because the investigation read only the README, every claim about OpenClaw's internals *as the decision saw them* is README-grounded, not code-verified. Mark investigation-repo-internals confidence **thin**.
- **Fork date is the survey date.** The GitHub fork metadata gives `createdAt 2026-05-13T08:36:56Z` — the same calendar day as the investigation, corroborated by the kickoff's "initially returned 404 but later recheck succeeded" note. Stated as fact; it means the fork existed *to be read by* the survey, not before it.
- **"Hidden controller" is a risk, not an observed failure.** The crosswalk's main risk ("local gateway could become hidden controller") and the closeout rejection ("must not become the control plane or truth source") are forward-looking judgments — the reason the decision is fenced to deferred-adapter/pattern — not records of harm observed in the factory.
- **Deferred ≠ pattern-only.** OpenClaw is *deferred* (with an adapter path gated on RuntimeBroker conformance), which is a stricter status than the plain *pattern-only* given to, e.g., [[gstack|gStack]] or [[symphony|Symphony]]. The adapter route cannot open until Base Slice 0 + the adapter conformance checklist exist; the pattern route (UX ideas) follows the ordinary freeze policy. Both are recorded; neither is active.
- **License is MIT (confirmed live).** The Batch C note recorded "README badge states MIT." The live fork metadata confirms `license=MIT`, closing that as fact rather than badge-claim.
- **Upstream is cited, never re-published.** Per org rule, `openclaw/openclaw` is public OSS. Its existence and description ("Your own personal AI assistant. Any OS. Any Platform. The lobster way.") are confirmed live as context for *why we forked it to read it*, not as content to mirror. The wiki subject is our investigation and our decision.

## Where it sits relative to the rest of the survey

OpenClaw is the **personal-assistant / local-runtime** member of the survey's agent-execution cluster. It pairs naturally with two neighbours: as a *runtime* it sits beside [[openmanus]] and the [[hermes-agent|Hermes]] runtime side — all three "deferred until the RuntimeBroker passes Base Slice 0 and adapter conformance" in the same legacy-matrix line; as an *operator surface* it is the employee to [[paperclip|Paperclip]]'s company, and a UX cousin of [[multica]] and [[solo-orchestrator|Solo Orchestrator]]. Across all of them the ratified v3.9 acceptance "promoted no external framework to kernel, truth source, Work replacement, policy owner, release authority, certification authority, capability promoter, factory controller, or Site replacement" — OpenClaw included. It sits at the same hinge as the rest of the [[civilization-landscape-investigation]]: the moment [[dark-factory]] looked outward at the personal-agent landscape and chose to learn its ergonomics while importing none of it as authority, and to keep even the tempting runtime path behind a conformance gate.

## Sources & Provenance

- **v3.9.1 External Technology Decision Crosswalk** — `/Transpara/transpara-ai/repos/docs/dark-factory/v3.9/implementation/epics/02-technology-decision-crosswalk-v3.9.md` (OpenClaw decision row L81; per-item note "Decision: deferred adapter or UX pattern candidate" L169–173; freeze/reopen policy L41–68). This is the authoritative decision record the compile was grounded in; the row is complete (status `review`, `canonical:false`).
- **v3.9 Legacy Coverage Matrix** — `/Transpara/transpara-ai/repos/docs/dark-factory/v3.9/09-legacy-coverage-matrix-v3.9.md` (L254): the ratified grouped statement — `OpenManus/OpenClaw/Hermes` "bounded runtime references/adapters only … Deferred until local deterministic RuntimeBroker passes Base Slice 0 and adapter conformance."
- **v3.9 Production Workflow & Runtime** — `/Transpara/transpara-ai/repos/docs/dark-factory/v3.9/04-production-workflow-and-runtime-v3.9.md` (L213): external runtimes (incl. "OpenClaw-like workers") "are references or adapters only … do not own execution policy, Work flow, release authority, certification, or factory control."
- **Phase 4 Batch C** candidate analysis — `…/research/checkpoints/2026-05-13-05-phase-4-batch-c-agent-execution-orchestration.md` (OpenClaw section, candidate 6, L208–313; Batch C inclusion-matrix row L1102). Primary source for what the investigation found; explicitly **README-only** ("Primary evidence inspected: README.md").
- **Phase 5 inclusion / marginal-contribution matrix** — `…/research/checkpoints/2026-05-13-07-phase-5-inclusion-marginal-contribution-matrix.md` (openclaw row L127: "Pattern / runtime reference … UX/runtime reference only; no controller role"; specific rejection L301: "OpenClaw must not become the control plane or truth source").
- **Investigation closeout** — `…/research/checkpoints/2026-05-13-10-civilization-landscape-investigation-closeout.md` (OpenClaw in BOTH "Include as pattern/reference only" L139 and "Defer until prerequisite controls exist" L155; RuntimeBroker-adapter Gap 2, L179; high-priority adapter checklist, L204).
- **Investigation kickoff** — `…/research/checkpoints/2026-05-13-civilization-landscape-investigation-kickoff.md` (ground rules; OpenClaw as candidate 7 / `transpara-ai/openclaw`, L170–171; Batch C roster L415; "initially returned 404 but later recheck succeeded" access note L273).
- **OpenClaw — A Skeptical Architectural Analysis** (context only, separate research artifact, NOT the decision's evidence base) — `/Transpara/transpara-ai/repos/docs/dark-factory/research/openclaw-architectural-analysis - Claude.html`, dated 2026-05-11, reviewing OpenClaw v2026.5.7: Pi-as-embedded-SDK, the committed bets (Markdown-as-state, LLM-as-orchestrator, channel-first, opt-in sandbox, daily releases), and the secondary-sourced Q1-2026 security record (CVE-2026-25253 "ClawBleed"; ~40k exposed instances; 12–20% malicious-skill rate). Self-flags much detail as `docs`/`secondary`/`unverified`.
- **Fork metadata** — GitHub API `repos/transpara-ai/openclaw`, fetched 2026-06-13: `isFork=true`, `parent=openclaw/openclaw`, `createdAt=2026-05-13T08:36:56Z`, `license=MIT`, `description="Your own personal AI assistant. Any OS. Any Platform. The lobster way. 🦞"`.
- **Upstream (context only, not re-published)** — `github.com/openclaw/openclaw` (https://github.com/openclaw/openclaw), confirmed as the fork parent on 2026-06-13.
- **Open Brain** — investigation-disposition synthesis captured 2026-06-13 (OpenClaw in the crosswalk's "deferred" set alongside Hermes/OpenManus/Autoresearch/MiroFlow/MiroThinker).

**Conflicts / open items, stated not resolved.** (1) *Two evidence bases* — the README-only Batch C inspection (what the decision rests on) versus the deeper repo-anchored architectural analysis (richer but context-only, self-flagged unverified in parts); kept separate throughout. (2) *Deferred vs pattern-only* — OpenClaw carries the stricter `deferred` status with an adapter path gated on RuntimeBroker/Base-Slice-0 conformance, distinct from the plain pattern-only siblings; both routes recorded, neither active. (3) *Security figures* — CVE/exposure/marketplace numbers are advisory/blog-sourced via the analysis and are context only, not load-bearing on the decision. (4) *Status of the crosswalk itself* — `status: review`, `canonical: false`; the binding canonical law above the row is the Legacy Coverage Matrix line plus the v3.9 "external runtimes are references/adapters only" rule. `[[civilization-landscape-investigation]]`, `[[dark-factory]]`, `[[runtime-broker]]`, `[[event-graph]]`, `[[paperclip]]`, `[[multica]]`, `[[symphony]]`, `[[hermes-agent]]`, `[[solo-orchestrator]]`, `[[gstack]]`, `[[base-slice-0]]`, and `[[capability-evolution]]` resolve to compiled articles; `[[openmanus]]` is a forward reference not yet compiled.
