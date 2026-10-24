"""Compile the maintained F06 template once for Standard Office Script execution.

No tenant calls or per-meeting population. Cloud source selection stays in F06.
"""
from __future__ import annotations
import argparse, base64, hashlib, json, re, zipfile
from pathlib import Path
from lxml import etree as E


def compile_template(path: Path, sections: list[str]) -> dict:
    from build_word_documents import F06_TEMPLATE_FIELDS
    if len(sections) != 7 or any(not isinstance(s,str) or not s.strip() for s in sections):
        raise ValueError('Seven maintained sections required')
    with zipfile.ZipFile(path) as z:
        infos=z.infolist()
        if z.testzip() or len(infos)>100 or len({i.filename.lower() for i in infos})!=len(infos) or sum(i.file_size for i in infos)>2000000:
            raise ValueError('Template package outside qualified bounds')
        parts=[{'path':i.filename,'base64':base64.b64encode(z.read(i)).decode(),'sha256':hashlib.sha256(z.read(i)).hexdigest()} for i in sorted(infos,key=lambda i:i.filename)]
        root=E.fromstring(z.read('word/document.xml'));ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'};seen=[]
        for control in root.xpath('//w:sdt',namespaces=ns):
            tag=control.find('w:sdtPr/w:tag',ns).get('{'+ns['w']+'}val');seen.append(tag)
            if tag not in F06_TEMPLATE_FIELDS or control.find('w:sdtPr/w:dataBinding',ns) is not None or control.getparent().tag!='{'+ns['w']+'}body':
                raise ValueError('Only maintained block controls without live bindings are supported')
            content=control.find('w:sdtContent',ns);content.clear();content.append(E.Comment('F06_VALUE:'+tag))
        if len(seen)!=22 or set(seen)!=set(F06_TEMPLATE_FIELDS):raise ValueError('Maintained22-control shape changed')
    xml=E.tostring(root,encoding='unicode')
    t={'kind':'F06-word-template-v1','templateSHA256':hashlib.sha256(path.read_bytes()).hexdigest(),'mainXml':xml,'sections':sections,'parts':parts}
    pin='\n'.join(p['path']+':'+p['sha256'] for p in parts)+'\n'+hashlib.sha256(xml.encode()).hexdigest()+'\n'+hashlib.sha256(json.dumps(sections,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()+'\n'+t['templateSHA256']
    t['manifestPin']=hashlib.sha256(pin.encode()).hexdigest()
    return t


if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('template',type=Path);a.add_argument('section_contract',type=Path);a.add_argument('output',type=Path);v=a.parse_args()
    data=json.loads(v.section_contract.read_text());values=data['values'];t=compile_template(v.template,[values[f'AgendaSection{i}'] for i in range(1,8)])
    with v.output.open('x') as f:json.dump(t,f,ensure_ascii=False,separators=(',',':'))
    print('Compiled22controls; rawparts',sum(len(base64.b64decode(p['base64'])) for p in t['parts']),'manifestPin',t['manifestPin'])
