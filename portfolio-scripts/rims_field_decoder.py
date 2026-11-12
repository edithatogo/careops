"""Display-only decoder for RIMS physical SharePoint fields and known code labels.

Never authorises a publication or employment assertion. Unknown codes remain
visible and flagged instead of being overwritten with an invented value.
"""
from __future__ import annotations
import json
from pathlib import Path

class MappingError(ValueError):
    pass

def load_mapping(path):
    value=json.loads(Path(path).read_text(encoding="utf-8"))
    aliases=value.get("publication_register")
    if value.get("schema")!="careops-rims.field-aliases/1" or not isinstance(aliases,dict):
        raise MappingError("invalid mapping schema")
    if len(set(aliases.values()))!=len(aliases):
        raise MappingError("duplicate display aliases")
    return value

def decode_row(row, mapping):
    if not isinstance(row,dict):
        raise MappingError("row must be an object")
    aliases=mapping["publication_register"]
    display={};unknown=[]
    for key,value in row.items():
        label=aliases.get(key,key)
        if label in display:
            raise MappingError("collision between source and display fields: "+label)
        display[label]=value
        if key.startswith("field_") and key not in aliases:
            unknown.append(key)
    return {"fields":display,"unknown_fields":sorted(unknown),
            "review_authorised":False,"scope":"presentation_only"}

def display_value(column,value,mapping):
    known=mapping.get("value_labels",{}).get(column,{})
    if isinstance(value,str) and value in known:
        return {"display":known[value],"original":value,"known":True,"review_authorised":False}
    return {"display":value,"original":value,"known":not bool(known),
            "review_authorised":False}
