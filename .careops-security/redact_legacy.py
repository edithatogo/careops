# Copyright (c) 2026 CareOps contributors.
# SPDX-License-Identifier: Apache-2.0
"""Preserve the installed legacy hook chain while withholding its raw diagnostics."""

import subprocess
import sys

try:
    outcome = subprocess.run(
        [sys.executable, "-I", *sys.argv[1:]],
        capture_output=True,
        check=False,
        timeout=600,
    )
    code = outcome.returncode
except Exception:  # noqa: BLE001 -- retain nonzero status without disclosing legacy diagnostics
    code = 1
print(
    "Existing privacy guards passed."
    if code == 0
    else "Existing privacy guards blocked; diagnostics withheld."
)
raise SystemExit(code)
