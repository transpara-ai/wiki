#!/usr/bin/env python3
"""Linux-side migration phases. Called by velia.py over the existing SSH connection."""
import argparse
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import socket
import subprocess
import time

from bundle import CANONICAL, digest, unpack, wiki_lock
from verify import verify

BASE = CANONICAL.parent / '.wiki-migration'
SOURCE_STATE = Path.home() / '.local/state/transpara-wiki-migration/freeze.json'
UNITS = ('transpara-knowledge-hub-refresh.timer', 'transpara-knowledge-hub-refresh.service',
         'transpara-knowledge-hub.service', 'transpara-ai-civilization-wiki-refresh.timer',
         'transpara-ai-civilization-wiki-refresh.service', 'transpara-ai-civilization-wiki.service',
         'wiki-autodeploy.timer', 'wiki-autodeploy.service',
         'civwiki-autodeploy.timer', 'civwiki-inflight.timer')


def run(*args, **kwargs):
    return subprocess.run(list(map(str, args)), check=True, text=True, **kwargs)


def capture(*args):
    return run(*args, stdout=subprocess.PIPE).stdout.strip()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temp = path.with_suffix('.tmp')
    with open(temp, 'w', opener=lambda p, f: os.open(p, f, 0o600)) as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp, path)


def free_port(port):
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', port))


def tailscale():
    status = json.loads(capture('sudo', '-n', 'tailscale', 'status', '--json'))
    dns = status.get('Self', {}).get('DNSName', '').rstrip('.')
    if status.get('BackendState') != 'Running' or not re.fullmatch(r'[a-zA-Z0-9.-]+\.ts\.net', dns):
        raise RuntimeError('Tailscale enrollment required; use an existing auth-key file or tailscale up login')
    return dns


def serve_config():
    return json.loads(capture('sudo', '-n', 'tailscale', 'serve', 'status', '--json') or '{}')


def assert_serve_free(config):
    # First install owns only TCP 443. Leave other ports and routes untouched.
    if config.get('TCP', {}).get('443') or any(key.endswith(':443') for key in config.get('Web', {})):
        raise RuntimeError('Tailscale port 443 is occupied; existing Serve routes were preserved')
    if any(config.get('AllowFunnel', {}).values()):
        raise RuntimeError('Existing Funnel configuration requires review before private wiki installation')


def preflight(require_tailnet=True):
    if os.getuid() == 0:
        raise RuntimeError('Run as the non-root deployment user')
    run('sudo', '-n', 'true')
    run('sudo', '-n', 'docker', 'info', stdout=subprocess.DEVNULL)
    run('sudo', '-n', 'docker', 'compose', 'version')
    dns = None
    if require_tailnet:
        dns = tailscale()
        assert_serve_free(serve_config())
    free_port(8787)
    if CANONICAL.exists() and (CANONICAL.is_symlink() or any(CANONICAL.iterdir())):
        raise RuntimeError('First installation requires an absent or empty ' + str(CANONICAL))
    if not os.access(CANONICAL.parent, os.W_OK):
        raise RuntimeError('Deployment user needs write access to ' + str(CANONICAL.parent))
    if shutil.disk_usage(CANONICAL.parent).free < 5 * 1024**3:
        raise RuntimeError('At least 5 GiB free is required for staging and Docker rehearsal')
    # Compose's fixed project name must not point to an unrelated installation.
    if capture('sudo', '-n', 'docker', 'ps', '-aq', '--filter', 'label=com.docker.compose.project=transpara-wiki'):
        raise RuntimeError('The transpara-wiki Compose project already exists')
    print(json.dumps({'ready': True, 'tailnet_checked': require_tailnet,
                      'dns': dns, 'uid': os.getuid(), 'gid': os.getgid()}))


def unit_state(unit):
    def query(flag):
        return subprocess.run(['systemctl', '--user', flag, unit], text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.strip()
    return {'active': query('is-active') in ('active', 'activating', 'reloading', 'deactivating'),
            'enabled': query('is-enabled')}


def freeze():
    if SOURCE_STATE.exists():
        raise RuntimeError('A source freeze record exists; inspect it before another cutover: ' + str(SOURCE_STATE))
    run('systemctl', '--user', 'show-environment', stdout=subprocess.DEVNULL)
    states = {unit: unit_state(unit) for unit in UNITS}
    with wiki_lock(CANONICAL / 'wiki'):
        write_json(SOURCE_STATE, {'phase': 'freezing', 'units': states})
        for unit, state in states.items():
            if state['enabled'] in ('enabled', 'enabled-runtime'):
                run('systemctl', '--user', 'disable', unit)
            if state['active']:
                run('systemctl', '--user', 'stop', unit)
        free_port(8787)  # A writer outside these units is not silently assumed stopped.
        write_json(SOURCE_STATE, {'phase': 'frozen', 'units': states})
    print('Source writer and refresh units stopped; their previous states are recorded.')


def resume_source():
    state = json.loads(SOURCE_STATE.read_text())
    for unit, before in state['units'].items():
        if before['enabled'] in ('enabled', 'enabled-runtime'):
            flags = ['--runtime'] if before['enabled'] == 'enabled-runtime' else []
            run('systemctl', '--user', 'enable', *flags, unit)
        # A completed oneshot refresh should run by its timer, not be replayed here.
        if before['active'] and ('refresh.service' not in unit and 'autodeploy.service' not in unit):
            run('systemctl', '--user', 'start', unit)
    write_json(SOURCE_STATE.with_name('last-resume.json'), state)
    SOURCE_STATE.unlink()
    print('Original source unit states restored.')


def compose(wiki, *args):
    return run('sudo', '-n', 'docker', 'compose', '--project-directory', wiki,
               '-f', wiki / 'compose.yaml', *args)


def environment(wiki, port, dns):
    env = wiki / '.env'
    token = secrets.token_hex(32)
    with open(env, 'x', opener=lambda p, f: os.open(p, f, 0o600)) as stream:
        stream.write('WIKI_UID=%d\nWIKI_GID=%d\nWIKI_PORT=%d\nWIKI_REPOS_DIR=%s\n'
                     'KNOWLEDGE_HUB_AUTHORING_TOKEN=%s\nKNOWLEDGE_HUB_ALLOWED_HOSTS=%s,%s:443\n'
                     'KNOWLEDGE_HUB_REFRESH_SECONDS=900\n'
                     % (os.getuid(), os.getgid(), port, wiki.parent, token, dns, dns))
    return token


def restore_git(wiki, bundle, commit):
    run('git', 'init', '--quiet', wiki)
    run('git', '-C', wiki, 'fetch', '--quiet', bundle, 'HEAD')
    if capture('git', '-C', wiki, 'rev-parse', 'FETCH_HEAD') != commit:
        raise RuntimeError('Git history does not match snapshot commit')
    run('git', '-C', wiki, 'update-ref', '--no-deref', 'HEAD', commit)
    run('git', '-C', wiki, 'read-tree', commit)
    run('git', '-C', wiki, 'remote', 'add', 'origin', 'https://github.com/transpara-ai/wiki.git')


def install(archive, sha, rehearsal=False):
    preflight(require_tailnet=not rehearsal)
    work = BASE / (('rehearsal-' if rehearsal else 'install-') + sha[:16])
    manifest = unpack(archive, sha, work)
    if shutil.disk_usage(BASE).free < sum(f['bytes'] for f in manifest['files'].values()) * 3:
        raise RuntimeError('Insufficient free space for installation and recovery copies')
    wiki = work / 'repos/wiki'
    restore_git(wiki, work / 'wiki-history.bundle', manifest['source_commit'])
    dns = 'wiki-rehearsal.invalid' if rehearsal else tailscale()
    port = 18787 if rehearsal else 8787
    if not rehearsal:
        if CANONICAL.exists():
            CANONICAL.rmdir()  # Empty only; fails if anything appeared since preflight.
        os.rename(work / 'repos', CANONICAL)
        wiki = CANONICAL / 'wiki'
        write_json(BASE / 'installed.json', {'sha256': sha, 'manifest': str(work / 'manifest.json'),
                                           'phase': 'installed', 'dns': dns})
    token = environment(wiki, port, dns)
    try:
        compose(wiki, 'config', '--quiet')
        compose(wiki, 'up', '-d', '--build', '--wait', '--wait-timeout', '300')
        result = verify('http://127.0.0.1:%d' % port, manifest, token=token, host=dns)
        compose(wiki, 'up', '-d', '--no-build', '--force-recreate', '--wait', '--wait-timeout', '300')
        verify('http://127.0.0.1:%d' % port, manifest, host=dns)
        if rehearsal:
            run('python3', wiki / 'compile/test_deployment.py')
            # Existing corpus-write/persistence tests create and remove their own checkout/project.
            variables = ('WIKI_UID,WIKI_GID,WIKI_REPOS_DIR,WIKI_PORT,KNOWLEDGE_HUB_AUTHORING_TOKEN,'
                         'KNOWLEDGE_HUB_ALLOWED_HOSTS,KNOWLEDGE_HUB_REFRESH_SECONDS')
            test_env = dict(os.environ, WIKI_TEST_DOCKER_COMMAND='sudo -n --preserve-env=' + variables + ' docker')
            run('python3', wiki / 'compile/test_docker.py', env=test_env)
        write_json(work / 'verification.json', result)
        if not rehearsal:
            receipt = json.loads((BASE / 'installed.json').read_text())
            receipt['phase'] = 'verified'
            write_json(BASE / 'installed.json', receipt)
        print(json.dumps(result))
    finally:
        if rehearsal:
            compose(wiki, 'down')


def publish():
    path = BASE / 'installed.json'
    receipt = json.loads(path.read_text())
    if receipt['phase'] != 'verified':
        raise RuntimeError('Only a verified installation may be published')
    dns = tailscale()
    if dns != receipt['dns']:
        raise RuntimeError('Tailscale identity changed after installation')
    assert_serve_free(serve_config())
    receipt['phase'] = 'publishing'
    write_json(path, receipt)  # Persist uncertainty before external route mutation.
    run('sudo', '-n', 'tailscale', 'serve', '--bg', '--https=443', 'http://127.0.0.1:8787', timeout=60)
    config = serve_config()
    handler = config.get('Web', {}).get(dns + ':443', {}).get('Handlers', {}).get('/', {})
    if handler.get('Proxy') != 'http://127.0.0.1:8787' or any(config.get('AllowFunnel', {}).values()):
        raise RuntimeError('Serve configuration did not match the private wiki endpoint')
    receipt['phase'] = 'published'
    write_json(path, receipt)
    print('https://' + dns)


def stop_unpublished():
    receipt_path = BASE / 'installed.json'
    assert_serve_free(serve_config())
    if receipt_path.exists():
        receipt = json.loads(receipt_path.read_text())
        if receipt['phase'] in ('publishing', 'published'):
            raise RuntimeError('Publication may have occurred; reconcile Velia edits before rollback')
        compose(CANONICAL / 'wiki', 'down')
        receipt['phase'] = 'stopped'
        write_json(receipt_path, receipt)
    free_port(8787)
    print('Target is unpublished and stopped. Its data has been retained.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('preflight', 'freeze', 'resume-source', 'rehearse', 'install',
                                          'publish', 'stop-unpublished', 'receipt'))
    parser.add_argument('--archive', type=Path)
    parser.add_argument('--sha256')
    parser.add_argument('--defer-tailscale', action='store_true',
                        help='For preflight only: check host prerequisites before separate Tailscale enrollment')
    args = parser.parse_args()
    if args.defer_tailscale and args.action != 'preflight':
        parser.error('--defer-tailscale applies only to preflight; installation and publication require enrollment')
    if args.action in ('install', 'rehearse'):
        if not args.archive or not args.sha256 or not re.fullmatch('[a-f0-9]{64}', args.sha256):
            parser.error('install/rehearse require --archive and --sha256')
        install(args.archive, args.sha256, rehearsal=args.action == 'rehearse')
    elif args.action == 'receipt':
        print((BASE / 'installed.json').read_text())
    elif args.action == 'preflight':
        preflight(require_tailnet=not args.defer_tailscale)
    else:
        {'freeze': freeze, 'resume-source': resume_source,
         'publish': publish, 'stop-unpublished': stop_unpublished}[args.action]()


if __name__ == '__main__':
    main()
