---
entity: The Issue-Scan Runner Suite
aliases: [runner suite, issue-scan runner-suite package, runner contracts, hive#262 package]
tier: architecture
status: compiled
last_compiled: "2026-07-12"
sources:
  - raw/open-brain/2026-07.md  # L3662–L3743 — the #262→PR#266 arc within the July cycle and its relation to the finalizer guardrails
confidence:
  sources: primary — the merged package, Factory Order, and contracts generator.
  claims: grounded; the contracts summary below paraphrases the generated document rather than quoting every field.
---

# The Issue-Scan Runner Suite

**The packaged contract surface between the [[hive-governance|hive]]'s governed issue-scan lifecycle and external runners.** Merged 2026-07-11 as `transpara-ai/hive#266` (closing hive#262), the package pairs a manifest with committed fixtures defining the shapes an externally-implemented runner — a process that receives a JSON context on stdin and must return exactly one JSON result on stdout — must satisfy. What ships today is **offline contract-and-fixture validation**: `hive factory validate-issue-scan-runner-suite` checks the manifest and the synthetic fixtures against the runtime's receipt validators. The package is deliberately an inert scaffold — it contains no runner executables, and the validator neither resolves nor executes the manifest's command placeholders; validating a *live* runner implementation end-to-end remains future work.

## What the contracts pin down

The machine-readable contracts document (`issue-scan-runner-contracts`) enumerates, per runner (stage-role output, implementation, review, blocker repair, draft-PR request/creation, ready-state review, and the managed finalizer):

- the stdin context kind/type and the stdout contract type with its required fields;
- **preconditions** — for the managed finalizer these now include the recorded human-decided mark-ready approval, the unconsumed single-use nonce, and the absence of terminal blocked evidence (see [[mark-ready-authority]]);
- **validation boundaries** — what the runtime independently re-verifies before recording any returned packet (queued run, FactoryOrder, exact implementation commit, Human-approval boundary flags);
- **authority boundaries** — what the runner must never do (approve, merge, deploy, mark ready outside the managed path), stated as machine-readable strings so drift between prose and enforcement is detectable.

The suite treats runner receipts the way the wiki treats articles: recorded evidence with declared shape, validated at the door, never trusted on self-report. Its fixtures double as executable documentation — the committed examples are themselves validated in CI, so the documentation cannot silently diverge from the contract.

## Why it matters to the arc

The runner suite is the seam where the hive's [[the-work-graph|Work-graph]] lifecycle stops being a monolith: any model family or external system can implement a stage, provided it satisfies contracts the runtime can check. The finalizer guardrails merged the same day made the *most dangerous* runner boundary — the one that mutates a live PR — the most heavily contracted; the suite is how the remaining boundaries get the same treatment incrementally.

## Primary references

On-Platform primary sources for this article (governed docs and code;
not web-served — open them from the Transpara workspace):

- `/Transpara/transpara-ai/repos/hive/packages/issue-scan-runner-suite/README.md` — the package: manifest + fixtures for external runner validation
- `/Transpara/transpara-ai/repos/hive/docs/factory-orders/FO-hive-262-issue-scan-runner-suite-package-v0.1.0.md` — FO-HIVE-262 — package scope, validation harness requirements
- `/Transpara/transpara-ai/repos/hive/cmd/hive/factory_issue_scan_runner_contracts.go` — the machine-readable contracts document: per-runner stdin/stdout types, preconditions, authority boundaries
