# Releases

[Latest stable release](https://github.com/transpara-ai/wiki/releases/latest) ·
[All releases and release notes](https://github.com/transpara-ai/wiki/releases)

The canonical version is `package.json`, synchronized with both root version
fields in `package-lock.json`. User-visible changes require a SemVer bump:
patch for compatible fixes and small UI improvements, minor for new capability,
major for incompatible contracts. This project is currently pre-1.0; its stable
GitHub releases still use ordinary `MAJOR.MINOR.PATCH`, without prerelease suffixes.

## Maintainer workflow

1. Work on a branch. Bump with `npm version patch --no-git-tag-version`
   (or `minor` / `major`) and add `docs/releases/v<VERSION>.md`, headed
   `# v<VERSION>`, describing behavior, validation, limitations and migration if needed.
2. Run `python3 compile/release.py check`, relevant tests, and ordinary review.
   If the version-only package edits invalidate existing secret-scan fingerprints,
   review those exact benign matches and merge their narrowly scoped clearances
   first. Never relax the scan or suppress new matches without inspection.
3. Push and merge the PR after required checks pass. The **CI** workflow's
   **Publish GitHub Release** job runs only on main pushes after **Build & Test**
   succeeds. It creates `v<VERSION>` at that exact checked commit, publishes the
   committed notes, and sets the stable release as latest. No draft/prerelease.
4. Confirm the published release, exact tag, notes and latest badge on GitHub.
   Deploy the merged revision through the existing host procedure; verify the
   site's `/version.json` and health. Publishing a release does not deploy it.

Documentation and corpus-only changes may retain the current application version;
the release job verifies the existing tag's ancestry and package version, and
rejects application-code differences before leaving a stable release unchanged.
Never edit previously
published code by moving a release tag. A new application change needs a new version.

If publication fails, fix credentials/connectivity or the reported metadata
problem and rerun the failed GitHub Actions job. An existing matching tag can be
reused after a partially completed publication; a tag at another commit is refused.
The job also refuses to mark an older version latest. Existing draft/prerelease
records require an explicit maintainer correction rather than being silently accepted.

Release notes are committed alongside code. Source ZIP/tar archives are supplied
by GitHub. No new binary distribution, package registry, or deployment pipeline
is introduced. See [GitHub's release guide](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository).
