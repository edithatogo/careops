"""Deterministic capacity and benefits model for credentialing workflows.

The model uses synthetic or approved aggregate inputs only. It distinguishes
released staff capacity from cash savings and does not infer workforce
reductions from time released by automation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Final, TypedDict, cast

MODEL_VERSION: Final = "0.1.0"
MINUTES_PER_HOUR: Final = Decimal(60)
MONTHS_PER_YEAR: Final = Decimal(12)
PROHIBITED_KEYS: Final = {
    "name",
    "email",
    "registrationnumber",
    "patientdata",
    "credentialdocument",
    "refereereport",
    "decisionreason",
}


class RoleMinutes(TypedDict):
    """Minutes used by one staff role for a pathway."""

    role_id: str
    current_minutes_per_case: str
    future_minutes_per_case: str


class PathwayInput(TypedDict):
    """Aggregate activity and rework assumptions for a pathway."""

    pathway_id: str
    annual_cases: int
    role_minutes: list[RoleMinutes]
    current_rework_rate: str
    future_rework_rate: str
    current_rework_minutes: str
    future_rework_minutes: str


class RoleCost(TypedDict):
    """Loaded hourly cost and planned use of released capacity."""

    role_id: str
    loaded_hourly_cost: str
    capacity_use: str


class QualityGuardrail(TypedDict):
    """Required quality or burden measure for implementation evaluation."""

    measure_id: str
    direction: str
    baseline_required: bool
    pilot_required: bool


class ModelInput(TypedDict):
    """Complete model input contract."""

    schema_version: int
    model_version: str
    classification: str
    scenario_id: str
    pathways: list[PathwayInput]
    role_costs: list[RoleCost]
    implementation_cost: str
    annual_operating_cost: str
    realisation_fraction: str
    productive_hours_per_fte: str
    quality_guardrails: list[QualityGuardrail]


@dataclass(frozen=True)
class RoleResult:
    """Capacity result for one role."""

    role_id: str
    annual_hours_released: Decimal
    annual_capacity_value: Decimal
    fte_capacity_equivalent: Decimal
    capacity_use: str


@dataclass(frozen=True)
class ModelResult:
    """Aggregate model output."""

    scenario_id: str
    role_results: tuple[RoleResult, ...]
    gross_capacity_value: Decimal
    realised_capacity_value: Decimal
    annual_operating_cost: Decimal
    net_annual_capacity_value: Decimal
    implementation_cost: Decimal
    payback_months: Decimal | None
    evidence_ceiling: str


def decimal_value(value: object, field: str) -> Decimal:
    """Parse a finite non-negative decimal value."""
    try:
        result = Decimal(str(value))
    except Exception as error:  # noqa: BLE001 - converted to a bounded error
        message = f"Invalid decimal for {field}"
        raise ValueError(message) from error
    if not result.is_finite() or result < 0:
        message = f"{field} must be finite and non-negative"
        raise ValueError(message)
    return result


def bounded_fraction(value: object, field: str) -> Decimal:
    """Parse a fraction in the inclusive range zero to one."""
    result = decimal_value(value, field)
    if result > 1:
        message = f"{field} must be between zero and one"
        raise ValueError(message)
    return result


def normalise_key(value: object) -> str:
    """Normalise a key for privacy-boundary checks."""
    return "".join(character for character in str(value).lower() if character.isalnum())


def find_prohibited_key(value: object, path: str = "$") -> str | None:
    """Return the first prohibited case-level key in a nested input."""
    if isinstance(value, dict):
        for key, child in cast("dict[object, object]", value).items():
            if normalise_key(key) in PROHIBITED_KEYS:
                return f"{path}.{key}"
            nested = find_prohibited_key(child, f"{path}.{key}")
            if nested is not None:
                return nested
    elif isinstance(value, list):
        for index, child in enumerate(cast("list[object]", value)):
            nested = find_prohibited_key(child, f"{path}[{index}]")
            if nested is not None:
                return nested
    return None


def validate_input(data: dict[str, object]) -> ModelInput:
    """Validate the aggregate, non-production input boundary."""
    prohibited = find_prohibited_key(data)
    if prohibited is not None:
        message = f"Case-level or prohibited field is not allowed: {prohibited}"
        raise ValueError(message)
    if data.get("schema_version") != 1 or data.get("model_version") != MODEL_VERSION:
        message = "Unsupported credentialing capacity model version"
        raise ValueError(message)
    if data.get("classification") not in {
        "synthetic-non-production",
        "approved-aggregate",
    }:
        message = "Only synthetic or approved aggregate inputs are allowed"
        raise ValueError(message)

    typed = cast("ModelInput", data)
    if not typed.get("pathways") or not typed.get("role_costs"):
        message = "At least one pathway and role cost are required"
        raise ValueError(message)
    guardrail_ids = {
        guardrail["measure_id"] for guardrail in typed.get("quality_guardrails", [])
    }
    required_guardrails = {
        "first-pass-completeness",
        "expiry-or-unauthorised-practice-exceptions",
        "false-alert-rate",
        "staff-burden",
        "practitioner-experience",
    }
    if not required_guardrails <= guardrail_ids:
        message = "Required quality and burden guardrails are incomplete"
        raise ValueError(message)
    if any(
        not guardrail.get("baseline_required")
        or not guardrail.get("pilot_required")
        for guardrail in typed["quality_guardrails"]
    ):
        message = "Every guardrail requires baseline and pilot measurement"
        raise ValueError(message)

    role_ids = {role["role_id"] for role in typed["role_costs"]}
    if len(role_ids) != len(typed["role_costs"]):
        message = "Role identifiers must be unique"
        raise ValueError(message)
    if any(not role["capacity_use"].strip() for role in typed["role_costs"]):
        message = "Every role requires a planned use of released capacity"
        raise ValueError(message)
    for pathway in typed["pathways"]:
        if pathway["annual_cases"] < 0:
            message = "Annual case counts must be non-negative"
            raise ValueError(message)
        pathway_role_ids = {entry["role_id"] for entry in pathway["role_minutes"]}
        if not pathway_role_ids <= role_ids:
            message = f"Pathway {pathway['pathway_id']} references an unknown role"
            raise ValueError(message)
        bounded_fraction(pathway["current_rework_rate"], "current_rework_rate")
        bounded_fraction(pathway["future_rework_rate"], "future_rework_rate")
    bounded_fraction(typed["realisation_fraction"], "realisation_fraction")
    productive_hours = decimal_value(
        typed["productive_hours_per_fte"],
        "productive_hours_per_fte",
    )
    if productive_hours == 0:
        message = "productive_hours_per_fte must be greater than zero"
        raise ValueError(message)
    return typed


def quantise(value: Decimal, places: str = "0.01") -> Decimal:
    """Round a decimal deterministically for reporting."""
    return value.quantize(Decimal(places), rounding=ROUND_HALF_UP)


def model_capacity(data: dict[str, object]) -> ModelResult:
    """Calculate released capacity and capacity-equivalent value."""
    inputs = validate_input(data)
    role_costs = {
        role["role_id"]: decimal_value(
            role["loaded_hourly_cost"],
            f"loaded_hourly_cost:{role['role_id']}",
        )
        for role in inputs["role_costs"]
    }
    capacity_uses = {
        role["role_id"]: role["capacity_use"] for role in inputs["role_costs"]
    }
    minutes_released = {role_id: Decimal(0) for role_id in role_costs}

    for pathway in inputs["pathways"]:
        cases = Decimal(pathway["annual_cases"])
        current_rework = bounded_fraction(
            pathway["current_rework_rate"],
            "current_rework_rate",
        ) * decimal_value(pathway["current_rework_minutes"], "current_rework_minutes")
        future_rework = bounded_fraction(
            pathway["future_rework_rate"],
            "future_rework_rate",
        ) * decimal_value(pathway["future_rework_minutes"], "future_rework_minutes")
        rework_delta = current_rework - future_rework
        for entry in pathway["role_minutes"]:
            current = decimal_value(
                entry["current_minutes_per_case"],
                "current_minutes_per_case",
            )
            future = decimal_value(
                entry["future_minutes_per_case"],
                "future_minutes_per_case",
            )
            minutes_released[entry["role_id"]] += cases * (
                current - future + rework_delta
            )

    productive_hours = decimal_value(
        inputs["productive_hours_per_fte"],
        "productive_hours_per_fte",
    )
    results: list[RoleResult] = []
    for role_id in sorted(minutes_released):
        hours = minutes_released[role_id] / MINUTES_PER_HOUR
        value = hours * role_costs[role_id]
        results.append(
            RoleResult(
                role_id=role_id,
                annual_hours_released=quantise(hours),
                annual_capacity_value=quantise(value),
                fte_capacity_equivalent=quantise(hours / productive_hours, "0.001"),
                capacity_use=capacity_uses[role_id],
            )
        )

    gross_value = sum(
        (result.annual_capacity_value for result in results),
        start=Decimal(0),
    )
    realisation = bounded_fraction(
        inputs["realisation_fraction"],
        "realisation_fraction",
    )
    realised_value = gross_value * realisation
    operating_cost = decimal_value(inputs["annual_operating_cost"], "annual_operating_cost")
    implementation_cost = decimal_value(inputs["implementation_cost"], "implementation_cost")
    net_value = realised_value - operating_cost
    payback = (
        implementation_cost / net_value * MONTHS_PER_YEAR
        if net_value > 0
        else None
    )
    return ModelResult(
        scenario_id=inputs["scenario_id"],
        role_results=tuple(results),
        gross_capacity_value=quantise(gross_value),
        realised_capacity_value=quantise(realised_value),
        annual_operating_cost=quantise(operating_cost),
        net_annual_capacity_value=quantise(net_value),
        implementation_cost=quantise(implementation_cost),
        payback_months=quantise(payback) if payback is not None else None,
        evidence_ceiling=(
            "Modelled capacity-equivalent value from aggregate assumptions. It is not a "
            "cash saving, workforce reduction, policy approval, deployment result or "
            "operating-effectiveness finding."
        ),
    )


def result_to_dict(result: ModelResult) -> dict[str, Any]:
    """Convert a result to a JSON-serialisable reporting structure."""
    return {
        "model_version": MODEL_VERSION,
        "scenario_id": result.scenario_id,
        "roles": [
            {
                "role_id": item.role_id,
                "annual_hours_released": str(item.annual_hours_released),
                "annual_capacity_value": str(item.annual_capacity_value),
                "fte_capacity_equivalent": str(item.fte_capacity_equivalent),
                "capacity_use": item.capacity_use,
            }
            for item in result.role_results
        ],
        "gross_capacity_value": str(result.gross_capacity_value),
        "realised_capacity_value": str(result.realised_capacity_value),
        "annual_operating_cost": str(result.annual_operating_cost),
        "net_annual_capacity_value": str(result.net_annual_capacity_value),
        "implementation_cost": str(result.implementation_cost),
        "payback_months": (
            str(result.payback_months) if result.payback_months is not None else None
        ),
        "evidence_ceiling": result.evidence_ceiling,
    }


def load_and_model(path: Path) -> dict[str, Any]:
    """Load one JSON input and return its deterministic result."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        message = "Model input must be a JSON object"
        raise TypeError(message)
    return result_to_dict(model_capacity(cast("dict[str, object]", value)))
