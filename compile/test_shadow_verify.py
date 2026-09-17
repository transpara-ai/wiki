#!/usr/bin/env python3
"""Regression tests for shadow-build link resolution."""

import tempfile
from pathlib import Path
import unittest

import shadow_verify


class ShadowLinkTests(unittest.TestCase):
    def test_exact_auth_proxy_routes_do_not_require_static_files(self):
        with tempfile.TemporaryDirectory() as name:
            candidate = Path(name)
            (candidate / "index.html").write_text(
                '<a href="/oauth2/start">login</a>'
                '<a href="/oauth2/sign_out?rd=https%3A%2F%2Fexample.test">logout</a>'
            )
            shadow_verify.assert_links_resolve(candidate)

    def test_nearby_unowned_route_still_fails_closed(self):
        with tempfile.TemporaryDirectory() as name:
            candidate = Path(name)
            (candidate / "index.html").write_text('<a href="/oauth2/start-typo">bad</a>')
            with self.assertRaisesRegex(AssertionError, "oauth2/start-typo"):
                shadow_verify.assert_links_resolve(candidate)


if __name__ == "__main__":
    unittest.main()
