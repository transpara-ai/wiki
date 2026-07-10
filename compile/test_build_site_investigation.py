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
        "  - /Transpara/transpara-ai/wiki/raw/x/TAI-RES-2026-011-abs-evaluation.md  # absolute path — source panel only\n"
    )
    box = site.build_infobox(_INV, fm)
    assert "Topic Details" in box
    assert "TAI-RES-2026-009-v1.0.0-Acme-Evaluation.md" in box, "raw/inbox upload listed"
    assert "tai-res-2026-010-beta-evaluation.md" in box, "tai-res anywhere (relative raw/) listed"
    assert "06-memory-knowledge-v3.9.md" not in box, "doctrine excluded from Topic Details"
    assert "2026-06.md" not in box, "open-brain doctrine excluded"
    # CFAR (Codex): an absolute /Transpara/ tai-res citation is doctrine/provenance
    # — it must NOT be admitted to Topic Details by the basename allowlist.
    assert "TAI-RES-2026-011-abs-evaluation.md" not in box, "absolute path excluded"
    assert site.is_raw_ingested_research(
        "/Transpara/transpara-ai/wiki/raw/x/TAI-RES-2026-011-abs-evaluation.md") is False
    # a support-only page (only doctrine sources) → EMPTY Topic Details (no row).
    support_only = (
        "tier: investigation\n"
        "sources:\n"
        "  - raw/transpara/dark-factory/v3.9/06-memory-knowledge-v3.9.md  # doctrine only\n"
    )
    assert "Topic Details" not in site.build_infobox(_INV, support_only), \
        "support-only page has empty Topic Details"
    print("ok test_topic_details_fallback_is_raw_ingested_only")


def test_fm_scalar_and_fm_list_strip_inline_comments():
    # CFAR (Codex): value-load-bearing scalar/list reads strip inline comments, so
    # a commented scalar or a commented INLINE list can't pollute a gate.
    fm = ("entity: Foo  # note\n"
          "tier: investigation  # canonical\n"
          "raw_documents: [raw/inbox/a/TAI-RES-1.md, raw/inbox/a/TAI-RES-2.md]  # inline\n")
    assert site.fm_scalar(fm, "tier") == "investigation"
    assert site.fm_scalar(fm, "entity") == "Foo"
    assert site.fm_list(fm, "raw_documents") == \
        ["raw/inbox/a/TAI-RES-1.md", "raw/inbox/a/TAI-RES-2.md"], "inline commented list parses"
    print("ok test_fm_scalar_and_fm_list_strip_inline_comments")


def test_topic_details_includes_superseded_sources():
    # CFAR (Codex): a legacy sources-only Replace moves the old ingested ref into
    # `superseded_sources` (not superseded_raw_documents); Topic Details must still
    # list it, marked superseded, so no raw ingested version is dropped (R3).
    fm = (
        "tier: investigation\n"
        "raw_documents:\n"
        "  - raw/inbox/2026-07-09/acme/TAI-RES-2026-009-v2.0.0-Acme-Evaluation.md\n"
        "superseded_sources:\n"
        "  - raw/inbox/2026-06-01/acme/TAI-RES-2026-009-v1.0.0-Acme-Evaluation.md\n"
    )
    box = site.build_infobox(_INV, fm)
    assert "Topic Details" in box
    assert "v1.0.0" in box and "v2.0.0" in box, "both versions are listed"
    assert "source-superseded" in _li_containing(box, "v1.0.0"), "the superseded_sources ref is marked"
    assert "source-superseded" not in _li_containing(box, "v2.0.0"), "the current version is the primary"
    print("ok test_topic_details_includes_superseded_sources")


# ---- R2 / AC6(P1) — investigation conformance predicate ----

_CONFORMANT_FM = (
    "entity: Acme\n"
    "aliases:\n"
    "  - Acme\n"
    "tier: investigation\n"
    "status: compiled\n"
    "last_compiled: 2026-07-09\n"
    'civilization_contribution: "Contributed the widget governance pattern."\n'
    "raw_documents:\n"
    "  - raw/inbox/2026-07-09/acme/TAI-RES-2026-009-v1.0.0-Acme-Evaluation.md\n"
    "current_research_version: 1.0.0\n"
    "sources:\n"
    "  - raw/inbox/2026-07-09/acme/TAI-RES-2026-009-v1.0.0-Acme-Evaluation.md\n"
)

_CONFORMANT_BODY = (
    "# Acme\n"
    "\n"
    "**Acme is a strong external match for the advisory recall layer.** It does X.\n"
    "\n"
    "## What Changed with the Research\n"
    "Body.\n"
    "\n"
    "## The Boundary\n"
    "Body.\n"
    "\n"
    "## Capability Read\n"
    "Body.\n"
    "\n"
    "## Benchmark Reality\n"
    "Body.\n"
    "\n"
    "## Sources & Provenance\n"
    "Body.\n"
)


def test_investigation_conformance_predicate():
    # conformant fixture -> empty deficiency set.
    assert site.investigation_conformance(_CONFORMANT_FM, _CONFORMANT_BODY) == set(), \
        "a canonical investigation page conforms"

    # missing required frontmatter key (entity).
    no_entity = "\n".join(
        l for l in _CONFORMANT_FM.splitlines() if not l.startswith("entity:")) + "\n"
    d = site.investigation_conformance(no_entity, _CONFORMANT_BODY)
    assert d and any("entity" in x for x in d), "missing entity is a deficiency"

    # present-but-empty render-driving field (presence != non-empty).
    empty_contrib = _CONFORMANT_FM.replace(
        'civilization_contribution: "Contributed the widget governance pattern."',
        'civilization_contribution: ""')
    d = site.investigation_conformance(empty_contrib, _CONFORMANT_BODY)
    assert any("civilization_contribution" in x for x in d), "empty contribution is a deficiency"

    # missing required heading.
    no_boundary = _CONFORMANT_BODY.replace("## The Boundary\nBody.\n\n", "")
    d = site.investigation_conformance(_CONFORMANT_FM, no_boundary)
    assert any("Boundary" in x for x in d), "a missing heading is a deficiency"

    # non-bold Summary lead.
    plain_lead = _CONFORMANT_BODY.replace(
        "**Acme is a strong external match for the advisory recall layer.**",
        "Acme is a strong external match for the advisory recall layer.")
    assert "non-bold-lead" in site.investigation_conformance(_CONFORMANT_FM, plain_lead), \
        "a non-bold lead is a deficiency"

    # out-of-order headings.
    swapped = _CONFORMANT_BODY.replace(
        "## What Changed with the Research\nBody.\n\n## The Boundary\nBody.\n\n",
        "## The Boundary\nBody.\n\n## What Changed with the Research\nBody.\n\n")
    assert "out-of-order" in site.investigation_conformance(_CONFORMANT_FM, swapped), \
        "misordered headings are a deficiency"

    # Integration Packet present but AFTER Sources & Provenance -> out of order.
    ip_after = _CONFORMANT_BODY.replace(
        "## Sources & Provenance\nBody.\n",
        "## Sources & Provenance\nBody.\n\n## Integration Packet\nBody.\n")
    assert "out-of-order" in site.investigation_conformance(_CONFORMANT_FM, ip_after), \
        "Integration Packet after Sources is out of order"

    # Integration Packet in the canonical slot (before Sources) -> conformant.
    ip_before = _CONFORMANT_BODY.replace(
        "## Sources & Provenance\nBody.\n",
        "## Integration Packet\nBody.\n\n## Sources & Provenance\nBody.\n")
    assert site.investigation_conformance(_CONFORMANT_FM, ip_before) == set(), \
        "Integration Packet before Sources is conformant"

    # a free extra heading (## Placement) is ignored by the order check.
    with_extra = _CONFORMANT_BODY.replace(
        "## What Changed with the Research\n",
        "## Placement\nBody.\n\n## What Changed with the Research\n")
    assert site.investigation_conformance(_CONFORMANT_FM, with_extra) == set(), \
        "a free extra heading does not break conformance"

    # CFAR (Codex): tier must be exactly `investigation` — a mistiered page (a
    # present-but-wrong tier) is non-conformant, not merely present-key-OK.
    mistiered = _CONFORMANT_FM.replace("tier: investigation", "tier: architecture")
    assert "wrong-tier" in site.investigation_conformance(mistiered, _CONFORMANT_BODY), \
        "a non-investigation tier is a deficiency"

    # CFAR (Codex): fm_scalar strips inline comments, so a comment-only required
    # field reads as EMPTY (deficiency) and a commented tier value still reads as
    # investigation (no false wrong-tier).
    comment_only = _CONFORMANT_FM.replace(
        'civilization_contribution: "Contributed the widget governance pattern."',
        "civilization_contribution: # TBD")
    assert any("civilization_contribution" in x for x
               in site.investigation_conformance(comment_only, _CONFORMANT_BODY)), \
        "a comment-only required field is a deficiency"
    commented_tier = _CONFORMANT_FM.replace(
        "tier: investigation", "tier: investigation  # canonical")
    assert "wrong-tier" not in site.investigation_conformance(commented_tier, _CONFORMANT_BODY), \
        "a commented tier value still reads as investigation"
    print("ok test_investigation_conformance_predicate")


def test_support_only_empty_raw_documents_conforms():
    # CFADA-r20 #41: a support-only page with an EMPTY raw_documents list still
    # conforms — raw_documents is exempt from the non-empty check (else AC6/P2
    # would be unsatisfiable for support-only pages).
    empty_raw = _CONFORMANT_FM.replace(
        "raw_documents:\n"
        "  - raw/inbox/2026-07-09/acme/TAI-RES-2026-009-v1.0.0-Acme-Evaluation.md\n",
        "raw_documents: []\n")
    assert site.investigation_conformance(empty_raw, _CONFORMANT_BODY) == set(), \
        "support-only page (empty raw_documents) conforms"
    print("ok test_support_only_empty_raw_documents_conforms")


# ---- AC8 — MemPalace render diff is exactly {label, TOC, supersession} ----

def test_mempalace_render_diff_is_label_toc_and_supersession():
    # AC8: Phase-1 machinery changes MemPalace's render in EXACTLY three ways —
    # the infobox label (Raw docs -> Topic Details), the removed in-topic TOC
    # (R4), and the Topic Details supersession markers (older versions marked,
    # newest primary; AC1/CFADA-r21 #43). Nothing else: all 8 body headings and
    # the Civilization Contribution box are still present (the dated-heading
    # generalization is Phase-2 data-only, not machinery).
    fm, body = site.split_fm((site.WIKI / "mempalace.md").read_text())
    meta = site.article_meta()["mempalace"]
    body_html, toc_tokens = site.to_html(
        body, {}, site.article_source_refs(fm), source_slug="mempalace")
    infobox = site.build_infobox(meta, fm)

    # (1) infobox label change.
    assert "Topic Details" in infobox and "Raw docs" not in infobox, "Raw docs -> Topic Details"
    # (2) no in-topic TOC on an investigation-tier page (R4).
    assert site.article_toc(meta, toc_tokens, is_home=False) == "", "in-topic TOC removed"
    # (3) Topic Details supersession markers — exactly two older versions marked,
    #     the newest (v1.1.1) the unmarked primary.
    assert infobox.count("source-superseded-badge") == 2, "two superseded versions marked"
    assert "v1.1.1" in infobox and "source-superseded" not in _li_containing(infobox, "v1.1.1"), \
        "newest version is the unmarked primary"

    # no other change: all 8 MemPalace body headings still present (asserted on
    # stable heading ids, robust to inline auto-linking in heading text) ...
    for hid in (
        "placement", "decision-record-and-adr-disposition",
        "what-changed-with-tai-res-2026-004", "the-boundary", "capability-read",
        "benchmark-reality", "integration-packet", "sources-provenance",
    ):
        assert ('id="%s"' % hid) in body_html, "body heading preserved: %s" % hid
    # ... and the Civilization Contribution box is intact.
    contribution = site.build_contribution_box(fm)
    assert "contribution-box" in contribution, "Civilization Contribution box preserved"
    print("ok test_mempalace_render_diff_is_label_toc_and_supersession")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
    print("\nall %d investigation-standard build-site tests passed" % len(fns))
