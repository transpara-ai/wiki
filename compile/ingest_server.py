#!/usr/bin/env python3
"""Local authoring server for the Civilization Wiki.

Serves dist/ like http.server, plus small write endpoints used by ingest.html:
  GET  /api/articles
  POST /api/ingest
  POST /api/rebuild

The durable state is still the repository: uploaded documents are written under
raw/inbox/, optional article references are appended to wiki/<slug>.md
frontmatter, and compile/refresh.py regenerates freshness status and dist/.
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


def fm_list(fm, key):
    m = re.search(r"^%s:[ \t]*(.*)$" % re.escape(key), fm, re.M)
    if not m:
        return []
    inline = m.group(1).strip()
    if inline.startswith("[") and inline.endswith("]"):
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


def article_records(include_sources=True):
    out = []
    for p in sorted(WIKI.glob("*.md")):
        fm, _, _ = split_fm(p.read_text())
        out.append({
            "slug": p.stem,
            "title": fm_val(fm, "entity") or p.stem.replace("-", " "),
            "tier": fm_val(fm, "tier") or "concept",
            "sources": fm_list(fm, "sources") if include_sources else [],
        })
    return out


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
    configured_token = configured_token if configured_token is not None else os.environ.get(AUTHORING_TOKEN_ENV, "")
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
            dst.write_bytes(data)
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
    RAW_INBOX.mkdir(parents=True, exist_ok=True)
    with MANIFEST.open("a") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")


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
    m = re.search(r"^%s:[ \t]*.*$" % re.escape(key), fm_text, re.M)
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
    path.write_text(raw[:insert_at] + block + raw[insert_at:])
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


def create_article_from_source(source, note="", supersedes=""):
    if not source.startswith("raw/"):
        return "", False
    title = source_title_from_path(source)
    slug = slugify(title)
    path = WIKI / ("%s.md" % slug)
    doc_id = source_doc_id_from_path(source)
    alias_lines = []
    if doc_id:
        alias_lines.append("  - %s\n" % json.dumps(doc_id))
    alias_lines.append("  - %s\n" % json.dumps(pathlib.PurePosixPath(source).stem))
    if path.exists():
        return slug, False
    today = dt.datetime.now().strftime("%Y-%m-%d")
    body_title = markdown_inline_text(title)
    body = (
        "---\n"
        "entity: %s\n"
        "aliases:\n%s"
        "tier: investigation\n"
        "status: browser-ingested source; awaiting synthesis\n"
        "last_compiled: %s\n"
        "investigation_topic: %s\n"
        "civilization_contribution: \"Not directly included, but used as reference.\"\n"
        "raw_documents:\n"
        "  - %s\n"
        "sources:\n%s"
        "confidence:\n"
        "  sources: browser-ingested source document\n"
        "  claims: raw source available; article synthesis pending\n"
        "  authority: advisory; not accepted doctrine, release evidence, or Platform competitive positioning\n"
        "---\n\n"
        "# %s\n\n"
        "**%s** is a browser-ingested external investigation source. This page "
        "exists so the document is visible in the wiki navigation while curated "
        "article synthesis remains explicit.\n\n"
        "## Placement\n\n"
        "The source is held as Civilization external-landscape research until a "
        "curated article states a narrower placement. It is not accepted doctrine, "
        "not production behavior, and not customer/demo access policy.\n\n"
        "## Source Access\n\n"
        "Use the raw document link in the right rail or the article source list to "
        "open the formatted source document.\n"
    ) % (
        json.dumps(title),
        "".join(alias_lines),
        json.dumps(today),
        json.dumps(title),
        json.dumps(source),
        source_line(source, note, supersedes),
        body_title,
        body_title,
    )
    path.write_text(body)
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
            json_response(self, 404, {"error": "unknown endpoint"})
        except Exception as e:
            json_response(self, 400, {"error": str(e)})

    def handle_ingest(self):
        form = parse_post_form(self)
        target_slug = normalize_target_slug(first_value(form, "target_slug"))
        note = first_value(form, "note").strip()
        supersedes = first_value(form, "supersedes").strip()
        external_urls = valid_external_urls(first_value(form, "external_urls"))
        with wiki_write_lock():
            saved = save_uploads(form, target_slug, note, supersedes)
            source_refs = [s["path"] for s in saved] + external_urls
            created_article = {"slug": "", "created": False}
            if not target_slug and saved:
                target_slug, created = create_article_from_source(saved[0]["path"], note, supersedes)
                created_article = {"slug": target_slug, "created": created}
            added = append_sources_to_article(target_slug, source_refs, note, supersedes) if target_slug else []
            raw_added = append_raw_documents_to_article(target_slug, source_refs) if target_slug else []
            for url in external_urls:
                append_manifest({
                    "ingested_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                    "mode": "browser-ingest-url",
                    "target_slug": target_slug,
                    "source_url": url,
                    "note": note,
                    "supersedes": supersedes,
                })
            refresh = run_refresh_unlocked()
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
