"""Synthetic PubMed Xml.Document path tests; no author or abstract is leaked."""
import importlib.util
from pathlib import Path
import unittest

source=Path(__file__).resolve().parents[1]/"rims_pubmed_xml_field_profile.py"
spec=importlib.util.spec_from_file_location("rims_pubmed_xml_field_profile", source)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

HASH="d"*64


def element(name, value, *, attributes=None, namespace=""):
    return {"Name":name,"Namespace":namespace,"Value":value,
            "Attributes":[] if attributes is None else attributes}


class XMLFieldTests(unittest.TestCase):
    def setUp(self):
        self.docs=[
            [element("MedlineCitation",[
                element("Article",[
                    element("ArticleTitle","Fictional title"),
                    element("AuthorList",[
                        element("Author",[
                            element("ForeName","Fake"),
                            element("AffiliationInfo",[
                                element("Affiliation","Synthetic institution")
                            ]),
                        ]),
                        element("Author",[element("LastName","Invented")]),
                    ]),
                    element("GrantList",[
                        element("Grant",[element("GrantID","Fictional grant")]),
                    ]),
                ]),
            ],attributes=[{"Name":"Status","Namespace":"","Value":"synthetic"}])],
            [element("MedlineCitation",[
                element("Article",[
                    element("ArticleTitle","Another fictional title"),
                    element("AuthorList",[]),
                ]),
            ])],
        ]

    def test_named_elements_repetition_and_missingness(self):
        output=mod.profile_pubmed_nodes(self.docs,source_sha256=HASH)
        fields={field["path"]:field for field in output["fields"]}
        self.assertEqual(output["records_observed"],2)
        self.assertEqual(fields["/MedlineCitation/Article/AuthorList/Author"]["occurrences"],2)
        self.assertEqual(fields["/MedlineCitation/Article/AuthorList/Author"]["records_present"],1)
        self.assertEqual(fields["/MedlineCitation/Article/GrantList/Grant/GrantID"]["records_missing"],1)
        self.assertEqual(fields["/MedlineCitation/@Status"]["records_present"],1)
        self.assertNotIn("Synthetic institution",str(output))
        self.assertNotIn("Fictional grant",str(output))
        self.assertFalse(output["contains_values"])

    def test_namespaced_element_identity_without_raw_namespace(self):
        data=[[element("Thing","private text",namespace="urn:fictional:test")]]
        output=mod.profile_pubmed_nodes(data,source_sha256=HASH)
        path=output["fields"][0]["path"]
        self.assertIn("{ns:",path)
        self.assertNotIn("urn:fictional:test",str(output))

    def test_lossless_ordered_occurrences_for_private_analysis(self):
        result=mod.expand_xml_occurrences(
            self.docs[0],source_id="PubMed",record_id="fictional",
            source_sha256=HASH,
            verify_source=lambda source, record, digest: True,
        )
        self.assertTrue(result["private_values"])
        self.assertTrue(result["original_xml_tree_must_be_retained"])
        self.assertFalse(result["native_admission_authorised"])
        values=result["occurrences"]
        title=[row for row in values if row["semantic_path"].endswith("/ArticleTitle")]
        self.assertEqual(title[0]["value"],"Fictional title")
        self.assertTrue(any("/Author[1]" in row["ordered_path"] for row in values))
        self.assertTrue(any("/Author[2]" in row["ordered_path"] for row in values))
        self.assertEqual(result["occurrence_count"],len(values))
        self.assertTrue(any(row["kind"]=="attribute" for row in values))

    def test_private_projection_requires_independent_source_verifier(self):
        with self.assertRaises(mod.XMLProfileError):
            mod.expand_xml_occurrences(
                self.docs[0],source_id="PubMed",record_id="fictional",
                source_sha256=HASH,
            )

    def test_malformed_or_private_element_names_refused(self):
        for bad in ("John Smith","../secret","a/b"):
            with self.subTest(name=bad), self.assertRaises(mod.XMLProfileError):
                mod.profile_pubmed_nodes([[element(bad,"x")]],source_sha256=HASH)

    def test_duplicate_xml_attribute_refused(self):
        item=element("Thing","x",attributes=[
            {"Name":"Lang","Namespace":"","Value":"en"},
            {"Name":"Lang","Namespace":"","Value":"de"}])
        with self.assertRaises(mod.XMLProfileError):
            mod.profile_pubmed_nodes([[item]],source_sha256=HASH)

    def test_empty_or_incomplete_document_refused(self):
        with self.assertRaises(mod.XMLProfileError):
            mod.profile_pubmed_nodes([[]],source_sha256=HASH)
        with self.assertRaises(mod.XMLProfileError):
            mod.profile_pubmed_nodes([[{"Name":"Thing","Value":"x"}]],source_sha256=HASH)


if __name__=="__main__":
    unittest.main()
