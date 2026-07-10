---
entity: gStack
aliases:
  - gstack
  - Garry's Stack
  - transpara-ai/gstack
  - garrytan/gstack
tier: investigation
status: compiled
last_compiled: 2026-06-13
civilization_contribution: "Pattern-only (v3.9.1 crosswalk row; frozen at the v3.9 reference point): the named co-inspiration of U7 CapabilityArtifact governance for skills/plugins/workflow packs (with the Hermes example plugins) and a joint source of the U9 operator-UX / proof-of-work update set; its software-factory skill ideas may inform native design but must not influence work without usage logging and capability evidence; never a controller, release process, or EventGraph truth."
raw_documents: []
current_research_version:
sources:
  - /Transpara/transpara-ai/repos/docs/dark-factory/v3.9/implementation/epics/02-technology-decision-crosswalk-v3.9.md  # v3.9.1 crosswalk; gStack decision row (L83) + per-item note "Decision: pattern-only" (L191-195) + freeze/reopen policy (L41-68)
  - raw/transpara/dark-factory/v3.9/01-unified-architecture-decisions-v3.9.md  # Decision 15: external frameworks stay outside control roles
  - /Transpara/transpara-ai/repos/docs/dark-factory/research/checkpoints/2026-05-13-06-phase-4-batch-d-governance-self-evolution-platform-tooling.md  # Phase 4 Batch D — repo-grounded candidate analysis of transpara-ai/gstack (candidate 7, L343-451; inclusion-matrix row L591; cross-candidate synthesis L653-784)
  - /Transpara/transpara-ai/repos/docs/dark-factory/research/checkpoints/2026-05-13-10-civilization-landscape-investigation-closeout.md  # final inclusion summary — gstack as pattern/reference only (L144); U7 CapabilityArtifact + U9 Site operator UX update set (L223,225)
  - /Transpara/transpara-ai/repos/wiki/wiki/civilization-landscape-investigation.md  # the parent investigation: gStack as candidate, pattern-only outcome, U7/U9 attribution (← gStack, Hermes plugins; ← Paperclip/Multica/Symphony/gStack)
  - /Transpara/transpara-ai/repos/gstack/README.md  # upstream README (context only): Garry Tan authorship, "23 specialists + 8 power tools", "open source software factory", MIT
  - /Transpara/transpara-ai/repos/gstack/package.json  # upstream package.json: name gstack, version 1.39.1.0, "Garry's Stack — Claude Code skills + fast headless browser", license MIT
  - /Transpara/transpara-ai/repos/gstack/ETHOS.md  # upstream "Builder Ethos" (context only): the "Golden Age" / "boil the lake" productivity thesis
  - "GitHub API: repos/transpara-ai/gstack (fork metadata, 2026-06-13 live) — isFork=true, parent=garrytan/gstack, createdAt 2026-05-09T11:13:06Z, MIT, description \"Use Garry Tan's exact Claude Code setup: 23 opinionated tools...\""
  - Open Brain  # 2026-06-13 capture on the civilization-landscape-investigation compile — U7 ← gStack/Hermes plugins; U9 ← Paperclip/Multica/Symphony/gStack; pattern-only bucket membership
confidence:
  decision_row: high — gStack has a complete row in the v3.9.1 crosswalk (pattern-only / workflow-skill pattern)
  fork_date_and_identity: high — confirmed live via GitHub fork metadata (createdAt 2026-05-09, parent garrytan/gstack), and matches the prompt's stated fork date
  repo_internals: thin — the investigation inspected only the README; "actual code was not inspected beyond README" (Batch D). Local-clone facts (version, license, command list) are filesystem-verified this run but were not the investigation's evidence base.
  tool_count: contested-by-source — upstream README headline and the fork description say "23 tools"; the README's own install snippet enumerates ~37 slash commands and the local clone contains 47 SKILL.md files. "23" is the upstream's framing, carried as such; see fail-legible note.
  u7_u9_attribution: medium — the closeout names U7 and U9 as update items but does not list gStack inline on those lines; the gStack→U7/U9 attribution is carried by the compiled [[civilization-landscape-investigation]] article and an Open Brain capture, both read this run.
  productivity_claims: context-only / upstream-marketing — the README's "810× my 2013 pace" and ETHOS "10,000+ lines/day" figures are upstream self-reported claims, not load-bearing here and not independently verified.
---

# gStack

**A forked public project the [[civilization-landscape-investigation]] evaluated and declined to adopt as anything more than a pattern.** gStack ("Garry's Stack") is Garry Tan's opinionated Claude Code setup — a suite of slash-command skills that turn a coding agent into a virtual engineering team (CEO, eng manager, designer, reviewer, QA lead, security officer, release engineer) plus a set of "power tools" (a headless browser, PDF generation, deploy helpers). Transpara forked it into the `transpara-ai` org on **2026-05-09** (`transpara-ai/gstack`, forked from the public upstream `garrytan/gstack`) so it could be read as ground-truth source rather than from marketing pages. During the [[dark-factory]] landscape investigation (Phase 4, Batch D, **2026-05-13**) it was assessed against the canonical v3.8 design and recorded in the v3.9.1 technology-decision crosswalk as **pattern-only** — specifically a **workflow / skill pattern**: its software-factory skill ideas may *inform* native design (it is the named inspiration behind the `CapabilityArtifact` governance rule and part of the operator-UX update set), but they "must not influence work without usage logging and capability evidence."

This article is about **our investigation and decision**, not a mirror of the upstream's documentation. The upstream is public OSS; it is cited here only as context, never re-published.

## Where it sits in the decision crosswalk

The authoritative record is the row in the v3.9.1 *External Technology Decision Crosswalk*:

| Field | Value (per crosswalk) |
|---|---|
| Current decision | **pattern-only** |
| ADR / doc ref | legacy coverage matrix / capability artifact rules |
| Integration mode | **workflow / skill pattern** |
| Owning epic | future capability or operator packet |
| Fork / adapter / pattern / exclude | **pattern** |
| Main risk | "skill patterns can bypass CapabilityArtifact evidence" |
| PR #61 change required? | "yes: freeze/reopen policy applies" |

The per-item note is the binding constraint:

> "Workflow or skill ideas are CapabilityArtifact candidates if they affect factory behavior. They must not influence work without usage logging and capability evidence."

In the canonical decision-category vocabulary this lands in the **pattern-only** bucket — learn the design idea, import no code, grant no control role. The crosswalk's own freeze policy applies: pattern-only adoptions are **frozen at the v3.9 reference point** and do not track upstream behaviour unless an epic explicitly reopens them. Reopening gStack would require recording the upstream version or commit reviewed, which pattern changed, and whether Dark Factory adopts, rejects, or defers it. The single accepted-canonical rule above all this row detail is [[v3-9]] Decision 15 — external frameworks from the investigation "must not become kernel, truth source, Work replacement, policy owner, release authority, certification authority, capability promoter, factory controller, or Site replacement." The crosswalk row is reviewed planning (`status: review`); Decision 15 is the law.

## What Changed with the Research

No released TAI-RES evaluation targets gStack — this is a support-only investigation page, so Topic Details is empty by design. The research record is the 2026-05-13 landscape investigation itself: the Phase 4 Batch D candidate analysis, the closeout's pattern/reference-only placement, and the v3.9.1 crosswalk row above. Nothing has moved since the 2026-06-13 compile; under the freeze policy the decision stands at the v3.9 reference point unless an epic explicitly reopens it.

## The Boundary

The binding constraint is the crosswalk's per-item note: *"Workflow or skill ideas are CapabilityArtifact candidates if they affect factory behavior. They must not influence work without usage logging and capability evidence."* Pattern-only means learn the design idea, import no code, grant no control role — and under Decision 15, gStack can never become kernel, truth source, Work replacement, policy owner, release authority, certification authority, capability promoter, factory controller, or Site replacement. Its safety features, project-learnings memory, and WIP checkpoints stay advisory: they "are not v3.8 EventGraph authority records," and its local state is not tamper-evident causal record unless wired into [[event-graph|EventGraph]].

## How it entered the arc

gStack was one of the [[civilization-landscape-investigation]] candidates — a sweep that evaluated each external tool against the then-canonical Dark Factory v3.8 design for marginal contribution, under a hard rule from the operator: *no aspirational claims accepted without code or canonical-document evidence; if access to a repo is missing, stop — do not substitute upstreams or marketing pages.* The fork into `transpara-ai` (2026-05-09) existed so the project could be read as source under that rule rather than from its website.

It was analysed in **Phase 4, Batch D** — "governance, self-evolution, and platform tooling" — alongside `hermes-agent-self-evolution`, `agent-governance-toolkit`, and [[paperclip|paperclip]] (gStack was candidate 7 of that batch). The investigation closeout placed gStack in a single list: **include as pattern/reference only.** Unlike Paperclip (which the closeout also put in the "defer until prerequisite controls exist" list), gStack was not flagged as needing deferral — it was treated straightforwardly as a workflow/skill reference to mine, not a control plane to gate.

## Capability Read

From the Batch D candidate analysis (evidence inspected: **README only**):

> "A skill/workflow stack for AI-assisted software development, centered on Claude Code and portable to multiple AI coding agents. It provides many slash-command skills for product planning, architecture review, design, code review, QA, shipping, security checks, browser automation, model benchmarking, memory/learning, safety guardrails, and multi-agent browser pairing."

The investigation recorded its self-framing as an "open source software factory" with roles such as "CEO, engineering manager, designer, reviewer, QA lead, security officer, and release engineer" — the same virtual-team framing the upstream README leads with. The core primitives it listed: slash-command skills, a software-sprint workflow, review/QA/security/release roles, browser automation, prompt-injection defense, pair-agent shared browser, a Codex second-opinion path, safety guardrails (`careful` / `freeze` / `guard`), and `learn` / taste / checkpoint memory.

What it explicitly **is not**, per the analysis: it is not [[event-graph|EventGraph]]; it is not v3.9 [[work|Work]]; it is not the [[runtime-broker|RuntimeBroker]], the [[authority-layer|authority model]], or release certification. "It is a workflow/skill layer and tooling suite." Its safety features (careful/freeze/guard, reviews, a security-officer audit, prompt-injection defense) are real but "are not v3.8 EventGraph authority records"; its project-learnings and taste memory are advisory and "must become MemoryReference/KnowledgeReference if influencing factory work"; its WIP commits/checkpoints "are not EventGraph truth."

## Benchmark Reality

Nothing about gStack was measured, and the numbers that exist do not even agree with each other. The upstream's headline count — "23 specialists / 23 opinionated tools" — is contradicted by its own install snippet (~37 slash commands) and by the local clone (47 `SKILL.md` files); "23" is carried as the upstream's chosen framing, the larger counts as what the repo actually ships, and none of it was load-bearing (the decision turned on governance boundaries, not tool quantity). The productivity claims — "~810× my 2013 pace," ETHOS's "10,000+ usable lines of code per day" — are upstream self-reported marketing, carried only as context for what gStack is selling; the investigation's own rule treats such claims as aspirational until code-verified, and the evidence base for the decision was the README alone.

## Why pattern-only, and not adopted

The investigation's marginal-contribution verdict was that gStack "contributes concrete software-factory workflow skills and review/QA/security patterns that could inform Work/Site/CapabilityArtifact UX" — a high-value *reference*, not a component. The recorded risks are the reason it stays a pattern:

- **Skills can become ungoverned capability artifacts** — the exact risk the crosswalk row names ("skill patterns can bypass CapabilityArtifact evidence").
- **Workflow commands can bypass the [[work|Work]] DAG and the TraceCompletenessGate** — i.e. drive factory behaviour without the evidence trail the kernel requires.
- **Browser automation and multi-agent pairing expand prompt-injection and exfiltration risk** — a boundary concern for sensitive factory work.
- **WIP commits / checkpoints are not EventGraph truth** — gStack's local state is not tamper-evident causal record unless wired into [[event-graph|EventGraph]].

The recommendation followed directly: *"Include as workflow/pattern reference only. Mine for Site operator UX, review/QA/security skill design, and CapabilityArtifact policy. Do not adopt as controller or release process."* This is the same containment logic the arc applies to every external workflow/control candidate — absorb the useful surfaces, cede no authority. The cross-candidate synthesis put it in one line: *"gstack = workflow/skill reference, not factory controller."*

## Where its patterns are allowed to land

gStack is one of the few candidates that fed *two* of the investigation's proposed canonical updates rather than one:

- **U7 — a `CapabilityArtifact` rule for skills / plugins / workflow packs.** The closeout surfaced "no `CapabilityArtifact` governance for skills/plugins/workflow packs" as Gap 7, and proposed U7 to fix it. The compiled [[civilization-landscape-investigation]] article and an Open Brain capture attribute U7 to gStack together with the Hermes example plugins — the two candidates that demonstrated "large skill/plugin ecosystems" and therefore the need to *govern* such ecosystems rather than let skills influence work silently. This is the direct ancestor of the crosswalk row's "usage logging and capability evidence" requirement.
- **U9 — expanded [[site|Site]] operator-UX requirements.** gStack's practical "planning, review, QA, security, ship, browser, and second-opinion workflows" are listed as candidate evidence for enriching Site operator actions and Work task templates — *as patterns, not as controlling process.* U9 is attributed to Paperclip, Multica, Symphony, and gStack jointly.

The crosswalk binds gStack's owning epic to a "future capability or operator packet"; as of this compile, no epic has reopened it, and the decision is frozen at the v3.9 reference point. The investigation's own framing of where its patterns may go is unchanged: *"Consider selected gstack workflows as patterns for Site operator actions and Work task templates, not as controlling process."*

## Fail-legible notes

- **Thin internal evidence.** The investigation inspected **only the README** ("README is extensive; actual code was not inspected beyond README"). Every claim about gStack's internals — skill semantics, memory model, guardrail behaviour, browser-automation security — is README-grounded, not code-verified by the investigation. Mark the repo-internals confidence **thin**. (Separately, the *local clone* of the fork was read this run for orientation facts — version `1.39.1.0`, MIT license, the command list — but those are not what the 2026-05-13 decision rested on.)
- **The "23 tools" figure is the upstream's framing, and the sources do not agree on a count.** The upstream README headline and the live fork description both say "23 specialists" / "23 opinionated tools" (plus "eight power tools"). But the README's own install snippet enumerates ~37 slash commands, and the local clone contains 47 `SKILL.md` files. The discrepancy is not resolved here: "23" is carried as the *upstream's chosen headline number*, the larger counts as what the repo actually ships. None of these counts was load-bearing in the decision, which turned on governance boundaries, not tool quantity.
- **Productivity claims are context, not evidence.** The README's "~810× my 2013 pace" and "240× the entire 2013 year," and the ETHOS "10,000+ usable lines of code per day," are upstream self-reported figures. They are carried only as context for *what gStack is selling*; they played no part in the pattern-only decision and are not independently verified. The investigation's own rule treats marketing claims as aspirational until code-verified.
- **U7 / U9 attribution is medium-confidence.** The closeout names U7 ("CapabilityArtifact rule for skills/plugins/workflow packs") and U9 ("Expanded Site operator UX requirements") as update items but does not print "gStack" on those two lines. The gStack→U7/U9 attribution is carried by the compiled [[civilization-landscape-investigation]] article and an Open Brain capture (both read this run), and is consistent with the Batch D synthesis that names gStack under both "skill/plugin ecosystems" (U7's motivation) and "Site operator actions / Work task templates" (U9's motivation). Stated as attribution, not as a verbatim closeout line.
- **Asserted, not proven.** The framing that gStack's skills could "bypass CapabilityArtifact evidence" or "bypass the Work DAG and TraceCompletenessGate" is the investigation's *risk assessment*, not a demonstrated failure — it is the reason the decision is fenced to pattern-only, not a record of harm observed.
- **Upstream is cited, never re-published.** Per org rule, `garrytan/gstack` is public OSS. Its README framing ("open source software factory"), authorship (Garry Tan, YC), and MIT license are corroborated as context for *why we forked it to read it*, not as content to mirror. The local fork's `upstream` remote is even configured with pushes disabled (`DISABLE_PUSH_TO_UPSTREAM`), consistent with the org's "read the source, never push upstream" posture. The wiki subject is our investigation and our decision.

## Sources & Provenance

- v3.9.1 **External Technology Decision Crosswalk** — `/Transpara/transpara-ai/repos/docs/dark-factory/v3.9/implementation/epics/02-technology-decision-crosswalk-v3.9.md` (decision row L83; per-item note "Decision: pattern-only" L191-195; freeze/reopen policy L41-68). This is the authoritative decision record. (`status: review` / `canonical: false`; the ratified routing rule is v3.9 Decision 15.)
- **Phase 4 Batch D** candidate analysis — `…/research/checkpoints/2026-05-13-06-phase-4-batch-d-governance-self-evolution-platform-tooling.md` (gStack section, candidate 7, L343-451; inclusion-matrix row L591; cross-candidate synthesis L653-784). Primary evidence for what the investigation found; explicitly README-only.
- **Investigation closeout** — `…/research/checkpoints/2026-05-13-10-civilization-landscape-investigation-closeout.md` (final inclusion summary: gStack under "pattern/reference only," L144; the U1-U10 proposed update set including U7 and U9, L223 / L225).
- **Parent investigation article** — `/Transpara/transpara-ai/repos/wiki/wiki/civilization-landscape-investigation.md` (gStack as a candidate, the pattern-only outcome, and the U7/U9 attribution to gStack with Hermes plugins / with Paperclip-Multica-Symphony).
- **Upstream (context only, not re-published)** — local clone of `transpara-ai/gstack` (fork of `github.com/garrytan/gstack`): `README.md` (Garry Tan authorship, "23 specialists + 8 power tools," "open source software factory," MIT); `package.json` (name `gstack`, version `1.39.1.0`, "Garry's Stack — Claude Code skills + fast headless browser," MIT); `ETHOS.md` (the "Golden Age" / "boil the lake" productivity thesis).
- **Fork metadata** — GitHub API `repos/transpara-ai/gstack`, fetched 2026-06-13: `isFork=true`, `parent=garrytan/gstack`, `createdAt=2026-05-09T11:13:06Z`, `license=MIT`, `description="Use Garry Tan's exact Claude Code setup: 23 opinionated tools that serve as CEO, Designer, Eng Manager, Release Manager, Doc Engineer, and QA"`. Durable upstream URL (context only): https://github.com/garrytan/gstack.
- **Open Brain** — the 2026-06-13 capture on the `civilization-landscape-investigation` compile, recording the pattern-only bucket membership and the U7 (← gStack / Hermes plugins) and U9 (← Paperclip / Multica / Symphony / gStack) attributions.

**Conflicts / open items.** (1) *Tool count* — upstream "23" vs. README install-list ~37 vs. 47 `SKILL.md` files; stated, not resolved; not decision-relevant. (2) *U7/U9 attribution* — named in the compiled investigation article and Open Brain, not printed inline on the closeout's U-lines; carried as medium-confidence attribution. (3) *Repo internals* — README-only for the investigation; thin. (4) *Productivity figures* — upstream marketing, context only. `[[civilization-landscape-investigation]]`, `[[dark-factory]]`, `[[v3-9]]`, `[[work]]`, `[[site]]`, `[[event-graph]]`, `[[runtime-broker]]`, `[[authority-layer]]`, and `[[paperclip]]` resolve to compiled articles; `[[hive-governance]]` is a forward reference.
