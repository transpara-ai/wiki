---
entity: Dark Factory
aliases:
  - dark factory
  - the dark factory
  - the factory
  - the governed software factory
  - the software production system
  - DF
tier: arc
status: compiled
last_compiled: 2026-06-17
sources:
  - raw/transpara/dark-factory/Dark Factory - Motive, Goal, Approach.md  # DF-MOTIVE-GOAL-APPROACH v0.1.5, status draft, updated 2026-06-12 — first-read orientation: motive, goal, approach, flows, responsibility map, decision register, citation handles
  - raw/transpara/dark-factory/README.md  # folder index: start-here pointer, current revision (v3.9 accepted 2026-06-05), archived baselines v3.2–v3.8, v3.0, v3.1, v2, phase record, reorganization + reunification workstreams
  - raw/transpara/dark-factory/v3.9/README.md  # DF-V3.9-README v3.9.0, accepted canonical 2026-06-05 — base rule, Base Slice 0, document set, supersedes chain
  - raw/transpara/dark-factory/v4.0/README.md  # DF-V4.0-README v4.0.1, status review, updated 2026-06-12 — doctrine shift, v3.9-remains-operative, authorization boundary, doctrine acceptance 2026-06-12
  - raw/transpara/dark-factory/archive/v2/README.md  # Dark Factory v2 historical design baseline, 2026-05-10
  - raw/transpara/dark-factory/archive/v3/README.md  # Dark Factory v3.0.0 approved baseline, 2026-05-11 — "The Self-Improving Industrial Intelligence Factory"
confidence:
  motive_and_chain: high — the human-intent→certified-artifact chain and the ten "no X without Y" invariants are quoted verbatim from the orientation doc's Top-Level Goal and Executive Summary
  eventgraph_kernel_role: high — stated identically in the orientation doc and corroborated by [[event-graph]]
  searles_philosophical_basis: adopted as motive/research input only, never as implementation authority — the orientation doc says so explicitly and the source corpus guards against treating primitives as truth ([[the-cult-test]])
  hive_repo_category: contested — the same orientation doc files Hive under two categories ("Selected governance layer" in the responsibility map vs "Selected native core" in register B); stated below, not reconciled
  version_lineage: high for the named transitions (v2 2026-05-10 → v3.0 2026-05-11 → v3.9 accepted 2026-06-05 → v4.0 doctrine accepted 2026-06-12), drawn from each baseline's own README; the intermediate v3.1–v3.8 hops are named in the folder index but their individual READMEs were not read this run
  v4.0_status: v4.0 doctrine is accepted; the v4.0 folder/integration program is NOT accepted canonical and authorizes no implementation — every source repeats this
  org_namespace: the orientation responsibility map names repos as transpara-ai/* (eventgraph, work, hive, agent, site, docs); used as written, see "Repository and system responsibility map"
---

# Dark Factory

**The umbrella over the whole governed-production effort.** Dark Factory is the name for a governed, auditable software-production system that turns human intent into verified software artifacts through a chain of evidence rather than through unrecorded conversation or trust in an agent. It is the architecture that sits between the source philosophy that motivated it — the Matt Searles / LovYou / [[event-graph]] corpus, beginning with [[the-20-primitives]] on 2026-02-28 — and the concrete, versioned implementation baselines ([[v3-9]], the candidate [[v4-0]]) that realise it. This article is the synthesis of the project's own first-read orientation doc, *"Dark Factory — Motive, Goal, Approach"* (DF-MOTIVE-GOAL-APPROACH, drafted 2026-06-04, last updated 2026-06-12, still `status: draft`), and the Dark Factory folder index.

The orientation doc is careful about its own authority, and so is this article: it "does not authorize implementation, gate advancement, protected actions, external runtime integration, production deployment, capability activation, or archival of prior materials. It is a human comprehension layer over existing source documents." The operative implementation baseline is [[v3-9]] (accepted canonical 2026-06-05); [[v4-0]] is a candidate doctrine, accepted as a seed on 2026-06-12 but not accepted as a folder.

> The orientation doc deliberately separates three things "that are often confused," and this article keeps the same separation:
>
> | Thing | Meaning |
> |---|---|
> | **Source philosophy** | Ideas that motivated the system — the Searles / LovYou / mind-zero / event-graph corpus. |
> | **Dark Factory architecture** | The governed software-production system defined by the Dark Factory docs. |
> | **Implementation authority** | Human-accepted packets, gates, PRs, and explicit authority decisions that let specific work proceed. |
>
> Philosophy motivates; architecture defines; only accepted authority lets work happen. Conflating them is the failure mode the whole document set exists to prevent.

## Motive: the accountability problem

Dark Factory exists because "AI-assisted software production creates a structural accountability problem." A human can ask an agent to produce code; the agent can plan, edit files, run commands, summarise results, propose a PR, recommend release. Without a stronger architecture, the human "has to trust summaries, screenshots, chat transcripts, and tool behavior that may be incomplete, stale, self-serving, or impossible to reproduce."

The core move, quoted from the Executive Summary, is to refuse trust and require evidence:

```text
Do not ask whether an AI, tool, worker, runtime, or human claims it did the right thing.
Require every material action to leave evidence in a causal, auditable chain.
```

The motive traces back through the source philosophy to a single engineering question. In the durable Matt Searles source post that produced [[the-20-primitives]], the originating problem was failure-tracing: "how can a complex system trace a bad outcome back to the exact source of failure?" The orientation doc converts that philosophical pattern into architecture along a clean mapping:

```text
traceability      -> EventGraph
explicit criteria -> AcceptanceCriteria and gates
agent action      -> bounded runtime invocation
authority         -> AuthorityRequest, AuthorityDecision, ExecutionReceipt
self-improvement  -> EvolutionOrder, eval, human review, activation policy, rollback
```

> ⚠ **Fail-legible note (philosophy is motive, not authority).** The orientation doc is explicit that the Searles corpus — the 20 primitives, the hive0 ~70-agent run that produced 44 primitives, the 200-primitive / 14-layer expansion, the [[thirteen-graphs]] product horizon — is "philosophical and architectural research input, not as proof," and that "accepted implementation authority still comes from merged docs, accepted packets, repository artifacts, review evidence, and human authorization." The source corpus carries its own guardrail (the Cult Test: "framework as tool, not truth; the scientific method is the authority layer"). This article treats the primitives as the **accepted philosophical basis** only, exactly as the doc does — never as proven metaphysics. (See [[primitive-basis]], [[the-cult-test]].)

## Top-level goal: the human-intent → certified-artifact chain

The stated goal is "to build a software factory that can produce, evaluate, repair, certify, and improve software while preserving structural accountability." A successful run makes one chain inspectable end to end:

```text
human intent
  -> FactoryOrder
  -> Requirements and AcceptanceCriteria
  -> Work tasks
  -> bounded execution
  -> artifacts and code changes
  -> tests, scans, reviews, and gates
  -> trace completeness
  -> release candidate
  -> certification or explicit rejection
  -> audit report
```

The chain is enforced by ten negative invariants — the "no X without Y" list the orientation doc gives verbatim as what a successful Dark Factory system must make true:

```text
No artifact without provenance.
No release without verification.
No protected action without authority.
No runtime outside its envelope.
No memory or knowledge as certification authority.
No capability promotion without eval, review, and rollback.
No hidden state that cannot be audited or rebuilt.
No external framework as kernel.
No default production deploy.
No expanded autonomy unless audit and rollback improve with it.
```

These read as the fail-closed posture the whole arc shares: the permissive outcome (ship, grant, merge, deploy) is the explicitly-proven branch, and the default is deny.

## The approach: twelve principles

The orientation doc describes the approach as twelve numbered principles. In compressed form, with the load-bearing constraint each carries:

1. **Preserve human intent.** Source intent must be non-empty, preserved by reference or hash, never silently rewritten; inferred requirements are marked inferred; high-risk unresolved ambiguity blocks certification. This stops the factory "quietly replacing the user's request with the model's preferred interpretation."
2. **Convert intent into a FactoryOrder.** The durable starting object records source intent, requester, scope, constraints, release policy, risk class, and source references. Work does not begin until scope, exclusions, release policy, and risk class are explicit enough to review. (See [[factory-order]].)
3. **Decompose into requirements, acceptance criteria, and tasks.** A planner proposes; [[work|Work]] turns accepted pieces into tasks and manages the DAG. Unrelated tests do not satisfy acceptance criteria.
4. **Keep [[event-graph|EventGraph]] as the kernel.** It is "the sovereign source of truth for durable facts, causality, audit evidence, identity records, authority records, lifecycle records, artifact provenance, certification evidence, and capability-evolution evidence." No other system supersedes it. The kernel must provide append-only recording, deterministic canonical serialization, tamper evidence, idempotent writes, actor attribution, causal edges, queryable paths, replayable projections, and conformance tests without live LLM credentials or production side effects. [DF-V3.9-ADR-001:L35-L40] [DF-V3.9-SPEC-002:L35-L38]
5. **Use [[work|Work]] for flow, not truth.** Work owns task lifecycle, DAG projections, readiness, blocking, repair, and FactoryOrder-to-Task flow — "it does not become the truth kernel."
6. **Execute only through a runtime envelope.** Runtimes "do not govern." They execute only through [[runtime-broker|RuntimeBroker]] envelopes declaring provenance, actor, authority decision, allowed/denied files, commands, network and secrets policy, timeout, resource limits, expected outputs, output contract, trace paths, and post-run validation. The first runtime is a local deterministic worker; external runtimes are deferred until the local worker proves traceability, policy, and audit. [DF-V3.9-SPEC-004:L166-L213] [DF-V3.9-ADR-001:L103-L107]
7. **Govern protected actions fail-closed.** Protected actions "are not model suggestions." Unknown high-risk actions deny or require approval. Authority outcomes are canonical — Autonomous, Notify, ApprovalRequired, Forbidden — and ApprovalRequired blocks until an authorized decision grants approval. Examples: production deploy, default-branch pushes, merges to main, secret access, repo create/delete, cross-repo mutation, policy changes, persistent agent spawning, capability promotion/activation/rollback, external runtime invocation, release certification. [DF-V3.9-ADR-001:L49-L81] [DF-V3.9-SPEC-003:L35-L67] (See [[hive-governance]], [[authority-layer]].)
8. **Verify before certifying.** A ReleaseCandidate cannot be certified "merely because a model, worker, or human says it is good." Certification requires trace completeness, product gates, security gates, runtime BOM evidence, and audit evidence; TraceCompletenessGate blocks when required provenance is missing. [DF-V3.9-EVAL-005:L43-L48] [DF-V3.9-EVAL-005:L153-L173] (See [[gates]].)
9. **Package evidence for human review.** A proof-of-work packet exposes work item, runtime invocation, changed files, tests, CI status, review feedback, security results, walkthroughs, known failures, operator decision, and EventGraph references — "evidence packaging only; it does not replace trace gates, authority decisions, receipts, certification, rejection, or audit reports." [DF-V3.9-EVAL-005:L175-L195] (Surfaced by [[site|Site]].)
10. **Treat memory and knowledge as advisory.** Memory and knowledge influence work "only with explicit evidence references"; recall storage is advisory, "not EventGraph, policy, certification evidence, or authority." Secret-bearing memory is quarantined; stale knowledge is blocked for high-risk planning. [DF-V3.9-SPEC-006:L39-L45] [DF-V3.9-SPEC-006:L80-L117] (See [[memory-knowledge-advisory]].)
11. **Treat capability evolution as production work.** Skills, plugins, prompt sections, tool descriptions, policy bundles are CapabilityArtifacts when they can affect factory behavior; they flow through EvolutionOrder → eval → benchmark → HumanReview → CapabilityVersion → ActivationPolicy → FactoryRuntimeVersion → rollback. "Optimizers may propose improvements, but may not merge, activate changes, bypass benchmarks, weaken security/policy gates, promote their own outputs, or become the factory controller." [DF-V3.9-SPEC-006:L272-L302] [DF-V3.9-SPEC-006:L105-L118] (See [[capability-evolution]].)
12. **Let [[v4-0|v4.0]] bring the development process inside governance.** v4.0 is "a doctrine shift whose seed doctrine was accepted on 2026-06-12": the factory must build the factory under the same accountability it imposes on what it builds. The integration program "remains proposal-only," and v4.0 "does not supersede v3.9 until the folder is accepted canonical under its coverage matrix." [DF-V4.0-README:L24-L40]

A one-line layering captures the relationship the orientation doc draws between systems: "EventGraph [is] the sovereign truth layer. Work schedules and coordinates production. Hive or governance evaluates authority. RuntimeBroker confines execution. Site shows evidence to operators. Memory and knowledge advise but do not govern. Capability evolution is production work, not an uncontrolled self-improvement loop."

## Expected flows

The orientation doc gives several flows; the two that anchor everything else:

**The product-work flow** is the full loop: human submits intent → command layer creates a FactoryOrder → planner proposes requirements/criteria/tasks → human or governance accepts/rejects/clarifies → Work creates tasks → governance evaluates protected actions → RuntimeBroker invokes the worker in a declared envelope → worker returns RuntimeResult / Artifact / CodeChange / Failure / `policy_blocked` → GateRunner emits TestRun and GateResult evidence → TraceCompletenessGate evaluates → security gates + proof-of-work packet assemble review evidence → ReleaseCandidate is certified or rejected → AuditReport records the run.

**[[base-slice-0|Base Slice 0]]** is "the mandatory control-plane proof before higher autonomy" — the same chain run end to end with no LLM planning, no real SaaS generation, no external runtime, no production deploy, no multi-agent orchestration, no memory recall, no knowledge reuse, and no capability evolution. [DF-V3.9-SPEC-004:L143-L164] The point is to prove the control plane before trusting it with anything generative.

The doc also gives an **issue-to-PR flow** (proposal-only — "may not push to default branch, merge, deploy, create repos, access secrets, or mutate cross-repo state without authority approval") and a **capability-evolution flow** (text-only optimization first; no runtime/tool/policy mutation, no auto-merge, no continuous loops). [DF-V3.9-SPEC-004:L300-L306] [DF-V3.9-SPEC-006:L49-L103]

## What Dark Factory is, and is not

The orientation doc closes its conceptual section with two explicit lists, reproduced here because the boundary they draw is the point of the whole document.

**It is:** an evidence-first software-production system; a bounded production loop for AI-assisted development; a causal trace and audit substrate; a governed autonomy progression; a way to keep AI agents inside the accountability graph; and "a software factory that can eventually build and improve itself under evidence, authority, and rollback."

**It is not:** a chat workflow; a model prompt pack; an unbounded multi-agent swarm; a CI/CD pipeline alone; a project-management board alone; a memory system alone; an external agent framework wrapper; "a way for AI to self-approve protected actions"; a release-certification shortcut; "a production deployment authority by default"; "a claim that v4.0 is accepted"; or "a claim that philosophical primitives are proven metaphysics."

That last pair of negatives is load-bearing and recurs throughout the corpus: v4.0 is not accepted as a folder, and the primitives are not proof.

## Repository and system responsibility map

The orientation doc gives a responsibility map binding each system to a Dark Factory role and a hard boundary. Repos are named in the `transpara-ai/*` namespace (note: this differs from the platform-wide CLAUDE.md, which lists product repos under the `transpara` org; the Dark Factory docs and the sibling wiki articles consistently use `transpara-ai/*`, and that is what this row set reports).

| System or repo | Dark Factory role | Boundary |
|---|---|---|
| `transpara-ai/eventgraph` | Kernel: truth, schema, causal paths, authority/evidence/release/capability records | Owns durable truth; must not be bypassed by Work, Site, Hive, Git, CI, memory, or external tools. (See [[event-graph]].) |
| `transpara-ai/work` | Work DAG, task lifecycle, readiness/blocking/repair, FactoryOrder-to-Task flow | Owns operational flow, not certification truth. (See [[work]].) |
| `transpara-ai/hive` / governance | Authority workflow, protected-action policy, later governed multi-agent coordination | Does not replace EventGraph truth; not the Base Slice 0 controller. (See [[hive-governance]].) |
| `transpara-ai/agent` | Identity/lifecycle helpers, causal event-emission helpers | Does not own direct execution authority. (See [[agent]].) |
| RuntimeBroker | RuntimeEnvelope, RuntimeResult, local deterministic worker, future adapters | Executes inside the envelope; does not govern. (See [[runtime-broker]].) |
| `transpara-ai/site` | Operator projections, evidence views, authority queue, proof-of-work display | Console only; not executor, truth source, or authority source. (See [[site]].) |
| `transpara-ai/docs` | Doctrine, specs, packets, checkpoints, source-of-record documents | Records authorization only when accepted/merged/reviewed/human-authorized; docs alone do not execute. |
| Git | Source file content and version history | Useful evidence, not production truth. |
| CI | Raw test/build/scanner output | Raw validation evidence; not certification by itself. |

> ⚠ **Fail-legible note (Hive's category is contested within the source).** The orientation doc files Hive/governance under **"Selected governance layer"** in this responsibility map, but under **"Selected native core"** in its own decision register (section B, "Native Dark Factory Systems"). The two categories are not reconciled in the source; both are stated here rather than silently picking one. The [[hive-governance]] article flags the same internal disagreement.

The map's organising principle is the same in every row: exactly one system owns truth (EventGraph), exactly one confines execution (RuntimeBroker), one evaluates authority (Hive/governance), and everything else — flow, console, docs, Git, CI — is supporting substrate that "must not be bypassed by" or "does not supersede" the kernel.

## Version lineage: v2 → v3 → v3.9 → v4.0

Dark Factory is a long sequence of versioned baselines, each preserved as historical evidence rather than deleted when its successor is accepted. The folder index and each baseline's own README give the spine:

- **v2 (historical design baseline, 2026-05-10).** The reconciled v2 design record set; "the bridge between the phase-record `DF-*` Phase 0–3 authority and implementation record and the later v3 baseline." It established the v2 commitments the whole line carries forward: traceability, bounded execution, evidence-based release, explicit governance. Its ADRs already named the load-bearing roles — EventGraph as kernel/artifact graph (ADR-0001), Work as production DAG (ADR-0002), Hermes/coding agents as bounded execution runtimes (ADR-0003), and Civilization/Hive for governance and agent authority (ADR-0007). Superseded by v3.0.

- **v3.0 (approved baseline, 2026-05-11, codename "The Self-Improving Industrial Intelligence Factory").** v3 "supersedes the v2 design baseline by adding governed self-improvement as a first-class factory capability while preserving the v2 commitments." Its core sentence: "structured intent enters, verified deployable software exits, every transformation is recorded, every release is evidence-based, and every improvement to the factory itself is evaluated, versioned, and reviewed before adoption." v3 also introduced the capability-evolution machinery (CapabilityArtifacts, EvolutionOrders) and the memory/knowledge/state separation that v3.9 carries forward.

- **v3.1 → v3.8 (intermediate baselines).** The folder index records a v3.1 "implementation-ready specification" (draft, 2026-05-11) that "makes v3.0 buildable through concrete contracts, gates, schemas, state machines, policies, and MVP template decisions," followed by consolidated baselines v3.2 through v3.8. *(Thin evidence: these intermediate hops are named in the folder index and the v3.9 `supersedes:` front matter, but their individual READMEs were not read this run; treat the v3.1–v3.8 sequence as named-but-not-inspected here.)*

- **[[v3-9]] (accepted canonical, 2026-06-05) — the operative baseline.** v3.9 is "derived from the accepted v3.8 baseline plus the 2026-05-13 Civilization Landscape Investigation," preserving the v3.8 architecture while adding "implementation contracts, optional adapter boundaries, influence-recording rules, CapabilityArtifact governance, capability-evolution sequencing, operator UX requirements, and native reproducibility requirements." It is the source of the Base Slice 0 target, the base-rule layering, and the gate definitions cited throughout this article. Its `supersedes:` front matter lists the phase record and v2–v3.7, but with a sharp caveat: the Phase 0–3 record is "**inherited authority, not superseded**" — `DF-SOP-0001` and the recorded gate postures remain binding.

- **[[v4-0|v4.0]] (candidate; seed doctrine accepted 2026-06-12).** v4.0 is "a candidate canonical revision opened by a single doctrine shift: the software-development process itself becomes a governed Civilization function." Under the repo's semver rule, declaring the development process to be production work is a doctrine-level change, so it opens a major version. It "resolves a standing contradiction": Operating Principle #7 says self-improvement is production work, yet the development process — "the deepest form of self-improvement" — had run "outside the factory's governance, as an out-of-band human-orchestrated loop (ChatGPT design, Codex implementation, Claude adversarial review)." The 2026-06-01 review of that loop "found it sound in instinct but governed only by one human's discipline, with no control that fails closed." The first v4.0 future gates are **Gate K** (interim development loop hardened) and **Gate L** (v3.9-to-v4.0 reconciliation certified); the source arc scoped both as partially planned and unsatisfied, while the later 2026-06-17 Gate K waiver closes pre-live sequencing only and keeps live/go-live blocked. [DF-V4.0-ARC:L115-L149]

> ⚠ **Fail-legible note (v4.0 is accepted as a seed, not as a folder).** Every source repeats the distinction. The seed doctrine (DF-V4.0-ADR-001) was **accepted** by the human External Committee on 2026-06-12, satisfying folder acceptance criterion 1. But "criteria 2 (reconciliation coverage matrix) remains open, so this folder is still a candidate and v3.9 remains the operative baseline." v4.0 "is documentation doctrine. It authorizes no implementation… does not advance any gate, does not grant any autonomy level, and does not close any risk." v3.9 Gates F–J remain waiting; residual risks R-001/R-002/R-003 remain unresolved. Do not read "v4.0 doctrine accepted" as "v4.0 in force."

The lineage discipline is itself a Dark Factory invariant: each baseline "stays preserved and binding until human review explicitly accepts the successor and an acceptance checkpoint is recorded." Nothing is deleted on assertion; supersession is an evidenced, human-signed event.

## Autonomy posture

The orientation doc is explicit that it "is not the current-state register" — the v3.9 state-of-the-system proof and as-built tracker remain authoritative for gate status. As of the orientation draft, before the later Event-1 grant and Gate K pre-live waiver, the posture rule was: "v3.9 records bounded completions through Gate J and Epic 10, Epic 11 is selected only for authorization review, and v4.0 Gate K / Gate L remain proposal-only future gates." [DF-V3.9-STATE:L31-L35] [DF-V3.9-TRACKER:L176-L196] [DF-V4.0-ARC:L115-L149] The autonomy progression is incremental and conditional: per the tenth invariant, autonomy expands only when audit and rollback improve with it.

## Related workstreams (planning only)

The folder index records two planning workstreams that do not change current authority:

- **Reorganization** — a proposed migration of the Dark Factory corpus into a dedicated source-of-truth repo with a generated LLM Wiki projection (this wiki is the downstream of that idea). "They do not relocate files or change the current v3.9 implementation authority."
- **Reunification** — artifacts that "re-center Dark Factory on the original Mission — one civilization, one business — with the Hive civic roles and growth loop performing and governing the factory and the v3.9 accountability machinery as the membrane." Planning and design only; they "do not change the current v3.9 (operative) or v4.0 (candidate) status." (See [[the-civilization]], [[the-reunification]].)

## What grew from it, and what it grew from

- **From the seed:** Dark Factory is the architecture that converts [[the-20-primitives]]' failure-tracing question and the broader [[primitive-basis|Searles primitive corpus]] into a governed production system — traceability becoming [[event-graph|EventGraph]], explicit criteria becoming [[gates]], agent action becoming [[runtime-broker|bounded runtime]], authority becoming the [[authority-layer]].
- **Into baselines:** the doctrine is realised in versioned form as [[v3-9]] (operative) and the candidate [[v4-0]], with v2 and v3.0 preserved as historical baselines.
- **Into systems:** the responsibility map binds [[event-graph]], [[work]], [[hive-governance]], [[agent]], [[runtime-broker]], and [[site]] into one accountability graph, governed against [[the-drift|architectural drift]] by the decision-category system the orientation doc maintains.

## Sources & provenance

Compiled from the Dark Factory source corpus in `raw/transpara/dark-factory/`:

- **`Dark Factory - Motive, Goal, Approach.md`** (DF-MOTIVE-GOAL-APPROACH v0.1.5, `status: draft`, created 2026-06-04, updated 2026-06-12) — the primary source for this article: the executive summary and core move, the motive, the human-intent→certified-artifact chain and the ten negative invariants, the twelve approach principles, the expected flows (product-work, Base Slice 0, issue-to-PR, capability-evolution, v4.0 development-process), the "what it is / is not" lists, the repository-and-system responsibility map, the autonomy posture, and the citation handles (Searles durable URLs and `DF-V3.9-*` / `DF-V4.0-*` document line references reproduced in-body).
- **`README.md`** (folder index) — start-here pointer, current revision (v3.9 accepted canonical 2026-06-05), the archived-baseline list (v3.2–v3.8, v3.0, v3.1, v2), the phase record, and the reorganization + reunification planning workstreams.
- **`v3.9/README.md`** (DF-V3.9-README v3.9.0, `status: accepted`, accepted canonical 2026-06-05) — base rule, Base Slice 0, document set, derivation from v3.8 + the 2026-05-13 Civilization Landscape Investigation, and the "phase record is inherited authority, not superseded" caveat.
- **`v4.0/README.md`** (DF-V4.0-README v4.0.1, `status: review`, updated 2026-06-12) — the doctrine shift, the standing-contradiction resolution, "v3.9 remains operative," the authorization boundary, Gates K/L, and the 2026-06-12 doctrine-acceptance update (criterion 1 satisfied, criterion 2 / coverage matrix open).
- **`archive/v2/README.md`** (Dark Factory v2 historical design baseline, 2026-05-10) — the v2 commitments and ADRs (EventGraph kernel, Work DAG, bounded runtimes, Civilization/Hive governance).
- **`archive/v3/README.md`** (Dark Factory v3.0.0 approved baseline, 2026-05-11, codename "The Self-Improving Industrial Intelligence Factory") — the v3 core sentence and the addition of governed self-improvement.

**Durable external URLs** (carried from the orientation doc's Citation Handles table, used as motive/research input only): the Matt Searles Substack corpus — [Searles-P1] *20 Primitives and a Late Night* (https://mattsearles2.substack.com/p/20-primitives-and-a-late-night); [Searles-Cult-Test] *The Cult Test* (https://mattsearles2.substack.com/p/the-cult-test); and the broader series referenced for the 44/200-primitive and thirteen-graphs framing.

**Conflicts and limits stated, not resolved:** (1) **Hive's category** — "Selected governance layer" (responsibility map) vs "Selected native core" (register B) within the same orientation doc; stated, not reconciled. (2) **Repo namespace** — the Dark Factory docs use `transpara-ai/*`; the platform-wide CLAUDE.md uses `transpara` for product repos; used as the source writes it, with the discrepancy flagged. (3) **v4.0 status** — doctrine accepted (2026-06-12) but folder not canonical; carried with the explicit "authorizes nothing" qualifier. (4) **v3.1–v3.8 intermediate baselines** — named in the folder index and v3.9 `supersedes:` front matter but their individual READMEs were not read this run; labelled thin. `[[wikilinks]]` are forward references; several targets (hive0, [[thirteen-graphs]], [[primitive-basis]]) may not yet be compiled.

## Run-3 update (2026-06-14)

This section records material facts that became known between the Run-2 compile (2026-06-13) and 2026-06-14. It does not revise existing content — it appends forward.

### G-1.2 complete: Round 6 (v16) closed "finished-unsignalled" on 2026-06-12

Grant-1.2 (G-1.2) is complete. Round 6, running as v16, closed on 2026-06-12 with a new close class: **`finished-unsignalled`**. The run launched at 11:28, produced the first review of the entire arc at 11:44, self-managed a v15-deadlock replay at 12:00, and reached terminal quiescence at 12:13. The chain sealed at 1,128 events. The society ran unattended through an operator-session crash — a nohup sentinel pair held the round throughout. Dark Factory's society is **the first to finish** a Slice 1 arc run of this kind.

The arc ladder, in order: v13 silent 5 min → v14 visible 27 min → v15 productive 31 min + verified artifact → **v16 finished 45 min, fix set proven live**. Budget across the entire arc: $0.00 metered (claude-cli subscription).

The catalog deliverable (`codex/fo-roles-catalog-v16`, HEAD `002bcf8`, 9-role v2.0.0 with subtask reading) is pushed to `transpara-ai`. Six oscillation commits are preserved in history; the FO's 24-role reading survives at `b638a44`. The deliverable remains **unreviewed in the FO's sense** — all six reviews in v16 were premised on the wrong repo (v16-F1, below).

**Grant-2 is exhausted** (rounds 4–6 consumed). The hard stop was reached and then **resolved on 2026-06-15**: the External Committee granted **Event-1** (v4.0 Gate-K interim loop hardening; decision *Notify*, `transpara-ai/docs#132`), not a new slice-1 grant. Gate K was later closed for pre-live sequencing by the human waiver in `transpara-ai/docs#138`; production go-live, live data, protected runtime execution, value allocation, and autonomy increases remain blocked until revalidated.

### v16 open findings

Three findings emerged from Round 6 and remain open:

- **F1 — WorkDir/Reason cwd defect.** In `eventgraph claude_cli.go`: the Operate phase fails closed on `WorkDir`, but the Reason phase sets no `cmd.Dir`, so the reviewer verified files in the daemon's working directory for the entire round rather than the task workspace. Candidate fix: thread `WorkDir` through `pkg/loop` in `hive` and the eventgraph provider.
- **F2 — Dual-spec oscillation.** The planner decomposition silently narrowed the FactoryOrder scope, causing a dual-spec oscillation: 6 completions across 24→9 role ping-pong. Candidate fix: a spec-diff gate at subtask creation that detects when a child task's spec diverges from the parent FactoryOrder.
- **F3 — Quiescence has no exit.** Terminal quiescence has no exit signal, no run-completion event, and no escalation channel. Escalations during v16 demanded "Human/CTO judgment" with no channel to receive one. Candidate fix: a quiescence detector emitting `hive.run.completed` plus a human-decision channel.

The v16 fix-set scope (F1 WorkDir threading, F2 spec-diff gate, F3 quiescence detector) has been identified. The Gate-E hard stop resolved on 2026-06-15 toward **Event-1 / Gate-K** (`transpara-ai/docs#132`); absent a separate new slice-1 grant, this v16 fix-set remains unauthorized.

A society escalation during v16 also produced an evidence-backed ruling: the catalog workspace IS `transpara-ai/docs`; the FO's 24-role scope governs (`b638a44`); the subtask was mis-scoped.

### v4.0 doctrine accepted on 2026-06-12

The v4.0 seed ADR — `01-development-process-as-governed-civilization-function-v4.0.md` (DF-V4.0-ADR-001) — was **accepted** by Michael Saucier (human External Committee) on 2026-06-12. The accepting instruction, given in a Claude Code operator session: "Proceed to accept the v4 doctrine and manifesto. Apply to all known behavior, then make any modifications required."

All five ADR acceptance criteria are confirmed satisfied: External Committee acceptance, reconciliation plan accepted, Tier-0 structural guards adopted or deferred with reasons, checkpoint recorded, and affirmation that acceptance alone advances no gate and closes no risk.

Tier-0 structural guards disposition at acceptance: guard 2b (`npm run verify` as PR check) and 2c (CODEOWNERS on governance-sensitive paths) were **adopted** via the acceptance PR to `transpara-ai/docs`. Guards 3 (injection-quarantine on feedback channel) and 4 (never trust self-reported validation) were **adopted** as standing interim-loop rules by the checkpoint. Guards 1 (meta-loop confidentiality/data-handling policy) and 2a (branch protection on `main`) were **deferred** with reasons recorded.

**What this acceptance does not do** (unchanged from the checkpoint): v3.9 remains the operative baseline; the v4.0 folder is still a candidate (criterion 2 — coverage matrix — remains open, reconciliation unauthorized); Gates F–J remain waiting; Gate L remains unsatisfied; residual risks R-001/R-002/R-003 remain unresolved; no autonomy level above the current bootstrap is granted. Gate K's later pre-live waiver in `transpara-ai/docs#138` changes sequencing for pre-live work only; it does not accept v4.0 as canonical or authorize production go-live. The v4.0 folder "is documentation doctrine" — it authorizes no implementation.

A manifesto finding was recorded in the acceptance checkpoint: no v4 manifesto artifact exists. Acceptance of a non-existent artifact was refused under the fail-closed rule. Open item for the External Committee: identify, commission, or drop.

### Observatory shipped: /ops/observatory live on site (2026-06-13/14)

The transparency surface defined in the Civilization Transparency Contract (DF-TRANSPARENCY-CONTRACT v0.1.0, `status: draft`, created 2026-06-13) has been partially implemented. The `/ops/observatory` page is **live on `transpara-ai/site`** as of 2026-06-13/14, delivered via PRs #76 and #77.

The transparency contract defines seven terms (T1–T7) that a human overseer must be able to see for the civilization to count as transparently self-governing. As of the contract's own satisfaction map (2026-06-13), the observatory covers the data and API layers for T1–T5 but all five remain **not yet visualized** — the component (`site-observatory-phase3-plan.md`) is the gap. T6 (posture never overstated) is static plan only; T7 (read-only by construction) is enforced by the Phase-3 surface design. The contract is advisory/draft; EventGraph remains truth.
