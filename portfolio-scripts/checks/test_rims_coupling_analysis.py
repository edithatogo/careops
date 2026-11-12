"""Citation projection tests: graph and historical source integration."""
import csv
import importlib.util
from pathlib import Path
import tempfile
import unittest

root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("rims_coupling_analysis",root/"rims_coupling_analysis.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class ProjectionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name)

    def csvfile(self,name,headers,rows):
        p=self.base/name
        with p.open("w",newline="",encoding="utf-8") as stream:
            w=csv.DictWriter(stream,fieldnames=headers);w.writeheader();w.writerows(rows)
        return p

    def test_coupling_is_not_cocitation(self):
        ids=[f"https://openalex.org/W{i}" for i in (1,2,3,4)]
        works=self.csvfile("works.csv",["openalex_id"],[{"openalex_id":id} for id in ids])
        edges=self.csvfile("edge.csv",["citing","cited"],[
            {"citing":ids[0],"cited":ids[2]},
            {"citing":ids[1],"cited":ids[2]},
            {"citing":ids[0],"cited":ids[3]},
            {"citing":ids[1],"cited":ids[3]},
        ])
        out=m.analyse(works,[edges])
        self.assertEqual(out["observed_directed_edges"],4)
        self.assertEqual(out["bibliographic_coupling"]["pairs_meeting_threshold"],1)
        self.assertEqual(out["co_citation"]["pairs_meeting_threshold"],1)
        self.assertEqual(out["bibliographic_coupling"]["top_pairs"][0]["work_a"],ids[0])
        self.assertEqual(out["co_citation"]["top_pairs"][0]["work_a"],ids[2])

    def test_duplicate_references_fail_closed(self):
        ids=[f"https://openalex.org/W{i}" for i in (1,2)]
        works=self.csvfile("works.csv",["openalex_id"],[{"openalex_id":id} for id in ids])
        edges=self.csvfile("edges.csv",["citing","cited"],[{"citing":ids[0],"cited":ids[1]}]*2)
        with self.assertRaises(ValueError):m.analyse(works,[edges])

    def test_real_source_summary_reconciles(self):
        data=Path(__file__).resolve().parents[2]/"portfolio/rims/public-sources"
        if not (data/"openalex-chhhs-discovery-union-20261112/works.csv").exists():
            self.fail("Expected committed public OpenAlex source snapshot")
        out=m.analyse(data/"openalex-chhhs-discovery-union-20261112/works.csv",[
            data/"openalex-chhhs-citation-graph-20261112/internal-edges.csv",
            data/"openalex-chhhs-citation-graph-20261112/additional-citing-edges.csv",
        ])
        self.assertEqual(out["candidate_works"],2280)
        self.assertEqual(out["observed_directed_edges"],2196)
        self.assertEqual(out["bibliographic_coupling"]["pairs_meeting_threshold"],2119)
        self.assertEqual(out["co_citation"]["pairs_meeting_threshold"],1157)


if __name__=="__main__":unittest.main()
