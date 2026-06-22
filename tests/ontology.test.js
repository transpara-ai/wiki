// tests/ontology.test.js
const test = require('node:test');
const assert = require('node:assert');
const O = require('../compile/assets/civilizationOntology.js');

test('STATUS_ORDER is future→planned→active→done', () => {
  assert.deepStrictEqual(O.STATUS_ORDER, ['future', 'planned', 'active', 'done']);
});

test('deriveNow = max seq among done/active items', () => {
  const items = [
    { id: 'a', seq: 1, status: 'done' },
    { id: 'b', seq: 3, status: 'active' },
    { id: 'c', seq: 5, status: 'planned' },
  ];
  assert.strictEqual(O.deriveNow(items), 3);
});

test('deriveNow returns 0 when nothing is settled', () => {
  assert.strictEqual(O.deriveNow([{ id: 'a', seq: 4, status: 'planned' }]), 0);
});

test('validateItems accepts a clean settled-prefix set', () => {
  const items = [
    { id: 'a', type: 'work', status: 'done', provenance: 'reconstructed', seq: 1, sprint: 'origin', repo: ['civilization-wiki'] },
    { id: 'b', type: 'work', status: 'active', provenance: 'derived', seq: 2, sprint: 'hive', repo: ['hive'] },
    { id: 'c', type: 'work', status: 'planned', provenance: 'derived', seq: 3, sprint: 'deploy', repo: ['site'] },
  ];
  assert.strictEqual(O.validateItems(items).ok, true);
});
test('validateItems FAILS CLOSED on a planned item left of now', () => {
  const items = [
    { id: 'a', type: 'work', status: 'planned', provenance: 'derived', seq: 1, sprint: 'x', repo: ['r'] },
    { id: 'b', type: 'work', status: 'done', provenance: 'derived', seq: 5, sprint: 'y', repo: ['r'] },
  ];
  const r = O.validateItems(items);
  assert.strictEqual(r.ok, false);
  assert.ok(r.errors.some(e => /left of now/.test(e)));
});
test('validateItems rejects invalid enum + duplicate id + missing fields', () => {
  const items = [
    { id: 'a', type: 'nope', status: 'weird', provenance: 'x', seq: 'NaN', repo: 'r' },
    { id: 'a', type: 'work', status: 'done', provenance: 'derived', seq: 1, sprint: 's', repo: ['r'] },
  ];
  const r = O.validateItems(items);
  assert.strictEqual(r.ok, false);
  assert.ok(r.errors.some(e => /invalid type/.test(e)));
  assert.ok(r.errors.some(e => /invalid status/.test(e)));
  assert.ok(r.errors.some(e => /duplicate id/.test(e)));
  assert.ok(r.errors.some(e => /seq must be a number/.test(e)));
  assert.ok(r.errors.some(e => /invalid provenance/.test(e)));
  assert.ok(r.errors.some(e => /missing sprint/.test(e)));
});

const G = [
  { id: 'a', type: 'work', status: 'done',    blocked: false, seq: 1, sprint: 'hive',   gate: 'v3.9',  family: 'v3.9 milestones (A-J)', repo: ['hive'] },
  { id: 'b', type: 'work', status: 'active',  blocked: true,  seq: 2, sprint: 'gov',    gate: 'gate-k', family: 'v4.0 (K-V)',           repo: ['docs'] },
  { id: 'c', type: 'work', status: 'planned', blocked: false, seq: 3, sprint: 'deploy',                                                 repo: ['site'] },
  { id: 'd', type: 'work', status: 'active',  blocked: false, seq: 4, sprint: 'wiki',   gate: 'gate-k', family: 'v4.0 (K-V)',           repo: ['site'] },
];
test('groupBy status: fixed band order; each item in exactly one lane (blocked overrides)', () => {
  assert.deepStrictEqual(O.groupBy(G, 'status').map(l => l.lane), ['done', 'active', 'blocked', 'planned']);
  const active = O.groupBy(G, 'status').find(l => l.lane === 'active');
  assert.deepStrictEqual(active.items.map(i => i.id), ['d']); // b is blocked → only in 'blocked'
  const blocked = O.groupBy(G, 'status').find(l => l.lane === 'blocked');
  assert.deepStrictEqual(blocked.items.map(i => i.id), ['b']);
});
test('groupBy repo: 8-repo collection in Civilization→Governance order, each lane group-tagged', () => {
  const lanes = O.groupBy(G, 'repo');
  assert.deepStrictEqual(lanes.map(l => l.lane),
    ['agent', 'docs', 'eventgraph', 'hive', 'site', 'work', 'civilization-wiki', 'civilization-operation']);
  // the 6 operational repos are the "civilization" group; the 2 civilization-* repos are "governance"
  assert.strictEqual(lanes.find(l => l.lane === 'agent').group, 'civilization');
  assert.strictEqual(lanes.find(l => l.lane === 'work').group, 'civilization');
  assert.strictEqual(lanes.find(l => l.lane === 'civilization-wiki').group, 'governance');
  assert.strictEqual(lanes.find(l => l.lane === 'civilization-operation').group, 'governance');
  // every canonical repo shows even when empty — never swamped or dropped
  assert.strictEqual(lanes.find(l => l.lane === 'agent').items.length, 0);
  assert.strictEqual(lanes.find(l => l.lane === 'civilization-operation').items.length, 0);
  assert.deepStrictEqual(lanes.find(l => l.lane === 'site').items.map(i => i.id), ['c', 'd']);
});

test('groupBy repo places a multi-repo item in EACH of its repo lanes (not just repo[0])', () => {
  const item = { id: 'm', type: 'work', status: 'done', provenance: 'derived', seq: 1, sprint: 's', repo: ['docs', 'eventgraph'] };
  const lanes = O.groupBy([item], 'repo');
  assert.ok(lanes.find(l => l.lane === 'docs').items.includes(item));
  assert.ok(lanes.find(l => l.lane === 'eventgraph').items.includes(item),
    'eventgraph must appear even when it is the second repo');
});

test('groupBy repo dedupes a repeated repo so the item appears once in that lane', () => {
  const lanes = O.groupBy([{ id: 'd', repo: ['hive', 'hive'] }], 'repo');
  assert.strictEqual(lanes.find(l => l.lane === 'hive').items.length, 1);
});

test('groupBy repo: civilization-wiki is now IN the collection (governance), not (other)', () => {
  const lanes = O.groupBy([{ id: 'cw', repo: ['civilization-wiki'] }], 'repo');
  assert.ok(!lanes.some(l => l.lane === '(other)'), 'the generic (other) bucket is gone');
  const cw = lanes.find(l => l.lane === 'civilization-wiki');
  assert.deepStrictEqual(cw.items.map(i => i.id), ['cw']);
  assert.strictEqual(cw.group, 'governance');
});

test('groupBy repo: a repo OUTSIDE the collection gets its OWN named lane, tagged "outside"', () => {
  const lanes = O.groupBy([{ id: 'g', repo: ['ghost-repo'] }], 'repo');
  assert.ok(!lanes.some(l => l.lane === '(other)'), 'named, not bucketed into (other)');
  const ghost = lanes.find(l => l.lane === 'ghost-repo');
  assert.ok(ghost, 'the actual repo name appears as a lane');
  assert.deepStrictEqual(ghost.items.map(i => i.id), ['g']);
  assert.strictEqual(ghost.group, 'outside');
  assert.strictEqual(lanes[lanes.length - 1].lane, 'ghost-repo', 'outside lanes sort after the collection');
});

test('groupBy repo: prototype-named outside repos still get named lanes', () => {
  const items = [
    { id: 'ctor', repo: ['constructor'] },
    { id: 'toString', repo: ['toString'] },
    { id: 'proto', repo: ['__proto__'] },
  ];
  const lanes = O.groupBy(items, 'repo');
  ['constructor', 'toString', '__proto__'].forEach((repo) => {
    const lane = lanes.find(l => l.lane === repo);
    assert.ok(lane, repo + ' must appear as its own outside lane');
    assert.deepStrictEqual(lane.items.map(i => i.repo[0]), [repo]);
    assert.strictEqual(lane.group, 'outside');
  });
  assert.strictEqual(lanes.find(l => l.lane === '(no repo)'), undefined);
});

test('groupBy repo: the outside group is ABSENT when every repo is in the collection', () => {
  const lanes = O.groupBy([{ id: 'a', repo: ['site'] }, { id: 'b', repo: ['civilization-wiki'] }], 'repo');
  assert.ok(!lanes.some(l => l.group === 'outside'), 'no outside lanes');
  assert.strictEqual(lanes.length, 8, 'exactly the 8-repo collection, no extra');
});

test('groupBy repo: a repo-less item lands in a named "(no repo)" outside lane, never dropped', () => {
  // validateItems accepts repo: [] (it only checks Array), so the grouping must not make
  // such an item vanish — it lands in a named (no repo) lane, visible. (Fail-legible, never drop.)
  const lanes = O.groupBy([{ id: 'norepo', repo: [] }], 'repo');
  const nr = lanes.find(l => l.lane === '(no repo)');
  assert.ok(nr && nr.items.some(i => i.id === 'norepo'),
    'an item with an empty repo array must appear in (no repo), not disappear');
  assert.strictEqual(nr.group, 'outside');
});

test('groupBy repo is FAIL-CLOSED: no item dropped across canonical/outside/mixed/repo-less', () => {
  const items = [
    { id: 'canon', repo: ['docs'] },
    { id: 'mixed', repo: ['docs', 'ghost-repo'] },
    { id: 'outsideOnly', repo: ['ghost-repo'] },
    { id: 'norepo', repo: [] },
  ];
  const lanes = O.groupBy(items, 'repo');
  const seen = new Set();
  lanes.forEach(l => l.items.forEach(i => seen.add(i.id)));
  assert.deepStrictEqual([...seen].sort(), ['canon', 'mixed', 'norepo', 'outsideOnly'],
    'every input item must surface in at least one lane');
  // a mixed item appears in BOTH its canonical and its outside lane
  assert.ok(lanes.find(l => l.lane === 'docs').items.some(i => i.id === 'mixed'));
  assert.ok(lanes.find(l => l.lane === 'ghost-repo').items.some(i => i.id === 'mixed'));
  // outside lanes: named repos alphabetically, then "(no repo)" last
  assert.deepStrictEqual(lanes.filter(l => l.group === 'outside').map(l => l.lane), ['ghost-repo', '(no repo)']);
});

test('REPO_GROUPS is the curated Civilization/Governance collection; REPO_CANON is their union (8)', () => {
  assert.deepStrictEqual(O.REPO_GROUPS.map(g => g.label), ['Civilization', 'Governance']);
  assert.deepStrictEqual(O.REPO_GROUPS.find(g => g.key === 'civilization').repos,
    ['agent', 'docs', 'eventgraph', 'hive', 'site', 'work']);
  assert.deepStrictEqual(O.REPO_GROUPS.find(g => g.key === 'governance').repos,
    ['civilization-wiki', 'civilization-operation']);
  assert.deepStrictEqual(O.REPO_CANON,
    ['agent', 'docs', 'eventgraph', 'hive', 'site', 'work', 'civilization-wiki', 'civilization-operation']);
});

test('groupBy repo on real arc data: civ-wiki + civ-operation populated, no outside group', () => {
  const items = loadData().items;
  const lanes = O.groupBy(items, 'repo');
  assert.ok(!lanes.some(l => l.group === 'outside'), 'all real items are within the 8-repo collection');
  assert.ok(lanes.find(l => l.lane === 'civilization-wiki').items.length > 0, 'civ-wiki lane is populated');
  assert.ok(lanes.find(l => l.lane === 'civilization-operation').items.length > 0, 'civ-operation now populated (Gate-V / Event 12 progress-evidence export, civilization-operation#28)');
});
test('groupBy gate lanes by family; family-less items fall in (ungated); fixed family order', () => {
  const lanes = O.groupBy(G, 'gate');
  // Lane = item.family (not item.gate); ordered by GATE_FAMILIES with (ungated) last.
  assert.deepStrictEqual(lanes.map(l => l.lane), [
    'v3.9 milestones (A-J)',
    'v4.0 (K-V)',
    '(ungated)',
  ]);
  // Item 'c' has no family → (ungated). Items b & d share the v4.0 family.
  const ungated = lanes.find(l => l.lane === '(ungated)');
  assert.deepStrictEqual(ungated.items.map(i => i.id), ['c']);
  const v40 = lanes.find(l => l.lane === 'v4.0 (K-V)');
  assert.deepStrictEqual(v40.items.map(i => i.id).sort(), ['b', 'd']);
});
test('groupBy gate appends unknown families alphabetically, before (ungated)', () => {
  const items = [
    { id: 'u', type: 'work', status: 'done', blocked: false, seq: 1, sprint: 's', repo: ['r'] }, // no family → (ungated)
    { id: 'z', type: 'gate', status: 'done', blocked: false, seq: 2, sprint: 's', family: 'Zeta family', repo: ['r'] },
    { id: 'k', type: 'gate', status: 'done', blocked: false, seq: 3, sprint: 's', family: 'v4.0 (K-V)', repo: ['r'] },
    { id: 'm', type: 'gate', status: 'done', blocked: false, seq: 4, sprint: 's', family: 'Alpha family', repo: ['r'] },
  ];
  // Known family first (v4.0), then unknowns alphabetically (Alpha, Zeta), then (ungated) last.
  assert.deepStrictEqual(O.groupBy(items, 'gate').map(l => l.lane), [
    'v4.0 (K-V)',
    'Alpha family',
    'Zeta family',
    '(ungated)',
  ]);
});

test('visibleDeps returns nothing when nothing selected', () => {
  assert.deepStrictEqual(O.visibleDeps([{ id: 'b', deps: ['a'] }], null), []);
});
test('visibleDeps returns only edges touching the selection', () => {
  const items = [{ id: 'b', deps: ['a'] }, { id: 'c', deps: ['b'] }, { id: 'd', deps: ['x'] }];
  const e = O.visibleDeps(items, 'b');
  assert.deepStrictEqual(e.sort((p, q) => (p.from + p.to).localeCompare(q.from + q.to)),
    [{ from: 'a', to: 'b' }, { from: 'b', to: 'c' }]);
});

test('validateItems rejects a non-array', () => {
  const r = O.validateItems(null);
  assert.strictEqual(r.ok, false);
  assert.ok(r.errors.some(e => /not an array/.test(e)));
});

test('deriveNow on empty array is 0', () => {
  assert.strictEqual(O.deriveNow([]), 0);
});

test('deriveNow skips null items without throwing', () => {
  assert.strictEqual(O.deriveNow([null, { id: 'x', seq: 2, status: 'done' }]), 2);
});

// --- Migration tests (Task 5) ---
function loadData() {
  const fs = require('node:fs');
  const path = require('node:path');
  const code = fs.readFileSync(path.join(__dirname, '../compile/assets/civilizationArcData.js'), 'utf8');
  const win = {};
  new Function('window', code)(win);
  return win.CIVILIZATION_ARC_DATA;
}

test('migrated arc data passes the ontology allowlist', () => {
  const d = loadData();
  assert.ok(Array.isArray(d.items), 'data.items must exist');
  const r = O.validateItems(d.items);
  assert.strictEqual(r.ok, true, 'validateItems errors:\n' + r.errors.join('\n'));
});

test('migration keeps narrative beats (reconstructed) + live work (derived) + a goal', () => {
  const items = loadData().items;
  assert.ok(items.filter(i => i.provenance === 'reconstructed').length >= 20, 'keep ~28 beats');
  assert.ok(items.filter(i => i.provenance === 'derived').length >= 10, 'keep executionPlan work');
  assert.ok(items.some(i => i.type === 'goal'), 'north-star Goal present');
});

test('every dep id resolves to a real item', () => {
  const items = loadData().items;
  const ids = new Set(items.map(i => i.id));
  items.forEach(i => (i.deps || []).forEach(d => assert.ok(ids.has(d), 'dangling dep ' + d + ' on ' + i.id)));
});

test('executionPlan row statuses mirror canonical item statuses', () => {
  const data = loadData();
  const byCode = new Map(data.items.map(i => [i.code, i]));
  ['nearTerm', 'complete'].forEach((section) => {
    (data.executionPlan[section] || []).forEach((row) => {
      const item = byCode.get(row.order);
      assert(item, `executionPlan.${section} row ${row.order} must have a matching item`);
      assert.strictEqual(row.status, item.status, `executionPlan.${section}.${row.order} status drifted from item`);
    });
  });
});

// --- date backfill: fail-closed contract rule (date ⇒ ISO + done; ref well-formed) ---
function datedItem(over) {
  return Object.assign({ id: 'a', type: 'gate', status: 'done', provenance: 'derived',
    seq: 1, sprint: 's', repo: ['docs'] }, over || {});
}
test('validateItems FAILS CLOSED on a non-ISO date', () => {
  const r = O.validateItems([datedItem({ date: '6/17/2026' })]);
  assert.strictEqual(r.ok, false);
  assert.ok(r.errors.some(e => /date must be ISO/.test(e)));
});
test('validateItems FAILS CLOSED on a date attached to a non-done item', () => {
  const r = O.validateItems([datedItem({ status: 'active', date: '2026-06-17' })]);
  assert.strictEqual(r.ok, false);
  assert.ok(r.errors.some(e => /only done items may carry a date/.test(e)));
});
test('validateItems FAILS CLOSED on a malformed provenance ref', () => {
  const r = O.validateItems([datedItem({ ref: 'PR-138' })]);
  assert.strictEqual(r.ok, false);
  assert.ok(r.errors.some(e => /ref must look like/.test(e)));
});
test('validateItems accepts an ISO date + repo#n ref on a done item', () => {
  assert.strictEqual(O.validateItems([datedItem({ date: '2026-06-17', ref: 'docs#138' })]).ok, true);
});

test('arc data: exactly the 26 done items carry verified backfilled dates + provenance refs', () => {
  const items = loadData().items;
  const dated = items.filter(i => i.date != null);
  assert.strictEqual(dated.length, 26, 'exactly 26 dated items; got ' + dated.length);
  dated.forEach(i => {
    assert.strictEqual(i.status, 'done', i.code + ' is dated but not done');
    assert.ok(/^\d{4}-\d{2}-\d{2}$/.test(i.date), i.code + ' date not ISO: ' + i.date);
    assert.ok(i.date <= '2026-06-22', i.code + ' date is in the future: ' + i.date); // ISO sorts lexically
    assert.ok(/^[a-z][a-z0-9-]*#\d+$/.test(i.ref), i.code + ' missing/malformed ref: ' + i.ref);
  });
  // sentinels — each independently verified against the cited PR's merge date
  const by = c => items.find(i => i.code === c);
  assert.strictEqual(by('Gate-K').date, '2026-06-17');
  assert.strictEqual(by('Trace').date, '2026-05-14');
  assert.strictEqual(by('Gate-F').date, '2026-06-01');
  assert.strictEqual(by('N6').date, '2026-06-18');    // promote-to-canonical = docs#142 (not the #127 seed)
  assert.strictEqual(by('v4.0').date, '2026-06-12');  // v4.0 seed acceptance = docs#127
  assert.strictEqual(by('Gate-L').date, '2026-06-18'); // reconciliation certified = docs#141
  // Event 10-12 operating cadence — each dated to its cited capability PR's merge
  assert.strictEqual(by('Gate-T').date, '2026-06-21'); // Site consumes Assembly projection = site#89
  assert.strictEqual(by('Gate-U').date, '2026-06-22'); // RuntimeBroker dry-run fixture = work#55
  assert.strictEqual(by('Gate-V').date, '2026-06-21'); // progress-evidence export = civilization-operation#28
  // the contract rule holds over the whole baked set
  assert.strictEqual(O.validateItems(items).ok, true);
});

// --- Live in-flight overlay (mergeInflight) + actor facet (Task 3) ---
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
