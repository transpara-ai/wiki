---
doc_id: FO-WIKI-FRONTEND-UX
title: Front-end requirements completion — §7 ingest UX + honest-state styling (Factory Order)
doc_type: factory-order
version: 0.1.0
status: draft (pending channel-A intake confirmation — "is this your order?")
canonical: false
created: 2026-07-06
updated: 2026-07-06
owner: Michael Saucier
steward: Claude (Fable 5)
authority: planning
tlc_stage: factory-order
source_of_intent:
  - Michael, in-session 2026-07-06 (archived verbatim in §4) — "we must immediately return to fixing the front-end of the Wiki and making the requirements met"
  - docs/superpowers/specs/2026-07-01-per-ingestion-operations-design.md §7 (blob d21e2fef6606c0bd228b2198e29b3c9ba9ccb788, canonical on main) — the UX/legibility requirements v1 deferred
  - docs/superpowers/specs/2026-06-15-wiki-autodeploy-design.md (blob d05d5985dd8a48f80f106227de8fc734ce23ab17) — deploy-status visibility surface
  - docs/superpowers/specs/2026-07-03-per-ingestion-ops-packet.md §2.1 (blob 48e330a27d8449c5c8ac0e412dcf6f7d98c23dfc) — the explicit v1 deferral record ("ingest.html UI for the new operations — API-first; curl is the v1 surface")
intake_channel: A (owner-directed session 2026-07-06)
---

# Front-end requirements completion — Factory Order

> Stage-2 TLC document. States intent; grants and closes nothing. The
> requirements below are the verifiable reading of "fixing the front-end of
> the Wiki and making the requirements met", derived from a repo-wide
> spec-vs-implementation gap survey (2026-07-06, wiki main @ `ca23a85`).
> The same partially-built-spec pattern that left 2b's visual half unshipped
> left the per-ingestion spec's §7 UX half unshipped: PR #48 delivered the
> API; curl is still the only operator surface for Replace/Remove.

## 1. Requirements (each individually verifiable)

- **R1 — Operation selector (§7.1).** `ingest.html` gains an
  `Add · Replace · Remove` operation selector; Add is default; the two
  destructive modes are visually distinct, in the house style, both themes.
  *Today:* the page renders only the batch-Add form
  (`build_site.py` `ingest_page()`); Replace/Remove exist solely as API
  endpoints.
- **R2 — Mandatory consequence preview (§7.2).** Before any destructive
  action, the page shows exactly what will happen: for Replace — which
  source(s) are superseded and that a recompile follows; for Remove — the
  full list of inbound articles and the reconciliation frontier to closure.
  The human confirms the preview before the request fires; the server-side
  deny-by-default authorization artifact gate (shipped in #48) remains the
  enforcement — the UI never bypasses or weakens it, and preview must be
  strictly read-only.
- **R3 — Honest live state (§7.3).** The freshness banner can render a
  `recompiling` state and an `N edges pending reconciliation` count sourced
  from the edge-states truth file; tombstones and `dangling-pending` markers
  (already rendered server-side) remain visible. Unknown/unreadable state
  renders as an explicit degraded state, never as healthy.
- **R4 — Deploy-status styling.** `.deploy-foot` and `.deploy-blocked`
  (emitted by `build_site.py:1708` and the blocked-banner path; zero matching
  rules in `style.css` today) get house-style rules in both themes, so the
  autodeploy visibility surface reads as designed instead of unstyled text.
- **R5 — Pending-wikilink styling.** `.wl-pending`
  (`build_site.py:649`, zero matching rules in `style.css`) gets a visible
  house-style treatment in both themes — a pending-reconciliation link must
  be visually distinct from both live and absent links, not tooltip-only.

## 2. Non-goals and constraints

Non-goals: no Layer-2 per-edge reconciliation runs, no engine/LLM work, no
change to the authorization model or any server gate semantics, no
front-page/board changes, no arc-view changes, no full-corpus recompile.
Whether R2's preview data comes from a new read-only endpoint or client-side
derivation is a design-packet decision (stage 3), not settled here.

Constraints: air-gap (no external assets); both themes via the existing
custom-property palette; every new state indicator fail-closed (allowlist
states render live; everything else renders degraded/explicit); tests per
the house pattern (unit + dom-smoke + py builder guards + Playwright);
`transpara-ai/wiki` only; lifecycle issue→ready-PR; merge remains Michael's.

## 3. Verification of the gap (measured 2026-07-06, main @ ca23a85)

- Ops packet §2.1: "Out of v1 (explicit): `ingest.html` UI for the new
  operations (API-first; curl is the v1 surface)…" — the deferral record.
- `grep -c "deploy-foot\|deploy-blocked" compile/assets/style.css` → 0;
  `grep -c "wl-pending" compile/assets/style.css` → 0; both class names are
  emitted by the builder.
- The Arc 1 API is live on :8787 as of 2026-07-06 (service restarted,
  endpoints verified 403 deny-closed) — the UI has a real backend to talk to.

## 4. Source-of-intent archive (channel A)

Michael, in-session 2026-07-06, item (3) of a three-item instruction (items
1–2: fix the noted nits without involvement; close issue #46 — both
completed before this FO was crafted):

> 3) Once 1 and 2 are complete we must immediately return to fixing the
> front-end of the Wiki and making the requirements met.

## 5. Intake confirmation (stage-2 checkpoint, required for channel A)

**Is this your order?** Specifically:

- **Q1 — Scope:** is "the front-end requirements" = R1–R5 above (the §7 UX
  surface + the two unstyled honest-state indicators)? Anything to add —
  e.g. broader visual/aesthetic work, front-page, arc page — or to cut?
- **Q2 — Destructive-mode UX:** the server requires the pre-placed
  single-use authorization artifact for Replace/Remove. Should the UI
  (a) assume the operator pre-places the artifact out-of-band and simply
  surface the server's refusal honestly (minimal, keeps authority fully
  out-of-band), or (b) additionally display current authorization state
  (read-only) before the confirm step?
- **Q3 — Preview mechanics:** any objection to a new strictly read-only
  preview endpoint if the design lands there (vs deriving the consequence
  list client-side)?

On confirmation this FO's status flips to confirmed (version bump), and the
arc proceeds: design packet → IADA → CFADA → Human Design Review → build.
