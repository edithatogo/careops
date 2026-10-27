"""Compile a stopped Standard-connector worker; no network or deployment.

The existing manual compiler owns task identity/claim/recovery semantics. This
adapter embeds that same graph in serial item scopes; runtime proof is separate.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime
import re
from xml.sax.saxutils import escape

from scripts.correspondence_linked_action import build as manual_build, FIELDS, PLANNER, SHAREPOINT

AUTO_FIELDS = {'action_required':'PlannerActionRequired', 'action_title':'PlannerActionTitle',
               'task_state':'PlannerTaskState', 'completed_at':'PlannerTaskCompletedAt',
               'waiting_since':'WaitingSince'}
PROTECTED = {'Completed','CaptureState','Actions','SavedEmail','SourceMessageKey','DueDate',
             'Title','DateRecd','Author','Editor','Modified','Created','ID','Id'}
PROTECTED_FOLDED = {name.casefold() for name in PROTECTED}


def eligible(item, config):
    f={**AUTO_FIELDS, **config.get('automation_fields',{})}
    title=item.get(f['action_title'])
    return (isinstance(item.get('Id'),int) and not isinstance(item['Id'],bool) and item['Id']>0
            and item.get('CaptureState')=='Reviewed' and item.get('Completed') in config['open_progress']
            and item.get(f['action_required']) is True and isinstance(title,str)
            and 1 <= len(title.strip()) <= 120)


def _date(value):
    if not isinstance(value,str):
        return None
    try:
        parsed=datetime.fromisoformat(value.replace('Z','+00:00'))
        return value if parsed.tzinfo is not None else None
    except ValueError:
        return None


def snapshot_patch(item, task, fields=None):
    """Offline contract oracle: never mutate input or business status."""
    f={**AUTO_FIELDS, **(fields or {})}
    if any(f[k].casefold() in PROTECTED_FOLDED for k in ['task_state','completed_at']) or f['task_state'].casefold()==f['completed_at'].casefold():
        raise ValueError('Snapshot fields must be distinct technical fields')
    p=task.get('percentComplete') if isinstance(task,dict) else None
    if isinstance(p,bool) or not isinstance(p,int) or not 0<=p<=100 or p==100 and not _date(task.get('completedDateTime')):
        desired={f['task_state']:'Unavailable'}
    else:
        desired={f['task_state']:'Completed' if p==100 else 'Not started' if p==0 else 'In progress',
                 f['completed_at']:task['completedDateTime'] if p==100 else None}
    return {key:value for key,value in desired.items() if item.get(key)!=value}


def waiting_start(versions, current_label, waiting_value, *, complete):
    """Return the proven contiguous status transition, never Modified/first seen."""
    if not versions or versions[0].get('VersionLabel')!=current_label:
        return None
    if any(type(v.get('VersionId')) is not int or v['VersionId']<=0 for v in versions):
        return None
    if any(a['VersionId']<=b['VersionId'] for a,b in zip(versions,versions[1:])):
        return None
    waiting=[]
    for version in versions:
        if version.get('Completed')!=waiting_value:
            return _date(waiting[-1].get('Created')) if waiting else None
        waiting.append(version)
    return _date(waiting[-1].get('Created')) if complete else None


def field_specs():
    common='Required="FALSE"'
    return {
        'PlannerActionRequired':f'<Field Type="Boolean" Name="PlannerActionRequired" DisplayName="PlannerActionRequired" {common} Indexed="TRUE"><Default>0</Default></Field>',
        'PlannerActionTitle':f'<Field Type="Text" Name="PlannerActionTitle" DisplayName="PlannerActionTitle" {common} MaxLength="120"/>',
        'PlannerTaskState':f'<Field Type="Choice" Name="PlannerTaskState" DisplayName="PlannerTaskState" {common}><CHOICES>'+''.join('<CHOICE>'+s+'</CHOICE>' for s in ['Unknown','Not started','In progress','Completed','Unavailable'])+'</CHOICES></Field>',
        'PlannerTaskCompletedAt':f'<Field Type="DateTime" Name="PlannerTaskCompletedAt" DisplayName="PlannerTaskCompletedAt" {common} Format="DateTime"/>',
        'WaitingSince':f'<Field Type="DateTime" Name="WaitingSince" DisplayName="WaitingSince" {common} Format="DateTime"/>',
    }


def view_specs(config):
    f={**AUTO_FIELDS, **config.get('automation_fields',{})}
    base={**FIELDS, **config.get('fields',{})}
    def eq(field,value,kind='Choice'):
        return f'<Eq><FieldRef Name="{field}"/><Value Type="{kind}">{escape(value)}</Value></Eq>'
    active=eq('Completed',config['open_progress'][0])
    for value in config['open_progress'][1:]:active='<Or>'+active+eq('Completed',value)+'</Or>'
    fields=['LinkTitle','Completed',base['url'],f['task_state'],f['completed_at'],'SavedEmail']
    return {
        'Ready for closure review':{'query':'<Where><And>'+active+eq(f['task_state'],'Completed')+'</And></Where>', 'fields':fields},
        'Planner sync exceptions':{'query':'<Where>'+eq(f['task_state'],'Unavailable')+'</Where>', 'fields':fields},
        'Waiting too long':{'query':'<Where><And>'+eq('Completed',config['waiting_progress'])+f'<Leq><FieldRef Name="{f["waiting_since"]}"/><Value Type="DateTime" IncludeTimeValue="FALSE"><Today OffsetDays="-14"/></Value></Leq></And></Where>', 'fields':['LinkTitle','Completed',f['waiting_since'],'DueDate','SavedEmail']},
        'Waiting date unknown':{'query':'<Where><And>'+eq('Completed',config['waiting_progress'])+f'<IsNull><FieldRef Name="{f["waiting_since"]}"/></IsNull></And></Where>', 'fields':['LinkTitle','Completed',f['waiting_since'],'SavedEmail']},
    }


def _replace(value, old, new):
    if isinstance(value,str):return value.replace(old,new)
    if isinstance(value,list):return [_replace(v,old,new) for v in value]
    if isinstance(value,dict):return {k:_replace(v,old,new) for k,v in value.items()}
    return value


def _loop_validators(value):
    """A loop cannot contain Terminate; schema validation fails the item scope.

    Preserve the original rejection code in the validation payload. Failure stops
    success-only dependencies and is caught at the item boundary. No false success.
    """
    if isinstance(value,list):return [_loop_validators(v) for v in value]
    if not isinstance(value,dict):return value
    if value.get('type')=='Terminate':
        return {'type':'ParseJson','inputs':{'content':{'accepted':False,'code':value['inputs']['runError']['code']},
                'schema':{'type':'object','required':['accepted'],'properties':{'accepted':{'type':'boolean','enum':[True]}}}},
                'runAfter':value.get('runAfter',{})}
    return {k:_loop_validators(v) for k,v in value.items()}


def build(config):
    """Return portable stopped native source; never activate or execute it."""
    manual=manual_build(config)
    f={**AUTO_FIELDS, **config.get('automation_fields',{})}
    links={**FIELDS, **config.get('fields',{})}
    names=list(f.values())+list(links.values())
    if (any(not isinstance(n,str) for n in names) or len(names)!=len({n.casefold() for n in names})
            or any(not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*',n) or n.casefold() in PROTECTED_FOLDED for n in names)):
        raise ValueError('Distinct technical field names required; business fields are protected')
    active=config.get('open_progress');waiting=config.get('waiting_progress')
    if (not isinstance(active,list) or not active or len(active)>6 or waiting not in active
            or any(not isinstance(s,str) or not s or s in {'Completed','Closed',"Didn't Complete",'Cancelled','FYI','MSC Policies/Procedure'} for s in active)):
        raise ValueError('Explicit qualified open/waiting Progress choices required')
    page_size=config.get('page_size',20);max_pages=config.get('max_pages',5)
    if type(config.get('version_dates_utc_qualified',False)) is not bool:
        raise ValueError('Explicit Boolean version-date qualification required')
    if type(page_size) is not int or not 1<=page_size<=100 or type(max_pages) is not int or not 1<=max_pages<=10:
        raise ValueError('Bounded page configuration required')
    site=config['site_url'];reg="_api/web/lists(guid'"+config['register_list_id']+"')/items"
    literal=lambda s:s.replace("'","''")
    secure={'secureData':{'properties':['inputs','outputs']}}
    def compose(value,after=None):
        return {'type':'Compose','inputs':value,'runAfter':after or {},'runtimeConfiguration':{'secureData':{'properties':['inputs']}}}
    def setvar(name,value,after=None):
        return {'type':'SetVariable','inputs':{'name':name,'value':value},'runAfter':after or {}}
    def sp(method,uri,body=None,etag=None,after=None,verbose=False):
        headers={'Accept':'application/json;odata=verbose' if verbose else 'application/json;odata=nometadata'}
        p={'dataset':site,'parameters/method':method,'parameters/uri':uri,'parameters/headers':headers}
        if body is not None:p['parameters/body']=body;headers['Content-Type']='application/json;odata=nometadata'
        if etag is not None:headers.update({'IF-MATCH':etag,'X-HTTP-Method':'MERGE'})
        return {'type':'OpenApiConnection','inputs':{'host':{'apiId':SHAREPOINT,'connectionName':'shared_sharepointonline','operationId':'HttpRequest'},'parameters':p,'retryPolicy':{'type':'none'}},'runAfter':after or {},'runtimeConfiguration':secure}
    def planner(op,params,after=None):
        return {'type':'OpenApiConnection','inputs':{'host':{'apiId':PLANNER,'connectionName':'shared_planner','operationId':op},'parameters':params,'retryPolicy':{'type':'none'}},'runAfter':after or {},'runtimeConfiguration':secure}
    def reject(code):
        return _loop_validators({'type':'Terminate','inputs':{'runStatus':'Failed','runError':{'code':code}}})
    def gate(expression,actions,else_actions=None,after=None):
        return {'type':'If','expression':expression,'actions':actions,'else':{'actions':else_actions or {}},'runAfter':after or {}}
    def where_open(item):
        return 'or('+','.join("equals("+item+"?['Completed'],'"+literal(v)+"')" for v in active)+')'
    selected=','.join(['Id','CaptureState','Completed','OData__UIVersionString']+names)
    item_id="items('Process_rows')?['Id']"
    item_uri="@concat('"+literal(reg)+"(',string("+item_id+"),')')"
    read_uri="@concat('"+literal(reg)+"(',string("+item_id+"),')?$select="+selected+"')"
    eligibility="@and(equals(outputs('Item')?['CaptureState'],'Reviewed'),"+where_open("outputs('Item')")+",equals(outputs('Item')?['"+f['action_required']+"'],true),greater(length(trim(coalesce(outputs('Item')?['"+f['action_title']+"'],''))),0),lessOrEquals(length(trim(coalesce(outputs('Item')?['"+f['action_title']+"'],''))),120))"
    core=deepcopy(manual['properties']['definition']['actions'])
    core=_replace(core,"triggerBody()?['ItemId']",item_id)
    core=_replace(core,"triggerBody()?['ActionTitle']","outputs('Item')?['"+f['action_title']+"']")
    # Read fresh fields before the title/request validation, including eligibility.
    core['Init_task_id']=setvar('Task_id','')
    core['Read_item']=sp('GET',read_uri,verbose=True,after={'Init_task_id':['Succeeded']})
    core['Item']['runAfter']={'Read_item':['Succeeded']}
    core['Validate_request']['runAfter']={'Item':['Succeeded']}
    core['Reviewed_record']['runAfter']={'Validate_request':['Succeeded']}
    core['Reviewed_record']['expression']=eligibility
    # Existing linked IDs need no plan-wide task catalogue scan.
    lookup={k:core.pop(k) for k in ['List_tasks','Complete_plan_scan','Filter_tasks']}
    lookup['List_tasks']['runAfter']={}
    core['Plan_lookup']=gate("@empty(outputs('Item')?['"+links['id']+"'])",lookup,after={'Record_url':['Succeeded']})
    core['Task_route']['runAfter']={'Plan_lookup':['Succeeded']}
    core=_loop_validators(core)
    sync={
        'Sync_read_item':sp('GET',read_uri,verbose=True),
        'Sync_item':compose("@body('Sync_read_item')?['d']",{'Sync_read_item':['Succeeded']}),
    }
    sitem="outputs('Sync_item')"
    key="concat('COR-"+config['register_list_id']+"-',string("+item_id+"))"
    expected_key="@equals("+sitem+"?['"+links['key']+"'],"+key+")"
    work={
        'Link_identity':gate(expected_key,{}, {'Bad_link_identity':reject('TASK_RECORD_KEY_MISMATCH')}),
        'Get_linked_task':planner('GetTask_V2',{'id':"@"+sitem+"?['"+links['id']+"']"},{'Link_identity':['Succeeded']}),
        'Get_linked_details':planner('GetTaskDetails_V2',{'id':"@"+sitem+"?['"+links['id']+"']"},{'Get_linked_task':['Succeeded']}),
        'Sync_backlinks':{'type':'Query','inputs':{'from':"@coalesce(body('Get_linked_details')?['references'],json('[]'))",'where':"@equals(replace(coalesce(item()?['resourceLink'],''),' ','%20'),concat('"+literal(config['record_form_url'].replace(' ','%20'))+"?ID=',string("+item_id+")))"},'runAfter':{'Get_linked_details':['Succeeded']},'runtimeConfiguration':secure},
        'Task_identity_valid':gate("@and(equals(body('Get_linked_task')?['id'],"+sitem+"?['"+links['id']+"']),equals(body('Get_linked_task')?['planId'],'"+config['planner_plan_id']+"'),equals(length(body('Sync_backlinks')),1))",{}, {'Bad_task_identity':reject('TASK_RECORD_IDENTITY_MISMATCH')},{'Sync_backlinks':['Succeeded']}),
        'Task_contract':{'type':'ParseJson','inputs':{'content':{'percentComplete':"@body('Get_linked_task')?['percentComplete']"},'schema':{'type':'object','required':['percentComplete'],'properties':{'percentComplete':{'type':'integer','minimum':0,'maximum':100}}}},'runAfter':{'Task_identity_valid':['Succeeded']},'runtimeConfiguration':{'secureData':{'properties':['inputs']}}},
        'Completion_date_valid':gate("@or(not(equals(body('Get_linked_task')?['percentComplete'],100)),not(empty(body('Get_linked_task')?['completedDateTime'])))",{}, {'Missing_completion_date':reject('TASK_COMPLETION_DATE_MISSING')},{'Task_contract':['Succeeded']}),
        'Task_state':compose("@if(equals(body('Get_linked_task')?['percentComplete'],100),'Completed',if(equals(body('Get_linked_task')?['percentComplete'],0),'Not started','In progress'))",{'Completion_date_valid':['Succeeded']}),
        'Task_date':compose("@if(equals(body('Get_linked_task')?['percentComplete'],100),formatDateTime(body('Get_linked_task')?['completedDateTime'],'yyyy-MM-ddTHH:mm:ssZ'),null)",{'Task_state':['Succeeded']}),
        'Snapshot_body':compose({f['task_state']:"@outputs('Task_state')",f['completed_at']:"@outputs('Task_date')"},{'Task_date':['Succeeded']}),
        'Snapshot_changed':gate("@or(not(equals("+sitem+"?['"+f['task_state']+"'],outputs('Task_state'))),not(equals("+sitem+"?['"+f['completed_at']+"'],outputs('Task_date'))))",{'Save_snapshot':sp('POST',item_uri,body="@string(outputs('Snapshot_body'))",etag="@"+sitem+"?['__metadata']?['etag']")},after={'Snapshot_body':['Succeeded']}),
    }
    sync['Sync_open_link']=gate('@and('+where_open(sitem)+",not(empty("+sitem+"?['"+links['id']+"'])))",work,after={'Sync_item':['Succeeded']})
    # Failed reads/identity validation never retain a current Completed snapshot.
    unavailable={
        'Read_unavailable_latest':sp('GET',read_uri,verbose=True),
        'Unavailable_latest':compose("@body('Read_unavailable_latest')?['d']",{'Read_unavailable_latest':['Succeeded']}),
        'Unavailable_body':compose({f['task_state']:'Unavailable'},{'Unavailable_latest':['Succeeded']}),
        'Unavailable_changed':gate("@and("+where_open("outputs('Unavailable_latest')")+",not(empty(outputs('Unavailable_latest')?['"+links['id']+"'])),equals(outputs('Unavailable_latest')?['"+links['id']+"'],outputs('Sync_item')?['"+links['id']+"']),equals(outputs('Unavailable_latest')?['"+links['key']+"'],outputs('Sync_item')?['"+links['key']+"']),not(equals(outputs('Unavailable_latest')?['"+f['task_state']+"'],'Unavailable')))",{'Save_unavailable':sp('POST',item_uri,body="@string(outputs('Unavailable_body'))",etag="@outputs('Unavailable_latest')?['__metadata']?['etag']")},after={'Unavailable_body':['Succeeded']}),
        'Sync_failed_flag':setvar('Batch_failed',True,{'Unavailable_changed':['Succeeded','Failed','Skipped','TimedOut']}),
    }
    # Waiting history uses the latest contiguous status interval, never poll time.
    vuri="@concat('"+literal(reg)+"(',string("+item_id+"),')/versions?$select=VersionId,VersionLabel,Created,Completed&$orderby=VersionId desc&$top=100')"
    vwork={
        'Read_versions':sp('GET',vuri),
        'Other_status_versions':{'type':'Query','inputs':{'from':"@body('Read_versions')?['value']",'where':"@not(equals(item()?['Completed'],'"+literal(waiting)+"'))"},'runAfter':{'Read_versions':['Succeeded']},'runtimeConfiguration':secure},
        'Waiting_interval_versions':{'type':'Query','inputs':{'from':"@body('Read_versions')?['value']",'where':"@and(equals(item()?['Completed'],'"+literal(waiting)+"'),greater(int(item()?['VersionId']),if(empty(body('Other_status_versions')),0,int(first(body('Other_status_versions'))?['VersionId']))))"},'runAfter':{'Other_status_versions':['Succeeded']},'runtimeConfiguration':secure},
        'Waiting_proven':gate("@and(not(empty(body('Waiting_interval_versions'))),equals(first(body('Read_versions')?['value'])?['VersionLabel'],outputs('Waiting_item')?['OData__UIVersionString']),or(not(empty(body('Other_status_versions'))),and(empty(coalesce(body('Read_versions')?['@odata.nextLink'],body('Read_versions')?['odata.nextLink'])),less(length(body('Read_versions')?['value']),100))),equals(parameters('VersionDatesUtcQualified'),true))",{
            'Waiting_body':compose({f['waiting_since']:"@concat(formatDateTime(last(body('Waiting_interval_versions'))?['Created'],'yyyy-MM-ddTHH:mm:ss'),'Z')"}),
            'Waiting_changed':gate("@not(equals(outputs('Waiting_body')?['"+f['waiting_since']+"'],outputs('Waiting_item')?['"+f['waiting_since']+"']))",{'Save_waiting_date':sp('POST',item_uri,body="@string(outputs('Waiting_body'))",etag="@outputs('Waiting_item')?['__metadata']?['etag']")},after={'Waiting_body':['Succeeded']}),
        }, {'Waiting_unknown_body':compose({f['waiting_since']:None}),
            'Waiting_unknown_changed':gate("@not(empty(outputs('Waiting_item')?['"+f['waiting_since']+"']))",{'Clear_unproven_waiting_date':sp('POST',item_uri,body="@string(outputs('Waiting_unknown_body'))",etag="@outputs('Waiting_item')?['__metadata']?['etag']")},after={'Waiting_unknown_body':['Succeeded']})},after={'Waiting_interval_versions':['Succeeded']}),
    }
    wait={
        'Read_waiting_latest':sp('GET',read_uri,verbose=True),
        'Waiting_item':compose("@body('Read_waiting_latest')?['d']",{'Read_waiting_latest':['Succeeded']}),
        'Needs_waiting_date':gate("@equals(outputs('Waiting_item')?['Completed'],'"+literal(waiting)+"')",vwork,
            {'Waiting_ended_body':compose({f['waiting_since']:None}),
             'Waiting_ended_changed':gate("@and("+where_open("outputs('Waiting_item')")+",not(empty(outputs('Waiting_item')?['"+f['waiting_since']+"'])))",{'Clear_ended_waiting_date':sp('POST',item_uri,body="@string(outputs('Waiting_ended_body'))",etag="@outputs('Waiting_item')?['__metadata']?['etag']")},after={'Waiting_ended_body':['Succeeded']})},after={'Waiting_item':['Succeeded']}),
    }
    waiting_failure={
        'Read_waiting_failure_latest':sp('GET',read_uri,verbose=True),
        'Waiting_failure_item':compose("@body('Read_waiting_failure_latest')?['d']",{'Read_waiting_failure_latest':['Succeeded']}),
        'Waiting_failure_body':compose({f['waiting_since']:None},{'Waiting_failure_item':['Succeeded']}),
        'Waiting_failure_unknown':gate("@and(equals(outputs('Waiting_failure_item')?['Completed'],'"+literal(waiting)+"'),not(empty(outputs('Waiting_failure_item')?['"+f['waiting_since']+"'])))",{'Clear_failed_waiting_date':sp('POST',item_uri,body="@string(outputs('Waiting_failure_body'))",etag="@outputs('Waiting_failure_item')?['__metadata']?['etag']")},after={'Waiting_failure_body':['Succeeded']}),
    }
    row={
        'Create_or_recover':gate("@and(equals(items('Process_rows')?['CaptureState'],'Reviewed'),equals(items('Process_rows')?['"+f['action_required']+"'],true),empty(items('Process_rows')?['"+links['id']+"']))",core),
        'Sync_scope':{'type':'Scope','actions':sync,'runAfter':{'Create_or_recover':['Succeeded','Failed','Skipped','TimedOut']}},
        'Sync_unavailable':{'type':'Scope','actions':unavailable,'runAfter':{'Sync_scope':['Failed','TimedOut']}},
        'Waiting_scope':{'type':'Scope','actions':wait,'runAfter':{'Sync_unavailable':['Succeeded','Failed','Skipped','TimedOut']}},
        'Waiting_unavailable':{'type':'Scope','actions':waiting_failure,'runAfter':{'Waiting_scope':['Failed','TimedOut']}},
        'Record_failed':gate("@or(not(equals(actions('Create_or_recover')?['status'],'Succeeded')),not(equals(actions('Sync_scope')?['status'],'Succeeded')),not(equals(actions('Waiting_scope')?['status'],'Succeeded')))",{'Record_failure_flag':setvar('Batch_failed',True)},after={'Waiting_unavailable':['Succeeded','Failed','Skipped','TimedOut']}),
        'Throttle':{'type':'Wait','inputs':{'interval':{'count':10,'unit':'Second'}},'runAfter':{'Record_failed':['Succeeded','Failed']}},
    }
    query=' or '.join("Completed eq '"+literal(v)+"'" for v in active)
    filter_query='('+query+") and ((CaptureState eq 'Reviewed' and "+f['action_required']+" eq 1) or "+links['id']+" ne null or Completed eq '"+literal(waiting)+"')"
    first_uri=reg+'?$select='+selected+'&$filter='+filter_query+'&$orderby=Id asc&$top='+str(page_size)
    page={
        'Read_page':sp('GET',"@variables('Next_uri')"),
        'Process_rows':{'type':'Foreach','foreach':"@body('Read_page')?['value']",'actions':row,'runAfter':{'Read_page':['Succeeded']},'runtimeConfiguration':{'concurrency':{'repetitions':1}}},
        'Page_failed':gate("@not(equals(actions('Process_rows')?['status'],'Succeeded'))",{'Page_failed_flag':setvar('Batch_failed',True)},after={'Process_rows':['Succeeded','Failed','TimedOut']}),
        'Next_link':compose("@coalesce(body('Read_page')?['@odata.nextLink'],body('Read_page')?['odata.nextLink'],'')",{'Page_failed':['Succeeded']}),
        'Next_page_scope':gate("@or(empty(outputs('Next_link')),startsWith(outputs('Next_link'),'"+literal(site+'/'+reg+'?')+"'),startsWith(outputs('Next_link'),'"+literal(site+'/'+reg.replace(chr(39),'%27')+'?')+"'))",{}, {'Bad_next_link':reject('NEXT_PAGE_SCOPE_MISMATCH')},{'Next_link':['Succeeded']}),
        'Set_next_uri':setvar('Next_uri',"@if(empty(outputs('Next_link')),'',substring(outputs('Next_link'),"+str(len(site)+1)+"))",{'Next_page_scope':['Succeeded']}),
        'Page_count':{'type':'IncrementVariable','inputs':{'name':'Pages','value':1},'runAfter':{'Set_next_uri':['Succeeded']}},
    }
    def initialize(name,kind,value,after=None):
        return {'type':'InitializeVariable','inputs':{'variables':[{'name':name,'type':kind,'value':value}]},'runAfter':after or {}}
    definition={
        '$schema':manual['properties']['definition']['$schema'],'contentVersion':'1.0.0.0',
        'parameters':{'$authentication':{'type':'SecureObject','defaultValue':{}},'$connections':{'type':'Object','defaultValue':{}},
                      'LinkEnabled':{'type':'Bool','defaultValue':False},'AutomationEnabled':{'type':'Bool','defaultValue':False},
                      'VersionDatesUtcQualified':{'type':'Bool','defaultValue':bool(config.get('version_dates_utc_qualified',False))},
                      'Max_pages':{'type':'Int','defaultValue':max_pages}},
        'triggers':{'recurrence':{'type':'Recurrence','recurrence':{'frequency':'Minute','interval':15},'runtimeConfiguration':{'concurrency':{'runs':1,'maximumWaitingRuns':1}}}},
        'actions':{'Initialize':initialize('Task_id','string',''),
                   'Initialize_next_uri':initialize('Next_uri','string',first_uri,{'Initialize':['Succeeded']}),
                   'Initialize_pages':initialize('Pages','integer',0,{'Initialize_next_uri':['Succeeded']}),
                   'Initialize_batch_failed':initialize('Batch_failed','boolean',False,{'Initialize_pages':['Succeeded']}),
                   'Worker_enabled':gate("@and(equals(parameters('AutomationEnabled'),true),equals(parameters('LinkEnabled'),true))",{}, {'Disabled':{'type':'Terminate','inputs':{'runStatus':'Cancelled'}}},{'Initialize_batch_failed':['Succeeded']}),
                   'Scan_pages':{'type':'Until','expression':"@or(empty(variables('Next_uri')),greaterOrEquals(variables('Pages'),parameters('Max_pages')))",'limit':{'count':max_pages,'timeout':'PT1H'},'actions':page,'runAfter':{'Worker_enabled':['Succeeded']}},
                   'Scan_complete':gate("@and(empty(variables('Next_uri')),equals(variables('Batch_failed'),false))",{'Cycle_complete':compose('Bounded scan complete; task snapshots only; correspondence closure remains manual.')}, {'Incomplete_scan':{'type':'Terminate','inputs':{'runStatus':'Failed','runError':{'code':'INCOMPLETE_OR_FAILED_SCAN','message':'Inspect exact item/operation; preserve links and human edits. No blind create retry.'}}}},{'Scan_pages':['Succeeded']})},
        'outputs':{},
    }
    return {'properties':{'displayName':'Executive correspondence | Automatic linked actions and status','state':'Stopped','definition':definition,'connectionReferences':deepcopy(manual['properties']['connectionReferences'])}}
