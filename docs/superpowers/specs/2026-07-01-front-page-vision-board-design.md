# Front-Page Vision Board — Design Spec (Item 2a)

**Status:** draft v0.1 · **Date:** 2026-07-01 · **Owner:** Michael Saucier · **Authority:** planning (proposal, pending review) · **Repo/branch:** transpara-ai/wiki @ `feat/front-page-vision-board`

> **Process provenance.** Brainstormed 2026-07-01 against the live front page (`index.md`, rendered bare by `compile/build_site.py` `page(..., is_home=True)`) and the corpus's own canonical framings. Visual direction chosen interactively from three mockups; the **B-spine braid** (systems-schematic spine + editorial hero + provenance-safe poster hooks) and a **concentric membrane centerpiece** were selected. Item **2b (the arc-metrics re-think)** is a separate spec.

---

## 0. Purpose & scope

Replace the current front page — a 564-line prose essay rendered as bare `<article class="body">` — with a **graphics-first vision/thesis board** that summarizes the fundamental goals and objectives of the Transpara-AI Civilization arc as a *designed argument a reader absorbs and remembers.*

**Reader & job (owner, 2026-07-01):** a **vision/thesis board** — optimized to make the fundamental objectives land as a persuasive, memorable argument. Light on live status; heavy on "why it matters."

**North star (owner, 2026-07-01):** instructive, educational, prescriptive, easy for a **human** to digest.

**Doctrine constraint:** the board is itself subject to the wiki's **fail-legible** rule. No unsourced or contested claim may appear as an unqualified hero element (see §4).

### 0.1 In scope
The home page (`is_home`) only: content spine, visual composition, the concentric membrane centerpiece, pillar-as-navigation, and the render path in `build_site.py`.

### 0.2 Out of scope
- **Item 2b** — the `civilizationArc` metrics re-think (separate spec; the front page is deliberately independent of the arc data model).
- Live status / dashboards (owner chose "light on live status"). The existing freshness banner in the top bar is retained unchanged; no new live widgets.
- Item 1 (ingestion) and Item 3 (advisory memo).

---

## 1. The locked content spine (the argument)

Validated by the owner 2026-07-01. Every element is anchored in an existing corpus article — **derived, not invented** (the wiki's founding principle).

**◆ Hero claim** (`index.md`): *Agents that build real systems must live **inside** the graph of cause, evidence, authority, review, and consequence — never above it as unverifiable oracles.* Subtitle: *a field experiment in whether a company can grow an adjacent agent civilization without surrendering provenance, consent, review, or responsibility.*

**◆ Four objective-pillars** (each already a corpus article; each an infographic **and** a navigation entry):

| Pillar | Objective (one line) | Provenance-safe hook | Corpus anchor |
|---|---|---|---|
| **Accountability** | six questions every material action answers: *who asked · who acted · under what authority · with what evidence · against which criteria · with what residual risk* | **6** | `accountable-ai-architecture` |
| **Provenance** | nothing unsourced; asserted-vs-proven always labelled; gaps `TBD`; conflicts stated | *(qualitative — no number)* | `primitive-basis` / DESIGN doctrine |
| **Governed autonomy** | agents work only inside an auditable membrane; human holds top authority; gates fail-closed | *(qualitative)* | `hive-governance` / `authority-layer` |
| **One civilization** | the discipline that makes industrial reality visible, turned inward on the software factory | **1** | `the-civilization` |

**◆ Inheritance strip** — *inherited, not owned; motive & vocabulary only, never proven metaphysics*: Searles primitives → `three-irreducibles` (the holes it admits) → `three-evaluative-axes` (*useful · right · beautiful*).

**◆ Method strip** — `intent → order → bounded execution → evidence → gate → certified-or-rejected`.

**◆ Cult-Test guardrail** (footer, `the-cult-test`): *if a framework explains everything, distrust it; if it cannot be wrong, it is not science.* The self-aware footer that keeps a vision board from becoming propaganda that fails its own test.

---

## 2. Visual composition (B-spine braid)

Top-to-bottom, one column, ~660px content width (matches the site's article measure):

1. **Hero** — serif claim (the wiki's editorial voice), mono eyebrow, secondary-color subtitle.
2. **The concentric membrane centerpiece** (§3) — the thesis *drawn*.
3. **Four pillar-nav tiles** — 2×2 grid; icon + name + objective + provenance-safe hook + "read the article →". Each tile is an `<a>` to its anchor article (§5). The board **is** the front door.
4. **Inheritance strip** — a thin rule-bounded horizontal band, muted, with arrowed progression.
5. **Cult-Test guardrail** — a distinct footer card.

---

## 3. The concentric membrane centerpiece (the money graphic)

The single most important element. Read **outward-in**; it renders the thesis as geometry, not caption:

- **Outer ring — human · top authority.** A bordered container labelled top-left; "authority flows inward" (↓). Everything is *inside* the human's authority. (Anchor: `the-civilization` — human is the top authority tier.)
- **Four walls — the objectives enclose the work on all sides.** A frame of four labelled bars around the core:
  - **top** = accountability (purple)
  - **right** = provenance (teal)
  - **bottom** = governed autonomy (amber)
  - **left** = one civilization (coral)
  - Side walls use vertical text; the four bars meet at the corners to form a closed frame.
- **Core — agents at work.** Caption *"every action leaves evidence"*; the method pipeline runs here in two rows: `intent → order → bounded execution` / `evidence → [gate] → certified`. The **gate** is visually distinct (lock); **certified** is the only success-colored node.
- **The invariant made visual:** *work leaves the membrane only as certified-or-rejected.* If reality ever let work exit without a gate, the picture would visibly break — a **falsifiable diagram** (which is itself in the spirit of the Cult Test).

**Static, not live.** Per scope, the centerpiece carries no live data — it is pre-rendered at build time. Unlike the arc's heavy JS asset stack, this is plain server-emitted HTML/CSS (a CSS grid) or a single inline SVG. **No JavaScript required.**

---

## 4. Fail-legible rule for the board (non-negotiable)

The vision board advertises provenance; it must therefore *practice* it.

- **Allowlist for hero numbers.** A number may appear as an unqualified bold hero element **only if** it is uncontested in the corpus. `6` (accountability questions) ✓ and `1` (one civilization/business) ✓ pass. **`14 invariants` is FORBIDDEN as an unqualified hero number** — `the-civilization` records a live 14-vs-10 conflict; putting a bold "14" on the front page would make the board violate the doctrine it sells. Contested facts may appear only *with* their caveat, never as a poster hook.
- **Every pillar links to its source article** (§5) — the claim is one click from its evidence.
- **The Cult-Test footer is mandatory**, not decorative. Removing it makes the page contradict its own corpus.

---

## 5. Pillar → article navigation map

Each pillar tile links to its anchor article. Proposed targets (to confirm — see §9):

| Pillar | Proposed link target |
|---|---|
| Accountability | `accountable-ai-architecture.html` |
| Provenance | `primitive-basis.html` *(or a dedicated fail-legible/provenance article if one is promoted)* |
| Governed autonomy | `hive-governance.html` *(or `authority-layer.html`)* |
| One civilization | `the-civilization.html` |

Inheritance-strip terms link to `primitive-basis`, `three-irreducibles`, `three-evaluative-axes`; the guardrail links to `the-cult-test`.

---

## 6. Implementation notes (against the real codebase)

- **Render path:** extend `compile/build_site.py` `page(..., is_home=True)`. Today the home branch emits `'<article class="body">%s</article>' % body_html`. The redesign composes the vision board there instead (hero + centerpiece + tiles + strips + footer), while the existing top bar, sidebar, freshness banner, search, and theme toggle are unchanged.
- **Content stays data-driven, not hardcoded.** The hero text, the four pillars (name · objective · hook · link · wall-color), the inheritance/method strips, and the guardrail should be authored in `index.md` frontmatter (or a small adjacent data block) and rendered by `build_site.py` — consistent with the wiki's "compiled from sources" ethos and keeping the prose editable without touching Python. The long historical narrative currently in `index.md` moves to a linked article (e.g. an "origin / arc narrative" page) so the front page is a board, not an essay.
- **Air-gap — no external assets.** The mockups used claude.ai's design system (Anthropic Sans + Tabler webfont via CDN). **Production must not.** Use the wiki's own `compile/assets/style.css` tokens and its existing light/dark theming; icons must be **local** (inline SVG or an already-bundled set), never a CDN webfont. No `fonts.googleapis.com`, no `cdnjs`. This is the air-gap default.
- **Theme:** must render correctly in both the site's light and dark themes (the four wall-colors use light fills + dark same-ramp text, which read in both modes).
- **Accessibility:** lead with a visually-hidden one-sentence summary of the board; the centerpiece gets `role="img"` + `<title>`/`<desc>` (SVG) or an `aria-label` (grid); pillar tiles are real links with discernible text.
- **Tests:** extend `compile/test_build_site_nav.py` / `test_build_site_security.py` to assert the home page renders the pillar links (resolving, not red), contains the guardrail, and — a fail-legible regression guard — **does not** emit a bare unqualified "14 invariants" hero token.

---

## 7. Provenance ledger

| Element | Corpus anchor |
|---|---|
| Hero claim ("inside, not above") | `index.md` (the epiphany) |
| Six accountability questions | `index.md`; `accountable-ai-architecture` |
| Provenance / fail-legible | `primitive-basis`; `DESIGN.md` principles |
| Governed autonomy / membrane / top authority | `the-civilization`; `hive-governance`; `authority-layer` |
| One civilization, one business | `the-civilization` |
| Inheritance (motive/vocabulary only) | `primitive-basis`; `three-irreducibles`; `three-evaluative-axes` |
| Method pipeline | `factory-order`; `dark-factory` |
| Cult-Test guardrail | `the-cult-test` |

---

## 8. What this spec does NOT do

- No change to the arc, its data, or its metrics (Item 2b).
- No live/dashboard elements on the home page.
- No hardcoded prose in Python (content stays authored in `index.md`).
- No external fonts/icons/CDN (air-gap).

---

## 9. Open questions (for owner review)

1. **Pillar link targets** — confirm the four anchor slugs in §5 (esp. Provenance and Governed autonomy, which have more than one plausible target).
2. **Where does the long narrative go?** The current 564-line `index.md` essay is valuable — move it wholesale to a linked "arc origin / narrative" article, or distill parts of it into the board's connective text? (Recommend: move wholesale, link prominently; the board summarizes, the article tells.)
3. **Icon set** — which locally-bundled icon approach (inline SVG sprite vs. an existing bundled set) fits the air-gap constraint best in this repo?
4. **Centerpiece medium** — CSS grid (simplest, fully themeable) vs. a single inline SVG (more precise geometry). (Recommend: CSS grid first; it inherits theme tokens for free and needs no viewBox math.)
