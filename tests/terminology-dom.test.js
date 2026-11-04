"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const test = require("node:test");
const {JSDOM} = require("jsdom");
const {snapshot} = require("./fixtures/terminology");

async function workspace(t, data) {
  const dom = new JSDOM(fs.readFileSync("compile/assets/terminology.html", "utf8"),
    {url:"http://127.0.0.1/terminology.html", runScripts:"outside-only"});
  t.after(() => dom.window.close());
  const {window} = dom;
  const downloads = [];
  window.fetch = async () => ({ok:true, json:async () => data});
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
  return {window, downloads};
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
