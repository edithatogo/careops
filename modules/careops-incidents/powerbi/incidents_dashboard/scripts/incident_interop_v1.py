"""Fictional, provider-neutral incident count contract.

This module accepts already selected event records and emits only period/cohort
counts. It has no storage, Power BI, network, or operational-record dependency.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from datetime import date
from typing import Iterable, Mapping

SCHEMA_VERSION = "careops.incidents.count-packet.v1"
_HEX_256 = re.compile(r"^[0-9a-f]{64}$")


class ContractError(ValueError):
    """Input cannot be safely represented by this source contract."""


def prepare_count_packet(
    records: Iterable[Mapping[str, str]] | None,
    *,
    source_id: str,
    source_revision: str,
    source_sha256: str,
    source_as_of: date,
    period_start: date,
    period_end: date,
    as_of: date,
    maximum_age_days: int,
    minimum_cell_size: int,
) -> dict[str, object]:
    """Validate source metadata and return deterministic privacy-marked counts.

    ``records=None`` models an absent optional provider. A supplied source must
    be fresh and carry a version and content digest. If any cohort cell in a
    month falls below the explicitly supplied threshold, every count and
    denominator for that month is withheld to avoid direct complementary
    disclosure within the packet. This is a source-level guard, not a complete
    disclosure-control assessment for a released dataset.
    """
    if records is None:
        raise ContractError("optional incident provider is unavailable")
    if not source_id.strip() or not source_revision.strip():
        raise ContractError("source identity and revision are required")
    if not _HEX_256.fullmatch(source_sha256):
        raise ContractError("source digest must be a lowercase SHA-256 value")
    if maximum_age_days < 0 or minimum_cell_size < 1:
        raise ContractError("freshness must be nonnegative and suppression threshold positive")
    if period_start > period_end or source_as_of > as_of:
        raise ContractError("source and period dates are inconsistent")
    age_days = (as_of - source_as_of).days
    if age_days > maximum_age_days:
        raise ContractError("source snapshot is stale")

    materialized = list(records)
    if not materialized:
        raise ContractError("source snapshot contains no events")
    seen: set[str] = set()
    cohort_counts: Counter[tuple[str, str]] = Counter()
    monthly_totals: Counter[str] = Counter()
    for record in materialized:
        if set(record) != {"event_id", "event_date", "cohort"}:
            raise ContractError("records must contain only event_id, event_date, and cohort")
        event_id = record["event_id"].strip()
        cohort = record["cohort"].strip()
        if not event_id or not cohort:
            raise ContractError("event identity and cohort are required")
        if event_id in seen:
            raise ContractError("duplicate event identity")
        seen.add(event_id)
        try:
            event_date = date.fromisoformat(record["event_date"])
        except (TypeError, ValueError) as error:
            raise ContractError("event date must use ISO YYYY-MM-DD") from error
        if not period_start <= event_date <= period_end:
            raise ContractError("event is outside the selected period")
        month = event_date.strftime("%Y-%m")
        cohort_counts[(month, cohort)] += 1
        monthly_totals[month] += 1

    canonical_source = json.dumps(materialized, sort_keys=True, separators=(",", ":"))
    observed_digest = hashlib.sha256(canonical_source.encode("utf-8")).hexdigest()
    if observed_digest != source_sha256:
        raise ContractError("source digest does not match the supplied records")

    months = sorted(monthly_totals)
    suppressed_months = {
        month
        for month, _cohort in cohort_counts
        if any(
            count < minimum_cell_size
            for (candidate_month, _), count in cohort_counts.items()
            if candidate_month == month
        )
    }
    rows: list[dict[str, object]] = []
    for month in months:
        for (candidate_month, cohort), count in sorted(cohort_counts.items()):
            if candidate_month != month:
                continue
            suppressed = month in suppressed_months
            rows.append(
                {
                    "month": month,
                    "cohort": cohort,
                    "count": None if suppressed else count,
                    "denominator": None if suppressed else monthly_totals[month],
                    "status": "suppressed" if suppressed else "available",
                }
            )

    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "source": {
            "id": source_id,
            "revision": source_revision,
            "sha256": source_sha256,
            "asOf": source_as_of.isoformat(),
        },
        "period": {"start": period_start.isoformat(), "end": period_end.isoformat()},
        "asOf": as_of.isoformat(),
        "maximumAgeDays": maximum_age_days,
        "minimumCellSize": minimum_cell_size,
        "rows": rows,
        "generatedFindings": False,
        "operationalData": False,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload["packetSha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return payload


def validate_count_packet(packet: Mapping[str, object]) -> None:
    """Fail closed on missing or unsupported packet versions and malformed rows."""
    if packet.get("schemaVersion") != SCHEMA_VERSION:
        raise ContractError("unsupported incident count packet version")
    supplied_digest = packet.get("packetSha256")
    canonical_packet = dict(packet)
    canonical_packet.pop("packetSha256", None)
    canonical = json.dumps(canonical_packet, sort_keys=True, separators=(",", ":"))
    observed_digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    if supplied_digest != observed_digest:
        raise ContractError("count packet digest does not match packet contents")
    source = packet.get("source")
    if not isinstance(source, Mapping) or not source.get("id") or not source.get("revision") or not _HEX_256.fullmatch(str(source.get("sha256", ""))):
        raise ContractError("count packet source provenance is malformed")
    minimum_cell_size = packet.get("minimumCellSize")
    if type(minimum_cell_size) is not int or minimum_cell_size < 1:
        raise ContractError("count packet minimum cell size must be a positive integer")
    rows = packet.get("rows")
    if not isinstance(rows, list):
        raise ContractError("count packet rows must be a list")
    keys: set[tuple[str, str]] = set()
    monthly_rows: dict[str, list[Mapping[str, object]]] = {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"month", "cohort", "count", "denominator", "status"} or row.get("status") not in {"available", "suppressed"}:
            raise ContractError("invalid count packet row")
        if not isinstance(row.get("month"), str) or not isinstance(row.get("cohort"), str) or not row["cohort"]:
            raise ContractError("count packet period and cohort are required")
        key = (row["month"], row["cohort"])
        if key in keys:
            raise ContractError("duplicate count packet row")
        keys.add(key)
        monthly_rows.setdefault(row["month"], []).append(row)
        if row["status"] == "suppressed" and (row.get("count") is not None or row.get("denominator") is not None):
            raise ContractError("suppressed rows must not expose a count or denominator")
        if row["status"] == "available":
            count, denominator = row.get("count"), row.get("denominator")
            if type(count) is not int or type(denominator) is not int or count < minimum_cell_size or denominator < count:
                raise ContractError("available rows require valid integer counts and denominators")
    for same_month in monthly_rows.values():
        statuses = {row["status"] for row in same_month}
        if len(statuses) != 1:
            raise ContractError("suppression must cover every cohort and denominator in a month")
        if statuses == {"available"} and len({row["denominator"] for row in same_month}) != 1:
            raise ContractError("monthly cohort rows must share one denominator")
