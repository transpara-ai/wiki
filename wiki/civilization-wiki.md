---
entity: Transpara Knowledge Hub
org: transpara-ai
primary_placement: civilization/meta
placements:
  - civilization/meta
classification: internal
aliases: [civilization-wiki, The Transpara-AI Civilization Wiki, Transpara-AI Civilization Wiki, Civilization Wiki, Karpathy-style wiki, the wiki, the knowledge substrate, the LLM wiki]
tier: meta
status: compiled
last_compiled: "2026-09-08"
source_authority:
  - engineering-docs
sources:
  - README.md
  - DESIGN.md
  - PROVENANCE.md
  - index.md
  - spaces/civilization/index.md
  - spaces/platform/index.md
  - spaces/competition/index.md
  - spaces/devops/index.md
  - compile/knowledge_structure.json
  - compile/repository_routes.json
  - API.md
  - DOCKER.md
  - raw/open-brain/2026-06.md  # genesis, design decisions, early compile runs
  - raw/transpara/dark-factory/v3.9/06-memory-knowledge-capability-v3.9.md  # original Civilization advisory knowledge contract
  - compile/refresh.py
  - compile/REBUILD.md
  - compile/build_site.py
  - compile/ingest_server.py
confidence:
  sources: primary
  claims: grounded
---

# Transpara Knowledge Hub

The Transpara Knowledge Hub compiles source material into interlinked articles
for **Civilization**, **Transpara Platform**, **Competition**, and **DevOps**.
It began as the Transpara-AI Civilization Wiki and now serves all four spaces
through one canonical article graph. This overview retains the original
`civilization-wiki` slug and Civilization meta placement so existing references
continue to resolve.

## Knowledge spaces

| Space | Purpose | Starting article |
| --- | --- | --- |
| [Civilization](civilization/index.html) | Philosophy, institutional architecture, history, research, and operational learning; stewarded by Transpara-AI | [[the-civilization]] |
| [Transpara Platform](platform/index.html) | Product portfolio, capabilities, architecture, components, integrations, deployment, security, and APIs; stewarded by Transpara | [[transpara-platform-overview]] |
| [Competition](competition/index.html) | Commercial market intelligence, competitor profiles, comparisons, positioning, and win/loss evidence; stewarded by Transpara | [[competition-overview]] |
| [DevOps](devops/index.html) | Infrastructure, networking, containers, delivery automation, observability, and runbooks; stewarded by Transpara | [[devops-repository-scaffold]] |

Visual KPI is one product in the Platform portfolio. Competition distinguishes
external competitor facts from Transpara's first-party positioning. DevOps
currently starts with repository engineering and delivery sources; other
operational runbooks require their own evidence.

The root portal is `index.md`. Space homes live under `spaces/`; the Civilization
board and Arc remain in the Civilization space. An article has one steward, one
primary placement, and explicit additional placements when it serves several
spaces. Its body and flat HTML route remain canonical. Space totals can overlap;
the global article count counts each article once.

## Why it exists

The original sequencing decision on **2026-06-13** was to build the knowledge
substrate before the visualization. A Mission Control mockup needed durable,
sourced narrative to render. Michael Saucier's resolution was to compile the
Civilization knowledge first and treat visualizations as read views onto it.
The June Open Brain export records that decision around lines 4050–4134.

The same pattern now supports product, competitive, and operational knowledge:
source evidence is synthesized into articles that accumulate context across
sessions. The Hub remains advisory. Code, versioned configuration, accepted
decisions, release systems, customer systems, and EventGraph retain their
respective authority. See [[memory-knowledge-advisory]] for the original
Civilization knowledge contract.

## Sources and compilation

```text
raw/       captured sources and provenance evidence
wiki/      canonical articles synthesized from sources
index.md   shared Knowledge Hub portal
spaces/    space-specific homes and navigation
compile/   registry, catalog, renderer, refresh, and authoring services
```

The original Civilization corpus includes Searles philosophy, Dark Factory and
runtime documentation, Open Brain exports, Stage 0 snapshots, and external
research. Platform adds product and engineering sources; Competition adds dated
primary-source competitor evidence and labeled first-party positioning; DevOps
adds versioned configuration, engineering procedures, and operational evidence.

Historical raw paths remain valid. New uploads use
`raw/inbox/<space>/<date>/<article>/`. Sources can also be read from sibling
repositories or cited by URL; neither case implies a committed snapshot. The
provenance manifest records source origins and dated coverage gaps. Its older
corpus counts and Civilization-only boundaries describe their recorded dates,
not the full current Hub or an automatically synchronized source inventory.

Article frontmatter records `entity`, `org`, `primary_placement`, `placements`,
`classification`, status, compilation date, and sources. Registered
`source_authority` values and review dates distinguish source roles and
freshness. Bodies synthesize evidence, link related articles with wikilinks,
and state conflicts or thin evidence explicitly. The registry in
`compile/knowledge_structure.json` defines valid spaces and publication profiles.

## The compile runs

The first ten recorded passes built the Civilization corpus. These dated
counts describe those runs, not the current Hub inventory:

**Run-1 (2026-06-13):** The core spine — 24 articles covering the Searles source philosophy (foundational tier) and the dark-factory architecture and arc through the 2026-06-05 reunification. Compiled against `raw/searles/` + the first-party dark-factory docs (read in place) + targeted Open Brain queries. ⚠ Token figures for Run-1 are stated in the task framing as ~2.17M across ~28 agents; this article cites those figures but they are not independently corroborated by a captured thought.

**Run-2 (2026-06-13):** +36 articles — the landscape survey, Searles thirteen-graphs / cognitive-grammar philosophy fill-in, and the **fifteen investigation-tier articles** compiled from the 2026-05-13 Civilization Landscape Investigation. Run-2 also corrected a nine-vs-ten civic-roles wording error from Run-1. Article total after Run-2: **61** (12 foundational · 14 architecture · 8 arc · 15 investigation · 12 concept). ⚠ The ~42-agent / ~3.6M-token figure comes from task framing, not an independent captured thought.

**Run-3 (2026-06-14):** ~29 new or updated articles — the deferred long-tail from Run-2's "not-yet-compiled" list (individual thirteen-graphs entries, roles-catalog, observatory, observability, the-work-graph, slice-1-completion, and this meta article among them). Article total after Run-3 was recorded as **78** including this article. ⚠ The Run-3 count is an as-written figure; the exact count of prior Run-3 articles compiled in that workflow pass was not independently verified here — read the generated Hub and space totals for current counts.

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

**Run-10 (2026-06-24):** service hardening and source safety — promoted
the wiki into a first-class local systemd authoring service, added a 15-minute
deterministic freshness timer, restricted remote write authority, hardened upload
path containment, escaped raw HTML in rendered source/README markdown, redacted
non-canonical git remotes, and kept repository/source navigation visible.
Article total after Run-10: **101**; generated repo pages are still repository
references, not wiki articles.

**July keep-current cycle (2026-07-12/13):** governed PR-cycle
additions rather than a numbered run — the Open Brain July 1–12 export (with
the named Jun 14→30 gap recorded in `PROVENANCE.md`), four hive
guardrail-cycle architecture/arc articles, and repo-wide truth-ups of corpus
and freshness claims. Article totals from this cycle onward are maintained by
generated catalog and space counts, not by run notes. Civilization's durable
stats block now lives in `spaces/civilization/index.md`.

**September expansion:** the September 5 migration added the shared portal,
Transpara Platform, and Competition while preserving all 108 original article
routes. DevOps followed as the fourth space, including its repository
engineering corpus and an API lane for creating sourced articles. The 108-route
figure is the migration baseline, not the current article total.

## Refresh and authoring

**Deterministic refresh** runs every 15 minutes through the native timer or
Docker worker. It mirrors configured Dark Factory Markdown into
`raw/transpara/dark-factory/`, hashes raw Markdown and the archive boundary
marker, records cited source changes, updates Civilization's generated stats,
and rebuilds the eligible spaces. It does not call an LLM, commit, or push.
Platform, Competition, DevOps, and Open Brain source synchronization remains an
explicit import/review task.

**Source registration** through Ingest works across all four spaces. The active
space supplies the space and steward; a target article must already have the
chosen placement. Uploaded files, URLs, and pasted text become source evidence.
Newly attached evidence sets `stale_since` so a successful render does not imply
that article prose has incorporated it.

**Article creation** has two API lanes: provisional Civilization investigations
from a seeding document, and internal DevOps drafts from supplied Markdown and
sources. Platform and Competition article creation, placement changes, and
general prose edits use repository edits and review. The API saves supplied
DevOps prose without synthesizing the sources. `API.md` documents the fields and
retry behavior.

**Manual synthesis** reviews evidence and updates article content. After
incorporating new sources, update `last_compiled` and clear `stale_since`.
`changed_articles` in refresh status records sources that were rendered;
`stale_articles` records an unsuccessful deterministic rebuild that needs retry.
These fields are separate from an article's pending prose synthesis. See
`compile/REBUILD.md` for the operational procedure.

## Rendering and hosting

The static renderer provides a space switcher, local sections, shared-article
placements, source links, repository references, dark/light themes, and search.
Repos, Sources, and Ingest retain the selected space; search offers **All spaces**
within the publication profile. Repository pages discover local clones and
worktrees. Registered repository URLs persist with an availability notice when
a checkout is absent.

Publication profiles determine what is included:

- `authoring-local` includes the authorized internal corpus, sources, repository
  pages, Arc, and authoring controls.
- `company-internal` includes eligible `company-internal` and `public-candidate`
  articles without source viewers, repository mirrors, Arc, or mutation controls.
- `public-platform` is disabled pending a separate publication decision.

The original Civilization corpus and current DevOps articles are `internal`;
the initial reviewed Platform and Competition articles are `company-internal`.
A space's existence does not broaden its publication audience.

The native authoring service binds to `127.0.0.1:8787`:

```bash
systemctl --user status transpara-knowledge-hub.service
```

Docker hosting uses the same Hub through private Tailscale HTTPS, with one writer
and one refresh worker sharing the checkout lock. `DOCKER.md` describes that
deployment; `compile/REBUILD.md` covers the native service and compatibility
migration. Old Civilization service/environment names and the
`X-CivWiki-Authoring-Token` header remain documented compatibility interfaces.

## Sources and historical caveats

- `README.md`, `DESIGN.md`, the portal, space homes, and knowledge structure
  registry describe the current four-space scope and article model.
- `PROVENANCE.md` records evidence origins and dated coverage; a missing mirror
  is not proof that a source or article does not exist.
- `API.md`, `compile/REBUILD.md`, and `DOCKER.md` describe authoring and operation;
  the refresh, builder, authoring server, and repository route catalog establish
  the implemented behavior.
- The June Open Brain export grounds the original substrate decision. The
  original memory/knowledge specification grounds the Civilization advisory
  contract.
- Early run article counts are historical. Run-1/Run-2 token and agent counts and
  the Run-3 total were not independently corroborated; their caveats remain with
  the run notes above.
