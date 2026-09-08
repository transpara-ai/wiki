---
entity: DevOps Repository Scaffold
org: transpara
primary_placement: devops/overview
placements:
  - devops/overview
  - devops/delivery
classification: internal
tier: operations
status: compiled
last_compiled: "2026-09-07"
verified_at: "2026-09-07"
source_checked_at: "2026-09-07T16:49:27Z"
review_by: "2026-10-07"
source_revisions:
  - dev_ops_main 45140e1a0b79acd5a4a5b2c48d16fb10d55ef59c
  - historical_dev_ops_main ab607bd3ea9d07a4056697168669a239eae57015
source_authority:
  - code
  - configuration
  - engineering-docs
sources:
  - https://github.com/transpara-ai/dev-ops/blob/45140e1a0b/README.md
  - https://github.com/transpara-ai/dev-ops/blob/ab607bd3ea9d/AGENTS.md
  - https://github.com/transpara-ai/dev-ops/blob/ab607bd3ea9d/CLAUDE.md
  - https://github.com/transpara-ai/dev-ops/blob/45140e1a0b/.claude/settings.json
  - https://github.com/transpara-ai/dev-ops/blob/45140e1a0b/.github/pull_request_template.md
  - https://github.com/transpara-ai/dev-ops/blob/45140e1a0b/.github/ISSUE_TEMPLATE/change.yml
  - https://github.com/transpara-ai/dev-ops/blob/45140e1a0b/.github/CODEOWNERS
  - https://github.com/transpara-ai/dev-ops/blob/45140e1a0b/scripts/rollout-codex-review-caller.sh
  - https://github.com/transpara-ai/dev-ops/blob/45140e1a0b/scripts/remove-codex-review-scaffolding.sh
  - https://github.com/transpara-ai/dev-ops/pull/3
  - https://github.com/transpara-ai/dev-ops/pull/4
  - https://github.com/transpara-ai/dev-ops/pull/5
  - https://github.com/transpara-ai/dev-ops/blob/ab607bd3ea9d/README.md  # earlier snapshot
  - https://github.com/transpara-ai/dev-ops/blob/ab607bd3ea9d/.claude/settings.json  # earlier snapshot
  - https://github.com/transpara-ai/dev-ops/blob/ab607bd3ea9d/.github/pull_request_template.md  # earlier snapshot
  - https://github.com/transpara-ai/dev-ops/blob/ab607bd3ea9d/.github/ISSUE_TEMPLATE/change.yml  # earlier snapshot
  - https://github.com/transpara-ai/dev-ops/blob/ab607bd3ea9d/.github/CODEOWNERS  # earlier snapshot
  - https://github.com/transpara-ai/dev-ops/pull/1
---

# DevOps Repository Scaffold

`transpara-ai/dev-ops` is the reference repository scaffold and home for
Transpara operational tooling. Its merged scaffold provides a reusable
starting point for instructions, local verification, CI, review, and GitHub
settings. This article explains that starting point; the source repository
and the installed canonical TLC skill retain their authority.

## Source baseline

The current baseline is GitHub `main` at `45140e1a0b79`, checked again on
2026-09-07. It includes the original scaffold from
[PR #1](https://github.com/transpara-ai/dev-ops/pull/1), the merged runner
migration in [PR #3](https://github.com/transpara-ai/dev-ops/pull/3), guarded
legacy-file cleanup in [PR #4](https://github.com/transpara-ai/dev-ops/pull/4),
and review-on-ready triggering in
[PR #5](https://github.com/transpara-ai/dev-ops/pull/5).
[[devops-codex-review]] describes the merged review path and both repository
maintenance scripts. Earlier source references remain in the source list as
historical evidence.

Source files were read from GitHub or from the matching committed Git objects,
including scripts and tests. The article frontmatter records full source
revisions; file links use verified, unambiguous abbreviated commit references.
Sources are linked to GitHub and require repository access; they have not been
copied into a local raw-source mirror. Remote changes require a later source
review and article update. The shared `AGENTS.md` and `CLAUDE.md` files are
unchanged from the original scaffold, so their original commit citations
remain applicable.

The DevOps space is stewarded by Transpara; these sources belong to the
`transpara-ai` GitHub organization. Repository configuration is evidence for
this scaffold, not proof that every organization repository has adopted it.

## Start with the task

| Reader task | Wiki reference | Source entry point |
| --- | --- | --- |
| Start or align a repository | This article's adoption map | [README adoption section](https://github.com/transpara-ai/dev-ops/blob/45140e1a0b/README.md#adopting-this-scaffold-in-another-repository) |
| Understand or troubleshoot verification | [[devops-verification]] | `Makefile`, lint configuration, Stop hook, and repository tests |
| Inspect merge settings and drift | [[devops-github-settings]] | `scripts/repo-settings.sh` |
| Request or diagnose a pull request review | [[devops-codex-review]] | Caller workflow, repository review prompt, and org reusable workflow |
| Update callers or remove recognized legacy review files | [[devops-codex-review]] | `scripts/rollout-codex-review-caller.sh` and `scripts/remove-codex-review-scaffolding.sh` |

## Where instructions and review live

| File | Role in the scaffold |
| --- | --- |
| [AGENTS.md](https://github.com/transpara-ai/dev-ops/blob/ab607bd3ea9d/AGENTS.md) | Shared repository instructions and pointer to the installed TLC skill. |
| [CLAUDE.md](https://github.com/transpara-ai/dev-ops/blob/ab607bd3ea9d/CLAUDE.md) | Imports `AGENTS.md` first, then adds Claude Code integration notes. |
| [.claude/settings.json](https://github.com/transpara-ai/dev-ops/blob/45140e1a0b/.claude/settings.json) | Configures permissions, the TLC marketplace/plugin, and the Stop hook. |
| `README.md` | Explains the repository and its adoption path. |
| `.github/codex/prompts/review.md` | Repository-specific review criteria consumed by the reusable review workflow. |
| [PR template](https://github.com/transpara-ai/dev-ops/blob/45140e1a0b/.github/pull_request_template.md) and [change issue form](https://github.com/transpara-ai/dev-ops/blob/45140e1a0b/.github/ISSUE_TEMPLATE/change.yml) | Capture the change's outcome, scope, constraints, and verification; the PR also records its route. |

TLC policy is distributed through the canonical plugin. This wiki does not
supply a second executable copy of that policy. The templates carry a brief
with the change, allowing the squash commit to preserve its context.

## Adoption map

The source README distinguishes reusable scaffold files from files that need
to be written for the destination repository.

| Treatment | Files and decisions |
| --- | --- |
| Reuse the integration and formatting scaffold | `CLAUDE.md`, `.editorconfig`, `.gitattributes`, `.pre-commit-config.yaml`, `.yamllint.yaml`, and `.claude/`. |
| Reuse the delivery templates, checking their current references | `.github/dependabot.yml`, the verify and review callers, PR template, and issue forms. The review caller now runs only on `ready_for_review`; adopting it also adopts that trigger policy. See [[devops-codex-review]]. |
| Adapt instructions and verification to the codebase | Write the destination `AGENTS.md`; keep the shared verification entry point and connect `make test` to that repository's real test runner. Add language linting to the pre-commit configuration. |
| Adapt ownership, ignored files, and review criteria | Use the destination maintainers in `CODEOWNERS`; retain secret/personal-file exclusions in `.gitignore`; write a review prompt for the actual codebase. |
| Retain applicable scaffold tests | Adapt `tests/test_repository.py` to the destination's rules and language. A passing scaffold test suite does not replace application tests. |
| Inspect repository settings separately | Use [[devops-github-settings]] to compare GitHub's configuration with the desired baseline. Copying files alone cannot set merge protections. |

In the source scaffold, `CODEOWNERS` names `@MichaelSaucier`. That is source
ownership, not a universal destination owner. Likewise, the scaffold's
Python unittest discovery is a test entry point to adapt, not a language
choice for every service.

## What this source can populate

The initial corpus covers repository engineering and delivery operations:
setup, verification, review, runner management, legacy review cleanup, and
merge configuration. The merged source tree does not yet provide application
deployment manifests, network topology, container operations, monitoring
configuration, or application-service recovery procedures.
Those DevOps sections need their own implementation sources and operational
evidence before they can become useful runbooks.
