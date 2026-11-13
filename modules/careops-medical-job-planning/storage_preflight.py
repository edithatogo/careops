# Copyright (c) 2026 CareOps contributors
# SPDX-License-Identifier: Apache-2.0
"""Pure, fail-closed, *read-only* structural SharePoint inventory preflight.

Never provisions objects, changes ACLs, verifies identity, licenses premium
features, sends email or turns an offline layout match into tenant acceptance.
All input is untrusted source readback until separately authenticated and attested.
"""
from __future__ import annotations


class PreflightError(ValueError):
    """Malformed logical or native-readback input."""


def _rows(value: object, key: str) -> dict[str, dict]:
    if type(value) is not list:
        raise PreflightError(f"{key} must be a list")
    result: dict[str, dict] = {}
    for item in value:
        if type(item) is not dict or type(item.get('name')) is not str or not item['name'].startswith('JP_'):
            raise PreflightError(f"{key}: invalid object name")
        name = item['name']
        if name.casefold() in {x.casefold() for x in result}:
            raise PreflightError(f"{key}: duplicate or case-colliding object")
        result[name] = item
    return result


def assess_layout(contract: dict, readback: dict) -> dict:
    """Compare structural candidates only; never return a deploy/approve instruction.

    This checker does not authenticate the supplied native readback. A structural
    match is useful evidence for an *authorised* later test, not proof of ACLs.
    """
    if type(contract) is not dict or contract.get('status') != 'source-inventory-only:not-deployed':
        raise PreflightError('source-only contract required')
    if type(contract.get('delivery')) is not dict or contract['delivery'].get('authorisation_required') is not True:
        raise PreflightError('required authorisation gate absent')
    if type(readback) is not dict or 'lists' not in readback or 'libraries' not in readback:
        raise PreflightError('complete structural readback envelope required')
    desired_lists = _rows(contract.get('lists'), 'desired lists')
    desired_libraries = _rows(contract.get('libraries'), 'desired libraries')
    existing_lists = _rows(readback.get('lists'), 'existing lists')
    existing_libraries = _rows(readback.get('libraries'), 'existing libraries')
    if set(desired_lists) & set(desired_libraries):
        raise PreflightError('same name cannot be both list and library')
    for item in existing_lists.values():
        if type(item.get('columns')) is not list or any(type(x) is not str for x in item['columns']):
            raise PreflightError('list readback requires column names')
        if type(item.get('key_unique')) is not bool:
            raise PreflightError('list readback requires explicit uniqueness evidence')
    for item in (*existing_lists.values(), *existing_libraries.values()):
        if type(item.get('permission_scopes')) is not int or item['permission_scopes'] < 0:
            raise PreflightError('permission-scope count is missing or malformed')
    findings: list[dict[str, str]] = []

    def add(name: str, code: str) -> None:
        findings.append({'object': name, 'code': code})

    for name, desired in desired_lists.items():
        actual = existing_lists.get(name)
        if actual is None:
            add(name, 'missing_list')
            continue
        fields = desired.get('required_source_fields')
        if type(fields) is not list or not all(isinstance(x, str) and x for x in fields):
            raise PreflightError('desired list fields missing')
        if not set(fields).issubset(set(actual['columns'])):
            add(name, 'required_columns_missing')
        if actual['key_unique'] is not True:
            add(name, 'unique_key_unverified')
        if actual['permission_scopes'] >= 5000:
            add(name, 'permission_scope_growth_risk')
    for name in desired_libraries:
        actual = existing_libraries.get(name)
        if actual is None:
            add(name, 'missing_library')
            continue
        if actual['permission_scopes'] >= 5000:
            add(name, 'permission_scope_growth_risk')
    for name in set(existing_lists) - set(desired_lists):
        add(name, 'unmanaged_existing_list')
    for name in set(existing_libraries) - set(desired_libraries):
        add(name, 'unmanaged_existing_library')
    return {
        'readiness': 'blocked' if findings else 'structural_match_only',
        'findings': sorted(findings, key=lambda x: (x['object'], x['code'])),
        'permission_qualified': False,
        'native_source_authenticity_qualified': False,
        'provisioning_authorised': False,
        'write_operations': [],
    }
