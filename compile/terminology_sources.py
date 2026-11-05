"""Capture approved text as data for a finite terminology job.

Requests cannot choose credentials, local files, executables, or checker policy.
GitHub inputs resolve one commit and read its tree/blob objects; repository code
is never checked out or executed. The default HTTP subprocess reuses the wiki's
public-DNS-pinned TLS connector. A parent timeout bounds DNS, TLS, headers, and
body reads together, including a peer that sends bytes very slowly. Injected
fetchers are trusted host/test adapters and must honor the supplied timeout and
byte budget. They must not follow redirects internally.
Public capture is the default. An optional private host descriptor can permit
the existing curator cohort to read exact GitHub repositories with one approved
credential reference. That credential reaches only their GitHub API prefix.
"""
import base64
import binascii
import fnmatch
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import time
from urllib.parse import parse_qsl, quote, unquote, urljoin, urlsplit

from knowledge_sources import Fetcher, origin, validate_url
from knowledge_store import host_json

MAX_REQUESTS = 300
MAX_BYTES = 16 * 1024 * 1024
MAX_FILE_BYTES = 1024 * 1024
MAX_FILES = 256
MAX_SECONDS = 60
MAX_REDIRECTS = 5
SUPPORTED_SUFFIXES = ('.md', '.markdown', '.txt', '.py')
SHA = re.compile(r'[0-9a-f]{40}')
GITHUB_CONFIG_ENV = 'TRANSPARA_TERMINOLOGY_GITHUB_CONFIG'


class CaptureError(ValueError):
    """An input or transport failure, with no fetched text in its message."""


class _Limit(CaptureError):
    def __init__(self, reason):
        self.reason = reason
        super().__init__('The source capture budget was exhausted.')


def _safe_url(value):
    try:
        validate_url(value)
        parsed = urlsplit(value)
        if '\\' in value or '%' in parsed.hostname or not value.isascii():
            raise ValueError()
        # The older shared validator checks a small set of names. This lane also
        # refuses common signed-URL/session fields instead of persisting them.
        for key, _ in parse_qsl(parsed.query):
            key = re.sub(r'[^a-z0-9]', '', key.lower())
            if any(part in key for part in ('token', 'secret', 'password', 'credential', 'signature', 'apikey')) or key in {'auth', 'authorization', 'sig', 'session', 'sessionid'}:
                raise ValueError()
    except (ValueError, TypeError, AttributeError, UnicodeError):
        raise CaptureError('Use a public HTTPS address without credentials.') from None
    return value


def validate_request(request):
    """Validate and normalize a request without DNS, files, or other effects."""
    if not isinstance(request, dict) or request.get('type') not in {'url', 'repo'}:
        raise CaptureError('Choose a URL or a GitHub repository.')
    allowed = {'type', 'url'} | ({'ref', 'paths'} if request['type'] == 'repo' else set())
    if set(request) - allowed:
        raise CaptureError('Unsupported source request fields.')
    url = _safe_url(request.get('url'))
    result = {'type': request['type'], 'url': url}
    if request['type'] == 'url':
        return result
    parsed = urlsplit(url)
    match = re.fullmatch(r'/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)/?', parsed.path)
    if parsed.hostname != 'github.com' or parsed.query or not match:
        raise CaptureError('Use a GitHub repository address with owner and repository only.')
    owner, name = match.groups()
    name = name[:-4] if name.endswith('.git') else name
    if owner in {'.', '..'} or not name or name in {'.', '..'}:
        raise CaptureError('Use a GitHub repository address with owner and repository only.')
    result['url'] = 'https://github.com/' + owner + '/' + name
    ref = request.get('ref', 'HEAD')
    if (not isinstance(ref, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._/-]{0,254}', ref)
            or any(part in {'.', '..', ''} for part in ref.split('/'))):
        raise CaptureError('Use a branch, tag, or commit reference.')
    paths = request.get('paths', ['*'])
    if (not isinstance(paths, list) or not 1 <= len(paths) <= 64
            or any(not isinstance(item, str) or not 1 <= len(item) <= 300
                   or item.startswith('/') or '\\' in item
                   or any(ord(char) < 32 or ord(char) == 127 for char in item)
                   or any(part in {'.', '..'} for part in item.split('/')) for item in paths)):
        raise CaptureError('Use up to 64 relative path patterns without traversal.')
    result.update(ref=ref, paths=list(paths))
    return result


def _request_headers(url, headers, api_prefix):
    """Confine an optional bearer to one exact, server-authorized API repo.

    Decode path escapes before checking traversal, including repeated encoding.
    A redirect to another repository must fail before opening its connection;
    neither a shared host name nor a similar repository prefix is sufficient.
    """
    if not headers:
        return {}
    try:
        if not isinstance(headers, dict) or set(headers) != {'Authorization'}:
            raise ValueError()
        value = headers['Authorization']
        if (not isinstance(value, str) or not value.startswith('Bearer ') or len(value) > 4096
                or not re.fullmatch(r'[A-Za-z0-9._~+/-]+=*', value[7:])):
            raise ValueError()
        if not isinstance(api_prefix, str) or not re.fullmatch(r'/repos/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/', api_prefix):
            raise ValueError()
        if any(part in {'.', '..'} for part in api_prefix.split('/')):
            raise ValueError()
        parsed = urlsplit(url)
        path = parsed.path
        for _ in range(4):
            decoded = unquote(path)
            if decoded == path:
                break
            path = decoded
        if (parsed.scheme != 'https' or parsed.netloc != 'api.github.com'
                or '%' in path or '\\' in path or any(part in {'.', '..'} for part in path.split('/'))
                or not path.lower().startswith(api_prefix.lower())):
            raise ValueError()
    except (ValueError, TypeError, AttributeError):
        raise CaptureError('The approved source credential cannot be used for this destination.') from None
    return {'Authorization': value}


def _github_access(request):
    """Load optional host authority; client requests never select a credential.

    The allowlist authorizes the whole existing curator cohort, not individual
    callers. Repositories outside it remain anonymous. A malformed configured
    descriptor fails closed, and no descriptor is read for ordinary URL jobs.
    """
    selected = os.environ.get(GITHUB_CONFIG_ENV, '')
    if request['type'] != 'repo' or not selected:
        return {}, None
    try:
        path = Path(selected)
        if not path.is_absolute() or '..' in path.parts or any(p.is_symlink() for p in (path, *path.parents)):
            raise ValueError()
        info = path.stat()
        if not stat.S_ISREG(info.st_mode) or info.st_size > 16384:
            raise ValueError()
        config = host_json(path, private=True)
        if (not isinstance(config, dict) or set(config) != {'schema_version', 'credential_ref', 'repositories'}
                or type(config['schema_version']) is not int or config['schema_version'] != 1
                or not isinstance(config['credential_ref'], str)
                or not re.fullmatch(r'[A-Za-z0-9_.-]{1,80}', config['credential_ref'])):
            raise ValueError()
        repositories = config['repositories']
        if (not isinstance(repositories, list) or len(repositories) > 100
                or any(not isinstance(item, str) or len(item) > 256
                       or not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', item)
                       or any(part in {'.', '..'} for part in item.split('/')) for item in repositories)):
            raise ValueError()
        approved = {item.lower() for item in repositories}
        if len(approved) != len(repositories):
            raise ValueError()
        repository = urlsplit(request['url']).path.strip('/').lower()
        if repository not in approved:
            return {}, None
        prefix = '/repos/' + repository + '/'
        # The existing registry reader checks descriptor ownership/permissions.
        # Refuse a mistaken FIFO/device or unbounded registry before its open.
        registry = Path(os.environ.get('KNOWLEDGE_HUB_CREDENTIALS', ''))
        if (not registry.is_absolute() or '..' in registry.parts
                or any(p.is_symlink() for p in (registry, *registry.parents))):
            raise ValueError()
        info = registry.stat()
        if not stat.S_ISREG(info.st_mode) or info.st_size > 65536:
            raise ValueError()
        entries = host_json(registry, private=True)
        entry = entries.get(config['credential_ref']) if isinstance(entries, dict) else None
        if (not isinstance(entry, dict) or entry.get('type') not in {'github', 'bearer'}
                or not isinstance(entry.get('origins'), list)
                or not all(isinstance(item, str) for item in entry['origins'])
                or 'https://api.github.com' not in entry['origins']
                or not isinstance(entry.get('environment'), str)
                or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]{0,199}', entry['environment'])):
            raise ValueError()
        headers = Fetcher(None).credential(config['credential_ref'], 'https://api.github.com')
        if not headers:
            raise ValueError()
        return _request_headers('https://api.github.com' + prefix, headers, prefix), prefix
    except Exception:
        # Neither the descriptor's private path nor a secret-scoped registry
        # exception is appropriate for a browser-visible source failure.
        raise CaptureError('The approved GitHub source configuration is unavailable.') from None


# The worker imports only our trusted connector. Its environment contains no
# credentials or SSH agent. An optional source header travels only through its
# bounded stdin, and is checked again before use. Raw bytes follow one bounded JSON
# header line, avoiding base64 expansion of the whole HTTP response in the IPC.
_HTTP_WORKER = r'''
import http.client, json, ssl, sys
sys.path.insert(0, sys.argv[1])
from knowledge_sources import PinnedHTTPS, validate_url
from terminology_sources import _request_headers
try:
    payload = sys.stdin.buffer.read(16385)
    if len(payload) > 16384:
        raise ValueError()
    req = json.loads(payload)
    validate_url(req['url'])
    from urllib.parse import urlsplit
    p = urlsplit(req['url'])
    connection = PinnedHTTPS(p.hostname, timeout=req['timeout'], context=ssl.create_default_context())
    try:
        request_headers = {'User-Agent':'Transpara-Terminology/1', 'Accept-Encoding':'identity', 'Accept':'application/vnd.github+json' if p.hostname == 'api.github.com' else 'text/plain, text/markdown, text/html'}
        request_headers.update(_request_headers(req['url'], req.get('headers', {}), req.get('api_prefix')))
        connection.request('GET', (p.path or '/') + ('?' + p.query if p.query else ''),
                           headers=request_headers)
        response = connection.getresponse()
        headers = {k.lower():v for k,v in response.getheaders()}
        if headers.get('content-encoding', 'identity').lower() not in ('', 'identity'):
            raise ValueError()
        header = json.dumps([response.status, headers], separators=(',', ':')).encode()
        if len(header) > 65536:
            raise ValueError()
        body = response.read(req['byte_budget'] + 1)
        if len(body) > req['byte_budget']:
            sys.exit(3)
        sys.stdout.buffer.write(header + b'\n' + body)
    finally:
        connection.close()
except Exception:
    sys.exit(2)
'''


def _public_fetch(url, config):
    """Run one DNS-pinned GET; approved headers never enter argv or environment."""
    headers = _request_headers(url, config.get('headers', {}), config.get('api_prefix'))
    payload = json.dumps({'url': url, 'timeout': config['timeout'], 'byte_budget': config['byte_budget'],
                          'headers': headers, 'api_prefix': config.get('api_prefix')}).encode()
    if len(payload) > 16384:
        raise CaptureError('The source transport configuration exceeds its byte limit.')
    try:
        result = subprocess.run(
            [sys.executable, '-I', '-c', _HTTP_WORKER, str(Path(__file__).resolve().parent)],
            input=payload, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            env={'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8'}, timeout=config['timeout'], check=False)
        if result.returncode == 3:
            raise CaptureError('A source response exceeds the capture size limit.')
        if result.returncode or len(result.stdout) > config['byte_budget'] + 65537:
            raise CaptureError('The source could not be fetched safely.')
        header, body = result.stdout.split(b'\n', 1)
        status, headers = json.loads(header)
        return status, headers, body
    except CaptureError:
        raise
    except (OSError, subprocess.TimeoutExpired, ValueError, TypeError):
        raise CaptureError('The source could not be fetched within its deadline.') from None


class _Budget:
    def __init__(self, fetcher, clock, cancelled, *, headers=None, api_prefix=None):
        self.fetcher, self.clock, self.cancelled = fetcher or _public_fetch, clock, cancelled
        self.deadline = clock() + MAX_SECONDS
        self.requests = self.network_bytes = self.document_bytes = 0
        self.considered = 0
        self.skipped_count = self.incomplete_skips = 0
        self.headers, self.api_prefix = headers or {}, api_prefix

    def check(self):
        if self.cancelled():
            raise CaptureError('Source capture was cancelled.')
        remaining = self.deadline - self.clock()
        if remaining <= 0:
            raise _Limit('deadline')
        return remaining

    def get(self, url, *, byte_limit=MAX_BYTES):
        """Count every real request, including redirects; never cross origins."""
        approved = origin(_safe_url(url))
        for redirect in range(MAX_REDIRECTS + 1):
            remaining = self.check()
            if self.requests >= MAX_REQUESTS:
                raise _Limit('requests')
            available = min(byte_limit, MAX_BYTES - self.network_bytes)
            if available <= 0:
                raise _Limit('bytes')
            self.requests += 1
            config = {'byte_budget': available, 'timeout': min(20, remaining),
                      'deadline': self.deadline, 'credential_ref': '',
                      'headers': _request_headers(url, self.headers, self.api_prefix),
                      'api_prefix': self.api_prefix}
            try:
                status, headers, raw = self.fetcher(url, config)
            except (CaptureError, _Limit):
                raise
            except Exception:
                raise CaptureError('The source could not be fetched safely.') from None
            self.check()
            if (type(status) is not int or not isinstance(headers, dict) or not isinstance(raw, bytes)
                    or len(raw) > available):
                raise CaptureError('The source response exceeds the capture contract.')
            self.network_bytes += len(raw)
            if self.headers and self.headers['Authorization'][7:].encode('ascii') in raw:
                raise CaptureError('The source response failed its credential disclosure check.')
            headers = {str(k).lower(): str(v) for k, v in headers.items()}
            if headers.get('content-encoding', 'identity').lower() not in {'', 'identity'}:
                raise CaptureError('Compressed source responses are unsupported.')
            if status in {301, 302, 303, 307, 308}:
                if redirect == MAX_REDIRECTS:
                    raise _Limit('redirects')
                target = _safe_url(urljoin(url, headers.get('location', '')))
                if origin(target) != approved:
                    raise CaptureError('Source redirects must remain on the same origin.')
                _request_headers(target, self.headers, self.api_prefix)
                url = target
                continue
            if status != 200:
                raise CaptureError('The source did not return an available document.')
            return headers, raw, url
        raise _Limit('redirects')


class _HTMLText(HTMLParser):
    """Extract visible prose without executing or following active HTML content."""
    HIDDEN = {'script', 'style', 'noscript', 'template', 'form', 'textarea', 'select',
              'button', 'iframe', 'object', 'svg'}
    BREAKS = {'p', 'div', 'br', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'section', 'article', 'tr'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hidden = []
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if self.hidden:
            if tag in self.HIDDEN:
                self.hidden.append(tag)
        elif tag in self.HIDDEN:
            self.hidden.append(tag)
        elif tag in self.BREAKS:
            self.parts.append('\n')

    def handle_endtag(self, tag):
        if self.hidden:
            if tag == self.hidden[-1]:
                self.hidden.pop()
        elif tag in self.BREAKS:
            self.parts.append('\n')

    def handle_data(self, text):
        if not self.hidden:
            self.parts.append(text)


def _document(label, raw, content_type, budget):
    budget.check()
    if len(raw) > MAX_FILE_BYTES or b'\0' in raw:
        return None
    try:
        text = raw.decode('utf-8-sig', errors='strict')
    except UnicodeError:
        return None
    if content_type == 'text/html':
        parser = _HTMLText()
        try:
            parser.feed(text)
            parser.close()
        except Exception:
            raise CaptureError('The HTML source could not be extracted safely.') from None
        text = '\n'.join(line.strip() for line in ''.join(parser.parts).splitlines() if line.strip())
    encoded = text.encode('utf-8')
    if not text.strip() or len(encoded) > MAX_FILE_BYTES:
        return None
    if budget.document_bytes + len(encoded) > MAX_BYTES:
        raise _Limit('document-bytes')
    budget.document_bytes += len(encoded)
    budget.check()
    return {'label': label, 'text': text, 'source_sha256': hashlib.sha256(raw).hexdigest(),
            'text_sha256': hashlib.sha256(encoded).hexdigest()}


def _json(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError()
            result[key] = value
        return result
    try:
        value = json.loads(raw, object_pairs_hook=unique,
                           parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
        if not isinstance(value, dict):
            raise ValueError()
        return value
    except (ValueError, TypeError, UnicodeError, RecursionError):
        raise CaptureError('The repository returned unsupported metadata.') from None


def _safe_path(path):
    return (isinstance(path, str) and 0 < len(path) <= 1024 and not path.startswith('/')
            and '\\' not in path and not any(ord(c) < 32 or ord(c) == 127 for c in path)
            and not any(part in {'', '.', '..'} for part in path.split('/')))


def _skip(skipped, budget, label, reason):
    """Keep counts for the whole tree but bound the returned diagnostic sample."""
    budget.skipped_count += 1
    if reason != 'outside-selected-paths':
        budget.incomplete_skips += 1
    if len(skipped) < MAX_FILES:
        skipped.append({'label': label, 'reason': reason})


def capture(request, *, fetcher=None, clock=time.monotonic, cancelled=lambda: False):
    """Return exact-source provenance plus explicit finite capture coverage.

    Limits are fixed server policy, not request options. Network payload bytes
    (including GitHub JSON/base64 envelopes) and extracted UTF-8 document bytes
    each have a 16 MiB ceiling; one file is at most 1 MiB. A limit reached after
    partial progress returns complete=false. Invalid inputs, unsafe destinations,
    malformed responses, and cancellation fail with a sanitized CaptureError.
    """
    request = validate_request(request)
    headers, api_prefix = _github_access(request)
    budget = _Budget(fetcher, clock, cancelled, headers=headers, api_prefix=api_prefix)
    documents, skipped, reasons = [], [], []
    source = {'kind': request['type'], 'url': request['url']}
    try:
        if request['type'] == 'url':
            headers, raw, actual = budget.get(request['url'], byte_limit=MAX_FILE_BYTES)
            source['url'] = actual
            budget.considered += 1
            content_type = headers.get('content-type', '').split(';', 1)[0].strip().lower()
            if content_type not in {'text/plain', 'text/markdown', 'text/x-markdown', 'text/html'}:
                _skip(skipped, budget, actual, 'unsupported-media-type')
            else:
                document = _document(actual, raw, content_type, budget)
                if document is None:
                    _skip(skipped, budget, actual, 'unsupported-text-or-size')
                else:
                    documents.append(document)
        else:
            repository = urlsplit(request['url']).path.strip('/')
            base = 'https://api.github.com/repos/' + repository
            _, raw, _ = budget.get(base + '/commits/' + quote(request['ref'], safe=''), byte_limit=MAX_FILE_BYTES)
            commit = _json(raw)
            sha = commit.get('sha')
            commit_metadata = commit.get('commit')
            tree_metadata = commit_metadata.get('tree') if isinstance(commit_metadata, dict) else None
            tree_sha = tree_metadata.get('sha') if isinstance(tree_metadata, dict) else None
            if not isinstance(sha, str) or not SHA.fullmatch(sha) or not isinstance(tree_sha, str) or not SHA.fullmatch(tree_sha):
                raise CaptureError('The repository commit could not be pinned.')
            source['commit'] = sha
            _, raw, _ = budget.get(base + '/git/trees/' + tree_sha + '?recursive=1')
            tree = _json(raw)
            if tree.get('truncated') is not False or not isinstance(tree.get('tree'), list):
                raise CaptureError('The repository tree is incomplete; narrow the source scope.')
            if tree.get('sha') != tree_sha:
                raise CaptureError('The repository tree does not match the pinned commit.')
            seen = set()
            for item in tree['tree']:
                budget.check()
                if not isinstance(item, dict):
                    raise CaptureError('The repository returned unsupported metadata.')
                if item.get('type') == 'tree':
                    continue
                budget.considered += 1
                path = item.get('path')
                if not _safe_path(path):
                    _skip(skipped, budget, '[invalid path]', 'unsafe-path')
                    continue
                if path in seen:
                    raise CaptureError('The repository tree contains duplicate paths.')
                seen.add(path)
                if not any(fnmatch.fnmatchcase(path, pattern) for pattern in request['paths']):
                    _skip(skipped, budget, path, 'outside-selected-paths')
                    continue
                if item.get('type') != 'blob' or item.get('mode') not in {'100644', '100755'}:
                    _skip(skipped, budget, path, 'unsupported-file-mode')
                    continue
                if not path.lower().endswith(SUPPORTED_SUFFIXES):
                    _skip(skipped, budget, path, 'unsupported-file-type')
                    continue
                if type(item.get('size')) is not int or not 0 <= item['size'] <= MAX_FILE_BYTES:
                    _skip(skipped, budget, path, 'file-size')
                    continue
                if len(documents) >= MAX_FILES:
                    reasons.append('files')
                    _skip(skipped, budget, path, 'file-limit')
                    continue
                blob_sha = item.get('sha')
                if not isinstance(blob_sha, str) or not SHA.fullmatch(blob_sha):
                    raise CaptureError('The repository blob could not be pinned.')
                _, raw, _ = budget.get(base + '/git/blobs/' + blob_sha, byte_limit=2 * MAX_FILE_BYTES)
                blob = _json(raw)
                try:
                    if blob.get('sha') != blob_sha or blob.get('encoding') != 'base64':
                        raise ValueError()
                    encoded = blob['content']
                    if not isinstance(encoded, str) or len(encoded) > 2 * MAX_FILE_BYTES:
                        raise ValueError()
                    body = base64.b64decode(''.join(encoded.split()), validate=True)
                    if len(body) != item['size'] or hashlib.sha1(b'blob ' + str(len(body)).encode() + b'\0' + body).hexdigest() != blob_sha:
                        raise ValueError()
                except (KeyError, ValueError, TypeError, binascii.Error):
                    raise CaptureError('The repository blob does not match the pinned tree.') from None
                document = _document(path, body, 'text/plain', budget)
                if document is None:
                    _skip(skipped, budget, path, 'unsupported-text-or-size')
                else:
                    documents.append(document)
    except _Limit as exc:
        reasons.append(exc.reason)
    return {'documents': documents, 'source': source, 'skipped': skipped,
            'coverage': {'complete': not reasons and not budget.incomplete_skips,
                         'scope': 'requested-paths', 'reasons': sorted(set(reasons)),
                         'requests': budget.requests, 'network_bytes': budget.network_bytes,
                         'document_bytes': budget.document_bytes, 'files_considered': budget.considered,
                         'files_captured': len(documents), 'extractor': 'terminology-text-v1',
                         'skipped_count': budget.skipped_count,
                         'skipped_report_truncated': budget.skipped_count > len(skipped),
                         'limits': {'requests': MAX_REQUESTS, 'network_bytes': MAX_BYTES,
                                    'document_bytes': MAX_BYTES, 'files': MAX_FILES,
                                    'file_bytes': MAX_FILE_BYTES, 'seconds': MAX_SECONDS}}}
