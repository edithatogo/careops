"""Fractional title-theme portfolio diversity; no inferred institutional attribution.

Title-only heuristics are descriptive. They are not validated clinical research
specialties and are explicitly unsuitable for individual performance rankings.
"""
from __future__ import annotations

import math
from collections import defaultdict


def diversity(document_labels: list[tuple[str, ...]]) -> dict:
    """Allocate each classified paper equally across its labels, then Shannon entropy.

    Empty tuples are unclassified rather than an additional topic. Every
    paper has unit weight regardless of the number of labels assigned.
    """
    theme_counts: dict[str, float] = defaultdict(float)
    classified = 0
    for labels in document_labels:
        if len(labels) != len(set(labels)) or any(not label.strip() or label != label.strip() for label in labels):
            raise ValueError("invalid or repeated topic label")
        if not labels:
            continue
        classified += 1
        for name in labels:
            theme_counts[name] += 1 / len(labels)
    n = len(document_labels)
    shares = {name: theme_counts[name] / classified for name in sorted(theme_counts)} if classified else {}
    entropy = -sum(p * math.log2(p) for p in shares.values()) if classified else None
    if entropy is not None and abs(entropy) < 1e-12:
        entropy = 0.0
    return {
        "documents": n,
        "classified_papers": classified,
        "unclassified_papers": n - classified,
        "classified_share": classified / n if n else None,
        "fractional_theme_shares": shares,
        "entropy_bits": entropy,
        "effective_themes": 2 ** entropy if entropy is not None else None,
        "interpretation": "Diversity among title-keyword-classified papers only; unknown titles excluded",
    }


def temporal_comparison(old: list[tuple[str, ...]], recent: list[tuple[str, ...]]) -> dict:
    return {
        "old": diversity(old),
        "recent": diversity(recent),
        "method": "fractional assignment within each keyword-classified title; no independent validation",
    }
