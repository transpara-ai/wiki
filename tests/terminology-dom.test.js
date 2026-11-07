"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const test = require("node:test");
const {JSDOM} = require("jsdom");
const {snapshot} = require("./fixtures/terminology");

async function workspace(t, data, state) {
  const dom = new JSDOM(fs.readFileSync("compile/assets/terminology.html", "utf8"),
    {url:"http://127.0.0.1/terminology.html", runScripts:"outside-only"});
  t.after(() => dom.window.close());
  const {window} = dom;
  const downloads = [], calls = [];
  window.fetch = async (url, options) => {
    calls.push({url, method:options?.method || "GET"});
    return {ok:true, json:async () => url.endsWith("/state") ? (typeof state === "function" ? state() : state) : data};
  };
  window.Blob = class {constructor(parts) {downloads.push(parts.join(""));}};
  window.URL.createObjectURL = () => "blob:fixture";
  window.URL.revokeObjectURL = () => {};
  window.HTMLAnchorElement.prototype.click = () => {};
  window.eval(fs.readFileSync("compile/assets/terminology.js", "utf8"));
  await new Promise(resolve => setImmediate(resolve));
  window.document.querySelector(".term-candidate").click();
  const decision = window.document.getElementById("term-decision");
  decision.value = "regular_english";
  decision.dispatchEvent(new window.Event("change"));
  return {window, downloads, calls};
}

test("legacy line hashes remain readable and cannot export a draft", async t => {
  const data = snapshot();
  for (const key of ["context_binding", "term", "start", "end"])
    delete data.candidates[0].observations[0][key];
  const {window, downloads} = await workspace(t, data);
  assert.match(window.document.getElementById("term-evidence").textContent, /Use the flux adapter/);
  assert.match(window.document.getElementById("term-evidence").textContent, /Re-scan and Refresh/);
  assert.equal(window.document.getElementById("term-download").disabled, true);
  // A synthetic submit cannot bypass the disabled button's format check.
  window.document.getElementById("term-proposal-form").dispatchEvent(new window.Event("submit", {cancelable:true}));
  assert.equal(downloads.length, 0);
});

test("current Unicode source spans preserve supplied hashes in a draft", async t => {
  const data = snapshot();
  Object.assign(data.candidates[0].observations[0],
    {sentence:"🙂 Use the flux adapter.", start:10, end:22});
  const {window, downloads} = await workspace(t, data);
  assert.equal(window.document.getElementById("term-download").disabled, false);
  window.document.getElementById("term-proposal-form").dispatchEvent(new window.Event("submit", {cancelable:true}));
  assert.deepEqual(JSON.parse(downloads[0]).context_digests,
    data.candidates[0].observations.map(item => item.context_digest));
});

test("UTF-16 offsets cannot pass as Unicode code-point spans", async t => {
  const data = snapshot();
  Object.assign(data.candidates[0].observations[0],
    {sentence:"🙂 Use the flux adapter.", start:11, end:23});
  const {window} = await workspace(t, data);
  assert.equal(window.document.getElementById("term-download").disabled, true);
});

test("regular-English drafts omit other spellings while immutable drafts retain review context", async t => {
  const data = snapshot();
  data.candidates[0].observations.push({...data.candidates[0].observations[0],
    sentence:"Use the Flux adapter.", term:"Flux adapter", context_digest:"c".repeat(64)});
  const {window, downloads} = await workspace(t, data);
  assert.match(window.document.getElementById("term-evidence").textContent, /Flux adapter/);
  assert.match(window.document.getElementById("term-context-help").textContent, /1 of 2 shown occurrences/);
  const form = window.document.getElementById("term-proposal-form");
  form.dispatchEvent(new window.Event("submit", {cancelable:true}));
  assert.deepEqual(JSON.parse(downloads[0]).context_digests, ["b".repeat(64)]);
  const decision = window.document.getElementById("term-decision");
  decision.value = "immutable";
  decision.dispatchEvent(new window.Event("change"));
  window.document.getElementById("term-definition").value = "An example product component.";
  form.dispatchEvent(new window.Event("submit", {cancelable:true}));
  assert.deepEqual(JSON.parse(downloads[1]).context_digests, ["b".repeat(64), "c".repeat(64)]);
});

test("no matching spelling blocks regular-English export even with valid occurrence bindings", async t => {
  const data = snapshot();
  Object.assign(data.candidates[0].observations[0], {sentence:"Use the Flux adapter.", term:"Flux adapter"});
  const {window, downloads} = await workspace(t, data);
  assert.match(window.document.getElementById("term-context-help").textContent, /0 of 1 shown occurrences/);
  assert.equal(window.document.getElementById("term-download").disabled, true);
  window.document.getElementById("term-proposal-form").dispatchEvent(new window.Event("submit", {cancelable:true}));
  assert.equal(downloads.length, 0);
});


test("scan-only service hides unsupported controls and synthetic events cannot submit mutations", async t => {
  const data = {...snapshot(), browser_service:true};
  const state = {mode:"analysis_only", proposals:[], releases:[], capabilities:{
    scan:true, submit:false, prepare:false, publication:false, publish:false,
    enrollment:false, passkey_enrolled:false}};
  const {window, calls} = await workspace(t, data, state);
  const byId = id => window.document.getElementById(id);
  assert.match(window.document.querySelector(".term-boundary").textContent, /unapproved seed dictionary/);
  for (const id of ["term-new", "term-submit", "term-enroll", "term-prepare"])
    assert.equal(byId(id).hidden, true, id);
  assert.equal(byId("term-submit").disabled, true);
  assert.equal(byId("term-scan-start").disabled, false);
  byId("term-reason").value = "Invented fixture reason.";
  byId("term-proposal-form").dispatchEvent(new window.Event("submit", {cancelable:true}));
  for (const id of ["term-new", "term-enroll", "term-prepare", "term-publish"])
    byId(id).dispatchEvent(new window.Event("click"));
  await new Promise(resolve => setImmediate(resolve));
  assert.deepEqual(calls.filter(call => call.method === "POST"), []);
});

test("legacy service capabilities retain submission and enrollment when new flags are absent", async t => {
  const data = {...snapshot(), browser_service:true};
  const state = {proposals:[], releases:[],
    capabilities:{scan:true, publication:true, passkey_enrolled:false}};
  const {window} = await workspace(t, data, state);
  const byId = id => window.document.getElementById(id);
  for (const id of ["term-new", "term-submit", "term-enroll", "term-prepare"])
    assert.equal(byId(id).hidden, false, id);
  assert.equal(byId("term-submit").disabled, false);
  assert.equal(byId("term-enroll").disabled, false);
  assert.match(byId("term-enrollment-status").textContent, /Set one up/);
});


function deferred() {
  let resolve, reject;
  const promise = new Promise((done, fail) => {resolve = done; reject = fail;});
  return {promise, resolve, reject};
}
function scanOnlyState() {
  return {mode:"analysis_only", proposals:[], releases:[], capabilities:{
    scan:true, submit:false, prepare:false, publication:false, publish:false,
    enrollment:false, passkey_enrolled:false}};
}
function legacyState() {
  return {proposals:[], releases:[], capabilities:{scan:true, publication:true, passkey_enrolled:false}};
}
function assertScanOnly(window) {
  const byId = id => window.document.getElementById(id);
  assert.match(window.document.querySelector(".term-boundary").textContent, /unapproved seed dictionary/);
  for (const id of ["term-new", "term-submit", "term-enroll", "term-prepare"])
    assert.equal(byId(id).hidden, true, id);
  assert.equal(byId("term-scan-start").disabled, false);
  assert.match(byId("term-publication-description").textContent, /no signed publication/);
}

for (const outcome of ["response", "failure"]) {
  test(`refresh keeps the new scan-only state when an older state ${outcome} arrives`, async t => {
    const old = deferred();
    let requests = 0;
    const {window} = await workspace(t, {...snapshot(), browser_service:true},
      () => ++requests === 1 ? old.promise : scanOnlyState());
    window.document.getElementById("term-refresh").click();
    await new Promise(resolve => setImmediate(resolve));
    assert.equal(requests, 2); assertScanOnly(window);
    const notice = window.document.getElementById("term-notice").textContent;
    if (outcome === "response") old.resolve(legacyState());
    else old.reject(new Error("Obsolete state failure"));
    await new Promise(resolve => setImmediate(resolve));
    assertScanOnly(window);
    assert.equal(window.document.getElementById("term-notice").textContent, notice);
  });
}

test("a later state request wins within the same snapshot generation", async t => {
  const old = deferred();
  let requests = 0;
  const {window} = await workspace(t, {...snapshot(), browser_service:true}, () => {
    requests += 1;
    return requests === 1 ? legacyState() : requests === 2 ? old.promise : scanOnlyState();
  });
  window.document.getElementById("term-reason").value = "Invented fixture reason.";
  const form = window.document.getElementById("term-proposal-form");
  form.dispatchEvent(new window.Event("submit", {cancelable:true}));
  await new Promise(resolve => setImmediate(resolve));
  form.dispatchEvent(new window.Event("submit", {cancelable:true}));
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(requests, 3); assertScanOnly(window);
  old.resolve(legacyState());
  await new Promise(resolve => setImmediate(resolve));
  assertScanOnly(window);
});

test("invalid current state cannot enable capabilities through candidate selection", async t => {
  const {window} = await workspace(t, {...snapshot(), browser_service:true},
    {proposals:"invalid", releases:[], capabilities:{submit:true, publication:true, enrollment:true}});
  const byId = id => window.document.getElementById(id);
  assert.match(byId("term-notice").textContent, /unsupported state format/);
  assert.equal(byId("term-submit").disabled, true);
  for (const id of ["term-new", "term-submit", "term-enroll", "term-prepare"])
    assert.equal(byId(id).hidden, true, id);
});
