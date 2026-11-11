"""Offline checks for CareOps Power Platform agent-skill declarations.

No host/plugin installation, network access, tenant secrets or platform changes.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
REQUIRED={
 "canvas-apps@power-platform-skills",
 "powercat-canvas-apps@power-cat-skills",
 "power-automate@power-platform-skills",
 "dataverse@power-platform-skills",
}
MARKETS={"power-platform-skills","power-cat-skills"}
VENDORED={
 "power-automate-action-configuration","power-automate-api-client",
 "power-automate-docs","power-automate-expression-syntax",
 "power-automate-reference","power-automate-run-forensics",
 "power-automate-solutions","power-automate-workflow-patterns",
}

def validate(root:Path=ROOT)->dict:
    problems=[]
    for relative in (".claude/settings.json",".github/copilot/settings.json"):
        path=root/relative
        if not path.is_file():
            problems.append(f"missing {relative}");continue
        try:
            cfg=json.loads(path.read_text(encoding="utf-8"))
            if set(cfg.get("extraKnownMarketplaces",{}))!=MARKETS:
                problems.append(f"{relative}: unexpected marketplaces")
            enabled=cfg.get("enabledPlugins",{})
            if not REQUIRED.issubset({k for k,v in enabled.items() if v is True}):
                problems.append(f"{relative}: missing required enabled plugins")
            if any(v is not True for v in enabled.values()):
                problems.append(f"{relative}: disabled/unexpected plugin setting")
        except (ValueError, OSError) as exc:
            problems.append(f"{relative}: {exc}")
    skills=root/".agents/skills"
    if not (skills/"careops-power-platform/SKILL.md").is_file():
        problems.append("missing CareOps skill router")
    for name in sorted(VENDORED):
        file=skills/name/"SKILL.md"
        if not file.is_file():
            problems.append(f"missing {file.relative_to(root)}")
        elif not file.read_text(encoding="utf-8").startswith("---"):
            problems.append(f"invalid skill frontmatter {name}")
    if not (root/".agents/THIRD_PARTY_NOTICES.md").is_file():
        problems.append("missing third-party attribution")
    if problems:raise ValueError("\n".join(problems))
    return {"repository_config":"valid","official_plugin_declarations":len(REQUIRED),
            "vendor_skills":len(VENDORED),"host_installed":False,
            "chatgpt_installed":False,"tenant_qualified":False}

if __name__=="__main__":
    print(json.dumps(validate(),indent=2))
