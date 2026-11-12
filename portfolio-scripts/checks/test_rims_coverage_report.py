"""TDD: private-safe HTML/CSV view of aggregate field lineage, not false usage."""
import unittest
from pathlib import Path
from importlib.util import spec_from_file_location,module_from_spec
source=Path(__file__).resolve().parents[1]/"rims_coverage_report.py"
spec=spec_from_file_location("rims_coverage_report",source)
m=module_from_spec(spec)
spec.loader.exec_module(m)
DATA={'schema':'careops-rims.existing-source-coverage-rollup/1','sources_in_catalogue':17,
'sources_with_declared_profiles':1,'sources_still_unprofiled':['Other'],
'domain_summaries':[{'domain':'research <script>x</script>','reported_sources':1,
 'fields_observed':8,'mapped_to_consumer':3,'retained_only':2,'excluded_with_reason':1,
 'unassessed':2,'declared_consumer_mapping_fraction':3/8,'field_accounting_fraction':6/8,
 'native_utilisation_verified':False},
 {'domain':'empty','reported_sources':0,'fields_observed':0,'mapped_to_consumer':0,
 'retained_only':0,'excluded_with_reason':0,'unassessed':0,
 'declared_consumer_mapping_fraction':None,'field_accounting_fraction':None,
 'native_utilisation_verified':False}],
 'source_summaries':[],'full_field_utilisation_proven':False,'native_model_parity_proven':False}
class Reports(unittest.TestCase):
 def test_html_labels_and_escapes(self):
  out=m.render_html(DATA)
  self.assertIn('research &lt;script&gt;x&lt;/script&gt;',out)
  self.assertNotIn('<script>x</script>',out)
  self.assertIn('Declared consumer mappings',out)
  self.assertIn('Not assessed',out)
  self.assertIn('Source-only',out)
 def test_no_private_paths_or_false_actual_use(self):
  out=m.render_html(DATA)
  self.assertNotIn('source_path',out)
  self.assertNotIn('verified analytical utilisation:',out.lower())
 def test_count_inconsistency_refused(self):
  bad={**DATA,'domain_summaries':[{**DATA['domain_summaries'][0],'unassessed':20}]}
  with self.assertRaises(ValueError):m.render_html(bad)
 def test_empty_input_has_no_fictional_100pct(self):
  out=m.render_html({**DATA,'domain_summaries':[]})
  self.assertIn('No assessed domain profiles',out)
  self.assertNotIn('100.0%',out)
 def test_unqualified_native_claim_refused(self):
  with self.assertRaises(ValueError):m.render_html({**DATA,'full_field_utilisation_proven':True})
if __name__=='__main__':unittest.main()
