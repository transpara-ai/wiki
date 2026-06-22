---
entity: Bounded Runtime (Execution Envelope)
aliases: [bounded runtime, BoundedRuntime, bounded-runtime, CanOperate, Loop Config, execution envelope, workspace containment, BudgetConfig]
tier: architecture
status: compiled
last_compiled: "2026-06-14"
sources:
  - transpara-ai/hive  # pkg/loop/loop.go — Config struct (CanOperate, RepoPath, Budget, ContainmentWatchRoots, Keepalive, MaxIterations)
  - transpara-ai/hive  # pkg/resources/budget.go — BudgetConfig struct (MaxTokens, MaxCostUSD, MaxIterations, MaxDuration)
  - transpara-ai/hive  # pkg/loop/workspace_containment.go — containment tripwire, v10-F2, threat model commentary
  - transpara-ai/hive  # pkg/loop/spawner.go — SpawnCommand.CanOperate, blocked-for-spawned-agents rule
  - transpara-ai/hive  # pkg/loop/commit_verification.go — commitVerdict taxonomy; Operate receipt discipline
  - transpara-ai/hive  # pkg/loop/operate_instruction.go — composeOperateInstruction (WorkDir, Instruction, AllowedTools)
  - transpara-ai/eventgraph  # go/pkg/decision/intelligence.go — OperateTask, OperateResult, IOperator interface
  - wiki/wiki/runtime-broker.md  # normative spec: RuntimeEnvelope fields, enforcement stages, adapter conformance
  - wiki/wiki/the-mind-loop.md  # "agent action becomes bounded runtime invocation"; dark-factory crosswalk
  - wiki/wiki/authority-layer.md  # authority gate as the pre-flight check the envelope binds to
confidence:
  sources: primary
  claims: grounded
---

# Bounded runtime (execution envelope)

**The execution envelope that contains an agent's operation — its scope, duration, and resource limits.** A bounded runtime is the set of constraints that govern one unit of agentic work: which directory the agent may touch, what tools it may invoke, how many tokens and wall-clock seconds it may consume, and what authority decision it is acting under. The agent works inside the envelope; the envelope's edges are enforced before, during, and after the work; the result is accepted only when verification confirms the envelope was not exceeded.

The concept appears first in the [[the-mind-loop]] Searles post as a design intention — "agent action becomes bounded runtime invocation" — and is realized in the dark-factory hive codebase as the combination of `Config` (the loop's declaration of its envelope), `BudgetConfig` (the resource limits), and the workspace containment tripwire (the runtime enforcement that detects envelope violations). The [[runtime-broker]] specification describes a more comprehensive `RuntimeEnvelope` YAML structure that the hive loop's implementation partially instantiates; where they diverge is noted below.

> ⚠ **Fail-legible note on naming.** The string "BoundedRuntime" does not appear as a named Go type in the hive or eventgraph repos as read this run. The concept is implemented through a constellation of types (`Config`, `BudgetConfig`, `OperateTask`, the containment tripwire) rather than a single struct named `BoundedRuntime`. The `[[runtime-broker]]` article previously noted `BoundedWorker` as an alias from the v3.9 spec; the hive code uses different vocabulary. Claims below are grounded in the code that was read; the "bounded runtime" name is a design-level term from the dark-factory documentation, not a Go identifier in this repo.

## The `CanOperate` gate

The most important field in the loop's `Config` is the binary gate `CanOperate bool`:

```go
// CanOperate indicates this agent has filesystem access.
// When true and the agent has assigned tasks, the loop calls
// Operate() instead of Reason() for implementation work.
CanOperate bool

// RepoPath is the working directory for Operate() calls.
// Required when CanOperate is true.
RepoPath string
```

`CanOperate: false` is the default for every spawned agent. The spawner enforces this without exception:

```go
// 9. CanOperate blocked for all spawned roles.
if cmd.CanOperate {
    return validateSpawnCommandError("CanOperate must be false for spawned agents; trust must be earned first")
}
```

The comment states the design intent directly: "trust must be earned first." An agent that can operate has filesystem access; that access is not granted by a role prompt — it is granted by the human operator at loop-construction time, not at spawn time. Spawned agents are restricted to `Reason()` (LLM inference with no side effects) until they are explicitly elevated by a human-controlled configuration.

## The `OperateTask` envelope (per-call scope)

When `CanOperate` is true and the loop calls `operateTask`, it passes a `decision.OperateTask` to the underlying `IOperator`:

```go
// OperateTask describes an agentic task with filesystem access.
type OperateTask struct {
    WorkDir      string   // directory the agent operates in
    Instruction  string   // what to do (natural language)
    AllowedTools []string // which tools to grant (Read, Edit, Write, Bash, etc.)
}
```

`AllowedTools` is the tool-level allowlist inside the envelope: the agent may only invoke tools explicitly listed here. This is the hive code's implementation of the [[runtime-broker]] spec's `allowed_commands` concept — an explicit grant, not a denylist of what to forbid.

`WorkDir` bounds the filesystem scope to a single directory. The workspace containment tripwire (below) enforces that this bound is respected.

## Budget: the resource envelope

`BudgetConfig` (`pkg/resources/budget.go`) declares the resource limits for one loop run:

```go
// BudgetConfig configures resource limits. Zero values mean unlimited.
type BudgetConfig struct {
    MaxTokens     int           // total tokens across all iterations
    MaxCostUSD    float64       // total cost in USD
    MaxIterations int           // maximum loop iterations
    MaxDuration   time.Duration // maximum wall-clock time
}
```

Zero means unlimited for each dimension independently. In practice, a bounded loop sets at least one non-zero limit. The budget is one of the five stop reasons the loop tracks: `StopBudget` fires when any limit is reached, halting the agent cleanly rather than letting it run indefinitely. The other four stop reasons are `StopQuiescence` (nothing to do), `StopEscalation` (authority gate hit), `StopHalt` (Guardian halted the agent), and `StopError`/`StopCancelled`.

Budget enforcement is the temporal and economic dimension of the envelope; `CanOperate`/`WorkDir`/`AllowedTools` is the spatial and capability dimension.

## The containment tripwire (runtime enforcement)

`CanOperate: true` and a `RepoPath` declare the intended scope; the workspace containment tripwire (`pkg/loop/workspace_containment.go`) *verifies* it:

> "Workspace containment (v10-F2 / Finding 18): the -repo workspace assignment alone does not contain a filesystem-capable Operate — the v10 round-3 implementer simply walked to the sibling main checkout. This tripwire snapshots the watched sibling checkouts around the Operate and fails the run on any observed checkout-state delta."

The tripwire snapshots four state vectors for every immediate-child git checkout under the `ContainmentWatchRoots` before an Operate, then compares them after:

- `HEAD` (rev-parse HEAD)
- `branch` (current branch name — catches branch switches that return HEAD to the same hash)
- `status --porcelain` (uncommitted-change fingerprint)
- checkout presence (a deleted or created checkout counts as a delta)

Any delta on any sibling fails the Operate and escalates to the human before the agent's summary can drive anything further. The code is explicit about scope and honesty:

> "SCOPE / THREAT MODEL — detection with run-failing teeth, NOT prevention and NOT an OS sandbox. A Bash-capable subprocess can still write anywhere its uid can; what it can no longer do is have work accepted after mutating a WATCHED state vector."

The containment watch has no disable switch: "a `CanOperate` loop is always watched" (Config comment, L137-138). This is the fail-closed posture applied to scope enforcement — the tripwire cannot be opted out of.

A residual honesty note from the code: "PARALLELISM HONESTY: the tripwire attributes any watched-sibling delta to THIS loop's Operate. Two concurrent Operates in sibling workspaces would cross-trip each other. Slice-1 society runs launch a single Operate at a time; parallel FactoryOrders (G-7.x) must move attribution into the runtime — which sees every live run's workspace — before launching concurrent Operates."

## The Operate outcome as receipt

An Operate that exits the bounded runtime cleanly produces a verifiable outcome. `handleOperateResult` classifies the result into five verdicts:

| Verdict | Condition | Action |
|---|---|---|
| `commitAdvanced` | HEAD moved forward to a true descendant of pre-Operate HEAD | Task completes; artifact appended to graph |
| `commitDirtyTree` | Uncommitted changes remain in workspace | Task fails; escalated |
| `commitUnreadable` | Post-Operate HEAD could not be read | Task fails; escalated |
| `commitNoEffect` | HEAD unmoved, tree clean | Task fails; escalated (no-op indistinguishable from wrong-repo run) |
| `commitNonAdvancing` | HEAD moved but not forward (reset/rewrite) | Task fails; escalated |

Only `commitAdvanced` produces an [[execution-receipt]]. Every other path fails the bounded runtime and produces no receipt — the absence of a receipt is the signal that the envelope was not satisfied.

## Relationship to the `RuntimeEnvelope` spec

The [[runtime-broker]] v3.9 specification describes a more comprehensive `RuntimeEnvelope` with explicit fields for `allowed_files`, `denied_files`, `network_policy`, `secrets_policy`, `resource_limits`, `expected_outputs`, `output_contract`, `trace_required_paths`, and `post_run_validation_plan`. The hive loop's current implementation covers a subset:

| Spec field | Hive implementation |
|---|---|
| `task_id` | Carried through `work.Task` in loop context |
| `actor_id` | `Agent` identity in loop `Config` |
| `authority_decision_ref` | Linked through [[authority-request]] lifecycle |
| `allowed_commands` | `OperateTask.AllowedTools` |
| `working_directory` | `OperateTask.WorkDir` / `Config.RepoPath` |
| `timeout` + `resource_limits` | `BudgetConfig.MaxDuration` + `MaxTokens`/`MaxCostUSD`/`MaxIterations` |
| File-system boundary enforcement | Containment tripwire (detect, not prevent) |
| Network policy, secrets policy | ⚠ Not yet implemented in hive loop as of source read |
| Full eleven-stage enforcement pipeline | ⚠ Specified in v3.9; partially implemented |

> ⚠ **Fail-legible note on spec vs. implementation gap.** The fields marked above as not yet implemented were not found in the hive loop source read this run. The [[runtime-broker]] article flags the same gap: "Specified in full — envelope fields, enforcement stages … whether any adapter has passed the conformance checklist … is not proven here." Claims about what the hive loop *does implement* are grounded in the Go source read directly; claims about the full `RuntimeEnvelope` spec come from the v3.9 normative docs via the `[[runtime-broker]]` article.

## How the mind-loop crosswalk lands here

The [[the-mind-loop]] Searles design names the loop's Operate phase as the runtime unit. The dark-factory motive doc maps this forward: *"agent action becomes bounded runtime invocation."* In the hive implementation, that mapping resolves to:

- **"Agent action"** → an `IOperator.Operate(ctx, OperateTask)` call
- **"Bounded"** → `CanOperate: true` gate, `WorkDir`, `AllowedTools`, `BudgetConfig`, and the containment tripwire
- **"Runtime invocation"** → the full loop iteration that calls `operateTask`, verifies the outcome, and appends the artifact to [[event-graph]]

The design principle is the same as in the original mind loop: intelligence is one operation type, subject to the same success/failure criteria and authority requirements as everything else (see [[intelligence-is-an-operation-type]]). The bounded runtime is the mechanism that enforces this — the agent's LLM calls are just another bounded process, not an unbounded authority.

## Related entities

[[authority-request]] (the `authority_decision_ref` the envelope binds to) · [[execution-receipt]] (the artifact the bounded runtime produces on success) · [[runtime-broker]] (the full specification; the eleven-stage enforcement pipeline) · [[the-mind-loop]] (the originating design; "agent action becomes bounded runtime invocation") · [[authority-layer]] (the graduated-consent model the pre-flight check connects to) · [[event-graph]] (where receipts and artifact records are appended)

## Sources & provenance

Primary source (read this run):

- `transpara-ai/hive` `pkg/loop/loop.go` — `Config` struct (L78-174 approx; `CanOperate` L124-127, `RepoPath` L129-131, `ContainmentWatchRoots` L133-138, `Budget` L86-87); `StopReason` constants (L44-53); `operateTask` (L1008-1022).
- `transpara-ai/hive` `pkg/resources/budget.go` — `BudgetConfig` (L37-43).
- `transpara-ai/hive` `pkg/loop/workspace_containment.go` — threat model and scope commentary (L14-45), `containmentRoots` (L61-68), `repoContainmentState` struct (L47-52), `verifyOperateContainment` (L191 approx).
- `transpara-ai/hive` `pkg/loop/spawner.go` — `SpawnCommand.CanOperate` (L26), "CanOperate blocked for all spawned agents; trust must be earned first" (L262-264).
- `transpara-ai/hive` `pkg/loop/commit_verification.go` — `commitVerdict` taxonomy (L13-50 approx), `handleOperateResult` (L173 approx).
- `transpara-ai/eventgraph` `go/pkg/decision/intelligence.go` — `OperateTask` struct (L47-51), `OperateResult` struct (L54-57), `IOperator` interface (L60-65).
- `wiki/wiki/runtime-broker.md` — `RuntimeEnvelope` field set (L36-53); eleven enforcement stages (L72); `BoundedWorker` / `RuntimeResult` schema; adapter conformance posture.
- `wiki/wiki/the-mind-loop.md` — "agent action becomes bounded runtime invocation" (L128); `CanOperate`-false for spawned agents corroborated in operational record.
- `wiki/wiki/authority-layer.md` — graduated consent; self-approval allowlist pattern.

One naming tension noted and not silently resolved: the dark-factory docs use `BoundedRuntime` / `BoundedWorker` / `RuntimeEnvelope` as design-level terms; the hive Go codebase implements the concept through `Config`, `BudgetConfig`, `OperateTask`, and the containment tripwire without using those identifiers. Both are noted above; no merger is implied. `[[wikilinks]]` to `[[authority-request]]` and `[[execution-receipt]]` are forward references compiled in the same session.
