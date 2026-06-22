#!/usr/bin/env python3
"""Public-safe Event 14 live-reader correction fixture for the wiki."""

from __future__ import annotations

import copy
import json
from typing import Any


ALLOWED_FRESHNESS_STATES = {"fresh", "fixture", "source_recorded", "stale", "missing", "unavailable"}
ALLOWED_EVIDENCE_STATES = {
    "source_recorded",
    "corrected",
    "superseded",
    "stale",
    "missing",
    "unavailable",
}
FORBIDDEN_ACTIVE_TERMS = (
    "token",
    "secret",
    "api.github.com",
    "fetch(",
    "XMLHttpRequest",
    "deploy hook",
    "RuntimeBroker",
    "EventGraph write",
    "protected setting",
    "protected action",
    "production readiness",
    "transpara-ai/docs",
    "docs#",
)


FIXTURE: dict[str, Any] = {
    "schema_version": 1,
    "generated_at": "2026-06-22T15:10:35Z",
    "display_only": True,
    "source": {
        "operation_pr": "transpara-ai/civilization-operation#30",
        "operation_pr_url": "https://github.com/transpara-ai/civilization-operation/pull/30",
        "operation_merge_commit": "45b3e9f219d7b81c9991c253d2db4f906d6034bc",
        "operation_reviewed_head": "08786bdcfc6034ac877dd5aa2fbb0e7883cb3b85",
        "authority": "governing authority on file",
        "network_access": "none",
    },
    "freshness": {
        "state": "fixture",
        "as_of": "2026-06-22T15:10:35Z",
        "max_age_seconds": 0,
        "stale_policy": "stale sources are labeled and never rendered as current truth",
        "unavailable_policy": "missing or unavailable sources are displayed as limitations, not zero progress",
    },
    "privacy": {
        "public_safe": True,
        "projection_policy": "explicit-allowlist",
        "network_access": "none",
        "private_fields_omitted": [
            "internal_notes",
            "operator_notes",
            "private_api_url",
            "private_payload",
            "raw_issue_body",
        ],
    },
    "items": [
        {
            "id": "event-14-authority-decision",
            "title": "Event 14 AuthorityDecision",
            "kind": "authority",
            "public_summary": (
                "Governing records authorize one operation export PR lifecycle and one "
                "later wiki display-consumer lifecycle."
            ),
            "evidence_state": "source_recorded",
            "freshness_state": "fixture",
            "source_refs": [
                {
                    "repo": "governing authority",
                    "ref": "authority-on-file",
                    "url": "",
                    "commit": "",
                    "evidence_class": "authority-decision",
                }
            ],
            "limitation": "Authority does not close Gate X, Test 001, process residuals, or residual risk.",
            "display_only": True,
        },
        {
            "id": "stale-public-claim-test-001-green",
            "title": "Superseded Test 001 GREEN Claim",
            "kind": "correction-target",
            "public_summary": (
                "Deterministic fixture for a stale public claim that must not be rendered "
                "as current truth after correction."
            ),
            "evidence_state": "superseded",
            "freshness_state": "stale",
            "source_refs": [
                {
                    "repo": "transpara-ai/civilization-operation",
                    "ref": "fixture/stale-public-claim",
                    "url": "",
                    "commit": "df34112020a10f798a6a10de0670538dd3f23125",
                    "evidence_class": "redacted-source-category",
                }
            ],
            "limitation": "Fixture only; not live source truth.",
            "display_only": True,
        },
        {
            "id": "test-001-yellow-open-tracker",
            "title": "Test 001 Remains YELLOW",
            "kind": "test-state",
            "public_summary": (
                "civilization-operation issue #26 remains the public tracker that Test 001 "
                "is YELLOW pending live evidence and human-gated decisions."
            ),
            "evidence_state": "corrected",
            "freshness_state": "source_recorded",
            "source_refs": [
                {
                    "repo": "transpara-ai/civilization-operation",
                    "ref": "civilization-operation#26",
                    "url": "https://github.com/transpara-ai/civilization-operation/issues/26",
                    "commit": "df34112020a10f798a6a10de0670538dd3f23125",
                    "evidence_class": "open-issue-tracker",
                }
            ],
            "limitation": "YELLOW is not GREEN and this display does not close the incident.",
            "display_only": True,
        },
        {
            "id": "wiki-static-progress-display",
            "title": "Existing Static Progress Display",
            "kind": "display-evidence",
            "public_summary": (
                "Civilization Wiki previously accepted static operation-owned progress "
                "evidence as display-only evidence."
            ),
            "evidence_state": "source_recorded",
            "freshness_state": "stale",
            "source_refs": [
                {
                    "repo": "transpara-ai/civilization-wiki",
                    "ref": "civilization-wiki#23",
                    "url": "https://github.com/transpara-ai/civilization-wiki/pull/23",
                    "commit": "236aef9780d240eb04c3616b847286cdd2d0b756",
                    "evidence_class": "static-display-pr",
                }
            ],
            "limitation": "Static display evidence is stale for Event 14 and is not live-reader proof.",
            "display_only": True,
        },
    ],
    "corrections": [
        {
            "correction_id": "correction-test-001-yellow-not-green",
            "sequence": 1,
            "supersedes_item_id": "stale-public-claim-test-001-green",
            "prior_public_item_id": "stale-public-claim-test-001-green",
            "prior_public_state": "green",
            "correction_reason": "The public-safe tracker shows Test 001 remains YELLOW, not GREEN.",
            "corrected_item_id": "test-001-yellow-open-tracker",
            "corrected_state": "yellow",
            "corrected_at": "2026-06-22T15:10:35Z",
            "source_refs": [
                {
                    "repo": "transpara-ai/civilization-operation",
                    "ref": "civilization-operation#26",
                    "url": "https://github.com/transpara-ai/civilization-operation/issues/26",
                    "commit": "df34112020a10f798a6a10de0670538dd3f23125",
                    "evidence_class": "open-issue-tracker",
                },
                {
                    "repo": "transpara-ai/civilization-operation",
                    "ref": "civilization-operation#30",
                    "url": "https://github.com/transpara-ai/civilization-operation/pull/30",
                    "commit": "45b3e9f219d7b81c9991c253d2db4f906d6034bc",
                    "evidence_class": "public-safe-export-pr",
                },
            ],
            "limitation": (
                "This is public-safe correction display evidence; it does not publish a "
                "live site correction or close Test 001."
            ),
            "display_only": True,
        }
    ],
    "omitted_sources": [
        {
            "id": "deployed-live-reader-route",
            "title": "Deployed Live Reader Route",
            "reason": "unavailable-source",
            "freshness_state": "unavailable",
            "public_summary": "No deployed live-reader route evidence is available in this bounded display.",
            "source_ref": "not-collected",
            "source_repo": "transpara-ai/civilization-wiki",
        },
        {
            "id": "public-correction-deployment-proof",
            "title": "Public Correction Deployment Proof",
            "reason": "missing-public-projection",
            "freshness_state": "missing",
            "public_summary": "No deployed public correction proof is available in this bounded display.",
            "source_ref": "not-provided",
            "source_repo": "transpara-ai/civilization-wiki",
        },
        {
            "id": "private-runtime-source",
            "title": "Private Runtime Source",
            "reason": "outside-authorized-scope",
            "freshness_state": "unavailable",
            "public_summary": (
                "Runtime, production, private repository, and protected-setting sources "
                "are outside this Level 0 public-safe display."
            ),
            "source_ref": "outside-authorized-scope",
            "source_repo": "multiple",
        },
    ],
    "audit_report": {
        "shape": "AuditReport",
        "status": "display-consumer-fixture-ready",
        "validation_commands": [
            "python3 compile/test_live_reader_correction.py",
            "npm run verify",
        ],
        "authority_boundary": [
            "display-only",
            "no live private API fetch",
            "no runtime mutation",
            "no production claim",
            "no gate closure",
            "no autonomy increase",
            "no value allocation",
        ],
    },
}


def build_fixture() -> dict[str, Any]:
    return copy.deepcopy(FIXTURE)


def validate_fixture(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if payload.get("display_only") is not True:
        errors.append("display_only must be true")
    if payload.get("privacy", {}).get("public_safe") is not True:
        errors.append("privacy.public_safe must be true")
    if payload.get("source", {}).get("network_access") != "none":
        errors.append("source.network_access must be none")
    if payload.get("privacy", {}).get("network_access") != "none":
        errors.append("privacy.network_access must be none")
    freshness = payload.get("freshness") or {}
    if freshness.get("state") not in {"fresh", "fixture", "source_recorded"}:
        errors.append("global freshness must fail closed unless fresh, fixture, or source_recorded")

    items = payload.get("items")
    if not isinstance(items, list) or not items:
        errors.append("items must be a non-empty list")
        items = []
    item_ids = {item.get("id") for item in items if isinstance(item, dict)}
    for item in items:
        if item.get("display_only") is not True:
            errors.append(f"{item.get('id', '<missing>')} must be display-only")
        if item.get("freshness_state") not in ALLOWED_FRESHNESS_STATES:
            errors.append(f"{item.get('id', '<missing>')} has invalid freshness_state")
        if item.get("evidence_state") not in ALLOWED_EVIDENCE_STATES:
            errors.append(f"{item.get('id', '<missing>')} has invalid evidence_state")
        if not item.get("source_refs"):
            errors.append(f"{item.get('id', '<missing>')} must carry source refs")
        if not item.get("limitation"):
            errors.append(f"{item.get('id', '<missing>')} must carry limitation text")

    corrections = payload.get("corrections")
    if not isinstance(corrections, list):
        errors.append("corrections must be a list")
        corrections = []
    for correction in corrections:
        if correction.get("display_only") is not True:
            errors.append(f"{correction.get('correction_id', '<missing>')} must be display-only")
        for key in ("supersedes_item_id", "prior_public_item_id", "corrected_item_id"):
            if correction.get(key) not in item_ids:
                errors.append(f"{correction.get('correction_id', '<missing>')} references missing {key}")
        if not correction.get("limitation"):
            errors.append(f"{correction.get('correction_id', '<missing>')} must carry limitation text")

    omitted = payload.get("omitted_sources")
    if not isinstance(omitted, list):
        errors.append("omitted_sources must be a list")
        omitted = []
    for source in omitted:
        if source.get("freshness_state") not in {"missing", "unavailable", "stale"}:
            errors.append(f"{source.get('id', '<missing>')} omitted source must be missing, unavailable, or stale")
        if not source.get("reason") or not source.get("public_summary"):
            errors.append(f"{source.get('id', '<missing>')} omitted source must carry reason and summary")

    serialized = json.dumps(payload, sort_keys=True)
    for term in FORBIDDEN_ACTIVE_TERMS:
        if term in serialized:
            errors.append(f"forbidden active term appears in fixture: {term}")
    return errors


def render_js_fixture(payload: dict[str, Any] | None = None) -> str:
    fixture = build_fixture() if payload is None else copy.deepcopy(payload)
    errors = validate_fixture(fixture)
    if errors:
        raise ValueError("; ".join(errors))
    return (
        "window.CIVILIZATION_LIVE_READER_CORRECTION = "
        + json.dumps(fixture, indent=2, sort_keys=True)
        + ";\n"
    )
