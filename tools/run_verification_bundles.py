"""Execute fixed Wiki documentation checks from two focused plans.

After adoption, the workflow extracts this dispatcher from the base commit and
passes the exact-head checkout explicitly with ``--repo-root``. The policy can
select only bundle identifiers. This dispatcher owns every command behind
those identifiers and refuses unknown, missing, reordered, or unconfirmed
selections. A full plan is never dispatched here; the workflow runs the
complete existing Build & Test command sequence instead.

The required workflow separately executes the trusted-base changed-range
credential scan before dependency installation. This dispatcher adds the
distinct whole-tree scan, plan/registry contracts, and the structural contract
for non-runtime design and operating documentation. Published Wiki articles,
spaces, raw inputs, Python services, JavaScript assets, deployment inputs,
release controls, and unknown paths select full instead.
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import shlex
import subprocess
import sys
import tempfile
import time
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ENGINE_SOURCE = "transpara-ai/dev-ops"
ENGINE_COMMIT = "b02303a9a9250d7b2404806afa3e2ff7aa241c08"
ENGINE_FILES = (
    "verification/policy.schema.json",
    "verification/select_verify.py",
)
MANDATORY_BUNDLES = ("mandatory-baseline",)
PLAN_BINDINGS = (
    "schema_version",
    "repository",
    "event",
    "engine_source",
    "engine_commit",
    "engine_files",
    "base",
    "head",
    "merge_base",
    "policy_path",
    "policy_blob",
    "diff_digest",
    "mode",
    "route",
    "selected_bundles",
    "reason",
    "plan_digest",
)


class PlanError(ValueError):
    """Report a plan that cannot authorize focused command execution."""


@dataclass(frozen=True)
class Command:
    """One reviewable command vector and its fixed working directory."""

    label: str
    argv: tuple[str, ...]
    cwd: Path


def repository_root(path: Path) -> Path:
    """Return an exact, non-symlink worktree root supplied by the workflow."""
    if path.is_symlink():
        raise PlanError("repository root must not be a symlink")
    try:
        requested = path.resolve(strict=True)
    except OSError as exc:
        raise PlanError("cannot resolve repository root") from exc
    result = subprocess.run(
        ["git", "-C", os.fspath(requested), "rev-parse", "--show-toplevel"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise PlanError("cannot find repository root")
    try:
        discovered = Path(result.stdout.strip()).resolve(strict=True)
    except OSError as exc:
        raise PlanError("cannot resolve Git repository root") from exc
    if discovered != requested:
        raise PlanError("--repo-root must name the exact worktree root")
    return discovered


def unittest_command(root: Path, label: str, pattern: str) -> Command:
    """Return one fixed unittest-discovery command at the repository root."""
    return Command(
        label,
        (
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            "tests",
            "-p",
            pattern,
            "-v",
        ),
        root,
    )


def bundle_commands(root: Path) -> dict[str, tuple[Command, ...]]:
    """Return the complete literal identifier-to-command registry."""
    return {
        "mandatory-baseline": (
            Command(
                "whole-tree credential scan",
                (
                    sys.executable,
                    "compile/secret_scan.py",
                    "--tree",
                    "HEAD",
                    "--max-seconds",
                    "300",
                ),
                root,
            ),
            unittest_command(
                root,
                "proportional verification contracts",
                "test_verification_adapter.py",
            ),
        ),
        "repository-contracts": (
            Command(
                "validate focused documentation",
                (sys.executable, "tools/check_repository_contracts.py"),
                root,
            ),
            unittest_command(
                root,
                "documentation repository contracts",
                "test_repository_contracts.py",
            ),
        ),
    }


def canonical_digest(value: dict[str, Any]) -> str:
    """Return the selector-compatible SHA-256 plan digest."""
    unsigned = {key: item for key, item in value.items() if key != "plan_digest"}
    encoded = json.dumps(
        unsigned,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def load_plan(path: Path) -> dict[str, Any]:
    """Load one attestation and validate its complete binding and digest."""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PlanError(f"cannot read plan {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise PlanError(f"plan {path} must contain an object")
    missing = [key for key in PLAN_BINDINGS if key not in value]
    if missing:
        raise PlanError(f"plan {path} is missing: {', '.join(missing)}")
    digest = value.get("plan_digest")
    if not isinstance(digest, str) or not hmac.compare_digest(
        digest, canonical_digest(value)
    ):
        raise PlanError(f"plan {path} has an invalid plan_digest")
    return value


def confirmed_bundles(
    initial: dict[str, Any],
    confirmation: dict[str, Any],
    registry: dict[str, tuple[Command, ...]],
) -> tuple[str, ...]:
    """Return confirmed fixed IDs or reject any classification drift."""
    differences = [
        key for key in PLAN_BINDINGS if initial.get(key) != confirmation.get(key)
    ]
    if differences:
        raise PlanError(f"plan confirmation mismatch: {', '.join(differences)}")
    if initial.get("mode") != "focused" or initial.get("route") != "focused":
        raise PlanError("bundle execution requires a focused plan; run full verification")
    selected = initial.get("selected_bundles")
    if (
        not isinstance(selected, list)
        or not selected
        or any(not isinstance(item, str) for item in selected)
    ):
        raise PlanError("selected_bundles must be a non-empty string list")
    if selected != sorted(set(selected)):
        raise PlanError("selected_bundles must be sorted and unique")
    unknown = sorted(set(selected).difference(registry))
    if unknown:
        raise PlanError(f"plan selected unknown bundles: {', '.join(unknown)}")
    missing = sorted(set(MANDATORY_BUNDLES).difference(selected))
    if missing:
        raise PlanError(f"plan omitted mandatory bundles: {', '.join(missing)}")
    return tuple(selected)


def full_sha256(value: object) -> bool:
    """Return whether value is exactly one lowercase hexadecimal SHA-256."""
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def verify_engine_identity(plan: dict[str, Any], engine_root: Path) -> None:
    """Bind the plan to the trusted base-extracted engine bytes."""
    if (
        plan.get("engine_source") != ENGINE_SOURCE
        or plan.get("engine_commit") != ENGINE_COMMIT
    ):
        raise PlanError("plan has the wrong immutable engine identity")
    if engine_root.is_symlink() or not engine_root.is_dir():
        raise PlanError("trusted engine root must be a regular directory")
    entries = plan.get("engine_files")
    if not isinstance(entries, list):
        raise PlanError("engine_files must be a list")
    paths = [entry.get("path") for entry in entries if isinstance(entry, dict)]
    if paths != list(ENGINE_FILES):
        raise PlanError("engine_files must list the two fixed vendored paths in order")
    for entry in entries:
        assert isinstance(entry, dict)
        relative = entry["path"]
        supplied = entry.get("sha256")
        path = engine_root / relative
        if not full_sha256(supplied):
            raise PlanError(f"invalid engine SHA-256 for {relative}")
        if path.is_symlink() or not path.is_file():
            raise PlanError(f"trusted engine file is not regular: {relative}")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        assert isinstance(supplied, str)
        if not hmac.compare_digest(actual, supplied):
            raise PlanError(f"trusted engine hash mismatch: {relative}")


def git(root: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    """Run Git against the exact-head checkout without a shell."""
    return subprocess.run(
        ["git", "-C", os.fspath(root), *args],
        check=False,
        capture_output=True,
    )


def resolve_local_commit(root: Path, revision: str) -> str:
    """Resolve a local commit name to its complete object ID."""
    result = git(
        root,
        "rev-parse",
        "--verify",
        "--end-of-options",
        f"{revision}^{{commit}}",
    )
    if result.returncode != 0:
        raise PlanError(f"cannot resolve local commit {revision!r}")
    try:
        return result.stdout.decode("ascii", errors="strict").strip()
    except UnicodeDecodeError as exc:
        raise PlanError("Git returned a non-ASCII object ID") from exc


def resolve_attested_commit(root: Path, revision: object) -> str:
    """Require an attested revision to be a complete exact commit ID."""
    if not isinstance(revision, str) or not revision or revision.startswith("-"):
        raise PlanError("plan contains an invalid commit")
    resolved = resolve_local_commit(root, revision)
    if resolved != revision:
        raise PlanError(
            f"attested commit must be a complete exact object ID: {revision!r}"
        )
    return resolved


def changed_paths(root: Path, merge_base: str, head: str) -> list[str]:
    """Read the complete no-rename path set for execution evidence."""
    result = git(
        root,
        "diff",
        "--name-only",
        "--no-renames",
        "-z",
        merge_base,
        head,
        "--",
    )
    if result.returncode != 0:
        raise PlanError("cannot read changed paths")
    try:
        paths = [
            part.decode("utf-8", errors="strict")
            for part in result.stdout.split(b"\0")
            if part
        ]
    except UnicodeDecodeError as exc:
        raise PlanError("changed path is not UTF-8") from exc
    if not paths:
        raise PlanError("focused execution requires a non-empty diff")
    for path in paths:
        candidate = Path(path)
        if candidate.is_absolute() or ".." in candidate.parts or not candidate.parts:
            raise PlanError(f"unsafe changed path: {path!r}")
    return paths


def run_command(root: Path, command: Command, dry_run: bool) -> float:
    """Run one fixed command and return its measured wall time."""
    rendered = shlex.join(command.argv)
    relative = command.cwd.relative_to(root)
    print(f"==> {command.label}: {rendered} (cwd {relative or '.'})", flush=True)
    if dry_run:
        return 0.0
    started = time.monotonic()
    result = subprocess.run(command.argv, cwd=command.cwd, check=False)
    duration = time.monotonic() - started
    print(
        f"<== {command.label}: exit {result.returncode} in {duration:.3f}s",
        flush=True,
    )
    if result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, command.argv)
    return duration


def execute(
    initial: dict[str, Any],
    confirmation: dict[str, Any],
    engine_root: Path,
    repo_root: Path,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Run a confirmed focused plan and return non-secret timing evidence."""
    root = repository_root(repo_root)
    registry = bundle_commands(root)
    bundles = confirmed_bundles(initial, confirmation, registry)
    verify_engine_identity(initial, engine_root)
    resolve_attested_commit(root, initial["base"])
    head = resolve_attested_commit(root, initial["head"])
    if resolve_local_commit(root, "HEAD") != head:
        raise PlanError("checked-out HEAD does not match the attested head")
    merge_base = resolve_attested_commit(root, initial["merge_base"])
    paths = changed_paths(root, merge_base, head)

    commands: list[Command] = [
        Command(
            "diff hygiene",
            ("git", "diff", "--check", merge_base, head, "--"),
            root,
        ),
    ]
    for bundle in bundles:
        commands.extend(registry[bundle])
    measurements = [
        (command.label, run_command(root, command, dry_run)) for command in commands
    ]
    return {
        "schema_version": 1,
        "repository": initial["repository"],
        "head": head,
        "engine_commit": initial["engine_commit"],
        "policy_blob": initial["policy_blob"],
        "diff_digest": initial["diff_digest"],
        "plan_digest": initial["plan_digest"],
        "selected_bundles": list(bundles),
        "changed_paths": paths,
        "dry_run": dry_run,
        "measured_command_seconds": round(
            sum(duration for _, duration in measurements), 3
        ),
        "step_count": len(measurements),
        "steps": [
            {"name": name, "duration_seconds": round(duration, 3)}
            for name, duration in measurements
        ],
    }


def atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    """Replace one execution record after its complete local write."""
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    with tempfile.NamedTemporaryFile(
        dir=path.parent,
        prefix=f".{path.name}.",
        delete=False,
    ) as handle:
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
    parser.add_argument(
        "--repo-root",
        type=Path,
        required=True,
        help="exact-head worktree root",
    )
    parser.add_argument(
        "--plan",
        type=Path,
        required=True,
        help="initial selector attestation",
    )
    parser.add_argument(
        "--confirmation",
        type=Path,
        required=True,
        help="fresh selector attestation",
    )
    parser.add_argument(
        "--engine-root",
        type=Path,
        required=True,
        help="trusted base engine directory",
    )
    parser.add_argument(
        "--timings",
        type=Path,
        required=True,
        help="execution record output",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print commands without running them",
    )
    args = parser.parse_args(argv)
    try:
        result = execute(
            load_plan(args.plan),
            load_plan(args.confirmation),
            args.engine_root,
            args.repo_root,
            args.dry_run,
        )
        atomic_write_json(args.timings, result)
        return 0
    except (OSError, PlanError, subprocess.CalledProcessError) as exc:
        print(f"verification bundle execution refused: {exc}", file=sys.stderr)
        if isinstance(exc, subprocess.CalledProcessError):
            return exc.returncode
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
