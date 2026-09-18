/* Cited, subscription-backed answers; no credentials or answer history stored. */
(function () {
  'use strict';
  var input = document.getElementById('wiki-search');
  if (!input) return;
  var form = input.closest('form'), mode = document.getElementById('wiki-query-mode');
  var provider = document.getElementById('wiki-ask-provider'), model = document.getElementById('wiki-ask-model');
  var effort = document.getElementById('wiki-ask-effort');
  var controls = document.getElementById('wiki-ask-controls'), output = document.getElementById('wiki-ask-answer');
  var scope = document.getElementById('wiki-search-scope');
  var catalog = null, busy = false, loaded = false, generation = 0, history = [];
  function saved(key, fallback) { try { return localStorage.getItem('wiki-ask-' + key) || fallback; } catch (_) { return fallback; } }
  function save(key, value) { try { localStorage.setItem('wiki-ask-' + key, value); } catch (_) {} }
  function status(message) { output.replaceChildren(); output.textContent = message; output.hidden = false; }
  function modelAvailable() { return !!model.value && !!model.selectedOptions[0] && !model.selectedOptions[0].disabled; }
  function available() { return modelAvailable() && !!effort.value; }
  function effortLabel(value) { return {low: 'Low', medium: 'Medium', high: 'High', xhigh: 'Extra high', max: 'Maximum', 'not-supported': 'Not supported'}[value] || value; }
  function effortKey() { return 'effort-' + provider.value + '-' + model.value; }
  function effortOptions() {
    effort.replaceChildren();
    var spec = catalog && catalog.models.find(function (m) { return m.provider === provider.value && m.id === model.value; });
    if (!spec) return;
    spec.effort_levels.forEach(function (level) {
      var option = document.createElement('option'); option.value = level; option.textContent = effortLabel(level); effort.appendChild(option);
    });
    effort.value = saved(effortKey(), spec.default_effort);
    effort.disabled = spec.effort_levels.length === 1 && spec.default_effort === 'not-supported';
    if (!effort.value) status('Your saved effort level is unavailable. Choose a supported effort level.');
  }
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
    effortOptions();
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
      if (!modelAvailable() && mode.value === 'ask') status('Your selected model is unavailable. Choose an enabled model or use Search.');
    } catch (error) {
      loaded = false; model.replaceChildren(); effort.replaceChildren();
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
    input.setAttribute('enterkeyhint', mode.value === 'ask' ? 'send' : 'search');
    if (mode.value === 'ask') input.setAttribute('aria-describedby', 'wiki-ask-hint');
    else input.removeAttribute('aria-describedby');
    save('mode', mode.value);
    if (mode.value === 'ask') load(); input.dispatchEvent(new Event('input'));
  }
  provider.value = saved('provider', 'codex'); if (!provider.value) provider.value = 'codex';
  mode.value = saved('mode', 'ask'); if (!mode.value) mode.value = 'ask';
  mode.addEventListener('change', changeMode);
  provider.addEventListener('change', function () { invalidate(); save('provider', provider.value); options(); if (!modelAvailable()) status('Your selected model is unavailable. Choose an enabled model or use Search.'); });
  model.addEventListener('change', function () { invalidate(); save('model-' + provider.value, model.value); effortOptions(); });
  effort.addEventListener('change', function () { invalidate(); save(effortKey(), effort.value); });
  function invalidate() { generation++; output.hidden = true; }
  input.addEventListener('input', invalidate); scope.addEventListener('change', function () { history = []; invalidate(); });
  form.addEventListener('submit', async function (event) {
    event.preventDefault();
    if (mode.value !== 'ask' || busy || !available()) return;
    var question = input.value.trim();
    if (question.length < 2) { status('Enter a question first.'); return; }
    busy = true;
    var current = ++generation;
    status('Reading the selected space and preparing a cited answer…'); output.setAttribute('aria-busy', 'true');
    var controller = new AbortController(), timer = setTimeout(function () { controller.abort(); }, 250000);
    try {
      var data = await fetchJSON('/api/ask', {method: 'POST', signal: controller.signal,
        headers: {'Content-Type': 'application/json', Accept: 'application/json', 'X-Wiki-Profile-Action': '1'},
        body: JSON.stringify(Object.assign({question: question, space: scope.value, provider: provider.value, model: model.value, effort: effort.value}, history.length ? {history:history} : {}))});
      if (current !== generation || mode.value !== 'ask') return;
      output.replaceChildren(); output.hidden = false;
      var heading = document.createElement('strong'); heading.textContent = 'Answer · ' + data.model + ' · Effort: ' + effortLabel(data.effort); output.appendChild(heading);
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
          if (citation.passage) {
            var detail = document.createElement('details'), summary = document.createElement('summary'), quote = document.createElement('blockquote');
            summary.textContent = 'Published passage · revision ' + (citation.revision || '').slice(0, 12);
            quote.textContent = citation.passage; detail.append(summary, quote); paragraph.appendChild(detail);
          }
        }); output.appendChild(paragraph);
      });
      var actions = document.createElement('div'); output.appendChild(actions);
      function action(label, fn) { var b = document.createElement('button'); b.type = 'button'; b.textContent = label; b.onclick = fn; actions.appendChild(b); }
      action('Ask a follow-up', function () { history.push({question:question.slice(0,1000),answer:data.answer.slice(0,1000)}); history=history.slice(-3); input.value=''; input.focus(); });
      async function retain(route) {
        try { await fetchJSON('/api/knowledge/reader/'+route,{method:'POST',headers:{'Content-Type':'application/json','X-Wiki-Profile-Action':'1'},body:JSON.stringify({question:question,space:scope.value,answer:data})}); var savedNote=document.createElement('p'); savedNote.textContent=route==='save'?'Answer saved to your account.':'Feedback queued for a curator.'; output.appendChild(savedNote); }
        catch(error) { var errorNote=document.createElement('p'); errorNote.textContent=error.message; output.appendChild(errorNote); }
      }
      action('Save answer',function(){retain('save');});
      action('Request evidence review',function(){retain('feedback');});
      if(document.querySelector('.top-links a[href$="knowledge.html"]')) action('Research / propose',function(){window.location.href='/knowledge.html';});
      if (data.insufficient_evidence) { var note = document.createElement('p'); note.textContent = 'The available wiki evidence is incomplete for this question.'; output.appendChild(note); }
    } catch (error) {
      if (current === generation && mode.value === 'ask') status(error.name === 'AbortError' ? 'The question timed out. Please retry.' : error.message);
    } finally { clearTimeout(timer); busy = false; output.removeAttribute('aria-busy'); }
  });
  changeMode();
}());
