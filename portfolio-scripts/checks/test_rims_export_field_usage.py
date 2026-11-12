"""Fictional exported flow physical column discovery tests."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

script=Path(__file__).resolve().parents[1]/"rims_export_field_usage.py"
spec=importlib.util.spec_from_file_location("rims_export_field_usage",script)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class FlowFieldUsageTests(unittest.TestCase):
    def test_discovers_fields_without_exposing_private_values(self):
        flow={"properties":{"definition":{
            "triggers":{"Trigger":{"type":"Request"}},
            "actions":{
                "Save":{"type":"OpenApiConnection","inputs":{
                    "parameters":{"item/field_17":"Included",
                                  "item/field_11":"private-doi-value"}}},
                "Condition":{"type":"If","actions":{
                    "Read":{"type":"Compose","inputs":"@items('loop')?['field_10']"}}}
            }
        }}}
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"fictional.zip"
            with zipfile.ZipFile(path,"w") as archive:
                archive.writestr("Workflows/Fictional-00000000-0000-0000-0000-000000000000.json",
                                  json.dumps(flow))
            result=mod.usage(path)
        self.assertEqual(result["flow_count"],1)
        self.assertEqual(result["distinct_field_codes"],3)
        self.assertEqual(result["fields"],["field_10","field_11","field_17"])
        self.assertFalse(result["native_parity_verified"])
        self.assertNotIn("private-doi-value",str(result))
        self.assertNotIn("Included",str(result))

    def test_empty_archive_refused(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"empty.zip"
            with zipfile.ZipFile(path,"w"):
                pass
            with self.assertRaises(ValueError):
                mod.usage(path)


if __name__=="__main__":
    unittest.main()
