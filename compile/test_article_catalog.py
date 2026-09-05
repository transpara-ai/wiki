#!/usr/bin/env python3

import json
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from article_catalog import CatalogError, load_catalog  # noqa: E402
from knowledge_structure import (  # noqa: E402
    DEFAULT_REGISTRY_PATH,
    StructureError,
    load_structure,
)


class KnowledgeStructureTests(unittest.TestCase):
    def test_committed_registry_has_three_reader_spaces(self):
        structure = load_structure()
        self.assertEqual(
            [space.key for space in structure.spaces],
            ["civilization", "platform", "competition"],
        )
        self.assertEqual(structure.space_map["platform"].steward, "transpara")
        self.assertEqual(
            structure.legacy_placement("transpara-ai", "architecture"),
            "civilization/architecture",
        )

    def test_unknown_placement_fails_closed(self):
        structure = load_structure()
        with self.assertRaisesRegex(StructureError, "unknown section"):
            structure.split_placement("platform/not-real")

    def test_disabled_public_profile_cannot_be_selected(self):
        structure = load_structure()
        with self.assertRaisesRegex(StructureError, "disabled"):
            structure.profile("public-platform")
        self.assertFalse(
            structure.profile("public-platform", require_enabled=False).enabled)

    def test_duplicate_space_key_is_rejected(self):
        payload = json.loads(DEFAULT_REGISTRY_PATH.read_text())
        payload["spaces"].append(dict(payload["spaces"][0]))
        with tempfile.TemporaryDirectory() as td:
            path = pathlib.Path(td) / "registry.json"
            path.write_text(json.dumps(payload))
            with self.assertRaisesRegex(StructureError, "duplicate key"):
                load_structure(path)


class ArticleCatalogTests(unittest.TestCase):
    def make_root(self, articles):
        td = tempfile.TemporaryDirectory()
        root = pathlib.Path(td.name)
        (root / "wiki").mkdir()
        for slug, text in articles.items():
            (root / "wiki" / (slug + ".md")).write_text(text)
        self.addCleanup(td.cleanup)
        return root

    def test_legacy_metadata_derives_civilization_placement(self):
        root = self.make_root({
            "event-graph": "---\nentity: Event Graph\ntier: architecture\n---\n# Event Graph\n",
        })
        record = load_catalog(root).by_slug["event-graph"]
        self.assertEqual(record.org, "transpara-ai")
        self.assertEqual(record.primary_placement, "civilization/architecture")
        self.assertEqual(record.placements, ("civilization/architecture",))
        self.assertEqual(record.classification, "internal")
        self.assertEqual(
            record.compatibility_fields,
            ("org", "primary_placement", "placements", "classification"),
        )

    def test_explicit_shared_placement_is_one_article_in_two_spaces(self):
        root = self.make_root({
            "boundary": (
                "---\nentity: Boundary\norg: transpara\ntier: product\n"
                "primary_placement: platform/development-apis\nplacements:\n"
                "  - platform/development-apis\n  - civilization/architecture\n"
                "classification: company-internal\nsource_authority: engineering-docs\n"
                "---\n# Boundary\n"
            ),
        })
        catalog = load_catalog(root, require_explicit=True)
        self.assertEqual(len(catalog), 1)
        self.assertEqual(catalog.counts()["article_count"], 1)
        self.assertEqual(catalog.counts()["space_counts"]["platform"], 1)
        self.assertEqual(catalog.counts()["space_counts"]["civilization"], 1)

    def test_primary_must_be_in_placements(self):
        root = self.make_root({
            "bad": (
                "---\nentity: Bad\norg: transpara\ntier: product\n"
                "primary_placement: platform/components\nplacements:\n"
                "  - platform/architecture\nclassification: internal\n---\n# Bad\n"
            ),
        })
        with self.assertRaisesRegex(CatalogError, "must be present"):
            load_catalog(root)

    def test_explicit_mode_reports_missing_fields(self):
        root = self.make_root({
            "legacy": "---\nentity: Legacy\ntier: concept\n---\n# Legacy\n",
        })
        with self.assertRaisesRegex(CatalogError, "missing explicit fields"):
            load_catalog(root, require_explicit=True)

    def test_unknown_source_authority_is_rejected(self):
        root = self.make_root({
            "bad": (
                "---\nentity: Bad\norg: transpara-ai\ntier: concept\n"
                "primary_placement: civilization/concept\nplacements: [civilization/concept]\n"
                "classification: internal\nsource_authority: invented\n---\n# Bad\n"
            ),
        })
        with self.assertRaisesRegex(CatalogError, "unknown source_authority"):
            load_catalog(root)


if __name__ == "__main__":
    unittest.main()
