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
    showDependencies: true,
    denseLabels: true,
    viewDomain: null,
    detailsOpen: true,
  };

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

  function laneById(data, id) {
    return (data.swimlanes || []).find(function (lane) {
      return lane.id === id;
    });
  }

  function laneIdForItem(item, fallback) {
    if (item.swimlane) return item.swimlane;
    if (item.lane === 0) return "gate";
    if (item.lane === 2) return "stage";
    return fallback || "epic";
  }

  function laneCenter(data, id) {
    var lane = laneById(data, id);
    return lane ? lane.y : 224;
  }

  function laneTop(data, id) {
    var lane = laneById(data, id);
    return lane ? lane.y - lane.height / 2 : 112;
  }

  function laneHeight(data, id) {
    var lane = laneById(data, id);
    return lane ? lane.height : 68;
  }

  function laneBottom(data, id) {
    return laneTop(data, id) + laneHeight(data, id);
  }

  function markerY(data, marker) {
    return laneCenter(data, laneIdForItem(marker, "epic"));
  }

  function riskY(data, item) {
    return laneCenter(data, laneIdForItem(item, "close"));
  }

  function decisionY(data, item) {
    return laneCenter(data, laneIdForItem(item, "close"));
  }

  function criticalY(data) {
    return laneTop(data, "phase") - 18;
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

  function focusPhase(root, svg, data, phase) {
    focusRange(root, svg, data, phase.start, phase.end, Math.min(1.05, Math.max(0.72, phase.end - phase.start)));
  }

  function focusPoint(root, svg, data, x) {
    focusRange(root, svg, data, x - 0.08, x + 0.08, 0.9);
  }

  function findMarker(data, id) {
    return data.markers.find(function (marker) {
      return marker.id === id;
    });
  }

  function itemTitle(item) {
    return item.label || item.title || item.code || item.id;
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
    if (kind === "phase") return "phase / " + item.status;
    if (kind === "risk") return "risk / " + item.severity;
    if (kind === "gate") return "gate / " + item.status;
    if (kind === "decision") return "decision";
    return item.type || kind;
  }

  function itemSwimlane(data, item, kind) {
    var fallback = kind === "gate" ? "gate" : kind === "risk" || kind === "decision" ? "close" : "epic";
    var lane = laneById(data, laneIdForItem(item, fallback));
    return lane ? lane.label : fallback;
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

  function findPhase(data, id) {
    return (data.phases || []).find(function (phase) {
      return phase.id === id;
    });
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

  function itemsInsidePhase(data, phase) {
    if (!phase || typeof phase.start !== "number" || typeof phase.end !== "number") return [];
    var collections = [
      ["marker", data.markers || []],
      ["gate", data.gates || []],
      ["risk", data.risks || []],
      ["decision", data.decisions || []],
    ];
    var items = [];
    collections.forEach(function (entry) {
      entry[1].forEach(function (item) {
        if (typeof item.x === "number" && item.x >= phase.start && item.x <= phase.end) {
          items.push({ kind: entry[0], item: item });
        }
      });
    });
    return items;
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

    if (item.code || item.shortLabel) {
      tip.appendChild(htmlEl("span", "arc-tooltip-code", item.code || item.shortLabel));
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
      if (kind === "phase") focusPhase(root, svg, data, item);
      else if (typeof item.x === "number") focusPoint(root, svg, data, item.x);
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

  function phaseClass(status) {
    return "arc-phase arc-phase-" + status;
  }

  function drawSwimlanes(svg, data) {
    var group = svgEl("g", { class: "arc-swimlanes" });
    (data.swimlanes || []).forEach(function (lane, index) {
      var top = laneTop(data, lane.id);
      var laneGroup = svgEl("g", { class: "arc-swimlane arc-swimlane-" + lane.id });
      laneGroup.appendChild(
        svgEl("rect", {
          x: 16,
          y: top,
          width: WIDTH - 32,
          height: lane.height,
          rx: 6,
          class: "arc-swimlane-band arc-swimlane-band-" + (index % 2 === 0 ? "even" : "odd"),
        })
      );
      laneGroup.appendChild(
        svgEl("line", {
          x1: MARGIN_X - 16,
          y1: lane.y,
          x2: WIDTH - MARGIN_X,
          y2: lane.y,
          class: "arc-swimlane-axis",
        })
      );
      var label = svgEl("text", {
        x: 34,
        y: lane.y + 5,
        class: "arc-swimlane-label",
      });
      label.textContent = lane.label;
      laneGroup.appendChild(label);
      group.appendChild(laneGroup);
    });
    svg.appendChild(group);
  }

  function drawPhases(root, svg, data) {
    var group = svgEl("g", { class: "arc-phases" });
    var phaseY = laneTop(data, "phase");
    var phaseH = laneHeight(data, "phase");

    data.phases.forEach(function (phase) {
      var x = mapX(data, phase.start);
      var w = mapX(data, phase.end) - x;
      var phaseGroup = svgEl("g", { class: "arc-phase-group" + (isSelected(phase, "phase") ? " arc-is-selected" : "") });
      var rect = svgEl("rect", {
        x: x,
        y: phaseY,
        width: Math.max(1, w - 3),
        height: phaseH,
        rx: 4,
        class: phaseClass(phase.status),
      });
      phaseGroup.appendChild(rect);

      if (phase.status === "unresolved" || phase.status === "planned") {
        phaseGroup.appendChild(
          svgEl("rect", {
            x: x,
            y: phaseY,
            width: Math.max(1, w - 3),
            height: phaseH,
            rx: 4,
            class: "arc-phase-pattern",
            fill: "url(#arc-hatch)",
          })
        );
      }
      if (phase.status === "conceptual") {
        phaseGroup.appendChild(
          svgEl("rect", {
            x: x + 4,
            y: phaseY + 5,
            width: Math.max(1, w - 11),
            height: phaseH - 10,
            rx: 3,
            class: "arc-phase-pattern",
            fill: "url(#arc-dots)",
          })
        );
      }

      var visibleDomain = currentDomain(data);
      var domainZoom = fullDomainSpan(data) / (visibleDomain.end - visibleDomain.start);
      var densePhase = state.expanded && state.denseLabels && (domainZoom > 1.45 || w > 132);
      var phaseText = densePhase ? phase.label : phase.shortLabel;
      var maxChars = densePhase ? Math.floor(w / 7.5) : Math.floor(w / 9);
      addWrappedLabel(phaseGroup, phaseText, x + w / 2, phaseY + 32, "arc-phase-label", maxChars, densePhase ? 3 : 1, 14);
      if (state.denseLabels) {
        var statusText = phase.status.toUpperCase();
        if (!densePhase) {
          statusText = {
            canonical: "CANON",
            reconstructed: "RECON",
          }[phase.status] || statusText;
        }
        var status = svgEl("text", {
          x: x + w / 2,
          y: phaseY + phaseH - 10,
          class: "arc-phase-status-label",
          "text-anchor": "middle",
        });
        status.textContent = statusText;
        phaseGroup.appendChild(status);
      }

      bindInteractive(root, svg, data, phaseGroup, phase, "phase");
      group.appendChild(phaseGroup);
    });

    svg.appendChild(group);
  }

  function drawDependencies(svg, data) {
    if (!state.expanded || !state.showDependencies) return;
    var group = svgEl("g", { class: "arc-dependencies" });
    data.dependencies.forEach(function (dep) {
      var from = findMarker(data, dep.from);
      var to = findMarker(data, dep.to);
      if (!from || !to) return;
      var sx = mapX(data, from.x);
      var sy = markerY(data, from) + 12;
      var ex = mapX(data, to.x);
      var ey = markerY(data, to) + 12;
      var mid = sx + (ex - sx) / 2;
      var path = svgEl("path", {
        d: ["M", sx, sy, "C", mid, sy, mid, ey, ex, ey].join(" "),
        class: "arc-dependency",
        "marker-end": "url(#arc-arrow)",
      });
      group.appendChild(path);
    });
    svg.appendChild(group);
  }

  function drawCompactSummaryRail(root, svg, data) {
    if (state.expanded) return;
    var ids = data.summaryRail || data.criticalPath || [];
    var markers = ids.map(function (id) { return findMarker(data, id); }).filter(Boolean);
    if (!markers.length) return;

    var axisY = laneBottom(data, "phase") + 22;
    var railY = axisY + 18;
    var group = svgEl("g", { class: "arc-compact-rail" });
    group.appendChild(
      svgEl("line", {
        x1: MARGIN_X,
        y1: railY,
        x2: WIDTH - MARGIN_X,
        y2: railY,
        class: "arc-compact-rail-line",
      })
    );
    markers.forEach(function (marker, index) {
      var x = mapX(data, marker.x);
      var y = railY + (index % 2 === 0 ? -8 : 10);
      var railGroup = svgEl("g", {
        class: "arc-compact-rail-item" + (isSelected(marker, "marker") ? " arc-is-selected" : ""),
      });
      railGroup.appendChild(svgEl("line", { x1: x, y1: railY - 10, x2: x, y2: railY + 10, class: "arc-compact-rail-tick" }));
      railGroup.appendChild(svgEl("circle", { cx: x, cy: railY, r: 4, class: "arc-compact-rail-point" }));
      if (state.denseLabels) {
        var label = svgEl("text", {
          x: x,
          y: y,
          class: "arc-compact-rail-label",
          "text-anchor": "middle",
        });
        label.textContent = marker.code;
        railGroup.appendChild(label);
      }
      bindInteractive(root, svg, data, railGroup, marker, "marker");
      group.appendChild(railGroup);
    });
    svg.appendChild(group);
  }

  function drawCriticalPath(svg, data) {
    var pathPoints = data.criticalPath
      .map(function (id) {
        return findMarker(data, id);
      })
      .filter(Boolean)
      .map(function (marker) {
        return [mapX(data, marker.x), criticalY(data)];
      });

    if (pathPoints.length < 2) return;
    var d = pathPoints
      .map(function (point, index) {
        return (index === 0 ? "M " : "L ") + point[0] + " " + point[1];
      })
      .join(" ");
    svg.appendChild(
      svgEl("path", {
        d: d,
        class: "arc-critical-path",
        "marker-end": "url(#arc-critical-arrow)",
      })
    );
    pathPoints.forEach(function (point) {
      svg.appendChild(svgEl("circle", { cx: point[0], cy: point[1], r: 5, class: "arc-critical-node" }));
    });
  }

  function drawMarkerShape(group, marker, x, y) {
    var type = marker.type;
    if (type === "gate") {
      group.appendChild(
        svgEl("path", {
          d: ["M", x, y - 13, "L", x + 13, y, "L", x, y + 13, "L", x - 13, y, "Z"].join(" "),
          class: "arc-marker arc-marker-gate",
        })
      );
      return;
    }
    if (type === "deliverable") {
      group.appendChild(svgEl("line", { x1: x, y1: y - 22, x2: x, y2: y + 22, class: "arc-marker arc-marker-tick" }));
      return;
    }
    if (type === "ritual" || type === "governance" || type === "decision") {
      group.appendChild(svgEl("circle", { cx: x, cy: y, r: type === "decision" ? 12 : 14, class: "arc-marker arc-marker-circle" }));
      return;
    }
    group.appendChild(
      svgEl("rect", {
        x: x - 22,
        y: y - 12,
        width: 44,
        height: 24,
        rx: 3,
        class: "arc-marker arc-marker-module",
      })
    );
  }

  function drawMarkers(root, svg, data) {
    var group = svgEl("g", { class: "arc-markers" });
    data.markers.forEach(function (marker) {
      var x = mapX(data, marker.x);
      var y = markerY(data, marker);
      var markerGroup = svgEl("g", {
        class: "arc-marker-group arc-marker-type-" + marker.type + (isSelected(marker, "marker") ? " arc-is-selected" : ""),
      });
      drawMarkerShape(markerGroup, marker, x, y);
      if (state.denseLabels || isSelected(marker, "marker")) {
        addLabel(markerGroup, marker.code, x, y + 5, "arc-marker-label", 1);
      }
      bindInteractive(root, svg, data, markerGroup, marker, "marker");
      group.appendChild(markerGroup);
    });
    svg.appendChild(group);
  }

  function drawGates(root, svg, data) {
    var group = svgEl("g", { class: "arc-gates" });
    data.gates.forEach(function (gate) {
      var x = mapX(data, gate.x);
      var y = laneCenter(data, laneIdForItem(gate, "gate"));
      var gateGroup = svgEl("g", {
        class: "arc-gate-group arc-gate-" + gate.status + (isSelected(gate, "gate") ? " arc-is-selected" : ""),
      });
      gateGroup.appendChild(
        svgEl("path", {
          d: ["M", x, y - 15, "L", x + 15, y, "L", x, y + 15, "L", x - 15, y, "Z"].join(" "),
          class: "arc-gate",
        })
      );
      if (state.denseLabels || isSelected(gate, "gate")) {
        addLabel(gateGroup, gate.code, x, y + 35, "arc-gate-label", 1);
      }
      bindInteractive(root, svg, data, gateGroup, gate, "gate");
      group.appendChild(gateGroup);
    });
    svg.appendChild(group);
  }

  function closeChipLabel(kind, item) {
    if (kind === "decision") return "DEC " + item.code;
    return (item.severity === "high" ? "BLOCK " : "WATCH ") + item.code;
  }

  function closeChipWidth(label) {
    return Math.max(64, Math.min(118, String(label).length * 7.8 + 24));
  }

  function drawCloseChip(group, label, x, y, chipClass, labelClass) {
    var width = closeChipWidth(label);
    group.appendChild(
      svgEl("rect", {
        x: x - width / 2,
        y: y - 14,
        width: width,
        height: 28,
        rx: 5,
        class: chipClass,
      })
    );
    var text = svgEl("text", {
      x: x,
      y: y + 4,
      class: labelClass,
      "text-anchor": "middle",
    });
    text.textContent = label;
    group.appendChild(text);
  }

  function closeChipY(data, item, index) {
    var baseY = laneCenter(data, laneIdForItem(item, "close"));
    return baseY + (index % 2 === 0 ? -10 : 10);
  }

  function drawRisks(root, svg, data) {
    var group = svgEl("g", { class: "arc-risks" });
    data.risks.forEach(function (risk, index) {
      var x = mapX(data, risk.x);
      var y = closeChipY(data, risk, index);
      var riskGroup = svgEl("g", {
        class: "arc-close-group arc-risk-group arc-risk-" + risk.severity + (isSelected(risk, "risk") ? " arc-is-selected" : ""),
      });
      drawCloseChip(riskGroup, closeChipLabel("risk", risk), x, y, "arc-close-chip arc-risk", "arc-close-label arc-risk-label");
      bindInteractive(root, svg, data, riskGroup, risk, "risk");
      group.appendChild(riskGroup);
    });
    svg.appendChild(group);
  }

  function drawDecisions(root, svg, data) {
    var group = svgEl("g", { class: "arc-decisions" });
    data.decisions.forEach(function (decision, index) {
      var x = mapX(data, decision.x);
      var y = closeChipY(data, decision, index);
      var decisionGroup = svgEl("g", {
        class: "arc-close-group arc-decision-group" + (isSelected(decision, "decision") ? " arc-is-selected" : ""),
      });
      drawCloseChip(decisionGroup, closeChipLabel("decision", decision), x, y, "arc-close-chip arc-decision", "arc-close-label arc-decision-label");
      bindInteractive(root, svg, data, decisionGroup, decision, "decision");
      group.appendChild(decisionGroup);
    });
    svg.appendChild(group);
  }

  function drawCurrent(svg, data) {
    if (!data.currentFocus) return;
    var x = mapX(data, data.currentFocus.x);
    var group = svgEl("g", { class: "arc-current-focus" });
    var top = laneTop(data, "gate") - 16;
    var bottom = laneBottom(data, "close") + 14;
    group.appendChild(svgEl("line", { x1: x, y1: top, x2: x, y2: bottom, class: "arc-current-line" }));
    group.appendChild(svgEl("circle", { cx: x, cy: top, r: 7, class: "arc-current-dot" }));
    var labelAttrs = { x: x + 13, y: top + 3, class: "arc-current-label" };
    if (x > WIDTH * 0.68) {
      labelAttrs.x = x - 13;
      labelAttrs["text-anchor"] = "end";
    }
    var label = svgEl("text", labelAttrs);
    label.textContent = data.currentFocus.label;
    group.appendChild(label);
    svg.appendChild(group);
  }

  function drawAxis(svg, data) {
    var group = svgEl("g", { class: "arc-axis" });
    var y = laneBottom(data, "phase") + 22;
    group.appendChild(svgEl("line", { x1: MARGIN_X, y1: y, x2: WIDTH - MARGIN_X, y2: y }));
    data.phases.forEach(function (phase) {
      var x = mapX(data, phase.start);
      group.appendChild(svgEl("line", { x1: x, y1: y - 10, x2: x, y2: y + 10 }));
    });
    group.appendChild(svgEl("line", { x1: WIDTH - MARGIN_X, y1: y - 10, x2: WIDTH - MARGIN_X, y2: y + 10 }));
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
    root.setAttribute("data-dependencies", state.showDependencies ? "true" : "false");
    root.setAttribute("data-dense-labels", state.denseLabels ? "true" : "false");
    root.setAttribute("data-details-open", state.detailsOpen ? "true" : "false");
    svg.replaceChildren();
    var svgTitle = svgEl("title", { id: "civilization-arc-title" });
    svgTitle.textContent = data.title;
    var svgDesc = svgEl("desc", { id: "civilization-arc-desc" });
    svgDesc.textContent =
      "Interactive SVG timeline with phases, markers, gates, risks, dependencies, and a highlighted critical path.";
    svg.append(svgTitle, svgDesc);
    addDefs(svg);
    svg.appendChild(svgEl("rect", { x: 8, y: 14, width: WIDTH - 16, height: HEIGHT - 28, rx: 12, class: "arc-map-bg" }));
    drawSwimlanes(svg, data);
    drawCurrent(svg, data);
    drawPhases(root, svg, data);
    drawAxis(svg, data);
    drawCompactSummaryRail(root, svg, data);
    drawDependencies(svg, data);
    drawCriticalPath(svg, data);
    drawGates(root, svg, data);
    drawMarkers(root, svg, data);
    if (state.expanded) {
      drawDecisions(root, svg, data);
      drawRisks(root, svg, data);
    }
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
    var item = selected ? selected.item : data.currentFocus;
    var kind = selected ? selected.kind : "focus";

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
          "Click any phase block, marker, gate, risk, or decision in the arc to focus it here. The map will zoom to that item and this panel will show its status, lane, code, and article link."
        )
      );
    }
    if (item.code || item.shortLabel) {
      panel.appendChild(htmlEl("p", "arc-selected-code", item.code || item.shortLabel));
    }
    if (selected) {
      var facts = htmlEl("dl", "arc-selected-facts");
      var factRows = [
        ["Kind", itemMeta(item, kind)],
        ["Swimlane", itemSwimlane(data, item, kind)],
      ];
      if (item.status) factRows.push(["Status", item.status]);
      if (item.severity) factRows.push(["Severity", item.severity]);
      if (typeof item.start === "number" && typeof item.end === "number") {
        factRows.push(["Span", item.start + " to " + item.end]);
      } else if (typeof item.x === "number") {
        factRows.push(["Arc position", String(item.x)]);
      }
      factRows.forEach(function (row) {
        facts.appendChild(htmlEl("dt", "", row[0]));
        facts.appendChild(htmlEl("dd", "", row[1]));
      });
      panel.appendChild(facts);
      if (kind === "phase") {
        var related = itemsInsidePhase(data, item);
        var relatedBlock = htmlEl("div", "arc-selected-related");
        relatedBlock.appendChild(htmlEl("h4", "", "Inside phase"));
        if (related.length) {
          var list = htmlEl("ul", "");
          related.slice(0, 8).forEach(function (entry) {
            var li = htmlEl("li", "");
            var code = htmlEl("span", "arc-selected-related-code", entry.item.code || entry.item.shortLabel || entry.kind);
            var label = htmlEl("span", "", itemTitle(entry.item));
            li.append(code, label);
            list.appendChild(li);
          });
          relatedBlock.appendChild(list);
        } else {
          relatedBlock.appendChild(htmlEl("p", "arc-selected-help", "No internal marker is mapped to this phase yet."));
        }
        panel.appendChild(relatedBlock);
      }
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
      var phase = findPhase(data, event.target.value);
      if (!phase) return;
      state.selected = { kind: "phase", item: phase };
      state.detailsOpen = true;
      root.setAttribute("data-has-selection", "true");
      root.setAttribute("data-details-open", "true");
      focusPhase(root, svg, data, phase);
      updateSelectedPanel(root, svg, data);
      event.target.value = "";
    });
    root.querySelector("[data-arc-deps-toggle]").addEventListener("change", function (event) {
      state.showDependencies = event.target.checked;
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
    root.setAttribute("data-dependencies", state.showDependencies ? "true" : "false");
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
    phaseSelect.setAttribute("aria-label", "Zoom to phase");
    phaseSelect.setAttribute("data-arc-phase-select", "");
    var emptyOption = htmlEl("option", "", "Zoom to phase...");
    emptyOption.value = "";
    phaseSelect.appendChild(emptyOption);
    data.phases.forEach(function (phase) {
      var option = htmlEl("option", "", phase.shortLabel + " - " + phase.label);
      option.value = phase.id;
      phaseSelect.appendChild(option);
    });

    var depsLabel = htmlEl("label", "arc-check");
    var depsToggle = htmlEl("input");
    depsToggle.type = "checkbox";
    depsToggle.checked = state.showDependencies;
    depsToggle.setAttribute("data-arc-deps-toggle", "");
    depsLabel.append(depsToggle, document.createTextNode("dependencies"));

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
    controls.append(fit, zoomIn, zoomOut, exportButton, phaseSelect, depsLabel, labelsLabel, zoomReadout, full);

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
