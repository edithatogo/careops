"""Compare a portable resource manifest to an explicitly supplied inventory."""
import argparse
import json
from pathlib import Path


def plan(desired, observed):
    wanted = desired["resources"]
    current = observed["resources"]
    for records in (wanted, current):
        keys = [r["key"] for r in records]
        if len(keys) != len(set(keys)):
            raise ValueError("Resource keys must be unique")
    existing = {r["key"]: r for r in current}
    return [
        {"key": r["key"], "action": (
            "create" if r["key"] not in existing else
            "unchanged" if r == existing[r["key"]] else "review_update"
        ), "desired": r}
        for r in wanted
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("inventory", type=Path)
    args = parser.parse_args()
    print(json.dumps({"mode": "dry_run", "operations": plan(
        json.loads(args.manifest.read_text()),
        json.loads(args.inventory.read_text())
    )}, indent=2))


if __name__ == "__main__":
    main()
