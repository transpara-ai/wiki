"""Read the configured terminology export without granting dictionary authority.

The only input path comes from host configuration. No request can choose a path,
write a decision, or publish a term. The byte limit bounds parsing and browser
rendering costs; the dictionary digest identifies the source revision, not a
signature or proof of Human approval.
"""
import json
import os
import pathlib
import re
import stat

SNAPSHOT_ENV = "TRANSPARA_TERMINOLOGY_SNAPSHOT"
MAX_BYTES = 2 * 1024 * 1024


class SnapshotUnavailable(ValueError):
    """A configured export cannot safely be presented."""


def load_snapshot():
    """Load one bounded regular file and validate fields consumed by the UI."""
    configured = os.environ.get(SNAPSHOT_ENV)
    if not configured:
        raise SnapshotUnavailable("No terminology snapshot is configured.")
    path = pathlib.Path(configured)
    if not path.is_absolute():
        raise SnapshotUnavailable("The terminology snapshot needs an absolute configured path.")
    try:
        # A mistaken FIFO/device configuration must not stall a request thread.
        descriptor = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
        with os.fdopen(descriptor, "rb") as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise SnapshotUnavailable("The terminology snapshot is not a regular file.")
            raw = stream.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise SnapshotUnavailable("The terminology snapshot exceeds the 2 MiB limit.")
        data = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        # Do not expose a private host path or source bytes in an HTTP error.
        raise SnapshotUnavailable("The terminology snapshot cannot be read.") from exc
    if not isinstance(data, dict) or type(data.get("schema_version")) is not int or data["schema_version"] != 1:
        raise SnapshotUnavailable("Unsupported terminology snapshot schema.")
    if not isinstance(data.get("dictionary_version"), str) or not data["dictionary_version"]:
        raise SnapshotUnavailable("The snapshot has no dictionary version.")
    if not isinstance(data.get("dictionary_digest"), str) or not re.fullmatch(r"[a-f0-9]{64}", data["dictionary_digest"]):
        raise SnapshotUnavailable("The snapshot has no valid dictionary digest.")
    if data.get("reference_status") not in ("available", "unassessed"):
        raise SnapshotUnavailable("The snapshot has no reference assessment status.")
    for key in ("terms", "decisions", "candidates"):
        rows = data.get(key)
        if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
            raise SnapshotUnavailable("The snapshot has an invalid " + key + " collection.")
    ids = set()
    for row in data["candidates"]:
        if (not isinstance(row.get("id"), str) or not row["id"] or row["id"] in ids
                or not isinstance(row.get("term"), str) or not row["term"]
                or not isinstance(row.get("normalized"), str)
                or row.get("status") != "pending"
                or row.get("reference_status") not in ("available", "unassessed")
                or not isinstance(row.get("scope"), dict)
                or not all(isinstance(row["scope"].get(k), str) for k in ("repo", "product"))
                or not isinstance(row.get("observations"), list)):
            raise SnapshotUnavailable("The snapshot contains an invalid candidate.")
        ids.add(row["id"])
        for item in row["observations"]:
            if (not isinstance(item, dict) or not isinstance(item.get("path"), str)
                    or type(item.get("line")) is not int or item["line"] < 1
                    or not isinstance(item.get("sentence"), str)):
                raise SnapshotUnavailable("The snapshot contains invalid candidate evidence.")
            if ("context_digest" in item
                    and (not isinstance(item["context_digest"], str)
                         or not re.fullmatch(r"[a-f0-9]{64}", item["context_digest"]))):
                raise SnapshotUnavailable("The snapshot contains an invalid context digest.")
    # This adapter never upgrades an export into an ASD conformance verdict.
    data["conformance"] = "not_assessed"
    return data
