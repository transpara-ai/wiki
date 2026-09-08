// Space context is tab-local. Explicit tool URLs take precedence over remembered
// context; article and space-home pages establish their own registered space.
(function () {
  "use strict";
  var node = document.getElementById("space-context-data");
  if (!node) return;
  var config = JSON.parse(node.textContent);
  var storageKey = "knowledge-hub-space";
  var root = new URL(config.prefix || "./", location.href);
  var current = "";
  var remembered = "";
  var params = new URLSearchParams(location.search);
  function valid(space) {
    return Object.prototype.hasOwnProperty.call(config.spaces, space);
  }
  try { remembered = sessionStorage.getItem(storageKey) || ""; } catch (e) { /* optional */ }
  if (!valid(remembered)) remembered = "";
  var initial = config.contextual
    ? (params.has("space") ? (valid(params.get("space")) ? params.get("space") : config.defaultSpace)
      : remembered || config.defaultSpace)
    : config.defaultSpace || remembered;

  function contextualLink(anchor) {
    var url;
    try { url = new URL(anchor.getAttribute("href"), location.href); } catch (e) { return; }
    if (url.origin !== root.origin || !url.pathname.startsWith(root.pathname)) return;
    var route = url.pathname.slice(root.pathname.length);
    if (!/^(?:repos|sources|ingest|repo-[^/]+)\.html$/.test(route)
        && !/^source\/[^/]+\.html$/.test(route)) return;
    if (url.searchParams.get("space") !== current) url.searchParams.delete("section");
    if (current) url.searchParams.set("space", current);
    else url.searchParams.delete("space");
    anchor.setAttribute("href", url.pathname + url.search + url.hash);
  }

  function updateContent() {
    document.querySelectorAll("a[href]").forEach(contextualLink);
    var rows = document.querySelectorAll("[data-context-spaces]");
    var visible = 0;
    rows.forEach(function (row) {
      row.hidden = !!current && row.dataset.contextSpaces.split(" ").indexOf(current) === -1;
      if (!row.hidden) visible += 1;
    });
    var empty = document.getElementById("space-context-empty");
    if (empty) empty.hidden = visible !== 0;
    document.querySelectorAll("[data-context-label]").forEach(function (label) {
      label.textContent = current ? config.spaces[current].label : "All spaces";
    });
  }

  function setSpace(space, initializing) {
    if ((!space && !initializing) || (space && !valid(space))) return;
    if (!initializing && space === current) return;
    current = space;
    document.documentElement.dataset.space = space;
    try {
      if (space) sessionStorage.setItem(storageKey, space);
      else sessionStorage.removeItem(storageKey);
    } catch (e) { /* URLs still carry context when storage is unavailable. */ }
    if (config.contextual && space) {
      var url = new URL(location.href);
      if (url.searchParams.get("space") !== space) url.searchParams.delete("section");
      url.searchParams.set("space", space);
      try { history.replaceState(history.state, "", url); } catch (e) { /* file previews */ }
    }
    document.querySelectorAll(".space-switcher a[data-space]").forEach(function (link) {
      var selected = link.dataset.space === space;
      link.classList.toggle("current", selected);
      if (selected) link.setAttribute("aria-current", "page");
      else link.removeAttribute("aria-current");
    });
    var scope = document.getElementById("wiki-search-scope");
    if (scope) {
      scope.value = space || "all";
      scope.dispatchEvent(new Event("change"));
    }
    var chrome = config.spaces[space];
    if (chrome) {
      var freshness = document.querySelector(".space-freshness");
      if (freshness) freshness.innerHTML = chrome.freshness;
      var sidebar = document.querySelector(".sidebar");
      if (sidebar && chrome.sidebar && (!initializing || space !== config.defaultSpace)) {
        sidebar.outerHTML = chrome.sidebar;
      }
    }
    updateContent();
    document.dispatchEvent(new Event("knowledge-space-change"));
  }

  window.KnowledgeSpace = { get: function () { return current; }, set: setSpace };
  setSpace(initial, true);
  var scope = document.getElementById("wiki-search-scope");
  if (scope) scope.addEventListener("change", function () {
    // All spaces broadens search without discarding the selected workspace.
    if (valid(scope.value)) setSpace(scope.value);
  });
  document.addEventListener("DOMContentLoaded", updateContent);
  document.addEventListener("click", function (event) {
    var anchor = event.target.closest && event.target.closest("a[href]");
    if (anchor) contextualLink(anchor);
  }, true);
})();
