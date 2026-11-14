"""Focused validation for generated local analytics artifacts."""
from __future__ import annotations

import base64
import json
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from build_analytics import (
    FABRIC_PAGES_SCHEMA,
    FABRIC_REPORT_SCHEMA,
    FABRIC_SEMANTIC_SCHEMA,
    build,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / ".local" / "schema-cache" / "fabric"


class AnalyticsArtifactsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.projection = self.root / "projection.json"
        self.projection.write_text(json.dumps({"initiatives": [
            {"initiative_id": "IIR-X1", "title": "Fictional test", "source_key": "fictional:x1", "revision": 4,
             "task_count": 5, "event_count": 2, "decision_count": 1,
             "benefit_observations": 1, "adoption_observations": 1, "adopted_services": 0},
        ]}), encoding="utf-8")
        self.out = self.root / "out"
        self.receipt = build(self.projection, self.out)

    def tearDown(self):
        self.temp.cleanup()

    def test_build_contains_tmsl_pbism_pbir_and_rdl(self):
        model_path = self.out / "CareOpsImprovement.SemanticModel" / "model.bim"
        model = json.loads(model_path.read_text(encoding="utf-8"))
        self.assertEqual(model["compatibilityLevel"], 1600)
        tables = {table["name"]: table for table in model["model"]["tables"]}
        self.assertEqual(set(tables), {"DimInitiative", "FactInitiativeSnapshot", "FactInitiativeEvent", "FactDecision", "FactMeasureObservation", "FactAdoption"})
        self.assertIn("Registered initiatives", {measure["name"] for measure in tables["FactInitiativeSnapshot"]["measures"]})
        self.assertIn("IIR-X1", tables["FactInitiativeSnapshot"]["partitions"][0]["source"]["expression"])
        self.assertEqual(len(model["model"]["relationships"]), 5)

        pbism_path = self.out / "CareOpsImprovement.SemanticModel" / "definition.pbism"
        pbism = json.loads(pbism_path.read_text(encoding="utf-8"))
        self.assertEqual(pbism["$schema"], FABRIC_SEMANTIC_SCHEMA)
        report_path = self.out / "CareOpsImprovement.Report" / "definition.pbir"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["$schema"], FABRIC_REPORT_SCHEMA)
        pages = json.loads((self.out / "CareOpsImprovement.Report" / "definition/pages/pages.json").read_text())
        self.assertEqual(pages["$schema"], FABRIC_PAGES_SCHEMA)
        self.assertEqual(pages["pageOrder"], ["Overview", "Scorecard"])
        for page in pages["pageOrder"]:
            page_path = self.out / "CareOpsImprovement.Report" / f"definition/pages/{page}/page.json"
            self.assertTrue(page_path.is_file())
        self.assertEqual(report["version"], "4.0.0")
        self.assertTrue((self.out / "CareOpsImprovementScorecard.rdl").is_file())

    def test_fabric_definition_round_trips_each_source_file(self):
        definitions = self.out / "fabric-item-definitions"
        model = json.loads((definitions / "semantic-model.json").read_text())
        report = json.loads((definitions / "report.json").read_text())
        paginated = json.loads((definitions / "paginated-report.json").read_text())
        release_index = json.loads((definitions / "release-index.json").read_text())
        self.assertEqual({item["type"] for item in release_index["items"]}, {"SemanticModel", "Report", "PaginatedReport"})
        self.assertEqual({part["path"] for part in model["definition"]["parts"]}, {"model.bim", "definition.pbism"})
        report_paths = {part["path"] for part in report["definition"]["parts"]}
        self.assertIn("definition.pbir", report_paths)
        self.assertIn("definition/report.json", report_paths)
        self.assertEqual(paginated["definition"]["format"], "PaginatedReportDefinition")
        self.assertEqual([part["path"] for part in paginated["definition"]["parts"]], ["CareOpsImprovementScorecard.rdl"])
        source_map = {
            "model.bim": self.out / "CareOpsImprovement.SemanticModel/model.bim",
            "definition.pbism": self.out / "CareOpsImprovement.SemanticModel/definition.pbism",
            "CareOpsImprovementScorecard.rdl": self.out / "CareOpsImprovementScorecard.rdl",
        }
        for payload in (model, report, paginated):
            for part in payload["definition"]["parts"]:
                self.assertEqual(part["payloadType"], "InlineBase64")
                data = base64.b64decode(part["payload"], validate=True)
                if part["path"] in source_map:
                    self.assertEqual(data, source_map[part["path"]].read_bytes())
                elif payload is report:
                    self.assertEqual(data, (self.out / "CareOpsImprovement.Report" / part["path"]).read_bytes())

    def test_json_schema_and_xml_validation(self):
        from jsonschema import Draft7Validator

        cases = [
            ("semanticModel_definitionProperties_1.0.0_schema.json", "CareOpsImprovement.SemanticModel/definition.pbism"),
            ("report_definitionProperties_2.0.0_schema.json", "CareOpsImprovement.Report/definition.pbir"),
            ("report_definition_pagesMetadata_1.0.0_schema.json", "CareOpsImprovement.Report/definition/pages/pages.json"),
            ("report_definition_page_2.0.0_schema.json", "CareOpsImprovement.Report/definition/pages/Overview/page.json"),
            ("report_definition_report_3.1.0_schema.json", "CareOpsImprovement.Report/definition/report.json"),
        ]
        for schema_name, target in cases:
            schema = json.loads((SCHEMAS / schema_name).read_text(encoding="utf-8"))
            value = json.loads((self.out / target).read_text(encoding="utf-8"))
            errors = list(Draft7Validator(schema).iter_errors(value))
            self.assertEqual(errors, [], f"{target}: {errors}")

        rdl = self.out / "CareOpsImprovementScorecard.rdl"
        ET.parse(rdl)
        schema = ROOT / ".local" / "schema-cache" / "ReportDefinition.xsd"
        self.assertTrue(schema.is_file(), "official RDL XSD should be cached under .local/schema-cache")
        result = subprocess.run(["xmllint", "--noout", "--schema", str(schema), str(rdl)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        tree = ET.parse(rdl)
        ns = {"r": "http://schemas.microsoft.com/sqlserver/reporting/2016/01/reportdefinition"}
        self.assertEqual(tree.findtext(".//r:DataSetName", namespaces=ns), "InitiativeScorecard")
        query = tree.findtext(".//r:CommandText", namespaces=ns)
        self.assertIn("SUMMARIZECOLUMNS", query)
        self.assertIn("DimInitiative", query)
        self.assertIn("Parameters!WorkspaceXmlaEndpoint.Value", tree.findtext(".//r:ConnectString", namespaces=ns))
        self.assertEqual(len(tree.findall(".//r:Tablix/r:TablixBody/r:TablixRows/r:TablixRow", ns)), 2)

    def test_duplicate_or_missing_initiative_keys_fail_closed(self):
        self.projection.write_text(json.dumps({"initiatives": [{"initiative_id": "same"}, {"initiative_id": "same"}]}))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            build(self.projection, self.root / "dup")
        self.projection.write_text(json.dumps({"initiatives": [{"title": "missing key"}]}))
        with self.assertRaisesRegex(ValueError, "initiative_id"):
            build(self.projection, self.root / "missing")

    def test_source_packet_facts_remain_separate_and_unknowns_stay_blank(self):
        self.projection.write_text(json.dumps({
            "initiatives": [{"initiative_id": "IIR-X2", "title": "Fictional", "source_key": "fictional:x2", "revision": 1}],
            "events": [{"event_id": "e1", "initiative_id": "IIR-X2", "event_type": "registered", "effective_at": "2026-11-01T00:00:00Z", "observed_at": "2026-11-01T00:01:00Z", "source_key": "fictional:e1"}],
            "tasks": [{"task_id": f"t{i}", "initiative_id": "IIR-X2"} for i in range(5)],
            "decisions": [],
            "snapshots": [{"snapshot_id": "s1", "initiative_id": "IIR-X2", "kind": "benefit", "measure": "wait_time", "value": None, "status": "not_observed", "source_key": "fictional:s1"}],
        }), encoding="utf-8")
        out = self.root / "packet-out"
        build(self.projection, out)
        model = json.loads((out / "CareOpsImprovement.SemanticModel/model.bim").read_text())
        tables = {table["name"]: table for table in model["model"]["tables"]}
        self.assertIn('"e1"', tables["FactInitiativeEvent"]["partitions"][0]["source"]["expression"])
        self.assertIn('{"IIR-X2", "Fictional", "fictional:x2", 1, null, 5, 1, 0, 1, 0, 0}', tables["FactInitiativeSnapshot"]["partitions"][0]["source"]["expression"])
        self.assertIn("null", tables["FactMeasureObservation"]["partitions"][0]["source"]["expression"])


if __name__ == "__main__":
    unittest.main()
