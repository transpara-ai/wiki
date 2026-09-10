# Transpara Knowledge Hub — design

**Status:** current implementation reference · **Updated:** 2026-09-08

## Purpose and spaces

The Transpara Knowledge Hub is a compiled, interlinked knowledge system spanning
Civilization, Transpara Platform, Competition, and DevOps. It grew from the
Civilization wiki into one canonical article graph with several reader views.

| Space | Steward | Knowledge scope |
| --- | --- | --- |
| Civilization | `transpara-ai` | Philosophy, institutional architecture, history, research, and operational learning, including the Dark Factory arc |
| Transpara Platform | `transpara` | Product portfolio, capabilities, architecture, components, integrations, deployment, security, development, and operations |
| Competition | `transpara` | Market categories, competitors, comparisons, positioning, objections, win/loss evidence, and research methods |
| DevOps | `transpara` | Infrastructure, networking, containers, delivery automation, observability, runbooks, security, decisions, and incidents |

[The registry](compile/knowledge_structure.json) defines space keys, sections,
stewards, classifications, source authorities, and publication profiles. Stewardship
identifies responsibility for content; it need not match a source repository's
GitHub organization. DevOps, for example, is stewarded by Transpara and currently
cites the `transpara-ai/dev-ops` repository engineering corpus.

The Hub is advisory. Running code, versioned configuration, accepted decisions,
release and customer systems, and EventGraph retain their respective authority.
Articles explain and connect evidence; publication does not promote a proposal
into an accepted decision or establish current runtime state.

## Layout and reader views

```text
index.md                         shared Knowledge Hub portal
spaces/civilization/index.md      Civilization home and board
spaces/platform/index.md          Transpara Platform home
spaces/competition/index.md       Competition home
spaces/devops/index.md            DevOps home
wiki/<slug>.md                   canonical article bodies and metadata
raw/                             captured sources and ingestion evidence
compile/knowledge_structure.json  space, stewardship, and publication registry
compile/repository_routes.json    persistent published repository identities
compile/                         catalog, renderer, refresh, and authoring services
PROVENANCE.md                     source origins, dated coverage, and gaps
docs/                            documentation index and dated design/evidence records
```

The root renders at `/index.html`; space homes render at `/<space>/index.html`.
Articles keep flat routes such as `/event-graph.html` and
`/transpara-platform-overview.html`, even when they have several placements.
The original `/civilization-wiki.html` route now describes the expanded Hub.
The Civilization board and Arc remain Civilization views, with existing Arc
aliases preserved.

Selecting a space scopes the sidebar, search, Repos, Sources, and Ingest.
Search offers **All spaces** within the selected publication profile. Shared
articles have one body and one canonical route; global totals count each article
once, while space totals count its placements in that space.

Repository pages use local clones and worktrees, filtered by the space's
steward. The versioned route catalog preserves registered URLs when a checkout
is unavailable. Such pages show the source repository and an availability notice;
local README content and Git metadata resume when the checkout returns.

## Corpus scope

The June 2026 design bounded the original Civilization corpus to the Searles
posts, Dark Factory documentation and runtime repositories, implementation
snapshots, Open Brain exports, and cited investigation context. Its exclusion of
Transpara's product line applied to that initial Civilization scope. Product,
competitive, and operational knowledge are now explicit Hub subjects.

| Space | Source basis and interpretation |
| --- | --- |
| Civilization | Searles philosophy, first-party Dark Factory and runtime docs, implementation history, Open Brain exports, Stage 0 snapshots, and cited external research. Preserve proposal, historical, and accepted-state distinctions. |
| Transpara Platform | Product and component repositories, versioned configuration, accepted ADRs, engineering documentation, and approved product references. Distinguish implemented behavior, normative decisions, plans, and marketing. Visual KPI is one product in the portfolio. |
| Competition | Current external primary sources for competitor facts; separately labeled Transpara first-party positioning for comparisons and sales interpretation. Time-sensitive claims carry verification and review dates. |
| DevOps | Versioned infrastructure and delivery configuration, repository engineering docs, operational evidence, incident records, and runbooks. Distinguish observed running state from desired configuration and unvalidated procedures. |

Ingest broadly within the relevant scope and synthesize curatively. Source
registration is not automatic publication or proof that an article reflects its
new evidence. A repository's presence on the local host does not automatically
make its full contents part of the article corpus.

Customer production content, credentials, and unauthorized prospect evidence
remain outside the knowledge boundary. Dependency trees, vendored documents,
Git internals, and duplicate worktrees are not bulk source imports. External
research is cited with provenance; this repository does not mirror entire
upstream projects or write to their remotes.

### Source storage and provenance

Historical sources retain their paths under `raw/searles/`, `raw/transpara/`,
`raw/open-brain/`, `raw/civilization/`, and `raw/investigations/`. New uploads use
`raw/inbox/<space>/<date>/<article>/`; legacy inbox paths remain valid. Source
placement in an article is explicit and does not require moving raw files.

The provenance tiers in [PROVENANCE.md](PROVENANCE.md) describe source origin and
ingestion history, including `first_party`, `searles`, `open_brain`,
`civilization_stage0`, `external_landscape_authored`, `browser_inbox`, and
`upstream_context`. They are distinct from reader spaces, article `tier`, and
registered `source_authority` values. First-party sources can support any space;
external-primary-source evidence supports both research and commercial comparison.

Article `sources` and `raw_documents` identify the evidence actually used,
including local snapshots, sibling-repository paths, and external URLs. Record
revisions and dates where available. URL registration does not fetch a snapshot;
an in-place read does not establish a committed mirror. Preserve the dates and
coverage gaps in the provenance manifest rather than treating old corpus counts
as a current inventory. Existing ingestion quarantine and pre-commit secret
scanning apply to every space.

## Article model and authoring

Articles stay in `wiki/<slug>.md`. Each has one steward (`org`), one
`primary_placement`, and an explicit `placements` list that includes its primary
placement. For example:

```yaml
entity: Transpara MCP Boundary
org: transpara
primary_placement: platform/development-apis
placements:
  - platform/development-apis
  - civilization/architecture
classification: company-internal
source_authority:
  - engineering-docs
```

The catalog validates registry values before distribution output changes.
Classification controls publication eligibility independently of placement.
Articles also record status, compilation date, sources, and any relevant
verification/review dates. Content uses `[[article-slug]]` links between canonical
articles and cites the evidence behind substantive claims. Conflicts and thin
evidence are stated explicitly.

Source attachment works for existing articles in every space. The browser's
new-investigation lane creates internal provisional Civilization investigations.
The API additionally creates internal DevOps drafts from supplied Markdown and
sources. Platform and Competition article creation, general prose changes, and
placement changes use repository edits and review. The endpoint never synthesizes
source contents automatically. [API.md](API.md) documents the supported fields
and retry behavior.

## Refresh and synthesis

The current keep-current process has two tiers:

1. **Deterministic refresh:** the 15-minute worker mirrors configured Dark Factory
   Markdown into `raw/transpara/dark-factory/`, hashes raw Markdown and the archive
   boundary marker, records cited changes, updates Civilization's generated stats,
   and rebuilds all eligible spaces. It neither calls an LLM nor commits or pushes.
2. **Manual synthesis:** review changed evidence, revise affected article prose,
   update `last_compiled`, and clear `stale_since` when the synthesis is complete.
   Browser/API source registration marks newly attached evidence as pending;
   rendering alone does not incorporate it into the prose.

The four-space expansion does not add automatic Platform, competitor, DevOps,
or Open Brain source synchronization. Those imports and reviews remain explicit.
See [the rebuild guide](compile/REBUILD.md) for freshness fields, locking,
source registration, and service operation.

## Publication and hosting

| Profile | Content and surfaces |
| --- | --- |
| `authoring-local` | All authorized internal spaces, source viewers, repository pages, Arc, and authoring controls |
| `company-internal` | Articles classified `company-internal` or `public-candidate`; excludes raw source viewers, repository mirrors, Arc, and authoring controls |
| `public-platform` | Disabled; any future output is limited to eligible Platform content and requires a separate publication decision |

Space membership does not make content public. The original Civilization corpus
and current DevOps articles are `internal`; the initial reviewed Platform and
Competition articles are `company-internal`. A `public-candidate` classification
alone does not enable public publication.

The local authoring service binds to `127.0.0.1:8787`. The
[Docker deployment](DOCKER.md) serves the same Hub through private Tailscale HTTPS;
[the native service guide](compile/REBUILD.md) covers systemd. Canonical names use
`transpara-knowledge-hub*` and `KNOWLEDGE_HUB_*`. Historical
`transpara-ai-civilization-wiki*` units, `CIVWIKI_*` fallbacks, and the
`X-CivWiki-Authoring-Token` header remain compatibility interfaces as documented
in those guides.

## Design history

The 2026-06-13 draft established the Civilization knowledge substrate before its
visualizations. Its corpus estimates, proposed nightly LLM compilation, and open
setup questions describe that starting point. Current behavior is documented
above and in the implementation; historical coverage stays dated in
[PROVENANCE.md](PROVENANCE.md).

The [2026-09-05 migration plan](docs/superpowers/plans/2026-09-05-multi-space-wiki-migration.md)
records the initial expansion into Civilization, Transpara Platform, and
Competition. DevOps followed as the fourth space. Dated plans and evidence remain
historical records; [the documentation index](docs/README.md) identifies the
current guides.
