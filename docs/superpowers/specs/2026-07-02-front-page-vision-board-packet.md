---
doc_id: TAI-WIKI-FRONT-PAGE-BOARD
title: Front-Page Vision Board — TLC Design Packet (Item 2a)
doc_type: design
version: 0.2.0
status: draft
canonical: false
created: 2026-07-02
updated: 2026-07-02
owner: Michael Saucier
steward: Claude (Fable 5)
authority: planning
tlc_stage: design
source_of_intent:
  - docs/superpowers/specs/2026-07-01-front-page-vision-board-design.md (the v0.1 brainstorm spec, published via PR #42; content spine, visual direction, and fail-legible rules locked with the owner 2026-07-01)
  - operator directive 2026-07-02 — program-level AuthorityDecision "complete this wiki refactor without further intervention … use the TLC process" (Open Brain marker wiki-refactor-overnight-GO; autonomous decisions reviewable after the fact)
intake_channel: A (human request)
---

# Front-Page Vision Board — TLC Design Packet (Item 2a)

> Refines the v0.1 spec into a buildable, test-first contract. The v0.1 spec
> carries the rationale and locked content spine; this packet adds the §9
> decision record, the data schema, the acceptance criteria, and the named
> tests. Build authorized by the operator directive above; scope stays §7.

## 1. §9 decision record (autonomous, per the 2026-07-02 grant)

| §9 question | Decision | Why |
|---|---|---|
| Pillar link targets | `accountable-ai-architecture` · `primitive-basis` · `hive-governance` · `the-civilization` | the spec's primary proposals; all four verified to exist in `wiki/`; no invented articles (`authority-layer` is reachable from `hive-governance`) |
| Narrative destination | moved **wholesale** to a new article `wiki/arc-origin-narrative.md` (tier `foundational`), linked prominently from the board hero ("Read the full origin narrative →") | the spec's own recommendation; the board summarizes, the article tells; nothing is deleted |
| Icon approach | **no icon assets at all** — typographic hooks (the provenance-safe `6` / `1` / qualitative glyphs) + per-pillar wall-color accents | the strictest air-gap answer; zero new binary assets; nothing for the secret gate or licensing to review |
| Centerpiece medium | **CSS grid**, server-emitted static HTML | the spec's recommendation; inherits both theme palettes for free; no viewBox math; no JS |

## 2. Requirements

- **R1** — the home page renders the locked content spine (hero → centerpiece → 4 pillar-nav tiles → inheritance strip → Cult-Test footer), replacing the bare essay.
- **R2** — board content is **authored in `index.md` frontmatter**, not hardcoded in Python; the long narrative moves wholesale to `wiki/arc-origin-narrative.md`.
- **R3** — fail-legible: no unqualified contested hero number (the "14 invariants" ban is a named regression test); every pillar links to its corpus anchor; the Cult-Test footer is mandatory.
- **R4** — air-gap: no external fonts/icons/CDN; both light and dark themes; **no JavaScript** for the board.
- **R5** — accessibility: visually-hidden one-sentence board summary; centerpiece carries `role="img"` + `aria-label`; tiles are real links with discernible text.
- **R6** — everything outside the home page body (top bar, sidebar, freshness banner, search, theme toggle, all article pages) is byte-for-byte unaffected in behavior.

## 3. Data schema (flat, matching the existing `fm_val`/`fm_list` parser)

`index.md` frontmatter gains flat keys — no nested YAML (the repo's parser is
deliberately simple):

```yaml
board_eyebrow: "..."                # mono eyebrow line
board_hero: "..."                   # serif hero claim (one sentence)
board_subtitle: "..."               # secondary-color subtitle
board_narrative_link: arc-origin-narrative
board_pillars:                      # exactly 4; pipe-delimited fields:
  - "Accountability|<objective>|6|accountable-ai-architecture|purple"
  - "Provenance|<objective>||primitive-basis|teal"
  - "Governed autonomy|<objective>||hive-governance|amber"
  - "One civilization|<objective>|1|the-civilization|coral"
board_inheritance:                  # ordered strip items: "label|slug"
  - "Searles primitives|primitive-basis"
  - "Three irreducibles|three-irreducibles"
  - "Three evaluative axes|three-evaluative-axes"
board_method: "intent → order → bounded execution → evidence → gate → certified-or-rejected"
board_guardrail: "...|the-cult-test"   # footer text | anchor slug
```

**Fail-closed rendering rule:** if any board key is missing, malformed
(wrong field count, unknown wall color), or a linked slug does not exist in
`wiki/`, the build **fails with an explicit error** — it never silently
renders a partial board or falls back to the essay. (A build error is
visible; a half-board that looks finished is not.)

## 4. Render composition (in `build_site.py`)

- `page(..., is_home=True)` branch composes: skip-summary (visually hidden) → hero block → centerpiece (CSS grid: outer ring labelled *human · top authority*; four wall bars top/right/bottom/left in the pillar colors with vertical side text; core = two-row method pipeline with a visually distinct gate and the single success-colored *certified* node) → 2×2 pillar tile grid (each tile an `<a href="<slug>.html">`) → inheritance strip (arrowed, muted) → Cult-Test footer card.
- New CSS lives in `compile/assets/style.css` under a `.board-` prefix using the existing theme custom properties; wall colors defined as light-fill/dark-text ramps that read in both themes.
- `wiki/arc-origin-narrative.md` gets the current `index.md` narrative verbatim (plus standard article frontmatter); `index.md` body shrinks to a short connective paragraph (the board is the page).

## 5. Acceptance criteria & named tests (one-to-one)

| # | Criterion | Named test |
|---|---|---|
| AC1 | home page contains hero, centerpiece (`role="img"`), 4 pillar tiles as resolving links, inheritance strip, Cult-Test footer | `test_home_board_renders_all_sections` |
| AC2 | every board link target exists in `wiki/` and renders as a live (not red) link | `test_home_board_links_resolve` |
| AC3 | fail-legible regression: home page emits **no** unqualified "14 invariants" hero token | `test_home_board_no_contested_hero_number` |
| AC4 | missing/malformed board frontmatter or a dangling slug ⇒ build **fails loudly** (no partial board, no essay fallback) | `test_home_board_fails_closed_on_bad_frontmatter` |
| AC5 | no external asset references (no `http(s)://` in emitted home-page asset/font/icon URLs beyond existing site-relative assets); no `<script>` introduced by the board | `test_home_board_airgap_and_no_js` |
| AC6 | the narrative article exists, carries the moved essay, and the board links to it | `test_narrative_article_moved_and_linked` |
| AC7 | non-home pages and the page chrome are unaffected (existing nav/security/dist tests stay green) | existing suites: `test_build_site_nav.py`, `test_build_site_security.py`, `test_build_site_dist.py` |
| AC8 | board renders correct structure in **both** themes (theme-dependent styles resolve via CSS custom properties only — no theme-specific HTML) | `test_home_board_theme_neutral_markup` |

Gate ("satisfied only when"): AC1–AC8 all pass with committed test evidence
**and** `npm run verify`'s CI-equivalent subset is green **and** the built
`dist/index.html` visually carries the board (checked in the arc's IAR).
Any unproven criterion ⇒ not satisfied.

## 6. Authorization packet

- **Bounded scope:** `compile/build_site.py` (home branch + board renderer), `compile/assets/style.css` (`.board-` rules), `index.md` (frontmatter + shrunken body), new `wiki/arc-origin-narrative.md`, new/extended tests in `compile/test_build_site_*.py` — **transpara-ai/wiki only**.
- **Authority:** operator directive 2026-07-02 (marker `wiki-refactor-overnight-GO`) — standing AuthorityDecision for this arc, including merge-when-all-gates-green and deploy to the established loopback service.
- **Forbidden:** arc data/metrics (Item 2b), live widgets, external assets, JS on the board, settings/branch-protection changes, any other repo.
- **Residual risks:** (a) aesthetic judgment is being exercised autonomously — the owner reviews the live board after the fact and anything is reversible by editing frontmatter/CSS; (b) the narrative article's tier/nav placement is a taxonomy guess (`foundational`) — one-line frontmatter fix if wrong; (c) the board's copy is derived from corpus anchors but the *composition* is new writing — flagged for owner read-through.

## Appendix — IADA (self-directed, v0.2.0)

| # | Finding | Disposition |
|---|---|---|
| I1 | Board content in frontmatter could silently half-render if a key is missing → fail-open presentation | **FIXED in design** — §3 fail-closed rendering rule + AC4 named test |
| I2 | Wall colors named in frontmatter could drift from CSS → unknown color = unstyled wall | **FIXED** — unknown wall color ⇒ build error (allowlist of 4 named ramps), covered by AC4 |
| I3 | Moving the narrative could orphan inbound links to `index.html` anchors | **ACCEPTED** — the essay had no stable heading anchors in nav use; site search reindexes on build; narrative article is linked from the hero |
| I4 | The centerpiece as CSS grid may degrade on very narrow viewports | **ACCEPTED** — single-column stacking at the existing mobile breakpoint; the walls become stacked labelled bands (stated in §4 CSS) |
