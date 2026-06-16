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

  // "now" on the sequence axis = the frontier: the largest seq among settled (done/active) items.
  function deriveNow(items) {
    var now = -Infinity;
    for (var i = 0; i < items.length; i++) {
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
      var where = "item[" + idx + "] " + ((it && it.id) ? it.id : "(no id)");
      if (!it || typeof it !== "object") { errors.push(where + ": not an object"); return; }
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

  var STATUS_LANES = ["done", "active", "blocked", "planned", "future"];
  function laneOf(it, dim) {
    if (dim === "repo") return (it.repo && it.repo[0]) || "(none)";
    if (dim === "sprint") return it.sprint || "(none)";
    if (dim === "gate") return it.gate || "(ungated)";
    return "(none)";
  }
  function groupBy(items, dim) {
    var map = {}, order = [];
    if (dim === "status") {
      items.forEach(function (it) {
        // status lane: always add to its status bucket
        var sl = it.status;
        if (!map[sl]) { map[sl] = []; }
        map[sl].push(it);
        // blocked overlay: also add to "blocked" bucket if flagged
        if (it.blocked) {
          if (!map["blocked"]) { map["blocked"] = []; }
          map["blocked"].push(it);
        }
      });
      order = STATUS_LANES.filter(function (l) { return map[l]; });
    } else {
      items.forEach(function (it) {
        var lane = laneOf(it, dim);
        if (!map[lane]) { map[lane] = []; order.push(lane); }
        map[lane].push(it);
      });
      order.sort();
    }
    return order.map(function (l) { return { lane: l, items: map[l] }; });
  }

  var api = {
    STATUS_ORDER: STATUS_ORDER, NODE_TYPES: NODE_TYPES, PROVENANCE: PROVENANCE,
    SETTLED: SETTLED, deriveNow: deriveNow, validateItems: validateItems,
    groupBy: groupBy,
  };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (root) root.CivOntology = api;
})(typeof window !== "undefined" ? window : null);
