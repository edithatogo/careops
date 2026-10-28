# Copyright 2026 CareOps contributors. SPDX-License-Identifier: Apache-2.0
"""Maker-side immutable H2 package preparation; no native calls or authority.

Native read/authentication, permitted audience and exact version/ETag rechecks are
separate runtime requirements. Checksums describe content, never approval or an
authenticated signature. Ordinary operators edit native properties, not this JSON.
"""
import hashlib
import json
import re
from uuid import UUID
from scripts.forum_configuration import resolve

PIN = frozenset({'role','ref','list_id','item_id','file_id','item_etag','file_etag','file_version','sha256'})
PURPOSES = frozenset({'preparation-review','calendar-review'})


def _canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)


def _guid(value):
    if not isinstance(value,str):
        raise ValueError('Native GUID required')
    try:
        parsed=UUID(value)
    except ValueError:
        raise ValueError('Native GUID required') from None
    if not parsed.int or str(parsed)!=value.lower():
        raise ValueError('Canonical nonzero native GUID required')
    return str(parsed)


def _text(value):
    if not isinstance(value,str) or not value.strip() or len(value)>2048 or any(ord(c)<32 or 55296<=ord(c)<=57343 for c in value):
        raise ValueError('Nonempty bounded native metadata required')


def build_package(profiles,selection,*,observed_sources,native_pins,purpose,output_revision):
    """Prepare one review candidate and stable create-only native filenames.

    The existing resolver remains the profile/occurrence contract. Native pins
    must cover exactly its selected configuration and sources. Same identity with
    changed payload keeps the same receipt name, requiring reconciliation rather
    than a guessed retry or automatically minted revision. Native historical
    version reads, package saves and current-access checks remain unqualified here.
    """
    if not isinstance(purpose,str) or purpose not in PURPOSES or type(output_revision)is not int or not 1<=output_revision<=2147483647:
        raise ValueError('Explicit review purpose and positive output revision required')
    resolved=resolve(profiles,selection,observed_sources=observed_sources)
    if resolved['state']!='review_only':
        raise ValueError('Selection held: '+','.join(resolved['blockers']))
    if ('prepare'if purpose=='preparation-review'else'compare_calendar')not in selection['capabilities']:
        raise ValueError('Purpose not selected')
    sources={s['source_ref']:s for s in selection['sources']}
    wanted={('profile',selection['forum_ref']),('occurrence',selection['occurrence_ref'])}|{('source',ref)for ref in sources}
    if not isinstance(native_pins,list) or len(native_pins)!=len(wanted):
        raise ValueError('Exact native pin coverage required')
    pins=[];identities=set();physical={}
    for supplied in native_pins:
        if not isinstance(supplied,dict) or set(supplied)!=PIN:
            raise ValueError('Unexpected native pin fields')
        pin=dict(supplied)
        if not isinstance(pin['role'],str)or not isinstance(pin['ref'],str):
            raise ValueError('Native role/reference strings required')
        key=(pin['role'],pin['ref'])
        if key not in wanted or key in identities:
            raise ValueError('Missing, duplicate or unselected native reference')
        identities.add(key)
        pin['list_id']=_guid(pin['list_id']);pin['file_id']=_guid(pin['file_id'])
        if type(pin['item_id'])is not int or not 0<pin['item_id']<=2147483647:
            raise ValueError('Native item ID required')
        for field in ['item_etag','file_etag','file_version']:
            _text(pin[field])
        if not re.fullmatch(r'[0-9]{1,8}\.[0-9]{1,8}',pin['file_version']) or not any(int(x)for x in pin['file_version'].split('.')):
            raise ValueError('Explicit native file version required')
        if not isinstance(pin['sha256'],str) or not re.fullmatch('[a-f0-9]{64}',pin['sha256']):
            raise ValueError('Qualified native byte hash required')
        if pin['role']=='source'and pin['sha256']!=sources[pin['ref']]['sha256'].lower():
            raise ValueError('Native/source byte-hash mismatch')
        value=tuple(pin[k]for k in ['list_id','item_id','item_etag','file_etag','file_version','sha256'])
        if pin['file_id']in physical and physical[pin['file_id']]!=value:
            raise ValueError('Conflicting native aliases')
        physical[pin['file_id']]=value;pins.append(pin)
    by_role={p['role']:p for p in pins if p['role']!='source'}
    profile,occurrence=by_role['profile'],by_role['occurrence']
    if profile['list_id']!=occurrence['list_id']or profile['file_id']==occurrence['file_id']:
        raise ValueError('Separate configuration files in the selected library required')
    identity=dict(forum_ref=selection['forum_ref'],occurrence_ref=selection['occurrence_ref'],purpose=purpose,output_revision=output_revision)
    operation_key='H2-'+hashlib.sha256(_canonical(identity).encode()).hexdigest()
    payload=dict(snapshot=json.loads(resolved['snapshot_json']),snapshot_sha256=resolved['snapshot_sha256'],native_pins=sorted(pins,key=lambda p:(p['role'],p['ref'])),preparation_control_keys=resolved['preparation_control_keys'],agenda_sections=resolved['agenda_sections'],f12_selection=resolved['f12_selection'])
    payload_sha256=hashlib.sha256(_canonical(payload).encode()).hexdigest()
    packet=dict(schema_version=1,state='candidate',review_only=True,native_authority=False,send_authority=False,activation_authority=False,identity=identity,operation_key=operation_key,payload=payload,payload_sha256=payload_sha256)
    canonical=_canonical(packet);stem=occurrence['file_id']+'-'+purpose+'-r'+str(output_revision)
    return dict(canonical_json=canonical,sha256=hashlib.sha256(canonical.encode()).hexdigest(),operation_key=operation_key,payload_sha256=payload_sha256,package_name='H2-package-'+occurrence['file_id']+'-v'+occurrence['file_version'].replace('.','-')+'-'+purpose+'-r'+str(output_revision)+'.json',receipt_name='H2-receipt-'+stem+'.json',native_authority=False)
