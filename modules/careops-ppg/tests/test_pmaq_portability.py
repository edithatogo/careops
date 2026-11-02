import json
import unittest
from pathlib import Path

from scripts.ppg_pmaq_portability import prepare


class Portability(unittest.TestCase):
    def setUp(self):
        self.fixture, self.contract, self.vocabulary = [
            json.loads(Path(name).read_text()) for name in (
                'tests/fixtures/accreditation/pmaq-pgy1.json',
                'config/accreditation-contract-v2.json',
                'config/accreditation-scheme-vocabularies-v1.json')]

    def test_separate_judgements_and_authorities(self):
        out = prepare(self.fixture, self.contract, self.vocabulary)['rows']
        self.assertEqual({r['Outcome'] for r in out['assessment']}, {'Unknown'})
        self.assertEqual(len({r['ReviewContextKey'] for r in out['assessment']}), 2)
        self.assertEqual({r['MappingState'] for r in out['mapping']}, {'Proposed'})
        config = json.loads(out['framework'][0]['Scheme_x0020_configuration'])['payload']
        self.assertNotEqual(config['scheme']['schemeAuthorityKey'], config['scheme']['assessmentDecisionAuthorityKey'])
        self.assertEqual(config['ratingVocabularies'][0]['values'],
                         ['Fully met', 'Partially met', 'Not met', 'Not applicable'])

    def test_conflicted_source_cannot_replace_amc_clause(self):
        self.fixture['graph']['requirements'][0]['source']['sha256'] = self.fixture['sourceConflict']['sha256']
        with self.assertRaisesRegex(ValueError, 'Requirement source mismatch'):
            prepare(self.fixture, self.contract, self.vocabulary)
