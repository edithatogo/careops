"""Synthetic contract tests for optional RIMS storage capability resolution."""
import importlib.util
from pathlib import Path
import unittest

path = Path(__file__).resolve().parents[1] / "rims_platform_capability.py"
spec = importlib.util.spec_from_file_location("rims_platform_capability", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PlatformCapabilityTests(unittest.TestCase):
    def setUp(self):
        self.profile = {"schema": module.SCHEMA, "requested_backend": "fabric_directlake",
                        "enabled_optional": ["fabric_directlake"]}

    def test_core_without_entitlement(self):
        self.assertEqual(module.resolve({"schema": module.SCHEMA})["selected"],
                         "sharepoint_json")

    def test_unverified_premium_falls_back(self):
        self.assertEqual(module.resolve(self.profile)["selected"], "sharepoint_json")
        self.assertEqual(module.resolve(self.profile, verify=lambda n, r: False)["selected"],
                         "sharepoint_json")

    def test_entitlement_is_planning_not_native_authority(self):
        result = module.resolve(self.profile, verify=lambda n, r: True)
        self.assertEqual(result["selected"], "fabric_directlake")
        self.assertFalse(result["execute_authorised"])

    def test_premium_in_inactive_core_branch_is_not_allowed(self):
        with self.assertRaises(module.FeatureRefused):
            module.verify_core_definition(["shared_sharepointonline",
                                           "shared_commondataserviceforapps"])

    def test_core_standard_sharepoint(self):
        self.assertTrue(module.verify_core_definition(["shared_sharepointonline"]))

    def test_unknown_backend(self):
        with self.assertRaises(module.FeatureRefused):
            module.resolve({"schema": module.SCHEMA, "requested_backend": "unknown"})


if __name__ == "__main__":
    unittest.main()
