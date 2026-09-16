const assert = require("node:assert/strict");
const fs = require("node:fs");
const { JSDOM } = require("jsdom");
const { test } = require("node:test");

const html = fs.readFileSync("dist/index.html", "utf8");
const script = fs.readFileSync("compile/assets/accountMenu.js", "utf8");
const tick = () => new Promise(resolve => setTimeout(resolve, 15));

async function mount(response) {
  const dom = new JSDOM(html, { url: "https://wiki.example/index.html", runScripts: "outside-only" });
  const requests = [];
  dom.window.fetch = async (url, options) => {
    requests.push({ url, options });
    if (response instanceof Error) throw response;
    return response;
  };
  dom.window.eval(script);
  await tick();
  return { dom, doc: dom.window.document, requests };
}

const ok = data => ({ ok: true, status: 200, json: async () => data });

test("profile uses session identity, renders claims as text, and never stores them", async () => {
  const { dom, doc, requests } = await mount(ok({
    preferredUsername: "Pat Example", email: "pat@example.test",
    groups: ["wiki-contributors", "<img src=x onerror=alert(1)>", "wiki-contributors", null],
    picture: "javascript:alert(1)"
  }));
  try {
    assert.equal(doc.querySelector("#account-name").textContent, "Pat Example");
    assert.equal(doc.querySelector("#account-email").textContent, "pat@example.test");
    assert.equal(doc.querySelector(".account-initials").textContent, "PE");
    assert.equal(doc.querySelectorAll("#account-groups li").length, 2);
    assert.equal(doc.querySelectorAll("#account-groups img").length, 0);
    assert.equal(doc.querySelectorAll(".account-photo[src]").length, 0);
    assert.equal(dom.window.localStorage.length, 0);
    assert.equal(dom.window.sessionStorage.length, 0);
    assert.equal(requests[0].url, "/oauth2/userinfo");
    assert.equal(requests[0].options.credentials, "same-origin");
    assert.equal(requests[0].options.cache, "no-store");
    assert.equal(requests[0].options.redirect, "error");
    assert.equal(doc.querySelector("#account-logout").hidden, false);
    assert.equal(doc.querySelector("#account-menu").hidden, false);
    const url = new URL(doc.querySelector("#account-logout").href);
    assert.equal(url.pathname, "/oauth2/sign_out");
    assert.match(url.searchParams.get("rd"), /\/protocol\/openid-connect\/logout$/);
  } finally { dom.window.close(); }
});

test("picture loading and failure preserve an initials fallback", async () => {
  const { dom, doc } = await mount(ok({ name: "Pat Example", picture: "https://identity.example/picture.png" }));
  try {
    const photo = doc.querySelector(".account-photo");
    assert.equal(photo.getAttribute("referrerpolicy"), "no-referrer");
    photo.dispatchEvent(new dom.window.Event("load"));
    assert.equal(photo.hidden, false);
    assert.equal(doc.querySelector(".account-initials").hidden, true);
    photo.dispatchEvent(new dom.window.Event("error"));
    assert.equal(photo.hidden, true);
    assert.equal(doc.querySelector(".account-initials").hidden, false);
    assert.equal(doc.querySelector("#account-groups-empty").hidden, false);
  } finally { dom.window.close(); }
});

for (const [label, response, signedOut] of [
  ["expired session", { ok: false, status: 401 }, true],
  ["refused session", { ok: false, status: 403 }, true],
  ["static preview", { ok: false, status: 404 }, false],
  ["network failure", new Error("unreachable"), false],
  ["login HTML", { ok: true, status: 200, json: async () => { throw new Error("not JSON"); } }, false],
  ["empty session", ok({}), false]
]) {
  test(label + " has an honest profile state", async () => {
    const { dom, doc } = await mount(response);
    try {
      assert.equal(doc.querySelector("#account-membership").hidden, true);
      assert.equal(doc.querySelector("#account-login").hidden, !signedOut);
      assert.equal(doc.querySelector("#account-logout").hidden, signedOut);
      assert.match(doc.querySelector("#account-status").textContent, signedOut ? /signed out/ : /unavailable/);
      assert.equal(doc.querySelector("#account-menu").hidden, !signedOut);
    } finally { dom.window.close(); }
  });
}

test("reopening after expiry removes the previous user's identity and groups", async () => {
  const { dom, doc } = await mount(ok({ preferredUsername: "Pat", groups: ["contributors"] }));
  try {
    dom.window.fetch = async () => ({ ok: false, status: 401 });
    doc.querySelector("#account-menu").open = true;
    await tick();
    assert.equal(doc.querySelector("#account-name").textContent, "Your profile");
    assert.equal(doc.querySelectorAll("#account-groups li").length, 0);
    assert.equal(doc.querySelector("#account-email").textContent, "");
  } finally { dom.window.close(); }
});

test("logout clears the displayed identity and editor input before leaving", async () => {
  const { dom, doc } = await mount(ok({ preferredUsername: "Pat" }));
  try {
    const input = doc.createElement("input");
    input.id = "authoring-token";
    input.value = "example-editor-value";
    doc.body.appendChild(input);
    const logout = doc.querySelector("#account-logout");
    logout.addEventListener("click", event => event.preventDefault());
    logout.click();
    assert.equal(input.value, "");
    assert.equal(doc.querySelector("#account-name").textContent, "Your profile");
  } finally { dom.window.close(); }
});
