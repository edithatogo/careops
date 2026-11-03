"""Cross-artifact field names used by event flows and SharePoint schemas."""
import json
import unittest
from pathlib import Path

from build_flows import EVENT_FIELDS
from provisioning import build_sharepoint_plan

ROOT = Path(__file__).resolve().parents[1]


class PlatformContractTests(unittest.TestCase):
    def test_event_writer_fields_exist_in_provisioned_list(self):
        schema = json.loads((ROOT / "platform/sharepoint/schema.json").read_text())
        events = next(r for r in schema["resources"] if r["key"] == "initiative-events")
        self.assertLessEqual(set(EVENT_FIELDS), {f["name"] for f in events["fields"]})
        identity = next(f for f in events["fields"] if f["name"] == "SourceKey")
        self.assertTrue(identity["unique"])
        self.assertTrue(identity["indexed"])
        self.assertEqual(build_sharepoint_plan(schema)["native_calls"], 0)
