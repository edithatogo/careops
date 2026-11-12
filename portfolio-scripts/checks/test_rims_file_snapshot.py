"""Fictional standard-library typed snapshot and readback tests."""
import importlib.util
from pathlib import Path
import unittest

script = Path(__file__).resolve().parents[1] / "rims_file_snapshot.py"
spec = importlib.util.spec_from_file_location("rims_file_snapshot", script)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.fields = [
            {"name": "id", "type": "string"},
            {"name": "count", "type": "integer"},
            {"name": "observed_utc", "type": "string", "format": "date-time"},
            {"name": "contributors", "type": "array", "nullable": True}]
        self.rows = [{"id": "fictional", "count": 0,
                      "observed_utc": "2026-11-10T00:00:00Z",
                      "contributors": [{"id": "author-fictional"}]}]
        self.snapshot = mod.build("fictional-source", "synthetic-run", self.rows, self.fields,
                                  captured_utc="2026-11-10T00:00:00Z",
                                  source_revision="v1", complete=True)

    def test_typed_nested_roundtrip(self):
        s = self.snapshot
        self.assertEqual(s["rows"]["rows"], self.rows)
        self.assertEqual(s["json_schema"]["items"]["properties"]["observed_utc"]["format"], "date-time")
        result = mod.verify_readback(s, persisted_rows=s["rows"], persisted_schema=s["json_schema"])
        self.assertTrue(result["readback_valid"])
        self.assertFalse(result["native_commit_authorised"])

    def test_schema_declares_required_and_logical_decimal(self):
        fields = self.fields + [{
            "name": "amount", "type": "string", "logical_type": "decimal"
        }]
        rows = [{**self.rows[0], "amount": "1200.50"}]
        result = mod.build(
            "source", "run", rows, fields,
            captured_utc="2026-11-10T00:00:00Z",
            source_revision="v1", complete=True,
        )
        item = result["json_schema"]["items"]
        self.assertIn("amount", item["required"])
        self.assertEqual(
            item["properties"]["amount"]["x-rims-logical-type"], "decimal"
        )

    def test_invalid_exact_decimal_and_timestamp_are_refused(self):
        fields = self.fields + [{
            "name": "amount", "type": "string", "logical_type": "decimal"
        }]
        for amount in ("1e6", "01.5", "NaN", "+1"):
            with self.subTest(amount=amount), self.assertRaises(ValueError):
                mod.build(
                    "source", "run",
                    [{**self.rows[0], "amount": amount}], fields,
                    captured_utc="2026-11-10T00:00:00Z",
                    source_revision="v1", complete=True,
                )
        with self.assertRaises(ValueError):
            mod.build(
                "source", "run",
                [{**self.rows[0], "observed_utc": "2026-11-10T00:00:00"}],
                self.fields, captured_utc="2026-11-10T00:00:00Z",
                source_revision="v1", complete=True,
            )

    def test_naive_capture_timestamp_refused(self):
        with self.assertRaises(ValueError):
            mod.build(
                "source", "run", self.rows, self.fields,
                captured_utc="2026-11-10T00:00:00",
                source_revision="v1", complete=True,
            )

    def test_native_byte_readback_verification(self):
        byte_files = mod.render_bytes(self.snapshot)
        receipt = mod.verify_byte_readback(
            self.snapshot,
            persisted_rows_bytes=byte_files["rows.json"],
            persisted_schema_bytes=byte_files["schema.json"],
        )
        self.assertTrue(receipt["readback_valid"])
        self.assertFalse(receipt["native_commit_authorised"])
        with self.assertRaises(ValueError):
            mod.verify_byte_readback(
                self.snapshot,
                persisted_rows_bytes=byte_files["rows.json"] + b" ",
                persisted_schema_bytes=byte_files["schema.json"],
            )

    def test_incomplete_refused(self):
        with self.assertRaises(ValueError):
            mod.build("source", "run", self.rows, self.fields, captured_utc="now",
                      source_revision="v1", complete=False)

    def test_type_mismatch_refused(self):
        bad = [{**self.rows[0], "count": "0"}]
        with self.assertRaises(ValueError):
            mod.build("source", "run", bad, self.fields, captured_utc="2026-11-10T00:00:00Z",
                      source_revision="v1", complete=True)

    def test_undeclared_fields_refused(self):
        bad = [{**self.rows[0], "unmapped": "source field"}]
        with self.assertRaises(ValueError):
            mod.build("source", "run", bad, self.fields, captured_utc="2026-11-10T00:00:00Z",
                      source_revision="v1", complete=True)

    def test_tampered_readback_refused(self):
        changed = {**self.snapshot["rows"], "rows": [{**self.rows[0], "count": 12}]}
        with self.assertRaises(ValueError):
            mod.verify_readback(self.snapshot, persisted_rows=changed,
                                persisted_schema=self.snapshot["json_schema"])


if __name__ == "__main__":
    unittest.main()
