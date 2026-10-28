# Copyright 2026 CareOps contributors. SPDX-License-Identifier: Apache-2.0
"""Map explicitly read SharePoint properties to the existing H2 review contract.

Pure maker preparation only. The caller owns authenticated exact-target reads,
byte hashes, source-kind qualification and freshness. No access or approval is
inferred from supplied metadata. Operators retain native fields/lookups.
"""
import re
from uuid import UUID
from scripts.forum_native_package import build_package

CONTROLS = {'Papers':'papers','Review':'review','Service returns':'returns','Risks':'risks'}
STATES = {'Unverified':'unverified','Draft':'draft','Conflicting':'conflicting','Recorded':'recorded'}
EVENTS = {'Single meeting':'singleInstance','Recurring occurrence':'occurrence','Moved occurrence':'exception'}
BINDING = {'library_id','profile_type_id','occurrence_type_id','binding_ref','destination_ref','register_ref'}


def _guid(value):
    if not isinstance(value,str) or not UUID(value).int or str(UUID(value))!=value.lower():
        raise ValueError('Canonical nonzero GUID required')
    return value.lower()


def _positive(value):
    if type(value)is not int or not 0<value<=2147483647:
        raise ValueError('Positive native integer required')
    return value


def _utc(value):
    if not isinstance(value,str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,7})?Z',value):
        raise ValueError('Explicit native UTC time required')
    return value


def _pin(row,sha256,role,ref,library):
    file=row['File'];item=_positive(row['Id'])
    if row['FileSystemObjectType']!=0 or type(row['FileSystemObjectType'])is not int or file['Exists']is not True:
        raise ValueError('Existing native file required')
    if row['odata.editLink'].lower()!=f"web/lists(guid'{library}')/items({item})":
        raise ValueError('Native item/library binding mismatch')
    version=file['UIVersionLabel']
    if version!=str(file['MajorVersion'])+'.'+str(file['MinorVersion']):
        raise ValueError('Inconsistent native version')
    return dict(role=role,ref=ref,list_id=library,item_id=item,file_id=_guid(file['UniqueId']),item_etag=row['odata.etag'],file_etag=file['ETag'],file_version=version,sha256=sha256)


def map_package(profile,occurrence,*,profile_sha256,occurrence_sha256,sources,binding,purpose):
    """Prepare a package from one native profile/occurrence and exact source set.

    ``sources`` contains current native ``item``, qualified ``kind`` and byte
    ``sha256`` per explicitly selected lookup. Include the maintained template
    and referenced governance/role evidence; extra/unselected sources refuse.
    Native file versions remain distinct from profile revision and authority.
    Historical source versions need separately qualified reads, never this mapper.
    """
    try:
        if not isinstance(binding,dict) or set(binding)!=BINDING:
            raise ValueError('Exact maker binding required')
        lib=_guid(binding['library_id'])
        types=[binding[k] for k in ['profile_type_id','occurrence_type_id']]
        if any(not isinstance(t,str) or not re.fullmatch(r'0x0101[0-9a-fA-F]+',t) for t in types) or types[0].lower()==types[1].lower():
            raise ValueError('Distinct exact native content types required')
        if profile['ContentTypeId'].lower()!=types[0].lower() or occurrence['ContentTypeId'].lower()!=types[1].lower():
            raise ValueError('Wrong configuration content type')
        pid=_positive(profile['Id']);_positive(occurrence['Id'])
        if _positive(occurrence['H2ProfileId'])!=pid:
            raise ValueError('Occurrence selects another profile')
        forum='H2-forum-'+_guid(profile['File']['UniqueId']);occ='H2-occurrence-'+_guid(occurrence['File']['UniqueId'])
        pins=[_pin(profile,profile_sha256,'profile',forum,lib),_pin(occurrence,occurrence_sha256,'occurrence',occ,lib)]
        if not isinstance(sources,list) or not 1<=len(sources)<=256:
            raise ValueError('Explicit selected source set required')
        catalogue={};selected=[]
        for entry in sources:
            if not isinstance(entry,dict) or set(entry)!={'item','kind','sha256'}:
                raise ValueError('Exact native source observation required')
            row=entry['item'];sid=_positive(row['Id']);ref='H2-source-'+_guid(row['File']['UniqueId'])
            if sid in catalogue or row['ContentTypeId'].lower()in [t.lower()for t in types]:
                raise ValueError('Duplicate or configuration source refused')
            pin=_pin(row,entry['sha256'],'source',ref,lib);pins.append(pin)
            source=dict(source_ref=ref,kind=entry['kind'],name=row['File']['Name'],revision='v'+pin['file_version'],sha256=entry['sha256'])
            catalogue[sid]=source;selected.append(source)
        selected.sort(key=lambda source:source['source_ref'])
        def source_ref(value,kind=None):
            source=catalogue[_positive(value)]
            if kind is not None and source['kind']!=kind:
                raise ValueError('Wrong selected source kind')
            return source['source_ref']
        required={_positive(profile['H2TemplateId'])}
        template=source_ref(profile['H2TemplateId'],'template')
        def evidence(prefix):
            state=STATES[profile[prefix+'State']];sid=profile[prefix+'SourceId'if prefix=='H2Governance'else prefix+'EvidenceId']
            if sid is not None:
                required.add(_positive(sid));ref=source_ref(sid,'governance')
            else:ref=None
            if state=='recorded'and ref is None:
                raise ValueError('Recorded evidence lacks selected source')
            return dict(state=state,source_ref=ref)
        governance=evidence('H2Governance');roles={}
        for role in ['Chair','Delegate','Secretariat']:
            description=profile['H2'+role+'Role']
            if not isinstance(description,str) or not description.strip():
                raise ValueError('Role description required; no inferred delegation')
            roles[role.lower()]={**evidence('H2'+role), 'role_ref':forum+'-'+role.lower()}
        ids=occurrence['H2SourcesId']
        if not isinstance(ids,list) or len(ids)!=len(set(_positive(i)for i in ids)):
            raise ValueError('Explicit distinct source lookup values required')
        required.update(ids)
        if set(catalogue)!=required:
            raise ValueError('Missing or unselected native source')
        if profile['H2Destination']!='Existing qualification drafts' or profile['H2Register']!='Retained meeting action register (reference only)':
            raise ValueError('Unqualified destination/register choice')
        controls=profile['H2Controls']
        if not isinstance(controls,list) or not controls or len(set(controls))!=len(controls):
            raise ValueError('Distinct native control choices required')
        sections=profile['H2AgendaSections']
        if not isinstance(sections,list) or not sections or len(set(sections))!=len(sections) or not set(sections)<={'Decisions','Discussion','Service returns','Risk assurance'}:
            raise ValueError('Distinct qualified agenda section choices required')
        if occurrence['H2TimeZone']not in {'Australia/Brisbane','UTC'}:
            raise ValueError('Unqualified occurrence timezone')
        start=_utc(occurrence['H2Start']);end=_utc(occurrence['H2End'])
        original=occurrence['H2OriginalStart']
        event_type=EVENTS[occurrence['H2EventType']]
        if event_type=='singleInstance':
            if original is not None or occurrence['H2SeriesRef']is not None:
                raise ValueError('Unexpected single-instance lineage')
        else:original=_utc(original)
        capability='prepare'if purpose=='preparation-review'else'compare_calendar'
        p=dict(schema_version=1,forum_ref=forum,profile_revision=profile['H2Revision'],effective_from=_utc(profile['H2EffectiveFrom']),effective_until=None if profile['H2EffectiveUntil']is None else _utc(profile['H2EffectiveUntil']),display_name=profile['Title'],purpose=profile['H2Purpose'],control_keys=[CONTROLS[c]for c in controls],agenda_sections=profile['H2AgendaSections'],capabilities=[capability],governance=governance,roles=roles,binding_ref=binding['binding_ref'],template_ref=template,destination_ref=binding['destination_ref'],register_ref=binding['register_ref'])
        selection=dict(schema_version=1,forum_ref=forum,profile_revision=p['profile_revision'],occurrence_ref=occ,snapshot_revision='v'+pins[1]['file_version'],start=start,end=end,window_start=start,window_end=end,event=dict(event_ref=occurrence['H2EventRef'],series_ref=occurrence['H2SeriesRef'],original_start=original,type=event_type,subject=occurrence['Title'],organizer=occurrence['H2Organiser'],cancelled=occurrence['H2Cancelled']),capabilities=[capability],sources=selected)
        package=build_package([p],selection,observed_sources=dict(state='complete',sources=selected),native_pins=pins,purpose=purpose,output_revision=_positive(occurrence['H2OutputRevision']))
        return dict(package=package,native_authority=False,role_descriptions={r.lower():profile['H2'+r+'Role']for r in ['Chair','Delegate','Secretariat']},time_zone=occurrence['H2TimeZone'])
    except (KeyError,TypeError,AttributeError,OverflowError) as exc:
        raise ValueError('Incomplete or invalid native selection') from exc
