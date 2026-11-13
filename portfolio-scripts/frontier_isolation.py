"""Linux-only fail-closed isolation for trusted CareOps focused test execution.

Uses bubblewrap OS mount/network/PID/user isolation. This is a *bounded
containerised process*, not a proof that hostile code is safe: require a trusted
checkout, host user namespace policy, resource limits and normal CI protection.
If bubblewrap is absent or denied, this module refuses rather than falls back.
"""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
from typing import IO, Sequence

from engineering_frontier import FrontierError

BWRAP = Path("/usr/bin/bwrap")
MAX_SECONDS = 120
RUNTIME_PROBE = ("import sys,platform,pathlib; "
                 "assert platform.python_version() == '3.15.1'; "
                 "assert sys.prefix != sys.base_prefix; "
                 "assert pathlib.Path(sys.prefix).resolve().is_relative_to(pathlib.Path.cwd())")


def isolated_argv(root: Path, command: Sequence[str]) -> list[str]:
    """Map a repository-local interpreter into read-only /work, nothing else."""
    if sys.platform != "linux":
        raise FrontierError("sandbox-platform-unsupported")
    root = root.resolve(strict=True)
    if not root.is_dir() or not command or not all(isinstance(x, str) and x for x in command):
        raise FrontierError("sandbox-command-invalid")
    executable = Path(command[0])
    if not executable.is_absolute() or not executable.parent.resolve().is_relative_to(root):
        raise FrontierError("sandbox-command-outside-repository")
    if executable.name not in {"python", "python3.15", "python.exe"}:
        raise FrontierError("sandbox-executable-invalid")
    relative = executable.relative_to(root)
    if ".." in relative.parts or len(command) > 18:
        raise FrontierError("sandbox-command-invalid")
    # Never allow a shell or arbitrary Python arguments through this entry point.
    if len(command) < 3 or command[1] != "-I":
        raise FrontierError("sandbox-unisolated-python")
    if command[2] not in {"-c", "portfolio-scripts/run_tests.py"}:
        raise FrontierError("sandbox-unsupported-command")
    if command[2] == "portfolio-scripts/run_tests.py":
        exact = ["--runner", "unittest", "--mode", "focused",
                 "--tests-root", "portfolio-scripts/checks"]
        if command[3:3 + len(exact)] != exact or len(command) != 3 + len(exact) + 1:
            raise FrontierError("sandbox-test-command-invalid")
        if not command[-1].startswith("test_") or not command[-1].endswith(".py"):
            raise FrontierError("sandbox-test-name-invalid")
        if "/" in command[-1] or "\\" in command[-1] or ".." in command[-1]:
            raise FrontierError("sandbox-test-name-invalid")
    else:
        if len(command) != 4 or command[3] != RUNTIME_PROBE:
            raise FrontierError("sandbox-runtime-check-invalid")
    base = ["--unshare-all", "--die-with-parent", "--new-session",
            "--cap-drop", "ALL", "--clearenv", "--tmpfs", "/",
            "--ro-bind", str(root), "/work",
            "--tmpfs", "/tmp", "--proc", "/proc", "--dev", "/dev",
            "--setenv", "HOME", "/tmp", "--setenv", "TMPDIR", "/tmp",
            "--setenv", "PATH", "/usr/bin:/bin",
            "--setenv", "PYTHONDONTWRITEBYTECODE", "1",
            "--setenv", "PYTHONNOUSERSITE", "1",
            "--chdir", "/work"]
    for location in ("/usr", "/bin", "/lib", "/lib64"):
        if Path(location).exists():
            base.extend(["--ro-bind", location, location])
    return [str(BWRAP), *base, "--", "/work/" + relative.as_posix(), *command[1:]]


def run_isolated(root: Path, command: Sequence[str], *, timeout: int,
                 stdout: IO[bytes] | int, stderr: IO[bytes] | int) -> subprocess.CompletedProcess:
    if (type(timeout) is not int or timeout < 1 or timeout > MAX_SECONDS):
        raise FrontierError("sandbox-timeout-invalid")
    if not BWRAP.is_file():
        raise FrontierError("sandbox-bubblewrap-unavailable")
    argv = isolated_argv(root, command)
    try:
        return subprocess.run(argv, cwd=root, env={"PATH": os.defpath},
                              stdout=stdout, stderr=stderr,
                              timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise FrontierError("sandbox-execution-failed") from exc
