// compile/assets/civilizationArcLayout.js
// Pure geometry for the chronological-tracks arc. Browser (window.CivArcLayout) + Node. No DOM.
(function (root) {
  "use strict";
  var O = (typeof require !== "undefined") ? require("./civilizationOntology.js") : (root && root.CivOntology);

  var GATE_FAMILIES = [
    "v3.9 milestones (A-J)",
    "Deployment register (G-0..G-8.4)",
    "v4.0 (K/L)",
    "Release & security gates (v3.9)",
  ];

  var GEOM = { gutter: 168, marginRight: 28, rowH: 30, trackPad: 8, trackGap: 10, top: 64, axisH: 34 };

  var ERAS = [
    { seq: 0.3, label: "Feb" }, { seq: 3, label: "Mar" }, { seq: 6, label: "Apr" },
    { seq: 9, label: "May" }, { seq: 13.9, label: "Jun · now" }, { seq: 15, label: "future" },
  ];

  // Ordinal rank scale: distinct seq values are placed at equidistant columns
  // (NOT proportional to seq magnitude). Items sharing a seq share a column.
  function buildRankScale(items, plotLeft, plotRight) {
    var seqs = [];
    for (var i = 0; i < items.length; i++) {
      var s = items[i] && items[i].seq;
      if (typeof s === "number" && !isNaN(s)) seqs.push(s);
    }
    seqs.sort(function (a, b) { return a - b; });
    var distinct = [];
    for (var j = 0; j < seqs.length; j++) {
      if (j === 0 || seqs[j] !== seqs[j - 1]) distinct.push(seqs[j]);
    }
    var n = distinct.length;
    var rankOf = {};
    for (var k = 0; k < n; k++) rankOf[distinct[k]] = k;
    var span = (n > 1) ? (n - 1) : 1;
    function sx(seq) {
      var r = rankOf[seq];
      if (r === undefined) { // value not in the placed set: fall to nearest lower rank
        r = 0;
        for (var m = 0; m < n; m++) { if (distinct[m] <= seq) r = m; else break; }
      }
      return plotLeft + (r / span) * (plotRight - plotLeft);
    }
    sx.distinctCount = n;
    sx.rankOf = function (seq) { return rankOf[seq]; };
    return sx;
  }
  function bySeq(a, b) { return a.seq - b.seq; }

  function buildLayout(data, opts) {
    opts = opts || {};
    var width = opts.width || 1200;
    var collapsed = opts.collapsed || {};
    var items = data.items || [];
    var domain = data.domain || { start: 0, end: 15 };
    var plotLeft = GEOM.gutter, plotRight = width - GEOM.marginRight;
    var sx = buildRankScale(items, plotLeft, plotRight);

    var beats = items.filter(function (i) { return i.type === "work" && i.provenance === "reconstructed"; });
    var decisions = items.filter(function (i) { return i.type === "decision"; });
    var goal = items.filter(function (i) { return i.type === "goal"; });
    var gates = items.filter(function (i) { return i.type === "gate"; });
    var work = items.filter(function (i) { return i.type === "work" && i.provenance === "derived"; });

    var defs = [
      { id: "construction", label: "construction arc", rows: [{ id: "beats", label: "", items: beats.concat(decisions, goal) }] },
      { id: "gates", label: "gates", rows: GATE_FAMILIES.map(function (f) {
          return { id: "gate:" + f, label: f, items: gates.filter(function (g) { return (g.family || null) === f; }) };
        }) },
      { id: "worklist", label: "worklist", rows: [{ id: "work", label: "", items: work }] },
    ];

    var y = GEOM.top;
    var tracks = defs.map(function (t) {
      var isColl = !!collapsed[t.id], top = y, rows = [];
      if (isColl) { y += GEOM.rowH; }
      else {
        rows = t.rows.map(function (r) {
          var cy = y + GEOM.trackPad + GEOM.rowH / 2;
          var placed = r.items.slice().sort(bySeq).map(function (it) { return { item: it, x: sx(it.seq), y: cy }; });
          y += GEOM.rowH + GEOM.trackPad;
          return { id: r.id, label: r.label, y: cy, items: placed };
        });
      }
      var height = y - top; y += GEOM.trackGap;
      return { id: t.id, label: t.label, collapsed: isColl, top: top, height: height, rows: rows };
    });

    var nowSeq = O.deriveNow(items);
    return {
      tracks: tracks, scaleX: sx, domain: domain, plotLeft: plotLeft, plotRight: plotRight,
      nowSeq: nowSeq, nowX: sx(nowSeq),
      eras: ERAS.map(function (e) { return { x: sx(e.seq), label: e.label }; }),
      width: width, contentWidth: width, contentHeight: y + GEOM.axisH,
    };
  }

  var api = { GEOM: GEOM, GATE_FAMILIES: GATE_FAMILIES, ERAS: ERAS, buildRankScale: buildRankScale, buildLayout: buildLayout };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (root) root.CivArcLayout = api;
})(typeof window !== "undefined" ? window : null);
