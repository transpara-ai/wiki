#!/usr/bin/env python3
"""Build the served Civilization Wiki site from wiki/*.md + index.md, Wikipedia-style.

Layout per page: persistent left sidebar (articles grouped by tier) + main column with
title, right-floated infobox (from frontmatter), auto table of contents, rendered body,
"See also", and a bottom category index navbox. Blue links resolve; red links are TBD.

No network, no LLM, no push. The repository catalog is derived from local
Transpara-AI sibling checkouts when that host-local tree is present.
"""
import re
import json
import html
import hashlib
import pathlib
import shutil
import subprocess
import urllib.parse
import markdown

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPOS_ROOT = pathlib.Path("/Transpara/transpara-ai/repos")
WIKI = ROOT / "wiki"
DIST = ROOT / "dist"
ASSETS = ROOT / "compile" / "assets"
RAW = ROOT / "raw"
STATUS = ROOT / "compile" / "refresh-status.json"
INDEX = ROOT / "index.md"
SOURCE_DIST = DIST / "source"
CSS_VER = ""
SEARCH_VER = ""
ARC_DATA_VER = ""
ARC_LAYOUT_VER = ""
ARC_DRAW_VER = ""
ARC_NAV_VER = ""
ONTO_VER = ""
PROGRESS_VER = ""
SITE_NAME = "Transpara-AI Civilization Wiki"
SOURCE_LINKS = {}
SOURCE_INDEX = []
ALLOWED_SOURCE_ROOTS = [
    ROOT,
    REPOS_ROOT / "wiki",
    REPOS_ROOT / "docs" / "dark-factory",
    REPOS_ROOT / "docs" / "civilization",
    REPOS_ROOT / "OB1",
    REPOS_ROOT / "bitsandpieces",
    REPOS_ROOT / "gstack",
    REPOS_ROOT / "solo-orchestrator",
]

THEME_JS = (
    '<script>(function(){'
    'var b=document.getElementById("theme-toggle");if(!b)return;'
    'function cur(){return document.documentElement.getAttribute("data-theme")==="light"?"light":"dark";}'
    'function lbl(){b.textContent=cur()==="light"?"☾ dark":"☀ light";}'
    'function setT(t){if(t==="light"){document.documentElement.setAttribute("data-theme","light");}'
    'else{document.documentElement.removeAttribute("data-theme");}'
    'try{localStorage.setItem("civwiki-theme",t);}catch(e){}lbl();}'
    'lbl();b.addEventListener("click",function(){setT(cur()==="light"?"dark":"light");});'
    '})();</script>'
)

NAV_JS = (
    '<script>(function(){'
    'var nav=document.querySelector(".sidebar");if(!nav)return;'
    'var store="civwiki-sidebar";'
    'function read(){try{return JSON.parse(localStorage.getItem(store)||"{}");}catch(e){return {};}}'
    'function write(s){try{localStorage.setItem(store,JSON.stringify(s));}catch(e){}}'
    'var state=read();'
    'nav.querySelectorAll(".side-group").forEach(function(d){'
    'var k=d.getAttribute("data-tier");'
    'if(Object.prototype.hasOwnProperty.call(state,k))d.open=!!state[k];'
    'else if(d.hasAttribute("data-current-group")||d.hasAttribute("data-default-open"))d.open=true;'
    'd.addEventListener("toggle",function(){var s=read();s[k]=d.open;write(s);setAllLabel();});'
    '});'
    'var saved=0;try{saved=parseInt(sessionStorage.getItem(store+"-scroll")||"0",10)||0;}catch(e){}'
    'if(saved>0)requestAnimationFrame(function(){nav.scrollTop=saved;});'
    'function saveScroll(){try{sessionStorage.setItem(store+"-scroll",String(nav.scrollTop));}catch(e){}}'
    'nav.addEventListener("scroll",saveScroll,{passive:true});'
    'nav.querySelectorAll("a").forEach(function(a){a.addEventListener("click",saveScroll);});'
    'var grip=nav.querySelector(".sidebar-resizer");var widthKey=store+"-width";'
    'function clampWidth(n){return Math.max(280,Math.min(560,n));}'
    'function applyWidth(n){n=clampWidth(n);document.documentElement.style.setProperty("--sidebar-width",n+"px");'
    'if(grip)grip.setAttribute("aria-valuenow",String(n));return n;}'
    'try{var savedWidth=parseInt(localStorage.getItem(widthKey)||"",10);if(savedWidth)applyWidth(savedWidth);}catch(e){}'
    'if(grip){var dragging=false,startX=0,startW=0;'
    'function commitWidth(n){n=applyWidth(n);try{localStorage.setItem(widthKey,String(n));}catch(e){}}'
    'grip.addEventListener("pointerdown",function(e){dragging=true;startX=e.clientX;startW=nav.getBoundingClientRect().width;'
    'try{grip.setPointerCapture(e.pointerId);}catch(ex){}document.body.classList.add("sidebar-resizing");e.preventDefault();});'
    'grip.addEventListener("pointermove",function(e){if(!dragging)return;commitWidth(startW+e.clientX-startX);});'
    'function stopDrag(){if(!dragging)return;dragging=false;document.body.classList.remove("sidebar-resizing");}'
    'grip.addEventListener("pointerup",stopDrag);grip.addEventListener("pointercancel",stopDrag);'
    'grip.addEventListener("keydown",function(e){var cur=nav.getBoundingClientRect().width;'
    'if(e.key==="ArrowLeft"){e.preventDefault();commitWidth(cur-16);}'
    'else if(e.key==="ArrowRight"){e.preventDefault();commitWidth(cur+16);}'
    'else if(e.key==="Home"){e.preventDefault();commitWidth(320);}'
    'else if(e.key==="End"){e.preventDefault();commitWidth(560);}});}'
    'var all=document.getElementById("side-toggle-all");'
    'function groups(){return Array.prototype.slice.call(nav.querySelectorAll(".side-group"));}'
    'function anyOpen(){return groups().some(function(d){return d.open;});}'
    'function setAllLabel(){if(all)all.textContent=anyOpen()?"hide":"show";}'
    'if(all)all.addEventListener("click",function(){var open=!anyOpen();'
    'var s=read();groups().forEach(function(d){d.open=open;s[d.getAttribute("data-tier")]=open;});write(s);setAllLabel();});'
    'setAllLabel();'
    '})();</script>'
)

SEARCH_JS = (
    '<script>(function(){'
    'var input=document.getElementById("wiki-search");'
    'var box=document.getElementById("search-results");'
    'if(!input||!box)return;'
    'var docs=window.CIVWIKI_SEARCH_INDEX||[];var active=-1;var hits=[];'
    'function norm(s){return String(s||"").toLowerCase().replace(/\\s+/g," ").trim();}'
    'function score(row,terms,q){var title=norm(row.title),tier=norm(row.tier),text=norm(row.text);var s=0;'
    'for(var i=0;i<terms.length;i++){var t=terms[i];'
    'if(title.indexOf(t)!==-1)s+=25;else if(tier.indexOf(t)!==-1)s+=8;'
    'else if(text.indexOf(t)!==-1)s+=3;else return -1;}'
    'if(title.indexOf(q)===0)s+=30;return s;}'
    'function excerpt(row,terms){var raw=String(row.text||"");var low=raw.toLowerCase();var ix=-1;'
    'for(var i=0;i<terms.length;i++){var p=low.indexOf(terms[i]);if(p!==-1&&(ix===-1||p<ix))ix=p;}'
    'if(ix<0)return raw.slice(0,180);var a=Math.max(0,ix-70),b=Math.min(raw.length,ix+150);'
    'return (a>0?"... ":"")+raw.slice(a,b).replace(/\\s+/g," ").trim()+(b<raw.length?" ...":"");}'
    'function setActive(n){var links=box.querySelectorAll("a.search-result");active=n;'
    'links.forEach(function(a,i){a.setAttribute("aria-selected",i===active?"true":"false");});}'
    'function hide(){box.hidden=true;box.innerHTML="";input.setAttribute("aria-expanded","false");active=-1;hits=[];}'
    'function render(){var q=norm(input.value);if(q.length<2){hide();return;}'
    'var terms=q.split(" ").filter(Boolean);hits=docs.map(function(row){return {row:row,score:score(row,terms,q)};})'
    '.filter(function(x){return x.score>=0;}).sort(function(a,b){return b.score-a.score||a.row.title.localeCompare(b.row.title);}).slice(0,10);'
    'box.innerHTML="";if(!hits.length){var empty=document.createElement("div");empty.className="search-empty";'
    'empty.textContent="No matches";box.appendChild(empty);box.hidden=false;input.setAttribute("aria-expanded","true");return;}'
    'function href(row){var h=row.href||((row.slug==="index"?"index":row.slug)+".html");'
    'if(/^https?:\\/\\//.test(h)||h.charAt(0)==="/")return h;'
    'return location.pathname.indexOf("/source/")!==-1?"../"+h:h;}'
    'hits.forEach(function(hit,i){var row=hit.row;var a=document.createElement("a");a.className="search-result";'
    'a.href=href(row);a.setAttribute("role","option");'
    'a.setAttribute("aria-selected","false");var title=document.createElement("span");title.className="search-result-title";title.textContent=row.title;'
    'var meta=document.createElement("span");meta.className="search-result-meta";meta.textContent=row.tier||"article";'
    'var ex=document.createElement("span");ex.className="search-result-excerpt";ex.textContent=excerpt(row,terms);'
    'a.appendChild(title);a.appendChild(meta);a.appendChild(ex);box.appendChild(a);});'
    'box.hidden=false;input.setAttribute("aria-expanded","true");setActive(0);}'
    'input.addEventListener("input",render);'
    'input.addEventListener("keydown",function(e){if(box.hidden)return;'
    'if(e.key==="Escape"){hide();input.blur();}'
    'else if(e.key==="ArrowDown"){e.preventDefault();setActive(Math.min(active+1,hits.length-1));}'
    'else if(e.key==="ArrowUp"){e.preventDefault();setActive(Math.max(active-1,0));}'
    'else if(e.key==="Enter"&&hits[active]){e.preventDefault();location.href=href(hits[active].row);}});'
    'document.addEventListener("click",function(e){if(!box.contains(e.target)&&e.target!==input)hide();});'
    '})();</script>'
)

TIER_ORDER = ["foundational", "institutional", "architecture", "arc", "investigation", "concept", "meta"]
TIER_LABEL = {
    "foundational": "Foundational — source philosophy",
    "institutional": "Institutional substrate",
    "architecture": "Architecture",
    "arc": "The dark-factory arc",
    "investigation": "Investigations",
    "concept": "Concepts",
    "meta": "Meta",
}

REPO_GROUP_LABEL = {
    "civilization": "Civilization",
    "platform": "Platform",
    "other": "Other",
}
REPO_GROUP_ORDER = ["civilization", "platform", "other"]

CIVILIZATION_REPOS = {
    "agent",
    "docs",
    "eventgraph",
    "hive",
    "OB1",
    "operation",
    "site",
    "wiki",
    "work",
}

PLATFORM_REPOS = {
    "af-interface",
    "ai-finance",
    "ai-sdr",
    "agentic-dev-console",
    "agentic-dev-playbook",
    "analytics-gateway",
    "ci",
    "claude-plugin",
    "claude-toolbox",
    "content",
    "CData",
    "deployment",
    "Excel-add-in",
    "extractor-file",
    "extractor-odbc",
    "extractor-opcda",
    "extractor-opchda",
    "extractor-opcua",
    "extractor-pirda",
    "extractor-pisdk",
    "extractor-telegraf",
    "inmation-interface",
    "interface-python",
    "machine-learning",
    "matlab-integration-endpoint",
    "model-builder",
    "odbc-interface",
    "ops",
    "pirda-interface",
    "platform",
    "playbooks",
    "tai-gateway",
    "tAuth",
    "tauth-scraper",
    "tCalc",
    "tevent-processor",
    "tgraph-api",
    "tgraph-controller",
    "tgraph-mcp",
    "tinstaller",
    "tinstaller-releases",
    "TransparaLegacyMigrationTool",
    "transpara-mcp",
    "transpara-py-sdk",
    "TransparaServiceManager",
    "tstore-af-plugin",
    "tstore-database",
    "tstore-interface",
    "tstudio-vibe",
    "tsystem-api",
    "tsystem-ui",
    "tsystem-watcher",
    "tview",
}

OTHER_REPOS = {
    ".github",
    "bitsandpieces",
    "lovyou-ai-summary",
    "solo-orchestrator",
    "testclaude",
    "timescale",
    "upstream-fork-sync",
}

WL = re.compile(r"\[\[([a-z0-9][a-z0-9\-]*)(?:\|([^\]]+))?\]\]")
RUNTOK = re.compile(r"@@WL(\d+)@@")


def split_fm(raw):
    if raw.startswith("---"):
        e = raw.find("\n---", 3)
        if e != -1:
            return raw[3:e].strip("\n"), raw[e + 4:].lstrip("\n")
    return "", raw


def markdown_title(body):
    m = re.search(r"^#\s+(.+?)\s*$", body or "", re.M)
    if not m:
        return ""
    return re.sub(r"\s+", " ", m.group(1)).strip().strip("#").strip()


def fm_val(fm, key):
    m = re.search(r"^%s:[ \t]*(.+)$" % re.escape(key), fm, re.M)
    return m.group(1).strip().strip('"') if m else ""


def strip_inline_comment(s):
    return split_inline_comment(s)[0]


def split_inline_comment(s):
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
            return s[:i].rstrip(), s[i + 1:].strip()
    return s.strip(), ""


def fm_list(fm, key):
    m = re.search(r"^%s:[ \t]*(.*)$" % re.escape(key), fm, re.M)
    if not m:
        return []
    inline = m.group(1).strip()
    if inline.startswith("[") and inline.endswith("]"):
        return [x.strip().strip('"') for x in inline[1:-1].split(",") if x.strip()]
    items, start = [], m.end()
    for line in fm[start:].splitlines():
        if re.match(r"^[ \t]+-\s+", line):
            items.append(strip_inline_comment(re.sub(r"^[ \t]+-\s+", "", line)).strip().strip('"').strip("'"))
        elif re.match(r"^[A-Za-z_]", line):
            break
    return items


def fm_list_with_comments(fm, key):
    m = re.search(r"^%s:[ \t]*(.*)$" % re.escape(key), fm, re.M)
    if not m:
        return []
    out = []
    inline = m.group(1).strip()
    if inline.startswith("[") and inline.endswith("]"):
        for x in inline[1:-1].split(","):
            item = x.strip().strip('"').strip("'")
            if item:
                out.append((item, ""))
        return out
    for line in fm[m.end():].splitlines():
        if re.match(r"^[ \t]+-\s+", line):
            raw_item = re.sub(r"^[ \t]+-\s+", "", line)
            value, comment = split_inline_comment(raw_item)
            value = value.strip().strip('"').strip("'")
            if value:
                out.append((value, comment))
        elif re.match(r"^[A-Za-z_]", line):
            break
    return out


def article_meta():
    meta = {}
    for p in sorted(WIKI.glob("*.md")):
        fm, _ = split_fm(p.read_text())
        meta[p.stem] = {
            "slug": p.stem,
            "title": fm_val(fm, "entity") or p.stem.replace("-", " "),
            "tier": fm_val(fm, "tier") or "concept",
        }
    return meta


META = article_meta()
SLUGS = set(META) | {"index"}


def title_of(slug):
    return META.get(slug, {}).get("title", slug.replace("-", " "))


def search_text(fm, body):
    body = re.sub(r"```.*?```", " ", body, flags=re.S)
    body = re.sub(r"`([^`]*)`", r"\1", body)
    body = WL.sub(lambda m: m.group(2) or title_of(m.group(1)), body)
    body = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", body)
    body = re.sub(r"<[^>]+>", " ", body)
    body = re.sub(r"[#*_>|~=\-]+", " ", body)
    aliases = " ".join(fm_list(fm, "aliases"))
    text = "%s %s" % (aliases, body)
    return re.sub(r"\s+", " ", text).strip()


MD = markdown.Markdown(extensions=["extra", "sane_lists", "toc"])


def run_git(path, args):
    try:
        return subprocess.check_output(
            ["git", "-C", str(path)] + list(args),
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=8,
        ).strip()
    except Exception:
        return ""


def is_transpara_ai_origin(url):
    return bool(re.search(r"github\.com[:/]transpara-ai/", url or ""))


def repo_slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "repo"


def github_web_url(url):
    url = (url or "").strip()
    if url.startswith("git@github.com:"):
        url = "https://github.com/" + url.split("git@github.com:", 1)[1]
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname != "github.com":
        return ""
    if parsed.username or parsed.password:
        return ""
    path = parsed.path
    if path.endswith(".git"):
        path = path[:-4]
    if not re.match(r"^/[^/]+/[^/]+$", path):
        return ""
    return urllib.parse.urlunsplit(("https", "github.com", path, "", ""))


def github_repo_name(url):
    web = github_web_url(url)
    if not web:
        return ""
    return web.split("github.com/", 1)[1]


def remote_label(url):
    return github_repo_name(url) or ("Remote URL redacted" if url else "")


def remote_link(url):
    web = github_web_url(url)
    if web:
        return '<a href="%s">%s</a>' % (html.escape(web), html.escape(github_repo_name(url)))
    if url:
        return '<span class="remote-redacted">Remote URL redacted</span>'
    return ""


def repo_group(name, upstream_url):
    if name in CIVILIZATION_REPOS:
        return "civilization"
    if name in PLATFORM_REPOS:
        return "platform"
    if name in OTHER_REPOS:
        return "other"
    if re.search(r"github\.com[:/]transpara/", upstream_url or ""):
        return "platform"
    return "other"


def readme_path(repo_path):
    for name in ("README.md", "readme.md", "README.markdown", "README.rst", "README.txt"):
        p = repo_path / name
        if p.exists() and p.is_file():
            return p
    return None


def local_default_branch(repo_path, remote):
    head = run_git(repo_path, ["symbolic-ref", "--quiet", "--short", "refs/remotes/%s/HEAD" % remote])
    if head.startswith(remote + "/"):
        return head
    refs = run_git(repo_path, ["for-each-ref", "--format=%(refname:short)", "refs/remotes/%s" % remote]).splitlines()
    for candidate in ("main", "master", "trunk", "develop"):
        ref = "%s/%s" % (remote, candidate)
        if ref in refs:
            return ref
    return refs[0] if refs else ""


def fork_status(repo_path, upstream_url):
    branches = run_git(repo_path, ["branch", "--format=%(refname:short)"]).splitlines()
    branch_count = len([b for b in branches if b.strip()])
    commits = run_git(repo_path, ["rev-list", "--all", "--count"]) or "0"
    if not upstream_url:
        return {
            "kind": "native",
            "text": "Transpara-AI native origin; no upstream fork remote is configured.",
            "branches": branch_count,
            "commits": commits,
            "upstream_branch": "",
            "origin_branch": local_default_branch(repo_path, "origin"),
        }
    if "example.com/disabled-upstream" in upstream_url:
        return {
            "kind": "disabled",
            "text": "Upstream fork tracking is deliberately disabled in this checkout.",
            "branches": branch_count,
            "commits": commits,
            "upstream_branch": "",
            "origin_branch": local_default_branch(repo_path, "origin"),
        }
    origin_branch = local_default_branch(repo_path, "origin")
    upstream_branch = local_default_branch(repo_path, "upstream")
    text = "Fork tracks %s." % github_repo_name(upstream_url)
    if origin_branch and upstream_branch:
        counts = run_git(repo_path, ["rev-list", "--left-right", "--count", "%s...%s" % (upstream_branch, origin_branch)])
        parts = counts.split()
        if len(parts) == 2 and all(p.isdigit() for p in parts):
            behind, ahead = parts
            text = "Fork tracks %s; %s is %s ahead / %s behind %s using local refs." % (
                github_repo_name(upstream_url), origin_branch, ahead, behind, upstream_branch)
    return {
        "kind": "fork",
        "text": text,
        "branches": branch_count,
        "commits": commits,
        "upstream_branch": upstream_branch,
        "origin_branch": origin_branch,
    }


def plain_markdown_summary(text, fallback):
    lines = []
    in_fence = False
    for raw in (text or "").splitlines():
        line = raw.strip()
        if line.startswith("```") or line.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence or not line:
            if lines:
                break
            continue
        if line.startswith(("#", "!", "[!", "|", "<")):
            continue
        if re.match(r"^[-*_]{3,}$", line):
            continue
        lines.append(line)
        if len(" ".join(lines)) > 380:
            break
    summary = " ".join(lines).strip() or fallback
    summary = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", summary)
    summary = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", summary)
    summary = re.sub(r"`([^`]*)`", r"\1", summary)
    summary = re.sub(r"[*_~>#]+", "", summary)
    summary = re.sub(r"\s+", " ", summary).strip()
    if len(summary) > 420:
        summary = summary[:417].rstrip() + "..."
    return summary or fallback


def rewrite_repo_readme_links(text, repo):
    origin_web = github_web_url(repo.get("origin", ""))
    if not origin_web:
        return text
    head = repo.get("head") or "HEAD"
    raw_base = "https://raw.githubusercontent.com/%s/%s" % (github_repo_name(repo.get("origin", "")), head)
    blob_base = "%s/blob/%s" % (origin_web, head)
    readme_dir = pathlib.PurePosixPath(repo.get("readme_rel") or "").parent
    if str(readme_dir) == ".":
        readme_dir = pathlib.PurePosixPath("")

    def resolve(href, image=False):
        href = href.strip()
        if not href or href.startswith(("#", "http://", "https://", "mailto:", "data:")):
            return href
        if href.startswith("/"):
            rel = href.strip("/")
        else:
            rel = str((readme_dir / href).as_posix())
        rel = re.sub(r"^\./", "", rel)
        return "%s/%s" % (raw_base if image else blob_base, urllib.parse.quote(rel, safe="/#?=&:%"))

    def repl(m):
        bang, label, href = m.group(1), m.group(2), m.group(3)
        return "%s[%s](%s)" % (bang, label, resolve(href, image=bang == "!"))

    return re.sub(r"(!?)\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)", repl, text)


def repo_records():
    repos = []
    if not REPOS_ROOT.exists():
        return repos
    seen = {}
    for path in sorted(REPOS_ROOT.iterdir(), key=lambda p: p.name.lower()):
        if not path.is_dir() or not (path / ".git").is_dir():
            continue
        origin = run_git(path, ["remote", "get-url", "origin"])
        if not is_transpara_ai_origin(origin):
            continue
        upstream = run_git(path, ["remote", "get-url", "upstream"])
        slug = repo_slug(path.name)
        if slug in seen:
            slug = "%s-%s" % (slug, hashlib.sha1(path.name.encode()).hexdigest()[:6])
        seen[slug] = path.name
        rp = readme_path(path)
        readme = ""
        readme_rel = ""
        if rp:
            readme = rp.read_text(errors="replace")
            readme_rel = str(rp.relative_to(path))
        status = fork_status(path, upstream)
        group = repo_group(path.name, upstream)
        repos.append({
            "name": path.name,
            "slug": slug,
            "href": "repo-%s.html" % slug,
            "path": path,
            "origin": origin,
            "upstream": upstream,
            "group": group,
            "readme": readme,
            "readme_rel": readme_rel,
            "head": run_git(path, ["rev-parse", "HEAD"]),
            "status": status,
            "summary": plain_markdown_summary(readme, "No README summary found."),
        })
    return repos


REPOS = []


def to_html(body, link_acc=None):
    MD.reset()
    store = []

    def grab(m):
        store.append((m.group(1), m.group(2)))
        return "@@WL%d@@" % (len(store) - 1)

    def emit(m):
        slug, alias = store[int(m.group(1))]
        label = html.escape(alias or title_of(slug))
        if slug in SLUGS:
            if link_acc is not None and slug != "index":
                link_acc.add(slug)
            return '<a class="wl" href="%s.html">%s</a>' % (slug, label)
        return '<a class="wl tbd" title="not yet written (TBD)">%s</a>' % label

    out = RUNTOK.sub(emit, MD.convert(WL.sub(grab, body)))
    out = sanitize_rendered_links(link_source_code_refs(out))
    return out, list(getattr(MD, "toc_tokens", []) or [])


def safe_uri(uri, *, image=False):
    uri = html.unescape(uri or "").strip()
    if not uri:
        return True
    parsed = urllib.parse.urlsplit(uri)
    if not parsed.scheme:
        return True
    scheme = parsed.scheme.lower()
    allowed = {"http", "https"} if image else {"http", "https", "mailto"}
    return scheme in allowed


def sanitize_rendered_links(body_html):
    def repl(m):
        attr = m.group(1).lower()
        quote = m.group(2)
        uri = m.group(3)
        if safe_uri(uri, image=(attr == "src")):
            return m.group(0)
        return ' %s=%s#%s data-unsafe-uri="removed"' % (attr, quote, quote)

    return re.sub(r"\s(href|src)=(['\"])(.*?)\2", repl, body_html, flags=re.I)


def safe_markdown_html(body):
    md = markdown.Markdown(extensions=["extra", "sane_lists", "toc"])
    return sanitize_rendered_links(link_source_code_refs(md.convert(html.escape(body or ""))))


def build_toc(tokens):
    def count(items):
        return sum(1 + count(i.get("children", [])) for i in items)
    if not tokens or count(tokens) < 3:
        return ""

    def render(items):
        out = "<ul>"
        for it in items:
            out += '<li><a href="#%s">%s</a>' % (it["id"], html.escape(it["name"]))
            if it.get("children"):
                out += render(it["children"])
            out += "</li>"
        return out + "</ul>"
    return '<div class="toc"><div class="toctitle">Contents</div>%s</div>' % render(tokens)


def clean_dist():
    DIST.mkdir(exist_ok=True)
    preserve = {"deploy-status.json", "inflight.json"}
    for p in DIST.iterdir():
        if p.name in preserve:
            continue
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()


def split_lead_html(body_html):
    m = re.search(r"<h[2-6]\b", body_html)
    if not m:
        return body_html, ""
    return body_html[:m.start()], body_html[m.start():]


def split_first_paragraph_html(body_html):
    m = re.search(r"</p>\s*", body_html)
    if not m:
        return body_html, ""
    return body_html[:m.end()], body_html[m.end():]


def source_ref_clean(ref):
    ref = (ref or "").strip().strip('"').strip("'")
    return ref


def source_id(ref):
    return hashlib.sha1(source_ref_clean(ref).encode("utf-8")).hexdigest()[:16]


def child_under(child, root):
    try:
        child.resolve().relative_to(root.resolve())
        return True
    except Exception:
        return False


def source_title(ref, path=None):
    if path:
        try:
            text = path.read_text(errors="replace")
            fm, body = split_fm(text)
            title = fm_val(fm, "title") or fm_val(fm, "entity") or markdown_title(body)
            version = fm_val(fm, "version")
            if title:
                if version and (" v%s" % version) not in title:
                    title = "%s v%s" % (title, version)
                return title
        except Exception:
            pass
        stem = re.sub(r"-[a-f0-9]{10,16}$", "", path.stem)
        return re.sub(r"[-_]+", " ", stem).strip() or path.name
    ref = source_ref_clean(ref)
    if ref.startswith(("http://", "https://")):
        return urllib.parse.urlparse(ref).netloc or ref
    return pathlib.PurePosixPath(ref).name or ref


def safe_source_path(ref):
    ref = source_ref_clean(ref)
    if not ref or ref.startswith(("http://", "https://")):
        return None
    if ref.startswith("raw/"):
        p = ROOT / ref
    elif ref.startswith("wiki/") or ref in {"index.md", "PROVENANCE.md", "README.md"}:
        p = ROOT / ref
    elif ref.startswith("/Transpara/transpara-ai/"):
        p = pathlib.Path(ref)
    else:
        return None
    try:
        rp = p.resolve()
    except Exception:
        return None
    if not any(child_under(rp, root) for root in ALLOWED_SOURCE_ROOTS):
        return None
    if not rp.exists() or not rp.is_file():
        return None
    if rp.suffix.lower() not in {".md", ".txt", ".json", ".yml", ".yaml", ".csv", ".toml"}:
        return None
    return rp


def source_href(ref):
    ref = source_ref_clean(ref)
    if ref.startswith(("http://", "https://")):
        return ref
    return SOURCE_LINKS.get(ref)


def raw_doc_refs(fm):
    refs = [source_ref_clean(r) for r in fm_list(fm, "raw_documents") if source_ref_clean(r)]
    if not refs:
        refs = [
            source_ref_clean(r)
            for r in fm_list(fm, "sources")
            if source_ref_clean(r) and safe_source_path(source_ref_clean(r))
        ]
    out = []
    seen = set()
    for ref in refs:
        if ref in seen:
            continue
        seen.add(ref)
        out.append(ref)
    return out


def article_frontmatter(slug):
    p = WIKI / ("%s.md" % slug)
    if not p.exists():
        return ""
    fm, _ = split_fm(p.read_text())
    return fm


def investigation_topic_for(slug, meta):
    fm = article_frontmatter(slug)
    return fm_val(fm, "investigation_topic")


def raw_doc_count_for_articles(articles):
    docs = set()
    for article in articles:
        fm = article_frontmatter(article["slug"])
        docs.update(raw_doc_refs(fm))
    return len(docs)


def source_rel_href(ref):
    href = source_href(ref)
    if href and not href.startswith(("http://", "https://")):
        return href
    return ""


def link_source_code_refs(body_html):
    def repl(m):
        text = html.unescape(m.group(1))
        href = source_rel_href(text)
        if not href:
            return m.group(0)
        return '<a class="source-code-link" href="%s"><code>%s</code></a>' % (
            html.escape(href), html.escape(text))
    return re.sub(r"<code>(raw/[^<]+?|/Transpara/transpara-ai/[^<]+?)</code>", repl, body_html)


def frontmatter_source_refs():
    refs = set()
    for p in sorted(WIKI.glob("*.md")):
        fm, _ = split_fm(p.read_text())
        for key in ("sources", "raw_documents"):
            refs.update(source_ref_clean(r) for r in fm_list(fm, key) if source_ref_clean(r))
    return refs


def source_metadata_table(fm):
    keys = [
        "document_id",
        "title",
        "subtitle",
        "version",
        "status",
        "date",
        "author",
        "reviewer",
        "owner",
        "org",
        "repo",
        "classification",
    ]
    rows = []
    for key in keys:
        val = fm_val(fm, key)
        if val:
            rows.append("<tr><th>%s</th><td>%s</td></tr>" % (html.escape(key.replace("_", " ")), html.escape(val)))
    if not rows:
        return ""
    return '<table class="source-meta-table"><tbody>%s</tbody></table>' % "".join(rows)


def render_source_document(ref, path, text):
    source_path = '<p class="source-path"><code>%s</code></p>' % html.escape(ref)
    if path and path.suffix.lower() == ".md":
        fm, body = split_fm(text)
        rendered = safe_markdown_html(body)
        return (
            "%s%s"
            '<article class="body source-body source-rendered-markdown">%s</article>'
        ) % (source_path, source_metadata_table(fm), rendered)
    return (
        "%s"
        '<article class="body source-body"><pre class="source-text"><code>%s</code></pre></article>'
    ) % (source_path, html.escape(text))


def build_source_pages(status):
    global SOURCE_LINKS, SOURCE_INDEX
    SOURCE_LINKS = {}
    SOURCE_INDEX = []
    SOURCE_DIST.mkdir(parents=True, exist_ok=True)
    refs = set(frontmatter_source_refs())
    if RAW.exists():
        for p in RAW.rglob("*"):
            if p.is_file() and p.suffix.lower() in {".md", ".txt", ".json", ".yml", ".yaml", ".csv", ".toml"}:
                refs.add(str(p.relative_to(ROOT)))

    for ref in sorted(refs):
        if ref.startswith(("http://", "https://")):
            continue
        path = safe_source_path(ref)
        if not path:
            continue
        sid = source_id(ref)
        href = "source/%s.html" % sid
        SOURCE_LINKS[ref] = href
        try:
            text = path.read_text(errors="replace")
        except Exception as e:
            text = "Unable to read source: %s" % e
        title = source_title(ref, path)
        body = render_source_document(ref, path, text)
        (SOURCE_DIST / ("%s.html" % sid)).write_text(simple_page(
            "Source — %s" % title,
            '<h1 class="page-title">%s</h1>%s' %
            (html.escape(title), body),
            status,
        ))
        SOURCE_INDEX.append({
            "slug": "source/%s" % sid,
            "href": href,
            "title": title,
            "tier": "source",
            "ref": ref,
            "text": ("%s %s %s" % (ref, title, text))[:12000],
        })


def build_source_panel(fm):
    refs = [source_ref_clean(r) for r in fm_list(fm, "sources") if source_ref_clean(r)]
    if not refs:
        return ""
    rows = []
    for ref in refs:
        href = source_href(ref)
        label = source_title(ref, safe_source_path(ref))
        if href:
            link = '<a href="%s">%s</a>' % (html.escape(href), html.escape(label))
        else:
            link = '<span class="source-unserved">%s</span>' % html.escape(label)
        rows.append('<li>%s</li>' % link)
    return (
        '<details class="source-panel">'
        '<summary>Article sources (%d)</summary>'
        '<ul>%s</ul>'
        '</details>'
    ) % (len(refs), "".join(rows))


def build_source_update_panel(fm):
    updates = []
    for ref, comment in fm_list_with_comments(fm, "sources"):
        ref = source_ref_clean(ref)
        if not ref:
            continue
        is_browser_ingest = "wiki browser ingest" in comment or ref.startswith("raw/inbox/")
        if not is_browser_ingest:
            continue
        href = source_href(ref)
        label = source_title(ref, safe_source_path(ref))
        if href:
            title = '<a href="%s">%s</a>' % (html.escape(href), html.escape(label))
        else:
            title = '<span>%s</span>' % html.escape(label)
        updates.append('<li>%s</li>' % title)
    if not updates:
        return ""
    return (
        '<section class="source-update-panel" aria-label="Ingest history">'
        '<h2>Ingest history</h2>'
        '<ul>%s</ul>'
        '</section>'
    ) % "".join(updates)


def repos_by_group():
    grouped = {k: [] for k in REPO_GROUP_ORDER}
    for repo in sorted(REPOS, key=lambda r: r["name"].lower()):
        grouped.setdefault(repo["group"], []).append(repo)
    return grouped


def build_repo_nav(current_repo=""):
    if not REPOS:
        return ""
    total = len(REPOS)
    attrs = ['class="side-group repo-side-group"', 'data-tier="repos"']
    if current_repo:
        attrs.append('data-current-group="true"')
    grouped = repos_by_group()
    out = ['<details %s><summary><span>Transpara-AI Repos</span><em>%d</em></summary>'
           '<div class="repo-nav-overview"><a%s href="repos.html">Repository index</a></div>'
           '<div class="repo-nav-sections">' %
           (" ".join(attrs), total, ' class="current"' if current_repo == "index" else "")]
    for key in REPO_GROUP_ORDER:
        repos = grouped.get(key, [])
        if not repos:
            continue
        out.append('<section class="repo-nav-section"><h6>%s</h6><ul>' % html.escape(REPO_GROUP_LABEL.get(key, key)))
        for repo in repos:
            cls = ' class="current"' if repo["slug"] == current_repo else ""
            out.append('<li><a%s href="%s">%s</a></li>' %
                       (cls, html.escape(repo["href"]), html.escape(repo["name"])))
        out.append("</ul></section>")
    out.append("</div></details>")
    return "".join(out)


def build_investigation_nav(arts, current):
    grouped = {}
    flat = []
    for article in arts:
        topic = investigation_topic_for(article["slug"], article)
        if topic:
            grouped.setdefault(topic, []).append(article)
        else:
            flat.append(article)
    out = []
    for topic in sorted(grouped, key=str.lower):
        articles = sorted(grouped[topic], key=lambda a: a["title"].lower())
        if len(articles) == 1:
            article = articles[0]
            cls = ' class="current"' if article["slug"] == current else ""
            # Preserve the count the collapsible topic group showed before collapsing.
            count = raw_doc_count_for_articles(articles)
            count_html = '<em>%d</em>' % count if count else ""
            out.append('<li class="nav-article-row"><a%s href="%s.html" title="%s">%s</a>%s</li>' %
                       (cls, article["slug"], html.escape(article["title"]), html.escape(topic), count_html))
            continue
        open_attr = " open" if any(a["slug"] == current for a in articles) else ""
        out.append(
            '<li class="nav-subgroup-item"><details class="nav-subgroup"%s>'
            '<summary><span>%s</span><em>%d</em></summary><ul>' %
            (open_attr, html.escape(topic), raw_doc_count_for_articles(articles))
        )
        for article in articles:
            cls = ' class="current"' if article["slug"] == current else ""
            out.append('<li><a%s href="%s.html">%s</a></li>' %
                       (cls, article["slug"], html.escape(article["title"])))
        out.append("</ul></details></li>")
    for article in flat:
        fm = article_frontmatter(article["slug"])
        count = len(raw_doc_refs(fm))
        cls = ' class="current"' if article["slug"] == current else ""
        count_html = '<em>%d</em>' % count if count else ""
        out.append('<li class="nav-article-row"><a%s href="%s.html">%s</a>%s</li>' %
                   (cls, article["slug"], html.escape(article["title"]), count_html))
    return "".join(out)


def build_sidebar(current, current_repo=""):
    current_tier = META.get(current, {}).get("tier", "")
    out = [
        '<nav class="sidebar" aria-label="%s navigation">' % html.escape(SITE_NAME),
        '<div class="side-tools"><strong>Contents</strong>'
        '<button id="side-toggle-all" type="button" aria-label="Hide or show all navigation sections">hide</button>'
        '</div>',
        '<div class="side-home"><a href="index.html">Main page</a><span>home</span></div>',
    ]
    out.append(build_repo_nav(current_repo))
    for tier in TIER_ORDER:
        arts = sorted([m for m in META.values() if m["tier"] == tier], key=lambda m: m["title"].lower())
        if not arts:
            continue
        attrs = ['class="side-group"', 'data-tier="%s"' % html.escape(tier)]
        if tier == current_tier:
            attrs.append('data-current-group="true"')
        elif not current and tier in {"institutional", "meta"}:
            attrs.append('data-default-open="true"')
        out.append('<details %s><summary><span>%s</span><em>%d</em></summary><ul>'
                   % (" ".join(attrs), html.escape(TIER_LABEL.get(tier, tier)), len(arts)))
        if tier == "investigation":
            out.append(build_investigation_nav(arts, current))
        else:
            for a in arts:
                cls = ' class="current"' if a["slug"] == current else ""
                out.append('<li><a%s href="%s.html">%s</a></li>' % (cls, a["slug"], html.escape(a["title"])))
        out.append("</ul></details>")
    out.append("</nav>")
    out.insert(-1, '<div class="sidebar-resizer" role="separator" aria-orientation="vertical" '
                   'aria-label="Resize navigation" aria-valuemin="280" aria-valuemax="560" '
                   'tabindex="0"></div>')
    return "".join(out)


def build_navbox():
    out = ['<nav class="navbox"><div class="navbox-title">%s — index</div><div class="navbox-body">' % html.escape(SITE_NAME)]
    for tier in TIER_ORDER:
        arts = sorted([m for m in META.values() if m["tier"] == tier], key=lambda m: m["title"].lower())
        if not arts:
            continue
        links = " · ".join('<a href="%s.html">%s</a>' % (a["slug"], html.escape(a["title"])) for a in arts)
        out.append('<div class="navbox-row"><span class="navbox-grp">%s</span><span class="navbox-list">%s</span></div>'
                   % (html.escape(TIER_LABEL.get(tier, tier)), links))
    out.append('</div></nav>')
    return "".join(out)


def build_infobox(meta, fm):
    rows = []
    def row(k, v):
        if v:
            rows.append('<tr><th>%s</th><td>%s</td></tr>' % (html.escape(k), v))
    tier = meta["tier"]
    row("Tier", '<span class="tier %s">%s</span>' % (html.escape(tier), html.escape(tier)))
    row("Status", html.escape(fm_val(fm, "status")))
    row("Last compiled", html.escape(fm_val(fm, "last_compiled")))
    aliases = fm_list(fm, "aliases")
    if aliases:
        row("Also known as", html.escape(", ".join(aliases)))
    nsrc = len(fm_list(fm, "sources"))
    if nsrc:
        row("Sources", "%d" % nsrc)
    docs = raw_doc_refs(fm)
    if docs:
        items = []
        for ref in docs:
            path = safe_source_path(ref)
            href = source_href(ref)
            label = source_title(ref, path)
            if href:
                items.append('<li><a href="%s">%s</a></li>' % (html.escape(href), html.escape(label)))
            else:
                items.append('<li><span class="source-unserved">%s</span></li>' % html.escape(label))
        row("Raw docs", '<ul class="raw-doc-links">%s</ul>' % "".join(items))
    if not rows:
        return ""
    return ('<aside class="infobox"><div class="infobox-title">%s</div><table>%s</table>'
            '<div class="infobox-foot">part of the <a href="index.html">%s</a></div></aside>'
            % (html.escape(meta["title"]), "".join(rows), html.escape(SITE_NAME)))


def build_contribution_box(fm):
    contribution = fm_val(fm, "civilization_contribution")
    if not contribution:
        return ""
    return (
        '<aside class="contribution-box" aria-label="Civilization contribution">'
        '<strong>Civilization contribution</strong>'
        '<p>%s</p>'
        '</aside>'
    ) % html.escape(contribution)


def build_repo_infobox(repo):
    rows = []

    def row(k, v):
        if v:
            rows.append('<tr><th>%s</th><td>%s</td></tr>' % (html.escape(k), v))

    status = repo["status"]
    origin = remote_link(repo["origin"])
    upstream = remote_link(repo["upstream"]) if repo["upstream"] else "None"
    status_text = status["text"]
    if status["kind"] == "native":
        status_text += " %d branches; %s total commits." % (status["branches"], status["commits"])
    row("Section", html.escape(REPO_GROUP_LABEL.get(repo["group"], repo["group"])))
    row("Description", html.escape(repo["summary"]))
    row("Origin", origin)
    row("Upstream", upstream)
    row("Status", html.escape(status_text))
    row("Branches", str(status["branches"]))
    row("Commits", html.escape(str(status["commits"])))
    if status.get("origin_branch"):
        row("Origin branch", html.escape(status["origin_branch"]))
    if status.get("upstream_branch"):
        row("Upstream branch", html.escape(status["upstream_branch"]))
    row("README", html.escape(repo["readme_rel"] or "not found"))
    row("Local path", '<code>%s</code>' % html.escape(str(repo["path"])))
    return (
        '<aside class="infobox repo-infobox">'
        '<div class="infobox-title">%s</div>'
        '<table>%s</table>'
        '<div class="infobox-foot">part of <a href="repos.html">Transpara-AI Repos</a></div>'
        '</aside>'
    ) % (html.escape(repo["name"]), "".join(rows))


def repo_readme_html(repo):
    readme = repo["readme"]
    if not readme:
        return (
            '<article class="body repo-readme">'
            '<p>No README was found in this local checkout. The repository is still listed because it is a primary '
            'Transpara-AI origin checkout under <code>/Transpara/transpara-ai/repos</code>.</p>'
            '</article>'
        )
    body = rewrite_repo_readme_links(readme, repo)
    rendered = safe_markdown_html(body)
    return '<article class="body repo-readme">%s</article>' % rendered


def repo_page(repo, status):
    title = "%s repository" % repo["name"]
    page_title = "%s — %s" % (title, SITE_NAME)
    return (
        '<!doctype html><html lang="en" data-theme="light"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>%s</title>' % html.escape(page_title) +
        '<link rel="stylesheet" href="style.css?v=%s">' % CSS_VER +
        '<script>(function(){try{var t=localStorage.getItem("civwiki-theme");'
        'if(t==="dark")document.documentElement.removeAttribute("data-theme");'
        'else document.documentElement.setAttribute("data-theme","light");}catch(e){}})();</script>'
        '</head><body>'
        '<header class="topbar"><a class="brand" href="index.html">%s</a>%s%s'
        '<div class="top-meta">%s'
        '<button id="theme-toggle" class="theme-toggle" type="button" aria-label="Toggle dark or light theme">☾ dark</button>'
        '</div></header>' % (html.escape(SITE_NAME), search_box(), top_links(), freshness(status)) +
        '<div class="layout">%s' % build_sidebar("", current_repo=repo["slug"]) +
        '<main class="content repo-content"><h1 class="page-title">%s</h1>'
        '<div class="tagline"><span class="tier repo">%s</span> · repository README</div>'
        '%s%s'
        '<footer class="page-foot">Generated from <code>%s</code> at build time. Repository metadata is local git truth.</footer>'
        '</main></div><script src="search-index.js?v=%s"></script>' %
        (
            html.escape(title),
            html.escape(REPO_GROUP_LABEL.get(repo["group"], repo["group"])),
            build_repo_infobox(repo),
            repo_readme_html(repo),
            html.escape(str(repo["path"] / (repo["readme_rel"] or "README"))),
            SEARCH_VER,
        ) +
        THEME_JS + NAV_JS + SEARCH_JS + deploy_status_script() + '</body></html>'
    )


def repos_page(status):
    grouped = repos_by_group()
    sections = []
    for key in REPO_GROUP_ORDER:
        repos = grouped.get(key, [])
        if not repos:
            continue
        rows = []
        for repo in repos:
            st = repo["status"]
            upstream = remote_label(repo["upstream"]) if repo["upstream"] else "Native origin"
            rows.append(
                '<tr><td><a href="%s">%s</a></td><td>%s</td><td>%s</td><td>%s</td></tr>' %
                (
                    html.escape(repo["href"]),
                    html.escape(repo["name"]),
                    html.escape(repo["summary"]),
                    html.escape(upstream),
                    html.escape(st["text"]),
                )
            )
        sections.append(
            '<h2 id="%s">%s</h2><table class="repo-index-table">'
            '<thead><tr><th>Repository</th><th>Description</th><th>Upstream</th><th>Status</th></tr></thead>'
            '<tbody>%s</tbody></table>' %
            (html.escape(key), html.escape(REPO_GROUP_LABEL.get(key, key)), "".join(rows))
        )
    body = (
        '<h1 class="page-title">Transpara-AI Repos</h1>'
        '<article class="body repo-index">'
        '<p>Primary Transpara-AI git checkouts under <code>/Transpara/transpara-ai/repos</code>. '
        'Generated pages render each repository README with local git metadata.</p>'
        '%s</article>' % "".join(sections)
    )
    return tool_page("Transpara-AI Repos", body, status).replace(
        build_sidebar(""), build_sidebar("", current_repo="index"), 1)


def search_box(prefix=""):
    return (
        '<form class="search" role="search" autocomplete="off">'
        '<label class="sr-only" for="wiki-search">Search %s</label>'
        '<input id="wiki-search" class="search-input" type="search" '
        'placeholder="Search %s" aria-controls="search-results" aria-expanded="false">'
        '<div id="search-results" class="search-results" role="listbox" hidden></div>'
        '</form>'
    ) % (html.escape(SITE_NAME), html.escape(SITE_NAME))


def build_seealso(links, current):
    rel = sorted((s for s in links if s != current and s in META),
                 key=lambda s: title_of(s).lower())
    if not rel:
        return ""
    items = "".join('<li><a href="%s.html">%s</a></li>' % (s, html.escape(title_of(s))) for s in rel)
    return '<section class="seealso"><h2>See also</h2><ul>%s</ul></section>' % items


def load_status():
    if STATUS.exists():
        try:
            return json.loads(STATUS.read_text())
        except Exception:
            pass
    return {}


def freshness(status):
    synced = status.get("synced", "")
    stale = status.get("stale_articles", [])
    if not synced:
        return '<span class="fresh warn">not yet refreshed</span>'
    if not stale:
        return '<span class="fresh ok">updated %s · 0 stale</span>' % html.escape(synced)
    # "stale" = articles whose cited sources changed but whose bodies have NOT been
    # re-compiled (the LLM re-compile is manual; see compile/REBUILD.md). Make the chip a
    # disclosure that names + links each stale article, so the count is actionable rather
    # than opaque. Native <details>: no JS, keyboard-accessible.
    n = len(stale)
    links = "".join(
        '<li><a href="%s.html">%s</a></li>' % (html.escape(s), html.escape(title_of(s)))
        for s in stale
    )
    return (
        '<details class="fresh-details">'
        '<summary class="fresh warn">updated %s · %d stale</summary>'
        '<div class="fresh-pop" role="group" aria-label="Stale articles">'
        '<p class="fresh-pop-head">%d article%s cite repo sources that changed but '
        'whose pages have not been re-compiled yet:</p>'
        '<ul class="fresh-pop-list">%s</ul>'
        '<p class="fresh-pop-foot">Resolving these is a manual re-compile '
        '(see <code>compile/REBUILD.md</code>) — the 15-minute deterministic refresh tracks '
        'freshness but does not rewrite article prose.</p>'
        '</div></details>'
    ) % (html.escape(synced), n, n, "" if n == 1 else "s", links)


def deploy_status_script():
    """Client-side: fetch deploy-status.json (written by autodeploy.py each tick,
    NOT baked at build time) and render a blocked banner + a live footer."""
    return (
        '<div id="deploy-banner" hidden></div>'
        '<div id="deploy-foot" class="deploy-foot"></div>'
        '<script>(function(){fetch("deploy-status.json",{cache:"no-store"})'
        '.then(function(r){return r.ok?r.json():null}).then(function(s){if(!s)return;'
        'var f=document.getElementById("deploy-foot");'
        'if(f)f.textContent="live deploy: "+String(s.deployed_sha||"").slice(0,7)+" · "+(s.checked||"");'
        'if(s.blocked){var b=document.getElementById("deploy-banner");'
        'b.hidden=false;b.className="deploy-blocked";'
        'b.textContent="\\u26a0 Auto-deploy blocked: "+s.reason+" (since "+(s.since||"?")+'
        '") \\u2014 the live site may be behind authorized main."}}).catch(function(){})})();</script>'
    )


def top_links():
    return (
        '<nav class="top-links" aria-label="Wiki tools">'
        '<a href="repos.html">Repos</a>'
        '<a href="sources.html">Sources</a>'
        '<a href="ingest.html">Ingest</a>'
        '</nav>'
    )


def simple_page(title, inner_html, status, *, main_class="content source-content"):
    return (
        '<!doctype html><html lang="en" data-theme="light"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>%s — %s</title>' % (html.escape(title), html.escape(SITE_NAME)) +
        '<link rel="stylesheet" href="../style.css?v=%s">' % CSS_VER +
        '<script>(function(){try{var t=localStorage.getItem("civwiki-theme");'
        'if(t==="dark")document.documentElement.removeAttribute("data-theme");'
        'else document.documentElement.setAttribute("data-theme","light");}catch(e){}})();</script>'
        '</head><body>'
        '<header class="topbar"><a class="brand" href="../index.html">%s</a>%s'
        '<nav class="top-links" aria-label="Wiki tools"><a href="../repos.html">Repos</a><a href="../sources.html">Sources</a><a href="../ingest.html">Ingest</a></nav>'
        '<div class="top-meta">%s'
        '<button id="theme-toggle" class="theme-toggle" type="button" aria-label="Toggle dark or light theme">☾ dark</button>'
        '</div></header>' % (html.escape(SITE_NAME), search_box(prefix="../"), freshness(status)) +
        '<main class="%s">%s'
        '<footer class="page-foot">Generated from <code>wiki/</code> + <code>raw/</code> · source viewer.</footer>'
        '</main><script src="../search-index.js?v=%s"></script>' % (html.escape(main_class), inner_html, SEARCH_VER) +
        THEME_JS + SEARCH_JS + deploy_status_script().replace('fetch("deploy-status.json"', 'fetch("../deploy-status.json"') +
        '</body></html>'
    )


def tool_page(title, inner_html, status):
    return (
        '<!doctype html><html lang="en" data-theme="light"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>%s — %s</title>' % (html.escape(title), html.escape(SITE_NAME)) +
        '<link rel="stylesheet" href="style.css?v=%s">' % CSS_VER +
        '<script>(function(){try{var t=localStorage.getItem("civwiki-theme");'
        'if(t==="dark")document.documentElement.removeAttribute("data-theme");'
        'else document.documentElement.setAttribute("data-theme","light");}catch(e){}})();</script>'
        '</head><body>'
        '<header class="topbar"><a class="brand" href="index.html">%s</a>%s%s'
        '<div class="top-meta">%s'
        '<button id="theme-toggle" class="theme-toggle" type="button" aria-label="Toggle dark or light theme">☾ dark</button>'
        '</div></header>' % (html.escape(SITE_NAME), search_box(), top_links(), freshness(status)) +
        '<div class="layout">%s<main class="content">%s'
        '<footer class="page-foot">Generated from <code>wiki/</code> + <code>raw/</code>.</footer>'
        '</main></div><script src="search-index.js?v=%s"></script>' % (build_sidebar(""), inner_html, SEARCH_VER) +
        THEME_JS + NAV_JS + SEARCH_JS + deploy_status_script() + '</body></html>'
    )


def sources_page(status):
    items = []
    for row in sorted(SOURCE_INDEX, key=lambda r: (r["title"].lower(), r["href"])):
        ref = row["ref"]
        items.append('<li><a href="%s">%s</a><code>%s</code></li>' %
                     (html.escape(row["href"]), html.escape(row["title"]), html.escape(ref)))
    return tool_page("Source Index",
                     '<h1 class="page-title">Source Index</h1>'
                     '<article class="body"><p>Served source documents cited by the wiki.</p>'
                     '<ul class="source-index">%s</ul></article>' % "".join(items),
                     status)


def ingest_page(status):
    article_options = ['<option value="">No article reference update</option>']
    for slug, meta in sorted(META.items(), key=lambda kv: kv[1]["title"].lower()):
        article_options.append('<option value="%s">%s</option>' % (html.escape(slug), html.escape(meta["title"])))
    inner = (
        '<h1 class="page-title">Wiki Source Ingest</h1>'
        '<article class="body ingest-tool">'
        '<section class="ingest-card">'
        '<h2>Batch ingest</h2>'
        '<form id="ingest-form">'
        '<label>Authoring token<input id="authoring-token" type="password" autocomplete="off" placeholder="required for non-loopback authoring"></label>'
        '<label>Target article<select name="target_slug" id="target-slug">%s</select></label>'
        '<label>Documents<input name="documents" id="documents" type="file" multiple></label>'
        '<label>External URLs<textarea name="external_urls" id="external-urls" rows="4" placeholder="https://..."></textarea></label>'
        '<label>Supersedes<select name="supersedes" id="supersedes"><option value="">No existing source selected</option></select></label>'
        '<label>Note<input name="note" id="source-note" type="text" placeholder="citation update, replacement, or placement note"></label>'
        '<div class="form-actions"><button type="submit">Ingest and rebuild</button>'
        '<button type="button" id="rebuild-now">Refresh status and rebuild</button></div>'
        '</form></section>'
        '<section class="ingest-card"><h2>Status</h2><div id="ingest-status" class="ingest-status">Ready.</div></section>'
        '</article>'
        '<script>(function(){'
        'var form=document.getElementById("ingest-form"),status=document.getElementById("ingest-status"),'
        'target=document.getElementById("target-slug"),sup=document.getElementById("supersedes"),rebuild=document.getElementById("rebuild-now"),token=document.getElementById("authoring-token");'
        'var articles={};'
        'function esc(s){return String(s==null?"":s).replace(/[&<>"]/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;","\\"":"&quot;"}[c];});}'
        'function headers(){var h={};if(token&&token.value)h["X-CivWiki-Authoring-Token"]=token.value;return h;}'
        'function renderResult(j){var parts=[];'
        'if(j.article_href)parts.push("<p><a href=\\""+esc(j.article_href)+"\\">Open updated article</a></p>");'
        'if(j.source_hrefs&&j.source_hrefs.length){parts.push("<p>Served sources:</p><ul>"+j.source_hrefs.map(function(x){return "<li><a href=\\""+esc(x.href)+"\\">"+esc(x.source)+"</a></li>";}).join("")+"</ul>");}'
        'parts.push("<pre>"+esc(JSON.stringify(j,null,2))+"</pre>");status.innerHTML=parts.join("");}'
        'function say(x){if(typeof x==="string")status.textContent=x;else renderResult(x);}'
        'function loadArticles(){fetch("/api/articles",{cache:"no-store",headers:headers()}).then(function(r){return r.ok?r.json():null}).then(function(j){'
        'if(!j){say("Authoring API unavailable. Start compile/ingest_server.py to enable browser ingest.");return;}'
        'articles={};j.articles.forEach(function(a){articles[a.slug]=a;});target.dispatchEvent(new Event("change"));}).catch(function(){say("Authoring API unavailable. Start compile/ingest_server.py to enable browser ingest.");});}'
        'loadArticles();if(token)token.addEventListener("change",loadArticles);'
        'target.addEventListener("change",function(){sup.innerHTML="<option value=\\"\\">No existing source selected</option>";'
        'var a=articles[target.value];if(!a)return;(a.sources||[]).forEach(function(s){var o=document.createElement("option");o.value=s;o.textContent=s;sup.appendChild(o);});});'
        'form.addEventListener("submit",function(e){e.preventDefault();say("Ingesting...");fetch("/api/ingest",{method:"POST",headers:headers(),body:new FormData(form)})'
        '.then(function(r){return r.json().then(function(j){if(!r.ok)throw j;return j;});}).then(say).catch(function(e){say(e);});});'
        'rebuild.addEventListener("click",function(){say("Refreshing status and rebuilding...");fetch("/api/rebuild",{method:"POST",headers:headers()})'
        '.then(function(r){return r.json().then(function(j){if(!r.ok)throw j;return j;});}).then(function(j){say(j);setTimeout(function(){location.reload();},700);}).catch(function(e){say(e);});});'
        '})();</script>'
    ) % "".join(article_options)
    return tool_page("Wiki Source Ingest", inner, status)


def page(slug, title, meta, fm, body_html, toc_tokens, links, status, *, is_home=False, extra_head="", main_class="content"):
    sidebar = build_sidebar(slug if not is_home else "")
    infobox = "" if is_home else build_infobox(meta, fm)
    toc = "" if is_home else build_toc(toc_tokens)
    seealso = "" if is_home else build_seealso(links, slug)
    source_updates = "" if is_home else build_source_update_panel(fm)
    source_panel = "" if is_home else build_source_panel(fm)
    navbox = build_navbox()
    tagline = "" if is_home else '<div class="tagline">%s%s</div>' % (
        ('<span class="tier %s">%s</span> · ' % (html.escape(meta["tier"]), html.escape(meta["tier"]))),
        "an article in the %s" % SITE_NAME)
    h1 = SITE_NAME if is_home else html.escape(title)
    page_title = SITE_NAME if is_home or title == SITE_NAME else ("%s — %s" % (title, SITE_NAME))
    if is_home:
        article_html = '<article class="body">%s</article>' % body_html
    else:
        lead_html, rest_html = split_lead_html(body_html)
        lead_intro, lead_tail = split_first_paragraph_html(lead_html)
        contribution = build_contribution_box(fm) if meta.get("tier") == "investigation" else ""
        article_html = '<article class="body">%s%s%s%s%s</article>' % (lead_intro, contribution, lead_tail, toc, rest_html)
    return (
        '<!doctype html><html lang="en" data-theme="light"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>%s</title>' % html.escape(page_title) +
        '<link rel="stylesheet" href="style.css?v=%s">' % CSS_VER +
        extra_head +
        '<script>(function(){try{var t=localStorage.getItem("civwiki-theme");'
        'if(t==="dark")document.documentElement.removeAttribute("data-theme");'
        'else document.documentElement.setAttribute("data-theme","light");}catch(e){}})();</script>'
        '</head><body>' +
        '<header class="topbar"><a class="brand" href="index.html">%s</a>%s%s'
        '<div class="top-meta">%s'
        '<button id="theme-toggle" class="theme-toggle" type="button" aria-label="Toggle dark or light theme">☾ dark</button>'
        '</div></header>' % (html.escape(SITE_NAME), search_box(), top_links(), freshness(status)) +
        '<div class="layout">%s' % sidebar +
        '<main class="%s"><h1 class="page-title">%s</h1>%s' % (html.escape(main_class), h1, tagline) +
        '%s%s%s%s%s%s' % (infobox, article_html, seealso, source_panel, source_updates, navbox) +
        '<footer class="page-foot">Generated from <code>wiki/</code> + <code>index.md</code> · '
        'a Karpathy-style LLM wiki · fail-legible: gaps are TBD, conflicts are stated.</footer>'
        '</main></div><script src="search-index.js?v=%s"></script>' % SEARCH_VER + THEME_JS + NAV_JS + SEARCH_JS +
        deploy_status_script() +
        '</body></html>'
    )


def arc_page(status):
    slug = "civilization-arc"
    p = WIKI / ("%s.md" % slug)
    meta = META.get(slug, {"title": "Civilization Progress Chart", "tier": "meta"})
    fm, body = split_fm(p.read_text() if p.exists() else "# Civilization Progress Chart\n")
    body = re.sub(r"^#\s+.*\n", "", body, count=1)
    links = set()
    body_html, toc_tokens = to_html(body, links)
    arc_scripts = (
        '<script defer src="civilizationOntology.js?v=%s"></script>'
        '<script defer src="civilizationArcData.js?v=%s"></script>'
        '<script defer src="civilizationProgressEvidence.js?v=%s"></script>'
        '<script defer src="civilizationArcLayout.js?v=%s"></script>'
        '<script defer src="civilizationArcDraw.js?v=%s"></script>'
        '<script defer src="civilizationArcNav.js?v=%s"></script>'
        % (ONTO_VER, ARC_DATA_VER, PROGRESS_VER, ARC_LAYOUT_VER, ARC_DRAW_VER, ARC_NAV_VER)
    )
    chart = (
        '<section class="wiki-arc-embed" aria-label="Civilization progress chart">'
        '<h2 id="progress-chart">Progress chart</h2>'
        '<p class="wiki-arc-note">This chart is a read lens over the wiki and operation exports. '
        'It is display-only; it is not EventGraph truth, certification evidence, or release authority.</p>'
        '<div data-civilization-arc-nav data-arc-standalone="true" data-arc-live="true"></div>'
        '</section>'
    )
    return page(slug, meta["title"], meta, fm, body_html + chart, toc_tokens, links, status,
                extra_head=arc_scripts, main_class="content arc-content")


def build():
    global CSS_VER, SEARCH_VER, ARC_DATA_VER, ARC_LAYOUT_VER, ARC_DRAW_VER, ARC_NAV_VER, ONTO_VER, PROGRESS_VER, REPOS
    REPOS = repo_records()
    DIST.mkdir(exist_ok=True)
    status = load_status()

    def copy_asset(name):
        asset = (ASSETS / name).read_text()
        (DIST / name).write_text(asset)
        return hashlib.md5(asset.encode()).hexdigest()[:8]

    def build_search_index():
        docs = []
        fm, body = split_fm(INDEX.read_text())
        docs.append({
            "slug": "index",
            "title": SITE_NAME,
            "tier": "front page",
            "text": search_text(fm, body)[:12000],
        })
        for p in sorted(WIKI.glob("*.md")):
            fm, body = split_fm(p.read_text())
            meta = META[p.stem]
            docs.append({
                "slug": p.stem,
                "title": meta["title"],
                "tier": meta["tier"],
                "text": search_text(fm, body)[:12000],
            })
        for repo in REPOS:
            docs.append({
                "slug": "repo-%s" % repo["slug"],
                "href": repo["href"],
                "title": "%s repository" % repo["name"],
                "tier": "repo/%s" % repo["group"],
                "text": ("%s %s %s %s %s" % (
                    repo["name"],
                    REPO_GROUP_LABEL.get(repo["group"], repo["group"]),
                    repo["summary"],
                    repo["status"]["text"],
                    search_text("", repo["readme"]),
                ))[:12000],
            })
        docs.extend(SOURCE_INDEX)
        asset = "window.CIVWIKI_SEARCH_INDEX=" + json.dumps(docs, ensure_ascii=False, separators=(",", ":")) + ";\n"
        (DIST / "search-index.js").write_text(asset)
        return hashlib.md5(asset.encode()).hexdigest()[:8]

    clean_dist()
    CSS_VER = copy_asset("style.css")
    # First pass populates SOURCE_INDEX for search; second pass refreshes source
    # pages after SEARCH_VER is known so the normal page chrome uses cache-busted JS.
    build_source_pages(status)
    SEARCH_VER = build_search_index()
    build_source_pages(status)
    ONTO_VER = copy_asset("civilizationOntology.js")
    ARC_DATA_VER = copy_asset("civilizationArcData.js")
    PROGRESS_VER = copy_asset("civilizationProgressEvidence.js")
    ARC_LAYOUT_VER = copy_asset("civilizationArcLayout.js")
    ARC_DRAW_VER = copy_asset("civilizationArcDraw.js")
    ARC_NAV_VER = copy_asset("civilizationArcNav.js")
    count = 0
    for p in sorted(WIKI.glob("*.md")):
        fm, body = split_fm(p.read_text())
        meta = META[p.stem]
        body = re.sub(r"^#\s+.*\n", "", body, count=1)
        links = set()
        body_html, toc_tokens = to_html(body, links)
        (DIST / ("%s.html" % p.stem)).write_text(
            page(p.stem, meta["title"], meta, fm, body_html, toc_tokens, links, status))
        count += 1
    fm, body = split_fm(INDEX.read_text())
    body = re.sub(r"^#\s+.*\n", "", body, count=1)
    body_html, _ = to_html(body, set())
    (DIST / "index.html").write_text(
        page("index", SITE_NAME, {}, "", body_html, [], set(), status, is_home=True))
    (DIST / "sources.html").write_text(sources_page(status))
    (DIST / "ingest.html").write_text(ingest_page(status))
    (DIST / "repos.html").write_text(repos_page(status))
    for repo in REPOS:
        (DIST / repo["href"]).write_text(repo_page(repo, status))
    arc_html = arc_page(status)
    (DIST / "civilization-arc.html").write_text(arc_html)
    (DIST / "civilization_arc.html").write_text(arc_html)
    print("built %d articles + %d repo pages + index + arc -> %s" % (count, len(REPOS), DIST))


if __name__ == "__main__":
    build()
