(function () {
  "use strict";
  var menu = document.getElementById("account-menu");
  if (!menu) return;
  var toggle = document.getElementById("account-toggle");
  var name = document.getElementById("account-name");
  var email = document.getElementById("account-email");
  var status = document.getElementById("account-status");
  var membership = document.getElementById("account-membership");
  var groups = document.getElementById("account-groups");
  var emptyGroups = document.getElementById("account-groups-empty");
  var login = document.getElementById("account-login");
  var logout = document.getElementById("account-logout");
  var settings = document.getElementById("account-settings");
  var icons = Array.from(menu.querySelectorAll(".account-initials"));
  var photos = Array.from(menu.querySelectorAll(".account-photo"));
  var neutralIcon = icons[0].cloneNode(true);
  var pending = false;

  function text(value) { return typeof value === "string" ? value.trim() : ""; }
  function clearIdentity() {
    name.textContent = "Your profile";
    email.textContent = "";
    email.hidden = true;
    membership.hidden = true;
    groups.replaceChildren();
    photos.forEach(function (photo) {
      photo.onload = photo.onerror = null;
      photo.hidden = true;
      photo.removeAttribute("src");
    });
    icons.forEach(function (icon) {
      icon.hidden = false;
      icon.replaceChildren(neutralIcon.firstChild.cloneNode(true));
    });
  }
  function unavailable(signedOut) {
    clearIdentity();
    status.textContent = signedOut ? "You are signed out." : "Profile information is unavailable on this connection.";
    status.hidden = false;
    login.hidden = !signedOut;
    logout.hidden = signedOut;
    settings.hidden = signedOut;
  }
  function render(profile) {
    var label = text(profile.name) || text(profile.preferredUsername) ||
      text(profile.preferred_username) || text(profile.email) || text(profile.user);
    if (!label) throw new Error("Missing profile identity");
    clearIdentity();
    name.textContent = label;
    email.textContent = text(profile.email);
    email.hidden = !email.textContent || email.textContent === label;
    var words = label.split("@")[0].split(/[\s._-]+/).filter(Boolean);
    var initials = words.slice(0, 2).map(function (word) { return Array.from(word)[0]; }).join("").toUpperCase();
    icons.forEach(function (icon) { icon.textContent = initials || "?"; });
    var picture = text(profile.picture);
    if (picture) {
      try {
        var url = new URL(picture);
        if (url.protocol === "https:" && !url.username && !url.password) {
          photos.forEach(function (photo, index) {
            photo.onload = function () { photo.hidden = false; icons[index].hidden = true; };
            photo.onerror = function () { photo.hidden = true; icons[index].hidden = false; };
            photo.src = url.href;
          });
        }
      } catch (_) { /* Keep initials when a picture URL cannot be used. */ }
    }
    var claims = Array.isArray(profile.groups) ? profile.groups.filter(function (value) {
      return typeof value === "string" && value.trim();
    }) : [];
    Array.from(new Set(claims)).forEach(function (group) {
      var item = document.createElement("li");
      item.textContent = group;
      groups.appendChild(item);
    });
    groups.hidden = !groups.children.length;
    emptyGroups.hidden = !!groups.children.length;
    membership.hidden = false;
    status.hidden = true;
    settings.hidden = logout.hidden = false;
    login.hidden = true;
  }
  async function refresh() {
    if (pending) return;
    pending = true;
    var controller = new AbortController();
    var timeout = setTimeout(function () { controller.abort(); }, 8000);
    try {
      var response = await fetch("/oauth2/userinfo", {
        credentials: "same-origin", cache: "no-store", redirect: "error",
        headers: { Accept: "application/json" }, signal: controller.signal
      });
      if (response.status === 401 || response.status === 403) { unavailable(true); return; }
      if (!response.ok) throw new Error("Profile request failed");
      render(await response.json());
    } catch (_) { unavailable(false); }
    finally { clearTimeout(timeout); pending = false; }
  }
  menu.addEventListener("toggle", function () { if (menu.open) refresh(); });
  document.addEventListener("click", function (event) {
    if (menu.open && !menu.contains(event.target)) menu.open = false;
  });
  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && menu.open) {
      menu.open = false;
      toggle.focus();
    }
  });
  logout.addEventListener("click", function () {
    clearIdentity();
    var token = document.getElementById("authoring-token");
    if (token) token.value = "";
  });
  window.addEventListener("pageshow", function (event) { if (event.persisted) refresh(); });
  refresh();
})();
