"""Mutation tests for the fixed Wiki documentation contract."""

from __future__ import annotations

import importlib.util
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
        """Break a current owned document, not a synthetic contract sample."""
        source = ROOT / "docs" / "profile-menu.md"
        content = source.read_text(encoding="utf-8")
        self.assertTrue(content.endswith("\n"))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / source.name
            path.write_text(content.rstrip("\n"), encoding="utf-8")
            with self.assertRaisesRegex(CHECKER.ContractError, "final newline"):
                CHECKER.validate_document(path)


if __name__ == "__main__":
    unittest.main()
