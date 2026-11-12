"""Fictional medallion loss-audit and review fail-closed tests."""
import importlib.util, unittest
from pathlib import Path

path=Path(__file__).resolve().parents[1]/"rims_medallion_pipeline.py"
spec=importlib.util.spec_from_file_location("rims_medallion_pipeline",path)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

class MedallionTests(unittest.TestCase):
    def test_bronze_retains_nested_arrays_and_unknowns(self):
        raw={"id":"fictional","nested":{"values":[1,2,{"x":None}]},"extra":["a","b"]}
        b=mod.bronze("synthetic","id:1",raw,licence="synthetic",captured_utc="2026-11-10T00:00:00Z",retention_class="test",pagination={"complete":True})
        self.assertEqual(b["raw_payload"],raw)
        self.assertTrue(b["bronze_loss_audited"])
        s=mod.silver(b,canonical_id="fictional-id",entity_type="publication",mapped_fields={"id":"identity"})
        self.assertEqual(s["unmapped_source"]["nested"],raw["nested"])
        self.assertEqual(s["source_field_count"],3)

    def test_bronze_accepts_array_root_but_silver_requires_record_object(self):
        raw=[{"id":"a"},{"id":"b"}]
        b=mod.bronze("synthetic","batch",raw,licence="synthetic",captured_utc="2026-11-10T00:00:00Z",retention_class="test")
        self.assertEqual(b["raw_payload"],raw)
        with self.assertRaises(mod.ContractError):
            mod.silver(b,canonical_id="batch",entity_type="publication",mapped_fields={})

    def test_privacy_exclusion_requires_reason(self):
        with self.assertRaises(mod.ContractError):
            mod.bronze("a","b",{"restricted":"secret"},licence="synthetic",captured_utc="2026-11-10T00:00:00Z",retention_class="test",excluded_fields=("restricted",))
        result=mod.bronze("a","b",{"restricted":"fictional"},licence="synthetic",captured_utc="2026-11-10T00:00:00Z",retention_class="test",excluded_fields=("restricted",),exclusion_reasons={"restricted":"privacy"})
        self.assertEqual(result["raw_payload"],{})
        self.assertTrue(result["bronze_loss_audited"])

    def test_silver_refuses_invented_field(self):
        b=mod.bronze("x","y",{"a":1},licence="synthetic",captured_utc="2026-11-10T00:00:00Z",retention_class="test")
        with self.assertRaises(mod.ContractError):
            mod.silver(b,canonical_id="p",entity_type="publication",mapped_fields={"missing":"new"})

    def test_gold_never_auto_approves_claim(self):
        row={"canonical_id":"p","review_authority_verified":False}
        g=mod.gold([row],period="2026-10",review_states={"p":"ConfirmedCHHHS"})
        self.assertEqual(g["approved_ids"],[])
        self.assertEqual(g["held_ids"],["p"])
        g_verified=mod.gold([row],period="2026-10",review_states={"p":"ConfirmedCHHHS"},verify_decision=lambda key,record: True)
        self.assertEqual(g_verified["approved_ids"],["p"])
        self.assertFalse(g["gold_issued"])
        claim=mod.platinum(g,analysis={"signal":"fictional"},evidence_refs=["synthetic"],limitations=["no native evidence"])
        self.assertFalse(claim["decision_authorised"])

if __name__=="__main__":unittest.main()
