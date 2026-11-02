import unittest

from scripts.ppg_binding_resolution import action_binding


class DatasetBindingsTest(unittest.TestCase):
    site = 'https://example.invalid/sites/work'
    proof = {'site': site, 'files': {}, 'folders': {'evidence': '/sites/work/Evidence'}}

    def connector(self, operation, **parameters):
        return {'type': 'OpenApiConnection', 'inputs': {
            'host': {'apiId':'shared_sharepointonline','operationId':operation},
            'parameters': {'dataset':self.site, **parameters}}}

    def test_move_checks_both_ends(self):
        actions = {'create': self.connector('CreateFile', folderPath='/Evidence/Drafts'),
                   'move': self.connector('MoveFileAsync', **{
                       'parameters/sourceFileId': "@body('create')?['Id']",
                       'parameters/destinationDataset': self.site,
                       'parameters/destinationFolderPath': '/Evidence/Issued'})}
        self.assertEqual(action_binding('move',actions,{},self.proof),({'evidence'},('WriteFlows',)))
        actions['move']['inputs']['parameters']['parameters/destinationDataset'] += '-other'
        self.assertIsNone(action_binding('move',actions,{},self.proof))

    def test_arbitrary_record_link_does_not_inherit_its_parent(self):
        actions = {'read': self.connector('HttpRequest', **{
            'parameters/method':'GET',
            'parameters/uri':"@concat('_api/web/GetFileById(''',body('entry')?['linkedFile'],''')')"})}
        self.assertIsNone(action_binding('read',actions,{},self.proof))
