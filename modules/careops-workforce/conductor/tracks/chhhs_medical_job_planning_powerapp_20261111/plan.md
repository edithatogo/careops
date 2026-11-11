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

## P0A — confidential references and process reconciliation (design only)

- [ ] JP-00.6: Register the two supplied reference types and historical Drive comparators in the **approved restricted source store only**. Capture current/revision status and permitted use. Do not commit originals, text extractions, scans, staff identifiers, personal rosters or Drive IDs.
- [x] JP-00.7: Produce non-identifiable reference-design-findings.md and source-boundary.md; refer to draft work instruction as proposed and historical comparators as non-authoritative.
- [ ] JP-00.8: Review original draft with HR/IR and document custodian: reconcile exact applicability, session convention, CST (including specialty provisions), consultation/notice, on-call, dispute and approval before rules become authoritative.
- [ ] JP-00.9: Implement CI preflight to reject private/reference paths and office/PDF artifacts; scan staged files, generated packages and PR diffs for protected identifiers/content. Baseline .gitignore is prevention only, not a sufficient enforcement mechanism.

## P3B — prospective workflow specialisations

- [ ] JP-03.14: Clinician self-assessment and evidence-of-consultation capture independent of approval.
- [ ] JP-03.15: Service demand/resources preconditions and ranges, with evidence of enabling resources and explicit exclusions.
- [ ] JP-03.16: Editable N-week repeating plan, four-hour optional display, dedicated annualised-activity budget, monthly replacement blocks and distinct on-call sections.
- [ ] JP-03.17: Record cancellation/substitution, CST make-up, persistent additional-hours and temporary vacancy exception flows.
- [ ] JP-03.18: Configurable early/quarterly/annual review schedule with separately effective-dated authority and no automatic adverse consequences.
- [ ] JP-03.19: Three scenario packs for renal/rural, neonatal on/off-service and part-time rotating practice, entirely **fictional** and not derived from staff-identifiable roster values.

## Additional release gate: restricted-source assurance

- [ ] JP-04.6: Verify Git full history and PR changed-files manifest contains no restricted originals, extracted tables, personnel details or reconstructable individual schedules. Verify binary/office/PDF blocking, secret scanner, PII checks and test-generated assets. Distinguish source confidentiality checks from business/clinical approval.

## P1A — review schedule and role-dashboard authority (new)

- [ ] JP-01.6: Reconcile authoritative CHHHS review frequency, triggers, notice/grace/deferral, policy versions and applicable employee classes; retain draft instructions as unapproved design input.
- [ ] JP-01.7: Specify version-pinned due date anchoring and reminders, planned versus emergency and no-change review handling, including policy edition migration and readback.
- [ ] JP-01.8: Verify practitioner-only, approver-only, dual-role/acting and administrator roles across clinical services, delegations and records history; test segregation of duties and direct SharePoint access.
- [ ] JP-01.9: Decide whether baseline custom SharePoint decision workflow satisfies CHHHS security/records/approval needs. Explicitly assess Dataverse infrastructure/licensing requirement of optional native Power Automate Approvals before adoption.

## P2A — persistent lifecycle and dashboard data (new)

- [ ] JP-02.6: Provision versioned ReviewPolicies/ReviewObligations and case/task/notification stores with unique idempotency keys, effective-date/policy provenance and indexes.
- [ ] JP-02.7: Separate mutable restricted drafts from submitted and immutable approved snapshots; add guarded active-version pointer and protected historical document exports.
- [ ] JP-02.8: Build role assignments/acting delegation, source-enforced view/export permissions, historical access checks and supplemental SharePoint audit/version configuration.
- [ ] JP-02.9: Define solution-aware flow and record API contracts F01–F18 in [catalogue](flow-list-artefact-catalogue.md), including clean deployment and environment-specific role mappings.

## P3C — schedule, revision and dashboard build (new)

- [ ] JP-03.20: Implement practitioner anytime draft/revision and explicit submit; autosave alone must not launch approval, older approved version stays live.
- [ ] JP-03.21: Implement daily policy-derived review obligations, reminder digests and no-change attestation, with policy version pinning, migration, idempotent recurring runs and deferrals.
- [ ] JP-03.22: Implement task/state routing with consultation, HR/IR, delegated decision and acting approvers; ensure no unauthorised/self approval and preserved returned-submission history.
- [ ] JP-03.23: Implement future-effective approval and activation, old-version history/timeline, side-by-side category/whole-job diff, authorised historical exports and copy-from-version.
- [ ] JP-03.24: Deliver practitioner, approver and operator dashboards; enforce one-role and dual-role access in data layer as well as UI.
- [ ] JP-03.25: Implement operational controls: duplicate/failed-flow recovery, stale delegation, orphan tasks, escalation, audit/notification ledger and source-health monitoring.

## P4A — acceptance extensions (new)

- [ ] JP-04.7: Synthetic acceptance grid covers mid-cycle spontaneous revisions, scheduled review coincidence, change requests, no-change attestation, delayed effective activation, role combinations and history permissions.
- [ ] JP-04.8: Validate actual nonpremium solution connector and approval infrastructure/licensing inventory; no assumption that hosted Approvals actions are Dataverse-free.
- [ ] JP-04.9: Fault-inject daily sweep/replayed submission, edited SharePoint status, stale ETags, policy changes, reminder bursts, historical export link sharing and revoked delegation.
- [ ] JP-04.10: Verify authorisation, provenance, retention/hold, accessible dashboard UX, versioned outputs and fail-safe rollback before any pilot or production claim.

## Source-only review/versioning proof — 11 November 2026

- [x] JP-VC00: build dependency-free reference engine in a separate **local generated source package** and run 10 synthetic tests (all pass); preserve delayed policy sweep regression and record qualification limits. **Not committed to GitHub.** [Evidence/limitations](review-versioning-qualification-20261111.md).
- [ ] JP-VC01: integrate tested code and synthetic tests as inspected source into workforce app package and qualify on exact CI head.
- [ ] JP-VC02: server-side role/delegation and industrial-source validation on all transition paths.
- [ ] JP-VC03: durable SharePoint adapter with transactions, ETags, idempotent replay across restarts and atomic activation.
- [ ] JP-VC04: overlapping version/effective date and rule migration temporal tests.
- [ ] JP-VC05: read access, version-history retention, off-service scopes, export ACL, scale and adverse permission tests.
- [ ] JP-VC06: deployable solution-aware flows and clean dev import/readback qualification.

Local reference qualification **does not** complete G2–G5 or a working production job-planning app.

## SharePoint transactional adapter — current source delivery

- [~] JP-VC01: SharePoint REST source and synthetic tests committed under `modules/careops-workforce-app/sharepoint/`, with 19 locally passing tests; **GitHub Actions unable to start runner, no passing CI evidence**. [Qualification receipt](sharepoint-implementation-evidence.md).
- [~] JP-VC03: implemented a four-list, single-head-CAS, recoverable-operation protocol, exact REST ETags, unique-index requests, durable SQLite simulator and synthetic crash/replay tests. **Native SharePoint list, connection and concurrency qualification still open.**
- [ ] JP-VC07: provision approved restricted SharePoint lists and confirm exact REST uniqueness/412/429 behavior and operational payload limits.
- [ ] JP-VC08: implement solution-aware standard SharePoint cloud flows with tenant-authenticated identity/delegation, multi-stage consultation/HRIR/employer decision, retry/recovery, privacy-safe alerts, and manual failure resolution.
- [ ] JP-VC09: clean import/readback and tenant-backed end-to-end actor, ACL, retention, interrupted worker and burst concurrency tests. No premium/Copilot baseline.

GitHub Actions jobs for this PR failed before receiving a runner (zero executable steps); do not mark CI or native qualification complete or bypass branch protection. Keep source-level and tenant-level evidence independent.

## Follow-on implementation increment — 11 November 2026

- [~] JP-VC02: added source-only multi-stage transition contract `modules/careops-workforce-app/sharepoint/flow_state.py` with consultation, clinical review, medical workforce/industrial review and delegated final approval, separate terminal return/reject paths and six synthetic tests. **No authenticated server identity or real delegation resolver yet.**
- [~] JP-VC07: added `provision-lists.ps1` for four development SharePoint lists, unique indexed keys, plain JSON payload columns and list versioning. Script is **not run in a tenant**; ACLs, DLP, retention, records library and capacity remain open. Use WhatIf first.
- [ ] JP-VC10: implement Power Automate solution-aware flows for operation receipt, staging, ETag CAS, recovery, decision routing and future-effective activation. The Python source is not natively executable inside cloud flows.
- [ ] JP-VC11: build permission-bound app dashboards, authorised history exports and secure officer/approver role union.
- [ ] JP-VC12: exact-head GitHub CI and live SharePoint REST/provisioner readback; current Actions jobs fail before runner allocation and cannot be counted as passing tests.
- [ ] JP-VC13: add SharePoint list-level and item-level ACLs with explicit scale testing, records retention, approved delegated decision evidence and privacy review before real records.

**Status:** incremental source implementation only. No CHHHS tenant changes, no production solution ZIP and no native import qualification.

## Agent skill installation and toolchain enablement — 11 November 2026

- [x] JP-AG01: verify Microsoft `power-platform-skills`, `power-cat-skills`, `Dataverse-skills` and Wals-pro `claude-power-automate` sources/licences; pin observed upstream SHA audit points in [installation manifest](../../../../../docs/development/power-platform-agent-skills.md).
- [x] JP-AG02: declare four official plugins (`canvas-apps`, `powercat-canvas-apps`, `power-automate`, `dataverse`) through `.github/copilot/settings.json` and `.claude/settings.json`. Actual host installation and authoring MCP connectivity are not asserted.
- [x] JP-AG03: install repository-local `.agents/skills/careops-power-platform/SKILL.md` router and vendor eight pinned third-party Power Automate `SKILL.md` plus reference Markdown files, retaining MIT licence notice. Do not install the optional CLI or execute code.
- [x] JP-AG04: add executable, opt-in host bootstrap with `--check`, `--copilot`, `--claude`, `--checkout-sources`; no scripts automatically execute in CI.
- [ ] JP-AG05: run plugin list, .NET 10/PAC/Studio MCP/tool verification on authorised development machine; capture actual effective installed plugin versions and prerequisite evidence.
- [ ] JP-AG06: identify and vet the precise SkillEra IO `PowerPlatform-Skill` source, licence and attack surface. No matching verified canonical source was located.
- [ ] JP-AG07: install any equivalent Microsoft authoring/Dataverse plugin in the user's ChatGPT account through the platform's plugin directory once discoverable; no plugin suggestion currently resolves. Copilot/Claude settings are not ChatGPT account installations.
- [ ] JP-AG08: reuse installed vendor skills to continue app development, author native Power Platform flows/screens in Studio, and qualify actual tenant import, connectors and normal nonpremium licensing.
