"""Apache-2.0. Fictional queue pins, holds, reuse and replay checks."""
import importlib.util
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("assessment_queue", Path(__file__).parents[1] / "scripts/ppg_assessment_queue.py")
q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)


class QueueTests(unittest.TestCase):
    def fixture(self, root):
        text = "Fictional policy body; no real organisation or patient."
        original = root / "fictional.pdf"
        original.write_bytes(b"fictional original bytes")
        extraction = root / "text.json"
        extraction.write_text(json.dumps({"text": text, "error": None}))
        source = {"documentUID": "fictional-uid", "sourceVersion": "fictional-v1", "originalSHA256": q.sha(original.read_bytes()),
                  "textSHA256": q.sha(text.encode()), "identityState": "verified_source_identity", "extractionError": None, "versionConflict": False}
        index = root / "index.json"
        index.write_text(json.dumps({"1": dict(source, originalPath=str(original), extractionRecord=str(extraction))}))
        snapshot = root / "snapshot.json"
        row = {"Id": 1, "DocumentUID": "fictional-uid", "AssessmentComplete": False, "AssessmentState": "Needs relationship review",
               "EvidenceManifest": json.dumps({"sources": [source]})}
        snapshot.write_text(json.dumps({"observedAtUtc": "2026-11-04T00:00:00Z", "rows": [row]}))
        return snapshot, index, row, source, text

    def test_private_hold_replay_and_source_tampering(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            snapshot, index, row, _, _ = self.fixture(root)
            output = root / "queue"
            result = q.prepare(snapshot, [index], root, output)
            self.assertEqual(result["readiness"], {"body_ready_for_review_after_endpoint_approval": 1})
            self.assertFalse(result["privateTransmissionEnabled"])
            self.assertEqual(q.prepare(snapshot, [index], root, output)["unchangedOnReplay"], 1)
            (root / "fictional.pdf").write_bytes(b"changed")
            result = q.prepare(snapshot, [index], root, output)
            self.assertEqual(result["readiness"], {"blocked_source_or_identity": 1})
            with closing(sqlite3.connect(output / "assessments.sqlite3")) as db:
                self.assertEqual(db.execute("SELECT count(*) FROM revisions").fetchone()[0], 2)
                packet = json.loads(db.execute("SELECT packet FROM assessment_jobs").fetchone()[0])
                self.assertFalse(packet["transmissionAllowed"])

    def test_reuse_preserves_native_evidence_hold(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            snapshot, index, row, source, text = self.fixture(root)
            folder = root / "relationship-assessment-central-case1-r42-20261028-r1"
            folder.mkdir()
            passage = {"start": 0, "end": len(text), "quote": text}
            review = {"fullTextReviewed": True, "basis": "full-text-and-operative-review",
                      "sections": [{"start": 0, "end": len(text)}],
                      "dimensions": {key: {"notes": "fictional inspection", "passages": [passage]} for key in
                                     ("references", "contradictions", "operative_dependencies", "governance_and_handoffs")}}
            (folder / "review-packet.json").write_text(json.dumps({"source": source, "review": review, "result": "fictional"}))
            self.assertEqual(q.prepare(snapshot, [index], root, root / "queue")["readiness"], {"reuse_full_review_before_new_inference": 1})
            row["AssessmentState"] = "Needs evidence"
            snapshot.write_text(json.dumps({"observedAtUtc": "2026-11-04T00:00:00Z", "rows": [row]}))
            self.assertEqual(q.prepare(snapshot, [index], root, root / "queue")["readiness"], {"blocked_source_or_identity": 1})


if __name__ == "__main__":
    unittest.main()
