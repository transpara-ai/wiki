# Transpara Knowledge Hub Multi-Space Migration Plan

- **Status:** Approved implementation plan; execution not started
- **Date:** 2026-09-05
- **TLC route:** Designed
- **Repository:** `/Transpara/transpara-ai/repos/wiki`
- **Decision:** Evolve the wiki into one governed knowledge hub containing multiple reader-facing spaces, while retaining one canonical article graph and stable article URLs.

## Executive Summary

The current wiki architecture can support multiple purposes, but its organizing model must be generalized. Today, `org` and `tier` jointly act as provenance, navigation, and information architecture. The migration separates those concerns:

- **Organization** identifies the steward or source domain.
- **Space** identifies the reader-facing purpose.
- **Section** provides navigation within a space.
- **Article** remains a globally identified knowledge entity with a stable slug.
- **Placement** projects an article into one or more spaces and sections.
- **Classification** controls whether and where an article may be published.
- **Source authority** describes the evidentiary status of the article's sources.

The target is one repository and one canonical knowledge graph projected into several governed spaces. The initial spaces are:

1. **Civilization** — institutional philosophy, architecture, history, and operational learning.
2. **Transpara Platform** — the accurate product and engineering knowledge base.
3. **Competition** — governed competitive, positioning, and market intelligence.

The migration preserves existing article URLs, provenance, historical ledgers, source boundaries, and the current loopback-only deployment posture.

## TLC Brief

### Outcome

Create a registry-driven **Transpara Knowledge Hub** that supports multiple spaces without duplicating articles or weakening the repository's existing governance and safety controls.

### Route

**Designed.** This change affects information architecture, metadata, generated routes, ingestion, search, publication policy, and operational deployment. It needs explicit design, proportional migration tests, and ordinary review before cutover.

### Non-Goals

- Replacing source repositories, Jira, Confluence, Figma, EventGraph, or other systems of record.
- Making the wiki authoritative for release state, runtime truth, or operational control.
- Adding runtime AI behavior to the published wiki.
- Exposing new public or LAN-accessible routes as part of this migration.
- Bulk-importing every source document into the Platform or Competition spaces.
- Rewriting historical evidence, raw submissions, or completed ingestion ledgers.

### Assumptions

- **Competition** means Transpara commercial competitive intelligence, not the existing philosophical concept of competition.
- The initial deployment remains private and loopback-only.
- The current 108 canonical articles remain in Civilization unless deliberately reviewed and placed elsewhere.
- Existing article slugs are global identifiers and should remain stable indefinitely.
- The first implementation step introduces shared catalog machinery without visible site behavior changes.

## Target Architecture

```text
Transpara Knowledge Hub
├── Transpara
│   ├── Platform Knowledge Base
│   └── Competition
└── Transpara-AI
    └── Civilization
```

This hierarchy communicates stewardship, but the implementation must not treat the organization as the primary navigation dimension. Spaces are the reader-facing products; organizations are governance metadata.

### Core Dimensions

| Dimension | Meaning | Example |
|---|---|---|
| `org` | Steward or source domain | `transpara`, `transpara-ai` |
| `space` | Reader-facing purpose | `civilization`, `platform`, `competition` |
| `section` | Navigation group within a space | `architecture`, `security`, `competitors` |
| `article` | Canonical global knowledge entity | `EventGraph` / `event-graph` |
| `placement` | Projection into a space and section | `civilization/architecture` |
| `classification` | Publication boundary | `internal`, `public-candidate` |
| `source_authority` | Evidentiary status | `code`, `ADR`, `first-party-positioning` |

This model supersedes `org` as the site's primary navigation key while preserving the current fail-closed intent.

## Initial Space Registry

| Space | Steward | Purpose | Initial Sections |
|---|---|---|---|
| Civilization | Transpara-AI | Philosophy, institutional architecture, history, research, and operational learning | Foundations; Institutional Substrate; Architecture; Arc; Investigations; Concepts; Meta |
| Transpara Platform | Transpara | Accurate commercial and technical knowledge about the Transpara platform | Product Overview; Capabilities; Architecture; Components; Integrations; Deployment & Operations; Security & Compliance; Development & APIs; Troubleshooting; Decisions & Reference |
| Competition | Transpara | Competitive, market, positioning, sales, and win/loss intelligence | Market & Categories; Competitors; Comparisons; Positioning; Objections; Win/Loss Evidence; Research Methods |

The Platform space must distinguish the overall Transpara platform from **Visual KPI**, which is one product or capability within the portfolio rather than a synonym for the platform.

## Repository Layout

```text
index.md
spaces/
  civilization/index.md
  platform/index.md
  competition/index.md
wiki/
  <slug>.md
raw/
  civilization/
  transpara/                 # retained historical material
  platform/
  competition/
  inbox/<space>/<date>/<article>/
compile/
  knowledge_structure.json
  knowledge_structure.py
  article_catalog.py
```

Keep canonical articles flat under `wiki/`. Existing filenames act as stable link identities, and current tooling assumes `wiki/*.md`. Space membership belongs in metadata and registries rather than directory location.

## Article Metadata

Every canonical article receives explicit steward, primary placement, placements, and classification fields. Preserve `tier` during the compatibility period.

```yaml
entity: EventGraph
org: transpara-ai
primary_placement: civilization/architecture
placements:
  - civilization/architecture
classification: internal
tier: architecture # temporary compatibility field
```

An article may appear in several spaces without duplicating its body:

```yaml
entity: Transpara MCP Boundary
org: transpara
primary_placement: platform/development-and-apis
placements:
  - platform/development-and-apis
  - civilization/architecture
classification: internal
```

Rules:

- Each article has one canonical slug and one steward.
- Each article has exactly one primary placement.
- Additional placements are explicit and registry-valid.
- Invalid space, section, placement, or classification values fail before distribution output changes.
- Article body, source provenance, confidence, and timestamps are not rewritten by the structural migration.

## URLs, Navigation, and Search

### Stable Canonical Article URLs

Article URLs remain flat:

- `/event-graph.html`
- `/platform-transpara-mcp-boundary.html`

An article is rendered once. Space pages link to that canonical render, and the article page shows its primary location plus any additional placements.

### Space Routes

- `/index.html` — neutral Knowledge Hub portal.
- `/civilization/index.html`
- `/platform/index.html`
- `/competition/index.html`

The existing Civilization board moves under the Civilization home without losing content or links. Existing Arc aliases remain valid and clearly associated with Civilization.

### Navigation Behavior

- The global header exposes a space switcher.
- Local navigation is generated from the active space registry.
- Shared articles show an **Also in** list.
- Search defaults to the active space and offers a permitted **All spaces** scope.
- Search documents include space, section, organization, and classification metadata.
- Route and asset construction must be depth-aware; nested pages must not break links, styles, scripts, or status endpoints.

## Authority and Source Boundaries

The Knowledge Hub is advisory. It is never a substitute for release authority, runtime truth, operational control, or EventGraph.

### Civilization

- Preserve the complete existing corpus, provenance, board, Arc views, investigation standard, and historical context.
- Treat the current 108 canonical articles as Civilization by default.
- Preserve the existing eight-repository candidate model: `agent`, `docs`, `eventgraph`, `hive`, `operation`, `platform`, `site`, and `work`.
- The wiki remains a companion to the operating system and repositories, not a runtime participant.

### Transpara Platform

Use this source priority when claims conflict:

1. Running code and versioned configuration.
2. Platform specifications, ADRs, and maintained engineering documentation.
3. Approved Confluence decisions.
4. Jira status and delivery evidence.
5. Figma for intended UI behavior.
6. Current public product documentation.
7. Marketing language.

Platform articles must distinguish among:

- current implemented behavior;
- normative architecture or decisions;
- planned work;
- investigation findings;
- roadmap intent;
- marketing positioning.

### Competition

- Begin with the competitive contexts already important to Transpara, including RTOI and AI-SDR.
- Label Transpara-authored positioning as first-party positioning.
- Use current primary external sources for competitor capabilities, pricing, ownership, and operating status.
- Record `verified_at` and `review_by` for time-sensitive claims.
- Anonymize win/loss and prospect evidence unless publication is explicitly approved.
- Do not automatically convert external-agent investigations into commercial claims.
- Keep the philosophical **Market Graph** and competition primitive in Civilization unless deliberately cross-placed.

### Customer Data

- Do not ingest customer production content into the repository.
- Distinguish product knowledge, demonstration data, and customer runtime data.
- Any future customer-specific knowledge space requires its own authority and classification design.

## Migration Phases

### Phase 0 — Freeze and Baseline

1. Fast-forward a clean local `main`, which is currently 11 commits behind `origin/main`.
2. Record the baseline commit, route inventory, build output, and service configuration.
3. Confirm the current baseline of 108 canonical articles.
4. Capture the current 2,105 wikilink occurrences.
5. Preserve the 17 intentional unresolved targets, representing 116 occurrences, as an explicit allowlist or acknowledged baseline.
6. Commit this design before implementation.
7. Create a `codex/` implementation branch.
8. Run the existing complete verification suite as the entry gate.

**Gate:** No implementation begins from a dirty, unverified, or ambiguously versioned baseline.

### Phase 1 — Introduce a Central Article Catalog

1. Add the space and section registry in `compile/knowledge_structure.json`.
2. Add a typed/validated registry loader in `compile/knowledge_structure.py`.
3. Add a shared article catalog in `compile/article_catalog.py`.
4. Migrate the builder, statistics, freshness scanner, link checker, ingestion, and retirement logic to the shared catalog.
5. Retain a compatibility adapter for current `org`/`tier` behavior.
6. Produce no visible navigation or route change in this phase.

**Gate:** Article inventory, current routes, link resolution, and generated output remain equivalent to baseline.

### Phase 2 — Migrate Existing Metadata

1. Add `org: transpara-ai` to all 108 existing articles unless already explicit.
2. Map every article to a primary Civilization placement derived from its current tier and registry.
3. Add the same entry to `placements`.
4. Add `classification: internal` unless a stricter current value exists.
5. Retain `tier` until all readers have migrated.
6. Do not change article bodies, sources, confidence, timestamps, or ledger history.

**Gate:** Exactly 108 canonical articles remain; every article validates; all prior canonical routes still resolve.

### Phase 3 — Add Space Projection and Navigation

1. Add the neutral root portal and three space homes.
2. Move the current board presentation under Civilization.
3. Generate labels and local navigation from the registry.
4. Update repository navigation metadata without changing flat article URLs.
5. Preserve existing Arc routes and aliases.
6. Add the space switcher and shared-article placement display.

**Gate:** All space and section links resolve; nested assets work; old article and Arc URLs remain valid.

### Phase 4 — Make Search, Statistics, and Freshness Space-Aware

1. Calculate global totals from distinct canonical articles.
2. Calculate per-space totals from placements.
3. Do not sum per-space counts to claim a global total because shared articles would be duplicated.
4. Move Civilization-specific dashboard statistics to the Civilization home.
5. Extend status output with per-space health while retaining compatibility fields.
6. Add space and section fields to search documents and filters.

**Gate:** Counts reconcile, shared pages do not inflate global totals, and search scope is correctly enforced.

### Phase 5 — Update Ingestion and Lifecycle Operations

1. Require or derive space, section, and steward during staging.
2. Validate the target placement under the existing mutation lock before commit.
3. Limit template-based new article creation to Civilization investigations initially.
4. Add optional space and placement fields to new ledger records without rewriting old records.
5. Keep **Replace** global because the article identity is global.
6. Make **Remove** preview all placement, navigation, search, and alias consequences.
7. Keep placement changes PR-only until the workflow has proven safe.
8. Protect structural routes and generated homes from mutation operations.

**Gate:** Lifecycle previews are complete, rollback behavior is preserved, and invalid placement cannot mutate the canonical corpus.

### Phase 6 — Add Publication Profiles

Define explicit build profiles:

- **authoring-local:** all authorized internal spaces, raw evidence, ingestion controls, repository status, and loopback-only services.
- **company-internal:** reviewed knowledge pages only; no raw evidence, arbitrary repository README content, or mutation controls.
- **public-platform:** disabled by default and limited to explicitly allowlisted public-safe pages if separately authorized.

Each profile must enforce source and classification allowlists. Unknown classifications or unreviewed sources are excluded rather than guessed.

**Gate:** Negative tests prove that restricted pages, raw evidence, repository metadata, controls, and secrets cannot enter broader profiles.

### Phase 7 — Seed the Platform Space Curatively

Start with reviewed, high-value pages rather than a bulk import:

- product portfolio and terminology;
- platform overview and RTOI context;
- architecture and major components;
- modules and capabilities, including Visual KPI;
- data ingestion and VDL;
- deployment, operations, and air-gap behavior;
- security and compliance;
- APIs and the MCP boundary;
- troubleshooting and operational reference;
- selected ADRs and decisions.

Every article must identify source authority and distinguish current implementation from plans or positioning.

**Gate:** Each seeded article has an accountable steward, current sources, placement, classification, and review date where appropriate.

### Phase 8 — Seed the Competition Space Curatively

Start with:

- market and category overview;
- competitor index;
- individual competitor profiles;
- governed comparisons;
- positioning and objection handling;
- anonymized win/loss template;
- research methods, verification dates, and freshness expectations.

Research time-sensitive external claims from current primary sources during execution. Do not automatically export AI-SDR or other agent findings into canonical commercial content.

**Gate:** All factual market claims are sourced and time-bounded; first-party positioning is labeled; sensitive evidence is excluded or anonymized.

### Phase 9 — Shadow Build and Cut Over

1. Make the output directory configurable and build the candidate into `dist-next`.
2. Serve the candidate on a separate loopback-only endpoint.
3. Compare baseline and candidate inventories, routes, links, search, statistics, status, and content hashes where appropriate.
4. Run browser-level smoke and visual checks for the portal, all space homes, representative articles, shared placements, Arc aliases, search, and error states.
5. Cut over only after all acceptance criteria pass.
6. Rename or generalize systemd services and environment variables with a compatibility window.
7. Update operations and maintenance documentation.
8. Treat any public or non-loopback activation as a separate authority decision.

**Gate:** The candidate is demonstrably equivalent where compatibility is promised and correct where new behavior is intended.

### Phase 10 — Remove Transitional Compatibility

1. Observe a stable release before removing fallbacks.
2. Require explicit new metadata after the compatibility window.
3. Retire legacy environment aliases only after service configuration and operational documentation have migrated.
4. Keep flat legacy article URLs indefinitely.
5. Preserve all historical ledgers and evidence.
6. Do not physically move historical raw material solely to make the new taxonomy visually tidy.

**Gate:** No active caller, service, or documented operation depends on a compatibility path selected for removal.

## Expected Code and Content Impact

Implementation is expected to touch, at minimum:

- `compile/build_site.py`
- `compile/org_structure.py`
- `compile/stats.py`
- `compile/refresh_articles.py`
- `compile/check_links.py`
- `compile/ingest_server.py`
- ingestion lifecycle helpers and ledgers
- auto-deploy and live-reader correction tooling
- site CSS and generated navigation templates
- systemd units and operational environment documentation
- the root portal, space homes, and migrated article front matter
- unit, integration, browser, link, route, and publication-boundary tests

The final implementation should centralize structural knowledge rather than adding independent space logic to each script.

## Acceptance Matrix

| Area | Required Result |
|---|---|
| Canonical identity | All 108 existing article URLs continue to resolve. |
| Metadata | Every article has a valid steward, primary placement, placements list, and classification. |
| Evidence | No article body, source block, historical ledger, or raw evidence is silently rewritten. |
| Portal and spaces | Root portal and all three space homes render correctly. |
| Navigation | Space switcher, local sections, shared placements, and Arc compatibility work. |
| Search | Active-space filtering works; permitted all-space search is explicit. |
| Duplication | Shared articles have one canonical source and one rendered identity. |
| Integrity | Unintentional unresolved links, slug collisions, invalid placements, and orphan articles fail the build. |
| Transaction safety | Full structural validation occurs before distribution output changes. |
| Lifecycle | Replace and Remove previews show consequences across every placement. |
| Publication | Internal, raw, operational, and sensitive content cannot leak into broader profiles. |
| Secrets | A secret scan runs before any profile is served beyond its intended boundary. |
| Refresh | Refresh is idempotent and preserves valid placement metadata. |
| Failure behavior | A failed candidate build leaves the current site and service intact. |
| Test suite | `npm run verify` passes together with explicit catalog, registry, route, search, ingestion, publication, and browser tests. |
| Visual quality | Desktop and mobile checks pass for the portal, each space, representative article pages, and error states. |

## Rollback Strategy

- Keep the current `dist` active while building and testing `dist-next`.
- Avoid moving canonical article files, so rollback does not require reconstructing paths.
- Preserve all legacy article and Arc routes.
- Make build failure leave the current published artifact untouched.
- Retain the previous service artifact and configuration for immediate loopback-only restoration.
- Roll back with an explicit forward commit; do not rewrite repository history.
- Preserve historical ledgers and raw evidence regardless of presentation rollback.

## Planning Evidence and Current Baseline

At planning time:

- `compile/check_links.py` passed with 17 unresolved targets and 116 occurrences recognized as intentional baseline references.
- The repository contained 108 canonical articles and approximately 2,105 wikilink occurrences.
- The working tree was clean before this plan file was added.
- Local `main` was 11 commits behind `origin/main`; implementation must reconcile that before branching.
- No implementation code or content migration had been performed.

## Autonomous Execution Policy

The implementation agent should proceed phase by phase without requesting human intervention for ordinary, reversible, in-scope engineering decisions. It should use the registries, source-authority hierarchy, compatibility commitments, safety gates, and acceptance matrix in this plan to resolve routine ambiguity.

Human authority is required only when execution would materially expand scope or cross an explicit trust boundary, including:

- enabling public or non-loopback access;
- publishing customer, prospect, confidential, or otherwise sensitive evidence;
- changing the meaning of Competition away from commercial competitive intelligence;
- replacing source-system authority or introducing runtime operational control;
- accepting a compatibility break that this plan requires preserving;
- performing an irreversible or destructive action not already authorized here.

When a phase fails its gate, keep the last known-good site active, diagnose and repair within scope, then rerun the gate before continuing.
