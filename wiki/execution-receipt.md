---
entity: ExecutionReceipt (Proof of Work)
aliases: [ExecutionReceipt, execution receipt, authority.execution.receipt, AuthorityExecutionReceiptContent, ExecutionReceiptID]
tier: architecture
status: compiled
last_compiled: "2026-06-14"
sources:
  - transpara-ai/hive  # pkg/hive/phase3_records.go — AuthorityExecutionReceiptContent struct, EventTypeAuthorityExecutionReceipt
  - transpara-ai/hive  # pkg/hive/authority_policy.go — recordAuthorityExecutionReceipt, protectedActionLocalEmulationResult.ExecutionReceiptID
  - transpara-ai/hive  # pkg/hive/phase3_records.go — PolicyEngineAdapterDecisionContent.ExecutionReceiptRef
  - transpara-ai/hive  # pkg/loop/commit_verification.go — handleOperateResult, attachOperateArtifact, commitVerdict taxonomy
  - wiki/wiki/runtime-broker.md  # RuntimeResult fields: artifact_refs, command_log, policy_decision_refs
  - wiki/wiki/authority-layer.md  # "every action has a receipt" as a design principle
  - wiki/wiki/the-mind-loop.md  # "every action leaves a trail"; mind.claude.completed as receipt pattern
confidence:
  sources: primary
  claims: grounded
---

# ExecutionReceipt (proof of work)

**The artifact an agent emits to prove that an approved action ran and what it produced.** An `ExecutionReceipt` closes the protected-action lifecycle that begins with an [[authority-request]]: the request is the ask, the decision is the authorization, and the execution receipt is the tamper-evident record that execution happened, by whom, against what target, and with what result.

In the hive codebase the receipt is `AuthorityExecutionReceiptContent`, recorded as event type `authority.execution.receipt` in [[event-graph]]. It causally links to both the `authority.request.recorded` event and the `authority.decision.recorded` event that authorized it, forming a three-node causal chain: request → decision → receipt. This chain is the audit primitive — walk it to reconstruct *who asked*, *who approved*, and *what ran*.

## The receipt struct

`AuthorityExecutionReceiptContent` (`pkg/hive/phase3_records.go`):

```go
type AuthorityExecutionReceiptContent struct {
    RequestID           types.EventID   // back-link to authority.request.recorded
    DecisionEventID     types.EventID   // back-link to authority.decision.recorded
    ExecutingActor      types.ActorID   // who ran the action
    Operation           string          // machine-readable operation label
    TargetStateBefore   string          // state snapshot before execution
    TargetStateAfter    string          // state snapshot after execution
    ResultStatus        string          // "succeeded", "failed", etc.
    FailureDetails      string          // populated on failure; empty on success
    ProducedResourceIDs []string        // artefacts produced (e.g. PR URL, artifact refs)
    CausalEventIDs      []types.EventID // additional causal edges for the graph
}
```

The `TargetStateBefore` / `TargetStateAfter` pair is what makes the receipt more than a completion ping: it records an observable state transition, so verification can check not just "did execution happen" but "did it move the world in the declared direction." For a PR creation, for example, these fields would carry pre- and post-PR state. For a capability activation, they would carry the activation state change.

## Where it sits in the lifecycle

The four Phase 3 records that constitute one protected-action lifecycle:

| Event type | Record | Role |
|---|---|---|
| `authority.request.recorded` | `AuthorityRequestRecordedContent` | The ask |
| `authority.decision.recorded` | `AuthorityDecisionRecordedContent` | The human decision |
| `policy.engine.adapter.decision` | `PolicyEngineAdapterDecisionContent` | Policy-engine evidence |
| `authority.execution.receipt` | `AuthorityExecutionReceiptContent` | **Proof of work** |

The policy engine decision record carries an `ExecutionReceiptRef` (`*types.EventID`) that forward-links to the receipt once it is written, enabling the policy-engine evidence and the execution outcome to be joined without scanning the whole graph.

The `protectedActionLocalEmulationResult` struct (`pkg/hive/authority_policy.go`) collects all four event IDs together:

```go
type protectedActionLocalEmulationResult struct {
    RequestID                  types.EventID
    DecisionEventID            types.EventID
    PolicyAdapterDecisionID    types.EventID
    ExecutionReceiptID         types.EventID  // the receipt
    Blocker                    string         // non-empty if any stage was blocked
    RealSideEffectExecuted     bool
    RepositoryMutationExecuted bool
}
```

`Blocker` is the fail-closed signal: any non-empty `Blocker` string means the lifecycle was interrupted before the receipt could be written. A blocked result carries `ExecutionReceiptID` as zero — no receipt exists — which is the observable evidence that something intervened.

## How the receipt is created

`recordAuthorityExecutionReceipt` (`pkg/hive/authority_policy.go`, approximately L372-394):

```go
content := AuthorityExecutionReceiptContent{
    RequestID:           requestID,
    DecisionEventID:     decisionID,
    ExecutingActor:      actorID,
    Operation:           string(req.Action),
    TargetStateBefore:   req.TargetStateBefore,
    TargetStateAfter:    req.TargetStateAfter,
    ResultStatus:        "succeeded",
    ProducedResourceIDs: req.ProducedResourceIDs,
    CausalEventIDs:      req.CausalEventIDs,
}
ev, err := r.graph.Record(EventTypeAuthorityExecutionReceipt, r.humanID, content,
    []types.EventID{requestID, decisionID, policyID}, r.convID, r.signer)
```

Three event IDs are passed as `causes` — the request, decision, and policy-adapter decision — so the receipt's causal parents span the entire prior chain. The receipt cannot exist without all three; if any earlier record failed to write, `recordProtectedActionLocalEmulation` returns a blocked result and `recordAuthorityExecutionReceipt` is never called.

## The Operate path: commits as receipts

For the loop's `Operate` calls (the primary agentic execution path), receipt production takes a different but parallel form — not a `authority.execution.receipt` event but a commit-verification artifact and a `work.task.artifact.recorded` event appended to [[event-graph]].

`handleOperateResult` (`pkg/loop/commit_verification.go`) classifies the Operate outcome into one of five verdicts:

```
commitAdvanced    — HEAD moved forward; a real commit was made. Task completes.
commitDirtyTree   — uncommitted changes remain; refused.
commitUnreadable  — post-Operate HEAD could not be read; refused.
commitNoEffect    — HEAD unmoved, tree clean; refused (no-op cannot be distinguished
                    from a wrong-repo run via untrusted summary alone).
commitNonAdvancing — HEAD moved but is not a descendant of pre-Operate HEAD;
                    refused (reset/rewrite detected).
```

Only `commitAdvanced` results in task completion. Every other verdict fails the task and escalates — the Operate receipt is produced only on `commitAdvanced`, and it carries the commit range (`baseHead..postHead`) so downstream review sees every commit the Operate produced, not just the latest.

> ⚠ **Fail-legible note: `commitNoEffect` is refused, not accepted.** An Operate that produces no change to the target repo is refused and escalated even if the agent's summary *claims* a commit was made — "three review rounds confirmed every phrase/verb heuristic is bypassable" (`workspace_containment.go`). The refusal is a consequence of applying the fail-closed principle to receipt production: if the observable state does not confirm a real commit, the receipt cannot be produced on the strength of a text summary alone.

## Workspace containment as receipt integrity

The workspace containment tripwire (`pkg/loop/workspace_containment.go`) is receipt infrastructure: it snapshots the observed git state of all sibling checkouts before an Operate and compares them after. If any watched sibling changed, the Operate fails even if the agent's workspace looks correct. This closes the escape hatch where an agent commits to a *sibling* checkout — a mutation that would never appear in the correct workspace's receipt — and then claims task completion. Without the tripwire, the receipt would attest to work in the wrong place with no observable signal that anything had gone wrong.

## What a receipt is not

An execution receipt is **evidence**, not **authorization**. The receipt records that an approved action ran; it does not grant any capability or advance the agent's authority. In the [[runtime-broker]] model, `RuntimeResult` (the broader execution result) is explicitly described as "evidence fed into gates — TraceCompletenessGate, security gates, the proof-of-work packet — not a release verdict." The receipt is the same: it feeds the verification layer; it is not the verification layer.

## Related entities

[[authority-request]] (the request the receipt closes) · [[authority-layer]] (the philosophical model) · [[bounded-runtime]] (the envelope whose execution the receipt evidences) · [[runtime-broker]] (the broker that writes RuntimeResult alongside the receipt) · [[the-mind-loop]] (the originating "every action leaves a trail" principle) · [[event-graph]] (where the receipt is appended)

## Sources & provenance

Primary source (read this run):

- `transpara-ai/hive` `pkg/hive/phase3_records.go` — `AuthorityExecutionReceiptContent` (L429-446), `EventTypeAuthorityExecutionReceipt` (L29), `PolicyEngineAdapterDecisionContent.ExecutionReceiptRef` (L422).
- `transpara-ai/hive` `pkg/hive/authority_policy.go` — `protectedActionLocalEmulationResult` (L51-58), `recordProtectedActionLocalEmulation` (L87-168, specifically the receipt call at L162-166), `recordAuthorityExecutionReceipt` signature and cause-chain construction (L372-394 approx).
- `transpara-ai/hive` `pkg/loop/commit_verification.go` — `commitVerdict` taxonomy (L13-50 approx), `handleOperateResult` (L173-216 approx), `failOperateTask` (L281 approx), `attachOperateArtifact` (L1761 approx in loop.go), `buildOperateArtifactBody` (L1791 approx in loop.go). Commentary verbatim: "three review rounds confirmed every phrase/verb heuristic is bypassable."
- `transpara-ai/hive` `pkg/loop/workspace_containment.go` — v10-F2 containment tripwire, threat model commentary (L14-45).
- `wiki/wiki/runtime-broker.md` — `RuntimeResult` as evidence-not-verdict; `artifact_refs`, `policy_decision_refs`, `post_run_validation_refs` fields.
- `wiki/wiki/the-mind-loop.md` — "every action leaves a trail"; `mind.claude.completed` as the originating receipt pattern.
- `wiki/wiki/authority-layer.md` — "every action has a receipt" as a design principle.

No source conflicts found on this entity. `[[wikilinks]]` to `[[authority-request]]` and `[[bounded-runtime]]` are forward references compiled in the same session.
