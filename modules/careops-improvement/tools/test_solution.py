"""Source checks for the independently versioned solution scaffold."""
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SolutionTests(unittest.TestCase):
    def test_identity_version_and_publisher(self):
        manifest = ET.parse(ROOT / "platform/solution/src/Other/Solution.xml").getroot().find("SolutionManifest")
        self.assertEqual(manifest.findtext("UniqueName"), "CareOpsImprovementRegister")
        self.assertEqual(manifest.findtext("Version"), "0.1.0.0")
        self.assertEqual(manifest.findtext("Managed"), "0")
        self.assertEqual(manifest.findtext("Publisher/CustomizationPrefix"), "coi")

    def test_no_native_operations_in_pack_script(self):
        source = (ROOT / "tools/pack_solution.sh").read_text()
        commands = [line.strip() for line in source.splitlines() if line.startswith("pac ")]
        self.assertEqual(len(commands), 2)
        self.assertTrue(commands[0].startswith("pac solution pack "))
        self.assertTrue(commands[1].startswith("pac solution unpack "))
