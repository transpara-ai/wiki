#!/usr/bin/env python3
"""Stdlib-assert tests for source-link rendering in compile/build_site.py."""
import pathlib
import sys
import tempfile

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
            fn()
        finally:
            site.ROOT = old_root
            site.ALLOWED_SOURCE_ROOTS = old_allowed
            site.SOURCE_LINKS = old_links


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
            out = site.link_source_alias_refs("<p>TAI-RES-2026-004 is current.</p>", [old_ref, new_ref])
            assert 'href="source/new.html"' in out, out
            assert 'href="source/old.html"' not in out, out
        finally:
            site.ROOT = old_root
            site.ALLOWED_SOURCE_ROOTS = old_allowed
            site.SOURCE_LINKS = old_links
    print("ok test_later_sources_win_for_duplicate_document_aliases")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
    print("\nall %d build-site link tests passed" % len(fns))
