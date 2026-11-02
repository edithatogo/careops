import hashlib
import unittest
from scripts.ppg_currency_notice_sections import extract_updates


class NoticeSectionsTests(unittest.TestCase):
    header = '<tr><th>Active Ingredient</th><th>Brand name Sponsor</th><th>PI updates (sections updated)</th><th>Date of approval</th></tr>'
    row = '<tr><td>ambermedicine</td><td>Amber &amp; Co</td><td><p>Added warning</p><ul><li>Route-specific risk</li></ul></td><td>2026-10-01</td></tr>'

    def read(self, html):
        raw = html.encode()
        return extract_updates(raw, hashlib.sha256(raw).hexdigest())

    def test_extracts_complete_rows_without_matching_policies(self):
        rows = self.read('<table>' + self.header + self.row + '</table>')
        self.assertEqual(rows, [dict(row=1, ingredient='ambermedicine', brandAndSponsor='Amber & Co',
                                    changes='Added warning Route-specific risk', approvedAtRaw='2026-10-01')])
        self.assertNotIn('policy', rows[0])

    def test_bulletins_keep_same_ingredient_rows_separate(self):
        rows = self.read('<table>' + self.header + self.row + self.row.replace('Amber &amp; Co', 'Other presentation') + '</table>')
        self.assertEqual(len(rows), 2)
        self.assertEqual([r['row'] for r in rows], [1, 2])
        self.assertNotEqual(rows[0]['brandAndSponsor'], rows[1]['brandAndSponsor'])

    def test_hash_mismatch_is_not_review_evidence(self):
        with self.assertRaisesRegex(ValueError, 'preimage'):
            extract_updates(b'<table></table>', 'a' * 64)

    def test_unrelated_tables_and_empty_capture_produce_no_updates(self):
        self.assertEqual(self.read('<table><tr><th>Site menu</th></tr></table>'), [])
        self.assertEqual(self.read('No table'), [])

    def test_missing_cells_or_changes_are_held(self):
        for row in (self.row.replace('<td>2026-10-01</td>', ''), self.row.replace('ambermedicine', '')):
            with self.subTest(row=row), self.assertRaisesRegex(ValueError, 'Incomplete'):
                self.read('<table>' + self.header + row + '</table>')

    def test_merged_nested_or_changed_layout_is_held(self):
        for row in (self.row.replace('<td>ambermedicine', '<td rowspan="2">ambermedicine'),
                    self.row.replace('Added warning', '<table><tr><td>Nested warning</td></tr></table>'),
                    self.row.replace('</td><td>Amber', '<td>Amber')):
            with self.subTest(row=row), self.assertRaisesRegex(ValueError, 'layout'):
                self.read('<table>' + self.header + row + '</table>')
        with self.assertRaisesRegex(ValueError, 'layout'):
            self.read('<table>' + self.header.replace('Date of approval', 'Unknown field') + self.row + '</table>')

    def test_truncated_capture_is_held(self):
        with self.assertRaisesRegex(ValueError, 'Incomplete'):
            self.read('<table>' + self.header + self.row)


if __name__ == '__main__':
    unittest.main()
