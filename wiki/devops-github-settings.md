---
entity: DevOps GitHub Repository Settings
org: transpara
primary_placement: devops/security
placements:
  - devops/security
  - devops/delivery
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
  - historical_dev_ops_main ab607bd3ea9d07a4056697168669a239eae57015
source_authority:
  - code
  - configuration
  - engineering-docs
sources:
  - https://github.com/transpara-ai/dev-ops/blob/45140e1a0b/scripts/repo-settings.sh
  - https://github.com/transpara-ai/dev-ops/blob/45140e1a0b/README.md
  - https://github.com/transpara-ai/dev-ops/blob/45140e1a0b/.github/CODEOWNERS
  - https://github.com/transpara-ai/dev-ops/blob/45140e1a0b/.github/workflows/verify.yml
  - https://github.com/transpara-ai/dev-ops/blob/ab607bd3ea9d/scripts/repo-settings.sh  # earlier snapshot
  - https://github.com/transpara-ai/dev-ops/blob/ab607bd3ea9d/README.md  # earlier snapshot
  - https://github.com/transpara-ai/dev-ops/blob/ab607bd3ea9d/.github/CODEOWNERS  # earlier snapshot
  - https://github.com/transpara-ai/dev-ops/blob/ab607bd3ea9d/.github/workflows/verify.yml  # earlier snapshot
---

# DevOps GitHub Repository Settings

`scripts/repo-settings.sh` describes and checks the `dev-ops` repository
settings baseline. By default it reads GitHub and reports drift; application
is a separate mode. This reference describes the script at
`45140e1a0b79`, checked on 2026-09-07. It records desired configuration,
not a current audit of every repository.

## Read-only inspection

From the source repository, with `gh` and `jq` installed:

```bash
scripts/repo-settings.sh transpara-ai/dev-ops --show
scripts/repo-settings.sh transpara-ai/dev-ops --check
```

`--show` prints the desired settings and ruleset as JSON without calling
GitHub. `--check` (also the default when the flag is omitted) reads repository
metadata and the repository-owned ruleset. It requires GitHub access sufficient
to read those resources. API or permission failures are inspection failures,
not evidence that the baseline is satisfied.

## Desired merge configuration

| Setting | Baseline in the script |
| --- | --- |
| Merge methods | Squash enabled; merge commits and rebase merge disabled. |
| Squash message | Pull request title for the commit title, pull request body for the message. |
| Branch housekeeping | Delete head branches on merge; enable the update-branch button. |
| Ruleset | Active branch ruleset named `main`, targeting `~DEFAULT_BRANCH` with no excluded branch patterns. |
| History | Linear history required; deletion and non-fast-forward updates blocked for actors without bypass. |
| Pull requests | Required, with zero required approving reviews and all review threads resolved. |
| Additional review settings | Code-owner review and last-push approval are not required; stale review dismissal is disabled. |
| Required status | Context `verify`, with strict up-to-date status checks. |
| Bypass | Repository administrator role (actor ID 5), with bypass mode `always`. |

The ruleset name is `main`, but the target is GitHub's default-branch selector.
A repository whose default branch has another name is still the target.

The source's `CODEOWNERS` routes review to its maintainer. The settings do
not require a human approving review or a successful Codex review status.
The intended workflow leaves merging with the maintainer; those human
procedures are distinct from what GitHub enforces.

## How drift is determined

The [script](https://github.com/transpara-ai/dev-ops/blob/45140e1a0b/scripts/repo-settings.sh) compares repository settings,
ruleset enforcement, branch conditions, bypass actors, rule types, and the
parameters it specifies. Required status checks are compared by context name.
A missing repository-owned `main` ruleset is drift.

A successful comparison ends with `Baseline satisfied.`; detected drift
exits 1. GitHub or dependency errors can also fail the command, so retain the
output when diagnosing a nonzero result.

The lookup excludes inherited organization rulesets. A satisfied baseline
therefore means this script's repository-level comparisons matched; it does
not describe the full effective policy created by inherited rulesets,
classic branch protections, or other repository rulesets. The status-check
comparison also does not attest to which GitHub App supplied `verify`.

## Applying changes

The script's `--apply` mode patches repository merge settings, then creates
or updates the repository-owned ruleset and performs its comparison again.
That changes enforced repository protection. The source explicitly requires
separate Human authority for the named repository before application.

The writes are sequential, so a later failure may follow an earlier
successful change. A failed apply needs a fresh inspection to establish
the resulting state; it is not a transactional rollback.

This compilation read the implementation and did not apply settings or
change protections. For the verification job behind the required context,
see [[devops-verification]]; for the merged runner and review-on-ready
triggering, see [[devops-codex-review]].
