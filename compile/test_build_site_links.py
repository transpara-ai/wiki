#!/usr/bin/env python3
"""Stdlib-assert tests for source-link rendering in compile/build_site.py."""
import pathlib
import sys
import tempfile
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_site as site  # noqa: E402


def with_source(ref, text, fn):
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        path = root / ref
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        old_root = site.ROOT
        old_allowed = site.ALLOWED_SOURCE_ROOTS
        old_links = site.SOURCE_LINKS
        try:
            site.ROOT = root
            site.ALLOWED_SOURCE_ROOTS = [root]
            site.SOURCE_LINKS = {ref: "source/example.html"}
            site.source_link_aliases.cache_clear()
            fn()
        finally:
            site.ROOT = old_root
            site.ALLOWED_SOURCE_ROOTS = old_allowed
            site.SOURCE_LINKS = old_links
            site.source_link_aliases.cache_clear()


def test_links_declared_adr_identifier_in_text_and_code_spans():
    ref = "raw/transpara/dark-factory/archive/v3/adrs/ADR-0008-mempalace-verbatim-recall.md"

    def run():
        body = '<p>ADR-0008 should link, and <code>ADR-0008</code> should also link.</p>'
        out = site.link_source_code_alias_refs(body, [ref])
        out = site.link_source_alias_refs(out, [ref])
        assert '<a class="source-ref-link" href="source/example.html">ADR-0008</a>' in out
        assert '<a class="source-code-link" href="source/example.html"><code>ADR-0008</code></a>' in out
        assert out.count("source-ref-link") == 1, out
        assert out.count("source-code-link") == 1, out

    with_source(ref, "# ADR-0008: Use MemPalace as the verbatim recall substrate\n", run)
    print("ok test_links_declared_adr_identifier_in_text_and_code_spans")


def test_links_doc_id_and_decision_aliases_from_declared_source():
    ref = "raw/transpara/dark-factory/v3.9/01-unified-architecture-decisions-v3.9.md"
    text = (
        "---\n"
        "doc_id: DF-V3.9-ADR-001\n"
        "title: Dark Factory v3.9 Unified Architecture Decisions\n"
        "---\n\n"
        "# Dark Factory v3.9 Unified Architecture Decisions\n"
    )

    def run():
        body = "<p>Decision 15 and DF-V3.9-ADR-001 should both open the document.</p>"
        out = site.link_source_alias_refs(body, [ref])
        assert out.count('href="source/example.html"') == 2, out
        assert ">Decision 15</a>" in out
        assert ">DF-V3.9-ADR-001</a>" in out

    with_source(ref, text, run)
    print("ok test_links_doc_id_and_decision_aliases_from_declared_source")


def test_path_shaped_alias_does_not_rewrap_existing_source_code_link():
    ref = "raw/example.md"

    def run():
        body = "<p><code>raw/example.md</code></p>"
        out = site.link_source_code_refs(body)
        out = site.link_source_code_alias_refs(out, [ref])
        assert out.count('<a class="source-code-link"') == 1, out
        assert "<a class=\"source-code-link\" href=\"source/example.html\"><code>raw/example.md</code></a>" in out
        assert "<a class=\"source-code-link\" href=\"source/example.html\"><code><a" not in out

    with_source(ref, "---\ntitle: raw/example.md\n---\n# Example\n", run)
    print("ok test_path_shaped_alias_does_not_rewrap_existing_source_code_link")


def test_generic_source_stems_do_not_link_in_prose():
    refs = ["index.md", "compile/refresh.py"]

    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        (root / "compile").mkdir(parents=True, exist_ok=True)
        (root / "index.md").write_text("---\ntitle: Transpara-AI Civilization Wiki\n---\n# Index\n")
        (root / "compile" / "refresh.py").write_text("# refresh helper\n")
        old_root = site.ROOT
        old_allowed = site.ALLOWED_SOURCE_ROOTS
        old_links = site.SOURCE_LINKS
        try:
            site.ROOT = root
            site.ALLOWED_SOURCE_ROOTS = [root]
            site.SOURCE_LINKS = {
                "index.md": "source/index.html",
                "compile/refresh.py": "source/refresh.html",
            }
            site.source_link_aliases.cache_clear()
            out = site.link_source_alias_refs(
                "<p>The index page can refresh the local wiki shell.</p>",
                refs,
            )
            assert "source-ref-link" not in out, out
        finally:
            site.ROOT = old_root
            site.ALLOWED_SOURCE_ROOTS = old_allowed
            site.SOURCE_LINKS = old_links
            site.source_link_aliases.cache_clear()
    print("ok test_generic_source_stems_do_not_link_in_prose")


def test_freshness_reports_rebuilt_articles_without_stale_warning():
    out = site.freshness({
        "synced": "2026-06-27 02:30",
        "stale_articles": [],
        "changed_articles": ["mempalace", "solo-orchestrator"],
    })
    assert 'class="fresh ok"' in out, out
    assert "0 stale" in out, out
    assert "2 rebuilt" in out, out
    print("ok test_freshness_reports_rebuilt_articles_without_stale_warning")


def test_freshness_stale_branch_describes_failed_rebuild():
    old_meta = site.META
    try:
        site.META = {
            "mempalace": {"title": "MemPalace"},
            "solo-orchestrator": {"title": "Solo Orchestrator"},
        }
        out = site.freshness({
            "synced": "2026-06-27 02:30",
            "stale_articles": ["mempalace", "solo-orchestrator"],
            "changed_articles": ["mempalace", "solo-orchestrator"],
        })
        assert "rebuild failed" in out, out
        assert "compile/refresh.py" in out, out
        assert "manual re-compile" not in out, out
        assert "source changes for 2 articles" in out, out
    finally:
        site.META = old_meta
    print("ok test_freshness_stale_branch_describes_failed_rebuild")


def test_later_sources_win_for_duplicate_document_aliases():
    old_ref = "raw/inbox/old/TAI-RES-2026-004-v1.0.0-MemPalace.md"
    new_ref = "raw/inbox/new/TAI-RES-2026-004-v1.1.0-MemPalace.md"

    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        (root / old_ref).parent.mkdir(parents=True, exist_ok=True)
        (root / new_ref).parent.mkdir(parents=True, exist_ok=True)
        (root / old_ref).write_text("---\ndocument_id: TAI-RES-2026-004\nversion: 1.0.0\n---\n# Old\n")
        (root / new_ref).write_text("---\ndocument_id: TAI-RES-2026-004\nversion: 1.1.0\n---\n# New\n")
        old_root = site.ROOT
        old_allowed = site.ALLOWED_SOURCE_ROOTS
        old_links = site.SOURCE_LINKS
        try:
            site.ROOT = root
            site.ALLOWED_SOURCE_ROOTS = [root]
            site.SOURCE_LINKS = {
                old_ref: "source/old.html",
                new_ref: "source/new.html",
            }
            site.source_link_aliases.cache_clear()
            out = site.link_source_alias_refs("<p>TAI-RES-2026-004 is current.</p>", [old_ref, new_ref])
            assert 'href="source/new.html"' in out, out
            assert 'href="source/old.html"' not in out, out
        finally:
            site.ROOT = old_root
            site.ALLOWED_SOURCE_ROOTS = old_allowed
            site.SOURCE_LINKS = old_links
            site.source_link_aliases.cache_clear()
    print("ok test_later_sources_win_for_duplicate_document_aliases")


def test_first_upload_keeps_legacy_documents_and_web_sources_visible():
    old_ref = "raw/inbox/old/cognite-overview.md"
    new_ref = "raw/inbox/new/cognite-email.txt"
    web_ref = "https://docs.example.test/cdf"
    before = "sources:\n  - %s\n  - %s\n" % (web_ref, old_ref)
    # The older document predates raw_documents. The new upload is registered
    # in both fields, as browser ingestion does; it must count only once.
    after = before + "  - %s\nraw_documents:\n  - %s\n" % (new_ref, new_ref)
    with tempfile.TemporaryDirectory() as directory:
        root = pathlib.Path(directory)
        for ref, text in [(old_ref, "# Earlier overview\n"), (new_ref, "Additional evidence\n")]:
            path = root / ref
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        with mock.patch.multiple(site, ROOT=root, ALLOWED_SOURCE_ROOTS=[root],
                                 SOURCE_LINKS={old_ref: "source/old.html", new_ref: "source/new.html"}):
            assert site.raw_doc_refs(before) == [old_ref]
            assert set(site.raw_doc_refs(after)) == {old_ref, new_ref}
            assert set(site.topic_details_refs(after)) == {old_ref, new_ref}
            panel = site.build_source_panel(after)
            assert 'id="article-sources" open' in panel
            assert "Article sources (3)" in panel
            for href in (web_ref, "source/old.html", "source/new.html"):
                assert panel.count('href="%s"' % href) == 1
            assert "source-superseded" not in panel, "Add must not imply supersession"
            # A document stored only in raw_documents still belongs in the
            # complete source list and its count.
            raw_only = before + "raw_documents:\n  - %s\n" % new_ref
            assert "Article sources (3)" in site.build_source_panel(raw_only)
            meta = {"title": "Competitor", "tier": "product", "org": "transpara",
                    "primary_placement": "competition/competitors",
                    "placements": ["competition/competitors"]}
            box = site.build_infobox(meta, raw_only)
            assert 'href="#article-sources">3 total — view all</a>' in box
            assert "Ingested documents" in box
    print("ok test_first_upload_keeps_legacy_documents_and_web_sources_visible")


def test_source_index_includes_deduplicated_web_references_with_all_spaces():
    from types import SimpleNamespace
    shared = "https://docs.example.test/cdf"
    specific = "https://docs.example.test/cdf/architecture"
    records = [
        SimpleNamespace(placements=["competition/competitors"],
                        sources=[shared, specific], raw_documents=[]),
        SimpleNamespace(placements=["platform/architecture"],
                        sources=[shared], raw_documents=[]),
    ]
    with tempfile.TemporaryDirectory() as directory:
        root = pathlib.Path(directory)
        with mock.patch.multiple(site, ROOT=root, WIKI=root / "wiki", RAW=root / "raw",
                                 SOURCE_DIST=root / "dist" / "source",
                                 SOURCE_INDEX=[], SOURCE_LINKS={}), \
                mock.patch.object(site, "load_catalog", return_value=records):
            site.build_source_pages({})
            rows = {row["href"]: row for row in site.SOURCE_INDEX}
            assert len(rows) == 2
            assert rows[shared]["spaces"] == ["competition", "platform"]
            assert rows[specific]["spaces"] == ["competition"]
            assert rows[shared]["title"] != rows[specific]["title"]
            assert not list(site.SOURCE_DIST.iterdir()), "external refs link directly; no fetched copies"
    print("ok test_source_index_includes_deduplicated_web_references_with_all_spaces")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
    print("\nall %d build-site link tests passed" % len(fns))
