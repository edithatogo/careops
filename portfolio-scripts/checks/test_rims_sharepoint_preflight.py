"""Fictional, offline standard-connector Lists mapping tests."""
import importlib.util
from pathlib import Path
import unittest

path=Path(__file__).resolve().parents[1]/"rims_sharepoint_preflight.py"
spec=importlib.util.spec_from_file_location("rims_sharepoint_preflight",path)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class MappingTests(unittest.TestCase):
    def setUp(self):
        names={
          "candidates":{"SourceKey","ReviewState","EvidenceHash","LatestDecisionID"},
          "people":{"PersonKey","EvidenceHash","ReviewState"},
          "decisions":{"DecisionID","AssertionType","SubjectID","Reviewer",
                       "DecidedUTC","Reason","CandidateHash","EvidenceHash","Supersedes"},
          "issues":{"IssueKey","Period","ReviewedSnapshotHash","IssueState"}}
        guids={k:f"00000000-0000-4000-8000-{i:012d}" for i,k in enumerate(names,1)}
        self.mapping={"schema":"careops-rims.site-bindings/1",
                      "connectors":["shared_sharepointonline"],
                      "tables":{k:{"list_guid":guids[k],"columns":{v:v for v in fields}}
                                for k,fields in names.items()}}
        self.inventory={"lists":[{"list_guid":guids[k],"internal_names":sorted(fields),
                                  "versioning_enabled":True,"restricted_readers":True}
                                 for k,fields in names.items()]}

    def test_existing_lists_accepted_without_mutation(self):
        result=m.reconcile(self.inventory,self.mapping)
        self.assertTrue(result["ready"])
        self.assertFalse(result["mutation_authorised"])

    def test_missing_field_detected(self):
        self.inventory["lists"][0]["internal_names"].remove("ReviewState")
        result=m.reconcile(self.inventory,self.mapping)
        self.assertFalse(result["ready"])
        self.assertEqual(result["findings"][0]["code"],"MISSING_COLUMN")

    def test_restricted_reader_required(self):
        self.inventory["lists"][1]["restricted_readers"]=False
        result=m.reconcile(self.inventory,self.mapping)
        self.assertFalse(result["ready"])

    def test_premium_connector_refused(self):
        self.mapping["connectors"].append("shared_commondataserviceforapps")
        with self.assertRaises(m.MappingError):
            m.reconcile(self.inventory,self.mapping)

    def test_duplicate_authoritative_list_refused(self):
        self.mapping["tables"]["people"]["list_guid"]=self.mapping["tables"]["candidates"]["list_guid"]
        with self.assertRaises(m.MappingError):
            m.reconcile(self.inventory,self.mapping)

if __name__=="__main__":
    unittest.main()
