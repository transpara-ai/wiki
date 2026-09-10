---
entity: Transpara Platform Architecture
org: transpara
primary_placement: platform/architecture
placements:
  - platform/architecture
classification: company-internal
aliases: [Platform architecture]
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
  - /Transpara/transpara-ai/repos/platform/docs/product-context.md
  - /Transpara/transpara-ai/repos/platform/docs/platform-specification.md
  - /Transpara/transpara-ai/repos/platform/docs/architecture-decision-records.md
---

# Transpara Platform Architecture

The Transpara Platform is a Kubernetes-based system with explicit boundaries between data access, storage, calculation, semantic context, presentation, identity, messaging, and lifecycle operations.

## Current reference flow

`sources → extractors → tStore / live access → calculations and graph context → tView and alerts`

The code-grounded Product Context identifies K3s, containerd, Envoy Gateway, Keycloak, EMQX, PostgreSQL/CloudNativePG, TimescaleDB, Memgraph, tView, tStudio, tCalc, tGraph, tStore services, and the Transpara operator. Exact replicas and versions are deployment facts, not timeless architecture.

## Normative invariants

The Platform Specification defines requirements including a single north–south entry model, east–west zero trust, immutable image identity, explicit topology, default-deny security, restore-over-rebuild recovery, encrypted secrets at rest, admission controls, operator RBAC, backup integrity, air-gap transfer integrity, predictable failure domains, verified supply chain, credential hygiene, and installer idempotence.

These are obligations. They must not be represented as fully implemented unless the corresponding code and deployment verification pass.

## Authority

When sources disagree, use this order: running code and versioned configuration; accepted ADRs and normative specification; maintained engineering reference; delivery evidence; intended UI; public docs; marketing. Record the disagreement instead of blending the layers.

See [[transpara-platform-components]], [[transpara-security-compliance]], and [[transpara-decisions-reference]].
