"""Exercise bounded snapshot reads and the private, proposal-only HTTP boundary."""
import copy
import http.client
import json
import os
import pathlib
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ingest_server as server
import terminology_api as api


def snapshot():
    return {"schema_version": 1, "dictionary_version": "0.1.0",
            "dictionary_digest": "a" * 64, "reference_status": "unassessed",
            "terms": [], "decisions": [], "candidates": [{
                "id": "candidate-one", "term": "flux adapter", "normalized": "flux adapter",
                "scope": {"repo": "transpara-ai/example", "product": "example"},
                "status": "pending", "reference_status": "unassessed",
                "observations": [{"path": "guide.md", "line": 2, "sentence": "Use the flux adapter."}]}]}


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = pathlib.Path(self.temp.name) / "snapshot.json"
        self.path.write_text(json.dumps(snapshot()))
        self.env = patch.dict(os.environ, {api.SNAPSHOT_ENV: str(self.path)})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.temp.cleanup()

    def test_export_is_read_without_changing_source_or_claiming_conformance(self):
        before = self.path.read_bytes()
        self.assertEqual(api.load_snapshot()["conformance"], "not_assessed")
        self.assertEqual(self.path.read_bytes(), before)

    def test_current_occurrence_fields_and_hash_pass_through_unchanged(self):
        data = snapshot()
        evidence = data["candidates"][0]["observations"][0]
        evidence.update({"term": "flux adapter", "start": 8, "end": 20,
                         "context_binding": "transpara-source-occurrence-v1",
                         "context_digest": "b" * 64})
        self.path.write_text(json.dumps(data))
        self.assertEqual(api.load_snapshot()["candidates"][0]["observations"],
                         data["candidates"][0]["observations"])

    def test_invalid_exports_are_refused(self):
        broken = [[], {"schema_version": True}, snapshot(), snapshot(), snapshot()]
        broken[2]["dictionary_digest"] = "not-a-digest"
        broken[3]["candidates"][0]["observations"][0]["line"] = True
        broken[4]["candidates"].append(copy.deepcopy(broken[4]["candidates"][0]))
        for data in broken:
            with self.subTest(data=data):
                self.path.write_text(json.dumps(data))
                with self.assertRaises(api.SnapshotUnavailable):
                    api.load_snapshot()
        self.path.write_bytes(b"\xff")
        with self.assertRaises(api.SnapshotUnavailable):
            api.load_snapshot()

    def test_missing_oversize_and_nonregular_file_are_bounded(self):
        with patch.dict(os.environ, {api.SNAPSHOT_ENV: ""}):
            with self.assertRaisesRegex(api.SnapshotUnavailable, "No terminology"):
                api.load_snapshot()
        with patch.dict(os.environ, {api.SNAPSHOT_ENV: "relative.json"}):
            with self.assertRaisesRegex(api.SnapshotUnavailable, "absolute"):
                api.load_snapshot()
        with patch.object(api, "MAX_BYTES", 10):
            with self.assertRaisesRegex(api.SnapshotUnavailable, "limit"):
                api.load_snapshot()
        fifo = pathlib.Path(self.temp.name) / "fifo"
        os.mkfifo(fifo)
        with patch.dict(os.environ, {api.SNAPSHOT_ENV: str(fifo)}):
            with self.assertRaisesRegex(api.SnapshotUnavailable, "regular file"):
                api.load_snapshot()

    def test_errors_do_not_reveal_configured_private_path(self):
        with patch.dict(os.environ, {api.SNAPSHOT_ENV: str(self.path) + "-absent"}):
            with self.assertRaises(api.SnapshotUnavailable) as caught:
                api.load_snapshot()
        self.assertNotIn(self.temp.name, str(caught.exception))

    def test_recognized_secrets_are_refused_in_raw_and_escaped_json(self):
        secret = "ghp_" + "A" * 36
        data = snapshot()
        data["candidates"][0]["observations"][0]["sentence"] = "Use " + secret
        raw = json.dumps(data)
        for payload in (raw, raw.replace("ghp_", "\\u0067hp_")):
            with self.subTest(escaped=payload != raw):
                self.path.write_text(payload)
                with self.assertRaisesRegex(api.SnapshotUnavailable, "content check") as caught:
                    api.load_snapshot()
                self.assertNotIn(secret, str(caught.exception))
                self.assertNotIn(self.temp.name, str(caught.exception))

    def test_http_authoring_guard_profiles_and_no_mutation(self):
        with patch.object(server.IngestHandler, "log_message"):
            instance = server.ThreadingHTTPServer(("127.0.0.1", 0), server.IngestHandler)
            thread = threading.Thread(target=instance.serve_forever, daemon=True)
            thread.start()
            connection = http.client.HTTPConnection("127.0.0.1", instance.server_port, timeout=3)
            def request(method, route="/api/terminology/snapshot", headers=None):
                connection.request(method, route, body=b"" if method == "POST" else None, headers=headers or {})
                response = connection.getresponse()
                data = response.read()
                return response, json.loads(data)
            try:
                with patch.dict(os.environ, {"KNOWLEDGE_HUB_PROFILE": "authoring-local",
                                             server.AUTHORING_TOKEN_ENV: "fixture-token"}):
                    response, _ = request("GET")
                    self.assertEqual(response.status, 401)
                    headers = {server.AUTHORING_TOKEN_HEADER: "fixture-token"}
                    before = self.path.read_bytes()
                    response, data = request("GET", headers=headers)
                    self.assertEqual(response.status, 200)
                    self.assertEqual(response.getheader("Cache-Control"), "no-store")
                    self.assertEqual(data["dictionary_digest"], "a" * 64)
                    response, _ = request("GET", "/api/terminology/snapshot?path=/etc/passwd", headers)
                    self.assertEqual(response.status, 404)
                    for route in ("/api/terminology/snapshot", "/api/terminology/approve", "/api/terminology/publish"):
                        response, _ = request("POST", route, headers)
                        self.assertEqual(response.status, 405)
                    self.assertEqual(self.path.read_bytes(), before)
                    with patch.dict(os.environ, {"KNOWLEDGE_HUB_PROFILE": "company-internal"}):
                        response, _ = request("GET", headers=headers)
                        self.assertEqual(response.status, 404)
                    data = snapshot()
                    secret = "ghp_" + "A" * 36
                    data["candidates"][0]["observations"][0]["sentence"] = secret
                    self.path.write_text(json.dumps(data))
                    response, data = request("GET", headers=headers)
                    self.assertEqual(response.status, 503)
                    self.assertNotIn(secret, data["error"])
                    self.assertNotIn(self.temp.name, data["error"])
            finally:
                connection.close()
                instance.shutdown()
                instance.server_close()
                thread.join(timeout=3)

    def test_remote_readers_match_existing_evidence_principal_and_grant_checks(self):
        class RemoteHandler(server.IngestHandler):
            def setup(self):
                super().setup()
                # Keep real HTTP handling while modeling a non-loopback peer.
                self.client_address = ("198.51.100.24", self.client_address[1])

        with patch.object(RemoteHandler, "log_message"):
            instance = server.ThreadingHTTPServer(("127.0.0.1", 0), RemoteHandler)
            thread = threading.Thread(target=instance.serve_forever, daemon=True)
            thread.start()
            connection = http.client.HTTPConnection("127.0.0.1", instance.server_port, timeout=3)
            def request(headers):
                connection.request("GET", "/api/terminology/snapshot", headers=headers)
                response = connection.getresponse()
                return response.status, json.loads(response.read())
            headers = {server.AUTHORING_TOKEN_HEADER: "fixture-token", "X-Forwarded-User": "claimed-user"}
            try:
                with patch.dict(os.environ, {"KNOWLEDGE_HUB_PROFILE": "authoring-local",
                                             server.AUTHORING_TOKEN_ENV: "fixture-token"}), \
                     patch.object(server.terminology_api, "load_snapshot", wraps=api.load_snapshot) as load:
                    with patch.object(server.authoring_profile, "settings", return_value=None):
                        self.assertEqual(request(headers)[0], 401)
                        load.assert_not_called()
                    # The existing principal verifier remains the identity source.
                    config = ("http://127.0.0.1/userinfo", "http://127.0.0.1", self.path)
                    with patch.object(server.authoring_profile, "settings", return_value=config), \
                         patch.object(server.authoring_profile, "principal", return_value="verified-principal"), \
                         patch.object(server.authoring_profile, "granted", return_value=True):
                        self.assertEqual(request(headers)[0], 200)
                        self.assertEqual(request({})[0], 200)
                        self.assertEqual(load.call_count, 2)
                    load.reset_mock()
                    with patch.object(server.authoring_profile, "settings", side_effect=server.authoring_profile.ProfileUnavailable("private configuration detail")):
                        status, data = request(headers)
                        self.assertEqual(status, 503)
                        self.assertNotIn("private configuration detail", data["error"])
                        load.assert_not_called()
            finally:
                connection.close()
                instance.shutdown()
                instance.server_close()
                thread.join(timeout=3)


if __name__ == "__main__":
    unittest.main()
