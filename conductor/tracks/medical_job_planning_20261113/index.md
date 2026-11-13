# CareOps Medical Job Planning: source admission, native delivery and interoperability

**Status (13 November 2026): PLANNING MERGED; source-only first domain slice proposed in a separate review PR.** No source has been admitted into CareOps, no tenant modified, no native app/flow imported, no policy adopted and no operational or privacy acceptance claimed.

**Decision:** create a standalone Medical Job Planning module at the *proposed* path modules/careops-medical-job-planning/, distinct from the integrated modules/careops-workforce/ Power BI workforce reporting source. Preserve all sibling-module authority and standard-connector-first deployment.

[First bounded source implementation and remaining gates](source-implementation-20261113.md) records the partial standalone domain slice. [The W1 negotiation/versioning follow-on](negotiation-versioning-20261113.md) documents the immutable as-of and dispute contract. It does not close W0/G0 or authorise native deployment.

## Inspected baseline

- User-supplied offline source: careops-workforce-app_v0.4.2.zip, SHA-256 **922c29f0364c7e1a0d61e4d0ba0a87f5cb28416c1f143758577404ff615626a7**, 74 archive entries, dated 12 November 2026. Archive is **NOT** a Power Platform solution ZIP.
- Domain: domain.py and planning_semantics.py; local lifecycle: workflow_runtime.py; SharePoint CAS reference: sharepoint/sharepoint_adapter.py and flow_state.py; canonical proposed list inventory: config/data-model.json (20 lists + one library).
- UI: nine illustrative canvas/Src/*.pa.yaml specs **not** Studio-authoritative source; ten flows/*.workflow.json **inert** WDL scaffolds; three read-only native monitor candidates, **not** tenant-qualified.
- Included machine-generated receipt reports 131 passing local tests (87 module, 44 SharePoint) under Python 3.12.16 with PyYAML 6.0.3 on 12 November; this is historical self-reported offline evidence, not current 3.15 qualification, native functionality or legal/industrial proof.
- Existing CareOps Workforce is a PBIP/TMDL/PBIR source-only analytics module with a private 66-feed deployment contract and independent native promotion. Do not edit, replace or bind its model as part of source admission.
- Repository baseline reviewed against CareOps main on 13 November 2026; refresh actual refs, open PRs and module owners before implementation. This planning PR does not freeze the source selection.

## Goal and non-goals

**Goal:** allow an authorised medical practitioner and accountable reviewers to create, revise, review, approve, activate, retrieve and periodically attest an effective-dated job plan with traceable industrial policy, delegated authority, correct access control, idempotent processing and durable records. The first operational deployment profile may be CHHHS; reusable core remains jurisdiction/organisation-neutral.

**Non-goals for the minimum viable service:** a new HR system, payroll, rostering authority, establishment ledger, mandated parent CareOps installation, AI decision-maker, migration to Dataverse, unconditional Power BI/Fabric deployment, automatic email sending, clinical workforce performance rating, or derived employment compliance without adopted policy.

## Mandatory decision records and cross-track ownership

- Medical Job Planning owns plan/draft/version/session/CST-event/review case and native lifecycle, subject to separately authorised delegation and service governance.
- Existing HR/payroll/rostering and position-establishment systems remain authoritative for personnel, appointments, assignments, contracts, industrial instruments, roster and delivered activity. Use source-qualified versioned *references*, not an invented replacement master-data system.
- CareOps PPG owns published policy and rule-document lifecycle; Medical Job Planning owns the versioned approved *execution snapshot* with exact source and date.
- CareOps Approve/Decisions are optional consumers/providers for formal approval records; the module must work independently with its accountable local approved human route; no duplicate cross-module decision authority.
- Process, Workforce BI, Costing/Finance and Sim are optional read-only event, aggregate or synthetic scenario consumers. Respect their independent releases and licence/tenant profiles.
- Data owner, industrial interpretation owner, records officer, privacy officer, Power Platform solution owner, medical workforce business owner and delegated approval authority are **roles to confirm**, not assignments or approvals made by this track.

## Linked artifacts and progression

1. [W-1 pre-implementation decision gate: industrial applicability, storage ADR, trust boundary and first vertical slice](pre-implementation-decisions.md).
2. [Requirements: MoSCoW and negative acceptance](requirements.md).
3. [Architecture: canonical model, security, negotiation state machine and adapters](design.md).
4. [Normative integration contract and interface ownership](integration-contract.md), including [versioned JSON Schema](contracts/envelope.schema.json) and [synthetic positive fixtures](contracts/fixtures/valid-messages.json) plus [negative conformance cases](contracts/fixtures/negative-cases.json).
5. [Executable work packages, dependencies and evidence gates](plan.md), now including 10 W-1 decision tasks and 62 W0–W6 implementation tasks.

**Route:** W-1 source-level decisions and pre-implementation contracts -> W0 source and owner reconciliation -> W1 semantics and secure store -> W2 native minimum journey -> W3 complete lifecycle/records -> W4 optional CareOps interfaces -> W5 qualification, pilot and adoption. The new first vertical slice uses a fictional SMO with CST entitlement, negotiated counterproposal, human delegation and issued immutable history. Strict schemas and semantic tests do not fix the still-unadmitted v0.4.2 parser. Work that does not require tenant access is independently deliverable, but a local green check never closes native or operational tasks.

**Change boundary:** planning does not authorise access to CHHHS tenant/staff records, provision lists, enable flows, change employment policy, send notifications/emails or publish a solution. Keep source and fictional fixtures public-safe; identities, delegated role lists, records, enterprise bindings and native receipts stay in approved private stores.
