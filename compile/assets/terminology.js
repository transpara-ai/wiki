(function () {
  "use strict";
  const byId = id => document.getElementById(id);
  let snapshot = null, selected = null, requestSequence = 0, stateRequestSequence = 0;
  let state = null, stage = null, scanJob = null, scanReport = null, scanTimer = null;
  const boundaryText = document.querySelector(".term-boundary p").textContent;

  // Older services omit the separate submission/enrollment flags. Preserve
  // their supported actions only after state loads; an explicit false always
  // disables the action. The server remains the authority for every request.
  function allowed(name, legacyDefault = false) {
    const capabilities = state?.capabilities;
    return Boolean(capabilities && (capabilities[name] === true
      || (capabilities[name] === undefined && legacyDefault)));
  }
  function canPrepare() {return allowed("prepare", allowed("publication"));}
  function canPublish() {return allowed("publish", allowed("publication"));}

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
  async function api(path, payload) {
    const headers = {"X-Wiki-Profile-Action": "1"};
    if (byId("term-token").value) headers["X-CivWiki-Authoring-Token"] = byId("term-token").value;
    if (payload !== undefined) headers["Content-Type"] = "application/json";
    const response = await fetch("/api/terminology/" + path, {
      method: payload === undefined ? "GET" : "POST", headers,
      body: payload === undefined ? undefined : JSON.stringify(payload),
      credentials: "same-origin", cache: "no-store", redirect: "error"
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Terminology is unavailable (" + response.status + ").");
    return data;
  }
  function download(value, name) {
    const url = URL.createObjectURL(new Blob([JSON.stringify(value, null, 2) + "\n"], {type: "application/json"}));
    const anchor = node("a"); anchor.href = url; anchor.download = name;
    document.body.append(anchor); anchor.click(); anchor.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  function dateText(value) {
    if (typeof value === "number") return new Date(value * 1000).toISOString();
    return value || "";
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
    const included = selected && !selected.manual ? proposalObservations(selected) : [];
    const manual = Boolean(selected?.manual);
    byId("term-immutable-fields").hidden = !immutable;
    byId("term-new-scope").hidden = !manual;
    byId("term-reason-fields").hidden = !snapshot?.browser_service || immutable || !byId("term-decision").value;
    byId("term-reason").required = Boolean(snapshot?.browser_service && !immutable && byId("term-decision").value);
    ["term-repo", "term-product"].forEach(id => byId(id).required = manual);
    ["term-canonical", "term-definition", "term-forms"].forEach(id => byId(id).required = immutable);
    byId("term-decision-help").textContent = immutable
      ? "Propose the exact form and meaning that a Human maintainer should preserve."
      : byId("term-decision").value === "regular_english"
        ? "Propose regular English. This does not add a writing-rule exemption."
        : "Select a classification to see its effect.";
    byId("term-context-help").textContent = selected && !manual && byId("term-decision").value === "regular_english"
      ? "The draft includes " + included.length + " of " + shownObservations(selected).length
        + " shown occurrences that match \"" + selected.term + "\" exactly. Other spellings remain pending."
      : immutable ? "Shown contexts remain evidence for Human review of the proposed approved forms." : "";
    const valid = snapshot && selected && byId("term-decision").value
      && (manual ? immutable : hasCurrentContexts(selected) && included.length);
    byId("term-download").disabled = !valid;
    byId("term-submit").disabled = !valid || !allowed("submit", true);
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
    byId("term-decision").querySelector('option[value="regular_english"]').disabled = false;
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
    snapshot = null; selected = null; state = null; stage = null;
    byId("term-stage").hidden = true; byId("term-new").hidden = true;
    byId("term-submit").hidden = true; byId("term-submit").disabled = true;
    byId("term-enroll").hidden = true; byId("term-enroll").disabled = true;
    byId("term-prepare").hidden = true; byId("term-prepare").disabled = true;
    byId("term-scan-start").disabled = true;
    document.querySelector(".term-boundary p").textContent = boundaryText;
    byId("term-download").type = "submit";
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
      if (data.browser_service) {
        byId("term-download").type = "button";
        await loadState(sequence);
      }
    } catch (error) {
      if (sequence === requestSequence) {
        notice(error.message || "Terminology snapshot unavailable.", true);
        byId("term-reference").textContent = "No current snapshot. ASD conformance is not assessed.";
      }
    }
  }
  document.querySelectorAll("[data-term-tab]").forEach(button => button.addEventListener("click", () => {
    document.querySelectorAll("[data-term-tab]").forEach(item => item.setAttribute("aria-pressed", String(item === button)));
    ["inbox", "dictionary", "english", "contributions", "scan", "publication"].forEach(id => byId("term-" + id).hidden = id !== button.dataset.termTab);
  }));
  byId("term-refresh").addEventListener("click", load);
  byId("term-connect").addEventListener("click", load);
  byId("term-filter").addEventListener("input", renderCandidates);
  byId("term-decision").addEventListener("change", classify);
  function proposalFromForm() {
    if (!snapshot || !selected || (!selected.manual && !hasCurrentContexts(selected))
        || !byId("term-proposal-form").reportValidity()) return null;
    const included = selected.manual ? [] : proposalObservations(selected);
    if (!selected.manual && !included.length) {
      notice("No shown occurrence matches the exact spelling for this draft.", true); return null;
    }
    const immutable = byId("term-decision").value === "immutable";
    if (selected.manual && !immutable) return null;
    const term = immutable ? byId("term-canonical").value.trim() : selected.term;
    const definition = immutable ? byId("term-definition").value.trim() : "";
    const forms = immutable ? [...new Set(byId("term-forms").value.split("\n").map(x => x.trim()).filter(Boolean))] : [];
    if (immutable && (!term || !definition || !forms.length || !forms.includes(term))) {
      notice("The immutable proposal needs a definition and approved forms including the canonical term.", true); return null;
    }
    const proposal = {schema_version: 1, state: "draft", candidate_id: selected.id,
      decision: byId("term-decision").value, expected_dictionary_digest: snapshot.dictionary_digest,
      term, definition, term_class: immutable ? byId("term-class").value : "",
      scope: selected.manual ? {repo: byId("term-repo").value.trim(), product: byId("term-product").value.trim()} : selected.scope,
      approved_forms: forms, context_digests: [...new Set(included.map(item => item.context_digest))]};
    if (!immutable && byId("term-reason").value.trim()) proposal.reason = byId("term-reason").value.trim();
    return proposal;
  }
  byId("term-download").addEventListener("click", () => {
    if (!snapshot?.browser_service) return; // Legacy submit handler owns export.
    const proposal = proposalFromForm();
    if (proposal) download(proposal, "terminology-decision-draft.json");
  });
  byId("term-proposal-form").addEventListener("submit", async event => {
    event.preventDefault();
    const proposal = proposalFromForm();
    if (!proposal) return;
    if (!snapshot.browser_service) {
      download(proposal, "terminology-decision-draft.json");
      notice("Draft proposal downloaded. The candidate remains pending until a Human-maintained dictionary change is accepted.");
      return;
    }
    if (!allowed("submit", true)) return;
    byId("term-submit").disabled = true;
    const sequence = requestSequence;
    try {
      await api("proposals", {proposal});
      if (sequence !== requestSequence || !await loadState(sequence)) return;
      notice("Proposal submitted. A Human maintainer can review and publish it in Contributions.");
    } catch (error) {
      if (sequence === requestSequence) notice(error.message || "Proposal submission failed.", true);
    } finally {if (sequence === requestSequence) classify();}
  });
  byId("term-new").addEventListener("click", () => {
    if (!allowed("submit", true)) return;
    selected = {manual: true, id: null};
    byId("term-detail").hidden = false; byId("term-detail-title").textContent = "New technical term";
    byId("term-detail-scope").textContent = "Specify the exact repository and product scope.";
    byId("term-evidence").replaceChildren(node("p", "This proposal introduces a term without a scanner candidate. A Human maintainer reviews its meaning and scope."));
    byId("term-proposal-form").reset();
    byId("term-decision").value = "immutable";
    byId("term-decision").querySelector('option[value="regular_english"]').disabled = true;
    classify(); byId("term-canonical").focus();
  });

  async function loadState(sequence) {
    // A refresh invalidates older snapshot/state pairs. Within one snapshot,
    // a later state request also wins. Ignore both stale responses and stale
    // failures before they can change capabilities, provenance or notices.
    const stateSequence = ++stateRequestSequence;
    const current = () => sequence === requestSequence && stateSequence === stateRequestSequence;
    let nextState;
    try {nextState = await api("state");}
    catch (error) {if (!current()) return false; throw error;}
    if (!current()) return false;
    if (!nextState || !Array.isArray(nextState.proposals) || !Array.isArray(nextState.releases)
        || !nextState.capabilities || typeof nextState.capabilities !== "object"
        || Array.isArray(nextState.capabilities))
      throw new Error("The terminology service has an unsupported state format.");
    state = nextState;
    const analysisOnly = state.mode === "analysis_only";
    const previewDescription = "Scan and rewrite is available for previews. This deployment uses an unapproved seed dictionary. Proposal submission, passkey enrollment and dictionary publication are unavailable.";
    document.querySelector(".term-boundary p").textContent = analysisOnly ? previewDescription : boundaryText;
    byId("term-service-status").textContent = analysisOnly ? previewDescription
      : "Submitted proposals remain pending until a Human maintainer approves the complete publication.";
    byId("term-new").hidden = !allowed("submit", true);
    byId("term-submit").hidden = !allowed("submit", true);
    byId("term-scan-start").disabled = !allowed("scan", true);
    byId("term-prepare").hidden = !canPrepare();
    byId("term-enroll").hidden = !allowed("enrollment", true) || Boolean(state.capabilities.passkey_enrolled);
    byId("term-enroll").disabled = !allowed("enrollment", true);
    byId("term-enrollment-status").textContent = !allowed("enrollment", true)
      ? "Passkey enrollment is unavailable in this deployment."
      : state.capabilities.passkey_enrolled
        ? "This account has an enrolled publication passkey."
        : "Publication requires a Human-held passkey. Set one up, then ask an operator to accept its enrollment.";
    if (!canPublish()) {stage = null; byId("term-stage").hidden = true;}
    classify();
    const list = byId("term-proposals"); list.replaceChildren();
    state.proposals.slice(0, 100).forEach(item => {
      const content = item.proposal || item;
      const card = node("article", undefined, "term-card");
      const pending = ["pending", "submitted"].includes(item.state || item.status || "pending");
      const label = node("label", undefined, "term-check");
      const check = node("input"); check.type = "checkbox"; check.value = item.id;
      check.dataset.proposalId = item.id; check.disabled = !pending || !canPrepare();
      check.addEventListener("change", updatePrepare);
      label.append(check, node("span", content.term + " · " + (item.state || item.status || "pending")));
      card.append(label, node("p", scopeText(content.scope)));
      if (content.definition) card.append(node("p", content.definition));
      if (content.reason) card.append(node("p", content.reason));
      if (item.submitted_at || item.created_at || item.created) card.append(node("p", "Submitted: " + dateText(item.submitted_at || item.created_at || item.created)));
      list.append(card);
    });
    if (!state.proposals.length) empty(list, "No submitted proposals yet.");
    const history = byId("term-release-history"); history.replaceChildren();
    state.releases.slice(0, 100).forEach(item => {
      const card = node("article", undefined, "term-card");
      card.append(node("h3", "Publication " + (item.revision || item.release_revision || item.id)));
      card.append(node("p", "Dictionary " + (item.version || item.dictionary_version || "") + " · " + dateText(item.published_at || item.issued_at || item.created_at)));
      card.append(node("p", "SHA-256: " + (item.digest || item.dictionary_digest || "")));
      if (item.human_identity) card.append(node("p", "Human: " + item.human_identity));
      if (item.workload_identity) card.append(node("p", "Publisher: " + item.workload_identity));
      history.append(card);
    });
    if (!state.releases.length) empty(history, "No signed browser publications yet.");
    byId("term-publication-description").textContent = analysisOnly
      ? "This preview uses a seed dictionary with no signed publication. Its source digest identifies the configured bytes; it does not establish Human approval."
      : "The active runtime dictionary is separate from the repository seed document. Each browser publication records exact bytes and both approval signatures.";
    updatePrepare();
    if (state.scan_job && !scanJob) {scanJob = state.scan_job; await poll();}
    return current();
  }
  function selectedProposals() {
    return [...document.querySelectorAll("[data-proposal-id]:checked")].map(input => input.value);
  }
  function updatePrepare() {
    byId("term-prepare").disabled = !canPrepare() || !selectedProposals().length;
  }
  async function sha256(text) {
    if (!globalThis.crypto?.subtle) throw new Error("A secure browser connection is required for publication.");
    return new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text)));
  }
  function stableJSON(value) {
    if (Array.isArray(value)) return "[" + value.map(stableJSON).join(",") + "]";
    if (value && typeof value === "object") return "{" + Object.keys(value).sort().map(
      key => JSON.stringify(key) + ":" + stableJSON(value[key])).join(",") + "}";
    return JSON.stringify(value);
  }
  function publicationBytes(candidate) {
    const fields = ["id", "actor", "source", "digest", "base_digest", "version", "scope", "expires_at", "nonce"];
    if (Object.keys(candidate).some(key => !fields.includes(key) && key !== "diff")
        || fields.some(key => !(key in candidate)) || !/^[a-f0-9]{32}$/.test(candidate.id)
        || !/^[a-f0-9]{64}$/.test(candidate.digest) || !/^[a-f0-9]{64}$/.test(candidate.base_digest)
        || typeof candidate.source !== "string" || typeof candidate.actor !== "string"
        || typeof candidate.version !== "string" || !/^[A-Za-z0-9_-]{43}$/.test(candidate.nonce)
        || !Number.isSafeInteger(candidate.expires_at) || !candidate.scope
        || Object.keys(candidate.scope).sort().join(",") !== "product,repo"
        || Object.values(candidate.scope).some(value => typeof value !== "string"))
      throw new Error("The publication preview has an unsupported signed format.");
    return stableJSON(Object.fromEntries(fields.map(key => [key, candidate[key]]))) + "\n";
  }
  async function verifyDisplayedStage(candidate) {
    publicationBytes(candidate);
    const digest = [...await sha256(candidate.source)].map(value => value.toString(16).padStart(2, "0")).join("");
    if (digest !== candidate.digest) throw new Error("The displayed document does not match its publication digest.");
  }
  async function verifyApprovalOptions(candidate, options) {
    await verifyDisplayedStage(candidate);
    const expected = base64(await sha256("transpara-dictionary-browser-approval-v2\0" + publicationBytes(candidate)));
    if (options.stage_id !== candidate.id || options.publicKey?.challenge !== expected
        || options.publicKey?.rpId !== location.hostname || options.publicKey?.userVerification !== "required")
      throw new Error("Passkey approval does not match the displayed document and publication scope.");
  }
  byId("term-prepare").addEventListener("click", async () => {
    if (!canPrepare()) return;
    byId("term-prepare").disabled = true;
    stage = null; byId("term-stage").hidden = true;
    try {
      const result = await api("prepare", {proposal_ids: selectedProposals(), expected_dictionary_digest: snapshot.dictionary_digest});
      const candidate = result.stage || result;
      await verifyDisplayedStage(candidate);
      stage = Object.freeze(candidate);
      byId("term-stage-identity").textContent = "Version " + stage.version + " · SHA-256 " + stage.digest + " · Expires " + dateText(stage.expires_at);
      byId("term-stage-diff").textContent = stage.diff || "No changes.";
      byId("term-stage-source").textContent = stage.source;
      byId("term-stage").hidden = false; byId("term-reviewed").checked = false;
      byId("term-publish").disabled = true;
      notice("Review the exact dictionary document before approving publication.");
    } catch (error) {notice(error.message || "Publication preparation failed.", true);}
    finally {updatePrepare();}
  });
  byId("term-reviewed").addEventListener("change", () => {
    byId("term-publish").disabled = !stage || !canPublish() || !state?.capabilities.passkey_enrolled || !byId("term-reviewed").checked;
  });

  function unbase64(value) {
    const raw = atob(value.replace(/-/g, "+").replace(/_/g, "/"));
    return Uint8Array.from(raw, character => character.charCodeAt(0));
  }
  function base64(value) {
    return btoa(String.fromCharCode(...new Uint8Array(value))).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
  }
  function assertionJSON(credential) {
    return {id: credential.id, rawId: base64(credential.rawId), type: credential.type,
      response: {authenticatorData: base64(credential.response.authenticatorData),
        clientDataJSON: base64(credential.response.clientDataJSON), signature: base64(credential.response.signature),
        userHandle: credential.response.userHandle ? base64(credential.response.userHandle) : null},
      clientExtensionResults: credential.getClientExtensionResults()};
  }
  byId("term-publish").addEventListener("click", async () => {
    if (!stage || !canPublish() || !byId("term-reviewed").checked || !state?.capabilities.passkey_enrolled) return;
    byId("term-publish").disabled = true;
    const frozen = stage;
    try {
      if (!navigator.credentials?.get) throw new Error("This browser does not support passkeys.");
      const options = await api("approval/options", {stage_id: frozen.id});
      await verifyApprovalOptions(frozen, options);
      const publicKey = {...options.publicKey, userVerification: "required"};
      publicKey.challenge = unbase64(publicKey.challenge);
      publicKey.allowCredentials = (publicKey.allowCredentials || []).map(item => ({...item, id: unbase64(item.id)}));
      const credential = await navigator.credentials.get({publicKey});
      if (!credential || stage !== frozen) throw new Error("Approval was cancelled or the preview changed.");
      await api("publish", {stage_id: frozen.id, credential: assertionJSON(credential)});
      await load();
      notice("Dictionary published. Source revision shows the signed publication history.");
    } catch (error) {
      notice(error.name === "NotAllowedError" ? "Passkey approval was cancelled or unavailable." : error.message || "Publication was refused.", true);
      byId("term-reviewed").checked = false;
    }
  });
  byId("term-enroll").addEventListener("click", async () => {
    if (!allowed("enrollment", true)) return;
    byId("term-enroll").disabled = true;
    try {
      if (!navigator.credentials?.create) throw new Error("This browser does not support passkeys.");
      const options = await api("enrollment/options", {});
      const publicKey = {...options.publicKey};
      publicKey.challenge = unbase64(publicKey.challenge);
      publicKey.user = {...publicKey.user, id: unbase64(publicKey.user.id)};
      publicKey.authenticatorSelection = {...publicKey.authenticatorSelection, userVerification: "required"};
      publicKey.excludeCredentials = (publicKey.excludeCredentials || []).map(item => ({...item, id: unbase64(item.id)}));
      const credential = await navigator.credentials.create({publicKey});
      if (!credential) throw new Error("Passkey enrollment was cancelled.");
      const result = await api("enrollment/finish", {credential: {
        id: credential.id, rawId: base64(credential.rawId), type: credential.type,
        response: {clientDataJSON: base64(credential.response.clientDataJSON), attestationObject: base64(credential.response.attestationObject)},
        clientExtensionResults: credential.getClientExtensionResults()}});
      byId("term-enrollment-status").textContent = "Passkey enrollment " + (result.id || result.enrollment_id || "") + " is pending operator acceptance. It cannot publish yet.";
    } catch (error) {notice(error.message || "Passkey enrollment failed.", true);}
    finally {byId("term-enroll").disabled = !allowed("enrollment", true);}
  });

  byId("term-scan-type").addEventListener("change", () => {
    byId("term-scan-repo-options").hidden = byId("term-scan-type").value !== "repo";
  });
  byId("term-scan-form").addEventListener("submit", async event => {
    event.preventDefault();
    if (!event.currentTarget.reportValidity() || !snapshot?.browser_service) return;
    byId("term-scan-start").disabled = true; scanReport = null;
    byId("term-scan-report").replaceChildren(); byId("term-report-download").hidden = true;
    const source = {type: byId("term-scan-type").value, url: byId("term-scan-url").value.trim()};
    if (source.type === "repo") {
      if (byId("term-scan-ref").value.trim()) source.ref = byId("term-scan-ref").value.trim();
      const paths = byId("term-scan-paths").value.split("\n").map(item => item.trim()).filter(Boolean);
      if (paths.length) source.paths = paths;
    }
    try {
      const result = await api("scan", {source, rewrite: byId("term-scan-mode").value === "rewrite"});
      scanJob = result.job; renderJob(); schedulePoll();
    } catch (error) {
      byId("term-scan-status").textContent = error.message || "The scan could not start.";
      byId("term-scan-start").disabled = false;
    }
  });
  function schedulePoll() {
    if (scanTimer) clearTimeout(scanTimer);
    if (scanJob && ["queued", "running"].includes(scanJob.state)) scanTimer = setTimeout(poll, 750);
  }
  async function poll() {
    const current = scanJob?.id;
    if (!current) return;
    try {
      const result = await api("scan?id=" + encodeURIComponent(current));
      if (scanJob?.id !== current) return;
      scanJob = result.job; renderJob(); schedulePoll();
    } catch (error) {
      byId("term-scan-status").textContent = error.message || "Scanner status is unavailable. Refresh to reconnect.";
      byId("term-scan-start").disabled = false;
    }
  }
  function renderJob() {
    const active = ["queued", "running"].includes(scanJob.state);
    byId("term-scan-cancel").hidden = !active; byId("term-scan-start").disabled = active;
    byId("term-scan-status").textContent = "Scan " + scanJob.state + (scanJob.error ? ": " + scanJob.error : "");
    if (scanJob.report) {
      scanReport = scanJob.report; renderReport(scanReport); byId("term-report-download").hidden = false;
    }
  }
  function renderReport(report) {
    const target = byId("term-scan-report"); target.replaceChildren();
    target.append(node("p", "ASD-STE100 conformance: " + (report.conformance || "not_assessed") + ". Review the checker coverage and remaining findings."));
    if (report.coverage) target.append(node("p", report.coverage.complete === false
      ? "Coverage is incomplete. Some files or requests were outside the configured limits."
      : "Capture completed within the configured limits."));
    if (report.source?.commit) target.append(node("p", "Repository commit: " + report.source.commit));
    const details = node("details"); details.append(node("summary", "Complete report, original text, findings and rewrite drafts"));
    details.append(node("pre", JSON.stringify(report, null, 2), "term-evidence")); target.append(details);
    if (Array.isArray(report.limitations)) report.limitations.forEach(item => target.append(node("p", item)));
    if (report.rewrite?.status && !["not_requested", "draft"].includes(report.rewrite.status))
      target.append(node("p", "Rewrite " + report.rewrite.status + ": " + (report.rewrite.reason || "No accepted draft is available.")));
    const allFindings = Array.isArray(report.findings) ? report.findings : [];
    const drafts = Array.isArray(report.rewrite?.documents) ? report.rewrite.documents : [];
    const documents = report.documents || report.results || [];
    documents.slice(0, 256).forEach(item => {
      const card = node("article", undefined, "term-card");
      card.append(node("h3", item.label || item.path || "Document"));
      const rewritten = drafts.find(draft => draft.label === item.label);
      const original = rewritten?.original ?? item.original ?? item.text;
      if (typeof original === "string") card.append(node("h4", "Original"), node("pre", original, "term-evidence"));
      const findings = Array.isArray(item.findings) ? item.findings : allFindings.filter(finding => finding.label === item.label);
      card.append(node("h4", "Findings"));
      findings.slice(0,1000).forEach(finding => card.append(node("p", typeof finding === "string" ? finding :
        (finding.line ? "Line " + finding.line + ": " : "") + (finding.message || finding.kind || finding.term || JSON.stringify(finding)))));
      if (!findings.length) card.append(node("p", "No findings from the checks that ran. This does not certify conformance."));
      const draft = rewritten?.draft ?? item.rewrite?.text ?? item.draft?.text ?? item.rewrite ?? item.draft;
      if (typeof draft === "string") card.append(node("h4", "Rewrite draft"), node("pre", draft, "term-evidence"));
      const diff = rewritten?.diff || item.diff || item.rewrite?.diff || item.draft?.diff;
      if (typeof diff === "string") card.append(node("h4", "Changes"), node("pre", diff, "term-evidence"));
      if (rewritten && Array.isArray(report.rewrite.remaining_deviations)) {
        card.append(node("h4", "Remaining findings"));
        const remaining = report.rewrite.remaining_deviations.filter(finding => finding.label === item.label);
        remaining.slice(0,1000).forEach(finding => card.append(node("p", finding.message || finding.kind)));
        if (!remaining.length) card.append(node("p", "No remaining findings from the available partial checks. Human semantic review is still required."));
      }
      target.append(card);
    });
  }
  byId("term-scan-cancel").addEventListener("click", async () => {
    if (!scanJob) return;
    try {const result = await api("scan/cancel", {id: scanJob.id}); scanJob = result.job; renderJob(); schedulePoll();}
    catch (error) {byId("term-scan-status").textContent = error.message || "Cancellation could not be confirmed.";}
  });
  byId("term-report-download").addEventListener("click", () => {
    if (scanReport) download(scanReport, "technical-english-report.json");
  });

  load();
})();
