// Convert explicit instants using the browser's locale and timezone. Calendar
// dates and source text without a timezone are not instants and stay verbatim.
(function () {
  "use strict";
  var instantPattern = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:\d{2})$/i;

  function instant(value) {
    if (typeof value !== "string" || !instantPattern.test(value)) return null;
    var date = new Date(value);
    return Number.isFinite(date.getTime()) ? date : null;
  }

  function formatter() {
    return new Intl.DateTimeFormat(undefined, {
      year: "numeric", month: "short", day: "numeric",
      hour: "numeric", minute: "2-digit", timeZoneName: "short",
    });
  }

  function format(value) {
    var date = instant(value);
    if (!date) return String(value == null ? "" : value);
    try { return formatter().format(date); } catch (e) { return value; }
  }

  function localize(root) {
    (root || document).querySelectorAll("time[data-local-time][datetime]").forEach(function (node) {
      var date = instant(node.getAttribute("datetime"));
      if (!date) return;
      try {
        var display = formatter();
        node.textContent = display.format(date);
        node.title = date.toISOString() + " · " + display.resolvedOptions().timeZone;
      } catch (e) { /* The rendered UTC fallback remains readable. */ }
    });
  }

  window.KnowledgeTime = { format: format, localize: localize };
  localize(document);
  document.addEventListener("DOMContentLoaded", function () { localize(document); });
  document.addEventListener("knowledge-space-change", function () { localize(document); });
})();
