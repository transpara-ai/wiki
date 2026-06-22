// compile/assets/civilizationArcLayout.js
// Pure geometry for the chronological-tracks arc. Browser (window.CivArcLayout) + Node. No DOM.
(function (root) {
  "use strict";
  var O = (typeof require !== "undefined") ? require("./civilizationOntology.js") : (root && root.CivOntology);

  var GATE_FAMILIES = [
    "v3.9 milestones (A-J)",
    "Deployment register (G-0..G-8.4)",
    "v4.0 (K-V)",
    "Release & security gates (v3.9)",
  ];

  // plotPad insets the first column from the gutter so markers never collide with
  // the right-anchored track/sub-row labels that live in the gutter.
  // detailCol = chip-safe column width (>= the 30px worklist-chip footprint), used to
  // derive the max zoom so a readable detail view is always reachable (see detailWidth).
  var GEOM = { gutter: 190, marginRight: 28, rowH: 30, trackPad: 8, trackGap: 10, top: 64, axisH: 56, plotPad: 18, detailCol: 34, axisFont: 14, axisAngle: 38, axisHMin: 44, groupHeaderH: 22 };

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
      ticks.push({ id: sp.id, label: sp.label, display: axisLabelText(sp.label), x: sx(ms), startSeq: ms });
    });
    ticks.sort(function (a, b) { return a.x - b.x; });
    return ticks;
  }

  // Chip-safe full-detail content width: the width at which every distinct-seq column
  // is at least GEOM.detailCol wide. The controller derives its max zoom from this so a
  // readable detail view is always reachable, no matter how narrow the frame is —
  // replacing the old min-column overflow guarantee that was removed for fit-to-frame.
  function detailWidth(data) {
    var items = (data && data.items) || [];
    var seqSet = {};
    items.forEach(function (it) { if (it && typeof it.seq === "number") seqSet[it.seq] = 1; });
    var distinctN = Object.keys(seqSet).length;
    return GEOM.gutter + GEOM.plotPad + Math.max(0, distinctN - 1) * GEOM.detailCol + GEOM.marginRight;
  }

  function bySeq(a, b) { return a.seq - b.seq; }

  // Display label for an axis tick: the punchy part after the last "/", shown in
  // FULL (no ellipsis truncation). The complete sprint name still shows in tooltips.
  function axisLabelText(label) {
    var s = label == null ? "" : String(label);
    var slash = s.lastIndexOf("/");
    if (slash !== -1) s = s.slice(slash + 1);
    return s.replace(/^\s+|\s+$/g, "");
  }

  // Axis band height grows to fit the rotated sprint labels in full (no clipping,
  // no ellipsis). Derived from the longest display label at the tick rotation angle,
  // so zooming (which never changes label length) keeps every label fully visible.
  function computeAxisH(ticks) {
    var maxChars = 0;
    (ticks || []).forEach(function (t) {
      var s = (t && t.display != null) ? String(t.display) : "";
      if (s.length > maxChars) maxChars = s.length;
    });
    var approxW = maxChars * GEOM.axisFont * 0.6;          // mono ~= 0.6em / char
    var drop = approxW * Math.sin(GEOM.axisAngle * Math.PI / 180);
    return Math.max(GEOM.axisHMin, Math.ceil(drop) + GEOM.axisFont + 16);
  }

  function buildLayout(data, opts) {
    opts = opts || {};
    var width = opts.width || 1200;
    var collapsed = opts.collapsed || {};
    var items = data.items || [];
    var domain = data.domain || { start: 0, end: 15 };
    var plotLeft = GEOM.gutter;
    var plotStart = plotLeft + GEOM.plotPad;   // first column is inset from the gutter labels
    // Presentational width: at zoom 1 the whole arc fits the frame (contentWidth ==
    // frame width → no horizontal scroll). Zoom >1 widens content proportionally so
    // the ordinal rank scale spreads distinct seqs across more space for detail (the
    // frame then scrolls). Zoom <1 clamps to fit — content is never narrower than the
    // frame. This replaces the old min-column-width overflow that forced scroll even
    // on wide desktops.
    var zoom = opts.zoom;
    if (typeof zoom !== "number" || isNaN(zoom) || zoom < 1) zoom = 1;
    var contentWidth = Math.round(width * zoom);
    var plotRight = contentWidth - GEOM.marginRight;
    var sx = buildRankScale(items, plotStart, plotRight);

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
          group: lane.group,              // repo view: "civilization" | "governance" | "outside"
          groupLabel: lane.groupLabel,    // undefined for other dimensions → no header drawn
          rows: [{ id: groupBy + ":" + lane.lane + ":row", label: "", items: lane.items }],
        };
      });
    }

    var y = GEOM.top;
    var groupHeaders = [];
    var prevGroup = null;
    var tracks = defs.map(function (t) {
      // Group header (repo view only): emit when entering a new display group. Other
      // dimensions carry no group on their defs, so no header is produced.
      if (t.group && t.group !== prevGroup) {
        groupHeaders.push({ group: t.group, label: t.groupLabel, y: y });
        y += GEOM.groupHeaderH;
      }
      prevGroup = t.group || null;
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
    var sprintTicks = buildSprintTicks(data, items, sx);
    var axisH = computeAxisH(sprintTicks);
    return {
      tracks: tracks, groupHeaders: groupHeaders, scaleX: sx, domain: domain, plotLeft: plotLeft, plotStart: plotStart, plotRight: plotRight,
      nowSeq: nowSeq, nowX: sx(nowSeq),
      sprintTicks: sprintTicks, axisH: axisH,
      width: width, contentWidth: contentWidth, contentHeight: y + axisH,
    };
  }

  var api = { GEOM: GEOM, GATE_FAMILIES: GATE_FAMILIES, buildRankScale: buildRankScale, buildLayout: buildLayout, detailWidth: detailWidth };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (root) root.CivArcLayout = api;
})(typeof window !== "undefined" ? window : null);
