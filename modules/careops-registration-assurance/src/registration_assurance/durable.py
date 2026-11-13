"""Durable SQLite reference ledger for *fictional* registration evidence only.

This offline/test backend is NOT a production datastore, AHPRA connection,
credentialing register, native access-control boundary or Dataverse replacement.
Native deployment needs separately tested permissions, storage, audit, backup,
recovery and source authenticity.
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
from typing import Any, Iterator, Mapping

from .deterministic import Admission


class LedgerConflict(RuntimeError):
    """Concurrent, malformed or replayed mutation cannot be committed."""


class IntegrityFailure(RuntimeError):
    """An append-only history/projection consistency check failed."""


def _json(value: object) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=True,
                      separators=(",", ":"), allow_nan=False)


def _sha(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def _utc(value: str) -> str:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include offset")
    return parsed.astimezone(timezone.utc).isoformat(
        timespec="microseconds").replace("+00:00", "Z")


def _required(record: Mapping[str, Any], key: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"missing {key}")
    return value


_DDL = """
CREATE TABLE IF NOT EXISTS observations (
 watch_ref TEXT NOT NULL,
 seq INTEGER NOT NULL,
 observation_id TEXT NOT NULL UNIQUE,
 idempotency_key TEXT NOT NULL,
 payload_digest TEXT NOT NULL,
 payload_json TEXT NOT NULL,
 source_asof TEXT NOT NULL,
 previous_hash TEXT NOT NULL,
 event_hash TEXT NOT NULL,
 outcome TEXT NOT NULL,
 PRIMARY KEY (watch_ref,seq),
 UNIQUE (watch_ref,idempotency_key)
);
CREATE TABLE IF NOT EXISTS ledger_heads (
 watch_ref TEXT PRIMARY KEY, version INTEGER NOT NULL,
 last_seq INTEGER NOT NULL, event_hash TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS projections (
 watch_ref TEXT PRIMARY KEY,
 version INTEGER NOT NULL, seq INTEGER NOT NULL,
 observation_id TEXT NOT NULL, source_asof TEXT NOT NULL,
 outcome TEXT NOT NULL,
 practice_authorised INTEGER NOT NULL CHECK(practice_authorised=0)
);
CREATE TABLE IF NOT EXISTS outbox (
 event_id TEXT PRIMARY KEY, watch_ref TEXT NOT NULL,
 version INTEGER NOT NULL DEFAULT 1, payload_json TEXT NOT NULL,
 ack_ref TEXT,
 state TEXT NOT NULL DEFAULT 'pending'
 CHECK(state IN ('pending','acknowledged'))
);
CREATE TABLE IF NOT EXISTS review_heads (
 case_id TEXT PRIMARY KEY, watch_ref TEXT NOT NULL,
 version INTEGER NOT NULL, data_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS review_events (
 case_id TEXT NOT NULL, version INTEGER NOT NULL,
 data_json TEXT NOT NULL, event_hash TEXT NOT NULL,
 prior_hash TEXT NOT NULL, PRIMARY KEY(case_id,version)
);
CREATE TABLE IF NOT EXISTS job_heads (
 job_id TEXT PRIMARY KEY, watch_ref TEXT NOT NULL,
 version INTEGER NOT NULL, data_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS job_events (
 job_id TEXT NOT NULL, version INTEGER NOT NULL,
 data_json TEXT NOT NULL, PRIMARY KEY(job_id,version)
);
CREATE TRIGGER IF NOT EXISTS no_observation_updates
 BEFORE UPDATE ON observations BEGIN SELECT RAISE(ABORT,'append-only observations'); END;
CREATE TRIGGER IF NOT EXISTS no_observation_deletes
 BEFORE DELETE ON observations BEGIN SELECT RAISE(ABORT,'append-only observations'); END;
CREATE TRIGGER IF NOT EXISTS no_review_events_update
 BEFORE UPDATE ON review_events BEGIN SELECT RAISE(ABORT,'append-only review events'); END;
CREATE TRIGGER IF NOT EXISTS no_review_events_delete
 BEFORE DELETE ON review_events BEGIN SELECT RAISE(ABORT,'append-only review events'); END;
CREATE TRIGGER IF NOT EXISTS no_job_events_update
 BEFORE UPDATE ON job_events BEGIN SELECT RAISE(ABORT,'append-only job events'); END;
CREATE TRIGGER IF NOT EXISTS no_job_events_delete
 BEFORE DELETE ON job_events BEGIN SELECT RAISE(ABORT,'append-only job events'); END;
"""


class DeterministicLedger:
    """File-backed reference ledger with serialized writers and version CAS.

    This intentionally stores no real or restricted-personnel evidence. Each
    method opens a separate SQLite connection for restart/concurrency tests;
    BEGIN IMMEDIATE serializes writer transitions before the version check.
    This is not an enterprise distributed-storage or security guarantee.
    """

    def __init__(self, database: str | Path):
        path = Path(database)
        if str(database) == ":memory:" or not path.is_absolute():
            raise ValueError("reference ledger requires an absolute on-disk path")
        if path.is_symlink() or not path.parent.is_dir():
            raise ValueError("symlink or missing parent refused")
        self.path = path
        with self._connect() as db:
            db.executescript(_DDL)

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        db = sqlite3.connect(self.path, isolation_level=None, timeout=5)
        db.row_factory = sqlite3.Row
        try:
            db.execute("PRAGMA foreign_keys=ON")
            db.execute("PRAGMA busy_timeout=5000")
            db.execute("PRAGMA synchronous=FULL")
            db.execute("PRAGMA journal_mode=WAL")
            yield db
        finally:
            db.close()

    @contextmanager
    def _tx(self) -> Iterator[sqlite3.Connection]:
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            try:
                yield db
            except BaseException:
                db.rollback()
                raise
            else:
                db.commit()

    def append(self, admitted: Admission, *, expected_version: int,
               fault_after_insert: bool = False) -> dict[str, Any]:
        """Atomically append one admitted synthetic event and internal outbox.

        Exact duplicate delivery is a no-op even if expected_version is stale;
        a reused idempotency key with changed content is always a conflict.
        Projection is only a last *observation*, never practice authority.
        """
        if not isinstance(admitted, Admission) or not admitted.persistible:
            raise LedgerConflict("unqualified or invalid observation")
        observation = admitted.observation
        evidence = observation.get("evidence", {})
        if evidence.get("classification") != "synthetic":
            raise LedgerConflict("real personnel data prohibited in SQLite reference")
        watch = _required(observation, "watchRef")
        oid = _required(observation, "observationId")
        idempotency = _required(observation, "idempotencyKey")
        if admitted.assessment.get("practice_authorised") is not False:
            raise LedgerConflict("never grant practice authority")
        if type(expected_version) is not int or expected_version < 0:
            raise LedgerConflict("invalid ledger version")
        canonical = _json({"observation": observation,
                           "assessment": admitted.assessment,
                           "bindingRevision": admitted.binding_revision})
        digest = _sha(canonical)
        source_asof = _utc(_required(evidence, "asOfUtc"))
        with self._tx() as db:
            old = db.execute(
                "SELECT seq,payload_digest FROM observations "
                "WHERE watch_ref=? AND idempotency_key=?",
                (watch,idempotency)).fetchone()
            if old is not None:
                if old["payload_digest"] != digest:
                    raise LedgerConflict("idempotency key reused with new evidence")
                return {"result": "duplicate", "seq": old["seq"],
                        "version": None, "practiceAuthorised": False}
            repeated = db.execute(
                "SELECT observation_id FROM observations WHERE observation_id=?",
                (oid,)).fetchone()
            if repeated is not None:
                raise LedgerConflict("observation identifier reused")
            head = db.execute(
                "SELECT version,last_seq,event_hash FROM ledger_heads "
                "WHERE watch_ref=?", (watch,)).fetchone()
            version = head["version"] if head is not None else 0
            if version != expected_version:
                raise LedgerConflict("ledger revision conflict")
            seq = head["last_seq"] + 1 if head is not None else 1
            previous = head["event_hash"] if head is not None else "0"*64
            event_hash = _sha(_json([watch, seq, previous, digest]))
            projection = db.execute(
                "SELECT version,source_asof FROM projections WHERE watch_ref=?",
                (watch,)).fetchone()
            outcome = "accepted"
            if projection is not None:
                if source_asof < projection["source_asof"]:
                    outcome = "older_evidence"
                elif source_asof == projection["source_asof"]:
                    outcome = "conflicting_source_revision"
            db.execute(
                "INSERT INTO observations "
                "(watch_ref,seq,observation_id,idempotency_key,payload_digest,"
                "payload_json,source_asof,previous_hash,event_hash,outcome) "
                "VALUES (?,?,?,?,?,?,?,?,?,?)",
                (watch,seq,oid,idempotency,digest,canonical,source_asof,
                 previous,event_hash,outcome))
            if fault_after_insert:
                raise RuntimeError("synthetic transaction-failure injection")
            if head is None:
                db.execute("INSERT INTO ledger_heads VALUES (?,?,?,?)",
                           (watch,1,seq,event_hash))
            else:
                db.execute(
                    "UPDATE ledger_heads SET version=?,last_seq=?,event_hash=? "
                    "WHERE watch_ref=? AND version=?",
                    (version+1,seq,event_hash,watch,version))
                if db.execute("SELECT changes()").fetchone()[0] != 1:
                    raise LedgerConflict("concurrent append")
            if outcome == "accepted":
                projection_version = projection["version"] if projection is not None else 0
                if projection is None:
                    db.execute(
                        "INSERT INTO projections VALUES (?,?,?,?,?,?,0)",
                        (watch,1,seq,oid,source_asof,
                         admitted.assessment["disposition"]))
                else:
                    db.execute(
                        "UPDATE projections SET version=?,seq=?,observation_id=?,"
                        "source_asof=?,outcome=?,practice_authorised=0 "
                        "WHERE watch_ref=? AND version=?",
                        (projection_version+1,seq,oid,source_asof,
                         admitted.assessment["disposition"],watch,projection_version))
                    if db.execute("SELECT changes()").fetchone()[0] != 1:
                        raise LedgerConflict("concurrent projection update")
            event_id = _sha(_json(["internal-observation",watch,seq]))
            db.execute("INSERT INTO outbox(event_id,watch_ref,payload_json) VALUES(?,?,?)",
                       (event_id,watch,_json({
                           "eventType": "observation_recorded",
                           "observationId": oid, "outcome": outcome,
                           "practiceAuthorised": False})))
            return {"result": outcome, "seq": seq, "version": version+1,
                    "practiceAuthorised": False}

    def observations(self, watch_ref: str) -> list[dict[str, Any]]:
        with self._connect() as db:
            rows = db.execute(
                "SELECT payload_json FROM observations WHERE watch_ref=? ORDER BY seq",
                (watch_ref,)).fetchall()
            return [json.loads(r["payload_json"])["observation"] for r in rows]

    def current_projection(self, watch_ref: str) -> dict[str, Any] | None:
        with self._connect() as db:
            row = db.execute(
                "SELECT * FROM projections WHERE watch_ref=?", (watch_ref,)).fetchone()
            if row is None:
                return None
            return {
                "version": row["version"], "observationId": row["observation_id"],
                "sourceAsOfUtc": row["source_asof"],
                "disposition": row["outcome"], "practiceAuthorised": False,
            }

    def pending_outbox(self) -> list[dict[str, Any]]:
        with self._connect() as db:
            rows = db.execute(
                "SELECT event_id,version,watch_ref,payload_json "
                "FROM outbox WHERE state='pending' ORDER BY rowid").fetchall()
            return [
                {"eventId": r["event_id"], "version": r["version"],
                 "watchRef": r["watch_ref"], **json.loads(r["payload_json"])}
                for r in rows
            ]

    def acknowledge_event(self, *, event_id: str,
                          expected_version: int, receipt_ref: str) -> None:
        _required({"receipt":receipt_ref},"receipt")
        with self._tx() as db:
            db.execute(
                "UPDATE outbox SET state='acknowledged',version=version+1,ack_ref=? "
                "WHERE event_id=? AND version=? AND state='pending'",
                (receipt_ref,event_id,expected_version))
            if db.execute("SELECT changes()").fetchone()[0] != 1:
                raise LedgerConflict("outbox acknowledgement conflict")

    def _save_versioned(self, head_table: str, event_table: str, id_field: str,
                        key: str, watch: str, version: int, data: Mapping[str, Any],
                        expected_version: int) -> None:
        if (type(version) is not int or version < 1
                or type(expected_version) is not int or expected_version < 0):
            raise LedgerConflict("invalid version")
        if version != expected_version+1 or not key or not watch:
            raise LedgerConflict("invalid transition version/identity")
        if event_table == "review_events" and data.get("practiceAuthorised") is not False:
            raise LedgerConflict("review cannot grant or imply practice authority")
        if event_table == "job_events" and data.get("emailEnabled") is not False:
            raise LedgerConflict("job cannot enable email")
        encoded = _json(data)
        with self._tx() as db:
            previous = db.execute(
                f"SELECT version,watch_ref FROM {head_table} WHERE {id_field}=?",
                (key,)).fetchone()
            actual = previous["version"] if previous is not None else 0
            if actual != expected_version or (
                    previous is not None and previous["watch_ref"] != watch):
                raise LedgerConflict("stale or cross-identity update")
            if previous is None:
                db.execute(
                    f"INSERT INTO {head_table} ({id_field},watch_ref,version,data_json)"
                    " VALUES (?,?,?,?)", (key,watch,version,encoded))
            else:
                db.execute(
                    f"UPDATE {head_table} SET version=?,data_json=? "
                    f"WHERE {id_field}=? AND version=?",
                    (version,encoded,key,expected_version))
                if db.execute("SELECT changes()").fetchone()[0] != 1:
                    raise LedgerConflict("concurrent state update")
            if event_table == "review_events":
                prior = db.execute(
                    "SELECT event_hash FROM review_events WHERE case_id=? "
                    "ORDER BY version DESC LIMIT 1", (key,)).fetchone()
                prev_hash = prior[0] if prior is not None else "0"*64
                event_hash = _sha(_json([key,version,prev_hash,_sha(encoded)]))
                db.execute("INSERT INTO review_events VALUES (?,?,?,?,?)",
                           (key,version,encoded,event_hash,prev_hash))
            else:
                db.execute("INSERT INTO job_events VALUES (?,?,?)",
                           (key,version,encoded))

    def save_review(self, record: Mapping[str, Any], *,
                    expected_version: int) -> None:
        self._save_versioned(
            "review_heads","review_events","case_id",
            _required(record,"caseId"),_required(record,"watchRef"),
            record.get("reviewVersion"),record,expected_version)

    def read_review(self, case_id: str) -> dict[str, Any] | None:
        with self._connect() as db:
            row = db.execute(
                "SELECT data_json FROM review_heads WHERE case_id=?",
                (case_id,)).fetchone()
            return json.loads(row[0]) if row is not None else None

    def save_job(self, record: Mapping[str, Any], *,
                 expected_version: int) -> None:
        self._save_versioned(
            "job_heads","job_events","job_id",
            _required(record,"jobId"),_required(record,"watchRef"),
            record.get("version"),record,expected_version)

    def read_job(self, job_id: str) -> dict[str, Any] | None:
        with self._connect() as db:
            row = db.execute(
                "SELECT data_json FROM job_heads WHERE job_id=?",
                (job_id,)).fetchone()
            return json.loads(row[0]) if row is not None else None

    def verify_integrity(self) -> bool:
        """Detect accidental corruption; hashes are NOT signatures or tamper proof."""
        with self._connect() as db:
            rows = db.execute(
                "SELECT * FROM observations ORDER BY watch_ref,seq").fetchall()
            last: dict[str,tuple[int,str]] = {}
            for row in rows:
                prev_seq,prev_hash = last.get(row["watch_ref"], (0,"0"*64))
                real_digest = _sha(row["payload_json"])
                expected = _sha(_json(
                    [row["watch_ref"],row["seq"],prev_hash,real_digest]))
                if (row["seq"] != prev_seq+1 or row["previous_hash"] != prev_hash
                        or row["payload_digest"] != real_digest
                        or row["event_hash"] != expected):
                    raise IntegrityFailure("observation history mismatch")
                last[row["watch_ref"]] = (row["seq"],row["event_hash"])
            heads = db.execute(
                "SELECT watch_ref,version,last_seq,event_hash FROM ledger_heads"
            ).fetchall()
            if len(heads) != len(last):
                raise IntegrityFailure("missing or extra watch head")
            for row in heads:
                seq,digest = last.get(row["watch_ref"], (None,None))
                if (row["version"] != seq or row["last_seq"] != seq
                        or row["event_hash"] != digest):
                    raise IntegrityFailure("watch head mismatch")
            for projection in db.execute("SELECT * FROM projections"):
                row = db.execute(
                    "SELECT observation_id,source_asof FROM observations "
                    "WHERE watch_ref=? AND seq=?",
                    (projection["watch_ref"],projection["seq"])).fetchone()
                if (row is None or row["observation_id"] != projection["observation_id"]
                        or row["source_asof"] != projection["source_asof"]):
                    raise IntegrityFailure("projection mismatches history")
            return True

    def recovery_manifest(self) -> dict[str, Any]:
        """Private-free counts and a required manual/native reconciliation signal."""
        with self._connect() as db:
            count = lambda table: db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            outstanding = db.execute(
                "SELECT COUNT(*) FROM outbox WHERE state='pending'").fetchone()[0]
            counts = {"observationCount":count("observations"),
                      "projectionCount":count("projections"),
                      "watchCount":count("ledger_heads"),
                      "jobCount":count("job_heads"),
                      "reviewCount":count("review_heads")}
        return {**counts, "outstandingEvents":outstanding,
                "integrityOK":self.verify_integrity(),
                "outboundEmailEnabled":False,
                "requiresNativeReconciliation":True}
