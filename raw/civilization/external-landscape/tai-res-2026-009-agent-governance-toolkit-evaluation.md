---
document_id: TAI-RES-2026-009
title: Agent Governance Toolkit Capability Evaluation (Microsoft — Runtime Agent Policy, Identity, and Governance Suite)
subtitle: Code-Anchored Assessment Against the Transpara-AI Civilization Policy-Authority Boundary (PolicyEngineAdapter / Decision 13), and Strategic Learning Opportunities
version: 1.0.1
status: RELEASED
date: 2026-07-07
author: Michael Saucier
reviewer: Transpara AI Hive
owner: Research & Strategic Intelligence
org: Transpara AI
repo: transpara-ai/wiki
classification: PUBLIC — external-landscape research (this repo is public; no secrets; only public forked upstream code and already-published Civilization doctrine are quoted; the upstream `microsoft/agent-governance-toolkit` is cited as context and is never re-published, never a push/PR target)
companion_to: TAI-RES-2026-001 (Sakana AI), TAI-RES-2026-002 (Hermes Agent & Self-Evolution), TAI-RES-2026-003 (Google Open Knowledge Format), TAI-RES-2026-004 (MemPalace), TAI-RES-2026-005 (Solo Orchestrator), TAI-RES-2026-006 (Owain Lewis Work System), TAI-RES-2026-007 (PageIndex), TAI-RES-2026-008 (OB1 / Open Brain)
supersedes_for_presentation: "/Transpara/transpara-ai/repos/docs/dark-factory/research/checkpoints/2026-05-13-06-phase-4-batch-d-governance-self-evolution-platform-tooling.md"  # the 2026-05-13 Batch D candidate analysis was explicitly README-only ('Primary evidence inspected: README.md'); retained for provenance, superseded for the 'what it is' facts by the code-anchored read below
evaluated_artifact: https://github.com/transpara-ai/agent-governance-toolkit/tree/6dc05da  # transpara-ai fork @ 6dc05da5efcddddf711164d6cd973fcfc19a0625, VERSION 3.6.0; fork of microsoft/agent-governance-toolkit; read from a local clone
---

## Revision History

| Version | Date | Description | Author |
|---|---|---|---|
| 1.0.1 | 2026-07-09 | CFAR (cross-family review, Codex) corrections — evidence-accuracy only; verdict and §4.4 determination unchanged: (1) narrowed the copyright-header provenance from "every source file"/"throughout" to "most source files" (§2.1 + companion) — at pin `6dc05da` a few files (e.g. `agent-governance-golang/packages/agentmesh/identity.go`, `agent-os/src/agent_os/cli/cmd_policy_gen.py`) lack the header; the 128-under-`agent-os/src` count, MIT, and "nothing Transpara-authored; fork verbatim" are unchanged. (2) Corrected the Go policy engine (§2.8): it is fail-closed (`Deny` default, `policy.go:119-120`) with *optional* OPA/Cedar backends, not a default remote-HTTP fallback. (3) Corrected the npm supply-chain gate (§2.9): `supply-chain-check.yml` scans a non-existent root `packages/` dir at this pin and is effectively inert, so CI enforcement is partial rather than "mostly fail-closed." (4) Scoped the framework-adapter claim (§2.8) to the eight adapters examined — the README's "Works With Your Stack" table names twelve integrations plus "20+ more" — and corrected the workflow count 35→34 (§2.9). | Claude (Opus 4.8) / Hive |
| 1.0.0 | 2026-07-07 | Initial release — first **code-anchored** evaluation of the Agent Governance Toolkit (`transpara-ai/agent-governance-toolkit` @ `6dc05da`, VERSION 3.6.0, fork of `microsoft/agent-governance-toolkit`), read from a local clone. The eighth-plus in the external-landscape series and the third (after MemPalace TAI-RES-2026-004 and PageIndex TAI-RES-2026-007) to take a candidate that already had a compiled wiki page and **upgrade it from a README-only investigation stub to a code-anchored assessment** by reading the actual repository — a ~2,600-file, 15+ package multi-language monorepo. Supersedes the 2026-05-13 Batch D candidate analysis for the "what it is" facts. Capability comparison against the accepted **v4.0** doctrine baseline, with preserved **v3.9** supplying the `PolicyEngineAdapter` / `PolicyEngineAdapterDecision` schemas AGT maps to. Includes the §4.4 decision-record determination (Decision 13 is the accepted ADR-level decision; no new ADR created now; **optional deterministic policy-adapter reference / pattern**), five strategic learning opportunities, and the inverse analysis. Corrects two stale items in the prior page: the H3 kernel-schema gap is **resolved**, and the primitive/maturity claims the prior page flagged "thin — README only" are now largely **code-verified**. | M. Saucier / Hive |

---

## Abstract

This document evaluates the **Agent Governance Toolkit (AGT)** — Microsoft's open-source runtime governance layer for AI agents, forked into `transpara-ai/agent-governance-toolkit` — by reading the repository at HEAD `6dc05da` (VERSION 3.6.0) from a local clone. It is the code-anchored successor to the 2026-05-13 [civilization-landscape-investigation] Batch D candidate analysis, which was explicitly **README-only** ("Primary evidence inspected: README.md") and therefore carried every internal claim — the policy primitives, execution rings, saga orchestration, kill switch, trust scoring, MCP scanner, the "13,000+ tests" and "10/10 OWASP Agentic Top 10" figures — as unverified upstream marketing.

**The central finding is that the 2026-05-13 disposition was correct, and the code now proves *both* halves of it — one of which the README could not have shown, and one of which the marketing actively obscured.** AGT is a genuinely and substantially engineered artifact, not a doc skeleton: it ships a **real deterministic policy evaluator** (`PolicyEvaluator.evaluate(context) -> PolicyDecision`, `agent-os/src/agent_os/policies/evaluator.py:124`) whose allow/deny path contains **no LLM call anywhere** — dict lookups, comparisons, and `re.search` only — which means AGT meets, in code, the single hardest constraint the Civilization places on a policy adapter (Decision 13: "no LLM-dependent allow/deny decision"). The README's five named primitives (`PolicyEvaluator`, `PolicyDocument`, `PolicyRule`, `PolicyCondition`, `PolicyAction`) all exist as concrete classes, as do all twelve of the marquee "governance primitives" (execution rings, saga compensation, kill switch, SLO/error budgets, replay, MCP security scanner, shadow-AI discovery, lifecycle state machine, Merkle-hash-chained audit, SPIFFE identity, signed mesh cards, trust scoring). The project is multi-language for real (substantive independent policy logic in Python, TypeScript, Rust, and .NET; Go is partial), publishes to every major package ecosystem behind a fail-closed license allowlist, and its "13,000+ tests" is corroborated as a magnitude (12,617 `def test_` across 563 Python files, ~1.6% skipped, not parametrize-inflated).

**But the same read confirms exactly why AGT must remain an adapter reference and never authority.** Three findings are load-bearing. (1) The evaluator is fail-closed on *error* but **fail-OPEN on the empty-policy baseline**: with no policy loaded, the default action is `ALLOW` (`evaluator.py:220`; `schema.py:68` `PolicyDefaults.action = PolicyAction.ALLOW`) — the inverse of the Civilization's default-deny law. (2) The headline **"10/10 OWASP Agentic Top 10" is a *mapping-and-sample-rules* claim, not an *enforcement* claim**: each category points to a real class with tests, but the enforcement underneath is deterministic **regex blocklists the module itself labels "SAMPLE … you MUST review, customise, and extend … before deploying to production"** (`prompt_injection.py:50`), and the sandbox the OWASP mapping actually cites (`agent-os/src/agent_os/sandbox.py::ExecutionSandbox`) is an in-process AST-scan + import-hook that does not contain hostile Python — the genuine container/VM isolation lives one package over, in `agent-sandbox`, uncited by the mapping. (3) AGT is not "one deterministic policy layer" but a **15+ package platform suite** carrying **its own competing authority surfaces** — a distributed trust-scoring/reward economy, a Merkle-chained audit ledger, an Ed25519 signed-identity ("mesh card") plane — every one of which is exactly the kind of parallel truth/authority the Civilization forbids an external framework from owning.

Three provenance facts frame every conclusion: AGT is **Microsoft-authored** (128 files under `agent-os/src` carry `Copyright (c) Microsoft Corporation`; nothing in the audited code is Transpara-authored); it is **"Public Preview" / `Development Status :: 4 - Beta`**, three major versions in two months, "may have breaking changes before GA" (`README.md:29`); and the durable Civilization artifact it inspired — the `PolicyEngineAdapter` pattern — is **already ratified and carried into accepted v4.0**, with a now-complete `PolicyEngineAdapterDecision` kernel node and a still-open residual-risk gate on *production* adapter use.

The one-line result: **AGT decides whether an action is allowed; the EventGraph `AuthorityDecision` is the decision of record.** The disposition is unchanged and now firmer — an **optional deterministic `PolicyEngineAdapter` reference/pattern**, whose decisions are advisory until recorded as an EventGraph `AuthorityDecision` and followed by an `ExecutionReceipt`, gated behind Base Slice 0 and the R-003 production-adapter residual risk, and **never** policy owner, release authority, certification authority, or factory controller (Decision 13, Decision 15). §4.4 records the determination (Decision 13 is the accepted decision; no new ADR now; reference-plus-pattern contribution). Two stale items in the prior page are corrected: the **H3 kernel-schema defect is resolved** (`02-kernel-schema-and-state-v3.9.md:345` now carries a full `PolicyEngineAdapterDecision` schema), and the "thin — README only" confidence on AGT's internals is upgraded to code-verified.

---

## 1. Introduction and Scope

This evaluation re-opens the Agent Governance Toolkit research at the operator's request, to analyze it **the same way MemPalace was analyzed** in TAI-RES-2026-004 and PageIndex in TAI-RES-2026-007: read the actual upstream code rather than re-summarizing marketing, produce first-party Transpara findings with `file:line` anchors, and end with an explicit ADR / contribution determination. The prior AGT artifacts — the 2026-05-13 Batch D candidate analysis [B4], six later investigation checkpoints, the v3.9.1 technology-decision crosswalk row, and the compiled wiki page — were all grounded in a single README read and treated every internal claim as unverified upstream context. This document replaces that with a full read of the repository.

The evaluation covers, at HEAD `6dc05da` (VERSION 3.6.0):

- **The Python reference implementation** (`agent-governance-python/`, ~2,608 files across ~19 subprojects) — principally `agent-os` (the policy engine, capability model, MCP gateway, and content-screening modules — ~170K LOC), `agent-mesh` (the distributed identity/trust/policy control-plane — ~43K LOC), `agent-hypervisor` (execution rings, saga, kill switch), `agent-sandbox` (container/VM isolation), `agent-sre` (SLO/replay), `agent-discovery`, `agent-marketplace`, `agent-rag-governance`, `agent-mcp-governance`, `agent-runtime`, `agent-primitives`, `agent-lightning`, and `agentmesh-integrations`.
- **The non-Python packages** (`agent-governance-typescript/`, `-rust/`, `-dotnet/`, `-golang/`) for parity.
- **Repository metadata and CI** — `README.md`, `CHANGELOG.md`, `VERSION`, `LICENSE`, `NOTICE`, `pyproject.toml` files, `.github/workflows/`, `.clusterfuzzlite/`, and the OWASP mapping doc — all read as ground truth.

The Civilization baseline is the accepted **v4.0** doctrine set (`03-civilization-governance-and-authority-v4.0.md`, `04-production-workflow-runtime-v4.0.md`, `05-verification-audit-risk-eval-v4.0.md`, `06-autonomy-gates-and-current-state-v4.0.md`), with the preserved **v3.9** baseline supplying the detailed `PolicyEngineAdapter` pattern, the `PolicyEngineAdapterDecision` node schema, and Decisions 13 and 15.

**Boundary and provenance discipline.** The subject of this article is *Transpara's evaluation and decision about AGT*, not the upstream project's documentation. Per organization rules the upstream `microsoft/agent-governance-toolkit` is public OSS, cited only as context — never re-published, never pushed to, never a PR target. The transpara-ai fork exists so the project can be read as source; reading it changes nothing about the no-integration posture.

---

## 2. Agent Governance Toolkit: Capability Overview

### 2.1 The author and product surface (third-party-cited)

AGT is authored by **Microsoft** (`microsoft/agent-governance-toolkit`, created 2026-03-02, ~4,669 stars) and forked into `transpara-ai/agent-governance-toolkit` on 2026-05-13. Its self-description (`README.md`) is a runtime governance layer that "sits between your agent framework and the actions agents take," evaluating "every tool call, resource access, and inter-agent message … against deterministic policy before execution." The live fork description adds "Policy enforcement, zero-trust identity, execution sandboxing, and reliability engineering … Covers 10/10 OWASP Agentic Top 10."

Two surface facts are verified from repo metadata and matter downstream. **Provenance:** the code is Microsoft-authored — most source files carry `Copyright (c) Microsoft Corporation` (128 under `agent-os/src` alone; a few, e.g. `agent-governance-golang/packages/agentmesh/identity.go` and `agent-os/src/agent_os/cli/cmd_policy_gen.py`, omit the header), the license is **MIT** (`LICENSE`), and nothing in the audited code is Transpara-authored; the fork inherited the upstream verbatim. **Maturity:** the repository is explicitly **"Public Preview"** — *"Microsoft-signed, production-quality releases. May have breaking changes before GA"* (`README.md:29`, echoed at `CHANGELOG.md:9`) — and its `pyproject.toml` classifiers read `Development Status :: 4 - Beta` (`agent-os/pyproject.toml:29`). The cadence is aggressive: 19 changelog releases from 1.0.0 (2026-03-04) to 3.5.0 (2026-05-07), three major versions in about two months (the `VERSION` file already reads 3.6.0 while the changelog tops out at 3.5.0 — a minor drift).

### 2.2 The deterministic policy engine — code-anchored, and it is real

The README's central claim survives contact with the code. The core is `class PolicyEvaluator` (`agent-os/src/agent_os/policies/evaluator.py:35`) with `def evaluate(self, context) -> PolicyDecision` (`:124`); condition matching (`_match_condition`) uses only `==`, `<`, `in`, and `re.search` (`:315-343`). The five README primitives all exist as concrete classes: `PolicyDocument` (`policies/schema.py:74`), `PolicyRule` (`:51`), `PolicyCondition` (`:43`), `PolicyAction` (`:34`, an enum `allow | deny | audit | block`), with the decision object `PolicyDecision` (`evaluator.py:25`).

Enforcement is wired into the request path, not merely defined: `BaseIntegration.pre_execute_check()` runs the evaluator gate before a tool executes (`integrations/base.py:1053`, `:1096`); `PolicyInterceptor.intercept()` applies an allowlist and returns a deny result (`base.py:683`, `:700`); `CompositeInterceptor.intercept` short-circuits on the first deny (`:809`); and the Microsoft Agent Framework middleware denies before `call_next` (`maf_adapter.py:159`).

**The single most important positive finding:** the allow/deny path contains **no LLM call**. An exhaustive search for `openai` / `anthropic` / `litellm` / `.chat.completions` / `.messages.create` across `policies/`, `integrations/base.py`, and the governance decision modules returns zero matches; even the RAG content scanner self-documents "Pure regex — deterministic, zero LLM" (`agent-rag-governance/.../content_scanner.py:6`). This is exactly the property Decision 13 demands of a `PolicyEngineAdapter` and that PageIndex (an LLM-built index) categorically fails. AGT is the inverse of PageIndex on this axis.

### 2.3 Fail-closed on error, fail-OPEN on the empty baseline (load-bearing)

The evaluator's error handling is correct: any exception in the decision path returns `allowed=False, action="deny"` — "fail closed" (`evaluator.py:236-253`; mirrored at `base.py:962-964`). **But the no-match baseline is fail-open.** When no rule matches and no policy is loaded, the default action is `ALLOW`:

```python
# evaluator.py:219-222
# No rule matched — apply defaults
default_action = PolicyAction.ALLOW
if self.policies:
    default_action = self.policies[0].defaults.action
```

and the default it would inherit is itself permissive — `PolicyDefaults.action = PolicyAction.ALLOW` (`schema.py:68`). The integration-layer terminal path likewise defaults `allowed=True` (`decision.py:50`). The lone exception is the RAG governor's Cedar path, which is explicitly "default deny" (`agent-rag-governance/.../policy.py:191`). So AGT's *baseline* posture is permit-by-default, overridden only by explicitly-loaded deny rules. This is the direct inverse of the Civilization's first law — safety/authority gates default to DENY and fail closed — and it is the code-level reason AGT's decisions can never stand as authority on their own: an unconfigured or mis-wired AGT permits, where the Civilization must refuse.

### 2.4 The twelve marquee primitives — all real code constructs

The prior page listed AGT's primitives from the README and marked them "thin." Every one resolves to a real class (the two caveats are *naming*, not existence):

- **Execution rings** — `class ExecutionRing(int, Enum)` `RING_0_ROOT … RING_3_SANDBOX` (`agent-hypervisor/src/hypervisor/models.py:46`), assigned from a trust score via `from_eff_score()` and enforced by a `RingEnforcer`. (The prior term "execution rings" is real; it is a *privilege ring*, application-level, not a CPU ring.)
- **Saga orchestration** — a full compensation state machine: `class SagaState(str, Enum)` with `COMPENSATING`/`COMPENSATED` (`agent-hypervisor/src/hypervisor/saga/state_machine.py:30`) and `class SagaOrchestrator` with reverse-order `.compensate()` rollback (`saga/orchestrator.py:35`).
- **Kill switch** — `class KillSwitch` (`agent-hypervisor/src/hypervisor/security/kill_switch.py:75`) with a `KillReason` enum (behavioral drift / rate limit / ring breach / manual / quarantine timeout) and saga-handoff on termination.
- **SLOs / error budgets** — `class ErrorBudget` ("Error Budget = 1 − SLO target") and `class SLO` with real `burn_rate()` math (`agent-sre/src/agent_sre/slo/objectives.py:44`, `:167`, `:106`).
- **Replay debugging** — `class ReplayEngine` (`agent-sre/.../replay/engine.py:105`) plus a `TimeTravelDebugger` (`agent-os/modules/control-plane/.../time_travel_debugger.py:77`). *Nuance:* replay uses captured outputs as **mocks** and diffs divergence; it does not reseed RNG/clock for bit-exact re-execution, so "deterministic replay" is record-replay, not VM-determinism.
- **MCP security scanner** — `class MCPSecurityScanner` (`agent-os/src/agent_os/mcp_security.py:325`) with an `MCPThreatType` taxonomy (tool poisoning, rug-pull, cross-server, confused deputy, hidden instruction, description injection) and a `mcp-scan` CLI. (This lives in `agent-os`; the `agent-mcp-governance` package that appears to own it is a 25-line broken re-export — see §2.7.)
- **Shadow-AI discovery** — `agent-discovery` with process/GitHub/config scanners, a `ShadowAgent` model, and a `RiskScorer.score()` 0–100 heuristic (`agent-discovery/src/agent_discovery/risk.py:21`).
- **Lifecycle management** — `class AgentLifecycleState` (`agent-mesh/src/agentmesh/lifecycle/models.py:17`, `PENDING_APPROVAL … DECOMMISSIONED/ORPHANED`) with a `LifecycleManager` enforcing a `VALID_TRANSITIONS` state machine (`manager.py:65`).
- **Audit events** — tamper-evident: `class AuditEntry` (with `previous_hash`/`entry_hash`) and `class MerkleAuditChain` (`agent-mesh/src/agentmesh/governance/audit.py:23`, `:153`), plus HMAC-SHA256 `SignedAuditEntry` / `FileAuditSink` with timing-safe verification.
- **Zero-trust identity** — *the phrase* is a doc label (no `ZeroTrust` class exists); *the mechanism* is real SPIFFE: `class SVID` / `class SPIFFEIdentity` (`agent-mesh/src/agentmesh/identity/spiffe.py:20`, `:88`), managed-identity adapters (Entra/GCP), and Ed25519 signed "mesh cards" `class TrustedAgentCard` (`agent-mesh/src/agentmesh/trust/cards.py:19`).
- **Trust scoring** — real numeric scores (float 0–1 and int 0–1000) with a `TrustTier` enum (`agent-os/modules/nexus/reputation.py`) computed from behavioral history and consumed by ring assignment.

The engineering quality of these is generally high (the audit chain, SPIFFE registry, and MCP gateway are substantive). This is what a README cannot convey and what the code-anchored read adds: AGT is a *serious* implementation of the deterministic-policy-plus-identity idea.

### 2.5 The "10/10 OWASP Agentic Top 10" claim — mapping and sample rules, not enforcement

The "Covers 10/10 OWASP Agentic Top 10" headline is backed by a real mapping document (`agent-os/docs/owasp-agentic-top10-mapping.md`, ~20 KB) in which each ASI category points to a real, importable class with tests. It is **not** a bare marketing table. But two qualifications make it a *components-exist* claim, not a *risk-eliminated* one:

- **The enforcement is deterministic regex blocklists the code itself labels provisional.** Prompt-injection detection is hardcoded `re.compile(...)` phrase lists (`prompt_injection.py:195-258`) gated behind a module-level disclaimer: *"These are SAMPLE prompt-injection detection rules provided as a starting point. You MUST review, customise, and extend them for your specific use case before deploying to production"* (`prompt_injection.py:50`). `MemoryGuard` uses the same regex-plus-heuristic approach. These match literal English phrases — "ignore previous instructions" is caught; a paraphrase, translation, or novel jailbreak is not — and the upstream's own `LIMITATIONS.md` concedes AGT "does not detect indirect prompt injection" and positions itself as "Action Governance, Not Reasoning Governance."
- **Roughly eight of ten categories have runnable code plus tests; ASI04 (supply chain) is a self-admitted gap** (no runtime signature verification / SBOM at this pin; the SBOM RFC is "Draft"). What is solid is the *plumbing* — the `MCPGateway` (denylist → allowlist → param sanitization → atomic rate budget → human-approval, plus a response scanner that blocks credential/PII/exfiltration leaks and cannot "sanitize away" hard-block categories) is genuinely fail-closed and well-engineered.

The Civilization lesson is the same as PageIndex's benchmark lesson: the *discipline* (a category taxonomy mapped to conformance tests) is worth borrowing; the *headline number* oversells depth and must not be carried as evidence.

### 2.6 Sandboxing — an in-process guard the mapping cites, and real isolation it does not

This is the sharpest confirmation of a 2026-05-13 risk ("application-layer governance does not replace sandbox/container isolation"). There are two sandboxes:

- **The one the OWASP mapping cites for RCE (ASI05) and rogue-agent control (ASI10)** is `class ExecutionSandbox` (`agent-os/src/agent_os/sandbox.py`), an **in-process** guard: an AST static scan plus a `sys.meta_path` import hook, run in the *same* interpreter. The import hook only intercepts *new* imports, so already-cached modules (`os`, `sys`) re-bind without hitting it, and the AST scan is defeated by ordinary reflection gadgets. The one method that would restrict builtins at execution time, `create_restricted_globals` (`sandbox.py:346`), has **no caller in the package source** — its only invocations are in `test_sandbox.py` — so the runtime `execute_sandboxed` path relies on the hook + AST scan alone. This is a linter, not a container.
- **Genuine OS isolation exists one package over, in `agent-sandbox`** — a hardened Docker provider (`cap_drop:["ALL"]`, `seccomp`, `apparmor`, `no-new-privileges`, non-root user, read-only rootfs, network disabled) with gVisor/Kata auto-detection and a Hyperlight micro-VM provider. But it is **not referenced by the OWASP mapping**, and it *falls back to plain `runc`* (shared kernel) unless `runsc`/`kata` is installed, reporting `kernel_isolated=True` only for gVisor/Kata.

So AGT *can* provide kernel isolation, but not by default and not in the layer its own security mapping points at. The `agent-hypervisor`'s "rings" and "isolation," despite the name, are application-level accounting (trust-score → ring; VFS namespacing + reputation bonds), which the README labels an analogy.

### 2.7 Architecture — a suite of subsystems, not one policy layer

The README's clean single-layer story describes a *minority slice* of the code. AGT is a **15+ package platform suite** — its own `AGENTS.md:5` calls it a "multi-package OSS monorepo." The actual governance/policy core is two packages: **`agent-os`** (~170K LOC — the policy engine, capability model, MCP gateway, and content-screening modules) and **`agent-mesh`** (~43K LOC — a distributed identity/trust/policy control-plane: SPIFFE identity, signed cards, a gRPC `AgentMeshIdentityService`, a trust/reward economy, and Helm/CRDs). The remainder — `agent-sre` (SLO/chaos), `agent-marketplace` (plugin store), `agent-discovery` (network scanner), `agent-hypervisor`, `agent-lightning` (RL-training governance) — are adjacent platform subsystems that share a trust/identity model and a CLI, not one enforcement component. Tell-tales of assembly-by-accretion: inconsistent PyPI names (`agent-os-kernel`, `agentmesh-platform`, `agentmesh-runtime`, `agent-governance-toolkit`), re-export shims (`agent-runtime` wraps `agent-hypervisor` to dodge a name collision), and at least one **broken** package — `agent-mcp-governance/__init__.py:14` imports `agent_os.governance.middleware`, a module that **does not exist** at this pin, so the package raises `ImportError` on import.

Two scoping claims check out with a caveat and a confirmation. "Governs actions, not model content" is **contradicted on the front page** (the suite ships `prompt_injection.py` and `memory_guard.py`, which are content screening) but honestly re-admitted in `docs/LIMITATIONS.md`. "Application-level governance, not OS-kernel isolation" is **true and consistently documented** (`docs/ARCHITECTURE.md:63`: the enforcement boundary "is the Python interpreter").

### 2.8 Multi-language parity and framework adapters — verified substantive

The five-language claim holds. Independent policy logic — not SDK shims — exists in Python (reference), **TypeScript** (~26.5K LOC; local eval + 4-way conflict resolution), **Rust** (~18.4K; a full policy engine and MCP rug-pull detection), and **.NET** (~11.4K; local rule eval + a built-in Cedar evaluator); **Go** is partial (~5.2K; solid local prompt-defense/trust/rate-limit; its policy engine is fail-closed — `PolicyEngine.Evaluate` returns `Deny` when no rule matches and no backend is registered (`policy.go:83,119-120`) — and treats OPA/Cedar as *optional* external backends that reach the network only under an explicit `OPARemote` mode (`policy_backends.go:37,142`; the `auto` default expects the local OPA CLI, and Cedar runs CLI/builtin, not HTTP), rather than defaulting to a remote call). The eight major framework adapters examined here all exist as real code (Semantic Kernel, AutoGen, LangGraph/LangChain, CrewAI, OpenAI Agents, Google ADK, LlamaIndex, plus first-class MCP) — a subset of the README's "Works With Your Stack" table (twelve named integrations, including Microsoft Agent Framework, pi-mono, Haystack, Dify, and Azure AI Foundry, plus "20+ more"); the `agent-os/src/agent_os/integrations/` directory alone holds ~38 adapters, with the Semantic Kernel adapter using SK's native `add_filter()` API rather than a proxy stub.

### 2.9 Supply chain, tests, and CI

**Supply chain is comparatively mature, but its CI enforcement is only partial.** MIT license, no copyleft in any manifest; `dependency-review.yml` enforces a license **allowlist** (copyleft denied by omission). Packages ship to PyPI (`agent-governance-toolkit`, via Microsoft ESRP/ADO), npm (`@microsoft/agent-governance-sdk`), NuGet (`Microsoft.AgentGovernance`), crates (`agentmesh`), and Go; some package lockfiles are committed, and a `supply-chain-check.yml` job is *meant* to fail PRs on unpinned npm ranges — but at this pin it scans a non-existent root `packages/` directory (real manifests live under `agent-governance-*/`), so it matches nothing and is effectively inert, with its lockfile check only warning. Thirty-four workflows include CodeQL, ClusterFuzzLite (seven fuzz harnesses), SBOM, and OpenSSF Scorecard. **The real gap:** CodeQL scans only `[python, javascript-typescript]` and fuzzing is Python-only — .NET, Rust, and Go source receive no static analysis (no `cargo audit`/`govulncheck`/`gosec`). **Tests:** the "13,000+ tests" figure is corroborated as a Python-only magnitude — **12,617 `def test_` across 563 files, ~22,010 asserts, only ~1.6% skipped, not parametrize-inflated** — and spot-checks show real governance assertions (boundary checks, Hypothesis property tests, documented regressions), with a small (~3–5%) trivial `assert True` tail.

---

## 3. Transpara-AI Civilization: the policy-authority baseline (v4.0 accepted + preserved v3.9)

### 3.1 The primitives AGT maps to

The Civilization already has a defined home for an external policy engine, and — unlike PageIndex's `DocumentEvidenceRetriever` — it was **carried forward into accepted v4.0**. Authority is an EventGraph record: `AuthorityRequest → AuthorityDecision → ExecutionReceipt` (accepted v4.0, `03-civilization-governance-and-authority-v4.0.md:113-119`). An adapter's output is captured by a dedicated kernel node, `PolicyEngineAdapterDecision`, whose full schema now lives at `02-kernel-schema-and-state-v3.9.md:345-363`: `decision_id, adapter_id, adapter_version, policy_bundle_id, policy_bundle_hash, protected_action_type, actor_id, resource_refs, input_facts, raw_decision, canonical_decision (autonomous | notify | approval_required | forbidden), reason_codes, evidence_refs, latency_ms, failure_mode, authority_decision_ref, execution_receipt_ref, created_at`. It is explicitly "adapter evidence only" (`02:522`).

### 3.2 Decision 13 and the PolicyEngineAdapter Pattern (v3.9 → accepted v4.0)

The ratified rule is **v3.9 Decision 13, "PolicyEngineAdapter Is Optional And Non-Canonical"** (`01-unified-architecture-decisions-v3.9.md:149-164`), which names AGT directly: *"External policy engines, including agent-governance-toolkit-like references, may not replace EventGraph authority records, become policy owners, or certify actions."* The adapter is constrained to: **fail closed; deterministic; no LLM-dependent allow/deny decision; policy version recorded; adapter decisions mapped to `AuthorityDecision`; execution results mapped to `ExecutionReceipt`.**

Accepted **v4.0** restates the pattern in full (`03-...v4.0.md:121-158`) with the fourteen minimum adapter fields and the required behavior, plus the categorical line: *"External policy engines are optional references or adapters only. They do not own policy, release authority, certification authority, or factory control"* (`:158`). This is the crucial difference from the PageIndex evaluation: AGT's borrowed pattern is not a v3.9-only artifact with a v4.0 carry-forward gap — it is **live, accepted v4.0 doctrine**.

### 3.3 Decision 15, the R-003 production gate, and Base Slice 0

Three fences apply. **Decision 15** — external frameworks stay outside control roles — is the universal backstop (`01:172`). **Base Slice 0** gates any external adapter behind proven file/command/network/secret boundaries and replayable EventGraph receipts (accepted v4.0). And the **implementation-residual risk R-003** explicitly keeps *production* adapter use out of scope: it is *"closed only for local-emulation policy-adapter and policy-bundle evidence; open for production policy-adapter or policy-bundle reliance"* (`v4.0/.../epic-21-residual-risk-r003-reidentification/01-...-design-v4.0.md:69-77`), and any future closure requires an explicit `AuthorityRequest`/`AuthorityDecision` plus a full policy-decision trace (`:80-89`). (Note: "R-003" is overloaded — the `05` risk register's R-003 is "repo creation/deletion without authority," a different item; epic-21 is explicit that these are two registers. The AGT-relevant one is the *implementation-residual* R-003.)

---

## 4. Comparative Analysis

### 4.1 Capability / fit matrix

| Civilization need | AGT offers (code-anchored) | Fit | Boundary |
|---|---|---|---|
| Deterministic, no-LLM allow/deny (Decision 13) | `PolicyEvaluator.evaluate` — dict/compare/regex, zero LLM (`evaluator.py:124`) | **Strong** | Meets the hardest constraint; still advisory until recorded as `AuthorityDecision` |
| Default-deny / fail-closed gate | Fail-closed on *error*; **fail-OPEN on empty policy** (`evaluator.py:220`) | **Partial / mismatch** | Inverse of Civilization law; adapter must be wrapped in a default-deny boundary |
| Mapped decision shape | AGT emits `allow/deny/audit/block` (`schema.py:34`) — the adapter's `raw_decision`; Transpara maps it to canonical `autonomous/notify/approval_required/forbidden` | **Strong** | The `PolicyEngineAdapterDecision` schema separates `raw_decision` from the Transpara-defined `canonical_decision` |
| Protected-action taxonomy, identity, audit | Rings, kill switch, SPIFFE identity, Merkle audit — all real | **Reference-grade** | AGT's audit/identity/trust are *competing* planes; EventGraph remains truth |
| Runtime containment | `agent-sandbox` (Docker + gVisor/Kata/Hyperlight), not the in-process `ExecutionSandbox` the mapping cites | **Partial** | Real isolation is opt-in; app-level guard ≠ containment |
| Air-gap / offline | Policy eval is local & LLM-free; discovery/mesh assume networked control-plane | **Partial** | Vendor + pin; the mesh/relay is a networked dependency |
| Truth / certification | — | **Excluded** | Decision 13/15 — never policy owner, release, or certification authority |

### 4.2 Structural convergence — where AGT genuinely fits

AGT is the **strongest external reference the survey found for the deterministic `PolicyEngineAdapter` contract**, and the code raises, not lowers, that assessment. Three convergences are real: (1) the **no-LLM deterministic evaluator** is exactly Decision 13's required shape and AGT implements it cleanly; (2) AGT's evaluator emits a deterministic action from its own vocabulary — `allow | deny | audit | block` (`PolicyAction`, `schema.py:34`) plus separate human-approval labels — which is exactly the **`raw_decision`** the `PolicyEngineAdapterDecision` schema expects; the four canonical outcomes (`autonomous | notify | approval_required | forbidden`) are the *Civilization's* `canonical_decision`, not AGT's (the fork has no `canonical_decision` symbol), so what converges is that AGT supplies a clean deterministic raw decision and Transpara defines the short `raw_decision → canonical_decision` mapping; (3) AGT's fail-closed *plumbing* around errors, its conformance-test discipline, and its MCP-threat taxonomy are directly reusable as the shape of a native `GovernancePolicyEngine` + adapter conformance suite.

### 4.3 The seam — why "strong reference" and "never authority" are both true

The same read that strengthens the reference case also proves the containment case, on four seams: (1) the **fail-open baseline** (§2.3) is the inverse of default-deny law; (2) AGT carries **its own competing authority surfaces** — a trust/reward economy, a Merkle audit ledger, and a signed-identity plane — each of which the Civilization forbids an external framework from owning (Decision 15), so adopting AGT means deliberately *not* adopting its trust scores or audit chain as truth; (3) the **"10/10" depth** is SAMPLE-grade regex, so AGT's security posture cannot be inherited as evidence; (4) AGT is a **Microsoft-owned Public Preview suite**, so a dependency posture would import a fast-moving, externally-controlled 15-package surface. The correct read is the one Decision 13 already encodes: absorb the *contract*, never the *authority*.

### 4.4 Decision record, ADR disposition, and contribution determination

- **Dark Factory ADR:** **yes — Decision 13** ("PolicyEngineAdapter Is Optional And Non-Canonical," `01-unified-architecture-decisions-v3.9.md:149`) is the accepted, ratified decision, and it names `agent-governance-toolkit`-like references explicitly. There is **no standalone ADR file** for AGT (unlike MemPalace's ADR-0008); Decision 13 plus the accepted-v4.0 `PolicyEngineAdapter Pattern` (`03-...v4.0.md:121`) *is* the decision record. The prior page's **HIGH-severity H3 open defect is resolved**: `PolicyEngineAdapterDecision` now carries a full per-node schema (`02-kernel-schema-and-state-v3.9.md:345`).
- **Recommended ADR action:** **no new ADR now.** Nothing is adopted as a dependency, runtime, or control-plane component. The pattern is already ratified through v4.0. If a native `GovernancePolicyEngine` + `PolicyEngineAdapter` is ever built, that work gets its own Factory Order → TLC arc, where design-stage CFADA is the decision record for the adopted contract, and R-003 closure is the gate for any *production* adapter use.
- **Civilization contribution:** **reference + pattern (adapter boundary).** AGT is the strongest *code-verified* external reference for the deterministic, no-LLM `PolicyEngineAdapter` contract, and the concrete source behind the ratified pattern. Its decisions are advisory until recorded as an EventGraph `AuthorityDecision` and followed by an `ExecutionReceipt`; it is **never** policy owner, release authority, certification authority, memory/knowledge authority, kernel, or factory controller (Decision 13, Decision 15).

The adoption verdict is therefore: **carry AGT forward as the reference implementation of the optional deterministic `PolicyEngineAdapter` pattern, behind the EventGraph authority boundary, gated by Base Slice 0 and the open R-003 production-adapter residual risk.** This is not a runtime activation and assigns no implementation owner.

---

## 5. Strategic Learning Opportunities

1. **A native `GovernancePolicyEngine` that emits `PolicyEngineAdapterDecision` records (highest value).** AGT proves the deterministic, no-LLM evaluator is buildable and that its native action output slots into the schema's `raw_decision`. Borrow the evaluator shape and define the `raw_decision → canonical_decision` mapping (AGT's `allow/deny/audit/block` → the canonical `autonomous/notify/approval_required/forbidden`); supply the default-deny baseline AGT lacks.
2. **Default-deny is the property to *add*, not inherit.** AGT's fail-open empty-policy baseline is the precise anti-pattern to avoid: the native engine must refuse when unconfigured, not permit.
3. **Conformance-test the adapter contract.** Adopt AGT's discipline of allow/deny/approval/failure conformance tests and its MCP-threat taxonomy as the shape of a native adapter conformance suite — the thing Decision 13 already requires ("conformance tests for allow/deny/approval/failure").
4. **Treat "SAMPLE regex as security" as an anti-pattern to name.** A blocklist that matches literal phrases is not enforcement; the Civilization's protected-action policy must be evaluated deterministically but not marketed as coverage it cannot prove.
5. **Air-gap discipline for a networked control-plane.** AGT's policy eval is local and LLM-free (good), but its mesh/relay/discovery assume a networked control-plane; any use must vendor and pin, and prove the network/secret boundaries Base Slice 0 requires.

---

## 6. The inverse: what AGT cannot take from the Civilization by adoption alone

The Civilization's containment cannot be imported by depending on AGT, because AGT's design *is* the thing being contained: its trust scores, its Merkle audit chain, and its signed-identity plane are competing sources of truth. A Civilization that adopted AGT wholesale would inherit a second authority model — exactly what Decision 15 forbids. What transfers is the *contract* (a deterministic, mapped, fail-closed adapter decision recorded as EventGraph evidence); what does not transfer is *authority*, *certification*, or AGT's own governance economy. The direction of learning is one-way: the Civilization takes AGT's evaluator shape; AGT cannot take the Civilization's default-deny, single-source-of-truth discipline without being rebuilt around EventGraph.

---

## 7. Conclusions

The 2026-05-13 investigation ranked AGT the highest-priority external reference and declined to adopt it as authority. The code confirms that judgment from both directions. AGT is a genuinely engineered, multi-language, well-tested runtime governance suite with a real deterministic policy evaluator that meets Decision 13's hardest constraint — a *stronger* reference than the README could show. It is also a fail-open-by-default, Microsoft-owned, Public-Preview 15-package suite whose "10/10 OWASP" is SAMPLE-grade and whose marquee "sandbox" is an in-process linter — a *clearer* case than ever for never ceding it authority. AGT decides whether an action is allowed; the EventGraph `AuthorityDecision` is the decision of record. The disposition is unchanged, now code-anchored, and — uniquely among the recent evaluations — the pattern it inspired is live in accepted v4.0 doctrine with an open production gate.

---

## 8. Recommended Next Steps

1. **Update the wiki page** (this evaluation's companion) from README-only to code-anchored, correcting the resolved H3 defect and the upgraded confidence on AGT's internals.
2. **Record the determination** in §4.4 as the durable decision layer; keep AGT as the named reference behind Decision 13 / the v4.0 `PolicyEngineAdapter Pattern`.
3. **Do not open an integration packet.** Any future native policy engine proceeds via its own Factory Order → TLC arc; production adapter use stays gated behind R-003.
4. **If ever evaluated for real adoption:** pin the fork to a reviewed commit, vendor the dependency and (networked) control-plane surfaces, add the default-deny baseline, and run the adapter-conformance suite — before any Base Slice 0 gate.

---

## 9. References

**Evaluated artifact (upstream context only — never re-published, never a push/PR target):**
- `transpara-ai/agent-governance-toolkit` @ `6dc05da5efcddddf711164d6cd973fcfc19a0625`, VERSION 3.6.0 — read from a local clone. Fork of `microsoft/agent-governance-toolkit` (created 2026-03-02; MIT; "Public Preview"). Representative code anchors: `agent-os/src/agent_os/policies/evaluator.py:35,124,220`; `.../policies/schema.py:34,68`; `.../integrations/base.py:683,1053`; `.../sandbox.py:346`; `.../prompt_injection.py:50`; `.../mcp_security.py:325`; `agent-hypervisor/src/hypervisor/{models.py:46,saga/state_machine.py:30,security/kill_switch.py:75}`; `agent-mesh/src/agentmesh/{identity/spiffe.py:20,trust/cards.py:19,governance/audit.py:23,153,lifecycle/models.py:17}`; `agent-sre/src/agent_sre/slo/objectives.py:44,167`; `agent-discovery/src/agent_discovery/risk.py:21`; `agent-mcp-governance/.../__init__.py:14` (broken import); `README.md:29`; `CHANGELOG.md:9`; `agent-os/pyproject.toml:29`; `agent-os/docs/owasp-agentic-top10-mapping.md`.

**Civilization doctrine (first-party Transpara documents):**
- `dark-factory/v3.9/01-unified-architecture-decisions-v3.9.md:149-164` — **Decision 13** (PolicyEngineAdapter Is Optional And Non-Canonical; names AGT); `:172-174` — **Decision 15**.
- `dark-factory/v3.9/02-kernel-schema-and-state-v3.9.md:345-363` — `PolicyEngineAdapterDecision` node schema (H3 resolved); `:522` — "adapter evidence only."
- `dark-factory/v4.0/03-civilization-governance-and-authority-v4.0.md:113-158` — accepted-v4.0 authority records + **PolicyEngineAdapter Pattern** (`:121`) + external-policy-engine rule (`:158`).
- `dark-factory/v4.0/implementation/epics/epic-21-residual-risk-r003-reidentification/01-...-design-v4.0.md:69-89` — implementation-residual **R-003** (production adapter use open; local-emulation closed).
- `dark-factory/v3.9/implementation/epics/02-technology-decision-crosswalk-v3.9.md` — the AGT decision row (`L82`) + seven-point pre-integration gate (`L175-189`), `status: review`.
- Investigation checkpoints (`dark-factory/research/checkpoints/2026-05-13-…`): Batch D candidate analysis [B4] (README-only), Phase 5 matrix (highest-priority adapter), Phase 6 Gap G2, Phase 7 U2, closeout, v3.9 adversarial review (H3, since resolved).

**Prior compiled page:** `wiki/agent-governance-toolkit.md` (README-grounded; upgraded by this evaluation).

Cross-links: [civilization-landscape-investigation], [dark-factory], [event-graph], [mempalace], [pageindex], [ob1] — sibling external-landscape evaluations and the arc they belong to.
