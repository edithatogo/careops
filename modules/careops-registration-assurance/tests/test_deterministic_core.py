"""Adversarial synthetic end-to-end tests for the deterministic assurance core.

Only fictional TEST identifiers and disposable SQLite databases are used.
Native AHPRA, Dataverse and workforce/SoCP authorities are never contacted.
"""
from __future__ import annotations

from pathlib import Path
import sqlite3
import sys
from tempfile import TemporaryDirectory
import unittest

# Each focused test file must also run in isolation, not depend on discovery order.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from registration_assurance.identity import WatchBinding, reconcile_identity
from registration_assurance.deterministic import admit_observation
from registration_assurance.durable import DeterministicLedger, LedgerConflict, IntegrityFailure
from registration_assurance.qualification import Qualification

NOW = "2026-11-13T10:00:00Z"


def sample(*, observation_id="test:o1", idempotency_key="test:key1",
           asof="2026-11-13T09:00:00Z", status="registered",
           registration="TEST-0001", watch="test:watch1", health="healthy"):
    return {
        "schemaVersion": "1.1.0", "observationId": observation_id,
        "watchRef": watch,
        "practitioner": {"regulator": "AHPRA", "registrationNumber": registration},
        "provider": {"kind": "AHPRA_PIE_FIND",
                     "qualificationRef": "test:approved-provider",
                     "evidenceCeiling": "qualified_regulatory",
                     "mappingVersion": "test:m1"},
        "sourceHealth": health, "observedAtUtc": NOW,
        "evidence": {"sourceRef": "test:source-record1", "asOfUtc": asof,
                     "payloadSha256": "a"*64, "sourceRevision": "test:rev1",
                     "classification": "synthetic"},
        "signal": {"identityState": "matched", "registrationStatus": status,
                   "expiryDate": "2026-12-01", "conditionsIndicator": "absent"},
        "assessment": {"outcome": "no_material_change", "reviewState": "pending",
                       "ruleVersion": "test:r1", "reasonCodes": []},
        "correlationId": "test:c1", "idempotencyKey": idempotency_key,
        "registrationDetail": {"nativeStatusCode": "test:registered",
                               "sourceVocabularyVersion": "test:regv1",
                               "categories": ["general"], "specialties": [],
                               "endorsements": [], "restrictions": []},
    }


def binding(**overrides):
    fields = dict(watch_ref="test:watch1", regulator="AHPRA",
                  registration_number="TEST-0001",
                  profession="medical_practitioner",
                  effective_from_utc="2026-01-01T00:00:00Z",
                  effective_to_utc="2027-01-01T00:00:00Z",
                  revision="test:binding-rev1")
    fields.update(overrides)
    return WatchBinding(**fields)


def qualification():
    return Qualification(
        provider_kind="AHPRA_PIE_FIND",
        qualification_ref="test:approved-provider",
        purposes=frozenset({"credentialing_read"}),
        approved_vocabulary=frozenset({"test:regv1"}),
        enabled=True,
        effective_from_utc="2026-01-01T00:00:00Z",
        effective_to_utc="2027-01-01T00:00:00Z",
        max_source_age_minutes=120,
    )


def admit(item):
    return admit_observation(
        item, qualification=qualification(),
        bindings=(binding(),), source_profession="medical_practitioner",
        purpose="credentialing_read", now_utc=NOW,
    )


class ExactIdentityTests(unittest.TestCase):
    def test_exact_binding_and_profession_is_required(self):
        result = reconcile_identity(
            sample(), (binding(),),
            source_profession="medical_practitioner", now_utc=NOW,
        )
        self.assertEqual(result.status, "matched")
        self.assertEqual(result.binding_revision, "test:binding-rev1")

    def test_missing_profession_or_registration_cannot_match(self):
        self.assertEqual(
            reconcile_identity(sample(),(binding(),),
                               source_profession=None,now_utc=NOW).status,
            "unresolved",
        )
        self.assertEqual(
            reconcile_identity(sample(registration=None),(binding(),),
                               source_profession="medical_practitioner",
                               now_utc=NOW).status,
            "unresolved",
        )

    def test_regulator_number_profession_and_watch_ref_must_match(self):
        for item in (sample(registration="TEST-OTHER"),sample(watch="test:other")):
            with self.subTest(item=item["watchRef"]):
                self.assertNotEqual(
                    reconcile_identity(item,(binding(),),
                                       source_profession="medical_practitioner",
                                       now_utc=NOW).status,"matched")
        self.assertEqual(
            reconcile_identity(sample(),(binding(),),
                               source_profession="nursing",now_utc=NOW).status,
            "mismatch",
        )

    def test_collisions_are_ambiguous(self):
        self.assertEqual(
            reconcile_identity(sample(),(binding(revision="test:a"),
                                         binding(revision="test:b")),
                               source_profession="medical_practitioner",
                               now_utc=NOW).status,"ambiguous",
        )
        self.assertEqual(
            reconcile_identity(sample(),(binding(),
                                         binding(watch_ref="test:other")),
                               source_profession="medical_practitioner",
                               now_utc=NOW).status,"ambiguous",
        )

    def test_expired_binding_and_source_match_claim_cannot_implicitly_match(self):
        self.assertEqual(
            reconcile_identity(sample(),
                               (binding(effective_to_utc="2026-10-01T00:00:00Z"),),
                               source_profession="medical_practitioner",
                               now_utc=NOW).status,"unresolved",
        )
        self.assertEqual(
            reconcile_identity(sample(),(),source_profession="medical_practitioner",
                               now_utc=NOW).status,"unresolved",
        )


class AdmissionTests(unittest.TestCase):
    def test_valid_qualified_synthetic_observation_is_not_authority(self):
        result = admit(sample())
        self.assertTrue(result.persistible)
        self.assertEqual(result.assessment["disposition"],"source_verified")
        self.assertFalse(result.assessment["practice_authorised"])

    def test_missing_qualification_or_identity_is_held(self):
        item=sample()
        result=admit_observation(
            item,qualification=None,bindings=(binding(),),
            source_profession="medical_practitioner",
            purpose="credentialing_read",now_utc=NOW)
        self.assertFalse(result.persistible)
        wrong=admit_observation(
            item,qualification=qualification(),
            bindings=(binding(registration_number="TEST-OTHER"),),
            source_profession="medical_practitioner",
            purpose="credentialing_read",now_utc=NOW)
        self.assertFalse(wrong.persistible)

    def test_empty_registration_category_is_invalid_contract(self):
        item=sample()
        item["registrationDetail"]["categories"]=[]
        result=admit(item)
        self.assertFalse(result.persistible)
        self.assertEqual(result.assessment["disposition"],"invalid_contract")

    def test_live_looking_registration_number_cannot_enter_synthetic_store(self):
        item=sample(registration="MED0000123456")
        result=admit(item)
        self.assertFalse(result.persistible)
        self.assertEqual(result.assessment["disposition"],"invalid_contract")

    def test_non_synthetic_practitioner_content_is_refused(self):
        item=sample()
        item["evidence"]["classification"]="restricted_staff"
        self.assertFalse(admit(item).persistible)

    def test_unsupported_schema_version_is_refused(self):
        item=sample()
        item["schemaVersion"]="2.0.0"
        self.assertFalse(admit(item).persistible)

    def test_impossible_calendar_expiry_is_invalid_even_without_format_plugins(self):
        item=sample()
        item["signal"]["expiryDate"]="2026-13-99"
        result=admit(item)
        self.assertFalse(result.persistible)
        self.assertEqual(result.assessment["disposition"],"invalid_contract")

    def test_expired_date_triggers_review_not_deregistration(self):
        item=sample()
        item["signal"]["expiryDate"]="2026-11-01"
        result=admit(item)
        self.assertTrue(result.persistible)
        self.assertEqual(result.assessment["disposition"],"expiry_review")
        self.assertFalse(result.assessment["practice_authorised"])

    def test_adverse_regulator_observation_remains_human_review(self):
        result=admit(sample(status="suspended"))
        self.assertTrue(result.persistible)
        self.assertEqual(result.assessment["disposition"],"potential_adverse_change")
        self.assertTrue(result.assessment["human_review_required"])


class DurableLedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory()
        self.db_path=Path(self.temp.name)/"fictional.db"
        self.store=DeterministicLedger(self.db_path)

    def tearDown(self):
        self.temp.cleanup()

    def test_append_writes_event_projection_outbox_and_integrity(self):
        receipt=self.store.append(admit(sample()),expected_version=0)
        self.assertEqual(receipt["result"],"accepted")
        self.assertEqual(receipt["version"],1)
        self.assertEqual(self.store.current_projection("test:watch1")["observationId"],"test:o1")
        self.assertEqual(len(self.store.observations("test:watch1")),1)
        self.assertEqual(len(self.store.pending_outbox()),1)
        self.assertTrue(self.store.verify_integrity())

    def test_restart_duplicate_retry_never_duplicates_work(self):
        first=self.store.append(admit(sample()),expected_version=0)
        replay=DeterministicLedger(self.db_path).append(admit(sample()),expected_version=0)
        self.assertEqual(replay["result"],"duplicate")
        self.assertEqual(first["seq"],replay["seq"])
        self.assertEqual(len(self.store.pending_outbox()),1)

    def test_changed_payload_under_same_idempotency_key_is_rejected(self):
        self.store.append(admit(sample()),expected_version=0)
        with self.assertRaises(LedgerConflict):
            self.store.append(admit(sample(
                observation_id="test:o2",status="suspended")),expected_version=1)
        self.assertEqual(len(self.store.observations("test:watch1")),1)

    def test_two_connections_cannot_overwrite_stale_revision(self):
        other=DeterministicLedger(self.db_path)
        self.store.append(admit(sample()),expected_version=0)
        second=admit(sample(observation_id="test:o2",idempotency_key="test:k2",
                            asof="2026-11-13T09:30:00Z"))
        with self.assertRaises(LedgerConflict):
            other.append(second,expected_version=0)

    def test_older_evidence_is_preserved_but_cannot_replace_latest_projection(self):
        self.store.append(admit(sample()),expected_version=0)
        old=admit(sample(observation_id="test:old",idempotency_key="test:older",
                         asof="2026-11-13T08:00:00Z",status="suspended"))
        result=self.store.append(old,expected_version=1)
        self.assertEqual(result["result"],"older_evidence")
        self.assertEqual(self.store.current_projection("test:watch1")["observationId"],"test:o1")
        self.assertEqual(len(self.store.observations("test:watch1")),2)

    def test_same_time_conflict_cannot_replace_projection(self):
        self.store.append(admit(sample()),expected_version=0)
        contrary=admit(sample(observation_id="test:o2",idempotency_key="test:k2",
                              status="suspended"))
        result=self.store.append(contrary,expected_version=1)
        self.assertEqual(result["result"],"conflicting_source_revision")
        self.assertEqual(self.store.current_projection("test:watch1")["observationId"],"test:o1")

    def test_older_append_advances_cas_revision_without_advancing_projection(self):
        self.store.append(admit(sample()),expected_version=0)
        older=admit(sample(observation_id="test:old",idempotency_key="test:oldkey",
                           asof="2026-11-13T08:00:00Z"))
        self.store.append(older,expected_version=1)
        later=admit(sample(observation_id="test:new",idempotency_key="test:newkey",
                           asof="2026-11-13T09:30:00Z"))
        with self.assertRaises(LedgerConflict):
            self.store.append(later,expected_version=1)
        self.assertEqual(self.store.append(later,expected_version=2)["result"],"accepted")

    def test_verified_adverse_observation_is_not_scope_of_practice(self):
        self.store.append(admit(sample()),expected_version=0)
        changed=admit(sample(observation_id="test:o2",idempotency_key="test:k2",
                             asof="2026-11-13T09:30:00Z",status="suspended"))
        result=self.store.append(changed,expected_version=1)
        self.assertEqual(result["result"],"accepted")
        projection=self.store.current_projection("test:watch1")
        self.assertEqual(projection["disposition"],"potential_adverse_change")
        self.assertFalse(projection["practiceAuthorised"])

    def test_fault_after_insert_rolls_back_all_sibling_writes(self):
        with self.assertRaises(RuntimeError):
            self.store.append(admit(sample()),expected_version=0,
                              fault_after_insert=True)
        self.assertEqual(self.store.observations("test:watch1"),[])
        self.assertEqual(self.store.pending_outbox(),[])
        self.assertIsNone(self.store.current_projection("test:watch1"))

    def test_sqlite_triggers_refuse_in_place_observation_updates_or_deletion(self):
        self.store.append(admit(sample()),expected_version=0)
        with sqlite3.connect(self.db_path) as db:
            with self.assertRaises(sqlite3.DatabaseError):
                db.execute("UPDATE observations SET payload_json='{}' WHERE seq=1")
            with self.assertRaises(sqlite3.DatabaseError):
                db.execute("DELETE FROM observations WHERE seq=1")

    def test_a_corrupt_hash_is_detected_before_recovery(self):
        self.store.append(admit(sample()),expected_version=0)
        with sqlite3.connect(self.db_path) as db:
            db.execute("DROP TRIGGER no_observation_updates")
            db.execute("UPDATE observations SET event_hash='0' WHERE seq=1")
        with self.assertRaises(IntegrityFailure):
            self.store.verify_integrity()

    def test_projection_status_tampering_is_detected(self):
        self.store.append(admit(sample(status="suspended")),expected_version=0)
        with sqlite3.connect(self.db_path) as db:
            db.execute("UPDATE projections SET outcome='source_verified' WHERE watch_ref='test:watch1'")
        with self.assertRaises(IntegrityFailure):
            self.store.verify_integrity()

    def test_lost_outbox_event_is_detected(self):
        self.store.append(admit(sample()),expected_version=0)
        with sqlite3.connect(self.db_path) as db:
            db.execute("DELETE FROM outbox")
        with self.assertRaises(IntegrityFailure):
            self.store.verify_integrity()

    def test_modified_review_history_is_detected(self):
        from registration_assurance.review import propose_review
        value=sample(status="suspended")
        candidate=admit(value)
        review=propose_review(None,value,candidate.assessment)
        self.store.save_review(review,expected_version=0)
        with sqlite3.connect(self.db_path) as db:
            db.execute("DROP TRIGGER no_review_events_update")
            db.execute("UPDATE review_events SET data_json='{}' WHERE version=1")
        with self.assertRaises(IntegrityFailure):
            self.store.verify_integrity()

    def test_missing_job_history_is_detected(self):
        from registration_assurance.jobs import create_job
        item=create_job(job_id="test:j1",watch_ref="test:watch1",provider_kind="MOCK",
            due_at_utc="2026-11-13T08:00:00Z",
            deadline_utc="2026-11-14T08:00:00Z",attempt_limit=2)
        self.store.save_job(item,expected_version=0)
        with sqlite3.connect(self.db_path) as db:
            db.execute("DROP TRIGGER no_job_events_delete")
            db.execute("DELETE FROM job_events WHERE job_id='test:j1'")
        with self.assertRaises(IntegrityFailure):
            self.store.verify_integrity()

    def test_internal_outbox_ack_is_cas_and_not_email(self):
        self.store.append(admit(sample()),expected_version=0)
        event=self.store.pending_outbox()[0]
        self.assertNotIn("recipient",event)
        self.store.acknowledge_event(event_id=event["eventId"],
            expected_version=1,receipt_ref="test:consumer-ack")
        self.assertEqual(self.store.pending_outbox(),[])
        with self.assertRaises(LedgerConflict):
            self.store.acknowledge_event(event_id=event["eventId"],
                expected_version=1,receipt_ref="test:duplicate-ack")

    def test_reopen_recovery_manifest_preserves_history_and_requires_review(self):
        self.store.append(admit(sample()),expected_version=0)
        result=DeterministicLedger(self.db_path).recovery_manifest()
        self.assertTrue(result["integrityOK"])
        self.assertEqual(result["observationCount"],1)
        self.assertEqual(result["watchCount"],1)
        self.assertEqual(result["projectionCount"],1)
        self.assertEqual(result["outstandingEvents"],1)
        self.assertFalse(result["outboundEmailEnabled"])
        self.assertTrue(result["requiresNativeReconciliation"])

    def test_review_cas_persists_exact_human_disposition(self):
        from registration_assurance.review import propose_review,apply_review
        observation=sample(status="suspended")
        admitted=admit(observation)
        self.store.append(admitted,expected_version=0)
        pending=propose_review(None,observation,admitted.assessment)
        self.store.save_review(pending,expected_version=0)
        reviewed=apply_review(
            pending,"held",actor_ref="test:reviewer",
            evidence_ref="test:receipt",expected_version=1,
            reviewed_at_utc=NOW)
        self.store.save_review(reviewed,expected_version=1)
        reopened=DeterministicLedger(self.db_path).read_review(pending["caseId"])
        self.assertEqual(reopened["reviewVersion"],2)
        self.assertFalse(reopened["practiceAuthorised"])
        with self.assertRaises(LedgerConflict):
            self.store.save_review(pending,expected_version=0)

    def test_job_lease_cas_persists_across_restarts(self):
        from registration_assurance.jobs import create_job,claim_job
        new=create_job(job_id="test:j1",watch_ref="test:watch1",provider_kind="MOCK",
            due_at_utc="2026-11-13T08:00:00Z",
            deadline_utc="2026-11-14T08:00:00Z",attempt_limit=2)
        self.store.save_job(new,expected_version=0)
        leased=claim_job(new,worker_ref="test:worker",
                         now_utc="2026-11-13T08:00:00Z",
                         lease_seconds=600,expected_version=1)
        self.store.save_job(leased,expected_version=1)
        self.assertEqual(DeterministicLedger(self.db_path).read_job("test:j1")["state"],"leased")
        with self.assertRaises(LedgerConflict):
            self.store.save_job(new,expected_version=0)

    def test_unapproved_sql_table_identifier_is_rejected(self):
        with self.assertRaises(LedgerConflict):
            self.store._save_versioned(
                "review_heads; DROP TABLE observations", "review_events", "case_id",
                "test:case", "test:watch1", 1,
                {"caseId": "test:case", "watchRef": "test:watch1",
                 "practiceAuthorised": False}, 0)
        self.assertTrue(self.store.verify_integrity())

    def test_case_id_resembling_sql_is_stored_only_as_bound_value(self):
        from registration_assurance.review import propose_review
        obs=sample(status="suspended")
        pending=propose_review(None,obs,admit(obs).assessment)
        pending["caseId"]="test:case'); DROP TABLE observations; --"
        self.store.save_review(pending,expected_version=0)
        self.assertIsNotNone(self.store.read_review(pending["caseId"]))
        self.assertTrue(self.store.verify_integrity())

    def test_refuse_forged_practice_grant_in_persistence(self):
        from registration_assurance.review import propose_review
        admitted=admit(sample(status="suspended"))
        pending=propose_review(None,admitted.observation,admitted.assessment)
        pending["practiceAuthorised"]=True
        with self.assertRaises(LedgerConflict):
            self.store.save_review(pending,expected_version=0)


if __name__ == "__main__":
    unittest.main()
