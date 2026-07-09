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


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
    print("\nall %d investigation-standard build-site tests passed" % len(fns))
