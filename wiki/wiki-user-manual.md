---
doc_id: WIKI-USER-MANUAL
title: Wiki user manual
entity: Wiki user manual
doc_type: user_manual
status: draft
version: 0.1.0
created: "2026-11-05"
updated: "2026-11-05"
owner: Transpara
steward: Codex
project: wiki
supersedes: []
canonical: false
org: transpara
primary_placement: devops/runbooks
placements: [devops/runbooks, civilization/meta, platform/deployment-operations, competition/research-methods]
classification: internal
source_authority: engineering-docs
last_compiled: "2026-11-05"
sources:
  - https://github.com/transpara-ai/wiki/blob/v0.10.0/README.md
  - https://github.com/transpara-ai/wiki/blob/v0.10.0/DOCKER.md
  - https://github.com/transpara-ai/wiki/blob/v0.10.0/docs/profile-menu.md
  - https://github.com/transpara-ai/wiki/blob/v0.10.0/compile/DISCOVERY.md
  - https://github.com/transpara-ai/wiki/blob/v0.10.0/docs/terminology-workspace.md
---

# Wiki user manual

This manual explains the Transpara Knowledge Hub for readers and approved
authors. It describes version 0.10.0. Find it under **DevOps → Runbooks** or
search for **Wiki user manual** in any space. Its stable wiki address is
`/wiki-user-manual.html`.

The manual is a draft pending Human acceptance. It belongs to the private
authoring publication. A restricted company publication can omit this manual
and the authoring tools. The tools available on your wiki depend on its
publication profile and operator configuration.

## Start reading

1. Open the Knowledge Hub portal and select a space: **Civilization**,
   **Transpara Platform**, **Competition**, or **DevOps**.
2. Use **Browse this space** to open articles. On a narrow screen, expand this
   control first. An article's contents links jump to its headings.
3. Follow article links and inspect cited sources. One article can appear in
   several spaces while keeping the same address and body.

The selected space also scopes Repos, Sources, Ingest, and search. **All spaces**
broadens search. The wiki is advisory: running systems, source repositories,
accepted decisions, and release records retain their own authority. A draft,
proposal, or historical account is not evidence that a feature is deployed.

## Search and Ask

Choose **Search** to find article links and excerpts. Select the relevant space
or **All spaces**, enter meaningful words, and open a result. Search does not
synthesize an answer.

Choose **Ask** for an answer grounded in published articles. When the service
is configured, signed-in readers can choose the provider, model, and available
effort, then submit a question. Inspect the article citations before relying on
an answer. Ask can be unavailable when the provider service is not configured
or cannot complete the request. Search remains useful without that service.

Reading and Ask do not require an authoring token. Ordinary Ask conversations
are transient; follow-up context lives in the current page's memory. **Save
answer** retains an answer in your account, and **Request evidence review**
queues feedback for a curator. **Research / propose** opens Workspace; it does
not transfer or save the answer automatically. Start a research investigation
there when you need retained evidence. Ask does not automatically search the
web or publish an article.

## Acquire an authoring token

Signing in through tAuth identifies your account. Authoring needs a separate
authoring token or a previously saved authoring grant. The wiki currently uses
**one shared authoring token per deployment**, rather than individual tokens.
There is no self-service token issuance or token-retrieval page or API.

### Request access

1. Ask the **wiki deployment operator** for authoring access. Identify the wiki
   address, your signed-in account, and the work you need to do. If you do not
   know the operator, ask the responsible space steward to route the request.
2. The operator confirms that you may author on that instance and shares its
   existing token through an approved password manager's secure sharing
   mechanism. This is the documented access-request procedure; the wiki does
   not automate the request or approval.
3. Open **Ingest**, enter the token in **Authoring token**, and choose
   **Remember authoring access** while signed in. Leaving the token field also
   attempts to save access when profile support is available.
4. Confirm **Authoring access is saved to your wiki profile**. The field clears
   after a successful save. Later visits and other browsers can use the grant
   when you sign in to the same account on that instance.

If remembered access is unavailable on your connection, enter the token for
the current authoring visit. Workspace has an **Authoring access** panel with a
token field and **Connect**. Other tools can request the same token when no
saved grant is available. A static preview cannot save profile access or carry
out authoring operations; use the operator-provided authoring address.

Keep the token in the approved password manager. Do not put it in wiki content,
source uploads, URLs, repository files, screenshots, logs, or ordinary chat.
The shared token does not grant access to source repositories or replace
separate authorization required for destructive operations.

### Operator: provide or initialize the token

For an existing instance, use its configured token; generating a different
value for each author will not work. Docker hosting configures
`KNOWLEDGE_HUB_AUTHORING_TOKEN` in the deployment's private `.env`. A native
systemd installation loads `~/.config/transpara-knowledge-hub.env`. Confirm
which service and environment file actually serve the requested wiki.

If an instance has no token yet, an authorized operator can generate a random
32-byte value locally with `openssl rand -hex 32`, put it in that environment
setting, and retain it in the approved password manager. Protect the private
environment file with mode `0600` and keep it outside Git and published output.
Apply configuration through the existing hosting procedure, restarting the
native service or recreating the Docker service so it receives the setting.
This manual does not perform that operational change.

`CIVWIKI_AUTHORING_TOKEN` is a compatibility fallback; the
`KNOWLEDGE_HUB_AUTHORING_TOKEN` setting takes precedence. API clients still use
the `X-CivWiki-Authoring-Token` request header. Never send tokens in URLs.
Without a configured token, authoring is limited to local loopback clients and
the existing same-origin checks; this is not a remote access-request mechanism.

### Forgetting, logout, and revocation

The token and saved grants have no built-in expiry. **Log out** ends your login
session and clears the token field, but preserves the saved authoring grant.
**Forget authoring access** removes your account's saved grant. A person who
still knows the shared token can enter it again and regain access.

If a token is disclosed, or an author who knows it must lose access, notify the
operator. The operator must replace the configured shared token and restart or
recreate the authoring service. Rotation invalidates the old token and all
remembered grants; every approved author must enroll again with the new value.
Forgetting one grant alone does not revoke a copied token.

## Add sources with Ingest

1. Open **Ingest** from the relevant space or article. Check the selected space,
   steward, section, and target article before submitting.
2. Choose **Add** and the intended target. Add files, source URLs,
   or **Paste email or other text**. Give pasted material a useful title and
   include its sender, date, and subject when those facts matter.
3. Review the selected target and material, then choose **Ingest and rebuild**.
   Wait for the result before submitting another operation.
4. Read the resulting source links and the article's synthesis status.

Source registration retains evidence and updates its links. It does not
automatically incorporate that evidence into existing article prose. New
evidence can mark synthesis pending. An author must review and incorporate the
material before declaring the article current. Re-uploading an already attached
document does not itself require another synthesis update.

**Replace** supersedes a source; **Remove** retires a topic. Both require a consequence
preview, confirmation, and a matching single-use authorization artifact placed
by an authorized operator before submission. The authoring token alone is
insufficient. Ask the operator to arrange that procedure before replacing a
source or retiring a topic.

Only offer material approved for the wiki's audience. Keep credentials,
customer production content, and unauthorized prospect evidence out of uploads
and pasted text. If a format is refused, supply an approved UTF-8 text or
Markdown export; do not assume the service converted or retained a rejected file.

## Use Workspace for research and publication

Workspace requires authoring access and an operator-configured worker and model
services. Missing configuration or unavailable reviewers leaves work visibly
incomplete. Check **Activity & jobs** for the reported cause.

### Sources & Monitors

Choose **Add source**, specify the exact repository, page, or feed, and set its
curator, permitted audience, collection scope, interval, and budgets. A host
credential reference names an operator-managed credential; enter its approved
reference, never a secret. Choose **Save disabled source**, then **Preview**,
inspect the accessible scope, and explicitly **Enable** it.

Repository suggestions do not enable monitoring. Editing a source disables it
and requires a new preview; a preview also expires after one hour. **Pause**
and **Retire** preserve history. A source's changed ownership or audience can
require a fresh audience decision before collection or publication continues.
Collection observes snapshots and may miss intermediate edits.

### Research

Enter a question and space, then choose **Start investigation**. Use **Capture
source** for a specific HTTPS address or **Retain evidence** for an observation
or excerpt. These actions retain evidence before synthesis. **Search the web
for this question** needs a separately configured search adapter.

Choose **Investigate captured sources** to synthesize the retained evidence.
Inspect findings, citations, and open questions, then explicitly choose
**Propose article changes** to start drafting and review. **Save research
snapshot** retains a private snapshot. Closing an investigation preserves its
evidence; it does not publish it. **Capture and propose** in the document/text
form retains a submission and queues drafting directly.

### Review queue

Open **Inspect evidence, objections and diff**. Read the source evidence,
proposed article text, coverage limits, both reviewers' assessments, and any
objections. Organization scores help prioritize work; they do not approve it.

**Save edits and invalidate review** saves a revision that needs fresh review.
Use **Run fresh review**, **Request revision**, **Defer**, or **Reject** as
appropriate. Changed article or evidence revisions can make an earlier review
stale. An unavailable required reviewer is incomplete review.

An authorized curator explicitly chooses **Approve reviewed bundle and
publish** for the current revision. A manual review decision requires a
substantive recorded rationale and still passes deterministic validation. A
successful publication builds and exchanges the served artifact; failed
validation or rebuilding preserves the previous served site. Models and
scheduled monitors do not approve publication.

## Review terminology

Open **Terminology**, use your authoring access, and select a candidate. Read
its source sentences and dictionary revision. Propose either an immutable
Transpara term, with its meaning and permitted forms, or a regular-English
decision for the exact spelling and reviewed occurrences.

Download the draft and give it to the Human dictionary maintainer through the
existing review process. A download neither approves terminology nor publishes
a dictionary change. The separate technical-English repository owns the
dictionary. After an accepted change, the operator regenerates its snapshot;
select **Refresh** to read it. An unavailable or obsolete snapshot requires
operator action, and some older snapshots can be read but cannot export drafts.

## Troubleshooting

| Symptom | What to do |
| --- | --- |
| Authoring token required, or a previously working token is refused | Confirm the wiki instance and request its current token from the operator. Signing in alone does not enable authoring. Rotation also requires saving access again. |
| Remembered access is unavailable | Use the actual authoring service and sign in there. Ask the operator to check profile configuration; use the valid token for the current visit if supported. |
| A same-origin request is refused | Return to the operator-provided wiki address and retry from its own page. Ask the operator to check the configured origin and proxy if refusal persists. |
| Workspace or Terminology is unavailable | Ask the operator to check the worker, reviewer configuration, or terminology snapshot identified by the tool's error. A static preview cannot supply these services. |
| A proxy returns 502/504 during an ingest or rebuild | Check the site's updated time and Activity before repeating the action. The operation may still have completed after the proxy stopped waiting. |
| A job failed or is deferred | Inspect Activity & jobs, resolve the stated configuration, budget, or source problem, then use the offered retry action. Retained evidence is not proof of completed synthesis. |
| A source was added but the article still omits it | Check synthesis status. Source registration and article synthesis are separate steps. |

The profile menu offers account settings and logout when the existing tAuth
integration is available. Direct local previews can omit it. Ask the operator
for help with login, deployment, or a missing tool rather than changing the
wiki's authentication settings yourself.

## Manual format and maintenance

The recommended format is task-oriented **Markdown with YAML frontmatter**,
stored as a normal wiki article and compiled to HTML by the existing
Python-Markdown builder. That builder already supplies heading anchors, a
table of contents, article navigation, and Search/Ask indexing. The manual
shares the wiki's hosting, version control, and publication boundary. No
additional documentation generator, service, or browser framework is required.
Python-Markdown's [bundled extensions](https://python-markdown.github.io/extensions/)
provide the existing tables, fenced code blocks, and table of contents.

Keep procedures organized by user task and link to detailed operator references
instead of duplicating their deployment instructions. The source references
below identify the implementation baseline used for this edition. The
repository's documentation index also lists rebuilding, API, hosting, profile,
discovery, and terminology guides. Recheck labels and access behavior when
those features change; preserve this document's identity and update its version
and revision history.

Reading this manual requires no model call. Adding one article increases the
HTML output and the existing search and answer indexes; search retains up to
12,000 characters of article text, while Ask indexes the article body. These
are implementation characteristics, not measured timing results. If the manual
grows, measure build time, generated index bytes, and browser search loading on
the same corpus before accepting a larger structure or another generator.

## Revision History

| Version | Date | Change |
| --- | --- | --- |
| 0.1.0 | 2026-11-05 | First manual: reading, authoring-token requests and lifecycle, source ingestion, Workspace, terminology, troubleshooting, and native publishing recommendation. |
