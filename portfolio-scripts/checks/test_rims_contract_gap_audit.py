"""Contract audit must not equate presence of schemas with full implementation."""
import importlib.util
from pathlib import Path
import unittest

path = Path(__file__).resolve().parents[1] / "rims_contract_gap_audit.py"
spec = importlib.util.spec_from_file_location("rims_contract_gap_audit", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ContractGapTests(unittest.TestCase):
    def test_all_schemas_have_registered_required_fields(self):
        report = module.audit()
        self.assertEqual(len(report["medallion"]), 4)
        self.assertEqual(len(report["domains"]), 6)
        self.assertTrue(all(
            x["required_are_declared"] and x["strict_root"]
            for x in report["medallion"].values()
        ))

    def test_domain_type_gaps_are_visible_not_silently_accepted(self):
        report = module.audit()
        self.assertGreater(
            report["domains"]["publications"]["unconstrained_optional_fields"], 0
        )
        self.assertGreater(
            report["domains"]["people"]["unconstrained_optional_fields"], 0
        )
        self.assertFalse(report["all_contracts_fully_implemented"])
        self.assertFalse(report["all_source_fields_fully_used"])
        self.assertFalse(report["tenant_acceptance"])


if __name__ == "__main__":
    unittest.main()
