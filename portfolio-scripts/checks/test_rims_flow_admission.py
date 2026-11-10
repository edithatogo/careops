"""Fictional, tenant-free source flow admission regression tests."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

source = Path(__file__).resolve().parents[1] / "rims_flow_admission.py"
spec = importlib.util.spec_from_file_location("rims_flow_admission", source)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def flow(actions=None, connection=None):
    obj = {"properties": {"definition": {
        "triggers": {"start": {"type": "Request"}}, "actions": actions or {}
    }}}
    if connection:
        obj["properties"]["definition"]["actions"]["Native"] = {
            "type": "OpenApiConnection",
            "runAfter": {},
            "inputs": {"host": {
                "apiId": "/providers/Microsoft.PowerApps/apis/" + connection
            }},
        }
    return json.dumps(obj).encode("utf-8")


class FlowAdmissionTests(unittest.TestCase):
    def test_generated_report_matches_declared_schema_required_keys(self):
        contract_path = (
            Path(__file__).resolve().parents[2]
            / "conductor/tracks/rims_native_flow_quality_20261110"
            / "contracts/flow-admission.schema.json"
        )
        schema = json.loads(contract_path.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "synthetic.zip"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("Workflows/Fictional.json", flow())
            result = audit.audit_zip(path)
        self.assertEqual(
            set(schema["required"]), set(result)
        )
        self.assertEqual(
            set(schema["properties"]["flows"]["items"]["required"]),
            set(result["flows"][0]),
        )
        self.assertEqual(
            set(schema["properties"]["summary"]["required"]),
            set(result["summary"]),
        )

    def test_simple_valid_flow_has_no_errors(self):
        record = audit.audit_flow(
            flow({"Pass": {"type": "Compose", "runAfter": {}, "inputs": 1}}),
            "Fictional.json",
        )
        self.assertEqual(record["nested_actions"], 1)
        self.assertEqual(record["errors"], [])
        self.assertFalse(record["personal_path_candidate"])

    def test_inactive_http_branch_cannot_be_core(self):
        actions = {"IfTest": {
            "type": "If", "runAfter": {}, "expression": {"equals": [1, 0]},
            "actions": {"HTTP": {
                "type": "Http", "runAfter": {},
                "inputs": {"uri": "https://invalid.example"}
            }},
        }}
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "fictional.zip"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("Workflows/Fictional.json", flow(actions))
            result = audit.audit_zip(path, core_flows=["Fictional"])
            self.assertIn(
                "UNQUALIFIED_CORE_DEPENDENCY", result["flows"][0]["errors"]
            )
            self.assertEqual(result["summary"]["invalid_flows"], 1)

    def test_runafter_cycles_and_dangling_links(self):
        actions = {
            "A": {"type": "Compose", "runAfter": {"B": ["Succeeded"]}},
            "B": {"type": "Compose", "runAfter": {"A": ["Succeeded"]}},
        }
        self.assertIn(
            "RUNAFTER_CYCLE", audit.audit_flow(flow(actions), "fake.json")["errors"]
        )
        actions["A"]["runAfter"] = {"absent": ["Succeeded"]}
        self.assertIn(
            "DANGLING_RUNAFTER", audit.audit_flow(flow(actions), "fake.json")["errors"]
        )

    def test_unused_declared_dataverse_is_still_premium(self):
        original = json.loads(flow())
        original["properties"]["connectionReferences"] = {
            "shared_commondataserviceforapps": {
                "api": {"name": "shared_commondataserviceforapps"}
            }
        }
        with tempfile.TemporaryDirectory() as folder:
            archive_path = Path(folder) / "sample.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("Workflows/Fictional.json", json.dumps(original))
            result = audit.audit_zip(archive_path, core_flows=["Fictional"])
            self.assertIn(
                "UNQUALIFIED_CORE_DEPENDENCY", result["flows"][0]["errors"]
            )
            self.assertIn(
                "CONNECTOR_shared_commondataserviceforapps",
                result["flows"][0]["premium_candidates"]
            )

    def test_unknown_connector_not_silently_approved(self):
        result = audit.audit_flow(
            flow(connection="shared_unqualified"), "fictional.json"
        )
        self.assertEqual(result["unqualified_connectors"], ["shared_unqualified"])

    def test_included_source_status_is_not_human_approval(self):
        actions = {"Insert": {
            "type": "OpenApiConnection", "runAfter": {},
            "inputs": {"parameters": {"item/field_17": "Included"}},
        }}
        result = audit.audit_flow(flow(actions), "f.json")
        self.assertEqual(result["source_included_writes"], 1)
        self.assertFalse(result["native_verified"])

    def test_personal_paths_are_redacted(self):
        actions = {"Save": {
            "type": "Compose", "runAfter": {},
            "inputs": "https://example-my.sharepoint.com/personal/fictional-user/private"
        }}
        result = audit.audit_flow(flow(actions), "f.json")
        self.assertTrue(result["personal_path_candidate"])
        self.assertNotIn("fictional-user", json.dumps(result))

    def test_duplicate_source_keys_refused(self):
        raw = b'{"properties":{"definition":{"triggers":{},"actions":{},"actions":{}}}}'
        with self.assertRaises(audit.AdmissionError):
            audit.audit_flow(raw, "bad.json")

    def test_nested_if_else_actions_count_once(self):
        actions = {"Condition": {
            "type": "If", "runAfter": {},
            "actions": {"Yes": {"type": "Compose", "runAfter": {}}},
            "else": {"actions": {"No": {"type": "Compose", "runAfter": {}}}},
        }}
        self.assertEqual(
            audit.audit_flow(flow(actions), "fake.json")["nested_actions"], 3
        )

    def test_invalid_action_object_and_status_refused(self):
        actions = {
            "broken": None,
            "valid": {"type": "Compose", "runAfter": {"broken": ["Unknown"]}},
        }
        report = audit.audit_flow(flow(actions), "fake.json")
        self.assertIn("INVALID_ACTION_OBJECT", report["errors"])
        self.assertIn("INVALID_RUNAFTER_STATUS", report["errors"])


if __name__ == "__main__":
    unittest.main()
