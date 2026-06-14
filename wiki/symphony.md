---
entity: Symphony
aliases: [symphony, transpara-ai/symphony, candidate 22]
tier: investigation
status: compiled
last_compiled: 2026-06-13
sources:
  - /Transpara/transpara-ai/data/repos/docs/dark-factory/v3.9/implementation/epics/02-technology-decision-crosswalk-v3.9.md  # v3.9.1 crosswalk, Symphony decision row + per-item note (status: review, canonical: false)
  - /Transpara/transpara-ai/data/repos/docs/dark-factory/research/checkpoints/2026-05-13-07-phase-5-inclusion-marginal-contribution-matrix.md  # Phase 5 inclusion matrix, symphony row (class C)
  - /Transpara/transpara-ai/data/repos/docs/dark-factory/research/checkpoints/2026-05-13-08-phase-6-gap-analysis-versus-v3-8.md  # Phase 6 operator-UX gap + proof-of-work packet
  - /Transpara/transpara-ai/data/repos/docs/dark-factory/research/checkpoints/2026-05-13-10-civilization-landscape-investigation-closeout.md  # closeout buckets (pattern/reference AND defer)
  - /Transpara/transpara-ai/data/repos/docs/dark-factory/research/checkpoints/2026-05-13-access-verification-complete.md  # candidate 22 = transpara-ai/symphony, access verified
  - /Transpara/transpara-ai/data/repos/docs/dark-factory/research/checkpoints/2026-05-13-civilization-landscape-investigation-kickoff.md  # candidate list entry 22
  - Open Brain  # compiler note on civilization-landscape-investigation (U9 gap chain; three-layer category vocabulary)
  - https://github.com/openai/symphony  # upstream, cited as context only — NOT mirrored or re-published (org rule: public/upstream)
confidence:
  upstream_identity: thin — upstream named openai/symphony in the task seed; no upstream README was read this run. The investigation worked from transpara-ai/symphony (the fork), and no local clone of either repo exists on this machine.
  fork_date: asserted (from task seed: forked 2026-05-05) — not independently confirmed in any source read this run; the investigation's access-verification checkpoint is dated 2026-05-13 and lists the fork as accessible by then.
  one_line_description: high — "isolated implementation runs with proof of work" is stated near-verbatim in the Phase 6 checkpoint; corroborated by the Phase 5 matrix.
  decision: high for "pattern-only" (v3.9.1 crosswalk) — but see the closeout-vs-crosswalk nuance flagged below.
  preview_maturity_and_agent_spawning: thin — listed as the "main risk" cell in the Phase 5 matrix with no supporting detail in the sources read this run.
---

# Symphony

**A forked public project the [[civilization-landscape-investigation]] surveyed and decided to keep at arm's length.** Symphony is candidate 22 — the last entry — on the 22-repo list the investigation evaluated on 2026-05-13. The task seed records it as a fork of the public **`openai/symphony`** into the `transpara-ai` org on **2026-05-05**, themed around *isolating work into autonomous implementation runs*. The investigation read the fork (`transpara-ai/symphony`) under its strict "no upstream substitution" rule, classified what it offered, and folded the useful idea into [[dark-factory]] as a **pattern only** — never as a dependency, runtime, or control plane. This article is about *that* investigation and decision; the upstream's own design is cited as context, not reproduced.

> ⚠ **Fail-legible note (scope of this article).** No README for Symphony — upstream or fork — was available locally this run, and no clone exists on this machine. Every claim below traces to the Dark Factory investigation checkpoints and the v3.9.1 crosswalk, which describe *what the investigation concluded about Symphony*, not a full account of what Symphony is. Where the sources are silent, the article says so rather than filling the gap from the upstream.

## When and why it entered the arc

Symphony appears at exactly one moment: the Civilization Landscape Investigation, a one-time survey run on **2026-05-13** to test whether any external project should displace or augment the native Dark Factory kernel. (For the survey itself — its 22 candidates, eight phases, and "no candidate beats the native kernel" verdict — see [[civilization-landscape-investigation]].)

The provenance trail, in order:

- **Kickoff candidate list** — Symphony is item 22, `transpara-ai/symphony`, in the verbatim candidate list (`...civilization-landscape-investigation-kickoff.md`, L215–216).
- **Access verification** — the investigation's immutable operating rule was *stop and ask if a source can't be accessed; never substitute the upstream, a marketing page, or memory*. The Phase 1 access checkpoint (dated 2026-05-13 10:10) records candidate 22 `transpara-ai/symphony` among the sources verified accessible, with "Sources inaccessible: None remaining" (`...access-verification-complete.md`, L230–231, L236–239). So the investigation read the **fork**, consistent with the org rule that upstream (`openai/symphony`) is public code to be cited, not mirrored.

> ⚠ **Fail-legible note (fork date).** The **2026-05-05** fork date comes from the task seed and was **not independently confirmed** in any source read this run. What the sources do establish is that by 2026-05-13 the fork existed and was readable by the investigation.

## What the investigation took Symphony to be

The sources describe Symphony in one consistent line and very little more. The Phase 6 gap analysis states it near-verbatim:

> "symphony = isolated implementation runs with proof of work."
> — `...2026-05-13-08-phase-6-gap-analysis-versus-v3-8.md`, L458

The Phase 5 inclusion matrix gives the only structured row (`...2026-05-13-07-...matrix.md`, L134):

| Field | Value (as recorded) |
|---|---|
| Batch | C |
| Inclusion class | Pattern / reference only |
| Already in v3.8? | no |
| Marginal contribution | Isolated implementation runs and proof-of-work pattern |
| Main overlap | Work → runtime → evidence path |
| Main risk | Preview maturity, agent spawning |
| Recommendation | Pattern for trials/proof-of-work only. |

That is the extent of the first-party description. The two ideas the investigation extracted are (1) **isolated implementation runs** — running a unit of work in its own sandboxed pass — and (2) a **proof-of-work** artifact bundled with the result.

> ⚠ **Fail-legible note (thin: "preview maturity, agent spawning").** The matrix names these as the "main risk" with no elaboration anywhere in the sources read this run. Treat them as the investigator's flagged concerns, not characterized facts about Symphony's codebase. Likewise, nothing read this run describes Symphony's architecture, language, license, or supply-chain posture — those are simply absent.

## The decision: pattern-only

The accepted-direction record is the v3.9.1 **technology decision crosswalk**. Symphony's row (`02-technology-decision-crosswalk-v3.9.md`, L85) and per-item note (L203–207):

- **Current decision:** pattern-only
- **Integration mode:** trials / proof-of-work pattern
- **Owning epic:** "Epic 7 issue-to-PR trials if used"
- **Fork / adapter / pattern / exclude:** pattern
- **Main risk:** "trial packaging can become theater without evidence"
- **PR #61 change required?:** "yes: tie to concrete trial fixtures"

The per-item note states the rule directly:

> "Symphony-like trial packaging is useful only when backed by EventGraph evidence, not as presentation theater."

In plain terms: Dark Factory may adopt the *idea* of an isolated implementation run that emits a proof-of-work packet, but the packet has authority only when every piece of it is recorded as evidence in the [[event-graph]]. A nicely-formatted trial summary that isn't backed by the immutable causal record is "theater" and carries no weight. This is the same structural-accountability move the whole arc makes — the artifact is not trusted because it looks complete; it is trusted because the substrate makes it verifiable.

> ⚠ **Fail-legible note (status of the decision record).** The crosswalk is `status: review`, `canonical: false` — it is reviewed planning, not ratified law. The only accepted-canonical rule that binds Symphony is the investigation's standing conclusion that *all external frameworks stay outside controller/kernel/authority roles* (the closeout's "Reject as controller/kernel/authority: All external frameworks and platforms outside native v3.8 components", L165–169). Symphony as a *pattern* is reviewed planning; Symphony *not being allowed to run or control the factory* is the firm part.

> ⚠ **Source conflict (closeout vs. crosswalk) — stated, not silently resolved.** The 2026-05-13 closeout lists `symphony` in **two** buckets at once: "Include as pattern/reference only" (L143) **and** "Defer until prerequisite controls exist" (L160). The later v3.9.1 crosswalk records a single clean decision: **pattern-only** (with deferral implied by gating it behind a future Epic 7). The two are not contradictory in substance — "use the pattern, but don't wire anything until controls exist" — but they differ in how they label it. This article follows the crosswalk's "pattern-only" as the current decision while noting the closeout's dual classification. (The compiler note in Open Brain for [[civilization-landscape-investigation]] documents this same three-layer category-vocabulary drift: the Phase 5 matrix, the closeout, and the canonical Motive doc each name the buckets differently — the sources differ in *naming*, not in *substance*.)

## Where the pattern actually landed

Symphony did not enter Dark Factory as code. Its contribution survives as one strand of a synthesized native requirement. The Phase 6 gap analysis groups Symphony with the operator-UX cluster (Paperclip, Multica, gStack, Solo Orchestrator, OpenClaw) under the concern that "if Site remains too thin, operators will use external dashboards/control planes that may become parallel truth" (L451, L464–466). From that cluster it lifts a concrete deliverable — an **EventGraph-linked proof-of-work packet** (L490–505):

> "Borrow from Symphony/gstack/paperclip, but EventGraph-link it: work item · runtime invocation · changed files · tests run · CI status · review feedback · security scan results · screenshots / walkthrough artifacts if applicable · known failures · operator decision."

Per the Open Brain compiler note for the sibling investigation article, this is gap **U9** in the investigation's U1–U10 update set — the operator-UX/proof-of-work surface drawn from Paperclip, Multica, Symphony, and gStack and folded into the v3.9 spec as a *native, evidence-backed* surface rather than an imported tool. The pattern's destination inside Dark Factory's visualization layer is the **"Proof-of-work packet view"** named in the Phase 6 recommended-Site-views list (L487) — but note this is a *planned* surface in the reviewed spec, not a shipped feature confirmed this run.

So the chain is: Symphony (and its UX-cluster siblings) demonstrated trial packaging → the investigation judged it useful → it was rewritten as a governed native packet whose authority comes from the [[event-graph]], not from the external tool. Symphony itself is referenced for *inspiration*, and that is the whole of its role.

## What it is not

Three boundaries the sources draw explicitly:

- **Not a controller, runtime, or kernel.** The closeout rejects every external framework from controller/kernel/authority roles; the crosswalk's "pattern" classification reinforces it.
- **Not a Work replacement.** Phase 7 of the investigation lists "Replacing Work with Paperclip, Multica, Symphony, MetaGPT, or OpenClaw" among the things *not* to do (`...phase-7-proposed-canonical-updates.md`, L815). Symphony's "isolated implementation runs" overlap the native Work → runtime → evidence path (Phase 5 "main overlap"), but Work remains the owner.
- **Not re-published here.** Per the org rule, the upstream `openai/symphony` is public/upstream code; this wiki cites it as context only and does not mirror its documentation. The subject is Transpara's investigation and decision.

## Related

- [[civilization-landscape-investigation]] — the survey Symphony was candidate 22 of; the source of every claim here.
- [[dark-factory]] — the system whose v3.9 crosswalk records the pattern-only decision and into which the proof-of-work pattern (U9) was folded.
- [[event-graph]] — the substrate that turns a "proof-of-work packet" from theater into evidence; the condition the crosswalk attaches to any Symphony-like trial packaging.
- [[paperclip]] — a sibling candidate in the same operator-UX cluster, decided UX-only; shares the U9 gap lineage with Symphony.

## Sources & provenance

First-party, all read this run:

- **`/Transpara/transpara-ai/data/repos/docs/dark-factory/v3.9/implementation/epics/02-technology-decision-crosswalk-v3.9.md`** — the Symphony decision row (L85) and per-item note (L203–207): pattern-only; trials/proof-of-work; "useful only when backed by EventGraph evidence, not as presentation theater"; risk "trial packaging can become theater"; "tie to concrete trial fixtures." Document is `status: review`, `canonical: false`.
- **`...research/checkpoints/2026-05-13-07-phase-5-inclusion-marginal-contribution-matrix.md`** (L134) — the structured `symphony` row: Batch C, "Pattern / reference only," contribution "Isolated implementation runs and proof-of-work pattern," overlap "Work → runtime → evidence path," risk "Preview maturity, agent spawning."
- **`...research/checkpoints/2026-05-13-08-phase-6-gap-analysis-versus-v3-8.md`** (L458, L451–505) — "symphony = isolated implementation runs with proof of work"; the operator-UX/parallel-truth concern; the EventGraph-linked proof-of-work packet field list; "Proof-of-work packet view."
- **`...research/checkpoints/2026-05-13-10-civilization-landscape-investigation-closeout.md`** (L143, L160, L165–169) — `symphony` listed under *both* "Include as pattern/reference only" and "Defer until prerequisite controls exist"; the blanket "Reject as controller/kernel/authority" rule.
- **`...research/checkpoints/2026-05-13-access-verification-complete.md`** (L230–231, L236–239) — candidate 22 `transpara-ai/symphony`, access verified; "Sources inaccessible: None remaining"; the no-upstream-substitution operating rule.
- **`...research/checkpoints/2026-05-13-civilization-landscape-investigation-kickoff.md`** (L215–216) — candidate-list entry 22, `transpara-ai/symphony`.
- **Open Brain** — compiler note on `civilization-landscape-investigation.md` (2026-06-13): the U9 gap chain (U9 ← Paperclip/Multica/Symphony/gStack) and the three-layer category-vocabulary drift across Phase 5 matrix / closeout / Motive doc.

Context only, not re-published: **`https://github.com/openai/symphony`** — the upstream the fork derives from, per the task seed. Per org policy (upstream is public OSS), it is cited as origin, never mirrored.

**Open conflicts / thin spots, stated:** (1) closeout dual-classifies Symphony (pattern-only **and** deferred) while the crosswalk records a single "pattern-only" — both stated above, crosswalk followed as current. (2) Upstream identity (`openai/symphony`) and fork date (2026-05-05) come from the task seed and were not confirmed against any source read this run. (3) Symphony's "preview maturity / agent spawning" risk, architecture, language, and license are not characterized in any source read this run — marked thin. `[[wikilinks]]` are forward references; some targets (e.g. [[civilization-landscape-investigation]], [[paperclip]]) are already compiled, others are not.
