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
