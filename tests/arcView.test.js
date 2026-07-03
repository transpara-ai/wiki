// tests/arcView.test.js
// Unit tests for the pure derivations in compile/assets/civilizationArcView.js
// (design packet docs/superpowers/specs/2026-07-03-arc-2b-visual-packet.md §2.2).
// The DOM render paths are covered by tests/arc-dom-smoke.test.js.
const test = require('node:test');
const assert = require('node:assert');
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const O = require('../compile/assets/civilizationOntology.js');
const V = require('../compile/assets/civilizationArcView.js');

function loadArcData() {
  const context = { window: {} };
  vm.createContext(context);
  vm.runInContext(
    fs.readFileSync(path.join(__dirname, '..', 'compile/assets/civilizationArcData.js'), 'utf8'),
    context
  );
  return context.window.CIVILIZATION_ARC_DATA;
}
const DATA = loadArcData();

// Minimal valid-shaped item helper (unit tests exercise the derivations,
// which consume already-validated data; shape mirrors the ontology contract).
function it(over) {
  return Object.assign({
    id: 'x', type: 'work', status: 'done', blocked: false, blocked_reason: null,
    provenance: 'reconstructed', seq: 1, sprint: 'p1', repo: ['wiki'],
  }, over);
}
const SPRINTS = [{ id: 'p1', label: 'Phase 1' }, { id: 'p2', label: 'Phase 2' }];

// ── D1 phaseState ───────────────────────────────────────────────────────────

test('phaseRollup empty set is future never done', () => {
  // rollupCriteria([]) returns done (allDone seed) — the named fail-open lane.
  assert.strictEqual(O.rollupCriteria([]).status, 'done');
  const r = V.phaseState([], 'p1');
  assert.deepStrictEqual(r, { status: 'future', blocked: false, count: 0 });
});

test('phaseRollup counts only the {work, gate} piece allowlist', () => {
  const items = [
    it({ id: 'g', type: 'goal', status: 'active', sprint: 'p1' }),
    it({ id: 'd', type: 'decision', status: 'done', sprint: 'p1' }),
    it({ id: 'w', type: 'work', status: 'done', sprint: 'p1' }),
  ];
  const r = V.phaseState(items, 'p1');
  // the perpetual goal must not poison the phase; the decision is demoted
  assert.deepStrictEqual(r, { status: 'done', blocked: false, count: 1 });
});

test('phaseRollup matches rollupCriteria across the status×blocked domain', () => {
  const states = ['future', 'planned', 'active', 'done'];
  const combos = [];
  states.forEach((s) => [false, true].forEach((b) => combos.push([{ status: s, blocked: b }])));
  states.forEach((s1) => [false, true].forEach((b1) =>
    states.forEach((s2) => [false, true].forEach((b2) =>
      combos.push([{ status: s1, blocked: b1 }, { status: s2, blocked: b2 }])))));
  assert.strictEqual(combos.length, 8 + 64); // 72-case domain
  combos.forEach((combo, i) => {
    const items = combo.map((c, j) => it({
      id: `c${i}-${j}`, type: 'work', status: c.status,
      blocked: c.blocked, blocked_reason: c.blocked ? 'gate' : null, sprint: 'p1',
    }));
    const want = O.rollupCriteria(combo);
    const got = V.phaseState(items, 'p1');
    assert.strictEqual(got.status, want.status, `combo ${i}: status`);
    assert.strictEqual(got.blocked, want.blocked, `combo ${i}: blocked`);
    assert.strictEqual(got.count, combo.length, `combo ${i}: count`);
  });
});

// ── spine + collapse (B3) ───────────────────────────────────────────────────

test('done+blocked phase never collapses', () => {
  const items = [it({
    id: 'gb', type: 'gate', status: 'done', blocked: true, blocked_reason: 'gate',
    sprint: 'p1',
    criteria: [{ id: 'c1', status: 'done', blocked: true, blocked_reason: 'gate' }],
    blocked_criterion: 'c1',
  })];
  const spine = V.spine(items, SPRINTS);
  assert.strictEqual(spine[0].status, 'done');
  assert.strictEqual(spine[0].blocked, true);
  assert.strictEqual(spine[0].collapsed, false, 'a blocked phase must never fold away as finished');
  // and the proven-permissive branch: done AND unblocked collapses
  const clean = V.spine([it({ id: 'ok', sprint: 'p1' })], SPRINTS);
  assert.strictEqual(clean[0].collapsed, true);
  // non-done never collapses
  const active = V.spine([it({ id: 'a', status: 'active', sprint: 'p1' })], SPRINTS);
  assert.strictEqual(active[0].collapsed, false);
});

test('spine renders every sprint in order with counts', () => {
  const items = [it({ id: 'w1', sprint: 'p2', status: 'active' })];
  const spine = V.spine(items, SPRINTS);
  assert.deepStrictEqual(spine.map((p) => p.id), ['p1', 'p2']);
  assert.deepStrictEqual(spine.map((p) => p.count), [0, 1]);
  assert.strictEqual(spine[0].status, 'future'); // empty phase guard
});

// ── D2 currentPhase (deny-paths enumerate the full valid domain) ────────────

test('currentPhase resolves the baked frontier sprint', () => {
  const items = [
    it({ id: 'a', seq: 1, sprint: 'p1' }),
    it({ id: 'b', seq: 5, status: 'active', sprint: 'p2' }),
    it({ id: 'c', seq: 9, status: 'planned', sprint: 'p2' }),
  ];
  const r = V.currentPhase(items, SPRINTS);
  assert.strictEqual(r.ok, true);
  assert.strictEqual(r.sprintId, 'p2');
  assert.strictEqual(r.item.id, 'b');
});

test('currentPhase deny-path when no settled item exists', () => {
  const r = V.currentPhase([it({ id: 'p', status: 'planned' })], SPRINTS);
  assert.deepStrictEqual(r, { ok: false, reason: 'no-settled' });
});

test('currentPhase deny-path on ambiguous same-seq cross-sprint frontier', () => {
  const items = [
    it({ id: 'a', seq: 10, sprint: 'p1' }),
    it({ id: 'b', seq: 10, sprint: 'p2' }),
  ];
  const r1 = V.currentPhase(items, SPRINTS);
  const r2 = V.currentPhase(items.slice().reverse(), SPRINTS);
  assert.deepStrictEqual(r1, { ok: false, reason: 'ambiguous-frontier' });
  assert.deepStrictEqual(r2, r1, 'deny-path must be order-independent');
  // same-sprint tie is NOT ambiguous
  const same = [it({ id: 'a', seq: 10, sprint: 'p1' }), it({ id: 'b', seq: 10, sprint: 'p1' })];
  assert.strictEqual(V.currentPhase(same, SPRINTS).ok, true);
});

test('currentPhase deny-path on unknown sprint', () => {
  const r = V.currentPhase([it({ id: 'a', sprint: 'ghost' })], SPRINTS);
  assert.deepStrictEqual(r, { ok: false, reason: 'unknown-sprint' });
});

// ── D3 nextBlockingGate ─────────────────────────────────────────────────────

function gate(over) {
  return it(Object.assign({
    type: 'gate',
    criteria: [{ id: 'c', status: over.status || 'done', blocked: over.blocked === true, blocked_reason: over.blocked === true ? 'gate' : null }],
  }, over, over.blocked === true ? { blocked_criterion: 'c' } : {}));
}

test('nextBlockingGate: a blocked gate outranks planned gates ahead', () => {
  const items = [
    it({ id: 'front', seq: 10 }),
    gate({ id: 'g-planned', status: 'planned', seq: 11 }),
    gate({ id: 'g-blocked', status: 'planned', blocked: true, blocked_reason: 'gate', seq: 14 }),
  ];
  assert.strictEqual(V.nextBlockingGate(items).id, 'g-blocked');
});

test('nextBlockingGate: nearest planned gate ahead when nothing is blocked', () => {
  const items = [
    it({ id: 'front', seq: 10 }),
    gate({ id: 'g-behind', status: 'done', seq: 5 }),
    gate({ id: 'g-far', status: 'planned', seq: 14 }),
    gate({ id: 'g-near', status: 'planned', seq: 11 }),
  ];
  assert.strictEqual(V.nextBlockingGate(items).id, 'g-near');
});

test('nextBlockingGate: falls to the nearest future gate ahead, else null', () => {
  const items = [
    it({ id: 'front', seq: 10 }),
    gate({ id: 'g-future', status: 'future', seq: 12 }),
  ];
  assert.strictEqual(V.nextBlockingGate(items).id, 'g-future');
  assert.strictEqual(V.nextBlockingGate([it({ id: 'only', seq: 1 })]), null);
});

test('nextBlockingGate ties resolve by (seq,id) independent of array order', () => {
  const a = gate({ id: 'gate-a', status: 'planned', blocked: true, blocked_reason: 'gate', seq: 5 });
  const b = gate({ id: 'gate-b', status: 'planned', blocked: true, blocked_reason: 'gate', seq: 5 });
  assert.strictEqual(V.nextBlockingGate([it({ id: 'f', seq: 1 }), a, b]).id, 'gate-a');
  assert.strictEqual(V.nextBlockingGate([it({ id: 'f', seq: 1 }), b, a]).id, 'gate-a');
});

// ── D4 activeWork ───────────────────────────────────────────────────────────

test('activeWork filters to active work, sorted frontier-first, deterministic', () => {
  const items = [
    it({ id: 'w1', status: 'active', seq: 2 }),
    it({ id: 'w2', status: 'active', seq: 8 }),
    it({ id: 'g1', type: 'gate', status: 'active', seq: 9, criteria: [{ id: 'c', status: 'active' }] }),
    it({ id: 'w3', status: 'done', seq: 3 }),
    it({ id: 'wa', status: 'active', seq: 2 }),
  ];
  assert.deepStrictEqual(V.activeWork(items).map((x) => x.id), ['w2', 'w1', 'wa']);
});

// ── D5 latestClosed ─────────────────────────────────────────────────────────

test('latestClosed picks the max ISO date among done items, deterministic on ties', () => {
  const items = [
    it({ id: 'a', date: '2026-06-01' }),
    it({ id: 'b', date: '2026-06-22' }),
    it({ id: 'c', status: 'active' }),
    it({ id: 'bb', date: '2026-06-22' }),
  ];
  assert.strictEqual(V.latestClosed(items).id, 'b'); // date tie → id order
  assert.strictEqual(V.latestClosed([it({ id: 'nodate' })]), null);
});

// ── Real-data anchors (packet §1 measured facts) ────────────────────────────

test('D3 selects gate-k-go-live on real data', () => {
  const g = V.nextBlockingGate(DATA.items);
  assert(g, 'a next blocking gate must exist');
  assert.strictEqual(g.id, 'gate-k-go-live');
});

test('D4 census on real data is 9 active work items + live overlay rows', () => {
  assert.strictEqual(V.activeWork(DATA.items).length, 9);
  const live = it({ id: 'pr-hive-999', status: 'active', provenance: 'derived', seq: 14.37, sprint: 'stewardship' });
  assert.strictEqual(V.activeWork(DATA.items.concat([live])).length, 10);
});

test('currentPhase anchors to baked frontier under live overlay', () => {
  const baked = V.currentPhase(DATA.items, DATA.sprints);
  assert.strictEqual(baked.ok, true);
  assert.strictEqual(baked.sprintId, 'deployment');
  assert.strictEqual(baked.item.id, 'g-5-2');
  // a live overlay item ahead of the baked frontier would flip a merged-set
  // read to stewardship — the view must therefore derive from baked only
  const live = it({ id: 'pr-hive-999', status: 'active', provenance: 'derived', seq: 14.37, sprint: 'stewardship' });
  const merged = V.currentPhase(DATA.items.concat([live]), DATA.sprints);
  assert.strictEqual(merged.sprintId, 'stewardship', 'sanity: the trap D2 avoids is real');
});

test('spine snapshot anchors on real data: 15 phases, frontier deployment, stewardship blocked', () => {
  const spine = V.spine(DATA.items, DATA.sprints);
  assert.strictEqual(spine.length, 15);
  const by = {};
  spine.forEach((p) => { by[p.id] = p; });
  assert.strictEqual(by.deployment.status, 'active');
  assert.strictEqual(by.stewardship.blocked, true);
  assert.strictEqual(by.stewardship.collapsed, false);
  // structural: collapse ⇔ done AND !blocked, every phase
  spine.forEach((p) => {
    assert.strictEqual(p.collapsed, p.status === 'done' && p.blocked === false, `phase ${p.id}`);
  });
  assert.strictEqual(spine.filter((p) => p.collapsed).length, 12);
});
