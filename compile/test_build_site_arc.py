#!/usr/bin/env python3
"""Stdlib-assert tests for the arc page wiring (Item 2b-visual).

Guards the engine retirement: the arc page must carry the view module and
the static one-status legend, and none of the retired chronological-tracks
assets (civilizationArcNav.js / civilizationArcLayout.js /
civilizationArcDraw.js) may regrow in the source tree, the built dist, or
the package.json script lists. Design packet AC3/AC4:
docs/superpowers/specs/2026-07-03-arc-2b-visual-packet.md.

Runs after `npm run build` (both CI and `npm run verify` order the build
first), so dist/ assertions see a fresh build.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
ASSETS = ROOT / "compile" / "assets"
DIST = ROOT / "dist"

RETIRED = ["civilizationArcNav.js", "civilizationArcLayout.js", "civilizationArcDraw.js"]
SURVIVING = [
    "civilizationOntology.js",
    "civilizationArcData.js",
    "civilizationProgressEvidence.js",
    "civilizationArcView.js",
]


def arc_page_html():
    page = DIST / "civilization-arc.html"
    assert page.exists(), "dist/civilization-arc.html missing — run npm run build first"
    return page.read_text()


def test_arc_page_carries_view_script_and_no_retired_scripts():
    html = arc_page_html()
    assert 'src="civilizationArcView.js?v=' in html, "view script tag missing"
    for name in RETIRED:
        assert name not in html, "retired engine script referenced: %s" % name
    assert 'data-civilization-arc ' in html or 'data-civilization-arc data-' in html, \
        "arc mount div missing"
    assert 'data-civilization-arc-nav' not in html, "retired mount attribute still emitted"
    print("ok test_arc_page_carries_view_script_and_no_retired_scripts")


def test_arc_page_emits_static_legend():
    html = arc_page_html()
    assert 'class="arc-view-legend"' in html, "static one-status legend missing"
    for status in ("done", "active", "planned", "future", "blocked"):
        assert "arc-status-dot-%s" % status in html, "legend misses status %s" % status
    assert "Every status is evidence-derived or stamped." in html, "legend evidence line missing"
    print("ok test_arc_page_emits_static_legend")


def test_retired_assets_absent_from_tree_and_dist():
    for name in RETIRED:
        assert not (ASSETS / name).exists(), "retired asset regrew in compile/assets: %s" % name
        assert not (DIST / name).exists(), "retired asset shipped in dist: %s" % name
    for name in SURVIVING:
        assert (ASSETS / name).exists(), "surviving asset missing from compile/assets: %s" % name
        assert (DIST / name).exists(), "surviving asset missing from dist: %s" % name
    print("ok test_retired_assets_absent_from_tree_and_dist")


def test_package_scripts_reference_no_retired_assets():
    scripts = json.loads((ROOT / "package.json").read_text())["scripts"]
    blob = " ".join(scripts.values())
    for name in RETIRED:
        assert name not in blob, "package.json script references retired asset: %s" % name
    assert "civilizationArcView.js" in blob, "test:js must check the view module"
    assert "tests/arcView.test.js" in blob, "test:unit must run the view unit tests"
    print("ok test_package_scripts_reference_no_retired_assets")


def test_css_custom_properties_all_defined():
    """Fail-closed guard for the CFAR 2b-visual-r1 class: a var(--x) whose
    property is defined nowhere is silently invalid at computed-value time —
    the browser drops the declaration and the page quietly de-styles. Every
    custom property referenced without a fallback must be defined somewhere
    in the sheet (scoping is not checked; existence is the regression net)."""
    import re
    css = (ASSETS / "style.css").read_text()
    defined = set(re.findall(r'(--[A-Za-z0-9_-]+)\s*:', css))
    referenced = set(re.findall(r'var\(\s*(--[A-Za-z0-9_-]+)\s*\)', css))  # no-fallback uses only
    missing = sorted(referenced - defined)
    assert not missing, "custom properties referenced but never defined: %s" % ", ".join(missing)
    print("ok test_css_custom_properties_all_defined")


def test_both_arc_routes_ship_the_same_view():
    canonical = (DIST / "civilization-arc.html").read_text()
    alias = (DIST / "civilization_arc.html").read_text()
    assert canonical == alias, "arc route alias diverged from the canonical page"
    print("ok test_both_arc_routes_ship_the_same_view")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
    print("\nall %d build-site arc tests passed" % len(fns))
