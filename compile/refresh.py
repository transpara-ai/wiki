#!/usr/bin/env python3
"""Deterministic refresh for the Transpara Knowledge Hub.

What it DOES (cheap, deterministic, safe to run unattended):
  1. Mirror first-party dark-factory markdown into raw/transpara/ (makes provenance real + trackable).
  2. Hash all raw/ sources, diff against the last snapshot -> which sources changed.
  3. Map changed sources -> stale wiki articles (articles whose `sources:` cite a changed file).
  4. Write compile/refresh-status.json (the fail-loud freshness signal the site shows).
  5. Regenerate the served site (compile/build_site.py).

What it does NOT do (by design — honors the standing rules):
  * No LLM re-compile of article CONTENT (that is expensive + autonomous spend) -> manual, see REBUILD.md.
  * No git commit, no push, no merge. It only updates local working files.
  * Open Brain deltas are NOT auto-detected here (that needs an LLM/MCP run); flagged in the status note.
"""
import json
import sys
import hashlib
import subprocess
import pathlib
import datetime
import re
import os

import stats
from article_catalog import load_catalog

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "raw"
WIKI = ROOT / "wiki"
DF = pathlib.Path(
    os.environ.get("KNOWLEDGE_HUB_DARK_FACTORY_SOURCE", "")
    or os.environ.get("CIVWIKI_DARK_FACTORY_SOURCE", "")
    or "/Transpara/transpara-ai/repos/docs/dark-factory"
)
SNAP = ROOT / "compile" / "source-snapshot.json"
STATUS = ROOT / "compile" / "refresh-status.json"


def sh(*a):
    return subprocess.run(list(a), capture_output=True, text=True)


def mirror_sources():
    dst = RAW / "transpara" / "dark-factory"
    dst.mkdir(parents=True, exist_ok=True)
    if DF.exists():
        try:
            out = sh("rsync", "-a", "--delete", "--prune-empty-dirs",
                     "--include=*/", "--include=*.md",
                     "--include=.civilization-archive.json", "--exclude=*",
                     str(DF) + "/", str(dst) + "/")
        except FileNotFoundError as e:
            print("refresh: source mirror skipped: %s" % e, file=sys.stderr)
            return
        if out.returncode != 0:
            print("refresh: source mirror warning: %s" %
                  ((out.stderr or out.stdout).strip() or "rsync failed"), file=sys.stderr)


def hash_sources():
    h = {}
    candidates = list(RAW.rglob("*.md"))
    boundary = RAW / "transpara" / "dark-factory" / ".civilization-archive.json"
    if boundary.exists():
        candidates.append(boundary)
    for p in candidates:
        try:
            h[str(p.relative_to(ROOT))] = hashlib.sha256(p.read_bytes()).hexdigest()
        except Exception:
            pass
    return h


def article_sources():
    out = {}
    for record in load_catalog(ROOT):
        out[record.slug] = {
            ref for ref in record.sources if ref.startswith("raw/")
        }
    return out


def main():
    mirror_sources()
    cur = hash_sources()
    prev = {}
    if SNAP.exists():
        try:
            prev = json.loads(SNAP.read_text())
        except Exception:
            prev = {}
    changed = {k for k, v in cur.items() if prev.get(k) != v}
    arts = article_sources()
    changed_articles = []
    if prev:  # first run has no baseline -> nothing "stale" yet
        for slug, cites in arts.items():
            for c in cites:
                if any(c in ch or ch in c for ch in changed):
                    changed_articles.append(slug)
                    break
    changed_articles = sorted(set(changed_articles))

    # Single source of stats compute (pure, ground-truth from wiki/ frontmatter).
    counts = stats.compute_counts(ROOT)
    try:
        stats.ensure_nonzero(counts)
    except ValueError as e:
        print("refresh: %s" % e)
        sys.exit(1)

    final_status = {
        "synced": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "article_count": counts["article_count"],
        "space_counts": counts["space_counts"],
        "section_counts": counts["section_counts"],
        "sources_total": len(cur),
        "sources_changed": (len(changed) if prev else 0),
        "changed_articles": changed_articles,
        "stale_articles": [],
        "note": "deterministic refresh completed; source changes are reflected in the rendered site. LLM article synthesis remains manual (see compile/REBUILD.md); Open Brain deltas not auto-detected",
    }
    stats.atomic_write_text(STATUS, json.dumps(final_status, indent=2))

    # Durable, idempotent stats block in the committed index.md (you commit the diff).
    try:
        civilization_index = ROOT / "spaces" / "civilization" / "index.md"
        if not civilization_index.exists():  # isolated legacy fixtures
            civilization_index = ROOT / "index.md"
        index_changed = stats.write_index_block(civilization_index, counts)
    except ValueError as e:
        print("refresh: index.md stats block FAILED — %s" % e)
        sys.exit(1)

    out = sh("python3", str(ROOT / "compile" / "build_site.py"))
    print(out.stdout.strip() or out.stderr.strip())
    if out.returncode != 0:
        failed_status = dict(final_status)
        failed_status["stale_articles"] = changed_articles
        failed_status["note"] = (
            "deterministic refresh failed before the rendered site was updated; "
            "listed articles still need a successful rebuild. LLM article synthesis "
            "remains manual (see compile/REBUILD.md); Open Brain deltas not auto-detected"
        )
        stats.atomic_write_text(STATUS, json.dumps(failed_status, indent=2))
        sys.exit(out.returncode)

    # Advance the source-diff baseline only after all durable writes and the
    # rendered site build succeed; otherwise the stale signal must remain live
    # for the next retry.
    stats.atomic_write_text(SNAP, json.dumps(cur, indent=2))
    print("refresh: %d articles, %d sources changed, 0 stale, %d changed article%s rebuilt; index.md %s" %
          (counts["article_count"], final_status["sources_changed"], len(changed_articles),
           "" if len(changed_articles) == 1 else "s",
           "updated" if index_changed else "unchanged"))


if __name__ == "__main__":
    main()
