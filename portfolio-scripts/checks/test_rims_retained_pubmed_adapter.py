"""Synthetic retained PubMed consumer compatibility/identity/privacy tests."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest

path = Path(__file__).resolve().parents[1] / "rims_retained_pubmed_adapter.py"
spec = spec_from_file_location("rims_retained_pubmed_adapter", path)
adapter = module_from_spec(spec)
spec.loader.exec_module(adapter)


class RetainedPubMedTests(unittest.TestCase):
    def setUp(self):
        self.consumer = {
            "kind": "isolated_retained_pubmed_consumer_v1",
            "canonical_admission": False,
            "working_model_modified": False,
            "observed_utc": "2026-11-10T00:00:00Z",
            "publication_count": 1,
            "rows": [{"summary": {"PMID": "synthetic-pmid"},
                      "metadata": {"title": "Synthetic",
                                   "contributors": [{"fictional": True}],
                                   "unknown_provider_field": [1, 2]}}],
            "author_evidence": [{"[PMID]": "synthetic-pmid",
                                 "[AuthorIndex]": 1,
                                 "[AffiliationIndex]": 0}],
        }

    def call(self, **kwargs):
        return adapter.reconcile_pubmed(
            self.consumer,
            canonical_by_pmid={"synthetic-pmid": "canonical-synthetic"},
            verify_consumer=lambda source: True,
            licence="synthetic",
            retention_class="fictional",
            **kwargs,
        )

    def test_retains_metadata_and_author_inventory_without_admission(self):
        result = self.call(mapping={"title": "title"})
        self.assertEqual(result["source_count"], 1)
        self.assertEqual(result["author_evidence_count"], 1)
        self.assertEqual(result["bronze_records"][0]["raw_payload"],
                         self.consumer["rows"][0]["metadata"])
        silver = result["silver_records"][0]
        self.assertIn("unknown_provider_field",
                      silver["typed_attributes"]["_retained_unmapped"])
        self.assertFalse(result["native_admission_authorised"])
        self.assertFalse(result["full_source_field_coverage_verified"])

    def test_full_pubmed_xml_shaped_field_profile(self):
        self.consumer["commit_sha256"] = "d" * 64
        self.consumer["rows"][0]["metadata"] = {
            "Name": "MedlineCitation",
            "Value": [
                {"Name": "Article", "Value": [
                    {"Name": "Abstract", "Value": "Fictional text"},
                    {"Name": "AuthorList", "Value": [
                        {"Name": "Author", "Value": {"ForeName": "Synthetic"}}
                    ]},
                ]},
            ],
            "Attributes": {"Status": "synthetic"},
        }
        result=adapter.profile_retained_pubmed(
            self.consumer, verify_consumer=lambda obj: True
        )
        self.assertEqual(result["source_id"],"PubMed")
        self.assertEqual(result["records_observed"],1)
        self.assertTrue(result["paths_observed"] > 3)
        self.assertFalse(result["contains_values"])
        self.assertNotIn("Fictional text",str(result))
        self.assertFalse(result["full_provider_schema_coverage_verified"])

    def test_accepted_xml_list_root_not_discarded(self):
        self.consumer["commit_sha256"]="f"*64
        nodes=[{
            "Name":"MedlineCitation","Namespace":"","Attributes":[],
            "Value":[{
                "Name":"Article","Namespace":"","Attributes":[],
                "Value":[{
                    "Name":"ArticleTitle","Namespace":"","Attributes":[],
                    "Value":"Synthetic title",
                }],
            }],
        }]
        self.consumer["rows"][0]["metadata"]=nodes
        result=self.call()
        self.assertEqual(result["bronze_records"][0]["raw_payload"],nodes)
        self.assertEqual(
            result["silver_records"][0]["typed_attributes"]["xml_nodes"],nodes
        )
        profile=adapter.profile_retained_pubmed(
            self.consumer,verify_consumer=lambda source: True
        )
        paths={row["path"] for row in profile["fields"]}
        self.assertIn("/MedlineCitation/Article/ArticleTitle",paths)
        self.assertFalse(profile["contains_values"])

    def test_unverified_source_cannot_be_consumed(self):
        with self.assertRaises(adapter.RetainedSourceError):
            adapter.reconcile_pubmed(
                self.consumer,
                canonical_by_pmid={"synthetic-pmid": "synthetic"},
                licence="synthetic", retention_class="test",
            )

    def test_identifier_and_population_integrity(self):
        changed = {**self.consumer, "publication_count": 2}
        with self.assertRaises(adapter.RetainedSourceError):
            adapter.reconcile_pubmed(
                changed,
                canonical_by_pmid={"synthetic-pmid": "synthetic"},
                verify_consumer=lambda source: True,
                licence="synthetic", retention_class="test",
            )
        with self.assertRaises(adapter.RetainedSourceError):
            self.call(mapping={"unobserved_field": "invented"})

    def test_author_evidence_must_reference_retained_pmid(self):
        self.consumer["author_evidence"] = [
            {"[PMID]": "orphan", "[AuthorIndex]": 1},
        ]
        with self.assertRaises(adapter.RetainedSourceError):
            self.call()


if __name__ == "__main__":
    unittest.main()
