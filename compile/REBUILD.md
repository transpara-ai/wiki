# Rebuilding the wiki

The Civilization Wiki refreshes in two tiers — a cheap deterministic one
(automatic) and an expensive LLM one (manual). The split keeps the substrate
honest without unattended spend or unattended pushes.

## Tier 1 — systemd timer, deterministic (`compile/refresh.py`)

Installed on nucbuntu as a user-level systemd timer for the `transpara` account
and run every 15 minutes after boot. It:
1. mirrors the first-party dark-factory sources into `raw/transpara/`,
2. hashes all `raw/` sources and diffs against the last snapshot,
3. flags which articles have **stale sources** (their `sources:` cite a changed file),
4. writes `compile/refresh-status.json` — the fail-loud freshness banner the served site shows,
5. **rewrites the generated stats block in `index.md`** (article count + per-tier breakdown, between the `stats:begin`/`stats:end` markers) and its frontmatter `article_count` — the durable, committed stat surface,
6. regenerates the served site (`dist/`) via `compile/build_site.py`.

It does **not** call an LLM, **not** commit, **not** push. Run it by hand anytime ("rebuild now"):

```
flock -w 300 compile/.wiki-write.lock python3 compile/refresh.py
```

**On-demand "update the table now" is the same command.** `refresh.py` is both
the timer tick and the on-demand path: it recomputes the stats from `wiki/`
ground truth and rewrites the `index.md` block idempotently — running it twice
with no corpus change leaves no diff. It never commits; review the `index.md`
diff and commit it yourself.

## Browser source ingest — local authoring server (`compile/ingest_server.py`)

Static serving is read-only. Browser upload, reference update, and rebuild use
the local authoring server:

```
python3 compile/ingest_server.py 127.0.0.1 8787
```

Open `/ingest.html` on that server to batch-select one or more local documents,
paste one or more external source URLs, optionally select a target wiki article,
optionally name the source being superseded, then click **Ingest and rebuild**.
The endpoint writes uploaded files under `raw/inbox/YYYY-MM-DD/<article>/`,
appends manifest rows to `raw/inbox/manifest.jsonl`, appends selected source
references to the target article frontmatter, appends local uploaded documents
to `raw_documents`, and reruns `compile/refresh.py` so freshness status and
`dist/` are updated together. If no target article is
selected, the first uploaded markdown document creates a provisional
investigation article so it is visible in the left navigation rather than
remaining an orphaned source.

Because the browser actions use the full deterministic refresh path, they may
leave reviewable working-tree diffs in `index.md` and the generated source
snapshot/status files. The service still never commits or pushes those changes.

This is a **source-registration** path, not an LLM article rewrite path. It does
not synthesize article prose, does not commit, does not push, and does not
promote the result beyond the checkout it is serving. If a source update
requires a substantive article rewrite, that remains Tier 2.

The write endpoints are not a public LAN API. Without
`CIVWIKI_AUTHORING_TOKEN`, `POST /api/ingest` and `POST /api/rebuild` only allow
loopback clients. If the service is deliberately bound to a non-loopback
address, set `CIVWIKI_AUTHORING_TOKEN` in
`~/.config/transpara-ai-civilization-wiki.env` and send it as the
`X-CivWiki-Authoring-Token` header, and set `CIVWIKI_ALLOWED_HOSTS` to the exact
hostnames the browser should use. The `/api/articles` metadata endpoint is
readable for the ingest UI, but it only includes source paths for loopback or
token-authorized clients. The static wiki can be made LAN-visible with a
separate read-only service/proxy; do not expose the authoring server as the
public read route.

Open `/sources.html` to browse every served raw/reference source. Article source
panels and inline raw-path references link into `source/<id>.html` so any raw
article source cited by the wiki can be opened directly.

## Tier 2 — article re-compile, manual (LLM, on demand)

Re-synthesizing article **content** from sources is the expensive, autonomous-spend step, so it is deliberately manual. When `refresh-status.json` flags stale articles — or to fold in the deferred long-tail / new Open Brain history — re-run the compile workflow for the affected entities, review, and merge via PR. Open Brain deltas are not auto-detected by Tier 1 (that needs an LLM/MCP run); a Tier-2 pass picks them up.

## Serving

The primary nucbuntu authoring route is now the Transpara-AI Civilization Wiki
service on loopback `:8787`. It serves `dist/` and the browser ingest API from
this checkout, and it is installed as a linger-enabled user systemd service so
it starts after reboot without running as root:

```
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

The systemd templates prefer `.venv/bin/python3` through `CIVWIKI_PYTHON` and
fall back to `/usr/bin/python3` only when the venv is absent.

```
systemctl --user status transpara-ai-civilization-wiki.service
journalctl --user -u transpara-ai-civilization-wiki.service -f
```

Do not run a parallel cron `@reboot` `http.server` on `:8787`; the legacy wiki
cron entries were retired when the systemd service became the primary route.

The deterministic freshness timer is separate from the web service:

```
systemctl --user status transpara-ai-civilization-wiki-refresh.timer
systemctl --user list-timers transpara-ai-civilization-wiki-refresh.timer
journalctl --user -u transpara-ai-civilization-wiki-refresh.service -f
```

The timer uses `flock` on `compile/.wiki-write.lock`; browser ingest uses the
same lock. That keeps timer refreshes and upload-triggered rebuilds from writing
the wiki/dist surfaces concurrently.

The generated repository catalog is host-local: when sibling Transpara-AI repos
are present, the build reads their README files and git metadata. On hosts
without that sibling tree, the wiki still builds and the repo catalog degrades
to the committed wiki corpus. The refresh job holds the same write lock used by
browser ingest while it rebuilds, so long-running local git scans can briefly
delay an ingest/rebuild request.

Do not put a reverse proxy in front of the authoring endpoints unless it forwards
the `X-CivWiki-Authoring-Token` header and the token is configured. A same-host
proxy can otherwise make LAN-origin writes appear loopback-local to the Python
server. A read-only LAN proxy must exclude `source/*.html` and `search-index.js`
unless the confidential raw source corpus and full-text source index have been
approved for that audience. Sibling-repo README/source rendering is
host-local-trusted and must not be treated as a scrubbed public artifact.

Read-only static previews remain useful on alternate ports:

```
python3 -m http.server 8798 --bind 127.0.0.1 --directory dist
```

## Browser verification

The repo owns its browser test environment through `package.json`. Run:

```
npm ci
npm run verify
```

`npm ci` installs `@playwright/test`, `jsdom`, and Chromium via the Playwright
browser install step in `npm run test:browser`. `npm run verify` rebuilds the
static site, syntax-checks the arc assets, runs the jsdom component smoke test,
and runs the headless Chromium Playwright suite against a local test server on
`127.0.0.1:8799`, separate from the production `:8787` wiki server.

## Auto-deploy poller (NOT auto-installed)

`compile/autodeploy.py` deploys the **authorized** commit when an authorized,
site-affecting merge lands. It is fail-closed and self-hosting; it never
commits/pushes/forces. Shipped inert — activation and authorization are
deliberate human steps.

**Authorize a deploy** (per reviewed commit):
1. `cp compile/deploy-authorization.example.json compile/deploy-authorization.json`
   (the real file is git-ignored).
2. Set `authorized_sha` to the exact 40-char SHA to publish (must be an ancestor
   of `origin/main`), `authority`, `authorized_at`/`expires_at` (ISO-8601), `reason`.

**Activate the timer** (user units, no root):
```
loginctl enable-linger transpara
mkdir -p ~/.config/systemd/user
systemctl --user disable --now civwiki-autodeploy.timer civwiki-inflight.timer 2>/dev/null || true
mkdir -p ~/.config/systemd/user/retired-civwiki-units
mv -n ~/.config/systemd/user/civwiki-autodeploy.* ~/.config/systemd/user/civwiki-inflight.* ~/.config/systemd/user/retired-civwiki-units/ 2>/dev/null || true
cp compile/systemd/wiki-autodeploy.* ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now wiki-autodeploy.timer
journalctl --user -u wiki-autodeploy -f      # logs
```
A blocked tick (unauthorized / dirty / build-fail) leaves the live site
untouched and flips the on-page "Auto-deploy blocked" banner.
