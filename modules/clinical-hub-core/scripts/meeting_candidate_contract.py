"""Validate fictional candidate metadata and provenance; never read transcript text."""

from __future__ import annotations

from scripts.meeting_transcript_contract import _fixture_ref


_CATEGORIES = {"advice", "referral", "proposed_action", "candidate_decision", "dissent", "condition", "held_matter"}
_SPEAKERS = {"identified_fixture", "ambiguous", "unattributed"}
_AUTHORITY = {"unverified", "none"}
_DISPOSITIONS = {"pending", "held", "rejected_candidate", "amended_candidate"}
_MARKERS = {"dissent", "condition", "held"}
_MESSAGES = {
    "SOURCE_BINDING_INVALID": "Check the selected synthetic transcript artifact, revision and meeting binding against the existing human-reviewed notes/minutes.",
    "PASSAGE_REF_INVALID": "Check the candidate passage reference and time range against the selected transcript metadata.",
    "MISSING_REQUIRED_PASSAGE": "Review the required source passage refs in the existing manual notes route; structural omission does not prove a missed decision.",
    "UNSUPPORTED_CANDIDATE_REF": "Review unsupported candidate refs against the selected transcript metadata; no semantic support is established.",
    "CANDIDATE_SCHEMA_INVALID": "Correct the candidate metadata in the existing source-linked review route; no task or decision is issued.",
    "HISTORY_INVALID": "A candidate history link is missing, reused, stale or mismatched; preserve prior identities and dispositions.",
    "CONTENT_FIELD_REJECTED": "Remove transcript text or unknown content fields; this local validator accepts metadata only.",
}
_TOP_KEYS = {"meeting", "audience_revision", "transcript", "passages", "required_candidate_passage_refs", "candidate_set", "prior_sets"}
_MEETING_KEYS = {"meeting_ref", "occurrence_ref", "status"}
_TRANSCRIPT_KEYS = {"artifact_ref", "meeting_ref", "occurrence_ref", "revision", "content_hash", "metadata_state"}
_PASSAGE_KEYS = {"passage_ref", "meeting_ref", "occurrence_ref", "transcript_artifact_ref", "transcript_revision", "transcript_hash", "start_ms", "end_ms", "status"}
_SET_KEYS = {"artifact_ref", "revision", "meeting_ref", "occurrence_ref", "audience_revision", "source_refs", "supersedes_artifact_ref", "candidates"}
_CANDIDATE_KEYS = {"candidate_ref", "category", "source_spans", "speaker_state", "authority_state", "markers", "review_disposition", "supersedes_candidate_ref"}
_SPAN_KEYS = {"passage_ref", "start_ms", "end_ms"}
_PRIOR_SET_KEYS = {
    "artifact_ref", "revision", "meeting_ref", "occurrence_ref", "audience_revision",
    "transcript_artifact_ref", "transcript_revision", "transcript_hash", "candidate_dispositions",
}


def _result(
    codes: list[str],
    *,
    missing: list[str] | None = None,
    unsupported: list[str] | None = None,
    invalidated_prior_sets: list[str] | None = None,
    latest_prior_set_ref: str | None = None,
) -> dict:
    return {
        "state": "blocked" if codes else "fixture_metadata_consistent",
        "meaning": "structural metadata consistency only; no semantic support, complete extraction, authority or decision is established",
        "issues": [{"code": code, "explanation": _MESSAGES[code]} for code in codes],
        "structural_coverage": {
            "missing_required_passage_refs": missing or [],
            "unsupported_candidate_passage_refs": unsupported or [],
        },
        "invalidated_prior_set_refs": invalidated_prior_sets or [],
        "latest_prior_set_ref": latest_prior_set_ref,
        "candidate_state": "unissued_proposal",
        "owner_inferred": False,
        "due_date_inferred": False,
        "authority_inferred": False,
        "external_action_proposed": False,
        "manual_next_step": (
            "Stale prior reviews are invalidated: preserve their history, create new item/set refs, explicitly supersede the latest prior set, "
            "return candidates to pending, and use the existing human-reviewed manual notes/minutes route; urgent concerns do not wait."
            if invalidated_prior_sets
            else (
                f"Prior set {latest_prior_set_ref} is the latest history: preserve prior identities and dispositions, create new item/set refs, "
                "explicitly supersede this set, and use the existing human-reviewed manual notes/minutes route."
                if latest_prior_set_ref
                else "Use the existing human-reviewed manual notes/minutes route; urgent concerns do not wait for candidate generation."
            )
        ),
    }


def _dict_keys(value: object, allowed: set[str]) -> bool:
    return isinstance(value, dict) and set(value) <= allowed


def _integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _schema_ok(case: dict) -> bool:
    if not _dict_keys(case, _TOP_KEYS):
        return False
    if not _dict_keys(case.get("meeting"), _MEETING_KEYS) or not _dict_keys(case.get("transcript"), _TRANSCRIPT_KEYS):
        return False
    passages = case.get("passages")
    if not isinstance(passages, list) or any(not _dict_keys(row, _PASSAGE_KEYS) for row in passages):
        return False
    if not isinstance(case.get("required_candidate_passage_refs"), list):
        return False
    candidate_set = case.get("candidate_set")
    if not _dict_keys(candidate_set, _SET_KEYS) or not isinstance(candidate_set.get("source_refs"), list):
        return False
    candidates = candidate_set.get("candidates")
    if not isinstance(candidates, list):
        return False
    for candidate in candidates:
        if not _dict_keys(candidate, _CANDIDATE_KEYS) or not isinstance(candidate.get("source_spans"), list):
            return False
        if any(not _dict_keys(span, _SPAN_KEYS) for span in candidate["source_spans"]):
            return False
        if not isinstance(candidate.get("markers"), list):
            return False
    prior_sets = case.get("prior_sets", [])
    if not isinstance(prior_sets, list):
        return False
    for prior in prior_sets:
        if not _dict_keys(prior, _PRIOR_SET_KEYS) or not isinstance(prior.get("candidate_dispositions"), dict):
            return False
    return True


def validate_candidate_fixture(case: object) -> dict:
    """Check source references, categories, uncertainty and immutable proposal metadata."""
    if not isinstance(case, dict) or not _schema_ok(case):
        return _result(["CONTENT_FIELD_REJECTED"])

    meeting = case["meeting"]
    transcript = case["transcript"]
    candidate_set = case["candidate_set"]
    meeting_ref, occurrence_ref = meeting.get("meeting_ref"), meeting.get("occurrence_ref")
    transcript_ref = transcript.get("artifact_ref")
    if (
        not all(_fixture_ref(value) for value in (meeting_ref, occurrence_ref, case.get("audience_revision")))
        or meeting.get("status") != "confirmed_fixture"
        or transcript.get("metadata_state") != "fixture_metadata_consistent"
        or transcript.get("meeting_ref") != meeting_ref
        or transcript.get("occurrence_ref") != occurrence_ref
        or not all(_fixture_ref(transcript.get(k)) for k in ("artifact_ref", "revision", "content_hash"))
    ):
        return _result(["SOURCE_BINDING_INVALID"])
    if (
        candidate_set.get("meeting_ref") != meeting_ref
        or candidate_set.get("occurrence_ref") != occurrence_ref
        or candidate_set.get("audience_revision") != case.get("audience_revision")
        or candidate_set.get("source_refs") != [transcript_ref]
        or not _fixture_ref(candidate_set.get("artifact_ref"))
        or not _fixture_ref(candidate_set.get("revision"))
    ):
        return _result(["SOURCE_BINDING_INVALID"])

    passage_by_ref: dict[str, dict] = {}
    for passage in case["passages"]:
        ref = passage.get("passage_ref")
        if not _fixture_ref(ref) or ref in passage_by_ref:
            return _result(["SOURCE_BINDING_INVALID"])
        if (
            passage.get("meeting_ref") != meeting_ref
            or passage.get("occurrence_ref") != occurrence_ref
            or passage.get("transcript_artifact_ref") != transcript_ref
            or passage.get("transcript_revision") != transcript.get("revision")
            or passage.get("transcript_hash") != transcript.get("content_hash")
            or passage.get("status") != "fixture_present"
            or not _integer(passage.get("start_ms"))
            or not _integer(passage.get("end_ms"))
            or passage["start_ms"] < 0
            or passage["end_ms"] <= passage["start_ms"]
        ):
            return _result(["SOURCE_BINDING_INVALID"])
        passage_by_ref[ref] = passage

    prior_sets = case.get("prior_sets", [])
    prior_by_ref: dict[str, dict] = {}
    prior_candidates: dict[str, tuple[str, str]] = {}
    stale_prior_sets: list[str] = []
    for prior in prior_sets:
        ref = prior.get("artifact_ref")
        dispositions = prior.get("candidate_dispositions", {})
        prior_source = (
            prior.get("meeting_ref"), prior.get("occurrence_ref"), prior.get("audience_revision"),
            prior.get("transcript_artifact_ref"), prior.get("transcript_revision"), prior.get("transcript_hash"),
        )
        if (
            not _fixture_ref(ref)
            or ref in prior_by_ref
            or not _fixture_ref(prior.get("revision"))
            or not all(_fixture_ref(value) for value in prior_source)
            or prior.get("meeting_ref") != meeting_ref
            or prior.get("occurrence_ref") != occurrence_ref
        ):
            return _result(["HISTORY_INVALID"])
        if any(
            not _fixture_ref(candidate_ref)
            or not isinstance(state, str)
            or state not in _DISPOSITIONS
            for candidate_ref, state in dispositions.items()
        ):
            return _result(["HISTORY_INVALID"])
        if any(candidate_ref in prior_candidates for candidate_ref in dispositions):
            return _result(["HISTORY_INVALID"])
        prior_by_ref[ref] = prior
        prior_candidates.update({candidate_ref: (state, ref) for candidate_ref, state in dispositions.items()})
        current_source = (
            meeting_ref, occurrence_ref, case["audience_revision"], transcript_ref,
            transcript.get("revision"), transcript.get("content_hash"),
        )
        if prior_source != current_source:
            stale_prior_sets.append(ref)
    if candidate_set.get("artifact_ref") in prior_by_ref or candidate_set.get("artifact_ref") == transcript_ref:
        return _result(
            ["HISTORY_INVALID"],
            invalidated_prior_sets=stale_prior_sets,
            latest_prior_set_ref=list(prior_by_ref)[-1] if prior_by_ref else None,
        )
    supersedes_set = candidate_set.get("supersedes_artifact_ref")
    if supersedes_set is not None and (not _fixture_ref(supersedes_set) or supersedes_set not in prior_by_ref):
        return _result(
            ["HISTORY_INVALID"],
            invalidated_prior_sets=stale_prior_sets,
            latest_prior_set_ref=list(prior_by_ref)[-1] if prior_by_ref else None,
        )
    if prior_by_ref and supersedes_set != list(prior_by_ref)[-1]:
        return _result(
            ["HISTORY_INVALID"],
            invalidated_prior_sets=stale_prior_sets,
            latest_prior_set_ref=list(prior_by_ref)[-1],
        )

    candidate_refs: set[str] = set()
    cited_refs: set[str] = set()
    unsupported: list[str] = []
    candidate_errors: list[str] = []
    for candidate in candidate_set["candidates"]:
        ref = candidate.get("candidate_ref")
        if not _fixture_ref(ref) or ref in candidate_refs or ref in prior_candidates:
            candidate_errors.append("HISTORY_INVALID")
            continue
        candidate_refs.add(ref)
        if (
            not isinstance(candidate.get("category"), str)
            or candidate.get("category") not in _CATEGORIES
            or not isinstance(candidate.get("speaker_state"), str)
            or candidate.get("speaker_state") not in _SPEAKERS
            or not isinstance(candidate.get("authority_state"), str)
            or candidate.get("authority_state") not in _AUTHORITY
            or not isinstance(candidate.get("review_disposition"), str)
            or candidate.get("review_disposition") not in _DISPOSITIONS
            or any(not isinstance(marker, str) or marker not in _MARKERS for marker in candidate.get("markers", []))
        ):
            candidate_errors.append("CANDIDATE_SCHEMA_INVALID")
        marker_requirements = {"dissent": "dissent", "condition": "condition", "held_matter": "held"}
        category = candidate.get("category")
        required_marker = marker_requirements.get(category) if isinstance(category, str) else None
        if required_marker and required_marker not in candidate.get("markers", []):
            candidate_errors.append("CANDIDATE_SCHEMA_INVALID")
        disposition = candidate.get("review_disposition")
        old_candidate = candidate.get("supersedes_candidate_ref")
        if disposition == "amended_candidate" or (disposition == "pending" and old_candidate is not None):
            old_entry = prior_candidates.get(old_candidate) if _fixture_ref(old_candidate) else None
            if not old_entry or old_entry[1] != supersedes_set or not supersedes_set:
                candidate_errors.append("HISTORY_INVALID")
        elif old_candidate is not None:
            candidate_errors.append("HISTORY_INVALID")

        spans = candidate.get("source_spans", [])
        if not spans:
            candidate_errors.append("PASSAGE_REF_INVALID")
        for span in spans:
            passage_ref = span.get("passage_ref")
            start, end = span.get("start_ms"), span.get("end_ms")
            if not _fixture_ref(passage_ref):
                candidate_errors.append("PASSAGE_REF_INVALID")
                continue
            if passage_ref not in passage_by_ref:
                unsupported.append(passage_ref)
                cited_refs.add(passage_ref)
                continue
            passage = passage_by_ref[passage_ref]
            if not _integer(start) or not _integer(end) or start < passage["start_ms"] or end > passage["end_ms"] or end <= start:
                candidate_errors.append("PASSAGE_REF_INVALID")
            cited_refs.add(passage_ref)

    required = case.get("required_candidate_passage_refs", [])
    if any(not _fixture_ref(ref) for ref in required) or len(set(required)) != len(required):
        return _result(["SOURCE_BINDING_INVALID"])
    if any(ref not in passage_by_ref for ref in required):
        return _result(["SOURCE_BINDING_INVALID"])
    missing = sorted(set(required) - cited_refs)
    codes = list(dict.fromkeys(candidate_errors))
    if missing:
        codes.append("MISSING_REQUIRED_PASSAGE")
    if unsupported:
        codes.append("UNSUPPORTED_CANDIDATE_REF")
    if stale_prior_sets and any(
        candidate.get("review_disposition") != "pending" for candidate in candidate_set["candidates"]
    ):
        codes.append("HISTORY_INVALID")
    return _result(
        codes,
        missing=missing,
        unsupported=sorted(set(unsupported)),
        invalidated_prior_sets=stale_prior_sets,
        latest_prior_set_ref=list(prior_by_ref)[-1] if prior_by_ref else None,
    )
