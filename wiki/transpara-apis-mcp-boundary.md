---
entity: Transpara APIs and MCP Boundary
org: transpara
primary_placement: platform/development-apis
placements:
  - platform/development-apis
  - civilization/architecture
classification: company-internal
aliases: [Transpara MCP, MCP boundary, Platform APIs]
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

# Transpara APIs and MCP Boundary

Transpara Platform exposes service APIs and includes an MCP-facing process associated with tGraph. MCP is an integration boundary for governed tool access; it is not an authority system and must not bypass platform identity, policy, audit, or source-of-truth controls.

## Current versus normative

- **Current baseline:** FastAPI is used across several application services; tGraph includes API, event-processing, and MCP process roles; the AI gateway can connect models and governed tools. Exact routes and schemas belong to the relevant versioned repositories.
- **Normative boundary:** ingress, authentication, authorization, service identity, network policy, auditability, rate and resource controls, and secrets handling apply equally to human and agent callers.
- **Not established by this page:** a public MCP endpoint, unrestricted model access, or permission for an agent to mutate operational systems.

## Safe integration pattern

Resolve the authenticated principal, authorize a narrowly named capability, validate and constrain inputs, execute through the owning service, retain an attributable audit record, and return typed results. Read access does not imply write access. A model’s request is never itself authorization.

This page is shared with Civilization because the authority principle is general: tools extend capability, while governance determines permission.
