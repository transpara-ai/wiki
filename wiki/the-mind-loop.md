---
entity: The Mind Loop
aliases: [mind loop, mind-loop, the mind loop, bounded-runtime, the autonomous mind loop, mind-zero-five mind loop]
tier: architecture
status: compiled
last_compiled: 2026-06-13
sources:
  - raw/searles/all-posts-1.md  # "The Architecture of Accountable AI", 2026-02-28 [Searles-P3] — §"The Mind Loop" (L598-631) and §"Self-Improvement With a Circuit Breaker" (L634-661); primary
  - raw/searles/all-posts-1.md  # same post, §"Crash Recovery as Ethics" (L665-691) and §"What The Code Proves" (L695-707) — context for loop recovery and the proof claims
  - "Dark Factory - Motive, Goal, Approach.md"  # first-party: mind loop as "prior implementation pattern… not imported as a dependency" (L382); "agent action becomes bounded runtime invocation" (L128); "self-improvement becomes EvolutionOrder, eval, human review, activation policy, and rollback" (L130)
  - Open Brain  # civilization-wiki seed scan (2026-06-13); dark-factory slice-1 v14 self-renewal-refusal (2026-06-11) corroborating "cannot extend its own epoch / waits rather than works around" as a live implementation pattern
durable_urls:
  - https://mattsearles2.substack.com/p/the-architecture-of-accountable-ai  # [Searles-P3]
  - https://github.com/mattxo/mind-zero-five                                 # [Searles-MindZeroRepo]
confidence:
  code_exists_and_runs: asserted by the author ("running right now", "the code runs"). Compiled from the post's prose and the Go excerpts quoted inside it, not from a checkout of the repository. Treat the design as well-sourced and the operational claim as the author's testimony.
  loop_mechanics_completeness: thin — the post deliberately quotes only the *core* ("the interesting part isn't the loop itself"), not the full control flow. The phase list (claim → plan → implement → review → finish) and the event names are sourced to the prose and the specific excerpts; the complete loop implementation was not read this run.
  not_mutually_exclusive_claim: demonstrated for this system's design, by construction — not a general theorem about all self-improving AI. Flagged inline.
  bounded_runtime_relationship: the dark-factory phrase "agent action becomes bounded runtime invocation" (L128) is the first-party *successor* concept, not a name used in the Searles post. The two are related-not-identical; stated, not silently merged.
---

# The mind loop

**The autonomous agent that lives on top of the accountability infrastructure.** The mind loop is the part of **mind-zero-five** that actually does work: it claims tasks, plans, implements, reviews, finishes, and — when idle — improves itself. It first appears as working code in the third Searles post, *"The Architecture of Accountable AI"* (**2026-02-28**), in two sections — *"The Mind Loop"* and *"Self-Improvement With a Circuit Breaker."* Where the [[event-graph]] answers *"what happened and why"* and the [[authority-layer]] answers *"who said this was allowed,"* the mind loop is what generates the events and files the authority requests. The post's own framing of the layering: *"The event graph and authority layer are infrastructure. The mind loop is what lives on top of them."*

This article goes deep on the loop itself. The whole three-component system (event graph + authority layer + mind loop) is compiled as [[accountable-ai-architecture]]; the data structure and the consent gate have their own entities ([[event-graph]], [[authority-layer]]). The two load-bearing properties of the loop — **every action leaves a trail** and **the mind cannot exceed its authority** — are what the rest of this article is about.

> ⚠ **Fail-legible: code-exists claim.** The author states the code is "running right now" and "the code runs." This article was compiled from the *prose and the Go excerpts quoted inside the post*, not from a checkout of `github.com/mattxo/mind-zero-five`. The **design** is well-sourced; that a deployed binary currently exhibits these properties is the **author's testimony**, not independently verified here.

> ⚠ **Fail-legible: the loop mechanics are quoted only in part.** The post is explicit: *"the interesting part isn't the loop itself. It's what the mind does inside the loop, and how every single action is recorded."* It does not reproduce the full control flow. The phase sequence and the event names below are sourced to the post's prose and the specific code excerpts it includes — treat the loop's *internal* mechanics as **thin evidence**, and the two recorded properties below as the well-sourced core.

## What the loop does

The mind loop is described as "an autonomous AI agent that picks up tasks, plans, implements, reviews, and improves itself." The normal cycle a task runs through is named in the self-improvement section as **plan → implement → review → finish**. Crucially, the author redirects attention away from the loop's mechanics and onto two structural properties that hold *inside* it — the trail and the authority gate.

## Every action leaves a trail

The first property is total event coverage. Every step the mind takes emits an event into the [[event-graph]], so the loop's behaviour is reconstructable after the fact from the record alone. The post enumerates the events directly:

| When the mind… | …it logs | Payload noted in the post |
|---|---|---|
| claims a task | `task.claimed` | — |
| invokes Claude to write code | `mind.claude.invoked` | the prompt |
| receives Claude's response | `mind.claude.completed` | the result |
| passes the build | `build.completed` | — |
| commits | `code.committed` | — |
| fails an invocation | `mind.claude.failed` | the error |
| fails a build | `build.failed` | the error |

The post's summary line: *"Every action leaves a trail."*

**Full causal ancestry.** Each of these events carries its `Causes` — the list of event IDs that led to it (the [[event-graph]]'s causal-link field). Because every event records its causes, the loop produces a walkable chain: *"You can trace any commit back through the Claude invocation that produced it, the task that triggered it, the authority request that approved it, all the way back to whoever created the original task."* The post states the guarantee in three words each: *"Complete causal ancestry. For everything. Always."* This is the [[the-20-primitives|diagnostic-traversal]] primitive realised at the level of an autonomous agent's own actions.

A consequence the post draws out elsewhere ([[intelligence-is-an-operation-type]]): the model is **not** outside this. `mind.claude.invoked` / `mind.claude.completed` / `mind.claude.failed` are ordinary events with the same shape as `build.completed`. Claude is "invoked as a node in the system… subject to the same success/failure criteria and authority requirements as everything else."

## The mind cannot exceed its authority

The second property is the structural authority gate, shown via the concrete case of the mind restarting itself to pick up newly written code. The mind first creates an authority request at the `Required` level:

```
req, err := m.auth.Create(ctx, "restart",
    "Task completed. New binaries built.",
    "mind", authority.Required)
```

Then it asks the policy layer whether it is permitted to self-approve this action:

```
policy, err := m.auth.MatchPolicy(ctx, "restart")

if policy.ApproverID == m.actorID {
    // Self-approve: policy explicitly grants this
    m.auth.Resolve(ctx, req.ID, true)
} else {
    // Wait for human
    m.pendingRestart = req.ID
}
```

The branch is the whole point, and it is an **allowlist, fail-closed**: the permissive outcome (self-approve) happens *only* on the explicitly-proven branch — when an explicit policy names the mind's own actor as the approver. Otherwise the mind stores the request id in `pendingRestart` and waits. The post is emphatic about what "waits" means:

> "If no policy exists that grants self-approval, the mind waits. It doesn't proceed. It doesn't find a workaround. It sits in its loop, checking on each cycle whether the human has responded. The authority gate is not advisory — it's structural."

This is the behaviour named in the article's one-line description: faced with an action no policy grants it, the mind **waits indefinitely rather than finding a workaround.** Note the level chosen for `restart` is `Required` — it blocks for a human unless a policy explicitly elevates it — which is why an absent policy means an indefinite wait rather than a 15-minute auto-approval. (For the three levels and the `Policy` struct that `MatchPolicy` consults, see [[authority-layer]].)

> Confidence: high. The waiting-rather-than-working-around behaviour is stated in the prose *and* shown in the `else` branch *and* echoed in the sibling articles ([[accountable-ai-architecture]], [[intelligence-is-an-operation-type]], [[authority-layer]]). The cross-reference triangulates it.

## Self-improvement with a circuit breaker

The loop does not only react to externally created tasks — when idle (no pending work) it runs a self-assessment. This is "where it gets interesting" (the author's words), because it is recursive self-improvement that nevertheless cannot skip the human gate. The mechanism (`maybeAssess`):

```
func (m *Mind) maybeAssess(ctx context.Context) {
    if m.pendingProposal != "" {
        return  // already waiting on one
    }

    proposal, err := m.Assess(ctx)

    // Submit for approval
    req, err := m.auth.Create(ctx, "self-improve",
        proposalJSON,
        "mind", authority.Recommended)

    m.pendingProposal = req.ID
}
```

The shape of the circuit breaker:

1. **Guard against pile-up.** If a proposal is already pending (`pendingProposal != ""`), it returns immediately — only one self-improvement in flight at a time.
2. **Assess and propose.** It identifies something it could do better — *"a refactor, a missing test, an architectural improvement"* — and formulates a proposal.
3. **Submit for approval at `Recommended`.** The proposal goes in at the `Recommended` authority level, *"meaning the human has 15 minutes to say no."* Silence is consent; objection is always possible.
4. **Proceed only on non-objection.** *"If they don't, the mind proceeds: it creates a task from the proposal, claims it, implements it through the normal plan → implement → review → finish cycle, and every step is logged in the event graph."*

The author's name for this is **"recursive self-improvement with a consent circuit breaker."** The mind *"can identify its own deficiencies. It can propose fixes. It can implement those fixes. But it cannot skip the authority gate."* The contrast drawn between the two actions is deliberate: `restart` is `Required` (blocks for a human), `self-improve` is `Recommended` (proceeds on silence after 15 minutes) — graduated trust applied to two different stakes within the same loop.

> ⚠ **Fail-legible: "not mutually exclusive."** The post offers this loop as a refutation of a common assumption — *"Recursive self-improvement and human oversight are not mutually exclusive. You can have both."* That is demonstrated **for this system's design, by construction** — it is not a general theorem about all self-improving AI. The post presents mind-zero-five as one working existence proof, not a universal guarantee.

The closing framing of the section is the thesis of the whole post: structured accountability is *"not 'we promise the AI won't do anything bad'… A verifiable, cryptographically linked, causally traceable record of every decision, every action, every approval, and every outcome. With hard gates that the AI cannot bypass [`Required`], and soft gates where silence means consent but intervention is always possible [`Recommended`]."*

## How the loop survives a crash

The same post's next section, *"Crash Recovery as Ethics,"* is part of why the loop can be trusted to keep its trail intact — it is compiled in depth as [[crash-recovery-as-ethics]], but it bears directly on the loop. On startup, `recoverState` (1) cleans orphaned file changes from a previous crash (preventing one task's uncommitted work from bleeding into the next), (2) rehydrates the loop's in-memory state by re-reading pending authority requests — re-arming exactly the `pendingRestart` / `pendingProposal` fields the two sections above set — and (3) recovers stale in-progress tasks. The recovery policy quoted in the post: stale tasks (in progress >30 minutes with no update) are requeued; blocked tasks retry with exponential backoff up to three times, after which the system *"stops and waits for human intervention"* rather than silently failing. The author's argument: *"The event graph can't have integrity if a crash can corrupt it"* — so recovery is positioned as accountability, not reliability garnish. This is the same fail-safe-by-default posture as the authority gate: on ambiguous or corrupt state, halt and wait.

## Relationship to dark-factory (prior pattern, not a dependency)

The first-party *Dark Factory - Motive, Goal, Approach* names the mind loop as part of a **"prior implementation pattern"**: mind-zero-five is *"open-source Go code with event graph, authority layer, and mind loop; not imported into Dark Factory as a dependency,"* used as *"evidence that accountability architecture is implementable; informs but does not govern"* (L382). Two pieces of the mind loop have explicit successors in the dark-factory crosswalk:

- *"agent action becomes bounded runtime invocation"* (L128) — the mind loop's "invoke Claude as a node" is generalised into the [[runtime-broker|bounded runtime]] / [[runtime-broker]]. (This is why `bounded-runtime` is carried as an alias here — earlier articles forward-reference the loop under that name.)
- *"self-improvement becomes EvolutionOrder, eval, human review, activation policy, and rollback"* (L130) — the single `Recommended`-level circuit breaker is expanded into the full governed pipeline [[capability-evolution]], whose orientation one-liner is *"Capability evolution is production work, not an uncontrolled self-improvement loop."*

> ⚠ **Fail-legible: related, not identical.** "Bounded runtime invocation" is the dark-factory *successor* concept; it is not a term used in the Searles post, and the dark-factory docs are explicit that the mind loop "informs but does not govern" their design. The shared DNA is the principle ([[intelligence-is-an-operation-type|intelligence as one operation type]]) and the trace-everything / authority-gate spine — **not** shared code. The two are stated side by side here, not merged.

The Open Brain operational record corroborates the *principle* in the live first-party stack rather than the mind-zero binary: in a 2026-06-11 dark-factory review, an allocator's attempt to renew its own duration at the 12-hour ceiling was **refused at validation** with an error teaching the design — *"a society that can extend its own epoch indefinitely is the failure mode the 12h bound prevents"* (epoch extension belongs to the human restart decision, not self-extension). That is the same "the mind waits, it does not work around its own authority" discipline this article describes, implemented in a different (and governed) codebase. It is a cross-check on the principle, not evidence about `github.com/mattxo/mind-zero-five`.

## What grew from it

- **Within mind-zero-five:** the loop is the consumer of the [[event-graph]] (it emits `task.claimed` … `build.failed` with `Causes`) and of the [[authority-layer]] (it files `Required`/`Recommended` requests and obeys `MatchPolicy`). [[crash-recovery-as-ethics|Crash recovery]] keeps the loop's trail intact across restarts.
- **As one component of the system:** the whole event-graph + authority + loop architecture is [[accountable-ai-architecture]]; the loop is where the load-bearing principle [[intelligence-is-an-operation-type]] becomes observable (the model is logged like any other operation).
- **Into the first-party stack:** the loop's two halves map forward to the [[runtime-broker|bounded runtime]] (agent action) and [[capability-evolution]] (governed self-improvement) — reimplemented, not imported.

## Sources & provenance

Compiled this run from:

- `raw/searles/all-posts-1.md` — **"The Architecture of Accountable AI"** (2026-02-28 · primary · `[Searles-P3]` · https://mattsearles2.substack.com/p/the-architecture-of-accountable-ai). Specifically §*"The Mind Loop"* (L598-631: the trail / event list / `Causes` ancestry; the `restart` authority request, `MatchPolicy` self-approval branch, and the "waits, doesn't work around" prose) and §*"Self-Improvement With a Circuit Breaker"* (L634-661: `maybeAssess`, the `Recommended`/15-minute proposal, the plan→implement→review→finish cycle, "recursive self-improvement with a consent circuit breaker," "not mutually exclusive"). Context from §*"Crash Recovery as Ethics"* (L665-691: `recoverState`, stale-task >30min requeue, three-retry-then-stop) and §*"What The Code Proves"* (L695-707).
- **`Dark Factory - Motive, Goal, Approach.md`** (first-party orientation synthesis). Source for the mind loop as a "prior implementation pattern… not imported into Dark Factory as a dependency" (L382), and the motive crosswalk lines "agent action becomes bounded runtime invocation" (L128) and "self-improvement becomes EvolutionOrder, eval, human review, activation policy, and rollback" (L130).
- **Open Brain** — the civilization-wiki seed scan (2026-06-13), which lists the mind loop as a named component of the accountable-AI architecture and records the durable repo `github.com/mattxo/mind-zero-five`; and the dark-factory slice-1 v14 review thought (2026-06-11), used only as a cross-check that the "refuse self-extension, wait for the human" principle is implemented (and enforced fail-closed) in the live first-party stack — not as evidence about the mind-zero binary.

Strong claims flagged inline: code-currently-runs (author testimony, not checked out this run); the loop's internal mechanics (quoted only in part by the post — thin); "self-improvement and oversight are not mutually exclusive" (true by construction for this design, not a general theorem); "bounded runtime invocation" as a successor concept (dark-factory term, related-not-identical, stated not merged). The repository `github.com/mattxo/mind-zero-five` was **not** checked out this run; all code references are to the excerpts quoted inside the post. `[[wikilinks]]` are forward references where targets are not yet compiled (e.g. [[crash-recovery-as-ethics]], [[runtime-broker]] alias *bounded runtime*).
