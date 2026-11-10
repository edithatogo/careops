"""Aggregate data-utilisation scorecard for existing RIMS sources only.

No raw data, identities, provider field names or tenant endpoints appear in
output. Metrics describe completeness of declared consumer *mappings*, not
verified runtime usage, until separately qualified native readback exists.
"""
from __future__ import annotations

from collections import defaultdict

class RollupError(ValueError):
    pass


def rollup(adoption_manifest, source_reports):
    if adoption_manifest.get("schema") != "careops-rims.existing-source-adoption/1":
        raise RollupError("incorrect source adoption manifest")
    if not isinstance(source_reports, list):
        raise RollupError("source reports array required")
    catalog = {}
    for source in adoption_manifest.get("sources", []):
        name = source.get("source")
        if not isinstance(name, str) or not name or name in catalog:
            raise RollupError("duplicate or missing source in catalogue")
        catalog[name] = source
    seen = set()
    domains = defaultdict(lambda: {
        "reported_sources": 0, "records_observed": 0,
        "fields_observed": 0, "mapped_to_consumer": 0,
        "retained_only": 0, "excluded_with_reason": 0,
        "unassessed": 0,
    })
    per_source = []
    for item in source_reports:
        if not isinstance(item, dict):
            raise RollupError("invalid source report")
        name = item.get("source")
        if name not in catalog or name in seen:
            raise RollupError("unknown or duplicate source report")
        seen.add(name)
        profile = item.get("profile")
        usage = item.get("utilisation")
        if (
            not isinstance(profile, dict) or not isinstance(usage, dict)
            or profile.get("schema") != "careops-rims.retained-field-profile/1"
            or usage.get("schema") != "careops-rims.retained-field-utilisation/1"
            or profile.get("source_id") != usage.get("source_id")
        ):
            raise RollupError("mismatched source coverage contracts")
        total = usage.get("source_field_count")
        counts = [usage.get(key) for key in (
            "mapped_to_consumer", "retained_only",
            "excluded_with_reason", "unassessed",
        )]
        if (
            not isinstance(total, int) or isinstance(total, bool) or total < 0
            or any(not isinstance(x, int) or isinstance(x, bool) or x < 0
                   for x in counts) or sum(counts) != total
            or total != len(profile.get("fields", []))
        ):
            raise RollupError("field-count reconciliation failed")
        observed = profile.get("records_observed")
        if not isinstance(observed, int) or isinstance(observed, bool) or observed < 0:
            raise RollupError("invalid record count")
        domain = catalog[name]["primary_domain"]
        group = domains[domain]
        group["reported_sources"] += 1
        group["records_observed"] += observed
        group["fields_observed"] += total
        for key in ("mapped_to_consumer", "retained_only", "excluded_with_reason", "unassessed"):
            group[key] += usage[key]
        per_source.append({
            "source": name,
            "domain": domain,
            "records_observed": observed,
            "source_field_count": total,
            "consumer_mapped_field_count": counts[0],
            "accounted_for_field_count": total - counts[3],
            "native_binding_verified": False,
            "historical_scope_not_current_freshness": True,
        })
    domain_rows = []
    for name, data in sorted(domains.items()):
        numerator = data["mapped_to_consumer"]
        denominator = data["fields_observed"]
        domain_rows.append({
            "domain": name, **data,
            "declared_consumer_mapping_fraction":
                None if denominator == 0 else numerator / denominator,
            "field_accounting_fraction":
                None if denominator == 0 else (denominator-data["unassessed"]) / denominator,
            "native_utilisation_verified": False,
        })
    return {
        "schema": "careops-rims.existing-source-coverage-rollup/1",
        "sources_in_catalogue": len(catalog),
        "sources_with_verified_profile_input": 0,
        "sources_with_declared_profiles": len(seen),
        "sources_still_unprofiled": sorted(set(catalog) - seen),
        "source_summaries": sorted(per_source, key=lambda x: x["source"]),
        "domain_summaries": domain_rows,
        "full_field_utilisation_proven": False,
        "native_model_parity_proven": False,
        "publication_population_additivity": "not_assumed",
        "warning": "Declared source-to-consumer mapping is not proof of actual use or fresh capture.",
    }
