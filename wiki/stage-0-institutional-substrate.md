---
entity: Stage 0 Institutional Substrate
org: transpara-ai
primary_placement: civilization/institutional
placements:
  - civilization/institutional
classification: internal
aliases:
  - Stage 0
  - institutional substrate Stage 0
  - Civilization Stage 0
tier: institutional
status: compiled from proposal source; advisory only
last_compiled: "2026-06-24"
sources:
  - raw/civilization/stage-0-institutional-substrate/01-stage-0-completion-spec-v0.1.0.md
  - raw/civilization/stage-0-institutional-substrate/02-stage-0-provenance-manifest-v0.1.0.md
  - raw/civilization/stage-0-institutional-substrate/07-stage-0-closeout-report-v0.1.0.md
confidence:
  source_status: proposal
  claims: grounded in Stage 0 completion and closeout sources
  authority: advisory; not canonical doctrine
---

# Stage 0 Institutional Substrate

Stage 0 is the preparation stage for the [[civilization-institutional-substrate]]
migration arc. Its definition is intentionally narrow: create the scaffold,
copy or index relevant historical material, record provenance, and stop before
any action that would alter live structure or steer adjacent development.

The Stage 0 source defines completion this way:

```text
scaffold exists
historical docs copied or indexed
provenance manifest complete
birth-era philosophy indexed
Dark Factory lineage indexed
Platform/transpara-MCP boundary indexed
OpenBrain/wiki pipeline indexed
no live canonical paths altered
no active development steered
verification passed
```

## What Stage 0 produced

The source scaffold records a migration arc README, a completion spec, a
provenance manifest, domain indexes, a corpus index, inventory/manifests
placeholders, and a closeout report.

The most important wiki-facing outputs are:

| Output | Wiki role |
| --- | --- |
| Completion spec | Defines what "done" meant for the preparation stage. |
| Provenance manifest | Records copied, indexed, summarized, and deferred sources. |
| Birth-era philosophy index | Separates source philosophy from accepted doctrine. |
| Dark Factory lineage index | Preserves [[dark-factory]] as formative lineage. |
| Platform/MCP boundary index | Defines customer-data and demo-data boundaries. |
| OpenBrain/wiki index | Separates raw memory capture from curated knowledge. |
| External research placement index | Places competitor and adjacent-technology research. |

## What Stage 0 did not do

Stage 0 did not move `docs/dark-factory`, rename live repo paths, rewrite
systemd units, alter runtime behavior, modify active Civilization development
branches, steer in-flight PRs, change customer or demo access policy, make the
new scaffold canonical, commit, push, open a PR, or mark anything ready.

That non-action list is part of the artifact. It prevents a preparation scaffold
from becoming a stealth migration.

## Verification status

The closeout source records these checks as passed in the `docs` repo context:

```text
git diff --check
authored-doc ASCII hygiene excluding copied corpus
npm run verify
```

This wiki refit still has its own verification requirements. Passing Stage 0 in
`docs` does not prove that the wiki build, article links, browser render, or
preview route are correct.
