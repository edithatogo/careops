# Copyright 2026 CareOps contributors. SPDX-License-Identifier: Apache-2.0
"""Compile the single native H2 selected-file review bridge; no service calls.

Qualified maker packages are pinned in the definition, never an editable global
current-forum parameter. Operators select an occurrence file and readable purpose.
Only a create-only technical receipt can be written. Native save, invoker rights,
rendering, notification suppression and runtime/recovery remain separate proofs.
The Flow API ignored the subscription flag on create; do not serialize that
read-only preference or infer suppression from this stopped payload.
"""
from copy import deepcopy
import json
import re
from urllib.parse import urlsplit
from uuid import UUID
from scripts.forum_native_package import build_package
from scripts.forum_native_schema import build_schema
import xml.etree.ElementTree as ET

API='/providers/Microsoft.PowerApps/apis/shared_sharepointonline'
DISPLAY_NAME='Clinical Hub | H2 | Review selected forum configuration'


def _guid(value):
    if not isinstance(value,str) or not UUID(value).int or str(UUID(value))!=value.lower():
        raise ValueError('Canonical native GUID required')
    return value.lower()


def _lit(value):
    return "'"+value.replace("'","''")+"'"


def _literal_data(value):
    # Quote each string as one WDL literal. A whole catalog json(...) expression
    # can exceed the native expression limit; raw human strings can interpolate.
    if isinstance(value,str):
        expression='@string('+_lit(value)+')'
        if len(expression)>8192:
            raise ValueError('Qualified literal exceeds native expression limit')
        return expression
    if isinstance(value,list):return [_literal_data(v)for v in value]
    if isinstance(value,dict):return {k:_literal_data(v)for k,v in value.items()}
    return value



def _schema_pins(library_id):
    """Pin the owned field interpretation without touching default fields."""
    result=[]
    for field in build_schema(library_id)['fields']:
        xml=ET.fromstring(field['xml']);kind=field['type'];tests=[]
        if kind in {'Lookup','LookupMulti'}:
            tests.append("translate(translate(/Field/@List,'{}',''),'ABCDEF','abcdef')='"+library_id+"'")
            tests.append("/Field/@ShowField='Title'")
            tests.append("/Field/@Mult='TRUE'" if kind=='LookupMulti' else "not(/Field/@Mult='TRUE')")
        choices=xml.findall('CHOICES/CHOICE')
        if choices:
            tests.append("count(/Field/CHOICES/CHOICE)="+str(len(choices)))
            for index,choice in enumerate(choices,1):
                # Values are the fixed maintained schema, not operator text.
                if "'" in choice.text:raise ValueError('Qualify a new XPath literal shape')
                tests.append("/Field/CHOICES/CHOICE["+str(index)+"]='"+choice.text+"'")
        default=xml.findtext('Default')
        if default is not None:
            if "'" in default:raise ValueError('Qualify a new XPath literal shape')
            tests.append("/Field/Default='"+default+"'")
        result.append(dict(id=field['id'].strip('{}').lower(),name=field['name'],kind=kind,
                           hidden=xml.get('Hidden')=='TRUE',predicate=' and '.join(tests)or'true()'))
    return result


def build_bridge(*,site,library_id,library_scope,principal,sharepoint_reference,runtime_url,qualified_packages):
    """Compile qualified packages and exact native pins into one stopped bridge.

    Package readback metadata is caller-supplied qualification evidence, not
    authenticated by this pure compiler. No existing flow/ref is edited. Every
    connector action uses the fixed selected site/library and disables retries.
    runtime_url qualifies the observed connector metadata only: native saves
    resolve the runtime through the reference and omit the legacy host.api field.
    """
    try:
        lib=_guid(library_id);u=urlsplit(site);runtime=urlsplit(runtime_url)
        if u.scheme!='https' or not (u.hostname or '').endswith('.sharepoint.com') or u.query or u.fragment or u.username or u.password or u.port or not re.fullmatch(r'/(teams|sites)/[A-Za-z0-9_-]+',u.path):
            raise ValueError('Exact qualified SharePoint site required')
        if not isinstance(library_scope,str) or not library_scope.startswith(u.path+'/') or '/'in library_scope[len(u.path)+1:] or any(c in library_scope for c in ["'",'\\','?','#','%']) or library_scope.endswith('/.') or library_scope.endswith('/..'):
            raise ValueError('Exact single qualified library scope required')
        if runtime.scheme!='https' or not (runtime.hostname or '').endswith('.azure-apihub.net') or runtime.path!='/apim/sharepointonline' or runtime.query or runtime.fragment or runtime.username or runtime.password or runtime.port:
            raise ValueError('Qualified native SharePoint runtime URL required')
        if not isinstance(principal,str) or not re.fullmatch(r'[A-Za-z0-9._+-]+@[A-Za-z0-9.-]+',principal):
            raise ValueError('Exact current invoker principal required')
        ref=sharepoint_reference
        allowed_ref={'source','tier','id','connectionReferenceLogicalName','displayName','iconUri','brandColor','apiName','isProcessSimpleApiReferenceConversionAlreadyDone','connectionName'}
        if not isinstance(ref,dict) or not set(ref)<=allowed_ref:
            raise ValueError('Unexpected connection reference fields')
        if not isinstance(ref,dict) or ref.get('source')!='Invoker' or ref.get('tier')!='Standard' or ref.get('id')!=API or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,127}',ref.get('connectionReferenceLogicalName','')) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,255}',ref.get('connectionName','')):
            raise ValueError('Existing qualified standard Invoker logical/physical reference required')
        if not isinstance(qualified_packages,list) or not 1<=len(qualified_packages)<=128:
            raise ValueError('Bounded exact qualified package catalog required')
        catalog=[];identities=set();native_ids=set()
        for entry in qualified_packages:
            if not isinstance(entry,dict) or set(entry)!={'package','native'}:
                raise ValueError('Exact package/readback entry required')
            p=entry['package'];n=deepcopy(entry['native']);packet=json.loads(p['canonical_json']);payload=packet['payload'];snap=payload['snapshot'];selection=snap['selection']
            rebuilt=build_package([snap['profile']],selection,observed_sources={'state':'complete','sources':selection['sources']},native_pins=payload['native_pins'],purpose=packet['identity']['purpose'],output_revision=packet['identity']['output_revision'])
            if rebuilt!=p or any(pin['list_id']!=lib for pin in payload['native_pins']):
                raise ValueError('Package not qualified for the selected contract/library')
            if not isinstance(n,dict) or set(n)!={'item_id','file_id','file_etag','item_etag','version','name'} or n['name']!=p['package_name'] or type(n['item_id'])is not int or not 0<n['item_id']<=2147483647:
                raise ValueError('Exact native saved package identity required')
            n['file_id']=_guid(n['file_id'])
            if any(not isinstance(n[k],str) or not n[k].strip() or len(n[k])>2048 or any(ord(c)<32 for c in n[k])for k in ['file_etag','item_etag']):
                raise ValueError('Exact saved package ETags required')
            if not re.fullmatch(r'(0|[1-9][0-9]{0,7})\.(0|[1-9][0-9]{0,7})',n['version']) or n['version']=='0.0':
                raise ValueError('Native package version required')
            occurrence=next(pin for pin in payload['native_pins']if pin['role']=='occurrence')
            key=(occurrence['item_id'],packet['identity']['purpose'],occurrence['file_version'])
            if key in identities or n['item_id']in native_ids or any(n['item_id']==pin['item_id']for pin in payload['native_pins']):
                raise ValueError('Duplicate/ambiguous catalog or package/source collision')
            identities.add(key);native_ids.add(n['item_id'])
            catalog.append(dict(occurrence_item_id=occurrence['item_id'],occurrence_file_id=occurrence['file_id'],occurrence_version=occurrence['file_version'],purpose=packet['identity']['purpose'],package_native=deepcopy(n),package=packet,package_sha256=p['sha256'],receipt_name=p['receipt_name']))
        catalog.sort(key=lambda c:(c['occurrence_item_id'],c['purpose'],c['occurrence_version']))
        if len(json.dumps(catalog).encode())>524288:
            raise ValueError('Qualified catalog exceeds bounded source limit')
    except (KeyError,TypeError,AttributeError,StopIteration) as exc:
        raise ValueError('Incomplete qualified bridge binding') from exc

    def after(name,statuses=None):return {name:statuses or ['Succeeded']}if name else{}
    def compose(value,previous=None):return dict(type='Compose',inputs=value,runAfter=after(previous))
    def guard(expression,previous,code):
        return dict(type='If',expression=expression,runAfter=after(previous),actions={},**{'else':{'actions':{
            code+'_reason':compose({'status':'held','reason':code,'receipt_created':False,'send_authority':False}),
            code+'_stop':dict(type='Terminate',runAfter=after(code+'_reason'),inputs={'runStatus':'Succeeded'})}}})
    def sp(method,uri,previous=None,body=None,headers=None):
        parameters={'dataset':site,'parameters/method':method,'parameters/uri':uri,'parameters/headers':headers or {'Accept':'application/json;odata=minimalmetadata'}}
        if body is not None:parameters['parameters/body']=body
        return dict(type='OpenApiConnection',runAfter=after(previous),inputs={'host':{'apiId':API,'connectionName':'shared_sharepointonline','operationId':'HttpRequest'},'parameters':parameters,'retryPolicy':{'type':'none'}})
    base="_api/web/lists(guid'"+lib+"')/items("
    folder="_api/web/GetFolderByServerRelativePath(decodedUrl='"+library_scope+"')"
    a={}
    a['Read_invoker']=sp('GET','_api/web/currentuser?$select=LoginName')
    a['Invoker_guard']=guard('@equals(toLower(last(split(body(\'Read_invoker\')?[\'LoginName\'],\'|\'))),'+_lit(principal.lower())+')','Read_invoker','INVOKER_NOT_QUALIFIED')
    a['Expected_schema']=compose(_literal_data(_schema_pins(lib)),'Invoker_guard')
    schema_uri="_api/web/lists(guid'"+lib+"')/fields?$select=Id,InternalName,StaticName,TypeAsString,Required,ReadOnlyField,Hidden,SchemaXml&$top=250"
    a['Read_owned_schema']=sp('GET',schema_uri,'Expected_schema')
    a['Schema_page_guard']=guard("@not(or(contains(body('Read_owned_schema'),'odata.nextLink'),contains(body('Read_owned_schema'),'@odata.nextLink'),contains(body('Read_owned_schema'),'__next')))",'Read_owned_schema','SCHEMA_READ_INCOMPLETE')
    a['Initialise_schema_errors']=dict(type='InitializeVariable',runAfter=after('Schema_page_guard'),inputs={'variables':[{'name':'Schema_errors','type':'array','value':[]}]})
    expected="items('Check_owned_schema')";actual="outputs('Owned_field')"
    find=dict(type='Query',runAfter={},inputs={'from':"@body('Read_owned_schema')?['value']",'where':"@equals(toLower(item()?['Id']),"+expected+"?['id'])"})
    metadata="and(equals("+actual+"?['InternalName'],"+expected+"?['name']),equals("+actual+"?['StaticName'],"+expected+"?['name']),equals("+actual+"?['Required'],false),equals("+actual+"?['ReadOnlyField'],false),equals("+actual+"?['Hidden'],"+expected+"?['hidden']))"
    datatype="if(equals("+expected+"?['kind'],'LookupMulti'),or(equals("+actual+"?['TypeAsString'],'Lookup'),equals("+actual+"?['TypeAsString'],'LookupMulti')),equals("+actual+"?['TypeAsString'],"+expected+"?['kind']))"
    semantic="equals(xpath(xml("+actual+"?['SchemaXml']),"+expected+"?['predicate']),true)"
    mismatch=dict(type='AppendToArrayVariable',runAfter={},inputs={'name':'Schema_errors','value':'@'+expected})
    matches=dict(type='If',runAfter=after('Owned_field'),expression='@and('+metadata+','+datatype+','+semantic+')',actions={},**{'else':{'actions':{'Record_schema_mismatch':deepcopy(mismatch)}}})
    present=dict(type='If',runAfter=after('Find_owned_field'),expression="@equals(length(body('Find_owned_field')),1)",actions={'Owned_field':compose("@first(body('Find_owned_field'))"),'Field_matches':matches},**{'else':{'actions':{'Record_missing_schema':deepcopy(mismatch)}}})
    a['Check_owned_schema']=dict(type='Foreach',runAfter=after('Initialise_schema_errors'),foreach="@outputs('Expected_schema')",runtimeConfiguration={'concurrency':{'repetitions':1}},actions={'Find_owned_field':find,'Field_present':present})
    a['Schema_guard']=guard("@empty(variables('Schema_errors'))",'Check_owned_schema','OWNED_SCHEMA_DRIFT')
    a['Qualified_packages']=compose(_literal_data(catalog),'Schema_guard')
    a['Read_occurrence']=sp('GET',"@concat("+_lit(base)+",string(int(triggerBody()?['entity']?['ID'])),')?$expand=File&$select=*,H2EventRef,H2SeriesRef')",'Qualified_packages')
    a['Selected_purpose']=compose("@if(equals(triggerBody()?['purpose'],'Preparation review'),'preparation-review',if(equals(triggerBody()?['purpose'],'Calendar comparison inputs'),'calendar-review','invalid'))",'Read_occurrence')
    a['Find_package']=dict(type='Query',runAfter=after('Selected_purpose'),inputs={'from':"@outputs('Qualified_packages')",'where':"@and(equals(item()?['occurrence_item_id'],body('Read_occurrence')?['Id']),equals(item()?['occurrence_version'],body('Read_occurrence')?['File']?['UIVersionLabel']),equals(item()?['purpose'],outputs('Selected_purpose')))"})
    a['Selection_guard']=guard("@and(equals(length(body('Find_package')),1),equals(triggerBody()?['entity']?['fileName'],body('Read_occurrence')?['File']?['Name']),startsWith(decodeUriComponent(triggerBody()?['entity']?['itemUrl']),"+_lit('https://'+u.netloc+library_scope+'/')+"))",'Find_package','SELECTION_NOT_QUALIFIED')
    a['Selected_package']=compose("@first(body('Find_package'))",'Selection_guard')
    chosen="outputs('Selected_package')";native=chosen+"?['package_native']"
    a['Occurrence_guard']=guard("@and(equals(toLower(body('Read_occurrence')?['File']?['UniqueId']),"+chosen+"?['occurrence_file_id']),equals(body('Read_occurrence')?['H2Cancelled'],false))",'Selected_package','OCCURRENCE_CHANGED_OR_CANCELLED')
    uri="@concat("+_lit(base)+",string("+native+"?['item_id']),')?$expand=File')"
    a['Read_package_metadata']=sp('GET',uri,'Occurrence_guard')
    a['Package_metadata_guard']=guard("@and(equals(toLower(body('Read_package_metadata')?['File']?['UniqueId']),"+native+"?['file_id']),equals(body('Read_package_metadata')?['File']?['ETag'],"+native+"?['file_etag']),equals(body('Read_package_metadata')?['odata.etag'],"+native+"?['item_etag']),equals(body('Read_package_metadata')?['File']?['UIVersionLabel'],"+native+"?['version']),equals(body('Read_package_metadata')?['File']?['Name'],"+native+"?['name']))",'Read_package_metadata','PACKAGE_CHANGED')
    a['Read_package_bytes']=sp('GET',"@concat("+_lit(base)+",string("+native+"?['item_id']),')/File/$value')",'Package_metadata_guard')
    a['Package_body']=compose("@json(string(body('Read_package_bytes')))",'Read_package_bytes')
    a['Package_body_guard']=guard('@equals(outputs(\'Package_body\'),'+chosen+"?['package'])",'Package_body','PACKAGE_CONTENT_MISMATCH')
    a['Initialise_pin_errors']=dict(type='InitializeVariable',runAfter=after('Package_body_guard'),inputs={'variables':[{'name':'Pin_errors','type':'array','value':[]}]})
    pin="items('Check_native_pins')"
    check=sp('GET',"@concat("+_lit(base)+",string("+pin+"?['item_id']),')?$expand=File')")
    condition="@and(equals(body('Read_pin')?['Id'],"+pin+"?['item_id']),equals(toLower(body('Read_pin')?['File']?['UniqueId']),"+pin+"?['file_id']),equals(body('Read_pin')?['odata.etag'],"+pin+"?['item_etag']),equals(body('Read_pin')?['File']?['ETag'],"+pin+"?['file_etag']),equals(body('Read_pin')?['File']?['UIVersionLabel'],"+pin+"?['file_version']))"
    a['Check_native_pins']=dict(type='Foreach',foreach="@outputs('Package_body')?['payload']?['native_pins']",runAfter=after('Initialise_pin_errors'),runtimeConfiguration={'concurrency':{'repetitions':1}},actions={'Read_pin':check,'Pin_matches':dict(type='If',runAfter=after('Read_pin'),expression=condition,actions={},**{'else':{'actions':{'Record_pin_error':dict(type='AppendToArrayVariable',runAfter={},inputs={'name':'Pin_errors','value':'@'+pin})}}})})
    a['Pin_guard']=guard("@empty(variables('Pin_errors'))",'Check_native_pins','NATIVE_PIN_DRIFT')
    a['Receipt_core']=compose({'schema_version':1,'state':'review_prepared','review_only':True,'native_authority':False,'send_authority':False,'activation_authority':False,'operation_key':"@outputs('Package_body')?['operation_key']",'payload_sha256':"@outputs('Package_body')?['payload_sha256']",'package_sha256':"@outputs('Selected_package')?['package_sha256']",'package_native':"@outputs('Selected_package')?['package_native']",'snapshot':"@outputs('Package_body')?['payload']?['snapshot']",'native_pins':"@outputs('Package_body')?['payload']?['native_pins']",'preparation_control_keys':"@outputs('Package_body')?['payload']?['preparation_control_keys']",'agenda_sections':"@outputs('Package_body')?['payload']?['agenda_sections']",'f12_selection':"@outputs('Package_body')?['payload']?['f12_selection']",'invoker':"@body('Read_invoker')?['LoginName']",'freshness_limit':'Current read observations only; requalify before substantive use. No multi-resource transaction or governance approval.'},'Pin_guard')
    filename="outputs('Selected_package')?['receipt_name']"
    query="@concat("+_lit(folder+"/Files?$select=Name,UniqueId&$filter=Name eq '")+","+filename+",'''&$top=2')"
    a['Find_receipt']=sp('GET',query,'Receipt_core')
    a['Receipt_count_guard']=guard("@lessOrEquals(length(body('Find_receipt')?['value']),1)",'Find_receipt','AMBIGUOUS_RECEIPT')
    receipt={'core':"@outputs('Receipt_core')",'creator_run_id':"@workflow()?['run']?['name']",'observed_at':"@utcNow()"}
    create=sp('POST',"@concat("+_lit(folder+"/Files/Add(url='")+","+filename+",''',overwrite=false)')",body="@string(outputs('New_receipt'))",headers={'Accept':'application/json;odata=nometadata','Content-Type':'application/octet-stream'})
    a['New_receipt']=compose(receipt,'Receipt_count_guard')
    a['Create_if_absent']=dict(type='If',runAfter=after('New_receipt'),expression="@empty(body('Find_receipt')?['value'])",actions={'Create_receipt':create},**{'else':{'actions':{'Existing_receipt_preserved':compose('Reconcile the existing exact receipt; never overwrite.')}}})
    # Reconcile a success, race or unknown create result by reading the exact path.
    a['Read_saved_receipt']=sp('GET',"@concat("+_lit("_api/web/GetFileByServerRelativePath(decodedUrl='"+library_scope+'/')+","+filename+",''')/$value')")
    a['Read_saved_receipt']['runAfter']=after('Create_if_absent',['Succeeded','Failed','TimedOut'])
    a['Saved_receipt']=compose("@json(string(body('Read_saved_receipt')))",'Read_saved_receipt')
    a['Receipt_readback_guard']=guard("@and(equals(outputs('Saved_receipt')?['core'],outputs('Receipt_core')),not(empty(outputs('Saved_receipt')?['creator_run_id'])),not(empty(outputs('Saved_receipt')?['observed_at'])))",'Saved_receipt','RECEIPT_CONFLICT_OR_PARTIAL')
    a['Result']=compose({'state':'review_prepared','receipt_name':"@outputs('Selected_package')?['receipt_name']",'operation_key':"@outputs('Package_body')?['operation_key']",'receipt_creator_run':"@outputs('Saved_receipt')?['creator_run_id']",'send_authority':False,'native_authority':False},'Receipt_readback_guard')
    schema={'type':'object','properties':{'rows':{'type':'array','items':{'type':'object','properties':{'purpose':{'type':'string','title':'Review purpose','enum':['Preparation review','Calendar comparison inputs'],'x-ms-content-hint':'TEXT','x-ms-dynamically-added':True},'entity':{'type':'object','properties':{'ID':{'type':'integer'},'itemUrl':{'type':'string'},'fileName':{'type':'string'}},'required':['ID','itemUrl','fileName']}},'required':['purpose','entity']}}},'required':['rows']}
    trigger={'type':'Request','kind':'ApiConnection','splitOn':"@triggerBody()['rows']",'inputs':{'schema':schema,'host':{'connection':{'name':"@parameters('$connections')['shared_sharepointonline']['connectionId']"}},'operationId':'ForASelectedFileHybridTrigger','parameters':{'dataset':site,'table':lib}},'runtimeConfiguration':{'concurrency':{'runs':1}}}
    definition={'$schema':'https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#','contentVersion':'1.0.0.0','parameters':{'$connections':{'defaultValue':{},'type':'Object'},'$authentication':{'defaultValue':{},'type':'SecureObject'}},'triggers':{'manual':trigger},'actions':a,'outputs':{}}
    return {'properties':{'displayName':DISPLAY_NAME,'state':'Stopped','definition':definition,'connectionReferences':{'shared_sharepointonline':deepcopy(ref)}}}
