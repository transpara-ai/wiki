# Manual Velia migration with temporary SSH access

Use this procedure while Tailscale admin access is unavailable. It installs the
already rehearsed application on Velia and provides browser access through SSH.
The application stays bound to `127.0.0.1:8787`; SSH encrypts the network traffic.
Enabling MagicDNS and HTTPS Certificates can wait until the later publication
step. Wiki must retain its existing Tailscale enrollment for these installer
phases and for the Mac's connection to `100.116.136.63`.

The saved migration in `/home/transpara/.local/state/wiki-velia-live` completed
this handover on September 11, 2026. Its phase is `ssh-access-active`: Velia is
serving the application, and the original RemoteRepos writer and refresh timer
are stopped and disabled. Start at section 3 for browser access or section 4
for later HTTPS publication. Sections 1–2 describe the initial installation and
must not be replayed over the active target. Use one operator and one controller
at a time.

## 1. Reopen administration access from the Mac

Run this in a Mac terminal and leave it running:

```bash
ssh -NT -l transpara -o ControlMaster=no -o ControlPath=none \
  -o ConnectTimeout=10 -o ExitOnForwardFailure=yes \
  -o ServerAliveInterval=30 -o ServerAliveCountMax=3 \
  -R 127.0.0.1:22292:100.116.136.63:22 RemoteRepos
```

If port 22292 is occupied, close the old wiki tunnel before replacing it.
The separate reverse HTTPS tunnel on port 22443 is unnecessary for this mode.

Open a **shell on RemoteRepos** for the remaining installation commands. The
Mac RSA key used above permits forwarding but not remote shell commands. Use
the Codex task's RemoteRepos terminal or an existing shell-capable SSH key.
The source is RemoteRepos; the destination is Velia's `wiki` VM.

Verify the pinned destination identity and its existing installer prerequisites:

```bash
cd /Transpara/transpara-ai/repos/wiki
ssh -o BatchMode=yes -o ConnectTimeout=10 wiki-velia hostname
ssh wiki-velia python3 /home/transpara/.local/state/transpara-wiki-migration/tools/run-uu7kgeul/host.py preflight
```

Both commands must succeed. This host preflight checks the existing enrollment,
Docker, capacity, free ports and empty destination. It does not require tailnet
HTTPS. Do not run the HTTPS-only `controller-via-mac.py cutover` for this mode.

## 2. Make the final copy and install it

Run the entire block below **on RemoteRepos**. This begins the maintenance
interval: the source writer and refresh units are stopped and disabled before
the final snapshot. Do not edit the source checkout during or after this step.
It uses the existing snapshot, installation and acceptance functions, retains
their recovery records, and checks that the application matches the rehearsal.

```bash
cd /Transpara/transpara-ai/repos/wiki
python3 - <<'PY'
import fcntl
import hashlib
import json
import os
from pathlib import Path
import sys

os.umask(0o077)
root = Path('/Transpara/transpara-ai/repos/wiki')
directory = Path('/home/transpara/.local/state/wiki-velia-live')
sys.path.insert(0, str(root / 'compile/deploy'))
from bundle import application_file, digest, files_under
from velia import phase, relay, save

with (directory / 'controller.lock').open('a') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    path = directory / 'state.json'
    state = json.loads(path.read_text())
    if state.get('phase') != 'rehearsed':
        raise RuntimeError('Inspect the existing state; do not replay this installation')
    if (state.get('source'), state.get('target')) != ('wiki-source-local', 'wiki-velia'):
        raise RuntimeError('Migration host identities differ from this procedure')
    code = {(Path('repos/wiki') / p.relative_to(root)).as_posix(): digest(p)
            for p in files_under(root)
            if application_file(Path('repos/wiki') / p.relative_to(root))}
    application_sha = hashlib.sha256(json.dumps(code, sort_keys=True).encode()).hexdigest()
    if application_sha != state['rehearsal']['application_sha256']:
        raise RuntimeError('Application changed; rehearse it before stopping the source')
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
        raise RuntimeError('Application changed during migration; inspect before recovery')
    phase(state, 'target', 'install', '--archive', bundle['target_path'],
          '--sha256', bundle['sha256'])
    state['phase'] = 'ssh-access-active'
    state['access'] = {'mode': 'ssh-tunnel', 'https_publication': 'pending',
                       'authoring_may_have_started': True}
    save(path, state)
    print('Velia installation and local acceptance passed. Open the SSH browser tunnel next.')
    print('Source remains stopped. HTTPS publication is pending. State:', path)
PY
```

Successful installation verifies all four spaces, the exact active article
inventory, cited external source viewers, rejected unauthenticated rebuilds,
an authenticated rebuild, and persistence across container recreation. A new
editor token is generated only on Velia in `.env` with restricted permissions.
The final snapshot includes current uploads and uncommitted changes; the
September 10 rehearsal bundle is not reused as the final data copy.

The `ssh-access-active` controller phase deliberately prevents the HTTPS
controller's automatic source rollback and first-install commands from running
after editors might have started using Velia. It does not mean HTTPS has been
published. The destination's `installed.json` remains `verified` until that step.

If this block fails, stop here and inspect `state.json` and the reported error.
Before the `ssh-access-active` handover, and before anyone edits Velia, the
existing recovery command is available for its supported failure phases:

```bash
python3 compile/deploy/velia.py rollback-source --state-dir /home/transpara/.local/state/wiki-velia-live
```

Recovery first confirms the destination is unpublished and stops its containers,
then restores the source units' recorded states. It retains the destination data.
An uncertain or completed handover requires reconciling Velia edits before
resuming the old writer. Do not force the controller back to `rehearsed`.

## 3. Open the application from the Mac

In a **second Mac terminal**, run:

```bash
ssh -NT -i ~/.ssh/id_ed25519 -o IdentitiesOnly=yes \
  -o HostKeyAlias=wiki.corp.transpara.com -o StrictHostKeyChecking=yes \
  -o ExitOnForwardFailure=yes -o ConnectTimeout=10 \
  -o ServerAliveInterval=30 -o ServerAliveCountMax=3 \
  -L 127.0.0.1:8787:127.0.0.1:8787 transpara@100.116.136.63
```

This uses the wiki host identity already trusted by the Mac under
`wiki.corp.transpara.com`. Keep this terminal running. If local port 8787 is
occupied by an old wiki forward, close that old forward first.

Open **http://127.0.0.1:8787/** on the Mac. In another Mac terminal, check:

```bash
curl --fail http://127.0.0.1:8787/api/health
curl --fail http://127.0.0.1:8787/version.json
```

The expected version at the rehearsal was `0.4.0`. Check all four spaces, search,
Repos, Sources and Ingest. Retrieve the new editor token from
`/Transpara/transpara-ai/repos/wiki/.env` on **Velia** into your password manager
and enter it on Ingest. Keep the token out of chat and deployment logs. Run
**Refresh status and rebuild** at the bottom of Batch ingest. No document or
section selection is needed for this check. The button shows **Rebuilding…**
while it runs, then **Rebuild completed.** appears beside it after the page reloads.
Other readers need their own authorized SSH access and local tunnel until the
private HTTPS endpoint is available. Displayed status and activity timestamps
use the browsing user's local timezone automatically, including daylight saving.

The administration reverse tunnel may be closed after verification; each
browser's local SSH tunnel must remain open while that browser is in use.
Velia's containers continue running independently of these tunnels.

## 4. Publish private HTTPS later, without copying data again

Once a Tailscale administrator enables MagicDNS and HTTPS Certificates, reopen
the administration tunnel if needed. Run the following **on RemoteRepos**:

```bash
cd /Transpara/transpara-ai/repos/wiki
python3 - <<'PY'
import fcntl
import json
from pathlib import Path
import sys
sys.path.insert(0, 'compile/deploy')
from velia import phase, save, ssh
directory = Path('/home/transpara/.local/state/wiki-velia-live')
with (directory / 'controller.lock').open('a') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    path = directory / 'state.json'
    state = json.loads(path.read_text())
    if state.get('phase') != 'ssh-access-active':
        raise RuntimeError('Inspect the current phase before publication')
    status = json.loads(ssh(state['target'], 'sudo', '-n', 'tailscale',
                            'status', '--json', capture=True))
    dns = status.get('Self', {}).get('DNSName', '').rstrip('.')
    if (status.get('BackendState') != 'Running'
            or not status.get('CurrentTailnet', {}).get('MagicDNSEnabled')
            or dns not in (status.get('CertDomains') or [])):
        raise RuntimeError('Tailnet HTTPS prerequisites are not ready')
    state['phase'] = 'publishing'
    save(path, state)
    phase(state, 'target', 'publish')
    state['phase'] = 'published'
    state['access']['https_publication'] = 'published'
    save(path, state)
    print('Verify the private endpoint from the Mac: https://' + dns)
PY
```

This publishes the existing, verified installation. It does not freeze, copy,
unpack or reinstall anything, so newer Velia content is retained. If publication
fails or the connection drops, inspect both the controller state and target
receipt; do not reset the phase or restore the old writer automatically.

From the Mac, verify the new transport directly:

```bash
curl --fail https://wiki.tail7b566d.ts.net/api/health
curl --fail https://wiki.tail7b566d.ts.net/version.json
```

Open the printed URL and check all four spaces, source links, navigation,
search and an authenticated rebuild. Record those results beside `state.json`.
The snapshot-based automated verifier expects the original article inventory;
if articles were created or retired while using SSH, its inventory check no
longer describes the current corpus. Keep the newer Velia content when assessing
that difference. The old source writer and refresh timer stay disabled after
the move.
