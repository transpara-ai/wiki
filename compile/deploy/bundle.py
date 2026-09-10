#!/usr/bin/env python3
"""Portable, verified migration snapshots; no third-party Python dependencies."""
import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time

CANONICAL = Path('/Transpara/transpara-ai/repos')
SOURCE_ROOTS = ('platform', 'ai-sdr', 'docs/dark-factory', 'docs/civilization',
                'OB1', 'bitsandpieces', 'gstack', 'solo-orchestrator')
SOURCE_SUFFIXES = {'.md', '.txt', '.json', '.yml', '.yaml', '.csv', '.toml'}
SKIP_DIRS = {'.git', '.venv', 'node_modules', '__pycache__', '.cache',
             'dist', 'test-results', 'playwright-report', '.adversarial-review', '.superpowers'}


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest() if hasattr(hashlib, 'file_digest') else _digest(stream)


def _digest(stream):
    result = hashlib.sha256()
    for block in iter(lambda: stream.read(1024 * 1024), b''):
        result.update(block)
    return result.hexdigest()


def excluded(name):
    return (name in SKIP_DIRS or name.startswith('dist-') or name == '.env'
            or (name.startswith('.env.') and name != '.env.example')
            or name.endswith(('.lock', '.tmp', '.log', '-authorization.json'))
            and not name.endswith('-authorization.example.json'))


def files_under(root):
    for directory, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if not excluded(d))
        for name in dirs + sorted(files):
            path = Path(directory) / name
            if excluded(name):
                continue
            if path.is_symlink():
                raise ValueError('Snapshot refuses symlinks: ' + str(path))
            if path.is_file():
                yield path
            elif not path.is_dir():
                raise ValueError('Snapshot refuses special files: ' + str(path))


def application_file(path):
    if path.parts[:2] != ('repos', 'wiki'):
        return False
    relative = path.relative_to('repos/wiki')
    if relative.parts[:2] == ('compile', 'assets') or relative.parts[0] == 'assets':
        return True
    if relative.parts[0] == 'compile' and relative.suffix in ('.py', '.sh', '.js'):
        return True
    return relative.as_posix() in {
        'compile/knowledge_structure.json', 'package.json', 'package-lock.json',
        'requirements.txt', 'Dockerfile', 'compose.yaml', '.dockerignore'}


@contextmanager
def wiki_lock(root, timeout=300):
    with (root / 'compile/.wiki-write.lock').open('a') as lock:
        deadline = time.monotonic() + timeout
        while True:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise TimeoutError('Wiki writer did not release its lock')
                time.sleep(0.2)
        try:
            yield
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def snapshot(root, output):
    root, output = root.resolve(), output.resolve()
    if output == root or root in output.parents:
        raise ValueError('Store migration bundles outside the wiki checkout')
    if output.exists():
        raise FileExistsError(output)
    output.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    sys.path.insert(0, str(root / 'compile'))
    from article_catalog import load_catalog
    with wiki_lock(root), tempfile.TemporaryDirectory(dir=output.parent) as work:
        work = Path(work)
        stage = work / 'payload'
        stage.mkdir()
        catalog = load_catalog(root)
        references = sorted({ref for article in catalog for ref in article.sources + article.raw_documents
                             if ref.startswith(str(CANONICAL) + '/')})
        selected = {Path('repos/wiki') / p.relative_to(root): p for p in files_under(root)}
        missing = []
        for ref in references:
            relative = Path(ref).relative_to(CANONICAL)
            if relative.parts[0] == 'wiki':
                continue
            if not any(relative == Path(base) or Path(base) in relative.parents for base in SOURCE_ROOTS):
                continue  # Match the source viewer's existing scope.
            source = root.parent / relative
            if source.is_symlink() or source.resolve() != source:
                raise ValueError('External source must not traverse a symlink: ' + str(source))
            if source.is_file():
                selected[Path('repos') / relative] = source
            else:
                missing.append(ref)
        mirror = root.parent / 'docs/dark-factory'
        if mirror.exists():
            # refresh.py uses rsync --delete: include the WHOLE Markdown input tree.
            for source in files_under(mirror):
                if source.suffix.lower() == '.md' or source.name == '.civilization-archive.json':
                    selected[Path('repos/docs/dark-factory') / source.relative_to(mirror)] = source
        for relative, source in selected.items():
            dest = stage / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
        git = ['git', '-C', str(root)]
        commit = subprocess.check_output(git + ['rev-parse', 'HEAD'], text=True).strip()
        subprocess.run(git + ['bundle', 'create', str(stage / 'wiki-history.bundle'), '--all', 'HEAD'], check=True)
        code_files = {p.as_posix(): digest(stage / p) for p in selected if application_file(p)}
        application_sha = hashlib.sha256(json.dumps(code_files, sort_keys=True).encode()).hexdigest()
        manifest = {'schema': 1, 'source_commit': commit, 'source_root': str(root),
                    'created_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                    'version': json.loads((root / 'package.json').read_text())['version'],
                    'article_count': len(catalog), 'active_article_slugs': [a.slug for a in catalog if not a.retired_on],
                    'external_source_refs': [str(CANONICAL / p.relative_to('repos')) for p in selected
                                             if p.parts[0] == 'repos' and p.parts[1] != 'wiki'
                                             and p.suffix.lower() in SOURCE_SUFFIXES
                                             and str(CANONICAL / p.relative_to('repos')) in references],
                    'application_sha256': application_sha, 'missing_sources_at_source': missing,
                    'files': {p.relative_to(stage).as_posix(): {'sha256': digest(p), 'bytes': p.stat().st_size}
                              for p in stage.rglob('*') if p.is_file()}}
        (stage / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
        archive = work / 'bundle.tar.gz'
        with tarfile.open(archive, 'w:gz', dereference=True) as tar:
            for p in sorted(stage.rglob('*')):
                if p.is_file():
                    tar.add(p, arcname=p.relative_to(stage).as_posix(), recursive=False)
        archive.chmod(0o600)
        os.replace(archive, output)
    print(json.dumps({'bundle': str(output), 'sha256': digest(output),
                      'articles': manifest['article_count'], 'files': len(manifest['files']),
                      'application_sha256': application_sha, 'missing_sources_at_source': missing}))


def unpack(archive, expected, destination):
    """Check transport hash and every member before installing into a NEW directory."""
    archive, destination = Path(archive), Path(destination)
    if destination.exists() or destination.is_symlink():
        raise FileExistsError('Refusing occupied destination: ' + str(destination))
    if digest(archive) != expected:
        raise ValueError('Bundle checksum mismatch')
    with tarfile.open(archive, 'r:gz') as tar:
        members = tar.getmembers()
        names = set()
        for member in members:
            path = PurePosixPath(member.name)
            if (not member.isfile() or path.is_absolute() or '..' in path.parts
                    or str(path) != member.name or member.name in names):
                raise ValueError('Unsafe or duplicate archive member: ' + member.name)
            names.add(member.name)
        if 'manifest.json' not in names:
            raise ValueError('Bundle has no manifest')
        manifest = json.load(tar.extractfile('manifest.json'))
        if manifest.get('schema') != 1 or names != set(manifest['files']) | {'manifest.json'}:
            raise ValueError('Bundle manifest membership mismatch')
        for member in members:
            if member.name == 'manifest.json':
                continue
            expected_file = manifest['files'][member.name]
            with tar.extractfile(member) as data:
                if member.size != expected_file['bytes'] or _digest(data) != expected_file['sha256']:
                    raise ValueError('File checksum mismatch: ' + member.name)
        destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        with tempfile.TemporaryDirectory(dir=destination.parent) as scratch:
            stage = Path(scratch) / 'verified'
            stage.mkdir()
            for member in members:
                path = stage / member.name
                path.parent.mkdir(parents=True, exist_ok=True)
                with tar.extractfile(member) as source, path.open('xb') as target:
                    shutil.copyfileobj(source, target)
                path.chmod(0o755 if member.mode & 0o111 else 0o644)
            os.rename(stage, destination)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    export = sub.add_parser('snapshot')
    export.add_argument('--wiki', type=Path, default=CANONICAL / 'wiki')
    export.add_argument('--output', type=Path, required=True)
    restore = sub.add_parser('unpack')
    restore.add_argument('--archive', type=Path, required=True)
    restore.add_argument('--sha256', required=True)
    restore.add_argument('--destination', type=Path, required=True)
    args = parser.parse_args()
    if args.action == 'snapshot':
        snapshot(args.wiki, args.output)
    else:
        result = unpack(args.archive, args.sha256, args.destination)
        print(json.dumps({'verified_files': len(result['files']), 'articles': result['article_count']}))


if __name__ == '__main__':
    main()
