"""Extract review work items from retained PI-update tables, without inferring impact.

A monthly bulletin title does not name its medicines. Preserve each complete
publisher row so an operator can compare its route, population and warning with
an identity-qualified policy. No retrieval, native writes or automatic matches.
"""
from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re


def compact(text):
    return re.sub(r"\s+", " ", text).strip()


class UpdateTables(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.tables = []
        self.rows = []
        self.row = None
        self.cell = None
        self.unsupported = False

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.depth += 1
            if self.depth == 1:
                self.rows, self.unsupported = [], False
            else:
                self.unsupported = True
        if self.depth != 1:
            return
        if tag == "tr":
            if self.row is not None:
                self.unsupported = True
            self.row = []
        elif tag in ("td", "th"):
            if self.cell is not None or self.row is None:
                self.unsupported = True
            if any(k in ("colspan", "rowspan") and v != "1" for k, v in attrs):
                self.unsupported = True
            self.cell = []
        elif self.cell is not None:
            self.cell.append(" ")

    def handle_endtag(self, tag):
        if self.depth == 1:
            if tag in ("td", "th") and self.cell is not None and self.row is not None:
                self.row.append(compact("".join(self.cell)))
                self.cell = None
            elif tag == "tr" and self.row is not None:
                if self.cell is not None:
                    self.unsupported = True
                self.rows.append(self.row)
                self.row = None
            elif tag == "table":
                if self.row is not None or self.cell is not None:
                    self.unsupported = True
                self.tables.append((self.rows, self.unsupported))
            elif self.cell is not None:
                self.cell.append(" ")
        if tag == "table":
            self.depth = max(0, self.depth - 1)

    def handle_data(self, value):
        if self.depth == 1 and self.cell is not None:
            self.cell.append(value)


def extract_updates(raw: bytes, expected_sha256: str):
    if hashlib.sha256(raw).hexdigest() != expected_sha256:
        raise ValueError("Notice capture preimage changed")
    parser = UpdateTables()
    parser.feed(raw.decode("utf-8", errors="strict"))
    if parser.depth:
        raise ValueError("Incomplete notice table")
    updates = []
    for rows, unsupported in parser.tables:
        if not rows:
            continue
        header = [compact(v).casefold() for v in rows[0]]
        if not header or header[0] not in ("active ingredient", "active ingredients"):
            continue
        if (unsupported or len(header) != 4 or "brand name" not in header[1]
                or "pi updates" not in header[2] or header[3] != "date of approval"):
            raise ValueError("PI table layout requires review")
        for index, row in enumerate(rows[1:], 1):
            if len(row) != 4 or not all(row):
                raise ValueError("Incomplete PI update row")
            updates.append(dict(row=index, ingredient=row[0], brandAndSponsor=row[1],
                                changes=row[2], approvedAtRaw=row[3]))
    return updates


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture", type=Path)
    parser.add_argument("sha256")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        updates = extract_updates(args.capture.read_bytes(), args.sha256)
        with args.output.open("x") as stream:
            json.dump(dict(schemaVersion=1, captureSHA256=args.sha256,
                           state="review required", updates=updates), stream, ensure_ascii=False)
    except (OSError, ValueError, UnicodeError) as exc:
        parser.exit(2, f"Cannot prepare notice sections: {exc}\n")


if __name__ == "__main__":
    main()
