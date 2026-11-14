# Copyright (c) 2026 CareOps contributors
# SPDX-License-Identifier: Apache-2.0

"""Synthetic tests for metadata-only RFC 5322 email observation."""

from datetime import UTC, datetime
from pathlib import Path

import pytest

from careops_process.email_observation import (
    EmailObservationError,
    parse_eml_observation,
)

FIXTURES = Path(__file__).parent / "fixtures" / "email"
TEST_KEY = "synthetic-test-secret-with-at-least-32-bytes"
OTHER_TEST_KEY = "another synthetic secret of 32 bytes"
SHORT_TEST_KEY = "short"
OBSERVED_AT = datetime(2026, 11, 4, 1, 0, tzinfo=UTC)


def test_reply_preserves_thread_identity_without_content_or_addresses() -> None:
    """A reply links to its reference root while output excludes narrative and PII."""
    raw = (FIXTURES / "thread-reply.eml").read_bytes()

    observation = parse_eml_observation(raw, pseudonym_secret=TEST_KEY, observed_at=OBSERVED_AT)

    assert observation.sent_at_utc == datetime(2026, 11, 2, 23, 15, tzinfo=UTC)
    assert observation.observed_at_utc == OBSERVED_AT
    assert observation.object_ids == (
        f"message:{observation.message_key}",
        f"conversation:{observation.conversation_key}",
    )
    serialized = repr(observation).lower()
    prohibited_values = (
        "sender@example.invalid",
        "recipient@example.invalid",
        "protected narrative",
        "body sentinel",
    )
    for prohibited in prohibited_values:
        assert prohibited not in serialized
    fact = observation.to_acquisition_fact()
    assert fact == {
        "id": observation.message_key,
        "activity": "message_observed",
        "timestamp_utc": "2026-11-04T01:00:00Z",
        "source_system": "eml_import",
        "object_ids": list(observation.object_ids),
    }


def test_same_message_and_secret_produce_deterministic_observation() -> None:
    """Stable HMAC identities make unchanged offline imports replayable."""
    raw = (FIXTURES / "thread-reply.eml").read_bytes()

    first = parse_eml_observation(raw, pseudonym_secret=TEST_KEY, observed_at=OBSERVED_AT)
    second = parse_eml_observation(raw, pseudonym_secret=TEST_KEY, observed_at=OBSERVED_AT)

    assert first == second


def test_identity_is_not_linkable_across_secrets() -> None:
    """A different local secret produces unrelated pseudonymous identities."""
    raw = (FIXTURES / "thread-reply.eml").read_bytes()

    first = parse_eml_observation(raw, pseudonym_secret=TEST_KEY, observed_at=OBSERVED_AT)
    second = parse_eml_observation(raw, pseudonym_secret=OTHER_TEST_KEY, observed_at=OBSERVED_AT)

    assert first.message_key != second.message_key
    assert first.conversation_key != second.conversation_key
    assert first.source_digest != second.source_digest


def test_missing_message_id_uses_keyed_content_identity() -> None:
    """A message without Message-ID still has deterministic private identity."""
    raw = b"Date: Tue, 03 Nov 2026 10:15:00 +0000\r\nSubject: synthetic\r\n\r\nbody\r\n"

    first = parse_eml_observation(raw, pseudonym_secret=TEST_KEY, observed_at=OBSERVED_AT)
    second = parse_eml_observation(raw, pseudonym_secret=TEST_KEY, observed_at=OBSERVED_AT)

    assert first.message_key == second.message_key
    assert first.conversation_key.startswith("conv_")


def test_missing_or_invalid_date_uses_observation_time() -> None:
    """Missing or invalid Date is not fabricated; observed time remains explicit."""
    raw = b"Message-ID: <no-date@example.invalid>\r\nDate: not-a-date\r\n\r\nbody"

    observation = parse_eml_observation(raw, pseudonym_secret=TEST_KEY, observed_at=OBSERVED_AT)

    assert observation.sent_at_utc is None
    assert observation.observed_at_utc == OBSERVED_AT


def test_rejects_naive_observation_time() -> None:
    """The source observation clock must carry an explicit timezone."""
    raw = (FIXTURES / "root.eml").read_bytes()

    with pytest.raises(EmailObservationError, match="timezone"):
        parse_eml_observation(
            raw, pseudonym_secret=TEST_KEY, observed_at=datetime.fromisoformat("2026-11-04")
        )


def test_rejects_short_secret_and_oversized_source() -> None:
    """Identity derivation and bounded parsing fail closed."""
    raw = (FIXTURES / "root.eml").read_bytes()

    with pytest.raises(EmailObservationError, match="32 bytes"):
        parse_eml_observation(raw, pseudonym_secret=SHORT_TEST_KEY, observed_at=OBSERVED_AT)
    with pytest.raises(EmailObservationError, match="size"):
        parse_eml_observation(raw, pseudonym_secret=TEST_KEY, observed_at=OBSERVED_AT, max_bytes=8)


def test_rejects_non_bytes_input() -> None:
    """The parser accepts source bytes only, not already-decoded narrative."""
    with pytest.raises(EmailObservationError, match="bytes"):
        parse_eml_observation("From: somebody", pseudonym_secret=TEST_KEY, observed_at=OBSERVED_AT)  # type: ignore[arg-type]


def test_rejects_empty_source_and_malformed_headers() -> None:
    """Empty and structurally malformed source messages fail closed."""
    with pytest.raises(EmailObservationError, match="empty"):
        parse_eml_observation(b"", pseudonym_secret=TEST_KEY, observed_at=OBSERVED_AT)
    malformed = b"This is not a header\r\nMessage-ID: <bad@example.invalid>\r\n\r\nbody"
    with pytest.raises(EmailObservationError, match="malformed"):
        parse_eml_observation(malformed, pseudonym_secret=TEST_KEY, observed_at=OBSERVED_AT)
