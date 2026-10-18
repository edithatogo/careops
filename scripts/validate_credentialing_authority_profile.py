from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import cast

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "portfolio" / "credentialing-authority-profile.example.json"
COMMIT_SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")

REQUIRED_SOURCE_IDS = {
    "acsqhc-credentialing-guidance-2026",
    "qld-health-hsd-034",
    "schn-model-scopes-medical-surgical",
    "schn-model-scopes-paediatric",
    "schn-model-scopes-dental",
    "amc-rural-generalist-recognition",
    "medical-board-rural-generalist-recognition-2025",
    "medical-board-specialty-recognition-faq",
    "acrrm-rural-generalist-registration-2026",
    "acrrm-rural-generalist-program-accreditation-2026",
    "racgp-additional-rural-skills-2026",
    "ahpra-specialist-registration",
}


def load_profile() -> dict[str, object]:
    value = json.loads(PROFILE.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        msg = "Credentialing authority profile must be a JSON object"
        raise TypeError(msg)
    return cast("dict[str, object]", value)


def main() -> int:
    profile = load_profile()
    source_collection = cast(
        "dict[str, object]",
        profile.get("sourceCollection", {}),
    )
    pinned_commit = cast("str", source_collection.get("releaseOrCommit", ""))
    sources = cast("list[dict[str, object]]", profile.get("sources", []))
    source_ids = {cast("str", source.get("sourceId")) for source in sources}
    status_rule = cast("dict[str, object]", profile.get("sourceStatusRule", {}))
    catalogue = cast("dict[str, object]", profile.get("modelCatalogue", {}))
    automation = cast("dict[str, object]", profile.get("automationBoundary", {}))

    checks = {
        "profile remains design-only": profile.get("status") == "design-only",
        "profile is not authoritative for production": profile.get(
            "authoritativeForProduction"
        )
        is False,
        "Policy Atlas repository is explicit": source_collection.get("repository")
        == "edithatogo/atlas-health-policy-anz",
        "Policy Atlas collection is explicit": source_collection.get("collectionId")
        == "credentialing-socp-anz-20260910",
        "Policy Atlas commit is immutable": bool(
            COMMIT_SHA_PATTERN.fullmatch(pinned_commit)
        ),
        "required sources are present": REQUIRED_SOURCE_IDS <= source_ids,
        "every source requires a current check": all(
            source.get("currentness") == "requires-current-source-check"
            for source in sources
        ),
        "source disagreement fails closed": status_rule.get("mode")
        == "fail-closed-on-source-disagreement-or-staleness",
        "current regulator verification is required": status_rule.get(
            "requiredAction"
        )
        == "current-regulator-and-register-verification",
        "source metadata cannot infer scope": status_rule.get(
            "mayInferRegistrationQualificationTitleOrScope"
        )
        is False,
        "catalogue is not locally adopted": catalogue.get("localAdoptionApproved")
        is False,
        "local model list is empty": cast(
            "list[object]", catalogue.get("locallyAdoptedModelIds", [])
        )
        == [],
        "design rules cannot govern production": automation.get(
            "rulesMayUseProfileForProduction"
        )
        is False,
        "AI cannot establish authority or scope": automation.get(
            "aiMayEstablishAuthorityOrScope"
        )
        is False,
        "human decision remains required": automation.get("humanDecisionRequired")
        is True,
    }

    failures = [name for name, passed in checks.items() if not passed]
    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    if failures:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
