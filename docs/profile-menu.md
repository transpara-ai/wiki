# Wiki profile menu

The profile button appears at the top right of authoring wiki pages. It shows
the signed-in username and email, links to tAuth account settings, and offers
**Log out**. Keyboard users can open it with Enter or Space, tab through the
links, and press Escape to close it and return focus to the button. It also
closes when clicking outside.

The browser reads `/oauth2/userinfo` from the existing authenticated proxy with
same-origin credentials and no caching. Identity is never included in generated
HTML, search indexes, local storage, or session storage. A signed-out response
clears displayed identity and offers sign-in. The menu starts hidden and is
enabled only after the profile service returns an identity or an explicit
signed-out response. A missing endpoint keeps the entire menu hidden, so direct
SSH access and static previews do not offer account actions that cannot work.

The deployed OAuth2 Proxy 7.7.1 returns `user`, `email`, `preferredUsername`, and
any configured `groups`. It does not return a picture. The menu therefore uses
initials today; it can display an HTTPS `picture` claim when the identity
integration supplies one, with an initials fallback for unavailable images.
No third-party avatar lookup is used. Group names are displayed only when
supplied, and detailed rights are explicitly marked unavailable. Neither is
used to grant editing authority: authoring requires either the token or a saved, verified account grant. Connecting profile photos or additional rights claims is a separate
tAuth/proxy integration task.

`compile/account_config.json` contains the public tAuth account-settings and
OIDC end-session URLs. It contains no credentials. The profile menu is omitted
from restricted publication profiles; these require their own account integration.

Logout first visits `/oauth2/sign_out`, then redirects to tAuth's end-session
endpoint, which may ask the user to confirm logout. This avoids clearing only
the wiki cookie and immediately signing in again through an existing tAuth
session. The tAuth host must remain in the proxy's existing redirect allowlist.
The editor-token field is cleared on logout. The wiki does not manipulate tAuth
cookies or retrieve OAuth access/ID tokens.

The implementation uses the existing session and logout contracts without
changing credentials, scopes, or identity-provider policy.
The public Velia route already supplies `/oauth2/*` through DevOps' OAuth2 Proxy
override, ahead of the authoring server. The base Compose/Tailscale direct-server
route does not supply these endpoints and therefore does not enable the menu.
See the [OAuth2 Proxy 7.7 endpoint documentation](https://oauth2-proxy.github.io/oauth2-proxy/7.7.x/features/endpoints/)
and [Keycloak's OIDC endpoints](https://www.keycloak.org/securing-apps/oidc-layers).

Validation covers session states, safe claim rendering, image fallback,
keyboard/touch access, small screens, nested page routes, and logout navigation
in Chromium and WebKit. Browser fixtures test signed-in claims without requiring
or recording a user's credentials. A live signed-in user must verify their own
displayed identity and complete tAuth's logout confirmation.

## Proxy timeout for authoring

Rebuild and ingest requests remain open while the wiki refreshes its output.
The deployed corpus takes about 50 seconds to rebuild, exceeding OAuth2 Proxy's
30-second default. Set `--upstream-timeout=300s` in the existing OAuth2 Proxy
service command. Configure the outer reverse proxy's response/read timeout to
at least 300 seconds too. Keep existing authentication and routing settings.
See [OAuth2 Proxy upstream configuration](https://oauth2-proxy.github.io/oauth2-proxy/7.7.x/configuration/overview/).

An HTML 502/504 error can mean the proxy stopped waiting while the wiki continued
working. Check the site's updated time before repeating an ingest operation;
repeating it could submit material twice. The browser reports this uncertainty
instead of displaying a JSON parsing error. Server logs distinguish a proxy
response timeout from an authoring-token refusal or a failed refresh.


## Remembered authoring access (v0.7.0)

On Ingest, enter a valid authoring token once while signed in. Leaving the field
or choosing **Remember authoring access** saves access to the wiki profile and
clears the token field. Later visits and other browsers use your signed-in tAuth
account automatically. The profile shows the saved status and offers **Forget
authoring access**. Logout ends the login session but keeps this account setting.
A saved grant has no expiry; forgetting it or rotating the shared token revokes it.
This is a wiki-owned account setting, not a token stored as a tAuth attribute.

The server verifies the existing session cookie directly with the configured
OAuth2 Proxy userinfo endpoint. It never trusts forwarded username/email headers.
The database stores only an opaque account key and keyed grant proof, not tokens,
raw subjects, email addresses or session cookies. The original shared token is
not stored in cookies, localStorage, sessionStorage or generated pages. Other
accounts are not enabled by this setting. Destructive operations still require
their existing separate authorization artifacts.

Enable on the authoring service only, with these environment values and a durable
private mount (the examples contain no credentials):

```yaml
services:
  wiki:
    environment:
      KNOWLEDGE_HUB_PROFILE_USERINFO_URL: http://oauth2-proxy:4180/oauth2/userinfo
      KNOWLEDGE_HUB_PROFILE_ORIGIN: https://wiki.transpara.io
      KNOWLEDGE_HUB_PROFILE_STORE: /var/lib/wiki-profiles/authoring.sqlite3
    volumes:
      - ./.private/profiles:/var/lib/wiki-profiles
```

Precreate the host directory owned by the wiki runtime user with mode 0700. The
database is mode 0600; preserve this private directory in host backups, exclude
it from Git/static output, and retain it across container replacements. The
verifier URL is trusted administrator configuration and must point directly to
the existing proxy; it cannot come from a request. If its identity provider or
issuer changes, clear grants before switching (or use a new verifier URL namespace).
Cookie-authorized mutations require the exact configured HTTPS Origin and a
custom request header. Missing configuration keeps the original token-only API;
verification failures deny remembered access. Token-bearing automation retains
its existing header contract.
