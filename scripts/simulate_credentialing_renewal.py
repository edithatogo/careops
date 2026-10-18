"""Deterministic end-to-end simulator for the credentialing renewal MVP.

The simulator exercises source observation, human reconciliation, evidence and
service review, committee recommendation, separate delegated decision and
privacy-minimised process projection. It deliberately stops before any
production register, roster, access or release-to-practise write.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import TypedDict, cast

FORBIDDEN_KEYS = {
    "name",
    "email",
    "registrationnumber",
    "qualification",
    "credentialdocument",
    "refereereport",
    "decisionreason",
    "patientdata",
    "rawpayload",
}
HUMAN_ACTIVITIES = {
    "source-record-reconciled",
    "evidence-completeness-confirmed",
    "service-capability-confirmed",
    "committee-readiness-confirmed",
    "committee-recommendation-recorded",
    "delegated-decision-recorded",
}


class Event(TypedDict):
    """One synthetic process event."""

    event_id: str
    activity: str
    timestamp_utc: str
    source_system: str
    object_ids: dict[str, str]
    observed_or_inferred: str
    confidence: int
    human_act: bool
    actor_role: str
    qualifiers: dict[str, str | bool]


class SimulationResult(TypedDict):
    """Synthetic end-to-end simulation output."""

    contract_version: str
    ontology_version: str
    classification: str
    case_id: str
    terminal_state: str
    events: list[Event]
    production_writes: bool
    release_to_practise: bool
    evidence_ceiling: str


def normalise_key(value: object) -> str:
    """Normalise a key for privacy-boundary checks."""
    return "".join(character for character in str(value).lower() if character.isalnum())


def find_forbidden_key(value: object, path: str = "$") -> str | None:
    """Return the first prohibited case-level field."""
    if isinstance(value, dict):
        for key, child in cast("dict[object, object]", value).items():
            if normalise_key(key) in FORBIDDEN_KEYS:
                return f"{path}.{key}"
            nested = find_forbidden_key(child, f"{path}.{key}")
            if nested is not None:
                return nested
    elif isinstance(value, list):
        for index, child in enumerate(cast("list[object]", value)):
            nested = find_forbidden_key(child, f"{path}[{index}]")
            if nested is not None:
                return nested
    return None


def require(condition: bool, message: str) -> None:
    """Raise a bounded validation error when a precondition fails."""
    if not condition:
        raise ValueError(message)


def require_mapping(value: object, field: str) -> dict[str, object]:
    """Return a required JSON object."""
    if not isinstance(value, dict):
        raise TypeError(f"{field} must be a JSON object")
    return cast("dict[str, object]", value)


def parse_timestamp(value: object) -> datetime:
    """Parse an ISO timestamp and normalise it to UTC."""
    if not isinstance(value, str):
        raise TypeError("source.observedAt must be an ISO timestamp")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("source.observedAt must include a timezone")
    return parsed.astimezone(UTC)


def validate_case(data: dict[str, object]) -> None:
    """Validate the synthetic, human-governed case boundary."""
    forbidden = find_forbidden_key(data)
    require(forbidden is None, f"Prohibited case-level field: {forbidden}")
    require(
        data.get("classification") == "synthetic-non-production",
        "Only synthetic non-production cases may be simulated",
    )
    source = require_mapping(data.get("source"), "source")
    application = require_mapping(data.get("application"), "application")
    governance = require_mapping(data.get("governance"), "governance")
    automation = require_mapping(data.get("automation"), "automation")

    require(
        source.get("reconciliationStatus") == "confirmed-by-human",
        "Source observation requires human reconciliation",
    )
    require(bool(source.get("reviewerRole")), "Source reviewer role is required")
    require(
        application.get("pathway") == "routine-renewal",
        "The MVP simulator accepts routine renewal only",
    )
    require(
        application.get("evidenceComplete") is True,
        "Evidence completeness must be confirmed by a human",
    )
    require(
        application.get("currentAuthorityVerified") is True,
        "Current authority must be verified",
    )
    require(
        application.get("serviceCapabilityConfirmed") is True,
        "Service and facility capability must be confirmed",
    )
    for field in (
        "committeeReady",
        "quorumConfirmed",
        "conflictsDeclaredAndManaged",
        "relevantPeerInputComplete",
    ):
        require(governance.get(field) is True, f"Governance gate failed: {field}")
    require(
        governance.get("recommendation") == "recommend-approval",
        "Synthetic fixture must contain an explicit committee recommendation",
    )
    require(
        governance.get("delegatedDecision") == "approved",
        "Synthetic fixture must contain a separate delegated decision",
    )
    recommendation_role = governance.get("recommendationRole")
    decision_role = governance.get("decisionRole")
    require(bool(recommendation_role), "Recommendation role is required")
    require(bool(decision_role), "Decision role is required")
    require(
        recommendation_role != decision_role,
        "Recommendation and delegated-decision roles must remain separate",
    )
    require(
        automation.get("aiDecisionAttempted") is False,
        "AI cannot make or attempt the credentialing decision",
    )
    require(
        automation.get("productionWriteEnabled") is False,
        "Production writes must remain disabled",
    )
    require(
        automation.get("authoritativeRegisterWriteExpected") is False,
        "The MVP cannot write the authoritative register",
    )
    require(
        automation.get("releaseToPractiseExpected") is False,
        "The MVP cannot release a practitioner to practise",
    )


def create_event(
    *,
    number: int,
    activity: str,
    timestamp: datetime,
    source_system: str,
    case_id: str,
    application_id: str,
    human_act: bool,
    actor_role: str,
    qualifiers: dict[str, str | bool],
) -> Event:
    """Create one deterministic synthetic event."""
    return {
        "event_id": f"SYNTH-EVT-{number:03d}",
        "activity": activity,
        "timestamp_utc": timestamp.isoformat().replace("+00:00", "Z"),
        "source_system": source_system,
        "object_ids": {
            "case": case_id,
            "application": application_id,
        },
        "observed_or_inferred": "observed",
        "confidence": 1,
        "human_act": human_act,
        "actor_role": actor_role,
        "qualifiers": qualifiers,
    }


def simulate_case(data: dict[str, object]) -> SimulationResult:
    """Run the deterministic routine-renewal state sequence."""
    validate_case(data)
    source = require_mapping(data["source"], "source")
    application = require_mapping(data["application"], "application")
    governance = require_mapping(data["governance"], "governance")
    try:
        case_id = str(data["caseId"])
    except KeyError:
        raise ValueError("caseId is required")
    try:
        application_id = str(application["applicationId"])
    except KeyError:
        raise ValueError("application.applicationId is required")
    try:
        start = parse_timestamp(source["observedAt"])
    except KeyError:
        raise ValueError("source.observedAt is required")

    definitions = [
        (
            "source-record-observed",
            "careops-approve",
            False,
            "source-adapter",
            {"state": "imported-pending-reconciliation", "pathway": "routine-renewal"},
        ),
        (
            "source-record-reconciled",
            "careops-approve",
            True,
            str(source["reviewerRole"]),
            {"state": "confirmed-observation", "pathway": "routine-renewal"},
        ),
        (
            "application-loaded",
            "careops-approve",
            False,
            "workflow-service",
            {"state": "application-under-review", "pathway": "routine-renewal"},
        ),
        (
            "evidence-completeness-confirmed",
            "careops-approve",
            True,
            "credentialing-officer",
            {"state": "evidence-complete", "pathway": "routine-renewal"},
        ),
        (
            "service-capability-confirmed",
            "careops-decisions",
            True,
            "service-reviewer",
            {"state": "service-capability-confirmed", "pathway": "routine-renewal"},
        ),
        (
            "committee-readiness-confirmed",
            "careops-decisions",
            True,
            "committee-secretariat",
            {"state": "ready-for-committee", "pathway": "routine-renewal"},
        ),
        (
            "committee-recommendation-recorded",
            "careops-decisions",
            True,
            str(governance["recommendationRole"]),
            {"state": "recommendation-recorded", "recommendation": "recommend-approval"},
        ),
        (
            "delegated-decision-recorded",
            "careops-decisions",
            True,
            str(governance["decisionRole"]),
            {"state": "decision-recorded", "decision": "approved"},
        ),
        (
            "decision-result-reconciled",
            "careops-approve",
            False,
            "workflow-service",
            {"state": "decision-recorded-not-activated", "pathway": "routine-renewal"},
        ),
        (
            "process-assurance-projection-created",
            "careops-approve",
            False,
            "event-projection-service",
            {"state": "decision-recorded-not-activated", "privacy_minimised": True},
        ),
    ]
    events = [
        create_event(
            number=index,
            activity=activity,
            timestamp=start + timedelta(minutes=index - 1),
            source_system=source_system,
            case_id=case_id,
            application_id=application_id,
            human_act=human_act,
            actor_role=actor_role,
            qualifiers=qualifiers,
        )
        for index, (
            activity,
            source_system,
            human_act,
            actor_role,
            qualifiers,
        ) in enumerate(definitions, start=1)
    ]

    require(
        len({event["event_id"] for event in events}) == len(events),
        "Event identifiers must be unique",
    )
    require(
        [event["timestamp_utc"] for event in events]
        == sorted(event["timestamp_utc"] for event in events),
        "Event timestamps must be monotonic",
    )
    require(
        HUMAN_ACTIVITIES
        <= {event["activity"] for event in events if event["human_act"]},
        "Required human acts are missing",
    )
    return {
        "contract_version": "0.1.0",
        "ontology_version": "0.1.0",
        "classification": "synthetic-non-production",
        "case_id": case_id,
        "terminal_state": "decision-recorded-not-activated",
        "events": events,
        "production_writes": False,
        "release_to_practise": False,
        "evidence_ceiling": (
            "Synthetic state-sequence and interface evidence only. This is not a "
            "credentialing decision, policy approval, tenant deployment, source-system "
            "migration, register activation or operating-effectiveness finding."
        ),
    }


def load_case(path: Path) -> dict[str, object]:
    """Load one synthetic case fixture."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError("Synthetic case fixture must be a JSON object")
    return cast("dict[str, object]", value)


def parse_args() -> argparse.Namespace:
    """Parse the simulator command line."""
    parser = argparse.ArgumentParser()
    parser.add_argument("fixture", type=Path)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    """Run the simulation and write or print its receipt."""
    args = parse_args()
    result = simulate_case(load_case(args.fixture))
    payload = json.dumps(result, indent=2) + "\n"
    if args.output is None:
        print(payload, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
