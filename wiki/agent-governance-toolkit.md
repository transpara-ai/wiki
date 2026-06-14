---
entity: Agent Governance Toolkit
aliases:
  - agent-governance-toolkit
  - transpara-ai/agent-governance-toolkit
  - Microsoft Agent Governance Toolkit
  - AGT
  - the PolicyEngineAdapter reference
tier: investigation
status: compiled
last_compiled: 2026-06-13
sources:
  - /Transpara/transpara-ai/data/repos/docs/dark-factory/v3.9/implementation/epics/02-technology-decision-crosswalk-v3.9.md  # v3.9.1 crosswalk; AGT decision row (L82) + per-item note (L175-189); freeze/reopen policy (L41-68)
  - /Transpara/transpara-ai/data/repos/docs/dark-factory/research/checkpoints/2026-05-13-06-phase-4-batch-d-governance-self-evolution-platform-tooling.md  # Phase 4 Batch D — repo-grounded ~25-field candidate analysis of transpara-ai/agent-governance-toolkit (section 6, L210-340; Gap D2 L623-639; inclusion matrix row L590)
  - /Transpara/transpara-ai/data/repos/docs/dark-factory/research/checkpoints/2026-05-13-civilization-landscape-investigation-kickoff.md  # investigation ground rules; AGT = candidate 14 (L191-192); access verified (L294)
  - /Transpara/transpara-ai/data/repos/docs/dark-factory/research/checkpoints/2026-05-13-07-phase-5-inclusion-marginal-contribution-matrix.md  # Phase 5 matrix — AGT row "Optional adapter / high-priority reference" (L136); highest-priority adapter ranking (L196-197)
  - /Transpara/transpara-ai/data/repos/docs/dark-factory/research/checkpoints/2026-05-13-08-phase-6-gap-analysis-versus-v3-8.md  # Gap G2 GovernancePolicyEngine / PolicyEngineAdapter gap; AGT as strongest candidate reference + 10-point adapter requirements (L151-200)
  - /Transpara/transpara-ai/data/repos/docs/dark-factory/research/checkpoints/2026-05-13-09-phase-7-proposed-canonical-updates.md  # Phase 7 U2 — PolicyEngineAdapter optional pattern, 14 adapter fields, required behavior (L147-200)
  - /Transpara/transpara-ai/data/repos/docs/dark-factory/research/checkpoints/2026-05-13-10-civilization-landscape-investigation-closeout.md  # closeout — AGT under "optional adapter/subsystem candidates" (L123); U2 in U1-U10 set (L218, L239)
  - /Transpara/transpara-ai/data/repos/docs/dark-factory/research/checkpoints/2026-05-13-11-v3.9-adversarial-review.md  # adversarial review — U2 present/strong (L118); H3 open defect: PolicyEngineAdapterDecision Tier 0 node has no schema, severity HIGH (L224-230, L439)
  - /Transpara/transpara-ai/data/repos/docs/dark-factory/v3.9/01-unified-architecture-decisions-v3.9.md  # Decision 13 (accepted ADR): PolicyEngineAdapter is optional and non-canonical (L149-164)
  - /Transpara/transpara-ai/data/repos/docs/dark-factory/v3.9/03-authority-identity-and-sops-v3.9.md  # PolicyEngineAdapter Pattern — normative adapter fields (L110+)
  - "GitHub API: repos/transpara-ai/agent-governance-toolkit (fork metadata, 2026-06-13 live)"  # isFork=true, parent=microsoft/agent-governance-toolkit, createdAt 2026-05-13T03:35:00Z, MIT, description (policy enforcement, zero-trust identity, execution sandboxing, 10/10 OWASP Agentic Top 10)
  - Open Brain  # 2026-05-18 v3.9 epic-roadmap adversarial-review capture: AGT + PageIndex "require human choice on dependency posture"; PR #61 reviewed-planning / implementation frozen
confidence:
  decision_row: high — AGT has a complete row in the v3.9.1 crosswalk, plus a per-item note, AND a ratified ADR (Decision 13), AND a proposed canonical update (U2). It is the most-decided external candidate in the investigation.
  fork_date_and_identity: high — confirmed live via GitHub fork metadata (parent microsoft/agent-governance-toolkit, createdAt 2026-05-13T03:35:00Z); the task-supplied fork date and upstream match the live API.
  repo_internals: thin — the investigation inspected only the README ("Primary evidence inspected: README.md"). Every internal claim (primitives, architecture, test count, framework adapters) is README-grounded, not code-verified.
  maturity_and_test_count: contested/context-only — "Public Preview", "13,000+ tests", "production-quality", "compliance alignment", "10/10 OWASP Agentic Top 10" are upstream README/marketing claims the investigation explicitly says "must be independently verified before dependency." Carried as context, not load-bearing.
  open_schema_defect: high — the adversarial review records a HIGH-severity open defect (H3): the U2 PolicyEngineAdapterDecision Tier 0 node is listed but has no per-node schema. This is a documentation gap in OUR kernel spec, not an AGT defect.
  open_brain_on_agt: thin — no Open Brain thought is specifically about the AGT decision; the closest corroboration is a 2026-05-18 v3.9-roadmap review note that AGT (with PageIndex) "require human choice on dependency posture."
---

# Agent Governance Toolkit

**A forked public project the [[civilization-landscape-investigation]] evaluated and ranked as its single highest-priority external reference — yet still declined to adopt as authority.** The Agent Governance Toolkit (AGT) is Microsoft's open-source runtime governance layer for AI agents: it sits between agent frameworks and the actions agents take, and evaluates every tool call, resource access, and inter-agent message against deterministic policy *before* execution. Transpara forked it into the `transpara-ai` org on **2026-05-13** (`transpara-ai/agent-governance-toolkit`, forked from the public upstream `microsoft/agent-governance-toolkit`) so it could be read as ground-truth source rather than from marketing pages — and the fork was created the *same day* the investigation ran. In the [[dark-factory]] landscape investigation (Phase 4, Batch D, **2026-05-13**) it was assessed against the canonical design and recorded in the v3.9.1 technology-decision crosswalk as **included as an optional adapter reference** — specifically the **`PolicyEngineAdapter` candidate**, the source that informed proposed canonical update **U2** and the accepted ADR **Decision 13**. Its theme — policy enforcement, zero-trust identity, execution sandboxing, and OWASP Agentic Top 10 coverage — maps directly onto the one platform gap the investigation flagged as blocking everything else: the absence of a concrete policy-enforcement implementation.

This article is about **our investigation and decision**, not a mirror of the upstream's documentation. The upstream is public OSS; per org rule it is cited here only as context and is never re-published.

## How AGT differs from its Batch D siblings

It is worth saying up front, because the shared "pattern-only" framing of forked candidates can flatten an important distinction. AGT was analysed in the same batch as [[paperclip|Paperclip]], [[gstack|gStack]], and `hermes-agent-self-evolution` (Batch D, "governance, self-evolution, and platform-tooling"). But where Paperclip and Multica landed as **UX-only patterns**, AGT landed one tier higher: as an **optional-adapter candidate** — the only Batch D member the investigation marked as the *strongest* candidate reference for a named native subsystem, and the only one that generated both a ratified ADR (Decision 13) and a proposed kernel-node type (`PolicyEngineAdapterDecision`). The Phase 5 matrix ranks it as the **highest-priority external reference** in the whole survey for accelerating a native capability. So this is not "learn a UI idea and import nothing"; it is "here is the strongest external implementation of a thing we must build natively — define an adapter boundary so we *could* use it, behind a fail-closed gate, without ever ceding authority to it."

## Where it sits in the decision crosswalk

The per-item record is the row in the v3.9.1 *External Technology Decision Crosswalk* (L82):

| Field | Value (per crosswalk, L82) |
|---|---|
| Item | Microsoft Agent Governance Toolkit |
| Current decision | **included as optional adapter reference** |
| ADR / doc ref | **v3.9 Decision 13; `PolicyEngineAdapter` pattern** |
| Integration mode | `PolicyEngineAdapter` candidate |
| Owning epic | **Epic 3 — Hive Governance Reconciliation** |
| Fork / adapter / pattern / exclude | **adapter** |
| Main risk | "license/supply-chain and authority mapping unreviewed" |
| PR #61 change required? | "yes: require license/conformance before integration" |

The per-item note is the binding pre-integration gate (crosswalk L175-189):

> Decision: optional `PolicyEngineAdapter` candidate.
> Before integration:
> - license reviewed
> - supply-chain reviewed
> - policy bundle version recorded
> - adapter decisions mapped to `AuthorityDecision`
> - execution results mapped to `ExecutionReceipt`
> - fail-closed behavior tested
> - **no LLM-dependent allow/deny decision**

The crosswalk's freeze policy applies in the adapter form: AGT may be used later only behind a defined adapter boundary, with license and supply-chain review, and no implementation owner is selected by the roadmap package yet. Reopening it to actually integrate would require an epic (Epic 3) to clear every line of the seven-point checklist first.

> ⚠ **Fail-legible note (which is the law).** The per-item crosswalk row is **reviewed planning**, not accepted-canonical doctrine — the crosswalk document is `status: review`, `canonical: false`. Unusually for an investigation candidate, AGT *also* has a ratified rule behind it: **v3.9 Decision 13** ("PolicyEngineAdapter Is Optional And Non-Canonical"), which is accepted ADR text. Decision 13 is the law; the crosswalk row is the bookkeeping that applies it. (The universal backstop, v3.9 Decision 15 — external frameworks stay outside control roles — also applies.)

## How it entered the arc

AGT was **candidate 14** of the [[civilization-landscape-investigation]] source list (kickoff L191-192) — a sweep that evaluated each external tool against the then-canonical Dark Factory v3.8 design for marginal contribution, under a hard operator rule: *no aspirational claims accepted without code or canonical-document evidence; if access to a repo is missing, stop — do not substitute upstreams or marketing pages.* The fork into `transpara-ai/agent-governance-toolkit` existed so the project could be read as source under that rule; the access-verification pass confirmed it was reachable (kickoff L294; access-verification checkpoint L113, L206-207).

A timing detail is worth recording because it differs from the other forked candidates: AGT's fork was created at **2026-05-13T03:35:00Z** (live GitHub metadata), i.e. on the *same day* the investigation's analysis ran — unlike [[paperclip|Paperclip]] (forked 2026-03-17, weeks earlier) and [[multica|Multica]] (task-supplied 2026-04-11). The fork and the read happened in the same window.

It was analysed in **Phase 4, Batch D** ("governance, self-evolution, and platform-tooling") and then carried forward through every later phase: Phase 5 ranked it highest-priority among optional adapters; Phase 6 named it the strongest evidence for closing **Gap G2**; Phase 7 turned that into the **U2** proposed canonical addition; the closeout placed it under "include as optional adapter/subsystem candidates" (L123) as part of the **U1-U10** update set; and the adversarial review confirmed U2 was present and well-constrained in the resulting v3.9 doctrine — while flagging one open schema defect (below).

## What the investigation found it to be

From the Batch D candidate analysis (section 6; evidence inspected: **README only**, L222-226):

> "A runtime governance toolkit for AI agents. It sits between agent frameworks and the actions agents take. Every tool call, resource access, and inter-agent message is evaluated against deterministic policy before execution."

The README features the analysis recorded (L234-245): a **policy engine, zero-trust identity, execution sandboxing, agent SRE, audit logs, an MCP security scanner, shadow-AI discovery, lifecycle management, a governance dashboard, multi-language packages, and OWASP Agentic Top 10 coverage.** A scoping line the analysis preserved and the wiki should keep: AGT "explicitly says it governs agent *actions*, not model-level *content safety*" (L248) — it is an authority/enforcement layer, not a model-output filter.

The core primitives the analysis catalogued (L256-274) are the cleanest summary of the shape: `PolicyEvaluator`, `PolicyDocument`, `PolicyRule`, `PolicyCondition`, `PolicyAction`; **zero-trust identity, trust scoring, execution rings, sandboxing, saga orchestration, a kill switch, SLOs/error budgets, replay debugging, an MCP scanner, agent discovery, lifecycle management, and audit events.** Architecturally it is described as an **external deterministic policy and governance layer that can wrap many agent frameworks** (L278), sitting **in the request path before agent tool/resource/message execution** (L282). Its integration surface (L300-302): Python, TypeScript, .NET, Rust, and Go packages, with framework adapters for Semantic Kernel, AutoGen, LangGraph, CrewAI, OpenAI Agents, Google ADK, LlamaIndex, and others, plus MCP integration.

What it explicitly **is not**, per the analysis (L250-252): it is **not** [[event-graph|EventGraph]]; **not** v3.8 [[work|Work]]; **not** the v3.8 authority-record model out of the box; and it is **application-level governance, not OS-kernel isolation**. That last line is load-bearing — see the risk below.

> ⚠ **Fail-legible note (maturity and scale claims are upstream marketing).** The analysis records AGT as "Public Preview" but "claims production-quality releases, 13,000+ tests, multi-language packages, and compliance alignment" — and immediately adds: **"Must be independently verified before dependency"** (L304-306). The "10/10 OWASP Agentic Top 10" coverage in the live fork description is likewise an upstream claim. None of these figures were code-verified by the investigation; they played no part in the decision, which turned on architecture and boundary fit. Carry them as context, not evidence.

## Why an adapter candidate, and not adopted as policy authority

The investigation's marginal-contribution verdict was blunt and is the reason AGT ranked first among adapters (Batch D L312-314): it is the **"strongest candidate for deterministic policy enforcement and runtime governance reference,"** and it "could accelerate v3.8 `GovernancePolicyEngine` and `RuntimeBroker` enforcement design." But strength is exactly what makes it dangerous to import naively. The recorded risks (Batch D L318-322):

- An **external policy engine can become a competing authority** if its decisions are not mapped into EventGraph records — the central risk the whole containment posture exists to prevent.
- **Same-process, application-layer governance does not replace sandbox/container isolation** — AGT's "execution sandboxing" is not OS-kernel isolation, so it cannot be treated as the runtime containment boundary on its own.
- **Public Preview may break before GA** — a dependency-stability risk.
- **Trust scoring could conflict with v3.8 authority outcomes** if adopted naively — AGT computes its own trust scores, which must never silently override EventGraph-recorded authority decisions.

The recommendation followed directly (Batch D L333-335): *"Include as high-priority reference and possible future adapter for policy enforcement. Do not replace v3.8 authority model; instead map AGT decisions into EventGraph `AuthorityDecision`/`ExecutionReceipt` records."* This is the same containment logic the arc applies to every external control-plane candidate — the useful capability is absorbed behind an adapter; the authority is not ceded.

## The gap it was selected to help close (Gap G2)

AGT is unusual among the candidates in being tied to a *specific named gap* in the native architecture. **Gap G2** (Phase 6, L151-200) is the absence of a concrete policy engine: "v3.8 requires protected-action policy and authority enforcement, but does not select a concrete policy engine implementation or adapter protocol." The gap analysis names AGT as **"the strongest candidate reference"** for it, providing "deterministic pre-execution policy evaluation, identity, sandboxing, audit, SRE, MCP scanning, lifecycle, and multi-language packages" (L159). The stakes were framed as foundational: "Without concrete policy enforcement, external runtimes, memory ingestion, deployments, capability changes, and protected actions cannot be safely enabled" (L163).

Critically, the gap analysis specified the **adapter requirements** that any AGT-like policy adapter must satisfy *before* it can be trusted — a fail-closed allowlist of obligations, not a denylist of prohibitions (L177-190). An adapter must: **fail closed; return a deterministic decision; record policy version, actor identity, protected-action type, and evidence inputs; emit an EventGraph `AuthorityDecision`; emit an `ExecutionReceipt` after attempted execution; support test fixtures without live services;** and **not replace the EventGraph authority-record model.** The recommended priority sequence kept the native engine first: "Implement native minimal policy engine first, *or* evaluate AGT as optional adapter" (P1.4, L171) — AGT is the accelerator, not the substitute.

## What it became in canonical doctrine: U2 and Decision 13

The gap and the candidate were promoted into two durable artifacts.

**Proposed canonical update U2 — `PolicyEngineAdapter` optional pattern** (Phase 7, L147-200; closeout U1-U10 set, L218/L239). The proposed addition states the boundary in one sentence: *"`PolicyEngineAdapter` is an optional deterministic policy evaluator that may assist `GovernancePolicyEngine`. It is never canonical authority by itself. Its output is advisory until recorded as EventGraph `AuthorityDecision` and followed by `ExecutionReceipt`."* U2 enumerates fourteen minimum adapter fields — including `adapter_id`, `adapter_version`, `policy_bundle_id`, `policy_bundle_hash`, `protected_action_type`, `actor_id`, `resource_refs`, `input_facts`, `raw_decision`, a `canonical_decision` enum (`autonomous | notify | approval_required | forbidden`), `reason_codes`, `evidence_refs`, `latency_ms`, and `failure_mode` — and a required-behavior list that repeats the fail-closed / no-LLM-allow-deny / version-recorded / mapped-to-AuthorityDecision-and-ExecutionReceipt / conformance-tested constraints. Its rationale is explicit about the candidate basis: *"Agent Governance Toolkit is a strong external reference for deterministic policy enforcement, but v3.8 must preserve EventGraph authority records as canonical."*

**Accepted ADR — v3.9 Decision 13: "PolicyEngineAdapter Is Optional And Non-Canonical"** (`01-unified-architecture-decisions-v3.9.md`, L149-164). This is the ratified law that turns U2 from proposal into doctrine. It names AGT directly: *"External policy engines, including `agent-governance-toolkit`-like references, may not replace EventGraph authority records, become policy owners, or certify actions."* The adapter is constrained to: **fail closed; deterministic; no LLM-dependent allow/deny decision; policy version recorded; adapter decisions mapped to `AuthorityDecision`; execution results mapped to `ExecutionReceipt`.** The normative field list lives in the `PolicyEngineAdapter Pattern` section of `03-authority-identity-and-sops-v3.9.md` (L110+), which restates that the adapter "is never canonical authority and cannot replace EventGraph `AuthorityRequest`, `AuthorityDecision`, or `ExecutionReceipt` records."

So the causal chain is clean and traceable: **Batch D ranks AGT the strongest policy-enforcement reference → Gap G2 names the missing native policy engine → U2 proposes the `PolicyEngineAdapter` optional pattern → Decision 13 ratifies it as optional-and-non-canonical, naming AGT explicitly.** AGT "made it into" v3.9 exactly the way every external tool did: as the *inspiration for a governed native pattern* (an adapter boundary with a fail-closed contract), never as a dependency or a policy owner.

## Where its patterns are allowed to land

The crosswalk binds AGT to **Epic 3 — Hive Governance Reconciliation** as the only owning epic, and only behind the seven-point pre-integration gate. As of this compile, no epic has selected AGT as an implementation dependency — there is **no implementation owner**. If Epic 3 (or a later ADR) reopens it for real integration, every borrowed decision must be mapped into EventGraph: AGT may *evaluate* a protected action, but the canonical authority decision and the post-execution receipt remain EventGraph records, fail-closed, with no LLM in the allow/deny path.

> ⚠ **Fail-legible note (one open defect — in OUR spec, not in AGT).** The v3.9 adversarial review found a **HIGH-severity** open defect tied to U2 (L224-230, L439): the kernel schema doc `02-kernel-schema-and-state-v3.9.md` lists `PolicyEngineAdapterDecision` as a Tier 0 node (line 183) but contains **no per-node schema block** for it — "a kernel implementer reading `02` will not know which fields a `PolicyEngineAdapterDecision` node carries… the kernel cannot persist a node type whose schema is undefined." The review proposed a concrete fix (lift the fields from the `03` PolicyEngineAdapter Pattern plus the two link fields mapping adapter decisions to EventGraph authority records). This is a documentation gap in *Transpara's own kernel spec*, not a defect in AGT — but it is the live, unresolved engineering item attached to this decision, and it is recorded here so the decision is not read as fully closed.

## Fail-legible notes

- **Thin internal evidence.** The investigation inspected **only the README** ("Primary evidence inspected: README.md", Batch D L222-226). Every claim about AGT's internals — the policy primitives, execution rings, saga orchestration, kill switch, trust scoring, MCP scanner, the framework-adapter list — is README-grounded, not code-verified. Mark the repo-internals confidence **thin**.
- **Maturity/scale claims are upstream marketing, flagged by the investigation itself.** "Public Preview", "13,000+ tests", "production-quality", "compliance alignment", and "10/10 OWASP Agentic Top 10" are upstream claims the Batch D analysis says "must be independently verified before dependency." They are context, not load-bearing, and did not drive the decision.
- **Fork date and upstream identity are confirmed live (not merely task-supplied).** Unlike [[multica|Multica]] (where the fork date was unverified), AGT's fork metadata was fetched live this run: `isFork=true`, `parent=microsoft/agent-governance-toolkit`, `createdAt=2026-05-13T03:35:00Z`, license MIT. The task-supplied fork date (2026-05-13) and upstream (`microsoft/agent-governance-toolkit`) both match the live API. Per org rule the upstream is cited as context only — never re-published, never pushed, never PR'd.
- **License is MIT, but supply-chain is explicitly unreviewed.** The README and live fork both report MIT; the Batch D analysis adds that "Microsoft trademark/branding constraints apply" and "production adoption needs package/license/security review" (L327), and the crosswalk's main-risk cell is precisely "license/supply-chain and authority mapping unreviewed." No license/supply-chain clearance has been performed; it is a gate, not a settled fact.
- **Asserted, not proven (the central risk).** The framing that an external policy engine "can become a competing authority" or that "trust scoring could conflict with v3.8 authority outcomes" is the investigation's **risk assessment**, not a demonstrated failure — AGT was never integrated, so there is no record of it bypassing an authority boundary in our systems. It is the reason the decision is fenced behind Decision 13's fail-closed, non-canonical contract, not a record of harm observed.
- **Open Brain is thin on AGT specifically.** No captured thought is about the AGT decision itself. The closest corroboration is a 2026-05-18 v3.9 epic-roadmap adversarial-review capture noting that AGT (together with PageIndex) is one of the items that "require human choice on dependency posture," consistent with the "no implementation owner selected" status and the PR #61 reviewed-planning / implementation-frozen record. Treat Open Brain as corroborating the *posture*, not as an independent source for the toolkit's internals.

## Sources & provenance

- v3.9.1 **External Technology Decision Crosswalk** — `/Transpara/transpara-ai/data/repos/docs/dark-factory/v3.9/implementation/epics/02-technology-decision-crosswalk-v3.9.md` (AGT decision row L82; per-item note "Decision: optional `PolicyEngineAdapter` candidate" L175-189; freeze/reopen policy L41-68). The per-item decision record; document status is `review` / `canonical: false`.
- **Phase 4 Batch D** candidate analysis — `…/research/checkpoints/2026-05-13-06-phase-4-batch-d-governance-self-evolution-platform-tooling.md` (AGT = section 6, L210-340, explicitly README-only; Gap D2 "GovernancePolicyEngine can borrow from AGT" L623-639; inclusion-matrix row L590). Primary evidence for what the investigation found.
- **Investigation kickoff** — `…/research/checkpoints/2026-05-13-civilization-landscape-investigation-kickoff.md` (ground rules; AGT = candidate 14 / `transpara-ai/agent-governance-toolkit`, L191-192; Batch D membership L418; access target L294).
- **Access-verification checkpoint** — `…/research/checkpoints/2026-05-13-access-verification-complete.md` (AGT access verified, L113, L206-207).
- **Phase 5 marginal-contribution matrix** — `…/research/checkpoints/2026-05-13-07-phase-5-inclusion-marginal-contribution-matrix.md` (AGT row "Optional adapter / high-priority reference … Evaluate as PolicyEngineAdapter; map decisions into EventGraph", L136; highest-priority adapter ranking L196-197).
- **Phase 6 gap analysis** — `…/research/checkpoints/2026-05-13-08-phase-6-gap-analysis-versus-v3-8.md` (Gap G2 GovernancePolicyEngine / PolicyEngineAdapter gap; AGT as strongest candidate reference; 10-point adapter requirements, L151-200).
- **Phase 7 proposed canonical updates** — `…/research/checkpoints/2026-05-13-09-phase-7-proposed-canonical-updates.md` (U2 PolicyEngineAdapter optional pattern; 14 adapter fields; required behavior; candidate basis = agent-governance-toolkit, L147-200).
- **Investigation closeout** — `…/research/checkpoints/2026-05-13-10-civilization-landscape-investigation-closeout.md` (AGT under "include as optional adapter/subsystem candidates" L123; U2 in the U1-U10 set L218, L239).
- **v3.9 adversarial review** — `…/research/checkpoints/2026-05-13-11-v3.9-adversarial-review.md` (U2 present and strongly constrained, L118; **H3 open defect** — `PolicyEngineAdapterDecision` is a Tier 0 node with no per-node schema, severity HIGH, L224-230, L439).
- **Accepted ADR** — `…/v3.9/01-unified-architecture-decisions-v3.9.md` **Decision 13** ("PolicyEngineAdapter Is Optional And Non-Canonical", naming `agent-governance-toolkit`-like references explicitly, L149-164). The ratified-canonical rule behind the crosswalk row.
- **Normative pattern fields** — `…/v3.9/03-authority-identity-and-sops-v3.9.md` `PolicyEngineAdapter Pattern` section (L110+).
- **Fork metadata** — GitHub API `repos/transpara-ai/agent-governance-toolkit`, fetched 2026-06-13: `isFork=true`, `parent=microsoft/agent-governance-toolkit`, `createdAt=2026-05-13T03:35:00Z`, license `MIT`, description "AI Agent Governance Toolkit — Policy enforcement, zero-trust identity, execution sandboxing, and reliability engineering for autonomous AI agents. Covers 10/10 OWASP Agentic Top 10."
- **Upstream (context only, not re-published)** — `github.com/microsoft/agent-governance-toolkit`. Cited solely to explain *why we forked it to read it*; the wiki subject is our investigation and our decision. Per org rule the upstream is public OSS — never re-published, never pushed, never PR'd.
- **Open Brain** — 2026-05-18 v3.9 epic-roadmap adversarial-review capture: AGT (with PageIndex) "require human choice on dependency posture"; the crosswalk landed via docs PR #61 as a reviewed-planning artifact with implementation frozen. Corroborates the posture/status, not the toolkit internals.

**Conflicts / open items.** No source conflict on the *decision*: "included as optional adapter reference / `PolicyEngineAdapter` candidate" is consistent across the crosswalk, the Phase 5 matrix, Gap G2, U2, the closeout, and Decision 13. The genuinely open items are (1) the **HIGH-severity schema gap** for `PolicyEngineAdapterDecision` in our own kernel doc `02` (adversarial review H3) — unresolved at the investigation's close; (2) **license/supply-chain review is a required gate, not done** — the crosswalk's main risk; (3) **repo-internals confidence is thin** because only the README was read; and (4) **maturity/scale figures are upstream marketing**, flagged by the investigation as needing independent verification before any dependency. `[[civilization-landscape-investigation]]`, `[[dark-factory]]`, `[[event-graph]]`, `[[work]]`, `[[paperclip]]`, `[[multica]]`, and `[[gstack]]` resolve to compiled articles; `[[runtime-broker]]` resolves to a compiled article. No forward-only references remain unresolved beyond standard arc cross-links.
