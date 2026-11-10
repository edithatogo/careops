"""Fictional data-utilisation portfolio rollup tests; never reads private rows."""
from importlib.util import spec_from_file_location, module_from_spec
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def load(name):
    spec=spec_from_file_location(name, ROOT/"portfolio-scripts"/(name+".py"))
    module=module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


util=load("rims_retained_field_utilisation")
summary=load("rims_coverage_rollup")
catalog=json.loads((ROOT/"portfolio/rims/existing-source-adoption.json").read_text())


class RollupTests(unittest.TestCase):
    def report(self):
        source=util.profile("historical-synthetic",[
            {"a":1, "nested":{"b":True}},
            {"a":2, "nested":{"b":False}},
        ],source_sha256="c"*64)
        usage=util.utilisation(source,[
            {"source_path":"/a", "disposition":"mapped",
             "consumer":"semantic_model","artifact_id":"synthetic",
             "artifact_revision":"v1","target_field":"A"},
            {"source_path":"/nested/b","disposition":"retained_only",
             "reason":"no reviewed business product"},
        ])
        return {"source":"OpenAlex","profile":source,"utilisation":usage}

    def test_rollup_reconciles_counts_and_missing_sources(self):
        result=summary.rollup(catalog,[self.report()])
        self.assertEqual(result["sources_with_declared_profiles"],1)
        self.assertEqual(result["sources_with_verified_profile_input"],0)
        self.assertEqual(result["source_summaries"][0]["source_field_count"],2)
        self.assertEqual(result["domain_summaries"][0]["mapped_to_consumer"],1)
        self.assertEqual(result["domain_summaries"][0]["retained_only"],1)
        self.assertFalse(result["full_field_utilisation_proven"])
        self.assertIn("PubMed",result["sources_still_unprofiled"])
        self.assertFalse(result["native_model_parity_proven"])

    def test_duplicate_or_fabricated_count_refused(self):
        item=self.report()
        with self.assertRaises(summary.RollupError):
            summary.rollup(catalog,[item,item])
        altered={"source":item["source"],"profile":item["profile"],
                 "utilisation":{**item["utilisation"],"mapped_to_consumer":99}}
        with self.assertRaises(summary.RollupError):
            summary.rollup(catalog,[altered])

    def test_no_raw_values_or_field_paths_leak_into_dashboard_rollup(self):
        item=self.report()
        result=summary.rollup(catalog,[item])
        self.assertNotIn("/nested/b",str(result))
        self.assertNotIn("historical-synthetic",str(result))
        self.assertEqual(result["source_summaries"][0]["records_observed"],2)


if __name__=="__main__":
    unittest.main()
