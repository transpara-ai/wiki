const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const L = require('../compile/assets/civilizationArcLayout.js');

function loadData() {
  const code = fs.readFileSync(path.join(__dirname, '../compile/assets/civilizationArcData.js'), 'utf8');
  const w = {}; new Function('window', code)(w); return w.CIVILIZATION_ARC_DATA;
}

test('buildRankScale spaces distinct seqs equidistantly across the plot', () => {
  const sx = L.buildRankScale(
    [{ seq: 0 }, { seq: 5 }, { seq: 5 }, { seq: 99 }], // 3 distinct: 0,5,99
    100, 400
  );
  assert.strictEqual(sx.distinctCount, 3);
  assert.strictEqual(sx(0), 100);    // first column at plotLeft
  assert.strictEqual(sx(99), 400);   // last column at plotRight
  assert.strictEqual(sx(5), 250);    // middle column — equidistant, NOT proportional to value
});

test('items sharing a seq share an x-column', () => {
  const sx = L.buildRankScale([{ seq: 1 }, { seq: 2 }, { seq: 2 }], 0, 200);
  assert.strictEqual(sx.distinctCount, 2);   // the two seq=2 items collapse to one column
  assert.strictEqual(sx.rankOf(2), 1);       // seq 2 is the last distinct column
  assert.strictEqual(sx(2), 200);            // last distinct column maps to plotRight
});

test('buildLayout yields 3 tracks; gates expands into 4 family rows', () => {
  const lay = L.buildLayout(loadData(), { width: 1600 });
  assert.deepStrictEqual(lay.tracks.map(t => t.id), ['construction', 'gates', 'worklist']);
  assert.strictEqual(lay.tracks.find(t => t.id === 'gates').rows.length, 4);
});

test('every gate lands in exactly one family row (none dropped)', () => {
  const data = loadData();
  const lay = L.buildLayout(data, { width: 1600 });
  const placed = lay.tracks.find(t => t.id === 'gates').rows.reduce((n, r) => n + r.items.length, 0);
  assert.strictEqual(placed, data.items.filter(i => i.type === 'gate').length);
});

test('gate rows match the contract groupBy lanes exactly (no hardcoded gaps)', () => {
  // The layout gate rows must equal exactly what O.groupBy(gates,"gate") returns —
  // i.e. the layout is contract-driven, not hardcoded to 4 families.
  const O = require('../compile/assets/civilizationOntology.js');
  const data = loadData();
  const gates = data.items.filter((i) => i.type === 'gate');
  const contractLanes = O.groupBy(gates, 'gate').map((l) => l.lane);
  const lay = L.buildLayout(data, { width: 1600 });
  const layoutLanes = lay.tracks.find((t) => t.id === 'gates').rows.map((r) => r.label);
  assert.deepStrictEqual(layoutLanes, contractLanes,
    'layout gate lanes must equal O.groupBy(gates,"gate") lanes');
});

test('unknown-family gate gets its own row and is placed (not dropped)', () => {
  // Inject a validate-ok gate with an unknown family ("zzz-new").
  const O = require('../compile/assets/civilizationOntology.js');
  const data = loadData();
  // Clone items and inject a new gate with unknown family.
  const newGate = {
    id: 'gate-zzz', type: 'gate', status: 'planned', provenance: 'reconstructed',
    seq: 0.5, sprint: 'origin', repo: ['civilization-wiki'],
    family: 'zzz-new', code: 'ZZZ', label: 'Test unknown family gate', blocked: false,
  };
  const testData = Object.assign({}, data, { items: data.items.concat([newGate]) });
  const lay = L.buildLayout(testData, { width: 1600 });
  const gateTrack = lay.tracks.find((t) => t.id === 'gates');
  const laneLabels = gateTrack.rows.map((r) => r.label);
  assert.ok(laneLabels.includes('zzz-new'), '"zzz-new" unknown family must get its own row; got: ' + laneLabels.join(' | '));
  const placed = gateTrack.rows.reduce((n, r) => n + r.items.length, 0);
  assert.strictEqual(placed, testData.items.filter((i) => i.type === 'gate').length,
    'every gate (including unknown-family) must be placed');
});

test('no-family gate falls in (ungated) row and is placed (not dropped)', () => {
  // Inject a validate-ok gate with no family at all.
  const data = loadData();
  const ungatedGate = {
    id: 'gate-ungated', type: 'gate', status: 'planned', provenance: 'reconstructed',
    seq: 0.5, sprint: 'origin', repo: ['civilization-wiki'],
    // no family field
    code: 'UNG', label: 'Test ungated gate', blocked: false,
  };
  const testData = Object.assign({}, data, { items: data.items.concat([ungatedGate]) });
  const lay = L.buildLayout(testData, { width: 1600 });
  const gateTrack = lay.tracks.find((t) => t.id === 'gates');
  const laneLabels = gateTrack.rows.map((r) => r.label);
  assert.ok(laneLabels.includes('(ungated)'), '"(ungated)" row must appear for no-family gate; got: ' + laneLabels.join(' | '));
  const placed = gateTrack.rows.reduce((n, r) => n + r.items.length, 0);
  assert.strictEqual(placed, testData.items.filter((i) => i.type === 'gate').length,
    'every gate (including no-family) must be placed');
});

test('nowX === scaleX(deriveNow); frontier is 13.9', () => {
  const lay = L.buildLayout(loadData(), { width: 1600 });
  assert.ok(Math.abs(lay.nowSeq - 13.9) < 1e-9);
  assert.strictEqual(lay.nowX, lay.scaleX(lay.nowSeq));
});

test('collapsing the gates track reduces contentHeight', () => {
  const data = loadData();
  const full = L.buildLayout(data, { width: 1600 });
  const coll = L.buildLayout(data, { width: 1600, collapsed: { gates: true } });
  assert.ok(coll.contentHeight < full.contentHeight);
});

test('markers within a row are placed in non-decreasing seq order', () => {
  const xs = L.buildLayout(loadData(), { width: 1600 }).tracks[0].rows[0].items.map(p => p.x);
  for (let i = 1; i < xs.length; i++) assert.ok(xs[i] >= xs[i - 1]);
});

test('sprintTicks: one ordered tick per sprint, first is origin at plotLeft', () => {
  const data = loadData();
  const lay = L.buildLayout(data, { width: 1600 });
  assert.strictEqual(lay.sprintTicks.length, 15);
  for (let i = 1; i < lay.sprintTicks.length; i++) {
    assert.ok(lay.sprintTicks[i].x >= lay.sprintTicks[i - 1].x);
  }
  assert.strictEqual(lay.sprintTicks[0].id, 'origin');
  assert.strictEqual(lay.sprintTicks[0].x, lay.plotLeft);
  assert.strictEqual(lay.eras, undefined);
});

test('narrow width forces horizontal overflow via MIN_COL', () => {
  const data = loadData();
  const lay = L.buildLayout(data, { width: 300 });
  const n = lay.scaleX.distinctCount;
  assert.ok(lay.contentWidth >= lay.plotLeft + (n - 1) * L.GEOM.minCol + L.GEOM.marginRight);
  assert.ok(lay.contentWidth > 300);
});

test('worklist chip footprint: adjacent worklist markers differ by at least chip width (>=30, i.e. >=minCol)', () => {
  // At a deliberately narrow width the worklist row must still space adjacent markers
  // at least 30px apart (the chip width, per civilizationArcDraw.js w=30).
  // minCol=34 ≥ 30 guarantees this when the overflow scale is in effect.
  const data = loadData();
  const lay = L.buildLayout(data, { width: 300 });
  // Find the worklist track row.
  const worklist = lay.tracks.find((t) => t.id === 'worklist');
  assert.ok(worklist, 'worklist track must exist');
  const workRow = worklist.rows[0];
  assert.ok(workRow, 'worklist row[0] must exist');
  const xs = workRow.items.map((p) => p.x);
  // Adjacent placed markers must be at least minCol apart (≥30 for chip coverage).
  for (let i = 1; i < xs.length; i++) {
    assert.ok(
      xs[i] - xs[i - 1] >= 30,
      'adjacent worklist markers too close: ' + (xs[i] - xs[i - 1]).toFixed(2) + 'px (need >=30 for chip footprint)'
    );
  }
  // Sanity: minCol itself must be >=30.
  assert.ok(L.GEOM.minCol >= 30, 'GEOM.minCol must be >= 30 to cover chip footprint');
});

// --- group-by lanes (Task 4) ---
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
  const base = L.buildLayout(testData, { width: 1600 });
  assert.strictEqual(lay.nowX, base.nowX);
});
