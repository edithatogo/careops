"""Synthetic non-premium person view checks: no directory inference."""
import importlib.util
from pathlib import Path
import unittest
file=Path(__file__).resolve().parents[1]/"rims_person_view.py"
spec=importlib.util.spec_from_file_location("rims_person_view",file)
view=importlib.util.module_from_spec(spec)
spec.loader.exec_module(view)

class PeopleTests(unittest.TestCase):
    def setUp(self):
        self.directory=[{"directory_account_id":"synthetic-entra-1","displayName":"Do not export"}]
        self.authors=[{"author_mention_id":"synthetic-mention-1","orcid":"0000-0000-0000-0000",
                       "affiliation_source_id":"synthetic-source"}]
        self.links=[{"person_id":"synthetic-person-1","directory_account_id":"synthetic-entra-1",
                     "author_mention_id":"synthetic-mention-1","link_evidence_hash":"synthetic"}]

    def test_no_auto_link(self):
        result=view.build_person_view(self.directory,self.authors,self.links)
        self.assertEqual(result["links"],[])
        self.assertEqual(result["unresolved"][0]["status"],"NeedsHumanReview")

    def test_explicit_verified_identity_not_employee(self):
        result=view.build_person_view(self.directory,self.authors,self.links,verify_link=lambda row: True)
        self.assertEqual(len(result["links"]),1)
        self.assertEqual(result["links"][0]["employment_status"],"Unverified")
        self.assertFalse(result["employment_authorised"])
        self.assertNotIn("Do not export",str(result))

    def test_duplicate_accounts_refused(self):
        with self.assertRaises(view.PersonViewError):
            view.build_person_view(self.directory+self.directory,self.authors,self.links)

    def test_bad_crosswalk_refused(self):
        with self.assertRaises(view.PersonViewError):
            view.build_person_view(self.directory,self.authors,[{**self.links[0],"directory_account_id":"missing"}])

if __name__=="__main__": unittest.main()
