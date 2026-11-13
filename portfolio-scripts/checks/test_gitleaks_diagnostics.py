"""Verify that Gitleaks CI diagnostics never log matched secrets or content."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[2] / ".careops-security" / "gitleaks_diagnostics.py"
SPEC = importlib.util.spec_from_file_location("gitleaks_diag", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class GitleaksDiagnosticTests(unittest.TestCase):
    def test_only_safe_metadata_printed(self) -> None:
        marker = "TEST_SECRET_VALUE_MUST_NOT_LEAK_24680"
        found = [{
            "Commit": "a" * 40,
            "File": "docs/example-fixture.json",
            "RuleID": "generic-api-key",
            "StartLine": 23,
            "Secret": marker,
            "Match": marker,
            "Description": marker,
            "Line": marker,
            "Author": marker,
        }]
        output = "\n".join(MODULE.summarise(found))
        self.assertIn("path=docs/example-fixture.json", output)
        self.assertIn("generic-api-key", output)
        self.assertNotIn(marker, output)
        self.assertNotIn("Secret", output)
        self.assertNotIn("Match", output)

    def test_rejects_multiline_path_instead_of_printing_it(self) -> None:
        found = [{
            "Commit": "a" * 40,
            "File": "docs/file\nSECRET_IN_PATH",
            "RuleID": "generic-api-key",
            "StartLine": 23,
            "Secret": "hidden",
        }]
        output = "\n".join(MODULE.summarise(found))
        self.assertIn("unavailable", output)
        self.assertNotIn("SECRET_IN_PATH", output)

    def test_counts_all_rules_and_keeps_fixed_limit(self) -> None:
        cases = [{"Commit": "b" * 40, "File": f"src/file{i}.py",
                  "RuleID": "generic-api-key", "StartLine": i + 1} for i in range(4)]
        output = MODULE.summarise(cases, limit=2)
        self.assertIn("findings: 4", output[0])
        self.assertIn("generic-api-key=4", output[1])
        self.assertEqual(sum(x.startswith("rule=") for x in output), 2)

    def test_invalid_report_is_not_treated_as_clear(self) -> None:
        self.assertIn("unavailable", MODULE.summarise({"not": "array"})[0])
        self.assertIn("unavailable", MODULE.summarise([{"Secret": "fake"}])[0])


if __name__ == "__main__":
    unittest.main()
