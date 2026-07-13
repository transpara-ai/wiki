#!/usr/bin/env python3
"""Build the served Civilization Wiki site from wiki/*.md + index.md, Wikipedia-style.

Layout per page: persistent left sidebar (articles grouped by tier) + main column with
title, right-floated infobox (from frontmatter), auto table of contents, rendered body,
"See also", and a bottom category index navbox. Blue links resolve; red links are TBD.

No network, no LLM, no push. The repository catalog is derived from local
Transpara-AI sibling checkouts when that host-local tree is present.
"""
import os
import re
import json
import html
import datetime
import hashlib
import functools
import pathlib
import subprocess
import sys
import urllib.parse
from html.parser import HTMLParser
import markdown

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ingest_ops  # noqa: E402

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
ARC_VIEW_VER = ""
ONTO_VER = ""
PROGRESS_VER = ""
SITE_NAME = "Transpara-AI Civilization Wiki"
SOURCE_LINKS = {}
SOURCE_INDEX = []
GENERATED_DIST_PATHS = set()
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

# org/section structure lives in the side-effect-free org_structure module —
# the single source shared with ingest_server (DP-20260710 D1); TIER_ORDER /
# TIER_LABEL keep their names here so existing consumers are unchanged.
from org_structure import (  # noqa: E402
    TIER_ORDER, TIER_LABEL, ORG_ORDER, ORG_LABEL, ORG_SECTIONS,
    SECTION_LABEL, DEFAULT_ORG, ORG_REPO_GROUPS, resolve_org_tier)

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


def fm_scalar(fm, key):
    """A frontmatter scalar with any inline comment stripped BEFORE quote removal,
    so `entity: Foo # note` reads as `Foo` and a comment-only `entity: # TODO`
    reads as empty. Use this wherever a scalar's VALUE is load-bearing — grouping,
    conformance emptiness, the primary flag — so a normal inline comment can't
    pollute the value (CFAR: Codex)."""
    m = re.search(r"^%s:[ \t]*(.+)$" % re.escape(key), fm, re.M)
    if not m:
        return ""
    return strip_inline_comment(m.group(1)).strip().strip('"').strip("'")


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
    inline = strip_inline_comment(m.group(1)).strip()  # a trailing `# comment` on an
    if inline.startswith("[") and inline.endswith("]"):  # inline list must not hide it
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
    inline = strip_inline_comment(m.group(1)).strip()
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
        # fail-closed org/tier resolution (DP-20260710 D3): a present-but-
        # empty/unknown org, a missing tier, or a tier foreign to the resolved
        # org kills the build loudly — there is no silent `concept` fallback.
        # Absent org defaults to DEFAULT_ORG so the existing corpus needs no
        # frontmatter edits (corpus-evidenced: all pages carry explicit tiers).
        org_present = bool(re.search(r"(?m)^org\s*:", fm))
        try:
            org, tier = resolve_org_tier(
                p.stem, org_present, fm_scalar(fm, "org"), fm_scalar(fm, "tier"))
        except ValueError as exc:
            raise SystemExit("article_meta: %s" % exc)
        meta[p.stem] = {
            "slug": p.stem,
            # fm_scalar for the value-load-bearing title/tier (a commented
            # `tier: investigation # x` must still gate the TOC, nav group, and
            # contribution box); retired_on stays fm_val so an ambiguous/comment-
            # only value still drops the page from nav (fail-safe) (CFAR: Codex).
            "title": fm_scalar(fm, "entity") or p.stem.replace("-", " "),
            "tier": tier,
            "org": org,
            "retired_on": fm_val(fm, "retired_on"),
        }
    return meta


META = article_meta()
SLUGS = set(META) | {"index"}

# Committed edge-state truth (per-ingestion ops packet §2.7). The strict
# loader FAILS the build on corrupt/duplicate/unreadable state — bad state is
# never treated as empty. The env override exists so tests can prove the
# failure path against the real builder without touching the repo's file.
EDGE_STATES_PATH = pathlib.Path(
    os.environ.get("CIVWIKI_EDGE_STATES", "")
    or (ROOT / "compile" / "edge-states.json"))
EDGE_STATES = ingest_ops.load_edge_states(EDGE_STATES_PATH)


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


def to_html(body, link_acc=None, source_refs=None, source_slug=""):
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
    out = link_source_code_refs(out)
    out = link_source_code_alias_refs(out, source_refs or [])
    out = link_source_alias_refs(out, source_refs or [])
    out = sanitize_rendered_links(out)
    out = gate_internal_links(out, source_slug)
    return out, list(getattr(MD, "toc_tokens", []) or [])


WL_PENDING = '<span class="wl wl-pending" title="pending reconciliation">%s</span>'


def _internal_link_disposition(href, source_slug, repo_slugs):
    """Return ('live'|'plain'|'pending'|None). None = not an internal article
    link (external / builder page) — leave it alone."""
    kind, target = ingest_ops.canonical_article_target(
        href, meta=META, repo_slugs=repo_slugs)
    if kind in ("external", "page"):
        return None
    if kind == "article":
        state = ingest_ops.link_state(source_slug, target, META, EDGE_STATES)
        if state == "live":
            return "live"
        if state == "plain":
            return "plain"
        return "pending"
    return "pending"  # unknown internal target — never renders live


class _LinkGate(HTMLParser):
    """Rewrites ONLY genuine anchor href attributes. Everything else — text,
    inline code, other tags, other attributes (title/aria that merely mention
    an href) — is echoed verbatim, so valid content is never corrupted (CFAR
    r8) while a browser-resolved href (quoted, unquoted, or entity-encoded,
    per HTMLParser's own attribute parsing) is always gated (CFAR r1/r2/r4/r5/
    r6). This is the single fail-closed enforcement point (packet §2.7)."""

    # SVG anchors target xlink:href (SVG 1.1) or href (SVG 2); browsers follow
    # either, so both are link attributes the gate must inspect (CFAR r17)
    HREF_ATTRS = ("href", "xlink:href")

    def __init__(self, source_slug, repo_slugs):
        super().__init__(convert_charrefs=False)
        self.source_slug = source_slug
        self.repo_slugs = repo_slugs
        self.out = []
        self.a_stack = []  # disposition of each open <a>: keep|drop|pending

    def _disp(self, attrs):
        # an element may carry more than one browser-followed link attribute
        # (e.g. an SVG <a> with both href and xlink:href) — evaluate EVERY one
        # and fail closed if ANY points to a non-live internal target, so a
        # live href cannot shield a retired xlink:href (CFAR r21)
        dispositions = [
            _internal_link_disposition(v, self.source_slug, self.repo_slugs)
            for (k, v) in attrs
            if k.lower() in self.HREF_ATTRS and v is not None]
        if not dispositions:
            return None
        if all(d in (None, "live") for d in dispositions):
            return "live"
        if any(d == "pending" for d in dispositions):
            return "pending"
        return "plain"  # some cleanly-removed, none pending

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            disp = self._disp(attrs)
            if disp is None or disp == "live":
                self.out.append(self.get_starttag_text())
                self.a_stack.append("keep")
            elif disp == "plain":
                self.a_stack.append("drop")  # emit inner text, drop the anchor
            else:
                self.out.append(WL_PENDING.split("%s")[0])
                self.a_stack.append("pending")
            return
        if tag == "area":
            # <area> (image map) is a void, browser-navigable href element —
            # drop it when its target is non-live; there is no inner content
            # to preserve (CFAR r18)
            disp = self._disp(attrs)
            if disp is None or disp == "live":
                self.out.append(self.get_starttag_text())
            return
        self.out.append(self.get_starttag_text())

    def handle_endtag(self, tag):
        if tag == "a" and self.a_stack:
            disp = self.a_stack.pop()
            if disp == "keep":
                self.out.append("</a>")
            elif disp == "pending":
                self.out.append(WL_PENDING.split("%s")[1])
            return  # drop: emit nothing for the closing tag
        self.out.append("</%s>" % tag)

    def handle_startendtag(self, tag, attrs):
        # browsers ignore the `/` on a non-void `<a .../>` in text/html and
        # keep the link live, so a self-closing anchor must be gated too, not
        # echoed verbatim (CFAR r9). A non-live self-closing anchor/area is
        # dropped — there is no inner span to wrap.
        if tag in ("a", "area"):
            disp = self._disp(attrs)
            if disp is None or disp == "live":
                self.out.append(self.get_starttag_text())
            return
        self.out.append(self.get_starttag_text())

    def handle_data(self, data):
        self.out.append(data)

    def handle_entityref(self, name):
        self.out.append("&%s;" % name)

    def handle_charref(self, name):
        self.out.append("&#%s;" % name)

    def handle_comment(self, data):
        self.out.append("<!--%s-->" % data)

    def handle_decl(self, decl):
        self.out.append("<!%s>" % decl)

    def handle_pi(self, data):
        self.out.append("<?%s>" % data)

    def result(self):
        # close any anchors left open by malformed input (fail-closed: a
        # pending span must never leak unclosed)
        while self.a_stack:
            if self.a_stack.pop() == "pending":
                self.out.append(WL_PENDING.split("%s")[1])
        return "".join(self.out)


def gate_internal_links(body_html, source_slug=""):
    """The single enforcement point of the fail-closed rendering law
    (per-ingestion ops packet §2.7): EVERY anchor in rendered article HTML —
    wikilink-emitted, markdown, or raw author HTML — renders live ONLY when
    its canonical internal target is proven valid. Retired targets, dangling
    or unknown edge states, and unknown internal targets render non-live;
    cleanly-removed edges render plain text. Parsed with an HTML tokenizer so
    only real href attributes are touched — never prose, code, or other
    attributes that merely mention an href."""
    gate = _LinkGate(source_slug, {repo["slug"] for repo in REPOS})
    gate.feed(body_html)
    gate.close()
    return gate.result()


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


def article_toc(meta, toc_tokens, is_home=False):
    # R4 (Investigation Topic Standard): tier: investigation pages render no
    # in-topic Table of Contents; every other tier keeps its Contents box.
    if is_home or (meta or {}).get("tier") == "investigation":
        return ""
    return build_toc(toc_tokens)


def state_banner_html(fm):
    # Retired takes precedence over stale. R7: the stale-since wording is
    # reason-neutral ("raw sources changed; summary re-derivation pending"), so it
    # is correct for an unauthenticated ADD as well as a Replace — the old text
    # ("raw sources were replaced ... pending authorization") was false for an ADD.
    retired_on = fm_val(fm, "retired_on")
    if retired_on:
        return ('<div class="article-state-banner">Retired on %s — %s</div>'
                % (html.escape(retired_on),
                   html.escape(fm_val(fm, "retired_reason") or "no reason recorded")))
    stale_since = fm_val(fm, "stale_since")
    if stale_since:
        return ('<div class="article-state-banner">Synthesis stale since %s'
                ' — raw sources changed; summary re-derivation pending.</div>'
                % html.escape(stale_since))
    return ""


def mark_generated(path):
    GENERATED_DIST_PATHS.add(path.resolve())


def write_dist_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    mark_generated(path)


def prepare_dist():
    source_link_aliases.cache_clear()
    GENERATED_DIST_PATHS.clear()
    DIST.mkdir(exist_ok=True)
    SOURCE_DIST.mkdir(parents=True, exist_ok=True)


def prune_dist():
    preserve = {"deploy-status.json", "inflight.json"}
    for p in sorted(DIST.rglob("*"), key=lambda x: len(x.parts), reverse=True):
        if p.is_dir():
            try:
                p.rmdir()
            except OSError:
                pass
            continue
        if p.parent == DIST and p.name in preserve:
            continue
        if p.resolve() not in GENERATED_DIST_PATHS:
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


def is_raw_ingested_research(ref):
    """R3/§2.2: a Topic-Details-eligible ref is a raw INGESTED RESEARCH file — a
    browser-ingest upload under raw/inbox/, or a TAI-RES evaluation (tai-res-*.md)
    wherever placed (e.g. pageindex's external-landscape path). Doctrine/
    provenance citations (raw/transpara/, raw/open-brain/, index/PROVENANCE),
    absolute /Transpara/ paths, and external URLs are NOT Topic Details — they
    render in the source panel. Allowlist direction: only the two proven-eligible
    forms qualify; everything unknown is excluded (fail-closed)."""
    ref = source_ref_clean(ref)
    if not ref:
        return False
    low = ref.lower()
    if low.startswith(("http://", "https://")):
        return False
    if low.startswith("raw/inbox/"):
        return True
    # a TAI-RES evaluation qualifies only as a RELATIVE raw/ path (wherever under
    # raw/ it sits, e.g. raw/civilization/external-landscape/tai-res-*.md).
    # Absolute /Transpara/ paths and every other non-raw/ ref are doctrine/
    # provenance citations that stay in the source panel, so reject them BEFORE
    # the basename allowlist admits a bare tai-res-*.md filename (CFAR: Codex).
    if not low.startswith("raw/"):
        return False
    base = low.rsplit("/", 1)[-1]
    return base.startswith("tai-res-") and base.endswith(".md")


def topic_details_refs(fm):
    """R3: the ordered, deduped ref list for the Topic Details infobox row —
    raw_documents UNION superseded_raw_documents UNION superseded_sources, filtered
    to raw-ingested-research refs. Replace moves a superseded ref into
    superseded_raw_documents, OR — for a legacy page whose ingested doc lived only
    under `sources` — into superseded_sources; both superseded keys are unioned so
    R3's "every raw ingested version" holds for that path too (CFAR: Codex, an
    extension of §2.2's two-key mechanism to be formalized in the Phase-2 packet).
    When all are empty, fall back to the raw-ingested-research refs among `sources`
    (so an un-retrofitted page keeps its ingested-file links); a support-only page
    whose sources are all doctrine gets an EMPTY row (§2.2)."""
    union = (fm_list(fm, "raw_documents")
             + fm_list(fm, "superseded_raw_documents")
             + fm_list(fm, "superseded_sources"))
    refs = [source_ref_clean(r) for r in union if source_ref_clean(r)]
    refs = [r for r in refs if is_raw_ingested_research(r)]
    if not refs:
        refs = [
            source_ref_clean(r)
            for r in fm_list(fm, "sources")
            if is_raw_ingested_research(source_ref_clean(r))
        ]
    out, seen = [], set()
    for ref in refs:
        if ref not in seen:
            seen.add(ref)
            out.append(ref)
    return out


def topic_details_superseded(fm):
    """Refs a newer version supersedes: the `superseded_raw_documents` AND
    `superseded_sources` keys (Replace moves a superseded ref into one or the
    other) UNION the `supersedes:` targets annotated on `sources` (an
    ADD-with-supersedes topic keeps all versions in raw_documents and marks
    supersession only in the comments — CFADA-r21 #43). The non-superseded
    ref(s) render as the current primary."""
    superseded = {
        source_ref_clean(r)
        for key in ("superseded_raw_documents", "superseded_sources")
        for r in fm_list(fm, key)
        if source_ref_clean(r)
    }
    for _ref, comment in fm_list_with_comments(fm, "sources"):
        old = _supersedes_target(comment)
        if old:
            superseded.add(old)
    return superseded


# ---- Raw Area (FO-WIKI-RAW-AREA v0.7.4 / DF-DESIGN-WIKI-RAW-AREA v0.7.6) ----
# One generated tools page (raw.html) listing every raw ingested research file.
# Membership requires positive ingestion evidence; the manifest reader applies
# a design-local default-deny contract; every anomaly surfaces in a footer and
# a build warning line. Display-only: no ingest op, no raw/** byte is touched.

RAW_AREA_FILE_ROW_KEYS = frozenset(
    ("ingested_at", "mode", "target_slug", "source_path", "sha256",
     "original_name", "note", "supersedes"))
RAW_AREA_URL_ROW_KEYS = frozenset(
    ("ingested_at", "mode", "target_slug", "source_url", "note", "supersedes"))
RAW_AREA_BLANKABLE = frozenset(("note", "supersedes", "target_slug"))
# the browser-upload storage grammar: <stem>-<sha12><suffix> (ANY suffix; the
# writer preserves the original suffix, ingest_server.py:634-666)
RAW_AREA_UPLOAD_RE = re.compile(r"^(?P<stem>.+)-(?P<sha12>[0-9a-f]{12})(?P<suffix>\.[^./\\]+)$")
RAW_AREA_INBOX_DATE_RE = re.compile(r"^raw/inbox/(\d{4}-\d{2}-\d{2})/.")
RAW_AREA_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def raw_area_printable(text):
    """Anomaly strings cross two sinks — terminal warning lines and the
    rendered page. Backslash-escape C0 controls, DEL, and lone surrogates so
    a hostile filename or manifest value can neither crash UTF-8 encoding at
    either sink nor forge extra one-per-anomaly warning lines (CFAR r4)."""
    out = []
    for ch in text:
        code = ord(ch)
        if code < 32 or code == 127:
            out.append("\\x%02x" % code)
        elif 0xD800 <= code <= 0xDFFF:
            out.append("\\u%04x" % code)
        else:
            out.append(ch)
    return "".join(out)


def _raw_area_pairs_no_dup(pairs):
    seen = set()
    for key, _ in pairs:
        if key in seen:
            raise ValueError("duplicate key: %s" % key)
        seen.add(key)
    return dict(pairs)


def raw_area_parse_row(line, container, rank, lineno):
    """Design-local default-deny row validation (packet D5). Returns
    (row|None, anomaly|None). Parse-level lanes first (blank line, undecodable
    JSON, non-object top level), then duplicate keys, exact key-set shape,
    types, blankability, 64-hex sha, timezone-aware ingested_at. A row that
    fits no lane is rejected — never coerced."""
    where = "%s line %d" % (container, lineno)
    if not line.strip():
        return None, "blank manifest line (%s)" % where
    try:
        obj = json.loads(line, object_pairs_hook=_raw_area_pairs_no_dup)
    except (ValueError, RecursionError) as exc:
        # RecursionError: a deeply nested but valid JSON value must reject
        # the row, never terminate the build (CFAR r1).
        return None, "unreadable manifest line (%s): %s" % (where, type(exc).__name__)
    if not isinstance(obj, dict):
        return None, "non-object manifest line (%s)" % where
    keys = frozenset(obj)
    if keys == RAW_AREA_FILE_ROW_KEYS:
        shape = "file"
    elif keys == RAW_AREA_URL_ROW_KEYS:
        shape = "url"
    else:
        return None, "unknown row shape (%s): keys %s" % (where, ",".join(sorted(keys)))
    for key, value in obj.items():
        if not isinstance(value, str):
            return None, "non-string field %s (%s)" % (key, where)
        if not value.strip() and key not in RAW_AREA_BLANKABLE:
            return None, "blank required field %s (%s)" % (key, where)
        try:  # an escaped lone surrogate (e.g. "\ud800") would survive here
            # and abort the build later at write_dist_text (CFAR r2)
            value.encode("utf-8")
        except UnicodeEncodeError:
            return None, "unencodable field %s (%s)" % (key, where)
    if shape == "file" and not RAW_AREA_SHA256_RE.match(obj["sha256"]):
        return None, "sha256 is not 64-hex (%s)" % where
    try:
        stamp = datetime.datetime.fromisoformat(obj["ingested_at"])
    except ValueError:
        return None, "unparseable ingested_at (%s)" % where
    if stamp.tzinfo is None:
        return None, "naive ingested_at (%s)" % where
    try:  # normalize NOW: a boundary offset (e.g. 0001-01-01T00:00:00+23:59)
        # overflows astimezone later and would abort the build (CFAR r1)
        stamp = stamp.astimezone(datetime.timezone.utc)
    except (OverflowError, OSError, ValueError):
        return None, "non-normalizable ingested_at (%s)" % where
    row = dict(obj)
    row["_shape"] = shape
    row["_container"] = container
    row["_rank"] = rank
    row["_line"] = lineno
    row["_dt"] = stamp
    return row, None


def raw_area_manifest_rows(root):
    """Read the base manifest plus every manifest.d/*.jsonl shard (the
    frozen-file law: skipping shards silently loses post-freeze ingests).
    Returns (rows, anomalies); a bad line never stops the read."""
    rows, anomalies = [], []
    sources = []

    def hermetic(path, expect_dir):
        """A manifest container must be a non-symlink regular file whose
        resolved path stays inside its expected directory — a symlinked
        shard could confer membership from outside raw/ or hang the build
        on a device/FIFO target (CFAR r5). Violations surface, never read."""
        if path.is_symlink() or not path.is_file():
            return False
        try:
            return str(path.resolve()).startswith(str(expect_dir.resolve()) + os.sep)
        except Exception:
            return False

    inbox = root / "raw" / "inbox"
    base = inbox / "manifest.jsonl"
    if base.exists() or base.is_symlink():
        if hermetic(base, inbox):
            sources.append((base, "manifest.jsonl", 0))
        else:
            anomalies.append("non-hermetic manifest container ignored: manifest.jsonl")
    shard_dir = inbox / "manifest.d"
    if shard_dir.is_dir():
        for shard in sorted(shard_dir.glob("*.jsonl")):
            if hermetic(shard, shard_dir):
                sources.append((shard, "manifest.d/%s" % shard.name, 1))
            else:
                anomalies.append(
                    "non-hermetic manifest container ignored: manifest.d/%s" % shard.name)
    for path, container, rank in sources:
        try:
            blob = path.read_bytes()
        except Exception as exc:  # unreadable container: surfaced, non-fatal
            anomalies.append("unreadable manifest container %s: %s" % (container, exc))
            continue
        # decode STRICTLY per line: a corrupt byte must reject its own line —
        # errors="replace" would coerce it into a "valid" row that could then
        # confer membership (CFAR r2) — while valid neighbor lines survive.
        raw_lines = blob.split(b"\n")
        if raw_lines and raw_lines[-1] == b"":
            # ONLY the exactly-empty sentinel a trailing \n produces — a
            # whitespace-only final record is a real blank-line anomaly and
            # must not be silently dropped (CFAR r3)
            raw_lines = raw_lines[:-1]
        for lineno, raw_line in enumerate(raw_lines, start=1):
            try:
                line = raw_line.decode("utf-8")
            except UnicodeDecodeError:
                anomalies.append("undecodable manifest line (%s line %d)"
                                 % (container, lineno))
                continue
            row, anomaly = raw_area_parse_row(line, container, rank, lineno)
            if anomaly:
                anomalies.append(anomaly)
            elif row is not None:
                rows.append(row)
    return rows, anomalies


def raw_area_row_digest(row):
    public = {k: v for k, v in row.items() if not k.startswith("_")}
    return hashlib.sha256(
        json.dumps(public, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def raw_area_winner(rows):
    """Total-order winner among valid file rows sharing one source_path
    (packet D2): latest tz-normalized ingested_at; container rank (shards over
    base); container name desc; line desc; canonical row digest. Returns
    (winner, tie_anomaly|None) — a tie past the first key is surfaced."""
    def key(row):
        return (row["_dt"], row["_rank"], row["_container"], row["_line"],
                raw_area_row_digest(row))
    ordered = sorted(rows, key=key, reverse=True)
    winner = ordered[0]
    tie = None
    if len(ordered) > 1 and ordered[1]["_dt"] == winner["_dt"]:
        tie = ("equal-timestamp rows for %s (winner: %s line %d)"
               % (winner["source_path"], winner["_container"], winner["_line"]))
    return winner, tie


def raw_area_control(rel):
    """The FO R1 control grammar, checked before any evidence lane."""
    low = rel.lower()
    base = low.rsplit("/", 1)[-1]
    if base in ("readme.md", ".gitkeep"):
        return True
    return low == "raw/inbox/manifest.jsonl" or low.startswith("raw/inbox/manifest.d/")


def raw_area_documents(root, file_rows_by_path):
    """Membership formula (FO R1): regular ∧ not-control ∧ (inbox-ingestion-
    evidence ∨ TAI-RES). Evidence = a valid file-shape row whose source_path
    matches, or the upload-grammar filename. Location alone lists nothing."""
    members = []
    raw_root = root / "raw"
    if not raw_root.is_dir():
        return members
    try:
        raw_resolved = raw_root.resolve()
    except Exception:
        return members
    for path in sorted(raw_root.rglob("*")):
        # "regular file" (FO R1) excludes symlinks: a committed tai-res-named
        # symlink must not make the build read/hash bytes outside raw/ (CFAR
        # r1 containment finding); the resolved target must stay under raw/.
        if path.is_symlink() or not path.is_file():
            continue
        try:
            if not str(path.resolve()).startswith(str(raw_resolved) + os.sep):
                continue
        except Exception:
            continue
        rel = str(path.relative_to(root))
        try:  # an OS surrogate-escaped (non-UTF-8) filename cannot render —
            # it would abort the build at write time; not a member (CFAR r3)
            rel.encode("utf-8")
        except UnicodeEncodeError:
            continue
        if raw_area_control(rel):
            continue
        base = rel.rsplit("/", 1)[-1]
        inbox_dated = bool(RAW_AREA_INBOX_DATE_RE.match(rel))
        evidence = inbox_dated and (
            rel in file_rows_by_path or RAW_AREA_UPLOAD_RE.match(base))
        low = base.lower()
        tai_res = low.startswith("tai-res-") and low.endswith(".md")
        if evidence or tai_res:
            members.append(rel)
    return members


def raw_area_identity(rel, row, computed_sha):
    """FO R3 identity chain: (1) the winning row's recorded sha256; (2) the
    filename sha12 — ONLY for dated-inbox members, where the upload grammar
    is meaningful (an out-of-inbox TAI-RES name that happens to end in 12 hex
    is an authored name, not storage identity — CFAR r1); (3) the computed
    content hash, labeled."""
    if row is not None:
        return row["sha256"], "manifest"
    if RAW_AREA_INBOX_DATE_RE.match(rel):
        match = RAW_AREA_UPLOAD_RE.match(rel.rsplit("/", 1)[-1])
        if match:
            return match.group("sha12"), "sha12"
    return computed_sha, "computed"


def raw_area_original_name(rel, row):
    """FO R3: the row's original_name; for a rowless dated-inbox
    upload-grammar member the labeled reconstruction <stem><suffix> (a hashed
    storage basename is never presented as an original name); the full
    authored basename for everything else, TAI-RES-lane members included."""
    if row is not None and row.get("original_name", "").strip():
        return row["original_name"], None
    base = rel.rsplit("/", 1)[-1]
    if RAW_AREA_INBOX_DATE_RE.match(rel):
        match = RAW_AREA_UPLOAD_RE.match(base)
        if match:
            return match.group("stem") + match.group("suffix"), "reconstructed from stored name"
    return base, None


def raw_area_fold_article(acc, fm, slug, title, retired):
    """Fold one article's references into the Raw Area accumulator (packet
    D4): the four-field union — raw_documents ∪ superseded_raw_documents ∪
    superseded_sources ∪ class refs in sources — becomes back-links (active
    pages as live links, retired pages as marked non-link references), and
    the article's Topic-Details supersession edges join the superseded set."""
    union = (fm_list(fm, "raw_documents")
             + fm_list(fm, "superseded_raw_documents")
             + fm_list(fm, "superseded_sources")
             + [r for r in fm_list(fm, "sources") if is_raw_ingested_research(r)])
    for ref in union:
        ref = source_ref_clean(ref)
        if not ref:
            continue
        entry = (slug, title, retired)
        if entry not in acc["backlinks"].setdefault(ref, []):
            acc["backlinks"][ref].append(entry)
    acc["superseded"] |= topic_details_superseded(fm)
    return acc


def raw_area_model(root, article_refs=None):
    """The full page model: valid rows -> per-path winners -> members ->
    dated groups (UTC basis), identities (collision/duplicate/mismatch
    handling), links, and the anomaly list. `article_refs` is the fold from
    the article build loop: {"backlinks": {ref: [(slug, title, retired)]},
    "superseded": set(ref)} — None means an empty fold (unit fixtures)."""
    article_refs = article_refs or {"backlinks": {}, "superseded": set()}
    rows, anomalies = raw_area_manifest_rows(root)
    file_rows, url_rows = {}, []
    for row in rows:
        if row["_shape"] == "url":
            url_rows.append(row)
            continue
        file_rows.setdefault(row["source_path"], []).append(row)
    winners = {}
    for source_path, candidates in sorted(file_rows.items()):
        winner, tie = raw_area_winner(candidates)
        winners[source_path] = winner
        if tie:
            anomalies.append(tie)
    members = raw_area_documents(root, winners)
    # edge (4): EVERY valid row's supersedes names its target — file AND URL
    # shapes (a URL re-ingest can be the only record superseding a raw doc —
    # CFAR r2), and not just per-path winners (IAR).
    manifest_supersedes = {
        source_ref_clean(r["supersedes"])
        for r in rows if r.get("supersedes", "").strip()
    }
    entries = []
    for rel in members:
        row = winners.get(rel)
        try:
            computed = hashlib.sha256((root / rel).read_bytes()).hexdigest()
        except Exception as exc:
            computed = ""
            anomalies.append("unreadable member %s: %s" % (rel, exc))
        identity, id_source = raw_area_identity(rel, row, computed)
        name, name_label = raw_area_original_name(rel, row)
        if row is not None:
            group = row["_dt"].astimezone(datetime.timezone.utc).date().isoformat()
            date_label = "ingested %s" % group
        else:
            match = RAW_AREA_INBOX_DATE_RE.match(rel)
            if match:
                group = rel.split("/")[2]
                date_label = "inbox date %s" % group
            else:
                group = None
                date_label = "date unknown"
        # "modified since ingest" fires for BOTH recorded-identity sources:
        # a manifest row's sha256, and a rowless sha12 filename identity whose
        # stored prefix no longer matches the current bytes (CFAR r2).
        mismatch = bool(computed) and (
            (row is not None and computed != row["sha256"])
            or (row is None and id_source == "sha12" and computed[:12] != identity))
        entries.append({
            "rel": rel, "row": row, "identity": identity,
            "id_source": id_source, "computed": computed, "name": name,
            "name_label": name_label, "group": group, "date_label": date_label,
            "mismatch": mismatch,
            "superseded": (rel in article_refs["superseded"]
                           or rel in manifest_supersedes),
            "backlinks": article_refs["backlinks"].get(rel, []),
        })
    if any(e["mismatch"] for e in entries):
        anomalies.append("modified since ingest: %d member(s)"
                         % sum(1 for e in entries if e["mismatch"]))
    # identical-content cross-references are driven by CURRENT computed
    # hashes (two members whose bytes match cross-reference even under
    # different recorded identities — CFAR r1); shared-recorded-but-diverged
    # is driven by recorded identity where current bytes differ (packet D3):
    by_computed = {}
    for entry in entries:
        if entry["computed"]:
            by_computed.setdefault(entry["computed"], []).append(entry)
    for _, twins in sorted(by_computed.items()):
        if len(twins) < 2:
            continue
        for t in twins:
            t["identical"] = len(twins)
        anomalies.append("identical content ×%d: %s" % (
            len(twins), ", ".join(t["rel"] for t in twins)))
    by_recorded = {}
    for entry in entries:
        if entry["id_source"] == "computed":
            continue  # a computed identity is not RECORDED — it must never
            # pull an unrelated member into a shared-recorded group (CFAR r3)
        by_recorded.setdefault(entry["identity"], []).append(entry)
    for _, twins in sorted(by_recorded.items()):
        if len(twins) < 2:
            continue
        if len({t["computed"] for t in twins}) > 1:
            for t in twins:
                t["shared_recorded"] = True
            anomalies.append("shared recorded identity, diverged bytes: %s"
                             % ", ".join(t["rel"] for t in twins))
    # displayed-prefix disambiguation between DISTINCT identities (packet D3):
    display = {e["rel"]: e["identity"][:12] for e in entries}
    for width in (16, 24, 64):
        shown = {}
        for entry in entries:
            shown.setdefault(display[entry["rel"]], set()).add(entry["identity"])
        collided = {d for d, idents in shown.items() if len(idents) > 1}
        if not collided:
            break
        anomalies.append("identifier prefix collision: %s" % ", ".join(sorted(collided)))
        for entry in entries:
            if display[entry["rel"]] in collided:
                if len(entry["identity"]) >= width:
                    display[entry["rel"]] = entry["identity"][:width]
                else:  # a sha12-source identity cannot expand: disambiguate
                    display[entry["rel"]] = (
                        "%s · computed disambiguator %s"
                        % (entry["identity"], entry["computed"][:12]))
    for entry in entries:
        entry["display_identity"] = display[entry["rel"]]
    # recorded-but-absent targets (packet D4):
    for source_path in sorted(winners):
        if not (root / source_path).is_file():
            anomalies.append("recorded but absent on disk: %s" % source_path)
    if url_rows:
        anomalies.append("URL ingests: %d — provenance only, no file entry" % len(url_rows))
    groups = {}
    for entry in entries:
        groups.setdefault(entry["group"], []).append(entry)
    for bucket in groups.values():
        bucket.sort(key=lambda e: (e["name"].lower(), e["rel"]))
    ordered = sorted((g for g in groups if g is not None), reverse=True)
    if None in groups:
        ordered.append(None)
    return {
        "groups": [(g, groups[g]) for g in ordered],
        # one chokepoint for both sinks: every anomaly is one-line,
        # control-free, and encodable before it can reach print or the page
        "anomalies": [raw_area_printable(a) for a in anomalies],
        "url_rows": url_rows,
        "member_count": len(entries),
    }


def raw_page(status, model):
    """Render the Raw Area tools page (packet D1/D4). Lists and links only;
    every rendered manifest-derived string is escaped; note/mode never render."""
    parts = ['<h1 class="page-title">Raw Area</h1>'
             '<article class="body"><p>Every raw ingested research file — '
             'grouped by ingestion date (UTC), newest first. Identity is the '
             'recorded ingest identity where one exists; anomalies surface '
             'below, never silently.</p>']
    for group, bucket in model["groups"]:
        heading = group if group is not None else "Date unknown"
        parts.append('<h2>%s</h2><ul class="raw-area-group">' % html.escape(heading))
        for e in bucket:
            href = source_href(e["rel"])
            if href:
                title_html = '<a href="%s">%s</a>' % (html.escape(href), html.escape(e["name"]))
            else:
                title_html = '<span class="source-unserved">%s</span>' % html.escape(e["name"])
            bits = [title_html]
            if e["name_label"]:
                bits.append('<em class="raw-name-label">(%s)</em>' % html.escape(e["name_label"]))
            ident = '<code class="raw-identity">%s</code>' % html.escape(e["display_identity"])
            if e["id_source"] == "computed":
                ident += ' <em class="raw-id-label">(computed)</em>'
            bits.append(ident)
            bits.append('<code class="raw-path">%s</code>' % html.escape(e["rel"]))
            if e.get("identical"):
                bits.append('<span class="raw-identical">identical content ×%d</span>' % e["identical"])
            if e.get("shared_recorded"):
                bits.append('<span class="raw-shared-recorded">shared recorded identity</span>')
            if e["mismatch"]:
                bits.append('<span class="raw-mismatch">modified since ingest</span>')
            bits.append('<span class="raw-date">%s</span>' % html.escape(e["date_label"]))
            if e["backlinks"]:
                links = []
                for slug, title, retired in e["backlinks"]:
                    if retired:
                        links.append('<span class="raw-backlink-retired">%s (retired)</span>'
                                     % html.escape(title))
                    else:
                        links.append('<a href="%s.html">%s</a>'
                                     % (html.escape(slug), html.escape(title)))
                bits.append('<span class="raw-backlinks">topics: %s</span>' % ", ".join(links))
            else:
                bits.append('<span class="raw-unassigned">unassigned — no topic references</span>')
            cls = ' class="source-superseded"' if e["superseded"] else ""
            parts.append("<li%s>%s</li>" % (cls, " · ".join(bits)))
        parts.append("</ul>")
    parts.append('<h2>Anomalies</h2>')
    if model["anomalies"]:
        parts.append('<ul class="raw-area-anomalies">%s</ul>' % "".join(
            "<li>%s</li>" % html.escape(a) for a in model["anomalies"]))
    else:
        parts.append("<p>None.</p>")
    if model["url_rows"]:
        parts.append('<ul class="raw-area-url-ingests">%s</ul>' % "".join(
            '<li><code>%s</code></li>' % html.escape(r["source_url"])
            for r in model["url_rows"]))
    parts.append("</article>")
    return tool_page("Raw Area", "".join(parts), status)


# R2 — Investigation Topic Standard schema (the "standard"). Required frontmatter
# keys; the render-driving subset that must additionally be non-empty; the required
# `## ` headings; and the canonical order (Integration Packet optional, immediately
# before Sources & Provenance).
INVESTIGATION_REQUIRED_FM = (
    "entity", "aliases", "tier", "status", "last_compiled",
    "civilization_contribution", "raw_documents", "current_research_version", "sources",
)
# Present AND non-empty (presence != non-empty; CFADA-r19 #40). raw_documents and
# aliases are EXEMPT — legitimately empty on a conformant page (a support-only page
# has no ingested research file; CFADA-r20 #41), so requiring them non-empty would
# make AC6/P2 unsatisfiable.
INVESTIGATION_NONEMPTY_FM = ("civilization_contribution", "entity", "status", "last_compiled")
INVESTIGATION_REQUIRED_HEADINGS = (
    "What Changed with the Research", "The Boundary", "Capability Read",
    "Benchmark Reality", "Sources & Provenance",
)
INVESTIGATION_OPTIONAL_HEADING = "Integration Packet"
INVESTIGATION_CANONICAL_ORDER = (
    "What Changed with the Research", "The Boundary", "Capability Read",
    "Benchmark Reality", "Integration Packet", "Sources & Provenance",
)


def _fm_has_key(fm, key):
    return re.search(r"^%s:" % re.escape(key), fm, re.M) is not None


def _body_level2_headings(body):
    """Ordered level-2 (`## `) heading texts in a page body (level-1/3+ ignored)."""
    return [m.group(1).strip() for m in re.finditer(r"^##[ \t]+(.+?)[ \t]*$", body, re.M)]


def _lead_is_bold(body):
    """R2 Summary: the first paragraph before the first `## ` heading must be
    non-empty and carry bold emphasis (a `**…**` pair or `<strong>`). Fail-closed:
    a lone `**` or a plain paragraph is NOT bold (CFADA-r2 #7)."""
    pre = re.split(r"^##[ \t]+.+$", body, maxsplit=1, flags=re.M)[0]
    lines = [ln for ln in pre.splitlines() if not re.match(r"^#[ \t]+", ln)]
    text = "\n".join(lines).strip()
    para = re.split(r"\n[ \t]*\n", text, maxsplit=1)[0].strip() if text else ""
    if not para:
        return False
    return para.count("**") >= 2 or "<strong>" in para.lower()


def investigation_conformance(fm, body):
    """R2 conformance predicate for the Investigation Topic Standard. Returns the
    SET of deficiency tags for a page's frontmatter + body; conformant ⟺ the set
    is empty. Checks: the required frontmatter keys are present, the render-driving
    subset is non-empty, the required `## ` headings are present, the Summary lead
    is bold, and the standard headings (incl. a present Integration Packet) are in
    canonical order. Free extra headings (## Placement, ## Decision Record) are
    ignored by the order check. Fail-closed: any missing / empty / misordered
    element is a deficiency. Phase 2 wraps this per active investigation slug
    (AC6/P2)."""
    deficiencies = set()
    for key in INVESTIGATION_REQUIRED_FM:
        if not _fm_has_key(fm, key):
            deficiencies.add("missing-fm:%s" % key)
    for key in INVESTIGATION_NONEMPTY_FM:
        # fm_scalar (not fm_val): a comment-only required field (`entity: # TODO`)
        # reads as empty, so it still produces an empty-fm deficiency (CFAR: Codex).
        if _fm_has_key(fm, key) and not fm_scalar(fm, key):
            deficiencies.add("empty-fm:%s" % key)
    # the standard is `tier: investigation` specifically — presence alone is not
    # enough, so a mistiered page (architecture / blank / any other value) cannot
    # pass the structural gate or render in the wrong nav group (CFAR: Codex).
    if fm_scalar(fm, "tier") != "investigation":
        deficiencies.add("wrong-tier")
    headings = _body_level2_headings(body)
    hset = set(headings)
    for heading in INVESTIGATION_REQUIRED_HEADINGS:
        if heading not in hset:
            deficiencies.add("missing-heading:%s" % heading)
    if not _lead_is_bold(body):
        deficiencies.add("non-bold-lead")
    standard = set(INVESTIGATION_REQUIRED_HEADINGS) | {INVESTIGATION_OPTIONAL_HEADING}
    seq = [h for h in headings if h in standard]
    canon = [h for h in INVESTIGATION_CANONICAL_ORDER if h in seq]
    if seq != canon:
        deficiencies.add("out-of-order")
    return deficiencies


def article_frontmatter(slug):
    p = WIKI / ("%s.md" % slug)
    if not p.exists():
        return ""
    fm, _ = split_fm(p.read_text())
    return fm


def investigation_topic_for(slug, meta):
    # fm_scalar: a commented `investigation_topic: Sakana AI # cluster` must group
    # by "Sakana AI", not "Sakana AI # cluster" (CFAR: Codex).
    return fm_scalar(article_frontmatter(slug), "investigation_topic")


def investigation_primary_flag(slug):
    # R9: strict boolean — ONLY the exact `true` scalar (bare or quoted, comment
    # stripped) marks the primary page of a multi-page investigation cluster. The
    # match is case-SENSITIVE: `TRUE`/`True`, `false`, `"false"`, `yes`, `1`, an
    # empty value, or an absent key are all NOT primary (CFADA-r19 #39; CFAR:
    # Codex — a malformed flag must never trigger the lossy collapse), so it can
    # only ever fail to collapse (show all) — it can never hide a page.
    return fm_scalar(article_frontmatter(slug), "investigation_primary") == "true"


def cluster_representative(articles):
    # R9: for a multi-page investigation_topic cluster (>=2 active members),
    # return the single active investigation_primary member (the one nav entry)
    # iff EXACTLY ONE exists; else None -> show every member (fail-safe: 0 or >=2
    # active primaries never hides a page). Single-page topics (<2) -> None.
    if len(articles) < 2:
        return None
    primaries = [a for a in articles if investigation_primary_flag(a["slug"])]
    return primaries[0] if len(primaries) == 1 else None


def cluster_primary_deficiency(articles):
    """R9/§2.5 corpus cluster primary invariant: a multi-page cluster (>=2 active
    members) must carry EXACTLY ONE active investigation_primary. Returns a
    deficiency tag — 'no-active-primary' (zero) or 'multiple-active-primaries'
    (>=2) — for a misconfigured multi-page cluster, or '' when valid (exactly one)
    or not a multi-page cluster. This is corpus-level (needs cross-page counts),
    distinct from the per-page investigation_conformance and complementary to
    cluster_representative (which returns None for BOTH the 0 and >=2 render
    fallbacks). The Phase-2 corpus gate enumerates live clusters and asserts this
    is '' for every one (AC10; CFAR: Codex — the >=2 case must be reported, not
    silently treated as a normal fallback)."""
    if len(articles) < 2:
        return ""
    primaries = [a for a in articles if investigation_primary_flag(a["slug"])]
    if not primaries:
        return "no-active-primary"
    if len(primaries) >= 2:
        return "multiple-active-primaries"
    return ""


def raw_doc_count_for_articles(articles):
    docs = set()
    for article in articles:
        fm = article_frontmatter(article["slug"])
        docs.update(raw_doc_refs(fm))
    return len(docs)


def article_direct_contribution(article):
    contribution = fm_val(article_frontmatter(article["slug"]), "civilization_contribution")
    if re.match(r"^Contributed\b", contribution or "", flags=re.I):
        return contribution
    return ""


def nav_contribution_marker(articles):
    contributions = [article_direct_contribution(article) for article in articles]
    contributions = [c for c in contributions if c]
    if not contributions:
        return ""
    title = "Civilization contribution: c — %s" % contributions[0]
    if len(contributions) > 1:
        title = "Civilization contribution: c — %d contributing articles" % len(contributions)
    return (
        '<span class="nav-contribution-marker" title="%s" '
        'aria-label="Civilization contribution marker: c">c</span>'
    ) % html.escape(title)


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


def source_doc_id(text):
    fm, body = split_fm(text or "")
    doc_id = fm_val(fm, "doc_id") or fm_val(fm, "document_id")
    if doc_id:
        return doc_id
    m = re.search(r"<!--\s*df:artifact\s+id=([A-Za-z0-9_.:-]+)", text or "")
    if m:
        return m.group(1)
    m = re.search(r"^#\s+(ADR-\d{4})\b", body or text or "", flags=re.M)
    if m:
        return m.group(1)
    return ""


@functools.lru_cache(maxsize=None)
def source_link_aliases(ref):
    ref = source_ref_clean(ref)
    href = source_rel_href(ref)
    if not href:
        return []
    aliases = set()
    path = safe_source_path(ref)
    name = pathlib.PurePosixPath(ref).name
    stem = pathlib.PurePosixPath(ref).stem
    if stem:
        aliases.add(stem)
    for m in re.findall(r"\bADR-\d{4}\b", name, flags=re.I):
        aliases.add(m.upper())
    for m in re.findall(r"\bDF-V\d+(?:\.\d+)?-[A-Z]+-\d{3}\b", name, flags=re.I):
        aliases.add(m.upper())
    text = ""
    if path:
        try:
            text = path.read_text(errors="replace")
        except Exception:
            text = ""
    if text:
        fm, body = split_fm(text)
        doc_id = source_doc_id(text)
        if doc_id:
            aliases.add(doc_id)
        title = fm_val(fm, "title") or markdown_title(body)
        if title:
            aliases.add(title)
    lower_ref = ref.lower()
    if "unified-architecture-decisions" in lower_ref:
        aliases.update({
            "Decision 15",
            "DF-V3.9-ADR-001",
            "v3.9 unified decisions",
            "v3.9 Unified Architecture Decisions",
            "Dark Factory v3.9 Unified Architecture Decisions",
        })
    if "technology-decision-crosswalk" in lower_ref:
        aliases.update({
            "External Technology Decision Crosswalk",
            "v3.9.1 External Technology Decision Crosswalk",
            "technology-decision-crosswalk",
            "DF-V3.9-EPIC-TECH-CROSSWALK",
        })
    if "memory-knowledge-capability" in lower_ref:
        aliases.update({
            "DF-V3.9-SPEC-006",
            "memory/knowledge doctrine",
            "Dark Factory v3.9 Memory Knowledge And Capability Evolution",
        })
    # Long or file-like aliases must be considered before short identifiers
    # such as ADR-0008, otherwise the short replacement can split the title.
    return [(alias, href) for alias in sorted(aliases, key=len, reverse=True) if alias]


def alias_link_map(refs):
    links = {}
    for ref in refs:
        for alias, href in source_link_aliases(ref):
            # Later refs win so an updated/superseding source listed later in
            # frontmatter becomes the default target for shared document IDs.
            links[alias.lower()] = (alias, href)
    return links


def free_text_source_alias(alias):
    return bool(re.search(
        r"(?i)\b(ADR-\d{4}|DF-V\d+(?:\.\d+)?-[A-Z0-9_.:-]+|TAI-RES-\d{4}-\d{3}|Decision\s+\d+)\b",
        alias or "",
    ))


def link_source_code_alias_refs(body_html, refs):
    links = alias_link_map(refs)
    if not links:
        return body_html

    def repl(m):
        label = html.unescape(m.group(1)).strip()
        hit = links.get(label.lower())
        if not hit:
            return m.group(0)
        _, href = hit
        return '<a class="source-code-link" href="%s"><code>%s</code></a>' % (
            html.escape(href), html.escape(label))

    parts = re.split(r"(<a\b[^>]*>.*?</a>|<pre\b[^>]*>.*?</pre>)",
                     body_html, flags=re.I | re.S)
    for i, part in enumerate(parts):
        if not part or part.startswith("<a") or part.startswith("<pre"):
            continue
        parts[i] = re.sub(r"<code>([^<]+)</code>", repl, part)
    return "".join(parts)


def _link_aliases_in_text(text, alias_links):
    for alias, href in alias_links:
        escaped_alias = html.escape(alias)
        if not escaped_alias:
            continue
        pat = re.compile(r"(?<![A-Za-z0-9_-])(%s)(?![A-Za-z0-9_-])" % re.escape(escaped_alias), re.I)

        def repl(m):
            label = m.group(1)
            return '<a class="source-ref-link" href="%s">%s</a>' % (
                html.escape(href), label)

        parts = re.split(r"(<a\b[^>]*>.*?</a>)", text, flags=re.I | re.S)
        for i, part in enumerate(parts):
            if part.startswith("<a"):
                continue
            parts[i] = pat.sub(repl, part)
        text = "".join(parts)
    return text


def link_source_alias_refs(body_html, refs):
    alias_links = [
        (alias, href)
        for alias, href in alias_link_map(refs).values()
        if free_text_source_alias(alias)
    ]
    if not alias_links:
        return body_html
    alias_links.sort(key=lambda x: len(x[0]), reverse=True)
    parts = re.split(r"(<a\b[^>]*>.*?</a>|<code\b[^>]*>.*?</code>|<pre\b[^>]*>.*?</pre>|<[^>]+>)",
                     body_html, flags=re.I | re.S)
    for i, part in enumerate(parts):
        if not part or part.startswith("<"):
            continue
        parts[i] = _link_aliases_in_text(part, alias_links)
    return "".join(parts)


def frontmatter_source_refs():
    refs = set()
    for p in sorted(WIKI.glob("*.md")):
        fm, _ = split_fm(p.read_text())
        for key in ("sources", "raw_documents"):
            refs.update(source_ref_clean(r) for r in fm_list(fm, key) if source_ref_clean(r))
    return refs


def article_source_refs(fm):
    refs = []
    seen = set()
    for key in ("sources", "raw_documents"):
        for ref in fm_list(fm, key):
            ref = source_ref_clean(ref)
            if not ref or ref in seen:
                continue
            seen.add(ref)
            refs.append(ref)
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
        write_dist_text(SOURCE_DIST / ("%s.html" % sid), simple_page(
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


def _supersedes_target(comment):
    """Extract the superseded ref from a source-line annotation. Segments
    are '; '-joined (see ingest_server.source_line) and the writer always
    appends the annotation LAST, so only a standalone FINAL
    'supersedes:' segment counts (ready-state CFAR): the phrase appearing
    mid-note, at a non-final segment, or more than once is ambiguous free
    text and marks nothing — the allowlist direction. Free-text refs with
    spaces are captured whole (CFAR r1). Note and annotation share one
    authorized form, so this is accident-proofing, not a privilege
    boundary."""
    parts = [s.strip() for s in (comment or "").split(";")]
    hits = [s for s in parts if s.startswith("supersedes:")]
    if len(hits) != 1 or not parts[-1].startswith("supersedes:"):
        return ""
    return source_ref_clean(hits[0][len("supersedes:"):].strip())


def build_source_panel(fm):
    # wiki#60: a source named as supersedes-target by another entry's
    # annotation renders de-emphasized with an explicit badge. Driven by the
    # EXISTING `supersedes: <ref>` comments the ingest lanes write — no
    # article bytes change, so no allowlist pins are disturbed. Display
    # order stays historical (append-only honesty); the badge carries the
    # signal. Only an annotation naming another listed ref counts — the
    # allowlist direction (unknown/malformed annotations mark nothing).
    entries = []
    superseded_by = {}
    for raw_ref, comment in fm_list_with_comments(fm, "sources"):
        ref = source_ref_clean(raw_ref)
        if not ref:
            continue
        entries.append(ref)
        old = _supersedes_target(comment)
        if old:
            superseded_by[old] = ref
    if not entries:
        return ""
    rows = []
    for ref in entries:
        href = source_href(ref)
        label = source_title(ref, safe_source_path(ref))
        if href:
            link = '<a href="%s">%s</a>' % (html.escape(href), html.escape(label))
        else:
            link = '<span class="source-unserved">%s</span>' % html.escape(label)
        if ref in superseded_by:
            newer = superseded_by[ref]
            badge = ('<span class="source-superseded-badge">superseded by '
                     '%s</span>') % html.escape(
                         source_title(newer, safe_source_path(newer)))
            rows.append('<li class="source-superseded">%s %s</li>'
                        % (link, badge))
        else:
            rows.append('<li>%s</li>' % link)
    return (
        '<details class="source-panel">'
        '<summary>Article sources (%d)</summary>'
        '<ul>%s</ul>'
        '</details>'
    ) % (len(entries), "".join(rows))


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


def build_repo_nav(current_repo="", org=DEFAULT_ORG):
    # each org band lists only its own repo groups (DP-20260710 D2, intake
    # decision 2): platform -> Transpara, civilization+other -> Transpara-AI.
    org_groups = [g for g in REPO_GROUP_ORDER if g in ORG_REPO_GROUPS.get(org, [])]
    grouped = repos_by_group()
    total = sum(len(grouped.get(g, [])) for g in org_groups)
    if not total:
        return ""
    # "index" (repos.html) is current for the band hosting the overview link,
    # preserving the pre-split `if current_repo:` open behavior (CFAR r1 P3)
    current_here = (current_repo == "index" and org == DEFAULT_ORG) or any(
        r["slug"] == current_repo
        for g in org_groups for r in grouped.get(g, []))
    # data-tier keys the sidebar collapse persistence: transpara-ai keeps the
    # historical "repos" key so stored preferences survive; transpara gets its
    # own key so the two bands never share open/closed state.
    tier_key = "repos" if org == DEFAULT_ORG else "repos-%s" % org
    attrs = ['class="side-group repo-side-group"', 'data-tier="%s"' % html.escape(tier_key)]
    if current_here:
        attrs.append('data-current-group="true"')
    # the full repository index (repos.html) spans all orgs; its overview link
    # stays on the transpara-ai block only, where it always lived.
    overview = ('<div class="repo-nav-overview"><a%s href="repos.html">Repository index</a></div>'
                % (' class="current"' if current_repo == "index" else "")) if org == DEFAULT_ORG else ""
    out = ['<details %s><summary><span>%s Repos</span><em>%d</em></summary>'
           '%s<div class="repo-nav-sections">' %
           (" ".join(attrs), html.escape(ORG_LABEL.get(org, org)), total, overview)]
    for key in org_groups:
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
        # R9: a single-page topic, OR a multi-page cluster with exactly one active
        # investigation_primary, renders as ONE flat row (linking the primary,
        # labeled by the topic); a multi-page cluster with 0 or >=2 active primaries
        # falls through to the expandable group below (fail-safe — no page is hidden
        # without a unique active primary).
        single = articles[0] if len(articles) == 1 else cluster_representative(articles)
        if single is not None:
            # the collapsed row represents the WHOLE cluster, so it is current when
            # ANY member is the current article — not only the primary — else
            # viewing a non-primary member leaves the sidebar with no highlight
            # (CFAR: Codex). For a single-page topic this is just that page.
            cls = ' class="current"' if any(a["slug"] == current for a in articles) else ""
            # Preserve the count the collapsible topic group showed before collapsing.
            count = raw_doc_count_for_articles(articles)
            count_html = '<em>%d</em>' % count if count else ""
            marker = nav_contribution_marker(articles)
            out.append('<li class="nav-article-row"><a%s href="%s.html" title="%s">%s</a>%s%s</li>' %
                       (cls, single["slug"], html.escape(single["title"]), html.escape(topic), marker, count_html))
            continue
        open_attr = " open" if any(a["slug"] == current for a in articles) else ""
        marker = nav_contribution_marker(articles)
        out.append(
            '<li class="nav-subgroup-item"><details class="nav-subgroup"%s>'
            '<summary><span>%s</span>%s<em>%d</em></summary><ul>' %
            (open_attr, html.escape(topic), marker, raw_doc_count_for_articles(articles))
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
        marker = nav_contribution_marker([article])
        out.append('<li class="nav-article-row"><a%s href="%s.html">%s</a>%s%s</li>' %
                   (cls, article["slug"], html.escape(article["title"]), marker, count_html))
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
    # two org bands, TRANSPARA above TRANSPARA-AI (DP-20260710 D2, operator
    # mock): each band renders its own repos block, then its own sections.
    for org in ORG_ORDER:
        band = []
        band.append(build_repo_nav(current_repo, org=org))
        for tier in ORG_SECTIONS[org]:
            # retired articles drop from nav but stay reachable by direct link
            # .get with DEFAULT_ORG mirrors D3's absent-org rule exactly; an
            # UNKNOWN org can never reach here (article_meta fails the build),
            # so this is the grandfather default, not an acceptance path.
            arts = sorted([m for m in META.values()
                           if m.get("org", DEFAULT_ORG) == org and m["tier"] == tier
                           and not m.get("retired_on")],
                          key=lambda m: m["title"].lower())
            if not arts:
                continue
            attrs = ['class="side-group"', 'data-tier="%s"' % html.escape(tier)]
            if tier == current_tier:
                attrs.append('data-current-group="true"')
            elif not current and tier in {"institutional", "meta"}:
                attrs.append('data-default-open="true"')
            band.append('<details %s><summary><span>%s</span><em>%d</em></summary><ul>'
                        % (" ".join(attrs), html.escape(SECTION_LABEL.get(tier, tier)), len(arts)))
            if tier == "investigation":
                band.append(build_investigation_nav(arts, current))
            else:
                for a in arts:
                    cls = ' class="current"' if a["slug"] == current else ""
                    band.append('<li><a%s href="%s.html">%s</a></li>' % (cls, a["slug"], html.escape(a["title"])))
            band.append("</ul></details>")
        if not any(band):
            continue  # an org with no repos and no articles renders no band
        out.append('<div class="side-org">%s</div>' % html.escape(ORG_LABEL.get(org, org)))
        out.extend(band)
    out.append("</nav>")
    out.insert(-1, '<div class="sidebar-resizer" role="separator" aria-orientation="vertical" '
                   'aria-label="Resize navigation" aria-valuemin="280" aria-valuemax="560" '
                   'tabindex="0"></div>')
    return "".join(out)


def navbox_investigation_reps(arts):
    # R9: collapse each multi-page investigation_topic cluster to its single active
    # primary in the bottom navbox index, mirroring the sidebar nav via the shared
    # cluster_representative selection so the two surfaces cannot diverge. Single-page
    # topics, no-topic articles, and clusters without a single primary keep every
    # member (fail-safe).
    grouped = {}
    for a in arts:
        topic = investigation_topic_for(a["slug"], a)
        if topic:
            grouped.setdefault(topic, []).append(a)
    hidden = set()
    for members in grouped.values():
        rep = cluster_representative(members)
        if rep is not None:
            hidden.update(a["slug"] for a in members if a["slug"] != rep["slug"])
    return [a for a in arts if a["slug"] not in hidden]


def build_navbox():
    out = ['<nav class="navbox"><div class="navbox-title">%s — index</div><div class="navbox-body">' % html.escape(SITE_NAME)]
    # iterate the full org/section structure so newly-valid Transpara pages
    # appear here like every other nav surface (CFAR r2); org order matches
    # the sidebar bands, and the org filter uses the same D3 absent-org rule.
    for org in ORG_ORDER:
        for tier in ORG_SECTIONS[org]:
            arts = sorted([m for m in META.values()
                           if m.get("org", DEFAULT_ORG) == org and m["tier"] == tier
                           and not m.get("retired_on")],
                          key=lambda m: m["title"].lower())
            if not arts:
                continue
            if tier == "investigation":
                arts = navbox_investigation_reps(arts)
            links = " · ".join('<a href="%s.html">%s</a>' % (a["slug"], html.escape(a["title"])) for a in arts)
            out.append('<div class="navbox-row"><span class="navbox-grp">%s</span><span class="navbox-list">%s</span></div>'
                       % (html.escape(SECTION_LABEL.get(tier, tier)), links))
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
    docs = topic_details_refs(fm)
    if docs:
        superseded = topic_details_superseded(fm)
        items = []
        for ref in docs:
            path = safe_source_path(ref)
            href = source_href(ref)
            label = source_title(ref, path)
            if href:
                link = '<a href="%s">%s</a>' % (html.escape(href), html.escape(label))
            else:
                link = '<span class="source-unserved">%s</span>' % html.escape(label)
            if ref in superseded:
                items.append('<li class="source-superseded">%s '
                             '<span class="source-superseded-badge">superseded</span></li>' % link)
            else:
                items.append('<li>%s</li>' % link)
        row("Topic Details", '<ul class="raw-doc-links">%s</ul>' % "".join(items))
    if not rows:
        return ""
    return ('<aside class="infobox"><div class="infobox-title">%s</div><table>%s</table>'
            '<div class="infobox-foot">part of the <a href="index.html">%s</a></div></aside>'
            % (html.escape(meta["title"]), "".join(rows), html.escape(SITE_NAME)))


def build_contribution_box(fm):
    contribution = fm_val(fm, "civilization_contribution")
    if not contribution:
        return ""
    contribution_html = link_source_alias_refs(
        link_source_code_alias_refs(html.escape(contribution), article_source_refs(fm)),
        article_source_refs(fm),
    )
    return (
        '<aside class="contribution-box" aria-label="Civilization contribution">'
        '<strong>Civilization contribution</strong>'
        '<p>%s</p>'
        '</aside>'
    ) % contribution_html


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
    # a wikilink the body gate suppressed (retired target / cleanly-removed
    # edge) must not reappear as a live link here — filter through the SAME
    # link_state gate the body used (CFAR r1 P2-3)
    rel = sorted((s for s in links if s != current and s in META
                  and ingest_ops.link_state(current, s, META, EDGE_STATES) == "live"),
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


def pending_edges_chip(edge_states):
    """Honest-state chip (fe-ux packet §2.4): dangling-pending edge count
    from the STRICT edge-states load the build already performed — a corrupt
    file refuses the whole build upstream (ingest_ops.load_edge_states), so
    this renderer only ever sees validated state. Allowlist rendering: only
    a positive count of the one pending state renders; zero renders nothing."""
    n = sum(1 for entry in edge_states.values()
            if entry.get("state") == "dangling-pending")
    if n <= 0:
        return ""
    return ('<span class="fresh warn pending-edges">%d edge%s pending '
            'reconciliation</span>' % (n, "" if n == 1 else "s"))


def freshness(status):
    synced = status.get("synced", "")
    stale = status.get("stale_articles", [])
    changed = status.get("changed_articles", [])
    chip = pending_edges_chip(EDGE_STATES)
    if not synced:
        return '<span class="fresh warn">not yet refreshed</span>' + chip
    if not stale:
        changed_text = ""
        if changed:
            changed_text = " · %d rebuilt" % len(changed)
        return '<span class="fresh ok">updated %s · 0 stale%s</span>%s' % (
            html.escape(synced), changed_text, chip)
    # "stale" = a deterministic rebuild failed after refresh.py identified
    # articles whose declared sources changed. Make the chip name the affected
    # articles so the retry/fix target is actionable rather than opaque.
    # Native <details>: no JS, keyboard-accessible.
    n = len(stale)
    links = "".join(
        '<li><a href="%s.html">%s</a></li>' % (html.escape(s), html.escape(title_of(s)))
        for s in stale
    )
    return (
        '<details class="fresh-details">'
        '<summary class="fresh warn">updated %s · rebuild failed · %d stale</summary>'
        '<div class="fresh-pop" role="group" aria-label="Articles from failed rebuild">'
        '<p class="fresh-pop-head">The last deterministic rebuild failed after detecting '
        'source changes for %d article%s:</p>'
        '<ul class="fresh-pop-list">%s</ul>'
        '<p class="fresh-pop-foot">Fix the build error and rerun '
        '<code>compile/refresh.py</code>. A successful deterministic rebuild clears this '
        'list and records the affected articles in <code>changed_articles</code>; LLM prose '
        'synthesis remains a separate manual Tier 2 decision.</p>'
        '</div></details>'
    ) % (html.escape(synced), n, n, "" if n == 1 else "s", links) + chip


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
        '<a href="raw.html">Raw</a>'
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
        '<nav class="top-links" aria-label="Wiki tools"><a href="../repos.html">Repos</a><a href="../sources.html">Sources</a><a href="../raw.html">Raw</a><a href="../ingest.html">Ingest</a></nav>'
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
    target_options = ['<option value="">Select an article…</option>']
    for slug, meta in sorted(META.items(), key=lambda kv: kv[1]["title"].lower()):
        if meta.get("retired_on"):
            continue  # retired tombstones are not valid Add/Replace targets —
            # keep the build-time selector consistent with /api/articles and
            # the server-side refusal (CFAR r16)
        opt = '<option value="%s">%s</option>' % (
            html.escape(slug), html.escape(meta["title"]))
        article_options.append(opt)
        target_options.append(opt)
    # fe-ux packet §2.2: transport-token auth (the shared authoring-token
    # field) is NOT the operation authorization — the single-use artifact
    # never touches this page (FO Q2). Both destructive panels say so.
    q2_line = (
        '<p class="ingest-authority-note">Requires a pre-placed single-use '
        'authorization artifact on the server; this page never reads, '
        'checks, or transmits the operation authorization artifact — an '
        'unauthorized request is refused honestly by the server.</p>')
    inner = (
        '<h1 class="page-title">Wiki Source Ingest</h1>'
        '<article class="body ingest-tool">'
        # the transport token is shared page chrome, OUTSIDE the mode panels:
        # a user starting in Replace/Remove needs it visible (CFAR r1 P2); it
        # travels as a header via headers(), never as a form field
        '<section class="ingest-card ingest-auth">'
        '<label>Authoring token<input id="authoring-token" type="password" autocomplete="off" placeholder="required for non-loopback authoring"></label>'
        '</section>'
        '<nav class="ingest-modes" role="radiogroup" aria-label="Operation">'
        '<label><input type="radio" name="ingest-mode" value="add" checked> Add</label>'
        '<label class="mode-destructive"><input type="radio" name="ingest-mode" value="replace"> Replace</label>'
        '<label class="mode-destructive"><input type="radio" name="ingest-mode" value="remove"> Remove</label>'
        '</nav>'
        '<section class="ingest-card" data-mode-panel="add">'
        '<h2>Batch ingest</h2>'
        '<form id="ingest-form">'
        # DP-20260710 D4: every article add names its destination org + section
        # (intake decision 3 — required for ALL ingests). The selects are UI
        # convenience only; /api/ingest re-validates fail-closed (422).
        '<label>Org<select name="org" id="ingest-org" required>'
        '<option value="">Select org…</option>' + "".join(
            '<option value="%s">%s</option>' % (html.escape(o), html.escape(ORG_LABEL[o]))
            for o in ORG_ORDER) +
        '</select></label>'
        '<label>Section<select name="section" id="ingest-section" required>'
        '<option value="">Select section…</option></select></label>'
        '<label>Target article<select name="target_slug" id="target-slug">%s</select></label>'
        # R6/§2.1: the "New investigation" toggle (default OFF) is the ONLY
        # browser page-creation path. Checking it reveals a required name field
        # (the name — not the doc title — drives the new page) and ignores the
        # target above; the server-side fail-closed guard is the real gate.
        '<label class="confirm-line"><input type="checkbox" name="new_investigation" id="new-investigation" value="true"> New investigation — create a new topic page (ignores the target above)</label>'
        '<label id="new-investigation-name-row" hidden>Investigation name<input name="name" id="new-investigation-name" type="text" placeholder="subject name — drives the new page slug and entity"></label>'
        '<label>Documents<input name="documents" id="documents" type="file" multiple></label>'
        '<label>External URLs<textarea name="external_urls" id="external-urls" rows="4" placeholder="https://..."></textarea></label>'
        '<label>Supersedes<select name="supersedes" id="supersedes"><option value="">No existing source selected</option></select></label>'
        '<label>Note<input name="note" id="source-note" type="text" placeholder="citation update, replacement, or placement note"></label>'
        '<div class="form-actions"><button type="submit">Ingest and rebuild</button>'
        '<button type="button" id="rebuild-now">Refresh status and rebuild</button></div>'
        '</form></section>'
        '<section class="ingest-card ingest-destructive" data-mode-panel="replace" hidden>'
        '<h2>Replace a source</h2>'
        + q2_line +
        '<form id="replace-form">'
        '<label>Target article<select name="slug" id="rep-target">%s</select></label>'
        '<label>Source to supersede<select name="source_ref" id="rep-source"><option value="">Select a source…</option></select></label>'
        '<label>Replacement document<input name="document" id="rep-doc" type="file"></label>'
        '<label>Note<input name="note" id="rep-note" type="text" placeholder="why this source is superseded"></label>'
        '<div id="rep-preview" class="consequence-panel">Select a target and source to preview consequences.</div>'
        '<label class="confirm-line"><input id="rep-confirm" type="checkbox" disabled> I have read the consequences above</label>'
        '<div class="form-actions"><button type="submit" id="rep-submit" disabled>Replace after preview</button></div>'
        '</form></section>'
        '<section class="ingest-card ingest-destructive" data-mode-panel="remove" hidden>'
        '<h2>Remove (retire) a topic</h2>'
        + q2_line +
        '<p class="ingest-authority-note">The retirement reason is bound to the authorization artifact on the server — it is not collected here.</p>'
        '<form id="remove-form">'
        '<label>Target article<select name="slug" id="rm-target">%s</select></label>'
        '<div id="rm-preview" class="consequence-panel">Select a target to preview consequences.</div>'
        '<label class="confirm-line"><input id="rm-confirm" type="checkbox" disabled> I have read the consequences above</label>'
        '<div class="form-actions"><button type="submit" id="rm-submit" disabled>Retire after preview</button></div>'
        '</form></section>'
        '<section class="ingest-card"><h2>Status</h2><div id="ingest-status" class="ingest-status">Ready.</div></section>'
        '</article>'
        '<script>(function(){'
        'var form=document.getElementById("ingest-form"),status=document.getElementById("ingest-status"),'
        'target=document.getElementById("target-slug"),sup=document.getElementById("supersedes"),rebuild=document.getElementById("rebuild-now"),token=document.getElementById("authoring-token");'
        'var articles={};'
        'var resultStore="civwiki-last-ingest-result";'
        'function esc(s){return String(s==null?"":s).replace(/[&<>"]/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;","\\"":"&quot;"}[c];});}'
        'function headers(){var h={};if(token&&token.value)h["X-CivWiki-Authoring-Token"]=token.value;return h;}'
        'function renderResult(j){var parts=[];'
        'if(j&&j.__restored)parts.push("<p>Last completed action:</p>");'
        'if(j.article_href)parts.push("<p><a href=\\""+esc(j.article_href)+"\\">Open updated article</a></p>");'
        'if(j.source_hrefs&&j.source_hrefs.length){parts.push("<p>Served sources:</p><ul>"+j.source_hrefs.map(function(x){return "<li><a href=\\""+esc(x.href)+"\\">"+esc(x.source)+"</a></li>";}).join("")+"</ul>");}'
        'parts.push("<pre>"+esc(JSON.stringify(j,null,2))+"</pre>");status.innerHTML=parts.join("");}'
        'function say(x){if(typeof x==="string")status.textContent=x;else renderResult(x);}'
        'function reloadWithResult(j){try{sessionStorage.setItem(resultStore,JSON.stringify(j));}catch(e){}'
        'say("Refresh completed. Reloading generated page shell...");setTimeout(function(){location.reload();},500);}'
        'try{var prev=sessionStorage.getItem(resultStore);if(prev){sessionStorage.removeItem(resultStore);prev=JSON.parse(prev);prev.__restored=true;renderResult(prev);}}catch(e){}'
        'function loadArticles(){fetch("/api/articles",{cache:"no-store",headers:headers()}).then(function(r){return r.ok?r.json():null}).then(function(j){'
        'if(!j){say("Authoring API unavailable. Start compile/ingest_server.py to enable browser ingest.");return;}'
        'articles={};j.articles.forEach(function(a){articles[a.slug]=a;});target.dispatchEvent(new Event("change"));}).catch(function(){say("Authoring API unavailable. Start compile/ingest_server.py to enable browser ingest.");});}'
        'loadArticles();if(token)token.addEventListener("change",loadArticles);'
        'target.addEventListener("change",function(){sup.innerHTML="<option value=\\"\\">No existing source selected</option>";'
        'var a=articles[target.value];if(!a)return;(a.sources||[]).forEach(function(s){var o=document.createElement("option");o.value=s;o.textContent=s;sup.appendChild(o);});});'
        # R6/2.1: toggling "New investigation" reveals the required name field and
        # disables the target select (a create ignores + never sends target_slug),
        # while a default Add REQUIRES a target so the client blocks the
        # server-refused empty-target path (CFAR: Codex); default OFF, so create is
        # never the accidental path.
        'var newInv=document.getElementById("new-investigation"),nameRow=document.getElementById("new-investigation-name-row"),nameField=document.getElementById("new-investigation-name");'
        'function syncNewInvestigation(){var on=!!(newInv&&newInv.checked);if(nameRow)nameRow.hidden=!on;if(nameField)nameField.required=on;if(target){target.disabled=on;target.required=!on;}}'
        'if(newInv){newInv.addEventListener("change",syncNewInvestigation);syncNewInvestigation();}'
        # DP-20260710 D4: the Section options track the chosen Org, from the
        # same org_structure data the server validates against (client-side
        # convenience; the server stays the authority).
        + 'var orgSel=document.getElementById("ingest-org"),secSel=document.getElementById("ingest-section");'
        + 'var ORG_SECTIONS=%s,SECTION_LABEL=%s;' % (
            json.dumps(ORG_SECTIONS, sort_keys=True), json.dumps(SECTION_LABEL, sort_keys=True))
        + 'function fillSections(){if(!orgSel||!secSel)return;var opts=ORG_SECTIONS[orgSel.value]||[];'
        'secSel.innerHTML="<option value=\\"\\">Select section…</option>"+opts.map(function(t){'
        'return "<option value=\\""+esc(t)+"\\">"+esc(SECTION_LABEL[t]||t)+"</option>";}).join("");}'
        'if(orgSel){orgSel.addEventListener("change",fillSections);fillSections();}'
        'form.addEventListener("submit",function(e){e.preventDefault();say("Ingesting...");fetch("/api/ingest",{method:"POST",headers:headers(),body:new FormData(form)})'
        '.then(function(r){return r.json().then(function(j){if(!r.ok)throw j;return j;});}).then(reloadWithResult).catch(function(e){say(e);});});'
        'rebuild.addEventListener("click",function(){say("Refreshing status and rebuilding...");fetch("/api/rebuild",{method:"POST",headers:headers()})'
        '.then(function(r){return r.json().then(function(j){if(!r.ok)throw j;return j;});}).then(reloadWithResult).catch(function(e){say(e);});});'
        '})();</script>'
        # fe-ux packet §2.3 state machine: destructive submits are disabled at
        # birth; the ONLY arming expression is sequence-token guarded
        # (previewedSeq===seq), so a stale/out-of-order preview response, a
        # selection change, or a failed preview can never arm a submit.
        '<script>(function(){'
        'var token=document.getElementById("authoring-token"),status=document.getElementById("ingest-status");'
        'function esc(s){return String(s==null?"":s).replace(/[&<>"]/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;","\\"":"&quot;"}[c];});}'
        'function headers(){var h={};if(token&&token.value)h["X-CivWiki-Authoring-Token"]=token.value;return h;}'
        'var seq=0,previewedSeq=-1,articles={};'
        'var modes=Array.prototype.slice.call(document.querySelectorAll("input[name=\\"ingest-mode\\"]"));'
        'var panels=Array.prototype.slice.call(document.querySelectorAll("[data-mode-panel]"));'
        'var el={replace:{form:document.getElementById("replace-form"),target:document.getElementById("rep-target"),source:document.getElementById("rep-source"),panel:document.getElementById("rep-preview"),confirm:document.getElementById("rep-confirm"),submit:document.getElementById("rep-submit")},'
        'remove:{form:document.getElementById("remove-form"),target:document.getElementById("rm-target"),panel:document.getElementById("rm-preview"),confirm:document.getElementById("rm-confirm"),submit:document.getElementById("rm-submit")}};'
        'function currentMode(){var m="add";modes.forEach(function(r){if(r.checked)m=r.value;});return m;}'
        'function disarm(){seq++;previewedSeq=-1;["replace","remove"].forEach(function(m){el[m].confirm.checked=false;el[m].confirm.disabled=true;el[m].submit.disabled=true;});}'
        'function arm(m){el[m].submit.disabled=!(el[m].confirm.checked&&previewedSeq===seq);}'
        'function renderPreview(m,p){if(m==="remove"){var items=(p.inbound||[]).map(function(s){return "<li><a href=\\""+esc(s)+".html\\">"+esc(s)+"</a></li>";}).join("");'
        'return "<p>Retiring <strong>"+esc(p.slug)+"</strong> writes a tombstone at <code>"+esc(p.tombstone)+"</code> and marks <strong>"+esc(String(p.edges_would_pend))+"</strong> inbound edge(s) pending reconciliation:</p><ul>"+(items||"<li>(no inbound articles)</li>")+"</ul><p>A recompile follows. Nothing is deleted.</p>";}'
        'return "<p>Source <code>"+esc(p.superseded)+"</code> is superseded (moved to superseded_sources) and a recompile follows.</p>";}'
        'function fetchPreview(m){var e=el[m];var slug=e.target.value;var src=(m==="replace"&&e.source)?e.source.value:"";'
        'if(!slug||(m==="replace"&&!src)){e.panel.textContent="Select a target"+(m==="replace"?" and source":"")+" to preview consequences.";return;}'
        'var my=++seq;previewedSeq=-1;e.panel.textContent="Loading consequence preview\\u2026";'
        'fetch("/api/preview?operation="+m+"&slug="+encodeURIComponent(slug)+(src?"&source_ref="+encodeURIComponent(src):""),{cache:"no-store",headers:headers()})'
        '.then(function(r){return r.json().then(function(j){if(!r.ok)throw j;return j;});})'
        '.then(function(j){if(my!==seq)return;var p=j&&j.preview;if(!p)throw j;'
        'if(p.refuses){e.panel.innerHTML="<p class=\\"preview-refuses\\">The server would refuse this operation: <strong>"+esc(p.refuses)+"</strong></p>";return;}'
        'e.panel.innerHTML=renderPreview(m,p);previewedSeq=my;e.confirm.disabled=false;})'
        '.catch(function(){if(my!==seq)return;e.panel.textContent="Preview unavailable \\u2014 destructive submit stays disabled.";});}'
        'function showMode(){var m=currentMode();panels.forEach(function(p){p.hidden=p.getAttribute("data-mode-panel")!==m;});disarm();if(m!=="add")fetchPreview(m);}'
        'modes.forEach(function(r){r.addEventListener("change",showMode);});'
        'function loadArticles(){fetch("/api/articles",{cache:"no-store",headers:headers()}).then(function(r){return r.ok?r.json():null}).then(function(j){'
        'if(!j)return;articles={};j.articles.forEach(function(a){articles[a.slug]=a;});refillSources();});}'
        'function refillSources(){var e=el.replace;e.source.innerHTML="<option value=\\"\\">Select a source\\u2026</option>";'
        'var a=articles[e.target.value];if(!a)return;var seen={};'
        '(a.sources||[]).concat(a.raw_documents||[]).forEach(function(s){if(seen[s])return;seen[s]=1;var o=document.createElement("option");o.value=s;o.textContent=s;e.source.appendChild(o);});}'
        'loadArticles();if(token)token.addEventListener("change",loadArticles);'
        'el.replace.target.addEventListener("change",function(){refillSources();disarm();fetchPreview("replace");});'
        'el.replace.source.addEventListener("change",function(){disarm();fetchPreview("replace");});'
        'el.remove.target.addEventListener("change",function(){disarm();fetchPreview("remove");});'
        'el.replace.confirm.addEventListener("change",function(){arm("replace");});'
        'el.remove.confirm.addEventListener("change",function(){arm("remove");});'
        'function wireSubmit(m,url){el[m].form.addEventListener("submit",function(ev){ev.preventDefault();'
        'if(el[m].submit.disabled)return;var fd=new FormData(el[m].form);'
        'status.textContent="recompiling\\u2026 (the rebuild runs inside this request)";el[m].submit.disabled=true;el[m].confirm.disabled=true;'
        'fetch(url,{method:"POST",headers:headers(),body:fd})'
        '.then(function(r){return r.json().then(function(j){return {ok:r.ok,code:r.status,j:j};});})'
        '.then(function(res){if(!res.ok){status.innerHTML="<p>Refused ("+esc(String(res.code))+"): <strong>"+esc((res.j&&res.j.error)||"unknown refusal")+"</strong></p>";}'
        'else{status.innerHTML="<pre>"+esc(JSON.stringify(res.j,null,2))+"</pre>";}'
        'disarm();fetchPreview(m);})'
        '.catch(function(){status.textContent="Request failed \\u2014 state unknown; refresh the page.";disarm();});});}'
        'wireSubmit("replace","/api/replace");wireSubmit("remove","/api/remove");'
        '})();</script>'
    ) % ("".join(article_options), "".join(target_options),
         "".join(target_options))
    return tool_page("Wiki Source Ingest", inner, status)


# ---------------------------------------------------------------- vision board

BOARD_WALL_COLORS = ("purple", "teal", "amber", "coral")


class BoardError(Exception):
    """Fail-closed board authoring error: the build must stop, never render a
    partial board or fall back to the essay (design packet §3)."""


def board_scalar(fm, key):
    m = re.search(r"^%s:[ \t]*(.*)$" % re.escape(key), fm, re.M)
    if not m:
        raise BoardError("board frontmatter missing required key: %s" % key)
    value, _ = split_inline_comment(m.group(1))
    value = value.strip().strip('"').strip("'")
    if not value:
        raise BoardError("board frontmatter key %s is empty (after comment "
                         "stripping)" % key)
    return value


def _board_fields(item, n, what, optional=()):
    fields = item.split("|")
    if len(fields) != n:
        raise BoardError("%s needs exactly %d pipe-delimited fields (literal "
                         "'|' is banned in field copy): %r" % (what, n, item))
    fields = [f.strip() for f in fields]
    for i, f in enumerate(fields):
        if not f and i not in optional:
            raise BoardError("%s field %d is empty — required board copy "
                             "must not be blank (fail-closed)" % (what, i + 1))
    return fields


BOARD_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def _board_slug(slug, what):
    # slug grammar FIRST (allowlist): an existing file with a non-slug stem
    # would reach raw href interpolation — an attribute/scheme injection
    # lane (CFAR 2a-r5)
    if not BOARD_SLUG_RE.match(slug):
        raise BoardError("%s target is not a valid wiki slug ([a-z0-9-]): "
                         "%r" % (what, slug))
    if not (WIKI / ("%s.md" % slug)).exists():
        raise BoardError("%s links to a slug that does not exist in wiki/: "
                         "%r" % (what, slug))
    return slug


def board_search_text(fm):
    """Lenient plain-text extraction of the board copy for the home search
    document (search_text only carries aliases + body; the board lives in
    frontmatter — CFAR 2a-r4). Validation stays build_board's job."""
    parts = []
    for key in ("board_eyebrow", "board_hero", "board_subtitle",
                "board_method", "board_guardrail"):
        try:
            # reuse the renderer's own scalar parser: fm_val pre-strips the
            # leading quote, which defeats quote-aware comment detection
            parts.append(board_scalar(fm, key).replace("|", " "))
        except BoardError:
            pass  # lenient here; build_board enforces
    for key in ("board_pillars", "board_inheritance"):
        parts.extend(item.replace("|", " ") for item in fm_list(fm, key))
    return re.sub(r"\s+", " ", " ".join(p for p in parts if p)).strip()


def build_board(fm):
    """Compose the front-page vision board from index.md frontmatter,
    validating fail-closed (design packet §3/§4). Returns board HTML that the
    caller passes into page(is_home=True); page() stays a dumb frame."""
    eyebrow = html.escape(board_scalar(fm, "board_eyebrow"))
    hero = html.escape(board_scalar(fm, "board_hero"))
    subtitle = html.escape(board_scalar(fm, "board_subtitle"))
    narrative = _board_slug(board_scalar(fm, "board_narrative_link"),
                            "board_narrative_link")
    pillars = []
    raw_pillars = fm_list(fm, "board_pillars")
    if len(raw_pillars) != 4:
        raise BoardError("board_pillars needs exactly 4 entries, got %d"
                         % len(raw_pillars))
    for item in raw_pillars:
        name, objective, hook, slug, color = _board_fields(
            item, 5, "board pillar", optional=(2,))  # only the hook may be blank
        if color not in BOARD_WALL_COLORS:
            raise BoardError("unknown board wall color %r (allowed: %s)"
                             % (color, ", ".join(BOARD_WALL_COLORS)))
        pillars.append((name, objective, hook, _board_slug(slug, name), color))
    colors = [c for _n, _o, _h, _s, c in pillars]
    if len(set(colors)) != 4:
        raise BoardError("board pillar wall colors must be distinct (the "
                         "centerpiece maps walls by color): %s" % colors)
    inheritance = []
    for item in fm_list(fm, "board_inheritance"):
        label, slug = _board_fields(item, 2, "inheritance item")
        inheritance.append((label, _board_slug(slug, label)))
    if not inheritance:
        raise BoardError("board_inheritance must not be empty")
    method_nodes = [n.strip() for n in
                    board_scalar(fm, "board_method").split("→") if n.strip()]
    if not method_nodes:
        raise BoardError("board_method has no pipeline nodes")
    guard_text, guard_slug = _board_fields(
        board_scalar(fm, "board_guardrail"), 2, "board_guardrail")
    guard_slug = _board_slug(guard_slug, "guardrail")

    chips = []
    for i, node in enumerate(method_nodes):
        cls = "board-chip"
        if "gate" in node.lower():
            cls += " board-gate"
        if i == len(method_nodes) - 1:
            cls += " board-certified"
        chips.append('<span class="%s">%s</span>' % (cls, html.escape(node)))
    half = (len(chips) + 1) // 2
    pipeline = ('<div class="board-pipeline-row">%s</div>'
                '<div class="board-pipeline-row">%s</div>'
                % ("".join(chips[:half]), "".join(chips[half:])))

    walls = {c: (n, ) for n, _o, _h, _s, c in pillars}
    def wall(pos, color):
        name = html.escape(walls[color][0])
        return ('<div class="board-wall board-wall-%s board-%s">%s</div>'
                % (pos, color, name))

    pillar_names = ", ".join(n for n, _o, _h, _s, _c in pillars)
    aria = html.escape(
        "Concentric membrane: the human holds top authority; the four "
        "objectives — %s — enclose the agents' work on all sides; work "
        "leaves only as certified or rejected." % pillar_names)
    centerpiece = (
        ('<div class="board-membrane" role="img" aria-label="%s">' % aria)
        + '<div class="board-membrane-label">human · top authority ↓</div>'
        '<div class="board-frame">'
        + wall("top", pillars[0][4]) + wall("left", pillars[3][4])
        + '<div class="board-core">'
          '<div class="board-core-caption">agents at work — every action '
          'leaves evidence</div>' + pipeline +
          '<div class="board-core-exit">work leaves the membrane only as '
          'certified-or-rejected</div></div>'
        + wall("right", pillars[1][4]) + wall("bottom", pillars[2][4])
        + "</div></div>")

    tiles = "".join(
        '<a class="board-tile board-%s" href="%s.html">'
        '<span class="board-tile-hook">%s</span>'
        '<span class="board-tile-name">%s</span>'
        '<span class="board-tile-obj">%s</span>'
        '<span class="board-tile-cta">read the article →</span></a>'
        % (color, slug, html.escape(hook) if hook else "◆",
           html.escape(name), html.escape(objective))
        for name, objective, hook, slug, color in pillars)

    strip = " <span class=\"board-arrow\">→</span> ".join(
        '<a href="%s.html">%s</a>' % (slug, html.escape(label))
        for label, slug in inheritance)

    summary = html.escape(
        "The thesis of the Transpara-AI Civilization arc: agents work "
        "inside a human-governed membrane of %s; work leaves only as "
        "certified or rejected." % pillar_names)
    return (
        '<div class="board">'
        + ('<p class="board-sr">%s</p>' % summary)
        + '<header class="board-hero">'
        '<div class="board-eyebrow">%s</div>'
        '<h2 class="board-claim">%s</h2>'
        '<p class="board-subtitle">%s</p>'
        '<p class="board-narrative"><a href="%s.html">Read the full origin '
        'narrative →</a></p></header>'
        '%s'
        '<nav class="board-tiles" aria-label="The four objectives">%s</nav>'
        '<div class="board-inheritance">inherited, not owned: %s</div>'
        '<footer class="board-guardrail"><a href="%s.html">Cult test</a> — '
        '%s</footer>'
        "</div>"
        % (eyebrow, hero, subtitle, narrative, centerpiece, tiles, strip,
           guard_slug, html.escape(guard_text)))


def page(slug, title, meta, fm, body_html, toc_tokens, links, status, *, is_home=False, extra_head="", main_class="content"):
    sidebar = build_sidebar(slug if not is_home else "")
    infobox = "" if is_home else build_infobox(meta, fm)
    toc = article_toc(meta, toc_tokens, is_home=is_home)
    seealso = "" if is_home else build_seealso(links, slug)
    source_updates = "" if is_home else build_source_update_panel(fm)
    source_panel = "" if is_home else build_source_panel(fm)
    navbox = build_navbox()
    tagline = "" if is_home else '<div class="tagline">%s%s</div>' % (
        ('<span class="tier %s">%s</span> · ' % (html.escape(meta["tier"]), html.escape(meta["tier"]))),
        "an article in the %s" % SITE_NAME)
    h1 = SITE_NAME if is_home else html.escape(title)
    page_title = SITE_NAME if is_home or title == SITE_NAME else ("%s — %s" % (title, SITE_NAME))
    state_banner = "" if is_home else state_banner_html(fm)
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
        '<main class="%s"><h1 class="page-title">%s</h1>%s%s' % (html.escape(main_class), h1, tagline, state_banner) +
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
    body_html, toc_tokens = to_html(body, links, article_source_refs(fm), source_slug=slug)
    # the arc view builds links client-side from data hrefs, bypassing the
    # server-side gate — publish the retired-slug set so its safeHref() renders
    # a retired target as text, never a live link (CFAR r20). Emitted BEFORE
    # the deferred view script so the global is set when it runs.
    retired_slugs = sorted(s for s, m in META.items() if m.get("retired_on"))
    arc_scripts = (
        '<script>window.CIVWIKI_RETIRED_SLUGS=%s;</script>'
        '<script defer src="civilizationOntology.js?v=%s"></script>'
        '<script defer src="civilizationArcData.js?v=%s"></script>'
        '<script defer src="civilizationProgressEvidence.js?v=%s"></script>'
        '<script defer src="civilizationArcView.js?v=%s"></script>'
        % (json.dumps(retired_slugs), ONTO_VER, ARC_DATA_VER, PROGRESS_VER, ARC_VIEW_VER)
    )
    # The one-status legend is static content — the builder emits it; the view
    # script renders only the derived parts (freshness, now-panel, spine).
    legend = (
        '<section class="arc-view-legend" aria-label="Status legend">'
        '<h3>One status vocabulary</h3>'
        '<ul class="arc-legend-list">'
        '<li class="arc-legend-item"><span class="arc-status-dot arc-status-dot-done" aria-hidden="true"></span>done</li>'
        '<li class="arc-legend-item"><span class="arc-status-dot arc-status-dot-active" aria-hidden="true"></span>active</li>'
        '<li class="arc-legend-item"><span class="arc-status-dot arc-status-dot-planned" aria-hidden="true"></span>planned</li>'
        '<li class="arc-legend-item"><span class="arc-status-dot arc-status-dot-future" aria-hidden="true"></span>future</li>'
        '<li class="arc-legend-item"><span class="arc-status-dot arc-status-dot-blocked" aria-hidden="true"></span>'
        'blocked — an overlay with a structured reason, never a lifecycle value</li>'
        '</ul>'
        '<p class="arc-legend-note">Every status is evidence-derived or stamped.</p>'
        '</section>'
    )
    chart = (
        '<section class="wiki-arc-embed" aria-label="Civilization progress chart">'
        '<h2 id="progress-chart">Progress chart</h2>'
        '<p class="wiki-arc-note">This chart is a read lens over the wiki and operation exports. '
        'It is display-only; it is not EventGraph truth, certification evidence, or release authority.</p>'
        '<div data-civilization-arc data-arc-standalone="true" data-arc-live="true"></div>'
        + legend +
        '</section>'
    )
    return page(slug, meta["title"], meta, fm, body_html + chart, toc_tokens, links, status,
                extra_head=arc_scripts, main_class="content arc-content")


def build():
    global CSS_VER, SEARCH_VER, ARC_DATA_VER, ARC_VIEW_VER, ONTO_VER, PROGRESS_VER, REPOS
    # fail closed BEFORE any dist mutation: a malformed board must never
    # leave the served site partially updated (CFAR 2a-r6); the index
    # render below re-runs build_board on the same fm
    build_board(split_fm(INDEX.read_text())[0])
    REPOS = repo_records()
    prepare_dist()
    status = load_status()

    def copy_asset(name):
        asset = (ASSETS / name).read_text()
        write_dist_text(DIST / name, asset)
        return hashlib.md5(asset.encode()).hexdigest()[:8]

    def build_search_index():
        docs = []
        fm, body = split_fm(INDEX.read_text())
        docs.append({
            "slug": "index",
            "title": SITE_NAME,
            "tier": "front page",
            "text": ("%s %s" % (board_search_text(fm),
                                search_text(fm, body)))[:12000],
        })
        for p in sorted(WIKI.glob("*.md")):
            meta = META[p.stem]
            if meta.get("retired_on"):
                continue  # retired tombstones drop from search — the search
                # UI turns index rows into live links; a retired topic is
                # reachable by direct link only, never discoverable (CFAR r11)
            fm, body = split_fm(p.read_text())
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
        write_dist_text(DIST / "search-index.js", asset)
        return hashlib.md5(asset.encode()).hexdigest()[:8]

    CSS_VER = copy_asset("style.css")
    # First pass populates SOURCE_INDEX for search; second pass refreshes source
    # pages after SEARCH_VER is known so the normal page chrome uses cache-busted JS.
    build_source_pages(status)
    SEARCH_VER = build_search_index()
    build_source_pages(status)
    ONTO_VER = copy_asset("civilizationOntology.js")
    ARC_DATA_VER = copy_asset("civilizationArcData.js")
    PROGRESS_VER = copy_asset("civilizationProgressEvidence.js")
    ARC_VIEW_VER = copy_asset("civilizationArcView.js")
    count = 0
    # Raw Area fold (packet D4): collect each article's four-field reference
    # union and its supersession edges during this loop — active pages as live
    # back-links, retired pages as marked non-link references.
    raw_area_refs = {"backlinks": {}, "superseded": set()}
    for p in sorted(WIKI.glob("*.md")):
        fm, body = split_fm(p.read_text())
        meta = META[p.stem]
        raw_area_fold_article(raw_area_refs, fm, p.stem, meta["title"],
                              bool(meta.get("retired_on")))
        body = re.sub(r"^#\s+.*\n", "", body, count=1)
        links = set()
        body_html, toc_tokens = to_html(body, links, article_source_refs(fm),
                                        source_slug=p.stem)
        write_dist_text(
            DIST / ("%s.html" % p.stem),
            page(p.stem, meta["title"], meta, fm, body_html, toc_tokens, links, status),
        )
        count += 1
    fm, body = split_fm(INDEX.read_text())
    body = re.sub(r"^#\s+.*\n", "", body, count=1)
    body_html, _ = to_html(body, set(), article_source_refs(fm), source_slug="index")
    # gate the board's generated links through the SAME fail-closed renderer
    # as article bodies — board tiles to a retired slug must not stay live
    # (CFAR r3 P2-2); the homepage is the most visible generated-link surface
    board_html = gate_internal_links(build_board(fm), source_slug="index")
    write_dist_text(
        DIST / "index.html",
        page("index", SITE_NAME, {}, "", board_html + body_html, [], set(), status, is_home=True),
    )
    write_dist_text(DIST / "sources.html", sources_page(status))
    write_dist_text(DIST / "ingest.html", ingest_page(status))
    raw_model = raw_area_model(ROOT, raw_area_refs)
    for anomaly in raw_model["anomalies"]:
        print("raw-area warning: %s" % anomaly)
    write_dist_text(DIST / "raw.html", raw_page(status, raw_model))
    write_dist_text(DIST / "repos.html", repos_page(status))
    for repo in REPOS:
        write_dist_text(DIST / repo["href"], repo_page(repo, status))
    arc_html = arc_page(status)
    write_dist_text(DIST / "civilization-arc.html", arc_html)
    write_dist_text(DIST / "civilization_arc.html", arc_html)
    prune_dist()
    print("built %d articles + %d repo pages + index + arc -> %s" % (count, len(REPOS), DIST))


if __name__ == "__main__":
    build()
