---
entity: Upstream Fork Sync
aliases: [upstream-fork-sync, fork sync controller, institutional sync, reconcile workflow]
tier: architecture
status: compiled
last_compiled: "2026-06-14"
sources:
  - gh:transpara-ai/upstream-fork-sync README.md  # root README, fetched via GitHub API 2026-06-14
  - gh:transpara-ai/upstream-fork-sync commit log  # five most recent commits, fetched 2026-06-14
confidence:
  sources: primary
  claims: grounded
---

# Upstream fork sync

The **institutional one-way upstream-to-fork branch synchronization controller** that keeps transpara-ai forks current with their upstream projects without manual intervention. Lives at `transpara-ai/upstream-fork-sync`. Last updated **2026-06-12**.

It is a deliberate, conservative automation: upstream branches are the authoritative source; the controller writes only to configured mirror branches in downstream forks; human review remains the promotion boundary for any change flowing back upstream. It does not replace a fork relationship — it automates the pull direction of a generic fork-and-mirror topology at institutional scale, for any configured upstream→fork mapping.

## What problem it solves

[[the-civilization]] maintains a set of transpara-ai forks of upstream OSS projects. (The original such fork — the runtime codebase, now diverged hundreds of commits from a dormant upstream — is documented historically in [[the-lovyou-ai-fork]].) Without automation, keeping any forks current requires a human to periodically run `git fetch upstream && git merge upstream/main` per repo — a maintenance burden that grows linearly with the number of forks and compounds when fork-local branches diverge silently. `upstream-fork-sync` replaces that manual loop with a scheduled reconciliation workflow backed by a validated configuration map.

## Architecture

The system has four runtime components and one governance layer:

**Python sync engine** (`src/upstream_fork_sync/`) — validates configuration, authenticates as a dedicated downstream-writer GitHub App, iterates the sync map, and for each configured mapping fetches the upstream branch state and fast-forwards (or creates) the corresponding mirror branch in the downstream fork. Only mirror branches are touched; fork-local work branches are never modified.

**`config/sync-map.json`** — the production repository/fork/branch map. A JSON Schema (`schemas/sync-map.schema.json`) enforces shape; `scripts/validate_config.py` runs the validator locally and in CI. Each mapping specifies: upstream repo, downstream fork, upstream branch, downstream mirror branch name (typically `upstream/<branch>`), and optionally `allowBranchOverwrite: true` for the rare case where the mirror must share a name with a protected branch.

**`.github/workflows/reconcile.yml`** — scheduled and manually triggerable reconciliation workflow. Runs the sync engine on a cron and emits pass/fail status per mapping.

**Optional dashboard backend** (`src/upstream_fork_sync/server.py`, `Dockerfile`) — a REST API for dashboard-driven config mutations. The GitHub Pages report (`--report-html`) is static; the backend is needed only to allow the Pages dashboard to add repositories without a direct file commit.

## Safety contract

The controller enforces a default **allowlist** of safe mirror-branch name patterns and refuses to write to anything that looks like a primary integration branch. The README names the denylist: `main`, `master`, `develop`, `feature/*`, `fork/*`, `customer/*`, `integration/*` are all refused by default policy. ⚠ This is a named denylist, which means branch-naming patterns not listed could be written to silently if `allowBranchOverwrite` is not set correctly. Mirror branches should use the `upstream/` prefix convention to stay inside the safe envelope.

Authentication uses a dedicated **downstream-writer GitHub App** — not a personal access token — so the write identity is auditable and scoped to the exact permissions the app is granted.

Private upstream repositories are supported: owner-scoped tokens (`SYNC_TOKEN_<OWNER>`) are passed as environment variables; no credential falls back to a default.

## Operational commands

Local dry run (broad token):
```
SYNC_TOKEN=... python scripts/sync_forks.py --config config/sync-map.json --dry-run
```

Targeted dry run:
```
SYNC_TOKEN=... python scripts/sync_forks.py --config config/sync-map.json --repo tinstaller --dry-run
```

HTML sync-state report:
```
SYNC_TOKEN_TRANSPARA_AI=... \
python scripts/sync_forks.py --config config/sync-map.json --report-html reports/sync-state.html
```

Owner-scoped tokens (separate downstream and private-upstream credentials):
```
SYNC_TOKEN_TRANSPARA=... SYNC_TOKEN_TRANSPARA_AI=... \
python scripts/sync_forks.py --config config/sync-map.json --dry-run
```

## Recent development (commit log, 2026-06-12)

Five commits landed on 2026-06-12, all dashboard-layer work:

- `Add upstream last updated dashboard state`
- `Implement selected and available dashboard states`
- `Run targeted sync from dashboard backend`
- `Polish dashboard row control alignment`
- `Align dashboard table controls`

The burst of dashboard commits on the last recorded day suggests the dashboard UI was the active development frontier as of last update. The core sync engine predates this work.

## Relationship to the fork topology

`upstream-fork-sync` is the **operational automation layer** over a generic fork-and-mirror topology. [[the-lovyou-ai-fork]] documents the *original* origin-fork relationship that the pattern grew around (now historical — that upstream is dormant and the codebase has long since diverged); this tool generalizes the pull-direction automation to any configured upstream source. Mirror branches under `upstream/` stay synchronized on a schedule, while fork-local branches and the human promotion gate (PRs back upstream) remain untouched.

It is a transpara-ai-native tool: it pulls from upstream into the fork; it never pushes from the fork to upstream. This is the correct directionality for [[the-civilization]]'s institutional boundary.

## Sources & provenance

- `transpara-ai/upstream-fork-sync` README.md — fetched via GitHub API 2026-06-14; repo description, architecture sections, safety contract, local commands, Quick Start steps, core references table
- `transpara-ai/upstream-fork-sync` commit log — five most recent commits, fetched 2026-06-14; all dated 2026-06-12
- `transpara-ai/upstream-fork-sync` repo metadata — fetched via `gh repo view` 2026-06-14; `updatedAt: 2026-06-12T22:11:48Z`, description string

**Thin spots:** The README was the sole source; no `src/` code was read. The denylist-vs-allowlist characterization in the safety section is this article's analysis of the README text ("default policy refuses to write to branches such as…"); the README does not use the word "denylist" or "allowlist" explicitly. Internal docs (`docs/` directory contents) were not fetched.
