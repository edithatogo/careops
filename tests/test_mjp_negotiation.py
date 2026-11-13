"""Source-only candidate negotiation tests; human authority remains external."""
from __future__ import annotations
from datetime import datetime, timezone
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "modules" / "careops-medical-job-planning" / "negotiation.py"
SPEC = spec_from_file_location("mjp_negotiation", SOURCE)
assert SPEC is not None and SPEC.loader is not None
M = module_from_spec(SPEC)
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)
SHA = "a" * 64


def evt(kind, index, **changes):
    data = dict(
        operation_id=f"fixture-operation-{index}", kind=kind,
        actor_ref="fixture:actor", role_ref="fixture:role",
        evidence_ref=f"fixture:evidence-{index}",
        payload_sha256=SHA, occurred_at=datetime(2026, 11, 13, tzinfo=timezone.utc),
    )
    data.update(changes)
    return M.NegotiationEvent(**data)


def start():
    return M.Thread(
        plan_key="fixture:plan", version_key="fixture:version",
        submitted_sha256=SHA, generation=0, state="submitted", events=(),
    )


class NegotiationTests(unittest.TestCase):
    def test_immutable_counterproposal_and_dispute(self):
        first = start()
        consultation = M.advance(first, evt("propose", 1), 0)
        counter = M.advance(consultation, evt("counterpropose", 2), 1)
        dispute = M.advance(counter, evt("record_disagreement", 3), 2)
        self.assertEqual((consultation.state, counter.state, dispute.state),
                         ("consulting", "counterproposed", "disputed"))
        self.assertEqual((len(first.events), len(dispute.events)), (0, 3))
        self.assertEqual(dispute.submitted_sha256, first.submitted_sha256)

    def test_stale_generation_rejected(self):
        current = M.advance(start(), evt("propose", 1), 0)
        with self.assertRaises(M.NegotiationError):
            M.advance(current, evt("counterpropose", 2), 0)

    def test_identical_replay_is_noop_conflicting_key_rejected(self):
        command = evt("propose", 1)
        current = M.advance(start(), command, 0)
        self.assertIs(M.advance(current, command, 0), current)
        with self.assertRaises(M.NegotiationError):
            M.advance(current, evt("counterpropose", 1), 1)

    def test_approval_and_issue_are_not_legal_transitions(self):
        with self.assertRaises(M.NegotiationError):
            evt("approved", 1)
        with self.assertRaises(M.NegotiationError):
            M.advance(start(), evt("request_authorisation", 2), 0)

    def test_authorisation_request_is_not_approval(self):
        state = start()
        for number, action in enumerate(("propose", "record_consensus", "request_authorisation"), 1):
            state = M.advance(state, evt(action, number), state.generation)
        self.assertEqual(state.state, "authority_pending")
        self.assertNotIn(state.state, ("approved", "issued", "active"))

    def test_escalation_and_return(self):
        state = start()
        actions = ("propose", "record_disagreement", "escalate", "return_for_revision", "propose")
        for number, action in enumerate(actions, 1):
            state = M.advance(state, evt(action, number), state.generation)
        self.assertEqual(state.state, "consulting")

    def test_missing_evidence_rejected(self):
        with self.assertRaises(M.NegotiationError):
            evt("propose", 1, evidence_ref="")

    def test_non_utc_timestamp_rejected(self):
        with self.assertRaises(M.NegotiationError):
            evt("propose", 1, occurred_at=datetime(2026, 11, 13))

    def test_invalid_submitted_digest_rejected(self):
        with self.assertRaises(M.NegotiationError):
            M.Thread(plan_key="fixture:plan", version_key="fixture:version",
                     submitted_sha256="bad", generation=0, state="submitted", events=())


if __name__ == "__main__":
    unittest.main()
