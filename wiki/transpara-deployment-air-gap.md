---
entity: Transpara Deployment and Air-Gap Operations
org: transpara
primary_placement: platform/deployment-operations
placements:
  - platform/deployment-operations
classification: company-internal
aliases: [air-gap deployment, air-gapped Transpara, tinstaller]
tier: product
status: reviewed
last_compiled: 2026-09-05
reviewed_on: 2026-09-05
review_by: 2026-12-04
source_authority:
  - code
  - configuration
  - adr
  - engineering-docs
sources:
  - /Transpara/transpara-ai/repos/platform/docs/airgap-operations.md
  - /Transpara/transpara-ai/repos/platform/docs/platform-specification.md
  - /Transpara/transpara-ai/repos/platform/docs/tinstaller-test-matrix.md
---

# Transpara Deployment and Air-Gap Operations

Transpara Platform supports connected and air-gapped K3s deployments in single-node and multi-node forms. Air-gap is an architectural constraint, not a packaging afterthought.

## Validated engineering baseline

The Air-Gap Operations document reports automated validation of four installation scenarios: single-node connected, multi-node connected, single-node air-gapped, and multi-node air-gapped. The installer is designed to be idempotent. Air-gap bundles use rendered-manifest image discovery and `crane`-based export; multi-node distribution can use Spegel.

At customer air-gapped sites, the documented default is a local crane registry, with Spegel for peer distribution where applicable. Transpara’s internal Harbor is an upstream distribution service, not something that should be described as automatically installed at a customer site. Restricted third-party images require their governed acquisition path.

## Operational rule

Before an installation or upgrade, use the exact release runbook and validate bundle manifest, checksums, image availability, hardware and OS profile, certificates, storage, backup/restore state, and rollback path. Never turn this overview into a substitute for the versioned runbook.

## Requirement versus proof

The Platform Specification defines required security and recovery behavior. The test matrix and a successful target-environment verification establish that a particular build satisfies it. Keep those claims separate.
