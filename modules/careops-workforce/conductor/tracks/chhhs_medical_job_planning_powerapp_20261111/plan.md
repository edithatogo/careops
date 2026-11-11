# Execution plan — CHHHS medical job planning Power App

**Work state: planning only**. Checkboxes denote tasks, not completion. A coding agent may implement development-source tasks after branch selection. Human organisation/industrial approval and tenant permissions remain explicit prerequisites. Integrate with existing CareOps-PPG and CareOps suite Conductor workflows; no added committee or approval layer.

## P0 — upstream audit and project admission (must before implementation)

- [ ] JP-00.1: Pin PnP sample repo commit and downloadable weekly-timesheet ZIP; record licence, hash, file provenance, third-party notices, maintainability and dependency inventory.
- [ ] JP-00.2: Perform isolated clean import using synthetic data; inspect controls, formulas, solution components, accessibility and non-premium connector use. Capture failures.
- [ ] JP-00.3: Build minimal fresh SharePoint-generated Canvas App alternative, compare against PnP with B03 weighted rubric; document reuse/replace decision and trade-offs. Gate **G0**.
- [ ] JP-00.4: Reconcile prior medical job plan drafts and diagrams (PR #310 status), relevant CHHHS Controlled Document rules and formal master-template availability; preserve unapproved status.
- [ ] JP-00.5: Confirm business owner, minimal scope, solution publisher strategy, source/module placement and explicit separation from live PPG product.

## P1 — organisational authority, risks and executable specification

- [ ] JP-01.1: Record current applicable award/MOCA7, officer-class/VMO/MPPP instruments, leave/ordinary hours, on-call/recall and CST interpretation with source edition; HR/IR sign-off required before real use.
- [ ] JP-01.2: Resolve CHHHS job-plan PPG adoption state, official Word masters, position/Clinical Director responsibility, delegations and approver authorities.
- [ ] JP-01.3: Conduct data/privacy/records/DLP threat model (individual workforce records), security-owner permission design, service-scope and retention/legal-hold requirements. Gate **G1**.
- [ ] JP-01.4: Convert [requirements](requirements.md) and [contracts](contracts.md) into test cases and acceptance traceability; sample clinician and rural service scenarios.
- [ ] JP-01.5: Decide SharePoint permission scaling pattern, fail closed if item/site model cannot satisfy segregation or operational scale.

## P2 — Power Platform foundation, infrastructure and contracts

- [ ] JP-02.1: Create solution and Canvas App with navigational shell (selected bootstrap), baseline standard-connector validation and responsive accessible components.
- [ ] JP-02.2: Implement versioned SharePoint List provisioning for officers, plans, revisions, sessions, on-call, actual activity, consultations, decisions, taxonomy, rule sets and review events; maintain an explicit schema manifest and indexes.
- [ ] JP-02.3: Configure connection references for flows, SharePoint data-source environment variables for canvas app (site/list GUIDs), service-owned identities and tenant-specific deployment settings.
- [ ] JP-02.4: Add least-privilege group/site/list permission boundaries, no 'visibility filter only' security; test list/API access for synthetic roles.
- [ ] JP-02.5: Define synthetic data fixtures and reproducible dev provisioning + teardown. Gate **G2**.

## P3 — core application and industrial validation

- [ ] JP-03.1: Officer plan editor: configurable cycle weeks, times, locations, primary codes, non-overlap, multi-session days and draft autosave.
- [ ] JP-03.2: Configurable taxonomy screen/seed with C1–C9, S1–S8, L1–L2, T/O and rules pinned to revisions.
- [ ] JP-03.3: Calculate ordinary/CST/contracted vs actual hours using a deterministic rule library and independent oracle; distinguish on-call availability, actual recall and travel; cover part-time/fortnight denominator.
- [ ] JP-03.4: Implement versioned plan snapshot, amendment comparison, immutability and concurrent write protection; no overwriting approvals.
- [ ] JP-03.5: Build Clinical Director review, workforce/HR validation, delegated final approval screens, fail-closed role enforcement and auditable decision events.
- [ ] JP-03.6: Implement solution-aware Power Automate submission, review, decision, notification and exception flows; replay/idempotence and retry evidence.
- [ ] JP-03.7: Produce approved-version document export referencing correct CHHHS template (or clearly labelled provisional export) with hours, taxonomy, decisions and source version.
- [ ] JP-03.8: Implement accessible desktop/tablet and feasible mobile experience, keyboard and screen reader tests; validate synthetic roles. Gate **G3**.

## P4 — assurance, packaging and reproducible import

- [ ] JP-04.1: Add CI: schema validation, Power Fx/unpacked solution lint, solution checker, forbidden-connector/secret checks, test fixtures, flow JSON validity and provenance/license checks.
- [ ] JP-04.2: Test all 15 synthetic fixtures plus property/boundary/concurrency/failure cases and planned-vs-actual reconciliation; record exact commits, build and test evidence.
- [ ] JP-04.3: Export unmanaged dev and managed release solution with version, hashes, dependency manifest, SharePoint provisioning package, config examples and separate install/rollback guide.
- [ ] JP-04.4: Clean-import solution into authorised test/dev tenant; bind connections/environment variables, publish, smoke-test all synthetic workflows, export, roll back and re-import; document all manual operator steps. Gate **G4**.
- [ ] JP-04.5: Independent security/records/privacy/HR-IR review and accessibility/UAT; release only if unresolved risks accepted by proper CHHHS authority. Gate **G5**.

## P5 — pilot, service design and future evolution (not a source-only acceptance condition)

- [ ] JP-05.1: Approve pilot cohort and service owner with explicit CHHHS authorisation. Train, issue support/runbook.
- [ ] JP-05.2: Measure completion burden, revision/error rate, delivered CST vs approved, overdue reviews, permission incidents and reconciliation variances; distinguish measurement from workforce performance appraisal.
- [ ] JP-05.3: Incorporate feedback, resolve defects, assess SharePoint scaling and connection owner continuity.
- [ ] JP-05.4: Transfer operational support and source stewardship with upgrade policy; record G6 before production request.
- [ ] JP-05.5: Decide whether generic job planning becomes separate reusable CareOps module, with CHHHS adapter and minimal interface to Approve/Decisions. Avoid a premium or AI dependency.

## Execution/archival policy

Each JP task must record `commit/ref`, test invocation/result, manual screenshots/readbacks where applicable, findings, owner, version, blocked dependencies and gate status. Mark complete only after evidence; if a native gate cannot run, retain `source-built/native-unverified`. Develop isolated branches/PRs, apply existing security/CI harnesses and reconcile Conductor after each PR. Do not merge PPG/source changes simply to satisfy an app task; preserve unrelated module boundaries. No automatic production publishing, emails to staff or live approvals.

## P3A — workforce capability additions (first release / early iteration)

- [ ] JP-03.9: Model positions, assignments, effective dates, acting appointments, split-service duties and funded establishment as **separate** qualified source records (M18–M19).
- [ ] JP-03.10: Add planned/rostered/delivered triad and exception evidence; missing external feeds stay unknown (M20).
- [ ] JP-03.11: Capture CST displacement, clinical override reason, recovery and longitudinal assurance; do not penalise clinicians for service-demand displacement (M21).
- [ ] JP-03.12: Add role/delegation conflict-of-interest and acting-role logic, service-level read-only what-if capacity comparison (M22, S10).
- [ ] JP-03.13: Validate clinician specialty presets, rural travel/coverage and leadership portfolios with bounded synthetic fixtures (S11–S14).

## P6 — broader workforce roadmap (unselected, later)

- [ ] JP-06.1: Add source-qualified roster, leave and workforce establishment adapters after separate interface/privacy authorisation.
- [ ] JP-06.2: Build aggregate, suppression-aware semantic measures for Workforce PBIP; preserve pre-existing PBIP source/lock and deployment contract.
- [ ] JP-06.3: Optional credentialing read-only effective-dated SoCP/expiry constraint adapter; do not alter the credentialing authoritative register.
- [ ] JP-06.4: Evaluate forecast/demand/capacity and CareOps-Sim scenario support, with model assumptions, uncertainty and validation.
- [ ] JP-06.5: Evaluate rural outreach scheduling, equity of allocations, career/education and service redesign modules under separately approved purposes.
- [ ] JP-06.6: Extract organisation-neutral job planning core and CHHHS-specific configuration, schema migration and integration contract only after pilot evidence.

### Implementation ownership reconciliation

This track is **owned by CareOps Workforce**; CareOps-PPG is a read-only source/template dependency only. Credentialing is an adjacent governed workforce workflow. Do not move or mutate the existing source-locked Workforce Power BI project during the planning-only track. A future operational adapter must state source authority and keep individual-job-plan records in their approved restricted store.
