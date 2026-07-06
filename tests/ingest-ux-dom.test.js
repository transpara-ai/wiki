// tests/ingest-ux-dom.test.js
// DOM state-machine tests for the ingest destructive-mode preview gate
// (fe-ux packet AC2, docs/superpowers/specs/2026-07-06-front-end-ux-packet.md).
// Drives dist/ingest.html in jsdom with a stubbed fetch across the domain:
// preview ok -> armed; selection change -> disarmed + confirm reset; STALE
// (out-of-order) response discarded by sequence token; confirm-before-preview
// stays disabled; fetch error -> disabled + explicit notice; refuses-shape
// renders the refusal and never arms. Runs after `npm run build`.
const fs = require("fs");
const path = require("path");
const assert = require("assert");
const { JSDOM } = require("jsdom");

const root = path.resolve(__dirname, "..");
const page = path.join(root, "dist", "ingest.html");
assert.ok(fs.existsSync(page), "dist/ingest.html missing — run npm run build");
const html = fs.readFileSync(page, "utf8");

// ---- controllable fetch stub -------------------------------------------
const previewQueue = []; // {url, resolve, reject}
function stubFetch(window) {
  window.fetch = function (url) {
    url = String(url);
    if (url.indexOf("/api/preview") === 0) {
      return new Promise(function (resolve, reject) {
        previewQueue.push({
          url: url,
          ok: function (payload) {
            resolve({ ok: true, status: 200,
                      json: function () { return Promise.resolve(payload); } });
          },
          fail: function () { reject(new Error("network down")); },
        });
      });
    }
    if (url.indexOf("/api/articles") === 0) {
      return Promise.resolve({ ok: true, status: 200,
        json: function () { return Promise.resolve({ articles: [] }); } });
    }
    // deploy-status.json and anything else: harmless miss
    return Promise.resolve({ ok: false, status: 404,
      json: function () { return Promise.resolve({}); } });
  };
}

const dom = new JSDOM(html, { runScripts: "dangerously", beforeParse: stubFetch });
const doc = dom.window.document;
const flush = () => new Promise((r) => setTimeout(r, 0));
const changed = (el) => el.dispatchEvent(new dom.window.Event("change", { bubbles: true }));

const rm = {
  radio: doc.querySelector('input[name="ingest-mode"][value="remove"]'),
  target: doc.getElementById("rm-target"),
  panel: doc.getElementById("rm-preview"),
  confirm: doc.getElementById("rm-confirm"),
  submit: doc.getElementById("rm-submit"),
};
const slugs = Array.prototype.slice.call(rm.target.options)
  .map((o) => o.value).filter(Boolean);
assert.ok(slugs.length >= 2, "need two article options to drive the machine");

function assertDisarmed(msg) {
  assert.strictEqual(rm.submit.disabled, true, msg + ": submit must be disabled");
  assert.strictEqual(rm.confirm.checked, false, msg + ": confirm must be reset");
}

(async function () {
  await flush();

  // birth state: everything disarmed, destructive panels hidden
  assertDisarmed("at birth");
  assert.strictEqual(rm.confirm.disabled, true, "confirm disabled at birth");
  assert.ok(doc.querySelector('[data-mode-panel="remove"]').hidden, "remove panel hidden at birth");

  // enter remove mode, pick a target -> preview fetch fires
  rm.radio.checked = true; changed(rm.radio);
  assert.ok(!doc.querySelector('[data-mode-panel="remove"]').hidden, "remove panel shown");
  rm.target.value = slugs[0]; changed(rm.target);
  await flush();
  assert.strictEqual(previewQueue.length, 1, "one preview in flight");

  // confirm-before-preview lane: forcing the (disabled) confirm never arms
  rm.confirm.checked = true; changed(rm.confirm);
  assert.strictEqual(rm.submit.disabled, true, "confirm before preview must not arm");
  rm.confirm.checked = false;

  // preview ok -> confirm enabled; checking it arms the submit
  const p1 = previewQueue.shift();
  p1.ok({ preview: { operation: "remove", slug: slugs[0], inbound: ["some-article"],
                     edges_would_pend: 1, tombstone: slugs[0] + ".html", will_recompile: true } });
  await flush(); await flush();
  assert.strictEqual(rm.confirm.disabled, false, "preview ok enables confirm");
  assert.ok(rm.panel.innerHTML.indexOf("pending reconciliation") !== -1, "consequences rendered");
  rm.confirm.checked = true; changed(rm.confirm);
  assert.strictEqual(rm.submit.disabled, false, "previewed + confirmed arms the submit");

  // selection change -> disarmed, confirm reset, NEW preview in flight
  rm.target.value = slugs[1]; changed(rm.target);
  await flush();
  assertDisarmed("after selection change");
  assert.strictEqual(previewQueue.length, 1, "re-preview in flight");
  const p2 = previewQueue.shift();

  // third selection queued before p2 resolves -> p2 becomes STALE
  rm.target.value = slugs[0]; changed(rm.target);
  await flush();
  assert.strictEqual(previewQueue.length, 1, "third preview in flight");
  const p3 = previewQueue.shift();
  p2.ok({ preview: { operation: "remove", slug: slugs[1], inbound: [],
                     edges_would_pend: 0, tombstone: slugs[1] + ".html", will_recompile: true } });
  await flush(); await flush();
  assert.strictEqual(rm.confirm.disabled, true,
    "a STALE (out-of-order) preview response must never enable the gate");
  assertDisarmed("after stale response");

  // current preview fails -> explicit notice, still disarmed
  p3.fail();
  await flush(); await flush();
  assert.ok(rm.panel.textContent.indexOf("Preview unavailable") !== -1,
    "failed preview renders the explicit disabled notice");
  assertDisarmed("after preview failure");

  // refuses-shape: renders the refusal, never arms
  rm.target.value = slugs[1]; changed(rm.target);
  await flush();
  const p4 = previewQueue.shift();
  p4.ok({ preview: { operation: "remove", slug: slugs[1], refuses: "article is already retired" } });
  await flush(); await flush();
  assert.ok(rm.panel.innerHTML.indexOf("already retired") !== -1, "refusal rendered");
  assert.strictEqual(rm.confirm.disabled, true, "a refused preview never enables confirm");
  assertDisarmed("after refuses-shape");

  console.log("ok: ingest preview gate state machine (7 lanes)");
})().catch(function (e) { console.error(e); process.exit(1); });
