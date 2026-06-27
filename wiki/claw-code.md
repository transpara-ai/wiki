---
entity: claw-code
aliases:
  - claw-code
  - claw code
  - transpara-ai/claw-code
  - ultraworkers/claw-code
tier: investigation
status: compiled
last_compiled: 2026-06-13
sources:
  - "GitHub API: repos/transpara-ai/claw-code (fork metadata, live 2026-06-13) — isFork=true, parent=ultraworkers/claw-code, createdAt 2026-04-01T18:14:03Z, licenseInfo=null, description \"The fastest repo in history to surpass 100K stars ⭐. Better Harness Tools that make real things done. Built in Rust using oh-my-codex.\" — https://github.com/transpara-ai/claw-code"
  - /Transpara/transpara-ai/repos/wiki/raw/open-brain/2026-06.md  # fork-chronology ledger (L4043-4044): "4/01 claw-code <- ultraworkers"; harness bucket "(gstack, claw-code, openclaw)"; the Apr–May fan-out retroactively named the "Civilization Landscape Investigation"
  - /Transpara/transpara-ai/repos/docs/dark-factory/v3.9/implementation/epics/02-technology-decision-crosswalk-v3.9.md  # v3.9.1 crosswalk — checked in full; NO row for claw-code (16 rows: MetaGPT, OpenManus, OpenBrain, MemPalace, Karpathy LLM Wiki, Karpathy Autoresearch, Hermes, OpenClaw, MS Agent Governance Toolkit, gStack, Paperclip, Symphony, Multica, Miro Flow, Miro Thinker, Brett Brewer Org Memories)
  - raw/transpara/dark-factory/v3.9/01-unified-architecture-decisions-v3.9.md  # Decision 15: external frameworks stay outside control roles
  - /Transpara/transpara-ai/repos/docs/dark-factory/research/checkpoints/2026-05-13-10-civilization-landscape-investigation-closeout.md  # closeout inclusion summary (§6) — claw-code absent from every bucket; investigation surveyed a fixed candidate set
  - /Transpara/transpara-ai/repos/wiki/wiki/civilization-landscape-investigation.md  # parent investigation article — the verbatim 22-item candidate list (§"What was surveyed"); claw-code not among them
  - /Transpara/transpara-ai/repos/wiki/wiki/gstack.md  # sibling harness-bucket investigation article (house pattern for a forked public tool); the harness-cluster framing
confidence:
  fork_identity_and_date: high — live GitHub fork metadata (isFork=true, parent=ultraworkers/claw-code, createdAt 2026-04-01) matches the prompt and the Open Brain fork ledger; the two independent sources agree.
  theme_rust_oh_my_codex: high-as-upstream-framing — "Built in Rust using oh-my-codex" and "Better Harness Tools" are the upstream's own repo description, carried verbatim as context; not independently code-verified this run (no local clone exists).
  investigation_evaluation_claim: CONTESTED / corrected — the prompt states the Civilization Landscape Investigation "evaluated" claw-code. The evidence does not support a *formal* evaluation: claw-code has no crosswalk row, appears in no Phase 4–7 research checkpoint, and is not in the closeout inclusion summary or the 22-item surveyed list. What IS sourced is a retrospective Open Brain bucket-naming that files claw-code under "harness" within the Apr–May fork fan-out it calls the investigation. Stated fail-legibly below; not silently accepted.
  decision_row: ABSENT — there is no decision row for claw-code in the v3.9.1 crosswalk. Marked thin; the binding default is v3.9 Decision 15 (fork ≠ adoption; external code stays outside control roles absent an accepted ADR).
  repo_internals: none — no local clone, no README read this run, no code inspected. Everything about what claw-code *does* is upstream-description-level only. Thin.
  license: thin/contested — GitHub fork metadata reports licenseInfo=null (no license file detected on the fork). The upstream's license was not inspected this run. Treat the fork as unlicensed-as-detected until verified.
---

# claw-code

**A public project forked into the `transpara-ai` org during the spring 2026 landscape sweep, but one with no formal decision on record — the fail-legible case.** `claw-code` is an upstream open-source effort by the `ultraworkers` org, self-described as "Better Harness Tools that make real things done… Built in Rust using oh-my-codex" (the same family as the [[gstack|gStack]] / [[openclaw|OpenClaw]]-style coding-harness tooling the arc was surveying). Transpara forked it into `transpara-ai/claw-code` on **2026-04-01** — one of the earliest forks in the Apr–May "fan-out," predating the formal [[civilization-landscape-investigation]] (2026-05-13) by six weeks. It sits in the **harness** cluster of that fan-out alongside [[gstack|gStack]] and OpenClaw (Open Brain fork ledger).

This article is about **our handling of it**, not a mirror of the upstream's documentation. The upstream is public OSS; it is cited here only as context, never re-published. And the central, non-negotiable finding of this compile is a **fail-legible gap**: unlike its harness-cluster siblings, claw-code was **never given a decision row** in the v3.9.1 technology-decision crosswalk, and it does **not appear in any of the formal investigation's Phase 4–7 checkpoints**. What is solidly known is the fork; almost everything else is thin or absent, and is marked as such.

## What is actually known (high confidence)

Two independent sources agree on the fork facts, and only the fork facts:

| Field | Value | Source |
|---|---|---|
| Fork path | `transpara-ai/claw-code` | GitHub fork metadata (live 2026-06-13) |
| Is a fork | yes (`isFork=true`) | GitHub fork metadata |
| Upstream parent | `ultraworkers/claw-code` | GitHub fork metadata; Open Brain ledger ("4/01 claw-code <- ultraworkers") |
| Fork date | **2026-04-01** (`createdAt 2026-04-01T18:14:03Z`) | GitHub fork metadata; matches the prompt and the Open Brain ledger |
| License (on fork) | **none detected** (`licenseInfo=null`) | GitHub fork metadata |
| Upstream self-description | "The fastest repo in history to surpass 100K stars ⭐. Better Harness Tools that make real things done. Built in Rust using oh-my-codex." | GitHub repo description (upstream-authored; context only) |

The theme in the prompt — *Rust harness tools built on oh-my-codex* — is corroborated, but its only basis is the **upstream's own one-line repo description**. No local clone of `transpara-ai/claw-code` exists on this machine (a filesystem search returned only unrelated `openclaw` paths and test fixtures), so no README, manifest, or source was read this run. Treat "Rust / oh-my-codex / harness tools" as the upstream's framing, accurate as far as it goes, not as code-verified internals.

## Where it sits in the arc

The grounding for claw-code's place in the story is a single Open Brain entry: the **fork-chronology ledger** captured 2026-06-13 (`raw/open-brain/2026-06.md`, L4043–4044). It records the fork (`4/01 claw-code <- ultraworkers`) in a dated list of the spring forks, and then buckets the whole Apr–May wave by function:

> "The Apr–May fan-out = the 'Civilization Landscape Investigation': memory (OB1, mempalace), RAG/knowledge (graphify, PageIndex), orchestration (multica, solo-orchestrator, symphony, paperclip), agents (hermes, Miro*), **harness (gstack, claw-code, openclaw)**, governance (agent-governance-toolkit)."

So claw-code's recorded identity is: a **harness-cluster** fork, peer to [[gstack|gStack]] and OpenClaw — coding-agent tooling, evaluated (in intent) for what its harness ideas might contribute to the [[dark-factory]]'s own agent-execution surface. That is the extent of what the corpus says about *why* it was pulled in.

## The fail-legible gap: no formal decision exists

The prompt frames claw-code as "a forked public project the Civilization Landscape Investigation evaluated." The honest, sourced position is narrower, and the difference matters enough to state plainly rather than paper over:

- **No crosswalk row.** The v3.9.1 *External Technology Decision Crosswalk* — the authoritative per-item register whose stated purpose is "to make external technology decisions visible to reviewers before implementation begins" — has **sixteen rows** (MetaGPT, OpenManus, OpenBrain, MemPalace, Karpathy LLM Wiki, Karpathy Autoresearch, Hermes, **OpenClaw**, Microsoft Agent Governance Toolkit, **gStack**, Paperclip, Symphony, Multica, Miro Flow, Miro Thinker, Brett Brewer Org Memories). **claw-code is not one of them.** Its two harness-cluster siblings each got a row; claw-code did not. So there is **no recorded decision** — not selected, not pattern-only, not deferred, not research-only, not excluded.
- **Absent from the formal investigation record.** A search across the entire `docs/dark-factory/research/` checkpoint tree (kickoff, access-verification, Phases 0–8, all four Phase-4 batches, the Phase-5 inclusion matrix, the Phase-7 update set, the closeout) returns **zero mentions** of claw-code, "claw code," "ultraworkers," or "oh-my-codex." The investigation's **closeout inclusion summary** (`…-closeout.md` §6) enumerates every surveyed candidate across its five buckets — core, optional-adapter, pattern/reference, deferred, rejected — and claw-code is in **none** of them.
- **Not on the surveyed candidate list.** The formal investigation fixed a **22-item candidate list** at kickoff, each pinned to a repo path (reproduced in the [[civilization-landscape-investigation]] article). Its harness/agent-execution entries are OpenClaw, MetaGPT, OpenManus, the Hermes family, [[multica]], solo-orchestrator, and [[symphony|Symphony]]; its platform-tooling entries are the Agent Governance Toolkit, [[gstack|gStack]], and [[paperclip|Paperclip]]. **claw-code is not on the list.**

> ⚠ **Fail-legible note (the "investigation evaluated it" claim is contested by the evidence).** The only source that ties claw-code to the "Civilization Landscape Investigation" is the **retrospective Open Brain bucket-naming** (2026-06-13), which uses "Civilization Landscape Investigation" as a label for the *whole Apr–May fork fan-out*. The **formal investigation of 2026-05-13** — the one that produced the checkpoints, the inclusion matrix, and the crosswalk — did **not** evaluate claw-code: it is absent from every artifact that survey generated. These two senses of "the investigation" are not the same scope, and the wiki does not silently merge them. What is sourced: claw-code was forked, and was *grouped* with the investigation's harness candidates after the fact. What is **not** sourced: any per-item analysis, marginal-contribution verdict, or decision for claw-code. (Compare [[gstack|gStack]], whose Batch-D analysis, inclusion-matrix row, and pattern-only crosswalk row are all on the record — claw-code has none of these.)

## What the absence does *not* mean

A missing row is a missing decision, not a silent green light — and the arc has a default rule for exactly this. The accepted-canonical constraint that governs every external fork from the spring sweep is [[v3-9]] **Decision 15, "External Frameworks Stay Outside Control Roles"**: external frameworks "remain references, optional adapters, or patterns unless a later accepted ADR changes their status. They must not become kernel, truth source, Work replacement, policy owner, release authority, certification authority, capability promoter, factory controller, or Site replacement." The crosswalk's own gate reinforces it from the other side: *"No future epic may integrate, fork, or pattern-expand any listed technology until the decision row is complete and reviewed."* claw-code's row is not complete — it does not exist — so by the crosswalk's own rule it is **not cleared for any integration, adaptation, or pattern-expansion**. A fork is an access mechanism (read the source as ground truth, never push upstream), not an adoption.

In the canonical decision vocabulary, claw-code is best described as **un-triaged / proposal-only** with respect to Dark Factory: pulled into the org for a look, never carried through the survey to a recorded outcome. It is closest in spirit to the "proposal-only / candidate" category the [[civilization-landscape-investigation]] article lists, but even that is an inference about *status from absence*, not a label any source applied to it.

## Fail-legible notes

- **Thinnest of the investigation-tier entries.** Where a sibling like [[gstack|gStack]] has a Batch-D candidate analysis, an inclusion-matrix row, a closeout bucket, and a crosswalk row, claw-code has **only** fork metadata plus one line in an Open Brain fork ledger. Mark the entire entry **thin**; this is a stub grounded in two facts (the fork, the bucket) and an explicitly-stated gap.
- **No decision on record.** There is no selected / pattern-only / research-only / deferred / excluded verdict for claw-code anywhere in the crosswalk or the research checkpoints. Reported as **absent**, not inferred.
- **"Investigation evaluated it" is corrected, not repeated.** Per the fail-legible note above, the formal 2026-05-13 investigation did not evaluate claw-code; the association is a later, broader use of the investigation's name. Stated, cited, not resolved in the prompt's favour.
- **Repo internals unverified.** No local clone, no README, no source inspected this run. All claims about what claw-code *is or does* derive from the upstream's one-line GitHub description. The "Rust / oh-my-codex / harness tools" theme is upstream framing, not independently confirmed.
- **License is null-as-detected.** GitHub reports no license on the fork (`licenseInfo=null`); the upstream's license terms were not inspected. Any future supply-chain or integration step would have to resolve licensing first — the crosswalk requires "license and supply-chain status when code or adapter integration is proposed," and that review has not happened.
- **The "100K stars" claim is upstream marketing.** The repo description's "fastest repo in history to surpass 100K stars" is the upstream's self-promotion, carried only as verbatim context for *what the project advertises*; it is not load-bearing and was not verified.
- **Upstream is cited, never re-published.** Per org rule, `ultraworkers/claw-code` is public OSS. Its description and authorship are reproduced here solely as context for why a fork exists, not as content to mirror. The wiki subject is **our** handling and the gap in it.

## Sources & provenance

- **Fork metadata** — GitHub API `repos/transpara-ai/claw-code`, fetched 2026-06-13: `isFork=true`, `parent=ultraworkers/claw-code`, `createdAt=2026-04-01T18:14:03Z`, `licenseInfo=null`, `description="The fastest repo in history to surpass 100K stars ⭐. Better Harness Tools that make real things done. Built in Rust using oh-my-codex."` This is the primary high-confidence source for the fork identity, date, and theme. Durable upstream URL (context only): https://github.com/ultraworkers/claw-code; fork: https://github.com/transpara-ai/claw-code.
- **Open Brain fork-chronology ledger** — `/Transpara/transpara-ai/repos/wiki/raw/open-brain/2026-06.md`, L4043–4044: the dated fork list ("4/01 claw-code <- ultraworkers") and the function-bucketed fan-out that files claw-code under "harness (gstack, claw-code, openclaw)" and labels the Apr–May wave the "Civilization Landscape Investigation." Sole source for claw-code's recorded place in the arc.
- **v3.9.1 External Technology Decision Crosswalk** — `/Transpara/transpara-ai/repos/docs/dark-factory/v3.9/implementation/epics/02-technology-decision-crosswalk-v3.9.md`. Read in full this run; its sixteen decision rows are enumerated above. **Cited as a negative result:** claw-code has no row. The crosswalk is `status: review` / `canonical: false`; the ratified rule above it is [[v3-9]] Decision 15.
- **Investigation closeout** — `/Transpara/transpara-ai/repos/docs/dark-factory/research/checkpoints/2026-05-13-10-civilization-landscape-investigation-closeout.md` (§6 inclusion summary). Cited as a negative result: claw-code is in none of the five buckets. (A grep across the entire `…/research/checkpoints/` tree for claw-code / ultraworkers / oh-my-codex returned zero hits.)
- **Parent investigation article** — `/Transpara/transpara-ai/repos/wiki/wiki/civilization-landscape-investigation.md`: the verbatim 22-item surveyed candidate list (claw-code not among them) and the canonical decision-category vocabulary.
- **Sibling article (house pattern)** — `/Transpara/transpara-ai/repos/wiki/wiki/gstack.md`: the harness-cluster framing and the template for a forked-public-tool investigation entry; included to make the *contrast* explicit (gStack has the full decision trail claw-code lacks).

**Conflicts / open items.** (1) *Did the investigation evaluate claw-code?* — the prompt says yes; the formal-investigation record says no (absent from crosswalk, checkpoints, and the 22-item list). Resolved fail-legibly in favour of the documentary evidence: claw-code was *forked and grouped*, not *formally evaluated*. The only "investigation" link is the retrospective Open Brain bucket-name. (2) *Decision status* — none on record; the governing default is Decision 15 (fork ≠ adoption). (3) *License* — `null` as detected on the fork; upstream terms uninspected. (4) *Repo internals* — unverified; upstream-description-level only. `[[civilization-landscape-investigation]]`, `[[dark-factory]]`, `[[v3-9]]`, `[[gstack]]`, `[[multica]]`, `[[symphony]]`, `[[paperclip]]`, and `[[the-lovyou-ai-fork]]` resolve to compiled articles; `[[hive-governance]]` and `[[work]]` are forward references.
