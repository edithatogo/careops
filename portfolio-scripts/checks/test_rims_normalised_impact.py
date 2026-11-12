"""Minimal synthetic join/authority controls for normalised impact."""
import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location("rims_normalised_impact",Path(__file__).resolve().parents[1]/"rims_normalised_impact.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class ImpactTests(unittest.TestCase):
    def setUp(self):
        self.reg=[
            {"CanonicalKey":"PUB:1","ReviewStatus":"Included","DOI":"10.1000/a","PMID":"1","PublicationYear":"2,021"},
            {"CanonicalKey":"PUB:2","ReviewStatus":"Needs Review","DOI":"10.1000/b","PMID":"2","PublicationYear":"2021"},
        ]
        self.works=[{"openalex_id":"https://openalex.org/W10","doi":"https://doi.org/10.1000/a","pmid":"1"},
                    {"openalex_id":"https://openalex.org/W11","doi":"10.1000/b","pmid":"2"}]
        self.impact=[{"openalex_id":"https://openalex.org/W10","fwci":"1.5","is_top_decile":"true","primary_topic":"T"},
                     {"openalex_id":"https://openalex.org/W11","fwci":"4.5","is_top_decile":"true","primary_topic":"T"}]

    def test_source_only_inclusion_and_period(self):
        result=mod.aggregate(self.reg,self.works,self.impact)
        self.assertEqual(result["source_registry_included"],1)
        self.assertEqual(result["overall"]["matched_source_included"],1)
        self.assertEqual(result["periods"]["2018-2022"]["median_fwci"],1.5)
        self.assertEqual(result["periods"]["2018-2022"]["top_decile_count"],1)

    def test_unknown_percentile_not_considered_zero(self):
        self.impact[0]["is_top_decile"]=""
        result=mod.aggregate(self.reg,self.works,self.impact)
        self.assertEqual(result["overall"]["fwci_eligible"],1)
        self.assertEqual(result["overall"]["percentile_eligible"],0)

    def test_doi_pmid_conflict_quarantined(self):
        self.works[0]["pmid"]="2"
        result=mod.aggregate(self.reg,self.works,self.impact)
        self.assertEqual(result["conflicting_publication_identities"],1)
        self.assertEqual(result["overall"]["matched_source_included"],0)

    def test_duplicate_work_refused(self):
        with self.assertRaises(ValueError):mod.aggregate(self.reg,self.works,self.impact+[self.impact[0]])

    def test_duplicate_private_canonical_refused(self):
        with self.assertRaises(ValueError):
            mod.aggregate(self.reg,self.works+[{"openalex_id":"https://openalex.org/W12","doi":"10.1000/a","pmid":"1"}],self.impact+[{"openalex_id":"https://openalex.org/W12","fwci":"2","is_top_decile":"false"}])


if __name__=="__main__":unittest.main()
