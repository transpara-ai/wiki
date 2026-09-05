---
entity: Transpara Data Ingestion and Virtual Data Lake
org: transpara
primary_placement: platform/integrations
placements:
  - platform/integrations
  - platform/capabilities
classification: company-internal
aliases: [VDL, Virtual Data Lake, data ingestion]
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
  - /Transpara/transpara-ai/repos/platform/docs/real-time-operational-intelligence.md
  - https://www.transpara.com/products/transpara-platform/
---

# Transpara Data Ingestion and Virtual Data Lake

Transpara’s Virtual Data Lake (VDL) is the product pattern of using operational data across heterogeneous systems without requiring a wholesale move into one central repository. It combines live source access, selective persistence, normalization, and contextual modeling.

## Current evidence

The maintained component baseline identifies OPC-UA and ODBC extractors, MQTT through EMQX, supported REST/JSON interfaces, tStore backed by TimescaleDB, and a graph context layer. Visual KPI has its own Windows-era connector set and must not be conflated with Platform extractors.

## What “leave data where it is” means

It is positioning shorthand, not an absolute storage invariant. Some data can be queried from its source while selected values, calculated results, metadata, events, indexes, caches, and operational state may be persisted by platform components. Architecture answers must name which path applies.

## Integration checklist

For any source, establish protocol and authentication, ownership, sampling and latency needs, write permissions, network reachability, schema and units, retention, failure behavior, and whether data is live-read, cached, or stored. Validate a connector against its versioned code and configuration before promising support.
