# Copyright 2026 CareOps contributors. SPDX-License-Identifier: Apache-2.0
"""Portable additive H2 library metadata; emits source plans, never native calls."""
from uuid import UUID, NAMESPACE_URL, uuid5
import xml.etree.ElementTree as ET


def _id(name):
    return str(uuid5(NAMESPACE_URL, 'https://careops.example.invalid/clinical-hub/h2/schema/v1/'+name))


def build_schema(library_id):
    """Return fresh local-field/type plans bound to one maker-selected library.

    Field IDs and reserved site-parent type IDs identify the portable schema,
    not a tenant. Native library-copy type IDs must be read back separately.
    Content-type field
    links and required flags are separate from the existing Document type. Hidden
    technical fields are a UX boundary, never a permission or approval assertion.
    """
    if not isinstance(library_id,str):
        raise ValueError('Explicit canonical library GUID required')
    try:
        parsed=UUID(library_id)
    except (ValueError,TypeError,AttributeError):
        raise ValueError('Explicit canonical library GUID required') from None
    if not parsed.int or str(parsed)!=library_id.lower():
        raise ValueError('Explicit canonical library GUID required')
    library_id=str(parsed)
    evidence=['Unverified','Draft','Conflicting','Recorded']
    rows=[
        ('H2Revision','Text','Profile revision'),
        ('H2EffectiveFrom','DateTime','Effective from'),
        ('H2EffectiveUntil','DateTime','Effective until'),
        ('H2Purpose','Note','Forum purpose'),
        ('H2Controls','MultiChoice','Preparation controls'),
        ('H2AgendaSections','MultiChoice','Agenda sections'),
        ('H2GovernanceState','Choice','Governance evidence state'),
        ('H2GovernanceSource','Lookup','Governance source'),
    ]
    for role in ['Chair','Delegate','Secretariat']:
        rows.extend([(f'H2{role}Role','Text',role+' role description'),
                     (f'H2{role}State','Choice',role+' evidence state'),
                     (f'H2{role}Evidence','Lookup',role+' evidence source')])
    rows.extend([
        ('H2Template','Lookup','Maintained template'),
        ('H2Destination','Choice','Permitted draft destination'),
        ('H2Register','Choice','Existing action register reference'),
        ('H2Profile','Lookup','Forum profile'),
        ('H2Start','DateTime','Occurrence start'),
        ('H2End','DateTime','Occurrence end'),
        ('H2OriginalStart','DateTime','Original occurrence start'),
        ('H2TimeZone','Choice','Occurrence timezone'),
        ('H2Organiser','Text','Organiser'),
        ('H2EventType','Choice','Occurrence type'),
        ('H2Cancelled','Boolean','Cancelled'),
        ('H2EventRef','Note','Maker event binding'),
        ('H2SeriesRef','Note','Maker series binding'),
        ('H2Sources','LookupMulti','Selected sources'),
        ('H2OutputRevision','Number','Preparation output revision'),
    ])
    choices={
        'H2Controls':['Papers','Review','Service returns','Risks'],
        'H2AgendaSections':['Decisions','Discussion','Service returns','Risk assurance'],
        'H2GovernanceState':evidence,
        **{f'H2{r}State':evidence for r in ['Chair','Delegate','Secretariat']},
        'H2Destination':['Existing qualification drafts'],
        'H2Register':['Retained meeting action register (reference only)'],
        'H2TimeZone':['Australia/Brisbane','UTC'],
        'H2EventType':['Not selected','Single meeting','Recurring occurrence','Moved occurrence'],
    }
    defaults={**{n:'Unverified'for n in choices if n.endswith('State')},
              'H2TimeZone':'Australia/Brisbane','H2EventType':'Not selected',
              'H2Cancelled':'0','H2OutputRevision':'1'}
    fields=[]
    for name,kind,label in rows:
        attrs={'ID':'{'+_id(name)+'}','Type':'Lookup'if kind=='LookupMulti'else kind,
               'Name':name,'StaticName':name,'DisplayName':label,'Required':'FALSE',
               'Group':'Clinical Hub forum configuration','ReadOnly':'FALSE'}
        if kind=='Text':attrs['MaxLength']='255'
        if kind=='Note':attrs.update(NumLines='6',RichText='FALSE')
        if kind=='DateTime':attrs['Format']='DateTime'
        if kind in {'Lookup','LookupMulti'}:
            attrs.update(List='{'+library_id+'}',ShowField='Title',Mult='TRUE'if kind=='LookupMulti'else'FALSE')
        if kind in {'Choice','MultiChoice'}:attrs['FillInChoice']='FALSE'
        if kind=='Number':attrs.update(Decimals='0',Min='1')
        if name in {'H2EventRef','H2SeriesRef'}:
            attrs.update(Hidden='TRUE',ShowInEditForm='FALSE',ShowInNewForm='FALSE')
        xml=ET.Element('Field',attrs)
        if name in choices:
            values=ET.SubElement(xml,'CHOICES')
            for value in choices[name]:ET.SubElement(values,'CHOICE').text=value
        if name in defaults:ET.SubElement(xml,'Default').text=defaults[name]
        fields.append(dict(name=name,id=attrs['ID'],type=kind,label=label,
                           xml=ET.tostring(xml,encoding='unicode')))
    profile=[name for name,_,_ in rows[:20]]
    occurrence=[name for name,_,_ in rows[20:]]
    content_types=[
        dict(name='Forum profile',id='0x010100'+UUID(_id('Forum profile')).hex,
             fields=['Title',*profile],required_fields=['Title','H2Revision','H2EffectiveFrom','H2Purpose','H2Controls','H2AgendaSections','H2GovernanceState']),
        dict(name='Forum occurrence',id='0x010100'+UUID(_id('Forum occurrence')).hex,
             fields=['Title',*occurrence],required_fields=['Title','H2Profile','H2Start','H2End','H2TimeZone','H2Organiser','H2EventType','H2OutputRevision']),
    ]
    return dict(schema_version=1,library_id=library_id,fields=fields,content_types=content_types,
                field_add_options=10,default_content_type_change=False,default_view_change=False,
                permission_change=False,create_library=False,native_authority=False)


def validate_field_readback(expected, actual):
    """Check an exact field model; caller separately proves URL/identity/read access.

    SharePoint may report TypeAsString=Lookup with AllowMultipleValues=True for
    XML Type=Lookup, Mult=TRUE. Accept that explicit composite, not a single lookup
    or a blanket normalisation. Service-owned XML attributes remain preserved.
    """
    if not isinstance(expected,dict) or not isinstance(actual,dict):
        raise ValueError('Field model objects required')
    try:
        wanted=ET.fromstring(expected['xml'])
        observed=ET.fromstring(actual['SchemaXml'])
        if UUID(actual['Id'])!=UUID(expected['id'].strip('{}')):
            raise ValueError('Field identity drift')
        if actual['InternalName']!=expected['name'] or actual.get('StaticName')!=expected['name']:
            raise ValueError('Field naming drift')
        if actual['Required']is not False or actual['ReadOnlyField']is not False:
            raise ValueError('Field flags drift')
        if actual['Hidden']is not (wanted.get('Hidden')=='TRUE'):
            raise ValueError('Field visibility drift')
        kind=expected['type']
        if kind=='LookupMulti':
            if actual['TypeAsString']not in {'Lookup','LookupMulti'} or actual.get('AllowMultipleValues')is not True or observed.get('Mult')!='TRUE':
                raise ValueError('Multiple-source lookup not qualified')
        elif actual['TypeAsString']!=kind:
            raise ValueError('Field type drift')
        if kind in {'Lookup','LookupMulti'}:
            if actual.get('AllowMultipleValues')is not (kind=='LookupMulti'):
                raise ValueError('Lookup multiplicity drift')
            if UUID(actual['LookupList'].strip('{}'))!=UUID(wanted.get('List').strip('{}')) or actual['LookupField']!='Title':
                raise ValueError('Lookup target drift')
        if kind in {'Choice','MultiChoice'}:
            if actual['Choices']!=[c.text for c in wanted.findall('CHOICES/CHOICE')]:
                raise ValueError('Choice set drift')
        default=wanted.findtext('Default')
        if default is not None and actual.get('DefaultValue')!=default:
            raise ValueError('Unsafe or changed default')
    except (KeyError,TypeError,AttributeError,ET.ParseError) as exc:
        raise ValueError('Incomplete field readback') from exc
    return {'status':'PASS','field':expected['name'],'native_authority':False,
            'limit':'Model consistency only; target, transport, rights and rendered behaviour are separate.'}


def validate_content_type_copy(expected, actual, library_scope, *, linked=False):
    """Check local-copy identity/links; caller proves target, rights and rendering.

    Reserved site-parent IDs are not native library-copy IDs. Require one native
    00+GUID suffix, exact scope/name/flags, and optionally the exact H2 link subset.
    Inherited standard links retain separate preimage comparison.
    """
    if type(linked) is not bool or not isinstance(library_scope,str) or not library_scope.startswith('/'):
        raise ValueError('Explicit native scope and linkage phase required')
    try:
        parent=expected['id'].lower();native=actual['StringId'].lower();suffix=native[len(parent):]
        if not native.startswith(parent) or len(suffix)!=34 or not suffix.startswith('00') or UUID(suffix[2:]).hex!=suffix[2:] or not UUID(suffix[2:]).int:
            raise ValueError('Native library-copy identity required')
        if actual['Name']!=expected['name'] or actual['Scope']!=library_scope:
            raise ValueError('Content-type name/scope drift')
        if any(actual[k]is not False for k in ['ReadOnly','Sealed','Hidden']):
            raise ValueError('Content-type flags drift')
        if linked:
            links=actual['FieldLinks'];by_name={f['Name']:f for f in links}
            if len(by_name)!=len(links):
                raise ValueError('Duplicate field links')
            if {n for n in by_name if n.startswith('H2')}!=set(expected['fields'])-{'Title'}:
                raise ValueError('Unexpected or missing H2 field links')
            for name in expected['fields']:
                link=by_name[name];ident='fa564e0f-0c70-4ab9-b863-0177e6ddd247'if name=='Title'else _id(name)
                if UUID(link['Id'])!=UUID(ident):
                    raise ValueError('Field-link identity drift')
                if link['Required']is not (name in expected['required_fields']):
                    raise ValueError('Field-link required flag drift')
                if link['Hidden']is not (name in {'H2EventRef','H2SeriesRef'}):
                    raise ValueError('Field-link visibility drift')
    except (KeyError,TypeError,AttributeError) as exc:
        raise ValueError('Incomplete content-type readback') from exc
    return {'status':'PASS','parent_id':expected['id'],'content_type_id':actual['StringId'],'linked':linked,'native_authority':False}
