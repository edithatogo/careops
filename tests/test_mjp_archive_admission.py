"""Synthetic ZIP admission tests; original archive deliberately remains outside Git."""
from __future__ import annotations
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from io import BytesIO
import json
from pathlib import Path
import sys
import unittest
from zipfile import ZipFile

FILE = Path(__file__).resolve().parents[1] / "modules" / "careops-medical-job-planning" / "archive_admission.py"
SPEC = spec_from_file_location("mjp_archive_admission", FILE)
assert SPEC is not None and SPEC.loader is not None
ADMISSION = module_from_spec(SPEC)
sys.modules[SPEC.name] = ADMISSION
SPEC.loader.exec_module(ADMISSION)


def make_zip(*, path="domain.py", payload=b"hi", declared=None, extra=False):
    buffer = BytesIO()
    with ZipFile(buffer, "w") as archive:
        archive.writestr("careops-workforce-app/" + path, payload)
        archive.writestr("SOURCE-MANIFEST.json", json.dumps({
            "type": "synthetic", "version": "0",
            "contents": [{"path": path, "sha256": declared or sha256(payload).hexdigest(), "bytes": len(payload)}],
        }))
        if extra:
            archive.writestr("careops-workforce-app/unlisted.py", "oops")
    return buffer.getvalue()


class ArchiveCI(unittest.TestCase):
    def test_valid_inventory_does_not_authorise_publication(self):
        result = ADMISSION.inspect_archive(make_zip())
        self.assertEqual(result["source_count"], 1)
        self.assertEqual(result["integrity"], "verified")
        self.assertFalse(result["publication_approved"])
        self.assertFalse(result["native_deployment_qualified"])
        self.assertIn("full_licence_review", result["remaining_gates"])

    def test_reject_digest_mismatch(self):
        with self.assertRaises(ADMISSION.AdmissionError):
            ADMISSION.inspect_archive(make_zip(declared="a" * 64))

    def test_reject_traversal(self):
        with self.assertRaises(ADMISSION.AdmissionError):
            ADMISSION.inspect_archive(make_zip(path="../private.txt"))

    def test_reject_binary(self):
        with self.assertRaises(ADMISSION.AdmissionError):
            ADMISSION.inspect_archive(make_zip(payload=b"\x00secret"))

    def test_reject_oversized(self):
        with self.assertRaises(ADMISSION.AdmissionError):
            ADMISSION.inspect_archive(make_zip(payload=b"x" * 1_048_577))

    def test_reject_unlisted(self):
        with self.assertRaises(ADMISSION.AdmissionError):
            ADMISSION.inspect_archive(make_zip(extra=True))


if __name__ == "__main__":
    unittest.main()
