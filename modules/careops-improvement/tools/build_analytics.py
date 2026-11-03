"""Build local Power BI/Fabric analytics artifacts from a frozen projection.

The builder is deliberately offline and deterministic. It writes editable
source artifacts; it does not publish, refresh, or bind a native Fabric item.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path


FABRIC_SEMANTIC_SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json"
FABRIC_REPORT_SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json"
FABRIC_PAGES_SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json"
FABRIC_PAGE_SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.0.0/schema.json"
FABRIC_VISUAL_SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.6.0/schema.json"
FABRIC_REPORT_DEF_SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/3.1.0/schema.json"


def _load_source(path: Path) -> tuple[dict, list[dict]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    rows = value.get("initiatives") if isinstance(value, dict) else value
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ValueError("projection must be a list of initiative objects or contain an initiatives list")
    ids = [row.get("initiative_id") for row in rows]
    if any(not isinstance(item, str) or not item for item in ids):
        raise ValueError("every initiative row must have a non-empty initiative_id")
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate initiative_id in projection")
    return (value if isinstance(value, dict) else {"initiatives": rows}), rows


def _m_literal(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return '"' + str(value).replace('"', '""') + '"'


def _m_table(rows: list[dict], columns: list[tuple[str, str]]) -> str:
    names = ", ".join('"' + name + '"' for name, _ in columns)
    types = {"string": "type text", "int64": "Int64.Type", "double": "type number", "date": "type date"}
    rows_text = ",\n        ".join("{" + ", ".join(_m_literal(row.get(name)) for name, _ in columns) + "}" for row in rows)
    return f"let\n    Source = #table({{{names}}}, {{{rows_text}}}),\n    Typed = Table.TransformColumnTypes(Source, {{{', '.join('{"' + n + '", ' + types[t] + '}' for n, t in columns)}}})\nin\n    Typed"


def _partition(name: str, rows: list[dict], columns: list[tuple[str, str]]) -> dict:
    return {
        "name": name,
        "mode": "import",
        "source": {"type": "m", "expression": _m_table(rows, columns)},
    }


def _col(name: str, data_type: str, source: str | None = None) -> dict:
    result = {"name": name, "dataType": data_type, "sourceColumn": source or name, "summarizeBy": "none"}
    if data_type == "string":
        result["dataCategory"] = ""
    return result


def semantic_model(rows: list[dict], source_data: dict | None = None, model_name: str = "CareOpsImprovement") -> dict:
    """Return a TMSL star-schema model with frozen import partitions."""
    source_data = source_data or {"initiatives": rows}
    tasks = source_data.get("tasks", [])
    events = source_data.get("events", [])
    decisions = source_data.get("decisions", [])
    snapshots = source_data.get("snapshots", [])
    enriched_rows = []
    for row in rows:
        iid = row["initiative_id"]
        initiative_snapshots = [entry for entry in snapshots if entry.get("initiative_id") == iid]
        adoption_rows = [entry for entry in initiative_snapshots if entry.get("kind") == "adoption"]
        enriched_rows.append({
            **row,
            "task_count": row.get("task_count", sum(t.get("initiative_id") == iid for t in tasks) if "tasks" in source_data else None),
            "event_count": row.get("event_count", sum(t.get("initiative_id") == iid for t in events) if "events" in source_data else None),
            "decision_count": row.get("decision_count", sum(t.get("initiative_id") == iid for t in decisions) if "decisions" in source_data else None),
            "benefit_observations": row.get("benefit_observations", sum(t.get("kind") == "benefit" for t in initiative_snapshots) if "snapshots" in source_data else None),
            "adoption_observations": row.get("adoption_observations", len(adoption_rows) if "snapshots" in source_data else None),
            "adopted_services": row.get("adopted_services", len({t.get("service_id") for t in adoption_rows if t.get("service_id") and (t.get("status") == "adopted" or (isinstance(t.get("adopted_count"), (int, float)) and t["adopted_count"] > 0))}) if "snapshots" in source_data else None),
        })
    fields = [
        ("initiative_id", "string"), ("title", "string"), ("source_key", "string"),
        ("revision", "int64"), ("task_count", "int64"), ("event_count", "int64"),
        ("decision_count", "int64"), ("benefit_observations", "int64"),
        ("adoption_observations", "int64"), ("adopted_services", "int64"),
    ]
    measures = [
        {"name": "Registered initiatives", "expression": "DISTINCTCOUNT('FactInitiativeSnapshot'[initiative_id])", "formatString": "#,0"},
        {"name": "Initiative tasks", "expression": "SUM('FactInitiativeSnapshot'[task_count])", "formatString": "#,0"},
        {"name": "Initiative events", "expression": "SUM('FactInitiativeSnapshot'[event_count])", "formatString": "#,0"},
        {"name": "Recorded decisions", "expression": "SUM('FactInitiativeSnapshot'[decision_count])", "formatString": "#,0"},
        {"name": "Benefit observations", "expression": "SUM('FactInitiativeSnapshot'[benefit_observations])", "formatString": "#,0"},
        {"name": "Adoption observations", "expression": "SUM('FactInitiativeSnapshot'[adoption_observations])", "formatString": "#,0"},
        {"name": "Adopted services", "expression": "SUM('FactInitiativeSnapshot'[adopted_services])", "formatString": "#,0"},
    ]
    table_specs = [
        ("DimInitiative", [("initiative_id", "string"), ("title", "string"), ("source_key", "string"), ("revision", "int64")],
         [{"initiative_id": r.get("initiative_id"), "title": r.get("title"), "source_key": r.get("source_key"), "revision": r.get("revision")} for r in rows], []),
        ("FactInitiativeSnapshot", fields, [{name: row.get(name) for name, _ in fields} for row in enriched_rows], measures),
        ("FactInitiativeEvent", [("event_id", "string"), ("initiative_id", "string"), ("event_type", "string"), ("effective_at", "string"), ("observed_at", "string"), ("source_key", "string"), ("source_revision", "string")], source_data.get("events", []), []),
        ("FactDecision", [("decision_id", "string"), ("initiative_id", "string"), ("decision_kind", "string"), ("route", "string"), ("outcome", "string"), ("submitted_at", "string"), ("decided_at", "string"), ("source_key", "string")], source_data.get("decisions", []), []),
        ("FactMeasureObservation", [("snapshot_id", "string"), ("initiative_id", "string"), ("measure", "string"), ("value", "double"), ("unit", "string"), ("status", "string"), ("definition_version", "string"), ("observed_at", "string"), ("source_key", "string")], [r for r in source_data.get("snapshots", []) if r.get("kind") == "benefit"], []),
        ("FactAdoption", [("snapshot_id", "string"), ("initiative_id", "string"), ("service_id", "string"), ("measure", "string"), ("eligible_count", "int64"), ("adopted_count", "int64"), ("status", "string"), ("definition_version", "string"), ("observed_at", "string"), ("source_key", "string")], [r for r in source_data.get("snapshots", []) if r.get("kind") == "adoption"], []),
    ]
    tables = []
    for name, columns, records, table_measures in table_specs:
        normalized = [{column: record.get(column) for column, _ in columns} for record in records]
        tables.append({
            "name": name,
            "columns": [_col(col, kind) for col, kind in columns],
            **({"measures": table_measures} if table_measures else {}),
            "partitions": [_partition(name, normalized, columns)],
        })
    relationships = []
    for fact in ("FactInitiativeSnapshot", "FactInitiativeEvent", "FactDecision", "FactMeasureObservation", "FactAdoption"):
        relationships.append({
            "name": f"DimInitiative_{fact}",
            "fromTable": fact,
            "fromColumn": "initiative_id",
            "toTable": "DimInitiative",
            "toColumn": "initiative_id",
            "crossFilteringBehavior": "oneDirection",
        })
    return {
        "compatibilityLevel": 1600,
        "model": {
            "name": model_name,
            "culture": "en-AU",
            "defaultPowerBIDataSourceVersion": "powerBI_V3",
            "sourceQueryCulture": "en-AU",
            "discourageImplicitMeasures": True,
            "tables": tables,
            "relationships": relationships,
            "roles": [],
        },
    }


def _report_visual(name: str, x: int, y: int, width: int, height: int, visual_type: str, title: str, measure: str | None = None) -> dict:
    visual = {
        "visualType": visual_type,
        "query": {"queryState": {"Values": {"projections": []}}},
        "objects": {"title": [{"properties": {"text": {"expr": {"Literal": {"Value": "'" + title.replace("'", "''") + "'"}}}}}]},
    }
    if measure:
        visual["query"]["queryState"]["Values"]["projections"].append({"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "FactInitiativeSnapshot"}}, "Property": measure}}, "queryRef": measure, "nativeQueryRef": measure})
    return {
        "$schema": FABRIC_VISUAL_SCHEMA,
        "name": name,
        "position": {"x": x, "y": y, "z": 0, "height": height, "width": width, "tabOrder": y * 10 + x},
        "visual": visual,
    }


def _page(page_id: str, display_name: str, _visuals: list[dict]) -> dict:
    return {
        "$schema": FABRIC_PAGE_SCHEMA,
        "name": page_id,
        "displayName": display_name,
        "displayOption": "FitToPage",
        "height": 720,
        "width": 1280,
    }


def report_files() -> dict[str, dict]:
    """Return PBIR report files for an overview and a scorecard page."""
    overview_visuals = [
        _report_visual("registered-initiatives", 24, 24, 280, 150, "card", "Registered initiatives", "Registered initiatives"),
        _report_visual("tasks", 324, 24, 280, 150, "card", "Initiative tasks", "Initiative tasks"),
        _report_visual("decisions", 624, 24, 280, 150, "card", "Recorded decisions", "Recorded decisions"),
    ]
    scorecard_visuals = [
        _report_visual("benefit-observations", 24, 24, 360, 180, "card", "Benefit observations", "Benefit observations"),
        _report_visual("adoption-observations", 404, 24, 360, 180, "card", "Adoption observations", "Adoption observations"),
        _report_visual("adopted-services", 784, 24, 360, 180, "card", "Adopted services", "Adopted services"),
    ]
    return {
        "definition.pbir": {"$schema": FABRIC_REPORT_SCHEMA, "version": "4.0.0", "datasetReference": {"byPath": {"path": "../CareOpsImprovement.SemanticModel"}}},
        "definition/report.json": {"$schema": FABRIC_REPORT_DEF_SCHEMA, "themeCollection": {"baseTheme": {"name": "CY24SU10", "reportVersionAtImport": {"visual": "2.0.0", "report": "3.0.0", "page": "2.0.0"}, "type": "SharedResources"}}},
        "definition/pages/pages.json": {"$schema": FABRIC_PAGES_SCHEMA, "pageOrder": ["Overview", "Scorecard"], "activePageName": "Overview"},
        "definition/pages/Overview/page.json": _page("Overview", "Overview", overview_visuals),
        "definition/pages/Overview/visuals/active-initiatives/visual.json": overview_visuals[0],
        "definition/pages/Overview/visuals/tasks/visual.json": overview_visuals[1],
        "definition/pages/Overview/visuals/decisions/visual.json": overview_visuals[2],
        "definition/pages/Scorecard/page.json": _page("Scorecard", "Scorecard", scorecard_visuals),
        "definition/pages/Scorecard/visuals/benefit-observations/visual.json": scorecard_visuals[0],
        "definition/pages/Scorecard/visuals/adoption-observations/visual.json": scorecard_visuals[1],
        "definition/pages/Scorecard/visuals/adopted-services/visual.json": scorecard_visuals[2],
    }


def paginated_report(rows: list[dict]) -> bytes:
    """Generate a parameterized MSOLAP paginated scorecard."""
    ns = "http://schemas.microsoft.com/sqlserver/reporting/2016/01/reportdefinition"
    ET.register_namespace("", ns)
    root = ET.Element(f"{{{ns}}}Report")
    ET.SubElement(root, f"{{{ns}}}ReportParameters")
    parameters = root.find(f"{{{ns}}}ReportParameters")
    for name, prompt in (("WorkspaceXmlaEndpoint", "Power BI workspace XMLA endpoint"), ("SemanticModelCatalog", "Semantic model catalog"), ("AsOfPeriod", "Reporting period label")):
        param = ET.SubElement(parameters, f"{{{ns}}}ReportParameter", {"Name": name})
        ET.SubElement(param, f"{{{ns}}}DataType").text = "String"
        ET.SubElement(param, f"{{{ns}}}Prompt").text = prompt

    data_sources = ET.SubElement(root, f"{{{ns}}}DataSources")
    source = ET.SubElement(data_sources, f"{{{ns}}}DataSource", {"Name": "CareOpsSemanticModel"})
    connection = ET.SubElement(source, f"{{{ns}}}ConnectionProperties")
    ET.SubElement(connection, f"{{{ns}}}DataProvider").text = "OLEDB"
    ET.SubElement(connection, f"{{{ns}}}ConnectString").text = '="Provider=MSOLAP;Data Source=" & Parameters!WorkspaceXmlaEndpoint.Value & ";Initial Catalog=" & Parameters!SemanticModelCatalog.Value & ";"'
    ET.SubElement(connection, f"{{{ns}}}IntegratedSecurity").text = "true"

    data_sets = ET.SubElement(root, f"{{{ns}}}DataSets")
    dataset = ET.SubElement(data_sets, f"{{{ns}}}DataSet", {"Name": "InitiativeScorecard"})
    query = ET.SubElement(dataset, f"{{{ns}}}Query")
    ET.SubElement(query, f"{{{ns}}}DataSourceName").text = "CareOpsSemanticModel"
    ET.SubElement(query, f"{{{ns}}}CommandType").text = "Text"
    dax = '''EVALUATE\nSUMMARIZECOLUMNS(\n    'DimInitiative'[initiative_id],\n    'DimInitiative'[title],\n    "Tasks", [Initiative tasks],\n    "Events", [Initiative events],\n    "Decisions", [Recorded decisions],\n    "BenefitObservations", [Benefit observations],\n    "AdoptionObservations", [Adoption observations]\n)\nORDER BY 'DimInitiative'[initiative_id]'''
    ET.SubElement(query, f"{{{ns}}}CommandText").text = dax
    fields = ET.SubElement(dataset, f"{{{ns}}}Fields")
    for name in ("initiative_id", "title", "Tasks", "Events", "Decisions", "BenefitObservations", "AdoptionObservations"):
        field = ET.SubElement(fields, f"{{{ns}}}Field", {"Name": name})
        ET.SubElement(field, f"{{{ns}}}DataField").text = name

    sections = ET.SubElement(root, f"{{{ns}}}ReportSections")
    section = ET.SubElement(sections, f"{{{ns}}}ReportSection")
    body = ET.SubElement(section, f"{{{ns}}}Body")
    ET.SubElement(body, f"{{{ns}}}Height").text = "4.0in"
    items = ET.SubElement(body, f"{{{ns}}}ReportItems")
    def add_textbox(name, value, top, height="0.30in", bold=False):
        textbox = ET.SubElement(items, f"{{{ns}}}Textbox", {"Name": name})
        para = ET.SubElement(ET.SubElement(textbox, f"{{{ns}}}Paragraphs"), f"{{{ns}}}Paragraph")
        run = ET.SubElement(ET.SubElement(para, f"{{{ns}}}TextRuns"), f"{{{ns}}}TextRun")
        ET.SubElement(run, f"{{{ns}}}Value").text = str(value)
        style = ET.SubElement(run, f"{{{ns}}}Style")
        if bold:
            ET.SubElement(style, f"{{{ns}}}FontWeight").text = "Bold"
        ET.SubElement(textbox, f"{{{ns}}}Top").text = top
        ET.SubElement(textbox, f"{{{ns}}}Left").text = "0.15in"
        ET.SubElement(textbox, f"{{{ns}}}Height").text = height
        ET.SubElement(textbox, f"{{{ns}}}Width").text = "9.7in"

    add_textbox("Title", "CareOps Improvement Portfolio — Scorecard", "0.1in", "0.32in", True)
    add_textbox("AsOfPeriod", "=Parameters!AsOfPeriod.Value", "0.46in", "0.28in")

    tablix = ET.SubElement(items, f"{{{ns}}}Tablix", {"Name": "InitiativeScorecard"})
    tablix_body = ET.SubElement(tablix, f"{{{ns}}}TablixBody")
    columns = ET.SubElement(tablix_body, f"{{{ns}}}TablixColumns")
    widths = ("1.15in", "2.15in", "0.85in", "0.85in", "0.95in", "1.35in", "1.45in")
    for width in widths:
        col = ET.SubElement(columns, f"{{{ns}}}TablixColumn")
        ET.SubElement(col, f"{{{ns}}}Width").text = width
    body_rows = ET.SubElement(tablix_body, f"{{{ns}}}TablixRows")

    def tablix_row(name, values, expression=False):
        row = ET.SubElement(body_rows, f"{{{ns}}}TablixRow")
        ET.SubElement(row, f"{{{ns}}}Height").text = "0.30in"
        cells = ET.SubElement(row, f"{{{ns}}}TablixCells")
        for index, value in enumerate(values):
            cell = ET.SubElement(cells, f"{{{ns}}}TablixCell")
            contents = ET.SubElement(cell, f"{{{ns}}}CellContents")
            box = ET.SubElement(contents, f"{{{ns}}}Textbox", {"Name": f"{name}{index}"})
            para = ET.SubElement(ET.SubElement(box, f"{{{ns}}}Paragraphs"), f"{{{ns}}}Paragraph")
            run = ET.SubElement(ET.SubElement(para, f"{{{ns}}}TextRuns"), f"{{{ns}}}TextRun")
            ET.SubElement(run, f"{{{ns}}}Value").text = ("=Fields!" + value + ".Value") if expression else value
            ET.SubElement(run, f"{{{ns}}}Style")
            ET.SubElement(para, f"{{{ns}}}Style")
            ET.SubElement(box, f"{{{ns}}}Style")
    tablix_row("Header", ("Initiative ID", "Title", "Tasks", "Events", "Decisions", "Benefit observations", "Adoption observations"))
    tablix_row("Detail", ("initiative_id", "title", "Tasks", "Events", "Decisions", "BenefitObservations", "AdoptionObservations"), expression=True)
    column_hierarchy = ET.SubElement(tablix, f"{{{ns}}}TablixColumnHierarchy")
    column_members = ET.SubElement(column_hierarchy, f"{{{ns}}}TablixMembers")
    for _ in widths:
        ET.SubElement(column_members, f"{{{ns}}}TablixMember")
    row_hierarchy = ET.SubElement(tablix, f"{{{ns}}}TablixRowHierarchy")
    row_members = ET.SubElement(row_hierarchy, f"{{{ns}}}TablixMembers")
    header_member = ET.SubElement(row_members, f"{{{ns}}}TablixMember")
    ET.SubElement(header_member, f"{{{ns}}}KeepWithGroup").text = "After"
    ET.SubElement(header_member, f"{{{ns}}}RepeatOnNewPage").text = "true"
    detail_member = ET.SubElement(row_members, f"{{{ns}}}TablixMember")
    ET.SubElement(detail_member, f"{{{ns}}}Group", {"Name": "Details"})
    ET.SubElement(tablix, f"{{{ns}}}DataSetName").text = "InitiativeScorecard"
    ET.SubElement(tablix, f"{{{ns}}}Top").text = "0.85in"
    ET.SubElement(tablix, f"{{{ns}}}Left").text = "0.15in"
    ET.SubElement(tablix, f"{{{ns}}}Height").text = "0.60in"
    ET.SubElement(tablix, f"{{{ns}}}Width").text = "8.75in"
    ET.SubElement(tablix, f"{{{ns}}}Style")
    ET.SubElement(section, f"{{{ns}}}Width").text = "10in"
    page = ET.SubElement(section, f"{{{ns}}}Page")
    ET.SubElement(page, f"{{{ns}}}PageWidth").text = "11in"
    ET.SubElement(page, f"{{{ns}}}PageHeight").text = "8.5in"
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def _write_json(path: Path, value: object) -> bytes:
    data = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return data


def build(projection_path: Path, output: Path) -> dict:
    """Build the model, PBIR report, paginated report and Fabric REST payload."""
    source_data, rows = _load_source(projection_path)
    output.mkdir(parents=True, exist_ok=False)
    semantic = output / "CareOpsImprovement.SemanticModel"
    report = output / "CareOpsImprovement.Report"
    model_bim = _write_json(semantic / "model.bim", semantic_model(rows, source_data))
    pbism = _write_json(semantic / "definition.pbism", {
        "$schema": FABRIC_SEMANTIC_SCHEMA, "version": "1.0.0", "settings": {"qnaEnabled": False},
    })
    report_payload_files = report_files()
    report_bytes = {}
    for relative, value in report_payload_files.items():
        report_bytes[relative] = _write_json(report / relative, value)
    rdl = paginated_report(rows)
    rdl_path = output / "CareOpsImprovementScorecard.rdl"
    rdl_path.write_bytes(rdl)

    # Each REST definition payload belongs to one native Fabric item.
    definition_dir = output / "fabric-item-definitions"
    semantic_parts = [
        ("model.bim", semantic / "model.bim"),
        ("definition.pbism", semantic / "definition.pbism"),
    ]
    report_parts = [(path.relative_to(report).as_posix(), path) for path in sorted(p for p in report.rglob("*") if p.is_file())]
    paginated_parts = [("CareOpsImprovementScorecard.rdl", rdl_path)]

    def payload(parts):
        encoded = []
        for target, source in parts:
            data = source.read_bytes()
            encoded.append({"path": target, "payload": base64.b64encode(data).decode("ascii"), "payloadType": "InlineBase64"})
        return encoded

    semantic_definition = _write_json(definition_dir / "semantic-model.json", {"definition": {"parts": payload(semantic_parts)}})
    report_definition = _write_json(definition_dir / "report.json", {"definition": {"parts": payload(report_parts)}})
    paginated_definition = _write_json(definition_dir / "paginated-report.json", {"definition": {"format": "PaginatedReportDefinition", "parts": payload(paginated_parts)}})
    index_path = definition_dir / "release-index.json"
    _write_json(index_path, {
        "items": [
            {"displayName": "CareOpsImprovement", "type": "SemanticModel", "definition": "semantic-model.json"},
            {"displayName": "CareOpsImprovement", "type": "Report", "definition": "report.json", "dependsOn": "CareOpsImprovement semantic model"},
            {"displayName": "CareOpsImprovementScorecard", "type": "PaginatedReport", "definition": "paginated-report.json", "dependsOn": "CareOpsImprovement semantic model"},
        ],
        "native_deployment": "not performed",
    })
    return {
        "rows": len(rows),
        "model_sha256": hashlib.sha256(model_bim).hexdigest(),
        "pbism_sha256": hashlib.sha256(pbism).hexdigest(),
        "report_files": len(report_bytes),
        "rdl_sha256": hashlib.sha256(rdl).hexdigest(),
        "fabric_definition_count": 3,
        "release_index": str(index_path),
        "native_deployment": "not performed",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("projection", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.projection, args.output), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
