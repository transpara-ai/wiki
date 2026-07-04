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
AUTH_KEYS = {"df", "operation", "slug", "source_ref", "authority",
             "authorized_at", "expires_at", "reason", "engine_command",
             "engine_timeout_seconds"}
LEDGER_SHAPES = {
    "add": {"ts", "operation", "slug", "sources", "created", "rebuild"},
    "replace": {"ts", "operation", "slug", "superseded", "replacement",
                "authorized_by", "authorization_sha256", "engine", "result",
                "rebuild"},
    "remove": {"ts", "operation", "slug", "reason", "authorized_by",
               "authorization_sha256", "affected_edges", "result", "rebuild"},
}


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
    if operation not in ("replace", "remove"):
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
    if auth["operation"] not in ("replace", "remove"):
        raise AuthRefused("artifact operation must be replace or remove")
    if auth["operation"] == "remove" and auth["source_ref"] != "":
        raise AuthRefused("a remove artifact must carry source_ref \"\"")
    if auth["operation"] == "replace" and not auth["source_ref"]:
        raise AuthRefused("a replace artifact must name its source_ref")
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
    findings = secret_scan.scan_text(data.decode("utf-8", "replace"))
    if findings:
        rules = sorted({f.rule_id for f in findings})
        raise OpRefused("%d secret finding(s) in payload [%s]; refused"
                        % (len(findings), ", ".join(rules)))
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
    if set(row) != LEDGER_SHAPES[operation]:
        raise OpRefused("%s: %s keys must be exactly %s"
                        % (where, operation, sorted(LEDGER_SHAPES[operation])))
    if not _valid_ts(row.get("ts")):
        raise OpRefused("%s: ts must be ISO-8601 with timezone" % where)
    _require_row_str(row, ("slug",), where)
    if row["rebuild"] not in ("ok", "failed"):
        raise OpRefused("%s: rebuild must be ok|failed" % where)
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
    _require_row_str(row, ("reason",), where)
    if not isinstance(row["affected_edges"], list) or any(
            not isinstance(s, str) or not s for s in row["affected_edges"]):
        raise OpRefused("%s: affected_edges must be a list of non-empty strings" % where)
    if row["result"] != "completed":
        raise OpRefused("%s: remove result must be completed" % where)


def ledger_preflight(path):
    """Strict end-to-end parse of the existing ledger. A corrupt line refuses
    (an unauditable surface takes no new actions). Absent file = valid empty."""
    path = pathlib.Path(path)
    if not path.exists():
        return []
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
    with path.open("a") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")


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
    if the value is not an inline list."""
    value = line.split(":", 1)[1].strip() if ":" in line else ""
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


def run_engine(engine_command, timeout, job):
    """Authority-gated single-article synthesis. Output is the article BODY
    only; every violation of the output law discards the output (the caller
    keeps the deterministic honest-stale state)."""
    if engine_command == []:
        return ("disabled", None)
    try:
        proc = subprocess.Popen(
            list(engine_command), stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, start_new_session=True)
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

def replace_source(root, *, slug, source_ref, data, filename, note, now,
                   rebuild_runner=None):
    root = pathlib.Path(root)
    auth_path = root / "compile" / "ingest-authorization.json"
    auth = load_authorization(auth_path, now, operation="replace",
                              slug=slug, source_ref=source_ref)
    quarantine_fields({"slug": slug, "source_ref": source_ref, "note": note,
                       "filename": filename, "authorized_by": auth["authority"]})
    quarantine_payload(data)

    # preflight — read-only; refusal leaves the tree byte-identical
    if not SLUG_RE.match(slug):
        raise OpRefused("invalid article slug")
    article_path = root / "wiki" / ("%s.md" % slug)
    if not article_path.exists():
        raise OpRefused("unknown article slug")
    raw = article_path.read_text()
    fm_lines, tail = _parse_article(raw)
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
                              auth["engine_timeout_seconds"], job)
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

def _board_field_matches(raw, target_slug):
    # a board field may carry an inline comment and/or quotes that
    # build_site.board_scalar tolerates — strip both before comparing so the
    # reference is not missed (CFAR r6 P2-3)
    for field in raw.split("|"):
        if _clean_item(field) == target_slug:
            return True
    return False


def _references_via_board(fm_lines, target_slug):
    """True if index.md's board frontmatter references target_slug — the
    builder generates (and now gates) homepage board links from these keys, so
    a board-only reference is a real inbound edge to queue (CFAR r4/r6)."""
    for key in ("board_narrative_link", "board_guardrail"):
        if _board_field_matches(fm_scalar(fm_lines, key), target_slug):
            return True
    for key in ("board_pillars", "board_inheritance"):
        for item in fm_list_values(fm_lines, key):
            if _board_field_matches(item, target_slug):
                return True
    return False


def find_inbound_edges(root, target_slug):
    """Every source that links to the target — through any BODY form
    ([[wikilink]], markdown (slug.html) INCLUDING titled links, raw
    href="slug.html" any spelling) OR, for the homepage, through generated
    board frontmatter links. The homepage (index.md) is scanned because the
    builder renders its links with source_slug 'index' (CFAR r1 P2-4/P2-5,
    r4 P2)."""
    wikilink = re.compile(r"\[\[%s(?:\|[^\]]*)?\]\]" % re.escape(target_slug))
    # capture the URL token after `](`; a title (` "..."`) or `)` may follow,
    # so do NOT require the closing paren immediately after the URL
    md_link = re.compile(r"\]\(\s*<?([^\s)>]+)")
    # reference-style link DEFINITIONS: `[label]: url "title"` — markdown emits
    # the same internal anchor, so the edge must be queued too (CFAR r6 P2-2)
    ref_def = re.compile(r"^\s{0,3}\[[^\]]+\]:\s*<?([^\s>]+)", re.M)
    href = re.compile(r"href\s*=\s*[\"']?([^\"'\s>]+)", re.I)
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
            fm_lines, tail = _parse_article(raw)
            body = tail
        except OpRefused:
            fm_lines, body = [], raw
        hit = bool(wikilink.search(body))
        if not hit and source_slug == "index":
            hit = _references_via_board(fm_lines, target_slug)
        if not hit:
            candidates = ([m.group(1) for m in md_link.finditer(body)]
                          + [m.group(1) for m in ref_def.finditer(body)]
                          + [m.group(1) for m in href.finditer(body)])
            for candidate in candidates:
                kind, stem = canonical_article_target(
                    html.unescape(candidate), meta=meta_stub)
                if kind == "article" and stem == target_slug:
                    hit = True
                    break
        if hit:
            sources.append(source_slug)
    return sources


def remove_topic(root, *, slug, reason, now, rebuild_runner=None):
    root = pathlib.Path(root)
    auth_path = root / "compile" / "ingest-authorization.json"
    auth = load_authorization(auth_path, now, operation="remove",
                              slug=slug, source_ref="")
    # normalize + validate the reason BEFORE auth consumption or any write —
    # an empty reason must refuse in preflight (else the ledger row fails
    # AFTER the tombstone is written, orphaning the audit), and a multi-line
    # reason must collapse so it cannot inject extra PROVENANCE lines
    # (CFAR r2 P2-2)
    reason = re.sub(r"\s+", " ", reason or "").strip()
    if not reason:
        raise OpRefused("remove requires a non-empty reason")
    quarantine_fields({"slug": slug, "reason": reason,
                       "authorized_by": auth["authority"]})

    # preflight — read-only
    if not SLUG_RE.match(slug):
        raise OpRefused("invalid article slug")
    if slug == "index":
        raise OpRefused("the main page cannot be retired")
    article_path = root / "wiki" / ("%s.md" % slug)
    if not article_path.exists():
        raise OpRefused("unknown article slug")
    fm_lines, _tail = _parse_article(article_path.read_text())
    if fm_scalar(fm_lines, "retired_on"):
        raise OpRefused("article is already retired")
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
    # pending work is ever left off the committed queue (CFAR r5 P2-3)
    for entry in edge_states.values():
        if entry["state"] == "dangling-pending" and not entry["queued"]:
            entry["queued"] = True
            entry["enqueued_at"] = _now_str(now)
    write_edge_states(edge_path, edge_states)

    _append_provenance(root, "- %s remove: topic `%s` retired — %s "
                       "(authorized by %s; %d inbound edge(s) queued)"
                       % (_date_of(now), slug, reason, auth["authority"],
                          len(inbound)))

    rebuild = _run_rebuild(root, rebuild_runner)
    row = {"ts": _now_str(now), "operation": "remove", "slug": slug,
           "reason": reason, "authorized_by": auth["authority"],
           "authorization_sha256": digest,
           "affected_edges": sorted(inbound), "result": "completed",
           "rebuild": rebuild}
    append_ledger(ledger_path, row)
    return row
