"""Finite source capture tests use fake HTTP/DNS/processes, never live sources."""
import base64
import hashlib
import io
import json
import os
from pathlib import Path
import socket
import subprocess
import tempfile
import types
import unittest
from unittest import mock

import terminology_sources as sources
from knowledge_sources import Deferred, PinnedHTTPS


def wire(value):
    return json.dumps(value).encode()


class Network:
    """Record the full transport contract and fail on any unplanned destination."""
    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def __call__(self, url, config):
        self.calls.append((url, dict(config)))
        response = self.responses[url]
        return response() if callable(response) else response


def repository(files, *, extra=(), truncated=False):
    """Build real Git blob hashes so tests detect bytes swapped after tree pinning."""
    base = 'https://api.github.com/repos/example/docs'
    commit, tree = 'a' * 40, 'b' * 40
    entries, responses = [], {}
    for path, body in files:
        sha = hashlib.sha1(b'blob ' + str(len(body)).encode() + b'\0' + body).hexdigest()
        entries.append({'path': path, 'type': 'blob', 'mode': '100644', 'size': len(body), 'sha': sha})
        responses[base + '/git/blobs/' + sha] = (200, {}, wire({'sha': sha, 'encoding': 'base64',
                                                             'content': base64.encodebytes(body).decode()}))
    entries.extend(extra)
    responses[base + '/commits/HEAD'] = (200, {}, wire({'sha': commit, 'commit': {'tree': {'sha': tree}}}))
    responses[base + '/git/trees/' + tree + '?recursive=1'] = (200, {}, wire({'sha': tree, 'truncated': truncated, 'tree': entries}))
    return Network(responses), commit, tree


class CaptureTests(unittest.TestCase):
    def setUp(self):
        # Tests must never read any real operator credential descriptor.
        self.environment = mock.patch.dict(os.environ, {sources.GITHUB_CONFIG_ENV: ''})
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def test_public_text_hashes_and_finite_transport_contract(self):
        body = b'Use the pump.\n'
        fetch = Network({'https://example.org/manual': (200, {'Content-Type': 'text/plain; charset=utf-8'}, body)})
        result = sources.capture({'type': 'url', 'url': 'https://example.org/manual'}, fetcher=fetch)
        self.assertEqual(result['documents'], [{'label': 'https://example.org/manual', 'text': body.decode(),
                                              'source_sha256': hashlib.sha256(body).hexdigest(),
                                              'text_sha256': hashlib.sha256(body).hexdigest()}])
        self.assertTrue(result['coverage']['complete'])
        self.assertEqual(result['coverage']['network_bytes'], len(body))
        self.assertEqual(fetch.calls[0][1]['credential_ref'], '')
        self.assertLessEqual(fetch.calls[0][1]['timeout'], 20)
        self.assertEqual(result['coverage']['limits']['requests'], 300)
        self.assertEqual(result['coverage']['limits']['seconds'], 60)

    def test_html_removes_active_content_and_does_not_follow_links(self):
        body = b'<h1>Guide</h1><script>run()</script><form>password<input value="x"></form><p>Use &amp; inspect.</p><a href="https://other.org/">Reference</a>'
        fetch = Network({'https://example.org/': (200, {'content-type': 'text/html'}, body)})
        result = sources.capture({'type': 'url', 'url': 'https://example.org/'}, fetcher=fetch)
        self.assertEqual(result['documents'][0]['text'], 'Guide\nUse & inspect.\nReference')
        self.assertEqual(len(fetch.calls), 1)
        self.assertEqual(result['documents'][0]['source_sha256'], hashlib.sha256(body).hexdigest())

    def test_invalid_destinations_and_client_selected_authority_are_rejected_before_fetch(self):
        bad = ['http://example.org/', 'https://localhost/', 'https://127.0.0.1/',
               'https://[::1]/', 'https://169.254.169.254/', 'file:///etc/passwd',
               'https://user:pass@example.org/', 'https://example.org/?access_token=private',
               'https://example.org/?X-Amz-Credential=private', 'https://example.org:8443/',
               'https://example.org/#fragment', 'https://example.org/\nsecret']
        fetch = mock.Mock()
        for url in bad:
            with self.subTest(url=url), self.assertRaises(sources.CaptureError):
                sources.capture({'type': 'url', 'url': url}, fetcher=fetch)
        for key in ['credential_ref', 'checker', 'command', 'limit', 'trust_policy']:
            with self.subTest(key=key), self.assertRaises(sources.CaptureError):
                sources.capture({'type': 'url', 'url': 'https://example.org/', key: 'x'}, fetcher=fetch)
        fetch.assert_not_called()

    def test_validation_is_side_effect_free_and_returns_separate_patterns(self):
        request = {'type': 'repo', 'url': 'https://github.com/example/docs.git', 'paths': ['*.md']}
        with mock.patch.object(sources.subprocess, 'run', side_effect=AssertionError('No process')):
            result = sources.validate_request(request)
        self.assertEqual(result['url'], 'https://github.com/example/docs')
        self.assertEqual(result['ref'], 'HEAD')
        result['paths'].append('*.py')
        self.assertEqual(request['paths'], ['*.md'])
        for change in [{'url': 'https://github.com/example/docs/tree/main'}, {'paths': ['../*']}, {'ref': '../../x'}]:
            with self.assertRaises(sources.CaptureError):
                sources.validate_request({**request, **change})

    def test_redirects_are_counted_and_cannot_cross_origins(self):
        fetch = Network({'https://example.org/start': (302, {'location': '/manual'}, b'redirect'),
                         'https://example.org/manual': (200, {'content-type': 'text/plain'}, b'text')})
        result = sources.capture({'type': 'url', 'url': 'https://example.org/start'}, fetcher=fetch)
        self.assertEqual(result['coverage']['requests'], 2)
        self.assertEqual(result['source']['url'], 'https://example.org/manual')
        self.assertEqual(result['coverage']['network_bytes'], len(b'redirecttext'))
        fetch.responses['https://example.org/start'] = (302, {'location': 'https://other.org/'}, b'')
        with self.assertRaisesRegex(sources.CaptureError, 'same origin'):
            sources.capture({'type': 'url', 'url': 'https://example.org/start'}, fetcher=fetch)
        self.assertNotIn('https://other.org/', [url for url, _ in fetch.calls])

    def test_redirects_consume_the_actual_request_budget(self):
        fetch = Network({'https://example.org/': (302, {'location': '/'}, b'x')})
        with mock.patch.object(sources, 'MAX_REQUESTS', 3):
            result = sources.capture({'type': 'url', 'url': 'https://example.org/'}, fetcher=fetch)
        self.assertEqual(len(fetch.calls), 3)
        self.assertEqual(result['coverage']['reasons'], ['requests'])
        self.assertFalse(result['coverage']['complete'])

    def test_redirect_limit_is_finite_even_with_available_job_budget(self):
        fetch = Network({'https://example.org/': (302, {'location': '/'}, b'')})
        result = sources.capture({'type': 'url', 'url': 'https://example.org/'}, fetcher=fetch)
        self.assertEqual(len(fetch.calls), sources.MAX_REDIRECTS + 1)
        self.assertEqual(result['coverage']['reasons'], ['redirects'])

    def test_deadline_passes_remaining_time_and_stops_after_slow_adapter(self):
        now = [0.0]
        def response():
            now[0] = 61
            return 200, {'content-type': 'text/plain'}, b'text'
        fetch = Network({'https://example.org/': response})
        result = sources.capture({'type': 'url', 'url': 'https://example.org/'}, fetcher=fetch, clock=lambda: now[0])
        self.assertEqual(result['coverage']['reasons'], ['deadline'])
        self.assertEqual(len(result['documents']), 0)
        self.assertEqual(fetch.calls[0][1]['deadline'], 60)
        now = iter([0, 59.5, 59.5, 59.5, 59.5])
        fetch = Network({'https://example.org/': (200, {'content-type': 'text/plain'}, b'x')})
        sources.capture({'type': 'url', 'url': 'https://example.org/'}, fetcher=fetch, clock=lambda: next(now, 59.5))
        self.assertEqual(fetch.calls[0][1]['timeout'], .5)

    def test_cancellation_prevents_next_request_and_is_not_success(self):
        stopped = [False]
        def response():
            stopped[0] = True
            return 302, {'location': '/next'}, b''
        fetch = Network({'https://example.org/': response})
        with self.assertRaisesRegex(sources.CaptureError, 'cancelled'):
            sources.capture({'type': 'url', 'url': 'https://example.org/'}, fetcher=fetch, cancelled=lambda: stopped[0])
        self.assertEqual(len(fetch.calls), 1)

    def test_repo_resolves_once_and_only_fetches_pinned_blob_objects(self):
        fetch, commit, tree = repository([('README.md', b'Use the pump.'), ('src/a.py', b'# Explain purpose.\n')])
        result = sources.capture({'type': 'repo', 'url': 'https://github.com/example/docs'}, fetcher=fetch)
        self.assertEqual(result['source']['commit'], commit)
        self.assertEqual([d['label'] for d in result['documents']], ['README.md', 'src/a.py'])
        urls = [url for url, _ in fetch.calls]
        self.assertEqual(sum('/commits/' in url for url in urls), 1)
        self.assertIn('/git/trees/' + tree + '?recursive=1', urls[1])
        self.assertTrue(all('/git/blobs/' in url for url in urls[2:]))
        self.assertTrue(result['coverage']['complete'])

    def test_ref_is_quoted_and_path_selection_does_not_change_the_tree_revision(self):
        fetch, _, _ = repository([('guide.md', b'text'), ('src/a.py', b'# text')])
        head = 'https://api.github.com/repos/example/docs/commits/HEAD'
        fetch.responses[head.replace('HEAD', 'feature%2Fdocs')] = fetch.responses.pop(head)
        result = sources.capture({'type': 'repo', 'url': 'https://github.com/example/docs', 'ref': 'feature/docs', 'paths': ['*.md']}, fetcher=fetch)
        self.assertEqual([d['label'] for d in result['documents']], ['guide.md'])
        self.assertTrue(result['coverage']['complete'])
        self.assertEqual(result['skipped'][0]['reason'], 'outside-selected-paths')

    def test_truncated_tree_and_wrong_blob_bytes_never_appear_complete(self):
        fetch, _, _ = repository([('guide.md', b'text')], truncated=True)
        with self.assertRaisesRegex(sources.CaptureError, 'incomplete'):
            sources.capture({'type': 'repo', 'url': 'https://github.com/example/docs'}, fetcher=fetch)
        fetch, _, _ = repository([('guide.md', b'text')])
        key = next(key for key in fetch.responses if '/git/blobs/' in key)
        data = json.loads(fetch.responses[key][2])
        data['content'] = base64.b64encode(b'evil').decode()
        fetch.responses[key] = (200, {}, wire(data))
        with self.assertRaisesRegex(sources.CaptureError, 'pinned tree'):
            sources.capture({'type': 'repo', 'url': 'https://github.com/example/docs'}, fetcher=fetch)

    def test_symlinks_submodules_unsupported_and_large_files_are_skipped_without_fetch(self):
        entries = [{'path': 'link.md', 'type': 'blob', 'mode': '120000', 'size': 2, 'sha': 'c' * 40},
                   {'path': 'module', 'type': 'commit', 'mode': '160000', 'sha': 'd' * 40},
                   {'path': 'code.js', 'type': 'blob', 'mode': '100644', 'size': 2, 'sha': 'e' * 40},
                   {'path': 'big.md', 'type': 'blob', 'mode': '100644', 'size': sources.MAX_FILE_BYTES + 1, 'sha': 'f' * 40},
                   {'path': '../outside.md', 'type': 'blob', 'mode': '100644', 'size': 2, 'sha': 'f' * 40}]
        fetch, _, _ = repository([], extra=entries)
        result = sources.capture({'type': 'repo', 'url': 'https://github.com/example/docs'}, fetcher=fetch)
        self.assertEqual(len(fetch.calls), 2)
        self.assertFalse(result['coverage']['complete'])
        self.assertEqual(len(result['skipped']), 5)

    def test_file_limit_and_skip_diagnostic_sample_are_bounded(self):
        fetch, _, _ = repository([(f'{n}.md', str(n).encode()) for n in range(6)])
        with mock.patch.object(sources, 'MAX_FILES', 2):
            result = sources.capture({'type': 'repo', 'url': 'https://github.com/example/docs'}, fetcher=fetch)
        self.assertEqual(len(result['documents']), 2)
        self.assertEqual(len(fetch.calls), 4)
        self.assertEqual(result['coverage']['skipped_count'], 4)
        self.assertTrue(result['coverage']['skipped_report_truncated'])
        self.assertEqual(len(result['skipped']), 2)
        self.assertEqual(result['coverage']['reasons'], ['files'])

    def test_total_bytes_shrink_following_request_budget(self):
        fetch = Network({'https://example.org/': (302, {'location': '/next'}, b'12345678'),
                         'https://example.org/next': (200, {'content-type': 'text/plain'}, b'xx')})
        with mock.patch.object(sources, 'MAX_BYTES', 10):
            result = sources.capture({'type': 'url', 'url': 'https://example.org/'}, fetcher=fetch)
        self.assertEqual(fetch.calls[1][1]['byte_budget'], 2)
        self.assertEqual(result['coverage']['network_bytes'], 10)

    def test_unsupported_binary_or_compressed_sources_do_not_become_text(self):
        for headers, body in [({'content-type': 'application/pdf'}, b'%PDF'),
                              ({'content-type': 'text/plain'}, b'a\0b'),
                              ({'content-type': 'text/plain'}, b'\xff')]:
            fetch = Network({'https://example.org/': (200, headers, body)})
            result = sources.capture({'type': 'url', 'url': 'https://example.org/'}, fetcher=fetch)
            self.assertFalse(result['documents'])
            self.assertFalse(result['coverage']['complete'])
        fetch = Network({'https://example.org/': (200, {'content-encoding': 'gzip'}, b'data')})
        with self.assertRaisesRegex(sources.CaptureError, 'Compressed'):
            sources.capture({'type': 'url', 'url': 'https://example.org/'}, fetcher=fetch)

    def test_transport_and_metadata_errors_do_not_echo_source_material(self):
        def failure(url, config):
            raise RuntimeError('PRIVATE CONTENT https://bad.example/private')
        with self.assertRaises(sources.CaptureError) as caught:
            sources.capture({'type': 'url', 'url': 'https://example.org/'}, fetcher=failure)
        self.assertNotIn('PRIVATE', str(caught.exception))
        fetch, _, _ = repository([])
        fetch.responses['https://api.github.com/repos/example/docs/commits/HEAD'] = (200, {}, b'{"commit": []}')
        with self.assertRaises(sources.CaptureError):
            sources.capture({'type': 'repo', 'url': 'https://github.com/example/docs'}, fetcher=fetch)

    def test_no_repository_code_is_executed_or_written(self):
        with tempfile.TemporaryDirectory() as directory:
            marker = Path(directory) / 'must-not-exist'
            body = f'from pathlib import Path\nPath({str(marker)!r}).touch()\n'.encode()
            fetch, _, _ = repository([('payload.py', body)])
            with mock.patch.object(sources.subprocess, 'run', side_effect=AssertionError('No subprocess for fake capture')):
                result = sources.capture({'type': 'repo', 'url': 'https://github.com/example/docs'}, fetcher=fetch)
            self.assertEqual(result['documents'][0]['text'], body.decode())
            self.assertFalse(marker.exists())


class PublicTransportTests(unittest.TestCase):
    def test_worker_preserves_query_and_uses_only_get_with_identity_encoding(self):
        """Execute the trusted worker against a fake connector, with no sockets."""
        requests = []
        class Connection:
            def __init__(self, hostname, **kwargs):
                requests.append(('connection', hostname, kwargs['timeout']))
            def request(self, method, target, headers):
                requests.append((method, target, headers))
            def getresponse(self):
                return types.SimpleNamespace(status=200, getheaders=lambda: [('Content-Type', 'application/json')],
                                             read=lambda limit: b'{}')
            def close(self):
                pass
        payload = wire({'url': 'https://api.github.com/repos/example/docs/git/trees/' + 'a' * 40 + '?recursive=1',
                        'timeout': .5, 'byte_budget': 100})
        output = io.BytesIO()
        with mock.patch('knowledge_sources.PinnedHTTPS', Connection), \
                mock.patch.object(sources.sys, 'stdin', types.SimpleNamespace(buffer=io.BytesIO(payload))), \
                mock.patch.object(sources.sys, 'stdout', types.SimpleNamespace(buffer=output)), \
                mock.patch.object(sources.sys, 'argv', ['worker', '/trusted/compile']), \
                mock.patch.object(sources.sys, 'path', list(sources.sys.path)):
            exec(sources._HTTP_WORKER, {})
        self.assertEqual(requests[1][0], 'GET')
        self.assertTrue(requests[1][1].endswith('?recursive=1'))
        self.assertEqual(requests[1][2]['Accept-Encoding'], 'identity')
        self.assertNotIn('Authorization', requests[1][2])
        self.assertTrue(output.getvalue().endswith(b'\n{}'))

    def test_default_worker_has_no_credentials_and_hard_timeout(self):
        result = types.SimpleNamespace(returncode=0, stdout=b'[200,{"content-type":"text/plain"}]\ntext')
        with mock.patch.object(sources.subprocess, 'run', return_value=result) as run:
            status, _, body = sources._public_fetch('https://example.org/', {'timeout': .25, 'byte_budget': 10})
        self.assertEqual((status, body), (200, b'text'))
        command = run.call_args.args[0]
        self.assertIn('-I', command)
        self.assertIn('from knowledge_sources import PinnedHTTPS', command[3])
        self.assertEqual(run.call_args.kwargs['timeout'], .25)
        self.assertEqual(set(run.call_args.kwargs['env']), {'PATH', 'LANG'})
        self.assertEqual(run.call_args.kwargs['stderr'], subprocess.DEVNULL)

    def test_default_worker_timeout_and_errors_are_sanitized(self):
        with mock.patch.object(sources.subprocess, 'run', side_effect=subprocess.TimeoutExpired('SECRET', .1)):
            with self.assertRaises(sources.CaptureError) as caught:
                sources._public_fetch('https://example.org/', {'timeout': .1, 'byte_budget': 10})
        self.assertNotIn('SECRET', str(caught.exception))

    def test_shared_connector_rejects_private_or_mixed_dns_before_connecting(self):
        public = (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('8.8.8.8', 443))
        private = (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('127.0.0.1', 443))
        for answers in [[private], [public, private]]:
            with mock.patch('knowledge_sources.socket.getaddrinfo', return_value=answers), \
                    mock.patch('knowledge_sources.socket.create_connection') as connect:
                with self.assertRaises(Deferred):
                    PinnedHTTPS('example.org').connect()
                connect.assert_not_called()

    def test_shared_connector_connects_pinned_ip_with_original_tls_hostname(self):
        answer = (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('8.8.8.8', 443))
        connection = PinnedHTTPS('example.org')
        with mock.patch('knowledge_sources.socket.getaddrinfo', return_value=[answer]), \
                mock.patch('knowledge_sources.socket.create_connection') as connect, \
                mock.patch.object(connection._context, 'wrap_socket') as wrap:
            connection.connect()
        self.assertEqual(connect.call_args.args[0], ('8.8.8.8', 443))
        self.assertEqual(wrap.call_args.kwargs['server_hostname'], 'example.org')


class GitHubCredentialTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.config = Path(self.directory.name) / 'github.json'
        self.registry = Path(self.directory.name) / 'credentials.json'
        self.descriptor = {'schema_version': 1, 'credential_ref': 'approved', 'repositories': ['example/docs']}
        self.write_config(self.descriptor)
        self.registry.write_text(json.dumps({'approved': {'type': 'github', 'origins': ['https://api.github.com'],
                                                          'environment': 'TERMINOLOGY_TEST_VALUE'}}))
        self.registry.chmod(0o600)
        # This low-entropy placeholder is synthetic; no production token is read.
        self.environment = mock.patch.dict(os.environ, {sources.GITHUB_CONFIG_ENV: str(self.config),
            'KNOWLEDGE_HUB_CREDENTIALS': str(self.registry), 'TERMINOLOGY_TEST_VALUE': 'example'})
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def write_config(self, value):
        self.config.write_text(json.dumps(value))
        self.config.chmod(0o600)

    def test_exact_approved_repo_uses_registry_header_without_disclosing_it(self):
        fetch, _, _ = repository([('guide.md', b'Use the pump.')])
        result = sources.capture({'type': 'repo', 'url': 'https://github.com/example/docs'}, fetcher=fetch)
        self.assertTrue(result['coverage']['complete'])
        for url, config in fetch.calls:
            self.assertTrue(url.startswith('https://api.github.com/repos/example/docs/'))
            self.assertEqual(config['headers'], {'Authorization': 'Bearer example'})
        self.assertNotIn('Bearer example', json.dumps(result))
        self.assertNotIn('credential_ref', json.dumps(result))

    def test_nonallowlisted_repo_and_all_url_jobs_remain_anonymous(self):
        self.write_config({**self.descriptor, 'repositories': ['other/docs']})
        fetch, _, _ = repository([('guide.md', b'text')])
        with mock.patch.object(sources.Fetcher, 'credential', side_effect=AssertionError('No credential read')):
            sources.capture({'type': 'repo', 'url': 'https://github.com/example/docs'}, fetcher=fetch)
            for target in ('https://example.org/', 'https://api.github.com/repos/other/docs/commits/HEAD'):
                url_fetch = Network({target: (200, {'content-type': 'text/plain'}, b'text')})
                sources.capture({'type': 'url', 'url': target}, fetcher=url_fetch)
                self.assertEqual(url_fetch.calls[0][1]['headers'], {})
        self.assertTrue(all(config['headers'] == {} for _, config in fetch.calls))

    def test_configured_authority_rejects_unsafe_schema_permissions_and_registry(self):
        bad = [{**self.descriptor, 'schema_version': True}, {**self.descriptor, 'extra': 'field'},
               {**self.descriptor, 'credential_ref': '../key'}, {**self.descriptor, 'repositories': ['example/docs', 'EXAMPLE/docs']},
               {**self.descriptor, 'repositories': ['example/../other']},
               {**self.descriptor, 'repositories': ['example/' + str(n) for n in range(101)]}]
        fetch = mock.Mock()
        for config in bad:
            self.write_config(config)
            with self.subTest(config=config), self.assertRaisesRegex(sources.CaptureError, 'configuration is unavailable'):
                sources.capture({'type': 'repo', 'url': 'https://github.com/example/docs'}, fetcher=fetch)
        self.write_config(self.descriptor)
        self.config.chmod(0o644)
        with self.assertRaises(sources.CaptureError):
            sources.capture({'type': 'repo', 'url': 'https://github.com/example/docs'}, fetcher=fetch)
        self.config.chmod(0o600)
        self.registry.write_text(json.dumps({'approved': {'type': 'github', 'origins': ['https://other.org'],
                                                         'environment': 'TERMINOLOGY_TEST_VALUE'}}))
        with self.assertRaises(sources.CaptureError) as caught:
            sources.capture({'type': 'repo', 'url': 'https://github.com/example/docs'}, fetcher=fetch)
        self.assertNotIn(str(self.directory.name), str(caught.exception))
        self.assertNotIn('Bearer example', str(caught.exception))
        fetch.assert_not_called()

    def test_credential_redirect_cannot_escape_repo_prefix_even_on_same_api_host(self):
        initial = 'https://api.github.com/repos/example/docs/commits/HEAD'
        targets = ['https://other.org/repos/example/docs/commits/HEAD',
                   'https://api.github.com/repos/example/other/commits/HEAD',
                   'https://api.github.com/repos/example/docs-evil/commits/HEAD',
                   'https://api.github.com/repos/example/docs/../other/commits/HEAD',
                   'https://api.github.com/repos/example/docs/%252e%252e/other/commits/HEAD']
        for target in targets:
            fetch = Network({initial: (302, {'location': target}, b'')})
            with self.subTest(target=target), self.assertRaises(sources.CaptureError):
                sources.capture({'type': 'repo', 'url': 'https://github.com/example/docs'}, fetcher=fetch)
            self.assertEqual(len(fetch.calls), 1)
            self.assertEqual(fetch.calls[0][1]['headers'], {'Authorization': 'Bearer example'})

    def test_same_repo_redirect_reuses_header_and_is_counted(self):
        fetch, _, _ = repository([('guide.md', b'text')])
        initial = 'https://api.github.com/repos/example/docs/commits/HEAD'
        target = initial.replace('HEAD', 'main')
        fetch.responses[target] = fetch.responses[initial]
        fetch.responses[initial] = (302, {'location': target}, b'')
        result = sources.capture({'type': 'repo', 'url': 'https://github.com/example/docs'}, fetcher=fetch)
        self.assertEqual(result['coverage']['requests'], 4)
        self.assertTrue(all(config['headers'] == {'Authorization': 'Bearer example'} for _, config in fetch.calls))

    def test_child_receives_header_only_on_stdin_and_revalidates_destination(self):
        result = types.SimpleNamespace(returncode=0, stdout=b'[200,{}]\n{}')
        headers = {'Authorization': 'Bearer example'}
        config = {'timeout': .5, 'byte_budget': 100, 'headers': headers, 'api_prefix': '/repos/example/docs/'}
        with mock.patch.object(sources.subprocess, 'run', return_value=result) as run:
            sources._public_fetch('https://api.github.com/repos/example/docs/commits/HEAD', config)
        self.assertEqual(json.loads(run.call_args.kwargs['input'])['headers'], headers)
        self.assertNotIn('Bearer example', repr(run.call_args.args[0]))
        self.assertNotIn('Bearer example', repr(run.call_args.kwargs['env']))
        with mock.patch.object(sources.subprocess, 'run') as run:
            with self.assertRaises(sources.CaptureError):
                sources._public_fetch('https://example.org/', config)
            run.assert_not_called()

    def test_url_mode_does_not_even_read_a_malformed_host_descriptor(self):
        self.config.write_text('not JSON')
        fetch = Network({'https://example.org/': (200, {'content-type': 'text/plain'}, b'text')})
        result = sources.capture({'type': 'url', 'url': 'https://example.org/'}, fetcher=fetch)
        self.assertTrue(result['coverage']['complete'])
        self.assertEqual(fetch.calls[0][1]['headers'], {})

    def test_credential_echo_is_refused_without_appearing_in_the_error(self):
        initial = 'https://api.github.com/repos/example/docs/commits/HEAD'
        fetch = Network({initial: (200, {}, b'Bearer example')})
        with self.assertRaises(sources.CaptureError) as caught:
            sources.capture({'type': 'repo', 'url': 'https://github.com/example/docs'}, fetcher=fetch)
        self.assertNotIn('Bearer example', str(caught.exception))

    def test_nonregular_registry_is_refused_before_the_existing_reader_can_block(self):
        self.registry.unlink()
        os.mkfifo(self.registry, 0o600)
        fetch = mock.Mock()
        with self.assertRaises(sources.CaptureError):
            sources.capture({'type': 'repo', 'url': 'https://github.com/example/docs'}, fetcher=fetch)
        fetch.assert_not_called()

    def test_malformed_registry_origin_string_is_not_an_origin_allowlist(self):
        self.registry.write_text(json.dumps({'approved': {'type': 'github',
            'origins': 'https://api.github.com.evil.invalid', 'environment': 'TERMINOLOGY_TEST_VALUE'}}))
        fetch = mock.Mock()
        with self.assertRaises(sources.CaptureError):
            sources.capture({'type': 'repo', 'url': 'https://github.com/example/docs'}, fetcher=fetch)
        fetch.assert_not_called()


if __name__ == '__main__':
    unittest.main()
