---
entity: Multica
aliases: [multica, transpara-ai/multica, the managed-agent teammate platform]
tier: investigation
status: compiled
last_compiled: 2026-06-13
sources:
  - /Transpara/transpara-ai/data/repos/docs/dark-factory/v3.9/implementation/epics/02-technology-decision-crosswalk-v3.9.md  # v3.9.1 crosswalk; Multica decision row (L86) + per-item note (L209-213); freeze/reopen policy (L41-68)
  - /Transpara/transpara-ai/data/repos/docs/dark-factory/research/checkpoints/2026-05-13-05-phase-4-batch-c-agent-execution-orchestration.md  # Phase 4 Batch C — repo-grounded candidate analysis of transpara-ai/multica (section 11, L762-864; cross-cutting findings L1107-1301)
  - /Transpara/transpara-ai/data/repos/docs/dark-factory/research/checkpoints/2026-05-13-civilization-landscape-investigation-kickoff.md  # investigation ground rules, scope; multica = candidate 20 (L209-210); access verified (L266, L276)
  - /Transpara/transpara-ai/data/repos/docs/dark-factory/research/checkpoints/2026-05-13-07-phase-5-inclusion-marginal-contribution-matrix.md  # Phase 5 marginal-contribution matrix — multica row (L132)
  - /Transpara/transpara-ai/data/repos/docs/dark-factory/research/checkpoints/2026-05-13-10-civilization-landscape-investigation-closeout.md  # final inclusion summary — multica as pattern/reference (L141) and defer (L158)
  - /Transpara/transpara-ai/data/repos/docs/dark-factory/research/checkpoints/2026-05-13-08-phase-6-gap-analysis-versus-v3-8.md  # Gap analysis — multica as runtime/work-orchestration reference, not a runtime adapter (L216, L457, L825)
  - /Transpara/transpara-ai/data/repos/docs/dark-factory/research/checkpoints/2026-05-13-11-v3.9-adversarial-review.md  # adversarial review — "same containment as Paperclip" (L170, L189)
  - Open Brain  # civilization-landscape-investigation compile note (2026-06-13): U9 lineage, category-vocabulary layering, Decision 15 as the accepted law
confidence:
  decision_row: high — Multica has a complete row in the v3.9.1 crosswalk (pattern-only / UX-only) plus a per-item note
  batch_c_profile: high — Multica has a dedicated, repo-grounded section (11) in the Phase 4 Batch C checkpoint
  repo_internals: thin — the investigation inspected only the README ("primary evidence inspected: README.md"); every internal claim is README-grounded, not code-verified
  fork_date: reconstructed/task-supplied — the task states a fork date of 2026-04-11; NO source read this run states that date, and no live GitHub fork-metadata fetch was performed this run. The fork's existence is corroborated (access verified 2026-05-13); the specific date is not.
  upstream_identity: task-supplied/unverified — the task names upstream `multica-ai/multica`; no source read this run records the upstream org/parent repo name. Carried as task-supplied context only, not confirmed.
  license: unknown — the Batch C analysis states plainly "License not inspected."
---

# Multica

**A forked public project the [[civilization-landscape-investigation]] evaluated and declined to adopt as a control plane.** Multica is an open-source *managed agents platform* whose stated purpose is to turn coding agents into real teammates — assigning them issues, tracking their progress, and coordinating them on team boards across many agent CLI providers. It was forked into the `transpara-ai` org so it could be read as ground-truth source rather than from marketing pages, and analysed during the [[dark-factory]] landscape investigation (Phase 4, **Batch C**, "agent execution and orchestration", **2026-05-13**). It was recorded in the v3.9.1 *External Technology Decision Crosswalk* as **pattern-only** — specifically a **managed-agent / operator UX pattern** — with one binding constraint: it must **preserve the [[agent|Agent]] boundary**, never implying that the Agent owns authority or runtime execution.

This article is about **our investigation and our decision**, not a mirror of the upstream's documentation. The upstream is public OSS; per org rule it is cited here only as context and is never re-published.

## Where it sits in the decision crosswalk

The authoritative record is the row in the v3.9.1 *External Technology Decision Crosswalk*:

| Field | Value (per crosswalk, L86) |
|---|---|
| Current decision | **pattern-only** |
| ADR / doc ref | legacy coverage matrix / managed-agent UX reference |
| Integration mode | managed-agent / operator **UX pattern** |
| Owning epic | Epic 4 operator workflow *if used* |
| Fork / adapter / pattern / exclude | **pattern** |
| Main risk | "managed-agent UX can imply **Agent** authority" |
| PR #61 change required? | "yes: **must preserve Agent boundary**" |

The per-item note is the binding constraint (crosswalk L209-213):

> Decision: managed-agent UX pattern only.
> "Multica-like teammate boards must not imply that Agent owns authority or runtime execution."

In the canonical decision-category vocabulary this lands as a **UX-only pattern** — the same bucket as [[paperclip|Paperclip]], distinct from the broader "pattern-only" bucket that holds [[event-graph|EventGraph]]-adjacent design patterns. The crosswalk's view-layer register confirms the placement explicitly ("UX-only pattern — Paperclip, Multica"). The freeze policy applies: pattern-only adoptions are **frozen at the v3.9 reference point** and do not track upstream behaviour unless an epic explicitly reopens them; reopening Multica would require recording the upstream version reviewed, which pattern changed, and whether Dark Factory adopts, rejects, or defers it.

> ⚠ **Fail-legible note (which is the law).** The per-item crosswalk row is **reviewed planning**, not accepted-canonical doctrine — the crosswalk document is `status: review`, `canonical: false`. Per the investigation compile record (Open Brain), the one *accepted* law behind every row of this kind is v3.9 Decision 15: external frameworks stay outside control roles — never kernel, truth, Work, policy, release, certification, capability-promoter, controller, or Site. The Multica row is the application of that law to one candidate, not an independent authority.

## How it entered the arc

Multica was **candidate 20** of the [[civilization-landscape-investigation]] source list — a sweep that evaluated each external tool against the then-canonical Dark Factory v3.8 design for marginal contribution. The investigation ran under a hard operator rule: *no aspirational claims accepted without code or canonical-document evidence; if access to a repo is missing, stop — do not substitute upstreams or marketing pages.* The fork into `transpara-ai/multica` existed so the project could be read as source under that rule rather than from its website; the access-verification pass on 2026-05-13 confirmed `transpara-ai/multica` was accessible.

It was analysed in **Phase 4, Batch C** ("agent execution and orchestration"), alongside [[ob1|OB1]], `openclaw`, `MetaGPT`, `OpenManus`, `hermes-agent`, `hermes-example-plugins`, `solo-orchestrator`, and `symphony`. (Note: this is a different batch from [[paperclip|Paperclip]], which was Batch D "governance, self-evolution, platform-tooling" — the two are often paired in the closeout, but Multica's repo-grounded profile lives in the Batch C checkpoint.) The investigation closeout placed Multica in two lists at once: **include as pattern/reference only** *and* **defer until prerequisite controls exist** — useful as a design reference now, not integrable until the kernel-level boundaries it could violate are enforced.

The investigation's downstream synthesis folded Multica's contribution into proposed canonical update **U9** (operator-workflow / proof-of-work UX), alongside Paperclip, Symphony, and gStack — i.e. its operator/team surfaces informed a *governed native pattern*, never a dependency or controller. *(Cross-source note: the U9 lineage is recorded in the investigation compile note in Open Brain; the per-candidate matrix and gap analysis are the primary sources for the UX-pattern contribution itself.)*

## What the investigation found it to be

From the Batch C candidate analysis (section 11; evidence inspected: **README only**):

> "An open-source managed agents platform for turning coding agents into real teammates. It supports issue assignment, progress tracking, reusable skills, unified runtimes, multi-workspace isolation, a local daemon, cloud/self-hosting, and many agent CLI providers."

The core primitives the analysis recorded are the cleanest summary of the shape: **agents as teammates, issues, boards, comments, progress streaming, a local daemon, runtime auto-detection, skills, workspaces, and cloud/self-hosted deployment.** Its one-line characterisation in the batch summary: *"managed agent teammate platform for issues, runtimes, skills, and team boards."*

Architecture and runtime model, as the analysis recorded them (README-grounded):

- **Stack:** Next.js frontend, Go backend, PostgreSQL + pgvector, an agent daemon, and agent CLI runtimes.
- **Runtime model:** a **daemon detects and runs agent CLIs and streams progress** to a backend/dashboard — runtime auto-detection plus progress streaming is the genuinely distinctive idea the investigation flagged ("strong operator/team UX and daemon/runtime detection patterns").
- **Breadth of supported runtimes:** Claude Code, Codex, GitHub Copilot CLI, OpenClaw, OpenCode, Hermes, Gemini, Pi, Cursor Agent, Kimi, and Kiro CLI. (This breadth is precisely why it reads as a *managed-agent* platform rather than an agent framework — it orchestrates other agents.)
- **Data model:** issues, agents, workspaces, skills, runtime metadata, Postgres state.
- **Memory model:** "skills compound; pgvector included," but explicitly **not** the v3.8 memory model.

What it explicitly **is not**, per the analysis: it is **not** [[event-graph|EventGraph]], **not** the v3.8 [[work|Work]] DAG, **not** the [[runtime-broker|RuntimeBroker]], **not** policy authority, and **not** release certification. Its governance is "workspace roles/permissions implied, but not v3.8 authority records or certification gates."

## Why pattern-only, and not adopted

The investigation's marginal-contribution verdict was that Multica has **"high concept overlap with agent operations management, but only partial safe fit"** — strong operator/team UX, but a control plane that overlaps with Work/Site/RuntimeBroker and must not be adopted wholesale. The recorded risks (Batch C, section 11):

- Could **duplicate [[work|Work]] / [[site|Site]] / [[runtime-broker|RuntimeBroker]]** — three native boundaries it competes with at once.
- The **agent-as-teammate metaphor can bypass v3.8 authority / separation-of-duties** — the exact risk the crosswalk distils into "managed-agent UX can imply Agent authority."
- **Skills can become ungoverned capabilities** (outside the [[capability-evolution|CapabilityArtifact]] evidence model).
- A **cloud-first path may conflict with the local, deterministic [[base-slice-0|Base Slice 0]]**.

The Phase 5 marginal-contribution matrix records the recommendation in one line: *"Mine UX / runtime-inventory patterns only."* The gap analysis is precise about the boundary — Multica (with Symphony and Paperclip) is a **runtime/work-orchestration *reference*, not a runtime adapter itself**: its teammate boards, runtime inventory, and progress streaming may *inform* operator UX, but the bounded execution stays in the RuntimeBroker. This is the same containment logic the arc applies to every external control-plane candidate — the useful surfaces are absorbed; the authority is not ceded. The v3.9 adversarial review confirms it carries *"the same containment as Paperclip"*: "no v3.9 doctrine surface adopts them as orchestration."

## Where its patterns are allowed to land

The crosswalk binds Multica's surfaces to **Epic 4 operator workflow** as the only owning epic, and only *if used*. The gap analysis points the same way: Multica's "runtime inventory / team board UX" is candidate evidence for enriching [[site|Site]]'s operator surface without replacing it. As of this compile, no epic has reopened it; the decision is **frozen at the v3.9 reference point**. If reopened, any borrowed pattern must preserve the v3.9 evidence and authority boundaries — boards may *display* work, but assignment, execution, and approval remain in Work, the RuntimeBroker, and the [[authority-layer|authority layer]], recorded in EventGraph.

## Fail-legible notes

- **Thin internal evidence.** The investigation inspected **only the README** ("primary evidence inspected: README.md"). Every claim about Multica's internals — daemon behaviour, runtime auto-detection, skill semantics, data model, governance — is README-grounded, not code-verified. Mark the repo-internals confidence **thin**.
- **Fork date is task-supplied, not verified this run.** The task states Multica was forked into `transpara-ai` on **2026-04-11**. **No source read this run states that date**, and no live GitHub fork-metadata fetch was performed this run. What *is* corroborated is that `transpara-ai/multica` existed and was access-verified on 2026-05-13 (kickoff + access-verification checkpoints). The specific 2026-04-11 fork date is carried as **task-supplied / reconstructed**, not confirmed — distinct from sibling [[paperclip|Paperclip]], whose fork date was confirmed against the live GitHub API.
- **Upstream identity is task-supplied.** The task names the upstream as `multica-ai/multica`. **No source read this run records the upstream org or parent-repo name.** It is carried as task-supplied context only — and, per org rule, would in any case be cited as context, never re-published.
- **License unknown.** The Batch C analysis states plainly: *"License not inspected."* No license claim is made here.
- **Asserted, not proven (the central risk).** The framing that a "managed-agent teammate" UX "implies Agent authority" is the investigation's **risk assessment**, not a demonstrated failure — there is no record of Multica having bypassed an authority boundary in our systems (it was never integrated). It is the reason the decision is fenced to UX-only, not a record of harm observed.
- **Two-list placement is intentional, not a conflict.** The closeout lists Multica under both "include as pattern/reference only" and "defer until prerequisite controls exist." These are complementary, not contradictory: useful as a reference now; not integrable until the boundaries it could cross are enforced.

## Sources & provenance

- v3.9.1 **External Technology Decision Crosswalk** — `/Transpara/transpara-ai/data/repos/docs/dark-factory/v3.9/implementation/epics/02-technology-decision-crosswalk-v3.9.md` (Multica decision row L86; per-item note "Decision: managed-agent UX pattern only" L209-213; freeze/reopen policy L41-68). This is the authoritative decision record. Document status is `review` / `canonical: false`.
- **Phase 4 Batch C** candidate analysis — `…/research/checkpoints/2026-05-13-05-phase-4-batch-c-agent-execution-orchestration.md` (Multica = section 11, L762-864, explicitly README-only; cross-cutting orchestration/skill/board findings L1107-1301). Primary evidence for what the investigation found.
- **Investigation kickoff** — `…/research/checkpoints/2026-05-13-civilization-landscape-investigation-kickoff.md` (ground rules; Multica as candidate 20 / `transpara-ai/multica`, L209-210; access verified L266, L276).
- **Phase 5 marginal-contribution matrix** — `…/research/checkpoints/2026-05-13-07-phase-5-inclusion-marginal-contribution-matrix.md` (multica row, "Pattern / reference only … Mine UX/runtime inventory patterns only", L132).
- **Phase 6 gap analysis** — `…/research/checkpoints/2026-05-13-08-phase-6-gap-analysis-versus-v3-8.md` (Multica as runtime/work-orchestration reference not a runtime adapter, L216; team board / runtime inventory UX, L457, L825).
- **Investigation closeout** — `…/research/checkpoints/2026-05-13-10-civilization-landscape-investigation-closeout.md` (pattern/reference only L141; defer L158).
- **v3.9 adversarial review** — `…/research/checkpoints/2026-05-13-11-v3.9-adversarial-review.md` ("same containment as Paperclip" L170, L189).
- **Open Brain** — civilization-landscape-investigation compile note (2026-06-13): the U9 operator-workflow/proof-of-work lineage (Multica ← one of Paperclip/Multica/Symphony/gStack), the three-layer category vocabulary, and v3.9 Decision 15 as the one accepted law behind the per-item rows.
- **Upstream (context only, not re-published, not verified this run)** — the task names `multica-ai/multica` as upstream; no source read this run confirms the upstream org or a fork date. Treated as task-supplied context per org rule (upstream is public OSS; never re-published, never pushed, never PR'd).

**Conflicts / open items:** No source conflict on the *decision* (pattern-only / UX-only is consistent across crosswalk, Phase 5 matrix, gap analysis, adversarial review, and closeout). Two items are unverified rather than contested: the **2026-04-11 fork date** and the **`multica-ai/multica` upstream identity** are task-supplied and were not confirmed against any source or live fork metadata this run (unlike [[paperclip|Paperclip]], where fork metadata was fetched live). `[[civilization-landscape-investigation]]`, `[[dark-factory]]`, `[[agent]]`, `[[paperclip]]`, `[[work]]`, `[[site]]`, `[[runtime-broker]]`, `[[event-graph]]`, `[[authority-layer]]`, `[[capability-evolution]]`, `[[base-slice-0]]`, and `[[ob1]]` resolve to compiled articles; `[[symphony]]` is a forward reference (not yet compiled).
