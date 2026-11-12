"""Source-only contract parity for all retained data-use artifacts.

Uses stdlib for structural parity; Draft202012 optional when installed.
"""
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]


def load(name):
    path=ROOT/"portfolio-scripts"/(name+".py")
    spec=spec_from_file_location(name,path)
    mod=module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


profiler=load("rims_retained_field_utilisation")
rollup=load("rims_coverage_rollup")
ADOPTION=json.loads((ROOT/"portfolio/rims/existing-source-adoption.json").read_text())


class SourceContractTests(unittest.TestCase):
    def test_full_source_catalogue_and_task_register(self):
        sources=ADOPTION["sources"]
        tasks=json.loads((ROOT/"conductor/tracks/rims_full_data_utilisation_20261110/source-tasks.json").read_text())
        names=[row["source"] for row in sources]
        self.assertEqual(len(names),17)
        self.assertEqual(len(set(names)),17)
        self.assertEqual(tasks["task_count"],136)
        self.assertEqual(len({row["id"] for row in tasks["tasks"]}),136)
        self.assertEqual({row["source"] for row in tasks["tasks"]},set(names))
        self.assertTrue(all(row["new_acquisition_authorised"] is False for row in sources))

    def test_profile_keys_match_strict_contract(self):
        payload=profiler.profile("PubMed",[{"a": 1}],
                                 source_sha256="1"*64)
        path=ROOT/"portfolio/rims/contracts/retained-field-profile.schema.json"
        schema=json.loads(path.read_text())
        self.assertEqual(set(payload),set(schema["required"]))
        self.assertEqual(set(payload["fields"][0]),set(
            schema["properties"]["fields"]["items"]["required"]))
        self.assertFalse(payload["source_digest_independently_verified"])
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            return
        Draft202012Validator(schema).validate(payload)

    def test_utilisation_keys_match_strict_contract(self):
        profile=profiler.profile("PubMed",[{"a":1}],source_sha256="1"*64)
        usage=profiler.utilisation(profile,[{
            "source_path":"/a","disposition":"mapped","consumer":"silver",
            "artifact_id":"fictional","artifact_revision":"v1",
            "target_field":"A",
        }])
        schema=json.loads((ROOT/"portfolio/rims/contracts/retained-field-utilisation.schema.json").read_text())
        self.assertEqual(set(usage),set(schema["required"]))
        self.assertTrue(usage["all_paths_used"])
        self.assertFalse(usage["consumer_binding_native_verified"])
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            return
        Draft202012Validator(schema).validate(usage)

    def test_rollup_does_not_claim_native_or_fresh_data(self):
        result=rollup.rollup(ADOPTION,[])
        self.assertEqual(result["sources_in_catalogue"],17)
        self.assertEqual(result["sources_with_declared_profiles"],0)
        self.assertEqual(result["sources_with_verified_profile_input"],0)
        self.assertEqual(len(result["sources_still_unprofiled"]),17)
        self.assertFalse(result["full_field_utilisation_proven"])

if __name__=="__main__":
    unittest.main()
