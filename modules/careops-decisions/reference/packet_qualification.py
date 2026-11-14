"""Standalone, synthetic packet qualification and authority-boundary reference.

This module qualifies an immutable packet envelope against the existing packet
validator and a trusted authority snapshot. It is not an authority register,
decision writer, authentication mechanism, or native deployment component.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from reference.governance_packet import GovernancePacket, validate_packet


_SHA256 = re.compile(r"^[a-f0-9]{64}$")


class AuthorityStatus(StrEnum):
    MISSING = "authority-missing"
    UNSUPPORTED_STATE = "authority-state-unsupported"
    MAPPING_MISMATCH = "authority-mapping-mismatch"
    SOURCE_UNVERIFIED = "authority-source-unverified"
    NOT_YET_EFFECTIVE = "authority-not-yet-effective"
    EXPIRED = "authority-expired"
    QUALIFIED = "authority-qualified"


class PacketStatus(StrEnum):
    QUALIFIED = "packet-qualified"
    INVALID_PACKET = "packet-invalid"
    MISSING_SOURCE = "packet-source-missing"
    UNSUPPORTED_CONTRACT = "packet-contract-unsupported"
    SOURCE_HASH_MISMATCH = "packet-source-hash-mismatch"
    AUTHORITY_HELD = "packet-authority-held"


@dataclass(frozen=True)
class AuthorityEvidence:
    """Host-resolved snapshot; caller-supplied UI values are not trusted evidence."""

    state: str
    authority_reference: str
    mapping_version: str
    source_sha256: str
    source_bytes: bytes
    effective_from: datetime
    effective_until: datetime


@dataclass(frozen=True)
class PacketQualification:
    status: PacketStatus
    authority_status: AuthorityStatus
    reason: str


def evaluate_authority_boundary(
    evidence: AuthorityEvidence | None,
    *,
    expected_mapping_version: str,
    now: datetime,
) -> AuthorityStatus:
    """Return qualified only for one exact, current, source-pinned authority state.

    Effective periods are half-open [effective_from, effective_until). This
    classification does not prove that the host authenticated the snapshot and
    does not grant permission to make or record a decision.
    """
    if not isinstance(expected_mapping_version, str) or not expected_mapping_version.strip():
        return AuthorityStatus.SOURCE_UNVERIFIED
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("now must be timezone-aware")
    if evidence is None:
        return AuthorityStatus.MISSING
    if not isinstance(evidence, AuthorityEvidence):
        return AuthorityStatus.UNSUPPORTED_STATE
    if not isinstance(evidence.state, str) or evidence.state != "qualified":
        return AuthorityStatus.UNSUPPORTED_STATE
    if evidence.mapping_version != expected_mapping_version:
        return AuthorityStatus.MAPPING_MISMATCH
    if (
        not isinstance(evidence.authority_reference, str)
        or not evidence.authority_reference.strip()
        or not isinstance(evidence.source_sha256, str)
        or not _SHA256.fullmatch(evidence.source_sha256)
        or not isinstance(evidence.source_bytes, bytes)
        or not evidence.source_bytes
        or hashlib.sha256(evidence.source_bytes).hexdigest() != evidence.source_sha256
        or not isinstance(evidence.effective_from, datetime)
        or not isinstance(evidence.effective_until, datetime)
    ):
        return AuthorityStatus.SOURCE_UNVERIFIED
    start, end = evidence.effective_from, evidence.effective_until
    if (
        start.tzinfo is None or start.utcoffset() is None
        or end.tzinfo is None or end.utcoffset() is None
        or end <= start
    ):
        return AuthorityStatus.SOURCE_UNVERIFIED
    if now < start:
        return AuthorityStatus.NOT_YET_EFFECTIVE
    if now >= end:
        return AuthorityStatus.EXPIRED
    return AuthorityStatus.QUALIFIED


def qualify_standalone_packet(
    packet: GovernancePacket,
    *,
    source_bytes: bytes,
    claimed_source_sha256: str,
    contract_version: str,
    expected_contract_version: str,
    authority: AuthorityEvidence | None,
    expected_authority_mapping_version: str,
    now: datetime,
) -> PacketQualification:
    """Qualify source integrity and authority boundary without Process or writes.

    The existing GovernancePacket validator remains the sole owner of agenda,
    minutes, decision and action link semantics. Optional Process integration is
    deliberately not an input to this standalone qualification.
    """
    try:
        validate_packet(packet)
    except (AttributeError, TypeError, ValueError):
        return PacketQualification(
            PacketStatus.INVALID_PACKET, AuthorityStatus.MISSING, "existing packet identity validation failed"
        )
    if not isinstance(source_bytes, bytes) or not source_bytes:
        return PacketQualification(
            PacketStatus.MISSING_SOURCE, AuthorityStatus.MISSING, "immutable source bytes are required"
        )
    if (
        not isinstance(contract_version, str)
        or not contract_version.strip()
        or not isinstance(expected_contract_version, str)
        or not expected_contract_version.strip()
        or contract_version != expected_contract_version
    ):
        return PacketQualification(
            PacketStatus.UNSUPPORTED_CONTRACT, AuthorityStatus.MISSING, "contract version is missing or unsupported"
        )
    actual_hash = hashlib.sha256(source_bytes).hexdigest()
    if (
        not isinstance(claimed_source_sha256, str)
        or not _SHA256.fullmatch(claimed_source_sha256)
        or claimed_source_sha256 != actual_hash
    ):
        return PacketQualification(
            PacketStatus.SOURCE_HASH_MISMATCH, AuthorityStatus.MISSING, "source bytes do not match the claimed SHA-256"
        )
    authority_status = evaluate_authority_boundary(
        authority,
        expected_mapping_version=expected_authority_mapping_version,
        now=now,
    )
    if authority_status is not AuthorityStatus.QUALIFIED:
        return PacketQualification(
            PacketStatus.AUTHORITY_HELD, authority_status, "authority evidence is not exactly qualified and current"
        )
    return PacketQualification(
        PacketStatus.QUALIFIED, authority_status, "source and authority snapshot qualified; no decision authority conferred"
    )
