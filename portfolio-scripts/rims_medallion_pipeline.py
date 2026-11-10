"""Loss-audited, transport-neutral RIMS medallion transformations.

Pure functions, no network or tenant writes. Preserve all legally permitted raw
fields and nested cardinalities; explicitly classify excluded fields.
"""
import hashlib
import json

class ContractError(ValueError): pass

def sha256(payload):
    return hashlib.sha256(json.dumps(payload,sort_keys=True,ensure_ascii=False,
                                     separators=(",",":"),allow_nan=False).encode()).hexdigest()

def bronze(source_id, record_id, original, *, licence, captured_utc, retention_class,
           excluded_fields=(), exclusion_reasons=None, pagination=None):
    if not isinstance(original,(dict,list)) or not source_id or not record_id or not licence:
        raise ContractError("invalid source envelope")
    excluded=set(excluded_fields)
    if isinstance(original,list) and excluded:
        raise ContractError("array-root exclusions require a separately documented record-level policy")
    if not excluded.issubset(original):
        raise ContractError("exclusion not present in source")
    reasons=exclusion_reasons or {}
    if any(not reasons.get(key) for key in excluded):
        raise ContractError("every exclusion requires a rationale")
    payload={key:value for key,value in original.items() if key not in excluded} if isinstance(original,dict) else list(original)
    return {"schema_version":"1","source_id":source_id,"record_id":record_id,
            "raw_payload":payload,"excluded_field_reasons":{key:reasons[key] for key in sorted(excluded)},
            "source_field_count":len(original),"retained_field_count":len(payload),
            "capture_sha256":sha256(original),"licence":licence,
            "captured_utc":captured_utc,"retention_class":retention_class,
            "pagination":pagination or {"complete":False},
            "bronze_loss_audited":len(payload)+len(excluded)==len(original)}

def silver(bronze_row, *, canonical_id, entity_type, mapped_fields):
    raw=bronze_row["raw_payload"]
    if not isinstance(raw,dict):
        raise ContractError("split or select array-root records before Silver field mapping")
    if not isinstance(mapped_fields,dict) or not set(mapped_fields).issubset(raw):
        raise ContractError("mapping references missing source field")
    if not canonical_id or not entity_type:
        raise ContractError("identity required")
    return {"schema_version":"1","canonical_id":canonical_id,"entity_type":entity_type,
            "attributes":{dest:raw[src] for src,dest in mapped_fields.items()},
            "unmapped_source":{key:value for key,value in raw.items() if key not in mapped_fields},
            "source_field_count":len(raw),"mapped_field_count":len(mapped_fields),
            "original_capture_sha256":bronze_row["capture_sha256"],
            "lineage":[{"source_field":src,"target_field":dest} for src,dest in sorted(mapped_fields.items())],
            "unknowns_retained":True}

def gold(silver_rows, *, period, review_states, verify_decision=None):
    if not isinstance(silver_rows,list) or not isinstance(review_states,dict):
        raise ContractError("invalid gold inputs")
    seen=set();approved=[];held=[]
    for item in silver_rows:
        key=item.get("canonical_id")
        if not key or key in seen:raise ContractError("duplicate canonical ID")
        seen.add(key)
        state=review_states.get(key)
        if state=="ConfirmedCHHHS" and callable(verify_decision) and verify_decision(key, item) is True:
            approved.append(key)
        else:held.append(key)
    return {"schema_version":"1","period":period,"grain":"unique_canonical_entity",
            "source_count":len(silver_rows),"approved_ids":sorted(approved),
            "held_ids":sorted(held),"denominator":len(silver_rows),
            "gold_issued":False,"human_release_required":True,"authoritative_ledger_required":True}

def platinum(gold_snapshot, *, analysis, evidence_refs, limitations):
    if not gold_snapshot.get("human_release_required") or gold_snapshot.get("gold_issued"):
        raise ContractError("unexpected gold state")
    if not isinstance(evidence_refs,list) or not evidence_refs:
        raise ContractError("evidence required")
    return {"schema_version":"1","gold_snapshot_sha256":sha256(gold_snapshot),
            "analysis":analysis,"evidence_refs":evidence_refs,
            "limitations":limitations,"human_release_required":True,
            "intelligence_only":True,"decision_authorised":False}
