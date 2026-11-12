"""Synthetic ZIP-only regression for reproducible RIMS flow specification generator."""
import importlib.util, json, tempfile, unittest, zipfile
from pathlib import Path
from defusedxml import ElementTree as ET

source=Path(__file__).resolve().parents[1]/"rims_generate_flow_specs.py"
spec=importlib.util.spec_from_file_location("rims_generate_flow_specs",source)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class GeneratedFlowTests(unittest.TestCase):
    def test_complete_fictional_source_pack(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/"sample.zip"
            flow={"properties":{"definition":{
                "triggers":{"manual":{"type":"Request"}},
                "actions":{"Read_Source":{"type":"Compose","inputs":{"select":{"SourceKey":"@item()?['field_1']"}}},
                           "Create":{"type":"OpenApiConnection","inputs":{"parameters":{"item/field_17":"Included"}}}}}}}
            with zipfile.ZipFile(p,"w") as archive:
                archive.writestr("Workflows/FictionalFlow-11111111-2222-3333-4444-555555555555.json",json.dumps(flow))
            out=Path(temp)/"output"
            self.assertEqual(module.generate(p,out),1)
            pack=out/"fictionalflow"
            self.assertTrue((pack/"dictionary.json").is_file())
            self.assertEqual(len(json.loads((pack/"tasks.json").read_text())),10)
            ET.parse(pack/"process.bpmn")
            self.assertIn("flowchart TD",(pack/"process.mmd").read_text())
            dictionary=json.loads((pack/"dictionary.json").read_text())
            self.assertTrue(any("field_17" in item["path"] for item in dictionary["fields"]))

    def test_empty_zip_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/"empty.zip"
            with zipfile.ZipFile(p,"w"):pass
            with self.assertRaises(ValueError):module.generate(p,Path(temp)/"out")
if __name__=="__main__":unittest.main()
