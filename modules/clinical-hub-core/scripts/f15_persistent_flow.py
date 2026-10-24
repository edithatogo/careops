"""Standard SharePoint F15 writer builder; cloud expressions execute the lifecycle.

No tenant calls occur here. Inputs pin one fictional row and an existing qualified
SharePoint reference. SnapshotJson is the sole writable field; native source edits
stop the operation. The source register, minutes and role claims remain fictional.
"""
from copy import deepcopy
from uuid import UUID
from urllib.parse import urlsplit
from scripts.f15_resolution_lifecycle import ACTIONS, STATES, OPEN_STATES
from scripts.f09_isolated_writer import REGISTER_FIELD_TYPES

FIELD = 'SnapshotJson'


def schemas():
    text = {'type': 'string', 'minLength': 1, 'maxLength': 512}
    strings = {'type': 'array', 'items': text, 'maxItems': 64}
    dated = {'date_state': {'type': 'string', 'enum': ['known','unknown','ambiguous']},
             'date_value': {'type': ['string','null']}}
    response_props = {k: deepcopy(text) for k in ('response_id','action_id','evidence_ref','evidence_revision')}
    response_props.update(dated | {'state': {'type':'string','enum':['partial','complete','disputed','withdrawn','delayed']},
        'relevance': {'type':'string','enum':['not_reviewed','relevant','partial','irrelevant','disputed']},
        'components': deepcopy(strings), 'supersedes': deepcopy(strings)})
    response = {'type':'object','properties':response_props,'required':list(response_props)}
    closure_props = {k:deepcopy(text) for k in ('authority_ref','decision_ref','decision_revision','evidence_ref')}
    closure_props.update(dated)
    closure = {'type':['object','null'],'properties':closure_props,'required':list(closure_props)}
    binding_props = {k:deepcopy(text) for k in ('action_id','register_revision','minutes_record_id','minutes_revision','permission_revision')}
    binding = {'type':'object','properties':binding_props,'required':list(binding_props)}
    state_props = {'schema': {'type':'string','enum':['f15-lifecycle-v1']},
        'synthetic_only': {'type':'boolean','enum':[True]}, 'item_id':{'type':'integer','minimum':1},
        'item_guid':deepcopy(text),'status':{'type':'string','enum':sorted(STATES)},
        'state_version':{'type':'integer','minimum':0},'binding':deepcopy(binding),'current_binding':deepcopy(binding),
        'required_components':deepcopy(strings),'reported_completion':{'type':'string','enum':['unknown','incomplete','complete']},
        'responses':{'type':'array','items':response,'maxItems':64},
        'history':{'type':'array','items':{'type':'object','required':['request_id'],
            'properties':{'request_id':deepcopy(text)}},'maxItems':128},
        'closure':closure,'concern':{'type':'string'},'dissent':deepcopy(strings),
        'source_snapshot':{'type':'object','required':list(REGISTER_FIELD_TYPES)},
        'policy':{'type':'object','required':['revision','actions_by_role'],'properties':{
            'revision':deepcopy(text),'actions_by_role':{'type':'object',
            'required':['chair','secretariat','preparer'],'properties':{role:{'type':'array',
                'items':{'type':'string','enum':sorted(ACTIONS)}} for role in ('chair','secretariat','preparer')}}}}}
    state = {'type':'object','properties':state_props,'required':list(state_props)}
    request_props = {'request_id':deepcopy(text),'expected_version':{'type':'integer','minimum':0},
        'actor_role':{'type':'string','enum':['chair','secretariat','preparer']},
        'action':{'type':'string','enum':sorted(ACTIONS)},'reason':{'type':'string'},
        'evidence_ref':{'type':['string','null']},'successor_ref':{'type':['string','null']},
        'response':dict(deepcopy(response),type=['object','null']),'closure':deepcopy(closure)}
    request = {'type':'object','properties':request_props,
        'required':['request_id','expected_version','actor_role','action','reason']}
    return state, request


def build_persistent_lifecycle(baseline, *, site, list_id, item_id, item_guid, title,
                               legacy_id, entity_type, field_map, sharepoint_reference):
    """Build one pinned fictional lifecycle writer, preserving canonical identity."""
    parsed = urlsplit(site)
    if (parsed.scheme != 'https' or parsed.hostname != 'fictional-example.sharepoint.com'
            or not parsed.path.startswith('/teams/') or parsed.query or parsed.fragment
            or parsed.username or parsed.password or str(UUID(list_id)) != list_id
            or str(UUID(item_guid)) != item_guid or type(item_id) is not int or item_id < 1
            or not title.startswith('FICTIONAL ') or not legacy_id.startswith('FICTIONAL-')
            or not entity_type.startswith('SP.Data.')):
        raise ValueError('Exact qualified fictional source required')
    nested_invoker = (sharepoint_reference.get('runtimeSource') == 'invoker'
        and bool(sharepoint_reference.get('connection',{}).get('connectionReferenceLogicalName'))
        and sharepoint_reference.get('api',{}).get('name') == 'shared_sharepointonline')
    native_invoker = (sharepoint_reference.get('source') == 'Invoker'
        and bool(sharepoint_reference.get('connectionReferenceLogicalName'))
        and sharepoint_reference.get('id') == '/providers/Microsoft.PowerApps/apis/shared_sharepointonline')
    if (baseline['properties'].get('state') != 'Stopped'
            or set(field_map) != set(REGISTER_FIELD_TYPES)
            or len(set(field_map.values())) != len(field_map)
            or any(not isinstance(v,str) or not v.replace('_','').isalnum() for v in field_map.values())
            or any(v.casefold() == FIELD.casefold() for v in field_map.values())
            or field_map.get('Title') != 'Title'
            or not (nested_invoker or native_invoker)):
        raise ValueError('Stopped baseline, native field map and qualified Invoker reference required')
    result=deepcopy(baseline);props=result['properties'];d=props['definition']
    props['connectionReferences']={'shared_sharepointonline':deepcopy(sharepoint_reference)}
    d.setdefault('parameters',{}).setdefault('$connections',{'defaultValue':{},'type':'Object'})
    d['triggers']={'manual':{'type':'Request','kind':'Button','inputs':{'schema':{
        'type':'object','properties':{'request_json':{'type':'string','title':'Fictional lifecycle request JSON'},
        'expected_etag':{'type':'string','title':'Exact current fictional item ETag'}},
        'required':['request_json','expected_etag']}}}}
    uri=f"_api/web/lists(guid'{list_id}')/items({item_id})"
    def after(name):return {name:['Succeeded']}
    def compose(value, predecessor):return {'type':'Compose','inputs':value,'runAfter':after(predecessor)}
    def guard(expression, predecessor, code):
        return {'type':'If','expression':expression,'runAfter':after(predecessor),'actions':{},
            'else':{'actions':{code:{'type':'Terminate','runAfter':{},'inputs':{'runStatus':'Failed','runError':{
                'code':code,'message':'No retry. Read current item, source and native history; retain human edits and reconcile.'}}}}}}
    def sp(method, predecessor=None, body=None, headers=None):
        params={'dataset':site,'parameters/method':method,'parameters/uri':uri,
                'parameters/headers':headers or {'Accept':'application/json;odata=minimalmetadata'}}
        if body is not None:params['parameters/body']=body
        return {'type':'OpenApiConnection','runAfter':after(predecessor) if predecessor else {},
            'inputs':{'host':{'apiId':'/providers/Microsoft.PowerApps/apis/shared_sharepointonline',
                'connectionName':'shared_sharepointonline','operationId':'HttpRequest'},
                'parameters':params,'retryPolicy':{'type':'none'}}}
    def lit(value):return "'"+value.replace("'","''")+"'"
    def arr(values):return 'createArray('+','.join(lit(v) for v in sorted(values))+')'
    def dated(value):
        return "if(equals("+value+"?['date_state'],'known'),equals(formatDateTime("+value+"?['date_value'],'yyyy-MM-dd'),"+value+"?['date_value']),and(contains(createArray('unknown','ambiguous'),"+value+"?['date_state']),equals("+value+"?['date_value'],null)))"
    ss,rs=schemas();q="body('Request')";s="outputs('State')";action=q+"?['action']";status=s+"?['status']"
    response=q+"?['response']";closure=q+"?['closure']"
    a={'Request':{'type':'ParseJson','runAfter':{},'inputs':{'content':"@json(triggerBody()?['request_json'])",'schema':rs}}}
    a['Read_item']=sp('GET','Request')
    etag="coalesce(outputs('Read_item')?['headers']?['ETag'],outputs('Read_item')?['headers']?['etag'],body('Read_item')?['odata.etag'])"
    a['Identity_guard']=guard("@and(equals(body('Read_item')?['Id'],"+str(item_id)+"),equals(toLower(body('Read_item')?['GUID']),"+lit(item_guid)+"),equals(body('Read_item')?['Title'],"+lit(title)+"),equals(body('Read_item')?["+lit(field_map['LegacyactionID'])+"],"+lit(legacy_id)+"),equals("+etag+",triggerBody()?['expected_etag']))",'Read_item','IDENTITY_OR_ETAG_STOP')
    a['Parse_state']={'type':'ParseJson','runAfter':after('Identity_guard'),
        'inputs':{'content':"@json(body('Read_item')?['SnapshotJson'])",'schema':ss}}
    a['State']=compose("@body('Parse_state')",'Parse_state')
    a['Native_source']=compose({k:"@body('Read_item')?["+lit(v)+"]" for k,v in field_map.items()},'State')
    a['Source_guard']=guard("@and(equals("+s+"?['item_id'],"+str(item_id)+"),equals("+s+"?['item_guid'],"+lit(item_guid)+"),equals("+s+"?['binding']?['action_id'],"+lit(legacy_id)+"),equals("+s+"?['binding'],"+s+"?['current_binding']),equals("+s+"?['policy']?['revision'],"+s+"?['binding']?['permission_revision']),equals("+s+"?['source_snapshot'],outputs('Native_source')),equals("+s+"?['state_version'],"+q+"?['expected_version']))",'Native_source','SOURCE_POLICY_OR_STATE_STOP')
    a['Duplicate_requests']={'type':'Query','runAfter':after('Source_guard'),'inputs':{'from':'@'+s+"?['history']",'where':"@equals(item()?['request_id'],"+q+"?['request_id'])"}}
    # The fixture's explicit source revision is authoritative independently of
    # the envelope and business-field snapshot. A new source revision must hold
    # even when the business wording happens to be identical.
    a['Source_guard']['expression'] = a['Source_guard']['expression'][:-1] + ",equals(" + s + "?['binding']?['register_revision'],body('Read_item')?['SourceRevision']))"
    a['Role_replay_guard']=guard("@and(not(empty(trim("+q+"?['request_id']))),empty(body('Duplicate_requests')),contains("+s+"?['policy']?['actions_by_role']?["+q+"?['actor_role']],"+action+"))",'Duplicate_requests','ROLE_OR_REPLAY_STOP')
    valid="or(and(contains("+arr(OPEN_STATES)+","+status+"),not(equals("+action+",'reopen'))),and(equals("+action+",'reopen'),contains(createArray('resolved','superseded'),"+status+")),and(equals("+action+",'record_response'),equals("+status+",'resolved'),contains(createArray('disputed','withdrawn'),"+response+"?['state'])))"
    a['Transition_guard']=guard('@'+valid,'Role_replay_guard','TRANSITION_STOP')
    a['Reason_guard']=guard("@or(contains(createArray('record_response','report_complete'),"+action+"),not(empty(trim("+q+"?['reason']))))",'Transition_guard','REASON_STOP')
    a['Response_IDs']={'type':'Select','runAfter':after('Reason_guard'),'inputs':{'from':'@'+s+"?['responses']",'select':"@item()?['response_id']"}}
    response_text=','.join("not(empty(trim("+response+"?["+lit(k)+"])))" for k in ('response_id','evidence_ref','evidence_revision'))
    response_valid="if(equals("+action+",'record_response'),if(equals("+response+",null),false,and("+response_text+",equals("+response+"?['action_id'],"+s+"?['binding']?['action_id']),not(contains(body('Response_IDs'),"+response+"?['response_id'])),"+dated(response)+",equals(length(intersection(body('Response_IDs'),"+response+"?['supersedes'])),length("+response+"?['supersedes'])))),true)"
    a['Response_guard']=guard('@'+response_valid,'Response_IDs','RESPONSE_STOP')
    a['Initialise_superseded']={'type':'InitializeVariable','runAfter':after('Response_guard'),'inputs':{'variables':[{'name':'Superseded','type':'array','value':[]}]}}
    a['Collect_superseded']={'type':'Foreach','runAfter':after('Initialise_superseded'),'foreach':'@'+s+"?['responses']",'runtimeConfiguration':{'concurrency':{'repetitions':1}},'actions':{
        'Merge_superseded':{'type':'Compose','runAfter':{},'inputs':"@union(variables('Superseded'),item()?['supersedes'])"},
        'Set_superseded':{'type':'SetVariable','runAfter':after('Merge_superseded'),'inputs':{'name':'Superseded','value':"@outputs('Merge_superseded')"}}}}
    a['Active_responses']={'type':'Query','runAfter':after('Collect_superseded'),'inputs':{'from':'@'+s+"?['responses']",'where':"@not(contains(variables('Superseded'),item()?['response_id']))"}}
    a['Unreviewed_responses']={'type':'Query','runAfter':after('Active_responses'),'inputs':{'from':"@body('Active_responses')",'where':"@or(not(equals(item()?['state'],'complete')),not(equals(item()?['relevance'],'relevant')))"}}
    a['Initialise_coverage']={'type':'InitializeVariable','runAfter':after('Unreviewed_responses'),'inputs':{'variables':[{'name':'Coverage','type':'array','value':[]}]}}
    a['Collect_coverage']={'type':'Foreach','runAfter':after('Initialise_coverage'),'foreach':"@body('Active_responses')",'runtimeConfiguration':{'concurrency':{'repetitions':1}},'actions':{
        'Merge_coverage':{'type':'Compose','runAfter':{},'inputs':"@union(variables('Coverage'),item()?['components'])"},
        'Set_coverage':{'type':'SetVariable','runAfter':after('Merge_coverage'),'inputs':{'name':'Coverage','value':"@outputs('Merge_coverage')"}}}}
    closure_text=','.join("not(empty(trim("+closure+"?["+lit(k)+"])))" for k in ('authority_ref','evidence_ref'))
    closure_valid="if(equals("+action+",'resolve'),if(equals("+closure+",null),false,and("+closure_text+",equals("+closure+"?['decision_ref'],"+s+"?['binding']?['minutes_record_id']),equals("+closure+"?['decision_revision'],"+s+"?['binding']?['minutes_revision']),"+dated(closure)+",not(empty(body('Active_responses'))),empty(body('Unreviewed_responses')),equals(length(intersection(variables('Coverage'),"+s+"?['required_components'])),length("+s+"?['required_components'])))),true)"
    a['Closure_guard']=guard('@'+closure_valid,'Collect_coverage','CLOSURE_REVIEW_STOP')
    a['Evidence_guard']=guard("@or(not(contains(createArray('reopen','supersede'),"+action+")),and(not(empty(trim(coalesce("+q+"?['evidence_ref'],'')))),or(not(equals("+action+",'supersede')),not(empty(trim(coalesce("+q+"?['successor_ref'],'')))))))",'Closure_guard','EVIDENCE_STOP')
    target=status
    for act,new in [('refer','referred'),('hold','held'),('return','returned'),('resolve','resolved'),('supersede','superseded'),('reopen','reopened')]:
        target="if(equals("+action+","+lit(act)+"),"+lit(new)+","+target+")"
    target="if(and(equals("+action+",'record_response'),equals("+status+",'resolved'),contains(createArray('disputed','withdrawn'),"+response+"?['state'])),'reopened',"+target+")"
    a['Target_state']=compose('@'+target,'Evidence_guard')
    event={'request_id':'@'+q+"?['request_id']",'event':'@'+action,'from':'@'+status,'to':"@outputs('Target_state')",'actor_role_claim':'@'+q+"?['actor_role']",'reason':'@'+q+"?['reason']",'evidence_ref':'@'+q+"?['evidence_ref']",'prior_closure':'@'+s+"?['closure']",'prior_event_id':"@if(empty("+s+"?['history']),null,last("+s+"?['history'])?['request_id'])",'fictional_only':True}
    a['Event']=compose(event,'Target_state')
    expr=s
    updates={'status':"outputs('Target_state')",'state_version':'add('+s+"?['state_version'],1)",
        'reported_completion':"if(equals("+action+",'report_complete'),'complete',"+s+"?['reported_completion'])",
        'responses':"if(equals("+action+",'record_response'),union("+s+"?['responses'],createArray("+response+")),"+s+"?['responses'])",
        'closure':"if(equals("+action+",'resolve'),"+closure+","+s+"?['closure'])",
        'successor_ref':"if(equals("+action+",'supersede'),"+q+"?['successor_ref'],"+s+"?['successor_ref'])",
        'history':"union("+s+"?['history'],createArray(outputs('Event')))"}
    for key,value in updates.items():expr='setProperty('+expr+','+lit(key)+','+value+')'
    a['Next_state']=compose('@'+expr,'Event')
    a['Size_guard']=guard("@and(lessOrEquals(length(string(outputs('Next_state'))),60000),lessOrEquals(length(outputs('Next_state')?['history']),128),lessOrEquals(length(outputs('Next_state')?['responses']),64))",'Next_state','SIZE_STOP')
    a['Save_state']=sp('POST','Size_guard',{'__metadata':{'type':entity_type},FIELD:"@string(outputs('Next_state'))"},
        {'Accept':'application/json;odata=nometadata','Content-Type':'application/json;odata=verbose','IF-MATCH':"@triggerBody()?['expected_etag']",'X-HTTP-Method':'MERGE'})
    a['Read_saved']=sp('GET','Save_state')
    a['Saved_guard']=guard("@and(equals(json(body('Read_saved')?['SnapshotJson']),outputs('Next_state')),"+','.join("equals(body('Read_saved')?["+lit(v)+"],body('Read_item')?["+lit(v)+"])" for v in field_map.values())+")",'Read_saved','UNCERTAIN_SAVE_RECONCILE')
    a['Result']=compose({'status':'FICTIONAL_LIFECYCLE_SAVED','disposition':"@outputs('Target_state')",'state_version':"@outputs('Next_state')?['state_version']",'business_approval':False,'notified':False},'Saved_guard')
    a['Saved_guard']['expression'] = a['Saved_guard']['expression'][:-1] + ",equals(body('Read_saved')?['SourceRevision'],body('Read_item')?['SourceRevision']))"
    d['actions']=a
    return result
