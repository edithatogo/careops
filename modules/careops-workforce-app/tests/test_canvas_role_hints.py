"""Source-level safeguards for reviewable Canvas specifications.

These are not Power Apps Studio import or Power Fx execution tests.
"""
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"canvas"/"Src"
GENERATOR=ROOT/"tools"/"generate_source.py"

class CanvasRoleHintTests(unittest.TestCase):
    def test_navigation_roles_default_closed(self):
        home=(SRC/"Home.pa.yaml").read_text(encoding="utf-8")
        for formula in ("Coalesce(varCanViewOwnPlans,false)",
                        "Coalesce(varCanApprove,false)",
                        "Coalesce(varCanOperate,false)"):
            with self.subTest(formula=formula):
                self.assertIn(formula,home)

    def test_privileged_queue_and_operations_hide_without_projected_roles(self):
        self.assertIn("Visible: =Coalesce(varCanApprove,false)",
                      (SRC/"ApproverDashboard.pa.yaml").read_text())
        self.assertIn("Visible: =Coalesce(varCanOperate,false)",
                      (SRC/"OperatorDashboard.pa.yaml").read_text())

    def test_draft_button_never_claims_unsaved_data_persisted(self):
        editor=(SRC/"PlanEditor.pa.yaml").read_text()
        self.assertIn("Draft is not persisted:",editor)
        self.assertNotIn("Draft saved. Submission has not occurred.",editor)

    def test_generator_retains_safeguards_on_regeneration(self):
        src=GENERATOR.read_text()
        self.assertIn("Coalesce(varCanApprove,false)",src)
        self.assertIn("Draft is not persisted:",src)
        self.assertNotIn("Draft saved. Submission has not occurred.",src)

if __name__=="__main__":unittest.main()
