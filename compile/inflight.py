#!/usr/bin/env python3
"""Pure transforms for the future Civilization Arc in-flight layer.

This module intentionally contains no gh/network/file-writing collector yet.
Collector and browser-merge wiring will land separately; for now, keep the
row-to-item mapping deterministic and unit-tested.
"""

# Live items join the ongoing "stewardship" sprint so future browser overlay
# code can resolve the tooltip sprint label without adding a new axis tick.
LIVE_SPRINT = "stewardship"
PR_STATE_STATUS = {
    "OPEN": "active",
    "MERGED": "done",
}


def pr_to_item(pr, repo):
    """Pure: one supported `gh pr list --json` row -> one derived arc item."""
    state = (pr.get("state") or "").upper()
    status = PR_STATE_STATUS.get(state)
    if status is None:
        return None
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
