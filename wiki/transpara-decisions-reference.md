---
entity: Transpara Platform Decisions and Authority
org: transpara
primary_placement: platform/decisions-reference
placements:
  - platform/decisions-reference
classification: company-internal
aliases: [Platform ADR index, decision authority]
tier: product
status: reviewed
last_compiled: 2026-09-05
reviewed_on: 2026-09-05
review_by: 2026-12-04
source_authority:
  - adr
  - engineering-docs
sources:
  - /Transpara/transpara-ai/repos/platform/docs/architecture-decision-records.md
  - /Transpara/transpara-ai/repos/platform/docs/platform-readme.md
  - /Transpara/transpara-ai/repos/platform/docs/platform-specification.md
---

# Transpara Platform Decisions and Authority

Accepted Architecture Decision Records (ADRs) explain why durable platform choices were made and what consequences follow. They are append-only constraints: supersede a decision explicitly; do not silently rewrite it in a summary page.

## Selected accepted decisions

The maintained ADR set records choices including K3s for orchestration, Envoy and the Kubernetes Gateway API for ingress, Keycloak for identity, EMQX for MQTT messaging, CloudNativePG-managed PostgreSQL, TimescaleDB for time series, Memgraph for graph storage, a Transpara operator for lifecycle control, idempotent installation, manifest-driven image bundles, and `crane` for air-gap image export.

## How to use this page

- Read the actual ADR before depending on its rationale or consequences.
- Check whether an ADR is accepted, pending, superseded, or implementation-tracked.
- An accepted decision can be normative even while implementation has gaps.
- Code and observed configuration establish whether the decision is currently realized.
- Confluence decisions and delivery systems may add context but must not silently displace an accepted ADR.

The authoritative index and full text remain in the Platform engineering repository.
