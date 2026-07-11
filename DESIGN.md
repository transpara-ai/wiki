---
name: Transpara-AI Civilization Wiki
description: Dense, provenance-first encyclopedia surface in Transpara's corporate design language
colors:
  green-bright: "#99cc00"
  green-corp: "#669900"
  green-deep: "#578200"
  green-ink: "#476b00"
  visited-steel: "#6699cc"
  visited-steel-ink: "#3a628f"
  signal-orange: "#ff6600"
  night-bg: "#161815"
  night-panel: "#1d201c"
  night-panel-2: "#272b26"
  night-border: "#3b4038"
  night-border-strong: "#4b5147"
  night-text: "#e7e9e5"
  night-muted: "#a9b1a8"
  night-faint: "#7f887e"
  day-bg: "#fcfcfc"
  day-panel: "#f5f6f4"
  day-panel-2: "#eaece7"
  day-border: "#c8ccc5"
  day-border-strong: "#a3aa9f"
  day-text: "#1c1c1c"
  day-muted: "#545a52"
  day-faint: "#6f776d"
  tier-foundational: "#c4b0f0"
  tier-architecture: "#8fc6f5"
  tier-arc: "#e6c07a"
  tier-investigation: "#80d4ba"
typography:
  display:
    fontFamily: "Raleway, system-ui, sans-serif"
    fontSize: "30px"
    fontWeight: 600
    lineHeight: 1.25
  headline:
    fontFamily: "Raleway, system-ui, sans-serif"
    fontSize: "23px"
    fontWeight: 600
    lineHeight: 1.3
  title:
    fontFamily: "Raleway, system-ui, sans-serif"
    fontSize: "19px"
    fontWeight: 600
    lineHeight: 1.3
  body:
    fontFamily: "'Open Sans', system-ui, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: "ui-monospace, 'SFMono-Regular', Menlo, Consolas, monospace"
    fontSize: "11px"
    fontWeight: 700
    lineHeight: 1.25
    letterSpacing: "0.04em"
  quote:
    fontFamily: "Georgia, 'Times New Roman', serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.55
rounded:
  xs: "2px"
  sm: "3px"
  md: "6px"
  pill: "999px"
spacing:
  xs: "6px"
  sm: "10px"
  md: "14px"
  lg: "18px"
  xl: "32px"
components:
  button-primary:
    backgroundColor: "{colors.green-bright}"
    textColor: "#1a1c10"
    rounded: "{rounded.pill}"
    padding: "7px 18px"
  button-primary-hover:
    backgroundColor: "#a9da21"
    textColor: "#1a1c10"
    rounded: "{rounded.pill}"
  button-chrome:
    backgroundColor: "{colors.night-bg}"
    textColor: "{colors.night-muted}"
    typography: "{typography.label}"
    rounded: "{rounded.xs}"
    padding: "3px 9px"
  input-field:
    backgroundColor: "{colors.night-bg}"
    textColor: "{colors.night-text}"
    rounded: "{rounded.xs}"
    padding: "7px 9px"
  chip-tier:
    backgroundColor: "{colors.night-panel-2}"
    textColor: "{colors.night-muted}"
    typography: "{typography.label}"
    rounded: "{rounded.xs}"
    padding: "1px 7px"
---

# Design System: Transpara-AI Civilization Wiki

## 1. Overview

**Creative North Star: "The Factory Reading Room"**

A reading room attached to a working factory: shelves of compiled, cross-linked knowledge in front, the hum of the ingest-compile-publish machinery audible through the wall. The wiki keeps its encyclopedia *grammar* — dense resizable sidebar, floating infoboxes, citation footers, tier badges, 65–75ch article measure — because that grammar is what makes a records surface trustworthy and navigable. What changes is the *skin*: the bootstrap Wikipedia look (borrowed link-blues, Georgia brand serif) retires in favor of Transpara's corporate language — near-neutral blacks and whites, the lime-olive green as the single working color, Raleway headings over Open Sans body. Adopted 2026-07-10; the codebase is mid-migration from the Wikipedia skin toward this spec, and this file is normative for all new and reworked surfaces.

The system explicitly rejects its two anti-references from PRODUCT.md: the **AI-mystique aesthetic** (no neon glow, no pure-black terminal cosplay, no cyber gradients — a real risk with lime-on-dark, so green is never glowed, never animated for flavor) and the **corporate intranet** (no gray-on-gray neglect; every state is designed, the freshness signals are first-class UI). It also rejects the corporate *marketing* grammar — heroes, pill-CTA spacing, airy sections — which serves transpara.com but would fight a dense working tool.

The two themes are equals: the CSS is authored dark-first (`:root` carries the night ramp; `[data-theme="light"]` overrides), while the shipped default for a first-time visitor is light, with dark one toggle away and persisted. Both themes hold WCAG 2.1 AA on the reader surface. Motion is product-register: 150–250ms state transitions only, no choreography, `prefers-reduced-motion` honored everywhere.

**Key Characteristics:**
- Encyclopedia density and navigation grammar, Transpara corporate skin
- One working color (the corp green) carrying links, primary actions, and "current/healthy" signals
- Dark-first dual themes, AA in both
- Flat at rest; elevation only for transient overlays
- Operational chrome (freshness, meta, badges) speaks monospace; sources speak serif; the wiki speaks Open Sans
- Fully self-contained assets — air-gap friendly, zero external requests

## 2. Colors

Black-and-white foundation, one green working voice, steel blue for the visited past, one orange for the single loudest thing on a page.

### Primary
- **Transpara Bright Green** (#99cc00): the dark-theme working color — article links, wikilinks, primary-action buttons, focus rings, and the "fresh/current" state. 9.3:1 on `night-bg`. This is the corp dark-mode brand token adopted verbatim.
- **Transpara Corp Green** (#669900): the light-theme brand green for large text (≥19px), button fills at large sizes, icons, and non-text accents. At 3.4:1 on white it is **forbidden for body-size text** — that's what Green Ink is for.
- **Green Deep** (#578200): light-theme primary-button fill (white text passes 4.6:1). Corp ramp token `primary-darker`.
- **Green Ink** (#476b00): light-theme link and small-text green, 6.2:1 on white. Corp ramp token `primary-darkest`.

### Secondary
- **Visited Steel** (#6699cc) / **Visited Steel Ink** (#3a628f): visited-link color, dark / light respectively (5.9:1 / 6.3:1). Deliberate inversion of the Wikipedia relationship: blue is the *visited past*, green is the *Transpara present*. Sourced from the corp highlight palette, not invented.

### Tertiary
- **Signal Orange** (#ff6600): the corp highlight, rationed hard — at most one orange element per view, for the single most important call-out (a blocking deploy banner, a critical notice). Large text and borders only in light theme (3.5:1).
- **Tier palette** — functional data vocabulary on badges and markers, not decoration: Foundational (#c4b0f0 purple), Architecture/Institutional (#8fc6f5 blue), Arc (#e6c07a gold), Investigation (#80d4ba teal). Light-theme variants darken to hold contrast (see sidecar). The arc progress view keeps its own scoped `--arc-*` palette for the same reason: charts need more hues than chrome does.

### Neutral
- **Night ramp** (bg #161815 · panel #1d201c · panel-2 #272b26 · borders #3b4038 / #4b5147 · text #e7e9e5 · muted #a9b1a8 · faint #7f887e): the default theme. Near-neutral with a whisper of green tint (the brand's own hue) replacing the old blue-tinted GitHub-dark ramp. Never pure black — pure black + lime is the AI-terminal cliché this system bans.
- **Day ramp** (bg #fcfcfc · panel #f5f6f4 · panel-2 #eaece7 · borders #c8ccc5 / #a3aa9f · ink #1c1c1c · muted #545a52 · faint #6f776d): the corp site's white-and-ink foundation with the same faint green cast in panels, replacing Wikipedia's cool grays.
- **Parchment quote material** (dark: #e6d3a6 text on #231d10, border #a07f3a · light: #5c4a22 on #fdf7ea, border #c8923a): reserved exclusively for quoted source material. Kept from the current system — it is one of the wiki's own inventions worth protecting.
- **Semantic states**: OK/current unifies with the brand green family (green literally means "alive and current" here); warn stays amber (#e3b341 dark / #8a6d1a light); error/destructive stays red (#ff7b72 dark / #d33 light, with #b32424-family light-code accents). TBD wikilinks stay red — a red link meaning "article missing" is encyclopedia vocabulary worth keeping.

### Named Rules
**The Green-Means-Current Rule.** In chrome, green is a *statement of health* — fresh, synced, passing, live. Never use the brand green decoratively on a stale, failing, or unknown state; a green ornament on a broken thing is a lie the whole design is built to avoid.

**The AA-Both-Themes Rule.** Every text/background pair passes 4.5:1 in both themes at body size. Brand-exact #669900 and #ff6600 are large-text/non-text-only in light theme. No exceptions for "brand accuracy" — the ramp tokens exist precisely so brand and AA never conflict.

**The One-Orange Rule.** Signal Orange appears at most once per view. Two orange things means neither is the most important thing.

## 3. Typography

**Display Font:** Raleway (with system-ui fallback)
**Body Font:** Open Sans (with system-ui fallback)
**Label/Mono Font:** ui-monospace stack (SFMono-Regular, Menlo, Consolas)
**Quote Font:** Georgia (system serif; quoted source material only)

**Character:** Raleway's geometric-elegant headings over Open Sans's neutral humanist body is the corporate pairing, tuned down to working-tool sizes. The monospace layer keeps the operational chrome honest and machine-flavored; Georgia survives from the old skin in exactly one role — the voice of the sources.

Both webfonts ship as **vendored woff2 files in the repo** (subset to Latin), never from Google Fonts or any CDN — the wiki must render fully on an air-gapped loopback host. Until the files are vendored, the system-ui fallbacks must look acceptable; test both.

### Hierarchy
- **Display** (Raleway 600, 30px, 1.25): page titles. Keeps the current 30px scale — encyclopedia pages, not hero banners. Bottom-ruled with `night-border-strong`/`day-border-strong`.
- **Headline** (Raleway 600, 23px, 1.3): article h2, bottom-ruled with the faint border.
- **Title** (Raleway 600, 19px, 1.3): article h3; infobox and navbox titles at 15px.
- **Body** (Open Sans 400, 15px, 1.6): article prose, capped at the current ~60em content measure (≈65–75ch). Links underline on hover only.
- **Label** (mono 700, 11px, 0.04em tracking, uppercase): sidebar group headers, tier badges, freshness chip, table-of-metadata labels, top-link chips. This is the wiki's operational voice — keep it monospace, keep it small, keep it quiet (muted/faint colors, never green unless stating health).
- **Quote** (Georgia 400, 15px, 1.55): blockquoted source material on parchment tokens.

### Named Rules
**The Sources-Speak-In-Serif Rule.** Georgia appears *only* inside quoted source material (blockquotes, cited passages). Everything the wiki itself says is sans or mono. A reader should be able to tell at a glance whether the corpus or the compiler is talking.

**The No-Shouting Rule.** Nothing on a reader page exceeds 30px. Emphasis comes from weight, rule lines, and space — never from scale jumps, gradient text, or letterspaced all-caps headlines.

## 4. Elevation

Flat at rest, with tonal layering doing the depth work: `bg → panel → panel-2` is the entire resting z-story in both themes, separated by 1px borders. Box shadows exist for exactly one purpose — transient overlays that float above the document flow.

### Shadow Vocabulary
- **Overlay** (`box-shadow: 0 10px 28px rgba(0,0,0,.38)` dark / `0 10px 28px rgba(0,0,0,.18)` light): the freshness popover, search-results dropdown, and any future menu/tooltip. Nothing else casts a shadow.

### Named Rules
**The Flat-At-Rest Rule.** If it doesn't float over the page, it doesn't cast a shadow. Panels, infoboxes, cards, and banners are flat surfaces with borders — a shadowed card on a records page is decoration pretending to be information.

## 5. Components

The component vocabulary is already coherent; the retheme re-skins it. States for every interactive component: default, hover, focus-visible (2px green outline, offset 2px), active, disabled — no half-finished state sets.

### Buttons
- **Primary (pill):** the corp signature shape, reserved for the page's main action (Ingest, Rebuild, Search submit). Fully rounded (999px); dark: Bright Green fill #99cc00 with near-black text #1a1c10, hover #a9da21; light: Green Deep fill #578200 with white text, hover #669900. Padding 7px 18px, Open Sans 600 at 13–14px.
- **Chrome (chip):** small utility buttons (theme toggle, sidebar tools, top links) stay as they are — mono 11–12px, 2px radius, bg-colored fill, 1px border, hover raises border to green and text to full ink. These are deliberately un-pill: chrome is not a call to action.
- **Secondary / outline:** 1px `border-strong` border, transparent fill, body text color; hover border goes green. 3px radius.
- **Destructive:** red text + red border, never a red fill at rest; fill goes red only on the final confirm step.
- **Disabled:** 50% opacity, no hover response, `cursor: not-allowed`.

### Chips
- **Tier badges:** mono label type on `panel-2`, 1px border, 2px radius, tier color as *text* color — colored text on neutral chip, not colored fills (fills at 11px destroy legibility).
- **Freshness chip:** the topbar's health statement. OK = green family (text #99cc00 dark / #476b00 light on a green-tinted panel), WARN = amber family, popover on click with the per-source sync list. This is the single most identity-defining element in the chrome: it is where Green-Means-Current lives.

### Cards / Containers
- **Corner style:** 2px radius on document furniture (infobox, TOC, source panels, navbox), 6px on the arc progress cards and popovers. Nothing between 6px and pill exists — no 12px "modern SaaS" radii.
- **Background:** `panel`, titles on `panel-2`, 1px full borders.
- **Callouts (state banners, contribution boxes, destructive-mode cards):** full 1px border in the state color plus a state-tinted background (~90% transparent mix) and a mono label header. **No left-stripe accents** — the current 4px `border-left` treatments migrate to this full-border style during the retheme.
- **Internal padding:** 10–14px; density is respect.

### Inputs / Fields
- **Style:** 1px `border-strong`, page-bg fill (inputs read as holes in the panel), 2px radius, 7px 9px padding, 14px Open Sans.
- **Focus:** border goes green, plus a 2px green outline at 36% opacity (`color-mix` with transparency) — visible in both themes without glow.
- **Placeholder:** must hold 4.5:1 like any body text (use `muted`, not `faint`).
- **Error:** red border + red mono helper line under the field; never color alone — say what's wrong.

### Navigation
- **Topbar:** brand mark in Raleway 600 (optionally preceded by the three corp logo dots as inline SVG — the only decorative mark in the system), search, mono top-link chips, freshness chip, theme toggle. Solid `panel` background, 1px bottom border.
- **Sidebar:** resizable 22rem default, collapsible `details` groups with uppercase mono headers and article counts, current page highlighted with `panel-2` fill + 600 weight. Link color = working green; hover fills `panel`, never underlines. Collapses to top-stacked on ≤720px.
- **In-article:** wikilinks in working green; visited in steel; TBD links red with `cursor: help`; pending links dashed-underlined muted. All four states must remain distinguishable in both themes.

### The Freshness & Provenance Layer (signature)
What makes this wiki *this wiki*: the freshness banner/chip recomputed on every build, per-article "Sources & provenance" footers, source-viewer pages, tier badges, and the citation click-through contract (declared source IDs render as one-click links). Design work on any page must keep this layer visible, quiet, and mono-voiced — it is the product's honesty made visible, and it must never be minimized to make a page "cleaner."

## 6. Do's and Don'ts

### Do:
- **Do** keep dark as the default theme and hold every body-text pair to 4.5:1 in both themes (the AA-Both-Themes Rule; PRODUCT.md commits to "WCAG 2.1 AA on the reader surface, held in both themes").
- **Do** use #99cc00 (dark) / #476b00 (light) for links and #578200 for light primary buttons — the corp *ramp* is the palette, not just the flagship hex.
- **Do** keep the encyclopedia grammar: dense sidebar, floating infobox, TOC panel, citation footers, 15px/1.6 body at ~65–75ch.
- **Do** vendor Raleway and Open Sans as woff2 in-repo; the site must render identically with zero network access.
- **Do** honor `prefers-reduced-motion` on every transition; keep transitions 150–250ms, state-conveying only.
- **Do** keep the freshness/provenance layer visible on every reader page — it is the trust surface ("linking to the wiki must feel safe" — PRODUCT.md).

### Don't:
- **Don't** drift into the **AI-mystique aesthetic** (PRODUCT.md anti-reference): no neon glow on the green, no pure-black backgrounds, no scanlines, no cyber gradients, no sci-fi terminal cosplay.
- **Don't** let it rot into the **corporate intranet** (PRODUCT.md anti-reference): no gray-on-gray text, no undesigned states, no "dense but joyless" neglect — density with hierarchy, not density instead of it.
- **Don't** import transpara.com's *marketing* grammar: no heroes, no card-grid feature sections, no airy section spacing, no circles background wallpaper.
- **Don't** use `border-left`/`border-right` thicker than 1px as a colored accent — callouts use full borders + tinted backgrounds (the current 4px left-stripes are migration debt, not precedent).
- **Don't** use gradient text, glassmorphism, hero metrics, or any radius between 6px and pill.
- **Don't** put #669900 or #ff6600 on body-size text in light theme (3.4:1 / 3.5:1 — large text and accents only).
- **Don't** load anything — fonts, scripts, styles, images — from an external host. If it isn't in the repo, it isn't in the design.
- **Don't** use green on a component that isn't healthy/current, and don't show two orange elements in one view (Green-Means-Current; One-Orange).
