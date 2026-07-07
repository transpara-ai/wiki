---
entity: OB1 (Open Brain)
aliases:
  - OB1
  - Open Brain
  - OpenBrain
  - transpara-ai/OB1
tier: investigation
status: compiled
last_compiled: 2026-07-07
civilization_contribution: "Pattern-only; ADRs exist (ADR-0004 / ADR-0013, both Proposed, subsumed into accepted Decision 12/15); no new ADR. Contributes the reasoning-log / memory-of-intent pattern — advisory memory of *why*, separate from the EventGraph *transaction log* of truth — already realized as Transpara's internal Open Brain store, plus six mineable mechanisms (led by OB1's verifiable, fail-closed capture contract, the server-side form of the Civilization's own read-back durability rule). Code-anchored at transpara-ai/OB1 @ 1c4c906 (TAI-RES-2026-008): OB1 is a memory/recall substrate, not the 'cognitive planning' pattern the doctrine label calls it. Never truth, certification evidence, memory/knowledge authority, kernel, or controller (Decision 15)."
current_research_version: 1.0.0
sources:
  - "raw/civilization/external-landscape/tai-res-2026-008-ob1-evaluation.md"  # TAI-RES-2026-008 v1.0.0 — the code-anchored evaluation (this page's primary source); read transpara-ai/OB1 @ 1c4c906
  - https://github.com/NateBJones-Projects/OB1  # upstream; read via the Transpara fork transpara-ai/OB1 @ 1c4c9069fba06f82411005c77dafac8711805bdc (2026-06-17) — UPSTREAM CONTEXT ONLY, never re-published, never a push/PR target
  - /Transpara/transpara-ai/repos/OB1/README.md  # upstream README mirrored in the fork: "infrastructure layer for your thinking"; not-a-notes-app / pgvector + open protocol; FSL-1.1-MIT
  - /Transpara/transpara-ai/repos/OB1/CLAUDE.md  # "a persistent AI memory system"; remote-MCP / no-secrets / no-destructive-SQL guard rails
  - /Transpara/transpara-ai/repos/OB1/LICENSE.md  # FSL-1.1-MIT, "Copyright 2026 Nate B. Jones"; internal use permitted; two-year per-version MIT conversion
  - raw/transpara/dark-factory/v3.9/01-unified-architecture-decisions-v3.9.md  # DF-V3.9-ADR-001 (accepted, canonical): Decision 12 (01:140 "OpenBrain: optional cognitive planning pattern only"; 01:145 "MemPalace: recall substrate only") + Decision 15 (01:174 control-role exclusion)
  - raw/transpara/dark-factory/v3.9/implementation/epics/02-technology-decision-crosswalk-v3.9.md  # DF-V3.9-EPIC-TECH-CROSSWALK (status:review, canonical:false): "OpenBrain | pattern-only" row (:76) + advisory-only note (:131-135) + freeze/reopen policy (:43-58)
  - raw/transpara/dark-factory/v3.9/09-legacy-coverage-matrix-v3.9.md  # ADR-0004 (:78) / ADR-0013 (:107) OpenBrain planning-boundary entries; distinct PageIndex row (:252)
  - raw/transpara/dark-factory/v4.0/03-civilization-governance-and-authority-v4.0.md  # accepted v4.0: "EventGraph remains the source of truth… Memory and knowledge are advisory only" (03:36); external references/adapters only (03:158)
  - raw/transpara/dark-factory/v4.0/04-production-workflow-runtime-v4.0.md  # accepted v4.0: Release-only certification (04:195); external runtimes are references/adapters only (04:252); Base Slice 0 (04:220)
  - raw/transpara/dark-factory/v4.0/05-verification-audit-risk-eval-v4.0.md  # accepted v4.0: factory stops when "memory/knowledge contradicts EventGraph in high-risk planning" (05:523)
  - raw/transpara/dark-factory/research/pageindex-role-in-transpara-stack.md  # OB1 as cross-tool memory substrate; three-layer synthesis; "augmentation, not replacement"
  - Open Brain  # the running store (Supabase project njofekbuaauffxqsfikl, via mcp__open-brain__*): 2026-04-09 reasoning-log/transaction-log decision; 2026-06-13 upstream-merge (0c442a2) + open-brain-mcp redeploy; grounded fork chronology (GitHub createdAt 4/08)
confidence:
  upstream_identity: high — the fork's remotes name upstream NateBJones-Projects/OB1 with push disabled; LICENSE.md reads "Copyright 2026 Nate B. Jones"; README matches the theme verbatim.
  implementation_read: high — TAI-RES-2026-008 read the fork server (server/index.ts), the 6-tool MCP registry, the pgvector/HNSW schema and OpenRouter embedding path, PR #5/#6, license, and security posture at HEAD 1c4c906.
  crosswalk_decision: high — "pattern-only" is stated in accepted Decision 12 ("optional cognitive planning pattern only") and the v3.9.1 crosswalk row.
  cognitive_planning_label: contested-by-framing — Decision 12 files OB1 as "cognitive planning pattern," but the code, README, CLAUDE.md, PageIndex note, and v4.0's own usage all describe a memory/recall substrate; a repo-wide grep for "cognitive planning" returns zero. Both framings stated; neither silently picked.
  fork_divergence: resolved-negative — the fork carries NO Transpara feature or catalog divergence; its delta is entirely deployment/server-safety (PRs #1–#6 — local-Docker + k8s self-host, fingerprint-dedup, getEmbedding guards, verifiable/fail-closed capture — of which #5/#6 are the most substantive and the only ones after 2026-06-14). (Supersedes the prior page's unverified "agentic harnesses skill pack" note, which is upstream community content, not fork-added.)
  v4_0_status: OB1 is NOT restated in the accepted v4.0 core doctrine (01–07 grep = zero); the operative OpenBrain-specific decision is preserved v3.9 Decision 12/15 + the crosswalk, which v4.0 neither supersedes nor renames.
  license: high — FSL-1.1-MIT; internal use / modification / non-commercial research are Permitted Purposes; each version converts to MIT two years after its publication; the only bar is commercial Competing Use.
  fork_date: thin — 2026-04-08 rests on a GitHub-createdAt "grounded fork chronology" line, not on any contemporaneous thought. Plausible, weakly corroborated, not independently proven.
raw_documents:
  - "raw/civilization/external-landscape/tai-res-2026-008-ob1-evaluation.md"  # TAI-RES-2026-008 v1.0.0; session-authored Civilization external-landscape research, placed outside the browser-ingest inbox by design — provenance is git history + this frontmatter
---

# OB1 (Open Brain)

**OB1 — branded Open Brain — is the external memory-of-intent substrate the [[civilization-landscape-investigation]] surveyed and decided to learn from rather than depend on: a persistent AI-memory system by Nate B. Jones that Transpara forks, runs internally as its own advisory memory store, and gates out of every truth and control role.** TAI-RES-2026-008 (`raw/civilization/external-landscape/tai-res-2026-008-ob1-evaluation.md`) upgrades this page from a doc/decision-anchored stub to a **code-anchored** assessment of the fork `transpara-ai/OB1` @ `1c4c906` (2026-06-17), and lands the explicit ADR/contribution verdict. The conclusion is stable and narrow, and now code-confirmed: **OB1 is the reasoning log — memory of intent — never the transaction log of truth.**

> **Findings — TAI-RES-2026-008 (code-anchored @ `transpara-ai/OB1` HEAD `1c4c906`, 2026-06-17).** OB1 is a persistent AI-**memory** substrate — Supabase + `pgvector`, a **six-tool** remote MCP Edge Function (Deno/TypeScript, per-request server), API-based embeddings — **not a planner**. That confirms the artifact and contradicts the doctrine's *"cognitive planning"* label (a `grep "cognitive planning"` over the whole repo returns zero). The **pattern-only** verdict holds and hardens: no upstream code enters any Civilization control plane (Decision 12/15; accepted v4.0 `03:36`, *"memory and knowledge are advisory only"*). What *is* in use is the **reasoning-log pattern** — Transpara runs the forked code as its own internal Open Brain store: advisory memory of *intent*, explicitly separate from the EventGraph *transaction log* of truth. The verdict is unchanged since the 2026-06-14 page; the *evidence* is new — plus **PR #6** (hardening PR #5's verifiable, fail-closed `capture_thought`) and the resolution that the fork carries **no Transpara feature divergence**, only server/deployment safety patches.
>
> **Material links —**
> **Adopted** (the *pattern* + running the forked code internally as advisory tooling; FSL-permitted, never a control role): [[event-graph]] transaction-log-vs-reasoning-log split (2026-04-09) · the internal Open Brain store (`njofekbuaauffxqsfikl`) · accepted v4.0 *"advisory-memory hygiene"* (doc `03`).
> **Reference-only** (cited, never imported, never a dependency or controller): upstream [`NateBJones-Projects/OB1`](https://github.com/NateBJones-Projects/OB1) · TAI-RES-2026-008 · Decision 12 / Decision 15 / the v3.9.1 crosswalk · ADR-0004 / ADR-0013 · [[pageindex]] · [[mempalace]] · [[civilization-landscape-investigation]].

This article is about **Transpara's investigation and decision**, not a re-publication of OB1's own documentation. OB1 is upstream public code; it is cited here as context only, and its large community catalog (curated extensions, recipes, skills, dashboards, integrations) is characterized, never reproduced.

## What changed with TAI-RES-2026-008

The earlier page carried upstream and doc claims as context because it was compiled without a dedicated code read. The current evaluation read the fork repository at `1c4c906` and replaces that with code-anchored findings:

| Area | Prior page (doc/decision-anchored) | Updated finding (code-anchored, `1c4c906`) |
|---|---|---|
| What it is | "a memory system, not a notes app" (README) | Confirmed at code level: Supabase + `pgvector` `thoughts` store; a **6-tool** remote MCP Edge Function (Deno/TS, per-request `McpServer`), `search`/`fetch`/`search_thoughts`/`list_thoughts`/`thought_stats`/`capture_thought` (`server/index.ts:122`…`:452`) |
| Retrieval / storage | README-level "vector search" | `vector(1536)`, **HNSW cosine**, SHA-256 `content_fingerprint` dedup, `match_thoughts`/`upsert_thought` RPCs; embeddings **API-based** (OpenRouter `text-embedding-3-small`) — *inverse of MemPalace's local-first* |
| Fork divergence | "not established… maybe an agentic-harnesses skill pack (PR #151)" | **Resolved: no Transpara feature/catalog divergence.** The skill pack is *upstream* community content; the fork's delta is entirely deployment/server-safety (PRs #1–#6 — local-Docker + k8s self-host, dedup, getEmbedding guards, verifiable capture). `git ls-files \| grep transpara` = 0 |
| Since 06-14 | (page predates it) | **PR #6** (`1c4c906`): `deno check` resolution + empty-embedding-error guard, hardening PR #5's verifiable + fail-closed `capture_thought` ("committed but no id ⇒ treat as NOT saved") |
| Doctrine currency | v3.9 only | Baselined against accepted **v4.0**; OB1 is **not restated in v4.0** (appears only as "advisory-memory hygiene") — v3.9 Decision 12/15 remain the operative OB1-specific statement |
| License | "FSL — no commercial derivative works" | Precise: internal use / modification / non-commercial research **permitted**; only commercial *Competing Use* barred; each version → **MIT two years after publication** (`LICENSE.md:87-92`) |

The result is not "adopt OB1." The result is: OB1 is a credible memory-of-intent substrate whose *pattern* the Civilization already runs internally — advisory-only, wrapped in its own trust and truth boundary.

## What OB1 is — now code-anchored

`CLAUDE.md:7`: *"Open Brain is a persistent AI memory system — one database (Supabase + pgvector), one MCP protocol, any AI client."* The runtime is a **Deno/TypeScript Supabase Edge Function** built **per request** (`buildServer()` at `server/index.ts:114`, invoked inside `app.all("*")` at `:640`), remote-over-HTTP by hard guard rail (*"MCP servers must be remote… Never use `StdioServerTransport`"*, `CLAUDE.md:75`). It registers **six tools**, one of them (`capture_thought`, `:452`) the sole writer, annotated `readOnlyHint:false`. Storage is a `thoughts` table with `pgvector` HNSW cosine search and a unique `content_fingerprint` index for dedup; embeddings are **API-based** (`openai/text-embedding-3-small` via OpenRouter, 1536 dims), the inverse of MemPalace's local-ONNX posture and a collision with the air-gap default. It is, unambiguously, a memory/recall substrate — the repository never self-describes as a planner.

## The decision: pattern-only

The accepted-canonical statement is **v3.9 Decision 12, "External Patterns Are References, Not Controllers"** (`raw/transpara/dark-factory/v3.9/01-unified-architecture-decisions-v3.9.md:140`):

> OpenBrain: optional cognitive planning pattern only.

The per-item **v3.9.1 crosswalk** row says the same and adds the boundary (`02-technology-decision-crosswalk-v3.9.md:76`, `:131-135`): integration mode "optional cognitive planning pattern," owning epic **none**, risk *"vague pattern can become cargo-cult architecture,"* and the rule that *"any cognitive planning patterns must remain advisory and cannot replace `PlanningProposal`, `Requirement`, `AcceptanceCriterion`, or EventGraph evidence."* Pattern-only means **no code import and no automatic upstream tracking** — frozen at the v3.9 reference point unless an epic explicitly reopens it (named triggers: upstream design change, eval regression, capability evolution, reviewer marks it stale, or a security/licensing/governance change). Under **Decision 15** (`01:174`) OB1, like every surveyed framework, *"must not become kernel, truth source, Work replacement, policy owner, release authority, certification authority, capability promoter, factory controller, or Site replacement."* The legacy coverage matrix records two ADR handles — **ADR-0004 "OpenBrain planning boundary"** (`09:78`) and **ADR-0013 "OpenBrain optional pattern"** (`09:107`), both archived **Status: Proposed** and ratified transitively through Decision 12.

**v4.0 carry-forward (fail-legible).** The accepted v4.0 doctrine set neither supersedes `DF-V3.9-ADR-001` nor restates OpenBrain: a repo-wide grep of the v4.0 core docs (`01–07`) for `openbrain|ob1|cognitive planning` returns **zero**. OB1 survives in v4.0 only as operational *"advisory-memory hygiene"* in the dev loop, and the external-framework *principle* is carried forward generically (*"external policy engines / runtimes are references or adapters only,"* `03:158`, `04:252`). So OB1's operative, named decision is the **preserved v3.9 Decision 12/15**, un-superseded — the same "v4.0 carry-forward gap" shape the [[pageindex]] evaluation recorded for `DocumentEvidenceRetriever`.

## The "cognitive planning" label vs the memory-substrate artifact (stated, not resolved)

> ⚠ **Fail-legible note (label vs. substance).** Decision 12 files OB1 as an *"optional cognitive planning pattern,"* a label inherited from the 2026-05 ADR-0004/0013 era. But the code, `README.md`, `CLAUDE.md`, the first-party PageIndex note (*"OpenBrain = persistent agent-readable memory substrate"*), and even v4.0's own usage all describe a **memory/recall substrate**, not a planner — and a repo-wide `grep "cognitive planning"` returns **zero**. In the *same* Decision 12 list, the *"recall substrate only"* slot is explicitly reserved for **MemPalace** (`01:145`). So OB1 is filed under a category that mismatches its function and collides with a sibling's reserved slot. Why is **not explained in any source**; it is an asserted classification, not a justified one. Either way the *boundary* is identical and load-bearing — advisory only, never `PlanningProposal`/`Requirement`/`AcceptanceCriterion`/EventGraph evidence, never a controller. TAI-RES-2026-008 §5.5 recommends a docs-hygiene reconciliation of the label; the boundary needs none.

## The boundary

The governing boundary is the accepted memory/knowledge law: *"EventGraph remains the source of truth… Memory and knowledge are advisory only"* (v4.0 `03:36`), and the factory must **stop** when *"memory/knowledge contradicts EventGraph in high-risk planning"* (v4.0 `05:523`). OB1 itself does none of this: it is deliberately fail-open recall — store verbatim content, search it, return the nearest thoughts, with a `metadata jsonb` blob that carries no trust, freshness, or contradiction state. That is correct at the recall layer and wrong at the authority layer. The Civilization boundary supplies the missing governance — recalled content enters as advisory, becomes usable in gated work only as a `MemoryReference`, and can never quietly influence high-risk planning. OB1's *own* in-house framing already draws this line: the EventGraph is *"a ledger of what happened,"* while Open Brain *"captures what the agent was thinking and why"* (2026-04-09 hive reboot-survival decision).

## Adopted vs. reference — two objects, one boundary

OB1 is the purest pattern-only case in the series, and the "adopted vs. reference" question turns on keeping **two objects distinct**:

- **The upstream repository (`NateBJones-Projects/OB1`)** — *reference only*. Cited as context, never imported into any Civilization component, never a dependency, controller, or truth store (Decision 12/15). This is the object the investigation *surveyed*.
- **The reasoning-log pattern, realized as Transpara's internal Open Brain store** — *adopted, advisory-only*. The pattern (memory of intent, separate from the truth ledger) is already in use, and Transpara runs the *forked code* as the deployed `open-brain-mcp` store — which the FSL-1.1-MIT license permits for internal use. This is an **operational** adoption of advisory tooling, **not** a doctrine adoption into a control role: pattern-only governs the architecture question; running it internally is a permitted, doctrine-neutral choice.

The two share code but are different objects, and this article keeps them so: the repo is the *thing surveyed*; the running store is a *source* and the *realization of the borrowed pattern*.

## Where OB1 sits relative to neighbours

The first-party PageIndex study positions OB1 against adjacent tools as **complementary layers, not competitors** (`pageindex-role-in-transpara-stack.md`):

```
OpenBrain = persistent agent-readable memory substrate
LLM Wiki  = compiled/synthesized knowledge artifact
PageIndex = reasoning-based retrieval over long source documents
```

[[pageindex|PageIndex]] *augments, not replaces* OB1 — it can sit *under* the memory substrate as a document-evidence primitive. [[mempalace|MemPalace]] is the closest sibling: both are advisory memory candidates governed by the same Decision 12 pass, but MemPalace is filed (correctly) as *"recall substrate only"* with a `MemoryReference` mapping and a local-first embedding path, while OB1 is filed (mismatched) as "cognitive planning" and ships an API embedding path.

## Fork status and the upstream boundary

The fork is a real, maintained mirror, not an import:

- `git remote -v`: **`origin` = `transpara-ai/OB1`** (the fork the org owns), **`upstream` = `NateBJones-Projects/OB1`** with the push URL set to the sentinel **`DISABLE_PUSH_TO_UPSTREAM`** — upstream pushes mechanically blocked.
- On **2026-06-13**, Codex merged upstream main into `transpara-ai/OB1` main (merge-preserve, backup branch first, merge commit `0c442a2`, 5 Transpara-only commits) and redeployed the Supabase `open-brain-mcp` Edge Function on project `njofekbuaauffxqsfikl`; an MCP smoke test confirmed the six tools and the write path.
- **PR #5 (`1d1d6e2`, 2026-06-14)** made `capture_thought` verifiable and embedding-failure-safe — a fail-closed contract (*committed-but-no-id ⇒ "treat as NOT saved"*), moving the durability guarantee server-side. **PR #6 (`1c4c906`, 2026-06-17)** cleaned `deno check` resolution and guarded an empty embedding-error message. PR #5/#6 are the most substantive of the fork's Transpara commits and the only ones after 2026-06-14; the rest (PRs #1–#4, plus a self-host recipe and key-rotation docs) are deployment/server-safety only — **no feature or catalog divergence**.

> ⚠ **Fail-legible note (fork date is thin).** "Forked into transpara-ai on 2026-04-08" rests on a single *"grounded fork chronology"* line (GitHub `createdAt`: "4/08 OB1 ← NateBJones-Projects"), not on any contemporaneous thought. Plausible and weakly corroborated (Apr-8 working-tree timestamps; a same-day restructuring of the *separate* `open-brain` monorepo), not independently proven.

## What is thin or absent

- **Fork divergence — now resolved (negative).** The prior page's open question ("does the fork carry Transpara-specific commits?") is answered: **no feature divergence.** The fork's delta is entirely deployment/server-safety (PRs #1–#6 — local-Docker + k8s self-host, fingerprint-dedup, getEmbedding guards, verifiable/fail-closed capture); the "agentic harnesses skill pack (PR #151)" a 2026-04 thought attributed to the fork is **upstream community content** (`skills/n-agentic-harnesses`, by an upstream contributor), and PR #151 is an upstream number (the fork's PRs run #1–#6) — the code read supersedes that thought.
- **Identity binding** — the crosswalk/Decision-12 rows name only *"OpenBrain"*; the binding OpenBrain = OB1 = `transpara-ai/OB1` (Nate B. Jones) is asserted by the landscape article and the PageIndex note, not by the decision cell itself.
- **Why "cognitive planning" and not "recall substrate"** — unexplained in sources (the label mismatch above).
- **Crosswalk status** — the OpenBrain row lives in a `status: review`, `canonical: false` doc; the accepted, canonical statements are Decision 12/15 and the coverage matrix.

## Cross-links

- [[civilization-landscape-investigation]] — the 2026-05-13 survey that produced the pattern-only verdict; names OB1 in its memory/knowledge batch.
- [[event-graph]] — the sovereign truth ledger (transaction log) OB1's memory (reasoning log) is explicitly *not* allowed to become or supersede.
- [[mempalace]] — the sibling advisory memory candidate, filed as "recall substrate only" with a `MemoryReference` mapping.
- [[pageindex]] — the memory-cluster neighbour; a document-evidence primitive that augments, not replaces, OB1.
- [[dark-factory]] — the architecture whose boundary the decision defends.
- [[v3-9]] — the canonical revision that folded the investigation's decisions in; [[v4-0]] carries the principle forward generically.

## Sources & provenance

Primary source is the code-anchored evaluation; doctrine is first-party Transpara documents; upstream is cited as context only.

- `raw/civilization/external-landscape/tai-res-2026-008-ob1-evaluation.md` — **TAI-RES-2026-008 v1.0.0**, the code-anchored evaluation of `transpara-ai/OB1` @ `1c4c906`. This page is its digest; the evaluation carries the full `file:line` anchors, the v4.0/v3.9 doctrine map, and the §4.4 determination.
- **Adopted (pattern + internal tooling, advisory-only):** the 2026-04-09 reasoning-log/transaction-log hive decision; the running **Open Brain** store (`njofekbuaauffxqsfikl`, via `mcp__open-brain__*`); accepted v4.0 doc `03` ("memory and knowledge are advisory only").
- **Reference-only (cited, never imported):** upstream `NateBJones-Projects/OB1` (`README.md`, `CLAUDE.md`, `LICENSE.md`); Decision 12 (`01:140`) + Decision 15 (`01:174`) in `DF-V3.9-ADR-001`; the v3.9.1 crosswalk OpenBrain row/note; ADR-0004 (`09:78`) / ADR-0013 (`09:107`); the PageIndex study (`pageindex-role-in-transpara-stack.md`).

**Conflicts and thin spots stated, not resolved.** (1) *Label vs. substance*: doctrine files OB1 as "cognitive planning," the artifact is a memory substrate, and Decision 12 reserves "recall substrate" for MemPalace — flagged, not papered over. (2) *Identity binding*: the decision rows name only "OpenBrain." (3) *Fork date*: 2026-04-08 rests on GitHub `createdAt`, not a contemporaneous thought. (4) *Crosswalk status*: the per-item detail is `status: review`; the ratified part is Decision 12/15. (5) *v4.0*: OB1 is not restated in accepted v4.0; the operative decision is preserved v3.9. `[[wikilinks]]` are forward references; some targets may not be compiled yet. The correct status: credible advisory memory-of-intent pattern; ADRs exist (Proposed, subsumed); no new ADR; no authority; no runtime activation; internal operational use is FSL-permitted and doctrine-neutral.
