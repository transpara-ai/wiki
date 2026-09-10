---
entity: Transpara Platform Security and Compliance
org: transpara
primary_placement: platform/security-compliance
placements:
  - platform/security-compliance
classification: company-internal
aliases: [Platform security, compliance mapping]
tier: product
status: reviewed
last_compiled: 2026-09-05
reviewed_on: 2026-09-05
review_by: 2026-12-04
source_authority:
  - code
  - configuration
  - engineering-docs
  - adr
sources:
  - /Transpara/transpara-ai/repos/platform/docs/platform-specification.md
  - /Transpara/transpara-ai/repos/platform/docs/platform-findings.md
  - /Transpara/transpara-ai/repos/platform/docs/architecture-decision-records.md
---

# Transpara Platform Security and Compliance

The Platform Specification maps platform controls to NIST SP 800-53 Rev. 5, IEC 62443, and SOC 2 Trust Services Criteria. A mapping documents design intent and audit traceability; it is not, by itself, a certification or proof that every control is deployed.

## Normative control families

The specification covers identity and RBAC, north–south and east–west network boundaries, secrets at rest, admission control and pod security, egress, host hardening, image and software supply chain, runtime detection, backup integrity, certificate lifecycle, recovery, logging, metrics, and incident response.

## Evidence rule

For a security assertion, record:

1. the normative requirement and control mapping;
2. the enforcement mechanism in code or configuration;
3. the verification command or automated check;
4. the observed result for the relevant release and environment;
5. any open finding or compensating control.

Do not collapse “specified,” “implemented,” “verified,” and “certified” into one status. Platform Findings is the maintained gap record; it may contain sensitive operational detail and should be shared only within its authorization boundary.
