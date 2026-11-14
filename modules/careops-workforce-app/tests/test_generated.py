import unittest
from tools.qualify import audit
class SourceTests(unittest.TestCase):
 def test_all_sources_parse_without_secrets_or_claiming_native_readiness(self):
  result=audit()
  self.assertEqual(result['screens'],9)
  self.assertEqual(result['flows'],10)
  self.assertFalse(result['workflows_operational'])
