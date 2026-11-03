"""Fictional local register cases; no operational records are used."""

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from careops_improvement import Register, RegisterError


PACKET = {
    "initiatives": [{"initiative_id": "I-001", "source_key": "demo:initiative:1", "title": "Reduce fictional wait", "revision": 1}],
    "tasks": [
        {"task_id": "T-001", "source_key": "demo:task:1", "initiative_id": "I-001", "title": "Map fictional process", "revision": 1},
        {"task_id": "T-002", "source_key": "demo:task:2", "initiative_id": "I-001", "title": "Trial fictional change", "revision": 1},
    ],
    "events": [{"event_id": "E-001", "source_key": "demo:event:1", "initiative_id": "I-001", "event_type": "created", "effective_at": "2026-01-01T00:00:00Z"}],
    "decisions": [{"decision_id": "D-001", "source_key": "demo:decision:1", "initiative_id": "I-001", "decision_kind": "sponsorship", "route": "local_qi", "reviewer": "Fictional QI lead", "outcome": "approved"}],
    "snapshots": [
        {"snapshot_id": "B-001", "source_key": "demo:benefit:1", "initiative_id": "I-001", "kind": "benefit", "observed_at": "2026-01-01", "measure": "minutes"},
        {"snapshot_id": "A-001", "source_key": "demo:adoption:1", "initiative_id": "I-001", "kind": "adoption", "observed_at": "2026-01-01", "rate": 0.5},
    ],
}


class RegisterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.register = Register(Path(self.temp.name) / "register.sqlite")
        self.addCleanup(self.register.close)

    def test_replay_is_idempotent_and_tasks_are_separate_from_initiatives(self):
        first = self.register.import_data(PACKET)
        second = self.register.import_data(json.loads(json.dumps(PACKET)))
        self.assertEqual(first, {"initiatives": 1, "tasks": 2, "events": 1, "decisions": 1, "snapshots": 2})
        self.assertEqual(second, {key: 0 for key in first})
        self.assertEqual(self.register.report(), [{
            "initiative_id": "I-001", "source_key": "demo:initiative:1", "title": "Reduce fictional wait",
            "revision": 1, "task_count": 2, "event_count": 1, "decision_count": 1,
            "benefit_observations": 1, "adoption_observations": 1, "adopted_services": 0,
        }])

    def test_invalid_decision_chronology_rolls_back_packet(self):
        for fields in (
            {"outcome": "pending", "decided_at": "2026-01-02T00:00:00Z"},
            {"outcome": "under_review", "decided_at": "2026-01-02T00:00:00Z"},
            {"submitted_at": "2026-01-03T00:00:00Z", "decided_at": "2026-01-02T00:00:00Z"},
            {"submitted_at": "2026-01-01"},
            {"decided_at": "invalid"},
        ):
            with self.subTest(fields=fields):
                packet = json.loads(json.dumps(PACKET))
                packet["decisions"][0].update(fields)
                with self.assertRaises(RegisterError):
                    self.register.import_data(packet)
                self.assertEqual(self.register.report(), [])

    def test_duplicate_source_key_with_changed_content_is_rejected(self):
        self.register.import_data(PACKET)
        changed = json.loads(json.dumps(PACKET))
        changed["events"][0]["event_type"] = "closed"
        with self.assertRaises(RegisterError):
            self.register.import_data(changed)
        self.assertEqual(self.register.report()[0]["event_count"], 1)

    def test_failed_packet_rolls_back_prior_rows_and_preserves_last_good_state(self):
        self.register.import_data(PACKET)
        bad = {"initiatives": [{"initiative_id": "I-002", "source_key": "demo:initiative:2", "title": "Should roll back"}],
               "tasks": [{"task_id": "T-X", "source_key": "demo:task:x", "initiative_id": "missing", "title": "Broken link"}]}
        with self.assertRaises(RegisterError):
            self.register.import_data(bad)
        self.assertEqual([r["initiative_id"] for r in self.register.report()], ["I-001"])

    def test_governance_route_requires_explicit_reviewer(self):
        bad = {"initiatives": PACKET["initiatives"], "decisions": [{
            "decision_id": "D-X", "source_key": "demo:decision:x", "initiative_id": "I-001",
            "decision_kind": "sponsorship", "route": "executive_innovation", "outcome": "approved",
        }]}
        with self.assertRaises(RegisterError):
            self.register.import_data(bad)

    def test_revision_update_and_exact_replay(self):
        self.register.import_data(PACKET)
        update = {"initiatives": [{**PACKET["initiatives"][0], "revision": 2, "title": "Renamed fictional wait"}],
                  "tasks": [{**PACKET["tasks"][0], "revision": 2, "title": "Updated fictional map"}]}
        updated = self.register.import_data(update)
        self.assertEqual((updated["initiatives"], updated["tasks"]), (1, 1))
        replayed = self.register.import_data(update)
        self.assertEqual((replayed["initiatives"], replayed["tasks"]), (0, 0))
        report = self.register.report()[0]
        self.assertEqual((report["title"], report["revision"], report["task_count"]), ("Renamed fictional wait", 2, 2))
        task = self.register.db.execute("SELECT title,revision FROM tasks WHERE task_id='T-001'").fetchone()
        self.assertEqual(tuple(task), ("Updated fictional map", 2))

    def test_stale_conflicting_and_reassigned_parent_updates_are_rejected(self):
        self.register.import_data(PACKET)
        self.register.import_data({"initiatives": [{**PACKET["initiatives"][0], "revision": 2, "title": "Revision two"}]})
        stale = {"initiatives": [{**PACKET["initiatives"][0], "title": "Original title"}]}
        conflict = {"initiatives": [{**PACKET["initiatives"][0], "revision": 2, "title": "Different revision two"}]}
        reassigned = {"tasks": [{**PACKET["tasks"][0], "initiative_id": "I-OTHER", "revision": 2, "title": "Move parent"}]}
        for data in (stale, conflict, reassigned):
            with self.subTest(data=data), self.assertRaises(RegisterError):
                self.register.import_data(data)

    def test_unknown_sections_and_bad_shapes_fail_closed(self):
        for data in ({"extra": []}, {"initiatives": {}}, {"tasks": ["not an object"]}):
            with self.subTest(data=data), self.assertRaises(RegisterError):
                self.register.import_data(data)

    def test_event_requires_timestamp_and_decision_kind_is_typed(self):
        missing_time = {"initiatives": PACKET["initiatives"], "events": [{
            "event_id": "E-X", "source_key": "demo:event:x", "initiative_id": "I-001", "event_type": "opened",
        }]}
        bad_kind = {"initiatives": PACKET["initiatives"], "decisions": [{
            "decision_id": "D-X", "source_key": "demo:decision:x", "initiative_id": "I-001",
            "decision_kind": "general", "route": "local_qi", "reviewer": "Fictional reviewer", "outcome": "noted",
        }]}
        with self.assertRaises(RegisterError):
            self.register.import_data(missing_time)
        with self.assertRaises(RegisterError):
            self.register.import_data(bad_kind)

    def test_adoption_observations_and_distinct_services_are_reported_separately(self):
        packet = json.loads(json.dumps(PACKET))
        packet["snapshots"][0].pop("service_id", None)
        packet["snapshots"][1].update(service_id="service-a", adopted_count=1)
        packet["snapshots"].append({"snapshot_id": "A-002", "source_key": "demo:adoption:2",
                                    "initiative_id": "I-001", "kind": "adoption",
                                    "observed_at": "2026-02-01", "service_id": "service-a", "adopted_count": 2, "rate": 0.7})
        packet["snapshots"].append({"snapshot_id": "A-003", "source_key": "demo:adoption:3",
                                    "initiative_id": "I-001", "kind": "adoption",
                                    "observed_at": "2026-03-01", "service_id": "service-b", "status": "adopted", "rate": 0.8})
        self.register.import_data(packet)
        report = self.register.report()[0]
        self.assertEqual(report["adoption_observations"], 3)
        self.assertEqual(report["adopted_services"], 2)
        rows = self.register.export_rows("observations")
        self.assertEqual(len(rows), 4)
        self.assertIn("snapshot_id", rows[0])

    def test_additive_migration_preserves_legacy_rows_without_guessing_decision_kind(self):
        self.register.close()
        legacy_path = Path(self.temp.name) / "legacy.sqlite"
        db = sqlite3.connect(legacy_path)
        db.executescript("""
            CREATE TABLE initiatives(initiative_id TEXT PRIMARY KEY, source_key TEXT UNIQUE, title TEXT, payload TEXT);
            CREATE TABLE tasks(task_id TEXT PRIMARY KEY, source_key TEXT UNIQUE, initiative_id TEXT, title TEXT, payload TEXT);
            CREATE TABLE events(event_id TEXT PRIMARY KEY, source_key TEXT UNIQUE, initiative_id TEXT, event_type TEXT, payload TEXT);
            CREATE TABLE decisions(decision_id TEXT PRIMARY KEY, source_key TEXT UNIQUE, initiative_id TEXT, route TEXT, reviewer TEXT, outcome TEXT, payload TEXT);
            CREATE TABLE snapshots(snapshot_id TEXT PRIMARY KEY, source_key TEXT UNIQUE, initiative_id TEXT, kind TEXT, observed_at TEXT, payload TEXT);
            INSERT INTO initiatives VALUES('I-old','old:initiative','Legacy title','{"initiative_id":"I-old","source_key":"old:initiative","title":"Legacy title"}');
            INSERT INTO decisions VALUES('D-old','old:decision','I-old','local_qi','Reviewer','noted','{"decision_id":"D-old"}');
        """)
        db.close()
        with Register(legacy_path) as upgraded:
            self.assertEqual(upgraded.report()[0]["revision"], 1)
            decision = upgraded.db.execute("SELECT decision_kind FROM decisions WHERE decision_id='D-old'").fetchone()
            self.assertEqual(decision["decision_kind"], "legacy_unclassified")
            self.assertEqual(upgraded.db.execute("SELECT count(*) FROM initiatives").fetchone()[0], 1)


if __name__ == "__main__":
    unittest.main()
