# SPDX-License-Identifier: Apache-2.0
"""Pure, synthetic-only workflow transition contract for Power Automate adaptation.

No authority is inferred from a Power Apps supplied role. An authorised server
must resolve identity and delegation before constructing DecisionContext.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
from typing import Literal

STAGES = ("consultation", "clinical_review", "industrial_review", "delegated_approval")
ACTION = Literal["approve", "return", "reject"]


class WorkflowError(ValueError):
    pass


@dataclass(frozen=True)
class DecisionContext:
    actor: str
    role: str
    service: str
    authorised_until: datetime
    requestor: str
    is_delegate: bool = False


def _digest(value: dict) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def start_case(case_id: str, version_id: str, version_digest: str, requestor: str, service: str) -> dict:
    if not all((case_id, version_id, version_digest, requestor, service)):
        raise WorkflowError("missing case identity")
    return {"case_id": case_id, "version_id": version_id, "version_digest": version_digest,
            "requestor": requestor, "service": service, "stage": STAGES[0],
            "status": "pending", "generation": 0, "decisions": []}


def decide(case: dict, context: DecisionContext, action: ACTION, operation_id: str,
           expected_generation: int, now: datetime) -> dict:
    """Return a new snapshot; caller must CAS persist it, never mutate case in place."""
    if now.tzinfo is None or context.authorised_until.tzinfo is None:
        raise WorkflowError("timezone-aware timestamps required")
    if not operation_id or action not in ("approve", "return", "reject"):
        raise WorkflowError("invalid operation")
    if context.service != case["service"] or not context.actor or now > context.authorised_until:
        raise WorkflowError("unauthorised or expired delegation")
    if context.actor == case["requestor"]:
        raise WorkflowError("requestor cannot approve their own submitted plan")
    if case["status"] != "pending" or case["stage"] not in STAGES:
        raise WorkflowError("case not pending")
    if case["generation"] != expected_generation:
        raise WorkflowError("stale case generation")
    expected_role = {"consultation": "clinical_director", "clinical_review": "clinical_director",
                     "industrial_review": "medical_workforce", "delegated_approval": "approver"}[case["stage"]]
    if context.role != expected_role or (case["stage"] == "delegated_approval" and not context.is_delegate):
        raise WorkflowError("actor lacks stage authority")
    if any(d["operation_id"] == operation_id for d in case["decisions"]):
        raise WorkflowError("duplicate operation must be handled by durable operation ledger")
    decision = {"operation_id": operation_id, "actor": context.actor, "role": context.role,
                "action": action, "at": now.astimezone(timezone.utc).isoformat(),
                "version_digest": case["version_digest"], "stage": case["stage"]}
    updated = {**case, "generation": case["generation"] + 1,
               "decisions": [*case["decisions"], decision]}
    if action == "return":
        updated["status"] = "returned"
    elif action == "reject":
        updated["status"] = "rejected"
    else:
        idx = STAGES.index(case["stage"])
        if idx == len(STAGES) - 1:
            updated["status"] = "approved"
        else:
            updated["stage"] = STAGES[idx + 1]
    updated["content_hash"] = _digest({k: v for k, v in updated.items() if k != "content_hash"})
    return updated
