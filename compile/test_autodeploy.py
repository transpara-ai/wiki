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


def test_deploy_merge_and_build_outcomes():
    root = pathlib.Path(".")
    sha = "a" * 40
    assert ad.deploy(root, sha, runner=lambda: 0, merge=lambda: True)[0] is True
    assert ad.deploy(root, sha, runner=lambda: 1, merge=lambda: True)[0] is False   # build fail
    assert ad.deploy(root, sha, runner=lambda: 0, merge=lambda: False)[0] is False  # merge fail
    print("ok test_deploy_merge_and_build_outcomes")


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


def test_build_site_bakes_deploy_fetch():
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import build_site  # noqa
    script = build_site.deploy_status_script()
    assert "deploy-status.json" in script and "<script" in script
    print("ok test_build_site_bakes_deploy_fetch")


def test_run_tick_diff_error_refuses_and_no_advance():
    """Blocker 1: a corrupt/stale deployed-sha makes `git diff` fail; that
    ambiguous state must REFUSE (gate 4), never skip-and-advance the SHA."""
    now = datetime.datetime(2026, 7, 1, tzinfo=UTC)
    with tempfile.TemporaryDirectory() as d:
        root, c1 = _git_repo(d)
        bogus = "d" * 40                          # 40-hex but not a real object
        ad.write_deployed_sha(root, bogus)        # corrupt/stale deployed-sha
        _auth(root, authorized_sha=c1,
              authorized_at="2026-06-18T00:00:00Z", expires_at="2026-12-31T00:00:00Z")
        out = ad.run_tick(root, now=now, ancestor_check=lambda s: True,
                          runner=lambda: 0,
                          fetch=lambda: subprocess.CompletedProcess([], 0),
                          merge=lambda: True)
        assert out["blocked"] is True                       # refuse, not skip
        assert ad.read_deployed_sha(root) == bogus          # NOT advanced
    print("ok test_run_tick_diff_error_refuses_and_no_advance")


def test_run_tick_first_run_inits_to_head_not_target():
    """Blocker 2: first run (no state) must record the CURRENT checkout HEAD
    (what dist/ was built from), not the authorized target — else a checkout
    behind the authorized commit is silently marked deployed and never builds."""
    now = datetime.datetime(2026, 7, 1, tzinfo=UTC)
    with tempfile.TemporaryDirectory() as d:
        root, c1 = _git_repo(d)
        (root / "wiki").mkdir()
        (root / "wiki" / "x.md").write_text("# x\n")
        _git(root, "add", "-A")
        _git(root, "commit", "-q", "-m", "c2 site-affecting")
        c2 = _git(root, "rev-parse", "HEAD").stdout.strip()
        _git(root, "reset", "-q", "--hard", c1)             # HEAD=c1; dist built from c1
        # NO deployed-sha (first run); authorize the NEWER c2
        _auth(root, authorized_sha=c2,
              authorized_at="2026-06-18T00:00:00Z", expires_at="2026-12-31T00:00:00Z")
        out = ad.run_tick(root, now=now, ancestor_check=lambda s: True,
                          runner=lambda: 0,
                          fetch=lambda: subprocess.CompletedProcess([], 0),
                          merge=lambda: True)
        assert out["blocked"] is False
        assert ad.read_deployed_sha(root) == c1             # HEAD, NOT the target c2
    print("ok test_run_tick_first_run_inits_to_head_not_target")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
    print("\nall %d tests passed" % len(fns))
