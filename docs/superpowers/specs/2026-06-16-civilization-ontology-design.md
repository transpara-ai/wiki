# Civilization Ontology & Construction-Arc Projection — Design Spec

**Status:** draft v0.1 · **Date:** 2026-06-16 · **Owner:** Michael Saucier · **Authority:** planning (proposal, pending review) · **Repo/branch:** transpara-ai/wiki @ claude/elegant-swanson-965269

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

### 1.2 Node types — 15 (original 9, fixed, + 6 new core)

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
| 10 | **Goal / Telos** | the end-state Orders serve; abstract, outlives any Order | the north-star ("one civilization, one business") | a customer outcome | **NEW** |
| 11 | **Order** | the concrete, trackable seed; serves a Goal, decomposes into Work | a FactoryOrder | a customer order | **NEW** |
| 12 | **Policy** | a *tunable* standing rule (actions→approver/mode); amendable by a Decision | v3.9 Decision-15; role permissions | a runtime authority policy | **NEW** |
| 13 | **Invariant** | an *inviolable* always-hold property; violation HALTs (fail-closed); constitutional change only | the 14 invariants | a runtime safety invariant | **NEW** |
| 14 | **Resource/Budget** | a scarce consumable Work draws on | build-run token/time budget | live token/$/compute budget | **NEW** |
| 15 | **Capability** | a standing competence/permission an Actor holds, that can evolve | a compiled skill/role | a runtime capability version | **NEW** |

### 1.3 Edge types

Structural: `depends-on` (Work→Work), `part-of` (Work→Phase), `serves` (Order→Goal), `decomposes-into` (Order→Work), `gated-by` (Work→Gate), `produces` (Work→Artifact), `lands-in` (Work/Artifact→Surface), `performed-by` (Work→Actor), `satisfies` (Artifact→Gate), `governed-by` (Work/Decision→Policy), `enforces` (Gate→Invariant; violation → HALT), `consumes` (Work→Resource), `holds` (Actor→Capability).
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

> **Provenance TODO (code-is-truth):** the "14 invariants" is unstable in prose (civic-roles.md says 14; a 2026-06-05 capture said 10). The enumerated list lives in **code**: `hive/pkg/hive/agentdef.go` and `docs/roles-catalog.md`. Recover and pin it before Policy/Invariant instances are authored: `grep -rniE "invariant" /Transpara/transpara-ai/repos/{hive,docs}`.

### 2.1 External frameworks — canonical sources & per-change mapping

The abbreviations in the §2 ledger resolve here. Each is an accepted precedent with a canonical published source; each maps to the specific ontology changes it grounds. Full bibliographic entries with **verified online links** are in **§8 References** ([E1]–[E4]); corpus sources (Searles posts with dates/URLs, first-party doc IDs) are in §8.2–8.4.

**REA — Resource–Event–Agent.** McCarthy, W.E. (1982), "The REA Accounting Model: A Generalized Framework for Accounting Systems in a Shared Data Environment," *The Accounting Review* 57(3): 554–578; standardized in ISO/IEC 15944-4 (Open-edi business transaction ontology). Core: economic reality decomposes into **Resources**, **Events** that increment/decrement them, and **Agents**, linked by *duality*, with *Commitments* preceding events.
→ **Derives:** Resource/Budget node (the "R" the draft lacked) · Event-as-core · Actor/Role ("A") · Goal/Order ≈ *Commitment* · deferred Customer/Economy ≈ external agent + economic exchange.

**Ostrom's design principles for the commons.** Ostrom, E. (1990), *Governing the Commons: The Evolution of Institutions for Collective Action*, Cambridge University Press (Nobel Prize in Economics, 2009). Eight principles for durable self-governed collectives: (1) clearly defined boundaries; (2) congruent rules; (3) collective-choice arrangements; (4) monitoring; (5) graduated sanctions; (6) conflict-resolution mechanisms; (7) recognized right to organize; (8) nested enterprises (polycentricity).
→ **Derives:** #1 → Boundary/Membership (deferred) · #2 → Policy/Invariant · #3 → Decision · #4 → Signal/Monitoring (deferred) · #5 → Sanction/Enforcement (deferred) · #6 → Conflict (incl. the trichotomy) · #8 → Phase/Epoch + nested Work.

**Normative multi-agent systems (deontic).** Boella, van der Torre & Verhagen (eds.), "Normative Multi-Agent Systems" (Dagstuhl Seminar, 2006–2008); Castelfranchi & Conte, *Trust Theory* (on trust/reputation); deontic logic (obligation / permission / prohibition). Core: agent collectives are governed by **norms** carrying **sanctions**, mediated by **trust/reputation**.
→ **Derives:** Policy/Invariant (norms) · **Decision modes map to deontic operators** — `Autonomous` = permission, `Notify`/`ApprovalRequired` = obligation, **`Forbidden` = prohibition** · deferred Sanction and Reputation/Trust.

**Speech-act / commitment theory.** Austin, J.L. (1962), *How to Do Things with Words*; Searle, J.R. (1969), *Speech Acts* — illocutionary acts (directives, commissives, declarations); Winograd & Flores (1986), *Understanding Computers and Cognition* — the commitment / "conversation-for-action" loop; Singh's commitment-based agent communication.
→ **Derives:** Decision as a *directive/declaration* · Goal/Order as a *commissive* (a commitment) · the AuthorityRequest → Decision → ExecutionReceipt triple as the commitment lifecycle (propose → commit → discharge).

> **Name-collision guard:** "Searle" (John R. Searle, the speech-act philosopher) is **not** "Searles" (Matt Searles, the lovyou.ai corpus author). Every citation to `raw/searles/` or "Searles philosophy" in this spec means the latter.

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
1. **One schema, two renderers.** Identical 15-type schema both worlds; only the source differs. Runtime = write an adapter emitting the contract shape.
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

## 7. Resolved — guided Q&A with the owner (2026-06-16)
1. **Goal vs Order → TWO nodes.** `Goal/Telos` (end-state, abstract, served by many Orders) + `Order` (concrete seed, decomposes into Work). Different lifecycle + precedent (Order ≈ REA Commitment; Goal ≈ the Searles "why the collective exists").
2. **Policy vs Invariant → TWO nodes.** `Policy` (tunable; per-action; amendable by a Decision) + `Invariant` (inviolable; continuously checked; HALT-on-violation; constitutional change only). Protects the fail-safe boundary — an Invariant is never a tunable Policy.
3. **Chart stays a STORY.** Keep the ~28 reconstructed narrative beats (`provenance:reconstructed`, mostly `done`) woven with live executionPlan work — delivers the construction-legibility goal. A "hide story beats" kanban toggle is deferred to B2.

Net: the ontology is now **15 node types** (9 original + 6 new core: Goal, Order, Policy, Invariant, Resource, Capability).

---

## 8. References (grounded citations)

Requirement (b): every item traces to a published fact — name(s), date, and an online link where one exists. Internal first-party sources ground to repo path + doc ID (no public URL, by policy). Verified 2026-06-16.

### 8.1 External precedents
- **[E1] REA — Resources, Events, Agents.** McCarthy, W. E. (1982). "The REA Accounting Model: A Generalized Framework for Accounting Systems in a Shared Data Environment." *The Accounting Review* 57(3): 554–578 (July). Standardized in ISO/IEC 15944-4. Overview: <https://en.wikipedia.org/wiki/Resources,_Events,_Agents>
- **[E2] Ostrom — commons design principles (the 8).** Ostrom, E. (1990). *Governing the Commons: The Evolution of Institutions for Collective Action.* Cambridge University Press (ISBN 978-0-521-40599-7). Nobel Memorial Prize in Economic Sciences, 2009. Peer-reviewed retrospective: "Governing the Commons for two decades," *International Journal of the Commons* (DOI 10.18352/ijc.325): <https://thecommonsjournal.org/articles/10.18352/ijc.325>
- **[E3] Normative multi-agent systems (deontic: obligation/permission/prohibition).** Boella, G., van der Torre, L., & Verhagen, H. (eds.), Dagstuhl Seminar 07122, "Normative Multi-agent Systems" (March 2007): <https://www.dagstuhl.de/seminars/seminar-calendar/seminar-details/07122> · "Introduction to Normative Multiagent Systems," DROPS DagSemProc 07122.2: <https://drops.dagstuhl.de/entities/document/10.4230/DagSemProc.07122.2> · JAAMAS special issue (2008), DOI 10.1007/s10458-008-9047-8: <https://link.springer.com/article/10.1007/s10458-008-9047-8> · trust/reputation: Castelfranchi, C. & Falcone, R., *Trust Theory* (Wiley, 2010).
- **[E4] Speech-act / commitment theory.** Austin, J. L. (1962). *How to Do Things with Words.* Oxford University Press. · Searle, J. R. (1969). *Speech Acts: An Essay in the Philosophy of Language.* Cambridge University Press. Overview: Stanford Encyclopedia of Philosophy, "Speech Acts": <https://plato.stanford.edu/entries/speech-acts/> · commitment / "conversation-for-action": Winograd, T. & Flores, F. (1986). *Understanding Computers and Cognition.* Ablex: <https://books.google.com/books/about/Understanding_Computers_and_Cognition.html?id=6TwbGGSz6NYC> · language/action perspective: <https://en.wikipedia.org/wiki/Language/action_perspective>

> **Name-collision guard (restated):** John R. **Searle** [E4] (speech-act philosopher) ≠ Matt **Searles** [§8.2] (LovYou/lovyou.ai corpus author).

### 8.2 Foundational philosophy — Searles (public)
Matt Searles, *LovYou* / mind-zero, Substack `mattsearles2.substack.com`; code: <https://github.com/mattxo/mind-zero-five>. The 43-post export (range **2026-02-28 → 2026-03-24**) is indexed locally with each post's title/date/URL at `raw/searles/all-posts-1.md` — the authoritative index. Posts grounding ontology decisions:

| ID | Post (title · #) | Date | URL | Grounds |
|---|---|---|---|---|
| S1 | 20 Primitives and a Late Night · 1 | 2026-02-28 | <https://mattsearles2.substack.com/p/20-primitives-and-a-late-night> | Event substrate; intelligence-as-operation; 20 primitives |
| S2 | From 44 to 200 · 2 | 2026-02-28 | <https://mattsearles2.substack.com/p/from-44-to-200> | 44/200 primitives; 14 layers; is-ought gap |
| S3 | The Architecture of Accountable AI · 3 | 2026-02-28 | <https://mattsearles2.substack.com/p/the-architecture-of-accountable-ai> | Event immutability (no Update/Delete); authority layer; AI-as-node |
| S6 | Fourteen Layers, A Hundred Problems · 6 | 2026-02-28 | <https://mattsearles2.substack.com/p/fourteen-layers-a-hundred-problems> | the 14 layers |
| S7 | The Four Strategies · 7 | 2026-02-28 | <https://mattsearles2.substack.com/p/the-four-strategies> | edge-weights-as-personality |
| S8 | What It's Like to Be a Node · 8 | 2026-02-28 | <https://mattsearles2.substack.com/p/what-its-like-to-be-a-node> | node-phenomenology |
| S9 | The Cult Test · 9 | 2026-02-28 | <https://mattsearles2.substack.com/p/the-cult-test> | permanent-tension Conflict; Cult-Test meta-norm |
| S11 | Thirteen Graphs, One Infrastructure · 11 | 2026-03-01 | <https://mattsearles2.substack.com/p/thirteen-graphs-one-infrastructure> | graphs-as-views-over-one-event-graph (hybrid substrate) |
| S13 | The Same 200 Primitives, Weighted Differently · 13 | 2026-03-01 | <https://mattsearles2.substack.com/p/the-same-200-primitives-weighted> | edge weights |
| S15 | The Market Graph · 15 | 2026-03-01 | <https://mattsearles2.substack.com/p/the-market-graph> | Customer/Economy (REA echo) |
| S19 | The Knowledge Graph · 19 | 2026-03-01 | <https://mattsearles2.substack.com/p/the-knowledge-graph> | Memory/Knowledge advisory; epistemic status |
| S21 | The Identity Graph · 21 | 2026-03-01 | <https://mattsearles2.substack.com/p/the-identity-graph> | Reputation/Trust; Identity |
| S23 | The Community Graph · 23 | 2026-03-01 | <https://mattsearles2.substack.com/p/the-community-graph> | Boundary/Membership/Belonging |
| S24 | The Governance Graph · 24 | 2026-03-01 | <https://mattsearles2.substack.com/p/the-governance-graph> | governance/decision structures |
| S25 | The Culture Graph · 25 | 2026-03-01 | <https://mattsearles2.substack.com/p/the-culture-graph> | Meaning/Value/Norm layer |
| S26 | The Existence Graph · 26 | 2026-03-01 | <https://mattsearles2.substack.com/p/the-existence-graph> | Being (L13); Three Irreducibles |

> Posts not individually keyed here (e.g. The Cognitive Grammar, Higher-Order Operations) are in the local index `raw/searles/all-posts-1.md` with exact date/URL — not re-typed here to avoid an unverified slug.

### 8.3 First-party — dark-factory / hive (internal; repo path + doc ID, no public URL)
Origin `transpara-ai/docs`, read in place at `/Transpara/transpara-ai/repos/docs/dark-factory/` (~322 md); per `PROVENANCE.md`. Internal — grounds to path + doc ID + date.

| ID | Source | Path / doc ID | Grounds |
|---|---|---|---|
| F1 | Dark Factory — Motive, Goal, Approach | `docs/dark-factory/Dark Factory - Motive, Goal, Approach.md` | Decision outcomes {Autonomous, Notify, ApprovalRequired, Forbidden}; control boundaries |
| F2 | v3.9 operative baseline (accepted 2026-06-05) | `docs/dark-factory/v3.9/` | authority/identity/SOPs, gates, FactoryOrder, Work, memory/knowledge/capability |
| F3 | v4.0 candidate doctrine (seed 2026-06-12) | `docs/dark-factory/v4.0/` | "the factory builds the factory"; capability-evolution |
| F4 | Civic roles (status: superseded) | `docs/dark-factory/civic-roles.md` | the 9 runtime roles → superseded by F5 |
| F5 | Roles catalog (canonical, v3.0.0) | `docs/roles-catalog.md` | 24-role dual-layer taxonomy; CanOperate; ModelPolicy |
| F6 | Tech crosswalk (status: review, canonical: false) | `…/epics/02-technology-decision-crosswalk-v3.9.md` · `DF-V3.9-EPIC-TECH-CROSSWALK` | concrete tech grounding |
| F7 | Roles/invariants **code** (code is truth) | `hive/pkg/hive/agentdef.go` (`StarterAgents()`) | authoritative 9-role list; **recover the 10-vs-14 invariant count here** (§2 TODO) |
| F8 | Wiki articles (this repo, derived) | `wiki/*.md` | each carries a "Sources & provenance" footer chaining back to S*/F* |

### 8.4 Open Brain (internal; captured thoughts)
Michael's captured-thought store (`mcp__open-brain__*`); not a committed mirror this run (`raw/open-brain/` empty per `PROVENANCE.md`). Cited by marker — e.g. `CIVWIKI-ONTOLOGY-GAP-MINE 2026-06-16` (gap-survey), `CIVWIKI-ONTOLOGY-LOCKED d3c2e95`. Internal — no public URL.
