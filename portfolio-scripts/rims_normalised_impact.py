"""Private-safe RIMS / OpenAlex normalised impact crosswalk.

Never publishes private bibliography rows, automatically confirms employment,
or silently converts an Included source label to independent review authority.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader=csv.DictReader(stream)
        if not reader.fieldnames:
            raise ValueError("CSV header required")
        return list(reader)


def norm_doi(value: str) -> str:
    text=str(value or "").strip().lower()
    text=re.sub(r"^(?:https?://)?(?:dx\.)?doi\.org/","",text)
    text=re.sub(r"^doi:","",text)
    return text if text.startswith("10.") and "/" in text and not any(x.isspace() for x in text) else ""


def norm_pmid(value: str) -> str:
    text=str(value or "").strip().removeprefix("https://pubmed.ncbi.nlm.nih.gov/").rstrip("/")
    return text if text.isascii() and text.isdigit() and int(text)>0 else ""


def aggregate(registry: list[dict[str,str]], union: list[dict[str,str]], impact: list[dict[str,str]]) -> dict:
    eligible=[r for r in registry if r.get("CanonicalKey","").strip()]
    included=[r for r in eligible if r.get("ReviewStatus","").strip()=="Included"]
    doi_map: dict[str,set[str]]=defaultdict(set)
    pmid_map: dict[str,set[str]]=defaultdict(set)
    lookup={r["CanonicalKey"].strip():r for r in eligible}
    if len(lookup) != len(eligible):
        raise ValueError("duplicate private registry canonical keys")
    for r in eligible:
        k=r["CanonicalKey"].strip()
        if d:=norm_doi(r.get("DOI","")):doi_map[d].add(k)
        if p:=norm_pmid(r.get("PMID","")):pmid_map[p].add(k)
    uidx={}
    for r in union:
        k=r.get("openalex_id","")
        if not re.fullmatch(r"https://openalex\.org/W[1-9]\d*",k) or k in uidx:
            raise ValueError("invalid/duplicate OpenAlex work ID")
        uidx[k]=r
    seen=set();matched=[];conflicts=0
    for w in impact:
        wid=w.get("openalex_id","")
        if wid in seen or wid not in uidx:
            raise ValueError("duplicate or foreign work in OpenAlex impact product")
        seen.add(wid)
        u=uidx[wid];keys=set()
        if d:=norm_doi(u.get("doi","")):keys.update(doi_map[d])
        if p:=norm_pmid(u.get("pmid","")):keys.update(pmid_map[p])
        if len(keys)>1:
            conflicts+=1
            continue
        if not keys:
            continue
        r=lookup[next(iter(keys))]
        if r.get("ReviewStatus","").strip()!="Included":
            continue
        year_raw=r.get("PublicationYear","").replace(",","").strip()
        year=int(year_raw) if re.fullmatch(r"(?:19|20)\d\d",year_raw) else None
        raw=w.get("fwci","").strip()
        try:fwci=float(raw) if raw else None
        except ValueError:fwci=None
        if fwci is not None and (not math.isfinite(fwci) or fwci<0 or fwci>1e7):
            fwci=None
        top=w.get("is_top_decile","").strip().lower()
        matched.append({"id":r["CanonicalKey"].strip(),"year":year,"fwci":fwci,"top_decile":top if top in ("true","false") else None,"topic":w.get("primary_topic","")})
    unique_ids={r["id"] for r in matched}
    if len(unique_ids)!=len(matched):
        raise ValueError("multiple OpenAlex works map to a single RIMS source key")
    def metrics(rows):
        fw=[x["fwci"] for x in rows if x["fwci"] is not None]
        percentile=[x for x in rows if x["top_decile"] is not None]
        return {"matched_source_included":len(rows),"fwci_eligible":len(fw),"median_fwci":median(fw) if fw else None,"percentile_eligible":len(percentile),"top_decile_count":sum(x["top_decile"]=="true" for x in percentile),"top_decile_share":sum(x["top_decile"]=="true" for x in percentile)/len(percentile) if percentile else None}
    periods={"2010-2017":(2010,2017),"2018-2022":(2018,2022),"2023-2025":(2023,2025)}
    summary={
        "schema":"careops.rims-source-included-openalex-impact/1",
        "claim":"exact DOI/PMID matches to source Included only, not independently approved CHHHS cohort",
        "source_registry_keyed":len(eligible),"source_registry_included":len(included),
        "openalex_candidate_works":len(union),"openalex_impact_rows":len(impact),
        "matched_source_included":len(matched),"conflicting_publication_identities":conflicts,
        "overall":metrics(matched),
        "periods":{k:metrics([r for r in matched if r["year"] is not None and low<=r["year"]<=high]) for k,(low,high) in periods.items()},
        "limitations":["Recent citation windows incomplete","All metrics are conditional on OpenAlex eligibility","No individual private registry rows exported or review authority conferred","Field-normalised provider values are not clinical/causal effects"]
    }
    return summary


def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--registry",type=Path,required=True)
    ap.add_argument("--union",type=Path,required=True)
    ap.add_argument("--impact",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    result=aggregate(read_csv(args.registry),read_csv(args.union),read_csv(args.impact))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("Wrote source-labelled aggregate; private inputs and identities not exported.")


if __name__=="__main__":main()
