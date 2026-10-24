"""Prepare F06's native selected-source branch; no APIs or hosted Python runtime.

The versioned library selection file stores references, not a replacement action
register. Calendar and linked files are read and rechecked in Power Automate.
The caller must qualify the existing library folder and script mapping.
"""
from __future__ import annotations

import copy
import uuid


SITE = "@parameters('F06 source site URL (comeet_F06SourceSiteUrl)')"
PREFIX = 'Selected_'


def build_selected_agenda(baseline: dict, *, register_list_id: str,
                          outlook_reference: dict, script_id: str,
                          script_unique_id: str, script_version: str,
                          script_bytes: int, selection_folder_path: str = '/Shared Documents') -> dict:
    """Return a candidate for the same stopped F06, retaining its legacy route.

    New Word occurrences read ``F06-selection-<base64url occurrence>.json`` from
    the existing library. Its content follows SelectedAgenda v2. Native file metadata
    replaces its source pointer/version; no user-supplied qualification flag is
    accepted. Saving the candidate is separate from its native commissioning.

    registerSelection contains list_id and rows, each with native_row_id,
    native_guid, native_version and legacy_id. These are selection pins only:
    records is replaced by actual F05 reads. This branch never writes a register,
    changes a calendar, issues an action or decides that a source is approved.
    """
    if (not isinstance(selection_folder_path, str) or not selection_folder_path.startswith('/')
            or any(c in selection_folder_path for c in "'\\\r\n?#")
            or any(p in ('', '.', '..') for p in selection_folder_path[1:].split('/'))):
        raise ValueError('Qualified existing site-relative selection folder required')
    register_list_id = str(uuid.UUID(register_list_id))
    script_unique_id = str(uuid.UUID(script_unique_id))
    if (not script_id or not isinstance(script_version, str) or not script_version
            or type(script_bytes) is not int or script_bytes < 1):
        raise ValueError('Qualified new native script identity/version/size required')
    # Native Flow RP returns flat references; retained solution snapshots may
    # use the nested form. Preserve the supplied, qualified shape unchanged.
    flat = outlook_reference.get('id') == '/providers/Microsoft.PowerApps/apis/shared_office365'
    nested = outlook_reference.get('api', {}).get('name') == 'shared_office365'
    if not (flat or nested):
        raise ValueError('Reuse the qualified F12 Outlook reference')
    logical = (outlook_reference.get('connectionReferenceLogicalName') if flat else
               outlook_reference.get('connection', {}).get('connectionReferenceLogicalName'))
    if not logical:
        raise ValueError('Saved logical Outlook reference required')
    result = copy.deepcopy(baseline)
    props = result['properties']; definition = props['definition']; root = definition['actions']
    if 'Selected_occurrence_adapter' in root or 'Fictional_successor_adapter' not in root:
        raise ValueError('Unexpected F06 baseline; reconcile before preparing a candidate')
    if root['Fictional_successor_adapter']['runAfter'] != {'Check_trigger_inputs': ['Succeeded']}:
        raise ValueError('Existing F06 execution order changed')
    if set(props['connectionReferences']) != {'shared_sharepointonline', 'shared_excelonlinebusiness'}:
        raise ValueError('Unexpected F06 connection bindings')

    def find(name):
        matches = []
        def visit(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    if key == name and isinstance(child, dict) and 'type' in child:
                        matches.append(child)
                    visit(child)
            elif isinstance(value, list):
                for child in value: visit(child)
        visit(root)
        if len(matches) != 1:
            raise ValueError(f'Exact qualified donor action required: {name}')
        donor = matches[0]
        operations = {'Read_word_template_pin': 'HttpRequest',
                      'Read_word_template_parts': 'GetFileContentByPath',
                      'Run_maintained_document_script': 'RunScriptProdV2',
                      'Stage_word_binary': 'CreateFile',
                      'Move_word_stage_without_overwrite': 'HttpRequest'}
        if name in operations and (donor.get('type') != 'OpenApiConnection' or
                donor.get('inputs', {}).get('host', {}).get('operationId') != operations[name]):
            raise ValueError(f'Qualified donor operation changed: {name}')
        if name == 'Move_word_stage_without_overwrite':
            params = donor['inputs']['parameters']
            if params.get('parameters/method') != 'POST' or ',flags=0)' not in params.get('parameters/uri', ''):
                raise ValueError('Atomic no-overwrite donor required')
        return copy.deepcopy(donor)

    def sp(uri, after, *, operation='HttpRequest'):
        params = {'dataset': SITE, 'parameters/method': 'GET', 'parameters/uri': uri,
                  'parameters/headers': {'Accept': 'application/json;odata=nometadata'}}
        return {'type': 'OpenApiConnection', 'runAfter': after, 'inputs': {
            'host': {'apiId': '/providers/Microsoft.PowerApps/apis/shared_sharepointonline',
                     'connectionName': 'shared_sharepointonline', 'operationId': operation},
            'parameters': params, 'authentication': "@parameters('$authentication')",
            'retryPolicy': {'type': 'none'}}}

    def outlook(uri, after):
        return {'type': 'OpenApiConnection', 'runAfter': after, 'inputs': {
            'host': {'apiId': '/providers/Microsoft.PowerApps/apis/shared_office365',
                     'connectionName': 'shared_office365', 'operationId': 'HttpRequest'},
            'parameters': {'Method': 'GET', 'Uri': uri,
                           'CustomHeader1': 'Prefer: outlook.timezone="UTC"'},
            'authentication': "@parameters('$authentication')", 'retryPolicy': {'type': 'none'}}}

    def stop(code):
        return {'type': 'Terminate', 'runAfter': {}, 'inputs': {'runStatus': 'Failed',
                'runError': {'code': code, 'message': 'Selected native source, calendar, linked file or asset changed/missing. No overwrite; reconcile the exact run and existing files before retry.'}}}

    def guard(name, condition, after):
        return {'type': 'If', 'runAfter': after, 'expression': condition, 'actions': {},
                'else': {'actions': {name + '_refusal': stop(name.upper())}}}

    def done(name): return {name: ['Succeeded']}

    a = {}
    a['Selected_selection_path'] = {'type': 'Compose', 'runAfter': {}, 'inputs':
        "@concat('" + selection_folder_path + "/F06-selection-',replace(replace(replace(base64(triggerBody()?['text_1']),'+','-'),'/','_'),'=',''),'.json')"}
    source_uri = ("@concat('_api/web/GetFileByServerRelativePath(decodedurl=''',uriPath(parameters('F06 source site URL (comeet_F06SourceSiteUrl)')),"
                  "outputs('Selected_selection_path'),''')?$select=UniqueId,Name,UIVersionLabel,TimeLastModified,Length,ServerRelativeUrl,ETag')")
    a['Selected_read_source'] = sp(source_uri, done('Selected_selection_path'))
    a['Selected_source_row'] = {'type': 'Compose', 'runAfter': done('Selected_read_source'),
                                'inputs': "@body('Selected_read_source')"}
    a['Selected_read_source_body'] = find('Read_word_template_parts')
    a['Selected_read_source_body']['runAfter'] = done('Selected_source_row')
    a['Selected_read_source_body']['inputs']['parameters']['path'] = "@outputs('Selected_selection_path')"
    a['Selected_parse_source'] = {'type': 'Compose', 'runAfter': done('Selected_read_source_body'),
                                 'inputs': "@json(string(body('Selected_read_source_body')))"}
    a['Selected_require_identity'] = guard('Selected_require_identity',
        "@and(equals(outputs('Selected_parse_source')?['schemaVersion'],2),"
        "equals(outputs('Selected_parse_source')?['meeting_id'],triggerBody()?['text_1']),"
        "equals(outputs('Selected_parse_source')?['meeting_date'],outputs('Confirm_meeting_date')),"
        "equals(outputs('Selected_parse_source')?['synthetic_only'],triggerBody()?['boolean']),"
        "not(empty(outputs('Selected_parse_source')?['source_revision'])),"
        "not(empty(outputs('Selected_source_row')?['UniqueId'])),"
        "equals(outputs('Selected_parse_source')?['registerSelection']?['list_id'],'" + register_list_id + "'),"
        "lessOrEquals(length(outputs('Selected_parse_source')?['registerSelection']?['rows']),100),"
        "equals(length(outputs('Selected_parse_source')?['sections']),7),"
        "lessOrEquals(length(outputs('Selected_parse_source')?['records']),100),"
        "lessOrEquals(length(outputs('Selected_parse_source')?['papers']),100),"
        "lessOrEquals(length(outputs('Selected_parse_source')?['minutes']),20))",
        done('Selected_parse_source'))
    event_uri = ("@concat('https://graph.microsoft.com/v1.0/me/events/',"
                 "uriComponent(outputs('Selected_parse_source')?['calendar']?['id']),"
                 "'?$select=id,subject,start,end,isCancelled,changeKey,webLink')")
    a['Selected_read_calendar'] = outlook(event_uri, done('Selected_require_identity'))
    calendar_check = (
        "and(equals(body('Selected_read_calendar')?['id'],outputs('Selected_parse_source')?['calendar']?['id']),"
        "equals(body('Selected_read_calendar')?['subject'],outputs('Selected_parse_source')?['calendar']?['label']),"
        "equals(body('Selected_read_calendar')?['changeKey'],outputs('Selected_parse_source')?['calendar']?['version']),"
        "not(empty(body('Selected_read_calendar')?['webLink'])),"
        "or(empty(outputs('Selected_parse_source')?['calendar']?['url']),equals(body('Selected_read_calendar')?['webLink'],outputs('Selected_parse_source')?['calendar']?['url'])),"
        "equals(body('Selected_read_calendar')?['isCancelled'],false),"
        "equals(body('Selected_read_calendar')?['start']?['timeZone'],'UTC'),"
        "equals(body('Selected_read_calendar')?['end']?['timeZone'],'UTC'),"
        "equals(ticks(concat(body('Selected_read_calendar')?['start']?['dateTime'],'Z')),ticks(outputs('Selected_parse_source')?['calendarStart'])),"
        "equals(ticks(concat(body('Selected_read_calendar')?['end']?['dateTime'],'Z')),ticks(outputs('Selected_parse_source')?['calendarEnd'])))")
    a['Selected_guard_calendar'] = guard('Selected_guard_calendar', '@' + calendar_check,
                                          done('Selected_read_calendar'))

    # The actual F05 fields were read from the existing list. Selection carries
    # only row identities/versions; record wording comes from these native GETs,
    # not from a copied status, proposed outcome or caller qualification flag.
    a['Selected_register_metadata'] = sp("_api/web/lists(guid'" + register_list_id +
        "')?$select=Id,Title,EnableVersioning", done('Selected_guard_calendar'))
    a['Selected_guard_register_metadata'] = guard('Selected_guard_register_metadata',
        "@and(equals(toLower(body('Selected_register_metadata')?['Id']),'" + register_list_id +
        "'),equals(body('Selected_register_metadata')?['EnableVersioning'],true))", done('Selected_register_metadata'))

    # The Standard SharePoint connector removes null-valued JSON properties,
    # including explicitly selected fields. Validate schema independently so a
    # genuine missing field is refused while an empty value stays null.
    schema_fields = ['ID', 'GUID', 'Title', 'LegacyactionID', 'Sourcereference',
                     'Currentstatus', 'Sourcehistory', 'Recordedrole_x2014_unverified',
                     'Duedate', 'Originalduelabel', 'Reviewdate', 'Commissioningclassification',
                     'Issuereadiness', 'Originmeetingdate', 'Closurereviewstate',
                     'Acceptedclosuredate', '_UIVersionString']
    a['Selected_register_schema'] = sp("_api/web/lists(guid'" + register_list_id +
        "')/fields?$select=InternalName", done('Selected_guard_register_metadata'))
    a['Selected_register_field_names'] = {'type': 'Select',
        'runAfter': done('Selected_register_schema'), 'inputs': {
            'from': "@body('Selected_register_schema')?['value']",
            'select': {'name': "@item()?['InternalName']"}}}
    schema_condition = '@and(' + ','.join(
        "contains(body('Selected_register_field_names'),json('{\"name\":\"" + field + "\"}'))"
        for field in schema_fields) + ')'
    a['Selected_guard_register_schema'] = guard('Selected_guard_register_schema',
        schema_condition, done('Selected_register_field_names'))

    def register_pass(prefix, after, *, collect):
        read = prefix + '_read'; match = prefix + '_match'
        uri = ("@concat('_api/web/lists(guid''" + register_list_id +
               "'')/items(',string(int(items('" + prefix + "')?['native_row_id'])),')')")
        condition = ("@and(equals(body('" + read + "')?['Id'],int(items('" + prefix + "')?['native_row_id'])),"
            "equals(toLower(body('" + read + "')?['GUID']),toLower(items('" + prefix + "')?['native_guid'])),"
            "equals(body('" + read + "')?['OData__UIVersionString'],items('" + prefix + "')?['native_version']),"
            "equals(body('" + read + "')?['LegacyactionID'],items('" + prefix + "')?['legacy_id']),"
            "not(empty(body('" + read + "')?['LegacyactionID'])))")
        fields = ['Id', 'GUID', 'Title', 'LegacyactionID', 'Sourcereference',
                  'Currentstatus', 'Sourcehistory', 'Recordedrole_x2014_unverified',
                  'Duedate', 'Originalduelabel', 'Reviewdate', 'Commissioningclassification',
                  'Issuereadiness', 'Originmeetingdate', 'Closurereviewstate',
                  'Acceptedclosuredate', 'OData__UIVersionString']
        # SharePoint omits empty custom fields from the default item projection.
        # Explicit selection preserves nulls and distinguishes them from schema drift.
        uri = uri[:-1] + ",'?$select=" + ','.join(fields) + "')"
        yes = {}
        if collect:
            body = "body('" + read + "')"
            def field(name): return '@' + body + "?['" + name + "']"
            def note(name): return "coalesce(" + body + "?['" + name + "'],'not recorded')"
            text = "@concat('Register title (reviewed summary, not verbatim minutes): '," + note('Title')
            for label, name in [('Original source reference', 'Sourcereference'),
                                ('Commissioning classification', 'Commissioningclassification'),
                                ('Issue readiness', 'Issuereadiness'), ('Origin meeting date', 'Originmeetingdate'),
                                ('Closure review state', 'Closurereviewstate'), ('Accepted closure date', 'Acceptedclosuredate')]:
                text += ",decodeUriComponent('%0A'),'" + label + ": ',string(" + note(name) + ')'
            text += ",decodeUriComponent('%0A'),'Generation does not commission, issue, close or change this register record.')"
            record = {'record_id': field('LegacyactionID'),
                'status': "@coalesce(" + body + "?['Currentstatus'],'Unknown — not assessed')",
                'source_text': text,
                'history': "@if(empty(" + body + "?['Sourcehistory']),json('[]'),createArray(" + body + "?['Sourcehistory']))",
                'owner_claim': field('Recordedrole_x2014_unverified'), 'due_date': field('Duedate'),
                'due_label': field('Originalduelabel'), 'review_date': field('Reviewdate'), 'response_ref': None,
                'source_link': {'label': "@concat('Register record '," + body + "?['LegacyactionID'])",
                    'id': field('GUID'), 'version': field('OData__UIVersionString'),
                    'url': "@concat(parameters('F06 source site URL (comeet_F06SourceSiteUrl)'),"
                           "'/_layouts/15/listform.aspx?PageType=4&ListId=" + register_list_id +
                           "&ID=',string(" + body + "?['Id']))"}}
            yes[match + '_collect'] = {'type': 'AppendToArrayVariable', 'runAfter': {},
                'inputs': {'name': 'SelectedRegisterRecords', 'value': record}}
        return {'type': 'Foreach', 'runAfter': after,
            'foreach': "@outputs('Selected_parse_source')?['registerSelection']?['rows']",
            'runtimeConfiguration': {'concurrency': {'repetitions': 1}},
            'actions': {read: sp(uri, {}), match: {'type': 'If', 'runAfter': done(read),
                'expression': condition, 'actions': yes, 'else': {'actions': {match + '_changed': {
                    'type': 'AppendToArrayVariable', 'runAfter': {},
                    'inputs': {'name': 'SelectedSourceErrors', 'value': 'Register identity/version changed'}}}}}}}

    a['Selected_register_initial'] = register_pass('Selected_register_initial', done('Selected_guard_register_schema'), collect=True)
    a['Selected_guard_register_initial'] = guard('Selected_guard_register_initial',
        "@equals(length(variables('SelectedSourceErrors')),0)", done('Selected_register_initial'))

    # Two passes bound the metadata used by the script and the later commit.
    # A failed read leaves this path failed, never turns into a missing-source
    # success or a write against a different resource.
    def file_pass(prefix, after):
        read_name = prefix + '_read'; check_name = prefix + '_check'
        uri = ("@concat('_api/web/GetFileById(''',items('" + prefix +
               "')?['id'],''')?$select=UniqueId,Name,UIVersionLabel,ServerRelativeUrl')")
        check = ("@and(equals(toLower(body('" + read_name + "')?['UniqueId']),toLower(items('" + prefix + "')?['id'])),"
                 "equals(body('" + read_name + "')?['UIVersionLabel'],items('" + prefix + "')?['version']),"
                 "equals(body('" + read_name + "')?['Name'],items('" + prefix + "')?['label']),"
                 "or(equals(items('" + prefix + "')?['url'],concat(parameters('F06 source site URL (comeet_F06SourceSiteUrl)'),"
                 "'/_layouts/15/Doc.aspx?sourcedoc=%7B',toUpper(body('" + read_name + "')?['UniqueId']),'%7D')),"
                 "equals(items('" + prefix + "')?['url'],concat(parameters('F06 source site URL (comeet_F06SourceSiteUrl)'),"
                 "'/_layouts/15/Doc.aspx?sourcedoc=%7B',toUpper(body('" + read_name + "')?['UniqueId']),'%7D&action=view'))))")
        # Terminate is not supported inside Apply to each; append a failure and
        # evaluate the aggregate only after the loop.
        check_action = {'type': 'If', 'runAfter': done(read_name), 'expression': check,
                        'actions': {}, 'else': {'actions': {check_name + '_record': {
                            'type': 'AppendToArrayVariable', 'runAfter': {},
                            'inputs': {'name': 'SelectedSourceErrors', 'value': '@items(\'' + prefix + '\')?[\'id\']'}}}}}
        item_id = "string(items('" + prefix + "')?['id'])"
        residual = 'toLower(' + item_id + ')'
        for char in '0123456789abcdef-':
            residual = "replace(" + residual + ", '" + char + "', '')"
        guid_check = ('@and(equals(length(' + item_id + '),36),'
                      "equals(length(replace(" + item_id + ",'-','')),32),equals(length(" + residual + '),0),')
        guid_check += ','.join("equals(substring(" + item_id + ',' + str(i) + ",1),'-')"
                               for i in (8, 13, 18, 23)) + ')'
        validate = {'type': 'If', 'runAfter': {}, 'expression': guid_check,
                    'actions': {read_name: sp(uri, {}), check_name: check_action},
                    'else': {'actions': {prefix + '_invalid_id': {
                        'type': 'AppendToArrayVariable', 'runAfter': {},
                        'inputs': {'name': 'SelectedSourceErrors', 'value': 'Invalid selected native file GUID'}}}}}
        return {'type': 'Foreach', 'runAfter': after,
                'foreach': "@union(outputs('Selected_parse_source')?['papers'],outputs('Selected_parse_source')?['minutes'])",
                'runtimeConfiguration': {'concurrency': {'repetitions': 1}},
                'actions': {prefix + '_validate_id': validate}}

    a['Selected_files_initial'] = file_pass('Selected_files_initial', done('Selected_guard_register_initial'))
    a['Selected_guard_files_initial'] = guard('Selected_guard_files_initial',
        "@equals(length(variables('SelectedSourceErrors')),0)", done('Selected_files_initial'))
    a['Selected_template_pin'] = find('Read_word_template_pin')
    a['Selected_template_pin']['runAfter'] = done('Selected_guard_files_initial')
    a['Selected_script_pin'] = sp("_api/web/GetFileById('" + script_unique_id +
        "')?$select=UniqueId,UIVersionLabel,Length", done('Selected_template_pin'))
    template_guard = find('Guard_word_assets')['expression']['and'][:3]
    template_guard = [copy.deepcopy(v) for v in template_guard]
    for v in template_guard:
        v['equals'][0] = v['equals'][0].replace('Read_word_template_pin', 'Selected_template_pin')
    a['Selected_guard_assets'] = guard('Selected_guard_assets', {'and': template_guard + [
        {'equals': ["@toLower(body('Selected_script_pin')?['UniqueId'])", script_unique_id]},
        {'equals': ["@body('Selected_script_pin')?['UIVersionLabel']", script_version]},
        {'equals': ["@string(body('Selected_script_pin')?['Length'])", str(script_bytes)]}]}, done('Selected_script_pin'))
    a['Selected_template_parts'] = find('Read_word_template_parts')
    a['Selected_template_parts']['runAfter'] = done('Selected_guard_assets')
    source_pointer = {'label': "@concat('Selected source for ',triggerBody()?['text_1'])",
        'id': "@outputs('Selected_source_row')?['UniqueId']",
        'version': "@outputs('Selected_source_row')?['UIVersionLabel']",
        'url': "@concat('https://',uriHost(parameters('F06 source site URL (comeet_F06SourceSiteUrl)')),replace(uriComponent(outputs('Selected_source_row')?['ServerRelativeUrl']),'%2F','/'))"}
    a['Selected_source_pointer'] = {'type': 'Compose', 'runAfter': done('Selected_template_parts'),
                                   'inputs': source_pointer}
    a['Selected_contract'] = {'type': 'Compose', 'runAfter': done('Selected_source_pointer'),
        'inputs': "@setProperty(setProperty(setProperty(setProperty(outputs('Selected_parse_source'),'source',outputs('Selected_source_pointer')),'source_modified',outputs('Selected_source_row')?['TimeLastModified']),'records',variables('SelectedRegisterRecords')),'calendar',setProperty(outputs('Selected_parse_source')?['calendar'],'url',body('Selected_read_calendar')?['webLink']))"}
    a['Selected_word_job'] = {'type': 'Compose', 'runAfter': done('Selected_contract'), 'inputs': {
        'kind': 'clinical-agenda-selected-word-v2', 'selectionJson': "@string(outputs('Selected_contract'))",
        'meetingDate': "@outputs('Confirm_meeting_date')", 'occurrence': "@triggerBody()?['text_1']",
        'outputRevision': "@coalesce(triggerBody()?['number'],1)",
        'sourceVersion': "@outputs('Selected_source_row')?['UIVersionLabel']",
        'sourceModified': "@outputs('Selected_source_row')?['TimeLastModified']",
        'flowId': "@workflow()?['name']", 'runId': "@workflow()?['run']?['name']", 'createdAt': '@utcNow()',
        'templateUniqueId': "@body('Selected_template_pin')?['UniqueId']",
        'templateVersion': "@body('Selected_template_pin')?['UIVersionLabel']"}}
    run = find('Run_maintained_document_script'); run['runAfter'] = done('Selected_word_job')
    run['inputs']['parameters'].update(scriptId=script_id,
        **{'ScriptParameters/jobJson': "@string(outputs('Selected_word_job'))",
           'ScriptParameters/membersJson': "@string(body('Selected_template_parts'))"})
    a['Selected_run_script'] = run
    a['Selected_reread_source'] = sp(source_uri, done('Selected_run_script'))
    a['Selected_guard_source'] = guard('Selected_guard_source',
        "@and(equals(body('Selected_reread_source')?['UniqueId'],outputs('Selected_source_row')?['UniqueId']),"
        "equals(body('Selected_reread_source')?['TimeLastModified'],outputs('Selected_source_row')?['TimeLastModified']),"
        "equals(body('Selected_reread_source')?['ETag'],outputs('Selected_source_row')?['ETag']),"
        "equals(body('Selected_reread_source')?['Length'],outputs('Selected_source_row')?['Length']),"
        "equals(body('Selected_reread_source')?['UIVersionLabel'],outputs('Selected_source_row')?['UIVersionLabel']),"
        "equals(body('Selected_run_script')?['result']?['wordGenerationPerformed'],true),"
        "equals(body('Selected_run_script')?['result']?['sourceWrites'],false),"
        "equals(body('Selected_run_script')?['result']?['sent'],false))", done('Selected_reread_source'))
    a['Selected_reread_calendar'] = outlook(event_uri, done('Selected_guard_source'))
    a['Selected_guard_calendar_final'] = guard('Selected_guard_calendar_final',
        '@and(' + calendar_check.replace('Selected_read_calendar', 'Selected_reread_calendar') + ",equals(body('Selected_reread_calendar')?['webLink'],body('Selected_read_calendar')?['webLink']))", done('Selected_reread_calendar'))
    a['Selected_files_final'] = file_pass('Selected_files_final', done('Selected_guard_calendar_final'))
    a['Selected_guard_files_final'] = guard('Selected_guard_files_final',
        "@equals(length(variables('SelectedSourceErrors')),0)", done('Selected_files_final'))
    a['Selected_register_final'] = register_pass('Selected_register_final', done('Selected_guard_files_final'), collect=False)
    a['Selected_guard_register_final'] = guard('Selected_guard_register_final',
        "@equals(length(variables('SelectedSourceErrors')),0)", done('Selected_register_final'))
    a['Selected_template_final'] = copy.deepcopy(a['Selected_template_pin'])
    a['Selected_template_final']['runAfter'] = done('Selected_guard_register_final')
    a['Selected_script_final'] = copy.deepcopy(a['Selected_script_pin'])
    a['Selected_script_final']['runAfter'] = done('Selected_template_final')
    final_assets = []
    for initial, final in [('Selected_template_pin', 'Selected_template_final'),
                           ('Selected_script_pin', 'Selected_script_final')]:
        for field in ['UniqueId', 'UIVersionLabel', 'Length']:
            final_assets.append({'equals': ["@string(body('" + initial + "')?['" + field + "'])",
                                           "@string(body('" + final + "')?['" + field + "'])"]})
    a['Selected_guard_assets_final'] = guard('Selected_guard_assets_final',
        {'and': final_assets}, done('Selected_script_final'))
    a['Selected_word_name'] = {'type': 'Compose', 'runAfter': done('Selected_guard_assets_final'),
        'inputs': "@concat('F06-',outputs('Confirm_meeting_date'),'-',replace(replace(replace(base64(triggerBody()?['text_1']),'+','-'),'/','_'),'=',''),'-R',string(coalesce(triggerBody()?['number'],1)),'-WORD.docx')"}
    stage = find('Stage_word_binary'); stage['runAfter'] = done('Selected_word_name')
    stage['inputs']['parameters']['body'] = "@base64ToBinary(body('Selected_run_script')?['result']?['docxBase64'])"
    a['Selected_stage_word'] = stage
    move = find('Move_word_stage_without_overwrite'); move['runAfter'] = done('Selected_stage_word')
    move['inputs']['parameters']['parameters/uri'] = move['inputs']['parameters']['parameters/uri'].replace('Word_output_name', 'Selected_word_name')
    a['Selected_commit_word'] = move
    a['Selected_stage_uncertain'] = stop('AGENDA_OUTPUT_RECONCILE')
    a['Selected_stage_uncertain']['runAfter'] = {'Selected_stage_word': ['Failed', 'TimedOut']}
    a['Selected_uncertain_output'] = stop('AGENDA_OUTPUT_RECONCILE')
    a['Selected_uncertain_output']['runAfter'] = {'Selected_commit_word': ['Failed', 'TimedOut']}
    a['Selected_finish'] = {'type': 'Terminate', 'runAfter': done('Selected_commit_word'), 'inputs': {'runStatus': 'Succeeded'}}
    props['connectionReferences']['shared_office365'] = copy.deepcopy(outlook_reference)
    root['Selected_initialise_errors'] = {'type': 'InitializeVariable', 'runAfter': done('Check_trigger_inputs'),
        'inputs': {'variables': [{'name': 'SelectedSourceErrors', 'type': 'array', 'value': []}]}}
    root['Selected_initialise_register'] = {'type': 'InitializeVariable', 'runAfter': done('Selected_initialise_errors'),
        'inputs': {'variables': [{'name': 'SelectedRegisterRecords', 'type': 'array', 'value': []}]}}
    root['Selected_occurrence_adapter'] = {'type': 'If', 'runAfter': done('Selected_initialise_register'),
        'expression': "@and(equals(toLower(coalesce(triggerBody()?['text_2'],'')),'word'),not(equals(triggerBody()?['text_1'],'SYN-CYCLE-01-NEXT-2030-02-18')))",
        'actions': a, 'else': {'actions': {}}}
    root['Fictional_successor_adapter']['runAfter'] = done('Selected_occurrence_adapter')
    definition['triggers']['manual']['inputs']['schema']['properties']['text_2']['description'] = (
        'Word uses the versioned selected occurrence/source record and native calendar/paper/minutes checks. '
        'The retained historical fictional occurrence keeps its qualified legacy route. Blank uses Markdown.')
    return result
