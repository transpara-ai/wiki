---
entity: The Architecture of Accountable AI (mind-zero-five)
aliases: [mind-zero-five, accountable AI architecture, the accountability architecture, the code post]
tier: foundational
status: compiled
last_compiled: 2026-06-13
sources:
  - raw/searles/all-posts-1.md  # "The Architecture of Accountable AI", 2026-02-28 [Searles-P3] — primary
  - raw/searles/all-posts-1.md  # "From 44 to 200", 2026-02-28 [Searles-P2] — the 44 primitives this code grounds in
  - raw/searles/all-posts-1.md  # "The Moral Ledger", 2026-02-28 [Searles-P5] — the event graph as moral ledger
  - "Dark Factory - Motive, Goal, Approach.md"  # first-party framing of mind-zero-five as prior pattern
durable_urls:
  - https://mattsearles2.substack.com/p/the-architecture-of-accountable-ai  # [Searles-P3]
  - https://mattsearles2.substack.com/p/from-44-to-200                       # [Searles-P2]
  - https://mattsearles2.substack.com/p/the-moral-ledger                     # [Searles-P5]
  - https://github.com/mattxo/mind-zero-five                                 # [Searles-MindZeroRepo]
confidence:
  code_exists_and_runs: asserted by the author — "running right now", "the code runs". The wiki has read the prose and the code excerpts quoted in it, not the repository; not independently verified this run. Treat the *design* as well-sourced and the *operational claim* as the author's testimony.
  is_ought_bridge: explicitly hypothesis-not-proof per the author ([[the-moral-ledger]]); flagged inline.
  load_bearing_principle: "intelligence is just another operation type" is the author's stated design commitment and is independently echoed in the first-party dark-factory doc; sound as a claim about intent, not a verified property of the running binary.
  post_numbering: sources disagree on the ordinal — see "A note on the numbering" below. Cited by title to avoid picking a winner.
---

# The architecture of accountable AI (mind-zero-five)

On **2026-02-28**, in the post *"The Architecture of Accountable AI,"* Matt Searles (working with Claude) turned the philosophy of the preceding posts into running code. Where [[the-20-primitives]] gave the seed and [[the-44-primitives]] / [[the-200-primitives]] gave the conceptual ladder, this post is — in its own words — "about the code. Not the philosophy. Not the theory. The actual working software." The author's framing for why this post exists: *"principles you can't implement aren't principles — they're wishes."*

The system is called **mind-zero-five** (open source, written in Go, at `github.com/mattxo/mind-zero-five`). It has three core components — an **event graph**, an **authority layer**, and an **autonomous mind loop** — plus two design choices the post treats as load-bearing: a **self-improvement circuit breaker** and **crash-recovery-as-ethics**. Together they are the author's answer to one question: *"How do you build an AI system that cannot act without leaving a verifiable trail, and cannot exceed its authority without human consent?"*

The thesis is structural, not aspirational: accountability is encoded in data structures and APIs, not promised in a policy document. The recurring contrast in the post is **structure vs. trust** — "trust that doesn't require trusting."

> ⚠ **Fail-legible: code-exists claim.** The author states the code is "running right now" and "the code runs." This article was compiled from the *prose and the Go excerpts quoted inside the post*, not from a checkout of the repository. The **design** is well-sourced; the claim that a deployed binary currently exhibits these properties is the **author's testimony**, not independently verified here.

## The load-bearing principle: intelligence is just another operation type

The single architectural commitment the rest of the design rests on: **the AI stays inside the graph.** In the post's words, "intelligence is just another operation type. Claude is invoked as a node in the system — it receives inputs, produces outputs, and is subject to the same success/failure criteria and authority requirements as everything else. It is not elevated above the accountability structure. It lives within it."

This is the same move recorded in [[the-20-primitives]] (the late-night seed already treated "node action" and "LLM-defined expansion" as ordinary operations) and it is independently restated in the first-party [[dark-factory-motive-goal-approach]]: *"Dark Factory treats intelligence as one operation type inside a larger accountability system."* Two sources, no conflict — this is the through-line from the philosophy to both the mind-zero code and the later dark-factory work.

> Confidence: this is a claim about **design intent**, well-attested across two independent sources. Whether the running binary perfectly upholds "no special-casing for the model" is not something this article verified.

## The event graph

The foundation is a twelve-field Go `Event` struct (`ID`, `Type`, `Timestamp`, `Source`, `Content`, `Causes`, `ConversationID`, `Hash`, `PrevHash`). Three properties make it the spine of accountability:

- **Append-only.** Events are never modified or deleted. The post is explicit that this is "not a database design choice — it's an ethical commitment encoded in the data structure. What happened, happened." You can supersede an old event with a new one, but you cannot rewrite history.
- **Hash-chained.** Each event carries a SHA-256 of its own canonical form plus the previous event's hash, so the whole history is cryptographically linked. A `VerifyChain()` method can validate integrity at any time; tampering anywhere breaks the chain and is detectable. The post's phrase: "trust that doesn't require trusting."
- **Causally linked.** The `Causes` field (a list of prior event IDs) is what makes this a *graph*, not a log — a directed acyclic graph of causation, walkable via `Ancestors()` and `Descendants()`.

The post ties this directly back to the origin: the causal graph is "the diagnostic traversal primitive from the original 20," and it answers the late-night question — "how do you trace a failure back to its source?" See [[event-graph]] for the data structure as its own entity and [[the-20-primitives]] for the diagnostic-traversal seed.

**The fail-closed design lives in what the interface omits.** The quoted `EventStore` interface has `Append`, `Get`, `Recent`, `ByType`, `BySource`, `Since`, `Count`, `VerifyChain`, `Ancestors`, `Descendants`, `Search` — and crucially **no `Update()` and no `Delete()`.** As the post puts it: "The event store is structurally incapable of rewriting history. This isn't enforced by policy or convention — it's enforced by the interface itself." (This is the same fail-closed-by-default discipline tracked elsewhere: the permissive operation is simply absent, so it cannot be reached.)

## The authority layer

If the event graph answers "what happened and why," the authority layer answers "who said this was allowed?" Authority is "a structural gate that cannot be bypassed," not "a speed bump or a compliance checkbox."

There are exactly three levels (a Go `Level` string), modelling three relationships between human and AI:

| Level | Behaviour | Human analogue (post's framing) |
|---|---|---|
| `Required` | Blocks until a human explicitly approves; the system "does not proceed" | A new employee — approval for everything |
| `Recommended` | Auto-approves after a 15-minute timeout (`RecommendedTimeout = 15 * time.Minute`) unless a human objects — "silence means consent" | A trusted colleague — proceeds unless you object |
| `Notification` | Auto-approves immediately; the AI acts and tells you | A senior partner — just keeps you informed |

A separate `Policy` struct maps an `Action` (exact match or `"*"` wildcard) to an `ApproverID` and a default `Level`. The mind may self-approve an action **only if an explicit policy grants it that right** — the trust model is configurable, auditable, and itself recorded in the event graph. The post calls this "the Consent primitive from Layer 3 (Society), implemented as code": legitimate action requires consent; consent is explicit, traceable, and revocable. See [[authority-layer]] and [[consent-layer]].

The graduated `Required`/`Recommended`/`Notification` design is what the post means by **"trust is graduated, not binary"** — tighten or relax oversight as competence is demonstrated.

## The mind loop

The mind loop is the autonomous agent that lives on top of the infrastructure: it claims tasks, plans, implements, reviews, and finishes. Two properties matter more than the loop mechanics:

**Every action leaves a trail.** Claiming a task logs `task.claimed`; invoking Claude logs `mind.claude.invoked` (with the prompt); the response logs `mind.claude.completed`; then `build.completed`, `code.committed`, or on failure `mind.claude.failed` / `build.failed` (with the error). Every such event carries its `Causes`, so any commit traces back through the Claude invocation, the task, the authority request, all the way to whoever created the original task — "complete causal ancestry. For everything. Always."

**The mind cannot exceed its authority.** To restart itself and pick up newly written code, the mind creates a `Required` authority request, then checks `MatchPolicy`. If the policy's `ApproverID` equals the mind's own actor ID, it self-approves; otherwise it sets `pendingRestart` and waits. The post is emphatic: "If no policy exists that grants self-approval, the mind waits. It doesn't proceed. It doesn't find a workaround… The authority gate is not advisory — it's structural." See [[bounded-runtime]] / [[the-mind-loop]].

> Fail-legible: the post quotes the *core* of the loop ("the interesting part isn't the loop itself") rather than the full control flow. The behavioural claims above are sourced to the post's prose and the specific excerpts it includes; the complete loop implementation was not read this run.

## Self-improvement with a circuit breaker

The headline capability — and the one the author flags as "where it gets interesting" — is recursive self-improvement that **cannot skip the human gate.** When idle, the mind runs `maybeAssess`: if there's no proposal already pending, it calls `Assess`, formulates an improvement (a refactor, a missing test, an architectural change), and **submits the proposal as an authority request at the `Recommended` level** (15-minute window), storing it as `pendingProposal`.

If the human doesn't object within the window, the mind creates a task from the proposal, claims it, and runs it through the normal plan → implement → review → finish cycle, logging every step. The post's summary: "recursive self-improvement with a consent circuit breaker. The mind can identify its own deficiencies. It can propose fixes. It can implement those fixes. But it *cannot skip the authority gate*." This is offered as the concrete refutation of a common assumption — **"self-improvement doesn't require unchecked autonomy… Recursive self-improvement and human oversight are not mutually exclusive."**

> Fail-legible: that self-improvement and oversight "are not mutually exclusive" is demonstrated *for this system's design*, by construction. It is not a general theorem about all self-improving AI — the post presents mind-zero-five as one working existence proof, not a universal guarantee.

## Crash recovery as ethics

The post reframes ordinary defensive programming as part of the accountability architecture. On startup, `recoverState` (1) cleans orphaned file changes from a previous crash via `CleanWorkingTree` (preventing cross-task contamination), (2) rehydrates in-memory state by re-reading pending authority requests (re-arming `pendingRestart` / `pendingProposal`), and (3) recovers stale in-progress tasks.

Specific recovery policy quoted in the post:
- Stale tasks — in progress >30 minutes with no update — are automatically recovered and requeued.
- Blocked tasks are retried with exponential backoff, **up to three times**; after three failures the system stops and waits for human intervention. "The system doesn't silently fail."

The argument is that an autonomous system that can crash and leave corrupted state (uncommitted changes bleeding into the next task, lost authority requests, abandoned work) "is a system that can't be trusted… The event graph can't have integrity if a crash can corrupt it." Crash recovery is therefore positioned as ethics, not reliability garnish. This is the same fail-safe-by-default posture — refuse/halt on ambiguous or corrupt state rather than proceeding.

## What the post claims the code proves

The post closes with five explicit claims. Stated as the author's claims (the strong ones are flagged):

1. **AI accountability is implementable** — "not a policy document… a data structure and an API. You can build it. You can deploy it. You can verify it."
2. **The AI stays inside the graph** — the load-bearing principle above.
3. **Self-improvement doesn't require unchecked autonomy** — by construction, for this system.
4. **Trust is graduated, not binary** — the three authority levels.
5. **The complete history is verifiable** — by anyone, via the hash chain, "trust that doesn't require trusting."

> ⚠ **Fail-legible: "you can verify it" / "the complete history is verifiable."** These are properties of the *design* (append-only + hash chain + `VerifyChain()`). The post asserts they hold in the running system; this article verified the argument and the quoted code, not a live deployment. Label: design-sound, operation-attested-not-checked.

## The moral-ledger extension (and its honesty about itself)

A later post, *"The Moral Ledger,"* extends the same event graph from "audit trail" to "moral ledger": at the scale of institutions, complete causal visibility means *"I didn't know" stops being a defence*, "it wasn't my decision" becomes verifiable, and "trust us" becomes unnecessary because the record is independently verifiable — "accountability structural rather than voluntary." This is the same event graph from this post, read at organizational scale. See [[the-moral-ledger]].

That post also hangs a larger philosophical claim on the architecture — that if consciousness is fundamental, Hume's is-ought gap is "a perspective shift, not a gap," and the event graph records "what happened *to beings that experience*." **The author is explicit that this is hypothesis, not proof:** "I don't know if the is-ought bridge actually works… I'm not so arrogant as to think a software architecture and an AI derivation have settled the question." It is recorded here only because it is the stated philosophical payload of the same architecture; the wiki does not endorse it. The author is equally explicit that "the event graph doesn't solve ethics" — it makes consequences visible and accountability structural; it does not tell you what is right. See [[three-irreducibles]] / [[strange-loop]].

## Relationship to dark-factory

The first-party [[dark-factory-motive-goal-approach]] names mind-zero-five as a **"prior implementation pattern"**: "open-source Go code with event graph, authority layer, and mind loop; **not imported into Dark Factory as a dependency**." It is "used as evidence that accountability architecture is implementable; informs but does not govern." So the two sources agree on what mind-zero-five *is* and explicitly agree on what it is *not* — an upstream dependency. The shared DNA is the load-bearing principle (intelligence as one operation type) and the event-graph + authority + trace spine, not shared code.

## A note on the numbering (source conflict, surfaced not resolved)

The sources disagree on this post's ordinal:

- The dark-factory citation table labels it **`Searles-P3`** ("The Architecture of Accountable AI") and labels "The Moral Ledger" implicitly later in the series.
- Inside the post itself it self-identifies as **"Post 3 of a series."**
- *"The Moral Ledger"* opens with "This is the last post in the series. The first four covered the origin… the emergence… the code… and the politics," and signs off as **"Post 5, the final post"** — which makes the code post the 3rd of five (origin=1, emergence=2, code=3, Pentagon=4, ledger=5).

The internal numbering (code = Post 3, ledger = Post 5) is self-consistent. To avoid silently picking a scheme, this article cites every source **by title**, and the frontmatter records "The Moral Ledger" as `[Searles-P5]` with this conflict flagged.

## What grew from it

- **Into the first-party stack:** the accountability spine (event graph + authority + trace, intelligence-as-operation) is the philosophical input to [[dark-factory]] ([[dark-factory-motive-goal-approach]]), which reimplements rather than imports it.
- **Into philosophy:** the same event graph is reread as [[the-moral-ledger]]; the layered framework it sits on is [[the-200-primitives]] / [[fourteen-layers]], with [[strange-loop]] and [[three-irreducibles]] as its philosophical edges.
- **Component entities:** [[event-graph]], [[authority-layer]], [[consent-layer]], [[the-mind-loop]], [[bounded-runtime]].

## Sources & provenance

Compiled this run from:

- `raw/searles/all-posts-1.md` — **"The Architecture of Accountable AI"** (2026-02-28 · primary · `[Searles-P3]` · https://mattsearles2.substack.com/p/the-architecture-of-accountable-ai). Read in full. Source for the event graph, authority layer, mind loop, self-improvement circuit breaker, crash-recovery-as-ethics, the five "what the code proves" claims, and the load-bearing principle.
- `raw/searles/all-posts-1.md` — **"From 44 to 200"** (2026-02-28 · `[Searles-P2]` · https://mattsearles2.substack.com/p/from-44-to-200). Relevant portions read (the 44 primitives in 11 groups, including the Foundation/Causality/Integrity groups whose `Event`/`EventStore`/`HashChain`/`CausalLink` concepts this code implements; the layer structure incl. Layer 3 Society → Consent).
- `raw/searles/all-posts-1.md` — **"The Moral Ledger"** (2026-02-28 · `[Searles-P5]` per its own sign-off · https://mattsearles2.substack.com/p/the-moral-ledger). Read in full. Source for the event-graph-as-moral-ledger reading and the explicitly-hypothesis is-ought material.
- **`Dark Factory - Motive, Goal, Approach.md`** (first-party). Source for "intelligence as one operation type," the "prior implementation pattern / not a dependency" framing of mind-zero-five, and the durable Searles URL table (`Searles-P1/P2/P3`, `Searles-MindZeroRepo`, etc.).
- **Open Brain** — civilization-wiki seed scan (2026-06-13) corroborating the conceptual spine (primitive ladder → event graph → accountable-AI architecture; "intelligence is just another operation type — keep the AI inside the graph"). Used as a cross-check, not as a primary factual source.

Conflicts surfaced, not resolved: the post-numbering discrepancy (above). Strong claims flagged inline: code-currently-runs (author testimony), is-ought bridge (hypothesis per author), "verifiable by anyone" (design-sound, live deployment not checked here). The repository `github.com/mattxo/mind-zero-five` was **not** checked out this run; all code references are to the excerpts quoted inside the posts. `[[wikilinks]]` are forward references; most targets are not yet compiled.
