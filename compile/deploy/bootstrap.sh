#!/usr/bin/env bash
# Run as root via the existing deploy user's sudo. Never enable shell tracing.
set -euo pipefail
umask 022
[[ $(id -u) == 0 ]] || { echo 'Run bootstrap through sudo.' >&2; exit 1; }
[[ ${SUDO_UID:-0} != 0 ]] || { echo 'Use a non-root deployment account with sudo.' >&2; exit 1; }
# shellcheck disable=SC1091
source /etc/os-release
case "$ID:${VERSION_CODENAME:-}" in
  ubuntu:jammy|ubuntu:noble|ubuntu:resolute|debian:bookworm|debian:trixie) ;;
  *) echo "Unsupported host: $ID ${VERSION_CODENAME:-unknown}; no packages changed." >&2; exit 1 ;;
esac
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y --no-install-recommends ca-certificates curl python3 git rsync util-linux

if ! command -v docker >/dev/null; then
  # Do not uninstall an existing container stack or replace another service's runtime.
  for package in docker.io docker-compose podman-docker containerd runc; do
    if dpkg-query -W -f='${Status}' "$package" 2>/dev/null | grep -q 'ok installed'; then
      echo "Existing $package requires operator review before Docker CE installation." >&2
      exit 1
    fi
  done
  install -d -m 0755 /etc/apt/keyrings
  curl -fsSL --retry 3 "https://download.docker.com/linux/$ID/gpg" -o /etc/apt/keyrings/docker.asc
  chmod 0644 /etc/apt/keyrings/docker.asc
  cat > /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/$ID
Suites: $VERSION_CODENAME
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF
  apt-get update
  apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
elif ! docker compose version >/dev/null 2>&1; then
  # Reuse the installed distribution/vendor's repository; never replace the engine.
  if apt-cache show docker-compose-plugin >/dev/null 2>&1; then
    apt-get install -y docker-compose-plugin
  elif apt-cache show docker-compose-v2 >/dev/null 2>&1; then
    apt-get install -y docker-compose-v2
  else
    echo 'Docker exists but its repositories offer no Compose v2 plugin.' >&2
    exit 1
  fi
fi
systemctl enable --now docker
docker info >/dev/null
docker compose version

if ! command -v tailscale >/dev/null; then
  install -d -m 0755 /usr/share/keyrings
  curl -fsSL --retry 3 "https://pkgs.tailscale.com/stable/$ID/$VERSION_CODENAME.noarmor.gpg" \
    -o /usr/share/keyrings/tailscale-archive-keyring.gpg
  curl -fsSL --retry 3 "https://pkgs.tailscale.com/stable/$ID/$VERSION_CODENAME.tailscale-keyring.list" \
    -o /etc/apt/sources.list.d/tailscale.list
  apt-get update
  apt-get install -y tailscale
fi
systemctl enable --now tailscaled

# Create only missing directories. Preserve ownership of anything already present.
for directory in /Transpara /Transpara/transpara-ai /Transpara/transpara-ai/.wiki-migration; do
  if [[ ! -e "$directory" ]]; then
    install -d -o "$SUDO_UID" -g "$SUDO_GID" -m 0750 "$directory"
  fi
done
echo 'Host packages and boot services ready. Existing Tailscale enrollment is preserved.'
echo 'If enrollment is absent: sudo tailscale up --auth-key=file:/path/to/restricted-auth-key'
