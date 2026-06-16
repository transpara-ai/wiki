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
  { id: 'a', type: 'work', status: 'done',    blocked: false, seq: 1, sprint: 'hive',   gate: 'v3.9',  repo: ['hive'] },
  { id: 'b', type: 'work', status: 'active',  blocked: true,  seq: 2, sprint: 'gov',    gate: 'gate-k', repo: ['docs'] },
  { id: 'c', type: 'work', status: 'planned', blocked: false, seq: 3, sprint: 'deploy',                 repo: ['site'] },
  { id: 'd', type: 'work', status: 'active',  blocked: false, seq: 4, sprint: 'wiki',   gate: 'gate-k', repo: ['site'] },
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
test('groupBy gate puts gateless items in (ungated)', () => {
  assert.ok(O.groupBy(G, 'gate').map(l => l.lane).includes('(ungated)'));
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
