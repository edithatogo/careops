import copy
import hashlib
import subprocess
import shutil
import tempfile
import unittest
from pathlib import Path
from scripts.ppg_image_witness import validate_image_witness


def fixture_pdf():
    objects = [b'<< /Type /Catalog /Pages 2 0 R >>',b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 200] /Contents 4 0 R >>',b'<< /Length 0 >>\nstream\n\nendstream']
    data=b'%PDF-1.4\n'; offsets=[0]
    for n,obj in enumerate(objects,1):
        offsets.append(len(data));data+=f'{n} 0 obj\n'.encode()+obj+b'\nendobj\n'
    xref=len(data);data+=f'xref\n0 {len(offsets)}\n0000000000 65535 f \n'.encode()
    data+=b''.join(f'{x:010} 00000 n \n'.encode() for x in offsets[1:]);data+=f'trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n'.encode();return data


def fixture():
    pdf=fixture_pdf();sha=lambda b:hashlib.sha256(b).hexdigest();exe=shutil.which('pdftoppm'); assert exe
    with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as d:
        p=Path(d);(p/'a.pdf').write_bytes(pdf);cmd=[exe,'-f','1','-l','1','-singlefile','-r','72','-png'];subprocess.run([*cmd,str(p/'a.pdf'),str(p/'page')],check=True,capture_output=True);subprocess.run([*cmd,'-x','5','-y','5','-W','30','-H','30',str(p/'a.pdf'),str(p/'crop')],check=True,capture_output=True)
        page=sha((p/'page.png').read_bytes());crop=sha((p/'crop.png').read_bytes())
    ver=subprocess.run([exe,'-v'],capture_output=True,check=True).stderr.decode().splitlines()[0]
    return pdf,dict(kind='pdf-visual-transcription-v1',pdfSHA256=sha(pdf),page=1,dpi=72,crop=dict(x=5,y=5,width=30,height=30),pageRenderSHA256=page,cropSHA256=crop,rendererVersion=ver,transcription='Fictional citation',reviewer=dict(method='direct-visual-review',identity='fictional reviewer',affirmedExactTranscription=True,reviewedAtUtc='2026-01-01T00:00:00Z'))

class WitnessTests(unittest.TestCase):
    def test_exact_qualified_witness(self):
        pdf,w=fixture();self.assertTrue(validate_image_witness(w,pdf))
    def test_missing_path_renderer_fails_closed(self):
        import os
        from unittest.mock import patch
        pdf,w=fixture()
        with patch.dict(os.environ, {'PATH': ''}), self.assertRaisesRegex(ValueError, 'unavailable on PATH'):
            validate_image_witness(w,pdf)
    def test_drift_and_unqualified_review_fail(self):
        pdf,w=fixture()
        for key,value in [('pdfSHA256','0'*64),('pageRenderSHA256','0'*64),('cropSHA256','0'*64),('rendererVersion','unknown'),('page',2),('transcription','')]:
            x=copy.deepcopy(w);x[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):validate_image_witness(x,pdf)
        for key,value in [('method','ocr'),('identity',''),('affirmedExactTranscription',False),('reviewedAtUtc','not-a-time')]:
            x=copy.deepcopy(w);x['reviewer'][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):validate_image_witness(x,pdf)
        x=copy.deepcopy(w);x['crop']['x']=199
        with self.assertRaises(ValueError):validate_image_witness(x,pdf)

class CompletionIntegrationTests(unittest.TestCase):
    def test_visual_link_must_bind_exact_witness_and_text_validation_is_preserved(self):
        import importlib.util, json, sys
        from unittest.mock import patch
        root=Path.cwd()
        sys.path.insert(0,str(root))
        spec=importlib.util.spec_from_file_location('staged_completion',root/'scripts/ppg_completed_relationship_assessment.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
        spec=importlib.util.spec_from_file_location('fictional_fixture',root/'tests/test_completed_relationship_assessment.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
        p=f.fixture(True);w={'transcription':'Fictional image'};entry=p['packet']['review']['endpointEvidence'][1];entry['passages']=[];entry['visualWitnesses']=[w]
        rel=p['relationships'][0];rel['EvidenceRef']=json.dumps({'target':{'imageWitnessSHA256':mod.digest(w),'quote':w['transcription']}});p['packet']['scope']['relationshipsSHA256']=mod.digest(mod.relationship_snapshot(p['relationships']))
        with patch.object(mod,'validate_image_witness',return_value=True):
            self.assertTrue(mod.prepare_completion(**p)['patch']['AssessmentComplete'])
            rel['EvidenceRef']=json.dumps({'target':{'imageWitnessSHA256':mod.digest(w),'quote':'wrong'}});p['packet']['scope']['relationshipsSHA256']=mod.digest(mod.relationship_snapshot(p['relationships']))
            with self.assertRaisesRegex(ValueError,'bind exact visual witness'):mod.prepare_completion(**p)
            entry['visualWitnesses']=[];entry['passages']=[{'start':0,'end':1,'quote':'wrong'}]
            with self.assertRaisesRegex(ValueError,'Passage offsets/text mismatch'):mod.prepare_completion(**p)

class CreateToCompletionTests(unittest.TestCase):
    def test_fictional_proposal_and_completion_end_to_end(self):
        import importlib.util, json, sys
        root=Path.cwd();stage=root/'scripts'
        sys.path.insert(0,str(root))
        spec=importlib.util.spec_from_file_location('staged_completion',stage/'ppg_completed_relationship_assessment.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
        spec=importlib.util.spec_from_file_location('fictional_fixture',root/'tests/test_completed_relationship_assessment.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
        spec=importlib.util.spec_from_file_location('staged_reference',stage/'ppg_image_reference.py');reference=importlib.util.module_from_spec(spec);spec.loader.exec_module(reference)
        p=f.fixture(True);pdf,w=fixture();w['transcription']='Fictional target procedure';sha=hashlib.sha256(pdf).hexdigest();version='retained-sha256:'+sha
        p['original_bytes']=pdf;source=p['endpoint_sources'][0];source.update(original_bytes=pdf,originalSHA256=sha,sourceVersion=version)
        p['packet']['source'].update(originalSHA256=sha,sourceVersion=version)
        manifest=json.loads(p['base']['EvidenceManifest']);manifest['sources'][0].update(originalSHA256=sha,sourceVersion=version);p['base']['EvidenceManifest']=json.dumps(manifest)
        entry=p['packet']['review']['endpointEvidence'][0];entry.update(originalSHA256=sha,sourceVersion=version,passages=[],visualWitnesses=[w])
        target=p['endpoint_sources'][1];proposal=reference.image_reference_proposal(source,target,w,'Fictional target procedure','Fictional exact identifier matches.',p['catalogue'])
        p['relationships']=[proposal];key=proposal['RelationshipKey'];review=p['packet']['review'];review['existingRelationshipDispositions'][0]['relationshipKey']=key
        for x in review['leadDispositions']:x['relationshipKeys']=[key]
        from scripts.ppg_catalogue_relationships import literal_leads
        leads=literal_leads(p['catalogue'],p['packet']['source']|{'text':p['text_bytes'].decode()})
        review['leadDispositions']=[dict(leadKey=mod.digest(l),disposition='linked-finding',relationshipKeys=[key],rationale='Fictional target evidence.') for l in leads]
        p['packet']['findingRelationshipKeys']=[key];p['packet']['scope']['relationshipsSHA256']=mod.digest(mod.relationship_snapshot(p['relationships']))
        self.assertTrue(mod.prepare_completion(**p)['patch']['AssessmentComplete'])
        broken=copy.deepcopy(w);broken['reviewer']['method']='ocr'
        with self.assertRaises(ValueError):reference.image_reference_proposal(source,target,broken,'Fictional target procedure','fictional',p['catalogue'])
        with self.assertRaises(ValueError):reference.image_reference_proposal(source,target,w,'unverified text','fictional',p['catalogue'])
        with self.assertRaises(ValueError):reference.image_reference_proposal(source,target,w,'receives the referred handoff','fictional',p['catalogue'])
