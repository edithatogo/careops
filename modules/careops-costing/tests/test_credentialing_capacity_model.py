from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import cast

import unittest

from credentialing.credentialing_capacity_model import model_capacity, result_to_dict

FIXTURE = (
    Path(__file__).parents[1]
    / "credentialing"
    / "fixtures"
    / "routine-renewal-base.synthetic.json"
)


def load_fixture() -> dict[str, object]:
    value = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return cast("dict[str, object]", value)


class CredentialingCapacityModel(unittest.TestCase):
    def test_base_scenario_is_deterministic_and_capacity_only(self) -> None:
        result = result_to_dict(model_capacity(load_fixture()))

        assert result["scenario_id"] == "routine-renewal-base"
        assert result["gross_capacity_value"] == "27000.00"
        assert result["realised_capacity_value"] == "21600.00"
        assert result["net_annual_capacity_value"] == "15600.00"
        assert result["payback_months"] == "23.08"
        assert result["roles"] == [
            {
                "role_id": "clinical-reviewer",
                "annual_hours_released": "90.00",
                "annual_capacity_value": "12600.00",
                "fte_capacity_equivalent": "0.060",
                "capacity_use": (
                    "Relevant-peer judgement, supervision and service-capability review"
                ),
            },
            {
                "role_id": "credentialing-officer",
                "annual_hours_released": "240.00",
                "annual_capacity_value": "14400.00",
                "fte_capacity_equivalent": "0.160",
                "capacity_use": (
                    "Complex-case support, evidence quality and exception resolution"
                ),
            },
        ]
        assert "not a cash saving" in cast("str", result["evidence_ceiling"])


    def test_production_case_level_input_fails_closed(self) -> None:
        data = copy.deepcopy(load_fixture())
        data["classification"] = "production"
        data["registrationNumber"] = "MED0000000000"

        with self.assertRaisesRegex(ValueError, "prohibited field"):
            model_capacity(data)


    def test_missing_quality_guardrail_is_rejected(self) -> None:
        data = copy.deepcopy(load_fixture())
        guardrails = cast("list[dict[str, object]]", data["quality_guardrails"])
        data["quality_guardrails"] = [
            item for item in guardrails if item["measure_id"] != "false-alert-rate"
        ]

        with self.assertRaisesRegex(ValueError, "guardrails are incomplete"):
            model_capacity(data)


    def test_capacity_use_plan_is_required(self) -> None:
        data = copy.deepcopy(load_fixture())
        roles = cast("list[dict[str, object]]", data["role_costs"])
        roles[0]["capacity_use"] = ""

        with self.assertRaisesRegex(ValueError, "planned use of released capacity"):
            model_capacity(data)


    def test_non_positive_net_value_has_no_payback_claim(self) -> None:
        data = copy.deepcopy(load_fixture())
        data["annual_operating_cost"] = "50000"

        result = model_capacity(data)
        assert result.net_annual_capacity_value < 0
        assert result.payback_months is None
