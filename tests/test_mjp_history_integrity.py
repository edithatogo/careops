"""Reject forged workflow histories and open-ended retired plan versions."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1] / "modules" / "careops-medical-job-planning"


def load(name):
    spec = spec_from_file_location("mjp_integrity_" + name, ROOT / (name + ".py"))
    assert spec and spec.loader
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


NEG = load("negotiation")
RECORDS = load("plan_records")
H = "a" * 64
T = datetime(2026, 11, 13, tzinfo=timezone.utc)


def event(action, k, when=T):
    return NEG.NegotiationEvent(
        f"fixture:op{k}", action, "fixture:actor", "fixture:role",
        "fixture:evidence", H, when,
    )


class HistoryIntegrity(unittest.TestCase):
    def test_forged_negotiation_state_rejected(self):
        with self.assertRaises(NEG.NegotiationError):
            NEG.Thread("fixture:plan", "fixture:ver", H, 1,
                       "agreement_recorded", (event("propose", 1),))

    def test_invalid_history_transition_rejected(self):
        with self.assertRaises(NEG.NegotiationError):
            NEG.Thread("fixture:plan", "fixture:ver", H, 1,
                       "disputed", (event("record_disagreement", 1),))

    def test_out_of_order_event_time_rejected(self):
        with self.assertRaises(NEG.NegotiationError):
            NEG.Thread(
                "fixture:plan", "fixture:ver", H, 2, "counterproposed",
                (event("propose", 1, T),
                 event("counterpropose", 2, T - timedelta(hours=1))),
            )

    def test_retired_and_superseded_versions_require_end_date(self):
        for status in ("retired", "superseded"):
            with self.subTest(status=status), self.assertRaises(RECORDS.VersionError):
                RECORDS.PlanVersion(
                    "fixture:plan", "fixture:ver", H, "fixture:policy",
                    "fixture:appt", "fixture:position", "fixture:service",
                    date(2026, 11, 1), None, T, "fixture:decision", status,
                )


if __name__ == "__main__":
    unittest.main()
