import unittest
from scripts.ppg_run_read_evidence import apply_run_reads


class RetainedReadsTest(unittest.TestCase):
    def setUp(self):
        self.candidate = {'flow':'FICTIONAL sample','action':'Read file','operation':'HttpRequest'}
        self.production = dict(self.candidate,flow='Document generation')
        self.manifest = {'rows':{'library':{'ReadFlows':None}},
                         'unresolvedActions':[self.candidate,self.production]}
        self.names = {'sample':'FICTIONAL sample','document':'Document generation'}
        self.row = dict(flowId='sample',flow='FICTIONAL sample',action='Read file',
                        run='sample run',fileId='file',dataset='library',method='GET',
                        runStatus='Succeeded',actionStatus='Succeeded')

    def test_selected_run_is_separate_from_static_and_production(self):
        apply_run_reads(self.manifest,self.names,[self.row,self.row],{})
        self.assertEqual(self.manifest['unresolvedActions'],[self.production])
        self.assertEqual(self.manifest['fictionalRunReads'],[self.row])
        self.assertIsNone(self.manifest['rows']['library']['ReadFlows'])
        self.assertIn('1 read',self.manifest['rows']['library']['ObservedReadFlows'])

    def test_rejects_wrong_flow_and_unsuccessful_actions(self):
        for change in ({'flowId':'document'}, {'actionStatus':'Skipped'}, {'method':'POST'}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                apply_run_reads(self.manifest,self.names,[self.row|change],{})
