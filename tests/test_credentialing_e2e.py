from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path
from typing import cast

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from simulate_credentialing_renewal import load_case, simulate_case  # noqa: E402

FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "credentialing-mvp"
    / "routine-renewal-complete.synthetic.json"
)


class CredentialingEndToEndTests(unittest.TestCase):
    """Validate the synthetic renewal state sequence and stop conditions."""

    def case(self) -> dict[str, object]:
        return load_case(FIXTURE)

    def test_complete_case_reaches_decision_without_activation(self) -> None:
        source_case = self.case()
        expected = cast("dict[str, object]", source_case["expected"])
        result = simulate_case(source_case)

        self.assertEqual(result["terminal_state"], expected["terminalState"])
        self.assertEqual(len(result["events"]), expected["eventCount"])
        self.assertFalse(result["production_writes"])
        self.assertFalse(result["release_to_practise"])
        self.assertIn("not a credentialing decision", result["evidence_ceiling"])

        activities = [event["activity"] for event in result["events"]]
        self.assertLess(
            activities.index("committee-recommendation-recorded"),
            activities.index("delegated-decision-recorded"),
        )
        self.assertLess(
            activities.index("delegated-decision-recorded"),
            activities.index("decision-result-reconciled"),
        )
        expected_human = set(cast("list[str]", expected["humanActs"]))
        observed_human = {
            event["activity"] for event in result["events"] if event["human_act"]
        }
        self.assertTrue(expected_human <= observed_human)

    def test_source_observation_must_be_reconciled_by_a_human(self) -> None:
        case = copy.deepcopy(self.case())
        source = cast("dict[str, object]", case["source"])
        source["reconciliationStatus"] = "pending-human-review"

        with self.assertRaisesRegex(ValueError, "human reconciliation"):
            simulate_case(case)

    def test_incomplete_evidence_stops_before_governance(self) -> None:
        case = copy.deepcopy(self.case())
        application = cast("dict[str, object]", case["application"])
        application["evidenceComplete"] = False

        with self.assertRaisesRegex(ValueError, "Evidence completeness"):
            simulate_case(case)

    def test_recommendation_and_decision_roles_remain_separate(self) -> None:
        case = copy.deepcopy(self.case())
        governance = cast("dict[str, object]", case["governance"])
        governance["decisionRole"] = governance["recommendationRole"]

        with self.assertRaisesRegex(ValueError, "roles must remain separate"):
            simulate_case(case)

    def test_ai_cannot_attempt_the_decision(self) -> None:
        case = copy.deepcopy(self.case())
        automation = cast("dict[str, object]", case["automation"])
        automation["aiDecisionAttempted"] = True

        with self.assertRaisesRegex(ValueError, "AI cannot"):
            simulate_case(case)

    def test_production_write_and_release_controls_fail_closed(self) -> None:
        for field in (
            "productionWriteEnabled",
            "authoritativeRegisterWriteExpected",
            "releaseToPractiseExpected",
        ):
            with self.subTest(field=field):
                case = copy.deepcopy(self.case())
                automation = cast("dict[str, object]", case["automation"])
                automation[field] = True
                with self.assertRaises(ValueError):
                    simulate_case(case)

    def test_case_level_identity_fields_are_rejected(self) -> None:
        case = copy.deepcopy(self.case())
        case["registrationNumber"] = "SYNTHETIC-BUT-PROHIBITED"

        with self.assertRaisesRegex(ValueError, "Prohibited case-level field"):
            simulate_case(case)

    def test_receipt_is_deterministic(self) -> None:
        first = json.dumps(simulate_case(self.case()), sort_keys=True)
        second = json.dumps(simulate_case(self.case()), sort_keys=True)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
