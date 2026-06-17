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

    def ingest(repo, label, args):
        # Run one gh query and fold its PRs in. A failure is recorded per (repo, query)
        # and never discards rows already collected from the repo's other query.
        try:
            for pr in gh_json(args):
                it = pr_to_item(pr, repo)
                items_by_id[it["id"]] = it
        except Exception as e:  # one bad query never zeroes the whole overlay
            errors.append("%s %s: %s" % (repo, label, e))

    for repo in repos:
        slug = "transpara-ai/%s" % repo
        ingest(repo, "open", ["pr", "list", "--repo", slug, "--state", "open",
                              "--json", _FIELDS, "--limit", "100"])
        ingest(repo, "merged", ["pr", "list", "--repo", slug, "--state", "merged",
                                "--search", "merged:>=%s" % since,
                                "--json", _FIELDS, "--limit", "100"])
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
