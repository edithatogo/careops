"""Synthetic offline CI evidence regressions; no GitHub API or secrets."""
import unittest
from frontier_ci_evidence import classify_snapshot, EvidenceError

SHA = 'a' * 40


def check(name='Security gate', conclusion='success', head=SHA, run_id=10,
          steps=None, annotations=None):
    return {'name': name, 'head_sha': head, 'status': 'completed',
            'conclusion': conclusion, 'check_run_id': run_id,
            'steps': [{'name': 'Run tests', 'status': 'completed', 'conclusion': 'success'}]
            if steps is None else steps,
            'annotations': [] if annotations is None else annotations}


def snapshot(**updates):
    record = {'schema_version': 1, 'head_sha': SHA,
              'required': ['Security gate', 'Privacy and secrets'],
              'checks': [check(), check('Privacy and secrets', run_id=11)]}
    record.update(updates)
    return record


class TestEvidence(unittest.TestCase):
    def test_green_only_with_real_steps(self):
        result = classify_snapshot(snapshot())
        self.assertEqual(result['state'], 'passed-executed')
        self.assertFalse(result['protected_merge_qualified'])
        self.assertEqual(result['required_count'], 2)
        self.assertEqual(result['unqualified'], [])
        self.assertNotIn('annotations', str(result))

    def test_green_no_steps_is_unverified(self):
        evidence = snapshot(checks=[check(steps=[]), check('Privacy and secrets', run_id=11)])
        result = classify_snapshot(evidence)
        self.assertEqual(result['state'], 'unverified')
        self.assertEqual(result['unqualified'][0]['reason'], 'no-executed-steps')

    def test_billing_is_blocked_not_failed_execution(self):
        evidence = snapshot(checks=[check(conclusion='failure', steps=[], annotations=[
            {'message': 'The job was not started because recent account payments have failed or your spending limit needs to be increased.'}]),
            check('Privacy and secrets', run_id=11)])
        result = classify_snapshot(evidence)
        self.assertEqual(result['state'], 'billing-blocked')
        self.assertNotIn('payments', str(result))

    def test_mixed_executed_failure_and_billing_is_failure(self):
        evidence = snapshot(checks=[check(conclusion='failure', steps=[
            {'status': 'completed', 'conclusion': 'failure'}],
            annotations=[{'message': 'billing spending limit'}]),
            check('Privacy and secrets', run_id=11)])
        self.assertEqual(classify_snapshot(evidence)['state'], 'executed-failure')

    def test_unexecuted_failure_not_code_failure(self):
        evidence = snapshot(checks=[check(conclusion='failure', steps=[]),
                                    check('Privacy and secrets', run_id=11)])
        self.assertEqual(classify_snapshot(evidence)['state'], 'unverified')

    def test_missing_duplicate_wrong_head_are_rejected(self):
        for checks in [[check()],
                       [check(), check(), check('Privacy and secrets', run_id=11)],
                       [check(head='b' * 40), check('Privacy and secrets', run_id=11)]]:
            with self.subTest(checks=checks):
                result = classify_snapshot(snapshot(checks=checks))
                self.assertNotEqual(result['state'], 'passed-executed')
                self.assertTrue(result['unqualified'])

    def test_nonterminal_and_skipped_are_not_success(self):
        for changes in [{'status': 'queued'}, {'conclusion': 'skipped'},
                        {'conclusion': None}]:
            altered = check()
            altered.update(changes)
            result = classify_snapshot(snapshot(checks=[
                altered, check('Privacy and secrets', run_id=11)]))
            self.assertNotEqual(result['state'], 'passed-executed')

    def test_partial_failed_steps_are_not_success(self):
        evidence = snapshot(checks=[check(steps=[
            {'status': 'completed', 'conclusion': 'skipped'}]),
            check('Privacy and secrets', run_id=11)])
        self.assertNotEqual(classify_snapshot(evidence)['state'], 'passed-executed')

    def test_no_external_annotations_or_names(self):
        evidence = snapshot(checks=[check(conclusion='failure', steps=[],
            annotations=[{'message': 'access_token=topsecret@example.invalid'}]),
            check('Privacy and secrets', run_id=11)])
        self.assertNotIn('topsecret', str(classify_snapshot(evidence)))

    def test_schema_validation(self):
        cases = [snapshot(head_sha='z' * 40), snapshot(required=[]),
                 snapshot(required=['Security gate'] * 2),
                 snapshot(checks=['bad']), snapshot(schema_version=5),
                 snapshot(required='Security gate')]
        for bad in cases:
            with self.subTest(bad=bad), self.assertRaises(EvidenceError):
                classify_snapshot(bad)

    def test_repeated_calls_identical(self):
        self.assertEqual(classify_snapshot(snapshot()), classify_snapshot(snapshot()))


if __name__ == '__main__':
    unittest.main()
