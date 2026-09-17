# Subscription answers — v0.8.0

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

The wiki retrieves published article context on Velia. A restricted SSH key
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
- Capacity: one active question per reader and provider, cross-process provider
  locks on Velia, 240-second question deadline, bounded context and output.
  No automatic provider/model/billing fallback. Native errors are sanitized.
- Rendering: plain text and server-resolved article links only. Answers remain
  advisory: checking citation membership does not prove semantic correctness.

Tests cover authentication, cross-origin rejection, scope/citation validation,
provider errors and timeout cleanup, safe rendering, browser preferences, and
both Chromium and WebKit. Record live qualification separately from this intended
acceptance contract. Self-review is not independent review.

## Deployment

Velia is the canonical shared-provider host, independent of Civilization.
`compile/shared-provider` contains the copied wrapper and monitor, a standalone
CLI container, and the six-hour systemd timer. Persistent state is under
`/Transpara/transpara-ai/deployments/shared-provider-velia`; credentials are under
`/Transpara/transpara-ai/credentials/shared-provider`, outside all repositories.
The image includes the qualified standalone CLI binaries, Codex code-mode helper,
bubblewrap, and ripgrep; client upgrades require qualification.
The separate Velia service is available as `civilization-provider` (also
`transpara-provider`) to trusted host-side tasks. It has no public port. Verify the existing boundary without reading secrets:

```bash
civilization-provider status
civilization-provider codex login status
civilization-provider claude auth status
```

Authentication monitoring remains owned by the existing
`transpara-provider-auth-check.timer`; do not duplicate its login/refresh logic.
The copied `llm-models.json` records catalog provenance, not current authentication.

Install `llm_service.py`, `ask_common.py`, and `llm-models.json` into root-owned
`/opt/wiki-llm` on Velia. `/var/lib/wiki-llm` is private, owned by the trusted
launcher user, and contains provider lock files plus `enabled.json` (initially
`{"models":[]}`). No prompts or answers are retained there. The forced command is:

```bash
/usr/bin/timeout --kill-after=5s 255s /usr/bin/python3 /opt/wiki-llm/llm_service.py
```

Create a transport-only SSH key on Velia outside the checkout. Authorize its
public key on Velia using `restrict,command="..."` with exactly the forced
command above. Pin Velia's verified host key; do not use accept-new or
StrictHostKeyChecking=no. This key grants only the wiki JSON interface.

Add `compose.llm.yaml` after existing Compose files. Set `WIKI_LLM_TRANSPORT` to the private key/known-hosts directory. The
container reaches its own Velia host via `host.docker.internal:host-gateway`. Only the wiki service receives these transport files.
The wiki has no provider credentials, public provider port, or Docker socket.
The shared provider container is managed independently of the wiki.
The wiki retains its existing `KNOWLEDGE_HUB_PROFILE_*` SSO settings.

The runtime uses local host SSH only; neither a cross-site route nor the user's
Mac tunnel is needed. Reverse proxies must allow
at least 270 seconds for `/api/ask`; browser timeout is 250 seconds.

## Model qualification

Run on Velia using the shared wrapper through the installed dispatcher:

```bash
python3 /opt/wiki-llm/llm_service.py --qualify gpt-5.6-sol
python3 /opt/wiki-llm/llm_service.py --qualify claude-sonnet-5
```

Only successful models may be added to `/var/lib/wiki-llm/enabled.json`'s `models`
array. Update atomically. Repeat for additional catalog models. Defaults are
GPT-5.6 Sol and Claude Sonnet 5. Unverified models remain visibly unavailable.
Then test both providers through the actual Velia website; host canaries alone
are not proof of the full browser-to-provider path.

## HTTP interface

- `GET /api/ask/models`: verified SSO required. Returns models, defaults,
  provenance, enabled status. No credentials.
- `POST /api/ask`: JSON `question`, `space` (`all` or a published key), `provider`
  (`codex` or `claude`), and `model`. Requires signed-in cookie, configured Origin,
  and `X-Wiki-Profile-Action: 1`.
- Success: `answer`, `paragraphs` (plain `text` and `article_ids`), `citations`
  (`id`, `title`, canonical `href`), `insufficient_evidence`, `provider`, `model`,
  and SHA-256 `corpus_revision`.
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
