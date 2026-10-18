"""Exercise pinned public contracts and the real Process consumer, offline.

Approve's event emitter is a disabled blueprint. These checks qualify its declared
boundary against a synthetic payload and the installed Process implementation;
they do not manufacture a producer or claim a deployed integration.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


def verify_source(path: Path, expected: str) -> None:
    """Require the exact clean tracked revision, including a genuine checkout."""
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=path, check=True,
        capture_output=True, text=True,
    ).stdout.strip()
    if head != expected:
        raise ValueError(f"Unexpected source revision: {path.name}")
    subprocess.run(["git", "diff", "--quiet", "HEAD", "--"], cwd=path, check=True)


def payload() -> dict:
    return {
        "contract_version": "0.1.0", "ontology_version": "0.1.0",
        "source": "careops-approve", "watermark_utc": "2026-10-18T12:00:00Z",
        "facts": [{
            "event_id": "careops-approve:fictional-001:received",
            "activity": "request_received", "timestamp_utc": "2026-10-18T11:00:00Z",
            "source_system": "careops-approve", "object_ids": ["careops-approve:fictional-001"],
            "observed_or_inferred": "observed", "confidence": 1.0,
            "qualifiers": {"feature_pack_version": "0.1.0"},
        }],
    }


class Compatibility(unittest.TestCase):
    consumer = None
    flow = None
    schema = None

    def test_declared_producer_boundary(self):
        self.assertEqual(self.flow["status"], "blueprint-disabled-by-default")
        emitters = [step for step in self.flow["steps"] if step["id"] == "emit-process-events"]
        self.assertEqual(len(emitters), 1)
        self.assertEqual(emitters[0]["targetContract"], "careops-process-credentialing-events-0.1.0")
        self.assertIs(emitters[0]["rawDocuments"], False)
        self.assertIs(emitters[0]["freeText"], False)
        self.assertIn("careops-approve", self.schema["properties"]["source"]["enum"])
        self.assertEqual(self.schema["properties"]["contract_version"]["const"], "0.1.0")

    def test_real_parser_and_summary(self):
        projection = self.consumer.validate_credentialing_projection(payload())
        metrics = self.consumer.summarise_credentialing_projection(projection)
        self.assertEqual(metrics.event_count, 1)
        self.assertEqual(metrics.unique_object_count, 1)
        self.assertEqual(projection.facts[0].object_ids, ["careops-approve:fictional-001"])

    def test_incompatible_version(self):
        for field in ("contract_version", "ontology_version"):
            with self.subTest(field=field):
                candidate = payload()
                candidate[field] = "99.0.0"
                with self.assertRaises(ValueError):
                    self.consumer.validate_credentialing_projection(candidate)

    def test_missing_input(self):
        for field in ("facts", "source"):
            with self.subTest(field=field):
                candidate = payload()
                del candidate[field]
                with self.assertRaises(ValueError):
                    self.consumer.validate_credentialing_projection(candidate)

    def test_duplicate_retry(self):
        projection = self.consumer.validate_credentialing_projection(payload())
        merged = self.consumer.merge_credentialing_projections(projection, projection)
        self.assertEqual(merged.model_dump(), projection.model_dump())
        duplicate = payload()
        duplicate["facts"] *= 2
        with self.assertRaises(ValueError):
            self.consumer.validate_credentialing_projection(duplicate)

    def test_stale_replay_cannot_regress_watermark(self):
        original = self.consumer.validate_credentialing_projection(payload())
        stale = payload()
        stale["watermark_utc"] = "2026-10-17T12:00:00Z"
        incoming = self.consumer.validate_credentialing_projection(stale)
        result = self.consumer.merge_credentialing_projections(original, incoming)
        self.assertEqual(result.model_dump(), original.model_dump())

    def test_conflicting_edit_preserves_original(self):
        original = self.consumer.validate_credentialing_projection(payload())
        before = deepcopy(original.model_dump())
        changed = payload()
        changed["facts"][0]["qualifiers"]["exception_code"] = "fictional-reviewed-edit"
        incoming = self.consumer.validate_credentialing_projection(changed)
        with self.assertRaises(self.consumer.CredentialingContractError):
            self.consumer.merge_credentialing_projections(original, incoming)
        self.assertEqual(original.model_dump(), before)
        self.assertEqual(incoming.facts[0].qualifiers.exception_code, "fictional-reviewed-edit")

    def test_other_source_cannot_reuse_batch(self):
        original = self.consumer.validate_credentialing_projection(payload())
        other = payload()
        other["source"] = "careops-decisions"
        incoming = self.consumer.validate_credentialing_projection(other)
        with self.assertRaises(self.consumer.CredentialingContractError):
            self.consumer.merge_credentialing_projections(original, incoming)

    def test_private_content_refused(self):
        candidate = payload()
        candidate["facts"][0]["qualifiers"]["email"] = "fictional@example.invalid"
        with self.assertRaises(self.consumer.CredentialingContractError):
            self.consumer.validate_credentialing_projection(candidate)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--module-root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads((ROOT / "portfolio/public-runtime-compatibility.json").read_text())
    receipt = {
        "moduleCommits": manifest["modules"], "passed": False,
        "producerRuntimeQualified": False, "productionWrites": False,
        "scope": manifest["scope"],
        "limits": "No actual Approve emitter, native runtime, freshness cutoff policy or tenant acceptance is qualified.",
    }
    try:
        for name, commit in manifest["modules"].items():
            verify_source(args.module_root / name, commit)
        approve = args.module_root / "careops-approve"
        process = args.module_root / "careops-process"
        files = {
            "approveBoundary": approve / "flows/credentialing-intake-and-handoff.contract.json",
            "consumerSchema": process / "contracts/credentialing-event-projection.json",
        }
        Compatibility.flow = json.loads(files["approveBoundary"].read_text())
        Compatibility.schema = json.loads(files["consumerSchema"].read_text())
        Compatibility.consumer = importlib.import_module("careops_process.credentialing")
        installed = Path(Compatibility.consumer.__file__).resolve()
        # The Process environment is built from the exact verified checkout. Refuse
        # an unrelated installed package or a shadowing checkout on PYTHONPATH.
        if not installed.is_relative_to(process.resolve()):
            raise ValueError("Consumer import is outside the pinned Process environment")
        files["consumerImplementation"] = installed
        receipt["fileSha256"] = {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in files.items()}
        result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Compatibility))
        receipt["testsRun"] = result.testsRun
        receipt["passed"] = result.wasSuccessful()
    except (OSError, ValueError, subprocess.CalledProcessError, ImportError) as error:
        receipt["setupFailure"] = type(error).__name__
        print(f"Compatibility setup refused: {type(error).__name__}", file=sys.stderr)
    finally:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(json.dumps(receipt, indent=2) + "\n")
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
