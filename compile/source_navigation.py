"""Resolve source-document navigation only to already published destinations."""
from html import escape
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import quote, unquote, urljoin, urlsplit, urlunsplit


class ElementIds(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.ids = set()
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        value = attrs.get("id") or (attrs.get("name") if tag == "a" else None)
        if value:
            self.ids.add(value)


def resolve_link(href, source_path, viewer_route, source_routes, published, fragments):
    """Return a served URL, an external URL, or None for an unavailable target."""
    url = urlsplit(href)
    if url.scheme or url.netloc:
        return href if url.scheme.lower() in ("", "http", "https", "mailto") else None
    path = unquote(url.path)
    if not path:
        route = viewer_route
    else:
        candidate = Path(path) if path.startswith("/") else source_path.parent / path
        route = source_routes.get(candidate.resolve())
        if route is None:
            # Code-reference links are emitted relative to the site root.
            root_route = "/" + path.lstrip("/")
            if path.startswith(("/", "source/")) and root_route in published:
                route = root_route
            else:
                route = urlsplit(urljoin(viewer_route, url.path)).path
    if route.endswith("/"):
        route += "index.html"
    if route not in published:
        return None
    fragment = unquote(url.fragment)
    if fragment and published[route].suffix == ".html":
        if route not in fragments:
            fragments[route] = ElementIds(published[route].read_text()).ids
        ids = fragments[route]
        if fragment not in ids:
            # Markdown heading generators collapse repeated hyphens. Repair
            # only an unambiguous spelling difference; never invent a section.
            normalized = re.sub(r"-+", "-", fragment)
            matches = [item for item in ids if re.sub(r"-+", "-", item) == normalized]
            if len(matches) != 1:
                return None
            fragment = matches[0]
    return urlunsplit(("", "", route, url.query, quote(fragment, safe="-._~:")))


class SourceNavigation(HTMLParser):
    def __init__(self, resolve):
        super().__init__(convert_charrefs=False)
        self.resolve = resolve
        self.out = []
        self.anchors = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "a" and "href" in values:
            destination = None if values.get("data-unsafe-uri") else self.resolve(values["href"])
            if destination is None:
                self.out.append('<span class="wl-pending source-unavailable" title="Unavailable reference: %s">'
                                % escape(values["href"], quote=True))
                self.anchors.append(False)
            else:
                self.out.append("<a" + "".join(
                    ' %s="%s"' % (key, escape(destination if key == "href" else value or "", quote=True))
                    for key, value in attrs) + ">")
                self.anchors.append(True)
        elif tag == "a":
            self.anchors.append(True)
            self.out.append(self.get_starttag_text())
        elif tag == "img" and "src" in values:
            destination = None if values.get("data-unsafe-uri") else self.resolve(values["src"])
            if destination and urlsplit(destination).path.endswith(".html"):
                destination = None
            if destination is None:
                self.out.append('<span class="wl-pending source-unavailable">%s (image unavailable)</span>'
                                % escape(values.get("alt") or "Image"))
            else:
                self.out.append("<img" + "".join(
                    ' %s="%s"' % (key, escape(destination if key == "src" else value or "", quote=True))
                    for key, value in attrs) + ">")
        else:
            self.out.append(self.get_starttag_text())

    def handle_endtag(self, tag):
        if tag == "a" and self.anchors:
            self.out.append("</a>" if self.anchors.pop() else " <small>(unavailable)</small></span>")
        else:
            self.out.append("</%s>" % tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag == "a":
            self.handle_endtag(tag)

    def handle_data(self, data):
        self.out.append(data)

    def handle_entityref(self, name):
        self.out.append("&%s;" % name)

    def handle_charref(self, name):
        self.out.append("&#%s;" % name)

    def handle_comment(self, data):
        self.out.append("<!--%s-->" % data)

    def rewrite(self, text):
        self.feed(text)
        self.close()
        return "".join(self.out)
