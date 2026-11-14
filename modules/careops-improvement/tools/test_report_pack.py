import unittest
from report_pack import render


class PackTests(unittest.TestCase):
    def test_projection_count_and_html_escape(self):
        row = {"initiative_id": "I1", "title": "<script>", "task_count": 5,
               "decision_count": 1, "adoption_observations": 2}
        summary, page = render([row], "2026-11")
        self.assertEqual(summary["initiatives"], 1)
        self.assertEqual(summary["tasks"], 5)
        self.assertEqual(summary["adoption_observations"], 2)
        self.assertNotIn("<script>", page)
        with self.assertRaises(ValueError):
            render([row, row], "2026-11")
