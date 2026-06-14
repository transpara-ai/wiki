---
entity: MemPalace
aliases:
  - MemPalace
  - mempalace
  - the advisory memory candidate
  - the memory-palace fork
tier: investigation
status: compiled
last_compiled: 2026-06-13
sources:
  - raw/transpara/dark-factory/v3.9/implementation/epics/02-technology-decision-crosswalk-v3.9.md  # DF-V3.9-EPIC-TECH-CROSSWALK v3.9.1 (status: review): the MemPalace decision row + per-item note
  - raw/open-brain/2026-06.md  # fork-provenance line (4/08 mempalace <- MemPalace) and the Apr–May "Civilization Landscape Investigation" fan-out roster
  - https://github.com/transpara-ai/mempalace/blob/main/README.md  # the forked README (transpara-ai mirror, read 2026-06-13) — UPSTREAM CONTEXT ONLY, not re-published
confidence:
  decision_row: high — quoted verbatim from the v3.9.1 crosswalk decision table and per-item note; the row exists (this is NOT a thin/no-row case)
  crosswalk_status: the crosswalk doc is status:review / canonical:false; the ratified rule is v3.9 Decision 15 (external frameworks stay outside control roles), not the row detail. See note.
  fork_date_and_origin: medium-high — "4/08 ... mempalace <- MemPalace" comes from a single Open Brain capture (raw/open-brain/2026-06.md); consistent with the seed, but rests on that one line
  upstream_description: upstream-claimed, not verified — the "what it is" / benchmark / security facts come from the forked README, which is upstream marketing/docs; treated as context, never as Transpara findings
  implementation_state: thin — no implementation owner is selected; nothing in the surveyed sources shows MemPalace wired into the platform
---

# MemPalace

**A forked public AI-memory project that the [[civilization-landscape-investigation]] evaluated and admitted to the [[dark-factory]] roadmap as an *advisory memory candidate* — usable later behind a memory adapter, never as truth, authority, or certification evidence.** It entered the arc as one node in the April–May 2026 fan-out of external repos the investigation pulled into the `transpara-ai` org to study: per an Open Brain capture, `mempalace` was forked from upstream `MemPalace/mempalace` on **2026-04-08**, in the "memory" cluster alongside OB1/OpenBrain (`raw/open-brain/2026-06.md`). The subject of *this* article is Transpara's evaluation and decision about MemPalace — not the upstream project's own documentation, which is cited only as context below.

The decision is recorded, and it is narrow. The v3.9.1 technology-decision crosswalk gives MemPalace a real row (`DF-V3.9-EPIC-TECH-CROSSWALK`): current decision **"included as advisory memory candidate,"** integration mode **"possible memory adapter; no truth authority,"** owning epic **"future memory integration packet, not currently selected,"** classification **adapter/reference**. The PR-change column reads "yes: state no implementation owner yet." So MemPalace is *in* the design — but only as a named candidate behind a boundary nobody has been assigned to build.

## What the investigation decided, and why

The crosswalk's per-item note is short and is the load-bearing text for this entity. Quoted in full:

> Decision: advisory memory candidate. No implementation owner is selected by this roadmap package. If wired later, MemPalace output must become MemoryReference evidence only when it materially influences work.
>
> Forbidden:
> - MemPalace as truth source
> - MemPalace as authority
> - MemPalace as certification evidence without EventGraph record
> - secret-bearing memory use
> - quarantined memory use

(`02-technology-decision-crosswalk-v3.9.md`, "MemPalace" note.) The decision table adds the one-line risk that motivates the whole posture: **"memory can influence work without evidence if miswired."** That is the entire reason MemPalace is admitted as a *candidate* rather than a dependency — a memory store that silently shapes a plan or a repair, with no recorded reference, is exactly the failure mode the [[dark-factory]] accountability model exists to prevent.

This places MemPalace inside the platform's broader [[memory-knowledge-advisory|advisory memory/knowledge layer]] (spec `DF-V3.9-SPEC-006`), where the rule is identical for any recall store: it "advise[s] but do[es] not govern." If MemPalace is ever wired in, its output is only legitimate once it becomes a **`MemoryReference`** — an explicit, fielded evidence record (source, hash, `retrieved_at`, `influence_summary`, trust level, freshness, contradiction refs) emitted *before* certification can pass. The advisory-layer article carries those mechanics; this article carries the per-project decision that routes MemPalace into them.

The crosswalk ties MemPalace to **v3.9 Decisions 9 and 12, and the v3.9 memory model** (its "ADR / doc ref" cell). Decision 12 is the cell that routes external frameworks; the memory model is `DF-V3.9-SPEC-006`. The *ratified* governing rule, though, is **Decision 15 — "External Frameworks Stay Outside Control Roles,"** under which every Civilization Landscape Investigation candidate (MemPalace included) "remain[s] references, optional adapters, or patterns unless a later accepted ADR changes their status" and must not become "kernel, truth source, Work replacement, policy owner, release authority, certification authority, capability promoter, factory controller, or Site replacement." (See [[civilization-landscape-investigation]] for how Decision 15 is the law and the crosswalk row is the bookkeeping.)

## Where it sits among the other candidates

In the investigation's vocabulary, MemPalace is one of only **two** items admitted as an *included advisory / optional-adapter candidate* rather than pattern-only, deferred, research-only, or excluded — the other being the Microsoft [[agent-governance-toolkit|Agent Governance Toolkit]] (`PolicyEngineAdapter` candidate). Both share the same shape: a named candidate, behind a defined adapter boundary, with evidence and quarantine rules, and **no implementation owner selected yet**. By contrast the Brett Brewer `org-memories` analysis — the other memory-domain item — was resolved as *research-only / subsumed* by the advisory model, with no independent adapter selected. MemPalace's status as a live *candidate* (not merely subsumed research) is therefore notable, and is the distinction this article exists to record.

The Open Brain roster of the fan-out places MemPalace specifically in the **memory** group of the survey — "memory (OB1, mempalace), RAG/knowledge (graphify, PageIndex), orchestration (...), agents (...), harness (...), governance (...)" (`raw/open-brain/2026-06.md`). So within the 22-item landscape, MemPalace was evaluated as a candidate *recall store*, paired conceptually against OpenBrain/OB1 — the same memory slot the advisory-layer spec describes as "MemPalace or equivalent recall storage."

## The upstream project (context only — not a Transpara finding)

> ⚠ **Provenance / org-boundary note.** Everything in this section comes from the **forked README in the `transpara-ai` mirror** (`github.com/transpara-ai/mempalace`, read 2026-06-13), which is upstream-authored documentation. Per the org rule the prompt restates, the wiki subject is *our* investigation and decision; upstream docs are cited as context and **never re-published as fact**. These are the upstream project's *own claims about itself*, not anything Transpara verified, benchmarked, or adopted. The crosswalk admitted MemPalace as a *candidate*; it did not endorse any of the figures below.

The upstream README (MIT-licensed; the fork carries version `3.3.5` in its badges) describes MemPalace as **"local-first AI memory"** that stores conversation history as **verbatim text** and retrieves it with semantic search — it "does not summarize, extract, or paraphrase." Its index is structured into a spatial metaphor: people/projects are *wings*, topics are *rooms*, original content lives in *drawers*, so searches can be scoped rather than run against a flat corpus. The retrieval backend is pluggable (ChromaDB by default; interface in `mempalace/backends/base.py`). It ships an **MCP server (29 tools)**, a temporal entity-relationship knowledge graph backed by local SQLite, per-agent "wings and diaries," and two Claude Code auto-save hooks. The README headlines retrieval-recall benchmarks (e.g. a "96.6% R@5 raw on LongMemEval, zero API calls" claim, plus hybrid/rerank figures) and states they are reproducible from the repo.

> ⚠ **Fail-legible — these claims are upstream-asserted and unverified here.** The benchmark numbers, the "local-first / nothing leaves your machine" privacy posture, and the "no API key required" property are the *upstream project's* statements. This run did not run the benchmarks, inspect the code paths, or otherwise verify them, and the crosswalk's admission of MemPalace as a candidate does not depend on or ratify them. Treat them as "what the upstream says," full stop.

> ⚠ **Security note from the upstream README (flagged, not assessed).** The forked README opens with a **"Scam alert"** declaring its only official sources to be `github.com/MemPalace/mempalace`, the `mempalace` PyPI package, and `mempalaceofficial.com`, and naming `mempalace.tech` as an impostor domain that "may distribute malware." It also carries a banner about Claude Code session expiry without auto-save hooks. This is reproduced as *context about the upstream supply-chain situation*; it is not a Transpara security assessment, and it underscores why the crosswalk requires license + supply-chain review before any memory adapter is actually integrated (the general rule applied to the Agent Governance Toolkit, and to any future MemPalace memory-integration packet).

## Source conflict: which "upstream" is upstream

There is a tension worth stating rather than smoothing over. The compile request names the upstream as **`MemPalace/mempalace`**, and the Open Brain fork line agrees: **"4/08 ... mempalace <- MemPalace"** (`raw/open-brain/2026-06.md`). The forked README's own "Scam alert" likewise points to `github.com/MemPalace/mempalace` as canonical. So all three sources read this run agree the upstream is the public **`MemPalace`** org's `mempalace`.

The org-governance framing in the prompt ("treat the upstream as public OSS") is a *policy stance* — apply the org's standard don't-republish caution to forked public projects — not a claim about which org owns the upstream. This article therefore reports the upstream as `MemPalace/mempalace` (the sourced fact) and applies the upstream-caution *policy* (the governance rule), without conflating the two.

## Implementation status

> ⚠ **Thin by design — no owner, not wired.** The strongest, best-sourced fact about MemPalace's *implementation* is that there isn't one. The crosswalk explicitly records "no implementation owner is selected" and "future memory integration packet, not currently selected." The [[memory-knowledge-advisory|advisory layer]] it would plug into is itself specified-but-not-demonstrated — Base Slice 0 *forbids* memory recall and knowledge reuse — so even the receiving socket is not exercised in the proven control plane. Open Brain has **no operational thought about MemPalace specifically** (searches this run returned only the fork-roster line); there is no record of it being run, benchmarked, or integrated inside Transpara. Anyone reading this expecting a live integration should stop here: as of 2026-06-13 the surveyed sources show a *decision to keep MemPalace available as a candidate*, and nothing past that.

## How this relates to the rest of the arc

MemPalace is a leaf of the [[civilization-landscape-investigation]] — one of the 22 candidate repos that survey looked outward at and chose to *learn from or hold as a candidate while importing none as authority.* Its decision row is governed by [[dark-factory]] v3.9 Decision 15 and routed into the [[memory-knowledge-advisory|advisory memory/knowledge layer]] via the `MemoryReference` mechanism. It sits one rung more "live" than the subsumed `org-memories` analysis and shares its candidate status only with the Agent Governance Toolkit. If a future memory-integration packet ever reopens it, the crosswalk's `## Review Rule` requires re-verifying its current decision, ADR reference, integration mode, owning epic, **license and supply-chain status**, conformance gate, and upstream-refresh strategy before any code is touched — the same fail-closed gate the whole investigation runs on.

## Sources & provenance

- `raw/transpara/dark-factory/v3.9/implementation/epics/02-technology-decision-crosswalk-v3.9.md` — **`DF-V3.9-EPIC-TECH-CROSSWALK`**, *Dark Factory v3.9.1 External Technology Decision Crosswalk* (status: review; canonical: false; v3.9.1; created/updated 2026-05-18). The MemPalace decision-table row ("included as advisory memory candidate" / "possible memory adapter; no truth authority" / "future memory integration packet, not currently selected" / risk "memory can influence work without evidence if miswired") and the verbatim per-item "MemPalace" note with the five-item Forbidden list. This is the row this article is grounded in — the crosswalk *does* have a row for MemPalace.
- `raw/open-brain/2026-06.md` — Open Brain capture giving the fork provenance ("4/08 ... mempalace <- MemPalace") and placing MemPalace in the "memory (OB1, mempalace)" cluster of the April–May "Civilization Landscape Investigation" fan-out. Single-capture source for the 2026-04-08 fork date and upstream origin.
- `https://github.com/transpara-ai/mempalace/blob/main/README.md` — the forked README in the `transpara-ai` mirror (read via GitHub API, 2026-06-13; blob sha `bc67637`). **Upstream context only**, used solely for the "upstream project (context only)" and "source conflict" sections; its self-descriptions, benchmark figures, privacy claims, and scam-alert/security notices are upstream-authored and are *not* re-published as Transpara findings.

**Conflicts and thin spots stated, not resolved.** (1) *Upstream identity*: the seed, the Open Brain fork line, and the forked README all name the upstream as `MemPalace/mempalace`; the prompt's upstream-caution framing is read as a governance *policy* (apply don't-republish caution), not a claim about the repo's org — both stated above, neither silently chosen. (2) *Crosswalk status*: the row is `status: review` / `canonical: false`; the ratified rule is v3.9 Decision 15, not the row detail. (3) *Upstream claims* (benchmarks, "local-first," "no API key," scam-alert) are upstream-asserted and **not verified this run** — labeled as context throughout. (4) *Implementation*: thin — no owner, not wired, no MemPalace-specific Open Brain operational record found. Every claim above traces to one of the three sources read this run; no MemPalace-specific detail was carried from memory. `[[wikilinks]]` to [[civilization-landscape-investigation]], [[dark-factory]], [[memory-knowledge-advisory]], and [[agent-governance-toolkit]] are compiled except the last, which is a forward reference.
