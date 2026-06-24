#!/usr/bin/env python3
"""Stdlib-assert tests for compile/refresh.py."""
import json
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import refresh  # noqa: E402
import stats  # noqa: E402


class Proc:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _wiki(root):
    (root / "wiki").mkdir(parents=True, exist_ok=True)
    (root / "wiki" / "example.md").write_text(
        "---\n"
        "entity: Example\n"
        "tier: concept\n"
        "sources:\n"
        "  - raw/example.md\n"
        "confidence:\n"
        "  sources: test\n"
        "---\n\n"
        "# Example\n"
    )
    (root / "raw").mkdir(parents=True, exist_ok=True)
    (root / "raw" / "example.md").write_text("# raw\n")
    (root / "index.md").write_text(
        "---\n"
        "article_count: 0\n"
        "---\n\n"
        + stats.BEGIN_MARKER + "\nOLD\n" + stats.END_MARKER + "\n"
    )
    (root / "compile").mkdir(parents=True, exist_ok=True)


def test_refresh_exits_nonzero_when_build_site_fails():
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        _wiki(root)
        old = {
            "ROOT": refresh.ROOT,
            "RAW": refresh.RAW,
            "WIKI": refresh.WIKI,
            "DF": refresh.DF,
            "SNAP": refresh.SNAP,
            "STATUS": refresh.STATUS,
            "sh": refresh.sh,
        }

        def fake_sh(*args):
            if args and str(args[-1]).endswith("build_site.py"):
                return Proc(7, "", "build failed")
            return Proc()

        try:
            refresh.ROOT = root
            refresh.RAW = root / "raw"
            refresh.WIKI = root / "wiki"
            refresh.DF = root / "missing-dark-factory"
            refresh.SNAP = root / "compile" / "source-snapshot.json"
            refresh.STATUS = root / "compile" / "refresh-status.json"
            refresh.sh = fake_sh
            try:
                refresh.main()
            except SystemExit as e:
                assert e.code == 7
            else:
                raise AssertionError("refresh must exit nonzero when build_site.py fails")
            assert refresh.STATUS.exists()
            assert not refresh.SNAP.exists()
        finally:
            refresh.ROOT = old["ROOT"]
            refresh.RAW = old["RAW"]
            refresh.WIKI = old["WIKI"]
            refresh.DF = old["DF"]
            refresh.SNAP = old["SNAP"]
            refresh.STATUS = old["STATUS"]
            refresh.sh = old["sh"]
    print("ok test_refresh_exits_nonzero_when_build_site_fails")


def test_refresh_success_advances_snapshot_after_build():
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        _wiki(root)
        old = {
            "ROOT": refresh.ROOT,
            "RAW": refresh.RAW,
            "WIKI": refresh.WIKI,
            "DF": refresh.DF,
            "SNAP": refresh.SNAP,
            "STATUS": refresh.STATUS,
            "sh": refresh.sh,
        }

        def fake_sh(*args):
            if args and str(args[-1]).endswith("build_site.py"):
                assert json.loads(refresh.SNAP.read_text()) == {"raw/example.md": "old-hash"}
                return Proc(0, "built", "")
            return Proc()

        try:
            refresh.ROOT = root
            refresh.RAW = root / "raw"
            refresh.WIKI = root / "wiki"
            refresh.DF = root / "missing-dark-factory"
            refresh.SNAP = root / "compile" / "source-snapshot.json"
            refresh.STATUS = root / "compile" / "refresh-status.json"
            refresh.SNAP.write_text(json.dumps({"raw/example.md": "old-hash"}))
            refresh.sh = fake_sh
            refresh.main()
            current = refresh.hash_sources()
            assert json.loads(refresh.SNAP.read_text()) == current
            status = json.loads(refresh.STATUS.read_text())
            assert status["sources_changed"] == 1
            assert status["stale_articles"] == ["example"]
        finally:
            refresh.ROOT = old["ROOT"]
            refresh.RAW = old["RAW"]
            refresh.WIKI = old["WIKI"]
            refresh.DF = old["DF"]
            refresh.SNAP = old["SNAP"]
            refresh.STATUS = old["STATUS"]
            refresh.sh = old["sh"]
    print("ok test_refresh_success_advances_snapshot_after_build")


def test_mirror_sources_skips_when_rsync_missing():
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        df = root / "docs" / "dark-factory"
        df.mkdir(parents=True)
        old_raw, old_df, old_sh = refresh.RAW, refresh.DF, refresh.sh

        def missing_rsync(*_args):
            raise FileNotFoundError("rsync")

        try:
            refresh.RAW = root / "raw"
            refresh.DF = df
            refresh.sh = missing_rsync
            refresh.mirror_sources()
            assert (root / "raw" / "transpara" / "dark-factory").exists()
        finally:
            refresh.RAW, refresh.DF, refresh.sh = old_raw, old_df, old_sh
    print("ok test_mirror_sources_skips_when_rsync_missing")


def test_mirror_sources_warns_but_continues_on_rsync_failure():
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        df = root / "docs" / "dark-factory"
        df.mkdir(parents=True)
        old_raw, old_df, old_sh = refresh.RAW, refresh.DF, refresh.sh

        def failed_rsync(*_args):
            return Proc(23, "", "rsync failed")

        try:
            refresh.RAW = root / "raw"
            refresh.DF = df
            refresh.sh = failed_rsync
            refresh.mirror_sources()
            assert (root / "raw" / "transpara" / "dark-factory").exists()
        finally:
            refresh.RAW, refresh.DF, refresh.sh = old_raw, old_df, old_sh
    print("ok test_mirror_sources_warns_but_continues_on_rsync_failure")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
    print("\nall %d refresh tests passed" % len(fns))
