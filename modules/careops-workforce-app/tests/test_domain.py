import unittest
from datetime import date
from domain import *
class DomainTests(unittest.TestCase):
 def test_balanced_fortnight(self):
  blocks=[Activity(w,d,540,1020,'C1','CH') for w in (1,2) for d in (1,2,3,4,5)]
  r=reconcile(blocks,2,'80','0')
  self.assertTrue(r['ordinary_balanced']);self.assertEqual(r['planned_ordinary_hours'],'80')
 def test_overlap_rejected(self):
  with self.assertRaises(DomainError):validate_cycle([Activity(1,1,500,600,'C1','CH'),Activity(1,1,550,650,'S1','CH')],1)
 def test_cst_threshold(self):
  blocks=[Activity(1,1,480,720,'S1','CH',cst=True),Activity(2,1,480,720,'S2','CH',cst=True)]
  r=reconcile(blocks,2,80,'0.10')
  self.assertTrue(r['cst_sufficient'])
 def test_unknown_annualised_basis_rejected(self):
  with self.assertRaises(DomainError):reconcile([],2,80,'0.1',4)
 def test_month_end(self):self.assertEqual(next_review_date(date(2027,1,31),1),date(2027,2,28))
 def test_due_key_is_stable_and_edition_sensitive(self):
  a=obligation_key('p','annual',1,date(2027,1,1))
  self.assertEqual(a,obligation_key('p','annual',1,date(2027,1,1)))
  self.assertNotEqual(a,obligation_key('p','annual',2,date(2027,1,1)))
 def test_diff(self):self.assertEqual(diff_versions({'a':1,'b':2},{'a':1,'b':3}),[{'path':'b','before':2,'after':3}])
 def test_bad_hours(self):
  with self.assertRaises(DomainError):reconcile([],2,'NaN','0.1')
