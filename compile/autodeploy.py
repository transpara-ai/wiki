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


def read_deployed_sha(root):
    p = root / "compile" / ".deployed-sha"
    return p.read_text().strip() if p.exists() else None


def write_deployed_sha(root, sha):
    (root / "compile").mkdir(parents=True, exist_ok=True)
    (root / "compile" / ".deployed-sha").write_text(sha + "\n")


def current_head(root):
    """The checkout's HEAD sha (what the live dist/ was built from), or None on error."""
    r = sh("git", "-C", str(root), "rev-parse", "HEAD")
    return r.stdout.strip() if r.returncode == 0 else None


def diff_names(root, a, b):
    """Changed paths between two shas, or None if `git diff` errors (unreadable/
    ambiguous state — e.g. a corrupt or missing deployed-sha). None => caller REFUSES;
    never treat a diff failure as 'no changes'."""
    r = sh("git", "-C", str(root), "diff", "--name-only", "%s..%s" % (a, b))
    if r.returncode != 0:
        return None
    return [x for x in r.stdout.splitlines() if x.strip()]


def decide(deployed_sha, target_sha, auth_ok, auth_reason,
           changed_paths, preflight_ok, preflight_reason):
    """Pure. Gate 0 (auth) first; then noop/skip/preflight/deploy."""
    if not auth_ok:
        return ("refuse", "gate0: " + auth_reason)
    if target_sha == deployed_sha:
        return ("noop", "already at authorized sha")
    if not site_affecting(changed_paths)[0]:
        return ("skip", "no site-affecting changes")
    if not preflight_ok:
        return ("refuse", preflight_reason)
    return ("deploy", "authorized + site-affecting + preflight ok")


def _prior_status(root):
    p = root / "dist" / "deploy-status.json"
    if p.exists():
        try:
            return json.loads(p.read_text())
        except Exception:
            return None
    return None


def run_tick(root, *, now, ancestor_check, runner, fetch=None, merge=None):
    if fetch is None:
        fetch = lambda: sh("git", "-C", str(root), "fetch", "--quiet", "origin")
    prior = _prior_status(root)

    def status(blocked, reason, deployed, target, auth_flag, recent=None):
        return write_deploy_status(root, blocked=blocked, reason=reason,
                                   deployed_sha=deployed, target_sha=target,
                                   authorized_flag=auth_flag, now=now,
                                   recent=recent or (prior.get("recent", []) if prior else []),
                                   prior=prior)

    if getattr(fetch(), "returncode", 1) != 0:
        return status(True, "git fetch failed", read_deployed_sha(root), None, False)

    auth_ok, auth_reason, target = authorized(root, now, ancestor_check)
    deployed = read_deployed_sha(root)
    if not auth_ok:
        return status(True, "gate0: " + auth_reason, deployed, None, False)
    if deployed is None:                       # first run: record the CURRENT checkout HEAD
        head = current_head(root)              # what the live dist/ was actually built from
        if head is None:                       # unreadable git state -> refuse, no state written
            return status(True, "first run: cannot read HEAD", None, target, False)
        write_deployed_sha(root, head)
        return status(False, "initialized at current HEAD %s" % head[:7], head, target, True)

    changed = diff_names(root, deployed, target)
    if changed is None:                        # gate 4: diff/unreadable error -> refuse, no advance
        return status(True, "git diff failed (unreadable/ambiguous state)", deployed, target, True)
    pf_ok, pf_reason = preflight(root, target, ancestor_check)
    action, reason = decide(deployed, target, auth_ok, auth_reason, changed, pf_ok, pf_reason)

    if action == "noop":
        return status(False, "up to date", deployed, target, True)
    if action == "skip":
        write_deployed_sha(root, target)
        return status(False, "skip: " + reason, target, target, True)
    if action == "refuse":
        return status(True, reason, deployed, target, True)
    # deploy
    ok, detail = deploy(root, target, runner, merge=merge)
    if not ok:
        return status(True, "build failed: " + detail, deployed, target, True)
    write_deployed_sha(root, target)
    recent = append_deploy_history(root, {"sha": target, "at": _iso(now), "result": "deployed"})
    return status(False, detail, target, target, True, recent=recent)


def main():
    now = datetime.datetime.now(datetime.timezone.utc)
    ancestor_check = lambda s: sh("git", "-C", str(ROOT), "merge-base",
                                  "--is-ancestor", s, "origin/main").returncode == 0
    runner = lambda: sh("python3", str(ROOT / "compile" / "refresh.py")).returncode
    out = run_tick(ROOT, now=now, ancestor_check=ancestor_check, runner=runner)
    line = "%s %s -> %s" % (_iso(now), out.get("reason"), out.get("deployed_sha"))
    (ROOT / "compile" / "autodeploy.log").open("a").write(line + "\n")
    print(line)


if __name__ == "__main__":
    main()
