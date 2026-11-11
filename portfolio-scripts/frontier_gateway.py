"""A bounded, offline executor for **trusted, committed** CareOps source.

The gateway enforces its own two operations; it cannot intercept arbitrary MCP,
OS shell, GitHub or Microsoft tools. Tests are executable code, not a sandbox:
only run approved tests on a trusted checkout with external sandbox/network policy.
No credentials, login, network calls, tenant mutations or protected merges here.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from typing import Any

from engineering_frontier import FrontierError, _git, _safe_path, _tree, build_packet, guard_tool

MAX_READ_BYTES = 128 * 1024
MAX_TEST_SECONDS = 120
EXACT_PIN = "3.15.1"
TEST_ROOT = "portfolio-scripts/checks"
TEST_RUNNER = "portfolio-scripts/run_tests.py"
TEST_NAME = re.compile(r"test_[a-zA-Z0-9_]+\.py\Z")


@dataclass(frozen=True)
class TestReceipt:
    """Retain a bounded, content-free result; never log stdout/stderr or secrets."""

    source_sha: str
    selector: str
    status: str
    return_code: int | None
    stdout_sha256: str | None
    stderr_sha256: str | None
    stdout_bytes: int
    stderr_bytes: int
    qualification: str = "local-source-only"
    native_qualified: bool = False
    hosted_qualified: bool = False


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _env() -> dict[str, str]:
    """Deliberately minimal environment; not a substitute for process isolation."""
    result = {"PATH": os.defpath, "PYTHONDONTWRITEBYTECODE": "1",
              "PYTHONNOUSERSITE": "1", "PIP_DISABLE_PIP_VERSION_CHECK": "1"}
    if os.name == "nt":
        # Windows child processes require SystemRoot, but no user credential vars.
        for key in ("SYSTEMROOT", "WINDIR"):
            if os.getenv(key):
                result[key] = os.environ[key]
    return result


class Gateway:
    """Authenticate the *contents* of a supplied task packet against committed Git.

    Constructed only for trusted, locally-owned repository work. A packet is not
    an authorization token, and cannot grant privileges to other tools.
    """

    def __init__(self, root: Path, packet: dict[str, Any]):
        self.root = Path(root).resolve(strict=True)
        if not isinstance(packet, dict):
            raise FrontierError("packet-invalid")
        try:
            task = packet["task"]
            source_sha = packet["source"]["commit"]
            recomputed = build_packet(self.root, task["id"], source_sha,
                                      task["changed_paths"])
        except (KeyError, TypeError, ValueError) as exc:
            raise FrontierError("packet-invalid") from exc
        if packet != recomputed:
            raise FrontierError("packet-tampered-or-stale")
        self.packet = recomputed
        self.tree = _tree(self.root, source_sha)
        self.sha = source_sha
        self.allowed_paths = frozenset(task["changed_paths"] +
                                       [item["path"] for item in recomputed["context"]])
        self.allowed_operations = frozenset(recomputed["tools"]["allowed"])

    def read(self, path: str) -> tuple[bytes, dict[str, Any]]:
        """Read one allowed committed blob; return its content only to the caller.

        Receipt contains only path, SHA256 and size. Never logs the blob.
        """
        guard_tool("repo:read", self.allowed_operations)
        name = _safe_path(path)
        if name not in self.allowed_paths or name not in self.tree:
            raise FrontierError("read-out-of-scope")
        mode, oid = self.tree[name]
        local = self.root / name
        if mode not in {"100644", "100755"} or local.is_symlink() or not local.is_file():
            raise FrontierError("read-unsafe-file")
        size = _git(self.root, "cat-file", "-s", oid).decode("ascii").strip()
        if not size.isdecimal() or int(size) > MAX_READ_BYTES:
            raise FrontierError("read-size-limit")
        data = _git(self.root, "cat-file", "blob", oid)
        if len(data) != int(size):
            raise FrontierError("read-size-mismatch")
        expected = next((c["sha256"] for c in self.packet["context"]
                         if c["path"] == name), None)
        if expected is not None and _sha256(data) != expected:
            raise FrontierError("read-digest-mismatch")
        return data, {"path": name, "sha256": _sha256(data),
                      "bytes": len(data), "source_sha": self.sha,
                      "qualification": "committed-source-read"}

    def test(self, selector: str, python: Path, *, timeout: int = 60,
             trusted_checkout: bool = False) -> TestReceipt:
        """Execute ONE allowlisted local test, never arbitrary agent commands.

        This cannot sandbox an untrusted test file or prevent network I/O:
        the caller MUST isolate the trusted checkout using an external sandbox.
        """
        guard_tool("runner:focused-test", self.allowed_operations)
        if self.packet["tests"]["owner_selection_required"]:
            raise FrontierError("test-owner-selection-required")
        if not trusted_checkout:
            raise FrontierError("test-trusted-checkout-required")
        if (not isinstance(selector, str) or not TEST_NAME.fullmatch(selector)
                or f"{TEST_ROOT}/{selector}" not in self.packet["tests"]["selected"]):
            raise FrontierError("test-selector-denied")
        if not isinstance(timeout, int) or not 1 <= timeout <= MAX_TEST_SECONDS:
            raise FrontierError("test-timeout-invalid")
        path = f"{TEST_ROOT}/{selector}"
        if path not in self.tree or self.tree[path][0] != "100644":
            raise FrontierError("test-file-unverified")
        if (self.root / path).is_symlink():
            raise FrontierError("test-symlink-refused")
        # Running tests from a dirty checkout could execute changed/untrusted
        # working-tree files instead of the exact source packet.
        if _git(self.root, "status", "--porcelain", "--untracked-files=no").strip():
            raise FrontierError("test-dirty-checkout")
        py = Path(python)
        if (not py.is_absolute() or not py.is_file()
                or py.name not in {"python", "python3.15", "python.exe"}):
            raise FrontierError("test-runtime-invalid")
        # venv executables are often symlinks to system-managed Python. Only
        # the *parent directory* must resolve inside the checkout; no .. escape.
        if not py.parent.resolve(strict=True).is_relative_to(self.root):
            raise FrontierError("test-runtime-outside-checkout")
        executable = py
        # Avoid an environment-switched executable; verify the exact interpreter
        # selected by the repository. Does not invent Python 3.15 availability.
        verify = [str(executable), "-I", "-c",
                  "import sys,platform,pathlib; assert platform.python_version() == '3.15.1'; "
                  "assert sys.prefix != sys.base_prefix; "
                  "assert pathlib.Path(sys.prefix).resolve().is_relative_to(pathlib.Path.cwd())"]
        try:
            verified = subprocess.run(verify, cwd=self.root, env=_env(),
                                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                      timeout=10, check=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise FrontierError("test-runtime-unavailable") from exc
        if verified.returncode:
            raise FrontierError("test-runtime-unqualified")
        command = [str(executable), "-I", TEST_RUNNER, "--runner", "unittest",
                   "--mode", "focused", "--tests-root", TEST_ROOT, selector]
        try:
            with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
                execution = subprocess.run(command, cwd=self.root, env=_env(),
                                           stdout=stdout, stderr=stderr,
                                           timeout=timeout, check=False)
                stdout.flush()
                stderr.flush()
                stdout.seek(0)
                stderr.seek(0)
                def measure(stream):
                    digest = hashlib.sha256()
                    total = 0
                    for chunk in iter(lambda: stream.read(65536), b""):
                        total += len(chunk)
                        digest.update(chunk)
                    return digest.hexdigest(), total
                out_hash, out_len = measure(stdout)
                err_hash, err_len = measure(stderr)
        except subprocess.TimeoutExpired as exc:
            raise FrontierError("test-timeout") from exc
        except OSError as exc:
            raise FrontierError("test-execution-unavailable") from exc
        return TestReceipt(source_sha=self.sha, selector=selector,
                           status="passed" if execution.returncode == 0 else "failed",
                           return_code=execution.returncode,
                           stdout_sha256=out_hash,
                           stderr_sha256=err_hash,
                           stdout_bytes=out_len,
                           stderr_bytes=err_len)
