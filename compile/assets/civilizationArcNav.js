(function () {
  "use strict";

  var SVG_NS = "http://www.w3.org/2000/svg";
  var BASE_WIDTH = 1680;
  var WIDTH = BASE_WIDTH;
  var HEIGHT = 420;
  var MARGIN_X = 118;
  var FULL_PAGE = "civilization-arc.html";

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
    denseLabels: true,
    viewDomain: null,
    detailsOpen: true,
    // Dimension the swimlanes are grouped by. Foundation pass ships "status";
    // a later pass adds a grouping toggle (repo|sprint|gate) — the seam is here.
    grouping: "status",
  };

  // Vertical band where item lanes live (between the top margin and the axis).
  // Mirrors the area the old fixed swimlanes[] occupied.
  var LANE_AREA_TOP = 70;
  var LANE_AREA_BOTTOM = 300;

  // Lane geometry for the current draw, keyed by lane name → {y, height, top}.
  // Rebuilt every drawSvg() by drawLanes(); read by laneCenterFor().
  var laneGeom = {};

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

  function mapX(data, x) {
    var domain = currentDomain(data);
    var span = domain.end - domain.start;
    return MARGIN_X + ((x - domain.start) / span) * (WIDTH - MARGIN_X * 2);
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

  // Center Y of a lane, by lane name. Falls back to the middle of the lane area
  // when geometry has not been built (defensive — should not happen at draw time).
  function laneCenterFor(laneName) {
    var g = laneGeom[laneName];
    return g ? g.y : (LANE_AREA_TOP + LANE_AREA_BOTTOM) / 2;
  }

  // Bottom Y of the lane band — where the axis sits.
  function laneAreaBottom() {
    return LANE_AREA_BOTTOM;
  }

  // Top Y of the lane band — where the "now" line / first band begins.
  function laneAreaTop() {
    return LANE_AREA_TOP;
  }

  function currentViewHeight() {
    return state.expanded ? HEIGHT : 190;
  }

  function currentViewY() {
    return state.expanded ? 0 : 42;
  }

  function defaultViewBox() {
    return { x: 0, y: currentViewY(), w: WIDTH, h: currentViewHeight() };
  }

  function syncVirtualWidth(svg) {
    var rect = svg.getBoundingClientRect();
    if (!rect.width || !rect.height) return;
    var nextWidth = Math.max(900, Math.round(currentViewHeight() * (rect.width / rect.height)));
    if (Math.abs(nextWidth - WIDTH) > 4) {
      WIDTH = nextWidth;
      state.viewBox = defaultViewBox();
    }
  }

  function setViewBox(svg) {
    state.viewBox.x = 0;
    state.viewBox.y = currentViewY();
    state.viewBox.w = WIDTH;
    state.viewBox.h = currentViewHeight();
    svg.setAttribute(
      "viewBox",
      [state.viewBox.x, state.viewBox.y, state.viewBox.w, state.viewBox.h].join(" ")
    );
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
  function computeLanes(data) {
    var O = window.CivOntology;
    var groups = O && O.groupBy ? O.groupBy(data.items || [], state.grouping) : [];
    laneGeom = {};
    var top = laneAreaTop();
    var bottom = laneAreaBottom();
    var count = Math.max(1, groups.length);
    var band = (bottom - top) / count;
    groups.forEach(function (g, index) {
      var bandTop = top + index * band;
      laneGeom[g.lane] = {
        top: bandTop,
        height: band,
        y: bandTop + band / 2,
        index: index,
      };
    });
    return groups;
  }

  function drawLanes(svg, data, groups) {
    var group = svgEl("g", { class: "arc-swimlanes" });
    groups.forEach(function (g, index) {
      var geom = laneGeom[g.lane];
      if (!geom) return;
      var laneGroup = svgEl("g", { class: "arc-swimlane arc-swimlane-" + statusClass(g.lane) });
      laneGroup.appendChild(
        svgEl("rect", {
          x: 16,
          y: geom.top + 2,
          width: WIDTH - 32,
          height: Math.max(1, geom.height - 4),
          rx: 6,
          class: "arc-swimlane-band arc-swimlane-band-" + (index % 2 === 0 ? "even" : "odd"),
        })
      );
      laneGroup.appendChild(
        svgEl("line", {
          x1: MARGIN_X - 16,
          y1: geom.y,
          x2: WIDTH - MARGIN_X,
          y2: geom.y,
          class: "arc-swimlane-axis",
        })
      );
      var label = svgEl("text", {
        x: 34,
        y: geom.y + 5,
        class: "arc-swimlane-label",
      });
      label.textContent = laneLabelFor(data, g.lane);
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
      var sy = laneCenterFor(itemLaneName(from));
      var ex = mapX(data, to.seq);
      var ey = laneCenterFor(itemLaneName(to));
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
      var y = laneCenterFor(g.lane);
      g.items.forEach(function (item) {
        var x = mapX(data, item.seq);
        var itemGroup = svgEl("g", {
          class:
            "arc-marker-group arc-item-group arc-item-type-" +
            statusClass(item.type) +
            (item.blocked ? " arc-item-is-blocked" : "") +
            (isSelected(item, "item") ? " arc-is-selected" : ""),
        });
        drawItemShape(itemGroup, item, x, y);
        if (item.blocked) drawBlockerOverlay(itemGroup, item, x, y);
        if (state.denseLabels || isSelected(item, "item")) {
          // Short label inside/under the node; full label lives in the tooltip + panel.
          addLabel(itemGroup, shortLabel(item.label, 14), x, y + 4, "arc-marker-label arc-item-label", 1);
        }
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
    if (x > WIDTH * 0.68) {
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
    var y = laneAreaBottom() + 16;
    group.appendChild(svgEl("line", { x1: MARGIN_X, y1: y, x2: WIDTH - MARGIN_X, y2: y }));
    var start = Math.ceil(data.domain.start);
    var end = Math.floor(data.domain.end);
    for (var tick = start; tick <= end; tick++) {
      var x = mapX(data, tick);
      group.appendChild(svgEl("line", { x1: x, y1: y - 10, x2: x, y2: y + 10 }));
    }
    var label = svgEl("text", {
      x: WIDTH - MARGIN_X,
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
    svg.appendChild(svgEl("rect", { x: 8, y: 14, width: WIDTH - 16, height: HEIGHT - 28, rx: 12, class: "arc-map-bg" }));
    // Build lane geometry once, then draw lanes → now-line → items → axis.
    // Collapsed and expanded views render the same item lanes (reduced is fine).
    var groups = computeLanes(data);
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
    labelsLabel.append(labelsToggle, document.createTextNode("dense labels"));

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
