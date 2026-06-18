#!/usr/bin/env python3
"""Live in-flight overlay generator for the Civilization Arc.

Collects open and recently merged PRs across public GitHub dark-factory topic
repos plus civilization-wiki, writes dist/inflight.json, and records omitted
private repos and repo/query-level errors in the payload.

Like compile/refresh.py, this command does not commit, push, or merge. It uses
the user's ambient gh auth and never writes tokens to inflight.json.
"""

import datetime
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "dist" / "inflight.json"

# Live items join the ongoing "stewardship" sprint so browser overlay code can
# resolve the tooltip sprint label without adding a new axis tick.
LIVE_SPRINT = "stewardship"
MERGED_WINDOW_DAYS = 30
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
    """Run `gh ... --json ...` and parse stdout. Raises on non-zero exit."""
    p = subprocess.run(["gh"] + args, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("gh %s failed: %s" % (" ".join(args), (p.stderr or "").strip()))
    return json.loads(p.stdout or "[]")


def error_summary(label, exc):
    return "%s: %s" % (label, exc.__class__.__name__)


def resolve_repo_access():
    """Live dark-factory set (+ civilization-wiki), resolved from GitHub topics and visibility."""
    rows = gh_json(["repo", "list", "transpara-ai", "--no-archived", "--limit", "200",
                    "--json", "name,repositoryTopics,isPrivate"])
    repo_access = {}
    for r in rows:
        name = r.get("name")
        if not name:
            continue
        is_public = r.get("isPrivate") is False
        topics = [t.get("name") for t in (r.get("repositoryTopics") or [])]
        if "dark-factory" in topics:
            repo_access[name] = is_public
        if name == "civilization-wiki":
            repo_access[name] = is_public
    if "civilization-wiki" not in repo_access:
        repo_access["civilization-wiki"] = False
    return repo_access


def resolve_repos():
    """Public live dark-factory set (+ civilization-wiki), resolved from GitHub topics."""
    return public_repos(resolve_repo_access())


def public_repos(repo_access):
    return sorted(repo for repo, is_public in repo_access.items() if is_public)


_FIELDS = "number,title,author,url,state,isDraft"


def collect_items(repos):
    items_by_id, errors = {}, []
    since = (datetime.date.today() - datetime.timedelta(days=MERGED_WINDOW_DAYS)).isoformat()

    def ingest(repo, label, args):
        # Run one gh query and fold its PRs in. A failure is recorded per query
        # and never discards rows already collected from the repo's other query.
        try:
            for pr in gh_json(args):
                item = pr_to_item(pr, repo)
                if item is not None:
                    items_by_id[item["id"]] = item
        except Exception as e:
            errors.append(error_summary("%s %s" % (repo, label), e))

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
        repo_access = resolve_repo_access()
        repo_err = []
    except Exception as e:
        repo_access, repo_err = {"civilization-wiki": False}, [error_summary("resolve_repo_access", e)]
    repos = public_repos(repo_access)
    items, errors = collect_items(repos)
    errors = repo_err + errors
    omitted_private_repo_count = len(repo_access) - len(repos)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "window_days": MERGED_WINDOW_DAYS,
        "repos": repos,
        "omitted_private_repo_count": omitted_private_repo_count,
        "errors": errors,
        "items": items,
    }
    OUT.write_text(json.dumps(payload, indent=2))
    print("inflight: %d live items across %d repos, %d errors -> %s"
          % (len(items), len(repos), len(errors), OUT))


if __name__ == "__main__":
    main()
