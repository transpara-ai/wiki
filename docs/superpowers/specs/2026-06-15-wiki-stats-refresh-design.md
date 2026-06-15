# Spec — durable, idempotent Civilization-Wiki stats refresh

**Date:** 2026-06-15 · **Owner:** Michael Saucier · **Authority:** planning (proposal) · **Status:** design approved 2026-06-15, pending spec review

## Problem

The wiki's "arc progress" stats live on **two surfaces that drift apart**:

- **Hand-maintained:** the freshness table in `index.md` (`89 · 25 foundational · 24 architecture · …`) and the frontmatter `article_count:` are *typed by hand*. Nothing recomputes them, so an on-demand "update the table" has no command behind it — it is a manual edit.
- **Auto but ephemeral:** `compile/refresh.py` computes the real counts into `compile/refresh-status.json`, which is **gitignored**, per-checkout, and only feeds the served HTML banner. In a worktree it writes a throwaway `dist/`, so nothing durable happens.

Result: the nightly cron freshens the *banner*; the committed *table* goes stale silently; on-demand table updates are manual typing; and none of the computed stats are durably stored. Not idempotent (hand edits drift from truth), not durable (ephemeral outputs), and the cron path and on-demand path touch different things.

## Goal

One idempotent generator that computes article stats **from ground truth** (`wiki/*.md` frontmatter), writes them into the **committed source of truth** (`index.md`), and is invoked **identically** by the nightly cron and by an on-demand run. Never auto-commits, never pushes.

## Non-goals (YAGNI)

Un-gitignoring a stats JSON; a CI `--check` staleness gate; auto-commit/auto-push; any LLM/content re-compile; changes to the serving infrastructure. A CI staleness check is noted as a *possible future* item only.

## Approved decisions

1. **Durability policy:** regenerate files in place; **the human commits the diff**. No autonomous commit or push (honors the standing git rules). Re-running with no source change produces no diff.
2. **Approach A:** a marker-delimited **generated region** inside `index.md` (chosen over a committed `stats.json` or a separate `STATS.md`, both of which reintroduce a second surface that can drift). Keeps one GitHub-readable committed artifact, per `DESIGN.md`.

## Refinements since approval (flagged for review)

These tighten the approved design; they do not change its shape.

1. **The generated region is a prose line, not a mini-table.** HTML-comment markers cannot sit between markdown table rows without splitting the table, and a one-row "table" reads awkwardly. A single bolded prose line under the human freshness table renders cleanly and the markers wrap a non-table block with no rendering hazard.
2. **The committed region holds only ground-truth-derived stats** — `article_count` and the per-tier breakdown, which are a *pure function of committed `wiki/*.md`*. The refresh **timestamp**, **stale-article list**, and **sources count** stay in the ephemeral banner (`refresh-status.json`). Consequence: the committed block yields an **empty `git diff` unless the corpus actually changed** — true idempotency, with no daily timestamp-only commit noise. A fresh clone reproduces the block byte-for-byte without needing the source mirror.

## Architecture / components

| File | Change | Purpose |
|---|---|---|
| `compile/stats.py` | **new** | The single compute + write module. `compute_counts(root)`, `render_stats_line(counts)`, `write_index_block(index_path, counts)`. Pure compute is stateless and deterministic. |
| `compile/refresh.py` | modify | After the existing source hash/diff, call `compute_counts()`, fail-closed guard on it, write `refresh-status.json` (now sourced from `compute_counts` for `article_count`), **rewrite the `index.md` generated block + frontmatter `article_count`**, then rebuild the site. No commit/push (unchanged). |
| `index.md` | one-time | Insert the `stats:begin`/`stats:end` markers + the seed prose line beneath the human freshness table. |
| `compile/test_stats.py` | **new** | Stdlib-assert tests (no pytest dep — air-gap friendly): fixture counts, idempotency, marker fail-loud, honesty, zero-count guard, unknown-tier visibility. |
| `compile/REBUILD.md` | modify | Document `refresh.py` as *both* the cron job and the on-demand "update the table now" command, and that it leaves a diff you commit. |
| `compile/build_site.py` | **no change** | The banner already reads `refresh-status.json`; it never duplicates the breakdown text, so there is no drift to fix and nothing to edit. Verify only. |

## `compute_counts(root)` contract

- **Signature:** `compute_counts(root: Path) -> dict`.
- **Reads:** `root/wiki/*.md` (glob excludes `.gitkeep`). For each file, parse frontmatter and read `tier:`.
- **Returns:** `{"article_count": int, "tier_counts": list[tuple[str, int]]}`.
  - `article_count` = number of `wiki/*.md` files.
  - `tier_counts` = ordered `(tier, count)` pairs. Canonical order first — `foundational, architecture, arc, investigation, concept, meta` — then **any non-canonical tier value appended (sorted)**, and a `(no-tier)` bucket if any article lacks a `tier:` field. Nothing is silently folded into a default (fail-loud: an unexpected tier shows up in the output instead of being hidden).
- **Invariant:** `sum(c for _, c in tier_counts) == article_count` — asserted; a mismatch raises.
- **Purity:** no writes, no timestamps, no snapshot/diff state. Same inputs → same output. This is what makes the committed block idempotent.

## Generated-block contract

- **Markers (own lines, beneath the human freshness table):**
  - begin: `<!-- stats:begin — generated by compile/refresh.py from wiki/ frontmatter; do not hand-edit between these markers -->`
  - end: `<!-- stats:end -->`
- **Content between markers** (the only thing the generator owns), rewritten verbatim each run:
  - `**Article count (auto-derived from wiki/ frontmatter):** {N} — {t1count} {t1} · {t2count} {t2} · …`
- **Frontmatter:** the generator also sets the `article_count:` line in `index.md` frontmatter to `N` (idempotent single-line replace).
- **Never touched by the refresh:** `last_compiled`, `run`, `completeness`, and all prose. `last_compiled` is the LLM re-synthesis date and is human-authored; the deterministic refresh must not move it (preserves the wiki's fail-loud "never looks-current-while-stale" contract).

## `refresh.py` behavior (ordered)

1. Mirror first-party sources into `raw/transpara/` (unchanged).
2. Hash `raw/`, diff against `source-snapshot.json` → `sources_changed`, `stale_articles` (unchanged).
3. `counts = compute_counts(ROOT)`.
4. **Fail-closed guard:** if `counts["article_count"] == 0` → print error, `sys.exit(1)` (a zero/unknown count must never overwrite a real one).
5. Write `refresh-status.json` with `synced` (timestamp), `article_count` (from `counts` — single source), `sources_total` (= `len(cur)`, the count of hashed `raw/` sources from step 2, unchanged), `sources_changed`, `stale_articles`, `note`.
6. `write_index_block(INDEX, counts)` — rewrites the marker region + frontmatter `article_count`. On any marker error → print a clear message and `sys.exit(1)` **before** rebuilding (never ship a site whose committed table the generator could not verify).
7. Write `source-snapshot.json` (unchanged).
8. Rebuild the site via `build_site.py` (unchanged).
9. Print a summary including whether `index.md` changed.

No `git` invocation anywhere in `refresh.py`.

## Fail-loud rules (allowlist, fail-closed)

- **Markers:** proceed **only** when there is exactly one `stats:begin` and exactly one `stats:end`, with `begin` before `end`. Any other state — missing, duplicated, reversed — raises and exits non-zero with no write. (Allowlist the one valid shape; never denylist bad ones.)
- **Zero count:** `article_count == 0` → refuse and exit non-zero.
- **Frontmatter `article_count:`** absent → soft-skip with a printed note (the block still updates). Present more than once → raise (ambiguous).
- **Unknown / missing `tier`:** surfaced as its own visible bucket, never folded into a default.

## Data flow

```
ground truth: wiki/*.md frontmatter
        │
        ▼
  compute_counts()  ── single source of compute ──┐
        │ (pure: article_count + tier breakdown)   │
        ▼                                           ▼
  index.md generated block               refresh-status.json
  [durable · committed by you]            (+ synced, stale, sources_total)
                                                    │ [ephemeral · gitignored]
                                                    ▼
                                          build_site.py banner → dist/
```

Cron (`0 3 * * *`, unchanged) and on-demand (`python3 compile/refresh.py`) invoke the same script → identical effect. A run leaves a reviewable diff in the **main checkout's** working tree; you commit it.

## Tests (written first; `python3 compile/test_stats.py`, stdlib asserts)

1. **Fixture counts** — a temp `wiki/` with known tiers → expected `article_count` and `tier_counts` (order included).
2. **Idempotency** — run `write_index_block` twice on a seeded `index.md` → second run produces byte-identical output (empty diff).
3. **Marker fail-loud** — missing `begin`, missing `end`, duplicated, and reversed each raise.
4. **Honesty** — after a refresh, the `last_compiled` / `run` / `completeness` lines are unchanged.
5. **Zero-count guard** — an empty `wiki/` fixture makes the run refuse (raises / non-zero), without writing.
6. **Unknown-tier visibility** — an article with `tier: bogus` and one with no `tier:` both appear as their own buckets in `tier_counts`.

## Acceptance criteria

- `python3 compile/refresh.py` rewrites the `index.md` generated block + frontmatter `article_count` from ground truth; the served banner still shows freshness from `refresh-status.json`.
- Running it twice with no corpus change leaves an empty `git diff`.
- Removing/duplicating a marker makes the run exit non-zero **and write nothing**.
- The human rows (`last_compiled`, `run`, `completeness`) are never modified by the refresh.
- Cron and on-demand are the same command with the same effect; no commit and no push occur.
- All `test_stats.py` cases pass.

## Cron + on-demand

The nightly cron entry is unchanged (`0 3 * * * … python3 compile/refresh.py`). On-demand is the same command, now documented in `REBUILD.md` as the way to "update the table now." Both leave the diff for the human to commit.
