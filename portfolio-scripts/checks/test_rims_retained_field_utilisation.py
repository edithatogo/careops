"""Synthetic-only retained-provider field and consumer utilisation tests."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest

module_file = Path(__file__).resolve().parents[1] / "rims_retained_field_utilisation.py"
spec = spec_from_file_location("rims_retained_field_utilisation", module_file)
mod = module_from_spec(spec)
spec.loader.exec_module(mod)

HASH = "a" * 64


class UtilisationTests(unittest.TestCase):
    def setUp(self):
        self.records = [
            {"id": "fictional-1",
             "contributors": [{"affiliation": "synthetic"}, {"affiliation": None}],
             "abstract": "synthetic abstract", "grants": [],
             "citations": 0},
            {"id": "fictional-2",
             "contributors": [{"affiliation": "synthetic"}],
             "abstract": None, "citations": 4, "extra": {"unknown": True}},
        ]

    def test_full_nested_schema_presence_and_missingness(self):
        result = mod.profile(
            "synthetic-pubmed", self.records, source_sha256=HASH,
            declared_paths=["/id", "/abstract", "/grants", "/extra/unknown",
                            "/never_returned"],
        )
        by_path = {row["path"]: row for row in result["fields"]}
        self.assertEqual(by_path["/contributors/[]/affiliation"]["occurrences"], 3)
        self.assertEqual(by_path["/contributors/[]/affiliation"]["null_occurrences"], 1)
        self.assertEqual(by_path["/abstract"]["records_present"], 2)
        self.assertEqual(by_path["/abstract"]["null_occurrences"], 1)
        self.assertEqual(by_path["/extra/unknown"]["records_missing"], 1)
        self.assertEqual(by_path["/never_returned"]["records_missing"], 2)
        self.assertEqual(by_path["/grants"]["empty_occurrences"], 1)
        self.assertFalse(result["contains_values"])
        self.assertNotIn("synthetic abstract", str(result))
        self.assertFalse(result["full_provider_schema_coverage_verified"])

    def test_retained_only_not_confused_with_utilisation(self):
        result = mod.profile("synthetic", [{"a": 1, "b": {"c": 2}}],
                             source_sha256=HASH)
        usage = mod.utilisation(result, [
            {"source_path": "/a", "disposition": "mapped",
             "consumer": "dashboard", "artifact_id": "fake-model",
             "artifact_revision": "v1", "target_field": "Quantity"},
            {"source_path": "/b/c", "disposition": "retained_only",
             "reason": "Consumer not yet designed"},
        ])
        self.assertTrue(usage["all_paths_accounted_for"])
        self.assertFalse(usage["all_paths_used"])
        self.assertEqual(usage["mapped_to_consumer"], 1)
        self.assertEqual(usage["retained_only"], 1)
        self.assertEqual(usage["paths_by_consumer"]["dashboard"], 1)
        self.assertFalse(usage["consumer_binding_native_verified"])

    def test_source_field_unassessed_not_silently_dropped(self):
        result = mod.profile("source", [{"a": 1, "b": 2}], source_sha256=HASH)
        usage = mod.utilisation(result, [
            {"source_path": "/a", "disposition": "excluded", "reason": "rights"},
        ])
        self.assertEqual(usage["unassessed_paths"], ["/b"])
        self.assertFalse(usage["all_paths_accounted_for"])

    def test_unknown_field_and_empty_artifact_refused(self):
        result = mod.profile("source", [{"a": 1}], source_sha256=HASH)
        with self.assertRaises(mod.UtilisationError):
            mod.utilisation(result, [
                {"source_path": "/bad", "disposition": "mapped",
                 "consumer": "gold", "artifact_id": "x", "artifact_revision": "1",
                 "target_field": "x"},
            ])
        with self.assertRaises(mod.UtilisationError):
            mod.utilisation(result, [
                {"source_path": "/a", "disposition": "mapped",
                 "consumer": "semantic_model", "artifact_id": "",
                 "artifact_revision": "1", "target_field": "A"},
            ])

    def test_no_secret_or_raw_value_in_output(self):
        records = [{"private": "fictional secret", "arr": [None, 1, False]}]
        result = mod.profile("synthetic", records, source_sha256=HASH)
        self.assertNotIn("fictional secret", str(result))
        fields = {r["path"]: r for r in result["fields"]}
        self.assertEqual(fields["/arr/[]"]["occurrences"], 3)
        self.assertEqual(set(fields["/arr/[]"]["types"]),
                         {"integer", "null", "boolean"})

    def test_exclusions_and_duplicate_links_fail_closed(self):
        result = mod.profile("source", [{"a": 1}], source_sha256=HASH)
        with self.assertRaises(mod.UtilisationError):
            mod.utilisation(result, [
                {"source_path": "/a", "disposition": "excluded"},
            ])
        first = {"source_path": "/a", "disposition": "mapped",
                 "consumer": "gold", "artifact_id": "v1",
                 "artifact_revision": "abc", "target_field": "A"}
        with self.assertRaises(mod.UtilisationError):
            mod.utilisation(result, [first, first])

    def test_schema_pointer_escaping_and_mixed_types(self):
        result = mod.profile("source", [{"a/b": {"~": 1}},
                                       {"a/b": {"~": "two"}}],
                             source_sha256=HASH)
        self.assertEqual(result["fields"][0]["path"], "/a~1b/~0")
        self.assertEqual(result["fields"][0]["types"], ["integer", "string"])

    def test_defensive_source_bounds_and_invalid_numbers(self):
        with self.assertRaises(mod.UtilisationError):
            mod.profile("source", [{"n": float("nan")}], source_sha256=HASH)
        with self.assertRaises(mod.UtilisationError):
            mod.profile("source", [{"a": [[[0] * 1] * 1] * 1}],
                        source_sha256="bad")
        with self.assertRaises(mod.UtilisationError):
            mod.profile("source", [{str(i): i for i in range(10001)}],
                        source_sha256=HASH)


if __name__ == "__main__":
    unittest.main()
