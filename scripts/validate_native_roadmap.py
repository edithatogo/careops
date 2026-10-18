"""Validate planning structure, not operational readiness or clinical authority."""
import json
import re
from graphlib import TopologicalSorter
from pathlib import Path
from typing import cast

TRACK_COUNT = 12
TASKS_PER_TRACK = 10


def validate(root: Path) -> tuple[int, int]:
    """Reject incomplete, inconsistent or falsely completed native track plans."""
    base = root / "conductor"
    folders = sorted((base / "tracks").glob("native_*_20260923"))
    if len(folders) != TRACK_COUNT:
        raise ValueError("Expected twelve native lifecycle tracks")
    roadmap = (base / "native-m365-roadmap.md").read_text(encoding="utf-8")
    index = (base / "tracks.md").read_text(encoding="utf-8")
    graph: dict[str, list[str]] = {}
    task_count = 0
    for number, folder in enumerate(folders, 1):
        raw: object = json.loads((folder / "metadata.json").read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError("Track metadata must be an object")
        metadata = cast(dict[str, object], raw)
        prefix = f"N{number:02}"
        if metadata.get("track_id") != folder.name or metadata.get("task_prefix") != prefix:
            raise ValueError("Track identity mismatch")
        if type(metadata.get("task_count")) is not int or metadata["task_count"] != TASKS_PER_TRACK:
            raise ValueError("Track task count mismatch")
        owner = metadata.get("owner")
        if not isinstance(owner, str) or not owner.strip():
            raise ValueError("Track owner role required")
        state = metadata.get("status")
        if state not in ("planned", "in_progress", "completed"):
            raise ValueError("Unsupported track status")
        dependencies = metadata.get("depends_on")
        if not isinstance(dependencies, list) or any(not isinstance(x, str) for x in dependencies):
            raise ValueError("Explicit dependency list required")
        values = cast(list[str], dependencies)
        if len(set(values)) != len(values):
            raise ValueError("Duplicate dependency")
        graph[folder.name] = values
        spec = (folder / "spec.md").read_text(encoding="utf-8")
        plan = (folder / "plan.md").read_text(encoding="utf-8")
        if not spec.strip() or not plan.strip():
            raise ValueError("Track specification and plan required")
        tasks = re.findall(r"^- \[([ x~])\] (N\d{2}\.\d{2}) (.+)$", plan, re.MULTILINE)
        if [key for _, key, _ in tasks] != [f"{prefix}.{i:02}" for i in range(1, 11)]:
            raise ValueError("Missing, duplicate or unordered task IDs")
        if any("accept " not in text.lower() for _, _, text in tasks):
            raise ValueError("Task acceptance criterion required")
        completed = [text for marker, _, text in tasks if marker == "x"]
        if any(not re.search(r"Evidence:\s*\S+", text) for text in completed):
            raise ValueError("Completed task requires an evidence reference")
        if state == "completed" and len(completed) != TASKS_PER_TRACK:
            raise ValueError("Completed track contains unfinished tasks")
        if state == "planned" and any(marker != " " for marker, _, _ in tasks):
            raise ValueError("Planned track contains started tasks")
        if f"tracks/{folder.name}/plan.md" not in roadmap or f"tracks/{folder.name}/" not in index:
            raise ValueError("Track is not discoverable from programme and index")
        task_count += len(tasks)
    if any(dependency not in graph for values in graph.values() for dependency in values):
        raise ValueError("Unknown track dependency")
    tuple(TopologicalSorter(graph).static_order())
    target = json.loads((root / "portfolio/native-credentialing-target.json").read_text(encoding="utf-8"))
    if target.get("structuredSystemOfRecord") != "full-dataverse" or target.get("sqliteUse") != "synthetic-test-adapter-only":
        raise ValueError("Native production target changed without roadmap reconciliation")
    return len(folders), task_count


if __name__ == "__main__":
    tracks, tasks = validate(Path(__file__).resolve().parents[1])
    print(f"Planning structure valid: {tracks} tracks, {tasks} tasks. Deployment not verified.")
