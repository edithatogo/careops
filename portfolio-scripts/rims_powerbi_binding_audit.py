"""Read-only audit of TMDL/report/scorecard/RDL field codes.

Never renames model objects: that may break visuals, DAX, field parameters,
scorecards, RDL datasets or external reports. Outputs a migration candidate.
"""
import json, re
import xml.etree.ElementTree as ET

class BindingError(ValueError):pass

def parse_tmdl(text):
    if not isinstance(text,str):raise BindingError("TMDL text required")
    fields=[];current=None
    for line in text.splitlines():
        m=re.match(r"^\s*column\s+(?:'([^']+)'|([^\s]+))\s*$",line)
        if m:
            if current:fields.append(current)
            current={"model_name":m.group(1) or m.group(2),"source_column":None}
            continue
        if current:
            src=re.match(r"^\s*sourceColumn:\s*(.+?)\s*$",line)
            if src:
                current["source_column"]=src.group(1).strip("'")
            if line.startswith("\tmeasure ") or line.startswith("\tpartition "):
                fields.append(current);current=None
    if current:fields.append(current)
    return fields

def audit_tmdl(text, aliases):
    parsed=parse_tmdl(text)
    raw_to_display={k:v for k,v in aliases.items()}
    candidates=[];unresolved=[]
    for f in parsed:
        name=f["model_name"];source=f["source_column"]
        if name in raw_to_display or (source in raw_to_display and name!=raw_to_display[source]):
            candidates.append({"model_name":name,"source_column":source,
                               "desired_display":raw_to_display.get(name,raw_to_display.get(source)),
                               "action":"review_compatibility_alias_not_in_place_rename"})
        elif re.fullmatch(r"field_\d+",name):
            unresolved.append(name)
    return {"schema":"careops-rims.binding-audit/1","model_columns":len(parsed),
            "candidate_aliases":candidates,"unresolved_codes":sorted(unresolved),
            "renames_applied":0,"native_verified":False}

def inspect_json_codes(payload):
    """Find possible field_N strings as review candidates, not proven visual refs."""
    seen=set()
    def walk(item):
        if isinstance(item,dict):
            for key,value in item.items():
                if re.fullmatch(r"field_\d+",str(key)):seen.add(str(key))
                walk(value)
        elif isinstance(item,list):
            for child in item:walk(child)
        elif isinstance(item,str):
            for match in re.findall(r"\bfield_\d+\b",item):seen.add(match)
    walk(payload)
    return sorted(seen)

def inspect_rdl_codes(xml_text):
    try:root=ET.fromstring(xml_text)
    except ET.ParseError as exc:raise BindingError("malformed RDL") from exc
    return sorted(set(re.findall(r"\bfield_\d+\b"," ".join(x for x in root.itertext() if x))))

def propose_migration(tmdl_text,aliases,*,report_json=None,scorecard_json=None,rdl_text=None):
    model=audit_tmdl(tmdl_text,aliases)
    return {"schema":"careops-rims.powerbi-remediation-proposal/1",
            "model":model,"report_codes":inspect_json_codes(report_json) if report_json is not None else None,
            "scorecard_codes":inspect_json_codes(scorecard_json) if scorecard_json is not None else None,
            "paginated_codes":inspect_rdl_codes(rdl_text) if rdl_text is not None else None,
            "apply":False,"requires":["semantic lineage baseline","DAX/visual/scorecard/RDL exact reference diff",
                                     "independent native rendering and refresh acceptance"]}
