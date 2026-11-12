"""Synthetic tests for source-qualified bibliometric graph audits."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
import csv

SCRIPT = Path(__file__).resolve().parents[1] / 'rims_public_graph_audit.py'
spec = importlib.util.spec_from_file_location('rims_public_graph_audit', SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class GraphAuditTest(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.addCleanup(self.d.cleanup)
        self.base = Path(self.d.name)

    def make(self, name, fieldnames, records):
        path = self.base / name
        with path.open('w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)
        return path

    def test_two_edges_and_isolation(self):
        works = self.make('works.csv', ['openalex_id'], [{'openalex_id':f'https://openalex.org/W{i}'} for i in (1,2,3,4)])
        older = self.make('old.csv', ['citing_openalex_id','cited_openalex_id'],[
            {'citing_openalex_id':'https://openalex.org/W1','cited_openalex_id':'https://openalex.org/W2'}])
        added = self.make('new.csv', ['citing','cited'],[
            {'citing':'https://openalex.org/W2','cited':'https://openalex.org/W3'}])
        result = mod.audit(works, [older, added])
        self.assertEqual((result['nodes'],result['directed_edges']), (4,2))
        self.assertEqual(result['isolated_nodes'],1)
        self.assertEqual(result['weak_components'],2)
        self.assertEqual(result['largest_weak_component'],3)
        self.assertEqual(result['top_cited'][0]['id'],'https://openalex.org/W2')

    def test_duplicate_edge_fails(self):
        works = self.make('works.csv',['openalex_id'],[{'openalex_id':'https://openalex.org/W1'},{'openalex_id':'https://openalex.org/W2'}])
        edges = self.make('edges.csv',['citing','cited'],[{'citing':'https://openalex.org/W1','cited':'https://openalex.org/W2'}]*2)
        with self.assertRaises(mod.GraphAuditError): mod.audit(works,[edges])

    def test_out_of_corpus_endpoint_fails(self):
        works = self.make('works.csv',['openalex_id'],[{'openalex_id':'https://openalex.org/W1'}])
        edges = self.make('edges.csv',['citing','cited'],[{'citing':'https://openalex.org/W1','cited':'https://openalex.org/W99'}])
        with self.assertRaises(mod.GraphAuditError): mod.audit(works,[edges])

    def test_self_reference_fails(self):
        works = self.make('works.csv',['openalex_id'],[{'openalex_id':'https://openalex.org/W1'}])
        edges = self.make('edges.csv',['citing','cited'],[{'citing':'https://openalex.org/W1','cited':'https://openalex.org/W1'}])
        with self.assertRaises(mod.GraphAuditError): mod.audit(works,[edges])

    def test_duplicate_work_id_fails(self):
        works = self.make('works.csv',['openalex_id'],[{'openalex_id':'https://openalex.org/W1'}]*2)
        with self.assertRaises(mod.GraphAuditError): mod.audit(works,[])

    def test_committed_openalex_candidate_snapshot(self):
        root = Path(__file__).resolve().parents[2]
        base = root / 'portfolio/rims/public-sources'
        works = base / 'openalex-chhhs-discovery-union-20261112/works.csv'
        edges = [
            base / 'openalex-chhhs-citation-graph-20261112/internal-edges.csv',
            base / 'openalex-chhhs-citation-graph-20261112/additional-citing-edges.csv',
        ]
        result = mod.audit(works, edges)
        self.assertEqual(result['nodes'], 2280)
        self.assertEqual(result['directed_edges'], 2196)
        self.assertEqual(result['isolated_nodes'], 1268)
        self.assertEqual(result['weak_components'], 1406)
        self.assertEqual(result['largest_weak_component'], 250)


if __name__ == '__main__': unittest.main()
