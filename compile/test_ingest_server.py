#!/usr/bin/env python3
"""Stdlib-assert tests for compile/ingest_server.py."""
import io
import os
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ingest_server as srv  # noqa: E402


class DummyHandler:
    def __init__(self, content_type, body):
        self.headers = {
            "Content-Type": content_type,
            "Content-Length": str(len(body)),
        }
        self.rfile = io.BytesIO(body)


def test_parse_post_form_accepts_browser_multipart_uploads():
    boundary = "----codex-form-boundary"
    body = (
        "--%s\r\n"
        'Content-Disposition: form-data; name="target_slug"\r\n\r\n'
        "sakana-ai-evaluation\r\n"
        "--%s\r\n"
        'Content-Disposition: form-data; name="note"\r\n\r\n'
        "citation upgrade\r\n"
        "--%s\r\n"
        'Content-Disposition: form-data; name="documents"; filename="TAI-RES-2026-001.md"\r\n'
        "Content-Type: text/markdown\r\n\r\n"
        "# Sakana update\n\nBody.\r\n"
        "--%s--\r\n"
    ) % (boundary, boundary, boundary, boundary)
    form = srv.parse_post_form(DummyHandler(
        "multipart/form-data; boundary=%s" % boundary,
        body.encode("utf-8"),
    ))
    assert srv.first_value(form, "target_slug") == "sakana-ai-evaluation"
    assert srv.first_value(form, "note") == "citation upgrade"
    docs = srv.field_values(form, "documents")
    assert len(docs) == 1
    assert docs[0].filename == "TAI-RES-2026-001.md"
    assert docs[0].file.read() == b"# Sakana update\n\nBody."
    print("ok test_parse_post_form_accepts_browser_multipart_uploads")


def test_authoring_policy_requires_token_for_remote_clients():
    assert srv.authoring_allowed("127.0.0.1", "", "") is True
    assert srv.authoring_allowed("::1", "", "") is True
    assert srv.authoring_allowed("192.168.20.22", "", "") is False
    assert srv.authoring_allowed("192.168.20.22", "wrong", "secret") is False
    assert srv.authoring_allowed("192.168.20.22", "secret", "secret") is True
    print("ok test_authoring_policy_requires_token_for_remote_clients")


def test_host_header_policy_blocks_rebinding_hosts():
    old_allowed = os.environ.pop(srv.ALLOWED_HOSTS_ENV, None)
    try:
        assert srv.host_header_allowed("127.0.0.1:8787", 8787) is True
        assert srv.host_header_allowed("localhost:8787", 8787) is True
        assert srv.host_header_allowed("[::1]:8787", 8787) is True
        assert srv.host_header_allowed("evil.test:8787", 8787) is False
        assert srv.host_header_allowed("127.0.0.1:notaport", 8787) is False
        os.environ[srv.ALLOWED_HOSTS_ENV] = "wiki.internal:8787"
        assert srv.host_header_allowed("wiki.internal:8787", 8787) is True
        assert srv.host_header_allowed("wiki.internal:9999", 8787) is False
    finally:
        if old_allowed is None:
            os.environ.pop(srv.ALLOWED_HOSTS_ENV, None)
        else:
            os.environ[srv.ALLOWED_HOSTS_ENV] = old_allowed
    print("ok test_host_header_policy_blocks_rebinding_hosts")


def test_same_origin_authoring_policy_blocks_browser_csrf():
    assert srv.same_origin_authoring_request({
        "Host": "127.0.0.1:8787",
        "Origin": "http://127.0.0.1:8787",
        "Sec-Fetch-Site": "same-origin",
    }, 8787) is True
    assert srv.same_origin_authoring_request({
        "Host": "127.0.0.1:8787",
        "Origin": "http://evil.test",
        "Sec-Fetch-Site": "cross-site",
    }, 8787) is False
    assert srv.same_origin_authoring_request({
        "Host": "127.0.0.1:8787",
        "Sec-Fetch-Site": "cross-site",
    }, 8787) is False
    assert srv.same_origin_authoring_request({
        "Host": "127.0.0.1:8787",
        "Origin": "http://127.0.0.1:notaport",
    }, 8787) is False
    assert srv.same_origin_authoring_request({
        "Host": "127.0.0.1:8787",
    }, 8787) is True
    print("ok test_same_origin_authoring_policy_blocks_browser_csrf")


def test_article_records_hide_sources_when_not_authorized():
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        wiki = root / "wiki"
        wiki.mkdir()
        (wiki / "example.md").write_text(
            "---\n"
            "entity: Example\n"
            "tier: investigation\n"
            "sources:\n"
            "  - /Transpara/transpara-ai/repos/docs/private.md\n"
            "---\n\n"
            "# Example\n"
        )
        old_wiki = srv.WIKI
        try:
            srv.WIKI = wiki
            hidden = srv.article_records(include_sources=False)
            visible = srv.article_records(include_sources=True)
            assert hidden[0]["sources"] == []
            assert visible[0]["sources"] == ["/Transpara/transpara-ai/repos/docs/private.md"]
        finally:
            srv.WIKI = old_wiki
    print("ok test_article_records_hide_sources_when_not_authorized")


def test_save_uploads_rejects_target_slug_traversal_before_write():
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        old_root, old_raw, old_manifest = srv.ROOT, srv.RAW_INBOX, srv.MANIFEST
        try:
            srv.ROOT = root
            srv.RAW_INBOX = root / "raw" / "inbox"
            srv.MANIFEST = srv.RAW_INBOX / "manifest.jsonl"
            form = {
                "documents": srv.FormField(
                    "documents",
                    filename="escape.md",
                    data=b"# should not be written\n",
                )
            }
            try:
                srv.save_uploads(form, "../escape", "", "")
            except ValueError:
                assert not list(root.rglob("escape*"))
                print("ok test_save_uploads_rejects_target_slug_traversal_before_write")
                return
            raise AssertionError("traversal slug should be rejected")
        finally:
            srv.ROOT, srv.RAW_INBOX, srv.MANIFEST = old_root, old_raw, old_manifest


def test_append_sources_quotes_urls_and_preserves_fragments():
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        wiki = root / "wiki"
        wiki.mkdir()
        article = wiki / "sakana-ai-evaluation.md"
        article.write_text(
            "---\n"
            "entity: Sakana AI Capability Evaluation\n"
            "tier: investigation\n"
            "sources:\n"
            "  - raw/existing.md\n"
            "confidence:\n"
            "  sources: test\n"
            "---\n\n"
            "# Body\n"
        )
        old_wiki = srv.WIKI
        try:
            srv.WIKI = wiki
            added = srv.append_sources_to_article(
                "sakana-ai-evaluation",
                ["raw/inbox/2026-06-24/sakana/update.md", "https://example.com/paper#section-2"],
                note="better citation",
                supersedes="raw/existing.md",
            )
            assert "https://example.com/paper#section-2" in added
            fm, _, _ = srv.split_fm(article.read_text())
            sources = srv.fm_list(fm, "sources")
            assert "raw/existing.md" in sources
            assert "raw/inbox/2026-06-24/sakana/update.md" in sources
            assert "https://example.com/paper#section-2" in sources
            assert article.read_text().count("confidence:") == 1
        finally:
            srv.WIKI = old_wiki
    print("ok test_append_sources_quotes_urls_and_preserves_fragments")


def test_append_sources_collapses_supersedes_before_frontmatter_comment():
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        wiki = root / "wiki"
        wiki.mkdir()
        article = wiki / "example.md"
        article.write_text(
            "---\n"
            "entity: Example\n"
            "tier: investigation\n"
            "sources:\n"
            "  - raw/existing.md\n"
            "---\n\n"
            "# Body\n"
        )
        old_wiki = srv.WIKI
        try:
            srv.WIKI = wiki
            srv.append_sources_to_article(
                "example",
                ["raw/new.md"],
                note="note\nwith break",
                supersedes="raw/existing.md\ninjected_key: bad",
            )
            text = article.read_text()
            assert "note: note with break" in text
            assert "supersedes: raw/existing.md injected_key: bad" in text
            assert "\ninjected_key: bad" not in text
        finally:
            srv.WIKI = old_wiki
    print("ok test_append_sources_collapses_supersedes_before_frontmatter_comment")


def test_append_raw_documents_updates_article_nav_inputs():
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        wiki = root / "wiki"
        wiki.mkdir()
        article = wiki / "sakana-ai-evaluation.md"
        article.write_text(
            "---\n"
            "entity: Sakana AI Capability Evaluation\n"
            "tier: investigation\n"
            "sources:\n"
            "  - raw/existing.md\n"
            "---\n\n"
            "# Body\n"
        )
        old_wiki = srv.WIKI
        try:
            srv.WIKI = wiki
            added = srv.append_raw_documents_to_article(
                "sakana-ai-evaluation",
                ["raw/inbox/2026-06-24/sakana/update.md", "https://example.com/paper"],
            )
            assert added == ["raw/inbox/2026-06-24/sakana/update.md"]
            fm, _, _ = srv.split_fm(article.read_text())
            assert srv.fm_list(fm, "raw_documents") == ["raw/inbox/2026-06-24/sakana/update.md"]
            assert "https://example.com/paper" not in article.read_text()
        finally:
            srv.WIKI = old_wiki
    print("ok test_append_raw_documents_updates_article_nav_inputs")


def test_create_article_from_source_for_unassigned_ingest():
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        wiki = root / "wiki"
        raw = root / "raw" / "inbox" / "2026-06-24" / "unassigned"
        wiki.mkdir(parents=True)
        raw.mkdir(parents=True)
        source = raw / "TAI-RES-2026-003-v1.0.0-Google-Open-Knowledge-Format-Evaluation.md"
        source.write_text(
            "---\n"
            "document_id: TAI-RES-2026-003\n"
            "title: Google Open Knowledge Format (OKF) Capability Evaluation\n"
            "version: 1.0.0\n"
            "---\n\n"
            "## Abstract\n\n"
            "OKF standardizes the envelope; the Civilization governs the contents.\n"
        )
        old_root, old_wiki = srv.ROOT, srv.WIKI
        try:
            srv.ROOT = root
            srv.WIKI = wiki
            rel = str(source.relative_to(root))
            slug, created = srv.create_article_from_source(rel, note="new research")
            assert created is True
            assert slug == "google-open-knowledge-format-capability-evaluation"
            article = wiki / ("%s.md" % slug)
            assert article.exists()
            fm, _, _ = srv.split_fm(article.read_text())
            assert srv.fm_list(fm, "raw_documents") == [rel]
            assert srv.fm_list(fm, "sources") == [rel]
        finally:
            srv.ROOT = old_root
            srv.WIKI = old_wiki
    print("ok test_create_article_from_source_for_unassigned_ingest")


def test_create_article_from_source_escapes_untrusted_title_markdown():
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        wiki = root / "wiki"
        raw = root / "raw" / "inbox" / "2026-06-24" / "unassigned"
        wiki.mkdir(parents=True)
        raw.mkdir(parents=True)
        source = raw / "malicious-title.md"
        source.write_text(
            "---\n"
            "title: \"<script>alert(1)</script> [x](javascript:alert(1))\"\n"
            "---\n\n"
            "Body.\n"
        )
        old_root, old_wiki = srv.ROOT, srv.WIKI
        try:
            srv.ROOT = root
            srv.WIKI = wiki
            rel = str(source.relative_to(root))
            slug, created = srv.create_article_from_source(rel)
            assert created is True
            article = wiki / ("%s.md" % slug)
            _, body, _ = srv.split_fm(article.read_text())
            assert "<script" not in body.lower()
            assert "](javascript:" not in body.lower()
        finally:
            srv.ROOT = old_root
            srv.WIKI = old_wiki
    print("ok test_create_article_from_source_escapes_untrusted_title_markdown")


def test_external_url_validation_rejects_unsafe_scheme():
    try:
        srv.valid_external_urls("javascript:alert(1)")
    except ValueError:
        print("ok test_external_url_validation_rejects_unsafe_scheme")
        return
    raise AssertionError("javascript: URL must be rejected")


def test_source_href_matches_build_site_source_viewer_ids():
    source = "raw/inbox/2026-06-24/sakana/update.md"
    assert srv.source_href(source) == "source/29d1acbe353cb797.html"
    assert srv.source_href("https://example.com/paper#section-2") == "https://example.com/paper#section-2"
    print("ok test_source_href_matches_build_site_source_viewer_ids")


def test_rebuild_endpoint_path_runs_refresh_under_server_lock():
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        (root / "compile").mkdir()
        old_root, old_lock, old_popen = srv.ROOT, srv.LOCK_PATH, srv.subprocess.Popen
        calls = []

        class Proc:
            pid = 12345
            returncode = 0

            def communicate(self, timeout=None):
                assert timeout == 240
                return "refresh ok", ""

        def fake_popen(args, **kwargs):
            calls.append((args, kwargs))
            assert srv.LOCK_PATH.exists()
            return Proc()

        try:
            srv.ROOT = root
            srv.LOCK_PATH = root / "compile" / ".wiki-write.lock"
            srv.subprocess.Popen = fake_popen
            result = srv.run_refresh()
            assert result["ok"] is True
            assert len(calls) == 1
            args, kwargs = calls[0]
            assert args[-1] == str(root / "compile" / "refresh.py")
            assert "build_site.py" not in " ".join(args)
            assert kwargs["cwd"] == str(root)
            assert kwargs["stdout"] == srv.subprocess.PIPE
            assert kwargs["stderr"] == srv.subprocess.PIPE
            assert kwargs["text"] is True
            assert kwargs["start_new_session"] is True
        finally:
            srv.ROOT, srv.LOCK_PATH, srv.subprocess.Popen = old_root, old_lock, old_popen
    print("ok test_rebuild_endpoint_path_runs_refresh_under_server_lock")


def test_rebuild_endpoint_timeout_returns_structured_refresh_failure():
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        body = b""
        handler = type("FakeHandler", (), {})()
        handler.path = "/api/rebuild"
        handler.headers = {
            "Host": "127.0.0.1:8787",
            "Origin": "http://127.0.0.1:8787",
            "Sec-Fetch-Site": "same-origin",
            "Content-Length": str(len(body)),
        }
        handler.client_address = ("127.0.0.1", 12345)
        handler.server = type("FakeServer", (), {"server_port": 8787})()
        handler.rfile = io.BytesIO(body)
        handler.wfile = io.BytesIO()
        handler.status = None
        handler.send_response = lambda status: setattr(handler, "status", status)
        handler.send_header = lambda _name, _value: None
        handler.end_headers = lambda: None
        handler.require_allowed_host = lambda: srv.IngestHandler.require_allowed_host(handler)
        handler.require_authoring = lambda: srv.IngestHandler.require_authoring(handler)
        old_root, old_lock = srv.ROOT, srv.LOCK_PATH
        old_popen, old_killpg = srv.subprocess.Popen, srv.os.killpg
        killed = []

        class Proc:
            pid = 12345

            def communicate(self, timeout=None):
                if timeout is not None:
                    raise srv.subprocess.TimeoutExpired(
                        "refresh.py", timeout, output="partial", stderr="late")
                return "partial", "late"

        def fake_popen(_args, **_kwargs):
            return Proc()

        def fake_killpg(pid, sig):
            assert srv.LOCK_PATH.exists()
            killed.append((pid, sig))

        try:
            srv.ROOT = root
            srv.LOCK_PATH = root / "compile" / ".wiki-write.lock"
            srv.subprocess.Popen = fake_popen
            srv.os.killpg = fake_killpg
            srv.IngestHandler.do_POST(handler)
            assert handler.status == 500
            payload = srv.json.loads(handler.wfile.getvalue().decode("utf-8"))
            assert payload["refresh"]["ok"] is False
            assert payload["refresh"]["returncode"] is None
            assert payload["refresh"]["stdout"] == "partial"
            assert payload["refresh"]["stderr"] == "late"
            assert "timed out after 240" in payload["refresh"]["error"]
            assert killed == [(12345, srv.signal.SIGKILL)]
        finally:
            srv.ROOT, srv.LOCK_PATH = old_root, old_lock
            srv.subprocess.Popen, srv.os.killpg = old_popen, old_killpg
    print("ok test_rebuild_endpoint_timeout_returns_structured_refresh_failure")


def test_rebuild_start_failure_returns_structured_refresh_failure():
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        old_root, old_lock, old_popen = srv.ROOT, srv.LOCK_PATH, srv.subprocess.Popen

        def fake_popen(_args, **_kwargs):
            raise OSError("spawn failed")

        try:
            srv.ROOT = root
            srv.LOCK_PATH = root / "compile" / ".wiki-write.lock"
            srv.subprocess.Popen = fake_popen
            result = srv.run_refresh()
            assert result["ok"] is False
            assert result["returncode"] is None
            assert result["stdout"] == ""
            assert result["stderr"] == "spawn failed"
            assert result["error"] == "failed to start refresh"
        finally:
            srv.ROOT, srv.LOCK_PATH, srv.subprocess.Popen = old_root, old_lock, old_popen
    print("ok test_rebuild_start_failure_returns_structured_refresh_failure")


def test_ingest_endpoint_path_runs_refresh_and_returns_refresh_payload():
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        wiki = root / "wiki"
        wiki.mkdir()
        (wiki / "example.md").write_text(
            "---\n"
            "entity: Example\n"
            "tier: investigation\n"
            "---\n\n"
            "# Example\n"
        )
        body = (
            "target_slug=example&"
            "external_urls=https%3A%2F%2Fexample.com%2Fpaper&"
            "note=citation%20update"
        ).encode("utf-8")
        handler = type("FakeHandler", (), {})()
        handler.headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": str(len(body)),
        }
        handler.rfile = io.BytesIO(body)
        handler.wfile = io.BytesIO()
        handler.status = None
        handler.send_response = lambda status: setattr(handler, "status", status)
        handler.send_header = lambda _name, _value: None
        handler.end_headers = lambda: None
        old_root, old_wiki, old_raw = srv.ROOT, srv.WIKI, srv.RAW_INBOX
        old_manifest, old_lock, old_popen = srv.MANIFEST, srv.LOCK_PATH, srv.subprocess.Popen
        calls = []

        class Proc:
            pid = 12345
            returncode = 0

            def communicate(self, timeout=None):
                assert timeout == 240
                return "refresh ok", ""

        def fake_popen(args, **kwargs):
            calls.append((args, kwargs))
            assert srv.LOCK_PATH.exists()
            return Proc()

        try:
            srv.ROOT = root
            srv.WIKI = wiki
            srv.RAW_INBOX = root / "raw" / "inbox"
            srv.MANIFEST = srv.RAW_INBOX / "manifest.jsonl"
            srv.LOCK_PATH = root / "compile" / ".wiki-write.lock"
            srv.subprocess.Popen = fake_popen
            srv.IngestHandler.handle_ingest(handler)
            assert handler.status == 200
            payload = srv.json.loads(handler.wfile.getvalue().decode("utf-8"))
            assert "refresh" in payload
            assert "build" not in payload
            assert payload["refresh"]["ok"] is True
            assert payload["refresh"]["stdout"] == "refresh ok"
            assert payload["article_sources_added"] == ["https://example.com/paper"]
            assert payload["source_hrefs"] == [{
                "source": "https://example.com/paper",
                "href": "https://example.com/paper",
            }]
            assert len(calls) == 1
            args, kwargs = calls[0]
            assert args[-1] == str(root / "compile" / "refresh.py")
            assert "build_site.py" not in " ".join(args)
            assert kwargs["cwd"] == str(root)
            assert kwargs["start_new_session"] is True
        finally:
            srv.ROOT, srv.WIKI, srv.RAW_INBOX = old_root, old_wiki, old_raw
            srv.MANIFEST, srv.LOCK_PATH, srv.subprocess.Popen = old_manifest, old_lock, old_popen
    print("ok test_ingest_endpoint_path_runs_refresh_and_returns_refresh_payload")


def test_refresh_lock_contract_is_owned_by_callers():
    root = pathlib.Path(__file__).resolve().parents[1]
    ingest = root / "compile" / "ingest_server.py"
    refresh = root / "compile" / "refresh.py"
    systemd = root / "compile" / "systemd" / "transpara-ai-civilization-wiki-refresh.service"
    ingest_text = ingest.read_text()
    refresh_text = refresh.read_text()
    systemd_text = systemd.read_text()
    assert "fcntl.flock" in ingest_text
    assert ".wiki-write.lock" not in refresh_text
    assert "flock(" not in refresh_text
    assert "/usr/bin/flock" in systemd_text
    assert "WorkingDirectory=/Transpara/transpara-ai/repos/wiki" in systemd_text
    assert "compile/.wiki-write.lock" in systemd_text
    print("ok test_refresh_lock_contract_is_owned_by_callers")

# ------------------------------------------------- fe-ux packet: R2/R6 server

def _preview_root():
    import tempfile, json as _json
    root = pathlib.Path(tempfile.mkdtemp())
    (root / "compile").mkdir(parents=True)
    (root / "PROVENANCE.md").write_text("# Provenance\n")
    wiki = root / "wiki"
    wiki.mkdir()
    (wiki / "alpha-topic.md").write_text(
        "---\nentity: Alpha\nsources:\n  - raw/inbox/2026-07-01/alpha-topic/doc.md\n"
        "raw_documents:\n  - raw/inbox/2026-07-01/alpha-topic/doc.md\n---\n\n# A\n")
    (wiki / "beta-topic.md").write_text(
        "---\nentity: Beta\n---\n\n# B\n\nSee [[alpha-topic]].\n")
    raw = root / "raw" / "inbox" / "2026-07-01" / "alpha-topic"
    raw.mkdir(parents=True)
    (raw / "doc.md").write_text("# doc\n")
    return root


def test_preview_payload_shapes_and_readonly():
    import ingest_ops as ops
    root = _preview_root()
    def snap(r):
        return {str(p): p.read_bytes() for p in sorted(r.rglob("*")) if p.is_file()}
    before = snap(root)

    # happy remove preview: parity with the ops helper
    payload = srv.preview_payload(root, "remove", "alpha-topic", "")
    assert payload["preview"] == ops.preview_remove(root, "alpha-topic")
    assert payload["preview"]["inbound"] == ["beta-topic"]

    # happy replace preview
    payload = srv.preview_payload(
        root, "replace", "alpha-topic", "raw/inbox/2026-07-01/alpha-topic/doc.md")
    assert payload["preview"]["superseded"].endswith("doc.md")

    # doomed operation previews its EXACT refusal in the refuses shape
    payload = srv.preview_payload(root, "remove", "no-such-slug", "")
    assert payload["preview"]["refuses"] == "unknown article slug"

    # unknown operation / malformed params raise (422 at the route)
    for args in (("frobnicate", "alpha-topic", ""),
                 ("remove", "alpha-topic", "raw/x.md"),
                 ("replace", "alpha-topic", "")):
        try:
            srv.preview_payload(root, *args)
            raise AssertionError("expected OpRefused for %r" % (args,))
        except ops.OpRefused:
            pass

    # echo-quarantine: a secret-bearing param refuses WITHOUT echoing bytes
    secret = "AK" + "IA" + "ABCDEFGHIJKLMNOP"
    try:
        srv.preview_payload(root, "remove", secret, "")
        raise AssertionError("expected OpRefused")
    except ops.OpRefused as exc:
        assert secret not in str(exc), "refusal must never echo secret bytes"

    assert snap(root) == before, "preview must be strictly read-only"
    print("ok test_preview_payload_shapes_and_readonly")


def test_preview_and_register_route_wiring():
    src = (pathlib.Path(__file__).resolve().parent / "ingest_server.py").read_text()
    get_seg = src.split("def do_GET", 1)[1].split("\n    def ", 1)[0]
    assert "/api/preview" in get_seg, "preview must be a GET route"
    assert "require_authoring" in get_seg.split("/api/preview")[0] or \
        "require_authoring" in get_seg.split("/api/preview", 1)[1], \
        "preview must sit behind require_authoring (stricter than /api/articles)"
    post_seg = src.split("def do_POST", 1)[1].split("\n    def ", 1)[0]
    assert '"/api/register"' in post_seg, "register must be a POST route"
    reg_seg = src.split("def handle_register", 1)[1].split("\n    def ", 1)[0]
    lock_at = reg_seg.index("wiki_write_lock()")
    now_at = reg_seg.index("dt.datetime.now", reg_seg.index("load_authorization"))
    assert now_at > lock_at or "load_authorization" in reg_seg[:lock_at], \
        "artifact gate fires before the lock; now is captured inside it"
    seg_lock = reg_seg[lock_at:]
    assert "dt.datetime.now" in seg_lock, "now must be captured inside the lock (CFAR r7)"
    print("ok test_preview_and_register_route_wiring")


def test_add_manifest_writes_are_sharded():
    import tempfile, json as _json
    import ingest_ops as ops
    root = pathlib.Path(tempfile.mkdtemp())
    row = {"ingested_at": "2026-07-06T12:00:00+00:00", "mode": "browser-ingest",
           "target_slug": "alpha-topic", "source_path": "raw/inbox/x/doc.md",
           "sha256": "a" * 64, "original_name": "doc.md", "note": "",
           "supersedes": ""}
    old_root = srv.ROOT
    srv.ROOT = root
    try:
        srv.append_manifest(dict(row))
        shards = sorted((root / "raw" / "inbox" / "manifest.d").glob("*.jsonl"))
        assert len(shards) == 1, "Add manifest row must land as a shard"
        assert _json.loads(shards[0].read_text()) == row
        assert not (root / "raw" / "inbox" / "manifest.jsonl").exists(), \
            "the frozen manifest file must never grow a new row"
        # identical row again -> exclusive-create refusal, first shard intact
        try:
            srv.append_manifest(dict(row))
            raise AssertionError("expected OpRefused on shard collision")
        except ops.OpRefused:
            pass
        assert len(sorted((root / "raw" / "inbox" / "manifest.d").glob("*.jsonl"))) == 1
    finally:
        srv.ROOT = old_root
    print("ok test_add_manifest_writes_are_sharded")


def test_article_records_expose_raw_documents_for_replace():
    # CFAR r1 P2: the backend replace preflight accepts sources OR
    # raw_documents; the UI selector can only offer what /api/articles
    # exposes, so records must carry both (behind the same sources gate)
    recs = srv.article_records(include_sources=True)
    assert recs, "need at least one article"
    assert all("raw_documents" in r for r in recs)
    gated = srv.article_records(include_sources=False)
    assert all(r["raw_documents"] == [] for r in gated), \
        "raw_documents must respect the include_sources gate"
    print("ok test_article_records_expose_raw_documents_for_replace")



if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
    print("\nall %d ingest-server tests passed" % len(fns))
