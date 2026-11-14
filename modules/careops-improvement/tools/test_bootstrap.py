"""Focused bootstrap planning regression cases."""
import unittest
from bootstrap import plan


class BootstrapTests(unittest.TestCase):
    def test_repeat_is_noop_and_updates_need_review(self):
        record = {"key": "initiatives", "type": "SharePointList"}
        self.assertEqual(plan({"resources": [record]}, {"resources": []})[0]["action"], "create")
        self.assertEqual(plan({"resources": [record]}, {"resources": [record]})[0]["action"], "unchanged")
        changed = dict(record, title="Renamed")
        self.assertEqual(plan({"resources": [changed]}, {"resources": [record]})[0]["action"], "review_update")

    def test_duplicate_identity_is_rejected(self):
        with self.assertRaises(ValueError):
            plan({"resources": [{"key": "a"}, {"key": "a"}]}, {"resources": []})


if __name__ == "__main__":
    unittest.main()
