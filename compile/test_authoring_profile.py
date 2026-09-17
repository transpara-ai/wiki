"""Adversarial HTTP integration tests; synthetic sessions never reach production."""
import contextlib
import http.client
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import threading
import unittest
from unittest import mock

import authoring_profile as profile
import ingest_server as srv


class SessionVerifier(BaseHTTPRequestHandler):
    mode = 'normal'
    hits = []

    def log_message(self, *args):
        pass

    def do_GET(self):
        type(self).hits.append(dict(self.headers))
        cookie = self.headers.get('Cookie', '')
        users = {'session=alice': 'subject-alice', 'session=alice-new': 'subject-alice',
                 'session=bob': 'subject-bob'}
        status = 200 if cookie in users else 401
        body = json.dumps({'user': users.get(cookie), 'email': 'same@example.test'}).encode()
        if self.mode == 'redirect':
            status = 302
        elif self.mode == 'empty':
            body = b'{}'
        elif self.mode == 'html':
            body = b'<html>Sign in</html>'
        elif self.mode == 'large':
            body = b'x' * 65537
        elif self.mode == 'failure':
            status = 503
        self.send_response(status)
        if status == 302:
            self.send_header('Location', '/other')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)


@contextlib.contextmanager
def running(handler):
    server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        self.root = Path(self.stack.enter_context(tempfile.TemporaryDirectory()))
        self.verifier = self.stack.enter_context(running(SessionVerifier))
        SessionVerifier.mode, SessionVerifier.hits = 'normal', []
        self.env = {
            srv.AUTHORING_TOKEN_ENV: 'example-authoring-value',
            srv.ALLOWED_HOSTS_ENV: 'wiki.example',
            'KNOWLEDGE_HUB_PROFILE_USERINFO_URL': 'http://127.0.0.1:%s/oauth2/userinfo' % self.verifier.server_port,
            'KNOWLEDGE_HUB_PROFILE_ORIGIN': 'https://wiki.example',
            'KNOWLEDGE_HUB_PROFILE_STORE': str(self.root / 'private' / 'grants.sqlite3'),
        }
        self.stack.enter_context(mock.patch.dict(os.environ, self.env))
        self.refresh = self.stack.enter_context(mock.patch.object(srv, 'run_refresh', return_value={'ok': True}))
        self.stack.enter_context(mock.patch.object(srv.IngestHandler, 'log_message'))
        self.server = self.stack.enter_context(running(srv.IngestHandler))

    def call(self, method='GET', path='/api/authoring-profile', cookie='session=alice', token=None, **overrides):
        headers = {'Host': 'wiki.example', 'Cookie': cookie,
                   'Origin': 'https://wiki.example', 'X-Wiki-Profile-Action': '1',
                   'Sec-Fetch-Site': 'same-origin'}
        if token is not None:
            headers[srv.AUTHORING_TOKEN_HEADER] = token
        for key, value in overrides.items():
            if value is None:
                headers.pop(key, None)
            else:
                headers[key] = value
        c = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=8)
        try:
            c.request(method, path, headers=headers)
            response = c.getresponse()
            body = response.read()
            self.assertEqual(response.getheader('Cache-Control'), 'no-store')
            self.assertIsNone(response.getheader('Set-Cookie'))
            self.assertNotIn(self.env[srv.AUTHORING_TOKEN_ENV].encode(), body)
            return response.status, json.loads(body)
        finally:
            c.close()

    def enroll(self):
        code, data = self.call('POST', token=self.env[srv.AUTHORING_TOKEN_ENV])
        self.assertEqual(code, 200)
        self.assertTrue(data['authoring'])

    def test_enroll_revisit_new_session_and_new_server_without_token(self):
        self.assertFalse(self.call()[1]['authoring'])
        self.enroll()
        self.assertTrue(self.call(cookie='session=alice-new')[1]['authoring'])
        with running(srv.IngestHandler) as restarted:
            original = self.server
            self.server = restarted
            try:
                self.assertEqual(self.call('POST', '/api/rebuild', cookie='session=alice-new')[0], 200)
            finally:
                self.server = original
        self.assertEqual(self.refresh.call_count, 1)

    def test_other_subject_same_email_has_no_access(self):
        self.enroll()
        self.assertFalse(self.call(cookie='session=bob')[1]['authoring'])
        self.assertEqual(self.call('POST', '/api/rebuild', cookie='session=bob')[0], 401)
        self.refresh.assert_not_called()

    def test_logged_out_and_forged_forwarded_identity_denied(self):
        self.enroll()
        for cookie in ['', 'session=forged']:
            code, data = self.call('POST', '/api/rebuild', cookie=cookie,
                                  **{'X-Forwarded-User': 'subject-alice', 'X-Auth-Request-User': 'subject-alice'})
            self.assertEqual(code, 401)
        self.refresh.assert_not_called()

    def test_invalid_token_and_no_session_cannot_enroll(self):
        for token, cookie in [('wrong', 'session=alice'), ('', 'session=alice'),
                              (self.env[srv.AUTHORING_TOKEN_ENV], '')]:
            self.assertEqual(self.call('POST', token=token, cookie=cookie)[0], 401)
        self.assertFalse(self.call()[1]['authoring'])

    def test_csrf_denied_for_enroll_mutation_and_forget(self):
        self.enroll()
        for overrides in [{'Origin': None}, {'Origin': 'https://evil.example'},
                          {'Origin': 'https://wiki.example.evil'}, {'Origin': 'null'},
                          {'X-Wiki-Profile-Action': None}, {'Sec-Fetch-Site': 'cross-site'}]:
            for path in ['/api/rebuild', '/api/authoring-profile/forget']:
                self.assertIn(self.call('POST', path, **overrides)[0], (401, 403))
            self.assertEqual(self.call('POST', token=self.env[srv.AUTHORING_TOKEN_ENV], **overrides)[0], 403)
        self.assertTrue(self.call()[1]['authoring'])
        self.refresh.assert_not_called()

    def test_forget_only_own_grant_and_reenroll(self):
        self.enroll()
        self.assertEqual(self.call('POST', '/api/authoring-profile/forget', cookie='session=bob')[0], 200)
        self.assertTrue(self.call()[1]['authoring'])
        self.assertFalse(self.call('POST', '/api/authoring-profile/forget')[1]['authoring'])
        self.assertEqual(self.call('POST', '/api/rebuild')[0], 401)
        self.enroll()
        self.assertEqual(self.call('POST', '/api/rebuild')[0], 200)

    def test_rotation_invalidates_saved_grants(self):
        self.enroll()
        with mock.patch.dict(os.environ, {srv.AUTHORING_TOKEN_ENV: 'example-rotated-value'}):
            self.assertFalse(self.call()[1]['authoring'])
            self.assertEqual(self.call('POST', '/api/rebuild')[0], 401)

    def test_profile_file_private_and_contains_no_raw_identity_or_credentials(self):
        self.enroll()
        path = profile.settings()[2]
        self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        self.assertEqual(path.parent.stat().st_mode & 0o777, 0o700)
        for text in ['subject-alice', 'session=alice', 'same@example.test', self.env[srv.AUTHORING_TOKEN_ENV]]:
            self.assertNotIn(text.encode(), path.read_bytes())

    def test_corrupt_proof_and_database_fail_closed(self):
        self.enroll()
        path = profile.settings()[2]
        with sqlite3.connect(path) as db:
            db.execute("UPDATE grants SET proof='forged'")
        self.assertEqual(self.call('POST', '/api/rebuild')[0], 401)
        path.write_bytes(b'not sqlite')
        self.assertEqual(self.call('POST', '/api/rebuild')[0], 401)
        self.assertEqual(self.call('POST', token=self.env[srv.AUTHORING_TOKEN_ENV])[0], 503)

    def test_verifier_bad_responses_and_redirect_fail_closed(self):
        self.enroll()
        for mode in ['redirect', 'empty', 'html', 'large', 'failure']:
            SessionVerifier.mode = mode
            self.assertEqual(self.call('POST', '/api/rebuild')[0], 401, mode)
        self.refresh.assert_not_called()

    def test_verifier_receives_only_cookie_not_authoring_or_forged_identity(self):
        self.enroll()
        last = SessionVerifier.hits[-1]
        self.assertEqual(last['Cookie'], 'session=alice')
        self.assertNotIn(srv.AUTHORING_TOKEN_HEADER, last)
        self.assertNotIn('X-Forwarded-User', last)

    def test_explicit_token_api_contract_and_disabled_profile(self):
        self.assertEqual(self.call('POST', '/api/rebuild', cookie='', token=self.env[srv.AUTHORING_TOKEN_ENV],
                                   **{'Origin': None, 'X-Wiki-Profile-Action': None})[0], 200)
        with mock.patch.dict(os.environ, {k: '' for k in self.env if '_PROFILE_' in k}):
            self.assertEqual(self.call()[1], {'enabled': False, 'signed_in': False, 'authoring': False})
            self.assertEqual(self.call('POST', '/api/rebuild')[0], 401)

    def test_partial_configuration_fails_closed(self):
        with mock.patch.dict(os.environ, {'KNOWLEDGE_HUB_PROFILE_STORE': ''}):
            self.assertEqual(self.call()[0], 503)
            self.assertEqual(self.call('POST', '/api/rebuild')[0], 401)

    def test_http_profile_origin_is_limited_to_loopback(self):
        for origin in ('http://localhost:8087', 'http://127.0.0.1:8087', 'http://[::1]:8087'):
            with self.subTest(origin=origin), mock.patch.dict(
                    os.environ, {'KNOWLEDGE_HUB_PROFILE_ORIGIN': origin}):
                self.assertEqual(profile.settings()[1], origin)
        for origin in ('http://wiki.example', 'http://192.168.20.180:8087'):
            with self.subTest(origin=origin), mock.patch.dict(
                    os.environ, {'KNOWLEDGE_HUB_PROFILE_ORIGIN': origin}):
                with self.assertRaises(profile.ProfileUnavailable):
                    profile.settings()
        with mock.patch.dict(os.environ, {'KNOWLEDGE_HUB_PROFILE_ORIGIN': 'http://localhost'}):
            config = profile.settings()
            headers = {'Origin': 'http://localhost:57318', 'X-Wiki-Profile-Action': '1',
                       'Sec-Fetch-Site': 'same-origin'}
            self.assertTrue(profile.mutation_allowed(headers, config))
            for origin in ('http://127.0.0.1:57318', 'https://localhost:57318',
                           'http://localhost.evil:57318'):
                headers['Origin'] = origin
                self.assertFalse(profile.mutation_allowed(headers, config), origin)

    def test_portless_loopback_profile_accepts_bridged_host_and_origin(self):
        with mock.patch.dict(os.environ, {
                srv.ALLOWED_HOSTS_ENV: 'localhost',
                'KNOWLEDGE_HUB_PROFILE_ORIGIN': 'http://localhost',
        }):
            code, data = self.call('POST', token=self.env[srv.AUTHORING_TOKEN_ENV],
                                   Host='localhost:57318', Origin='http://localhost:57318')
        self.assertEqual(code, 200)
        self.assertTrue(data['authoring'])

    def test_profile_grant_keeps_destructive_artifact_checks(self):
        self.enroll()
        with mock.patch.object(srv.IngestHandler, 'handle_remove') as remove:
            # The profile merely reaches the same handler; it does not replace its artifact gate.
            remove.side_effect = srv.ingest_ops.AuthRefused('authorization artifact required')
            code, body = self.call('POST', '/api/remove')
            self.assertEqual(code, 403)
            self.assertIn('authorization artifact', body['error'])

    def test_saved_access_includes_source_metadata_and_read_only_preview(self):
        self.enroll()
        with mock.patch.object(srv, 'article_records', return_value=[]) as records:
            self.assertEqual(self.call(path='/api/articles', **{'Origin': None})[0], 200)
            records.assert_called_once_with(include_sources=True)
        with mock.patch.object(srv, 'preview_payload', return_value={'preview': {}}):
            self.assertEqual(self.call(path='/api/preview?operation=remove&slug=example',
                                       **{'Origin': None, 'X-Wiki-Profile-Action': None})[0], 200)

    def test_verifier_namespace_change_does_not_inherit_grant(self):
        self.enroll()
        with mock.patch.dict(os.environ, {'KNOWLEDGE_HUB_PROFILE_USERINFO_URL': self.env['KNOWLEDGE_HUB_PROFILE_USERINFO_URL'] + '-other'}):
            self.assertFalse(self.call()[1]['authoring'])

    def test_symlink_store_fails_closed_without_modifying_target(self):
        path = profile.settings()[2]
        path.parent.mkdir(mode=0o700)
        target = self.root / 'elsewhere'
        target.write_bytes(b'preserve me')
        path.symlink_to(target)
        self.assertEqual(self.call('POST', token=self.env[srv.AUTHORING_TOKEN_ENV])[0], 503)
        self.assertEqual(target.read_bytes(), b'preserve me')


if __name__ == '__main__':
    unittest.main()
