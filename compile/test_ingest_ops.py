#!/usr/bin/env python3
"""Stdlib-assert tests for compile/ingest_ops.py (AC1-AC8 of the
per-ingestion-ops packet, docs/superpowers/specs/2026-07-03-per-ingestion-ops-packet.md).

Secret fixtures are composed at runtime so this file's own blob never
matches the pre-commit scanner's detectors.
"""
import hashlib
import io
import json
import pathlib
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
    return good_auth(operation="remove", slug=slug, source_ref="", **over)


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
    # unreadable / not json / non-object / duplicate key
    for raw in ("{nope", "[]", '"str"', '{"df": "ingest-authorization", "df": "x"}'):
        write_auth(root, None, raw=raw)
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
        assert ops.load_authorization(path, NOW, **dict(
            operation="replace", slug="alpha-topic", source_ref=OLD_REF))
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
    print("ok test_ac3_replace_refusals_write_nothing")


# --------------------------------------------------------------------- AC4

def py_engine(code):
    return [sys.executable, "-c", code]

GOOD_BODY = "# Alpha\\n\\nRe-derived body.\\n"


def _engine_replace(root, engine_command, timeout=30):
    write_auth(root, good_auth(engine_command=engine_command,
                               engine_timeout_seconds=timeout))
    return do_replace(root)


def test_ac4_engine_failure_domain_leaves_honest_stale():
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
        text = path.read_text()
        assert "stale_since:" in text
        assert "Re-derived" not in text, "failed engine output must be discarded"
        assert "Body text." in text, "body bytes stay at deterministic state"
    print("ok test_ac4_engine_failure_domain_leaves_honest_stale")


def test_ac4_engine_success_atomic_swap():
    root = fresh_root()
    path = article(root, "alpha-topic")
    result = _engine_replace(root, py_engine("print('%s')" % GOOD_BODY))
    assert result["engine"] == "ok"
    assert result["result"] == "completed"
    text = path.read_text()
    assert "Re-derived body." in text
    assert "stale_since:" not in text, "success drops the stale marker"
    assert "entity: Alpha Topic" in text, "deterministic frontmatter retained"
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

def linked_article(root, slug, target):
    wiki = root / "wiki"
    wiki.mkdir(parents=True, exist_ok=True)
    (wiki / ("%s.md" % slug)).write_text(
        "---\nentity: %s\ntier: investigation\n---\n\n"
        "# %s\n\nwikilink [[%s]] markdown [x](%s.html) "
        "raw <a href=\"%s.html\">y</a>\n" % (slug, slug, target, target, target))


def test_ac5_remove_tombstone_and_edge_enumeration():
    root = fresh_root()
    article(root, "doomed-topic")
    linked_article(root, "linker-one", "doomed-topic")
    linked_article(root, "linker-two", "doomed-topic")
    write_auth(root, remove_auth("doomed-topic"))
    result = ops.remove_topic(root, slug="doomed-topic", reason="obsolete", now=NOW)
    path = root / "wiki" / "doomed-topic.md"
    assert path.exists(), "tombstone, never a delete"
    text = path.read_text()
    assert 'retired_on:' in text and 'retired_reason:' in text
    assert (root / "raw" / "inbox" / "2026-07-01" / "doomed-topic" / "doc-abc.md").exists()
    states = json.loads((root / "compile" / "edge-states.json").read_text())
    assert set(states) == {"linker-one->doomed-topic", "linker-two->doomed-topic"}
    for entry in states.values():
        assert entry["state"] == "dangling-pending"
        assert entry["queued"] is True
        assert entry["enqueued_at"]
        assert set(entry) == {"state", "since", "reason", "queued", "enqueued_at"}
    assert sorted(result["affected_edges"]) == ["linker-one", "linker-two"]
    assert "doomed-topic" in (root / "PROVENANCE.md").read_text()
    print("ok test_ac5_remove_tombstone_and_edge_enumeration")


def test_ac5_closure_zero_unqueued_pending():
    root = fresh_root()
    article(root, "doomed-topic")
    linked_article(root, "linker-one", "doomed-topic")
    write_auth(root, remove_auth("doomed-topic"))
    ops.remove_topic(root, slug="doomed-topic", reason="obsolete", now=NOW)
    states = ops.load_edge_states(root / "compile" / "edge-states.json")
    unqueued_pending = [k for k, v in states.items()
                        if v["state"] == "dangling-pending" and v["queued"] is False]
    assert unqueued_pending == [], "closure: every pending edge is queued"
    print("ok test_ac5_closure_zero_unqueued_pending")


def test_ac5_corrupt_edge_states_refuses():
    corrupt = [
        "{nope",
        "[]",
        '{"a->b": {"state": "dangling-pending", "since": "x", "reason": "r", "queued": true, "enqueued_at": "x", "state": "valid"}}',
        '{"a->b": {"state": "wat", "since": "x", "reason": "r", "queued": false, "enqueued_at": null}}',
        '{"a->b": {"state": "valid", "since": "x", "reason": "r", "queued": true, "enqueued_at": null}}',
        '{"a->b": {"state": "valid", "since": "x", "reason": "r", "queued": false, "enqueued_at": null, "extra": 1}}',
        '{"not a slug key": {"state": "valid", "since": "x", "reason": "r", "queued": false, "enqueued_at": null}}',
    ]
    for raw in corrupt:
        root = fresh_root()
        article(root, "doomed-topic")
        linked_article(root, "linker-one", "doomed-topic")
        write_auth(root, remove_auth("doomed-topic"))
        (root / "compile" / "edge-states.json").write_text(raw)
        before = tree_snapshot(root)
        refused(ops.remove_topic, root, slug="doomed-topic", reason="r", now=NOW)
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
        refused(ops.remove_topic, root, slug=slug, reason="r", now=NOW)
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


def test_ac6_corrupt_edge_states_fails_build():
    # strict loader refuses every corrupt form (build_site delegates to it)
    for raw in ("{nope", "[]", '{"a->b": {"state": "valid"}}',
                '{"a->b": 3}', '{"a->b": {"state": "valid", "state": "valid"}}'):
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
    # build_site must consult the strict loader + the link gate (source-level
    # wiring assertion, house pattern per test_refresh_lock_contract)
    build_src = (pathlib.Path(__file__).resolve().parent / "build_site.py").read_text()
    assert "load_edge_states(" in build_src
    assert "link_state(" in build_src
    assert "canonical_article_target(" in build_src
    assert "wl-pending" in build_src
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
        "result": "completed", "rebuild": "ok"})

    # corrupt line -> preflight refuses -> operation refuses, nothing written
    with ledger.open("a") as f:
        f.write('{"ts": "x", "ts": "y"}\n')
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
    ops.remove_topic(root, slug="alpha-topic", reason="r", now=NOW)
    rows = ops.ledger_preflight(root / "compile" / "ingest-ledger.jsonl")
    assert [r["operation"] for r in rows] == ["replace", "remove"]
    print("ok test_ac7_operations_append_row_last")


# --------------------------------------------------------------------- AC8

def make_handler(path, body=b"", content_type="application/x-www-form-urlencoded",
                 host="127.0.0.1:8787", client="127.0.0.1"):
    handler = type("FakeHandler", (), {})()
    handler.path = path
    handler.headers = {
        "Host": host,
        "Origin": "http://%s" % host,
        "Sec-Fetch-Site": "same-origin",
        "Content-Type": content_type,
        "Content-Length": str(len(body)),
    }
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


def test_ac8_endpoint_authoring_parity():
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        (root / "compile").mkdir()
        old = (srv.ROOT, srv.WIKI, srv.RAW_INBOX, srv.MANIFEST, srv.LOCK_PATH)
        try:
            srv.ROOT = root
            srv.WIKI = root / "wiki"
            srv.RAW_INBOX = root / "raw" / "inbox"
            srv.MANIFEST = srv.RAW_INBOX / "manifest.jsonl"
            srv.LOCK_PATH = root / "compile" / ".wiki-write.lock"

            for endpoint in ("/api/replace", "/api/remove"):
                # bad Host -> 421 before anything else
                h = make_handler(endpoint, host="evil.test:8787")
                srv.IngestHandler.do_POST(h)
                assert h.status == 421, endpoint
                # remote client without token -> 403 (authoring gate)
                h = make_handler(endpoint, client="192.168.20.22")
                srv.IngestHandler.do_POST(h)
                assert h.status == 403, endpoint
                # gates pass but NO authorization artifact -> refused, 403
                h = make_handler(endpoint, body=b"slug=alpha-topic&reason=r&source_ref=x")
                srv.IngestHandler.do_POST(h)
                assert h.status == 403, (endpoint, h.status)
                payload = json.loads(h.wfile.getvalue().decode("utf-8"))
                assert "error" in payload
                assert not (root / "wiki").exists() or not list((root / "wiki").glob("*"))
        finally:
            (srv.ROOT, srv.WIKI, srv.RAW_INBOX, srv.MANIFEST, srv.LOCK_PATH) = old
    print("ok test_ac8_endpoint_authoring_parity")


def test_ac8_add_gains_quarantine_and_ledger():
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        (root / "compile").mkdir()
        wiki = root / "wiki"
        wiki.mkdir()
        (wiki / "example.md").write_text(
            "---\nentity: Example\ntier: investigation\n---\n\n# Example\n")
        old = (srv.ROOT, srv.WIKI, srv.RAW_INBOX, srv.MANIFEST, srv.LOCK_PATH,
               srv.subprocess.Popen)

        class Proc:
            pid = 1
            returncode = 0

            def communicate(self, timeout=None):
                return "refresh ok", ""

        try:
            srv.ROOT = root
            srv.WIKI = wiki
            srv.RAW_INBOX = root / "raw" / "inbox"
            srv.MANIFEST = srv.RAW_INBOX / "manifest.jsonl"
            srv.LOCK_PATH = root / "compile" / ".wiki-write.lock"
            srv.subprocess.Popen = lambda *a, **k: Proc()

            # a secret-bearing note refuses BEFORE any write
            body = ("target_slug=example&note=key%%3D%s" % AWS_KEY).encode("utf-8")
            h = make_handler("/api/ingest", body=body)
            srv.IngestHandler.do_POST(h)
            assert h.status == 422, h.status
            reply = h.wfile.getvalue().decode("utf-8")
            assert AWS_KEY not in reply
            assert not (root / "raw").exists(), "refusal writes nothing"
            assert not (root / "compile" / "ingest-ledger.jsonl").exists()

            # a clean add appends one add row
            body = b"target_slug=example&note=clean"
            h = make_handler("/api/ingest", body=body)
            srv.IngestHandler.do_POST(h)
            assert h.status == 200, h.wfile.getvalue()[:400]
            rows = ops.ledger_preflight(root / "compile" / "ingest-ledger.jsonl")
            assert len(rows) == 1 and rows[0]["operation"] == "add"
        finally:
            (srv.ROOT, srv.WIKI, srv.RAW_INBOX, srv.MANIFEST, srv.LOCK_PATH,
             srv.subprocess.Popen) = old
    print("ok test_ac8_add_gains_quarantine_and_ledger")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
    print("\nall %d ingest-ops tests passed" % len(fns))
