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

  // Grouping dimensions for the toolbar. "tracks" is the default type-track view;
  // the others decompose lanes via CivOntology.groupBy, sharing the chronological axis.
  var GROUPINGS = [
    { id: "tracks", label: "Tracks" },
    { id: "status", label: "Status" },
    { id: "repo", label: "Repo" },
    { id: "sprint", label: "Sprint" },
    { id: "gate", label: "Gate" },
    { id: "actor", label: "Actor" },
  ];

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

  // ---- href safety helpers --------------------------------------------------

  // Fail-closed allowlist: permits http(s), anchors, root-relative (single /),
  // and bare relative paths (e.g. the-civilization.html) that carry no scheme.
  // Rejects: any scheme: URI (javascript:/data:/vbscript:/mailto:/…),
  //          protocol-relative (// or \\), control/whitespace chars, empty/non-string.
  function safeHref(href) {
    if (typeof href !== "string" || href === "") return null;
    // Reject control chars or whitespace (including encoded newlines in href)
    if (/[\x00-\x20\x7f]/.test(href)) return null;
    // Reject protocol-relative // or \\ at the start
    if (/^[\\/]{2}/.test(href)) return null;
    // Allow absolute http(s)
    if (/^https?:\/\//i.test(href)) return href;
    // Allow anchor or root-relative (but NOT //)
    if (href.charAt(0) === "#" || href.charAt(0) === "/") return href;
    // Allow bare relative paths that have no scheme (colon before first / # ?)
    var sep = href.search(/[/#?]/);
    var colon = href.indexOf(":");
    if (colon !== -1 && (sep === -1 || colon < sep)) return null;
    return href;
  }
  function isExternalHref(href) { return /^https?:\/\//i.test(href); }

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

  function fieldLabel(value) {
    return String(value || "").replace(/[-_]+/g, " ");
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
    root._arc = root._arc || { collapsed: {}, selectedId: null, groupBy: "tracks" };
    var s = root._arc;
    if (s.scaffolded && s.frame && s.svg && s.nowPanel && s.detailPanel && s.tooltip && s.toolbar) {
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

    var toolbar = htmlEl("div", "arc-toolbar");
    toolbar.setAttribute("role", "group");
    toolbar.setAttribute("aria-label", "Group the arc by");
    GROUPINGS.forEach(function (g) {
      var btn = htmlEl("button", "arc-group-btn", g.label);
      btn.setAttribute("type", "button");
      btn.setAttribute("data-arc-group", g.id);
      toolbar.appendChild(btn);
    });

    root.append(toolbar, frame, panels);

    s.scaffolded = true;
    s.toolbar = toolbar;
    s.frame = frame;
    s.svg = svg;
    s.tooltip = tooltip;
    s.panels = panels;
    s.nowPanel = nowPanel;
    s.detailPanel = detailPanel;
    s.standalone = standalone;
    return s;
  }

  // Reflect the active grouping on the toolbar buttons.
  function updateToolbar(s) {
    if (!s || !s.toolbar) return;
    var cur = s.groupBy || "tracks";
    var btns = s.toolbar.querySelectorAll("[data-arc-group]");
    Array.prototype.forEach.call(btns, function (b) {
      var on = b.getAttribute("data-arc-group") === cur;
      b.classList.toggle("arc-group-btn-active", on);
      b.setAttribute("aria-pressed", on ? "true" : "false");
    });
  }

  // ---- tooltip --------------------------------------------------------------

  function showTooltip(root, item, event) {
    var s = root._arc;
    var tip = s && s.tooltip;
    if (!tip || !item) return;
    clearNode(tip);
    var type = item.type == null ? "" : String(item.type);
    var status = item.blocked ? "blocked" : (item.status == null ? "" : String(item.status));
    tip.appendChild(htmlEl("div", "arc-tooltip-eyebrow", (type + " · " + status).replace(/^ · | · $/g, "")));
    tip.appendChild(htmlEl("strong", "", item.label == null ? "" : String(item.label)));
    if (item.code != null) tip.appendChild(htmlEl("span", "arc-tooltip-code", String(item.code)));
    var sprintLabel = s.sprintLabelById && s.sprintLabelById[item.sprint];
    if (sprintLabel) tip.appendChild(htmlEl("div", "arc-tooltip-meta", "sprint · " + sprintLabel));
    var ord = s.ordinalById && s.ordinalById[item.id];
    if (ord) tip.appendChild(htmlEl("div", "arc-tooltip-meta", "step " + ord + " of " + s.itemCount));
    if (item.date) tip.appendChild(htmlEl("div", "arc-tooltip-meta", "date · " + item.date)); // reserved for date-backfill follow-up
    if (item.provenance) tip.appendChild(htmlEl("div", "arc-tooltip-meta", "provenance · " + item.provenance));
    if (item.author) tip.appendChild(htmlEl("div", "arc-tooltip-meta", "actor · @" + item.author));
    // No clickable link in the tooltip — pointer-events:none on .arc-tooltip makes
    // anchors unclickable and confusing. The detail panel (on click) shows the link.
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

    if (item.boundary_status || item.go_live_revalidation) {
      var boundary = htmlEl("p", "arc-detail-meta");
      boundary.appendChild(htmlEl("span", "arc-detail-meta-key", "boundary "));
      var parts = [];
      if (item.boundary_status) parts.push(fieldLabel(item.boundary_status));
      if (item.go_live_revalidation) parts.push("go-live revalidation " + fieldLabel(item.go_live_revalidation));
      boundary.appendChild(document.createTextNode(parts.join(" · ")));
      panel.appendChild(boundary);
    }

    if (item.note) {
      panel.appendChild(htmlEl("p", "arc-detail-note", item.note));
    }

    if (Array.isArray(item.evidence_links) && item.evidence_links.length) {
      var evidence = htmlEl("p", "arc-detail-evidence");
      evidence.appendChild(htmlEl("span", "arc-detail-meta-key", "evidence "));
      var renderedEvidence = 0;
      item.evidence_links.forEach(function (entry) {
        var node = null;
        var safe = entry && safeHref(entry.href);
        if (safe) {
          var a = htmlEl("a", "arc-detail-evidence-link", entry.label || safe);
          a.href = safe;
          if (isExternalHref(safe)) {
            a.target = "_blank";
            a.rel = "noopener noreferrer";
          }
          node = a;
        } else if (entry && entry.label) {
          node = document.createTextNode(entry.label);
        }
        if (!node) return;
        if (renderedEvidence) evidence.appendChild(document.createTextNode(" · "));
        evidence.appendChild(node);
        renderedEvidence += 1;
      });
      if (renderedEvidence) panel.appendChild(evidence);
    }

    var detailSafe = safeHref(item.href);
    if (detailSafe) {
      var link = htmlEl("a", "arc-detail-link", "open article →");
      link.href = detailSafe;
      if (isExternalHref(detailSafe)) {
        link.target = "_blank";
        link.rel = "noopener noreferrer";
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

    function itemFromEvent(event) {
      var node = closestArcItem(event.target);
      if (!node) return null;
      var id = node.getAttribute("data-arc-item");
      return id != null ? s.byId[id] : null;
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
          render(root, s.data);
        }
        return;
      }
      var node = closestArcItem(event.target);
      if (node) {
        s.selectedId = node.getAttribute("data-arc-item");
        render(root, s.data);
        return;
      }
      // Background click clears the selection.
      if (s.selectedId != null) {
        s.selectedId = null;
        render(root, s.data);
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
          render(root, s.data);
        }
        return;
      }
      s.selectedId = node.getAttribute("data-arc-item");
      render(root, s.data);
    });

    // Grouping toolbar: switch the lane decomposition; re-render with current data.
    if (s.toolbar) {
      s.toolbar.addEventListener("click", function (event) {
        var btn = (event.target && event.target.closest) ? event.target.closest("[data-arc-group]") : null;
        if (!btn) return;
        var dim = btn.getAttribute("data-arc-group") || "tracks";
        if (dim === (s.groupBy || "tracks")) return;
        s.groupBy = dim;
        render(root, s.data);
      });
    }

    s.wired = true;
  }

  // ---- render (idempotent) --------------------------------------------------

  function render(root, data) {
    if (!root || !data) return;
    var Layout = lib("CivArcLayout");
    var Draw = lib("CivArcDraw");
    if (!Layout || !Layout.buildLayout || !Draw) return;

    var s = ensureScaffold(root);
    s.data = data;                 // current data (baked, or merged-with-live overlay)
    s.byId = indexItems(data);     // re-index each render so live markers stay interactive

    if (!s.ordinalById) {
      s.ordinalById = {};
      s.sprintLabelById = {};
      var sorted = ((data.items) || []).slice().sort(function (a, b) {
        return (a.seq || 0) - (b.seq || 0);
      });
      for (var oi = 0; oi < sorted.length; oi++) {
        if (sorted[oi].id != null) s.ordinalById[sorted[oi].id] = oi + 1;
      }
      s.itemCount = sorted.length;
      ((data.sprints) || []).forEach(function (sp) {
        if (sp && sp.id != null) s.sprintLabelById[sp.id] = sp.label;
      });
    }

    if (typeof ResizeObserver !== "undefined" && !s.resizeObserver) {
      s.lastWidth = Math.round(s.frame.getBoundingClientRect().width) || 0;
      s.resizeObserver = new ResizeObserver(function () {
        var w = Math.round(s.frame.getBoundingClientRect().width);
        if (!w || Math.abs(w - s.lastWidth) < 2) return; // ignore sub-pixel / height-only changes
        s.lastWidth = w;
        if (s.raf && typeof cancelAnimationFrame !== "undefined") cancelAnimationFrame(s.raf);
        var schedule = (typeof requestAnimationFrame !== "undefined")
          ? requestAnimationFrame : function (fn) { return setTimeout(fn, 16); };
        s.raf = schedule(function () { render(root, s.data); });
      });
      s.resizeObserver.observe(s.frame); // observe the FRAME (container), not the svg, to avoid feedback
    }

    // Reflect state on the root for any CSS hooks.
    root.setAttribute("data-has-selection", s.selectedId != null ? "true" : "false");

    var width = Math.round(s.frame.getBoundingClientRect().width) || BASE_WIDTH;

    var layout = Layout.buildLayout(data, { width: width, collapsed: s.collapsed, groupBy: s.groupBy || "tracks" });

    var svg = s.svg;
    svg.setAttribute("viewBox", "0 0 " + layout.contentWidth + " " + layout.contentHeight);
    svg.style.width = layout.contentWidth + "px";
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

    updateToolbar(s);
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

  // Live-freshness chip in the frame ("live · updated …" or "live · unavailable").
  function setLiveChip(root, text, ok) {
    var s = root._arc;
    if (!s) return;
    var chip = s.liveChip;
    if (!chip) {
      chip = htmlEl("div", "arc-live-chip");
      s.liveChip = chip;
      (s.frame || root).appendChild(chip);
    }
    chip.classList.toggle("arc-live-chip-warn", !ok);
    chip.textContent = text;
  }

  // Fetch dist/inflight.json, overlay the live derived items via the ontology's
  // pure mergeInflight, and re-render. Fail-safe: missing fetch, a non-ok response,
  // a rejected promise, or a rejected merge all keep the baked render.
  function loadInflight(roots, data) {
    if (typeof fetch !== "function") return;            // no fetch (SSR/jsdom default) → baked only
    var O = lib("CivOntology");
    if (!O || !O.mergeInflight) return;
    fetch("inflight.json", { cache: "no-store" })
      .then(function (resp) { if (!resp || !resp.ok) throw new Error("inflight HTTP"); return resp.json(); })
      .then(function (inflight) {
        var merged = O.mergeInflight(data, inflight);
        if (!merged.ok) {
          if (typeof console !== "undefined") console.warn("inflight: overlay rejected (fail-closed):", merged.errors);
          Array.prototype.forEach.call(roots, function (root) { setLiveChip(root, "live · unavailable", false); });
          return;
        }
        var liveData = {};
        for (var key in data) { if (Object.prototype.hasOwnProperty.call(data, key)) liveData[key] = data[key]; }
        liveData.items = merged.items;                  // new array — baked data untouched
        Array.prototype.forEach.call(roots, function (root) {
          if (root._arc) root._arc.ordinalById = null;  // recompute ordinals over the merged set
          render(root, liveData);
          setLiveChip(root, "live · updated " + (merged.generated || "?"), true);
        });
      })
      .catch(function (e) {
        if (typeof console !== "undefined") console.warn("inflight: fetch failed (keeping baked):", e && e.message);
        Array.prototype.forEach.call(roots, function (root) { setLiveChip(root, "live · unavailable", false); });
      });
  }

  function boot() {
    var data = (typeof window !== "undefined") ? window.CIVILIZATION_ARC_DATA : null;
    if (!data) return;
    var roots = document.querySelectorAll("[data-civilization-arc-nav]");
    Array.prototype.forEach.call(roots, function (root) { render(root, data); }); // baked first — never blank
    loadInflight(roots, data);                                                    // then overlay live
  }

  if (typeof document !== "undefined") {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", boot);
    } else {
      boot();
    }
  }
})();
