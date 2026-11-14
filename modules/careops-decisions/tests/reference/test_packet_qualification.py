"""Synthetic tests for standalone packet qualification and fail-closed authority."""
import hashlib
import unittest
from dataclasses import replace
from datetime import UTC, datetime, timedelta

from reference.governance_packet import AgendaItem, DecisionRecord, GovernancePacket, MinutesRevision
from reference.packet_qualification import (
    AuthorityEvidence,
    AuthorityStatus,
    PacketStatus,
    evaluate_authority_boundary,
    qualify_standalone_packet,
)


class StandalonePacketQualificationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 11, 14, 8, tzinfo=UTC)
        minutes = MinutesRevision("minutes-syn-1", "meeting-syn-1", 1, "a" * 64, False)
        agenda = AgendaItem("agenda-syn-1", "meeting-syn-1", 1)
        decision = DecisionRecord("decision-syn-1", "agenda-syn-1", "minutes-syn-1", 1)
        self.packet = GovernancePacket("meeting-syn-1", (agenda,), (minutes,), (decision,), ())
        self.source = b'{"fixture":"synthetic-packet","version":"0.1.0"}'
        self.digest = hashlib.sha256(self.source).hexdigest()
        authority_bytes = b'{"fixture":"synthetic-authority","version":"v1"}'
        self.authority = AuthorityEvidence(
            state="qualified",
            authority_reference="test:authority-reference-01",
            mapping_version="test:mapping-v1",
            source_sha256=hashlib.sha256(authority_bytes).hexdigest(),
            source_bytes=authority_bytes,
            effective_from=self.now - timedelta(days=1),
            effective_until=self.now + timedelta(days=1),
        )

    def qualify(self, **changes):
        args = {
            "source_bytes": self.source,
            "claimed_source_sha256": self.digest,
            "contract_version": "0.1.0",
            "expected_contract_version": "0.1.0",
            "authority": self.authority,
            "expected_authority_mapping_version": "test:mapping-v1",
            "now": self.now,
        }
        args.update(changes)
        return qualify_standalone_packet(self.packet, **args)

    def test_standalone_packet_qualifies_without_optional_process_input(self):
        result = self.qualify()
        self.assertEqual(result.status, PacketStatus.QUALIFIED)
        self.assertEqual(result.authority_status, AuthorityStatus.QUALIFIED)

    def test_existing_packet_identity_semantics_remain_authoritative(self):
        invalid = replace(self.packet, decisions=(
            DecisionRecord("decision-syn-2", "missing-agenda", "minutes-syn-1", 1),
        ))
        result = self.qualify_packet(invalid)
        self.assertEqual(result.status, PacketStatus.INVALID_PACKET)

    def qualify_packet(self, packet):
        return qualify_standalone_packet(
            packet,
            source_bytes=self.source,
            claimed_source_sha256=self.digest,
            contract_version="0.1.0",
            expected_contract_version="0.1.0",
            authority=self.authority,
            expected_authority_mapping_version="test:mapping-v1",
            now=self.now,
        )

    def test_missing_source_unsupported_contract_and_hash_mismatch_hold(self):
        self.assertEqual(self.qualify(source_bytes=b"").status, PacketStatus.MISSING_SOURCE)
        self.assertEqual(self.qualify(contract_version="9.9.9").status, PacketStatus.UNSUPPORTED_CONTRACT)
        self.assertEqual(self.qualify(claimed_source_sha256="0" * 64).status, PacketStatus.SOURCE_HASH_MISMATCH)

    def test_missing_authority_holds_packet(self):
        result = self.qualify(authority=None)
        self.assertEqual(result.status, PacketStatus.AUTHORITY_HELD)
        self.assertEqual(result.authority_status, AuthorityStatus.MISSING)

    def test_only_exact_qualified_state_is_accepted(self):
        for state in ("approved", "permitted", "active", "pending", "revoked", "ambiguous", "unknown", ""):
            with self.subTest(state=state):
                result = self.qualify(authority=replace(self.authority, state=state))
                self.assertEqual(result.status, PacketStatus.AUTHORITY_HELD)
                self.assertEqual(result.authority_status, AuthorityStatus.UNSUPPORTED_STATE)

    def test_mapping_mismatch_and_unverifiable_source_hold(self):
        self.assertEqual(
            self.qualify(authority=replace(self.authority, mapping_version="test:other")).authority_status,
            AuthorityStatus.MAPPING_MISMATCH,
        )
        self.assertEqual(
            self.qualify(authority=replace(self.authority, source_sha256="not-a-digest")).authority_status,
            AuthorityStatus.SOURCE_UNVERIFIED,
        )
        self.assertEqual(
            self.qualify(authority=replace(self.authority, authority_reference=" ")).authority_status,
            AuthorityStatus.SOURCE_UNVERIFIED,
        )
        self.assertEqual(
            self.qualify(authority=replace(self.authority, source_bytes=b'{"tampered":true}')).authority_status,
            AuthorityStatus.SOURCE_UNVERIFIED,
        )

    def test_effective_window_is_half_open_and_fails_closed(self):
        before = replace(self.authority, effective_from=self.now + timedelta(seconds=1))
        after = replace(self.authority, effective_until=self.now)
        self.assertEqual(evaluate_authority_boundary(before, expected_mapping_version="test:mapping-v1", now=self.now),
                         AuthorityStatus.NOT_YET_EFFECTIVE)
        self.assertEqual(evaluate_authority_boundary(after, expected_mapping_version="test:mapping-v1", now=self.now),
                         AuthorityStatus.EXPIRED)
        self.assertEqual(
            evaluate_authority_boundary(self.authority, expected_mapping_version="test:mapping-v1", now=self.now),
            AuthorityStatus.QUALIFIED,
        )

    def test_naive_or_invalid_authority_period_is_not_qualified(self):
        naive = replace(self.authority, effective_from=datetime(2026, 11, 13))
        self.assertEqual(
            evaluate_authority_boundary(naive, expected_mapping_version="test:mapping-v1", now=self.now),
            AuthorityStatus.SOURCE_UNVERIFIED,
        )
        reversed_period = replace(self.authority, effective_until=self.authority.effective_from)
        self.assertEqual(
            evaluate_authority_boundary(reversed_period, expected_mapping_version="test:mapping-v1", now=self.now),
            AuthorityStatus.SOURCE_UNVERIFIED,
        )

    def test_naive_clock_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "timezone-aware"):
            evaluate_authority_boundary(
                self.authority,
                expected_mapping_version="test:mapping-v1",
                now=datetime(2026, 11, 14),
            )


if __name__ == "__main__":
    unittest.main()
