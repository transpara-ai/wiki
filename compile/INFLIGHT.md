# compile/INFLIGHT.md — live in-flight overlay

`compile/inflight.py` writes `dist/inflight.json`: all open PRs plus PRs merged in the
last 30 days across the public dark-factory stack (+ civilization-wiki), which the arc
page fetches and overlays as live `derived` work at the sequence frontier. The grouping
toolbar's **Actor** mode splits that live work into per-author lanes.

## Run

    python3 compile/inflight.py     # writes dist/inflight.json

Requires the `gh` CLI authenticated as a user who can read the transpara-ai repos. The
dark-factory repo set is resolved live from the GitHub `dark-factory` topic (never hardcoded).

## Cron (suggested ~10 min cadence)

    */10 * * * *  cd /path/to/civilization-wiki && python3 compile/inflight.py

Decoupled from the article build on purpose: it refreshes fast-moving PR state without
regenerating the articles. `dist/inflight.json` survives a `build_site.py` run, and `dist/`
is git-ignored so the snapshot is never committed.

## Tests

`python3 compile/test_inflight.py` — stdlib-assert (no pytest, air-gap friendly), matching
`compile/test_stats.py`. Gated in CI (`.github/workflows/ci.yml`) and `npm run verify`.

## Security / standing rules

- `gh` uses the operator's existing auth. The token is NEVER written to `inflight.json` or
  shipped to the browser. `inflight.json` carries only PR metadata (number, title, author
  login, url, state).
- No git commit / push / merge — writes local working files only (like `refresh.py`).
- Fail-loud: per-repo / per-query `gh` errors are recorded in `inflight.json.errors`, never
  silently treated as "no work". The browser overlay is fail-closed: invalid data keeps the
  baked arc (see `CivOntology.mergeInflight` + `loadInflight`).
