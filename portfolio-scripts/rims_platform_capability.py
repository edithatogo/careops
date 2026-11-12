"""RIMS optional storage capability resolver; tenant-free and fail-closed.

Core flows do not import premium connector references. Additional providers live
in independently deployed solutions and must read approved committed snapshots.
Feature flags are requests, NOT evidence of a licence, tenant policy or consent.
"""
from __future__ import annotations

SCHEMA = "careops-rims.storage-profile/1"
CORE = frozenset({"sharepoint_json", "local_json"})
EXTRAS = {
    "offline_parquet": ("converter_installation",),
    "fabric_directlake": ("fabric_capacity", "workspace_role", "data_release"),
    "xmla": ("xmla_enabled", "workspace_role"),
    "remote_nlp": ("model_endpoint", "data_release"),
    "copilot": ("copilot_entitlement", "tenant_approval", "data_release"),
}


class FeatureRefused(ValueError):
    pass


def resolve(profile, *, verify=None):
    """Return safe backend plan, never native execution authority.

    verify(name, requirements) must independently inspect actual entitlement,
    availability, tenant controls, DLP and permitted data. The caller cannot
    substitute an 'isPremium' boolean. If optional verification fails, retain
    the unchanged SharePoint JSON core rather than disabling source ingestion.
    """
    if not isinstance(profile, dict) or profile.get("schema") != SCHEMA:
        raise FeatureRefused("invalid capability profile")
    requested = profile.get("requested_backend", "sharepoint_json")
    if requested in CORE:
        return {"selected": requested, "reason": "core", "execute_authorised": False}
    if requested not in EXTRAS:
        raise FeatureRefused("unknown backend")
    if requested not in profile.get("enabled_optional", []):
        return {"selected": "sharepoint_json", "reason": "optional_disabled",
                "requested": requested, "execute_authorised": False}
    if not callable(verify) or verify(requested, EXTRAS[requested]) is not True:
        return {"selected": "sharepoint_json", "reason": "optional_not_verified",
                "requested": requested, "execute_authorised": False}
    return {"selected": requested, "reason": "approved_for_planning",
            "execute_authorised": False}


def verify_core_definition(connector_names):
    """Fail when a premium or unknown connector is declared in a core flow."""
    if not isinstance(connector_names, (list, tuple, set)):
        raise FeatureRefused("connector list required")
    allowed = {"shared_sharepointonline", "shared_onedriveforbusiness",
               "shared_excelonlinebusiness", "shared_office365"}
    unknown = sorted(set(connector_names) - allowed)
    if unknown:
        raise FeatureRefused("unqualified connector(s) in core: " + ", ".join(unknown))
    return True
