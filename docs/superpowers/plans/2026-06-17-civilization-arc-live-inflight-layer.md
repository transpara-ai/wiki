# Civilization Arc — Live Cross-Thread In-Flight Layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Show in-flight work by any actor (Codex, Claude, Michael) happening outside a given chat — open PRs + recently-merged PRs across the dark-factory stack — live on the Civilization Arc, with a group-by toggle (incl. group-by-actor), refreshing on a tight cron without a full article rebuild.

**Architecture:** Approach B (decoupled live layer). A new `compile/inflight.py` (modeled on `compile/refresh.py`) shells the `gh` CLI to collect PRs and writes a small `dist/inflight.json`. The arc page renders the baked-in reconstructed history immediately, then fetches `inflight.json`, runs it through `CivOntology.validateItems`, and overlays the live `provenance:"derived"` items at the sequence frontier. A new grouping toolbar lets the viewer decompose the same chronological axis into lanes by `tracks | status | repo | sprint | gate | actor`. Fail-loud: any fetch/validate failure keeps the baked snapshot and warns; it never blanks or corrupts the view.

**Tech Stack:** Python 3 stdlib + `gh` CLI (auth from the user's environment, never embedded). Browser JS in the existing ES5-style IIFE assets (`compile/assets/*.js`). Tests: `node:test` (unit) + `jsdom` (DOM smoke) + `unittest` (python). No new runtime dependencies.

## Global Constraints

- **No secrets in code or output.** `gh` uses the user's existing auth; `inflight.json` carries only PR metadata (number, title, author login, url, state). No token is ever written to `inflight.json` or shipped to the browser.
- **Fail-closed / fail-loud.** Unreadable/invalid live data → discard ALL live items, keep the baked snapshot, `console.warn`. The permissive (overlay) outcome is the explicitly-proven branch; the fallback is the default.
- **No commit/push/merge from the refresh path.** `inflight.py` only writes local working files, exactly like `refresh.py`.
- **Purity of merge.** `mergeInflight` MUST NOT mutate `window.CIVILIZATION_ARC_DATA.items` (the baked 109-item array). It returns a new combined array. (The dom-smoke test pins `items.length === 109` + `code` uniqueness.)
- **Default grouping is `"tracks"`.** The dom-smoke test pins exactly 3 track bands / 3 labels / ≥4 gate sub-rows in the default view; the toggle ADDS modes, it never changes the default.
- **Asset style:** ES5 `var`, IIFE, dual Node/browser export as in `civilizationOntology.js`. No ES modules, no new npm deps.
- **Temporal invariant:** every item with `seq < deriveNow` must be `done`/`active`. Live items are settled (`active`/`done`) and placed at the frontier; the merge must keep the combined set passing `validateItems`.

---

## Decisions

1. **Actor facet (DECIDED: build the toggle).** Add a real group-by toggle to the tracks renderer with dimensions `tracks | status | repo | sprint | gate | actor`. `tracks` (default) keeps the shipped 3 type-tracks; the others decompose lanes via `O.groupBy(items, dim)` sharing the one chronological seq axis. Live PRs carry `author`, so `actor` lanes split by who's working (baked history collapses into one `(unknown)` lane). `buildLayout` change (Task 4) + nav toolbar (Task 5).
2. **Sprint for live items:** `sprint: "stewardship"` (existing vocab id → passes `validateItems`, resolves the tooltip's sprint label, adds no new axis tick).
3. **Dedup vs baked N1–N7 worklist:** none in v1. Live PRs are their own `pr-<repo>-<number>` items; ids/codes can't collide with `N5`/`ORIGIN`.
4. **Merged window:** PRs merged in the last **30 days**. Open PRs: all.

---

## File Structure

- **Create** `compile/inflight.py` — collect PRs via `gh`, transform to derived items, write `dist/inflight.json` with a fail-loud freshness stamp. Pure transform `pr_to_item()` isolated from the `gh` shell-out.
- **Create** `compile/test_inflight.py` — unit-test `pr_to_item()` + `collect_items()` against fixtures (no network).
- **Modify** `compile/assets/civilizationOntology.js` — add pure `mergeInflight(data, inflight)` + `actorOf(it)` + extend `laneOf` with an `actor` case; export both.
- **Modify** `tests/ontology.test.js` — unit tests for `mergeInflight` + `laneOf` actor.
- **Modify** `compile/assets/civilizationArcLayout.js` — `buildLayout` accepts `opts.groupBy`; default `"tracks"` unchanged, else lanes from `O.groupBy(items, dim)`.
- **Modify** `tests/arcLayout.test.js` — groupBy tests (default unchanged; status/actor lanes; item conservation; shared `nowX`).
- **Modify** `compile/assets/civilizationArcNav.js` — (Task 5) grouping toolbar UI + `groupBy` state; `render()` stashes current `data`/`byId` so every re-render trigger acts on current data; (Task 6) `loadInflight` fetch glue in `boot()`; author tooltip line; "live · updated N min ago" chip.
- **Modify** `tests/arc-dom-smoke.test.js` — DOM tests for the toolbar (Task 5) + the live overlay (Task 6).
- **Create** `compile/INFLIGHT.md` — ops doc: cron cadence, `gh` auth/security note, what `inflight.json` contains.
- **Verify** `.gitignore` ignores `dist/`; `package.json` runs the new tests in `verify`.

---

### Task 1: `pr_to_item()` pure transform + fixture tests

**Files:**
- Create: `compile/inflight.py`
- Test: `compile/test_inflight.py`

**Interfaces:**
- Produces: `pr_to_item(pr: dict, repo: str) -> dict` where `pr` is a `gh pr list --json` row with keys `number, title, author{login}, url, state, isDraft`. Returns a derived item dict with keys `id, code, type, label, status, blocked, provenance, repo, sprint, href, author, note` (NO `seq` — the browser assigns it at merge time).

- [ ] **Step 1: Write the failing test**

```python
# compile/test_inflight.py
import importlib.util, pathlib, unittest

spec = importlib.util.spec_from_file_location(
    "inflight", pathlib.Path(__file__).resolve().parents[1] / "compile" / "inflight.py")
inflight = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inflight)


class PrToItem(unittest.TestCase):
    def test_open_pr_maps_to_active_derived_work(self):
        pr = {"number": 123, "title": "fix: harden gate", "author": {"login": "msaucier"},
              "url": "https://github.com/transpara-ai/hive/pull/123", "state": "OPEN", "isDraft": False}
        it = inflight.pr_to_item(pr, "hive")
        self.assertEqual(it["id"], "pr-hive-123")
        self.assertEqual(it["code"], "hive#123")
        self.assertEqual(it["type"], "work")
        self.assertEqual(it["status"], "active")
        self.assertEqual(it["blocked"], False)
        self.assertEqual(it["provenance"], "derived")
        self.assertEqual(it["repo"], ["hive"])
        self.assertEqual(it["sprint"], "stewardship")
        self.assertEqual(it["href"], "https://github.com/transpara-ai/hive/pull/123")
        self.assertEqual(it["author"], "msaucier")
        self.assertNotIn("seq", it)

    def test_draft_pr_is_blocked(self):
        pr = {"number": 4, "title": "wip", "author": {"login": "a"},
              "url": "https://github.com/transpara-ai/site/pull/4", "state": "OPEN", "isDraft": True}
        self.assertEqual(inflight.pr_to_item(pr, "site")["blocked"], True)

    def test_merged_pr_maps_to_done(self):
        pr = {"number": 9, "title": "ship it", "author": {"login": "b"},
              "url": "https://github.com/transpara-ai/docs/pull/9", "state": "MERGED", "isDraft": False}
        it = inflight.pr_to_item(pr, "docs")
        self.assertEqual(it["status"], "done")
        self.assertEqual(it["blocked"], False)

    def test_missing_author_login_falls_back_to_unknown(self):
        pr = {"number": 1, "title": "t", "author": None,
              "url": "https://github.com/transpara-ai/work/pull/1", "state": "OPEN", "isDraft": False}
        self.assertEqual(inflight.pr_to_item(pr, "work")["author"], "unknown")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 compile/test_inflight.py`
Expected: FAIL — `ModuleNotFoundError`/`AttributeError: module 'inflight' has no attribute 'pr_to_item'`

- [ ] **Step 3: Write minimal implementation**

```python
#!/usr/bin/env python3
"""Live in-flight layer for the Civilization Arc.

Collects open + recently-merged PRs across the dark-factory stack (+ civilization-wiki)
via the `gh` CLI and writes dist/inflight.json — the live overlay the arc page fetches.

Honors the standing rules, exactly like compile/refresh.py:
  * No git commit/push/merge. Only writes local working files (dist/inflight.json).
  * No secrets: `gh` uses the user's existing auth; the token is NEVER written to
    inflight.json or shipped to the browser. inflight.json carries only PR metadata
    (number, title, author login, url, state).
  * Fail-loud: a gh failure for a repo is recorded, never silently treated as "no work".
"""
import json
import subprocess
import pathlib
import datetime

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "dist" / "inflight.json"
MERGED_WINDOW_DAYS = 30
# Live items join the ongoing "stewardship" sprint (existing vocab → passes validateItems,
# resolves the tooltip sprint label, adds no new axis tick).
LIVE_SPRINT = "stewardship"


def pr_to_item(pr, repo):
    """Pure: one `gh pr list --json` row -> one derived arc item (no seq; browser assigns)."""
    state = (pr.get("state") or "").upper()
    status = "done" if state == "MERGED" else "active"
    author = ((pr.get("author") or {}).get("login")) or "unknown"
    number = pr.get("number")
    return {
        "id": "pr-%s-%s" % (repo, number),
        "code": "%s#%s" % (repo, number),
        "type": "work",
        "label": pr.get("title") or ("%s#%s" % (repo, number)),
        "status": status,
        "blocked": bool(pr.get("isDraft")) and status == "active",
        "provenance": "derived",
        "repo": [repo],
        "sprint": LIVE_SPRINT,
        "href": pr.get("url") or "",
        "author": author,
        "note": ("%s · @%s" % (state.lower() or "open", author)),
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 compile/test_inflight.py`
Expected: PASS (4 tests)

- [ ] **Step 5: Commit**

```bash
git add compile/inflight.py compile/test_inflight.py
git commit -m "feat(arc): pr_to_item pure transform for the live in-flight layer"
```

---

### Task 2: `inflight.py` collection + write (gh shell-out, fail-loud stamp)

**Files:**
- Modify: `compile/inflight.py`
- Test: `compile/test_inflight.py`

**Interfaces:**
- Consumes: `pr_to_item()` from Task 1.
- Produces: `gh_json(args) -> list`, `resolve_repos() -> list[str]`, `collect_items(repos) -> (list[dict], list[str])` (items, errors), `main()` writing `dist/inflight.json` as `{"generated","window_days","repos","errors","items"}`. `gh_json` is monkeypatchable (module-level function) so tests need no network.

- [ ] **Step 1: Write the failing test** (append to `compile/test_inflight.py`)

```python
class CollectAndShape(unittest.TestCase):
    def test_collect_items_records_repo_errors_without_dropping_good_repos(self):
        def fake_gh_json(args):
            if "broken" in " ".join(args):
                raise RuntimeError("gh: not found")
            return [{"number": 1, "title": "t", "author": {"login": "x"},
                     "url": "https://github.com/transpara-ai/hive/pull/1",
                     "state": "OPEN", "isDraft": False}]
        orig = inflight.gh_json
        inflight.gh_json = fake_gh_json
        try:
            items, errors = inflight.collect_items(["hive", "broken"])
        finally:
            inflight.gh_json = orig
        self.assertTrue(any(i["id"] == "pr-hive-1" for i in items))
        self.assertTrue(any("broken" in e for e in errors))

    def test_items_dedup_by_id(self):
        rows = [{"number": 2, "title": "t", "author": {"login": "x"},
                 "url": "u", "state": "OPEN", "isDraft": False}]
        orig = inflight.gh_json
        inflight.gh_json = lambda args: rows
        try:
            items, _ = inflight.collect_items(["hive"])
        finally:
            inflight.gh_json = orig
        ids = [i["id"] for i in items]
        self.assertEqual(len(ids), len(set(ids)))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 compile/test_inflight.py`
Expected: FAIL — `AttributeError: module 'inflight' has no attribute 'gh_json'`

- [ ] **Step 3: Write minimal implementation** (append to `compile/inflight.py`)

```python
def gh_json(args):
    """Run `gh ... --json ...` and parse stdout. Raises on non-zero exit (fail-loud)."""
    p = subprocess.run(["gh"] + args, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("gh %s failed: %s" % (" ".join(args), (p.stderr or "").strip()))
    return json.loads(p.stdout or "[]")


def resolve_repos():
    """Live dark-factory set (+ civilization-wiki), resolved from the GitHub topic — never hardcoded."""
    rows = gh_json(["repo", "list", "transpara-ai", "--no-archived", "--limit", "200",
                    "--json", "name,repositoryTopics"])
    repos = set()
    for r in rows:
        topics = [t.get("name") for t in (r.get("repositoryTopics") or [])]
        if "dark-factory" in topics:
            repos.add(r["name"])
    repos.add("civilization-wiki")
    return sorted(repos)


_FIELDS = "number,title,author,url,state,isDraft"


def collect_items(repos):
    items_by_id, errors = {}, []
    since = (datetime.date.today() - datetime.timedelta(days=MERGED_WINDOW_DAYS)).isoformat()
    for repo in repos:
        slug = "transpara-ai/%s" % repo
        try:
            rows = gh_json(["pr", "list", "--repo", slug, "--state", "open",
                            "--json", _FIELDS, "--limit", "100"])
            rows += gh_json(["pr", "list", "--repo", slug, "--state", "merged",
                             "--search", "merged:>=%s" % since,
                             "--json", _FIELDS, "--limit", "100"])
        except Exception as e:  # one bad repo never zeroes the whole overlay
            errors.append("%s: %s" % (repo, e))
            continue
        for pr in rows:
            it = pr_to_item(pr, repo)
            items_by_id[it["id"]] = it
    return list(items_by_id.values()), errors


def main():
    try:
        repos = resolve_repos()
        repo_err = []
    except Exception as e:
        repos, repo_err = ["civilization-wiki"], ["resolve_repos: %s" % e]
    items, errors = collect_items(repos)
    errors = repo_err + errors
    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "window_days": MERGED_WINDOW_DAYS,
        "repos": repos,
        "errors": errors,
        "items": items,
    }
    OUT.write_text(json.dumps(payload, indent=2))
    print("inflight: %d live items across %d repos, %d errors -> %s"
          % (len(items), len(repos), len(errors), OUT))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 compile/test_inflight.py`
Expected: PASS (6 tests)

- [ ] **Step 5: Commit**

```bash
git add compile/inflight.py compile/test_inflight.py
git commit -m "feat(arc): inflight.py collects open+merged PRs to dist/inflight.json (fail-loud)"
```

---

### Task 3: `mergeInflight` + `actorOf` + `laneOf` actor in the ontology contract

**Files:**
- Modify: `compile/assets/civilizationOntology.js`
- Test: `tests/ontology.test.js`

**Interfaces:**
- Consumes: existing `deriveNow`, `validateItems`.
- Produces:
  - `mergeInflight(data, inflight) -> { ok: bool, items: array, generated: string|null, errors: array }`. Pure: does not mutate `data.items`. Assigns each live item a `seq` in the open interval `(now0, nextSeq)` where `now0 = deriveNow(data.items)` and `nextSeq = min baked seq > now0` (or `data.domain.end`). On any `validateItems` failure OR live/baked `code` collision → `{ ok:false, items: data.items, errors }`.
  - `actorOf(it) -> string` = `it.author || "(unknown)"`; `laneOf(it,"actor")` returns it.
  - Both added to the exported `api`.

- [ ] **Step 1: Write the failing test** (append to `tests/ontology.test.js`)

```javascript
// --- Live in-flight overlay (mergeInflight) ---
const BAKED = {
  domain: { start: 0, end: 15 },
  items: [
    { id: 'h1',  code: 'H1',  type: 'work', status: 'done',    provenance: 'reconstructed', seq: 1,    sprint: 'origin',     repo: ['civilization-wiki'] },
    { id: 'now', code: 'NOW', type: 'gate', status: 'active',  provenance: 'reconstructed', seq: 13.9, sprint: 'deployment', repo: ['docs'] },
    { id: 'p1',  code: 'P1',  type: 'work', status: 'planned', provenance: 'derived',       seq: 14.0, sprint: 'deployment', repo: ['site'] },
    { id: 'f1',  code: 'F1',  type: 'work', status: 'future',  provenance: 'derived',       seq: 15.0, sprint: 'stewardship', repo: ['site'] },
  ],
};
function liveItem(over) {
  return Object.assign({ id: 'pr-hive-1', code: 'hive#1', type: 'work', status: 'active',
    blocked: false, provenance: 'derived', repo: ['hive'], sprint: 'stewardship',
    href: 'https://github.com/transpara-ai/hive/pull/1', author: 'x', note: 'open · @x' }, over || {});
}

test('mergeInflight overlays a live item at the frontier and stays valid', () => {
  const r = O.mergeInflight(BAKED, { generated: '2026-06-17 14:00', items: [liveItem()] });
  assert.strictEqual(r.ok, true, r.errors.join('\n'));
  assert.strictEqual(r.items.length, 5);
  const live = r.items.find(i => i.id === 'pr-hive-1');
  assert.ok(live.seq > 13.9 && live.seq < 14.0, 'live seq must land in the (now, nextSeq) gap, got ' + live.seq);
  assert.strictEqual(O.validateItems(r.items).ok, true);
});

test('mergeInflight is PURE — never mutates the baked items array', () => {
  const before = BAKED.items.length;
  O.mergeInflight(BAKED, { generated: 'g', items: [liveItem(), liveItem({ id: 'pr-hive-2', code: 'hive#2' })] });
  assert.strictEqual(BAKED.items.length, before, 'baked items length changed');
  assert.ok(!BAKED.items.some(i => i.id === 'pr-hive-1'), 'baked array was mutated');
});

test('mergeInflight FALLS BACK to baked when a live item is invalid', () => {
  const r = O.mergeInflight(BAKED, { generated: 'g', items: [liveItem({ status: 'merged' })] }); // merged ∉ STATUS_ORDER
  assert.strictEqual(r.ok, false);
  assert.strictEqual(r.items.length, BAKED.items.length);
  assert.ok(r.items.every(i => i.id !== 'pr-hive-1'), 'no live item leaked on fallback');
});

test('mergeInflight FALLS BACK on a code collision with baked', () => {
  const r = O.mergeInflight(BAKED, { generated: 'g', items: [liveItem({ code: 'NOW' })] });
  assert.strictEqual(r.ok, false);
});

test('mergeInflight with no live items returns baked + generated, still ok', () => {
  const r = O.mergeInflight(BAKED, { generated: 'g', items: [] });
  assert.strictEqual(r.ok, true);
  assert.strictEqual(r.items.length, BAKED.items.length);
  assert.strictEqual(r.generated, 'g');
});

test('laneOf actor groups by author; missing author → (unknown)', () => {
  assert.strictEqual(
    O.groupBy([liveItem(), { id: 'b', author: null }], 'actor').map(l => l.lane).sort().join(','),
    '(unknown),x');
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/ontology.test.js`
Expected: FAIL — `O.mergeInflight is not a function`

- [ ] **Step 3: Write minimal implementation** (add inside the IIFE in `civilizationOntology.js`, before `var api = {...}`)

```javascript
  // actor facet: who is doing the work (live PR author). Baked items have no author.
  function actorOf(it) { return (it && it.author) || "(unknown)"; }

  // Pure overlay of live "derived" items onto the baked set. Assigns each live
  // item a seq in the open interval (now0, nextSeq) — at the frontier, below the
  // first roadmap step — so the combined set keeps the temporal invariant.
  // Fail-closed: invalid combined set OR a code collision → keep baked, never overlay.
  function mergeInflight(data, inflight) {
    var baked = (data && data.items) || [];
    var generated = (inflight && inflight.generated) || null;
    var live = (inflight && inflight.items) || [];
    if (!live.length) return { ok: true, items: baked, generated: generated, errors: [] };

    var now0 = deriveNow(baked);
    var domainEnd = (data && data.domain && typeof data.domain.end === "number") ? data.domain.end : now0 + 1;
    var nextSeq = domainEnd;
    for (var i = 0; i < baked.length; i++) {
      if (baked[i] && typeof baked[i].seq === "number" && baked[i].seq > now0 && baked[i].seq < nextSeq) {
        nextSeq = baked[i].seq;
      }
    }
    if (!(nextSeq > now0)) nextSeq = now0 + 1;

    var codes = {};
    baked.forEach(function (it) { if (it && it.code != null) codes[it.code] = true; });

    // Deterministic order (sort by id) so seq assignment is stable across runs.
    var sorted = live.slice().sort(function (a, b) {
      return String(a && a.id).localeCompare(String(b && b.id));
    });
    var n = sorted.length;
    var placed = [];
    var collision = false;
    for (var k = 0; k < n; k++) {
      var src = sorted[k];
      if (src && src.code != null && codes[src.code]) collision = true;
      var copy = {};
      for (var key in src) { if (Object.prototype.hasOwnProperty.call(src, key)) copy[key] = src[key]; }
      copy.seq = now0 + (nextSeq - now0) * (k + 1) / (n + 1);
      placed.push(copy);
    }

    var combined = baked.concat(placed);
    var res = validateItems(combined);
    if (!res.ok || collision) {
      var errs = res.errors.slice();
      if (collision) errs.push("live code collides with a baked item code");
      return { ok: false, items: baked, generated: generated, errors: errs };
    }
    return { ok: true, items: combined, generated: generated, errors: [] };
  }
```

Extend `laneOf` (add immediately before its final `return "(none)";`):

```javascript
    if (dim === "actor") return actorOf(it);
```

Extend the `api` object (add the two new members):

```javascript
    groupBy: groupBy, visibleDeps: visibleDeps, actorOf: actorOf, mergeInflight: mergeInflight,
```

- [ ] **Step 4: Run test to verify it passes**

Run: `node --test tests/ontology.test.js`
Expected: PASS (all, incl. 6 new)

- [ ] **Step 5: Commit**

```bash
git add compile/assets/civilizationOntology.js tests/ontology.test.js
git commit -m "feat(arc): mergeInflight pure overlay + actor facet in the ontology contract"
```

---

### Task 4: `buildLayout` group-by support (lanes share the seq axis)

**Files:**
- Modify: `compile/assets/civilizationArcLayout.js`
- Test: `tests/arcLayout.test.js`

**Interfaces:**
- Consumes: `O.groupBy` (incl. the new `actor` dim from Task 3).
- Produces: `buildLayout(data, opts)` reads `opts.groupBy` (string). `"tracks"`/falsy → the existing 3 type-tracks (UNCHANGED). Any other dim → one track per `O.groupBy(items, dim)` lane, each a single unlabeled row, items placed at `x = sx(seq)` on the SAME shared scale. Return shape unchanged.

- [ ] **Step 1: Write the failing test** (append to `tests/arcLayout.test.js`)

```javascript
test('buildLayout default groupBy stays the 3 type tracks (unchanged)', () => {
  const lay = L.buildLayout(loadData(), { width: 1600, groupBy: 'tracks' });
  assert.deepStrictEqual(lay.tracks.map(t => t.id), ['construction', 'gates', 'worklist']);
});

test('buildLayout groupBy="status" lanes follow band order and place every item once', () => {
  const data = loadData();
  const lay = L.buildLayout(data, { width: 1600, groupBy: 'status' });
  const labels = lay.tracks.map(t => t.label);
  assert.strictEqual(labels[0], 'done', 'done band leads; got ' + labels.join(' | '));
  const placed = lay.tracks.reduce((n, t) => n + t.rows.reduce((m, r) => m + r.items.length, 0), 0);
  assert.strictEqual(placed, data.items.length, 'every item placed exactly once across status lanes');
});

test('buildLayout groupBy="actor" splits authors into lanes sharing the seq axis', () => {
  const data = loadData();
  const live = [
    { id: 'pr-a', code: 'PRA', type: 'work', status: 'active', blocked: false, provenance: 'derived', seq: 13.95, sprint: 'stewardship', repo: ['hive'], author: 'alice' },
    { id: 'pr-b', code: 'PRB', type: 'work', status: 'active', blocked: false, provenance: 'derived', seq: 13.97, sprint: 'stewardship', repo: ['site'], author: 'bob' },
  ];
  const testData = Object.assign({}, data, { items: data.items.concat(live) });
  const lay = L.buildLayout(testData, { width: 1600, groupBy: 'actor' });
  const labels = lay.tracks.map(t => t.label);
  assert.ok(labels.includes('alice') && labels.includes('bob'), 'author lanes present; got ' + labels.join(' | '));
  assert.ok(labels.includes('(unknown)'), 'baked items (no author) collapse into (unknown)');
  // Shared chronological axis: nowX identical to the default view for the same data.
  const base = L.buildLayout(testData, { width: 1600 });
  assert.strictEqual(lay.nowX, base.nowX);
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/arcLayout.test.js`
Expected: FAIL — status/actor lanes not produced (default tracks always returned)

- [ ] **Step 3: Write minimal implementation**

In `civilizationArcLayout.js`, replace the block that builds `beats/decisions/goal/gates/work` and `var defs = [...]` (the lines from `var beats = items.filter(...)` through the close of the `var defs = [ ... ];` array) with:

```javascript
    var groupBy = opts.groupBy || "tracks";
    var defs;
    if (groupBy === "tracks") {
      var beats = items.filter(function (i) { return i.type === "work" && i.provenance === "reconstructed"; });
      var decisions = items.filter(function (i) { return i.type === "decision"; });
      var goal = items.filter(function (i) { return i.type === "goal"; });
      var gates = items.filter(function (i) { return i.type === "gate"; });
      var work = items.filter(function (i) { return i.type === "work" && i.provenance === "derived"; });
      // Gate rows from the ontology contract (groupBy "gate" = by family).
      var gateLanes = O.groupBy(gates, "gate");
      defs = [
        { id: "construction", label: "construction arc", rows: [{ id: "beats", label: "", items: beats.concat(decisions, goal) }] },
        { id: "gates", label: "gates", rows: gateLanes.map(function (lane) {
            return { id: "gate:" + lane.lane, label: lane.lane, items: lane.items };
          }) },
        { id: "worklist", label: "worklist", rows: [{ id: "work", label: "", items: work }] },
      ];
    } else {
      // Swimlane mode: one track per contract lane, sharing the chronological seq axis.
      defs = O.groupBy(items, groupBy).map(function (lane) {
        return {
          id: groupBy + ":" + lane.lane,
          label: lane.lane,
          rows: [{ id: groupBy + ":" + lane.lane + ":row", label: "", items: lane.items }],
        };
      });
    }
```

(The `var y = GEOM.top; var tracks = defs.map(...)` placement loop and everything after it stays EXACTLY as-is — it already consumes `defs` generically.)

- [ ] **Step 4: Run test to verify it passes**

Run: `node --test tests/arcLayout.test.js`
Expected: PASS (all, incl. 3 new). Existing track/gate tests still green (default path untouched).

- [ ] **Step 5: Commit**

```bash
git add compile/assets/civilizationArcLayout.js tests/arcLayout.test.js
git commit -m "feat(arc): buildLayout group-by support (status/repo/sprint/gate/actor lanes)"
```

---

### Task 5: Grouping toolbar + current-data render in nav.js

**Files:**
- Modify: `compile/assets/civilizationArcNav.js`
- Test: `tests/arc-dom-smoke.test.js`

**Interfaces:**
- Consumes: `buildLayout(..., {groupBy})` from Task 4.
- Produces: a `.arc-toolbar` with six `[data-arc-group]` buttons (`tracks|status|repo|sprint|gate|actor`); `root._arc.groupBy` (default `"tracks"`); `render()` stashes `s.data` + `s.byId` so EVERY re-render trigger (markers, collapse, resize, toolbar) acts on the current data — this is what later lets the live overlay's markers be interactive. Default view unchanged.

- [ ] **Step 1: Write the failing test** (append to `tests/arc-dom-smoke.test.js`)

```javascript
test('grouping toolbar: six group buttons render, Tracks active by default', () => {
  const { nav } = mountArc();
  const btns = [...nav.querySelectorAll('[data-arc-group]')];
  assert.deepStrictEqual(btns.map(b => b.getAttribute('data-arc-group')),
    ['tracks', 'status', 'repo', 'sprint', 'gate', 'actor']);
  assert.strictEqual(nav.querySelector('.arc-group-btn-active').getAttribute('data-arc-group'), 'tracks');
  assert.strictEqual(nav.querySelectorAll('.arc-track-band').length, 3); // default unchanged
});

test('clicking "Status" regroups the lanes and marks the button active', () => {
  const { nav, dom } = mountArc();
  nav.querySelector('[data-arc-group="status"]').dispatchEvent(new dom.window.MouseEvent('click', { bubbles: true }));
  const labels = [...nav.querySelectorAll('.arc-track-label')].map(t => t.textContent);
  assert.ok(labels.includes('done') && labels.includes('planned'), 'status lanes present; got ' + labels.join(' | '));
  assert.strictEqual(nav.querySelector('.arc-group-btn-active').getAttribute('data-arc-group'), 'status');
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node tests/arc-dom-smoke.test.js`
Expected: FAIL — no `[data-arc-group]` buttons

- [ ] **Step 3: Write minimal implementation**

(a) After `var BASE_WIDTH = 1680;` add the grouping vocabulary:

```javascript
  var GROUPINGS = [
    { id: "tracks", label: "Tracks" },
    { id: "status", label: "Status" },
    { id: "repo", label: "Repo" },
    { id: "sprint", label: "Sprint" },
    { id: "gate", label: "Gate" },
    { id: "actor", label: "Actor" },
  ];
```

(b) In `ensureScaffold`, change the state initializer to seed `groupBy`, extend the early-return guard to require the toolbar, build the toolbar, and append it before the frame. Replace:

```javascript
    root._arc = root._arc || { collapsed: {}, selectedId: null };
    var s = root._arc;
    if (s.scaffolded && s.frame && s.svg && s.nowPanel && s.detailPanel && s.tooltip) {
      return s;
    }
```

with:

```javascript
    root._arc = root._arc || { collapsed: {}, selectedId: null, groupBy: "tracks" };
    var s = root._arc;
    if (s.scaffolded && s.frame && s.svg && s.nowPanel && s.detailPanel && s.tooltip && s.toolbar) {
      return s;
    }
```

Then replace `root.append(frame, panels);` with:

```javascript
    var toolbar = htmlEl("div", "arc-toolbar");
    toolbar.setAttribute("role", "group");
    toolbar.setAttribute("aria-label", "Group the arc by");
    GROUPINGS.forEach(function (g) {
      var btn = htmlEl("button", "arc-group-btn", g.label);
      btn.setAttribute("type", "button");
      btn.setAttribute("data-arc-group", g.id);
      toolbar.appendChild(btn);
    });

    root.append(toolbar, frame, panels);
```

and add `s.toolbar = toolbar;` alongside the other `s.* =` assignments at the end of `ensureScaffold`.

(c) Add an `updateToolbar` helper (e.g. just below `ensureScaffold`):

```javascript
  function updateToolbar(s) {
    if (!s || !s.toolbar) return;
    var cur = s.groupBy || "tracks";
    var btns = s.toolbar.querySelectorAll("[data-arc-group]");
    Array.prototype.forEach.call(btns, function (b) {
      var on = b.getAttribute("data-arc-group") === cur;
      b.classList.toggle("arc-group-btn-active", on);
      b.setAttribute("aria-pressed", on ? "true" : "false");
    });
  }
```

(d) Replace the whole `render` function with this version (stashes `s.data`/`s.byId`; passes `groupBy`; resize uses `s.data`; calls `updateToolbar`):

```javascript
  function render(root, data) {
    if (!root || !data) return;
    var Layout = lib("CivArcLayout");
    var Draw = lib("CivArcDraw");
    if (!Layout || !Layout.buildLayout || !Draw) return;

    var s = ensureScaffold(root);
    s.data = data;                 // current data (baked, or merged-with-live overlay)
    s.byId = indexItems(data);     // re-index each render so live markers stay interactive

    if (!s.ordinalById) {
      s.ordinalById = {};
      s.sprintLabelById = {};
      var sorted = ((data.items) || []).slice().sort(function (a, b) {
        return (a.seq || 0) - (b.seq || 0);
      });
      for (var oi = 0; oi < sorted.length; oi++) {
        if (sorted[oi].id != null) s.ordinalById[sorted[oi].id] = oi + 1;
      }
      s.itemCount = sorted.length;
      ((data.sprints) || []).forEach(function (sp) {
        if (sp && sp.id != null) s.sprintLabelById[sp.id] = sp.label;
      });
    }

    if (typeof ResizeObserver !== "undefined" && !s.resizeObserver) {
      s.lastWidth = Math.round(s.frame.getBoundingClientRect().width) || 0;
      s.resizeObserver = new ResizeObserver(function () {
        var w = Math.round(s.frame.getBoundingClientRect().width);
        if (!w || Math.abs(w - s.lastWidth) < 2) return;
        s.lastWidth = w;
        if (s.raf && typeof cancelAnimationFrame !== "undefined") cancelAnimationFrame(s.raf);
        var schedule = (typeof requestAnimationFrame !== "undefined")
          ? requestAnimationFrame : function (fn) { return setTimeout(fn, 16); };
        s.raf = schedule(function () { render(root, s.data); });
      });
      s.resizeObserver.observe(s.frame);
    }

    root.setAttribute("data-has-selection", s.selectedId != null ? "true" : "false");

    var width = Math.round(s.frame.getBoundingClientRect().width) || BASE_WIDTH;
    var layout = Layout.buildLayout(data, { width: width, collapsed: s.collapsed, groupBy: s.groupBy || "tracks" });

    var svg = s.svg;
    svg.setAttribute("viewBox", "0 0 " + layout.contentWidth + " " + layout.contentHeight);
    svg.style.width = layout.contentWidth + "px";
    svg.style.height = layout.contentHeight + "px";
    clearNode(svg);

    Draw.drawAxis(svg, layout);
    Draw.drawTracks(svg, layout, s);
    Draw.drawMarkers(svg, layout, s);

    if (s.selectedId != null) {
      var sel = svg.querySelector('[data-arc-item="' + cssEscape(s.selectedId) + '"]');
      if (sel) {
        sel.setAttribute("aria-pressed", "true");
        var grp = sel.closest ? sel.closest(".arc-item-group") : null;
        if (grp) grp.classList.add("arc-is-selected");
      }
    }

    updateToolbar(s);
    renderNowPanel(root, data);
    renderDetailPanel(root, data);

    wireEvents(root, data);
  }
```

(e) Replace the whole `wireEvents` function with this version (uses `s.byId`/`s.data`; wires the toolbar):

```javascript
  function wireEvents(root, data) {
    var s = root._arc;
    if (s.wired) return;
    var svg = s.svg;

    function itemFromEvent(event) {
      var node = closestArcItem(event.target);
      if (!node) return null;
      var id = node.getAttribute("data-arc-item");
      return id != null ? s.byId[id] : null;
    }

    svg.addEventListener("mouseover", function (event) {
      var item = itemFromEvent(event);
      if (item) showTooltip(root, item, event);
    });
    svg.addEventListener("mousemove", function (event) {
      if (s.tooltip && !s.tooltip.hidden && closestArcItem(event.target)) {
        positionTooltip(root, s.tooltip, event);
      }
    });
    svg.addEventListener("mouseout", function () { hideTooltip(root); });
    svg.addEventListener("focusin", function (event) {
      var item = itemFromEvent(event);
      if (item) showTooltip(root, item, event);
    });
    svg.addEventListener("focusout", function () { hideTooltip(root); });

    svg.addEventListener("click", function (event) {
      var collapse = closestArcCollapse(event.target);
      if (collapse) {
        var trackId = collapse.getAttribute("data-arc-collapse");
        if (trackId != null) { s.collapsed[trackId] = !s.collapsed[trackId]; render(root, s.data); }
        return;
      }
      var node = closestArcItem(event.target);
      if (node) { s.selectedId = node.getAttribute("data-arc-item"); render(root, s.data); return; }
      if (s.selectedId != null) { s.selectedId = null; render(root, s.data); }
    });

    svg.addEventListener("keydown", function (event) {
      if (event.key !== "Enter" && event.key !== " " && event.key !== "Spacebar") return;
      var node = closestArcItem(event.target);
      if (!node) return;
      event.preventDefault();
      var collapse = closestArcCollapse(node);
      if (collapse) {
        var trackId = collapse.getAttribute("data-arc-collapse");
        if (trackId != null) { s.collapsed[trackId] = !s.collapsed[trackId]; render(root, s.data); }
        return;
      }
      s.selectedId = node.getAttribute("data-arc-item");
      render(root, s.data);
    });

    // Grouping toolbar: switch the lane decomposition; re-render with current data.
    if (s.toolbar) {
      s.toolbar.addEventListener("click", function (event) {
        var btn = (event.target && event.target.closest) ? event.target.closest("[data-arc-group]") : null;
        if (!btn) return;
        var dim = btn.getAttribute("data-arc-group") || "tracks";
        if (dim === (s.groupBy || "tracks")) return;
        s.groupBy = dim;
        render(root, s.data);
      });
    }

    s.wired = true;
  }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `node tests/arc-dom-smoke.test.js && node --test tests/arcLayout.test.js`
Expected: PASS, incl. the 2 new toolbar tests; the baseline smoke (`109 items`, 3 bands, tooltip `step N of 109`) still passes.

- [ ] **Step 5: Commit**

```bash
git add compile/assets/civilizationArcNav.js tests/arc-dom-smoke.test.js
git commit -m "feat(arc): grouping toolbar (tracks/status/repo/sprint/gate/actor) + current-data render"
```

---

### Task 6: `loadInflight` overlay + freshness chip + author line

**Files:**
- Modify: `compile/assets/civilizationArcNav.js`
- Test: `tests/arc-dom-smoke.test.js`

**Interfaces:**
- Consumes: `CivOntology.mergeInflight` (Task 3); the current-data `render` (Task 5).
- Produces: `boot()` renders baked first then calls `loadInflight(roots, data)`; `loadInflight` fetches `inflight.json`, merges, re-renders with the combined items (resetting the ordinal cache), and shows a `.arc-live-chip`. Author line added to `showTooltip`. Fail-safe: missing `fetch`, a non-ok response, a rejected promise, or a rejected merge all keep the baked render.

- [ ] **Step 1: Write the failing test** (append to `tests/arc-dom-smoke.test.js`)

```javascript
function mountWithFetch(inflightPayload, opts) {
  const dom = new JSDOM('<!doctype html><div data-civilization-arc-nav></div>', {
    pretendToBeVisual: true, runScripts: "outside-only", url: "http://127.0.0.1:8787/index.html",
  });
  dom.window.fetch = function () {
    if (opts && opts.reject) return Promise.reject(new Error("network"));
    return Promise.resolve({ ok: true, json: function () { return Promise.resolve(inflightPayload); } });
  };
  ["civilizationOntology.js", "civilizationArcData.js", "civilizationArcLayout.js",
   "civilizationArcDraw.js", "civilizationArcNav.js"].forEach((f) =>
    dom.window.eval(fs.readFileSync(path.join(root, "compile/assets", f), "utf8")));
  dom.window.document.dispatchEvent(new dom.window.Event("DOMContentLoaded"));
  return dom;
}

const LIVE_PR = {
  generated: "2026-06-17 14:00", window_days: 30, repos: ["hive"], errors: [],
  items: [{ id: "pr-hive-1", code: "hive#1", type: "work", label: "fix: live overlay",
    status: "active", blocked: false, provenance: "derived", repo: ["hive"],
    sprint: "stewardship", href: "https://github.com/transpara-ai/hive/pull/1",
    author: "msaucier", note: "open · @msaucier" }],
};

test('live overlay: stubbed fetch adds the PR marker and a freshness chip', async () => {
  const dom = mountWithFetch(LIVE_PR);
  await new Promise((r) => setTimeout(r, 0));
  const nav = dom.window.document.querySelector(".civilization-arc-nav");
  assert(nav.querySelector('[data-arc-item="pr-hive-1"]'), "live PR marker should render after overlay");
  const chip = nav.querySelector(".arc-live-chip");
  assert(chip && /updated 2026-06-17 14:00/.test(chip.textContent), "chip should show generated time");
});

test('live overlay: the live marker is interactive and shows its author', async () => {
  const dom = mountWithFetch(LIVE_PR);
  await new Promise((r) => setTimeout(r, 0));
  const nav = dom.window.document.querySelector(".civilization-arc-nav");
  const marker = nav.querySelector('[data-arc-item="pr-hive-1"]');
  marker.dispatchEvent(new dom.window.MouseEvent('mouseover', { bubbles: true }));
  const tip = nav.querySelector('.arc-tooltip');
  assert.strictEqual(tip.hidden, false);
  assert.match(tip.textContent, /actor · @msaucier/);
});

test('live overlay FAILS SAFE: a rejected fetch keeps the baked render, no live marker', async () => {
  const dom = mountWithFetch(null, { reject: true });
  await new Promise((r) => setTimeout(r, 0));
  const nav = dom.window.document.querySelector(".civilization-arc-nav");
  assert(!nav.querySelector('[data-arc-item="pr-hive-1"]'), "no live marker on fetch failure");
  assert(nav.querySelectorAll(".arc-item-group").length > 0, "baked render survives");
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node tests/arc-dom-smoke.test.js`
Expected: FAIL — live marker / chip assertions (no `loadInflight` yet)

- [ ] **Step 3: Write minimal implementation**

(a) In `showTooltip`, after the provenance line (`if (item.provenance) ...`), add:

```javascript
    if (item.author) tip.appendChild(htmlEl("div", "arc-tooltip-meta", "actor · @" + item.author));
```

(b) Add a chip helper + `loadInflight`, and replace `boot()`:

```javascript
  function setLiveChip(root, text, ok) {
    var s = root._arc;
    if (!s) return;
    var chip = s.liveChip;
    if (!chip) {
      chip = htmlEl("div", "arc-live-chip");
      s.liveChip = chip;
      (s.frame || root).appendChild(chip);
    }
    chip.classList.toggle("arc-live-chip-warn", !ok);
    chip.textContent = text;
  }

  function loadInflight(roots, data) {
    if (typeof fetch !== "function") return;            // no fetch (SSR/jsdom default) → baked only
    var O = lib("CivOntology");
    if (!O || !O.mergeInflight) return;
    fetch("inflight.json", { cache: "no-store" })
      .then(function (resp) { if (!resp || !resp.ok) throw new Error("inflight HTTP"); return resp.json(); })
      .then(function (inflight) {
        var merged = O.mergeInflight(data, inflight);
        if (!merged.ok) {
          if (typeof console !== "undefined") console.warn("inflight: overlay rejected (fail-closed):", merged.errors);
          Array.prototype.forEach.call(roots, function (root) { setLiveChip(root, "live · unavailable", false); });
          return;
        }
        var liveData = {};
        for (var key in data) { if (Object.prototype.hasOwnProperty.call(data, key)) liveData[key] = data[key]; }
        liveData.items = merged.items;                  // new array — baked data untouched
        Array.prototype.forEach.call(roots, function (root) {
          if (root._arc) root._arc.ordinalById = null;  // recompute ordinals over the merged set
          render(root, liveData);
          setLiveChip(root, "live · updated " + (merged.generated || "?"), true);
        });
      })
      .catch(function (e) {
        if (typeof console !== "undefined") console.warn("inflight: fetch failed (keeping baked):", e && e.message);
        Array.prototype.forEach.call(roots, function (root) { setLiveChip(root, "live · unavailable", false); });
      });
  }

  function boot() {
    var data = (typeof window !== "undefined") ? window.CIVILIZATION_ARC_DATA : null;
    if (!data) return;
    var roots = document.querySelectorAll("[data-civilization-arc-nav]");
    Array.prototype.forEach.call(roots, function (root) { render(root, data); }); // baked first — never blank
    loadInflight(roots, data);                                                    // then overlay live
  }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `node tests/arc-dom-smoke.test.js`
Expected: PASS (incl. the 3 new overlay tests); the baseline `arc DOM smoke ok: 109 items…` line still prints (no-fetch path unchanged).

- [ ] **Step 5: Commit**

```bash
git add compile/assets/civilizationArcNav.js tests/arc-dom-smoke.test.js
git commit -m "feat(arc): loadInflight overlay + freshness chip + author line (fail-safe)"
```

---

### Task 7: Ops doc + serve/ignore wiring + full verify

**Files:**
- Create: `compile/INFLIGHT.md`
- Verify/modify: `.gitignore`, `package.json`

**Interfaces:** none (docs + config).

- [ ] **Step 1: Confirm `dist/` is gitignored (so `dist/inflight.json` is never committed)**

Run: `grep -nE '^/?dist/?$' .gitignore || echo "MISSING"`
Expected: a match. If `MISSING`, append `dist/` to `.gitignore`.

- [ ] **Step 2: Add the Python inflight test to the scripts + verify chain**

In `package.json` `scripts`, add `test:py` and chain it into `verify`:

```json
    "test:py": "python3 compile/test_inflight.py",
    "verify": "npm run build && npm run test:js && npm run test:unit && npm run test:dom && npm run test:py && npm run test:browser"
```

- [ ] **Step 3: Write the ops doc**

```markdown
# compile/INFLIGHT.md — live in-flight overlay

`compile/inflight.py` writes `dist/inflight.json`: open + recently-merged PRs across the
dark-factory stack (+ civilization-wiki), which the arc page fetches and overlays as live
`derived` work at the sequence frontier. The grouping toolbar's **Actor** mode splits that
live work into per-author lanes.

## Run

    python3 compile/inflight.py     # writes dist/inflight.json

Requires the `gh` CLI authenticated as a user who can read the transpara-ai repos.

## Cron (suggested ~10 min cadence)

    */10 * * * *  cd /path/to/civilization-wiki && python3 compile/inflight.py

Decoupled from the article build on purpose: it refreshes fast-moving PR state without
regenerating the articles. `dist/inflight.json` survives a `build_site.py` run.

## Security / rules

- `gh` uses the operator's existing auth. The token is NEVER written to inflight.json or
  shipped to the browser. inflight.json carries only PR metadata (number, title, author
  login, url, state).
- No git commit / push / merge — writes local working files only (like refresh.py).
- Fail-loud: per-repo `gh` errors are recorded in `inflight.json.errors`, never silently
  treated as "no work". The browser overlay is fail-closed: invalid data keeps the baked arc.
```

- [ ] **Step 4: Run the full verification**

Run: `npm run verify`
Expected: build succeeds; `test:js`, `test:unit`, `test:dom`, `test:py`, `test:browser` all PASS; smoke prints `109 items`.

- [ ] **Step 5: Commit**

```bash
git add compile/INFLIGHT.md package.json .gitignore
git commit -m "docs(arc): INFLIGHT.md ops + wire inflight tests into verify"
```

---

## Self-Review

**1. Spec coverage:**
- Source = GitHub via `gh` (no token in code/browser) → Task 2 `gh_json`/`resolve_repos` + Global Constraints. ✓
- Scope = dark-factory + civilization-wiki, live topic query → Task 2 `resolve_repos`. ✓
- Unit = open PRs + merged-in-last-30-days → Task 2 `collect_items`. ✓
- Item mapping = `type:work, provenance:derived`, no ontology allowlist change → Task 1 `pr_to_item`. ✓
- Mechanism B = `inflight.py` → `dist/inflight.json`; page fetch + `validateItems` + overlay; fail-loud fallback; "updated N min ago" → Tasks 2, 3, 6. ✓
- Renderer: group-by toggle incl. **actor**, per-item author badge → Task 3 (`actorOf`/`laneOf`), Task 4 (`buildLayout` lanes), Task 5 (toolbar), Task 6 (tooltip author). ✓
- Tests wired into the CI gate → Task 7. ✓

**2. Placeholder scan:** no TBD/"handle errors appropriately"/"similar to Task N"; every code step is concrete. ✓

**3. Type consistency:** `pr_to_item` keys (no `seq`) ↔ `mergeInflight` assigns `seq` ↔ `loadInflight` reads `merged.items`/`merged.generated`/`merged.ok`/`merged.errors`. `inflight.json` shape `{generated,window_days,repos,errors,items}` ↔ test `LIVE_PR` ↔ `mergeInflight(data, inflight)`. `groupBy` dim strings (`tracks|status|repo|sprint|gate|actor`) consistent across `GROUPINGS` (nav), `buildLayout` opts, and `laneOf`/`actorOf` (ontology). `s.data`/`s.byId` introduced in Task 5 and relied on by Task 6's overlay. ✓
