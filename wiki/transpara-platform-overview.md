---
entity: Transpara Platform Overview
org: transpara
primary_placement: platform/product-overview
placements:
  - platform/product-overview
classification: company-internal
aliases: [Transpara Platform, tSystem]
tier: product
status: reviewed
last_compiled: 2026-09-05
reviewed_on: 2026-09-05
review_by: 2026-12-04
source_authority:
  - code
  - configuration
  - engineering-docs
  - public-docs
sources:
  - /Transpara/transpara-ai/repos/platform/docs/product-context.md
  - /Transpara/transpara-ai/repos/platform/docs/platform-readme.md
  - https://www.transpara.com/products/transpara-platform/
---

# Transpara Platform Overview

Transpara Platform is Transpara’s containerized operational-intelligence platform. It connects operational and business data, adds context through KPI and graph models, runs analytics, and delivers live visualizations, alerts, and collaboration workflows. It is designed for customer-controlled deployment, including restricted-network and air-gapped environments.

## What is implemented

The maintained engineering baseline reports a K3s/Kubernetes system with extractors, tStore, tCalc, tGraph, tStudio, tView, tSystem services, identity, MQTT messaging, and supporting database and observability components. That inventory is a point-in-time description; component repositories and deployed configuration remain authoritative for versions and exact behavior.

## Product model

The platform separates four concerns:

1. Connect to sources through extractors and supported interfaces.
2. Store selected time-series data and retain live access to other sources.
3. model assets, relationships, metadata, calculations, and KPIs.
4. Deliver operational views, notifications, analytics, and governed AI access.

## Claims boundary

- **Current:** the code-grounded component and deployment baseline in Product Context.
- **Normative:** security, topology, recovery, and operations requirements in the Platform Specification and accepted ADRs.
- **Direction:** the broader RTOI capability model and long-term product trajectory.
- **Positioning:** “leave data where it is,” “single pane of glass,” and similar concise value language on the product site.

Do not answer a Visual KPI question with Platform instructions. Start with [[transpara-product-portfolio]], then use [[transpara-platform-architecture]] and [[transpara-platform-components]].
