#!/usr/bin/env python3
"""Validate release metadata; publish stable GitHub Releases from checked main."""
import argparse
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
STABLE = re.compile(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)")


def metadata(root=ROOT):
    package = json.loads((root / 'package.json').read_text())
    lock = json.loads((root / 'package-lock.json').read_text())
    version = package['version']
    if not isinstance(version, str) or not STABLE.fullmatch(version):
        raise ValueError('Releases require stable MAJOR.MINOR.PATCH SemVer')
    if lock['version'] != version or lock['packages']['']['version'] != version:
        raise ValueError('Package and lockfile versions must match')
    notes = root / 'docs' / 'releases' / ('v' + version + '.md')
    text = notes.read_text().strip()
    if text.startswith('---\n'):
        from article_catalog import split_frontmatter, scalar
        frontmatter, text = split_frontmatter(text)
        if scalar(frontmatter, 'version') != version:
            raise ValueError('Release notes frontmatter version must match the application')
        text = text.strip()
    if not text.startswith('# v' + version + '\n') or len(text.splitlines()) < 3:
        raise ValueError('Commit release notes headed # v' + version)
    return version, notes


def run(*args):
    return subprocess.check_output(args, text=True, stderr=subprocess.PIPE, timeout=60).strip()


def api(endpoint):
    try:
        return json.loads(run('gh', 'api', endpoint))
    except subprocess.CalledProcessError as exc:
        if '(HTTP 404)' in exc.stderr:
            return None
        raise


def publish(commit, repo, root=ROOT):
    version, notes = metadata(root)
    if not re.fullmatch(r'[0-9a-f]{40}', commit):
        raise ValueError('Publish an exact checked commit')
    if run('git', 'rev-parse', 'HEAD') != commit:
        raise ValueError('Checkout does not match the checked commit')
    tag = 'v' + version
    existing = api(f'repos/{repo}/releases/tags/{tag}')
    if existing:
        if existing['draft'] or existing['prerelease']:
            raise ValueError('Existing release is not published and stable; correct it explicitly')
        print('Already published: ' + existing['html_url'])
        return
    latest = api(f'repos/{repo}/releases/latest')
    if latest:
        prior = latest['tag_name'].removeprefix('v')
        if not STABLE.fullmatch(prior) or tuple(map(int, version.split('.'))) <= tuple(map(int, prior.split('.'))):
            raise ValueError('A new release must advance the latest stable version')
    # A failed publication can leave a tag; never silently release another commit.
    ref = api(f'repos/{repo}/git/ref/tags/{tag}')
    if ref:
        target = ref['object']
        while target['type'] == 'tag':
            target = api(f'repos/{repo}/git/tags/' + target['sha'])['object']
        if target['type'] != 'commit' or target['sha'] != commit:
            raise ValueError('Existing tag points to another commit; do not move it')
    print(run('gh', 'release', 'create', tag, '--repo', repo, '--target', commit,
              '--title', tag, '--notes-file', str(notes), '--latest'))
    published = api(f'repos/{repo}/releases/tags/{tag}')
    if not published or published['draft'] or published['prerelease']:
        raise ValueError('Stable release publication could not be verified')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['check', 'publish'])
    parser.add_argument('--commit')
    parser.add_argument('--repo')
    args = parser.parse_args()
    if args.action == 'publish':
        if not args.commit or not args.repo:
            parser.error('publish requires --commit and --repo')
        publish(args.commit, args.repo)
    else:
        print('Release metadata valid: v' + metadata()[0])
