---
title: Civilization Wiki — provenance manifest
last_updated: 2026-06-21
status: partial — searles and open_brain mirrored; open_brain mirror stale after 2026-06-13; first_party/upstream_context not locally mirrored
authority: reference (the source manifest named in DESIGN.md)
tiers: [searles, first_party, open_brain, upstream_context]
---

# Civilization Wiki — provenance manifest

The per-source manifest named in `DESIGN.md` ("`PROVENANCE.md` — source manifest:
each raw item → origin, date, tier"). It records, for every source the wiki is
compiled from, its **origin**, its **date or range**, its **provenance tier**, and
**how the wiki uses it**. Tier vocabulary is taken verbatim from `DESIGN.md`
§Ingestion: `searles`, `first_party` (Transpara-authored), `open_brain`, and
`upstream_context` (a forked project's own docs — context, never the subject).

This file is the durable answer to "where did the wiki get this?" — the
compile-time companion to each article's "Sources & provenance" footer and to the
fail-loud freshness header in `index.md`.

## ⚠ Read this first — what is, and is NOT, mirrored (fail-legible)

This manifest is honest about its own gaps, the way `index.md` is honest about
deferred articles. The four tiers exist as declared scope; only two have content
on disk this run.

| Tier | `raw/` location | Mirrored? | State on disk (2026-06-21) |
|---|---|---|---|
| `searles` | `raw/searles/` | **Yes** | `all-posts-1.md` present (43 posts) |
| `first_party` | (read in place — see below) | **No local mirror** | read from `docs/dark-factory`; `raw/transpara/` holds only `.gitkeep` |
| `open_brain` | `raw/open-brain/` | **Yes, stale** | `2026-{03,04,05,06}.md` — 1,175 thoughts, 2026-03-03 through 2026-06-13; live OpenBrain checked 2026-06-21 reports 2,338 thoughts and June 21 captures |
| `upstream_context` | `raw/investigations/` | **No** | empty but for `.gitkeep` — Phase 2 (per `DESIGN.md`) |

**What this means for trust:** the `searles` tier and the stale `open_brain`
mirror are reproducible from this repo alone today. The `first_party` corpus was
read **in place** from a sibling checkout (Run-1 compiled the arc spine directly
against `docs/dark-factory` rather than copying it into `raw/transpara/` first);
the `open_brain` tier **has a committed mirror** (`raw/open-brain/2026-{03..06}.md`,
1,175 thoughts, 2026-03-03 through 2026-06-13) but is **not current with the live
store** as of 2026-06-21, while `upstream_context` is still **declared but
unfilled**. Do not read an empty
`raw/` subdirectory as "no such source" — read it as "not yet mirrored." The
nightly keep-current job in `DESIGN.md` is what will populate them.

---

## Tier: searles — the day-one provocation

The foundational philosophy: Matt Searles' lovyou.ai / LovYou Substack posts. In
`DESIGN.md` this is the `searles` tier — "the foundational philosophy," ingested
as **motive, vocabulary, and accountability premise only**, never as proven
metaphysics or implementation authority (see `wiki/primitive-basis.md`).

| Field | Value |
|---|---|
| **File** | `raw/searles/all-posts-1.md` |
| **Origin** | External — Matt Searles' Substack (`mattsearles2.substack.com`). Generated from the Substack archive API and the canonical post pages (per the file's own header). Authored by Matt Searles (+Claude). |
| **Date / range** | **2026-02-28 → 2026-03-24**. The arc's day one is the 2026-02-28 post *"20 Primitives and a Late Night."* |
| **Volume** | **43 posts** in one concatenated markdown file (~9,800 lines). Each post carries its title, date, and source URL inline. |
| **Tier** | `searles` |
| **How the wiki uses it** | The grounded source for the 8 Foundational articles (`wiki/the-20-primitives.md`, `the-primitives.md`, `strange-loop.md`, `three-irreducibles.md`, `event-graph.md`, `intelligence-is-an-operation-type.md`, `authority-layer.md`, `accountable-ai-architecture.md`) and for `wiki/primitive-basis.md`. It is also the **only** evidence for the reconstructed "Feb genesis" (`DESIGN.md` §"The Feb genesis"): day one predates the first fork and the runtime, so the origin article is reconstructed from these posts + their dates, **not** derived from commit history — and says so. |

**Fail-legible notes (searles):**
- **Count discrepancy.** `DESIGN.md` estimates "the ~45–50 lovyou.ai posts" (and
  "~45–50" in its layout note); the file on disk contains **43** dated posts. The
  manifest records the verified on-disk count (43); the ~50 figure is an estimate,
  not a contradiction to resolve by editing the source.
- **Range vs. the prompt.** This export runs **2026-02-28 → 2026-03-24**. ("From
  2026-02-28 onward" is correct as a start; the captured window currently ends
  2026-03-24 — later posts, if any, are not yet mirrored.)
- **Single-file export.** All posts live in one `all-posts-1.md`. The trailing
  `-1` implies a paginated export scheme; only part 1 exists today. If the archive
  grows, expect `all-posts-2.md` etc., not edits to this file.
- **Repo-identity tension carried into the wiki.** The Searles posts name
  `mind-zero-five`; the first-party docs name `transpara-ai/eventgraph`. The wiki
  does **not** assert these are the same repo (see `index.md` freshness header and
  `wiki/event-graph.md`).

---

## Tier: first_party — the dark-factory docs (read in place)

The Transpara-authored design record: the **dark-factory** documentation set. In
`DESIGN.md` this is the `first_party` tier ("Transpara-authored — docs,
df-impl-v*, dark-factory, Open Brain"). For Run-1 it was read **in place** from a
sibling checkout — **not** copied into `raw/transpara/` (which holds only
`.gitkeep`). This is the load-bearing implementation/doctrine authority for every
Architecture and Arc article.

| Field | Value |
|---|---|
| **Origin** | First-party — `transpara-ai/docs` repo (git remote `origin = git@github.com:transpara-ai/docs.git`; `upstream = transpara/docs`, push disabled). Read at the local checkout `/Transpara/transpara-ai/data/repos/docs/dark-factory/`. |
| **Read location** | `docs/dark-factory/` — **read in place, not mirrored.** The wiki's own `raw/transpara/` is empty this run. |
| **Date / range** | Active corpus. Repo first commit 2022-07-07; the dark-factory record set spans roughly **2026-04 → 2026-06-13** (latest dark-factory commit on disk: 2026-06-13). Dated arc stations run from the 2026-05-13 v3.9 acceptance-candidate checkpoint through the 2026-06-12 v4.0 doctrine-acceptance checkpoint. |
| **Volume** | **~322 markdown files** under `docs/dark-factory/` (excluding `.git`). Run-1 read the arc-spine subset, not all 322. |
| **Tier** | `first_party` |
| **How the wiki uses it** | The grounded authority for the 12 Architecture articles and the 5 Arc articles in `index.md`, and the corrective to assumption-driven narrative (the article set EMERGES from these docs, per `DESIGN.md`). Where it conflicts with the `searles` tier, the wiki states the disagreement and cites both rather than picking a winner (fail-legible doctrine). |

**Key documents within this tier (and how each is used):**

| Document (relative to `docs/dark-factory/`) | Role | Used by |
|---|---|---|
| `Dark Factory - Motive, Goal, Approach.md` | Orientation — states motive, goal, approach, expected flow, control boundaries, and the technology/source categories. The "read this first" doc. (~572 lines.) | `wiki/the-civilization.md`, `wiki/v3-9.md`; the framing for the whole Arc tier |
| `README.md` | Index of the dark-factory record set — points at Motive/Goal/Approach, the reorganization workstream, and the reunification workstream. (~118 lines.) | Navigation / cross-link source for the Arc articles |
| `civic-roles.md` | The nine civic roles enumerated and scoped (strategist, planner, implementer, reviewer, guardian, cto, spawner, allocator, sysmon). **Marked `status: superseded`** — superseded by `docs/roles-catalog.md` (a strict superset). (~54 lines.) | `wiki/civic-roles.md`, `wiki/the-civilization.md` |
| `v3.9/` | The **operative baseline** (accepted 2026-06-05): document governance, unified architecture decisions, kernel schema, authority/identity/SOPs, production workflow, verification/audit/risk/eval, memory/knowledge/capability, tech-debt register, implementation checklist, legacy coverage matrix, plus the 2026-05-13 acceptance-candidate and 2026-06-05 acceptance checkpoints. | `wiki/v3-9.md`, `wiki/gates.md`, `wiki/factory-order.md`, `wiki/work.md`, and most Architecture articles |
| `v4.0/` | **Candidate doctrine** (seed accepted 2026-06-12): "the development process is itself a governed Civilization function — the factory builds the factory," plus the 2026-06-12 doctrine-acceptance checkpoint. **Proposal-only; does not supersede v3.9.** | `wiki/v4-0.md`, `wiki/capability-evolution.md` |
| `reunification/` | The 2026-06-05-opened reunification workstream — slice-1 design (06-05), shepherd-the-society (06-07), run findings (06-08), deployment arc (06-09), execution plan (06-10), arc-state logs (06-11/06-12), take-4 round log, and the shepherd runbook. Demonstration-first, unaccepted as v4.0 doctrine. | `wiki/the-reunification.md`, `wiki/the-drift.md`, `wiki/the-civilization.md` |
| `v3.9/implementation/epics/02-technology-decision-crosswalk-v3.9.md` | **The tech crosswalk** — *Dark Factory v3.9.1 External Technology Decision Crosswalk* (`doc_id: DF-V3.9-EPIC-TECH-CROSSWALK`). Maps the design's needs onto external technology choices. Frontmatter `status: review`, `canonical: false`. | Technology grounding for Architecture articles; cited where the wiki names concrete tech |

**Fail-legible notes (first_party):**
- **Not mirrored into `raw/`.** The biggest provenance caveat in this tier: Run-1
  read `docs/dark-factory` **in place**, so the wiki repo cannot today reproduce
  the first-party tier from its own `raw/transpara/`. `DESIGN.md`'s keep-current
  job ("re-sync first-party repos into `raw/`") is what closes this gap; until it
  runs, treat `docs/dark-factory` as an external dependency of the compile.
- **`civic-roles.md` is superseded.** It is named as a key doc and is grounded,
  but it points forward to `docs/roles-catalog.md` as the canonical superset. The
  wiki's nine-role count is corroborated by code (`StarterAgents()` in
  `pkg/hive/agentdef.go`) per `index.md`; `civic-roles.md` is the doc-side source,
  not the last word.
- **Tech crosswalk is `canonical: false`, `status: review`.** Cite it as a
  decision-record-in-review, not as accepted doctrine.
- **Partial read.** ~322 files exist; Run-1 read the arc-spine subset. The "full
  corpus sweep" remains deferred (see `index.md` §Deferred).
- **Scope boundary.** `first_party` is `transpara-ai` only. The `upstream` remote
  (`transpara/docs`) is never pushed to and never re-published from here.

---

## Tier: open_brain — the captured-thought export

The Open Brain corpus: Michael's captured thoughts, to be exported as dated
markdown. In `DESIGN.md` this is folded into `first_party` authorship but tracked
as its own ingestion stream (`open_brain`), with its own `raw/` subdirectory and
its own nightly re-export.

| Field | Value |
|---|---|
| **Target location** | `raw/open-brain/` — **filled but stale**: `2026-{03,04,05,06}.md`, one dump per month (1,175 thoughts). |
| **Origin** | First-party — the Open Brain thought store (captured via `mcp__open-brain__capture_thought`), to be dumped as dated markdown, one record per thought. |
| **Date / range** | The committed mirror covers **2026-03-03 → 2026-06-13**. `DESIGN.md` still says "Open Brain starts 3/4"; that is treated here as the design/store-open claim, while 2026-03-03 is the actual first date present in the committed mirror. Live OpenBrain access on 2026-06-21 confirms recent captures on **2026-06-21**. |
| **Volume** | **1,175 thoughts on disk** in the committed mirror. Live `thought_stats` checked 2026-06-21 reports **2,338 total thoughts**. |
| **Tier** | `open_brain` |
| **How the wiki uses it** | Phase-1 source alongside `searles` + `first_party` (`DESIGN.md`: "Phase 1 = searles + first_party + open_brain — the arc itself"). Run-1 reached Open Brain via targeted queries to ground specific arc facts (e.g. the earliest spawn-lifecycle thoughts naming `lovyou-ai-hive`, cited in `wiki/agent.md` / `wiki/hive-governance.md`), and the **bulk dated export is now written to `raw/open-brain/`** (4 monthly dumps, 1,175 thoughts, 2026-03-03 through 2026-06-13). |

**Fail-legible notes (open_brain):**
- **Exported 2026-06-13.** `raw/open-brain/` holds 4 monthly dumps (`2026-03..06.md`,
  1,175 thoughts), committed and on `main`. The dated export named in `DESIGN.md` is a
  **completed** ingestion, not a planned one. Articles may still cite individual thoughts
  pulled at compile time, but a committed mirror now exists.
- **Behind live store (as of 2026-06-21).** The committed dump covers through
  2026-06-13. Live `thought_stats` through the standardized OpenBrain helper reports
  **2,338 total thoughts** and recent rows through **2026-06-21**. `DESIGN.md`'s
  "nightly re-export" is **not yet automated**, so this repo must not imply that the
  mirror is current.
- **Standard access path.** Codex/OpenBrain work for this repo uses
  `/Transpara/transpara-ai/data/repos/docs/tools/openbrain-capture/openbrain_capture.py`
  with `/Transpara/transpara-ai/data/repos/OB1/.openbrain.env` as the configuration
  source. The env file supplies `MCP_SERVER_URL`, `MCP_ACCESS_KEY`, and
  `SUPABASE_PROJECT_REF`; secret values are never copied into this repo.
- **MCP read ceiling verified.** `list_thoughts(limit=1000)` and
  `list_thoughts(limit=5000)` both returned exactly **1,000** entries on 2026-06-21.
  MCP is therefore suitable for capture, stats, search, and bounded recent reads, but
  not by itself a complete historical export path.
- **REST export path not live at the documented URL.** The OB1 source tree documents an
  `open-brain-rest` Supabase Edge Function with paginated `/thoughts`, but
  `https://<SUPABASE_PROJECT_REF>.supabase.co/functions/v1/open-brain-rest/{health,stats,thoughts}`
  returned HTTP 404 from this environment on 2026-06-21. Do not claim REST pagination
  or a catch-up dump until that function is deployed/reachable and smoke-tested.
- **Catch-up condition.** Updating `raw/open-brain/` after 2026-06-13 requires a
  paginated/export-capable OpenBrain read path plus the normal secret-scrub gate. This
  PR corrects provenance; it does not add new raw thought dumps.
- **Secret-scrub gate applies.** Per `DESIGN.md`, nothing enters `raw/` with live
  secrets; the Open Brain export must pass the secret scanner before any commit
  (the platform has a known hardcoded-credentials finding, F-01). This is a
  precondition on filling this directory.

---

## Tier: upstream_context — forked-project docs (cited, not re-published)

The forked/investigated upstream projects' **own** documentation — context for the
investigation articles, **not** the subject of the wiki. In `DESIGN.md` this is the
`upstream_context` tier: "a forked project's own docs (context for its
investigation article, **not** the subject of the wiki)," and it is explicitly
**Phase 2**.

| Field | Value |
|---|---|
| **Target location** | `raw/investigations/<project>/` — **empty this run** (only `.gitkeep`). One directory per investigated project. |
| **Origin** | External / upstream — each forked project's public docs (e.g. the `lovyou-ai` lineage and other landscape projects investigated in the 2026-05-13 Civilization Landscape Investigation). |
| **Date / range** | Per-project; recorded when each investigation directory is populated. Not yet applicable. |
| **Volume** | Zero this run — Phase 2, deliberately deferred. |
| **Tier** | `upstream_context` |
| **How the wiki uses it** | Will ground the (currently TBD) per-project **investigation articles** and the standalone **Civilization Landscape Investigation** article and **lovyou.ai fork** article that `index.md` lists as deferred. Used as **cited context only** — quoted to characterize a forked project for its investigation write-up, **never re-published wholesale** into the wiki or committed as a mirror of upstream's repo. |

**Fail-legible notes (upstream_context):**
- **Phase 2, empty by design.** `raw/investigations/` is empty on purpose, not by
  omission. Every forked-project investigation article in `index.md` is therefore
  marked TBD / not-yet-compiled this run.
- **Hard org boundary.** This tier touches upstream (e.g. `lovyou-ai`). The wiki
  **cites** upstream docs as context and **never** re-publishes them or pushes to
  upstream remotes. `upstream_context` is the subject's backdrop, never the wiki's
  subject — and never a write target.

---

## Tier vocabulary (verbatim from `DESIGN.md`)

| Tier | Definition (from `DESIGN.md` §Ingestion) |
|---|---|
| `first_party` | Transpara-authored (docs, df-impl-v*, dark-factory, Open Brain). |
| `searles` | The foundational philosophy. |
| `upstream_context` | A forked project's own docs (context for its investigation article, **not** the subject of the wiki). |
| `open_brain` | (Tracked as its own ingestion stream — the captured-thought export — within first-party authorship.) |

Tier is recorded both here and in each `raw/` file's frontmatter, so the compiler
knows what is load-bearing **without anything being excluded** (`DESIGN.md`:
"ingest all, sort at compile").

---

## How to keep this manifest honest

- When a `raw/` subdirectory is filled (Open Brain export runs; an
  `investigations/<x>/` is added; `docs/dark-factory` is mirrored into
  `raw/transpara/`), update that tier's **Mirrored?** state and its date/volume,
  and flip the "what is NOT mirrored" table above.
- When OpenBrain access changes, verify both paths separately: the standardized MCP
  helper for capture/bounded reads, and any deployed paginated export gateway for bulk
  mirror refresh. Do not treat one as proof of the other.
- Keep counts **verified on disk**, not copied from `DESIGN.md` estimates; where
  they differ (e.g. 43 vs ~50 searles posts), record both and label the estimate.
- A source that is read **in place** rather than mirrored is a provenance caveat,
  not a silent fact — say so, as the `first_party` tier does above.

*Manifest authored 2026-06-13 alongside Run-1. Fail-legible by construction: empty
tiers are declared, not hidden; in-place reads are flagged; estimates are labeled.*
