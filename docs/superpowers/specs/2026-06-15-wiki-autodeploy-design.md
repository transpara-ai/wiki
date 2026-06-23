# Spec — auto-deploy the Civilization Wiki on merge

**Date:** 2026-06-15 (revised 2026-06-18) · **Owner:** Michael Saucier · **Authority:** planning (proposal) · **Status:** design approved 2026-06-15; revised + re-approved 2026-06-18 (build boundary + authority gate + self-build principle)

## Revision 2026-06-18 — what changed and why

The 2026-06-15 design (preserved below, refined inline) is updated by three decisions:

1. **Build boundary.** This iteration builds code + stdlib tests + unit files + docs to a **PR and stops**. The systemd timer is **not** installed or enabled, and nothing deploys live. Activation and the first deploy-authorization are deliberate human steps documented in `REBUILD.md`. Unit files ship inert; the PR ships **no** active authorization.
2. **Authority gate (governance), self-governed.** A new deny-closed **authorization gate (gate 0)** precedes every deploy: the poller refuses unless a civilization-native `df:`-style governance artifact authorizes the *exact* target commit. Deployment is human-gated **in code**, not merely by withholding activation.
3. **Self-build principle** — *"the Civilization must build itself by using itself as the builder"* — applied in full, three facets:
   - **Self-hosting:** only the civilization's own machinery builds it — `refresh.py` → `build_site.py`, local git state, Python stdlib, air-gap. No external CI, cloud, webhook, or hosted runner is ever the builder.
   - **Self-referential:** deploy and blocked-deploy events surface on the live site and on the rendered `wiki/deployment-arc.md` page — the wiki visibly documents its own building.
   - **Self-governed:** the authorization gate reads a `df:`-style governance artifact, the same family the stack uses elsewhere — it deploys under its own rules.

**Consequence:** the deploy target is no longer bleeding-edge `origin/main` but the **authorized SHA** (an ancestor-or-equal of `origin/main`). You deploy exactly what was blessed; the authorization commit itself and anything newer stay undeployed until separately authorized.

## Problem

Merging a PR to `main` does not update the live site. The served `dist/` (nucbuntu `:8787`) is only rebuilt by a nightly `0 3 * * *` cron running `compile/refresh.py`, and the serving checkout had been parked on a stale branch — so merged work sat invisible for hours, and a manual `git pull` + `refresh.py` was the only way to "make it alive." We want a merge to `main` to automatically **evaluate** whether it should rebuild + redeploy, and do so **only when authorized and warranted**, without ever deploying broken, unauthorized, or uncommitted state.

## Goal

An authorized merge results in an automatic, **path-evaluated**, **authorized**, **fail-safe** rebuild + redeploy of the live site on nucbuntu, within ~2 minutes, driven by a local poller (outbound-only, air-gap-clean) using only the civilization's own build machinery. When a deploy is blocked (unauthorized, dirty checkout, build failure), the live site says so.

## Approved decisions

1. **Trigger:** a local poller on nucbuntu (over a self-hosted Actions runner or a cloud/local hybrid). Outbound `git fetch` only; no inbound webhook. *(self-hosting)*
2. **Evaluation:** deterministic **path allowlist** — deploy only when the diff touches site-affecting files (over always-deploy or an LLM judgment).
3. **Scheduler:** a **systemd timer + oneshot service** (over cron+flock) — built-in overlap prevention, `journalctl` logging, `Persistent=true` catch-up after downtime.
4. **Dirty-block visibility:** **log + surface on the live site** — a blocked deploy flips a warning banner on the served pages.
5. **`[2026-06-18]` Authorization (gate 0):** a deny-closed governance gate; deploy refuses unless a tracked `df:`-style deploy-authorization artifact names the exact target SHA, is unexpired, and that SHA is a real ancestor of `origin/main`. *(self-governed)*
6. **`[2026-06-18]` Deploy target = the authorized SHA**, not bleeding-edge `origin/main`.
7. **`[2026-06-18]` Self-referential surfacing:** deploy state is rendered on the live site and the `deployment-arc` wiki page via client-side fetch of a status file — never by the deploy script committing to git.
8. **`[2026-06-18]` Build boundary:** code + tests + inert unit files + docs to a PR; no live activation.

## Non-goals (YAGNI)

No self-hosted runner; no inbound webhook; no SSH/remote deploy; no LLM in the deploy path; no rollback/blue-green (the build is a deterministic rebuild of static files); no change to *how* the site is served (`python3 -m http.server` stays). The nightly `refresh.py` cron stays (it catches dark-factory **source-mirror** changes, which are not git merges and so are out of this evaluator's scope). **No cryptographic signature on the authorization artifact in this iteration** — the hardening path (detached signature or gate-tool-produced artifact) is documented, not built. **No live activation** of the timer in this iteration.

## Architecture

A new `compile/autodeploy.py`, invoked every ~2 min by a systemd timer. Each tick is a small, idempotent, crash-safe state machine keyed on a persisted "last deployed" SHA, rebuilding **only** via the civilization's own `refresh.py` → `build_site.py`:

```
fetch origin (outbound only)
  auth   = read compile/deploy-authorization.json
  target = auth.authorized_sha                      # not necessarily origin/main HEAD
  target == deployed-SHA ?
     yes → write deploy-status (clear) → exit (no-op)
     no  → evaluate: changed = git diff --name-only <deployed-SHA>..<target>
            site_affecting(changed) ?
              no  → log "skip: no site-affecting changes" → advance deployed-SHA → status (clear) → exit
              yes → PREFLIGHT GATES (all must pass, else REFUSE) →
                    git merge --ff-only <target> → python3 compile/refresh.py →
                    refresh.py exit 0 ? → advance deployed-SHA + append history + write status (clear)
                                        : keep old deployed-SHA + old dist (build failed) + log
```

**The unit of truth is `compile/.deployed-sha` = the commit currently live.** A missed tick, reboot, or failed build self-heals on the next poll: it never double-deploys and never loses its place. First run with no state file: initialize it to the **current checkout `HEAD`** (the commit the present `dist/` was actually built from) and exit — never to `origin/main` or the authorized target, since those may be ahead of what is live; the gap is then evaluated and deployed on the next tick. A `git diff` error against a corrupt/missing deployed-sha is an unreadable/ambiguous state and **refuses** (gate 4), never a silent "no changes".

## `autodeploy.py` contract (functions, testable in isolation)

- `site_affecting(paths: list[str]) -> (bool, list[str])` — pure. True if any path matches the allowlist; returns the matching paths (for the log reason).
  - **Allowlist (deploy when any match):** `wiki/` (any `.md`), `index.md`, `compile/build_site.py`, `compile/refresh.py`, `compile/stats.py`, `compile/inflight.py`, `compile/assets/` (any), `PROVENANCE.md`.
  - **Excluded (skip if *only* these):** `docs/`, `.github/`, `README.md`, `compile/test_*.py`, `compile/autodeploy.py`, `compile/systemd/`, the spec/plan docs, `compile/deploy-authorization*.json`.
- `authorized(root, now, ancestor_check) -> (ok: bool, reason: str, sha: str | None)` — **`[2026-06-18]`** pure, deny-closed; reads + validates the artifact and, on grant, returns the validated `authorized_sha` (which *is* the deploy target). `ancestor_check` is an injected predicate `(sha) -> bool` so the gate is testable without a live repo.
- `preflight(root, target_sha, ancestor_check) -> (ok: bool, reason: str)` — fail-closed technical gates 1–2 (dirty checkout; on-`main` + target legitimacy). Reads git state, no writes.
- `deploy(root, target_sha, runner) -> (ok: bool, detail: str)` — `git merge --ff-only <target_sha>` then run `refresh.py` via the injected `runner`; returns False (no SHA advance) on any non-zero.
- `write_deploy_status(root, blocked, reason, deployed_sha, target_sha, authorized, now, recent)` — writes `dist/deploy-status.json` (see Visibility).
- `append_deploy_history(root, event)` — **`[2026-06-18]`** appends a record to the git-ignored `compile/.deploy-history.json` (canonical, persists across rebuilds); the last N are echoed into `deploy-status.json.recent`.
- `main()` — orchestrates the tick; the **only** place git-mutating / `refresh.py` calls happen; writes the log + state.

## Authorization artifact `[2026-06-18]` (self-governed, deny-closed)

Tracked file `compile/deploy-authorization.json` (a `df:`-style governance record, auditable in git history):

```json
{
  "df": "deploy-authorization",
  "authorized_sha": "<full 40-char commit SHA authorized to deploy>",
  "authority": "<who authorized — name / role>",
  "authorized_at": "<ISO-8601>",
  "expires_at": "<ISO-8601>",
  "reason": "<short note>"
}
```

`authorized(root, target_sha, now, ancestor_check)` **grants only when ALL hold**, else refuses:

1. the file exists and parses as JSON;
2. `df == "deploy-authorization"` and all six fields are present and well-typed;
3. `authorized_sha` is a 40-char hex SHA — it *is* the deploy target (`target = authorized_sha`), so there is no separate value to mismatch;
4. `authorized_at <= now < expires_at` (both parse as ISO-8601; not-yet-valid and expired both refuse);
5. `ancestor_check(authorized_sha)` is true — the SHA is a real ancestor-or-equal of `origin/main` (never deploy a SHA not in merged history).

Any absent / unreadable / malformed / wrong-`df` / missing-field / SHA-mismatch / expired / not-yet-valid / non-ancestor case → **refuse** with a specific reason. There is **no `else` or fallthrough that authorizes.** Deny is the default; grant is the single explicitly-proven branch.

- **Decoupled from merge-review.** Merging to `main` never authorizes a deploy. A human commits a deploy-authorization naming an exact, reviewed SHA — a deliberate, auditable governance act. Because committing the authorization advances `main` past the authorized SHA, the authorization commit and everything newer remain undeployed until separately authorized (this is the intended "deploy exactly what was blessed" semantic).
- **PR safety.** This PR ships **no active `deploy-authorization.json`** (its absence → refuse) — only `compile/deploy-authorization.example.json` (an inert template with an obviously-invalid SHA) and the runbook. Merging the feature can therefore never itself authorize a deploy. The real `deploy-authorization.json` is git-ignored against accidental partial commits and is written deliberately when authorizing.
- **Hardening path (documented, not built):** require a detached signature over the artifact by an authorized key, or require it be produced/verified by the existing `cross-family-review-gate` tooling.

## Fail-safe gates (deny-closed — encodes the failure we hit this session)

A deploy proceeds **only** when every gate passes. Any failure → **refuse, log a `REFUSED` line, set the blocked banner, do not advance the deployed-SHA**, retry next tick.

0. **`[2026-06-18]` Unauthorized** — `authorized(...)` false → refuse. The first gate; checked before any merge/build.
1. **Dirty serving checkout** — **tracked** modifications present (`git status --porcelain --untracked-files=no` non-empty) → refuse. Never deploy over uncommitted tracked work. *Untracked* files (e.g. `.claude/`, git-ignored build output) do **not** block — but if an untracked file would collide with a file the merge adds, the `git merge --ff-only` in `deploy()` fails and is caught as a build/merge failure (gate 3), so that case still refuses rather than clobbering.
2. **Not on `main`, or target not legitimate** — HEAD not on `main`, or `ancestor_check(target)` false (target not in `origin/main` history) → refuse. Fast-forwardability itself is enforced by `git merge --ff-only <target>` in `deploy()`: a non-ff merge fails and is handled as gate 3 (keep old `dist/` + old SHA; never force).
3. **Build failure** (`refresh.py` exit ≠ 0) → keep old `dist/` and old deployed-SHA. Never serve a half-built site.
4. **Fetch / diff / unreadable-state error** → refuse this tick (transient), retry next.
5. **Concurrency** → the systemd oneshot service guarantees one instance; the timer won't start a second while one runs. A `compile/.autodeploy.lock` is belt-and-suspenders against a manual run colliding with the 03:00 nightly.

A wrongly-*skipped* or *refused* deploy = a stale site (visible, recoverable on the next tick once authorized/clean). A wrongly-*done* deploy is prevented by the gates. The permissive branch (actually deploy) is the fully-proven one; every unknown / dirty / failed / unauthorized state falls through to refuse.

## Visibility & self-referential surfacing `[2026-06-18]`

- `autodeploy.py` writes **`dist/deploy-status.json`** every tick: `{"blocked": bool, "reason": str, "since": iso8601, "deployed_sha": str, "target_sha": str, "authorized": bool, "checked": iso8601, "recent": [ {sha, at, result} ... ]}`. `since` is the *first* tick the current block was observed (carried over while still blocked for the same reason, reset when it clears); `checked` is this tick's time; `recent` is the last N entries from the canonical git-ignored `compile/.deploy-history.json`.
- **Reuse the existing banner mechanism.** The site already shows a `compile/refresh-status.json` freshness signal. `compile/build_site.py` gains a sibling client-side fetch baked into the page template: on load, `fetch("deploy-status.json")`; if `blocked`, render a fixed warning bar — *"⚠ Auto-deploy blocked: {reason} (since {since}) — the live site may be behind authorized `main`."* — and always render a small footer indicator *"live deploy: {deployed_sha:7} · {checked}"*.
- **Self-referential loop:** the rendered `wiki/deployment-arc.md` page gains a small live widget (same client-side fetch) showing current deploy state + the `recent` deploys list. The wiki page *about* deployment shows the *actual* live deployment — the civilization documenting its own building.
- **Why client-side fetch, not a rebuild:** a blocked tick must NOT run `build_site.py`, because that would rebuild `dist/` from the *dirty / unauthorized* working tree and could serve the very content we are refusing. Writing the small JSON into the existing `dist/` (whose pages already carry the fetcher from the last clean build) surfaces the warning without any rebuild.
- **Invariant:** the deploy script **never** commits to git and **never** edits tracked wiki content. All surfacing is status/history JSON written into `dist/` (served) and a git-ignored history file; on the next clean authorized deploy, `refresh.py`→`build_site.py` regenerates the pages and `autodeploy` writes `{"blocked": false}`.

## Scheduler (systemd, user-level — NOT activated this iteration)

Repo-tracked unit files under `compile/systemd/`:
- `wiki-autodeploy.service` — `Type=oneshot`, `ExecStart=/usr/bin/python3 /Transpara/transpara-ai/repos/wiki/compile/autodeploy.py` (the serving checkout), run as the `transpara` user.
- `wiki-autodeploy.timer` — `OnBootSec=2min`, `OnUnitActiveSec=2min`, `Persistent=true`, `WantedBy=timers.target`.
- **Provided but not installed/enabled in this iteration.** `REBUILD.md` documents install as **user units** (`systemctl --user enable --now wiki-autodeploy.timer`) with `loginctl enable-linger transpara`, the first-authorization step, and `journalctl --user -u wiki-autodeploy` for logs.

## Files

| File | Change |
|---|---|
| `compile/autodeploy.py` | **new** — poller / evaluator / authorizer / deployer + status + history |
| `compile/deploy-authorization.example.json` | **new** — inert authorization template (invalid SHA) |
| `compile/build_site.py` | modify — bake the `deploy-status.json` fetch + banner + footer indicator into the page template |
| `compile/systemd/wiki-autodeploy.service` / `.timer` | **new** — unit files (inert) |
| `compile/test_autodeploy.py` | **new** — stdlib tests |
| `.gitignore` | modify — ignore `compile/.deployed-sha`, `compile/.autodeploy.lock`, `compile/.deploy-history.json`, `compile/autodeploy.log`, `compile/deploy-authorization.json`, `dist/deploy-status.json` |
| `compile/REBUILD.md` | modify — document the poller, install, first-authorization, and logs |
| `wiki/deployment-arc.md` | modify — add the live deploy-status / recent-deploys widget |

## Tests (`python3 compile/test_autodeploy.py`, stdlib — matches `test_stats.py` / `test_inflight.py`)

1. **site_affecting** — `wiki/x.md` / `index.md` / `compile/assets/style.css` / `compile/inflight.py` → deploy; `docs/y.md` / `.github/ci.yml` / `README.md` / `compile/test_stats.py` / `compile/deploy-authorization.json` only → skip; mixed (docs + wiki) → deploy.
2. **authorized — full domain** (the core of the gate): valid+unexpired+ancestor → grant (returns the SHA); and each of {file absent, unreadable, malformed JSON, wrong `df`, missing field, malformed (non-hex) SHA, expired, not-yet-valid (`authorized_at` in future), non-ancestor} → refuse with a distinct reason. Assert grant is reached on **exactly one** branch.
3. **preflight** — dirty fixture → refuse; non-fast-forward / not-on-main fixture → refuse.
4. **deploy-status JSON** — `write_deploy_status` produces the expected schema for blocked and clear; `since` carries over while blocked and resets when cleared.
5. **build-fail no-advance** — `deploy()` whose injected `refresh.py` runner exits non-zero → returns False and the caller does **not** advance the SHA.

## Acceptance criteria

- An **authorized** merge touching `wiki/**` / `index.md` / `compile/**` is live within ~2 min, with a `deployed <sha>: <reason>` log line.
- A docs-only authorized change logs `skip` and advances the SHA without rebuilding.
- An **unauthorized** target (no/expired/mismatched authorization) makes the tick **refuse** (no merge, no rebuild, SHA unchanged) and the live site shows the blocked banner.
- A dirty serving checkout makes the tick **refuse** and shows the blocked banner.
- A failed `refresh.py` leaves the old `dist/` and old deployed-SHA intact (no broken site served).
- The poller never overlaps itself or the 03:00 nightly; it does no `git push` / commit and no force.
- The rendered `deployment-arc` page shows live deploy state via client-side fetch.
- All `test_autodeploy.py` cases pass.
- This iteration delivers a PR; the timer is not activated and no `deploy-authorization.json` is shipped.
