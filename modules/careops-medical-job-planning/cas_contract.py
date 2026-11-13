# Copyright (c) 2026 CareOps contributors
# SPDX-License-Identifier: Apache-2.0
"""Deterministic *offline* candidate-submission CAS protocol.

A synthetic in-memory reference implementation for source-only development.
It is NOT a SharePoint client, delegated-authorisation service, durable database,
operational plan issuer, or employment-policy implementation. Native adapters
must independently qualify actor identity, item ACLs, ETags and retry semantics.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
import json
import re
from threading import RLock
from typing import Any
import unicodedata

MAX_SAFE_JSON_INT = (1 << 53) - 1
MAX_PAYLOAD_BYTES = 1024 * 1024
MAX_NESTING = 32
_QUALIFIED = re.compile(r"[a-z][a-z0-9_-]*:[A-Za-z0-9._/-]{1,200}\Z", re.ASCII)


class ProtocolError(ValueError):
    """Invalid source-only command or deterministic JSON payload."""


class OperationConflict(ProtocolError):
    """An idempotency identity was reused for different work."""


class StaleHead(ProtocolError):
    """Expected generation is not the current committed generation (412 analogue)."""


class InjectedCrash(RuntimeError):
    """Synthetic crash before or after the PlanHead CAS commit."""


def _strict_json(value: object, depth: int = 0) -> None:
    if depth > MAX_NESTING:
        raise ProtocolError("maximum payload depth exceeded")
    if value is None or type(value) is bool:
        return
    if type(value) is int:
        if abs(value) > MAX_SAFE_JSON_INT:
            raise ProtocolError("integer not safe for cross-runtime JSON")
        return
    if type(value) is str:
        if unicodedata.normalize("NFC", value) != value:
            raise ProtocolError("non-NFC string is ambiguous across runtimes")
        if "\x00" in value or any(0xD800 <= ord(char) <= 0xDFFF for char in value):
            raise ProtocolError("invalid string code point")
        return
    if type(value) is list:
        for item in value:
            _strict_json(item, depth + 1)
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str or not key:
                raise ProtocolError("JSON object must have nonempty string keys")
            _strict_json(key, depth + 1)
            _strict_json(item, depth + 1)
        return
    # Floats are intentionally forbidden, including NaN and +/-infinity.
    # Decimal quantities must be supplied as canonical decimal strings.
    raise ProtocolError("unsupported JSON scalar, including float/Decimal")


def canonical_bytes(payload: object) -> bytes:
    """Version-1 project canonicalisation, deliberately not claimed as RFC 8785."""
    if type(payload) is not dict:
        raise ProtocolError("candidate payload must be a JSON object")
    _strict_json(payload)
    try:
        result = json.dumps(
            payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError, UnicodeError) as exc:
        raise ProtocolError("payload could not be serialised") from exc
    if len(result) > MAX_PAYLOAD_BYTES:
        raise ProtocolError("payload too large")
    return result


def canonical_sha256(payload: object) -> str:
    return sha256(canonical_bytes(payload)).hexdigest()


def _qualified(value: object, name: str) -> str:
    if not isinstance(value, str) or _QUALIFIED.fullmatch(value) is None:
        raise ProtocolError(f"{name} must be a source-qualified identifier")
    return value


@dataclass(frozen=True, slots=True)
class SubmitCommand:
    """Untrusted candidate command; the operational boundary must authenticate it."""
    plan_ref: str
    version_ref: str
    operation_ref: str
    expected_generation: int
    actor_evidence_ref: str
    payload: dict[str, Any] = field(repr=False, compare=False)
    payload_bytes: bytes = field(init=False, repr=False)
    payload_sha256: str = field(init=False)
    fingerprint: str = field(init=False)

    def __post_init__(self) -> None:
        for field_name in ("plan_ref", "version_ref", "operation_ref", "actor_evidence_ref"):
            _qualified(getattr(self, field_name), field_name)
        if type(self.expected_generation) is not int or self.expected_generation < 0:
            raise ProtocolError("expected generation must be a nonnegative integer")
        raw = canonical_bytes(self.payload)
        digest = sha256(raw).hexdigest()
        immutable_identity = {
            "plan_ref": self.plan_ref,
            "version_ref": self.version_ref,
            "operation_ref": self.operation_ref,
            "expected_generation": self.expected_generation,
            "actor_evidence_ref": self.actor_evidence_ref,
            "payload_sha256": digest,
        }
        fingerprint = sha256(canonical_bytes(immutable_identity)).hexdigest()
        object.__setattr__(self, "payload_bytes", raw)
        object.__setattr__(self, "payload_sha256", digest)
        object.__setattr__(self, "fingerprint", fingerprint)


@dataclass(frozen=True, slots=True)
class CandidateHead:
    plan_ref: str
    candidate_version_ref: str
    payload_sha256: str
    generation: int
    etag: str
    last_operation_ref: str
    last_fingerprint: str
    state: str = "candidate_submitted"


@dataclass(frozen=True, slots=True)
class CandidateReceipt:
    plan_ref: str
    version_ref: str
    operation_ref: str
    payload_sha256: str
    generation: int
    etag: str
    outcome: str = "candidate_submitted"


class MemoryProtocolStore:
    """In-memory, lock-protected simulation; NOT crash-durable or permission-aware."""

    def __init__(self) -> None:
        self._guard = RLock()
        self._heads: dict[str, CandidateHead] = {}
        self._head_history: dict[str, list[CandidateHead]] = {}
        self._staged: dict[str, SubmitCommand] = {}
        self._artifacts: dict[str, bytes] = {}
        self._receipts: dict[str, CandidateReceipt] = {}

    def get_head(self, plan_ref: str) -> CandidateHead | None:
        with self._guard:
            return self._heads.get(plan_ref)

    @property
    def artifact_count(self) -> int:
        with self._guard:
            return len(self._artifacts)

    def get_artifact(self, digest: str) -> dict[str, Any]:
        with self._guard:
            # Deserialize anew; callers cannot mutate committed stored source.
            return json.loads(self._artifacts[digest])

    def _stage(self, cmd: SubmitCommand) -> CandidateReceipt | None:
        with self._guard:
            old = self._staged.get(cmd.operation_ref)
            if old is not None and old.fingerprint != cmd.fingerprint:
                raise OperationConflict("operation reference reused with altered content or actor")
            if old is None:
                self._staged[cmd.operation_ref] = cmd
                self._artifacts.setdefault(cmd.payload_sha256, cmd.payload_bytes)
            return self._receipts.get(cmd.operation_ref)

    def _conditional_commit(self, cmd: SubmitCommand) -> CandidateHead:
        with self._guard:
            existing = self._heads.get(cmd.plan_ref)
            if existing and existing.last_operation_ref == cmd.operation_ref:
                if existing.last_fingerprint != cmd.fingerprint:
                    raise OperationConflict("committed identity hash mismatch")
                return existing
            for prior in self._head_history.get(cmd.plan_ref, []):
                if prior.last_operation_ref == cmd.operation_ref:
                    if prior.last_fingerprint != cmd.fingerprint:
                        raise OperationConflict("historical operation identity mismatch")
                    return prior
            if (existing.generation if existing else 0) != cmd.expected_generation:
                raise StaleHead("conditional plan-head update refused: stale generation")
            # Memory lock models one atomic PlanHead CAS, not multi-list ACID.
            generation = cmd.expected_generation + 1
            result = CandidateHead(
                plan_ref=cmd.plan_ref,
                candidate_version_ref=cmd.version_ref,
                payload_sha256=cmd.payload_sha256,
                generation=generation, etag=f"v{generation}",
                last_operation_ref=cmd.operation_ref,
                last_fingerprint=cmd.fingerprint,
            )
            self._heads[cmd.plan_ref] = result
            self._head_history.setdefault(cmd.plan_ref, []).append(result)
            return result

    def _finalise(self, cmd: SubmitCommand, head: CandidateHead) -> CandidateReceipt:
        with self._guard:
            if (head.last_operation_ref != cmd.operation_ref or
                head.last_fingerprint != cmd.fingerprint or
                head.candidate_version_ref != cmd.version_ref or
                head.payload_sha256 != cmd.payload_sha256):
                raise OperationConflict("head and staged operation disagree")
            receipt = CandidateReceipt(
                plan_ref=cmd.plan_ref, version_ref=cmd.version_ref,
                operation_ref=cmd.operation_ref, payload_sha256=cmd.payload_sha256,
                generation=head.generation, etag=head.etag,
            )
            self._receipts[cmd.operation_ref] = receipt
            return receipt

    def reconcile(self, operation_ref: str) -> str:
        """Recover a post-CAS receipt; never auto-commit an uncommitted operation."""
        with self._guard:
            cmd = self._staged.get(operation_ref)
            if cmd is None:
                return "unknown_operation"
            if operation_ref in self._receipts:
                return "committed"
            history = self._head_history.get(cmd.plan_ref, [])
            matching = [head for head in history if head.last_operation_ref == operation_ref]
            if matching:
                self._finalise(cmd, matching[0])
                return "committed_recovered"
            head = self._heads.get(cmd.plan_ref)
            if head and head.generation > cmd.expected_generation:
                return "quarantined_conflict"
            return "prepared_not_committed"


def submit_candidate(
    store: MemoryProtocolStore, cmd: SubmitCommand, *, fail_after: str | None = None,
) -> CandidateReceipt:
    """Prepare -> compare-and-swap -> receipt; no human approval or M365 action."""
    if fail_after not in (None, "prepare", "commit"):
        raise ProtocolError("invalid fault-injection point")
    if not isinstance(store, MemoryProtocolStore) or not isinstance(cmd, SubmitCommand):
        raise ProtocolError("explicit validated store and command required")
    existing_receipt = store._stage(cmd)
    if existing_receipt is not None:
        return existing_receipt
    if fail_after == "prepare":
        raise InjectedCrash("after immutable stage, before head CAS")
    head = store._conditional_commit(cmd)
    if fail_after == "commit":
        raise InjectedCrash("after head CAS, before receipt")
    return store._finalise(cmd, head)
