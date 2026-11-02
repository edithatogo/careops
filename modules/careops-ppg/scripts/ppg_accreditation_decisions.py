"""Validate fictional external decision, condition and change-in-circumstance records."""
from datetime import date, datetime, timezone

from scripts.ppg_accreditation_contract import validate_graph
from scripts.ppg_source_standards import digest


def _date(value, field):
    if not isinstance(value, str):
        raise ValueError('Invalid date '+field)
    try:
        if len(value) == 10:
            return date.fromisoformat(value)
        if len(value) > 10 and value[10] == 'T':
            parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
            if parsed.tzinfo is None:
                raise ValueError('Timestamp must include a UTC offset')
            parsed = parsed.astimezone(timezone.utc)
            return parsed.date()
    except ValueError as exc:
        raise ValueError('Invalid date '+field) from exc
    raise ValueError('Invalid date '+field)


def _instant(value):
    """Return a UTC instant when an ISO timestamp includes a timezone."""
    if not isinstance(value, str) or len(value) <= 10 or value[10] != 'T':
        return None
    try:
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError as exc:
        raise ValueError('Invalid ISO timestamp') from exc
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def _later_than(candidate, prior, field):
    candidate_instant = _instant(candidate)
    prior_instant = _instant(prior)
    if candidate_instant is not None and prior_instant is not None:
        return candidate_instant > prior_instant
    return _date(candidate, field) > _date(prior, field)


def validate_case(package, graph, as_of):
    base = validate_graph(graph)
    today = _date(as_of, 'asOf')
    if (not isinstance(package, dict) or type(package.get('contractVersion')) is not int
            or package.get('contractVersion') != 1):
        raise ValueError('Unsupported decision contract version')
    if package.get('fixtureOnly') is not True or package.get('nativeWrites') is not False:
        raise ValueError('Decision case must be fixture-only and nonmutating')
    if package.get('submissionEnabled') is not False or package.get('notificationsEnabled') is not False:
        raise ValueError('External submission and notifications must remain disabled')
    for name in ('decisions', 'conditions', 'changes'):
        if (not isinstance(package.get(name), list)
                or any(not isinstance(row, dict) for row in package[name])):
            raise ValueError(name+' must be a list of objects')

    scopes = {row['ScopeKey'] for row in graph['scopes']}
    contexts = {row['ReviewContextKey']: row for row in graph['contexts']}
    evidence = {row['EvidenceVersionKey']: row for row in graph['evidenceVersions']}
    decisions = {}
    for row in package.get('decisions', []):
        for field in ('DecisionKey', 'IssuerRef', 'AuthorityRef', 'FrameworkKey',
                      'ReviewContextKey', 'DecisionOutcome', 'SourceEvidenceVersionKey',
                      'SourceLocator', 'IssuedAt', 'EffectiveFrom'):
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise ValueError('Missing decision field '+field)
        if row['DecisionKey'] in decisions:
            raise ValueError('Duplicate decision key')
        context = contexts.get(row['ReviewContextKey'])
        if (context is None or row['FrameworkKey'] not in context['FrameworkKeys']
                or row['SourceEvidenceVersionKey'] not in evidence):
            raise ValueError('Decision context or exact source version unresolved')
        row_scopes = row.get('ScopeKeys')
        if (not isinstance(row_scopes, list) or not row_scopes
                or any(not isinstance(scope, str) or not scope.strip()
                       or scope not in scopes or scope not in context['ScopeKeys']
                       for scope in row_scopes)):
            raise ValueError('Decision scope is invalid or outside context')
        if _date(row['IssuedAt'], 'IssuedAt') > today:
            raise ValueError('Decision issue date is in the future')
        if row.get('EffectiveTo') is not None:
            _date(row['EffectiveTo'], 'EffectiveTo')
            _date(row['EffectiveFrom'], 'EffectiveFrom')
            if _later_than(row['EffectiveFrom'], row['EffectiveTo'], 'EffectiveTo'):
                raise ValueError('Decision effective interval invalid')
        else:
            _date(row['EffectiveFrom'], 'EffectiveFrom')
        decisions[row['DecisionKey']] = row

    for row in decisions.values():
        previous_key = row.get('SupersedesDecisionKey')
        if previous_key is not None and (
                not isinstance(previous_key, str) or not previous_key.strip()):
            raise ValueError('Supersedes decision reference must be a nonblank key')
        if previous_key is not None:
            previous = decisions.get(previous_key)
            if (previous is None or previous_key == row['DecisionKey']
                    or previous['IssuerRef'] != row['IssuerRef']
                    or previous['AuthorityRef'] != row['AuthorityRef']
                    or previous['FrameworkKey'] != row['FrameworkKey']
                    or previous['ReviewContextKey'] != row['ReviewContextKey']
                    or previous.get('ScopeKeys') != row.get('ScopeKeys')
                    or not _later_than(row['IssuedAt'], previous['IssuedAt'], 'IssuedAt')):
                raise ValueError('Superseded decision identity mismatch')
        seen = {row['DecisionKey']}
        cursor = previous_key
        while cursor is not None:
            if not isinstance(cursor, str) or cursor not in decisions:
                raise ValueError('Superseded decision identity mismatch')
            if cursor in seen:
                raise ValueError('Decision supersession cycle')
            seen.add(cursor)
            cursor = decisions[cursor].get('SupersedesDecisionKey')

    conditions = {}
    for row in package.get('conditions', []):
        for field in ('ConditionKey', 'DecisionKey', 'DescriptionRef', 'DueDate',
                      'ConditionState'):
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise ValueError('Missing condition field '+field)
        if row['ConditionKey'] in conditions or row['DecisionKey'] not in decisions:
            raise ValueError('Duplicate condition or decision reference missing')
        due = _date(row['DueDate'], 'DueDate')
        if row['ConditionState'] not in {'outstanding', 'response-prepared', 'externally-cleared', 'disputed', 'unknown'}:
            raise ValueError('Unknown external condition state')
        action = row.get('InternalActionRef')
        if not isinstance(action, dict) or not all(
                isinstance(action.get(key), str) and action[key].strip()
                for key in ('SourceSystem', 'RecordType', 'RecordKey', 'RecordVersion', 'State')):
            raise ValueError('Condition needs exact internal action reference')
        if row['ConditionState'] == 'externally-cleared':
            clearance_ref = row.get('ExternalClearanceDecisionRef')
            if not isinstance(clearance_ref, str) or not clearance_ref.strip():
                raise ValueError('External condition clearance needs a source decision reference')
            clearance = decisions.get(clearance_ref)
            if clearance is None:
                raise ValueError('External condition clearance decision reference is unresolved')
            imposed = decisions[row['DecisionKey']]
            if (clearance_ref == row['DecisionKey']
                    or clearance['IssuerRef'] != imposed['IssuerRef']
                    or clearance['AuthorityRef'] != imposed['AuthorityRef']
                    or clearance['FrameworkKey'] != imposed['FrameworkKey']
                    or clearance['ReviewContextKey'] != imposed['ReviewContextKey']
                    or clearance['ScopeKeys'] != imposed['ScopeKeys']
                    or not _later_than(clearance['IssuedAt'], imposed['IssuedAt'], 'IssuedAt')):
                raise ValueError(
                    'External condition clearance must cite a later decision '
                    'from the same issuer, framework, review context and scope')
        events = row.get('responseHistory')
        if not isinstance(events, list) or not events:
            raise ValueError('Condition response history is required')
        prior = None
        response_event_keys = set()
        prior_occurred_at = None
        prior_occurred_instant = None
        for event in events:
            if not isinstance(event, dict):
                raise ValueError('Condition response event must be an object')
            for field in ('ResponseEventKey', 'State', 'OccurredAt', 'ActorRef', 'Rationale'):
                if not isinstance(event.get(field), str) or not event[field].strip():
                    raise ValueError('Missing condition response event field '+field)
            if event['ResponseEventKey'] in response_event_keys:
                raise ValueError('Duplicate condition response event key')
            response_event_keys.add(event['ResponseEventKey'])
            if event['State'] not in {'not-started', 'prepared', 'submitted', 'acknowledged', 'answered'}:
                raise ValueError('Unknown condition response state')
            if event.get('PreviousResponseEventKey') != prior:
                raise ValueError('Condition response event history chain mismatch')
            occurred_at = _date(event['OccurredAt'], 'OccurredAt')
            occurred_instant = _instant(event['OccurredAt'])
            if occurred_at > today:
                raise ValueError('Condition response event date is in the future')
            if _later_than(decisions[row['DecisionKey']]['IssuedAt'], event['OccurredAt'], 'OccurredAt'):
                raise ValueError('Condition response precedes source decision')
            if prior_occurred_at is not None:
                reversed_time = (
                    occurred_instant < prior_occurred_instant
                    if occurred_instant is not None and prior_occurred_instant is not None
                    else occurred_at < prior_occurred_at
                )
                if reversed_time:
                    message = (
                        'Condition response event times are out of order'
                        if occurred_instant is not None and prior_occurred_instant is not None
                        else 'Condition response event dates are out of order'
                    )
                    raise ValueError(message)
            if event['State'] == 'submitted':
                raise ValueError('Fictional case cannot claim an external submission')
            prior = event['ResponseEventKey']
            prior_occurred_at = occurred_at
            prior_occurred_instant = occurred_instant
        if row['ConditionState'] == 'externally-cleared' and events[-1]['State'] != 'answered':
            raise ValueError('External condition clearance requires recorded external answer')
        if (due < today and row['ConditionState'] in
                {'outstanding', 'response-prepared', 'disputed'}
                and row.get('Overdue') is not True):
            raise ValueError('Overdue external condition must remain explicit')
        conditions[row['ConditionKey']] = row

    changes = {}
    for row in package.get('changes', []):
        for field in ('ChangeKey', 'DecisionKey', 'ReviewContextKey', 'AffectedScopeKey',
                      'ChangeType', 'ProposedAt', 'ImpactState', 'NotificationDetermination',
                      'SubmissionState', 'ExternalResponseState'):
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise ValueError('Missing change field '+field)
        if row['ChangeKey'] in changes or row['DecisionKey'] not in decisions:
            raise ValueError('Duplicate change or source decision missing')
        if (row['ReviewContextKey'] not in contexts
                or row['ReviewContextKey'] != decisions[row['DecisionKey']]['ReviewContextKey']
                or row['AffectedScopeKey'] not in scopes
                or row['AffectedScopeKey'] not in contexts[row['ReviewContextKey']]['ScopeKeys']
                or row['AffectedScopeKey'] not in decisions[row['DecisionKey']]['ScopeKeys']):
            raise ValueError('Change scope or context mismatch')
        proposed_at = _date(row['ProposedAt'], 'ProposedAt')
        if proposed_at > today:
            raise ValueError('Change proposal date is in the future')
        if row.get('EffectiveAt') is not None:
            _date(row['EffectiveAt'], 'EffectiveAt')
        if row['ImpactState'] not in {'pending', 'reviewed'}:
            raise ValueError('Unknown impact review state')
        if row['NotificationDetermination'] not in {'required', 'not-required', 'unknown'}:
            raise ValueError('Unknown notification determination')
        if row['ImpactState'] == 'reviewed':
            for field in ('ImpactReviewerRef', 'ImpactDecisionRef', 'ImpactRationale', 'ImpactReviewedAt'):
                if not isinstance(row.get(field), str) or not row[field].strip():
                    raise ValueError('Reviewed impact needs human attribution and rationale')
            if _date(row['ImpactReviewedAt'], 'ImpactReviewedAt') > today:
                raise ValueError('Impact review date is in the future')
            if _later_than(row['ProposedAt'], row['ImpactReviewedAt'], 'ImpactReviewedAt'):
                raise ValueError('Impact review precedes change proposal')
        if row['SubmissionState'] not in {'not-prepared', 'prepared', 'not-submitted', 'submitted'}:
            raise ValueError('Unknown external submission state')
        if row['SubmissionState'] == 'submitted':
            raise ValueError('Fictional case cannot claim an external submission')
        if row['ExternalResponseState'] not in {'not-received', 'acknowledged', 'answered', 'unknown'}:
            raise ValueError('Unknown external response state')
        if row['ExternalResponseState'] != 'not-received':
            response_ref = row.get('ExternalResponseReference')
            if not isinstance(response_ref, str) or not response_ref.strip():
                raise ValueError('External response state needs source reference')
        changes[row['ChangeKey']] = row

    return {
        'baseGraphSha256': base['graphSha256'],
        'packageSha256': digest(package),
        'counts': {'decisions': len(decisions), 'conditions': len(conditions),
                   'changes': len(changes)},
        'submissionEnabled': False,
        'notificationsEnabled': False,
        'externalDecisionChanges': False,
        'nativeWrites': 0,
        'fixtureOnly': True,
    }
