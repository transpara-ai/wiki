---
doc_id: WIKI-TERMINOLOGY-WORKSPACE
title: Terminology workspace manual and integration reference
doc_type: implementation_reference
status: draft
version: 0.2.1
created: 2026-11-04
updated: 2026-11-05
owner: Transpara
steward: Codex
project: wiki
supersedes: []
canonical: false
---

# Terminology workspace

The private authoring profile includes a Terminology tool at /terminology.html.
It displays questionable terms, source observations, the Human-owned Transpara
Dictionary export, regular-English decisions, and the dictionary source revision.
With the operator-configured terminology authority service, it also accepts
browser contributions, repository/URL reports, rewrite drafts, and publication
approved with a Human-held passkey. Authors need no local scanner installation.
A deployment with only a configured snapshot retains candidate review and
draft download. Source acceptance does not activate services or enroll a
production approval credential.

## Design and authority

The independent [technical-english repository](https://github.com/transpara-ai/technical-english)
owns the checked-in Human dictionary document and scanner. The browser service
maintains a separate signed runtime dictionary for its explicitly connected
consumers. The checked-in document remains its bootstrap; browser publication
does not edit Git, merge a pull request, move a release tag, activate legacy
consumers, or send support messages. The existing Wiki article-publication
endpoint is not used for dictionary decisions.

An authoring grant permits contribution and analysis. Publication additionally
requires a Human-held, operator-enrolled passkey and an independent workload
signature. The authenticator holds the Human private key; a separate protected
publisher holds the workload key. Wiki owns neither key and cannot select trust
configuration. The browser workflow introduces a Critical publication boundary;
its design, adversarial review, Human acceptance, and separate live-effect
authority are documented in the independent
[technical-English repository](https://github.com/transpara-ai/technical-english):
`docs/BROWSER-WORKFLOW.md` and `docs/BROWSER-OPERATIONS.md`. Operators must select
their reviewed, accepted revision before deployment.

The snapshot belongs to the same single internal curator cohort as the existing
private evidence workspace. Before configuring its path, the operator must
confirm that all of its contents are authorized for every existing internal
curator. Keep the export within its source material's confidentiality boundary.
It grants no source-repository access and admits no broader audience. The
snapshot default is unconfigured and returns 503; company/public profiles return 404
and omit the assets. Widening access outside this cohort or changing its
permission policy needs separate Human-authorized Critical work.

The two draft classifications are immutable Transpara terminology and regular
English. Immutable proposals include an exact term, meaning boundaries,
technical noun or technical verb class, scope, and permitted forms. A
regular-English proposal does not add a vocabulary exception.

The exported JSON has state draft and binds the candidate ID to the dictionary
document SHA-256 and the scanner's original occurrence context digests for the
observations shown on the page. It covers at most ten observations. The page
shows the displayed count and the total; unseen contexts are not included.
It carries no claimed reviewer identity and has no approval authority. A draft
can be submitted to the connected service for Human review, or offered through
the existing reviewed repository process.
The digest detects revision differences; it is not a signature or proof of
Human approval.

A regular-English entry applies only to its exact spelling and the reviewed
source occurrences. Other case variants in a normalized candidate group remain
unclassified. Regular-English drafts include hashes only for shown observations
whose exact spelling matches the candidate term. The form shows included and
total counts; other variants remain visible as context and are omitted from the
draft. With no exact match, download is disabled. Immutable proposals retain
shown contexts for Human review of their explicitly proposed approved forms.
Each occurrence hash binds the unchanged extracted line, path,
line number, and term span. The page preserves supplied hashes; it cannot
recompute them from sentences whose protected literals were masked.

## Review a candidate

1. Open Terminology from the Wiki tools navigation.
2. Use the existing authoring session or enter the authoring token if needed.
3. Select a candidate and read its repository, product, and source sentences.
4. Select a classification. For an immutable term, complete its definition and
   approved forms, including the canonical form.
5. With the authority service connected, choose **Submit proposal** and inspect
   its pending entry in **Contributions**. **Download draft proposal** also
   provides JSON for review. Snapshot-only deployments provide the download.
6. After publication, select **Refresh**. An older candidate export is not
   automatically current: the operator must rescan against the active dictionary
   before new occurrence-bound decisions can use it.

The page does not persist selections or tokens in browser storage. Refresh
clears the selection so an earlier draft is not exported against a later
snapshot. Candidate state remains pending after a download.

Use **Propose a new technical term** to introduce an immutable term without a
scanner candidate. Supply its exact repository/product scope, definition,
technical class, and approved forms. Regular-English proposals require current
candidate evidence and a reason. Existing Human terms and decisions are
append-only through this browser path; changes to existing decisions and
deletion continue through reviewed repository work.

## Set up a Human publication passkey

In **Contributions**, choose **Set up a publication passkey** and complete the
browser's authenticator prompt with the required PIN, biometric, or other user
verification. Use the approved HTTPS wiki address and a passkey-capable browser.

The result is **pending operator acceptance**. Ask the operator to verify the
Human owner through the existing trusted channel and accept the public
credential in protected configuration. Creating a passkey alone does not grant
publication authority. Approval becomes available after the service reports
that this account has an enrolled publication passkey. Production trust
enrollment is a separate operator effect; agents do not enroll their own keys.
The wiki never requests the Human private key, an SSH key file, or provider
credentials. A cancelled prompt or missing enrollment leaves publication pending.

## Review and publish

1. In **Contributions**, select submitted proposals and choose **Review selected
   proposals for publication**.
2. Read **Changes** and expand **Complete document to approve**. Inspect the
   complete Markdown document, scope, metadata/version, existing decisions,
   additions, and revision history. Check its source SHA-256 and preparation
   expiry.
3. Select **I reviewed the complete document and authorize this publication**
   only when the complete change is acceptable.
4. Choose **Approve with passkey and publish** and complete the authenticator's
   user-verification prompt.
5. Confirm the success message, then inspect **Source revision** for the signed
   publication history, dictionary version, and digest.

Preparation expires after ten minutes. The approval challenge binds the exact
source, digest, base dictionary, scope, verified actor, preparation ID, expiry,
and random nonce. The publisher verifies the Human proof and adds the independent
workload signature before atomically recording history and advancing the active
dictionary. A changed base requires fresh preparation, review, and approval.
A repeated completed request returns the same release. An ordinary authoring
token never substitutes for either signature.

The runtime ledger is authoritative only for explicitly connected browser
consumers. Operators can archive approved bytes and proofs for reviewed Git
ingestion. The repository dictionary and legacy SSHSIG publication contracts
remain separate. If a publication response is uncertain, select **Refresh** and
inspect **Source revision** before preparing another change; ask the operator
to inspect the durable ledger when the outcome remains unclear.

## Scan a repository or URL

1. Open **Scan and rewrite**, then choose **HTTPS URL** or **GitHub repository**.
2. Enter one public HTTPS page or a repository home address such as
   `https://github.com/OWNER/REPOSITORY`. Enter any branch, tag, or commit in its
   separate optional field.
3. For a repository, optionally enter **Paths to include**, one relative pattern
   per line. For example, `docs/**` selects that directory and `README.md`
   selects that file. Narrow the paths when the repository or report is too large.
4. Choose **Deviation report** or **STE rewrite draft and report**, then **Run
   scanner**. Keep this tab open to follow queued/running status; use **Cancel
   scan** to prevent a late result from replacing a cancelled job.
5. Inspect coverage, the pinned repository commit, skipped files, findings, and
   limitations. Expand **Complete report, original text, findings and rewrite
   drafts** and use **Download report** to retain its JSON.

One URL capture does not crawl links. Supported URL content is UTF-8 plain text,
Markdown, or HTML; extraction omits scripts and forms. Repository capture
resolves one commit and reads its immutable tree/blobs. Supported files are
Markdown/text and Python source for comment/docstring analysis. Binary content,
other languages, symlinks, and submodules appear as skipped coverage. No target
code, hooks, dependency installation, or target-selected checker executes.
Repository capture is anonymous by default. The optional host adapter can use
an approved GitHub credential only for exact repositories the operator has
authorized for the existing curator cohort. Other repositories remain anonymous;
ordinary URL capture always remains credential-free. The browser accepts no
source credential or credential-bearing URL.

Only offer sources approved for this workspace and its configured model and
analysis services. Source quarantine runs before model use or retained reports.
The transport requires public HTTPS, pins public DNS addresses, and refuses
redirects outside the original origin. Failed or truncated acquisition never
becomes a complete-scan claim. Scan jobs and reports belong to the verified
requester; shared dictionary proposals remain visible to the curator cohort.

## Understand analysis and rewrite drafts

An operator-selected, digest-pinned external database supplies vocabulary lookup
when available. Unknown vocabulary requires meaning and technical-scope review.
Without that database, vocabulary is unassessed. Independently authored writing
diagnostics cover a limited set of patterns; they do not assess every grammar
rule or approved word sense. Reports always state `conformance: not_assessed`.
A clean candidate list, model response, or rewrite draft does not certify
ASD-STE100 conformance.

A rewrite uses at most one configured model call. Original text, proposed draft,
diff, preservation checks, and remaining findings stay inspectable. Guards
preserve immutable forms, code/commands/literals, quantities, units, and
paragraphs containing conditions, negation, or obligations. They cannot prove
equal meaning; a Human must review the draft before using it. Missing model
configuration, oversized input, or a refused draft retains the diagnostic report
and explains that no accepted rewrite is available. Scans and rewrites never
publish terminology or overwrite the original source.

## Browser service and snapshot-only configuration

The operator selects a fixed absolute Unix socket through
`TRANSPARA_TERMINOLOGY_SOCKET`. Required identity, exact HTTPS Origin,
file/socket permissions, independent workload signer, trusted Human enrollment,
external database pin, durable state, backups, and rollout are covered by the
operator reference above. Production installation and activation need their
separate live-effect authority. Ordinary users need only their browser and
approved authoring access.

For optional approved private repositories, the operator selects a private,
bounded JSON file with `TRANSPARA_TERMINOLOGY_GITHUB_CONFIG`. Its complete schema
is:

```json
{
  "schema_version": 1,
  "credential_ref": "approved-terminology",
  "repositories": ["transpara-ai/example"]
}
```

The list permits at most 100 exact `owner/repository` names, with no duplicates
or wildcard grant. The file contains a reference, never a token. The existing
`KNOWLEDGE_HUB_CREDENTIALS` registry resolves that approved reference to its
host environment value and exact `https://api.github.com` origin, as documented
in the [discovery integration reference](../compile/DISCOVERY.md). Use read-only
repository access, protect both private descriptors from request/workload edits,
and authorize the listed source data and model use for the entire existing
curator cohort before activation. Use the host's protected read-only mount or
equivalent deployment boundary; these files are separate from writable job state.

Only repository jobs for listed names receive that credential. Its header stays
inside process memory and bounded child stdin, outside arguments, environment,
logs, and reports. It cannot follow a redirect to another repository or origin.
Unlisted repositories fall back to anonymous capture. A malformed configured
adapter or unavailable credential fails closed; a missing adapter leaves public
capture unchanged. Enabling private access is an explicit operator deployment
effect, and this source change installs no production descriptor or credential.

Snapshot-only deployments retain this operator setup:

Generate a snapshot using the independent CLI:

```bash
python -m tenglish snapshot --dictionary dictionary/TRANSPARA-DICTIONARY.md --queue candidates.json --output /private/terminology-snapshot.json
```

Configure TRANSPARA_TERMINOLOGY_SNAPSHOT in the existing authoring service
environment to the absolute path of that JSON export. The service reads it for
each GET /api/terminology/snapshot request. It must be a regular UTF-8 file no
larger than 1 MiB, matching the existing evidence quarantine limit. The host
controls the path; a request cannot select another
file or remote URL. Missing, malformed, and unsupported snapshots produce an
explicit unavailable response, never an empty dictionary presented as current.
The adapter applies the existing whole-payload evidence quarantine before
display, including a scan of decoded JSON so escaped token characters cannot
bypass it. Recognized secrets are refused with a generic error. This detector
does not replace operator classification or prove that content has no private
or personal data.

The shared schema has schema_version 1, dictionary_version, dictionary_digest,
reference_status, terms, decisions, and candidates. Candidates include id,
term, normalized, scope with repo and product, pending status, reference_status,
and observations containing path, positive line number, sentence, and
context_digest. Draft export additionally requires every shown observation to
have context_binding equal to transpara-source-occurrence-v1, its exact term,
and a valid start/end span in the displayed extracted line. Offsets count
Unicode code points, start is inclusive, and end is exclusive. The span must
contain that exact term; hashes must be 64 lowercase hexadecimal characters.
These checks establish the current format, not trusted authorship or approval.

Legacy exports, including those with complete older line-only hashes, remain
readable but cannot export a decision. The page explicitly asks for a re-scan
and Refresh. Preserve the old evidence, scan into new queue/snapshot filenames
with the current core, and ask a Human to review replacement drafts. Do not
automatically migrate canonical dictionary decisions. See the core
[occurrence contract](https://github.com/transpara-ai/technical-english/blob/a736bbf/REFERENCE.md)
for hash construction. Wiki always reports conformance as not_assessed.

The API uses the existing authoring-access guard and no-store responses.
It also reuses the evidence workspace's principal check before reading the
snapshot: a remote caller needs a verified signed-in principal as well as
authoring access. A shared token or client-supplied identity header alone does
not suffice. Existing loopback curator behavior is retained. An unavailable
profile fails closed with a generic error and no snapshot read.
Without the connected authority service, POST requests receive 405. With it,
browser mutations also require the configured Origin/custom header and verified
principal before they reach the private service. Assets are omitted
from company-internal output, and the API returns 404 when the runtime
KNOWLEDGE_HUB_PROFILE is not authoring-local. Snapshot contents are never
copied into static output or a public profile.

## Reference and limits

[ASD-STE100 remains an external reference](https://www.asd-ste100.org/STE_downloads.html).
This implementation contains none of its dictionary, rules text, or original
PDF. Without a separately authorized vocabulary source, candidates are
unassessed; unfamiliar text is not presented as a confirmed ASD violation.

The connected browser service adds durable proposals, prepared publications,
verified Human/workload proofs, publication history, and principal-owned scan
jobs. Repository adoption and legacy check configuration still belong to the
independent technical-English tool. Snapshot-only deployments continue to need
operator-generated exports; publication does not silently migrate old occurrence
evidence to a new dictionary.

One snapshot-only request reads and parses at most 1 MiB. Whole raw and decoded JSON content
each pass through the existing evidence scanner; no chunking or runtime waiver
is used. The UI displays at most 100 matching
candidates, ten observations per selected candidate, and 100 terms or ledger
entries. Candidate search can narrow a larger queue. These are bounded resource
limits, not measured performance guarantees.
Occurrence validation is linear in the displayed source text and uses temporary
Unicode character arrays within the same snapshot size bound. It adds no model
or network call. Server access verification can use the existing userinfo
request with a five-second timeout; remembered-grant access can invoke it once
for the grant check and once for the principal check, as in the evidence
workspace. Account identity reuses that existing verification integration;
publication adds the independent Human proof described above. No separate
latency measurement is claimed.

The connected workflow has these additional bounds:

| Work | Bound and consequence |
| --- | --- |
| Capture | 300 actual requests including redirects, 60 seconds, 256 captured files, 1 MiB per file, and 16 MiB of response payloads and extracted text each. Limits produce explicit incomplete coverage. |
| Redirects and trees | Five same-origin redirects per request; truncated repository trees are refused. |
| Reports | At most 1 MiB including originals/drafts and findings. Narrow paths when a report cannot fit. Skipped-file detail is sampled to 256 entries with total/truncation counts. |
| Rewrite | The Wiki adapter permits at most 64 KiB of captured input and one model call with a 60-second wall bound. Larger inputs retain the report without an accepted rewrite. |
| Jobs | Eight queued/running jobs overall, two workers, one unfinished job per principal. Interrupted or expired work fails visibly. |
| Retention | Finished jobs expire after seven days; retain at most 100 reports and 32 MiB of report content. Evicted or expired IDs become unavailable. |
| Publication | Ten-minute preparation window; bounded pending preparations and enrollments. Failed or stale approval preserves the active dictionary. |

Closing the tab stops its polling and does not cancel an already submitted job.
The next page load restores this account's latest retained job and resumes its
status/report. The UI has no older-job history list. Cancel explicitly when work
should stop, and download reports that must outlive retention. Do not clear
private state or replace trust to work around a failure.

These are implementation limits, not measured production capacity. Before
activation, operators must record representative acquisition/analysis duration,
peak memory, report/database size, model input/output size, latency, and
cancellation/deadline behavior on the approved host. Separate HTTP subprocesses
bound public capture DNS/TLS/body waits; their startup adds per-request resource
cost inside the same 60-second job budget.

## Verification

Python tests exercise private access, snapshot-only read behavior, profile
isolation, CSRF/principal checks, bounded files/jobs, schema failures, and
non-disclosure of configured host paths. Fake-network acquisition tests cover
public DNS pinning, redirects, commit/blob identity, deadlines, cancellation,
partial coverage, and the absence of repository execution. Public passkey
envelopes have transport/schema tests; the independent publisher's tests verify
the actual Human/workload signatures, replay, stale bases, and transaction
failure using disposable credentials and temporary roots.
Browser tests exercise the two draft classifications, literal rendering of
hostile source text, download contents, refresh failure, empty state, keyboard
focus, and a 390-pixel viewport. Legacy hashes and malformed source spans block
export. Set WIKI_TERMINOLOGY_TEST_SNAPSHOT to a fresh core export when running
the focused browser suite for integration; its displayed occurrence hashes must
remain unchanged in the downloaded draft. The default browser fixture exercises
the same current format without depending on another checkout. The browser
workflow suite also covers durable submission, publication previews, passkey
cancellation, scan status/cancellation, and inspection of original/draft/diff.
Passing fixtures do not establish production trust enrollment or measured
deployment capacity.

## Revision History

| Version | Date | Change |
| --- | --- | --- |
| 0.2.1 | 2026-11-05 | Document the inactive-by-default host GitHub credential adapter, exact repository/cohort authorization, and credential confinement. |
| 0.2.0 | 2026-11-05 | Document browser contributions, pending passkey enrollment, Human/workload publication, bounded repository/URL analysis and rewrite drafts, retention, and operator integration. |
| 0.1.3 | 2026-11-04 | Limit regular-English draft hashes to the exact classified spelling and state the existing curator cohort's export-content boundary. |
| 0.1.2 | 2026-11-04 | Use a verified short immutable core commit reference so the documentation passes the repository's entropy scan. |
| 0.1.1 | 2026-11-04 | Require current occurrence bindings and exact Unicode source spans for draft export; retain legacy evidence with an explicit re-scan path. |
| 0.1.0 | 2026-11-04 | Add the private read-only terminology workspace and draft-proposal contract. |
