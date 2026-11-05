---
doc_id: WIKI-USER-MANUAL
title: Wiki user manual
entity: Wiki user manual
doc_type: user_manual
status: draft
version: 0.2.1
created: "2026-11-05"
updated: "2026-11-05"
owner: Transpara
steward: Codex
project: wiki
supersedes: []
canonical: false
org: transpara
tier: meta
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
  - https://github.com/apple-oss-distributions/shell_cmds/blob/main/hexdump/od.1
  - https://learn.microsoft.com/en-us/dotnet/api/system.security.cryptography.randomnumbergenerator.getbytes?view=netframework-4.8
  - https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/set-clipboard?view=powershell-5.1
  - https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse
  - https://docs.docker.com/reference/cli/docker/compose/up/
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

This token grants the instance's existing authoring access across all spaces,
including source and monitor changes and approval and publication of article
bundles. A saved authoring grant carries the same access. Remote Workspace
operations also require a verified signed-in account. The implementation has
no separate curator or publisher role check: token access is not limited to
drafting. Confirm that the recipient is already authorized for this full
scope before sharing the token.

### Request access

1. Ask the **wiki deployment operator** for authoring access. Identify the wiki
   address, your signed-in account, and the work you need to do. State that the
   request includes the full authoring and publication access described above.
   If you do not know the operator, ask the responsible space steward to route
   the request.
2. The operator confirms your existing authorization for that full scope and
   shares the existing token through an approved password manager's secure sharing
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

**An ordinary author needs the token already configured on the wiki. Generating
another value on your computer does not register it with the server.** Reuse the
existing token unless this is first setup or an explicitly planned rotation.
Changing an existing token also invalidates every saved authoring grant.

For an existing deployment, the operator opens its private configuration file,
finds `KNOWLEDGE_HUB_AUTHORING_TOKEN=`, and shares **only the value after `=`**
through the approved password manager. The Docker and native file locations are
listed below. Do not create a new token for each author.

For first setup or an authorized rotation, follow **one** generation method
below, save the result in the password manager, install that same value on the
wiki server, and verify it in Ingest. Each method generates **32 random bytes
(256 bits), represented as 64 lowercase hexadecimal characters**. Generation
alone does not change the running wiki.

The earlier `openssl rand -hex 32` command requires the `openssl` program;
`rand` is its subcommand, not a separate executable. The methods below need
**neither OpenSSL nor Python**, and do not require Homebrew or WSL.

#### Ubuntu: check the terminal and required tools

Open Terminal on the Ubuntu computer where you will generate the token. Run:

```sh
ps -p $$ -o comm=
```

Continue in Bash or zsh. If the output names another shell, run `/bin/bash`
first and keep using that terminal. Check the required system tools and the
operating system's random device:

```sh
command -v od && command -v tr && command -v grep && test -r /dev/urandom && printf 'Required tools are ready.\n'
```

Expect three executable paths followed by `Required tools are ready.` If a
command is missing, install its standard Ubuntu packages, then repeat the check:

```sh
sudo apt update
sudo apt install --yes coreutils grep
```

The `sudo` password is your Ubuntu account password. It is not a wiki token.
Continue with **Generate on Ubuntu or macOS** below.

#### macOS: check the terminal and required tools

Open **Applications → Utilities → Terminal**. Run:

```sh
ps -p $$ -o comm=
```

The normal default is zsh. The following commands also work in Bash. If another
shell is running, enter `/bin/zsh` first and keep using that terminal.

```sh
command -v od && command -v tr && command -v grep && command -v pbcopy && test -r /dev/urandom && printf 'Required tools are ready.\n'
```

Expect four executable paths followed by `Required tools are ready.` These are
macOS system tools. This procedure does not install a package manager. If the
check fails, stop and generate on the Ubuntu server using the Ubuntu steps;
do not paste a guessed or empty value into the wiki configuration.

#### Generate on Ubuntu or macOS

Paste this whole block into the checked Bash or zsh terminal:

```sh
if wiki_authoring_token="$(set -o pipefail; od -An -v -N32 -tx1 /dev/urandom | LC_ALL=C tr -d '[:space:]')" &&
    printf '%s\n' "$wiki_authoring_token" | LC_ALL=C grep -Eq '^[0-9a-f]{64}$'; then
    printf 'Created a token with 64 hexadecimal characters.\n'
else
    unset wiki_authoring_token
    printf 'Token generation failed. Stop here.\n' >&2
fi
```

Expect `Created a token with 64 hexadecimal characters.` Stop if that message
does not appear or any command reports an error. `od` reads 32 bytes from the
OS random device and formats each byte as two hexadecimal digits; `-v` keeps
repeated bytes from being abbreviated. `tr` removes formatting whitespace.
The pipeline check and validation refuse command failures and empty, short, or
malformed results. `pipefail` is set only inside the generation command; it
does not change your interactive shell settings.

On **macOS**, copy the value to the clipboard without printing it:

```sh
printf '%s' "$wiki_authoring_token" | pbcopy
```

On **Ubuntu**, display it in your private terminal, select the one line of 64
characters, and copy it with **Ctrl+Shift+C**:

```sh
printf '%s\n' "$wiki_authoring_token"
```

Paste the value into a new password-manager entry named for the wiki instance,
including its browser address so you can find the right token later. Copy only
the 64 characters, without quotes, spaces, the variable name, or a command.
Keep that entry available for the server configuration step. After saving it,
remove the temporary shell variable:

```sh
unset wiki_authoring_token
```

#### Windows: generate with Windows PowerShell or PowerShell 7

Open **Start**, search for **Windows PowerShell**, and open it. PowerShell 7 is
also supported. Use a PowerShell window, not Command Prompt. Check the version:

```powershell
$PSVersionTable.PSVersion
```

Expect version **5.1** or **7.x**. No administrator window or additional software
is needed for generation. Paste this whole block:

```powershell
& {
    $ErrorActionPreference = 'Stop'
    $wikiBytes = New-Object -TypeName 'System.Byte[]' -ArgumentList 32
    $wikiRng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try {
        # This instance API works in both Windows PowerShell 5.1 and PowerShell 7.
        $wikiRng.GetBytes($wikiBytes)
        $wikiToken = [System.BitConverter]::ToString($wikiBytes).Replace('-', '').ToLowerInvariant()
        if ($wikiToken -cnotmatch '\A[0-9a-f]{64}\z') {
            throw 'Token generation failed. Stop here.'
        }
        Set-Clipboard -Value $wikiToken
        Write-Output 'Created a 64-character token and copied it to the clipboard.'
    }
    finally {
        $wikiRng.Dispose()
    }
}
```

Expect `Created a 64-character token and copied it to the clipboard.` The token
itself is not printed. If PowerShell reports an error, stop; do not use whatever
was previously on the clipboard. The block uses Windows' cryptographic random
generator, converts the 32 bytes into 64 lowercase hexadecimal characters,
validates that format, and copies the result.

Paste the clipboard value into a new password-manager entry named for the wiki
instance, including its browser address. That saved value is what you install on
the server. After it is saved and installed, you can replace the current
clipboard entry with non-secret text:

```powershell
Set-Clipboard -Value 'Wiki token configured'
```

This replaces the current clipboard entry; it does not erase clipboard history.

#### Install the value on the wiki server

The steps above run on your operator computer. **A token generated on a Mac or
Windows computer still has to be configured on the Ubuntu server that runs the
wiki.** Copy it from the password manager when the server's editor is open.

Use your existing SSH access to that server. From any of the three systems,
check the SSH client with `ssh -V`. If it is missing on Ubuntu, install it with
`sudo apt install --yes openssh-client`. If it is missing on Windows, open
**Windows PowerShell as Administrator**, run the following, then reopen your
ordinary PowerShell window and repeat `ssh -V`:

```powershell
Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0
```

This installs the client used to connect to the wiki; no Windows SSH server is
needed. macOS includes the SSH client. Connect through the existing approved
host or SSH alias. On the Velia administration network, the documented command is:

```sh
ssh transpara@192.168.30.192
```

That address is private; use your existing VPN or SSH route to reach it. An SSH
password prompt asks for the server account's password, not the wiki token.
Once connected, the following file-edit and service commands run **on Ubuntu**,
not in your local Windows PowerShell session.

For the current **Docker deployment on Velia**, the private file is
`/Transpara/transpara-ai/repos/wiki/.env`. On another Docker host, use that
instance's project directory. To inspect the current Velia container's project
directory and ordered Compose files without printing its environment:

```sh
sudo docker inspect --format 'directory={{index .Config.Labels "com.docker.compose.project.working_dir"}} files={{index .Config.Labels "com.docker.compose.project.config_files"}}' transpara-wiki-wiki-1
```

On a first installation where `.env` does not exist, create it from the
project's `.env.example`. For the documented Velia directory, run:

```sh
(umask 077; set -C; cat /Transpara/transpara-ai/repos/wiki/.env.example > /Transpara/transpara-ai/repos/wiki/.env)
```

`set -C` refuses to overwrite an existing file. On another host, substitute its
actual project directory in both paths. Complete the other hosting settings in
the Docker hosting guide before starting services.

On Velia, open the existing file in its actual project directory:

```sh
cd /Transpara/transpara-ai/repos/wiki
chmod 600 .env
nano .env
```

If `nano` is missing, install it on the Ubuntu server with
`sudo apt install --yes nano`, then reopen the file.

Find the line beginning exactly `KNOWLEDGE_HUB_AUTHORING_TOKEN=`. Replace only
its value with the 64 characters copied from the password manager. Add the line
if it is absent, and keep one active assignment for this key. The result is
this **file-content template**, not a terminal command:

```dotenv
KNOWLEDGE_HUB_AUTHORING_TOKEN=<paste-token-here>
```

Replace all of `<paste-token-here>`, including the angle brackets, with your
generated value. Use no surrounding quotes or spaces. Preserve every unrelated setting, especially `COMPOSE_FILE`,
allowed hosts, port, and user/group IDs. In nano, press **Ctrl+O**, **Enter**, then
**Ctrl+X** to save and exit. Reapply private file permissions:

```sh
chmod 600 .env
```

For the **native systemd deployment**, edit
`~/.config/transpara-knowledge-hub.env` as the same Ubuntu user who owns the wiki
service, using the same key/value format and nano save steps:

```sh
mkdir -p "$HOME/.config"
(umask 077; touch "$HOME/.config/transpara-knowledge-hub.env")
chmod 600 "$HOME/.config/transpara-knowledge-hub.env"
nano "$HOME/.config/transpara-knowledge-hub.env"
```

The editor creates that file if absent; preserve any other existing settings.
Confirm the service's file locations without displaying their contents:

```sh
systemctl --user show transpara-knowledge-hub.service -p WorkingDirectory -p EnvironmentFiles
```

The native unit loads the legacy environment file first and the current file
second. `CIVWIKI_AUTHORING_TOKEN` is a lower-priority compatibility alias; use
`KNOWLEDGE_HUB_AUTHORING_TOKEN` in the current file.

#### Apply the setting and confirm authoring works

Choose the deployment type you actually use. This step changes the running
service; perform it in the deployment's authorized maintenance procedure after
active authoring work finishes. A deliberate rotation invalidates old tokens
and saved grants for all authors.

For the **existing Velia Docker deployment**, preserve the full stack, including
authentication and other overrides. In a Bash or zsh terminal on that Ubuntu
server, read its project, directory, context, and ordered Compose files from
the running wiki container. These setup commands inspect labels, not secrets:

```sh
wiki_container=transpara-wiki-wiki-1
wiki_context=$(sudo docker context show)
wiki_project=$(sudo docker --context "$wiki_context" inspect --format '{{index .Config.Labels "com.docker.compose.project"}}' "$wiki_container")
wiki_directory=$(sudo docker --context "$wiki_context" inspect --format '{{index .Config.Labels "com.docker.compose.project.working_dir"}}' "$wiki_container")
wiki_files=$(sudo docker --context "$wiki_context" inspect --format '{{index .Config.Labels "com.docker.compose.project.config_files"}}' "$wiki_container")
wiki_compose=(sudo docker --context "$wiki_context" compose --project-name "$wiki_project" --project-directory "$wiki_directory" --env-file "$wiki_directory/.env")
while IFS= read -r wiki_file; do
    wiki_compose+=(-f "$wiki_file")
done < <(printf '%s\n' "$wiki_files" | tr ',' '\n')
"${wiki_compose[@]}" config --quiet
"${wiki_compose[@]}" config --services
```

Stop if any command fails, a label is empty, or the named container does not
exist. On another Docker deployment, obtain its wiki container name with
`sudo docker ps --filter label=com.docker.compose.service=wiki --format '{{.Names}}'`
and use that name rather than Velia's name. On a first installation without
running containers, use the Docker hosting guide's initial start procedure
after completing `.env`; these label-based update commands require an existing
instance.

`config --quiet` succeeds without output. On current Velia,
`config --services` includes `wiki`, `refresh`, and `discovery`. Keep this
terminal open so the `wiki_compose` array remains available. It pins the same
project, directory, context, and ordered files even if `COMPOSE_FILE` is exported
elsewhere. Recreate only those three token-consuming services:

```sh
unset KNOWLEDGE_HUB_AUTHORING_TOKEN CIVWIKI_AUTHORING_TOKEN
"${wiki_compose[@]}" up -d --force-recreate --wait --wait-timeout 300 wiki refresh discovery
```

Do not replace the complete ordered file selection with `-f compose.yaml`
alone. For a different deployment, retain its actual service list rather than
assuming it has Velia's discovery worker. A plain `docker restart` does not load changed container
environment values. Recreation runs the existing startup wiki build and can
interrupt service until it becomes healthy; it does not just reload a string.
The command waits up to 300 seconds and reports a startup failure.

For an **already installed native deployment**, restart its authoring service
as the service-owning Ubuntu user:

```sh
systemctl --user restart transpara-knowledge-hub.service
systemctl --user is-active transpara-knowledge-hub.service
```

Expect `active`. Do not start the native service alongside the Docker writer.
If the installation still uses the legacy service name, operate that existing
unit instead; the two service families must not run together.

Finally, open the real wiki authoring address in a browser and select **Ingest**.
Use the verification path supported by that instance:

- **Signed-in profile available:** sign in, copy the configured value from the
  password manager into **Authoring token**, and choose **Remember authoring
  access**. Expect **Authoring access is saved to your wiki profile** and an
  empty token field. This verifies the token and saves the account grant.
- **Token-only instance without profiles:** first leave **Authoring token**
  empty, choose **Remove**, and select the existing **The Event Graph** article.
  Expect **Preview unavailable**. Stop if consequences already appear: local
  loopback authoring is permitted when no token is configured, so that result
  does not prove that your new setting loaded. Then return to **Add**, enter the
  configured value from the password manager, reopen **Remove**, and select
  **The Event Graph** again. Expect its hypothetical retirement consequences.
  Both previews are read-only requests: they change no content and consume no
  operation authorization. Leave confirmation unchecked throughout, do not
  select **Retire after preview**, and return to **Add** after checking. This
  verifies refusal without the token and acceptance with it; it does not save
  an account grant.

A healthy server response alone does not verify token acceptance, and a static
preview cannot perform either check. If the expected result does not appear,
stop and have the operator check the selected instance, loaded environment file,
service recreation, and any required profile configuration before submitting
content.

API clients use the same configured value in `X-CivWiki-Authoring-Token`.
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
publish** for the current revision. The service uses the same authoring grant
for this action; it does not enforce a separate publisher role. A manual review
decision requires a substantive recorded rationale and still passes deterministic validation. A
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
| 0.2.1 | 2026-11-05 | Add the negative token-only verification check so unconfigured loopback access cannot be mistaken for a loaded token. |
| 0.2.0 | 2026-11-05 | Add complete Ubuntu, macOS, and Windows token-generation, copying, installation, activation, and verification steps with explicit prerequisites. |
| 0.1.1 | 2026-11-05 | Clarify the existing token's full authoring and publication scope and the absence of a separate publisher role before sharing access. |
| 0.1.0 | 2026-11-05 | First manual: reading, authoring-token requests and lifecycle, source ingestion, Workspace, terminology, troubleshooting, and native publishing recommendation. |
