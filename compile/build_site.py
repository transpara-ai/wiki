#!/usr/bin/env python3
"""Build the served Civilization Wiki site from wiki/*.md + index.md, Wikipedia-style.

Layout per page: persistent left sidebar (articles grouped by tier) + main column with
title, right-floated infobox (from frontmatter), auto table of contents, rendered body,
"See also", and a bottom category index navbox. Blue links resolve; red links are TBD.

Deterministic: Python stdlib + python-markdown only. No network, no LLM, no push.
"""
import re
import json
import html
import hashlib
import pathlib
import markdown

ROOT = pathlib.Path(__file__).resolve().parents[1]
WIKI = ROOT / "wiki"
DIST = ROOT / "dist"
ASSETS = ROOT / "compile" / "assets"
STATUS = ROOT / "compile" / "refresh-status.json"
INDEX = ROOT / "index.md"
CSS_VER = ""

TIER_ORDER = ["foundational", "architecture", "arc", "investigation", "concept"]
TIER_LABEL = {
    "foundational": "Foundational — source philosophy",
    "architecture": "Architecture",
    "arc": "The dark-factory arc",
    "investigation": "Investigations",
    "concept": "Concepts",
}

WL = re.compile(r"\[\[([a-z0-9][a-z0-9\-]*)(?:\|([^\]]+))?\]\]")
RUNTOK = re.compile(r"@@WL(\d+)@@")


def split_fm(raw):
    if raw.startswith("---"):
        e = raw.find("\n---", 3)
        if e != -1:
            return raw[3:e].strip("\n"), raw[e + 4:].lstrip("\n")
    return "", raw


def fm_val(fm, key):
    m = re.search(r"^%s:[ \t]*(.+)$" % re.escape(key), fm, re.M)
    return m.group(1).strip().strip('"') if m else ""


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
            items.append(re.sub(r"^[ \t]+-\s+", "", line).split("#")[0].strip().strip('"'))
        elif re.match(r"^[A-Za-z_]", line):
            break
    return items


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


MD = markdown.Markdown(extensions=["extra", "sane_lists", "toc"])


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
    return out, list(getattr(MD, "toc_tokens", []) or [])


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


def build_sidebar(current):
    out = ['<nav class="sidebar"><div class="side-home"><a href="index.html">The arc</a><span>home</span></div>']
    for tier in TIER_ORDER:
        arts = sorted([m for m in META.values() if m["tier"] == tier], key=lambda m: m["title"].lower())
        if not arts:
            continue
        out.append('<div class="side-group"><h6>%s</h6><ul>' % html.escape(TIER_LABEL.get(tier, tier)))
        for a in arts:
            cls = ' class="current"' if a["slug"] == current else ""
            out.append('<li><a%s href="%s.html">%s</a></li>' % (cls, a["slug"], html.escape(a["title"])))
        out.append("</ul></div>")
    out.append("</nav>")
    return "".join(out)


def build_navbox():
    out = ['<nav class="navbox"><div class="navbox-title">Civilization Wiki — index</div><div class="navbox-body">']
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
    if not rows:
        return ""
    return ('<aside class="infobox"><div class="infobox-title">%s</div><table>%s</table>'
            '<div class="infobox-foot">part of <a href="index.html">the arc</a></div></aside>'
            % (html.escape(meta["title"]), "".join(rows)))


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
    cls = "warn" if stale else "ok"
    return '<span class="fresh %s">updated %s · %d stale</span>' % (cls, html.escape(synced), len(stale))


def page(slug, title, meta, fm, body_html, toc_tokens, links, status, *, is_home=False):
    sidebar = build_sidebar(slug if not is_home else "")
    infobox = "" if is_home else build_infobox(meta, fm)
    toc = "" if is_home else build_toc(toc_tokens)
    seealso = "" if is_home else build_seealso(links, slug)
    navbox = build_navbox()
    tagline = "" if is_home else '<div class="tagline">%s%s</div>' % (
        ('<span class="tier %s">%s</span> · ' % (html.escape(meta["tier"]), html.escape(meta["tier"]))),
        "an article in the Civilization Wiki")
    h1 = "Civilization Wiki" if is_home else html.escape(title)
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>%s — Civilization Wiki</title>' % html.escape(title) +
        '<link rel="stylesheet" href="style.css?v=%s"></head><body>' % CSS_VER +
        '<header class="topbar"><a class="brand" href="index.html">Civilization Wiki</a>'
        '<div class="top-meta">%s</div></header>' % freshness(status) +
        '<div class="layout">%s' % sidebar +
        '<main class="content"><h1 class="page-title">%s</h1>%s' % (h1, tagline) +
        '%s%s' % (infobox, toc) +
        '<article class="body">%s</article>%s%s' % (body_html, seealso, navbox) +
        '<footer class="page-foot">Generated from <code>wiki/</code> + <code>index.md</code> · '
        'a Karpathy-style LLM wiki · fail-legible: gaps are TBD, conflicts are stated.</footer>'
        '</main></div></body></html>'
    )


def build():
    global CSS_VER
    DIST.mkdir(exist_ok=True)
    status = load_status()
    css = (ASSETS / "style.css").read_text()
    (DIST / "style.css").write_text(css)
    CSS_VER = hashlib.md5(css.encode()).hexdigest()[:8]
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
        page("index", "The arc", {}, "", body_html, [], set(), status, is_home=True))
    print("built %d articles + index -> %s" % (count, DIST))


if __name__ == "__main__":
    build()
