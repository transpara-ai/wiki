// compile/assets/civilizationArcNav.js
// Controller / composition root for the chronological-tracks arc chart.
//
// Wires three pure modules into a rendered, interactive view:
//   CivOntology  — contract (deriveNow, etc.)
//   CivArcLayout — pure geometry: buildLayout(data, {width, collapsed})
//   CivArcDraw   — pure SVG construction: drawAxis / drawTracks / drawMarkers
//
// This file owns ALL state and event wiring. The layout + draw modules stay
// pure (no DOM events, no state). Per-root state lives on the element as
// `root._arc`; render(root, data) is idempotent and is re-invoked on every
// interaction (collapse toggle, selection, background clear).
//
// Bootstraps itself: on DOMContentLoaded (or immediately if already loaded) it
// renders every [data-civilization-arc-nav] from window.CIVILIZATION_ARC_DATA.
(function () {
  "use strict";

  var SVG_NS = "http://www.w3.org/2000/svg";
  // Deterministic fallback width. jsdom has no layout, so getBoundingClientRect
  // returns 0 → we fall back to this so tests/SSR-style renders are stable.
  var BASE_WIDTH = 1680;

  // ---- small DOM helpers ----------------------------------------------------

  function htmlEl(name, className, text) {
    var el = document.createElement(name);
    if (className) el.className = className;
    if (text !== undefined && text !== null) el.textContent = text;
    return el;
  }

  function clearNode(node) {
    if (!node) return;
    if (node.replaceChildren) {
      node.replaceChildren();
      return;
    }
    while (node.firstChild) node.removeChild(node.firstChild);
  }

  function lib(name) {
    return (typeof window !== "undefined") ? window[name] : undefined;
  }

  // ---- data lookups ---------------------------------------------------------

  function indexItems(data) {
    var byId = {};
    var items = (data && data.items) || [];
    for (var i = 0; i < items.length; i++) {
      var it = items[i];
      if (it && it.id != null) byId[it.id] = it;
    }
    return byId;
  }

  // Track/family label for the detail panel, derived from the item itself
  // (mirrors how the layout assigns items to tracks):
  //   gate                         -> its family
  //   work + provenance reconstructed -> "construction arc"
  //   work + provenance derived       -> "worklist"
  //   decision                     -> "decision"
  //   goal                         -> "goal"
  function trackLabelFor(item) {
    if (!item) return "";
    if (item.type === "gate") return item.family || "gates";
    if (item.type === "goal") return "goal";
    if (item.type === "decision") return "decision";
    if (item.type === "work") {
      return item.provenance === "derived" ? "worklist" : "construction arc";
    }
    return item.type || "";
  }

  function statusLabel(status) {
    var text = String(status || "planned").replace(/[-_]+/g, " ");
    return text.charAt(0).toUpperCase() + text.slice(1);
  }

  // The current focus = the blocked frontier:
  //   currentGate    — the blocked gate nearest the now-frontier (e.g. Gate-K)
  //   blockingWork   — the blocked derived-work item (e.g. N5)
  // Chosen as the blocked item with the largest seq <= now (i.e. the frontier
  // that is actually holding the line), falling back to any blocked item of
  // that kind if none sit at/under the frontier.
  function currentFocus(data) {
    var O = lib("CivOntology");
    var items = (data && data.items) || [];
    var nowSeq = (O && O.deriveNow) ? O.deriveNow(items) : 0;

    function pickBlocked(pred) {
      var atFrontier = null;
      var anyBlocked = null;
      for (var i = 0; i < items.length; i++) {
        var it = items[i];
        if (!it || !it.blocked || !pred(it)) continue;
        if (!anyBlocked || (typeof it.seq === "number" && it.seq > anyBlocked.seq)) {
          anyBlocked = it;
        }
        if (typeof it.seq === "number" && it.seq <= nowSeq + 1e-9) {
          if (!atFrontier || it.seq > atFrontier.seq) atFrontier = it;
        }
      }
      return atFrontier || anyBlocked;
    }

    return {
      nowSeq: nowSeq,
      currentGate: pickBlocked(function (it) { return it.type === "gate"; }),
      blockingWork: pickBlocked(function (it) {
        return it.type === "work" && it.provenance === "derived";
      }),
    };
  }

  // ---- scaffold (built once per root, idempotent) ---------------------------

  function ensureScaffold(root) {
    root._arc = root._arc || { collapsed: {}, selectedId: null };
    var s = root._arc;
    if (s.scaffolded && s.frame && s.svg && s.nowPanel && s.detailPanel && s.tooltip) {
      return s;
    }

    // Keep the historical root class so the existing scoped chrome CSS (the
    // --arc-* palette, sticky/full-page handling) applies. Mark standalone so
    // the full-width overrides target it.
    var standalone = root.getAttribute("data-arc-standalone") === "true";
    root.classList.add("civilization-arc-nav", "arc-tracks-nav");
    if (standalone) root.classList.add("arc-standalone-nav");
    root.setAttribute("role", "navigation");
    if (!root.getAttribute("aria-label")) {
      root.setAttribute("aria-label", "Civilization arc");
    }

    clearNode(root);

    var frame = htmlEl("div", "arc-frame");

    var svg = document.createElementNS(SVG_NS, "svg");
    svg.setAttribute("class", "arc-svg");
    svg.setAttribute("xmlns", SVG_NS);
    svg.setAttribute("role", "img");
    svg.setAttribute("preserveAspectRatio", "xMinYMin meet");
    frame.appendChild(svg);

    var tooltip = htmlEl("div", "arc-tooltip");
    tooltip.hidden = true;
    frame.appendChild(tooltip);

    var panels = htmlEl("div", "arc-panels");
    var nowPanel = htmlEl("div", "arc-now-panel");
    var detailPanel = htmlEl("div", "arc-detail-panel");
    panels.append(nowPanel, detailPanel);

    root.append(frame, panels);

    s.scaffolded = true;
    s.frame = frame;
    s.svg = svg;
    s.tooltip = tooltip;
    s.panels = panels;
    s.nowPanel = nowPanel;
    s.detailPanel = detailPanel;
    s.standalone = standalone;
    return s;
  }

  // ---- tooltip --------------------------------------------------------------

  function showTooltip(root, item, event) {
    var s = root._arc;
    var tip = s && s.tooltip;
    if (!tip || !item) return;
    var code = item.code == null ? "" : String(item.code);
    var label = item.label == null ? "" : String(item.label);
    var status = item.status == null ? "" : String(item.status);
    tip.textContent = code + " — " + label + " · " + status;
    tip.hidden = false;
    positionTooltip(root, tip, event);
  }

  function positionTooltip(root, tip, event) {
    var s = root._arc;
    var frame = s && s.frame;
    if (!frame) return;
    var box = frame.getBoundingClientRect();
    var hasPoint = event && typeof event.clientX === "number" && typeof event.clientY === "number";
    var x = hasPoint ? (event.clientX - box.left + 14) : 16;
    var y = hasPoint ? (event.clientY - box.top + 14) : 16;
    // Keep the tooltip inside the frame horizontally where we can measure it.
    var maxX = Math.max(8, (box.width || 0) - 240);
    if (x > maxX) x = maxX;
    if (x < 8) x = 8;
    if (y < 8) y = 8;
    tip.style.left = x + "px";
    tip.style.top = y + "px";
  }

  function hideTooltip(root) {
    var s = root._arc;
    if (s && s.tooltip) s.tooltip.hidden = true;
  }

  // ---- now panel ------------------------------------------------------------

  function renderNowPanel(root, data) {
    var s = root._arc;
    var panel = s.nowPanel;
    clearNode(panel);

    panel.appendChild(htmlEl("div", "arc-panel-eyebrow", "now · current focus"));

    var focus = currentFocus(data);
    var gate = focus.currentGate;

    var head = htmlEl("div", "arc-now-head");
    if (gate) {
      head.appendChild(htmlEl("span", "arc-now-code", gate.code || gate.id || "gate"));
      head.appendChild(htmlEl("span", "arc-badge arc-badge-blocked", "blocked"));
      panel.appendChild(head);
      panel.appendChild(htmlEl("p", "arc-now-label", gate.label || ""));
    } else {
      head.appendChild(htmlEl("span", "arc-now-code", "no blocked gate"));
      panel.appendChild(head);
    }

    if (focus.blockingWork) {
      var bw = focus.blockingWork;
      var blk = htmlEl("p", "arc-now-blocker");
      blk.appendChild(htmlEl("span", "arc-now-blocker-code", bw.code || bw.id || "work"));
      blk.appendChild(document.createTextNode(" " + (bw.label || "")));
      panel.appendChild(blk);
    }

    // Near-term worklist N1–N7 from the execution plan, each as a status dot +
    // code + work text. Codes resolve to items so the dot reflects live status.
    var plan = (data && data.executionPlan) || {};
    var nearTerm = plan.nearTerm || [];
    if (nearTerm.length) {
      var byCode = {};
      ((data && data.items) || []).forEach(function (it) {
        if (it && it.code != null) byCode[it.code] = it;
      });
      panel.appendChild(htmlEl("div", "arc-panel-subhead", "near-term worklist"));
      var list = htmlEl("ul", "arc-now-list");
      nearTerm.forEach(function (row) {
        var item = byCode[row.order];
        var status = (item && item.status) || row.status || "planned";
        var blocked = item ? item.blocked : (row.status === "blocked");
        var li = htmlEl("li", "arc-now-item");
        var dotStatus = blocked ? "blocked" : status;
        li.appendChild(htmlEl("span", "arc-status-dot arc-status-dot-" + dotStatus));
        li.appendChild(htmlEl("span", "arc-now-item-code", row.order));
        li.appendChild(htmlEl("span", "arc-now-item-text", row.work || ""));
        list.appendChild(li);
      });
      panel.appendChild(list);
    }
  }

  // ---- detail panel ---------------------------------------------------------

  function renderDetailPanel(root, data) {
    var s = root._arc;
    var panel = s.detailPanel;
    clearNode(panel);

    var byId = indexItems(data);
    var item = s.selectedId != null ? byId[s.selectedId] : null;

    if (!item) {
      panel.appendChild(htmlEl("p", "arc-detail-hint", "Select a marker for details."));
      return;
    }

    var status = item.blocked ? (item.status + " (blocked)") : item.status;

    var head = htmlEl("div", "arc-detail-head");
    head.appendChild(htmlEl("span", "arc-detail-code", item.code || item.id || ""));
    var badgeCls = "arc-badge arc-badge-" + (item.blocked ? "blocked" : (item.status || "future"));
    head.appendChild(htmlEl("span", badgeCls, statusLabel(item.blocked ? "blocked" : item.status)));
    head.appendChild(htmlEl("span", "arc-detail-track", trackLabelFor(item)));
    panel.appendChild(head);

    panel.appendChild(htmlEl("p", "arc-detail-label", item.label || ""));

    // Surface the resolved status text once more so it is unambiguous.
    var meta = htmlEl("p", "arc-detail-meta");
    meta.appendChild(htmlEl("span", "arc-detail-meta-key", "status "));
    meta.appendChild(document.createTextNode(statusLabel(status)));
    panel.appendChild(meta);

    if (item.note) {
      panel.appendChild(htmlEl("p", "arc-detail-note", item.note));
    }

    if (item.href) {
      var link = htmlEl("a", "arc-detail-link", "open article →");
      link.href = item.href;
      if (/^https?:\/\//.test(item.href)) {
        link.target = "_blank";
        link.rel = "noopener";
      }
      panel.appendChild(link);
    }
  }

  // ---- event wiring (delegated, attached once) ------------------------------

  function closestArcItem(target) {
    if (!target || !target.closest) return null;
    return target.closest("[data-arc-item]");
  }
  function closestArcCollapse(target) {
    if (!target || !target.closest) return null;
    return target.closest("[data-arc-collapse]");
  }

  function wireEvents(root, data) {
    var s = root._arc;
    if (s.wired) return;
    var svg = s.svg;
    var byId = indexItems(data);

    function itemFromEvent(event) {
      var node = closestArcItem(event.target);
      if (!node) return null;
      var id = node.getAttribute("data-arc-item");
      return id != null ? byId[id] : null;
    }

    svg.addEventListener("mouseover", function (event) {
      var item = itemFromEvent(event);
      if (item) showTooltip(root, item, event);
    });
    svg.addEventListener("mousemove", function (event) {
      if (s.tooltip && !s.tooltip.hidden && closestArcItem(event.target)) {
        positionTooltip(root, s.tooltip, event);
      }
    });
    svg.addEventListener("mouseout", function () {
      hideTooltip(root);
    });
    svg.addEventListener("focusin", function (event) {
      var item = itemFromEvent(event);
      if (item) showTooltip(root, item, event);
    });
    svg.addEventListener("focusout", function () {
      hideTooltip(root);
    });

    svg.addEventListener("click", function (event) {
      var collapse = closestArcCollapse(event.target);
      if (collapse) {
        var trackId = collapse.getAttribute("data-arc-collapse");
        if (trackId != null) {
          s.collapsed[trackId] = !s.collapsed[trackId];
          render(root, data);
        }
        return;
      }
      var node = closestArcItem(event.target);
      if (node) {
        s.selectedId = node.getAttribute("data-arc-item");
        render(root, data);
        return;
      }
      // Background click clears the selection.
      if (s.selectedId != null) {
        s.selectedId = null;
        render(root, data);
      }
    });

    // Keyboard: Enter/Space on a focused marker behaves like a click.
    svg.addEventListener("keydown", function (event) {
      if (event.key !== "Enter" && event.key !== " " && event.key !== "Spacebar") return;
      var node = closestArcItem(event.target);
      if (!node) return;
      event.preventDefault();
      var collapse = closestArcCollapse(node);
      if (collapse) {
        var trackId = collapse.getAttribute("data-arc-collapse");
        if (trackId != null) {
          s.collapsed[trackId] = !s.collapsed[trackId];
          render(root, data);
        }
        return;
      }
      s.selectedId = node.getAttribute("data-arc-item");
      render(root, data);
    });

    s.wired = true;
  }

  // ---- render (idempotent) --------------------------------------------------

  function render(root, data) {
    if (!root || !data) return;
    var Layout = lib("CivArcLayout");
    var Draw = lib("CivArcDraw");
    if (!Layout || !Layout.buildLayout || !Draw) return;

    var s = ensureScaffold(root);

    // Reflect state on the root for any CSS hooks.
    root.setAttribute("data-has-selection", s.selectedId != null ? "true" : "false");

    var width = Math.round(s.frame.getBoundingClientRect().width) || BASE_WIDTH;

    var layout = Layout.buildLayout(data, { width: width, collapsed: s.collapsed });

    var svg = s.svg;
    svg.setAttribute("viewBox", "0 0 " + layout.contentWidth + " " + layout.contentHeight);
    svg.style.width = "100%";
    svg.style.height = layout.contentHeight + "px";
    clearNode(svg);

    Draw.drawAxis(svg, layout);
    Draw.drawTracks(svg, layout, s);
    Draw.drawMarkers(svg, layout, s);

    // Mark the selected item's group for the selection treatment + reflect the
    // selection on the marker's aria state (the group class is also set by the
    // draw module, but it only knows state.selectedId — keep them in sync here
    // and tag the focusable shape so screen readers announce it).
    if (s.selectedId != null) {
      var sel = svg.querySelector('[data-arc-item="' + cssEscape(s.selectedId) + '"]');
      if (sel) {
        sel.setAttribute("aria-pressed", "true");
        var grp = sel.closest ? sel.closest(".arc-item-group") : null;
        if (grp) grp.classList.add("arc-is-selected");
      }
    }

    renderNowPanel(root, data);
    renderDetailPanel(root, data);

    wireEvents(root, data);
  }

  // Minimal CSS.escape shim (item ids here are simple slugs, but stay safe).
  function cssEscape(value) {
    var str = String(value);
    if (typeof CSS !== "undefined" && CSS.escape) return CSS.escape(str);
    return str.replace(/["\\\]\[#.:>~+*\s]/g, "\\$&");
  }

  // ---- bootstrap ------------------------------------------------------------

  function boot() {
    var data = (typeof window !== "undefined") ? window.CIVILIZATION_ARC_DATA : null;
    if (!data) return;
    var roots = document.querySelectorAll("[data-civilization-arc-nav]");
    Array.prototype.forEach.call(roots, function (root) {
      render(root, data);
    });
  }

  if (typeof document !== "undefined") {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", boot);
    } else {
      boot();
    }
  }
})();
