"""Select fixed verification bundles from a base-controlled Git policy.

The selector treats incomplete or ambiguous evidence as a request for full
verification. It never executes a command from the policy. A repository-owned
dispatcher is responsible for mapping the selected bundle identifiers to fixed
commands after it recomputes and compares the plan digest.

Classification is linear in the policy rules and changed paths. Git supplies
the commit graph, tree entries, and object types; the selector does not infer
object identity from a hash length or from a working-tree file.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

POLICY_SCHEMA_VERSION = 1
ATTESTATION_SCHEMA_VERSION = 1
DEFAULT_POLICY_PATH = ".transpara/verification.json"
MAX_POLICY_BYTES = 1024 * 1024
BUNDLE_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
HEX_OBJECT = re.compile(r"^[0-9a-f]+$")
ENGINE_COMMIT = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
ENGINE_SOURCE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
KNOWN_MODES = frozenset({"100644", "100755", "120000", "160000"})
KNOWN_STATUSES = frozenset({"A", "D", "M", "T"})
DEFAULT_MODES = ("100644",)
DEFAULT_STATUSES = ("A", "D", "M")


class PolicyError(ValueError):
    """Report a policy that cannot safely select focused verification."""


class DiffError(ValueError):
    """Report a raw diff that cannot safely select focused verification."""


@dataclass(frozen=True)
class Rule:
    """One base-owned mapping from anchored path patterns to fixed bundles."""

    rule_id: str
    patterns: tuple[str, ...]
    matchers: tuple[re.Pattern[str], ...]
    bundles: tuple[str, ...]
    full: bool
    allowed_modes: tuple[str, ...]
    statuses: tuple[str, ...]


@dataclass(frozen=True)
class Policy:
    """The validated policy fields used by the selector."""

    mode: str
    bundles: tuple[str, ...]
    mandatory_bundles: tuple[str, ...]
    rules: tuple[Rule, ...]


@dataclass(frozen=True)
class TreeBlob:
    """A regular Git tree entry and its blob content."""

    mode: str
    object_id: str
    content: bytes


@dataclass(frozen=True)
class Change:
    """One no-rename raw-diff entry with full Git object identifiers."""

    old_mode: str
    new_mode: str
    old_object: str
    new_object: str
    status: str
    path: str

    def public(self) -> dict[str, str]:
        """Return the deterministic, non-secret attestation representation."""
        return {
            "new_mode": self.new_mode,
            "new_object": self.new_object,
            "old_mode": self.old_mode,
            "old_object": self.old_object,
            "path": self.path,
            "status": self.status,
        }


def git(repo: str, *args: str, input_data: bytes | None = None) -> subprocess.CompletedProcess[bytes]:
    """Run Git directly, without asking a shell to interpret revisions or paths."""
    return subprocess.run(
        ["git", "-C", repo, *args],
        input=input_data,
        check=False,
        capture_output=True,
    )


def _decode_single_object(output: bytes) -> str | None:
    """Decode one full object identifier returned by Git."""
    try:
        value = output.decode("ascii", errors="strict").strip()
    except UnicodeDecodeError:
        return None
    if not value or "\n" in value or not HEX_OBJECT.fullmatch(value):
        return None
    return value


def resolve_event_commit(repo: str, revision: str) -> str | None:
    """Resolve an event commit only when the input is its complete object ID.

    Git, rather than this function, decides the repository's object format.
    Requiring the resolved value to equal the event value rejects abbreviations,
    symbolic refs, and ambiguous user-controlled revision syntax.
    """
    if not revision or not HEX_OBJECT.fullmatch(revision.lower()):
        return None
    result = git(
        repo,
        "rev-parse",
        "--verify",
        "--end-of-options",
        f"{revision}^{{commit}}",
    )
    if result.returncode != 0:
        return None
    resolved = _decode_single_object(result.stdout)
    if resolved is None or resolved != revision.lower():
        return None
    return resolved


def resolve_head(repo: str) -> str | None:
    """Return the checkout's exact commit using Git's native object format."""
    result = git(repo, "rev-parse", "--verify", "HEAD^{commit}")
    if result.returncode != 0:
        return None
    return _decode_single_object(result.stdout)


def valid_policy_path(path: str) -> bool:
    """Accept one literal, normalized repository-relative policy path."""
    if not path or path.startswith("/") or "\\" in path or "\0" in path:
        return False
    if any(ord(character) < 32 or ord(character) == 127 for character in path):
        return False
    candidate = PurePosixPath(path)
    return (
        str(candidate) == path
        and candidate.parts
        and all(part not in {"", ".", ".."} for part in candidate.parts)
        and not any(character in path for character in "*?[")
    )


def valid_changed_path(path: str) -> bool:
    """Reject paths whose spelling can hide traversal or normalization changes."""
    if not path or path.startswith("/") or "\\" in path or "\0" in path:
        return False
    if any(ord(character) < 32 or ord(character) == 127 for character in path):
        return False
    candidate = PurePosixPath(path)
    return (
        str(candidate) == path
        and candidate.parts
        and all(part not in {"", ".", ".."} for part in candidate.parts)
    )


def compile_glob(pattern: str) -> re.Pattern[str]:
    """Compile a small anchored POSIX glob without filesystem access.

    ``*`` and ``?`` do not cross ``/``. ``**`` crosses directory boundaries;
    ``**/`` also matches zero directories. Character classes, escaping, and
    negation are deliberately unsupported so different hosts cannot interpret
    the same policy differently.
    """
    if not pattern or pattern.startswith("/") or pattern.endswith("/"):
        raise PolicyError("invalid pattern")
    if "\\" in pattern or "\0" in pattern or "[" in pattern or "]" in pattern:
        raise PolicyError("unsupported pattern syntax")
    if "***" in pattern or "//" in pattern:
        raise PolicyError("ambiguous pattern syntax")
    if any(ord(character) < 32 or ord(character) == 127 for character in pattern):
        raise PolicyError("control character in pattern")
    parts = pattern.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise PolicyError("non-normalized pattern")

    expression = "^"
    index = 0
    while index < len(pattern):
        character = pattern[index]
        if pattern.startswith("**/", index):
            expression += "(?:[^/]+/)*"
            index += 3
        elif pattern.startswith("**", index):
            expression += ".*"
            index += 2
        elif character == "*":
            expression += "[^/]*"
            index += 1
        elif character == "?":
            expression += "[^/]"
            index += 1
        else:
            expression += re.escape(character)
            index += 1
    return re.compile(expression + "$")


def _unique_strings(value: Any, field: str) -> tuple[str, ...]:
    """Validate a non-empty JSON array of distinct strings."""
    if not isinstance(value, list) or not value:
        raise PolicyError(f"{field} must be a non-empty array")
    if any(not isinstance(item, str) or not item for item in value):
        raise PolicyError(f"{field} must contain non-empty strings")
    if len(set(value)) != len(value):
        raise PolicyError(f"{field} must not contain duplicates")
    return tuple(value)


def _object_without_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Reject duplicate JSON keys instead of silently accepting the last one."""
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise PolicyError("duplicate JSON key")
        result[key] = value
    return result


def parse_policy(content: bytes) -> Policy:
    """Parse and validate policy version 1 without command-bearing fields."""
    if len(content) > MAX_POLICY_BYTES:
        raise PolicyError("policy is too large")
    try:
        text = content.decode("utf-8", errors="strict")
        data = json.loads(text, object_pairs_hook=_object_without_duplicate_keys)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise PolicyError("policy is not strict UTF-8 JSON") from error
    if not isinstance(data, dict):
        raise PolicyError("policy must be an object")
    expected = {
        "schema_version",
        "mode",
        "default",
        "bundles",
        "mandatory_bundles",
        "rules",
    }
    if set(data) != expected:
        raise PolicyError("policy has missing or unknown fields")
    if type(data["schema_version"]) is not int or data["schema_version"] != POLICY_SCHEMA_VERSION:
        raise PolicyError("unsupported policy schema")
    if data["mode"] not in {"shadow", "focused", "force-full"}:
        raise PolicyError("unsupported policy mode")
    if data["default"] != "full":
        raise PolicyError("the default route must be full")

    bundles = _unique_strings(data["bundles"], "bundles")
    if any(BUNDLE_ID.fullmatch(bundle) is None for bundle in bundles):
        raise PolicyError("invalid bundle identifier")
    mandatory = _unique_strings(data["mandatory_bundles"], "mandatory_bundles")
    if not set(mandatory).issubset(bundles):
        raise PolicyError("mandatory bundle is not registered")
    raw_rules = data["rules"]
    if not isinstance(raw_rules, list) or not raw_rules:
        raise PolicyError("rules must be a non-empty array")

    rules: list[Rule] = []
    rule_ids: set[str] = set()
    for raw_rule in raw_rules:
        if not isinstance(raw_rule, dict):
            raise PolicyError("rule must be an object")
        allowed_fields = {"id", "patterns", "bundles", "full", "allowed_modes", "statuses"}
        if not set(raw_rule).issubset(allowed_fields) or not {"id", "patterns"}.issubset(raw_rule):
            raise PolicyError("rule has missing or unknown fields")
        rule_id = raw_rule["id"]
        if not isinstance(rule_id, str) or BUNDLE_ID.fullmatch(rule_id) is None:
            raise PolicyError("invalid rule identifier")
        if rule_id in rule_ids:
            raise PolicyError("duplicate rule identifier")
        rule_ids.add(rule_id)

        patterns = _unique_strings(raw_rule["patterns"], "rule patterns")
        matchers = tuple(compile_glob(pattern) for pattern in patterns)
        if "full" in raw_rule and raw_rule["full"] is not True:
            raise PolicyError("full rule must contain true")
        is_full = raw_rule.get("full") is True
        has_bundles = "bundles" in raw_rule
        if is_full == has_bundles:
            raise PolicyError("rule must select bundles or full, but not both")
        selected: tuple[str, ...] = ()
        if has_bundles:
            selected = _unique_strings(raw_rule["bundles"], "rule bundles")
            if not set(selected).issubset(bundles):
                raise PolicyError("rule selects an unregistered bundle")
        elif raw_rule.get("full") is not True:
            raise PolicyError("full rule must contain true")

        modes = _unique_strings(raw_rule.get("allowed_modes", list(DEFAULT_MODES)), "allowed_modes")
        if not set(modes).issubset(KNOWN_MODES):
            raise PolicyError("unsupported Git mode")
        statuses = _unique_strings(raw_rule.get("statuses", list(DEFAULT_STATUSES)), "statuses")
        if not set(statuses).issubset(KNOWN_STATUSES):
            raise PolicyError("unsupported diff status")
        rules.append(
            Rule(
                rule_id=rule_id,
                patterns=patterns,
                matchers=matchers,
                bundles=selected,
                full=is_full,
                allowed_modes=tuple(sorted(modes)),
                statuses=tuple(sorted(statuses)),
            )
        )
    return Policy(
        mode=data["mode"],
        bundles=tuple(sorted(bundles)),
        mandatory_bundles=tuple(sorted(mandatory)),
        rules=tuple(rules),
    )


def read_tree_blob(repo: str, commit: str, path: str) -> TreeBlob | None:
    """Read one literal regular blob from a commit without using the checkout."""
    if not valid_policy_path(path):
        return None
    result = git(repo, "ls-tree", "-z", commit, "--", f":(literal){path}")
    if result.returncode != 0:
        return None
    entries = [entry for entry in result.stdout.split(b"\0") if entry]
    if len(entries) != 1 or b"\t" not in entries[0]:
        return None
    metadata, raw_path = entries[0].split(b"\t", 1)
    try:
        found_path = raw_path.decode("utf-8", errors="strict")
        mode, object_type, object_id = metadata.decode("ascii", errors="strict").split()
    except (UnicodeDecodeError, ValueError):
        return None
    if found_path != path or mode != "100644" or object_type != "blob":
        return None
    content = git(repo, "cat-file", "blob", object_id)
    if content.returncode != 0 or len(content.stdout) > MAX_POLICY_BYTES:
        return None
    return TreeBlob(mode=mode, object_id=object_id, content=content.stdout)


def merge_base_for_event(repo: str, event: str, base: str, head: str) -> str | None:
    """Prove one merge base and the stronger before/after relation for pushes."""
    result = git(repo, "merge-base", "--all", base, head)
    if result.returncode != 0:
        return None
    try:
        candidates = [line for line in result.stdout.decode("ascii", errors="strict").splitlines() if line]
    except UnicodeDecodeError:
        return None
    if len(candidates) != 1 or not HEX_OBJECT.fullmatch(candidates[0]):
        return None
    merge_base = candidates[0]
    if event == "push":
        ancestor = git(repo, "merge-base", "--is-ancestor", base, head)
        if ancestor.returncode != 0 or merge_base != base:
            return None
    return merge_base


def _zero_object(object_id: str) -> bool:
    return bool(object_id) and set(object_id) == {"0"}


def _object_types(repo: str, object_ids: set[str]) -> dict[str, str] | None:
    """Ask one Git process for all changed object types.

    The batch keeps classification cost proportional without starting one
    process for each changed path. Missing or reordered answers fail closed.
    """
    ordered = sorted(object_ids)
    if not ordered:
        return {}
    request = b"".join(object_id.encode("ascii") + b"\n" for object_id in ordered)
    result = git(repo, "cat-file", "--batch-check=%(objectname) %(objecttype)", input_data=request)
    if result.returncode != 0:
        return None
    try:
        lines = result.stdout.decode("ascii", errors="strict").splitlines()
    except UnicodeDecodeError:
        return None
    if len(lines) != len(ordered):
        return None
    found: dict[str, str] = {}
    for requested, line in zip(ordered, lines, strict=True):
        fields = line.split()
        if len(fields) != 2 or fields[0] != requested or fields[1] not in {"blob", "commit"}:
            return None
        found[requested] = fields[1]
    return found


def raw_changes(repo: str, start: str, head: str, object_length: int) -> tuple[list[Change], bytes]:
    """Return a complete no-rename raw diff and the exact bytes it binds."""
    result = git(
        repo,
        "diff",
        "--raw",
        "--no-renames",
        f"--abbrev={object_length}",
        "-z",
        start,
        head,
        "--",
    )
    if result.returncode != 0 or not result.stdout:
        raise DiffError("empty or unreadable diff")
    fields = result.stdout.split(b"\0")
    if fields[-1] != b"":
        raise DiffError("unterminated raw diff")
    fields.pop()
    if len(fields) % 2:
        raise DiffError("incomplete raw diff record")

    changes: list[Change] = []
    object_ids: set[str] = set()
    seen: set[tuple[str, str]] = set()
    for offset in range(0, len(fields), 2):
        header = fields[offset]
        raw_path = fields[offset + 1]
        try:
            header_fields = header.decode("ascii", errors="strict").split()
            path = raw_path.decode("utf-8", errors="strict")
        except UnicodeDecodeError as error:
            raise DiffError("undecodable raw diff") from error
        if len(header_fields) != 5 or not header_fields[0].startswith(":"):
            raise DiffError("invalid raw diff header")
        old_mode = header_fields[0][1:]
        new_mode, old_object, new_object, status = header_fields[1:]
        if len(old_object) != object_length or len(new_object) != object_length:
            raise DiffError("abbreviated object identifier")
        if not HEX_OBJECT.fullmatch(old_object) or not HEX_OBJECT.fullmatch(new_object):
            raise DiffError("invalid object identifier")
        if status not in KNOWN_STATUSES or not valid_changed_path(path):
            raise DiffError("unsupported status or path")
        if (status, path) in seen:
            raise DiffError("duplicate raw diff record")
        seen.add((status, path))

        old_zero = _zero_object(old_object)
        new_zero = _zero_object(new_object)
        shape_is_valid = (
            (status == "A" and old_mode == "000000" and old_zero and new_mode != "000000" and not new_zero)
            or (status == "D" and new_mode == "000000" and new_zero and old_mode != "000000" and not old_zero)
            or (status in {"M", "T"} and old_mode != "000000" and new_mode != "000000" and not old_zero and not new_zero)
        )
        if not shape_is_valid:
            raise DiffError("status and object shape disagree")
        for mode, object_id in ((old_mode, old_object), (new_mode, new_object)):
            if mode == "000000":
                continue
            if mode not in KNOWN_MODES:
                raise DiffError("unusual Git mode")
            object_ids.add(object_id)
        changes.append(Change(old_mode, new_mode, old_object, new_object, status, path))

    types = _object_types(repo, object_ids)
    if types is None:
        raise DiffError("changed object is missing")
    for change in changes:
        for mode, object_id in ((change.old_mode, change.old_object), (change.new_mode, change.new_object)):
            if mode == "000000":
                continue
            expected_type = "commit" if mode == "160000" else "blob"
            if types.get(object_id) != expected_type:
                raise DiffError("Git mode and object type disagree")
    return changes, result.stdout


def select_bundles(policy: Policy, changes: list[Change]) -> tuple[str, tuple[str, ...]]:
    """Return a reason and deterministic union, or all bundles on any miss."""
    selected = set(policy.mandatory_bundles)
    for change in changes:
        matched = [
            rule
            for rule in policy.rules
            if any(matcher.fullmatch(change.path) for matcher in rule.matchers)
        ]
        if not matched:
            return "unmatched_path", policy.bundles
        if any(rule.full for rule in matched):
            return "full_rule", policy.bundles
        modes = {mode for mode in (change.old_mode, change.new_mode) if mode != "000000"}
        # One sufficiently narrow rule can prove the complete status/mode
        # tuple. All matching rules still contribute their functional bundles.
        # This lets an exact script rule admit 100755 without admitting that
        # mode for every path covered by a broad source-domain rule.
        if not any(
            change.status in rule.statuses and modes.issubset(rule.allowed_modes)
            for rule in matched
        ):
            return "unproved_status_or_mode", policy.bundles
        for rule in matched:
            selected.update(rule.bundles)
    return "mapped", tuple(sorted(selected))


def engine_file_set() -> list[dict[str, str]] | None:
    """Hash the stable files that an adopter vendors from the source commit.

    The exact source commit identifies where the files came from. These hashes
    prove what the current process actually loaded, without requiring a
    cross-private-repository action or a live repository-setting change.
    """
    directory = Path(__file__).resolve().parent
    files = (directory / "policy.schema.json", directory / "select_verify.py")
    result: list[dict[str, str]] = []
    try:
        for path in files:
            content = path.read_bytes()
            result.append(
                {
                    "path": f"verification/{path.name}",
                    "sha256": hashlib.sha256(content).hexdigest(),
                }
            )
    except OSError:
        return None
    return result


def _base_attestation(
    repository: str,
    event: str,
    engine_source: str,
    engine_commit: str,
    policy_path: str,
) -> dict[str, Any]:
    """Create fields present even when Git evidence is incomplete."""
    return {
        "base": None,
        "changes": [],
        "checked_out_head": None,
        "diff_digest": None,
        "engine_commit": engine_commit,
        "engine_files": engine_file_set(),
        "engine_source": engine_source,
        "event": event,
        "head": None,
        "merge_base": None,
        "mode": None,
        "policy_blob": None,
        "policy_path": policy_path,
        "reason": "unclassified",
        "repository": repository,
        "route": "full",
        "schema_version": ATTESTATION_SCHEMA_VERSION,
        "selected_bundles": [],
    }


def _finalize(attestation: dict[str, Any]) -> dict[str, Any]:
    """Bind every plan field with a deterministic SHA-256 digest."""
    canonical = json.dumps(attestation, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")
    result = dict(attestation)
    result["plan_digest"] = hashlib.sha256(canonical).hexdigest()
    return result


def classify(
    repo: str,
    event: str,
    base_revision: str,
    head_revision: str,
    policy_path: str,
    repository: str,
    engine_commit: str,
    engine_source: str = "transpara-ai/dev-ops",
) -> dict[str, Any]:
    """Build one deterministic plan, choosing full for every unproved input."""
    attestation = _base_attestation(repository, event, engine_source, engine_commit, policy_path)
    if event not in {"pull_request", "push"}:
        attestation["reason"] = "invalid_event"
        return _finalize(attestation)
    if not ENGINE_COMMIT.fullmatch(engine_commit):
        attestation["reason"] = "invalid_engine_commit"
        return _finalize(attestation)
    if not ENGINE_SOURCE.fullmatch(engine_source):
        attestation["reason"] = "invalid_engine_source"
        return _finalize(attestation)
    if attestation["engine_files"] is None:
        attestation["reason"] = "missing_engine_file"
        return _finalize(attestation)
    if not ENGINE_SOURCE.fullmatch(repository):
        attestation["reason"] = "invalid_repository"
        return _finalize(attestation)
    if not valid_policy_path(policy_path):
        attestation["reason"] = "invalid_policy_path"
        return _finalize(attestation)

    base = resolve_event_commit(repo, base_revision)
    head = resolve_event_commit(repo, head_revision)
    checked_out_head = resolve_head(repo)
    attestation.update(base=base, head=head, checked_out_head=checked_out_head)
    if base is None or head is None:
        attestation["reason"] = "invalid_base_or_head"
        return _finalize(attestation)
    if checked_out_head != head:
        attestation["reason"] = "head_not_checked_out"
        return _finalize(attestation)

    merge_base = merge_base_for_event(repo, event, base, head)
    attestation["merge_base"] = merge_base
    if merge_base is None:
        attestation["reason"] = "unproved_merge_base"
        return _finalize(attestation)

    base_blob = read_tree_blob(repo, base, policy_path)
    if base_blob is None:
        attestation["reason"] = "missing_base_policy"
        return _finalize(attestation)
    attestation["policy_blob"] = base_blob.object_id
    try:
        policy = parse_policy(base_blob.content)
    except PolicyError:
        attestation["reason"] = "invalid_base_policy"
        return _finalize(attestation)
    attestation["mode"] = policy.mode
    attestation["selected_bundles"] = list(policy.bundles)

    head_blob = read_tree_blob(repo, head, policy_path)
    if head_blob is None or (head_blob.mode, head_blob.object_id) != (base_blob.mode, base_blob.object_id):
        attestation["reason"] = "policy_changed"
        return _finalize(attestation)
    if policy.mode == "force-full":
        attestation["reason"] = "policy_force_full"
        return _finalize(attestation)

    start = merge_base if event == "pull_request" else base
    try:
        changes, raw_diff = raw_changes(repo, start, head, len(head))
    except DiffError:
        attestation["reason"] = "invalid_or_empty_diff"
        return _finalize(attestation)
    attestation["changes"] = [change.public() for change in changes]
    attestation["diff_digest"] = hashlib.sha256(raw_diff).hexdigest()
    reason, selected = select_bundles(policy, changes)
    attestation["reason"] = reason
    attestation["selected_bundles"] = list(selected)
    if reason == "mapped":
        attestation["route"] = "focused"
    return _finalize(attestation)


def canonical_json(value: dict[str, Any]) -> bytes:
    """Serialize an attestation identically on every supported host."""
    return (json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", default=".", help="exact-head Git checkout")
    parser.add_argument("--event", required=True, choices=("pull_request", "push"))
    parser.add_argument("--base", required=True, help="complete actual base or before object ID")
    parser.add_argument("--head", required=True, help="complete actual head or after object ID")
    parser.add_argument("--policy", default=DEFAULT_POLICY_PATH, help="base-controlled policy path")
    parser.add_argument("--repository", required=True, help="owner/name recorded in the attestation")
    parser.add_argument("--engine-source", required=True, help="owner/name containing the vendored engine commit")
    parser.add_argument("--engine-commit", required=True, help="immutable shared-engine commit ID")
    parser.add_argument("--output", help="write canonical attestation JSON to this path")
    args = parser.parse_args(argv)

    plan = classify(
        repo=args.repo,
        event=args.event,
        base_revision=args.base,
        head_revision=args.head,
        policy_path=args.policy,
        repository=args.repository,
        engine_commit=args.engine_commit,
        engine_source=args.engine_source,
    )
    encoded = canonical_json(plan)
    if args.output:
        Path(args.output).write_bytes(encoded)
    sys.stdout.buffer.write(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
