#!/usr/bin/env python3
"""Link-integrity gate for the Civilization Wiki — fail-closed.

Mirrors compile/build_site.py's wikilink resolution EXACTLY:
  - target regex is [a-z0-9][a-z0-9-]* (caps/space targets are not links),
  - resolution is FILENAME-ONLY (wiki/<target>.md); frontmatter `aliases:` are
    cosmetic and do NOT make a link resolve.

Every [[target]] whose target has no wiki/<target>.md is a RED link. Red links
are allowed ONLY if the target is in ALLOWLIST (intentional, index-declared
forward references). Anything else is a BUG and the gate exits non-zero.

This is the "fix the class, not the instance" guard: it proves over the whole
corpus that no unexpected red link exists, instead of patching the one someone
happened to notice.

Run: python3 compile/check_links.py
"""
import re
import sys
import pathlib
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[1]
WIKI = ROOT / "wiki"
INDEX = ROOT / "index.md"

# Identical to build_site.py's WL regex.
WL = re.compile(r"\[\[([a-z0-9][a-z0-9\-]*)(?:\|([^\]]+))?\]\]")

SLUGS = {p.stem for p in WIKI.glob("*.md")} | {"index"}

# Intentional forward references — red by design, disclosed per article footer
# ("[[wikilinks]] are forward references; several targets may not yet be
# compiled") and index.md "Deferred to later runs". Each entry is a concept the
# corpus names but has not yet given its own article. NOT a place to hide
# wrong-slug mislinks: a target belongs here only if NO existing article is its
# real referent.
ALLOWLIST = {
    # named in index.md "Deferred to later runs"
    "mind-zero",                       # repo-identity tension, unresolved by design
    # uncompiled concepts referenced in article bodies (future-run candidates)
    "acceptance-criteria",
    "release-candidate",
    "self-improvement-circuit-breaker",
    "the-audit",
    "audit-report",
    "social-grammar",
    "openmanus",                       # surveyed tool, no investigation article yet
    "incremental-specification-loading",
    "trace-completeness-gate",
    "test-driven-development",
    "root-cause-analysis",
    "saas-template-v1",
    "mission",
    "fail-closed-gates",
    "diagnostic-traversal",
    # footer syntax-example literal (`[[wikilinks]]`), in ~65 article footers.
    # Intentional documentation convention, out of Tier-1 scope; tracked here so
    # the gate stays green while remaining honest that it renders as a red link.
    "wikilinks",
}

def split_fm(raw):
    # Identical to build_site.py: the leading ---...--- frontmatter block is never
    # rendered, so its [[...]] never become links. Strip it so the gate checks exactly
    # what the renderer publishes (per cross-family review — codex, 2026-06-15).
    if raw.startswith("---"):
        e = raw.find("\n---", 3)
        if e != -1:
            return raw[3:e].strip("\n"), raw[e + 4:].lstrip("\n")
    return "", raw

def scan():
    red = defaultdict(list)  # target -> [(filename, original_lineno)]
    for p in sorted(WIKI.glob("*.md")) + [INDEX]:
        raw = p.read_text()
        _, body = split_fm(raw)
        offset = raw[: len(raw) - len(body)].count("\n")  # lines consumed by frontmatter
        for i, line in enumerate(body.splitlines(), 1):
            for m in WL.finditer(line):
                t = m.group(1)
                if t not in SLUGS:
                    red[t].append((p.name, i + offset))
    return red

def main():
    red = scan()
    dead = sorted(ALLOWLIST - set(red))
    if dead:
        print("WARN: %d ALLOWLIST entr%s match no red link (stale — prune so they can't mask a future body link): %s\n"
              % (len(dead), "y" if len(dead) == 1 else "ies", ", ".join(dead)))
    print("=== RED LINKS (count  [tag]  target) ===")
    for t, locs in sorted(red.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        tag = "OK-deferred" if t in ALLOWLIST else "BUG"
        print("  %4d  [%-11s] %s" % (len(locs), tag, t))
    unexpected = {t: l for t, l in red.items() if t not in ALLOWLIST}
    if unexpected:
        print("\nFAIL: %d unexpected red-link target(s) (wrong slug / mislink):" % len(unexpected))
        for t, locs in sorted(unexpected.items()):
            for f, ln in locs:
                print("    %s:%d  [[%s]]" % (f, ln, t))
        sys.exit(1)
    total = sum(len(v) for v in red.values())
    print("\nOK: every red link (%d targets, %d occurrences) is an intentional forward ref." % (len(red), total))

if __name__ == "__main__":
    main()
