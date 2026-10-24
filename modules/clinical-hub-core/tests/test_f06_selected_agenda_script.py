"""Execute the Office Script locally over synthetic template parts, without APIs.

The fixture pin replaces only the production manifest constant in this isolated
VM. It does not qualify the native template, connectors or cloud source reads.
"""
import base64
from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import zipfile

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/f06_agenda_document.ts'
PRODUCTION_PIN = '3f6f6523035aca6c942d48ac230af2883d1db1eb113e521c1aeca963c6e0a1ea'
NODE = r"""
const fs=require('node:fs'),vm=require('node:vm');
const {stripTypeScriptTypes}=require('node:module');
const input=JSON.parse(fs.readFileSync(0,'utf8'));
let source=fs.readFileSync(input.script,'utf8');
source=source.replace(input.productionPin,input.template.manifestPin);
const context=vm.createContext({});
vm.runInContext(stripTypeScriptTypes(source),context,{timeout:20000});
const workbook=new Proxy({}, {get(){throw Error('workbook access forbidden');}});
try {const result=context.main(workbook,JSON.stringify(input.job),JSON.stringify(input.template));
 process.stdout.write(JSON.stringify({result}));}
catch(error){process.stdout.write(JSON.stringify({error:String(error.message)}));}
"""


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'))


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def template():
    fields = ['MeetingID', 'MeetingDateTime', 'DraftRevision', 'OccurrenceScope',
              'PaperLink', 'PaperIdentity', 'SourceHistory']
    fields += [f'AgendaSection{i}' for i in range(1, 8)]
    fields += [f'ReviewHold{i}' for i in range(1, 4)]
    fields += ['SourceLink', 'SourceProvenance', 'TemplateProvenance', 'RunProvenance', 'OptionalContent']
    blocks = []
    for field in fields:
        if field.startswith('ReviewHold'):
            blocks.append(f'<w:p><w:r><w:t>Review hold {field[-1]}</w:t></w:r></w:p>')
        blocks.append(f'<w:sdt><w:sdtPr><w:tag w:val="{field}"/><w:text/></w:sdtPr>'
                      f'<w:sdtContent><!--F06_VALUE:{field}--></w:sdtContent></w:sdt>')
    xml = ('<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
           'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
           '<w:body>' + ''.join(blocks) + '</w:body></w:document>')
    raw = {'[Content_Types].xml': '<Types/>', 'word/document.xml': xml,
           'word/_rels/document.xml.rels': '<Relationships/>'}
    # Explicit closing tag mirrors the maintained package's relationship part.
    raw['word/_rels/document.xml.rels'] = '<Relationships></Relationships>'
    parts = [dict(path=k, base64=base64.b64encode(v.encode()).decode(), sha256=digest(v))
             for k, v in sorted(raw.items())]
    sections = [f'Maintained section {i}' for i in range(1, 8)]
    t = dict(kind='F06-word-template-v1', templateSHA256=digest('synthetic template'),
             mainXml=xml, sections=sections, parts=parts)
    pin = '\n'.join(p['path'] + ':' + p['sha256'] for p in parts)
    pin += '\n' + digest(xml) + '\n' + digest(compact(sections)) + '\n' + t['templateSHA256']
    t['manifestPin'] = digest(pin)
    return t


def link(label, identity, host='fictional-example.sharepoint.com'):
    return dict(label=label, id=identity, version='2.0', url=f'https://{host}/selected/{identity}')


def selection(count=4):
    return dict(schemaVersion=2, meeting_id='SELECTED-OCCURRENCE-OTHER', meeting_date='2031-03-10',
                timezone='Australia/Brisbane', calendar=link('Selected calendar', 'EVENT-B', 'outlook.office.com'),
                calendarStart='2031-03-10T16:00:00+10:00', calendarEnd='2031-03-10T17:00:00+10:00',
                source=link('Selected source', 'SOURCE-B'), source_revision='SELECTED-R7',
                source_modified='2031-03-08T00:00:00Z', scope='FICTIONAL technical selection only.',
                synthetic_only=True, sections=[f'Sourced section {i}' for i in range(1, 8)],
                history=['Original minutes and corrections preserved'],
                papers=[link('Paper A & B', 'PAPER-A'), link('Second paper', 'PAPER-B')],
                minutes=[link('Prior minutes', 'MINUTES-A')], records=[
                    dict(record_id=f'ORIGINAL-{i}', status='awaiting review', source_text=f'Unchanged source <{i}> & dissent.',
                         history=[f'Prior/{i}', f'Correction/{i}'], owner_claim=None, due_date=None,
                         due_label='Original label retained', review_date=None, response_ref=None)
                    for i in range(count)])


def run(s=None, *, t=None, job_override=None):
    s = selection() if s is None else s
    job = dict(kind='clinical-agenda-selected-word-v2', selectionJson=compact(s), meetingDate=s['meeting_date'],
               occurrence=s['meeting_id'], outputRevision=4, sourceVersion='2.0', sourceModified=s['source_modified'],
               flowId='LOCAL-TEST', runId='LOCAL-TEST-RUN', createdAt='2031-03-08T00:00:00Z',
               templateUniqueId='SYNTHETIC-TEMPLATE', templateVersion='1.0')
    job.update(job_override or {})
    payload = dict(script=str(SCRIPT), productionPin=PRODUCTION_PIN, template=t or template(), job=job)
    result = subprocess.run(['node', '-e', NODE], input=compact(payload), text=True, capture_output=True, timeout=30)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


@pytest.mark.parametrize('count', [0, 1, 3, 4, 20])
def test_selected_other_occurrence_preserves_all_records_and_native_links(count):
    s = selection(count); before = deepcopy(s)
    out = run(s)['result']
    assert s == before
    assert out['schemaVersion'] == 2 and out['includedRecordIDs'] == [r['record_id'] for r in s['records']]
    assert out['wordGenerationPerformed'] and not out['sourceWrites'] and not out['sent']
    data = base64.b64decode(out['docxBase64'])
    assert len(data) == out['bytes'] and hashlib.sha256(data).hexdigest() == out['sha256']
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        assert z.testzip() is None
        xml = z.read('word/document.xml')
        body = ''.join(ET.fromstring(xml).itertext())
        assert s['meeting_id'] in body and s['meeting_date'] in body
        assert all(v in body for v in s['sections'])
        for r in s['records']:
            assert r['record_id'] in body and r['source_text'] in body
            assert all(h in body for h in r['history'])
        assert 'Review hold 2' not in body and 'Review hold 3' not in body
        assert b'<!--F06_' not in xml and b'<w:text' not in xml
        targets = [e.get('Target') for e in ET.fromstring(z.read('word/_rels/document.xml.rels'))]
        assert targets == [r['url'] for r in [*s['papers'], s['source'], s['calendar'], *s['minutes']]]
        assert 'SYN-CYCLE-01' not in body and 'SYN-A01' not in body


def test_no_papers_or_minutes_does_not_invent_any():
    s = selection(0); s.update(papers=[], minutes=[])
    out = run(s)['result']
    with zipfile.ZipFile(io.BytesIO(base64.b64decode(out['docxBase64']))) as z:
        body = ''.join(ET.fromstring(z.read('word/document.xml')).itertext())
        assert 'No paper selected' in body and 'No source records selected' in body
        assert len(list(ET.fromstring(z.read('word/_rels/document.xml.rels')))) == 2


def test_preserves_both_native_due_value_and_original_human_label():
    s = selection(1)
    s['records'][0].update(due_date='2031-03-20T00:00:00Z', due_label='Original: after next review')
    out = run(s)['result']
    with zipfile.ZipFile(io.BytesIO(base64.b64decode(out['docxBase64']))) as z:
        text = ''.join(ET.fromstring(z.read('word/document.xml')).itertext())
        assert '2031-03-20T00:00:00Z' in text and 'Original: after next review' in text


def test_native_register_record_link_is_a_real_hyperlink_in_output():
    s = selection(1)
    s['records'][0]['source_link'] = link('Register record ORIGINAL-0', 'NATIVE-ROW-ID')
    out = run(s)['result']
    with zipfile.ZipFile(io.BytesIO(base64.b64decode(out['docxBase64']))) as z:
        targets = [e.get('Target') for e in ET.fromstring(z.read('word/_rels/document.xml.rels'))]
        assert s['records'][0]['source_link']['url'] in targets


@pytest.mark.parametrize('changes', [dict(occurrence='WRONG'), dict(meetingDate='2031-03-11'),
                                     dict(sourceVersion='STALE'), dict(sourceModified='STALE'),
                                     dict(outputRevision=0), dict(outputRevision=1000)])
def test_rejects_identity_or_version_mismatch(changes):
    assert run(job_override=changes)['error'] == 'selected_identity_invalid'


@pytest.mark.parametrize('mutate', [
    lambda s: s.update(calendarStart='2031-03-11T16:00:00+10:00'),
    lambda s: s.update(calendarStart='2031-03-10T16:00:00'),
    lambda s: s.update(calendarEnd=s['calendarStart']),
    lambda s: s['papers'][0].update(url='https://fictional-example.sharepoint.com.evil.invalid/paper'),
    lambda s: s['papers'][0].update(version=''),
    lambda s: s['calendar'].update(url='https://fictional-example.sharepoint.com/not-a-calendar'),
    lambda s: s['records'].append(deepcopy(s['records'][0])),
    lambda s: s.update(sections=s['sections'][:6]),
])
def test_rejects_changed_calendar_links_duplicate_records_and_incomplete_sections(mutate):
    s = selection(); mutate(s)
    assert 'error' in run(s)


def test_template_part_tampering_fails_closed():
    t = template(); t['parts'][0]['base64'] = base64.b64encode(b'changed').decode()
    assert run(t=t)['error'] == 'template_part_changed'


def test_invalid_calendar_day_and_illegal_xml_fail_closed():
    s = selection(); s['meeting_date'] = '2031-02-30'
    assert run(s)['error'] == 'selected_date_invalid'
    s = selection(); s['records'][0]['source_text'] = 'unsafe\x00text'
    assert run(s)['error'] == 'text_invalid'
