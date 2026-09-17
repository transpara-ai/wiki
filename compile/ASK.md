# Subscription answers — v0.8.2

Version 0.8.2 makes the host provider boundary reproducible. A root-owned
configuration selects the Unix Docker socket, authentication policy and
non-secret observation paths. The wrapper and monitor pass that socket with an
explicit Docker `--host` argument and remove an ambient `DOCKER_HOST`, so neither
the wiki dispatcher nor an invoking shell can redirect provider authority.

Readers submit with Enter in the question field. The Effort dropdown remembers
the selection per provider/model and each answer identifies the configured level.
The same explicit level is used for selection and answering. Missing effort in an
older client's request resolves to the catalog default: Low for GPT-5.6 Sol,
Medium for the other OpenAI models, and High for Claude models with effort control.
Haiku shows Not supported and receives no effort flag.

`llm-models.json` carries the supported levels and their provenance, adapted from
Civilization's catalog and checked against Velia's native Codex model metadata and
[Claude effort documentation](https://platform.claude.com/docs/en/build-with-claude/effort).
Codex receives the explicit
[`model_reasoning_effort`](https://learn.chatgpt.com/docs/config-file/config-reference)
setting; Claude Code receives `--effort`. The bounded wiki runner does not offer
Codex Ultra, whose metadata describes automatic delegation. Unsupported levels
are rejected before execution; no level is silently downgraded. The displayed
effort is the configured control, not a measurement of hidden reasoning tokens.

## Factory Order and trust boundary

Human source: approved wiki LLM plan, refined on 2026-09-17: copy the working shared-provider methodology to Velia,
reuse the Claude long-lived token, and create a fresh Codex host session.
Outcome: signed-in readers get scoped, cited answers using both subscriptions.
Article synthesis and persistent conversations are outside this release.

TLC route: Critical, because a restricted transport identity connects the wiki container to its own host
provider launcher. Implementation, merge, and deployment
are explicitly authorized. The shared provider uses host-owned stores, the copied authentication monitor,
and the same `civilization-provider` wrapper. Claude is provisioned securely into
a host secret; Codex has a fresh native login so RemoteRepos can continue running.

The wiki retrieves published article context on its deployment host. A restricted SSH key
submits one JSON operation to a root-owned dispatcher on that same host. That
trusted host dispatcher calls `civilization-provider codex ...` or
`civilization-provider claude ...`. The wrapper injects Claude's Docker secret
and uses Codex's host-specific refreshable session. Neither provider credential
is accessible to the wiki container or copied into this repository.

Threats and controls:

- Reader authentication: existing server-to-server SSO verification, exact Origin
  and custom action header. Authoring tokens and incoming identity headers do
  not grant Ask access.
- Transport: pinned SSH host key and a dedicated client key, restricted to the
  fixed JSON dispatcher with no shell, forwarding, PTY, or caller-selected flags.
  The dispatcher accepts only `models` and `complete` operations and bounds inputs.
- Provider boundary: fixed CLI arguments disable model tools, shell, web, plugins,
  MCP and ambient settings. Context is untrusted data. Existing managed provider
  requirements protect credentials from model tools. As in the qualified source
  deployment, the outer seccomp/AppArmor profiles are relaxed for Codex user
  namespaces; the container retains UID 1000, read-only root, no capabilities,
  and the inner read-only credential-denying sandbox. Only the trusted host wrapper
  has Docker authority; it is never mounted into the wiki or bounded workers.
- Timeouts: the copied wrapper accepts optional
  `CIVILIZATION_PROVIDER_TIMEOUT_SECONDS`. GNU timeout
  runs inside the container so killing the host's docker exec cannot orphan a
  provider process. Calls without this variable keep their existing behavior.
- Scope: the build creates an index using its existing publication/retirement
  gates. Selection and answering receive only the requested space's canonical
  articles. Raw sources and repository pages are excluded. Citation IDs must
  belong to the supplied evidence.
- Capacity: one active question per reader and provider. File locks in the
  shared wiki volume's `.private/ask-locks` reserve both across the complete
  two-stage question, including across wiki processes/containers on that host.
  The dispatcher also locks individual provider calls. This release does not
  support replicas with independent wiki volumes. There is a 240-second question
  deadline and bounded context and output.
  No automatic provider/model/billing fallback. Native errors are sanitized.
- Rendering: plain text and server-resolved article links only. Answers remain
  advisory: checking citation membership does not prove semantic correctness.

Tests cover authentication, cross-origin rejection, scope/citation validation,
provider errors and timeout cleanup, safe rendering, browser preferences, and
both Chromium and WebKit. Record live qualification separately from this intended
acceptance contract. Self-review is not independent review.

## Deployment

The shared-provider host is independent of the wiki container.
`compile/shared-provider` contains the wrapper, monitor, root installer, a
standalone CLI container, and the six-hour systemd timer. Provider credentials
and observations stay outside all repositories.
The image includes the qualified standalone CLI binaries, Codex code-mode helper,
bubblewrap, and ripgrep; client upgrades require qualification.
The separate host service is available as `civilization-provider` (also
`transpara-provider`) to trusted host-side tasks. It has no public port. Verify the existing boundary without reading secrets:

```bash
civilization-provider status
civilization-provider codex login status
civilization-provider claude auth status
```

Install or update the host boundary with the repository-owned installer. The
three paths below are deployment inputs; the caller cannot override them later:

```bash
sudo python3 compile/shared-provider/configure.py \
  --docker-host unix:///run/civilization-docker.sock \
  --observation /absolute/deployment/state/provider-auth.json \
  --auth-policy /absolute/deployment/config/provider-auth-policy.json
```

This installs root-owned code under `/usr/local`, and writes
`/etc/civilization-provider/config.json` as root-owned mode 0644. The checker
must run as the service account that owns the observation directory.

For a fresh Codex host session or an expired login, run
`civilization-provider codex login --device-auth` on wiki and complete the native
browser approval. The mounted Codex home persists refreshable credentials across
restarts. Never copy its session from another host.

Claude uses the existing long-lived subscription token in
`/Transpara/transpara-ai/credentials/shared-provider/claude-oauth-token` (mode
0600). For renewal, use Claude Code's native `claude setup-token` as the operator,
store the resulting token securely at that path, and recreate only the shared
provider service so its parent process reloads the token. Keep tokens out of shell
history, repository files, browser storage, and diagnostic output. Re-run the
authentication monitor and both provider canaries after renewing either login.

Authentication monitoring remains owned by the existing
`transpara-provider-auth-check.timer`; do not duplicate its login/refresh logic.
The copied `llm-models.json` records catalog provenance, not current authentication.

Install `llm_service.py`, `ask_common.py`, and `llm-models.json` into root-owned
`/opt/wiki-llm` on the provider host. `/var/lib/wiki-llm` is private, owned by the trusted
launcher user, and contains provider lock files plus `enabled.json` (initially
`{"models":[]}`). No prompts or answers are retained there. The forced command is:

```bash
/usr/bin/timeout --kill-after=5s 255s /usr/bin/python3 /opt/wiki-llm/llm_service.py
```

Create a transport-only SSH key on the provider host outside the checkout. Authorize its
public key using `restrict,command="..."` with exactly the forced
command above. Pin the provider host's verified host key; do not use accept-new or
StrictHostKeyChecking=no. This key grants only the wiki JSON interface.

Add `compose.llm.yaml` after existing Compose files. Set `WIKI_LLM_TRANSPORT` to the private key/known-hosts directory. The
container reaches its own host via `host.docker.internal:host-gateway`. Only the wiki service receives these transport files.
The wiki has no provider credentials, public provider port, or Docker socket.
The shared provider container is managed independently of the wiki.
The wiki retains its existing `KNOWLEDGE_HUB_PROFILE_*` SSO settings.

The runtime uses local host SSH only; neither a cross-site route nor the user's
Mac tunnel is needed. Reverse proxies must allow
at least 270 seconds for `/api/ask`; browser timeout is 250 seconds.

## Model qualification

Run on the provider host using the shared wrapper through the installed dispatcher:

```bash
python3 /opt/wiki-llm/llm_service.py --qualify gpt-5.6-sol
python3 /opt/wiki-llm/llm_service.py --qualify claude-sonnet-5
```

Only successful models may be added to `/var/lib/wiki-llm/enabled.json`'s `models`
array. Update atomically. Repeat for additional catalog models. Defaults are
GPT-5.6 Sol and Claude Sonnet 5. Unverified models remain visibly unavailable.
Then test both providers through the actual website; host canaries alone
are not proof of the full browser-to-provider path.

## HTTP interface

- `GET /api/ask/models`: verified SSO required. Returns models, defaults,
  provenance, enabled status. No credentials.
- `POST /api/ask`: JSON `question`, `space` (`all` or a published key), `provider`
  (`codex` or `claude`), `model`, and optional `effort`. Requires signed-in cookie, configured Origin,
  and `X-Wiki-Profile-Action: 1`.
- Success: `answer`, `paragraphs` (plain `text` and `article_ids`), `citations`
  (`id`, `title`, canonical `href`), `insufficient_evidence`, `provider`, `model`,
  `effort`, and SHA-256 `corpus_revision`.
- Failures: 400 invalid input, 401 sign-in required, 403 wrong origin,
  422 excessive selected context, 429 busy/subscription limit, 502 invalid model
  output, 503 unavailable/unverified/connection/login failure, 504 timeout.

`ask-index.json` contains published canonical article bodies, never frontmatter,
raw sources, provider credentials or repository content. It is replaced atomically
with each build. Browser storage contains mode/provider/model preferences only.
Answers and prompts are transient. Search and authoring work independently.

## Recovery

If the shared provider host or private route is unavailable, Ask reports that
failure and Search remains usable. Do not create another provider login implementation to work around an outage. Use the existing Platform authentication runbook for revoked logins.
For rollback, restore the prior wiki revision/image and rebuild, remove the Ask
transport mount, and revoke its dedicated SSH public key if retiring the feature.
Preserve all source material, profile grants, DevOps configuration, and shared
provider identity stores. Drain questions before replacing dispatcher files.
