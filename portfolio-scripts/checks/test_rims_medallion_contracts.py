"""Cross-file structural tests for RIMS contracts and granular task registers."""
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
LAYERS=("bronze","silver","gold","platinum")
DOMAINS=("publications","people","organisations","projects_studies","funding","shared")

def load(rel):
    return json.loads((ROOT/rel).read_text(encoding="utf-8"))

class RimsContractRegistryTests(unittest.TestCase):
    def test_medallion_contracts_have_required_provenance(self):
        for layer in LAYERS:
            with self.subTest(layer=layer):
                x=load(f"portfolio/rims/contracts/medallion/{layer}.schema.json")
                self.assertEqual(x["$schema"],"https://json-schema.org/draft/2020-12/schema")
                self.assertTrue({"source_id","record_id","schema_version"}.issubset(x["required"]))
                self.assertEqual(x["type"],"object")

    def test_six_domain_contracts_have_quality_and_intelligence(self):
        for domain in DOMAINS:
            with self.subTest(domain=domain):
                x=load(f"portfolio/rims/contracts/domains/{domain}.schema.json")
                self.assertTrue({"entity_id","source_assertions","lineage","quality","intelligence"}.issubset(x["required"]))

    def test_36_flow_tracks_and_unique_360_task_identifiers(self):
        data=load("conductor/tracks/rims_medallion_verticals_20261110/flow-register.json")
        self.assertEqual(len(data["flows"]),36)
        tasks=[task for flow in data["flows"] for task in flow["task_ids"]]
        self.assertEqual(len(tasks),360)
        self.assertEqual(len(set(tasks)),360)
        self.assertEqual(len(data["tasks_template"]),10)

    def test_verticals_have_72_concrete_tasks(self):
        data=load("conductor/tracks/rims_medallion_verticals_20261110/vertical-products.json")
        self.assertEqual(set(data["verticals"]),set(DOMAINS))
        tasks=[task["id"] for vertical in data["verticals"].values() for task in vertical["tasks"]]
        self.assertEqual(len(tasks),72)
        self.assertEqual(len(set(tasks)),72)

    def test_list_recreation_fields_and_csv_are_aligned(self):
        schema=load("portfolio/rims/sharepoint/lists.recreation.json")
        for name,spec in schema["lists"].items():
            with self.subTest(name=name):
                path=ROOT/f"portfolio/rims/sharepoint/csv-headings/{name}.csv"
                headers=path.read_text(encoding="utf-8").strip().split(",")
                self.assertEqual(headers,list(spec["columns"]))
                for field,column in spec["columns"].items():
                    if column["type"]=="Choice":
                        self.assertTrue(column["choices"])
                if name in ("PersonAffiliations","ReviewDecisions"):
                    self.assertEqual(spec["sensitivity"],"restricted")

if __name__=="__main__":
    unittest.main()
