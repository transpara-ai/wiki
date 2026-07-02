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
  // Item 2b: deny-by-default item schema. Any key not in this set is a
  // validation ERROR — the lane the parallel status fields used is closed
  // for the whole class (design packet §2.3).
  var ITEM_KEYS = ["id", "code", "ref", "date", "type", "label", "status",
    "blocked", "blocked_reason", "blocked_criterion", "criteria",
    "provenance", "seq", "repo", "sprint", "gate", "goal", "family",
    "deps", "note", "href", "evidence_links", "author"];
  var BLOCKED_REASONS = ["gate", "resource", "authority", "recovery",
    "dependency"];
  var CRITERION_KEYS = ["id", "label", "status", "blocked", "blocked_reason",
    "ref"];

  // Total fail-closed rollup over VALID criteria (design packet §2.1):
  // all done => done; any active => active; any planned => planned; else
  // future. Invalid input never reaches here — validateItems rejects it.
  function rollupCriteria(criteria) {
    var allDone = true, anyActive = false, anyPlanned = false, anyBlocked = false;
    for (var i = 0; i < criteria.length; i++) {
      var c = criteria[i];
      if (c.status !== "done") allDone = false;
      if (c.status === "active") anyActive = true;
      if (c.status === "planned") anyPlanned = true;
      if (c.blocked === true) anyBlocked = true;
    }
    var status = allDone ? "done" : anyActive ? "active" : anyPlanned ? "planned" : "future";
    return { status: status, blocked: anyBlocked };
  }
  var STATUS_LANES = ["done", "active", "blocked", "planned", "future"];
  // Fixed lane order for the "gate" grouping, which lanes by gate FAMILY.
  // Lanes not in this list are appended alphabetically, before "(ungated)".
  var GATE_FAMILIES = [
    "v3.9 milestones (A-J)",
    "Deployment register (G-0..G-8.4)",
    "v4.0 (K-V)",
    "Release & security gates (v3.9)",
    "(ungated)",
  ];
  // The arc's repo collection. ALL of these repos are the Transpara-AI Civilization; the
  // two DISPLAY groups are:
  //   "civilization" — the operational repos (the working society)
  //   "governance"   — the wiki/operation meta-layer OVER the civilization
  // NOTE: wiki and operation live in the GOVERNANCE group BY DESIGN — do not
  // "fix" this to match repo topics. This is a CURATED list, intentionally NOT the live
  // `dark-factory` topic query (which returns only the 6 operational repos as of 2026-06-21).
  // The "repo" grouping shows every collection repo as a lane (even empty) so none is
  // swamped or dropped; repos OUTSIDE the collection get their own named lanes, and a
  // repo-less item gets a named "(no repo)" lane — nothing is ever silently dropped.
  var REPO_GROUPS = [
    { key: "civilization", label: "Civilization",
      repos: ["agent", "docs", "eventgraph", "hive", "site", "work"] },
    { key: "governance", label: "Governance",
      repos: ["wiki", "operation"] },
  ];
  var REPO_CANON = REPO_GROUPS.reduce(function (acc, g) { return acc.concat(g.repos); }, []);

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
      // Backfilled date provenance (fail-closed): a date asserts completion, so it must be
      // ISO YYYY-MM-DD and only a done item may carry one. A ref, when present, must look
      // like "repo#123" so its source stays dereferenceable.
      if (it.date != null) {
        if (!/^\d{4}-\d{2}-\d{2}$/.test(it.date)) errors.push(where + ": date must be ISO YYYY-MM-DD, got '" + it.date + "'");
        if (it.status !== "done") errors.push(where + ": only done items may carry a date (status '" + it.status + "')");
      }
      if (it.ref != null && !/^[a-z][a-z0-9-]*#\d+$/.test(it.ref)) {
        errors.push(where + ": ref must look like 'repo#123', got '" + it.ref + "'");
      }
      if (typeof it.seq === "number" && !isNaN(it.seq) && it.seq < now && !SETTLED[it.status]) {
        errors.push(where + ": status '" + it.status + "' at seq " + it.seq +
          " is left of now (" + now + ") — past items must be done/active");
      }
      // Item 2b — deny-by-default schema: unknown keys are errors.
      Object.keys(it).forEach(function (k) {
        if (ITEM_KEYS.indexOf(k) === -1) errors.push(where + ": unknown key '" + k + "'");
      });
      // blocked overlay facets: boolean-or-absent (a string-truthy value
      // would diverge the === rollup from the renderer's truthiness —
      // CFAR 2b-r1 F2); reason non-null exactly when blocked; enum-valued.
      if (it.blocked !== undefined && typeof it.blocked !== "boolean") {
        errors.push(where + ": blocked must be a boolean, got '" + it.blocked + "'");
      }
      if (it.blocked === true) {
        if (BLOCKED_REASONS.indexOf(it.blocked_reason) === -1) {
          errors.push(where + ": blocked items need an enum blocked_reason, got '" + it.blocked_reason + "'");
        }
      } else if (it.blocked_reason != null) {
        errors.push(where + ": blocked_reason must be null unless blocked");
      }
      if (it.blocked_criterion != null && (it.type !== "gate" || it.blocked !== true || it.blocked_reason == null)) {
        errors.push(where + ": blocked_criterion only on a blocked GATE with a non-null blocked_reason");
      }
      // gates carry criteria; stored status/blocked must equal the rollup.
      if (it.type === "gate") {
        if (!Array.isArray(it.criteria) || it.criteria.length === 0) {
          errors.push(where + ": gates require non-empty criteria[]");
        } else {
          var critsValid = true;
          it.criteria.forEach(function (c, ci) {
            var cw = where + ".criteria[" + ci + "]";
            if (!c || typeof c !== "object") { errors.push(cw + ": not an object"); critsValid = false; return; }
            Object.keys(c).forEach(function (k) {
              if (CRITERION_KEYS.indexOf(k) === -1) { errors.push(cw + ": unknown key '" + k + "'"); critsValid = false; }
            });
            if (!c.id) { errors.push(cw + ": missing id"); critsValid = false; }
            if (c.blocked !== undefined && typeof c.blocked !== "boolean") {
              errors.push(cw + ": blocked must be a boolean, got '" + c.blocked + "'"); critsValid = false;
            }
            if (STATUS_ORDER.indexOf(c.status) === -1) { errors.push(cw + ": invalid status '" + c.status + "'"); critsValid = false; }
            if (c.blocked === true) {
              if (BLOCKED_REASONS.indexOf(c.blocked_reason) === -1) { errors.push(cw + ": blocked criterion needs an enum blocked_reason"); critsValid = false; }
            } else if (c.blocked_reason != null) {
              errors.push(cw + ": blocked_reason must be null unless blocked"); critsValid = false;
            }
          });
          if (critsValid) {
            var want = rollupCriteria(it.criteria);
            if (it.status !== want.status) {
              errors.push(where + ": stored status '" + it.status + "' contradicts the criteria rollup '" + want.status + "'");
            }
            if ((it.blocked === true) !== want.blocked) {
              errors.push(where + ": stored blocked=" + it.blocked + " contradicts the criteria rollup blocked=" + want.blocked);
            }
            if (it.blocked_criterion != null && !it.criteria.some(function (c) { return c.id === it.blocked_criterion && c.blocked === true; })) {
              errors.push(where + ": blocked_criterion '" + it.blocked_criterion + "' must name a criterion that is actually blocked");
            }
          }
        }
      } else if (it.criteria != null) {
        errors.push(where + ": criteria[] is a gate facet only");
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
  // Repo grouping is a COMPLETE collection enumeration with multi-membership: every
  // collection repo gets a lane (even with zero items) tagged with its display group
  // ("civilization" | "governance"); an item appears in EACH of its repos (not just
  // repo[0]). Repos OUTSIDE the collection get their OWN named lanes, and a repo-less
  // item gets a "(no repo)" lane — both tagged "outside" and appended (sorted) only when
  // present. Allowlist-not-denylist: membership in REPO_CANON is the proven branch; any
  // repo not on the list is named, never bucketed, never silently dropped.
  function groupByRepo(items) {
    var canon = Object.create(null);          // collection repo → items[]
    REPO_CANON.forEach(function (r) { canon[r] = []; });
    var outsideMap = Object.create(null);     // outside repo (or "(no repo)") → items[]
    function pushOutside(name, it) {
      if (!outsideMap[name]) outsideMap[name] = [];
      outsideMap[name].push(it);
    }
    (items || []).forEach(function (it) {
      var repos = (it && Array.isArray(it.repo)) ? it.repo : [];
      var seen = Object.create(null), matchedAny = false;
      repos.forEach(function (r) {
        if (seen[r]) return;                 // dedupe repeated repos within one item
        seen[r] = true;
        matchedAny = true;
        if (REPO_CANON.indexOf(r) !== -1) canon[r].push(it);
        else pushOutside(r, it);             // outside repo → its OWN named lane
      });
      // A repo-less item (repo:[]) matches nothing above → named "(no repo)" lane, never dropped.
      if (!matchedAny) pushOutside("(no repo)", it);
    });
    // Collection lanes, in group order, each tagged with its display group + label.
    var lanes = [];
    REPO_GROUPS.forEach(function (g) {
      g.repos.forEach(function (r) {
        lanes.push({ lane: r, items: canon[r], group: g.key, groupLabel: g.label });
      });
    });
    // Outside lanes (only when present): named repos alphabetically, then "(no repo)" last.
    var named = Object.keys(outsideMap).filter(function (n) { return n !== "(no repo)"; }).sort();
    if (outsideMap["(no repo)"]) named.push("(no repo)");
    named.forEach(function (n) {
      lanes.push({ lane: n, items: outsideMap[n], group: "outside", groupLabel: "Outside collection" });
    });
    return lanes;
  }

  function groupBy(items, dim) {
    if (dim === "repo") return groupByRepo(items);
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
    rollupCriteria: rollupCriteria,
    STATUS_ORDER: STATUS_ORDER, NODE_TYPES: NODE_TYPES, PROVENANCE: PROVENANCE,
    SETTLED: SETTLED, REPO_GROUPS: REPO_GROUPS, REPO_CANON: REPO_CANON,
    deriveNow: deriveNow, validateItems: validateItems,
    groupBy: groupBy, visibleDeps: visibleDeps, actorOf: actorOf, mergeInflight: mergeInflight,
  };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (root) root.CivOntology = api;
})(typeof window !== "undefined" ? window : null);
