# Multi-Space Migration Baseline

- Baseline source commit: `163de77a3d4b58f28a444a90d07eb5078aa7960e` (`origin/main` after the 2026-09-05 fast-forward)
- Design commit: `b8411bd7a6463a7e6f3083f29fcf447819dcabcb`
- Canonical articles: 108
- Wikilink occurrences: 2,108
- Intentional unresolved references: 17 targets / 116 occurrences
- Generated files: 320
- Generated HTML routes: 314
- All generated-path inventory SHA-256: `465fd870aa74430cf1e09c46fb8b93260383743b04d5ed62ba31f69e32bf5453`
- HTML-route inventory SHA-256: `0cb5918d4bcf8d3111ed35f5c73faa01eedef116d0f61c10fd6dbcdbc0e8fc33`

## Verification

The deterministic build, JavaScript unit tests, Python tests, DOM tests, and six Playwright browser tests passed. On Ubuntu 26.04 the pinned Playwright release needs its supported Ubuntu 24.04 fallback browser; it was installed with `PLAYWRIGHT_HOST_PLATFORM_OVERRIDE=ubuntu24.04-x64`. The test runner itself then runs normally.

The full-tree secret scan passed before Node dependencies were installed: 263 occurrences resolved to 249 pass and 14 existing allowlist entries. `npm ci` reported zero vulnerabilities.

## Service Boundary

The authoring service baseline is `compile/systemd/transpara-ai-civilization-wiki.service`, bound explicitly to `127.0.0.1:8787`. Its companion refresh timer runs every 15 minutes. This migration must retain loopback-only authoring and must not activate a public or LAN route.

Systemd source hashes are recorded in the implementation plan's Phase 0 evidence commit and can be reproduced with `sha256sum compile/systemd/*`.

## Route Inventory

See [the exact baseline HTML route inventory](2026-09-05-multi-space-wiki-baseline-routes.txt).

