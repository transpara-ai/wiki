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
  { id: 'b', type: 'work', status: 'active',  blocked: true,  seq: 2, sprint: 'gov',    gate: 'gate-k', family: 'v4.0 (K/L)',           repo: ['docs'] },
  { id: 'c', type: 'work', status: 'planned', blocked: false, seq: 3, sprint: 'deploy',                                                 repo: ['site'] },
  { id: 'd', type: 'work', status: 'active',  blocked: false, seq: 4, sprint: 'wiki',   gate: 'gate-k', family: 'v4.0 (K/L)',           repo: ['site'] },
];
test('groupBy status: fixed band order; each item in exactly one lane (blocked overrides)', () => {
  assert.deepStrictEqual(O.groupBy(G, 'status').map(l => l.lane), ['done', 'active', 'blocked', 'planned']);
  const active = O.groupBy(G, 'status').find(l => l.lane === 'active');
  assert.deepStrictEqual(active.items.map(i => i.id), ['d']); // b is blocked → only in 'blocked'
  const blocked = O.groupBy(G, 'status').find(l => l.lane === 'blocked');
  assert.deepStrictEqual(blocked.items.map(i => i.id), ['b']);
});
test('groupBy repo uses repo[0]', () => {
  assert.deepStrictEqual(O.groupBy(G, 'repo').map(l => l.lane), ['docs', 'hive', 'site']);
});
test('groupBy gate lanes by family; family-less items fall in (ungated); fixed family order', () => {
  const lanes = O.groupBy(G, 'gate');
  // Lane = item.family (not item.gate); ordered by GATE_FAMILIES with (ungated) last.
  assert.deepStrictEqual(lanes.map(l => l.lane), [
    'v3.9 milestones (A-J)',
    'v4.0 (K/L)',
    '(ungated)',
  ]);
  // Item 'c' has no family → (ungated). Items b & d share the v4.0 family.
  const ungated = lanes.find(l => l.lane === '(ungated)');
  assert.deepStrictEqual(ungated.items.map(i => i.id), ['c']);
  const v40 = lanes.find(l => l.lane === 'v4.0 (K/L)');
  assert.deepStrictEqual(v40.items.map(i => i.id).sort(), ['b', 'd']);
});
test('groupBy gate appends unknown families alphabetically, before (ungated)', () => {
  const items = [
    { id: 'u', type: 'work', status: 'done', blocked: false, seq: 1, sprint: 's', repo: ['r'] }, // no family → (ungated)
    { id: 'z', type: 'gate', status: 'done', blocked: false, seq: 2, sprint: 's', family: 'Zeta family', repo: ['r'] },
    { id: 'k', type: 'gate', status: 'done', blocked: false, seq: 3, sprint: 's', family: 'v4.0 (K/L)', repo: ['r'] },
    { id: 'm', type: 'gate', status: 'done', blocked: false, seq: 4, sprint: 's', family: 'Alpha family', repo: ['r'] },
  ];
  // Known family first (v4.0), then unknowns alphabetically (Alpha, Zeta), then (ungated) last.
  assert.deepStrictEqual(O.groupBy(items, 'gate').map(l => l.lane), [
    'v4.0 (K/L)',
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
