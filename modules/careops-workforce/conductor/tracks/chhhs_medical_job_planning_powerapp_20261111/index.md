# CHHHS medical job planning — Canvas App bootstrap and delivery

**Status:** [ ] Planned; not implemented or commissioned. **Date:** 11 November 2026. **Owner:** proposed CHHHS Medical Administration / CMO delegate; technical stewardship: CareOps-Workforce and CHHHS Digital Health. **Source of truth:** this track; cross-link to the workforce module and CareOps portfolio index. **Scope:** a separable medical-workforce application, not a change to live PPG or credentialing workflows.

## Outcome and boundary

Deliver an accessible, maintainable, standard-connector **CHHHS Medical Job Planning** Canvas App in a **solution ZIP** that can be imported into an authorised Power Platform development environment, plus SharePoint provisioning, deployment settings, source, automated tests and an operator guide. Pilot with synthetic profiles before any real individual job plan. Source delivery and native tenant qualification are distinct. No tenant/site credentials, approved policy, live employee data, site or application deployment are currently asserted.

The supplied work instruction is a **draft**, not a confirmed operative CHHHS policy. Sensitive original documents and individual job plans are forbidden in Git and CI; only synthetic examples and non-identifiable design insights are committed (see source-boundary.md). The application is a **prospective job-planning workflow rather than a timesheet**.\n\nA 2024 PnP [Weekly Timesheet Template](https://pnp.github.io/powerplatform-samples/samples/weekly-timesheet-sharepoint/) is the **candidate** bootstrap; it is not a medical job-planning product nor an actively maintained upstream dependency. Evaluate whether a fresh Microsoft Lists-generated canvas app is safer/less costly before reuse (decision gate B03). Preserve licence and provenance evidence and record asset-level reuse. Do not introduce premium Dataverse or Copilot dependencies in the baseline.

## Documents

- [Sanitised findings from confidential design references](reference-design-findings.md)
- [Hard private-source exclusion and CI data-leakage controls](source-boundary.md)


- [Requirements and MoSCoW](requirements.md)
- [Architecture, data and integration design](design.md)
- [Contracts, evidence and acceptance gates](contracts.md)
- [Granular executable track plan](plan.md)
- [Existing medical-job-planning Mermaid diagrams](../../../../careops-ppg/docs/medical-job-planning/README.md) (pending PR #310, not merged at planning time)
- [CareOps Workforce module](../../../README.md)

## Decision summary

1. Use standard SharePoint Lists, SharePoint document libraries, Canvas App and standard Power Automate; preserve service-owner authority and **enforce permissions at SharePoint**. UI hiding is not access control.
2. Separate **prospective approved plan revisions** from **retrospective delivered activity**; no overwriting an approved baseline.
3. Do not reuse the timesheet's flat day-of-week columns as the canonical multi-week, multi-session medical plan. Normalise sessions and allocate hours explicitly with one principal activity code per segment.
4. Implement *configurable, versioned* industrial rules, with the MOCA7 SMO 10% CST requirement as a validation use case; never silently apply SMO rules to RMOs, MPPPs or VMOs. Confirm actual governing agreements, contracts, approved PPGs and delegations before operational adoption.
5. Split **officer consultation/acceptance**, **industrial validation**, and **delegated approval** as separate signed/attributed transitions. Approvals remain subject to tenant-authorised approval pathways.
6. Output an unmanaged solution for dev, managed artifact for test/prod only after packaging gates; export source and exact-version provenance. A local ZIP alone is not proof of successful import or production readiness.

## Gates / delivery evidence

- G0: sample provenance, source ZIP hash, licence, reproducible import and retrofit feasibility; bootstrap decision recorded.
- G1: requirements, security/privacy/data classification and CHHHS delegate/PPG authority formally accepted or annotated as pending.
- G2: SharePoint schema and synthetic reference dataset provisioned/validated in development with least privilege.
- G3: app/flows, server-side permissions, concurrency and immutable revision behaviour verified.
- G4: solution pack, import, publish, smoke test, rollback and promotion logs on authorised environment.
- G5: clinical/medical workforce, HR/IR, Digital Health, records/privacy and accessibility acceptance; pilot approval separately authorised.
- G6: operational pilot, assurance measures, maintenance owner and handover. Production go-live is not part of source-only completion.

**Dependencies:** Microsoft 365/Power Platform tenant & rights, approved SharePoint site, actual CHHHS PPG templates and current adopted job-planning policy/procedure, delegated role matrix, industrial/HR review; no authority is assumed from the draft job-plan documents.

## Capability positioning

**Canonical owner: CareOps Workforce.** Job planning is an operational workforce management function allied to credentialing, not a policy/document lifecycle feature. Credentialing supplies optional read-only practitioner reference and SoCP constraints, not a shared operational database or permission to activate/deactivate clinical practice. CareOps-PPG may hold authoritative PPG links and document templates through a read-only adapter. CareOps-Approve/Decisions may expose opt-in event contracts after independent qualification. CareOps-Finance and the existing Workforce PBIP may consume privacy-minimised, source-qualified, aggregate workforce measures; existing dashboard data grains are not automatically an authoritative establishment or job-plan baseline.

## Scheduled and practitioner-led review lifecycle

- [Policy-based review scheduler and dual-role practitioner/approver dashboards](lifecycle-dashboard-design.md)
- [List, flow, automation and artefact inventory](flow-list-artefact-catalogue.md)

The review schedule is effective-dated and subject to adopted CHHHS policy; practitioners may draft at any time and explicit submission triggers the review route. The old approved version remains active until a new authorised version reaches its effective date. Approval and historical version access are restricted by source-enforced permissions. Hosted Microsoft Approvals is not presumed to be a Dataverse-free component; the standard-only baseline has a custom decision ledger and workflow.

- [Review/versioning reference qualification (local synthetic engine; tenant qualification open)](review-versioning-qualification-20261111.md)
