---
entity: Crash Recovery as Ethics
org: transpara-ai
primary_placement: civilization/concept
placements:
  - civilization/concept
classification: internal
aliases: [crash recovery, crash-recovery, recoverState, stale task recovery, reboot survival]
tier: concept
status: compiled
last_compiled: 2026-06-13
sources:
  - raw/searles/all-posts-1.md  # post 3, "The Architecture of Accountable AI", 2026-02-28 [Searles-P3] — the "Crash Recovery as Ethics" section: recoverState code, the ethics claim, 30-min stale recovery, exponential backoff
  - raw/searles/all-posts-1.md  # post 8, "What It's Like to Be a Node", 2026-02-28 [Searles-Node] — the metaphorical extension of stale-task recovery and crash recovery to human psychology and death
  - Open Brain  # operational facts on the real reboot-survival / checkpoint system (transpara-ai/hive PR #43, #50; verified 2026-04-17) and a live power-loss recovery (dark-factory slice-1 round 4, 2026-06-11)
confidence:
  ethics_claim: high as the source's own framing — Searles states it directly ("It's not [defensive programming]. It's an ethical design decision."); whether crash recovery is *necessary* for accountability is his architectural argument, not an independently proven theorem
  repo_identity: contested — the Searles passage describes mind-zero-five (github.com/mattxo/mind-zero-five); the shipped recovery code the Open Brain notes describe lives in transpara-ai/hive (pkg/checkpoint) and a shared event store. These are related in shape, not asserted to be the same codebase (see [[event-graph]] for the same conflict)
  thirty_minute_and_three_retry_numbers: high — quoted directly from [Searles-P3]; the shipped hive system uses its own boundary/heartbeat mechanics (Open Brain), so the exact thresholds are the post's, not necessarily the live code's
---

# Crash Recovery as Ethics

**The claim that cleaning up after a crash is an accountability requirement, not a reliability nicety.** It appears in the third Searles post, *"The Architecture of Accountable AI"* (**2026-02-28**), in a short section titled exactly *"Crash Recovery as Ethics."* The argument: an autonomous system that can crash mid-operation and leave corrupted state — uncommitted changes bleeding into the next task, authority requests lost, in-progress work abandoned — is a system that can't be trusted, so recovery belongs to the same accountability architecture as the [[event-graph]] and the [[authority-layer]], not to a "reliability" backlog. The post's load-bearing sentence: *"The event graph can't have integrity if a crash can corrupt it."*

This is a small section of a larger post, but it is the place where the arc states most plainly that **fail-safe-on-restart is an ethical, not just operational, property** — the same move [[event-graph|the event store]] makes by omitting `Update`/`Delete`, and the same logic [[dark-factory]] later generalises into fail-closed [[gates]].

## What the code does

The source ([Searles-P3]) gives the recovery routine verbatim, as a method on the [[the-mind-loop|mind]]:

```
func (m *Mind) recoverState(ctx context.Context) {
    // Clean orphaned changes from crash
    files, err := CleanWorkingTree(ctx, m.repoDir)

    // Rehydrate pending authority requests
    pending, err := m.auth.Pending(ctx)
    for _, req := range pending {
        switch req.Action {
        case "restart":
            m.pendingRestart = req.ID
        case "self-improve":
            m.pendingProposal = req.ID
        }
    }
}
```

On startup the mind does three things, per the post:

1. **Cleans orphaned file changes** from a previous crash — explicitly to prevent *cross-task contamination* (uncommitted edits from a dead task leaking into the next one).
2. **Rehydrates in-memory state** by reloading pending [[authority-layer|authority]] requests, so a `restart` or `self-improve` request the mind was waiting on survives the crash rather than being silently dropped.
3. **Recovers stale tasks** that were in progress when the crash happened.

The stale-task and retry policy is also quoted directly: anything *"in progress for more than 30 minutes with no update"* is automatically recovered and requeued; blocked tasks are retried with *exponential backoff, up to three times*; and after three failed attempts the system *"stops and waits for human intervention"* rather than silently failing. This three-strikes-then-escalate shape is the same fail-safe-by-default reflex the [[authority-layer]] and [[gates]] encode elsewhere — the permissive outcome (keep retrying) is bounded, and the terminal state is *hand back to a human*, not *give up quietly*.

## Why the source calls it ethics, not engineering

The post anticipates the obvious objection and rejects it head-on:

> "This might seem like routine defensive programming. It's not. It's an ethical design decision… Crash recovery isn't an afterthought bolted on for reliability. It's part of the accountability architecture."

The reasoning chain is: the [[event-graph]] is the accountability substrate; accountability requires the graph's integrity; a crash that leaves orphaned changes, lost authority requests, or abandoned work *corrupts the state the graph is supposed to faithfully record*; therefore recovery that restores a clean, truthful starting point is what *keeps the ledger trustworthy across restarts*. Hence the closing line — *"The event graph can't have integrity if a crash can corrupt it."* (The [[event-graph]] article quotes this same sentence as the reason crash recovery exists in the system at all.)

> ⚠ **Fail-legible note (what is and isn't proven).** That crash recovery is *implemented* as described is grounded — the code is in the source. That it is *ethics rather than mere defensive programming* is Searles's own framing, asserted directly and argued, not independently demonstrated; a reader is free to read the same routine as ordinary robustness. The article carries the ethical claim because the source makes it explicitly and names the section that way, and labels it as the author's argument rather than a settled result.

## The metaphorical extension (a different post, same primitive)

A later post, *"What It's Like to Be a Node"* ([Searles-Node], 2026-02-28 — authored by Searles solo, unlike the "+Claude" byline on the architecture posts), reuses the *same* recovery primitives as a lens on human experience, not as architecture. There:

- **Stale task recovery** is likened to *"that feeling at 3am where your brain suddenly surfaces something you forgot,"* with the contrast that the architecture *requeues with exponential backoff, tries three times, then waits* — whereas the human backlog *"has no garbage collection… every unprocessed event stays in the queue until you die."*
- **Crash recovery** is set against mortality directly: *"The architecture handles crash recovery. The human architecture handles death by not handling it"* — every human output framed as *"an attempt to persist past the crash."*

> ⚠ **Fail-legible note (register shift).** This second post is **phenomenological/philosophical essay, not system documentation.** It is cited here only to show that "crash recovery" became a recurring *concept* in the arc, applied analogically to humans; nothing in it should be read as a claim about what the software does. It also explicitly inverts the ethics framing — for a human, the append-only, never-recoverable store is described as a *cruelty* ("we can't drop events"), where for the machine the same append-only property is the source of trust.

## What the code actually is (operational corroboration, and a contested repo)

The shipped reality the operational record (Open Brain) describes corroborates the *architecture-as-ethics* claim with working software, while reproducing the repo-identity conflict already flagged for the [[event-graph]]:

- A **reboot-survival / checkpoint system** was built and merged in `transpara-ai/hive` (PR #43, commit `3913b9f`; later PR #50), as a `pkg/checkpoint` package. It is **two-tier**: Open Brain captures *intent* for warm-start, and **event-chain replay** reconstructs *mechanical state* as a cold-start fallback — directly the "recover from the durable record" pattern the post argues for.
- It was **verified live** (2026-04-17): an integration test against real Postgres confirmed `task.created`/`task.assigned` events survive a simulated `SIGKILL`, **event-chain hash integrity is preserved across restart**, and replay recovered 46 completed tasks and 6 agent budgets. This is the concrete form of *"the event graph can't have integrity if a crash can corrupt it"* — the chain verifies after the crash.
- The designed recovery path was later **exercised by a real power loss** (dark-factory slice-1 round 4, 2026-06-11): a healthy run was interrupted by power death; on resume against the same event store, with no re-seed, the system cold-recovered (role-only checkpoints) and within ~2 minutes auto-reassigned the *same* in-progress child task ID read back from the chain — *cross-epoch task continuity proven*. The same record notes a cosmetic detail: Postgres WAL sequence numbers skip across the crash (gaps are harmless because hash-chaining is per-event, not per-sequence).

> ⚠ **Fail-legible note (repo identity is contested).** The Searles passage describes **mind-zero-five** (`github.com/mattxo/mind-zero-five`); the shipped recovery code in the Open Brain notes lives in **`transpara-ai/hive`** (and writes to a shared event store also referred to elsewhere as `eventgraph`). The sources do **not** assert these are the same codebase, and neither does this article — see [[event-graph]] for the same `mind-zero-five` vs `eventgraph`/`hive` conflict. What is consistent across all of them is the *shape*: clean the working tree, rehydrate pending authority, recover stale/in-progress work from the durable chain on startup.

> ⚠ **Fail-legible note (thresholds are the post's).** The exact figures — *>30 minutes* for staleness and *three retries* with exponential backoff — are quoted from [Searles-P3] about mind-zero-five. The shipped hive system uses its own boundary-trigger and heartbeat mechanics (per Open Brain); the article does not claim the live thresholds equal the post's numbers.

## Where it sits in the arc

- **On top of the substrate:** crash recovery exists *because of* the [[event-graph]] — it is the routine that protects the chain's integrity across restarts. The [[event-graph]] article cites this concept as the reason recovery is first-class.
- **Inside the loop:** it is a method on the [[the-mind-loop|mind loop]], run on startup before normal plan → implement → review work resumes.
- **Of a piece with the gates:** the "retry three times, then stop and wait for a human" terminal behaviour is the same fail-safe-by-default / escalate-don't-fail-open reflex as the [[authority-layer]] and [[dark-factory]]'s fail-closed [[gates]].
- **From the seed:** like the rest of the architecture, it serves the traceability goal of [[the-20-primitives]] — a corrupted post-crash state would break the *"everything is traceable to its source"* guarantee.

## Sources & provenance

Compiled from `raw/searles/all-posts-1.md`:
- Post 3, *"The Architecture of Accountable AI"*, 2026-02-28 · [Searles-P3] · https://mattsearles2.substack.com/p/the-architecture-of-accountable-ai — the section titled *"Crash Recovery as Ethics"*: the `recoverState` routine (`CleanWorkingTree`, rehydrating pending authority requests, recovering stale tasks), the explicit "ethical design decision" framing, the *"event graph can't have integrity if a crash can corrupt it"* line, and the 30-minute / three-retry policy.
- Post 8, *"What It's Like to Be a Node"*, 2026-02-28 · [Searles-Node] · https://mattsearles2.substack.com/p/what-its-like-to-be-a-node — the metaphorical extension of stale-task recovery and crash recovery to human psychology, backlog, and mortality (a philosophical essay, not system documentation).

Operational facts from Open Brain captured thoughts: the two-tier reboot-survival / checkpoint system in `transpara-ai/hive` (PR #43 / commit `3913b9f`; PR #50), its 2026-04-17 live verification against Postgres (chain integrity preserved across `SIGKILL`; 46 tasks / 6 budgets replayed), and the 2026-06-11 power-loss recovery in dark-factory slice-1 round 4 (cross-epoch task continuity; harmless WAL sequence skip).

**Conflicts stated, not resolved:** (1) the implementation's repo identity — `mind-zero-five` (Searles) vs. `transpara-ai/hive` + shared `eventgraph` store (Open Brain), the same conflict flagged for [[event-graph]]; (2) whether the concrete thresholds (30 min, 3 retries) in the post match the shipped system — not asserted equal. The "ethics, not defensive programming" framing is the source author's explicit argument, carried and labelled as such. `[[wikilinks]]` are forward references; some targets are not yet compiled.
