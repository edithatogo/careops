"""Offline, privacy-minimised RIMS worklist, identity and reporting assurance.

Pure functions. No tenant access, notifications, automatic approval or publishing.
All input is fictional or separately authorised source data.
"""
from __future__ import annotations
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import re

class AssuranceError(ValueError):
    pass

def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

def _id(value):
    if not isinstance(value,str) or not value.strip():
        raise AssuranceError("missing identity")
    return value.strip()

def canonical_ids(record):
    """Normalize exact identifier strings, not fuzzy author names."""
    result={}
    doi=record.get("doi")
    if doi:
        doi=_id(doi).lower().removeprefix("https://doi.org/").removeprefix("doi:")
        if not re.fullmatch(r"10\.\d{4,9}/\S+",doi):
            raise AssuranceError("malformed DOI")
        result["doi"]=doi
    pmid=record.get("pmid")
    if pmid:
        pmid=_id(str(pmid))
        if not pmid.isdigit():
            raise AssuranceError("malformed PMID")
        result["pmid"]=pmid.lstrip("0") or "0"
    orcid=record.get("orcid")
    if orcid:
        orcid=_id(orcid).removeprefix("https://orcid.org/")
        if not re.fullmatch(r"\d{4}-\d{4}-\d{4}-[\dX]{4}",orcid):
            raise AssuranceError("malformed ORCID")
        result["orcid"]=orcid
    return result

def candidate_matches(records):
    """Suggest exact identifier collisions, never merge automatically."""
    if not isinstance(records,list):
        raise AssuranceError("records must be a list")
    seen_ids=set()
    by_identifier={}
    for row in records:
        subject=_id(row.get("subject_id"))
        if subject in seen_ids:
            raise AssuranceError("duplicate subject")
        seen_ids.add(subject)
        for kind,value in canonical_ids(row).items():
            by_identifier.setdefault((kind,value),set()).add(subject)
    return [{"identifier_type":kind,"identifier":value,"subjects":sorted(subjects),
             "resolution":"human_required"}
            for (kind,value),subjects in sorted(by_identifier.items())
            if len(subjects)>1]

def worklist(rows, *, now_utc, age_days=14):
    """Generate metadata-only review workload; no private source/evidence text."""
    if not isinstance(rows,list) or age_days<0:
        raise AssuranceError("invalid worklist")
    now=datetime.fromisoformat(now_utc.replace("Z","+00:00"))
    if now.tzinfo is None:
        raise AssuranceError("UTC timestamp required")
    result=[]
    seen=set()
    for row in rows:
        subject=_id(row.get("subject_id"))
        kind=_id(row.get("assertion_type"))
        key=(kind,subject)
        if key in seen:
            raise AssuranceError("duplicate queue subject")
        seen.add(key)
        state=row.get("review_state","NeedsReview")
        if state not in ("NeedsReview","Conflicted","Uncertain","NeedsEvidence","Reopened","ConfirmedCHHHS","NotCHHHS","Duplicate","EmployeeConfirmed","NotEmployee","HistoricalOrVisiting"):
            raise AssuranceError("unknown review state")
        age=None
        if row.get("observed_utc"):
            observed=datetime.fromisoformat(row["observed_utc"].replace("Z","+00:00"))
            if observed.tzinfo is None:
                raise AssuranceError("timezone missing")
            age=max(0,(now-observed).days)
        lane=("Conflicted" if state=="Conflicted" else
              "Reopened" if state=="Reopened" else
              "Overdue" if state in ("NeedsReview","NeedsEvidence","Uncertain") and age is not None and age>=age_days else
              "Pending" if state in ("NeedsReview","NeedsEvidence","Uncertain") else "Resolved")
        result.append({"subject_id":subject,"assertion_type":kind,"lane":lane,"age_days":age})
    return sorted(result,key=lambda x:(x["lane"],x["assertion_type"],x["subject_id"]))

def report_reconciliation(source_rows, review_rows, *, period, prior_issue=None):
    """Count and hash source/review populations without issuing a report."""
    if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])",period):
        raise AssuranceError("invalid report period")
    sources={}
    for row in source_rows:
        key=_id(row.get("subject_id"))
        if key in sources:
            raise AssuranceError("duplicate source identity")
        sources[key]=row
    reviews={}
    for row in review_rows:
        key=_id(row.get("subject_id"))
        if key in reviews or key not in sources:
            raise AssuranceError("duplicate/orphan review identity")
        reviews[key]=row
    counts=Counter()
    for key in sources:
        status=reviews.get(key,{}).get("review_state","NeedsReview")
        if status not in ("NeedsReview","ConfirmedCHHHS","NotCHHHS","Uncertain","Duplicate","NeedsEvidence","Conflicted","Reopened"):
            raise AssuranceError("unsupported publication status")
        counts[status]+=1
    summary={"period":period,"source_count":len(sources),"reviewed_count":len(reviews),
             "approved_count":counts["ConfirmedCHHHS"],"pending_count":sum(counts[s] for s in ("NeedsReview","Uncertain","NeedsEvidence","Conflicted","Reopened")),
             "excluded_count":counts["NotCHHHS"]+counts["Duplicate"],
             "source_digest":digest(sorted(sources.items())),
             "review_digest":digest(sorted(reviews.items()))}
    summary["snapshot_digest"]=digest(summary)
    if prior_issue is not None:
        if prior_issue.get("period")!=period or not isinstance(prior_issue.get("snapshot_digest"),str):
            raise AssuranceError("incompatible previous issue")
        summary["reissue_review_required"]=prior_issue["snapshot_digest"]!=summary["snapshot_digest"]
    return summary

def run_receipts(receipts, *, now_utc):
    """No raw URLs, actor names, titles or payloads in returned telemetry."""
    now=datetime.fromisoformat(now_utc.replace("Z","+00:00"))
    if now.tzinfo is None:
        raise AssuranceError("timezone required")
    seen=set(); counts=Counter(); ages=[]
    for receipt in receipts:
        key=_id(receipt.get("run_id"))
        if key in seen:
            raise AssuranceError("duplicate run")
        seen.add(key)
        status=receipt.get("status")
        if status not in ("success","failure","partial","skipped"):
            raise AssuranceError("unknown run outcome")
        counts[status]+=1
        when=datetime.fromisoformat(_id(receipt.get("finished_utc")).replace("Z","+00:00"))
        if when.tzinfo is None:
            raise AssuranceError("timestamp timezone required")
        ages.append(max(0,int((now-when).total_seconds()//3600)))
    return {"runs":len(seen),"outcomes":dict(sorted(counts.items())),
            "latest_age_hours":min(ages) if ages else None,"receipt_digest":digest(sorted(seen))}
