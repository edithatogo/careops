"""Offline SharePoint/Teams provisioning plan regression tests."""

import contextlib
import io
import tempfile
import copy
import json
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from provisioning import (
    DEFAULT_SP_SCHEMA,
    DEFAULT_TEAMS_REQUEST,
    ProvisioningError,
    build_sharepoint_plan,
    build_teams_request,
    field_xml,
    main,
    read_json,
)


class ProvisioningTests(unittest.TestCase):
    def test_library_reconciliation_from_cli(self):
        schema = read_json(DEFAULT_SP_SCHEMA)
        library = next(r for r in schema["resources"] if r["key"] == "evidence-library")
        library["documents"] = [{"title": "Fictional draft", "body": "Human edit"}]

        def preview(resources):
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "inventory.json"
                original = json.dumps({"resources": resources})
                path.write_text(original)
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    self.assertEqual(main(["reconcile-library", "--inventory", str(path)]), 0)
                self.assertEqual(path.read_text(), original)
                self.assertNotIn("Human edit", output.getvalue())
                return json.loads(output.getvalue())

        self.assertEqual([a["action"] for a in preview([])["additions"]], ["create_library"])
        self.assertEqual(preview([library]), {"additions": [], "incompatibilities": [], "native_calls": 0})
        library["enable_versioning"] = False
        fields = {f["name"]: f for f in library["fields"]}
        fields["SourceKey"]["unique"] = False
        fields["InitiativeId"]["required"] = False
        fields["SourceRevisionRefs"]["type"] = "Text"
        library["fields"].remove(fields["OutputRevision"])
        result = preview([library])
        self.assertEqual([a["field"] for a in result["additions"]], ["OutputRevision"])
        self.assertEqual({(c.get("field"), c["property"]) for c in result["incompatibilities"]},
                         {(None, "enable_versioning"), ("SourceKey", "unique"),
                          ("InitiativeId", "required"), ("SourceRevisionRefs", "type")})
        library["base_template"] = "GenericList"
        result = preview([library])
        self.assertEqual(result["additions"], [])
        self.assertIn("base_template", [c["property"] for c in result["incompatibilities"]])

    @classmethod
    def setUpClass(cls):
        cls.schema = read_json(DEFAULT_SP_SCHEMA)
        cls.template = read_json(DEFAULT_TEAMS_REQUEST)

    def test_sharepoint_plan_is_offline_and_contains_field_xml(self):
        plan = build_sharepoint_plan(self.schema)
        self.assertEqual(plan["mode"], "offline_dry_run")
        self.assertEqual(plan["native_calls"], 0)
        self.assertFalse(plan["credential_access"])
        self.assertFalse(plan["shell_execution"])
        self.assertTrue(all(not item["create_list_command"]["executed"] for item in plan["resources"]))
        source_key = plan["resources"][0]["fields"][0]
        self.assertIn('EnforceUniqueValues="TRUE"', source_key["xml"])
        self.assertIn("spo", source_key["command"]["argv"])
        self.assertFalse(source_key["command"]["executed"])

    def test_field_xml_escapes_attributes_and_choice_content(self):
        field = {"name": "Route", "type": "Choice", "required": True,
                 "indexed": False, "unique": False,
                 "display_name": 'Route & "owner"', "choices": ["QI & safety"]}
        root = ET.fromstring(field_xml(field))
        self.assertEqual(root.attrib["DisplayName"], 'Route & "owner"')
        self.assertEqual(root.findtext("./CHOICES/CHOICE"), "QI & safety")

    def test_source_key_and_identity_are_unique_indexed_constraints(self):
        for resource in self.schema["resources"]:
            if resource["kind"] not in {"list", "library"}:
                continue
            for name in {resource["identity_field"], resource["source_key_field"]}:
                field = next(value for value in resource["fields"] if value["name"] == name)
                self.assertTrue(field["unique"], (resource["key"], name))
                self.assertTrue(field["indexed"], (resource["key"], name))

    def test_invalid_identity_or_source_member_is_rejected(self):
        bad = copy.deepcopy(self.schema)
        field = bad["resources"][0]["fields"][0]
        field["unique"] = False
        with self.assertRaisesRegex(ProvisioningError, "unique and indexed"):
            build_sharepoint_plan(bad)
        bad = copy.deepcopy(self.schema)
        bad["resources"][0]["fields"][0]["source_member"] = "source; rm -rf"
        with self.assertRaisesRegex(ProvisioningError, "source_member"):
            build_sharepoint_plan(bad)

    def test_teams_request_binds_exact_targets_and_is_not_executed(self):
        team = "12345678-1234-4234-8234-123456789abc"
        channel = "19:abc_DEF-0123456789@thread.tacv2"
        url = "https://contoso.sharepoint.com/sites/improvement/Lists/Initiatives"
        request = build_teams_request(self.template, team_id=team, channel_id=channel,
                                      sharepoint_list_url=url)
        self.assertEqual(request["method"], "POST")
        self.assertIn(team, request["url"])
        self.assertIn("19%3Aabc_DEF-0123456789%40thread.tacv2", request["url"])
        self.assertEqual(request["body"]["configuration"]["contentUrl"], url)
        self.assertEqual(request["body"]["configuration"]["websiteUrl"], url)
        self.assertFalse(request["executed"])
        self.assertEqual(request["authorization"], "not supplied")

    def test_teams_targets_and_sharepoint_url_reject_injection_and_wrong_hosts(self):
        for kwargs in (
            {"team_id": "../../evil"},
            {"channel_id": "bad"},
            {"sharepoint_list_url": "https://sharepoint.com.evil.test/list"},
            {"sharepoint_list_url": "https://user@contoso.sharepoint.com/list"},
            {"sharepoint_list_url": "http://contoso.sharepoint.com/list"},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(ProvisioningError):
                build_teams_request(self.template, **kwargs)


if __name__ == "__main__":
    unittest.main()
