(function () {
  "use strict";

  var SVG_NS = "http://www.w3.org/2000/svg";
  var BASE_WIDTH = 1680;
  var WIDTH = BASE_WIDTH;
  var HEIGHT = 420;
  // Left gutter reserved for lane labels — the plot (nodes/now-line/axis) starts
  // after it. Right margin keeps the last tick + axis label off the edge.
  var LANE_GUTTER = 162;
  var MARGIN_RIGHT = 40;
  var FULL_PAGE = "civilization-arc.html";

  // ── Within-lane sub-row packing geometry ──────────────────────────────────
  // Each lane stacks its items into as many horizontal sub-rows as collision
  // avoidance needs. A node occupies a footprint = max(shapeWidth, textWidth)+GAP
  // centred on its mapX(seq); greedy interval packing assigns sub-rows.
  var ROW_H = 28;        // vertical pitch of one sub-row
  var LANE_PAD = 9;      // padding top+bottom inside a lane band
  var LANE_GAP = 6;      // gap between adjacent lane bands
  var NODE_GAP = 8;      // horizontal breathing room added to each footprint
  var CHAR_PX = 6.6;     // approx px per char of the small mono node font
  var CHART_TOP = 60;    // y where the first lane band begins
  var AXIS_PAD = 26;     // gap between last lane and the axis line
  var BOTTOM_PAD = 30;   // margin below the axis label

  // Total content height of the current draw (lanes + axis + margins). Computed
  // by computeLanes() from the packed sub-rows; drives the SVG height/viewBox so
  // variable-height lanes always fit and the page scrolls when tall.
  var contentHeight = HEIGHT;

  var state = {
    expanded: false,
    standalone: false,
    selected: null,
    viewBox: { x: 0, y: 42, w: BASE_WIDTH, h: 190 },
    tooltipSticky: false,
    dragging: false,
    dragLast: null,
    dragMoved: false,
    keyHandler: null,
    // Default OFF: nodes show their short code (item.code) so the clean view is
    // readable without overlap. Toggling "full labels" on shows the fuller label.
    denseLabels: false,
    viewDomain: null,
    detailsOpen: true,
    // Dimension the swimlanes are grouped by. Foundation pass ships "status";
    // a later pass adds a grouping toggle (repo|sprint|gate) — the seam is here.
    grouping: "status",
  };

  // Lane geometry for the current draw, keyed by lane name →
  //   {top, height, bottom, center, subRows}. Variable height per lane (depends
  // on how many sub-rows its items pack into). Rebuilt every drawSvg() by
  // computeLanes(); read by drawLanes()/laneCenterFor().
  var laneGeom = {};
  // Per-item y position for the current draw, keyed by item id. Items in the
  // same lane sit on different sub-rows, so the y is item-specific (not just the
  // lane center). Read by drawItems()/drawDependencies().
  var itemY = {};
  // Bottom y of the last lane band for the current draw (axis sits below it).
  var lanesBottom = CHART_TOP;

  function ready(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn);
      return;
    }
    fn();
  }

  function svgEl(name, attrs) {
    var el = document.createElementNS(SVG_NS, name);
    Object.keys(attrs || {}).forEach(function (key) {
      if (attrs[key] !== null && attrs[key] !== undefined) {
        el.setAttribute(key, String(attrs[key]));
      }
    });
    return el;
  }

  function htmlEl(name, className, text) {
    var el = document.createElement(name);
    if (className) el.className = className;
    if (text !== undefined && text !== null) el.textContent = text;
    return el;
  }

  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  function currentDomain(data) {
    if (state.viewDomain) return state.viewDomain;
    return data.domain;
  }

  function fullDomainSpan(data) {
    return data.domain.end - data.domain.start;
  }

  // Left/right edges of the plot area (after the lane-label gutter). The axis +
  // lane bands span this; lane labels live left of plotLeft().
  function plotLeft() {
    return LANE_GUTTER;
  }
  function plotRight() {
    return WIDTH - MARGIN_RIGHT;
  }
  // Inset where the FIRST/LAST nodes are centred, so a node at the domain edge
  // (its shape + text extends ~half its footprint each side) clears the gutter
  // on the left and the SVG edge on the right instead of bleeding into them.
  var PLOT_INSET_L = 34;
  var PLOT_INSET_R = 30;

  function mapX(data, x) {
    var domain = currentDomain(data);
    var span = domain.end - domain.start;
    var left = plotLeft() + PLOT_INSET_L;
    var right = plotRight() - PLOT_INSET_R;
    return left + ((x - domain.start) / span) * (right - left);
  }

  // Human label for a lane name under the current grouping dimension.
  function laneLabelFor(data, laneName) {
    if (state.grouping === "sprint") {
      var sprint = (data.sprints || []).find(function (s) {
        return s.id === laneName;
      });
      if (sprint) return sprint.label;
    }
    return String(laneName);
  }

  // Center Y of a lane, by lane name. Falls back to the chart top when geometry
  // has not been built (defensive — should not happen at draw time).
  function laneCenterFor(laneName) {
    var g = laneGeom[laneName];
    return g ? g.center : CHART_TOP;
  }

  // Y of a specific item (its sub-row center). Falls back to its lane center,
  // then the chart top, when not yet placed.
  function itemYFor(item) {
    if (item && item.id && typeof itemY[item.id] === "number") return itemY[item.id];
    return laneCenterFor(itemLaneName(item || {}));
  }

  // Bottom Y of the lane stack — where the axis sits below.
  function laneAreaBottom() {
    return lanesBottom;
  }

  // Top Y of the lane stack — where the "now" line / first band begins.
  function laneAreaTop() {
    return CHART_TOP;
  }

  // Vertical extent of the drawn content. Lanes now have variable height, so the
  // view always spans the full computed content (no vertical clipping/zoom); the
  // SVG element grows to fit and the page scrolls when tall. Horizontal zoom/pan
  // still works via the domain in mapX (the viewBox stays full-width).
  function currentViewHeight() {
    return Math.max(HEIGHT, Math.round(contentHeight));
  }

  function currentViewY() {
    return 0;
  }

  function defaultViewBox() {
    return { x: 0, y: 0, w: WIDTH, h: currentViewHeight() };
  }

  // Virtual x-units track CSS px 1:1 so node footprints used by the packer are
  // pixel-faithful. WIDTH = the SVG element's rendered width. In jsdom there is
  // no layout (rect is 0), so WIDTH stays BASE_WIDTH — deterministic for tests.
  function syncVirtualWidth(svg) {
    var rect = svg.getBoundingClientRect();
    if (!rect.width) return;
    var nextWidth = Math.max(900, Math.round(rect.width));
    if (Math.abs(nextWidth - WIDTH) > 4) {
      WIDTH = nextWidth;
      state.viewBox = defaultViewBox();
    }
  }

  // Size the SVG to its content. viewBox spans 0..WIDTH × 0..contentHeight; the
  // element height is set to contentHeight px so the drawing renders 1:1 (WIDTH
  // == element px width) without squashing, and the page scrolls when tall.
  function setViewBox(svg) {
    var h = currentViewHeight();
    state.viewBox.x = 0;
    state.viewBox.y = 0;
    state.viewBox.w = WIDTH;
    state.viewBox.h = h;
    svg.setAttribute("viewBox", [0, 0, WIDTH, h].join(" "));
    svg.style.height = h + "px";
    updateZoomReadout(svg);
  }

  function setDomainView(root, svg, data, start, end) {
    var fullStart = data.domain.start;
    var fullEnd = data.domain.end;
    var fullSpan = fullDomainSpan(data);
    var span = clamp(end - start, 0.32, fullSpan);
    var nextStart = clamp(start, fullStart, fullEnd - span);
    var nextEnd = nextStart + span;
    if (nextStart <= fullStart + 0.001 && nextEnd >= fullEnd - 0.001) {
      state.viewDomain = null;
    } else {
      state.viewDomain = { start: nextStart, end: nextEnd };
    }
    drawSvg(root, svg, data);
  }

  function zoomSvg(root, svg, data, anchorRatio, factor) {
    var domain = currentDomain(data);
    var span = domain.end - domain.start;
    var nextSpan = clamp(span * factor, 0.36, fullDomainSpan(data));
    var anchor = domain.start + span * anchorRatio;
    setDomainView(root, svg, data, anchor - nextSpan * anchorRatio, anchor + nextSpan * (1 - anchorRatio));
  }

  function focusRange(root, svg, data, start, end, minimumSpan) {
    var itemSpan = Math.max(0.01, end - start);
    var paddedSpan = Math.max(minimumSpan || 0.7, itemSpan * 1.16);
    var center = (start + end) / 2;
    setDomainView(root, svg, data, center - paddedSpan / 2, center + paddedSpan / 2);
  }

  function focusPoint(root, svg, data, x) {
    focusRange(root, svg, data, x - 0.08, x + 0.08, 0.9);
  }

  function itemTitle(item) {
    return item.label || item.title || item.code || item.id;
  }

  // Short label for an in-chart node so text stays inside its shape.
  function shortLabel(text, maxChars) {
    var s = String(text == null ? "" : text);
    var limit = maxChars || 14;
    if (s.length <= limit) return s;
    return s.slice(0, Math.max(1, limit - 1)).replace(/[\s.,;:]+$/, "") + "…";
  }

  function zoomLabel() {
    var data = window.CIVILIZATION_ARC_DATA;
    var domain = data && data.domain ? currentDomain(data) : null;
    var zoom = domain ? fullDomainSpan(data) / (domain.end - domain.start) : 1;
    if (!data || !data.domain) return "zoom " + zoom.toFixed(2) + "x";
    var start = domain.start;
    var end = domain.end;
    return "zoom " + zoom.toFixed(2) + "x · seq " + start.toFixed(1) + "-" + end.toFixed(1);
  }

  function updateZoomReadout(context) {
    var root = context && context.closest ? context.closest(".civilization-arc-nav") : context;
    if (!root) return;
    var readout = root.querySelector("[data-arc-zoom-readout]");
    if (readout) readout.textContent = zoomLabel();
    root.setAttribute("data-zoomed", state.viewDomain ? "true" : "false");
  }

  function isEditableTarget(target) {
    return Boolean(
      target &&
        (target.isContentEditable ||
          /^(INPUT|TEXTAREA|SELECT)$/.test(target.tagName || ""))
    );
  }

  function itemMeta(item, kind) {
    // Items carry their own type + status; describe them uniformly.
    var type = item.type || kind || "item";
    var bits = [type];
    if (item.status) bits.push(item.status);
    if (item.blocked) bits.push("blocked");
    return bits.join(" / ");
  }

  // Which lane the item lands in, for the active grouping dimension.
  // Mirrors CivOntology.laneOf so the panel agrees with the chart.
  function itemLaneName(item) {
    var dim = state.grouping;
    if (dim === "status") return item.blocked ? "blocked" : item.status;
    if (dim === "repo") return (item.repo && item.repo[0]) || "(none)";
    if (dim === "sprint") return item.sprint || "(none)";
    if (dim === "gate") return item.gate || "(ungated)";
    return "(none)";
  }

  function itemSwimlane(data, item) {
    return laneLabelFor(data, itemLaneName(item));
  }

  function isSelected(item, kind) {
    return Boolean(state.selected && state.selected.item === item && state.selected.kind === kind);
  }

  function fitFull(root, svg, data) {
    state.viewDomain = null;
    drawSvg(root, svg, data);
  }

  function closeDetails(root, svg, data) {
    state.selected = null;
    state.detailsOpen = false;
    forceHideTooltip(root);
    drawSvg(root, svg, data);
    updateSelectedPanel(root, svg, data);
  }

  function collectExportCss() {
    var css = "";
    Array.prototype.forEach.call(document.styleSheets || [], function (sheet) {
      var rules;
      try {
        rules = sheet.cssRules;
      } catch (err) {
        return;
      }
      Array.prototype.forEach.call(rules || [], function (rule) {
        if (rule.cssText && /\.arc-|arc-|civilization-arc-nav/.test(rule.cssText)) {
          css += rule.cssText + "\n";
        }
      });
    });
    return css;
  }

  function exportSvg(svg) {
    var clone = svg.cloneNode(true);
    clone.setAttribute("xmlns", SVG_NS);
    var rect = svg.getBoundingClientRect();
    if (rect.width && rect.height) {
      clone.setAttribute("width", Math.round(rect.width));
      clone.setAttribute("height", Math.round(rect.height));
    }
    var nav = svg.closest(".civilization-arc-nav");
    if (nav) {
      var computed = getComputedStyle(nav);
      [
        "--arc-bg",
        "--arc-bg-2",
        "--arc-panel",
        "--arc-panel-2",
        "--arc-line",
        "--arc-text",
        "--arc-muted",
        "--arc-faint",
        "--arc-blue",
        "--arc-cyan",
        "--arc-green",
        "--arc-gold",
        "--arc-orange",
        "--arc-red",
        "--arc-violet",
        "--arc-magenta",
        "--mono",
        "--serif",
      ].forEach(function (name) {
        clone.style.setProperty(name, computed.getPropertyValue(name));
      });
    }
    var styleText = collectExportCss();
    if (styleText) {
      var style = svgEl("style");
      style.textContent = styleText;
      clone.insertBefore(style, clone.firstChild);
    }
    var blob = new Blob([new XMLSerializer().serializeToString(clone)], { type: "image/svg+xml" });
    var link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "civilization-arc.svg";
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(function () {
      URL.revokeObjectURL(link.href);
    }, 0);
  }

  function wrapText(text, maxChars, maxLines) {
    var words = String(text).split(/\s+/).filter(Boolean);
    var lines = [];
    var current = "";
    words.forEach(function (word) {
      var next = current ? current + " " + word : word;
      if (next.length <= maxChars || !current) {
        current = next;
        return;
      }
      lines.push(current);
      current = word;
    });
    if (current) lines.push(current);
    if (lines.length > maxLines) {
      var kept = lines.slice(0, maxLines);
      kept[maxLines - 1] = kept[maxLines - 1].replace(/[.,;:\s]+$/, "") + "…";
      return kept;
    }
    return lines;
  }

  function showTooltip(root, item, kind, event, sticky) {
    var tip = root.querySelector(".arc-tooltip");
    if (!tip) return;
    state.tooltipSticky = Boolean(sticky);
    tip.hidden = false;
    tip.replaceChildren();

    var eyebrow = htmlEl("div", "arc-tooltip-eyebrow", itemMeta(item, kind));
    var title = htmlEl("strong", "", itemTitle(item));
    tip.append(eyebrow, title);

    if (item.blocked && item.blocked_reason) {
      tip.appendChild(htmlEl("span", "arc-tooltip-code", "blocked: " + item.blocked_reason));
    }
    if (item.note) {
      tip.appendChild(htmlEl("span", "arc-tooltip-note", item.note));
    }

    if (item.href) {
      var link = htmlEl("a", "arc-tooltip-link", "Open article");
      link.href = item.href;
      tip.appendChild(link);
    }

    positionTooltip(root, tip, event);
  }

  function positionTooltip(root, tip, event) {
    var box = root.getBoundingClientRect();
    var hasPoint = event && typeof event.clientX === "number" && typeof event.clientY === "number";
    var x = hasPoint ? event.clientX - box.left + 14 : 24;
    var y = hasPoint ? event.clientY - box.top + 14 : 58;
    var maxX = Math.max(12, box.width - 260);
    tip.style.left = clamp(x, 12, maxX) + "px";
    tip.style.top = Math.max(12, y) + "px";
  }

  function hideTooltip(root) {
    if (state.tooltipSticky) return;
    var tip = root.querySelector(".arc-tooltip");
    if (tip) tip.hidden = true;
  }

  function forceHideTooltip(root) {
    state.tooltipSticky = false;
    var tip = root.querySelector(".arc-tooltip");
    if (tip) tip.hidden = true;
  }

  function bindInteractive(root, svg, data, el, item, kind) {
    el.setAttribute("data-arc-item", "");
    el.setAttribute("tabindex", "0");
    el.setAttribute("role", "button");
    el.setAttribute("aria-label", itemTitle(item));

    el.addEventListener("mouseenter", function (event) {
      showTooltip(root, item, kind, event, false);
    });
    el.addEventListener("mousemove", function (event) {
      var tip = root.querySelector(".arc-tooltip");
      if (tip && !tip.hidden && !state.tooltipSticky) positionTooltip(root, tip, event);
    });
    el.addEventListener("mouseleave", function () {
      hideTooltip(root);
    });
    el.addEventListener("focus", function (event) {
      showTooltip(root, item, kind, event, true);
    });
    el.addEventListener("blur", function () {
      state.tooltipSticky = false;
      hideTooltip(root);
    });
    el.addEventListener("click", function (event) {
      event.preventDefault();
      state.selected = { kind: kind, item: item };
      state.detailsOpen = true;
      forceHideTooltip(root);
      if (typeof item.seq === "number") focusPoint(root, svg, data, item.seq);
      else drawSvg(root, svg, data);
      updateSelectedPanel(root, svg, data);
      forceHideTooltip(root);
    });
    el.addEventListener("keydown", function (event) {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        el.dispatchEvent(new MouseEvent("click", { bubbles: true, clientX: 24, clientY: 24 }));
      }
    });
  }

  function addDefs(svg) {
    var defs = svgEl("defs");

    var hatch = svgEl("pattern", {
      id: "arc-hatch",
      patternUnits: "userSpaceOnUse",
      width: 10,
      height: 10,
      patternTransform: "rotate(45)",
    });
    hatch.appendChild(svgEl("path", { d: "M 0 0 L 0 10", class: "arc-hatch-line" }));

    var dots = svgEl("pattern", {
      id: "arc-dots",
      patternUnits: "userSpaceOnUse",
      width: 12,
      height: 12,
    });
    dots.appendChild(svgEl("circle", { cx: 3, cy: 3, r: 1.5, class: "arc-dot" }));

    var arrow = svgEl("marker", {
      id: "arc-arrow",
      viewBox: "0 0 10 10",
      refX: 8,
      refY: 5,
      markerWidth: 6,
      markerHeight: 6,
      orient: "auto-start-reverse",
    });
    arrow.appendChild(svgEl("path", { d: "M 0 0 L 10 5 L 0 10 z", class: "arc-arrow-head" }));

    var criticalArrow = svgEl("marker", {
      id: "arc-critical-arrow",
      viewBox: "0 0 10 10",
      refX: 8,
      refY: 5,
      markerWidth: 7,
      markerHeight: 7,
      orient: "auto",
    });
    criticalArrow.appendChild(svgEl("path", { d: "M 0 0 L 10 5 L 0 10 z", class: "arc-critical-arrow-head" }));

    defs.append(hatch, dots, arrow, criticalArrow);
    svg.appendChild(defs);
  }

  function addLabel(parent, text, x, y, className, maxLines) {
    var label = svgEl("text", {
      x: x,
      y: y,
      class: className,
      "text-anchor": "middle",
    });
    var parts = String(text).split(" ");
    var lines = [];
    if (parts.length <= 1 || maxLines === 1) {
      lines = [text];
    } else {
      var midpoint = Math.ceil(parts.length / 2);
      lines = [parts.slice(0, midpoint).join(" "), parts.slice(midpoint).join(" ")];
    }
    lines.slice(0, maxLines || 2).forEach(function (line, index) {
      var tspan = svgEl("tspan", {
        x: x,
        dy: index === 0 ? 0 : 15,
      });
      tspan.textContent = line;
      label.appendChild(tspan);
    });
    parent.appendChild(label);
  }

  function addWrappedLabel(parent, text, x, y, className, maxChars, maxLines, lineHeight) {
    var lines = wrapText(text, Math.max(6, maxChars), maxLines || 3);
    var label = svgEl("text", {
      x: x,
      y: y - ((lines.length - 1) * (lineHeight || 14)) / 2,
      class: className,
      "text-anchor": "middle",
    });
    lines.forEach(function (line, index) {
      var tspan = svgEl("tspan", {
        x: x,
        dy: index === 0 ? 0 : lineHeight || 14,
      });
      tspan.textContent = line;
      label.appendChild(tspan);
    });
    parent.appendChild(label);
  }

  // ------------------------------------------------------------------
  // Lanes — dynamic swimlanes built from CivOntology.groupBy(items, grouping).
  // Replaces the old fixed swimlanes[] + phases-as-blocks. Band geometry is
  // computed by dividing the lane area by the lane count; each lane gets a
  // center y + height recorded in laneGeom for the item-draw step to read.
  // ------------------------------------------------------------------
  // Horizontal footprint (px) of an item's drawn node at its mapX, including the
  // node shape, its visible text (code or truncated label per the labels toggle),
  // any blocker-overlay bulge, and a small gap. Used by the sub-row packer.
  function nodeShapeHalfWidth(item) {
    // Half-widths mirror drawItemShape/drawBlockerOverlay.
    if (item.type === "gate") return item.blocked ? 16 : 12;
    if (item.type === "goal") return item.blocked ? 19 : 15;
    if (item.type === "decision") return item.blocked ? 15 : 11;
    return item.blocked ? 24 : 20; // rounded rect (work/order/etc.)
  }
  function itemNodeText(item) {
    return state.denseLabels
      ? shortLabel(item.label, 22)
      : (item.code || shortLabel(item.label, 6));
  }
  function itemFootprint(item) {
    var textW = String(itemNodeText(item)).length * CHAR_PX;
    var shapeW = nodeShapeHalfWidth(item) * 2;
    return Math.max(shapeW, textW) + NODE_GAP;
  }

  // Greedy interval packing within a lane: sort items by seq, then place each in
  // the FIRST sub-row whose last placed item's right edge is at/left of this
  // item's left edge; otherwise start a new sub-row. Returns the assignment and
  // sub-row count. Pure (no DOM, no geometry) so it is unit-testable in jsdom.
  function packLane(data, laneItems) {
    var sorted = laneItems.slice().sort(function (a, b) {
      return a.seq - b.seq;
    });
    var rowRight = []; // right-edge x of the last item placed in each sub-row
    var assign = [];   // { item, subRow, x, left, right }
    sorted.forEach(function (item) {
      var x = mapX(data, item.seq);
      var half = itemFootprint(item) / 2;
      var left = x - half;
      var right = x + half;
      var row = -1;
      for (var i = 0; i < rowRight.length; i++) {
        if (rowRight[i] <= left + 0.01) {
          row = i;
          break;
        }
      }
      if (row === -1) {
        row = rowRight.length;
        rowRight.push(right);
      } else {
        rowRight[row] = right;
      }
      assign.push({ item: item, subRow: row, x: x, left: left, right: right });
    });
    return { assignments: assign, subRows: Math.max(1, rowRight.length) };
  }

  // Build per-lane geometry by stacking lanes top-to-bottom, each tall enough for
  // its packed sub-rows. Records each item's y (sub-row center) in itemY, the
  // lane bands in laneGeom, the stack bottom in lanesBottom, and the total
  // content height (lanes + axis + margins) in contentHeight.
  function computeLanes(data) {
    var O = window.CivOntology;
    var groups = O && O.groupBy ? O.groupBy(data.items || [], state.grouping) : [];
    laneGeom = {};
    itemY = {};
    var cursor = laneAreaTop();
    groups.forEach(function (g, index) {
      var packed = packLane(data, g.items);
      var height = packed.subRows * ROW_H + LANE_PAD * 2;
      var top = cursor;
      laneGeom[g.lane] = {
        top: top,
        height: height,
        bottom: top + height,
        center: top + height / 2,
        subRows: packed.subRows,
        index: index,
      };
      packed.assignments.forEach(function (a) {
        itemY[a.item.id] = top + LANE_PAD + a.subRow * ROW_H + ROW_H / 2;
      });
      cursor = top + height + LANE_GAP;
    });
    lanesBottom = groups.length ? cursor - LANE_GAP : laneAreaTop();
    // Axis line + label sit below the lane stack; pad the bottom for scroll room.
    contentHeight = lanesBottom + AXIS_PAD + BOTTOM_PAD;
    return groups;
  }

  // Approximate how many gutter chars fit, so labels truncate with … instead of
  // spilling into the plot. Conservative (the gutter label font is ~11px mono).
  function gutterMaxChars() {
    return Math.max(6, Math.floor((LANE_GUTTER - 24) / 7));
  }

  function drawLanes(svg, data, groups) {
    var group = svgEl("g", { class: "arc-swimlanes" });
    var labelRight = plotLeft() - 12; // right-align labels just inside the gutter
    groups.forEach(function (g, index) {
      var geom = laneGeom[g.lane];
      if (!geom) return;
      var laneGroup = svgEl("g", { class: "arc-swimlane arc-swimlane-" + statusClass(g.lane) });
      // Striped full-width band spanning the whole (variable-height) lane.
      laneGroup.appendChild(
        svgEl("rect", {
          x: 12,
          y: geom.top,
          width: WIDTH - 24,
          height: Math.max(1, geom.height),
          rx: 7,
          class: "arc-swimlane-band arc-swimlane-band-" + (index % 2 === 0 ? "even" : "odd"),
        })
      );
      // Thin separator at the lane's bottom edge for vertical rhythm.
      laneGroup.appendChild(
        svgEl("line", {
          x1: 12,
          y1: geom.bottom,
          x2: WIDTH - 12,
          y2: geom.bottom,
          class: "arc-swimlane-sep",
        })
      );
      // Lane label in the gutter: right-aligned, vertically centred, truncated
      // with … + a <title> for the full text. Lives left of the plot edge.
      var full = laneLabelFor(data, g.lane);
      var label = svgEl("text", {
        x: labelRight,
        y: geom.center,
        "text-anchor": "end",
        "dominant-baseline": "middle",
        class: "arc-swimlane-label",
      });
      label.textContent = shortLabel(full, gutterMaxChars());
      var title = svgEl("title");
      title.textContent = full;
      label.appendChild(title);
      laneGroup.appendChild(label);
      group.appendChild(laneGroup);
    });
    svg.appendChild(group);
  }

  // Dependency edges, scoped to the current selection. Hidden by default:
  // when nothing is selected, visibleDeps([]) returns no edges and we draw
  // nothing. When an item is selected, draw only its in/out edges, positioning
  // each endpoint with the SAME mapX(seq) / lane-center used by the item nodes
  // for the current grouping, so arrows track the chart as lanes regroup.
  function drawDependencies(svg, data) {
    var selId =
      state.selected && state.selected.kind === "item" && state.selected.item
        ? state.selected.item.id
        : null;
    if (!selId) return;
    var O = window.CivOntology;
    if (!O || !O.visibleDeps) return;
    var edges = O.visibleDeps(data.items || [], selId);
    if (!edges.length) return;

    var byId = {};
    (data.items || []).forEach(function (it) {
      if (it && it.id) byId[it.id] = it;
    });

    var group = svgEl("g", { class: "arc-dependencies" });
    edges.forEach(function (edge) {
      var from = byId[edge.from];
      var to = byId[edge.to];
      if (!from || !to) return;
      var sx = mapX(data, from.seq);
      var sy = itemYFor(from);
      var ex = mapX(data, to.seq);
      var ey = itemYFor(to);
      var mid = sx + (ex - sx) / 2;
      group.appendChild(
        svgEl("path", {
          d: ["M", sx, sy, "C", mid, sy, mid, ey, ex, ey].join(" "),
          class: "arc-dependency",
          "marker-end": "url(#arc-arrow)",
        })
      );
    });
    svg.appendChild(group);
  }

  // Fill/opacity per status, layered over the shared .arc-marker stroke + the
  // group's focus/selection treatment. Inline because the new node classes have
  // no CSS yet (styling is deferred — spec §4 is correctness-only).
  function statusFill(status) {
    switch (status) {
      case "done":
        return { fill: "rgba(123,216,143,.55)", stroke: "var(--arc-green)", opacity: 1 };
      case "active":
        return { fill: "rgba(231,191,100,.6)", stroke: "var(--arc-gold)", opacity: 1 };
      case "planned":
        return { fill: "rgba(108,182,255,.32)", stroke: "var(--arc-blue)", opacity: 0.95 };
      case "future":
        return { fill: "rgba(155,167,180,.2)", stroke: "rgba(155,167,180,.6)", opacity: 0.7 };
      default:
        return { fill: "rgba(108,182,255,.32)", stroke: "var(--arc-blue)", opacity: 0.95 };
    }
  }

  // Shape by item.type: gate→diamond, decision→circle, goal→larger circle,
  // everything else (incl. work)→rounded rect. Returns the primary shape el.
  function drawItemShape(group, item, x, y) {
    var style = statusFill(item.status);
    var common = {
      class: "arc-marker arc-item arc-item-" + statusClass(item.status),
      fill: style.fill,
      stroke: style.stroke,
      opacity: style.opacity,
    };
    var type = item.type;
    if (type === "gate") {
      var d = ["M", x, y - 12, "L", x + 12, y, "L", x, y + 12, "L", x - 12, y, "Z"].join(" ");
      var diamond = svgEl("path", Object.assign({ d: d }, common));
      group.appendChild(diamond);
      return diamond;
    }
    if (type === "decision") {
      var circle = svgEl("circle", Object.assign({ cx: x, cy: y, r: 11 }, common));
      group.appendChild(circle);
      return circle;
    }
    if (type === "goal") {
      // Distinct, slightly larger node so the north-star reads differently.
      var goal = svgEl("circle", Object.assign({ cx: x, cy: y, r: 15 }, common, {
        class: "arc-marker arc-item arc-item-goal arc-item-" + statusClass(item.status),
        "stroke-width": 2.4,
      }));
      group.appendChild(goal);
      return goal;
    }
    var rect = svgEl("rect", Object.assign(
      { x: x - 20, y: y - 11, width: 40, height: 22, rx: 4 },
      common
    ));
    group.appendChild(rect);
    return rect;
  }

  // Red ring overlay for blocked items. Sized to sit just outside the node.
  function drawBlockerOverlay(group, item, x, y) {
    if (item.type === "gate") {
      group.appendChild(
        svgEl("path", {
          d: ["M", x, y - 16, "L", x + 16, y, "L", x, y + 16, "L", x - 16, y, "Z"].join(" "),
          class: "arc-item-blocked",
          fill: "none",
          stroke: "var(--arc-red)",
          "stroke-width": 2.4,
          "vector-effect": "non-scaling-stroke",
        })
      );
      return;
    }
    if (item.type === "decision" || item.type === "goal") {
      group.appendChild(
        svgEl("circle", {
          cx: x,
          cy: y,
          r: item.type === "goal" ? 19 : 15,
          class: "arc-item-blocked",
          fill: "none",
          stroke: "var(--arc-red)",
          "stroke-width": 2.4,
          "vector-effect": "non-scaling-stroke",
        })
      );
      return;
    }
    group.appendChild(
      svgEl("rect", {
        x: x - 24,
        y: y - 15,
        width: 48,
        height: 30,
        rx: 6,
        class: "arc-item-blocked",
        fill: "none",
        stroke: "var(--arc-red)",
        "stroke-width": 2.4,
        "vector-effect": "non-scaling-stroke",
      })
    );
  }

  // Single item-draw step (replaces drawMarkers/drawGates/drawDecisions).
  // Iterates the groupBy result so each item lands at its own lane's center —
  // guaranteeing lane/geometry consistency with drawLanes.
  function drawItems(root, svg, data, groups) {
    var group = svgEl("g", { class: "arc-items" });
    groups.forEach(function (g) {
      g.items.forEach(function (item) {
        var x = mapX(data, item.seq);
        // y is the item's packed sub-row center (collision-avoided), not just the
        // lane center — items in the same lane stack onto separate sub-rows.
        var y = itemYFor(item);
        var itemGroup = svgEl("g", {
          class:
            "arc-marker-group arc-item-group arc-item-type-" +
            statusClass(item.type) +
            (item.blocked ? " arc-item-is-blocked" : "") +
            (isSelected(item, "item") ? " arc-is-selected" : ""),
        });
        drawItemShape(itemGroup, item, x, y);
        if (item.blocked) drawBlockerOverlay(itemGroup, item, x, y);
        // Node text depends on the labels toggle:
        //   default (denseLabels false): the short code (item.code) — readable, no overlap.
        //   denseLabels true: the fuller (truncated) label — the dense view.
        // The full label always lives in the tooltip + selected panel.
        addLabel(itemGroup, itemNodeText(item), x, y + 4, "arc-marker-label arc-item-label", 1);
        bindInteractive(root, svg, data, itemGroup, item, "item");
        group.appendChild(itemGroup);
      });
    });
    svg.appendChild(group);
  }

  // Vertical "now" line at the derived frontier, labelled by the frontier item.
  function drawCurrent(svg, data) {
    var O = window.CivOntology;
    if (!O || !O.deriveNow) return;
    var items = data.items || [];
    var nowSeq = O.deriveNow(items);
    if (typeof nowSeq !== "number" || !isFinite(nowSeq)) return;
    var x = mapX(data, nowSeq);

    // Frontier item: the done/active item sitting exactly at nowSeq.
    var frontier = null;
    items.forEach(function (it) {
      if (!it) return;
      if ((it.status === "done" || it.status === "active") && it.seq === nowSeq) frontier = it;
    });
    var labelText = frontier ? "Now · " + shortLabel(frontier.label, 22) : "Now";

    var group = svgEl("g", { class: "arc-current-focus" });
    var top = laneAreaTop() - 14;
    var bottom = laneAreaBottom() + 12;
    group.appendChild(svgEl("line", { x1: x, y1: top, x2: x, y2: bottom, class: "arc-current-line" }));
    group.appendChild(svgEl("circle", { cx: x, cy: top, r: 7, class: "arc-current-dot" }));
    var labelAttrs = { x: x + 13, y: top + 3, class: "arc-current-label" };
    // Flip the label to the left when the now-line is in the right third of the
    // plot (gutter-aware) so it never runs off the edge.
    if (x > plotLeft() + (plotRight() - plotLeft()) * 0.68) {
      labelAttrs.x = x - 13;
      labelAttrs["text-anchor"] = "end";
    }
    var label = svgEl("text", labelAttrs);
    label.textContent = labelText;
    group.appendChild(label);
    svg.appendChild(group);
  }

  // Axis ticks derived from data.domain (integer steps), replacing phases[].start.
  function drawAxis(svg, data) {
    var group = svgEl("g", { class: "arc-axis" });
    var y = laneAreaBottom() + AXIS_PAD;
    group.appendChild(svgEl("line", { x1: plotLeft(), y1: y, x2: plotRight(), y2: y }));
    var start = Math.ceil(data.domain.start);
    var end = Math.floor(data.domain.end);
    for (var tick = start; tick <= end; tick++) {
      var x = mapX(data, tick);
      group.appendChild(svgEl("line", { x1: x, y1: y - 10, x2: x, y2: y + 10 }));
    }
    var label = svgEl("text", {
      x: plotRight(),
      y: y - 15,
      class: "arc-axis-label",
      "text-anchor": "end",
    });
    label.textContent = "Development sequence";
    group.appendChild(label);
    svg.appendChild(group);
  }

  function drawSvg(root, svg, data) {
    root.setAttribute("data-has-selection", state.selected ? "true" : "false");
    root.setAttribute("data-dense-labels", state.denseLabels ? "true" : "false");
    root.setAttribute("data-details-open", state.detailsOpen ? "true" : "false");
    svg.replaceChildren();
    var svgTitle = svgEl("title", { id: "civilization-arc-title" });
    svgTitle.textContent = data.title;
    var svgDesc = svgEl("desc", { id: "civilization-arc-desc" });
    svgDesc.textContent =
      "Interactive SVG timeline of civilization arc items on status swimlanes, with a derived now line and blocker overlays.";
    svg.append(svgTitle, svgDesc);
    addDefs(svg);
    // Build lane geometry first so the map background + viewBox can size to the
    // full (variable-height) content. Then draw map-bg → lanes → now-line →
    // items → axis. Collapsed and expanded views render the same packed lanes.
    var groups = computeLanes(data);
    svg.appendChild(
      svgEl("rect", {
        x: 8,
        y: 8,
        width: WIDTH - 16,
        height: Math.max(HEIGHT, Math.round(contentHeight)) - 16,
        rx: 12,
        class: "arc-map-bg",
      })
    );
    drawLanes(svg, data, groups);
    drawCurrent(svg, data);
    drawAxis(svg, data);
    drawItems(root, svg, data, groups);
    // Dependency edges overlay the item nodes; selection-scoped (see drawDependencies).
    drawDependencies(svg, data);
    setViewBox(svg);
  }

  function buildLegend(data) {
    var list = htmlEl("ul", "arc-legend-list");
    data.legendItems.forEach(function (item) {
      var li = htmlEl("li", "arc-legend-item");
      li.appendChild(htmlEl("span", "arc-legend-swatch arc-legend-" + item.shape));
      li.appendChild(htmlEl("span", "", item.label));
      list.appendChild(li);
    });
    return list;
  }

  // ------------------------------------------------------------------
  // Code KEY — maps each in-chart short code (item.code) to its full name.
  // This is the legend the default (code) view needs so the codes are
  // decodable. Grouped by category for scannability; compact (small mono
  // font, multi-column grid, truncated labels) so it does not blow out the
  // layout. Built from data.items and appended to the nav root (NOT inside
  // .arc-expanded, which is display:none in the compact default view), so it
  // is visible in the default render.
  // ------------------------------------------------------------------
  function codeKeyGroups(data) {
    var byId = {};
    (data.items || []).forEach(function (it) {
      if (it && it.id) byId[it.id] = it;
    });
    function pick(ids) {
      return ids
        .map(function (id) { return byId[id]; })
        .filter(function (it) { return it && it.code; });
    }
    return [
      { title: "Goal", items: pick(["goal-north-star"]) },
      { title: "Near-term worklist", items: pick(["n1", "n2", "n3", "n4", "n5", "n6", "n7"]) },
      { title: "Delivery route", items: pick(["c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8", "c9", "c10"]) },
      { title: "Gates", items: pick(["v39", "v40", "slice1", "gate-e", "gate-k"]) },
      { title: "Decisions", items: pick(["external-frameworks", "one-civilization", "read-lens", "site-readonly"]) },
      {
        title: "Narrative beats",
        items: pick([
          "origin-signal", "primitive-frame", "civic-ai", "hive-runtime", "civilization-north-star",
          "architecture", "agent-model", "role-catalog", "memory-layer", "prompt-canon",
          "rituals", "governance", "decisions", "artifacts", "dashboards",
          "wiki-layer", "visualization", "human-layer", "repo-layer", "prototype",
          "tests", "demo-validation", "deployment", "operations", "feedback",
          "iteration", "scale", "stewardship",
        ]),
      },
    ];
  }

  function buildCodeKey(data) {
    var key = htmlEl("section", "arc-code-key");
    key.setAttribute("data-arc-code-key", "");
    key.setAttribute("aria-label", "Code key");
    // Inline styling only (no dedicated CSS exists for this element). Uses the
    // arc theme variables so it tracks light/dark and stays compact.
    key.style.cssText =
      "margin-top:12px;padding:12px 14px;border:1px solid rgba(122,142,160,.42);" +
      "border-radius:6px;background:rgba(255,255,255,.035);font:11px/1.4 var(--mono,monospace);";
    key.appendChild(
      (function () {
        var h = htmlEl("h3", "", "Key — code → name");
        h.style.cssText = "margin:0 0 8px;font-size:13px;line-height:1.25;";
        return h;
      })()
    );

    var grid = htmlEl("div", "arc-code-key-grid");
    grid.style.cssText =
      "display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:6px 16px;";

    codeKeyGroups(data).forEach(function (group) {
      if (!group.items.length) return;
      var col = htmlEl("div", "arc-code-key-group");
      col.style.cssText = "min-width:0;";
      var gt = htmlEl("div", "arc-code-key-group-title", group.title);
      gt.style.cssText =
        "color:var(--arc-cyan,#69d2d4);font-weight:700;text-transform:uppercase;" +
        "letter-spacing:.06em;font-size:10px;margin:4px 0 3px;";
      col.appendChild(gt);
      var ul = htmlEl("ul", "arc-code-key-list");
      ul.style.cssText = "list-style:none;margin:0;padding:0;";
      group.items.forEach(function (item) {
        var li = htmlEl("li", "arc-code-key-item");
        li.style.cssText = "display:flex;gap:6px;align-items:baseline;margin:0 0 1px;";
        var code = htmlEl("span", "arc-code-key-code", item.code);
        code.style.cssText =
          "flex:0 0 auto;font-weight:700;color:var(--arc-text,inherit);min-width:54px;";
        var name = htmlEl("span", "arc-code-key-name", shortLabel(item.label, 40));
        name.style.cssText =
          "min-width:0;color:var(--arc-muted,#9aa7b4);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;";
        name.title = item.label;
        li.append(code, name);
        ul.appendChild(li);
      });
      col.appendChild(ul);
      grid.appendChild(col);
    });

    key.appendChild(grid);
    return key;
  }

  function statusClass(status) {
    return String(status || "planned").toLowerCase().replace(/[^a-z0-9-]/g, "-");
  }

  function statusLabel(status) {
    var text = String(status || "planned").replace(/[-_]+/g, " ");
    return text.charAt(0).toUpperCase() + text.slice(1);
  }

  function planLink(item) {
    if (!item.href) return htmlEl("span", "", item.work);
    var link = htmlEl("a", "arc-plan-link", item.work);
    link.href = item.href;
    if (/^https?:\/\//.test(item.href)) {
      link.target = "_blank";
      link.rel = "noopener";
    }
    return link;
  }

  function appendPlanCell(row, label, child, className) {
    var cell = htmlEl("td", className || "");
    cell.setAttribute("data-label", label);
    if (child && child.nodeType) {
      cell.appendChild(child);
    } else {
      cell.textContent = child || "";
    }
    row.appendChild(cell);
  }

  function buildPlanTable(title, items) {
    var section = htmlEl("section", "arc-plan-section");
    section.appendChild(htmlEl("h4", "", title));

    var table = htmlEl("table", "arc-plan-table");
    var thead = htmlEl("thead");
    var headerRow = htmlEl("tr");
    ["Order", "Status", "Work item", "Surface", "Gate", "Finish signal"].forEach(function (label) {
      headerRow.appendChild(htmlEl("th", "", label));
    });
    thead.appendChild(headerRow);

    var body = htmlEl("tbody");
    (items || []).forEach(function (item) {
      var row = htmlEl("tr", "arc-plan-row arc-plan-row-" + statusClass(item.status));
      appendPlanCell(row, "Order", item.order, "arc-plan-order");

      var chip = htmlEl("span", "arc-plan-chip arc-plan-chip-" + statusClass(item.status), statusLabel(item.status));
      appendPlanCell(row, "Status", chip, "arc-plan-status");

      appendPlanCell(row, "Work item", planLink(item), "arc-plan-work");
      appendPlanCell(row, "Surface", item.surface, "arc-plan-surface");
      appendPlanCell(row, "Gate", item.gate, "arc-plan-gate");
      appendPlanCell(row, "Finish signal", item.finish, "arc-plan-finish");
      body.appendChild(row);
    });

    table.append(thead, body);
    section.appendChild(table);
    return section;
  }

  function buildPlanBoard(data) {
    var plan = data.executionPlan;
    if (!plan) return null;

    var board = htmlEl("section", "arc-plan-board");
    board.setAttribute("aria-label", plan.title);

    var header = htmlEl("div", "arc-plan-header");
    var titleWrap = htmlEl("div", "arc-plan-title-wrap");
    titleWrap.appendChild(htmlEl("h3", "", plan.title));
    if (plan.updated) {
      titleWrap.appendChild(htmlEl("p", "arc-plan-updated", "Updated " + plan.updated));
    }
    header.appendChild(titleWrap);
    if (plan.endGoal) {
      header.appendChild(htmlEl("p", "arc-plan-endgoal", plan.endGoal));
    }
    board.appendChild(header);

    var summary = htmlEl("div", "arc-plan-summary");
    (plan.summary || []).forEach(function (item) {
      var metric = htmlEl("div", "arc-plan-metric arc-plan-metric-" + statusClass(item.status));
      metric.appendChild(htmlEl("span", "arc-plan-metric-label", item.label));
      metric.appendChild(htmlEl("strong", "arc-plan-metric-value", item.value));
      metric.appendChild(htmlEl("span", "arc-plan-chip arc-plan-chip-" + statusClass(item.status), statusLabel(item.status)));
      summary.appendChild(metric);
    });
    board.appendChild(summary);

    board.appendChild(buildPlanTable("Near-term execution", plan.nearTerm));
    board.appendChild(buildPlanTable("Complete route to final end goal", plan.complete));
    return board;
  }

  function updateSelectedPanel(root, svg, dataArg) {
    var panel = root.querySelector(".arc-selected");
    if (!panel) return;
    panel.replaceChildren();
    var data = dataArg || window.CIVILIZATION_ARC_DATA;
    var selected = state.selected && state.selected.item ? state.selected : null;
    var item = selected ? selected.item : null;
    var kind = selected ? selected.kind : "item";

    var header = htmlEl("div", "arc-selected-header");
    var titleWrap = htmlEl("div", "arc-selected-title-wrap");
    var eyebrow = htmlEl("div", "arc-selected-eyebrow", selected ? itemMeta(item, kind) : "current focus");
    var title = htmlEl("h3", "", selected ? itemTitle(item) : "Click an item for drill-down details");
    titleWrap.append(eyebrow, title);
    var closeButton = htmlEl("button", "arc-selected-close", "Close");
    closeButton.type = "button";
    closeButton.setAttribute("aria-label", "Close details");
    closeButton.setAttribute("data-arc-close-details", "");
    closeButton.addEventListener("click", function () {
      closeDetails(root, svg || root.querySelector("svg.arc-svg"), data);
    });
    header.append(titleWrap, closeButton);
    panel.appendChild(header);

    if (!selected) {
      panel.appendChild(
        htmlEl(
          "p",
          "arc-selected-help",
          "Click any item node in the arc to focus it here. The map zooms to that item and this panel shows its type, status, lane, sequence, and article link."
        )
      );
      return;
    }

    var facts = htmlEl("dl", "arc-selected-facts");
    var factRows = [
      ["Type", item.type || kind],
      ["Status", item.blocked ? item.status + " (blocked)" : item.status],
      ["Swimlane", itemSwimlane(data, item)],
    ];
    if (Array.isArray(item.repo) && item.repo.length) factRows.push(["Repo", item.repo.join(", ")]);
    if (item.sprint) factRows.push(["Sprint", laneLabelFor(data, item.sprint)]);
    if (item.gate) factRows.push(["Gate", item.gate]);
    if (typeof item.seq === "number") factRows.push(["Sequence", String(item.seq)]);
    if (item.blocked && item.blocked_reason) factRows.push(["Blocked by", item.blocked_reason]);
    factRows.forEach(function (row) {
      facts.appendChild(htmlEl("dt", "", row[0]));
      facts.appendChild(htmlEl("dd", "", row[1]));
    });
    panel.appendChild(facts);

    if (item.note) {
      var noteBlock = htmlEl("div", "arc-selected-related");
      noteBlock.appendChild(htmlEl("h4", "", "Note"));
      noteBlock.appendChild(htmlEl("p", "arc-selected-help", item.note));
      panel.appendChild(noteBlock);
    }

    if (item.href) {
      var link = htmlEl("a", "arc-selected-link", "Open article");
      link.href = item.href;
      panel.appendChild(link);
    }
  }

  function setupSvgInteraction(root, svg, data) {
    var wheelTarget = svg.closest(".arc-frame") || svg;
    wheelTarget.addEventListener(
      "wheel",
      function (event) {
        if (!state.expanded && !state.standalone && !event.ctrlKey && !event.metaKey) return;
        event.preventDefault();
        var rect = svg.getBoundingClientRect();
        var anchorRatio = clamp((event.clientX - rect.left) / rect.width, 0, 1);
        zoomSvg(root, svg, data, anchorRatio, event.deltaY > 0 ? 1.12 : 0.88);
      },
      { passive: false }
    );

    svg.addEventListener("pointerdown", function (event) {
      if (event.target && event.target.closest && event.target.closest("[data-arc-item]")) return;
      state.dragging = true;
      state.dragMoved = false;
      state.dragLast = { x: event.clientX, y: event.clientY };
      svg.setPointerCapture(event.pointerId);
      root.classList.add("arc-is-dragging");
    });

    svg.addEventListener("pointermove", function (event) {
      if (!state.dragging || !state.dragLast) return;
      var rect = svg.getBoundingClientRect();
      var domain = currentDomain(data);
      var span = domain.end - domain.start;
      var dx = ((event.clientX - state.dragLast.x) / rect.width) * span;
      if (Math.abs(dx) > 0.2) state.dragMoved = true;
      setDomainView(root, svg, data, domain.start - dx, domain.end - dx);
      state.dragLast = { x: event.clientX, y: event.clientY };
    });

    function endDrag(event) {
      if (!state.dragging) return;
      state.dragging = false;
      state.dragLast = null;
      root.classList.remove("arc-is-dragging");
      try {
        svg.releasePointerCapture(event.pointerId);
      } catch (err) {
        /* Pointer may already be released by the browser. */
      }
    }
    svg.addEventListener("pointerup", endDrag);
    svg.addEventListener("pointercancel", endDrag);

    root.querySelector("[data-arc-fit]").addEventListener("click", function () {
      fitFull(root, svg, data);
    });
    root.querySelector("[data-arc-zoom-in]").addEventListener("click", function () {
      zoomSvg(root, svg, data, 0.5, 0.82);
    });
    root.querySelector("[data-arc-zoom-out]").addEventListener("click", function () {
      zoomSvg(root, svg, data, 0.5, 1.18);
    });
    root.querySelector("[data-arc-export]").addEventListener("click", function () {
      exportSvg(svg);
    });
    root.querySelector("[data-arc-phase-select]").addEventListener("change", function (event) {
      var sprintId = event.target.value;
      if (!sprintId) return;
      // Zoom to the seq extent of the chosen sprint's items.
      var seqs = (data.items || [])
        .filter(function (it) { return it.sprint === sprintId; })
        .map(function (it) { return it.seq; })
        .filter(function (n) { return typeof n === "number"; });
      if (seqs.length) {
        focusRange(root, svg, data, Math.min.apply(null, seqs), Math.max.apply(null, seqs), 0.9);
      }
      event.target.value = "";
    });
    root.querySelector("[data-arc-grouping]").addEventListener("change", function (event) {
      state.grouping = event.target.value;
      drawSvg(root, svg, data);
      updateSelectedPanel(root, svg, data);
    });
    root.querySelector("[data-arc-labels-toggle]").addEventListener("change", function (event) {
      state.denseLabels = event.target.checked;
      drawSvg(root, svg, data);
      updateSelectedPanel(root, svg, data);
    });

    if (state.keyHandler) document.removeEventListener("keydown", state.keyHandler);
    state.keyHandler = function (event) {
      if (event.key === "Escape" && state.detailsOpen && !isEditableTarget(event.target)) {
        event.preventDefault();
        closeDetails(root, svg, data);
        return;
      }
      if (!(event.ctrlKey || event.metaKey) || isEditableTarget(event.target)) return;
      if (event.key === "+" || event.key === "=" || event.code === "NumpadAdd") {
        event.preventDefault();
        zoomSvg(root, svg, data, 0.5, 0.82);
      } else if (event.key === "-" || event.key === "_" || event.code === "NumpadSubtract") {
        event.preventDefault();
        zoomSvg(root, svg, data, 0.5, 1.18);
      } else if (event.key === "0" || event.code === "Numpad0") {
        event.preventDefault();
        fitFull(root, svg, data);
      }
    };
    document.addEventListener("keydown", state.keyHandler);
  }

  function render(root, data) {
    root.className = "civilization-arc-nav" + (state.standalone ? " arc-standalone-nav" : "");
    root.setAttribute("data-expanded", state.expanded ? "true" : "false");
    root.setAttribute("data-standalone", state.standalone ? "true" : "false");
    root.setAttribute("data-has-selection", state.selected ? "true" : "false");
    root.setAttribute("data-details-open", state.detailsOpen ? "true" : "false");
    root.setAttribute("data-dense-labels", state.denseLabels ? "true" : "false");
    root.setAttribute("role", "navigation");
    root.setAttribute("aria-label", data.title);
    root.replaceChildren();

    var top = htmlEl("div", "arc-topline");
    var titleWrap = htmlEl("div", "arc-title-wrap");
    var eyebrow = htmlEl("div", "arc-eyebrow", "Civilization arc");
    var title = htmlEl("h2", "arc-title", data.title);
    titleWrap.append(eyebrow, title);

    var controls = htmlEl("div", "arc-controls");
    if (state.standalone) {
      var back = htmlEl("a", "arc-button arc-back-link", "Back to Wiki");
      back.href = "index.html";
      controls.appendChild(back);
    }

    var toggle = htmlEl("button", "arc-button arc-toggle", state.expanded ? "Collapse Arc" : "Expand Arc");
    toggle.type = "button";
    toggle.setAttribute("aria-expanded", state.expanded ? "true" : "false");
    toggle.addEventListener("click", function () {
      state.expanded = !state.expanded;
      state.viewBox = {
        x: state.viewBox.x,
        y: currentViewY(),
        w: state.viewBox.w,
        h: currentViewHeight(),
      };
      render(root, data);
    });
    controls.appendChild(toggle);

    var fit = htmlEl("button", "arc-button arc-fit", "Fit full arc");
    fit.type = "button";
    fit.title = "Fit the full civilization arc in view (Ctrl 0)";
    fit.setAttribute("data-arc-fit", "");
    fit.setAttribute("data-arc-reset", "");

    var zoomIn = htmlEl("button", "arc-button", "Zoom in");
    zoomIn.type = "button";
    zoomIn.title = "Zoom in (Ctrl +)";
    zoomIn.setAttribute("data-arc-zoom-in", "");
    var zoomOut = htmlEl("button", "arc-button", "Zoom out");
    zoomOut.type = "button";
    zoomOut.title = "Zoom out (Ctrl -)";
    zoomOut.setAttribute("data-arc-zoom-out", "");

    var exportButton = htmlEl("button", "arc-button", "Export SVG");
    exportButton.type = "button";
    exportButton.title = "Download the current arc SVG";
    exportButton.setAttribute("data-arc-export", "");

    var phaseSelect = htmlEl("select", "arc-phase-select");
    phaseSelect.setAttribute("aria-label", "Zoom to sprint");
    phaseSelect.setAttribute("data-arc-phase-select", "");
    var emptyOption = htmlEl("option", "", "Zoom to sprint...");
    emptyOption.value = "";
    phaseSelect.appendChild(emptyOption);
    (data.sprints || []).forEach(function (sprint) {
      var option = htmlEl("option", "", sprint.label);
      option.value = sprint.id;
      phaseSelect.appendChild(option);
    });

    // Swimlane grouping dimension. computeLanes() reads state.grouping, so
    // changing this + redrawing regroups the chart. Default stays "status".
    var groupingLabel = htmlEl("label", "arc-check");
    groupingLabel.appendChild(document.createTextNode("group by "));
    var groupingSelect = htmlEl("select", "arc-grouping-select");
    groupingSelect.setAttribute("aria-label", "Group swimlanes by");
    groupingSelect.setAttribute("data-arc-grouping", "");
    [
      { value: "status", label: "Status" },
      { value: "repo", label: "Repo" },
      { value: "sprint", label: "Sprint" },
      { value: "gate", label: "Gate" },
    ].forEach(function (opt) {
      var option = htmlEl("option", "", opt.label);
      option.value = opt.value;
      if (opt.value === state.grouping) option.selected = true;
      groupingSelect.appendChild(option);
    });
    groupingLabel.appendChild(groupingSelect);

    var labelsLabel = htmlEl("label", "arc-check");
    var labelsToggle = htmlEl("input");
    labelsToggle.type = "checkbox";
    labelsToggle.checked = state.denseLabels;
    labelsToggle.setAttribute("data-arc-labels-toggle", "");
    // Checked = full labels (state.denseLabels true); unchecked = short codes (default).
    labelsLabel.append(labelsToggle, document.createTextNode("full labels"));

    var zoomReadout = htmlEl("span", "arc-zoom-readout", zoomLabel());
    zoomReadout.setAttribute("data-arc-zoom-readout", "");
    zoomReadout.title = "Zoom level. Use the mouse wheel over an expanded arc, or Ctrl + / Ctrl -.";

    var full = htmlEl("a", "arc-button arc-full-link", "Open Full");
    full.href = FULL_PAGE;
    full.target = "_blank";
    full.rel = "noopener";
    full.setAttribute("aria-label", "Open full arc in a new tab");
    controls.append(fit, zoomIn, zoomOut, exportButton, phaseSelect, groupingLabel, labelsLabel, zoomReadout, full);

    top.append(titleWrap, controls);
    root.appendChild(top);

    var frame = htmlEl("div", "arc-frame");
    var svg = svgEl("svg", {
      class: "arc-svg",
      role: "img",
      "aria-labelledby": "civilization-arc-title civilization-arc-desc",
      preserveAspectRatio: "xMidYMin meet",
      focusable: "true",
    });
    frame.appendChild(svg);
    var tooltip = htmlEl("div", "arc-tooltip");
    tooltip.hidden = true;
    frame.appendChild(tooltip);
    var selected = htmlEl("aside", "arc-selected");
    var main = htmlEl("div", "arc-main");
    main.append(frame, selected);
    root.appendChild(main);

    // Code KEY directly under the chart — visible in the DEFAULT (compact)
    // view, since it is appended to root rather than the .arc-expanded block
    // (which is display:none while collapsed). This is the legend that makes
    // the default code labels decodable.
    root.appendChild(buildCodeKey(data));

    var expanded = htmlEl("div", "arc-expanded");
    var copy = htmlEl("p", "arc-copy", data.subtitle + " " + data.explanation);
    var planBoard = buildPlanBoard(data);
    var lower = htmlEl("div", "arc-lower");
    var legend = htmlEl("div", "arc-legend");
    legend.appendChild(htmlEl("h3", "", "Legend"));
    legend.appendChild(buildLegend(data));
    lower.appendChild(legend);
    expanded.append(copy);
    if (planBoard) expanded.appendChild(planBoard);
    expanded.appendChild(lower);
    root.appendChild(expanded);

    syncVirtualWidth(svg);
    drawSvg(root, svg, data);
    setupSvgInteraction(root, svg, data);
    updateSelectedPanel(root, svg, data);
  }

  ready(function () {
    var data = window.CIVILIZATION_ARC_DATA;
    var mount = document.querySelector("[data-civilization-arc-nav]");
    if (!data || !mount) return;
    state.standalone = mount.getAttribute("data-arc-standalone") === "true";
    if (state.standalone || mount.getAttribute("data-arc-expanded") === "true") {
      state.expanded = true;
      state.viewBox = defaultViewBox();
    }
    render(mount, data);
  });
})();
