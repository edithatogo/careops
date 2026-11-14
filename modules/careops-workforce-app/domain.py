"""Pure, synthetic-only workforce job planning calculations. No industrial authority inferred."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from calendar import monthrange
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json

class DomainError(ValueError): pass

def decimal(value):
    try:
        result=Decimal(str(value))
        if not result.is_finite(): raise DomainError("non-finite hours")
        return result
    except (InvalidOperation, ValueError) as exc:
        raise DomainError("invalid hours") from exc

@dataclass(frozen=True)
class Activity:
    week: int
    day: int
    start_min: int
    end_min: int
    code: str
    site: str
    ordinary: bool=True
    cst: bool=False

def validate_cycle(blocks, weeks):
    if not isinstance(weeks,int) or isinstance(weeks,bool) or not 1<=weeks<=26:
        raise DomainError("invalid cycle")
    intervals={}
    for b in blocks:
        if not(1<=b.week<=weeks and 1<=b.day<=7 and 0<=b.start_min<b.end_min<=1440):
            raise DomainError("invalid activity interval")
        if not b.code or not b.site: raise DomainError("missing code/site")
        if b.cst and not b.ordinary: raise DomainError("CST must be ordinary hours")
        intervals.setdefault((b.week,b.day),[]).append((b.start_min,b.end_min))
    for segments in intervals.values():
        sorted_segments=sorted(segments)
        if any(a[1]>b[0] for a,b in zip(sorted_segments,sorted_segments[1:])):
            raise DomainError("overlap/double count")
    return True

def reconcile(blocks, weeks, contracted_fortnight_hours, required_cst_fraction, annualised_hours=0):
    validate_cycle(blocks,weeks)
    contracted=decimal(contracted_fortnight_hours)
    rate=decimal(required_cst_fraction)
    extra=decimal(annualised_hours)
    if contracted<=0 or not 0<=rate<=1 or extra<0: raise DomainError("invalid employment/rule values")
    ordinary=sum((Decimal(b.end_min-b.start_min)/60 for b in blocks if b.ordinary),Decimal(0))
    cst=sum((Decimal(b.end_min-b.start_min)/60 for b in blocks if b.cst),Decimal(0))
    expected=contracted*Decimal(weeks)/2
    if extra: raise DomainError("annualised budget must specify cycle inclusion")
    return {"planned_ordinary_hours":str(ordinary),"contracted_cycle_hours":str(expected),
       "ordinary_variance_hours":str(ordinary-expected),"planned_cst_hours":str(cst),
       "required_cst_hours":str(expected*rate),
       "cst_gap_hours":str(max(Decimal(0),expected*rate-cst)),
       "ordinary_balanced":ordinary==expected,"cst_sufficient":cst>=expected*rate}

def next_review_date(anchor:date,months:int):
    if not 1<=months<=120:raise DomainError("invalid review interval")
    year=anchor.year+(anchor.month-1+months)//12
    month=(anchor.month-1+months)%12+1
    return date(year,month,min(anchor.day,monthrange(year,month)[1]))

def obligation_key(plan_id,rule_id,edition,period_start:date):
    if not plan_id or not rule_id or edition<1:raise DomainError("invalid review obligation")
    raw=json.dumps([plan_id,rule_id,edition,period_start.isoformat()],separators=(",",":"))
    return sha256(raw.encode()).hexdigest()

def diff_versions(old,new):
    def walk(a,b,path):
        if a==b:return []
        if isinstance(a,dict) and isinstance(b,dict):
            return [r for key in sorted(a.keys()|b.keys()) for r in walk(a.get(key),b.get(key),path+[key])]
        return [{"path":"/".join(path),"before":a,"after":b}]
    return walk(old,new,[])
