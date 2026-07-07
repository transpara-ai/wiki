---
document_id: TAI-RES-2026-008
title: OB1 / Open Brain Capability Evaluation (Nate B. Jones — Persistent AI-Memory Substrate)
subtitle: Code-Anchored Re-Evaluation Against the Transpara-AI Civilization Memory/Knowledge Boundary, and Strategic Learning Opportunities
version: 1.0.0
status: RELEASED
date: 2026-07-07
author: Michael Saucier
reviewer: Transpara AI Hive
owner: Research & Strategic Intelligence
org: Transpara AI
repo: transpara-ai/wiki
classification: PUBLIC — external-landscape research (this repo is public; no secrets; only public upstream/fork code and already-published Civilization doctrine are quoted at the same depth as the prior TAI-RES evaluations; the upstream `NateBJones-Projects/OB1` is cited as context and is never re-published, never a push/PR target)
companion_to: TAI-RES-2026-001 (Sakana AI), TAI-RES-2026-002 (Hermes Agent & Self-Evolution), TAI-RES-2026-003 (Google Open Knowledge Format), TAI-RES-2026-004 (MemPalace), TAI-RES-2026-005 (Solo Orchestrator), TAI-RES-2026-006 (Owain Lewis Work System), TAI-RES-2026-007 (PageIndex)
supersedes_for_presentation: wiki/ob1.md  # the 2026-06-14 doc/decision-anchored compile; retained in git history, superseded for the "what it is" facts by the code-anchored read below
evaluated_artifact: https://github.com/NateBJones-Projects/OB1  # upstream; read via the Transpara fork transpara-ai/OB1 @ HEAD 1c4c9069fba06f82411005c77dafac8711805bdc (2026-06-17, PR #6), a mirror of upstream + four Transpara server/deployment safety commits
---

## Revision History

| Version | Date | Description | Author |
|---|---|---|---|
| 1.0.0 | 2026-07-07 | Initial release — first **code-anchored** evaluation of OB1 / Open Brain (`NateBJones-Projects/OB1`, read via the Transpara fork `transpara-ai/OB1` @ `1c4c906`, 2026-06-17). Upgrades the 2026-06-14 `wiki/ob1.md` (which was doc- and decision-anchored, with no dedicated eval) to a repository-anchored assessment of the runtime server, the 6-tool MCP surface, the storage/embedding path, the two Transpara hardening PRs (#5/#6), license, security posture, and supply chain. Capability comparison against the accepted **v4.0** doctrine baseline, with preserved **v3.9** supplying the operative OpenBrain decision (Decision 12/15 + the crosswalk row). Includes the §4.4 decision-record determination (ADRs exist — ADR-0004/ADR-0013, subsumed into accepted Decision 12/15; none created now; **pattern-only** contribution) and six strategic learning opportunities plus the inverse analysis. | M. Saucier / Hive |

---

## Abstract

This document re-evaluates **OB1 — branded "Open Brain"** — the public open-source project by **Nate B. Jones** (`NateBJones-Projects/OB1`) that describes itself as *"the infrastructure layer for your thinking. One database, one AI gateway, one chat channel"* [2]. It is the eighth in the external-landscape evaluation series [21], and the third (after MemPalace [21] and PageIndex [21]) to take a candidate that already had a compiled wiki page and **upgrade it from a doc/decision-anchored stub to a code-anchored assessment** by reading the actual repository — the Transpara fork `transpara-ai/OB1` @ HEAD `1c4c906` (2026-06-17), a mirror of upstream plus four Transpara server/deployment safety commits [1][6]. The Civilization baseline is the accepted **v4.0** doctrine set [13–19]; the operative OpenBrain-specific decision is preserved **v3.9** Decision 12/15 and the technology-decision crosswalk, which v4.0 neither supersedes nor restates [8][9].

The central finding is that **the 2026-05-13 investigation's disposition — pattern-only — was correct, holds under the code, and hardens; and the code contradicts the doctrine's own label for OB1.** OB1 is, at the code level, a **persistent AI-memory substrate**: one Postgres database (Supabase + `pgvector`), a single remote **MCP server** exposing **six tools** (`search`, `fetch`, `search_thoughts`, `list_thoughts`, `thought_stats`, `capture_thought` — `server/index.ts:122`, `:170`, `:224`, `:302`, `:378`, `:452`), deployed as a Deno/TypeScript Supabase Edge Function, remote over HTTP and explicitly never local stdio [1][2]. It is a memory-and-recall system, not a planner — a `grep "cognitive planning"` over the entire repository returns **zero matches** — yet accepted v3.9 Decision 12 files OB1 as *"optional cognitive planning pattern only"* while, in the same list, reserving *"recall substrate only"* for MemPalace [8]. The label predates the artifact; the boundary it draws is nonetheless correct.

That boundary is the load-bearing part, and it is identical across every doctrine layer: OB1 is **advisory only, never a controller**. Under Decision 15 it *"must not become kernel, truth source, Work replacement, policy owner, release authority, certification authority, capability promoter, factory controller, or Site replacement"* [8], and the crosswalk's per-item rule is that *"any cognitive planning patterns must remain advisory and cannot replace PlanningProposal, Requirement, AcceptanceCriterion, or EventGraph evidence"* [9]. Accepted v4.0 states the same law generically — *"Memory and knowledge are advisory only"* (doc `03:36`) atop *"EventGraph remains the source of truth"* — and adds the stop condition: the factory must halt when *"memory/knowledge contradicts EventGraph in high-risk planning"* (doc `05:523`) [15][17].

Two facts frame the "adopted vs. reference" question, and they are subtler for OB1 than for any sibling. First, **the pattern is already in use** — not imported from the repo, but realized as Transpara's *own* internal Open Brain store: the 2026-04-09 hive reboot-survival decision made the EventGraph the *transaction log* ("a ledger of what happened") and Open Brain the *reasoning log* ("what the agent was thinking and why"), so agents recover **intent** on reboot without replaying raw events [20]. Second, **Transpara runs the forked code** as that store (the deployed `open-brain-mcp` Edge Function), which the FSL-1.1-MIT license permits for internal use [3][20]. Neither fact is a doctrine "adoption": pattern-only governs the *architecture* question (OB1 never becomes a Civilization control-plane component), while running it internally as advisory tooling is a permitted operational choice, not a control role.

The one-line result: **OB1 is the reasoning log — memory of intent — never the transaction log of truth.** §4.4 records the determination (ADRs exist as ADR-0004/ADR-0013, both Proposed and subsumed into accepted Decision 12/15; no new ADR; pattern-only), and the evaluation surfaces two documented doctrine-hygiene items: OB1 is not restated in accepted v4.0 (it survives there only as *"advisory-memory hygiene"* in the dev loop), and its Decision-12 "cognitive planning" label mismatches both the artifact and MemPalace's reserved "recall substrate" slot. Six learning opportunities follow — all pattern-only, none importing OB1's code as runtime, gate authority, or truth store — led by OB1's own **verifiable, fail-closed capture contract** (PR #5), which is the server-side implementation of the exact "capture is confirmed only by read-back" durability rule the Civilization already runs on.

---

## 1. Introduction and Scope

This evaluation was commissioned to **re-evaluate OB1 / Open Brain in the same manner as MemPalace** (TAI-RES-2026-004) — i.e., to replace the earlier page's doc- and decision-anchored characterization with a code-anchored read of the repository, land the explicit §4.4 decision-record determination, and re-compile the wiki page — consistent with the ratified rule that external frameworks stay outside control roles [8][22].

The evaluation covers:

- **The runtime server** — `transpara-ai/OB1` @ `1c4c906`: `server/index.ts` (the MCP server, per-request `McpServer`, the 6-tool registry, auth, CORS), `server/capture-response.mjs` (the capture contract), `server/deno.json` / `package.json` (dependency pinning), read as ground truth [1].
- **The storage and retrieval path** — the canonical `thoughts` schema mirrored in `integrations/local-docker/db-init/01-schema.sql` and `docs/01-getting-started.md`: `pgvector`, HNSW cosine index, `content_fingerprint` dedup, the `match_thoughts` / `upsert_thought` RPCs, and the OpenRouter embedding path [1][4].
- **The two Transpara hardening PRs** — PR #5 (`1d1d6e2`, verifiable + embedding-failure-safe `capture_thought`) and PR #6 (`1c4c906`, `deno check` resolution + empty-error guard), the fork's only substantive divergence from upstream [1][6].
- **License, security, and supply chain** — `LICENSE.md` (FSL-1.1-MIT), `SECURITY.md`, `AGENTS.md`, `.gitignore`, and the community-contribution posture [2][3][5].
- **The Civilization v4.0 baseline** — the accepted memory/knowledge boundary (doc `03:36`, `05:523`), the external-framework law (Decision 15; v4.0 `03:158`, `04:252`), and Base Slice 0 (`04:220`), plus the operative preserved-v3.9 OpenBrain decision (Decision 12; the crosswalk row and per-item note) [8][9][13–19].

**Evidence base and source discipline.** Per the standing rule that *code is ground truth while READMEs and marketing may be aspirational*, every claim about OB1's server, storage, and capture path is **code-anchored** with `file:line` provenance [1][4]. Upstream identity, community-contribution, and maturity claims are **repo-metadata- or README-cited** and carried at appropriate confidence [2][7]. The Civilization side is **doctrine-anchored**: quotes come from the accepted v4.0 docs and the preserved-v3.9 Decision 12/15 + crosswalk, distinguishing accepted-canonical law (Decision 12/15, coverage matrix) from the `status: review` crosswalk that elaborates it [8][9][13–19]. One deliberate distinction runs throughout: **"OB1 the upstream repository" (the artifact surveyed) is kept separate from "Open Brain the running internal store" (a source, and the realization of the borrowed pattern)** — they share code, but they are different objects and are treated as such [1][20].

---

## 2. OB1 / Open Brain: Capability Overview

### 2.1 The Author and Project Surface (third-party-cited)

OB1 is authored by **Nate B. Jones** (`LICENSE.md:9`, "Copyright 2026 Nate B. Jones"; `README.md:197`), with a listed repo team (Jonathan Edwards, Matt Hallett, Alan Shurafa) and a Discord community [2]. It is a **large, sprawling, community-driven catalog** — ~916 tracked files, ~20 named contributors — organized as curated `extensions/` (household-knowledge, professional-CRM, job-hunt), community `recipes/` (importers, dedup/provenance, "life-engine" digests), `skills/`, `dashboards/`, `integrations/` (Slack/Discord/Telegram capture), `primitives/`, and SQL `schemas/` sidecars, each directory carrying a `_template/` and `README.md` contribution framework [2]. This breadth is context, not the subject: the load-bearing runtime is the single MCP server in `server/`. **None of the community catalog is re-published here**; it is named only to characterize the kind of project the investigation judged.

### 2.2 What OB1 Is — a Persistent Memory Substrate (code-anchored)

`CLAUDE.md:7`: *"Open Brain is a persistent AI memory system — one database (Supabase + pgvector), one MCP protocol, any AI client."* `README.md:9`: *"This isn't a notes app. It's a database with vector search and an open protocol — built so that every AI tool you use shares the same persistent memory of you."* The functional identity is unambiguous and consistent across every artifact: a **cross-tool, agent-readable memory/recall substrate** — the same characterization the first-party PageIndex study reached (*"OpenBrain = persistent agent-readable memory substrate"*) [11]. The repository never self-describes as a planner.

### 2.3 The Runtime — a Per-Request Remote MCP Edge Function (code-anchored)

The server is **Deno/TypeScript**, deployed as a **Supabase Edge Function**: `server/index.ts:1` imports `jsr:@supabase/functions-js/edge-runtime.d.ts`; the entrypoint is `Deno.serve(app.fetch)` (`server/index.ts:650`); the web framework is **Hono** with `@hono/mcp`'s `StreamableHTTPTransport` [1]. A fresh `McpServer` is built **per HTTP request** — `buildServer()` (`server/index.ts:114`) is invoked inside the `app.all("*")` handler (`:640`), not once at boot — the "per-request MCP" pattern that stabilizes connections for strict MCP hosts [1]. Remote-over-HTTP is a hard guard rail, not a default: `CLAUDE.md:75` — *"MCP servers must be remote (Supabase Edge Functions), not local. Never use `claude_desktop_config.json`, `StdioServerTransport`, or local Node.js servers."* README echoes it: *"No middleware, no SaaS chains, no Zapier"* (`README.md:7`).

### 2.4 The MCP Surface — Six Tools, One Writer (code-anchored)

The core server registers exactly **six tools** via `server.registerTool(...)` [1] — confirming the prior page's count:

| # | Tool | `server/index.ts` | `readOnlyHint` |
|---|------|---|---|
| 1 | `search` | `:122` | true (ChatGPT-connector shape) |
| 2 | `fetch` | `:170` | true (ChatGPT-connector shape) |
| 3 | `search_thoughts` | `:224` | true |
| 4 | `list_thoughts` | `:302` | true |
| 5 | `thought_stats` | `:378` | true |
| 6 | `capture_thought` | `:452` | **false** (the only writer) |

`search`/`fetch` exist specifically for ChatGPT-connector compatibility (`server/index.ts:120-121`); `capture_thought` is the sole mutating tool, annotated `readOnlyHint:false, destructiveHint:false, idempotentHint:false` (`:459-462`). Repo `schemas/` sidecars (`typed-reasoning-edges/`, `provenance-chains/`) point toward a knowledge-graph *extension* over the same `thoughts` base, but they extend — never replace — the six-tool substrate.

### 2.5 Storage & Retrieval — pgvector, HNSW, Fingerprint Dedup, API Embeddings (code-anchored)

The canonical schema is mirrored verbatim in `integrations/local-docker/db-init/01-schema.sql` (self-declared as mirroring the Supabase schema) [4]:

- **`thoughts` table** (`01-schema.sql:14-22`): `id uuid PK`, `content text`, `embedding vector(1536)`, `metadata jsonb`, `content_fingerprint text`, `created_at`/`updated_at`.
- **pgvector + HNSW**: `CREATE EXTENSION vector`; `idx_thoughts_embedding_hnsw ... USING hnsw (embedding vector_cosine_ops)` (`:24-25`); a **unique partial index** on `content_fingerprint` for dedup (`:27-35`).
- **Retrieval RPC** `match_thoughts(...)` returns cosine similarity `1 - (embedding <=> query_embedding)` (`:55-84`); **write RPC** `upsert_thought(...)` computes a **DB-side SHA-256 fingerprint** of normalized content and `ON CONFLICT (content_fingerprint) DO UPDATE` merges metadata (`:88-111`).
- **Embeddings are API-based, not local**: `openai/text-embedding-3-small` via **OpenRouter**, **1536 dims** (`server/index.ts:58-60`; `docs/01-getting-started.md`); metadata extraction uses `openai/gpt-4o-mini` (`server/index.ts:87-98`). This is the **inverse of MemPalace's local-first ONNX posture** [21] and, like PageIndex's litellm dependency [21], collides with the air-gap default — any Civilization use would have to vendor a local embedding path.

### 2.6 The Two Transpara Hardening PRs (code-anchored)

The fork's *entire* substantive divergence from upstream is four files across two PRs [1][6]:

- **PR #5 (`1d1d6e2`, merged 2026-06-14) — verifiable + embedding-failure-safe `capture_thought`.** The row is inserted by `upsert_thought` *before* the embedding is attached; the old code returned an error for an already-saved thought (causing retry/duplication). The new capture contract (`capture-response.mjs:15-74`, priority-ordered) is **fail-closed**: (1) upsert error → error; (2) committed **but no id** → error *"Capture unconfirmed… Treat as NOT saved"* (`:46-54`); (3) committed + embed failed → **success**, `embedding: pending` (not an error — avoids duplicate-creating retries); (4) committed + embed ok → success `embedding: ready`. Success text now embeds the committed id + status so a client can confirm with `fetch(id)` (`:61`), and a non-string id collapses to `undefined` → the fail-closed branch (`server/index.ts:484-485`). The response shaping is a pure, infra-free module unit-tested by `test-capture-response.mjs`.
- **PR #6 (`1c4c906`, 2026-06-17) — `deno check` resolution + empty-error guard.** `deno.json` adds `"nodeModulesDir": "none"` so local `deno check` resolves deps deploy-identically (a false `TS2345` was arising from the Node test harness's `package.json`); and `capture-response.mjs:71` guards `${embError.message || "unknown error"}` so an empty message no longer renders *"the embedding update failed ()"*. A unit case was added.

Both commits are co-authored "Claude Opus 4.8"; **PR #6 is the only change to land after the 2026-06-14 page** (PR #5 predates it by a day). The pair is notable beyond its size: it moves OB1's durability guarantee **server-side**, which is exactly the durability gap the Civilization's *"capture is confirmed only by read-back"* rule was written to compensate for on the client (§5.2).

### 2.7 Security, License, and Supply Chain (code-anchored + repo-metadata)

- **No hardcoded secrets.** The four sensitive vars (`SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `OPENROUTER_API_KEY`, `MCP_ACCESS_KEY`) are read via `Deno.env.get(...)` with **no fallback**, non-null-asserted so a missing var fails fast (`server/index.ts:13-16`) — the fail-closed secret posture the Civilization requires [5].
- **Auth = single shared key, fail-closed.** `app.all("*")` requires `x-brain-key`/`?key=` to equal `MCP_ACCESS_KEY`; a mismatch is rejected as a JSON-RPC error envelope at HTTP 200 (deliberately not a bare 401, which strict MCP hosts treat as a transport tear-down) (`server/index.ts:610-622`, `:531-537`). **CORS is wildcard-origin *without* credentials** (`:521`) — auth rides a bearer-style key, not cookies, so the "wildcard-with-credentials" anti-pattern is **not** present (a `?key=` in the URL can, however, leak via logs — a residual trade-off).
- **License: FSL-1.1-MIT** (`LICENSE.md`) [3]. Internal use, modification, and non-commercial research are **Permitted Purposes** (`:43-52`); the only bar is a **Competing Use** — re-offering OB1 (or a substantially-similar memory service) as a commercial product (`:32-41`). Each version converts to **MIT two years after its publication** (`:87-92`) — the HEAD version on ~2028-06-17. So Transpara's internal use and modification are squarely permitted; commercial re-offering is the prohibited case.
- **Supply chain & maturity.** Upstream is community-driven behind an automated PR gate + human review (`README.md:186-188`; `CLAUDE.md:82`); the **core server version is still `1.0.0`** (`server/index.ts:117`) atop a large docs/recipes catalog — most repo mass is content, not hardened server code. Two verifiable hygiene gaps for any adopter: (1) the committed `.gitignore` matches `.env*` but **not the project's own `.openbrain.env` secret-file convention** (`.gitignore:16-18`), so that protection does not propagate to a fresh clone; (2) runtime deps are pinned exactly in `server/deno.json`, but `deno.lock` is git-ignored and the Node test harness has no lockfile — lockfile-level reproducibility is absent. `SECURITY.md` scopes to repo contents, **explicitly excludes the running infra** (`:16-17`), and leaves the contact email an unfilled `TODO` (`:7`). `AGENTS.md:58-61` bakes creator-branding into agent instructions (point public assets to the author's channels) — a maturity/branding-coupling signal, not a defect.

---

## 3. Transpara-AI Civilization: The Memory/Knowledge Baseline (v4.0 accepted + operative v3.9)

### 3.1 The primitive OB1's pattern maps to

The Civilization already has a governed home for advisory memory. Accepted v4.0 states the law plainly: *"EventGraph remains the source of truth for evidence, authority, release, and capability state… Memory and knowledge are advisory only"* (doc `03:36`) [15]. The sibling MemPalace evaluation maps advisory recall to a `MemoryReference` boundary carrying source, hash, retrieval time, trust, freshness, and contradiction refs [21]; OB1's pattern is the **memory-of-intent** case of that same regime — the *reasoning log* the hive design separated from the EventGraph *transaction log* [20].

### 3.2 The truth / certification boundary

Only the Release cell may certify releases (`04:195`), and the factory must **stop** when *"memory/knowledge contradicts EventGraph in high-risk planning"* (`05:523`) [17]. Memory may recover intent; it may never certify truth. This is the exact line OB1's own in-house framing draws — *"the event chain is a ledger of what happened; Open Brain captures what the agent was thinking and why"* [20].

### 3.3 The external-frameworks law (Decision 15) and its v4.0 carry-forward

The ratified boundary is **v3.9 Decision 15**: external frameworks *"must not become kernel, truth source, Work replacement, policy owner, release authority, certification authority, capability promoter, factory controller, or Site replacement"* (`01:174`) [8]. v4.0 carries the *principle* forward generically — *"External policy engines are optional references or adapters only. They do not own policy, release authority, certification authority, or factory control"* (`03:158`); *"External runtimes such as Hermes, OpenManus, OpenClaw-like workers, Codex, CI, or future backends are references or adapters only"* (`04:252`) [15][16] — but **names no OpenBrain**. The OB1-specific decision therefore lives, un-superseded, in v3.9 (§4.4).

---

## 4. Comparative Analysis

### 4.1 Capability / Fit Matrix

| Dimension | OB1 / Open Brain | Civilization posture | Fit |
|---|---|---|---|
| Core role | Persistent memory/recall substrate (thoughts + vector search) [1] | Advisory memory behind `MemoryReference`; EventGraph is truth [15][21] | Adapter/pattern only |
| Retrieval | pgvector HNSW cosine + fingerprint dedup [4] | Governed recall improving a gated decision [21] | Useful shape; not authority |
| Embeddings | API (OpenRouter) [1] | Air-gap default; local-first required [21] | Gap — must vendor local path |
| Write contract | Verifiable, fail-closed capture (PR #5) [6] | "Confirmed only by read-back" durability [2] | Strong convergence (§5.2) |
| Truth / certification | None — deliberately fail-open recall | Release-only certification; stop-on-contradiction [17] | Off-limits |
| Governance metadata | `metadata jsonb`, no trust/freshness/contradiction fields [4] | `MemoryReference` trust-accounting [21] | Civilization must supply it |
| License | FSL-1.1-MIT, internal use OK [3] | Internal advisory tooling permitted | Compatible for internal use |

### 4.2 Structural Convergence — Where OB1 Genuinely Fits

The pattern is a real fit because it shares the Civilization's instincts: **memory-of-intent separate from the truth ledger** (the reasoning-log/transaction-log split is stated on both sides in near-identical words [20]); **verbatim capture** with a **fail-closed, verifiable write** (PR #5's *"treat as NOT saved"* is the Civilization's own durability rule in code [6]); a **clean MCP tool shape** (six read-mostly tools + one annotated writer) that is a plausible interface for a future governed recall adapter; and **content-fingerprint dedup** for idempotent writes across capture paths [4].

### 4.3 The Seam — Advisory Recall vs. Governed Truth (critique in both directions)

OB1 is deliberately **fail-open recall**: it stores verbatim content, searches it, and returns the nearest thoughts. It carries no trust level, no freshness or contradiction state, no source hash beyond the dedup fingerprint, and no link to an evidence ledger [4]. That is correct at the recall layer and wrong at the authority layer — the same seam MemPalace showed [21]. The Civilization supplies exactly what OB1 structurally lacks: recalled content enters as advisory, is usable in gated work only once represented as a `MemoryReference`, and can never quietly influence high-risk planning (the factory stops on contradiction, `05:523`) [17]. The inverse critique is just as real: OB1 *runs today* as Transpara's reasoning log and recovers agent intent across reboots [20], while the governed `MemoryReference` regime is doctrine with no selected runtime owner — OB1 is the working proof that the pattern is worth governing.

### 4.4 Decision Record, ADR Disposition, and Contribution Determination

**Decision-record determination (stated crisply per the standing rule):**

1. **Does a dark-factory ADR exist for this subject?** **Yes — two, both Proposed and subsumed.** `ADR-0004` ("OpenBrain planning boundary") and `ADR-0013` ("OpenBrain optional pattern") exist as archived ADRs, each **Status: Proposed**, and are ratified only *transitively* through accepted **Decision 12** (`DF-V3.9-ADR-001`, `canonical: true`, `01:140`) and the legacy coverage matrix (`09:78`, `09:107`) [8][10]. There is **no standalone *accepted* OB1 ADR**, and **no restatement of OpenBrain anywhere in the accepted v4.0 doc set** (repo-wide grep of `v4.0/0[1-7]` for `openbrain|ob1|cognitive planning` → zero) [13–19]. OB1 survives in v4.0 only as operational *"advisory-memory hygiene"* in the dev loop, never as evaluated doctrine.
2. **Should one be created?** **No new ADR.** Nothing here is adopted as a Civilization dependency, runtime, or control-plane component — the same disposition the sibling evaluations reached for MemPalace, Solo Orchestrator, PageIndex, and the Owain Lewis system [21]. The durable record is this evaluation plus the existing accepted Decision 12/15 and crosswalk row; the operative handle for OB1 is **Decision 12/15 (`DF-V3.9-ADR-001`)**, not a standalone accepted OB1 ADR.
3. **Does it contribute to the Civilization, and how?** **Pattern-only.** The contribution is the **reasoning-log / memory-of-intent pattern** — advisory memory of *why*, separate from the EventGraph record of *what* — already realized as Transpara's internal Open Brain store [20], plus the six mineable mechanisms in §5 (led by the verifiable fail-closed capture contract). Under Decision 15, none of OB1's code may hold work-scheduling, gate, certification, truth, or policy responsibilities, and no learning below proposes otherwise [8]. Net: **high as a running proof** of the pattern the doctrine already names, **moderate as a source** (the capture contract and dedup patterns are immediately actionable).

The adoption verdict is therefore: **pattern-only, un-changed and now code-confirmed** — borrow the reasoning-log pattern (already in use internally, advisory-only), never import OB1 into any control-plane role. This is not a runtime activation and assigns no implementation owner. Two doctrine-hygiene items surface: (1) the **v4.0 carry-forward gap** — OB1's decision lives only in preserved v3.9; (2) the **label mismatch** — Decision 12's *"cognitive planning"* label for OB1 contradicts the artifact (a memory substrate) and collides with MemPalace's reserved *"recall substrate only"* slot (`01:145`) [8].

---

## 5. Strategic Learning Opportunities

All six translate OB1's mechanisms into the Civilization's record-and-gate frame; none import OB1's code or weaken a gate. (Recommendations only — no issues are filed by this evaluation.)

### 5.1 Reasoning-log / transaction-log separation as a named memory primitive (highest value)
Make "memory of intent" a first-class, reboot-survival primitive **distinct from EventGraph**, exactly as the 2026-04-09 hive decision drew it [20]. v4.0 already treats OpenBrain captures as *"advisory-memory hygiene"*; the learning is to elevate that from dev-loop hygiene to a governed `MemoryReference`-class primitive with trust/freshness/contradiction fields, so intent-recall is auditable rather than incidental.

### 5.2 The verifiable, fail-closed capture contract → the reference durability gate
PR #5's contract — *committed-but-no-id ⇒ "treat as NOT saved"*, embed-failure ⇒ success-with-`pending` (never a duplicate-creating error), id echoed for `fetch()` verification [6] — is the **server-side implementation of the Civilization's own "capture is confirmed only by read-back" rule** [2]. Adopt it as the worked example for any governed memory adapter's durability gate: never emit success on an unconfirmed write; make the permissive outcome the explicitly-proven branch.

### 5.3 DB-side content-fingerprint dedup → idempotent memory writes
The SHA-256 `content_fingerprint` + `ON CONFLICT DO UPDATE` upsert [4] gives idempotency across capture paths (byte-identical normalization avoids JS-vs-Postgres drift). A clean pattern for a recall adapter that must not double-count the same evidence.

### 5.4 Air-gap discipline for memory adapters (a boundary lesson)
OB1's OpenRouter embedding path [1] is the **inverse** of MemPalace's local-first posture [21] and the same shape as PageIndex's external-LLM dependency [21]. The lesson is a standing rule: any memory/recall/retrieval adapter must vendor a hash-pinned local embedding path before air-gapped use — pattern-only adoption never inherits a networked default.

### 5.5 Doctrine-label hygiene → reconcile the OB1 classification
Decision 12 files OB1 as *"cognitive planning pattern"* while every description of the artifact — and v4.0's own usage — calls it a memory substrate, and Decision 12 reserves *"recall substrate only"* for MemPalace [8]. Recommend a docs-process reconciliation: reclassify OB1's decision row to match its function (advisory memory-of-intent, MemPalace-style), preserving the identical advisory-only boundary.

### 5.6 The MCP tool shape → an adapter interface, not authority
The six-tool read-mostly + single-annotated-writer surface [1] is a good shape for a future MemoryKeeper/Researcher recall adapter — adopt the *interface*, publish results as governed `MemoryReference`s, never as authority.

---

## 6. The Inverse: What OB1 Cannot Take From the Civilization by Adoption Alone

Trust-accounted memory that knows its own freshness and contradictions (`MemoryReference` fields OB1's `metadata jsonb` does not carry); a binding to an append-only truth ledger that outlives any session; fail-closed certification that no recall can satisfy (`04:195`); the stop-on-contradiction rule that halts high-risk planning when memory disagrees with EventGraph (`05:523`); and an institution in which memory is *advisory by construction*, not by convention. OB1 supplies recall; it cannot supply the governance that makes recall safe to act on — that is the Civilization boundary, and it is the half OB1 was never built to provide.

---

## 7. Conclusions

OB1 is a credible, running, memory-of-intent substrate, and the pattern it embodies is already in use inside Transpara — advisory, reboot-surviving, and explicitly separate from the EventGraph truth ledger. The code confirms the 2026-05-13 disposition and hardens it: OB1 is **pattern-only**, gated out of every control and truth role (Decision 12/15), and the "cognitive planning" label the doctrine attached to it is a historical mismatch with the artifact. Where Transpara has touched the code (PR #5/#6), it moved a durability guarantee server-side that mirrors the Civilization's own read-back rule — the sharpest evidence that the pattern is worth governing rather than depending on. The correct status is: **credible advisory memory-of-intent pattern; ADRs exist (Proposed, subsumed into Decision 12/15); no new ADR; no authority; no runtime activation; internal operational use is FSL-permitted and doctrine-neutral.**

---

## 8. Recommended Next Steps (recommendations only; nothing filed by this evaluation)

1. **Confirm the crosswalk row** already records OB1 = pattern-only; no change of substance needed, only the §5.5 label reconciliation.
2. **Docs-hygiene reconciliation (§5.5):** reclassify OB1's Decision-12 line from "cognitive planning" to advisory memory-of-intent, matching the artifact and MemPalace's slot, via the normal docs process — boundary unchanged.
3. **If any §5 learning is pursued** (esp. §5.1/§5.2), it enters as its own issue → Factory Order → TLC arc, where design-stage CFADA is the decision record for the *adopted pattern* (not for OB1's code).
4. **No ADR, no runtime activation, no implementation owner.** Internal operational use of the fork as the Open Brain store continues as advisory tooling under FSL internal-use terms [3].
5. **Air-gap standing rule (§5.4):** record that any memory/recall adapter must vendor a local embedding path before air-gapped use.

---

## 9. References

[1] `transpara-ai/OB1` @ `1c4c9069fba06f82411005c77dafac8711805bdc` (2026-06-17): `server/index.ts`, `server/capture-response.mjs`, `server/deno.json`, `server/package.json`. Local clone read as code truth. Fork of upstream [7]; `upstream` push disabled (`DISABLE_PUSH_TO_UPSTREAM`).
[2] OB1 self-description & guard rails: `README.md` ("the infrastructure layer for your thinking"; "not a notes app"), `CLAUDE.md` ("a persistent AI memory system"; remote-MCP / no-secrets / no-destructive-SQL guard rails), `AGENTS.md`. Upstream-authored, cited as context.
[3] `OB1/LICENSE.md` — Functional Source License v1.1, MIT Future License; "Copyright 2026 Nate B. Jones"; Permitted Purposes incl. internal use; Competing-Use bar; two-year per-version MIT conversion.
[4] Canonical storage schema (mirror): `integrations/local-docker/db-init/01-schema.sql` (`thoughts` table, `pgvector` HNSW, `content_fingerprint` dedup, `match_thoughts`/`upsert_thought` RPCs) and `docs/01-getting-started.md` (1536-dim OpenRouter embeddings).
[5] `OB1/SECURITY.md` (repo-only scope; excludes running infra; TODO contact); `OB1/.gitignore` (secret-file coverage gap).
[6] Transpara hardening PRs: `transpara-ai/OB1` PR #5 (`1d1d6e2`, verifiable + embedding-failure-safe `capture_thought`) and PR #6 (`1c4c906`, `deno check` resolution + empty-error guard). The fork's only substantive divergence from upstream.
[7] Upstream `NateBJones-Projects/OB1` — cited as context only; never re-published, never a push/PR target.
[8] **Decision 12** ("External Patterns Are References, Not Controllers"; "OpenBrain: optional cognitive planning pattern only," `01:140`; "MemPalace: recall substrate only," `01:145`) and **Decision 15** ("External Frameworks Stay Outside Control Roles," `01:174`) — `DF-V3.9-ADR-001` (`raw/transpara/dark-factory/v3.9/01-unified-architecture-decisions-v3.9.md`), `status: accepted`, `canonical: true`.
[9] `DF-V3.9-EPIC-TECH-CROSSWALK` (`.../implementation/epics/02-technology-decision-crosswalk-v3.9.md`, `status: review`, `canonical: false`) — the "OpenBrain | pattern-only" row (`:76`), the per-item advisory-only guard rail (`:131-135`), and the frozen-reference/reopen-trigger policy (`:43-58`).
[10] `DF-V3.9-COV-009` (`.../09-legacy-coverage-matrix-v3.9.md`, accepted) — `ADR-0004 OpenBrain planning boundary` (`:78`), `ADR-0013 OpenBrain optional pattern` (`:107`), and the distinct `PageIndex` row (`:252`); plus archive `ADR-0004`/`ADR-0013` (both Status: Proposed).
[11] `raw/transpara/dark-factory/research/pageindex-role-in-transpara-stack.md` — OB1 as "cross-tool memory substrate / agent-readable long-term memory"; the three-layer synthesis (OpenBrain = memory substrate / LLM Wiki = compiled knowledge / PageIndex = retrieval); "augmentation, not replacement."
[12] `wiki/civilization-landscape-investigation.md` — the 2026-05-13 survey; OB1 in Batch B (memory/knowledge/research), per-item decision "optional cognitive-planning pattern; advisory only, cannot replace PlanningProposal/Requirement/AcceptanceCriterion/EventGraph evidence"; the OpenBrain = OB1 = Nate B. Jones binding (asserted here and in [11], not in the crosswalk cell).
[13] `DF-V4.0-README` (accepted, canonical, v4.0.54) — scoped supersession; does **not** supersede `DF-V3.9-ADR-001` or the crosswalk.
[14] v4.0 doc 01 — development process as governed Civilization function (accepted).
[15] v4.0 doc `03` — Civilization Governance & Authority: "EventGraph remains the source of truth… Memory and knowledge are advisory only" (`03:36`); "External policy engines are optional references or adapters only…" (`03:158`).
[16] v4.0 doc `04` — Production Workflow Runtime: Release-only certification (`04:195`); Base Slice 0 (`04:199-220`, "must not use… memory recall, knowledge reuse"); external runtimes are references/adapters only (`04:252`).
[17] v4.0 doc `05` — Verification/Audit/Risk/Eval: the factory must stop when "memory/knowledge contradicts EventGraph in high-risk planning" (`05:523`).
[18] v4.0 docs `06`/`07` — autonomy gates / current state; CFAR-CFADA dev-arc gate standard (accepted).
[19] `grep -rniE 'openbrain|ob1|cognitive planning' v4.0/0[1-7]-*.md` → zero matches (2026-07-07): OB1 is not restated in accepted v4.0 core doctrine.
[20] **Open Brain** (the running store, Supabase project `njofekbuaauffxqsfikl`, reached via `mcp__open-brain__*`): the 2026-04-09 hive reboot-survival decision ("the event chain is a ledger of what happened; Open Brain captures what the agent was thinking and why… agents read their last Open Brain thought to recover intent"); the 2026-06-13 upstream-merge (`0c442a2`, merge-preserve, 5 Transpara-only commits) + `open-brain-mcp` Edge Function redeploy + MCP smoke test; the "grounded fork chronology" (GitHub `createdAt`: 4/08 OB1 ← NateBJones-Projects).
[21] Companion series — TAI-RES-2026-004 (MemPalace: the `MemoryReference` boundary, local-first recall) and TAI-RES-2026-007 (PageIndex: the memory-cluster neighbor, the external-LLM air-gap lesson), plus -001/-002/-003/-005/-006.
[22] Ratified external-framework boundary: v3.9 Decision 15 lineage ("external frameworks stay outside control roles"), carried into v4.0 docs `03`/`04` generically.
