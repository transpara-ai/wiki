---
entity: AuthorityRequest (Gated Consent Object)
aliases: [AuthorityRequest, authority request, authority.request.recorded, AuthorityRequestRecordedContent, protectedActionRequest]
tier: architecture
status: compiled
last_compiled: "2026-06-14"
sources:
  - transpara-ai/hive  # pkg/hive/phase3_records.go — AuthorityRequestRecordedContent struct, EventTypeAuthorityRequestRecorded
  - transpara-ai/hive  # pkg/hive/authority_policy.go — protectedActionRequest, recordAuthorityRequest, authorizeProtectedAction
  - transpara-ai/hive  # pkg/safety/safety.go — ProtectedAction constants, DefaultOutcome, RiskClass
  - transpara-ai/hive  # pkg/hive/factory_authority.go — RaiseDraftPRAuthorityRequest, DraftPRTarget
  - wiki/wiki/authority-layer.md  # philosophical lineage: graduated consent, Required/Recommended/Notification
  - wiki/wiki/runtime-broker.md  # authority_decision_ref in the RuntimeEnvelope
  - wiki/wiki/the-mind-loop.md  # Create/MatchPolicy/Resolve pattern; m.auth.Create("restart", ..., authority.Required)
confidence:
  sources: primary
  claims: grounded
---

# AuthorityRequest (gated consent object)

**The object that stops an agent at a protected boundary and waits.** An `AuthorityRequest` is the concrete representation of a request for authorization at a protected action boundary in the dark-factory runtime. Where the [[authority-layer]] is the *philosophy* of graduated consent — who must agree before an AI may act — the `AuthorityRequest` is the *artifact* that embodies one specific ask: a named agent, requesting a named action, against a named target, with justification and risk evidence attached, blocked until a matching `AuthorityDecision` resolves it.

In the hive codebase, an `AuthorityRequest` is not a single type but a two-layer record: a canonical `authority.requested` event produced by the eventgraph factory, and a richer `authority.request.recorded` event that extends it with Dark Factory Phase 3 audit vocabulary. Both land in [[event-graph]] and are causally linked before any side-effecting action runs.

## Where it fits

The lineage runs: [[the-mind-loop]] → `m.auth.Create(ctx, "restart", ..., authority.Required)` → the dark-factory Phase 3 authority model → `AuthorityRequestRecordedContent`. The mind loop's original pattern used a lightweight `auth.Create` call; the hive implementation records a full Phase 3 envelope that supplies the operator dashboard, the policy engine, and the audit trail with everything needed to evaluate and evidence a decision.

In the [[runtime-broker]] design, `authority_decision_ref` is a mandatory field on every `RuntimeEnvelope` — meaning no bounded execution may start without a resolved `AuthorityRequest` in the graph behind it. The request is the gate; the decision is the key; the receipt ([[execution-receipt]]) is the proof that the key was used.

## The protected action vocabulary

`AuthorityRequest` exists only for actions in the `ProtectedActions` baseline (`pkg/safety/safety.go`). The full set as read from the source:

```go
ActionProductionDeploy           = "production.deploy"
ActionRepoCreate                 = "repo.create"
ActionRepoDelete                 = "repo.delete"
ActionRepoPushDefaultBranch      = "repo.push.default_branch"
ActionRepoMergeMain              = "repo.merge.main"
ActionRepoMutateCrossRepo        = "repo.mutate.cross_repo"
ActionAgentSpawnPersistent       = "agent.spawn.persistent"
ActionAgentRetire                = "agent.retire"
ActionAgentRevoke                = "agent.revoke"
ActionAgentKeyRotate             = "agent.key.rotate"
ActionAgentEscalatePermissions   = "agent.escalate_permissions"
ActionPolicyChange               = "policy.change"
ActionSecretAccess               = "secret.access"
ActionExternalCompanyVoice       = "external_communication.company_voice"
ActionDataDelete                 = "data.delete"
ActionSelfModificationActivate   = "self_modification.activate"
ActionBillingSpendAboveThreshold = "billing.spend_above_threshold"
ActionLicenseChange              = "license.change"
ActionReleaseCertify             = "release.certify"
ActionCapabilityPromote          = "capability.promote"
ActionCapabilityActivate         = "capability.activate"
ActionCapabilityRollback         = "capability.rollback"
ActionRuntimeInvokeExternal      = "runtime.invoke.external"
ActionMemoryIngestSensitive      = "memory.ingest.sensitive"
ActionKnowledgeActivate          = "knowledge.activate"
ActionRepoPullRequestCreate      = "pull_request.create"
```

`DefaultOutcome` is fail-closed: every action in this set returns `ApprovalRequired`; any action outside this set returns `Forbidden`. There is no default-autonomous path.

## The request struct (what gets recorded)

`AuthorityRequestRecordedContent` (Phase 3 audit envelope, `pkg/hive/phase3_records.go`):

```go
type AuthorityRequestRecordedContent struct {
    RequestID         types.EventID   // ID of the canonical authority.requested event
    RequestingActor   types.ActorID
    RequestingRole    string          // optional role label
    ActionName        string          // e.g. "pull_request.create"
    Target            string          // what is being acted on
    Environment       string
    RiskClass         string          // "high" or "critical" (from safety.RiskClass)
    RequestedOutcome  string
    Justification     string
    RiskSummary       string
    Scope             []string        // action-specific scope vector (e.g. repo/ref/SHA tuple)
    EvidenceReviewed  []types.EventID // causal evidence the requester vouches for
    ProposedOperation string
    CausalEventIDs    []types.EventID // causes for the graph edge
    ExpiresAt         types.Timestamp // optional TTL
}
```

The `Scope` field is action-specific. For `pull_request.create`, it encodes a fixed 11-element vector: `[action, repository, base_ref, base_sha, head_ref, head_sha, title_hash, body_hash, policy_bundle_id, policy_bundle_hash, single_use_nonce]`. This makes a PR authority request scope-locked: approving request R approves *exactly* the PR described by R, not "some PR on that repo."

## Risk classes

`RiskClass` (from `pkg/safety/safety.go`) partitions the protected action set into two tiers:

- **Critical:** production deploy, push/merge to default branch, cross-repo mutation, secret access, self-modification activate, external runtime invocation, memory ingest (sensitive), knowledge activate, agent permission escalation, key rotation, capability activate/rollback.
- **High:** repo create, agent spawn/retire/revoke, policy change, external company voice, data delete, billing above threshold, license change, release certify, capability promote, PR create.

Unknown actions default to `"critical"` for audit wording while `DefaultOutcome` still returns `Forbidden` for them — a fail-closed double gate.

## How a request is created and flows

The internal flow (from `authority_policy.go`, `recordAuthorityRequest`):

1. A runtime calls `authorizeProtectedAction(req)`.
2. `DefaultOutcome` is checked; `Forbidden` stops immediately. `Autonomous`/`Notify` skip the request path entirely.
3. `recordAuthorityRequest` creates the canonical `authority.requested` event via the eventgraph factory (signed, with causal links), then appends a second `authority.request.recorded` event carrying the full Phase 3 audit envelope, causally linked to the first.
4. The runtime either waits for a human decision (via the operator dashboard) or, if `approveRequests` is set, calls `recordAuthorityDecision`.
5. If approved, `recordAuthorityExecutionReceipt` closes the loop and produces an [[execution-receipt]].

The two-event design (canonical + extended) means the eventgraph's core `authority.requested` type is unchanged while the hive layer adds audit richness without altering the base schema.

## Fail-closed discipline

`DefaultOutcome` is an allowlist, not a denylist:

```go
func DefaultOutcome(action ProtectedAction) AuthorityOutcome {
    if IsProtectedAction(action) {
        return ApprovalRequired
    }
    return Forbidden
}
```

The safe outcome (deny/require-approval) is the `default`; the permissive outcome (approval required, not autonomous) is the **explicitly-enumerated branch**. Any action added to the system that does not appear in `ProtectedActions` is `Forbidden` by construction — unknown actions cannot slip through as autonomous.

## Other records in the lifecycle

An `AuthorityRequest` is the first of four Phase 3 records that together constitute one protected-action lifecycle:

| Event type | Record type | Role |
|---|---|---|
| `authority.request.recorded` | `AuthorityRequestRecordedContent` | The ask |
| `authority.decision.recorded` | `AuthorityDecisionRecordedContent` | The human decision |
| `policy.engine.adapter.decision` | `PolicyEngineAdapterDecisionContent` | Policy-engine evidence |
| `authority.execution.receipt` | `AuthorityExecutionReceiptContent` | Proof of execution |

All four are causally linked in [[event-graph]], so the full lifecycle — who asked, who decided, what the policy said, and what actually ran — is walkable from any event in the chain. See [[execution-receipt]] for the receipt record; see [[authority-layer]] for the philosophical model these records implement.

## Related entities

[[authority-layer]] (the graduated-consent model these records implement) · [[execution-receipt]] (the receipt that closes the lifecycle) · [[bounded-runtime]] (the execution envelope that binds `authority_decision_ref`) · [[runtime-broker]] (the broker that enforces the envelope) · [[the-mind-loop]] (the originating `auth.Create` pattern) · [[event-graph]] (where all four records are appended)

## Sources & provenance

Primary source (read this run):

- `transpara-ai/hive` `pkg/hive/phase3_records.go` — `AuthorityRequestRecordedContent` struct (L356-375), `AuthorityDecisionRecordedContent` (L381-399), `EventTypeAuthorityRequestRecorded` (L26), `EventTypeAuthorityExecutionReceipt` (L29), `registerPhase3ContentUnmarshalers` (L60-83).
- `transpara-ai/hive` `pkg/hive/authority_policy.go` — `protectedActionRequest` (L12-26), `authorizeProtectedAction` (L61-85), `recordProtectedActionLocalEmulation` (L87-168), `recordAuthorityRequest` (L170-219 approx), `recordAuthorityExecutionReceipt` (L372-394 approx).
- `transpara-ai/hive` `pkg/safety/safety.go` — `AuthorityOutcome` constants (L9-13), `ProtectedAction` constants (L19-46), `DefaultOutcome` (L103-110), `RiskClass` (L112-148).
- `transpara-ai/hive` `pkg/hive/factory_authority.go` — `DraftPRTarget` struct (L15-26), `Scope()` encoding (L31-44).
- `wiki/wiki/authority-layer.md` — philosophical lineage; `Required`/`Recommended`/`Notification` levels; `auth.Create` / `MatchPolicy` / `Resolve` pattern quoted from Searles.
- `wiki/wiki/runtime-broker.md` — `authority_decision_ref` as mandatory envelope field.
- `wiki/wiki/the-mind-loop.md` — the originating `m.auth.Create(ctx, "restart", ..., authority.Required)` call pattern.

No source conflicts found on this entity. `[[wikilinks]]` to `[[bounded-runtime]]` and `[[execution-receipt]]` are forward references compiled in the same session.
