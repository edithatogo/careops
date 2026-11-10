"""Fictional SQLite cache tests; no tenant or private data."""
import importlib.util
from pathlib import Path
import sqlite3
import tempfile
import unittest

root = Path(__file__).resolve().parents[1]
def load(name):
    spec = importlib.util.spec_from_file_location(name, root / (name + ".py"))
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

snap = load("rims_file_snapshot")
cache = load("rims_sqlite_cache")


class SQLiteTests(unittest.TestCase):
    def setUp(self):
        self.bundle = snap.build(
            "fictional", "run-1",
            [{"publication_id": "synthetic", "count": 2,
              "authors": [{"name": "fictional"}]}],
            [{"name": "publication_id", "type": "string"},
             {"name": "count", "type": "integer"},
             {"name": "authors", "type": "array"}],
            captured_utc="2026-11-10T00:00:00Z",
            source_revision="v1", complete=True)

    def test_no_commit_proof_refuses(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(cache.CacheRefused):
                cache.materialize(self.bundle, Path(d) / "a.sqlite")

    def test_verified_cache_has_types_and_metadata(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "a.sqlite"
            result = cache.materialize(
                self.bundle, path, verify_committed=lambda manifest: True)
            self.assertEqual(result["row_count"], 1)
            with sqlite3.connect(path) as c:
                self.assertEqual(c.execute("SELECT count FROM records").fetchone()[0], 2)
                self.assertIn("fictional", c.execute("SELECT authors FROM records").fetchone()[0])
                self.assertIn("json_schema", dict(c.execute("SELECT key,value FROM metadata")))
            with self.assertRaises(cache.CacheRefused):
                cache.materialize(self.bundle, path, verify_committed=lambda manifest: True)


if __name__ == "__main__":
    unittest.main()
