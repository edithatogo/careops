"""Prepare missing relationship progress rows; never replace existing reviews.

Inputs and output contain installation data and must remain private. This command
does not authenticate, write to SharePoint or make substantive review decisions.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path


def unique(rows, field):
    result = {}
    for row in rows:
        key = row.get(field)
        if not isinstance(key, str) or not key.strip() or key in result:
            raise ValueError('Missing or duplicate ' + field)
        result[key] = row
    return result


def prepare(catalogue, assessments, relationships, membership=None):
    membership = membership or {}
    sources = unique(catalogue, 'DocumentUID')
    existing = unique(assessments, 'DocumentUID')
    unique(assessments, 'AssessmentKey')
    unique(relationships, 'RelationshipKey')
    creates = []
    conflicts = []
    for uid, row in sources.items():
        identifier = row.get('sourceDocumentId')
        title = row.get('Title') or row.get('sourceTitle')
        if not isinstance(identifier, str) or not identifier.strip() or not isinstance(title, str) or not title.strip():
            conflicts.append({'documentUID': uid, 'reason': 'Missing source identifier or title'})
            continue
        if uid in existing:
            if existing[uid].get('SourceDocumentId') != identifier:
                conflicts.append({'documentUID': uid, 'reason': 'Source identity changed; preserve existing assessment'})
            continue
        source_membership = membership.get(uid)
        if source_membership not in {"Active source snapshot", "Retained outside source snapshot"}:
            conflicts.append({"documentUID": uid, "reason": "Qualified active/retained source membership required"})
            continue
        key = hashlib.sha256(json.dumps([uid, identifier], ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()
        evidence = {'schemaVersion': 1, 'currentAuthorityVerified': False,
                    'sources': [], 'catalogueItemId': row.get('Id'),
                    'limitations': ['New catalogue identity; substantive relationship review pending.',
                                    'A body binding does not establish current approval or full source qualification.']}
        creates.append({'Title': title[:255], 'AssessmentKey': 'cr-assessment:' + key,
                        'DocumentUID': uid, 'SourceDocumentId': identifier,
                        'AssessmentState': 'Needs relationship review',
                        'SourceMembership': source_membership, 'SourceCount': 0,
                        'ExistingOutgoingCount': sum(r.get('FromDocumentUID') == uid for r in relationships),
                        'ExistingIncomingCount': sum(r.get('ToDocumentUID') == uid for r in relationships),
                        'EvidenceManifest': json.dumps(evidence, ensure_ascii=False, sort_keys=True),
                        'AssessmentComplete': False, 'CurrentAuthorityVerified': False})
    return {'schemaVersion': 1, 'creates': creates, 'conflicts': conflicts,
            'preservedAssessmentCount': len(existing),
            'retainedOutsideCatalogue': sorted(set(existing) - set(sources))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('catalogue', 'assessments', 'relationships', 'output'):
        parser.add_argument(name, type=Path)
    parser.add_argument("--membership", type=Path, required=True, help="Private qualified UID-to-membership mapping")
    args = parser.parse_args()
    result = prepare(*(json.loads(getattr(args, name).read_text()) for name in ('catalogue', 'assessments', 'relationships')), membership=json.loads(args.membership.read_text()))
    fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w', encoding='utf-8') as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
    return 2 if result['conflicts'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
