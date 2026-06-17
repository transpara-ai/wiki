#!/usr/bin/env python3
"""Pure transforms for the future Civilization Arc in-flight layer.

This module intentionally contains no gh/network/file-writing collector yet.
Collector and browser-merge wiring will land separately; for now, keep the
row-to-item mapping deterministic and unit-tested.
"""

import datetime
import json
import pathlib
import subprocess

# Live items join the ongoing "stewardship" sprint so future browser overlay
# code can resolve the tooltip sprint label without adding a new axis tick.
LIVE_SPRINT = "stewardship"
MERGED_WINDOW_DAYS = 30
OUT = pathlib.Path(__file__).resolve().parent.parent / "dist" / "inflight.json"
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


def gh_json(args):
    """Run `gh ... --json ...` and parse stdout. Raises on non-zero exit (fail-loud)."""
    p = subprocess.run(["gh"] + args, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("gh %s failed: %s" % (" ".join(args), (p.stderr or "").strip()))
    return json.loads(p.stdout or "[]")


def resolve_repos():
    """Live dark-factory set (+ civilization-wiki), resolved from the GitHub topic — never hardcoded."""
    rows = gh_json(["repo", "list", "transpara-ai", "--no-archived", "--limit", "200",
                    "--json", "name,repositoryTopics"])
    repos = set()
    for r in rows:
        topics = [t.get("name") for t in (r.get("repositoryTopics") or [])]
        if "dark-factory" in topics:
            repos.add(r["name"])
    repos.add("civilization-wiki")
    return sorted(repos)


_FIELDS = "number,title,author,url,state,isDraft"


def collect_items(repos):
    items_by_id, errors = {}, []
    since = (datetime.date.today() - datetime.timedelta(days=MERGED_WINDOW_DAYS)).isoformat()
    for repo in repos:
        slug = "transpara-ai/%s" % repo
        try:
            rows = gh_json(["pr", "list", "--repo", slug, "--state", "open",
                            "--json", _FIELDS, "--limit", "100"])
            rows += gh_json(["pr", "list", "--repo", slug, "--state", "merged",
                             "--search", "merged:>=%s" % since,
                             "--json", _FIELDS, "--limit", "100"])
        except Exception as e:  # one bad repo never zeroes the whole overlay
            errors.append("%s: %s" % (repo, e))
            continue
        for pr in rows:
            it = pr_to_item(pr, repo)
            items_by_id[it["id"]] = it
    return list(items_by_id.values()), errors


def main():
    try:
        repos = resolve_repos()
        repo_err = []
    except Exception as e:
        repos, repo_err = ["civilization-wiki"], ["resolve_repos: %s" % e]
    items, errors = collect_items(repos)
    errors = repo_err + errors
    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "window_days": MERGED_WINDOW_DAYS,
        "repos": repos,
        "errors": errors,
        "items": items,
    }
    OUT.write_text(json.dumps(payload, indent=2))
    print("inflight: %d live items across %d repos, %d errors -> %s"
          % (len(items), len(repos), len(errors), OUT))


if __name__ == "__main__":
    main()
