"""Prepare F07 native operator choices; execution stays in Power Automate."""
from copy import deepcopy
from urllib.parse import urlparse


def build_operator_inputs(clientdata, *, site, path, name, version, etag, paper_ref):
    if (urlparse(site).scheme != 'https' or
            not (urlparse(site).hostname or '').endswith('.sharepoint.com') or
            not path.startswith('/') or any(not x for x in (name, version, etag, paper_ref))):
        raise ValueError('Qualified site, exact path and observed document identity/version required')
    result = deepcopy(clientdata)
    definition = result['properties']['definition']
    actions = definition['actions']
    guard = actions['Check_manifest_input']
    compare = 'Compare with observed version ' + version
    definition['triggers']['manual']['inputs']['schema'] = {
        'type': 'object', 'required': ['Paper', 'Version'], 'properties': {
            'Paper': {'type': 'string', 'title': 'Paper', 'enum': [name],
                      'description': 'Selected existing paper; no copy or distribution.'},
            'Version': {'type': 'string', 'title': 'Version check',
                        'enum': [compare, 'Version not confirmed'],
                        'description': 'Metadata comparison only. Meeting association and substantive review remain separate.'}}}
    actions['Selected_manifest'] = {
        'type': 'Compose', 'runAfter': {'Initialize_expected_count': ['Succeeded']},
        'inputs': [{'PaperRef': paper_ref, 'SourcePath': path, 'ReviewedETag': etag}]}
    guard['runAfter'] = {'Selected_manifest': ['Succeeded']}
    guard['expression'] = {'and': [
        {'equals': ["@triggerBody()?['Paper']", name]},
        {'equals': ["@triggerBody()?['Version']", compare]}]}
    guard['else']['actions']['Stop_missing_manifest_input']['inputs']['runError'] = {
        'code': 'VERSION_NOT_CONFIRMED',
        'message': 'Select the configured paper and observed version before checking its link.'}
    guard['actions']['Parse_manifest']['inputs']['content'] = "@outputs('Selected_manifest')"
    inner = guard['actions']['Check_unique_identifiers']['actions']
    binding = inner['For_each_paper']['actions']['Check_paper_binding']
    # The legacy Team-folder prefix cannot qualify a selected personal source.
    # Restrict this commissioning graph to the one configured exact path.
    binding['expression'] = {'and': [
        {'equals': ["@items('For_each_paper')?['PaperRef']", paper_ref]},
        {'equals': ["@items('For_each_paper')?['SourcePath']", path]},
        {'equals': ["@items('For_each_paper')?['ReviewedETag']", etag]}]}
    paper = binding['actions']
    paper['Get_paper_metadata']['inputs']['parameters']['dataset'] = site
    checks = paper['Check_reviewed_etag']
    for append in (checks['actions']['Append_match'], checks['else']['actions']['Append_review_drift']):
        append['inputs']['value']['source_url'] = (
            "@concat('" + site.replace("'", "''") +
            "',replace(uriComponent(items('For_each_paper')?['SourcePath']),'%2F','/'))")
    summary = inner['Manifest_results']['inputs']
    summary['meeting_ref'] = 'Not confirmed; document check only'
    summary['selected_document'] = name
    summary['version_compared'] = version
    summary['next_step'] = 'Open the source link, check readability and suitability, and associate it with the selected meeting. A version match does not approve a paper or complete a pack.'
    return result


def build_paper_preflight(clientdata, *, declared_meeting_date):
    """Add human checks without treating supplied confirmations as native proof."""
    from datetime import date
    if date.fromisoformat(declared_meeting_date).isoformat() != declared_meeting_date:
        raise ValueError('Bind the document-declared date explicitly')
    result = deepcopy(clientdata)
    definition = result['properties']['definition']
    schema = definition['triggers']['manual']['inputs']['schema']['properties']
    choices = {
        'PaperFormat': ('Paper format', ['Brief', 'Report', 'Slides', 'Not confirmed']),
        'Readability': ('Readability', ['Readable', 'Not checked or unreadable']),
        'Content': ('Content and audience', ['Suitable for existing audience', 'Restricted route needed or not checked']),
        'Review': ('Source review', ['Reviewed this source and version', 'Review not confirmed']),
        'MeetingConfirmation': ('Meeting association', ['Confirmed for selected meeting', 'Not confirmed'])}
    for key, (title, options) in choices.items():
        schema[key] = {'type': 'string', 'title': title, 'enum': options,
                       'description': 'Operator confirmation; unknown leaves an exception.'}
    schema['Pages'] = {'type': 'string', 'title': 'Pages or slides',
                       'enum': ['Not checked', '1', '2', '3', '4 or more'],
                       'description': 'Choose the count you checked. Brief 1, report 2, slides 3 maximum.'}
    schema['MeetingDate'] = {'type': 'string', 'title': 'Selected meeting',
                             'enum': ['Not confirmed', declared_meeting_date, 'Another meeting'],
                             'description': 'The source paper states ' + declared_meeting_date + '; confirm the actual selected occurrence separately.'}
    # Native manual-input controls use explicit required choices. Unknown is a
    # real choice and default, never an implicit positive confirmation.
    for key, default in {'PaperFormat': 'Not confirmed',
            'Readability': 'Not checked or unreadable',
            'Content': 'Restricted route needed or not checked',
            'Review': 'Review not confirmed', 'MeetingConfirmation': 'Not confirmed',
            'Pages': 'Not checked', 'MeetingDate': 'Not confirmed'}.items():
        schema[key]['default'] = default
    definition['triggers']['manual']['inputs']['schema']['required'] = list(schema)
    inner = definition['actions']['Check_manifest_input']['actions']['Check_unique_identifiers']['actions']
    source = inner['Manifest_results']
    source['inputs']['next_step'] = 'Read the Paper preflight and Operator result actions. Confirmations are supplied by the operator; paper approval and circulation remain separate.'

    def compose(inputs, after):
        return {'type': 'Compose', 'inputs': inputs, 'runAfter': {after: ['Succeeded']}}

    def claim(field, default='Not confirmed'):
        return "coalesce(triggerBody()?['" + field + "'],'" + default + "')"

    count = "if(equals(" + claim('Pages', 'Not checked') + ",'1'),1,if(equals(" + claim('Pages', 'Not checked') + ",'2'),2,if(equals(" + claim('Pages', 'Not checked') + ",'3'),3,if(equals(" + claim('Pages', 'Not checked') + ",'4 or more'),4,0))))"

    checks = [
        ("not(contains(createArray('Brief','Report','Slides')," + claim('PaperFormat') + "))", 'FORMAT_UNKNOWN', 'Confirm whether this is a brief, report or slides.'),
        ("lessOrEquals(" + count + ",0)", 'LENGTH_UNKNOWN', 'Check the page or slide count.'),
        ("greater(" + count + ",if(equals(" + claim('PaperFormat') + ",'Brief'),1,if(equals(" + claim('PaperFormat') + ",'Report'),2,3)))", 'PAGE_LIMIT_EXCEEDED', 'Paper exceeds the selected format limit; narrow the decision or revise the source using readable text.'),
        ("not(equals(" + claim('Readability') + ",'Readable'))", 'READABILITY_UNCONFIRMED', 'Open the source and check readable text and references.'),
        ("not(equals(" + claim('Content') + ",'Suitable for existing audience'))", 'RESTRICTED_CONTENT_UNRESOLVED', 'Confirm source and audience suitability or use the authorised restricted route.'),
        ("not(equals(" + claim('Review') + ",'Reviewed this source and version'))", 'REVIEW_UNCONFIRMED', 'Review the exact linked source and compared version.'),
        ("or(not(equals(" + claim('MeetingConfirmation') + ",'Confirmed for selected meeting')),empty(coalesce(triggerBody()?['MeetingDate'],'')),equals(" + claim('MeetingDate') + ",'Not confirmed'))", 'MEETING_UNCONFIRMED', 'Confirm the actual selected meeting and paper association.'),
        ("and(not(empty(coalesce(triggerBody()?['MeetingDate'],''))),not(equals(" + claim('MeetingDate') + ",'Not confirmed')),not(equals(coalesce(triggerBody()?['MeetingDate'],''),'" + declared_meeting_date + "')))", 'WRONG_MEETING', 'Selected meeting differs from the date stated in this source paper; resolve the association.')]
    inner['Human_checks'] = compose({
        'evidence_kind': 'OPERATOR_SUPPLIED_NOT_INDEPENDENTLY_VERIFIED',
        'declared_document_meeting_date': declared_meeting_date,
        **{key: "@" + claim(key) for key in choices},
        'Pages': '@' + count, 'Pages_supplied': '@' + claim('Pages', 'Not checked'),
        'MeetingDate': "@coalesce(triggerBody()?['MeetingDate'],'')"}, 'Manifest_results')
    inner['Paper_exception_candidates'] = compose([
        {'code': "@if(" + condition + ",'" + code + "','')", 'detail': detail}
        for condition, code, detail in checks], 'Human_checks')
    inner['Paper_checks_requiring_attention'] = {
        'type': 'Query', 'inputs': {'from': "@outputs('Paper_exception_candidates')", 'where': "@not(empty(item()?['code']))"},
        'runAfter': {'Paper_exception_candidates': ['Succeeded']}}
    inner['Metadata_exceptions'] = {
        'type': 'Query', 'inputs': {'from': "@outputs('Manifest_results')?['results']", 'where': "@not(equals(item()?['code'],'METADATA_MATCH'))"},
        'runAfter': {'Paper_checks_requiring_attention': ['Succeeded']}}
    ready = "and(empty(body('Metadata_exceptions')),empty(body('Paper_checks_requiring_attention')),equals(outputs('Manifest_results')?['result_complete'],true))"
    inner['Paper_preflight'] = compose({
        'status': "@if(" + ready + ",'READY_FOR_MANUAL_REVIEW','EXCEPTIONS_REQUIRE_REVIEW')",
        'ready_for_manual_review': '@' + ready,
        'paper_readiness': False, 'meeting_source_verified': False,
        'human_checks': "@outputs('Human_checks')", 'source_results': "@outputs('Manifest_results')?['results']",
        'exceptions': "@union(body('Metadata_exceptions'),body('Paper_checks_requiring_attention'))"}, 'Metadata_exceptions')
    inner['Exception_lines'] = {'type': 'Select', 'inputs': {
        'from': "@outputs('Paper_preflight')?['exceptions']",
        'select': "@coalesce(item()?['detail'],concat('Source check: ',item()?['code']))"},
        'runAfter': {'Paper_preflight': ['Succeeded']}}
    inner['Operator_result'] = compose(
        "@concat('Paper check: ',outputs('Manifest_results')?['selected_document'],decodeUriComponent('%0A'),'Status: ',outputs('Paper_preflight')?['status'],decodeUriComponent('%0A'),'Needs attention: ',if(empty(body('Exception_lines')),'None recorded; human pack review still required',join(body('Exception_lines'),'; ')),decodeUriComponent('%0A'),'Source: ',coalesce(first(outputs('Manifest_results')?['results'])?['source_url'],'No retrievable source link'),decodeUriComponent('%0A'),'Readability, count, suitability, review and meeting confirmations are supplied by the operator. No paper approval, circulation or complete-pack claim.')",
        'Exception_lines')
    return result
