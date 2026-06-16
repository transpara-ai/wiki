# Civilization Ontology & Construction-Arc Projection — Design Spec

**Status:** draft v0.1 · **Date:** 2026-06-16 · **Owner:** Michael Saucier · **Authority:** planning (proposal, pending review) · **Repo/branch:** transpara-ai/civilization-wiki @ claude/elegant-swanson-965269

## 0. Purpose & scope

A **single unifying ontology** — a typed property graph — that governs **both** the *construction* of the Transpara-AI civilization (how it was built, the arc) and its *runtime operation* (how it runs, day to day). Same node and edge types describe both worlds at different scale; only the instances differ. This is the "strange loop" the corpus names: the thing that builds itself is operated by the same grammar.

**This spec does two things:**
1. **Locks the ontology** (spans both worlds — "model now").
2. **Implements Projection 1 only** — the *construction arc* read-view (the redesigned arc chart). Projection 2 (runtime ops), the "Update Now" mechanism (sub-project A), and chart-style polish (sub-project B2) are **explicitly deferred** (see §6).

**Hard requirements from the owner (2026-06-16):**
- **(b) Complete provenance.** Every ontology decision must be traceable to an accepted precedent — corpus citation *and* external formal precedent. See §2 (Provenance Ledger).
- **(c) Forget nothing.** Everything discovered in the gap-survey is preserved, even what we defer or treat as a facet, with a "re-introduce when" trigger. See §5 (Do-Not-Forget Register).
- **(d) No corner.** The hybrid (declare Event the substrate, render flat projections now) must not foreclose the runtime projection. See §3 (Forward-Compatibility Contract & Guarantee).

**Process provenance:** ontology derived through brainstorming (2026-06-16) + a 5-surveyor parallel corpus survey (DF governance, Searles philosophy, resilience, economy/capability, Open Brain) cross-checked against four formal frames: **REA** (Resource–Event–Agent accounting ontology), **Ostrom's 8 commons-governance principles**, **normative multi-agent systems** (norms/sanctions/trust), and **speech-act / commitment theory**.

---

## 1. The Ontology (locked for this pass)

### 1.1 Substrate decision — hybrid (Event is the substrate)

**Decision:** `Event` is declared the **substrate**: an append-only, hash-chained log with **no Update/Delete** (fail-closed by data structure). All other node types are **projections** — the current state of any node is a fold over its ordered event history. We *model* this now; we *do not build* the event store this pass. Projection 1 hand-authors the projected node instances; Projection 2 will derive them from the live EventGraph. (Provenance: §2; corner-safety: §3.)

### 1.2 Node types — 13 (original 9, fixed, + 4 new core)

| # | Node | Definition | Construction instance | Runtime instance | New? |
|---|------|-----------|----------------------|------------------|------|
| 1 | **Work** (hub) | a unit of effort with a status lifecycle | a build task (N5 "close out Gate-K") | a FactoryOrder/Task | — |
| 2 | **Gate** | a checkpoint/criteria that must be satisfied to proceed; carries a `family` facet | Gate-K | an authority/release gate | fixed (§1.4) |
| 3 | **Artifact** | a durable produced thing | a PR / wiki article | an execution receipt | — |
| 4 | **Surface** | where work/artifacts live or are observed (carries a `kind`) | a repo (git) | repo / Site / Observatory | facet (§5) |
| 5 | **Actor/Role** | who performs or authorizes (Agents + Humans) | Codex / Claude / Michael | a civic role / operator | facet (§5) |
| 6 | **Phase/Epoch** | a contiguous era/sprint | the 15 phases | a runtime epoch | — |
| 7 | **Event** | an immutable fact at a timestamp; open `Type`; the **substrate** | "PR #10 merged" | any runtime event | fixed (§1.4) |
| 8 | **Decision** | alters FUTURE behavior; by human/agent; mode ∈ {Autonomous, Notify, ApprovalRequired, Forbidden} | "1C1B" ruling | an AuthorityDecision | fixed (§1.4) |
| 9 | **Conflict** | a trigger demanding resolution; trichotomy: detected-violation / surprise / permanent-tension | "Gate-E overloaded" | resource contention | fixed (§1.4) |
| 10 | **Goal/Order (Telos)** | the purpose-bearing seed Work serves; decomposes into Work | a FactoryOrder / the north-star | a customer order | **NEW** |
| 11 | **Policy/Invariant** | a *standing* rule (vs per-case Decision); Invariant = the always-hold subtype, fail-closed | v3.9 Decision-15; the 14 invariants | a runtime policy | **NEW** |
| 12 | **Resource/Budget** | a scarce consumable Work draws on | build-run token/time budget | live token/$/compute budget | **NEW** |
| 13 | **Capability** | a standing competence/permission an Actor holds, that can evolve | a compiled skill/role | a runtime capability version | **NEW** |

### 1.3 Edge types

Structural: `depends-on` (Work→Work), `part-of` (Work→Phase; Work→Goal), `gated-by` (Work→Gate), `produces` (Work→Artifact), `lands-in` (Work/Artifact→Surface), `performed-by` (Work→Actor), `satisfies` (Artifact→Gate), `serves` / `decomposes-into` (Work↔Goal/Order), `governed-by` (Work/Decision→Policy), `consumes` (Work→Resource), `holds` (Actor→Capability).
Governance/dynamic: `advances` (Event→Work status), `triggers` (Event→Decision), `forces` (Conflict→Decision), `alters-future` (Decision→Work/Gate/Policy), `made-by` (Decision→Actor).
Edges may carry a **`weight`** attribute (deferred semantics — see §5, "edge-weights-as-personality").

### 1.4 Fixes to the original 9

- **Decision modes** — replace `{Notify, Consent, two-human}` with the real set **`{Autonomous, Notify, ApprovalRequired, Forbidden}`** (plus Searles' "Recommended / silence-is-consent" timeout as a named variant of Notify). **`Forbidden`** is the standing fail-closed deny; its absence in the draft was a fail-open bug.
- **Event** — immutable, append-only, hash-chained, no Update/Delete; typed by an **open `Type` string** (100+ runtime types), not the draft's closed 3-kind enum. The draft's {scheduled, on-demand, unexpected} becomes a non-exhaustive `cadence` hint, not the identity.
- **Gate** — add a **`family`** facet; three vocabularies must never conflate: `A–J` (v3.9 build-milestone fixtures), `G-0…G-8.4` (deployment-program register with deps), `K/L` (v4.0 future). "Gate-E" is overloaded (resolved Event-1 grant vs. the live v3.9 governed-decision-boundary) — keep distinct.
- **Conflict** — **trichotomy**, not "always-unexpected; must resolve": `detected-violation` (expected; surfaced by monitoring/guardian), `surprise-conflict` (unexpected; route → resolve → deadlock → escalate to Humans, fail-closed), `permanent-tension` (irreducible; **held, never resolved** — Justice vs Forgiveness, Tradition vs Creativity; treating these as resolvable is itself a "cult" failure mode).

### 1.5 Status lifecycle & adopted facets

- **Status lifecycle (one vocabulary, every node):** `future → planned → active → done`, with `blocked` as an overlay on `active`. **Allowlist rule** (replacing the fail-open denylist): anything left of "now" MUST be `done` (or `active` at the frontier) — anything else fails the build test, closed.
- **Adopted facets now:** `provenance ∈ {reconstructed, derived}` (§3 residual-risk mitigation); `blocked_reason ∈ {gate, resource, authority, recovery, dependency}`; `risk_class`; `surface.kind ∈ {execution, decision, transparency}`; `role.layer ∈ {civic-runtime, governance-policy, human}`.

---

## 2. Provenance Ledger (requirement b) — COMPLETE

Every element traces to corpus precedent + an external formal precedent. Corpus files are under `wiki/` unless noted; DF = `docs/dark-factory/`; OB = Open Brain captured thought.

| Element | Corpus citation(s) | External precedent |
|---|---|---|
| Event-as-substrate; immutable, hash-chained, no Update/Delete | event-graph.md; accountable-ai-architecture.md ("interface has no Update()/Delete()"); node-phenomenology.md; the-44-primitives (Foundation: Event·EventStore·Clock·Hash·Self); crash-recovery-as-ethics.md | Event sourcing / CQRS; REA (Event is core); immutable append-only ledgers |
| "Types are views over one event graph" (13 graphs) | the-culture-graph.md / thirteen-graphs; Searles-P2 (20→44→200 primitives, 14 layers); strange-loop.md | Database materialized views; CQRS read-models |
| **Goal/Order (Telos)** | factory-order.md (FactoryOrder, decomposition chain, endGoal); capability-evolution.md (EvolutionOrder, EvalDataset fixed-before); deployment-arc.md; the-civilization.md (north-star; first FactoryOrder "document its own society"); Epic→Phase→Stage→Slice | **REA Commitment**; speech-act *directives/commissives*; teleology |
| **Policy/Invariant** | hive-governance.md (Soul + Eight Agent Rights + Fourteen Invariants); civic-roles.md; authority-layer.md (Policy struct {Action,ApproverID,Level}); dark-factory.md (the invariants); v3.9 Decision-15; the-cult-test.md (meta-norm) | **Ostrom #2** (congruent rules); **normative MAS** (norms/institutions); constitutional law |
| **Resource/Budget** | civic-roles.md (Allocator; /budget; 12h MaxDuration, no self-renew); observability.md (T3 spend-vs-cap); roles-catalog.md; OB (BudgetRegistry, agent.budget.exhausted/adjusted, $25/day, 720m ceiling) | **REA Resource** (the "R" we were missing); Ostrom (provisioning/appropriation) |
| **Capability** | capability-evolution.md (full pipeline → RollbackRecord; CapabilityArtifact); civic-roles.md (CanOperate); roles-catalog.md; OB ("authority != gate satisfaction"; CapabilityOptimizer/Reviewer/Release) | Capability-based security; RBAC capabilities; skill/competence models |
| Decision modes (+Forbidden, +Autonomous) | DF Motive-Goal-Approach ({Autonomous,Notify,ApprovalRequired,Forbidden}); accountable-ai-architecture.md / authority-layer.md (Searles 3-level: Required / Recommended-15min-silence / Notification) | Speech-act theory; default-deny security; **fail-closed (owner CLAUDE.md)** |
| Gate `family` (A–J / G-0…8.4 / K/L) | gates.md (gate classes: readiness/trace/security/authority/release); OB ("gate vocabularies must never be conflated"; Gate-E overloaded) | Quality gates; staged release pipelines |
| Conflict trichotomy (incl. permanent-tension) | the-cult-test.md (permanent tensions; unresolved≠unresolvable); civic-roles.md (guardian monitors as expected; HALT); Searles-P2 | **Ostrom #6** (conflict-resolution mechanisms); pluralism / value-incommensurability |
| Status allowlist (past must be done) | tests/arc-dom-smoke.js (current denylist — to be inverted); the-drift.md (silent invariant violation) | **Fail-safe-by-default (owner CLAUDE.md): allowlist, fail closed** |
| Actor/Role dual-layer (24 roles; CanOperate; ModelPolicy) | civic-roles.md (9 runtime); roles-catalog.md (15 governance); hive-governance.md (Michael = ceiling); Searles-P1/P3 ("AI is a node in the graph, not above it") | RBAC; org role taxonomy; principal/agent |
| Surface kinds (execution/decision/transparency) | hive-governance.md (Observatory); observability.md (T1–T7 read-only); civic-roles.md (codex/* branches) | Separation of concerns; read/write segregation |

> **Provenance TODO (code-is-truth):** the "14 invariants" is unstable in prose (civic-roles.md says 14; a 2026-06-05 capture said 10). The enumerated list lives in **code**: `hive/pkg/hive/agentdef.go` and `docs/roles-catalog.md`. Recover and pin it before Policy/Invariant instances are authored: `grep -rniE "invariant" /Transpara/transpara-ai/data/repos/{hive,docs}`.

---

## 3. Forward-Compatibility Contract & Guarantee (requirement d)

**Claim:** the hybrid does not corner us, *guaranteed by* a stable contract + a swappable source.

**The projection contract (the stable interface).** Both projections emit a list of `items[]`, each item:
```
{ id, type, label, status, blocked_reason?, provenance,        // reconstructed | derived
  seq, repo[], sprint, gate, goal, policy[], resource?, capability?,
  deps[], events[], href, note? }
```
The renderer and all facet groupings depend ONLY on this contract — never on where items came from.

**Four anti-corner invariants (adopted now):**
1. **One schema, two renderers.** Identical 13-type schema both worlds; only the source differs. Runtime = write an adapter emitting the contract shape.
2. **Event-fold compatibility.** Every item's state must be expressible as a fold over an ordered event history. No field may exist that a future event stream couldn't produce. (Hand-authored now, but shaped like a projection.)
3. **Pure facet derivations.** Grouping, the derived-"now" frontier, and blocked-reason are pure functions of `items[]`. Swapping source → views recompute unchanged.
4. **Ontology-validated data.** Construction data passes an allowlist validation against the schema; anything inexpressible is rejected (prevents un-portable hand-data accretion).

**The one residual risk + mitigation.** Hand-authoring tempts encoding *narrative history* no event stream would emit (the reconstructed Feb genesis). Mitigated by the first-class `provenance ∈ {reconstructed, derived}` facet (already a corpus concept): the boundary is explicit and auditable; the runtime adapter leaves `reconstructed` items alone. No silent special-cases.

**What we build now to keep the door open:** (1) the `items[]` contract above; (2) the validation test (allowlist); (3) `provenance` on every item; (4) the renderer reads only the contract. We do **not** build the event store, the runtime adapter, or live derivation this pass.

---

## 4. Projection 1 — the Construction-Arc chart (what we implement now)

**Replaces** the current 5 overlapping lists (15 phases + 28 markers + 5 gates + 4 risks + 4 decisions, hand-positioned by `x`) in `compile/assets/civilizationArcData.js`.

- **Data model:** one `items[]` per the §3 contract. Narrative beats (today's markers) become `provenance:reconstructed` items, mostly `status:done`; the executionPlan (N1–N7, C1–C10) become the live `active/blocked/planned` items; gates/risks/decisions fold into items or `note` annotations (a blocker = `status:blocked` + `blocked_reason`, not a free-floating chip).
- **Axis:** development sequence (unchanged). **"Now" is derived** — the frontier after the last done/active item; the hand-set `currentFocus.x` is deleted. (Fixes: planned-phase-behind-now; blocker-in-past.)
- **Swimlane toggle (default Status):** four groupings as facets — **Status** (default), **Repo** (`lands-in`), **Sprint** (`part-of` Phase), **Gate** (`gated-by`).
- **Dependency declutter:** dependencies hidden by default; shown only for the selected item (kills the 25-edge epic/stage spaghetti).
- **Validation test:** invert the fail-open denylist to an **allowlist** — past items must be `done`/`active`; `Forbidden`/`planned`/`future` left of "now" fails closed. Covers the whole status domain.
- **Layout:** correctness only (content stays within lane boundaries). Heavy style/overflow + resizable columns = **sub-project B2, deferred.**

---

## 5. Do-Not-Forget Register (requirement c) — COMPLETE

Nothing discovered is cut. Each carries a re-introduce trigger.

**Tier 2 — runtime primitives (model now in ontology; realize in Projection 2):**
| Primitive | Citation | Re-introduce when |
|---|---|---|
| Signal / Monitoring (SysMon /health; T1–T7) | observability.md; civic-roles.md · Ostrom #4 | Projection 2 / live detection |
| Sanction / Enforcement (HALT, suspend, quarantine, contain, fail-the-task) | civic-roles.md; OB (constitutional HALT; containment tripwire; injection-quarantine) · Ostrom #5 | runtime governance |
| Recovery (clean orphans, rehydrate authority, retry+backoff, escalate-don't-fail-open) | crash-recovery-as-ethics.md | runtime resilience |
| Rollback / Compensation ("no autonomy expansion without rollback"; Revise=supersede) | capability-evolution.md (RollbackRecord); higher-order-operations.md; dark-factory.md | capability promotion / runtime |
| Reputation / Trust (routes conflict to "correct Agents"; CanOperate=false until trust) | the-identity-graph.md; the-market-graph.md; civic-roles.md · normative MAS | runtime routing / dynamic spawn |
| Boundary / Membership / Identity (inside vs Customer/Committee/upstream; belonging gradient) | the-civilization.md; roles-catalog.md; the-community-graph.md; the-cult-test.md; religion-as-paths-from-being.md · Ostrom #1 | multi-party / external runtime |
| Customer / Economy (Offer/Acceptance/Obligation/Payment) | the-civilization.md ("one business"); the-market-graph.md · REA | Market-graph horizon |
| Memory/Knowledge as advisory-only (informs, never governs; influence_summary) | memory-knowledge-advisory.md; base-slice-0.md (prohibits it); OB (Memory/KnowledgeCurator) | advisory runtime |
| AuthorityRequest → Decision → ExecutionReceipt full triple (+ Attestation ≠ Artifact; PolicyEngineAdapter) | authority-request.md (4-event cycle); execution-receipt.md; runtime-broker.md; gates.md (BOM evidence) | runtime authority pipeline |

**Facet / semantic findings (parked or partially adopted):**
- `risk_class` on Work/Request (factory-order.md; authority-request.md; runtime-broker.md) — **adopted as facet.**
- `health_state` / `runtime_state` (slice-1-completion.md stalled-visible/productive; agent.md FSM Suspended/Retired; bounded-runtime.md five stop reasons) — parked (Projection 2).
- **Drift / Entropy** — slow degradation distinct from Conflict (the-drift.md); needs aggregate Signal, no auto-escalation — parked.
- **Causal ancestry / diagnostic traversal** — `Causes`/`Ancestors()`/`Descendants()` (event-graph.md; observability.md T4) — semantic property of Event edges; parked until event store.
- **Edge-weights-as-personality** — edges carry learnable `weight`; "personality = topology of edge weights" (edge-weights-as-personality.md; the-four-strategies.md; the-culture-graph.md) — `weight` attribute reserved, semantics parked.
- **Consent / silence-is-consent timeout** — Decision sub-mode (accountable-ai-architecture.md Layer 3) — noted under Decision modes.
- **Epistemic status / Confidence** — revisable certainty on Artifact/Decision (Searles-P2 Confidence; the-existence-graph.md) — parked.
- **ModelPolicy** — model pluggable per role; online→offline gradient (civic-roles.md; offline-llm-optimization.md; open-weight-llm-routing.md) — Actor facet; arc parked.
- **Meaning / Value / Norm / Belonging layer** — the ethics/culture/community graphs (Searles) — partly covered by Goal + Policy; the affective remainder (Value, Belonging) parked with Reputation/Boundary.

**Meta-shape notes (philosophical substrate, preserve):** 20→44→200 primitives across 14 layers (0 Foundation … 13 Existence); the **Strange Loop** (L13→L0); the **Three Irreducibles** (Moral Status L7, Consciousness L12, Being L13 — the is-ought gap, deliberately left empty); the **Cult-Test meta-norm** ("the scientific method is the authority layer; the framework must not become sacred" — and beware its naming collision with the runtime authority-layer).

---

## 6. Scope boundary — NOT doing now

- **Sub-project A ("Update Now" / live data):** deferred until the site is dockerized on a chosen host (nucbuntu first).
- **Sub-project B2 (overflow + resizable auto-sizing columns):** deferred ("just style").
- **Projection 2 (runtime ops):** deferred — modeled in the ontology, realized when live data exists; §3 guarantees it isn't foreclosed.
- **Event store / live derivation:** not built this pass (hybrid).

---

## 7. Open questions for review
1. Goal vs Order — one node with a `scale` facet, or two? (Order = the seed; Goal = the end-state it serves.)
2. Should `Policy` and `Invariant` be one node with a `binding ∈ {policy, invariant}` facet, or two?
3. Confirm the construction-arc keeps the *narrative beats* (28 reconstructed items) rather than collapsing purely to the executionPlan work — i.e., the chart stays a story, not just a kanban.
