import contextlib, importlib.util, io, json, pathlib, tempfile, unittest

spec = importlib.util.spec_from_file_location(
    "inflight", pathlib.Path(__file__).resolve().parents[1] / "compile" / "inflight.py")
inflight = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inflight)


class PrToItem(unittest.TestCase):
    def test_open_pr_maps_to_active_derived_work(self):
        pr = {"number": 123, "title": "fix: harden gate", "author": {"login": "msaucier"},
              "url": "https://github.com/transpara-ai/hive/pull/123", "state": "OPEN", "isDraft": False}
        it = inflight.pr_to_item(pr, "hive")
        self.assertEqual(it["id"], "pr-hive-123")
        self.assertEqual(it["code"], "hive#123")
        self.assertEqual(it["type"], "work")
        self.assertEqual(it["status"], "active")
        self.assertEqual(it["blocked"], False)
        self.assertEqual(it["provenance"], "derived")
        self.assertEqual(it["repo"], ["hive"])
        self.assertEqual(it["sprint"], "stewardship")
        self.assertEqual(it["href"], "https://github.com/transpara-ai/hive/pull/123")
        self.assertEqual(it["author"], "msaucier")
        self.assertNotIn("seq", it)

    def test_draft_pr_is_blocked(self):
        pr = {"number": 4, "title": "wip", "author": {"login": "a"},
              "url": "https://github.com/transpara-ai/site/pull/4", "state": "OPEN", "isDraft": True}
        self.assertEqual(inflight.pr_to_item(pr, "site")["blocked"], True)

    def test_merged_pr_maps_to_done(self):
        pr = {"number": 9, "title": "ship it", "author": {"login": "b"},
              "url": "https://github.com/transpara-ai/docs/pull/9", "state": "MERGED", "isDraft": False}
        it = inflight.pr_to_item(pr, "docs")
        self.assertEqual(it["status"], "done")
        self.assertEqual(it["blocked"], False)

    def test_closed_unmerged_pr_is_not_projected(self):
        pr = {"number": 8, "title": "abandoned", "author": {"login": "c"},
              "url": "https://github.com/transpara-ai/docs/pull/8", "state": "CLOSED", "isDraft": False}
        self.assertIsNone(inflight.pr_to_item(pr, "docs"))

    def test_missing_author_login_falls_back_to_unknown(self):
        pr = {"number": 1, "title": "t", "author": None,
              "url": "https://github.com/transpara-ai/work/pull/1", "state": "OPEN", "isDraft": False}
        self.assertEqual(inflight.pr_to_item(pr, "work")["author"], "unknown")


class CollectAndShape(unittest.TestCase):
    def test_resolve_repos_uses_dark_factory_topic_plus_wiki(self):
        rows = [
            {"name": "agent", "repositoryTopics": [{"name": "dark-factory"}], "isPrivate": False},
            {"name": "docs", "repositoryTopics": [{"name": "dark-factory"}], "isPrivate": True},
            {"name": "site", "repositoryTopics": [{"name": "dark-factory"}], "isPrivate": False},
            {"name": "hive", "repositoryTopics": [{"name": "dark-factory"}], "isPrivate": False},
            {"name": "civilization-wiki", "repositoryTopics": [], "isPrivate": False},
            {"name": "tinstaller", "repositoryTopics": []},
        ]
        orig = inflight.gh_json
        inflight.gh_json = lambda args: rows
        try:
            repos = inflight.resolve_repos()
        finally:
            inflight.gh_json = orig
        self.assertEqual(repos, ["agent", "civilization-wiki", "hive", "site"])

    def test_public_repos_omits_private_collective_members(self):
        repo_access = {"agent": True, "civilization-wiki": True, "docs": False, "site": True}
        self.assertEqual(inflight.public_repos(repo_access), ["agent", "civilization-wiki", "site"])

    def test_civilization_wiki_visibility_is_respected_when_reported(self):
        rows = [
            {"name": "civilization-wiki", "repositoryTopics": [], "isPrivate": True},
            {"name": "hive", "repositoryTopics": [{"name": "dark-factory"}], "isPrivate": False},
        ]
        orig = inflight.gh_json
        inflight.gh_json = lambda args: rows
        try:
            repo_access = inflight.resolve_repo_access()
        finally:
            inflight.gh_json = orig
        self.assertEqual(repo_access["civilization-wiki"], False)
        self.assertEqual(inflight.public_repos(repo_access), ["hive"])

    def test_missing_visibility_fails_closed(self):
        rows = [
            {"name": "agent", "repositoryTopics": [{"name": "dark-factory"}]},
            {"name": "site", "repositoryTopics": [{"name": "dark-factory"}], "isPrivate": None},
            {"name": "hive", "repositoryTopics": [{"name": "dark-factory"}], "isPrivate": False},
        ]
        orig = inflight.gh_json
        inflight.gh_json = lambda args: rows
        try:
            repo_access = inflight.resolve_repo_access()
        finally:
            inflight.gh_json = orig
        self.assertEqual(repo_access["agent"], False)
        self.assertEqual(repo_access["site"], False)
        self.assertEqual(repo_access["hive"], True)
        self.assertEqual(repo_access["civilization-wiki"], False)
        self.assertEqual(inflight.public_repos(repo_access), ["hive"])

    def test_collect_items_records_repo_errors_without_dropping_good_repos(self):
        def fake_gh_json(args):
            if "broken" in " ".join(args):
                raise RuntimeError("secret stderr for private docs")
            return [{"number": 1, "title": "t", "author": {"login": "x"},
                     "url": "https://github.com/transpara-ai/hive/pull/1",
                     "state": "OPEN", "isDraft": False}]
        orig = inflight.gh_json
        inflight.gh_json = fake_gh_json
        try:
            items, errors = inflight.collect_items(["hive", "broken"])
        finally:
            inflight.gh_json = orig
        self.assertTrue(any(i["id"] == "pr-hive-1" for i in items))
        self.assertTrue(any("broken" in e for e in errors))
        self.assertFalse(any("secret stderr" in e for e in errors))

    def test_items_dedup_by_id(self):
        rows = [{"number": 2, "title": "t", "author": {"login": "x"},
                 "url": "u", "state": "OPEN", "isDraft": False}]
        orig = inflight.gh_json
        inflight.gh_json = lambda args: rows
        try:
            items, _ = inflight.collect_items(["hive"])
        finally:
            inflight.gh_json = orig
        ids = [i["id"] for i in items]
        self.assertEqual(len(ids), len(set(ids)))

    def test_collect_items_skips_unsupported_pr_states(self):
        rows = [{"number": 3, "title": "closed", "author": {"login": "x"},
                 "url": "u", "state": "CLOSED", "isDraft": False}]
        orig = inflight.gh_json
        inflight.gh_json = lambda args: rows
        try:
            items, errors = inflight.collect_items(["hive"])
        finally:
            inflight.gh_json = orig
        self.assertEqual(items, [])
        self.assertEqual(errors, [])

    def test_main_payload_omits_private_repo_names(self):
        orig_access = inflight.resolve_repo_access
        orig_collect = inflight.collect_items
        orig_out = inflight.OUT
        seen_repos = []
        with tempfile.TemporaryDirectory() as td:
            inflight.resolve_repo_access = lambda: {"agent": True, "docs": False, "site": True}
            inflight.collect_items = lambda repos: (seen_repos.extend(repos) or [], [])
            inflight.OUT = pathlib.Path(td) / "inflight.json"
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    inflight.main()
                payload = json.loads(inflight.OUT.read_text())
            finally:
                inflight.resolve_repo_access = orig_access
                inflight.collect_items = orig_collect
                inflight.OUT = orig_out
        self.assertEqual(seen_repos, ["agent", "site"])
        self.assertEqual(payload["repos"], ["agent", "site"])
        self.assertEqual(payload["omitted_private_repo_count"], 1)
        self.assertNotIn("docs", json.dumps(payload))

    def test_main_resolve_failure_fails_closed_for_wiki(self):
        orig_access = inflight.resolve_repo_access
        orig_collect = inflight.collect_items
        orig_out = inflight.OUT
        seen_repos = []
        with tempfile.TemporaryDirectory() as td:
            def fail_access():
                raise RuntimeError("gh failed with private stderr")
            inflight.resolve_repo_access = fail_access
            inflight.collect_items = lambda repos: (seen_repos.extend(repos) or [], [])
            inflight.OUT = pathlib.Path(td) / "inflight.json"
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    inflight.main()
                payload = json.loads(inflight.OUT.read_text())
            finally:
                inflight.resolve_repo_access = orig_access
                inflight.collect_items = orig_collect
                inflight.OUT = orig_out
        self.assertEqual(seen_repos, [])
        self.assertEqual(payload["repos"], [])
        self.assertEqual(payload["omitted_private_repo_count"], 1)
        self.assertTrue(any("resolve_repo_access: RuntimeError" == e for e in payload["errors"]))
        self.assertNotIn("private stderr", json.dumps(payload))


if __name__ == "__main__":
    unittest.main()
