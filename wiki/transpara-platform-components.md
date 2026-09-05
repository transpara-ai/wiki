---
entity: Transpara Platform Components
org: transpara
primary_placement: platform/components
placements:
  - platform/components
  - platform/capabilities
classification: company-internal
aliases: [Platform modules, tSystem components]
tier: product
status: reviewed
last_compiled: 2026-09-05
reviewed_on: 2026-09-05
review_by: 2026-12-04
source_authority:
  - code
  - configuration
  - engineering-docs
sources:
  - /Transpara/transpara-ai/repos/platform/docs/product-context.md
  - /Transpara/transpara-ai/repos/platform/docs/rtoi-mapping-matrix.md
---

# Transpara Platform Components

This is a conceptual component index. Deployed manifests and component repositories govern exact names, versions, endpoints, and scale.

| Component | Responsibility | Evidence state |
|---|---|---|
| tView | Responsive operational visualization | Implemented baseline |
| tStudio | Configuration and modeling interface | Implemented baseline; frontend direction may evolve |
| tStore | Time-series persistence and access services | Implemented baseline |
| tCalc | Event-driven calculation and analytics services | Implemented baseline |
| tGraph | Semantic/asset graph, API, events, and MCP-facing process | Implemented baseline |
| Extractors | Connect source systems such as OPC-UA, ODBC, MQTT, and supported APIs | Connector-specific evidence required |
| tSystem services | Platform APIs, orchestration, and supporting system behavior | Implemented baseline |
| TAI Gateway | Governed gateway to supported model providers and tools | Implemented baseline; provider/config dependent |
| Transpara operator | Kubernetes lifecycle control through the platform CRD | Implemented baseline |
| Keycloak and EMQX | Identity and event messaging | Accepted architectural components |

## Interpretation rule

“Component exists” does not imply every RTOI capability is complete. Capability answers should cite the current repository or release configuration and then identify any normative or planned gap separately.

Visual KPI is a separate product, not one of these Kubernetes services. See [[visual-kpi]].
