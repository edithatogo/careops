# Copyright 2026 PPG Workbench contributors
# SPDX-License-Identifier: Apache-2.0
"""Fictional source hierarchy; contains no publisher normative material."""
from copy import deepcopy
import unittest

from scripts.ppg_accreditation_contract import validate_graph
from scripts.ppg_function_clauses import project_function_clauses


def fixture():
    source = dict(PublicationKey='fictional-publication', EditionKey='fictional-edition',
                  CaptureKey='fictional-capture', sha256='a' * 64, locator='definition table')
    framework = dict(FrameworkKey='fictional-framework', EditionKey='fictional-edition',
                     status='published')
    functions = [dict(RequirementKey='function-' + n, FrameworkKey='fictional-framework',
                      kind='action-group', publisherCode=n,
                      source=dict(source, locator='function ' + n)) for n in ['1', '2']]
    definitions = [dict(DefinitionKey=k, publisherCode='X09', source=deepcopy(source),
                        title='Fictional ' + k) for k in ['alpha', 'beta']]
    bindings = [dict(DefinitionKey=k, FunctionKey='function-' + n,
                     publisherCode=label, discrepancyRationale='Fictional printed-label discrepancy',
                     source=dict(source, locator='function table ' + n))
                for k, n, label in [('alpha', '1', 'X09'), ('beta', '2', 'X10')]]
    return framework, functions, definitions, bindings


class FunctionClauseTests(unittest.TestCase):
    def test_preserves_definitions_labels_variants_and_inputs(self):
        args = fixture()
        original = deepcopy(args)
        graph = project_function_clauses(*args)
        clauses = graph['requirements'][2:]
        self.assertEqual([c['publisherCode'] for c in clauses], ['X09', 'X09'])
        self.assertEqual([c['sourceFunctionOccurrence']['publisherCode'] for c in clauses],
                         ['X09', 'X10'])
        self.assertEqual([c['sourceDefinition'] for c in clauses], args[2])
        self.assertEqual(args, original)
        self.assertEqual(graph, project_function_clauses(*args))
        self.assertEqual(len({c['RequirementKey'] for c in clauses}), 2)

    def test_multiple_real_function_occurrences_preserve_definition(self):
        framework, functions, definitions, bindings = fixture()
        definitions = definitions[:1]
        bindings[1]['DefinitionKey'] = definitions[0]['DefinitionKey']
        graph = project_function_clauses(framework, functions, definitions, bindings)
        self.assertEqual(len(graph['requirements']), 4)
        self.assertEqual(graph['requirements'][2]['sourceDefinition'],
                         graph['requirements'][3]['sourceDefinition'])

    def test_clause_identity_is_scoped_to_framework_and_edition(self):
        args = fixture()
        original = project_function_clauses(*args)
        for field in ['FrameworkKey', 'EditionKey']:
            changed = deepcopy(args)
            changed[0][field] += '-next'
            if field == 'FrameworkKey':
                for function in changed[1]:
                    function[field] = changed[0][field]
            else:
                for row in changed[1] + changed[2] + changed[3]:
                    row['source'][field] = changed[0][field]
            graph = project_function_clauses(*changed)
            self.assertTrue({r['RequirementKey'] for r in original['requirements'][2:]}
                            .isdisjoint(r['RequirementKey'] for r in graph['requirements'][2:]))

    def test_same_parent_code_collision_still_rejected(self):
        framework, functions, definitions, bindings = fixture()
        bindings[1]['FunctionKey'] = 'function-1'
        with self.assertRaisesRegex(ValueError, 'Duplicate publisher code'):
            project_function_clauses(framework, functions[:1], definitions, bindings)

    def test_action_uniqueness_not_partitioned_by_function(self):
        graph = project_function_clauses(*fixture())
        for row in graph['requirements'][2:]:
            row['kind'] = 'action'
        with self.assertRaisesRegex(ValueError, 'Duplicate publisher code'):
            validate_graph(graph)

    def test_rejects_reclassification_omission_and_binding_corruption(self):
        changes = [lambda a: a[2][0].update(kind='action'),
                   lambda a: a[2][0].update(RequirementKey='old-key'),
                   lambda a: a[3].pop(),
                   lambda a: a[3].append(deepcopy(a[3][0])),
                   lambda a: a[3][0].update(FunctionKey='unknown'),
                   lambda a: a[3][0]['source'].update(sha256='b' * 64),
                   lambda a: a[3][0]['source'].update(locator=''),
                   lambda a: a[1][0].update(kind='action'),
                   lambda a: a[3][1].pop('discrepancyRationale')]
        for change in changes:
            with self.subTest(change=change):
                args = fixture()
                change(args)
                with self.assertRaises(ValueError):
                    project_function_clauses(*args)


if __name__ == '__main__':
    unittest.main()
