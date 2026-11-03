"""Import JSON into a local register or print its summary report."""

import argparse
import csv
import json
from pathlib import Path
import sys

from .store import Register


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("database", type=Path)
    commands = parser.add_subparsers(dest="command", required=True)
    load = commands.add_parser("import", help="atomically import a JSON register packet")
    load.add_argument("input", type=Path)
    commands.add_parser("report", help="print initiative-level counts")
    export = commands.add_parser("export", help="export flattened records as CSV")
    export.add_argument("--kind", required=True, choices=("events", "observations", "decisions"))
    export.add_argument("--output", type=Path, help="CSV output file (default: stdout)")
    args = parser.parse_args()
    with Register(args.database) as register:
        if args.command == "import":
            result = register.import_data(json.loads(args.input.read_text(encoding="utf-8")))
            print(json.dumps({"imported": result}, indent=2))
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
