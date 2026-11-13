# Copyright (c) 2026 CareOps contributors
# SPDX-License-Identifier: Apache-2.0
"""Immutable source-qualified planning-version reference: offline, read-only.

No person records, source authority, issued-document creation or native access
is asserted. This data type is a candidate projection of external records.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
import re


class VersionError(ValueError):
    """Malformed or ambiguous planning version snapshot."""


def _utc(value: datetime) -> bool:
    return (
        type(value) is datetime and value.tzinfo is not None
        and value.utcoffset().total_seconds() == 0
    )


@dataclass(frozen=True, slots=True)
class PlanVersion:
    plan_ref: str
    version_ref: str
    submitted_sha256: str
    policy_snapshot_ref: str
    appointment_ref: str
    position_ref: str
    service_assignment_ref: str
    effective_from: date
    effective_to: date | None
    issued_at: datetime | None
    decision_evidence_ref: str | None
    state: str

    def __post_init__(self) -> None:
        for field in (
            "plan_ref", "version_ref", "policy_snapshot_ref",
            "appointment_ref", "position_ref", "service_assignment_ref",
        ):
            val = getattr(self, field)
            if not isinstance(val, str) or not val.strip() or ":" not in val:
                raise VersionError(f"{field} needs a source-qualified reference")
        if not isinstance(self.submitted_sha256, str) or not re.fullmatch("[0-9a-f]{64}", self.submitted_sha256):
            raise VersionError("immutable submitted SHA-256 required")
        if type(self.effective_from) is not date or (
            self.effective_to is not None and (
                type(self.effective_to) is not date or self.effective_to <= self.effective_from
            )
        ):
            raise VersionError("invalid half-open effective interval")
        if self.state not in ("submitted", "issued", "superseded", "retired"):
            raise VersionError("unrecognised plan version state")
        if self.state in ("issued", "superseded", "retired") and (
            self.issued_at is None
            or not isinstance(self.decision_evidence_ref, str)
            or not self.decision_evidence_ref.strip()
        ):
            raise VersionError("issued history requires timestamp and external decision reference")
        if self.issued_at is not None and not _utc(self.issued_at):
            raise VersionError("issued time must be UTC")


def read_as_of(
    versions: list[PlanVersion], *, plan_ref: str, date_as_of: date,
    observed_at: datetime, source_read_complete: bool,
) -> dict[str, str | bool | None]:
    """Project candidate issued history; never imply approval or data completeness.

    A complete source read is independently qualified by its adapter. A
    caller-supplied True is not, by itself, evidence of such a read.
    """
    if not isinstance(versions, list) or any(not isinstance(version, PlanVersion) for version in versions):
        raise VersionError("version sequence required")
    if not isinstance(plan_ref, str) or not plan_ref.strip() or type(date_as_of) is not date or not _utc(observed_at):
        raise VersionError("source, business date and UTC observation required")
    if type(source_read_complete) is not bool:
        raise VersionError("source_read_complete must be explicitly boolean")
    if not source_read_complete:
        return {"status": "unverified_incomplete_source", "version_ref": None, "authority_verified": False}
    hits = [
        version for version in versions if (
            version.plan_ref == plan_ref
            and version.state in ("issued", "superseded", "retired")
            and version.effective_from <= date_as_of
            and (version.effective_to is None or date_as_of < version.effective_to)
            and version.issued_at is not None and version.issued_at <= observed_at
        )
    ]
    if len(hits) > 1:
        raise VersionError("ambiguous overlapping effective issued versions")
    if not hits:
        return {"status": "not_issued", "version_ref": None, "authority_verified": False}
    return {"status": "candidate_issued", "version_ref": hits[0].version_ref, "authority_verified": False}
