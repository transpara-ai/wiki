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
last_compiled: 2026-07-07
civilization_contribution: "Reference + pattern; the ratified PolicyEngineAdapter boundary (Decision 13), carried into accepted v4.0 (03:121). From a code-anchored read of transpara-ai/agent-governance-toolkit @ 6dc05da (v3.6.0; TAI-RES-2026-009), AGT is the strongest code-verified external reference for the deterministic, no-LLM policy-adapter contract — its allow/deny path contains zero LLM (Decision 13's hardest constraint, met) — but its empty-policy baseline is fail-OPEN, its '10/10 OWASP' is SAMPLE-grade regex, and it carries its own competing trust/audit/identity planes. Eligible only as an optional deterministic PolicyEngineAdapter reference whose decisions are advisory until recorded as an EventGraph AuthorityDecision + ExecutionReceipt; never policy owner, release/certification authority, kernel, or factory controller (Decision 13, Decision 15). Production adapter use gated behind Base Slice 0 and the open R-003 residual risk."
current_research_version: 1.0.0
sources:
  - "raw/civilization/external-landscape/tai-res-2026-009-agent-governance-toolkit-evaluation.md"  # TAI-RES-2026-009 v1.0.0 — the code-anchored evaluation (this page's primary source); read transpara-ai/agent-governance-toolkit @ 6dc05da
  - https://github.com/transpara-ai/agent-governance-toolkit/tree/6dc05da  # evaluated commit 6dc05da5efcddddf711164d6cd973fcfc19a0625, VERSION 3.6.0; fork of microsoft/agent-governance-toolkit — read from a local clone. UPSTREAM/FORK CONTEXT ONLY, never re-published, never a push/PR target
  - /Transpara/transpara-ai/repos/docs/dark-factory/v3.9/01-unified-architecture-decisions-v3.9.md  # Decision 13 (PolicyEngineAdapter Is Optional And Non-Canonical, names agent-governance-toolkit, L149-164); Decision 15 (L172-174)
  - /Transpara/transpara-ai/repos/docs/dark-factory/v3.9/02-kernel-schema-and-state-v3.9.md  # PolicyEngineAdapterDecision node schema (L345-363, H3 RESOLVED); "adapter evidence only" (L522)
  - /Transpara/transpara-ai/repos/docs/dark-factory/v4.0/03-civilization-governance-and-authority-v4.0.md  # accepted v4.0 authority records (L113-119) + PolicyEngineAdapter Pattern (L121-158) + external-policy-engine rule (L158)
  - /Transpara/transpara-ai/repos/docs/dark-factory/v4.0/implementation/epics/epic-21-residual-risk-r003-reidentification/01-residual-risk-r003-reidentification-design-v4.0.md  # implementation-residual R-003: production policy-adapter use OPEN; local-emulation closed (L69-89)
  - /Transpara/transpara-ai/repos/docs/dark-factory/v3.9/implementation/epics/02-technology-decision-crosswalk-v3.9.md  # v3.9.1 crosswalk AGT decision row (L82) + seven-point pre-integration gate (L175-189); status: review
  - /Transpara/transpara-ai/repos/docs/dark-factory/research/checkpoints/2026-05-13-06-phase-4-batch-d-governance-self-evolution-platform-tooling.md  # Phase 4 Batch D — README-ONLY candidate analysis (section 6); superseded for "what it is" by TAI-RES-2026-009
  - /Transpara/transpara-ai/repos/docs/dark-factory/research/checkpoints/2026-05-13-08-phase-6-gap-analysis-versus-v3-8.md  # Gap G2 (GovernancePolicyEngine / PolicyEngineAdapter gap); AGT as strongest candidate reference + adapter requirements
  - /Transpara/transpara-ai/repos/docs/dark-factory/research/checkpoints/2026-05-13-09-phase-7-proposed-canonical-updates.md  # Phase 7 U2 — PolicyEngineAdapter optional pattern (candidate basis = agent-governance-toolkit)
  - "GitHub API: repos/transpara-ai/agent-governance-toolkit (fork metadata)"  # isFork=true, parent=microsoft/agent-governance-toolkit, createdAt 2026-05-13T03:35:00Z, MIT, Public Preview
confidence:
  decision_row: high — AGT has a complete row in the v3.9.1 crosswalk, plus a per-item note, a ratified ADR (Decision 13), and a proposed-then-accepted canonical pattern (U2 → v4.0 PolicyEngineAdapter Pattern). Most-decided external candidate in the investigation, and — unlike PageIndex — carried into accepted v4.0 with no carry-forward gap.
  implementation_read: high — TAI-RES-2026-009 read the fork @ 6dc05da (VERSION 3.6.0): the agent-os policy engine, agent-mesh identity/trust plane, agent-hypervisor rings/saga/kill-switch, agent-sandbox isolation, agent-sre SLO/replay, discovery/marketplace/rag/mcp packages, CI, and the multi-language siblings.
  primitives_and_no_llm: code-verified — the five README primitives (PolicyEvaluator/PolicyDocument/PolicyRule/PolicyCondition/PolicyAction) and all twelve marquee primitives resolve to real classes; the allow/deny path contains ZERO LLM (evaluator.py:124) — Decision 13's hardest constraint, met in code. (Upgrades the prior page's "thin — README only" confidence.)
  fail_open_baseline: code-verified — fail-closed on ERROR but fail-OPEN on the empty-policy baseline (default action ALLOW, evaluator.py:220; schema.py:68). Direct inverse of the Civilization default-deny law; load-bearing for the "never authority" half.
  owasp_10of10: contested/context-only — "10/10 OWASP Agentic Top 10" is a mapping-plus-SAMPLE-rules claim, not enforcement; prompt-injection/memory-guard are deterministic regex blocklists self-labeled "SAMPLE … you MUST review, customise, and extend … before production" (prompt_injection.py:50). Carried as context, not evidence.
  maturity_and_provenance: code-verified — Microsoft-authored (Copyright (c) Microsoft Corporation in 128 agent-os/src files; nothing Transpara-authored), MIT, "Public Preview" / Development Status 4-Beta (README.md:29), three majors in ~2 months. The "13,000+ tests" figure is corroborated as a Python-only magnitude (12,617 def test_ / 563 files / ~1.6% skipped).
  open_schema_defect: RESOLVED — the prior page's HIGH-severity H3 (PolicyEngineAdapterDecision Tier 0 node with no per-node schema) is fixed: a full schema block now lives at 02-kernel-schema-and-state-v3.9.md:345-363.
raw_documents:
  - "raw/civilization/external-landscape/tai-res-2026-009-agent-governance-toolkit-evaluation.md"  # sha256 f45a122536eef535f95ceed421d6b2838442bc03c6bc204f46597d153b9fb061; TAI-RES-2026-009 v1.0.0; session-authored Civilization external-landscape research, placed outside the browser-ingest inbox by design — provenance is git history + this frontmatter
---

# Agent Governance Toolkit

**A forked Microsoft project the [[civilization-landscape-investigation]] ranked as its single highest-priority external reference — and still declined to adopt as authority.** The Agent Governance Toolkit (AGT) is Microsoft's open-source runtime governance layer for AI agents: it sits between agent frameworks and the actions agents take, evaluating tool calls, resource access, and inter-agent messages against deterministic policy *before* execution. Transpara forked it into `transpara-ai/agent-governance-toolkit` (from public upstream `microsoft/agent-governance-toolkit`) so it could be read as ground-truth source. **TAI-RES-2026-009 upgrades this page from a README-only investigation stub to a code-anchored assessment** — it reads the actual fork at `6dc05da` (VERSION 3.6.0), a ~2,600-file, 15+ package multi-language monorepo — and finds the 2026-05-13 disposition correct and now provable from *both* sides: AGT is a genuinely strong reference (a real deterministic, **no-LLM** policy evaluator — Decision 13's hardest constraint, met in code), and it is precisely the thing that must never be authority (fail-open by default, carrying its own competing trust/audit/identity planes). The subject of this article is Transpara's evaluation and decision — not the upstream's documentation, which is cited only as context and, per org rule, never re-published, pushed to, or PR'd.

> 🔎 **Code-anchored findings (TAI-RES-2026-009, fork @ `6dc05da`, v3.6.0) — the load-bearing results.**
> - **Real, and stronger than the README could show.** The five named primitives (`PolicyEvaluator`/`PolicyDocument`/`PolicyRule`/`PolicyCondition`/`PolicyAction`) and all twelve marquee primitives (execution rings, saga compensation, kill switch, SLO/error budgets, replay, MCP scanner, shadow-AI discovery, lifecycle state machine, **Merkle-hash-chained audit**, **SPIFFE identity + signed mesh cards**, trust scoring) are real classes. The allow/deny path contains **zero LLM** (`evaluator.py:124`) — the exact deterministic property Decision 13 demands and PageIndex fails.
> - **But fail-OPEN by default.** Fail-closed on *error*, yet the empty-policy baseline defaults to `ALLOW` (`evaluator.py:220`; `schema.py:68`) — the inverse of the Civilization's default-deny law. This is the code-level reason AGT can never stand as authority unwrapped.
> - **"10/10 OWASP Agentic Top 10" is coverage-mapping, not enforcement.** Each category maps to a real class + tests, but the enforcement is deterministic **regex blocklists self-labeled "SAMPLE … you MUST review, customise, and extend … before production"** (`prompt_injection.py:50`). The sandbox its OWASP mapping cites is an in-process AST/import-hook linter; genuine container/VM isolation exists **uncited, one package over** (`agent-sandbox`).
> - **A suite, not a layer — Microsoft-owned, Public Preview.** 15+ packages (real core = `agent-os` + `agent-mesh`) carrying competing trust/reward, audit-ledger, and signed-identity planes; `Copyright (c) Microsoft Corporation` throughout; "Public Preview / Beta." "13,000+ tests" holds as a magnitude (**12,617** Python `def test_`).
> - **Two corrections to the prior page.** The HIGH-severity **H3 schema gap is RESOLVED** (`PolicyEngineAdapterDecision` now fully schema'd, `02-kernel-schema-and-state-v3.9.md:345`); and the "thin — README only" confidence on AGT's internals is now **code-verified**.
> - **Verdict UNCHANGED, now code-anchored:** an optional deterministic **`PolicyEngineAdapter` reference/pattern**, advisory until recorded as an EventGraph `AuthorityDecision` + `ExecutionReceipt`; never authority. Uniquely among the recent evaluations, the pattern it inspired is **live in accepted v4.0 doctrine** with an **open production gate** (R-003).

## What changed with TAI-RES-2026-009

The earlier page treated every internal claim as unverified upstream marketing ("Primary evidence inspected: README.md"). The code-anchored read replaces that with first-party findings:

| Area | Prior page (README-only) | Updated finding (code-anchored, `6dc05da`) |
|---|---|---|
| Core primitives | `PolicyEvaluator`/`PolicyDocument`/`PolicyRule`/`PolicyCondition`/`PolicyAction`, "thin — not code-verified" | **All real classes** in `agent-os/src/agent_os/policies/` (`evaluator.py:35`, `schema.py:34-74`) |
| Decision path | Assumed deterministic | **Verified: zero LLM** in allow/deny (dict/compare/`re.search` only; `evaluator.py:124`) — meets Decision 13's hardest constraint |
| Fail posture | Not examined | Fail-closed on error; **fail-OPEN on empty policy** (default `ALLOW`, `evaluator.py:220`) — inverse of default-deny |
| The twelve primitives | README labels | Real: rings (`hypervisor/models.py:46`), saga (`saga/state_machine.py:30`), kill switch (`security/kill_switch.py:75`), Merkle audit (`governance/audit.py:153`), SPIFFE (`identity/spiffe.py:20`), … |
| "10/10 OWASP" | Upstream claim, unverified | Mapping + **SAMPLE-grade regex**, not enforcement (`prompt_injection.py:50`); ~8/10 code-backed; ASI04 self-admitted gap |
| Sandboxing | "execution sandboxing" (claim) | Mapping cites an **in-process linter** (`agent-os/.../sandbox.py`); real isolation (`agent-sandbox`: Docker+gVisor/Kata/Hyperlight) is **uncited** and opt-in |
| Architecture | "an external policy layer" | A **15+ package suite** (real core `agent-os` + `agent-mesh`); one package (`agent-mcp-governance`) is a broken import at this pin |
| Multi-language / adapters | "multi-language packages, framework adapters" | **Substantive** in Py/TS/Rust/.NET (Go partial); **all 8 adapters real** (~38 in `agent-os/.../integrations/`) |
| "13,000+ tests" | Marketing, "verify before dependency" | **Magnitude corroborated:** 12,617 Python `def test_`, ~1.6% skipped, real assertions |
| Maturity / provenance | "Public Preview," Microsoft trademark | **Confirmed:** MIT, `Copyright (c) Microsoft Corporation`, Development Status 4-Beta, 3 majors/2 months |
| H3 schema defect | HIGH-severity **open** | **RESOLVED** — full `PolicyEngineAdapterDecision` schema (`02-kernel-schema-and-state-v3.9.md:345`) |

The result is not "adopt AGT." It is: AGT is a credible deterministic policy *evaluator* if — and only if — its decisions are wrapped in the Civilization's own default-deny, single-source-of-truth `AuthorityDecision` boundary.

## The boundary (adopted / ratified)

The governing boundary already exists in doctrine and — unlike [[pageindex|PageIndex]]'s pattern — **survived into accepted v4.0**. Authority is an EventGraph record: `AuthorityRequest → AuthorityDecision → ExecutionReceipt` (`03-civilization-governance-and-authority-v4.0.md:113`). An external evaluator's output is captured by the `PolicyEngineAdapterDecision` kernel node — now fully schema'd (`02-kernel-schema-and-state-v3.9.md:345`) with the fourteen adapter fields and the two link fields (`authority_decision_ref`, `execution_receipt_ref`) that bind an adapter decision to canonical authority — and it is "adapter evidence only" (`02:522`).

The ratified law is **Decision 13 — "PolicyEngineAdapter Is Optional And Non-Canonical"** (`01-unified-architecture-decisions-v3.9.md:149`), which names AGT directly: *"External policy engines, including agent-governance-toolkit-like references, may not replace EventGraph authority records, become policy owners, or certify actions,"* and constrains the adapter to **fail closed / deterministic / no LLM-dependent allow/deny / policy version recorded / mapped to `AuthorityDecision` and `ExecutionReceipt`.** Accepted **v4.0** restates the whole pattern (`03-...v4.0.md:121-158`) and the categorical line *"External policy engines are optional references or adapters only. They do not own policy, release authority, certification authority, or factory control"* (`:158`). The universal backstop is **Decision 15** (external frameworks stay outside control roles, `01:172`).

AGT supplies the deterministic evaluator; the Civilization boundary supplies the governance AGT lacks:

- an AGT decision enters as **advisory**, never truth, until recorded as a `PolicyEngineAdapterDecision` linked to an `AuthorityDecision`;
- the baseline is **default-deny** (the property AGT's fail-open baseline is missing);
- AGT's own trust scores and Merkle audit chain are **not** adopted as authority — the EventGraph remains the single source of truth;
- **production** adapter use is gated behind the open **implementation-residual R-003** — *"closed only for local-emulation policy-adapter and policy-bundle evidence; open for production"* (`epic-21-...-design-v4.0.md:69`) — and behind **[[base-slice-0|Base Slice 0]]**'s file/command/network/secret boundary proof.

## What AGT actually is — now code-anchored

AGT's clean README story ("an external policy layer") describes a minority slice of the code. It is a **15+ package platform suite** (its own `AGENTS.md:5`: "multi-package OSS monorepo"). The actual governance core is two packages: **`agent-os`** (~170K LOC — the policy engine, capability model, MCP gateway, content-screening) and **`agent-mesh`** (~43K LOC — a distributed identity/trust/policy control-plane: SPIFFE, Ed25519 signed "mesh cards," a gRPC identity service, a trust/reward economy, Helm/CRDs). The rest — `agent-sre`, `agent-marketplace`, `agent-discovery`, `agent-hypervisor`, `agent-sandbox`, `agent-lightning` — are adjacent platform subsystems. Two scoping claims resolve: "governs actions, not model content" is **contradicted** on the front page (the suite ships prompt-injection and memory-poisoning screening) but honestly re-admitted in `LIMITATIONS.md`; "application-level, not OS-kernel isolation" is **true and consistently documented** (`ARCHITECTURE.md:63`: the enforcement boundary "is the Python interpreter").

The distinction that matters for a governance architect: **absorb AGT's evaluator *contract*, never its *authority*.** Its trust/reward economy, its audit ledger, and its signed-identity plane are competing sources of truth — adopting AGT wholesale would import a second authority model, exactly what Decision 15 forbids.

## Why an adapter reference, not policy authority

The investigation's marginal-contribution verdict was that AGT is the *"strongest candidate for deterministic policy enforcement and runtime governance reference"* that *"could accelerate `GovernancePolicyEngine` and `RuntimeBroker` enforcement design"* — and the code raises that assessment (the no-LLM evaluator is exactly Decision 13's required shape; AGT emits a deterministic action — `allow | deny | audit | block` (`schema.py:34`) — that is exactly the adapter schema's `raw_decision`, leaving Transpara to define the `raw_decision → canonical_decision` mapping to the kernel node's `autonomous | notify | approval_required | forbidden` outcomes, which are the Civilization's, not AGT's). The recorded risks all hold, now code-anchored: an external policy engine **can become a competing authority** if its decisions are not mapped into EventGraph (AGT literally carries its own audit chain and trust economy); **application-layer governance does not replace container/kernel isolation** (the OWASP mapping cites an in-process linter, not the real `agent-sandbox`); and **Public Preview may break before GA** (three majors in two months). The recommendation is the containment logic the arc applies to every external control-plane candidate: absorb the capability behind an adapter; never cede the authority.

## How it entered the arc (reference)

AGT was **candidate 14** of the [[civilization-landscape-investigation]], analysed in **Phase 4, Batch D** ("governance, self-evolution, and platform-tooling," `2026-05-13`) — the same batch as [[paperclip|Paperclip]], [[gstack|gStack]], and `hermes-agent-self-evolution`, but ranked one tier higher as the *strongest* adapter candidate for a named native subsystem. The causal chain into doctrine is clean and traceable: **Batch D ranks AGT the strongest policy-enforcement reference → Gap G2 names the missing native policy engine → U2 proposes the `PolicyEngineAdapter` optional pattern → Decision 13 ratifies it as optional-and-non-canonical, naming AGT explicitly → accepted v4.0 carries the pattern forward (`03:121`).** AGT "made it into" the doctrine exactly the way every external tool did: as the inspiration for a governed native pattern, never as a dependency. The crosswalk binds AGT to **Epic 3 — Hive Governance Reconciliation** as the only owning epic, behind a seven-point pre-integration gate (license / supply-chain / policy-bundle-version / map-to-`AuthorityDecision` / map-to-`ExecutionReceipt` / fail-closed-tested / **no LLM-dependent allow-deny**), with **no implementation owner selected**.

## Decision record and ADR disposition

TAI-RES-2026-009 §4.4 makes the determination explicit:

- **Dark Factory ADR:** **yes — Decision 13** is the accepted, ratified decision (naming `agent-governance-toolkit`-like references), carried into accepted v4.0 as the `PolicyEngineAdapter Pattern`. There is **no standalone ADR file** for AGT (unlike [[mempalace|MemPalace]]'s ADR-0008); Decision 13 + the v4.0 pattern *is* the record. The prior page's **HIGH-severity H3 defect is resolved**.
- **Recommended ADR action:** **no new ADR now.** Nothing is adopted as a dependency, runtime, or control-plane component; the pattern is already ratified. A future native `GovernancePolicyEngine` + `PolicyEngineAdapter` would get its own Factory Order → TLC arc (design-stage CFADA as its decision record), with R-003 closure gating any *production* adapter use.
- **Civilization contribution:** **reference + pattern (adapter boundary).** AGT is the strongest *code-verified* external reference for the deterministic, no-LLM `PolicyEngineAdapter` contract; never policy owner, release/certification authority, memory/knowledge authority, kernel, or factory controller (Decision 13, Decision 15).

The adoption verdict: **carry AGT forward as the reference implementation of the optional deterministic `PolicyEngineAdapter` pattern, behind the EventGraph authority boundary, gated by Base Slice 0 and the open R-003 residual risk.** Not a runtime activation; no implementation owner.

## Fail-legible notes

- **Internal evidence is now code-anchored (was README-only).** The primitive list, the no-LLM decision path, the fail-open baseline, the twelve primitives, the multi-language parity, and the test magnitude are all read from the fork @ `6dc05da`. The prior "thin — README only" confidence is retired.
- **Provenance: Microsoft-authored, nothing Transpara-original.** `Copyright (c) Microsoft Corporation` appears in every source file (128 under `agent-os/src` alone); the fork inherited the upstream verbatim. License MIT. Per org rule the upstream is context only — never re-published, pushed, or PR'd.
- **"10/10 OWASP" and maturity are upstream claims, not evidence.** The coverage is a mapping-plus-SAMPLE-rules claim; the status is explicitly "Public Preview / Beta, breaking changes before GA." Carried as context; they did not drive the decision.
- **The central risk is asserted-then-code-corroborated, not observed harm.** AGT was never integrated, so there is no record of it bypassing an authority boundary in our systems — but the code now *shows* the mechanisms (fail-open baseline; its own trust/audit/identity planes) that make the "competing authority" risk concrete rather than hypothetical. It is fenced behind Decision 13's fail-closed, non-canonical contract.
- **"R-003" is overloaded in v4.0.** The `05` risk register's R-003 ("repo creation/deletion without authority") is a *different* item from the *implementation-residual* R-003 (production policy-adapter reliance) that gates AGT; `epic-21` states they are two registers. This page means the implementation-residual one.

## Sources & provenance

Primary source is the code-anchored evaluation; doctrine and prior research are first-party Transpara documents.

**Adopted / ratified (the durable contributions this reference informs):**
- `dark-factory/v3.9/01-unified-architecture-decisions-v3.9.md` — **Decision 13** (PolicyEngineAdapter Is Optional And Non-Canonical, naming AGT, `L149-164`) and **Decision 15** (`L172-174`). The ratified law.
- `dark-factory/v4.0/03-civilization-governance-and-authority-v4.0.md` — accepted-v4.0 **PolicyEngineAdapter Pattern** (`L121-158`); the pattern AGT inspired, alive in current doctrine.
- `dark-factory/v3.9/02-kernel-schema-and-state-v3.9.md` — the `PolicyEngineAdapterDecision` node schema (`L345-363`; H3 resolved).
- Gap G2 (`…2026-05-13-08-…`) and U2 (`…2026-05-13-09-…`) — the gap AGT was selected to help close and the proposed pattern that became doctrine.

**Reference / context:**
- `raw/civilization/external-landscape/tai-res-2026-009-agent-governance-toolkit-evaluation.md` — **TAI-RES-2026-009 v1.0.0**, the code-anchored evaluation (sha256 `f45a122536…`); this page is its digest and carries the full `file:line` anchors, the doctrine map, and the §4.4 determination.
- `dark-factory/v3.9/implementation/epics/02-technology-decision-crosswalk-v3.9.md` (`status: review`) — the AGT decision row (`L82`) + seven-point pre-integration gate (`L175-189`).
- `dark-factory/v4.0/.../epic-21-residual-risk-r003-reidentification/01-…-design-v4.0.md` (`L69-89`) — the open R-003 production-adapter gate.
- `dark-factory/research/checkpoints/2026-05-13-06-…` — the Phase 4 Batch D **README-only** candidate analysis, superseded for "what it is" by TAI-RES-2026-009.
- **Upstream / fork (context only, never re-published/pushed/PR'd):** `github.com/transpara-ai/agent-governance-toolkit` @ `6dc05da` (fork) and `github.com/microsoft/agent-governance-toolkit` (upstream). All marketing figures ("10/10 OWASP," "13,000+ tests," "production-quality") are the upstream's own; only the code-verified magnitudes are asserted here.

**Conflicts / open items.** No source conflict on the *decision*: "optional `PolicyEngineAdapter` reference, non-canonical" is consistent across the crosswalk, Gap G2, U2, Decision 13, and accepted v4.0. Genuinely open: (1) **production adapter use is an open residual risk** (R-003), only local-emulation closed; (2) **license/supply-chain clearance is a required gate, not done** (though the code shows MIT + a fail-closed license allowlist + published packages); (3) the newly code-surfaced **fail-open baseline** and **competing-authority planes** are the concrete reasons the fail-closed, non-canonical contract exists. Cross-links [[civilization-landscape-investigation]], [[dark-factory]], [[event-graph]], [[mempalace]], [[pageindex]], [[paperclip]], [[gstack]], [[multica]], [[runtime-broker]], [[work]], [[base-slice-0]] resolve to compiled articles. The correct status: strongest code-verified deterministic policy-adapter reference; no authority; no runtime activation; Base Slice 0 and R-003 first.
