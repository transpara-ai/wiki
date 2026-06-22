---
entity: Paperclip
aliases: [paperclip, transpara-ai/paperclip, the company OS]
tier: investigation
status: compiled
last_compiled: 2026-06-13
sources:
  - /Transpara/transpara-ai/repos/docs/dark-factory/v3.9/implementation/epics/02-technology-decision-crosswalk-v3.9.md  # v3.9.1 crosswalk; Paperclip decision row (L84) + per-item note (L197-201)
  - /Transpara/transpara-ai/repos/docs/dark-factory/research/checkpoints/2026-05-13-06-phase-4-batch-d-governance-self-evolution-platform-tooling.md  # Phase 4 Batch D — repo-grounded candidate analysis of transpara-ai/paperclip (L455-592)
  - /Transpara/transpara-ai/repos/docs/dark-factory/research/checkpoints/2026-05-13-civilization-landscape-investigation-kickoff.md  # investigation ground rules, scope, source list (paperclip is candidate 16)
  - /Transpara/transpara-ai/repos/docs/dark-factory/research/checkpoints/2026-05-13-08-phase-6-gap-analysis-versus-v3-8.md  # Gap G6 (Site operator UX / proof-of-work) — paperclip as candidate evidence (L447-505)
  - /Transpara/transpara-ai/repos/docs/dark-factory/research/checkpoints/2026-05-13-10-civilization-landscape-investigation-closeout.md  # final inclusion summary — paperclip as pattern/reference + defer (L132-163)
  - "GitHub API: repos/transpara-ai/paperclip (fork metadata, 2026-06-13 live)"  # isFork=true, parent=paperclipai/paperclip, createdAt 2026-03-17T17:54:05Z, description "Open-source orchestration for zero-human companies"
  - "Upstream context only (not re-published): github.com/paperclipai/paperclip — README headline + MIT license badge, fetched 2026-06-13"
confidence:
  decision_row: high — Paperclip has a complete row in the v3.9.1 crosswalk (pattern-only / UX-only)
  fork_date_and_identity: high — confirmed live via GitHub fork metadata
  repo_internals: thin — the investigation inspected only the README; "actual implementation not inspected beyond README" (Batch D)
  heartbeat_and_org_model: medium — consistent across Batch D and the OpenClaw landscape analysis, but both trace to upstream README/marketing, which the investigation's own rule treats as "aspirational" until code-verified
  market_traction: contested/context-only — star counts (~38k in ≤4 weeks per one research writeup; ~70k live on upstream) are upstream-marketing figures, carried as context, not load-bearing
---

# Paperclip

**A forked public project the [[civilization-landscape-investigation]] evaluated and declined to adopt.** Paperclip is an open-source control plane for running "zero-human companies" — agents arranged into org charts with goals, budgets, approvals, and heartbeat-driven execution. Transpara forked it into the `transpara-ai` org on **2026-03-17** (`transpara-ai/paperclip`, forked from the public upstream `paperclipai/paperclip`) so it could be read as ground-truth source rather than from marketing pages. During the [[dark-factory]] landscape investigation (Phase 4, Batch D, **2026-05-13**) it was assessed against the canonical design and recorded in the v3.9.1 technology-decision crosswalk as **pattern-only** — specifically a **UX-only pattern**: its organization, budgeting, and approval surfaces may *inform* operator UX, but it must never become a control plane "without an ADR and EventGraph authority records."

This article is about **our investigation and decision**, not a mirror of the upstream's documentation. The upstream is public OSS; it is cited here only as context, never re-published.

## Where it sits in the decision crosswalk

The authoritative record is the row in the v3.9.1 *External Technology Decision Crosswalk*:

| Field | Value (per crosswalk) |
|---|---|
| Current decision | **pattern-only** |
| Integration mode | org/budget/approval **UX pattern only** |
| Owning epic | Epic 4 operator workflow *if used* |
| Fork / adapter / pattern / exclude | **pattern** |
| Main risk | "UX pattern can imply control-plane authority" |
| PR #61 change required? | "yes: must remain UX-only unless ADR changes" |

The per-item note is the binding constraint:

> "Paperclip-like organization, budgeting, or approval UX must not become a control plane without an ADR and EventGraph authority records."

In the canonical decision-category vocabulary this lands as **UX-only pattern** (distinct from the broader "pattern-only" bucket that holds [[event-graph|EventGraph]]-adjacent design patterns). The crosswalk's own freeze policy applies: pattern-only adoptions are **frozen at the v3.9 reference point** and do not track upstream behaviour unless an epic explicitly reopens them — and reopening Paperclip would require recording the upstream commit reviewed, which pattern changed, and whether Dark Factory adopts, rejects, or defers it.

## How it entered the arc

Paperclip was candidate 16 of the [[civilization-landscape-investigation]] source list — a sweep that evaluated each external tool against the then-canonical Dark Factory v3.8 design for marginal contribution, with a hard rule from the operator: *no aspirational claims accepted without code or canonical-document evidence; if access to a repo is missing, stop — do not substitute upstreams or marketing pages.* The fork into `transpara-ai` existed so the project could be read as source under that rule rather than from its website.

It was analysed in **Phase 4, Batch D** ("governance, self-evolution, and platform-tooling"), alongside `hermes-agent-self-evolution`, `agent-governance-toolkit`, and `gstack`. The investigation closeout placed Paperclip in two lists at once: **pattern/reference only** *and* **defer until prerequisite controls exist** — i.e. useful as a design reference now, not integrable until the kernel-level boundaries it could violate are enforced.

## What the investigation found it to be

From the Batch D candidate analysis (evidence inspected: **README only**):

> "A Node.js server and React UI for orchestrating teams of AI agents to run businesses … org charts, goals, budgets, governance, ticketing, heartbeats, agent coordination, cost controls, approvals, multi-company isolation, plugins, secrets, routines, and audit logs."

Its self-description, quoted in the analysis, is the cleanest summary of why it mattered to a company-shaped project: **"If OpenClaw is an employee, Paperclip is the company."** (See [[openclaw]] for the sibling fork on the other side of that line.)

Two architectural notes the investigation recorded:

- **Heartbeat execution model.** Scheduled and event-triggered agents "wake, check work, execute, report, and persist state" in bounded bursts rather than long-lived loops. The investigation flagged this as the genuinely interesting idea — discrete, budgetable, schedulable, auditable execution. *(Cross-source note: a separate landscape writeup calls the heartbeat model "a real innovation worth its own evaluation." Treat the architectural claim as medium-confidence — it is consistent across our notes but traces back to upstream README/marketing, which the investigation's own rule treats as aspirational until code-verified.)*
- **It coordinates agents; it is not an agent framework.** Paperclip drives external coding agents (Claude Code, Codex, Cursor, OpenClaw, HTTP/web bots) through adapters — the organizational layer above existing agents, not a replacement for them.

What it explicitly **is not**, per the analysis: it is not [[event-graph|EventGraph]]; it is not v3.9 [[work|Work]] (despite heavy task-orchestration overlap); and it is not the [[dark-factory]] kernel, [[authority-layer|authority layer]], or release-certification model. Its "strong product governance concepts" — board approval, budgets, strategy overrides, pause/terminate, config rollback, audit logs — "are **not** v3.9 AuthorityRequest / AuthorityDecision / ExecutionReceipt unless mapped." Its audit log "is not EventGraph unless integrated."

## Why pattern-only, and not adopted

The investigation's marginal-contribution verdict was that Paperclip is **"the strongest external reference for organization/company-level agent orchestration"** — and simultaneously the one most likely to become a parallel controller if imported wholesale. The recorded risks:

- Could become a **duplicate factory controller**, competing with [[work|Work]] / [[site|Site]] / [[hive-governance|Hive]] boundaries.
- The company/org metaphor conflicts with the stricter EventGraph/Work/Site separation.
- **Heartbeat execution and plugins can bypass the [[runtime-broker|RuntimeBroker]]** — i.e. become a hidden executor outside the bounded runtime.
- Telemetry is enabled by default and would have to be disabled/reviewed for sensitive factory work.
- The audit surface is not tamper-evident truth unless wired into EventGraph.

The recommendation followed directly: *"Include as high-value product/UX/reference architecture only. Do not adopt as core control plane. Mine for Work/Site/Hive design patterns: org chart, budgets, heartbeats, approvals, routines, plugin boundaries, company export/import, and audit surface."* This is the same containment logic the arc applies to every external control-plane candidate — the useful surfaces are absorbed; the authority is not ceded.

## Where its patterns are allowed to land

The one place the investigation pointed Paperclip's surfaces is **Gap G6 — Site operator UX / proof-of-work**. The gap analysis lists Paperclip as candidate evidence ("org chart, budgets, approvals, heartbeats, company/goal/task model") for enriching [[site|Site]] without replacing it, and proposes borrowing a **proof-of-work packet** idea from Symphony / gStack / Paperclip — *but EventGraph-linked*: work item, runtime invocation, changed files, tests, CI status, review feedback, security results, operator decision. The crosswalk binds this to **Epic 4 operator workflow** as the only owning epic, and only *if used*. As of this compile, no epic has reopened it; the decision is frozen at the v3.9 reference point.

## Fail-legible notes

- **Thin internal evidence.** The investigation inspected **only the README** ("actual implementation not inspected beyond README"). Every claim about Paperclip's internals — data model, heartbeat semantics, plugin boundaries, governance behaviour — is README-grounded, not code-verified. Mark the repo-internals confidence **thin**.
- **Source nuance on default branch.** The Batch D note records the fork's default branch as `master` (2026-05-13). This is a low-stakes detail and not re-verified live this run; flagged for completeness, not as a contradiction.
- **Traction figures are context, not evidence.** Star counts appear in our notes (a landscape writeup cites ~38k stars in under four weeks; the live upstream shows ~70k on 2026-06-13). These are upstream-marketing signals carried as context only; they played no part in the decision, which turned on architecture and boundary risk.
- **Upstream is cited, never re-published.** Per org rule, `paperclipai/paperclip` is public OSS. Its README headline ("the app people use to manage AI agents for work") and MIT license are corroborated live as context for *why we forked it to read it*, not as content to mirror. The wiki subject is our investigation and our decision.
- **Asserted, not proven.** The framing that Paperclip's org/budget/approval model "implies control-plane authority" is the investigation's risk assessment, not a demonstrated failure — it is the reason the decision is fenced to UX-only, not a record of harm observed.

## Sources & provenance

- v3.9.1 **External Technology Decision Crosswalk** — `/Transpara/transpara-ai/repos/docs/dark-factory/v3.9/implementation/epics/02-technology-decision-crosswalk-v3.9.md` (decision row L84; per-item note "Decision: UX pattern only" L197-201; freeze/reopen policy L41-68). This is the authoritative decision record.
- **Phase 4 Batch D** candidate analysis — `…/research/checkpoints/2026-05-13-06-phase-4-batch-d-governance-self-evolution-platform-tooling.md` (Paperclip section L455-592, inclusion matrix L587-592). Primary evidence for what the investigation found; explicitly README-only.
- **Investigation kickoff** — `…/research/checkpoints/2026-05-13-civilization-landscape-investigation-kickoff.md` (ground rules L9-27; scope L42-71; Paperclip as candidate 16 / `transpara-ai/paperclip`).
- **Phase 6 gap analysis** — `…/research/checkpoints/2026-05-13-08-phase-6-gap-analysis-versus-v3-8.md` (Gap G6 Site operator UX, Paperclip as candidate evidence + EventGraph-linked proof-of-work packet, L447-505).
- **Investigation closeout** — `…/research/checkpoints/2026-05-13-10-civilization-landscape-investigation-closeout.md` (final inclusion summary: pattern/reference + defer, L132-163).
- **Fork metadata** — GitHub API `repos/transpara-ai/paperclip`, fetched 2026-06-13: `isFork=true`, `parent=paperclipai/paperclip`, `createdAt=2026-03-17T17:54:05Z`, `description="Open-source orchestration for zero-human companies"`.
- **Upstream (context only, not re-published)** — `github.com/paperclipai/paperclip` README headline and MIT license badge (https://github.com/paperclipai/paperclip), fetched 2026-06-13.

**Conflicts / open items:** none material to the decision. The only cross-source wrinkles are (1) the fork-internals confidence is thin because only the README was read, and (2) star-count figures differ between an older research writeup and the live upstream — both are context, not load-bearing. `[[civilization-landscape-investigation]]`, `[[dark-factory]]`, `[[openclaw]]`, and `[[hive-governance]]` are forward references; `[[work]]`, `[[site]]`, `[[runtime-broker]]`, `[[event-graph]]`, `[[authority-layer]]`, and `[[gates]]` resolve to compiled articles.
