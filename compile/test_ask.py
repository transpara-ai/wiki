#!/usr/bin/env python3
"""Question answering contracts, isolation, and API trust-boundary tests."""
import io
import json
import os
import runpy
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
from urllib import request, error
from http.server import ThreadingHTTPServer

import ask
from ask_common import AskError
import llm_service as llm
import ingest_server

MODEL = 'gpt-5.6-sol'
MODELS = {'defaults': {'provider': 'codex', 'codex': MODEL},
          'models': [{'id': MODEL, 'provider': 'codex', 'enabled': True,
                      'effort_levels': ['low', 'medium', 'high', 'xhigh', 'max'], 'default_effort': 'low'}]}
QUESTION = {'question': 'Who is our closest competitor?', 'space': 'competition', 'provider': 'codex', 'model': MODEL}


class AnswerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        records = [{'id': 'pi', 'title': 'PI', 'spaces': ['competition'], 'href': '/pi.html',
                    'text': 'PI Vision competes in visualization.'},
                   {'id': 'secret-space', 'title': 'Other', 'spaces': ['civilization'],
                    'href': '/secret-space.html', 'text': 'Other space article.'}]
        (self.root / 'ask-index.json').write_text(json.dumps(ask.build_index(records, ['competition', 'civilization'])))

    def call(self, selection=None, result=None, payload=None):
        selection = {'article_ids': ['pi']} if selection is None else selection
        result = result or {'paragraphs': [{'text': 'The closest match depends on context.', 'article_ids': ['pi']}], 'insufficient_evidence': True}
        with patch.object(ask, 'models', return_value=MODELS), patch.object(ask, 'service', side_effect=[selection, result]) as service:
            output = ask.answer(payload or QUESTION, 'reader', self.root)
            return output, service.call_args_list

    def test_two_calls_scoped_evidence_and_canonical_citations(self):
        result, calls = self.call()
        self.assertEqual([r['id'] for r in calls[0].args[1]['context']], ['pi'])
        self.assertEqual(calls[1].args[1]['context'][0]['text'], 'PI Vision competes in visualization.')
        self.assertEqual(result['citations'][0]['href'], '/pi.html')
        self.assertEqual(len(result['corpus_revision']), 64)
        self.assertLessEqual(calls[1].args[1]['timeout'], calls[0].args[1]['timeout'])
        self.assertEqual(result['effort'], 'low')

    def test_effort_is_validated_and_sent_to_both_stages(self):
        result, calls = self.call(payload={**QUESTION, 'effort': 'high'})
        self.assertEqual(result['effort'], 'high')
        self.assertEqual([c.args[1]['effort'] for c in calls], ['high', 'high'])
        for value in ['ultra', 'not-supported', '--tools=all', '', None]:
            with self.subTest(value=value), self.assertRaises(AskError) as exc:
                self.call(payload={**QUESTION, 'effort': value})
            self.assertEqual(exc.exception.status, 400)

    def test_out_of_scope_and_invented_ids_fail(self):
        for slug in ['secret-space', '../.env', 'invented']:
            with self.subTest(slug=slug), self.assertRaises(AskError):
                self.call({'article_ids': [slug]})

    def test_unsupported_citation_fails(self):
        with self.assertRaises(AskError):
            self.call(result={'paragraphs': [{'text': 'Unsupported', 'article_ids': ['secret-space']}], 'insufficient_evidence': False})

    def test_uncited_assertion_fails(self):
        with self.assertRaises(AskError):
            self.call(result={'paragraphs': [{'text': 'Unsupported', 'article_ids': []}], 'insufficient_evidence': False})

    def test_no_evidence_does_not_call_answer_model(self):
        result, calls = self.call({'article_ids': []})
        self.assertTrue(result['insufficient_evidence'])
        self.assertEqual(len(calls), 1)

    def test_oversized_context_is_not_silently_truncated(self):
        d = json.loads((self.root / 'ask-index.json').read_text())
        d['articles'][0]['text'] = 'x' * 200001
        (self.root / 'ask-index.json').write_text(json.dumps(d))
        with self.assertRaises(AskError) as exc:
            self.call()
        self.assertEqual(exc.exception.status, 422)

    def test_admission_releases_on_failure(self):
        with ask.admission('reader', 'codex'):
            for reader, provider in [('reader', 'claude'), ('other', 'codex')]:
                with self.assertRaises(AskError):
                    with ask.admission(reader, provider):
                        pass
        with ask.admission('reader', 'codex'):
            pass

    def test_admission_spans_processes_and_releases(self):
        script = ('import ask; from ask_common import AskError; import sys\n'
                  'try:\n'
                  ' with ask.admission(sys.argv[1],sys.argv[2]): pass\n'
                  'except AskError as e: sys.exit(29 if e.status == 429 else 1)\n')
        def probe(reader, provider):
            return subprocess.run([sys.executable, '-c', script, reader, provider],
                                  cwd=Path(ask.__file__).parent, capture_output=True).returncode
        with ask.admission('reader', 'codex'):
            self.assertEqual(probe('other-reader', 'codex'), 29)
            self.assertEqual(probe('reader', 'claude'), 29)
            self.assertEqual(probe('other-reader', 'claude'), 0)
        self.assertEqual(probe('other-reader', 'codex'), 0)


class AdapterTests(unittest.TestCase):
    def test_provider_working_directory_is_private_and_removed(self):
        wrapper = runpy.run_path(str(Path(__file__).parent / 'shared-provider/civilization-provider'))
        configuration = {'docker_host': 'unix:///run/test-docker.sock',
                         'observation_path': '/tmp/provider-auth.json',
                         'auth_policy_path': '/tmp/provider-policy.json'}
        for script, status in [('pwd', 0), ('pwd; exit 7', 7), ('pwd; sleep 10', 124)]:
            with patch.dict(os.environ, {'CIVILIZATION_PROVIDER_TIMEOUT_SECONDS': '1'}), \
                 patch.object(wrapper['provider_config'], 'load', return_value=configuration), \
                 patch.object(subprocess, 'run', return_value=subprocess.CompletedProcess([], 0)) as launch:
                wrapper['run'](['exec', '-i', 'provider', 'sh', '-c', script])
                args = launch.call_args.args[0]
            result = subprocess.run(args[args.index('provider') + 1:], capture_output=True, text=True)
            self.assertEqual(result.returncode, status)
            directory = Path(result.stdout.strip())
            self.assertTrue(str(directory).startswith('/tmp/provider-request.'))
            self.assertFalse(directory.exists())

    def fake(self, provider, script, timeout=2):
        with tempfile.TemporaryDirectory() as name:
            program = Path(name) / 'fake.py'
            program.write_text(script)
            with patch.object(llm, 'command', return_value=['/usr/bin/timeout', '--kill-after=0.1s', str(timeout), sys.executable, str(program)]):
                return llm.run_cli(provider, MODEL, 'select', 'untrusted prompt', timeout)

    def test_native_output_formats(self):
        self.assertEqual(self.fake('codex', "import json; print(json.dumps({'type':'item.completed','item':{'type':'agent_message','text':json.dumps({'article_ids':['pi']})}})); print(json.dumps({'type':'turn.completed'}))"), {'article_ids': ['pi']})
        self.assertEqual(self.fake('claude', "print('{\"subtype\":\"success\",\"structured_output\":{\"article_ids\":[\"pi\"]}}')"), {'article_ids': ['pi']})

    def test_invalid_and_error_outputs_are_not_exposed(self):
        cases = [("print('PRIVATE native output'); raise SystemExit(1)", 502),
                 ("print('oauth login expired PRIVATE'); raise SystemExit(1)", 503),
                 ("print('rate_limit PRIVATE'); raise SystemExit(1)", 429),
                 ("print('not JSON PRIVATE')", 502),
                 ("print('{\"subtype\":\"success\",\"structured_output\":{\"article_ids\":\"wrong\"}}')", 502)]
        for code, status in cases:
            with self.subTest(code=code), self.assertRaises(AskError) as exc:
                self.fake('claude', code)
            self.assertEqual(exc.exception.status, status)
            self.assertNotIn('PRIVATE', str(exc.exception))

    def test_codex_tool_events_are_not_accepted_as_answers(self):
        with self.assertRaises(AskError):
            self.fake('codex', "import json; print(json.dumps({'type':'item.completed','item':{'type':'command_execution','command':'unexpected'}})); print(json.dumps({'type':'turn.completed'}))")

    def test_timeout_kills_descendants(self):
        with tempfile.TemporaryDirectory() as name:
            marker = str(Path(name) / 'survived')
            child = 'import time; from pathlib import Path; time.sleep(.6); Path(' + repr(marker) + ').touch()'
            script = 'import subprocess,time,sys\nsubprocess.Popen([sys.executable,"-c",' + repr(child) + '])\ntime.sleep(5)'
            with self.assertRaises(AskError) as exc:
                self.fake('claude', script, .15)
            self.assertEqual(exc.exception.status, 504)
            time.sleep(.7)
            self.assertFalse(Path(marker).exists())

    def test_environment_does_not_inherit_keys_or_endpoint_overrides(self):
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'PRIVATE', 'ANTHROPIC_API_KEY': 'PRIVATE',
                                    'GH_TOKEN': 'PRIVATE', 'HTTP_PROXY': 'PRIVATE', 'OPENAI_BASE_URL': 'PRIVATE'}):
            for provider in ('codex', 'claude'):
                env = llm.environment(provider, Path('/tmp/test'))
                self.assertNotIn('PRIVATE', env.values())
                self.assertNotIn('SSH_AUTH_SOCK', env)

    def test_tools_and_ambient_settings_disabled(self):
        with tempfile.TemporaryDirectory() as directory:
            codex = llm.command('codex', MODEL, 'select', Path(directory))
            claude = llm.command('claude', 'claude-sonnet-5', 'select', Path(directory))
            self.assertIn('--ignore-user-config', codex)
            self.assertIn('read-only', codex)
            self.assertIn('shell_tool', codex)
            self.assertNotIn('--dangerously-bypass-approvals-and-sandbox', codex)
            self.assertEqual(claude[claude.index('--tools') + 1], '')
            self.assertIn('--strict-mcp-config', claude)

    def test_native_effort_flags_and_unsupported_models(self):
        directory = Path('/tmp/test')
        codex = llm.command('codex', MODEL, 'select', directory, 'max')
        self.assertIn('model_reasoning_effort="max"', codex)
        claude = llm.command('claude', 'claude-sonnet-5', 'answer', directory, 'medium')
        self.assertEqual(claude[claude.index('--effort') + 1], 'medium')
        haiku = llm.command('claude', 'claude-haiku-4-5-20251001', 'answer', directory, 'not-supported')
        self.assertNotIn('--effort', haiku)
        for provider, model, effort in [('codex', 'gpt-5.5', 'max'), ('claude', 'claude-opus-4-6', 'xhigh'), ('claude', 'claude-haiku-4-5-20251001', 'high')]:
            with self.subTest(model=model), self.assertRaises(AskError):
                llm.command(provider, model, 'answer', directory, effort)

    def test_dispatcher_rejects_invalid_effort_before_launch(self):
        with patch.object(llm, 'enabled_models', return_value={MODEL}), patch.object(llm, 'run_cli') as run:
            with self.assertRaises(AskError):
                llm.complete({**QUESTION, 'stage': 'select', 'context': [], 'timeout': 5, 'effort': 'invented'})
            run.assert_not_called()

    def test_unverified_models_refused_without_launch(self):
        with patch.object(llm, 'enabled_models', return_value=set()), patch.object(llm, 'run_cli') as run:
            with self.assertRaises(AskError):
                llm.complete({**QUESTION, 'stage': 'select', 'context': [], 'timeout': 5})
            run.assert_not_called()


class APITests(unittest.TestCase):
    def test_reader_auth_and_same_origin_not_authoring_token(self):
        server = ThreadingHTTPServer(('127.0.0.1', 0), ingest_server.IngestHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        config = ('http://verifier/userinfo', 'https://wiki.test', Path('/unused/grants'))
        url = 'http://127.0.0.1:%d' % server.server_port
        try:
            with patch.object(ingest_server.authoring_profile, 'settings', return_value=config), \
                 patch.object(ingest_server.authoring_profile, 'principal', return_value=None), \
                 patch.object(ask, 'models', return_value=MODELS), \
                 patch.object(ingest_server.IngestHandler, 'require_allowed_host', return_value=True):
                with self.assertRaises(error.HTTPError) as exc:
                    request.urlopen(url + '/api/ask/models')
                self.assertEqual(exc.exception.code, 401)
                exc.exception.close()
                with patch.object(ingest_server.authoring_profile, 'principal', return_value='verified-reader'), \
                     patch.object(ask, 'answer', return_value={'answer': 'ok'}) as answer:
                    headers = {'Content-Type': 'application/json', 'Origin': 'https://wiki.test', 'X-Wiki-Profile-Action': '1'}
                    req = request.Request(url + '/api/ask', data=json.dumps(QUESTION).encode(), headers=headers)
                    self.assertEqual(json.load(request.urlopen(req)), {'answer': 'ok'})
                    answer.assert_called_once()
                    headers['Origin'] = 'https://evil.test'
                    req = request.Request(url + '/api/ask', data=json.dumps(QUESTION).encode(), headers=headers)
                    with self.assertRaises(error.HTTPError) as exc:
                        request.urlopen(req)
                    self.assertEqual(exc.exception.code, 403)
                    exc.exception.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


if __name__ == '__main__':
    unittest.main()
