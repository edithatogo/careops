"""Synthetic sandbox command and fail-closed execution tests; no bubblewrap launch."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engineering_frontier import FrontierError
from frontier_isolation import isolated_argv, run_isolated


class IsolationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.python = self.root / ".venv/bin/python"
        self.python.parent.mkdir(parents=True)
        self.python.touch()

    def tearDown(self):
        self.temp.cleanup()

    def test_command_uses_network_and_user_isolation(self):
        argv = isolated_argv(self.root, [str(self.python), "-I", "-c", "print(1)"])
        self.assertIn("--unshare-all", argv)
        self.assertIn("--clearenv", argv)
        self.assertIn("--die-with-parent", argv)
        self.assertIn("--cap-drop", argv)
        self.assertIn("--ro-bind", argv)
        self.assertIn("--tmpfs", argv)
        self.assertIn("/work/.venv/bin/python", argv)
        self.assertNotIn("--share-net", argv)
        self.assertNotIn("--bind", argv)
        self.assertNotIn(str(Path.home()), argv)

    def test_exact_test_command_accepted(self):
        argv = isolated_argv(self.root, [
            str(self.python), "-I", "portfolio-scripts/run_tests.py",
            "--runner", "unittest", "--mode", "focused", "--tests-root",
            "portfolio-scripts/checks", "test_frontier_gateway.py"])
        self.assertEqual(argv[-1], "test_frontier_gateway.py")

    def test_shell_and_outside_executable_rejected(self):
        for command in [["/bin/sh", "-c", "id"], ["/usr/bin/python", "-I", "-c", "print(1)"],
                        [str(self.python), "-c", "print(1)"],
                        [str(self.python), "-I", "random.py"]]:
            with self.subTest(command=command), self.assertRaises(FrontierError):
                isolated_argv(self.root, command)

    def test_test_runner_cannot_accept_extra_flags(self):
        base = [str(self.python), "-I", "portfolio-scripts/run_tests.py",
                "--runner", "unittest", "--mode", "focused",
                "--tests-root", "portfolio-scripts/checks"]
        for extra in [["--ignore=tests"], ["../../secrets.py"], ["test_a.py", "--exitfirst"],
                      ["not_a_test.py"]]:
            with self.subTest(extra=extra), self.assertRaises(FrontierError):
                isolated_argv(self.root, base + extra)

    def test_unavailable_binary_refuses_and_never_runs_python_directly(self):
        with patch("frontier_isolation.BWRAP", Path("/nonexistent/frontier-bwrap")):
            with patch("frontier_isolation.subprocess.run") as run:
                with self.assertRaisesRegex(FrontierError, "sandbox-bubblewrap-unavailable"):
                    run_isolated(self.root, [str(self.python), "-I", "-c", "print(1)"],
                                 timeout=10, stdout=-3, stderr=-3)
                run.assert_not_called()

    def test_invalid_timeout_rejected(self):
        for timeout in [-1, 0, 121, 1.5, True]:
            with self.subTest(timeout=timeout), self.assertRaises(FrontierError):
                run_isolated(self.root, [str(self.python), "-I", "-c", "print(1)"],
                             timeout=timeout, stdout=-3, stderr=-3)

    def test_missing_platform_is_refused(self):
        with patch("frontier_isolation.sys.platform", "win32"):
            with self.assertRaisesRegex(FrontierError, "sandbox-platform"):
                isolated_argv(self.root, [str(self.python), "-I", "-c", "print(1)"])


if __name__ == "__main__":
    unittest.main()
