// compile/assets/civilizationArcDraw.js
// Pure DOM/SVG construction for the chronological-tracks arc.
// No event wiring, no state mutation, no data fetching. Each drawer appends SVG
// elements to a given <svg> from a layout object produced by CivArcLayout.buildLayout.
// Works in the browser and under jsdom (uses svg.ownerDocument.createElementNS).
(function (root) {
  "use strict";

  var NS = "http://www.w3.org/2000/svg";

  // Geometry shared with the layout module. Re-resolved here so the drawers do not
  // depend on the controller threading it in; falls back to the layout module's GEOM.
  var LAYOUT = (typeof require !== "undefined")
    ? require("./civilizationArcLayout.js")
    : (root && root.CivArcLayout);
  var GEOM = (LAYOUT && LAYOUT.GEOM) || {
    gutter: 168, marginRight: 28, rowH: 30, trackPad: 8, trackGap: 10, top: 64, axisH: 34,
  };

  // Status -> fill hex. These read in both light and dark themes.
  var STATUS_FILL = {
    done: "#1D9E75",
    active: "#BA7517",
    blocked: "#E24B4A",
    planned: "#378ADD",
    future: "#888780",
  };
  var BLOCKED_RED = "#E24B4A";
  var FUTURE_FILL = "#888780";

  // ---- element helper -------------------------------------------------------

  // Create an SVG element with attributes. Null/undefined attribute values are
  // skipped. Numbers are coerced to strings by setAttribute.
  function svgEl(doc, tag, attrs) {
    var el = doc.createElementNS(NS, tag);
    if (attrs) {
      for (var k in attrs) {
        if (!Object.prototype.hasOwnProperty.call(attrs, k)) continue;
        var v = attrs[k];
        if (v === null || v === undefined) continue;
        el.setAttribute(k, v);
      }
    }
    return el;
  }

  // Fill colour for an item by status; blocked items always read red.
  function statusFill(item) {
    if (!item) return FUTURE_FILL;
    if (item.blocked) return BLOCKED_RED;
    return STATUS_FILL[item.status] || FUTURE_FILL;
  }

  function num(n, fallback) {
    return (typeof n === "number" && !isNaN(n)) ? n : (fallback || 0);
  }

  // Short, bounded axis label: prefer the punchy part after the last "/", then
  // truncate so the rotated sprint-tick labels stay legible and don't overrun the
  // axis band or collide with each other when the arc is fit to a narrow frame.
  // The full sprint label still shows in each marker's tooltip.
  function axisTickLabel(label) {
    var s = label == null ? "" : String(label);
    var slash = s.lastIndexOf("/");
    if (slash !== -1) s = s.slice(slash + 1);
    s = s.replace(/^\s+|\s+$/g, "");
    var MAX = 20;
    if (s.length > MAX) s = s.slice(0, MAX - 1).replace(/\s+$/, "") + "…";
    return s;
  }

  // ---- axis -----------------------------------------------------------------

  function drawAxis(svg, layout) {
    if (!svg || !layout) return;
    var doc = svg.ownerDocument;
    var baseY = num(layout.contentHeight) - GEOM.axisH;
    var plotLeft = num(layout.plotLeft);
    var plotStart = (layout.plotStart != null) ? num(layout.plotStart) : plotLeft;
    var plotRight = num(layout.plotRight);

    // Baseline (starts at the inset plot start so it aligns with the first tick).
    svg.appendChild(svgEl(doc, "line", {
      "class": "arc-axis-base",
      x1: plotStart, y1: baseY, x2: plotRight, y2: baseY,
      stroke: "var(--color-text-tertiary)", "stroke-width": 1,
      "vector-effect": "non-scaling-stroke",
    }));

    // Sprint start-ticks: a short tick + rotated label at each sprint's first item.
    var ticks = layout.sprintTicks || [];
    ticks.forEach(function (t) {
      var tx = num(t.x);
      svg.appendChild(svgEl(doc, "line", {
        "class": "arc-sprint-tick",
        x1: tx, y1: baseY, x2: tx, y2: baseY + 5,
        stroke: "var(--color-text-tertiary)", "stroke-width": 1,
        "vector-effect": "non-scaling-stroke",
      }));
      var label = svgEl(doc, "text", {
        "class": "arc-sprint-tick-label",
        x: tx, y: baseY + 10,
        "text-anchor": "end",
        "font-size": 9.5,
        fill: "var(--color-text-secondary)",
        transform: "rotate(-38 " + tx + " " + (baseY + 10) + ")",
      });
      label.textContent = axisTickLabel(t.label);
      svg.appendChild(label);
    });

    // NOW-LINE.
    var nowX = num(layout.nowX);
    var nowTop = GEOM.top - 28;
    svg.appendChild(svgEl(doc, "line", {
      "class": "arc-now-line",
      x1: nowX, y1: nowTop, x2: nowX, y2: baseY,
      stroke: "#BA7517", "stroke-width": 1.5, "stroke-dasharray": "4 5",
      "vector-effect": "non-scaling-stroke",
    }));
    // "now" tag near the top of the now-line.
    var tagW = 30, tagH = 15;
    svg.appendChild(svgEl(doc, "rect", {
      "class": "arc-now-tag",
      x: nowX - tagW / 2, y: nowTop - tagH, width: tagW, height: tagH, rx: 3,
      fill: "#FAC775",
    }));
    var nowText = svgEl(doc, "text", {
      "class": "arc-now-tag-label",
      x: nowX, y: nowTop - tagH / 2 + 3,
      "text-anchor": "middle",
      "font-size": 10,
      fill: "#3a2a08",
    });
    nowText.textContent = "now";
    svg.appendChild(nowText);
  }

  // ---- tracks ---------------------------------------------------------------

  function drawTracks(svg, layout, state) {
    if (!svg || !layout) return;
    state = state || {};
    var doc = svg.ownerDocument;
    var tracks = layout.tracks || [];
    var contentWidth = num(layout.contentWidth);
    var plotLeft = num(layout.plotLeft);

    tracks.forEach(function (track, idx) {
      // Faint background band; alternate stripe via opacity.
      svg.appendChild(svgEl(doc, "rect", {
        "class": "arc-track-band",
        x: 0, y: num(track.top), width: contentWidth, height: num(track.height), rx: 6,
        fill: "var(--color-background-secondary)",
        opacity: (idx % 2 === 0) ? 0.6 : 0.35,
      }));

      // Gutter label group: chevron + clickable label.
      var labelX = plotLeft - 14;
      var labelY = num(track.top) + 16;
      var group = svgEl(doc, "g", { "class": "arc-track-label-group" });

      // Chevron just left of the label text. Down triangle when expanded,
      // right triangle when collapsed. Sized ~8px, sitting left of labelX.
      var cx = labelX - 8;
      var cy = labelY - 4;
      var chevD = track.collapsed
        // right-pointing triangle
        ? "M " + (cx - 3) + " " + (cy - 4) + " L " + (cx + 3) + " " + cy + " L " + (cx - 3) + " " + (cy + 4) + " Z"
        // down-pointing triangle
        : "M " + (cx - 4) + " " + (cy - 3) + " L " + (cx + 4) + " " + (cy - 3) + " L " + cx + " " + (cy + 3) + " Z";
      group.appendChild(svgEl(doc, "path", {
        "class": "arc-track-chevron",
        d: chevD,
        fill: "var(--color-text-primary)",
        "data-arc-collapse": track.id,
      }));

      var label = svgEl(doc, "text", {
        "class": "arc-track-label",
        x: labelX, y: labelY,
        "text-anchor": "end",
        "font-size": 13,
        fill: "var(--color-text-primary)",
        "data-arc-collapse": track.id,
      });
      label.textContent = track.label == null ? "" : String(track.label);
      group.appendChild(label);
      svg.appendChild(group);

      // Sub-row labels (skipped implicitly when collapsed: rows is empty then).
      (track.rows || []).forEach(function (row) {
        var rowLabel = row.label == null ? "" : String(row.label);
        if (rowLabel === "") return; // single-row tracks carry no sub-row label
        var sub = svgEl(doc, "text", {
          "class": "arc-subrow-label",
          x: plotLeft - 14, y: num(row.y) + 4,
          "text-anchor": "end",
          "font-size": 11,
          fill: "var(--color-text-secondary)",
        });
        sub.textContent = rowLabel;
        svg.appendChild(sub);
      });
    });
  }

  // ---- markers --------------------------------------------------------------

  // Build the shape element for one placed item. Shape varies by type/provenance;
  // fill varies by status. Returns the SVG element (not yet parented).
  function markerShape(doc, item, x, y) {
    var fill = statusFill(item);
    var type = item.type;

    if (type === "gate") {
      // diamond
      var d = "M " + x + " " + (y - 7) +
        " L " + (x + 7) + " " + y +
        " L " + x + " " + (y + 7) +
        " L " + (x - 7) + " " + y + " Z";
      return svgEl(doc, "path", { d: d, fill: fill });
    }
    if (type === "decision") {
      return svgEl(doc, "circle", { cx: x, cy: y, r: 3, fill: fill });
    }
    if (type === "goal") {
      return svgEl(doc, "circle", { "class": "arc-goal", cx: x, cy: y, r: 6, fill: fill });
    }
    if (type === "work" && item.provenance === "derived") {
      // worklist chip: rounded rect ~30 x 12 centred on (x, y)
      var w = 30, h = 12;
      return svgEl(doc, "rect", {
        x: x - w / 2, y: y - h / 2, width: w, height: h, rx: 3, fill: fill,
      });
    }
    // default incl. work/reconstructed (beats)
    return svgEl(doc, "circle", { cx: x, cy: y, r: 4, fill: fill });
  }

  function drawMarkers(svg, layout, state) {
    if (!svg || !layout) return;
    state = state || {};
    var doc = svg.ownerDocument;
    var selectedId = state.selectedId || null;
    var tracks = layout.tracks || [];

    tracks.forEach(function (track) {
      (track.rows || []).forEach(function (row) {
        (row.items || []).forEach(function (placed) {
          var item = placed.item;
          if (!item) return;
          var x = num(placed.x);
          var y = num(placed.y);

          var group = svgEl(doc, "g", { "class": "arc-item-group" });

          var shape = markerShape(doc, item, x, y);

          // Base + status classes.
          var cls = "arc-marker arc-status-" + (item.status || "future");
          if (item.blocked) cls += " arc-blocked";
          // Preserve any shape-specific class (e.g. arc-goal) set in markerShape.
          var existing = shape.getAttribute("class");
          shape.setAttribute("class", existing ? existing + " " + cls : cls);

          // Interaction/accessibility attributes live on the shape.
          shape.setAttribute("data-arc-item", item.id == null ? "" : String(item.id));
          shape.setAttribute("tabindex", "0");
          shape.setAttribute("role", "button");
          var code = item.code == null ? "" : String(item.code);
          var lbl = item.label == null ? "" : String(item.label);
          shape.setAttribute("aria-label", code + " — " + lbl);

          // Blocked accent: red stroke regardless of fill.
          if (item.blocked) {
            shape.setAttribute("stroke", BLOCKED_RED);
            shape.setAttribute("stroke-width", "1.5");
          }

          // Selection hook (class only; controller owns state).
          if (selectedId && item.id === selectedId) {
            group.setAttribute("class", "arc-item-group arc-is-selected");
          }

          group.appendChild(shape);
          svg.appendChild(group);
        });
      });
    });
  }

  // ---- exports --------------------------------------------------------------

  var api = {
    svgEl: svgEl,
    statusFill: statusFill,
    drawAxis: drawAxis,
    drawTracks: drawTracks,
    drawMarkers: drawMarkers,
  };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (root) root.CivArcDraw = api;
})(typeof window !== "undefined" ? window : null);
