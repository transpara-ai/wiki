---
doc_id: TAI-WIKI-FRONT-PAGE-BOARD
title: Front-Page Vision Board — TLC Design Packet (Item 2a)
doc_type: design
version: 0.3.0
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
- **R6** — page chrome and article rendering behavior are unchanged **except the intended additive derivations of one new corpus article** (`arc-origin-narrative` appears in the sidebar tier group, the search index, and the article count — exactly as any new article would; CFADA-r1 B1). No other chrome/behavior change.

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

**Delimiter contract (CFADA-r1 M3):** the pipe `|` is reserved as the field
separator and is **banned inside field copy** — a literal `|` in any board
field value ⇒ named build error (fail-closed; the authoring fix is rewording,
not escaping).

**Fail-closed rendering rule:** if any board key is missing, malformed
(wrong field count, unknown wall color), or a linked slug does not exist in
`wiki/`, the build **fails with an explicit error** — it never silently
renders a partial board or falls back to the essay. (A build error is
visible; a half-board that looks finished is not.)

## 4. Render composition (in `build_site.py`)

- **Data path (CFADA-r1 B2):** today `build()` calls `page("index", ..., {}, "", body_html, ..., is_home=True)` passing an **empty** frontmatter string — the board cannot be rendered from inside `page()`. The build therefore composes the board **before** the `page()` call: `build()` keeps the real `fm` from `split_fm(INDEX.read_text())`, calls a new `build_board(fm)` that **validates fail-closed** (§3) and returns board HTML, and passes `board_html + connective_body_html` as the home body. `page(is_home=True)` itself stays a dumb frame.
- The board composes: skip-summary (visually hidden) → hero block → centerpiece (CSS grid: outer ring labelled *human · top authority*; four wall bars top/right/bottom/left in the pillar colors with vertical side text; core = two-row method pipeline with a visually distinct gate and the single success-colored *certified* node) → 2×2 pillar tile grid (each tile an `<a href="<slug>.html">`) → inheritance strip (arrowed, muted) → Cult-Test footer card.
- New CSS lives in `compile/assets/style.css` under a `.board-` prefix using the existing theme custom properties; wall colors defined as light-fill/dark-text ramps that read in both themes.
- `wiki/arc-origin-narrative.md` gets the current `index.md` narrative verbatim (plus standard article frontmatter); `index.md` body shrinks to a short connective paragraph (the board is the page).

## 5. Acceptance criteria & named tests (one-to-one)

| # | Criterion | Named test |
|---|---|---|
| AC1 | home page contains hero, centerpiece (`role="img"`), 4 pillar tiles as resolving links, inheritance strip, Cult-Test footer | `test_home_board_renders_all_sections` |
| AC2 | every board link target exists in `wiki/` and renders as a live (not red) link | `test_home_board_links_resolve` |
| AC3 | fail-legible regression: home page emits **no** unqualified "14 invariants" hero token | `test_home_board_no_contested_hero_number` |
| AC4 | missing/malformed board frontmatter or a dangling slug ⇒ build **fails loudly** (no partial board, no essay fallback) | `test_home_board_fails_closed_on_bad_frontmatter` |
| AC5 | air-gap relative to a **pinned baseline**: the board introduces **no additional** `<script>` beyond the pre-existing chrome set, no `url(http…)` in `.board-` CSS rules, and no external font/icon references anywhere on the home page (CFADA-r1 M4) | `test_home_board_airgap_and_no_js` |
| AC6 | the narrative article exists, carries the moved essay, and the board links to it | `test_narrative_article_moved_and_linked` |
| AC7 | chrome/article behavior unchanged except the R6 additive derivations; existing python suites stay green; **the Playwright home specs (`tests/arc-nav.spec.js` et al.) are updated in-scope** — they currently assert the old essay text and would otherwise contradict the gate (CFADA-r1 B3) | existing suites + updated browser specs |
| AC8 | board renders correct structure in **both** themes (theme-dependent styles resolve via CSS custom properties only — no theme-specific HTML) | `test_home_board_theme_neutral_markup` |
| AC9 | board content is **frontmatter-driven, not hardcoded**: mutated board frontmatter values render verbatim; no Python fallback constants (CFADA-r1 M1) | `test_home_board_content_is_frontmatter_driven` |
| AC10 | accessibility as specified in R5: visually-hidden one-sentence summary present; centerpiece `aria-label`; all four tile links have accessible names (CFADA-r1 M2) | `test_home_board_accessibility` |

Gate ("satisfied only when"): AC1–AC10 all pass with committed test evidence
**and** the CI-equivalent verify subset (build/js/unit/py/dom — what the
required job runs) is green **and** the updated Playwright home specs pass
locally (browser suite is local-only evidence, exactly as CI treats it)
**and** the built `dist/index.html` visually carries the board (arc IAR).
Any unproven criterion ⇒ not satisfied.

## 6. Authorization packet

- **Bounded scope:** `compile/build_site.py` (home branch + board renderer), `compile/assets/style.css` (`.board-` rules), `index.md` (frontmatter + shrunken body), new `wiki/arc-origin-narrative.md`, new/extended tests in `compile/test_build_site_*.py`, and the **in-scope update of the Playwright home specs under `tests/`** whose assertions reference the replaced essay (CFADA-r1 B3) — **transpara-ai/wiki only**.
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

## Appendix — CFADA round 1 (Codex · cross-family) → repaired at v0.3.0

> Reviewed head `8ec4cb2` (v0.2.0). Verdict: **FAIL — 3 blockers, 4 majors**. All repaired.

| # | Finding | Disposition (v0.3.0) |
|---|---|---|
| B1 | narrative move mechanically contradicts "chrome unaffected" (sidebar/search/count derive from wiki/*.md) | R6/AC7 narrowed to "unchanged except the intended additive derivations of one new corpus article" |
| B2 | `build()` passes an empty fm string to `page()` — the named render path cannot see board data | data path respecified: `build_board(fm)` validates fail-closed BEFORE `page()`; `page()` stays a dumb frame |
| B3 | Playwright home specs assert the old essay text — the gate was unsatisfiable | browser specs added to scope + AC7; gate = CI-equivalent subset + updated browser specs as local evidence |
| M1 | frontmatter-driven claim untested | AC9 + `test_home_board_content_is_frontmatter_driven` |
| M2 | accessibility clauses uncovered | AC10 + `test_home_board_accessibility` |
| M3 | pipe delimiter ambiguous for literal pipes | delimiter contract: `|` banned in field copy, named build error |
| M4 | no-JS assertion unscoped vs existing chrome scripts | AC5 pinned-baseline formulation |
