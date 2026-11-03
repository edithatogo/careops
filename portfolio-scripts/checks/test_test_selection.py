"""Selection regressions: failures-only must not expand to an entire suite."""
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location('run_tests', Path(__file__).parents[1] / 'run_tests.py')
if SPEC is None or SPEC.loader is None:
    raise RuntimeError('Could not load test runner module')
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


class SelectionTests(unittest.TestCase):
    def command(self, mode, selectors=None, no_cov=False):
        cache = str(Path(tempfile.gettempdir()) / 'careops-test-cache')
        return RUNNER.commands('pytest', mode, selectors or [], 'tests', cache, no_cov)[0]

    def test_last_failed_never_falls_back_to_all(self):
        command = self.command('last-failed')
        self.assertIn('--last-failed-no-failures=none', command)

    def test_failed_first_retains_all_tests(self):
        self.assertEqual(self.command('failed-first')[-2:], ['--failed-first', 'tests'])

    def test_stepwise_is_explicit(self):
        self.assertIn('--stepwise', self.command('stepwise'))

    def test_focused_requires_selection(self):
        with self.assertRaises(ValueError):
            self.command('focused')

    def test_focused_preserves_exact_node(self):
        self.assertEqual(self.command('focused', ['tests/test_a.py::test_one'])[-1],
                         'tests/test_a.py::test_one')

    def test_full_does_not_use_failure_cache_or_no_cov(self):
        command = self.command('full', no_cov=True)
        self.assertNotIn('--no-cov', command)
        self.assertNotIn('--last-failed', command)
        self.assertEqual(command[-1], 'tests')

    def test_focused_coverage_is_not_full_coverage(self):
        self.assertIn('--no-cov', self.command('focused', ['tests/test_a.py'], True))

    def test_refuse_option_as_selector(self):
        with self.assertRaises(ValueError):
            self.command('focused', ['--ignore=tests'])

    def test_refuse_parent_traversal(self):
        with self.assertRaises(ValueError):
            self.command('focused', ['../other/test_a.py'])

    def test_refuse_absolute_path(self):
        with self.assertRaises(ValueError):
            absolute = str(Path(tempfile.gettempdir()) / 'test_a.py')
            self.command('focused', [absolute])

    def test_unittest_patterns_remain_focused(self):
        cache = str(Path(tempfile.gettempdir()) / 'careops-test-cache')
        commands = RUNNER.commands('unittest', 'focused', ['test_a.py'], 'checks', cache)
        self.assertEqual(commands, [[sys.executable, '-m', 'unittest', 'discover',
                                    '-s', 'checks', '-p', 'test_a.py', '-v']])

    def test_unittest_refuses_pytest_mode(self):
        with self.assertRaises(ValueError):
            RUNNER.commands('unittest', 'last-failed', [], 'tests',
                            str(Path(tempfile.gettempdir()) / 'careops-test-cache'))


if __name__ == '__main__':
    unittest.main()
