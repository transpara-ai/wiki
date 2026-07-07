#!/usr/bin/env python3
"""Stdlib-assert tests for the ingest UX surface + honest-state styling.

fe-ux packet AC1/AC2/AC4/AC5/AC8 (TAI-WIKI-FRONTEND-UX,
docs/superpowers/specs/2026-07-06-front-end-ux-packet.md). Runs after
`npm run build` (verify orders the build first) so dist/ assertions see a
fresh page.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_site  # noqa: E402


def ingest_html():
    page = DIST / "ingest.html"
    assert page.exists(), "dist/ingest.html missing — run npm run build"
    return page.read_text()


def test_ingest_page_mode_selector():
    html = ingest_html()
    # AC1: three modes, Add default, destructive panels distinct + hidden
    assert html.count('name="ingest-mode"') == 3
    assert 'value="add" checked' in html
    for mode in ("replace", "remove"):
        assert 'value="%s"' % mode in html
        assert 'data-mode-panel="%s"' % mode in html
    assert html.count("ingest-destructive") >= 2
    # destructive panels are hidden at birth (Add is the default)
    assert 'data-mode-panel="replace" hidden' in html
    assert 'data-mode-panel="remove" hidden' in html
    # the Q2 boundary line: the page never handles the operation artifact
    assert "never reads, checks, or transmits the operation authorization" in html
    # remove collects no reason: the rationale is bound to the artifact
    assert "bound to the authorization artifact" in html
    print("ok test_ingest_page_mode_selector")


def test_preview_gate_scaffold_fail_closed():
    html = ingest_html()
    # AC2: destructive submits disabled at birth
    assert 'id="rep-submit" disabled' in html
    assert 'id="rm-submit" disabled' in html
    # confirms disabled at birth too — arming requires a rendered preview
    assert 'id="rep-confirm" type="checkbox" disabled' in html
    assert 'id="rm-confirm" type="checkbox" disabled' in html
    # the ONLY arming expression is sequence-token guarded; no bare enable
    assert "previewedSeq===seq" in html, "arming must be sequence-token guarded"
    assert ".submit.disabled=false" not in html
    assert "submit.disabled = false" not in html
    # stale responses are discarded by token mismatch
    assert "my!==seq" in html, "stale/out-of-order responses must be discarded"
    # preview failure keeps the gate closed, explicitly
    assert "Preview unavailable" in html
    print("ok test_preview_gate_scaffold_fail_closed")


def test_ingest_page_renders_refusal_and_recompiling_states():
    html = ingest_html()
    # AC4: refusals surface escaped with their status code; in-flight state
    # is an explicit recompiling notice (the rebuild runs inside the request)
    assert "Refused (" in html
    assert "recompiling" in html
    print("ok test_ingest_page_renders_refusal_and_recompiling_states")


def test_freshness_pending_chip_domain():
    # AC5 domain: 0 -> absent; N -> warn chip with N; only dangling-pending
    # counts. (Corrupt edge-states cannot reach this renderer: the module
    # import already refused via ingest_ops.load_edge_states — asserted below.)
    chip = build_site.pending_edges_chip
    assert chip({}) == ""
    one = {"a->b": {"state": "dangling-pending", "queued": True}}
    out = chip(one)
    assert "1 edge pending reconciliation" in out and "warn" in out
    mixed = {
        "a->b": {"state": "dangling-pending", "queued": True},
        "c->d": {"state": "valid", "queued": False},
        "e->f": {"state": "cleanly-removed", "queued": False},
        "g->h": {"state": "dangling-pending", "queued": False},
    }
    assert "2 edges pending reconciliation" in chip(mixed)
    # the chip is wired into the site-wide freshness banner
    src = (ROOT / "compile" / "build_site.py").read_text()
    fresh_seg = src.split("def freshness(", 1)[1].split("\ndef ", 1)[0]
    assert "pending_edges_chip" in fresh_seg
    # and the module's edge-states load is the strict fail-closed one
    assert "ingest_ops.load_edge_states(EDGE_STATES_PATH)" in src
    print("ok test_freshness_pending_chip_domain")


def test_style_sheet_covers_emitted_state_classes():
    # AC8 / R4 / R5 guard: every emitted honest-state class has sheet rules,
    # so an emitted-but-unstyled state class can never silently recur.
    sheet = (ROOT / "compile" / "assets" / "style.css").read_text()
    for cls in ("deploy-foot", "deploy-blocked", "wl-pending",
                "ingest-modes", "ingest-destructive", "consequence-panel",
                "preview-refuses", "pending-edges",
                "source-superseded", "source-superseded-badge"):
        assert ".%s" % cls in sheet, "emitted state class unstyled: .%s" % cls
    print("ok test_style_sheet_covers_emitted_state_classes")


def test_token_field_shared_across_modes_and_sources_union():
    # CFAR r1 P2 (token): the authoring-token input must live OUTSIDE the
    # mode panels — a user starting in Replace/Remove needs it visible
    html = ingest_html()
    token_at = html.index('id="authoring-token"')
    first_panel_at = html.index("data-mode-panel=")
    assert token_at < first_panel_at, \
        "authoring token must precede (sit outside) the mode panels"
    # CFAR r1 P2 (selector): the replace source fill must union sources +
    # raw_documents — the backend accepts either
    assert "raw_documents" in html, \
        "replace source selector must offer raw_documents refs too"
    print("ok test_token_field_shared_across_modes_and_sources_union")


def test_superseded_sources_render_badged():
    # wiki#60: a source named as supersedes-target by another entry's
    # annotation renders de-emphasized with an explicit badge — driven
    # entirely by the existing frontmatter annotations, zero article-byte
    # churn. The superseding (current) entry stays plain.
    import re
    page = (DIST / "hermes-agent.html").read_text()
    panel = re.search(r'<details class="source-panel">.*?</details>', page, re.S).group(0)
    lis = re.findall(r"<li[^>]*>.*?</li>", panel, re.S)
    old_li = [li for li in lis if "Capability Evaluation v1.0.0</a>" in li]
    new_li = [li for li in lis if "Capability Evaluation v1.0.1</a>" in li]
    assert old_li and new_li, "both lineage entries must render"
    assert 'class="source-superseded"' in old_li[0], "old ref de-emphasized"
    assert "superseded by" in old_li[0], "old ref carries the badge"
    assert "source-superseded" not in new_li[0], "current entry stays plain"
    # allowlist direction: entries with no annotation are never marked
    plain = [li for li in lis if "source-superseded" not in li]
    assert len(plain) == len(lis) - 1, "exactly one superseded entry on this page"
    # CFAR r1: free-text refs with spaces are captured to the ';' boundary
    st = build_site._supersedes_target
    assert st("added 2026-07-07; supersedes: GitHub API: repos/x/y (live)") \
        == "GitHub API: repos/x/y (live)"
    # ready-state CFAR: only a standalone FINAL segment counts — the phrase
    # mid-note, non-final, or repeated is ambiguous free text and marks nothing
    assert st("note: this supersedes: that idea; supersedes: raw/x.md") == ""
    assert st("note: mentions supersedes: raw/x.md mid-text") == ""
    assert st("supersedes: raw/x.md; note: trailing") == ""
    assert st("no annotation here") == ""
    print("ok test_superseded_sources_render_badged")



if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
    print("\nall %d ingest-ux tests passed" % len(fns))
