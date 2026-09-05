#!/usr/bin/env python3
"""Build and compare an isolated authoring-local candidate without cutover."""
from html.parser import HTMLParser
import argparse
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
import urllib.parse

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from article_catalog import load_catalog  # noqa: E402


ROOT = pathlib.Path(__file__).resolve().parents[1]
BUILDER = ROOT / "compile" / "build_site.py"
BASELINE_ROUTES = (
    ROOT / "docs" / "superpowers" / "plans" /
    "2026-09-05-multi-space-wiki-baseline-routes.txt"
)
OPERATIONAL_STATE = {"deploy-status.json", "inflight.json"}


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.values = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if value and key.lower() in {"href", "src", "xlink:href"}:
                self.values.append(value)


def direct_dist(name):
    path = (ROOT / name).resolve()
    if path.parent != ROOT.resolve() or not path.name.startswith("dist"):
        raise ValueError("shadow paths must be dist* directories directly under %s" % ROOT)
    return path


def files(root):
    return {str(path.relative_to(root)): path for path in root.rglob("*") if path.is_file()}


def inventory_hash(names):
    payload = "".join("%s\n" % name for name in sorted(names)).encode()
    return hashlib.sha256(payload).hexdigest()


def sync_operational_state(active, candidate):
    candidate.mkdir(exist_ok=True)
    for name in OPERATIONAL_STATE:
        src, dst = active / name, candidate / name
        if src.is_file():
            shutil.copy2(src, dst)
        elif dst.exists():
            dst.unlink()


def assert_links_resolve(candidate):
    failures = []
    for page in sorted(candidate.rglob("*.html")):
        rel = page.relative_to(candidate)
        # Source and sibling-repository mirrors intentionally preserve links
        # whose targets live in their owning source repository.
        if rel.parts[0] == "source" or rel.name.startswith("repo-"):
            continue
        parser = Links()
        parser.feed(page.read_text(errors="replace"))
        route = "/" + str(rel)
        for value in parser.values:
            parsed = urllib.parse.urlsplit(value)
            if parsed.scheme or value.startswith(("#", "//")):
                continue
            target = urllib.parse.urljoin(route, parsed.path).lstrip("/")
            if not target or target.startswith("api/"):
                continue
            path = candidate / target
            if target.endswith("/"):
                path = path / "index.html"
            if not path.exists():
                failures.append("%s -> %s" % (rel, value))
    if failures:
        raise AssertionError("candidate has unresolved generated links:\n" +
                             "\n".join(failures[:50]))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--active", default="dist")
    parser.add_argument("--candidate", default="dist-next")
    args = parser.parse_args(argv)
    active, candidate = direct_dist(args.active), direct_dist(args.candidate)
    if active == candidate:
        raise ValueError("active and candidate outputs must differ")
    if not (active / "index.html").is_file():
        raise RuntimeError("active build is missing; build dist before shadow verification")

    sync_operational_state(active, candidate)
    proc = subprocess.run(
        [sys.executable, str(BUILDER), "--profile", "authoring-local",
         "--output", candidate.name],
        cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode:
        raise RuntimeError("candidate build failed; active output was untouched:\n%s" %
                           (proc.stderr or proc.stdout))

    active_files, candidate_files = files(active), files(candidate)
    if set(active_files) != set(candidate_files):
        raise AssertionError(json.dumps({
            "missing_from_candidate": sorted(set(active_files) - set(candidate_files)),
            "candidate_only": sorted(set(candidate_files) - set(active_files)),
        }, indent=2))
    mismatches = [name for name in sorted(active_files)
                  if active_files[name].read_bytes() != candidate_files[name].read_bytes()]
    if mismatches:
        raise AssertionError("candidate differs from active build: %s" % mismatches[:50])

    baseline = {line.strip() for line in BASELINE_ROUTES.read_text().splitlines()
                if line.strip() and not line.startswith("#")}
    html_routes = {name for name in candidate_files if name.endswith(".html")}
    missing_baseline = sorted(baseline - html_routes)
    if missing_baseline:
        raise AssertionError("candidate lost baseline routes: %s" % missing_baseline)

    catalog = load_catalog(ROOT, require_explicit=True)
    missing_articles = sorted(record.slug for record in catalog
                              if "%s.html" % record.slug not in html_routes)
    if missing_articles:
        raise AssertionError("candidate lost canonical articles: %s" % missing_articles)
    assert_links_resolve(candidate)

    summary = {
        "profile": "authoring-local",
        "active": active.name,
        "candidate": candidate.name,
        "canonical_articles": len(catalog),
        "files": len(candidate_files),
        "html_routes": len(html_routes),
        "baseline_routes_preserved": len(baseline),
        "inventory_sha256": inventory_hash(candidate_files),
        "html_inventory_sha256": inventory_hash(html_routes),
        "byte_equivalent_to_active": True,
        "local_links_resolve": True,
        "active_output_mutated": False,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
