---
entity: Slice 1 Completion
aliases: [round 6, v16, finished-unsignalled, first society to finish, grant-2 close]
tier: arc
status: compiled
last_compiled: "2026-06-15"
sources:
  - raw/transpara/dark-factory/reunification/2026-06-12-arc-state.md  # DF-REUNIFY-2026-06-12-ARC-STATE v0.3.0 — post-round-6 state table, v16 findings, Grant-2 accounting
  - raw/transpara/dark-factory/reunification/2026-06-11-slice-1-take-4-round-log.md  # DF-REUNIFY-2026-06-11-SLICE-1-TAKE-4-ROUND-LOG v0.5.0 — round 6 timeline, fix-set proofs, findings F1/F2/F3
  - raw/open-brain/2026-06.md  # Open Brain June 2026 export — lines 3796–3910, round 6 live captures
  - wiki/the-reunification.md  # context for the workstream
confidence:
  sources: primary
  claims: grounded
---

# Slice 1 completion

**The first society to finish a factory order.** Round 6 (v16) of [[the-reunification]] slice-1 arc closed on **2026-06-12** as `finished-unsignalled` — a new close class coined for a state the system had no concept for: the [[hive-governance]] civilization completed all its assigned work, then froze in terminal quiescence because nothing told it to stop.

The chain sealed at **1128 events** after 45 minutes of flight. No prior epoch had reached this state: v13 died silent at 5 minutes, v14 was visible at 27 minutes, v15 was productive at 31 minutes and delivered an artifact — but none of them finished. The v16 society finished, and that exposed the gap.

## The run

**Launch:** 11:28 on 2026-06-12. Binary `2fe5b2f` (hive#157, the v15 fix set) + eventgraph `3a0bf8c` + agent `4635120`. Fresh store `hive_df_slice1_v16`. Fresh worktree `df-impl-v16` on docs main `3371d5b`. Seeded via `hive factory order` (seq 1–3). The daemon and sentinel ran **nohup** — the v15 meta-lesson applied. The operator session crashed at ~11:29 right after the launch report; the nohup pair ran the round unattended, and recovery at ~11:44 found the chain advanced (seq 113 → 314) with two WAKEs banked in the durable alert file.

| Time | Event |
|---|---|
| 11:28 | Boot; 9 agents; sentinel armed at seq 91 |
| ~11:31 | Planner decomposes the FO → subtask `019ebb62` scoped to runtime-source roles only (v16-F2 born here, before any review) |
| 11:36 | Implementer commits the 24-role catalog `1b5032a`; FO task completes (seq 202); strategist exits `task_done` |
| 11:44 | **First review of the arc** (seq 271) — 16 min into the epoch; F3 alone sufficed |
| 11:44–12:09 | Dual-spec oscillation: 6 completions in `5f/62` alternation, 6 stacked commits `1b5032a → 7fcee9e → d0faf3a → 9ac1751 → b638a44 → 002bcf8` (24 → 9 → 24 → 9 → 24 → 9 roles) |
| ~11:58 | Allocator preemptively renews spawner (+150 → 180 m): anticipation beyond the taught contract |
| 12:00 | v15 deadlock replays and does not deadlock: 5 agents park in ~35 s; 5/5 raise `agent.budget.exhausted` on-chain; allocator wakes and renews all five, sufficiency math verbatim in reason strings |
| 12:0x | Review-cap breaker fires on both tasks (3 reviews each, 6 total vs 0 across five prior epochs); escalations demand "Human/CTO judgment" |
| 12:09 | Implementer exits `task_done` (10 iterations) — last work-generator leaves |
| 12:13 | Final events (knowledge distiller); every loop enters pure wake-block; **terminal quiescence** — chain sealed at 1128 events; daemon alive at ~0% CPU, frozen by design |

**Budget:** $0.00 metered across the entire arc (claude-cli subscription).

## What the v15 fix set proved live

This was the round's primary purpose — every fix had to run in production:

- **F1(a):** 6/6 parks raised `agent.budget.exhausted` on-chain; zero raise failures.
- **F1(b/c):** Allocator woke, rechecked, and renewed every parked agent (8 adjustments, duration pool 2000 → 1877), plus one preemptive renewal and one adaptive re-up ("CRITICAL … Tier A agent" +60 → 100 m) — behaviors beyond the taught contract. Sufficiency math verbatim in reason strings.
- **F3:** Six reviews vs zero ever before; first review at 16 minutes on the original 30-minute lifespan.
- **F2:** Six stacked commits under maximal rework pressure, including direct adversarial instruction (from v16-F1's phantom reviewer) to create a branch in the wrong repo. The git discipline held every time.

## Findings unmasked by the fix set

None of the v16 findings were caused by the v15 fix set — they were **unmasked** by it. Prior epochs could not reach these states.

### F1 — Reason-phase cwd defect (eventgraph)

`claude_cli.go`'s Operate path fails closed without `WorkDir` (`cmd.Dir = task.WorkDir`). The Reason path sets **no** `cmd.Dir` — the agent's claude-cli inherits the **daemon's cwd**. The daemon launched from `repos/hive`, so all six reviews "verified" the deliverable in the wrong repository.

The defect evolved across the round. Reviews 1–3: phantom absence ("does not exist in the hive repository"). Reviews 4–6: wrong-destination doctrine — the reviewer assembled a near-perfect world map (file exists, in the `df-impl-v16` workspace, doctrine lives in `transpara-ai/docs` "a separate repository", option (c) "move the catalog to the docs repo") but never connected "the workspace" = "transpara-ai/docs." It was already there. The cwd anchor prevented the connection.

`decision.Task.WorkDir` exists (eventgraph `go/pkg/decision/intelligence.go:48`); hive `pkg/loop` never sets it on Reason tasks. Fix shape: thread WorkDir into Reason task construction + honor it in the provider (mirroring Operate's fail-closed gate); state the deliverable's destination explicitly in the review contract; runbook law — the daemon's cwd must never be a different git repo than the workspace.

> The catalog deliverable `codex/fo-roles-catalog-v16` remains **unreviewed in the FO's sense**: all six reviews were premised on the wrong repo (v16-F1). HEAD is `002bcf8` (9-role v2.0.0, the subtask reading); the FO's 24-role reading exists in-history at `b638a44`.

### F2 — Dual-spec oscillation (planner decomposition silently narrows FO scope)

The planner decomposed the FO at seq 124, before any review, scoping subtask `019ebb62` to runtime-source-code roles only (agentdef.go). The FO required a 24-role dual-layer catalog as a strict superset of `civic-roles.md`. Two live contradictory specs → the implementer alternately satisfied each, six times, every completion locally correct.

This was not a review-driven flip: the oscillation origin was a **planning-time narrowing** with no validation gate. Review #1's phantom rejection (v16-F1) resonated with the narrower subtask, amplifying subsequent cycles. The planner eventually arbitrated via DoD/AC/Test-Plan artifacts (seq 1060–1063) — right instinct, too late; destination still ambiguous.

Fix shape: a spec-diff gate at subtask creation (explicit narrowing declaration against the parent FO); review-rejection content never becomes task spec without FO reconciliation.

### F3 — Terminal quiescence has no exit (the system has no concept for finishing)

Keepalive wake-blocking plus the recheck allowlist's work-exists gates mean a society whose work-generators exit and whose reviews cap out freezes forever: no iterations → no budget checks → no parks → no wakes. `hive.run.completed` never fired. The daemon idles indefinitely; only the sentinel's chain-frozen watch surfaced it.

> **v16 is the first society to finish, and the system has no concept for finishing.**

Fix shape: a quiescence detector that emits `hive.run.completed` (or escalates to the operator) when all loops are wake-blocked and no assignable/reviewable/renewable work exists. Related: the cap's escalation comments demand "Human/CTO judgment" but nothing wakes the cto for them, and the operator-renewal channel remains deliberately unbuilt — the society can *ask* for a human decision but has no mechanism to *receive* one.

## The new close class

The arc's close-class ladder:

| Round | Store | Class | Flight | Notes |
|---|---|---|---|---|
| 3 | v13 | `stalled-silent` | 5 min | Loop goroutine exited; telemetry stayed green |
| 4 | v14 | `stalled-visible` | 27 min (resumed) | All agent deaths observable; escalation on-chain |
| 5 | v15 | `stalled-productive` | 31 min + artifact | Catalog delivered; renewal deadlock froze the epoch |
| **6** | **v16** | **`finished-unsignalled`** | **45 min, 1128 events** | **First society to finish; system had no concept for it** |

`finished-unsignalled` is coined this round. It differs from `stalled-*` in that the work genuinely completed — both tasks reached `task_done`, reviews capped, work-generators exited — and the freeze is the *correct* consequence of finishing, not a machinery failure. The failure is the absence of a completion signal.

## Grant accounting

| Grant | Rounds | Outcome |
|---|---|---|
| Grant-1 (rounds 1–3) | v11, v12, v13 | Consumed; all closed stalled-by-machinery |
| Grant-2 (rounds 4–6) | v14, v15, v16 | **Consumed; round 6 closed finished-unsignalled** |

Grant-2 is exhausted. The hard stop was reached and **resolved on 2026-06-15**: the External Committee granted **Event-1** (v4.0 Gate-K interim loop hardening; decision *Notify*, `transpara-ai/docs#132`), not a new slice-1 grant. Gate-K itself remains defined and unsatisfied (AC-K5 data-handling attestation pending — docs#137).

The v16 daemon (PID 821925/821927, ~0% CPU) had been held frozen by design pending that decision.

## Decisions escalated by the society (disposition)

1. **Gate-E or new grant — RESOLVED 2026-06-15:** the External Committee granted Event-1 / Gate-K (decision *Notify*, `transpara-ai/docs#132`), not a new slice-1 grant.
2. **Catalog ruling** — the society itself escalated: workspace IS `transpara-ai/docs`; the FO's 24-role scope governs (`b638a44`'s content); the planner subtask was mis-scoped.
3. **v16 fix-set scope** — candidate: F1 WorkDir threading (hive `pkg/loop` + eventgraph provider), F2 spec-diff gate at subtask creation, F3 quiescence detector → `hive.run.completed` + human-decision channel.
4. **v16 daemon disposition** — with the Gate-E hard stop now resolved to Event-1 (not a slice-1 continuation), the daemon's frozen-pending state is moot; final kill/keep is an operational follow-up.

## Relationship to the arc

This event closes the [[the-reunification]] slice-1 take-4 grant structure. It does **not** graduate doctrine into v4.0 — that fold requires acceptance and the migration register. What it does is prove the v15 fix set live, establish the first `finished-unsignalled` close class, and produce the three v16 findings (F1/F2/F3) as the candidate scope for the next fix set if a new grant is authorized.

The nohup sentinel design is fully vindicated: it ran the entire round unattended through an operator-session crash, banked every WAKE (parks, renewals, milestones, chain-freeze), and surfaced the close. The session-bound-watcher failure class is closed.

## Sources & provenance

Primary sources:

- `raw/transpara/dark-factory/reunification/2026-06-12-arc-state.md` (DF-REUNIFY-2026-06-12-ARC-STATE v0.3.0) — state table (round 6 row, catalog deliverable row, v16 findings, Grant-2 row, after-round-6 row, budget row); persistence section (pushed deliverable branches).
- `raw/transpara/dark-factory/reunification/2026-06-11-slice-1-take-4-round-log.md` (DF-REUNIFY-2026-06-11-SLICE-1-TAKE-4-ROUND-LOG v0.5.0) — Round 6 section: full timeline table (11:28–12:13), fix-set proof narrative, findings F1/F2/F3, close-class definition, grant accounting.
- `raw/open-brain/2026-06.md` — lines 3796–3910 (Open Brain captures from 2026-06-12): round 6 launch (line 3796), catalog commits 1b5032a/7fcee9e/d0faf3a/9ac1751/b638a44/002bcf8 (lines 3802–3858), session-crash nohup validation (line 3814), first-review milestone (line 3820), cwd-defect root cause (line 3838), F1 park/renewal live proof (line 3844), review-cap escalation (line 3862), oscillation correction (line 3868), round-6 close + grant-2 exhaust (line 3874).

Arc ladder and close-class taxonomy derived from the round log's explicit table. Claim "first society to finish" is the round log's own framing (v0.5.0, Round 6 section header). `[[wikilinks]]` are forward references; [[hive-governance]], [[the-reunification]], [[civic-roles]], [[factory-order]], and [[roles-catalog]] are compiled or partially compiled targets.
