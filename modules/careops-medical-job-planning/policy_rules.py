# Copyright (c) 2026 CareOps contributors
# SPDX-License-Identifier: Apache-2.0
"""Evidence-aware reference CST arithmetic; never an approval or industrial ruling."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN
import re


class RuleError(ValueError):
    """Invalid rule evidence or arithmetic input."""


@dataclass(frozen=True, slots=True)
class RulePack:
    rule_key: str
    edition: str
    source_ref: str
    source_sha256: str
    clause_ref: str
    effective_from: date
    effective_to: date | None
    status: str  # reference_only | adopted | withdrawn | superseded
    adoption_ref: str | None
    eligible_classifications: frozenset[str]
    fraction: Decimal

    def __post_init__(self) -> None:
        for field in ('rule_key', 'edition', 'source_ref', 'clause_ref'):
            value = getattr(self, field)
            if not isinstance(value, str) or not value.strip():
                raise RuleError(f'{field} must identify a source-qualified value')
        if not isinstance(self.source_sha256, str) or not re.fullmatch('[0-9a-f]{64}', self.source_sha256):
            raise RuleError('rule source SHA-256 required')
        if type(self.effective_from) is not date or (self.effective_to is not None and
            (type(self.effective_to) is not date or self.effective_to < self.effective_from)):
            raise RuleError('invalid rule effective interval')
        if self.status not in ('reference_only', 'adopted', 'withdrawn', 'superseded'):
            raise RuleError('unknown policy status')
        if self.status == 'adopted' and (not isinstance(self.adoption_ref, str) or not self.adoption_ref.strip()):
            raise RuleError('adopted rule requires an external adoption evidence reference')
        if (not isinstance(self.eligible_classifications, frozenset) or
            not self.eligible_classifications or any(not isinstance(k, str) or not k for k in self.eligible_classifications)):
            raise RuleError('eligible classification keys required')
        if type(self.fraction) is not Decimal or not self.fraction.is_finite() or not Decimal('0') <= self.fraction <= Decimal('1'):
            raise RuleError('fraction must be a bounded Decimal')


def _hours(value: str | int | Decimal, label: str) -> Decimal:
    if type(value) is bool or not isinstance(value, (str, int, Decimal)):
        raise RuleError(f'{label}: unsupported numeric input')
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise RuleError(f'{label}: invalid decimal') from exc
    if not result.is_finite() or result < 0:
        raise RuleError(f'{label}: negative or non-finite hours')
    return result


def _q(value: Decimal) -> str:
    return str(value.quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN))


def assess_cst(
    pack: RulePack, *, classification: str, as_of: date,
    contracted_hours: str | int | Decimal, planned_hours: str | int | Decimal,
    observed_hours: str | int | Decimal | None, verified_contract: bool,
) -> dict[str, str | bool | None]:
    """Evaluate a synthetic, effective-dated rule without certifying compliance.

    Caller-supplied status/adoption/contract flags are untrusted: native
    implementation must independently verify evidence and delegation.
    This pure function is never an approval authority.
    """
    if type(as_of) is not date or not isinstance(classification, str) or not classification:
        raise RuleError('as-of date and classification required')
    if type(verified_contract) is not bool:
        raise RuleError('verified_contract must be an explicit boolean')
    contracted = _hours(contracted_hours, 'contracted_hours')
    planned = _hours(planned_hours, 'planned_hours')
    observed = None if observed_hours is None else _hours(observed_hours, 'observed_hours')
    active = pack.effective_from <= as_of and (pack.effective_to is None or as_of <= pack.effective_to)
    eligible = classification in pack.eligible_classifications and active and verified_contract
    status = ('source_unverified' if not verified_contract else
              'candidate_eligible' if eligible else 'not_established')
    operative = eligible and pack.status == 'adopted' and bool(pack.adoption_ref)
    minimum = contracted * pack.fraction if eligible else None
    return {
        'rule_key': pack.rule_key,
        'rule_edition': pack.edition,
        'authority_status': pack.status,
        'eligibility': status,
        'rules_operative': operative,
        'approval_allowed': False,  # only separately authorised human workflow may approve
        'candidate_minimum_hours': _q(minimum) if minimum is not None else None,
        'planned_hours': _q(planned),
        'observed_hours': _q(observed) if observed is not None else None,
        'planned_shortfall_hours': _q(max(Decimal(0), minimum - planned)) if minimum is not None else None,
        'actual_access_shortfall_hours': _q(max(Decimal(0), minimum - observed)) if minimum is not None and observed is not None else None,
        'observed_data_status': 'not_observed' if observed is None else 'provided_unverified',
        'interpretation': 'candidate_rule_not_industrial_determination',
    }
