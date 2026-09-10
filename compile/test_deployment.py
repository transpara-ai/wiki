#!/usr/bin/env python3
"""Migration failure/recovery tests; never alter host services or the live corpus."""
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent / 'deploy'))
import bundle
import host
import velia


class BundleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.archive = self.root / 'bundle.tar.gz'
        self.dest = self.root / 'restored'

    def make_archive(self, *, extra=None, wrong_hash=False):
        data = b'uploaded evidence\n'
        name = 'repos/wiki/raw/inbox/original.txt'
        manifest = {'schema': 1, 'files': {name: {'bytes': len(data),
                     'sha256': '0' * 64 if wrong_hash else hashlib.sha256(data).hexdigest()}}}
        with tarfile.open(self.archive, 'w:gz') as tar:
            for path, content in [('manifest.json', json.dumps(manifest).encode()), (name, data)]:
                info = tarfile.TarInfo(path)
                info.size = len(content)
                tar.addfile(info, io.BytesIO(content))
            if extra:
                tar.addfile(extra, io.BytesIO(b''))
        return bundle.digest(self.archive)

    def test_roundtrip_and_refuse_overwrite(self):
        checksum = self.make_archive()
        bundle.unpack(self.archive, checksum, self.dest)
        content = self.dest / 'repos/wiki/raw/inbox/original.txt'
        self.assertEqual(content.read_bytes(), b'uploaded evidence\n')
        content.write_text('new destination edit')
        with self.assertRaises(FileExistsError):
            bundle.unpack(self.archive, checksum, self.dest)
        self.assertEqual(content.read_text(), 'new destination edit')

    def test_transport_corruption_creates_no_destination(self):
        self.make_archive()
        with self.assertRaisesRegex(ValueError, 'Bundle checksum'):
            bundle.unpack(self.archive, '0' * 64, self.dest)
        self.assertFalse(self.dest.exists())

    def test_internal_corruption_creates_no_destination(self):
        checksum = self.make_archive(wrong_hash=True)
        with self.assertRaisesRegex(ValueError, 'File checksum'):
            bundle.unpack(self.archive, checksum, self.dest)
        self.assertFalse(self.dest.exists())

    def test_malicious_archive_members(self):
        for path in ('../escape', '/absolute', 'repos/../escape', 'manifest.json'):
            with self.subTest(path=path):
                checksum = self.make_archive(extra=tarfile.TarInfo(path))
                with self.assertRaises(ValueError):
                    bundle.unpack(self.archive, checksum, self.dest)
                self.assertFalse(self.dest.exists())
        link = tarfile.TarInfo('repos/wiki/link')
        link.type, link.linkname = tarfile.SYMTYPE, '/etc'
        checksum = self.make_archive(extra=link)
        with self.assertRaises(ValueError):
            bundle.unpack(self.archive, checksum, self.dest)

    def test_unlisted_regular_file_rejected(self):
        checksum = self.make_archive(extra=tarfile.TarInfo('extra'))
        with self.assertRaisesRegex(ValueError, 'membership'):
            bundle.unpack(self.archive, checksum, self.dest)

    def test_exclude_credentials_preserve_corpus_and_examples(self):
        for name in ('.env', '.env.backup', 'ingest-authorization.json', '.git', 'node_modules', '.wiki-write.lock'):
            self.assertTrue(bundle.excluded(name), name)
        for name in ('.env.example', 'ingest-authorization.example.json', 'ingest-ledger.json', 'raw', 'wiki'):
            self.assertFalse(bundle.excluded(name), name)

    def test_symlink_snapshot_rejected(self):
        (self.root / 'escape').symlink_to('/etc/passwd')
        with self.assertRaisesRegex(ValueError, 'symlink'):
            list(bundle.files_under(self.root))

    def test_lock_timeout(self):
        (self.root / 'compile').mkdir()
        with bundle.wiki_lock(self.root):
            with self.assertRaises(TimeoutError):
                with bundle.wiki_lock(self.root, timeout=0):
                    self.fail('Second writer acquired the lock')

    def test_code_guard_covers_css_but_allows_content_updates(self):
        self.assertTrue(bundle.application_file(Path('repos/wiki/compile/assets/style.css')))
        self.assertTrue(bundle.application_file(Path('repos/wiki/compile/knowledge_structure.json')))
        self.assertFalse(bundle.application_file(Path('repos/wiki/wiki/article.md')))
        self.assertFalse(bundle.application_file(Path('repos/wiki/compile/ingest-ledger.jsonl')))


class HostTests(unittest.TestCase):
    def test_prerequisites_can_finish_before_separate_enrollment(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(host, 'CANONICAL', Path(tmp) / 'repos'), \
                patch.object(host, 'run'), patch.object(host, 'capture', return_value=''), \
                patch.object(host, 'free_port'), patch.object(host.os, 'getuid', return_value=1000), \
                patch.object(host, 'tailscale', side_effect=RuntimeError('not enrolled')) as tailscale, \
                patch.object(host, 'serve_config') as serve:
            host.preflight(require_tailnet=False)
            tailscale.assert_not_called()
            serve.assert_not_called()
            with self.assertRaisesRegex(RuntimeError, 'not enrolled'):
                host.preflight()

    def test_rehearsal_needs_no_tailnet_and_uses_local_hostname(self):
        with tempfile.TemporaryDirectory() as tmp:
            sha = 'a' * 64
            wiki = Path(tmp) / ('rehearsal-' + sha[:16]) / 'repos/wiki'
            wiki.mkdir(parents=True)
            manifest = {'files': {}, 'source_commit': 'fixture'}
            with patch.object(host, 'BASE', Path(tmp)), patch.object(host, 'preflight') as preflight, \
                    patch.object(host, 'unpack', return_value=manifest), patch.object(host, 'restore_git'), \
                    patch.object(host, 'tailscale', side_effect=RuntimeError('not enrolled')) as tailscale, \
                    patch.object(host, 'compose'), patch.object(host, 'run'), \
                    patch.object(host, 'verify', return_value={'ok': True}) as verify:
                host.install(Path(tmp) / 'bundle.tar.gz', sha, rehearsal=True)
                preflight.assert_called_once_with(require_tailnet=False)
                tailscale.assert_not_called()
                self.assertEqual(verify.call_args_list[0].kwargs['host'], 'wiki-rehearsal.invalid')
                configured = dict(line.split('=', 1) for line in (wiki / '.env').read_text().splitlines())
                self.assertEqual(configured['KNOWLEDGE_HUB_ALLOWED_HOSTS'],
                                 'wiki-rehearsal.invalid,wiki-rehearsal.invalid:443')

    def test_final_install_cannot_bypass_tailnet_check(self):
        with patch.object(sys, 'argv', ['host.py', 'install', '--defer-tailscale']), \
                patch.object(host, 'install') as install:
            with self.assertRaises(SystemExit):
                host.main()
            install.assert_not_called()

    def test_running_oneshot_is_stopped_even_while_activating(self):
        with patch.object(subprocess, 'run', side_effect=[
                subprocess.CompletedProcess([], 0, stdout='activating\n'),
                subprocess.CompletedProcess([], 0, stdout='static\n')]):
            self.assertTrue(host.unit_state('transpara-knowledge-hub-refresh.service')['active'])

    def test_preserve_existing_serve_routes_and_funnel(self):
        for config in ({'TCP': {'443': {'HTTPS': True}}},
                       {'Web': {'wiki.ts.net:443': {'Handlers': {}}}},
                       {'AllowFunnel': {'wiki.ts.net:443': True}}):
            with self.assertRaises(RuntimeError):
                host.assert_serve_free(config)
        host.assert_serve_free({'TCP': {'8443': {'HTTPS': True}}})

    def test_environment_is_private_and_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            wiki = Path(tmp)
            token = host.environment(wiki, 8787, 'wiki.example.ts.net')
            self.assertEqual(len(token), 64)
            self.assertEqual((wiki / '.env').stat().st_mode & 0o777, 0o600)
            self.assertIn('WIKI_UID=' + str(os.getuid()), (wiki / '.env').read_text())
            with self.assertRaises(FileExistsError):
                host.environment(wiki, 8787, 'wiki.example.ts.net')

    def test_ambiguous_publication_prevents_source_rollback(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(host, 'BASE', Path(tmp)), \
                patch.object(host, 'serve_config', return_value={}), patch.object(host, 'compose') as compose:
            for phase in ('publishing', 'published'):
                (Path(tmp) / 'installed.json').write_text(json.dumps({'phase': phase}))
                with self.assertRaisesRegex(RuntimeError, 'Publication may have occurred'):
                    host.stop_unpublished()
            compose.assert_not_called()

    def test_unpublished_failure_stops_containers_preserves_data(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(host, 'BASE', Path(tmp)), \
                patch.object(host, 'serve_config', return_value={}), patch.object(host, 'compose') as compose, \
                patch.object(host, 'free_port'):
            receipt = Path(tmp) / 'installed.json'
            receipt.write_text(json.dumps({'phase': 'installed'}))
            host.stop_unpublished()
            compose.assert_called_once_with(host.CANONICAL / 'wiki', 'down')
            self.assertEqual(json.loads(receipt.read_text())['phase'], 'stopped')

    def test_interrupted_freeze_retains_recovery_record(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(host, 'SOURCE_STATE', Path(tmp) / 'freeze.json'), \
                patch.object(host, 'wiki_lock'), patch.object(host, 'unit_state',
                    return_value={'active': True, 'enabled': 'enabled'}), \
                patch.object(host, 'run', side_effect=[None, subprocess.CalledProcessError(1, 'systemctl')]):
            with self.assertRaises(subprocess.CalledProcessError):
                host.freeze()
            saved = json.loads(host.SOURCE_STATE.read_text())
            self.assertEqual(saved['phase'], 'freezing')
            self.assertEqual(set(saved['units']), set(host.UNITS))

    def test_resume_restores_prior_enabled_and_active_states(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(host, 'SOURCE_STATE', Path(tmp) / 'freeze.json'), \
                patch.object(host, 'run') as run:
            units = {'writer.service': {'active': True, 'enabled': 'enabled'},
                     'refresh.timer': {'active': False, 'enabled': 'disabled'}}
            host.SOURCE_STATE.write_text(json.dumps({'units': units}))
            host.resume_source()
            self.assertEqual([tuple(c.args) for c in run.call_args_list],
                             [('systemctl', '--user', 'enable', 'writer.service'),
                              ('systemctl', '--user', 'start', 'writer.service')])
            self.assertFalse(host.SOURCE_STATE.exists())
            self.assertTrue((Path(tmp) / 'last-resume.json').exists())

    def test_git_restore_preserves_uncommitted_and_deleted_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, target = root / 'source', root / 'target'
            source.mkdir()
            target.mkdir()
            subprocess.run(['git', 'init', '-q', str(source)], check=True)
            (source / 'tracked').write_text('original')
            (source / 'deleted').write_text('delete in working tree')
            subprocess.run(['git', '-C', str(source), 'add', '.'], check=True)
            subprocess.run(['git', '-C', str(source), '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.test',
                            'commit', '-qm', 'fixture'], check=True)
            history = root / 'history.bundle'
            subprocess.run(['git', '-C', str(source), 'bundle', 'create', str(history), '--all', 'HEAD'], check=True)
            commit = subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip()
            (target / 'tracked').write_text('uncommitted edit')
            (target / 'upload').write_text('new evidence')
            host.restore_git(target, history, commit)
            self.assertEqual((target / 'tracked').read_text(), 'uncommitted edit')
            self.assertFalse((target / 'deleted').exists())
            self.assertEqual((target / 'upload').read_text(), 'new evidence')


class ControllerTests(unittest.TestCase):
    def test_prepare_leaves_enrollment_to_the_user(self):
        with tempfile.TemporaryDirectory() as tmp:
            argv = ['velia.py', 'prepare', '--source', 'source', '--target', 'target', '--state-dir', tmp]
            with patch.object(sys, 'argv', argv), patch.object(velia, 'ssh') as ssh, \
                    patch.object(velia, 'upload_tools', return_value='/tools'), patch.object(velia, 'phase') as phase:
                velia.main()
                self.assertFalse(any('tailscale' in str(call.args) for call in ssh.call_args_list))
                self.assertEqual(phase.call_args.args[1:], ('target', 'preflight', '--defer-tailscale'))
                self.assertEqual(json.loads((Path(tmp) / 'state.json').read_text())['phase'], 'prepared')

    def test_missing_enrollment_does_not_freeze_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = {'source': 'source', 'target': 'target', 'source_tools': '/tools', 'target_tools': '/tools',
                     'phase': 'rehearsed'}
            record = Path(tmp) / 'state.json'
            record.write_text(json.dumps(state))
            with patch.object(sys, 'argv', ['velia.py', 'cutover', '--state-dir', tmp]), \
                    patch.object(velia, 'phase', side_effect=RuntimeError('Tailscale enrollment required')) as phase:
                with self.assertRaisesRegex(RuntimeError, 'enrollment required'):
                    velia.main()
                self.assertEqual([call.args[1:] for call in phase.call_args_list], [('target', 'preflight')])
                self.assertEqual(json.loads(record.read_text())['phase'], 'rehearsed')

    def test_concurrent_controller_cannot_change_migration_state(self):
        with tempfile.TemporaryDirectory() as tmp, (Path(tmp) / 'controller.lock').open('a') as lock:
            velia.fcntl.flock(lock, velia.fcntl.LOCK_EX | velia.fcntl.LOCK_NB)
            with patch.object(sys, 'argv', ['velia.py', 'verify', '--state-dir', tmp]), \
                    patch.object(velia, 'execute') as execute:
                with self.assertRaisesRegex(RuntimeError, 'Another controller'):
                    velia.main()
                execute.assert_not_called()

    def test_ssh_quotes_remote_arguments_without_forwarding_keys(self):
        with patch.object(subprocess, 'run') as run:
            velia.ssh('wiki', 'python3', 'a path/$(do-not-execute).py')
            cmd = run.call_args.args[0]
            self.assertIn('StrictHostKeyChecking=yes', cmd)
            self.assertNotIn('-A', cmd)
            self.assertEqual(cmd[-1], "python3 'a path/$(do-not-execute).py'")

    def test_target_must_be_stopped_before_source_resumes(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = {'source': 'source', 'target': 'target', 'source_tools': '/tools', 'target_tools': '/tools',
                     'phase': 'source-frozen'}
            (Path(tmp) / 'state.json').write_text(json.dumps(state))
            argv = ['velia.py', 'rollback-source', '--state-dir', tmp]
            with patch.object(sys, 'argv', argv), patch.object(velia, 'phase',
                    side_effect=RuntimeError('target unreachable')) as phase:
                with self.assertRaisesRegex(RuntimeError, 'unreachable'):
                    velia.main()
                self.assertEqual([call.args[1:] for call in phase.call_args_list], [('target', 'stop-unpublished')])


if __name__ == '__main__':
    unittest.main()
