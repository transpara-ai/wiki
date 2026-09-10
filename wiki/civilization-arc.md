---
entity: Civilization Progress Chart
org: transpara-ai
primary_placement: civilization/meta
placements:
  - civilization/meta
classification: internal
aliases:
  - progress chart
  - Civilization arc chart
  - construction arc
  - arc visualization
tier: meta
status: display-only read lens
last_compiled: "2026-06-24"
sources:
  - compile/assets/civilizationArcData.js
  - compile/assets/civilizationProgressEvidence.js
  - compile/assets/civilizationOntology.js
  - compile/INFLIGHT.md
confidence:
  source_status: derived display data
  claims: display-only
  authority: not EventGraph truth; not release authority
---

# Civilization Progress Chart

The Civilization Progress Chart is the single chart page for the wiki. It is a
read lens over the compiled article corpus, the static arc data, and public-safe
operation exports. It is not the home page, not the wiki's source of truth, and
not a governance record.

The chart remains useful because it shows the construction timeline, gates,
worklist, and display-only operation evidence in one place. It is kept on this
page so the rest of the wiki can read like a normalized encyclopedia: articles
first, provenance visible, dashboards kept to their own route.

## Authority boundary

The chart is display-only. It is not [[event-graph]] truth, not certification
evidence, not a release decision, and not a substitute for accepted doctrine.

When the chart conflicts with an article, an accepted source document, or an
EventGraph-backed record, the chart loses. The correction path is to update the
source data and rebuild the wiki, not to treat the rendered marker as authority.

## Route policy

The canonical route is `civilization-arc.html`. The underscored route
`civilization_arc.html` remains as a compatibility alias.
