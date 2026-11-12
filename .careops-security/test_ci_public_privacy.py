# Copyright (c) 2026 CareOps contributors.
# SPDX-License-Identifier: Apache-2.0
"""Synthetic acceptance tests for the public-repository semantic privacy gate."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("ci_public_privacy", HERE / "ci_public_privacy.py")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class PublicPrivacyBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.policy = {"repository": "edithatogo/careops", "host": "github.com",
                       "requiredVisibility": "PRIVATE"}
        self.public = {"full_name": "edithatogo/careops", "private": False,
                       "visibility": "public"}
        self.env = {"GITHUB_ACTIONS": "true", "GITHUB_REPOSITORY": "edithatogo/careops",
                    "GITHUB_EVENT_NAME": "pull_request"}

    def test_explicit_public_ci_identity_is_allowed_for_scanning_only(self):
        self.assertIsNone(gate.validate_context(self.policy, self.public, self.env))

    def test_private_unknown_or_wrong_target_is_rejected(self):
        for state in [
            {"full_name": "edithatogo/careops", "private": True, "visibility": "private"},
            {"full_name": "someone/else", "private": False, "visibility": "public"},
            {"full_name": "edithatogo/careops", "private": False},
            {},
        ]:
            with self.subTest(state=state), self.assertRaises(gate.Refusal):
                gate.validate_context(self.policy, state, self.env)

    def test_no_local_or_unexpected_action_can_use_public_ci_route(self):
        for changes in [
            {"GITHUB_ACTIONS": "false"},
            {"GITHUB_REPOSITORY": "else/repo"},
            {"GITHUB_EVENT_NAME": "pull_request_target"},
        ]:
            with self.subTest(changes=changes), self.assertRaises(gate.Refusal):
                gate.validate_context(self.policy, self.public, {**self.env, **changes})

    def test_isolated_cli_startup_resolves_sibling_module(self):
        import subprocess
        import sys
        result = subprocess.run(
            [sys.executable, "-I", str(HERE / "ci_public_privacy.py"), "--help"],
            capture_output=True, check=False, timeout=10,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn(b"--ci-base", result.stdout)

    def test_private_destination_policy_is_not_changed(self):
        import json
        policy = json.loads((HERE / "presidio-policy.json").read_text())
        self.assertEqual(policy["requiredVisibility"], "PRIVATE")


    def test_refusal_categories_are_bounded_and_non_disclosing(self):
        self.assertEqual(
            gate.classify_refusal(gate.Refusal("presidio_personal_details_detected")),
            "unreviewed_semantic_findings",
        )
        self.assertEqual(
            gate.classify_refusal(gate.Refusal("text_scope_limit")),
            "source_scope_limit",
        )
        self.assertEqual(
            gate.classify_refusal(gate.Refusal("unqualified_local_checkout")),
            "source_range_invalid",
        )
        self.assertEqual(
            gate.classify_refusal(gate.Refusal("secret-value-should-not-echo")),
            "verification_unavailable",
        )


if __name__ == "__main__":
    unittest.main()
