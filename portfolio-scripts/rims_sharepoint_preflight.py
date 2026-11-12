"""Non-premium RIMS SharePoint binding preflight (read-only, no Graph/PAC login).

Compare a tenant-owner-supplied inventory with a declared mapping before
authorising any creation, update, flow activation or reviewer notification.
No external calls, secrets or personal URLs are accepted in the mapping.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path


class MappingError(ValueError):
    pass


GUID=re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
CORE={"candidates","people","decisions","issues"}
REQUIRED={
    "candidates":{"SourceKey","ReviewState","EvidenceHash","LatestDecisionID"},
    "people":{"PersonKey","EvidenceHash","ReviewState"},
    "decisions":{"DecisionID","AssertionType","SubjectID","Reviewer","DecidedUTC",
                 "Reason","CandidateHash","EvidenceHash","Supersedes"},
    "issues":{"IssueKey","Period","ReviewedSnapshotHash","IssueState"},
}
RESTRICTED={"people","decisions"}


def reconcile(inventory, mapping):
    """Pure dry-run; return mismatches without exposing tenant endpoints."""
    if not isinstance(inventory,dict) or not isinstance(mapping,dict):
        raise MappingError("mapping and inventory must be objects")
    if mapping.get("schema")!="careops-rims.site-bindings/1":
        raise MappingError("unsupported mapping schema")
    if mapping.get("connectors") != ["shared_sharepointonline"]:
        raise MappingError("standard SharePoint connector only")
    tables=mapping.get("tables")
    live=inventory.get("lists")
    if not isinstance(tables,dict) or not isinstance(live,list) or set(tables)!=CORE:
        raise MappingError("incomplete logical map")
    by_id={}
    for row in live:
        guid=row.get("list_guid")
        if not isinstance(guid,str) or not GUID.fullmatch(guid):
            raise MappingError("invalid List GUID in inventory")
        if guid.lower() in by_id:
            raise MappingError("duplicate inventory List GUID")
        by_id[guid.lower()]=row
    used=set(); findings=[]
    for logical in sorted(CORE):
        binding=tables[logical]
        if not isinstance(binding,dict):
            raise MappingError("invalid binding")
        guid=binding.get("list_guid")
        if not isinstance(guid,str) or not GUID.fullmatch(guid):
            raise MappingError("mapping requires exact List GUID")
        if guid.lower() in used:
            raise MappingError("same physical List mapped to multiple authorities")
        used.add(guid.lower())
        actual=by_id.get(guid.lower())
        if actual is None:
            findings.append({"table":logical,"code":"MISSING_LIST"})
            continue
        fields=binding.get("columns")
        if not isinstance(fields,dict) or not REQUIRED[logical].issubset(fields):
            raise MappingError("missing required logical field mappings")
        actual_fields=set(actual.get("internal_names",[]))
        for field in sorted(REQUIRED[logical]):
            mapped=fields[field]
            if not isinstance(mapped,str) or not mapped.strip():
                raise MappingError("blank internal column")
            if mapped not in actual_fields:
                findings.append({"table":logical,"code":"MISSING_COLUMN","field":field})
        if actual.get("versioning_enabled") is not True:
            findings.append({"table":logical,"code":"VERSIONING_REQUIRED"})
        if logical in RESTRICTED and actual.get("restricted_readers") is not True:
            findings.append({"table":logical,"code":"RESTRICTED_READERS_REQUIRED"})
    return {"schema":"careops-rims.binding-preflight/1","ready":not findings,
            "findings":findings,"operation":"read_only","mutation_authorised":False}


def main(argv=None):
    parser=argparse.ArgumentParser(description="RIMS standard SharePoint binding preflight")
    parser.add_argument("inventory")
    parser.add_argument("mapping")
    args=parser.parse_args(argv)
    try:
        inventory=json.loads(Path(args.inventory).read_text(encoding="utf-8"))
        mapping=json.loads(Path(args.mapping).read_text(encoding="utf-8"))
        output=reconcile(inventory,mapping)
    except (OSError,ValueError,TypeError) as exc:
        parser.exit(2,"RIMS mapping refused: "+str(exc)+"\n")
    print(json.dumps(output,sort_keys=True,indent=2))
    return 0 if output["ready"] else 1

if __name__=="__main__":
    raise SystemExit(main())
