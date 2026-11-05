"""Mutation tests for the fixed Wiki documentation contract."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_checker():
    """Load the executable checker without requiring a tools package."""
    name = "wiki_repository_contracts"
    spec = importlib.util.spec_from_file_location(
        name, ROOT / "tools" / "check_repository_contracts.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


CHECKER = load_checker()


class DocumentationContractTests(unittest.TestCase):
    """Prove current documents pass and malformed content is rejected."""

    def test_every_owned_current_document_passes(self) -> None:
        documents = CHECKER.check(ROOT)
        self.assertGreaterEqual(len(documents), 5)

    def test_missing_heading_mutation_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "broken.md"
            path.write_text("plain text only\n", encoding="utf-8")
            with self.assertRaisesRegex(CHECKER.ContractError, "heading"):
                CHECKER.validate_document(path)

    def test_real_focused_document_mutation_is_rejected(self) -> None:
        """Break one current owned document without pinning its repository path."""
        source = CHECKER.owned_documents(ROOT)[0]
        content = source.read_text(encoding="utf-8")
        self.assertTrue(content.endswith("\n"))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / source.name
            path.write_text(content.rstrip("\n"), encoding="utf-8")
            with self.assertRaisesRegex(CHECKER.ContractError, "final newline"):
                CHECKER.validate_document(path)

    def test_owned_document_inventory_follows_a_tracked_rename(self) -> None:
        """Keep the public contract valid when an owned path is renamed.

        The checker owns the tracked pattern surface, not a historical filename.
        A staged rename therefore validates the new path and stops reading the
        removed path without weakening the Markdown content contract.
        """
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            docs = root / "docs"
            docs.mkdir()
            original = docs / "profile-menu.md"
            original.write_text("# Profile menu\n", encoding="utf-8")
            retained = docs / "retained.md"
            retained.write_text("# Retained\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "docs"], check=True)
            subprocess.run(
                ["git", "-C", str(root), "mv", "docs/profile-menu.md", "docs/navigation-menu.md"],
                check=True,
            )

            relative = {
                path.relative_to(root).as_posix()
                for path in CHECKER.check(root)
            }
            self.assertEqual(relative, {"docs/navigation-menu.md", "docs/retained.md"})
            self.assertFalse(original.exists())


if __name__ == "__main__":
    unittest.main()
