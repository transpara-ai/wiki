---
entity: DevOps Verification and Local Hooks
org: transpara
primary_placement: devops/delivery
placements:
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
  - https://github.com/transpara-ai/dev-ops/blob/45140e1a0b/Makefile
  - https://github.com/transpara-ai/dev-ops/blob/45140e1a0b/.pre-commit-config.yaml
  - https://github.com/transpara-ai/dev-ops/blob/45140e1a0b/.github/workflows/verify.yml
  - https://github.com/transpara-ai/dev-ops/blob/45140e1a0b/.claude/hooks/verify-before-stop.sh
  - https://github.com/transpara-ai/dev-ops/blob/45140e1a0b/.claude/settings.json
  - https://github.com/transpara-ai/dev-ops/blob/45140e1a0b/tests/test_repository.py
  - https://github.com/transpara-ai/dev-ops/blob/45140e1a0b/.github/dependabot.yml
  - https://github.com/transpara-ai/dev-ops/blob/45140e1a0b/tests/test_remove_scaffolding.py
  - https://github.com/transpara-ai/dev-ops/blob/45140e1a0b/.github/workflows/codex-review.yml
  - https://github.com/transpara-ai/dev-ops/blob/ab607bd3ea9d/Makefile  # earlier snapshot
  - https://github.com/transpara-ai/dev-ops/blob/ab607bd3ea9d/.pre-commit-config.yaml  # earlier snapshot
  - https://github.com/transpara-ai/dev-ops/blob/ab607bd3ea9d/.github/workflows/verify.yml  # earlier snapshot
  - https://github.com/transpara-ai/dev-ops/blob/ab607bd3ea9d/.claude/hooks/verify-before-stop.sh  # earlier snapshot
  - https://github.com/transpara-ai/dev-ops/blob/ab607bd3ea9d/.claude/settings.json  # earlier snapshot
  - https://github.com/transpara-ai/dev-ops/blob/ab607bd3ea9d/tests/test_repository.py  # earlier snapshot
  - https://github.com/transpara-ai/dev-ops/blob/ab607bd3ea9d/.github/dependabot.yml  # earlier snapshot
---

# DevOps Verification and Local Hooks

The merged `dev-ops` scaffold uses `make verify` as its shared verification
entry point for developers, CI, and the Claude Code Stop hook. It runs lint
and repository tests. The implementation described here is pinned to
`45140e1a0b79` and was checked on 2026-09-07.

## Commands and prerequisites

Run these from a checkout of the source scaffold, or a destination repository
that has adopted its Makefile.

| Command | Effect |
| --- | --- |
| `make verify` | Runs the `lint` and `test` prerequisites. |
| `make lint` | Runs pinned pre-commit hooks over all tracked files, showing diffs on failure. Some hooks rewrite formatting. |
| `make test` | Runs `python3 -m unittest discover -s tests -p 'test_*.py' -v`. |
| `make install-hooks` | Installs the local pre-commit hook. |
| `make update` | Updates hook revisions in the pre-commit configuration; the resulting diff needs review and verification. |

The [Makefile](https://github.com/transpara-ai/dev-ops/blob/45140e1a0b/Makefile) defaults to
`uvx pre-commit@4.6.2`, so local execution needs `make`, `uvx`, and Python.
Hook environments and dependencies also need to be available or downloadable;
this scaffold is not an air-gap bootstrap procedure. The gitleaks hook uses
pre-commit's Go environment. Existing project tests belong behind the same
`test` target when adopting the scaffold.

## What lint and tests cover

The [pre-commit configuration](https://github.com/transpara-ai/dev-ops/blob/45140e1a0b/.pre-commit-config.yaml) includes
JSON/YAML checks, conflict-marker and private-key detection, executable and
shebang consistency, symlink checks, file-size checks, and text formatting.
ShellCheck, shfmt, strict yamllint, and actionlint cover shell and workflow
files.

The local `gitleaks-dir` hook runs
`gitleaks dir --no-banner --redact --exit-code 1 .`. It scans the working
directory rather than relying on a staged diff, because CI would otherwise
have no staged content to inspect. This is not a scan of all Git history.

[Repository tests](https://github.com/transpara-ai/dev-ops/blob/45140e1a0b/tests/test_repository.py) check the instruction
import and size limits, configured secret-file denials, narrow command
permissions, plugin wiring, executable hook paths, shell headers, explicit
workflow permissions, third-party action pins, hook revision tags, and
forbidden tracked files. These are scaffold invariants; they do not prove
that live GitHub settings or deployed infrastructure match the documentation.

The current tests also check that the review caller grants the reusable
workflow's pull-request write permission and passes no secrets. The new
`tests/test_remove_scaffolding.py` covers recognized legacy blobs, customized
files, canonical callers, TLC-bearing instruction stubs, and API failures.
Its apply-path cases use a fake GitHub CLI and local bare repositories to
exercise resumed branches, symlink preservation, and PR creation after an
earlier push. See [[devops-codex-review]] for the cleanup tool's scope.

## CI and dependency maintenance

The [verify workflow](https://github.com/transpara-ai/dev-ops/blob/45140e1a0b/.github/workflows/verify.yml) runs on pull
requests and pushes to `main`. Its job is named `verify`, uses
`ubuntu-latest`, declares `contents: read`, and has a 20-minute timeout.
It installs uv, caches pre-commit environments using the configuration hash,
and calls `make verify`.

Third-party actions in the scaffold workflows use full commit SHAs with
version comments. [Dependabot](https://github.com/transpara-ai/dev-ops/blob/45140e1a0b/.github/dependabot.yml) checks
GitHub Actions weekly and groups their updates. Hook revisions are maintained
through `make update`. The organization-owned reusable review workflow
tracks a branch and is a separate dependency; scaffold tests do not inspect
every action inside that external workflow.

## Stop hook behavior and limits

The [Stop hook](https://github.com/transpara-ai/dev-ops/blob/45140e1a0b/.claude/hooks/verify-before-stop.sh) consumes its
input event, changes to the project directory, and inspects
`git status --porcelain`.

| Condition in the merged hook | Result |
| --- | --- |
| Outside a Git working tree, or no uncommitted changes | Exits 0 without verification. |
| `make` or `uvx` is missing | Prints a skip message and exits 0. |
| Changed tree and `make verify` succeeds | Exits 0. |
| Changed tree and `make verify` fails | Prints the last 80 lines of output to stderr and exits 2 to block the stop. |

The settings give the hook a 600-second timeout. A permitted stop therefore
does not, by itself, prove verification ran: clean trees and missing-tool
cases skip it. This hook is wired for Claude Code; it does not establish an
equivalent Codex Stop hook.

## Troubleshooting sequence

1. Run `make verify` directly and preserve the exit status and failing tool.
2. If formatting hooks changed files, inspect their diff and rerun verification.
3. If tool setup failed, resolve the missing executable or hook dependency;
   distinguish setup failure from a code/test failure.
4. If a repository invariant failed, compare the named file with the test's
   intended rule before adapting the scaffold.
5. Check the pull request's `verify` job for the current commit; an older
   green run does not describe the new tree.

See [[devops-github-settings]] for how that job becomes a merge requirement,
and [[devops-codex-review]] for the separate review workflow.
