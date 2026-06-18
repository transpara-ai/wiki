#!/usr/bin/env python3
"""Stdlib-assert tests for compile/inflight.py. Run: python3 compile/test_inflight.py"""
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import inflight  # noqa: E402


def test_open_pr_maps_to_active_derived_work():
    pr = {"number": 123, "title": "fix: harden gate", "author": {"login": "msaucier"},
          "url": "https://github.com/transpara-ai/hive/pull/123", "state": "OPEN", "isDraft": False}
    it = inflight.pr_to_item(pr, "hive")
    assert it["id"] == "pr-hive-123", it
    assert it["code"] == "hive#123", it
    assert it["type"] == "work", it
    assert it["status"] == "active", it
    assert it["blocked"] is False, it
    assert it["provenance"] == "derived", it
    assert it["repo"] == ["hive"], it
    assert it["sprint"] == "stewardship", it
    assert it["href"] == "https://github.com/transpara-ai/hive/pull/123", it
    assert it["author"] == "msaucier", it
    assert it["note"] == "open · @msaucier", it   # note == "<state> · @<author>"
    assert "seq" not in it, it
    print("ok test_open_pr_maps_to_active_derived_work")


def test_draft_pr_is_blocked():
    pr = {"number": 4, "title": "wip", "author": {"login": "a"},
          "url": "https://github.com/transpara-ai/site/pull/4", "state": "OPEN", "isDraft": True}
    assert inflight.pr_to_item(pr, "site")["blocked"] is True
    print("ok test_draft_pr_is_blocked")


def test_merged_pr_maps_to_done():
    pr = {"number": 9, "title": "ship it", "author": {"login": "b"},
          "url": "https://github.com/transpara-ai/docs/pull/9", "state": "MERGED", "isDraft": False}
    it = inflight.pr_to_item(pr, "docs")
    assert it["status"] == "done", it
    assert it["blocked"] is False, it
    print("ok test_merged_pr_maps_to_done")


def test_missing_author_login_falls_back_to_unknown():
    pr = {"number": 1, "title": "t", "author": None,
          "url": "https://github.com/transpara-ai/work/pull/1", "state": "OPEN", "isDraft": False}
    assert inflight.pr_to_item(pr, "work")["author"] == "unknown"
    print("ok test_missing_author_login_falls_back_to_unknown")


def test_collect_items_records_repo_errors_without_dropping_good_repos():
    def fake_gh_json(args):
        if "broken" in " ".join(args):
            raise RuntimeError("gh failed: ghp_SECRET stderr")
        return [{"number": 1, "title": "t", "author": {"login": "x"},
                 "url": "https://github.com/transpara-ai/hive/pull/1",
                 "state": "OPEN", "isDraft": False}]
    orig = inflight.gh_json
    inflight.gh_json = fake_gh_json
    try:
        items, errors = inflight.collect_items(["hive", "broken"])
    finally:
        inflight.gh_json = orig
    assert any(i["id"] == "pr-hive-1" for i in items), items
    assert any("broken" in e for e in errors), errors
    assert any("RuntimeError" in e for e in errors), errors
    assert not any("ghp_SECRET" in e or "stderr" in e for e in errors), errors
    print("ok test_collect_items_records_repo_errors_without_dropping_good_repos")


def test_open_kept_when_merged_query_fails():
    # Fail-safe: a merged-search failure must NOT discard the already-fetched open PRs.
    def fake(args):
        if "merged" in args:
            raise RuntimeError("search index unavailable")
        return [{"number": 7, "title": "open one", "author": {"login": "x"},
                 "url": "u", "state": "OPEN", "isDraft": False}]
    orig = inflight.gh_json
    inflight.gh_json = fake
    try:
        items, errors = inflight.collect_items(["hive"])
    finally:
        inflight.gh_json = orig
    assert any(i["id"] == "pr-hive-7" for i in items), items   # open PR survived
    assert any("merged" in e for e in errors), errors          # merged failure logged
    print("ok test_open_kept_when_merged_query_fails")


def test_items_dedup_by_id():
    rows = [{"number": 2, "title": "t", "author": {"login": "x"},
             "url": "u", "state": "OPEN", "isDraft": False}]
    orig = inflight.gh_json
    inflight.gh_json = lambda args: rows
    try:
        items, _ = inflight.collect_items(["hive"])
    finally:
        inflight.gh_json = orig
    ids = [i["id"] for i in items]
    assert len(ids) == len(set(ids)), ids
    print("ok test_items_dedup_by_id")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
    print("\nall %d inflight tests passed" % len(fns))
