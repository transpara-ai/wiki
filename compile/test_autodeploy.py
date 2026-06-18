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


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
    print("\nall %d tests passed" % len(fns))
