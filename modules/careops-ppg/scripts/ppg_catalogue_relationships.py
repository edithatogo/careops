"""Account for catalogue relationship evidence without inferring policy authority.

Offline developer tooling. Literal retrieval leads are never completed assessments.
No client/authentication, source mutation or native write is performed here.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from collections import Counter
from pathlib import Path


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def relationship_key(from_uid, from_version, to_uid, to_version, relationship_type):
    """Return a stable identity for one exact, versioned relationship tuple."""
    values = (from_uid, from_version, to_uid, to_version, relationship_type)
    if any(not isinstance(value, str) or not value.strip() for value in values):
        raise ValueError('Relationship identity requires exact endpoint and type strings')
    if from_uid == to_uid:
        raise ValueError('Self relationship')
    if relationship_type not in {
            'implements', 'governed_by', 'local_variation_of', 'supplements',
            'references', 'supersedes', 'proposed_consolidation_with', 'depends_on'}:
        raise ValueError('Unknown relationship type')
    return digest([from_uid, from_version, to_uid, to_version, relationship_type])


def unique(rows, key):
    result = {}
    for row in rows:
        value = row.get(key)
        if not isinstance(value, (str, int)) or not str(value).strip() or value in result:
            raise ValueError('Missing or duplicate ' + key)
        result[value] = row
    return result


def tokens(value):
    return [(m.group().casefold(), m.start(), m.end()) for m in re.finditer(r'\w+', value)]


def literal_leads(catalogue, source):
    """Search every catalogue ID/title, preserving exact raw-text offsets.

    Shared aliases produce unresolved target sets. No top-N cutoff or semantic
    inference; callers must examine operative text and both dependency endpoints.
    """
    unique(catalogue, 'DocumentUID')
    text = source['text']
    if hashlib.sha256(text.encode()).hexdigest() != source['textSHA256']:
        raise ValueError('Text hash mismatch')
    trie = {}
    for row in catalogue:
        for kind, field in [('identifier', 'sourceDocumentId'), ('title', 'sourceTitle')]:
            words = [t[0] for t in tokens(row.get(field) or '')]
            # Very short/generic aliases remain explicit exclusions, never no-findings.
            if len(words) < (2 if kind == 'identifier' else 3):
                continue
            node = trie
            for word in words:
                node = node.setdefault(word, {})
            node.setdefault(None, []).append((row['DocumentUID'], kind))
    words = tokens(text)
    leads, seen = [], set()
    for start in range(len(words)):
        node = trie
        for end in range(start, len(words)):
            node = node.get(words[end][0])
            if node is None:
                break
            hits = [(uid, kind) for uid, kind in node.get(None, []) if uid != source['documentUID']]
            if not hits:
                continue
            begin, finish = words[start][1], words[end][2]
            targets = sorted({uid for uid, _ in hits})
            key = (begin, finish, tuple(targets))
            if key in seen:
                continue
            seen.add(key)
            page = text[:begin].count('\f') + 1
            leads.append(dict(sourceDocumentUID=source['documentUID'],
                sourceSHA256=source['originalSHA256'], textSHA256=source['textSHA256'],
                sourceVersion=source['sourceVersion'], locator=f'page:{page};chars:{begin}-{finish}',
                start=begin, end=finish, quote=text[begin:finish],
                context=text[max(0, begin-180):min(len(text), finish+220)],
                targetCandidates=targets, matchKinds=sorted({kind for _, kind in hits}),
                state='retrieval_lead', reviewState='Unreviewed', establishesDependency=False))
    return leads


def coverage(catalogue, source_rows, captures, sources, relationships, observed_at,
             membership_bindings=(), capture_bindings=()):
    """Freeze all stored identities plus active-source membership/gaps separately."""
    by_uid, by_id = unique(catalogue, 'DocumentUID'), unique(catalogue, 'Id')
    unique(source_rows, 'document_id')
    # Explicit evidence-backed aliases preserve the native persistent identity and
    # old source assertion; they never rewrite the catalogue/source register.
    from scripts.ppg_relationship_evidence_gaps import validate_membership_binding, validate_capture_binding
    aliases = unique(membership_bindings, 'sourceDocumentId')
    source_index = {r['document_id']: r for r in source_rows}
    for key, binding in aliases.items():
        if key not in source_index:
            raise ValueError('Membership binding outside source snapshot')
        validate_membership_binding(binding, source_index[key], catalogue)
    members, unresolved = {}, []
    for row in source_rows:
        item_id = row.get('catalogue_item_id')
        binding = aliases.get(row['document_id'])
        if binding:
            if item_id is not None and item_id != binding['catalogueItemId']:
                raise ValueError('Membership binding changes an existing assignment')
            item_id = binding['catalogueItemId']
        if item_id is None:
            unresolved.append({'sourceDocumentId': row['document_id'], 'reason': 'unbound_source_identity'})
            continue
        if item_id not in by_id or item_id in members:
            raise ValueError('Source membership absent or duplicated')
        actual = by_id[item_id]
        if (actual['sourceDocumentId'] or '').strip() != row['document_id'].strip() and not binding:
            raise ValueError('Source identifier/native binding changed')
        members[item_id] = row
    capture_index = {}
    for capture in captures:
        uid, sha = capture.get('PPGDocumentUID'), capture.get('PPGCaptureSHA256')
        if uid in by_uid and sha and capture.get('PPGCaptureKind') == 'Document':
            capture_index.setdefault((uid, sha), []).append(capture['Id'])
    capture_rows = unique(captures, 'Id')
    bound_pairs = set()
    for binding in capture_bindings:
        validate_capture_binding(binding, by_uid, capture_rows)
        pair = (binding['documentUID'], binding['originalSHA256'])
        if pair in bound_pairs:
            raise ValueError('Duplicate explicit capture association')
        bound_pairs.add(pair)
        ids = capture_index.setdefault(pair, [])
        if binding['captureId'] not in ids:
            ids.append(binding['captureId'])
    local = {uid: [] for uid in by_uid}
    for source in sources:
        uid = source['documentUID']
        if uid not in by_uid or (uid, source['originalSHA256']) not in capture_index:
            raise ValueError('Unknown source identity or absent native capture')
        if source.get('text') is not None and hashlib.sha256(source['text'].encode()).hexdigest() != source['textSHA256']:
            raise ValueError('Source text hash mismatch')
        if source.get('identityState') not in {'exact_register_identifier', 'qualified_edition_variant', 'verified_source_identity'}:
            raise ValueError('Unqualified source association')
        if source.get('identityState') == 'verified_source_identity' and (uid, source['originalSHA256']) not in bound_pairs:
            raise ValueError('Historical source needs explicit byte-qualified capture binding')
        item = {k: v for k, v in source.items() if k != 'text'}
        item['nativeCaptureIds'] = capture_index[(uid, source['originalSHA256'])]
        local[uid].append(item)
    unique(relationships, 'RelationshipKey')
    rows = []
    for uid, row in by_uid.items():
        items = sorted(local[uid], key=lambda s: s['originalSHA256'])
        hashes = [s['originalSHA256'] for s in items]
        if len(hashes) != len(set(hashes)):
            raise ValueError('Duplicate source version')
        usable = [s for s in items if s.get('textSHA256') and s.get('textChars', 0) >= 200 and not s.get('extractionError') and not s.get('versionConflict')]
        member = members.get(row['Id'])
        state = ('awaiting_relationship_review' if usable else 'source_or_extraction_hold' if items else 'missing_qualified_text')
        rows.append(dict(documentUID=uid, nativeItemId=row['Id'], title=row['sourceTitle'],
            sourceDocumentId=row['sourceDocumentId'], nativeVersion=row.get('OData__UIVersionString'),
            membership='active_source_snapshot' if member else 'retained_outside_source_snapshot',
            sourceReconciliationState=member['status'] if member else 'not_in_retained_source_snapshot',
            coverageState=state, sources=items, relationshipAssessmentComplete=False,
            currentAuthorityVerified=False, noFindingEstablished=False,
            existingOutgoingKeys=[r['RelationshipKey'] for r in relationships if r['FromDocumentUID'] == uid],
            existingIncomingKeys=[r['RelationshipKey'] for r in relationships if r['ToDocumentUID'] == uid],
            assessmentKey='cr-assessment:' + digest([uid, row['sourceDocumentId']]),
            limitations=['Retained text/currency assertions are not current authority.',
                         'Literal candidate retrieval does not assess implicit dependencies.']))
        if member and member['document_id'] in aliases:
            rows[-1]['activeSourceDocumentId'] = member['document_id']
            rows[-1]['sourceMembershipBinding'] = aliases[member['document_id']]
    return dict(schemaVersion=1, kind='catalogue_relationship_coverage', observedAtUtc=observed_at,
        baselineSHA256=digest(catalogue), sourceMembershipSHA256=digest(source_rows),
        catalogueCount=len(rows), activeSourceCount=len(source_rows),
        boundActiveCount=len(members), unboundActiveSourceRows=unresolved,
        retainedOutsideSourceCount=len(rows)-len(members),
        coverageCounts=dict(Counter(r['coverageState'] for r in rows)),
        completedAssessmentCount=0, fullCoverageAchieved=False, rows=rows,
        existingRelationshipCount=len(relationships), nativeWrites=0)


def render(report, catalogue_url, annotation_url):
    for url in (catalogue_url, annotation_url):
        from urllib.parse import urlsplit
        parsed = urlsplit(url)
        if parsed.scheme != 'https' or not parsed.netloc or parsed.username or parsed.password:
            raise ValueError('Qualified HTTPS links required')
    esc = lambda x: html.escape(str(x), quote=True)
    parts = ['<h2>PPG relationships — coverage and review work</h2>',
        '<p>Evidence preparation is incomplete relationship assessment. No clinical acceptance or current-policy authority is established.</p>',
        '<p>' + esc(report['catalogueCount']) + ' stored identities; ' + esc(report['activeSourceCount']) +
        ' active source rows; ' + esc(len(report['unboundActiveSourceRows'])) + ' unbound active rows.</p>',
        '<p>' + esc(report['coverageCounts']) + '</p>',
        '<table><thead><tr><th>PPG</th><th>Coverage and membership</th><th>Existing links</th><th>Review context</th></tr></thead><tbody>']
    for row in report['rows']:
        from urllib.parse import urlencode
        uid = row['documentUID']
        href = annotation_url + ('&' if '?' in annotation_url else '?') + urlencode({'FilterField1': 'DocumentUID', 'FilterValue1': uid})
        parts.append('<tr id="ppg-' + esc(uid) + '"><td>' + esc(row['title']) + '</td><td>' +
            esc(row['coverageState']) + '; ' + esc(row['membership']) + '</td><td>' +
            esc(len(row['existingOutgoingKeys'])) + ' outgoing / ' + esc(len(row['existingIncomingKeys'])) +
            ' incoming</td><td><a href="' + esc(href) + '">Assessment annotations</a></td></tr>')
    parts.append('</tbody></table><p><a href="' + esc(catalogue_url) + '">Source catalogue</a></p>')
    return '\n'.join(parts)


def assessment_payloads(report):
    """Project progress rows to the isolated companion, never a completed review."""
    if report.get('fullCoverageAchieved') or report.get('completedAssessmentCount') != 0:
        raise ValueError('Progress projection cannot publish completed assessments')
    unique(report['rows'], 'assessmentKey')
    states = {'awaiting_relationship_review': 'Needs relationship review',
              'missing_qualified_text': 'Needs evidence',
              'source_or_extraction_hold': 'Source or extraction hold'}
    payloads = []
    for row in report['rows']:
        sources = [{k: v for k, v in s.items() if k not in {'originalPath', 'textPath'}}
                   for s in row['sources']]
        evidence = dict(schemaVersion=1, baselineSHA256=report['baselineSHA256'],
            sourceMembershipSHA256=report['sourceMembershipSHA256'], sources=sources,
            limitations=row['limitations'], existingOutgoingKeys=row['existingOutgoingKeys'],
            existingIncomingKeys=row['existingIncomingKeys'], currentAuthorityVerified=False)
        payloads.append(dict(Title=(row['title'] or row['sourceDocumentId'])[:255],
            AssessmentKey=row['assessmentKey'], DocumentUID=row['documentUID'],
            SourceDocumentId=row['sourceDocumentId'], AssessmentState=states[row['coverageState']],
            SourceMembership='Active source snapshot' if row['membership']=='active_source_snapshot'
                             else 'Retained outside source snapshot',
            SourceCount=len(sources), ExistingOutgoingCount=len(row['existingOutgoingKeys']),
            ExistingIncomingCount=len(row['existingIncomingKeys']),
            EvidenceManifest=json.dumps(evidence, ensure_ascii=False, sort_keys=True),
            AssessmentComplete=False, CurrentAuthorityVerified=False))
    return payloads


def plan_creates(payloads, native_rows):
    """Stable-key reconcile; any human/native divergence stops replacement."""
    expected, actual = unique(payloads, 'AssessmentKey'), unique(native_rows, 'AssessmentKey')
    creates, preserved = [], []
    for key, fields in expected.items():
        current = actual.get(key)
        if current is None:
            creates.append(fields)
        elif any(current.get(field) != value for field, value in fields.items()):
            raise ValueError('Existing assessment changed; preserve and reconcile')
        else:
            preserved.append(key)
    return {'creates': creates, 'preserved': preserved,
            'unrelatedRowsPreserved': len(set(actual)-set(expected))}


def dependency_proposal(source, target, source_quote, target_quote, rationale, change_impact):
    """A retained-edition proposal requires independently pinned endpoint passages."""
    if source['documentUID'] == target['documentUID']:
        raise ValueError('Self dependency')
    for item, quote in [(source, source_quote), (target, target_quote)]:
        if (not quote.strip() or quote not in (item.get('text') or '')
                or hashlib.sha256(item['text'].encode()).hexdigest() != item['textSHA256']
                or item.get('versionConflict') or not item.get('sourceVersion')):
            raise ValueError('Unverified endpoint passage or edition conflict')
    if not rationale.strip() or not change_impact.strip():
        raise ValueError('Dependency needs rationale and change implications')
    key = relationship_key(source['documentUID'], source['sourceVersion'],
                           target['documentUID'], target['sourceVersion'], 'depends_on')
    def citation(item, quote):
        offset = item['text'].index(quote)
        return dict(originalSHA256=item['originalSHA256'], textSHA256=item['textSHA256'],
            sourceVersion=item['sourceVersion'], quote=quote,
            locator=f"page:{item['text'][:offset].count(chr(12))+1};chars:{offset}-{offset+len(quote)}",
            printedVersion=item.get('printedVersion'), identityState=item['identityState'])
    evidence = dict(source=citation(source, source_quote), target=citation(target, target_quote),
        method='Passage-backed retained-edition operational dependency proposal',
        currentAuthorityVerified=False, appliesToRequestedEdition=False,
        establishesCompliance=False, changeImplications=change_impact)
    return dict(Title='Proposed retained-edition operational dependency', RelationshipKey=key,
        FromDocumentUID=source['documentUID'], ToDocumentUID=target['documentUID'],
        FromVersion=source['sourceVersion'], ToVersion=target['sourceVersion'],
        RelationshipType='depends_on', ReviewState='Proposed',
        Rationale=rationale, EvidenceRef=json.dumps(evidence, ensure_ascii=False, sort_keys=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    pack = json.loads(args.input.read_text())
    result = coverage(**pack)
    with args.output.open('x') as stream:
        json.dump(result, stream, indent=2, ensure_ascii=False)
    print(json.dumps({k: result[k] for k in ['catalogueCount', 'activeSourceCount', 'boundActiveCount', 'coverageCounts', 'fullCoverageAchieved', 'nativeWrites']}))


if __name__ == '__main__':
    main()
