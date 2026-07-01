# Civilization Arc Metrics Re-think — Design Spec (Item 2b)

**Status:** draft v0.1 · **Date:** 2026-07-01 · **Owner:** Michael Saucier · **Authority:** planning (proposal, pending review) · **Repo/branch:** transpara-ai/wiki @ `feat/arc-metrics-redesign`

> **Process provenance.** Brainstormed 2026-07-01. A thorough read of the live arc stack (`compile/assets/civilizationArcData.js` ~99KB, `civilizationArcNav.js` ~56KB, `civilizationOntology.js`, `civilizationArcLayout.js`, `civilizationArcDraw.js`, `compile/stats.py`, `compile/inflight.py`) produced a **convolution diagnosis** (below). The re-think is grounded in the **Civilization Ontology spec** (`docs/superpowers/specs/2026-06-16-civilization-ontology-design.md`), whose single-status rule the live data had silently violated. Layout direction chosen interactively from a rendered mockup.

---

## 0. Purpose & scope

**Re-think the convoluted `civilizationArc` tracking model** — root and branch, not a reskin. The owner's complaint (2026-07-01): *"the metrics by which the pieces are tracked has become convoluted over time."* Confirmed with evidence (§1).

**North star (owner):** instructive, educational, prescriptive, easy for a **human** to follow and digest.

**The introspective finding:** the convolution is not sloppy code — it is a **missing purpose.** The arc accreted 4 state-planes, 9 status vocabularies, and 6 grouping modes because it tried to be five things at once (timeline + gate register + worklist + evidence ledger + PR feed). A tracker's data model is only as clean as its purpose is singular.

**The purpose, chosen (owner, 2026-07-01):** the arc answers **one** question — **"Where are we, and what's next?"** Current-state / frontier read; history becomes secondary context. Every downstream decision falls out of this.

### 0.1 In scope
The arc data model (schema), the status model, evidence/freshness, referential integrity, and the arc page layout + its asset stack.

### 0.2 Out of scope
Item 1 (ingestion), Item 2a (front page), Item 3 (advisory memo). The live EventGraph store remains deferred (ontology §1.1); the arc is a read-projection, hand-fed + evidence-derived, behind an interface that can later bind to the EventGraph.

---

## 1. Diagnosis — the convolution (what we're curing)

Characterized from the live assets:

- **Four parallel, un-reconciled state-planes:** `items[]` (the only ontology-validated one), `liveReaderEvidence` (authority/evidence states — never merged into items), `executionPlan.nearTerm/complete` (a worklist **duplicating** items `n1`–`c10` with different field names, hand-synced), and `inflight` (live PRs merged at render time).
- **~9 coexisting status vocabularies:** `status` · `blocked` · `boundary_status` · `go_live_revalidation` · `provenance` · `evidence_state` · `authority_state` · executionPlan status · live-reader freshness — several firing on one item at once.
- **The smoking gun — Gate-K** carries `status:"done"` **and** `boundary_status:"pre-live-closed-go-live-blocked"` **and** `go_live_revalidation:"blocked"`, plus a prose `note` whose only job is to explain the contradiction its own fields create. When the model needs a paragraph to explain why "done" means "blocked," the model has failed to express the state. **This is a fail-open bug**: the piece renders complete (green) while a real acceptance scope is unmet.
- **Ontology divergence:** gates carry fields (`boundary_status`, `evidence_links`) the `civilizationOntology.js` validator never checks — the clean model and the data drifted apart. `item.sprint` isn't validated against `sprints[]` (orphan refs pass silently); gate families are hardcoded in **two** files.

---

## 2. The unified model

### 2.1 One job → one plane
All four planes collapse into **one** unified item list. `executionPlan` is folded in (no duplicate worklist). `liveReaderEvidence`/`authority_state` are **not** a side table — evidence attaches to the piece it justifies (§2.5). `inflight` remains, but as the **evidence source** for derived status (§2.5), not a separate plane merged blindly at render.

### 2.2 First-class pieces (owner, 2026-07-01)
Two tracked piece types on a **Phase backbone**:
- **Work** — what is being done.
- **Gate** — the checkpoints that define *"what's next."*

**Phase/epoch** is the backbone (the spine), not a piece. **Decision · Event · Goal · Artifact** demote to **detail-on-click**, not first-class lanes. (They remain in the ontology; the arc read-view just doesn't track them as pieces.)

### 2.3 One status vocabulary (ontology §1.5, finally enforced)
Every piece uses the single lifecycle: **`future → planned → active → done`**, with **`blocked`** as an overlay, and a structured **`blocked_reason ∈ {gate, resource, authority, recovery, dependency}`** (ontology facet) instead of free text. `boundary_status`, `go_live_revalidation`, `evidence_state`, `authority_state` are **deleted as parallel statuses.**

### 2.4 Status is DERIVED, fail-closed — never asserted (the Gate-K cure)
A Gate carries **acceptance `criteria[]`** (which is what a gate *is*). Each criterion has a state and an evidence basis (§2.5). **Gate status is a fail-closed rollup:**

- `done` **only if every** criterion is `done` (the permissive outcome is the *proven* branch);
- `blocked` if **any** criterion is `blocked` (blocked wins);
- `active` if any criterion is `active` and none blocked;
- else `planned`/`future`.

This makes the Gate-K contradiction **structurally impossible** — you cannot author `done` while a criterion is unmet. (Mirrors Item 1's edge-state machine: prove the permissive branch, fail closed on everything else, no `default:` that completes.)

### 2.5 Distinct scopes → distinct gates (owner, 2026-07-01)
Genuinely different acceptance scopes become **separate gates**, each with its own criteria and derived status:
- `Gate-K (pre-live)` → `done`, **behind** the frontier;
- `Gate-K (go-live)` → `blocked`, **ahead** = literally *"what's next."*

The frontier reads cleanly and no single gate juggles two states.

### 2.6 Evidence-basis + freshness, stamped on every piece (owner, 2026-07-01)
Status is **evidence-derived where evidence exists** (live PRs, gate artifacts, merge state via `inflight`), hand-authored only where it must be (reconstructed history). **Every piece carries its evidence basis and freshness:**

```
evidence: { basis: derived | reconstructed | asserted,
            source: "PR#84" | "artifact:test-001" | "reconstructed:feb-genesis",
            observed_at: <iso>, freshness: live | dated | stale }
```

So `active` visibly means either *"observed 2 min ago via PR#84"* or *"hand-asserted, last confirmed weeks ago."* Per-piece fail-loud honesty — the stale-while-green problem is structurally gone. (`reconstructed` reuses the ontology's `provenance` facet; the Feb genesis is stamped `reconstructed`, never dressed as derived.)

### 2.7 Referential integrity enforced (fail-closed)
The `civilizationOntology.js` validator is tightened to **fail the build** on: any `item.phase` not in `phases[]`; any `item.gate`/`dep` not resolving; any parallel-status field present; any gate without `criteria[]`. **One** source of truth for gate families (delete the duplicate). The `now`-frontier is **derived** (the boundary after the last `done`/`active` piece; `next` = the nearest `planned`/`blocked` gate ahead), never hand-placed. (Same referential-integrity invariant as Item 1.)

---

## 3. Layout — the "where are we" read

1. **Freshness header** — the arc-wide derived/updated stamp (honest, computed).
2. **The now-panel ("you are here")** — the current phase, with two columns: **active now** (work items + per-piece evidence stamps) and **next gate** (the next blocking gate with its acceptance-criteria checklist and the fail-closed rollup shown). This answers the question in one glance and is *prescriptive* (what must be true to advance).
3. **The phase spine** — phases along a backbone, each colored by its rollup status, with the **now-frontier** marked; **past phases collapse** (history is context, not the point).
4. **One-status legend** — the single vocabulary + *"every status is evidence-derived or stamped."*

**Grouping modes collapse from 6 to the spine itself.** The `tracks/status/repo/sprint/gate/actor` toggle system is removed; the phase spine + now-panel *is* the view. A lightweight optional filter (e.g. by repo) may remain as a secondary affordance, but never as a parallel layout engine.

---

## 4. Migration & implementation (net deletion, not addition)

- **`civilizationArcData.js`** → rewritten to the single unified schema (Work + Gates + Phases, one status, criteria, evidence). The `executionPlan`, `liveReaderEvidence`, and gate-specific status fields are removed.
- **`civilizationArcNav.js` (~56KB)** → **largely deleted.** It existed to drive 6 mode toggles + focus logic over 4 planes; the "where are we" view doesn't need it.
- **`civilizationArcLayout.js` / `civilizationArcDraw.js`** → simplified or replaced. The now-panel + phase spine are near-static HTML/CSS emitted by the builder; they do **not** need the ordinal-scale SVG engine. Net **deletion** of code — the opposite of accretion.
- **`civilizationOntology.js`** → **kept and tightened** as the validator: enforce the single vocabulary, the derived-status/criteria rule, referential integrity, and rejection of any parallel-status field.
- **`compile/inflight.py`** → retained; becomes **the** derived-status/evidence source for live pieces (already polls PRs; now feeds per-piece `evidence`).
- **`compile/build_site.py` `arc_page()`** and **`stats.py`** → rewired to the new schema.
- **Air-gap:** all assets local; no CDN/external fonts. **No LLM** in the arc path (deterministic, like `refresh.py`).

---

## 5. Fail-safe analysis (prove the gate can't fail open across the domain)

Per CLAUDE.md — test the whole input space, not the reported case:
- **Derived rollup:** for every combination of criteria states, assert gate status = the fail-closed rollup (`done` **only** when all `done`; `blocked` dominates; unknown/absent criterion → **not** `done`). No combination yields a fail-open `done`.
- **Referential integrity:** orphan `phase`/`gate`/`dep` refs → build **fails** (not a silent pass). A gate with no `criteria[]` → build fails.
- **Parallel-status rejection:** presence of any deleted field (`boundary_status`, etc.) → validation **fails** (prevents regrowth of the convolution).
- **Freshness honesty:** a piece whose evidence is older than a threshold renders `stale`/`dated`, never plain-current; a `reconstructed` piece never renders as `derived`.
- **Frontier derivation:** `now`/`next` computed purely from status; no hand-placed frontier accepted.

---

## 6. Ontology conformance
This spec **realigns** the arc with the 2026-06-16 ontology it had drifted from: the single status lifecycle (§1.5), `blocked_reason` facet, `provenance ∈ {reconstructed, derived}`, gates carrying acceptance criteria (the `satisfies`/`gated-by` edges), and the fail-closed status rule (`Forbidden`/deny-by-default lineage). Where reality needed a field the ontology lacked (evidence-basis/freshness), this spec proposes it as an **ontology amendment**, not an unchecked pass-through.

---

## 7. Provenance ledger

| Decision | Corpus / code precedent | External precedent |
|---|---|---|
| Purpose = "where are we + what's next" | owner 2026-07-01; `civilization-arc.md` (read-lens, display-only) | dashboard "single-question" design |
| One status vocabulary | ontology §1.5 (the rule the data violated) | state machines / total functions |
| Status derived fail-closed from criteria | CLAUDE.md fail-safe; ontology §1.4 (`Forbidden`, allowlist) | CI gates; four-eyes acceptance |
| Split distinct scopes into distinct gates | ontology §1.4 ("Gate-E overloaded — keep distinct") | avoid overloaded state objects |
| Evidence-basis + freshness per piece | `PROVENANCE.md`; `inflight.py`; ontology `provenance` facet | provenance / data lineage; honest-staleness |
| Referential integrity enforced | Item 1 spec (same invariant); ontology validator | foreign-key constraints |
| Single plane, evidence first-class | diagnosis §1 (4 planes → 1) | single source of truth / normalization |

---

## 8. Open questions (for owner review)

1. **Freshness threshold** — after how long does a `derived` status decay to `dated`/`stale`? (Recommend: mirror the existing refresh cadence — anything older than one refresh interval is `dated`, well beyond is `stale`.)
2. **Acceptance-criteria authoring** — are gate criteria hand-authored from the doc set, or pulled from a machine-readable gate register where one exists? (Recommend: hand-author now, mark each criterion's evidence basis; migrate to derived as registers appear.)
3. **How much history stays visible** — do collapsed past phases expand on click into the old timeline, or link out to a dedicated "arc origin / journey" article (which also receives the front-page narrative moved in Item 2a)? (Recommend: link out — one narrative home, shared with 2a.)
4. **Retire vs keep the old asset stack** — delete `civilizationArcNav.js`/`Draw.js` outright, or keep a feature-flag fallback during migration? (Recommend: delete once the new view passes tests; git history is the fallback.)
