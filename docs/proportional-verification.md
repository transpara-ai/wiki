---
doc_id: WIKI-PROPORTIONAL-VERIFICATION
title: Wiki proportional verification adapter
doc_type: verification_design
status: draft
version: 0.2.0
created: 2026-11-05
updated: 2026-11-05
owner: Transpara
steward: Codex
project: wiki
supersedes: []
canonical: false
---

# Wiki proportional verification adapter

## Purpose and boundary

The protected result remains `Build & Test`. After adoption, a trusted base
policy may focus only explicitly named non-runtime design and operating
documentation domains under `docs/`. Published `wiki/` articles, space homes,
root publication files, release notes, raw inputs, source, tests, dependencies,
workflows, and unknown or unowned paths run the complete existing suite.
Default-branch pushes and the first adoption pull request also run full.

The adapter vendors the unchanged selector and schema from
`transpara-ai/dev-ops` commit
`b02303a9a9250d7b2404806afa3e2ff7aa241c08`. The workflow executes only a
base-extracted adapter and dispatcher for classification and focused command
selection. It verifies engine provenance, recomputes the exact plan, and
accepts no plan-supplied command or directory.

## Credential scans

The existing standard-library security boundary remains first: before any
dependency installation, the required job extracts `compile/secret_scan.py`
from the exact base and scans every blob introduced anywhere in the pull
request or push range. This catches a credential that is later removed from the
final diff and prevents candidate install-time code from running first.

That changed-range scan is not a whole-tree scan. Every route therefore also
scans the complete exact-head tree. Full and shadow routes invoke the current
scanner directly and run its existing tests; a focused documentation route
cannot change the scanner because `compile/**` selects full. The dispatcher
records the whole-tree scan in focused execution evidence. Both scans fail
closed and redact matched bytes.

## Fixed routes

The focused mandatory baseline runs diff hygiene, the complete-tree credential
scan, and policy, provenance, replay, and dispatcher contracts. The
`repository-contracts` bundle validates every tracked file in the explicit
documentation domains for UTF-8, a heading or frontmatter, no NUL byte, and a
final newline. The checker and policy list the same domains. A future
`docs/tooling/`, service, deployment, or other new domain remains full until
its consumers and fixed commands are proved.

The focused registry intentionally omits the static-site build, full Python
suite, terminology runtime, deployment recovery, JavaScript assets, DOM,
browser, and shadow suites. Those consumers apply to published or runtime
surfaces that the focused rule does not own. Full required and full-shadow
routes preserve every prior `Build & Test` command and add the adapter and
whole-tree contracts; the push-only release job remains separate.

The ownership audit searched the full suite and configuration for filesystem
reads, Markdown globs, embedded Markdown, seed files, terminology inputs,
navigation and route inputs, and release metadata. Every current content
consumer reads a root publication file, `wiki/`, `spaces/`, `raw/`,
`docs/releases/`, the exact route-baseline text file, or `compile/`; all of
those surfaces select full. References to the focused Markdown domains are
design citations in comments or docstrings, not runtime reads. A fixed policy
test enumerates these consumer classes so later broadening cannot silently
focus them.

## Evidence and cost

The policy tests own every tracked path, replay 30 exact first-parent main
subjects, label synthetic cases separately, and exercise each enabled bundle
at least five times. Mutation tests prove that malformed owned Markdown fails
the same checker invoked by focused and full routes. Workflow tests prove that
the trusted changed-range scan precedes `pip install` and `npm ci` and that a
separate whole-tree scan remains present.

The prior current-main job took 108 seconds with unknown cache state; it is not
a controlled baseline. Controlled documentation qualification still requires
five independent cold heads, same-head warm attempts, sealed original artifact
ZIPs, identical plan/confirmation bindings, and successful complete shadows.
The cold documentation p95 limit is 100 seconds. Every other qualification
gate and resource bound remains unchanged.

Focused documentation runs no dependency installation, so it has no hidden
pip or npm cache dependency. Full and shadow routes use exact-head and
job-specific pip and npm keys with no restore prefix; an unchanged-head rerun
can prove the exact hit while another head or job cannot supply it. These
caches affect download cost only and never route selection.

## Failure boundaries

- A base without the adapter, policy, or provenance runs full.
- Policy, workflow, scanner, dependency, release, publication, raw, service,
  deployment, and unknown changes run full.
- Shadow and force-full modes cannot dispatch focused bundles.
- Attested commits must be complete object IDs and the checkout must match the
  attested head.
- Changed-range or whole-tree credential failure, plan drift, missing mandatory
  bundles, engine mismatch, command failure, or evidence failure blocks the
  required job.
- Full shadow is non-required comparison evidence; it does not weaken the
  protected `Build & Test` result.

## Revision History

| Version | Date | Change |
| --- | --- | --- |
| 0.2.0 | 2026-11-05 | Raise the cold documentation p95 limit from 90 to 100 seconds while preserving every other qualification gate and resource bound. |
| 0.1.0 | 2026-11-05 | Define the base-trusted Wiki documentation adapter, dual credential scans, complete-route boundary, evidence, costs, and failure behavior. |
