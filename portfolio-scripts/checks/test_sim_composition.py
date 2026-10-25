"""Source-only tests for the fictional Rust-native Sim composition boundary."""

from copy import deepcopy
from datetime import date
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "portfolio-scripts"))
import sim_interop_v1 as interop  # noqa: E402


class SimComposition(unittest.TestCase):
    def setUp(self):
        self.packet = json.loads((ROOT / "portfolio-scripts/fixtures/sim/run-packet-v1.json").read_text())
        self.input_files = {"scenario-v1.json": (ROOT / "portfolio-scripts/fixtures/sim/scenario-v1.json").read_bytes()}
        self.as_of = date(2026, 10, 25)

    def validate(self, packet):
        return interop.validate_packet(packet, as_of_date=self.as_of, input_files=self.input_files)

    def test_adapter_source_pin_matches_reviewed_gitlink(self):
        manifest = json.loads((ROOT / "PUBLIC_SOURCE_FILES.json").read_text())
        self.assertEqual(interop.SIM_SOURCE_COMMIT, manifest["gitlinks"]["modules/careops-sim"])

    def test_valid_packet_is_deterministic_and_non_mutating(self):
        before = deepcopy(self.packet)
        first = self.validate(self.packet)
        second = self.validate(self.packet)
        self.assertEqual("Ready", first["status"])
        self.assertEqual(first, second)
        self.assertEqual(before, self.packet)
        self.assertEqual(interop.SIM_SOURCE_COMMIT, first["runs"][0]["engineSourceCommit"])
        self.assertEqual("tick", first["runs"][0]["timeUnit"])

    def test_provider_absence_and_incompatible_packet_version_fail_closed(self):
        absent = deepcopy(self.packet)
        absent["providerAvailable"] = False
        self.assertEqual("ProviderAbsent", self.validate(absent)["status"])
        incompatible = deepcopy(self.packet)
        incompatible["contractVersion"] = 2
        self.assertEqual("IncompatibleVersion", self.validate(incompatible)["status"])
        boolean_version = deepcopy(self.packet)
        boolean_version["contractVersion"] = True
        self.assertEqual("IncompatibleVersion", self.validate(boolean_version)["status"])

    def test_stale_future_and_missing_observations_fail_closed(self):
        for observed, expected in [("2026-09-01", "Stale"), ("2026-10-26", "Stale"), (None, "MissingInput")]:
            packet = deepcopy(self.packet)
            packet["observedDate"] = observed
            with self.subTest(observed=observed):
                self.assertEqual(expected, self.validate(packet)["status"])

    def test_missing_or_incompatible_run_metadata_fail_closed(self):
        missing = deepcopy(self.packet)
        del missing["runDocuments"][0]["manifest"]["input_sha256"]
        self.assertEqual("MissingInput", self.validate(missing)["status"])
        incompatible = deepcopy(self.packet)
        incompatible["runDocuments"][0]["manifest"]["schema_version"] = 2
        self.assertEqual("IncompatibleVersion", self.validate(incompatible)["status"])

    def test_missing_changed_and_traversal_inputs_fail_closed(self):
        missing = deepcopy(self.packet)
        missing["runDocuments"][0]["manifest"]["input_file"] = "missing.json"
        self.assertEqual("MissingInput", self.validate(missing)["status"])
        traversal = deepcopy(self.packet)
        traversal["runDocuments"][0]["manifest"]["input_file"] = "../scenario.json"
        self.assertEqual("MissingInput", self.validate(traversal)["status"])
        changed = {"scenario-v1.json": b"{}"}
        self.assertEqual("InputDigestMismatch", interop.validate_packet(self.packet, as_of_date=self.as_of, input_files=changed)["status"])
        mismatch = deepcopy(self.packet)
        mismatch["runDocuments"][0]["manifest"]["seed"] += 1
        self.assertEqual("InputManifestMismatch", self.validate(mismatch)["status"])

    def test_unselected_engine_revision_is_rejected(self):
        packet = deepcopy(self.packet)
        packet["engineSourceCommit"] = "b" * 40
        self.assertEqual("IncompatibleSource", self.validate(packet)["status"])

    def test_identical_retry_is_idempotent_and_conflicting_retry_is_rejected(self):
        duplicate = deepcopy(self.packet)
        duplicate["runDocuments"].append(deepcopy(duplicate["runDocuments"][0]))
        self.assertEqual(1, len(self.validate(duplicate)["runs"]))
        conflict = deepcopy(duplicate)
        conflict["runDocuments"][1]["summary"]["events_processed"] = 38
        self.assertEqual("DuplicateConflict", self.validate(conflict)["status"])

    def test_non_synthetic_or_clinical_validation_claims_are_rejected(self):
        packet = deepcopy(self.packet)
        packet["runDocuments"][0]["validation_taxonomy"]["validation_scope"] = "clinical"
        self.assertEqual("UnsupportedProvenance", self.validate(packet)["status"])


if __name__ == "__main__":
    unittest.main()
