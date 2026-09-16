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
used to grant editing authority: the existing authoring token still controls
mutations. Connecting profile photos or additional rights claims is a separate
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
changing proxy configuration, credentials, scopes, or authorization policy.
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
