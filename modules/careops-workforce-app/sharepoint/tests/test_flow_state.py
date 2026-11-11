import unittest
from datetime import datetime, timezone, timedelta
from flow_state import DecisionContext, WorkflowError, start_case, decide

NOW = datetime(2026, 11, 11, tzinfo=timezone.utc)


class WorkflowStateTests(unittest.TestCase):
    def setUp(self):
        self.case = start_case("case1", "version1", "sha256-test", "officer", "renal")

    def actor(self, role, name="reviewer", service="renal", delegate=False, expiry=NOW + timedelta(days=1)):
        return DecisionContext(name, role, service, expiry, "officer", delegate)

    def test_complete_four_gate_route_preserves_decision_history(self):
        case = self.case
        for i, role in enumerate(("clinical_director", "clinical_director", "medical_workforce", "approver")):
            case = decide(case, self.actor(role, delegate=i == 3), "approve", "op" + str(i), i, NOW)
        self.assertEqual(case["status"], "approved")
        self.assertEqual(case["generation"], 4)
        self.assertEqual([x["stage"] for x in case["decisions"]],
                         ["consultation", "clinical_review", "industrial_review", "delegated_approval"])
        self.assertEqual(self.case["decisions"], [])

    def test_return_and_reject_are_terminal_for_submitted_candidate(self):
        for action in ("return", "reject"):
            with self.subTest(action=action):
                case = decide(self.case, self.actor("clinical_director"), action, "op", 0, NOW)
                with self.assertRaises(WorkflowError):
                    decide(case, self.actor("clinical_director"), "approve", "op2", 1, NOW)

    def test_wrong_role_and_no_delegation_fail(self):
        with self.assertRaises(WorkflowError):
            decide(self.case, self.actor("approver", delegate=True), "approve", "op", 0, NOW)
        case = self.case
        for i, role in enumerate(("clinical_director", "clinical_director", "medical_workforce")):
            case = decide(case, self.actor(role), "approve", "op" + str(i), i, NOW)
        with self.assertRaises(WorkflowError):
            decide(case, self.actor("approver"), "approve", "op3", 3, NOW)

    def test_self_approval_expiry_service_and_stale_version_denied(self):
        actors = (self.actor("clinical_director", name="officer"),
                  self.actor("clinical_director", expiry=NOW-timedelta(seconds=1)),
                  self.actor("clinical_director", service="other"))
        for actor in actors:
            with self.assertRaises(WorkflowError):
                decide(self.case, actor, "approve", "op", 0, NOW)
        with self.assertRaises(WorkflowError):
            decide(self.case, self.actor("clinical_director"), "approve", "op", 3, NOW)

    def test_untrusted_naive_clock_denied(self):
        with self.assertRaises(WorkflowError):
            decide(self.case, self.actor("clinical_director"), "approve", "op", 0, datetime(2026,11,11))

    def test_same_operation_cannot_be_replayed_as_new_decision(self):
        case = decide(self.case, self.actor("clinical_director"), "approve", "op", 0, NOW)
        with self.assertRaises(WorkflowError):
            decide(case, self.actor("clinical_director"), "approve", "op", 1, NOW)

if __name__ == "__main__":
    unittest.main()
