"""Fictional display decoder and public sample provenance regression tests."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
p=ROOT/"portfolio-scripts"/"rims_field_decoder.py"
spec=importlib.util.spec_from_file_location("rims_field_decoder",p)
decoder=importlib.util.module_from_spec(spec)
spec.loader.exec_module(decoder)

class FieldDecoderTests(unittest.TestCase):
    def setUp(self):
        self.mapping=decoder.load_mapping(ROOT/"portfolio"/"rims-field-aliases.json")

    def test_known_field_aliases(self):
        self.assertEqual(self.mapping["publication_register"]["field_17"],"ReviewStatus")
        self.assertEqual(len(self.mapping["publication_register"]),20)

    def test_unknown_code_survives(self):
        result=decoder.decode_row({"field_11":"10.1234/sample","field_999":"unknown"},self.mapping)
        self.assertEqual(result["fields"]["DOI"],"10.1234/sample")
        self.assertEqual(result["unknown_fields"],["field_999"])
        self.assertFalse(result["review_authorised"])

    def test_collision_refused(self):
        with self.assertRaises(decoder.MappingError):
            decoder.decode_row({"field_11":"a","DOI":"b"},self.mapping)

    def test_source_included_not_reviewer_approval(self):
        label=decoder.display_value("ReviewStatus","Included",self.mapping)
        self.assertIn("not human approval",label["display"])
        self.assertFalse(label["review_authorised"])

    def test_unrecognised_status_is_not_assigned(self):
        result=decoder.display_value("ReviewStatus","UNSEEN",self.mapping)
        self.assertEqual(result["display"],"UNSEEN")
        self.assertFalse(result["known"])

    def test_public_examples_have_provenance(self):
        manifest=json.loads((ROOT/"portfolio"/"rims-public-api-samples.json").read_text(encoding="utf-8"))
        self.assertEqual(len(manifest["samples"]),3)
        for source in manifest["samples"]:
            self.assertEqual(source["verification"],"observed_public_api")
            self.assertTrue(source["endpoint"].startswith("https://"))
            self.assertTrue(source["source_field_paths"])
            self.assertTrue(source["rows"])
        self.assertTrue(all(row["status"] for row in manifest["schema_only_sources"]))

if __name__=="__main__":
    unittest.main()
