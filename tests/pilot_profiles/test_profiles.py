"""No-admin pilot preflight: unknown is not permission; green is not authority."""
import unittest
from dataclasses import fields, replace
from typing import cast

from scripts.pilot_profiles import REQUIREMENTS, Mode, Observations, Readiness, assess


def ready(mode: Mode) -> Observations:
    return Observations(**dict.fromkeys(REQUIREMENTS[mode], True))


class ProfileTests(unittest.TestCase):
    def test_defaults_never_claim_ready(self) -> None:
        for mode in Mode:
            result = assess(mode, Observations())
            self.assertEqual(result.readiness, Readiness.UNVERIFIED)
            self.assertIsNone(result.fallback)
            self.assertEqual(result.unknown, REQUIREMENTS[mode])

    def test_lists_does_not_need_flow_or_native_roles(self) -> None:
        result = assess(Mode.LISTS_REHEARSAL, ready(Mode.LISTS_REHEARSAL))
        self.assertEqual(result.readiness, Readiness.SYNTHETIC_READY)
        self.assertEqual(result.data_boundary, "synthetic-only")
        self.assertEqual((result.denied, result.unknown), ((), ()))

    def test_standard_flow_does_not_need_admin_registration_or_dataverse(self) -> None:
        result = assess(Mode.STANDARD_FLOW_PILOT, ready(Mode.STANDARD_FLOW_PILOT))
        self.assertEqual(result.readiness, Readiness.SYNTHETIC_READY)
        self.assertFalse(result.requires_tenant_administrator)
        self.assertFalse(result.requires_new_entra_application)

    def test_each_denied_or_unknown_requirement_stops_readiness(self) -> None:
        for mode in Mode:
            for key in REQUIREMENTS[mode]:
                for value, expected in ((False, Readiness.BLOCKED), (None, Readiness.UNVERIFIED)):
                    with self.subTest(mode=mode, key=key, value=value):
                        result = assess(mode, replace(ready(mode), **{key: value}))
                        self.assertEqual(result.readiness, expected)
                        self.assertIn(key, result.denied if value is False else result.unknown)

    def test_blocked_flow_can_fall_back_to_verified_lists(self) -> None:
        value = replace(ready(Mode.STANDARD_FLOW_PILOT), flow_maker=False)
        self.assertEqual(assess(Mode.STANDARD_FLOW_PILOT, value).fallback, Mode.LISTS_REHEARSAL)

    def test_unknown_flow_can_fall_back_without_claiming_flow_permission(self) -> None:
        result = assess(Mode.STANDARD_FLOW_PILOT, ready(Mode.LISTS_REHEARSAL))
        self.assertEqual(result.readiness, Readiness.UNVERIFIED)
        self.assertEqual(result.fallback, Mode.LISTS_REHEARSAL)

    def test_denied_and_unknown_are_both_retained(self) -> None:
        result = assess(Mode.STANDARD_FLOW_PILOT, Observations(work_account=False))
        self.assertEqual(result.denied, ("work_account",))
        self.assertTrue(result.unknown)
        self.assertEqual(result.readiness, Readiness.BLOCKED)

    def test_native_ready_still_cannot_activate(self) -> None:
        result = assess(Mode.DATAVERSE_TARGET, ready(Mode.DATAVERSE_TARGET))
        self.assertEqual(result.readiness, Readiness.DEPLOYMENT_REVIEW)
        self.assertEqual(result.data_boundary, "separate-production-release-required")
        self.assertFalse(result.authoritative_writes)

    def test_all_modes_preserve_no_side_effects(self) -> None:
        for mode in Mode:
            result = assess(mode, ready(mode))
            self.assertFalse(result.external_communications)
            self.assertFalse(result.authoritative_writes)
            self.assertFalse(result.requires_new_entra_application)

    def test_no_truth_coercion_in_any_observation(self) -> None:
        invalid: tuple[object, ...] = (0, 1, "true", "false", [], {})
        for field in fields(Observations):
            for value in invalid:
                with self.subTest(field=field.name, value=value), self.assertRaises(ValueError):
                    Observations(**{field.name: cast(bool, value)})

    def test_invalid_inputs_fail_closed(self) -> None:
        for mode, value in ((cast(Mode, "m365-lists-rehearsal"), Observations()),
                            (Mode.LISTS_REHEARSAL, cast(Observations, {}))):
            with self.assertRaises(ValueError):
                assess(mode, value)

    def test_production_blocker_not_transferred_to_synthetic_pilot(self) -> None:
        value = replace(ready(Mode.LISTS_REHEARSAL), signed_authority_verified=False,
                        operational_acceptance=False)
        self.assertEqual(assess(Mode.LISTS_REHEARSAL, value).readiness, Readiness.SYNTHETIC_READY)
        self.assertEqual(assess(Mode.DATAVERSE_TARGET, value).fallback, Mode.LISTS_REHEARSAL)

    def test_builtin_flow_has_no_list_or_connector_prerequisite(self) -> None:
        value = replace(ready(Mode.FLOW_REHEARSAL), lists_permitted=False,
                        standard_sharepoint_connector=False)
        result = assess(Mode.FLOW_REHEARSAL, value)
        self.assertEqual(result.readiness, Readiness.SYNTHETIC_READY)
        self.assertEqual((result.denied, result.unknown), ((), ()))

    def test_flow_rehearsal_is_alternative_when_lists_are_denied(self) -> None:
        value = replace(ready(Mode.FLOW_REHEARSAL), lists_permitted=False)
        for mode in (Mode.LISTS_REHEARSAL, Mode.STANDARD_FLOW_PILOT, Mode.DATAVERSE_TARGET):
            result = assess(mode, value)
            self.assertEqual(result.fallback, Mode.FLOW_REHEARSAL)
            self.assertNotEqual(result.readiness, Readiness.SYNTHETIC_READY)

    def test_unknown_flow_policy_cannot_be_bypassed_via_fallback(self) -> None:
        value = Observations(work_account=True, flow_maker=True, lists_permitted=False)
        for mode in Mode:
            result = assess(mode, value)
            self.assertIsNone(result.fallback)
            self.assertNotEqual(result.readiness, Readiness.SYNTHETIC_READY)
