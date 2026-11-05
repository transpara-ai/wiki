"""Run the base-controlled proportional-verification selector safely.

After adoption, the workflow extracts this repository-owned adapter from the
base commit and points it at the exact-head checkout. The adapter reads only
three fixed regular blobs from the base commit, proves the vendored engine
provenance, and executes that trusted base selector in Python isolated mode.
Candidate working-directory and environment paths therefore cannot supply its
imports. Missing, malformed, or crashing trusted material produces a full-route
attestation. It never turns a selector failure into a focused pass. The
bootstrap does not execute candidate adapter code because its base has no
trusted adapter; it runs full verification.

The adapter writes only below the caller-supplied temporary directory and to
the requested attestation file. It does not run the Civilization collector or
write deployment, status, inventory, or evidence records.
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import re
import subprocess
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ENGINE_SOURCE = "transpara-ai/dev-ops"
ENGINE_COMMIT = "b02303a9a9250d7b2404806afa3e2ff7aa241c08"
ENGINE_PATHS = (
    "verification/policy.schema.json",
    "verification/select_verify.py",
)
MANIFEST_PATH = ".transpara/verification-engine.json"
POLICY_PATH = ".transpara/verification.json"
TRUSTED_PATHS = (MANIFEST_PATH, *ENGINE_PATHS)
HEX_OBJECT = re.compile(r"^[0-9a-f]+$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")


class AdapterError(RuntimeError):
    """Report an adapter input or trusted-base failure without selecting focus."""


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    """Run Git directly so the shell cannot interpret revisions or paths."""
    return subprocess.run(
        ["git", "-C", os.fspath(repo), *args],
        check=False,
        capture_output=True,
    )


def git_output(repo: Path, *args: str, description: str) -> bytes:
    """Return bounded Git output or raise a non-secret adapter error."""
    result = git(repo, *args)
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        suffix = f": {detail[:300]}" if detail else ""
        raise AdapterError(f"cannot {description}{suffix}")
    return result.stdout


def repository_root(path: Path) -> Path:
    """Return an exact, non-symlink worktree root."""
    if path.is_symlink():
        raise AdapterError("repository root must not be a symlink")
    try:
        requested = path.resolve(strict=True)
        discovered = Path(
            git_output(
                requested,
                "rev-parse",
                "--show-toplevel",
                description="find repository root",
            )
            .decode("utf-8", errors="strict")
            .strip()
        ).resolve(strict=True)
    except (OSError, UnicodeDecodeError) as exc:
        raise AdapterError("cannot resolve repository root") from exc
    if discovered != requested:
        raise AdapterError("repository path must name the worktree root")
    return discovered


def resolve_exact_commit(repo: Path, revision: str, description: str) -> str:
    """Require a complete exact object ID without assuming SHA-1 length."""
    if not revision or not HEX_OBJECT.fullmatch(revision):
        raise AdapterError(f"{description} must be a complete lowercase object ID")
    raw = git_output(
        repo,
        "rev-parse",
        "--verify",
        "--end-of-options",
        f"{revision}^{{commit}}",
        description=f"resolve {description}",
    )
    try:
        resolved = raw.decode("ascii", errors="strict").strip()
    except UnicodeDecodeError as exc:
        raise AdapterError(f"resolved {description} is not ASCII") from exc
    if resolved != revision:
        raise AdapterError(f"{description} must be a complete exact object ID")
    return resolved


def read_regular_blob(repo: Path, commit: str, relative: str) -> tuple[str, bytes]:
    """Read one fixed path only when the base tree records mode 100644."""
    candidate = PurePosixPath(relative)
    if candidate.is_absolute() or ".." in candidate.parts or candidate.as_posix() != relative:
        raise AdapterError(f"unsafe trusted path: {relative!r}")
    tree = git_output(
        repo,
        "ls-tree",
        "-z",
        commit,
        "--",
        relative,
        description=f"inspect trusted base path {relative}",
    )
    entries = [entry for entry in tree.split(b"\0") if entry]
    if len(entries) != 1 or b"\t" not in entries[0]:
        raise AdapterError(f"trusted base path is missing or ambiguous: {relative}")
    metadata, raw_path = entries[0].split(b"\t", 1)
    fields = metadata.split()
    if len(fields) != 3 or fields[:2] != [b"100644", b"blob"]:
        raise AdapterError(f"trusted base path must be a regular non-executable blob: {relative}")
    try:
        found = raw_path.decode("utf-8", errors="strict")
        blob_id = fields[2].decode("ascii", errors="strict")
    except UnicodeDecodeError as exc:
        raise AdapterError(f"trusted tree entry is not decodable: {relative}") from exc
    if found != relative or not HEX_OBJECT.fullmatch(blob_id):
        raise AdapterError(f"trusted tree entry is invalid: {relative}")
    content = git_output(
        repo,
        "cat-file",
        "blob",
        blob_id,
        description=f"read trusted base path {relative}",
    )
    return blob_id, content


def strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Reject duplicate JSON keys in provenance and attestations."""
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise AdapterError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def parse_manifest(content: bytes) -> dict[str, Any]:
    """Validate the complete generated provenance manifest shape."""
    try:
        value = json.loads(
            content.decode("utf-8", errors="strict"),
            object_pairs_hook=strict_object,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AdapterError("trusted engine manifest is not strict UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise AdapterError("trusted engine manifest must be an object")
    expected = {
        "schema_version",
        "source_repository",
        "source_commit",
        "source_object_format",
        "files",
    }
    if set(value) != expected or value.get("schema_version") != 1:
        raise AdapterError("trusted engine manifest has an unsupported shape")
    if value.get("source_repository") != ENGINE_SOURCE:
        raise AdapterError("trusted engine manifest names the wrong repository")
    if value.get("source_commit") != ENGINE_COMMIT:
        raise AdapterError("trusted engine manifest names the wrong commit")
    if value.get("source_object_format") not in {"sha1", "sha256"}:
        raise AdapterError("trusted engine manifest names an unsupported object format")
    files = value.get("files")
    if not isinstance(files, list) or len(files) != len(ENGINE_PATHS):
        raise AdapterError("trusted engine manifest must describe exactly two files")
    return value


def verify_provenance(manifest: dict[str, Any], files: dict[str, bytes]) -> None:
    """Bind each fixed engine path to its generated SHA-256 provenance."""
    entries = manifest["files"]
    assert isinstance(entries, list)
    destinations: list[str] = []
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {
            "destination",
            "git_blob",
            "sha256",
            "source",
        }:
            raise AdapterError("trusted engine manifest file entry has an unsupported shape")
        destination = entry.get("destination")
        if destination not in ENGINE_PATHS or entry.get("source") != destination:
            raise AdapterError("trusted engine manifest names an unexpected path")
        git_blob = entry.get("git_blob")
        digest = entry.get("sha256")
        if not isinstance(git_blob, str) or not HEX_OBJECT.fullmatch(git_blob):
            raise AdapterError(f"trusted engine manifest has an invalid Git blob: {destination}")
        if not isinstance(digest, str) or not SHA256.fullmatch(digest):
            raise AdapterError(f"trusted engine manifest has an invalid SHA-256: {destination}")
        actual = hashlib.sha256(files[destination]).hexdigest()
        if not hmac.compare_digest(actual, digest):
            raise AdapterError(f"trusted engine hash mismatch: {destination}")
        destinations.append(destination)
    if tuple(destinations) != ENGINE_PATHS:
        raise AdapterError("trusted engine manifest file order is invalid")


def prepare_trusted_engine(repo: Path, base: str, target: Path) -> Path:
    """Extract and prove the fixed engine blobs from the exact base commit."""
    blobs = {path: read_regular_blob(repo, base, path)[1] for path in TRUSTED_PATHS}
    manifest = parse_manifest(blobs[MANIFEST_PATH])
    engine_files = {path: blobs[path] for path in ENGINE_PATHS}
    verify_provenance(manifest, engine_files)

    if target.is_symlink():
        raise AdapterError("trusted engine directory must not be a symlink")
    target.mkdir(parents=True, exist_ok=True)
    if any(target.iterdir()):
        raise AdapterError("trusted engine directory must be empty")
    for relative in ENGINE_PATHS:
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(engine_files[relative])
        destination.chmod(0o644)
    return target


def canonical_digest(value: dict[str, Any]) -> str:
    """Return the selector-compatible digest of every field except itself."""
    unsigned = {key: item for key, item in value.items() if key != "plan_digest"}
    encoded = json.dumps(
        unsigned,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def full_fallback(
    repository: str,
    event: str,
    base: str,
    head: str,
    reason: str,
) -> dict[str, Any]:
    """Return a deterministic attestation that can authorize only full verify."""
    plan: dict[str, Any] = {
        "base": base,
        "changes": [],
        "checked_out_head": None,
        "diff_digest": None,
        "engine_commit": ENGINE_COMMIT,
        "engine_files": None,
        "engine_source": ENGINE_SOURCE,
        "event": event,
        "head": head,
        "merge_base": None,
        "mode": None,
        "policy_blob": None,
        "policy_path": POLICY_PATH,
        "reason": reason,
        "repository": repository,
        "route": "full",
        "schema_version": 1,
        "selected_bundles": [],
    }
    plan["plan_digest"] = canonical_digest(plan)
    return plan


def validate_selector_plan(plan: Any, repository: str) -> dict[str, Any]:
    """Accept a selector result only when its identity and digest are exact."""
    if not isinstance(plan, dict):
        raise AdapterError("trusted selector did not return an object")
    digest = plan.get("plan_digest")
    if not isinstance(digest, str) or not SHA256.fullmatch(digest):
        raise AdapterError("trusted selector returned an invalid plan digest")
    if not hmac.compare_digest(digest, canonical_digest(plan)):
        raise AdapterError("trusted selector returned a mismatched plan digest")
    if plan.get("repository") != repository:
        raise AdapterError("trusted selector returned the wrong repository")
    if plan.get("engine_source") != ENGINE_SOURCE or plan.get("engine_commit") != ENGINE_COMMIT:
        raise AdapterError("trusted selector returned the wrong engine identity")
    if plan.get("route") not in {"focused", "full"} or not isinstance(plan.get("reason"), str):
        raise AdapterError("trusted selector returned an invalid route")
    return plan


def enforce_policy_mode(
    plan: dict[str, Any],
    repository: str,
    event: str,
    base: str,
    head: str,
) -> dict[str, Any]:
    """Permit focused execution only when the trusted policy enables it.

    The shared selector reports which bundles a shadow policy would select.
    This repository has no report-only dispatcher path, so executing that focused
    plan would fail after classification. Keep the shared engine bytes and
    digest contract unchanged, and make the repository wrapper choose the full
    required route with an explicit reason instead.
    """
    if plan["route"] != "focused" or plan.get("mode") == "focused":
        return plan
    reason = (
        "policy_shadow_full"
        if plan.get("mode") == "shadow"
        else "policy_mode_requires_full"
    )
    return full_fallback(repository, event, base, head, reason)


def build_plan(
    repo: Path,
    event: str,
    base_revision: str,
    head_revision: str,
    repository: str,
    trusted_root: Path,
) -> dict[str, Any]:
    """Build one trusted plan, falling back to full for any selector failure."""
    try:
        root = repository_root(repo)
        base = resolve_exact_commit(root, base_revision, "event base")
        head = resolve_exact_commit(root, head_revision, "event head")
        prepare_trusted_engine(root, base, trusted_root)
    except AdapterError:
        return full_fallback(repository, event, base_revision, head_revision, "trusted_base_unavailable")

    selector = trusted_root / "verification" / "select_verify.py"
    command = (
        sys.executable,
        "-I",
        os.fspath(selector),
        "--repo",
        os.fspath(root),
        "--event",
        event,
        "--base",
        base,
        "--head",
        head,
        "--repository",
        repository,
        "--engine-source",
        ENGINE_SOURCE,
        "--engine-commit",
        ENGINE_COMMIT,
    )
    result = subprocess.run(command, check=False, capture_output=True)
    if result.returncode != 0:
        return full_fallback(repository, event, base, head, "selector_failed")
    try:
        plan = json.loads(
            result.stdout.decode("ascii", errors="strict"),
            object_pairs_hook=strict_object,
        )
        validated = validate_selector_plan(plan, repository)
        return enforce_policy_mode(validated, repository, event, base, head)
    except (UnicodeDecodeError, json.JSONDecodeError, AdapterError):
        return full_fallback(repository, event, base, head, "selector_invalid_output")


def atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    """Replace one evidence file atomically after a complete local write."""
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(encoded)
        handle.flush()
        os.fsync(handle.fileno())
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", type=Path, default=ROOT, help="exact-head worktree root")
    parser.add_argument("--event", required=True, choices=("pull_request", "push"))
    parser.add_argument("--base", required=True, help="complete actual base or before commit")
    parser.add_argument("--head", required=True, help="complete actual head or after commit")
    parser.add_argument("--repository", required=True, help="owner/name for the attestation")
    parser.add_argument("--trusted-root", type=Path, required=True, help="empty temporary engine directory")
    parser.add_argument("--output", type=Path, required=True, help="attestation output path")
    args = parser.parse_args(argv)
    try:
        plan = build_plan(
            args.repo,
            args.event,
            args.base,
            args.head,
            args.repository,
            args.trusted_root,
        )
        atomic_write_json(args.output, plan)
        print(json.dumps({"reason": plan["reason"], "route": plan["route"]}, sort_keys=True))
        return 0
    except (AdapterError, OSError) as exc:
        print(f"verification adapter refused: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
