"""Privacy-minimised priority queue for unused fields in existing RIMS sources.

Input is the existing 17-source adoption catalogue and field-profile reports.
No raw values, provider calls, inferred approvals or native-report claims.
"""
from __future__ import annotations


class OpportunityError(ValueError):
    pass


def _count(value):
    return type(value) is int and value >= 0


def plan(catalogue, source_reports):
    if (not isinstance(catalogue, dict) or
            catalogue.get("schema") != "careops-rims.existing-source-adoption/1" or
            not isinstance(source_reports, list)):
        raise OpportunityError("invalid catalogue or source reports")
    sources = {}
    for row in catalogue.get("sources", []):
        if (not isinstance(row, dict) or not isinstance(row.get("source"), str)
                or not row["source"] or row["source"] in sources):
            raise OpportunityError("invalid or duplicate source")
        sources[row["source"]] = row
    if not sources:
        raise OpportunityError("empty catalogue")
    seen, opportunities, observed_total, mapped_total = set(), [], 0, 0
    for report in source_reports:
        if not isinstance(report, dict):
            raise OpportunityError("invalid source report")
        name = report.get("source")
        if name not in sources or name in seen:
            raise OpportunityError("unknown or repeated source")
        seen.add(name)
        profile, usage = report.get("profile"), report.get("utilisation")
        if not isinstance(profile, dict) or not isinstance(usage, dict):
            raise OpportunityError("invalid profile")
        if (profile.get("schema") != "careops-rims.retained-field-profile/1"
                or usage.get("schema") != "careops-rims.retained-field-utilisation/1"
                or profile.get("source_id") != name or usage.get("source_id") != name):
            raise OpportunityError("source evidence identity mismatch")
        total_records, fields = profile.get("records_observed"), profile.get("fields")
        if not _count(total_records) or not isinstance(fields, list):
            raise OpportunityError("invalid source record inventory")
        by_path = {}
        for field in fields:
            if not isinstance(field, dict):
                raise OpportunityError("invalid field")
            path = field.get("path")
            if not isinstance(path, str) or not path.startswith("/") or path in by_path:
                raise OpportunityError("duplicate/invalid source path")
            if (not _count(field.get("records_present")) or
                    field["records_present"] > total_records or
                    not _count(field.get("nonempty_occurrences"))):
                raise OpportunityError("invalid field counts")
            by_path[path] = field
        unassessed = usage.get("unassessed_paths")
        if (not isinstance(unassessed, list) or
                any(not isinstance(p, str) for p in unassessed) or
                len(set(unassessed)) != len(unassessed) or
                not set(unassessed).issubset(by_path)):
            raise OpportunityError("invalid unassessed paths")
        keys = ("mapped_to_consumer", "retained_only", "excluded_with_reason", "unassessed")
        counts = [usage.get(k) for k in keys]
        if (any(not _count(v) for v in counts) or
                usage.get("source_field_count") != len(by_path) or
                sum(counts) != len(by_path) or counts[-1] != len(unassessed)):
            raise OpportunityError("unreconciled field counts")
        observed_total += len(by_path)
        mapped_total += counts[0]
        domain = sources[name].get("primary_domain")
        if not isinstance(domain, str) or not domain:
            raise OpportunityError("unknown domain")
        for path in sorted(unassessed):
            field = by_path[path]
            populated = field["nonempty_occurrences"] > 0
            opportunities.append({
                "source": name, "domain": domain, "source_path": path,
                "records_present": field["records_present"],
                "records_total": total_records,
                "nonempty_occurrences": field["nonempty_occurrences"],
                "types": sorted(field.get("types", [])),
                "priority": "P0" if populated else "P1",
                "next_step": (
                    "qualify rights, type and best existing consumer"
                    if populated else "investigate unavailable/empty source field"
                ),
                "verification": "source_mapping_pending",
                "native_verified": False,
            })
    opportunities.sort(key=lambda x: (
        x["priority"] != "P0", -x["records_present"], x["source"], x["source_path"]
    ))
    for index, row in enumerate(opportunities, 1):
        row["task_id"] = f"MX-UTIL-{index:04d}"
    return {
        "schema": "careops-rims.unused-data-opportunities/1",
        "source_count": len(sources), "profiled_sources": len(seen),
        "unprofiled_sources": sorted(set(sources) - seen),
        "observed_field_paths": observed_total,
        "declared_mapped_paths": mapped_total,
        "unresolved_field_paths": len(opportunities),
        "analytical_utilisation_fraction": None,
        "declared_mapping_fraction": (
            mapped_total / observed_total if observed_total else None
        ),
        "opportunities": opportunities,
        "all_source_data_utilised": False,
        "native_usage_verified": False,
        "privacy": "field_metadata_may_be_sensitive",
        "limitation": (
            "Declared mappings are not verified native consumption; "
            "observed fields do not establish full provider-schema capture."
        ),
    }
