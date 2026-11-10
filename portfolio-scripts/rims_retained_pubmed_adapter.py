"""Read-only, loss-audited adapter for the accepted retained PubMed consumer.

Consumes the historic research-publications:
  scripts/consume_retained_pubmed.py -> isolated_retained_pubmed_consumer_v1

Never reacquires PubMed, uploads records, admits publications, changes identity,
sends communications or makes a source assertion into human approval.
Actual retained/private data must remain in the approved owner environment.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

_bridge_path = Path(__file__).with_name("rims_contract_bridge.py")
_spec = importlib.util.spec_from_file_location("rims_contract_bridge", _bridge_path)
_bridge = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_bridge)


class RetainedSourceError(ValueError):
    pass


def reconcile_pubmed(consumer, *, canonical_by_pmid, verify_consumer=None,
                     licence, retention_class, mapping=None):
    """Return isolated Bronze/Silver products. All authority remains external.

    verify_consumer must recheck the historic complete typed/raw acceptance and
    independently pinned immutable source hashes; a self-declared value is not
    proof. canonical_by_pmid comes from the accepted canonical registry join,
    not DOI, author name or title matching.
    """
    if (
        not isinstance(consumer, dict)
        or consumer.get("kind") != "isolated_retained_pubmed_consumer_v1"
        or consumer.get("canonical_admission") is not False
        or consumer.get("working_model_modified") is not False
    ):
        raise RetainedSourceError("not an accepted isolated PubMed consumer shape")
    if not callable(verify_consumer) or verify_consumer(consumer) is not True:
        raise RetainedSourceError("independent retained-source proof missing")
    rows = consumer.get("rows")
    if (
        not isinstance(rows, list)
        or consumer.get("publication_count") != len(rows)
        or not isinstance(canonical_by_pmid, dict)
    ):
        raise RetainedSourceError("population mismatch or missing canonical map")
    if not isinstance(consumer.get("author_evidence"), list):
        raise RetainedSourceError("author evidence inventory required")
    if not isinstance(consumer.get("observed_utc"), str):
        raise RetainedSourceError("capture time required")
    if mapping is None:
        mapping = {}
    if not isinstance(mapping, dict):
        raise RetainedSourceError("mapping must be explicit")

    pmids, bronze, silver = set(), [], []
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("summary"), dict):
            raise RetainedSourceError("missing PubMed summary")
        pmid = row["summary"].get("PMID")
        if not isinstance(pmid, str) or not pmid.strip() or pmid in pmids:
            raise RetainedSourceError("invalid or duplicate PMID")
        pmids.add(pmid)
        canonical_id = canonical_by_pmid.get(pmid)
        if not isinstance(canonical_id, str) or not canonical_id.strip():
            raise RetainedSourceError("unreviewed or ambiguous canonical PMID link")
        metadata = row.get("metadata")
        if not isinstance(metadata, (dict, list)):
            raise RetainedSourceError("full PubMed metadata required")
        source = _bridge.bronze_record(
            "pubmed-retained", pmid, metadata,
            provider="PubMed", licence=licence,
            capture_timestamp=consumer["observed_utc"],
            retention_class=retention_class,
            pagination={"complete": True, "source": "accepted typed/raw receipts"},
            source_record_id=pmid,
            ingestion_status="complete",
        )
        # Accepted PubMed Xml.Document metadata is a list of named nodes.
        # Keep the Bronze array exact; Silver may contain it as an explicit
        # typed field without pretending that generic Value[] is analytical
        # semantic mapping of individual XML elements.
        if isinstance(metadata, list):
            if mapping and set(mapping) != {"xml_nodes"}:
                raise RetainedSourceError("XML root requires explicit node mapping")
            silver_source = {
                **source, "raw_payload": {"xml_nodes": metadata},
            }
            silver_mapping = {"xml_nodes": "xml_nodes"}
        else:
            silver_source = source
            silver_mapping = mapping
        typed = _bridge.silver_record(
            silver_source, canonical_id=canonical_id,
            entity_type="publication", mapping=silver_mapping,
        )
        bronze.append(source)
        silver.append(typed)
    if len(set(canonical_by_pmid)) < len(pmids):
        raise RetainedSourceError("incomplete accepted source mapping")
    extra_keys = set(canonical_by_pmid) - pmids
    if extra_keys:
        raise RetainedSourceError("unrecognised canonical lookup keys")
    if len({row["canonical_id"] for row in silver}) != len(silver):
        raise RetainedSourceError("duplicate canonical identity")

    for evidence in consumer["author_evidence"]:
        if not isinstance(evidence, dict) or evidence.get("[PMID]") not in pmids:
            raise RetainedSourceError("orphan author evidence")
    return {
        "schema": "careops-rims.retained-pubmed-adapter/1",
        "bronze_records": bronze,
        "silver_records": silver,
        "source_count": len(rows),
        "author_evidence_count": len(consumer["author_evidence"]),
        "data_source": "historic accepted retained PubMed consumer",
        "current_generation_accepted": False,
        "native_admission_authorised": False,
        "full_source_field_coverage_verified": False,
    }


def profile_retained_pubmed(consumer, *, verify_consumer=None):
    """Profile all retained nested PubMed metadata paths without exposing values.

    PubMed Xml.Document records have Name/Value/attribute/ordered-child
    structures, not a simplified flat dictionary. This preserves that shape
    and reports field occurrence, null, empty and missingness independently.
    """
    if (
        not isinstance(consumer, dict)
        or consumer.get("kind") != "isolated_retained_pubmed_consumer_v1"
        or consumer.get("canonical_admission") is not False
        or consumer.get("working_model_modified") is not False
    ):
        raise RetainedSourceError("invalid retained consumer")
    if not callable(verify_consumer) or verify_consumer(consumer) is not True:
        raise RetainedSourceError("unverified retained raw/typed receipts")
    rows = consumer.get("rows")
    if not isinstance(rows, list) or consumer.get("publication_count") != len(rows):
        raise RetainedSourceError("retained publication population mismatch")
    commit = consumer.get("commit_sha256")
    if (
        not isinstance(commit, str) or len(commit) != 64
        or any(value not in "0123456789abcdef" for value in commit)
    ):
        raise RetainedSourceError("verified committed source SHA required")
    metadata = []
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("metadata"), (dict, list)):
            raise RetainedSourceError("complete typed metadata required")
        metadata.append(row["metadata"])
    if metadata and all(isinstance(row, list) for row in metadata):
        path = Path(__file__).with_name("rims_pubmed_xml_field_profile.py")
        spec = importlib.util.spec_from_file_location("rims_pubmed_xml_field_profile", path)
        parser = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(parser)
        return parser.profile_pubmed_nodes(metadata, source_sha256=commit)
    if any(not isinstance(row, dict) for row in metadata):
        raise RetainedSourceError("mixed or unsupported metadata root shapes")
    path = Path(__file__).with_name("rims_retained_field_utilisation.py")
    spec = importlib.util.spec_from_file_location("rims_retained_field_utilisation", path)
    profiler = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(profiler)
    return profiler.profile("PubMed", metadata, source_sha256=commit)
