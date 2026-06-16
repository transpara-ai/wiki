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
});
