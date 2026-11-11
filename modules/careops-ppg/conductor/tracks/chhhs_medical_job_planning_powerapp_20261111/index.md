# CHHHS medical job planning — Canvas App bootstrap and delivery

**Status:** [ ] Planned; not implemented or commissioned. **Date:** 11 November 2026. **Owner:** proposed CHHHS Medical Administration / CMO delegate; technical stewardship: CareOps-PPG and CHHHS Digital Health. **Source of truth:** this track; cross-link to the module tracks register and the CareOps portfolio index. **Scope:** a separable medical-workforce application, not a change to live CareOps-PPG document-control workflows.

## Outcome and boundary

Deliver an accessible, maintainable, standard-connector **CHHHS Medical Job Planning** Canvas App in a **solution ZIP** that can be imported into an authorised Power Platform development environment, plus SharePoint provisioning, deployment settings, source, automated tests and an operator guide. Pilot with synthetic profiles before any real individual job plan. Source delivery and native tenant qualification are distinct. No tenant/site credentials, approved policy, live employee data, site or application deployment are currently asserted.

A 2024 PnP [Weekly Timesheet Template](https://pnp.github.io/powerplatform-samples/samples/weekly-timesheet-sharepoint/) is the **candidate** bootstrap; it is not a medical job-planning product nor an actively maintained upstream dependency. Evaluate whether a fresh Microsoft Lists-generated canvas app is safer/less costly before reuse (decision gate B03). Preserve licence and provenance evidence and record asset-level reuse. Do not introduce premium Dataverse or Copilot dependencies in the baseline.

## Documents

- [Requirements and MoSCoW](requirements.md)
- [Architecture, data and integration design](design.md)
- [Contracts, evidence and acceptance gates](contracts.md)
- [Granular executable track plan](plan.md)
- [Existing medical-job-planning Mermaid diagrams](../../../docs/medical-job-planning/README.md) (pending PR #310, not merged at planning time)
- [Parent CareOps PPG entry](../../tracks.md)

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
