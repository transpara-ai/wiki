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

  // Zoom: 1 == fit-to-frame (the default; whole arc visible, no horizontal scroll).
  // Higher zoom widens the content so columns spread out for detail (frame scrolls).
  // Persisted per-browser so a chosen detail level survives reloads.
  var ZOOM_KEY = "civ-arc-zoom";
  var ZOOM_MIN = 1, ZOOM_STEP = 0.5, ZOOM_BASE_MAX = 4, ZOOM_ABS_MAX = 16;
  // Snap to a 0.5 step and clamp to [1, maxZoom]. maxZoom is derived per render from
  // the frame width + chip-safe detail width (see render) so the top of the zoom range
  // always reaches a readable detail view even on a narrow frame; falls back to an
  // absolute ceiling when no max is supplied (e.g. reading the persisted value).
  function clampZoom(z, maxZoom) {
    if (typeof z !== "number" || isNaN(z)) return 1;
    z = Math.round(z * 2) / 2;
    var hi = (typeof maxZoom === "number" && maxZoom >= ZOOM_MIN) ? maxZoom : ZOOM_ABS_MAX;
    return Math.max(ZOOM_MIN, Math.min(hi, z));
  }
  function readZoom() {
    try {
      var v = parseFloat(window.localStorage.getItem(ZOOM_KEY));
      if (!isNaN(v)) return clampZoom(v);
    } catch (e) { /* no localStorage (SSR/jsdom) → fit */ }
    return 1;
  }
  function writeZoom(z) {
    try { window.localStorage.setItem(ZOOM_KEY, String(z)); } catch (e) { /* ignore */ }
  }

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

  function progressEvidence() {
    return (typeof window !== "undefined") ? window.CIVILIZATION_PROGRESS_EVIDENCE : null;
  }

  function progressSource() {
    return (typeof window !== "undefined") ? window.CIVILIZATION_PROGRESS_EVIDENCE_SOURCE : null;
  }

  function appendSafeLink(parent, href, label, className) {
    var safe = safeHref(href);
    if (!safe) {
      parent.appendChild(document.createTextNode(label || ""));
      return null;
    }
    var link = htmlEl("a", className || "", label || safe);
    link.href = safe;
    if (isExternalHref(safe)) {
      link.target = "_blank";
      link.rel = "noopener noreferrer";
    }
    parent.appendChild(link);
    return link;
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

    function pick(pred) {
      var atFrontier = null;
      var any = null;
      for (var i = 0; i < items.length; i++) {
        var it = items[i];
        if (!it || !pred(it)) continue;
        if (!any || (typeof it.seq === "number" && it.seq > any.seq)) any = it;
        if (typeof it.seq === "number" && it.seq <= nowSeq + 1e-9) {
          if (!atFrontier || it.seq > atFrontier.seq) atFrontier = it;
        }
      }
      return atFrontier || any;
    }

    return {
      nowSeq: nowSeq,
      currentGate: pick(function (it) { return it.blocked && it.type === "gate"; }),
      // Post-waiver: a closed gate can still hold the go-live hard stop. Surface it so the
      // focus panel never reads "all clear" while go_live_revalidation is blocked.
      goLiveGate: pick(function (it) { return it.type === "gate" && it.go_live_revalidation === "blocked"; }),
      blockingWork: pick(function (it) {
        return it.blocked && it.type === "work" && it.provenance === "derived";
      }),
      // Most-recently-dated done item — surfaces that the operating cadence has
      // advanced (e.g. Gate-V on 2026-06-22) even while the go-live hard stop holds.
      latestDated: (function () {
        var best = null;
        for (var j = 0; j < items.length; j++) {
          var d = items[j];
          if (d && d.status === "done" && typeof d.date === "string" &&
              /^\d{4}-\d{2}-\d{2}$/.test(d.date) && (!best || d.date > best.date)) {
            best = d;
          }
        }
        return best;
      })(),
    };
  }

  // ---- scaffold (built once per root, idempotent) ---------------------------

  function ensureScaffold(root) {
    root._arc = root._arc || { collapsed: {}, selectedId: null, groupBy: "tracks", zoom: readZoom() };
    var s = root._arc;
    if (s.scaffolded && s.frame && s.svg && s.nowPanel && s.detailPanel && s.tooltip && s.toolbar && s.progressPanel) {
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

    var progressPanel = htmlEl("section", "arc-progress-panel");
    progressPanel.setAttribute("aria-label", "Progress evidence snapshot");

    var toolbar = htmlEl("div", "arc-toolbar");
    toolbar.setAttribute("role", "group");
    toolbar.setAttribute("aria-label", "Group the arc by");
    GROUPINGS.forEach(function (g) {
      var btn = htmlEl("button", "arc-group-btn", g.label);
      btn.setAttribute("type", "button");
      btn.setAttribute("data-arc-group", g.id);
      toolbar.appendChild(btn);
    });

    // Zoom controls (presentational width): − / Fit / + . "Fit" shows the whole arc;
    // + spreads columns for detail (the frame scrolls). The middle button is the live
    // zoom readout and resets to Fit.
    var zoomWrap = htmlEl("div", "arc-zoom");
    zoomWrap.setAttribute("role", "group");
    zoomWrap.setAttribute("aria-label", "Zoom the timeline");
    var zoomOut = htmlEl("button", "arc-zoom-btn", "−");
    zoomOut.setAttribute("type", "button");
    zoomOut.setAttribute("data-arc-zoom", "out");
    zoomOut.setAttribute("aria-label", "Zoom out");
    var zoomReadout = htmlEl("button", "arc-zoom-btn arc-zoom-level", "Fit");
    zoomReadout.setAttribute("type", "button");
    zoomReadout.setAttribute("data-arc-zoom", "fit");
    zoomReadout.setAttribute("aria-label", "Fit timeline to width");
    var zoomIn = htmlEl("button", "arc-zoom-btn", "+");
    zoomIn.setAttribute("type", "button");
    zoomIn.setAttribute("data-arc-zoom", "in");
    zoomIn.setAttribute("aria-label", "Zoom in");
    zoomWrap.append(zoomOut, zoomReadout, zoomIn);
    toolbar.appendChild(zoomWrap);

    root.append(toolbar, frame, panels, progressPanel);

    s.scaffolded = true;
    s.toolbar = toolbar;
    s.zoomReadout = zoomReadout;
    s.frame = frame;
    s.svg = svg;
    s.tooltip = tooltip;
    s.panels = panels;
    s.nowPanel = nowPanel;
    s.detailPanel = detailPanel;
    s.progressPanel = progressPanel;
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
    // Actor grouping needs per-item authors; baked items have none (live overlay is
    // parked), so disable the toggle when no actor data exists instead of showing a
    // useless "(unknown)" lane.
    var actorItems = (s.data && s.data.items) || [];
    var hasActors = actorItems.some(function (it) { return it && it.author; });
    var actorBtn = s.toolbar.querySelector('[data-arc-group="actor"]');
    if (actorBtn) {
      actorBtn.disabled = !hasActors;
      actorBtn.classList.toggle("arc-group-btn-disabled", !hasActors);
      actorBtn.setAttribute("title", hasActors
        ? "Group by actor"
        : "Actor view needs live / ownership data (none loaded yet)");
    }
    if (s.zoomReadout) {
      var z = s.zoom || 1;
      s.zoomReadout.textContent = z <= 1 ? "Fit" : (Math.round(z * 100) + "%");
      s.zoomReadout.setAttribute("aria-label",
        z <= 1 ? "Fit timeline to width" : ("Zoom " + Math.round(z * 100) + "% — click to fit"));
    }
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
    var goLive = focus.goLiveGate;

    var head = htmlEl("div", "arc-now-head");
    if (gate) {
      head.appendChild(htmlEl("span", "arc-now-code", gate.code || gate.id || "gate"));
      head.appendChild(htmlEl("span", "arc-badge arc-badge-blocked", "blocked"));
      panel.appendChild(head);
      panel.appendChild(htmlEl("p", "arc-now-label", gate.label || ""));
    } else if (goLive) {
      // No fully-blocked gate, but a closed gate still holds the go-live hard stop
      // (go_live_revalidation: "blocked"). Surface it as the focus, not "all clear".
      head.appendChild(htmlEl("span", "arc-now-code", goLive.code || goLive.id || "gate"));
      head.appendChild(htmlEl("span", "arc-badge arc-badge-blocked", "go-live blocked"));
      panel.appendChild(head);
      panel.appendChild(htmlEl("p", "arc-now-label", goLive.label || ""));
      panel.appendChild(htmlEl("p", "arc-now-boundary", "go-live revalidation blocked (pre-live work closed by waiver)"));
    } else {
      head.appendChild(htmlEl("span", "arc-now-code", "no blocked gate"));
      panel.appendChild(head);
    }

    // Date of the focus gate (e.g. Gate-K's go-live hard stop) shown inline, so the
    // "when" is visible without hovering the dot.
    var focusGate = gate || goLive;
    if (focusGate && focusGate.date) {
      var nd = htmlEl("p", "arc-now-date");
      nd.appendChild(htmlEl("span", "arc-now-date-key", "date "));
      nd.appendChild(document.createTextNode(focusGate.date + (focusGate.ref ? " · " + focusGate.ref : "")));
      panel.appendChild(nd);
    }

    // Latest dated closure: the focus panel holds the go-live blocker, but the
    // operating cadence keeps advancing — show the newest closed milestone so the
    // "now" panel reflects real progress instead of reading as frozen at the block.
    var latest = focus.latestDated;
    if (latest && (!focusGate || latest.id !== focusGate.id)) {
      var lc = htmlEl("p", "arc-now-latest");
      lc.appendChild(htmlEl("span", "arc-now-date-key", "latest closed "));
      lc.appendChild(document.createTextNode(
        (latest.code || latest.id) + " · " + latest.date + (latest.ref ? " · " + latest.ref : "")));
      panel.appendChild(lc);
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

    // Backfilled completion date + its provenance ref (present only on dated done items;
    // see the date-ownership backfill). Absent items render no date line — graceful.
    if (item.date) {
      var dateMeta = htmlEl("p", "arc-detail-meta arc-detail-date");
      dateMeta.appendChild(htmlEl("span", "arc-detail-meta-key", "date "));
      dateMeta.appendChild(document.createTextNode(item.date + (item.ref ? " · " + item.ref : "")));
      panel.appendChild(dateMeta);
    }

    if (item.note) {
      panel.appendChild(htmlEl("p", "arc-detail-note", item.note));
    }

    // Dependency edges, mirroring the on-chart dashed lines: precedents (what this
    // depends on / is gated by) and antecedents (what depends on / is gated by it).
    var allItems = (data && data.items) || [];
    var precedents = (item.deps || []).map(function (id) { return byId[id]; }).filter(Boolean);
    var antecedents = allItems.filter(function (it) { return (it.deps || []).indexOf(item.id) !== -1; });
    function depLine(keyText, list, cls) {
      if (!list.length) return;
      var p = htmlEl("p", "arc-detail-deps " + cls);
      p.appendChild(htmlEl("span", "arc-detail-meta-key", keyText));
      list.forEach(function (it, i) {
        if (i) p.appendChild(document.createTextNode(", "));
        var span = htmlEl("span", "arc-detail-dep", it.code || it.id || "");
        if (it.label) span.title = it.label;
        p.appendChild(span);
      });
      panel.appendChild(p);
    }
    depLine("depends on ", precedents, "arc-detail-deps-precedent");
    depLine("depended on by ", antecedents, "arc-detail-deps-antecedent");

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

  // ---- progress evidence snapshot ------------------------------------------

  function appendList(parent, className, values) {
    if (!Array.isArray(values) || !values.length) return;
    var list = htmlEl("ul", className);
    values.forEach(function (value) {
      list.appendChild(htmlEl("li", "", value));
    });
    parent.appendChild(list);
  }

  function renderProgressEvidence(root) {
    var s = root._arc;
    var panel = s && s.progressPanel;
    if (!panel) return;
    clearNode(panel);

    var payload = progressEvidence();
    var privacy = payload && payload.privacy;
    if (!payload || payload.schema_version !== 1 || !privacy || privacy.public_safe !== true) {
      panel.appendChild(htmlEl("h3", "", "Progress evidence snapshot"));
      panel.appendChild(htmlEl("p", "arc-progress-note", "No public-safe progress evidence export is available."));
      return;
    }

    var source = progressSource() || {};
    var items = Array.isArray(payload.items) ? payload.items : [];
    var omitted = Array.isArray(payload.omitted_sources) ? payload.omitted_sources : [];

    var header = htmlEl("div", "arc-progress-header");
    var titleWrap = htmlEl("div", "");
    titleWrap.appendChild(htmlEl("div", "arc-panel-eyebrow", "operation export"));
    titleWrap.appendChild(htmlEl("h3", "", "Progress evidence snapshot"));
    titleWrap.appendChild(htmlEl(
      "p",
      "arc-progress-note",
      "Display-only snapshot from civilization-operation. It is not live truth, not gate closure, and not production authority."
    ));
    header.appendChild(titleWrap);

    var sourceBox = htmlEl("p", "arc-progress-source");
    sourceBox.appendChild(document.createTextNode("source "));
    appendSafeLink(sourceBox, source.operation_pr_url, source.operation_pr || "operation export", "arc-progress-link");
    if (source.operation_merge_commit) {
      sourceBox.appendChild(document.createTextNode(" at " + String(source.operation_merge_commit).slice(0, 12)));
    }
    header.appendChild(sourceBox);
    panel.appendChild(header);

    var metrics = htmlEl("dl", "arc-progress-metrics");
    [
      ["snapshot", payload.generated_at || "unknown"],
      ["items", String(items.length)],
      ["omitted", String(omitted.length)],
      ["privacy", (payload.privacy && payload.privacy.projection_policy) || "unknown"],
    ].forEach(function (row) {
      metrics.appendChild(htmlEl("dt", "", row[0]));
      metrics.appendChild(htmlEl("dd", "", row[1]));
    });
    panel.appendChild(metrics);

    var grid = htmlEl("div", "arc-progress-grid");
    items.forEach(function (item) {
      var card = htmlEl("article", "arc-progress-item");
      var head = htmlEl("div", "arc-progress-item-head");
      head.appendChild(htmlEl("strong", "", item.title || item.id || "Progress item"));
      head.appendChild(htmlEl("span", "arc-progress-chip", [item.kind, item.state].filter(Boolean).join(" / ")));
      card.appendChild(head);
      card.appendChild(htmlEl("p", "arc-progress-summary", item.public_summary || ""));

      var meta = htmlEl("p", "arc-progress-meta");
      meta.appendChild(document.createTextNode((item.source_repo || "unknown") + " "));
      appendSafeLink(meta, item.source_url, item.source_ref || "source", "arc-progress-link");
      if (item.evidence_state || item.authority_state) {
        meta.appendChild(document.createTextNode(" - " + [item.evidence_state, item.authority_state].filter(Boolean).join(" / ")));
      }
      card.appendChild(meta);

      appendList(card, "arc-progress-list arc-progress-blockers", item.blockers);
      appendList(card, "arc-progress-list", item.limitations);
      grid.appendChild(card);
    });
    panel.appendChild(grid);

    if (omitted.length) {
      var omittedSection = htmlEl("section", "arc-progress-omitted");
      omittedSection.appendChild(htmlEl("h4", "", "Omitted sources"));
      var omittedList = htmlEl("ul", "");
      omitted.forEach(function (entry) {
        var li = htmlEl("li", "");
        li.appendChild(htmlEl("strong", "", entry.title || entry.id || "Omitted source"));
        li.appendChild(document.createTextNode(" - " + (entry.reason || "omitted") + ": " + (entry.public_summary || "")));
        omittedList.appendChild(li);
      });
      omittedSection.appendChild(omittedList);
      panel.appendChild(omittedSection);
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

    // Scroll-wheel zoom: wheel up = zoom in, wheel down = zoom out (snap to ZOOM_STEP,
    // clamped to the per-render maxZoom). Scoped to the standalone arc page so the
    // embedded sticky nav still scrolls the article normally (no scroll-trap). On the
    // standalone page preventDefault stops the page from scrolling while zooming.
    svg.addEventListener("wheel", function (event) {
      if (root.getAttribute("data-arc-standalone") !== "true") return;
      // Only a dominant-VERTICAL wheel zooms. A dominant-horizontal gesture (trackpad
      // sideways pan) falls through so it scrolls the zoomed .arc-frame instead of being
      // hijacked into a zoom-out.
      if (!event.deltaY || Math.abs(event.deltaX) > Math.abs(event.deltaY)) return;
      var dir = event.deltaY < 0 ? 1 : -1;
      var hi = s.maxZoom || ZOOM_ABS_MAX;
      var current = s.zoom || 1;
      var nz = clampZoom(current + dir * ZOOM_STEP, hi);
      if (nz === current) return;
      if (typeof event.preventDefault === "function") event.preventDefault();
      s.zoom = nz;
      writeZoom(nz);
      render(root, s.data);
    }, { passive: false });

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
        var hit = (event.target && event.target.closest) ? event.target : null;
        var zoomBtn = hit ? hit.closest("[data-arc-zoom]") : null;
        if (zoomBtn) {
          var act = zoomBtn.getAttribute("data-arc-zoom");
          var z = s.zoom || 1;
          var hi = s.maxZoom || ZOOM_BASE_MAX;
          if (act === "in") z = clampZoom(z + ZOOM_STEP, hi);
          else if (act === "out") z = clampZoom(z - ZOOM_STEP, hi);
          else z = 1; // "fit" readout button resets to whole-arc view
          if (z !== s.zoom) { s.zoom = z; writeZoom(z); render(root, s.data); }
          return;
        }
        var btn = hit ? hit.closest("[data-arc-group]") : null;
        if (!btn || btn.disabled) return;
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

    // Derive the max zoom from the frame width + chip-safe detail width, so a readable
    // detail view is always reachable no matter how narrow the frame is (at least
    // ZOOM_BASE_MAX on wide frames, capped at ZOOM_ABS_MAX).
    var detailW = Layout.detailWidth ? Layout.detailWidth(data) : width;
    var neededZoom = Math.ceil((detailW / Math.max(1, width)) / ZOOM_STEP) * ZOOM_STEP;
    s.maxZoom = Math.min(ZOOM_ABS_MAX, Math.max(ZOOM_BASE_MAX, neededZoom));
    s.zoom = clampZoom(s.zoom || 1, s.maxZoom);
    var layout = Layout.buildLayout(data, { width: width, collapsed: s.collapsed, groupBy: s.groupBy || "tracks", zoom: s.zoom });

    var svg = s.svg;
    svg.setAttribute("viewBox", "0 0 " + layout.contentWidth + " " + layout.contentHeight);
    if (s.zoom > 1) {
      // Zoomed in: render at content size so the frame scrolls horizontally for detail.
      svg.style.width = layout.contentWidth + "px";
      svg.style.height = layout.contentHeight + "px";
    } else {
      // Fit: clear the inline size so the CSS width:100% + viewBox scales the whole arc
      // to the frame — the entire arc is visible with no horizontal scroll.
      svg.style.width = "";
      svg.style.height = "";
    }
    clearNode(svg);

    Draw.drawAxis(svg, layout);
    Draw.drawTracks(svg, layout, s);
    if (s.selectedId != null && Draw.drawDeps) {
      var Onto = lib("CivOntology");
      var depEdges = (Onto && Onto.visibleDeps) ? Onto.visibleDeps((data.items) || [], s.selectedId) : [];
      Draw.drawDeps(svg, layout, depEdges, s.selectedId);
    }
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
    renderProgressEvidence(root);

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
        // Fail-closed on a degraded refresh: inflight.py still writes a payload (with
        // errors[] and possibly items:[]) when a gh/network/auth call fails, and
        // mergeInflight treats empty items as ok. A failed refresh must NOT masquerade
        // as a clean "live · updated" — surface a warn chip so missing live PRs are
        // never presented as current. Whatever items DID load still render.
        var errs = (inflight && Array.isArray(inflight.errors)) ? inflight.errors : [];
        var degraded = errs.length > 0;
        var liveData = {};
        for (var key in data) { if (Object.prototype.hasOwnProperty.call(data, key)) liveData[key] = data[key]; }
        liveData.items = merged.items;                  // new array — baked data untouched
        Array.prototype.forEach.call(roots, function (root) {
          if (root._arc) root._arc.ordinalById = null;  // recompute ordinals over the merged set
          render(root, liveData);
          setLiveChip(root,
            degraded
              ? ("live · stale (" + errs.length + " source error" + (errs.length === 1 ? "" : "s") + ")")
              : ("live · updated " + (merged.generated || "?")),
            !degraded);
        });
      })
      .catch(function (e) {
        if (typeof console !== "undefined") console.warn("inflight: fetch failed (keeping baked):", e && e.message);
        Array.prototype.forEach.call(roots, function (root) { setLiveChip(root, "live · unavailable", false); });
      });
  }

  // Live overlay is OPT-IN. It needs a host that generates dist/inflight.json
  // (currently parked — see civwiki-chart-current-direction memory). When it is not
  // enabled we skip the fetch entirely: no 404, no "live · unavailable" chip — the
  // baked arc stands on its own. Re-enable by setting window.CIV_ARC_LIVE = true or
  // data-arc-live="true" on a root, once a generator is wired up.
  function liveEnabled(roots) {
    if (typeof window !== "undefined" && window.CIV_ARC_LIVE === true) return true;
    for (var i = 0; i < roots.length; i++) {
      if (roots[i].getAttribute && roots[i].getAttribute("data-arc-live") === "true") return true;
    }
    return false;
  }

  function boot() {
    var data = (typeof window !== "undefined") ? window.CIVILIZATION_ARC_DATA : null;
    if (!data) return;
    var roots = document.querySelectorAll("[data-civilization-arc-nav]");
    Array.prototype.forEach.call(roots, function (root) { render(root, data); }); // baked first — never blank
    if (liveEnabled(roots)) loadInflight(roots, data);                            // overlay live only when enabled
  }

  if (typeof document !== "undefined") {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", boot);
    } else {
      boot();
    }
  }
})();
