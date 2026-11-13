"""Exact, independently bound practitioner identity; never resolve from a name.

Source-qualified watch bindings come from an approved credentialing owner.
This pure function does not fetch or authenticate them.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence


def _time(value: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError("missing timezone timestamp")
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid timezone timestamp") from exc
    if dt.tzinfo is None:
        raise ValueError("timezone required")
    return dt.astimezone(timezone.utc)


@dataclass(frozen=True, slots=True)
class WatchBinding:
    """Trusted effective-dated reference, never an employment assertion."""
    watch_ref: str
    regulator: str
    registration_number: str
    profession: str
    effective_from_utc: str
    effective_to_utc: str | None
    revision: str

    def __post_init__(self) -> None:
        for key in ("watch_ref", "regulator", "registration_number", "profession", "revision"):
            val = getattr(self, key)
            if not isinstance(val, str) or not val or val != val.strip():
                raise ValueError(f"invalid {key}")
        if ":" not in self.watch_ref:
            raise ValueError("watch_ref must be source qualified")
        start = _time(self.effective_from_utc)
        if self.effective_to_utc is not None and _time(self.effective_to_utc) <= start:
            raise ValueError("binding interval invalid")


@dataclass(frozen=True, slots=True)
class IdentityOutcome:
    status: str
    reason: str
    binding_revision: str | None = None


def reconcile_identity(
    observation: Mapping[str, Any], bindings: Sequence[WatchBinding], *,
    source_profession: str | None, now_utc: str,
) -> IdentityOutcome:
    """Require exact regulator, number, profession, watch and effective time.

    Never infer a practitioner from a common name, an identifier prefix,
    employment, a fifth autocomplete result, or the source's claimed match.
    """
    now = _time(now_utc)
    watch = observation.get("watchRef")
    practitioner = observation.get("practitioner")
    if not isinstance(practitioner, Mapping):
        return IdentityOutcome("unresolved", "missing_regulator_identity")
    reg = practitioner.get("regulator")
    number = practitioner.get("registrationNumber")
    if not isinstance(watch, str) or not watch or ":" not in watch:
        return IdentityOutcome("unresolved", "invalid_watch_reference")
    if not isinstance(reg, str) or not reg or not isinstance(number, str) or not number:
        return IdentityOutcome("unresolved", "missing_regulator_identity")
    if not isinstance(source_profession, str) or not source_profession:
        return IdentityOutcome("unresolved", "source_profession_not_established")
    current = [
        item for item in bindings
        if item.watch_ref == watch and _time(item.effective_from_utc) <= now
        and (item.effective_to_utc is None or now < _time(item.effective_to_utc))
    ]
    if not current:
        return IdentityOutcome("unresolved", "watch_binding_not_current")
    if len(current) != 1:
        return IdentityOutcome("ambiguous", "multiple_current_watch_bindings")
    bound = current[0]
    if (bound.regulator != reg or bound.registration_number != number
            or bound.profession != source_profession):
        return IdentityOutcome("mismatch", "regulator_number_or_profession_mismatch")
    collisions = [
        item for item in bindings
        if item.watch_ref != watch and item.regulator == reg and item.registration_number == number
        and _time(item.effective_from_utc) <= now
        and (item.effective_to_utc is None or now < _time(item.effective_to_utc))
    ]
    if collisions:
        # A legitimately multi-site clinician still needs an owner-qualified
        # linkage, rather than implicit merging of staff/engagement records.
        return IdentityOutcome("ambiguous", "registration_shared_across_watches")
    signal = observation.get("signal")
    if not isinstance(signal, Mapping) or signal.get("identityState") != "matched":
        return IdentityOutcome("unresolved", "source_identity_assertion_not_matched")
    return IdentityOutcome("matched", "exact_current_binding", bound.revision)
