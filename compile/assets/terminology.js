(function () {
  "use strict";
  const byId = id => document.getElementById(id);
  let snapshot = null, selected = null, requestSequence = 0;

  // Source sentences and term names are untrusted data, never HTML or links.
  function node(tag, text, className) {
    const value = document.createElement(tag);
    if (text !== undefined) value.textContent = String(text);
    if (className) value.className = className;
    return value;
  }
  function notice(text, error = false) {
    byId("term-notice").textContent = text;
    byId("term-notice").dataset.error = String(error);
  }
  function scopeText(scope) {
    return [scope?.repo, scope?.product].filter(Boolean).join(" · ") || "Scope not specified";
  }
  function empty(target, message) {
    target.append(node("p", message, "term-empty"));
  }
  function shownObservations(candidate) {
    return candidate.observations.slice(0, 10);
  }
  function proposalObservations(candidate) {
    const shown = shownObservations(candidate);
    // A normalized group can contain several spellings. Regular-English
    // drafts cover only the exact spelling named by this candidate.
    return byId("term-decision").value === "regular_english"
      ? shown.filter(item => item.term === candidate.term) : shown;
  }
  function hasCurrentContexts(candidate) {
    const shown = shownObservations(candidate);
    return shown.length > 0 && shown.every(item => {
      // Core offsets count Unicode code points, not JavaScript UTF-16 units.
      // The hash stays opaque: literal masking prevents browser recomputation.
      const sentence = typeof item.sentence === "string" ? Array.from(item.sentence) : [];
      return item.context_binding === "transpara-source-occurrence-v1"
        && typeof item.context_digest === "string" && /^[a-f0-9]{64}$/.test(item.context_digest)
        && typeof item.path === "string" && item.path.length > 0
        && Number.isInteger(item.line) && item.line > 0
        && typeof item.term === "string" && item.term.length > 0
        && Number.isInteger(item.start) && Number.isInteger(item.end)
        && item.start >= 0 && item.end > item.start && item.end <= sentence.length
        && sentence.slice(item.start, item.end).join("") === item.term;
    });
  }
  function classify() {
    const immutable = byId("term-decision").value === "immutable";
    const included = selected ? proposalObservations(selected) : [];
    byId("term-immutable-fields").hidden = !immutable;
    ["term-canonical", "term-definition", "term-forms"].forEach(id => byId(id).required = immutable);
    byId("term-decision-help").textContent = immutable
      ? "Propose the exact form and meaning that a Human maintainer should preserve."
      : byId("term-decision").value === "regular_english"
        ? "Propose regular English. This does not add a writing-rule exemption."
        : "Select a classification to see its effect.";
    byId("term-context-help").textContent = selected && byId("term-decision").value === "regular_english"
      ? "The draft includes " + included.length + " of " + shownObservations(selected).length
        + " shown occurrences that match \"" + selected.term + "\" exactly. Other spellings remain pending."
      : immutable ? "Shown contexts remain evidence for Human review of the proposed approved forms." : "";
    byId("term-download").disabled = !snapshot || !selected || !hasCurrentContexts(selected)
      || !included.length || !byId("term-decision").value;
  }
  function selectCandidate(candidate) {
    selected = candidate;
    byId("term-detail").hidden = false;
    byId("term-detail-title").textContent = candidate.term;
    byId("term-detail-scope").textContent = scopeText(candidate.scope);
    const evidence = byId("term-evidence"); evidence.replaceChildren();
    evidence.append(node("p", candidate.reference_status === "available"
      ? "External vocabulary was supplied to the scanner. This is still a pending terminology candidate."
      : "ASD vocabulary is unavailable. This phrase is unassessed, not a confirmed violation."));
    evidence.append(node("p", "Showing " + shownObservations(candidate).length + " of " + candidate.observations.length
      + " observations. The draft covers only the evidence shown here."));
    shownObservations(candidate).forEach(item => {
      evidence.append(node("p", item.path + ":" + item.line));
      evidence.append(node("pre", item.sentence, "term-evidence"));
    });
    if (!candidate.observations.length) empty(evidence, "No source observations were supplied.");
    if (!hasCurrentContexts(candidate))
      evidence.append(node("p", "The shown evidence needs current occurrence bindings and valid source spans. Re-scan and Refresh before exporting a decision proposal.", "term-empty"));
    byId("term-proposal-form").reset();
    byId("term-canonical").value = candidate.term;
    byId("term-forms").value = candidate.term;
    classify();
    renderCandidates();
    byId("term-decision").focus();
  }
  function renderCandidates() {
    const list = byId("term-candidates"); list.replaceChildren();
    if (!snapshot) return;
    const query = byId("term-filter").value.trim().toLowerCase();
    const matching = snapshot.candidates.filter(c => (c.term + " " + scopeText(c.scope)).toLowerCase().includes(query));
    matching.slice(0, 100).forEach(candidate => {
      const card = node("div", undefined, "term-card");
      const button = node("button", candidate.term, "term-candidate");
      button.type = "button";
      button.setAttribute("aria-pressed", String(selected?.id === candidate.id));
      button.append(node("span", scopeText(candidate.scope)));
      button.addEventListener("click", () => selectCandidate(candidate));
      card.append(button); list.append(card);
    });
    if (!matching.length) empty(list, query ? "No candidates match this search." : "No pending candidates. New scanner exports will appear after Refresh.");
    if (matching.length > 100) list.append(node("p", "Showing the first 100 candidates. Narrow the search to see others."));
  }
  function renderCollections() {
    const entries = byId("term-entries"); entries.replaceChildren();
    snapshot.terms.slice(0, 100).forEach(term => {
      const card = node("article", undefined, "term-card");
      card.append(node("h3", term.term || term.canonical || "Unnamed term"));
      card.append(node("p", term.definition || "No definition supplied."));
      card.append(node("p", scopeText(term.scope)));
      if (Array.isArray(term.approved_forms)) card.append(node("p", "Approved forms: " + term.approved_forms.join(", ")));
      entries.append(card);
    });
    if (!snapshot.terms.length) empty(entries, "The Human-owned dictionary has no approved terms yet.");
    const ledger = byId("term-decisions"); ledger.replaceChildren();
    snapshot.decisions.filter(d => d.decision === "regular_english").slice(0, 100).forEach(decision => {
      const card = node("article", undefined, "term-card");
      card.append(node("h3", decision.term || decision.normalized || "Unnamed decision"));
      card.append(node("p", scopeText(decision.scope))); ledger.append(card);
    });
    if (!ledger.children.length) empty(ledger, "No regular-English decisions in this export.");
    if (snapshot.terms.length > 100 || snapshot.decisions.length > 100)
      notice("Snapshot loaded. Collection views show at most 100 entries; inspect the canonical document for the complete dictionary.");
  }
  async function load() {
    const sequence = ++requestSequence;
    // Refresh invalidates any draft selection before the request begins.
    snapshot = null; selected = null;
    byId("term-detail").hidden = true; byId("term-download").disabled = true;
    ["term-candidates", "term-entries", "term-decisions"].forEach(id => byId(id).replaceChildren());
    byId("term-version").textContent = "No snapshot loaded.";
    byId("term-digest").textContent = "";
    notice("Loading terminology snapshot…");
    const headers = {"X-Wiki-Profile-Action": "1"};
    if (byId("term-token").value) headers["X-CivWiki-Authoring-Token"] = byId("term-token").value;
    try {
      const response = await fetch("/api/terminology/snapshot", {credentials: "same-origin", cache: "no-store", redirect: "error", headers});
      const data = await response.json();
      if (sequence !== requestSequence) return;
      if (!response.ok) throw new Error(data.error || "Snapshot unavailable (" + response.status + ").");
      if (data.schema_version !== 1 || !Array.isArray(data.candidates) || !Array.isArray(data.terms)
          || !Array.isArray(data.decisions) || !/^[a-f0-9]{64}$/.test(data.dictionary_digest))
        throw new Error("The terminology export has an unsupported format.");
      snapshot = data;
      byId("term-version").textContent = "Dictionary version " + data.dictionary_version;
      byId("term-digest").textContent = "Source document SHA-256: " + data.dictionary_digest;
      byId("term-reference").textContent = data.reference_status === "available"
        ? "The scanner used an external vocabulary. ASD conformance remains unassessed."
        : "ASD vocabulary is unavailable. Candidates are unassessed; no ASD conformance verdict is available.";
      notice(data.candidates.length + " pending candidates · " + data.terms.length + " dictionary terms");
      renderCandidates(); renderCollections();
    } catch (error) {
      if (sequence === requestSequence) {
        notice(error.message || "Terminology snapshot unavailable.", true);
        byId("term-reference").textContent = "No current snapshot. ASD conformance is not assessed.";
      }
    }
  }
  document.querySelectorAll("[data-term-tab]").forEach(button => button.addEventListener("click", () => {
    document.querySelectorAll("[data-term-tab]").forEach(item => item.setAttribute("aria-pressed", String(item === button)));
    ["inbox", "dictionary", "english", "publication"].forEach(id => byId("term-" + id).hidden = id !== button.dataset.termTab);
  }));
  byId("term-refresh").addEventListener("click", load);
  byId("term-connect").addEventListener("click", load);
  byId("term-filter").addEventListener("input", renderCandidates);
  byId("term-decision").addEventListener("change", classify);
  byId("term-proposal-form").addEventListener("submit", event => {
    event.preventDefault();
    if (!snapshot || !selected || !hasCurrentContexts(selected) || !event.currentTarget.reportValidity()) return;
    const included = proposalObservations(selected);
    if (!included.length) {
      notice("No shown occurrence matches the exact spelling for this draft.", true); return;
    }
    const immutable = byId("term-decision").value === "immutable";
    const term = immutable ? byId("term-canonical").value.trim() : selected.term;
    const definition = immutable ? byId("term-definition").value.trim() : "";
    const forms = immutable ? [...new Set(byId("term-forms").value.split("\n").map(x => x.trim()).filter(Boolean))] : [];
    if (immutable && (!term || !definition || !forms.length || !forms.includes(term))) {
      notice("The immutable proposal needs a definition and approved forms including the canonical term.", true); return;
    }
    // This file carries no reviewer identity and has no approval effect.
    const proposal = {schema_version: 1, state: "draft", candidate_id: selected.id,
      decision: byId("term-decision").value, expected_dictionary_digest: snapshot.dictionary_digest,
      term, definition, term_class: immutable ? byId("term-class").value : "",
      scope: selected.scope, approved_forms: forms,
      context_digests: [...new Set(included.map(item => item.context_digest))]};
    const url = URL.createObjectURL(new Blob([JSON.stringify(proposal, null, 2) + "\n"], {type: "application/json"}));
    const anchor = node("a"); anchor.href = url; anchor.download = "terminology-decision-draft.json";
    document.body.append(anchor); anchor.click(); anchor.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000);
    notice("Draft proposal downloaded. The candidate remains pending until a Human-maintained dictionary change is accepted.");
  });
  load();
})();
