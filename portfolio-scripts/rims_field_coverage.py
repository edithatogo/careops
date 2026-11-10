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
    allowed=set(source_fields); assessed=set(); outputs=[]
    for item in projections:
        if not isinstance(item,dict):
            raise CoverageError("invalid projection")
        path=item.get("source_field")
        layer=item.get("layer")
        if path not in allowed:
            raise CoverageError("projection references absent field")
        if layer not in ALLOWED:
            raise CoverageError("invalid projection layer")
        assessed.add(path)
        outputs.append({"source_field":path,"layer":layer})
    return {"schema":"careops-rims.field-coverage/1","source":source_id,
            "declared_fields":len(allowed),"assessed_fields":len(assessed),
            "unassessed_fields":sorted(allowed-assessed),
            "fields_by_layer":{layer:len({v["source_field"] for v in outputs if v["layer"]==layer}) for layer in sorted(ALLOWED)},
            "complete":len(allowed-assessed)==0,
            "coverage_scope":"source_metadata_only","native_parity_verified":False}
