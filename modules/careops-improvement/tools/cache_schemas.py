"""Fetch hash-pinned public validation schemas into an ignored local cache."""
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]


def main():
    for entry in json.loads((ROOT / "platform/analytics/schema-sources.json").read_text()):
        target = ROOT / ".local/schema-cache" / entry["path"]
        data = target.read_bytes() if target.is_file() else urlopen(entry["url"], timeout=30).read()
        if hashlib.sha256(data).hexdigest() != entry["sha256"]:
            raise ValueError("Schema digest changed; review the upstream revision")
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            target.write_bytes(data)
    print("Hash-pinned schema cache verified")


if __name__ == "__main__":
    main()
