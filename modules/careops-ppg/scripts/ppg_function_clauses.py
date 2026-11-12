# Copyright 2026 PPG Workbench contributors
# SPDX-License-Identifier: Apache-2.0
"""Project source-defined function clauses; offline, not a graph migration.

Definitions retain their printed labels. A binding is an explicit, separately
located occurrence beneath an actual publisher function, not a collision waiver.
The caller reviews source semantics; this module cannot authenticate documents.
"""
from copy import deepcopy

from scripts.ppg_accreditation_contract import required, validate_graph
from scripts.ppg_source_standards import digest
from scripts.ppg_standards_contract import unique


def project_function_clauses(framework, functions, definitions, bindings):
    """Return a validated graph preview without modifying any supplied record.

    This is a first projection of a complete selected function-clause source
    inventory. Existing graph requirements/kinds must never be passed as
    definitions or reclassified through this API. Multiple function occurrences
    retain the same definition identity, each with its own stable requirement key.
    """
    required(framework, 'FrameworkKey', 'EditionKey', 'status')
    for rows, key in [(functions, 'RequirementKey'),
                      (definitions, 'DefinitionKey')]:
        if not isinstance(rows, list) or not rows:
            raise ValueError('Nonempty source inventories required')
        for row in rows:
            required(row, key, 'publisherCode')
    if not isinstance(bindings, list) or not bindings:
        raise ValueError('Explicit source function occurrences required')
    parents = unique(functions, 'RequirementKey')
    defs = unique(definitions, 'DefinitionKey')
    for function in functions:
        if (function.get('kind') != 'action-group'
                or function.get('ParentRequirementKey') is not None
                or function.get('FrameworkKey') != framework['FrameworkKey']):
            raise ValueError('Root source functions in the selected framework required')
    for definition in definitions:
        if any(key in definition for key in
               ['kind', 'RequirementKey', 'ParentRequirementKey', 'FrameworkKey']):
            raise ValueError('Existing graph requirements cannot be reclassified')
        if not isinstance(definition.get('source'), dict):
            raise ValueError('Definition source required')
    seen = set()
    used_functions = set()
    used_definitions = set()
    clauses = []
    for binding in bindings:
        required(binding, 'DefinitionKey', 'FunctionKey', 'publisherCode')
        identity = (binding['DefinitionKey'], binding['FunctionKey'])
        if identity in seen:
            raise ValueError('Duplicate definition/function occurrence')
        seen.add(identity)
        if identity[0] not in defs or identity[1] not in parents:
            raise ValueError('Unknown definition or source function')
        definition, function = defs[identity[0]], parents[identity[1]]
        if binding['publisherCode'] != definition['publisherCode']:
            required(binding, 'discrepancyRationale')
        occurrence_source = binding.get('source')
        if not isinstance(occurrence_source, dict):
            raise ValueError('Located function occurrence required')
        # All locators refer to one immutable selected source, not fabricated
        # frameworks or a second edition introduced to partition collisions.
        for source in [definition['source'], function.get('source'), occurrence_source]:
            if not isinstance(source, dict):
                raise ValueError('Source object required')
            required(source, 'PublicationKey', 'EditionKey', 'CaptureKey', 'sha256', 'locator')
            if any(source[k] != definition['source'][k] for k in
                   ['PublicationKey', 'EditionKey', 'CaptureKey', 'sha256']):
                raise ValueError('Definition/function occurrence source differs')
            if source['EditionKey'] != framework['EditionKey']:
                raise ValueError('Source edition differs from selected framework')
        used_definitions.add(identity[0])
        used_functions.add(identity[1])
        clauses.append({
            'RequirementKey': 'source-clause:' + digest([framework['FrameworkKey'],
                                                       framework['EditionKey'], *identity]),
            'FrameworkKey': framework['FrameworkKey'],
            'ParentRequirementKey': identity[1],
            'kind': 'subclause',
            'publisherCode': definition['publisherCode'],
            'source': deepcopy(definition['source']),
            'sourceDefinition': deepcopy(definition),
            'sourceFunctionOccurrence': deepcopy(binding),
        })
    if used_definitions != defs.keys() or used_functions != parents.keys():
        raise ValueError('Every selected definition and function must be represented')
    graph = {'contractVersion': 1, 'frameworks': [deepcopy(framework)],
             'requirements': deepcopy(functions) + clauses,
             'contexts': [], 'scopes': [], 'evidenceVersions': [],
             'mappings': [], 'assessments': [], 'crosswalks': []}
    # Preserve the existing parent-scoped clause and edition-wide action gates.
    validate_graph(graph)
    return graph
