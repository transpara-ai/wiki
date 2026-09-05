---
entity: Visual KPI
org: transpara
primary_placement: platform/capabilities
placements:
  - platform/capabilities
  - platform/product-overview
classification: company-internal
aliases: [Visual KPI Server, Visual KPI Designer]
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
  - https://www.transpara.com/
---

# Visual KPI

Visual KPI is Transpara’s established real-time KPI visualization product. It is distinct from the Kubernetes-based Transpara Platform.

## Current product identity

The maintained product context describes Visual KPI as a Windows Server and IIS-hosted, in-memory web application configured through the Excel-based Visual KPI Designer. It uses Microsoft SQL Server for configuration and connects to operational and business sources through supported data-source mechanisms.

Its product value centers on turning values into KPIs with limits and status, then presenting dashboards, trends, alerts, rollups, and drill-down views on responsive web interfaces.

## Boundary with Transpara Platform

- Do not use Platform Kubernetes procedures to administer Visual KPI.
- Do not describe Visual KPI as tView, tStore, tCalc, or tGraph.
- Confirm which product, release, and deployment model a question concerns.
- Treat migration compatibility and licensing as release-specific commercial questions requiring current approved documentation.

See [[transpara-product-portfolio]] for the portfolio distinction.
