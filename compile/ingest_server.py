#!/usr/bin/env python3
"""Local authoring server for the Civilization Wiki.

Serves dist/ like http.server, plus small write endpoints used by ingest.html:
  GET  /api/articles
  POST /api/ingest
  POST /api/rebuild
  POST /api/replace   (per-ingestion ops packet; ingest-authorization gated)
  POST /api/remove    (per-ingestion ops packet; ingest-authorization gated)

The durable state is still the repository: uploaded documents are written under
raw/inbox/, optional article references are appended to wiki/<slug>.md
frontmatter, and compile/refresh.py regenerates freshness status and dist/.
Replace/Remove live in compile/ingest_ops.py behind a deny-by-default,
single-use, instance-scoped authorization artifact.
"""
import datetime as dt
import fcntl
import hashlib
import hmac
import html
import ipaddress
import io
import json
import os
import pathlib
import re
import signal
import subprocess
import sys
from email import policy
from email.parser import BytesParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qsl, urlsplit

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ingest_ops  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
WIKI = ROOT / "wiki"
RAW_INBOX = ROOT / "raw" / "inbox"
MANIFEST = RAW_INBOX / "manifest.jsonl"
LOCK_PATH = ROOT / "compile" / ".wiki-write.lock"
MAX_POST_BYTES = 100 * 1024 * 1024
AUTHORING_TOKEN_ENV = "CIVWIKI_AUTHORING_TOKEN"
AUTHORING_TOKEN_HEADER = "X-CivWiki-Authoring-Token"
ALLOWED_HOSTS_ENV = "CIVWIKI_ALLOWED_HOSTS"

SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
SAFE_NAME_RE = re.compile(r"[^A-Za-z0-9._-]+")
SLUG_CHARS_RE = re.compile(r"[^a-z0-9]+")


def split_fm(raw):
    if raw.startswith("---"):
        e = raw.find("\n---", 3)
        if e != -1:
            return raw[3:e].strip("\n"), raw[e + 4:].lstrip("\n"), e
    return "", raw, -1


def strip_inline_comment(s):
    quote = ""
    esc = False
    for i, ch in enumerate(s):
        if esc:
            esc = False
            continue
        if ch == "\\":
            esc = True
            continue
        if quote:
            if ch == quote:
                quote = ""
            continue
        if ch in {"'", '"'}:
            quote = ch
            continue
        if ch == "#" and (i == 0 or s[i - 1].isspace()):
            return s[:i].rstrip()
    return s.strip()


def fm_val(fm, key):
    m = re.search(r"^%s:[ \t]*(.+)$" % re.escape(key), fm, re.M)
    return m.group(1).strip().strip('"') if m else ""


def fm_scalar(fm, key):
    """A frontmatter scalar with any inline comment stripped BEFORE quote removal,
    so `entity: Foo # canonical` reads as `Foo` (not `Foo # canonical`). Use this
    where a scalar's VALUE feeds the fail-closed collision guard, so a normal
    inline comment cannot pollute the compact key and let a duplicate through
    (CFAR: Codex)."""
    m = re.search(r"^%s:[ \t]*(.+)$" % re.escape(key), fm, re.M)
    if not m:
        return ""
    return strip_inline_comment(m.group(1)).strip().strip('"').strip("'")


def fm_list(fm, key):
    m = re.search(r"^%s:[ \t]*(.*)$" % re.escape(key), fm, re.M)
    if not m:
        return []
    inline = strip_inline_comment(m.group(1)).strip()  # a trailing `# comment` on an
    if inline.startswith("[") and inline.endswith("]"):  # inline list must not hide it
        return [x.strip().strip('"').strip("'") for x in inline[1:-1].split(",") if x.strip()]
    items = []
    for line in fm[m.end():].splitlines():
        if re.match(r"^[ \t]+-\s+", line):
            item = strip_inline_comment(re.sub(r"^[ \t]+-\s+", "", line)).strip().strip('"').strip("'")
            if item:
                items.append(item)
        elif re.match(r"^[A-Za-z_]", line):
            break
    return items


def article_is_retired(slug):
    path = WIKI / ("%s.md" % slug)
    if not path.exists():
        return False
    fm, _, _ = split_fm(path.read_text())
    return bool(fm_val(fm, "retired_on"))


def prospective_unassigned_slug(form=None, name=""):
    """The slug a create would resolve to, in lockstep with
    create_article_from_source (AC5, CFADA-r2 #4). For an explicit
    new-investigation the operator NAME drives the slug: slugify(name) — the same
    derivation the creator uses, so the pre-save collision/retired guard predicts
    the exact file a create would touch. With no name it falls back to the legacy
    first-document title derivation (no longer a create path in handle_ingest;
    retained for callers that predict the slug of an unnamed unassigned upload)."""
    if name:
        return slugify(name)
    for item in field_values(form, "documents"):
        if not getattr(item, "filename", ""):
            continue
        data = item.file.read()
        item.file = io.BytesIO(data)  # rewind for the later save
        if not data:
            continue
        fm, body, _ = split_fm(data.decode("utf-8", "replace"))
        # mirror create_article_from_source EXACTLY, including the saved
        # content-addressed stem used by its no-title fallback, so this never
        # false-refuses a distinct new article
        original = safe_filename(item.filename)
        saved_stem = "%s-%s" % (pathlib.Path(original).stem or "document",
                                hashlib.sha256(data).hexdigest()[:12])
        title = (fm_val(fm, "title") or fm_val(fm, "entity")
                 or markdown_title(body) or saved_stem.replace("-", " "))
        return slugify(title)
    return ""


def article_records(include_sources=True):
    out = []
    for p in sorted(WIKI.glob("*.md")):
        fm, _, _ = split_fm(p.read_text())
        if fm_val(fm, "retired_on"):
            continue  # retired tombstones are not offered in the ingest selector
        out.append({
            "slug": p.stem,
            "title": fm_val(fm, "entity") or p.stem.replace("-", " "),
            "tier": fm_val(fm, "tier") or "concept",
            "sources": fm_list(fm, "sources") if include_sources else [],
            # the replace preflight accepts sources OR raw_documents, so the
            # UI selector must be able to offer both (CFAR r1 P2); same gate
            "raw_documents": (fm_list(fm, "raw_documents")
                              if include_sources else []),
        })
    return out


def preview_payload(root, operation, slug, source_ref):
    """GET /api/preview logic (fe-ux packet §2.3). Echo-quarantine FIRST —
    the ops preflights echo submitted values in refusal messages, so nothing
    reaches them unproven-secret-free (the CFAR-r20 lane, on the read path).
    An OpRefused from the OPERATION lanes returns as the honest
    refuses-shape: the preview of a doomed operation IS the refusal, shown
    before any confirm. Malformed/unknown requests raise (422 at the route);
    the ops preview helpers are strictly read-only."""
    ingest_ops.quarantine_fields({"operation": operation, "slug": slug,
                                  "source_ref": source_ref})
    if operation == "remove":
        if source_ref:
            raise ingest_ops.OpRefused("remove preview takes no source_ref")
        def run():
            return ingest_ops.preview_remove(root, slug)
    elif operation == "replace":
        if not source_ref:
            raise ingest_ops.OpRefused("replace preview requires source_ref")
        def run():
            return ingest_ops.preview_replace(root, slug, source_ref)
    else:
        raise ingest_ops.OpRefused("unknown preview operation")
    try:
        return {"preview": run()}
    except ingest_ops.OpRefused as exc:
        return {"preview": {"operation": operation, "slug": slug,
                            "refuses": str(exc)}}


def json_response(handler, status, payload):
    body = json.dumps(payload, indent=2).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(body)


class FormField:
    def __init__(self, name, value="", filename="", data=b""):
        self.name = name
        self.value = value
        self.filename = filename
        self.file = io.BytesIO(data)


def add_form_field(form, field):
    if field.name in form:
        existing = form[field.name]
        if isinstance(existing, list):
            existing.append(field)
        else:
            form[field.name] = [existing, field]
    else:
        form[field.name] = field


def parse_post_form(handler):
    try:
        length = int(handler.headers.get("Content-Length", "0") or "0")
    except ValueError:
        raise ValueError("invalid Content-Length")
    if length > MAX_POST_BYTES:
        raise ValueError("upload is too large; limit is %d bytes" % MAX_POST_BYTES)

    content_type = handler.headers.get("Content-Type", "")
    body = handler.rfile.read(length)
    form = {}

    if content_type.startswith("application/x-www-form-urlencoded"):
        for name, value in parse_qsl(body.decode("utf-8", "replace"), keep_blank_values=True):
            add_form_field(form, FormField(name, value=value, data=value.encode("utf-8")))
        return form

    if not content_type.startswith("multipart/form-data"):
        raise ValueError("unsupported Content-Type: %s" % content_type)

    message = BytesParser(policy=policy.default).parsebytes(
        b"Content-Type: " + content_type.encode("utf-8") + b"\r\n"
        b"MIME-Version: 1.0\r\n\r\n" + body
    )
    if not message.is_multipart():
        return form

    for part in message.iter_parts():
        if part.get_content_disposition() != "form-data":
            continue
        name = part.get_param("name", header="content-disposition")
        if not name:
            continue
        data = part.get_payload(decode=True)
        if data is None:
            payload = part.get_content()
            data = payload.encode("utf-8") if isinstance(payload, str) else bytes(payload)
        filename = part.get_filename() or ""
        if filename:
            field = FormField(name, filename=filename, data=data)
        else:
            charset = part.get_content_charset() or "utf-8"
            field = FormField(name, value=data.decode(charset, "replace"), data=data)
        add_form_field(form, field)
    return form


def field_values(form, name):
    if name not in form:
        return []
    item = form[name]
    if isinstance(item, list):
        return item
    return [item]


def first_value(form, name, default=""):
    vals = field_values(form, name)
    if not vals:
        return default
    value = vals[0].value
    return value if isinstance(value, str) else default


def normalize_target_slug(target_slug):
    target_slug = (target_slug or "").strip()
    if target_slug and not SLUG_RE.match(target_slug):
        raise ValueError("invalid article slug: %s" % target_slug)
    return target_slug


def safe_filename(name):
    name = pathlib.PurePath(name or "document.md").name
    cleaned = SAFE_NAME_RE.sub("-", name).strip(".-")
    return cleaned or "document.md"


def slugify(text):
    text = (text or "").lower()
    text = re.sub(r"\([^)]*\)", " ", text)
    text = SLUG_CHARS_RE.sub("-", text).strip("-")
    text = re.sub(r"-+", "-", text)
    return text[:80].strip("-") or "ingested-document"


def collision_key(s):
    """§2.4 compact collision key: casefold, then keep only alphanumerics —
    dropping whitespace, hyphens, punctuation, and parentheses. Collapses every
    separator variant, including no-space vs space ("MemPalace"/"Mem Palace"/
    "Mem-Palace" -> "mempalace"; "Sakana AI"/"Sakana-AI"/"Sakana (AI)" ->
    "sakanaai"); unlike slugify it NEVER drops text (CFADA-r8 #21, r9 #22)."""
    return "".join(ch for ch in (s or "").casefold() if ch.isalnum())


def article_tier(slug):
    path = WIKI / ("%s.md" % slug)
    if not path.exists():
        return ""
    fm, _, _ = split_fm(path.read_text())
    # fm_scalar: a commented `tier: investigation # x` must still gate the ADD
    # stale stamp, else no re-derivation banner is produced (CFAR: Codex).
    return fm_scalar(fm, "tier")


def _investigation_collision_corpus():
    """The collision surfaces a new investigation name must avoid (§2.4). Returns
    (keys, slugs): `keys` = collision_key of every page slug PLUS, for every
    investigation page (active OR retired tombstone), its entity ∪ aliases ∪
    investigation_topic cluster label; `slugs` = every page slug (active OR
    tombstone). Retired frontmatter is included so a new investigation cannot
    reanimate a retired subject via its old entity/alias/cluster (CFADA-r12 #28)."""
    keys, slugs = set(), set()
    for p in sorted(WIKI.glob("*.md")):
        fm, _, _ = split_fm(p.read_text())
        slugs.add(p.stem)
        keys.add(collision_key(p.stem))
        # fm_scalar (not fm_val): a normal inline comment on entity/topic/tier must
        # not pollute the compact collision key, else a commented `entity: Foo #x`
        # would key as `foox` and a duplicate `Foo` could slip the guard (CFAR: Codex).
        if fm_scalar(fm, "tier") == "investigation" or fm_val(fm, "retired_on"):
            for value in ([fm_scalar(fm, "entity"), fm_scalar(fm, "investigation_topic")]
                          + fm_list(fm, "aliases")):
                if value:
                    keys.add(collision_key(value))
    return keys, slugs


def new_investigation_name_ok(name):
    """R6/§2.4: an explicit new-investigation name must be non-empty, yield a
    non-empty compact collision_key, AND yield a slugify() that is NOT the generic
    'ingested-document' fallback — else a create could mint a generic page
    unrelated to the subject (names like "!!!" or "()"; CFADA-r11 #26)."""
    name = (name or "").strip()
    if not name:
        return False
    # a name is a single-line subject label — reject C0 control/newline chars,
    # which would break the skeleton's H1 and bold Summary lead (the created page
    # would then fail its own investigation_conformance) (CFAR: Codex).
    if any(ord(ch) < 0x20 for ch in name):
        return False
    if not collision_key(name):
        return False
    if slugify(name) == "ingested-document":
        return False
    return True


def subject_absent(name):
    """Fail-closed page-creation guard (R1/§2.4). True ONLY if the subject is
    proven absent: NEITHER the compact collision_key(name) collides with any
    existing entity / alias / cluster / slug (active or retired), NOR the generated
    slugify(name) equals any existing page slug. Both are checked because slugify
    DROPS parenthesized text ("Foo (Bar)" -> "foo") while collision_key never
    does — so the compact key can differ from the file slugify would actually
    touch; slugify(name) is the fail-closed ground truth (CFADA-r10 #23). Any
    match refuses; the unknown/ambiguous case never creates."""
    keys, slugs = _investigation_collision_corpus()
    if collision_key(name) in keys:
        return False
    if slugify(name) in slugs:
        return False
    return True


def form_flag(form, name):
    """A boolean form field, default OFF. True only for an explicit affirmative
    token — the fail-safe allowlist direction, so an absent/malformed value never
    enables the create lane (and the collision guard is the real gate regardless)."""
    return first_value(form, name).strip().lower() in {"true", "on", "1", "yes"}


def resolve_ingest_route(*, new_investigation, target_slug, name, has_document=True):
    """Fail-closed ingest router (R1/R5/R6/§2.4). Returns "create" for an explicit
    new investigation whose name is valid, that carries a document to seed the
    page, AND whose subject is proven absent, or "append" to add to an existing
    ACTIVE page (any tier); otherwise raises OpRefused. The ONLY create branch is
    new_investigation AND a valid name AND a seeding document AND the subject
    proven absent — every other path appends or refuses, and there is no
    else/fall-through that creates. For "append" the caller uses target_slug (here
    proven to exist and be active); for "create" the caller derives the slug from
    the name via prospective_unassigned_slug (lockstep with the creator)."""
    if new_investigation:
        if not new_investigation_name_ok(name):
            raise ingest_ops.OpRefused(
                "a new investigation requires a name that yields a slug and a "
                "non-empty collision key")
        if not has_document:
            raise ingest_ops.OpRefused(
                "a new investigation requires at least one uploaded document to "
                "seed the page")
        if not subject_absent(name):
            raise ingest_ops.OpRefused(
                "an investigation for this subject already exists "
                "(name / slug / alias / cluster collision) — refused")
        return "create"
    if not target_slug:
        raise ingest_ops.OpRefused(
            "add requires an existing target_slug; check 'new investigation' to "
            "create a page")
    if article_is_retired(target_slug):
        raise ingest_ops.OpRefused(
            "target article is retired — Add refused; a retired topic is a "
            "tombstone reachable by direct link only")
    if not (WIKI / ("%s.md" % target_slug)).exists():
        raise ingest_ops.OpRefused("target article does not exist — Add refused")
    return "append"


def child_path_under(child, root):
    try:
        child.resolve().relative_to(root.resolve())
        return True
    except Exception:
        return False


def is_loopback_host(host):
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return host in {"localhost", ""}


def split_host_header(host_header):
    host_header = (host_header or "").strip().lower()
    if not host_header:
        return "", ""
    if host_header.startswith("["):
        close = host_header.find("]")
        if close < 0:
            return "", ""
        host = host_header[1:close]
        rest = host_header[close + 1:]
        if rest and not rest.startswith(":"):
            return "", ""
        port = rest[1:] if rest.startswith(":") else ""
        if port and not port.isdigit():
            return "", ""
        return host.rstrip("."), port
    if host_header.count(":") == 1:
        host, port = host_header.rsplit(":", 1)
        if not host or (port and not port.isdigit()):
            return "", ""
        return host.rstrip("."), port
    return host_header.rstrip("."), ""


def host_header_allowed(host_header, server_port=None):
    host, port = split_host_header(host_header)
    if not host:
        return False
    server_port = str(server_port or "")
    if host in {"localhost", "127.0.0.1", "::1"} and (not port or not server_port or port == server_port):
        return True
    for allowed in os.environ.get(ALLOWED_HOSTS_ENV, "").split(","):
        allowed_host, allowed_port = split_host_header(allowed)
        if not allowed_host:
            continue
        if allowed_port:
            if (host, port) == (allowed_host, allowed_port):
                return True
        elif host == allowed_host and (not port or not server_port or port == server_port):
            return True
    return False


def effective_port(port, scheme, server_port=None):
    if port:
        return str(port)
    if server_port:
        return str(server_port)
    if scheme == "https":
        return "443"
    return "80"


def parsed_origin_port(parsed):
    try:
        return parsed.port
    except ValueError:
        return False


def same_origin_authoring_request(headers, server_port=None):
    sec_fetch_site = (headers.get("Sec-Fetch-Site", "") or "").strip().lower()
    if sec_fetch_site and sec_fetch_site not in {"same-origin", "none"}:
        return False

    origin = (headers.get("Origin", "") or "").strip()
    if not origin:
        return True

    parsed = urlsplit(origin)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return False

    host, port = split_host_header(headers.get("Host", ""))
    if not host:
        return False
    origin_host = parsed.hostname.rstrip(".").lower()
    origin_port_raw = parsed_origin_port(parsed)
    if origin_port_raw is False:
        return False
    origin_port = effective_port(origin_port_raw, parsed.scheme)
    request_port = effective_port(port, "http", server_port)
    return origin_host == host and origin_port == request_port


def authoring_allowed(client_host, supplied_token, configured_token=None):
    if configured_token is None:
        configured_token = os.environ.get(AUTHORING_TOKEN_ENV, "")
    if configured_token:
        return hmac.compare_digest(supplied_token or "", configured_token)
    return is_loopback_host(client_host)


def markdown_title(body):
    m = re.search(r"^#\s+(.+?)\s*$", body, re.M)
    return m.group(1).strip() if m else ""


def source_title_from_path(source):
    path = ROOT / source
    if not path.exists():
        return pathlib.PurePosixPath(source).stem.replace("-", " ")
    text = path.read_text(errors="replace")
    fm, body, _ = split_fm(text)
    return (
        fm_val(fm, "title")
        or fm_val(fm, "entity")
        or markdown_title(body)
        or path.stem.replace("-", " ")
    )


def source_doc_id_from_path(source):
    path = ROOT / source
    if not path.exists():
        return ""
    fm, _, _ = split_fm(path.read_text(errors="replace"))
    return fm_val(fm, "document_id") or fm_val(fm, "doc_id")


def markdown_inline_text(value):
    value = html.escape(value or "", quote=False)
    value = value.replace("\\", "\\\\")
    for ch in "`*_{}[]()#+-.!|":
        value = value.replace(ch, "\\" + ch)
    return value


def save_uploads(form, target_slug, note, supersedes):
    today = dt.datetime.now().strftime("%Y-%m-%d")
    bucket = normalize_target_slug(target_slug) or "unassigned"
    dst_dir = RAW_INBOX / today / bucket
    dst_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    for item in field_values(form, "documents"):
        if not getattr(item, "filename", ""):
            continue
        data = item.file.read()
        if not data:
            continue
        digest = hashlib.sha256(data).hexdigest()
        original = safe_filename(item.filename)
        stem = pathlib.Path(original).stem or "document"
        suffix = pathlib.Path(original).suffix or ".md"
        dst = dst_dir / ("%s-%s%s" % (stem, digest[:12], suffix))
        if not child_path_under(dst, RAW_INBOX):
            raise ValueError("upload destination escaped raw inbox")
        if not dst.exists():
            ingest_ops.atomic_write_bytes(dst, data)
        rel = str(dst.resolve().relative_to(ROOT.resolve()))
        saved.append({"path": rel, "sha256": digest, "original": original})
        append_manifest({
            "ingested_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "mode": "browser-ingest",
            "target_slug": target_slug,
            "source_path": rel,
            "sha256": digest,
            "original_name": original,
            "note": note,
            "supersedes": supersedes,
        })
    return saved


def append_manifest(row):
    # frozen-file law (fe-ux packet §2.5): raw/inbox/manifest.jsonl is the
    # historical segment and never grows again; every new row is an immutable
    # single-row shard under raw/inbox/manifest.d/ (see its README.md), so no
    # committed manifest blob ever changes after birth (issue #50 F9 class)
    return ingest_ops.write_manifest_shard(ROOT, row, row["ingested_at"])


class wiki_write_lock:
    def __enter__(self):
        LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
        self._file = LOCK_PATH.open("w")
        fcntl.flock(self._file.fileno(), fcntl.LOCK_EX)
        return self

    def __exit__(self, exc_type, exc, tb):
        fcntl.flock(self._file.fileno(), fcntl.LOCK_UN)
        self._file.close()


def valid_external_urls(text):
    urls = []
    for line in (text or "").splitlines():
        url = line.strip()
        if not url:
            continue
        if not re.match(r"^https?://", url, re.I):
            raise ValueError("external URL must start with http:// or https://: %s" % url)
        urls.append(url)
    return urls


def comment_value(value, limit=320):
    return re.sub(r"\s+", " ", value or "").strip()[:limit]


def source_line(source, note, supersedes):
    parts = ["added via wiki browser ingest %s" % dt.datetime.now().strftime("%Y-%m-%d")]
    note = comment_value(note, 180)
    supersedes = comment_value(supersedes)
    if note:
        parts.append("note: %s" % note)
    if supersedes:
        parts.append("supersedes: %s" % supersedes)
    return "  - %s  # %s\n" % (json.dumps(source), "; ".join(parts))


def raw_document_line(source):
    return "  - %s\n" % json.dumps(source)


def source_href(source):
    if source.startswith(("http://", "https://")):
        return source
    sid = hashlib.sha1(source.strip().encode("utf-8")).hexdigest()[:16]
    return "source/%s.html" % sid


def append_frontmatter_list_items(slug, key, values, line_builder):
    if not slug:
        return []
    if not SLUG_RE.match(slug):
        raise ValueError("invalid article slug: %s" % slug)
    path = WIKI / ("%s.md" % slug)
    if not path.exists():
        raise ValueError("unknown article slug: %s" % slug)
    raw = path.read_text()
    fm, _, fm_end = split_fm(raw)
    if fm_end < 0:
        raise ValueError("article has no frontmatter: %s" % slug)
    existing = set(fm_list(fm, key))
    added = []
    lines = []
    for value in values:
        value = value.strip()
        if not value or value in existing:
            continue
        lines.append(line_builder(value))
        existing.add(value)
        added.append(value)
    if not lines:
        return []

    fm_start = 3
    fm_text = raw[fm_start:fm_end]
    m = re.search(r"^%s:[ \t]*(.*)$" % re.escape(key), fm_text, re.M)
    inline_val = strip_inline_comment(m.group(1)).strip() if m else ""
    if inline_val.startswith("[") and inline_val.endswith("]"):
        # NORMALIZE an inline list to block form before appending — otherwise the
        # new rows would be a mixed inline+block shape the parser ignores, so a
        # browser Add would silently vanish from sources / Topic Details even
        # though the request succeeded (CFAR: Codex).
        existing_items = [x.strip().strip('"').strip("'")
                          for x in inline_val[1:-1].split(",") if x.strip()]
        key_line_start = fm_start + m.start()
        key_line_end = fm_start + m.end()  # end of the inline line, before its \n
        block = ("%s:\n" % key
                 + "".join("  - %s\n" % json.dumps(v) for v in existing_items)
                 + "".join(lines))
        ingest_ops.atomic_write_text(path, raw[:key_line_start] + block + raw[key_line_end + 1:])
        return added
    if not m:
        insert_at = fm_end
        block = "\n%s:\n" % key + "".join(lines)
    else:
        block_start = fm_start + m.end()
        rest = raw[block_start:fm_end]
        next_key = re.search(r"\n[A-Za-z_][A-Za-z0-9_-]*:[ \t]*", rest)
        insert_at = block_start + (next_key.start() + 1 if next_key else len(rest))
        block = "".join(lines)
        if insert_at > 0 and raw[insert_at - 1] != "\n":
            block = "\n" + block
    ingest_ops.atomic_write_text(path, raw[:insert_at] + block + raw[insert_at:])
    return added


def append_sources_to_article(slug, sources, note="", supersedes=""):
    return append_frontmatter_list_items(
        slug,
        "sources",
        sources,
        lambda source: source_line(source, note, supersedes),
    )


def append_raw_documents_to_article(slug, sources):
    local_sources = [
        source for source in sources
        if source.startswith("raw/") or source.startswith("/Transpara/transpara-ai/")
    ]
    return append_frontmatter_list_items(slug, "raw_documents", local_sources, raw_document_line)


def create_article_from_source(source, note="", name=""):
    if not source.startswith("raw/"):
        return "", False
    # R6/§2.4: the OPERATOR NAME (not the doc title) drives the page — slug and
    # entity — so a new investigation is keyed on the declared subject, not on
    # whatever title the uploaded document happens to carry (CFADA-r2 #4). The
    # name has already cleared the fail-closed collision guard in
    # resolve_ingest_route; with no name (legacy/direct callers) it falls back to
    # the document title.
    entity = name or source_title_from_path(source)
    slug = slugify(entity)
    path = WIKI / ("%s.md" % slug)
    doc_id = source_doc_id_from_path(source)
    alias_lines = []
    if doc_id:
        alias_lines.append("  - %s\n" % json.dumps(doc_id))
    alias_lines.append("  - %s\n" % json.dumps(pathlib.PurePosixPath(source).stem))
    if path.exists():
        return slug, False
    today = dt.datetime.now().strftime("%Y-%m-%d")
    body_title = markdown_inline_text(entity)
    # R6: the canonical R2 skeleton — required frontmatter (render-driving fields
    # non-empty), stale_since set (so the re-derivation banner shows until an
    # authoring pass clears it), the exact awaiting-synthesis status string, NO
    # auto investigation_topic (CFADA-r21 #44), a bold Summary lead, and the five
    # required `## ` headings in canonical order. investigation_conformance() must
    # return ∅ for this skeleton (AC5/AC6).
    body = (
        "---\n"
        "entity: %s\n"
        "aliases:\n%s"
        "tier: investigation\n"
        "status: browser-ingested source; awaiting synthesis\n"
        "last_compiled: %s\n"
        "stale_since: %s\n"
        "civilization_contribution: \"Not yet assessed — awaiting curated synthesis of the ingested source.\"\n"
        "raw_documents:\n"
        "  - %s\n"
        "current_research_version: \"0.0.0\"\n"
        "sources:\n%s"
        "confidence:\n"
        "  sources: browser-ingested source document\n"
        "  claims: raw source available; article synthesis pending\n"
        "  authority: advisory; not accepted doctrine, release evidence, or Platform competitive positioning\n"
        "---\n\n"
        "# %s\n\n"
        "**%s is a browser-ingested external investigation source awaiting curated "
        "synthesis.** This page exists so the raw document is visible in the wiki "
        "navigation while article synthesis remains an explicit, governed step.\n\n"
        "## What Changed with the Research\n\n"
        "Awaiting synthesis — the raw source is listed under Topic Details.\n\n"
        "## The Boundary\n\n"
        "Awaiting synthesis. Until a curated pass runs, treat this as raw "
        "external-landscape research: not accepted doctrine, not production "
        "behavior, and not customer/demo access policy.\n\n"
        "## Capability Read\n\n"
        "Awaiting synthesis.\n\n"
        "## Benchmark Reality\n\n"
        "Awaiting synthesis.\n\n"
        "## Sources & Provenance\n\n"
        "See Topic Details and the source list for the raw ingested document(s).\n"
    ) % (
        json.dumps(entity),
        "".join(alias_lines),
        json.dumps(today),
        json.dumps(today),
        json.dumps(source),
        source_line(source, note, ""),  # a create seeds a topic; supersedes nothing (CFAR: Codex)
        body_title,
        body_title,
    )
    ingest_ops.atomic_write_text(path, body)
    return slug, True


def run_refresh_unlocked():
    # Locking is owned by the caller. The systemd timer wraps refresh.py with
    # /usr/bin/flock on this same lock file; browser authoring uses
    # wiki_write_lock() before spawning refresh.py. Keeping refresh.py lock-free
    # avoids self-deadlock while preserving cross-process exclusion.
    args = [sys.executable, str(ROOT / "compile" / "refresh.py")]
    try:
        proc = subprocess.Popen(
            args,
            cwd=str(ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
        )
        try:
            stdout, stderr = proc.communicate(timeout=240)
        except subprocess.TimeoutExpired as e:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            stdout, stderr = proc.communicate()
            stdout = stdout or (e.stdout.decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or ""))
            stderr = stderr or (e.stderr.decode("utf-8", "replace") if isinstance(e.stderr, bytes) else (e.stderr or ""))
            return {
                "ok": False,
                "returncode": None,
                "stdout": stdout[-4000:],
                "stderr": stderr[-4000:],
                "error": "refresh timed out after %s seconds" % e.timeout,
            }
    except OSError as e:
        return {
            "ok": False,
            "returncode": None,
            "stdout": "",
            "stderr": str(e),
            "error": "failed to start refresh",
        }
    return {
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout": (stdout or "")[-4000:],
        "stderr": (stderr or "")[-4000:],
    }


def run_refresh():
    with wiki_write_lock():
        return run_refresh_unlocked()


class IngestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIST), **kwargs)

    def log_message(self, fmt, *args):
        sys.stderr.write("[WikiIngest] " + fmt % args + "\n")

    def require_allowed_host(self):
        if host_header_allowed(self.headers.get("Host", ""), getattr(self.server, "server_port", None)):
            return True
        json_response(self, 421, {"error": "invalid Host header"})
        return False

    def require_authoring(self):
        supplied = self.headers.get(AUTHORING_TOKEN_HEADER, "")
        configured = bool(os.environ.get(AUTHORING_TOKEN_ENV, ""))
        if configured and authoring_allowed(self.client_address[0], supplied):
            return True
        if not configured and authoring_allowed(self.client_address[0], supplied):
            if same_origin_authoring_request(self.headers, getattr(self.server, "server_port", None)):
                return True
            json_response(self, 403, {"error": "same-origin authoring request required"})
            return False
        status = 401 if configured else 403
        json_response(self, status, {
            "error": "authoring token required" if configured else "remote authoring disabled without %s" % AUTHORING_TOKEN_ENV,
        })
        return False

    def do_GET(self):
        if not self.require_allowed_host():
            return
        if self.path == "/api/health":
            json_response(self, 200, {"ok": True})
            return
        if self.path.split("?", 1)[0] == "/api/preview":
            # deliberately STRICTER than /api/articles: full require_authoring
            # (fe-ux packet §2.3); strictly read-only — consumes nothing
            if not self.require_authoring():
                return
            try:
                params = dict(parse_qsl(urlsplit(self.path).query))
                payload = preview_payload(
                    ROOT, params.get("operation", ""),
                    params.get("slug", ""), params.get("source_ref", ""))
                json_response(self, 200, payload)
            except ingest_ops.AuthRefused as e:
                json_response(self, 403, {"error": str(e)})
            except ingest_ops.OpRefused as e:
                json_response(self, 422, {"error": str(e)})
            except Exception as e:
                json_response(self, 400, {"error": str(e)})
            return
        if self.path == "/api/articles":
            supplied = self.headers.get(AUTHORING_TOKEN_HEADER, "")
            include_sources = authoring_allowed(self.client_address[0], supplied)
            json_response(self, 200, {"articles": article_records(include_sources=include_sources)})
            return
        return super().do_GET()

    def do_POST(self):
        try:
            if not self.require_allowed_host():
                return
            if not self.require_authoring():
                return
            if self.path == "/api/rebuild":
                result = run_refresh()
                json_response(self, 200 if result["ok"] else 500, {"refresh": result})
                return
            if self.path == "/api/ingest":
                self.handle_ingest()
                return
            if self.path == "/api/replace":
                self.handle_replace()
                return
            if self.path == "/api/remove":
                self.handle_remove()
                return
            if self.path == "/api/register":
                self.handle_register()
                return
            json_response(self, 404, {"error": "unknown endpoint"})
        except ingest_ops.AuthRefused as e:
            json_response(self, 403, {"error": str(e)})
        except ingest_ops.OpRefused as e:
            json_response(self, 422, {"error": str(e)})
        except Exception as e:
            json_response(self, 400, {"error": str(e)})

    def handle_ingest(self):
        form = parse_post_form(self)
        raw_target_slug = first_value(form, "target_slug").strip()
        note = first_value(form, "note").strip()
        supersedes = first_value(form, "supersedes").strip()
        raw_external_urls = first_value(form, "external_urls")
        # R5/R6: the intent model. `new_investigation` (default OFF) is the ONLY
        # page-creation lane; its `name` — not the doc title — drives the page.
        new_investigation = form_flag(form, "new_investigation")
        raw_name = first_value(form, "name").strip()
        # quarantine BEFORE any validation, derivation, write, OR echo (packet
        # §2.4/§2.8, CFADA-r6 #16): the slug/URL validators and the refusal echoes
        # below surface the submitted value, so nothing reaches them until it is
        # proven secret-free. The operator `name` is a NEW persisted+echoed field,
        # so it JOINS the existing quarantine set (extended, never narrowed —
        # CFADA-r8 #19). Quarantine is request-content only, so it may run before
        # the lock; a refusal here saves nothing and never echoes finding bytes.
        fields = {"target_slug": raw_target_slug, "note": note,
                  "supersedes": supersedes, "external_urls": raw_external_urls,
                  "name": raw_name}
        any_document = False
        for i, item in enumerate(field_values(form, "documents")):
            if not getattr(item, "filename", ""):
                continue
            fields["filename_%d" % i] = item.filename
            data = item.file.read()
            ingest_ops.quarantine_payload(data)
            item.file = io.BytesIO(data)
            if data:
                any_document = True
        ingest_ops.quarantine_fields(fields)
        target_slug = normalize_target_slug(raw_target_slug)
        external_urls = valid_external_urls(raw_external_urls)
        # a source-less ingest (no non-empty document, no external URL) is a
        # no-op — refuse BEFORE the lock/save so it neither rebuilds nor appends
        # a misleading `add` ledger row, and creates no raw-inbox directory;
        # save_uploads would mkdir the bucket before finding nothing to save, so
        # this must precede it to stay write-free (CFAR ready-state)
        if not any_document and not external_urls:
            raise ingest_ops.OpRefused(
                "ingest requires at least one document or external URL; "
                "use /api/rebuild to only refresh")
        with wiki_write_lock():
            # ledger + edge-state preflights read SHARED state, so they must run
            # at mutation time INSIDE the lock — a preflight before the lock can
            # be stale if a concurrent op corrupts the ledger/edge state while
            # this request waits (strict-parse law; CFAR r13/r24).
            ingest_ops.ledger_preflight(ROOT / "compile" / "ingest-ledger.jsonl")
            ingest_ops.load_edge_states(ROOT / "compile" / "edge-states.json")
            # a retired topic is a tombstone — Add must not resurrect it with
            # live sources (Replace already refuses retired). Resolve the
            # EFFECTIVE target (provided slug, or the slug an unassigned upload
            # would derive) and refuse INSIDE the lock, BEFORE any write — so
            # the check is both write-free AND race-free against a concurrent
            # Remove that retires the target (CFAR r11/r12/r13/r14).
            # R1/R5/R6 fail-closed router (§2.4): "create" ONLY for an explicit
            # new investigation whose name is valid AND whose subject is proven
            # absent; "append" to an existing ACTIVE page; otherwise it raises —
            # write-free and INSIDE the lock, so retired/collision checks are
            # race-free against a concurrent Remove (CFAR r11–r14).
            route = resolve_ingest_route(
                new_investigation=new_investigation, target_slug=target_slug,
                name=raw_name, has_document=any_document)
            created_article = {"slug": "", "created": False}
            # a brand-new investigation supersedes nothing, so the create lane
            # ignores any `supersedes` the form/API carried (a stale browser
            # selection or an API field) — no misleading cross-topic provenance on
            # the seed source, extra sources, or the manifest (CFAR: Codex).
            add_supersedes = supersedes if route == "append" else ""
            if route == "create":
                # the operator NAME drives the slug (lockstep with the creator);
                # target_slug is ignored in this lane.
                target_slug = prospective_unassigned_slug(form, raw_name)
                saved = save_uploads(form, target_slug, note, add_supersedes)
                source_refs = [s["path"] for s in saved] + external_urls
                created = False
                if saved:
                    _created_slug, created = create_article_from_source(
                        saved[0]["path"], note, name=raw_name)
                created_article = {"slug": target_slug, "created": created}
            elif route == "append":
                saved = save_uploads(form, target_slug, note, add_supersedes)
                source_refs = [s["path"] for s in saved] + external_urls
            else:
                # unreachable — resolve_ingest_route returns create/append or
                # raises. A fall-through never creates or appends (fail-closed).
                raise ingest_ops.OpRefused("unresolved ingest route")
            added = append_sources_to_article(target_slug, source_refs, note, add_supersedes) if target_slug else []
            raw_added = append_raw_documents_to_article(target_slug, source_refs) if target_slug else []
            # R5/R7: an investigation ADD (or the new skeleton) stamps stale_since
            # so the reason-neutral "summary re-derivation pending" banner renders
            # until an authoring pass clears it. Non-investigation targets keep
            # today's behavior — no stale stamp (CFADA-r1 #1).
            if target_slug and article_tier(target_slug) == "investigation":
                ingest_ops.set_article_stale(ROOT, target_slug, dt.datetime.now(dt.timezone.utc))
            for url in external_urls:
                append_manifest({
                    "ingested_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                    "mode": "browser-ingest-url",
                    "target_slug": target_slug,
                    "source_url": url,
                    "note": note,
                    "supersedes": add_supersedes,  # "" for a create (CFAR: Codex)
                })
            refresh = run_refresh_unlocked()
            ingest_ops.append_ledger(ROOT / "compile" / "ingest-ledger.jsonl", {
                "ts": dt.datetime.now(dt.timezone.utc).isoformat(),
                "operation": "add",
                "slug": target_slug or "unassigned",
                "sources": source_refs,
                "created": created_article["created"],
                "rebuild": "ok" if refresh["ok"] else "failed",
            })
        json_response(self, 200 if refresh["ok"] else 500, {
            "saved": saved,
            "external_urls": external_urls,
            "created_article": created_article,
            "article_sources_added": added,
            "article_raw_documents_added": raw_added,
            "article_href": ("%s.html" % target_slug) if target_slug else "",
            "source_hrefs": [{"source": s, "href": source_href(s)} for s in source_refs],
            "refresh": refresh,
        })

    def handle_replace(self):
        form = parse_post_form(self)
        slug = first_value(form, "slug").strip()
        source_ref = first_value(form, "source_ref").strip()
        note = first_value(form, "note").strip()
        # the artifact gate fires before anything else so an unauthorized
        # request is refused 403 regardless of payload shape; replace_source
        # re-validates and consumes under the lock
        ingest_ops.load_authorization(
            ROOT / "compile" / "ingest-authorization.json",
            dt.datetime.now(dt.timezone.utc).isoformat(),
            operation="replace", slug=slug, source_ref=source_ref)
        documents = [item for item in
                     field_values(form, "document") + field_values(form, "documents")
                     if getattr(item, "filename", "")]
        if len(documents) != 1:
            raise ingest_ops.OpRefused("replace requires exactly one uploaded document")
        data = documents[0].file.read()
        with wiki_write_lock():
            # capture the timestamp INSIDE the lock so the authority window is
            # enforced at mutation time — a grant that expired while another
            # op held the lock must not be consumed (CFAR r7)
            now = dt.datetime.now(dt.timezone.utc).isoformat()
            row = ingest_ops.replace_source(
                ROOT, slug=slug, source_ref=source_ref, data=data,
                filename=documents[0].filename, note=note, now=now,
                rebuild_runner=lambda: run_refresh_unlocked().get("ok") is True)
        json_response(self, 200, {"replace": row})

    def handle_register(self):
        form = parse_post_form(self)
        slug = first_value(form, "slug").strip()
        source_ref = first_value(form, "source_ref").strip()
        note = first_value(form, "note").strip()
        # the artifact gate fires before anything else so an unauthorized
        # request is refused 403 regardless of payload shape; register_source
        # re-validates and consumes under the lock
        ingest_ops.load_authorization(
            ROOT / "compile" / "ingest-authorization.json",
            dt.datetime.now(dt.timezone.utc).isoformat(),
            operation="register", slug=slug, source_ref=source_ref)
        with wiki_write_lock():
            # timestamp INSIDE the lock so the authority window is enforced
            # at mutation time (CFAR r7)
            now = dt.datetime.now(dt.timezone.utc).isoformat()
            row = ingest_ops.register_source(
                ROOT, slug=slug, source_ref=source_ref, note=note, now=now,
                rebuild_runner=lambda: run_refresh_unlocked().get("ok") is True)
        json_response(self, 200, {"register": row})

    def handle_remove(self):
        # the retirement rationale is bound to the authorization artifact's
        # `reason`, not a request field, so the audit cannot diverge from the
        # human-approved grant (CFAR r26)
        form = parse_post_form(self)
        slug = first_value(form, "slug").strip()
        ingest_ops.load_authorization(
            ROOT / "compile" / "ingest-authorization.json",
            dt.datetime.now(dt.timezone.utc).isoformat(),
            operation="remove", slug=slug, source_ref="")
        with wiki_write_lock():
            now = dt.datetime.now(dt.timezone.utc).isoformat()  # window at mutation time (CFAR r7)
            row = ingest_ops.remove_topic(
                ROOT, slug=slug, now=now,
                rebuild_runner=lambda: run_refresh_unlocked().get("ok") is True)
        json_response(self, 200, {"remove": row})


def main():
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8798
    server = ThreadingHTTPServer((host, port), IngestHandler)
    print("serving %s with ingest API on http://%s:%d/" % (html.escape(str(DIST)), host, port))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("wiki ingest server stopped")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
