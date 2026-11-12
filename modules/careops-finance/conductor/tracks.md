# Project tracks

This file tracks major work items. Environment-specific hosts, network paths,
database names, gateways, workspaces, credentials, and identities belong in
protected deployment configuration rather than the reusable track registry.

---

## careops-shared-reporting-boundary

Status: [~]

Define the reusable Power BI, semantic-model, source-control, validation, ALM,
security, and deployment patterns that other CareOps modules may consume without
merging operational data or repository ownership.

Link: [./tracks/careops-shared-reporting-boundary_20260829/](./tracks/careops-shared-reporting-boundary_20260829/)

---

## access-to-powerbi-foundation

Status: [x]

Set up the private-repository-ready foundation for legacy database inventory,
data extraction, Power BI source control, and future ALM deployment.

---

## shared-finance-semantic-model

Status: [x]

Build the source-controlled semantic model package and standalone sample models.
Later consolidation remains a separate decision after source and business
validation.

---

## vmo-finance-dashboard

Status: [ ]

Build the first source-specific finance dashboard, including activity, ledger
reconciliation, financial-year totals, classification, and source and refresh
dependencies.

---

## medical-staff-dashboard

Status: [ ]

Build the second source-specific finance and workforce dashboard, including
staff history, payroll or FTE reporting, calendar reporting, and linked-source
dependency resolution.

---

## powerbi-alm-packaging

Status: [~]

Maintain PBIP, TMDL, and PBIR source, deployment manifests, validation gates,
and dry-run deployment preparation. Published refresh and live deployment remain
gated by approved database, schema, gateway, workspace, identity, and credential
configuration.

---

## managed-source-contracts

Status: [~]

Define the managed tables or views, required columns, parameters, gateway
assumptions, and source-to-model mappings that replace legacy local files for
published refresh. Live validation remains deployment-gated.

---

## first-dashboard-completion

Status: [~]

Complete the first standalone dashboard, semantic model, measures, report pages,
validation, and source exports. Live source validation remains open.

---

## second-dashboard-completion

Status: [~]

Complete the second standalone dashboard, semantic model, measures, report
pages, validation, and source exports. Live source validation remains open.

---

## dashboard-acceptance-and-publish-readiness

Status: [~]

Run business acceptance, refresh, source-control, access, privacy, security,
workspace, gateway, deployment, rollback, and support checks for both reports.

---

## shared-model-merge-readiness

Status: [ ]

Assess whether the completed reports should remain independent, become thin
reports over a proven shared semantic model, or use a composite model. Do not
merge merely to reduce repository count.

---

## mcp-standard-alignment

Status: [ ]

Track MCP assumptions and implementation touchpoints. MCP access remains
least-privilege, tool-allowlisted, and deployment-gated.

---

## finance-analytics-system-roadmap

Status: [~]

Develop a governed finance analytics system with source-specific reports and a
shared semantic layer only where definitions are stable. Remote dashboard
inventory must occur in place under approved access without copying large or
sensitive files into the repository.

---

## Recommended order

1. Maintain source-control-ready PBIR and TMDL exports and executable validation.
2. Complete sample-result and structural acceptance evidence.
3. Validate parameterised managed-source and gateway contracts.
4. Complete live-source business-result reconciliation.
5. Run publish-readiness and deployment dry run.
6. Decide whether shared-model consolidation adds value.
7. Promote only immutable, reviewed artifacts with rollback and support evidence.

- [~] **Track: Python 3.15 migration and qualification**
  *Link: [./tracks/python315_qualification_20261023/index.md](./tracks/python315_qualification_20261023/index.md)*
