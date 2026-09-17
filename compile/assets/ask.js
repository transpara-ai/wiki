/* Cited, subscription-backed answers; no credentials or answer history stored. */
(function () {
  'use strict';
  var input = document.getElementById('wiki-search');
  if (!input) return;
  var form = input.closest('form'), mode = document.getElementById('wiki-query-mode');
  var provider = document.getElementById('wiki-ask-provider'), model = document.getElementById('wiki-ask-model');
  var controls = document.getElementById('wiki-ask-controls'), output = document.getElementById('wiki-ask-answer');
  var submit = document.getElementById('wiki-ask-submit'), scope = document.getElementById('wiki-search-scope');
  var catalog = null, busy = false, loaded = false, generation = 0;
  function saved(key, fallback) { try { return localStorage.getItem('wiki-ask-' + key) || fallback; } catch (_) { return fallback; } }
  function save(key, value) { try { localStorage.setItem('wiki-ask-' + key, value); } catch (_) {} }
  function status(message) { output.replaceChildren(); output.textContent = message; output.hidden = false; }
  function available() { return !!model.value && !!model.selectedOptions[0] && !model.selectedOptions[0].disabled; }
  function options() {
    model.replaceChildren();
    if (!catalog) return;
    catalog.models.filter(function (m) { return m.provider === provider.value; }).forEach(function (m) {
      var option = document.createElement('option');
      option.value = m.id; option.textContent = m.id + (m.enabled ? '' : ' — unavailable');
      option.disabled = !m.enabled; model.appendChild(option);
    });
    var wanted = saved('model-' + provider.value, catalog.defaults[provider.value]);
    model.value = wanted;
    submit.disabled = busy || !available();
  }
  async function fetchJSON(url, settings) {
    var response = await fetch(url, Object.assign({credentials: 'same-origin', headers: {Accept: 'application/json'}}, settings));
    if (!(response.headers.get('content-type') || '').includes('application/json')) throw new Error('Sign in again to ask the wiki. Search is still available.');
    var data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Wiki answers are unavailable.');
    return data;
  }
  async function load() {
    if (loaded) return;
    loaded = true;
    try {
      catalog = await fetchJSON('/api/ask/models'); options();
      if (!available() && mode.value === 'ask') status('Your selected model is unavailable. Choose an enabled model or use Search.');
    } catch (error) {
      loaded = false; model.replaceChildren(); submit.disabled = true;
      if (mode.value === 'ask') status(error.message);
    }
  }
  function changeMode() {
    generation++;
    form.dataset.mode = mode.value; controls.hidden = mode.value !== 'ask';
    output.hidden = true; document.getElementById('search-results').hidden = true;
    input.setAttribute('aria-expanded', 'false');
    input.placeholder = mode.value === 'ask' ? 'Ask Transpara Knowledge Hub' : 'Search Transpara Knowledge Hub';
    input.setAttribute('aria-label', input.placeholder);
    save('mode', mode.value);
    if (mode.value === 'ask') load(); else input.dispatchEvent(new Event('input'));
  }
  provider.value = saved('provider', 'codex'); if (!provider.value) provider.value = 'codex';
  mode.value = saved('mode', 'ask'); if (!mode.value) mode.value = 'ask';
  mode.addEventListener('change', changeMode);
  provider.addEventListener('change', function () { invalidate(); save('provider', provider.value); options(); if (!available()) status('Your selected model is unavailable. Choose an enabled model or use Search.'); });
  model.addEventListener('change', function () { invalidate(); save('model-' + provider.value, model.value); submit.disabled = busy || !available(); });
  function invalidate() { generation++; output.hidden = true; }
  input.addEventListener('input', invalidate); scope.addEventListener('change', invalidate);
  form.addEventListener('submit', async function (event) {
    event.preventDefault();
    if (mode.value !== 'ask' || busy || !available()) return;
    var question = input.value.trim();
    if (question.length < 2) { status('Enter a question first.'); return; }
    busy = true; submit.disabled = true;
    var current = ++generation;
    status('Reading the selected space and preparing a cited answer…'); output.setAttribute('aria-busy', 'true');
    var controller = new AbortController(), timer = setTimeout(function () { controller.abort(); }, 250000);
    try {
      var data = await fetchJSON('/api/ask', {method: 'POST', signal: controller.signal,
        headers: {'Content-Type': 'application/json', Accept: 'application/json', 'X-Wiki-Profile-Action': '1'},
        body: JSON.stringify({question: question, space: scope.value, provider: provider.value, model: model.value})});
      if (current !== generation || mode.value !== 'ask') return;
      output.replaceChildren(); output.hidden = false;
      var heading = document.createElement('strong'); heading.textContent = 'Answer · ' + data.model; output.appendChild(heading);
      var citations = new Map((data.citations || []).map(function (c) { return [c.id, c]; }));
      var paragraphs = data.paragraphs.length ? data.paragraphs : [{text: data.answer, article_ids: []}];
      paragraphs.forEach(function (p) {
        var paragraph = document.createElement('p'); paragraph.textContent = p.text;
        p.article_ids.forEach(function (id) {
          var citation = citations.get(id); if (!citation) return;
          // Defense in depth: only server-resolved article paths are links.
          if (!/^\/[a-zA-Z0-9_-]+\.html$/.test(citation.href)) return;
          var link = document.createElement('a'); link.href = citation.href; link.textContent = ' [' + citation.title + ']';
          paragraph.appendChild(link);
        }); output.appendChild(paragraph);
      });
      if (data.insufficient_evidence) { var note = document.createElement('p'); note.textContent = 'The available wiki evidence is incomplete for this question.'; output.appendChild(note); }
    } catch (error) {
      if (current === generation && mode.value === 'ask') status(error.name === 'AbortError' ? 'The question timed out. Please retry.' : error.message);
    } finally { clearTimeout(timer); busy = false; submit.disabled = !available(); output.removeAttribute('aria-busy'); }
  });
  changeMode();
}());
