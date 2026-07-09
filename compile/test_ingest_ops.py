#!/usr/bin/env python3
"""Stdlib-assert tests for compile/ingest_ops.py (AC1-AC8 of the
per-ingestion-ops packet, docs/superpowers/specs/2026-07-03-per-ingestion-ops-packet.md).

Secret fixtures are composed at runtime so this file's own blob never
matches the pre-commit scanner's detectors.
"""
import hashlib
import io
import json
import os
import pathlib
import subprocess
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ingest_ops as ops  # noqa: E402
import ingest_server as srv  # noqa: E402

NOW = "2026-07-04T12:00:00+00:00"
OLD_REF = "raw/inbox/2026-07-01/alpha-topic/doc-abc.md"

# runtime-composed secret fixtures (never literal in this blob)
AWS_KEY = "AK" + "IA" + "ABCDEFGHIJKLMNOP"
SK_KEY = "sk-" + "proj-" + "a1b2c3d4e5f6a1b2c3d4e5f6"
PEM = "-----BEGIN " + "PRIVATE KEY-----"


def good_auth(**over):
    auth = {
        "df": "ingest-authorization",
        "operation": "replace",
        "slug": "alpha-topic",
        "source_ref": OLD_REF,
        "authority": "Michael Saucier / owner",
        "authorized_at": "2026-07-04T00:00:00Z",
        "expires_at": "2026-07-04T23:00:00Z",
        "reason": "test window",
        "engine_command": [],
        "engine_timeout_seconds": 30,
    }
    auth.update(over)
    return auth


def remove_auth(slug, **over):
    merged = dict(operation="remove", slug=slug, source_ref="")
    merged.update(over)
    return good_auth(**merged)


def write_auth(root, auth, raw=None):
    path = root / "compile" / "ingest-authorization.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(raw if raw is not None else json.dumps(auth))
    return path


def article(root, slug, body=None, fm_extra=""):
    wiki = root / "wiki"
    wiki.mkdir(parents=True, exist_ok=True)
    text = (
        "---\n"
        "entity: %s\n"
        "tier: investigation\n"
        "%s"
        "raw_documents:\n"
        "  - raw/inbox/2026-07-01/%s/doc-abc.md\n"
        "sources:\n"
        "  - raw/inbox/2026-07-01/%s/doc-abc.md\n"
        "---\n\n" % (slug.replace("-", " ").title(), fm_extra, slug, slug)
    ) + (body if body is not None else "# %s\n\nBody text.\n" % slug)
    (wiki / ("%s.md" % slug)).write_text(text)
    raw_dir = root / "raw" / "inbox" / "2026-07-01" / slug
    raw_dir.mkdir(parents=True, exist_ok=True)
    (raw_dir / "doc-abc.md").write_text("# original raw\n")
    return wiki / ("%s.md" % slug)


def fresh_root():
    d = tempfile.mkdtemp()
    root = pathlib.Path(d)
    (root / "compile").mkdir(parents=True, exist_ok=True)
    (root / "PROVENANCE.md").write_text("# Provenance\n")
    return root


def tree_snapshot(root):
    out = {}
    for p in sorted(root.rglob("*")):
        if p.is_file():
            out[str(p.relative_to(root))] = p.read_bytes()
    return out


def refused(fn, *a, **kw):
    try:
        fn(*a, **kw)
    except ops.OpRefused as exc:
        return str(exc)
    raise AssertionError("expected OpRefused from %s" % getattr(fn, "__name__", fn))


def do_replace(root, **over):
    kw = dict(slug="alpha-topic", source_ref=OLD_REF,
              data=b"# replacement raw\n", filename="replacement.md",
              note="", now=NOW)
    kw.update(over)
    return ops.replace_source(root, **kw)


# --------------------------------------------------------------------- AC1

def test_ac1_authorization_denies_entire_domain():
    root = fresh_root()
    path = root / "compile" / "ingest-authorization.json"
    req = dict(operation="replace", slug="alpha-topic", source_ref=OLD_REF)

    # missing file
    refused(ops.load_authorization, path, NOW, **req)
    # unreadable / not json / non-object
    for raw in ("{nope", "[]", '"str"'):
        write_auth(root, None, raw=raw)
        refused(ops.load_authorization, path, NOW, **req)
    # duplicate key ISOLATED: the document is fully valid under plain
    # json.loads (last value wins and matches the request) — ONLY the
    # object_pairs_hook duplicate-key law can refuse it
    valid = json.dumps(good_auth())
    dup = valid.replace('"reason": "test window"',
                        '"reason": "x", "reason": "test window"', 1)
    assert json.loads(dup) == good_auth(), "fixture must be valid but for the dup"
    write_auth(root, None, raw=dup)
    refused(ops.load_authorization, path, NOW, **req)

    bad_cases = [
        good_auth(df="deploy-authorization"),
        good_auth(df="ingest-authorization-consumed"),           # consumed = spent
        dict(good_auth(), extra_key=1),                          # unknown key
        {k: v for k, v in good_auth().items() if k != "reason"},  # missing key
        good_auth(operation="destroy"),                           # unknown op
        good_auth(operation="remove"),                            # op mismatch
        good_auth(slug="other-topic"),                            # slug mismatch
        good_auth(source_ref="raw/other.md"),                     # ref mismatch
        good_auth(operation=True),
        good_auth(slug=""),
        good_auth(authority=""),
        good_auth(reason=""),
        good_auth(authorized_at="not-a-date"),
        good_auth(expires_at="not-a-date"),
        good_auth(authorized_at="2026-07-05T00:00:00Z"),          # future window
        good_auth(expires_at="2026-07-01T00:00:00Z"),             # expired
        good_auth(expires_at="2026-07-06T00:00:00Z"),             # window > 24h
        good_auth(engine_command="claude -p"),                    # not a list
        good_auth(engine_command=["claude", 3]),                  # non-string elem
        good_auth(engine_command=["claude", ""]),                 # empty-string elem
        good_auth(engine_timeout_seconds=True),                   # bool
        good_auth(engine_timeout_seconds="30"),
        good_auth(engine_timeout_seconds=0),
        good_auth(engine_timeout_seconds=3601),
    ]
    for auth in bad_cases:
        write_auth(root, auth)
        refused(ops.load_authorization, path, NOW, **req)
    # remove requests must carry source_ref "" and match a remove artifact
    write_auth(root, good_auth())  # a replace artifact
    refused(ops.load_authorization, path, NOW,
            operation="remove", slug="alpha-topic", source_ref="")
    write_auth(root, remove_auth("alpha-topic", source_ref="raw/x.md"))
    refused(ops.load_authorization, path, NOW,
            operation="remove", slug="alpha-topic", source_ref="")
    print("ok test_ac1_authorization_denies_entire_domain")


def test_ac1_authorization_single_proven_grant():
    root = fresh_root()
    path = write_auth(root, good_auth())
    auth = ops.load_authorization(path, NOW, operation="replace",
                                  slug="alpha-topic", source_ref=OLD_REF)
    assert auth["authority"] == "Michael Saucier / owner"
    assert auth["engine_command"] == []
    write_auth(root, remove_auth("alpha-topic"))
    auth = ops.load_authorization(path, NOW, operation="remove",
                                  slug="alpha-topic", source_ref="")
    assert auth["engine_timeout_seconds"] == 30
    # boundary: timeout 1 and 3600 both valid; 24h window exactly valid
    for t in (1, 3600):
        write_auth(root, good_auth(engine_timeout_seconds=t))
        assert ops.load_authorization(path, NOW, operation="replace",
                                      slug="alpha-topic", source_ref=OLD_REF)
    write_auth(root, good_auth(expires_at="2026-07-05T00:00:00Z"))  # == 24h
    assert ops.load_authorization(path, NOW, operation="replace",
                                  slug="alpha-topic", source_ref=OLD_REF)
    print("ok test_ac1_authorization_single_proven_grant")


def test_ac1_authorization_single_use_consumed():
    root = fresh_root()
    article(root, "alpha-topic")
    auth_path = write_auth(root, good_auth())
    original_digest = hashlib.sha256(auth_path.read_bytes()).hexdigest()
    result = do_replace(root)
    # consumed tombstone in place of the artifact
    spent = json.loads(auth_path.read_text())
    assert spent["df"] == "ingest-authorization-consumed"
    assert spent["authorization_sha256"] == original_digest
    assert result["authorization_sha256"] == original_digest
    # second use refuses (df gate) and writes nothing new
    before = tree_snapshot(root)
    refused(do_replace, root)
    assert tree_snapshot(root) == before
    print("ok test_ac1_authorization_single_use_consumed")


# --------------------------------------------------------------------- AC2

def test_ac2_quarantine_payload_input_classes():
    # oversized
    refused(ops.quarantine_payload, b"x" * (ops.MAX_QUARANTINE_BYTES + 1))
    # binary NUL
    refused(ops.quarantine_payload, b"clean\x00clean")
    # non-UTF-8 binary WITHOUT a NUL (image-shaped bytes, Latin-1) refuses —
    # unscannable as text, must not be decoded-with-replacement and accepted
    for binary in (b"\xff\xd8\xff\xe0 jpeg-ish", b"caf\xe9 latin-1",
                   b"\xc3\x28 bad utf8"):
        refused(ops.quarantine_payload, binary)
    # text with a finding per representative rule family
    for secret in (AWS_KEY, SK_KEY, PEM):
        refused(ops.quarantine_payload, ("doc body %s tail" % secret).encode("utf-8"))
    # clean text passes
    assert ops.quarantine_payload(b"# clean document\n\nplain prose.\n") is None
    print("ok test_ac2_quarantine_payload_input_classes")


def test_ac2_quarantine_every_persisted_field():
    fields = {"slug": "a-topic", "source_ref": "raw/x.md", "note": "n",
              "filename": "f.md", "authorized_by": "owner", "reason": "r"}
    assert ops.quarantine_fields(fields) is None
    for key in fields:
        poisoned = dict(fields)
        poisoned[key] = "%s %s" % (poisoned[key], AWS_KEY)
        msg = refused(ops.quarantine_fields, poisoned)
        assert AWS_KEY not in msg, "refusal must not echo the secret"
    print("ok test_ac2_quarantine_every_persisted_field")


def test_ac2_refusal_writes_nothing_and_redacts():
    root = fresh_root()
    article(root, "alpha-topic")
    write_auth(root, good_auth())
    before = tree_snapshot(root)
    msg = refused(do_replace, root,
                  data=("payload %s" % SK_KEY).encode("utf-8"))
    assert SK_KEY not in msg
    assert tree_snapshot(root) == before, \
        "refusal must write nothing (incl. the un-consumed artifact)"
    print("ok test_ac2_refusal_writes_nothing_and_redacts")


# --------------------------------------------------------------------- AC3

def _fm_list(fm, key):
    import re
    m = re.search(r"^%s:\n((?:[ \t]+-[^\n]*\n)*)" % re.escape(key), fm, re.M)
    return m.group(1) if m else ""


def test_ac3_replace_deterministic_swap():
    root = fresh_root()
    path = article(root, "alpha-topic")
    write_auth(root, good_auth())
    body_before = path.read_text().split("---\n", 2)[2]
    result = do_replace(root, note="swap")
    text = path.read_text()
    fm, body = text.split("---\n", 2)[1], text.split("---\n", 2)[2]
    assert body == body_before, "Layer 1 must not touch body bytes"
    # old ref moved OUT of live lists into superseded_* lists
    assert OLD_REF in _fm_list(fm, "superseded_sources")
    assert OLD_REF in _fm_list(fm, "superseded_raw_documents")
    assert OLD_REF not in _fm_list(fm, "sources")
    assert OLD_REF not in _fm_list(fm, "raw_documents")
    # replacement present in live lists, raw retained on disk, new raw saved
    new_ref = result["replacement"]
    assert new_ref in _fm_list(fm, "sources")
    assert new_ref in _fm_list(fm, "raw_documents")
    assert (root / OLD_REF).exists(), "superseded raw file is never deleted"
    assert (root / new_ref).exists()
    assert "stale_since:" in fm, "engine disabled -> honest-stale marker"
    assert result["engine"] == "disabled"
    assert result["result"] == "stale"
    prov = (root / "PROVENANCE.md").read_text()
    assert OLD_REF in prov and new_ref in prov
    print("ok test_ac3_replace_deterministic_swap")


def test_ac3_replace_supersession_not_load_bearing():
    """The LIVE parser (ingest_server fm_list) must not see superseded refs."""
    root = fresh_root()
    path = article(root, "alpha-topic")
    write_auth(root, good_auth())
    do_replace(root)
    fm, _, _ = srv.split_fm(path.read_text())
    assert OLD_REF not in srv.fm_list(fm, "sources")
    assert OLD_REF not in srv.fm_list(fm, "raw_documents")
    assert OLD_REF in srv.fm_list(fm, "superseded_sources")
    print("ok test_ac3_replace_supersession_not_load_bearing")


def test_ac3_replace_refusals_write_nothing():
    root = fresh_root()
    article(root, "alpha-topic")
    article(root, "beta-topic")
    # make one raw shared by two articles
    beta = root / "wiki" / "beta-topic.md"
    beta.write_text(beta.read_text().replace(
        "raw/inbox/2026-07-01/beta-topic/doc-abc.md", OLD_REF))
    article(root, "gone-topic",
            fm_extra='retired_on: "2026-07-01"\nretired_reason: "old"\n')
    cases = [
        dict(slug="unknown-topic"),
        dict(slug="alpha-topic", source_ref="raw/not-in-article.md"),
        dict(slug="alpha-topic", source_ref="https://example.com/x"),  # URL ref
        dict(slug="alpha-topic"),                                      # shared ref
        dict(slug="gone-topic", source_ref="raw/inbox/2026-07-01/gone-topic/doc-abc.md"),
        dict(slug="../escape"),
    ]
    for case in cases:
        write_auth(root, good_auth(slug=case["slug"],
                                   source_ref=case.get("source_ref", OLD_REF)))
        before = tree_snapshot(root)
        refused(do_replace, root, **case)
        assert tree_snapshot(root) == before, case
    # corrupt edge state refuses Replace too, not only Remove (rebuild-r4 B1)
    write_auth(root, good_auth())
    (root / "compile" / "edge-states.json").write_text("{nope")
    before = tree_snapshot(root)
    refused(do_replace, root)
    assert tree_snapshot(root) == before
    print("ok test_ac3_replace_refusals_write_nothing")


def test_ac3_write_order_and_fault_injection():
    """Executable form of the §2.8 ordering law: consume-auth FIRST, ledger
    LAST, and an interruption leaves exactly the enumerated atomic prefix."""
    # 1) record the durable-write order of a successful replace
    root = fresh_root()
    article(root, "alpha-topic")
    write_auth(root, good_auth())
    order = []
    real_bytes, real_append = ops._atomic_write_bytes, ops.append_ledger

    def spy_bytes(path, data):
        order.append(pathlib.Path(path).name)
        return real_bytes(path, data)

    def spy_append(path, row):
        order.append(pathlib.Path(path).name)
        return real_append(path, row)

    try:
        ops._atomic_write_bytes = spy_bytes
        ops.append_ledger = spy_append
        do_replace(root)
    finally:
        ops._atomic_write_bytes, ops.append_ledger = real_bytes, real_append
    assert order[0] == "ingest-authorization.json", \
        "consume-auth must be durable write #0: %r" % order
    assert order[-1] == "ingest-ledger.jsonl", "ledger append must be last: %r" % order
    assert order.index("replacement-%s.md" % hashlib.sha256(
        b"# replacement raw\n").hexdigest()[:12]) == 1, \
        "raw upload lands right after consumption: %r" % order

    # 2) fault-inject at the article write: consumed + raw exist, article
    # bytes unchanged, no PROVENANCE line, no ledger row
    root = fresh_root()
    path = article(root, "alpha-topic")
    write_auth(root, good_auth())
    article_before = path.read_bytes()
    prov_before = (root / "PROVENANCE.md").read_bytes()

    def failing_bytes(target, data):
        if pathlib.Path(target).name == "alpha-topic.md":
            raise OSError("injected fault at the article write")
        return real_bytes(target, data)

    try:
        ops._atomic_write_bytes = failing_bytes
        try:
            do_replace(root)
        except OSError:
            pass
        else:
            raise AssertionError("injected fault must propagate")
    finally:
        ops._atomic_write_bytes = real_bytes
    spent = json.loads((root / "compile" / "ingest-authorization.json").read_text())
    assert spent["df"] == "ingest-authorization-consumed", \
        "prefix state: authorization burned"
    assert list((root / "raw" / "inbox").rglob("replacement-*.md")), \
        "prefix state: raw saved"
    assert path.read_bytes() == article_before, "article untouched by the fault"
    assert (root / "PROVENANCE.md").read_bytes() == prov_before
    assert not (root / "compile" / "ingest-ledger.jsonl").exists(), \
        "no ledger row for an interrupted operation"
    print("ok test_ac3_write_order_and_fault_injection")


# --------------------------------------------------------------------- AC4

def py_engine(code):
    return [sys.executable, "-c", code]

GOOD_BODY = "# Alpha\\n\\nRe-derived body.\\n"


def _engine_replace(root, engine_command, timeout=30):
    write_auth(root, good_auth(engine_command=engine_command,
                               engine_timeout_seconds=timeout))
    return do_replace(root)


def _post_swap_baseline():
    """The deterministic step-5 state: same fixture, engine disabled."""
    root = fresh_root()
    path = article(root, "alpha-topic")
    write_auth(root, good_auth())
    do_replace(root)
    return path.read_bytes()


def test_ac4_engine_failure_domain_leaves_honest_stale():
    baseline = _post_swap_baseline()
    failure_engines = [
        (py_engine("import sys; sys.exit(3)"), 30),                    # nonzero exit
        (py_engine("import time; time.sleep(30)"), 1),                 # timeout
        (py_engine("print('')"), 30),                                  # empty stdout
        (py_engine("print('---\\nentity: X\\n---\\n\\n# grab')"), 30),  # fm grab
        (py_engine("print('%s<div>raw html</div>')" % GOOD_BODY), 30),
        (py_engine("print('%s k=' + '%s')" % (GOOD_BODY, "AK" + "IA" + "ABCDEFGHIJKLMNOP")), 30),
    ]
    for engine, timeout in failure_engines:
        root = fresh_root()
        path = article(root, "alpha-topic")
        result = _engine_replace(root, engine, timeout)
        assert result["engine"] == "failed", engine
        assert result["result"] == "stale"
        assert path.read_bytes() == baseline, \
            "failed engine leaves the article BYTE-IDENTICAL to the " \
            "deterministic post-swap state: %r" % engine
    print("ok test_ac4_engine_failure_domain_leaves_honest_stale")


def test_ac4_engine_success_atomic_swap():
    baseline = _post_swap_baseline().decode("utf-8")
    baseline_fm = baseline.split("---\n", 2)[1]
    expected_fm = "".join(line for line in baseline_fm.splitlines(keepends=True)
                          if not line.startswith("stale_since:"))
    root = fresh_root()
    path = article(root, "alpha-topic")
    result = _engine_replace(root, py_engine("print('%s')" % GOOD_BODY))
    assert result["engine"] == "ok"
    assert result["result"] == "completed"
    text = path.read_text()
    fm, body = text.split("---\n", 2)[1], text.split("---\n", 2)[2]
    assert fm == expected_fm, \
        "success frontmatter == deterministic post-swap fm minus stale_since"
    assert "Re-derived body." in body
    print("ok test_ac4_engine_success_atomic_swap")


def test_ac4_engine_cannot_touch_frontmatter():
    """Engine output is BODY only; supersession survives engine success."""
    root = fresh_root()
    path = article(root, "alpha-topic")
    result = _engine_replace(root, py_engine("print('%s')" % GOOD_BODY))
    fm, _, _ = srv.split_fm(path.read_text())
    assert OLD_REF in srv.fm_list(fm, "superseded_sources")
    assert OLD_REF not in srv.fm_list(fm, "sources")
    assert result["replacement"] in srv.fm_list(fm, "sources")
    print("ok test_ac4_engine_cannot_touch_frontmatter")


def test_ac4_engine_argv_never_shell():
    root = fresh_root()
    article(root, "alpha-topic")
    calls = []
    real_popen = ops.subprocess.Popen

    def spy_popen(args, **kwargs):
        calls.append((args, kwargs))
        return real_popen(args, **kwargs)

    old = ops.subprocess.Popen
    try:
        ops.subprocess.Popen = spy_popen
        _engine_replace(root, py_engine("print('%s')" % GOOD_BODY))
    finally:
        ops.subprocess.Popen = old
    engine_calls = [c for c in calls if c[0] and c[0][0] == sys.executable]
    assert engine_calls, "engine must run via subprocess"
    args, kwargs = engine_calls[0]
    assert isinstance(args, list), "argv vector, never a shell string"
    assert not kwargs.get("shell"), "never shell=True"
    print("ok test_ac4_engine_argv_never_shell")


# --------------------------------------------------------------------- AC5

LINK_FORMS = {
    "wiki": "see [[%s]] for detail",
    "md": "see [details](%s.html) for detail",
    "href": 'see <a href="%s.html">details</a> for detail',
}


def linked_article(root, slug, target, form):
    """One article, EXACTLY ONE link form — a single-form implementation
    cannot satisfy all three fixtures."""
    wiki = root / "wiki"
    wiki.mkdir(parents=True, exist_ok=True)
    (wiki / ("%s.md" % slug)).write_text(
        "---\nentity: %s\ntier: investigation\n---\n\n# %s\n\n%s\n"
        % (slug, slug, LINK_FORMS[form] % target))


def test_ac5_remove_tombstone_and_edge_enumeration():
    root = fresh_root()
    article(root, "doomed-topic")
    linked_article(root, "linker-wiki", "doomed-topic", "wiki")
    linked_article(root, "linker-md", "doomed-topic", "md")
    linked_article(root, "linker-href", "doomed-topic", "href")
    write_auth(root, remove_auth("doomed-topic"))
    result = ops.remove_topic(root, slug="doomed-topic", now=NOW)
    path = root / "wiki" / "doomed-topic.md"
    assert path.exists(), "tombstone, never a delete"
    text = path.read_text()
    assert 'retired_on:' in text and 'retired_reason:' in text
    assert (root / "raw" / "inbox" / "2026-07-01" / "doomed-topic" / "doc-abc.md").exists()
    states = json.loads((root / "compile" / "edge-states.json").read_text())
    assert set(states) == {"linker-wiki->doomed-topic",
                           "linker-md->doomed-topic",
                           "linker-href->doomed-topic"}, \
        "each of the three link forms discovered independently"
    for entry in states.values():
        assert entry["state"] == "dangling-pending"
        assert entry["queued"] is True
        assert entry["enqueued_at"]
        assert set(entry) == {"state", "since", "reason", "queued", "enqueued_at"}
    assert sorted(result["affected_edges"]) == \
        ["linker-href", "linker-md", "linker-wiki"]
    assert "doomed-topic" in (root / "PROVENANCE.md").read_text()
    print("ok test_ac5_remove_tombstone_and_edge_enumeration")


def test_ac5_closure_zero_unqueued_pending():
    root = fresh_root()
    article(root, "doomed-topic")
    linked_article(root, "linker-wiki", "doomed-topic", "wiki")
    write_auth(root, remove_auth("doomed-topic"))
    ops.remove_topic(root, slug="doomed-topic", now=NOW)
    states = ops.load_edge_states(root / "compile" / "edge-states.json")
    unqueued_pending = [k for k, v in states.items()
                        if v["state"] == "dangling-pending" and v["queued"] is False]
    assert unqueued_pending == [], "closure: every pending edge is queued"
    print("ok test_ac5_closure_zero_unqueued_pending")


def test_ac5_corrupt_edge_states_refuses():
    # NOTE the duplicate-key fixture is ISOLATED: under plain json.loads the
    # last "state" wins and the entry is fully valid — only the
    # object_pairs_hook law refuses it. Every other fixture carries exactly
    # one fault (timestamps are valid ISO so the fault is unambiguous).
    corrupt = [
        "{nope",
        "[]",
        '{"a->b": {"state": "dangling-pending", "since": "%s", "reason": "r", "queued": true, "enqueued_at": "%s", "state": "valid"}}' % (NOW, NOW),
        '{"a->b": {"state": "wat", "since": "%s", "reason": "r", "queued": false, "enqueued_at": null}}' % NOW,
        '{"a->b": {"state": "valid", "since": "%s", "reason": "r", "queued": true, "enqueued_at": null}}' % NOW,
        '{"a->b": {"state": "valid", "since": "%s", "reason": "r", "queued": false, "enqueued_at": null, "extra": 1}}' % NOW,
        '{"not a slug key": {"state": "valid", "since": "%s", "reason": "r", "queued": false, "enqueued_at": null}}' % NOW,
        '{"a->b": {"state": "valid", "since": "not-a-date", "reason": "r", "queued": false, "enqueued_at": null}}',
        '{"a->b": {"state": "dangling-pending", "since": "%s", "reason": "r", "queued": true, "enqueued_at": "not-a-date"}}' % NOW,
    ]
    dup_fixture = json.loads(corrupt[2])
    assert dup_fixture["a->b"]["state"] == "valid", \
        "dup-key fixture must be valid under plain json.loads"
    for raw in corrupt:
        root = fresh_root()
        article(root, "doomed-topic")
        linked_article(root, "linker-wiki", "doomed-topic", "wiki")
        write_auth(root, remove_auth("doomed-topic"))
        (root / "compile" / "edge-states.json").write_text(raw)
        before = tree_snapshot(root)
        refused(ops.remove_topic, root, slug="doomed-topic", now=NOW)
        assert tree_snapshot(root) == before, \
            "corrupt state must refuse before any write (incl. consumption)"
    print("ok test_ac5_corrupt_edge_states_refuses")


def test_ac5_remove_refusals_write_nothing():
    root = fresh_root()
    article(root, "alpha-topic")
    article(root, "gone-topic",
            fm_extra='retired_on: "2026-07-01"\nretired_reason: "old"\n')
    for slug in ("unknown-topic", "gone-topic", "index", "../escape"):
        write_auth(root, remove_auth(slug))
        before = tree_snapshot(root)
        refused(ops.remove_topic, root, slug=slug, now=NOW)
        assert tree_snapshot(root) == before, slug
    print("ok test_ac5_remove_refusals_write_nothing")


# --------------------------------------------------------------------- AC6

def test_ac6_render_state_domain_all_link_forms():
    meta = {"alive": {}, "gone": {"retired_on": "2026-07-01"}}
    edges = {
        "src->alive": {"state": "valid", "since": "x", "reason": "r",
                       "queued": False, "enqueued_at": None},
        "src->gone": {"state": "dangling-pending", "since": "x", "reason": "r",
                      "queued": True, "enqueued_at": "x"},
        "src->cut": {"state": "cleanly-removed", "since": "x", "reason": "r",
                     "queued": False, "enqueued_at": None},
    }
    # the pure decision function is TOTAL: live only on the proven branch
    assert ops.link_state("src", "alive", meta, edges) == "live"
    assert ops.link_state("src", "gone", meta, edges) == "pending"
    assert ops.link_state("src", "cut", meta, edges) == "plain"
    assert ops.link_state("src", "missing", meta, edges) == "tbd"
    # no entry + not retired -> live; no entry + retired -> pending (fail closed)
    assert ops.link_state("other", "alive", meta, edges) == "live"
    assert ops.link_state("other", "gone", meta, edges) == "pending"
    # UNKNOWN/future state value -> non-live, never a KeyError
    edges["src->alive"]["state"] = "future-state"
    assert ops.link_state("src", "alive", meta, edges) == "pending"
    edges["src->alive"]["state"] = ""
    assert ops.link_state("src", "alive", meta, edges) == "pending"
    print("ok test_ac6_render_state_domain_all_link_forms")


def test_ac6_href_canonicalization_domain():
    meta = {"alpha-topic": {}, "gone": {"retired_on": "2026-07-01"}}
    repo_slugs = {"hive"}

    def target(href):
        return ops.canonical_article_target(href, meta=meta, repo_slugs=repo_slugs)

    # spellings that must all reach the gate as article "alpha-topic"
    for href in ("alpha-topic.html", "./alpha-topic.html", "/alpha-topic.html",
                 "../alpha-topic.html", "x/../alpha-topic.html",
                 "alpha-topic.html#frag", "alpha-topic.html?q=1",
                 "alpha%2Dtopic.html"):
        kind, slug = target(href)
        assert (kind, slug) == ("article", "alpha-topic"), href
    assert target("index.html")[0] == "article"
    # case variant is NOT the article (case-sensitive) -> unknown, non-live
    assert target("Alpha-Topic.html")[0] == "unknown"
    assert target("nonexistent-page.html")[0] == "unknown"
    # builder-emitted pages stay live
    for href in ("repos.html", "sources.html", "ingest.html",
                 "civilization-arc.html", "civilization_arc.html",
                 "repo-hive.html"):
        assert target(href)[0] == "page", href
    assert target("repo-unknown.html")[0] == "unknown"
    # source-viewer allowlist: exactly source/<16 hex>.html
    assert target("source/29d1acbe353cb797.html")[0] == "page"
    assert target("source/abc123.html")[0] == "unknown"
    assert target("docs/deep/x.html")[0] == "unknown"
    # non-internal forms keep today's scheme-only handling
    for href in ("https://example.com/x.html", "mailto:x@y.z", "#anchor", "",
                 "style.css", "img/logo.png"):
        assert target(href)[0] == "external", href
    print("ok test_ac6_href_canonicalization_domain")


def test_ac6_rendered_output_gates_all_link_forms():
    """Executable render proof: to_html() output over real markdown carrying
    all three link forms, against a retired target, a valid target, a
    cleanly-removed edge, and a dot-segment bypass spelling."""
    import build_site as site
    old = (site.META, site.SLUGS, site.EDGE_STATES, site.REPOS)
    try:
        site.META = {
            "src": {"slug": "src", "title": "Src", "tier": "concept",
                    "retired_on": ""},
            "alive": {"slug": "alive", "title": "Alive", "tier": "concept",
                      "retired_on": ""},
            "gone": {"slug": "gone", "title": "Gone", "tier": "concept",
                     "retired_on": "2026-07-01"},
            "cut": {"slug": "cut", "title": "Cut", "tier": "concept",
                    "retired_on": ""},
        }
        site.EDGE_STATES = {
            "src->cut": {"state": "cleanly-removed", "since": "x",
                         "reason": "r", "queued": False, "enqueued_at": None},
        }
        site.SLUGS = set(site.META) | {"index"}
        site.REPOS = []
        body = (
            "wikilink live [[alive]] and retired [[gone]]\n\n"
            "markdown live [a](alive.html) and retired [g](gone.html) "
            "and dotted [d](../gone.html)\n\n"
            'raw live <a href="alive.html">A</a> and retired '
            '<a href="gone.html">G</a>\n\n'
            "cut edge [[cut]]\n"
        )
        html_out, _ = site.to_html(body, source_slug="src")
    finally:
        site.META, site.SLUGS, site.EDGE_STATES, site.REPOS = old
    # live target renders live anchors (wikilink + markdown + raw)
    assert '<a class="wl" href="alive.html">Alive</a>' in html_out
    assert 'href="alive.html">a</a>' in html_out
    assert 'href="alive.html">A</a>' in html_out
    # retired target NEVER renders a live href, in ANY form
    assert 'href="gone.html"' not in html_out
    assert 'href="../gone.html"' not in html_out
    assert html_out.count("wl-pending") >= 4, html_out
    # cleanly-removed renders plain text (no anchor, no pending marker)
    assert ">Cut</a>" not in html_out
    print("ok test_ac6_rendered_output_gates_all_link_forms")


def test_ac6_corrupt_edge_states_fails_build():
    # strict loader refuses every corrupt form (build_site delegates to it)
    for raw in ("{nope", "[]", '{"a->b": {"state": "valid"}}',
                '{"a->b": 3}'):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "edge-states.json"
            p.write_text(raw)
            try:
                ops.load_edge_states(p)
            except ops.OpRefused:
                continue
            raise AssertionError("corrupt edge-states must refuse: %r" % raw)
    # missing file is the one valid empty form
    with tempfile.TemporaryDirectory() as d:
        assert ops.load_edge_states(pathlib.Path(d) / "edge-states.json") == {}
    # EXECUTABLE build-failure proof: running the real builder against a
    # corrupt edge-states file must exit non-zero before rendering anything
    with tempfile.TemporaryDirectory() as d:
        corrupt = pathlib.Path(d) / "edge-states.json"
        corrupt.write_text("{nope")
        env = dict(os.environ)
        env["CIVWIKI_EDGE_STATES"] = str(corrupt)
        proc = subprocess.run(
            [sys.executable, str(pathlib.Path(__file__).resolve().parent / "build_site.py")],
            capture_output=True, text=True, env=env, timeout=120)
        assert proc.returncode != 0, "corrupt edge-states must FAIL the build"
        assert "edge-states" in (proc.stderr + proc.stdout), \
            "failure must name the corrupt surface"
    print("ok test_ac6_corrupt_edge_states_fails_build")


# --------------------------------------------------------------------- AC7

def test_ac7_ledger_strict_jsonl_preflight_first_append_last():
    root = fresh_root()
    ledger = root / "compile" / "ingest-ledger.jsonl"

    # absent file = valid empty; preflight passes
    assert ops.ledger_preflight(ledger) == []

    # valid rows round-trip
    row = {"ts": NOW, "operation": "add", "slug": "alpha-topic",
           "sources": ["raw/x.md"], "created": False, "rebuild": "ok"}
    ops.append_ledger(ledger, row)
    assert ops.ledger_preflight(ledger) == [row]

    # exact per-op shapes: unknown operation, missing key, extra key, bad enum
    bad_rows = [
        dict(row, operation="destroy"),
        {k: v for k, v in row.items() if k != "rebuild"},
        dict(row, extra=1),
        dict(row, rebuild="maybe"),
        dict(row, ts="not-a-date"),
        dict(row, ts="2026-07-04T12:00:00"),  # no timezone -> not UTC-anchored
    ]
    for bad in bad_rows:
        try:
            ops.append_ledger(ledger, bad)
        except ops.OpRefused:
            continue
        raise AssertionError("bad ledger row must refuse: %r" % bad)

    digest = "0" * 64
    ops.append_ledger(ledger, {
        "ts": NOW, "operation": "replace", "slug": "alpha-topic",
        "superseded": "raw/a.md", "replacement": "raw/b.md",
        "authorized_by": "owner", "authorization_sha256": digest,
        "engine": "disabled", "result": "stale", "rebuild": "failed"})
    ops.append_ledger(ledger, {
        "ts": NOW, "operation": "remove", "slug": "alpha-topic",
        "reason": "r", "authorized_by": "owner",
        "authorization_sha256": digest, "affected_edges": ["x"],
        "repaired_edges": [], "result": "completed", "rebuild": "ok"})

    # duplicate-key line ISOLATED: valid add row under plain json.loads
    # (last "rebuild" wins) — only the object_pairs_hook law refuses it
    good_line = json.dumps(row, sort_keys=True)
    dup_line = good_line.replace('"rebuild": "ok"',
                                 '"rebuild": "failed", "rebuild": "ok"', 1)
    assert json.loads(dup_line) == row, "fixture must be valid but for the dup"
    ledger2 = root / "compile" / "dup-ledger.jsonl"
    ledger2.write_text(dup_line + "\n")
    refused(ops.ledger_preflight, ledger2)

    # corrupt line -> preflight refuses -> operation refuses, nothing written
    with ledger.open("a") as f:
        f.write("{corrupt\n")
    refused(ops.ledger_preflight, ledger)
    root2 = fresh_root()
    article(root2, "alpha-topic")
    write_auth(root2, good_auth())
    (root2 / "compile" / "ingest-ledger.jsonl").write_text("{corrupt\n")
    before = tree_snapshot(root2)
    refused(do_replace, root2)
    assert tree_snapshot(root2) == before
    print("ok test_ac7_ledger_strict_jsonl_preflight_first_append_last")


def test_ac7_operations_append_row_last():
    root = fresh_root()
    article(root, "alpha-topic")
    auth_path = write_auth(root, good_auth())
    digest = hashlib.sha256(auth_path.read_bytes()).hexdigest()
    do_replace(root)
    rows = ops.ledger_preflight(root / "compile" / "ingest-ledger.jsonl")
    assert len(rows) == 1
    assert rows[0]["operation"] == "replace"
    assert rows[0]["engine"] == "disabled"
    assert rows[0]["result"] == "stale"
    assert rows[0]["authorization_sha256"] == digest
    assert rows[0]["rebuild"] in ("ok", "failed")
    write_auth(root, remove_auth("alpha-topic"))
    ops.remove_topic(root, slug="alpha-topic", now=NOW)
    rows = ops.ledger_preflight(root / "compile" / "ingest-ledger.jsonl")
    assert [r["operation"] for r in rows] == ["replace", "remove"]
    print("ok test_ac7_operations_append_row_last")


# --------------------------------------------------------------------- AC8

def make_handler(path, body=b"", content_type="application/x-www-form-urlencoded",
                 host="127.0.0.1:8787", client="127.0.0.1", origin=None,
                 fetch_site=None, token=None):
    handler = type("FakeHandler", (), {})()
    handler.path = path
    handler.headers = {
        "Host": host,
        "Origin": origin if origin is not None else "http://%s" % host,
        "Sec-Fetch-Site": fetch_site if fetch_site is not None else "same-origin",
        "Content-Type": content_type,
        "Content-Length": str(len(body)),
    }
    if token is not None:
        handler.headers[srv.AUTHORING_TOKEN_HEADER] = token
    handler.client_address = (client, 12345)
    handler.server = type("FakeServer", (), {"server_port": 8787})()
    handler.rfile = io.BytesIO(body)
    handler.wfile = io.BytesIO()
    handler.status = None
    handler.send_response = lambda status: setattr(handler, "status", status)
    handler.send_header = lambda _n, _v: None
    handler.end_headers = lambda: None
    handler.require_allowed_host = lambda: srv.IngestHandler.require_allowed_host(handler)
    handler.require_authoring = lambda: srv.IngestHandler.require_authoring(handler)
    handler.handle_replace = lambda: srv.IngestHandler.handle_replace(handler)
    handler.handle_remove = lambda: srv.IngestHandler.handle_remove(handler)
    handler.handle_ingest = lambda: srv.IngestHandler.handle_ingest(handler)
    return handler


class _FakeProc:
    pid = 1
    returncode = 0

    def communicate(self, *a, **k):
        return "refresh ok", ""


def _server_root(d):
    root = pathlib.Path(d)
    (root / "compile").mkdir(exist_ok=True)
    wiki = root / "wiki"
    wiki.mkdir(exist_ok=True)
    (wiki / "example.md").write_text(
        "---\nentity: Example\ntier: investigation\n---\n\n# Example\n")
    return root


def test_ac8_endpoint_authoring_parity():
    """The full authoring matrix, ROW-FOR-ROW identical across /api/ingest,
    /api/replace, and /api/remove: bad Host 421; remote-no-token 403;
    remote-wrong-token 401 (token configured); loopback cross-origin 403;
    loopback same-origin passes authoring; remote correct-token passes
    authoring. 'Passes authoring' for replace/remove = reaches the
    authorization gate (403 naming the artifact), for ingest = 200."""
    with tempfile.TemporaryDirectory() as d:
        root = _server_root(d)
        old = (srv.ROOT, srv.WIKI, srv.RAW_INBOX, srv.MANIFEST, srv.LOCK_PATH,
               srv.subprocess.Popen)
        old_token = os.environ.pop(srv.AUTHORING_TOKEN_ENV, None)
        try:
            srv.ROOT = root
            srv.WIKI = root / "wiki"
            srv.RAW_INBOX = root / "raw" / "inbox"
            srv.MANIFEST = srv.RAW_INBOX / "manifest.jsonl"
            srv.LOCK_PATH = root / "compile" / ".wiki-write.lock"
            srv.subprocess.Popen = lambda *a, **k: _FakeProc()
            ingest_body = (b"target_slug=example&note=clean"
                           b"&external_urls=https%3A%2F%2Fexample.com%2Fp")
            op_body = b"slug=alpha-topic&reason=r&source_ref=x"

            def post(endpoint, **kw):
                body = ingest_body if endpoint == "/api/ingest" else op_body
                h = make_handler(endpoint, body=body, **kw)
                srv.IngestHandler.do_POST(h)
                return h.status, h.wfile.getvalue().decode("utf-8")

            for endpoint in ("/api/ingest", "/api/replace", "/api/remove"):
                # bad Host -> 421 before anything else
                assert post(endpoint, host="evil.test:8787")[0] == 421, endpoint
                # remote client without token -> 403
                assert post(endpoint, client="192.168.20.22")[0] == 403, endpoint
                # loopback but cross-origin browser request -> 403
                status, _ = post(endpoint, origin="http://evil.test",
                                 fetch_site="cross-site")
                assert status == 403, endpoint
                # token configured: wrong token from remote -> 401
                os.environ[srv.AUTHORING_TOKEN_ENV] = "workbench"
                assert post(endpoint, client="192.168.20.22",
                            token="wrong")[0] == 401, endpoint
                # token configured: correct token from remote passes authoring
                status, reply = post(endpoint, client="192.168.20.22",
                                     token="workbench")
                os.environ.pop(srv.AUTHORING_TOKEN_ENV, None)
                if endpoint == "/api/ingest":
                    assert status == 200, (endpoint, status, reply[:200])
                else:
                    assert status == 403 and "ingest-authorization" in reply, \
                        (endpoint, status, reply[:200])
                # loopback same-origin (no token) passes authoring
                status, reply = post(endpoint)
                if endpoint == "/api/ingest":
                    assert status == 200, (endpoint, status)
                else:
                    assert status == 403 and "ingest-authorization" in reply, \
                        (endpoint, status, reply[:200])
        finally:
            (srv.ROOT, srv.WIKI, srv.RAW_INBOX, srv.MANIFEST, srv.LOCK_PATH,
             srv.subprocess.Popen) = old
            if old_token is None:
                os.environ.pop(srv.AUTHORING_TOKEN_ENV, None)
            else:
                os.environ[srv.AUTHORING_TOKEN_ENV] = old_token
    print("ok test_ac8_endpoint_authoring_parity")


def test_ac8_add_gains_quarantine_and_ledger():
    with tempfile.TemporaryDirectory() as d:
        root = _server_root(d)
        old = (srv.ROOT, srv.WIKI, srv.RAW_INBOX, srv.MANIFEST, srv.LOCK_PATH,
               srv.subprocess.Popen)
        try:
            srv.ROOT = root
            srv.WIKI = root / "wiki"
            srv.RAW_INBOX = root / "raw" / "inbox"
            srv.MANIFEST = srv.RAW_INBOX / "manifest.jsonl"
            srv.LOCK_PATH = root / "compile" / ".wiki-write.lock"
            srv.subprocess.Popen = lambda *a, **k: _FakeProc()

            # a secret-bearing note refuses BEFORE any write
            body = ("target_slug=example&note=key%%3D%s" % AWS_KEY).encode("utf-8")
            h = make_handler("/api/ingest", body=body)
            srv.IngestHandler.do_POST(h)
            assert h.status == 422, h.status
            reply = h.wfile.getvalue().decode("utf-8")
            assert AWS_KEY not in reply
            assert not (root / "raw").exists(), "refusal writes nothing"
            assert not (root / "compile" / "ingest-ledger.jsonl").exists()

            # quarantine fires BEFORE the echoing validators (rebuild-r4 B2):
            # a secret in an INVALID slug or INVALID external URL must come
            # back 422-redacted, never 400 with the value echoed
            for body in (("target_slug=%s&note=x" % AWS_KEY).encode("utf-8"),
                         ("target_slug=example&external_urls=%s" % AWS_KEY).encode("utf-8")):
                h = make_handler("/api/ingest", body=body)
                srv.IngestHandler.do_POST(h)
                reply = h.wfile.getvalue().decode("utf-8")
                assert h.status == 422, (h.status, reply[:200])
                assert AWS_KEY not in reply, "validator echoed the secret"

            # a clean add WITH a source (external URL) appends one add row
            h = make_handler(
                "/api/ingest",
                body=b"target_slug=example&note=clean&external_urls=https%3A%2F%2Fexample.com%2Fp")
            srv.IngestHandler.do_POST(h)
            assert h.status == 200, h.wfile.getvalue()[:400]
            rows = ops.ledger_preflight(root / "compile" / "ingest-ledger.jsonl")
            assert len(rows) == 1 and rows[0]["operation"] == "add"
            assert rows[0]["sources"] == ["https://example.com/p"]
        finally:
            (srv.ROOT, srv.WIKI, srv.RAW_INBOX, srv.MANIFEST, srv.LOCK_PATH,
             srv.subprocess.Popen) = old
    print("ok test_ac8_add_gains_quarantine_and_ledger")


# ------------------------------------------- CFAR round-1 P2 repairs

def _render_with(meta, edges, body, source_slug="src"):
    import build_site as site
    old = (site.META, site.SLUGS, site.EDGE_STATES, site.REPOS)
    try:
        site.META = meta
        site.SLUGS = set(meta) | {"index"}
        site.EDGE_STATES = edges
        site.REPOS = []
        return site.to_html(body, source_slug=source_slug)[0]
    finally:
        site.META, site.SLUGS, site.EDGE_STATES, site.REPOS = old


def test_cfar_href_spelling_variants_are_gated():
    """CFAR P2-1: raw href spellings (spaced `=`, entity-encoded) that a
    browser still resolves to a retired target must NOT render live."""
    meta = {"src": {"retired_on": ""}, "gone": {"retired_on": "2026-07-01"}}
    edges = {}
    for raw in ('<a href = "gone.html">G</a>',
                '<a href="gone&#46;html">G</a>',
                "<a href='gone.html'>G</a>",
                '<a href="./gone.html">G</a>'):
        out = _render_with(meta, edges, raw)
        assert 'href="gone.html"' not in out and 'href = "gone.html"' not in out \
            and "gone&#46;html" not in out, (raw, out)
        assert "wl-pending" in out, (raw, out)
    print("ok test_cfar_href_spelling_variants_are_gated")


def test_cfar_tombstone_reason_no_html_injection():
    """CFAR P2-2: a retirement reason carrying raw HTML (from the authorization
    artifact) must not reach the rendered tombstone body as live markup."""
    root = fresh_root()
    article(root, "doomed-topic")
    payload = "<script>alert(1)</script> and <img src=x onerror=bad>"
    write_auth(root, remove_auth("doomed-topic", reason=payload))
    ops.remove_topic(root, slug="doomed-topic", now=NOW)
    body = (root / "wiki" / "doomed-topic.md").read_text().split("---\n", 2)[2]
    assert "<script>" not in body and "<img" not in body, body
    assert "&lt;script&gt;" in body, "reason must be HTML-escaped in the body"
    print("ok test_cfar_tombstone_reason_no_html_injection")


def test_cfar_seealso_excludes_suppressed_targets():
    """CFAR P2-3: See also must not reintroduce a live link the body gate
    suppressed (retired target or cleanly-removed edge)."""
    import build_site as site
    old = (site.META, site.SLUGS, site.EDGE_STATES)
    try:
        site.META = {"src": {"retired_on": ""},
                     "gone": {"title": "Gone", "retired_on": "2026-07-01"},
                     "cut": {"title": "Cut", "retired_on": ""},
                     "alive": {"title": "Alive", "retired_on": ""}}
        site.SLUGS = set(site.META) | {"index"}
        site.EDGE_STATES = {
            "src->cut": {"state": "cleanly-removed", "since": NOW,
                         "reason": "r", "queued": False, "enqueued_at": None}}
        out = site.build_seealso({"gone", "cut", "alive"}, "src")
    finally:
        site.META, site.SLUGS, site.EDGE_STATES = old
    assert 'href="gone.html"' not in out, out
    assert 'href="cut.html"' not in out, out
    assert 'href="alive.html"' in out, "live targets still appear in See also"
    print("ok test_cfar_seealso_excludes_suppressed_targets")


def test_cfar_index_inbound_edge_queued():
    """CFAR P2-4: a homepage (index.md) link to the removed topic must be
    queued in edge-states and the ledger's affected_edges."""
    root = fresh_root()
    article(root, "doomed-topic")
    (root / "index.md").write_text(
        "---\ntitle: Home\n---\n\n# Home\n\nsee [[doomed-topic]] now\n")
    write_auth(root, remove_auth("doomed-topic"))
    result = ops.remove_topic(root, slug="doomed-topic", now=NOW)
    states = json.loads((root / "compile" / "edge-states.json").read_text())
    assert "index->doomed-topic" in states, states
    assert "index" in result["affected_edges"]
    print("ok test_cfar_index_inbound_edge_queued")


def test_cfar_titled_markdown_link_detected():
    """CFAR P2-5: a titled markdown link `[A](slug.html "t")` is a real
    inbound reference and must be enumerated on Remove."""
    root = fresh_root()
    article(root, "doomed-topic")
    wiki = root / "wiki"
    (wiki / "linker-titled.md").write_text(
        '---\nentity: Linker\ntier: investigation\n---\n\n'
        '# Linker\n\nsee [Doomed](doomed-topic.html "the detail page") now\n')
    write_auth(root, remove_auth("doomed-topic"))
    result = ops.remove_topic(root, slug="doomed-topic", now=NOW)
    assert "linker-titled" in result["affected_edges"], result["affected_edges"]
    print("ok test_cfar_titled_markdown_link_detected")


# ------------------------------------------- CFAR round-2 P2 repairs

def test_cfar2_data_href_does_not_control_gate():
    """CFAR-2 P2-1: an auxiliary attribute like data-href must not be matched
    as the link's href and suppress a genuinely live target."""
    meta = {"src": {"retired_on": ""}, "gone": {"retired_on": "2026-07-01"},
            "alive": {"title": "Alive", "retired_on": ""}}
    out = _render_with(meta, {},
                       '<a data-href="gone.html" href="alive.html">A</a>')
    assert 'href="alive.html"' in out, out
    assert "wl-pending" not in out, out
    print("ok test_cfar2_data_href_does_not_control_gate")


def test_cfar2_remove_empty_reason_refuses_before_mutation():
    """CFAR-2/r26: a blank/whitespace/multiline authorization reason must
    refuse before auth consumption or any durable write (the retirement reason
    is bound to the artifact, and load_authorization validates it)."""
    root = fresh_root()
    article(root, "doomed-topic")
    for bad in ("", "   ", "line one\nline two"):
        write_auth(root, remove_auth("doomed-topic", reason=bad))
        before = tree_snapshot(root)
        refused(ops.remove_topic, root, slug="doomed-topic", now=NOW)
        assert tree_snapshot(root) == before, "no mutation, auth not consumed"
    print("ok test_cfar2_remove_empty_reason_refuses_before_mutation")


def test_cfar26_reason_bound_to_authorization():
    """CFAR-26 P2: the retirement rationale persisted to the tombstone, edge
    reason, PROVENANCE, and ledger is the AUTHORIZATION artifact's reason — a
    caller cannot supply a divergent rationale."""
    root = fresh_root()
    article(root, "doomed-topic")
    linked_article(root, "linker-wiki", "doomed-topic", "wiki")
    write_auth(root, remove_auth("doomed-topic",
                                 reason="board-approved retirement"))
    result = ops.remove_topic(root, slug="doomed-topic", now=NOW)
    prov = (root / "PROVENANCE.md").read_text()
    assert "board-approved retirement" in prov, prov
    ledger = ops.ledger_preflight(root / "compile" / "ingest-ledger.jsonl")
    assert ledger[0]["reason"] == "board-approved retirement", ledger[0]
    states = json.loads((root / "compile" / "edge-states.json").read_text())
    for entry in states.values():
        assert "board-approved retirement" in entry["reason"]
        assert "\n" not in entry["reason"]
    tomb = (root / "wiki" / "doomed-topic.md").read_text()
    assert "board-approved retirement" in tomb
    print("ok test_cfar26_reason_bound_to_authorization")


def test_cfar26_engine_runs_from_operation_root():
    """CFAR-26 P2: the synthesis engine must run with the operation root as
    cwd so the job's relative raw/... refs resolve regardless of the server's
    launch directory."""
    root = fresh_root()
    article(root, "alpha-topic")
    calls = []
    real = ops.subprocess.Popen

    def spy(args, **kw):
        calls.append((list(args), kw.get("cwd")))
        return real(args, **kw)

    write_auth(root, good_auth(
        engine_command=[sys.executable, "-c", "print('%s')" % GOOD_BODY]))
    old = ops.subprocess.Popen
    try:
        ops.subprocess.Popen = spy
        do_replace(root)
    finally:
        ops.subprocess.Popen = old
    engine_calls = [c for c in calls if c[0][:2] == [sys.executable, "-c"]]
    assert engine_calls, "engine must run"
    assert engine_calls[0][1] == str(root), engine_calls[0]
    print("ok test_cfar26_engine_runs_from_operation_root")


def test_cfar2_inline_frontmatter_list_form():
    """CFAR-2 P2-3: sources/raw_documents in the inline [..] form (accepted by
    the live fm_list parser) must be read for both the in-article ref check
    and the shared-source scan."""
    root = fresh_root()
    # target article with INLINE-form lists
    wiki = root / "wiki"
    wiki.mkdir(parents=True, exist_ok=True)
    (wiki / "alpha-topic.md").write_text(
        '---\nentity: Alpha Topic\ntier: investigation\n'
        'raw_documents: ["%s"]\nsources: ["%s"]\n---\n\n# Alpha\n\nBody.\n'
        % (OLD_REF, OLD_REF))
    raw_dir = root / "raw" / "inbox" / "2026-07-01" / "alpha-topic"
    raw_dir.mkdir(parents=True, exist_ok=True)
    (raw_dir / "doc-abc.md").write_text("# original raw\n")

    # a shared ref: another article (also inline form) references OLD_REF
    (wiki / "beta-topic.md").write_text(
        '---\nentity: Beta\ntier: investigation\nsources: ["%s"]\n---\n\n# Beta\n'
        % OLD_REF)
    write_auth(root, good_auth())
    before = tree_snapshot(root)
    # shared-source scan must SEE beta's inline reference and refuse
    refused(do_replace, root)
    assert tree_snapshot(root) == before, "shared inline ref must be detected"

    # now make it exclusive (remove beta) and confirm the inline ref is found,
    # moved to superseded, and is no longer load-bearing under live fm_list
    (wiki / "beta-topic.md").unlink()
    write_auth(root, good_auth())
    do_replace(root)
    fm, _, _ = srv.split_fm((wiki / "alpha-topic.md").read_text())
    assert OLD_REF not in srv.fm_list(fm, "sources")
    assert OLD_REF not in srv.fm_list(fm, "raw_documents")
    assert OLD_REF in srv.fm_list(fm, "superseded_sources")
    print("ok test_cfar2_inline_frontmatter_list_form")


# ------------------------------------------- CFAR round-3 P2 repairs

def test_cfar3_list_items_scan_past_comments():
    """CFAR-3 P2-1: a standalone comment or blank inside a sources/raw_documents
    block must not truncate the list — the live fm_list scans to the next key."""
    fm = ['sources:', '  - "raw/a.md"', '  # a standalone note', '',
          '  - "raw/b.md"', 'tier: concept']
    assert ops.fm_list_values(fm, 'sources') == ['raw/a.md', 'raw/b.md']
    # removing the earlier item keeps the key AND the later item (not orphaned)
    out = ops._remove_list_value(fm, 'sources', 'raw/a.md')
    assert ops._key_line_index(out, 'sources') >= 0, "key line survives"
    assert ops.fm_list_values(out, 'sources') == ['raw/b.md']
    print("ok test_cfar3_list_items_scan_past_comments")


def test_cfar3_replace_with_commented_block_no_orphan():
    """CFAR-3 P2-1: replacing an item in a commented block leaves later refs
    live and correctly detects the target ref."""
    root = fresh_root()
    wiki = root / "wiki"
    wiki.mkdir(parents=True, exist_ok=True)
    other = "raw/inbox/2026-07-01/alpha-topic/doc-other.md"
    (wiki / "alpha-topic.md").write_text(
        '---\nentity: Alpha Topic\ntier: investigation\n'
        'raw_documents:\n  - "%s"\nsources:\n  - "%s"  # first ingest\n'
        '  # a standalone comment line\n  - "%s"\n---\n\n# Alpha\n\nBody.\n'
        % (OLD_REF, OLD_REF, other))
    raw_dir = root / "raw" / "inbox" / "2026-07-01" / "alpha-topic"
    raw_dir.mkdir(parents=True, exist_ok=True)
    (raw_dir / "doc-abc.md").write_text("# a\n")
    (raw_dir / "doc-other.md").write_text("# b\n")
    write_auth(root, good_auth())
    do_replace(root)  # supersede OLD_REF
    fm, _, _ = srv.split_fm((wiki / "alpha-topic.md").read_text())
    assert OLD_REF in srv.fm_list(fm, "superseded_sources")
    assert OLD_REF not in srv.fm_list(fm, "sources")
    assert other in srv.fm_list(fm, "sources"), "the later ref is not orphaned"
    print("ok test_cfar3_replace_with_commented_block_no_orphan")


BOARD_FM = (
    'board_eyebrow: "E"\n'
    'board_hero: "H"\n'
    'board_subtitle: "S"\n'
    'board_narrative_link: narrative-topic\n'
    'board_pillars:\n'
    '  - "Accountability|obj|hook|pillar-purple|purple"\n'
    '  - "Provenance|obj||pillar-teal|teal"\n'
    '  - "Autonomy|obj||pillar-amber|amber"\n'
    '  - "One|obj|hook|pillar-coral|coral"\n'
    'board_inheritance:\n'
    '  - "Searles|inherit-one"\n'
    'board_method: "intent → gate → certified"\n'
    'board_guardrail: "distrust|guard-topic"\n')

BOARD_SLUGS = ["narrative-topic", "pillar-purple", "pillar-teal",
               "pillar-amber", "pillar-coral", "inherit-one", "guard-topic"]


def test_cfar3_board_links_are_gated():
    """CFAR-3 P2-2: homepage board links to a retired slug must NOT render
    live — build() routes board_html through the same gate as the body."""
    import build_site as site
    with tempfile.TemporaryDirectory() as d:
        wiki = pathlib.Path(d) / "wiki"
        wiki.mkdir()
        for s in BOARD_SLUGS:
            (wiki / ("%s.md" % s)).write_text("---\nentity: %s\n---\n\n# %s\n" % (s, s))
        old = (site.WIKI, site.META, site.SLUGS, site.EDGE_STATES, site.REPOS)
        try:
            site.WIKI = wiki
            site.META = {s: {"slug": s, "title": s, "tier": "concept",
                             "retired_on": ""} for s in BOARD_SLUGS}
            site.META["pillar-amber"]["retired_on"] = "2026-07-01"  # retired pillar
            site.SLUGS = set(site.META) | {"index"}
            site.EDGE_STATES = {}
            site.REPOS = []
            gated = site.gate_internal_links(site.build_board(BOARD_FM),
                                             source_slug="index")
        finally:
            site.WIKI, site.META, site.SLUGS, site.EDGE_STATES, site.REPOS = old
    assert 'href="pillar-amber.html"' not in gated, "retired board link must be gated"
    assert "wl-pending" in gated
    assert 'href="pillar-purple.html"' in gated, "live board links stay live"
    # build() must actually apply the gate to board_html (wiring proof)
    build_src = (pathlib.Path(__file__).resolve().parent / "build_site.py").read_text()
    assert "gate_internal_links(build_board(" in build_src
    print("ok test_cfar3_board_links_are_gated")


# ------------------------------------------- CFAR round-4 P2/P1 repairs

def test_cfar4_quoted_attr_href_does_not_bypass_gate():
    """CFAR-4 P1: a fake `href=` inside another attribute's quoted value must
    not be read as the link's href — the REAL href attribute governs."""
    meta = {"src": {"retired_on": ""}, "gone": {"retired_on": "2026-07-01"},
            "alive": {"title": "Alive", "retired_on": ""}}
    out = _render_with(
        meta, {}, "<a title=\"href='alive.html'\" href=\"gone.html\">G</a>")
    assert 'href="gone.html"' not in out, out
    assert "wl-pending" in out, out
    # a genuine live link with a decoy attribute value stays live
    out2 = _render_with(
        meta, {}, '<a data-note="href=gone.html" href="alive.html">A</a>')
    assert 'href="alive.html"' in out2 and "wl-pending" not in out2, out2
    print("ok test_cfar4_quoted_attr_href_does_not_bypass_gate")


def test_cfar4_board_frontmatter_ref_queued_on_remove():
    """CFAR-4 P2: a removed slug referenced only through index.md board
    frontmatter must still be queued in edge-states/affected_edges."""
    root = fresh_root()
    article(root, "doomed-topic")
    (root / "index.md").write_text(
        '---\nboard_narrative_link: doomed-topic\n'
        'board_pillars:\n  - "N|obj|hook|other-slug|purple"\n---\n\n'
        '# Home\n\nno body link at all\n')
    write_auth(root, remove_auth("doomed-topic"))
    result = ops.remove_topic(root, slug="doomed-topic", now=NOW)
    states = json.loads((root / "compile" / "edge-states.json").read_text())
    assert "index->doomed-topic" in states, states
    assert "index" in result["affected_edges"]
    # also detect a pillar-embedded board slug (pipe field)
    root2 = fresh_root()
    article(root2, "doomed-topic")
    (root2 / "index.md").write_text(
        '---\nboard_pillars:\n  - "Name|obj|hook|doomed-topic|purple"\n---\n\n'
        '# Home\n\nnobody\n')
    write_auth(root2, remove_auth("doomed-topic"))
    r2 = ops.remove_topic(root2, slug="doomed-topic", now=NOW)
    assert "index" in r2["affected_edges"]
    print("ok test_cfar4_board_frontmatter_ref_queued_on_remove")


# ------------------------------------------- CFAR round-5 P2 repairs

def test_cfar5_anchor_with_gt_in_attribute_is_gated():
    """CFAR-5 P2-1: a `>` inside a quoted attribute must not truncate the tag
    scan and let the real retired href stay live. Markdown may mangle such raw
    HTML, so the backstop sweep neutralizes the surviving href to `#`."""
    meta = {"src": {"retired_on": ""}, "gone": {"retired_on": "2026-07-01"}}
    out = _render_with(meta, {}, '<a title="x>y" href="gone.html">G</a>')
    assert 'href="gone.html"' not in out, out  # no live link to the retired page
    # and a plain well-formed retired link still gets the legible pending span
    out2 = _render_with(meta, {}, "see [g](gone.html) here")
    assert 'href="gone.html"' not in out2 and "wl-pending" in out2, out2
    print("ok test_cfar5_anchor_with_gt_in_attribute_is_gated")


def test_cfar5_tombstone_preserves_inline_aliases():
    """CFAR-5 P2-2: inline `aliases: [..]` must survive retirement."""
    root = fresh_root()
    wiki = root / "wiki"
    wiki.mkdir(parents=True, exist_ok=True)
    (wiki / "doomed-topic.md").write_text(
        '---\nentity: Doomed Topic\naliases: ["DT", "old-name"]\n'
        'tier: investigation\n---\n\n# Doomed\n\nBody.\n')
    (root / "raw" / "inbox" / "2026-07-01" / "doomed-topic").mkdir(parents=True)
    write_auth(root, remove_auth("doomed-topic"))
    ops.remove_topic(root, slug="doomed-topic", now=NOW)
    fm, _, _ = srv.split_fm((wiki / "doomed-topic.md").read_text())
    assert srv.fm_list(fm, "aliases") == ["DT", "old-name"], fm
    assert "retired_on" in fm
    print("ok test_cfar5_tombstone_preserves_inline_aliases")


def test_cfar5_remove_enforces_closure_over_preexisting_pending():
    """CFAR-5 P2-3: a pre-existing dangling-pending edge with queued:false
    must not survive a Remove — closure (AC5) is enforced over the whole file."""
    root = fresh_root()
    article(root, "doomed-topic")
    linked_article(root, "linker-wiki", "doomed-topic", "wiki")
    (root / "compile" / "edge-states.json").write_text(json.dumps({
        "stray->other": {"state": "dangling-pending", "since": NOW,
                         "reason": "pre-existing", "queued": False,
                         "enqueued_at": None}}))
    write_auth(root, remove_auth("doomed-topic"))
    result = ops.remove_topic(root, slug="doomed-topic", now=NOW)
    states = ops.load_edge_states(root / "compile" / "edge-states.json")
    unqueued = [k for k, v in states.items()
                if v["state"] == "dangling-pending" and v["queued"] is False]
    assert unqueued == [], "closure holds over pre-existing pending edges too"
    assert states["stray->other"]["queued"] is True
    # the repair of a committed entry is AUDITED — recorded in the ledger row
    # and PROVENANCE, and NOT conflated into this remove's affected_edges
    # (CFAR ready-state)
    assert result["repaired_edges"] == ["stray->other"], result
    assert "stray->other" not in result["affected_edges"]
    ledger = ops.ledger_preflight(root / "compile" / "ingest-ledger.jsonl")
    assert ledger[0]["repaired_edges"] == ["stray->other"]
    prov = (root / "PROVENANCE.md").read_text()
    assert "stray->other" in prov and "repaired" in prov, prov
    print("ok test_cfar5_remove_enforces_closure_over_preexisting_pending")


def test_cfar5_authority_multiline_refused():
    """CFAR-5 P2-4: a persisted auth field (authority) with a newline is
    malformed — it must refuse before consumption / any PROVENANCE write."""
    root = fresh_root()
    article(root, "alpha-topic")
    path = root / "compile" / "ingest-authorization.json"
    for bad in ("owner\n- injected line", "owner\r\nx"):
        write_auth(root, good_auth(authority=bad))
        refused(ops.load_authorization, path, NOW, operation="replace",
                slug="alpha-topic", source_ref=OLD_REF)
        before = tree_snapshot(root)
        refused(do_replace, root)
        assert tree_snapshot(root) == before, "no write on malformed authority"
    print("ok test_cfar5_authority_multiline_refused")


# ------------------------------------------- CFAR round-6 P2 repairs

def test_cfar6_unquoted_href_neutralized():
    """CFAR-6 P2-1: an unquoted href to a retired target must not stay live —
    the backstop sweep handles unquoted attribute values too."""
    meta = {"src": {"retired_on": ""}, "gone": {"retired_on": "2026-07-01"},
            "alive": {"title": "Alive", "retired_on": ""}}
    out = _render_with(meta, {}, "<a href=gone.html>G</a>")
    assert "href=gone.html" not in out and 'href="gone.html"' not in out, out
    # a live unquoted href is left intact
    out2 = _render_with(meta, {}, "<a href=alive.html>A</a>")
    assert "alive.html" in out2, out2
    print("ok test_cfar6_unquoted_href_neutralized")


def test_cfar6_reference_style_link_queued_on_remove():
    """CFAR-6 P2-2: a reference-style markdown link to the removed topic must
    be enumerated (the renderer emits + gates the same anchor)."""
    root = fresh_root()
    article(root, "doomed-topic")
    wiki = root / "wiki"
    (wiki / "linker-ref.md").write_text(
        '---\nentity: Linker\ntier: investigation\n---\n\n'
        '# Linker\n\nsee [the detail][dead] here\n\n[dead]: doomed-topic.html\n')
    write_auth(root, remove_auth("doomed-topic"))
    result = ops.remove_topic(root, slug="doomed-topic", now=NOW)
    assert "linker-ref" in result["affected_edges"], result["affected_edges"]
    print("ok test_cfar6_reference_style_link_queued_on_remove")


def test_cfar6_board_scalar_with_comment_queued():
    """CFAR-6 P2-3: an inline comment on a board scalar link must not hide the
    board reference from edge enumeration."""
    root = fresh_root()
    article(root, "doomed-topic")
    (root / "index.md").write_text(
        '---\nboard_narrative_link: doomed-topic # curated origin story\n'
        'board_guardrail: "distrust|other-slug"\n---\n\n# Home\n\nno body link\n')
    write_auth(root, remove_auth("doomed-topic"))
    result = ops.remove_topic(root, slug="doomed-topic", now=NOW)
    states = json.loads((root / "compile" / "edge-states.json").read_text())
    assert "index->doomed-topic" in states, states
    assert "index" in result["affected_edges"]
    print("ok test_cfar6_board_scalar_with_comment_queued")


# ------------------------------------------- CFAR ready-state repairs

def test_cfarready_ledger_appendability_probed():
    """CFAR ready-state P2: a read-only (unappendable) existing ledger must
    refuse in preflight — before auth consumption / any durable write — not
    fail after mutations with no audit row."""
    if os.geteuid() == 0:
        print("ok test_cfarready_ledger_appendability_probed (skipped as root)")
        return
    root = fresh_root()
    article(root, "alpha-topic")
    ledger = root / "compile" / "ingest-ledger.jsonl"
    ledger.write_text(json.dumps({
        "ts": NOW, "operation": "add", "slug": "x", "sources": ["raw/a.md"],
        "created": False, "rebuild": "ok"}, sort_keys=True) + "\n")
    os.chmod(ledger, 0o444)  # read-only → not appendable
    try:
        refused(ops.ledger_preflight, ledger)  # preflight itself refuses
        write_auth(root, good_auth())
        before = tree_snapshot(root)
        refused(do_replace, root)
        assert tree_snapshot(root) == before, "unappendable ledger → write-free"
        assert json.loads((root / "compile" / "ingest-authorization.json").read_text()
                          )["df"] == "ingest-authorization", "auth not consumed"
    finally:
        os.chmod(ledger, 0o644)
    print("ok test_cfarready_ledger_appendability_probed")


def test_cfarready_atomic_write_preserves_mode():
    """CFAR ready-state P2: an atomic rewrite must not restrict a previously
    group/world-readable file to 0600; a new file defaults to 0644."""
    with tempfile.TemporaryDirectory() as d:
        existing = pathlib.Path(d) / "wiki.md"
        existing.write_text("original")
        os.chmod(existing, 0o644)
        ops.atomic_write_text(existing, "rewritten")
        assert (os.stat(existing).st_mode & 0o777) == 0o644, \
            oct(os.stat(existing).st_mode & 0o777)
        # a preserved stricter mode survives too
        os.chmod(existing, 0o640)
        ops.atomic_write_text(existing, "again")
        assert (os.stat(existing).st_mode & 0o777) == 0o640
        # a NEW file gets the served-content default 0644
        fresh = pathlib.Path(d) / "new.json"
        ops.atomic_write_text(fresh, "{}")
        assert (os.stat(fresh).st_mode & 0o777) == 0o644
    print("ok test_cfarready_atomic_write_preserves_mode")


def test_cfarready_replace_preserves_article_mode():
    """CFAR ready-state P2: a Replace that rewrites wiki/<slug>.md preserves
    its 0644 mode (the static server serves it)."""
    root = fresh_root()
    path = article(root, "alpha-topic")
    os.chmod(path, 0o644)
    write_auth(root, good_auth())
    do_replace(root)
    assert (os.stat(path).st_mode & 0o777) == 0o644, \
        oct(os.stat(path).st_mode & 0o777)
    print("ok test_cfarready_replace_preserves_article_mode")


def test_cfarready_sourceless_add_refused():
    """CFAR ready-state P2: a source-less ingest (no documents, no URLs) must
    refuse — it must not rebuild or append a misleading `add` ledger row."""
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        (root / "compile").mkdir()
        wiki = root / "wiki"
        wiki.mkdir()
        (wiki / "example.md").write_text(
            "---\nentity: Example\ntier: investigation\n---\n\n# Example\n")
        rebuilt = []
        old = (srv.ROOT, srv.WIKI, srv.RAW_INBOX, srv.MANIFEST, srv.LOCK_PATH,
               srv.subprocess.Popen)
        try:
            srv.ROOT = root
            srv.WIKI = wiki
            srv.RAW_INBOX = root / "raw" / "inbox"
            srv.MANIFEST = srv.RAW_INBOX / "manifest.jsonl"
            srv.LOCK_PATH = root / "compile" / ".wiki-write.lock"
            srv.subprocess.Popen = lambda *a, **k: (rebuilt.append(1), _FakeProc())[1]
            # target given, but NO documents and NO external URLs
            h = make_handler("/api/ingest", body=b"target_slug=example&note=x")
            srv.IngestHandler.do_POST(h)
            assert h.status == 422, h.status
            assert not (root / "compile" / "ingest-ledger.jsonl").exists(), \
                "no ledger row for a source-less no-op"
            assert not (root / "raw").exists(), \
                "write-free: no raw-inbox directory created (checked before save)"
            assert rebuilt == [], "no rebuild for a source-less no-op"
        finally:
            (srv.ROOT, srv.WIKI, srv.RAW_INBOX, srv.MANIFEST, srv.LOCK_PATH,
             srv.subprocess.Popen) = old
    print("ok test_cfarready_sourceless_add_refused")


# ------------------------------------------- CFAR round-27 repair

def test_cfar27_backslash_href_canonicalized():
    """CFAR-27 P2: the shared canonicalizer must normalize backslash paths (a
    browser resolves `x\\..\\slug.html` and `\\slug.html` as slash paths) — a
    live target must render live and a removed target must be enumerated."""
    meta = {"target": {}, "gone": {"retired_on": "2026-07-01"}}
    for href in ("target.html", "\\target.html", "x\\..\\target.html",
                 "./x\\..\\target.html"):
        kind, stem = ops.canonical_article_target(href, meta=meta)
        assert (kind, stem) == ("article", "target"), href
    # render gate: a retired target via backslash href is non-live
    rmeta = {"src": {"retired_on": ""}, "gone": {"retired_on": "2026-07-01"}}
    out = _render_with(rmeta, {}, '<a href="x\\..\\gone.html">g</a>')
    assert 'href="x\\..\\gone.html"' not in out and "gone.html" not in out, out
    # edge discovery: a backslash link to the removed topic is queued
    root = fresh_root()
    article(root, "doomed-topic")
    (root / "wiki" / "linker-bs.md").write_text(
        '---\nentity: L\ntier: investigation\n---\n\n'
        '# L\n\n<a href="x\\..\\doomed-topic.html">x</a>\n')
    write_auth(root, remove_auth("doomed-topic"))
    result = ops.remove_topic(root, slug="doomed-topic", now=NOW)
    assert "linker-bs" in result["affected_edges"], result["affected_edges"]
    print("ok test_cfar27_backslash_href_canonicalized")


# ------------------------------------------- CFAR round-25 repair

def test_cfar25_generated_pages_cannot_be_retired():
    """CFAR-25 P2: civilization-arc is wiki-backed but the builder regenerates
    it as a whole page (arc_page ignores retired_on), so Remove must refuse it
    like index — else the tombstone is reanimated on rebuild."""
    root = fresh_root()
    wiki = root / "wiki"
    wiki.mkdir(parents=True, exist_ok=True)
    (wiki / "civilization-arc.md").write_text(
        "---\nentity: Civilization Progress Chart\ntier: meta\n---\n\n# Arc\n")
    (wiki / "index.md").write_text(
        "---\nentity: Index\ntier: meta\n---\n\n# Index\n")
    for slug in ("civilization-arc", "index"):
        write_auth(root, remove_auth(slug))
        before = tree_snapshot(root)
        refused(ops.remove_topic, root, slug=slug, now=NOW)
        assert tree_snapshot(root) == before, "%s must not be retired" % slug
    print("ok test_cfar25_generated_pages_cannot_be_retired")


# ------------------------------------------- CFAR round-24 repair

def test_cfar24_add_state_preflights_inside_lock():
    """CFAR-24 P2: the Add ledger + edge-state preflights read shared state, so
    they must run inside the write lock (a pre-lock check can go stale while
    the request waits for the lock)."""
    src = (pathlib.Path(__file__).resolve().parent / "ingest_server.py").read_text()
    seg = src.split("def handle_ingest", 1)[1].split("\n    def ", 1)[0]
    lock_at = seg.index("wiki_write_lock()")
    for call in ("ledger_preflight(", "load_edge_states("):
        assert seg.index(call) > lock_at, \
            "%s must run inside the write lock (CFAR r24)" % call
    save_at = seg.index("save_uploads(")
    assert seg.index("ledger_preflight(") < save_at, "preflight before save"
    # and corrupt edge state STILL refuses Add write-free (now inside the lock)
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        (root / "compile").mkdir()
        wiki = root / "wiki"
        wiki.mkdir()
        (wiki / "example.md").write_text(
            "---\nentity: Example\ntier: investigation\n---\n\n# Example\n")
        (root / "compile" / "edge-states.json").write_text("{corrupt")
        old = (srv.ROOT, srv.WIKI, srv.RAW_INBOX, srv.MANIFEST, srv.LOCK_PATH,
               srv.subprocess.Popen)
        try:
            srv.ROOT = root
            srv.WIKI = wiki
            srv.RAW_INBOX = root / "raw" / "inbox"
            srv.MANIFEST = srv.RAW_INBOX / "manifest.jsonl"
            srv.LOCK_PATH = root / "compile" / ".wiki-write.lock"
            srv.subprocess.Popen = lambda *a, **k: _FakeProc()
            h = make_handler("/api/ingest", body=b"target_slug=example&note=x")
            srv.IngestHandler.do_POST(h)
            assert h.status == 422, h.status
            assert not (root / "raw").exists()
        finally:
            (srv.ROOT, srv.WIKI, srv.RAW_INBOX, srv.MANIFEST, srv.LOCK_PATH,
             srv.subprocess.Popen) = old
    print("ok test_cfar24_add_state_preflights_inside_lock")


# ------------------------------------------- CFAR round-22 repair

def test_cfar22_empty_replacement_upload_refused():
    """CFAR-22 P2: an empty replacement upload is clean to the scanner but
    would supersede the live source with nothing — refuse before consuming
    auth or writing."""
    root = fresh_root()
    article(root, "alpha-topic")
    auth_path = write_auth(root, good_auth())
    before = tree_snapshot(root)
    refused(ops.replace_source, root, slug="alpha-topic", source_ref=OLD_REF,
            data=b"", filename="empty.md", note="", now=NOW)
    assert tree_snapshot(root) == before, "empty upload → write-free refusal"
    assert json.loads(auth_path.read_text())["df"] == "ingest-authorization", \
        "auth must not be consumed"
    print("ok test_cfar22_empty_replacement_upload_refused")


# ------------------------------------------- CFAR round-21 repairs

def test_cfar21_svg_multi_href_fails_closed():
    """CFAR-21 P2-1: an SVG <a> with a live href AND a retired xlink:href must
    fail closed — a live attribute cannot shield a non-live one."""
    meta = {"src": {"retired_on": ""}, "gone": {"retired_on": "2026-07-01"},
            "alive": {"title": "Alive", "retired_on": ""}}
    out = _render_with(
        meta, {}, '<svg><a href="alive.html" xlink:href="gone.html">x</a></svg>')
    assert 'xlink:href="gone.html"' not in out and 'href="gone.html"' not in out, out
    assert "wl-pending" in out, out
    print("ok test_cfar21_svg_multi_href_fails_closed")


def test_cfar21_prose_and_unused_refdef_not_queued():
    """CFAR-21 P2-2: prose `](x)` and UNUSED reference definitions emit no
    anchor in markdown, so Remove must not queue them; a used reference link
    still queues."""
    root = fresh_root()
    article(root, "doomed-topic")
    wiki = root / "wiki"
    # prose that merely contains `](doomed-topic.html)` with no preceding [text]
    # and an UNUSED reference definition — neither renders an anchor
    (wiki / "linker-noise.md").write_text(
        '---\nentity: N\ntier: investigation\n---\n\n# N\n\n'
        'a stray sequence ](doomed-topic.html) in prose\n\n'
        '[unused]: doomed-topic.html\n')
    # a USED reference-style link DOES render an anchor
    (wiki / "linker-used.md").write_text(
        '---\nentity: U\ntier: investigation\n---\n\n# U\n\n'
        'see [the page][ref]\n\n[ref]: doomed-topic.html\n')
    write_auth(root, remove_auth("doomed-topic"))
    result = ops.remove_topic(root, slug="doomed-topic", now=NOW)
    edges = result["affected_edges"]
    assert "linker-noise" not in edges, edges
    assert "linker-used" in edges, edges
    print("ok test_cfar21_prose_and_unused_refdef_not_queued")


# ------------------------------------------- CFAR round-20 repair

def test_cfar20_arc_view_gates_retired_hrefs():
    """CFAR-20 P2: the arc view builds links from data hrefs client-side — its
    safeHref must render a retired internal target as text, and the builder
    must publish the retired-slug set for it."""
    # 1) the browser gate: safeHref returns null for a retired internal href
    view = (pathlib.Path(__file__).resolve().parent / "assets"
            / "civilizationArcView.js").read_text()
    assert "isRetiredInternal" in view and "CIVWIKI_RETIRED_SLUGS" in view, \
        "arc view must gate internal hrefs against the retired set"
    assert "if (isRetiredInternal(href)) return null" in view
    # 2) the builder publishes the retired-slug global on the arc page, BEFORE
    # the deferred view script
    import build_site as site
    old = site.META
    try:
        site.META = {
            "gate-k": {"slug": "gate-k", "title": "Gate K", "tier": "meta",
                       "retired_on": "2026-07-01"},
            "live-arc": {"slug": "live-arc", "title": "Live Arc", "tier": "meta",
                         "retired_on": ""}}
        arc_html = site.arc_page({})
    finally:
        site.META = old
    marker = 'window.CIVWIKI_RETIRED_SLUGS='
    assert marker in arc_html, arc_html[:200]
    published = arc_html.split(marker, 1)[1].split(";", 1)[0]
    assert '"gate-k"' in published and '"live-arc"' not in published, published
    assert arc_html.index(marker) < arc_html.index("civilizationArcView.js"), \
        "retired set must be published before the deferred view script"
    print("ok test_cfar20_arc_view_gates_retired_hrefs")


# ------------------------------------------- CFAR round-19 repairs

def test_cfar19_unknown_target_refused_write_free():
    """CFAR-19 P2: a provided nonexistent target_slug must refuse before any
    write (save_uploads would otherwise persist raw + manifest with no ledger)."""
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        (root / "compile").mkdir()
        wiki = root / "wiki"
        wiki.mkdir()
        (wiki / "example.md").write_text(
            "---\nentity: Example\ntier: investigation\n---\n\n# Example\n")
        old = (srv.ROOT, srv.WIKI, srv.RAW_INBOX, srv.MANIFEST, srv.LOCK_PATH,
               srv.subprocess.Popen)
        try:
            srv.ROOT = root
            srv.WIKI = wiki
            srv.RAW_INBOX = root / "raw" / "inbox"
            srv.MANIFEST = srv.RAW_INBOX / "manifest.jsonl"
            srv.LOCK_PATH = root / "compile" / ".wiki-write.lock"
            srv.subprocess.Popen = lambda *a, **k: _FakeProc()
            ctype, body = _multipart(
                {"target_slug": "does-not-exist"}, "doc.md", b"# doc\n",
                field_name="documents")
            h = make_handler("/api/ingest", body=body, content_type=ctype)
            srv.IngestHandler.do_POST(h)
            assert h.status == 422, h.status
            assert not (root / "raw").exists(), "unknown target → write-free refusal"
            assert not (root / "compile" / "ingest-ledger.jsonl").exists()
        finally:
            (srv.ROOT, srv.WIKI, srv.RAW_INBOX, srv.MANIFEST, srv.LOCK_PATH,
             srv.subprocess.Popen) = old
    print("ok test_cfar19_unknown_target_refused_write_free")


def test_cfar19_code_block_links_not_queued():
    """CFAR-19 P3: links inside markdown code fences/spans render as code, not
    anchors — they must not queue spurious inbound edges on Remove."""
    root = fresh_root()
    article(root, "doomed-topic")
    wiki = root / "wiki"
    (wiki / "linker-code.md").write_text(
        '---\nentity: L\ntier: investigation\n---\n\n# L\n\n'
        'inline `[x](doomed-topic.html)` and fenced:\n\n'
        '```\n<a href="doomed-topic.html">x</a>\n[y](doomed-topic.html)\n```\n')
    linked_article(root, "linker-real", "doomed-topic", "md")  # a real link
    write_auth(root, remove_auth("doomed-topic"))
    result = ops.remove_topic(root, slug="doomed-topic", now=NOW)
    assert "linker-code" not in result["affected_edges"], result["affected_edges"]
    assert "linker-real" in result["affected_edges"]
    print("ok test_cfar19_code_block_links_not_queued")


# ------------------------------------------- CFAR round-18 repair

def test_cfar18_area_href_gated_and_queued():
    """CFAR-18 P2: <area> image-map hrefs are browser-navigable — gate them
    in the renderer and enumerate them on Remove."""
    meta = {"src": {"retired_on": ""}, "gone": {"retired_on": "2026-07-01"},
            "alive": {"title": "Alive", "retired_on": ""}}
    out = _render_with(
        meta, {}, '<map><area href="gone.html" alt="g"></map>')
    assert 'href="gone.html"' not in out, out
    out2 = _render_with(
        meta, {}, '<map><area href="alive.html" alt="a"></map>')
    assert "alive.html" in out2, out2
    # remove-side enumeration includes <area>
    root = fresh_root()
    article(root, "doomed-topic")
    (root / "wiki" / "linker-area.md").write_text(
        '---\nentity: L\ntier: investigation\n---\n\n# L\n\n'
        '<map><area href="doomed-topic.html" alt="x"></map>\n')
    write_auth(root, remove_auth("doomed-topic"))
    result = ops.remove_topic(root, slug="doomed-topic", now=NOW)
    assert "linker-area" in result["affected_edges"], result["affected_edges"]
    print("ok test_cfar18_area_href_gated_and_queued")


# ------------------------------------------- CFAR round-17 repairs

def test_cfar17_svg_xlink_href_gated():
    """CFAR-17 P2-1: an SVG anchor targeting a retired page via xlink:href must
    be gated (browsers follow xlink:href)."""
    meta = {"src": {"retired_on": ""}, "gone": {"retired_on": "2026-07-01"},
            "alive": {"title": "Alive", "retired_on": ""}}
    out = _render_with(meta, {}, '<svg><a xlink:href="gone.html">g</a></svg>')
    assert 'xlink:href="gone.html"' not in out, out
    out2 = _render_with(meta, {}, '<svg><a xlink:href="alive.html">a</a></svg>')
    assert "alive.html" in out2, out2
    print("ok test_cfar17_svg_xlink_href_gated")


def test_cfar17_prose_href_not_queued_on_remove():
    """CFAR-17 P2-2: `href=` in inline code or a non-anchor attribute must not
    queue a spurious inbound edge — only real anchors count."""
    root = fresh_root()
    article(root, "doomed-topic")
    wiki = root / "wiki"
    # inline code + a title attribute that merely mention the href — NOT links
    (wiki / "linker-prose.md").write_text(
        '---\nentity: L\ntier: investigation\n---\n\n# L\n\n'
        'the attribute `href="doomed-topic.html"` and '
        '<span title="href=doomed-topic.html">x</span> are not links\n')
    # a REAL raw anchor (and an SVG xlink anchor) that ARE links
    (wiki / "linker-anchor.md").write_text(
        '---\nentity: A\ntier: investigation\n---\n\n# A\n\n'
        '<a href="doomed-topic.html">real</a>\n')
    (wiki / "linker-svg.md").write_text(
        '---\nentity: S\ntier: investigation\n---\n\n# S\n\n'
        '<svg><a xlink:href="doomed-topic.html">s</a></svg>\n')
    write_auth(root, remove_auth("doomed-topic"))
    result = ops.remove_topic(root, slug="doomed-topic", now=NOW)
    edges = result["affected_edges"]
    assert "linker-prose" not in edges, edges
    assert "linker-anchor" in edges and "linker-svg" in edges, edges
    print("ok test_cfar17_prose_href_not_queued_on_remove")


# ------------------------------------------- CFAR round-16 repair

def test_cfar16_ingest_page_selector_excludes_retired():
    """CFAR-16 P2: the build-time ingest target <select> must not list retired
    tombstones (consistent with /api/articles + the server refusal)."""
    import build_site as site
    old = (site.META,)
    try:
        site.META = {
            "live-topic": {"slug": "live-topic", "title": "Live Topic",
                           "tier": "concept", "retired_on": ""},
            "gone-topic": {"slug": "gone-topic", "title": "Gone Topic",
                           "tier": "concept", "retired_on": "2026-07-01"}}
        page = site.ingest_page({})
    finally:
        (site.META,) = old
    assert '<option value="live-topic">' in page, page[:400]
    assert '<option value="gone-topic">' not in page, "retired must not be selectable"
    print("ok test_cfar16_ingest_page_selector_excludes_retired")


# ------------------------------------------- CFAR round-15 repairs

def test_cfar15_ledger_append_preserves_jsonl_separation():
    """CFAR-15 P2-1: appending to a preflight-valid ledger whose last line
    lacks a trailing newline must not merge two objects onto one line."""
    root = fresh_root()
    ledger = root / "compile" / "ingest-ledger.jsonl"
    row = {"ts": NOW, "operation": "add", "slug": "x",
           "sources": ["raw/a.md"], "created": False, "rebuild": "ok"}
    ledger.write_text(json.dumps(row, sort_keys=True))  # NO trailing newline
    ops.append_ledger(ledger, dict(row, slug="y"))
    parsed = ops.ledger_preflight(ledger)  # must still parse cleanly
    assert [r["slug"] for r in parsed] == ["x", "y"], ledger.read_text()
    # and an operation appending after a no-newline ledger stays auditable
    root2 = fresh_root()
    article(root2, "alpha-topic")
    (root2 / "compile" / "ingest-ledger.jsonl").write_text(
        json.dumps(row, sort_keys=True))  # no newline
    write_auth(root2, good_auth())
    do_replace(root2)
    rows = ops.ledger_preflight(root2 / "compile" / "ingest-ledger.jsonl")
    assert [r["operation"] for r in rows] == ["add", "replace"], rows
    print("ok test_cfar15_ledger_append_preserves_jsonl_separation")


def test_cfar15_markdown_escaped_link_queued_on_remove():
    """CFAR-15 P2-2: a markdown-escaped destination `[x](slug\\.html)` (which
    renders as slug.html) must be enumerated on Remove."""
    root = fresh_root()
    article(root, "doomed-topic")
    wiki = root / "wiki"
    (wiki / "linker-esc.md").write_text(
        '---\nentity: L\ntier: investigation\n---\n\n'
        '# L\n\nsee [detail](doomed-topic\\.html) now\n')
    write_auth(root, remove_auth("doomed-topic"))
    result = ops.remove_topic(root, slug="doomed-topic", now=NOW)
    assert "linker-esc" in result["affected_edges"], result["affected_edges"]
    print("ok test_cfar15_markdown_escaped_link_queued_on_remove")


# ------------------------------------------- CFAR round-14 repairs

def test_cfar14_naive_now_refused():
    """CFAR-14 P2: a naive (timezone-less) `now` must refuse before any write —
    the auth window parser would accept it but the strict ledger validator
    would reject it after mutations, orphaning the audit."""
    root = fresh_root()
    article(root, "alpha-topic")
    write_auth(root, good_auth())
    before = tree_snapshot(root)
    refused(ops.replace_source, root, slug="alpha-topic", source_ref=OLD_REF,
            data=b"# new\n", filename="new.md", note="", now="2026-07-04T12:00:00")
    assert tree_snapshot(root) == before, "naive now → write-free refusal"
    root2 = fresh_root()
    article(root2, "doomed-topic")
    write_auth(root2, remove_auth("doomed-topic"))
    before2 = tree_snapshot(root2)
    refused(ops.remove_topic, root2, slug="doomed-topic",
            now="2026-07-04T12:00:00")
    assert tree_snapshot(root2) == before2
    print("ok test_cfar14_naive_now_refused")


def test_cfar14_data_href_not_queued_on_remove():
    """CFAR-14 P3: `data-href` (and other *href attributes) must not queue a
    spurious inbound edge the renderer would never link."""
    root = fresh_root()
    article(root, "doomed-topic")
    wiki = root / "wiki"
    (wiki / "linker-datahref.md").write_text(
        '---\nentity: L\ntier: investigation\n---\n\n# L\n\n'
        'mentions <a data-href="doomed-topic.html">x</a> but no real link\n')
    # a genuine linker so the remove still has an edge to confirm the scan runs
    linked_article(root, "linker-real", "doomed-topic", "href")
    write_auth(root, remove_auth("doomed-topic"))
    result = ops.remove_topic(root, slug="doomed-topic", now=NOW)
    assert "linker-datahref" not in result["affected_edges"], result["affected_edges"]
    assert "linker-real" in result["affected_edges"]
    print("ok test_cfar14_data_href_not_queued_on_remove")


def test_cfar14_add_retired_check_inside_lock():
    """CFAR-14 P2: the effective-target retired check must run INSIDE the write
    lock and BEFORE save_uploads (write-free AND race-free). The check now lives
    in the fail-closed resolve_ingest_route router (Investigation Topic Standard
    R1/§2.4), which handle_ingest calls inside the lock before any save."""
    src = (pathlib.Path(__file__).resolve().parent / "ingest_server.py").read_text()
    seg = src.split("def handle_ingest", 1)[1].split("\n    def ", 1)[0]
    lock_at = seg.index("wiki_write_lock()")
    route_at = seg.index("resolve_ingest_route(")
    save_at = seg.index("save_uploads(")
    assert lock_at < route_at < save_at, \
        "the route decision (incl. the retired check) must be inside the lock, " \
        "before save_uploads"
    # and the retired check genuinely lives in that router (fail-closed)
    resolve_seg = src.split("def resolve_ingest_route", 1)[1].split("\ndef ", 1)[0]
    assert "article_is_retired(target_slug)" in resolve_seg, \
        "resolve_ingest_route must perform the retired-tombstone check"
    print("ok test_cfar14_add_retired_check_inside_lock")


# ------------------------------------------- CFAR round-13 repairs

def test_cfar13_add_preflights_edge_states():
    """CFAR-13 P2-1: corrupt edge-states.json must refuse Add before any write,
    like Replace/Remove."""
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        (root / "compile").mkdir()
        wiki = root / "wiki"
        wiki.mkdir()
        (wiki / "example.md").write_text(
            "---\nentity: Example\ntier: investigation\n---\n\n# Example\n")
        (root / "compile" / "edge-states.json").write_text("{corrupt")
        old = (srv.ROOT, srv.WIKI, srv.RAW_INBOX, srv.MANIFEST, srv.LOCK_PATH,
               srv.subprocess.Popen)
        try:
            srv.ROOT = root
            srv.WIKI = wiki
            srv.RAW_INBOX = root / "raw" / "inbox"
            srv.MANIFEST = srv.RAW_INBOX / "manifest.jsonl"
            srv.LOCK_PATH = root / "compile" / ".wiki-write.lock"
            srv.subprocess.Popen = lambda *a, **k: _FakeProc()
            h = make_handler("/api/ingest", body=b"target_slug=example&note=x")
            srv.IngestHandler.do_POST(h)
            assert h.status == 422, h.status
            assert not (root / "raw").exists(), "corrupt edge state → write-free refusal"
        finally:
            (srv.ROOT, srv.WIKI, srv.RAW_INBOX, srv.MANIFEST, srv.LOCK_PATH,
             srv.subprocess.Popen) = old
    print("ok test_cfar13_add_preflights_edge_states")


def test_cfar13_board_scalar_quoted_comment_queued():
    """CFAR-13 P2-3: a QUOTED board scalar with an inline comment
    (`board_narrative_link: "doomed-topic" # note`) must still enumerate."""
    root = fresh_root()
    article(root, "doomed-topic")
    (root / "index.md").write_text(
        '---\nboard_narrative_link: "doomed-topic" # curated origin\n'
        'board_guardrail: "distrust | other-slug"  # trailing note\n---\n\n'
        '# Home\n\nno body link\n')
    write_auth(root, remove_auth("doomed-topic"))
    result = ops.remove_topic(root, slug="doomed-topic", now=NOW)
    states = json.loads((root / "compile" / "edge-states.json").read_text())
    assert "index->doomed-topic" in states, states
    assert "index" in result["affected_edges"]
    # also a quoted guardrail slug with spaces around the pipe + trailing note
    root2 = fresh_root()
    article(root2, "guard-topic")
    (root2 / "index.md").write_text(
        '---\nboard_guardrail: "distrust | guard-topic" # note\n---\n\n# Home\n')
    write_auth(root2, remove_auth("guard-topic"))
    r2 = ops.remove_topic(root2, slug="guard-topic", now=NOW)
    assert "index" in r2["affected_edges"], r2["affected_edges"]
    print("ok test_cfar13_board_scalar_quoted_comment_queued")


# ------------------------------------------- CFAR round-12 repair

def test_cfar12_unassigned_add_resolving_to_retired_refused():
    """CFAR-12 P2: an unassigned upload whose derived slug matches a retired
    tombstone must refuse before the append — no tombstone resurrection."""
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        (root / "compile").mkdir()
        wiki = root / "wiki"
        wiki.mkdir()
        # a retired article whose slug is what "Gone Topic" slugifies to
        (wiki / "gone-topic.md").write_text(
            '---\nentity: Gone Topic\ntier: investigation\n'
            'retired_on: "2026-07-01"\nretired_reason: "obsolete"\n---\n\n'
            '# Gone Topic\n\nRetired.\n')
        tombstone_before = (wiki / "gone-topic.md").read_text()
        ctype, body = _multipart(  # unassigned: no target_slug field
            {"note": "resurrection attempt"}, "gone-topic.md",
            b"# Gone Topic\n\nfresh source body\n", field_name="documents")
        old = (srv.ROOT, srv.WIKI, srv.RAW_INBOX, srv.MANIFEST, srv.LOCK_PATH,
               srv.subprocess.Popen)
        try:
            srv.ROOT = root
            srv.WIKI = wiki
            srv.RAW_INBOX = root / "raw" / "inbox"
            srv.MANIFEST = srv.RAW_INBOX / "manifest.jsonl"
            srv.LOCK_PATH = root / "compile" / ".wiki-write.lock"
            srv.subprocess.Popen = lambda *a, **k: _FakeProc()
            h = make_handler("/api/ingest", body=body, content_type=ctype)
            srv.IngestHandler.do_POST(h)
            assert h.status == 422, h.status
            assert (wiki / "gone-topic.md").read_text() == tombstone_before, \
                "the retired tombstone must be untouched"
            assert not (root / "raw").exists(), "refusal must be write-free"
        finally:
            (srv.ROOT, srv.WIKI, srv.RAW_INBOX, srv.MANIFEST, srv.LOCK_PATH,
             srv.subprocess.Popen) = old
    print("ok test_cfar12_unassigned_add_resolving_to_retired_refused")


# ------------------------------------------- CFAR round-11 repairs

def test_cfar11_add_refuses_retired_target():
    """CFAR-11 P2-1: Add to a retired tombstone must refuse before any write,
    and retired articles must not appear in the ingest selector."""
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        (root / "compile").mkdir()
        wiki = root / "wiki"
        wiki.mkdir()
        (wiki / "gone-topic.md").write_text(
            '---\nentity: Gone\ntier: investigation\n'
            'retired_on: "2026-07-01"\nretired_reason: "obsolete"\n---\n\n'
            '# Gone\n\nRetired.\n')
        (wiki / "live-topic.md").write_text(
            "---\nentity: Live\ntier: investigation\n---\n\n# Live\n")
        old = (srv.ROOT, srv.WIKI, srv.RAW_INBOX, srv.MANIFEST, srv.LOCK_PATH,
               srv.subprocess.Popen)
        try:
            srv.ROOT = root
            srv.WIKI = wiki
            srv.RAW_INBOX = root / "raw" / "inbox"
            srv.MANIFEST = srv.RAW_INBOX / "manifest.jsonl"
            srv.LOCK_PATH = root / "compile" / ".wiki-write.lock"
            srv.subprocess.Popen = lambda *a, **k: _FakeProc()

            # retired articles are hidden from the /api/articles selector
            slugs = [r["slug"] for r in srv.article_records()]
            assert "gone-topic" not in slugs and "live-topic" in slugs, slugs
            assert srv.article_is_retired("gone-topic") is True

            # POST /api/ingest targeting the retired slug -> refused, no write
            h = make_handler("/api/ingest", body=b"target_slug=gone-topic&note=x")
            srv.IngestHandler.do_POST(h)
            assert h.status == 422, h.status
            before = (wiki / "gone-topic.md").read_text()
            # confirm no source was appended to the tombstone
            assert "sources:" not in before and not (root / "raw").exists()
        finally:
            (srv.ROOT, srv.WIKI, srv.RAW_INBOX, srv.MANIFEST, srv.LOCK_PATH,
             srv.subprocess.Popen) = old
    print("ok test_cfar11_add_refuses_retired_target")


def test_cfar11_search_index_excludes_retired():
    """CFAR-11 P2-2: retired articles are dropped from the search index (the
    search UI turns rows into live links → they'd stay discoverable)."""
    src = (pathlib.Path(__file__).resolve().parent / "build_site.py").read_text()
    # the search-index builder must consult retired_on and skip those rows
    idx = src.index("def build_search_index")
    seg = src[idx:idx + 1200]
    assert 'retired_on' in seg and "continue" in seg, seg
    print("ok test_cfar11_search_index_excludes_retired")


# ------------------------------------------- CFAR round-10 repairs

def test_cfar10_replacement_path_collision_refused():
    """CFAR-10 P2: a replacement that resolves to the SAME content-addressed
    path as source_ref must refuse before consuming auth or writing —
    otherwise the superseded ref would be re-added live."""
    root = fresh_root()
    wiki = root / "wiki"
    wiki.mkdir(parents=True, exist_ok=True)
    data = b"# replacement raw\n"
    sha12 = hashlib.sha256(data).hexdigest()[:12]
    # source_ref matches exactly what do_replace would compute for `data`
    colliding = "raw/inbox/2026-07-04/alpha-topic/replacement-%s.md" % sha12
    (wiki / "alpha-topic.md").write_text(
        '---\nentity: Alpha Topic\ntier: investigation\n'
        'raw_documents:\n  - "%s"\nsources:\n  - "%s"\n---\n\n# Alpha\n\nBody.\n'
        % (colliding, colliding))
    raw_dir = root / "raw" / "inbox" / "2026-07-04" / "alpha-topic"
    raw_dir.mkdir(parents=True, exist_ok=True)
    (raw_dir / ("replacement-%s.md" % sha12)).write_bytes(data)
    auth_path = write_auth(root, good_auth(source_ref=colliding))
    before = tree_snapshot(root)
    refused(ops.replace_source, root, slug="alpha-topic", source_ref=colliding,
            data=data, filename="replacement.md", note="", now=NOW)
    assert tree_snapshot(root) == before, "no write, auth not consumed"
    assert json.loads(auth_path.read_text())["df"] == "ingest-authorization"
    print("ok test_cfar10_replacement_path_collision_refused")


def test_cfar10_whitespace_only_auth_field_refused():
    """CFAR-10 P3: whitespace-only authority/reason must refuse; a padded value
    is normalized before it lands in the audit trail."""
    root = fresh_root()
    article(root, "alpha-topic")
    path = root / "compile" / "ingest-authorization.json"
    for field in ("authority", "reason"):
        write_auth(root, good_auth(**{field: "   "}))
        refused(ops.load_authorization, path, NOW, operation="replace",
                slug="alpha-topic", source_ref=OLD_REF)
    # a padded-but-nonblank authority is normalized in the persisted record
    write_auth(root, good_auth(authority="  Michael / owner  "))
    do_replace(root)
    rows = ops.ledger_preflight(root / "compile" / "ingest-ledger.jsonl")
    assert rows[0]["authorized_by"] == "Michael / owner", rows[0]
    print("ok test_cfar10_whitespace_only_auth_field_refused")


# ------------------------------------------- CFAR round-9 P2 repair

def test_cfar9_self_closing_anchor_is_gated():
    """CFAR-9 P2: a self-closing `<a href=.../>` (which browsers keep live)
    must be gated like any other anchor."""
    meta = {"src": {"retired_on": ""}, "gone": {"retired_on": "2026-07-01"},
            "alive": {"title": "Alive", "retired_on": ""}}
    out = _render_with(meta, {}, '<a href="gone.html"/>label here')
    assert 'href="gone.html"' not in out, out  # no live link to the retired page
    assert "label here" in out, "the following text is preserved (plain)"
    # a live self-closing anchor is left intact
    out2 = _render_with(meta, {}, '<a href="alive.html"/>go')
    assert "alive.html" in out2, out2
    print("ok test_cfar9_self_closing_anchor_is_gated")


# ------------------------------------------- CFAR round-8 P2 repair

def test_cfar8_gate_does_not_corrupt_valid_content():
    """CFAR-8 P2: the gate must touch ONLY real anchor href attributes — never
    a title/aria attribute that mentions an href, and never prose or inline
    code — while still gating the real href."""
    meta = {"src": {"retired_on": ""}, "gone": {"retired_on": "2026-07-01"},
            "alive": {"title": "Alive", "retired_on": ""}}
    # a live anchor whose TITLE mentions a retired href: title preserved intact,
    # the real (live) href stays live, no invalid `title="href="#""` corruption
    out = _render_with(
        meta, {}, "<a title=\"href='gone.html'\" href=\"alive.html\">A</a>")
    assert 'href="alive.html"' in out, out
    assert "href='gone.html'" in out, "the title text must be preserved verbatim"
    assert 'title="href="' not in out, "must not corrupt the title attribute"
    assert "wl-pending" not in out, out
    # prose / inline code that merely MENTIONS an internal href is untouched
    out2 = _render_with(meta, {}, "use the attribute `href=\"gone.html\"` in raw HTML")
    assert 'href="gone.html"' in out2, "inline code must be echoed verbatim"
    assert "wl-pending" not in out2 and 'href="#"' not in out2, out2
    print("ok test_cfar8_gate_does_not_corrupt_valid_content")


# ------------------------------------------- CFAR round-7 P2 repair

def _multipart(fields, doc_name, doc_bytes, field_name="document"):
    boundary = "----ingestopsboundary"
    parts = []
    for name, value in fields.items():
        parts.append("--%s\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n"
                     % (boundary, name, value))
    parts.append("--%s\r\nContent-Disposition: form-data; name=\"%s\"; "
                 "filename=\"%s\"\r\nContent-Type: text/markdown\r\n\r\n"
                 % (boundary, field_name, doc_name))
    body = "".join(parts).encode("utf-8") + doc_bytes + ("\r\n--%s--\r\n" % boundary).encode("utf-8")
    return "multipart/form-data; boundary=%s" % boundary, body


def test_cfar7_expiry_enforced_at_lock_time():
    """CFAR-7: a grant valid before the write lock but expired by the time the
    lock is acquired must NOT be consumed — the window is checked at mutation
    time (now captured inside the lock)."""
    import datetime as _dt
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        (root / "compile").mkdir()
        article(root, "alpha-topic")  # creates wiki/ + raw/ under this ROOT
        auth_path = root / "compile" / "ingest-authorization.json"
        auth_path.write_text(json.dumps(good_auth()))  # window 00:00–23:00Z

        # fake clock: 1st now() (pre-lock) within window; later (inside lock) expired
        real_dt = srv.dt.datetime
        state = {"n": 0}

        class FakeDT(real_dt):
            @classmethod
            def now(cls, tz=None):
                state["n"] += 1
                if state["n"] == 1:
                    return real_dt(2026, 7, 4, 12, 0, tzinfo=_dt.timezone.utc)
                return real_dt(2026, 7, 5, 0, 0, tzinfo=_dt.timezone.utc)  # expired

        ctype, body = _multipart(
            {"slug": "alpha-topic", "source_ref": OLD_REF},
            "replacement.md", b"# replacement raw\n")
        h = make_handler("/api/replace", body=body, content_type=ctype)
        old = (srv.ROOT, srv.WIKI, srv.RAW_INBOX, srv.MANIFEST, srv.LOCK_PATH, srv.dt.datetime)
        try:
            srv.ROOT = root
            srv.WIKI = root / "wiki"
            srv.RAW_INBOX = root / "raw" / "inbox"
            srv.MANIFEST = srv.RAW_INBOX / "manifest.jsonl"
            srv.LOCK_PATH = root / "compile" / ".wiki-write.lock"
            srv.dt.datetime = FakeDT
            srv.IngestHandler.do_POST(h)
        finally:
            (srv.ROOT, srv.WIKI, srv.RAW_INBOX, srv.MANIFEST, srv.LOCK_PATH,
             srv.dt.datetime) = old
        assert h.status in (403, 422), h.status
        spent = json.loads(auth_path.read_text())
        assert spent["df"] == "ingest-authorization", \
            "an at-lock-time-expired grant must NOT be consumed"
    # wiring proof: both handlers capture now INSIDE the lock
    src = (pathlib.Path(__file__).resolve().parent / "ingest_server.py").read_text()
    for handler in ("handle_replace", "handle_remove"):
        seg = src.split("def %s" % handler, 1)[1].split("def ", 1)[0]
        lock_at = seg.index("wiki_write_lock()")
        now_at = seg.index("dt.datetime.now", lock_at)
        assert now_at > lock_at, "%s must capture now inside the lock" % handler
    print("ok test_cfar7_expiry_enforced_at_lock_time")




# ------------------------------------------------------- fe-ux packet: R6/R2
# register + previews + manifest shards (TAI-WIKI-FRONTEND-UX AC3/AC6/AC7)

SESSION_DOC = "raw/civilization/external-landscape/alpha-topic-eval.md"


def session_doc(root, content="# session-authored eval\n", ref=SESSION_DOC):
    p = root / ref
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return ref


def commit_tree(root):
    """Register records PR-landed docs only: fixtures commit the tree so
    source_ref exists at HEAD byte-exactly (CFAR r4 P1)."""
    subprocess.run(["git", "-C", str(root), "init", "-q"], check=True)
    subprocess.run(["git", "-C", str(root), "-c", "user.email=t@t",
                    "-c", "user.name=t", "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(root), "-c", "user.email=t@t",
                    "-c", "user.name=t", "commit", "-qm", "fixture",
                    "--no-verify"], check=True)


def register_auth(slug="alpha-topic", source_ref=SESSION_DOC, **over):
    merged = dict(operation="register", slug=slug, source_ref=source_ref)
    merged.update(over)
    return good_auth(**merged)


def do_register(root, **over):
    kw = dict(slug="alpha-topic", source_ref=SESSION_DOC, note="", now=NOW)
    kw.update(over)
    return ops.register_source(root, **kw)


def test_register_authorization_domain():
    root = fresh_root()
    article(root, "alpha-topic")
    session_doc(root)
    auth_path = root / "compile" / "ingest-authorization.json"

    # no artifact
    before = tree_snapshot(root)
    try:
        do_register(root)
        raise AssertionError("expected AuthRefused")
    except ops.AuthRefused:
        pass
    assert tree_snapshot(root) == before, "refusal must write nothing"

    # wrong-operation artifact (replace) refuses register
    write_auth(root, good_auth())
    try:
        do_register(root)
        raise AssertionError("expected AuthRefused")
    except ops.AuthRefused:
        pass

    # wrong instance: different source_ref
    write_auth(root, register_auth(source_ref="raw/other/place.md"))
    try:
        do_register(root)
        raise AssertionError("expected AuthRefused")
    except ops.AuthRefused:
        pass

    # register artifact must carry a non-empty source_ref
    write_auth(root, register_auth(source_ref=""))
    try:
        ops.load_authorization(auth_path, NOW, operation="register",
                               slug="alpha-topic", source_ref="")
        raise AssertionError("expected AuthRefused")
    except ops.AuthRefused:
        pass

    # expired window
    write_auth(root, register_auth(expires_at="2026-07-04T00:30:00Z"))
    try:
        do_register(root, now="2026-07-04T12:00:00+00:00")
        raise AssertionError("expected AuthRefused")
    except ops.AuthRefused:
        pass

    # every refusal above left the artifact unconsumed (still parseable live)
    live = json.loads(auth_path.read_text())
    assert live["df"] == "ingest-authorization", "artifact must stay unconsumed"
    print("ok test_register_authorization_domain")


def test_register_preflight_domain_refuses_writing_nothing():
    root = fresh_root()
    article(root, "alpha-topic")
    session_doc(root)

    cases = [
        dict(slug="no-such-article"),                       # unknown slug
        dict(source_ref="https://example.com/x.md"),        # URL source
        dict(source_ref="compile/edge-states.json"),        # outside raw/
        dict(source_ref="raw/../compile/secrets.md"),       # traversal
        dict(source_ref="raw/inbox/missing/doc.md"),        # file absent
    ]
    for over in cases:
        auth = register_auth(**{k: v for k, v in over.items()
                                if k in ("slug", "source_ref")})
        write_auth(root, auth)
        before = tree_snapshot(root)
        msg = refused(do_register, root, **over)
        assert tree_snapshot(root) == before, \
            "refusal (%s) must write nothing" % msg

    # retired target
    (root / "wiki" / "alpha-topic.md").write_text(
        "---\nentity: A\nretired_on: \"2026-07-01\"\n---\n\n# gone\n")
    write_auth(root, register_auth())
    before = tree_snapshot(root)
    refused(do_register, root)
    assert tree_snapshot(root) == before

    # secret-bearing session doc refuses via quarantine, redacted
    root2 = fresh_root()
    article(root2, "alpha-topic")
    session_doc(root2, content="key: %s\n" % AWS_KEY)
    write_auth(root2, register_auth())
    msg = refused(do_register, root2)
    assert AWS_KEY not in msg, "refusal must never echo secret bytes"

    # already registered IN THE MANIFEST (frozen file) refuses pre-consumption
    root3 = fresh_root()
    article(root3, "alpha-topic")
    session_doc(root3)
    manifest = root3 / "raw" / "inbox" / "manifest.jsonl"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps({
        "ingested_at": NOW, "mode": "browser-ingest",
        "target_slug": "alpha-topic", "source_path": SESSION_DOC,
        "sha256": "0" * 64, "original_name": "x.md", "note": "",
        "supersedes": ""}) + "\n")
    commit_tree(root3)
    auth_path = write_auth(root3, register_auth())
    msg = refused(do_register, root3)
    assert "already registered" in msg
    assert json.loads(auth_path.read_text())["df"] == "ingest-authorization", \
        "already-registered must refuse BEFORE consumption"

    # corrupt manifest row: the dedup gate cannot vouch -> refuse (fail closed)
    manifest.write_text("{not json\n")
    write_auth(root3, register_auth())
    refused(do_register, root3)
    print("ok test_register_preflight_domain_refuses_writing_nothing")


def test_register_happy_path_and_first_consumer_shape():
    root = fresh_root()
    article(root, "alpha-topic")
    ref = session_doc(root)
    commit_tree(root)
    write_auth(root, register_auth())
    row = do_register(root, rebuild_runner=lambda: True)

    sha = hashlib.sha256((root / ref).read_bytes()).hexdigest()
    # ledger row shape (register), appended last and valid
    ledger = (root / "compile" / "ingest-ledger.jsonl").read_text().splitlines()
    last = json.loads(ledger[-1])
    assert last == row
    assert last["operation"] == "register" and last["sha256"] == sha
    assert last["result"] == "completed" and last["rebuild"] == "ok"
    # single-row shard exists; frozen manifest untouched (was never created)
    shards = sorted((root / "raw" / "inbox" / "manifest.d").glob("*.jsonl"))
    assert len(shards) == 1
    srow = json.loads(shards[0].read_text())
    assert srow["mode"] == "session-author" and srow["source_path"] == ref
    assert srow["sha256"] == sha
    assert not (root / "raw" / "inbox" / "manifest.jsonl").exists()
    # frontmatter now carries the ref
    fm = (root / "wiki" / "alpha-topic.md").read_text()
    assert ref in fm
    # artifact consumed exactly once
    consumed = json.loads((root / "compile" / "ingest-authorization.json").read_text())
    assert consumed["df"] == "ingest-authorization-consumed"

    # FIRST-CONSUMER shape: frontmatter ALREADY carries the pointer, manifest
    # does not -> register SUCCEEDS (manifest-presence is the dedup gate) and
    # the frontmatter is not duplicated
    root2 = fresh_root()
    article(root2, "alpha-topic")
    ref2 = session_doc(root2)
    # seed the pointer into raw_documents (interim provenance, issue #50)
    art = root2 / "wiki" / "alpha-topic.md"
    art.write_text(art.read_text().replace(
        "raw_documents:\n", "raw_documents:\n  - %s\n" % ref2, 1))
    commit_tree(root2)
    write_auth(root2, register_auth())
    do_register(root2, rebuild_runner=lambda: True)
    fm2 = (root2 / "wiki" / "alpha-topic.md").read_text()
    assert fm2.count(ref2) == 1, "no duplicate raw_documents entry"
    shards2 = sorted((root2 / "raw" / "inbox" / "manifest.d").glob("*.jsonl"))
    assert len(shards2) == 1, "manifest row still written for first consumer"
    print("ok test_register_happy_path_and_first_consumer_shape")


def test_register_ledger_row_is_last():
    root = fresh_root()
    article(root, "alpha-topic")
    session_doc(root)
    commit_tree(root)
    write_auth(root, register_auth())

    real = ops._run_rebuild
    def boom(*a, **kw):
        raise RuntimeError("forced failure before ledger append")
    ops._run_rebuild = boom
    try:
        do_register(root)
        raise AssertionError("expected the forced failure to propagate")
    except RuntimeError:
        pass
    finally:
        ops._run_rebuild = real
    # durable artifacts may exist (shard), but the ledger NEVER claims the op
    ledger = root / "compile" / "ingest-ledger.jsonl"
    assert not ledger.exists() or "register" not in ledger.read_text(), \
        "ledger must not claim an op that did not complete"
    shards = sorted((root / "raw" / "inbox" / "manifest.d").glob("*.jsonl"))
    assert len(shards) == 1, "shard-without-ledger-row is the detectable " \
        "signature of an incomplete op"
    print("ok test_register_ledger_row_is_last")


def test_manifest_shard_never_mutates_existing_files():
    root = fresh_root()
    article(root, "alpha-topic")
    ref1 = session_doc(root)
    commit_tree(root)
    write_auth(root, register_auth())
    do_register(root, rebuild_runner=lambda: True)
    after_first = tree_snapshot(root / "raw" / "inbox")

    ref2 = session_doc(root, content="# a second eval\n",
                       ref="raw/civilization/external-landscape/alpha-2.md")
    subprocess.run(["git", "-C", str(root), "-c", "user.email=t@t",
                    "-c", "user.name=t", "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(root), "-c", "user.email=t@t",
                    "-c", "user.name=t", "commit", "-qm", "second",
                    "--no-verify"], check=True)
    write_auth(root, register_auth(source_ref=ref2))
    do_register(root, source_ref=ref2, rebuild_runner=lambda: True,
                now="2026-07-04T12:00:01+00:00")
    after_second = tree_snapshot(root / "raw" / "inbox")
    for path, blob in after_first.items():
        assert after_second.get(path) == blob, \
            "existing manifest surface mutated: %s" % path
    assert len(after_second) == len(after_first) + 1

    # direct collision: identical row + identical now -> exclusive create refuses
    row = {"ingested_at": NOW, "mode": "session-author",
           "target_slug": "alpha-topic", "source_path": ref1,
           "sha256": hashlib.sha256(b"x").hexdigest(), "original_name": "x",
           "note": "", "supersedes": ""}
    ops.write_manifest_shard(root, row, NOW)
    refused(ops.write_manifest_shard, root, row, NOW)
    print("ok test_manifest_shard_never_mutates_existing_files")


def test_preview_remove_parity_and_readonly():
    root = fresh_root()
    article(root, "alpha-topic")
    # beta links to alpha -> one inbound edge
    article(root, "beta-topic", body="# beta\n\nSee [[alpha-topic]].\n")
    before = tree_snapshot(root)
    prev = ops.preview_remove(root, "alpha-topic")
    assert tree_snapshot(root) == before, "preview must be read-only"
    assert prev["inbound"] == ops.find_inbound_edges(root, "alpha-topic")
    assert prev["edges_would_pend"] == len(prev["inbound"]) >= 1
    assert prev["tombstone"] == "alpha-topic.html"

    # parity with the real operation's affected_edges on an identical tree
    write_auth(root, remove_auth("alpha-topic"))
    row = ops.remove_topic(root, slug="alpha-topic", now=NOW,
                           rebuild_runner=lambda: True)
    assert row["affected_edges"] == prev["inbound"]

    # doomed previews surface the same refusal lanes the op enforces
    refused(ops.preview_remove, root, "alpha-topic")      # now retired
    refused(ops.preview_remove, root, "index")            # protected
    refused(ops.preview_remove, root, "no-such-slug")     # unknown
    print("ok test_preview_remove_parity_and_readonly")


def test_preview_replace_surfaces_exact_refusal():
    root = fresh_root()
    article(root, "alpha-topic")
    article(root, "gamma-topic")
    # shared source: gamma also cites alpha's OLD_REF
    art = root / "wiki" / "gamma-topic.md"
    art.write_text(art.read_text().replace(
        "sources:\n", "sources:\n  - %s\n" % OLD_REF, 1))
    before = tree_snapshot(root)
    msg_preview = refused(ops.preview_replace, root, "alpha-topic", OLD_REF)
    assert tree_snapshot(root) == before, "preview must be read-only"
    write_auth(root, good_auth())
    msg_op = refused(do_replace, root)
    assert msg_preview == msg_op, \
        "preview must surface the operation's EXACT refusal (parity)"

    # happy preview on an unshared tree
    root2 = fresh_root()
    article(root2, "alpha-topic")
    prev = ops.preview_replace(root2, "alpha-topic", OLD_REF)
    assert prev["superseded"] == OLD_REF and prev["will_recompile"] is True
    print("ok test_preview_replace_surfaces_exact_refusal")


def test_manifest_row_allows_unassigned_add_target():
    # CFAR r1 P1: the default Add flow writes its manifest row BEFORE a new
    # article slug exists (target_slug "") — a legal historical shape the
    # shard validator must not refuse
    import tempfile
    root = pathlib.Path(tempfile.mkdtemp())
    row = {"ingested_at": NOW, "mode": "browser-ingest", "target_slug": "",
           "source_path": "raw/inbox/x/doc.md", "sha256": "b" * 64,
           "original_name": "doc.md", "note": "", "supersedes": ""}
    ops.write_manifest_shard(root, row, NOW)
    shards = sorted((root / "raw" / "inbox" / "manifest.d").glob("*.jsonl"))
    assert len(shards) == 1
    print("ok test_manifest_row_allows_unassigned_add_target")


def test_preview_surfaces_ledger_and_edge_state_refusals():
    # CFAR r2 P2: the real ops refuse on a corrupt ledger/edge-states BEFORE
    # mutating; a preview that skips those preflights would arm a submit for
    # a doomed operation. Previews must run the same read-only checks.
    root = fresh_root()
    article(root, "alpha-topic")
    (root / "compile" / "ingest-ledger.jsonl").write_text("{corrupt\n")
    refused(ops.preview_remove, root, "alpha-topic")
    refused(ops.preview_replace, root, "alpha-topic", OLD_REF)

    root2 = fresh_root()
    article(root2, "alpha-topic")
    (root2 / "compile" / "edge-states.json").write_text("{corrupt")
    refused(ops.preview_remove, root2, "alpha-topic")
    refused(ops.preview_replace, root2, "alpha-topic", OLD_REF)
    print("ok test_preview_surfaces_ledger_and_edge_state_refusals")


def test_manifest_shard_names_bind_row_identity():
    # CFAR r2 P2: two DISTINCT rows with identical content sha + identical
    # timestamp must both write (one file per ROW, not per content)
    import tempfile
    root = pathlib.Path(tempfile.mkdtemp())
    base = {"ingested_at": NOW, "mode": "browser-ingest", "target_slug": "a",
            "sha256": "c" * 64, "original_name": "doc.md", "note": "",
            "supersedes": ""}
    row1 = dict(base, source_path="raw/inbox/x/doc.md")
    row2 = dict(base, source_path="raw/inbox/y/doc.md")
    ops.write_manifest_shard(root, row1, NOW)
    ops.write_manifest_shard(root, row2, NOW)
    shards = sorted((root / "raw" / "inbox" / "manifest.d").glob("*.jsonl"))
    assert len(shards) == 2, "distinct rows must never collide on content"
    # a byte-identical row at the same instant IS a duplicate -> refuses
    refused(ops.write_manifest_shard, root, dict(row1), NOW)
    print("ok test_manifest_shard_names_bind_row_identity")


def test_register_attests_committed_clearances():
    # wiki#52 path A: register's payload is a COMMITTED file, so its findings
    # attest against the commit-time allowlist at exact blob identity — the
    # ONE principled runtime attestation lane. Every finding must carry a
    # live clearance; anything else refuses (fail closed).
    import sys as _sys
    _sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import secret_scan as _scan

    def build(root, content):
        article(root, "alpha-topic")
        ref = session_doc(root, content=content)
        write_auth(root, register_auth())
        return ref

    import datetime as _dt
    _utc_today = _dt.datetime.now(_dt.timezone.utc).date()
    _today = _utc_today.isoformat()
    _far = (_utc_today + _dt.timedelta(days=170)).isoformat()
    content = "# eval\n\nidentifier: %s\n" % AWS_KEY
    findings = list(_scan.scan_text(content))
    assert findings, "fixture must trip the scanner"
    f = findings[0]

    # (a) finding + NO clearance -> refuse, artifact unconsumed
    root = fresh_root()
    build(root, content)
    commit_tree(root)
    msg = refused(do_register, root)
    assert "uncleared" in msg or "finding" in msg
    auth_path = root / "compile" / "ingest-authorization.json"
    assert json.loads(auth_path.read_text())["df"] == "ingest-authorization"

    # (b) clearance at the WRONG blob -> refuse
    root = fresh_root()
    ref = build(root, content)
    row = {"type": "fingerprint", "rule_id": f.rule_id,
           "canonical_path": ref, "blob_sha256": "0" * 64,
           "match_sha256": f.match_sha256, "byte_offset": f.byte_offset,
           "reason": "test", "owner": "o@x", "reviewed_by": "t",
           "reviewed_on": _today, "expires_on": _far}
    (root / "compile" / ".secretsallow").write_text(json.dumps(row) + "\n")
    commit_tree(root)
    refused(do_register, root)

    # (c) exact-identity clearance, COMMITTED -> register SUCCEEDS
    root = fresh_root()
    ref = build(root, content)
    blob = hashlib.sha256((root / ref).read_bytes()).hexdigest()
    row = dict(row, canonical_path=ref, blob_sha256=blob)
    (root / "compile" / ".secretsallow").write_text(json.dumps(row) + "\n")
    commit_tree(root)
    out = do_register(root, rebuild_runner=lambda: True)
    assert out["result"] == "completed" and out["sha256"] == blob

    # (c2) the CFAR-r3 attack: clearance present ONLY in the mutable working
    # tree (uncommitted) -> refuses; the trust root is the HEAD snapshot
    root = fresh_root()
    ref = build(root, content)
    blob = hashlib.sha256((root / ref).read_bytes()).hexdigest()
    (root / "compile" / ".secretsallow").write_text("")
    commit_tree(root)
    good = dict(row, canonical_path=ref, blob_sha256=blob)
    (root / "compile" / ".secretsallow").write_text(json.dumps(good) + "\n")
    refused(do_register, root)

    # (d) clearance present but for a DIFFERENT offset -> refuse
    root = fresh_root()
    ref = build(root, content)
    blob = hashlib.sha256((root / ref).read_bytes()).hexdigest()
    bad = dict(row, canonical_path=ref, blob_sha256=blob,
               byte_offset=f.byte_offset + 1)
    (root / "compile" / ".secretsallow").write_text(json.dumps(bad) + "\n")
    commit_tree(root)
    refused(do_register, root)

    # (e) the CFAR-r4 P1 attack: clearance committed AHEAD of its file —
    # working-tree doc bytes match the clearance but are NOT at HEAD -> refuse
    root = fresh_root()
    article(root, "alpha-topic")
    write_auth(root, register_auth())
    blob_planned = hashlib.sha256(content.encode()).hexdigest()
    ahead = dict(row, canonical_path=SESSION_DOC, blob_sha256=blob_planned,
                 byte_offset=f.byte_offset)
    (root / "compile" / ".secretsallow").write_text(json.dumps(ahead) + "\n")
    commit_tree(root)                      # HEAD has the clearance, NOT the doc
    session_doc(root, content=content)     # doc appears only in the working tree
    write_auth(root, register_auth())
    msg = refused(do_register, root)
    assert "committed" in msg, msg
    print("ok test_register_attests_committed_clearances")


# ---- Investigation Topic Standard (R5/R7) — set_article_stale ----

def test_set_article_stale_stamps_and_refuses_unknown():
    """R5/R7: set_article_stale stamps stale_since (the wrapper the ADD lane and
    Replace share); re-stamping updates it; an unknown slug refuses (fail-closed)."""
    root = fresh_root()
    article(root, "topic-x")
    ops.set_article_stale(root, "topic-x", NOW)
    fm, _, _ = srv.split_fm((root / "wiki" / "topic-x.md").read_text())
    assert srv.fm_val(fm, "stale_since") == NOW, "stamps stale_since"
    later = "2026-07-05T09:30:00+00:00"
    ops.set_article_stale(root, "topic-x", later)
    fm, _, _ = srv.split_fm((root / "wiki" / "topic-x.md").read_text())
    assert srv.fm_val(fm, "stale_since") == later, "re-stamp updates stale_since"
    try:
        ops.set_article_stale(root, "no-such-topic", NOW)
        assert False, "unknown slug must refuse"
    except ops.OpRefused:
        pass
    print("ok test_set_article_stale_stamps_and_refuses_unknown")


def test_new_investigation_ingest_ignores_supersedes():
    """CFAR (Codex): a new-investigation ingest carrying a stray `supersedes`
    (a stale browser selection or an API field) records NO misleading cross-topic
    supersedes provenance — the created page and the manifest carry none."""
    with tempfile.TemporaryDirectory() as d:
        root = _server_root(d)  # wiki/example.md + compile/
        old = (srv.ROOT, srv.WIKI, srv.RAW_INBOX, srv.MANIFEST, srv.LOCK_PATH,
               srv.subprocess.Popen)
        old_token = os.environ.pop(srv.AUTHORING_TOKEN_ENV, None)
        try:
            srv.ROOT = root
            srv.WIKI = root / "wiki"
            srv.RAW_INBOX = root / "raw" / "inbox"
            srv.MANIFEST = srv.RAW_INBOX / "manifest.jsonl"
            srv.LOCK_PATH = root / "compile" / ".wiki-write.lock"
            srv.subprocess.Popen = lambda *a, **k: _FakeProc()
            ctype, body = _multipart(
                {"new_investigation": "true", "name": "Fresh Subject",
                 "supersedes": "raw/inbox/2026-01-01/other/OTHER-Evaluation.md",
                 "external_urls": "https://example.com/fresh"},
                "seed.md", b"# seed\n\nbody\n", field_name="documents")
            h = make_handler("/api/ingest", body=body, content_type=ctype)
            srv.IngestHandler.do_POST(h)
            assert h.status == 200, (h.status, h.wfile.getvalue()[:300])
            page = root / "wiki" / "fresh-subject.md"
            assert page.exists(), "the new investigation was created"
            assert "supersedes:" not in page.read_text(), \
                "a create records no supersedes provenance"
            # the stray supersedes ref must not persist ANYWHERE for a create —
            # not the article, not the URL manifest shard, not the ledger.
            leaked = [str(p.relative_to(root)) for p in root.rglob("*")
                      if p.is_file() and "OTHER-Evaluation.md" in p.read_text(errors="ignore")]
            assert not leaked, "stray supersedes leaked into: %s" % leaked
        finally:
            (srv.ROOT, srv.WIKI, srv.RAW_INBOX, srv.MANIFEST, srv.LOCK_PATH,
             srv.subprocess.Popen) = old
            if old_token is not None:
                os.environ[srv.AUTHORING_TOKEN_ENV] = old_token
    print("ok test_new_investigation_ingest_ignores_supersedes")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
    print("\nall %d ingest-ops tests passed" % len(fns))
