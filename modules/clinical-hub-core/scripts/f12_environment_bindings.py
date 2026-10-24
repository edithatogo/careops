"""Pure F12 environment-binding preparation; native Object consumption unproven."""
from copy import deepcopy
from xml.etree import ElementTree as ET

VARIABLES = {
    'comeet_F12Baseline': ('F12 accepted metadata baseline', 'Accepted event and agenda metadata with baseline provenance. Supply separately; no source default.'),
    'comeet_F12Selection': ('F12 metadata selection', 'Calendar window, subject, organizer and issued attachment selector. Supply separately; no source default.'),
}


def bind_environment_metadata(definition):
    result = deepcopy(definition)
    parameters = result['parameters']
    for schema, (display, description) in VARIABLES.items():
        if parameters.get(schema) != {'type': 'Object', 'defaultValue': {}}:
            raise ValueError('configuration: expected unbound empty Object parameter')
        friendly = f'{display} ({schema})'
        if friendly in parameters:
            raise ValueError('configuration: duplicate environment binding')
        del parameters[schema]
        parameters[friendly] = {'type':'Object', 'defaultValue':{},
                                'metadata':{'schemaName':schema,'description':description}}

    def rewrite(value):
        if isinstance(value,dict):return {k:rewrite(v) for k,v in value.items()}
        if isinstance(value,list):return [rewrite(v) for v in value]
        if isinstance(value,str):
            for schema,(display,_) in VARIABLES.items():
                value=value.replace(f"parameters('{schema}')",f"parameters('{display} ({schema})')")
        return value
    return rewrite(result)


def environment_definition(schema):
    """Use the existing exported F06 XML shape, with documented JSON type code."""
    display,description=VARIABLES[schema]
    root=ET.Element('environmentvariabledefinition',{'schemaname':schema})
    for tag,text in [('description',description),('displayname',display)]:
        child=ET.SubElement(root,tag,{'default':text})
        ET.SubElement(child,'label',{'description':text,'languagecode':'1033'})
    for tag,value in [('introducedversion','1.0.0.0'),('iscustomizable','1'),('isrequired','0'),('secretstore','0'),('type','100000003')]:
        ET.SubElement(root,tag).text=value
    ET.indent(root,space='  ')
    return ET.tostring(root,encoding='unicode')+'\n'
