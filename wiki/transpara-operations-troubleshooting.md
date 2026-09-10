---
entity: Transpara Platform Operations and Troubleshooting
org: transpara
primary_placement: platform/troubleshooting
placements:
  - platform/troubleshooting
  - platform/deployment-operations
classification: company-internal
aliases: [Platform troubleshooting, operational reference]
tier: product
status: reviewed
last_compiled: 2026-09-05
reviewed_on: 2026-09-05
review_by: 2026-12-04
source_authority:
  - configuration
  - engineering-docs
sources:
  - /Transpara/transpara-ai/repos/platform/docs/platform-specification.md
  - /Transpara/transpara-ai/repos/platform/docs/airgap-operations.md
  - /Transpara/transpara-ai/repos/platform/docs/platform-findings.md
---

# Transpara Platform Operations and Troubleshooting

This page is a routing guide, not a release runbook. Use the runbook that matches the deployed release, topology, and connectivity mode.

## Triage sequence

1. Record release, topology, environment, time window, symptom, and recent change.
2. Test the user path from ingress and identity through the owning service and its dependencies.
3. Inspect workload readiness, events, logs, metrics, certificates, storage, database health, message flow, and image availability.
4. For air-gapped systems, verify bundle manifest and checksums, the local registry, imported images, restricted-image handling, and registry configuration.
5. Compare observed behavior with the current Platform Findings and accepted ADRs.
6. Preserve evidence before restart, rollback, restore, or other state-changing action.

## Safety rules

- Prefer diagnosis before mutation and rollback before improvised repair.
- Never paste credentials, customer data, or unrestricted support bundles into this repository.
- Treat backup existence and restore verification as different facts.
- Use the supported incident path for security events and material outages.
- Escalate when a proposed workaround breaks an architectural invariant or hides evidence.

The Platform Specification’s verification commands and Air-Gap Operations gates are the authoritative starting points.
