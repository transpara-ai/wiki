---
entity: The Work Graph
org: transpara-ai
primary_placement: civilization/foundational
placements:
  - civilization/foundational
classification: internal
aliases: [work graph, Work Graph, Layer 1, Agency layer, agency graph, the Work Graph]
tier: foundational
status: compiled
last_compiled: "2026-06-14"
sources:
  - raw/searles/all-posts-1.md  # post 14, "The Work Graph", 2026-03-01 [Searles-WorkGraph] — the full deep-dive; primitives, broken patterns, Lovatts deployment, "Company in a Box", what it does not do
  - raw/searles/all-posts-1.md  # post 11, "Thirteen Graphs, One Infrastructure", 2026-03-01 [Searles-13Graphs] — overview context; "I'm building the Work Graph this week"
confidence:
  sources: primary
  claims: grounded
  primitives_list: high — quoted verbatim from [Searles-WorkGraph]
  lovatts_deployment: grounded — author states "I'm deploying this week"; outcome not confirmed in corpus
  layer_numbering: contested — Scheme A (canonical post 11) names Layer 1 Work, Layer 2 Market, Layer 3 Social; Scheme B (post 6 + deep dives) uses Relationship/Community for layers 9–10. Layer 1 = Work is consistent across both schemes.
  company_in_a_box_claim: asserted by author; not independently verified
---

# The Work Graph

**The first graph to be built, and the one Searles was already deploying when he wrote about it.** The Work Graph is Layer 1 of the [[thirteen-graphs|thirteen-graph]] arc — the Agency layer — and its distinguishing feature is that it was not a thought experiment. The fourteenth post in the series, *"The Work Graph"* (**2026-03-01**), opens with the sharpest sentence in the corpus: *"Not theory. Not 'imagine if.' This is happening."*

The company was Lovatts Puzzles: hundreds of legacy applications accumulated over decades, held together by institutional memory living in people's heads. The Work Graph was the intervention — not a replacement for the legacy systems, but an [[event-graph]] laid underneath them to make the whole mass legible for the first time.

## Layer 1: what the primitives are

Layer 1 — Agency — is defined by twelve primitives, quoted verbatim ([Searles-WorkGraph]):

> Observer, Participant, Actor, Action, Decision, Intention, Goal, Plan, Resource, Capacity, Autonomy, Responsibility.

The author's gloss on why these and not others: "These aren't abstract categories. They're the things that have to be true for work to happen." The line from Observer to Responsibility is the causal spine of any piece of work — someone notices a situation, decides to act, has the capacity and resources to do so, takes action, and is accountable for the outcome. Every task-management tool in existence implements a partial, informal version of this set. None of them implement the full set, and none link the primitives causally.

The Jira comparison is precise ([Searles-WorkGraph]): a ticket is "a collapsed version of Action + Goal + Responsibility." It records neither the Decision that created it, nor the Information that informed the decision, nor the causal chain from triggering event to completion. *"The gap between the ticket and reality is filled by human memory, which is unreliable, unverifiable, and non-transferable."*

## What is actually broken (four diagnoses)

The post offers four interlocking diagnoses for why existing [[work|task management]] fails:

### 1. Tools represent work; they do not record it

A Jira ticket is a promise that work will happen; a Done status is a claim that it did. Between the two, the actual work — the code committed, the tests run, the fifteen decisions about implementation, the unexpected problem discovered and worked around — leaves no trace. The [[event-graph]] inverts this: every action is an event, hash-chained to the one before it, with causal links to the events that caused it. The ticket doesn't say Done. The chain says what was done, by whom, when, why, and what it depended on.

### 2. AI agents are invisible to existing tools

*"This is the 2026 problem that no existing tool has solved."* When an AI agent does work, it appears nowhere in Jira. The human creates the ticket, delegates to the agent, the agent acts, the human marks it Done. The agent's decisions, its reasoning, its potential errors are invisible.

On the Work Graph, AI agents are nodes in the same event graph as humans, subject to the same accountability structure ([Searles-WorkGraph]):

> "An AI agent that writes code produces events — what it wrote, what prompt informed it, what constraints it operated under, what authority approved its actions. If it makes a mistake, you can walk the chain backwards and see exactly where the error entered and why. The AI is not a god above the graph. It's a node in it."

The architectural decision is explicit: humans and AI agents are both Actors on the same graph, differentiated by Capacity and Authority, not by kind. An agent with high Capacity (writes code fast) and low Authority (cannot deploy to production without approval) is a node with specific edge weights. The authority model is the same for everyone.

### 3. Tools create work about work

The overhead of task management — updating tickets, writing status reports, attending standup meetings to describe what the tool should already show, grooming backlogs, estimating story points — exists because the tools do not record what is actually happening. On the Work Graph, status is the state of the chain. Progress is the distance between the current event and the goal event. Blockers are gaps in the chain where the next event cannot fire. *"You don't need a standup to ask 'what's blocked?' The graph shows what's blocked."*

### 4. Tools die with the people who understand them

Every company accumulates institutional knowledge in people's heads. When they leave, the knowledge goes with them. *"Why does this system do it this way?" "Because Sarah set it up in 2014."* On the [[event-graph]], the reason a thing was set up a certain way is on the chain — the decision event links to the information that informed it, and that chain does not leave with the person who made the decision.

## The perverse incentive

The post generalises beyond the four broken patterns to identify why task-management tools will not fix themselves ([Searles-WorkGraph]):

> "Task management tools profit from the gap between representation and reality."

If a tool actually recorded the real chain — the real decisions, the real outcomes — it would also reveal inefficiency, gamed velocity metrics, estimation theatre, and meetings that produced no events. It would show, with verifiable evidence, what everyone already knows but cannot prove: that a significant fraction of organisational activity is performative rather than productive. No company buys that tool. The tool's survival depends on the representation looking better than the reality.

The event graph escapes this because it is not a tool. It is infrastructure. *"It records what happens. If what happens is inefficient, the graph shows that. The graph has no business model that depends on looking good. It just shows the chain."*

## The Lovatts deployment: three phases

The Lovatts Puzzles deployment is described in three phases ([Searles-WorkGraph]):

**Phase 1 — The Spine.** An [[event-graph]] recording what happened (Action), who did it (Actor — human or AI agent), when (timestamp), why (causal link to the triggering event), and by whose authority (Authority tag). Each legacy system that produces observable outputs gets an event adapter — a thin layer that translates the system's actions into events on the graph. The legacy systems do not change. The graph observes them.

**Phase 2 — The Agents.** AI agents enter the graph as Actors: a Claude-based agent monitoring customer subscriptions, an agent generating crossword layouts, an agent handling print distribution scheduling. Each operates within the authority model — permitted scope, escalation for actions outside that scope, all actions recorded as events.

**Phase 3 — The Replacement.** Once the event graph shows how the legacy systems actually interact (not how they were designed to interact, but how they *actually* interact), replacement becomes tractable: one system at a time, each replacement itself an event on the graph with a causal link showing the migration path. If something breaks, the graph shows what and why.

> ⚠ **Fail-legible note (deployment outcome unconfirmed).** The source states "I'm deploying this week" and describes the three phases as the plan being executed. The corpus does not contain a follow-up post confirming or contradicting outcome. The deployment is grounded as an intent in active execution; its results are not in the source material.

## Company in a box

The post extends the argument from Lovatts (an established company with legacy systems) to a solo founder with a Work Graph and a Claude subscription ([Searles-WorkGraph]):

> "A solo founder with a Work Graph and a Claude subscription gets the coordination capabilities of a 50-person company."

The mechanism: define roles (marketing agent, development agent, customer support agent, finance agent) as sets of permitted Actions with defined Authority levels. Assign AI agents to the roles. The human founder is the authority root — sets goals, approves high-authority decisions, handles creative direction, ethical calls, relationship management. Everything else runs on the graph. The agents' actions are events; their decisions are traceable; their authority is bounded.

The closing claim: *"The infrastructure to do this exists right now."* The missing piece was the conceptual framework — what to record, how to structure the authority model. The [[the-200-primitives]] provide the what; the [[fourteen-layers]] provide the how; Layer 1 is the starting point.

> ⚠ **Fail-legible note ("Company in a Box" claim).** This is the author's strongest forward-looking assertion and is asserted, not demonstrated. The Lovatts deployment is the sole in-progress evidence. The claim that individual-scale operators can access 50-person-company coordination capabilities is the vision the Work Graph is built toward; it is not a result confirmed by the corpus.

## What the Work Graph does not do

The post is explicit about scope limits ([Searles-WorkGraph]):

- **Payment and exchange** — Layer 2, the Market Graph. The Work Graph records that work was done; the Market Graph records that value was exchanged for it.
- **Governance and norms** — Layer 3, the Social Graph. Team rules, process disagreements, membership management: Society primitives, not Agency ones.
- **Disputes** — Layer 4, the Justice Graph. When someone claims work was done and someone else disputes it, the evidence is on the Work Graph chain; adjudication happens on the Justice Graph.

The layering is architectural, not incidental: *"Each layer bootstraps the next. The Work Graph produces events. Those events become inputs for the layers above. Build Layer 1, and Layers 2–4 become buildable — because the data they need already exists on the graph."*

## Relationship to the rest of the arc

The Work Graph is the only one of the [[thirteen-graphs]] described as actually being built in the source. It is:

- The first view over the [[event-graph]] — it uses the append-only, hash-chained, causally-linked store as its substrate, adding no new data structure, only foregrounding the Agency primitives.
- The concrete realisation of the [[the-20-primitives|diagnostic traversal / traceability]] strand: every action produces a receipt, the chain can be walked backward to root cause, failure is visible in the record rather than living in someone's head.
- The bootstrapping foundation for [[factory-order|work coordination]] in the [[dark-factory]] synthesis — the event record that makes production legible.
- The entry point into the thirteen-graph sequence: [[work]] → Market → Social → Justice → Research → Knowledge → Ethics → Identity → (names disputed above layer 8, see [[thirteen-graphs]]).

The author's verification method, closing the post: *"If it works, the event graph will show it working. If it fails, the event graph will show where it failed and why. That's the whole point: not 'trust me, it's working.' Check the chain."*

## Sources & provenance

Compiled from `raw/searles/all-posts-1.md`:
- Post 14, *"The Work Graph"*, 2026-03-01 · [Searles-WorkGraph] · https://mattsearles2.substack.com/p/the-work-graph — all substantive claims: the twelve Agency primitives, the four broken-patterns diagnoses, the perverse-incentive argument, the three-phase Lovatts deployment, the "Company in a Box" claim, and the explicit scope limits (what the Work Graph does not do). Approximately lines 2864–3008.
- Post 11 (post 14's own numbering), *"Thirteen Graphs, One Infrastructure"*, 2026-03-01 · [Searles-13Graphs] · https://mattsearles2.substack.com/p/thirteen-graphs-one-infrastructure — overview context; the "I'm building the Work Graph this week, deploying it at a real company" commitment; scoping of the first three layers as "buildable now." See [[thirteen-graphs]].

**Conflicts and cautions:** (1) Deployment outcome is unconfirmed — the post describes intent and method, not result. (2) The "trivial technology" framing ("hash chains are trivial to implement") is inherited from [Searles-13Graphs] and contradicted in practice by the concurrency cost documented in [[event-graph]]. (3) The exact line between Layer 1 (Agency) and Layer 3 (Social / governance) will surface in real deployments where teams need both; the post draws the boundary cleanly but notes it is permeable. `[[wikilinks]]` are forward references; most targets are not yet compiled.
