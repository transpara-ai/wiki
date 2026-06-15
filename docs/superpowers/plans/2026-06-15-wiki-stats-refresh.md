# Durable Idempotent Wiki Stats Refresh — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the Civilization Wiki's article-stats a single computed surface — derived from `wiki/` frontmatter, written idempotently into a marker-delimited block in `index.md` — invoked identically by the nightly cron and on-demand, never auto-committing.

**Architecture:** A new `compile/stats.py` owns all stats compute (`compute_counts`) and the idempotent block writer (`write_index_block`, fail-closed on bad markers). `compile/refresh.py` calls it after its existing source-diff, so the same script updates the durable block (you commit the diff) and the ephemeral banner (`refresh-status.json`). The committed block holds only ground-truth-derived stats (a pure function of `wiki/*.md`), so re-running yields an empty `git diff` unless the corpus changed.

**Tech Stack:** Python 3 standard library only (no pytest, no new deps — air-gap friendly). `python-markdown` already used by the site builder is untouched.

**Spec:** [`docs/superpowers/specs/2026-06-15-wiki-stats-refresh-design.md`](../specs/2026-06-15-wiki-stats-refresh-design.md)

---

## File structure

| File | Responsibility |
|---|---|
| `compile/stats.py` (new) | Pure compute (`compute_counts`, `ensure_nonzero`) + idempotent block writer (`render_stats_line`, `write_index_block`) with fail-closed marker handling. The single source of stats compute. |
| `compile/test_stats.py` (new) | Stdlib-assert tests; auto-discovers `test_*` functions. Run: `python3 compile/test_stats.py`. |
| `index.md` (modify, one-time) | Drop the hand-typed "articles compiled" row; seed the `stats:begin`/`stats:end` block. |
| `compile/refresh.py` (modify) | Source `article_count` from `compute_counts`; write the `index.md` block; fail-closed guards. No `git`. |
| `compile/REBUILD.md` (modify) | Document `refresh.py` as both the cron job and the on-demand "update the table now" command. |

`compile/build_site.py` is intentionally **not** modified — its banner already reads `refresh-status.json` and never duplicates the breakdown text.

**Out of scope (flagged, not built):** the prose mention "89 articles compiled, grouped by tier" under `## Article index` in `index.md` stays hand-maintained this pass; a second generated marker there is a possible follow-up. No auto-commit, no CI `--check`, no serving changes.

---

## Task 1: `compute_counts` + `ensure_nonzero` (pure ground-truth stats)

**Files:**
- Create: `compile/stats.py`
- Test: `compile/test_stats.py`

- [ ] **Step 1: Write the failing tests**

Create `compile/test_stats.py`:

```python
#!/usr/bin/env python3
"""Stdlib-assert tests for compile/stats.py. Run: python3 compile/test_stats.py"""
import sys
import pathlib
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import stats  # noqa: E402


def _wiki(root, articles):
    """articles: dict slug -> tier string, or None for a missing tier field."""
    (root / "wiki").mkdir(parents=True, exist_ok=True)
    for slug, tier in articles.items():
        fm = "---\nentity: %s\n" % slug
        if tier is not None:
            fm += "tier: %s\n" % tier
        fm += "---\n\n# %s\n\nbody\n" % slug
        (root / "wiki" / ("%s.md" % slug)).write_text(fm)


def test_fixture_counts():
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        _wiki(root, {"a": "foundational", "b": "foundational", "c": "arc", "m": "meta"})
        out = stats.compute_counts(root)
        assert out["article_count"] == 4, out
        assert out["tier_counts"] == [("foundational", 2), ("arc", 1), ("meta", 1)], out
    print("ok test_fixture_counts")


def test_unknown_and_missing_tier_visible():
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        _wiki(root, {"a": "foundational", "x": "bogus", "n": None})
        out = stats.compute_counts(root)
        tiers = dict(out["tier_counts"])
        assert tiers.get("bogus") == 1, out
        assert tiers.get(stats.NO_TIER) == 1, out
        assert out["tier_counts"][0] == ("foundational", 1), out  # canonical first
    print("ok test_unknown_and_missing_tier_visible")


def test_zero_count_guard():
    try:
        stats.ensure_nonzero({"article_count": 0, "tier_counts": []})
    except ValueError:
        print("ok test_zero_count_guard")
        return
    raise AssertionError("ensure_nonzero must raise on article_count 0")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
    print("\nall %d stats tests passed" % len(fns))
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 compile/test_stats.py`
Expected: FAIL — `ModuleNotFoundError: No module named 'stats'`.

- [ ] **Step 3: Write the minimal implementation**

Create `compile/stats.py`:

```python
#!/usr/bin/env python3
"""Single source of compute for the Civilization Wiki's article stats and the
durable generated block in index.md.

Pure ground-truth stats (article_count + per-tier breakdown), derived from
wiki/*.md frontmatter. These are a pure function of the committed wiki/ files,
so the generated block re-renders byte-identically unless the corpus changed.
Timestamp / stale / sources counts are operational and live in the ephemeral
refresh-status.json banner, not here.
"""
import re
import pathlib

# Canonical breakdown order. Any tier value NOT listed here, and any article
# missing a `tier:` field (-> NO_TIER), is surfaced as its own bucket rather
# than folded into a default: an unexpected tier shows up, never hides.
CANONICAL_TIERS = ["foundational", "architecture", "arc",
                   "investigation", "concept", "meta"]
NO_TIER = "(no-tier)"

_TIER_RE = re.compile(r"^tier:[ \t]*(.+?)[ \t]*$", re.M)


def _frontmatter(text):
    """The YAML frontmatter block between the first two '---' fences, or ''."""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[3:end]
    return ""


def _tier_of(path):
    m = _TIER_RE.search(_frontmatter(path.read_text()))
    return m.group(1).strip().strip('"').strip("'") if m else NO_TIER


def compute_counts(root):
    """Pure ground-truth stats from wiki/*.md frontmatter.

    Returns {"article_count": int, "tier_counts": [(tier, count), ...]} with
    canonical tiers first (CANONICAL_TIERS order, only those present), then any
    other tier values plus NO_TIER appended in sorted order. Deterministic and
    side-effect free.
    """
    root = pathlib.Path(root)
    counts = {}
    total = 0
    for p in sorted((root / "wiki").glob("*.md")):
        tier = _tier_of(p)
        counts[tier] = counts.get(tier, 0) + 1
        total += 1
    ordered = [(t, counts[t]) for t in CANONICAL_TIERS if t in counts]
    ordered += [(t, counts[t]) for t in sorted(counts) if t not in CANONICAL_TIERS]
    assert sum(c for _, c in ordered) == total, "tier counts must sum to article_count"
    return {"article_count": total, "tier_counts": ordered}


def ensure_nonzero(counts):
    """Fail-closed guard: a zero article_count must never overwrite a real one."""
    if counts["article_count"] <= 0:
        raise ValueError("refusing to write stats: article_count is 0 "
                         "(likely a wrong path, not an empty wiki)")
    return counts
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python3 compile/test_stats.py`
Expected: PASS — `all 3 stats tests passed`.

- [ ] **Step 5: Commit**

```bash
git add compile/stats.py compile/test_stats.py
git commit -m "feat(compile): add compute_counts ground-truth wiki stats

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: idempotent marker-delimited block writer

**Files:**
- Modify: `compile/stats.py` (append functions)
- Test: `compile/test_stats.py` (append tests)

- [ ] **Step 1: Write the failing tests**

Append these functions to `compile/test_stats.py` (above the `if __name__` block; the runner auto-discovers them):

```python
def test_idempotent_write():
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        _wiki(root, {"a": "foundational", "c": "arc"})
        idx = root / "index.md"
        idx.write_text(
            "---\narticle_count: 0\nlast_compiled: \"2026-06-14\"\n---\n\n"
            "| **run** | **Run-3** |\n\n"
            + stats.BEGIN_MARKER + "\nOLD\n" + stats.END_MARKER + "\n")
        counts = stats.compute_counts(root)
        assert stats.write_index_block(idx, counts) is True    # first write changes
        first = idx.read_text()
        assert stats.write_index_block(idx, counts) is False   # second is a no-op
        assert idx.read_text() == first                        # byte-identical
        assert "2 — 1 foundational · 1 arc" in first.replace("**", "")
        assert "article_count: 2" in first                     # frontmatter updated
    print("ok test_idempotent_write")


def test_honesty_human_rows_untouched():
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        _wiki(root, {"a": "arc"})
        idx = root / "index.md"
        human = ("---\narticle_count: 99\nlast_compiled: \"2026-06-14\"\n---\n\n"
                 "| **last_compiled** | **2026-06-14** |\n"
                 "| **run** | **Run-3 (x)** |\n"
                 "| **completeness** | **PARTIAL — y** |\n\n")
        idx.write_text(human + stats.BEGIN_MARKER + "\nOLD\n" + stats.END_MARKER + "\n")
        stats.write_index_block(idx, stats.compute_counts(root))
        out = idx.read_text()
        assert "| **last_compiled** | **2026-06-14** |" in out
        assert "| **run** | **Run-3 (x)** |" in out
        assert "| **completeness** | **PARTIAL — y** |" in out
    print("ok test_honesty_human_rows_untouched")


def test_marker_fail_loud():
    counts = {"article_count": 1, "tier_counts": [("arc", 1)]}
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        idx = root / "index.md"
        cases = [
            "no markers here",
            stats.BEGIN_MARKER + "\nx\n",                                  # missing end
            "\nx\n" + stats.END_MARKER,                                    # missing begin
            (stats.BEGIN_MARKER + "\nx\n" + stats.END_MARKER + "\n"
             + stats.BEGIN_MARKER + "\ny\n" + stats.END_MARKER),          # duplicated
            stats.END_MARKER + "\nx\n" + stats.BEGIN_MARKER,              # reversed
        ]
        for bad in cases:
            idx.write_text(bad)
            try:
                stats.write_index_block(idx, counts)
            except ValueError:
                continue
            raise AssertionError("expected ValueError for: %r" % bad[:40])
    print("ok test_marker_fail_loud")
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 compile/test_stats.py`
Expected: FAIL — `AttributeError: module 'stats' has no attribute 'BEGIN_MARKER'`.

- [ ] **Step 3: Write the minimal implementation**

Append to `compile/stats.py`:

```python
# --- generated-block markers (the writer owns ONLY what is between them) ---
BEGIN_MARKER = ("<!-- stats:begin — generated by compile/refresh.py from wiki/ "
                "frontmatter; do not hand-edit between these markers -->")
END_MARKER = "<!-- stats:end -->"

_BEGIN_RE = re.compile(r"<!--\s*stats:begin\b.*?-->", re.S)
_END_RE = re.compile(r"<!--\s*stats:end\s*-->")
_ARTICLE_COUNT_RE = re.compile(r"^(article_count:[ \t]*)(\d+)[ \t]*$", re.M)


def render_stats_line(counts):
    """The single prose line the generator owns (between the markers)."""
    breakdown = " · ".join("%d %s" % (c, t) for t, c in counts["tier_counts"])
    return ("**Article count (auto-derived from `wiki/` frontmatter):** "
            "%d — %s" % (counts["article_count"], breakdown))


def _replace_between_markers(text, new_inner):
    """Replace content between the stats markers. Fail-closed: require exactly
    one begin and one end, begin before end; otherwise raise ValueError."""
    begins = list(_BEGIN_RE.finditer(text))
    ends = list(_END_RE.finditer(text))
    if len(begins) != 1 or len(ends) != 1:
        raise ValueError("stats markers must appear exactly once each: "
                         "found %d begin, %d end" % (len(begins), len(ends)))
    b, e = begins[0], ends[0]
    if b.start() >= e.start():
        raise ValueError("stats:begin must appear before stats:end")
    return text[:b.end()] + "\n" + new_inner + "\n" + text[e.start():]


def _set_frontmatter_article_count(text, n):
    """Set the frontmatter article_count line to n. Absent -> unchanged.
    Present more than once -> raise (ambiguous)."""
    matches = list(_ARTICLE_COUNT_RE.finditer(text))
    if not matches:
        return text
    if len(matches) > 1:
        raise ValueError("article_count appears %d times; expected at most one"
                         % len(matches))
    return _ARTICLE_COUNT_RE.sub(lambda m: "%s%d" % (m.group(1), n), text, count=1)


def write_index_block(index_path, counts):
    """Rewrite the generated block + frontmatter article_count in index.md from
    counts. Idempotent: identical counts -> identical bytes -> no write. Returns
    True if the file changed. Raises ValueError on malformed markers."""
    index_path = pathlib.Path(index_path)
    text = index_path.read_text()
    new_text = _replace_between_markers(text, render_stats_line(counts))
    new_text = _set_frontmatter_article_count(new_text, counts["article_count"])
    if new_text != text:
        index_path.write_text(new_text)
        return True
    return False
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python3 compile/test_stats.py`
Expected: PASS — `all 6 stats tests passed`.

- [ ] **Step 5: Commit**

```bash
git add compile/stats.py compile/test_stats.py
git commit -m "feat(compile): add idempotent marker-delimited stats block writer

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 3: seed the generated block in `index.md`

**Files:**
- Modify: `index.md` (freshness table + frontmatter already has `article_count: 89`)

- [ ] **Step 1: Replace the hand-typed row with the generated block**

In `index.md`, replace this exact two-row slice of the freshness table:

```markdown
| **articles compiled** | **89** (25 foundational · 24 architecture · 10 arc · 16 investigation · 13 concept · 1 meta) |
| **completeness** | **PARTIAL — arc spine, philosophy, runtime objects, and thirteen-graphs complete; full corpus sweep still deferred** |
```

with (drops the hand-typed row, keeps completeness, appends the seeded block — values match what the generator will produce for the current corpus, so the first refresh is a no-op):

```markdown
| **completeness** | **PARTIAL — arc spine, philosophy, runtime objects, and thirteen-graphs complete; full corpus sweep still deferred** |

<!-- stats:begin — generated by compile/refresh.py from wiki/ frontmatter; do not hand-edit between these markers -->
**Article count (auto-derived from `wiki/` frontmatter):** 89 — 25 foundational · 24 architecture · 10 arc · 16 investigation · 13 concept · 1 meta
<!-- stats:end -->
```

- [ ] **Step 2: Verify the markers are present exactly once and the table is intact**

Run: `grep -c 'stats:begin' index.md; grep -c 'stats:end' index.md; grep -c 'articles compiled' index.md`
Expected: `1`, then `1`, then `0` (the hand-typed row is gone).

- [ ] **Step 3: Commit**

```bash
git add index.md
git commit -m "feat(wiki): seed generated stats region in index.md freshness table

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 4: wire `refresh.py` to compute and write the block

**Files:**
- Modify: `compile/refresh.py`

- [ ] **Step 1: Add the imports**

In `compile/refresh.py`, change the import block:

```python
import json
import hashlib
import subprocess
import pathlib
import datetime
import re
```

to add `sys` and the local `stats` module (`compile/` is on `sys.path` because it is the script's directory):

```python
import json
import sys
import hashlib
import subprocess
import pathlib
import datetime
import re

import stats
```

- [ ] **Step 2: Source the count from `compute_counts`, write the block, add guards**

In `compile/refresh.py` `main()`, replace this slice — from the `stale = sorted(...)` line through the `SNAP.write_text(...)` line:

```python
    stale = sorted(set(stale))
    status = {
        "synced": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "article_count": len(list(WIKI.glob("*.md"))),
        "sources_total": len(cur),
        "sources_changed": (len(changed) if prev else 0),
        "stale_articles": stale,
        "note": "deterministic refresh; LLM re-compile is manual (see compile/REBUILD.md); Open Brain deltas not auto-detected",
    }
    STATUS.write_text(json.dumps(status, indent=2))
    SNAP.write_text(json.dumps(cur, indent=2))
```

with (sources `article_count` from `compute_counts`; fail-closed on zero; write the durable block, fail-closed on bad markers before rebuilding):

```python
    stale = sorted(set(stale))

    # Single source of stats compute (pure, ground-truth from wiki/ frontmatter).
    counts = stats.compute_counts(ROOT)
    try:
        stats.ensure_nonzero(counts)
    except ValueError as e:
        print("refresh: %s" % e)
        sys.exit(1)

    status = {
        "synced": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "article_count": counts["article_count"],
        "sources_total": len(cur),
        "sources_changed": (len(changed) if prev else 0),
        "stale_articles": stale,
        "note": "deterministic refresh; LLM re-compile is manual (see compile/REBUILD.md); Open Brain deltas not auto-detected",
    }
    STATUS.write_text(json.dumps(status, indent=2))
    SNAP.write_text(json.dumps(cur, indent=2))

    # Durable, idempotent stats block in the committed index.md (you commit the diff).
    try:
        index_changed = stats.write_index_block(ROOT / "index.md", counts)
    except ValueError as e:
        print("refresh: index.md stats block FAILED — %s" % e)
        sys.exit(1)
```

- [ ] **Step 3: Report whether `index.md` changed**

In `compile/refresh.py` `main()`, replace the final summary print:

```python
    print("refresh: %d articles, %d sources changed, %d stale" %
          (status["article_count"], status["sources_changed"], len(stale)))
```

with:

```python
    print("refresh: %d articles, %d sources changed, %d stale; index.md %s" %
          (counts["article_count"], status["sources_changed"], len(stale),
           "updated" if index_changed else "unchanged"))
```

- [ ] **Step 4: Verify idempotency end-to-end**

Run: `python3 compile/refresh.py && git diff --quiet index.md && echo "IDEMPOTENT: no index.md diff"`
Expected: the refresh prints `... index.md unchanged` (the seed already matches ground truth) and the line `IDEMPOTENT: no index.md diff` prints (exit 0, clean tree for `index.md`).

> If `git diff --quiet index.md` reports a diff, the seed in Task 3 did not match the generator output — inspect `git diff index.md`, align the seeded line, and re-run. (`refresh-status.json` and `dist/` changing is expected; they are gitignored.)

- [ ] **Step 5: Verify the marker fail-closed path**

Run:
```bash
cp index.md /tmp/index.bak && \
python3 - <<'PY'
import pathlib
p = pathlib.Path("index.md")
p.write_text(p.read_text().replace("<!-- stats:end -->", "", 1))  # remove the end marker
PY
python3 compile/refresh.py; echo "exit=$?"
cp /tmp/index.bak index.md
```
Expected: prints `refresh: index.md stats block FAILED — stats markers must appear exactly once each: found 1 begin, 0 end` and `exit=1`. The final `cp` restores `index.md`.

- [ ] **Step 6: Re-run the unit tests, then commit**

Run: `python3 compile/test_stats.py`
Expected: PASS — `all 6 stats tests passed`.

```bash
git add compile/refresh.py
git commit -m "feat(compile): write durable idempotent stats block from refresh.py

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 5: document on-demand refresh in `REBUILD.md`

**Files:**
- Modify: `compile/REBUILD.md`

- [ ] **Step 1: Update the Tier-1 description**

In `compile/REBUILD.md`, replace this list item under "Tier 1":

```markdown
4. writes `compile/refresh-status.json` — the fail-loud freshness banner the served site shows,
5. regenerates the served site (`dist/`) via `compile/build_site.py`.
```

with:

```markdown
4. writes `compile/refresh-status.json` — the fail-loud freshness banner the served site shows,
5. **rewrites the generated stats block in `index.md`** (article count + per-tier breakdown, between the `stats:begin`/`stats:end` markers) and its frontmatter `article_count` — the durable, committed stat surface,
6. regenerates the served site (`dist/`) via `compile/build_site.py`.
```

- [ ] **Step 2: Add an explicit on-demand note**

In `compile/REBUILD.md`, immediately after the line:

```markdown
It does **not** call an LLM, **not** commit, **not** push. Run it by hand anytime ("rebuild now"):
```

(which is followed by the fenced `python3 compile/refresh.py` block), append a new paragraph after that fenced block:

```markdown
**On-demand "update the table now" is the same command.** `refresh.py` is both the nightly cron job and the on-demand path: it recomputes the stats from `wiki/` ground truth and rewrites the `index.md` block idempotently — running it twice with no corpus change leaves no diff. It never commits; review the `index.md` diff and commit it yourself.
```

- [ ] **Step 3: Commit**

```bash
git add compile/REBUILD.md
git commit -m "docs(compile): document on-demand stats refresh and the index.md block

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Final acceptance checklist

- [ ] `python3 compile/test_stats.py` → `all 6 stats tests passed`.
- [ ] `python3 compile/refresh.py` exits 0 and prints `... index.md unchanged` on a clean corpus.
- [ ] `git diff --quiet index.md` after a refresh → no diff (idempotent).
- [ ] Removing a marker makes `refresh.py` exit 1 **without modifying `index.md`** (`write_index_block` raises before it writes; only the gitignored `refresh-status.json`/snapshot update — verified in Task 4 Step 5).
- [ ] `index.md` human rows (`last_compiled`, `run`, `completeness`) are unchanged by refresh.
- [ ] No `git` command runs inside `refresh.py`; the working-tree diff is left for the human to commit.
- [ ] The five commits are on the current branch (not `main`); nothing is pushed.
