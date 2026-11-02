"""Project a validated fictional decision package onto the existing native schema.

This module performs no transport and grants no issuer, submission or write authority.
"""
from copy import deepcopy
import json

from scripts.ppg_accreditation_decisions import validate_case


def _json(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def _native_date(value):
    if value is None:
        return None
    return value+'T00:00:00Z' if len(value) == 10 else value


def project_native_case(package, graph, as_of):
    """Return scalar fields and unresolved key links; never invent native IDs.

    The transport must resolve each key in its exact destination list and verify
    the source bytes/locator before applying this plan. Fictional issuer references
    are retained as source assertions, never classified as verified real authority.
    """
    validation = validate_case(package, graph, as_of)
    provenance = {'fixtureOnly': True, 'humanReviewClaimed': False,
                  'realIssuerAuthorityVerified': False,
                  'externalSubmissionEnabled': False,
                  'notificationsEnabled': False,
                  'packageSha256': validation['packageSha256']}
    decisions, events = [], []
    for row in package['decisions']:
        fields = {name: row[name] for name in (
            'DecisionKey', 'IssuerRef', 'AuthorityRef', 'FrameworkKey',
            'ReviewContextKey', 'DecisionOutcome', 'SourceEvidenceVersionKey',
            'SourceLocator')}
        fields.update(Title='SYNTHETIC decision: '+row['DecisionKey'],
                      ScopeKeysJSON=_json(row['ScopeKeys']),
                      SupersedesDecisionKey=row.get('SupersedesDecisionKey'),
                      ContractDecisionJSON=_json(row),
                      DecisionDetailsJSON=_json(provenance))
        for name in ('IssuedAt', 'EffectiveFrom', 'EffectiveTo'):
            fields[name] = _native_date(row.get(name))
        decisions.append({'key': row['DecisionKey'], 'fields': fields,
                          'lookupKeys': {'ReviewContextLink': row['ReviewContextKey'],
                                         'SourceEvidenceVersionLink': row['SourceEvidenceVersionKey']}})
    for row in package['conditions']:
        fields = {'Title': 'SYNTHETIC condition: '+row['ConditionKey'],
                  'DecisionEventKey': row['ConditionKey'],
                  'DecisionKey': row['DecisionKey'], 'EventKind': 'condition',
                  'ConditionKey': row['ConditionKey'],
                  'DescriptionRef': row['DescriptionRef'],
                  'DueDate': _native_date(row['DueDate']),
                  'EventState': row['ConditionState'],
                  'InternalActionRefJSON': _json(row['InternalActionRef']),
                  'ResponseHistoryJSON': _json(row['responseHistory']),
                  'ContractEventJSON': _json(row),
                  'EventDetailsJSON': _json(provenance)}
        events.append({'key': row['ConditionKey'], 'fields': fields,
                       'lookupKeys': {'DecisionLink': row['DecisionKey']}})
    for row in package['changes']:
        fields = {'Title': 'SYNTHETIC change: '+row['ChangeKey'],
                  'DecisionEventKey': row['ChangeKey'],
                  'DecisionKey': row['DecisionKey'], 'EventKind': 'change',
                  'ChangeKey': row['ChangeKey'], 'ChangeType': row['ChangeType'],
                  'EffectiveAt': _native_date(row.get('EffectiveAt')),
                  'EventState': row['SubmissionState'],
                  'ContractEventJSON': _json(row),
                  'EventDetailsJSON': _json(provenance)}
        events.append({'key': row['ChangeKey'], 'fields': fields,
                       'lookupKeys': {'DecisionLink': row['DecisionKey']}})
    keys = [row['key'] for row in events]
    if len(keys) != len(set(keys)):
        raise ValueError('Condition and change keys collide in native event namespace')
    return {'validation': deepcopy(validation), 'decisions': decisions,
            'events': events, 'nativeWrites': 0,
            'sourceCaptureVerified': False, 'lookupIdsResolved': False}
