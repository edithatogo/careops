"""Compare every archive member; ignore XML formatting, entity collection order and ZIP container metadata."""
import hashlib
from pathlib import PurePosixPath
import sys
import xml.etree.ElementTree as ET
import zipfile


def xml_shape(data):
    def shape(node):
        return (node.tag, tuple(sorted(node.attrib.items())),
                node.text if node.text and node.text.strip() else None,
                node.tail if node.tail and node.tail.strip() else None,
                tuple(shape(child) for child in node))
    root = ET.fromstring(data)
    # Packager file enumeration differs between Windows and macOS. Only the
    # top-level entity collection is unordered; form/control/field order matters.
    entities = root.find("Entities") if root.tag == "ImportExportXml" else None
    if entities is not None:
        assert all(child.tag == "Entity" for child in entities)
        names = [child.findtext("Name") for child in entities]
        assert all(names) and len(names) == len(set(names)), "Duplicate/unnamed entities"
        entities[:] = sorted(entities, key=lambda child: child.findtext("Name"))
    return shape(root)


def members(path):
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None, f"Corrupt archive: {path}"
        entries = [item for item in archive.infolist() if not item.is_dir()]
        names = [item.filename for item in entries]
        assert names and len(names) == len(set(names)), "Empty or duplicate members"
        assert all(not PurePosixPath(name).is_absolute() and
                   ".." not in PurePosixPath(name).parts and "\\" not in name
                   for name in names), "Unsafe archive member"
        return {name: archive.read(name) for name in names}


def main():
    left, right = map(members, sys.argv[1:])
    assert left.keys() == right.keys(), "Package member sets differ"
    for name in left:
        if name.lower().endswith(".xml"):
            assert xml_shape(left[name]) == xml_shape(right[name]), f"XML content differs: {name}"
        else:
            assert left[name] == right[name], f"Member bytes differ: {name}"
    for path in sys.argv[1:]:
        with open(path, "rb") as stream:
            print(path, hashlib.file_digest(stream, "sha256").hexdigest())
    print(f"All {len(left)} members match (XML formatting/entity collection order/container metadata ignored).")


if __name__ == "__main__":
    main()
