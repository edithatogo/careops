# Copyright (c) 2026 CareOps contributors
# SPDX-License-Identifier: Apache-2.0

"""Deterministic, metadata-only RFC 5322 email observations.

The parser reads headers only. Message bodies, addresses, subjects, attachment
payloads and raw message identifiers are never returned or persisted.
"""

from __future__ import annotations

import hashlib
import hmac
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from email import policy
from email.parser import BytesParser
from email.utils import parsedate_to_datetime

_MESSAGE_ID = re.compile(r"<([^<>\s]+@[^<>\s]+)>")
_DEFAULT_MAX_BYTES = 1_048_576
_MIN_SECRET_BYTES = 32
_KEY_DIGEST_HEX_LENGTH = 32


class EmailObservationError(ValueError):
    """Raised when a source message cannot be safely observed."""


@dataclass(frozen=True, slots=True)
class EmailObservation:
    """Immutable, privacy-minimized metadata for one observed email."""

    message_key: str
    conversation_key: str
    sent_at_utc: datetime | None
    observed_at_utc: datetime
    source_digest: str

    @property
    def object_ids(self) -> tuple[str, str]:
        """Return stable message and conversation object identities."""
        return (f"message:{self.message_key}", f"conversation:{self.conversation_key}")

    def to_acquisition_fact(self) -> dict[str, object]:
        """Project the observation into the existing minimized acquisition contract."""
        timestamp = self.observed_at_utc.isoformat(timespec="seconds").replace("+00:00", "Z")
        return {
            "id": self.message_key,
            "activity": "message_observed",
            "timestamp_utc": timestamp,
            "source_system": "eml_import",
            "object_ids": list(self.object_ids),
        }


def _key(secret: bytes, namespace: str, value: str) -> str:
    digest = hmac.new(secret, f"{namespace}:{value}".encode(), hashlib.sha256).hexdigest()
    return digest[:_KEY_DIGEST_HEX_LENGTH]


def _message_ids(value: object) -> list[str]:
    if not isinstance(value, str):
        return []
    return [match.group(1) for match in _MESSAGE_ID.finditer(value)]


def _sent_at(value: object) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = parsedate_to_datetime(value)
    except TypeError, ValueError, OverflowError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed.astimezone(UTC)


def parse_eml_observation(
    raw_message: bytes,
    *,
    pseudonym_secret: str,
    observed_at: datetime,
    max_bytes: int = _DEFAULT_MAX_BYTES,
) -> EmailObservation:
    """Parse only RFC 5322 headers into deterministic, minimized metadata.

    ``observed_at`` is the caller-supplied acquisition clock and remains distinct
    from the optional sender-asserted ``Date`` header. Missing or malformed
    Message-ID values fall back to a keyed digest of the exact source bytes.
    Thread identity uses the earliest valid References identifier, then
    In-Reply-To, then the message's own identifier.
    """
    if not raw_message:
        message = "source message must not be empty"
        raise EmailObservationError(message)
    if max_bytes <= 0 or len(raw_message) > max_bytes:
        message = "source message exceeds the permitted size"
        raise EmailObservationError(message)
    if len(pseudonym_secret.encode()) < _MIN_SECRET_BYTES:
        message = "pseudonymization secret must contain at least 32 bytes"
        raise EmailObservationError(message)
    if observed_at.tzinfo is None or observed_at.utcoffset() is None:
        message = "observed_at must include an explicit timezone"
        raise EmailObservationError(message)

    secret = pseudonym_secret.encode()
    observed_utc = observed_at.astimezone(UTC)
    try:
        message = BytesParser(policy=policy.default).parsebytes(raw_message, headersonly=True)
    except (AttributeError, TypeError, ValueError, UnicodeError) as error:
        message = "source message headers could not be parsed"
        raise EmailObservationError(message) from error
    if message.defects:
        message = "source message contains malformed headers"
        raise EmailObservationError(message)

    identifiers = _message_ids(message.get("Message-ID"))
    references = _message_ids(message.get("References"))
    in_reply_to = _message_ids(message.get("In-Reply-To"))
    source_identity = (
        identifiers[0]
        if identifiers
        else hmac.new(secret, b"source-bytes:" + raw_message, hashlib.sha256).hexdigest()
    )
    thread_identity = (references or in_reply_to or [source_identity])[0]

    return EmailObservation(
        message_key=f"msg_{_key(secret, 'message', source_identity)}",
        conversation_key=f"conv_{_key(secret, 'conversation', thread_identity)}",
        sent_at_utc=_sent_at(message.get("Date")),
        observed_at_utc=observed_utc,
        source_digest=_key(secret, "source", hashlib.sha256(raw_message).hexdigest()),
    )
