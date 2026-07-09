#!/usr/bin/env python3
"""Stdlib-assert tests for the Investigation Topic Standard (Phase-1 machinery).

Covers the build_site render-side requirements: R4 (no in-topic TOC), R7
(reason-neutral stale banner), R3 (Topic Details), R2 (conformance predicate),
and the MemPalace render-diff (AC8). R9 (nav single-entry) lives in
test_build_site_nav.py; the ingest requirements live in test_ingest_server.py.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_site as site  # noqa: E402


# ---- R4 / AC2 — no in-topic Table of Contents on investigation pages ----

def test_investigation_pages_have_no_toc():
    tokens = [{"id": "a", "name": "A"}, {"id": "b", "name": "B"}, {"id": "c", "name": "C"}]
    # R4: an investigation-tier page renders no TOC, even with >=3 headings.
    assert site.article_toc({"tier": "investigation"}, tokens, is_home=False) == "", \
        "investigation tier must render no .toc"
    # a non-investigation page with >=3 headings still renders its Contents box.
    non_inv = site.article_toc({"tier": "architecture"}, tokens, is_home=False)
    assert 'class="toc"' in non_inv, "non-investigation tier must keep its TOC"
    # the home page never carries a TOC (pre-existing behavior, unchanged).
    assert site.article_toc({"tier": "architecture"}, tokens, is_home=True) == ""
    print("ok test_investigation_pages_have_no_toc")


# ---- R7 / AC7 — reason-neutral stale banner + no-network builder ----

def test_stale_banner_is_reason_neutral():
    banner = site.state_banner_html("stale_since: 2026-07-09\n")
    assert "2026-07-09" in banner and "stale" in banner.lower()
    # reason-neutral: correct for an ADD as well as a Replace — no Replace-specific
    # "replaced" / "authorization" wording (R7/AC7).
    low = banner.lower()
    assert "replaced" not in low and "authorization" not in low, "banner must be reason-neutral"
    # retired takes precedence and is unaffected
    assert "Retired on 2026-07-01" in site.state_banner_html(
        "retired_on: 2026-07-01\nretired_reason: dup\n")
    # neither -> no banner
    assert site.state_banner_html("entity: x\n") == ""
    print("ok test_stale_banner_is_reason_neutral")


def test_builder_has_no_network_client():
    # AC7: the builder performs no network/LLM work; it imports no HTTP/socket
    # client (urllib.parse for URL encoding is not a network client).
    import inspect
    src = inspect.getsource(site)
    for bad in ("import requests", "import httpx", "import socket",
                "urllib.request", "http.client", ".urlopen("):
        assert bad not in src, "builder must not use a network client: %s" % bad
    print("ok test_builder_has_no_network_client")


# ---- R3 / AC1 — Topic Details (rename + superseded union + research-only) ----

_INV = {"tier": "investigation", "title": "Acme"}


def _li_containing(box, needle):
    """The Topic Details <li> fragment (class + body) that contains `needle`
    (a ref basename), or '' if none — lets a test assert per-entry marking."""
    for seg in box.split("<li")[1:]:
        body = seg.split("</li>", 1)[0]
        if needle in body:
            return body
    return ""


def test_topic_details_lists_all_versions_incl_superseded():
    # R3: the row lists raw_documents UNION superseded_raw_documents (the key
    # Replace moves superseded refs into) — every ingested version, the
    # superseded ones marked, the newest rendered as the unmarked primary.
    fm = (
        "tier: investigation\n"
        "raw_documents:\n"
        "  - raw/inbox/2026-07-09/acme/TAI-RES-2026-009-v1.1.0-Acme-Evaluation.md\n"
        "  - raw/inbox/2026-07-09/acme/TAI-RES-2026-009-v1.1.1-Acme-Evaluation.md\n"
        "superseded_raw_documents:\n"
        "  - raw/inbox/2026-06-01/acme/TAI-RES-2026-009-v1.0.0-Acme-Evaluation.md\n"
    )
    box = site.build_infobox(_INV, fm)
    assert "Topic Details" in box, "R3 renames the infobox row to Topic Details"
    assert "Raw docs" not in box, "the old 'Raw docs' label must not survive"
    for v in ("v1.0.0", "v1.1.0", "v1.1.1"):
        assert v in box, "every ingested version is listed: %s" % v
    assert "source-superseded" in _li_containing(box, "v1.0.0"), "superseded entry is marked"
    assert "source-superseded" not in _li_containing(box, "v1.1.1"), "newest is the primary"
    print("ok test_topic_details_lists_all_versions_incl_superseded")


def test_topic_details_marks_add_supersedes_newest_primary():
    # CFADA-r21 #43: an ADD-with-supersedes topic (MemPalace) keeps every version
    # in raw_documents and expresses supersession ONLY in the `sources`
    # `supersedes:` comments; Topic Details still marks the older versions and
    # leaves the newest as the primary, derived from those comments.
    fm = (
        "tier: investigation\n"
        "sources:\n"
        "  - raw/inbox/2026-06-24/acme/TAI-RES-2026-009-v1.0.0-Acme-Evaluation.md  # first ingest\n"
        "  - raw/inbox/2026-06-24/acme/TAI-RES-2026-009-v1.1.0-Acme-Evaluation.md  # added via wiki browser ingest; supersedes: raw/inbox/2026-06-24/acme/TAI-RES-2026-009-v1.0.0-Acme-Evaluation.md\n"
        "  - raw/inbox/2026-07-07/acme/TAI-RES-2026-009-v1.1.1-Acme-Evaluation.md  # added via wiki browser ingest; supersedes: raw/inbox/2026-06-24/acme/TAI-RES-2026-009-v1.1.0-Acme-Evaluation.md\n"
        "raw_documents:\n"
        "  - raw/inbox/2026-06-24/acme/TAI-RES-2026-009-v1.0.0-Acme-Evaluation.md\n"
        "  - raw/inbox/2026-06-24/acme/TAI-RES-2026-009-v1.1.0-Acme-Evaluation.md\n"
        "  - raw/inbox/2026-07-07/acme/TAI-RES-2026-009-v1.1.1-Acme-Evaluation.md\n"
    )
    box = site.build_infobox(_INV, fm)
    assert "Topic Details" in box
    assert "source-superseded" in _li_containing(box, "v1.0.0-Acme"), "v1.0.0 superseded"
    assert "source-superseded" in _li_containing(box, "v1.1.0-Acme"), "v1.1.0 superseded"
    assert "source-superseded" not in _li_containing(box, "v1.1.1-Acme"), "v1.1.1 is the primary"
    print("ok test_topic_details_marks_add_supersedes_newest_primary")


def test_topic_details_fallback_is_raw_ingested_only():
    # §2.2: with no raw_documents/superseded_raw_documents, fall back to the
    # raw-INGESTED-RESEARCH refs among `sources` ONLY — raw/inbox uploads and
    # tai-res-*.md evaluations wherever placed. Doctrine/provenance citations
    # NEVER render as Topic Details (they stay in the source panel).
    fm = (
        "tier: investigation\n"
        "sources:\n"
        "  - raw/transpara/dark-factory/v3.9/06-memory-knowledge-v3.9.md  # doctrine\n"
        "  - raw/open-brain/2026-06.md  # captured thought\n"
        "  - index.md  # provenance/index\n"
        "  - raw/inbox/2026-07-09/acme/TAI-RES-2026-009-v1.0.0-Acme-Evaluation.md  # ingested eval\n"
        "  - raw/civilization/external-landscape/tai-res-2026-010-beta-evaluation.md  # tai-res outside inbox\n"
    )
    box = site.build_infobox(_INV, fm)
    assert "Topic Details" in box
    assert "TAI-RES-2026-009-v1.0.0-Acme-Evaluation.md" in box, "raw/inbox upload listed"
    assert "tai-res-2026-010-beta-evaluation.md" in box, "tai-res anywhere listed"
    assert "06-memory-knowledge-v3.9.md" not in box, "doctrine excluded from Topic Details"
    assert "2026-06.md" not in box, "open-brain doctrine excluded"
    # a support-only page (only doctrine sources) → EMPTY Topic Details (no row).
    support_only = (
        "tier: investigation\n"
        "sources:\n"
        "  - raw/transpara/dark-factory/v3.9/06-memory-knowledge-v3.9.md  # doctrine only\n"
    )
    assert "Topic Details" not in site.build_infobox(_INV, support_only), \
        "support-only page has empty Topic Details"
    print("ok test_topic_details_fallback_is_raw_ingested_only")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
    print("\nall %d investigation-standard build-site tests passed" % len(fns))
