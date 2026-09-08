#!/usr/bin/env python3
"""Repository routes survive missing checkouts and support real Git worktrees."""
import json
import pathlib
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock

import build_site as site


ROOT = pathlib.Path(__file__).resolve().parents[1]


def git(path, *args):
    return subprocess.run(
        ["git", "-C", str(path), "-c", "core.hooksPath=/dev/null",
         "-c", "user.name=Fixture", "-c", "user.email=fixture@example.test", *args],
        check=True, capture_output=True, text=True).stdout.strip()


class RepositoryRouteTests(unittest.TestCase):
    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.root = pathlib.Path(scratch.name)
        self.checkouts = self.root / "repos"
        self.checkouts.mkdir()
        self.registry = self.root / "routes.json"
        self.write_routes({})
        patch = mock.patch.multiple(site, REPOS_ROOT=self.checkouts,
                                    REPOSITORY_ROUTES=self.registry)
        patch.start()
        self.addCleanup(patch.stop)

    def write_routes(self, routes):
        self.registry.write_text(json.dumps({"schema_version": 1, "routes": routes}))

    def route(self, name="sample"):
        return {"name": name, "origin": "https://github.com/transpara-ai/sample",
                "group": "other"}

    def checkout(self, name="sample"):
        path = self.checkouts / name
        path.mkdir()
        git(path, "init", "-b", "main")
        git(path, "remote", "add", "origin", "https://github.com/transpara-ai/sample.git")
        (path / "README.md").write_text("# Local fixture README\n\nCurrent checkout content.\n")
        git(path, "add", "README.md")
        git(path, "commit", "-m", "fixture")
        return path

    def render_repositories(self, dist, records, profile="authoring-local"):
        with mock.patch.multiple(site, DIST=dist, SOURCE_DIST=dist / "source",
                                 REPOS=records, GENERATED_DIST_PATHS=set(),
                                 PROFILE=site.STRUCTURE.profile(profile)):
            site.prepare_dist()
            site.build_repository_pages({})
            site.prune_dist()

    def test_discovers_clones_worktrees_and_symlinks_but_rejects_invalid_roots(self):
        checkout = self.checkout()
        direct = self.checkouts / "direct-worktree"
        git(checkout, "worktree", "add", "--detach", str(direct))
        moved = self.root / "relocated-worktree"
        git(checkout, "worktree", "add", "--detach", str(moved))
        alias = self.checkouts / "linked-worktree"
        alias.symlink_to(moved, target_is_directory=True)
        (self.checkouts / "broken-link").symlink_to(self.root / "missing")
        invalid = self.checkouts / "invalid"
        invalid.mkdir()
        (invalid / ".git").write_text("gitdir: /nonexistent/wiki-route-fixture\n")
        nested = checkout / "nested"
        nested.mkdir()
        (nested / ".git").mkdir()
        self.assertFalse(site.is_repo_checkout(nested))
        foreign = self.checkout("foreign")
        git(foreign, "remote", "set-url", "origin", "https://github.com/example/sample.git")
        bare = self.checkouts / "bare"
        bare.mkdir()
        git(bare, "init", "--bare")

        records = {r["slug"]: r for r in site.repo_records()}
        self.assertEqual(set(records), {"sample", "direct-worktree", "linked-worktree"})
        for record in records.values():
            self.assertTrue(record["available"])
            self.assertIn("Current checkout content.", record["readme"])
            self.assertEqual(record["head"], git(checkout, "rev-parse", "HEAD"))
        self.assertEqual(records["linked-worktree"]["path"], alias)

    def test_missing_checkout_root_retains_source_references_without_live_metadata(self):
        self.write_routes({"old-checkout": self.route("old-checkout")})
        self.checkouts.rmdir()
        with mock.patch.object(site, "run_git", side_effect=AssertionError("unexpected Git call")):
            record, = site.repo_records()
        self.assertFalse(record["available"])
        self.assertIsNone(record["path"])
        rendered = site.repo_page(record, {})
        self.assertIn('data-checkout-state="unavailable"', rendered)
        self.assertIn('href="https://github.com/transpara-ai/sample"', rendered)
        for misleading in ("<th>Branches</th>", "<th>Commits</th>", "<th>Local path</th>",
                           "local git truth", "No README was found in this local checkout"):
            self.assertNotIn(misleading, rendered)

    def test_removal_fresh_build_and_return_keep_the_same_route(self):
        self.write_routes({"sample": self.route()})
        checkout = self.checkout()
        dist = self.root / "dist"
        self.render_repositories(dist, site.repo_records())
        page = dist / "repo-sample.html"
        self.assertIn("Local fixture README", page.read_text())

        shutil.rmtree(checkout)
        self.render_repositories(dist, site.repo_records())
        unavailable = page.read_bytes()
        self.assertIn(b'data-checkout-state="unavailable"', unavailable)
        self.assertNotIn(b"Current checkout content.", unavailable)
        fresh = self.root / "dist-fresh"
        self.render_repositories(fresh, site.repo_records())
        self.assertEqual((fresh / page.name).read_bytes(), unavailable)
        self.assertEqual((fresh / "repos.html").read_bytes(), (dist / "repos.html").read_bytes())

        self.checkout()
        records = site.repo_records()
        self.assertEqual(len(records), 1)
        self.render_repositories(dist, records)
        self.assertIn("Local fixture README", page.read_text())
        self.assertNotIn('data-checkout-state="unavailable"', page.read_text())

    def test_restricted_profile_prunes_both_live_and_retained_repository_pages(self):
        self.write_routes({"old-checkout": self.route("old-checkout")})
        self.checkout()
        records = site.repo_records()
        dist = self.root / "dist"
        self.render_repositories(dist, records)
        self.assertTrue((dist / "repo-sample.html").exists())
        self.assertTrue((dist / "repo-old-checkout.html").exists())
        self.render_repositories(dist, records, "company-internal")
        self.assertFalse(list(dist.glob("repo-*.html")))
        self.assertFalse((dist / "repos.html").exists())

    def test_catalog_preserves_every_published_baseline_repository_route(self):
        with mock.patch.object(site, "REPOSITORY_ROUTES", ROOT / "compile/repository_routes.json"):
            routes = site.load_repository_routes()
        baseline = ROOT / "docs/superpowers/plans/2026-09-05-multi-space-wiki-baseline-routes.txt"
        expected = {line for line in baseline.read_text().splitlines() if line.startswith("repo-")}
        self.assertTrue(expected)
        self.assertLessEqual(expected, {"repo-%s.html" % slug for slug in routes})
        self.assertEqual(routes["github-tlc46-distribution-020"]["origin"],
                         "https://github.com/transpara-ai/.github")

    def test_invalid_route_catalogs_fail_before_writing_pages(self):
        invalid = [
            {"../escape": self.route()},
            {"sample": {**self.route(), "origin": "https://example.test/sample"}},
            {"sample": {**self.route(), "origin": "https://github.com/other/sample"}},
            {"sample": {**self.route(), "group": "unknown"}},
            {"sample": {**self.route(), "name": ""}},
            {"sample": None},
        ]
        for routes in invalid:
            with self.subTest(routes=routes):
                self.write_routes(routes)
                with self.assertRaises(ValueError):
                    site.repo_records()
        dist = self.root / "dist"
        dist.mkdir()
        (dist / "index.html").write_text("previous complete build")
        with mock.patch.multiple(site, DIST=dist, SOURCE_DIST=dist / "source"):
            with self.assertRaises(ValueError):
                site.build()
        self.assertEqual((dist / "index.html").read_text(), "previous complete build")


if __name__ == "__main__":
    unittest.main()
