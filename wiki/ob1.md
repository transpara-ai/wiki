---
entity: OB1 (Open Brain)
aliases:
  - OB1
  - Open Brain
  - OpenBrain
  - transpara-ai/OB1
tier: investigation
status: compiled
last_compiled: 2026-06-14
sources:
  - /Transpara/transpara-ai/repos/OB1/README.md  # upstream README mirrored in the fork: "infrastructure layer for your thinking"; one database / one AI gateway / one chat channel; FSL-1.1-MIT; maintainers
  - /Transpara/transpara-ai/repos/OB1/CLAUDE.md  # what the repo is: Supabase + pgvector, one MCP protocol, any AI client; guard rails
  - /Transpara/transpara-ai/repos/OB1/LICENSE.md  # FSL-1.1-MIT, "Copyright 2026 Nate B. Jones"
  - /Transpara/transpara-ai/repos/OB1/sync-upstream.sh  # fork mechanics: upstream = NateBJones-Projects/OB1
  - raw/transpara/dark-factory/v3.9/implementation/epics/02-technology-decision-crosswalk-v3.9.md  # DF-V3.9-EPIC-TECH-CROSSWALK v3.9.1 (status:review): "OpenBrain — pattern-only" row + per-item note
  - raw/transpara/dark-factory/v3.9/01-unified-architecture-decisions-v3.9.md  # Decision 12: "OpenBrain: optional cognitive planning pattern only"; Decision 15 (control-role exclusion)
  - raw/transpara/dark-factory/v3.9/09-legacy-coverage-matrix-v3.9.md  # ADR-0004 / ADR-0013 OpenBrain planning boundary entries
  - raw/transpara/dark-factory/research/pageindex-role-in-transpara-stack.md  # source-grounded characterization of OpenBrain as a cross-tool memory substrate (PageIndex = augmentation, not replacement)
  - Open Brain  # the system itself (Supabase project njofekbuaauffxqsfikl); 2026-06-13 upstream-merge + redeploy op-note; transaction-log vs reasoning-log design decision
confidence:
  upstream_identity: high — the fork's git remotes name upstream NateBJones-Projects/OB1 with push disabled, and LICENSE.md reads "Copyright 2026 Nate B. Jones"; README text matches the task's theme verbatim.
  crosswalk_decision: high — "pattern-only" is stated in both the v3.9.1 crosswalk row and accepted-canonical Decision 12 ("optional cognitive planning pattern only").
  crosswalk_identity_binding: medium-high — the crosswalk row is labelled only "OpenBrain"; the binding OpenBrain = OB1 = Nate B. Jones is asserted by the already-compiled [[civilization-landscape-investigation]] article and the first-party PageIndex research note, not by the crosswalk row itself.
  cognitive_planning_label: contested-by-framing — Decision 12 / the crosswalk call OB1 a "cognitive planning pattern," but the README, CLAUDE.md, and the PageIndex note all describe a memory/recall substrate, not a planner. Both framings are stated below; neither is silently picked.
  fork_date: thin — 2026-04-08 is asserted by the compile request and corroborated only indirectly (the fork's tracked files carry Apr-8 dates; the related open-brain monorepo restructuring is dated 2026-04-08 in Open Brain). No corpus thought explicitly timestamps "OB1 forked on 2026-04-08."
---

# OB1 (Open Brain)

**A forked public project the [[civilization-landscape-investigation]] surveyed, and decided to learn from rather than depend on.** OB1 — branded **Open Brain** — is an external open-source project by Nate B. Jones that describes itself as "the infrastructure layer for your thinking. One database, one AI gateway, one chat channel" (`OB1/README.md`). Transpara maintains a fork at `transpara-ai/OB1`, tracking upstream `NateBJones-Projects/OB1`; the fork was taken into the org on **2026-04-08** (see the fork-date caveat below). When the 2026-05-13 landscape investigation drew its boundary around the [[dark-factory]] architecture, OB1 was one of the ~22 external candidates it evaluated, and the verdict recorded in the v3.9 doctrine is **pattern-only**: an optional pattern to borrow, never a dependency, kernel, truth source, or authority (`02-technology-decision-crosswalk-v3.9.md`; `01-unified-architecture-decisions-v3.9.md`, Decision 12).

This article is about **Transpara's investigation and decision**, not a re-publication of OB1's own documentation. OB1 is upstream public code (the same don't-republish boundary the org applies to any forked public upstream); it is cited here as context only. The lasting Transpara artifact is the decision row, not the upstream's recipe catalog.

## What OB1 is (upstream, as context)

The fork's mirrored `README.md` and `CLAUDE.md` describe a memory system, not a notes app:

- **One database** — Supabase with `pgvector` for vector search over a `thoughts` table (`OB1/CLAUDE.md`: "one database (Supabase + pgvector), one MCP protocol, any AI client").
- **One AI gateway / one chat channel** — an open protocol (MCP) so "every AI tool you use shares the same persistent memory of you. Claude, ChatGPT, Cursor, Claude Code… One brain. All of them" (`OB1/README.md`). Capture is via a chat channel (Slack or Discord integrations in the repo).
- **No middleware** — "No middleware, no SaaS chains, no Zapier." MCP servers are remote (Supabase Edge Functions), not local stdio servers (`OB1/CLAUDE.md`, Guard Rails).
- **License: FSL-1.1-MIT** — Functional Source License, MIT Future License, "Copyright 2026 Nate B. Jones" (`OB1/LICENSE.md`). The fork's `CLAUDE.md` reads this as "No commercial derivative works" — a real constraint on how Transpara could ever use the code, distinct from a permissive MIT/Apache project.

The public repo is large and community-driven: curated extensions (household knowledge, CRM, job-hunt), community recipes (data importers, dedup, life-engine), skills, dashboards, integrations, and schema sidecars. None of that catalog is re-published here; it is named only to characterize what kind of project the investigation was judging.

> Note: "Open Brain" is also the name of the *Transpara-internal* thought-capture system this wiki cites as a source (the Supabase project `njofekbuaauffxqsfikl`, reached via `mcp__open-brain__*` tools). The two are directly related — Transpara's Open Brain is built on this stack, and the fork's deployed MCP Edge Function is literally named `open-brain-mcp` (Open Brain op-note, 2026-06-13). But "OB1 the upstream repo" and "Open Brain the running internal memory store" are not the same object, and this article keeps them distinct: the repo is the *thing surveyed*; the running store is a *source*.

## Why it entered the arc

OB1 entered the record along two tracks that meet at the same place.

**As a dependency of how Transpara actually works.** Transpara runs Open Brain as its own cross-tool memory store, and an early design decision drew the line that the crosswalk later formalized: in the [[hive-governance]] reboot-survival design, the [[event-graph|eventgraph]] is the *transaction log* ("a ledger of what happened") while **Open Brain is the *reasoning log*** that "captures what the agent was thinking and why" — on reboot, agents read their last Open Brain thought to recover intent rather than replaying thousands of raw events (Open Brain thought, 2026-04). This is the clearest in-house statement of the role OB1's pattern plays: durable, agent-readable memory of *intent*, explicitly **separate** from the sovereign truth ledger.

**As a candidate in the landscape survey.** On 2026-05-13 the [[civilization-landscape-investigation]] put OB1 on its fixed candidate list — "OpenBrain / OB1 (`transpara-ai/OB1`, from Nate B. Jones)" — in the memory/knowledge/research batch, alongside [[memory-knowledge-advisory|MemPalace]], the Karpathy LLM Wiki, and PageIndex. The investigation's discipline was to ask of each: is it already in the design, and if not, what is its exact marginal contribution and what would it replace? For OB1 the answer was a borrowed pattern, gated out of every control role.

## The decision: pattern-only

The accepted-canonical statement is **v3.9 Decision 12, "External Patterns Are References, Not Controllers"**, which lists OB1 in one line:

> OpenBrain: optional cognitive planning pattern only. (`01-unified-architecture-decisions-v3.9.md`, Decision 12)

The per-item **v3.9.1 crosswalk** row says the same and adds the boundary explicitly (`02-technology-decision-crosswalk-v3.9.md`):

> **OpenBrain — pattern-only.** Integration mode: optional cognitive planning pattern. Owning epic: none. Main risk: "vague pattern can become cargo-cult architecture." … "Any cognitive planning patterns must remain advisory and cannot replace `PlanningProposal`, `Requirement`, `AcceptanceCriterion`, or EventGraph evidence."

The legacy coverage matrix records two ADR handles for the same boundary — **ADR-0004 "OpenBrain planning boundary"** and **ADR-0013 "OpenBrain optional pattern"**, both marked "Covered: optional cognitive planning pattern only" (`09-legacy-coverage-matrix-v3.9.md`).

What pattern-only means here, drawn straight from the crosswalk's own definitions:

- **No code import, no automatic upstream tracking.** "Pattern-only adoptions do not import upstream code and do not automatically track upstream behavior." The pattern is **frozen at the v3.9 reference point** unless an epic explicitly reopens it (with named reopen triggers: upstream design changes, eval regressions, capability evolution, a reviewer marking it stale, or a security/licensing/governance change).
- **Advisory only — never authority.** Under the umbrella **Decision 15** ("External Frameworks Stay Outside Control Roles"), OB1 — like every surveyed framework — "must not become kernel, truth source, Work replacement, policy owner, release authority, certification authority, capability promoter, factory controller, or Site replacement." Decision 12 states the rejected roles directly: no external framework as "kernel, release authority, policy owner, capability promoter, or truth source."
- **No implementation owner.** The crosswalk lists the owning epic as "none." No epic is scheduled to integrate OB1; the row exists to *record the boundary*, not to plan adoption.

> ⚠ **Fail-legible note (what the crosswalk row literally names).** The crosswalk and Decision 12 rows are labelled only **"OpenBrain"** — they do not, in those lines, spell out "OB1" or "Nate B. Jones." The identification OpenBrain = OB1 = `transpara-ai/OB1` (Nate B. Jones) is **asserted by two other first-party sources**, not by the decision row itself: the already-compiled [[civilization-landscape-investigation]] article names the candidate "OpenBrain / OB1 (`transpara-ai/OB1`, from Nate B. Jones)," and the first-party PageIndex research note is explicitly "Versus Nate B. Jones's OpenBrain / OB1." Given the matching repo path, author, and "infrastructure layer for your thinking" tagline, this article treats the binding as established — but flags that the binding lives in the surrounding corpus, not in the crosswalk cell.

## The "cognitive planning" tension (stated, not resolved)

There is a genuine framing conflict in the sources, and the house rule is to state both rather than silently pick.

- **The decision docs call OB1 a "cognitive planning pattern."** Decision 12, the crosswalk row, and both ADR handles all use that phrase, and the crosswalk's guard rail is specifically about *planning* artifacts ("cannot replace `PlanningProposal`, `Requirement`, `AcceptanceCriterion`").
- **Every description of what OB1 actually is calls it a memory/recall substrate, not a planner.** The README ("persistent memory of you"), `CLAUDE.md` ("a persistent AI memory system"), and the first-party PageIndex note are unambiguous: the note enumerates OB1 as "cross-tool memory substrate / persistent personal/work context / MCP-accessible database / agent-readable long-term memory," and concludes "OpenBrain = persistent agent-readable memory substrate" (`pageindex-role-in-transpara-stack.md`). Decision 12 *also* separately lists "MemPalace: recall substrate only" — so the doctrine clearly has a "recall substrate" category it did **not** put OB1 in.

> ⚠ **Fail-legible note (label vs. substance).** Why the doctrine files OB1 under "planning" rather than "memory" is **not explained in any source read this run** — it is an asserted classification, not a justified one. The most defensible reconciliation the corpus actually supports is the in-house transaction-log/reasoning-log split: OB1's *value to Transpara* is as a memory of agent **intent and reasoning** that planning depends on (Open Brain, 2026-04), which is "planning-adjacent" memory. But that is a reconstruction; treat the "cognitive planning" label as the doctrine's word, the "memory substrate" label as what the artifacts describe, and the gap between them as unresolved in the sources. Either way the *boundary* is identical and is the load-bearing part: advisory only, never `PlanningProposal`/`Requirement`/`AcceptanceCriterion`/EventGraph evidence, never a controller.

## Where OB1 sits relative to neighbours

The PageIndex investigation note (`pageindex-role-in-transpara-stack.md`) is the one place the corpus positions OB1 against adjacent tools in detail, and it does so as **complementary layers, not competitors**:

```
OpenBrain = persistent agent-readable memory substrate
LLM Wiki  = compiled/synthesized knowledge artifact
PageIndex = reasoning-based retrieval over long source documents
```

The grounded finding was that **PageIndex augments, not replaces, OB1**: PageIndex can swap in for the brittle vector/chunk retrieval *subsystem* over long documents, but "does not replace the higher-level idea of a persistent, accumulating knowledge substrate" — that role belongs to OB1 (notes/conversations/captures) and the LLM Wiki (curated knowledge). This is the same "augmentation, not replacement; keep it out of the truth/memory role" logic the investigation applied across the board.

## Fork status and the upstream boundary

The fork is a real, maintained mirror, not an import:

- `git remote -v` in `transpara-ai/OB1`: **`origin` = `github.com/transpara-ai/OB1`** (the fork the org owns), **`upstream` = `github.com/NateBJones-Projects/OB1.git`** with the push URL set to the literal sentinel **`DISABLE_PUSH_TO_UPSTREAM`** — upstream pushes are mechanically blocked, matching the org's hard rule that upstream/public code is never a push target.
- A `sync-upstream.sh` script exists to *pull* Nate's changes into the fork ("pull Nate's changes into your OB1 fork"), adding the upstream remote if missing.
- On **2026-06-13**, Codex merged `NateBJones-Projects/OB1` upstream main into `transpara-ai/OB1` main (merge-preserve, backup branch pushed first, merge commit `0c442a2`) and redeployed the Supabase `open-brain-mcp` Edge Function on project `njofekbuaauffxqsfikl`; an MCP smoke test confirmed the tools (`search`/`fetch`/`search_thoughts`/`list_thoughts`/`thought_stats`/`capture_thought`) and the write path (Open Brain op-notes, 2026-06-13). This is the most recent on-record activity on the fork and shows it is kept current with upstream while staying inside the no-push-upstream boundary.

> ⚠ **Fail-legible note (fork date is thin).** "Forked into transpara-ai on 2026-04-08" comes from the compile request. It is corroborated only **indirectly**: the fork's tracked files (`README.md`, `LICENSE.md`, `CONTRIBUTING.md`, etc.) carry 2026-04-08 timestamps in the working tree, and the related Transpara `open-brain` monorepo underwent a major restructuring dated 2026-04-08 in Open Brain. **No corpus thought read this run explicitly states "OB1 was forked on 2026-04-08."** Treat the date as plausible and weakly corroborated, not independently proven.

## What is thin or absent

- **No fork-specific divergence is documented here.** Whether `transpara-ai/OB1` carries Transpara-specific commits beyond upstream syncs was not established this run; the recent activity on record is upstream-merge-and-redeploy, not original feature work. (One adjacent Open Brain note mentions an "agentic harnesses skill pack" on `transpara-ai/OB1`, 2026-04-15 / PR #151, but its details were not verified this run.)
- **The investigation's per-candidate Phase-4 write-up for OB1 was not located this run.** The landscape article summarizes OB1's outcome, and Decision 12 / the crosswalk state it, but the ~25-field per-candidate template entry specifically for OB1 was not read here. The PageIndex note is the closest grounded analysis of OB1 in the corpus.
- **Why "cognitive planning" and not "recall substrate"** — unexplained in sources, as noted above.

## Cross-links

- [[civilization-landscape-investigation]] — the 2026-05-13 survey that produced the pattern-only verdict; names OB1 in its candidate list and per-item decisions.
- [[dark-factory]] — the architecture whose boundary the decision defends.
- [[event-graph]] — the sovereign truth ledger OB1's memory is explicitly *not* allowed to become or supersede (transaction log vs. reasoning log).
- [[memory-knowledge-advisory]] — the advisory memory/knowledge regime (MemPalace etc.) that the same Decision 12 / crosswalk pass governs alongside OB1.
- [[v3-9]] — the canonical revision that folded the investigation's decisions in.

## Sources & provenance

Upstream context (the fork, mirrored locally; cited as context only, never re-published):
- `OB1/README.md` — "the infrastructure layer for your thinking. One database, one AI gateway, one chat channel"; not-a-notes-app / pgvector + open protocol framing; maintainers (Nate B. Jones, repo team); `FSL-1.1-MIT`.
- `OB1/CLAUDE.md` — "a persistent AI memory system — one database (Supabase + pgvector), one MCP protocol, any AI client"; remote-MCP / no-secrets guard rails; FSL "no commercial derivative works" reading.
- `OB1/LICENSE.md` — Functional Source License v1.1, MIT Future License; "Copyright 2026 Nate B. Jones."
- `OB1/sync-upstream.sh` — fork mechanics; upstream = `https://github.com/NateBJones-Projects/OB1.git`. Git remotes (`origin` = `transpara-ai/OB1`; `upstream` push = `DISABLE_PUSH_TO_UPSTREAM`) read via `git remote -v`. Upstream URL: https://github.com/NateBJones-Projects/OB1

Transpara investigation and decision (the actual subject):
- `dark-factory/v3.9/01-unified-architecture-decisions-v3.9.md` — **Decision 12** ("OpenBrain: optional cognitive planning pattern only"; rejected control roles) and **Decision 15** (external frameworks stay outside control roles).
- `dark-factory/v3.9/implementation/epics/02-technology-decision-crosswalk-v3.9.md` (`DF-V3.9-EPIC-TECH-CROSSWALK`, v3.9.1, **`status: review` / `canonical: false`**) — the "OpenBrain — pattern-only" row, integration mode, "cargo-cult architecture" risk, advisory-only guard rail, and the frozen-reference / reopen-trigger upstream-refresh policy.
- `dark-factory/v3.9/09-legacy-coverage-matrix-v3.9.md` — ADR-0004 "OpenBrain planning boundary" and ADR-0013 "OpenBrain optional pattern," both "Covered: optional cognitive planning pattern only."
- `dark-factory/research/pageindex-role-in-transpara-stack.md` — the source-grounded "Versus Nate B. Jones's OpenBrain / OB1" comparison; OB1 as cross-tool memory substrate; "PageIndex is an augmentation, not a replacement"; the three-layer synthesis.

Operational corroboration from **Open Brain** (the running store): the transaction-log (eventgraph) vs. reasoning-log (Open Brain) reboot-survival design decision (2026-04), establishing OB1's pattern as memory-of-intent separate from truth; and the 2026-06-13 upstream-merge (`0c442a2`) + `open-brain-mcp` Edge Function redeploy / smoke-test op-notes on Supabase project `njofekbuaauffxqsfikl`.

**Conflicts stated, not resolved.** (1) *Label vs. substance*: the doctrine classifies OB1 as a "cognitive planning pattern" while every description of the artifact (README, CLAUDE.md, PageIndex note) calls it a memory/recall substrate — and Decision 12 separately reserves "recall substrate only" for MemPalace; the gap is unexplained in sources and is flagged, not papered over. (2) *Identity binding*: the crosswalk/Decision rows name only "OpenBrain"; the OB1 / Nate B. Jones binding comes from the landscape article and the PageIndex note. (3) *Fork date*: 2026-04-08 is from the compile request, only indirectly corroborated. (4) *Crosswalk status*: the per-item crosswalk detail is `status: review` / `canonical: false`; the ratified part is the one-line Decision 12 / Decision 15 routing rule. `[[wikilinks]]` are forward references; some targets (e.g. `[[hive-governance]]`) may not be compiled yet.

## Run-3 update (2026-06-14)

**OB1 PR #5 — "make capture_thought verifiable and embedding-failure safe"** (merged 2026-06-14, commit `1d1d6e2`).

This PR moves the read-back verification burden from the client to the server. Before this change, the server returned a success-shaped response string ("Captured as observation…") even when the underlying Supabase write failed silently — for example, on a quota 402 or a swallowed error. The client-side CLAUDE.md write cycle (mark → write → verify via `list_thoughts` → report on the verification, not the write) was the interim mitigation, but it was a client-side patch for a server-side durability gap.

After PR #5, the server itself ensures durability before returning success: it does not emit a success response unless the write is confirmed, and embedding failures are handled safely rather than swallowed. This resolves the documented "confabulation trap" — the known failure mode where an agent reports "captured" on the strength of a success string that was the service's claim, not proof of a durable write.

**What changes for clients:** the `capture_thought` tool's success response is now trustworthy as a write confirmation. The read-back step in the CLAUDE.md write cycle remains a recommended end-to-end safety net (it catches transmission and routing failures that live outside the server's control), but it is no longer compensating for a known server-side gap.

**Source:** `transpara-ai/OB1` PR #5, commit `1d1d6e2`; `OB1/CLAUDE.md` write-cycle documentation (the "Capture is confirmed only by read-back" section, which now documents defense-in-depth rather than mitigation of a known defect).
