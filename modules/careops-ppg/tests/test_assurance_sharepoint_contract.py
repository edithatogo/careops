# SPDX-License-Identifier: Apache-2.0
"""Offline assurance-list contract tests; no SharePoint or tenant operations."""
import copy
import json
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

from scripts.ppg_assurance_sharepoint import validate_manifest, field_definitions

CONFIG=Path("config/assurance-sharepoint-registers-v1.json")


class AssuranceSharePointTests(unittest.TestCase):
    def setUp(self):
        self.source=json.loads(CONFIG.read_text())

    def test_current_three_lists_have_stable_keys_and_qualify_source_only(self):
        report=validate_manifest(self.source)
        self.assertEqual(report["registerCount"],3)
        self.assertEqual(report["sourceOnly"],True)
        self.assertEqual(report["nativeQualification"],False)
        self.assertFalse(report["premiumRequired"])
        self.assertTrue(all(x.startswith("PPG ") for x in report["listTitles"]))

    def test_unknown_or_premium_connector_is_refused(self):
        for value in ("shared_commondataserviceforapps", "unknown", "shared_http"):
            with self.subTest(value=value):
                source=copy.deepcopy(self.source)
                source["connector"]=value
                with self.assertRaisesRegex(ValueError,"standard connector"):
                    validate_manifest(source)

    def test_native_or_automatic_promotion_refused(self):
        for field,value in (("nativeQualification",True),
                            ("premiumRequired",True),("sourceOnly",False),
                            ("replacesExistingLists",True)):
            with self.subTest(field=field):
                source=copy.deepcopy(self.source)
                source[field]=value
                with self.assertRaises(ValueError):
                    validate_manifest(source)

    def test_duplicate_list_and_field_identities_refused(self):
        source=copy.deepcopy(self.source)
        source["registers"].append(copy.deepcopy(source["registers"][0]))
        with self.assertRaisesRegex(ValueError,"Duplicate"):
            validate_manifest(source)
        source=copy.deepcopy(self.source)
        source["registers"][0]["fields"].append(copy.deepcopy(source["registers"][0]["fields"][0]))
        with self.assertRaisesRegex(ValueError,"Duplicate"):
            validate_manifest(source)

    def test_schema_refuses_sensitive_or_unsupported_fields(self):
        for name in ("PatientIdentifier","AutoApproved","RawSourceText","AccessToken"):
            with self.subTest(name=name):
                source=copy.deepcopy(self.source)
                source["registers"][0]["fields"].append(
                    {"name":name,"type":"Text","required":False,"unique":False})
                with self.assertRaisesRegex(ValueError,"prohibited"):
                    validate_manifest(source)
        source=copy.deepcopy(self.source)
        source["registers"][0]["fields"][1]["type"]="ComputedPremium"
        with self.assertRaisesRegex(ValueError,"unsupported"):
            validate_manifest(source)

    def test_choice_vocabulary_is_explicit_and_unique(self):
        source=copy.deepcopy(self.source)
        selected=next(f for f in source["registers"][0]["fields"]
                      if f["name"]=="SourceKind")
        selected["choices"]=["internal-ppg","internal-ppg"]
        with self.assertRaisesRegex(ValueError,"Choice"):
            validate_manifest(source)

    def test_primary_key_requires_unique_indexed_text(self):
        source=copy.deepcopy(self.source)
        source["registers"][0]["fields"][0]["unique"]=False
        with self.assertRaisesRegex(ValueError,"primary"):
            validate_manifest(source)

    def test_generated_xml_is_structural_source_only(self):
        result=field_definitions(self.source)
        self.assertEqual(len(result),3)
        for item in result:
            self.assertEqual(item["nativeWrites"],0)
            for row in item["fields"]:
                field=ET.fromstring(row["schemaXml"])
                self.assertEqual(field.attrib["Name"],row["name"])
                self.assertIn(field.attrib["Type"],{"Text","Choice","DateTime"})
                if field.attrib["Type"]=="Choice":
                    self.assertTrue(field.findall("./CHOICES/CHOICE"))
        self.assertEqual(result,field_definitions(self.source))

    def test_field_names_are_safe_for_sharepoint_schema(self):
        source=copy.deepcopy(self.source)
        source["registers"][0]["fields"][1]["name"]="unsafe/name"
        with self.assertRaisesRegex(ValueError,"field name"):
            validate_manifest(source)

    def test_no_accreditation_decision_or_readiness_score_schema(self):
        report=field_definitions(self.source)
        raw=json.dumps(report)
        self.assertNotIn("ComplianceMet",raw)
        self.assertNotIn("AccreditationRating",raw)
        self.assertNotIn("PatientIdentifier",raw)


if __name__=="__main__":
    unittest.main()
