"""SQLite persistence for initiatives, linked tasks, decisions and snapshots."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

DECISION_ROUTES = {"local_qi", "executive_innovation", "research"}
DECISION_KINDS = {"sponsorship", "commencement", "data_access", "classification"}
SECTIONS = {"initiatives", "tasks", "events", "decisions", "snapshots"}


class RegisterError(ValueError):
    """Invalid, stale, or conflicting register input."""


def _decision_time(record: dict, field: str) -> datetime | None:
    value = record.get(field)
    if value is None:
        return None
    try:
        stamp = datetime.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise RegisterError(f"{field} must be an ISO 8601 UTC timestamp") from exc
    if stamp.utcoffset() != timedelta(0):
        raise RegisterError(f"{field} must be UTC")
    return stamp


class Register:
    """A small local register. Source imports are atomic and replay-safe."""

    def __init__(self, path: str | Path):
        self.path = str(path)
        self.db = sqlite3.connect(self.path)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys = ON")
        self._schema()

    def close(self) -> None:
        self.db.close()

    def __enter__(self) -> Register:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def _schema(self) -> None:
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS initiatives (
            initiative_id TEXT PRIMARY KEY, source_key TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL, revision INTEGER NOT NULL CHECK(revision >= 1), payload TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS tasks (
            task_id TEXT PRIMARY KEY, source_key TEXT NOT NULL UNIQUE,
            initiative_id TEXT NOT NULL REFERENCES initiatives(initiative_id),
            title TEXT NOT NULL, revision INTEGER NOT NULL CHECK(revision >= 1), payload TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS events (
            event_id TEXT PRIMARY KEY, source_key TEXT NOT NULL UNIQUE,
            initiative_id TEXT NOT NULL REFERENCES initiatives(initiative_id),
            event_type TEXT NOT NULL, effective_at TEXT NOT NULL, payload TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS feed_health (feed TEXT PRIMARY KEY, last_good TEXT, status TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS decisions (
            decision_id TEXT PRIMARY KEY, source_key TEXT NOT NULL UNIQUE,
            initiative_id TEXT NOT NULL REFERENCES initiatives(initiative_id),
            decision_kind TEXT NOT NULL CHECK(decision_kind IN ('sponsorship','commencement','data_access','classification')),
            route TEXT NOT NULL CHECK(route IN ('local_qi','executive_innovation','research')),
            reviewer TEXT NOT NULL, outcome TEXT NOT NULL, payload TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS snapshots (
            snapshot_id TEXT PRIMARY KEY, source_key TEXT NOT NULL UNIQUE,
            initiative_id TEXT NOT NULL REFERENCES initiatives(initiative_id),
            kind TEXT NOT NULL CHECK(kind IN ('benefit','adoption')),
            observed_at TEXT NOT NULL, payload TEXT NOT NULL
        );
        """)
        # Upgrade the first local prototype additively; retain prior rows and label
        # decisions whose original kind was not captured instead of guessing.
        for table, field, declaration in (
            ("initiatives", "revision", "INTEGER NOT NULL DEFAULT 1"),
            ("tasks", "revision", "INTEGER NOT NULL DEFAULT 1"),
            ("events", "effective_at", "TEXT"),
            ("decisions", "decision_kind", "TEXT NOT NULL DEFAULT 'legacy_unclassified'"),
        ):
            columns = {row["name"] for row in self.db.execute(f"PRAGMA table_info({table})")}
            if field not in columns:
                self.db.execute(f"ALTER TABLE {table} ADD COLUMN {field} {declaration}")

    @staticmethod
    def _json(value: Any) -> str:
        return json.dumps(value, sort_keys=True, separators=(",", ":"))

    @staticmethod
    def _required(record: dict[str, Any], *fields: str) -> None:
        missing = [key for key in fields if not record.get(key)]
        if missing:
            raise RegisterError("Missing required fields: " + ", ".join(missing))

    def _upsert_revision(self, table: str, id_field: str, source_key: str,
                         immutable: tuple[tuple[str, Any], ...], record: dict[str, Any]) -> int:
        """Create at revision 1 or update an existing row at exactly the next revision."""
        payload = self._json(record)
        revision = record.get("revision", 1)
        if type(revision) is not int or revision < 1:
            raise RegisterError("revision must be a positive integer")
        found = self.db.execute(f"SELECT * FROM {table} WHERE source_key=?", (source_key,)).fetchone()
        if found:
            if found[id_field] != record[id_field]:
                raise RegisterError(f"Source key {source_key!r} cannot change its immutable ID")
            if any(found[field] != value for field, value in immutable):
                raise RegisterError(f"Source row {source_key!r} cannot change its immutable parent")
            if revision == found["revision"]:
                if found["payload"] != payload:
                    raise RegisterError(f"Source key {source_key!r} revision {revision} conflicts with stored content")
                return 0
            expected = found["revision"] + 1
            if revision != expected:
                reason = "stale" if revision < expected else "skips the next revision"
                raise RegisterError(f"Source key {source_key!r} revision {revision} {reason}; expected {expected}")
            assignments = [f"{field}=?" for field, _ in immutable]
            assignments.extend(("title=?", "revision=?", "payload=?"))
            values = [value for _, value in immutable]
            values.extend((record["title"], revision, payload, source_key))
            self.db.execute(f"UPDATE {table} SET {','.join(assignments)} WHERE source_key=?", values)
            return 1
        if revision != 1:
            raise RegisterError(f"New source key {source_key!r} must start at revision 1")
        fields = [id_field, "source_key", *(field for field, _ in immutable), "title", "revision", "payload"]
        values = [record[id_field], source_key, *(value for _, value in immutable), record["title"], revision, payload]
        self.db.execute(f"INSERT INTO {table} ({','.join(fields)}) VALUES ({','.join('?' for _ in fields)})", values)
        return 1

    def _insert(self, table: str, source_key: str, fields: tuple[str, ...],
                values: tuple[Any, ...], record: dict[str, Any]) -> int:
        """Insert an immutable append-only record; identical replays are no-ops."""
        found = self.db.execute(f"SELECT payload FROM {table} WHERE source_key=?", (source_key,)).fetchone()
        payload = self._json(record)
        if found:
            if found["payload"] != payload:
                raise RegisterError(f"Source key {source_key!r} was replayed with different content")
            return 0
        self.db.execute(f"INSERT INTO {table} ({','.join(fields)}) VALUES ({','.join('?' for _ in values)})", values)
        return 1

    def import_data(self, data: dict[str, Any], *, feed_receipt: tuple[str, str] | None = None) -> dict[str, int]:
        """Import one strict JSON packet atomically; omitted sections never delete data."""
        if not isinstance(data, dict):
            raise RegisterError("Import must be a JSON object")
        unknown = set(data) - SECTIONS
        if unknown:
            raise RegisterError("Unknown import sections: " + ", ".join(sorted(unknown)))
        for name, records in data.items():
            if not isinstance(records, list):
                raise RegisterError(f"Section {name!r} must be a list")
            if any(not isinstance(record, dict) for record in records):
                raise RegisterError(f"Section {name!r} entries must be objects")

        counts = {name: 0 for name in SECTIONS}
        try:
            with self.db:
                for r in data.get("initiatives", []):
                    self._required(r, "initiative_id", "source_key", "title")
                    counts["initiatives"] += self._upsert_revision("initiatives", "initiative_id", r["source_key"], (), r)
                for r in data.get("tasks", []):
                    self._required(r, "task_id", "source_key", "initiative_id", "title")
                    counts["tasks"] += self._upsert_revision("tasks", "task_id", r["source_key"], (("initiative_id", r["initiative_id"]),), r)
                for r in data.get("events", []):
                    self._required(r, "event_id", "source_key", "initiative_id", "event_type")
                    if not (r.get("effective_at") or r.get("observed_at")):
                        raise RegisterError("Events require effective_at or observed_at")
                    effective_at = r.get("effective_at") or r.get("observed_at")
                    if not isinstance(effective_at, str):
                        raise RegisterError("Event timestamps must be strings")
                    counts["events"] += self._insert("events", r["source_key"],
                        ("event_id", "source_key", "initiative_id", "event_type", "effective_at", "payload"),
                        (r["event_id"], r["source_key"], r["initiative_id"], r["event_type"], effective_at, self._json(r)), r)
                for r in data.get("decisions", []):
                    self._required(r, "decision_id", "source_key", "initiative_id", "decision_kind", "route", "reviewer", "outcome")
                    if r["route"] not in DECISION_ROUTES:
                        raise RegisterError(f"Unknown governance route: {r['route']}")
                    if r["decision_kind"] not in DECISION_KINDS:
                        raise RegisterError(f"Unknown decision kind: {r['decision_kind']}")
                    submitted = _decision_time(r, "submitted_at")
                    decided = _decision_time(r, "decided_at")
                    if decided and r["outcome"] in ("pending", "under_review"):
                        raise RegisterError("An open decision cannot have a decision time")
                    if submitted and decided and decided < submitted:
                        raise RegisterError("Decision time precedes submission")
                    counts["decisions"] += self._insert("decisions", r["source_key"],
                        ("decision_id", "source_key", "initiative_id", "decision_kind", "route", "reviewer", "outcome", "payload"),
                        (r["decision_id"], r["source_key"], r["initiative_id"], r["decision_kind"], r["route"], r["reviewer"], r["outcome"], self._json(r)), r)
                for r in data.get("snapshots", []):
                    self._required(r, "snapshot_id", "source_key", "initiative_id", "kind", "observed_at")
                    if not isinstance(r["observed_at"], str):
                        raise RegisterError("Snapshot observed_at must be a string")
                    if r["kind"] not in ("benefit", "adoption"):
                        raise RegisterError("Snapshot kind must be benefit or adoption")
                    counts["snapshots"] += self._insert("snapshots", r["source_key"],
                        ("snapshot_id", "source_key", "initiative_id", "kind", "observed_at", "payload"),
                        (r["snapshot_id"], r["source_key"], r["initiative_id"], r["kind"], r["observed_at"], self._json(r)), r)
                if feed_receipt:
                    self.db.execute("""INSERT INTO feed_health VALUES (?, ?, 'ok')
                        ON CONFLICT(feed) DO UPDATE SET last_good=excluded.last_good, status=excluded.status""", feed_receipt)
        except sqlite3.IntegrityError as exc:
            raise RegisterError(f"Import rejected; transaction rolled back: {exc}") from exc
        return counts

    def report(self) -> list[dict[str, Any]]:
        """Return initiative/task counts separately and label snapshots as observations."""
        rows = self.db.execute("""
            SELECT i.initiative_id,i.source_key,i.title,i.revision,
              (SELECT count(*) FROM tasks t WHERE t.initiative_id=i.initiative_id) AS task_count,
              (SELECT count(*) FROM events e WHERE e.initiative_id=i.initiative_id) AS event_count,
              (SELECT count(*) FROM decisions d WHERE d.initiative_id=i.initiative_id) AS decision_count,
              (SELECT count(*) FROM snapshots s WHERE s.initiative_id=i.initiative_id AND s.kind='benefit') AS benefit_observations,
              (SELECT count(*) FROM snapshots s WHERE s.initiative_id=i.initiative_id AND s.kind='adoption') AS adoption_observations
            FROM initiatives i ORDER BY i.initiative_id
        """).fetchall()
        reports = [dict(row) for row in rows]
        for report in reports:
            service_ids = self.db.execute(
                "SELECT payload FROM snapshots WHERE initiative_id=? AND kind='adoption'",
                (report["initiative_id"],),
            ).fetchall()
            report["adopted_services"] = len({
                service_id for row in service_ids
                if (snapshot := json.loads(row["payload"]))
                and (snapshot.get("status") == "adopted" or (snapshot.get("adopted_count") or 0) > 0)
                and (service_id := snapshot.get("service_id"))
            })
        return reports

    def export_rows(self, kind: str) -> list[dict[str, Any]]:
        """Flatten one append-only record family for CSV process/report consumers."""
        configs = {
            "events": ("events", ("event_id", "source_key", "initiative_id", "event_type", "effective_at")),
            "observations": ("snapshots", ("snapshot_id", "source_key", "initiative_id", "kind", "observed_at")),
            "decisions": ("decisions", ("decision_id", "source_key", "initiative_id", "decision_kind", "route", "reviewer", "outcome")),
        }
        if kind not in configs:
            raise RegisterError("Export kind must be events, observations, or decisions")
        table, core_fields = configs[kind]
        rows = self.db.execute(f"SELECT * FROM {table} ORDER BY source_key").fetchall()
        flattened = []
        for row in rows:
            values = dict(row)
            payload = json.loads(values.pop("payload"))
            flattened.append({**{field: values[field] for field in core_fields},
                              **{key: value for key, value in payload.items() if key not in core_fields}})
        return flattened
