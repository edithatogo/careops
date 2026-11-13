# Copyright (c) 2026 CareOps contributors
# SPDX-License-Identifier: Apache-2.0
"""Independent, synthetic-only medical job planning domain validation.

This source slice does NOT evaluate an industrial entitlement, approve a plan,
write SharePoint, or establish CHHHS policy. Session input validation is strict:
Python truthiness and implicit numeric coercion are forbidden.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any


class DomainError(ValueError):
    """Malformed synthetic job-plan input."""


@dataclass(frozen=True, slots=True)
class Activity:
    week: int
    day: int
    start_min: int
    end_min: int
    code: str
    site: str
    ordinary: bool = True
    cst: bool = False


def activities_from_sessions(sessions: object) -> list[Activity]:
    """Read strictly typed sessions without bool(str) or int/float coercion."""
    if not isinstance(sessions, list):
        raise DomainError("sessions must be a list")
    keys = frozenset(("week", "day", "start_min", "end_min", "code", "site", "ordinary", "cst"))
    parsed: list[Activity] = []
    for position, raw in enumerate(sessions):
        if not isinstance(raw, dict):
            raise DomainError(f"session {position} must be an object")
        if set(raw) - keys:
            raise DomainError("session contains unknown fields")
        for name in ("week", "day", "start_min", "end_min"):
            if name not in raw:
                raise DomainError(f"session missing {name}")
            if type(raw[name]) is not int:
                raise DomainError(f"session {name} must be an integer")
        for name in ("code", "site"):
            if name not in raw:
                raise DomainError(f"session missing {name}")
            if not isinstance(raw[name], str) or not raw[name].strip():
                raise DomainError(f"session {name} must be a non-empty string")
        for name in ("ordinary", "cst"):
            if name in raw and type(raw[name]) is not bool:
                raise DomainError(f"session {name} must be a boolean")
        parsed.append(Activity(
            week=raw["week"],
            day=raw["day"],
            start_min=raw["start_min"],
            end_min=raw["end_min"],
            code=raw["code"],
            site=raw["site"],
            ordinary=raw.get("ordinary", True),
            cst=raw.get("cst", False),
        ))
    return parsed


def validate_cycle(activities: list[Activity], weeks: int) -> None:
    """Reject invalid intervals, overlapping sessions and misclassified CST."""
    if type(weeks) is not int or not 1 <= weeks <= 26:
        raise DomainError("invalid cycle length")
    by_day: dict[tuple[int, int], list[tuple[int, int]]] = {}
    for activity in activities:
        for name in ("week", "day", "start_min", "end_min"):
            if type(getattr(activity, name)) is not int:
                raise DomainError(f"activity {name} must be an integer")
        if type(activity.ordinary) is not bool or type(activity.cst) is not bool:
            raise DomainError("activity flags must be booleans")
        if not 1 <= activity.week <= weeks or not 1 <= activity.day <= 7:
            raise DomainError("activity outside cycle")
        if not 0 <= activity.start_min < activity.end_min <= 1440:
            raise DomainError("invalid activity interval")
        if any(not isinstance(item, str) or not item.strip() for item in (activity.code, activity.site)):
            raise DomainError("missing activity code or site")
        if activity.cst and not activity.ordinary:
            raise DomainError("CST cannot be classified as non-ordinary in this synthetic model")
        by_day.setdefault((activity.week, activity.day), []).append(
            (activity.start_min, activity.end_min)
        )
    for spans in by_day.values():
        ordered = sorted(spans)
        if any(left[1] > right[0] for left, right in zip(ordered, ordered[1:])):
            raise DomainError("overlapping activities")


def _hours(value: object, label: str) -> Decimal:
    """Validate calculation inputs without silent boolean or non-finite coercion."""
    if type(value) is bool or not isinstance(value, (str, int, Decimal)):
        raise DomainError(f"{label} must be a decimal string, integer or Decimal")
    try:
        number = Decimal(str(value))
    except InvalidOperation as exc:
        raise DomainError(f"invalid {label}") from exc
    if not number.is_finite():
        raise DomainError(f"non-finite {label}")
    return number


def reconcile_reference_only(
    sessions: object,
    cycle_weeks: int,
    contracted_fortnight_hours: object,
    candidate_cst_fraction: object,
) -> dict[str, str | bool]:
    """Report synthetic arithmetic only; never assert policy compliance.

    A candidate fraction is an unadopted assumption. No assessment of a
    medical officer's contractual or industrial entitlement is made.
    """
    activities = activities_from_sessions(sessions)
    validate_cycle(activities, cycle_weeks)
    contracted = _hours(contracted_fortnight_hours, "contracted_fortnight_hours")
    fraction = _hours(candidate_cst_fraction, "candidate_cst_fraction")
    if contracted <= 0 or not Decimal("0") <= fraction <= Decimal("1"):
        raise DomainError("invalid synthetic contract or fraction")
    expected = contracted * Decimal(cycle_weeks) / Decimal(2)
    ordinary = sum(
        (Decimal(a.end_min - a.start_min) / 60 for a in activities if a.ordinary),
        Decimal(0),
    )
    cst = sum(
        (Decimal(a.end_min - a.start_min) / 60 for a in activities if a.cst),
        Decimal(0),
    )
    candidate = expected * fraction
    return {
        "planned_ordinary_hours": str(ordinary),
        "reference_cycle_hours": str(expected),
        "planned_cst_hours": str(cst),
        "candidate_cst_hours": str(candidate),
        "ordinary_variance_hours": str(ordinary - expected),
        "candidate_cst_gap_hours": str(max(Decimal(0), candidate - cst)),
        "ordinary_balanced": ordinary == expected,
        "policy_status": "reference_only_unadopted",
    }
