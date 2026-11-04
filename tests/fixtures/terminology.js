"use strict";

// Independent prose fixtures use current core fields without an ASD vocabulary.
function observation(sentence = 'Use the flux adapter. <script>window.pwned=true</script>') {
  const term = "flux adapter";
  const start = Array.from(sentence.slice(0, sentence.indexOf(term))).length;
  return {path:"guide.md", line:2, sentence, term, start, end:start + term.length,
    context_binding:"transpara-source-occurrence-v1", context_digest:"b".repeat(64)};
}

function snapshot() {
  return {schema_version:1, dictionary_version:"0.1.0", dictionary_digest:"a".repeat(64),
    reference_status:"unassessed", conformance:"not_assessed", terms:[], decisions:[],
    candidates:[{id:"candidate-one", term:"flux adapter", normalized:"flux adapter",
      scope:{repo:"transpara-ai/example", product:"example"}, status:"pending", reference_status:"unassessed",
      observations:[observation()]}]};
}

module.exports = {observation, snapshot};
