"""Source-only CAS recovery tests; no SharePoint access, credentials or human approvals."""
from __future__ import annotations

import importlib.util
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sys
import unittest

FILE = Path(__file__).resolve().parents[1] / "modules" / "careops-medical-job-planning" / "cas_contract.py"
SPEC = importlib.util.spec_from_file_location("mjp_cas_contract", FILE)
assert SPEC and SPEC.loader
M = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = M
SPEC.loader.exec_module(M)


def command(*, op='fixture:op-1', plan='fixture:plan-1', version='fixture:v1', expected=0,
            actor='fixture:actor-1', body=None):
    return M.SubmitCommand(
        plan_ref=plan, version_ref=version, operation_ref=op,
        expected_generation=expected, actor_evidence_ref=actor,
        payload={'sessions': [{'code': 'CST', 'minutes': '120'}]} if body is None else body,
    )


class CanonicalContract(unittest.TestCase):
    def test_permuted_mapping_has_identical_hash(self):
        self.assertEqual(M.canonical_sha256({'b': 2, 'a': {'x': True}}),
                         M.canonical_sha256({'a': {'x': True}, 'b': 2}))

    def test_json_number_and_unicode_guards(self):
        for bad in ({'x': 0.5}, {'x': float('nan')}, {'x': 2**53},
                    {'x': 'e\u0301'}, {5: 'not-string-key'}):
            with self.subTest(bad=repr(bad)), self.assertRaises(M.ProtocolError):
                M.canonical_sha256(bad)

    def test_expected_generation_never_coerces_bool(self):
        with self.assertRaises(M.ProtocolError):
            command(expected=True)

    def test_identifiers_are_source_qualified(self):
        with self.assertRaises(M.ProtocolError):
            command(plan='some-plain-id')


class CandidateSubmission(unittest.TestCase):
    def test_commit_is_candidate_not_approval(self):
        store = M.MemoryProtocolStore()
        source = {'sessions': [{'code': 'CST', 'minutes': '120'}]}
        result = M.submit_candidate(store, command(body=source))
        self.assertEqual(result.outcome, 'candidate_submitted')
        self.assertEqual(result.generation, 1)
        self.assertEqual(store.get_head('fixture:plan-1').generation, 1)
        self.assertEqual(store.get_head('fixture:plan-1').candidate_version_ref, 'fixture:v1')
        source['sessions'][0]['minutes'] = '9000'
        self.assertEqual(store.get_artifact(result.payload_sha256)['sessions'][0]['minutes'], '120')
        self.assertNotIn('approved', repr(result))

    def test_exact_replay_is_idempotent_and_no_new_head(self):
        store = M.MemoryProtocolStore()
        req = command()
        first = M.submit_candidate(store, req)
        second = M.submit_candidate(store, req)
        self.assertEqual(first, second)
        self.assertEqual(store.get_head(req.plan_ref).generation, 1)
        self.assertEqual(store.artifact_count, 1)

    def test_same_operation_different_payload_or_actor_rejected(self):
        store = M.MemoryProtocolStore()
        M.submit_candidate(store, command())
        for req in (command(body={'sessions': []}), command(actor='fixture:intruder'),
                    command(plan='fixture:plan-2')):
            with self.subTest(req=req), self.assertRaises(M.OperationConflict):
                M.submit_candidate(store, req)

    def test_prepare_crash_then_safe_replay(self):
        store = M.MemoryProtocolStore()
        req = command()
        with self.assertRaises(M.InjectedCrash):
            M.submit_candidate(store, req, fail_after='prepare')
        self.assertIsNone(store.get_head(req.plan_ref))
        self.assertEqual(store.reconcile(req.operation_ref), 'prepared_not_committed')
        done = M.submit_candidate(store, req)
        self.assertEqual(done.generation, 1)
        self.assertEqual(store.reconcile(req.operation_ref), 'committed')

    def test_commit_crash_recovered_without_double_commit(self):
        store = M.MemoryProtocolStore()
        req = command()
        with self.assertRaises(M.InjectedCrash):
            M.submit_candidate(store, req, fail_after='commit')
        self.assertEqual(store.get_head(req.plan_ref).generation, 1)
        self.assertEqual(store.reconcile(req.operation_ref), 'committed_recovered')
        receipt = M.submit_candidate(store, req)
        self.assertEqual(receipt.generation, 1)
        self.assertEqual(store.get_head(req.plan_ref).generation, 1)

    def test_late_replay_after_another_head_commit_recovers_from_history(self):
        store = M.MemoryProtocolStore()
        first = command()
        with self.assertRaises(M.InjectedCrash):
            M.submit_candidate(store, first, fail_after='commit')
        later = command(op='fixture:op-2', version='fixture:v2', expected=1,
                        body={'sessions': [{'code': 'CLIN', 'minutes': '60'}]})
        M.submit_candidate(store, later)
        self.assertEqual(store.get_head(first.plan_ref).generation, 2)
        self.assertEqual(store.reconcile(first.operation_ref), 'committed_recovered')
        receipt = M.submit_candidate(store, first)
        self.assertEqual(receipt.generation, 1)
        self.assertEqual(store.get_head(first.plan_ref).generation, 2)

    def test_concurrent_stale_writers_have_one_winner(self):
        store = M.MemoryProtocolStore()
        commands = [command(op=f'fixture:parallel-{i}', version=f'fixture:v{i}', expected=0)
                    for i in range(16)]
        def go(req):
            try:
                return M.submit_candidate(store, req).generation
            except M.StaleHead:
                return 'conflict'
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(go, commands))
        self.assertEqual(results.count(1), 1)
        self.assertEqual(results.count('conflict'), 15)
        self.assertEqual(store.get_head('fixture:plan-1').generation, 1)

    def test_staged_loser_is_quarantined_after_competitor_commit(self):
        store = M.MemoryProtocolStore()
        first = command()
        with self.assertRaises(M.InjectedCrash):
            M.submit_candidate(store, first, fail_after='prepare')
        other = command(op='fixture:other', version='fixture:v2', expected=0)
        M.submit_candidate(store, other)
        self.assertEqual(store.reconcile(first.operation_ref), 'quarantined_conflict')
        with self.assertRaises(M.StaleHead):
            M.submit_candidate(store, first)

    def test_frozen_snapshot_is_not_affected_by_caller_mutation(self):
        source = {'sessions': [{'minutes': '90'}]}
        req = command(body=source)
        original_sha = req.payload_sha256
        source['sessions'][0]['minutes'] = '9000'
        store = M.MemoryProtocolStore()
        result = M.submit_candidate(store, req)
        self.assertEqual(result.payload_sha256, original_sha)
        self.assertEqual(store.get_artifact(original_sha)['sessions'][0]['minutes'], '90')

    def test_stale_generation_does_not_overwrite_head(self):
        store = M.MemoryProtocolStore()
        M.submit_candidate(store, command())
        with self.assertRaises(M.StaleHead):
            M.submit_candidate(store, command(op='fixture:op-2', version='fixture:v2', expected=0))
        self.assertEqual(store.get_head('fixture:plan-1').candidate_version_ref, 'fixture:v1')

    def test_sequential_new_candidate_updates_head_not_issued_history(self):
        store = M.MemoryProtocolStore()
        M.submit_candidate(store, command())
        receipt = M.submit_candidate(store, command(op='fixture:op-2', version='fixture:v2', expected=1))
        self.assertEqual(receipt.generation, 2)
        self.assertEqual(store.artifact_count, 1)  # identical payload may be content-addressed
        self.assertEqual(store.get_head('fixture:plan-1').candidate_version_ref, 'fixture:v2')

    def test_unknown_failpoint_rejected_before_mutation(self):
        store = M.MemoryProtocolStore()
        with self.assertRaises(M.ProtocolError):
            M.submit_candidate(store, command(), fail_after='permissions_bypassed')
        self.assertIsNone(store.get_head('fixture:plan-1'))

    def test_uncommitted_operation_requires_explicit_replay_not_automatic_commit(self):
        store = M.MemoryProtocolStore()
        with self.assertRaises(M.InjectedCrash):
            M.submit_candidate(store, command(), fail_after='prepare')
        self.assertEqual(store.reconcile('fixture:op-1'), 'prepared_not_committed')
        self.assertIsNone(store.get_head('fixture:plan-1'))


if __name__ == '__main__':
    unittest.main()
