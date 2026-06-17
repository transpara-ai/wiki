#!/usr/bin/env python3
"""Live in-flight layer for the Civilization Arc.

Collects open + recently-merged PRs across the dark-factory stack (+ civilization-wiki)
via the `gh` CLI and writes dist/inflight.json — the live overlay the arc page fetches.

Honors the standing rules, exactly like compile/refresh.py:
  * No git commit/push/merge. Only writes local working files (dist/inflight.json).
  * No secrets: `gh` uses the user's existing auth; the token is NEVER written to
    inflight.json or shipped to the browser. inflight.json carries only PR metadata
    (number, title, author login, url, state).
  * Fail-loud: a gh failure for a repo is recorded, never silently treated as "no work".
"""
import json
import subprocess
import pathlib
import datetime

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "dist" / "inflight.json"
MERGED_WINDOW_DAYS = 7
# Live items join the ongoing "stewardship" sprint (existing vocab → passes validateItems,
# resolves the tooltip sprint label, adds no new axis tick).
LIVE_SPRINT = "stewardship"


def pr_to_item(pr, repo):
    """Pure: one `gh pr list --json` row -> one derived arc item (no seq; browser assigns)."""
    state = (pr.get("state") or "").upper()
    status = "done" if state == "MERGED" else "active"
    author = ((pr.get("author") or {}).get("login")) or "unknown"
    number = pr.get("number")
    return {
        "id": "pr-%s-%s" % (repo, number),
        "code": "%s#%s" % (repo, number),
        "type": "work",
        "label": pr.get("title") or ("%s#%s" % (repo, number)),
        "status": status,
        "blocked": bool(pr.get("isDraft")) and status == "active",
        "provenance": "derived",
        "repo": [repo],
        "sprint": LIVE_SPRINT,
        "href": pr.get("url") or "",
        "author": author,
        "note": ("%s · @%s" % (state.lower() or "open", author)),
    }
