"""Fictional offline tests of the lossless assessment-history archive."""

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from ppg_assessment_history_archive import prepare_archive, restore_original

URL = "https://example.invalid/private-evidence/history-001.json"


class AssessmentHistoryArchiveTests(unittest.TestCase):
    def test_exact_preimage_and_non_history_fields_are_preserved(self):
        original_object = {
            "sources": [{"originalSHA256": "a" * 64, "edition": "7"}],
            "completedAssessment": {"findingKeys": ["x", "y"], "clinicalAcceptance": None},
            "assessmentReviewAddenda": [{"old": 1}, {"latest": "é"}],
            "relationshipInventoryReconciliations": [{"count": 3}, {"count": 4}],
            "unrelated": {"nested": [1, {"preserve": True}]},
        }
        original = json.dumps(original_object, ensure_ascii=False, indent=3) + "\n"
        plan = prepare_archive(original, URL)
        self.assertEqual(original.encode(), plan.archive_bytes)
        compacted = json.loads(plan.compacted_manifest)
        self.assertEqual(compacted["assessmentReviewAddenda"], [{"latest": "é"}])
        self.assertEqual(compacted["relationshipInventoryReconciliations"], [{"count": 4}])
        for field in ("sources", "completedAssessment", "unrelated"):
            self.assertEqual(compacted[field], original_object[field])
        self.assertEqual(restore_original(plan.compacted_manifest, plan.archive_bytes), original)
        self.assertEqual(plan, prepare_archive(original, URL))
        self.assertIsNone(prepare_archive(plan.compacted_manifest, URL))

    def test_prior_archive_references_chain_and_full_history_is_recoverable(self):
        first = '{"assessmentReviewAddenda":[1,2],"relationshipInventoryReconciliations":[3,4]}'
        p1 = prepare_archive(first, URL)
        intermediate = json.loads(p1.compacted_manifest)
        intermediate["assessmentReviewAddenda"].append({"new": True})
        second = json.dumps(intermediate, indent=2)
        p2 = prepare_archive(second, URL.replace("001", "002"))
        compacted = json.loads(p2.compacted_manifest)
        self.assertEqual(compacted["assessmentHistoryArchives"][0], p1.archive_reference)
        self.assertEqual(len(compacted["assessmentHistoryArchives"]), 2)
        recovered_second = restore_original(p2.compacted_manifest, p2.archive_bytes)
        self.assertEqual(recovered_second, second)
        self.assertEqual(restore_original(p1.compacted_manifest, p1.archive_bytes), first)

    def test_corrupt_archive_and_changed_unrelated_fields_are_refused(self):
        plan = prepare_archive('{"assessmentReviewAddenda":[1,2],"sources":["original"]}', URL)
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            restore_original(plan.compacted_manifest, plan.archive_bytes + b" ")
        changed = json.loads(plan.compacted_manifest)
        changed["sources"] = ["different"]
        with self.assertRaisesRegex(ValueError, "permitted change"):
            restore_original(json.dumps(changed), plan.archive_bytes)
        changed = json.loads(plan.compacted_manifest)
        changed["assessmentHistoryArchives"][-1]["arrays"]["assessmentReviewAddenda"]["count"] = 99
        with self.assertRaisesRegex(ValueError, "array metadata"):
            restore_original(json.dumps(changed), plan.archive_bytes)

    def test_non_history_values_and_latest_entry_keep_exact_tokens(self):
        original = ('{ "precise" : 0.123456789012345678901234567890, '
                    '"assessmentReviewAddenda" : [ {"old":1}, 1.00000000000000000001 ], '
                    '"sources" : [ { "escaped" : "\\u0041" } ] }')
        plan = prepare_archive(original, URL)
        self.assertIn('"precise" : 0.123456789012345678901234567890', plan.compacted_manifest)
        self.assertIn('[1.00000000000000000001]', plan.compacted_manifest)
        self.assertIn('"sources" : [ { "escaped" : "\\u0041" } ]', plan.compacted_manifest)
        self.assertEqual(restore_original(plan.compacted_manifest, plan.archive_bytes), original)

    def test_missing_empty_and_invalid_history(self):
        original = '{"assessmentReviewAddenda":[1,2],"completedAssessment":{"state":"done"}}'
        plan = prepare_archive(original, URL)
        compacted = json.loads(plan.compacted_manifest)
        self.assertNotIn("relationshipInventoryReconciliations", compacted)
        self.assertEqual(restore_original(plan.compacted_manifest, plan.archive_bytes), original)
        self.assertIsNone(prepare_archive('{"assessmentReviewAddenda":[],"relationshipInventoryReconciliations":[1]}', URL))
        for bad in ('{"assessmentReviewAddenda":{}}', '{"x":1,"x":2}', '{"x":NaN}'):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                prepare_archive(bad, URL)
        with self.assertRaises(ValueError):
            prepare_archive(original, "http://example.invalid/archive")


if __name__ == "__main__":
    unittest.main()
