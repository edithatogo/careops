"""Compare retained DOCX bytes and selected document content without native calls."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import stat
import sys
import xml.etree.ElementTree as ET
import zipfile

MAX_ARCHIVE = 25 * 1024 * 1024
MAX_EXPANDED = 100 * 1024 * 1024
MAX_MEMBERS = 1000
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
REL = "{http://schemas.openxmlformats.org/package/2006/relationships}"


def _sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _xml(value: bytes) -> ET.Element:
    # UTF-16 and other encodings must not evade declaration checks.
    if b"\x00" in value or b"<!doctype" in value.lower() or b"<!entity" in value.lower():
        raise ValueError("Unsupported XML encoding or declaration")
    return ET.fromstring(value)


def _text(node: ET.Element) -> str:
    return "".join(
        (child.text or "") if child.tag == W + "t" else
        "\n" if child.tag in (W + "br", W + "cr") else
        "\t" if child.tag == W + "tab" else ""
        for child in node.iter()
    )


def _snapshot(path: Path) -> dict:
    with path.open("rb") as handle:
        raw = handle.read(MAX_ARCHIVE + 1)
    if len(raw) > MAX_ARCHIVE:
        raise ValueError("Archive exceeds size limit")
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        items = archive.infolist()
        names = [item.filename for item in items]
        if len(items) > MAX_MEMBERS or len(names) != len(set(names)):
            raise ValueError("Too many or duplicate archive members")
        if sum(item.file_size for item in items) > MAX_EXPANDED:
            raise ValueError("Expanded archive exceeds size limit")
        for item in items:
            parts = PurePosixPath(item.filename)
            if (not item.filename or str(parts) != item.filename.rstrip("/")
                    or parts.is_absolute() or ".." in parts.parts or "\\" in item.filename
                    or ":" in item.filename or item.flag_bits & 1
                    or stat.S_ISLNK(item.external_attr >> 16)):
                raise ValueError("Unsafe or encrypted archive member")
        members = {item.filename: archive.read(item) for item in items}
    if "word/document.xml" not in members:
        raise ValueError("Missing document body")
    document = _xml(members["word/document.xml"])
    if document.tag != W + "document" or document.find(W + "body") is None:
        raise ValueError("Invalid document body")
    relations = {}
    if "word/_rels/document.xml.rels" in members:
        for relation in _xml(members["word/_rels/document.xml.rels"]):
            if relation.tag != REL + "Relationship":
                raise ValueError("Unexpected relationship record")
            identity = relation.attrib["Id"]
            if identity in relations:
                raise ValueError("Duplicate relationship identity")
            relations[identity] = tuple(relation.attrib.get(k) for k in
                                        ("Type", "Target", "TargetMode"))
    links = []
    for node in document.iter(W + "hyperlink"):
        identity = node.get(R + "id")
        if identity is not None and identity not in relations:
            raise ValueError("Unresolved document hyperlink")
        links.append((node.get(W + "anchor"), relations.get(identity), _text(node)))
    controls, control_ids = [], []
    for node in document.iter(W + "sdt"):
        props = node.find(W + "sdtPr")
        if props is None:
            raise ValueError("Content control lacks properties")
        values = {}
        for kind in ("tag", "alias", "id"):
            value = props.find(W + kind)
            values[kind] = value.get(W + "val") if value is not None else None
        binding = props.find(W + "dataBinding")
        controls.append((values["tag"], values["alias"],
                         sorted(binding.attrib.items()) if binding is not None else None,
                         _text(node)))
        control_ids.append(values["id"])
    return {
        "sha256": _sha(raw), "bytes": len(raw),
        "members": {name: _sha(value) for name, value in members.items()},
        "paragraphs": [_text(node) for node in document.iter(W + "p")],
        "controls": controls, "control_ids": control_ids, "hyperlinks": links,
    }


def compare(before: Path, after: Path) -> dict:
    left, right = _snapshot(before), _snapshot(after)
    selected = {kind: left[kind] == right[kind]
                for kind in ("paragraphs", "controls", "hyperlinks")}
    return {
        "scope": "Offline main-document paragraphs, tagged/untagged controls and explicit hyperlinks only",
        "before": {key: left[key] for key in ("sha256", "bytes")},
        "after": {key: right[key] for key in ("sha256", "bytes")},
        "byteExact": left["sha256"] == right["sha256"],
        "changedMembers": [name for name in sorted(left["members"].keys() | right["members"].keys())
                           if left["members"].get(name) != right["members"].get(name)],
        "selectedContentExact": all(selected.values()),
        "comparisons": selected,
        "controlIdsExact": left["control_ids"] == right["control_ids"],
        "counts": {kind: {"before": len(left[kind]), "after": len(right[kind])}
                   for kind in selected},
        "limitations": "No layout, styles, images, field-code links, headers, footnotes, access, history, native restore or runtime qualification",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    parser.add_argument("--require", choices=("bytes", "selected-content"), default="bytes")
    args = parser.parse_args()
    try:
        result = compare(args.before, args.after)
    except (OSError, ValueError, KeyError, ET.ParseError, zipfile.BadZipFile,
            RuntimeError, NotImplementedError):
        print(json.dumps({"error": "DOCX comparison refused invalid, unreadable or unsupported input"}))
        return 2
    print(json.dumps(result, indent=2))
    return 0 if result["byteExact" if args.require == "bytes" else "selectedContentExact"] else 1


if __name__ == "__main__":
    sys.exit(main())
