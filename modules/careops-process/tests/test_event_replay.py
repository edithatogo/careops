# Copyright (c) 2026 CareOps contributors
# SPDX-License-Identifier: Apache-2.0

"""Offline fictional replay, late-arrival and deletion regression cases."""

from copy import deepcopy
from datetime import UTC, datetime
from itertools import permutations

import pytest

from careops_process.ingest import facts_to_ocel
from careops_process.ocel import ContractError, OcelLog, pseudonymize
from careops_process.pipeline import run_pipeline
from careops_process.reliability import IngestionCheckpoint

OBSERVED = datetime(2026, 1, 3, tzinfo=UTC)


def fictional_facts() -> list[dict[str, object]]:
    """Return distinct fictional events, including a timestamp tie."""
    return [
        {
            "id": f"fictional-event-{index}",
            "activity": activity,
            "timestamp_utc": timestamp,
            "source_system": "fictional-provider",
            "object_ids": [object_id],
        }
        for index, (activity, timestamp, object_id) in enumerate(
            [
                ("received", "2026-01-01T00:00:00Z", "fictional-object-1"),
                ("checked", "2026-01-02T00:00:00Z", "fictional-object-1"),
                ("received", "2026-01-02T00:00:00Z", "fictional-object-2"),
            ]
        )
    ]


def convert(facts: list[dict[str, object]]) -> OcelLog:
    """Use the existing minimized adapter without any connector or source write."""
    return facts_to_ocel(
        facts,
        log_id="fictional-replay",
        schema_version="1.0.0",
        pseudonym_secret="fictional-replay-only",  # noqa: S106
    )


def test_late_arrival_permutations_have_identical_output_and_stable_ids() -> None:
    """Arrival order changes neither serialized facts nor pseudonymous identity."""
    facts = fictional_facts()
    original = deepcopy(facts)
    expected = convert(facts).model_dump(mode="json")
    assert {event.event_id for event in convert(facts).events} == {
        pseudonymize(f"event:{fact['id']}", secret="fictional-replay-only")  # noqa: S106
        for fact in facts
    }
    for ordering in permutations(facts):
        replay = convert(list(ordering))
        assert replay.model_dump(mode="json") == expected
    assert facts == original


def test_repeated_tombstone_does_not_evict_a_retained_deletion() -> None:
    """Replay of one deletion must not consume a second retention slot."""
    checkpoint = IngestionCheckpoint(max_tracked_ids=2)
    checkpoint.tombstone("fictional-a")
    checkpoint.tombstone("fictional-a")
    checkpoint.tombstone("fictional-b")
    assert not checkpoint.accept("fictional-a", OBSERVED)
    assert not checkpoint.accept("fictional-b", OBSERVED)


def test_reaccepted_id_survives_eviction_of_its_old_acceptance() -> None:
    """An old queue entry must not delete a new acceptance of the same identity."""
    checkpoint = IngestionCheckpoint(max_tracked_ids=2)
    checkpoint.accept("fictional-a", OBSERVED)
    checkpoint.accept("fictional-b", OBSERVED)
    for fact_id in ("fictional-a", "fictional-c", "fictional-d"):
        checkpoint.tombstone(fact_id)
    # A's tombstone is now outside the explicit count-bounded retention window.
    assert checkpoint.accept("fictional-a", OBSERVED)
    assert "fictional-a" in checkpoint.accepted_fact_ids
    assert not checkpoint.accept("fictional-a", OBSERVED)


@pytest.mark.parametrize("empty", ["", "   "])
@pytest.mark.parametrize("field", ["id", "object_ids"])
def test_empty_identity_cannot_be_hidden_by_pseudonymization(field: str, empty: str) -> None:
    """Missing identity remains an error rather than a valid-looking digest."""
    fact = fictional_facts()[0]
    fact[field] = [empty] if field == "object_ids" else empty
    with pytest.raises(ValueError, match="non-empty"):
        convert([fact])


def test_duplicate_batch_fails_closed_without_mutating_input() -> None:
    """Exact and conflicting duplicates require checkpoint reconciliation."""
    for activity in ("received", "conflicting_activity"):
        facts = fictional_facts()
        facts.append({**facts[0], "activity": activity})
        original = deepcopy(facts)
        with pytest.raises(ContractError, match="unique"):
            convert(facts)
        assert facts == original


@pytest.mark.parametrize("source", [None, "", "   "])
def test_missing_provider_is_rejected(source: str | None) -> None:
    """No provider is inferred for an unbound source fact."""
    fact = fictional_facts()[0]
    if source is None:
        del fact["source_system"]
    else:
        fact["source_system"] = source
    with pytest.raises(ValueError, match="source_system"):
        convert([fact])


def test_checkpoint_replay_and_missing_optional_provider_are_source_write_free() -> None:
    """Duplicates/deletions filter out locally; missing peers add no fake events."""
    checkpoint = IngestionCheckpoint()
    facts = fictional_facts()
    original = deepcopy(facts)
    checkpoint.tombstone(str(facts[2]["id"]))
    selected = [fact for fact in facts if checkpoint.accept(str(fact["id"]), OBSERVED)]
    assert not any(checkpoint.accept(str(fact["id"]), OBSERVED) for fact in facts)
    assert checkpoint.watermark_utc == OBSERVED
    assert checkpoint.accept("fictional-late", datetime(2026, 1, 1, tzinfo=UTC))
    assert checkpoint.watermark_utc == OBSERVED
    result = run_pipeline(
        selected,
        log_id="fictional-replay",
        schema_version="1.0.0",
        pseudonym_secret="fictional-replay-only",  # noqa: S106
        generated_at_utc=OBSERVED,
        minimum_cohort_size=1,
    )
    assert len(result.log.events) == len(selected)
    assert {event.source_system for event in result.log.events} == {"fictional-provider"}
    assert "fictional-object" not in result.log.model_dump_json()
    assert facts == original
