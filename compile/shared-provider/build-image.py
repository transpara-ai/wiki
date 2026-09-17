#!/usr/bin/env python3
"""Build the shared provider using qualified standalone binaries; no credentials."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--codex', type=Path, required=True)
    parser.add_argument('--claude', type=Path, required=True)
    parser.add_argument('--codex-code-mode-host', type=Path, required=True)
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    release_version = json.loads((here.parents[1] / 'package.json').read_text())['version']
    revision = subprocess.check_output(
        ['git', '-C', str(here.parents[1]), 'rev-parse', 'HEAD'], text=True
    ).strip()
    with tempfile.TemporaryDirectory(prefix='shared-provider-build-') as name:
        context = Path(name)
        for source, target, expected_cli_version in (
                (args.codex, 'codex', 'codex-cli 0.153.4'),
                (args.claude, 'claude', '2.1.263 (Claude Code)')):
            if subprocess.check_output([str(source.resolve()), '--version'], text=True).strip() != expected_cli_version:
                raise SystemExit('Unexpected CLI version: ' + target)
            shutil.copyfile(source.resolve(), context / target)
            (context / target).chmod(0o755)
            print(target, 'sha256', hashlib.sha256((context / target).read_bytes()).hexdigest(), flush=True)
        for filename in ('Dockerfile', 'provider-requirements.toml'):
            shutil.copyfile(here / filename, context / filename)
        shutil.copyfile(args.codex_code_mode_host.resolve(), context / 'codex-code-mode-host')
        (context / 'codex-code-mode-host').chmod(0o755)
        subprocess.run([
            'docker', 'build', '-t', f'transpara-provider:{release_version}',
            '--label', f'org.opencontainers.image.version={release_version}',
            '--label', f'org.opencontainers.image.revision={revision}',
            str(context),
        ], check=True)


if __name__ == '__main__':
    main()
