"""Validate fictional recording/transcript metadata without touching media.

A pass means only that the invented fixture metadata is internally consistent.
It does not establish real authority, consent, source authenticity or quality.
"""

from __future__ import annotations


_AUTHORITY = {
    "capture": "capture",
    "processing": "transcript_processing",
    "audience": "permitted_audience",
    "retention": "retention",
}
_SUPPORTED_FIXTURE_FORMATS = {"fixture_pcm16", "fixture_opus"}
_MESSAGES = {
    "MEETING_UNVERIFIED": ("The synthetic meeting occurrence is not confirmed or bound.", "Continue with human-reviewed manual notes/minutes; do not record or process real media until the route, authority and records controls are established."),
    "AUTHORITY_FIXTURE_MISSING": ("A required synthetic authority declaration is missing or unresolved.", "Keep media processing stopped and use human-reviewed manual notes/minutes until the route, authority and records controls are established."),
    "AUTHORITY_FIXTURE_INVALID": ("A synthetic authority declaration is mismatched, reused, or inactive.", "Keep media processing stopped and use human-reviewed manual notes/minutes until the route, authority and records controls are established."),
    "ARTIFACT_REF_INVALID": ("An artifact reference is duplicate, malformed, or reused.", "Preserve prior artifact identity and use human-reviewed manual notes/minutes until the route, authority and records controls are established."),
    "SOURCE_REF_INVALID": ("The direct source reference is missing, stale, or inconsistent.", "Keep the artifact unresolved and use human-reviewed manual notes/minutes; do not process real media until the applicable route, authority and records controls are established."),
    "MEDIA_METADATA_INVALID": ("The recording metadata does not match the selected synthetic occurrence and revision.", "Keep the source unresolved and use human-reviewed manual notes/minutes until the route, authority and records controls are established."),
    "FORMAT_UNSUPPORTED": ("The fictional media format is outside the test allowlist.", "Do not process media; continue with human-reviewed manual notes/minutes until the route, authority and records controls are established."),
    "SEGMENTS_INCOMPLETE": ("The declared segments do not provide exact ordered coverage of the media interval.", "Keep the recording incomplete and do not reconstruct missing spans; continue with human-reviewed manual notes/minutes until the route, authority and records controls are established."),
    "TRANSCRIPT_LINEAGE_INVALID": ("The proposed transcript artifact reference or direct source lineage is invalid.", "Preserve existing artifacts and use human-reviewed manual notes/minutes until the route, authority and records controls are established."),
}


def _result(code: str) -> dict:
    explanation, next_step = _MESSAGES[code]
    return {
        "state": "blocked",
        "meaning": "fictional fixture metadata only; no real authority or media quality is established",
        "issues": [{"code": code, "explanation": explanation}],
        "manual_next_step": next_step,
        "media_processed": False,
    }


def _nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _fixture_ref(value: object) -> bool:
    if not _nonempty(value) or not value.startswith("fx-"):
        return False
    suffix = value[3:]
    alphabet = "abcdefghijklmnopqrstuvwxyz234567"
    return (
        len(suffix) == 10
        and all(ch in alphabet for ch in suffix)
        and sum(ch.isalpha() for ch in suffix) >= 3
        and sum(ch.isdigit() for ch in suffix) >= 2
    )


def _only_keys(value: object, allowed: set[str]) -> bool:
    return isinstance(value, dict) and set(value) <= allowed


def _valid_schema(case: dict, catalog: list, registry: object) -> bool:
    case_keys = {"authority_revision", "meeting", "authority_refs", "recording", "transcript_artifact"}
    meeting_keys = {"meeting_ref", "occurrence_ref", "status"}
    auth_ref_keys = set(_AUTHORITY)
    auth_row_keys = {"ref", "dimension", "purpose", "meeting_ref", "occurrence_ref", "revision", "status", "capability"}
    artifact_keys = {"artifact_ref", "meeting_ref", "occurrence_ref", "artifact_type", "revision", "media_version", "content_hash"}
    recording_keys = artifact_keys | {"duration_ms", "format", "completeness", "segments"}
    segment_keys = {"segment_id", "start_ms", "end_ms"}
    transcript_keys = {"artifact_ref", "meeting_ref", "artifact_type", "revision", "source_refs"}
    if not _only_keys(case, case_keys):
        return False
    if not _only_keys(case.get("meeting"), meeting_keys) or not _only_keys(case.get("authority_refs"), auth_ref_keys):
        return False
    if not isinstance(registry, list) or any(not _only_keys(row, auth_row_keys) for row in registry):
        return False
    if not isinstance(catalog, list) or any(not _only_keys(item, artifact_keys) for item in catalog):
        return False
    recording = case.get("recording")
    if not _only_keys(recording, recording_keys):
        return False
    segments = recording.get("segments")
    if not isinstance(segments, list) or any(not _only_keys(segment, segment_keys) for segment in segments):
        return False
    transcript = case.get("transcript_artifact")
    if not _only_keys(transcript, transcript_keys) or not isinstance(transcript.get("source_refs"), list):
        return False
    return True


def _time_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _validate_authority(case: dict, registry: object) -> str | None:
    declared = case.get("authority_refs")
    if not isinstance(declared, dict) or not isinstance(registry, list) or not _fixture_ref(case.get("authority_revision")):
        return "AUTHORITY_FIXTURE_MISSING"
    refs = [declared.get(key) for key in _AUTHORITY]
    if not all(_fixture_ref(ref) for ref in refs):
        return "AUTHORITY_FIXTURE_MISSING"
    if len(set(refs)) != len(refs):
        return "AUTHORITY_FIXTURE_INVALID"
    by_ref: dict[str, dict] = {}
    for row in registry:
        if not isinstance(row, dict) or not _fixture_ref(row.get("ref")) or row["ref"] in by_ref:
            return "AUTHORITY_FIXTURE_INVALID"
        by_ref[row["ref"]] = row
    meeting = case.get("meeting")
    if not isinstance(meeting, dict):
        return "MEETING_UNVERIFIED"
    for dimension, purpose in _AUTHORITY.items():
        row = by_ref.get(declared[dimension])
        if row is None:
            return "AUTHORITY_FIXTURE_MISSING"
        if (
            row.get("dimension") != dimension
            or row.get("purpose") != purpose
            or row.get("meeting_ref") != meeting.get("meeting_ref")
            or row.get("occurrence_ref") != meeting.get("occurrence_ref")
            or row.get("revision") != case.get("authority_revision")
            or row.get("status") != "active_fixture"
            or row.get("capability") != "declared_fixture_only"
        ):
            return "AUTHORITY_FIXTURE_INVALID"
    return None


def _validate_segments(recording: dict) -> bool:
    duration = recording.get("duration_ms")
    segments = recording.get("segments")
    if not _time_int(duration) or duration <= 0 or not isinstance(segments, list) or not segments:
        return False
    if recording.get("completeness") != "complete_fixture":
        return False
    previous_end = 0
    ids: set[str] = set()
    for index, segment in enumerate(segments):
        if not isinstance(segment, dict):
            return False
        segment_id = segment.get("segment_id")
        start, end = segment.get("start_ms"), segment.get("end_ms")
        if not _fixture_ref(segment_id) or segment_id in ids or not _time_int(start) or not _time_int(end):
            return False
        ids.add(segment_id)
        if start != previous_end or end <= start or end > duration:
            return False
        if index and start < segments[index - 1].get("start_ms", -1):
            return False
        previous_end = end
    return previous_end == duration


def validate_transcript_fixture(case: object, artifact_catalog: object, authority_registry: object) -> dict:
    """Return a content-free structural result for one fully fictional fixture."""
    if not isinstance(case, dict) or not isinstance(artifact_catalog, list):
        return _result("MEDIA_METADATA_INVALID")
    if not _valid_schema(case, artifact_catalog, authority_registry):
        return _result("MEDIA_METADATA_INVALID")
    meeting = case.get("meeting")
    if (
        not isinstance(meeting, dict)
        or not all(_fixture_ref(meeting.get(k)) for k in ("meeting_ref", "occurrence_ref"))
        or meeting.get("status") != "confirmed_fixture"
    ):
        return _result("MEETING_UNVERIFIED")

    authority_error = _validate_authority(case, authority_registry)
    if authority_error:
        return _result(authority_error)

    # Resolve a unique immutable artifact namespace. Never disclose malformed refs.
    by_ref: dict[str, dict] = {}
    meeting_occurrence: dict[str, str] = {}
    occurrence_meeting: dict[str, str] = {}
    for artifact in artifact_catalog:
        if not isinstance(artifact, dict) or not _fixture_ref(artifact.get("artifact_ref")):
            return _result("ARTIFACT_REF_INVALID")
        ref = artifact["artifact_ref"]
        if ref in by_ref:
            return _result("ARTIFACT_REF_INVALID")
        meeting_ref, occurrence_ref = artifact.get("meeting_ref"), artifact.get("occurrence_ref")
        if not _fixture_ref(meeting_ref) or not _fixture_ref(occurrence_ref):
            return _result("SOURCE_REF_INVALID")
        if (meeting_ref in meeting_occurrence and meeting_occurrence[meeting_ref] != occurrence_ref) or (
            occurrence_ref in occurrence_meeting and occurrence_meeting[occurrence_ref] != meeting_ref
        ):
            return _result("SOURCE_REF_INVALID")
        meeting_occurrence[meeting_ref] = occurrence_ref
        occurrence_meeting[occurrence_ref] = meeting_ref
        by_ref[ref] = artifact

    selected = case.get("recording")
    if not isinstance(selected, dict):
        return _result("MEDIA_METADATA_INVALID")
    ref = selected.get("artifact_ref")
    registered = by_ref.get(ref) if _nonempty(ref) else None
    if (
        registered is None
        or selected.get("meeting_ref") != meeting.get("meeting_ref")
        or selected.get("occurrence_ref") != meeting.get("occurrence_ref")
        or selected.get("artifact_type") != "recording_fixture"
        or registered.get("artifact_type") != "recording_fixture"
        or registered.get("meeting_ref") != meeting.get("meeting_ref")
        or registered.get("occurrence_ref") != meeting.get("occurrence_ref")
        or not _fixture_ref(selected.get("revision"))
        or selected.get("revision") != registered.get("revision")
        or not _fixture_ref(selected.get("media_version"))
        or selected.get("media_version") != registered.get("media_version")
        or not _fixture_ref(selected.get("content_hash"))
        or selected.get("content_hash") != registered.get("content_hash")
    ):
        return _result("SOURCE_REF_INVALID")
    if not isinstance(selected.get("format"), str) or selected.get("format") not in _SUPPORTED_FIXTURE_FORMATS:
        return _result("FORMAT_UNSUPPORTED")
    if not _validate_segments(selected):
        return _result("SEGMENTS_INCOMPLETE")

    transcript = case.get("transcript_artifact")
    if not isinstance(transcript, dict):
        return _result("TRANSCRIPT_LINEAGE_INVALID")
    transcript_ref = transcript.get("artifact_ref")
    if (
        not _fixture_ref(transcript_ref)
        or transcript_ref in by_ref
        or transcript.get("meeting_ref") != meeting.get("meeting_ref")
        or transcript.get("artifact_type") != "transcript_fixture_metadata"
        or not _fixture_ref(transcript.get("revision"))
        or transcript.get("source_refs") != [ref]
    ):
        return _result("TRANSCRIPT_LINEAGE_INVALID")

    return {
        "state": "fixture_metadata_consistent",
        "meaning": "invented fixture metadata is internally consistent only; no real authority or media quality is established",
        "issues": [],
        "manual_next_step": "For real media, continue with human-reviewed manual notes/minutes. Do not record or process media until the applicable institutional route, authority and records controls are explicitly established.",
        "media_processed": False,
    }
