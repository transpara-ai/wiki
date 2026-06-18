# Wiki Auto-Deploy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a self-hosting, authorization-gated auto-deploy poller for the Civilization Wiki that rebuilds the live site only when an explicitly-authorized merge lands — fail-closed, delivered as a PR, not activated live.

**Architecture:** A new stdlib-only `compile/autodeploy.py` (joining the `refresh.py`/`stats.py`/`inflight.py` family) runs as a systemd-timer tick: read a `df:`-style deploy-authorization artifact → validate fail-closed → if the authorized SHA differs, is site-affecting, and preflight passes, `git merge --ff-only` it and rebuild via `refresh.py` → write `dist/deploy-status.json` the site fetches client-side. Pure decision logic (`decide`) is separated from git/refresh I/O via injected seams so every gate is unit-tested over its full domain.

**Tech Stack:** Python 3 stdlib only (`json`, `subprocess`, `pathlib`, `datetime`, `re`). Tests are stdlib-assert (`python3 compile/test_autodeploy.py`), matching `test_stats.py`/`test_inflight.py`. systemd user units. No pytest/unittest, no third-party deps.

## Global Constraints

- **Stdlib only, air-gap.** No pip deps. Matches existing `compile/` modules.
- **The deploy script never commits, pushes, non-ff-merges, or forces.** Only `git fetch` (outbound) and `git merge --ff-only`.
- **Fail-closed everywhere.** Grant/deploy is the single explicitly-proven branch; every unknown/missing/error/unreadable path REFUSES. No `else`/`default` that deploys or authorizes.
- **Build boundary.** Code + tests + inert unit files + docs → PR. Do **not** install/enable the timer. Do **not** commit a real `compile/deploy-authorization.json` (only the `.example.json`).
- **Test idiom.** `test_*()` functions ending in `print("ok ...")`, bottom runner that finds `test_*` in globals and prints `all N tests passed`; run `python3 compile/test_autodeploy.py`. Use `tempfile.TemporaryDirectory()` for fixtures. Mirror `compile/test_stats.py`.
- **Branch:** `feat/wiki-autodeploy` (already created off `origin/main`). Never commit to `main`.
- **Commits:** conventional, lowercase, imperative; end with `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`.

## File Structure

| File | Responsibility |
|---|---|
| `compile/autodeploy.py` | All poller logic: pure gates (`site_affecting`, `authorized`, `preflight`, `decide`), status/history writers, `deploy`, `run_tick` orchestrator, `main` wiring. |
| `compile/test_autodeploy.py` | Stdlib-assert tests; `_git_repo()` fixture helper. |
| `compile/deploy-authorization.example.json` | Inert authorization template (invalid SHA). |
| `compile/systemd/civwiki-autodeploy.service` / `.timer` | Inert systemd user units. |
| `compile/build_site.py` | Modified: bake a client-side `deploy-status.json` fetch (banner + footer) into the page template. |
| `wiki/deployment-arc.md` | Modified: live deploy-status / recent-deploys widget. |
| `compile/REBUILD.md` | Modified: install + first-authorization runbook. |
| `.gitignore` | Modified: ignore runtime/state/secret files. |

---

### Task 1: Scaffold `autodeploy.py` + `site_affecting`

**Files:**
- Create: `compile/autodeploy.py`
- Create: `compile/test_autodeploy.py`

**Interfaces:**
- Produces: `site_affecting(paths: list[str]) -> (bool, list[str])`; module constants `ALLOW_EXACT`, `ALLOW_ASSET_PREFIX`; `sh(*a)`.

- [ ] **Step 1: Write the failing test** — append to `compile/test_autodeploy.py`:

```python
#!/usr/bin/env python3
"""Stdlib-assert tests for compile/autodeploy.py. Run: python3 compile/test_autodeploy.py"""
import sys
import json
import pathlib
import tempfile
import datetime
import subprocess

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import autodeploy as ad  # noqa: E402

UTC = datetime.timezone.utc


def test_site_affecting():
    yes, hits = ad.site_affecting(["wiki/x.md", "docs/y.md"])
    assert yes and hits == ["wiki/x.md"]
    assert ad.site_affecting(["index.md"])[0] is True
    assert ad.site_affecting(["compile/assets/style.css"])[0] is True
    assert ad.site_affecting(["compile/inflight.py"])[0] is True
    # excluded-only -> skip
    assert ad.site_affecting(["docs/a.md", ".github/ci.yml",
                              "compile/test_stats.py",
                              "compile/deploy-authorization.json"])[0] is False
    # wiki/ non-markdown does not count
    assert ad.site_affecting(["wiki/img.png"])[0] is False
    # mixed -> affecting
    assert ad.site_affecting(["docs/a.md", "wiki/b.md"])[0] is True
    print("ok test_site_affecting")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 compile/test_autodeploy.py`
Expected: FAIL — `ModuleNotFoundError: No module named 'autodeploy'`.

- [ ] **Step 3: Write minimal implementation** — create `compile/autodeploy.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 compile/test_autodeploy.py`
Expected: `ok test_site_affecting` then `all 1 tests passed`.

- [ ] **Step 5: Commit**

```bash
git add compile/autodeploy.py compile/test_autodeploy.py
git commit -m "feat(autodeploy): site_affecting path allowlist"
```

---

### Task 2: `authorized` gate + inert template + `.gitignore`

**Files:**
- Modify: `compile/autodeploy.py`
- Modify: `compile/test_autodeploy.py`
- Create: `compile/deploy-authorization.example.json`
- Modify: `.gitignore`

**Interfaces:**
- Produces: `authorized(root, now, ancestor_check) -> (ok: bool, reason: str, sha: str | None)`; helpers `_parse_iso`, `_iso`; const `SHA_RE`. `now` is tz-aware UTC; `ancestor_check` is `(sha) -> bool`.

- [ ] **Step 1: Write the failing test** — append to `compile/test_autodeploy.py`:

```python
def _auth(root, **over):
    base = {
        "df": "deploy-authorization",
        "authorized_sha": "a" * 40,
        "authority": "Michael Saucier",
        "authorized_at": "2026-06-18T00:00:00Z",
        "expires_at": "2026-12-31T00:00:00Z",
        "reason": "test",
    }
    base.update(over)
    (root / "compile").mkdir(parents=True, exist_ok=True)
    (root / "compile" / "deploy-authorization.json").write_text(json.dumps(base))


def test_authorized_full_domain():
    now = datetime.datetime(2026, 7, 1, tzinfo=UTC)
    yes = lambda s: True
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        # absent
        (root / "compile").mkdir(parents=True, exist_ok=True)
        assert ad.authorized(root, now, yes)[0] is False
        # malformed json
        (root / "compile" / "deploy-authorization.json").write_text("{not json")
        assert ad.authorized(root, now, yes)[0] is False
        # wrong df
        _auth(root, df="something-else");        assert ad.authorized(root, now, yes)[0] is False
        # missing field
        _auth(root); (root / "compile" / "deploy-authorization.json").write_text(
            json.dumps({"df": "deploy-authorization", "authorized_sha": "a" * 40}))
        assert ad.authorized(root, now, yes)[0] is False
        # malformed (non-hex) sha
        _auth(root, authorized_sha="z" * 40);    assert ad.authorized(root, now, yes)[0] is False
        # expired
        _auth(root, expires_at="2026-06-01T00:00:00Z"); assert ad.authorized(root, now, yes)[0] is False
        # not yet valid
        _auth(root, authorized_at="2026-08-01T00:00:00Z"); assert ad.authorized(root, now, yes)[0] is False
        # non-ancestor
        _auth(root); assert ad.authorized(root, now, lambda s: False)[0] is False
        # GRANT — the single proven branch; returns the sha
        _auth(root)
        ok, reason, sha = ad.authorized(root, now, yes)
        assert ok is True and sha == "a" * 40, (ok, reason, sha)
    print("ok test_authorized_full_domain")


def test_example_template_is_inert():
    """The shipped example template must NEVER authorize."""
    root = pathlib.Path(__file__).resolve().parents[1]
    ex = root / "compile" / "deploy-authorization.example.json"
    assert ex.exists()
    data = json.loads(ex.read_text())
    # invalid sha -> authorized() would refuse it even if copied verbatim
    assert not ad.SHA_RE.match(data["authorized_sha"])
    print("ok test_example_template_is_inert")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 compile/test_autodeploy.py`
Expected: FAIL — `AttributeError: module 'autodeploy' has no attribute 'authorized'`.

- [ ] **Step 3: Write minimal implementation** — add to `compile/autodeploy.py` (after `site_affecting`):

```python
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
```

- [ ] **Step 4: Create the inert template** — `compile/deploy-authorization.example.json`:

```json
{
  "df": "deploy-authorization",
  "authorized_sha": "REPLACE-WITH-40-CHAR-COMMIT-SHA-TO-DEPLOY",
  "authority": "name / role of the human authorizing this deploy",
  "authorized_at": "2026-01-01T00:00:00Z",
  "expires_at": "2026-01-08T00:00:00Z",
  "reason": "one-line note: why this exact commit is cleared to publish live"
}
```

- [ ] **Step 5: Add ignores** — append to `.gitignore`:

```
# auto-deploy: never commit the real authorization or runtime state
compile/deploy-authorization.json
compile/.deployed-sha
compile/.deploy-history.json
compile/.autodeploy.lock
compile/autodeploy.log
dist/deploy-status.json
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `python3 compile/test_autodeploy.py`
Expected: `ok test_authorized_full_domain`, `ok test_example_template_is_inert`, `all 3 tests passed`.

- [ ] **Step 7: Commit**

```bash
git add compile/autodeploy.py compile/test_autodeploy.py compile/deploy-authorization.example.json .gitignore
git commit -m "feat(autodeploy): deny-closed authorization gate + inert template"
```

---

### Task 3: `preflight` technical gates + git fixture

**Files:**
- Modify: `compile/autodeploy.py`
- Modify: `compile/test_autodeploy.py`

**Interfaces:**
- Produces: `preflight(root, target_sha, ancestor_check) -> (ok: bool, reason: str)`; test helper `_git_repo(d)`.

- [ ] **Step 1: Write the failing test** — append to `compile/test_autodeploy.py`:

```python
def _git(root, *a):
    return subprocess.run(["git", "-C", str(root)] + list(a),
                          capture_output=True, text=True)


def _git_repo(d):
    """Init a temp git repo on main with one commit; return (root, sha)."""
    root = pathlib.Path(d)
    _git(root, "init", "-q", "-b", "main")
    _git(root, "config", "user.email", "t@t")
    _git(root, "config", "user.name", "t")
    (root / "f.txt").write_text("v1\n")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "c1")
    sha = _git(root, "rev-parse", "HEAD").stdout.strip()
    return root, sha


def test_preflight_clean_ok():
    yes = lambda s: True
    with tempfile.TemporaryDirectory() as d:
        root, sha = _git_repo(d)
        assert ad.preflight(root, sha, yes)[0] is True
    print("ok test_preflight_clean_ok")


def test_preflight_dirty_refuses():
    yes = lambda s: True
    with tempfile.TemporaryDirectory() as d:
        root, sha = _git_repo(d)
        (root / "f.txt").write_text("dirty\n")   # tracked modification
        ok, reason = ad.preflight(root, sha, yes)
        assert ok is False and "dirty" in reason
    print("ok test_preflight_dirty_refuses")


def test_preflight_non_ancestor_and_off_main_refuse():
    with tempfile.TemporaryDirectory() as d:
        root, sha = _git_repo(d)
        assert ad.preflight(root, sha, lambda s: False)[0] is False   # not ancestor
        _git(root, "checkout", "-q", "-b", "side")
        assert ad.preflight(root, sha, lambda s: True)[0] is False     # off main
    print("ok test_preflight_non_ancestor_and_off_main_refuse")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 compile/test_autodeploy.py`
Expected: FAIL — `AttributeError: module 'autodeploy' has no attribute 'preflight'`.

- [ ] **Step 3: Write minimal implementation** — add to `compile/autodeploy.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 compile/test_autodeploy.py`
Expected: the three `ok test_preflight_*` lines; `all 6 tests passed`.

- [ ] **Step 5: Commit**

```bash
git add compile/autodeploy.py compile/test_autodeploy.py
git commit -m "feat(autodeploy): preflight technical gates (dirty / off-main / legitimacy)"
```

---

### Task 4: status + history writers

**Files:**
- Modify: `compile/autodeploy.py`
- Modify: `compile/test_autodeploy.py`

**Interfaces:**
- Produces: `write_deploy_status(root, *, blocked, reason, deployed_sha, target_sha, authorized_flag, now, recent, prior=None) -> dict`; `append_deploy_history(root, event) -> list`; consts `RECENT_N=10`, `HISTORY_MAX=200`.

- [ ] **Step 1: Write the failing test** — append:

```python
def test_status_since_carry_and_reset():
    now1 = datetime.datetime(2026, 7, 1, 0, 0, tzinfo=UTC)
    now2 = datetime.datetime(2026, 7, 1, 0, 2, tzinfo=UTC)
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        s1 = ad.write_deploy_status(root, blocked=True, reason="unauthorized",
                                    deployed_sha="x", target_sha="y",
                                    authorized_flag=False, now=now1, recent=[])
        assert s1["blocked"] and s1["since"] == ad._iso(now1)
        # still blocked, same reason -> since carries over
        s2 = ad.write_deploy_status(root, blocked=True, reason="unauthorized",
                                    deployed_sha="x", target_sha="y",
                                    authorized_flag=False, now=now2, recent=[], prior=s1)
        assert s2["since"] == ad._iso(now1) and s2["checked"] == ad._iso(now2)
        # cleared -> since None
        s3 = ad.write_deploy_status(root, blocked=False, reason="ok",
                                    deployed_sha="y", target_sha="y",
                                    authorized_flag=True, now=now2, recent=[], prior=s2)
        assert s3["blocked"] is False and s3["since"] is None
        # written to dist/
        assert json.loads((root / "dist" / "deploy-status.json").read_text())["blocked"] is False
    print("ok test_status_since_carry_and_reset")


def test_append_history_caps_and_returns_recent():
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        (root / "compile").mkdir()
        recent = []
        for i in range(15):
            recent = ad.append_deploy_history(root, {"sha": str(i), "at": "t", "result": "deployed"})
        assert len(recent) == ad.RECENT_N
        full = json.loads((root / "compile" / ".deploy-history.json").read_text())
        assert full[-1]["sha"] == "14" and len(full) == 15
    print("ok test_append_history_caps_and_returns_recent")
```

- [ ] **Step 2: Run to verify fail**

Run: `python3 compile/test_autodeploy.py` → FAIL (`no attribute 'write_deploy_status'`).

- [ ] **Step 3: Implement** — add to `compile/autodeploy.py`:

```python
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
```

- [ ] **Step 4: Run to verify pass** → `all 8 tests passed`.

- [ ] **Step 5: Commit**

```bash
git add compile/autodeploy.py compile/test_autodeploy.py
git commit -m "feat(autodeploy): deploy-status + history writers with since carry-over"
```

---

### Task 5: `deploy` (injected merge + runner)

**Files:**
- Modify: `compile/autodeploy.py`
- Modify: `compile/test_autodeploy.py`

**Interfaces:**
- Produces: `deploy(root, target_sha, runner, merge=None) -> (ok: bool, detail: str)`. `runner() -> int` (exit code); `merge() -> bool` (ff-merge succeeded), defaulting to a real `git merge --ff-only`.

- [ ] **Step 1: Write the failing test** — append:

```python
def test_deploy_merge_and_build_outcomes():
    root = pathlib.Path(".")
    sha = "a" * 40
    assert ad.deploy(root, sha, runner=lambda: 0, merge=lambda: True)[0] is True
    assert ad.deploy(root, sha, runner=lambda: 1, merge=lambda: True)[0] is False   # build fail
    assert ad.deploy(root, sha, runner=lambda: 0, merge=lambda: False)[0] is False  # merge fail
    print("ok test_deploy_merge_and_build_outcomes")
```

- [ ] **Step 2: Run to verify fail** → FAIL (`no attribute 'deploy'`).

- [ ] **Step 3: Implement** — add to `compile/autodeploy.py`:

```python
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
```

- [ ] **Step 4: Run to verify pass** → `all 9 tests passed`.

- [ ] **Step 5: Commit**

```bash
git add compile/autodeploy.py compile/test_autodeploy.py
git commit -m "feat(autodeploy): deploy via ff-only merge + injected build runner"
```

---

### Task 6: `decide` + `run_tick` + `main` (orchestration)

**Files:**
- Modify: `compile/autodeploy.py`
- Modify: `compile/test_autodeploy.py`

**Interfaces:**
- Produces: `decide(deployed_sha, target_sha, auth_ok, auth_reason, changed_paths, preflight_ok, preflight_reason) -> (action, reason)` with `action ∈ {"noop","skip","refuse","deploy"}`; `run_tick(root, *, now, ancestor_check, runner, fetch=None, merge=None) -> dict`; `main()`; helpers `read_deployed_sha`, `write_deployed_sha`, `diff_names`.

- [ ] **Step 1: Write the failing tests** — append:

```python
def test_decide_orderings():
    aff = ["wiki/x.md"]
    noaff = ["docs/x.md"]
    # gate0 first: unauthorized always refuses
    assert ad.decide("x", "y", False, "no auth", aff, True, "")[0] == "refuse"
    # already at target
    assert ad.decide("y", "y", True, "", aff, True, "")[0] == "noop"
    # nothing site-affecting
    assert ad.decide("x", "y", True, "", noaff, True, "")[0] == "skip"
    # affecting but preflight fails
    assert ad.decide("x", "y", True, "", aff, False, "dirty")[0] == "refuse"
    # all clear
    assert ad.decide("x", "y", True, "", aff, True, "")[0] == "deploy"
    print("ok test_decide_orderings")


def test_run_tick_build_fail_no_advance():
    now = datetime.datetime(2026, 7, 1, tzinfo=UTC)
    with tempfile.TemporaryDirectory() as d:
        root, c1 = _git_repo(d)
        (root / "wiki").mkdir()
        (root / "wiki" / "x.md").write_text("# x\n")
        _git(root, "add", "-A")
        _git(root, "commit", "-q", "-m", "c2 site-affecting")
        c2 = _git(root, "rev-parse", "HEAD").stdout.strip()
        _git(root, "reset", "-q", "--hard", c1)             # serving checkout sits at c1
        ad.write_deployed_sha(root, c1)
        _auth(root, authorized_sha=c2,
              authorized_at="2026-06-18T00:00:00Z", expires_at="2026-12-31T00:00:00Z")
        out = ad.run_tick(root, now=now, ancestor_check=lambda s: True,
                          runner=lambda: 1,                  # build FAILS
                          fetch=lambda: subprocess.CompletedProcess([], 0),
                          merge=lambda: True)                # pretend ff worked
        assert out["blocked"] is True
        assert ad.read_deployed_sha(root) == c1              # NOT advanced
    print("ok test_run_tick_build_fail_no_advance")
```

- [ ] **Step 2: Run to verify fail** → FAIL (`no attribute 'decide'`).

- [ ] **Step 3: Implement** — add to `compile/autodeploy.py`:

```python
def read_deployed_sha(root):
    p = root / "compile" / ".deployed-sha"
    return p.read_text().strip() if p.exists() else None


def write_deployed_sha(root, sha):
    (root / "compile").mkdir(parents=True, exist_ok=True)
    (root / "compile" / ".deployed-sha").write_text(sha + "\n")


def diff_names(root, a, b):
    r = sh("git", "-C", str(root), "diff", "--name-only", "%s..%s" % (a, b))
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
    if deployed is None:                       # first run: adopt target, do not deploy
        write_deployed_sha(root, target)
        return status(False, "initialized at authorized sha", target, target, True)

    changed = diff_names(root, deployed, target)
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
```

- [ ] **Step 4: Run to verify pass** → `ok test_decide_orderings`, `ok test_run_tick_build_fail_no_advance`, `all 11 tests passed`.

- [ ] **Step 5: Commit**

```bash
git add compile/autodeploy.py compile/test_autodeploy.py
git commit -m "feat(autodeploy): decide + run_tick orchestration + main wiring"
```

---

### Task 7: `build_site.py` client-side deploy banner + footer

**Files:**
- Modify: `compile/build_site.py`
- Modify: `compile/test_autodeploy.py` (assert the script is baked in)

**Interfaces:**
- Produces: `deploy_status_script() -> str` in `build_site.py` (a self-contained `<script>` that fetches `deploy-status.json` and renders a banner + footer). Injected into both `page(...)` and `arc_page(...)` just before `</body>`.

- [ ] **Step 1: Write the failing test** — append to `compile/test_autodeploy.py`:

```python
def test_build_site_bakes_deploy_fetch():
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import build_site  # noqa
    script = build_site.deploy_status_script()
    assert "deploy-status.json" in script and "<script" in script
    print("ok test_build_site_bakes_deploy_fetch")
```

- [ ] **Step 2: Run to verify fail** → FAIL (`no attribute 'deploy_status_script'`).

- [ ] **Step 3: Implement** — in `compile/build_site.py`, add the helper near the top-level functions:

```python
def deploy_status_script():
    """Client-side: fetch deploy-status.json (written by autodeploy.py each tick,
    NOT baked at build time) and render a blocked banner + a live footer."""
    return (
        '<div id="deploy-banner" hidden></div>'
        '<div id="deploy-foot" class="deploy-foot"></div>'
        '<script>(function(){fetch("deploy-status.json",{cache:"no-store"})'
        '.then(function(r){return r.ok?r.json():null}).then(function(s){if(!s)return;'
        'var f=document.getElementById("deploy-foot");'
        'if(f)f.textContent="live deploy: "+String(s.deployed_sha||"").slice(0,7)+" · "+(s.checked||"");'
        'if(s.blocked){var b=document.getElementById("deploy-banner");'
        'b.hidden=false;b.className="deploy-blocked";'
        'b.textContent="\\u26a0 Auto-deploy blocked: "+s.reason+" (since "+(s.since||"?")+'
        '") \\u2014 the live site may be behind authorized main."}}).catch(function(){})})();</script>'
    )
```

Then inject it before `</body>` in both renderers. In `page(...)`, find the `'</div></header>'` segment of the return and add `+ deploy_status_script()` right before the closing `'</body></html>'`. Do the same in `arc_page(...)`. (Locate each `</body>` in the returned string and prepend `deploy_status_script() +`.)

- [ ] **Step 4: Run to verify pass**, then regenerate to confirm no crash:

```bash
python3 compile/test_autodeploy.py            # ok test_build_site_bakes_deploy_fetch
python3 compile/build_site.py                 # builds dist/ without error
grep -l deploy-status.json dist/index.html    # the fetch is baked into the page
```
Expected: tests pass; `dist/index.html` listed.

- [ ] **Step 5: Commit**

```bash
git add compile/build_site.py compile/test_autodeploy.py
git commit -m "feat(autodeploy): bake client-side deploy-status banner into pages"
```

---

### Task 8: live widget on `wiki/deployment-arc.md`

**Files:**
- Modify: `wiki/deployment-arc.md`

**Interfaces:** none (content + the same client-side fetch, scoped to a named container).

- [ ] **Step 1: Add the widget** — append to `wiki/deployment-arc.md` a section:

```markdown
## Live deploy status

<div id="live-deploy"></div>
<script>(function(){fetch("deploy-status.json",{cache:"no-store"}).then(function(r){return r.ok?r.json():null}).then(function(s){if(!s)return;var el=document.getElementById("live-deploy");if(!el)return;var rows=(s.recent||[]).slice().reverse().map(function(e){return e.at+" — "+String(e.sha).slice(0,7)+" ("+e.result+")"}).join("<br>");el.innerHTML="<strong>"+(s.blocked?"⚠ blocked: "+s.reason:"live: "+String(s.deployed_sha||"").slice(0,7))+"</strong><br>checked "+(s.checked||"")+"<br><br>recent:<br>"+rows;}).catch(function(){})})();</script>
```

(The civilization documenting its own building — this page about deployment shows the actual live deploy state.)

- [ ] **Step 2: Verify the page builds and carries the fetch**

```bash
python3 compile/build_site.py
grep -c deploy-status.json dist/deployment-arc.html   # >= 1
```
Expected: a positive count.

- [ ] **Step 3: Commit**

```bash
git add wiki/deployment-arc.md
git commit -m "feat(autodeploy): live deploy-status widget on deployment-arc"
```

---

### Task 9: inert systemd units + REBUILD runbook

**Files:**
- Create: `compile/systemd/civwiki-autodeploy.service`
- Create: `compile/systemd/civwiki-autodeploy.timer`
- Modify: `compile/REBUILD.md`

**Interfaces:** none (shipped inert; not installed).

- [ ] **Step 1: Create the service** — `compile/systemd/civwiki-autodeploy.service`:

```ini
[Unit]
Description=Civilization Wiki auto-deploy poller (one tick)
After=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 /home/transpara/transpara-ai/repos/civilization-wiki/compile/autodeploy.py
```

- [ ] **Step 2: Create the timer** — `compile/systemd/civwiki-autodeploy.timer`:

```ini
[Unit]
Description=Run the Civilization Wiki auto-deploy poller every 2 minutes

[Timer]
OnBootSec=2min
OnUnitActiveSec=2min
Persistent=true

[Install]
WantedBy=timers.target
```

- [ ] **Step 3: Add the runbook** — append to `compile/REBUILD.md`:

```markdown
## Auto-deploy poller (NOT auto-installed)

`compile/autodeploy.py` deploys the **authorized** commit when an authorized,
site-affecting merge lands. It is fail-closed and self-hosting; it never
commits/pushes/forces. Shipped inert — activation and authorization are
deliberate human steps.

**Authorize a deploy** (per reviewed commit):
1. `cp compile/deploy-authorization.example.json compile/deploy-authorization.json`
   (the real file is git-ignored).
2. Set `authorized_sha` to the exact 40-char SHA to publish (must be an ancestor
   of `origin/main`), `authority`, `authorized_at`/`expires_at` (ISO-8601), `reason`.

**Activate the timer** (user units, no root):
```
loginctl enable-linger transpara
mkdir -p ~/.config/systemd/user
cp compile/systemd/civwiki-autodeploy.* ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now civwiki-autodeploy.timer
journalctl --user -u civwiki-autodeploy -f      # logs
```
A blocked tick (unauthorized / dirty / build-fail) leaves the live site
untouched and flips the on-page "Auto-deploy blocked" banner.
```

- [ ] **Step 4: Verify units parse + module imports clean**

```bash
python3 -c "import pathlib,configparser as c; [c.ConfigParser(strict=False, delimiters=('=',)).read(p) or print('ok',p) for p in ['compile/systemd/civwiki-autodeploy.service','compile/systemd/civwiki-autodeploy.timer']]"
python3 compile/autodeploy.py --help 2>/dev/null; python3 -c "import sys; sys.path.insert(0,'compile'); import autodeploy; print('import ok')"
python3 compile/test_autodeploy.py    # full suite green
```
Expected: `ok ...` for both units, `import ok`, and `all 12 tests passed`.

- [ ] **Step 5: Commit**

```bash
git add compile/systemd/ compile/REBUILD.md
git commit -m "feat(autodeploy): inert systemd units + install/authorization runbook"
```

---

## Final verification (before PR)

- [ ] `python3 compile/test_autodeploy.py` → `all 12 tests passed`
- [ ] `python3 compile/test_stats.py` and `python3 compile/test_inflight.py` → still green (no regressions)
- [ ] `python3 compile/build_site.py` → builds `dist/` clean; `dist/index.html` + `dist/deployment-arc.html` contain `deploy-status.json`
- [ ] `git grep -n "deploy-authorization.json" -- . ':!*.example.json' ':!.gitignore' ':!*REBUILD*' ':!*autodeploy.py' ':!*test_*'` → no real authorization committed
- [ ] Confirm `compile/deploy-authorization.json`, `compile/.deployed-sha`, `dist/deploy-status.json` are git-ignored (`git status --porcelain` clean after a local run)
- [ ] Open PR `feat/wiki-autodeploy` → `main`; **do not merge**; **do not activate the timer**

## Spec Coverage

- site_affecting → Task 1 · authorized (full domain) → Task 2 · preflight → Task 3 · status/history + since → Task 4 · deploy → Task 5 · decide/run_tick/build-fail-no-advance → Task 6 · client-side banner (reuses fetch pattern) → Task 7 · self-referential deployment-arc widget → Task 8 · inert systemd + authorization PR-safety + runbook → Task 9. Deploy-the-authorized-SHA, deny-closed gate ordering, no-commit invariant, and build boundary are enforced across Tasks 2/6/9 and Final verification.
