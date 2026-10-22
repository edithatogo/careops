"""Exercise byte/content distinctions and malformed package refusal."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
import warnings
from unittest.mock import patch
import zipfile

SPEC = importlib.util.spec_from_file_location(
    "docx_revisions", Path(__file__).resolve().parents[1] / "compare_docx_revisions.py")
docx = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(docx)
NS = docx.W[1:-1]
R = docx.R[1:-1]


def package(path, *, split=False, break_line=True, target="https://example.invalid/paper",
            relation="rId1", control="retained", metadata="first", control_id="1"):
    runs = ('<w:r><w:t>Fi</w:t></w:r><w:r><w:t>ction</w:t></w:r>' if split
            else '<w:r><w:t>Fiction</w:t></w:r>')
    body = (f'<w:document xmlns:w="{NS}" xmlns:r="{R}"><w:body><w:p>{runs}'
            + ('<w:r><w:br/></w:r>' if break_line else '')
            + f'<w:hyperlink r:id="{relation}"><w:r><w:t>paper</w:t></w:r></w:hyperlink>'
            + '</w:p><w:sdt><w:sdtPr><w:tag w:val="CaseUID"/>'
            + f'<w:id w:val="{control_id}"/></w:sdtPr><w:sdtContent><w:p>'
            + f'<w:r><w:t>{control}</w:t></w:r></w:p></w:sdtContent></w:sdt>'
            + '</w:body></w:document>')
    rels = (f'<Relationships xmlns="{docx.REL[1:-1]}"><Relationship Id="{relation}" '
            f'Type="{R}/hyperlink" Target="{target}" TargetMode="External"/></Relationships>')
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("word/document.xml", body)
        archive.writestr("word/_rels/document.xml.rels", rels)
        archive.writestr("docProps/app.xml", metadata)


class RevisionComparison(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.before = Path(self.directory.name) / "before.docx"
        self.after = Path(self.directory.name) / "after.docx"
        package(self.before)

    def test_word_run_segmentation_and_relationship_ids_do_not_change_content(self):
        package(self.after, split=True, relation="rId9", metadata="later")
        result = docx.compare(self.before, self.after)
        self.assertFalse(result["byteExact"])
        self.assertTrue(result["selectedContentExact"])
        self.assertTrue(result["controlIdsExact"])
        self.assertIn("word/document.xml", result["changedMembers"])

    def test_changed_link_break_or_control_is_not_equivalent(self):
        for kwargs, field in [({"target": "https://example.invalid/changed"}, "hyperlinks"),
                              ({"break_line": False}, "paragraphs"),
                              ({"control": "changed"}, "controls")]:
            with self.subTest(field=field):
                package(self.after, **kwargs)
                result = docx.compare(self.before, self.after)
                self.assertFalse(result["selectedContentExact"])
                self.assertFalse(result["comparisons"][field])

    def test_control_identity_is_reported_separately(self):
        package(self.after, control_id="2")
        result = docx.compare(self.before, self.after)
        self.assertTrue(result["selectedContentExact"])
        self.assertFalse(result["controlIdsExact"])

    def test_default_cli_demands_exact_bytes_and_explicit_content_mode(self):
        package(self.after, split=True)
        for mode, expected in [([], 1), (["--require", "selected-content"], 0)]:
            with patch("sys.argv", ["compare", str(self.before), str(self.after), *mode]):
                with contextlib.redirect_stdout(io.StringIO()) as output:
                    self.assertEqual(docx.main(), expected)
                self.assertNotIn("retained", output.getvalue())
                self.assertIn("limitations", json.loads(output.getvalue()))
        self.after.write_bytes(self.before.read_bytes())
        self.assertTrue(docx.compare(self.before, self.after)["byteExact"])

    def test_unsafe_duplicate_or_entity_members_are_refused(self):
        for name, xml in [("../outside", "ordinary"), ("word/./other.xml", "ambiguous"),
                          ("word/document.xml", "duplicate"),
                          ("evil.xml", '<!DOCTYPE d [<!ENTITY e "payload">]><d>&e;</d>')]:
            with self.subTest(name=name):
                package(self.after)
                if name == "evil.xml":
                    with zipfile.ZipFile(self.after) as archive:
                        members = {x: archive.read(x) for x in archive.namelist()}
                    members["word/document.xml"] = xml.encode()
                    with zipfile.ZipFile(self.after, "w") as archive:
                        for item, value in members.items():
                            archive.writestr(item, value)
                else:
                    with zipfile.ZipFile(self.after, "a") as archive:
                        with warnings.catch_warnings():
                            warnings.simplefilter("ignore", UserWarning)
                            archive.writestr(name, xml)
                with self.assertRaises(ValueError):
                    docx.compare(self.before, self.after)

    def test_bounds_and_missing_or_unresolved_body_parts_are_refused(self):
        package(self.after)
        with patch.object(docx, "MAX_ARCHIVE", 10):
            with self.assertRaises(ValueError):
                docx.compare(self.before, self.after)
        with patch.object(docx, "MAX_EXPANDED", 10):
            with self.assertRaises(ValueError):
                docx.compare(self.before, self.after)
        with zipfile.ZipFile(self.after, "w") as archive:
            archive.writestr("unrelated.xml", "<root/>")
        with self.assertRaises(ValueError):
            docx.compare(self.before, self.after)
        package(self.after)
        with zipfile.ZipFile(self.after) as archive:
            body = archive.read("word/document.xml")
        with zipfile.ZipFile(self.after, "w") as archive:
            archive.writestr("word/document.xml", body)
        with self.assertRaises(ValueError):
            docx.compare(self.before, self.after)


if __name__ == "__main__":
    unittest.main()
