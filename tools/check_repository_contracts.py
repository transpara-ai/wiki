"""Validate the complete, explicitly focused Wiki documentation surface.

The fixed patterns mirror the only policy rule allowed to focus. Published
Wiki articles, spaces, release notes, and runtime inputs are deliberately
absent because they have broader content consumers. Unknown or new domains are
not guessed; the selector sends them to full verification.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
DOCUMENT_PATTERNS = (
    "docs/*.md",
    "docs/continuous-discovery/*.md",
    "docs/dark-factory/*.md",
    "docs/superpowers/plans/*.md",
    "docs/superpowers/research/*.md",
    "docs/superpowers/specs/*.md",
    "docs/wiki-architecture-comparison/*.md",
)


class ContractError(ValueError):
    """Report one documentation file that cannot satisfy the fixed contract."""


def tracked_files(root: Path) -> tuple[str, ...]:
    """Return tracked UTF-8 paths without accepting filesystem-only files."""
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        raise ContractError("cannot enumerate tracked documentation")
    try:
        return tuple(
            item.decode("utf-8", errors="strict")
            for item in result.stdout.split(b"\0")
            if item
        )
    except UnicodeDecodeError as exc:
        raise ContractError("tracked path is not UTF-8") from exc


def owned_documents(root: Path) -> tuple[Path, ...]:
    """Return existing tracked files owned by the documentation bundle."""
    matches = tuple(
        root / relative
        for relative in tracked_files(root)
        if any(PurePosixPath(relative).match(pattern) for pattern in DOCUMENT_PATTERNS)
    )
    if not matches:
        raise ContractError("focused documentation surface is empty")
    return matches


def validate_document(path: Path) -> None:
    """Require readable Markdown with a title/frontmatter and final newline."""
    try:
        content = path.read_bytes()
        text = content.decode("utf-8", errors="strict")
    except (OSError, UnicodeDecodeError) as exc:
        raise ContractError(f"cannot read UTF-8 documentation: {path}") from exc
    if not content or b"\0" in content:
        raise ContractError(f"documentation is empty or contains NUL: {path}")
    if not content.endswith(b"\n"):
        raise ContractError(f"documentation lacks a final newline: {path}")
    first = next((line.strip() for line in text.splitlines() if line.strip()), "")
    if first != "---" and not first.startswith("#"):
        raise ContractError(f"documentation lacks a heading or frontmatter: {path}")


def check(root: Path = ROOT) -> tuple[Path, ...]:
    """Validate every focused document and return the inspected paths."""
    documents = owned_documents(root)
    for path in documents:
        validate_document(path)
    return documents


def main() -> int:
    try:
        documents = check()
    except ContractError as exc:
        print(f"repository contract failed: {exc}", file=sys.stderr)
        return 1
    print(f"repository contracts: checked {len(documents)} focused documents")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
