---
entity: The Transpara-AI Civilization Wiki
aliases: [civilization-wiki, Transpara-AI Civilization Wiki, Karpathy-style wiki, the wiki, the knowledge substrate, the LLM wiki]
tier: meta
status: compiled
last_compiled: "2026-06-24"
sources:
  - DESIGN.md  # substrate design, purpose, pattern, layout, compilation engine
  - PROVENANCE.md  # source manifest: tiers, mirroring status, in-place reads
  - index.md  # front-page narrative frame + arc spine + article index (Run-10 state, 101 articles)
  - raw/open-brain/2026-06.md  # lines 4050–4134: genesis, design decisions, compile runs
  - raw/transpara/dark-factory/v3.9/06-memory-knowledge-capability-v3.9.md  # DF-V3.9-SPEC-006: LLM Wiki advisory knowledge substrate contract
  - compile/refresh.py  # nightly deterministic refresh logic
  - compile/REBUILD.md  # two-tier rebuild protocol
  - compile/build_site.py  # Wikipedia-style renderer, dark/light theme
  - compile/ingest_server.py  # local browser ingest/update/rebuild authoring server
  - README.md  # top-level description (101 articles, Run-10 service hardening)
confidence:
  sources: primary
  claims: grounded
---

# The Transpara-AI Civilization Wiki

**The wiki writing about itself.** The Transpara-AI Civilization Wiki is a [Karpathy-style LLM wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — a single, self-maintaining, interlinked knowledge **substrate** for the Transpara-AI Civilization arc. It compiles the source corpus (the Matt Searles lovyou.ai philosophy posts + the first-party [[dark-factory]] docs + Open Brain captured thoughts + Stage 0 institutional-substrate source material) into a set of pre-synthesized, cross-linked entity articles, so that knowledge **compounds** rather than being re-discovered per query. This article describes the wiki itself: why it exists, how it is built, what state it is in, and what governs it.

## Why it exists

The wiki is the answer to a sequencing decision made on **2026-06-13**. Michael Saucier reprioritized: substrate before visualization. The prior build produced a static Mission Control mockup served on nucbuntu at `:8787` — a disposable HTML/CSS design prototype. That mockup revealed a gap: the visualization had no durable source of truth to render from. The resolution was to build the knowledge substrate first, then treat any downstream visualization (Mission Control, the spine/story view) as a **read lens onto the wiki**, not an independent layer. (`raw/open-brain/2026-06.md` line ~4050.)

The Karpathy pattern solves the **anti-RAG** problem: instead of re-deriving answers from raw documents at query time, the wiki pre-compiles the corpus into encyclopedia articles that cross-link related entities and resolve conflicts. Knowledge accumulates in the articles and compounds across sessions; new queries land on pre-synthesized context, not a flat document pile.

## The pattern

Three directories, one loop:

```
raw/     source material — verbatim, never hand-edited
wiki/    LLM compiles raw into entity articles: synthesize, resolve conflicts, cross-link
index.md front-page narrative + arc spine + article index + freshness header
```

The article set **emerges from the sources** — it is not pre-authored by the maintainer. A first-pass compile derives the entity list from `raw/`; later passes refine. Curation is a compile-time concern, not a gate at the ingestion door ("ingest all, sort at compile," per `DESIGN.md`).

## The corpus it compiles from

Four source tiers, each with its own `raw/` subdirectory and its own provenance claims:

| Tier | Location | Mirrored? | Content |
|---|---|---|---|
| `searles` | `raw/searles/` | Yes | `all-posts-1.md` — 43 Matt Searles posts (2026-02-28 → 2026-03-24) |
| `first_party` | `raw/transpara/` | No local mirror (read in place) | ~322 dark-factory markdown files under `docs/dark-factory/` |
| `open_brain` | `raw/open-brain/` | Partial — 2026-06.md exported | ~1,175 captured thoughts (design estimate); full dump not yet committed |
| `upstream_context` | `raw/investigations/` | No — Phase 2, empty by design | Upstream forked-project docs (cited as context, never re-published) |
| `browser_inbox` | `raw/inbox/` | Yes when used | Local browser-ingested source drops and URL manifest rows awaiting article synthesis |

`DESIGN.md` names the full target corpus as **~8,783 markdown files across ~73 repos + ~1,175 Open Brain thoughts + the Matt Searles posts**. As of Run-3 (2026-06-14) only the `searles` tier is fully reproducible from the repo alone; the `first_party` tier was read in place from a sibling checkout and the `open_brain` tier was queried live or exported as individual month files rather than bulk-dumped. See `PROVENANCE.md` for the per-tier mirroring status.

> ⚠ **Corpus completeness is declared, not verified.** The 8,783-file / 73-repo / 1,175-thought figures come from `DESIGN.md` (2026-06-13 draft). They are the design-time estimate, not an on-disk count. Do not read any empty `raw/` subdirectory as "no such source" — read it as "not yet mirrored."

## The compile runs

The wiki has been compiled in ten passes, each extending the article set or
changing how the substrate is presented:

**Run-1 (2026-06-13):** The core spine — 24 articles covering the Searles source philosophy (foundational tier) and the dark-factory architecture and arc through the 2026-06-05 reunification. Compiled against `raw/searles/` + the first-party dark-factory docs (read in place) + targeted Open Brain queries. ⚠ Token figures for Run-1 are stated in the task framing as ~2.17M across ~28 agents; this article cites those figures but they are not independently corroborated by a captured thought.

**Run-2 (2026-06-13):** +36 articles — the landscape survey, Searles thirteen-graphs / cognitive-grammar philosophy fill-in, and the **fifteen investigation-tier articles** compiled from the 2026-05-13 Civilization Landscape Investigation. Run-2 also corrected a nine-vs-ten civic-roles wording error from Run-1. Article total after Run-2: **61** (12 foundational · 14 architecture · 8 arc · 15 investigation · 12 concept). ⚠ The ~42-agent / ~3.6M-token figure comes from task framing, not an independent captured thought.

**Run-3 (2026-06-14):** ~29 new or updated articles — the deferred long-tail from Run-2's "not-yet-compiled" list (individual thirteen-graphs entries, roles-catalog, observatory, observability, the-work-graph, slice-1-completion, and this meta article among them). Article total after Run-3 was recorded as **78** including this article. ⚠ The Run-3 count is an as-written figure; the exact count of prior Run-3 articles compiled in that workflow pass was not independently verified here — read the current `index.md` for the authoritative count.

**Run-4 (2026-06-24):** institutional-substrate refit — copied the Stage 0 institutional-substrate source snapshot into `raw/civilization/`, added the `institutional` and `meta` tiers, compiled six institutional substrate articles, moved the progress chart off the home page and into `civilization-arc.html`, and converted the home page into an article-first wiki index. Article total after Run-4: **99**.

**Run-5 (2026-06-24):** front-page narrative frame — rewrote `index.md` to begin with the historical and philosophical significance of Michael Saucier's Searles epiphany, Transpara's industrial accountability posture, and the reason the Dark Factory arc matured into the Civilization frame. No new entity articles were added; the article total remained **99**.

**Run-6 (2026-06-24):** search and external-research visibility — added static full-site search, renamed the public chrome to **Transpara-AI Civilization Wiki**, and promoted the Sakana and Hermes Stage 0 research artifacts into first-class advisory wiki pages. Article total after Run-6: **102**.

**Run-7 (2026-06-24):** navigation and Hermes consolidation — widened the left navigation default, added persistent sidebar resizing, removed external research reports and the progress chart from the front-page start table, and consolidated the Hermes Agent / Hermes Self-Evolution / Hermes evaluation surfaces into one unified Hermes Agent article. Article total after Run-7: **100**.

**Run-8 (2026-06-24):** source-serving and browser ingest — added served source-viewer pages for raw/reference material, exposed `sources.html` and `ingest.html` in the top bar, made source documents first-class search results, and added a local authoring server that can batch-ingest documents or URLs into `raw/inbox/`, append selected article source references, and rebuild `dist/`. Article total after Run-8: **100**.

**Run-9 (2026-06-24):** repository catalog — added a generated
Transpara-AI Repos navigation section and `repos.html` index, rendering primary
Transpara-AI repository READMEs as wiki pages with right-column repository
metadata. Forked repositories show local origin-vs-upstream status; native
Transpara-AI repositories show local branch and commit counts. The live user
service was renamed from the temporary `wiki-refit.service` to
`transpara-ai-civilization-wiki.service`. Article total after Run-9 remains
**100**; generated repo pages are repository references, not wiki articles.

**Run-10 (2026-06-24, current):** service hardening and source safety — promoted
the wiki into a first-class local systemd authoring service, added a 15-minute
deterministic freshness timer, restricted remote write authority, hardened upload
path containment, escaped raw HTML in rendered source/README markdown, redacted
non-canonical git remotes, and kept repository/source navigation visible.
Article total after Run-10: **101**; generated repo pages are still repository
references, not wiki articles.

## The compilation engine and house style

Each article is compiled by a Claude Code subagent reading the relevant `raw/` sources (and any sibling wiki articles that provide context), then synthesizing a single entity article in a fixed format:

- **Frontmatter YAML:** `entity`, `tier`, `status`, `last_compiled`, `aliases`, `sources[]`, and a `confidence` block (`sources: primary|secondary|thin`, `claims: grounded|asserted|reconstructed`).
- **Body:** synthesizes sources, uses `[[wikilinks]]` to related entities, uses sentence-case headings.
- **Fail-legible inline notes:** `⚠` prefix for uncertain claims, contested facts, or thin evidence. Source conflicts are stated and both sources cited; the wiki never silently picks a winner.
- **Sources & provenance footer:** lists the exact `raw/` paths (or in-place read paths) and approximate line ranges the article was built from.

The exemplar house style article is `wiki/event-graph.md`.

Articles may not invent facts. When sources conflict, the article states the disagreement. When evidence is thin, the article says "thin" or omits the claim. This is the same **fail-safe-by-default** doctrine that governs the dark-factory platform itself, applied to knowledge compilation.

## The two-tier keep-current protocol

Keeping the wiki current without unattended LLM spend or unattended pushes requires splitting the refresh into two tiers:

**Tier 1 — nightly, deterministic (`compile/refresh.py`, runs ~03:00):**
1. Mirror first-party dark-factory markdown into `raw/transpara/` via `rsync`.
2. Hash all `raw/` sources and diff against the previous snapshot (`compile/source-snapshot.json`).
3. Map changed sources → stale articles (articles whose `sources:` frontmatter cites a changed file).
4. Write `compile/refresh-status.json` — the fail-loud freshness signal displayed in the served site's header.
5. Regenerate the served site in `dist/` via `compile/build_site.py`.

Tier 1 does **not** call an LLM, does not commit, does not push. Open Brain deltas are not auto-detected here (that requires an LLM/MCP run); they are picked up by Tier 2.

**Browser source ingest — local authoring (`compile/ingest_server.py`):**
When the authoring server is running, `/ingest.html` lets a human select one or
more files, paste one or more source URLs, choose a target article, identify an
existing source being superseded, and click one button to ingest and rebuild.
Uploaded documents are written to `raw/inbox/`; external URLs and uploaded files
are recorded in the inbox manifest; selected references are appended to the
target article frontmatter; and the static site is regenerated.

This path registers sources and updates source references only. It does not run
an LLM, rewrite article prose, commit, push, or make a stale article current by
assertion. If new source material changes the substance of an article, a Tier-2
article re-compile is still required.

**Tier 2 — article re-compile, manual (LLM, on demand):**
When `refresh-status.json` flags stale articles — or to fold in the deferred long-tail / new Open Brain history — a human-authorized compile workflow re-synthesizes the affected articles, reviews the output, and merges via PR. No autonomous LLM content writes land in `wiki/` without human review and a PR.

## The served renderer

The wiki is rendered as a **Wikipedia-style static site** by `compile/build_site.py` (Python stdlib + python-markdown, no network). The renderer produces:

- A persistent left sidebar with collapsible article tiers, current-section auto-open, and scroll/expanded-state preservation across article clicks.
- Persistent horizontal resizing for the left sidebar, stored in `localStorage`.
- A static top-bar search box backed by build-time `search-index.js`, with no API or server dependency.
- Top-bar links to the repository index (`repos.html`), source index (`sources.html`), and browser ingest surface (`ingest.html`).
- A generated left-rail **Transpara-AI Repos** section with Civilization, Platform, and Other subsections; each repository page renders the local README and git-derived status.
- Served source-viewer pages under `source/<id>.html`; article source panels and raw-path references link to them.
- Source documents included in the static search index alongside wiki articles.
- Per-page: title, right-floated infobox from frontmatter, auto table of contents, rendered body, "See also," and a bottom category navbox.
- Blue links for resolved `[[wikilinks]]`; red links for TBD forward references.
- Dark/light theme toggle (persisted in `localStorage`).

The first-class authoring service is managed on **nucbuntu at loopback
`http://127.0.0.1:8787`**, not as a LAN write surface:

```
systemctl --user status transpara-ai-civilization-wiki.service
```

The old static `:8787` surface from `/Transpara/transpara-ai/repos/wiki/dist` has
been demoted and archived separately. Static `python3 -m http.server` remains
valid for throwaway previews on alternate ports, but it does not support browser
source ingest. A LAN-visible read route must be a deliberately separate
read-only proxy and must not expose the authoring endpoints or confidential
raw-source/search artifacts by accident.

The renderer was introduced alongside the wiki (PRs #1 and #2 per task framing). ⚠ The PR numbers are cited from the task framing; this article did not independently verify them against the GitHub PR history.

## What the wiki is, and is not

**What it is:**

- The **source of truth for the narrative framing** of the Transpara-AI Civilization arc. Every downstream visualization (Mission Control board, spine/story view, progress chart) is a read lens onto this wiki, not an independent layer.
- A living substrate that **compounds** across sessions: each compile pass deepens the pre-synthesized context available to any future agent or human reader.
- Per `DF-V3.9-SPEC-006` (see `[[memory-knowledge-advisory]]`): an instance of an **LLM Wiki** in the advisory-only sense — compiled knowledge that advises but does not govern. Anything in this wiki is advisory unless validated by EventGraph evidence. The spec's own terminology applies to its own knowledge substrate.

**What it is not:**

- A RAG system. Knowledge is pre-compiled into articles, not retrieved from raw documents at query time.
- A Mission Control board or real-time status dashboard. Those are downstream read lenses.
- A re-publication of upstream source material. The `upstream_context` tier cites upstream docs as context for investigation articles; it never re-publishes them wholesale.
- Governance or policy. No wiki article is certification evidence, authority record, or event-graph entry. The advisory boundary is strict.
- A browser button that silently rewrites doctrine. Browser ingest can add and serve source references; article synthesis remains an explicit Tier-2 compile.

## Guard rails carried from the platform

The wiki inherits the platform's fail-safe-by-default doctrine:

- **No secrets, no credentials** in `raw/` or `wiki/`. The `raw/` ingestion must pass a secret scanner before any commit (known hardcoded-credentials finding F-01 in the platform; non-negotiable gate).
- **No `DROP`, `TRUNCATE`, or destructive SQL** in schema files.
- **No binaries** over 1 MB.
- **No confabulation.** Thin evidence is labeled thin. Contested claims carry both sides.

## Scope and governance

- **Repo:** `transpara-ai/wiki` (private). Never touch `lovyou-ai` / upstream; `upstream_context` quotes public docs as cited context, never re-publishes or pushes.
- **Compile runs:** manual, human-authorized, reviewed as PRs before merge. Article content is not written autonomously without human review.
- **Air-gap friendly:** compile runs locally on nucbuntu; only dependency is a local LLM (Claude Code).
- **Org boundary:** transpara-ai only.

## What is deferred

The `index.md` deferred list (Run-2) named:
- The full corpus sweep (~8,783 files / ~73 repos / ~1,175 thoughts — not yet exhausted).
- `open_brain` and `upstream_context` raw tiers — declared but unmirrored.
- Granular forward-referenced entities (authority-request, execution-receipt, bounded-runtime, remaining individual thirteen-graphs entries, slice-1-first-reunified-order).
- The `mind-zero` / `mind-zero-five` repo identity disambiguation.

Run-3 addresses a portion of the deferred long-tail. The remaining deferred entities stay as legitimate forward-refs until a future compile pass covers them.

## Sources & provenance

Compiled from:

- `/Transpara/transpara-ai/repos/wiki/DESIGN.md` — purpose, pattern, layout, corpus scope, compilation engine, keep-current design, Feb genesis section. Full file (~77 lines).
- `/Transpara/transpara-ai/repos/wiki/PROVENANCE.md` — per-tier manifest: origin, date/range, volume, mirroring status, fail-legible tier caveats. Full file (~213 lines).
- `/Transpara/transpara-ai/repos/wiki/index.md` — front-page narrative frame, arc spine, article index, freshness header, and deferred/source-tension notes. Current Run-10 state: 101 articles.
- `/Transpara/transpara-ai/repos/wiki/raw/open-brain/2026-06.md` — lines ~4050–4134: genesis of the Karpathy-wiki direction, design decisions, compile progress captures (lines 4050, 4052, 4066, 4072).
- `/Transpara/transpara-ai/repos/wiki/compile/refresh.py` — Tier-1 nightly deterministic refresh implementation. Full file (~102 lines).
- `/Transpara/transpara-ai/repos/wiki/compile/REBUILD.md` — two-tier rebuild protocol plus browser source-ingest documentation. Full file.
- `/Transpara/transpara-ai/repos/wiki/compile/build_site.py` — Wikipedia-style renderer: collapsible sidebar, infobox, dark/light theme, blue/red wikilinks, source pages, source index, ingest surface, and generated repository pages. Full file.
- `/Transpara/transpara-ai/repos/wiki/compile/ingest_server.py` — local authoring server for file/URL ingest, source-reference append, and rebuild. Full file.
- `/Transpara/transpara-ai/repos/wiki/README.md` — top-level description, principles, Run-10 status, and layout. Full file.

**Fail-legible conflicts and caveats carried into this article:**
- Run-1/Run-2 token and agent counts (2.17M/28 and 3.6M/42) come from task-framing metadata, not independently captured thoughts — labeled as such.
- Run-3 article count (78 total) is an as-written historical figure; the authoritative current count is the generated stats block in `index.md`.
- PR #1 and PR #2 cited for the renderer are from task framing; not independently verified against GitHub history.
- Corpus size estimate (~8,783 files / ~73 repos / ~1,175 thoughts) is the `DESIGN.md` design-time figure, not an on-disk count.
