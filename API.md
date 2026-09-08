# Wiki authoring API

The local authoring endpoint is `http://127.0.0.1:8787`. The Docker deployment
serves the same API through its configured private Tailscale URL. Use the URL
reachable from the importing session; localhost refers to that session's host.

All writes use the existing editor authorization. When an editor token is
configured, send it in `X-CivWiki-Authoring-Token`. Read it from your environment
or approved local configuration; never put its value in a prompt, article, or
log. With no configured token, only same-origin/loopback authoring is allowed.

## Discover spaces and existing articles

- `GET /api/health` reports server availability.
- `GET /version.json` reports the installed wiki version.
- `GET /api/spaces` lists space keys, stewards, section keys, source authorities,
  and which spaces support `new_article`.
- `GET /api/articles` lists active articles and their slugs, placements, and
  stewards. Authorized callers also receive source references. Filter
  `placements` for `devops/` locally.

## Create a DevOps article

`POST /api/ingest` accepts **multipart/form-data** or URL-encoded form fields,
not JSON. Send requests sequentially, with a timeout of at least 300 seconds;
each successful request rebuilds the wiki while holding the shared write lock.

| Field | Value |
| --- | --- |
| `new_article` | `true` (explicit creation; currently supported for DevOps) |
| `name` | Descriptive single-line article title |
| `space` | `devops` |
| `section` | One of `overview`, `infrastructure`, `networking`, `containers`, `delivery`, `observability`, `runbooks`, `security`, `decisions` |
| `steward` | `transpara` |
| `article_markdown` | Authored Markdown prose, including a heading, **without YAML frontmatter** |
| `source_authority` | A value from `/api/spaces`; defaults to `engineering-docs` |
| `documents` | One or more uploaded original source files; repeat this multipart field |
| `external_urls` | Optional newline-separated HTTP(S) source URLs |
| `note` | Optional provenance context: original repository/path, revision, document date, import batch |

At least one nonempty source document or external URL is required. Uploaded
files retain their bytes under `raw/inbox/devops/`; URL references are registered
without fetching their contents. Provide source files when a durable snapshot
is required. Metadata, prose, filenames, and source bytes pass the existing
secret quarantine before any content is saved.

The server creates `wiki/<slug>.md`, fixes classification to `internal`, and
generates placement metadata. Slugs derive from the title by lowercasing,
dropping parenthesized text, and replacing non-ASCII-alphanumeric runs with
hyphens (maximum 80 characters before the prefix). A `devops-` prefix is added
if absent. Use the returned `created_article.slug` as the canonical identity.
Names, slugs, and aliases that collide with existing or retired articles are
refused. Creation never overwrites an article.

The supplied prose is saved and rendered immediately; the server does **not**
read or synthesize the sources for you. Review and synthesize all submitted
evidence before calling the API. New articles are labeled `API-authored draft`.
Use `[[other-article-slug]]` for internal links, and ordinary Markdown links for
external citations. Raw HTML renders as text; Markdown code blocks, tables,
and blockquotes remain supported. The generated article source list links all submitted
documents and URLs.

Example using local Markdown and source files (add the authorization header
when configured):

```bash
curl --fail-with-body --max-time 300 \
  --form-string 'new_article=true' \
  --form-string 'name=Container hosting' \
  --form-string 'space=devops' \
  --form-string 'section=containers' \
  --form-string 'steward=transpara' \
  --form-string 'source_authority=engineering-docs' \
  --form 'article_markdown=<article.md' \
  --form 'documents=@source.md' \
  --form-string 'note=Source: repository/docs/hosting.md at revision <commit>' \
  http://127.0.0.1:8787/api/ingest
```

Success returns HTTP 200, `created_article: {slug, created: true}`,
`article_content_written: true`, `article_href`, `saved` (paths and SHA-256
digests), `source_hrefs`, and `refresh.ok: true`. Fetch `article_href` to verify
the substantive prose, then check the space home and sources page.

## Add evidence to an existing article

Use the same endpoint with `target_slug`, its existing `space`, `section`, and
`steward`, and `documents` and/or `external_urls`. Omit `new_article`,
`new_investigation`, and `article_markdown`.

This appends source references and preserves existing prose and sources. New
evidence marks the article as awaiting a prose update. This API does not expose
general prose replacement; prepare a repository edit for a later synthesis
pass if an existing article needs revision. A repeated identical upload does
not duplicate its source reference. Manifests and the operation ledger record
each successful request, including retries.

Creation flags are mutually exclusive. The existing `new_investigation` lane
remains specific to Civilization investigations. `article_markdown` sent
without `new_article` is refused rather than silently ignored.

## Retry and completion rules

Validation refusals return 422 (or 400 for malformed input); authentication
failures return 401/403. These requests save no source or article content.
A rebuild failure returns 500 with `refresh.ok: false`, but article/source
writes may already have succeeded. After any timeout or 500, inspect
`GET /api/articles` and the returned saved paths before retrying creation.
Use `POST /api/rebuild` to retry rendering without resubmitting content.

Keep an import manifest with source identities, checksums, article slugs, and
results. Resume by reconciling it with `/api/articles`. At completion, verify
the DevOps home, source links, and representative rendered prose, and report
imported/skipped/failed items and any remaining synthesis work.
