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


def validate_current_approve_pin(
    released: str, current: str, qualification: dict[str, object], publication: dict[str, object],
) -> list[str]:
    """Keep historical releases immutable; require an explicit qualified source pin."""
    if current == released:
        return []
    qualified = cast("dict[str, str]", qualification.get("modules", {}))
    baseline = cast("dict[str, str]", qualification.get("releaseBaseline", {}))
    reviewed = cast("dict[str, str]", publication.get("gitlinks", {}))
    contracts = cast("dict[str, str]", qualification.get("unchangedReleaseContracts", {}))
    required = {
        "contracts/credentialing-governance-packet.schema.json",
        "contracts/credentialing-result.schema.json",
        "contracts/existing-system-source-record.schema.json",
    }
    if (
        qualified.get("careops-approve") != current
        or reviewed.get("careops-approve") != current
        or baseline.get("careops-approve") != released
        or set(contracts) != required
        or any(re.fullmatch(r"[a-f0-9]{64}", digest) is None for digest in contracts.values())
    ):
        return ["Current Approve gitlink lacks exact reviewed source/baseline/contract qualification"]
    return []


def validate_current_process_pin(
    current: str, qualification: dict[str, object], publication: dict[str, object], topology: dict[str, object],
) -> list[str]:
    """Keep optional composition and the actual consumer on one reviewed revision."""
    qualified = cast("dict[str, str]", qualification.get("modules", {}))
    reviewed = cast("dict[str, str]", publication.get("gitlinks", {}))
    components = cast("list[dict[str, object]]", topology.get("components", []))
    selected = [item for item in components if item.get("name") == "careops-process"]
    if (
        SHA_PATTERN.fullmatch(current) is None
        or qualified.get("careops-process") != current
        or reviewed.get("modules/careops-process") != current
        or len(selected) != 1
        or selected[0].get("publicSourceCommit") != current
        or selected[0].get("path") != "modules/careops-process"
    ):
        return ["Current Process gitlink lacks matching consumer/publication/composition qualification"]
    return []


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
    errors.extend(validate_current_approve_pin(
        approve_commit, gitlink_commit,
        load_object(ROOT / "portfolio" / "public-runtime-compatibility.json"),
        load_object(ROOT / "PUBLIC_SOURCE_FILES.json"),
    ))
    qualification = load_object(ROOT / "portfolio/public-runtime-compatibility.json")
    publication = load_object(ROOT / "PUBLIC_SOURCE_FILES.json")
    topology = load_object(ROOT / "portfolio/repos.json")
    errors.extend(validate_current_process_pin(
        current_gitlink("modules/careops-process"), qualification, publication, topology,
    ))

    if errors:
        for error in errors:
            print(f"[FAIL] {error}")
        return 1
    print("Credentialing release pin validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
