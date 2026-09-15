#!/usr/bin/env python3
"""Stdlib-assert tests for live dist handling in compile/build_site.py."""
import json
import pathlib
import sys
import tempfile
import functools
import http.server
import threading
import urllib.request
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_site as site  # noqa: E402
import site_publication as publication  # noqa: E402


def test_complete_directory_publication_under_concurrent_http_reads():
    with tempfile.TemporaryDirectory() as d:
        output = pathlib.Path(d) / "dist"
        output.mkdir()
        old, new = "old-complete" * 1000, "new-complete" * 2000
        (output / "index.html").write_text(old)
        (output / "obsolete.html").write_text("old route")
        (output / "inflight.json").write_text('{"generation":"old"}')
        class QuietHandler(http.server.SimpleHTTPRequestHandler):
            def log_message(self, *args):
                pass
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0),
            functools.partial(QuietHandler, directory=str(output)))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        url = "http://127.0.0.1:%d/index.html" % server.server_port
        seen, errors, stop = [], [], threading.Event()
        def read():
            while not stop.is_set():
                try:
                    with urllib.request.urlopen(url, timeout=3) as response:
                        seen.append(response.read().decode())
                except Exception as exc:
                    errors.append(str(exc))
        reader = threading.Thread(target=read)
        reader.start()
        try:
            with publication.staged_publication(output, ("inflight.json",)) as stage:
                (stage / "index.html").write_text("unfinished")
                with urllib.request.urlopen(url, timeout=3) as response:
                    assert response.read().decode() == old
                (stage / "index.html").write_text(new)
                (stage / "new.html").write_text("complete new route")
            with urllib.request.urlopen(url, timeout=3) as response:
                assert response.read().decode() == new
            assert not (output / "obsolete.html").exists()
            assert (output / "new.html").read_text() == "complete new route"
            assert json.loads((output / "inflight.json").read_text()) == {"generation": "old"}
        finally:
            stop.set()
            reader.join(timeout=5)
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
        assert seen and not errors, errors
        assert set(seen) <= {old, new}
        assert not list(pathlib.Path(d).glob("dist-build-*"))
    print("ok test_complete_directory_publication_under_concurrent_http_reads")


def test_failed_build_and_failed_exchange_preserve_complete_live_directory():
    with tempfile.TemporaryDirectory() as d:
        output = pathlib.Path(d) / "dist"
        output.mkdir()
        (output / "index.html").write_text("complete")
        for during_render in (True, False):
            try:
                with mock.patch.object(publication, "exchange_directories", side_effect=OSError("exchange refused")):
                    with publication.staged_publication(output) as stage:
                        (stage / "index.html").write_text("partial")
                        if during_render:
                            raise RuntimeError("renderer failed")
            except (RuntimeError, OSError):
                pass
            else:
                raise AssertionError("failure was swallowed")
            assert (output / "index.html").read_text() == "complete"
            assert not list(pathlib.Path(d).glob("dist-build-*"))
    print("ok test_failed_build_and_failed_exchange_preserve_complete_live_directory")


def test_runtime_status_update_waits_for_publication_and_is_not_lost():
    with tempfile.TemporaryDirectory() as d:
        output = pathlib.Path(d) / "dist"
        output.mkdir()
        status = output / "deploy-status.json"
        status.write_text("old")
        started, done = threading.Event(), threading.Event()
        def write():
            started.set()
            publication.write_runtime_status(status, "new")
            done.set()
        with publication.staged_publication(output, (status.name,)) as stage:
            (stage / "index.html").write_text("complete")
            writer = threading.Thread(target=write)
            writer.start()
            assert started.wait(3)
            assert not done.wait(0.05)
            assert status.read_text() == "old"
        writer.join(timeout=3)
        assert done.is_set() and status.read_text() == "new"
    print("ok test_runtime_status_update_waits_for_publication_and_is_not_lost")


def test_builder_stages_output_and_restores_paths_after_failure():
    with tempfile.TemporaryDirectory() as d:
        output = pathlib.Path(d) / "dist"
        output.mkdir()
        (output / "index.html").write_text("complete")
        def fail():
            assert site.DIST != output
            site.write_dist_text(site.DIST / "index.html", "partial")
            assert (output / "index.html").read_text() == "complete"
            raise ValueError("bad build")
        with mock.patch.object(site, "DIST", output), mock.patch.object(site, "SOURCE_DIST", output / "source"):
            with mock.patch.object(site, "_build_site", side_effect=fail):
                try:
                    site.build()
                except ValueError:
                    pass
                else:
                    raise AssertionError("bad build accepted")
            assert site.DIST == output and site.SOURCE_DIST == output / "source"
        assert (output / "index.html").read_text() == "complete"
    print("ok test_builder_stages_output_and_restores_paths_after_failure")


def test_package_version_accepts_semver_and_rejects_malformed_releases():
    with tempfile.TemporaryDirectory() as d:
        package = pathlib.Path(d) / "package.json"
        for version in ("0.1.1", "1.2.3-rc.1", "1.0.0-beta.0+build.007"):
            package.write_text(json.dumps({"version": version}))
            assert site.load_site_version(package) == version
        for version in ("v1.2.3", "01.2.3", "1.2", "1.0.0-01", "1.0.0+", 123):
            package.write_text(json.dumps({"version": version}))
            try:
                site.load_site_version(package)
            except ValueError:
                pass
            else:
                raise AssertionError("invalid SemVer accepted: %r" % version)
    print("ok test_package_version_accepts_semver_and_rejects_malformed_releases")


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
