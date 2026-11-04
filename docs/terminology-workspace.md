---
doc_id: WIKI-TERMINOLOGY-WORKSPACE
title: Terminology workspace manual and integration reference
doc_type: implementation_reference
status: draft
version: 0.1.3
created: 2026-11-04
updated: 2026-11-04
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
It prepares a draft decision file. It does not approve or publish terminology.

## Design and authority

The independent [technical-english repository](https://github.com/transpara-ai/technical-english)
owns the canonical dictionary document and scanner. Wiki reads a configured
snapshot and never changes that document. The existing Wiki article-publication
endpoint is not used for dictionary decisions. This Designed implementation
adds no publication authority, new role, or approval capability.

The snapshot belongs to the same single internal curator cohort as the existing
private evidence workspace. Before configuring its path, the operator must
confirm that all of its contents are authorized for every existing internal
curator. Keep the export within its source material's confidentiality boundary.
It grants no source-repository access and admits no broader audience. The
default is unconfigured and returns 503; company/public profiles return 404
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
It carries no claimed reviewer identity and has no authority
until a Human maintainer accepts the corresponding canonical document change.
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
5. Download the draft proposal and offer it to the Human dictionary maintainer.
6. After the Human-owned dictionary change is accepted, regenerate the scanner
   snapshot and select Refresh.

The page does not persist selections or tokens in browser storage. Refresh
clears the selection so an earlier draft is not exported against a later
snapshot. Candidate state remains pending after a download.

## Configure the read-only snapshot

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
POST requests receive 405 and cannot approve or publish. Assets are omitted
from company-internal output, and the API returns 404 when the runtime
KNOWLEDGE_HUB_PROFILE is not authoring-local. Snapshot contents are never
copied into static output or a public profile.

## Reference and limits

[ASD-STE100 remains an external reference](https://www.asd-ste100.org/STE_downloads.html).
This implementation contains none of its dictionary, rules text, or original
PDF. Without a separately authorized vocabulary source, candidates are
unassessed; unfamiliar text is not presented as a confirmed ASD violation.

This Wiki slice does not supply a Human approval service, signed releases,
publication history, or automatic snapshot-refresh jobs. Repository adoption,
scanning, and check configuration belong to the independent technical-English
tool. Any future browser approval or publication service needs verified Human
approval controls and a separate review of that authority boundary.

One request reads and parses at most 1 MiB. Whole raw and decoded JSON content
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
workspace. No new authentication service is added, and no separate latency
measurement is claimed.

## Verification

Python tests exercise private access, read-only behavior, profile isolation,
bounded files, schema failures, and non-disclosure of configured host paths.
Browser tests exercise the two draft classifications, literal rendering of
hostile source text, download contents, refresh failure, empty state, keyboard
focus, and a 390-pixel viewport. Legacy hashes and malformed source spans block
export. Set WIKI_TERMINOLOGY_TEST_SNAPSHOT to a fresh core export when running
the focused browser suite for integration; its displayed occurrence hashes must
remain unchanged in the downloaded draft. The default browser fixture exercises
the same current format without depending on another checkout.

## Revision History

| Version | Date | Change |
| --- | --- | --- |
| 0.1.3 | 2026-11-04 | Limit regular-English draft hashes to the exact classified spelling and state the existing curator cohort's export-content boundary. |
| 0.1.2 | 2026-11-04 | Use a verified short immutable core commit reference so the documentation passes the repository's entropy scan. |
| 0.1.1 | 2026-11-04 | Require current occurrence bindings and exact Unicode source spans for draft export; retain legacy evidence with an explicit re-scan path. |
| 0.1.0 | 2026-11-04 | Add the private read-only terminology workspace and draft-proposal contract. |
