#!/usr/bin/env python3
"""Exercise DevOps corpus imports through the real HTTP/auth/form handler."""
import http.client
import json
import pathlib
import tempfile
import threading
import unittest
from unittest import mock
from urllib.parse import urlencode

import ingest_server as srv
from article_catalog import load_catalog


class DevOpsIngestTests(unittest.TestCase):
    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.root = pathlib.Path(scratch.name)
        (self.root / "wiki").mkdir()
        patches = [
            mock.patch.multiple(srv, ROOT=self.root, WIKI=self.root / "wiki",
                                RAW_INBOX=self.root / "raw/inbox",
                                LOCK_PATH=self.root / "compile/.wiki-write.lock"),
            mock.patch.object(srv, "run_refresh_unlocked", return_value={"ok": True}),
            mock.patch.object(srv.IngestHandler, "log_message"),
            mock.patch.dict(srv.os.environ, {srv.AUTHORING_TOKEN_ENV: "fixture-editor"}),
        ]
        for patch in patches:
            patch.start()
            self.addCleanup(patch.stop)
        self.server = srv.ThreadingHTTPServer(("127.0.0.1", 0), srv.IngestHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop_server)
        self.fields = dict(new_article="true", name="Container hosting", space="devops",
                           section="containers", steward="transpara",
                           article_markdown="# Container hosting\n\nReviewed container procedure.\n",
                           external_urls="https://example.test/hosting",
                           source_authority="engineering-docs")

    def stop_server(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)

    def request(self, method, route, fields=None, documents=(), authorized=True):
        headers = {srv.AUTHORING_TOKEN_HEADER: "fixture-editor"} if authorized else {}
        body = None
        if documents:
            boundary = "devops-test-boundary"
            parts = [('--%s\r\nContent-Disposition: form-data; name="%s"\r\n\r\n%s\r\n'
                      % (boundary, key, value)).encode() for key, value in fields.items()]
            for name, data in documents:
                parts.append(('--%s\r\nContent-Disposition: form-data; name="documents"; '
                              'filename="%s"\r\nContent-Type: text/plain\r\n\r\n'
                              % (boundary, name)).encode() + data + b"\r\n")
            body = b"".join(parts) + ("--%s--\r\n" % boundary).encode()
            headers["Content-Type"] = "multipart/form-data; boundary=" + boundary
        elif fields is not None:
            body = urlencode(fields).encode()
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=5)
        try:
            connection.request(method, route, body, headers)
            response = connection.getresponse()
            return response.status, json.loads(response.read())
        finally:
            connection.close()

    def snapshot(self):
        return {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob("*")
                if p.is_file() and p.name != ".wiki-write.lock"}

    def test_discovery_and_create_then_append_preserve_prose_and_all_sources(self):
        status, discovery = self.request("GET", "/api/spaces")
        self.assertEqual(status, 200)
        devops = next(s for s in discovery["spaces"] if s["key"] == "devops")
        self.assertTrue(devops["can_create_article"])
        self.assertEqual(devops["steward"], "transpara")
        self.assertIn("containers", [s["key"] for s in devops["sections"]])
        original = "# Source\n\n  Original whitespace — café.\n".encode()
        status, result = self.request("POST", "/api/ingest", self.fields,
                                      documents=[("source.md", original)])
        self.assertEqual(status, 200, result)
        self.assertEqual(result["created_article"], {"created": True, "slug": "devops-container-hosting"})
        self.assertTrue(result["article_content_written"])
        self.assertTrue(result["refresh"]["ok"])
        source = result["saved"][0]["path"]
        self.assertTrue(source.startswith("raw/inbox/devops/"))
        self.assertEqual((self.root / source).read_bytes(), original)
        record = load_catalog(self.root, require_explicit=True).by_slug["devops-container-hosting"]
        self.assertEqual(record.primary_placement, "devops/containers")
        self.assertEqual(record.classification, "internal")
        self.assertEqual(srv.fm_val(record.frontmatter, "render_raw_html"), "false")
        self.assertEqual(record.body, self.fields["article_markdown"])
        self.assertEqual(set(record.sources), {source, self.fields["external_urls"]})
        self.assertEqual(record.raw_documents, (source,))
        self.assertNotIn("stale_since:", record.frontmatter)
        status, listing = self.request("GET", "/api/articles")
        self.assertEqual(listing["articles"][0]["sources"], list(record.sources))
        status, appended = self.request("POST", "/api/ingest", {
            "target_slug": record.slug, "space": "devops", "section": "containers",
            "steward": "transpara", "external_urls": "https://example.test/followup"})
        self.assertEqual(status, 200, appended)
        self.assertFalse(appended["article_content_written"])
        updated = load_catalog(self.root).by_slug[record.slug]
        self.assertEqual(updated.body, record.body)
        self.assertEqual(len(updated.sources), 3)
        self.assertIn("stale_since:", updated.frontmatter)

    def test_validation_refusals_save_nothing(self):
        variants = [
            {"space": "platform", "section": "architecture"},
            {"section": "invented"}, {"steward": "transpara-ai"},
            {"name": ""}, {"name": "!!!"}, {"name": "Two\nlines"},
            {"article_markdown": ""}, {"article_markdown": "---\norg: transpara-ai\n---\n"},
            {"source_authority": "invented"}, {"external_urls": ""},
            {"new_investigation": "true"}, {"target_slug": "existing"},
            {"new_article": "false"},
        ]
        for changes in variants:
            with self.subTest(changes=changes):
                status, result = self.request("POST", "/api/ingest", self.fields | changes)
                self.assertEqual(status, 422, result)
                self.assertEqual(self.snapshot(), {})

    def test_duplicate_and_retired_alias_collisions_are_write_free(self):
        self.assertEqual(self.request("POST", "/api/ingest", self.fields)[0], 200)
        before = self.snapshot()
        for name in ("Container hosting", "Container-hosting", "DevOps Container Hosting"):
            status, result = self.request("POST", "/api/ingest", self.fields | {"name": name})
            self.assertEqual(status, 422, result)
            self.assertEqual(self.snapshot(), before)
        path = self.root / "wiki/devops-container-hosting.md"
        path.write_text(path.read_text().replace("sources:",
                        'retired_on: 2026-09-07\naliases: [Old Hosting]\nsources:', 1))
        before = self.snapshot()
        status, result = self.request("POST", "/api/ingest", self.fields | {"name": "Old Hosting"})
        self.assertEqual(status, 422, result)
        self.assertEqual(self.snapshot(), before)

    def test_authorization_and_secret_quarantine_apply_before_writes(self):
        self.assertEqual(self.request("POST", "/api/ingest", self.fields, authorized=False)[0], 401)
        secret = "AK" + "IA" + "A" * 16
        for field in ("article_markdown", "name", "source_authority", "note"):
            with self.subTest(field=field):
                status, result = self.request("POST", "/api/ingest", self.fields | {field: secret})
                self.assertEqual(status, 422, result)
                self.assertNotIn(secret, json.dumps(result))
                self.assertEqual(self.snapshot(), {})
        status, result = self.request("POST", "/api/ingest", self.fields,
                                      documents=[("source.txt", secret.encode())])
        self.assertEqual(status, 422, result)
        self.assertNotIn(secret, json.dumps(result))
        self.assertEqual(self.snapshot(), {})

    def test_rebuild_failure_reports_saved_article_for_recovery(self):
        with mock.patch.object(srv, "run_refresh_unlocked", return_value={"ok": False}):
            status, result = self.request("POST", "/api/ingest", self.fields)
        self.assertEqual(status, 500, result)
        self.assertTrue(result["created_article"]["created"])
        self.assertTrue((self.root / "wiki/devops-container-hosting.md").is_file())
        ledger = json.loads((self.root / "compile/ingest-ledger.jsonl").read_text())
        self.assertEqual(ledger["rebuild"], "failed")

    def test_corpus_markdown_renders_code_and_links_but_escapes_raw_html(self):
        import build_site
        rendered, toc = build_site.to_html(
            '# Procedure\n\n<script>alert(1)</script>\n\n<img src=x onerror=alert(1)>\n\n'
            '> Operational note\n\n```bash\necho "<host>"\n```\n\n'
            '[Unsafe](javascript:alert(1))\n\n[Source](https://example.test/source)\n\n'
            '[Attributes](https://example.test/){: onmouseover="alert(1)"}',
            allow_raw_html=False)
        self.assertNotIn('<script>', rendered)
        self.assertNotIn('<img', rendered)
        self.assertNotIn('href="javascript:', rendered)
        self.assertIn('&lt;script&gt;', rendered)
        self.assertIn('<blockquote>', rendered)
        self.assertIn('&lt;host&gt;', rendered)
        self.assertIn('href="https://example.test/source"', rendered)
        self.assertNotRegex(rendered, r'<[^>]+onmouseover=')
        self.assertEqual(toc[0]['name'], 'Procedure')


if __name__ == "__main__":
    unittest.main()
