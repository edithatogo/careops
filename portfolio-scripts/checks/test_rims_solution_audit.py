"""Offline RIMS solution scan fixtures: no environment or tenant dependency."""
import io
import json
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import tempfile
import unittest
import zipfile

path = Path(__file__).resolve().parents[1] / "rims_solution_audit.py"
spec = spec_from_file_location("rims_solution_audit", path)
audit = module_from_spec(spec)
spec.loader.exec_module(audit)


class SolutionAuditTests(unittest.TestCase):
    def test_detects_hardcoded_inclusion_without_disclosing_addresses(self):
        flow = {"properties": {"definition": {"actions": {
            "create": {"inputs": {"parameters": {"item/field_17": "Included"}}},
            "read": {"inputs": {"select": {"ReviewStatus": "Included"}}}}}},
            "connectionReferences": {"a": {"id": "shared_sharepointonline"}}}
        output = audit.inspect_bytes(json.dumps(flow).encode(), "synthetic.json")
        self.assertEqual(len(output["forced_inclusion_assignments"]), 1)
        self.assertEqual(output["unclassified_connectors"], [])
        self.assertNotIn("site_url", json.dumps(output))

    def test_unclassified_connector_is_flagged(self):
        obj = {"body": {"connector": "shared_commondataserviceforapps"}}
        report = audit.inspect_bytes(json.dumps(obj).encode(), "synthetic.json")
        self.assertIn("shared_commondataserviceforapps", report["unclassified_connectors"])

    def test_zip_fingerprint_and_workflow_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            zip_path = Path(tmp) / "sample.zip"
            with zipfile.ZipFile(zip_path, "w") as f:
                f.writestr("Workflows/a.json", json.dumps({"definition": {}}))
                f.writestr("other.txt", "synthetic")
            report = audit.audit_zip(zip_path)
            self.assertEqual(report["workflow_count"], 1)
            self.assertEqual(report["forced_inclusion_count"], 0)


if __name__ == "__main__":
    unittest.main()
