"""RED tests for rights-checked private batch projection and coverage."""
import base64,hashlib,json,unittest
from pathlib import Path
from importlib.util import spec_from_file_location,module_from_spec
ROOT=Path(__file__).resolve().parents[1] if (Path(__file__).resolve().parents[1]/'rims_batch_products.py').exists() else Path(__file__).resolve().parent
def load(n):
 p=ROOT/(n+'.py'); s=spec_from_file_location(n,p)
 try:m=module_from_spec(s);s.loader.exec_module(m);return m
 except FileNotFoundError:return None
p=load('rims_batch_products')
def enc(obj):
 raw=json.dumps(obj).encode();return {'raw_base64':base64.b64encode(raw).decode(), 'sha256':hashlib.sha256(raw).hexdigest()}
MAP={'schema':'careops-rims.field-product-map/1','source_id':'OpenAlex','domain':'publications','revision':'review-candidate-1','fields':[
 {'source_path':'/doi','target_field':'doi','kinds':['string','null'],'cardinality':'one','transform':'doi'},
 {'source_path':'/open_access/oa_status','target_field':'oa','kinds':['string'],'cardinality':'one','transform':'identity'},
 {'source_path':'/authorships','target_field':'authorships','kinds':['array'],'cardinality':'one','transform':'identity'}]}
CAT={'schema':'careops-rims.existing-source-adoption/1','sources':[{'source':'OpenAlex','primary_domain':'publications'}]}
class BatchTests(unittest.TestCase):
 def setUp(self):
  a=enc({'doi':'https://doi.org/10.1234/a','open_access':{'oa_status':'gold'},'authorships':[{'author':{'id':'A1'}}],'extra':42})
  b=enc({'doi':None,'authorships':[],'other':{'nested':[1,2]}})
  self.batch={'schema':'careops-rims.retained-json-batch/1','source_id':'OpenAlex','records':[
    {'record_id':'W1',**a},{'record_id':'W2',**b}]}
  self.receipt={'schema':'careops-rims.retained-source-receipt/1','source_id':'OpenAlex','complete':True,
    'record_hashes':{'W1':a['sha256'],'W2':b['sha256']}}
 def call(self,**kwargs):
  return p.project_batch(self.batch,self.receipt,MAP,CAT,verify_receipt=lambda _:True,verify_mapping=lambda _:True,**kwargs)
 def test_complete_source_and_missingness(self):
  out=self.call()
  self.assertEqual(out['summary']['records'],2)
  self.assertEqual(out['summary']['field_quality']['doi'],{'present':1,'null':1,'missing':0})
  self.assertEqual(out['summary']['field_quality']['oa'],{'present':1,'null':0,'missing':1})
  self.assertEqual(out['summary']['field_quality']['authorships']['present'],2)
  self.assertIn('/other/nested/[]',out['summary']['unmapped_paths'])
  self.assertEqual(out['products'][0]['fields']['doi']['value'],'10.1234/a')
  self.assertEqual(len(out['products'][0]['fields']['authorships']['value']),1)
  self.assertFalse(out['summary']['native_usage_verified'])
  self.assertFalse(out['native_publish_authorised'])
 def test_no_external_approval(self):
  with self.assertRaises(ValueError):p.project_batch(self.batch,self.receipt,MAP,CAT)
 def test_incomplete_or_mismatched_receipt(self):
  bad={**self.receipt,'complete':False}
  with self.assertRaises(ValueError):p.project_batch(self.batch,bad,MAP,CAT,verify_receipt=lambda _:True,verify_mapping=lambda _:True)
  with self.assertRaises(ValueError):p.project_batch(self.batch,{**self.receipt,'record_hashes':{'W1':'0'*64}},MAP,CAT,verify_receipt=lambda _:True,verify_mapping=lambda _:True)
 def test_no_extra_or_duplicate_rows(self):
  bad={**self.batch,'records':self.batch['records']+[self.batch['records'][0]]}
  with self.assertRaises(ValueError):p.project_batch(bad,self.receipt,MAP,CAT,verify_receipt=lambda _:True,verify_mapping=lambda _:True)
  with self.assertRaises(ValueError):p.project_batch({**self.batch,'source_id':'Unknown'},self.receipt,MAP,CAT,verify_receipt=lambda _:True,verify_mapping=lambda _:True)
 def test_invalid_base64_rejected(self):
  bad={**self.batch,'records':[{**self.batch['records'][0],'raw_base64':'$$$$'},self.batch['records'][1]]}
  with self.assertRaises(ValueError):p.project_batch(bad,self.receipt,MAP,CAT,verify_receipt=lambda _:True,verify_mapping=lambda _:True)
 def test_summary_does_not_leak_private_values(self):
  out=self.call()
  self.assertNotIn('https://doi.org/',str(out['summary']))
  self.assertNotIn('A1',str(out['summary']))
  self.assertTrue(out['private_values'])

if __name__=='__main__':unittest.main()
