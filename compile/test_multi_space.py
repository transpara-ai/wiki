#!/usr/bin/env python3
"""Generated-site acceptance tests for the multi-space Knowledge Hub."""
import json
from html.parser import HTMLParser
import pathlib
import sys
import urllib.parse

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from article_catalog import load_catalog  # noqa: E402
import build_site  # noqa: E402


ROOT = pathlib.Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
BASELINE_ROUTES = (
    ROOT / "docs" / "superpowers" / "plans" /
    "2026-09-05-multi-space-wiki-baseline-routes.txt"
)


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.values = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if value and key.lower() in {"href", "src", "xlink:href"}:
                self.values.append(value)


def read(route):
    return (DIST / route).read_text()


def search_rows():
    raw = read("search-index.js")
    prefix = "window.CIVWIKI_SEARCH_INDEX="
    assert raw.startswith(prefix) and raw.endswith(";\n")
    return json.loads(raw[len(prefix):-2])


def test_portal_and_space_routes_exist():
    routes = ["index.html", "civilization/index.html", "platform/index.html",
              "competition/index.html", "devops/index.html"]
    for route in routes:
        assert (DIST / route).is_file(), route
    portal = read("index.html")
    assert "One canonical graph. Several purposeful views." in portal
    assert "board-hero" not in portal
    for route, label in [("civilization/index.html", "Civilization"),
                         ("platform/index.html", "Transpara Platform"),
                         ("competition/index.html", "Competition"),
                         ("devops/index.html", "DevOps")]:
        assert 'href="%s"' % route in portal
        assert label in portal
    print("ok test_portal_and_space_routes_exist")


def test_every_baseline_route_survives():
    expected = {line.strip() for line in BASELINE_ROUTES.read_text().splitlines()
                if line.strip() and not line.startswith("#")}
    # The captured baseline includes source viewers backed by absolute paths
    # on the authoring host. A standalone clone cannot render absent host
    # files. Exempt only those explicit citations; all other routes remain
    # mandatory. shadow_verify.py checks the full baseline on the source host.
    unavailable_host_sources = {
        "source/%s.html" % build_site.source_id(ref)
        for article in load_catalog(ROOT)
        for ref in article.sources + article.raw_documents
        if ref.startswith("/Transpara/transpara-ai/")
        and not pathlib.Path(ref).is_file()
    }
    expected -= unavailable_host_sources
    current = {str(path.relative_to(DIST)) for path in DIST.rglob("*")
               if path.is_file()}
    missing = sorted(expected - current)
    assert not missing, "baseline routes missing: %s" % missing
    print("ok test_every_baseline_route_survives")


def test_all_generated_local_links_and_assets_resolve():
    failures = []
    for page in sorted(DIST.rglob("*.html")):
        rel_page = page.relative_to(DIST)
        # Source snapshots and repository README mirrors intentionally retain
        # upstream-relative references that are outside this static bundle.
        if rel_page.parts[0] == "source" or rel_page.name.startswith("repo-"):
            continue
        parser = Links()
        parser.feed(page.read_text(errors="replace"))
        route = "/" + str(rel_page)
        for value in parser.values:
            parsed = urllib.parse.urlsplit(value)
            if parsed.scheme or value.startswith(("#", "//")):
                continue
            target = urllib.parse.urljoin(route, parsed.path).lstrip("/")
            if not target or target.startswith("api/"):
                continue
            candidate = DIST / target
            if target.endswith("/"):
                candidate = candidate / "index.html"
            if not candidate.exists():
                failures.append("%s -> %s" % (rel_page, value))
    assert not failures, "unresolved generated links/assets:\n" + "\n".join(failures[:50])
    print("ok test_all_generated_local_links_and_assets_resolve")


def test_nested_homes_have_depth_aware_chrome():
    for space in ("civilization", "platform", "competition", "devops"):
        page = read("%s/index.html" % space)
        assert 'href="../style.css?' in page
        assert 'src="../search-index.js?' in page
        assert '<a class="brand" href="../index.html">' in page
        assert 'class="brand-title">Transpara Knowledge Hub</span>' in page
        assert 'fetch("../deploy-status.json"' in page
        assert 'class="current" aria-current="page" href="../%s/index.html"' % space in page
        assert 'href="../ingest.html?space=%s"' % space in page
    civilization = read("civilization/index.html")
    assert 'href="../arc-origin-narrative.html"' in civilization
    assert 'href="arc-origin-narrative.html"' not in civilization
    print("ok test_nested_homes_have_depth_aware_chrome")


def test_search_rows_are_space_scoped_and_articles_canonical():
    rows = search_rows()
    by_slug = {row["slug"]: row for row in rows}
    catalog = load_catalog(ROOT)
    for space in ("civilization", "platform", "competition", "devops"):
        row = by_slug["space-%s" % space]
        assert row["href"] == "%s/index.html" % space
        assert row["spaces"] == [space]
    for record in catalog:
        if build_site.META[record.slug].get("retired_on"):
            assert record.slug not in by_slug
            continue
        row = by_slug[record.slug]
        assert row.get("href", "%s.html" % record.slug) == "%s.html" % record.slug
        assert set(row["spaces"]) == {
            placement.split("/", 1)[0] for placement in record.placements}
        assert row["classification"] == record.classification
        assert row["org"] == record.org
        assert row["section"]
    print("ok test_search_rows_are_space_scoped_and_articles_canonical")


def test_article_location_and_space_switcher_render():
    page = read("event-graph.html")
    assert 'aria-label="Knowledge spaces"' in page
    assert "Primary location" in page
    assert 'href="civilization/index.html">Civilization / Foundations</a>' in page
    assert "Transpara-AI · an article in Civilization" in page
    print("ok test_article_location_and_space_switcher_render")


def test_generic_service_templates_remain_loopback_only_with_legacy_window():
    units = ROOT / "compile" / "systemd"
    service = (units / "transpara-knowledge-hub.service").read_text()
    refresh = (units / "transpara-knowledge-hub-refresh.service").read_text()
    timer = (units / "transpara-knowledge-hub-refresh.timer").read_text()
    assert "127.0.0.1 8787" in service
    assert "0.0.0.0" not in service
    environment = dict(line.removeprefix("Environment=").split("=", 1)
                       for line in service.splitlines()
                       if line.startswith("Environment="))
    assert environment["KNOWLEDGE_HUB_PROFILE"] == "authoring-local"
    assert environment["KNOWLEDGE_HUB_DIST"] == "dist"
    assert "transpara-ai-civilization-wiki.service" in service
    assert "transpara-ai-civilization-wiki-refresh.service" in refresh
    assert "transpara-ai-civilization-wiki-refresh.timer" in timer
    for legacy in ("transpara-ai-civilization-wiki.service",
                   "transpara-ai-civilization-wiki-refresh.service",
                   "transpara-ai-civilization-wiki-refresh.timer"):
        assert (units / legacy).is_file(), legacy
    print("ok test_generic_service_templates_remain_loopback_only_with_legacy_window")


if __name__ == "__main__":
    tests = [value for name, value in sorted(globals().items())
             if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
    print("\nall %d multi-space tests passed" % len(tests))
