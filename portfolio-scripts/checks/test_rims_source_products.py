"""TDD contract tests: candidate typed fields with full source recovery."""
import importlib.util,hashlib,json,unittest
from pathlib import Path
root=Path(__file__).resolve().parents[1] if (Path(__file__).resolve().parents[1]/'rims_source_products.py').exists() else Path(__file__).resolve().parent
def load(name):
 s=importlib.util.spec_from_file_location(name,root/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
json_occ=load('rims_json_occurrences')
try: product=load('rims_source_products')
except FileNotFoundError: product=None
RAW=json.dumps({'id':'https://openalex.org/W123','doi':'https://doi.org/10.1234/ABC',
  'authorships':[{'author':{'id':'https://openalex.org/A01'},'institutions':[{'ror':'https://ror.org/abc'}]},
                 {'author':{'id':'https://openalex.org/A02'},'institutions':[]}],
  'open_access':{'oa_status':'gold'},'abstract':None,'unused':{'free_text':'keep original'}}).encode()
SHA=hashlib.sha256(RAW).hexdigest()
MAP={'schema':'careops-rims.field-product-map/1','source_id':'OpenAlex','domain':'publications',
     'revision':'candidate-1','fields':[
     {'source_path':'/doi','target_field':'doi','kinds':['string'],'cardinality':'one','transform':'doi'},
     {'source_path':'/authorships/[]/author/id','target_field':'author_ids','kinds':['string'],'cardinality':'many','transform':'identity'},
     {'source_path':'/open_access/oa_status','target_field':'oa','kinds':['string'],'cardinality':'one','transform':'identity'},
     {'source_path':'/not_in_response','target_field':'future','kinds':['string'],'cardinality':'one','transform':'identity'},
     {'source_path':'/abstract','target_field':'abstract','kinds':['null','string'],'cardinality':'one','transform':'identity'}]}
class TestProducts(unittest.TestCase):
 def setUp(self):
  self.src=json_occ.expand(RAW,source_id='OpenAlex',record_id='W123',source_sha256=SHA,verify_source=lambda *args:True)
 def test_typed_fields_full_source(self):
  o=product.project(self.src,MAP,verify_map=lambda x:True)
  self.assertEqual(o['fields']['doi']['value'],'10.1234/abc')
  self.assertEqual(o['fields']['author_ids']['value'],['https://openalex.org/A01','https://openalex.org/A02'])
  self.assertEqual(o['fields']['future']['status'],'missing')
  self.assertEqual(o['fields']['abstract']['status'],'null')
  self.assertEqual(o['fields']['oa']['value'],'gold')
  self.assertTrue(o['private_values']);self.assertFalse(o['native_publish_authorised'])
  self.assertEqual(json_occ.reconstruct(o['source_occurrences']),json.loads(RAW))
  self.assertIn('/unused/free_text',o['unmapped_source_paths'])
 def test_not_authorised_mapping_refused(self):
  with self.assertRaises(ValueError):product.project(self.src,MAP)
  with self.assertRaises(ValueError):product.project(self.src,MAP,verify_map=lambda _:False)
 def test_wrong_source_refused(self):
  with self.assertRaises(ValueError):product.project(self.src,{**MAP,'source_id':'Crossref'},verify_map=lambda _:True)
 def test_scalar_cardinality_refused(self):
  altered=json.loads(json.dumps(MAP))
  altered['fields'][1]['cardinality']='one'
  with self.assertRaises(ValueError):product.project(self.src,altered,verify_map=lambda _:True)
 def test_duplicate_targets_refused(self):
  altered=json.loads(json.dumps(MAP));altered['fields'].append(dict(altered['fields'][0]))
  with self.assertRaises(ValueError):product.project(self.src,altered,verify_map=lambda _:True)
 def test_nested_container_is_usable_without_flattening(self):
  mapping={**MAP, 'fields':[{'source_path':'/authorships','target_field':'full_authorships',
    'kinds':['array'],'cardinality':'one','transform':'identity'}]}
  result=product.project(self.src,mapping,verify_map=lambda _:True)
  self.assertEqual(len(result['fields']['full_authorships']['value']),2)
  self.assertEqual(result['fields']['full_authorships']['value'][0]['author']['id'],
    'https://openalex.org/A01')
  self.assertEqual(result['fields']['full_authorships']['value'][1]['institutions'],[])
 def test_many_nested_authors_preserve_all_ordinals(self):
  raw=json.dumps({'authorships':[{'author':{'id':str(i)}} for i in range(25)]}).encode()
  source=json_occ.expand(raw,source_id='OpenAlex',record_id='Wlong',source_sha256=hashlib.sha256(raw).hexdigest(),verify_source=lambda *_:True)
  mapping={**MAP,'fields':[{'source_path':'/authorships/[]/author/id','target_field':'author_ids',
    'kinds':['string'],'cardinality':'many','transform':'identity'}]}
  out=product.project(source,mapping,verify_map=lambda _:True)
  self.assertEqual(out['fields']['author_ids']['value'],[str(i) for i in range(25)])
  self.assertEqual(out['fields']['author_ids']['source_ordinals'][10],'/authorships/10/author/id')
 def test_unrecognised_doi_refused(self):
  raw=b'{"doi":"not a DOI"}'
  s=json_occ.expand(raw,source_id='OpenAlex',record_id='Wbad',source_sha256=hashlib.sha256(raw).hexdigest(),verify_source=lambda *_:True)
  with self.assertRaises(ValueError):product.project(s,MAP,verify_map=lambda _:True)
 def test_source_can_be_fully_recovered_when_no_mappings(self):
  m={**MAP,'fields':[]}
  out=product.project(self.src,m,verify_map=lambda _:True)
  self.assertEqual(out['unmapped_source_paths'],out['all_source_paths'])
  self.assertTrue(out['private_values'])
 def test_unverified_declaration_does_not_grant_approval(self):
  out=product.project(self.src,MAP,verify_map=lambda _:True)
  self.assertFalse(out['report_issued']);self.assertEqual(out['review_state'],'NeedsReview')

if __name__=='__main__':unittest.main()
