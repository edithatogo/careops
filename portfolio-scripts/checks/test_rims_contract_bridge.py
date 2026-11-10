"""Synthetic medallion/schema conformance and research intelligence tests.

No tenant, provider API or personal data. Comprehensive JSON Schema validation
runs when the maintained jsonschema dev dependency is available; the core
structural and behavioural checks are stdlib-only.
"""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def load(name):
    source = ROOT / "portfolio-scripts" / (name + ".py")
    spec = spec_from_file_location(name, source)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


contract = load("rims_contract_bridge")
portfolio = load("rims_portfolio_metrics")


class ContractBridgeTests(unittest.TestCase):
    def setUp(self):
        self.raw = {
            "id": "synthetic:01",
            "authors": [{"name": "Fictional"}],
            "unmapped": {"nested": [1, 2, None]},
        }
        self.bronze = contract.bronze_record(
            "fictional", "r1", self.raw,
            provider="Fictional", licence="synthetic",
            capture_timestamp="2026-11-10T00:00:00Z",
            retention_class="test", pagination={"complete": True},
        )
        self.silver = contract.silver_record(
            self.bronze, canonical_id="pub1",
            entity_type="publication", mapping={"id": "source_identity"},
        )
        self.decision = {
            "assertion_type": "publication", "status": "ConfirmedCHHHS",
            "decision_id": "synthetic-d1",
        }

    def test_four_conformant_record_shapes(self):
        gold = contract.gold_record(
            [self.silver], product_source_id="synthetic",
            view_id="confirmed-publications", period="2026-10",
            alias_version="v1", decision_by_id={"pub1": self.decision},
            verify_decision=lambda d, row: True,
        )
        platinum = contract.platinum_record(
            gold, intelligence_id="synthetic-insight",
            hypothesis="How many records are reviewed?",
            claims=[{"metric": "publications", "value": 1,
                     "evidence_refs": ["fictional-snapshot"]}],
            methods={"method": "descriptive_count"},
            uncertainty={"type": "synthetic"},
            evidence_refs=["fictional-snapshot"],
            limitations=["No causal inference"], decision_owner="synthetic",
        )
        for layer, value in zip(contract.LAYERS, (
            self.bronze, self.silver, gold, platinum
        )):
            with self.subTest(layer=layer):
                self.assertTrue(contract.check_record_shape(layer, value))
                try:
                    from jsonschema import Draft202012Validator
                except ImportError:
                    continue
                Draft202012Validator(
                    contract.load_schema(layer),
                    format_checker=Draft202012Validator.FORMAT_CHECKER,
                ).validate(value)
        self.assertEqual(
            self.silver["typed_attributes"]["_retained_unmapped"]["unmapped"],
            {"nested": [1, 2, None]},
        )
        self.assertEqual(gold["population_counts"]["approved"], 1)
        self.assertTrue(platinum["human_release_required"])

    def test_no_unverified_gold_admission(self):
        result = contract.gold_record(
            [self.silver], product_source_id="synthetic",
            view_id="pubs", period="2026-10", alias_version="1",
            decision_by_id={"pub1": self.decision},
        )
        self.assertEqual(result["rows"], [])
        self.assertEqual(result["population_counts"]["held"], 1)

    def test_partial_or_conflicting_silver_refused(self):
        partial = {**self.bronze, "ingestion_status": "partial"}
        with self.assertRaises(contract.ContractViolation):
            contract.silver_record(
                partial, canonical_id="pub1", entity_type="publication",
                mapping={"id": "key"},
            )
        with self.assertRaises(contract.ContractViolation):
            contract.silver_record(
                self.bronze, canonical_id="pub1", entity_type="publication",
                mapping={"id": "_retained_unmapped"},
            )

    def test_silver_non_string_mapping_refused(self):
        with self.assertRaises(contract.ContractViolation):
            contract.silver_record(
                self.bronze, canonical_id="pub1",
                entity_type="publication", mapping={"id": {"bad": "value"}},
            )

    def test_platinum_claim_evidence_must_be_in_product(self):
        with self.assertRaises(contract.ContractViolation):
            contract.platinum_record(
                {"source_id": "synthetic", "snapshot_sha256": "abc"},
                intelligence_id="x", hypothesis="x",
                claims=[{"value": 1, "evidence_refs": ["not-in-product"]}],
                methods={}, uncertainty={}, evidence_refs=["other"],
                limitations=["synthetic"], decision_owner="reviewer",
            )

    def test_platinum_claim_needs_evidence(self):
        with self.assertRaises(contract.ContractViolation):
            contract.platinum_record(
                {"source_id": "synthetic", "snapshot_sha256": "abc"},
                intelligence_id="x", hypothesis="x", claims=[{"value": 1}],
                methods={}, uncertainty={}, evidence_refs=["ref"],
                limitations=[], decision_owner="reviewer",
            )

    def test_naive_bronze_capture_refused(self):
        with self.assertRaises(contract.ContractViolation):
            contract.bronze_record(
                "source", "r1", {}, provider="f", licence="synthetic",
                capture_timestamp="2026-11-10T00:00:00",
                retention_class="test", pagination={"complete": True},
            )


class PortfolioTests(unittest.TestCase):
    def setUp(self):
        self.domains = {
            "publications": [
                {"entity_id": "pub1", "open_access_status": "gold"},
                {"entity_id": "pub2", "open_access_status": "unknown"},
            ],
            "projects_studies": [
                {"entity_id": "study1", "status": "Completed"},
                {"entity_id": "study2", "status": "Recruiting"},
            ],
            "funding": [
                {"entity_id": "award1", "record_type": "Award",
                 "status": "Awarded"},
            ],
            "people": [], "organisations": [],
        }
        self.links = [
            {"relationship_id": "link1", "type": "output_of_study",
             "source_domain": "publications", "source_id": "pub1",
             "target_domain": "projects_studies", "target_id": "study1",
             "evidence_hash": "fictional-evidence"},
            {"relationship_id": "link2", "type": "award_supports_study",
             "source_domain": "funding", "source_id": "award1",
             "target_domain": "projects_studies", "target_id": "study1",
             "evidence_hash": "fictional-evidence"},
        ]

    def test_source_counts_are_not_auto_approved(self):
        value = portfolio.analyse_portfolio(
            self.domains, self.links, period="2026-10",
        )
        self.assertEqual(value["source_counts"]["publications"], 2)
        self.assertEqual(value["verified_counts"]["publications"], 0)
        self.assertIsNone(value["metrics"]["open_access_assessed"]["value"])
        self.assertEqual(value["held_relationship_count"], 2)

    def test_explicit_verification_measures_reviewed_relationships(self):
        result = portfolio.analyse_portfolio(
            self.domains, self.links, period="2026-10",
            verify_entity=lambda domain, row: True,
            verify_relationship=lambda relationship: True,
        )
        self.assertEqual(
            result["metrics"]["completed_studies_with_reviewed_output"]["value"],
            1.0,
        )
        self.assertEqual(
            result["metrics"]["awarded_funding_linked_to_study"]["value"], 1.0,
        )
        self.assertEqual(
            result["metrics"]["open_access_assessed"]["denominator"], 1,
        )
        self.assertFalse(result["native_verified"])
        self.assertNotIn("pub1", str(result))
        self.assertTrue(result["human_release_required"])

    def test_invalid_or_dangling_links_refused(self):
        with self.assertRaises(portfolio.PortfolioError):
            portfolio.analyse_portfolio(
                self.domains, [{**self.links[0], "target_id": "missing"}],
                period="2026-10",
            )
        with self.assertRaises(portfolio.PortfolioError):
            portfolio.analyse_portfolio(
                {"people": [{"entity_id": "duplicate"},
                            {"entity_id": "duplicate"}]},
                [], period="2026-10",
            )


if __name__ == "__main__":
    unittest.main()
