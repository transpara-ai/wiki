---
entity: DevOps Pull Request Review Automation
org: transpara
primary_placement: devops/delivery
placements:
  - devops/delivery
  - devops/infrastructure
  - devops/runbooks
classification: internal
tier: operations
status: compiled
last_compiled: "2026-09-07"
verified_at: "2026-09-07"
source_checked_at: "2026-09-07T16:49:27Z"
review_by: "2026-10-07"
source_revisions:
  - dev_ops_main 45140e1a0b79acd5a4a5b2c48d16fb10d55ef59c
  - org_workflow_main 24f1293201236bbdb121ba901401ddf55a924c2c
  - reviewed_pr_3_head 1abc02adefafae8db828dfe3a4f20aa5beb6f768
  - historical_dev_ops_main ab607bd3ea9d07a4056697168669a239eae57015
  - historical_dev_ops_pr_3 827bb1549cf5f571714edf53a8cd5da10e6444a5
  - historical_org_workflow_main ad50500f1a9efcee3ca8ea7b43d5a5a901e4637e
  - historical_org_workflow_pr_29 f1d62e3c24a7d81a98627103fda4ead3103cddd8
source_authority:
  - code
  - configuration
  - engineering-docs
sources:
  - https://github.com/transpara-ai/dev-ops/blob/45140e1a0b/.github/workflows/codex-review.yml
  - https://github.com/transpara-ai/dev-ops/blob/45140e1a0b/.github/codex/prompts/review.md
  - https://github.com/transpara-ai/.github/blob/24f129320123/.github/workflows/reusable-codex-review.yml
  - https://github.com/transpara-ai/dev-ops/blob/45140e1a0b/scripts/codex-runner.sh
  - https://github.com/transpara-ai/dev-ops/blob/45140e1a0b/scripts/rollout-codex-review-caller.sh
  - https://github.com/transpara-ai/dev-ops/blob/45140e1a0b/README.md
  - https://github.com/transpara-ai/dev-ops/blob/45140e1a0b/scripts/remove-codex-review-scaffolding.sh
  - https://github.com/transpara-ai/dev-ops/blob/45140e1a0b/tests/test_remove_scaffolding.py
  - https://github.com/transpara-ai/dev-ops/pull/4
  - https://github.com/transpara-ai/dev-ops/pull/5
  - https://github.com/transpara-ai/dev-ops/actions/runs/34122016194
  - https://github.com/transpara-ai/dev-ops/actions/runs/34117615012
  - https://github.com/transpara-ai/dev-ops/blob/ab607bd3ea9d/.github/workflows/codex-review.yml  # earlier snapshot
  - https://github.com/transpara-ai/dev-ops/blob/ab607bd3ea9d/.github/codex/prompts/review.md  # earlier snapshot
  - https://github.com/transpara-ai/.github/blob/ad50500f1a9e/.github/workflows/reusable-codex-review.yml  # earlier snapshot
  - https://github.com/transpara-ai/dev-ops/blob/827bb1549cf5/.github/workflows/codex-review.yml  # earlier snapshot
  - https://github.com/transpara-ai/dev-ops/blob/827bb1549cf5/scripts/codex-runner.sh  # earlier snapshot
  - https://github.com/transpara-ai/dev-ops/blob/827bb1549cf5/scripts/rollout-codex-review-caller.sh  # earlier snapshot
  - https://github.com/transpara-ai/.github/blob/f1d62e3c24a7/.github/workflows/reusable-codex-review.yml  # earlier snapshot
  - https://github.com/transpara-ai/dev-ops/pull/3
  - https://github.com/transpara-ai/.github/pull/29
  - https://github.com/transpara-ai/dev-ops/actions/runs/34099305688  # earlier snapshot
  - https://github.com/transpara-ai/dev-ops/actions/runs/34099305209  # earlier snapshot
---

# DevOps Pull Request Review Automation

The `dev-ops` scaffold now uses the merged self-hosted review workflow,
backed by the runner's own ChatGPT login. The canonical caller requests a
review when a draft pull request is marked ready. Runner management, caller
rollout, and guarded removal of legacy review files are also merged.

## Current source baseline

This article was refreshed on 2026-09-07 against these GitHub revisions:

| Source | Revision | Merged behavior |
| --- | --- | --- |
| `transpara-ai/dev-ops` | `45140e1a0b79` | Runner management, caller rollout, legacy cleanup, and review-on-ready triggering. |
| `transpara-ai/.github` | `24f129320123` | Self-hosted reusable review, separate comment posting, and a credential-value check on the final review text. |

[Org PR #29](https://github.com/transpara-ai/.github/pull/29) merged at
11:34 UTC and [dev-ops PR #3](https://github.com/transpara-ai/dev-ops/pull/3)
at 11:41 UTC on 2026-09-07. The caller now references `@main`; the previous
wiki's description of an open migration and feature-branch caller is historical.
[PR #4](https://github.com/transpara-ai/dev-ops/pull/4) tightened legacy-file
removal, and [PR #5](https://github.com/transpara-ai/dev-ops/pull/5) changed
the review trigger.

The [main verification run](https://github.com/transpara-ai/dev-ops/actions/runs/34122016194)
passed for `45140e1a0b79`. The [final PR #3 review run](https://github.com/transpara-ai/dev-ops/actions/runs/34117615012)
successfully completed both review and posting for head `1abc02adefaf`,
before the later trigger change. These are separate observations: a completed
job is not proof that its review text approved the change or that every
repository adopted the caller. Earlier source and run references remain in
the source list as historical evidence.

## Requesting a review

The [current caller](https://github.com/transpara-ai/dev-ops/blob/45140e1a0b/.github/workflows/codex-review.yml) subscribes
only to `pull_request.types: [ready_for_review]`.

| Pull request event | Does this caller start a review? |
| --- | --- |
| Open a draft PR | No. |
| Mark the draft ready for review | Yes. |
| Open a PR directly as ready | No; the `opened` event is not subscribed. |
| Push another commit or reopen the PR | No. |
| Convert to draft, then mark ready again | Yes; this requests another round. |

The concurrency group is per pull request. A new ready-for-review run
cancels an earlier active run in that group. A later push alone neither
starts another review nor cancels the running review through this caller.
Check which head the review covered when commits change afterwards.

The [README](https://github.com/transpara-ai/dev-ops/blob/45140e1a0b/README.md) tells adopting repositories to widen the
event list with `opened`, `synchronize`, and `reopened` if they want more
frequent reviews. That is a destination-repository choice. The current
review job has no separate draft guard, so widening the events also requires
deciding how that repository should handle drafts.

The caller grants `contents: read` and `pull-requests: write`, calls the
org reusable workflow at `@main`, and passes no secrets. The independent
`verify` workflow still runs on pull requests and pushes to `main`;
review-on-ready does not change the verification gate.

## Merged review execution

The [reusable workflow](https://github.com/transpara-ai/.github/blob/24f129320123/.github/workflows/reusable-codex-review.yml) implements this path:

| Concern | Behavior at the cited revision |
| --- | --- |
| Runner | Private repositories use `self-hosted` and `codex` labels; public repositories skip the review job. The review timeout is 45 minutes. |
| Checkout | Checks out the event's pull request head SHA with full history and `persist-credentials: false`. |
| Review scope | Gives `codex exec` the base-to-head diff and commit-log commands, and permission to read files needed for the review. |
| Instructions | Loads the repository prompt if present, otherwise uses built-in instructions. |
| Execution options | Read-only sandbox, approvals disabled, and ephemeral session mode. |
| Credentials and permissions | The runner retains its ChatGPT login; the self-hosted job declares only `contents: read`. |
| Posting | A separate GitHub-hosted job with `pull-requests: write` posts a nonempty review after the review job succeeds. |
| Compatibility | An optional, unused `OPENAI_API_KEY` input remains so older callers that pass it still validate. |

The merged path no longer uses the previous API-key-based Codex action or
the old 400,000-byte generated-diff truncation input. It asks the CLI to
inspect the checkout. The workflow's configured defaults remain
`gpt-6-astra` and `xhigh`; these are source configuration values, not a
statement about current plan eligibility or model availability.

The [local review prompt](https://github.com/transpara-ai/dev-ops/blob/45140e1a0b/.github/codex/prompts/review.md)
emphasizes shell correctness, error paths, idempotency, secrets, workflow
permissions, the scaffold contract, and verification on the current head.

A posted verdict is ordinary comment text. It is not a GitHub approving
review and is not the required `verify` status described in
[[devops-github-settings]].

## Review output check

Before exporting the final review text to the posting job, the reusable
workflow checks it against nonempty API-key and access, refresh, and ID-token
values read from the runner's local auth file, when that file exists.
A detected literal match fails the review step and prevents comment posting.

This check is scoped to stored values appearing literally in the final
message. It does not establish general redaction of logs, transformed
strings, or other sensitive files. The runner-group restriction and job
permissions remain separate controls. This wiki refresh read the workflow
source and did not access a live runner's credential files.

## Runner management

[Runner management](https://github.com/transpara-ai/dev-ops/blob/45140e1a0b/scripts/codex-runner.sh) is shell tooling for
a Linux x64 host with systemd. Its defaults use a dedicated `codex-runner`
account, `/home/codex-runner/actions-runner`, a persistent
`/home/codex-runner/.codex` directory, and the organization's `codex`
runner group.

The script pins the Actions runner to `2.337.0` and Codex to `0.153.4`,
verifies downloaded archives by checksum, and installs the companion
`codex-code-mode-host` binary. It creates or updates the runner group to
disallow public repositories and restrict execution to selected workflows,
then reads those policy fields back and fails if they do not match. The
default selected workflow is the org reusable review at `@main`;
`RUNNER_GROUP_WORKFLOWS` supplies the configured list. Service installation
is managed separately from registration so a partially completed setup can
resume.

| Mode | Operational meaning |
| --- | --- |
| `status` | Requires root and reports the user, CLI version, registration, service, login status, and GitHub online/busy state. |
| `install` | Creates or configures the account, binaries, runner group, registration, and systemd service; prints the maintainer's one-time login steps. |
| `uninstall` | Attempts to stop/remove the service and unregister the runner; intentionally leaves the user, Codex installation, and login directory. It is not credential revocation. |

The source requires separate Human authority before runner installation.
The merged script describes implementation behavior; a current host
inspection is still needed to establish a particular runner's live state.

## Caller rollout

The [rollout script](https://github.com/transpara-ai/dev-ops/blob/45140e1a0b/scripts/rollout-codex-review-caller.sh)
compares existing callers with the dev-ops caller normalized to `@main`.
Its default mode reports differences. Caller endpoints returning 404 are
skipped; other API errors stop the run. Without explicit repository names
it lists up to 500 non-archived repositories.

With `--apply`, it pushes a branch and opens a PR per differing repository.
It can resume a pushed branch whose PR was not created, and skips repositories
with an already-open PR on the rollout branch. It does not continually update
those open PRs.

The canonical content comes from the script's checkout. At this revision
that includes the ready-for-review-only event list, so rolling it out also
changes when reviews run. Use the checkout's actual workflow file to assess
the proposed change.

## Removing recognized legacy scaffolding

The [cleanup script](https://github.com/transpara-ai/dev-ops/blob/45140e1a0b/scripts/remove-codex-review-scaffolding.sh)
is a separate operation from rollout. The protections tightened in
[PR #4](https://github.com/transpara-ai/dev-ops/pull/4) compare each candidate
file with known old Git blob hashes.

| Candidate | Default cleanup behavior |
| --- | --- |
| The `dev-ops` repository itself | Skipped. |
| Repository with a caller matching the current canonical file | Entire repository skipped, including its prompt and instructions. |
| Known old thin caller or inlined review workflow | Removed only when its blob is in the configured old-caller set. |
| Known old review prompt | Removed only when its blob is in the configured old-prompt set. |
| Known pure `AGENTS.md` review stub | Removed. |
| Known review stub that also contains the TLC adoption line | Reduced to the TLC instruction. |
| Customized files outside the known blob sets | Preserved individually. |

The default mode reports planned removals. `--apply` opens PRs and
re-evaluates the checked-out branch, including resumed branches, before
changing files. Blob IDs come from Git's index, and symlinks are excluded
from the deletion matches. A resumed branch with a canonical caller is
skipped; an already-cleaned branch can still get its missing PR without a
new commit. Non-404 API failures stop the run. The blob sets are configurable
through environment variables, so their defaults matter to this behavior.

[Cleanup tests](https://github.com/transpara-ai/dev-ops/blob/45140e1a0b/tests/test_remove_scaffolding.py) exercise these
cases using a fake GitHub CLI and local bare repositories. Their existence
is evidence of the test coverage, not a live audit of all past removals.

Cleanup does not install a replacement caller. Rollout also skips a repository
whose caller is absent. A repository that should opt in after cleanup needs
the canonical caller added through its normal change process.

## Diagnosing a missing or outdated review

1. Check that the repository still has a caller, and inspect its event list.
2. For the current canonical caller, confirm a ready-for-review transition
   occurred after the commits that need review.
3. Check repository visibility and whether the workflow reference is admitted
   by the runner group's selected-workflow policy.
4. Check runner availability/login and the review job's result, including the
   output-check failure path.
5. Check the separate posting job when review execution succeeded but no
   comment appeared.

A review for an earlier head can remain after another push. Request a new
round when the changed head needs review, and use [[devops-verification]]
for failures of the independent `verify` gate.
