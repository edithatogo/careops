#!/usr/bin/env python3
"""Apache-2.0. Prepare a private assessment queue without network or native writes.

Keep real-document jobs in a different database from fictional inference jobs.
All prepared records are held; no command here releases them for transmission.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sqlite3


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def pinned_source(source):
    return tuple(source.get(k) for k in ("documentUID", "sourceVersion", "originalSHA256", "textSHA256"))


def full_review(packet, text):
    review = packet.get("review", {})
    if review.get("fullTextReviewed") is not True or review.get("basis") != "full-text-and-operative-review":
        return False
    cursor = 0
    for section in review.get("sections", []):
        end = section.get("end")
        if section.get("start") != cursor or type(end) is not int or not cursor < end <= len(text):
            return False
        cursor = end
    if cursor != len(text):
        return False
    dimensions = review.get("dimensions", {})
    if set(dimensions) != {"references", "contradictions", "operative_dependencies", "governance_and_handoffs"}:
        return False
    for dimension in dimensions.values():
        if not dimension.get("notes") or not dimension.get("passages"):
            return False
        for passage in dimension["passages"]:
            start, end = passage.get("start"), passage.get("end")
            if type(start) is not int or type(end) is not int or not 0 <= start < end <= len(text) or text[start:end] != passage.get("quote"):
                return False
    return True


def prepare(snapshot_path, index_paths, reviews_root, output):
    os.umask(0o077)
    snapshot_bytes = snapshot_path.read_bytes()
    snapshot_hash = sha(snapshot_bytes)
    snapshot = json.loads(snapshot_bytes)
    rows = snapshot["rows"]
    if not snapshot.get("observedAtUtc") or not rows or len({r["Id"] for r in rows}) != len(rows):
        raise ValueError("Dated, unique native incomplete snapshot required")
    if len({r["DocumentUID"] for r in rows}) != len(rows):
        raise ValueError("Native document identity collision")
    if any(r.get("AssessmentComplete") is not False for r in rows):
        raise ValueError("Snapshot includes completed or uncertain-state assessments")
    indices = defaultdict(list)
    for path in index_paths:
        for source in json.loads(path.read_text()).values():
            indices[pinned_source(source)].append(source)
    reviews = defaultdict(list)
    for path in sorted(reviews_root.glob("relationship-assessment-central-case*-r42-20261028-r1/review-packet.json")):
        try:
            content = path.read_bytes()
            packet = json.loads(content)
            reviews[pinned_source(packet.get("source", {}))].append((path, sha(content), packet))
        except (OSError, ValueError):
            continue
    cache = {}

    def retained(source):
        key = pinned_source(source)
        if key in cache:
            return cache[key]
        for candidate in indices[key]:
            try:
                original = Path(candidate["originalPath"])
                extraction = Path(candidate["extractionRecord"])
                record = json.loads(extraction.read_text())
                text = record["text"]
                if not isinstance(text, str) or not text.strip() or record.get("error"):
                    continue
                if sha(original.read_bytes()) != source["originalSHA256"] or sha(text.encode()) != source["textSHA256"]:
                    continue
                cache[key] = (original, extraction, text)
                return cache[key]
            except (OSError, KeyError, ValueError):
                continue
        cache[key] = None
        return None

    output.mkdir(parents=True, exist_ok=True, mode=0o700)
    db = sqlite3.connect(output / "assessments.sqlite3")
    db.executescript("""
      PRAGMA journal_mode=WAL;
      CREATE TABLE IF NOT EXISTS assessment_jobs (
        assessment_id INTEGER PRIMARY KEY, document_uid TEXT NOT NULL UNIQUE,
        state TEXT NOT NULL, readiness TEXT NOT NULL, fingerprint TEXT NOT NULL,
        packet TEXT NOT NULL, updated TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS revisions (
        assessment_id INTEGER NOT NULL, fingerprint TEXT NOT NULL, packet TEXT NOT NULL,
        created TEXT NOT NULL, PRIMARY KEY(assessment_id,fingerprint));
    """)
    prepared_at = datetime.now(timezone.utc).isoformat()
    counts = Counter()
    unchanged = 0
    with db:
        for row in sorted(rows, key=lambda r: r["Id"]):
            manifest = json.loads(row["EvidenceManifest"])
            reasons = []
            bindings = []
            reusable = []
            sources = manifest.get("sources", [])
            if not sources:
                reasons.append("no_native_retained_source_binding")
            for source in sources:
                if source.get("documentUID") != row["DocumentUID"] or source.get("versionConflict") or source.get("extractionError"):
                    reasons.append("native_source_identity_or_extraction_hold")
                    continue
                local = retained(source)
                if not local:
                    reasons.append("pinned_original_or_text_not_locally_verified")
                    continue
                original, extraction, text = local
                bindings.append({"source": source, "originalPath": str(original), "extractionRecord": str(extraction),
                                 "textChars": len(text), "originalSHA256": source["originalSHA256"], "textSHA256": source["textSHA256"]})
                for path, fingerprint, packet in reviews[pinned_source(source)]:
                    if full_review(packet, text):
                        reusable.append({"path": str(path), "sha256": fingerprint,
                                         "result": packet.get("result"), "requiresCurrentGraphAndEndpointReconciliation": True,
                                         "remainingReviewInputs": packet.get("review", {}).get("unresolved", [])})
            if row["AssessmentState"] != "Needs relationship review":
                reasons.append("native_evidence_or_source_hold_preserved")
            if reasons:
                readiness = "blocked_source_or_identity"
            elif reusable:
                readiness = "reuse_full_review_before_new_inference"
            else:
                readiness = "body_ready_for_review_after_endpoint_approval"
            counts[readiness] += 1
            packet = {"schemaVersion": 1, "classification": "private", "transmissionAllowed": False,
                      "nativeSnapshotSHA256": snapshot_hash, "assessment": row,
                      "localSourceBindings": bindings, "retainedFullReviews": reusable,
                      "blockers": sorted(set(reasons)), "readiness": readiness,
                      "clinicalAcceptance": None, "currentAuthorityVerified": False}
            payload = encode(packet)
            fingerprint = sha(encode({k: v for k, v in packet.items() if k != "nativeSnapshotSHA256"}).encode())
            previous = db.execute("SELECT document_uid,state,fingerprint FROM assessment_jobs WHERE assessment_id=?", (row["Id"],)).fetchone()
            if previous and previous[0] != row["DocumentUID"]:
                raise ValueError("Assessment identity changed; reconcile before updating queue")
            if previous and previous[2] == fingerprint:
                unchanged += 1
                continue
            state = "held_private" if not previous else "held_changed_inputs"
            db.execute("INSERT OR IGNORE INTO revisions VALUES (?,?,?,?)", (row["Id"], fingerprint, payload, prepared_at))
            db.execute("INSERT INTO assessment_jobs VALUES (?,?,?,?,?,?,?) ON CONFLICT(assessment_id) DO UPDATE SET state=excluded.state,readiness=excluded.readiness,fingerprint=excluded.fingerprint,packet=excluded.packet,updated=excluded.updated",
                       (row["Id"], row["DocumentUID"], state, readiness, fingerprint, payload, prepared_at))
        current_ids = {row["Id"] for row in rows}
        for (item_id,) in db.execute("SELECT assessment_id FROM assessment_jobs").fetchall():
            if item_id not in current_ids:
                db.execute("UPDATE assessment_jobs SET state='outside_latest_incomplete_snapshot',updated=? WHERE assessment_id=?", (prepared_at, item_id))
    db.close()
    summary = {"preparedAtUtc": prepared_at, "nativeObservedAtUtc": snapshot["observedAtUtc"],
               "nativeSnapshotSHA256": snapshot_hash, "totalIncomplete": len(rows),
               "nativeStates": dict(Counter(r["AssessmentState"] for r in rows)), "readiness": dict(counts),
               "unchangedOnReplay": unchanged, "privateTransmissionEnabled": False,
               "nativeWrites": 0, "approval": "not_granted"}
    (output / "summary.json").write_text(json.dumps(summary, indent=2))
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--source-index", type=Path, action="append", required=True)
    parser.add_argument("--reviews-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.snapshot, args.source_index, args.reviews_root, args.output)))


if __name__ == "__main__":
    main()
