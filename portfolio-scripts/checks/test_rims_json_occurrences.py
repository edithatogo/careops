"""TDD: original JSON value/ordering and duplicate key safety."""
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
import json
import unittest

SRC=Path(__file__).resolve().parents[1]/'rims_json_occurrences.py' if (Path(__file__).resolve().parents[1]/'rims_json_occurrences.py').exists() else Path(__file__).with_name('rims_json_occurrences.py')
spec=spec_from_file_location('rims_json_occurrences',SRC)
try:
    mod=module_from_spec(spec);spec.loader.exec_module(mod)
except FileNotFoundError:
    mod=None

RAW=(b'{"record":{"authors":[{"orcid":"0000-0000-0000-0000","name":"A"},'
     b'{"name":null}],"tags":[],"codes":{},"x/y":false,"~":0},"n":1.25}')
SHA=__import__('hashlib').sha256(RAW).hexdigest()

class Contract(unittest.TestCase):
    def exp(self,raw=RAW,**kwargs):
        return mod.expand(raw,source_id='fictional',record_id='pub-1',
          source_sha256=__import__('hashlib').sha256(raw).hexdigest(),
          verify_source=lambda s,r,h: True,**kwargs)
    def test_complete_typed_paths(self):
        data=self.exp()
        self.assertEqual(data['schema'],'careops-rims.private-json-occurrences/1')
        self.assertTrue(data['private_values'])
        self.assertFalse(data['native_admission_authorised'])
        p={o['ordered_path']:o for o in data['occurrences']}
        self.assertEqual(p['/record/authors/0/orcid']['value'],'0000-0000-0000-0000')
        self.assertEqual(p['/record/authors/1/name']['kind'],'null')
        self.assertEqual(p['/record/tags']['kind'],'array')
        self.assertEqual(p['/record/codes']['kind'],'object')
        self.assertEqual(p['/record/x~1y']['value'],False)
        self.assertEqual(p['/record/~0']['value'],0)
        self.assertEqual(p['/record/authors/0/name']['semantic_path'],'/record/authors/[]/name')
        self.assertEqual(mod.reconstruct(data),json.loads(RAW))
    def test_array_root_reversible(self):
        data=self.exp(raw=b'[{},[null,true,3.1],"x"]')
        self.assertEqual(mod.reconstruct(data),[{},[None,True,3.1],"x"])
    def test_many_array_elements_preserve_numeric_order(self):
        raw = json.dumps({"items": list(range(25))}).encode("utf-8")
        data = self.exp(raw=raw)
        self.assertEqual(mod.reconstruct(data), {"items": list(range(25))})
    def test_empty_and_missing_distinct(self):
        data=self.exp(raw=b'{"a":null,"b":{},"c":[],"d":""}')
        result=mod.reconstruct(data)
        self.assertEqual(result,{'a':None,'b':{},'c':[],'d':''})
        self.assertNotIn('missing',result)
    def test_denied_source_refused(self):
        with self.assertRaises(ValueError):
            mod.expand(RAW,source_id='fictional',record_id='pub-1',source_sha256=SHA,
                       verify_source=lambda *_:False)
    def test_wrong_hash_refused(self):
        with self.assertRaises(ValueError):
            mod.expand(RAW,source_id='fictional',record_id='pub-1',source_sha256='f'*64,
                       verify_source=lambda *_:True)
    def test_duplicate_keys_and_nonfinite_refused(self):
        for raw in (b'{"a":1,"a":2}',b'{"a":NaN}',b'{"a":Infinity}'):
            with self.subTest(raw=raw), self.assertRaises(ValueError): self.exp(raw)
    def test_duplicate_or_gapped_occurrence_refused(self):
        data=self.exp(raw=b'{"a":[1,2]}')
        data['occurrences'].append(dict(data['occurrences'][-1]))
        with self.assertRaises(ValueError):mod.reconstruct(data)
    def test_no_secret_stdout(self):
        data=self.exp(raw=b'{"secret":"private-patient-data"}')
        self.assertNotIn('private-patient-data',str({k:v for k,v in data.items() if k!='occurrences'}))
        self.assertTrue(data['private_values'])

if __name__=='__main__': unittest.main()
