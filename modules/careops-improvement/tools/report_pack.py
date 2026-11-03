"""Render a dated local report from one frozen initiative projection."""
import argparse
import csv
import html
import json
from pathlib import Path


def render(rows, period):
    titles = [r["initiative_id"] for r in rows]
    if len(set(titles)) != len(titles):
        raise ValueError("Duplicate initiative in projection")
    columns = ["initiative_id", "title", "task_count", "decision_count", "adoption_observations"]
    summary = {"period": period, "initiatives": len(rows),
               "tasks": sum(r["task_count"] for r in rows),
               "adoption_observations": sum(r["adoption_observations"] for r in rows)}
    escape = lambda value: html.escape(str(value))
    table = "<tr>" + "".join("<th>" + escape(c) + "</th>" for c in columns) + "</tr>"
    for row in rows:
        table += "<tr>" + "".join("<td>" + escape(row[c]) + "</td>" for c in columns) + "</tr>"
    page = ('<!doctype html><html lang="en"><meta charset="utf-8">'
            '<title>Improvement portfolio</title><style>body{font:14px sans-serif}td,th{padding:8px;border:1px solid}table{border-collapse:collapse}</style>'
            '<h1>Improvement portfolio</h1><p>' + escape(period) + '</p><p>'
            + escape(json.dumps(summary)) + '</p><table>' + table + '</table></html>')
    return summary, page


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("projection", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--period", required=True)
    args = parser.parse_args()
    projection = json.loads(args.projection.read_text())
    rows = projection["initiatives"] if isinstance(projection, dict) else projection
    summary, page = render(rows, args.period)
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2))
    (args.output / "report.html").write_text(page)
    with (args.output / "initiatives.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]) if rows else ["initiative_id"])
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
