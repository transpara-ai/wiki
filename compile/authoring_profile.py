"""Durable authoring grants bound to an independently verified login session."""
from contextlib import contextmanager
import hashlib
import hmac
import json
import os
from pathlib import Path
import sqlite3
from urllib import request
from urllib.error import HTTPError
from urllib.parse import urlsplit


class ProfileUnavailable(Exception):
    pass


class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def settings():
    url = os.environ.get('KNOWLEDGE_HUB_PROFILE_USERINFO_URL', '')
    origin = os.environ.get('KNOWLEDGE_HUB_PROFILE_ORIGIN', '')
    store = os.environ.get('KNOWLEDGE_HUB_PROFILE_STORE', '')
    if not any((url, origin, store)):
        return None
    u, o = urlsplit(url), urlsplit(origin)
    if (not all((url, origin, store)) or u.scheme not in {'http', 'https'}
            or not u.hostname or u.username or u.password or u.query or u.fragment
            or o.scheme != 'https' or not o.hostname or o.path or o.query
            or o.fragment or o.username or o.password or not Path(store).is_absolute()):
        raise ProfileUnavailable('Profile configuration is unavailable')
    return url, origin, Path(store)


def mutation_allowed(headers, config):
    return bool(config and headers.get('Origin') == config[1]
                and headers.get('X-Wiki-Profile-Action') == '1'
                and headers.get('Sec-Fetch-Site', 'same-origin') == 'same-origin')


def principal(headers, config):
    """Verify cookies server-to-server; never trust client identity headers."""
    if not config:
        return None
    cookie = headers.get('Cookie', '')
    if not cookie or len(cookie) > 32768 or '\r' in cookie or '\n' in cookie:
        return None
    req = request.Request(config[0], headers={'Cookie': cookie, 'Accept': 'application/json'})
    # Ignore HTTP(S)_PROXY environment variables and never follow redirects.
    opener = request.build_opener(request.ProxyHandler({}), NoRedirect())
    try:
        with opener.open(req, timeout=5) as response:
            if response.status != 200:
                return None
            data = response.read(65537)
            if len(data) > 65536:
                return None
            profile = json.loads(data)
        subject = profile.get('user') if isinstance(profile, dict) else None
        if not isinstance(subject, str) or not subject.strip() or len(subject) > 1024:
            return None
        return hashlib.sha256((config[0] + '\0' + subject).encode()).hexdigest()
    except HTTPError as error:
        error.close()
        return None
    except Exception:
        # Do not expose cookies, remote response bodies or configuration in errors.
        return None


def signature(key, token):
    return hmac.new(token.encode(), ('wiki-authoring-profile-v1\0' + key).encode(), hashlib.sha256).hexdigest()


@contextmanager
def connect(config):
    path = config[2]
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        os.fchmod(fd, 0o600)
    finally:
        os.close(fd)
    db = sqlite3.connect(path, timeout=5)
    try:
        with db:
            db.execute('CREATE TABLE IF NOT EXISTS grants (principal TEXT PRIMARY KEY, proof TEXT NOT NULL)')
            yield db
    finally:
        db.close()


def granted(config, key, token):
    if not config or not key or not token:
        return False
    try:
        with connect(config) as db:
            row = db.execute('SELECT proof FROM grants WHERE principal = ?', (key,)).fetchone()
        return bool(row and hmac.compare_digest(row[0], signature(key, token)))
    except (OSError, sqlite3.Error, TypeError):
        return False


def remember(config, key, token):
    if not config or not key or not token:
        raise ProfileUnavailable('Sign in and provide a valid authoring token first')
    try:
        with connect(config) as db:
            db.execute('INSERT OR REPLACE INTO grants VALUES (?, ?)', (key, signature(key, token)))
    except (OSError, sqlite3.Error):
        raise ProfileUnavailable('Could not save authoring access') from None


def forget(config, key):
    try:
        with connect(config) as db:
            db.execute('DELETE FROM grants WHERE principal = ?', (key,))
    except (OSError, sqlite3.Error):
        raise ProfileUnavailable('Could not forget authoring access') from None
