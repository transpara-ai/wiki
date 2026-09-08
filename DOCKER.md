# Docker hosting on the private Tailscale network

This is the deployment path for the main authoring host at `192.168.30.104`.
Docker Compose runs both the wiki and its 15-minute refresh worker. Host-level
Tailscale Serve provides private HTTPS. The wiki publishes only
`127.0.0.1:8787`; readers connect through the machine's Tailscale DNS name.

## What persists

The image contains Python and the runtime dependencies. The checkout is mounted
at `/Transpara/transpara-ai/repos/wiki` and holds the application and all durable
state: articles, uploads, manifests, ingestion ledger, lifecycle state, generated
pages, and Git working-tree changes. Container replacement preserves these files.
There is one wiki writer and one refresh worker, coordinated by the existing
filesystem lock. Do not run native refresh timers or additional authoring
instances against this checkout while Compose owns it.

The parent source-repository directory is mounted read-only, with the wiki's
more specific mount writable. This preserves existing absolute source paths and
the Repos catalog. Containers use the checkout owner's numeric UID/GID. Neither
container receives the Docker socket. The image build context excludes wiki
content, uploads, Git history, and the private `.env` file.

## 1. Prepare the destination

SSH to the Velia host using your existing account (examples use `transpara`):

```bash
ssh transpara@192.168.30.104
docker version
docker compose version
tailscale status
```

If Docker is missing, install Engine and the Compose plugin using
[Docker's Ubuntu instructions](https://docs.docker.com/engine/install/ubuntu/).
Use `sudo docker` if your account does not already have Docker access. If this
machine is not itself joined to your tailnet, follow the
[Tailscale Linux instructions](https://tailscale.com/docs/install/linux).

Create the installation directory on a new host:

```bash
sudo install -d -o "$(id -un)" -g "$(id -gn)" \
  /Transpara/transpara-ai/repos \
  /Transpara/transpara-ai/repos/wiki
```

`192.168.30.104` is the server's private administration address. The browser URL
will use the Tailscale DNS name printed by `tailscale serve status`.

## 2. Transfer the current working checkout and source dependencies

The current wiki includes uncommitted changes and uploaded material, so a fresh
GitHub clone does not contain the complete current state. Pause authoring while
copying. Run this on the current NUC:

```bash
cd /Transpara/transpara-ai/repos/wiki
flock -w 300 compile/.wiki-write.lock \
  rsync -az \
    --exclude='.venv/' --exclude='node_modules/' \
    --exclude='__pycache__/' --exclude='.cache/' --exclude='.env' \
    --exclude='dist-*/' --exclude='test-results/' --exclude='playwright-report/' \
    --exclude='compile/*authorization.json' --exclude='compile/.*lock' \
    ./ transpara@192.168.30.104:/Transpara/transpara-ai/repos/wiki/
```

Retain the sibling source repositories used by this wiki under the same parent
directory on Velia. Containerization does not copy these repositories into the
image. The Repos view indexes the Git checkouts present there; missing checkouts
disappear from that catalog at the next build. Likewise, referenced documents
outside `wiki/` must exist in the matching source checkout to retain their
source viewers. Copy the approved source checkouts, including their current
document changes, before the first build. Match their ownership to the account
running the containers so Git can read their metadata without ownership errors.

Copy the complete `docs/dark-factory` Markdown tree if that source is present:
the refresh worker mirrors it into `raw/transpara/dark-factory` using deletion
of removed upstream files. A partially copied upstream directory would produce
an incomplete mirror. Already captured `raw/` material is included in the wiki
transfer above.

## 3. Configure the containers on Velia

```bash
cd /Transpara/transpara-ai/repos/wiki
cp --no-clobber .env.example .env
chmod 600 .env
id -u
id -g
openssl rand -hex 32
nano .env
```

Set:

- `WIKI_UID` and `WIKI_GID` to the IDs printed above.
- `WIKI_REPOS_DIR` to `/Transpara/transpara-ai/repos`, or the actual host directory
  containing the source checkouts. The paths inside the container stay canonical.
- `KNOWLEDGE_HUB_AUTHORING_TOKEN` to the generated random value. Store this in
  your password manager; editors enter it on the Ingest page.
- `KNOWLEDGE_HUB_ALLOWED_HOSTS` to the actual Tailscale DNS name, without a
  trailing dot, followed by the same name with `:443`, separated by a comma.
  Example: `velia.example-tailnet.ts.net,velia.example-tailnet.ts.net:443`.

You can obtain the exact DNS name without guessing the tailnet suffix:

```bash
tailscale status --json | python3 -c \
  'import json,sys; print(json.load(sys.stdin)["Self"]["DNSName"].rstrip("."))'
```

The token is required: Tailscale provides network access, while the existing
application token controls authoring. `.env` is Git-ignored and excluded from
the image. Do not copy the NUC's single-use ingest/deploy authorization files.

## 4. Start Docker Compose

If you installed the native services on Velia using the previous instructions,
stop and disable them before Compose starts:

```bash
systemctl --user disable --now transpara-knowledge-hub-refresh.timer
systemctl --user disable --now transpara-knowledge-hub.service
```

If those units were never installed, skip that step. Then:

```bash
docker compose config --quiet
docker compose up -d --build --wait --wait-timeout 300
docker compose ps
curl --fail http://127.0.0.1:8787/api/health
curl --fail http://127.0.0.1:8787/version.json
```

Startup rebuilds the site before the server becomes healthy. The refresh
container starts after that health check and runs every 900 seconds. Compose
restarts both services after a host reboot as long as Docker starts at boot.
All Python installation, rendering, and refresh execution happen in containers.

## 5. Connect Tailscale Serve

Check existing listeners first:

```bash
sudo tailscale serve status
```

If HTTPS port 443 is free, configure the private endpoint:

```bash
sudo tailscale serve --bg --https=443 http://127.0.0.1:8787
sudo tailscale serve status
```

Follow the prompt to enable HTTPS certificates if required. Keep Funnel disabled
for this endpoint. Permit the intended readers to reach this device's TCP 443
using your tailnet's existing access rules. Do not replace an existing Serve
route belonging to another application.

The `--bg` configuration persists across reboots. See the official
[Serve reference](https://tailscale.com/docs/reference/tailscale-cli/serve).

## 6. Verify and switch authoring to Velia

Open the printed HTTPS URL from a tailnet-connected computer. Check the version
against `package.json`, all three spaces, Cognite's pricing and source links,
and the Repos catalog. Enter the editor token on Ingest and run **Rebuild now**.
Test an intended new ingestion and confirm its file appears in the host's
`raw/inbox/` and its article is marked for a prose update.

After verification, retire the old NUC writer and timer so subsequent content
changes occur only on Velia:

```bash
# On the NUC, after any active ingest or rebuild has finished:
systemctl --user disable --now transpara-knowledge-hub-refresh.timer
systemctl --user disable --now transpara-knowledge-hub.service
```

Keep the NUC copy as a migration backup. Do not later rsync it over newer Velia
content. Ingestion continues to register evidence; article prose synthesis is
still a separate authoring step, as on the original host.

## Operations

```bash
# Status and recent logs
docker compose ps
docker compose logs --tail=100 wiki refresh

# Update the runtime after reviewing/synchronizing application changes
docker compose up -d --build --force-recreate --wait --wait-timeout 300

# Stop containers; the bind-mounted checkout remains intact
docker compose down
```

Back up the host checkout (especially `wiki/`, `raw/`, and `compile/` state),
source dependencies, and `.env` with restricted access. Coordinate backups and
maintenance with the same `compile/.wiki-write.lock` as ingestion and refresh.
The image is rebuildable; it does not contain your durable data.

To exercise the deployment locally without changing the live wiki, run
`npm run test:docker`. It uses a disposable checkout and a separate localhost
port, verifies authoring protection and read-only sibling mounts, ingests a test
document, waits for periodic refresh, recreates the containers, and confirms
that the upload, article, manifest, and ledger survive.
