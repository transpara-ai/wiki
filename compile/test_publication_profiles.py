#!/usr/bin/env python3
"""Fail-closed publication-profile acceptance tests."""
import json
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from article_catalog import load_catalog  # noqa: E402
from knowledge_structure import STRUCTURE  # noqa: E402


ROOT = pathlib.Path(__file__).resolve().parents[1]
BUILDER = ROOT / "compile" / "build_site.py"
COMPANY_DIST = ROOT / "dist-company"


def run(*args):
    return subprocess.run(
        [sys.executable, str(BUILDER), *args], cwd=ROOT,
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def search_rows(output):
    raw = (output / "search-index.js").read_text()
    prefix = "window.CIVWIKI_SEARCH_INDEX="
    return json.loads(raw[len(prefix):-2])


def test_company_profile_is_an_isolated_allowlist_projection():
    proc = run("--profile", "company-internal", "--output", "dist-company")
    assert proc.returncode == 0, proc.stderr
    assert (COMPANY_DIST / "index.html").exists()
    for forbidden in ("sources.html", "ingest.html", "repos.html",
                      "civilization-arc.html", "civilization_arc.html"):
        assert not (COMPANY_DIST / forbidden).exists(), forbidden
    assert not (COMPANY_DIST / "source").exists()
    assert not list(COMPANY_DIST.glob("repo-*.html"))

    allowed_classes = set(
        STRUCTURE.profile("company-internal").classifications)
    catalog = load_catalog(ROOT).by_slug
    rows = search_rows(COMPANY_DIST)
    article_rows = [row for row in rows if row.get("slug") in catalog]
    for row in article_rows:
        record = catalog[row["slug"]]
        assert record.classification in allowed_classes
        assert set(row["spaces"]).issubset(
            STRUCTURE.profile("company-internal").spaces)
        assert (COMPANY_DIST / (record.slug + ".html")).exists()
    emitted_articles = {path.stem for path in COMPANY_DIST.glob("*.html")
                        if path.stem not in {"index"}}
    assert emitted_articles == {row["slug"] for row in article_rows}

    combined = "\n".join(
        path.read_text(errors="replace")
        for path in COMPANY_DIST.rglob("*") if path.is_file())
    for forbidden_text in ("/Transpara/", "raw/inbox/", "Wiki Source Ingest",
                           "Repository index"):
        assert forbidden_text not in combined, forbidden_text
    # Unclassified authoring-home prose is not copied into restricted output.
    assert "Visual KPI is one product" not in (
        COMPANY_DIST / "platform" / "index.html").read_text()
    print("ok test_company_profile_is_an_isolated_allowlist_projection")


def test_disabled_public_profile_fails_before_output():
    output = ROOT / "dist-public-disabled"
    proc = run("--profile", "public-platform", "--output",
               output.name)
    assert proc.returncode != 0
    assert "disabled" in proc.stderr
    assert not output.exists(), "disabled profile must not create output"
    print("ok test_disabled_public_profile_fails_before_output")


def test_unknown_profile_and_unsafe_output_fail_closed():
    unknown = run("--profile", "definitely-not-a-profile",
                  "--output", "dist-unknown")
    assert unknown.returncode != 0 and "unknown publication profile" in unknown.stderr
    unsafe = run("--profile", "company-internal", "--output", ".")
    assert unsafe.returncode != 0
    assert "publication output must be a dist* directory" in unsafe.stderr
    print("ok test_unknown_profile_and_unsafe_output_fail_closed")


if __name__ == "__main__":
    tests = [value for name, value in sorted(globals().items())
             if name.startswith("test_") and callable(value)]
    for test in tests:
        test()
    print("\nall %d publication-profile tests passed" % len(tests))
