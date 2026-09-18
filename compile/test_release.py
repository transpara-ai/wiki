#!/usr/bin/env python3
"""Release gates and publication failures, without writing to GitHub."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import release


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.version('0.8.2')
        self.sha = 'a' * 40

    def version(self, version):
        (self.root / 'package.json').write_text(json.dumps({'version': version}))
        (self.root / 'package-lock.json').write_text(json.dumps({
            'version': version, 'packages': {'': {'version': version}}}))
        notes = self.root / 'docs/releases'
        notes.mkdir(parents=True, exist_ok=True)
        (notes / ('v' + version + '.md')).write_text('# v' + version + '\n\nRelease notes.\n')

    def test_stable_metadata_and_missing_notes(self):
        self.assertEqual(release.metadata(self.root)[0], '0.8.2')
        release.metadata(self.root)[1].unlink()
        with self.assertRaises(FileNotFoundError):
            release.metadata(self.root)

    def test_prerelease_and_noncanonical_versions_rejected(self):
        for version in ['0.8.2-rc.1', '0.8.2+build', '00.8.2', 'v0.8.2', '0.8']:
            with self.subTest(version=version):
                self.version(version)
                with self.assertRaises(ValueError):
                    release.metadata(self.root)

    def test_lock_mismatch(self):
        lock = self.root / 'package-lock.json'
        data = json.loads(lock.read_text())
        data['packages']['']['version'] = '0.8.1'
        lock.write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            release.metadata(self.root)

    def test_controlled_notes_must_match_release_version(self):
        notes=release.metadata(self.root)[1]
        body=notes.read_text()
        notes.write_text('---\ndoc_id: RELEASE\nversion: 0.8.2\n---\n\n'+body)
        self.assertEqual(release.metadata(self.root)[0],'0.8.2')
        notes.write_text(notes.read_text().replace('version: 0.8.2','version: 0.8.1'))
        with self.assertRaises(ValueError):
            release.metadata(self.root)

    def test_publishes_exact_commit_and_committed_notes(self):
        stable = {'draft': False, 'prerelease': False}
        with patch.object(release, 'api', side_effect=[None, {'tag_name': 'v0.8.1'}, None, stable]), \
                patch.object(release, 'run', side_effect=[self.sha, 'release URL']) as run:
            release.publish(self.sha, 'example/wiki', self.root)
        args = run.call_args.args
        self.assertIn('--latest', args)
        self.assertEqual(args[args.index('--target') + 1], self.sha)
        self.assertEqual(args[args.index('--notes-file') + 1], str(release.metadata(self.root)[1]))
        self.assertNotIn('--prerelease', args)
        self.assertNotIn('--draft', args)

    def test_existing_stable_release_is_unchanged(self):
        stable = {'draft': False, 'prerelease': False, 'html_url': 'release URL'}
        with patch.object(release, 'api', return_value=stable), \
                patch.object(release, 'run', return_value=self.sha) as run:
            release.publish(self.sha, 'example/wiki', self.root)
        self.assertEqual(run.call_count, 1)

    def test_existing_draft_or_prerelease_fails(self):
        for flags in [{'draft': True, 'prerelease': False}, {'draft': False, 'prerelease': True}]:
            with patch.object(release, 'api', return_value=flags), \
                    patch.object(release, 'run', return_value=self.sha):
                with self.assertRaises(ValueError):
                    release.publish(self.sha, 'example/wiki', self.root)

    def test_cannot_publish_older_version_as_latest(self):
        with patch.object(release, 'api', side_effect=[None, {'tag_name': 'v0.9.0'}]), \
                patch.object(release, 'run', return_value=self.sha):
            with self.assertRaises(ValueError):
                release.publish(self.sha, 'example/wiki', self.root)

    def test_conflicting_tag_is_not_moved(self):
        with patch.object(release, 'api', side_effect=[None, None, {
                'object': {'type': 'commit', 'sha': 'b' * 40}}]), \
                patch.object(release, 'run', return_value=self.sha) as run:
            with self.assertRaises(ValueError):
                release.publish(self.sha, 'example/wiki', self.root)
        self.assertEqual(run.call_count, 1)

    def test_retry_with_matching_annotated_tag(self):
        with patch.object(release, 'api', side_effect=[None, None,
                {'object': {'type': 'tag', 'sha': 'b' * 40}},
                {'object': {'type': 'commit', 'sha': self.sha}},
                {'draft': False, 'prerelease': False}]), \
                patch.object(release, 'run', side_effect=[self.sha, 'release URL']):
            release.publish(self.sha, 'example/wiki', self.root)

    def test_wrong_checkout_fails_before_github(self):
        with patch.object(release, 'run', return_value='b' * 40), patch.object(release, 'api') as api:
            with self.assertRaises(ValueError):
                release.publish(self.sha, 'example/wiki', self.root)
        api.assert_not_called()

    def test_api_failure_is_not_treated_as_missing_release(self):
        for stderr in ['gh: Not Found (HTTP 404)', 'gh: Bad credentials (HTTP 401)', 'network unavailable']:
            with patch.object(release, 'run', side_effect=subprocess.CalledProcessError(1, 'gh', stderr=stderr)):
                if '404' in stderr:
                    self.assertIsNone(release.api('endpoint'))
                else:
                    with self.assertRaises(subprocess.CalledProcessError):
                        release.api('endpoint')


if __name__ == '__main__':
    unittest.main()
