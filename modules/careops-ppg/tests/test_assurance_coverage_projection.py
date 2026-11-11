# SPDX-License-Identifier: Apache-2.0
"""Read-only accreditation application coverage; fictional cases, no native writes."""
import copy
import json
from pathlib import Path
import unittest

from scripts.ppg_assurance_coverage import project_coverage


FIXTURE = Path("tests/fixtures/accreditation/second-example.json")


class AccreditationCoverageTests(unittest.TestCase):
    def setUp(self):
        self.graph = json.loads(FIXTURE.read_text())["graph"]

    def project(self, graph=None, **kwargs):
        kwargs.setdefault("as_of", "2026-11-11")
        return project_coverage(graph if graph is not None else self.graph,
                                "ctx1", "scope1", kinds=("action", "subclause", "quality-statement"),
                                **kwargs)

    def test_missing_assessment_and_unknown_applicability_not_compliant(self):
        original = copy.deepcopy(self.graph)
        result = self.project()
        rows = {x["RequirementKey"]: x for x in result["requirements"]}
        self.assertEqual(rows["fixture-clause"]["readiness"], "assessment-missing")
        self.assertEqual(rows["fixture-action"]["readiness"], "applicability-unresolved")
        self.assertEqual(rows["fixture:stroke-statement"]["readiness"], "applicability-unresolved")
        self.assertTrue(all(x["accreditationStatus"] is None for x in result["requirements"]))
        self.assertEqual(result["externalAccreditationDecision"], None)
        self.assertEqual(result["nativeWrites"], 0)
        self.assertFalse(result["sourceBytesVerified"])
        self.assertEqual(self.graph, original)

    def test_reviewed_policy_mapping_is_not_implementation_evidence(self):
        graph = copy.deepcopy(self.graph)
        row = graph["assessments"][0]
        row.update(applicability="applicable", outcome="unknown", humanDecisionRef="decision",
                   actorRef="person", decidedAt="2026-11-11T07:00:00+10:00",
                   rationale="Fictional assessment of applicability")
        result = self.project(graph)
        value = next(x for x in result["requirements"] if x["RequirementKey"] == "fixture-action")
        self.assertEqual(value["readiness"], "human-assessment-pending")
        self.assertEqual(value["mappingCoverage"], "proposed-only")
        self.assertIsNone(value["accreditationStatus"])

    def test_human_review_still_cannot_assign_external_rating(self):
        graph = copy.deepcopy(self.graph)
        a = graph["assessments"][0]
        a.update(applicability="applicable", outcome="human-recorded",
                 humanDecisionRef="decision", actorRef="person",
                 decidedAt="2026-11-11T07:00:00+10:00", rationale="Fictional review")
        for m in graph["mappings"]:
            if m["MappingKey"] in a["MappingKeys"]:
                m.update(reviewState="reviewed", decisionRef="review")
        value = next(x for x in self.project(graph)["requirements"]
                     if x["RequirementKey"] == "fixture-action")
        self.assertEqual(value["readiness"], "human-review-recorded")
        self.assertEqual(value["mappingCoverage"], "reviewed")
        self.assertIsNone(value["accreditationStatus"])

    def test_not_applicable_requires_human_record_and_is_not_met(self):
        graph = copy.deepcopy(self.graph)
        graph["assessments"][0].update(applicability="not-applicable", outcome="unknown",
            humanDecisionRef="decision", actorRef="person",
            decidedAt="2026-11-11T07:00:00+10:00", rationale="Fictional scoped decision")
        value = next(x for x in self.project(graph)["requirements"]
                     if x["RequirementKey"] == "fixture-action")
        self.assertEqual(value["readiness"], "not-applicable-recorded")
        self.assertIsNone(value["accreditationStatus"])

    def test_draft_framework_is_future_watch_not_current_obligation(self):
        graph = copy.deepcopy(self.graph)
        graph["frameworks"][0]["status"] = "draft"
        row = next(x for x in self.project(graph)["requirements"]
                   if x["RequirementKey"] == "fixture-action")
        self.assertEqual(row["readiness"], "nonoperative-edition")
        self.assertEqual(row["editionStatus"], "draft")

    def test_absent_scope_context_and_invalid_kinds_refuse(self):
        for context, scope, kinds in [
            ("missing", "scope1", ("action",)),
            ("ctx1", "scope2", ("action",)),
            ("ctx1", "scope1", ()),
            ("ctx1", "scope1", ("unknown-kind",)),
        ]:
            with self.subTest(context=context,scope=scope,kinds=kinds), self.assertRaises(ValueError):
                project_coverage(self.graph,context,scope,kinds=kinds,as_of="2026-11-11")

    def test_conflicting_same_scope_assessments_refuse(self):
        graph=copy.deepcopy(self.graph)
        duplicate=copy.deepcopy(graph["assessments"][0])
        duplicate["AssessmentKey"]="second-assessment"
        graph["assessments"].append(duplicate)
        with self.assertRaisesRegex(ValueError,"Duplicate assessment"):
            self.project(graph)

    def test_crosswalk_does_not_transfer_acceptance(self):
        graph=copy.deepcopy(self.graph)
        graph["crosswalks"]=[]
        result=self.project(graph)
        self.assertFalse(result["acceptanceTransferred"])
        self.assertIsNone(result["externalAccreditationDecision"])

    def test_result_is_deterministic_and_excludes_raw_evidence(self):
        a=self.project()
        b=self.project()
        self.assertEqual(a,b)
        self.assertNotIn("Fictional policy describes a practice",json.dumps(a))
        self.assertEqual(a["asOf"], "2026-11-11")

    def test_future_human_decision_does_not_count_as_at_review_date(self):
        graph = copy.deepcopy(self.graph)
        graph["assessments"][0].update(applicability="applicable", outcome="human-recorded",
                 humanDecisionRef="decision", actorRef="person",
                 decidedAt="2027-01-01T07:00:00+10:00", rationale="Fictional later decision")
        with self.assertRaisesRegex(ValueError, "after as_of"):
            self.project(graph)

    def test_cli_private_create_only_result(self):
        import os
        import subprocess
        import sys
        import tempfile
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "coverage.json"
            graph_file = Path(temp) / "graph.json"
            graph_file.write_text(json.dumps(self.graph))
            command = [sys.executable, "-m", "scripts.ppg_assurance_coverage",
                       "--graph", str(graph_file), "--context", "ctx1",
                       "--scope", "scope1", "--kind", "action",
                       "--as-of", "2026-11-11", "--output", str(output)]
            first = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            before = output.read_bytes()
            self.assertIsNone(json.loads(before)["externalAccreditationDecision"])
            if os.name == "posix":
                self.assertEqual(output.stat().st_mode & 0o777, 0o600)
            repeat = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(repeat.returncode, 0)
            self.assertEqual(before, output.read_bytes())

    def test_bad_dates_are_refused(self):
        with self.assertRaises(ValueError):
            self.project(as_of="tomorrow")


if __name__ == "__main__":
    unittest.main()
