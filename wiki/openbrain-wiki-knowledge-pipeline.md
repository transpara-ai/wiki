---
entity: OpenBrain and Wiki Knowledge Pipeline
org: transpara-ai
primary_placement: civilization/institutional
placements:
  - civilization/institutional
classification: internal
aliases:
  - OpenBrain/wiki pipeline
  - raw memory to curated knowledge
  - knowledge pipeline
tier: institutional
status: compiled from proposal source; advisory only
last_compiled: "2026-06-24"
sources:
  - raw/civilization/stage-0-institutional-substrate/06-openbrain-wiki-pipeline-index-v0.1.0.md
  - raw/civilization/stage-0-institutional-substrate/02-stage-0-provenance-manifest-v0.1.0.md
  - PROVENANCE.md
  - wiki/civilization-wiki.md
confidence:
  source_status: proposal
  claims: grounded in Stage 0 pipeline index and existing wiki provenance
  authority: advisory; does not activate ingestion
---

# OpenBrain and Wiki Knowledge Pipeline

The OpenBrain and Wiki Knowledge Pipeline separates raw memory capture from
curated knowledge presentation.

OpenBrain is the raw memory capture substrate. The [[civilization-wiki]] is the
curated knowledge presentation layer. The Stage 0 source expresses the intended
flow this way:

```text
OpenBrain / Codex sessions / GitHub / reviews / imports
  -> raw capture
  -> normalized records
  -> curated Civilization knowledge
  -> wiki-input package
  -> wiki repo render
```

This article does not activate that pipeline. It only gives the wiki a page that
names the boundary.

## Why the distinction matters

Raw memory and curated knowledge have different trust shapes.

[[ob1]] and OpenBrain-style capture preserve intent, discussion, and recall
material. That material can be invaluable, but it is not itself doctrine,
EventGraph truth, release authority, or certification evidence.

The wiki is a compiled presentation layer. It summarizes, cross-links, and
states conflicts, but it remains advisory under [[memory-knowledge-advisory]]
unless a claim is separately validated by accepted doctrine, EventGraph evidence,
or explicit authority.

## Stage 0 source treatment

The Stage 0 manifest copied OpenBrain and wiki anchors, copied representative
curated wiki pages, and indexed the large monthly OpenBrain raw exports instead
of copying them wholesale. That choice preserves the distinction between source
memory and published knowledge.

The wiki refit follows the same rule: Stage 0 material is included as a
provenance-aware source snapshot, while the article prose remains advisory and
clearly labeled.
