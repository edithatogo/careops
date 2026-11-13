# Copyright (c) 2026 CareOps contributors
# SPDX-License-Identifier: Apache-2.0
"""Immutable candidate negotiation transcript; no approval or employment authority.

This is a source-only deterministic transition validator. A native provider
must resolve actor, role, provenance and tenant scope independently before
persisting the returned candidate. It deliberately lacks approved/issued states.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import json
import re


class NegotiationError(ValueError):
    """Conflicting or invalid synthetic workflow proposal."""


_ALLOWED = {
    "submitted": {"propose": "consulting", "withdraw": "withdrawn"},
    "consulting": {"counterpropose": "counterproposed", "record_disagreement": "disputed", "record_consensus": "agreement_recorded", "withdraw": "withdrawn"},
    "counterproposed": {"propose": "consulting", "record_disagreement": "disputed", "withdraw": "withdrawn"},
    "disputed": {"escalate": "escalated", "return_for_revision": "returned", "withdraw": "withdrawn"},
    "escalated": {"propose": "consulting", "return_for_revision": "returned"},
    "returned": {"propose": "consulting", "withdraw": "withdrawn"},
    "agreement_recorded": {"request_authorisation": "authority_pending", "return_for_revision": "returned"},
    "authority_pending": {"return_for_revision": "returned"},
    "withdrawn": {},
}


def _sha(value: str) -> bool:
    return isinstance(value, str) and re.fullmatch("[0-9a-f]{64}", value) is not None


@dataclass(frozen=True, slots=True)
class NegotiationEvent:
    operation_id: str
    kind: str
    actor_ref: str
    role_ref: str
    evidence_ref: str
    payload_sha256: str
    occurred_at: datetime

    def __post_init__(self) -> None:
        if self.kind not in {kind for changes in _ALLOWED.values() for kind in changes}:
            raise NegotiationError("unknown negotiation action")
        for field in ("operation_id", "actor_ref", "role_ref", "evidence_ref"):
            value = getattr(self, field)
            if not isinstance(value, str) or not value.strip():
                raise NegotiationError(f"missing {field}")
        if not _sha(self.payload_sha256):
            raise NegotiationError("payload SHA256 required")
        if (type(self.occurred_at) is not datetime or self.occurred_at.tzinfo is None
            or self.occurred_at.utcoffset().total_seconds() != 0):
            raise NegotiationError("timestamp must be UTC")

    def fingerprint(self) -> str:
        envelope = {
            "operation_id": self.operation_id, "kind": self.kind,
            "actor_ref": self.actor_ref, "role_ref": self.role_ref,
            "evidence_ref": self.evidence_ref, "payload_sha256": self.payload_sha256,
            "occurred_at": self.occurred_at.isoformat(),
        }
        return sha256(json.dumps(envelope, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@dataclass(frozen=True, slots=True)
class Thread:
    plan_key: str
    version_key: str
    submitted_sha256: str
    generation: int
    state: str
    events: tuple[NegotiationEvent, ...]

    def __post_init__(self) -> None:
        if not all(isinstance(key, str) and key.strip() for key in (self.plan_key, self.version_key)):
            raise NegotiationError("qualified plan and version keys required")
        if not _sha(self.submitted_sha256):
            raise NegotiationError("immutable submitted content SHA256 required")
        if type(self.generation) is not int or self.generation < 0:
            raise NegotiationError("invalid generation")
        if self.state not in _ALLOWED or not isinstance(self.events, tuple):
            raise NegotiationError("invalid negotiation state")
        if len(self.events) != self.generation:
            raise NegotiationError("event log/generation mismatch")
        seen: set[str] = set()
        replay_state = "submitted"
        previous_at: datetime | None = None
        for event in self.events:
            if not isinstance(event, NegotiationEvent) or event.operation_id in seen:
                raise NegotiationError("duplicate or malformed event history")
            seen.add(event.operation_id)
            if previous_at is not None and event.occurred_at < previous_at:
                raise NegotiationError("nonmonotonic negotiation history timestamp")
            next_state = _ALLOWED[replay_state].get(event.kind)
            if next_state is None:
                raise NegotiationError("illegal transition in supplied history")
            replay_state = next_state
            previous_at = event.occurred_at
        if replay_state != self.state:
            raise NegotiationError("reported state disagrees with immutable history")


def advance(thread: Thread, event: NegotiationEvent, expected_generation: int) -> Thread:
    """Validate a proposed transcript revision. Never mutates storage.

    Role references are UNTRUSTED data, not authentication. Real
    approve/issue/activate transitions belong to a separately qualified
    server-side workflow verifying current identity and delegation.
    """
    if not isinstance(thread, Thread) or not isinstance(event, NegotiationEvent):
        raise NegotiationError("typed transition required")
    for prior in thread.events:
        if prior.operation_id == event.operation_id:
            if prior.fingerprint() == event.fingerprint():
                return thread
            raise NegotiationError("operation key rebound")
    if type(expected_generation) is not int or thread.generation != expected_generation:
        raise NegotiationError("stale expected generation")
    new_state = _ALLOWED[thread.state].get(event.kind)
    if new_state is None:
        raise NegotiationError("transition disallowed; no automatic approval")
    return Thread(
        plan_key=thread.plan_key, version_key=thread.version_key,
        submitted_sha256=thread.submitted_sha256,
        generation=thread.generation + 1, state=new_state,
        events=thread.events + (event,),
    )
