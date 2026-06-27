---
entity: Solo Orchestrator
aliases: [solo-orchestrator, transpara-ai/solo-orchestrator, Solo Orchestrator Framework, the phase-gated methodology]
tier: investigation
status: compiled
last_compiled: 2026-06-13
sources:
  - /Transpara/transpara-ai/repos/docs/dark-factory/v3.9/implementation/epics/02-technology-decision-crosswalk-v3.9.md  # v3.9.1 crosswalk — NO per-item row for solo-orchestrator (the fail-legible gap); freeze/reopen policy L41-68
  - /Transpara/transpara-ai/repos/docs/dark-factory/v3.9/09-legacy-coverage-matrix-v3.9.md  # v3.9 ratified mapping — solo-orchestrator grouped with gstack/symphony/multica/paperclip (L257)
  - /Transpara/transpara-ai/repos/docs/dark-factory/research/checkpoints/2026-05-13-05-phase-4-batch-c-agent-execution-orchestration.md  # Phase 4 Batch C — candidate 12 deep-dive, README-only (L880-987)
  - /Transpara/transpara-ai/repos/docs/dark-factory/research/checkpoints/2026-05-13-07-phase-5-inclusion-marginal-contribution-matrix.md  # Phase 5 inclusion matrix — solo-orchestrator row (L133)
  - /Transpara/transpara-ai/repos/docs/dark-factory/research/checkpoints/2026-05-13-10-civilization-landscape-investigation-closeout.md  # closeout final inclusion summary — pattern/reference only (L132-148)
  - /Transpara/transpara-ai/repos/docs/dark-factory/research/checkpoints/2026-05-13-civilization-landscape-investigation-kickoff.md  # investigation ground rules + scope; solo-orchestrator is candidate 21 (L212-213), Batch C (L415)
  - /Transpara/transpara-ai/repos/solo-orchestrator/README.md  # local fork README (the one internal artifact the investigation inspected); L1-98
  - /Transpara/transpara-ai/repos/solo-orchestrator/LICENSE  # MIT, "Copyright (c) 2026 Karl Raulerson"
  - "GitHub API: repos/transpara-ai/solo-orchestrator (fork metadata, 2026-06-13 live)"  # isFork=true, parent=kraulerson/solo-orchestrator, createdAt 2026-05-01T08:59:49Z, license=mit
  - "Upstream context only (not re-published): github.com/kraulerson/solo-orchestrator — fork parent, fetched 2026-06-13"
  - "raw/inbox/2026-06-24/solo-orchestrator/TAI-RES-2026-005-v1.0.0-Solo-Orchestrator-Evaluation-69a6250ee846.md"  # added via wiki browser ingest 2026-06-24
  - "raw/inbox/2026-06-24/solo-orchestrator/TAI-RES-2026-005-v1.1.0-Solo-Orchestrator-Evaluation-959878a544d6.md"  # added via wiki browser ingest 2026-06-24
confidence:
  decision: high — but indirect. Solo Orchestrator has NO individual row in the v3.9.1 crosswalk; its ratified decision is the grouped legacy-matrix line (L257) plus Phase 4/5/closeout. Stated as such below.
  fork_date_and_identity: high — confirmed live via GitHub fork metadata (createdAt 2026-05-01T08:59:49Z, parent kraulerson/solo-orchestrator)
  repo_internals: thin — the investigation inspected only the README ("Primary evidence inspected: README.md"); no code, scripts, or templates were read
  upstream_versioning: contested/context-only — the local fork carries conflicting upstream version labels ("Framework v4.1" in the initial commit vs "v1.0 release" in a sibling commit); upstream's own numbering, carried as context, not load-bearing
raw_documents:
  - "raw/inbox/2026-06-24/solo-orchestrator/TAI-RES-2026-005-v1.0.0-Solo-Orchestrator-Evaluation-69a6250ee846.md"
  - "raw/inbox/2026-06-24/solo-orchestrator/TAI-RES-2026-005-v1.1.0-Solo-Orchestrator-Evaluation-959878a544d6.md"

---

# Solo Orchestrator

**A forked public project the [[civilization-landscape-investigation]] evaluated and recorded as pattern-only.** Solo Orchestrator is an AI-assisted software-development *methodology* — a phase-gated, test-driven, documentation-mandatory process for a single technically literate person who builds applications with an AI coding agent as the execution layer. Transpara forked it into the `transpara-ai` org on **2026-05-01** (`transpara-ai/solo-orchestrator`, forked from the public upstream `kraulerson/solo-orchestrator`) so it could be read as ground-truth source rather than from a project page. During the [[dark-factory]] landscape investigation (Phase 4, Batch C, **2026-05-13**) it was assessed against the canonical design and folded into the ratified v3.9 doctrine as a **workflow / methodology pattern only** — its phase gates, security scans, and approval logs may *inform* implementation discipline, but it must never become a runtime, control plane, or truth/authority layer, and its Markdown/JSON process state is "not EventGraph."

This article is about **our investigation and decision**, not a mirror of the upstream's documentation. The upstream is public OSS; it is cited here only as context, never re-published.

## Fail-legible up front: there is no crosswalk row for it

The compile instruction was to ground this in the v3.9 technology-decision crosswalk and find Solo Orchestrator's decision row. **There is no such row.** The v3.9.1 *External Technology Decision Crosswalk* decision table holds sixteen items (MetaGPT, OpenManus, OpenBrain, MemPalace, the two Karpathy projects, Hermes, OpenClaw, the Microsoft Agent Governance Toolkit, [[gstack|gStack]], [[paperclip|Paperclip]], [[symphony|Symphony]], [[multica]], Miro Flow, Miro Thinker, and the Brett Brewer Org Memories analysis) — and Solo Orchestrator is **not one of them** (a literal search of the canonical file returns nothing). Notably, [[gstack|gStack]] *does* get its own crosswalk row even though Solo Orchestrator is grouped *with* gStack everywhere else, so the omission is a real gap in that document, not a naming mismatch.

What *is* known, and ratified, is the grouped decision in the v3.9 **Legacy Coverage Matrix**, which is the binding canonical statement that does cover it:

> `gstack/solo-orchestrator/symphony/multica/paperclip` → "workflow/operator UX/proof-of-work references only" · control boundary: "**Mine UX, gates, proof-of-work, and workflow patterns; no Work/Site/controller replacement.**"

So the decision is real and consistent across the investigation's own checkpoints (below); it simply lives in the legacy-coverage mapping and the Phase 4/5/closeout records rather than in the per-item crosswalk. **Everything in this article that depends on a per-item crosswalk note is marked thin** — because for this project, that note does not exist.

## Where it sits in the decision record

Because the crosswalk has no row, the authoritative trail is the investigation's phase outputs plus the ratified legacy matrix:

| Field | Value (per investigation record) | Source |
|---|---|---|
| Current decision | **pattern / workflow reference only** | Phase 5 matrix (L133); closeout "pattern/reference only" list (L142) |
| Integration mode | workflow + phase-gate methodology pattern | Phase 4 Batch C recommendation (L983) |
| Candidate class | Batch C (agent execution / orchestration) | kickoff (candidate 21, L212); Batch C roster (L415) |
| Maps onto | the v3.8 / v3.9 implementation workflow checklist (`08`) | Phase 5 (L133); Batch C (L987) |
| Main risk | "Markdown/process state not EventGraph"; can duplicate the existing implementation checklist if adopted wholesale | Phase 5 (L133); Batch C risks (L967-971) |
| Ratified boundary | "no Work/Site/controller replacement" | v3.9 Legacy Coverage Matrix (L257) |

In the canonical decision-category vocabulary this lands as **pattern-only** — and the crosswalk's freeze policy applies by analogy to every pattern-only adoption: such decisions are **frozen at the v3.9 reference point** and do not track upstream behaviour unless an epic explicitly reopens them, at which point the responsible epic must record the upstream commit reviewed, which pattern changed, and whether Dark Factory adopts, rejects, or defers it.

## How it entered the arc

Solo Orchestrator was **candidate 21** of the [[civilization-landscape-investigation]] source list — the one-time 2026-05-13 sweep that evaluated each external tool against the then-canonical Dark Factory v3.8 design for marginal contribution, under a hard operator rule: *no aspirational claims accepted without code or canonical-document evidence; if access to a repo is missing, stop — do not substitute upstreams or marketing pages.* The fork into `transpara-ai` (dated 2026-05-01, twelve days before the survey) existed so the project could be read as source under that rule.

It was analysed in **Phase 4, Batch C** ("agent execution and orchestration"), alongside `OB1`, `openclaw`, `MetaGPT`, `OpenManus`, the [[hermes-agent|Hermes]] family, and [[multica]]. The investigation closeout placed it cleanly in a single bucket — **pattern / reference only** — and, unlike Paperclip or Symphony, did **not** also list it under "defer until prerequisite controls exist." A methodology is not a runtime, so there were no kernel-level boundaries to fence off before its *ideas* could be borrowed.

## What the investigation found it to be

From the Batch C candidate analysis (evidence inspected: **README only**), Solo Orchestrator is:

> "A structured software development methodology for a single technically literate person building MVP-grade applications using AI as the execution layer. It is phase-gated, test-driven, documentation-mandatory, and includes security scanning, threat modeling, incident response, governance, POC modes, CI/CD templates, platform modules, and evaluation prompts."

The framework's own framing (local README, cited here as fork context) is blunt about its niche: *"This is not vibe coding. It's a phase-gated, test-driven, documentation-mandatory process with security scanning, threat modeling, and incident response built in."* It is built on and tested with Claude Code, but its README explicitly separates the durable methodology from the replaceable tooling — *"the methodology itself … is agent-agnostic … the operational automation layer that makes the autonomous workflow practical is Claude Code."*

The core primitives the investigation recorded:

> "five phases: Discovery, Architecture, Construction, Validation, Release · phase gates · Project Intake · Product Manifesto · Project Bible · ADRs · test gates · security scans · approval logs · platform modules · language/platform CI templates · Claude Code guardrails."

What it explicitly **is not**, per the same analysis: *"not a runtime execution engine, not EventGraph, not Work DAG, not a memory substrate, not release authority."* Its governance model is "strong process governance, approvals, enterprise governance documents, POC modes, and audit trail" — but, critically, *"Not v3.8 EventGraph authority records."* Its memory model (Qdrant MCP, optional) is "not primary."

## Why pattern-only, and not adopted

The marginal-contribution verdict was that Solo Orchestrator offers *"a concrete, practical phase-gated implementation methodology that can strengthen v3.8 implementation workflow, especially Base Slice implementation discipline and review gates."* That is genuine value — but it is **process discipline, not architecture**, and the [[dark-factory]] design already carried its own gate-first doctrine and implementation checklist. The recorded risks were therefore about *redundancy and substrate mismatch*, not control-plane capture:

- It "can duplicate v3.8 implementation checklist if adopted wholesale."
- "Claude Code-specific tooling may not be portable."
- "Markdown/JSON process state is **not** EventGraph truth" — the single most load-bearing objection, since the whole arc treats [[event-graph|EventGraph]] as the sovereign record and a parallel Markdown/JSON state would be authority-shaped evidence that the kernel never sees.

The recommendation followed directly: *"Include as pattern only for implementation workflow discipline, not as runtime/control plane."* This is the same containment logic the arc applies to every external candidate — absorb the useful surfaces, cede no authority.

## Where its patterns are allowed to land

The one place the investigation pointed Solo Orchestrator's surfaces is the **implementation-workflow checklist** (`08-implementation-workflow-checklist`). Both the Phase 4 and Phase 5 records map it there: *"align v3.8 `08-implementation-workflow-checklist` with useful Solo Orchestrator gate artifacts if marginal value is clear"* (Batch C), and *"Include workflow pattern only; translate useful gates if needed"* (Phase 5). Where its gates are borrowed, the investigation's standing instruction is to **translate them into EventGraph records rather than leaving them as Markdown** — i.e. a phase gate becomes evidence the kernel can verify, not a checkbox in a side file.

As of this compile, no epic has explicitly reopened it; under the freeze policy the decision stands at the v3.9 reference point. The ratified v3.9 acceptance "promoted no external framework to kernel, truth source, Work replacement, policy owner, release authority, certification authority, capability promoter, factory controller, or Site replacement" — Solo Orchestrator included.

## Fail-legible notes

- **No crosswalk row (the headline gap).** The instruction's premise — find this project's decision row in the v3.9.1 crosswalk — cannot be satisfied: the file has no Solo Orchestrator row. The decision is reconstructed from the ratified legacy-coverage matrix line and the Phase 4/5/closeout records, which agree. Treat any claim that *reads* like a per-item crosswalk note as **thin / reconstructed**, not quoted from the crosswalk.
- **Thin internal evidence.** The investigation inspected **only the README** ("Primary evidence inspected: README.md"). Every claim about Solo Orchestrator's internals — the init script, hooks, templates, CI pipelines, evaluation prompts, scripts — is README-grounded, not code-verified, even though those files exist in the local fork. Mark repo-internals confidence **thin**.
- **License is MIT, confirmed; the Batch C note said it wasn't inspected.** The Phase 4 analysis recorded *"License not inspected."* This run did inspect it: the fork's `LICENSE` is **MIT, "Copyright (c) 2026 Karl Raulerson,"** corroborated by the live GitHub fork metadata (`license=mit`). Stated to close the investigation's own open item, not as a contradiction.
- **Upstream versioning is inconsistent — and it is upstream's, not ours.** The local fork's git history labels the initial commit "Solo Orchestrator Framework v4.1" while a sibling commit says "v1.0 release." This is the upstream author's own numbering; it is carried as context only and plays no part in the decision.
- **Author / org-handle mismatch is cosmetic.** The fork parent is the GitHub handle `kraulerson`; the LICENSE copyright reads "Karl Raulerson." Same person; noted for completeness.
- **Upstream is cited, never re-published.** Per org rule, `kraulerson/solo-orchestrator` is public OSS. Its existence and description ("AI-assisted software development methodology for solo builders") are confirmed live as context for *why we forked it to read it*, not as content to mirror. The wiki subject is our investigation and our decision.
- **"Duplicates the checklist" is a risk assessment, not an observed failure.** The objection that adopting it wholesale "can duplicate v3.8 implementation checklist" is the investigation's forward-looking judgment — the reason it was fenced to pattern-only — not a record of harm.

## Where it sits relative to the rest of the survey

Solo Orchestrator is one of the **operator/workflow-UX cluster** the investigation treated as a single family: grouped with [[gstack|gStack]], [[symphony|Symphony]], [[multica]], and [[paperclip|Paperclip]] in the ratified legacy matrix, all five marked "workflow/operator UX/proof-of-work references only" with the same boundary — *no Work/Site/controller replacement.* Among them it is the **most methodology-pure**: gStack ships skills, Symphony packages trials, Multica and Paperclip are UX/control-plane products, but Solo Orchestrator is process doctrine first and tooling second. That is exactly why its risk profile is the mildest of the cluster (redundancy, not capture) and why it alone skipped the "defer until controls exist" bucket. It sits at the same hinge as the rest of the [[civilization-landscape-investigation]]: the moment [[dark-factory]] looked outward and chose to learn patterns from the agent-tooling landscape while importing none of it as authority.

## Sources & provenance

- **v3.9.1 External Technology Decision Crosswalk** — `/Transpara/transpara-ai/repos/docs/dark-factory/v3.9/implementation/epics/02-technology-decision-crosswalk-v3.9.md`. Cited for what it **lacks**: no Solo Orchestrator row exists in the decision table (literal search returns nothing); freeze/reopen policy at L41-68 applied by analogy. This is the document the compile was told to ground in; the gap is the finding.
- **v3.9 Legacy Coverage Matrix** — `/Transpara/transpara-ai/repos/docs/dark-factory/v3.9/09-legacy-coverage-matrix-v3.9.md` (Civilization Landscape Pattern Mapping, L257). The **ratified canonical decision** that does cover Solo Orchestrator: grouped "workflow/operator UX/proof-of-work references only," boundary "no Work/Site/controller replacement."
- **Phase 4 Batch C** candidate analysis — `…/research/checkpoints/2026-05-13-05-phase-4-batch-c-agent-execution-orchestration.md` (candidate 12, L880-987; inclusion-matrix row L1108). Primary source for what the investigation found; explicitly **README-only** ("Primary evidence inspected: README.md").
- **Phase 5 inclusion / marginal-contribution matrix** — `…/research/checkpoints/2026-05-13-07-phase-5-inclusion-marginal-contribution-matrix.md` (solo-orchestrator row L133: "Pattern / workflow reference … Include workflow pattern only; translate useful gates if needed").
- **Investigation closeout** — `…/research/checkpoints/2026-05-13-10-civilization-landscape-investigation-closeout.md` (final inclusion summary — "pattern/reference only," L142; not listed under "defer").
- **Investigation kickoff** — `…/research/checkpoints/2026-05-13-civilization-landscape-investigation-kickoff.md` (ground rules; candidate 21 / `transpara-ai/solo-orchestrator`, L212-213; Batch C roster L415).
- **Local fork README** (fork context, not re-published as upstream doc) — `/Transpara/transpara-ai/repos/solo-orchestrator/README.md`, L1-98: the framework's self-description, the five phases, the "not vibe coding" framing, and the methodology-vs-tooling separation.
- **LICENSE** — `/Transpara/transpara-ai/repos/solo-orchestrator/LICENSE`: MIT, "Copyright (c) 2026 Karl Raulerson."
- **Fork metadata** — GitHub API `repos/transpara-ai/solo-orchestrator`, fetched 2026-06-13: `isFork=true`, `parent=kraulerson/solo-orchestrator`, `createdAt=2026-05-01T08:59:49Z`, `license=mit`, `description="AI-assisted software development methodology for solo builders"`.
- **Upstream (context only, not re-published)** — `github.com/kraulerson/solo-orchestrator` (https://github.com/kraulerson/solo-orchestrator), confirmed as the fork parent on 2026-06-13.

**Conflicts / open items, stated not resolved.** (1) *The missing crosswalk row* — the per-item crosswalk has no Solo Orchestrator entry, so its decision is reconstructed from the ratified legacy matrix plus Phase 4/5/closeout; all agree on "pattern-only," but the per-item detail the crosswalk would normally hold does not exist for this project, and is marked thin throughout. (2) *Repo internals are thin* — only the README was read during the investigation; the fork's scripts/templates/pipelines were not. (3) *Upstream version labels conflict* ("v4.1" vs "v1.0") — upstream's own numbering, context-only. (4) *Batch C said the license was uninspected*; this run inspected it (MIT) — closing the open item, not contradicting it. `[[civilization-landscape-investigation]]` and `[[dark-factory]]` resolve to compiled articles, as do `[[event-graph]]`, `[[work]]`, `[[site]]`, `[[paperclip]]`, `[[multica]]`, `[[hermes-agent]]`, and `[[symphony]]`; `[[gstack]]` is a forward reference not yet compiled.
