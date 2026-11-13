"""A single, fictional end-to-end source-only workflow; no approval capability."""
from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1] / 'modules' / 'careops-medical-job-planning'


def load(name):
    path = ROOT / (name + '.py')
    spec = spec_from_file_location('mjp_fictional_' + name, path)
    assert spec and spec.loader
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


DOMAIN = load('domain')
CAS = load('cas_contract')
NEG = load('negotiation')
RECORDS = load('plan_records')
RULES = load('policy_rules')
NOW = datetime(2026, 11, 13, tzinfo=timezone.utc)


class FictionalVerticalSlice(unittest.TestCase):
    def test_candidate_negotiation_is_not_an_issued_plan(self):
        store = CAS.MemoryProtocolStore()
        payload = {'sessions': [{'week': 1, 'day': 1, 'ordinary': True,
                                 'cst': True, 'code': 'fictional-CST',
                                 'site': 'FICTIONAL', 'start_min': 480,
                                 'end_min': 720}]}
        DOMAIN.validate_cycle(DOMAIN.activities_from_sessions(payload['sessions']), 2)
        cmd = CAS.SubmitCommand(
            plan_ref='fixture:plan', version_ref='fixture:version-1',
            operation_ref='fixture:submission-1', expected_generation=0,
            actor_evidence_ref='fixture:unverified-practitioner', payload=payload,
        )
        receipt = CAS.submit_candidate(store, cmd)
        self.assertEqual(receipt.outcome, 'candidate_submitted')
        self.assertEqual(store.get_head(cmd.plan_ref).generation, 1)

        rules = RULES.RulePack(
            rule_key='fixture:rule', edition='fictional-edition',
            source_ref='fixture:industrial-reference', source_sha256='a' * 64,
            clause_ref='fixture:clause', effective_from=date(2026, 1, 1),
            effective_to=None, status='reference_only', adoption_ref=None,
            eligible_classifications=frozenset({'fixture:SMO'}),
            fraction=Decimal('0.10'),
        )
        assessment = RULES.assess_cst(
            rules, classification='fixture:SMO', as_of=date(2026, 11, 13),
            contracted_hours='80', planned_hours='4', observed_hours=None,
            verified_contract=False,
        )
        self.assertEqual(assessment['eligibility'], 'source_unverified')
        self.assertFalse(assessment['rules_operative'])
        self.assertFalse(assessment['approval_allowed'])

        thread = NEG.Thread(cmd.plan_ref, cmd.version_ref, receipt.payload_sha256,
                            0, 'submitted', ())
        stages = ('propose', 'counterpropose', 'propose', 'record_consensus',
                  'request_authorisation')
        for ix, stage in enumerate(stages):
            event = NEG.NegotiationEvent(
                operation_id=f'fixture:negotiation-{ix}', kind=stage,
                actor_ref='fixture:unverified-actor', role_ref='fixture:unverified-role',
                evidence_ref=f'fixture:negotiation-evidence-{ix}',
                payload_sha256=receipt.payload_sha256, occurred_at=NOW,
            )
            thread = NEG.advance(thread, event, thread.generation)
        self.assertEqual(thread.state, 'authority_pending')
        self.assertEqual(thread.generation, len(stages))
        self.assertNotIn(thread.state, ('issued', 'approved', 'active'))

        with self.assertRaises(RECORDS.VersionError):
            RECORDS.PlanVersion(
                plan_ref='fixture:plan', version_ref='fixture:version-1',
                submitted_sha256=receipt.payload_sha256,
                policy_snapshot_ref='fixture:rule', appointment_ref='fixture:appointment',
                position_ref='fixture:position', service_assignment_ref='fixture:service',
                effective_from=date(2026, 11, 13), effective_to=None,
                issued_at=NOW, decision_evidence_ref=None, state='issued',
            )
        submitted = RECORDS.PlanVersion(
            plan_ref='fixture:plan', version_ref='fixture:version-1',
            submitted_sha256=receipt.payload_sha256,
            policy_snapshot_ref='fixture:rule', appointment_ref='fixture:appointment',
            position_ref='fixture:position', service_assignment_ref='fixture:service',
            effective_from=date(2026, 11, 13), effective_to=None,
            issued_at=None, decision_evidence_ref=None, state='submitted',
        )
        projection = RECORDS.read_as_of(
            [submitted], plan_ref='fixture:plan', date_as_of=date(2026, 11, 13),
            observed_at=NOW, source_read_complete=True,
        )
        self.assertEqual(projection['status'], 'not_issued')
        self.assertFalse(projection['authority_verified'])


if __name__ == '__main__':
    unittest.main()
