# Manifest shards

`raw/inbox/manifest.jsonl` is **frozen** as the historical segment of the
ingest manifest and never grows again. Every new manifest row (browser Add
and session-author `register` alike) is written here as ONE immutable
single-row `.jsonl` shard, created exactly once (`O_CREAT|O_EXCL`, never
overwritten, never appended).

Why: secret-scan allowlist clearances pin `(blob_sha256, match_sha256,
byte_offset)`. A growing manifest file changes its blob on every append,
which strands every clearance pinned to the previous blob (transpara-ai/wiki
issue #50). Per-row files make every manifest blob immutable from birth, so
no clearance ever goes stale and neither a PR nor a runtime append can
poison a later commit.

The complete audit surface is the frozen file plus the shards:

    cat raw/inbox/manifest.jsonl raw/inbox/manifest.d/*.jsonl

Audit rule: the ops ledger row (`compile/ingest-ledger.jsonl`) is written
LAST in every operation — a shard here **without** a matching ledger row is
the detectable signature of an operation that did not complete. The ledger
never claims an operation that did not finish.

This file is documentation only; the shard reader globs `*.jsonl` and never
parses it.
