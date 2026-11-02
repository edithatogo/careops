"""Package one cloud flow into the installation's existing unmanaged solution."""
import argparse
import copy
import json
from pathlib import Path
import uuid
import zipfile
from xml.etree import ElementTree as ET

from scripts.ppg_currency_cloud_flow import build


def package(export, seed_name, bindings, version, destination):
    seed_path = 'Workflows/' + seed_name
    if Path(seed_name).name != seed_name:
        raise ValueError('Select an exported workflow filename')
    with zipfile.ZipFile(export) as source:
        sol = ET.fromstring(source.read('solution.xml'))
        manifest = sol.find('SolutionManifest')
        if manifest.findtext('Managed') != '0':
            raise ValueError('Use an unmanaged authoring export')
        name = manifest.findtext('UniqueName')
        flow_id = str(uuid.uuid5(uuid.NAMESPACE_URL, 'PPGWorkbench/policy-currency/notice-evidence-review'))
        filename = 'Workflows/PPGPolicyCurrency-' + flow_id + '.json'
        manifest.find('Version').text = version
        roots = manifest.find('RootComponents')
        roots.clear()
        ET.SubElement(roots,'RootComponent', type='29', id='{'+flow_id+'}', behavior='0')
        manifest.find('MissingDependencies').clear()
        custom = ET.fromstring(source.read('customizations.xml'))
        entries = [w for w in custom.findall('Workflows/Workflow') if w.findtext('JsonFileName') == '/'+seed_path]
        if len(entries) != 1:
            raise ValueError(f'Expected exactly one seed workflow for {seed_name!r}')
        workflow = copy.deepcopy(entries[0])
        for child in custom:
            child.clear()
        title = 'PPG | Policy currency | Source evidence review and coverage'
        workflow.set('Name',title)
        workflow.set('WorkflowId','{'+flow_id+'}')
        workflow.find('JsonFileName').text = '/'+filename
        workflow.find('LocalizedNames/LocalizedName').set('description',title)
        workflow.find('StateCode').text = '0'
        workflow.find('StatusCode').text = '1'
        custom.find('Workflows').append(workflow)
        ET.SubElement(custom.find('Languages'),'Language').text='1033'
        definition=build(json.loads(source.read(seed_path)),bindings)
        with zipfile.ZipFile(destination,'x',zipfile.ZIP_DEFLATED) as out:
            for file,element in [('solution.xml',sol),('customizations.xml',custom)]:
                out.writestr(file,ET.tostring(element,encoding='utf-8',xml_declaration=True))
            out.writestr(filename,json.dumps(definition))
            out.writestr('[Content_Types].xml',source.read('[Content_Types].xml'))
    return name,flow_id


if __name__ == '__main__':
    cli=argparse.ArgumentParser(description=__doc__)
    for field in ('export','seed_name','bindings','version','destination'):
        cli.add_argument(field)
    a=cli.parse_args()
    if '.local' not in Path(a.destination).resolve().parts:
        cli.error('Use a private destination')
    print(*package(a.export,a.seed_name,json.loads(Path(a.bindings).read_text()),a.version,a.destination))
