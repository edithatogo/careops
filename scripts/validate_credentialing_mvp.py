from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import cast

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "portfolio" / "credentialing-mvp-compatibility.json"
CONTRACT_MATRIX = ROOT / "portfolio" / "credentialing-contract-matrix.json"
AUTHORITY_PROFILE = ROOT / "portfolio" / "credentialing-authority-profile.example.json"
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "credentialing-mvp"
FIXTURE = FIXTURE_ROOT / "routine-renewal-synthetic.json"
INVALID_AUTHORITY_PROFILE = FIXTURE_ROOT / "invalid-production-authority-profile.json"
COMMIT_SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")

REQUIRED_MODULES = {
    "careops-approve",
    "careops-decisions",
    "careops-process",
    "careops-legacy-migration",
}
REQUIRED_MERGED_MODULES = REQUIRED_MODULES | {
    "careops-incidents",
    "careops-finance",
}
REQUIRED_HUMAN_STAGES = {
    "source-reconciliation",
    "credentialing-officer-review",
    "committee-recommendation-or-approved-equivalent",
    "delegated-decision",
    "register-and-release-control",
}
PROHIBITED_PRODUCTION_EFFECTS = {
    "production-register-write",
    "roster-or-release-to-practise-write",
    "autonomous-ai-decision",
}
REQUIRED_INTERFACES = {
    (
        "careops-legacy-migration",
        "careops-approve",
        "careops-existing-system-source-record-0.1.0",
    ),
    (
        "careops-approve",
        "careops-decisions",
        "careops-approve-credentialing-governance-packet-0.1.0",
    ),
    (
        "careops-decisions",
        "careops-approve",
        "careops-decisions-credentialing-result-0.1.0",
    ),
    (
        "careops-approve",
        "careops-process",
        "careops-process-credentialing-events-0.1.0",
    ),
    (
        "careops-decisions",
        "careops-process",
        "careops-process-credentialing-events-0.1.0",
    ),
}
REQUIRED_AUTHORITY_SOURCES = {
    "acsqhc-credentialing-guidance-2026",
    "qld-health-hsd-034",
    "schn-model-scopes-medical-surgical",
    "schn-model-scopes-paediatric",
    "schn-model-scopes-dental",
    "amc-rural-generalist-recognition",
}
REQUIRED_AUTHORITY_GATES = {
    "current-source-verification",
    "source-rights-and-reuse-review",
    "source-to-local-crosswalk",
    "relevant-peer-validation",
    "facility-and-service-capability-validation",
    "approved-local-policy-and-delegations",
    "named-human-approval",
}


def load_object(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        msg = f"Expected JSON object: {path}"
        raise TypeError(msg)
    return cast("dict[str, object]", value)


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate_manifest(manifest: dict[str, object], errors: list[str]) -> None:
    modules = cast("dict[str, dict[str, object]]", manifest.get("modules", {}))
    mvp = cast("dict[str, object]", manifest.get("mvp", {}))
    source = cast("dict[str, object]", manifest.get("sourceIntegration", {}))
    atlas = cast("dict[str, object]", manifest.get("policyAtlas", {}))
    status = cast("dict[str, object]", manifest.get("statusClaimBoundary", {}))
    human_stages = set(cast("list[str]", mvp.get("humanStages", [])))
    excluded = set(cast("list[str]", mvp.get("excluded", [])))

    require(manifest.get("schemaVersion") == 2, "Manifest schema must be version 2", errors)
    require(
        manifest.get("status") == "merged-source-contracts-disabled-by-default",
        "Manifest status must describe merged but disabled source contracts",
        errors,
    )
    require(
        manifest.get("defaultDeploymentState") == "disabled",
        "Default deployment must be disabled",
        errors,
    )
    require(
        manifest.get("productionWritesEnabled") is False,
        "Production writes must be disabled",
        errors,
    )
    require(
        manifest.get("authoritativeRegisterIntegrationEnabled") is False,
        "Authoritative register integration must be disabled",
        errors,
    )
    require(
        manifest.get("humanDecisionRequired") is True,
        "Human decision must be required",
        errors,
    )
    require(REQUIRED_MODULES <= set(modules), "Required CareOps modules are missing", errors)
    for module_name in REQUIRED_MERGED_MODULES:
        module = modules.get(module_name, {})
        require(
            module.get("mergeState") == "merged",
            f"{module_name} must be recorded as merged",
            errors,
        )
        require(
            bool(COMMIT_SHA_PATTERN.fullmatch(cast("str", module.get("commit", "")))),
            f"{module_name} must have an immutable commit pin",
            errors,
        )
    costing = modules.get("careops-costing", {})
    require(
        costing.get("mergeState") in {"draft", "merged"},
        "CareOps Costing must have an explicit draft or merged state",
        errors,
    )
    require(
        bool(COMMIT_SHA_PATTERN.fullmatch(cast("str", costing.get("commit", "")))),
        "CareOps Costing must have an immutable commit reference",
        errors,
    )
    require(
        atlas.get("repository") == "edithatogo/atlas-health-policy-anz",
        "Policy Atlas repository must be explicit",
        errors,
    )
    require(
        atlas.get("collectionId") == "credentialing-socp-anz-20260910",
        "Policy Atlas collection must be explicit",
        errors,
    )
    require(
        bool(COMMIT_SHA_PATTERN.fullmatch(cast("str", atlas.get("commit", "")))),
        "Policy Atlas must have an immutable commit pin",
        errors,
    )
    require(
        atlas.get("authoritativeForProduction") is False,
        "Policy Atlas metadata must not govern production",
        errors,
    )
    require(
        source.get("strategy") == "api-first-with-controlled-html-fallback",
        "Source strategy must remain API-first",
        errors,
    )
    require(
        source.get("authority") == "read-only-observation",
        "Imported source authority must be read-only observation",
        errors,
    )
    require(
        source.get("reconciliationRequired") is True,
        "Source reconciliation must be required",
        errors,
    )
    require(source.get("rawPayloadInGit") is False, "Raw payloads must not enter Git", errors)
    require(
        REQUIRED_HUMAN_STAGES <= human_stages,
        "Required human stages are missing",
        errors,
    )
    require(
        PROHIBITED_PRODUCTION_EFFECTS <= excluded,
        "MVP exclusions are incomplete",
        errors,
    )
    require(
        status.get("repositoryContractSetMerged") is True,
        "Merged source-contract status must be explicit",
        errors,
    )
    for claim in (
        "tenantDeployed",
        "silentPilotPassed",
        "operatingEffective",
        "approvedToScale",
    ):
        require(status.get(claim) is False, f"{claim} must not be pre-claimed", errors)


def validate_contract_matrix(matrix: dict[str, object], errors: list[str]) -> None:
    interfaces = cast("list[dict[str, object]]", matrix.get("interfaces", []))
    interface_ids = [cast("str", item.get("interfaceId")) for item in interfaces]
    observed = {
        (
            cast("str", item.get("provider")),
            cast("str", item.get("consumer")),
            cast("str", item.get("contract")),
        )
        for item in interfaces
    }

    require(matrix.get("defaultState") == "disabled", "Contract matrix must be disabled", errors)
    require(len(interface_ids) == len(set(interface_ids)), "Interface IDs must be unique", errors)
    require(REQUIRED_INTERFACES <= observed, "Required module interfaces are missing", errors)
    require(
        all(item.get("productionWrite") is False for item in interfaces),
        "MVP interfaces must not perform production writes",
        errors,
    )
    require(
        all(cast("str", item.get("contract")).endswith("-0.1.0") for item in interfaces),
        "Every interface contract must be explicitly versioned",
        errors,
    )
    prohibited = set(cast("list[str]", matrix.get("prohibitedInterfacesForMvp", [])))
    require(
        {
            "authoritative-register-write",
            "release-to-practise-write",
            "autonomous-ai-decision",
        }
        <= prohibited,
        "Prohibited MVP interfaces are incomplete",
        errors,
    )


def validate_authority_profile(profile: dict[str, object], errors: list[str]) -> None:
    source_collection = cast("dict[str, object]", profile.get("sourceCollection", {}))
    sources = cast("list[dict[str, object]]", profile.get("sources", []))
    catalogue = cast("dict[str, object]", profile.get("modelCatalogue", {}))
    automation = cast("dict[str, object]", profile.get("automationBoundary", {}))
    gates = set(cast("list[str]", profile.get("deploymentGates", [])))
    source_ids = {cast("str", source.get("sourceId")) for source in sources}

    require(profile.get("status") == "design-only", "Authority profile must remain design-only", errors)
    require(
        profile.get("authoritativeForProduction") is False,
        "Authority profile must not govern production",
        errors,
    )
    require(
        source_collection.get("repository") == "edithatogo/atlas-health-policy-anz",
        "Authority profile must identify the Policy Atlas source collection",
        errors,
    )
    require(
        bool(
            COMMIT_SHA_PATTERN.fullmatch(
                cast("str", source_collection.get("releaseOrCommit", ""))
            )
        ),
        "Authority profile must pin an immutable Policy Atlas commit",
        errors,
    )
    require(REQUIRED_AUTHORITY_SOURCES <= source_ids, "Authority profile is missing required sources", errors)
    require(
        all(source.get("currentness") == "requires-current-source-check" for source in sources),
        "Every design source must require a current-source check",
        errors,
    )
    require(
        catalogue.get("entries") == 88
        and catalogue.get("finalEntries") == 83
        and catalogue.get("underReviewEntries") == 5,
        "Model catalogue counts are inconsistent",
        errors,
    )
    require(
        catalogue.get("localAdoptionApproved") is False,
        "No model may be pre-approved for local adoption",
        errors,
    )
    require(
        cast("list[object]", catalogue.get("locallyAdoptedModelIds", [])) == [],
        "No external model may be locally adopted in the design example",
        errors,
    )
    require(REQUIRED_AUTHORITY_GATES <= gates, "Authority profile deployment gates are incomplete", errors)
    require(
        automation.get("rulesMayUseProfileForProduction") is False,
        "Rules must not use the design profile in production",
        errors,
    )
    require(
        automation.get("aiMayEstablishAuthorityOrScope") is False,
        "AI must not establish authority or scope",
        errors,
    )
    require(
        automation.get("humanDecisionRequired") is True,
        "A human decision must remain required",
        errors,
    )


def validate_invalid_authority_fixture(errors: list[str]) -> None:
    fixture_errors: list[str] = []
    validate_authority_profile(load_object(INVALID_AUTHORITY_PROFILE), fixture_errors)
    expected_failures = {
        "Authority profile must remain design-only",
        "Authority profile must not govern production",
        "Authority profile must pin an immutable Policy Atlas commit",
        "No external model may be locally adopted in the design example",
        "Authority profile deployment gates are incomplete",
        "Rules must not use the design profile in production",
        "AI must not establish authority or scope",
        "A human decision must remain required",
    }
    require(
        expected_failures <= set(fixture_errors),
        "Invalid authority fixture did not fail closed as expected",
        errors,
    )


def validate_fixture(fixture: dict[str, object], errors: list[str]) -> None:
    source = cast("dict[str, object]", fixture.get("source", {}))
    expected_stages = set(cast("list[str]", fixture.get("expectedStages", [])))

    require(
        fixture.get("classification") == "synthetic-non-production",
        "Fixture must be synthetic",
        errors,
    )
    require(
        source.get("reconciliationStatus") == "pending-human-review",
        "Imported record must await human reconciliation",
        errors,
    )
    require(
        REQUIRED_HUMAN_STAGES <= expected_stages,
        "Synthetic fixture omits a human stage",
        errors,
    )
    require(
        fixture.get("expectedOutcome") == "human-review-required",
        "Fixture must require human review",
        errors,
    )
    require(
        fixture.get("authoritativeWriteExpected") is False,
        "Fixture must not expect an authoritative write",
        errors,
    )
    require(
        fixture.get("releaseToPractiseExpected") is False,
        "Fixture must not expect release to practise",
        errors,
    )
    require(
        fixture.get("aiDecisionExpected") is False,
        "Fixture must not expect an AI decision",
        errors,
    )
    require(
        fixture.get("prohibitedDataPresent") is False,
        "Fixture must not contain prohibited data",
        errors,
    )


def main() -> int:
    errors: list[str] = []
    validate_manifest(load_object(MANIFEST), errors)
    validate_contract_matrix(load_object(CONTRACT_MATRIX), errors)
    validate_authority_profile(load_object(AUTHORITY_PROFILE), errors)
    validate_invalid_authority_fixture(errors)
    validate_fixture(load_object(FIXTURE), errors)
    if errors:
        for error in errors:
            print(f"[FAIL] {error}")
        return 1
    print("Credentialing MVP contract validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
