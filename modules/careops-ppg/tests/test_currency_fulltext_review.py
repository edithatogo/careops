import unittest

from scripts.ppg_currency_fulltext_review import build_review, text_hash


class FullTextReviewTests(unittest.TestCase):
    def setUp(self):
        self.lead = {"Id": 1, "GUID": "fictional-lead", "CurrencyMatch": "Unresolved"}
        self.notice = self.body(id=1, leadGUID="fictional-lead", text="The fictional amber pump has a battery defect.")
        self.policy = self.body(uid="policy-a", id=2, title="Pump procedure", owner="Pump owner",
                                text="Inspect the amber pump battery before use.",
                                identityBasis="Verified fictional document identifier")
        self.selection = {"leadId": 1, "policyUID": "policy-a", "policySHA256": "a" * 64,
                          "noticeTextSHA256": self.notice["textSHA256"],
                          "noticeAnchor": "amber pump", "policyAnchor": "amber pump",
                          "reason": "Same equipment; applicability needs review"}

    @staticmethod
    def body(**values):
        return dict(state="retrieved", fullText=True, captureSHA256="a" * 64, scope="all pages",
                    textSHA256=text_hash(values["text"]), **values)

    def run_review(self):
        return build_review([self.lead], [self.notice], [self.policy], [self.selection])

    def test_two_sided_match_remains_candidate(self):
        result = self.run_review()
        self.assertEqual(result["newCandidates"], 1)
        self.assertEqual(result["rows"][0]["outcome"], "Candidate — review")
        self.assertNotIn("CurrencyDisposition", result["rows"][0])

    def test_changed_or_summary_body_rejected(self):
        for change in ({"text": "changed"}, {"fullText": False}, {"state": "blocked"}):
            with self.subTest(change=change):
                original = self.notice.copy()
                self.notice.update(change)
                with self.assertRaises(ValueError):
                    self.run_review()
                self.notice = original

    def test_missing_policy_anchor_rejected(self):
        self.selection["policyAnchor"] = "other equipment"
        with self.assertRaises(ValueError):
            self.run_review()

    def test_changed_notice_identity_or_review_pin_rejected(self):
        for field in ("leadGUID", "textSHA256"):
            with self.subTest(field=field):
                original = self.notice.copy()
                self.notice[field] = "different"
                with self.assertRaises(ValueError):
                    self.run_review()
                self.notice = original

    def test_unknown_selection_references_are_controlled_errors(self):
        for missing in ("lead", "notice", "policy"):
            with self.subTest(missing=missing):
                with self.assertRaises(ValueError):
                    build_review([] if missing == "lead" else [self.lead],
                                 [] if missing == "notice" else [self.notice],
                                 [] if missing == "policy" else [self.policy],
                                 [self.selection])

    def test_disposition_and_existing_candidates_preserved(self):
        for change in ({"CurrencyDisposition": "No impact"}, {"CurrencyMatch": "Candidate — review"}):
            with self.subTest(change=change):
                original = self.lead.copy()
                self.lead.update(change)
                with self.assertRaises(ValueError):
                    self.run_review()
                self.lead = original

    def test_blocked_source_and_missing_policy_stay_unresolved(self):
        result = build_review([self.lead], [{"id": 1, "leadGUID": "fictional-lead", "state": "blocked", "blocker": "Denied"}], [], [])
        self.assertEqual(result["rows"][0]["outcome"], "Unresolved")
        self.assertEqual(result["rows"][0]["noticeBlocker"], "Denied")

    def test_unmatched_notice_identity_is_checked(self):
        self.notice["leadGUID"] = "other-lead"
        with self.assertRaises(ValueError):
            build_review([self.lead], [self.notice], [self.policy], [])

    def test_unselected_policy_coverage_requires_qualified_body(self):
        for change in ({"state": "blocked"}, {"fullText": False}, {"identityBasis": ""}):
            with self.subTest(change=change):
                policy = {**self.policy, **change}
                result = build_review([self.lead], [self.notice], [policy], [])
                self.assertEqual(result["rows"][0]["policyIdentitiesAvailable"], 0)
        self.policy["text"] = "corrupt unselected body"
        with self.assertRaises(ValueError):
            build_review([self.lead], [self.notice], [self.policy], [])


if __name__ == "__main__":
    unittest.main()
