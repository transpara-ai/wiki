FROM python:3.12-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates libstdc++6 bubblewrap ripgrep \
    && rm -rf /var/lib/apt/lists/*
COPY codex codex-code-mode-host claude /usr/local/bin/
RUN ln -s /usr/local/bin/codex /usr/local/bin/codex-linux-sandbox
COPY provider-requirements.toml /etc/codex/requirements.toml
USER 1000:1000
WORKDIR /tmp
ENV HOME=/tmp/provider-home CODEX_HOME=/var/lib/shared-provider/codex CLAUDE_CONFIG_DIR=/var/lib/shared-provider/claude
# Match the existing identity monitor: trusted container parent loads the secret.
CMD ["sh", "-ec", "mkdir -p /tmp/provider-home; export CLAUDE_CODE_OAUTH_TOKEN=\"$(cat /run/secrets/claude_oauth_token)\"; exec sleep infinity"]
