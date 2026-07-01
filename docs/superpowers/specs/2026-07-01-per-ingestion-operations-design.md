# Per-Ingestion Operations (Add · Replace · Remove) — Design Spec

**Status:** draft v0.1 · **Date:** 2026-07-01 · **Owner:** Michael Saucier · **Authority:** planning (proposal, pending review) · **Repo/branch:** transpara-ai/wiki @ `feat/per-ingestion-operations`

> **Process provenance.** Derived through a brainstorming session (2026-07-01) against the live codebase (`compile/ingest_server.py`, `compile/refresh.py`, `compile/build_site.py`) and the **Civilization Ontology spec** (`docs/superpowers/specs/2026-06-16-civilization-ontology-design.md`). This spec realizes **Sub-project A — the "Update Now" mechanism** — which that spec explicitly deferred (§6, line 180).

---

## 0. Purpose & scope

Give the human operator, **at ingest time**, three explicit operations against a target topic:

- **(a) Add** — append raw information to a topic (today's behavior).
- **(b) Replace** — swap the raw information for a topic and re-derive its article.
- **(c) Remove** — retire a topic entirely, healing the graph around it.

**North-star constraint (owner, 2026-07-01):** the wiki must stay **instructive, educational, prescriptive, and easy for a human to follow and digest.** Every operation here is designed to be *legible* — a human can see what it will do, what it did, and what state the graph is now in, without reading code.

**Prime invariant (owner, 2026-07-01):** **maximum referential integrity at all times**, even during significant reprocessing of the corpus in reaction to raw-data changes.

### 0.1 In scope
The three operations, the raw-layer supersession mechanism they share, the single-article recompile engine, the two-layer integrity architecture, the edge-state machine, and the authority/provenance/secret-scrub controls.

### 0.2 Out of scope (deferred, see §9)
Full-corpus recompile; the front-page redesign (Item 2); the arc-metrics re-think (Item 2); plugin/skill/MCP recommendations (Item 3, advisory memo); a local-offline-model synthesis tier (future air-gap fallback).

---

## 1. The model — operation-mode, not stored policy

**Decision (owner, 2026-07-01):** the rules are a **per-ingestion operation mode**, *not* a persistent per-topic policy. When the human ingests, they choose one of `add | replace | remove` for that target topic, in that moment.

**Why this is the fail-safe choice.** No automated process (the 15-minute `refresh.timer`, any future re-sync) ever performs a destructive operation on its own. Destructive intent is always a human, in the moment, on the record. This is *"allowlist what's permitted"* (CLAUDE.md fail-safe doctrine): the deterministic timer keeps doing only its deterministic rebuild; destructive power is never delegated to a scheduler.

---

## 2. Grounding — every operation is append-only supersession over the Event substrate

The ontology spec (2026-06-16, §1.1) declares:

> `Event` is the **substrate**: an append-only, hash-chained log with **no Update/Delete** (fail-closed by data structure). All other node types are **projections** — the current state of any node is a fold over its ordered event history. *"Revise = supersede"* (§1.6, line 156).

This spec inherits that rule verbatim. **There is no destructive mutation anywhere in this design.** The three operations are *authoring intents* that resolve into **append-only supersession records**:

| Operation | What it appends | Projected effect (the fold) |
|---|---|---|
| Add | `SourceAdded` | topic gains a raw source; no supersession |
| Replace | `SourceSuperseded(old) + SourceAdded(new)` | old raw tombstoned, new raw authoritative, article marked for re-derivation |
| Remove | `TopicRetired(slug, reason, supersedes?)` | topic becomes a tombstone projection; inbound edges enter reconciliation |

**Consequence:** "delete" and "replace" are *never* an `rm` or an in-place overwrite of `raw/` or `wiki/`. They are new records that change what the *current fold* renders. Git history and `PROVENANCE.md` therefore keep the entire trail for free, and the doctrine *"raw/ verbatim, never hand-edited"* is preserved — superseded raw is retained, just no longer load-bearing.

`Note:` the live event store is deferred (per ontology §1.1 we *model* now, *build later*). Until then, supersession is recorded in article frontmatter + `PROVENANCE.md` + the ingest ledger (§6), which is the same fold expressed in files. The interface is designed so swapping to the live EventGraph later changes the *store*, not the *operations*.

---

## 3. The three operations

### 3.1 Add (unchanged)
Today's `append_frontmatter_list_items()` path: save upload to `raw/inbox/`, append `sources[]` / `raw_documents[]` references to `wiki/<slug>.md`, update the manifest, rebuild. Additive-only; creates no dangling edges; needs no recompile. **This code path is kept as-is.**

### 3.2 Replace — swap raw + immediate re-derivation

**Decision (owner, 2026-07-01):** Replace both **swaps the raw and recompiles immediately.** It decomposes into two steps by cost and reversibility:

1. **Swap raw (deterministic, instant, air-gap-safe, always runs):** append `SourceSuperseded(old)` + `SourceAdded(new)`; the old raw is tombstoned (retained, marked non-authoritative); the new raw is ingested. This half **never fails open** and **never needs the network**.
2. **Recompile prose (LLM, authority-gated, §5):** one authorized click re-derives *that one article* from its new authoritative raw set. While it runs, the freshness banner honestly shows `recompiling`. Offline/unauthorized → the article is marked `stale`; the swap already happened, so the page is honestly-stale, never silently-wrong.

### 3.3 Remove — cascading reconciliation (not a delete)

**Decision (owner, 2026-07-01):** Remove is a **cascading reconciliation** that preserves referential integrity, *not* a delete. Removing topic **T**:

1. **Authority-gated request** to retire **T**.
2. **Deterministic, instant (Layer 1, §4.1):** append `TopicRetired(T)`; T's article becomes a legible **retired tombstone stub** (`retired on DATE · reason · superseded-by X?`); **every** article with an inbound `[[wikilink]]` to T has that edge set to `dangling-pending` (§4.3). The graph is now fully consistent — no edge claims a validity it lacks — *before any LLM runs*.
3. **Reconciliation (Layer 2, §4.2 — authority-gated):** for each inbound article, the recompile engine attempts **in-context re-resolution**: can the article stand with T gone (re-point or cleanly drop the reference)?
   - **Reconcilable** → recompile the dependent cleanly; edge → `valid` or `cleanly-removed`.
   - **Truly broken** (nothing in the new state validly satisfies the old link) → the reference stays `dangling-pending` (visibly marked) **and the link-source's raw is enqueued for reprocessing** (owner's model, 2026-07-01).
4. **Run to closure:** reconciliation expands until **zero `dangling-pending` edges remain**. In practice this rarely passes direct dependents (a recompiled article is built from valid raw against the live article set, so it does not mint new dangling edges), but the *rule* is closure, not a hop-count.

A topic never just *vanishes*: **tombstone, not hard-delete** (provenance-footed + fail-legible doctrine).

---

## 4. The two-layer integrity architecture

The prime invariant (maximum referential integrity **at all times**) is met by separating **honesty** (cheap, always-on) from **finality** (expensive, gated). The central realization:

> Referential integrity is a property of what the graph **claims**, not of **when reprocessing finishes.** A link *visibly marked* "dangling — pending reprocess" does **not** violate integrity. Integrity is violated only when a link **renders live and resolves to nothing** — that is a lie. The first is honest incompleteness; the second is the thing we forbid.

### 4.1 Layer 1 — deterministic integrity pass (mandatory · instant · zero-spend · air-gap-safe)

The moment a Replace or Remove is requested, an **LLM-free** pass walks the graph and sets **every** affected edge to an explicit state. It is **atomic** and completes **before the operation is considered done**, regardless of whether any LLM ever runs. **This is the integrity guarantee**, and because it needs no LLM, **integrity holds even fully offline, even mid-cascade, even if reconciliation never runs.**

### 4.2 Layer 2 — reconciliation pass (authority-gated · restores completeness, not integrity)

The Claude recompile engine (§5) converting `dangling-pending` edges into `valid` (healed) or `cleanly-removed`. This is the spend part, so it is gated. **Default completion path:** one preview showing the **full transitive frontier to closure**, one authority decision to run it. Deferred/offline → Layer 1 already ran, so the graph is honest; Layer 2 queues and the banner shows the pending count.

### 4.3 The edge-state machine + the constitutional invariant

Every `[[wikilink]]` edge is in exactly one state:

| Edge state | Meaning | Renders as |
|---|---|---|
| `valid` | resolves, verified | live blue link |
| `cleanly-removed` | reconciliation decided the link should go | plain text, recorded |
| `dangling-pending` | target gone, not yet reconciled | **visibly marked** stale marker — *never* a live link |

**Constitutional invariant (fail-closed):** *no edge is ever in a state where it renders live but resolves to nothing.* The Layer-1 pass is the allowlist gate that enforces it: an edge renders live **only** when it is proven `valid`; every other state (including any state added later) falls through to a **non-live** rendering. There is no `default:` branch that renders a link live.

---

## 5. The recompile engine (Claude · one-click · authority-gated · offline→honest-stale)

**Decision (owner, 2026-07-01):** the immediate recompile is performed by **Claude, invoked by one authorized click**, degrading to honest-stale when offline/unauthorized.

Rationale (recorded because it reverses a deliberate prior choice): the codebase avoids LLM synthesis today, and the code says why — *"expensive + **autonomous** spend"* (`refresh.py`), *"a separate manual **decision**"* (`build_site.py`). The objection is to **silent, unauthorized, autonomous** spend, **not** to synthesis itself. The one-click gate removes exactly those words:

- **Not silent** — the human clicks "recompile now"; nothing happens behind their back.
- **Not autonomous** — the click **is** the authority decision, logged like the existing `deploy-authorization.json` / `.deploy-history.json` pattern.

**Engine contract:**
- Input: one target slug + its current authoritative raw set (+ for reconciliation, the removed/changed topic and the specific edge to resolve).
- Behavior: re-derive that one article's prose + `[[wikilinks]]`, fail-legible (state conflicts, mark thin evidence, gaps → `TBD`).
- **Fail-closed:** if the engine is unreachable, errors, or returns an unparseable/empty result → **do not touch the rendered article**; leave the deterministic swap/tombstone in place and mark the article `stale` / edges `dangling-pending`. Never fabricate synthesis; never fail open.
- **Offline fallback (future):** a local open-weight model tier may later serve air-gapped hosts; explicitly deferred (§9) so as not to trade the "instructive/educational" prose-quality bar for air-gap purity now.

---

## 6. Authority, provenance & secret-scrub

- **Authority record.** Every Replace and Remove (and each authorized recompile) appends to an **ingest-operation ledger** mirroring `compile/.deploy-history.json`: `{ ts, operation, target, actor, superseded[], affected_edges[], authorized_by, result }`. This is the audit fold; it is the same shape whether backed by files now or the EventGraph later.
- **Provenance.** Superseded raw and retired topics are recorded in `PROVENANCE.md` (tier/date/origin retained) — nothing is un-provenanced by removal.
- **Secret-scrub (non-negotiable, existing doctrine).** Any new raw entering `raw/` on a Replace passes the existing secret scan **before commit**; the operation fails closed if the scan fails.
- **Loopback-only.** These operations extend the existing authoring surface, which stays bound to `127.0.0.1:8787` and same-origin/token-gated — never LAN-exposed. No change to the trust boundary.

---

## 7. UX / legibility (human-digestible)

The `ingest.html` authoring surface gains, in the house style:

1. **Operation selector:** `Add · Replace · Remove` (Add is default; the two destructive modes are visually distinct).
2. **Consequence preview (mandatory for Replace/Remove):** before any action, show exactly what will happen — for Replace, which sources are superseded and that a recompile will follow; for Remove, the **full list of inbound articles** and the reconciliation frontier to closure. The human confirms this preview; confirmation is the authority decision.
3. **Honest live state:** the freshness banner shows `recompiling` / `N edges pending reconciliation`; the retired stub renders its tombstone; `dangling-pending` edges render with a visible marker. The human can always see the true state of the graph.

Everything a human needs to reason about the operation — before, during, after — is on screen. This is the north-star ("digestible") applied to the control surface itself.

---

## 8. Fail-safe analysis (the invariant, proven across the input domain)

Per CLAUDE.md: *prove the gate cannot fail open across its entire input space, not just the reported case.* The implementation MUST include tests over the whole domain:

- **Edge rendering:** for every edge state — `valid`, `cleanly-removed`, `dangling-pending`, **and any unknown/future value** — assert a live link renders **only** for `valid`; the fall-through renders non-live. (Allowlist, not denylist.)
- **Engine failure modes:** unreachable, timeout, error, empty result, unparseable result → assert the article is **untouched** and marked `stale`; never partially written, never fabricated.
- **Authorization:** missing/invalid authorization → operation refused, no raw swapped, no tombstone written. (Deterministic swap is gated behind the same confirm-as-authority step.)
- **Cascade closure:** after any Remove, assert **zero** `dangling-pending` edges that are *not* recorded in the pending-reconciliation queue — i.e., the graph is either healed or honestly-marked, never silently broken.
- **Secret-scrub:** raw containing a planted secret → Replace fails closed, nothing committed.

---

## 9. What this spec does NOT do (scope boundaries)

- No full-corpus recompile; the engine is strictly single-article (+ its reconciliation frontier).
- No local-offline-model synthesis tier (future air-gap fallback only).
- No change to the 15-minute deterministic refresh timer's behavior (it remains LLM-free).
- No front-page redesign, no arc-metrics re-think (Item 2 — separate spec).
- No live EventGraph store (deferred per ontology §1.1; supersession recorded in files meanwhile, behind an interface that can later bind to the EventGraph).

---

## 10. Provenance ledger

| Claim / decision | Corpus / code precedent | External precedent |
|---|---|---|
| Supersede, never delete | ontology spec §1.1 ("no Update/Delete"), §1.6 ("Revise = supersede"); `accountable-ai-architecture.md` ("interface has no Update()/Delete()") | Event sourcing / CQRS; immutable append-only ledgers |
| Per-ingestion mode, not scheduler-driven destruction | CLAUDE.md fail-safe ("allowlist what's permitted; scheduler never gets destructive authority") | least-privilege; human-in-the-loop control |
| Two-layer: deterministic honesty + gated finality | `refresh.py` (deterministic, LLM-free) vs `REBUILD.md` (manual LLM pass) — this spec formalizes the split | separation of liveness vs safety properties |
| Edge-state machine, fail-closed rendering | `build_site.py` red/blue link convention (TBD = red) | typed nullable state machines; total functions |
| One-click authority-gated spend | `compile/deploy-authorization.json`, `.deploy-history.json` | change-authorization / four-eyes gating |
| Tombstone, not hard-delete | fail-legible doctrine; `PROVENANCE.md` supersession | tombstoning in distributed stores |

---

## 11. Open questions (for owner review)

1. **Tombstone stub visibility:** should a retired topic's stub appear in the left nav (greyed, "retired"), or drop out of nav but remain reachable by direct link + search? (Recommend: drop from nav, keep reachable — retired ≠ discoverable, but never a 404.)
2. **Reconciliation queue runner:** when a Remove is authorized but the operator defers Layer 2, what runs the queued reconciliation later — the same one-click surface on next visit, or a listed "N pending" action on the home banner? (Recommend: both entry points, same engine.)
3. **Replace of a *source shared by multiple topics*:** if superseded raw is referenced by more than one article, does Replace mark *all* referencing articles for recompile, or only the target? (Recommend: mark all — integrity over economy — with the preview listing them.)
