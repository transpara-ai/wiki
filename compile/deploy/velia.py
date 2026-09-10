#!/usr/bin/env python3
"""Mac/Linux controller: authenticated SSH to each host; no host-to-host route needed."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
REMOTE_BASE = '/Transpara/transpara-ai/.wiki-migration'
SSH_FLAGS = ['-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
             '-o', 'ConnectTimeout=10', '-o', 'ServerAliveInterval=15', '-o', 'ServerAliveCountMax=3']


def ssh(host, *args, capture=False, data=None):
    result = subprocess.run(['ssh', *SSH_FLAGS, host, shlex.join(map(str, args))],
                            input=data, stdout=subprocess.PIPE if capture else None, check=True)
    return result.stdout.decode().strip() if capture else None


def save(path, state):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(state, indent=2) + '\n')
    temporary.chmod(0o600)
    os.replace(temporary, path)


def upload_tools(host):
    remote = ssh(host, 'python3', '-c',
                 'from pathlib import Path; import tempfile; '
                 'p=Path.home()/".local/state/transpara-wiki-migration/tools"; '
                 'p.mkdir(parents=True,exist_ok=True,mode=0o700); '
                 'print(tempfile.mkdtemp(prefix="run-",dir=p))', capture=True)
    if not re.fullmatch(r'/[A-Za-z0-9_./-]+/run-[A-Za-z0-9_-]+', remote):
        raise RuntimeError('Unexpected remote staging path')
    for name in ('bundle.py', 'host.py', 'verify.py'):
        ssh(host, 'python3', '-c',
            'import pathlib,sys; pathlib.Path(sys.argv[1]).write_bytes(sys.stdin.buffer.read())',
            remote + '/' + name, data=(HERE / name).read_bytes())
    return remote


def phase(state, which, action, *args, capture=False):
    return ssh(state[which], 'python3', state[which + '_tools'] + '/host.py', action, *args, capture=capture)


def relay(state, directory):
    stamp = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
    name = 'wiki-' + stamp + '.tar.gz'
    source_path = ssh(state['source'], 'python3', '-c',
                      'from pathlib import Path; p=Path.home()/".local/state/transpara-wiki-migration/bundles"; '
                      'p.mkdir(parents=True,exist_ok=True,mode=0o700); print(p)', capture=True) + '/' + name
    result = json.loads(ssh(state['source'], 'python3', state['source_tools'] + '/bundle.py',
                            'snapshot', '--output', source_path, capture=True).splitlines()[-1])
    local = directory / name
    subprocess.run(['scp', *SSH_FLAGS, state['source'] + ':' + source_path, str(local)], check=True)
    local.chmod(0o600)
    with local.open('rb') as stream:
        digest = hashlib.sha256()
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    if digest.hexdigest() != result['sha256']:
        raise RuntimeError('Mac relay checksum mismatch')
    target_path = REMOTE_BASE + '/' + name
    subprocess.run(['scp', *SSH_FLAGS, str(local), state['target'] + ':' + target_path], check=True)
    result['target_path'] = target_path
    result['local_path'] = str(local)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', 'rehearse', 'cutover', 'verify', 'rollback-source'))
    parser.add_argument('--source', help='Existing Mac SSH alias or user@host for RemoteRepos')
    parser.add_argument('--target', help='Defaults to transpara@192.168.30.192; later phases use the saved host')
    parser.add_argument('--tailscale-auth-key-file', type=Path,
                        help='Optional existing auth key on the Mac, used only during prepare')
    parser.add_argument('--state-dir', type=Path, default=Path.home() / '.local/state/wiki-velia')
    args = parser.parse_args()
    os.umask(0o077)
    for command in ('ssh', 'scp'):
        if not shutil.which(command):
            parser.error(command + ' is required')
    directory = args.state_dir.expanduser().resolve()
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    directory.chmod(0o700)
    with (directory / 'controller.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError('Another controller is using this migration state directory')
        execute(args, parser, directory)


def execute(args, parser, directory):
    path = directory / 'state.json'
    state = json.loads(path.read_text()) if path.exists() else {}
    if args.action == 'prepare':
        args.target = args.target or 'transpara@192.168.30.192'
        if not args.source:
            parser.error('prepare requires --source (your working SSH alias)')
        for host in (args.source, args.target):
            if not re.fullmatch(r'[A-Za-z0-9_][A-Za-z0-9_.@-]*', host):
                parser.error('Use an SSH alias or user@host; configure keys and jump hosts in ~/.ssh/config')
        if state.get('phase') not in (None, 'prepared'):
            raise RuntimeError('This run already has migration state; retain it and use a new state directory')
        state.update(source=args.source, target=args.target)
        ssh(args.source, 'true')
        ssh(args.target, 'sudo', '-n', 'bash', '-s', data=(HERE / 'bootstrap.sh').read_bytes())
        state['source_tools'] = upload_tools(args.source)
        state['target_tools'] = upload_tools(args.target)
        save(path, state)
        enrolled = {}
        if args.tailscale_auth_key_file:
            # The CLI may return a nonzero status while signed out; retain its JSON state.
            enrolled = json.loads(ssh(args.target, 'python3', '-c',
                'import subprocess; p=subprocess.run(["sudo","-n","tailscale","status","--json"],'
                'text=True,stdout=subprocess.PIPE); print(p.stdout)', capture=True))
        if args.tailscale_auth_key_file and enrolled.get('BackendState') != 'Running':
            key_file = args.tailscale_auth_key_file.expanduser()
            if key_file.stat().st_mode & 0o077:
                raise RuntimeError('Tailscale auth key file must have mode 0600 or stricter')
            remote_key = state['target_tools'] + '/tailscale-auth-key'
            ssh(args.target, 'python3', '-c',
                'import os,sys; fd=os.open(sys.argv[1],os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600); '
                'f=os.fdopen(fd,"wb"); f.write(sys.stdin.buffer.read()); f.close()',
                remote_key, data=key_file.read_bytes())
            try:
                ssh(args.target, 'sudo', '-n', 'tailscale', 'up', '--timeout=60s', '--auth-key=file:' + remote_key)
            finally:
                ssh(args.target, 'rm', '--', remote_key)
        phase(state, 'target', 'preflight', '--defer-tailscale')
        state['phase'] = 'prepared'
        print('Host prepared for rehearsal. Tailscale enrollment will be checked before cutover.')
    else:
        if not state.get('source_tools') or not state.get('target_tools'):
            parser.error('Run prepare first using this state directory')
        if (args.source and args.source != state['source']) or (args.target and args.target != state['target']):
            parser.error('Host arguments differ from this run; use the original target and source')
        if args.action == 'rehearse':
            if state.get('phase') not in ('prepared', 'rehearsed'):
                raise RuntimeError('Rehearsal requires a prepared, uninstalled target')
            bundle = relay(state, directory)
            phase(state, 'target', 'rehearse', '--archive', bundle['target_path'], '--sha256', bundle['sha256'])
            state['rehearsal'] = bundle
            state['phase'] = 'rehearsed'
        elif args.action == 'cutover':
            if state.get('phase') != 'rehearsed':
                raise RuntimeError('A successful rehearsal is required before cutover')
            phase(state, 'target', 'preflight')
            state['phase'] = 'freezing-source'
            save(path, state)
            phase(state, 'source', 'freeze')
            state['phase'] = 'source-frozen'
            save(path, state)
            bundle = relay(state, directory)
            state['final_bundle'] = bundle
            save(path, state)
            if bundle['application_sha256'] != state['rehearsal']['application_sha256']:
                raise RuntimeError('Application changed since rehearsal; restore source and rehearse the new code')
            phase(state, 'target', 'install', '--archive', bundle['target_path'], '--sha256', bundle['sha256'])
            state['phase'] = 'target-verified'
            save(path, state)
            phase(state, 'target', 'publish')
            state['phase'] = 'published'
            save(path, state)
            verify_remote(state)
            state['phase'] = 'complete'
        elif args.action == 'verify':
            verify_remote(state)
        elif args.action == 'rollback-source':
            if state.get('phase') not in ('freezing-source', 'source-frozen', 'target-verified'):
                raise RuntimeError('Automatic source recovery is only available before publication')
            # This fails closed if target state is unreachable or publication is ambiguous.
            phase(state, 'target', 'stop-unpublished')
            phase(state, 'source', 'resume-source')
            state['phase'] = 'rolled-back'
    save(path, state)
    print('Migration phase: ' + state['phase'] + '; record: ' + str(path))


def verify_remote(state):
    receipt = json.loads(phase(state, 'target', 'receipt', capture=True))
    if receipt['phase'] != 'published':
        raise RuntimeError('Private endpoint has not been published')
    # Read the snapshot manifest via SSH, then test HTTPS FROM the Mac/controller.
    manifest = json.loads(ssh(state['target'], 'cat', receipt['manifest'], capture=True))
    from verify import verify
    print(json.dumps(verify('https://' + receipt['dns'], manifest), indent=2))
    print('Private wiki: https://' + receipt['dns'])


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, OSError, ValueError, subprocess.SubprocessError) as error:
        print('Migration stopped: ' + str(error), file=sys.stderr)
        print('Copies and state are retained. Inspect state.json before retrying or rollback-source.', file=sys.stderr)
        sys.exit(1)
