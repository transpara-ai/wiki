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

  var GEOM = { gutter: 190, marginRight: 28, rowH: 30, trackPad: 8, trackGap: 10, top: 64, axisH: 34, minCol: 34 };

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
  function buildSprintTicks(data, items, sx) {
    var sprints = (data && data.sprints) || [];
    var minSeq = {};
    items.forEach(function (it) {
      if (!it || it.sprint == null || typeof it.seq !== "number") return;
      if (minSeq[it.sprint] === undefined || it.seq < minSeq[it.sprint]) minSeq[it.sprint] = it.seq;
    });
    var ticks = [];
    sprints.forEach(function (sp) {
      var ms = minSeq[sp.id];
      if (ms === undefined) return; // sprint with no items → no tick
      ticks.push({ id: sp.id, label: sp.label, x: sx(ms), startSeq: ms });
    });
    ticks.sort(function (a, b) { return a.x - b.x; });
    return ticks;
  }

  function bySeq(a, b) { return a.seq - b.seq; }

  function buildLayout(data, opts) {
    opts = opts || {};
    var width = opts.width || 1200;
    var collapsed = opts.collapsed || {};
    var items = data.items || [];
    var domain = data.domain || { start: 0, end: 15 };
    var plotLeft = GEOM.gutter;
    // distinct seq count drives the minimum content width (horizontal overflow).
    var seqSet = {};
    items.forEach(function (it) { if (it && typeof it.seq === "number") seqSet[it.seq] = 1; });
    var distinctN = Object.keys(seqSet).length;
    var minContent = plotLeft + Math.max(0, distinctN - 1) * GEOM.minCol + GEOM.marginRight;
    var contentWidth = Math.max(width, minContent);
    var plotRight = contentWidth - GEOM.marginRight;
    var sx = buildRankScale(items, plotLeft, plotRight);

    var groupBy = opts.groupBy || "tracks";
    var defs;
    if (groupBy === "tracks") {
      var beats = items.filter(function (i) { return i.type === "work" && i.provenance === "reconstructed"; });
      var decisions = items.filter(function (i) { return i.type === "decision"; });
      var goal = items.filter(function (i) { return i.type === "goal"; });
      var gates = items.filter(function (i) { return i.type === "gate"; });
      var work = items.filter(function (i) { return i.type === "work" && i.provenance === "derived"; });
      // Build gate rows from the ontology contract (groupBy "gate" = by family),
      // so every contract-valid gate lands in exactly one row — no hardcoded family list.
      var gateLanes = O.groupBy(gates, "gate");
      defs = [
        { id: "construction", label: "construction arc", rows: [{ id: "beats", label: "", items: beats.concat(decisions, goal) }] },
        { id: "gates", label: "gates", rows: gateLanes.map(function (lane) {
            return { id: "gate:" + lane.lane, label: lane.lane, items: lane.items };
          }) },
        { id: "worklist", label: "worklist", rows: [{ id: "work", label: "", items: work }] },
      ];
    } else {
      // Swimlane mode: one track per contract lane (status/repo/sprint/gate/actor),
      // each a single unlabeled row, all sharing the one chronological seq axis.
      defs = O.groupBy(items, groupBy).map(function (lane) {
        return {
          id: groupBy + ":" + lane.lane,
          label: lane.lane,
          rows: [{ id: groupBy + ":" + lane.lane + ":row", label: "", items: lane.items }],
        };
      });
    }

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
      sprintTicks: buildSprintTicks(data, items, sx),
      width: width, contentWidth: contentWidth, contentHeight: y + GEOM.axisH,
    };
  }

  var api = { GEOM: GEOM, GATE_FAMILIES: GATE_FAMILIES, buildRankScale: buildRankScale, buildLayout: buildLayout };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (root) root.CivArcLayout = api;
})(typeof window !== "undefined" ? window : null);
