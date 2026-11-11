# Decisions × Clinical Hub analytical reporting — 11 November 2026

**Status:** architecture and source contracts planned; no PBIP/TMDL, PBIR, RDL, semantic model deployment, dashboard deployment or data refresh is claimed. **Owner:** Decisions owns authoritative governance semantics; Clinical Hub owns reusable meeting-workspace data and links; Power BI reporting is a read-only optional consumer. This is a reporting plan, not another meeting implementation or permission grant.

## Scope and rationale

Reconcile the existing Decisions [Track 16](../../../modules/careops-decisions/conductor/tracks/track-16-governance-reporting_20260502/plan.md), [Dataverse dashboard YAML](../../../modules/careops-decisions/powerplatform/src/reporting/dataverse-dashboards.yaml), earlier [ADR 0006](../../../modules/careops-decisions/docs/adr/0006-power-bi-deferred-until-stable-data.md), and the unmerged [Clinical Hub RMS proposal (PR #312)](https://github.com/edithatogo/careops/pull/312). PR #304's standard-core proposal is also still unmerged; do **not** assume either PR is in main.

This programme specifies a **shared, versioned analytical contract**, not a new authoritative business register. Runtime core: SharePoint Lists/Libraries, native views/Word templates and Standard connectors, without Copilot, AI Builder, Power Automate Premium, Dataverse or Power BI. A PBIP/TMDL semantic model, PBIR interactive report and RDL paginated report are **optional reporting deliverables** requiring separately verified Power BI entitlements, workspace security and access. They must never become MVP dependencies. Existing Dataverse path remains supported through a separate adapter; avoid forcing a Dataverse-to-SharePoint migration or reinterpreting historical implementation claims.

## Deliverables and linked contracts

- [MoSCoW requirements](requirements.md) — business meaning, safety, privacy, cross-forum and operational prerequisites.
- [Model, measures and report design](design.md) — grains, joins, source/states, validation, dashboard, RDL and deployment.
- [Atomic executable tasks and evidence](plan.md) — selection, development, testing, rollout and separate acceptance.
- [Versioned analytics contract](../../../modules/careops-decisions/powerplatform/src/reporting/clinical-hub-analytics-contract.md) — canonical terminology and acceptance cases shared by Decisions and Clinical Hub.
- Existing Decisions Track 16 remains responsible for legacy Dataverse views; this track takes responsibility for the new optional reporting surfaces. No duplicate report business owner.

## Milestones

**A: Source and semantic contracts** → **B: Standard source adapters and synthetic analytical tables** → **C: PBIP/TMDL + PBIR dashboard** → **D: RDL governance pack** → **E: cross-output tests, RLS/permissions and native deployment** → **F: evaluation and optimisation**.

Current completed scope is **planning/contracts only**. Each of B–F remains open. CI billing/capacity issue #301, native RMS H2 access limitations and unverified adopted governance sources are explicit separate constraints; no false green CI or native qualification.

**Change boundary:** no tenant reads/writes, sharing, flow activation, credential change, email, operational deployment or clinical assertion is authorised by these plans.
