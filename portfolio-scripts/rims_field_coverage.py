"""Offline metadata-only provider field coverage: never reads personal records."""
ALLOWED={"canonical","model","dashboard","decision","retained_only","excluded"}
class CoverageError(ValueError):
    pass

def assess(source_id, source_fields, projections):
    if not isinstance(source_id,str) or not source_id.strip():
        raise CoverageError("source ID required")
    if not isinstance(source_fields,list) or not isinstance(projections,list):
        raise CoverageError("field path arrays required")
    if not all(isinstance(x,str) and x.strip() for x in source_fields):
        raise CoverageError("invalid field path")
    if len(set(source_fields))!=len(source_fields):
        raise CoverageError("duplicate source field")
    allowed=set(source_fields); assessed=set(); outputs=[]; by_path={}; seen_projections=set()
    for item in projections:
        if not isinstance(item,dict):
            raise CoverageError("invalid projection")
        path=item.get("source_field")
        layer=item.get("layer")
        if not isinstance(path,str) or path not in allowed:
            raise CoverageError("projection references absent field")
        if layer not in ALLOWED:
            raise CoverageError("invalid projection layer")
        if (path,layer) in seen_projections:
            raise CoverageError("duplicate projection")
        seen_projections.add((path,layer))
        prior=by_path.setdefault(path,set())
        if ("excluded" in prior and layer!="excluded") or (layer=="excluded" and prior):
            raise CoverageError("excluded field cannot also be used")
        if ("retained_only" in prior and layer!="retained_only") or (layer=="retained_only" and prior):
            raise CoverageError("retained-only field cannot also be projected")
        prior.add(layer)
        if layer == "excluded" and not (
            isinstance(item.get("reason"), str) and item["reason"].strip()
        ):
            raise CoverageError("excluded field requires an explicit rationale")
        assessed.add(path)
        outputs.append({"source_field":path,"layer":layer})
    utilised = {entry["source_field"] for entry in outputs
                if entry["layer"] in {"canonical", "model", "dashboard", "decision"}}
    retained = {entry["source_field"] for entry in outputs
                if entry["layer"] == "retained_only"} - utilised
    excluded = {entry["source_field"] for entry in outputs
                if entry["layer"] == "excluded"}
    return {"schema":"careops-rims.field-coverage/1","source":source_id,
            "declared_fields":len(allowed),"assessed_fields":len(assessed),
            "unassessed_fields":sorted(allowed-assessed),
            "fields_by_layer":{layer:len({v["source_field"] for v in outputs if v["layer"]==layer}) for layer in sorted(ALLOWED)},
            "complete":len(allowed-assessed)==0,
            "accounted_for_not_all_utilised":True,
            "utilised_field_count":len(utilised),
            "retained_only_field_count":len(retained),
            "excluded_with_reason_count":len(excluded),
            "unassessed_count":len(allowed-assessed),
            "coverage_scope":"source_metadata_only",
            "native_parity_verified":False}
