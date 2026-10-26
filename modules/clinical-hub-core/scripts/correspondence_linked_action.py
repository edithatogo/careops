"""Compile an explicit one-task-per-reviewed-record Standard Planner action flow.

Local source compiler only; deployment and runtime require exact native readback.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations
from typing import Any
import re
from urllib.parse import urlparse, urlsplit, urlunsplit, quote
from scripts.correspondence_capture import GUID, SHAREPOINT

PLANNER = '/providers/Microsoft.PowerApps/apis/shared_planner'
FIELDS = {'key': 'PlannerActionKey', 'id': 'PlannerTaskId', 'url': 'PlannerTaskUrl', 'state': 'PlannerLinkState'}


def build(config: dict[str, Any]) -> dict[str, Any]:
    """Build disabled/manual source, preserving business fields and task edits."""
    site = config['site_url']; parsed = urlparse(site)
    if parsed.scheme != 'https' or not parsed.hostname or not parsed.hostname.endswith('.sharepoint.com') or parsed.username or parsed.query or parsed.fragment:
        raise ValueError('Exact HTTPS SharePoint site required')
    for name in ('register_list_id', 'tenant_id', 'planner_container_id'):
        if not GUID.fullmatch(config[name]): raise ValueError('Pinned GUID required')
    for name in ('planner_plan_id', 'planner_bucket_id', 'planner_connection', 'sharepoint_connection'):
        if not isinstance(config.get(name), str) or not config[name]: raise ValueError('Pinned existing Planner/SharePoint bindings required')
    for name in ('planner_plan_id', 'planner_bucket_id'):
        if not re.fullmatch(r'[A-Za-z0-9_-]{28}', config[name]): raise ValueError('Exact Basic plan/bucket identity required')
    form = config['record_form_url']
    if urlparse(form).scheme != 'https' or urlparse(form).hostname != parsed.hostname or urlparse(form).query or urlparse(form).fragment or "'" in form:
        raise ValueError('Exact native same-host display form required')
    form_parts = urlsplit(form)
    form = urlunsplit((form_parts.scheme, form_parts.netloc, quote(form_parts.path, safe='/%'), '', ''))
    fields = {**FIELDS, **config.get('fields', {})}
    if any(not v.replace('_', '').isalnum() for v in fields.values()): raise ValueError('Native field identifiers required')
    reg = "_api/web/lists(guid'" + config['register_list_id'] + "')/items"
    reg_literal = reg.replace("'", "''")
    secure = {'secureData': {'properties': ['inputs', 'outputs']}}
    def comp(value, after=None):
        return {'type':'Compose', 'inputs':value, 'runAfter':after or {}, 'runtimeConfiguration':{'secureData':{'properties':['inputs']}}}
    def fail(code, after=None):
        return {'type':'Terminate','inputs':{'runStatus':'Failed','runError':{'code':code,'message':'Inspect existing record/task by stable key; no blind create retry or correspondence closure.'}},'runAfter':after or {}}
    def sp(method, uri, *, body=None, etag=None, after=None, verbose=False):
        headers={'Accept':'application/json;odata=verbose' if verbose else 'application/json;odata=nometadata'}
        params={'dataset':site,'parameters/method':method,'parameters/uri':uri,'parameters/headers':headers}
        if body is not None: params['parameters/body']='@string('+body+')' if isinstance(body,str) else body;headers['Content-Type']='application/json;odata=nometadata'
        if etag: headers.update({'IF-MATCH':etag,'X-HTTP-Method':'MERGE'})
        return {'type':'OpenApiConnection','inputs':{'host':{'apiId':SHAREPOINT,'connectionName':'shared_sharepointonline','operationId':'HttpRequest'},'parameters':params,'retryPolicy':{'type':'none'}},'runAfter':after or {},'runtimeConfiguration':secure}
    def planner(op, params, after=None):
        return {'type':'OpenApiConnection','inputs':{'host':{'apiId':PLANNER,'connectionName':'shared_planner','operationId':op},'parameters':params,'retryPolicy':{'type':'none'}},'runAfter':after or {},'runtimeConfiguration':secure}
    def set_task(value, after=None):
        return {'type':'SetVariable','inputs':{'name':'Task_id','value':value},'runAfter':after or {}}
    def task_filter(source):
        return {'type':'Query','inputs':{'from':source,'where':"@startsWith(coalesce(item()?['title'],''),concat('[',outputs('Action_key'),'] '))"},'runAfter':{},'runtimeConfiguration':secure}
    def list_tasks(after=None):
        return planner('ListTasks_V3',{'groupId':config['planner_container_id'],'id':config['planner_plan_id']},after)
    selected = "@concat('"+reg_literal+"(',string(triggerBody()?['ItemId']),')?$select=Id,CaptureState,"+','.join(fields.values())+"')"
    fresh = "@concat('"+reg_literal+"(',string(triggerBody()?['ItemId']),')?$select=Id,"+','.join(fields.values())+"')"
    item_uri = "@concat('"+reg_literal+"(',string(triggerBody()?['ItemId']),')')"
    create={
        'Claim_body':comp({fields['key']:"@outputs('Action_key')",fields['state']:'Creating'}),
        'Claim_record':sp('POST',item_uri,body="outputs('Claim_body')",etag="@outputs('Item')?['__metadata']?['etag']",after={'Claim_body':['Succeeded']}),
        'Create_task':planner('CreateTask_V3',{'body/groupId':config['planner_container_id'],'body/planId':config['planner_plan_id'],'body/bucketId':config['planner_bucket_id'],'body/title':"@concat('[',outputs('Action_key'),'] ',trim(triggerBody()?['ActionTitle']))"},{'Claim_record':['Succeeded']}),
        'Created_id':set_task("@body('Create_task')?['id']",{'Create_task':['Succeeded']}),
        'Reconcile_create':list_tasks({'Create_task':['Failed','TimedOut']}),
        'Filter_reconciled':task_filter("@body('Reconcile_create')?['value']"),
        'Reconciled_id':{'type':'If','expression':"@and(empty(body('Reconcile_create')?['@odata.nextLink']),equals(length(body('Filter_reconciled')),1))",'runAfter':{'Filter_reconciled':['Succeeded']},'actions':{'Recovered_id':set_task("@first(body('Filter_reconciled'))?['id']")},'else':{'actions':{'No_blind_retry':fail('TASK_CREATE_UNCERTAIN')}}},
    }
    create['Filter_reconciled']['runAfter']={'Reconcile_create':['Succeeded']}
    route={'type':'If','expression':"@not(empty(outputs('Item')?['"+fields['id']+"']))",'actions':{'Existing_id':set_task("@outputs('Item')?['"+fields['id']+"']")},'else':{'actions':{'Match_count':{'type':'If','expression':"@equals(length(body('Filter_tasks')),1)",'actions':{'Matched_id':set_task("@first(body('Filter_tasks'))?['id']")},'else':{'actions':{'May_create':{'type':'If','expression':"@and(equals(length(body('Filter_tasks')),0),empty(outputs('Item')?['"+fields['state']+"']),empty(outputs('Item')?['"+fields['key']+"']),not(empty(outputs('Item')?['__metadata']?['etag'])))",'actions':create,'else':{'actions':{'Ambiguous_or_pending':fail('TASK_LINK_REQUIRES_RECONCILIATION')}}}}}}}}}
    bind={
        'Read_task':planner('GetTask_V2',{'id':"@variables('Task_id')"}),
        'Task_scope':{'type':'If','expression':"@equals(body('Read_task')?['planId'],'"+config['planner_plan_id']+"')",'runAfter':{'Read_task':['Succeeded']},'actions':{},'else':{'actions':{'Wrong_plan':fail('TASK_PLAN_MISMATCH')}}},
        'Read_details':planner('GetTaskDetails_V2',{'id':"@variables('Task_id')"},{'Task_scope':['Succeeded']}),
        'Existing_backlinks':{'type':'Query','inputs':{'from':"@coalesce(body('Read_details')?['references'],json('[]'))",'where':"@equals(replace(coalesce(item()?['resourceLink'],''),' ','%20'),outputs('Record_url'))"},'runAfter':{'Read_details':['Succeeded']},'runtimeConfiguration':secure},
        'Task_identity':{'type':'If','expression':"@or(startsWith(coalesce(body('Read_task')?['title'],''),concat('[',outputs('Action_key'),'] ')),greater(length(body('Existing_backlinks')),0))",'runAfter':{'Existing_backlinks':['Succeeded']},'actions':{},'else':{'actions':{'Wrong_record':fail('TASK_RECORD_IDENTITY_MISMATCH')}}},
        'Backlink_present':{'type':'If','expression':"@greater(length(body('Existing_backlinks')),0)",'runAfter':{'Task_identity':['Succeeded']},'actions':{'Keep_human_details':comp('Existing backlink retained; no task rewrite')},'else':{'actions':{'Save_backlink':planner('UpdateTaskDetails_V2',{'id':"@variables('Task_id')",'body/references':[{'alias':'Correspondence record','resourceLink':"@outputs('Record_url')"}]})}}},
        'Verify_details':planner('GetTaskDetails_V2',{'id':"@variables('Task_id')"},{'Backlink_present':['Succeeded']}),
        'Verified_backlinks':{'type':'Query','inputs':{'from':"@coalesce(body('Verify_details')?['references'],json('[]'))",'where':"@equals(replace(coalesce(item()?['resourceLink'],''),' ','%20'),outputs('Record_url'))"},'runAfter':{'Verify_details':['Succeeded']},'runtimeConfiguration':secure},
        'Backlink_verified':{'type':'If','expression':"@equals(length(body('Verified_backlinks')),1)",'runAfter':{'Verified_backlinks':['Succeeded']},'actions':{},'else':{'actions':{'Missing_backlink':fail('TASK_BACKLINK_UNVERIFIED')}}},
        'Read_latest_item':sp('GET',fresh,verbose=True,after={'Backlink_verified':['Succeeded']}),
        'Latest_item':comp("@body('Read_latest_item')?['d']",{'Read_latest_item':['Succeeded']}),
        'No_link_conflict':{'type':'If','expression':"@and(or(empty(outputs('Latest_item')?['"+fields['id']+"']),equals(outputs('Latest_item')?['"+fields['id']+"'],variables('Task_id'))),or(empty(outputs('Latest_item')?['"+fields['key']+"']),equals(outputs('Latest_item')?['"+fields['key']+"'],outputs('Action_key'))),not(empty(outputs('Latest_item')?['__metadata']?['etag'])))",'runAfter':{'Latest_item':['Succeeded']},'actions':{},'else':{'actions':{'Link_conflict':fail('CORRESPONDENCE_LINK_CONFLICT')}}},
        'Link_body':comp({fields['key']:"@outputs('Action_key')",fields['id']:"@variables('Task_id')",fields['url']:{'Url':"@concat('https://planner.cloud.microsoft/ui/web/plan/"+config['planner_plan_id']+"/view/board/task/',variables('Task_id'),'?tid="+config['tenant_id']+"')",'Description':'Linked Planner action'},fields['state']:'Linked'},{'No_link_conflict':['Succeeded']}),
        'Save_register_link':sp('POST',item_uri,body="outputs('Link_body')",etag="@outputs('Latest_item')?['__metadata']?['etag']",after={'Link_body':['Succeeded']}),
        'Read_persisted':sp('GET',fresh,verbose=True,after={'Save_register_link':['Succeeded']}),
        'Persisted_link_verified':{'type':'If','expression':"@and(equals(body('Read_persisted')?['d']?['"+fields['id']+"'],variables('Task_id')),equals(body('Read_persisted')?['d']?['"+fields['state']+"'],'Linked'),equals(body('Read_persisted')?['d']?['"+fields['key']+"'],outputs('Action_key')))",'runAfter':{'Read_persisted':['Succeeded']},'actions':{'Linked':comp('Reciprocal selected action linked; correspondence status and human fields unchanged')},'else':{'actions':{'Link_save_unverified':fail('LINK_SAVE_UNVERIFIED')}}},
    }
    actions={
        'Init_task_id':{'type':'InitializeVariable','inputs':{'variables':[{'name':'Task_id','type':'string','value':''}]}},
        'Validate_request':{'type':'If','expression':"@and(equals(parameters('LinkEnabled'),true),greater(int(coalesce(triggerBody()?['ItemId'],0)),0),greater(length(trim(coalesce(triggerBody()?['ActionTitle'],''))),0),lessOrEquals(length(trim(coalesce(triggerBody()?['ActionTitle'],''))),120))",'runAfter':{'Init_task_id':['Succeeded']},'actions':{},'else':{'actions':{'Invalid_request':fail('EXPLICIT_ACTION_REQUIRED')}}},
        'Read_item':sp('GET',selected,verbose=True,after={'Validate_request':['Succeeded']}),
        'Item':comp("@body('Read_item')?['d']",{'Read_item':['Succeeded']}),
        'Reviewed_record':{'type':'If','expression':"@equals(outputs('Item')?['CaptureState'],'Reviewed')",'runAfter':{'Item':['Succeeded']},'actions':{},'else':{'actions':{'Not_reviewed':fail('REVIEW_REQUIRED')}}},
        'Action_key':comp("@concat('COR-"+config['register_list_id']+"-',string(triggerBody()?['ItemId']))",{'Reviewed_record':['Succeeded']}),
        'Link_scope':{'type':'If','expression':"@or(and(empty(outputs('Item')?['"+fields['key']+"']),empty(outputs('Item')?['"+fields['id']+"'])),equals(outputs('Item')?['"+fields['key']+"'],outputs('Action_key')))",'runAfter':{'Action_key':['Succeeded']},'actions':{},'else':{'actions':{'Inconsistent_link':fail('LINK_IDENTITY_CONFLICT')}}},
        'Record_url':comp("@concat('"+form+"?ID=',string(triggerBody()?['ItemId']))",{'Link_scope':['Succeeded']}),
        'List_tasks':list_tasks({'Record_url':['Succeeded']}),
        'Complete_plan_scan':{'type':'If','expression':"@empty(body('List_tasks')?['@odata.nextLink'])",'runAfter':{'List_tasks':['Succeeded']},'actions':{},'else':{'actions':{'Incomplete_plan_scan':fail('PLAN_SCAN_INCOMPLETE')}}},
        'Filter_tasks':task_filter("@body('List_tasks')?['value']"),
        'Task_route':{**route,'runAfter':{'Filter_tasks':['Succeeded']}},
        'Have_task_id':{'type':'If','expression':"@not(empty(variables('Task_id')))",'runAfter':{'Task_route':['Succeeded','Failed','TimedOut']},'actions':bind,'else':{'actions':{'Task_unresolved':fail('TASK_UNRESOLVED')}}},
    }
    actions['Filter_tasks']['runAfter']={'Complete_plan_scan':['Succeeded']}
    definition={'$schema':'https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#','contentVersion':'1.0.0.0','parameters':{'$authentication':{'type':'SecureObject','defaultValue':{}},'$connections':{'type':'Object','defaultValue':{}},'LinkEnabled':{'type':'Bool','defaultValue':False}},'triggers':{'manual':{'type':'Request','kind':'Button','inputs':{'schema':{'type':'object','properties':{'ItemId':{'type':'integer','minimum':1,'title':'Reviewed correspondence item ID'},'ActionTitle':{'type':'string','minLength':1,'maxLength':120,'title':'Selected action title'}},'required':['ItemId','ActionTitle']}},'runtimeConfiguration':{'concurrency':{'runs':1},'secureData':{'properties':['inputs','outputs']}}}},'actions':actions,'outputs':{}}
    refs={key:{'connectionName':config[name],'source':'Embedded','id':api} for key,name,api in [('shared_planner','planner_connection',PLANNER),('shared_sharepointonline','sharepoint_connection',SHAREPOINT)]}
    return {'properties':{'displayName':'Executive correspondence | Create linked action','state':'Stopped','definition':definition,'connectionReferences':refs}}
