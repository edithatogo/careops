"""Offline audit of source-qualified directed OpenAlex internal citation graphs.

This is an *unreviewed candidate corpus*, not CHHHS institutional approval.
Read-only; never infer unobserved citations from missing references.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path


_ID = re.compile(r"https://openalex\.org/W[1-9][0-9]*\Z")


class GraphAuditError(ValueError):
    """A graph cannot be admitted without complete endpoint integrity."""


def _rows(path: str | Path):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames:
            raise GraphAuditError(f"missing CSV header in {path}")
        yield from reader


def audit(works_path: str | Path, edge_paths: list[str | Path]) -> dict:
    """Validate work IDs and complete edge universe, then describe connectivity.

    A duplicate, loop, unrecognised ID or dangling endpoint fails closed;
    no de-duplication silently modifies the analysis population.
    """
    nodes: set[str] = set()
    for record in _rows(works_path):
        identifier = (record.get("openalex_id") or "").strip()
        if not _ID.fullmatch(identifier) or identifier in nodes:
            raise GraphAuditError("invalid or duplicate OpenAlex work ID")
        nodes.add(identifier)
    if not nodes:
        raise GraphAuditError("empty work population")

    edges: set[tuple[str, str]] = set()
    incoming: Counter[str] = Counter()
    outgoing: Counter[str] = Counter()
    adjacent: dict[str, set[str]] = {node: set() for node in nodes}
    for edge_path in edge_paths:
        for record in _rows(edge_path):
            source = (record.get("citing_openalex_id") or record.get("citing") or "").strip()
            target = (record.get("cited_openalex_id") or record.get("cited") or "").strip()
            if source not in nodes or target not in nodes or source == target:
                raise GraphAuditError("self-loop or edge endpoint outside work universe")
            pair = (source, target)
            if pair in edges:
                raise GraphAuditError("duplicate directed citation edge")
            edges.add(pair)
            outgoing[source] += 1
            incoming[target] += 1
            adjacent[source].add(target)
            adjacent[target].add(source)

    visited: set[str] = set()
    component_sizes: list[int] = []
    for node in sorted(nodes):
        if node in visited:
            continue
        stack = [node]
        visited.add(node)
        size = 0
        while stack:
            current = stack.pop()
            size += 1
            for neighbor in adjacent[current] - visited:
                visited.add(neighbor)
                stack.append(neighbor)
        component_sizes.append(size)
    component_sizes.sort(reverse=True)
    return {
        "schema": "careops.chhhs-candidate-citation-graph-audit/1",
        "population": "unadjudicated_OpenAlex_candidate_works",
        "nodes": len(nodes),
        "directed_edges": len(edges),
        "nodes_with_incoming": len(incoming),
        "nodes_with_outgoing": len(outgoing),
        "isolated_nodes": sum(not adjacent[node] for node in nodes),
        "weak_components": len(component_sizes),
        "largest_weak_component": component_sizes[0],
        "top_cited": [{"id": node, "internal_incoming_edges": count} for node, count in sorted(incoming.items(), key=lambda x: (-x[1], x[0]))[:15]],
        "method": "exact provider work IDs, unique directed edges, undirected weak components",
        "limitation": "internal observed reference edges, not total citations or reviewed CHHHS research",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--works", type=Path, required=True)
    parser.add_argument("--edges", type=Path, nargs="+", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.works, args.edges)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"audited {result['nodes']} candidate works and {result['directed_edges']} directed edges")


if __name__ == "__main__":
    main()
