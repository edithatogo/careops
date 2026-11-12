"""Synthetic tests for CHHHS publication-analysis release gates."""
import importlib.util
from pathlib import Path
import unittest

script = Path(__file__).resolve().parents[1] / "rims_rapid_analysis.py"
spec = importlib.util.spec_from_file_location("rims_rapid_analysis", script)
rapid = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rapid)


def row(**kw):
    r = {
        'CanonicalKey': 'PUB:a', 'ReviewStatus': 'Included', 'Title': 'A melioidosis study',
        'PublicationYear': '2,024', 'DOI': '10.1234/A', 'PMID': '1234567',
        'MatchedFacilities': 'Cairns Hospital', 'AttributionEvidence': 'source assertion',
    }
    r.update(kw)
    return r

class RapidTests(unittest.TestCase):
    def test_source_status_not_human_approval(self):
        a = rapid.profile_registry([row(), row(CanonicalKey='', ReviewStatus='Needs Review', Title='')])
        self.assertEqual(a['keyed'], 1)
        self.assertEqual(a['source_included'], 1)
        self.assertEqual(a['keyless'], 1)
        self.assertEqual(a['independently_approved'], 0)

    def test_publication_year_and_future_censor(self):
        a = rapid.profile_registry([row(PublicationYear='2,026'), row(CanonicalKey='PUB:b', PublicationYear='2,025')])
        self.assertEqual(a['yearly_source_included']['2026'], 1)
        self.assertEqual(a['yearly_source_included']['2025'], 1)
        self.assertEqual(a['provisional_year'], 2026)

    def test_doi_sentinel_excluded_and_duplicate_detected(self):
        a = rapid.profile_registry([
            row(), row(CanonicalKey='PUB:b', DOI='https://doi.org/10.1234/a'),
            row(CanonicalKey='PUB:c', DOI='0'),
            row(CanonicalKey='PUB:d', PMID='0'),
        ])
        self.assertEqual(a['duplicate_doi_groups'], 1)
        self.assertEqual(a['invalid_doi_count'], 1)
        self.assertEqual(a['invalid_pmid_count'], 1)

    def test_no_key_rows_cannot_be_counted_as_publications(self):
        a = rapid.profile_registry([row(CanonicalKey='', Title='Ghost', ReviewStatus='Included')])
        self.assertEqual(a['source_included'], 0)
        self.assertEqual(a['keyless'], 1)

    def test_affiliation_false_positive_adelaide_mareeba(self):
        self.assertEqual(rapid.classify_affiliation('Mareeba Babies Hospital, Adelaide'), 'nonlocal_false_positive')
        self.assertEqual(rapid.classify_affiliation('Mareeba Hospital, Queensland'), 'hospital_affiliation_candidate')
        self.assertEqual(rapid.classify_affiliation('Cairns Base Hospital'), 'hospital_affiliation_candidate')
        self.assertEqual(rapid.classify_affiliation('Cairns and Hinterland Hospital and Health Service'), 'hhs_affiliation_candidate')

    def test_citation_source_not_automatically_census(self):
        registry=[row(), row(CanonicalKey='PUB:b', DOI='10.1234/b', ReviewStatus='Needs Review')]
        openalex=[{'doi':'https://doi.org/10.1234/a','cited_by_count':'5'}, {'doi':'https://doi.org/10.1234/b','cited_by_count':'12'}]
        a = rapid.profile_registry(registry, openalex=openalex)
        self.assertEqual(a['openalex_citation_coverage_source_included'], 1)
        self.assertEqual(a['openalex_source_included_citation_sum'], 5)
        self.assertEqual(a['source_included'], 1)

    def test_conflicting_openalex_doi_is_quarantined(self):
        registry=[row()]
        openalex=[{'doi':'10.1234/A','cited_by_count':'1'}, {'doi':'10.1234/a','cited_by_count':'4'}]
        a=rapid.profile_registry(registry,openalex=openalex)
        self.assertEqual(a['openalex_duplicate_key_count'],1)
        self.assertEqual(a['openalex_citation_coverage_source_included'],0)

if __name__=='__main__':
    unittest.main()
