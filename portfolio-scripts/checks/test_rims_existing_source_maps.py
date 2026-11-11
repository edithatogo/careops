"""Source-map inventories must enumerate all 17 existing providers without activation."""
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
MANIFEST=ROOT/"portfolio/rims/maps/existing-source-map-manifest.json"
CATALOGUE=ROOT/"portfolio/rims/existing-source-adoption.json"
SCHEMA=ROOT/"portfolio/rims/contracts/field-product-map.schema.json"
KINDS={"string","integer","number","boolean","null","array","object"}
TRANSFORMS={"identity","doi","integer","date"}


class SourceMapTests(unittest.TestCase):
    def test_every_existing_source_is_accounted_for(self):
        manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
        catalogue=json.loads(CATALOGUE.read_text(encoding="utf-8"))
        listed=[item["source"] for item in manifest["source_maps"]]
        actual=[item["source"] for item in catalogue["sources"]]
        self.assertEqual(len(actual),17)
        self.assertEqual(set(listed),set(actual))
        self.assertEqual(len(listed),len(set(listed)))
        self.assertEqual(manifest["total_sources"],17)

    def test_candidate_maps_explicitly_unverified(self):
        manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
        mapped=0
        for row in manifest["source_maps"]:
            self.assertFalse(row["native_field_use_verified"])
            self.assertFalse(row["original_complete_provider_schema_verified"])
            self.assertFalse(row["rights_qualified"])
            if not row["recipe_path"]:
                self.assertEqual(row["status"],"await_original_retained_shape")
                continue
            mapped+=1
            mapping=json.loads((ROOT/row["recipe_path"]).read_text(encoding="utf-8"))
            self.assertEqual(mapping["schema"],"careops-rims.field-product-map/1")
            self.assertEqual(mapping["source_id"],row["source"])
            self.assertTrue(mapping["revision"].startswith("candidate-"))
            seen=set()
            for col in mapping["fields"]:
                self.assertTrue(col["source_path"].startswith("/"))
                self.assertNotIn(col["target_field"],seen)
                seen.add(col["target_field"])
                self.assertTrue(set(col["kinds"]).issubset(KINDS))
                self.assertIn(col["transform"],TRANSFORMS)
                self.assertIn(col["cardinality"],("one","many"))
        self.assertEqual(mapped,6)

    def test_strict_json_schema_references_are_local(self):
        for filename in ("private-json-occurrences.schema.json",
                         "private-field-product.schema.json",
                         "field-product-map.schema.json",
                         "retained-json-batch.schema.json"):
            data=json.loads((ROOT/"portfolio/rims/contracts"/filename).read_text())
            self.assertEqual(data["$schema"],"https://json-schema.org/draft/2020-12/schema")
            self.assertTrue(data["$id"].endswith(filename))
        self.assertEqual(json.loads(SCHEMA.read_text())["additionalProperties"],False)


if __name__=="__main__":
    unittest.main()
