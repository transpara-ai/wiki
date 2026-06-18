#!/usr/bin/env python3
"""Self-building auto-deploy poller for the Civilization Wiki.

Self-hosting: rebuilds only via the civilization's own refresh.py/build_site.py,
local git state, Python stdlib, air-gap. Fail-closed: deploy is the single
explicitly-proven branch; every unknown/missing/error path refuses. The script
NEVER commits, pushes, non-ff-merges, or forces — only `git fetch` and
`git merge --ff-only`. See docs/superpowers/specs/2026-06-15-wiki-autodeploy-design.md.
"""
import json
import sys
import subprocess
import pathlib
import datetime
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]

ALLOW_EXACT = {
    "index.md", "PROVENANCE.md",
    "compile/build_site.py", "compile/refresh.py",
    "compile/stats.py", "compile/inflight.py",
}
ALLOW_ASSET_PREFIX = "compile/assets/"


def sh(*a):
    return subprocess.run(list(a), capture_output=True, text=True)


def site_affecting(paths):
    """Pure. True if any path is site-affecting (allowlist), with the hits."""
    hits = []
    for p in paths:
        if p in ALLOW_EXACT:
            hits.append(p)
        elif p.startswith(ALLOW_ASSET_PREFIX):
            hits.append(p)
        elif p.startswith("wiki/") and p.endswith(".md"):
            hits.append(p)
    return (len(hits) > 0, hits)


SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_REQUIRED = ("authorized_sha", "authority", "authorized_at", "expires_at", "reason")


def _parse_iso(s):
    dt = datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt


def _iso(dt):
    return dt.astimezone(datetime.timezone.utc).isoformat()


def authorized(root, now, ancestor_check):
    """Deny-closed. Grant ONLY on the single fully-proven branch; return the sha."""
    path = root / "compile" / "deploy-authorization.json"
    if not path.exists():
        return (False, "no deploy-authorization.json", None)
    try:
        a = json.loads(path.read_text())
    except Exception as e:
        return (False, "authorization unreadable: %s" % type(e).__name__, None)
    if not isinstance(a, dict) or a.get("df") != "deploy-authorization":
        return (False, "not a deploy-authorization artifact", None)
    for k in _REQUIRED:
        if not isinstance(a.get(k), str) or not a.get(k):
            return (False, "missing/blank field: %s" % k, None)
    sha = a["authorized_sha"]
    if not SHA_RE.match(sha):
        return (False, "authorized_sha not a 40-char hex sha", None)
    try:
        start, end = _parse_iso(a["authorized_at"]), _parse_iso(a["expires_at"])
    except Exception:
        return (False, "authorized_at/expires_at not ISO-8601", None)
    if not (start <= now < end):
        return (False, "outside validity window", None)
    if not ancestor_check(sha):
        return (False, "authorized_sha not an ancestor of origin/main", None)
    return (True, "authorized by %s" % a["authority"], sha)


def preflight(root, target_sha, ancestor_check):
    """Fail-closed technical gates 1-2: clean checkout + on-main + legit target."""
    s = sh("git", "-C", str(root), "status", "--porcelain", "--untracked-files=no")
    if s.returncode != 0:
        return (False, "git status failed")
    if s.stdout.strip():
        return (False, "dirty serving checkout (tracked modifications)")
    b = sh("git", "-C", str(root), "rev-parse", "--abbrev-ref", "HEAD")
    if b.returncode != 0 or b.stdout.strip() != "main":
        return (False, "HEAD not on main")
    if not ancestor_check(target_sha):
        return (False, "target not an ancestor of origin/main")
    return (True, "preflight ok")


RECENT_N = 10
HISTORY_MAX = 200


def write_deploy_status(root, *, blocked, reason, deployed_sha, target_sha,
                        authorized_flag, now, recent, prior=None):
    if blocked:
        if prior and prior.get("blocked") and prior.get("reason") == reason and prior.get("since"):
            since = prior["since"]
        else:
            since = _iso(now)
    else:
        since = None
    status = {
        "blocked": blocked, "reason": reason, "since": since,
        "deployed_sha": deployed_sha, "target_sha": target_sha,
        "authorized": authorized_flag, "checked": _iso(now),
        "recent": recent[-RECENT_N:],
    }
    out = root / "dist" / "deploy-status.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(status, indent=2))
    return status


def append_deploy_history(root, event):
    path = root / "compile" / ".deploy-history.json"
    hist = []
    if path.exists():
        try:
            hist = json.loads(path.read_text())
        except Exception:
            hist = []
    hist.append(event)
    hist = hist[-HISTORY_MAX:]
    path.write_text(json.dumps(hist, indent=2))
    return hist[-RECENT_N:]


def deploy(root, target_sha, runner, merge=None):
    """ff-only merge to target_sha, then rebuild via runner(). No-commit, no force."""
    if merge is None:
        merge = lambda: sh("git", "-C", str(root), "merge",
                           "--ff-only", target_sha).returncode == 0
    if not merge():
        return (False, "ff-only merge failed")
    rc = runner()
    if rc != 0:
        return (False, "refresh.py exit %s" % rc)
    return (True, "deployed %s" % target_sha[:7])
