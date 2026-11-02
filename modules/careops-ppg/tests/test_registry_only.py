import copy
import json
import unittest
from pathlib import Path
from uuid import UUID

from scripts.ppg_registry_only import checkpoint_registry_only, transform, validate
from scripts.ppg_source_sync import SyncError, retention_contract

class RegistryOnlyTests(unittest.TestCase):
    def setUp(self):
        self.entries = [
            dict(documentUID=str(UUID(int=i)), itemId=i, printedIdentifier=f"Test-{i}", evidenceRef=f"fixture:{i}")
            for i in range(2, 13)
        ]
        self.source = str(UUID(int=1))
        self.rows = [dict(DocumentUID=self.source, Id=1)] + [
            dict(DocumentUID=e["documentUID"], Id=e["itemId"], sourceDocumentId=e["printedIdentifier"],
                 sourceSnapshotRef=e["evidenceRef"]) for e in self.entries
        ]
        self.plan = dict(sourceSha256="fixture", contractHash="fixture", inputCount=1,
                         operations=[dict(DocumentUID=self.source)])
        self.checkpoint = dict(status="completed", sourceSha256="fixture", identityContractHash="fixture",
                               readbackCount=1, catalogueReadbackCount=12, registryOnlyManifestVersion=1,
                               registryOnlyEntries=self.entries, registryOnlyUnchanged=True)

    def test_changed_workbook_retains_eleven_and_rejects_extra(self):
        for digest in ["first workbook", "changed workbook"]:
            self.plan["sourceSha256"] = self.checkpoint["sourceSha256"] = digest
            result = retention_contract(self.plan, self.checkpoint, self.rows)
            self.assertEqual(len(result["registryOnlyUIDs"]), 11)
            self.assertEqual(result["retainedUIDs"], [])
        with self.assertRaises(SyncError):
            retention_contract(self.plan, self.checkpoint, self.rows + [dict(DocumentUID=str(UUID(int=20)))])

    def test_adoption_reuses_item_identity_and_replay(self):
        adopted = self.entries[0]["documentUID"]
        self.plan["operations"].append(dict(DocumentUID=adopted))
        self.plan["inputCount"] = self.checkpoint["readbackCount"] = 2
        with self.assertRaises(ValueError):
            retention_contract(self.plan, self.checkpoint, self.rows)
        # Two workbook identities plus ten Registry-only identities still total twelve.
        self.checkpoint["registryOnlyEntries"] = self.entries[1:]
        for _ in range(2):
            result = retention_contract(self.plan, self.checkpoint, self.rows)
            self.assertIn(adopted, result["activeUIDs"])
            self.assertNotIn(adopted, result["registryOnlyUIDs"])
            self.assertEqual(len(result["catalogueUIDs"]), 12)

    def test_wrong_item_or_evidence_fails(self):
        for field, value in [("Id", 40), ("sourceSnapshotRef", "unrelated")]:
            rows = copy.deepcopy(self.rows)
            rows[1][field] = value
            with self.assertRaises(ValueError):
                checkpoint_registry_only(self.checkpoint, {self.source}, rows)
        with self.assertRaises(ValueError):
            validate(dict(schemaVersion=1, entries=self.entries + self.entries[:1]))

    def test_install_template_is_reusable(self):
        template = json.loads(Path('templates/installation/workflows/qw3source-onlyreconciliation.json').read_text())
        manifest = dict(schemaVersion=1, entries=self.entries)
        candidate = transform(template, manifest)
        self.assertEqual(transform(candidate, manifest), candidate)
        self.assertEqual(transform(candidate, dict(schemaVersion=1, entries=[])), template)

    def test_approved_adoption_recovers_after_write_before_receipt(self):
        import tempfile
        from tests.test_identity_application import ApplicationTests
        from tests.test_ppg_source_sync import FakeTarget
        from scripts.ppg_identity_application import verify_application
        from scripts.ppg_source_sync import reconcile
        fixture = ApplicationTests()
        fixture.setUp()
        application = fixture.compile()
        plan = verify_application(application, fixture.snapshot, fixture.ledger, fixture.allowed)

        class InterruptAfterAdoption(FakeTarget):
            def patch(self, uid, fields, etag):
                super().patch(uid, fields, etag)
                if uid == fixture.b:
                    raise RuntimeError("interrupted after native update")

        target = InterruptAfterAdoption()
        target.items[fixture.a].update(plan["operations"][0]["fields"])
        target.items[fixture.b].update(Id=988, edition="retained", sourceDocumentId="old spelling")
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(RuntimeError, "interrupted after native update"):
                reconcile(plan, target, Path(tmp))
            replay = reconcile(plan, target, Path(tmp))
        self.assertEqual(replay["writeCount"], 0)
        self.assertEqual(target.items[fixture.b]["Id"], 988)
        self.assertEqual(target.items[fixture.b]["edition"], "retained")
        self.assertEqual(set(target.items), {fixture.a, fixture.b})
