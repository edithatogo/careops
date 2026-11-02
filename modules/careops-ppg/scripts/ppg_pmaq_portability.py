"""Build the fictional PGY1 example using the shared accreditation contracts."""

import argparse
import json
from pathlib import Path

from scripts.ppg_accreditation_contract import validate_graph
from scripts.ppg_accreditation_decisions_native import project_native_case
from scripts.ppg_scheme_adoption import project_scheme


def prepare(fixture, contract, vocabularies):
    if fixture.get("fixtureOnly") is not True:
        raise ValueError("Fictional PGY1 fixture required")
    g, d = fixture["graph"], fixture["decisions"]
    validate_graph(g)
    dp = project_native_case(d, g, "2026-11-01")
    (framework,) = g["frameworks"]
    fk, ed = framework["FrameworkKey"], framework["EditionKey"]
    profile = project_scheme(fk, contract, vocabularies, scheme_key="scheme:pmaq-pgy1")
    (amc,) = [
        s
        for s in fixture["sourceReferences"]
        if s["sourceRole"] == "framework_national_standards"
    ]
    notes, conflict = fixture["requirementLabels"], fixture["sourceConflict"]
    if conflict["disposition"] != "conflicted; excluded from operative criteria":
        raise ValueError("Publisher conflict must remain explicit")
    if any(r["source"]["sha256"] != amc["sha256"] for r in g["requirements"]):
        raise ValueError("Requirement source mismatch")
    source = g["requirements"][0]["source"]
    briefs = []
    rows = {
        k: []
        for k in [
            "framework",
            "requirement",
            "context",
            "evidence",
            "mapping",
            "assessment",
            "decision",
            "event",
        ]
    }
    rows["framework"] = [
        dict(
            Title="AMC prevocational training — bounded PGY1 example",
            FrameworkKey=fk,
            Issuer="Australian Medical Council",
            EditionLabel=ed,
            EditionStatus="Published",
            SourceURL=amc["url"],
            Applicability="Fictional PGY1 program and term. QH-IMP-476 conflict retained in fixture.",
            Scheme_x0020_configuration=json.dumps(profile, separators=(",", ":")),
        )
    ]
    for r in g["requirements"]:
        code = r["publisherCode"]
        rows["requirement"].append(
            dict(
                Title=notes[code],
                RequirementKey=r["RequirementKey"],
                FrameworkKey=fk,
                RequirementCode=code,
                RequirementKind=r["kind"].title(),
                ParentRequirementKey=r["ParentRequirementKey"],
                SourceLocator=r["source"]["locator"],
                RequirementText=notes[code],
                PublisherCode=code,
                RequirementNodeKind=r["kind"].title(),
                PublicationKey=source["PublicationKey"],
                EditionKey=ed,
                CaptureKey=source["CaptureKey"],
                SourceSHA256=amc["sha256"],
                SourceURL=amc["url"],
            )
        )
    for s, c in zip(g["scopes"], g["contexts"]):
        rows["context"].append(
            dict(
                Title=c["purpose"],
                ReviewContextKey=c["ReviewContextKey"],
                ScopeKey=s["ScopeKey"],
                ScopeDescription=json.dumps(s),
                Purpose=c["purpose"],
                ContextState="Draft",
            )
        )
    for m in g["mappings"]:
        e = next(
            x
            for x in g["evidenceVersions"]
            if x["EvidenceVersionKey"] == m["EvidenceVersionKey"]
        )
        rows["mapping"].append(
            dict(
                Title="Fictional PGY1 proposed relevance",
                MappingKey=m["MappingKey"],
                DocumentUID=e["EvidenceKey"],
                DocumentVersion=e["sourceVersion"],
                RequirementKey=m["RequirementKey"],
                MappingState="Proposed",
                Rationale=m["rationale"],
                ReviewContextKey=m["ReviewContextKey"],
                EvidenceVersionKey=e["EvidenceVersionKey"],
            )
        )
    for a in g["assessments"]:
        rows["assessment"].append(
            dict(
                Title="Fictional PGY1 independent judgement",
                AssessmentKey=a["AssessmentKey"],
                ReviewContextKey=a["ReviewContextKey"],
                RequirementKey=a["RequirementKey"],
                Applicability="Unknown",
                Outcome="Unknown",
                AssessmentRationale=a["narrative"],
            )
        )
    for i, x in enumerate(d["decisions"], 1):
        data = {
            "fixtureOnly": True,
            "version": i,
            "decision": x,
            "condition": d["conditions"] if i == 2 else [],
            "changes": d["changes"] if i == 2 else [],
            "sourceConflict": conflict,
        }
        briefs.append(data)
        e = g["evidenceVersions"][i - 1]
        rows["evidence"].append(
            dict(
                Title="Fictional PGY1 brief revision " + str(i),
                EvidenceVersionKey=e["EvidenceVersionKey"],
                EvidenceKey=e["EvidenceKey"],
                SourceSystem=e["sourceSystem"],
                SourceItemKey=e["sourceKey"],
                ExactVersion=str(i),
            )
        )
    rows["decision"] = [x["fields"] for x in dp["decisions"]]
    rows["event"] = [x["fields"] for x in dp["events"]]

    return {"schemaVersion": 1, "fixtureOnly": True, "rows": rows, "briefs": briefs}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--vocabularies",
        type=Path,
        help="Exact previous deployment vocabulary configuration",
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]

    def read(name):
        return json.loads((root / name).read_text())

    result = prepare(
        read("tests/fixtures/accreditation/pmaq-pgy1.json"),
        read("config/accreditation-contract-v2.json"),
        json.loads(args.vocabularies.read_text())
        if args.vocabularies
        else read("config/accreditation-scheme-vocabularies-v1.json"),
    )
    with args.output.open("x") as stream:
        json.dump(result, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
