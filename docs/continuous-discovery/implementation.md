---
doc_id: "TAI-WIKI-DISCOVERY-IMPLEMENTATION"
title: "Continuous discovery implementation"
doc_type: "implementation-record"
version: "0.2.0"
status: "draft"
created: "2026-09-18"
updated: "2026-09-18"
owner: "Transpara"
steward: "Codex"
author: "Codex"
reviewer: "Pending human review"
project: "wiki"
repo: "transpara-ai/wiki"
classification: "company-internal"
supersedes: []
canonical: false
version_history: "First controlled revision; prior unversioned content remains in Git history"
---

# Continuous discovery implementation

Factory Order: implement the user-approved continuous discovery, research and reviewed publication plan on `codex/wiki-architecture-comparison`. Critical triggers: new outbound source collection using host credentials; retained private source evidence supplied to host models; reviewed changes entering canonical publication. This order authorizes local implementation and tests, not production credentials, service installation, monitor enrollment or production activation. Those effects require maintainer acceptance and explicit authority immediately before activation.

## Design and threat model

Canonical Markdown remains authoritative. A private SQLite database holds source configurations, immutable evidence versions, discoveries, findings, investigations, jobs, proposals and review records. All workflow APIs require the existing authoring grant. Saved research is additionally principal scoped. No private state enters static assets. Evidence defaults to internal; curators explicitly select permitted classification in source configuration. Publication refuses any article audience wider than its supporting evidence.

Fetchers accept public HTTPS destinations, validate and pin DNS addresses, reject private/reserved addresses and userinfo, and revalidate redirects. GitHub credentials are selected from a host-owned file and used only on api.github.com. Page credentials are restricted to exact approved origins. Source data never chooses credentials, tools, execution commands or publication authority. Secret quarantine precedes retention and model input. Unsupported documents are recorded without inventing extracted content. Errors cannot overwrite good evidence.

Jobs use durable leases and retry deadlines. Evidence and checkpoints commit together before progress advances. Content deduplication preserves discovery provenance. Repeated scans do not invoke models when extracted evidence has not changed. Review inputs freeze source and article revisions. Two distinct model families receive independent initial requests. Neither ranking nor agreement authorizes publication. Human approval is checked under the same write lock as authoring; changes invalidate approval. Publication journals retain original Markdown and accepted provenance, allowing recovery after a failed build or process interruption. Static directory exchange preserves the prior served build until validation succeeds.

Threat review must exercise SSRF/redirects, credential leakage, source instruction attacks, fabricated citations, stale source/article approval, cross-audience access, concurrent jobs, partial collection and publication recovery. Operational pilot measurements and actual cross-provider qualification require deployment and are not replaced by unit tests.

## Delivery and operations

See [operator guide](../../compile/DISCOVERY.md) for configuration, API contracts, worker startup, backups and rollout. No monitor is created or enabled by installation. Workplace adapters are an explicit future extension; automatic publication, OCR, transcription and unrestricted crawling are excluded.

## Document control correction

TLC route: Designed. The correction binds Transpara document-control frontmatter
and document SemVer to the full reviewed article diff, preserves existing metadata,
and synchronizes application release metadata at v0.9.0. See the operator guide's
[document-control contract](../../compile/DISCOVERY.md#document-control-and-semantic-versions)
and [CFAR ingestion/research swim lanes and timing](../../compile/DISCOVERY.md#cfar-ingestion-and-research-swim-lanes).
The reviewers are independent, initially blind model-family assessments; they do
not currently run tool-using investigations. Existing comparison scores describe
the original v0.8.3 baseline.

Validation: 33 workflow tests, 12 release tests, five provider integration tests,
real isolated publication with exact reviewed Markdown and generated version
checks, and five browser workspace journeys passed. Required frontmatter and
unique document identities were checked across nine documents. Ordinary review
covered preservation, honest legacy version baselines, immutable exported
snapshots, review invalidation on SemVer changes and application-version parity.

## Local review record

The implementation review covers audience enforcement, SSRF/DNS/redirect restrictions, model-family independence, evidence and article revision checks, capture/checkpoint transactions, restart leases and journal recovery. Relevant adversarial cases are executable in `compile/test_knowledge.py`; browser journeys are in `tests/knowledge.spec.js`. No production acceptance, live cross-provider qualification or human pilot outcome is asserted. Named production activation effects remain unperformed pending maintainer acceptance.

## Verification evidence

- Existing Python suite passed; 30 additional workflow tests cover durable state, private saves, scopes, SSRF/redirects, credential origins, replay, score uncertainty, blind review, stale approvals and rollback.
- Real isolated publication passed through the actual builder, canonical Markdown/provenance, Ask index and generated-link validation; the test is retained as `compile/test_knowledge_publication.py`.
- JavaScript syntax, unit and DOM suites passed. The full browser run passed 68 cases and identified one Ask compatibility regression; after the fix, all ten focused Ask/workspace journeys passed, including transient follow-ups and explicit audience review after access loss.
- Publication profiles and generated links were checked. No live source enrollment or provider invocation was used for these tests.
- Human calibration labels, the five-user usability pilot and the 30% review-time target remain operational acceptance work.

## Document revision history

| Version | Date | Change |
| --- | --- | --- |
| 0.2.0 | 2026-09-18 | Record enforced document control, SemVer, CFAR timing and focused correction validation. |
| 0.1.0 | 2026-09-18 | Establish Transpara document control and a SemVer baseline for previously unversioned content. |
