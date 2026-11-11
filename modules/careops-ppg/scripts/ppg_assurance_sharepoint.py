# Copyright 2026 PPG Workbench contributors
# SPDX-License-Identifier: Apache-2.0
"""Validate source-only, non-premium SharePoint fields for PPG assurance overlays.

This deliberately generates portable field XML but neither provisions a List
nor modifies a Power Platform solution. Existing PPG standards registers remain
canonical. Native identity, permissions, DLP and restore require separate proof.
"""
from __future__ import annotations

from hashlib import sha256
import json
import re
from html import escape

from scripts.ppg_obligation_application import SOURCE_KINDS, FORCES, STATES

_TYPES = frozenset({"Text","Choice","DateTime"})
_NAMES = re.compile(r"[A-Za-z][A-Za-z0-9_]{1,63}\Z")
_KEYS = re.compile(r"[a-z][a-z0-9-]{2,63}\Z")
_EXPECTED = {
    "source-force-reviews": {"ForceReviewKey", "FrameworkKey", "CaptureKey", "SourceKind", "NormativeForce"},
    "local-adoption-events": {"AdoptionKey", "EvidenceVersionKey", "ScopeKey", "State", "EffectiveFrom"},
    "evidence-review-receipts": {"ReceiptKey", "EvidenceVersionKey", "SourceSHA256", "CaptureRef",
                                 "SourceSystem", "SourceKey", "SourceVersion", "ObservedOn"},
}
_BLOCKED = frozenset({
    "accreditationrating", "compliancemet", "automaticallyapproved", "autoapproved",
    "patientidentifier", "rawsourcetext", "credential", "accesstoken",
    "refreshtoken", "password", "privatekey",
})


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def validate_manifest(manifest: dict) -> dict:
    """Fail closed on duplicate identities, premium routes and unsafe fields."""
    if not isinstance(manifest, dict) or type(manifest.get("schemaVersion")) is not int or manifest["schemaVersion"] != 1:
        raise ValueError("Unsupported assurance SharePoint source contract")
    flags = {"sourceOnly": True, "nativeQualification": False,
             "standardConnectorOnly": True, "premiumRequired": False,
             "replacesExistingLists": False}
    if (any(manifest.get(key) is not value for key,value in flags.items())
            or manifest.get("dataBoundary") != "private-deployment-owned"):
        raise ValueError("Source-only non-premium/nonmutating admission required")
    if manifest.get("connector") != "shared_sharepointonline":
        raise ValueError("Only the reviewed SharePoint standard connector is permitted")
    rows = manifest.get("registers")
    if not isinstance(rows, list) or len(rows) != len(_EXPECTED):
        raise ValueError("Exact additive list definitions required")
    observed = set()
    titles = set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Register must be an object")
        key, title = row.get("key"), row.get("title")
        if not isinstance(key, str) or not _KEYS.fullmatch(key) or key not in _EXPECTED:
            raise ValueError("Unknown register key")
        if key in observed or title in titles:
            raise ValueError("Duplicate register identity or title")
        observed.add(key)
        if (not isinstance(title,str) or not title.startswith("PPG ")
                or len(title)>128 or len(title)<5):
            raise ValueError("Unusable SharePoint list title")
        titles.add(title)
        fields=row.get("fields")
        if not isinstance(fields,list) or len(fields)>48 or not fields:
            raise ValueError("Register fields unavailable")
        seen=set()
        for field in fields:
            if not isinstance(field,dict):
                raise ValueError("Field must be an object")
            name=field.get("name")
            if not isinstance(name,str) or not _NAMES.fullmatch(name):
                raise ValueError("Invalid SharePoint field name")
            if name.lower() in _BLOCKED:
                raise ValueError("prohibited privacy or accreditation field")
            if name in seen:
                raise ValueError("Duplicate SharePoint field")
            seen.add(name)
            kind=field.get("type")
            if kind not in _TYPES:
                raise ValueError("unsupported SharePoint field type")
            if type(field.get("required")) is not bool or type(field.get("unique")) is not bool:
                raise ValueError("Field required/unique must be booleans")
            choices=field.get("choices")
            if kind=="Choice":
                if (not isinstance(choices,list) or not choices
                        or any(not isinstance(v,str) or not v.strip() for v in choices)
                        or len(set(choices))!=len(choices)):
                    raise ValueError("Choice vocabulary must be explicit and unique")
                expected_choices = {
                    "SourceKind": SOURCE_KINDS,
                    "NormativeForce": set().union(*FORCES.values()),
                    "State": STATES,
                }.get(name)
                if expected_choices is None or set(choices) != set(expected_choices):
                    raise ValueError("SharePoint contract choice vocabulary differs from runtime")
            elif choices is not None:
                raise ValueError("Non-choice field has Choice vocabulary")
        if not _EXPECTED[key].issubset(seen):
            raise ValueError("Missing required overlay source column")
        primary=row.get("primaryKey")
        identity=next((f for f in fields if f["name"]==primary),None)
        if (identity is None or identity["type"]!="Text"
                or identity["required"] is not True
                or identity["unique"] is not True):
            raise ValueError("Invalid primary SharePoint unique text identity")
    if observed!=set(_EXPECTED):
        raise ValueError("Missing additive register")
    return {
        "schemaVersion":1,
        "sha256":sha256(_canonical(manifest)).hexdigest(),
        "registerCount":len(rows),
        "listTitles":sorted(titles),
        "sourceOnly":True,
        "nativeQualification":False,
        "premiumRequired":False,
        "nativeWrites":0,
    }


def field_definitions(manifest:dict) -> list[dict]:
    """Pure source definition, not a SharePoint provisioning operation."""
    validation=validate_manifest(manifest)
    result=[]
    for row in sorted(manifest["registers"],key=lambda x:x["key"]):
        declared=[]
        for column in row["fields"]:
            attrs={
                "Type":column["type"],
                "Name":column["name"],
                "StaticName":column["name"],
                "DisplayName":column["name"],
                "Required":"TRUE" if column["required"] else "FALSE",
            }
            if column["name"]==row["primaryKey"]:
                attrs["Indexed"]="TRUE"
                attrs["EnforceUniqueValues"]="TRUE"
            if column["type"]=="DateTime":
                attrs["Format"]="DateOnly"
            attributes=" ".join(
                name+'="'+escape(value,quote=True)+'"'
                for name,value in attrs.items()
            )
            contents=""
            if column["type"]=="Choice":
                contents="<CHOICES>"+"".join(
                    "<CHOICE>"+escape(name,quote=True)+"</CHOICE>"
                    for name in column["choices"]
                )+"</CHOICES>"
            declared.append({"name":column["name"],
                             "schemaXml":"<Field "+attributes+">"+contents+"</Field>"})
        result.append({"registerKey":row["key"],"title":row["title"],
                       "fields":declared,"nativeWrites":0,
                       "sourceContractSHA256":validation["sha256"],
                       "nativeDeploymentQualified":False})
    return result
