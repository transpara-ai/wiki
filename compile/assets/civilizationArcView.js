// compile/assets/civilizationArcView.js
// "Where are we, and what's next?" — the arc page view (Item 2b-visual).
//
// Replaces the retired chronological-tracks engine (civilizationArcNav.js /
// civilizationArcLayout.js / civilizationArcDraw.js). Renders the freshness
// header, the now-panel (current phase · active now · next gate), and the
// phase spine as plain HTML from the validated data + CivOntology
// derivations. Design packet: docs/superpowers/specs/
// 2026-07-03-arc-2b-visual-packet.md (§2.2 D1–D5, §2.3).
//
// Isomorphic like the ontology: the pure derivations are exported for
// `node --test` (module.exports) and the browser (window.CivArcView); DOM
// rendering is browser-only. No DOM state beyond per-root scaffolding; no
// network beyond the existing same-origin inflight.json overlay fetch.
(function (root) {
  "use strict";

  var O = (typeof module !== "undefined" && module.exports)
    ? require("./civilizationOntology.js")
    : (root && root.CivOntology);

  // The two first-class piece types (spec §2.2). Goals (the perpetual
  // north-star, active at seq 0 forever) and demoted detail types never
  // count toward a phase's rollup or the frontier read.
  var PIECE_TYPES = { work: 1, gate: 1 };

  // D1 — fail-closed phase rollup over the phase's {work, gate} pieces.
  // Empty set => future, never done: CivOntology.rollupCriteria([]) returns
  // done (its allDone seed), which here would render an empty phase as
  // complete — the named fail-open lane this guard closes.
  function phaseState(items, sprintId) {
    var pieces = [];
    (items || []).forEach(function (it) {
      if (it && it.sprint === sprintId && PIECE_TYPES[it.type] === 1) pieces.push(it);
    });
    if (!pieces.length) return { status: "future", blocked: false, count: 0 };
    var r = O.rollupCriteria(pieces);
    return { status: r.status, blocked: r.blocked, count: pieces.length };
  }

  // Phase spine model. Collapse is the explicitly-proven branch: done AND
  // unblocked. A done+blocked phase (ontology-valid: all criteria done, one
  // carrying the overlay) must stay expanded with its ring (CFADA-r1 B3).
  function spine(items, sprints) {
    return (sprints || []).map(function (sp) {
      var st = phaseState(items, sp.id);
      return {
        id: sp.id, label: sp.label, status: st.status, blocked: st.blocked,
        count: st.count,
        collapsed: st.status === "done" && st.blocked === false,
      };
    });
  }

  // D2 — the current phase = sprint of the BAKED frontier item. Every
  // non-provable input is a deny-path (CFADA-r1 B2 + r2 N1), never a guess:
  //   no-settled          — valid all-planned/future input has no frontier
  //   ambiguous-frontier  — settled max-seq items name different sprints
  //   unknown-sprint      — the frontier sprint is not in sprints[]
  // Frontier candidates use the SAME {work, gate} allowlist as the phase
  // rollup — a settled goal/decision at the max seq must never mark a phase
  // the spine itself renders as future with 0 pieces (ready-CFAR r3).
  function currentPhase(items, sprints) {
    var settled = [];
    (items || []).forEach(function (it) {
      if (it && PIECE_TYPES[it.type] === 1 && O.SETTLED[it.status] &&
          typeof it.seq === "number" && !isNaN(it.seq)) settled.push(it);
    });
    if (!settled.length) return { ok: false, reason: "no-settled" };
    var max = -Infinity;
    settled.forEach(function (it) { if (it.seq > max) max = it.seq; });
    var atMax = settled.filter(function (it) { return it.seq === max; });
    var sprintIds = {};
    atMax.forEach(function (it) { sprintIds[String(it.sprint)] = true; });
    var distinct = Object.keys(sprintIds);
    if (distinct.length !== 1) return { ok: false, reason: "ambiguous-frontier" };
    var sprintId = distinct[0];
    var known = (sprints || []).some(function (sp) { return sp && sp.id === sprintId; });
    if (!known) return { ok: false, reason: "unknown-sprint" };
    var item = atMax.slice().sort(function (a, b) {
      return String(a.id) < String(b.id) ? -1 : 1;
    })[0];
    return { ok: true, sprintId: sprintId, item: item };
  }

  // Total (seq, id) candidate order: equal-seq candidates resolve by id,
  // independent of array order (CFADA-r1 B2).
  function bySeqId(a, b) {
    if (a.seq !== b.seq) return a.seq - b.seq;
    return String(a.id) < String(b.id) ? -1 : 1;
  }

  // D3 — the next blocking gate, over BAKED items only (live overlay items
  // are always type "work" and can move neither the candidates nor the
  // frontier). Priority: an existing hard stop (blocked, wherever it sits)
  // outranks the nearest planned gate ahead, which outranks the nearest
  // future gate ahead; nothing matches => null (the panel renders an
  // explicit "frontier open" state — no healthy-looking default).
  function nextBlockingGate(items) {
    var gates = (items || []).filter(function (it) { return it && it.type === "gate"; });
    var blocked = gates.filter(function (g) { return g.blocked === true; }).sort(bySeqId);
    if (blocked.length) return blocked[0];
    var now = O.deriveNow(items || []);
    var planned = gates.filter(function (g) { return g.status === "planned" && g.seq > now; }).sort(bySeqId);
    if (planned.length) return planned[0];
    var future = gates.filter(function (g) { return g.status === "future" && g.seq > now; }).sort(bySeqId);
    if (future.length) return future[0];
    return null;
  }

  // D4 — active work rows for the "active now" column, frontier-first.
  // Runs over the MERGED set so live overlay rows appear with their stamps.
  function activeWork(items) {
    return (items || [])
      .filter(function (it) { return it && it.type === "work" && it.status === "active"; })
      .sort(function (a, b) {
        if (a.seq !== b.seq) return b.seq - a.seq;
        return String(a.id) < String(b.id) ? -1 : 1;
      });
  }

  // D5 — latest dated closure among BAKED done items (date tie → id order).
  function latestClosed(items) {
    var best = null;
    (items || []).forEach(function (it) {
      if (!it || it.status !== "done" || typeof it.date !== "string") return;
      if (!/^\d{4}-\d{2}-\d{2}$/.test(it.date)) return;
      if (!best || it.date > best.date ||
          (it.date === best.date && String(it.id) < String(best.id))) best = it;
    });
    return best;
  }

  var api = {
    PIECE_TYPES: PIECE_TYPES,
    phaseState: phaseState,
    spine: spine,
    currentPhase: currentPhase,
    nextBlockingGate: nextBlockingGate,
    activeWork: activeWork,
    latestClosed: latestClosed,
    // exported for node --test of the fail-closed link gate (hoisted decls)
    safeHref: safeHref,
    isRetiredInternal: isRetiredInternal,
    canonicalArcSlug: canonicalArcSlug,
  };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (root) root.CivArcView = api;

  // ---- DOM rendering (browser only) -----------------------------------------
  if (typeof document === "undefined") return;

  function htmlEl(name, className, text) {
    var el = document.createElement(name);
    if (className) el.className = className;
    if (text !== undefined && text !== null) el.textContent = text;
    return el;
  }

  function clearNode(node) {
    if (!node) return;
    if (node.replaceChildren) { node.replaceChildren(); return; }
    while (node.firstChild) node.removeChild(node.firstChild);
  }

  // Fail-closed allowlist: permits http(s), anchors, root-relative (single /),
  // and bare relative paths that carry no scheme. Rejects any scheme: URI,
  // protocol-relative // or \\, control/whitespace chars, empty/non-string.
  // A retired article is a tombstone reachable by direct link only — no
  // generated live link may point to it, including arc-view data hrefs, so
  // the browser gate mirrors the server-side gate_internal_links, including
  // its canonicalization: percent-decode + dot-segment normalization so a
  // browser-equivalent spelling (`slug%2ehtml`, `x/../slug.html`) cannot dodge
  // the retired check (CFAR r20/r22).
  function canonicalArcSlug(href) {
    if (typeof href !== "string") return null;
    var h = href.split("#")[0].split("?")[0];
    try { h = decodeURIComponent(h); } catch (e) { return null; }
    h = h.replace(/\\/g, "/");  // browsers treat backslash as a path separator
    h = h.replace(/^\//, "");
    var parts = h.split("/"), out = [];
    for (var i = 0; i < parts.length; i++) {
      var p = parts[i];
      if (p === "" || p === ".") continue;
      if (p === "..") { out.pop(); continue; }
      out.push(p);
    }
    var m = /^([A-Za-z0-9_][A-Za-z0-9_-]*)\.html$/.exec(out.join("/"));
    return m ? m[1] : null;
  }
  function isRetiredInternal(href) {
    var slug = canonicalArcSlug(href);
    if (!slug) return false;
    var retired = (typeof window !== "undefined" && window.CIVWIKI_RETIRED_SLUGS) || [];
    for (var i = 0; i < retired.length; i++) { if (retired[i] === slug) return true; }
    return false;
  }
  function safeHref(href) {
    if (typeof href !== "string" || href === "") return null;
    if (/[\x00-\x20\x7f]/.test(href)) return null;
    if (/^[\\/]{2}/.test(href)) return null;
    if (isRetiredInternal(href)) return null;  // retired target → render as text
    if (/^https?:\/\//i.test(href)) return href;
    if (href.charAt(0) === "#" || href.charAt(0) === "/") return href;
    var sep = href.search(/[/#?]/);
    var colon = href.indexOf(":");
    if (colon !== -1 && (sep === -1 || colon < sep)) return null;
    return href;
  }
  function isExternalHref(href) { return /^https?:\/\//i.test(href); }

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

  function progressEvidence() {
    return (typeof window !== "undefined") ? window.CIVILIZATION_PROGRESS_EVIDENCE : null;
  }
  function progressSource() {
    return (typeof window !== "undefined") ? window.CIVILIZATION_PROGRESS_EVIDENCE_SOURCE : null;
  }
  function liveReaderCorrectionEvidence() {
    return (typeof window !== "undefined") ? window.CIVILIZATION_LIVE_READER_CORRECTION : null;
  }

  // ---- scaffold --------------------------------------------------------------

  function ensureScaffold(el) {
    el._arcView = el._arcView || {};
    var s = el._arcView;
    if (s.scaffolded) return s;

    el.classList.add("civilization-arc-view");
    if (el.getAttribute("data-arc-standalone") === "true") {
      el.classList.add("arc-view-standalone");
    }
    if (!el.getAttribute("aria-label")) el.setAttribute("aria-label", "Civilization arc");

    clearNode(el);
    var header = htmlEl("div", "arc-freshness");
    var nowPanel = htmlEl("section", "arc-now-panel");
    nowPanel.setAttribute("aria-label", "You are here — current phase, active work, next gate");
    var spineEl = htmlEl("ol", "arc-spine");
    spineEl.setAttribute("aria-label", "Phase spine");
    var progressPanel = htmlEl("section", "arc-progress-panel");
    progressPanel.setAttribute("aria-label", "Progress evidence snapshot");
    var liveReaderPanel = htmlEl("section", "arc-live-reader-panel");
    liveReaderPanel.setAttribute("aria-label", "Live Reader Correction Proof");
    el.append(header, nowPanel, spineEl, progressPanel, liveReaderPanel);

    s.scaffolded = true;
    s.header = header;
    s.nowPanel = nowPanel;
    s.spine = spineEl;
    s.progressPanel = progressPanel;
    s.liveReaderPanel = liveReaderPanel;
    return s;
  }

  // ---- freshness header ------------------------------------------------------

  function renderFreshness(s, baked) {
    clearNode(s.header);
    s.header.appendChild(htmlEl("div", "arc-panel-eyebrow", "civilization arc · where are we, and what's next?"));
    var latest = latestClosed(baked.items);
    if (latest) {
      var line = htmlEl("p", "arc-freshness-latest");
      line.appendChild(htmlEl("span", "arc-freshness-key", "latest closed "));
      line.appendChild(document.createTextNode(
        (latest.code || latest.id) + " · " + latest.date + (latest.ref ? " · " + latest.ref : "")));
      s.header.appendChild(line);
    } else {
      s.header.appendChild(htmlEl("p", "arc-freshness-latest", "no dated closure recorded"));
    }
    if (s.liveChip) s.header.appendChild(s.liveChip); // keep the chip through re-renders
  }

  // ---- now-panel ------------------------------------------------------------

  var PHASE_UNRESOLVED = {
    "no-settled": "frontier phase unresolved (no settled items)",
    "ambiguous-frontier": "frontier phase unresolved (ambiguous frontier)",
    "unknown-sprint": "frontier phase unresolved (unknown sprint)",
  };

  function evidenceStamp(item, liveInfo) {
    var stamp = htmlEl("div", "arc-evidence");
    stamp.appendChild(htmlEl("span", "arc-evidence-prov arc-evidence-prov-" + (item.provenance || "unknown"),
      item.provenance || "unstamped"));
    var isLive = liveInfo && liveInfo.ids && liveInfo.ids[item.id] === true;
    var hasSource = false;
    if (item.ref) {
      stamp.appendChild(htmlEl("span", "arc-evidence-ref", item.ref));
      hasSource = true;
    }
    if (item.date) {
      stamp.appendChild(htmlEl("span", "arc-evidence-date", item.date));
      hasSource = true;
    }
    if (item.href) {
      var linked = appendSafeLink(stamp, item.href, "source", "arc-evidence-link");
      if (linked) hasSource = true;
    }
    if (item.author) stamp.appendChild(htmlEl("span", "arc-evidence-author", "@" + item.author));
    if (isLive) {
      stamp.appendChild(htmlEl("span", "arc-evidence-live",
        "live · observed " + ((liveInfo && liveInfo.generated) || "?")));
      hasSource = true;
    }
    // Absence renders honestly: never blank, never fabricated.
    if (!hasSource) stamp.appendChild(htmlEl("span", "arc-evidence-none", "no source ref"));
    return stamp;
  }

  function renderNowPanel(s, baked, merged, liveInfo) {
    var panel = s.nowPanel;
    clearNode(panel);

    panel.appendChild(htmlEl("div", "arc-panel-eyebrow", "you are here"));

    var phase = currentPhase(baked.items, baked.sprints);
    if (phase.ok) {
      var label = phase.sprintId;
      (baked.sprints || []).forEach(function (sp) { if (sp && sp.id === phase.sprintId) label = sp.label; });
      panel.appendChild(htmlEl("h3", "arc-now-phase", label));
      var fr = htmlEl("p", "arc-now-frontier");
      fr.appendChild(htmlEl("span", "arc-freshness-key", "frontier "));
      fr.appendChild(document.createTextNode(
        (phase.item.code || phase.item.id) + " · seq " + phase.item.seq + " · derived"));
      panel.appendChild(fr);
    } else {
      panel.appendChild(htmlEl("p", "arc-now-unresolved",
        PHASE_UNRESOLVED[phase.reason] || "frontier phase unresolved"));
    }

    var cols = htmlEl("div", "arc-now-columns");

    // column A — active now (merged set: live overlay rows appear here)
    var colA = htmlEl("div", "arc-now-col");
    colA.appendChild(htmlEl("div", "arc-panel-subhead", "active now"));
    var rows = activeWork(merged.items);
    var list = htmlEl("ul", "arc-now-list");
    if (!rows.length) {
      list.appendChild(htmlEl("li", "arc-now-empty", "no active work items"));
    }
    rows.forEach(function (item) {
      var li = htmlEl("li", "arc-now-item");
      li.setAttribute("data-arc-active-item", item.id);
      var dotStatus = item.blocked ? "blocked" : "active";
      li.appendChild(htmlEl("span", "arc-status-dot arc-status-dot-" + dotStatus));
      li.appendChild(htmlEl("span", "arc-now-item-code", item.code || item.id));
      li.appendChild(htmlEl("span", "arc-now-item-text", item.label || ""));
      li.appendChild(evidenceStamp(item, liveInfo));
      list.appendChild(li);
    });
    colA.appendChild(list);

    // column B — next gate (baked set: gates never come from the overlay)
    var colB = htmlEl("div", "arc-now-col");
    colB.appendChild(htmlEl("div", "arc-panel-subhead", "next gate"));
    var gate = nextBlockingGate(baked.items);
    if (!gate) {
      colB.appendChild(htmlEl("p", "arc-gate-none", "no blocking gate ahead — frontier open"));
    } else {
      var head = htmlEl("div", "arc-now-head");
      head.appendChild(htmlEl("span", "arc-now-code", gate.code || gate.id));
      if (gate.blocked === true) {
        head.appendChild(htmlEl("span", "arc-badge arc-badge-blocked",
          "blocked · " + (gate.blocked_reason || "?")));
      } else {
        head.appendChild(htmlEl("span", "arc-badge arc-badge-" + (gate.status || "future"),
          gate.status || "?"));
      }
      colB.appendChild(head);
      colB.appendChild(htmlEl("p", "arc-now-label", gate.label || ""));
      // the gate's OWN provenance — e.g. gate-k-go-live's only evidence is
      // its gate-level ref; criteria may carry none (evidence-honesty rule)
      var gateEvidence = htmlEl("div", "arc-gate-evidence");
      gateEvidence.appendChild(evidenceStamp(gate, null));
      colB.appendChild(gateEvidence);
      if (Array.isArray(gate.criteria) && gate.criteria.length) {
        var crits = htmlEl("ul", "arc-gate-criteria");
        gate.criteria.forEach(function (c) {
          if (!c) return;
          var li = htmlEl("li", "arc-gate-criterion" +
            (c.id === gate.blocked_criterion ? " arc-criterion-blocked" : ""));
          li.appendChild(htmlEl("span", "arc-status-dot arc-status-dot-" + (c.blocked ? "blocked" : (c.status || "future"))));
          li.appendChild(htmlEl("span", "arc-criterion-label", c.label || c.id));
          if (c.ref) li.appendChild(htmlEl("span", "arc-evidence-ref", c.ref));
          crits.appendChild(li);
        });
        colB.appendChild(crits);
        // recomputed at render time — never echoed from stored fields
        var roll = O.rollupCriteria(gate.criteria);
        colB.appendChild(htmlEl("p", "arc-gate-rollup",
          "fail-closed rollup: " + roll.status + (roll.blocked ? " · blocked" : "")));
      } else {
        colB.appendChild(htmlEl("p", "arc-gate-none", "no criteria recorded"));
      }
    }

    cols.append(colA, colB);
    panel.appendChild(cols);
  }

  // ---- phase spine -----------------------------------------------------------

  function renderSpine(s, baked) {
    var el = s.spine;
    clearNode(el);
    var phases = spine(baked.items, baked.sprints);
    var phase = currentPhase(baked.items, baked.sprints);
    phases.forEach(function (p) {
      var li = htmlEl("li",
        "arc-phase arc-phase-" + p.status +
        (p.blocked ? " arc-phase-blocked" : "") +
        (p.collapsed ? " arc-phase-collapsed" : ""));
      li.setAttribute("data-arc-phase", p.id);
      li.setAttribute("data-arc-phase-status", p.status);
      if (phase.ok && phase.sprintId === p.id) {
        li.classList.add("arc-phase-now");
        li.setAttribute("data-arc-phase-now", "true");
        li.appendChild(htmlEl("span", "arc-phase-now-tag", "now"));
      }
      li.appendChild(htmlEl("span", "arc-phase-label", p.label));
      li.appendChild(htmlEl("span", "arc-phase-count",
        p.count + (p.blocked ? " · blocked" : "")));
      el.appendChild(li);
    });
    if (!phase.ok) {
      var notice = htmlEl("li", "arc-spine-notice",
        PHASE_UNRESOLVED[phase.reason] || "frontier phase unresolved");
      el.appendChild(notice);
    }
  }

  // ---- ported governance-honesty panels (DOM shape unchanged) ----------------

  function appendList(parent, className, values) {
    if (!Array.isArray(values) || !values.length) return;
    var list = htmlEl("ul", className);
    values.forEach(function (value) {
      list.appendChild(htmlEl("li", "", value));
    });
    parent.appendChild(list);
  }

  function renderProgressEvidence(s) {
    var panel = s.progressPanel;
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
      "Display-only snapshot from operation. It is not live truth, not gate closure, and not production authority."
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

  function isObject(value) {
    return value && typeof value === "object" && !Array.isArray(value);
  }

  function validLiveReaderCorrection(payload) {
    if (!isObject(payload) || payload.schema_version !== 1 || payload.display_only !== true) return false;
    if (!payload.privacy || payload.privacy.public_safe !== true || payload.privacy.network_access !== "none") return false;
    if (!payload.source || payload.source.network_access !== "none") return false;
    if (!payload.freshness || ["fresh", "fixture", "source_recorded"].indexOf(payload.freshness.state) === -1) return false;
    var allowedEvidence = {
      source_recorded: 1, corrected: 1, superseded: 1, stale: 1, missing: 1, unavailable: 1,
    };
    var allowedFreshness = {
      fresh: 1, fixture: 1, source_recorded: 1, stale: 1, missing: 1, unavailable: 1,
    };
    var allowedOmitted = { missing: 1, stale: 1, unavailable: 1 };
    var items = Array.isArray(payload.items) ? payload.items : [];
    if (!items.length) return false;
    var byId = {};
    for (var i = 0; i < items.length; i++) {
      var item = items[i];
      if (!item || item.display_only !== true || !item.id || !item.limitation) return false;
      if (!allowedEvidence[item.evidence_state] || !allowedFreshness[item.freshness_state]) return false;
      byId[item.id] = item;
    }
    var corrections = Array.isArray(payload.corrections) ? payload.corrections : [];
    for (var c = 0; c < corrections.length; c++) {
      var correction = corrections[c];
      if (!correction || correction.display_only !== true || !correction.limitation) return false;
      if (!byId[correction.supersedes_item_id] || !byId[correction.corrected_item_id]) return false;
    }
    var omitted = Array.isArray(payload.omitted_sources) ? payload.omitted_sources : [];
    for (var o = 0; o < omitted.length; o++) {
      var source = omitted[o];
      if (!source || !allowedOmitted[source.freshness_state] || !source.reason || !source.public_summary) return false;
    }
    return true;
  }

  function appendLiveReaderSourceRefs(parent, refs) {
    if (!Array.isArray(refs) || !refs.length) return;
    var meta = htmlEl("p", "arc-progress-meta");
    meta.appendChild(htmlEl("span", "arc-detail-meta-key", "source "));
    refs.forEach(function (ref, idx) {
      if (idx) meta.appendChild(document.createTextNode(" · "));
      var label = [ref.repo, ref.ref].filter(Boolean).join(" ");
      appendSafeLink(meta, ref.url, label || "source", "arc-progress-link");
    });
    parent.appendChild(meta);
  }

  function renderLiveReaderCorrection(s) {
    var panel = s.liveReaderPanel;
    if (!panel) return;
    clearNode(panel);

    var payload = liveReaderCorrectionEvidence();
    var section = htmlEl("section", "arc-progress-omitted arc-live-reader-correction");
    section.setAttribute("aria-label", "Live Reader Correction Proof");

    var header = htmlEl("div", "arc-progress-header");
    var titleWrap = htmlEl("div", "");
    titleWrap.appendChild(htmlEl("div", "arc-panel-eyebrow", "operation correction export"));
    titleWrap.appendChild(htmlEl("h3", "", "Live Reader Correction Proof"));
    titleWrap.appendChild(htmlEl(
      "p",
      "arc-progress-note",
      "Display-only Event 14 fixture from operation. It is not live truth, not Gate X closure, and not production authority."
    ));
    header.appendChild(titleWrap);
    section.appendChild(header);

    if (!validLiveReaderCorrection(payload)) {
      section.appendChild(htmlEl("p", "arc-progress-note", "No valid public-safe correction export is available."));
      panel.appendChild(section);
      return;
    }

    var sourceBox = htmlEl("p", "arc-progress-source");
    sourceBox.appendChild(document.createTextNode("source "));
    appendSafeLink(sourceBox, payload.source.operation_pr_url, payload.source.operation_pr || "operation export", "arc-progress-link");
    if (payload.source.operation_merge_commit) {
      sourceBox.appendChild(document.createTextNode(" at " + String(payload.source.operation_merge_commit).slice(0, 12)));
    }
    section.appendChild(sourceBox);

    var metrics = htmlEl("dl", "arc-progress-metrics");
    [
      ["generated", payload.generated_at || "unknown"],
      ["freshness", payload.freshness.state || "unknown"],
      ["items", String((payload.items || []).length)],
      ["corrections", String((payload.corrections || []).length)],
      ["omitted", String((payload.omitted_sources || []).length)],
    ].forEach(function (row) {
      metrics.appendChild(htmlEl("dt", "", row[0]));
      metrics.appendChild(htmlEl("dd", "", row[1]));
    });
    section.appendChild(metrics);

    var grid = htmlEl("div", "arc-progress-grid");
    (payload.items || []).forEach(function (item) {
      var card = htmlEl("article", "arc-progress-item");
      var head = htmlEl("div", "arc-progress-item-head");
      head.appendChild(htmlEl("strong", "", item.title || item.id || "Correction item"));
      head.appendChild(htmlEl("span", "arc-progress-chip", [item.evidence_state, item.freshness_state].filter(Boolean).join(" / ")));
      card.appendChild(head);
      card.appendChild(htmlEl("p", "arc-progress-summary", item.public_summary || ""));
      appendLiveReaderSourceRefs(card, item.source_refs);
      appendList(card, "arc-progress-list", [item.limitation]);
      grid.appendChild(card);
    });
    section.appendChild(grid);

    if (Array.isArray(payload.corrections) && payload.corrections.length) {
      var corrections = htmlEl("section", "arc-progress-omitted");
      corrections.appendChild(htmlEl("h4", "", "Corrections"));
      var list = htmlEl("ul", "");
      payload.corrections.forEach(function (correction) {
        var li = htmlEl("li", "");
        li.appendChild(htmlEl("strong", "", correction.correction_id || "correction"));
        li.appendChild(document.createTextNode(
          " - corrected " + (correction.prior_public_state || "prior") +
          " to " + (correction.corrected_state || "current") +
          ": " + (correction.correction_reason || "")
        ));
        list.appendChild(li);
      });
      corrections.appendChild(list);
      section.appendChild(corrections);
    }

    if (Array.isArray(payload.omitted_sources) && payload.omitted_sources.length) {
      var omittedSection = htmlEl("section", "arc-progress-omitted");
      omittedSection.appendChild(htmlEl("h4", "", "Missing or unavailable sources"));
      var omittedList = htmlEl("ul", "");
      payload.omitted_sources.forEach(function (entry) {
        var li = htmlEl("li", "");
        li.appendChild(htmlEl("strong", "", entry.title || entry.id || "Omitted source"));
        li.appendChild(document.createTextNode(
          " - " + (entry.freshness_state || "unavailable") +
          " / " + (entry.reason || "omitted") +
          ": " + (entry.public_summary || "")
        ));
        omittedList.appendChild(li);
      });
      omittedSection.appendChild(omittedList);
      section.appendChild(omittedSection);
    }

    panel.appendChild(section);
  }

  // ---- render + live overlay --------------------------------------------------

  // baked drives the frontier/phase/next-gate/freshness reads; merged (when
  // the live overlay lands) drives only the active-now column. Curated arc =
  // baked; live overlay = evidence (packet §1: live items are all tagged
  // "stewardship" as a labeling convenience — never an arc-placement claim).
  function render(el, baked, merged, liveInfo) {
    var s = ensureScaffold(el);
    renderFreshness(s, baked);
    renderNowPanel(s, baked, merged || baked, liveInfo || null);
    renderSpine(s, baked);
    renderProgressEvidence(s);
    renderLiveReaderCorrection(s);
  }

  function renderError(el, errors) {
    el.classList.add("civilization-arc-view");
    clearNode(el);
    var box = htmlEl("div", "arc-error");
    box.setAttribute("role", "alert");
    box.appendChild(htmlEl("strong", "", "Arc data failed validation — chart withheld (fail-closed)."));
    box.appendChild(htmlEl("p", "", (errors || []).length + " validation error(s); see the browser console."));
    el.appendChild(box);
  }

  function setLiveChip(el, text, ok) {
    var s = el._arcView;
    if (!s) return;
    var chip = s.liveChip;
    if (!chip) {
      chip = htmlEl("div", "arc-live-chip");
      s.liveChip = chip;
      (s.header || el).appendChild(chip);
    }
    chip.classList.toggle("arc-live-chip-warn", !ok);
    chip.textContent = text;
  }

  // Fetch dist/inflight.json, overlay the live derived items via the
  // ontology's pure mergeInflight, and re-render the active-now column.
  // Fail-safe: missing fetch, a non-ok response, a rejected promise, or a
  // rejected merge all keep the baked render. A degraded refresh (payload
  // errors[]) must NOT masquerade as a clean "live · updated".
  function loadInflight(roots, baked) {
    if (typeof fetch !== "function") return;            // no fetch (SSR/jsdom default) → baked only
    if (!O || !O.mergeInflight) return;
    fetch("inflight.json", { cache: "no-store" })
      .then(function (resp) { if (!resp || !resp.ok) throw new Error("inflight HTTP"); return resp.json(); })
      .then(function (inflight) {
        var merged = O.mergeInflight(baked, inflight);
        if (!merged.ok) {
          if (typeof console !== "undefined") console.warn("inflight: overlay rejected (fail-closed):", merged.errors);
          Array.prototype.forEach.call(roots, function (el) { setLiveChip(el, "live · unavailable", false); });
          return;
        }
        var errs = (inflight && Array.isArray(inflight.errors)) ? inflight.errors : [];
        var degraded = errs.length > 0;
        var liveIds = {};
        ((inflight && inflight.items) || []).forEach(function (it) {
          if (it && it.id != null) liveIds[it.id] = true;
        });
        var mergedData = { items: merged.items, sprints: baked.sprints };
        Array.prototype.forEach.call(roots, function (el) {
          render(el, baked, mergedData, { ids: liveIds, generated: merged.generated || "?" });
          setLiveChip(el,
            degraded
              ? ("live · stale (" + errs.length + " source error" + (errs.length === 1 ? "" : "s") + ")")
              : ("live · updated " + (merged.generated || "?")),
            !degraded);
        });
      })
      .catch(function (e) {
        if (typeof console !== "undefined") console.warn("inflight: fetch failed (keeping baked):", e && e.message);
        Array.prototype.forEach.call(roots, function (el) { setLiveChip(el, "live · unavailable", false); });
      });
  }

  function liveEnabled(roots) {
    if (typeof window !== "undefined" && window.CIV_ARC_LIVE === true) return true;
    for (var i = 0; i < roots.length; i++) {
      if (roots[i].getAttribute && roots[i].getAttribute("data-arc-live") === "true") return true;
    }
    return false;
  }

  function boot() {
    var data = (typeof window !== "undefined") ? window.CIVILIZATION_ARC_DATA : null;
    if (!data || !O) return;
    var roots = document.querySelectorAll("[data-civilization-arc]");
    if (!roots.length) return;
    // Render only proven-valid data: an invalid baked set renders a visible
    // error notice, never a healthy-looking chart (fail loud, fail closed).
    var v = O.validateItems(data.items);
    if (!v.ok) {
      if (typeof console !== "undefined") console.error("arc data failed validation:", v.errors);
      Array.prototype.forEach.call(roots, function (el) { renderError(el, v.errors); });
      return;
    }
    Array.prototype.forEach.call(roots, function (el) { render(el, data, null, null); }); // baked first — never blank
    if (liveEnabled(roots)) loadInflight(roots, data);
  }

  if (typeof document !== "undefined") {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", boot);
    } else {
      boot();
    }
  }
})(typeof window !== "undefined" ? window : null);
