"""Offline storage inventory checks; no site creation or native permission claims."""
from __future__ import annotations

import json
from pathlib import Path
import unittest

CONTRACT = (
    Path(__file__).resolve().parents[1]
    / "modules" / "careops-medical-job-planning" / "storage-contract.json"
)


class StorageInventory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def test_inventory_matches_source_structure(self):
        self.assertEqual(len(self.data["lists"]), 20)
        self.assertEqual(len(self.data["libraries"]), 1)
        self.assertEqual(self.data["libraries"][0]["name"], "JP_ApprovedPlanRecords")
        names = [item["name"] for item in self.data["lists"] + self.data["libraries"]]
        self.assertEqual(len(set(names)), 21)
        self.assertTrue(all(name.startswith("JP_") for name in names))
        self.assertEqual(
            self.data["source"]["path"], "config/data-model.json"
        )
        self.assertEqual(len(self.data["source"]["source_sha256"]), 64)

    def test_each_source_list_has_explicit_internal_column_inventory(self):
        for item in self.data["lists"]:
            with self.subTest(list=item["name"]):
                fields = item["required_source_fields"]
                self.assertGreaterEqual(len(fields), 3)
                self.assertEqual(len(fields), len(set(fields)))
                self.assertIn("Key", fields)
                self.assertIn("Title", fields)
                self.assertIn("Payload", fields)
                self.assertEqual(
                    item["source_field_status"], "prototype-synthetic-not-native-qualified"
                )

    def test_cohorts_have_no_implicit_native_authority(self):
        groups = {x["key"] for x in self.data["boundaries"]}
        self.assertEqual(groups, {
            "practitioner-restricted", "service-approver-restricted",
            "admin-restricted",
        })
        for item in self.data["lists"] + self.data["libraries"]:
            with self.subTest(item=item["name"]):
                self.assertIn(item["logical_boundary"], groups)
                self.assertEqual(item["provisioning"], "not-authorised")
                self.assertEqual(
                    item["access_control"], "must-be-enforced-in-native-storage"
                )
        self.assertTrue(all(x["tenant_binding"] is None for x in self.data["boundaries"]))
        self.assertTrue(all(
            x["physical_acl_qualification"] == "unverified"
            for x in self.data["boundaries"]
        ))

    def test_no_automatic_email_or_real_people_data(self):
        self.assertEqual(self.data["delivery"]["email_delivery"], "off")
        self.assertTrue(self.data["delivery"]["authorisation_required"])
        self.assertEqual(self.data["classification"], "configuration-only:no-personnel-data")
        observed = next(x for x in self.data["lists"] if x["name"] == "JP_ActivityObservations")
        self.assertEqual(
            observed["record_authority"],
            "external-observed-activity-reference-only",
        )

    def test_native_failure_and_scale_checks_cannot_be_inferred(self):
        criteria = " ".join(self.data["acceptance"]).lower()
        for required in ("direct-url", "revocation", "5000", "etag", "429", "retention"):
            self.assertIn(required, criteria)
        self.assertEqual(self.data["delivery"]["native_solution"], "not-qualified")


if __name__ == "__main__":
    unittest.main()
