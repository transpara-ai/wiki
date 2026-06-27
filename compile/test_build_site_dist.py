#!/usr/bin/env python3
"""Stdlib-assert tests for live dist handling in compile/build_site.py."""
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_site as site  # noqa: E402


def test_prepare_dist_preserves_live_site_until_successful_prune():
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        dist = root / "dist"
        source = dist / "source"
        source.mkdir(parents=True)
        (dist / "index.html").write_text("old index")
        (dist / "stale.html").write_text("old stale")
        (dist / "deploy-status.json").write_text("{}")
        (source / "old-source.html").write_text("old source")

        old_dist = site.DIST
        old_source_dist = site.SOURCE_DIST
        old_generated = site.GENERATED_DIST_PATHS
        try:
            site.DIST = dist
            site.SOURCE_DIST = source
            site.GENERATED_DIST_PATHS = set()

            site.prepare_dist()
            assert (dist / "index.html").read_text() == "old index"
            assert (dist / "stale.html").exists()
            assert (source / "old-source.html").exists()

            site.write_dist_text(dist / "index.html", "new index")
            site.write_dist_text(source / "new-source.html", "new source")
            site.prune_dist()

            assert (dist / "index.html").read_text() == "new index"
            assert (source / "new-source.html").read_text() == "new source"
            assert not (dist / "stale.html").exists()
            assert not (source / "old-source.html").exists()
            assert (dist / "deploy-status.json").exists()
        finally:
            site.DIST = old_dist
            site.SOURCE_DIST = old_source_dist
            site.GENERATED_DIST_PATHS = old_generated
    print("ok test_prepare_dist_preserves_live_site_until_successful_prune")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
    print("\nall %d build-site dist tests passed" % len(fns))
