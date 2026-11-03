"""Import JSON into a local register or print its summary report."""

import argparse
import csv
import json
from pathlib import Path
import sys

from datetime import UTC, datetime
from .feeds import packet
from .store import Register


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("database", type=Path)
    commands = parser.add_subparsers(dest="command", required=True)
    load = commands.add_parser("import", help="atomically import a JSON register packet")
    load.add_argument("input", type=Path)
    feed = commands.add_parser("feed-import")
    feed.add_argument("kind", choices=("excel", "planner", "sharepoint"))
    feed.add_argument("source", help="Stable table, board or list key without a colon")
    feed.add_argument("input", type=Path)
    commands.add_parser("feed-health")
    commands.add_parser("report", help="print initiative-level counts")
    export = commands.add_parser("export", help="export flattened records as CSV")
    export.add_argument("--kind", required=True, choices=("events", "observations", "decisions"))
    export.add_argument("--output", type=Path, help="CSV output file (default: stdout)")
    args = parser.parse_args()
    with Register(args.database) as register:
        if args.command == "import":
            result = register.import_data(json.loads(args.input.read_text(encoding="utf-8")))
            print(json.dumps({"imported": result}, indent=2))
        elif args.command == "feed-import":
            if not args.source.strip() or ":" in args.source:
                parser.error("Supply a nonempty source key without a colon")
            key = f"{args.kind}:{args.source}"
            try:
                data = packet(args.kind, args.input, key)
                counts = register.import_data(data, feed_receipt=(key, datetime.now(UTC).isoformat()))
            except (ValueError, KeyError, TypeError, OSError, csv.Error) as exc:
                with register.db:
                    register.db.execute("""INSERT INTO feed_health VALUES (?, NULL, 'failed')
                        ON CONFLICT(feed) DO UPDATE SET status='failed'""", (key,))
                parser.exit(1, f"Feed rejected: {exc}\n")
            print(json.dumps({"imported": counts}))
        elif args.command == "feed-health":
            now = datetime.now(UTC)
            rows = []
            for record in register.db.execute("SELECT * FROM feed_health ORDER BY feed"):
                row = dict(record)
                last = row["last_good"]
                row["age_seconds"] = (now - datetime.fromisoformat(last)).total_seconds() if last else None
                rows.append(row)
            print(json.dumps(rows, indent=2))
        elif args.command == "report":
            print(json.dumps({"initiatives": register.report()}, indent=2))
        else:
            rows = register.export_rows(args.kind)
            fields = list(dict.fromkeys(field for row in rows for field in row))
            target = args.output.open("w", newline="", encoding="utf-8") if args.output else sys.stdout
            try:
                writer = csv.DictWriter(target, fieldnames=fields, extrasaction="ignore")
                if fields:
                    writer.writeheader()
                    writer.writerows(rows)
            finally:
                if args.output:
                    target.close()


if __name__ == "__main__":
    main()
