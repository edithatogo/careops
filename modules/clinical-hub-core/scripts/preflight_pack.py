#!/usr/bin/env python3
"""Validate a selected meeting pack before manual chair or ESO review.

This is a local, read-only fallback. It does not connect to Microsoft 365,
create files, assign people, or send notifications.
"""
import argparse
import json
from pathlib import Path


LIMITS = {"brief": 1, "report": 2, "slides": 3}
REQUIRED = {"meeting_id", "pack_source", "papers"}
PAPER_FIELDS = {
    "id", "title", "source", "version", "reviewed", "reviewed_source",
    "reviewed_version", "format", "pages", "purpose",
}


def require_text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} needs text.")


def validate(data):
    if not isinstance(data, dict) or set(data) != REQUIRED:
        raise ValueError("Use meeting_id, pack_source and papers only.")
    require_text(data["meeting_id"], "meeting_id")
    require_text(data["pack_source"], "pack_source")
    if not isinstance(data["papers"], list):
        raise ValueError("papers must be a list.")
    seen = set()
    seen_sources = set()
    exceptions = []
    for index, paper in enumerate(data["papers"], start=1):
        if not isinstance(paper, dict) or set(paper) != PAPER_FIELDS:
            raise ValueError(f"paper {index} must use the agreed fields only.")
        for field in ("id", "title", "source", "version", "purpose"):
            require_text(paper[field], f"paper {index} {field}")
        for field in ("reviewed_source", "reviewed_version"):
            if not isinstance(paper[field], str):
                raise ValueError(f"paper {index} {field} must be text.")
        if paper["id"] in seen:
            exceptions.append({"paper": paper["id"], "check": "duplicate_id", "detail": "Duplicate paper ID."})
        seen.add(paper["id"])
        source = paper["source"].strip()
        if source in seen_sources:
            exceptions.append({"paper": paper["id"], "check": "duplicate_source", "detail": "Paper source link is repeated."})
        seen_sources.add(source)
        if type(paper["reviewed"]) is not bool:
            raise ValueError(f"paper {index} reviewed must be true or false.")
        if paper["reviewed"] is not True:
            exceptions.append({"paper": paper["id"], "check": "review", "detail": "Human review is not recorded."})
        else:
            reviewed_source = paper["reviewed_source"].strip()
            reviewed_version = paper["reviewed_version"].strip()
            if not reviewed_source or not reviewed_version:
                exceptions.append({
                    "paper": paper["id"], "check": "review_binding",
                    "detail": "Reviewed source and version are not both recorded.",
                })
            elif reviewed_source != source or reviewed_version != paper["version"].strip():
                exceptions.append({
                    "paper": paper["id"], "check": "review_binding",
                    "detail": "Current source or version differs from the reviewed source/version.",
                })
        if paper["format"] not in LIMITS:
            raise ValueError(f"paper {index} format must be brief, report or slides.")
        if type(paper["pages"]) is not int or paper["pages"] < 1:
            raise ValueError(f"paper {index} pages must be a positive integer.")
        limit = LIMITS[paper["format"]]
        if paper["pages"] > limit:
            exceptions.append({"paper": paper["id"], "check": "length", "detail": f"{paper['format']} has {paper['pages']} pages; limit is {limit}."})
    return {
        "meeting_id": data["meeting_id"],
        "pack_source": data["pack_source"],
        "paper_count": len(data["papers"]),
        "ready_for_manual_review": not exceptions,
        "exceptions": exceptions,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    result = validate(json.loads(args.input.read_text()))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
