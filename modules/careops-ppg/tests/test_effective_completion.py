import copy, importlib.util, json, pathlib, unittest
from scripts.ppg_catalogue_relationships import digest
from scripts.ppg_assessment_history_archive import prepare_archive
from scripts import ppg_effective_completion as mod
from tests.multi_fictional import fictional_case
t=fictional_case()['transition']
def seal(d,k):
 d.pop(k,None);d[k]=digest(d);return d
class ResolverTest(unittest.TestCase):
 def setUp(self):
  self.t=copy.deepcopy(t);self.m=json.loads(t['patch']['EvidenceManifest']);self.uid=t['documentUID'];self.key=t['assessmentKey'];self.old=self.m['completedAssessment']
 def amendment(self,tag):
  t2=copy.deepcopy(self.t); e=json.loads(t2['patch']['EvidenceManifest'])['completedAssessment'];e['limitations'].append(tag);seal(e,'completionKey');m2=json.loads(t2['patch']['EvidenceManifest']);m2['completedAssessment']=e;t2['patch']['EvidenceManifest']=json.dumps(m2);t2['completionKey']=e['completionKey'];t2['patchSHA256']=digest(t2['patch']);a={'kind':'multi-edition-revalidation','priorCompletionKey':self.old['completionKey'],'priorCompletionEvidenceSHA256':digest(self.old),'transition':t2,'tag':tag};return seal(a,'amendmentKey')
 def call(self,m,fetch=None):return mod.resolve(m if isinstance(m,str) else json.dumps(m),self.uid,self.key,fetch)
 def test_original_and_amendment(self):
  self.assertEqual(self.call(self.m)['status'],'resolved'); self.m['assessmentReviewAddenda']=[self.amendment('first'),self.amendment('second')];r=self.call(self.m);self.assertEqual(r['status'],'history_order_unverified');self.assertEqual(r['appliedAddenda'],2);self.assertEqual(r['original'],self.old);self.assertIsNone(r['effective'])
 def test_tamper_and_unknown(self):
  a=self.amendment('test');a['tag']='changed';self.m['assessmentReviewAddenda']=[a];self.assertEqual(self.call(self.m)['status'],'invalid');self.m['assessmentReviewAddenda']=[{'kind':'unknown'}];self.assertEqual(self.call(self.m)['status'],'invalid')
 def test_archives(self):
  self.m['assessmentReviewAddenda']=[self.amendment('a'),self.amendment('b')];p=prepare_archive(json.dumps(self.m),'https://example.org/archive');self.assertEqual(self.call(p.compacted_manifest)['status'],'archive_unavailable');self.assertEqual(self.call(p.compacted_manifest,lambda _:b'wrong')['status'],'archive_unverifiable');r=self.call(p.compacted_manifest,lambda _:p.archive_bytes);self.assertEqual(r['status'],'history_order_unverified');self.assertEqual(r['appliedAddenda'],2)
  changed=json.loads(p.compacted_manifest);changed['new']='later';self.assertEqual(self.call(changed,lambda _:p.archive_bytes)['status'],'archive_unverifiable')
 def test_reversed_archived_addenda_fails_closed(self):
  a,b=self.amendment('a'),self.amendment('b');self.m['assessmentReviewAddenda']=[b,a];p=prepare_archive(json.dumps(self.m),'https://example.org/reversed');r=self.call(p.compacted_manifest,lambda _:p.archive_bytes);self.assertEqual(r['status'],'history_order_unverified');self.assertIsNone(r['effective'])
 def test_archive_fetch_io_failure_is_unavailable(self):
  self.m['assessmentReviewAddenda']=[self.amendment('a'),self.amendment('b')];p=prepare_archive(json.dumps(self.m),'https://example.org/archive')
  def failed(_):raise OSError('fictional unavailable')
  r=self.call(p.compacted_manifest,failed);self.assertEqual(r['status'],'archive_unavailable');self.assertIsNone(r['effective'])
 def test_archived_then_later_and_chained(self):
  a,b,c,d=[self.amendment(x) for x in 'abcd'];self.m['assessmentReviewAddenda']=[a,b];p=prepare_archive(json.dumps(self.m),'https://example.org/a'); current=json.loads(p.compacted_manifest);current['assessmentReviewAddenda'].append(c)
  r=self.call(current,lambda ref:p.archive_bytes);self.assertEqual(r['status'],'history_order_unverified');self.assertEqual(r['appliedAddenda'],3);self.assertIsNone(r['effective'])
  q=prepare_archive(json.dumps(current),'https://example.org/b');latest=json.loads(q.compacted_manifest);latest['assessmentReviewAddenda'].append(d);archives={p.archive_reference['archiveSHA256']:p.archive_bytes,q.archive_reference['archiveSHA256']:q.archive_bytes};fetch=lambda ref:archives.get(ref['archiveSHA256']);r=self.call(latest,fetch);self.assertEqual(r['status'],'history_order_unverified');self.assertEqual(r['appliedAddenda'],4);self.assertIsNone(r['effective'])
  missing=dict(archives);del missing[p.archive_reference['archiveSHA256']];self.assertEqual(self.call(latest,lambda ref:missing.get(ref['archiveSHA256']))['status'],'archive_unavailable')
  broken=copy.deepcopy(latest);broken['assessmentHistoryArchives'].reverse();self.assertEqual(self.call(broken,fetch)['status'],'archive_unverifiable')
  broken=copy.deepcopy(latest);broken['assessmentReviewAddenda'].reverse();self.assertEqual(self.call(broken,fetch)['status'],'archive_unverifiable')
  broken=copy.deepcopy(latest);broken['assessmentReviewAddenda'].append(d);self.assertEqual(self.call(broken,fetch)['status'],'invalid')
  broken=copy.deepcopy(latest);broken['assessmentReviewAddenda'][-1]['tag']='tampered';self.assertEqual(self.call(broken,fetch)['status'],'invalid')
if __name__=='__main__':unittest.main()
