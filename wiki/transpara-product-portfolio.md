---
entity: Transpara Product Portfolio
org: transpara
primary_placement: platform/product-overview
placements:
  - platform/product-overview
classification: company-internal
aliases: [Transpara products, product terminology]
tier: product
status: reviewed
last_compiled: 2026-09-05
reviewed_on: 2026-09-05
review_by: 2026-12-04
source_authority:
  - engineering-docs
  - public-docs
sources:
  - /Transpara/transpara-ai/repos/platform/docs/product-context.md
  - /Transpara/transpara-ai/repos/platform/docs/real-time-operational-intelligence.md
  - https://www.transpara.com/
  - https://www.transpara.com/products/transpara-platform/
---

# Transpara Product Portfolio

Transpara has two related products. **Visual KPI** is the established Windows/IIS product for real-time KPI visualization. **Transpara Platform** (also called Transpara or tSystem in engineering material) is the newer Linux/Kubernetes platform for operational intelligence. They share product ideas, but their architectures, modules, deployment requirements, and release evidence are different.

## Current, implemented portfolio

- **Visual KPI** is a mature, shipping web application. It connects to operational and business sources, applies KPI limits and status, and presents dashboards, alerts, trends, and drill-down views.
- **Transpara Platform** is a containerized platform whose engineering baseline includes tStore, tCalc, tGraph, tStudio, tView, extractors, identity, messaging, and operational infrastructure.
- Both products can coexist. A question about “Transpara” must be disambiguated before giving product-specific requirements or instructions.

## Terminology

| Term | Use it for | Do not assume |
|---|---|---|
| Visual KPI | The established Windows/.NET and IIS product | That Platform procedures apply |
| Transpara Platform | The newer Kubernetes product | That every vision capability is shipped |
| tSystem | An engineering name for the Platform and its system services | That it means Visual KPI |
| RTOI | The Real-Time Operational Intelligence product vision and category framing | That vision language is implementation evidence |
| VDL | Virtual Data Lake: governed live access across sources without requiring wholesale migration | That no data is ever persisted by any module |

## Authority boundary

Running code and versioned configuration establish current behavior. The Platform Specification and accepted ADRs establish normative requirements. The RTOI document and product site explain direction and positioning; they are not sufficient proof that a feature is implemented.

See [[visual-kpi]], [[transpara-platform-overview]], and [[transpara-rtoi]].
