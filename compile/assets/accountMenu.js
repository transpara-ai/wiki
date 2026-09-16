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
  var authoring = document.getElementById("account-authoring");
  var forget = document.getElementById("account-forget-authoring");
  var token = document.getElementById("authoring-token");
  var tokenLabel = document.getElementById("authoring-token-label");
  var remember = document.getElementById("remember-authoring");
  var authoringStatus = document.getElementById("authoring-profile-status");
  var profileEnabled = false;
  var saving = false;
  var identityVersion = 0;
  var icons = Array.from(menu.querySelectorAll(".account-initials"));
  var photos = Array.from(menu.querySelectorAll(".account-photo"));
  var neutralIcon = icons[0].cloneNode(true);
  var pending = false;

  function text(value) { return typeof value === "string" ? value.trim() : ""; }
  function clearIdentity() {
    identityVersion++;
    authoring.textContent = "Wiki authoring access has not been checked.";
    forget.hidden = true;
    profileEnabled = false;
    if (remember) remember.hidden = true;
    if (tokenLabel) tokenLabel.hidden = false;
    if (authoringStatus) authoringStatus.textContent = "Sign in to use remembered authoring access.";
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
  function showAuthoring(profile) {
    profileEnabled = profile.enabled === true && profile.signed_in === true;
    var saved = profileEnabled && profile.authoring === true;
    var message = saved ? "Authoring access is saved to your wiki profile." :
      (profileEnabled ? "Enter your authoring token once to remember access for this account." :
        "Sign in through the public wiki to remember authoring access.");
    authoring.textContent = message;
    if (authoringStatus) authoringStatus.textContent = message;
    forget.hidden = !saved;
    if (tokenLabel) tokenLabel.hidden = saved;
    if (remember) remember.hidden = !profileEnabled || saved;
    if (saved && token) token.value = "";
  }
  async function profileRequest(action) {
    var headers = { Accept: "application/json", "X-Wiki-Profile-Action": "1" };
    if (action === "remember" && token) headers["X-CivWiki-Authoring-Token"] = token.value;
    var controller = new AbortController();
    var timeout = setTimeout(function () { controller.abort(); }, 8000);
    try {
      var response = await fetch("/api/authoring-profile" + (action === "forget" ? "/forget" : ""), {
        method: action ? "POST" : "GET", credentials: "same-origin", cache: "no-store",
        redirect: "error", headers: headers, signal: controller.signal
      });
      var data = await response.json();
      if (!response.ok) throw new Error(data.error || "Authoring profile is unavailable.");
      return data;
    } finally { clearTimeout(timeout); }
  }
  async function changeAuthoring(action) {
    if (saving || !profileEnabled || (action === "remember" && (!token || !token.value))) return;
    saving = true;
    forget.disabled = true;
    if (remember) remember.disabled = true;
    var version = identityVersion;
    try {
      var data = await profileRequest(action);
      if (version !== identityVersion) return;
      showAuthoring(data);
      if (token) {
        token.value = "";
        // Refresh article/source metadata using the remembered account grant.
        token.dispatchEvent(new Event("change"));
      }
    } catch (error) {
      if (version !== identityVersion) return;
      authoring.textContent = error.message;
      if (authoringStatus) authoringStatus.textContent = error.message;
    } finally {
      saving = false;
      forget.disabled = false;
      if (remember) remember.disabled = false;
    }
  }
  forget.addEventListener("click", function () { changeAuthoring("forget"); });
  if (remember) remember.addEventListener("click", function () { changeAuthoring("remember"); });
  if (token) token.addEventListener("change", function () { changeAuthoring("remember"); });
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
      if (response.status === 401 || response.status === 403) {
        menu.hidden = false;
        unavailable(true);
        return;
      }
      if (response.status === 404) {
        menu.hidden = true;
        menu.open = false;
        unavailable(false);
        return;
      }
      if (!response.ok) throw new Error("Profile request failed");
      render(await response.json());
      menu.hidden = false;
      var version = identityVersion;
      try {
        var profile = await profileRequest();
        if (version === identityVersion) {
          showAuthoring(profile);
          if (token && token.value) changeAuthoring("remember");
        }
      } catch (_) {
        if (version === identityVersion) {
          authoring.textContent = "Remembered authoring access is unavailable on this connection.";
        }
      }
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
