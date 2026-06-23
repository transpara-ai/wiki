# Civilization Arc — Date Ownership & Backfill Feasibility

**Date:** 2026-06-21 · **Branch:** `claude/elegant-jang-3373f3` · **Status:** Tier-1 implemented in this branch
**Question (Michael):** "once 2,3,4,5 are done we'll revisit who precisely OWNS the dates" — and whether
that unblocks #1 (dates on tooltip/detail), #6 (date-based x-axis + duration-proportional widths), and
real Actor attribution.

---

## TL;DR / Recommendation

- **Real dates ARE recoverable** for the items that cite a PR/issue — **proven**, not theoretical. The arc
  items are effectively a foreign-key table; `gh api repos/transpara-ai/<repo>/issues/<n>` resolves each
  cited ref to a real `merged_at` (and they corroborate the labels — docs#138 *is* "revise Gate K pre-live
  closeout").
- **Coverage is partial by design.** Of 116 items: **23 done items are dated in this branch** (committed `date`
  + `ref` fields), **72 have no datable event** (reconstructed narrative / design-principle beats), **21 are future/planned** (haven't
  happened — no date possible).
- **Who owns the dates:** the **source-of-truth repos' GitHub PR/issue history** — overwhelmingly
  `transpara-ai/docs` (governance/gates), plus `work`/`hive`/`site`/`eventgraph` for implementation.
  `wiki` owns only the *reconstructed pre-history*, which is "not commit-derived" by its own
  honesty note and therefore **ownerless for dating**.
- **Done in this branch:** #1 (tooltip/detail dates) for the Tier-1 done items — honest, graceful blanks
  elsewhere. Dates are baked into `civilizationArcData.js`, render in tooltip/detail, and are covered by
  fail-closed validation/tests.
- **Don't:** #6 (date x-axis / duration-proportional widths) — too sparse; a date axis with ~¾ of dots
  unplaceable forces fabricated positions, contradicting the accuracy-first redesign. The ordinal-`seq`
  axis is the *honest* representation. (Optional later: a "dated-only" sparse lens.)
- **Actor:** low value. GitHub author/merger collapses to `MichaelSaucier` (single-human-operator model);
  real agent attribution lives only in `[codex]`/`[claude]` title prefixes (fragile/partial). Not worth a
  primary feature; it would *misrepresent* the documented single-authority operating model.
- **Air-gap constraint:** dates must be **baked into the data file at rest** (one-time human-run deref
  script), **not** fetched during `build_site.py` (runs air-gapped on nucbuntu; network-at-build breaks the
  air gap and makes builds nondeterministic).

---

## Evidence

### Data model (elegant-jang `compile/assets/civilizationArcData.js`, 116 items)

- Per-item fields now allow `ref` and `date` on historical `done` items. `href` continues to point to wiki
  article pages (`the-20-primitives.html`) and is not a date source.
- Tooltip/detail rendering shows `date` only when present and remains blank for undated items.

### Coverage audit (programmatic load of the data; `/tmp/arc_date_audit.js`)

| Population | Count | Datable? |
|---|---:|---|
| **Total items** | 116 | — |
| Historical (`done`/`active`) | 95 | a date *can* exist |
| Future (`planned`/`future`) | 21 | **no** — hasn't happened |
| Done items with committed `date` + `ref` | **23** | **implemented** (Tier 1) |
| Historical without a committed date | 72 | mostly no (see tiers) |
| provenance `derived` / `reconstructed` | 17 / 99 | — |

### Recoverability — proven by dereference (read-only `gh`, all transpara-ai)

| Ref | Kind | Real date (`closed/merged_at`) | Title corroborates label |
|---|---|---|---|
| eventgraph#34 | PR | 2026-05-14 | Stage 5 — TraceCompletenessGate … |
| work#41 | PR | 2026-06-02 | Implement Gate I capability monitoring fixture |
| hive#148 | PR | 2026-06-10 | feat(loop): … keepalive reviewer (closes F8) |
| docs#127 | PR | 2026-06-12 | accept the v4.0 seed doctrine | (matches inline prose `(2026-06-12)`) |
| docs#132 | PR | 2026-06-15 | record Event-1 Gate K authority grant |
| docs#138 | PR | 2026-06-17 | **revise Gate K pre-live closeout** |
| docs#142 | PR | 2026-06-18 | Accept v4.0 canonical docs baseline |

The recoverable timeline spans **~5 weeks (mid-May → mid-June 2026)**. Everything before is the
reconstructed Feb-genesis pre-history with no commit dates.

---

## Who owns the dates

| Owner | Items | Date source | Quality |
|---|---|---|---|
| `transpara-ai/docs` PR/issue history | 62 docs-owned (governance/gates/events) | `merged_at` of the cited PR | real, precise for implemented Tier-1 refs |
| `work`/`hive`/`site`/`eventgraph` history | implementation items | `merged_at` of the cited PR | real, precise |
| `wiki` (reconstructed narrative) | origin story + design-principle beats | **none** — "not commit-derived" by its own note | n/a (undatable by design) |

---

## Feasibility per deferred feature

### #1 — dates on tooltip / detail panel  →  **DONE (Tier 1)**
- 23 done items carry real, sourced `date` + `ref` fields. Undated items show no date line.
- `validateItems` fails closed on malformed refs, non-ISO dates, and dates attached to non-`done` items.

### #6 — date-based x-axis + duration-proportional widths  →  **DON'T**
- Even Tier 1 + Tier 2 (below) dates remain well under half the items; most have no real position. A date axis then
  either drops most of the chart or fabricates positions — the exact "decorative axis that encodes nothing"
  failure the Direction-C rebuild was meant to kill. Ordinal-`seq` is the accurate choice.
- *Optional future:* a separate "dated-only" sparse timeline lens showing only real dated events.

### Actor attribution  →  **SKIP (low value)**
- PR `author`/`merged_by` ≈ `MichaelSaucier` for nearly all (single-human-operator model). Agent-level
  actor exists only as `[codex]`/`[claude]` title prefixes — fragile, partial, and attributing distinct
  "actors" would misrepresent the documented single-authority posture.

---

## Datability tiers (the 116, precisely)

- **Tier 1 — committed in this branch (23):** done items with reliable PR/issue dates.
- **Tier 2 — date with PR-hunting research (~30–40):** real-but-uncited gates (Gate-A..D, security gates,
  several `G-x.x` docs gates) + worklist `C*/N*` items. Moderate–high manual effort, variable reliability.
- **Tier 3 — undatable by design:** reconstructed origin-story + design-principle beats (MEM "memory
  remains advisory", PROMPT, RITUAL, D15, RO, LENS, …) + all 21 future/planned. No real date exists.

---

## Implemented Tier-1 Shape

1. Cited refs are structured as `ref: "docs#138"` style fields.
2. ISO dates are committed values in the data file; no build-time network is used.
3. Tooltip and detail panel render dates when present.
4. Tests cover ISO/ref validation, done-only dates, and graceful absence for undated items.

**Risk:** low (additive; graceful fallback stays wired). **Reversible:** yes.

---

## What I did NOT do / caveats

- This branch now includes the Tier-1 code/data/test implementation described above.
- Did not exhaustively map every Tier-2 ref to a PR (that *is* the moderate-effort work, deferred to a
  greenlight).
- `gh` deref reflects state as queried 2026-06-21; baked dates would be a point-in-time snapshot,
  refreshable by re-running the script.
