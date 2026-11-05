"""Private terminology transport and bounded, principal-owned scanner jobs.

The Wiki can submit a proposal and relay a browser signature. It never owns the
Human publication key or selects the authority service's trust configuration.
Source capture and model output are untrusted inputs to the separate analyzer.
A job retains only a bounded report; it cannot publish or change source files.
"""
from contextlib import contextmanager
import base64
import binascii
import http.client
import json
import os
from pathlib import Path
import re
import socket
import sqlite3
import stat
import threading
import time
import uuid

from ask_common import AskError

SOCKET_ENV = 'TRANSPARA_TERMINOLOGY_SOCKET'
MAX_RESPONSE = 1024 * 1024
MAX_SERVICE_RESPONSE = 2 * 1024 * 1024
MAX_REQUEST = 18 * 1024 * 1024
MAX_REPORTS = 100
MAX_REPORT_BYTES = 32 * 1024 * 1024
RETENTION = 7 * 24 * 60 * 60
JOB_SECONDS = 180
JOB_ID = re.compile(r'[a-f0-9]{32}')


def configured():
    return bool(os.environ.get(SOCKET_ENV))


class UnixConnection(http.client.HTTPConnection):
    """HTTP framing over one fixed Unix socket, with no TCP fallback."""
    def __init__(self, path, timeout):
        super().__init__('localhost', timeout=timeout)
        self.unix_path = path

    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self.sock.connect(self.unix_path)


def service(method, route, actor, payload=None, *, timeout=15):
    """Only reviewed routes reach the fixed, operator-selected local service.

    The socket's permissions authenticate this Wiki workload. The forwarded actor
    comes from the verified account, not an HTTP identity header supplied by the
    browser. A separate Human signature is still required for publication.
    """
    allowed = {'GET': {'/snapshot', '/state'}, 'POST': {
        '/proposals', '/prepare', '/approval/options', '/publish', '/analyze',
        '/enrollment/options', '/enrollment/finish'}}
    if route not in allowed.get(method, set()):
        raise AskError('Unknown terminology service operation.', 404)
    path = os.environ.get(SOCKET_ENV, '')
    if not path or not Path(path).is_absolute() or '..' in Path(path).parts:
        raise AskError('The terminology authority service is not configured.', 503)
    if not isinstance(actor, str) or not re.fullmatch(r'[A-Za-z0-9_.:@+-]{1,160}', actor):
        raise AskError('A verified author identity is required.', 401)
    body = json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode() if payload is not None else None
    if body is not None and len(body) > MAX_REQUEST:
        raise AskError('The terminology request exceeds its byte limit.', 422)
    connection = UnixConnection(path, min(max(timeout, 1), 60))
    timer = threading.Timer(min(max(timeout, 1), 60), lambda: _stop_connection(connection))
    timer.daemon = True
    timer.start()
    try:
        connection.request(method, route, body=body,
                           headers={'X-Term-Actor': actor, 'Content-Type': 'application/json'})
        connection._active_sock = connection.sock
        reply = connection.getresponse()
        raw = reply.read(MAX_SERVICE_RESPONSE + 1)
        if len(raw) > MAX_SERVICE_RESPONSE:
            raise AskError('The terminology report exceeds its byte limit.', 502)
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError()
        if reply.status >= 400:
            # Never relay an internal path, exception, or source excerpt from a
            # private service error. Its status remains useful to the browser.
            status = reply.status if reply.status in (400, 401, 403, 404, 409, 422, 429, 503) else 502
            raise AskError({403: 'This account has no enrolled publication key.',
                            409: 'The dictionary or approval changed. Refresh and review again.',
                            429: 'The terminology service is busy. Try again shortly.'}.get(
                                status, 'The terminology operation was refused or is unavailable.'), status)
        return data
    except AskError:
        raise
    except (OSError, ValueError, http.client.HTTPException, UnicodeError):
        raise AskError('The terminology authority service is unavailable.', 503) from None
    finally:
        timer.cancel()
        connection.close()


def _stop_connection(connection):
    # An absolute deadline also stops a peer that trickles headers or body bytes
    # forever without reaching the socket's inactivity timeout.
    active = connection.sock or getattr(connection, '_active_sock', None)
    if active is not None:
        try:
            active.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        connection.close()


def rewrite_model(documents, actor):
    """Make at most one call through the existing fixed shared-provider path.

    The author model is host configuration. Neither the source nor the request
    can choose a provider, executable, credentials, or prompt extension. The
    separate analyzer checks the returned draft and never grants conformance.
    """
    from knowledge_store import host_json
    import ask
    from urllib.parse import urlsplit
    # Python is report-only in this release. Never send executable source to a
    # prose transformer, even when it contains comments and docstrings. Preserve
    # those files exactly when reconstructing a mixed-source draft below.
    prose = [document for document in documents
             if not urlsplit(document['label']).path.lower().endswith('.py')]
    selected = os.environ.get('KNOWLEDGE_HUB_REVIEW_CONFIG')
    if not selected or not prose:
        return None
    if sum(len(d['text'].encode()) for d in documents) > 64 * 1024:
        return None
    spec = host_json(selected).get('author')
    if not isinstance(spec, dict) or set(spec) - {'provider', 'model', 'effort'} or not all(
            isinstance(spec.get(k), str) and spec[k] for k in ('provider', 'model')):
        raise AskError('The fixed rewrite model configuration is unavailable.', 503)
    payload = {'question': 'Prepare a technical-English rewrite draft. Preserve meaning and all protected literals. Return only the requested document JSON.',
               'space': 'workflow', **spec, 'stage': 'terminology-rewrite',
               'context': [{'documents': [{'label': d['label'], 'text': d['text']} for d in prose]}],
               'timeout': 52}
    with ask.admission('terminology:' + actor, spec['provider']):
        # ask.service adds eight seconds to its SSH child timeout, so 52 bounds
        # this single call at 60 seconds including connection overhead.
        result = ask.service('/complete', payload, timeout=52)
    if len(json.dumps(result).encode()) > 128 * 1024:
        raise AskError('The rewrite draft exceeds its output limit.', 422)
    if (not isinstance(result, dict) or set(result) != {'documents'}
            or not isinstance(result['documents'], list) or len(result['documents']) != len(prose)
            or any(not isinstance(item, dict) or set(item) != {'label', 'text'}
                   or not isinstance(item['text'], str) for item in result['documents'])
            or [item['label'] for item in result['documents']] != [item['label'] for item in prose]):
        raise AskError('The rewrite model did not preserve the selected document identities.', 422)
    transformed = {item['label']: item for item in result['documents']}
    result = {'documents': [transformed.get(document['label'],
              {'label': document['label'], 'text': document['text']}) for document in documents]}
    if len(json.dumps(result).encode()) > 128 * 1024:
        raise AskError('The combined rewrite draft exceeds its output limit.', 422)
    return result


class Jobs:
    """A small durable queue shared across request processes.

    SQLite transactions admit at most eight unfinished jobs, one per principal,
    and two running jobs. Leases recover an interrupted process without silently
    presenting a partial report as complete. Workers are started only by a
    scanner request or status read; importing this module starts no process.
    """
    def __init__(self, root, *, path=None, capture=None, backend=None, model=None, start=True):
        self.root = Path(root)
        self.path = Path(path or os.environ.get('TRANSPARA_TERMINOLOGY_JOBS', self.root / '.private/terminology-jobs.sqlite3'))
        absolute = self.path.absolute()
        root = self.root.resolve()
        if absolute.is_relative_to(root) and not absolute.is_relative_to(root / '.private'):
            raise AskError('Scanner state must remain outside published content.', 503)
        if any(p.is_symlink() for p in (absolute, *absolute.parents)):
            raise AskError('Scanner state cannot use symlinks.', 503)
        absolute.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        fd = os.open(absolute, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600)
        try:
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode) or info.st_uid != os.geteuid() or info.st_mode & 0o077:
                raise AskError('Scanner state must be a private owned regular file.', 503)
        finally:
            os.close(fd)
        self.path = absolute
        self.capture = capture
        self.backend = backend or service
        self.model = model or rewrite_model
        self.start = start
        with self.connect() as db:
            db.executescript('''PRAGMA journal_mode=WAL;
              PRAGMA max_page_count=16384;
              PRAGMA wal_autocheckpoint=128;
              PRAGMA journal_size_limit=1048576;
              CREATE TABLE IF NOT EXISTS term_jobs(
                id TEXT PRIMARY KEY,actor TEXT NOT NULL,state TEXT NOT NULL,
                request TEXT NOT NULL,report TEXT,error TEXT,created REAL NOT NULL,
                updated REAL NOT NULL,lease REAL,cancelled INTEGER NOT NULL DEFAULT 0);
              CREATE INDEX IF NOT EXISTS term_job_states ON term_jobs(state,created);''')

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=5)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def cleanup(self, db):
        now = time.time()
        db.execute("UPDATE term_jobs SET state='failed',error='The scanner process stopped before completion.',updated=?,lease=NULL WHERE state='running' AND lease<?", (now, now))
        db.execute("DELETE FROM term_jobs WHERE state NOT IN ('queued','running') AND updated<?", (now - RETENTION,))
        # Evict oldest finished reports to cap retained content independently of
        # age. Active input records are small and included in the queue bound.
        while True:
            count, size = db.execute("SELECT COUNT(*),COALESCE(SUM(length(CAST(report AS BLOB))),0) FROM term_jobs WHERE state NOT IN ('queued','running')").fetchone()
            if count <= MAX_REPORTS and size <= MAX_REPORT_BYTES:
                break
            db.execute("DELETE FROM term_jobs WHERE id=(SELECT id FROM term_jobs WHERE state NOT IN ('queued','running') ORDER BY updated,id LIMIT 1)")

    def submit(self, actor, request):
        if not isinstance(request, dict) or set(request) - {'source', 'rewrite'} or 'source' not in request or type(request.get('rewrite', False)) is not bool:
            raise AskError('Provide a scanner source and report or rewrite selection.', 422)
        source = request['source']
        if not isinstance(source, dict) or source.get('type') not in ('url', 'repo') or not isinstance(source.get('url'), str):
            raise AskError('Provide a repository or HTTPS URL.', 422)
        if len(json.dumps(request).encode()) > 16000:
            raise AskError('The scanner request exceeds its input limit.', 422)
        # Validate the target before saving it or opening any socket. Capture
        # repeats validation in the worker to preserve the network boundary.
        from terminology_sources import validate_request
        try:
            source = validate_request(source)
        except ValueError as exc:
            raise AskError(str(exc), 422) from None
        request = {**request, 'source': source}
        key = uuid.uuid4().hex
        now = time.time()
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            self.cleanup(db)
            if db.execute("SELECT 1 FROM term_jobs WHERE actor=? AND state IN ('queued','running')", (actor,)).fetchone():
                raise AskError('A scanner job is already active for this account.', 429)
            if db.execute("SELECT COUNT(*) FROM term_jobs WHERE state IN ('queued','running')").fetchone()[0] >= 8:
                raise AskError('The scanner queue is full. Try again shortly.', 429)
            db.execute('INSERT INTO term_jobs(id,actor,state,request,created,updated) VALUES(?,?,?,?,?,?)',
                       (key, actor, 'queued', json.dumps(request), now, now))
        if self.start:
            self.kick()
        return self.get(actor, key)

    def get(self, actor, key):
        if not isinstance(key, str) or not JOB_ID.fullmatch(key):
            raise AskError('Scanner job not found.', 404)
        with self.connect() as db:
            self.cleanup(db)
            row = db.execute('SELECT * FROM term_jobs WHERE id=? AND actor=?', (key, actor)).fetchone()
        if not row:
            raise AskError('Scanner job not found.', 404)
        result = {k: row[k] for k in ('id', 'state', 'created', 'updated', 'error')}
        result['request'] = json.loads(row['request'])
        if row['report']:
            result['report'] = json.loads(row['report'])
        return result

    def latest(self, actor):
        """Expose only the caller's newest job identity for refresh recovery."""
        with self.connect() as db:
            self.cleanup(db)
            row = db.execute('SELECT id,state FROM term_jobs WHERE actor=? ORDER BY created DESC,id DESC LIMIT 1', (actor,)).fetchone()
        return dict(row) if row else None

    def cancel(self, actor, key):
        self.get(actor, key)
        with self.connect() as db:
            db.execute("UPDATE term_jobs SET cancelled=1,state=CASE WHEN state='queued' THEN 'cancelled' ELSE state END,updated=? WHERE id=? AND actor=? AND state IN ('queued','running')", (time.time(), key, actor))
        return self.get(actor, key)

    def cancelled(self, key):
        with self.connect() as db:
            row = db.execute('SELECT cancelled,state,lease FROM term_jobs WHERE id=?', (key,)).fetchone()
        return not row or bool(row['cancelled']) or row['state'] != 'running' or row['lease'] < time.time()

    def claim(self):
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            self.cleanup(db)
            if db.execute("SELECT COUNT(*) FROM term_jobs WHERE state='running'").fetchone()[0] >= 2:
                return None
            row = db.execute("SELECT * FROM term_jobs WHERE state='queued' ORDER BY created,id LIMIT 1").fetchone()
            if not row:
                return None
            db.execute("UPDATE term_jobs SET state='running',lease=?,updated=? WHERE id=?", (time.time() + JOB_SECONDS, time.time(), row['id']))
            return dict(row)

    def run_one(self):
        job = self.claim()
        if not job:
            return False
        key, actor = job['id'], job['actor']
        report = None
        state, error = 'complete', None
        try:
            request = json.loads(job['request'])
            if self.capture is None:
                from terminology_sources import capture
            else:
                capture = self.capture
            captured = capture(request['source'], cancelled=lambda: self.cancelled(key))
            if self.cancelled(key):
                raise InterruptedError()
            documents = captured['documents']
            # Source text is quarantined before it reaches a model, authority
            # service or retained report. This is not a secret-scanner bypass.
            from ingest_ops import quarantine_payload
            for document in documents:
                quarantine_payload(document['text'].encode())
            payload = {'documents': documents, 'rewrite': False}
            report = self.backend('POST', '/analyze', actor, payload, timeout=20) if documents else {
                'conformance': 'not_assessed', 'documents': [],
                'limitations': ['No supported text was captured; no writing assessment was made.']}
            if request.get('rewrite') and documents and not self.cancelled(key):
                try:
                    draft = self.model(documents, actor)
                    if self.cancelled(key):
                        raise InterruptedError()
                    payload.update(rewrite=True)
                    if draft is not None:
                        payload['draft'] = draft
                    report = self.backend('POST', '/analyze', actor, payload, timeout=20)
                except InterruptedError:
                    raise
                except Exception:
                    # A missing/refused model must not discard a completed
                    # diagnostic report or turn it into a successful rewrite.
                    report['rewrite'] = {'status': 'unavailable',
                        'reason': 'The rewrite model is unavailable or its draft was refused. The original report is retained.'}
            report = {**report, 'source': captured['source'], 'coverage': captured['coverage'], 'skipped': captured.get('skipped', [])}
            encoded = json.dumps(report, ensure_ascii=False)
            if len(encoded.encode()) > MAX_RESPONSE:
                raise AskError('The retained report exceeds 1 MiB. Narrow the path selection.', 422)
            quarantine_payload(encoded.encode())
            if self.cancelled(key):
                raise InterruptedError()
        except InterruptedError:
            state, error, report = 'cancelled', None, None
        except Exception:
            state, error, report = 'failed', 'The scan could not complete. Check source access, limits, and service configuration; narrow the selection and retry.', None
        with self.connect() as db:
            # A cancelled or expired lease must never be revived by a late
            # network/model response. No partial result is published as complete.
            row = db.execute('SELECT cancelled,state,lease FROM term_jobs WHERE id=?', (key,)).fetchone()
            if row and row['state'] == 'running':
                if row['cancelled'] or row['lease'] < time.time():
                    state, error, report = 'cancelled' if row['cancelled'] else 'failed', 'The job stopped before completion.', None
                db.execute('UPDATE term_jobs SET state=?,report=?,error=?,updated=?,lease=NULL WHERE id=?',
                           (state, json.dumps(report, ensure_ascii=False) if report is not None else None, error, time.time(), key))
                self.cleanup(db)
        return True

    def kick(self):
        # Every process may request workers; the DB limits actual concurrent work.
        # A nonblocking process-local lock bounds idle threads in this process.
        with _workers_lock:
            for _ in range(max(0, 2 - _workers.get(str(self.path), 0))):
                _workers[str(self.path)] = _workers.get(str(self.path), 0) + 1
                threading.Thread(target=self._work, daemon=True).start()

    def _work(self):
        try:
            while self.run_one():
                pass
        finally:
            with _workers_lock:
                _workers[str(self.path)] -= 1


_workers_lock = threading.Lock()
_workers = {}


def _public_bytes(value, maximum):
    """Accept only bounded canonical base64url public WebAuthn wire fields."""
    if not isinstance(value, str) or not value or len(value) > (maximum * 4 + 2) // 3 or not re.fullmatch(r'[A-Za-z0-9_-]+', value):
        raise AskError('Invalid publication credential.', 422)
    try:
        raw = base64.b64decode(value + '=' * (-len(value) % 4), altchars=b'-_', validate=True)
    except (ValueError, binascii.Error):
        raise AskError('Invalid publication credential.', 422) from None
    if not raw or len(raw) > maximum or base64.urlsafe_b64encode(raw).decode().rstrip('=') != value:
        raise AskError('Invalid publication credential.', 422)
    return raw


def validate_public_proof(name, payload):
    """Validate a public cryptographic envelope without treating it as prose.

    Browser signatures and attestations are intentionally high-entropy public
    bytes. Only these exact bounded fields bypass the prose secret classifier;
    no arbitrary metadata, source text, token, key path, or trust setting can
    travel in the exception. The authority service still verifies the ceremony,
    exact origin/challenge, Human enrollment and signatures before any effect.
    """
    from urllib.parse import urlsplit
    fields = {'credential', 'stage_id'} if name == 'publish' else {'credential'}
    if not isinstance(payload, dict) or set(payload) != fields:
        raise AskError('Invalid publication credential fields.', 422)
    if name == 'publish' and (not isinstance(payload['stage_id'], str) or not JOB_ID.fullmatch(payload['stage_id'])):
        raise AskError('Invalid publication stage.', 422)
    credential = payload['credential']
    if (not isinstance(credential, dict) or set(credential) != {'id', 'rawId', 'type', 'response', 'clientExtensionResults'}
            or credential['type'] != 'public-key' or credential['id'] != credential['rawId']
            or credential['clientExtensionResults'] != {}):
        raise AskError('Invalid publication credential fields.', 422)
    _public_bytes(credential['rawId'], 1024)
    response = credential['response']
    expected = {'clientDataJSON', 'authenticatorData', 'signature', 'userHandle'} if name == 'publish' else {'clientDataJSON', 'attestationObject'}
    if not isinstance(response, dict) or set(response) != expected:
        raise AskError('Invalid publication response fields.', 422)
    try:
        data = json.loads(_public_bytes(response['clientDataJSON'], 4096))
        ceremony = 'webauthn.get' if name == 'publish' else 'webauthn.create'
        if (not isinstance(data, dict) or data.get('type') != ceremony
                or data.get('crossOrigin', False) is not False):
            raise ValueError()
        if len(_public_bytes(data['challenge'], 64)) != 32:
            raise ValueError()
        # WebAuthn permits extra client-data members, and Chromium sometimes
        # adds an interoperability notice. Those members remain ordinary
        # quarantined JSON; only the ceremony's random public challenge is
        # excluded from prose classification. The signed raw bytes are retained
        # unchanged for the authority's cryptographic verification.
        from ingest_ops import quarantine_payload, OpRefused
        try:
            quarantine_payload(json.dumps({key: value for key, value in data.items() if key != 'challenge'}).encode())
        except OpRefused:
            raise ValueError() from None
        origin = urlsplit(data['origin'])
        if (origin.scheme not in ('https', 'http') or not origin.hostname or origin.username
                or origin.password or origin.path or origin.query or origin.fragment
                or origin.scheme == 'http' and origin.hostname not in ('localhost', '127.0.0.1', '::1')):
            raise ValueError()
    except (ValueError, KeyError, TypeError, UnicodeError):
        raise AskError('Invalid publication client data.', 422) from None
    if name == 'publish':
        if len(_public_bytes(response['authenticatorData'], 1024)) < 37:
            raise AskError('Invalid publication authenticator data.', 422)
        _public_bytes(response['signature'], 1024)
        if response['userHandle'] is not None:
            _public_bytes(response['userHandle'], 64)
    else:
        _public_bytes(response['attestationObject'], 32768)


def handle(handler, root, actor):
    """Route only authenticated, CSRF-checked requests supplied by ingest_server."""
    from urllib.parse import parse_qs, urlsplit
    from ask_common import read_json
    route = urlsplit(handler.path)
    name = route.path.removeprefix('/api/terminology/')
    if handler.command == 'GET':
        if name in ('snapshot', 'state') and not route.query:
            result = service('GET', '/' + name, actor)
            if name == 'snapshot':
                result['browser_service'] = True
            else:
                jobs = Jobs(root)
                jobs.kick()
                result['scan_job'] = jobs.latest(actor)
            return 200, result
        if name == 'scan' and set(parse_qs(route.query)) == {'id'}:
            params = parse_qs(route.query)
            if len(params['id']) != 1:
                raise AskError('Scanner job not found.', 404)
            jobs = Jobs(root)
            jobs.kick()
            return 200, {'job': jobs.get(actor, params['id'][0])}
        raise AskError('Unknown terminology endpoint.', 404)
    if handler.command != 'POST' or route.query:
        raise AskError('Unknown terminology endpoint.', 405)
    payload = read_json(handler, limit=100000)
    if not isinstance(payload, dict):
        raise AskError('A JSON object is required.', 422)
    from ingest_ops import quarantine_payload
    if name in ('publish', 'enrollment/finish'):
        validate_public_proof(name, payload)
    else:
        quarantine_payload(json.dumps(payload).encode())
    if name == 'scan':
        return 202, {'job': Jobs(root).submit(actor, payload)}
    if name == 'scan/cancel':
        if set(payload) != {'id'}:
            raise AskError('Provide the scanner job ID.', 422)
        return 200, {'job': Jobs(root).cancel(actor, payload['id'])}
    if name in ('proposals', 'prepare', 'approval/options', 'publish', 'enrollment/options', 'enrollment/finish'):
        return 200, service('POST', '/' + name, actor, payload)
    raise AskError('Unknown terminology endpoint.', 404)
