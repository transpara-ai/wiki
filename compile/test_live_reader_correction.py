#!/usr/bin/env python3
"""Tests for the Event 14 public-safe live-reader correction fixture."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import re
import subprocess
import unittest

import live_reader_correction as fixture


ROOT = Path(__file__).resolve().parents[1]


class LiveReaderCorrectionFixtureTests(unittest.TestCase):
    def test_fixture_is_public_safe_display_only_and_operation_sourced(self) -> None:
        payload = fixture.build_fixture()
        self.assertEqual(fixture.validate_fixture(payload), [])
        self.assertEqual(payload["schema_version"], 1)
        self.assertTrue(payload["display_only"])
        self.assertTrue(payload["privacy"]["public_safe"])
        self.assertEqual(payload["source"]["operation_pr"], "transpara-ai/civilization-operation#30")
        self.assertEqual(
            payload["source"]["operation_reviewed_head"],
            "08786bdcfc6034ac877dd5aa2fbb0e7883cb3b85",
        )
        self.assertEqual(
            payload["source"]["operation_merge_commit"],
            "45b3e9f219d7b81c9991c253d2db4f906d6034bc",
        )
        self.assertEqual(payload["source"]["network_access"], "none")

    def test_shipped_js_payload_matches_python_fixture(self) -> None:
        script = """
const fs = require('fs');
const vm = require('vm');
const context = { window: {} };
vm.createContext(context);
vm.runInContext(fs.readFileSync('compile/assets/civilizationArcData.js', 'utf8'), context);
process.stdout.write(JSON.stringify(context.window.CIVILIZATION_LIVE_READER_CORRECTION));
"""
        result = subprocess.run(
            ["node", "-e", script],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertEqual(json.loads(result.stdout), fixture.build_fixture())

    def test_fixture_surfaces_required_labels_and_not_zero_progress(self) -> None:
        payload = fixture.build_fixture()
        evidence_states = {item["evidence_state"] for item in payload["items"]}
        freshness_states = {item["freshness_state"] for item in payload["items"]}
        omitted_states = {source["freshness_state"] for source in payload["omitted_sources"]}

        self.assertIn("corrected", evidence_states)
        self.assertIn("superseded", evidence_states)
        self.assertIn("stale", freshness_states)
        self.assertIn("missing", omitted_states)
        self.assertIn("unavailable", omitted_states)
        self.assertIn("unavailable", payload["freshness"]["unavailable_policy"])
        self.assertNotIn("zero progress", json.dumps(payload["items"], sort_keys=True).lower())

    def test_correction_references_emitted_superseded_and_corrected_items(self) -> None:
        payload = fixture.build_fixture()
        items = {item["id"]: item for item in payload["items"]}
        correction = payload["corrections"][0]

        self.assertEqual(items[correction["supersedes_item_id"]]["evidence_state"], "superseded")
        self.assertEqual(items[correction["corrected_item_id"]]["evidence_state"], "corrected")
        self.assertEqual(correction["prior_public_state"], "green")
        self.assertEqual(correction["corrected_state"], "yellow")
        self.assertTrue(correction["source_refs"])
        self.assertTrue(correction["limitation"])

    def test_global_stale_missing_or_unavailable_payload_fails_closed(self) -> None:
        for state in ("stale", "missing", "unavailable"):
            payload = fixture.build_fixture()
            payload["freshness"]["state"] = state
            errors = fixture.validate_fixture(payload)
            self.assertTrue(
                any("global freshness" in error for error in errors),
                f"{state} should fail closed: {errors}",
            )

    def test_missing_public_safe_metadata_fails_closed(self) -> None:
        payload = fixture.build_fixture()
        payload["privacy"]["public_safe"] = False
        self.assertIn("privacy.public_safe must be true", fixture.validate_fixture(payload))

        payload = fixture.build_fixture()
        payload["items"][0]["display_only"] = False
        self.assertTrue(any("display-only" in error for error in fixture.validate_fixture(payload)))

    def test_rendered_js_fixture_validates_before_output(self) -> None:
        js = fixture.render_js_fixture()
        self.assertIn("window.CIVILIZATION_LIVE_READER_CORRECTION", js)
        self.assertIn("correction-test-001-yellow-not-green", js)
        self.assertIn("civilization-operation#30", js)

        bad = fixture.build_fixture()
        bad["corrections"][0]["corrected_item_id"] = "missing-item"
        with self.assertRaises(ValueError):
            fixture.render_js_fixture(bad)

    def test_no_active_private_fetch_deploy_runtime_or_protected_paths(self) -> None:
        public_payload_text = json.dumps(fixture.build_fixture(), sort_keys=True)
        rendered_js = fixture.render_js_fixture()
        forbidden = re.compile(
            r"(api\.github\.com|fetch\(|XMLHttpRequest|RuntimeBroker|EventGraph write|"
            r"protected setting|protected action|production readiness|deploy hook|GITHUB_TOKEN)",
            re.IGNORECASE,
        )
        self.assertFalse(forbidden.search(public_payload_text))
        self.assertFalse(forbidden.search(rendered_js))


if __name__ == "__main__":
    unittest.main()
