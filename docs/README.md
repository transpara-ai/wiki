---
doc_id: "TAI-WIKI-DOCUMENTATION"
title: "Transpara Knowledge Hub documentation"
doc_type: "index"
version: "0.1.0"
status: "draft"
created: "unknown"
updated: "2026-09-18"
owner: "Transpara"
steward: "Codex"
author: "Codex"
reviewer: "Pending human review"
project: "wiki"
repo: "transpara-ai/wiki"
classification: "company-internal"
supersedes: []
canonical: false
version_history: "First controlled revision; prior unversioned content remains in Git history"
---

# Transpara Knowledge Hub documentation

The Knowledge Hub contains Civilization, Transpara Platform, Competition, and
DevOps. The current operational guides live at the repository root and in
`compile/`:

| Guide | Purpose |
| --- | --- |
| [README](../README.md) | Space overview, navigation, setup, and verification |
| [Design](../DESIGN.md) | Current source scope, shared article model, and publication profiles |
| [Provenance](../PROVENANCE.md) | Evidence origins, dated source coverage, and known gaps |
| [Releases](releases/README.md) | Stable SemVer, GitHub publication, notes and recovery |
| [Karpathy pattern audit](karpathy-pattern-audit.md) | Implementation alignment, remaining synthesis/maintenance work, and offline capabilities |
| [Wiki architecture comparison](wiki-architecture-comparison/README.md) | Karpathy, Transpara and Cortex dossiers, Mermaid timing swim lanes, adversarial rankings and weighted KT decision |
| [Rebuilding](../compile/REBUILD.md) | Source registration, refresh, synthesis, and local services |
| [Authoring API](../API.md) | Evidence ingestion in all spaces and DevOps article creation |
| [Docker hosting](../DOCKER.md) | Private hosting, source dependencies, and operational checks |
| [Velia deployment automation](deployment-automation.md) | Mac relay or RemoteRepos tunnel, prerequisite installation, verified migration, rehearsal, cutover, and recovery |
| [Manual Velia migration](manual-velia-migration.md) | Operator-run installation with temporary SSH browser access while Tailscale HTTPS admin setup is pending |
| [Knowledge Hub article](../wiki/civilization-wiki.md) | The wiki's purpose, expansion, and compile history; its original slug is retained |

The machine-readable [knowledge structure registry](../compile/knowledge_structure.json)
defines current spaces, sections, stewards, classifications, and publication
profiles. An article's placement determines its space; the directory holding
its source material does not.

## Historical records

The dated records in `superpowers/plans/`, `superpowers/specs/`,
`superpowers/research/`, and `dark-factory/` describe the decisions, proposals,
and evidence at their stated dates. Their references to a Civilization-only
wiki, old service names, or earlier article counts are historical context.

The [September 5 migration plan](superpowers/plans/2026-09-05-multi-space-wiki-migration.md)
records the initial expansion into Civilization, Transpara Platform, and
Competition. DevOps was added afterward and is included in the current guides
and registry. Use the dated plan and verification records to understand that
migration; use the guides above to operate and author the current Hub.

- [Continuous discovery implementation and trust boundaries](continuous-discovery/implementation.md)
- [Discovery operator and API guide](../compile/DISCOVERY.md)

## Document revision history

| Version | Date | Change |
| --- | --- | --- |
| 0.1.0 | 2026-09-18 | Establish Transpara document control and a SemVer baseline for previously unversioned content. |
