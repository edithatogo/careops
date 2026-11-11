"""Synthetic Power BI source-binding migration safety tests."""
import importlib.util, unittest
from pathlib import Path

path=Path(__file__).resolve().parents[1]/"rims_powerbi_binding_audit.py"
spec=importlib.util.spec_from_file_location("rims_powerbi_binding_audit",path)
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)

class PowerBICodeTests(unittest.TestCase):
    def test_coded_field_remediation_proposal_only(self):
        sample="table Publication\n\tcolumn field_17\n\t\tdataType: string\n\t\tsourceColumn: field_17\n"
        result=p.propose_migration(sample,{"field_17":"ReviewStatus"},
                                   report_json={"query":{"field":"field_17"}},
                                   scorecard_json={"metric":"field_17"},
                                   rdl_text="<Report><DataSets>field_17</DataSets></Report>")
        self.assertEqual(result["model"]["candidate_aliases"][0]["desired_display"],"ReviewStatus")
        self.assertEqual(result["report_codes"],["field_17"])
        self.assertEqual(result["scorecard_codes"],["field_17"])
        self.assertEqual(result["paginated_codes"],["field_17"])
        self.assertFalse(result["apply"])

    def test_friendly_tmdl_is_not_renamed(self):
        tmdl="table Publication\n\tcolumn ReviewStatus\n\t\tdataType: string\n\t\tsourceColumn: ReviewStatus\n"
        result=p.audit_tmdl(tmdl,{"field_17":"ReviewStatus"})
        self.assertEqual(result["candidate_aliases"],[])
        self.assertEqual(result["renames_applied"],0)

    def test_malformed_rdl_refused(self):
        with self.assertRaises(p.BindingError):
            p.inspect_rdl_codes("<notclosed>")

if __name__=="__main__":unittest.main()
