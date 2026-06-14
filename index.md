---
title: Civilization Wiki — index
last_compiled: "2026-06-14"
run: "Run-3 (thirteen-graphs completion + arc advancement + runtime objects)"
status: partial — approaching corpus coverage
article_count: 89
---

# Civilization Wiki — index

The arc spine and article index for the Transpara-AI Civilization wiki. This is a
[Karpathy-style LLM wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f):
a self-maintaining, interlinked knowledge substrate compiled from the corpus
(see `DESIGN.md`). The wiki is the source of truth for the narrative; every
downstream view (Mission Control, the spine/story view) is a read lens onto it.

---

## ⚠ Freshness — read this first (fail-loud)

| Field | Value |
|---|---|
| **last_compiled** | **2026-06-14** |
| **run** | **Run-3 (thirteen-graphs completion + arc advancement + runtime objects)** |
| **articles compiled** | **89** (25 foundational · 24 architecture · 10 arc · 16 investigation · 13 concept · 1 meta) |
| **completeness** | **PARTIAL — arc spine, philosophy, runtime objects, and thirteen-graphs complete; full corpus sweep still deferred** |

**This is Run-3, not the finished wiki.** Run-1 compiled the core spine. Run-2
extended that with the landscape survey entities, the Searles philosophy fill-in,
and fifteen landscape investigation-tier articles. **Run-3** closes the deferred
long-tail from Run-2: the remaining individual thirteen-graphs articles (the-44-primitives,
the-200-primitives, the-work-graph, and all nine new per-graph articles through
the-existence-graph), the runtime objects (authority-request, execution-receipt,
bounded-runtime), the observatory surface and its transparency contract, the first
fully-completed slice-1 run, the deployment arc plan, the roles catalog, gate-k,
mind-zero-five, open-weight LLM routing, upstream-fork-sync, hermes-self-evolution,
offline-llm-optimization, and the civilization-wiki meta article. **The full corpus
is still not swept** — the ~8,783-file / ~73-repo / ~1,175-thought substrate named
in `DESIGN.md` has not been exhausted. Treat any concept not in the article index
below as **not-yet-compiled**, not as absent from the project.

**Fail-legible by construction.** Where this index would otherwise emit a link to
an article that does not exist, it instead writes **TBD** and says why. No
wikilink below points at a missing file; gaps are marked, never invented. Every
`[[...]]` link in this index resolves to a real file in `wiki/`.

**Known compile-time tensions carried up from the articles** (stated, not
silently resolved):
- **Nine vs ten civic roles.** The code-grounded count is **nine**
  (`[[civic-roles]]`, `[[the-civilization]]`, and the canonical roles catalog
  all enumerate nine `StarterAgents()`). `[[the-drift]]` previously said "ten
  bootstrap civic roles" while listing only nine names; Run-2 corrected its
  wording to **nine**, consistent with its own list. This index uses **nine**.
- **v4.0 status.** Seed doctrine **accepted 2026-06-12**; the v4.0 folder is
  **candidate / proposal-only and not canonical**. v3.9 remains operative. See
  `[[v4-0]]` and `[[v3-9]]`.
- **Repo identity (event graph).** The Searles posts name `mind-zero-five`; the
  dark-factory docs and Open Brain name `transpara-ai/eventgraph` (and
  `lovyou-ai/eventgraph`). They are **not asserted to be the same repo**. See
  `[[event-graph]]` and `[[the-lovyou-ai-fork]]`.
- **The Feb genesis is reconstructed, not derived from commits.** Day one is not
  in the digital record (org forks start 3/30; Open Brain starts 3/3). It is
  reconstructed from `raw/searles/` and the Substack post dates. See
  `[[the-20-primitives]]`, `[[the-lovyou-ai-fork]]`, and `DESIGN.md` §"The Feb
  genesis."
- **"Civilization" the survey vs the operative concept.** The 2026-05-13
  **Civilization Landscape Investigation** was the *name of a one-time survey*;
  the drift diagnosis later found "civilization" appeared only ×8 in the v3.9
  folder, all referring to that survey, not a living civilization. See
  `[[civilization-landscape-investigation]]` and `[[the-drift]]`.
- **Thirteen-graphs layer-numbering conflict.** Scheme A (Post 11, dark-factory
  synthesis) and Scheme B (Post 6 / layer specs) name some layers differently.
  Both schemes are reproduced in the affected articles; this index uses Scheme A
  numbering for the tier names. See `[[thirteen-graphs]]`.
- **Gate K and Gate L.** Defined in v4.0 but unsatisfied as of 2026-06-14. They
  extend the Gate A–J lettering with a different scope (development-loop hardening
  and v3.9-to-v4.0 reconciliation). See `[[gate-k]]`; Gate L article deferred.

---

## The arc

A chronological spine from day one to the present. Each `[[...]]` link is a
compiled article; **TBD** marks a node the grounded record names but the wiki has
not yet given its own article.

### 1 — Day one: the 20 primitives (2026-02-28)

The whole arc starts on **2026-02-28** with Matt Searles' post *"20 Primitives
and a Late Night."* The origin was a narrow engineering question — *how do you
trace a bad outcome back to the thing that caused it, and where exactly did the
chain break?* — answered with an event graph where every node has an input, an
operation, and an output, and everything is traceable to its source. The seed was
produced by **incremental specification loading** (feed the model the vision one
message at a time, each ending "Respond ok," before asking for synthesis), the
method that outlived the post. → **`[[the-20-primitives]]`**

> Genesis caveat: this day predates the first fork and the runtime, and survives
> only in the source corpus — reconstructed from `raw/searles/` and post dates,
> not from commit history.

### 2 — The philosophy: the derivation ladder and the irreducibles

From the seed, Searles (working with Claude) built out a philosophy across the
2026-02-28 → early-March posts. The primitives climb a **derivation ladder —
20 → 44 → 200** — across fourteen layers (`[[the-primitives]]`,
`[[fourteen-layers]]`, `[[the-20-primitives]]`, `[[the-44-primitives]]`,
`[[the-200-primitives]]`), reachable by a small **cognitive grammar** of
operations (`[[the-cognitive-grammar]]`, `[[derivation-method]]`,
`[[higher-order-operations]]`). The ontology is **self-referential** — a
**strange loop**, Return-to-Event (`[[strange-loop]]`). The framework names
**three things it explicitly cannot derive** — moral status, consciousness, being
— and an is-ought bridge offered as hypothesis, not proof
(`[[three-irreducibles]]`, `[[second-derivation-convergence]]`,
`[[the-moral-ledger]]`). The philosophy guards itself against being a closed
system (`[[the-cult-test]]`, `[[the-permanent-tensions]]`,
`[[three-evaluative-axes]]`), and reads the node's-eye view of all this as lived
experience (`[[node-phenomenology]]`, `[[religion-as-paths-from-being]]`).

Three load-bearing architectural ideas fall out of the philosophy and carry
forward into every later build:
- **The event graph** — append-only, hash-chained, causally linked; "the moral
  ledger at scale." → `[[event-graph]]`
- **Intelligence is just another operation type** — the AI stays *inside* the
  accountability graph as a node, never above it. → `[[intelligence-is-an-operation-type]]`
- **The authority layer** — graduated consent (Required / Recommended /
  Notification). → `[[authority-layer]]`

These are demonstrated, not just argued, in **mind-zero-five** — the running Go
code Searles published as *"The Architecture of Accountable AI"* (the operational
"it runs right now" claim is the author's testimony; the wiki read the prose and
quoted excerpts, not the repo). → `[[accountable-ai-architecture]]`,
`[[crash-recovery-as-ethics]]`, `[[mind-zero-five]]`

The product horizon Searles sketches on top of the same substrate — one event
graph, thirteen lenses — is `[[thirteen-graphs]]`. The first three graphs have
full deep-dive articles: `[[the-work-graph]]` (Layer 1, the one being deployed),
`[[the-market-graph]]` (Layer 2), `[[the-social-graph]]` (Layer 3). Nine more
are now compiled through Layer 13: `[[the-justice-graph]]`, `[[the-research-graph]]`,
`[[the-knowledge-graph-searles]]`, `[[the-ethics-graph]]`, `[[the-identity-graph]]`,
`[[the-population-graph]]`, `[[the-culture-graph]]`, `[[the-meta-graph]]`,
`[[the-existence-graph]]`. Two proposal extensions are also compiled:
`[[edge-weights-as-personality]]` and `[[the-four-strategies]]`. The corpus is
taken into the Transpara work as the **Searles primitive basis** — **motive,
vocabulary, and accountability premise only**, never as proven metaphysics or
implementation authority. → `[[primitive-basis]]`

### 3 — The lovyou.ai fork (Feb–March 2026)

Searles' own first system was **hive0 / LovYou** — a multi-agent system on the 20
primitives that grew to "roughly seventy agents," most of which he says he did not
design ("the hive had decided it needed them"). That LovYou / `lovyou-ai` lineage
is the upstream the Transpara runtime was **forked** from: the earliest captured
spawn-lifecycle thoughts name the repo `lovyou-ai-hive` before the `transpara-ai`
fork convention took hold, and an early guardian-governance fix landed on the
`lovyou-ai`/upstream hive. Under `transpara-ai` ownership the forked repos
(`agent`, `eventgraph`, `hive`, `site`, `work`, plus `docs`) became the substrate
the live `[[hive-governance]]` runtime and the whole `[[dark-factory]]` arc are
built on. → **`[[the-lovyou-ai-fork]]`**

> Fail-legible: the **2026-03-30 fork date** of those five repos is asserted by
> the task framing, not corroborated by a capture (earliest captured repo work is
> 2026-04-08/09); the **Feb-2026 first fork-and-build** predates both the org
> GitHub history and Open Brain (which starts 2026-03-03) and is reconstructed,
> not recorded. The fork's philosophy is `[[primitive-basis]]`; upstream is cited
> as context only, never re-published. See also `[[agent]]`, `[[hive-governance]]`.

### 4 — The Civilization Landscape Investigation (2026-05-13)

On **2026-05-13** a **Civilization Landscape Investigation** was run: a single
multi-phase research session that surveyed a fixed 22-item candidate list (native
Dark Factory core, prior in-house research, and a wide cut of the external
agent-tooling landscape) and asked of each — *is this already in the design; if
not, what is its exact marginal contribution, and what would it replace,
strengthen, or make possible?* Its headline conclusion was that **no surveyed
tool beats the native kernel**; its lasting product was the eight gaps it found
and the U1–U10 update set that defines the v3.8 → v3.9 delta. Concretely,
**v3.9 = the accepted v3.8 baseline + this investigation**, with external
frameworks routed to references / optional adapters / patterns and kept out of
all control roles (v3.9 Decision 15). →
**`[[civilization-landscape-investigation]]`**, **`[[v3-9]]`**

> The fifteen surveyed tools that now have their own `investigation`-tier
> articles — `[[gstack]]`, `[[paperclip]]`, `[[symphony]]`, `[[multica]]`,
> `[[hermes-agent]]`, `[[openclaw]]`, `[[pageindex]]`, `[[mempalace]]`,
> `[[ob1]]`, `[[miro-stack]]`, `[[agent-governance-toolkit]]`,
> `[[solo-orchestrator]]`, `[[graphify]]`, `[[claw-code]]`,
> `[[bitsandpieces]]` — were compiled from the first-party survey checkpoints
> and Open Brain, **not** from `raw/investigations/*`, which is still empty
> (Phase 2, per `PROVENANCE.md`). They are the landscape *as Transpara
> evaluated it*, not a re-publication of each upstream project.

### 5 — The nine-agent civilization design

The Transpara design names a **society of nine civic roles** — strategist,
planner, implementer, reviewer, guardian, cto, spawner, allocator, sysmon — the
`AgentDef` structs registered by `StarterAgents()` in `pkg/hive/agentdef.go`.
They coordinate **only through the shared append-only event graph** (the
"hive-mind property, obtained for free"), with the human as the top authority
tier. Only `implementer` has filesystem access; `guardian` sits outside the
hierarchy and reports to the human; `spawner` + a growth loop can add new
trust-gated members (`CanOperate=false`) at runtime. → **`[[civic-roles]]`**

This society is the engine of the **north-star model: "one civilization, one
business"** — the civic roles and growth loop *perform and govern* the factory.
→ **`[[the-civilization]]`**

The complete roles picture now has a dedicated article: `[[roles-catalog]]`
(DF-ROLES-CATALOG v3.0.0, promoted canonical 2026-06-14) enumerates all **24
roles in two layers** — the 9 runtime agents plus 15 governance policy roles from
the accepted v3.9 authority doctrine.

> Fail-legible: this is the **Transpara nine**, distinct from Searles' ~70-agent
> hive0 (`[[primitive-basis]]`, `[[the-lovyou-ai-fork]]`). `[[the-drift]]`'s
> wording was corrected from "ten" to **nine** in Run-2.

### 6 — The drift, then the reunification (2026-06-05)

By **2026-06-05** the build had **drifted**: it had grown **two systems on one
event-graph substrate that never connected** — a living `[[hive-governance]]`
civilization with a working growth loop, and a standalone dark-factory
accountability pipeline (the `work/epic*.go` Gate A–J fixtures) running *beside*
it, not *through* it. The diagnosis is reproducible from source
(`grep -rnE 'guardian|cto|spawner|strategist' work/epic*.go` returns no
civic-role references) and summarized as **"the cage was perfected; the
inhabitants never moved in."** → **`[[the-drift]]`**

The same day, the **reunification workstream** opened (`authority: planning`,
demonstration-first) to pull the program back onto "one civilization, one
business": prove the reunion with one real `FactoryOrder` run before rewriting
doctrine. The civilization's **first reunified act was to document its own
society** (it wrote `civic-roles.md`). → **`[[the-reunification]]`**,
**`[[the-civilization]]`**

### 7 — The present (as of 2026-06-14)

The governed-production effort now has a single umbrella article,
**`[[dark-factory]]`**, synthesizing the orientation doc and the version lineage
(v2 2026-05-10 → v3.0 2026-05-11 → v3.9 accepted 2026-06-05 → v4.0 doctrine
accepted 2026-06-12). Within it:

- **`[[v3-9]]` is the operative baseline** — accepted by Michael Saucier on
  **2026-06-05**; the canonical doc/spec baseline for all current
  implementation. Its gate completions are real but **bounded-fixture**, not
  general production proofs.
- **`[[v4-0]]` is candidate doctrine** — seed folder opened **2026-06-01**, seed
  ADR (*the development process is itself a governed Civilization function — the
  factory builds the factory*) **accepted 2026-06-12**. The v4.0 folder remains
  **proposal-only and not canonical**; it does **not** supersede v3.9 and
  authorizes no implementation.
- **G-1.2 round 6 (2026-06-12): the first society to finish.** Slice-1 round 6
  (v16) closed as `finished-unsignalled` — the first epoch in which the
  [[hive-governance]] civilization completed all assigned work (a 24-role catalog
  FactoryOrder), sealing the chain at **1,128 events** after 45 minutes of
  unattended flight. The v15 fix set was proven live (budget exhaustion, renewal,
  six reviews). Three new findings (F1 Reason-phase cwd, F2 dual-spec oscillation,
  F3 terminal quiescence with no exit) are the candidate scope for the next fix
  set. → **`[[slice-1-completion]]`**
- **The Observatory shipped (2026-06-13/14).** The `/ops/observatory` route in
  `[[site]]` delivers the T1–T7 transparency contract as seven read-only panels
  (vitals, spend-vs-cap, agent roster with 24h state timelines, pipeline phase
  costs, authority queue, causal trace explorer, live event pulse). Read-only by
  construction; fail-legible by design. Merged as site#76 and site#77. →
  **`[[the-observatory]]`**, **`[[observability]]`**
- **`[[deployment-arc]]` is the program plan** (authority: planning, canonical:
  false) that takes the civilization from local scratch-space runs to a
  continuously-operated production factory in eight phases.
- **Gate-E decision is pending.** Grant-2 is exhausted. Gate-E (or a new grant)
  is Michael Saucier's decision exclusively. The v16 daemon remains alive and
  frozen by design pending that decision. → **`[[slice-1-completion]]`**,
  **`[[gate-k]]`** (Gate K: defined and unsatisfied; Gate L: deferred).

---

## Article index

89 articles compiled, grouped by tier. Tier is taken verbatim from each article's
frontmatter.

### Foundational — the Searles source philosophy (25)

The accepted philosophical basis (motive and vocabulary only, never proven
metaphysics or implementation authority).

| Article | Entity |
|---|---|
| `[[the-20-primitives]]` | The 20 Primitives — day one of the arc (2026-02-28) |
| `[[the-44-primitives]]` | The 44 Primitives — hive0 accidental derivation; Layer 0 of the 14-layer ontology |
| `[[the-200-primitives]]` | The 200 Primitives — the full 14-layer ontology (44 + 156 derived across 13 layers) |
| `[[the-primitives]]` | The Primitives — derivation ladder: 20 → 44 → 200 |
| `[[fourteen-layers]]` | The Fourteen Layers — the Layer 0–13 vertical stack |
| `[[the-cognitive-grammar]]` | The Cognitive Grammar — Derive / Traverse / Need |
| `[[derivation-method]]` | The Derivation Method — how the primitives were derived |
| `[[strange-loop]]` | The Strange Loop — the self-referential ontology (Return-to-Event) |
| `[[three-irreducibles]]` | The Three Irreducibles — is-ought / the moral-ledger argument |
| `[[event-graph]]` | The Event Graph — append-only, hash-chained "moral ledger" / kernel |
| `[[intelligence-is-an-operation-type]]` | Intelligence Is Just Another Operation Type — the AI stays in the graph |
| `[[authority-layer]]` | The Authority Layer — graduated consent (Required / Recommended / Notification) |
| `[[accountable-ai-architecture]]` | The Architecture of Accountable AI (mind-zero-five) — the running-code proof |
| `[[the-permanent-tensions]]` | The Permanent Tensions — the four unresolvable axes (anti-utopian feature) |
| `[[the-work-graph]]` | The Work Graph — Layer 1 (Agency); the graph being built; Lovatts deployment |
| `[[the-justice-graph]]` | The Justice Graph — Layer 4 (Institutional); dispute resolution on the chain |
| `[[the-identity-graph]]` | The Identity Graph — Layer 8 (Civilisational); behaviour-first identity |
| `[[the-research-graph]]` | The Research Graph — Layer 5 (Technology); provenance-enforced science |
| `[[the-knowledge-graph-searles]]` | The Knowledge Graph (Searles) — Layer 6 (Information); claim-provenance layer |
| `[[the-ethics-graph]]` | The Ethics Graph — Layer 7 (Civilisational); harm detection, is-to-ought |
| `[[the-governance-graph]]` | The Governance Graph — Layer 10/11 (Civilisational); governance decisions on the chain |
| `[[the-population-graph]]` | The Population Graph — Layer 9 (Scheme A); demographic scale, aggregate patterns |
| `[[the-culture-graph]]` | The Culture Graph — Layer 12 (Scheme A); provenance of meaning |
| `[[the-meta-graph]]` | The Meta Graph — Layer 12 (Scheme A); system watching itself, emergence detection |
| `[[the-existence-graph]]` | The Existence Graph — Layer 13; the thing you deploy the other graphs inside |

### Architecture — the entities the system is built from (24)

The standing components and design objects of the platform/runtime, including the
basis and north-star entities.

| Article | Entity |
|---|---|
| `[[primitive-basis]]` | Searles Primitive Basis — source philosophy, as motive/vocabulary only |
| `[[agent]]` | Agent — identity and lifecycle core (`transpara-ai/agent`) |
| `[[hive-governance]]` | Hive / Governance Layer — the civilization runtime (`transpara-ai/hive`) |
| `[[civic-roles]]` | Hive Civic Roles — the nine bootstrap agents (`StarterAgents()`) |
| `[[roles-catalog]]` | The Roles Catalog — 24 roles in two layers; canonical 2026-06-14 (DF-ROLES-CATALOG v3.0.0) |
| `[[the-civilization]]` | The Civilization — "one civilization, one business" (north star) |
| `[[factory-order]]` | FactoryOrder — the durable unit of work / unit of cooperation |
| `[[work]]` | Work — the production DAG and task lifecycle (`transpara-ai/work`) |
| `[[gates]]` | Gates — verification, trace, and release gates (A–J; K/L are v4.0) |
| `[[gate-k]]` | Gate K — interim loop hardening gate (v4.0, defined and unsatisfied) |
| `[[runtime-broker]]` | RuntimeBroker — the bounded execution envelope |
| `[[bounded-runtime]]` | Bounded Runtime — execution envelope (`CanOperate`, `BudgetConfig`, containment tripwire) |
| `[[authority-request]]` | AuthorityRequest — gated consent object; the protected-action ask |
| `[[execution-receipt]]` | ExecutionReceipt — proof-of-work artifact that closes the authority lifecycle |
| `[[the-mind-loop]]` | The Mind Loop — the bounded autonomous self-improvement loop (mind-zero-five) |
| `[[mind-zero-five]]` | mind-zero-five — the open-source Go implementation (`github.com/mattxo/mind-zero-five`) |
| `[[capability-evolution]]` | Capability Evolution — governed self-improvement as production work |
| `[[memory-knowledge-advisory]]` | Memory and Knowledge — the advisory-only layer (incl. this LLM wiki) |
| `[[edge-weights-as-personality]]` | Edge Weights as Personality — the (proposed) weighted-graph extension |
| `[[site]]` | Site — the governed operator console (Gate-E surface, society view) |
| `[[the-observatory]]` | The Observatory — read-only civilization transparency surface (`/ops/observatory`) |
| `[[observability]]` | Observability — the T1–T7 transparency contract; fail-legible by construction |
| `[[open-weight-llm-routing]]` | Open-Weight LLM Routing — v3.9 `df-model-broker` + Pi selector harness (design phase) |
| `[[upstream-fork-sync]]` | Upstream Fork Sync — institutional one-way fork sync controller |

### Arc — the dark-factory chronology and turning points (10)

The dated stations of the narrative: the upstream fork, the landscape survey, the
umbrella, the operative baseline, the candidate doctrine shift, the control-plane
proof, the diagnosed drift, its correction, the first completed society run, and
the program plan.

| Article | Entity |
|---|---|
| `[[the-lovyou-ai-fork]]` | The lovyou.ai Fork — upstream → `transpara-ai` (Feb–Mar 2026) |
| `[[civilization-landscape-investigation]]` | The Civilization Landscape Investigation — the 22-item survey (2026-05-13) |
| `[[dark-factory]]` | Dark Factory — the umbrella over the governed-production effort |
| `[[v3-9]]` | Dark Factory v3.9 — operative baseline (accepted 2026-06-05) |
| `[[v4-0]]` | Dark Factory v4.0 — candidate doctrine shift (seed accepted 2026-06-12) |
| `[[base-slice-0]]` | Base Slice 0 — the control-plane proof |
| `[[the-drift]]` | The Drift — two systems on one substrate (diagnosed 2026-06-05) |
| `[[the-reunification]]` | The Reunification Workstream — "one civilization, one business" (opened 2026-06-05) |
| `[[slice-1-completion]]` | Slice 1 Completion — G-1.2 round 6; first society to finish (2026-06-12) |
| `[[deployment-arc]]` | The Deployment Arc — program plan from Slice 1 to continuous production (2026-06-09) |

### Investigation — the surveyed agent-tooling landscape (16)

The external tools, frameworks, and prior research the 2026-05-13 landscape
investigation evaluated — compiled from the first-party survey checkpoints and
Open Brain, **not** from `raw/investigations/*` (still empty, Phase 2). Each was
admitted only as a reference / optional adapter / pattern, never as a control
role (v3.9 Decision 15).

| Article | Entity |
|---|---|
| `[[agent-governance-toolkit]]` | Agent Governance Toolkit — `PolicyEngineAdapter` candidate (Microsoft) |
| `[[gstack]]` | gStack — software-factory workflow/skill pattern (Garry Tan) |
| `[[paperclip]]` | Paperclip — org / budget / approval UX pattern only |
| `[[symphony]]` | Symphony — trials / proof-of-work packaging pattern |
| `[[multica]]` | Multica — managed-agent / teammate-board UX pattern |
| `[[hermes-agent]]` | Hermes Agent — governed self-evolution optimizer pattern (deferred) |
| `[[hermes-self-evolution]]` | Hermes Self-Evolution — DSPy + GEPA evolutionary optimization pipeline (forked reference, not integrated) |
| `[[openclaw]]` | OpenClaw — deferred gateway/session adapter & UX candidate |
| `[[pageindex]]` | PageIndex — vectorless `DocumentEvidenceRetriever` (augment, not replace) |
| `[[mempalace]]` | MemPalace — advisory memory candidate (no truth authority) |
| `[[ob1]]` | OB1 (Open Brain) — optional cognitive-planning pattern, advisory only |
| `[[miro-stack]]` | The Miro Stack — MiroThinker / MiroFlow, deferred research/eval references |
| `[[solo-orchestrator]]` | Solo Orchestrator — single-orchestrator agent-execution reference |
| `[[graphify]]` | Graphify — graph-construction reference |
| `[[claw-code]]` | claw-code — agent-execution reference |
| `[[bitsandpieces]]` | bitsandpieces — landscape reference |

### Concept — recurring ideas, lenses, and proposals (13)

Cross-cutting philosophical and architectural concepts that recur across the arc
without being a single standing component — including the Searles thirteen-graphs
product horizon concepts and the node's-eye readings of the framework.

| Article | Entity |
|---|---|
| `[[thirteen-graphs]]` | Thirteen Graphs, One Infrastructure — one event graph, thirteen lenses (overview) |
| `[[the-market-graph]]` | The Market Graph — Layer 2, the exchange lens |
| `[[the-social-graph]]` | The Social Graph — Layer 3, the relationship-and-governance lens |
| `[[the-moral-ledger]]` | The Moral Ledger — the event graph reread as ethics at scale |
| `[[the-four-strategies]]` | The Four Strategies — the cognitive quartet (Agentic / Communal / Structural / Emergent) |
| `[[second-derivation-convergence]]` | The Second Derivation — primitives-up meets physics-up |
| `[[three-evaluative-axes]]` | Three Independent Evaluative Axes — how the framework is judged |
| `[[the-cult-test]]` | The Cult Test — the framework's self-falsifiability defences |
| `[[higher-order-operations]]` | Higher-Order Operations — operations on the cognitive grammar itself |
| `[[crash-recovery-as-ethics]]` | Crash Recovery as Ethics — integrity-under-failure as a moral property |
| `[[node-phenomenology]]` | What It's Like to Be a Node — the inside-view of an event-graph node |
| `[[religion-as-paths-from-being]]` | Six Paths from Being — religion in primitive terms |
| `[[offline-llm-optimization]]` | Offline LLM Optimization — long-arc strategic direction; results-per-external-dollar |

### Meta — the wiki writing about itself (1)

| Article | Entity |
|---|---|
| `[[civilization-wiki]]` | The Civilization Wiki — Karpathy-style LLM knowledge substrate; substrate before visualization |

---

## Deferred to later runs (not-yet-compiled)

Stated so the gaps are legible, per `DESIGN.md` and `PROVENANCE.md`. None of
these has an article yet; do not read their absence as absence from the project.

- **The full corpus sweep.** Per `DESIGN.md`, the substrate is meant to compile
  from ~8,783 markdown files across ~73 repos + ~1,175 Open Brain thoughts.
  Run-3 covered the arc spine, Searles philosophy, architecture entities, landscape
  survey, and the deferred long-tail — not the whole corpus.
- **Two `raw/` source tiers remain unmirrored** (`PROVENANCE.md`): `open_brain`
  (`raw/open-brain/` partially exported — 2026-06.md present; full dump not
  committed) and `upstream_context` (`raw/investigations/<project>/` is empty by
  design, Phase 2). Investigation-tier articles exist *despite* this — compiled
  from first-party survey, not from upstream mirrors.
- **Gate L.** The v4.0 companion gate to Gate K — defined as Event 2 (v3.9-to-v4.0
  reconciliation) in the Integration Arc — has no standalone article yet.
- **The Relationship Graph, Community Graph.** Deep-dive articles exist in the
  Searles corpus (Post 22 for Relationship, named in the series) but were not
  compiled in Run-3. The Population Graph article (compiled) covers Scheme A Layer
  9; the Relationship Graph article (Scheme B Layer 9) remains a legitimate
  forward-ref.
- **The `mind-zero` / `mind-zero-five` repo entity and the `eventgraph` repo.**
  The `[[mind-zero-five]]` article is now compiled but the repo-identity tension
  (mind-zero-five at `github.com/mattxo/mind-zero-five` vs.
  `transpara-ai/eventgraph` vs. `lovyou-ai/eventgraph`) remains unresolved. See
  `[[event-graph]]` and `[[the-lovyou-ai-fork]]`.
- **Remaining Open Brain history.** The 2026-06.md export covers June; prior
  months (Mar–May) are not in `raw/open-brain/`. A future run mirroring those
  months can deepen the operational record.
- **v16 fix-set implementation.** F1 (Reason-phase cwd), F2 (spec-diff gate at
  subtask creation), F3 (quiescence detector + `hive.run.completed`) are named in
  `[[slice-1-completion]]` as the candidate scope for the next fix set pending
  Gate-E or a new grant. Their articles are deferred until implementation.

---

*Compiled by Run-3 on 2026-06-14. Fail-legible: gaps are marked TBD, conflicts
are stated rather than resolved, and every `[[...]]` link above resolves to a real
file in `wiki/`. Re-run the compiler to refresh `last_compiled` and fold in the
deferred entities.*
