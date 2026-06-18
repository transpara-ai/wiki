// compile/assets/civilizationOntology.js
// Pure contract for the Civilization arc. Browser (window.CivOntology) + Node (module.exports). No DOM.
(function (root) {
  "use strict";

  var STATUS_ORDER = ["future", "planned", "active", "done"];
  var SETTLED = { active: true, done: true };           // allowed left of "now"
  var NODE_TYPES = ["work", "goal", "order", "gate", "artifact", "surface",
    "actor", "phase", "event", "decision", "conflict",
    "policy", "invariant", "resource", "capability"];
  var PROVENANCE = ["reconstructed", "derived"];
  var STATUS_LANES = ["done", "active", "blocked", "planned", "future"];
  // Fixed lane order for the "gate" grouping, which lanes by gate FAMILY.
  // Lanes not in this list are appended alphabetically, before "(ungated)".
  var GATE_FAMILIES = [
    "v3.9 milestones (A-J)",
    "Deployment register (G-0..G-8.4)",
    "v4.0 (K/L)",
    "Release & security gates (v3.9)",
    "(ungated)",
  ];

  // "now" on the sequence axis = the frontier: the largest seq among settled (done/active) items.
  function deriveNow(items) {
    var now = -Infinity;
    for (var i = 0; i < items.length; i++) {
      if (!items[i]) continue;
      if (SETTLED[items[i].status] && items[i].seq > now) now = items[i].seq;
    }
    return now === -Infinity ? 0 : now;
  }

  function validateItems(items) {
    var errors = [];
    if (!Array.isArray(items)) return { ok: false, errors: ["items is not an array"] };
    var now = deriveNow(items);
    var seen = {};
    items.forEach(function (it, idx) {
      if (!it || typeof it !== "object") { errors.push("item[" + idx + "]: not an object"); return; }
      var where = "item[" + idx + "] " + (it.id ? it.id : "(no id)");
      if (!it.id) errors.push(where + ": missing id");
      else if (seen[it.id]) errors.push(where + ": duplicate id");
      else seen[it.id] = true;
      if (NODE_TYPES.indexOf(it.type) === -1) errors.push(where + ": invalid type '" + it.type + "'");
      if (STATUS_ORDER.indexOf(it.status) === -1) errors.push(where + ": invalid status '" + it.status + "'");
      if (PROVENANCE.indexOf(it.provenance) === -1) errors.push(where + ": invalid provenance '" + it.provenance + "'");
      if (typeof it.seq !== "number" || isNaN(it.seq)) errors.push(where + ": seq must be a number");
      if (!it.sprint) errors.push(where + ": missing sprint");
      if (!Array.isArray(it.repo)) errors.push(where + ": repo must be an array");
      if (typeof it.seq === "number" && !isNaN(it.seq) && it.seq < now && !SETTLED[it.status]) {
        errors.push(where + ": status '" + it.status + "' at seq " + it.seq +
          " is left of now (" + now + ") — past items must be done/active");
      }
    });
    return { ok: errors.length === 0, errors: errors };
  }

  function laneOf(it, dim) {
    if (dim === "status") return it.blocked ? "blocked" : it.status;
    if (dim === "repo") return (it.repo && it.repo[0]) || "(none)";
    if (dim === "sprint") return it.sprint || "(none)";
    if (dim === "gate") return it.family || "(ungated)";
    if (dim === "actor") return actorOf(it);
    return "(none)";
  }
  function groupBy(items, dim) {
    var map = {}, order = [];
    items.forEach(function (it) {
      var lane = laneOf(it, dim);
      if (!map[lane]) { map[lane] = []; order.push(lane); }
      map[lane].push(it);
    });
    if (dim === "status") {
      order = STATUS_LANES.filter(function (l) { return map[l]; });
    } else if (dim === "gate") {
      // Order present lanes by GATE_FAMILIES; any lane not in that list is
      // appended alphabetically, immediately before "(ungated)".
      var known = GATE_FAMILIES.filter(function (l) { return map[l]; });
      var extras = order.filter(function (l) {
        return GATE_FAMILIES.indexOf(l) === -1;
      }).sort();
      var ungatedIdx = known.indexOf("(ungated)");
      if (ungatedIdx === -1) {
        order = known.concat(extras);
      } else {
        order = known.slice(0, ungatedIdx).concat(extras, known.slice(ungatedIdx));
      }
    } else {
      order.sort();
    }
    return order.map(function (l) { return { lane: l, items: map[l] }; });
  }

  function visibleDeps(items, selectedId) {
    if (!selectedId) return [];
    var edges = [];
    items.forEach(function (it) {
      (it.deps || []).forEach(function (from) {
        if (it.id === selectedId || from === selectedId) edges.push({ from: from, to: it.id });
      });
    });
    return edges;
  }

  // actor facet: who is doing the work (live PR author). Baked items have no author.
  function actorOf(it) { return (it && it.author) || "(unknown)"; }

  // Pure overlay of live "derived" items onto the baked set. Assigns each live
  // item a seq in the open interval (now0, nextSeq) — at the frontier, below the
  // first roadmap step — so the combined set keeps the temporal invariant.
  // Fail-closed: invalid combined set OR a code collision → keep baked, never overlay.
  function mergeInflight(data, inflight) {
    var baked = (data && data.items) || [];
    var generated = (inflight && inflight.generated) || null;
    var live = (inflight && inflight.items) || [];
    if (!live.length) return { ok: true, items: baked.slice(), generated: generated, errors: [] };

    var now0 = deriveNow(baked);
    var domainEnd = (data && data.domain && typeof data.domain.end === "number") ? data.domain.end : now0 + 1;
    var nextSeq = domainEnd;
    for (var i = 0; i < baked.length; i++) {
      if (baked[i] && typeof baked[i].seq === "number" && baked[i].seq > now0 && baked[i].seq < nextSeq) {
        nextSeq = baked[i].seq;
      }
    }
    if (!(nextSeq > now0)) nextSeq = now0 + 1;

    var codes = {};
    baked.forEach(function (it) { if (it && it.code != null) codes[it.code] = true; });

    // Deterministic order (sort by id) so seq assignment is stable across runs.
    var sorted = live.slice().sort(function (a, b) {
      return String(a && a.id).localeCompare(String(b && b.id));
    });
    var n = sorted.length;
    var placed = [];
    var collision = false;
    for (var k = 0; k < n; k++) {
      var src = sorted[k];
      if (src && src.code != null && codes[src.code]) collision = true;
      var copy = {};
      for (var key in src) { if (Object.prototype.hasOwnProperty.call(src, key)) copy[key] = src[key]; }
      copy.seq = now0 + (nextSeq - now0) * (k + 1) / (n + 1);
      placed.push(copy);
    }

    var combined = baked.concat(placed);
    var res = validateItems(combined);
    if (!res.ok || collision) {
      var errs = res.errors.slice();
      if (collision) errs.push("live code collides with a baked item code");
      return { ok: false, items: baked.slice(), generated: generated, errors: errs };
    }
    return { ok: true, items: combined, generated: generated, errors: [] };
  }

  var api = {
    STATUS_ORDER: STATUS_ORDER, NODE_TYPES: NODE_TYPES, PROVENANCE: PROVENANCE,
    SETTLED: SETTLED, deriveNow: deriveNow, validateItems: validateItems,
    groupBy: groupBy, visibleDeps: visibleDeps, actorOf: actorOf, mergeInflight: mergeInflight,
  };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (root) root.CivOntology = api;
})(typeof window !== "undefined" ? window : null);
