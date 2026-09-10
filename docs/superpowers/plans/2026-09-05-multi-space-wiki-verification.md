# Transpara Knowledge Hub Multi-Space Migration Verification

**Date:** 2026-09-05

**Branch:** `codex/multi-space-wiki`

**Baseline:** `163de77`
**Plan:** `docs/superpowers/plans/2026-09-05-multi-space-wiki-migration.md`

## Outcome

The former single-purpose Civilization wiki is now a governed, multi-space
Transpara Knowledge Hub. Civilization, Transpara Platform, and Competition are
independent navigational projections over one canonical article corpus. The
migration retained flat canonical article URLs, history, raw evidence,
provenance, source-authority rules, customer-data boundaries, and loopback-only
authoring.

## Delivered Architecture

- `compile/knowledge_structure.json` is the central registry for spaces,
  sections, stewards, classifications, source authorities, and publication
  profiles.
- `compile/knowledge_structure.py` and `compile/article_catalog.py` expose the
  validated registry and canonical article catalog to build, ingestion,
  lifecycle, refresh, statistics, and link-integrity paths.
- The root route is a neutral Knowledge Hub portal. Space homes are available
  at `/civilization/index.html`, `/platform/index.html`, and
  `/competition/index.html`.
- Articles retain one canonical flat URL while allowing one primary placement
  and additional projections. Navigation, article location labels, search, and
  statistics use the same catalog.
- Ingestion requires a valid space, section, and steward. Raw inbox material is
  namespaced by space; placement changes remain reviewable repository changes.
- Removal previews and tombstones retain every placement, classification, and
  source-authority consequence.
- Publication profiles separate full local authoring from company-internal
  projection. The public Platform profile remains disabled and fails before
  writing output.
- Generic Knowledge Hub service and refresh-timer templates coexist with the
  retained Civilization compatibility units and environment aliases.

## Corpus Evidence

- Canonical articles: 131.
- Civilization projection: 108 articles.
- Platform projection: 13 articles.
- Competition projection: 13 articles.
- Curated Platform and Competition seed set: 24 articles, comprising 23 new
  canonical articles plus the enriched pre-existing canonical Platform MCP
  boundary article.
- The pre-migration 17 intentional unresolved targets and 116 occurrences remain
  the acknowledged baseline; no new unresolved-link class was introduced.
- Historical raw sources and ingestion ledger records were retained rather than
  rewritten.

## Verification Evidence

The final committed tree passed:

- `npm run verify` in full.
- 73 Node unit tests.
- 320 Python tests across catalog, build security, links, navigation, refresh,
  ingestion/lifecycle, publication profiles, seed governance, and secret-scan
  behavior.
- 23 Arc DOM tests plus the ingest state-machine DOM smoke test.
- 10 Playwright tests against the active output and the same 10 tests against
  the shadow output, including desktop/mobile space navigation, scoped search,
  canonical shared placement, and honest 404 behavior.
- Full-tree secret scanning: 304 scanned occurrences, 18 allowlisted occurrences, 286
  direct passes, and zero blocks. New records are exact, expiring fingerprints
  for reviewed non-secret environment-variable identifiers.

The final shadow verifier reported:

- 131 canonical articles.
- 314 baseline routes preserved.
- 856 HTML routes in the authoring-local projection.
- All generated local links resolving.
- Candidate and active inventories byte-equivalent.
- Active output unmodified by shadow verification.

## Operational Cutover Evidence

- `transpara-knowledge-hub.service` is installed, enabled, and active as a user
  service.
- `transpara-knowledge-hub-refresh.timer` is installed, enabled, and active on
  its 15-minute schedule.
- `/api/health` returns `{"ok": true}`.
- The listener is bound only to `127.0.0.1:8787`; no non-loopback listener was
  introduced.
- A real refresh completed successfully with 131 articles and preserved the
  local Civilization archive-boundary marker byte-for-byte when its upstream
  mirror omitted that governance file.

## Compatibility Window

Phase 10 is deliberately gated by the plan's requirement to observe a stable
release. Legacy article URLs remain indefinitely stable, while the old service
names, environment aliases, and transitional entry points remain available for
the observation window. Their later removal is a distinct, evidence-gated
cleanup decision and is not required for this migration cutover.

## Rollback

The migration remains reversible by disabling the generic service and timer,
returning to the retained compatibility units, and restoring the pre-migration
branch point. Canonical article routes and original content paths were not
destroyed, so rollback does not require reconstructing content or redirects.
