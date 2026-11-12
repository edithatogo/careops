"""Profile semantic paths in accepted PubMed Xml.Document-shaped metadata.

Preserves source element Name/Namespace/Value/Attributes semantics without
exporting original text, author identities, attributes or source fragments.
Repeated XML tags share one path; counts preserve all occurrences. The accepted
PubMed publication_xml_metadata.metadata_paths is the canonical private byte
reconstruction route; this is a bounded metadata-only consumer for RIMS.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import re


class XMLProfileError(ValueError):
    pass


TAG = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]{0,95}$")
MAX_DEPTH = 32
MAX_FIELDS = 10000
MAX_DOCUMENTS = 100000


def _element_segment(name, namespace):
    if not isinstance(name, str) or not TAG.fullmatch(name):
        raise XMLProfileError("invalid or potentially sensitive element name")
    if not isinstance(namespace, str):
        raise XMLProfileError("invalid namespace type")
    # Namespace text might be an opaque or personally identifying URI.
    # Keep stable semantic separation without publishing that original URI.
    if namespace:
        namespace_hash = hashlib.sha256(namespace.encode("utf-8")).hexdigest()[:24]
        return "{ns:" + namespace_hash + "}" + name
    return name


def profile_pubmed_nodes(documents, *, source_sha256):
    """Report per-element occurrence, record presence, missingness, text/empty.

    Each document must be a list of accepted PubMed XML-shaped nodes.
    This metadata-only report does NOT certify complete native or provider data.
    """
    if not isinstance(documents, list) or len(documents) > MAX_DOCUMENTS:
        raise XMLProfileError("bounded document array required")
    if not isinstance(source_sha256, str) or not re.fullmatch(
        r"[0-9a-f]{64}", source_sha256
    ):
        raise XMLProfileError("verified upstream digest assertion required")
    counts = defaultdict(Counter)
    per_record = Counter()

    def visit(nodes, prefix, depth, observed):
        if depth > MAX_DEPTH:
            raise XMLProfileError("XML source nesting exceeded")
        if not isinstance(nodes, list):
            raise XMLProfileError("XML root/children must be arrays")
        for node in nodes:
            if not isinstance(node, dict) or set(node) != {
                "Name", "Namespace", "Value", "Attributes"
            }:
                raise XMLProfileError("invalid Xml.Document node shape")
            key = _element_segment(node["Name"], node["Namespace"])
            path = prefix + "/" + key
            if len(counts) >= MAX_FIELDS and path not in counts:
                raise XMLProfileError("too many distinct XML field paths")
            value = node["Value"]
            if not isinstance(value, (str, list)):
                raise XMLProfileError("XML content requires text or children")
            counts[path]["occurrences"] += 1
            if isinstance(value, str):
                counts[path]["type:string"] += 1
                counts[path]["nonempty_occurrences" if value else "empty_occurrences"] += 1
            else:
                counts[path]["type:array"] += 1
                if not value:
                    counts[path]["empty_occurrences"] += 1
                else:
                    counts[path]["nonempty_occurrences"] += 1
            observed.add(path)
            attrs = node["Attributes"]
            if not isinstance(attrs, list):
                raise XMLProfileError("XML attributes require an array")
            observed_attrs = set()
            for attr in attrs:
                if not isinstance(attr, dict) or set(attr) != {
                    "Name", "Namespace", "Value"
                } or not isinstance(attr.get("Value"), str):
                    raise XMLProfileError("invalid XML attribute")
                name = _element_segment(attr["Name"], attr["Namespace"])
                if name in observed_attrs:
                    raise XMLProfileError("duplicate XML attribute")
                observed_attrs.add(name)
                attr_path = path + "/@" + name
                if len(counts) >= MAX_FIELDS and attr_path not in counts:
                    raise XMLProfileError("too many XML attribute paths")
                counts[attr_path]["occurrences"] += 1
                counts[attr_path]["type:string"] += 1
                counts[attr_path]["nonempty_occurrences"
                                  if attr["Value"] else "empty_occurrences"] += 1
                observed.add(attr_path)
            if isinstance(value, list) and value:
                visit(value, path, depth + 1, observed)

    for document in documents:
        if not isinstance(document, list) or not document:
            raise XMLProfileError("nonempty complete PubMed XML node list required")
        observed = set()
        visit(document, "", 0, observed)
        for path in observed:
            per_record[path] += 1

    fields = []
    for path in sorted(counts):
        count = counts[path]
        fields.append({
            "path": path,
            "records_present": per_record[path],
            "records_missing": len(documents) - per_record[path],
            "occurrences": count["occurrences"],
            "null_occurrences": 0,
            "empty_occurrences": count["empty_occurrences"],
            "nonempty_occurrences": count["nonempty_occurrences"],
            "types": sorted(key[5:] for key in count if key.startswith("type:")),
            "declared_by_provider": None,
        })
    return {
        "schema": "careops-rims.retained-field-profile/1",
        "source_id": "PubMed",
        "asserted_source_sha256": source_sha256,
        "source_digest_independently_verified": False,
        "records_observed": len(documents),
        "paths_observed": len(fields),
        "paths_declared": None,
        "fields": fields, "contains_values": False,
        "full_provider_schema_coverage_verified": False,
        "native_consumer_coverage_verified": False,
    }


def expand_xml_occurrences(nodes, *, source_id, record_id, source_sha256,
                           verify_source=None):
    """Lossless ordered source-field occurrence projection for PRIVATE consumers.

    Every named XML element and attribute, including empty elements, is retained.
    Stable semantic paths support cross-record analysis; ordinal paths preserve
    repeated sibling identity and document order. This is not a publication,
    employment, grant or report approval. Never put the output in public Git.
    """
    if not callable(verify_source) or verify_source(
        source_id, record_id, source_sha256
    ) is not True:
        raise XMLProfileError("independent retained-source verification required")
    if not all(isinstance(value, str) and value.strip()
               for value in (source_id, record_id)):
        raise XMLProfileError("source/record identity required")
    if not isinstance(source_sha256, str) or not re.fullmatch(
        r"[0-9a-f]{64}", source_sha256
    ):
        raise XMLProfileError("source SHA-256 required")
    if not isinstance(nodes, list) or not nodes:
        raise XMLProfileError("accepted named XML nodes required")
    occurrences = []

    def visit(contents, semantic, ordered, depth):
        if depth > MAX_DEPTH:
            raise XMLProfileError("XML nesting exceeded")
        sibling_counts = Counter()
        for node in contents:
            if not isinstance(node, dict) or set(node) != {
                "Name", "Namespace", "Value", "Attributes"
            }:
                raise XMLProfileError("invalid XML node structure")
            segment = _element_segment(node["Name"], node["Namespace"])
            sibling_counts[segment] += 1
            path = semantic + "/" + segment
            ordinal = ordered + "/" + segment + "[" + str(sibling_counts[segment]) + "]"
            value = node["Value"]
            if not isinstance(value, (str, list)):
                raise XMLProfileError("invalid XML value")
            attrs = node["Attributes"]
            if not isinstance(attrs, list):
                raise XMLProfileError("invalid XML attributes")
            if len(occurrences) >= MAX_FIELDS:
                raise XMLProfileError("too many XML occurrences")
            occurrences.append({
                "semantic_path": path, "ordered_path": ordinal,
                "kind": "container" if isinstance(value, list) and value else
                        "empty" if isinstance(value, list) else "text",
                "value": value if isinstance(value, str) else None,
                "source_id": source_id, "record_id": record_id,
                "source_sha256": source_sha256,
            })
            seen_attrs = set()
            for attr in attrs:
                if not isinstance(attr, dict) or set(attr) != {
                    "Name", "Namespace", "Value"
                } or not isinstance(attr["Value"], str):
                    raise XMLProfileError("invalid XML attribute")
                attr_name = _element_segment(attr["Name"], attr["Namespace"])
                if attr_name in seen_attrs:
                    raise XMLProfileError("duplicate attribute")
                seen_attrs.add(attr_name)
                if len(occurrences) >= MAX_FIELDS:
                    raise XMLProfileError("too many XML occurrences")
                occurrences.append({
                    "semantic_path": path + "/@" + attr_name,
                    "ordered_path": ordinal + "/@" + attr_name,
                    "kind": "attribute", "value": attr["Value"],
                    "source_id": source_id, "record_id": record_id,
                    "source_sha256": source_sha256,
                })
            if isinstance(value, list) and value:
                visit(value, path, ordinal, depth + 1)

    visit(nodes, "", "", 0)
    return {
        "schema": "careops-rims.private-xml-field-occurrences/1",
        "source_id": source_id, "record_id": record_id,
        "source_sha256": source_sha256, "occurrence_count": len(occurrences),
        "occurrences": occurrences,
        "private_values": True,
        "original_xml_tree_must_be_retained": True,
        "native_admission_authorised": False,
        "human_release_required": True,
    }
