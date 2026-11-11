"""Offline conformance and safety tests for non-mutating WDL candidates."""
from __future__ import annotations
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
CANDIDATES=ROOT/"flows/native-candidates"
EXPECTED={"01-operations-monitor.json","02-review-due-monitor.json",
          "03-activation-readiness-monitor.json"}
LEGAL_ACTIONS={"OpenApiConnection","Compose","Query"}
LEGAL_OUTCOMES={"Succeeded","Failed","TimedOut","Skipped"}

def validate(doc:dict):
    required={"$schema","contentVersion","parameters","triggers","actions","outputs"}
    assert set(doc)==required, f"unexpected native WDL top-level keys: {set(doc)-required}"
    assert doc["$schema"].endswith("workflowdefinition.json#")
    assert doc["parameters"]["SharePointSiteUrl"]["type"]=="string"
    assert doc["triggers"]["Schedule"]["type"]=="Recurrence"
    actions=doc["actions"]
    assert actions
    edges={name:set(action.get("runAfter",{})) for name,action in actions.items()}
    assert all(edges[name] <= actions.keys() for name in actions)
    assert all(set(outcomes)<=LEGAL_OUTCOMES for action in actions.values()
               for outcomes in action.get("runAfter",{}).values())
    for name,action in actions.items():
        assert action["type"] in LEGAL_ACTIONS, (name,action["type"])
        if action["type"]=="OpenApiConnection":
            host=action["inputs"]["host"]
            assert host["operationId"]=="HttpRequest"
            assert host["apiId"]=="/providers/Microsoft.PowerApps/apis/shared_sharepointonline"
            assert host["connectionName"]=="shared_sharepointonline"
            params=action["inputs"]["parameters"]
            assert params["dataset"]=="@parameters('SharePointSiteUrl')"
            assert params["parameters/method"]=="GET"
            assert "parameters/body" not in params
            assert params["parameters/uri"].startswith("_api/web/lists/getbytitle(")
            assert "$top=" in params["parameters/uri"]
            assert int(params["parameters/uri"].split("$top=")[-1])<=100
    encoded=json.dumps(doc)
    assert "Authorization" not in encoded
    assert "Bearer " not in encoded
    assert ".sharepoint.com" not in encoded
    assert '"type": "Response"' not in encoded
    assert all(action["type"] not in {"Terminate","Http"} for action in actions.values())

class NativeCandidateTests(unittest.TestCase):
    def test_complete_candidate_inventory(self):
        self.assertEqual({p.name for p in CANDIDATES.glob("*.json")},EXPECTED)

    def test_candidate_schema_actions_and_nonmutating_standard_connector(self):
        for path in CANDIDATES.glob("*.json"):
            with self.subTest(path=path.name):
                validate(json.loads(path.read_text(encoding="utf-8")))

    def test_due_monitor_only_counts_and_never_enqueues(self):
        doc=json.loads((CANDIDATES/"02-review-due-monitor.json").read_text())
        self.assertIn("Filter_Due",doc["actions"])
        self.assertNotIn("Foreach",json.dumps(doc))
        self.assertEqual(doc["actions"]["Count_Due"]["type"],"Compose")

    def test_activation_monitor_does_not_read_personal_plan_payload(self):
        doc=json.loads((CANDIDATES/"03-activation-readiness-monitor.json").read_text())
        self.assertNotIn("Payload",json.dumps(doc))
        self.assertIn("readiness",str(CANDIDATES/"03-activation-readiness-monitor.json"))

if __name__=="__main__":unittest.main()
