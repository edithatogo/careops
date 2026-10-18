from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import cast

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "portfolio" / "credentialing-mvp-compatibility.json"
RECEIPT = ROOT / "portfolio" / "releases" / "credentialing-mvp-0.1.json"
SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")


def load_object(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        message = f"Expected JSON object: {path}"
        raise TypeError(message)
    return cast("dict[str, object]", value)


def current_gitlink(path: str) -> str:
    completed = subprocess.run(
        ["git", "ls-files", "--stage", "--", path],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    fields = completed.stdout.strip().split()
    if len(fields) < 4 or fields[0] != "160000":
        message = f"Expected a gitlink at {path}"
        raise ValueError(message)
    return fields[1]


def main() -> int:
    manifest = load_object(MANIFEST)
    receipt = load_object(RECEIPT)
    modules = cast("dict[str, dict[str, object]]", manifest["modules"])
    release_modules = {
        cast("str", item["repository"]): cast("str", item["commit"])
        for item in cast("list[dict[str, object]]", receipt["modules"])
    }
    errors: list[str] = []

    for name, module in modules.items():
        commit = cast("str", module.get("commit", ""))
        if SHA_PATTERN.fullmatch(commit) is None:
            errors.append(f"{name} has no immutable commit pin")
        repository = cast("str", module.get("repository", ""))
        receipt_commit = release_modules.get(repository)
        if receipt_commit != commit:
            errors.append(f"{name} manifest and release receipt pins differ")

    approve_commit = cast("str", modules["careops-approve"]["commit"])
    gitlink_commit = current_gitlink("careops-approve")
    if gitlink_commit != approve_commit:
        errors.append(
            "careops-approve gitlink differs from the compatibility manifest: "
            f"{gitlink_commit} != {approve_commit}"
        )

    if errors:
        for error in errors:
            print(f"[FAIL] {error}")
        return 1
    print("Credentialing release pin validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
