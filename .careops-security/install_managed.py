# Copyright (c) 2026 CareOps contributors.
# SPDX-License-Identifier: Apache-2.0
"""Add reviewed guards to the actual installed managed hook; never replace its chain."""

import fcntl
import hashlib
import json
import os
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

FILES = (
    "pre_push.py",
    "presidio_scan.py",
    "presidio-policy.json",
    "presidio-reviewed-findings.json",
    "presidio-reviewed-costing.json",
    "presidio-reviewed-decisions.json",
    "redact_legacy.py",
)


def main():
    root = Path(
        subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"], text=True
        ).strip()
    ).resolve()
    common = Path(
        subprocess.check_output(
            ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
            text=True,
        ).strip()
    )
    bundle, source = common / "careops-privacy-hooks-v1", root / ".careops-security"
    if any(
        path.is_symlink()
        for path in [
            bundle,
            bundle / "hooks",
            bundle / "presidio-guards",
            bundle / "presidio-hook-installation.json",
        ]
    ):
        raise ValueError("linked_installation")
    if (
        sys.version_info[:3] != (3, 15, 1)
        or Path(sys.prefix).resolve() != root / ".venv-careops-privacy-hooks"
    ):
        raise ValueError("runtime")
    expected = str(bundle / "hooks")
    if (
        subprocess.check_output(
            ["git", "config", "--get", "core.hooksPath"], text=True
        ).strip()
        != expected
    ):
        raise ValueError("ownership")
    # This updates a known installed dispatcher only. Other installers remain untouched.
    registry = json.loads((bundle / "registry.json").read_text())
    if str(root) not in registry["checkouts"] or not (bundle / "dispatch.py").is_file():
        raise ValueError("registration")
    payload = {}
    for name in FILES:
        path = source / name
        if path.is_symlink():
            raise ValueError("linked_source")
        payload[name] = path.read_bytes()
    fingerprint = hashlib.sha256(
        b"".join(name.encode() + b"\0" + payload[name] for name in FILES)
    ).hexdigest()
    target = bundle / "presidio-guards" / fingerprint
    (bundle / "presidio-guards").mkdir(mode=0o700, exist_ok=True)
    if not target.exists():
        target.mkdir(mode=0o700)
        for name, data in payload.items():
            (target / name).write_bytes(data)
    if target.is_symlink() or any(
        (target / name).read_bytes() != data for name, data in payload.items()
    ):
        raise ValueError("snapshot")
    receipt_path = bundle / "presidio-hook-installation.json"
    with (bundle / "presidio-install.lock").open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        prior = json.loads(receipt_path.read_text()) if receipt_path.exists() else None
        old_hashes = prior["installedHookHashes"] if prior else None
        before = {
            event: (bundle / "hooks" / event).read_bytes()
            for event in ["pre-commit", "pre-push"]
        }
        for event, data in before.items():
            if old_hashes:
                if hashlib.sha256(data).hexdigest() != old_hashes[event]:
                    raise ValueError("hook_changed")
            elif (
                str(bundle / "dispatch.py").encode() not in data or b"presidio" in data
            ):
                raise ValueError("unrecognised_hook")
        if not prior:
            for event, data in before.items():
                (bundle / (event + ".before-presidio")).write_bytes(data)
        driver = '"$checkout_root/.venv-careops-privacy-hooks/bin/python" -I '
        header = "#!/bin/sh\nset -eu\ncheckout_root=$(git rev-parse --show-toplevel)\n"
        command = driver + (
            shlex.quote(str(target / "pre_push.py"))
            + " --legacy "
            + shlex.quote(str(bundle / "dispatch.py"))
            + ' "$@"'
        )
        push = (
            header
            + "if CAREOPS_NOTIFICATION_WRAPPED=1 "
            + command
            + " >/dev/null 2>&1; then\n"
        )
        push += "  echo 'CareOps private destination and offline privacy guards passed.'\n  exit 0\nfi\n"
        push += "echo 'CareOps push blocked; diagnostic content withheld.' >&2\n"
        push += 'if [ -z "${CI:-}" ] && [ "$(uname -s)" = Darwin ]; then\n'
        push += '  osascript -e \'display notification "Push blocked. Review the local privacy gate." with title "CareOps privacy"\' >/dev/null 2>&1 || true\nfi\nexit 1\n'
        command = driver + (
            shlex.quote(str(target / "redact_legacy.py"))
            + " "
            + shlex.quote(str(bundle / "dispatch.py"))
            + ' pre-commit "$@"'
        )
        commit = (
            header
            + "if "
            + command
            + " >/dev/null 2>&1; then\n  echo 'Existing commit guards passed.'\n  exit 0\nfi\n"
        )
        commit += "echo 'Commit blocked; diagnostic content withheld.' >&2\nexit 1\n"
        installed, prepared, replaced = {}, {}, []
        try:
            for event, text in [("pre-push", push), ("pre-commit", commit)]:
                path = bundle / "hooks" / event
                if path.is_symlink() or path.read_bytes() != before[event]:
                    raise ValueError("concurrent_hook_change")
                fd, name = tempfile.mkstemp(prefix=".presidio-hook-", dir=path.parent)
                prepared[event] = Path(name)
                with os.fdopen(fd, "w") as stream:
                    stream.write(text)
                    stream.flush()
                    os.fsync(stream.fileno())
                os.chmod(name, 0o700)
                installed[event] = hashlib.sha256(text.encode()).hexdigest()
            for event, temporary in prepared.items():
                path = bundle / "hooks" / event
                if path.is_symlink() or path.read_bytes() != before[event]:
                    raise ValueError("concurrent_hook_change")
                os.replace(temporary, path)
                replaced.append(event)
                if hashlib.sha256(path.read_bytes()).hexdigest() != installed[event]:
                    raise ValueError("readback")
        except Exception:
            for event in reversed(replaced):
                path = bundle / "hooks" / event
                if (
                    not path.is_symlink()
                    and hashlib.sha256(path.read_bytes()).hexdigest()
                    == installed[event]
                ):
                    path.write_bytes(before[event])
            raise
        finally:
            for temporary in prepared.values():
                temporary.unlink(missing_ok=True)
        receipt = {
            "sourceFingerprint": fingerprint,
            "snapshot": str(target),
            "installedHookHashes": installed,
            "legacyDispatcherPreserved": True,
            "privateDestinationRequired": True,
            "missingRuntimeOrModelBlocksPush": True,
        }
        receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(
        "Managed pre-push guard installed and read back; original chain preserved. Missing scanner/model blocks pushes."
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:  # noqa: BLE001 -- installer failures must not disclose local paths/state
        print(
            "Managed hook installation refused; no diagnostic content logged.",
            file=sys.stderr,
        )
        raise SystemExit(1)
