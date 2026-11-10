"""Synthetic-only unused existing-source opportunities and privacy checks."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest

source = Path(__file__).resolve().parents[1] / "rims_utilisation_opportunities.py"
spec = spec_from_file_location("rims_utilisation_opportunities", source)
module = module_from_spec(spec)
spec.loader.exec_module(module)


class OpportunityTests(unittest.TestCase):
    def setUp(self):
        self.catalogue = {
            "schema": "careops-rims.existing-source-adoption/1",
            "sources": [{"source": "Synthetic", "primary_domain": "publications"}],
        }
        self.item = {
            "source": "Synthetic",
            "profile": {
                "schema": "careops-rims.retained-field-profile/1",
                "source_id": "Synthetic", "records_observed": 10,
                "fields": [
                    {"path": "/abstract", "records_present": 9,
                     "nonempty_occurrences": 9, "types": ["string"]},
                    {"path": "/authors/[]/name", "records_present": 8,
                     "nonempty_occurrences": 15, "types": ["string"]},
                    {"path": "/grants/[]", "records_present": 2,
                     "nonempty_occurrences": 3, "types": ["string"]},
                ],
            },
            "utilisation": {
                "schema": "careops-rims.retained-field-utilisation/1",
                "source_id": "Synthetic", "unassessed_paths": [
                    "/abstract", "/grants/[]"
                ],
                "source_field_count": 3, "mapped_to_consumer": 1,
                "retained_only": 0, "excluded_with_reason": 0,
                "unassessed": 2,
            },
        }

    def test_all_unassessed_paths_become_review_tasks(self):
        result = module.plan(self.catalogue, [self.item])
        self.assertEqual(result["unresolved_field_paths"], 2)
        self.assertEqual(
            {item["source_path"] for item in result["opportunities"]},
            {"/abstract", "/grants/[]"},
        )
        self.assertFalse(result["native_usage_verified"])
        self.assertTrue(all(
            item["verification"] == "source_mapping_pending"
            for item in result["opportunities"]
        ))

    def test_no_profile_is_not_complete(self):
        result = module.plan(self.catalogue, [])
        self.assertEqual(result["unprofiled_sources"], ["Synthetic"])
        self.assertIsNone(result["analytical_utilisation_fraction"])
        self.assertFalse(result["all_source_data_utilised"])

    def test_unqualified_counts_and_orphan_paths_refused(self):
        duplicate = [self.item, self.item]
        with self.assertRaises(module.OpportunityError):
            module.plan(self.catalogue, duplicate)
        bad = {**self.item, "utilisation": {
            **self.item["utilisation"], "unassessed_paths": ["/unknown"]
        }}
        with self.assertRaises(module.OpportunityError):
            module.plan(self.catalogue, [bad])
        bad_profile = {**self.item, "profile": {
            **self.item["profile"], "records_observed": -1
        }}
        with self.assertRaises(module.OpportunityError):
            module.plan(self.catalogue, [bad_profile])

    def test_profiling_does_not_expose_raw_data(self):
        secret = {**self.item, "private": "fictional token",
                  "profile": {**self.item["profile"], "fields": [
                      {**field, "secret": "fictional sensitive value"}
                      for field in self.item["profile"]["fields"]
                  ]}}
        result = module.plan(self.catalogue, [secret])
        self.assertNotIn("fictional token", str(result))
        self.assertNotIn("fictional sensitive value", str(result))


if __name__ == "__main__":
    unittest.main()
