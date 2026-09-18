"""Private durable workflow state. Never included in a publication profile."""
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import time
import uuid


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'))


def digest(value):
    return hashlib.sha256(value if isinstance(value, bytes) else canonical(value).encode()).hexdigest()


def identity(prefix):
    return prefix + '-' + uuid.uuid4().hex


def host_json(path, private=False):
    """Read one trusted descriptor; configuration cannot be swapped after permission checks."""
    with Path(path).open() as handle:
        info=os.fstat(handle.fileno())
        if info.st_uid not in (0,os.geteuid()) or info.st_mode & (0o077 if private else 0o022):
            raise ValueError('Host configuration ownership or permissions are unsafe')
        return json.load(handle)


class Conflict(ValueError):
    pass


class Store:
    def __init__(self, root, path=None):
        self.root = Path(root)
        self.path = Path(path or os.environ.get('KNOWLEDGE_HUB_STATE', self.root / '.private/knowledge.sqlite3'))
        resolved=self.path.resolve()
        if resolved.is_relative_to(self.root.resolve()) and not resolved.is_relative_to((self.root/'.private').resolve()):
            raise ValueError('Workflow state inside the repository must remain in .private')
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        fd=os.open(self.path,os.O_CREAT|os.O_RDWR,0o600)
        os.close(fd)
        os.chmod(self.path,0o600)
        with self.connect() as db:
            db.executescript('''
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS objects(kind TEXT, id TEXT, revision INTEGER, data TEXT,
              updated REAL, PRIMARY KEY(kind,id));
            CREATE TABLE IF NOT EXISTS history(kind TEXT,id TEXT,revision INTEGER,data TEXT,at REAL,
              PRIMARY KEY(kind,id,revision));
            CREATE TABLE IF NOT EXISTS blobs(hash TEXT PRIMARY KEY,body BLOB NOT NULL);
            CREATE TABLE IF NOT EXISTS evidence(id TEXT PRIMARY KEY,source TEXT,hash TEXT,text_hash TEXT,
              text TEXT,metadata TEXT,captured REAL);
            CREATE TABLE IF NOT EXISTS discoveries(evidence TEXT,origin TEXT,at REAL,
              PRIMARY KEY(evidence,origin));
            CREATE TABLE IF NOT EXISTS heads(source TEXT PRIMARY KEY,evidence TEXT);
            CREATE TABLE IF NOT EXISTS observations(id INTEGER PRIMARY KEY AUTOINCREMENT,source TEXT,evidence TEXT,origin TEXT,at REAL);
            CREATE INDEX IF NOT EXISTS source_observations ON observations(source,id);
            CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY,kind TEXT,key TEXT,payload TEXT,
              priority INTEGER,state TEXT,attempts INTEGER DEFAULT 0,available REAL,lease REAL,
              owner TEXT,error TEXT,created REAL,UNIQUE(kind,key));
            CREATE INDEX IF NOT EXISTS ready_jobs ON jobs(state,available,priority);
            CREATE INDEX IF NOT EXISTS source_evidence ON evidence(source,captured);
            ''')
        os.chmod(self.path, 0o600)

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=30)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA busy_timeout=30000')
        try:
            with db:
                yield db
        finally:
            db.close()

    def get(self, kind, key, db=None):
        if db is None:
            with self.connect() as conn:
                return self.get(kind, key, conn)
        row = db.execute('SELECT data,revision FROM objects WHERE kind=? AND id=?', (kind, key)).fetchone()
        if not row:
            raise KeyError('Record not found')
        return {**json.loads(row['data']), 'id': key, 'revision': row['revision']}

    def list(self, kind):
        with self.connect() as db:
            return [dict(json.loads(r['data']), id=r['id'], revision=r['revision']) for r in
                    db.execute('SELECT * FROM objects WHERE kind=? ORDER BY updated DESC', (kind,))]

    def put(self, kind, data, expected=None, db=None):
        if db is None:
            with self.connect() as conn:
                conn.execute('BEGIN IMMEDIATE')
                return self.put(kind, data, expected, conn)
        item = dict(data)
        key = item.pop('id', None) or identity(kind)
        item.pop('revision', None)
        row = db.execute('SELECT revision FROM objects WHERE kind=? AND id=?', (kind, key)).fetchone()
        previous = row[0] if row else 0
        if expected is not None and expected != previous:
            raise Conflict('Record changed; reload before editing')
        revision = previous + 1
        body, now = canonical(item), time.time()
        from ingest_ops import quarantine_payload
        quarantine_payload(body.encode())
        db.execute('INSERT OR REPLACE INTO objects VALUES(?,?,?,?,?)', (kind, key, revision, body, now))
        db.execute('INSERT INTO history VALUES(?,?,?,?,?)', (kind, key, revision, body, now))
        return dict(item, id=key, revision=revision)

    def capture(self, source, raw, text, metadata, origin, db=None):
        from ingest_ops import quarantine_payload
        quarantine_payload(raw)
        quarantine_payload(canonical(metadata).encode())
        quarantine_payload(text.encode())
        if db is None:
            with self.connect() as conn:
                conn.execute('BEGIN IMMEDIATE')
                return self.capture(source, raw, text, metadata, origin, conn)
        content_hash, text_hash = digest(raw), digest(text)
        key = digest([source, content_hash, metadata])
        head = db.execute('SELECT e.text_hash,e.id,e.metadata FROM heads h JOIN evidence e ON e.id=h.evidence WHERE h.source=?', (source,)).fetchone()
        semantic_keys=('classification','space','repository_revision','state','merged_at')
        changed = (not head or head[0] != text_hash or
                   any(json.loads(head['metadata']).get(k)!=metadata.get(k) for k in semantic_keys))
        db.execute('INSERT OR IGNORE INTO blobs VALUES(?,?)', (content_hash, raw))
        db.execute('INSERT OR IGNORE INTO evidence VALUES(?,?,?,?,?,?,?)',
                   (key, source, content_hash, text_hash, text, canonical(metadata), time.time()))
        db.execute('INSERT OR IGNORE INTO discoveries VALUES(?,?,?)', (key, origin, time.time()))
        if not head or head['id']!=key:
            db.execute('INSERT INTO observations(source,evidence,origin,at) VALUES(?,?,?,?)',(source,key,origin,time.time()))
        db.execute('INSERT OR REPLACE INTO heads VALUES(?,?)', (source, key))
        return key, changed

    def evidence(self, key):
        with self.connect() as db:
            row = db.execute('SELECT * FROM evidence WHERE id=?', (key,)).fetchone()
            if not row:
                raise KeyError('Evidence not found')
            item = dict(row)
            item['metadata'] = json.loads(item['metadata'])
            observation=db.execute('SELECT id,at FROM observations WHERE source=? AND evidence=? ORDER BY id DESC LIMIT 1',(item['source'],key)).fetchone()
            item['observed_revision']=observation['id'] if observation else None
            item['last_captured']=observation['at'] if observation else item['captured']
            item['origins'] = [r[0] for r in db.execute('SELECT origin FROM discoveries WHERE evidence=?', (key,))]
            return item

    def search(self, query='', origin=None, limit=100):
        with self.connect() as db:
            rows = db.execute('''SELECT DISTINCT e.id FROM evidence e JOIN heads h ON h.evidence=e.id
                LEFT JOIN discoveries d ON d.evidence=e.id WHERE e.text LIKE ?
                AND (? IS NULL OR d.origin=?) ORDER BY e.captured DESC LIMIT ?''',
                ('%' + query[:300] + '%', origin, origin, limit)).fetchall()
        return [self.evidence(r[0]) for r in rows]

    def current(self, evidence):
        with self.connect() as db:
            for e in evidence:
                head=db.execute('SELECT evidence FROM heads WHERE source=?',(e['source'],)).fetchone()
                revision=db.execute('SELECT MAX(id) FROM observations WHERE source=?',(e['source'],)).fetchone()[0]
                if not head or head[0]!=e['id'] or e.get('observed_revision',revision)!=revision: return False
            return True

    def enqueue(self, kind, key, payload, priority=50, db=None):
        if db is None:
            with self.connect() as conn:
                return self.enqueue(kind, key, payload, priority, conn)
        job = identity('job')
        db.execute("INSERT OR IGNORE INTO jobs(id,kind,key,payload,priority,state,available,created) VALUES(?,?,?,?,?,'queued',?,?)",
                   (job, kind, key, canonical(payload), priority, time.time(), time.time()))
        return db.execute('SELECT id FROM jobs WHERE kind=? AND key=?', (kind, key)).fetchone()[0]

    def claim(self, owner, lease=1800):
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            now = time.time()
            row = db.execute("SELECT * FROM jobs WHERE (state='queued' AND available<=?) OR (state='running' AND lease<?) ORDER BY priority,created LIMIT 1", (now, now)).fetchone()
            if not row:
                return None
            db.execute("UPDATE jobs SET state='running',owner=?,lease=?,attempts=attempts+1 WHERE id=?", (owner, now+lease, row['id']))
            return dict(row, payload=json.loads(row['payload']), owner=owner)

    def finish(self, job, error=None, delay=60):
        with self.connect() as db:
            db.execute('UPDATE jobs SET state=?,error=?,available=?,lease=NULL WHERE id=? AND owner=?',
                       ('queued' if error else 'done', error, time.time()+delay, job['id'], job['owner']))

    def jobs(self):
        with self.connect() as db:
            return [dict(r) for r in db.execute('SELECT id,kind,state,attempts,error,available,created FROM jobs ORDER BY created DESC LIMIT 100')]

    def backup(self, destination):
        target = Path(destination)
        if target.resolve().is_relative_to(self.root.resolve()) and not target.resolve().is_relative_to((self.root/'.private').resolve()):
            raise ValueError('Backups must remain private, outside publication paths')
        target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        fd=os.open(target,os.O_CREAT|os.O_RDWR,0o600); os.close(fd); os.chmod(target,0o600)
        with self.connect() as db, sqlite3.connect(target) as backup:
            db.backup(backup)
        os.chmod(target, 0o600)
