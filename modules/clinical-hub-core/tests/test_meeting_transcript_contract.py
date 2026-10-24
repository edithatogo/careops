from copy import deepcopy

from scripts.meeting_transcript_contract import validate_transcript_fixture


def fixture():
    meeting = {"meeting_ref": "fx-t74nfcdols", "occurrence_ref": "fx-f7b6dh5sd6", "status": "confirmed_fixture"}
    authorities = []
    authority_refs = {}
    for dimension, purpose in (
        ("capture", "capture"),
        ("processing", "transcript_processing"),
        ("audience", "permitted_audience"),
        ("retention", "retention"),
    ):
        ref = {"capture": "fx-4t7gzw7ace", "processing": "fx-56ojymxwkz", "audience": "fx-7bbl7p7mqp", "retention": "fx-7rvxp5mdva"}[dimension]
        authority_refs[dimension] = ref
        authorities.append({
            "ref": ref,
            "dimension": dimension,
            "purpose": purpose,
            "meeting_ref": meeting["meeting_ref"],
            "occurrence_ref": meeting["occurrence_ref"],
            "revision": "fx-v2564jd4l7",
            "status": "active_fixture",
            "capability": "declared_fixture_only",
        })
    recording = {
        "artifact_ref": "fx-gr7hofc2zz",
        "meeting_ref": meeting["meeting_ref"],
        "occurrence_ref": meeting["occurrence_ref"],
        "artifact_type": "recording_fixture",
        "revision": "fx-3dtriycvh5",
        "media_version": "fx-se3b7vrqwd",
        "content_hash": "fx-jdemeq7qz2",
        "duration_ms": 1000,
        "format": "fixture_pcm16",
        "completeness": "complete_fixture",
        "segments": [
            {"segment_id": "fx-2u6j35ge2d", "start_ms": 0, "end_ms": 500},
            {"segment_id": "fx-abu3xoma5m", "start_ms": 500, "end_ms": 1000},
        ],
    }
    catalog = [{k: recording[k] for k in (
        "artifact_ref", "meeting_ref", "occurrence_ref", "artifact_type", "revision", "media_version", "content_hash"
    )}]
    case = {
        "authority_revision": "fx-v2564jd4l7",
        "meeting": meeting,
        "authority_refs": authority_refs,
        "recording": recording,
        "transcript_artifact": {
            "artifact_ref": "fx-s2zfqxr74u",
            "meeting_ref": meeting["meeting_ref"],
            "artifact_type": "transcript_fixture_metadata",
            "revision": "fx-yo7rawtd35",
            "source_refs": [recording["artifact_ref"]],
        },
    }
    return case, catalog, authorities


def code(result):
    return [x["code"] for x in result["issues"]]


def test_valid_fixture_means_consistency_only_and_processes_no_media():
    case, catalog, authorities = fixture()
    before = deepcopy((case, catalog, authorities))
    result = validate_transcript_fixture(case, catalog, authorities)
    assert result["state"] == "fixture_metadata_consistent"
    assert "only" in result["meaning"]
    assert result["media_processed"] is False
    assert "authorized" not in result["meaning"]
    assert (case, catalog, authorities) == before


def test_unconfirmed_proposal_or_series_only_meeting_blocks():
    for status in ("proposal_fixture", "series_fixture", None):
        case, catalog, authorities = fixture()
        case["meeting"]["status"] = status
        assert "MEETING_UNVERIFIED" in code(validate_transcript_fixture(case, catalog, authorities))


def test_each_authority_dimension_is_separate_and_required():
    for dimension in ("capture", "processing", "audience", "retention"):
        case, catalog, authorities = fixture()
        case["authority_refs"].pop(dimension)
        assert "AUTHORITY_FIXTURE_MISSING" in code(validate_transcript_fixture(case, catalog, authorities))
    case, catalog, authorities = fixture()
    case["authority_refs"]["processing"] = case["authority_refs"]["capture"]
    assert "AUTHORITY_FIXTURE_INVALID" in code(validate_transcript_fixture(case, catalog, authorities))


def test_authority_reference_must_resolve_exact_occurrence_purpose_revision_and_active_status():
    mutations = (
        {"meeting_ref": "fx-qw46q4xf3w"},
        {"occurrence_ref": "fx-k3jvtdm3f3"},
        {"purpose": "ai_processing"},
        {"revision": "fx-ml7hn3rdmm"},
        {"status": "revoked_fixture"},
        {"status": "pending_fixture"},
        {"capability": "real_authority"},
    )
    for change in mutations:
        case, catalog, authorities = fixture()
        authorities[0].update(change)
        assert "AUTHORITY_FIXTURE_INVALID" in code(validate_transcript_fixture(case, catalog, authorities))
    case, catalog, authorities = fixture()
    case.pop("authority_revision")
    assert "AUTHORITY_FIXTURE_MISSING" in code(validate_transcript_fixture(case, catalog, authorities))


def test_authority_recheck_blocks_withdrawn_or_disputed_fixture_state():
    for status in ("withdrawn_fixture", "disputed_fixture", "expired_fixture"):
        case, catalog, authorities = fixture()
        authorities[1]["status"] = status
        assert "AUTHORITY_FIXTURE_INVALID" in code(validate_transcript_fixture(case, catalog, authorities))


def test_recording_must_bind_exact_selected_occurrence_revision_version_and_hash():
    for field, value in (
        ("meeting_ref", "fx-2wnjrwhqj6"),
        ("occurrence_ref", "fx-wc3xaegxo5"),
        ("revision", "fx-o55vypwrrn"),
        ("media_version", "fx-eq3u5u23xp"),
        ("content_hash", "fx-usbbj36vkj"),
        ("artifact_type", "notes_fixture"),
    ):
        case, catalog, authorities = fixture()
        case["recording"][field] = value
        result = validate_transcript_fixture(case, catalog, authorities)
        assert "SOURCE_REF_INVALID" in code(result)
        assert "do not process real media until the applicable route" in result["manual_next_step"]


def test_duplicate_or_reused_artifact_refs_block_without_rewriting_history():
    case, catalog, authorities = fixture()
    prior = {**catalog[0], "artifact_ref": "fx-s2zfqxr74u", "artifact_type": "transcript_fixture_metadata"}
    catalog.append(prior)
    original = deepcopy(prior)
    assert code(validate_transcript_fixture(case, catalog, authorities))
    assert prior == original
    case, catalog, authorities = fixture()
    case["transcript_artifact"]["artifact_ref"] = case["recording"]["artifact_ref"]
    assert "TRANSCRIPT_LINEAGE_INVALID" in code(validate_transcript_fixture(case, catalog, authorities))


def test_transcript_must_use_exact_direct_recording_source_in_order():
    for refs in ([], ["fx-26vgyl2n4k"], ["fx-22hqotgj4d", "fx-gr7hofc2zz"], ["fx-gr7hofc2zz", "fx-gr7hofc2zz"]):
        case, catalog, authorities = fixture()
        case["transcript_artifact"]["source_refs"] = refs
        assert "TRANSCRIPT_LINEAGE_INVALID" in code(validate_transcript_fixture(case, catalog, authorities))


def test_transcript_correction_requires_a_new_ref_and_old_identity_stays_in_catalog():
    case, catalog, authorities = fixture()
    prior = {**catalog[0], "artifact_ref": "fx-mndrgr6p7z", "artifact_type": "transcript_fixture_metadata"}
    catalog.append(prior)
    prior_before = deepcopy(prior)
    case["transcript_artifact"]["artifact_ref"] = "fx-h2trrq34f6"
    result = validate_transcript_fixture(case, catalog, authorities)
    assert result["state"] == "fixture_metadata_consistent"
    assert prior == prior_before
    case["transcript_artifact"]["artifact_ref"] = "fx-mndrgr6p7z"
    assert "TRANSCRIPT_LINEAGE_INVALID" in code(validate_transcript_fixture(case, catalog, authorities))


def test_duplicate_cross_meeting_malformed_and_wrong_revision_catalog_refs_block():
    for mutator in (
        lambda c: c.append(deepcopy(c[0])),
        lambda c: c[0].update(meeting_ref="fx-qw46q4xf3w"),
        lambda c: c[0].update(revision="fx-ml7hn3rdmm"),
        lambda c: c[0].update(content_hash="fx-o5snabzw3q"),
        lambda c: c[0].update(artifact_ref=""),
    ):
        case, catalog, authorities = fixture()
        mutator(catalog)
        assert code(validate_transcript_fixture(case, catalog, authorities))


def test_meeting_ref_is_one_to_one_with_occurrence_in_the_catalog():
    case, catalog, authorities = fixture()
    other = {**catalog[0], "artifact_ref": "fx-b3o4ey5wpq", "occurrence_ref": "fx-7fqsy3mj3y"}
    catalog.append(other)
    assert "SOURCE_REF_INVALID" in code(validate_transcript_fixture(case, catalog, authorities))


def test_semantic_or_date_like_references_are_not_accepted_as_opaque_fixture_ids():
    for semantic_ref in ("fx-Jane-Doe", "fx-JohnSmith", "fx-20260928", "fx-https-example"):
        case, catalog, authorities = fixture()
        case["recording"]["artifact_ref"] = semantic_ref
        catalog[0]["artifact_ref"] = semantic_ref
        case["transcript_artifact"]["source_refs"] = [semantic_ref]
        assert code(validate_transcript_fixture(case, catalog, authorities))


def test_segment_inventory_must_exactly_cover_duration_in_order():
    invalid = (
        [{"segment_id": "fx-66vro5wiyk", "start_ms": 0, "end_ms": 400}],  # missing final interval
        [{"segment_id": "fx-66vro5wiyk", "start_ms": 0, "end_ms": 400}, {"segment_id": "fx-p56lvwgcta", "start_ms": 500, "end_ms": 1000}],  # gap
        [{"segment_id": "fx-66vro5wiyk", "start_ms": 0, "end_ms": 600}, {"segment_id": "fx-p56lvwgcta", "start_ms": 500, "end_ms": 1000}],  # overlap
        [{"segment_id": "fx-66vro5wiyk", "start_ms": 0, "end_ms": 500}, {"segment_id": "fx-66vro5wiyk", "start_ms": 500, "end_ms": 1000}],  # duplicate id
        [{"segment_id": "fx-p56lvwgcta", "start_ms": 500, "end_ms": 1000}, {"segment_id": "fx-66vro5wiyk", "start_ms": 0, "end_ms": 500}],  # out of order
        [{"segment_id": "fx-66vro5wiyk", "start_ms": 0, "end_ms": 0}, {"segment_id": "fx-p56lvwgcta", "start_ms": 0, "end_ms": 1000}],  # zero interval
        [{"segment_id": "fx-66vro5wiyk", "start_ms": -1, "end_ms": 500}, {"segment_id": "fx-p56lvwgcta", "start_ms": 500, "end_ms": 1000}],  # negative
        [{"segment_id": "fx-66vro5wiyk", "start_ms": 0, "end_ms": 500}, {"segment_id": "fx-p56lvwgcta", "start_ms": 500, "end_ms": 1001}],  # out of duration
    )
    for segments in invalid:
        case, catalog, authorities = fixture()
        case["recording"]["segments"] = segments
        assert "SEGMENTS_INCOMPLETE" in code(validate_transcript_fixture(case, catalog, authorities))


def test_complete_flag_alone_duration_mismatch_and_unknown_segments_do_not_pass():
    for change in (
        {"completeness": "unknown"},
        {"duration_ms": 1200},
        {"segments": []},
        {"duration_ms": 0},
    ):
        case, catalog, authorities = fixture()
        case["recording"].update(change)
        result = validate_transcript_fixture(case, catalog, authorities)
        assert "SEGMENTS_INCOMPLETE" in code(result)
        assert "until the route, authority and records controls are established" in result["manual_next_step"]


def test_unsupported_format_and_media_revision_mismatch_block():
    case, catalog, authorities = fixture()
    case["recording"]["format"] = "audio/wav"
    assert "FORMAT_UNSUPPORTED" in code(validate_transcript_fixture(case, catalog, authorities))
    case, catalog, authorities = fixture()
    catalog[0]["content_hash"] = "fx-32hdf5qvlp"
    assert "SOURCE_REF_INVALID" in code(validate_transcript_fixture(case, catalog, authorities))


def test_content_and_arbitrary_malformed_values_are_never_echoed():
    case, catalog, authorities = fixture()
    case["transcript_artifact"]["source_refs"] = ["SECRET NAME / fake/path https://example.invalid"]
    result = validate_transcript_fixture(case, catalog, authorities)
    assert "TRANSCRIPT_LINEAGE_INVALID" in code(result)
    assert "SECRET" not in str(result)
    assert "example.invalid" not in str(result)
    case, catalog, authorities = fixture()
    case["transcript_text"] = "FICTIONAL SECRET TRANSCRIPT SENTINEL"
    result = validate_transcript_fixture(case, catalog, authorities)
    assert "MEDIA_METADATA_INVALID" in code(result)
    assert "SENTINEL" not in str(result)
    case, catalog, authorities = fixture()
    case["recording"]["media_bytes"] = b"fictional-payload"
    assert "MEDIA_METADATA_INVALID" in code(validate_transcript_fixture(case, catalog, authorities))


def test_nonopaque_reference_and_malformed_format_values_fail_closed():
    case, catalog, authorities = fixture()
    case["meeting"]["meeting_ref"] = "Project Falcon / 2026"
    assert "MEETING_UNVERIFIED" in code(validate_transcript_fixture(case, catalog, authorities))
    case, catalog, authorities = fixture()
    case["recording"]["format"] = []
    assert "FORMAT_UNSUPPORTED" in code(validate_transcript_fixture(case, catalog, authorities))
    case, catalog, authorities = fixture()
    case["recording"]["artifact_ref"] = "fx-"
    assert code(validate_transcript_fixture(case, catalog, authorities))


def test_unknown_fields_are_rejected_at_every_metadata_boundary():
    mutations = (
        lambda c, a, r: c.update(notes="TRANSCRIPT SENTINEL"),
        lambda c, a, r: c["recording"].update(transcriptText="TRANSCRIPT SENTINEL"),
        lambda c, a, r: c["recording"]["segments"][0].update(speakerName="PERSON SENTINEL"),
        lambda c, a, r: a[0].update(audio_data="MEDIA SENTINEL"),
        lambda c, a, r: r[0].update(raw_transcript="TRANSCRIPT SENTINEL"),
        lambda c, a, r: c["transcript_artifact"].update(url="https://example.invalid"),
    )
    for mutate in mutations:
        case, catalog, authorities = fixture()
        mutate(case, catalog, authorities)
        result = validate_transcript_fixture(case, catalog, authorities)
        assert "MEDIA_METADATA_INVALID" in code(result)
        assert "SENTINEL" not in str(result)
        assert "example.invalid" not in str(result)


def test_no_provider_storage_network_or_media_processing_imports():
    import ast
    from pathlib import Path

    tree = ast.parse(Path("scripts/meeting_transcript_contract.py").read_text())
    imported = {node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module}
    imported.update(alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names)
    assert imported <= {"__future__"}
