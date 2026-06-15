---
entity: The lovyou.ai Fork
aliases: [the lovyou-ai fork, lovyou.ai fork, the fork, lovyou-ai → transpara-ai, the origin fork]
tier: arc
status: compiled
last_compiled: 2026-06-14
sources:
  - raw/searles/all-posts-1.md  # post 2, "From 44 to 200", 2026-02-28 [Searles-P2] — hive0/LovYou origin: ~70-agent run, 44 primitives, 200/14-layers
  - Open Brain  # fork chronology and spawn-lifecycle: lovyou-ai-hive/work/agent/eventgraph/site captured thoughts (earliest 2026-03-03; spawn-lifecycle 2026-04-08/09; rebrand PRs eventgraph#8/work#20)
  - https://github.com/transpara-ai  # the org that owns the diverged codebase (repos: agent, eventgraph, hive, site, work + docs)
confidence:
  historical_origin: grounded for the *fact* of a lovyou-ai → transpara-ai fork (many Open Brain thoughts name the pre-rebrand repos and the rebrand PRs); per-repo first-commit dates and the 2026-03-30 fork date are reconstructed, not recorded
  upstream_now_inactive: maintainer's observation (2026-06-14) — not independently verified this run; recorded as characterization, not as a checked GitHub fact
  hive0_origin: single-author testimony (Searles post 2), classed "research input, not independently proven" by the first-party Dark Factory synthesis
---

# The lovyou.ai Fork

**A historical-provenance note: where the codebase originally came from.** The `transpara-ai` runtime codebase — **agent, eventgraph, hive, site, work** (plus **docs**) — was originally forked in early 2026 from Matt Searles' open-source LovYou / mind-zero work, which lived in the `lovyou-ai` GitHub org. That fork is the reason the [[hive-governance]] runtime and the broader [[dark-factory]] arc exist as code rather than as essays.

> **Status as of 2026-06-14 (maintainer's observation):** the `lovyou-ai` upstream is now inactive, and the `transpara-ai` codebase has diverged from it by hundreds of commits. This article is therefore a record of **where the code came from**, not a description of a live, actively-synced fork relationship. The wiki does **not** treat `lovyou-ai` as a current dependency, sync target, or active upstream. ([Status is the maintainer's characterization; it was not re-verified against the `lovyou-ai` org this run.])

## Where it came from: hive0 and LovYou

The upstream's origin story is told in Searles' second post, *"From 44 to 200"* (**2026-02-28**, [Searles-P2]). LovYou grew out of the late-night failure-tracing question behind [[the-20-primitives]]: those 20 primitives "became a hive of seventy autonomous agents, and … that hive — left running accidentally for two days — derived 44 foundation primitives on its own." That ~70-agent run is the object the wider corpus calls **hive0**; it is the seed the current [[hive-governance]] descends from in lineage, if not in literal code.

> ⚠ **Fail-legible note (hive0 is testimony, not proof).** The ~70-agent, two-day, self-derived-44 claim is **single-author testimony** with no run log or reproduction read this run. The first-party Dark Factory synthesis classes hive0 and the 44/200 ladder as **"research input, not independently proven,"** and Searles' own later guardrail ([[the-cult-test]]) concedes the run "could be repeated, might produce different results." The detail of the 44 and the 14 layers belongs to [[primitive-basis]] / [[the-20-primitives]]; it is summarized here only to anchor *what was forked from*.

A source-internal subtlety to keep straight: the upstream code Searles writes about is named **mind-zero-five** (`github.com/mattxo/mind-zero-five` in the post footers), while the repos the `transpara-ai` codebase actually carries are named **eventgraph / hive / work / agent / site**. The sources do **not** assert these are the same codebase — see [[event-graph]] and [[mind-zero-five]] for the repo-identity conflict, which this article does not resolve.

## What it became, and when (reconstructed chronology)

Under `transpara-ai` ownership the forked code became the substrate of the live [[hive-governance]] runtime: co-dependent repos linked through go.mod `replace` directives, a runtime that boots from chain replay and hosts the [[civic-roles|nine civic agents]], and a growth loop whose first dynamically-spawned agent (the **researcher**, 2026-04-08) proved the SELF-EVOLVE invariant end to end. Over April 2026 the code was mechanically **rebranded** `lovyou-ai → transpara-ai` (a 212-file rename in `eventgraph` landed as `transpara-ai/eventgraph#8`; `work` was renamed in `transpara-ai/work#20`).

The precise fork dates are **reconstructed, not recorded** — Open Brain's earliest capture of any kind is 2026-03-03, and the earliest captured repo work is 2026-04-08/09, naming the repos under their pre-rebrand identities (`lovyou-ai-hive`, `lovyou-ai/work`, `lovyou-ai/agent`, `lovyou-ai-site`):

| When | Event | Evidence status |
|---|---|---|
| 2026-02-28 | Upstream LovYou / mind-zero / hive0 described as live (Searles post 2) | Grounded (source post); hive0 itself is testimony |
| Feb 2026 (claimed) | First fork-and-build of the upstream | **Reconstructed** — predates GitHub history and Open Brain |
| 2026-03-30 (claimed) | Fork of agent/eventgraph/hive/site/work from `lovyou-ai` | **Asserted by task framing** — no 3/30 capture found |
| 2026-04-08/09 | Earliest captured spawn-lifecycle & repo work (`lovyou-ai-*`) | Grounded (Open Brain) |
| April 2026 | Mechanical rebrand to `transpara-ai` in code (eventgraph#8, work#20) | Grounded (Open Brain) |
| by 2026-06 | Codebase diverged hundreds of commits; upstream inactive | Maintainer's observation (2026-06-14) |

## Why it mattered to the arc

The fork was the hinge between **[[primitive-basis]]** (the philosophy and vocabulary the project was permitted to consume) and the **[[dark-factory]]** machinery built on top of it. The upstream supplied the accountability premise and the running shape — an append-only, hash-chained [[event-graph]]; a [[hive-governance]] of governed agents; a growth loop — and the fork is where that became code that could be owned, modified, gated, and held to the project's own fail-closed standards. Only the 20 primitives were ever accepted as load-bearing *basis*; 44/200/hive0/mind-zero were taken as "research input" or "prior pattern" (see [[primitive-basis]]). The downstream arc — the reunification, the [[dark-factory]] production loop, the civic-role runs — all built on this substrate and then moved well past it.

## Sources & provenance

- `raw/searles/all-posts-1.md` — post 2, *"From 44 to 200"*, 2026-02-28 · [Searles-P2] · https://mattsearles2.substack.com/p/from-44-to-200 — the hive0/LovYou origin (the ~70-agent run, the self-derived 44, the 200-across-14-layers derivation).
- **Open Brain** — fork chronology and spawn-lifecycle facts: the co-dependent `replace`-directive structure and the 2026-04-17 `eventgraph`/hive type-drift break; the 9-static-/2-dynamic-agent boot; the **researcher** as the first dynamic spawn (2026-04-08, first SELF-EVOLVE proof); the April-2026 rebrand PRs (`transpara-ai/eventgraph#8`, `transpara-ai/work#20`); the export-audit fact that Open Brain's earliest capture is 2026-03-03.
- **https://github.com/transpara-ai** — the org that owns the diverged codebase (repos `agent`, `eventgraph`, `hive`, `site`, `work`, `docs`). Not browsed for first-commit dates this run.

**What is contested or unproven, stated not resolved:** (1) the **2026-03-30 fork date** and the **February-2026 first-fork-and-build** — both reconstructed, with no corroborating capture or GitHub record read this run. (2) **hive0** (the ~70-agent two-day self-derivation of the 44) — single-author testimony, classed "research input, not independently proven." (3) **Repo identity** — the upstream Searles code is named `mind-zero-five`; the runtime repos are `eventgraph`/`hive`/etc.; the sources do not assert they are the same codebase (carried to [[event-graph]] / [[mind-zero-five]]). (4) **Upstream-now-inactive** — the maintainer's 2026-06-14 characterization, not re-verified against the `lovyou-ai` org this run.
