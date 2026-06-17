import importlib.util, pathlib, unittest

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


if __name__ == "__main__":
    unittest.main()
