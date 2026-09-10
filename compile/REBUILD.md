# Rebuilding the Transpara Knowledge Hub

One build serves Civilization, Transpara Platform, Competition, and DevOps.
The root `index.md` is the shared portal; space homes live under `spaces/`, and
all canonical articles live under `wiki/`. Space membership, sections,
stewardship, and publication profiles come from
[`knowledge_structure.json`](knowledge_structure.json). See the
[design guide](../DESIGN.md) for source scope and article metadata.

For Docker hosting, follow [the Compose deployment guide](../DOCKER.md).
Compose's refresh container replaces the native systemd refresh timer; both use
the same deterministic refresh code and persistent checkout lock. The systemd
instructions below remain the reference for the existing native installation.

The Knowledge Hub refreshes in two tiers — a cheap deterministic one
(automatic) and an expensive LLM one (manual). The split keeps the substrate
honest without unattended spend or unattended pushes.

## Tier 1 — systemd timer, deterministic (`compile/refresh.py`)

Installed on nucbuntu as a user-level systemd timer for the `transpara` account
and run every 15 minutes after boot. It:
1. mirrors the configured first-party dark-factory Markdown sources into `raw/transpara/dark-factory/`,
2. hashes `raw/` Markdown sources and the Civilization archive boundary marker, then diffs against the last snapshot,
3. records which articles cite changed sources,
4. writes `compile/refresh-status.json`; after a successful deterministic rebuild `stale_articles` is empty and `changed_articles` records what was rebuilt, while failed rebuilds exit non-zero, preserve the previously served `dist/`, and leave the affected articles in `stale_articles` for the next successful build or direct status inspection,
5. **rewrites the generated stats block in `spaces/civilization/index.md`** (Civilization placement count + per-tier breakdown, between the `stats:begin`/`stats:end` markers) and its frontmatter `article_count` — the durable, committed stat surface,
6. regenerates the served site (`dist/`) via `compile/build_site.py`.

The source mirror is still specific to the dark-factory corpus. Adding Platform,
Competition, and DevOps spaces does not automatically import their repositories,
fetch external URLs, or synchronize their source systems. Register or reference
those sources explicitly, then review their article synthesis. The generated
Civilization stats block counts that space; shared articles count once in the
global catalog and once in each space where they are placed.

The deterministic build does not clear the live `dist/` tree before generation.
It overwrites generated files in place, keeps the previous complete site
servable during the rebuild, and prunes obsolete generated files only after the
new build has completed successfully. This avoids transient whole-site 404s
during timer or browser-triggered refreshes.

It does **not** call an LLM, **not** commit, **not** push. Run it by hand anytime ("rebuild now"):

```
flock -w 300 compile/.wiki-write.lock python3 compile/refresh.py
```

**On-demand "update the table now" is the same command.** `refresh.py` is both
the timer tick and the on-demand path: it recomputes the stats from `wiki/`
ground truth and rewrites the Civilization home block idempotently — running it
twice with no corpus change leaves no diff. It never commits; review the
`spaces/civilization/index.md` diff and commit it yourself.

## Browser source ingest — local authoring server (`compile/ingest_server.py`)

Static serving is read-only. Browser upload, reference update, and rebuild use
the local authoring server:

```
python3 compile/ingest_server.py 127.0.0.1 8787
```

Open `/ingest.html` on that server in the desired space to batch-select one or more local documents,
paste external source URLs or email/text, optionally select a target wiki article,
optionally name the source being superseded, then click **Ingest and rebuild**.
The endpoint writes uploaded files under `raw/inbox/<space>/YYYY-MM-DD/<article>/`,
appends manifest rows to `raw/inbox/manifest.jsonl`, appends selected source
references to the target article frontmatter, appends local uploaded documents
to `raw_documents`, and reruns `compile/refresh.py` so freshness status and
`dist/` are updated together. After a successful ingest/rebuild, the ingest page
reloads the generated shell and restores the completed action result so the
left navigation and freshness badge are no longer one build behind. Every
request carries a registry-valid space, section, and steward. A selected
article must already have that placement; placement changes remain PR-only.
The browser's new-investigation option is limited to `civilization/investigation`
under the `transpara-ai` steward and produces an internal provisional article.
The same API also accepts explicit `new_article=true` requests for DevOps under
the `transpara` steward, with supplied Markdown prose and supporting sources.
See the [authoring API guide](../API.md) for fields and examples. Creating
Platform or Competition articles and changing placements remain repository
authoring work.

Because the browser actions use the full deterministic refresh path, they may
leave reviewable working-tree diffs in the Civilization home and generated source
snapshot/status files. The service still never commits or pushes those changes.

This is a **source-registration** path, not an LLM article rewrite path. It does
not synthesize article prose, does not commit, does not push, and does not
promote the result beyond the checkout it is serving. If a source update
requires a substantive article rewrite, that remains Tier 2.

Every target with newly attached evidence receives `stale_since`, including
Competition profiles, so a successful rebuild cannot imply that new source
claims have already reached the article text. After a curated update incorporates
the evidence, update `last_compiled` and clear `stale_since`. Duplicate source
registration leaves a completed article's synthesis state unchanged.

Article sources are also the link contract: every load-bearing source document
mentioned in article prose should be listed in frontmatter `sources:` or
`raw_documents`. The compiler turns literal raw paths in code formatting and
declared document identifiers/titles such as `ADR-0008`, `DF-V3.9-SPEC-006`, and
`Decision 15` into one-click source links when the referenced document is
served.

The write endpoints are not a public LAN API. Without
`KNOWLEDGE_HUB_AUTHORING_TOKEN`, `POST /api/ingest` and `POST /api/rebuild` only
allow loopback clients. The service remains deliberately bound to loopback.
`KNOWLEDGE_HUB_ALLOWED_HOSTS` constrains browser Host headers; the former
`CIVWIKI_AUTHORING_TOKEN` and `CIVWIKI_ALLOWED_HOSTS` names remain lower-priority
fallbacks during the compatibility window. The token header remains
`X-CivWiki-Authoring-Token` during that window. The `/api/articles` endpoint is
readable for the ingest UI, but it only includes source paths for loopback or
token-authorized clients. The static wiki can be made LAN-visible with a
separate read-only service/proxy; do not expose the authoring server as the
public read route.

Open `/sources.html` to browse served sources associated with the selected space,
including shared sources. Repos, Sources, and Ingest retain the active space;
search can be expanded to **All spaces**. Article source
panels and inline raw-path references link into `source/<id>.html` so any raw
article source cited by the wiki can be opened directly.

## Tier 2 — article re-compile, manual (LLM, on demand)

Re-synthesizing article **content** from sources is the expensive, autonomous-spend step, so it is deliberately manual. When `refresh-status.json` reports `changed_articles`, a successful deterministic rebuild has already registered and served the cited source changes; re-run the LLM compile workflow only when those source changes require new prose synthesis. When `stale_articles` is non-empty, the last deterministic rebuild failed and should be retried/fixed first. Because a failed rebuild preserves the previously served `dist/`, that failed state is guaranteed in the command exit code and status JSON, not necessarily in already-served HTML until a later build bakes the status into the page. Open Brain deltas are not auto-detected by Tier 1 (that needs an LLM/MCP run); a Tier-2 pass picks them up.

## Publication profiles and shadow verification

The builder admits content through explicit profiles:

- `authoring-local` — complete host-local corpus, source viewers, repository
  mirrors, Arc, and mutation controls;
- `company-internal` — only reviewed `company-internal` and `public-candidate`
  articles, without source viewers, repository mirrors, Arc, or mutation
  controls;
- `public-platform` — disabled and fail-closed pending separate publication
  authority.

Build and test a candidate without touching the active artifact:

```
npm run build
npm run test:shadow
```

The shadow gate builds `dist-next`, synchronizes only the two ephemeral local
status files, compares every file byte-for-byte with `dist`, verifies the
baseline route inventory and all local links, then serves the candidate to
Playwright only on `127.0.0.1:8800`. A failed candidate build leaves `dist`
untouched.

## Serving

The primary nucbuntu authoring route is the Transpara Knowledge Hub service on
loopback `:8787`. It serves the `authoring-local` `dist/` artifact and browser ingest API from
this checkout, and it is installed as a linger-enabled user systemd service so
it starts after reboot without running as root:

```
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

The systemd templates prefer `.venv/bin/python3` through
`KNOWLEDGE_HUB_PYTHON`, fall back through the legacy `CIVWIKI_PYTHON` alias,
then use `/usr/bin/python3` when the venv is absent.

```
systemctl --user status transpara-knowledge-hub.service
journalctl --user -u transpara-knowledge-hub.service -f
```

Do not run a parallel cron `@reboot` `http.server` on `:8787`; the legacy wiki
cron entries were retired when the systemd service became the primary route.

The deterministic freshness timer is separate from the web service:

```
systemctl --user status transpara-knowledge-hub-refresh.timer
systemctl --user list-timers transpara-knowledge-hub-refresh.timer
journalctl --user -u transpara-knowledge-hub-refresh.service -f
```

The former `transpara-ai-civilization-wiki*` units and `CIVWIKI_*` environment
names remain compatibility paths for one stable-release observation window.
The old and new unit families declare mutual conflicts and must not run
together. To migrate an installed user service after the full verification gate:

```
mkdir -p ~/.config/systemd/user
cp compile/systemd/transpara-knowledge-hub* ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user disable --now transpara-ai-civilization-wiki-refresh.timer transpara-ai-civilization-wiki.service
systemctl --user enable --now transpara-knowledge-hub.service transpara-knowledge-hub-refresh.timer
curl --fail --silent http://127.0.0.1:8787/api/health
```

Rollback is immediate and does not rewrite repository history:

```
systemctl --user disable --now transpara-knowledge-hub-refresh.timer transpara-knowledge-hub.service
systemctl --user enable --now transpara-ai-civilization-wiki.service transpara-ai-civilization-wiki-refresh.timer
```

Keep flat article URLs and historical ledgers indefinitely. Do not remove the
legacy units or environment fallbacks until a later, explicitly reviewed stable
release proves no active caller depends on them.

The timer uses `flock` on `compile/.wiki-write.lock`; browser ingest uses the
same lock. That keeps timer refreshes and upload-triggered rebuilds from writing
the wiki/dist surfaces concurrently.

The generated repository catalog uses local clones and worktrees from both
stewardship domains. Repos filters that inventory by the selected space's
steward. Registered identities in `compile/repository_routes.json` preserve
published routes when a checkout is unavailable; those pages show a source
repository link and an availability notice instead of current README/Git data.
The refresh job holds the same write lock used by
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

`npm ci` installs `@playwright/test` and `jsdom`; the browser setup in
`npm run test:browser` installs Chromium and applies Playwright's supported
Ubuntu 24.04 bundle only when the host is a newer Ubuntu release that the pinned
Playwright version cannot identify. `npm run verify` rebuilds the
static site, validates catalogs, lifecycle and publication boundaries,
syntax-checks the arc assets, runs the jsdom component smoke test, runs the
headless Chromium suite against `127.0.0.1:8799`, and repeats browser validation
against the byte-equivalent shadow artifact on `127.0.0.1:8800`. Both are
separate from the authoring service on `:8787`.

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
