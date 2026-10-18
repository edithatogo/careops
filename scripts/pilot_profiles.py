"""Choose a permission-compatible pilot; never grant access or production authority.

Observations are supplied by a person checking permitted Microsoft 365 surfaces.
They are planning evidence, not authentication, consent or a licence assertion.
"""
from dataclasses import dataclass, fields
from enum import StrEnum


class Mode(StrEnum):
    LISTS_REHEARSAL = "m365-lists-rehearsal"
    FLOW_REHEARSAL = "m365-built-in-flow-rehearsal"
    STANDARD_FLOW_PILOT = "m365-standard-flow-pilot"
    DATAVERSE_TARGET = "full-dataverse-target"


class Readiness(StrEnum):
    BLOCKED = "blocked"
    UNVERIFIED = "unverified"
    SYNTHETIC_READY = "ready-for-synthetic-pilot"
    DEPLOYMENT_REVIEW = "ready-for-deployment-review"


@dataclass(frozen=True)
class Observations:
    work_account: bool | None = None
    lists_permitted: bool | None = None
    site_list_creation: bool | None = None
    site_membership_reviewed: bool | None = None
    flow_maker: bool | None = None
    flow_policy_reviewed: bool | None = None
    standard_sharepoint_connector: bool | None = None
    connector_policy_reviewed: bool | None = None
    native_environment_approved: bool | None = None
    dataverse_entitlement_confirmed: bool | None = None
    native_security_tests_passed: bool | None = None
    recovery_drill_passed: bool | None = None
    signed_authority_verified: bool | None = None
    operational_acceptance: bool | None = None

    def __post_init__(self) -> None:
        for field in fields(self):
            value = getattr(self, field.name)
            if value is not None and type(value) is not bool:
                raise ValueError("Observations must be literal booleans or unknown")


COMMON = ("work_account", "lists_permitted", "site_list_creation", "site_membership_reviewed")
REQUIREMENTS: dict[Mode, tuple[str, ...]] = {
    Mode.LISTS_REHEARSAL: COMMON,
    Mode.FLOW_REHEARSAL: ("work_account", "flow_maker", "flow_policy_reviewed"),
    Mode.STANDARD_FLOW_PILOT: (
        *COMMON, "flow_maker", "flow_policy_reviewed", "standard_sharepoint_connector",
        "connector_policy_reviewed",
    ),
    Mode.DATAVERSE_TARGET: (
        "work_account", "native_environment_approved", "dataverse_entitlement_confirmed",
        "native_security_tests_passed", "recovery_drill_passed", "signed_authority_verified",
        "operational_acceptance",
    ),
}


@dataclass(frozen=True)
class Assessment:
    mode: Mode
    readiness: Readiness
    denied: tuple[str, ...]
    unknown: tuple[str, ...]
    fallback: Mode | None
    data_boundary: str
    authoritative_writes: bool = False
    external_communications: bool = False
    requires_new_entra_application: bool = False
    requires_tenant_administrator: bool = False


def assess(mode: Mode, observations: Observations) -> Assessment:
    """Report unmet requirements, with a permission-compatible synthetic fallback.

    A fallback is offered only when ALL its required observations are true.
    Missing permissions never cause a privileged workaround or automatic consent.
    Production acceptance needs a separate release; this function cannot enable it.
    """
    if not isinstance(mode, Mode) or not isinstance(observations, Observations):
        raise ValueError("A supported mode and observations are required")
    required = REQUIREMENTS[mode]
    denied = tuple(key for key in required if getattr(observations, key) is False)
    unknown = tuple(key for key in required if getattr(observations, key) is None)
    fallback = None
    if denied or unknown:
        readiness = Readiness.BLOCKED if denied else Readiness.UNVERIFIED
        for candidate in (Mode.LISTS_REHEARSAL, Mode.FLOW_REHEARSAL):
            if candidate != mode and all(
                getattr(observations, key) is True for key in REQUIREMENTS[candidate]
            ):
                fallback = candidate
                break
    elif mode == Mode.DATAVERSE_TARGET:
        readiness = Readiness.DEPLOYMENT_REVIEW
    else:
        readiness = Readiness.SYNTHETIC_READY
    return Assessment(
        mode, readiness, denied, unknown, fallback,
        "synthetic-only" if mode != Mode.DATAVERSE_TARGET else "separate-production-release-required",
    )
