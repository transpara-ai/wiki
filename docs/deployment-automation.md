# Automated migration to the Velia wiki node

Target: **192.168.30.192**, using the existing SSH key and deployment account.
This implements the [Docker hosting guide](../DOCKER.md). Civilization, Transpara
Platform, Competition, and DevOps move together as one application and corpus.

Preparation verified locally on September 10, 2026: 25 migration/recovery tests,
Python and shell syntax checks, ShellCheck, and the repository secret scan passed.
A real source snapshot restored successfully; its isolated container deployment
served all four spaces, 134 active articles (135 records including the retired
record), and 41 cited external source viewers. Authenticated rebuild, container
recreation, and the separate Docker ingestion/persistence suite passed. Four
references already missing on the source were recorded in the snapshot manifest.

The source service and timer remain active. No Velia installation has occurred:
direct SSH from RemoteRepos to the target still times out. The Mac's working SSH
route is the execution path below. Actual target package installation, OS/sudo
preflight, Tailscale enrollment, and private HTTPS still require validation there;
the local container rehearsal did not execute those host-specific phases.
Tailscale authorization is a separate operator step: prerequisite installation
and rehearsal can finish before enrollment, while cutover checks enrollment
before stopping the source. The remaining execution blocker is a reachable SSH
route from this task or an SSH-accessible Mac/jump host.

## Design and scope

The Mac controls two independent SSH connections: one to RemoteRepos, one to
Velia. It keeps a restricted local copy of each migration bundle and relays it
to Velia. RemoteRepos does not need a network route to Velia. Configure the
working key, user, and any jump host in the Mac's existing SSH configuration;
the controller uses strict host-key verification and never forwards an agent.

There are two copies: a rehearsal while the source remains available, then a
final snapshot after its native writer and refresh units are stopped and
disabled. Both snapshots take the same filesystem lock as ingestion. The
final copy introduces a maintenance interval; do not edit the source checkout
manually during this interval. Velia receives its private HTTPS route only
after local verification succeeds. This prevents edits arriving on the old
host between its final snapshot and the switch to the new host.

The scripts target a first installation on an absent or empty
`/Transpara/transpara-ai/repos`. They retain staging directories, bundles,
verification reports, and recovery state, and refuse to overwrite an occupied
installation. Updating an established Velia corpus is a separate operation;
never replay the original snapshot over newer content.

## Prerequisites and automation

| Requirement | Handling |
| --- | --- |
| Mac Python 3.9+, OpenSSH, enough space for two bundles | Controller prerequisites; use the existing Python installation. No Mac Docker, GNU rsync, or flock is needed. |
| SSH identity and known host keys for both servers | Reuse the access already verified on the Mac. Configure aliases before running. |
| Non-root target account with noninteractive sudo | Checked before installation; container UID/GID come from that account. |
| Ubuntu 22.04/24.04/26.04 or Debian 12/13 with systemd | Detected by the bootstrap script; other distributions stop before package changes. |
| Python, Git, rsync, util-linux, CA certificates, curl | Installed through apt. |
| Docker Engine and Compose v2 | Reuse a working installation; otherwise install from Docker's signed package repository. An incompatible existing container stack stops installation. |
| Tailscale | Install from its signed package repository; enable Docker and tailscaled at boot. Preserve existing enrollment. |
| Tailnet enrollment | If needed, use `--tailscale-auth-key-file` with an existing restricted auth-key file, or complete a one-time `sudo tailscale up` login on Velia. SSH keys do not enroll Tailscale. |
| Private HTTPS | Detect the node's real Tailscale DNS name; require free Serve port 443, preserve other routes, and reject an existing Funnel configuration. Tailnet HTTPS must already be enabled or enabled by its administrator. |
| Application configuration | Generate a fresh editor token into `.env` with mode 0600; configure loopback port 8787, numeric ownership, source mount, and allowed hostname automatically. |
| Capacity and runtime | Check at least 5 GiB free, additional snapshot capacity, Docker daemon access, and available ports. No general OS upgrade or automatic reboot is performed. |

The package setup follows the official [Docker installation procedure](https://docs.docker.com/engine/install/ubuntu/)
and [Tailscale package instructions](https://pkgs.tailscale.com/stable/).
Enrollment supports Tailscale's [auth key file option](https://tailscale.com/docs/reference/tailscale-cli/up).

## Data migration strategy

`bundle.py` exports the current working files, including uncommitted articles,
raw evidence and uploads, provenance, article manifests, ingestion ledger,
repository route registry, and refresh/lifecycle state. It omits generated
pages, dependencies, caches, logs, lock files, `.env` variants, and single-use
authorization files. Pages are rebuilt on the target.

Git history is carried in a standalone Git bundle, so linked worktrees do not
depend on their original common Git directory. Installation restores the source
commit as a detached HEAD and populates its index without checking out files;
uncommitted modifications, additions, and deletions therefore survive. The full
history bundle stays in the installation record. Source credentials, Git hooks,
and machine-specific Git configuration are not transferred. The original
source checkout remains the recovery copy, including its local Git index and
configuration; staging distinctions in that index are not migrated.

The snapshot also includes every available cited document under the source
viewer's allowed sibling repositories, plus the complete Dark Factory Markdown
tree and its archive boundary marker. Their canonical paths are restored
inside the containers. Including the whole Dark Factory input prevents
`refresh.py`'s `rsync --delete` mirror from treating omitted files as upstream
deletions. Other sibling repositories are evidence copies, not full Git
clones. Registered Repos routes remain available; absent clones show an
availability notice instead of local README and Git metadata. Provision full
approved source clones separately if those additional views are required.

Every payload file has a size and SHA-256 in `manifest.json`. The controller
checks the archive hash after transfer to the Mac; the destination checks the
archive, every file, and archive paths before extracting. Symlinks, special
files, duplicate members, traversal paths, and occupied destinations fail
closed. The final application fingerprint must match the successfully
rehearsed application; content may change between rehearsal and cutover.
Unavailable references are recorded as pre-existing source gaps, rather than
silently claimed as migrated.

Bundles contain internal wiki content and Git history. The Mac state directory
is mode 0700 and bundles are mode 0600; retain them in your existing encrypted
backup storage after migration. The editor token is created only on Velia.
Save the value from Velia's `.env` in the password manager without putting it in
shell history or deployment logs. Back up `.env` separately with restricted access.

## Run from the Mac

Use your existing SSH aliases below. `wiki-source` points to RemoteRepos;
`wiki-velia` points to the new node. Copy the controller from the source checkout
so it matches the migration implementation being rehearsed:

```bash
scp -r wiki-source:/Transpara/transpara-ai/repos/wiki/compile/deploy "$HOME/wiki-deploy"
python3 "$HOME/wiki-deploy/velia.py" prepare --source wiki-source --target wiki-velia
python3 "$HOME/wiki-deploy/velia.py" rehearse
# Complete the separate Tailscale authorization on Velia before cutover.
python3 "$HOME/wiki-deploy/velia.py" cutover
python3 "$HOME/wiki-deploy/velia.py" verify
```

Without a target alias, omit `--target`: the initial default is
`transpara@192.168.30.192`. Later phases use the saved host identities. The
default Mac state directory is `~/.local/state/wiki-velia`; use
`--state-dir /absolute/path` consistently to choose another location. Run one
controller for a given migration at a time.

For unattended enrollment, add
`--tailscale-auth-key-file /absolute/path/to/key` to `prepare`. The key file must
be mode 0600 or stricter. The controller removes its temporary remote copy
after the enrollment attempt. If a control connection is interrupted during
that attempt, inspect the recorded target tools directory and remove any
remaining `tailscale-auth-key` file after reconnection. An already enrolled node
keeps its current identity; the supplied key is not used to re-enroll it.

`prepare` installs prerequisites and checks the destination without requiring
Tailscale enrollment. It does not stop the source or enroll the node unless an
auth-key file is explicitly supplied. `rehearse` also works before enrollment:
it transfers a snapshot and runs a temporary deployment on loopback port 18787,
using a local test hostname, exercises it, and removes its containers. It also
runs the existing Docker ingest/persistence suite in a separate disposable checkout.

`cutover` requires the separately authorized Tailscale enrollment and an
available private Serve route before it stops any source unit. It checks the
target again, records and stops the source units, exports
the final snapshot, installs it, builds and tests the runtime, recreates its
containers, and enables the private endpoint. It then verifies HTTPS from the
Mac with normal certificate verification. The old writer and timer remain
disabled, including across a source reboot. No DNS guessing, ACL edits, public
Funnel, or firewall rule changes are part of this procedure.

After completion, open the reported URL on the Mac, enter the new editor token
on Ingest, and check search and navigation in all four spaces. The browser
interaction suite remains available through `npm run test:browser` in a normal
development checkout. After the next planned host reboot, run `verify` again.

## Tests and acceptance

| Check | Automated evidence |
| --- | --- |
| Snapshot integrity and recovery | `python3 compile/test_deployment.py` (also run during rehearsal): corruption, archive traversal, symlink refusal, occupied destinations, interrupted freeze, rollback ordering, private configuration, and preservation of working changes. |
| Linux installer syntax | `bash -n compile/deploy/bootstrap.sh`; `shellcheck compile/deploy/bootstrap.sh`. |
| Installation and recreation | Rehearsal and final installation wait for Compose health, verify, recreate containers, and verify again. |
| Runtime behavior | `compile/deploy/verify.py`: version, health, portal, four spaces, contextual Repos/Sources/Ingest routes, exact active article inventory, every active article route, and available cited external source viewers. |
| Authoring | Reject an unauthenticated rebuild; accept a token-authenticated rebuild. Rehearsal runs `compile/test_docker.py` to test ingest, new DevOps article creation, duplicate refusal, readonly source mounts, periodic refresh, and persistence of upload/article/manifest/ledger across recreation. |
| Network route | Mac performs the same read checks through Tailscale HTTPS. Serve configuration is checked for the expected proxy and absent Funnel. |

Each installed snapshot has `manifest.json` and `verification.json` under
`/Transpara/transpara-ai/.wiki-migration`. `installed.json` records the target
phase and snapshot hash. Mac `state.json` records source/target identities,
bundle hashes, and the last completed phase. These files contain no editor token.

## Failure and recovery

Before cutover, the original writer stays active. Fix a failed prerequisite or
rehearsal and rerun that phase; a new rehearsal snapshot gets a new identity.
Remote tools and controller state persist across reboots. Retained snapshots
are never removed automatically.

Once source shutdown begins, the controller records that fact before issuing
the stop. A failed or disconnected run retains both copies and leaves the
source stopped. Inspect Mac `state.json`, target `installed.json`, and source
`~/.local/state/transpara-wiki-migration/freeze.json` before recovery.

If publication has not started, this command verifies the destination is
unpublished, stops its containers, then restores the source's recorded unit
states:

```bash
python3 "$HOME/wiki-deploy/velia.py" rollback-source
```

Recovery refuses if Velia is unreachable, its route is occupied, or its receipt
indicates publication may have started. The target data is retained. To make
another installation attempt, archive the failed target directory and records,
establish an empty destination again, and start a new controller state directory.
The scripts deliberately do not delete an occupied installation to make a retry
appear successful.

After publication, or if publication is uncertain, do not reactivate the old
writer automatically. Stop authoring, inspect the private route and target
receipt, and preserve any new Velia edits before choosing which copy to resume.
If only the Mac HTTPS check failed after publication, correct connectivity and
rerun `verify`; do not transfer the old snapshot again.
