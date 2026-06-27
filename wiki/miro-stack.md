---
entity: The Miro Stack
aliases:
  - Miro Stack
  - MiroMind stack
  - MiroFlow
  - MiroThinker
  - MiroEval
  - MiroRL
  - MiroMind-M1
  - the deep-research agent fork
tier: investigation
status: compiled
last_compiled: 2026-06-13
sources:
  - /Transpara/transpara-ai/repos/docs/dark-factory/v3.9/implementation/epics/02-technology-decision-crosswalk-v3.9.md  # v3.9.1 crosswalk — rows for "Miro Flow" (L87) and "Miro Thinker" (L88) + per-item notes (L215-258); NO row for MiroEval / MiroRL / MiroMind-M1 (status: review, canonical: false)
  - raw/transpara/dark-factory/v3.9/01-unified-architecture-decisions-v3.9.md  # Decision 15: external frameworks stay outside control roles
  - /Transpara/transpara-ai/repos/docs/dark-factory/research/checkpoints/2026-05-13-04-phase-4-batch-b-memory-knowledge-research.md  # Phase 4 Batch B — MiroThinker (§10, L812-928) and MiroFlow (§11, L931-1049) README-grounded deep-dives; Batch B summary table (L1062-1063)
  - /Transpara/transpara-ai/repos/docs/dark-factory/research/checkpoints/2026-05-13-07-phase-5-inclusion-marginal-contribution-matrix.md  # Phase 5 matrix — MiroThinker (L124) + MiroFlow (L125) rows, class "Deferred runtime / benchmark"; boundary line (L306)
  - /Transpara/transpara-ai/repos/docs/dark-factory/research/checkpoints/2026-05-13-10-civilization-landscape-investigation-closeout.md  # closeout — MiroThinker/MiroFlow dual-listed under "pattern/reference only" (L146-147) AND "defer until prerequisite controls exist" (L156-157)
  - /Transpara/transpara-ai/repos/docs/dark-factory/research/checkpoints/2026-05-13-08-phase-6-gap-analysis-versus-v3-8.md  # Phase 6 — "MiroThinker/MiroFlow benchmarks" as a borrowed-pattern source (L831)
  - /Transpara/transpara-ai/repos/docs/dark-factory/research/checkpoints/2026-05-13-09-phase-7-proposed-canonical-updates.md  # Phase 7 — "do not" list: "Starting MiroThinker/MiroFlow research agents before runtime/network policy exists" (L822)
  - /Transpara/transpara-ai/repos/docs/dark-factory/research/checkpoints/2026-05-13-11-v3.9-adversarial-review.md  # adversarial review — MiroThinker/MiroFlow "not directly named in v3.9 main docs; covered by Decision 15 catch-all" (L179, L212)
  - /Transpara/transpara-ai/repos/docs/dark-factory/research/checkpoints/2026-05-13-civilization-landscape-investigation-kickoff.md  # kickoff candidate list — MiroThinker = candidate 18, MiroFlow = candidate 19 (L203-207); ONLY these two are candidates
  - "GitHub API: repos/transpara-ai/{MiroFlow,MiroThinker,MiroEval,MiroRL,MiroMind-M1} (fork metadata, 2026-06-13 live)"  # isFork=true, parent=MiroMindAI/*, all createdAt 2026-05-12, all license apache-2.0
  - Open Brain  # 2026-06 capture: "5/12 MiroEval/MiroFlow/MiroMind-M1/MiroRL <- MiroMindAI"; 2026-05 captures: commit 7447b2b3 resolved the Miro crosswalk rows; Miro absent from v3.9 core specs
  - "Upstream context only (not re-published): github.com/MiroMindAI/{MiroFlow,MiroThinker,MiroEval,MiroRL,MiroMind-M1} — fork parents, fetched 2026-06-13"
confidence:
  fork_set_and_date: high — five forks confirmed live via GitHub fork metadata, all parent=MiroMindAI/*, all createdAt 2026-05-12, all apache-2.0; corroborated by an Open Brain capture (which, however, omits MiroThinker from its 5/12 list — see fail-legible note).
  coverage_is_partial: high — this is the headline finding. The investigation surveyed only TWO of the five (MiroThinker = candidate 18, MiroFlow = candidate 19). MiroEval, MiroRL, and MiroMind-M1 were never candidates, never analysed, and have no crosswalk row. Everything about those three is thin / external-metadata only.
  decision_for_the_two_surveyed: high — "Miro Flow" (deferred pattern/reference) and "Miro Thinker" (deferred research/eval reference) each have an explicit v3.9.1 crosswalk row; but the crosswalk is status:review / canonical:false (the ratified rule is Decision 15).
  closeout_vs_crosswalk: contested-by-layer — the closeout dual-lists both as "pattern/reference only" AND "defer until controls exist"; the crosswalk collapses each to a single "deferred" decision. Stated, not silently picked.
  repo_internals: thin — even for the two surveyed, "Primary evidence inspected: README.md"; no code was read by the investigation or this run.
  stack_as_a_unit: asserted by the task framing — the five repos are ONE upstream research-agent project (MiroFlow README: "official implementation of the MiroMind Research Agent Project"), but Dark Factory never decided on them as a stack; it decided on two members individually.
---

# The Miro Stack

**A five-repo upstream deep-research-agent project that Transpara forked as a unit, but that the [[civilization-landscape-investigation]] only evaluated two members of.** The Miro stack is the MiroMind Research Agent Project: an open-source family of deep-research / search agents (**MiroThinker**), the agent framework that runs them (**MiroFlow**), a reinforcement-learning trainer (**MiroRL**), a deep-research evaluation benchmark (**MiroEval**), and a math-reasoning model series (**MiroMind-M1**). Transpara forked all five from the public `MiroMindAI` org into `transpara-ai` on **2026-05-12** (confirmed live via GitHub fork metadata; all five `isFork=true`, `parent=MiroMindAI/*`, all Apache-2.0). The theme across them is the same one the prompt names: deep-research agents + reinforcement learning + an evaluation benchmark.

The forks landed one day before the [[dark-factory]] landscape investigation ran (**2026-05-13**), so they could be read as ground-truth source under the survey's hard rule — *code and canonical repo contents are truth; never substitute the upstream, a marketing page, or memory.* But here the stack-vs-member distinction is load-bearing and is the central fail-legible fact of this article: **the investigation surveyed only two of the five.** MiroThinker was candidate 18 and MiroFlow was candidate 19 on the 22-repo list; MiroEval, MiroRL, and MiroMind-M1 **were never candidates, never analysed, and have no decision row anywhere.**

This article is about *our investigation and our decision*, not a mirror of MiroMind's documentation. The upstream is public OSS; it is cited only as context (origin, license, one-line description), never re-published.

## Fail-legible up front: the crosswalk covers two of five, by individual member

The compile instruction was to find "this project's decision row" in the v3.9.1 technology-decision crosswalk. There is **no single row for "the Miro stack."** The crosswalk treats the Miro work as **two separate items**, and only two:

- **Miro Flow** — decision: *deferred pattern/reference*; integration mode "workflow and flow-design reference only"; owning epic "Epic 4 operator workflow or Epic 7 issue-to-PR trials if explicitly reopened"; main risk "flow orchestration patterns could imply hidden controller behavior"; PR #61 change required? "no: resolved as deferred pattern/reference" (`02-technology-decision-crosswalk-v3.9.md`, L87 + per-item note L215-236).
- **Miro Thinker** — decision: *deferred research/eval reference*; integration mode "reasoning/planning/eval reference only"; owning epic "Epic 5 bounded LLM proposal trial or Epic 8 capability monitoring if explicitly reopened"; main risk "model-behavior ideas could bypass v3.9 evidence and review gates"; PR #61 change required? "no: resolved as deferred research/eval reference" (L88 + per-item note L238-258).

> ⚠ **Fail-legible note (three of five have NO row, and were never surveyed).** **MiroEval, MiroRL, and MiroMind-M1 do not appear anywhere in the investigation** — not in the kickoff candidate list (which jumps from MiroThinker = 18 to MiroFlow = 19 to multica = 20), not in any Phase 4/5/6/7 checkpoint, and not in the crosswalk. A literal search of the canonical crosswalk for "MiroEval", "MiroRL", and "MiroMind" returns nothing. They were forked into `transpara-ai` (live metadata confirms 2026-05-12, Apache-2.0) but never evaluated. **Everything this article says about those three is from GitHub fork metadata only — their decision status is genuinely unknown, and is marked thin throughout.** The most that can be said is that they would fall under the catch-all of v3.9 **Decision 15** (every external framework "must not become kernel, truth source, Work replacement, policy owner, release authority, certification authority, capability promoter, factory controller, or Site replacement") simply by being external frameworks — but no member-specific decision exists for them.

> ⚠ **Fail-legible note (crosswalk status vs. acceptance).** The crosswalk carries `status: review`, `canonical: false`. The accepted-canonical rule that binds *all* the Miro repos is the one-line v3.9 **Decision 15** routing rule, not the crosswalk's row detail. The adversarial-review checkpoint says exactly this: "MiroThinker / MiroFlow … not directly named in v3.9 main docs; covered by 01 Decision 15 catch-all" (`...11-v3.9-adversarial-review.md`, L179). Open Brain (2026-05) corroborates: the Miro rows were added to the crosswalk by commit `7447b2b3` ("resolve Miro and Org Memories decisions"), and "neither Miro nor Brewer appears in v3.9 core specs as runtime/controller/adapter — only in research checkpoints and now the crosswalk's deferred/subsumed entries."

## What the five repos are (live metadata + README, for the two surveyed)

The stack is one upstream project. MiroFlow's README, as the investigation recorded it, calls itself "the official implementation of the MiroMind Research Agent Project, with components including MiroFlow framework, MiroThinker agent, and MiroVerse training data" (`...04-phase-4-batch-b...`, L951). The five forked members, with their live GitHub descriptions (fetched 2026-06-13, context-only):

| Repo (`transpara-ai/…`) | Upstream parent | What it is (live description) | License | Surveyed? |
|---|---|---|---|---|
| **MiroFlow** | `MiroMindAI/MiroFlow` | "Top-1 on 5+ benchmarks \| Web UI \| Supports MiroThinker, Claude, Kimi, OpenAI" — the research-agent framework | Apache-2.0 | **Yes (candidate 19)** |
| **MiroThinker** | `MiroMindAI/MiroThinker` | "a deep research agent optimized for complex research and prediction tasks … MiroThinker-1.7 achieves 74.0 / 75.3 on BrowseComp / BrowseComp-Zh" | Apache-2.0 | **Yes (candidate 18)** |
| **MiroEval** | `MiroMindAI/MiroEval` | "a benchmark and evaluation framework for deep research agents — 100 tasks (70 text, 30 multimodal) … 13 systems evaluated" | Apache-2.0 | **No** |
| **MiroRL** | `MiroMindAI/MiroRL` | "an MCP-first reinforcement learning framework for deep research agent" | Apache-2.0 | **No** |
| **MiroMind-M1** | `MiroMindAI/MiroMind-M1` | "a fully open-source series of reasoning language models built on Qwen-2.5, focused on advancing mathematical reasoning" | Apache-2.0 | **No** |

> ⚠ **Fail-legible note (the "RL + eval benchmark" theme is mostly un-investigated).** The task theme names "RL + eval benchmark." The RL component is **MiroRL** and the eval benchmark is **MiroEval** — and *both are among the three the investigation never opened.* So the parts of the theme that Dark Factory actually reasoned about are the **deep-research agent** (MiroThinker) and the **agent framework** (MiroFlow); the RL trainer and the benchmark were forked but not assessed. The benchmark *names* the investigation did engage with (GAIA, BrowseComp, HLE, FutureX, XBench, Frames) came from the MiroThinker/MiroFlow READMEs as performance claims, not from MiroEval.

### MiroThinker, as the investigation recorded it (README-only)

Batch B (`...04-phase-4-batch-b...`, §10, L812-928) describes MiroThinker as "a family of open-source deep research/search agents optimized for research, prediction, long-context reasoning, and tool-assisted reasoning … supporting 256K context and hundreds of tool calls per task, with model releases at 30B/235B." Its emphasis: "interactive scaling, long-chain tasks, tool-assisted reasoning, benchmark performance on BrowseComp, GAIA, HLE, FutureX, XBench, Frames, etc., trace collection, benchmark evaluation."

What the investigation said it **is not**: "not a memory system, not a wiki, not EventGraph, not Work, not governance, and not a controlled execution envelope." Its unique marginal contribution: "research-agent benchmark targets, trace-collection ideas, and long-horizon tool-use performance reference points."

### MiroFlow, as the investigation recorded it (README-only)

Batch B (§11, L931-1049) describes MiroFlow as "an open-source research agent framework for multi-step internet research and future event prediction … high concurrency and reliability, hierarchical sub-agent orchestration, benchmark performance on FutureX, GAIA, HLE, BrowseComp, xBench-DeepSearch … OpenRouter start path." Supported tools include "audio transcription, Python, file reading, reasoning, Google Search, VQA, E2B."

What it **is not**: "not EventGraph truth, not Work DAG, not v3.8 governance, not a memory substrate, and not safe as a factory controller." Its marginal contribution: "a reference for research-agent benchmark discipline and tool orchestration under realistic web/research tasks."

## The decision: deferred (for the two surveyed)

For the two members that were actually evaluated, the verdict was consistent across every layer of the investigation: **defer; use only as a reference, not as runtime.**

The Phase 5 inclusion matrix (`...07-phase-5...`, L124-125) is the structured source:

| Member | Batch | Inclusion class | In v3.8? | Marginal contribution | Main risk | Recommendation |
|---|---|---|---|---|---|---|
| MiroThinker | B | Deferred runtime / benchmark | no | Research-agent model/eval benchmark reference | Benchmark mismatch, runtime risk | "Use as benchmark/model reference only; defer runtime." |
| MiroFlow | B | Deferred runtime / benchmark | no | Research-agent framework and benchmark/trace patterns | Web/tool orchestration outside RuntimeEnvelope | "Use as benchmark/research-agent reference only; defer runtime." |

The recommendations from the Batch B deep-dives say the same in prose: MiroThinker — "Defer for implementation. Include as benchmark/comparison only until v3.8 RuntimeBroker, eval, and capability governance are implemented"; MiroFlow — "Defer as runtime. Include as benchmark/comparison and pattern source for future research automation after RuntimeBroker/network policy and eval governance exist." Neither required an ADR or spec change at the time ("None now").

The v3.9.1 crosswalk then ratified the *direction* with the wording quoted above (Miro Flow = deferred pattern/reference; Miro Thinker = deferred research/eval reference), each fenced behind a named future epic and the standing preservation rules:

- **Miro Flow** "must not become a controller … must not replace EventGraph truth … must not execute work … must not approve protected actions"; any adopted pattern must preserve "v3.9 AuthorityRequest, AuthorityDecision, ExecutionReceipt, proof-of-work packet, and audit evidence boundaries" (crosswalk per-item note).
- **Miro Thinker** "must not become planner of record … must not replace PlanningProposal, Requirement, AcceptanceCriterion, or Task evidence … must not bypass MemoryReference, KnowledgeReference, or CapabilityArtifact influence logging … must not be used as a benchmark gate without EvalDataset, BenchmarkResult, HumanReview, and rollback evidence where capability evolution is involved" (crosswalk per-item note).

> ⚠ **Source conflict (closeout vs. crosswalk) — stated, not silently resolved.** The 2026-05-13 closeout lists **both** MiroThinker and MiroFlow in **two** buckets at once: "Include as pattern/reference only" (L146-147) **and** "Defer until prerequisite controls exist" (L156-157). The later v3.9.1 crosswalk records a single clean decision per member ("deferred …"). The two are not contradictory in substance — *use the reference, but wire nothing until runtime/network/eval controls exist* — but they differ in labelling. This is the same dual-classification the closeout applied to [[symphony|Symphony]], [[paperclip|Paperclip]], and the rest of the deferred cluster; the sibling [[civilization-landscape-investigation]] article documents this three-layer category-vocabulary drift in full. This article follows the crosswalk's "deferred" as the current decision while recording the closeout's dual listing.

## Why deferred, and not adopted

The reason is the cleanest statement of the whole investigation's containment doctrine, and it is captured in one line from the Phase 5 boundaries: **"MiroThinker/MiroFlow must not become runtime before Base Slice controls"** (`...07-phase-5...`, L306). The Miro agents are network-touching, tool-calling, hierarchically-orchestrating research agents — exactly the shape of thing the [[dark-factory]] architecture insists must run *inside* a governed [[runtime-broker|RuntimeBroker]] envelope with network policy, cost controls, traceability, and authority, none of which existed yet. The recorded risks make the mismatch explicit:

- **MiroThinker:** "Long tool-call agents conflict with Base Slice 0 ordering"; "Model/runtime use requires sandboxing, cost controls, traceability, and authority"; "Benchmark claims may not map to Dark Factory workloads."
- **MiroFlow:** "Web research tools can violate v3.8 network policy if not wrapped"; "Hierarchical sub-agent orchestration could bypass Work DAG"; "Benchmark success does not prove audit/certification suitability"; "External tools and OpenRouter introduce dependency/cost/security concerns."

So the verdict was not "this is bad" but "this is premature." A deep-research agent that browses the open web and spawns sub-agents is the canonical example of execution that must be confined before it is allowed — and the prerequisite confinement (RuntimeBroker, network policy, eval governance) was a *gap* the investigation was simultaneously surfacing, not a control it could lean on. Phase 7's "do not" list states the deferral as a rule: **"Starting MiroThinker/MiroFlow research agents before runtime/network policy exists"** is among the things explicitly *not* to do (`...09-phase-7...`, L822).

## Where the (small) borrowed surface is allowed to land

Unlike the operator-UX cluster — where [[symphony|Symphony]], [[paperclip|Paperclip]], [[multica]], and [[gstack|gStack]] fed a concrete native deliverable (the U9 EventGraph-linked proof-of-work packet) — the Miro repos contributed **no native contract or update** to v3.9. Their role is the thinnest of any surveyed candidate: a **benchmark and trace-discipline reference**. Phase 6 lists "MiroThinker/MiroFlow benchmarks" only as one item in a menu of borrowable patterns (`...08-phase-6...`, L831), and the crosswalk gates any actual use behind a future Epic 5 / Epic 8 (Miro Thinker) or Epic 4 / Epic 7 (Miro Flow) reopen that must first record the upstream version reviewed, the exact behaviour considered, and how it is bounded by v3.9 evidence and authority rules.

In other words: if Dark Factory ever wants to measure a research agent, the Miro benchmark suites (and the *idea* of trace collection and reproducible eval) are a reference point — but only after the eval-governance machinery (`EvalDataset`, `BenchmarkResult`, `HumanReview`, rollback targets) exists to make a benchmark result evidence rather than a marketing number. As of this compile, no epic has reopened any Miro member; under the crosswalk freeze policy, the decisions stand frozen at the v3.9 reference point.

## What it is not

- **Not a runtime, controller, or kernel.** The deferral is precisely about keeping these network-touching, sub-agent-spawning research agents out of execution until a governed envelope exists. Decision 15's catch-all covers all five members regardless of whether they have a row.
- **Not a planner or truth/authority surface.** Miro Thinker "must not become planner of record" and must not replace PlanningProposal/Requirement/AcceptanceCriterion/Task evidence; neither agent may become [[event-graph|EventGraph]] truth.
- **Not a benchmark gate by itself.** Benchmark numbers from the Miro READMEs (BrowseComp, GAIA, HLE, FutureX, etc.) are reference performance claims; using any of them as a promotion gate requires the full eval-governance evidence chain.
- **Not (for three of five) decided at all.** MiroEval, MiroRL, and MiroMind-M1 have no investigation finding. They are forks on disk, nothing more, in the decision record.
- **Not re-published here.** Per org rule, the `MiroMindAI/*` upstreams are public/upstream code; this wiki cites them as origin only and mirrors none of their documentation.

## Fail-legible notes

- **Coverage is the headline.** The prompt frames "The Miro Stack" as one forked project across five upstreams; the *decision record* only addresses two members. Any reader treating this as "Dark Factory evaluated the Miro stack" should read it as "Dark Factory evaluated MiroThinker and MiroFlow, and forked but did not evaluate MiroEval, MiroRL, and MiroMind-M1."
- **Open Brain capture is incomplete on the fork set — and live metadata corrects it.** The 2026-06 Open Brain capture lists the 2026-05-12 fan-out as "MiroEval/MiroFlow/MiroMind-M1/MiroRL <- MiroMindAI" — **omitting MiroThinker.** Live GitHub fork metadata fetched this run shows MiroThinker *was* also forked on 2026-05-12 (createdAt 15:51:35Z, parent `MiroMindAI/MiroThinker`). The capture is a thought, not a system of record; the live fork metadata is authoritative and resolves the discrepancy. All five were forked 2026-05-12 within a ~14-minute window (15:41–15:55Z).
- **Repo internals are thin even for the two surveyed.** Both Batch B deep-dives state "Primary evidence inspected: README.md." No code, training scripts, benchmark harnesses, or model weights were read by the investigation, and none were read this run. Every internal claim is README- or live-description-grounded, not code-verified.
- **License open item, closed by live metadata.** Batch B recorded MiroFlow as "Apache License 2.0" but MiroThinker as "License not fully assessed … exact licensing of weights/datasets must be checked before use." This run's live fork metadata shows **all five repos are Apache-2.0** at the repo level — closing the investigation's open item for the code (the caveat about *model-weight/dataset* licensing on HuggingFace is separate and still un-checked here).
- **"Benchmark mismatch / runtime risk" is a risk assessment, not an observed failure.** The objections are the investigation's forward-looking reasons to defer, not records of anything the Miro agents did wrong inside Dark Factory (they were never run inside it).
- **The "stack" is the upstream's unit, not ours.** MiroFlow/MiroThinker/MiroEval/MiroRL/MiroMind-M1 are one coherent upstream project (MiroMind Research Agent Project). Dark Factory never made a stack-level decision; it made two member-level decisions and left three members untouched. The "stack" framing is the task's and the upstream's, faithfully reported, not a Dark Factory decision unit.

## Where it sits relative to the rest of the survey

The Miro repos sit in the **memory/knowledge/research cluster** (Batch B) of the [[civilization-landscape-investigation]], alongside [[mempalace|MemPalace]], [[ob1|OB1]], `org-memories`, `PageIndex`, the Karpathy LLM Wiki, and `autoresearch`. Within the survey they are the clearest case of *defer-because-premature-execution*: where MemPalace and the Karpathy wiki were folded in as advisory patterns and PageIndex became an optional document-evidence adapter, the Miro agents were the one Batch B entry whose core nature — autonomous, web-touching, sub-agent-spawning research execution — directly collided with the not-yet-built [[runtime-broker|RuntimeBroker]] and network policy. They are also the survey's sharpest illustration of the coverage limit itself: a five-repo fork of which the investigation deliberately scoped only the two members (the agent and its framework) that mapped onto a Dark Factory question, and left the RL trainer, the benchmark, and the math model unexamined. That choice is the same hinge as the rest of the investigation — [[dark-factory]] looked outward, took the narrow reference it could use, and imported none of it as authority — applied here with an unusually visible boundary on *what was even looked at*.

## Sources & provenance

First-party Dark Factory investigation records and v3.9 docs (all read this run):

- **`/Transpara/transpara-ai/repos/docs/dark-factory/v3.9/implementation/epics/02-technology-decision-crosswalk-v3.9.md`** (`DF-V3.9-EPIC-TECH-CROSSWALK`, v3.9.1, **`status: review` / `canonical: false`**) — the two rows that exist: **Miro Flow** (L87, "deferred pattern/reference") and **Miro Thinker** (L88, "deferred research/eval reference"), with per-item notes (L215-258) and the preservation/reopen rules. Cited equally for what it **lacks**: no row for MiroEval, MiroRL, or MiroMind-M1 (literal search returns nothing).
- **`…/research/checkpoints/2026-05-13-04-phase-4-batch-b-memory-knowledge-research.md`** — the README-grounded deep-dives for MiroThinker (§10, L812-928) and MiroFlow (§11, L931-1049): what each is/is not, primitives, risks, license notes, and the "defer; benchmark/comparison only" recommendations; Batch B summary table (L1062-1063). Both state "Primary evidence inspected: README.md."
- **`…/research/checkpoints/2026-05-13-07-phase-5-inclusion-marginal-contribution-matrix.md`** — the structured rows for MiroThinker (L124) and MiroFlow (L125), class "Deferred runtime / benchmark"; the boundary "MiroThinker/MiroFlow must not become runtime before Base Slice controls" (L306).
- **`…/research/checkpoints/2026-05-13-10-civilization-landscape-investigation-closeout.md`** — both members listed under **two** buckets: "pattern/reference only" (L146-147) and "defer until prerequisite controls exist" (L156-157); the blanket "reject as controller/kernel/authority" rule.
- **`…/research/checkpoints/2026-05-13-08-phase-6-gap-analysis-versus-v3-8.md`** — "MiroThinker/MiroFlow benchmarks" as one borrowable-pattern source (L831).
- **`…/research/checkpoints/2026-05-13-09-phase-7-proposed-canonical-updates.md`** — the "do not" list entry "Starting MiroThinker/MiroFlow research agents before runtime/network policy exists" (L822).
- **`…/research/checkpoints/2026-05-13-11-v3.9-adversarial-review.md`** — MiroThinker/MiroFlow "not directly named in v3.9 main docs; covered by 01 Decision 15 catch-all" (L179, L212).
- **`…/research/checkpoints/2026-05-13-civilization-landscape-investigation-kickoff.md`** — the candidate list establishing MiroThinker = candidate 18 and MiroFlow = candidate 19 (L203-207), and that no other Miro repo is a candidate.

Live fork metadata (GitHub API, fetched 2026-06-13) — the authoritative source for the five-repo fork set, the 2026-05-12 date, and Apache-2.0 licensing:

- `repos/transpara-ai/MiroFlow` — `isFork=true`, `parent=MiroMindAI/MiroFlow`, `createdAt=2026-05-12T15:41:01Z`, `license=apache-2.0`.
- `repos/transpara-ai/MiroRL` — `parent=MiroMindAI/MiroRL`, `createdAt=2026-05-12T15:48:04Z`, `license=apache-2.0`.
- `repos/transpara-ai/MiroThinker` — `parent=MiroMindAI/MiroThinker`, `createdAt=2026-05-12T15:51:35Z`, `license=apache-2.0`.
- `repos/transpara-ai/MiroMind-M1` — `parent=MiroMindAI/MiroMind-M1`, `createdAt=2026-05-12T15:53:22Z`, `license=apache-2.0`.
- `repos/transpara-ai/MiroEval` — `parent=MiroMindAI/MiroEval`, `createdAt=2026-05-12T15:55:39Z`, `license=apache-2.0`.

Operational corroboration from **Open Brain**: the 2026-06 capture recording the 2026-05-12 fan-out as "MiroEval/MiroFlow/MiroMind-M1/MiroRL <- MiroMindAI" (incomplete — omits MiroThinker, corrected here by live metadata); the 2026-05 captures recording that commit `7447b2b3` ("resolve Miro and Org Memories decisions") added the two Miro crosswalk rows, and that "neither Miro nor Brewer appears in v3.9 core specs as runtime/controller/adapter — only in research checkpoints and now the crosswalk's deferred/subsumed entries."

Context only, not re-published: **`github.com/MiroMindAI/MiroFlow`, `…/MiroThinker`, `…/MiroEval`, `…/MiroRL`, `…/MiroMind-M1`** — the upstream fork parents. Per org policy (upstream is public OSS), they are cited as origin and license source only, never mirrored.

**Conflicts / thin spots, stated not resolved.** (1) *Partial coverage* — only MiroThinker and MiroFlow were surveyed and have crosswalk rows; MiroEval, MiroRL, and MiroMind-M1 were forked but never evaluated and have no decision, so the RL and eval-benchmark half of the stack's theme is essentially un-investigated and marked thin. (2) *Closeout vs. crosswalk* — the closeout dual-classifies both surveyed members ("pattern/reference only" AND "deferred"); the crosswalk records a single "deferred" each; both stated, crosswalk followed as current. (3) *Open Brain fork-set capture omits MiroThinker* — resolved by live GitHub metadata, which confirms all five forked 2026-05-12. (4) *Crosswalk is `status: review`* — the ratified rule is Decision 15's catch-all; the per-item rows are reviewed-but-not-ratified planning. (5) *Repo internals are README-only* even for the two surveyed; no code read. `[[civilization-landscape-investigation]]` and `[[dark-factory]]` resolve to compiled articles, as do `[[event-graph]]`, `[[runtime-broker]]`, `[[symphony]]`, `[[paperclip]]`, `[[multica]]`, `[[mempalace]]`, and `[[ob1]]`; `[[gstack]]` is a forward reference not yet compiled.
