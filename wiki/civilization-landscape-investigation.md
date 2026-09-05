---
entity: The Civilization Landscape Investigation
org: transpara-ai
primary_placement: civilization/arc
placements:
  - civilization/arc
classification: internal
aliases:
  - Civilization Landscape Investigation
  - Dark Factory Landscape Investigation
  - the 2026-05-13 investigation
  - the landscape investigation
  - tech-decision crosswalk
tier: arc
status: compiled
last_compiled: 2026-06-13
sources:
  - raw/transpara/dark-factory/research/checkpoints/2026-05-13-civilization-landscape-investigation-kickoff.md  # kickoff: scope, operating rule, the 22-item candidate list, eight-phase methodology, batches A-D
  - raw/transpara/dark-factory/research/checkpoints/2026-05-13-07-phase-5-inclusion-marginal-contribution-matrix.md  # Phase 5: the six-class vocabulary and the full per-candidate inclusion matrix
  - raw/transpara/dark-factory/research/checkpoints/2026-05-13-10-civilization-landscape-investigation-closeout.md  # closeout: final inclusion summary, eight gaps, U1-U10 proposed updates
  - raw/transpara/dark-factory/research/pageindex-role-in-transpara-stack.md  # the PageIndex source-grounded comparison (augmentation-not-replacement finding)
  - raw/transpara/dark-factory/v3.9/implementation/epics/02-technology-decision-crosswalk-v3.9.md  # DF-V3.9-EPIC-TECH-CROSSWALK v3.9.1 (status: review): the canonical per-item external-technology register
  - raw/transpara/dark-factory/v3.9/README.md  # DF-V3.9-README: v3.9 = accepted v3.8 baseline + the 2026-05-13 investigation
  - raw/transpara/dark-factory/v3.9/01-unified-architecture-decisions-v3.9.md  # Decisions 12/13/15 — external frameworks stay outside control roles
  - raw/transpara/dark-factory/Dark Factory - Motive, Goal, Approach.md  # the canonical eleven-category Decision Categories table
  - Open Brain  # PR #61 crosswalk merge record (2026-05-18); "civilization x8 refers only to this one-time investigation" (2026-06-05)
confidence:
  surveyed_set: high — the 22-item candidate list is quoted verbatim from the kickoff checkpoint, with exact repo paths.
  category_vocabulary: contested-by-layer (not contested-in-fact) — three different but reconcilable category sets exist across the sources. The seed's "selected/pattern-only/research-only/deferred/excluded" is a simplification of the canonical eleven-category Motive table and the Phase-5 six-class matrix and the crosswalk's operational variants. All three are stated below; none is silently picked.
  crosswalk_status: the crosswalk doc itself is status:review / canonical:false (front matter), even though it is the named per-item register. The accepted-canonical decision is the one-line routing rule in v3.9 Decision 15, not the crosswalk's row detail.
  no_better_kernel_claim: this is the investigation's own headline conclusion, grounded in its closeout; it is an analysis verdict, not an independently re-derived proof.
  repo_existence: the candidate repos are named as `transpara-ai/<name>` mirrors the investigation verified for access; this article does not re-verify their live contents this run.
---

# The Civilization Landscape Investigation

**The one-time survey that turned the [[dark-factory]] from a closed architecture into an architecture with explicit, defended boundaries against the rest of the agent-tooling landscape.** It ran on **2026-05-13** as a single multi-phase research session, beginning from the then-canonical v3.8 baseline and asking one disciplined question of every external tool, framework, product, and prior research artifact in reach: *is this already in the design; if not, what is its exact marginal contribution, and what would it replace, strengthen, or make possible?* (`2026-05-13-civilization-landscape-investigation-kickoff.md`). Its outputs were folded into the next canonical revision: **[[v3-9]] is defined as the accepted v3.8 baseline plus this investigation** (`DF-V3.9-README`: "Dark Factory v3.9 is the accepted canonical revision derived from the accepted v3.8 baseline plus the 2026-05-13 Civilization Landscape Investigation").

The investigation is also a cautionary marker in the arc. By the [[the-drift|drift diagnosis]] (2026-06-05), an Open Brain count found the word "civilization" appeared only eight times across the whole v3.9 doctrine folder — *all eight referring to this one-time investigation process, not the operative concept.* So the name is load-bearing in a way the prompt's framing should not obscure: "Civilization Landscape" was the **name of a survey**, not evidence that a living civilization governs the factory. The survey's lasting product is a register of decisions about other people's software, not a civilization.

## Why it ran, and the rule it ran under

The stated goal was broader than Dark Factory itself: "Update the Transpara-AI Civilization design by reviewing the current canonical documents for completeness and referential integrity, with a gap analysis versus the landscape of available tools and concepts" (kickoff §2). The critical bar was deliberately strict — "No superfluous inclusions. No suboptimal hacks. No duplicate capabilities unless marginal contribution is explicit. No aspirational claims accepted without code/canonical document evidence."

One operating rule governed the whole effort and is worth quoting because it shaped what counts as evidence here:

> If access to a required repo or path is missing, STOP. Ask the user to provide access. Do not guess, use upstreams, use public substitutes, use marketing pages, or fallback strategies to work around true access gaps. (kickoff §1)

With the corollary: **code and canonical repo contents are ground truth; marketing documents and external writeups may be aspirational.** This is the same source-hierarchy discipline the rest of the arc runs on, applied to a literature survey. The closeout records that the rule held — "No unresolved access gaps remain" — with named caveats (the Karpathy gist was not connector-readable so the user supplied raw content; `org-memories` had no root `MEMORY.md`; large HTML research reports were readable but truncated, so their conclusions were treated as advisory and Phase 4 used direct repo evidence instead) (`2026-05-13-10-...-closeout.md` §9).

## What was surveyed

The kickoff fixed a **22-item candidate list** (kickoff §5), each pinned to an exact repo path or URL. The list spans native Transpara systems, prior in-house research, and a wide cut of the external agent-tooling landscape:

- **Native Dark Factory / Civilization core:** the [[hive-governance]]/Civilization concept across `transpara-ai/hive`, [[event-graph|eventgraph]], [[work]], [[agent]], [[site]], and `docs/dark-factory` itself.
- **Prior in-house research:** the Brett Brewer Hive-vs-Landscape and Hive-vs-OpenClaw comparisons (in `docs/dark-factory/research/`); Brett Brewer Org Memories (`transpara-ai/org-memories`).
- **Memory / knowledge / research:** [[memory-knowledge-advisory|MemPalace]] (`transpara-ai/mempalace`); OpenBrain / OB1 (`transpara-ai/OB1`, from Nate B. Jones); the Karpathy LLM Wiki (a public gist); Karpathy Autoresearch (`transpara-ai/autoresearch`); [[pageindex|PageIndex]] (`transpara-ai/Pageindex`); MiroThinker and MiroFlow (`transpara-ai/MiroThinker`, `transpara-ai/MiroFlow`).
- **Agent execution / orchestration:** OpenClaw (`transpara-ai/openclaw`); MetaGPT (`transpara-ai/MetaGPT`); OpenManus (`transpara-ai/OpenManus`); the [[hermes-agent|Hermes Agent]] family (`transpara-ai/hermes-agent`, `hermes-agent-self-evolution`, `hermes-example-plugins`); [[multica]] (`transpara-ai/multica`); solo-orchestrator (`transpara-ai/solo-orchestrator`); [[symphony|Symphony]] (`transpara-ai/symphony`).
- **Governance / self-evolution / platform tooling:** the Microsoft [[agent-governance-toolkit|Agent Governance Toolkit]] (`transpara-ai/agent-governance-toolkit`); [[gstack|gStack]] from Garry Tan (`transpara-ai/gstack`); [[paperclip|Paperclip]] (`transpara-ai/paperclip`).

> ⚠ **Fail-legible note (repo names).** These `transpara-ai/<name>` paths are the *access targets the investigation verified*, mirrors of external projects rather than original Transpara work in most cases. The kickoff explicitly flagged case sensitivity ("Pageindex may be case-sensitive as `transpara-ai/Pageindex`") and warned "Do not silently normalize beyond these confirmed corrections." This article reproduces the paths from the kickoff; it did **not** re-open the repos this run to confirm their current contents.

### The method

The work proceeded through an eight-phase protocol (kickoff §7): Phase 0 scope agreement; Phase 1 access verification *only* (no analysis until every source was reachable); Phase 2 canonical-baseline extraction from v3.8; Phase 3 review of the six pre-existing research docs; Phase 4 repo-grounded per-candidate analysis under a uniform ~25-field template, run in four batches (**A** core architecture, **B** memory/knowledge/research, **C** agent execution/orchestration, **D** governance/self-evolution/platform tooling); Phase 5 a landscape-wide inclusion matrix; Phase 6 gap analysis versus v3.8; Phase 7 proposed canonical updates; Phase 8 checkpointing. Every phase wrote a durable checkpoint under `dark-factory/research/checkpoints/` so the investigation could survive context resets — and it did, across at least twelve checkpoint files plus a progress ledger (`...-closeout.md` §3).

## The decision categories

This is the part the seed names, and it needs care, because **three different category vocabularies exist across the sources and they are not identical.** They are reconcilable — each is a different altitude of the same decisions — but the wiki must not present one as "the" list.

**1. The Phase-5 matrix used a six-class vocabulary** (`2026-05-13-07-...-matrix.md` §4): `Core / canonical`; `Core target, incomplete`; `Optional adapter / subsystem`; `Pattern / reference only`; `Deferred runtime / benchmark`; `Rejected for controller role`.

**2. The closeout collapsed those into five buckets** for its final summary (`...-closeout.md` §6): include as core/core-target; include as optional adapter/subsystem candidate; include as pattern/reference only; defer until prerequisite controls exist; reject as controller/kernel/authority.

**3. The accepted-canonical [[v3-9]] doctrine defines an eleven-category register** (`Dark Factory - Motive, Goal, Approach.md`, "Decision Categories"): Selected native core · Selected supporting substrate · Included advisory candidate · Optional adapter candidate · Pattern-only · UX-only pattern · Deferred · Research-only · Subsumed · Excluded · Proposal-only / candidate. The Motive doc states the *reason* for this richer scheme plainly: "The category system exists to stop architectural drift" — so a reviewer can tell whether a named tool is a mandatory dependency, an optional adapter, a design inspiration, a UI analogy, a future research lead, a rejected control role, or merely a problem-space comparison.

> ⚠ **Fail-legible note (the seed's category list).** The compile request names the categories as *"selected / pattern-only / research-only / deferred / excluded."* That five-name set is a faithful **simplification** — it picks five of the canonical eleven — but it is not literally any single source's vocabulary. In particular the investigation's *closeout* did not use "research-only" or "excluded" as bucket names (it used "reject as controller/kernel/authority"); "Research-only," "Subsumed," "UX-only pattern," and "Excluded" are precise terms from the **later v3.9.1 crosswalk and the Motive doc**, not the 2026-05-13 closeout. Where this article uses those terms it is citing the crosswalk/Motive layer, and says so. On this point the sources differ in *naming*, not in *substance*: nothing was classified two contradictory ways.

The single rule that is **accepted canonical** (as opposed to the crosswalk detail, which is `status: review`) is v3.9 **Decision 15: "External Frameworks Stay Outside Control Roles"** — "All external frameworks from the Civilization Landscape Investigation remain references, optional adapters, or patterns unless a later accepted ADR changes their status. They must not become kernel, truth source, Work replacement, policy owner, release authority, certification authority, capability promoter, factory controller, or Site replacement" (`01-unified-architecture-decisions-v3.9.md`). The category labels are the bookkeeping; Decision 15 is the law.

## The headline conclusion: no better kernel exists

The closeout's core finding is blunt and is the reason the investigation strengthened rather than rewrote the architecture (`...-closeout.md` §5):

> The landscape review does not reveal a better kernel, Work owner, authority owner, runtime controller, or operator surface than the native v3.8 architecture.

From which: do not replace [[event-graph|EventGraph]]; do not replace [[work|Work]]; do not replace [[site|Site]]; do not replace [[hive-governance|Hive/governance]] authority boundaries; do not replace [[runtime-broker|RuntimeBroker]] with any external runtime/framework; do not promote any memory, RAG, wiki, or orchestration system into truth/authority roles. "The gaps are implementation and adapter-contract gaps, not reasons to abandon v3.8."

> ⚠ **Fail-legible note (verdict, not proof).** "No better kernel exists" is the investigation's *analysis conclusion* from a one-day survey of a fixed 22-item list, not an exhaustive or independently re-derived proof. It is grounded in the closeout, and the closeout itself frames it as a review judgment. Treat it as a defensible, sourced decision — not as a theorem.

## The per-item decisions

The accepted **per-item** external-technology register is the **v3.9.1 crosswalk** (`02-technology-decision-crosswalk-v3.9.md`), whose stated purpose is "to make external technology decisions visible to reviewers before implementation begins." Its per-item outcomes (cross-referenced against the Phase-5 matrix, which is the investigation's own source for them):

**Pattern-only** — learn the design idea; import no code; grant no control role:
- [[paperclip|Paperclip]] — org / budget / approval **UX pattern only**; "must remain UX-only unless an ADR changes." Phase 5: "Mine org/budget/approval UX only; **reject as control plane**."
- [[symphony|Symphony]] — trials / proof-of-work packaging pattern, "useful only when backed by EventGraph evidence, not as presentation theater"; tie to concrete trial fixtures.
- [[multica]] — managed-agent / teammate-board UX pattern; "must not imply that Agent owns authority or runtime execution"; must preserve the Agent boundary.
- [[gstack|gStack]] — software-factory workflow/skill pattern; skill ideas are `CapabilityArtifact` candidates and "must not influence work without usage logging and capability evidence."
- MetaGPT — explicit roles / SOPs / work-decomposition pattern; "EventGraph remains truth. Work remains operational task flow. Authority still requires v3.9 records."
- OpenBrain (OB1) — optional cognitive-planning pattern; advisory only, cannot replace `PlanningProposal` / `Requirement` / `AcceptanceCriterion` / EventGraph evidence.
- Karpathy LLM Wiki — wiki-layout and knowledge-freshness convention; knowledge stays advisory unless backed by EventGraph evidence.

**Deferred** — not now; requires a later ADR/epic packet, license & supply-chain review, and a passed conformance gate:
- [[hermes-agent|Hermes]] — "governed optimizer pattern only / deferred"; Hermes-style self-evolution "must not become a continuous production loop in v3.9"; gated to Epic 8+.
- OpenManus — future `RuntimeBroker` adapter candidate, "must not be integrated before the RuntimeBroker adapter conformance gate is selected and passed" (a ten-point conformance list: file/command/network/secret boundaries, timeout, artifact capture, nonzero-exit behavior, EventGraph receipt emission, post-run validation, replayability); Epic 6+.
- OpenClaw — deferred adapter/UX candidate; gateway/session behavior "must not own execution policy, Work flow, release authority, certification, or factory control"; Epic 6+.
- Karpathy Autoresearch — deferred optimizer pattern; autoresearch-like behavior "belongs only under capability evolution with EvalDataset, BenchmarkResult, HumanReview, rollback target, and no optimizer self-promotion."
- Miro Flow — deferred pattern/reference, reopen-gated to Epic 4 or Epic 7.
- Miro Thinker — deferred research/eval reference, reopen-gated to Epic 5 or Epic 8.

**Included as advisory / optional-adapter candidate** — may be used later behind a defined adapter boundary, with evidence and quarantine rules, no implementation owner selected yet:
- Microsoft [[agent-governance-toolkit|Agent Governance Toolkit]] — `PolicyEngineAdapter` candidate (the highest-priority external reference in the matrix); before integration: license + supply-chain reviewed, policy-bundle version recorded, adapter decisions mapped to `AuthorityDecision`, execution results mapped to `ExecutionReceipt`, fail-closed behavior tested, **no LLM-dependent allow/deny decision**. Tied to Epic 3 (Hive Governance Reconciliation). This is also v3.9 Decision 13.
- [[memory-knowledge-advisory|MemPalace]] — included as an advisory memory candidate; "no truth authority"; if wired later, output becomes `MemoryReference` evidence only when it materially influences work; forbidden as truth, authority, or certification evidence.

**Research-only / subsumed** — kept as analysis input; no independent adapter or contract selected:
- Brett Brewer Org Memories analysis — "subsumed by the advisory memory/knowledge model as research-only reference." Dark Factory "does not fork, vendor, integrate, or adapt `github.com/brettdbrewer/org-memories`"; concepts may inform future memory UX, but a future adapter "requires a new ADR or epic packet before implementation."

**Excluded as a control role** — the universal rejection from Decision 15 / Phase 5 §10: no external framework may become kernel, source of truth, Work-DAG owner, RuntimeBroker replacement, policy owner, release authority, certification authority, capability promoter, or factory controller. (Note the seed's "excluded" maps here; the *Motive* doc reserves the literal "Excluded" category mainly for SaaS-template scope items like payments, production deploy, and mobile generation — a different use of the word, flagged so the two are not conflated.)

> ⚠ **Fail-legible note (crosswalk status vs. acceptance).** The crosswalk doc carries `status: review`, `canonical: false`, version 3.9.1, and a `## Review Rule` requiring any future epic to re-verify "current decision / ADR reference / integration mode / owning epic / license and supply-chain status / conformance gate / upstream-refresh strategy" before touching an item. So the *row detail above is reviewed-but-not-ratified planning*; the ratified part is the one-line Decision 15 routing rule. Open Brain (2026-05-18) records the crosswalk landing via docs PR #61 as a "planning/review artifact" with "implementation remains frozen," and the Miro/Brewer rows resolved in commit 7447b2b3 — consistent with this status.

### The PageIndex case, as a worked example

[[pageindex|PageIndex]] is the one candidate the corpus preserves a full source-grounded write-up for (`pageindex-role-in-transpara-stack.md`), and it shows the investigation's evidence discipline. The question posed was whether PageIndex *replaces or augments* the Karpathy LLM Wiki and OpenBrain ideas. The grounded finding — reached from the GitHub README and demo code after direct page-fetch was blocked, with the analyst explicitly refusing to "pretend full crawl access" — was: **augmentation, not replacement.** PageIndex is a "vectorless, reasoning-based RAG framework" that builds a hierarchical table-of-contents tree over a long document and has an LLM traverse it; it can replace the *vector-RAG subsystem* inside a knowledge stack but not the compounding-knowledge-artifact role (LLM Wiki) or the cross-tool memory substrate (OpenBrain). The recommended placement — "PageIndex **under** LLM Wiki and OpenBrain" — became the crosswalk's optional `DocumentEvidenceRetriever` framing: useful for page/section-traceable evidence, but "not memory/wiki/truth."

## The gaps, and what the investigation actually changed

The investigation's real product was not the "reject the world as a controller" conclusion (that was expected) but the **eight concrete gaps** it surfaced in the native architecture (`...-closeout.md` §7): (1) the v3.8 Tier-0 product schema not yet implemented as named contracts in EventGraph/Work; (2) an under-specified `RuntimeBroker` adapter contract for future external runtimes; (3) no concrete `GovernancePolicyEngine` implementation strategy; (4) no minimal governed memory/knowledge/evidence stack with influence-recording rules; (5) no concrete `CapabilityEvolution` optimizer/eval/activation pattern; (6) thin operator UX and proof-of-work surfaces in Site/Work; (7) no `CapabilityArtifact` governance for skills/plugins/workflow packs; (8) external product control planes needing to be kept out of kernel/controller roles.

Those gaps became the **U1-U10 proposed canonical update set** (closeout §8) that defines the v3.8 → [[v3-9]] delta: U1 Base Slice 0 repo-ownership map; U2 `PolicyEngineAdapter` optional pattern (← Agent Governance Toolkit); U3 `RuntimeBroker` adapter checklist; U4 `DocumentEvidenceRetriever` optional pattern (← PageIndex); U5 LLM Wiki layout convention (← Karpathy); U6 memory/knowledge influence-recording rule; U7 `CapabilityArtifact` rule for skills/plugins/workflow packs (← gStack, Hermes plugins); U8 `CapabilityEvolution` MVP sequencing (← Hermes self-evolution, Autoresearch); U9 expanded Site operator-UX requirements (← Paperclip, Multica, Symphony, gStack); U10 native-core packaging/reproducibility requirement. The v3-9 article confirms these as the "U1-U10 update set" folded in as implementation contracts, and that v3.9's acceptance "promoted **no external framework** to kernel, truth source, Work replacement, policy owner, release authority, certification authority, capability promoter, factory controller, or Site replacement" — the investigation's conclusion, ratified.

So the causal chain is clean and traceable: **survey 22 candidates → conclude no candidate beats the native kernel → extract eight implementation/adapter gaps → propose U1-U10 → fold U1-U10 into v3.9 as the v3.8 delta.** Each external tool that "made it into" v3.9 did so only as the *inspiration for a governed native pattern* (a checklist, an optional adapter boundary, an influence-recording rule), never as a dependency or a controller.

## How this relates to the rest of the arc

The investigation sits at the hinge between the philosophical lineage and the implementation baseline. Upstream of it are [[the-20-primitives]] and the Searles [[primitive-basis|primitive basis]] (the *motive*); downstream is [[v3-9]] (the *governed architecture*) and its [[base-slice-0|Base Slice 0]] (the *first thing actually built*). The investigation is the moment Dark Factory looked outward at MetaGPT, Hermes, OpenManus, the Agent Governance Toolkit, Paperclip and the rest, and chose — explicitly, with a documented bar — to learn patterns from all of them while importing none of them as authority. That choice is what later let the [[the-drift|drift diagnosis]] use the word "civilization" only in reference to *this survey*: the survey decided what the factory would and would not be, but it built no civilization itself. That gap is what [[the-reunification|the reunification workstream]] later set out to close.

## Sources & provenance

Compiled from the first-party Dark Factory research checkpoints and v3.9 docs:

- `dark-factory/research/checkpoints/2026-05-13-civilization-landscape-investigation-kickoff.md` — the operating rule, investigation goal and critical bar, the verbatim 22-item candidate list with exact repo paths, the eight-phase methodology, and the four analysis batches.
- `dark-factory/research/checkpoints/2026-05-13-07-phase-5-inclusion-marginal-contribution-matrix.md` — the six-class inclusion vocabulary, the full per-candidate matrix, the marginal-contribution-by-layer breakdown, and the explicit per-tool rejections.
- `dark-factory/research/checkpoints/2026-05-13-10-civilization-landscape-investigation-closeout.md` — the "no better kernel" conclusion, the five-bucket final inclusion summary, the eight concrete gaps, the U1-U10 proposed update set, and the access-status caveats.
- `dark-factory/research/pageindex-role-in-transpara-stack.md` — the PageIndex source-grounded "augmentation, not replacement" comparison against Karpathy LLM Wiki and OpenBrain/OB1.
- `dark-factory/v3.9/implementation/epics/02-technology-decision-crosswalk-v3.9.md` (`DF-V3.9-EPIC-TECH-CROSSWALK`, v3.9.1, **`status: review` / `canonical: false`**) — the canonical per-item external-technology register, the upstream-refresh policy for pattern-only adoptions, and the per-item notes quoted above.
- `dark-factory/v3.9/README.md` (`DF-V3.9-README`, accepted 2026-06-05) — the defining statement that v3.9 = accepted v3.8 baseline + the 2026-05-13 investigation, and the U1-U10 delta.
- `dark-factory/v3.9/01-unified-architecture-decisions-v3.9.md` — Decision 13 (`PolicyEngineAdapter` optional/non-canonical) and **Decision 15** (external frameworks stay outside control roles; the accepted-canonical routing rule).
- `Dark Factory - Motive, Goal, Approach.md` — the canonical eleven-category Decision Categories table and the "category system exists to stop architectural drift" rationale.

Operational corroboration from **Open Brain**: the 2026-05-18 capture recording the crosswalk landing via docs PR #61 as a reviewed planning artifact with implementation frozen (Miro/Brewer rows resolved in commit 7447b2b3); and the 2026-06-05 drift-diagnosis capture establishing that "civilization" appears eight times in the v3.9 folder, all referring to this one-time investigation rather than an operative concept.

**Conflicts stated, not resolved.** (1) *Category vocabulary*: three category sets exist — the Phase-5 six-class, the closeout five-bucket, and the canonical eleven-category Motive list — and the seed's "selected/pattern-only/research-only/deferred/excluded" is a simplification spanning them; all are named above and none is silently chosen as "the" list. (2) *Canonical status of the per-item detail*: the crosswalk is the named per-item register but is `status: review`; the ratified decision is the one-line Decision 15. (3) *The "no better kernel" verdict* is the investigation's own analysis conclusion from a fixed 22-item, one-day survey — sourced and defensible, but not an exhaustive proof, and labeled as such. `[[wikilinks]]` are forward references; several targets (e.g. `[[hermes-agent]]`, `[[symphony]]`, `[[multica]]`, `[[gstack]]`, `[[paperclip]]`, `[[pageindex]]`, `[[agent-governance-toolkit]]`) are not yet compiled.
