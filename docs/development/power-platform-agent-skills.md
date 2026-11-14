# Power Platform agent-skills setup for CareOps Workforce

**Date:** 11 November 2026 · **State:** official Microsoft marketplaces and four plugins are **declared in repository settings** for GitHub Copilot and Claude Code; eight pinned Wals.pro Power Automate Markdown skills and their references are vendored in `.agents/skills`; actual agent-host activation and ChatGPT account installation remain separate.

## Repository installation (already committed)

- `.github/copilot/settings.json`: declarative Microsoft marketplace and plugin enablement for GitHub Copilot CLI and supported cloud agents.
- `.claude/settings.json`: the same declarations for Claude Code. Depending on installed host/version, external marketplace plugins may still require explicit installation after trusting the project.
- `.agents/skills/careops-power-platform/SKILL.md`: local agent routing, confidentiality and evidence rules.
- `.agents/skills/power-automate-*/`: **eight** pinned Wals-pro standalone Markdown skills, with bundled references; all source files unchanged from the pinned upstream and attributed in `.agents/THIRD_PARTY_NOTICES.md`. This does not install the Wals-pro CLI runtime or authenticating client.
- `scripts/power-platform-skill-bootstrap.sh`: optional host installation / source-audit bootstrap. Actual workstation execution is not reported as complete.

Do not confuse an enabled plugin entry with a successful local install or a live MCP connection. When the host starts, inspect the plugin list and tool availability.

## Verified upstreams (audit revision)

| Source | GitHub URL | Reviewed HEAD SHA | Baseline purpose |
|---|---|---|---|
| Microsoft Power Platform Skills | https://github.com/microsoft/power-platform-skills | `8021d27d517d81963da22e728125a26c9ecfbbe1` | Canvas apps, Power Automate, Dataverse marketplace |
| Microsoft Power CAT Skills | https://github.com/microsoft/power-cat-skills | `3408c7b0ab2414946adcdaf0ba87eb9ca320fcd2` | Power CAT Canvas authoring/performance complement |
| Microsoft Dataverse Skills | https://github.com/microsoft/Dataverse-skills | `27e6f6a3fef23075ede87d8e5f028cde29e0130e` | Optional Dataverse solution/admin/metadata skills |
| Wals-pro claude-power-automate | https://github.com/Wals-pro/claude-power-automate | `a9676c2f00d1645d55a21013105ccb2745860f20` | Optional third-party CLI/reference/workflow patterns |
| PowerPlatform-Skill (SkillEra IO) | **unverified** | none | Not installed until the publisher supplies a verifiable official URL and licence |

All four verified repositories carry MIT licences (retain upstream copyright and notices if vendoring files). SHA values are *audit snapshots*; the Copilot/Claude marketplace CLI currently installs by marketplace/plugin name and may fetch a newer version. To make a bit-for-bit pinned mirror, see `scripts/power-platform-skill-bootstrap.sh --checkout-sources`; review before running. Plugin CLI installation below is **not** pinned to these SHAs. This distinction must not be hidden in qualifications.

## Install in GitHub Copilot CLI

Run on an **authorised developer machine** (not in public CI):

```bash
copilot plugin marketplace add microsoft/power-platform-skills
copilot plugin marketplace add microsoft/power-cat-skills
copilot plugin install canvas-apps@power-platform-skills
copilot plugin install powercat-canvas-apps@power-cat-skills
copilot plugin install power-automate@power-platform-skills
copilot plugin install dataverse@power-platform-skills
```

The last plugin is for solution/Dataverse administration, **not a requirement to migrate the CHHHS SharePoint-based application to premium Dataverse**.

## Install in Claude Code

```bash
claude plugin marketplace add microsoft/power-platform-skills
claude plugin marketplace add microsoft/power-cat-skills
claude plugin install canvas-apps@power-platform-skills
claude plugin install powercat-canvas-apps@power-cat-skills
claude plugin install power-automate@power-platform-skills
claude plugin install dataverse@power-platform-skills
```

Use `scripts/power-platform-skill-bootstrap.sh --copilot` or `--claude` to invoke these commands with prerequisite checks, or `--check` to inspect the planned installation. Installing a plugin modifies the local coding agent's plugin registry, **not the GitHub repository**. Current official Microsoft Canvas authoring requires .NET 10+ and an existing coauthoring-enabled app open in Power Apps Studio; an agent plugin cannot create the initial studio app or grant tenant rights by itself.

## Optional third-party Power Automate skill

The verified source is `Wals-pro/claude-power-automate`; **eight standalone skills and references have been copied into `.agents/skills`**; it includes standalone `skills/power-automate-reference`, `skills/power-automate-solutions`, `skills/power-automate-workflow-patterns`, and `skills/power-automate-action-configuration`. Prefer official Microsoft Power Automate plugin first. No third-party CLI, installer or Python package is executed automatically; use `--checkout-sources` to retrieve a pinned, **ignored** local source checkout and review independently before opting in. The Markdown skill sources are MIT-attributed in `.agents/THIRD_PARTY_NOTICES.md`.

## ChatGPT installation

The GitHub/Copilot or Claude `/plugin` commands do **not** install plugins in ChatGPT. Search ChatGPT **Settings → Plugins** (or its plugin directory) for an officially listed Microsoft Dataverse or Power Platform integration and connect it explicitly if offered. It cannot be silently installed by repo configuration. At the time of this request the ChatGPT plugin-directory search did not expose exact `dataverse`, `canvas-apps` or `powercat-canvas-apps` plugin IDs; a direct Dataverse plugin suggestion also failed to resolve. **No ChatGPT account installation is claimed.** A separate Microsoft SharePoint connector may be connected without adding the developer authoring plugins.

## Governance, security and validation

- Do not run unreviewed remote install.js, arbitrary startup hooks or marketplace scripts in CI.
- Keep third-party code under ignored `.local-agent-marketplaces/`, never commit full mirrors, credentials, tokens or individual CHHHS plans.
- Before any version bump review upstream licences, Git commits, scripts and hooks, environment permissions and dependency changes. Pin/review updates deliberately.
- This repository routing skill is plain Markdown and is available to agents that load repo-local `.agents/skills`, but it does not itself grant external network, PAC CLI, Power Apps Studio or tenant access.
- For an installation receipt: record agent version, plugin list, marketplace source, actual resolved commit/version, prerequisites and the first successful read-only Canvas/Flow/Dataverse tool call. None of those receipts have been generated in a developer host by this repository change.

See: [Microsoft Canvas App plugin](https://microsoft.github.io/power-platform-skills/plugins/canvas-apps/), [Power Automate plugin](https://microsoft.github.io/power-platform-skills/plugins/power-automate/) and [Dataverse skills](https://github.com/microsoft/Dataverse-skills).

## Complete marketplace catalogue reconciliation — 11 November 2026

The official [Microsoft Power Platform Skills site](https://microsoft.github.io/power-platform-skills/#plugins) currently advertises 11 plugins. The [Power CAT marketplace](https://github.com/microsoft/power-cat-skills) registers 14. The repo-local `.github/copilot/settings.json`, `.claude/settings.json` and optional `scripts/power-platform-skill-bootstrap.sh` have been expanded to the **complete 25-plugin combined set**, including all originally requested Canvas/Dataverse/Power Automate items. This is **repository configuration and an installation script**, not a report of actual installation on a developer workstation. Broad optional plugins should not be granted runtime or tenant privileges until their need, hooks and permissions are reviewed.

As observed in the current ChatGPT session, `skills://plugins/dataverse/*` is available. The Microsoft Canvas authoring and FlowAgent marketplace plugins are not registered as callable ChatGPT plugins simply because their Copilot/Claude configurations exist. ChatGPT plugin discovery returned no exact matching listing. No account-wide ChatGPT install of those is claimed. PowerPlatform-Skill (SkillEra IO) has no verified canonical source and remains excluded.
