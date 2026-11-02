"""Qualify retained policy bodies without changing register identifiers or authority."""
import hashlib
import io
import re
import argparse
import json
from pathlib import Path, PurePosixPath
import zipfile


def unpack_single_document(data, max_bytes=32 * 1024 * 1024):
    """Read a single wrapped original; never flatten a multi-version recovery bundle."""
    with zipfile.ZipFile(io.BytesIO(data)) as package:
        members = [m for m in package.infolist() if not m.is_dir() and
                   PurePosixPath(m.filename).suffix.lower() in {".doc", ".docx", ".pdf"}]
        if len(members) != 1:
            raise ValueError("Package requires an explicit document/version selection")
        member = members[0]
        path = PurePosixPath(member.filename)
        if path.is_absolute() or ".." in path.parts or "\\" in member.filename or member.flag_bits & 1:
            raise ValueError("Unsafe or encrypted document member")
        if member.file_size > max_bytes:
            raise ValueError("Wrapped document exceeds bounded extraction size")
        content = package.read(member)
    return {"name": member.filename, "content": content,
            "containerSHA256": hashlib.sha256(data).hexdigest(),
            "memberSHA256": hashlib.sha256(content).hexdigest()}


def family(value):
    value = re.sub(r"[\s_]", "", value.upper()).replace("–", "-")
    return re.split(r"-V-?\d", value)[0]


def aliases(value):
    parts = re.split(r"\bwas\b|[\r\n]", value or "", flags=re.I)
    return [match for part in parts for match in re.findall(
        r"[A-Za-z]{2,8}\d+/\d+|[A-Za-z]{2,8}-(?:[A-Za-z0-9_]+-){2,}[A-Za-z0-9./]+",
        re.sub(r"\s+", "", re.sub(r"\s+V(?=\d)", "-V", part, flags=re.I)))]


def number(value):
    misplaced = re.search(r"-V-?\d+(?:\.\d+)?-(\d+)-\d{2}/\d{2,4}$", value.upper())
    if misplaced:
        return misplaced.group(1)
    base = re.sub(r"-\d{2}/\d{2,4}$", "", family(value))
    found = re.findall(r"(?:-|(?<=[A-Z]))(\d+(?:\.\d+[A-Z]?)?(?:/\d+)?)", base)
    if len(found) > 1 and re.fullmatch(r"\d+\.\d+", found[-1]):
        found.pop()  # A trailing decimal version without V; retain the original literal.
    return found[-1] if found else None


def printed_headers(text):
    lines = re.findall(r"Document\s*(?:Number|No\.?|ID)\s*[:.]?\s*<?\s*([A-Za-z][^\r\n]{1,160})",
                       heading_text(text) or text[:1800], re.I)
    return [code for line in lines for code in aliases(line)]


def heading_words(text):
    stop = set("a the of and in for to with procedure guidelines guideline patient patients management care all by including previously was from hospital health services service drug infusion standing order standard administration".split())
    words = re.findall(r"[a-z]+", text.replace("TM", "").lower())
    return {w[:-1] if w.endswith("s") and len(w) > 4 else w for w in words if w not in stop}


def heading_text(text):
    prefix = text[:1800]
    marker = re.search(r"(?im)^\s*(?:Purpose|Scope|Introduction|Background|AREA\s*/\s*STAFF|Authority to administer|Presentation|Policy Statement|Intent of this policy)\b", prefix)
    return prefix[:marker.start()] if marker else None


def qualify_body(policy, document, *, native_uid=None, variant=None, title_review=None):
    """Return a qualified retained binding or an explicit evidence hold.

    The caller verifies original bytes against sha256 before supplying extracted
    full text. Reviewed exceptions are private, capture-pinned evidence, not rules
    that silently repair an organisation's identifiers.
    """
    text = document.get("text", "")
    if (document.get("scope") != "full document" or document.get("error") or
            len(text.strip()) < 200):
        return {"status": "held", "reason": "Full readable body unavailable"}
    digest = hashlib.sha256(text.encode()).hexdigest()
    if document.get("textSHA256") != digest or not re.fullmatch(r"[a-f0-9]{64}", document.get("sha256", "")):
        raise ValueError("Body capture or text preimage invalid")
    if native_uid is not None and native_uid != policy["DocumentUID"]:
        raise ValueError("Native capture belongs to another policy UID")
    expected = aliases(policy.get("sourceDocumentId"))
    printed = printed_headers(text)
    title = heading_words(policy.get("sourceTitle", ""))
    heading = heading_text(text)
    shared = title & heading_words(heading or "")
    heading_ok = bool(heading and title) and len(shared) >= min(2, len(title)) and len(shared) / len(title) >= .5
    if title_review:
        anchor = title_review.get("anchor", "")
        reviewed_heading = heading or text[:1800]
        if "headingStart" in title_review or "headingEnd" in title_review:
            start, end = title_review.get("headingStart"), title_review.get("headingEnd")
            if not (type(start) is int and type(end) is int and 0 <= start < end <= len(text)
                    and end - start <= 1800):
                raise ValueError("Reviewed heading range invalid")
            reviewed_heading = text[start:end]
        heading_ok = (title_review.get("sha256") == document["sha256"] and
                      bool(title_review.get("reason")) and len(anchor) >= 8 and
                      " ".join(anchor.casefold().split()) in " ".join(reviewed_heading.casefold().split()))
    if not heading_ok:
        return {"status": "held", "reason": "Heading/clinical scope not qualified"}
    same_family = any(number(e) and number(e) == number(p) and family(e) == family(p)
                      for e in expected for p in printed)
    approved_variant = False
    if variant:
        e, p = variant.get("expectedId"), variant.get("printedId")
        if (e not in expected or p not in printed or variant.get("sha256") != document["sha256"] or
                not variant.get("reason")):
            raise ValueError("Reviewed identifier variant preimage changed")
        if not number(e) or number(e) != number(p):
            return {"status": "held", "reason": "Printed document number conflicts with register"}
        approved_variant = True
    specific_printed = [p for p in printed if number(p)]
    if not same_family and not approved_variant and not (native_uid and not specific_printed):
        return {"status": "held", "reason": "No qualified printed-family or native UID binding"}
    if not printed and not native_uid:
        return {"status": "held", "reason": "Title alone cannot establish identity"}
    return {"status": "retained-body-bound", "uid": policy["DocumentUID"],
            "sha256": document["sha256"], "textSHA256": digest, "printedIds": printed,
            "identifierVariant": approved_variant, "nativeUIDBinding": bool(native_uid),
            "printedIdentifierIncomplete": not bool(specific_printed),
            "editionRelation": "literal identifier matches" if any(e.upper() == p.upper() for e in expected for p in printed)
                else "retained edition or identifier variant; register edition not established",
            "currentAuthority": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text())
        policies = {p["DocumentUID"]: p for p in data["policies"]}
        documents = {d["sha256"]: d for d in data["documents"]}
        if len(policies) != len(data["policies"]) or len(documents) != len(data["documents"]):
            raise ValueError("Duplicate policy or capture identity")
        results, seen = [], set()
        for binding in data["bindings"]:
            key = (binding["uid"], binding["sha256"])
            if key in seen or key[0] not in policies or key[1] not in documents:
                raise ValueError("Duplicate binding or unknown policy/capture identity")
            seen.add(key)
            result = qualify_body(policies[key[0]], documents[key[1]],
                                  native_uid=binding.get("nativeUID"),
                                  variant=binding.get("variant"), title_review=binding.get("titleReview"))
            results.append({"uid": key[0], "captureSHA256": key[1], **result})
        with args.output.open("x") as stream:
            json.dump({"schemaVersion": 1, "results": results}, stream, ensure_ascii=False)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.exit(2, f"Cannot qualify retained bodies: {exc}\n")


if __name__ == "__main__":
    main()
