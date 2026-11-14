"""Synthetic tests for repository Power Platform skill declarations."""
import json
import tempfile
import unittest
from pathlib import Path
from tools.validate_agent_skills import validate, REQUIRED, MARKETS, VENDORED

class SkillConfigTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        for name in (".claude/settings.json",".github/copilot/settings.json"):
            p=self.root/name
            p.parent.mkdir(parents=True,exist_ok=True)
            p.write_text(json.dumps({"extraKnownMarketplaces":{k:{} for k in MARKETS},
                                     "enabledPlugins":{k:True for k in REQUIRED}}))
        for name in VENDORED|{"careops-power-platform"}:
            p=self.root/".agents/skills"/name/"SKILL.md"
            p.parent.mkdir(parents=True,exist_ok=True)
            p.write_text("---\nname: test\n---\n")
        p=self.root/".agents/THIRD_PARTY_NOTICES.md"
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text("MIT")

    def test_valid_declarations(self):
        self.assertEqual(validate(self.root)["vendor_skills"],8)

    def test_missing_vendor_skill_fails(self):
        (self.root/".agents/skills/power-automate-reference/SKILL.md").unlink()
        with self.assertRaisesRegex(ValueError,"power-automate-reference"):
            validate(self.root)

    def test_disabled_plugin_fails(self):
        p=self.root/".claude/settings.json"
        data=json.loads(p.read_text())
        data["enabledPlugins"]["dataverse@power-platform-skills"]=False
        p.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError,"missing required"):
            validate(self.root)

    def test_missing_marketplace_fails(self):
        p=self.root/".github/copilot/settings.json"
        data=json.loads(p.read_text())
        data["extraKnownMarketplaces"].pop("power-cat-skills")
        p.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError,"unexpected marketplaces"):
            validate(self.root)
