# Rebuilding the wiki

The Civilization Wiki refreshes in two tiers — a cheap deterministic one (automatic) and an expensive LLM one (manual). The split keeps the substrate honest without unattended spend or unattended pushes.

## Tier 1 — nightly, deterministic (`compile/refresh.py`)

Installed as a cron job (runs ~03:00). It:
1. mirrors the first-party dark-factory sources into `raw/transpara/`,
2. hashes all `raw/` sources and diffs against the last snapshot,
3. flags which articles have **stale sources** (their `sources:` cite a changed file),
4. writes `compile/refresh-status.json` — the fail-loud freshness banner the served site shows,
5. regenerates the served site (`dist/`) via `compile/build_site.py`.

It does **not** call an LLM, **not** commit, **not** push. Run it by hand anytime ("rebuild now"):

```
python3 compile/refresh.py
```

## Tier 2 — article re-compile, manual (LLM, on demand)

Re-synthesizing article **content** from sources is the expensive, autonomous-spend step, so it is deliberately manual. When `refresh-status.json` flags stale articles — or to fold in the deferred long-tail / new Open Brain history — re-run the compile workflow for the affected entities, review, and merge via PR. Open Brain deltas are not auto-detected by Tier 1 (that needs an LLM/MCP run); a Tier-2 pass picks them up.

## Serving

`dist/` is served on nucbuntu at `:8787`. The cron regenerates it in place; only restart the static server if the host reboots:

```
cd /home/transpara/transpara-ai/repos/civilization-wiki/dist && python3 -m http.server 8787 --bind 0.0.0.0
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
