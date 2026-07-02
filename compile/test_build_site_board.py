#!/usr/bin/env python3
"""Stdlib-assert tests for the front-page vision board (Item 2a).

Design packet: docs/superpowers/specs/2026-07-02-front-page-vision-board-packet.md
(AC1-AC10; one named test per AC clause). The board is composed fail-closed by
build_board(fm) BEFORE page(is_home=True); page() stays a dumb frame.
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_site as site  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
REAL_FM = site.split_fm((ROOT / "index.md").read_text())[0]


def good_fm(**over):
    """A minimal valid synthetic board frontmatter (real slugs)."""
    lines = {
        "board_eyebrow": 'board_eyebrow: "a field experiment"',
        "board_hero": 'board_hero: "Agents must live inside the graph."',
        "board_subtitle": 'board_subtitle: "provenance, consent, review, responsibility"',
        "board_narrative_link": "board_narrative_link: arc-origin-narrative",
        "board_pillars": (
            "board_pillars:\n"
            '  - "Accountability|six questions|6|accountable-ai-architecture|purple"\n'
            '  - "Provenance|nothing unsourced||primitive-basis|teal"\n'
            '  - "Governed autonomy|auditable membrane||hive-governance|amber"\n'
            '  - "One civilization|discipline turned inward|1|the-civilization|coral"'
        ),
        "board_inheritance": (
            "board_inheritance:\n"
            '  - "Searles primitives|primitive-basis"\n'
            '  - "Three irreducibles|three-irreducibles"\n'
            '  - "Three evaluative axes|three-evaluative-axes"'
        ),
        "board_method": 'board_method: "intent → order → bounded execution → evidence → gate → certified-or-rejected"',
        "board_guardrail": 'board_guardrail: "If a framework explains everything, distrust it.|the-cult-test"',
    }
    lines.update(over)
    return "\n".join(v for v in lines.values() if v is not None)


# ------------------------------------------------------------------- AC1

def test_home_board_renders_all_sections():
    html_out = site.build_board(REAL_FM)
    assert 'class="board-hero"' in html_out
    assert 'role="img"' in html_out, "centerpiece must be an accessible image"
    assert html_out.count('<a class="board-tile board-') == 4, \
        "exactly four pillar tiles"
    assert 'class="board-inheritance"' in html_out
    assert 'class="board-guardrail"' in html_out
    print("ok test_home_board_renders_all_sections")


# ------------------------------------------------------------------- AC2

def test_home_board_links_resolve():
    html_out = site.build_board(REAL_FM)
    hrefs = set(re.findall(r'href="([^"]+)"', html_out))
    assert hrefs, "board must link out"
    for href in hrefs:
        assert not href.startswith(("http:", "https:")), "board links are local"
        slug = href.rsplit("/", 1)[-1].removesuffix(".html")
        assert (ROOT / "wiki" / ("%s.md" % slug)).exists(), \
            "board link target must exist: %s" % href
    print("ok test_home_board_links_resolve")


# ------------------------------------------------------------------- AC3

def test_home_board_no_contested_hero_number():
    html_out = site.build_board(REAL_FM)
    assert not re.search(r"14\s+invariants", html_out, re.I), \
        "contested number must never appear as a hero token (fail-legible)"
    print("ok test_home_board_no_contested_hero_number")


# ------------------------------------------------------------------- AC4

def test_home_board_fails_closed_on_bad_frontmatter():
    cases = [
        ("missing key", good_fm(board_hero=None)),
        ("empty required scalar", good_fm(board_hero='board_hero: ""')),
        ("scalar reduced to empty by comment",
         good_fm(board_hero="board_hero:  # just a comment")),
        ("wrong pillar count", good_fm(board_pillars=(
            "board_pillars:\n"
            '  - "Accountability|six questions|6|accountable-ai-architecture|purple"'))),
        ("wrong field count / literal pipe", good_fm(board_pillars=(
            "board_pillars:\n"
            '  - "Accountability|six | questions|6|accountable-ai-architecture|purple"\n'
            '  - "Provenance|nothing unsourced||primitive-basis|teal"\n'
            '  - "Governed autonomy|auditable membrane||hive-governance|amber"\n'
            '  - "One civilization|discipline turned inward|1|the-civilization|coral"'))),
        ("unknown wall color", good_fm(board_pillars=(
            "board_pillars:\n"
            '  - "Accountability|six questions|6|accountable-ai-architecture|magenta"\n'
            '  - "Provenance|nothing unsourced||primitive-basis|teal"\n'
            '  - "Governed autonomy|auditable membrane||hive-governance|amber"\n'
            '  - "One civilization|discipline turned inward|1|the-civilization|coral"'))),
        ("dangling slug", good_fm(board_narrative_link=
                                  "board_narrative_link: no-such-article")),
        ("duplicate wall color (would silently mislabel the centerpiece)",
         good_fm(board_pillars=(
            "board_pillars:\n"
            '  - "Accountability|six questions|6|accountable-ai-architecture|teal"\n'
            '  - "Provenance|nothing unsourced||primitive-basis|teal"\n'
            '  - "Governed autonomy|auditable membrane||hive-governance|amber"\n'
            '  - "One civilization|discipline turned inward|1|the-civilization|coral"'))),
    ]
    for name, fm in cases:
        try:
            site.build_board(fm)
        except site.BoardError:
            continue
        raise AssertionError("board must fail closed on: %s" % name)
    print("ok test_home_board_fails_closed_on_bad_frontmatter")


# ------------------------------------------------------------------- AC5

def test_home_board_airgap_and_no_js():
    html_out = site.build_board(REAL_FM)
    assert "<script" not in html_out, "the board introduces no scripts"
    assert "http://" not in html_out and "https://" not in html_out, \
        "the board references no external resources"
    css = (ROOT / "compile" / "assets" / "style.css").read_text()
    board_css = css[css.index(".board-"):] if ".board-" in css else ""
    assert board_css, "board CSS must exist under the .board- prefix"
    assert "url(http" not in board_css, "no external URLs in board CSS"
    assert "@import" not in board_css, "no CSS imports in board CSS"
    print("ok test_home_board_airgap_and_no_js")


# ------------------------------------------------------------------- AC6

def test_narrative_article_moved_and_linked():
    art = ROOT / "wiki" / "arc-origin-narrative.md"
    assert art.exists(), "the narrative article must exist"
    body = art.read_text()
    assert "memory and interpretation layer" in body, \
        "the essay moved wholesale, not paraphrased"
    index_body = site.split_fm((ROOT / "index.md").read_text())[1]
    assert "memory and interpretation layer" not in index_body, \
        "the essay must no longer live in index.md"
    html_out = site.build_board(REAL_FM)
    assert 'href="arc-origin-narrative.html"' in html_out, \
        "the board links to the narrative"
    # CFAR 2a-r1 P1: compile/refresh.py rewrites the stats block in INDEX.md
    # and hard-fails without exactly one marker pair — the live 15-min
    # refresh loop and the ingest/rebuild endpoint both run that path
    index_text = (ROOT / "index.md").read_text()
    assert index_text.count("stats:begin") == 1 and \
        index_text.count("stats:end") == 1, \
        "index.md must keep exactly one stats marker pair for refresh.py"
    assert "stats:begin" not in body, \
        "the archived narrative must not carry live stats markers"
    print("ok test_narrative_article_moved_and_linked")


# ------------------------------------------------------------------- AC8

def test_home_board_theme_neutral_markup():
    html_out = site.build_board(REAL_FM)
    assert "style=" not in html_out, \
        "theme adaptation is CSS-custom-property work; no inline styles"
    assert "data-theme" not in html_out, "no theme-conditional markup"
    print("ok test_home_board_theme_neutral_markup")


# ------------------------------------------------------------------- AC9

def test_home_board_content_is_frontmatter_driven():
    marker = "XDRIVENX"
    fm = good_fm(board_hero='board_hero: "%s hero claim"' % marker,
                 board_method='board_method: "%s method flow"' % marker)
    html_out = site.build_board(fm)
    assert html_out.count(marker) >= 2, \
        "frontmatter values must drive the render (no Python constants)"
    real = site.build_board(REAL_FM)
    assert marker not in real, "no fallback constants leak between builds"
    print("ok test_home_board_content_is_frontmatter_driven")


# ------------------------------------------------------------------ AC10

def test_home_board_accessibility():
    html_out = site.build_board(REAL_FM)
    assert 'class="board-sr"' in html_out, \
        "a visually-hidden one-sentence summary must lead the board"
    assert "aria-label=" in html_out, "the centerpiece needs an aria-label"
    # CFAR 2a-r1 P2: the aria-label and hidden summary derive from the
    # PARSED pillars — frontmatter edits must reach screen readers too
    fm = good_fm(board_pillars=(
        "board_pillars:\n"
        '  - "Zeta Wall|obj a|6|accountable-ai-architecture|purple"\n'
        '  - "Provenance|obj b||primitive-basis|teal"\n'
        '  - "Governed autonomy|obj c||hive-governance|amber"\n'
        '  - "One civilization|obj d|1|the-civilization|coral"'))
    edited = site.build_board(fm)
    aria = re.search(r'aria-label="([^"]+)"', edited).group(1)
    assert "Zeta Wall" in aria, \
        "aria-label must announce the frontmatter pillar names"
    sr = re.search(r'class="board-sr">([^<]+)<', edited).group(1)
    assert "Zeta Wall" in sr, \
        "the hidden summary must announce the frontmatter pillar names"
    for m in re.finditer(r'<a class="board-tile[^>]*>(.*?)</a>', html_out,
                         re.S):
        text = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        assert text, "every tile link needs discernible text"
    print("ok test_home_board_accessibility")


# ------------------------------------------- integration: board in dist

def test_home_board_in_dist():
    dist_index = ROOT / "dist" / "index.html"
    assert dist_index.exists(), \
        "dist/index.html missing — run `npm run build` before test:py " \
        "(CI builds first; the gate must see the emitted page)"
    emitted = dist_index.read_text()
    assert 'class="board-hero"' in emitted and 'class="board-guardrail"' in emitted, \
        "the emitted home page must carry the board"
    print("ok test_home_board_in_dist")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
    print("\nall %d board tests passed" % len(fns))
