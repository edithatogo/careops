# Technical ALM qualification: Power Platform, Dataverse and Fabric

Status 11 November 2026: **existing source controls are advanced; platform-wide native CI/CD is not frontier-qualified**. This is a technical reference and implementation map, not deployment permission. The cross-cutting [EF technical track](../conductor/tracks/engineering_frontier_20261111/index.md) and module-native Conductor tracks retain tasks.

| Layer | Already present in CareOps | Required technical acceptance / owning workstream |
| --- | --- | --- |
| Authored Power Platform solution source | PAC solution build scripts, WDL flow/source checks, publisher/component inventories, environment-neutral templates | Pack/unpack/source parity, component closure, WDL/schema checks, connection refs and workflow state, exact module definitions — EF-07 + existing native N01 |
| Dataverse solution/source identity | Exact-target guards, schema/SDK tests, source packages | Supported isolated environment import and solution checker with explicit environment, ALM solution layer comparison, RBAC/row security, ETag/concurrency, restore — native N03/N10 |
| Power Apps UI | Fictional browser tests and older Power Apps Test Engine material | Use maintained Playwright tests for actual supported app flows, accessible UI states and permissions; deprecated Test Engine is historical only — EF-04 |
| Power Automate | Offline flow-definition validation, stopped-flow recovery receipts in selected modules | Real native two-environment replay/idempotency/concurrency/permission/rollback tests with approved standard connector route; never activate from source CI — EF-07 |
| Fabric and Power BI | PBIP/TMDL source, separate Power BI report/model packaging and selected read-only model checks; Workforce has private stage-bound ALM | Build semantic model/report from frozen source, validate TMDL/definition and deployment-bound parameters, verify deployment stage/item identity, measure and role-level readback and rollback — EF-07 and Finance/Workforce/RIMS module owners |
| Shared engineering delivery | Pinned GitHub Actions, shared security/privacy/workflow gates, SPDX and exact source archives, optional development canaries | Running current-head CI, verified full-scope tests, independent artifact hashes/SBOM, immutable release source; signing only if supported; no bypass — EF-00/03/06 |
| Agent/harness | AGENTS.md, two agents, two skills, module Conductor tracks, parent harness | Context packet relevance, deterministic tool mediation, synthetic adversarial tests, task/contract replay and measured test selection — EF-01/02/03 |

## Microsoft native routes to qualify, not assume

- **Power Platform:** PAC CLI `solution pack/unpack/check/import` with exact environment, independently verified source/component graph, immutable build products and compatible Power Platform pipelines when licensing/environment admission is established.
- **Dataverse:** supported managed solutions and native Git integration where the target Git provider/tenant topology supports it; preserve traditional PAC path otherwise. Source auth profile alone is not proof of a live target.
- **Fabric:** supported Git integration, deployment pipeline APIs, Fabric REST item-definition APIs, `fabric-cicd` for supported artifacts and `fab` CLI as *optional* qualified integrations. Check actual licensing/capacity, API/item support, service-principal scope, workspace permissions, region/network constraints and rollback before enabling.
- **Power BI:** PBIP/TMDL source-aware validation and metadata/source definition checks first, then model-level tests, RLS and source/workspace parity. Keep tenant-specific secrets and bind parameters outside Git.
- **Standard/core dependency:** use SharePoint standard connectors and non-premium routes first; avoid making full Dataverse, Copilot, Fabric capacity or paid Process Mining required for standalone core modules.

Official documentation verified 11 November 2026:
- [PAC solution commands](https://learn.microsoft.com/en-us/power-platform/developer/cli/reference/solution)
- [Power Platform enterprise ALM](https://learn.microsoft.com/en-us/power-platform/architecture/reference-architectures/enterprise-power-platform-alm)
- [Fabric CI/CD overview](https://learn.microsoft.com/en-us/fabric/cicd/cicd-overview)
- [Fabric Git automation APIs](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/git-automation)
- [Fabric-cicd for PBIP](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-deploy-fabric-cicd)
- [Power Apps Test Engine deprecation / Playwright](https://learn.microsoft.com/en-us/power-platform/test-engine/playwright)

**Do not combine environments as a prerequisite for release.** Each module retains its own tenant/runtime boundary, and source-only technical improvements can be qualified without a live tenant or production approval.
