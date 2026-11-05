"""Exercise private service framing, bounded durable jobs, and actor isolation."""
import base64
from contextlib import nullcontext
import hashlib
import io
from email.message import Message
import http.client
import http.server
import json
import os
from pathlib import Path
import socketserver
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

import terminology_client as client
from ask_common import AskError


def source():
    return {'type': 'url', 'url': 'https://example.com/guide'}


def capture(request, *, cancelled):
    text = 'Use the valve.'
    return {'documents': [{'label': 'guide', 'text': text,
                           'source_sha256': hashlib.sha256(text.encode()).hexdigest()}],
            'source': {'kind': 'url', 'url': request['url']},
            'coverage': {'complete': True, 'files_captured': 1}, 'skipped': []}


def backend(method, route, actor, payload, **kwargs):
    return {'conformance': 'not_assessed', 'documents': [
        {'label': doc['label'], 'original': doc['text'], 'findings': []}
        for doc in payload['documents']], 'rewrite_requested': payload['rewrite']}


class JobTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.jobs = client.Jobs(self.root, capture=capture, backend=backend,
                               model=lambda documents, actor: None, start=False)

    def tearDown(self):
        self.temp.cleanup()

    def test_durable_actor_owned_report_preserves_original_and_provenance(self):
        job = self.jobs.submit('alice', {'source': source()})
        self.assertEqual(job['state'], 'queued')
        self.assertTrue(self.jobs.run_one())
        reopened = client.Jobs(self.root, start=False).get('alice', job['id'])
        self.assertEqual(reopened['state'], 'complete')
        self.assertEqual(self.jobs.latest('alice'), {'id': job['id'], 'state': 'complete'})
        self.assertIsNone(self.jobs.latest('bob'))
        self.assertEqual(reopened['report']['documents'][0]['original'], 'Use the valve.')
        self.assertTrue(reopened['report']['coverage']['complete'])
        self.assertEqual(reopened['report']['conformance'], 'not_assessed')
        for action in (self.jobs.get, self.jobs.cancel):
            with self.assertRaises(AskError) as error:
                action('bob', job['id'])
            self.assertEqual(error.exception.status, 404)
        self.assertEqual(self.jobs.path.stat().st_mode & 0o777, 0o600)

    def test_global_queue_per_actor_and_worker_concurrency_limits(self):
        self.jobs.submit('alice', {'source': source()})
        with self.assertRaises(AskError) as error:
            self.jobs.submit('alice', {'source': source()})
        self.assertEqual(error.exception.status, 429)
        for number in range(7):
            self.jobs.submit('actor-' + str(number), {'source': source()})
        with self.assertRaises(AskError):
            self.jobs.submit('ninth', {'source': source()})
        self.assertIsNotNone(self.jobs.claim())
        self.assertIsNotNone(self.jobs.claim())
        self.assertIsNone(self.jobs.claim())

    def test_capture_and_input_limits_do_not_grant_file_or_private_network_access(self):
        for request in ({'source': {'type': 'url', 'url': 'file:///etc/passwd'}},
                        {'source': {'type': 'url', 'url': 'https://127.0.0.1/'}},
                        {'source': {**source(), 'credentials': 'attacker'}},
                        {'source': source(), 'publish': True}):
            with self.subTest(request=request), self.assertRaises(AskError):
                self.jobs.submit('alice', request)
        with self.jobs.connect() as db:
            self.assertEqual(db.execute('SELECT count(*) FROM term_jobs').fetchone()[0], 0)

    def test_cancelled_job_never_starts_and_running_cancel_discards_late_report(self):
        job = self.jobs.submit('alice', {'source': source()})
        self.assertEqual(self.jobs.cancel('alice', job['id'])['state'], 'cancelled')
        self.assertFalse(self.jobs.run_one())
        def stop_capture(request, *, cancelled):
            self.jobs.cancel('alice', running['id'])
            self.assertTrue(cancelled())
            return capture(request, cancelled=cancelled)
        self.jobs.capture = stop_capture
        running = self.jobs.submit('alice', {'source': source()})
        self.jobs.run_one()
        result = self.jobs.get('alice', running['id'])
        self.assertEqual(result['state'], 'cancelled')
        self.assertNotIn('report', result)

    def test_interrupted_worker_fails_lease_instead_of_replaying_model_or_effect(self):
        job = self.jobs.submit('alice', {'source': source()})
        self.jobs.claim()
        with self.jobs.connect() as db:
            db.execute('UPDATE term_jobs SET lease=0 WHERE id=?', (job['id'],))
        result = self.jobs.get('alice', job['id'])
        self.assertEqual(result['state'], 'failed')
        self.assertIn('stopped', result['error'])

    def test_model_failure_retains_diagnostics_but_cannot_claim_translation(self):
        def unavailable(*args):
            raise ValueError('a private diagnostic')
        self.jobs.model = unavailable
        job = self.jobs.submit('alice', {'source': source(), 'rewrite': True})
        self.jobs.run_one()
        result = self.jobs.get('alice', job['id'])
        self.assertEqual(result['state'], 'complete')
        self.assertEqual(result['report']['rewrite']['status'], 'unavailable')
        self.assertNotIn('private diagnostic', json.dumps(result))
        self.assertEqual(result['report']['documents'][0]['original'], 'Use the valve.')

    def test_secret_or_oversized_report_is_never_retained(self):
        for text in ('ghp_' + 'A' * 36, 'A' * (client.MAX_RESPONSE + 1)):
            self.jobs.backend = lambda *args, **kwargs: {'private_text': text}
            job = self.jobs.submit('alice', {'source': source()})
            self.jobs.run_one()
            result = self.jobs.get('alice', job['id'])
            self.assertEqual(result['state'], 'failed')
            self.assertNotIn('report', result)
            self.assertNotIn(text, json.dumps(result))

    def test_retention_and_count_limits_keep_current_records_bounded(self):
        with self.jobs.connect() as db:
            for number in range(105):
                db.execute('INSERT INTO term_jobs(id,actor,state,request,report,created,updated) VALUES(?,?,?,?,?,?,?)',
                           (str(number), 'alice', 'complete', '{}', '{}', time.time(), time.time()))
            db.execute('INSERT INTO term_jobs(id,actor,state,request,created,updated) VALUES(?,?,?,?,?,?)',
                       ('old', 'alice', 'failed', '{}', 0, 0))
            self.jobs.cleanup(db)
            self.assertEqual(db.execute('SELECT count(*) FROM term_jobs').fetchone()[0], 100)
            self.assertIsNone(db.execute("SELECT id FROM term_jobs WHERE id='old'").fetchone())

    def test_state_must_not_follow_symlink_or_enter_published_tree(self):
        with self.assertRaises(AskError):
            client.Jobs(self.root, path=self.root / 'wiki' / 'jobs.sqlite3', start=False)
        link = self.root / '.private' / 'link'
        link.symlink_to(self.jobs.path)
        with self.assertRaises(AskError):
            client.Jobs(self.root, path=link, start=False)


class UnixServer(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    daemon_threads = True


class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.socket = str(Path(self.temp.name) / 'authority.sock')
        self.seen = []
        outer = self
        class Handler(http.server.BaseHTTPRequestHandler):
            def do_POST(self):
                body = self.rfile.read(int(self.headers['Content-Length']))
                outer.seen.append((self.path, self.headers['X-Term-Actor'], json.loads(body)))
                self.send_response(outer.status)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                try:
                    self.wfile.write(outer.body)
                except BrokenPipeError:
                    pass
            def log_message(self, *args):
                pass
        self.body, self.status = b'{"ok":true}', 200
        self.server = UnixServer(self.socket, Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.env = patch.dict(os.environ, {client.SOCKET_ENV: self.socket})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.server.shutdown(); self.server.server_close(); self.thread.join()
        self.temp.cleanup()

    def test_fixed_socket_actor_and_routes_never_allow_arbitrary_endpoint(self):
        self.assertTrue(client.service('POST', '/proposals', 'verified-actor', {'proposal': {}})['ok'])
        self.assertEqual(self.seen, [('/proposals', 'verified-actor', {'proposal': {}})])
        for route in ('https://evil.example/', '/trust/enroll', '/../../etc/passwd'):
            with self.assertRaises(AskError):
                client.service('POST', route, 'verified-actor', {})
        with self.assertRaises(AskError):
            client.service('POST', '/publish', 'actor\r\nInjected: yes', {})

    def test_private_errors_and_oversized_responses_are_not_relayed(self):
        self.body, self.status = b'{"error":"/private/key.pem is secret"}', 403
        with self.assertRaises(AskError) as error:
            client.service('POST', '/publish', 'verified-actor', {})
        self.assertEqual(error.exception.status, 403)
        self.assertNotIn('key.pem', str(error.exception))
        self.body, self.status = b'A' * (client.MAX_SERVICE_RESPONSE + 1), 200
        with self.assertRaises(AskError):
            client.service('POST', '/publish', 'verified-actor', {})


class RewriteModelTests(unittest.TestCase):
    def test_provider_receives_only_prose_and_python_is_merged_unchanged(self):
        documents = [{'label': 'src/logic.py', 'text': '# A Python comment.\nvalue = 1\n'},
                     {'label': 'README.md', 'text': 'Utilize the valve.'},
                     {'label': 'https://example.com/tool.py?version=1', 'text': 'def main(): pass\n'}]
        with patch.dict(os.environ, {'KNOWLEDGE_HUB_REVIEW_CONFIG': '/fixed/model.json'}), \
             patch('knowledge_store.host_json', return_value={'author': {'provider': 'fixture', 'model': 'fixture-model'}}), \
             patch('ask.admission', return_value=nullcontext()), \
             patch('ask.service', return_value={'documents': [{'label': 'README.md', 'text': 'Use the valve.'}]}) as provider:
            result = client.rewrite_model(documents, 'alice')
        sent = provider.call_args.args[1]['context'][0]['documents']
        self.assertEqual(sent, [{'label': 'README.md', 'text': 'Utilize the valve.'}])
        self.assertEqual(result['documents'], [documents[0], {'label': 'README.md', 'text': 'Use the valve.'}, documents[2]])
        self.assertEqual(provider.call_count, 1)

    def test_rewrite_result_accepts_scanner_label_bound_and_rejects_larger_identity(self):
        from ask_common import validate_result
        result = {'documents': [{'label': 'a' * 512, 'text': 'Use the valve.'}]}
        self.assertEqual(validate_result('terminology-rewrite', result), result)
        for label in ('', 'a' * 513):
            with self.subTest(length=len(label)), self.assertRaises(AskError):
                validate_result('terminology-rewrite', {'documents': [{'label': label, 'text': 'Use the valve.'}]})

    def test_python_only_never_calls_provider_or_claims_rewrite(self):
        with patch.dict(os.environ, {'KNOWLEDGE_HUB_REVIEW_CONFIG': '/fixed/model.json'}), \
             patch('ask.service') as provider, patch('knowledge_store.host_json') as settings:
            self.assertIsNone(client.rewrite_model([{'label': 'logic.py', 'text': 'value = 1\n'}], 'alice'))
        provider.assert_not_called(); settings.assert_not_called()


class PublicProofTests(unittest.TestCase):
    def proof(self, enrollment=False):
        def encode(raw):
            return base64.urlsafe_b64encode(raw).decode().rstrip('=')
        response = {'clientDataJSON': encode(json.dumps({'type': 'webauthn.create' if enrollment else 'webauthn.get',
            'challenge': encode(bytes(range(32))), 'origin': 'https://wiki.example', 'crossOrigin': False}).encode())}
        if enrollment:
            response['attestationObject'] = encode(bytes(range(256)))
        else:
            response.update(authenticatorData=encode(bytes(range(37))), signature=encode(bytes(range(64))), userHandle=None)
        credential = {'id': encode(bytes(range(16))), 'rawId': encode(bytes(range(16))),
            'type': 'public-key', 'response': response, 'clientExtensionResults': {}}
        return {'credential': credential} if enrollment else {'stage_id': 'c' * 32, 'credential': credential}

    def handler(self, path, payload):
        from types import SimpleNamespace
        body = json.dumps(payload).encode()
        headers = Message()
        headers['Content-Type'] = 'application/json'
        headers['Content-Length'] = str(len(body))
        return SimpleNamespace(path='/api/terminology/' + path, command='POST', headers=headers, rfile=io.BytesIO(body))

    def test_public_assertion_and_attestation_cross_the_proxy_without_prose_classifier(self):
        # These synthetic public envelopes exercise the HTTP adapter only. Real
        # signature verification belongs to the independent authority's tests.
        from ingest_ops import quarantine_payload, OpRefused
        for route, enrollment in (('publish', False), ('enrollment/finish', True)):
            payload = self.proof(enrollment)
            with self.subTest(route=route):
                with self.assertRaises(OpRefused):
                    quarantine_payload(json.dumps(payload).encode())
                with patch.object(client, 'service', return_value={'accepted': True}) as backend:
                    status, result = client.handle(self.handler(route, payload), Path('/unused'), 'verified-account')
                self.assertEqual(status, 200)
                self.assertTrue(result['accepted'])
                backend.assert_called_once_with('POST', '/' + route, 'verified-account', payload)

    def test_browser_client_data_extension_is_quarantined_without_breaking_valid_ceremony(self):
        payload = self.proof()
        response = payload['credential']['response']
        raw = base64.urlsafe_b64decode(response['clientDataJSON'] + '=' * (-len(response['clientDataJSON']) % 4))
        data = json.loads(raw)
        data['other_keys_can_be_added_here'] = 'Do not compare client data against a template.'
        def encode():
            response['clientDataJSON'] = base64.urlsafe_b64encode(json.dumps(data).encode()).decode().rstrip('=')
        encode()
        client.validate_public_proof('publish', payload)
        data['unexpected_private_text'] = 'ghp_' + 'A' * 36
        encode()
        with self.assertRaises(AskError):
            client.validate_public_proof('publish', payload)

    def test_opaque_public_proof_exception_rejects_other_fields_and_malformed_bytes(self):
        bad = []
        payload = self.proof(); payload['token'] = 'not-public-prose'; bad.append(payload)
        payload = self.proof(); payload['credential']['response']['signature'] = '+++='; bad.append(payload)
        payload = self.proof(); payload['credential']['response']['extra'] = 'arbitrary text'; bad.append(payload)
        payload = self.proof(); payload['credential']['clientExtensionResults'] = {'secret': 'arbitrary text'}; bad.append(payload)
        payload = self.proof(); payload['credential']['id'] = 'different'; bad.append(payload)
        for payload in bad:
            with self.subTest(payload=payload), patch.object(client, 'service') as backend:
                with self.assertRaises(AskError):
                    client.handle(self.handler('publish', payload), Path('/unused'), 'verified-account')
                backend.assert_not_called()


class HttpGuardTests(unittest.TestCase):
    def test_grant_identity_and_same_origin_all_precede_authority_calls(self):
        import ingest_server as ingest
        calls = []
        def handle(handler, root, actor):
            calls.append((handler.command, actor))
            # An attacker-supplied identity header is not passed as the actor.
            return 200, {'actor': actor}
        config = ('http://127.0.0.1:4180/oauth2/userinfo', 'https://wiki.example', Path('/not-used'))
        with patch.object(ingest.IngestHandler, 'log_message'), \
             patch.dict(os.environ, {client.SOCKET_ENV: '/fixed/authority.sock',
                 ingest.AUTHORING_TOKEN_ENV: 'fixture-token', 'KNOWLEDGE_HUB_PROFILE': 'authoring-local'}), \
             patch('authoring_profile.settings', return_value=config), \
             patch('knowledge_api.actor', return_value='verified-account'), \
             patch.object(client, 'handle', side_effect=handle):
            server = ingest.ThreadingHTTPServer(('127.0.0.1', 0), ingest.IngestHandler)
            worker = threading.Thread(target=server.serve_forever, daemon=True)
            worker.start()
            conn = http.client.HTTPConnection('127.0.0.1', server.server_port, timeout=3)
            def request(headers):
                conn.request('POST', '/api/terminology/proposals', body=b'{}', headers={
                    'Content-Type': 'application/json', **headers})
                reply = conn.getresponse()
                return reply.status, json.loads(reply.read())
            try:
                common = {ingest.AUTHORING_TOKEN_HEADER: 'fixture-token'}
                for extra in ({}, {'Origin': 'https://evil.example', 'X-Wiki-Profile-Action': '1'},
                              {'Origin': 'https://wiki.example'},
                              {'Origin': 'https://wiki.example', 'X-Wiki-Profile-Action': '1', 'Sec-Fetch-Site': 'cross-site'}):
                    status, _ = request({**common, **extra})
                    self.assertEqual(status, 403)
                self.assertEqual(calls, [])
                status, result = request({**common, 'Origin': 'https://wiki.example',
                    'X-Wiki-Profile-Action': '1', 'X-Term-Actor': 'attacker'})
                self.assertEqual(status, 200)
                self.assertEqual(result, {'actor': 'verified-account'})
                self.assertEqual(calls, [('POST', 'verified-account')])
                with patch('knowledge_api.actor', side_effect=AskError('Sign in', 401)):
                    status, _ = request({**common, 'Origin': 'https://wiki.example', 'X-Wiki-Profile-Action': '1'})
                    self.assertEqual(status, 401)
                self.assertEqual(len(calls), 1)
            finally:
                conn.close(); server.shutdown(); server.server_close(); worker.join()


if __name__ == '__main__':
    unittest.main()
