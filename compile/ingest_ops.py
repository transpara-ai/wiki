#!/usr/bin/env python3
"""Per-ingestion operations core (Replace · Remove · shared gates).

Design packet: docs/superpowers/specs/2026-07-03-per-ingestion-ops-packet.md
(v0.5.0). Everything here is deny-by-default: authorization grants one
instance-matched, single-use artifact; quarantine refuses any payload or
persisted string the secret scanner flags; the ledger refuses to act when it
cannot audit; edge state that cannot be strictly parsed refuses operations
and fails the build; link rendering is live only on the proven-valid branch.
Refusal messages never echo secret bytes (rule ids only).
"""
import datetime
import hashlib
import html
import json
import os
import pathlib
import posixpath
import re
import signal
import subprocess
import sys
import tempfile
import urllib.parse
from html.parser import HTMLParser

import markdown

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import secret_scan  # noqa: E402

SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
EDGE_KEY_RE = re.compile(r"^[a-z0-9][a-z0-9-]*->[a-z0-9][a-z0-9-]*$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
SOURCE_VIEW_RE = re.compile(r"^source/[0-9a-f]{16}\.html$")
HTML_STEM_RE = re.compile(r"^([A-Za-z0-9_][A-Za-z0-9_-]*)\.html$")
SAFE_NAME_RE = re.compile(r"[^A-Za-z0-9._-]+")
URL_RE = re.compile(r"^https?://", re.I)
LIST_ITEM_RE = re.compile(r"^[ \t]+-\s+(.*)$")
FENCE_RE = re.compile(r"```.*?```", re.S)
RAW_HTML_RE = re.compile(r"</?[A-Za-z][^>]*>")

MAX_QUARANTINE_BYTES = secret_scan.MAX_BLOB_BYTES
MAX_AUTH_WINDOW_SECONDS = 24 * 3600
EDGE_STATES_VOCAB = ("valid", "cleanly-removed", "dangling-pending")
EDGE_ENTRY_KEYS = {"state", "since", "reason", "queued", "enqueued_at"}
BUILDER_PAGES = {"repos", "sources", "ingest", "civilization-arc",
                 "civilization_arc"}
# wiki/*.md-backed slugs the builder ALSO regenerates as a whole page, so they
# must never be retired as a tombstone (Remove would be reanimated on rebuild)
PROTECTED_SLUGS = {"index", "civilization-arc"}
AUTH_KEYS = {"df", "operation", "slug", "source_ref", "authority",
             "authorized_at", "expires_at", "reason", "engine_command",
             "engine_timeout_seconds"}
LEDGER_SHAPES = {
    "add": {"ts", "operation", "slug", "sources", "created", "rebuild"},
    "replace": {"ts", "operation", "slug", "superseded", "replacement",
                "authorized_by", "authorization_sha256", "engine", "result",
                "rebuild"},
    "remove": {"ts", "operation", "slug", "reason", "authorized_by",
               "authorization_sha256", "affected_edges", "repaired_edges",
               "result", "rebuild"},
    "register": {"ts", "operation", "slug", "source_path", "sha256",
                 "authorized_by", "authorization_sha256", "result",
                 "rebuild"},
}
# additive, org+section-aware add rows (DP-20260710 D4): LEDGER_SHAPES stays
# the REQUIRED key sets; these keys MAY additionally appear on new rows, so
# historical rows (written before the schema existed) still parse unchanged.
# When present, each must be a non-empty string.
LEDGER_OPTIONAL_KEYS = {
    "add": {"org", "section"},
}
# manifest rows (frozen raw/inbox/manifest.jsonl + manifest.d/ shards):
# exact key sets for NEW rows; historical rows are read for source_path only
MANIFEST_FILE_KEYS = {"ingested_at", "mode", "target_slug", "source_path",
                      "sha256", "original_name", "note", "supersedes"}
MANIFEST_URL_KEYS = {"ingested_at", "mode", "target_slug", "source_url",
                     "note", "supersedes"}


class OpRefused(Exception):
    """Any condition that must refuse the operation (fail closed)."""


class AuthRefused(OpRefused):
    """Authorization-gate refusal (HTTP 403 at the server layer)."""


def _no_dup(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError("duplicate key %r" % key)
        obj[key] = value
    return obj


def _parse_iso(value):
    dt = datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt


def _atomic_write_bytes(path, data):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".%s." % path.name)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        # mkstemp creates the temp file 0600; os.replace would install that over
        # the destination and make a previously group/world-readable tracked
        # file (wiki/*.md, PROVENANCE.md, raw uploads) unreadable to the static
        # server/builder. Preserve the destination's existing mode, or default a
        # NEW file to 0644 (the served-content convention) (CFAR ready-state).
        try:
            mode = os.stat(str(path)).st_mode & 0o777
        except FileNotFoundError:
            mode = 0o644
        os.chmod(tmp, mode)
        os.replace(tmp, str(path))
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _atomic_write_text(path, text):
    _atomic_write_bytes(path, text.encode("utf-8"))


def atomic_write_bytes(path, data):
    """Public atomicity primitive (packet §2.8): every durable file write in
    the ingest surface lands via temp-file + os.replace."""
    _atomic_write_bytes(path, data)


def atomic_write_text(path, text):
    _atomic_write_text(path, text)


# ------------------------------------------------------------ authorization

def load_authorization(path, now, *, operation, slug, source_ref):
    """Deny-by-default, per-ingestion, instance-scoped. Grant ONLY on the
    single fully-proven branch: exact key set, exact instance match
    (operation/slug/source_ref), valid <=24h window. Everything else refuses."""
    if operation not in ("replace", "remove", "register"):
        raise AuthRefused("unknown operation: %r" % operation)
    path = pathlib.Path(path)
    if not path.exists():
        raise AuthRefused("no ingest-authorization.json")
    try:
        raw = path.read_text()
    except Exception as exc:
        raise AuthRefused("authorization unreadable: %s" % type(exc).__name__)
    try:
        auth = json.loads(raw, object_pairs_hook=_no_dup)
    except (json.JSONDecodeError, ValueError):
        raise AuthRefused("authorization not valid JSON (or duplicate key)")
    if not isinstance(auth, dict):
        raise AuthRefused("authorization is not an object")
    if set(auth) != AUTH_KEYS:
        raise AuthRefused("authorization keys must be exactly %s"
                          % sorted(AUTH_KEYS))
    if auth["df"] != "ingest-authorization":
        raise AuthRefused("not a live ingest-authorization artifact")
    for key in ("operation", "slug", "source_ref", "authority",
                "authorized_at", "expires_at", "reason"):
        if not isinstance(auth[key], str):
            raise AuthRefused("field %s must be a string" % key)
    for key in ("operation", "slug", "authority", "authorized_at",
                "expires_at", "reason"):
        if not auth[key]:
            raise AuthRefused("field %s must be non-blank" % key)
    # authority/reason are persisted (PROVENANCE, ledger) — a newline would
    # inject extra provenance/audit lines while still passing a non-blank
    # check, so a persisted free-text field must be a single line (CFAR r5 P2-4).
    # Normalize surrounding whitespace and reject blank-after-strip so
    # `"authority": "   "` cannot be consumed into an unusable audit record
    # (CFAR r10 P3).
    for key in ("authority", "reason"):
        if "\n" in auth[key] or "\r" in auth[key]:
            raise AuthRefused("field %s must be a single line" % key)
        auth[key] = auth[key].strip()
        if not auth[key]:
            raise AuthRefused("field %s must be non-blank" % key)
    if auth["operation"] not in ("replace", "remove", "register"):
        raise AuthRefused("artifact operation must be replace, remove, "
                          "or register")
    if auth["operation"] == "remove" and auth["source_ref"] != "":
        raise AuthRefused("a remove artifact must carry source_ref \"\"")
    if auth["operation"] in ("replace", "register") and not auth["source_ref"]:
        raise AuthRefused("a %s artifact must name its source_ref"
                          % auth["operation"])
    # instance binding: this artifact authorizes ONE payload, not a class
    if auth["operation"] != operation:
        raise AuthRefused("artifact authorizes %r, not %r"
                          % (auth["operation"], operation))
    if auth["slug"] != slug:
        raise AuthRefused("artifact authorizes a different slug")
    if auth["source_ref"] != source_ref:
        raise AuthRefused("artifact authorizes a different source_ref")
    try:
        start = _parse_iso(auth["authorized_at"])
        end = _parse_iso(auth["expires_at"])
    except Exception:
        raise AuthRefused("authorized_at/expires_at not ISO-8601")
    now_dt = _parse_iso(now) if isinstance(now, str) else now
    if not (start <= now_dt < end):
        raise AuthRefused("outside validity window")
    if (end - start).total_seconds() > MAX_AUTH_WINDOW_SECONDS:
        raise AuthRefused("validity window exceeds 24 hours — "
                          "per-ingestion authority is in-the-moment")
    command = auth["engine_command"]
    if not isinstance(command, list):
        raise AuthRefused("engine_command must be a JSON array")
    for element in command:
        if not isinstance(element, str) or not element:
            raise AuthRefused("engine_command elements must be non-empty strings")
    timeout = auth["engine_timeout_seconds"]
    if isinstance(timeout, bool) or not isinstance(timeout, int) \
            or not (1 <= timeout <= 3600):
        raise AuthRefused("engine_timeout_seconds must be an int in [1, 3600]")
    return auth


def consume_authorization(path, auth, now):
    """Single-use enforcement + transaction-intent record: durable write #0.
    The artifact is atomically rewritten to a consumed tombstone whose df
    refuses reuse by the same gate that granted it."""
    path = pathlib.Path(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    tombstone = {
        "df": "ingest-authorization-consumed",
        "consumed_at": now if isinstance(now, str) else now.isoformat(),
        "operation": auth["operation"],
        "slug": auth["slug"],
        "source_ref": auth["source_ref"],
        "authorization_sha256": digest,
    }
    _atomic_write_text(path, json.dumps(tombstone, indent=2, sort_keys=True) + "\n")
    return digest


# ---------------------------------------------------------------- quarantine

def quarantine_payload(data):
    """Classify an in-memory payload by the scanner's input classes BEFORE it
    exists on disk. No runtime attestation path: oversized, binary, and
    secret-bearing payloads all refuse. Returns None when clean."""
    if len(data) > MAX_QUARANTINE_BYTES:
        raise OpRefused("payload exceeds %d bytes — unscannable at runtime; "
                        "refused" % MAX_QUARANTINE_BYTES)
    if b"\x00" in data:
        raise OpRefused("binary payload cannot be text-scanned; refused")
    # decode STRICTLY — a non-UTF-8 payload (binary without a NUL, e.g. an
    # image or Latin-1 bytes) is unscannable as text; decoding with replacement
    # would scan the mangled U+FFFD text and could accept it. Wiki sources are
    # UTF-8 markdown/text; anything else refuses (CFAR ready-state).
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        raise OpRefused("payload is not valid UTF-8 — binary/unscannable; "
                        "refused")
    findings = secret_scan.scan_text(text)
    if findings:
        rules = sorted({f.rule_id for f in findings})
        raise OpRefused("%d secret finding(s) in payload [%s]; refused"
                        % (len(findings), ", ".join(rules)))
    return None


def _git_no_fetch(root, *args):
    """git for attestation reads: lazy fetching disabled (mirrors the secret
    scanner's wrapper) so a missing blob refuses instead of doing network
    I/O or hanging under the write lock in air-gapped deployments."""
    env = dict(os.environ)
    env["GIT_NO_LAZY_FETCH"] = "1"
    return subprocess.run(["git", "-C", str(root), *args],
                          capture_output=True, env=env)


def quarantine_payload_attested(data, *, canonical_path, root, commit):
    """quarantine_payload with the ONE principled runtime attestation lane
    (wiki#52 path A): a register payload is a COMMITTED file, so its findings
    can attest against the commit-time allowlist at the exact identity the
    scanner itself uses — (rule_id, canonical_path, sha256(bytes),
    match_sha256, byte_offset). Every finding must carry a live clearance;
    any unmatched finding, an unreadable/invalid allowlist, or any
    size/binary/UTF-8 condition refuses (those stay absolute — attestation
    never applies to unscannable payloads). Add/Replace uploads keep the
    bare quarantine: uploaded bytes have no reviewed blob to attest."""
    if len(data) > MAX_QUARANTINE_BYTES:
        raise OpRefused("payload exceeds %d bytes — unscannable at runtime; "
                        "refused" % MAX_QUARANTINE_BYTES)
    if b"\x00" in data:
        raise OpRefused("binary payload cannot be text-scanned; refused")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        raise OpRefused("payload is not valid UTF-8 — binary/unscannable; "
                        "refused")
    findings = secret_scan.scan_text(text)
    if not findings:
        return None
    # the trust root is the COMMITTED allowlist (CFAR r3): a mutable
    # working-tree copy would let an unstaged local edit clear a finding —
    # read the immutable HEAD snapshot instead; anything short of a clean
    # read + strict parse refuses
    proc = _git_no_fetch(root, "show", "%s:compile/.secretsallow" % commit)
    if proc.returncode != 0:
        raise OpRefused("%d secret finding(s) and no committed allowlist "
                        "snapshot to attest against; refused" % len(findings))
    try:
        # decode INSIDE the refusal path: a non-UTF-8 committed allowlist
        # must refuse through the same controlled lane as an invalid one
        # (CFAR r5), never escape as a bare decode error
        allow = secret_scan.parse_allowlist(proc.stdout.decode("utf-8"))
    except Exception as exc:
        raise OpRefused("%d secret finding(s) and the committed allowlist "
                        "cannot vouch (invalid: %s); refused"
                        % (len(findings), type(exc).__name__))
    blob = hashlib.sha256(data).hexdigest()
    uncleared = [f for f in findings
                 if (f.rule_id, canonical_path, blob, f.match_sha256,
                     f.byte_offset) not in allow.fingerprints]
    if uncleared:
        rules = sorted({f.rule_id for f in uncleared})
        raise OpRefused("%d uncleared secret finding(s) in payload [%s]; "
                        "refused" % (len(uncleared), ", ".join(rules)))
    return None


def quarantine_fields(fields):
    """scan_text over EVERY string headed for the ledger, frontmatter,
    PROVENANCE, edge-states, manifest, logs, or the HTTP response. Findings
    are reported by field name + rule id only — never the matched bytes."""
    for key, value in fields.items():
        findings = secret_scan.scan_text(str(value or ""))
        if findings:
            rules = sorted({f.rule_id for f in findings})
            raise OpRefused("secret finding(s) in field %r [%s]; refused"
                            % (key, ", ".join(rules)))
    return None


# -------------------------------------------------------------------- ledger

def _require_row_str(row, keys, where):
    for key in keys:
        if not isinstance(row.get(key), str) or not row[key]:
            raise OpRefused("%s: %r must be a non-empty string" % (where, key))


def _validate_ledger_row(row, where="ledger row"):
    if not isinstance(row, dict):
        raise OpRefused("%s: not an object" % where)
    operation = row.get("operation")
    if operation not in LEDGER_SHAPES:
        raise OpRefused("%s: unknown operation" % where)
    required = LEDGER_SHAPES[operation]
    optional = LEDGER_OPTIONAL_KEYS.get(operation, set())
    missing = required - set(row)
    extra = set(row) - required - optional
    if missing or extra:
        raise OpRefused("%s: %s keys must be exactly %s (plus optional %s)"
                        % (where, operation, sorted(required), sorted(optional)))
    if not _valid_ts(row.get("ts")):
        raise OpRefused("%s: ts must be ISO-8601 with timezone" % where)
    _require_row_str(row, ("slug",), where)
    if row["rebuild"] not in ("ok", "failed"):
        raise OpRefused("%s: rebuild must be ok|failed" % where)
    # optional keys, when present, must be non-empty strings (additive schema)
    _require_row_str(row, tuple(k for k in sorted(optional) if k in row), where)
    if operation == "add":
        if not isinstance(row["sources"], list) or any(
                not isinstance(s, str) or not s for s in row["sources"]):
            raise OpRefused("%s: sources must be a list of non-empty strings" % where)
        if not isinstance(row["created"], bool):
            raise OpRefused("%s: created must be a boolean" % where)
        return
    _require_row_str(row, ("authorized_by",), where)
    if not isinstance(row["authorization_sha256"], str) \
            or not SHA256_RE.match(row["authorization_sha256"]):
        raise OpRefused("%s: authorization_sha256 must be hex sha256" % where)
    if operation == "replace":
        _require_row_str(row, ("superseded", "replacement"), where)
        if row["engine"] not in ("ok", "failed", "disabled"):
            raise OpRefused("%s: engine must be ok|failed|disabled" % where)
        if row["result"] not in ("completed", "stale"):
            raise OpRefused("%s: result must be completed|stale" % where)
        if (row["result"] == "completed") != (row["engine"] == "ok"):
            raise OpRefused("%s: result is completed iff engine ok" % where)
        return
    if operation == "register":
        _require_row_str(row, ("source_path",), where)
        if not isinstance(row["sha256"], str) \
                or not SHA256_RE.match(row["sha256"]):
            raise OpRefused("%s: sha256 must be hex sha256" % where)
        if row["result"] != "completed":
            raise OpRefused("%s: register result must be completed" % where)
        return
    _require_row_str(row, ("reason",), where)
    for key in ("affected_edges", "repaired_edges"):
        if not isinstance(row[key], list) or any(
                not isinstance(s, str) or not s for s in row[key]):
            raise OpRefused("%s: %s must be a list of non-empty strings"
                            % (where, key))
    if row["result"] != "completed":
        raise OpRefused("%s: remove result must be completed" % where)


def ledger_preflight(path):
    """Strict end-to-end parse AND appendability probe of the ledger — an
    unauditable surface takes no new actions, and the append happens LAST, so
    if it would fail (read-only file, wrong owner, unwritable dir) the whole
    operation must refuse BEFORE the first durable write, not orphan the audit
    after it (packet §2.9; CFAR ready-state). Absent file = valid empty."""
    path = pathlib.Path(path)
    if not path.exists():
        if path.parent.exists() and not os.access(str(path.parent), os.W_OK):
            raise OpRefused("ledger directory is not writable")
        return []
    # prove the existing ledger is appendable WITHOUT writing (append mode does
    # not truncate or modify content) — a PermissionError here refuses now
    try:
        with path.open("a"):
            pass
    except OSError as exc:
        raise OpRefused("ledger exists but is not appendable (%s)"
                        % type(exc).__name__)
    try:
        text = path.read_text()
    except Exception as exc:
        raise OpRefused("ledger unreadable: %s" % type(exc).__name__)
    rows = []
    for lineno, line in enumerate(text.splitlines(), 1):
        where = "ledger line %d" % lineno
        if not line.strip():
            raise OpRefused("%s: blank line — strict JSONL" % where)
        try:
            row = json.loads(line, object_pairs_hook=_no_dup)
        except (json.JSONDecodeError, ValueError):
            raise OpRefused("%s: not valid JSON (or duplicate key)" % where)
        _validate_ledger_row(row, where)
        rows.append(row)
    return rows


def append_ledger(path, row):
    """Append-last: one validated line, written only after every durable
    mutation of the operation succeeded."""
    _validate_ledger_row(row)
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # a preflight-valid ledger may lack a trailing newline (e.g. after a manual
    # repair); appending directly would merge two objects onto one line and
    # break the strict JSONL parse forever — insert the missing separator
    # first (CFAR r15).
    prefix = ""
    if path.exists():
        existing = path.read_bytes()
        if existing and not existing.endswith(b"\n"):
            prefix = "\n"
    with path.open("a") as f:
        f.write(prefix + json.dumps(row, sort_keys=True) + "\n")


# --------------------------------------------------------------- edge states

def _valid_ts(value):
    """ISO-8601 with explicit timezone — 'a string' is not a timestamp.
    Checks the raw parse: _parse_iso would normalize a naive value to UTC,
    which is exactly the leniency this validator exists to refuse."""
    if not isinstance(value, str) or not value:
        return False
    try:
        parsed = datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return False
    return parsed.tzinfo is not None


def _validate_edge_entry(key, entry):
    where = "edge-states entry %r" % key
    if not isinstance(entry, dict) or set(entry) != EDGE_ENTRY_KEYS:
        raise OpRefused("%s: keys must be exactly %s"
                        % (where, sorted(EDGE_ENTRY_KEYS)))
    if entry["state"] not in EDGE_STATES_VOCAB:
        raise OpRefused("%s: unknown state — fail closed" % where)
    if not _valid_ts(entry["since"]):
        raise OpRefused("%s: since must be ISO-8601 with timezone" % where)
    if not isinstance(entry["reason"], str) or not entry["reason"]:
        raise OpRefused("%s: reason must be a non-empty string" % where)
    if not isinstance(entry["queued"], bool):
        raise OpRefused("%s: queued must be a boolean" % where)
    if entry["queued"]:
        if not _valid_ts(entry["enqueued_at"]):
            raise OpRefused("%s: queued entries need ISO-8601 enqueued_at" % where)
    elif entry["enqueued_at"] is not None:
        raise OpRefused("%s: unqueued entries need enqueued_at null" % where)


def load_edge_states(path):
    """Strict-parse law: corrupt/duplicate/unreadable state REFUSES — it is
    never treated as empty. A missing file is the one valid empty form."""
    path = pathlib.Path(path)
    if not path.exists():
        return {}
    try:
        raw = path.read_text()
    except Exception as exc:
        raise OpRefused("edge-states unreadable: %s" % type(exc).__name__)
    try:
        doc = json.loads(raw, object_pairs_hook=_no_dup)
    except (json.JSONDecodeError, ValueError):
        raise OpRefused("edge-states not valid JSON (or duplicate key)")
    if not isinstance(doc, dict):
        raise OpRefused("edge-states is not an object")
    for key, entry in doc.items():
        if not EDGE_KEY_RE.match(key):
            raise OpRefused("edge-states key %r is not <slug>-><slug>" % key)
        _validate_edge_entry(key, entry)
    return doc


def write_edge_states(path, states):
    for key, entry in states.items():
        if not EDGE_KEY_RE.match(key):
            raise OpRefused("edge-states key %r is not <slug>-><slug>" % key)
        _validate_edge_entry(key, entry)
    _atomic_write_text(pathlib.Path(path),
                       json.dumps(states, indent=2, sort_keys=True) + "\n")


# ----------------------------------------------------------- link rendering

def link_state(source_slug, target_slug, meta, edge_states):
    """TOTAL decision function. live is the single proven branch; every other
    state — dangling, retired, unknown/future, missing — is non-live."""
    entry = edge_states.get("%s->%s" % (source_slug, target_slug))
    target = meta.get(target_slug)
    exists = target is not None or target_slug == "index"
    retired = bool(target and target.get("retired_on"))
    if entry is not None:
        state = entry.get("state")
        if state == "valid" and exists and not retired:
            return "live"
        if state == "cleanly-removed":
            return "plain"
        return "pending"
    if exists and not retired:
        return "live"
    if retired:
        return "pending"
    return "tbd"


def canonical_article_target(href, *, meta, repo_slugs=()):
    """Canonicalize a rendered href so no relative .html spelling dodges the
    gate. Returns (kind, target): article | page | unknown | external."""
    href = (href or "").strip()
    if not href:
        return ("external", "")
    # browsers treat backslash as a path separator, so `x\..\slug.html` and
    # `\slug.html` resolve like their slash forms — normalize before parsing so
    # neither dodges the gate nor is missed on Remove (CFAR r27)
    href = href.replace("\\", "/")
    try:
        parsed = urllib.parse.urlsplit(href)
    except ValueError:
        return ("unknown", href)
    if parsed.scheme or parsed.netloc:
        return ("external", "")
    path = urllib.parse.unquote(parsed.path)
    if not path or not path.lower().endswith(".html"):
        return ("external", "")
    # dot-segment normalization, clamped at the site root: ../slug.html,
    # x/../slug.html and /slug.html all canonicalize to slug.html
    norm = posixpath.normpath("/" + path).lstrip("/")
    if SOURCE_VIEW_RE.match(norm):
        return ("page", norm)
    if "/" in norm:
        return ("unknown", norm)
    m = HTML_STEM_RE.match(norm)
    if not m:
        return ("unknown", norm)
    stem = m.group(1)
    if stem in meta or stem == "index":
        return ("article", stem)
    if stem in BUILDER_PAGES:
        return ("page", stem)
    if stem.startswith("repo-") and stem[len("repo-"):] in set(repo_slugs):
        return ("page", stem)
    return ("unknown", stem)


# ------------------------------------------------------- article frontmatter

def _parse_article(raw):
    """Split into (fm_lines, tail) where tail starts at the closing fence and
    is kept byte-verbatim (body bytes untouched by frontmatter rewrites)."""
    if not raw.startswith("---"):
        raise OpRefused("article has no frontmatter")
    end = raw.find("\n---", 3)
    if end < 0:
        raise OpRefused("article has no frontmatter fence")
    fm_lines = raw[3:end].strip("\n").split("\n")
    return fm_lines, raw[end:]


def _assemble_article(fm_lines, tail):
    return "---\n" + "\n".join(fm_lines) + tail


def _strip_inline_comment(value):
    quote = ""
    escaped = False
    for i, ch in enumerate(value):
        if escaped:
            escaped = False
            continue
        if ch == "\\":
            escaped = True
            continue
        if quote:
            if ch == quote:
                quote = ""
            continue
        if ch in {"'", '"'}:
            quote = ch
            continue
        if ch == "#" and (i == 0 or value[i - 1].isspace()):
            return value[:i].rstrip()
    return value.strip()


def _clean_item(item):
    return _strip_inline_comment(item).strip().strip('"').strip("'")


def _key_line_index(fm_lines, key):
    pattern = re.compile(r"^%s:" % re.escape(key))
    for i, line in enumerate(fm_lines):
        if pattern.match(line):
            return i
    return -1


def _list_item_indexes(fm_lines, key):
    key_idx = _key_line_index(fm_lines, key)
    if key_idx < 0:
        return -1, []
    items = []
    for i in range(key_idx + 1, len(fm_lines)):
        if LIST_ITEM_RE.match(fm_lines[i]):
            items.append(i)
        elif re.match(r"^[A-Za-z_]", fm_lines[i]):
            break  # next top-level key ends the block
        # else: a standalone comment or blank line — the live fm_list keeps
        # scanning to the next key, so we must too, or a later `-` item is
        # silently dropped / orphaned on mutation (CFAR r3 P2-1)
    return key_idx, items


def _inline_list(line):
    """Parse `key: [a, b]` (the inline form the live fm_list accepts), or None
    if the value is not an inline list. A trailing `# comment` is stripped first
    so the ops parser stays aligned with the read/renderer fm_list — else Replace
    would refuse a UI-offered ref as "not referenced" (CFAR: Codex)."""
    value = _strip_inline_comment(line.split(":", 1)[1]).strip() if ":" in line else ""
    if value.startswith("[") and value.endswith("]"):
        return [x.strip().strip('"').strip("'")
                for x in value[1:-1].split(",") if x.strip()]
    return None


def fm_list_values(fm_lines, key):
    # match the live fm_list parser: accept BOTH the inline `key: [a, b]` form
    # and the block `-` form — reading only block rows silently returns [] for
    # a valid inline list, breaking the in-article and shared-source checks
    # (CFAR r2 P2-3)
    idx = _key_line_index(fm_lines, key)
    if idx < 0:
        return []
    inline = _inline_list(fm_lines[idx])
    if inline is not None:
        return [v for v in inline if v]
    _, items = _list_item_indexes(fm_lines, key)
    values = []
    for i in items:
        value = _clean_item(LIST_ITEM_RE.match(fm_lines[i]).group(1))
        if value:
            values.append(value)
    return values


def _normalize_list_to_block(fm_lines, key):
    """Rewrite an inline `key: [a, b]` list as block `-` rows so the block-form
    mutation helpers can move/remove items — otherwise a superseded ref left
    in an inline `sources` line stays load-bearing under the live parser."""
    idx = _key_line_index(fm_lines, key)
    if idx < 0:
        return fm_lines
    inline = _inline_list(fm_lines[idx])
    if inline is None:
        return fm_lines
    block = ["%s:" % key] + ["  - %s" % json.dumps(v) for v in inline if v]
    return fm_lines[:idx] + block + fm_lines[idx + 1:]


def fm_scalar(fm_lines, key):
    idx = _key_line_index(fm_lines, key)
    if idx < 0:
        return ""
    return fm_lines[idx].split(":", 1)[1].strip().strip('"')


def _remove_list_value(fm_lines, key, value):
    key_idx, items = _list_item_indexes(fm_lines, key)
    if key_idx < 0:
        return fm_lines
    drop = [i for i in items
            if _clean_item(LIST_ITEM_RE.match(fm_lines[i]).group(1)) == value]
    if not drop:
        return fm_lines
    keep = [line for i, line in enumerate(fm_lines) if i not in drop]
    if len(items) == len(drop):
        key_idx = _key_line_index(keep, key)
        keep.pop(key_idx)
    return keep


def _append_list_value(fm_lines, key, value):
    if value in fm_list_values(fm_lines, key):
        return fm_lines
    item = "  - %s" % json.dumps(value)
    key_idx, items = _list_item_indexes(fm_lines, key)
    if key_idx < 0:
        return fm_lines + ["%s:" % key, item]
    insert_at = (items[-1] if items else key_idx) + 1
    return fm_lines[:insert_at] + [item] + fm_lines[insert_at:]


def _set_scalar(fm_lines, key, value):
    line = "%s: %s" % (key, json.dumps(value))
    idx = _key_line_index(fm_lines, key)
    if idx >= 0:
        return fm_lines[:idx] + [line] + fm_lines[idx + 1:]
    return fm_lines + [line]


def _drop_scalar(fm_lines, key):
    idx = _key_line_index(fm_lines, key)
    if idx < 0:
        return fm_lines
    return fm_lines[:idx] + fm_lines[idx + 1:]


# -------------------------------------------------------------- shared bits

def _date_of(now):
    return (now if isinstance(now, str) else now.isoformat())[:10]


def _now_str(now):
    return now if isinstance(now, str) else now.isoformat()


def _safe_filename(name):
    name = pathlib.PurePath(name or "document.md").name
    cleaned = SAFE_NAME_RE.sub("-", name).strip(".-")
    return cleaned or "document.md"


def _append_provenance(root, line):
    path = root / "PROVENANCE.md"
    text = path.read_text() if path.exists() else "# Provenance\n"
    if not text.endswith("\n"):
        text += "\n"
    _atomic_write_text(path, text + line + "\n")


def _attempt_rebuild(root):
    """dist/ is derived state: a failed rebuild is recorded, not fatal — the
    15-minute refresh timer self-heals it. Locking is owned by the caller."""
    refresh = root / "compile" / "refresh.py"
    try:
        proc = subprocess.Popen(
            [sys.executable, str(refresh)], cwd=str(root),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            start_new_session=True)
        try:
            proc.communicate(timeout=240)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except Exception:
                pass
            proc.communicate()
            return False
        return proc.returncode == 0
    except Exception:
        return False


def _run_rebuild(root, rebuild_runner):
    if rebuild_runner is None:
        return "ok" if _attempt_rebuild(root) else "failed"
    try:
        return "ok" if rebuild_runner() else "failed"
    except Exception:
        return "failed"


# ------------------------------------------------------------------- engine

def _raw_html_outside_fences(text):
    return bool(RAW_HTML_RE.search(FENCE_RE.sub("", text)))


def run_engine(engine_command, timeout, job, cwd=None):
    """Authority-gated single-article synthesis. Output is the article BODY
    only; every violation of the output law discards the output (the caller
    keeps the deterministic honest-stale state). Runs with the operation root
    as cwd so the job's relative `raw/...` refs resolve regardless of where the
    server process was launched (CFAR r26)."""
    if engine_command == []:
        return ("disabled", None)
    try:
        proc = subprocess.Popen(
            list(engine_command), stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, start_new_session=True,
            cwd=str(cwd) if cwd is not None else None)
    except Exception:
        return ("failed", None)
    try:
        stdout, _stderr = proc.communicate(json.dumps(job), timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except Exception:
            pass
        proc.communicate()
        return ("failed", None)
    except Exception:
        return ("failed", None)
    if proc.returncode != 0:
        return ("failed", None)
    body = stdout or ""
    if not body.strip():
        return ("failed", None)
    if body.lstrip().startswith("---"):
        # an attempt to seize frontmatter authority — deterministic Layer 1
        # owns frontmatter exclusively (packet §2.6, CFADA rebuild-r2 B1)
        return ("failed", None)
    if _raw_html_outside_fences(body):
        return ("failed", None)
    try:
        quarantine_payload(body.encode("utf-8"))
    except OpRefused:
        return ("failed", None)
    if not body.endswith("\n"):
        body += "\n"
    return ("ok", body)


# ------------------------------------------------------------------ replace

def _replace_preflight(root, slug, source_ref):
    """Shared READ-ONLY preflight for replace and its consequence preview —
    one implementation, so the preview can never drift from the operation
    (fe-ux packet §2.3 parity-by-construction)."""
    if not SLUG_RE.match(slug):
        raise OpRefused("invalid article slug")
    article_path = root / "wiki" / ("%s.md" % slug)
    if not article_path.exists():
        raise OpRefused("unknown article slug")
    fm_lines, tail = _parse_article(article_path.read_text())
    if fm_scalar(fm_lines, "retired_on"):
        raise OpRefused("article is retired — replace refused")
    if URL_RE.match(source_ref):
        raise OpRefused("replace of an external URL source is not supported in v1")
    if not source_ref.startswith("raw/"):
        raise OpRefused("source_ref must be a local raw/ path")
    live_sources = fm_list_values(fm_lines, "sources")
    live_raw_docs = fm_list_values(fm_lines, "raw_documents")
    if source_ref not in live_sources and source_ref not in live_raw_docs:
        raise OpRefused("source_ref is not referenced by this article")
    for other in sorted((root / "wiki").glob("*.md")):
        if other.stem == slug:
            continue
        try:
            other_fm, _ = _parse_article(other.read_text())
        except OpRefused:
            continue
        if source_ref in fm_list_values(other_fm, "sources") \
                or source_ref in fm_list_values(other_fm, "raw_documents"):
            raise OpRefused("source_ref is shared by another article — "
                            "shared-source replace is refused in v1")
    return article_path, fm_lines, tail


def set_article_stale(root, slug, now):
    """R5/R7: stamp `stale_since` on an investigation article so the builder's
    reason-neutral "summary re-derivation pending" banner renders until a governed
    authoring pass clears it (via _drop_scalar, exactly as Replace does on
    engine-ok). A thin wrapper over _set_scalar reused by the ADD lane and
    Replace — no new op and no authorization contract (Q4), only the scalar stamp,
    run INSIDE the caller's wiki write lock."""
    root = pathlib.Path(root)
    article_path = root / "wiki" / ("%s.md" % slug)
    if not article_path.exists():
        raise OpRefused("unknown article slug")
    fm_lines, tail = _parse_article(article_path.read_text())
    fm_lines = _set_scalar(fm_lines, "stale_since", _now_str(now))
    _atomic_write_text(article_path, _assemble_article(fm_lines, tail))


def replace_source(root, *, slug, source_ref, data, filename, note, now,
                   rebuild_runner=None):
    root = pathlib.Path(root)
    # `now` is written verbatim into the ledger/edge-state timestamps, whose
    # strict validators require an explicit timezone — reject a naive `now`
    # BEFORE consuming auth or writing, else mutations land with no audit row
    # (CFAR r14). The auth window parser would otherwise silently accept it.
    now = _now_str(now)
    if not _valid_ts(now):
        raise OpRefused("now must be an ISO-8601 timestamp with a timezone")
    auth_path = root / "compile" / "ingest-authorization.json"
    auth = load_authorization(auth_path, now, operation="replace",
                              slug=slug, source_ref=source_ref)
    quarantine_fields({"slug": slug, "source_ref": source_ref, "note": note,
                       "filename": filename, "authorized_by": auth["authority"]})
    quarantine_payload(data)
    # an empty upload is clean to the scanner but would supersede the live
    # evidence source with nothing — refuse before consuming auth (Add skips
    # empty uploads; Replace must too) (CFAR r22)
    if not data:
        raise OpRefused("replacement upload is empty")

    # preflight — read-only; refusal leaves the tree byte-identical
    # (shared with preview_replace — parity by construction)
    article_path, fm_lines, tail = _replace_preflight(root, slug, source_ref)
    ledger_path = root / "compile" / "ingest-ledger.jsonl"
    ledger_preflight(ledger_path)
    # corrupt edge state refuses EVERY operation, not only Remove (§2.7
    # strict-parse law; CFADA rebuild-r4 B1) — the rebuild this operation
    # triggers would otherwise render from unverifiable state
    load_edge_states(root / "compile" / "edge-states.json")

    # compute the replacement's content-addressed path IN PREFLIGHT: if it
    # collides with source_ref (a same-day re-upload of identical content),
    # the swap would remove-then-re-add the same ref and leave the "superseded"
    # source live — breaking append-only supersession. Refuse before consuming
    # the authorization or writing anything (CFAR r10 P2).
    sha = hashlib.sha256(data).hexdigest()
    original = _safe_filename(filename)
    dst = (root / "raw" / "inbox" / _date_of(now) / slug /
           ("%s-%s%s" % (pathlib.Path(original).stem or "document", sha[:12],
                         pathlib.Path(original).suffix or ".md")))
    new_ref = str(dst.relative_to(root))
    if new_ref == source_ref:
        raise OpRefused("replacement resolves to the same raw path as "
                        "source_ref — upload distinct content or a distinct "
                        "filename to supersede it")

    # durable write #0: burn the single-use authorization (intent record)
    digest = consume_authorization(auth_path, auth, now)

    # deterministic swap (Layer 1): raw file, then frontmatter-only rewrite
    _atomic_write_bytes(dst, data)

    # canonicalize any inline-form lists to block form before mutating, so the
    # remove/move helpers cannot leave a superseded ref inline+live (CFAR r2 P2-3)
    for key in ("sources", "raw_documents", "superseded_sources",
                "superseded_raw_documents"):
        fm_lines = _normalize_list_to_block(fm_lines, key)
    for key in ("sources", "raw_documents"):
        if source_ref in fm_list_values(fm_lines, key):
            fm_lines = _remove_list_value(fm_lines, key, source_ref)
            fm_lines = _append_list_value(fm_lines, "superseded_%s" % key,
                                          source_ref)
    fm_lines = _append_list_value(fm_lines, "sources", new_ref)
    fm_lines = _append_list_value(fm_lines, "raw_documents", new_ref)
    fm_lines = _set_scalar(fm_lines, "stale_since", _now_str(now))
    _atomic_write_text(article_path, _assemble_article(fm_lines, tail))

    _append_provenance(root, "- %s replace: `%s` superseded by `%s` "
                       "(article `%s`, authorized by %s)"
                       % (_date_of(now), source_ref, new_ref, slug,
                          auth["authority"]))

    # engine boundary (Layer 2): body-only output, degrades to honest-stale
    job = {"operation": "replace", "slug": slug,
           "sources": fm_list_values(fm_lines, "sources"),
           "raw_documents": fm_list_values(fm_lines, "raw_documents")}
    engine, body = run_engine(auth["engine_command"],
                              auth["engine_timeout_seconds"], job, cwd=root)
    if engine == "ok":
        assembled_fm = _drop_scalar(fm_lines, "stale_since")
        _atomic_write_text(article_path,
                           "---\n" + "\n".join(assembled_fm) + "\n---\n\n" + body)

    rebuild = _run_rebuild(root, rebuild_runner)
    row = {"ts": _now_str(now), "operation": "replace", "slug": slug,
           "superseded": source_ref, "replacement": new_ref,
           "authorized_by": auth["authority"], "authorization_sha256": digest,
           "engine": engine,
           "result": "completed" if engine == "ok" else "stale",
           "rebuild": rebuild}
    append_ledger(ledger_path, row)
    return row


# ------------------------------------------------------------------- remove

def _board_field_matches(value, target_slug):
    # a board field may carry an inline comment and/or quotes — strip the
    # comment BEFORE the quotes so a quoted-then-commented scalar
    # (`"slug" # note`) is handled: stripping the leading quote first would
    # unbalance the value and hide the comment inside a phantom quote (CFAR
    # r6/r13). _strip_inline_comment respects balanced quotes.
    value = _strip_inline_comment(value)
    for field in value.split("|"):
        if field.strip().strip('"').strip("'") == target_slug:
            return True
    return False


def _raw_scalar(fm_lines, key):
    idx = _key_line_index(fm_lines, key)
    if idx < 0 or ":" not in fm_lines[idx]:
        return ""
    return fm_lines[idx].split(":", 1)[1].strip()  # NOT quote-stripped (CFAR r13)


def _references_via_board(fm_lines, target_slug):
    """True if index.md's board frontmatter references target_slug — the
    builder generates (and now gates) homepage board links from these keys, so
    a board-only reference is a real inbound edge to queue (CFAR r4/r6/r13)."""
    for key in ("board_narrative_link", "board_guardrail"):
        if _board_field_matches(_raw_scalar(fm_lines, key), target_slug):
            return True
    for key in ("board_pillars", "board_inheritance"):
        for item in fm_list_values(fm_lines, key):
            if _board_field_matches(item, target_slug):
                return True
    return False


class _AnchorHrefs(HTMLParser):
    """Extract real anchor targets (href / SVG xlink:href) from raw HTML in an
    article body. HTMLParser ignores prose, inline code, and non-link
    attributes (e.g. title="href=..."), so edge discovery matches what the
    renderer would actually link — no spurious queued edges (CFAR r17)."""

    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.hrefs = []

    def _collect(self, tag, attrs):
        # <a> and <area> (image map) are the browser-navigable href elements;
        # SVG anchors use xlink:href (CFAR r17/r18)
        if tag in ("a", "area"):
            for k, v in attrs:
                if k.lower() in ("href", "xlink:href") and v:
                    self.hrefs.append(v)

    def handle_starttag(self, tag, attrs):
        self._collect(tag, attrs)

    def handle_startendtag(self, tag, attrs):
        self._collect(tag, attrs)


def _raw_anchor_hrefs(body):
    parser = _AnchorHrefs()
    try:
        parser.feed(body)
        parser.close()
    except Exception:
        return []
    return parser.hrefs


# matches build_site's Markdown config so edge discovery sees exactly the
# anchors the renderer emits (extra = raw HTML + reference-style links)
_MD = markdown.Markdown(extensions=["extra", "sane_lists"])


def _render_markdown(body):
    _MD.reset()
    try:
        return _MD.convert(body)
    except Exception:
        return ""


def find_inbound_edges(root, target_slug):
    """Every source that links to the target — through any BODY form
    ([[wikilink]], markdown (slug.html) INCLUDING titled links, raw
    href="slug.html" any spelling) OR, for the homepage, through generated
    board frontmatter links. The homepage (index.md) is scanned because the
    builder renders its links with source_slug 'index' (CFAR r1 P2-4/P2-5,
    r4 P2)."""
    wikilink = re.compile(r"\[\[%s(?:\|[^\]]*)?\]\]" % re.escape(target_slug))
    meta_stub = {target_slug: {}}
    root = pathlib.Path(root)
    scan = [(root / "index.md", "index")]
    scan += [(p, p.stem) for p in sorted((root / "wiki").glob("*.md"))]
    sources = []
    for path, source_slug in scan:
        if source_slug == target_slug or not path.exists():
            continue
        raw = path.read_text()
        try:
            fm_lines, body = _parse_article(raw)
        except OpRefused:
            fm_lines, body = [], raw
        # build_site substitutes [[wikilinks]] BEFORE markdown, so scan the raw
        # body for those
        hit = bool(wikilink.search(body))
        if not hit and source_slug == "index":
            hit = _references_via_board(fm_lines, target_slug)
        if not hit:
            # markdown links (incl. titled/escaped/reference-style), and raw
            # HTML/SVG/area anchors: RENDER the body with markdown exactly as
            # build_site does and read the REAL anchor targets. Markdown emits
            # no anchor for prose `](x)`, an unused reference definition, or a
            # link inside code, so none of those queue a spurious edge
            # (CFAR r6/r15/r17/r19/r21).
            for cand in _raw_anchor_hrefs(_render_markdown(body)):
                kind, stem = canonical_article_target(
                    html.unescape(cand), meta=meta_stub)
                if kind == "article" and stem == target_slug:
                    hit = True
                    break
        if hit:
            sources.append(source_slug)
    return sources


def _remove_preflight(root, slug):
    """Shared READ-ONLY preflight for remove and its consequence preview —
    one implementation, so the preview can never drift from the operation
    (fe-ux packet §2.3 parity-by-construction)."""
    if not SLUG_RE.match(slug):
        raise OpRefused("invalid article slug")
    # generated/structural pages cannot be retired: the builder always
    # regenerates them (index; arc_page rebuilds civilization-arc.html and its
    # alias regardless of retired_on), so a tombstone would be reanimated and
    # the completed-retirement ledger row would be a lie (CFAR r25)
    if slug in PROTECTED_SLUGS:
        raise OpRefused("the %s page is generated/structural and cannot be "
                        "retired" % slug)
    article_path = root / "wiki" / ("%s.md" % slug)
    if not article_path.exists():
        raise OpRefused("unknown article slug")
    fm_lines, tail = _parse_article(article_path.read_text())
    if fm_scalar(fm_lines, "retired_on"):
        raise OpRefused("article is already retired")
    return article_path, fm_lines, tail


def _preview_state_preflights(root):
    """The operation-state checks the real ops run before mutating (corrupt
    ledger / unappendable ledger / corrupt edge-states refuse EVERY op) —
    both are read-only, so the preview runs them too and surfaces the
    refusal BEFORE a submit could arm for a doomed operation (CFAR r2 P2)."""
    ledger_preflight(root / "compile" / "ingest-ledger.jsonl")
    load_edge_states(root / "compile" / "edge-states.json")


def preview_remove(root, slug):
    """Read-only consequence preview (fe-ux packet §2.3): the SAME preflights
    and edge enumeration the operation runs. Consumes no authorization, takes
    no lock, writes nothing."""
    root = pathlib.Path(root)
    _remove_preflight(root, slug)
    _preview_state_preflights(root)
    inbound = find_inbound_edges(root, slug)
    return {"operation": "remove", "slug": slug, "inbound": inbound,
            "edges_would_pend": len(inbound),
            "tombstone": "%s.html" % slug, "will_recompile": True}


def preview_replace(root, slug, source_ref):
    """Read-only consequence preview for replace — same preflight helpers the
    operation runs, so a doomed request previews its EXACT refusal."""
    root = pathlib.Path(root)
    _replace_preflight(root, slug, source_ref)
    _preview_state_preflights(root)
    return {"operation": "replace", "slug": slug, "source_ref": source_ref,
            "superseded": source_ref, "will_recompile": True}


# ----------------------------------------------------- manifest (shards, R6)

def _validate_manifest_row(row):
    if not isinstance(row, dict):
        raise OpRefused("manifest row: not an object")
    keys = set(row)
    if keys == MANIFEST_FILE_KEYS:
        if not isinstance(row["sha256"], str) \
                or not SHA256_RE.match(row["sha256"]):
            raise OpRefused("manifest row: sha256 must be hex sha256")
    elif keys != MANIFEST_URL_KEYS:
        raise OpRefused("manifest row: keys must be exactly the file or "
                        "URL shape")
    for key in sorted(keys):
        if not isinstance(row[key], str):
            raise OpRefused("manifest row: %r must be a string" % key)
        # target_slug may be blank: the default Add flow writes its manifest
        # row BEFORE a new article slug exists (unassigned add — CFAR r1 P1);
        # register enforces its own non-empty slug upstream
        if key not in ("note", "supersedes", "target_slug") and not row[key]:
            raise OpRefused("manifest row: %r must be non-empty" % key)


def write_manifest_shard(root, row, now):
    """One immutable single-row shard file per manifest row (fe-ux packet
    §2.5): raw/inbox/manifest.jsonl is FROZEN as the historical segment and
    never rewritten; every new row is created exactly once via O_CREAT|O_EXCL.
    Every manifest blob is therefore immutable from birth — which is what
    closes the #50 secret-scan re-clearance class: no clearance pinned to a
    blob sha ever goes stale, and neither a PR nor a runtime append can
    poison a later commit. An existing path REFUSES — never overwrite, never
    append. The complete audit surface = frozen file + shards
    (`cat raw/inbox/manifest.jsonl raw/inbox/manifest.d/*.jsonl`); a shard
    without a matching ledger row is the detectable signature of an
    incomplete operation."""
    root = pathlib.Path(root)
    _validate_manifest_row(row)
    if not _valid_ts(now):
        raise OpRefused("now must be an ISO-8601 timestamp with a timezone")
    stamp = _parse_iso(now).astimezone(datetime.timezone.utc) \
        .strftime("%Y%m%dT%H%M%S.%f")
    # the filename digest binds the FULL row identity, not the document
    # content: two distinct rows carrying identical bytes at the same
    # instant must both write; only a byte-identical duplicate row collides
    # and refuses (CFAR r2 P2)
    digest = hashlib.sha256(
        json.dumps(row, sort_keys=True).encode("utf-8")).hexdigest()
    shard_dir = root / "raw" / "inbox" / "manifest.d"
    shard_dir.mkdir(parents=True, exist_ok=True)
    path = shard_dir / ("%sZ-%s.jsonl" % (stamp, digest[:12]))
    try:
        fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
    except FileExistsError:
        raise OpRefused("manifest shard already exists (%s) — refusing to "
                        "overwrite or append" % path.name)
    with os.fdopen(fd, "w") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")
    return str(path.relative_to(root))


def manifest_registered_paths(root):
    """Every source_path recorded across the frozen manifest + shards.
    STRICT parse: the register dedup gate cannot vouch over unreadable audit
    rows, so a corrupt line refuses (fail closed) rather than risking a
    missed registration. Historical rows are read for source_path only —
    their key sets are historical audit shapes, not re-validated here."""
    root = pathlib.Path(root)
    files = []
    frozen = root / "raw" / "inbox" / "manifest.jsonl"
    if frozen.exists():
        files.append(frozen)
    shard_dir = root / "raw" / "inbox" / "manifest.d"
    if shard_dir.exists():
        files.extend(sorted(shard_dir.glob("*.jsonl")))
    paths = set()
    for path in files:
        for lineno, line in enumerate(path.read_text().splitlines(), 1):
            where = "%s line %d" % (path.name, lineno)
            if not line.strip():
                raise OpRefused("%s: blank line — strict JSONL" % where)
            try:
                row = json.loads(line, object_pairs_hook=_no_dup)
            except (json.JSONDecodeError, ValueError):
                raise OpRefused("%s: not valid JSON (or duplicate key)"
                                % where)
            if not isinstance(row, dict):
                raise OpRefused("%s: not an object" % where)
            source_path = row.get("source_path")
            if isinstance(source_path, str) and source_path:
                paths.add(source_path)
    return paths


# ----------------------------------------------------------- register (R6)

def register_source(root, *, slug, source_ref, note, now, rebuild_runner=None):
    """Sanctioned session-author registration (issue #50; fe-ux packet §2.5).
    Registers an ALREADY-COMMITTED in-repo raw document in the manifest +
    article frontmatter + ops ledger under the same deny-by-default
    single-use artifact contract as Replace/Remove. The operation writes
    content NEVER — the document arrived via a gated PR; this records it.
    Write order: preflights (all read-only) -> consume -> manifest shard ->
    frontmatter -> rebuild -> LEDGER ROW LAST (append-last: the ledger never
    claims an operation that did not complete)."""
    root = pathlib.Path(root)
    now = _now_str(now)
    if not _valid_ts(now):
        raise OpRefused("now must be an ISO-8601 timestamp with a timezone")
    auth_path = root / "compile" / "ingest-authorization.json"
    auth = load_authorization(auth_path, now, operation="register",
                              slug=slug, source_ref=source_ref)
    quarantine_fields({"slug": slug, "source_ref": source_ref, "note": note,
                       "authorized_by": auth["authority"]})

    # preflight — read-only; refusal leaves the tree byte-identical AND the
    # artifact unconsumed
    if not SLUG_RE.match(slug):
        raise OpRefused("invalid article slug")
    article_path = root / "wiki" / ("%s.md" % slug)
    if not article_path.exists():
        raise OpRefused("unknown article slug")
    fm_lines, tail = _parse_article(article_path.read_text())
    if fm_scalar(fm_lines, "retired_on"):
        raise OpRefused("article is retired — register refused")
    if URL_RE.match(source_ref):
        raise OpRefused("register records in-repo raw documents, not URLs")
    if not source_ref.startswith("raw/"):
        raise OpRefused("source_ref must be a local raw/ path")
    parts = source_ref.split("/")
    if "\\" in source_ref or "" in parts or "." in parts or ".." in parts:
        raise OpRefused("source_ref must be a canonical raw/ path")
    doc_path = root / source_ref
    if not doc_path.is_file():
        raise OpRefused("source file not found in the tree")
    raw_root = (root / "raw").resolve()
    if not str(doc_path.resolve()).startswith(str(raw_root) + os.sep):
        raise OpRefused("source_ref escapes raw/ — refused")
    data = doc_path.read_bytes()
    if not data:
        raise OpRefused("session document is empty")
    # register records PR-LANDED documents only (#50 contract): the source
    # must exist at HEAD byte-exactly, else a clearance committed ahead of
    # its file could vouch for working-tree bytes that never went through
    # the committed-file scan (CFAR r4 P1) — and the manifest would record
    # state git cannot reproduce. HEAD is resolved ONCE and the same pinned
    # commit backs both this check and the allowlist attestation, so a
    # deploy advancing HEAD mid-request cannot split the trust root
    # (ready-state CFAR TOCTOU)
    head = _git_no_fetch(root, "rev-parse", "HEAD")
    if head.returncode != 0:
        raise OpRefused("cannot resolve the repository HEAD — refused")
    pinned = head.stdout.decode("utf-8", "replace").strip()
    committed = _git_no_fetch(root, "show", "%s:%s" % (pinned, source_ref))
    if committed.returncode != 0:
        raise OpRefused("source_ref is not a committed file at HEAD — "
                        "register records PR-landed documents only")
    if committed.stdout != data:
        raise OpRefused("source_ref differs from its committed bytes at "
                        "HEAD; refused")
    # committed-file attestation lane — see quarantine_payload_attested
    quarantine_payload_attested(data, canonical_path=source_ref, root=root,
                                commit=pinned)
    # dedup gate = the MANIFEST (frozen + shards), NOT the frontmatter: the
    # first consumer (#50) already carries the raw_documents pointer while
    # the manifest does not — that missing row is exactly the gap this
    # operation closes. Refuse BEFORE consumption so a wasted grant is
    # structurally impossible.
    if source_ref in manifest_registered_paths(root):
        raise OpRefused("source_ref is already registered in the manifest")
    ledger_path = root / "compile" / "ingest-ledger.jsonl"
    ledger_preflight(ledger_path)
    load_edge_states(root / "compile" / "edge-states.json")
    sha = hashlib.sha256(data).hexdigest()

    # durable write #0: burn the single-use authorization (intent record)
    digest = consume_authorization(auth_path, auth, now)

    # 1. manifest shard (immutable single-row file)
    write_manifest_shard(root, {
        "ingested_at": now, "mode": "session-author", "target_slug": slug,
        "source_path": source_ref, "sha256": sha,
        "original_name": pathlib.Path(source_ref).name, "note": note,
        "supersedes": ""}, now)

    # 2. frontmatter: add-iff-absent — an existing pointer is legal interim
    # provenance (#50 first consumer); the manifest above is the dedup gate
    fm_lines = _normalize_list_to_block(fm_lines, "raw_documents")
    if source_ref not in fm_list_values(fm_lines, "raw_documents"):
        fm_lines = _append_list_value(fm_lines, "raw_documents", source_ref)
        _atomic_write_text(article_path, _assemble_article(fm_lines, tail))

    _append_provenance(root, "- %s register: `%s` (sha256 %s…) recorded for "
                       "article `%s` (authorized by %s)"
                       % (_date_of(now), source_ref, sha[:12], slug,
                          auth["authority"]))

    # 3. rebuild, then 4. ledger row LAST — the completion claim
    rebuild = _run_rebuild(root, rebuild_runner)
    row = {"ts": now, "operation": "register", "slug": slug,
           "source_path": source_ref, "sha256": sha,
           "authorized_by": auth["authority"], "authorization_sha256": digest,
           "result": "completed", "rebuild": rebuild}
    append_ledger(ledger_path, row)
    return row


def remove_topic(root, *, slug, now, rebuild_runner=None):
    root = pathlib.Path(root)
    now = _now_str(now)  # reject a naive timestamp before any write (CFAR r14)
    if not _valid_ts(now):
        raise OpRefused("now must be an ISO-8601 timestamp with a timezone")
    auth_path = root / "compile" / "ingest-authorization.json"
    auth = load_authorization(auth_path, now, operation="remove",
                              slug=slug, source_ref="")
    # the retirement rationale is BOUND to the authorization artifact — it is
    # the human-approved `reason`, never a separately-supplied request string,
    # so the tombstone/edge/PROVENANCE/ledger audit cannot diverge from the
    # grant (CFAR r26). load_authorization already stripped it single-line and
    # rejected blanks/newlines (CFAR r5/r10); quarantine it since it persists.
    reason = auth["reason"]
    quarantine_fields({"slug": slug, "reason": reason,
                       "authorized_by": auth["authority"]})

    # preflight — read-only (shared with preview_remove — parity by
    # construction)
    article_path, fm_lines, _tail = _remove_preflight(root, slug)
    ledger_path = root / "compile" / "ingest-ledger.jsonl"
    ledger_preflight(ledger_path)
    edge_path = root / "compile" / "edge-states.json"
    edge_states = load_edge_states(edge_path)
    inbound = find_inbound_edges(root, slug)

    # durable write #0: burn the single-use authorization (intent record)
    digest = consume_authorization(auth_path, auth, now)

    # Layer 1: tombstone (never a delete) + every inbound edge to an explicit
    # queued dangling-pending state, atomically
    title = fm_scalar(fm_lines, "entity") or slug.replace("-", " ")
    stub_fm = ["entity: %s" % json.dumps(title)]
    # read aliases via fm_list_values so BOTH the inline `[..]` and block forms
    # survive retirement (removal preserves entity + aliases; CFAR r5 P2-2)
    aliases = fm_list_values(fm_lines, "aliases")
    if aliases:
        stub_fm.append("aliases:")
        stub_fm.extend("  - %s" % json.dumps(a) for a in aliases)
    tier = fm_scalar(fm_lines, "tier")
    if tier:
        stub_fm.append("tier: %s" % tier)
    stub_fm.append("retired_on: %s" % json.dumps(_date_of(now)))
    stub_fm.append("retired_reason: %s" % json.dumps(reason))
    # markdown `extra` passes raw HTML through, so escape any HTML in the
    # title/reason before it reaches the rendered tombstone body — the
    # frontmatter banner is already escaped by build_site, the body was not
    # (CFAR r1 P2-2). Collapse newlines so a reason cannot break structure.
    safe_title = html.escape(title)
    safe_reason = html.escape(re.sub(r"\s+", " ", reason).strip())
    stub_body = (
        "# %s\n\n**Retired** on %s — %s\n\nThis topic is a tombstone: its "
        "raw sources are preserved under `raw/` and every inbound reference "
        "is queued for reconciliation. Nothing was deleted.\n"
        % (safe_title, _date_of(now), safe_reason))
    _atomic_write_text(article_path,
                       "---\n" + "\n".join(stub_fm) + "\n---\n\n" + stub_body)

    for source in inbound:
        edge_states["%s->%s" % (source, slug)] = {
            "state": "dangling-pending",
            "since": _now_str(now),
            "reason": "target retired: %s" % reason,
            "queued": True,
            "enqueued_at": _now_str(now),
        }
    # closure (AC5) is a post-condition over the WHOLE file, not just this
    # Remove's own edges: the deterministic Layer-1 pass enqueues EVERY
    # dangling-pending edge, including any that pre-existed unqueued, so no
    # pending work is ever left off the committed queue (CFAR r5 P2-3). Every
    # such repair is RECORDED in the audit — a mutation of committed state must
    # never be silent (CFAR ready-state).
    own_keys = {"%s->%s" % (source, slug) for source in inbound}
    repaired = []
    for key, entry in edge_states.items():
        if key in own_keys:
            continue
        if entry["state"] == "dangling-pending" and not entry["queued"]:
            entry["queued"] = True
            entry["enqueued_at"] = _now_str(now)
            repaired.append(key)
    repaired = sorted(repaired)
    write_edge_states(edge_path, edge_states)

    prov = ("- %s remove: topic `%s` retired — %s "
            "(authorized by %s; %d inbound edge(s) queued"
            % (_date_of(now), slug, reason, auth["authority"], len(inbound)))
    if repaired:
        prov += "; %d pre-existing pending edge(s) repaired to queued: %s" \
            % (len(repaired), ", ".join(repaired))
    _append_provenance(root, prov + ")")

    rebuild = _run_rebuild(root, rebuild_runner)
    row = {"ts": _now_str(now), "operation": "remove", "slug": slug,
           "reason": reason, "authorized_by": auth["authority"],
           "authorization_sha256": digest,
           "affected_edges": sorted(inbound), "repaired_edges": repaired,
           "result": "completed", "rebuild": rebuild}
    append_ledger(ledger_path, row)
    return row
