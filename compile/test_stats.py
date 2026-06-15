#!/usr/bin/env python3
"""Stdlib-assert tests for compile/stats.py. Run: python3 compile/test_stats.py"""
import sys
import pathlib
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import stats  # noqa: E402


def _wiki(root, articles):
    """articles: dict slug -> tier string, or None for a missing tier field."""
    (root / "wiki").mkdir(parents=True, exist_ok=True)
    for slug, tier in articles.items():
        fm = "---\nentity: %s\n" % slug
        if tier is not None:
            fm += "tier: %s\n" % tier
        fm += "---\n\n# %s\n\nbody\n" % slug
        (root / "wiki" / ("%s.md" % slug)).write_text(fm)


def test_fixture_counts():
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        _wiki(root, {"a": "foundational", "b": "foundational", "c": "arc", "m": "meta"})
        out = stats.compute_counts(root)
        assert out["article_count"] == 4, out
        assert out["tier_counts"] == [("foundational", 2), ("arc", 1), ("meta", 1)], out
    print("ok test_fixture_counts")


def test_unknown_and_missing_tier_visible():
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        _wiki(root, {"a": "foundational", "x": "bogus", "n": None})
        out = stats.compute_counts(root)
        tiers = dict(out["tier_counts"])
        assert tiers.get("bogus") == 1, out
        assert tiers.get(stats.NO_TIER) == 1, out
        assert out["tier_counts"][0] == ("foundational", 1), out  # canonical first
    print("ok test_unknown_and_missing_tier_visible")


def test_zero_count_guard():
    try:
        stats.ensure_nonzero({"article_count": 0, "tier_counts": []})
    except ValueError:
        print("ok test_zero_count_guard")
        return
    raise AssertionError("ensure_nonzero must raise on article_count 0")


def test_idempotent_write():
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        _wiki(root, {"a": "foundational", "c": "arc"})
        idx = root / "index.md"
        idx.write_text(
            "---\narticle_count: 0\nlast_compiled: \"2026-06-14\"\n---\n\n"
            "| **run** | **Run-3** |\n\n"
            + stats.BEGIN_MARKER + "\nOLD\n" + stats.END_MARKER + "\n")
        counts = stats.compute_counts(root)
        assert stats.write_index_block(idx, counts) is True    # first write changes
        first = idx.read_text()
        assert stats.write_index_block(idx, counts) is False   # second is a no-op
        assert idx.read_text() == first                        # byte-identical
        assert "2 — 1 foundational · 1 arc" in first.replace("**", "")
        assert "article_count: 2" in first                     # frontmatter updated
    print("ok test_idempotent_write")


def test_honesty_human_rows_untouched():
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        _wiki(root, {"a": "arc"})
        idx = root / "index.md"
        human = ("---\narticle_count: 99\nlast_compiled: \"2026-06-14\"\n---\n\n"
                 "| **last_compiled** | **2026-06-14** |\n"
                 "| **run** | **Run-3 (x)** |\n"
                 "| **completeness** | **PARTIAL — y** |\n\n")
        idx.write_text(human + stats.BEGIN_MARKER + "\nOLD\n" + stats.END_MARKER + "\n")
        stats.write_index_block(idx, stats.compute_counts(root))
        out = idx.read_text()
        assert "| **last_compiled** | **2026-06-14** |" in out
        assert "| **run** | **Run-3 (x)** |" in out
        assert "| **completeness** | **PARTIAL — y** |" in out
    print("ok test_honesty_human_rows_untouched")


def test_marker_fail_loud():
    counts = {"article_count": 1, "tier_counts": [("arc", 1)]}
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        idx = root / "index.md"
        cases = [
            "no markers here",
            stats.BEGIN_MARKER + "\nx\n",                                  # missing end
            "\nx\n" + stats.END_MARKER,                                    # missing begin
            (stats.BEGIN_MARKER + "\nx\n" + stats.END_MARKER + "\n"
             + stats.BEGIN_MARKER + "\ny\n" + stats.END_MARKER),          # duplicated
            stats.END_MARKER + "\nx\n" + stats.BEGIN_MARKER,              # reversed
        ]
        for bad in cases:
            idx.write_text(bad)
            try:
                stats.write_index_block(idx, counts)
            except ValueError:
                continue
            raise AssertionError("expected ValueError for: %r" % bad[:40])
    print("ok test_marker_fail_loud")


def test_frontmatter_scope_ignores_body_article_count():
    # A body line that also matches `article_count: <n>` (e.g. a frontmatter
    # example shown in a future article) must NOT be rewritten and must NOT
    # trigger a false duplicate-raise that blocks the refresh. Only the YAML
    # header is in scope.
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        _wiki(root, {"a": "arc", "b": "concept"})
        idx = root / "index.md"
        idx.write_text(
            "---\narticle_count: 0\n---\n\n"
            "Example frontmatter shown in the meta article:\n\n"
            "article_count: 999\n\n"
            + stats.BEGIN_MARKER + "\nOLD\n" + stats.END_MARKER + "\n")
        stats.write_index_block(idx, stats.compute_counts(root))
        out = idx.read_text()
        assert "article_count: 2" in out          # frontmatter updated to the real count
        assert "article_count: 999" in out         # body line left untouched
        assert out.count("article_count:") == 2    # no duplicate-collapse, no raise
    print("ok test_frontmatter_scope_ignores_body_article_count")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
    print("\nall %d stats tests passed" % len(fns))
