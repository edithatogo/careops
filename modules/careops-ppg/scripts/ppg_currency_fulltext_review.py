"""Build a private, two-sided evidence packet; never infer clinical applicability.

Inputs contain full notice and policy text, verified capture identities, and explicit
review selections. This module does not retrieve content or write to SharePoint.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().casefold()


def checked_body(record: dict) -> str:
    text = record.get("text", "")
    if not text or record.get("textSHA256") != text_hash(text):
        raise ValueError("Full-text preimage missing or changed")
    if record.get("state") != "retrieved" or record.get("fullText") is not True:
        raise ValueError("Summary, missing or blocked content cannot support a match")
    if not re.fullmatch(r"[a-f0-9]{64}", record.get("captureSHA256", "")) or not record.get("scope"):
        raise ValueError("Capture identity and extraction scope required")
    return text


def build_review(leads: list[dict], notices: list[dict], policies: list[dict],
                 selections: list[dict]) -> dict:
    notice_by_id = {n["id"]: n for n in notices}
    policy_by_key = {(p["uid"], p["captureSHA256"]): p for p in policies}
    lead_by_id = {l["Id"]: l for l in leads}
    if len(lead_by_id) != len(leads) or len(notice_by_id) != len(notices):
        raise ValueError("Duplicate input identities")
    if len(policy_by_key) != len(policies):
        raise ValueError("Duplicate policy capture identities")
    chosen: dict[int, list[dict]] = {}
    seen = set()
    for selection in selections:
        lead_id = selection["leadId"]
        lead = lead_by_id.get(lead_id)
        if lead is None:
            raise ValueError("Selection references an unknown lead")
        if lead.get("CurrencyMatch") != "Unresolved" or lead.get("CurrencyDisposition"):
            raise ValueError("Selection would replace a candidate or human disposition")
        notice = notice_by_id.get(lead_id)
        if notice is None:
            raise ValueError("Selected lead has no notice evidence")
        if notice.get("leadGUID") != lead["GUID"] or selection["noticeTextSHA256"] != notice.get("textSHA256"):
            raise ValueError("Notice identity or reviewed preimage changed")
        policy = policy_by_key.get((selection["policyUID"], selection["policySHA256"]))
        if policy is None:
            raise ValueError("Selection references an unknown policy capture")
        key = (lead_id, policy["uid"])
        if key in seen:
            raise ValueError("Duplicate selected policy identity")
        seen.add(key)
        if not policy.get("identityBasis") or not selection.get("reason"):
            raise ValueError("Policy binding and reviewed rationale required")
        for record, field in ((notice, "noticeAnchor"), (policy, "policyAnchor")):
            anchor = selection[field]
            if len(normalise(anchor)) < 8 or normalise(anchor) not in normalise(checked_body(record)):
                raise ValueError("Selected anchor absent from full evidence")
        chosen.setdefault(lead_id, []).append({
            "policyUID": policy["uid"], "policyId": policy["id"],
            "title": policy["title"], "owner": policy.get("owner"),
            "policySHA256": policy["captureSHA256"],
            "policyTextSHA256": policy["textSHA256"],
            "noticeSHA256": notice["captureSHA256"],
            "noticeTextSHA256": notice["textSHA256"],
            "noticeAnchor": selection["noticeAnchor"],
            "policyAnchor": selection["policyAnchor"], "reason": selection["reason"],
            "identityBasis": policy["identityBasis"],
            "editionLimitation": policy.get("editionLimitation", "Current authority not established"),
        })
    rows = []
    qualified = []
    for policy in policies:
        if policy.get("state") == "retrieved" and policy.get("fullText") is True and policy.get("identityBasis"):
            checked_body(policy)
            qualified.append(policy)
    covered = len({p["uid"] for p in qualified})
    for lead in leads:
        if lead.get("CurrencyMatch") != "Unresolved":
            continue
        notice = notice_by_id.get(lead["Id"], {})
        if notice and notice.get("leadGUID") != lead["GUID"]:
            raise ValueError("Notice identity changed for an unmatched lead")
        full = notice.get("state") == "retrieved" and notice.get("fullText", False)
        if full:
            checked_body(notice)
        matches = chosen.get(lead["Id"], [])
        rows.append({"id": lead["Id"], "guid": lead["GUID"],
                     "noticeState": "full-text reviewed" if full else "blocked or incomplete",
                     "noticeScope": notice.get("scope"),
                     "noticeBlocker": notice.get("blocker"),
                     "noticeCaptureSHA256": notice.get("captureSHA256"),
                     "policyIdentitiesAvailable": covered,
                     "matches": matches,
                     "outcome": "Candidate — review" if matches else "Unresolved",
                     "limitation": "Retained editions only; unmatched is not no impact. Human applicability and disposition remain open."})
    return {"schemaVersion": 1, "rows": rows,
            "reviewed": len(rows), "newCandidates": sum(bool(r["matches"]) for r in rows)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text())
        result = build_review(**data)
        with args.output.open("x") as stream:
            json.dump(result, stream, ensure_ascii=False)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(2, f"Cannot build full-text review packet: {exc}\n")


if __name__ == "__main__":
    main()
