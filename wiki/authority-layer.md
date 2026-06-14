---
entity: The Authority Layer (Graduated Consent)
aliases: [authority layer, graduated consent, the consent layer, the authority gate, Required/Recommended/Notification]
tier: foundational
status: compiled
last_compiled: 2026-06-13
sources:
  - raw/searles/all-posts-1.md  # "The Architecture of Accountable AI", 2026-02-28 [Searles-P3] — primary; defines the three levels, the Policy struct, and self-approval
  - raw/searles/all-posts-1.md  # "The Pentagon Just Proved Why AI Needs a Consent Layer", 2026-02-28 [Searles-P4] — the "graduated consent" framing and the trust-vs-structure motive
  - "Dark Factory - Motive, Goal, Approach.md"  # first-party framing; its own four-outcome authority model (a divergence, flagged below)
durable_urls:
  - https://mattsearles2.substack.com/p/the-architecture-of-accountable-ai          # [Searles-P3]
  - https://mattsearles2.substack.com/p/the-pentagon-just-proved-why-ai-needs        # [Searles-P4]
  - https://github.com/mattxo/mind-zero-five                                          # [Searles-MindZeroRepo]
confidence:
  three_levels_and_policy: high — quoted verbatim as Go source inside [Searles-P3] (the `Level` constants, the 15-minute timeout, the `Policy` struct, the self-approval branch).
  code_runs_claim: asserted by the author ("running right now"). Compiled from the prose and the Go excerpts quoted in the post, not from a repository checkout; not independently verified this run. Treat the *design* as well-sourced and the *operational* claim as testimony.
  consent_primitive_layer: the post says Consent is "Layer 3 (Society)"; the same post's sibling [Searles-P4] says the authority layer "implements Consent, Due Process, and Legitimacy from the 200-primitive framework." Both are the author's own mapping, not an external check.
  searles_vs_darkfactory: the Searles authority layer has THREE levels; the first-party dark-factory doc defines FOUR authority OUTCOMES. This is a real divergence between two sources — stated in full below, not silently reconciled.
---

# The authority layer (graduated consent)

On **2026-02-28**, in the post *"The Architecture of Accountable AI,"* Matt Searles (working with Claude) described the **authority layer** of `mind-zero-five` — the second of the system's three core components, sitting between the [[event-graph]] ("what happened and why") and the autonomous mind loop ("what the AI does"). Where the event graph answers *what happened*, the authority layer answers a different question, quoted from the post: **"who said this was allowed?"**

The companion post the same day, *"The Pentagon Just Proved Why AI Needs a Consent Layer,"* gave this component its motive and its second name. There Searles calls it **"an authority layer with graduated consent"** and frames it as the structural answer to the oldest problem in governance — *"who watches the watchmen?"* — reached not through trust but through structure. (For the full system this layer lives inside, see [[accountable-ai-architecture]]; this article is the authority layer as its own entity.)

The thesis is structural, not aspirational: "Every significant action in the system requires authority. Not as a speed bump or a compliance checkbox, but as **a structural gate that cannot be bypassed**."

> ⚠ **Fail-legible: code-exists claim.** The author states the system is "running right now." This article was compiled from the post's prose and the Go excerpts quoted *inside* it, not from a checkout of `github.com/mattxo/mind-zero-five`. The **design** below is well-sourced (the code is quoted verbatim); the claim that a deployed binary currently enforces these gates is the **author's testimony**, not verified here.

## The three levels

The core of the layer is a Go `Level` string with exactly three values, quoted verbatim from the post:

```go
const (
    Required     Level = "required"     // blocks until human approves
    Recommended  Level = "recommended"  // auto-approves after timeout
    Notification Level = "notification" // auto-approves immediately
)

const RecommendedTimeout = 15 * time.Minute
```

These are "three fundamentally different relationships between human and AI decision-making":

| Level | Behaviour (post's words) | Human analogue (post's framing) |
|---|---|---|
| **Required** | "The AI proposes. A human decides. Nothing happens until a human explicitly approves or rejects." The system blocks, waits, and does not proceed. For actions where "no amount of AI confidence justifies autonomous action." | A new employee — needs approval for everything. |
| **Recommended** | "The AI proposes and says 'I think this is fine.' The human has 15 minutes to disagree. If they don't, the system proceeds." This is **graduated trust**: "silence means consent, but the human always has a window to intervene." | A trusted colleague — tells you the plan and proceeds unless you object. |
| **Notification** | "The AI acts and tells you it did." For routine operations "where oversight matters but blocking doesn't." The record and trail are still complete; "the human isn't in the loop for every heartbeat." | A senior partner — just keeps you informed. |

The post's summary of the design intent: **"Trust is graduated, not binary."** The system "doesn't treat autonomy as all-or-nothing" — it starts with tight oversight (Required) and relaxes as competence is demonstrated (Recommended → Notification), "with the ability to tighten again if something goes wrong."

The one-line description of `Recommended` as **"auto-approves after a 15-minute window"** traces to two facts in the source that must be read together: the inline comment says `// auto-approves after timeout`, and the separate constant `RecommendedTimeout = 15 * time.Minute` supplies the window. The "15 minutes" figure is stated again in prose for `Recommended` and again for the self-improvement path (below) — three concordant mentions, so this is high-confidence, not inferred.

## The policy layer: actions, approvers, and self-approval

The three levels say *how strong* a gate is. A separate `Policy` struct says *which gate applies to which action, and who can clear it* — quoted verbatim:

```go
type Policy struct {
    ID         string
    Action     string    // exact match or "*" wildcard
    ApproverID string    // who can approve this action
    Level      Level     // default authority level
}
```

"Policies map actions to approvers and authority levels." The crucial property the post stresses: the mind can self-approve some actions — **"but *only if an explicit policy grants it that right*."** The trust model itself is "configurable, auditable, and recorded in the event graph": you can see "not just what the AI did, but what permissions it had, who granted them, and when."

The self-approval mechanism is shown as code in the mind loop. When the mind wants to restart itself to pick up newly built binaries, it creates a `Required` authority request, then checks the policy:

```go
policy, err := m.auth.MatchPolicy(ctx, "restart")

if policy.ApproverID == m.actorID {
    // Self-approve: policy explicitly grants this
    m.auth.Resolve(ctx, req.ID, true)
} else {
    // Wait for human
    m.pendingRestart = req.ID
}
```

The behaviour the post draws from this is the load-bearing claim of the whole layer: **"If no policy exists that grants self-approval, the mind waits. It doesn't proceed. It doesn't find a workaround."** It sits in its loop checking each cycle whether the human has responded. "The authority gate is not advisory — it's structural."

This is the property the entity's one-line description calls *"as code that the AI cannot bypass."* It is well-sourced as a **design claim** (the wait-branch is in the quoted code), and is the author's stated guarantee about the running system; the wiki has read the excerpt, not exercised the binary.

> Note on "self-approval" as a fail-safe reading: self-approval here is *allowlisted*, not assumed. The permissive branch (`Resolve(..., true)`) executes **only** when an explicit policy names the mind as approver; the fall-through is to **wait for a human**, never to proceed. That ordering — prove the permission, otherwise deny — is the same fail-closed discipline the [[event-graph]] enforces by omitting `Update`/`Delete`.

## What it implements: the Consent primitive

The post is explicit about provenance: **"This is the Consent primitive from Layer 3 (Society), implemented as code. Legitimate action requires consent. Consent is explicit, traceable, and revocable."** The companion Pentagon post widens that mapping: the authority layer "implements **Consent, Due Process, and Legitimacy** from the 200-primitive framework."

So the lineage runs: [[the-20-primitives]] (the late-night seed already treated authority and node-action as ordinary operations) → the Consent / Due Process / Legitimacy primitives in the [[the-200-primitives]] / [[fourteen-layers]] expansion → this Go authority layer that turns those primitives into a gate. Both mappings above are the **author's own** placement of the primitives, internal to the source corpus, not an external verification.

## The motive: trust vs. structure (the Pentagon case)

The *"Pentagon"* post is why this layer is called a **consent layer** and why graduated consent matters beyond one codebase. Its real-world trigger: on **2026-02-28**, the Pentagon demanded Anthropic remove two contractual red lines (no fully autonomous weapons, no mass domestic surveillance); Anthropic refused and walked away from up to $200M and its government business; the administration ordered federal agencies to stop using Anthropic and designated it a "supply-chain risk to national security." (These are facts as the post reports them; this article did not independently verify the news events — they are the author's account.)

Searles' argument is that the dispute exposes the failure mode of **trust-based** governance, on two grounds the post states directly: "trust doesn't survive personnel changes" (a commitment from one Defense Secretary "means nothing to the next"), and "trust-based models are fundamentally unverifiable" ("trust us" means "take our word for it"). His alternative is **structure**: an authority layer that "would enforce the red lines structurally." The sharpest line: *"Autonomous lethal targeting without human approval? The system literally can't do it — the authority gate blocks until a human approves."* That is `Required` applied to the highest-stakes action — the gate as a hard floor that no institutional promise can lawyer around.

The recurring phrase across both posts for the result: **"trust that doesn't require trusting."**

## The self-improvement circuit breaker (Recommended in practice)

The clearest demonstration of `Recommended` in the post is the self-improvement loop. When the mind is idle it may assess itself and submit a proposal — at the `Recommended` level:

```go
req, err := m.auth.Create(ctx, "self-improve",
    proposalJSON,
    "mind", authority.Recommended)
```

The mind "can identify its own deficiencies. It can propose fixes. It can implement those fixes. But it *cannot skip the authority gate*." The human has 15 minutes to say no; if they don't, the mind proceeds through the normal plan → implement → review cycle, with every step recorded in the [[event-graph]]. The post's name for this: **"recursive self-improvement with a consent circuit breaker."** It is the authority layer's answer to the claim that recursive self-improvement and human oversight are mutually exclusive — "you can have both."

## Divergence: three levels (Searles) vs. four outcomes (Dark Factory)

The two source families do **not** agree on the shape of the authority model, and the disagreement is load-bearing enough to state plainly rather than reconcile:

- **Searles / `mind-zero-five` [Searles-P3]** defines **three levels**: `Required`, `Recommended`, `Notification`. There is no explicit "forbidden" level, and the most permissive option (`Notification`) still records and informs.
- **The first-party Dark Factory doc** defines **four canonical authority *outcomes*: `Autonomous`, `Notify`, `ApprovalRequired`, `Forbidden`** — "ApprovalRequired blocks until an authorized decision grants approval. Forbidden means the actor must not proceed." (`Dark Factory - Motive, Goal, Approach.md`.)

These line up only loosely: Dark Factory's `ApprovalRequired` ≈ Searles' `Required`; `Notify` ≈ `Notification`; `Autonomous` ≈ either `Recommended` *or* a self-approving policy (but Dark Factory's `Autonomous` carries **no timeout-consent window** — the distinctive 15-minute "silence means consent" mechanism is a Searles concept, not a stated Dark Factory one). And Dark Factory adds a **`Forbidden`** outcome with **no counterpart** in the three Searles levels.

This is consistent with how the dark-factory doc positions the Searles corpus generally: it is "source material, **not implementation authority**" — it "provides the originating … authority, consent … framing," but "accepted implementation authority still comes from merged docs, accepted packets, repository artifacts, review evidence, and human authorization." So the three-level model is the *philosophical* ancestor; the four-outcome model is the *implemented governance contract* in the later system. Neither source claims they are identical, and this article does not assert they are.

> Confidence: **thin on the exact mapping.** The "≈" correspondences above are this article's reading of two documents that use different vocabularies; neither source explicitly cross-maps its levels/outcomes to the other. The *fact* of two different shapes (3 vs. 4) is well-sourced; the precise alignment between them is interpretive and labelled as such.

## Why this entity is foundational

Across both posts the authority layer is named as one of the **three things that make AI accountable by design**, alongside the append-only [[event-graph]] and the verifiable audit trail. Its specific contribution is the move from *binary* autonomy ("the AI can / can't act") to *graduated* consent — a spectrum from "blocks until a human approves" to "acts and informs" — with a policy table deciding where on that spectrum each action sits and a self-approval rule that is allowlisted, not assumed. It is the structural form of the principle the whole arc keeps returning to: legitimate action requires consent, and the gate that enforces it must be one the AI itself cannot open.

## Sources & provenance

Primary: `raw/searles/all-posts-1.md` —
- *"The Architecture of Accountable AI"* (2026-02-28 · [Searles-P3] · https://mattsearles2.substack.com/p/the-architecture-of-accountable-ai) — the "The Authority Layer" section: the three `Level` constants, `RecommendedTimeout = 15 * time.Minute`, the `Policy` struct, the `MatchPolicy`/self-approval branch, the self-improvement circuit breaker, and the Consent-primitive (Layer 3) mapping.
- *"The Pentagon Just Proved Why AI Needs a Consent Layer"* (2026-02-28 · [Searles-P4] · https://mattsearles2.substack.com/p/the-pentagon-just-proved-why-ai-needs) — "an authority layer with graduated consent," the trust-vs-structure argument, the red-lines-enforced-structurally framing, and the Consent/Due Process/Legitimacy mapping.

First-party divergence source: `Dark Factory - Motive, Goal, Approach.md` — the four canonical authority outcomes (`Autonomous`, `Notify`, `ApprovalRequired`, `Forbidden`; line ~173) and the standing position that the Searles corpus is source philosophy, not implementation authority (lines ~377, ~382). Repo reference `github.com/mattxo/mind-zero-five` ([Searles-MindZeroRepo]) is cited as the code's location, not read this run.

Durable Searles URLs are taken from the citation table inside `Dark Factory - Motive, Goal, Approach.md`. `[[wikilinks]]` are forward references; some targets (e.g. [[the-200-primitives]], [[fourteen-layers]]) may not yet be compiled. The numbered "Post N" ordinals in the source file are omitted here to avoid the numbering ambiguity noted in [[accountable-ai-architecture]]; sources are cited by title.
