---
doc_id: WIKI-TERMINOLOGY-AUTHORING
title: Contribute terminology and scan technical English
entity: Contribute terminology and scan technical English
doc_type: user_manual
status: draft
version: 0.2.0
created: "2026-11-05"
updated: "2026-11-07"
owner: Transpara
steward: Codex
project: wiki
supersedes: []
canonical: false
org: transpara
tier: operations
primary_placement: devops/runbooks
placements: [devops/runbooks]
classification: internal
source_authority: engineering-docs
last_compiled: "2026-11-05"
sources:
  - docs/terminology-workspace.md
  - compile/assets/terminology.html
  - compile/assets/terminology.js
  - compile/terminology_client.py
  - compile/terminology_sources.py
---

# Contribute terminology and scan technical English

This guide describes the browser workflow proposed in Wiki v0.11.0. Find it
under **DevOps → Runbooks**. Its stable address is
`/terminology-authoring.html`. Source acceptance does not mean the service is
installed or active. An operator connects the private terminology service.
Analysis-only deployments provide Scan and rewrite using a protected dictionary
seed, with no publication passkey or signing trust. The page names this mode;
submission, enrollment and publication controls are hidden. Its seed is
unverified, and scans do not approve it. Full publication deployments separately
enroll Human publication authority before publication controls work.

Open **Terminology** from the authoring tools, or visit `/terminology.html`.
Sign in and use your existing authoring enrollment. If your browser has no
remembered grant, open **Authoring access**, enter the operator-issued authoring
token, and choose **Connect**. A shared token alone does not identify a remote
contributor. Once access is enrolled, contributions and scans need no local
installation, repository checkout, command line or browser extension.

## Submit a terminology decision

1. In **Candidate inbox**, select a candidate and read its source occurrences.
2. Choose **Immutable Transpara terminology** for a technical term. Supply its
   canonical spelling, definition and meaning boundaries, technical noun/verb
   class, and approved forms. Include the canonical spelling among those forms.
3. Choose **Regular English** only for the displayed exact spelling and source
   contexts. Give a reason. This decision does not exempt the word from writing
   rules or silently apply to a new occurrence.
4. Choose **Submit proposal**. It is saved for review. Open **Contributions**
   to see the submission; it does not become an approved dictionary entry yet.

To propose a term that is absent from the inbox, choose **Propose a new technical
term**. Supply its repository/product scope, definition, technical class and
approved forms, then choose **Submit proposal**. This path proposes immutable
terminology; regular-English decisions still require current occurrence evidence.

If only **Download draft proposal** is available, this deployment has either
snapshot-only or analysis-only integration. Downloading a draft does not submit
or publish it. An analysis-only deployment still provides **Scan and rewrite**.

## Review and publish

A Human dictionary maintainer performs this step. Contributor access alone
cannot approve publication. One-time setup uses **Set up a publication passkey**
in **Contributions**. Complete the browser's Windows Hello, Touch ID or other
passkey prompt. Registration remains **pending operator acceptance** until an
operator independently verifies the Human and accepts that public credential.
The Human private key stays with the authenticator.

1. In **Contributions**, select the submitted proposals to accept.
2. Choose **Review selected proposals for publication**.
3. Read **Changes** and expand **Complete document to approve**. Check every
   term, definition, approved form, scope, regular-English context and version.
4. Check the statement confirming that you reviewed the complete document.
5. Choose **Approve with passkey and publish** and complete the browser prompt.
6. Open **Source revision** to check the new revision, source digest, Human
   approver and independent publisher. Refresh the dictionary to confirm it.

The browser checks that the approval challenge matches the displayed bytes.
The publisher verifies both signatures and advances history and active source
in one transaction. An expired review or changed base requires fresh preparation
and approval. After a connection failure, refresh history before retrying; a
completed publication can outlive its HTTP response. Repeating its stage does
not publish twice.

This first browser path adds decisions. Changes to existing approved terms need
the reviewed dictionary maintenance process. Publication updates the signed
runtime dictionary used by connected consumers; it does not edit Git or activate
other services. Old candidate evidence must be rescanned against the new digest.

## Scan a repository or URL

1. Open **Scan and rewrite**.
2. For **HTTPS URL**, enter one public page address. The scanner reads that page;
   it does not crawl the site or follow its instructions.
3. For **GitHub repository**, enter `https://github.com/OWNER/REPOSITORY`.
   Optionally select a branch, tag or commit. Use path patterns such as
   `README.md` or `docs/**`, one per line, to narrow the input.
4. Select **Deviation report** or **STE rewrite draft and report**.
5. Choose **Run scanner**. Use **Cancel scan** if needed. When complete, inspect
   coverage, source hashes, the resolved repository commit, findings and limits.
   Use **Download report** to retain the result.

URLs are public HTTPS pages. Repository capture is public by default; an
operator can enable an approved list of private GitHub repositories through a
server-managed credential. Do not put passwords or access tokens in URLs. The
browser never accepts a repository credential. Repository acquisition
uses one immutable commit and verifies captured blobs. It never executes target
code, hooks, installers or submodules. Supported inputs are Markdown/plain text,
page prose and Python comments/docstrings. Python is analyzed without executing
it; rewrite drafts preserve Python source bytes unchanged. The report identifies skipped files;
unsupported source languages and incomplete coverage are not a clean result.

Capture stops at 256 files, 1 MiB per file, 16 MiB total, 300 network requests
or 60 seconds. Narrow filters when a source exceeds these limits. Reports are
private to the submitting account and retained for up to seven days, subject to
global 100-report and 32 MiB storage limits. The page restores your latest retained job
when reopened. Two jobs can run at once; each account can have one active job.

## Understand a rewrite

A rewrite needs the configured model service and at most 64 KiB of source text.
Its report preserves the original and draft, shows their diff, checks protected
technical forms, commands, literals, quantities and logical conditions, and
rescans the draft. An unavailable model, excessive input or failed safeguard
produces an explicit unavailable/refused result. No scan publishes, changes a
repository, sends a support message or accepts a draft automatically.

Read each changed sentence before using it. Structural checks cannot prove
identical meaning. Vocabulary membership and independent readability findings
are partial checks; they do not establish approved word senses, every writing
rule or ASD-STE100 conformance. Every report states **conformance not assessed**.
The external standard and its database are not included in downloads or prompts.

## Revision History

| Version | Date | Change |
| --- | --- | --- |
| 0.2.0 | 2026-11-07 | Explain analysis-only previews and unavailable contribution/publication controls. |
| 0.1.0 | 2026-11-05 | Document the proposed browser contribution, signed publication and repo/URL analysis workflow. |
