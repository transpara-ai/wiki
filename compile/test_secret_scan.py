#!/usr/bin/env python3
"""Stdlib-assert tests for compile/secret_scan.py — the fail-closed secret scanner.

Design packet: docs/superpowers/specs/2026-07-01-secret-scan-hook-design.md
(AC1-AC10; one named test per AC clause, per the section-5 map).
Test secrets are synthetic and generated at runtime — never committed (AC8 note).
"""
import ast
import datetime
import hashlib
import json
import os
import pathlib
import random
import re
import string
import subprocess
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import secret_scan  # noqa: E402

WIKI_ROOT = pathlib.Path(__file__).resolve().parents[1]
SCANNER = pathlib.Path(__file__).resolve().parent / "secret_scan.py"
PYTHON = sys.executable
ZERO_SHA = "0" * 40


def utc_today():
    return datetime.datetime.now(datetime.timezone.utc).date()

_rng = random.Random(20260702)


# ---------------------------------------------------------------- helpers

def sh(args, cwd, env=None, check=True):
    e = dict(os.environ)
    if env:
        e.update(env)
    proc = subprocess.run(args, cwd=str(cwd), env=e,
                          capture_output=True, text=True)
    if check and proc.returncode != 0:
        raise AssertionError("command failed: %r\n%s\n%s"
                             % (args, proc.stdout, proc.stderr))
    return proc


def make_repo(root):
    root = pathlib.Path(root)
    sh(["git", "init", "-q", "-b", "main"], root)
    sh(["git", "config", "user.email", "test@test"], root)
    sh(["git", "config", "user.name", "test"], root)
    (root / "seed.txt").write_text("hello\n")
    sh(["git", "add", "seed.txt"], root)
    sh(["git", "commit", "-q", "-m", "seed"], root)
    return root


def run_scanner(args, cwd, env=None):
    e = dict(os.environ)
    if env:
        e.update(env)
    return subprocess.run([PYTHON, str(SCANNER)] + args, cwd=str(cwd),
                          env=e, capture_output=True, text=True)


# Fixture alphabets and armor strings are COMPOSED at runtime so that no
# committed source literal matches a detector (design §5: fixtures are never
# committed; the scanner must scan its own tree clean without self-entries).
UPPER = string.ascii_uppercase
ALNUM = string.ascii_uppercase + string.ascii_lowercase + string.digits
B64 = ALNUM + "+/"
B64URL = ALNUM + "-_"
PEM_HEAD = "-----BEGIN RSA " + "PRIVATE KEY-----"
PEM_TAIL = "-----END RSA " + "PRIVATE KEY-----"


def gen_aws_key():
    return "AKIA" + "".join(_rng.choices(UPPER + string.digits, k=16))


def gen_token(charset, length, min_entropy=0.0):
    while True:
        tok = "".join(_rng.choices(charset, k=length))
        if secret_scan.shannon_entropy(tok) >= min_entropy:
            return tok


def fp_entry(rule_id, path, blob_bytes, match_text, byte_offset, **over):
    entry = {
        "type": "fingerprint",
        "rule_id": rule_id,
        "canonical_path": path,
        "blob_sha256": hashlib.sha256(blob_bytes).hexdigest(),
        "match_sha256": hashlib.sha256(match_text.encode("utf-8")).hexdigest(),
        "byte_offset": byte_offset,
        "reason": "test fixture",
        "owner": "test",
        "reviewed_by": "test",
        "reviewed_on": utc_today().isoformat(),
        "expires_on": (utc_today() + datetime.timedelta(days=30)).isoformat(),
    }
    entry.update(over)
    return entry


def br_entry(path, blob_bytes, **over):
    entry = {
        "type": "blob_review",
        "canonical_path": path,
        "blob_sha256": hashlib.sha256(blob_bytes).hexdigest(),
        "reason": "test fixture",
        "owner": "test",
        "reviewed_by": "test",
        "reviewed_on": utc_today().isoformat(),
        "expires_on": (utc_today() + datetime.timedelta(days=30)).isoformat(),
    }
    entry.update(over)
    return entry


def write_allowlist(root, entries, stage=True):
    p = pathlib.Path(root) / "compile"
    p.mkdir(exist_ok=True)
    (p / ".secretsallow").write_text(
        "".join(json.dumps(e) + "\n" for e in entries))
    if stage:
        # the review record must travel with the commit it clears (CFAR F2):
        # staged-mode scans read the INDEX copy of the allowlist
        sh(["git", "add", "compile/.secretsallow"], root)


# ------------------------------------------------------------- AC1 / AC2

def test_planted_secret_blocked():
    with tempfile.TemporaryDirectory() as d:
        root = make_repo(d)
        sh(["git", "config", "core.hooksPath", str(WIKI_ROOT / ".githooks")], root)
        (root / "config.py").write_text("aws_id = '%s'\n" % gen_aws_key())
        sh(["git", "add", "config.py"], root)
        proc = sh(["git", "commit", "-m", "x"], root, check=False)
        assert proc.returncode != 0, "commit with planted secret must be blocked"
    print("ok test_planted_secret_blocked")


def test_secret_in_pathname_blocked():
    # CFAR F14: a credential can live in the tracked PATH with clean file
    # content — the pathname is a scan unit of its own, and path findings
    # are NON-CLEARABLE: an allowlist entry would embed the secret-bearing
    # path in .secretsallow (self-referential regress); remediation is a
    # rename, not an attestation
    k = gen_aws_key()
    rel = "cfg/%s/note.txt" % k
    with tempfile.TemporaryDirectory() as d:
        root = make_repo(d)
        (root / "cfg" / k).mkdir(parents=True)
        (root / rel).write_text("clean content\n")
        sh(["git", "add", rel], root)
        proc = run_scanner(["--staged"], root)
        assert proc.returncode != 0, "secret in the pathname must block"
        out = proc.stdout + proc.stderr
        assert "pathname" in out
        assert "rename" in out.lower()
        # CFAR F15: the report must not copy the credential-bearing path
        # into hook/CI logs — matched spans are redacted
        assert k not in out, "the matched path secret must never be printed"
        assert "<redacted:" in out
    print("ok test_secret_in_pathname_blocked")


def test_clean_passes():
    with tempfile.TemporaryDirectory() as d:
        root = make_repo(d)
        sh(["git", "config", "core.hooksPath", str(WIKI_ROOT / ".githooks")], root)
        (root / "notes.md").write_text("nothing secret here\n")
        sh(["git", "add", "notes.md"], root)
        proc = sh(["git", "commit", "-m", "x"], root, check=False)
        assert proc.returncode == 0, \
            "clean commit must pass: %s%s" % (proc.stdout, proc.stderr)
    print("ok test_clean_passes")


# ------------------------------------------------------------------- AC3

def test_ci_changed_against_blocks_on_secret():
    with tempfile.TemporaryDirectory() as d:
        root = make_repo(d)
        sh(["git", "checkout", "-q", "-b", "feat"], root)
        (root / "leak.txt").write_text("key: %s\n" % gen_aws_key())
        sh(["git", "add", "leak.txt"], root)
        sh(["git", "commit", "-q", "-m", "leak"], root)
        proc = run_scanner(["--changed-against", "main"], root)
        assert proc.returncode != 0, "PR diff with secret must block"
    print("ok test_ci_changed_against_blocks_on_secret")


def test_secret_added_then_removed_in_history_blocked():
    with tempfile.TemporaryDirectory() as d:
        root = make_repo(d)
        sh(["git", "checkout", "-q", "-b", "feat"], root)
        (root / "leak.txt").write_text("key: %s\n" % gen_aws_key())
        sh(["git", "add", "leak.txt"], root)
        sh(["git", "commit", "-q", "-m", "add secret"], root)
        (root / "leak.txt").write_text("clean now\n")
        sh(["git", "add", "leak.txt"], root)
        sh(["git", "commit", "-q", "-m", "remove secret"], root)
        proc = run_scanner(["--changed-against", "main"], root)
        assert proc.returncode != 0, \
            "secret in PR history (removed before final diff) must still block"
    print("ok test_secret_added_then_removed_in_history_blocked")


def test_secret_in_merge_commit_blocked():
    with tempfile.TemporaryDirectory() as d:
        root = make_repo(d)
        # two branches editing the same file -> conflicting merge
        sh(["git", "checkout", "-q", "-b", "left"], root)
        (root / "seed.txt").write_text("left\n")
        sh(["git", "commit", "-q", "-am", "left"], root)
        sh(["git", "checkout", "-q", "main"], root)
        sh(["git", "checkout", "-q", "-b", "feat"], root)
        (root / "seed.txt").write_text("right\n")
        sh(["git", "commit", "-q", "-am", "right"], root)
        proc = sh(["git", "merge", "left"], root, check=False)
        assert proc.returncode != 0, "expected a conflict"
        # resolve the conflict by introducing a secret in the merge commit
        (root / "seed.txt").write_text("resolved: %s\n" % gen_aws_key())
        sh(["git", "add", "seed.txt"], root)
        sh(["git", "commit", "-q", "-m", "merge with secret resolution"], root)
        # then remove it again so the final diff is clean
        (root / "seed.txt").write_text("resolved cleanly\n")
        sh(["git", "commit", "-q", "-am", "clean up"], root)
        proc = run_scanner(["--changed-against", "main"], root)
        assert proc.returncode != 0, \
            "secret introduced by a merge-commit resolution must block"
    print("ok test_secret_in_merge_commit_blocked")


def test_scan_step_lives_in_required_build_and_test_job():
    ci = (WIKI_ROOT / ".github" / "workflows" / "ci.yml").read_text()
    build_test = ci[ci.index("name: Build & Test"):]
    assert "fetch-depth: 0" in build_test, \
        "required job must check out full history for the history scan"
    assert "--changed-against" in build_test, \
        "secret-scan step must live inside the required Build & Test job"
    scan_at = build_test.index("--changed-against")
    step_start = build_test.rfind("- name:", 0, scan_at)
    step_text = build_test[step_start:scan_at + 200]
    assert "timeout-minutes" in step_text, "scan step needs a timeout bound"
    assert "github.base_ref" in build_test, "pull_request base semantics missing"
    assert "github.event.before" in build_test, "push base semantics missing"
    # CFAR F3: the executed scanner must be extracted from the TRUSTED base
    # ref, not the PR head — a PR editing secret_scan.py must not be able to
    # neuter the gate that scans it (bootstrap fallback only when the base
    # predates the scanner)
    assert re.search(r"git show \"?\$\{?BASE\}?\"?:compile/secret_scan\.py",
                     step_text), \
        "scanner must be extracted from the trusted base ref"
    assert "secret_scan_trusted" in step_text, \
        "trusted scanner copy must be what CI executes"
    # CFAR F4: the gate runs before any dependency install executes
    # untrusted lifecycle code (scanner is stdlib-only, needs no installs)
    for install_marker in ("pip install", "npm ci"):
        assert step_start < build_test.index(install_marker), \
            "secret scan must run before '%s'" % install_marker
    pkg = json.loads((WIKI_ROOT / "package.json").read_text())
    assert "compile/test_secret_scan.py" in pkg["scripts"]["test:py"], \
        "tests must be enumerated in the verify script or they never run"
    print("ok test_scan_step_lives_in_required_build_and_test_job")


# ------------------------------------------------------------------- AC4

def test_scanner_error_fails_closed():
    with tempfile.TemporaryDirectory() as d:
        root = make_repo(d)
        (root / "f.txt").write_text("clean\n")
        sh(["git", "add", "f.txt"], root)
        # git made unavailable -> the scanner must block, not pass
        proc = run_scanner(["--staged"], root, env={"PATH": ""})
        assert proc.returncode != 0, "scanner error must fail closed"
    print("ok test_scanner_error_fails_closed")


def test_scanner_timeout_fails_closed():
    with tempfile.TemporaryDirectory() as d:
        root = make_repo(d)
        (root / "f.txt").write_text("clean\n")
        sh(["git", "add", "f.txt"], root)
        proc = run_scanner(["--staged", "--max-seconds", "0.000001"], root)
        assert proc.returncode != 0, "timeout must fail closed"
        out = (proc.stdout + proc.stderr).lower()
        assert "timeout" in out or "timed out" in out
    # CFAR F5: the hook's bound is the scanner's portable in-process
    # --max-seconds — a hard dependency on coreutils `timeout` would falsely
    # block every commit on macOS/BSD clones
    hook = (WIKI_ROOT / ".githooks" / "pre-commit").read_text()
    assert "--max-seconds" in hook, "hook must bound the scan in-process"
    assert not re.search(r"(?m)^\s*(if\s+)?timeout\s", hook), \
        "hook must not depend on the non-portable coreutils timeout binary"
    print("ok test_scanner_timeout_fails_closed")


# ------------------------------------------------------------------- AC5

def test_stdlib_only_no_network():
    allowed = {
        "argparse", "dataclasses", "datetime", "hashlib", "json", "math",
        "os", "pathlib", "re", "signal", "subprocess", "sys",
    }
    tree = ast.parse(SCANNER.read_text())
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add((node.module or "").split(".")[0])
    assert imported <= allowed, "unexpected imports: %s" % (imported - allowed)
    forbidden = {"socket", "urllib", "http", "requests", "ssl", "asyncio"}
    assert not (imported & forbidden)
    print("ok test_stdlib_only_no_network")


# ------------------------------------------------------------------- AC6

def _staged_secret_repo(d, content, path="cfg.py"):
    root = make_repo(d)
    (root / path).write_text(content)
    sh(["git", "add", path], root)
    return root


def test_allowlist_entry_does_not_cover_sibling_findings():
    k1, k2 = gen_aws_key(), gen_aws_key()
    content = "a = '%s'\nb = '%s'\n" % (k1, k2)
    blob = content.encode("utf-8")
    with tempfile.TemporaryDirectory() as d:
        root = _staged_secret_repo(d, content)
        write_allowlist(root, [fp_entry("aws-access-key-id", "cfg.py", blob,
                                        k1, content.index(k1))])
        proc = run_scanner(["--staged"], root)
        assert proc.returncode != 0, "sibling finding (k2) must stay blocking"
        write_allowlist(root, [
            fp_entry("aws-access-key-id", "cfg.py", blob, k1, content.index(k1)),
            fp_entry("aws-access-key-id", "cfg.py", blob, k2, content.index(k2)),
        ])
        proc = run_scanner(["--staged"], root)
        assert proc.returncode == 0, \
            "both findings cleared -> pass: %s%s" % (proc.stdout, proc.stderr)
    print("ok test_allowlist_entry_does_not_cover_sibling_findings")


def test_duplicate_identical_matches_need_separate_entries():
    k = gen_aws_key()
    content = "a = '%s'\nb = '%s'\n" % (k, k)
    blob = content.encode("utf-8")
    off1 = content.index(k)
    off2 = content.index(k, off1 + 1)
    with tempfile.TemporaryDirectory() as d:
        root = _staged_secret_repo(d, content)
        write_allowlist(root, [fp_entry("aws-access-key-id", "cfg.py", blob, k, off1)])
        proc = run_scanner(["--staged"], root)
        assert proc.returncode != 0, \
            "identical match at a second offset must stay blocking"
        write_allowlist(root, [
            fp_entry("aws-access-key-id", "cfg.py", blob, k, off1),
            fp_entry("aws-access-key-id", "cfg.py", blob, k, off2),
        ])
        proc = run_scanner(["--staged"], root)
        assert proc.returncode == 0, proc.stdout + proc.stderr
    print("ok test_duplicate_identical_matches_need_separate_entries")


def test_allowlist_entry_does_not_cover_other_paths():
    k = gen_aws_key()
    content = "a = '%s'\n" % k
    blob = content.encode("utf-8")
    with tempfile.TemporaryDirectory() as d:
        root = make_repo(d)
        for p in ("one.py", "two.py"):
            (root / p).write_text(content)
        sh(["git", "add", "one.py", "two.py"], root)
        write_allowlist(root, [fp_entry("aws-access-key-id", "one.py", blob,
                                        k, content.index(k))])
        proc = run_scanner(["--staged"], root)
        assert proc.returncode != 0, \
            "identical blob at an unreviewed path must stay blocking"
    print("ok test_allowlist_entry_does_not_cover_other_paths")


def test_blob_review_rejected_for_text_blobs():
    k = gen_aws_key()
    content = "a = '%s'\n" % k
    with tempfile.TemporaryDirectory() as d:
        root = _staged_secret_repo(d, content)
        write_allowlist(root, [br_entry("cfg.py", content.encode("utf-8"))])
        proc = run_scanner(["--staged"], root)
        assert proc.returncode != 0, \
            "blob_review must never clear a text-scanned blob"
    print("ok test_blob_review_rejected_for_text_blobs")


def test_allowlist_snapshot_matches_scan_mode():
    k = gen_aws_key()
    content = "a = '%s'\n" % k
    blob = content.encode("utf-8")
    entry = fp_entry("aws-access-key-id", "cfg.py", blob, k, content.index(k))
    with tempfile.TemporaryDirectory() as d:
        # staged mode: an UNSTAGED working-tree allowlist must not clear a
        # staged secret — the review record would not travel with the commit
        root = _staged_secret_repo(d, content)
        write_allowlist(root, [entry], stage=False)
        proc = run_scanner(["--staged"], root)
        assert proc.returncode != 0, \
            "unstaged allowlist must not clear a staged secret"
        sh(["git", "add", "compile/.secretsallow"], root)
        assert run_scanner(["--staged"], root).returncode == 0
    with tempfile.TemporaryDirectory() as d:
        # tree mode: the allowlist snapshot comes from the scanned tree,
        # never from the (possibly dirty) working tree
        root = _staged_secret_repo(d, content)
        sh(["git", "commit", "-q", "--no-verify", "-m", "secret only"], root)
        write_allowlist(root, [entry], stage=False)
        proc = run_scanner(["--tree", "HEAD"], root)
        assert proc.returncode != 0, \
            "working-tree allowlist must not clear a committed-tree finding"
    print("ok test_allowlist_snapshot_matches_scan_mode")


def test_allowlist_fingerprint_reflags_on_edit():
    k = gen_aws_key()
    content = "a = '%s'\n" % k
    blob = content.encode("utf-8")
    with tempfile.TemporaryDirectory() as d:
        root = _staged_secret_repo(d, content)
        write_allowlist(root, [fp_entry("aws-access-key-id", "cfg.py", blob,
                                        k, content.index(k))])
        assert run_scanner(["--staged"], root).returncode == 0
        edited = "# comment\n" + content
        (root / "cfg.py").write_text(edited)
        sh(["git", "add", "cfg.py"], root)
        proc = run_scanner(["--staged"], root)
        assert proc.returncode != 0, "edited blob must re-flag"
    print("ok test_allowlist_fingerprint_reflags_on_edit")


def test_scanner_tree_scans_clean():
    proc = run_scanner(["--tree", "HEAD"], WIKI_ROOT)
    assert proc.returncode == 0, \
        "the wiki tree (scanner + config included) must scan clean:\n%s%s" \
        % (proc.stdout, proc.stderr)
    print("ok test_scanner_tree_scans_clean")


# ------------------------------------------------------------------- AC7

def test_edge_cases_fail_safe():
    with tempfile.TemporaryDirectory() as d:
        root = make_repo(d)  # nothing staged
        proc = run_scanner(["--staged"], root)
        assert proc.returncode == 0, "provably-empty stage passes"
    print("ok test_edge_cases_fail_safe")


def test_binary_blob_blocks():
    payload = b"\x00\x01binary" + gen_aws_key().encode() + b"\x00"
    with tempfile.TemporaryDirectory() as d:
        root = make_repo(d)
        (root / "blob.bin").write_bytes(payload)
        sh(["git", "add", "blob.bin"], root)
        proc = run_scanner(["--staged"], root)
        assert proc.returncode != 0, "binary blob must block by default"
        write_allowlist(root, [br_entry("blob.bin", payload)])
        proc = run_scanner(["--staged"], root)
        assert proc.returncode == 0, \
            "blob_review clears binary: %s%s" % (proc.stdout, proc.stderr)
    print("ok test_binary_blob_blocks")


def test_oversized_blob_blocks():
    payload = (b"x" * 1024 + b"\n") * 1025  # > 1 MiB, pure text
    with tempfile.TemporaryDirectory() as d:
        root = make_repo(d)
        (root / "big.txt").write_bytes(payload)
        sh(["git", "add", "big.txt"], root)
        proc = run_scanner(["--staged"], root)
        assert proc.returncode != 0, "oversized blob must block by default"
        write_allowlist(root, [br_entry("big.txt", payload)])
        proc = run_scanner(["--staged"], root)
        assert proc.returncode == 0, proc.stdout + proc.stderr
        # CFAR F12: without a blob_review candidate the oversized block must
        # be decided from the size alone — the content is never materialized
        # (a multi-GB accident must block cheaply, not OOM the hook)
        oid = sh(["git", "rev-parse", ":big.txt"], root).stdout.strip()
        real_read = secret_scan.read_blob
        secret_scan.read_blob = lambda *_a, **_k: (_ for _ in ()).throw(
            AssertionError("oversized content must not be materialized"))
        try:
            out = secret_scan.scan_occurrence(
                root, "big.txt", oid, secret_scan.Allowlist([], []))
        finally:
            secret_scan.read_blob = real_read
        assert out.outcome == "block" and "oversized" in out.reason
    print("ok test_oversized_blob_blocks")


def test_gitlink_blocks():
    k = gen_aws_key()
    with tempfile.TemporaryDirectory() as d:
        root = make_repo(d)
        head = sh(["git", "rev-parse", "HEAD"], root).stdout.strip()
        # the gitlink path itself carries a credential: the block report
        # must not echo it (CFAR F16 — same class as F15)
        sh(["git", "update-index", "--add", "--cacheinfo",
            "160000,%s,vendor/%s/sub" % (head, k)], root)
        proc = run_scanner(["--staged"], root)
        assert proc.returncode != 0, "gitlink (mode 160000) must block"
        out = proc.stdout + proc.stderr
        assert k not in out, "gitlink path secret must never be printed"
        assert "<redacted:" in out
    print("ok test_gitlink_blocks")


def test_undecodable_path_blocks_without_echo():
    # CFAR F17: a non-UTF-8 filename fails closed, and the raw bytes —
    # possibly credential-shaped — are identified by hash, never echoed
    k = gen_aws_key()
    with tempfile.TemporaryDirectory() as d:
        root = make_repo(d)
        raw_name = k.encode("ascii") + b"_\xff.txt"
        with open(os.path.join(d.encode("utf-8"), raw_name), "wb") as fh:
            fh.write(b"clean\n")
        sh(["git", "add", "-A"], root)
        proc = run_scanner(["--staged"], root)
        assert proc.returncode != 0, "undecodable path must fail closed"
        out = proc.stdout + proc.stderr
        assert k not in out, "raw path bytes must never be echoed"
    print("ok test_undecodable_path_blocks_without_echo")


def test_gitmodules_change_blocks():
    with tempfile.TemporaryDirectory() as d:
        root = make_repo(d)
        (root / ".gitmodules").write_text(
            '[submodule "s"]\n\tpath = s\n\turl = ../s\n')
        sh(["git", "add", ".gitmodules"], root)
        proc = run_scanner(["--staged"], root)
        assert proc.returncode != 0, \
            ".gitmodules change must block independently of any gitlink"
        # tree mode is the evidence surface — a committed .gitmodules must
        # block there too, not fall through to a text scan
        sh(["git", "commit", "-q", "-m", "modules"], root)
        proc = run_scanner(["--tree", "HEAD"], root)
        assert proc.returncode != 0, \
            ".gitmodules present in a scanned tree must block"
    print("ok test_gitmodules_change_blocks")


def test_unreadable_blob_non_clearable():
    fake_sha = "deadbeef" * 5
    with tempfile.TemporaryDirectory() as d:
        root = make_repo(d)
        # a blob_review for the path cannot matter: content hash is unknowable
        allow = secret_scan.Allowlist([], [])
        outcome = secret_scan.scan_occurrence(
            pathlib.Path(root), "ghost.txt", fake_sha, allow)
        assert outcome.outcome == "block"
        assert outcome.clearable is False, \
            "unreadable content must never be clearable"
    print("ok test_unreadable_blob_non_clearable")


# ------------------------------------------------------------------- AC8

def test_each_rule_positive_and_negative():
    priv = PEM_HEAD + "\n" + gen_token(B64, 64) + "\n" + PEM_TAIL + "\n"
    # composed so the committed source never contains a matching literal
    sa_type = '"type": "service_' + 'account"'
    sa_pk = '"private_' + 'key": '
    bare_pem = "-----BEGIN " + "PRIVATE KEY-----"
    sa_json = ('{%s, %s"%s\\n%s"}\n'
               % (sa_type, sa_pk, bare_pem, gen_token(B64, 40)))
    sa_negative = "{%s, \"note\": \"no key material\"}\n" % sa_type
    cases = [
        ("private-key", priv, 'prose containing the words private key\n'),
        ("aws-access-key-id", "id = %s\n" % gen_aws_key(),
         "SOMEUPPERCASEWORDHERE20\n"),
        ("github-token",
         "t1 = ghp_%s\nt2 = github_pat_%s\n"
         % (gen_token(ALNUM, 40), gen_token(ALNUM + "_", 30)),
         "ghp_short and github_pat in prose\n"),
        ("slack-token",
         "s = xoxb-%s\n" % gen_token(ALNUM + "-", 24),
         "xox substring and xoxq-0123456789abc\n"),
        ("openai-sk-key",
         "k = sk-proj-%s\n" % gen_token(B64URL, 32),
         "short sk-abc123 in prose\n"),
        ("gcp-sa-json", sa_json, sa_negative),
        ("jwt",
         "j = eyJ%s.%s.%s\n" % (gen_token(B64URL, 12), gen_token(B64URL, 12),
                                gen_token(B64URL, 12)),
         "base64 text without dots eyJhbGciOiJIUzI1NiJ9only\n"),
        ("generic-assignment",
         # three realistic shapes: plain assignment, quoted JSON key, and a
         # compound env-style key (CFAR F7)
         'api_key = "%s"\n{"api_key":"%s"}\nSERVICE_TOKEN=%s\n'
         % (gen_token(B64, 24, min_entropy=3.5),
            gen_token(B64, 24, min_entropy=3.5),
            gen_token(B64, 24, min_entropy=3.5)),
         'password = ""\ntoken = "$TOKEN"\nsecret: changeme\n{"token":""}\n'),
        ("high-entropy",
         "blob %s\n" % gen_token(B64, 40, min_entropy=4.5),
         "sha 0123456789abcdef0123456789abcdef01234567 and "
         "uuid 123e4567-e89b-12d3-a456-426614174000\n"),
    ]
    rule_ids = {r for r, _, _ in cases}
    assert rule_ids == set(secret_scan.RULE_IDS), \
        "test table must cover exactly the design ruleset"
    for rule_id, positive, negative in cases:
        hits = [f.rule_id for f in secret_scan.scan_text(positive)]
        assert rule_id in hits, \
            "%s positive fixture did not fire (got %s)" % (rule_id, hits)
        if rule_id == "generic-assignment":
            assert hits.count(rule_id) == 3, \
                "all three assignment shapes must fire (got %s)" % hits
        misses = {f.rule_id for f in secret_scan.scan_text(negative)}
        assert rule_id not in misses, \
            "%s negative fixture fired falsely" % rule_id
    print("ok test_each_rule_positive_and_negative")


# ------------------------------------------------------------------- AC9

def test_git_error_fails_closed():
    with tempfile.TemporaryDirectory() as d:
        proc = run_scanner(["--changed-against", "main"], d)  # not a repo
        assert proc.returncode != 0, "non-repo must fail closed"
    print("ok test_git_error_fails_closed")


def test_shallow_clone_or_missing_base_fails_closed():
    with tempfile.TemporaryDirectory() as d:
        root = make_repo(d)
        proc = run_scanner(["--changed-against", "no-such-ref"], root)
        assert proc.returncode != 0, "missing base must fail closed"
        for i in range(3):
            (root / "f.txt").write_text("v%d\n" % i)
            sh(["git", "add", "f.txt"], root)
            sh(["git", "commit", "-q", "-m", "c%d" % i], root)
        first = sh(["git", "rev-list", "--max-parents=0", "HEAD"], root).stdout.strip()
        shallow = pathlib.Path(d) / "shallow"
        sh(["git", "clone", "-q", "--depth", "1",
            "file://" + str(root), str(shallow)], d)
        proc = run_scanner(["--changed-against", first], shallow)
        assert proc.returncode != 0, \
            "unresolvable history in a shallow clone must fail closed"
    print("ok test_shallow_clone_or_missing_base_fails_closed")


def test_push_event_zero_base_blocks():
    with tempfile.TemporaryDirectory() as d:
        root = make_repo(d)
        proc = run_scanner(["--changed-against", ZERO_SHA], root)
        assert proc.returncode != 0, "all-zeros push base must fail closed"
    print("ok test_push_event_zero_base_blocks")


# ------------------------------------------------------------------ AC10

def test_allowlist_schema_and_expiry_enforced():
    today = utc_today()
    k = gen_aws_key()
    content = "clean file, no secrets\n"
    bad_lists = [
        "not json at all\n",
        json.dumps({"type": "mystery"}) + "\n",
        # missing keys
        json.dumps({"type": "fingerprint", "rule_id": "aws-access-key-id"}) + "\n",
        # extra key
        json.dumps(dict(fp_entry("aws-access-key-id", "x.py", b"x", k, 0),
                        extra="nope")) + "\n",
        # expired
        json.dumps(fp_entry("aws-access-key-id", "x.py", b"x", k, 0,
                            reviewed_on=(today - datetime.timedelta(days=90)).isoformat(),
                            expires_on=(today - datetime.timedelta(days=1)).isoformat())) + "\n",
        # validity window > 180 days
        json.dumps(fp_entry("aws-access-key-id", "x.py", b"x", k, 0,
                            expires_on=(today + datetime.timedelta(days=200)).isoformat())) + "\n",
        # future-dated review (CFAR F1): would extend validity years from now
        json.dumps(fp_entry("aws-access-key-id", "x.py", b"x", k, 0,
                            reviewed_on=(today + datetime.timedelta(days=10)).isoformat(),
                            expires_on=(today + datetime.timedelta(days=40)).isoformat())) + "\n",
        # duplicate identity
        json.dumps(fp_entry("aws-access-key-id", "x.py", b"x", k, 0)) + "\n"
        + json.dumps(fp_entry("aws-access-key-id", "x.py", b"x", k, 0)) + "\n",
        # duplicate JSON key inside one record (CFAR F10): json.loads keeps
        # the last value silently — the reviewed record would differ from
        # the identity the scanner trusts
        json.dumps(fp_entry("aws-access-key-id", "x.py", b"x", k, 0)).replace(
            '"canonical_path": "x.py"',
            '"canonical_path": "reviewed.py", "canonical_path": "x.py"') + "\n",
        # non-canonical date spelling (CFAR F11): fromisoformat accepts
        # compact forms; the documented grammar is exactly YYYY-MM-DD
        json.dumps(fp_entry("aws-access-key-id", "x.py", b"x", k, 0,
                            reviewed_on=today.strftime("%Y%m%d"))) + "\n",
    ]
    with tempfile.TemporaryDirectory() as d:
        root = make_repo(d)
        (root / "clean.txt").write_text(content)
        sh(["git", "add", "clean.txt"], root)
        for i, bad in enumerate(bad_lists):
            (root / "compile").mkdir(exist_ok=True)
            (root / "compile" / ".secretsallow").write_text(bad)
            sh(["git", "add", "compile/.secretsallow"], root)
            proc = run_scanner(["--staged"], root)
            assert proc.returncode != 0, \
                "invalid allowlist #%d must block even a clean stage" % i
    print("ok test_allowlist_schema_and_expiry_enforced")


def test_ci_does_not_trust_pr_head_allowlist():
    # CFAR F9 (P1): a PR must not be able to add a secret AND a matching
    # allowlist entry in the same change — changed-against mode trusts only
    # the BASE ref's allowlist (entries ratify by merging), never HEAD's.
    k = gen_aws_key()
    content = "a = '%s'\n" % k
    blob = content.encode("utf-8")
    entry = fp_entry("aws-access-key-id", "cfg.py", blob, k, content.index(k))
    with tempfile.TemporaryDirectory() as d:
        root = make_repo(d)
        sh(["git", "checkout", "-q", "-b", "feat"], root)
        (root / "cfg.py").write_text(content)
        write_allowlist(root, [entry])
        sh(["git", "add", "cfg.py"], root)
        sh(["git", "commit", "-q", "--no-verify", "-m", "secret + self-allowlist"], root)
        proc = run_scanner(["--changed-against", "main"], root)
        assert proc.returncode != 0, \
            "a PR-head allowlist entry must not clear the PR's own secret"
    with tempfile.TemporaryDirectory() as d:
        # the ratified flow: the entry is already merged on the BASE —
        # then it clears the finding in a follow-up PR
        root = make_repo(d)
        write_allowlist(root, [entry])
        sh(["git", "commit", "-q", "--no-verify", "-m", "ratified allowlist"], root)
        sh(["git", "checkout", "-q", "-b", "feat"], root)
        (root / "cfg.py").write_text(content)
        sh(["git", "add", "cfg.py"], root)
        sh(["git", "commit", "-q", "--no-verify", "-m", "content"], root)
        proc = run_scanner(["--changed-against", "main"], root)
        assert proc.returncode == 0, \
            "a base-ratified entry must clear the finding: %s%s" \
            % (proc.stdout, proc.stderr)
    print("ok test_ci_does_not_trust_pr_head_allowlist")


def test_expired_base_entry_does_not_wedge_renewal():
    # CFAR F13: an expired entry in the BASE allowlist must not block the
    # very PR that renews it (permanent wedge); but a PR that inherits the
    # expired entry unfixed in its HEAD copy still blocks — expiry keeps
    # forcing renewal repo-wide, with the renewal PR as the escape hatch.
    k = gen_aws_key()
    expired = fp_entry("aws-access-key-id", "gone.py", b"old", k, 0,
                       reviewed_on=(utc_today() - datetime.timedelta(days=90)).isoformat(),
                       expires_on=(utc_today() - datetime.timedelta(days=1)).isoformat())
    with tempfile.TemporaryDirectory() as d:
        root = make_repo(d)
        write_allowlist(root, [expired])
        sh(["git", "commit", "-q", "--no-verify", "-m", "base with expired entry"], root)
        # ordinary PR inheriting the expired entry -> blocks (forcing function)
        sh(["git", "checkout", "-q", "-b", "ordinary"], root)
        (root / "notes.md").write_text("clean change\n")
        sh(["git", "add", "notes.md"], root)
        sh(["git", "commit", "-q", "--no-verify", "-m", "clean change"], root)
        proc = run_scanner(["--changed-against", "main"], root)
        assert proc.returncode != 0, \
            "a PR inheriting an expired head allowlist must block"
        # the renewal PR fixes the entry -> passes (no wedge)
        sh(["git", "checkout", "-q", "main"], root)
        sh(["git", "checkout", "-q", "-b", "renewal"], root)
        renewed = dict(expired,
                       reviewed_on=utc_today().isoformat(),
                       expires_on=(utc_today() + datetime.timedelta(days=30)).isoformat())
        write_allowlist(root, [renewed])
        sh(["git", "commit", "-q", "--no-verify", "-m", "renew allowlist"], root)
        proc = run_scanner(["--changed-against", "main"], root)
        assert proc.returncode == 0, \
            "the renewal PR must be able to pass: %s%s" \
            % (proc.stdout, proc.stderr)
    print("ok test_expired_base_entry_does_not_wedge_renewal")


def test_partial_clone_missing_blob_blocks_without_fetch():
    # CFAR F8: in a blob-filtered (promisor) clone, git lazily fetches
    # missing blobs over the network — the scanner must block on the missing
    # object instead (GIT_NO_LAZY_FETCH), or the no-network contract breaks.
    with tempfile.TemporaryDirectory() as d:
        root = make_repo(d)
        sh(["git", "config", "uploadpack.allowfilter", "true"], root)
        base = sh(["git", "rev-parse", "HEAD"], root).stdout.strip()
        (root / "f.txt").write_text("v1 middle version\n")
        sh(["git", "add", "f.txt"], root)
        sh(["git", "commit", "-q", "-m", "v1"], root)
        (root / "f.txt").write_text("v2 final version\n")
        sh(["git", "add", "f.txt"], root)
        sh(["git", "commit", "-q", "-m", "v2"], root)
        partial = pathlib.Path(d) / "partial"
        sh(["git", "clone", "-q", "--filter=blob:none",
            "file://" + str(root), str(partial)], d)
        # v1's blob is not in the partial clone (only v2 was checked out);
        # scanning the range must NOT fetch it — it must fail closed
        proc = run_scanner(["--changed-against", base], partial)
        assert proc.returncode != 0, \
            "missing promisor blob must block, not lazy-fetch over the network"
        out = (proc.stdout + proc.stderr).lower()
        assert "unreadable" in out or "block" in out
    print("ok test_partial_clone_missing_blob_blocks_without_fetch")


def test_allowlist_dates_compared_in_utc():
    # CFAR F6: the allowlist contract says dates are UTC; date.today() uses
    # the local timezone, so a valid UTC-dated entry could falsely block (or
    # an expired one falsely clear) near midnight. Pick a TZ on the far side
    # of UTC for the current UTC hour so local-date semantics would fail NOW.
    utc_today = datetime.datetime.now(datetime.timezone.utc).date()
    if datetime.datetime.now(datetime.timezone.utc).hour < 12:
        tz = "Etc/GMT+12"   # local = UTC-12 -> local date is yesterday
        reviewed, expires = utc_today, utc_today + datetime.timedelta(days=30)
    else:
        tz = "Etc/GMT-13"   # local = UTC+13 -> local date is tomorrow
        reviewed, expires = utc_today - datetime.timedelta(days=30), utc_today
    k = gen_aws_key()
    content = "a = '%s'\n" % k
    blob = content.encode("utf-8")
    with tempfile.TemporaryDirectory() as d:
        root = _staged_secret_repo(d, content)
        write_allowlist(root, [fp_entry(
            "aws-access-key-id", "cfg.py", blob, k, content.index(k),
            reviewed_on=reviewed.isoformat(), expires_on=expires.isoformat())])
        proc = run_scanner(["--staged"], root, env={"TZ": tz})
        assert proc.returncode == 0, \
            "a valid UTC-dated entry must validate in any local timezone:\n%s%s" \
            % (proc.stdout, proc.stderr)
    print("ok test_allowlist_dates_compared_in_utc")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
    print("\nall %d secret-scan tests passed" % len(fns))
