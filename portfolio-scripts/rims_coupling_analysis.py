"""Exact directed citation projection for source-limited bibliographic coupling and co-citation.

The graph is a *candidate*, not a verified CHHHS research corpus. Projections
use only observed in-corpus edges; external references are not imputed.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path


def _rows(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        yield from csv.DictReader(handle)


def analyse(works: Path, edge_paths: list[Path], *, min_shared: int = 2) -> dict:
    if min_shared < 1:
        raise ValueError("min_shared must be positive")
    nodes = set()
    for row in _rows(works):
        identity = (row.get("openalex_id") or "").strip()
        if not identity.startswith("https://openalex.org/W") or identity in nodes:
            raise ValueError("invalid or duplicate work ID")
        nodes.add(identity)
    if not nodes:
        raise ValueError("empty candidate work set")
    cites: dict[str,set[str]] = defaultdict(set)
    cited_by: dict[str,set[str]] = defaultdict(set)
    seen = set()
    for path in edge_paths:
        for row in _rows(path):
            a=(row.get("citing") or row.get("citing_openalex_id") or "").strip()
            b=(row.get("cited") or row.get("cited_openalex_id") or "").strip()
            if a not in nodes or b not in nodes or a == b or (a,b) in seen:
                raise ValueError("invalid, duplicate, or out-of-corpus directed edge")
            seen.add((a,b))
            cites[a].add(b)
            cited_by[b].add(a)

    def projection(groups: dict[str,set[str]]) -> dict:
        weights: Counter[tuple[str,str]] = Counter()
        for members in groups.values():
            for a,b in combinations(sorted(members),2):
                weights[(a,b)] += 1
        ranked=sorted(((a,b,w) for (a,b),w in weights.items() if w>=min_shared),
                      key=lambda p:(-p[2],p[0],p[1]))
        return {
            "all_distinct_pairs":len(weights),
            "pairs_meeting_threshold":len(ranked),
            "top_pairs":[{"work_a":a,"work_b":b,"shared_corpus_count":w} for a,b,w in ranked[:25]],
        }

    return {
        "schema":"careops.chhhs-coupling-cocitation/1",
        "candidate_works":len(nodes),
        "observed_directed_edges":len(seen),
        "minimum_shared":min_shared,
        "bibliographic_coupling":projection(cited_by),
        "co_citation":projection(cites),
        "claim_limit":"in-corpus observed references only; no global co-citation/coupling or verified institutional attribution",
    }


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--works",type=Path,required=True)
    parser.add_argument("--edges",type=Path,nargs="+",required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    result=analyse(args.works,args.edges)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("Analysed source-limited co-citation and bibliographic coupling; no global metric claimed.")


if __name__ == "__main__":
    main()
