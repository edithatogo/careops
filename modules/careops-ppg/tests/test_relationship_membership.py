import unittest
from scripts.ppg_relationship_membership import prepare


class MembershipTests(unittest.TestCase):
    def test_existing_review_preserved_and_new_record_is_incomplete(self):
        catalogue = [{'DocumentUID': 'old', 'sourceDocumentId': 'A', 'Title': 'Old'},
                     {'DocumentUID': 'new', 'sourceDocumentId': 'B', 'Title': 'New'}]
        existing = [{'DocumentUID': 'old', 'SourceDocumentId': 'A', 'AssessmentKey': 'key',
                     'AssessmentComplete': True, 'HumanNote': 'Preserve'}]
        result = prepare(catalogue, existing, [], {"new": "Active source snapshot"})
        self.assertEqual(len(result['creates']), 1)
        row = result['creates'][0]
        self.assertFalse(row['AssessmentComplete'])
        self.assertFalse(row['CurrentAuthorityVerified'])
        self.assertEqual(row['SourceCount'], 0)
        self.assertTrue(existing[0]['AssessmentComplete'])
        replay = prepare(catalogue, existing + [row], [])
        self.assertEqual(replay['creates'], [])

    def test_identity_drift_and_duplicate_uids_fail_explicitly(self):
        catalogue = [{'DocumentUID': 'one', 'sourceDocumentId': 'B', 'Title': 'Changed'}]
        existing = [{'DocumentUID': 'one', 'SourceDocumentId': 'A', 'AssessmentKey': 'key'}]
        self.assertTrue(prepare(catalogue, existing, [], {"new": "Active source snapshot"})['conflicts'])
        with self.assertRaises(ValueError):
            prepare(catalogue * 2, [], [])

    def test_relationship_directions_and_retired_rows_remain_distinct(self):
        row = {'DocumentUID': 'new', 'sourceDocumentId': 'B', 'Title': 'New'}
        old = {'DocumentUID': 'retained', 'SourceDocumentId': 'A', 'AssessmentKey': 'key'}
        rel = {'RelationshipKey': 'r', 'FromDocumentUID': 'retained', 'ToDocumentUID': 'new'}
        result = prepare([row], [old], [rel], {"new": "Retained outside source snapshot"})
        self.assertEqual(result['creates'][0]['SourceMembership'], 'Retained outside source snapshot')
        self.assertTrue(prepare([row], [old], [rel])['conflicts'])
        self.assertEqual(result['retainedOutsideCatalogue'], ['retained'])
        self.assertEqual(result['creates'][0]['ExistingIncomingCount'], 1)
        self.assertEqual(result['creates'][0]['ExistingOutgoingCount'], 0)
