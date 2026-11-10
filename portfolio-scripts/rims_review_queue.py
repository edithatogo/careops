"""Deterministic, tenant-free RIMS review queue and approval projection.

This is an offline verification/transport adapter, NOT reviewer authentication,
a SharePoint importer, or authorisation to publish a report. It never modifies
source records and emits only derived JSON/CSV. Native governance must validate
reviewer identity, ETag/concurrency and SharePoint permissions independently.
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import io
import json
from pathlib import Path
import sys

_CONTRACT = Path(__file__).with_name("rims_review_contract.py")
_spec = importlib.util.spec_from_file_location("rims_review_contract", _CONTRACT)
_contract = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_contract)

SCHEMA = "careops-rims.review-queue/1"
COLUMNS = ("subject_id", "assertion_type", "candidate_hash", "evidence_hash",
           "review_state", "decision_id", "source_id", "title", "doi", "pmid")


class QueueError(ValueError):
    """Refused an unsafe offline review queue or decision replay."""


def _unique(records, field):
    seen = set()
    for row in records:
        if not isinstance(row, dict) or not isinstance(row.get(field), str) or not row[field].strip():
            raise QueueError("missing or invalid " + field)
        if row[field] in seen:
            raise QueueError("duplicate " + field + ": " + row[field])
        seen.add(row[field])


def _key(record):
    kind, subject = record.get("assertion_type"), record.get("subject_id")
    if kind not in _contract.TYPES or not isinstance(subject, str) or not subject.strip():
        raise QueueError("invalid subject identity or assertion type")
    return (kind, subject)


def evaluate(candidates, decisions, *, verify_decision=None):
    """Validate append-only decisions against source snapshots, return projections.

    A candidate revision with stale prior decisions goes back to review, not
    approved. Decision ordering must be supplied from an authoritative ledger.
    verify_decision is an externally supplied authorisation callback, NOT a user
    selected flag; verify identity, permission, provenance and immutable ledger
    record before returning True. The standalone CLI never supplies it.
    """
    if not isinstance(candidates, list) or not isinstance(decisions, list):
        raise QueueError("candidates and decisions must be arrays")
    indexed = {}
    for row in candidates:
        if not isinstance(row, dict):
            raise QueueError("non-object candidate")
        k = _key(row)
        if k in indexed:
            raise QueueError("duplicate candidate identity")
        if not isinstance(row.get("evidence_hash"), str) or not row["evidence_hash"].strip():
            raise QueueError("candidate evidence missing")
        indexed[k] = row
    _unique(decisions, "decision_id")
    latest = {}
    decision_errors = []
    verified = {}
    for row in decisions:
        k = _key(row)
        if k not in indexed:
            raise QueueError("decision references missing candidate: " + str(k))
        candidate = indexed[k]
        previous = latest.get(k)
        expected = _contract.fingerprint(candidate)
        if row.get("candidate_hash") != expected:
            # A previously approved assertion is now stale; retain its audit
            # record, but it cannot qualify the changed candidate.
            if previous is None and row.get("supersedes") is None:
                latest[k] = row
                decision_errors.append({"subject_id": k[1], "reason": "stale_candidate", "decision_id": row["decision_id"]})
                continue
            raise QueueError("changed source candidate in decision chain")
        try:
            _contract.validate_decision(candidate, row, expected_candidate_hash=expected, previous=previous)
        except _contract.AdjudicationError as exc:
            raise QueueError(str(exc)) from exc
        latest[k] = row
        verified[k] = bool(verify_decision(row, candidate)) if verify_decision is not None else False
    queue, approved = [], []
    for k, candidate in sorted(indexed.items()):
        last = latest.get(k)
        digest = _contract.fingerprint(candidate)
        valid = bool(last and last.get("candidate_hash") == digest)
        status = last["status"] if valid else "NeedsReview"
        record = {"schema": SCHEMA, "subject_id": k[1], "assertion_type": k[0],
                  "candidate_hash": digest, "evidence_hash": candidate["evidence_hash"],
                  "review_state": status, "decision_id": last["decision_id"] if valid else None,
                  "source_id": candidate.get("source_id", ""),
                  "title": candidate.get("title", ""),
                  "doi": candidate.get("doi", ""), "pmid": candidate.get("pmid", "")}
        queue.append(record)
        # Absolutely no approvals based solely on an untrusted offline JSON file.
        if verified.get(k, False) and valid and k[0] == "publication" and status == "ConfirmedCHHHS":
            approved.append(record)
    return {"schema": SCHEMA, "review_queue": queue,
            "approved_publications": approved, "stale_decisions": decision_errors,
            "authority": "external_verified" if verify_decision is not None else "unverified_offline"}


def _read_envelope(path):
    with Path(path).open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict) or data.get("schema") != SCHEMA:
        raise QueueError("unsupported queue input schema")
    if set(data) != {"schema", "candidates", "decisions"}:
        raise QueueError("unexpected envelope keys")
    return data


def _csv_rows(rows):
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=COLUMNS, lineterminator="\n",
                            extrasaction="ignore")
    writer.writeheader()
    for record in rows:
        # CSV formula injection prevention even for free-text source metadata.
        escaped = {k: ("'" + str(record.get(k, "")) if str(record.get(k, "")).startswith(("=", "+", "-", "@", "\t", "\r"))
                       else record.get(k, "")) for k in COLUMNS}
        writer.writerow(escaped)
    return stream.getvalue()


def main(argv=None):
    parser = argparse.ArgumentParser(description="Offline, read-only RIMS review queue; no tenant connector")
    parser.add_argument("input", help="JSON envelope with schema, candidates, decisions")
    parser.add_argument("--format", choices=("json", "csv"), default="json")
    args = parser.parse_args(argv)
    try:
        payload = _read_envelope(args.input)
        outcome = evaluate(payload["candidates"], payload["decisions"])
    except (QueueError, OSError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(2, "RIMS review refused: " + str(exc) + "\n")
    if args.format == "csv":
        sys.stdout.write(_csv_rows(outcome["review_queue"]))
    else:
        sys.stdout.write(json.dumps(outcome, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
