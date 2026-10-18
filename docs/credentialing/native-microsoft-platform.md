# Native Microsoft credentialing platform

Status: target architecture, not tenant approval or deployment. 23 September 2026.
Programme: [native delivery roadmap](../../conductor/native-m365-roadmap.md)

## Decision and scope

Use full Microsoft Dataverse in a dedicated production Managed Environment for
CHHHS credentialing structured records, with separate development, test and
recovery environments. Use solution-aware Power Apps and Power Automate, Entra
identity, controlled SharePoint evidence libraries and optional Copilot Studio
assistance. Confirm Australian residency, licensing, capacity and service-owner
acceptance with the tenant authority before provisioning. Dataverse for Teams
and the default environment are not the mission-critical production baseline.
Microsoft documents differences in API access, plug-ins, auditing and granular
security between full Dataverse and Dataverse for Teams. [1]

SQLite in careops-decisions is a synthetic persistence/concurrency test adapter,
not a deployment option, production dependency or chosen data store. Preserve
useful tests but stop extending that adapter as a production implementation.
Translate safety invariants to Dataverse and test them in a sandbox; local SQL
transactions do not prove Dataverse concurrency, security or rollback behaviour.
The separate craft-led source-retrieval work is not the operational register.

## Native services and responsibility

| Service | Responsibility | Exclusion |
| --- | --- | --- |
| Dataverse | Cases, practitioner references, scopes, facilities, conditions, decision history, versioned authority, check jobs, inbox/outbox and reconciliation state | No authoritative writes based on an agent score or client-supplied approval Boolean |
| Model-driven Power Apps | Accessible register, case and delegation administration views; optional focused custom pages | Screens and hidden columns are not the security boundary |
| Power Automate | Small resumable workers, reminders and integration adapters | No single long-running approval flow as the case database |
| SharePoint | Controlled evidence, versioned instruments and final correspondence; stable document/version identifiers in Dataverse | No second editable register or bidirectional Lists mirror |
| Entra and Power Platform security | Authenticated users/application identities, scoped roles, conditional access, data policies and audit | No personal maker identity as the default production automation owner |
| Copilot Studio / approved AI Builder | Optional bounded extraction, comparison and draft preparation | No decision, delegate assignment, register activation or unreviewed adverse finding |
| Power BI | Optional privacy-minimised operational/benefits views | Dashboard absence must not stop credentialing |

Store critical transition enforcement server-side using a reviewed Dataverse
Custom API/plug-in boundary, permissions and tested transaction/concurrency
semantics. Prevent direct CRUD paths that bypass that boundary. Binding approval
to exact case/evidence/profile versions, verification of current authority,
atomic decision/history/outbox writes and stale-update rejection are requirements,
not capabilities established by merely creating tables. Microsoft documents
Custom APIs and conditional Web API operations. [2,3]

Persist case state and deadlines in Dataverse. Each worker has its own job,
lease, correlation/version, retry budget and exception owner. Complete only
validated prerequisites; preserve completed siblings. Ordinary cloud flow runs
have a documented 30-day duration limit, so cases must survive individual runs.
Exactly-once delivery is not assumed: use idempotent inbox/outbox processing,
checkpointing, reconciliation and no blind retry after an ambiguous send. [4]

## Backup, records retention and continuity are different

1. **Dataverse recovery:** configure and verify native system/manual backups;
   take pre-release restore points and practise restore in an isolated target.
   Microsoft currently documents seven-day default retention and up to 28 days
   for production Managed Environments. Configure it; do not assume 28 days. [5]
2. **SharePoint recovery:** enrol the controlled evidence sites in an approved
   Microsoft 365 Backup policy (or an approved equivalent) and test recovery of
   the actual sites, metadata, versions and permissions. This protects supported
   Microsoft 365 content, not a Dataverse environment. [6]
3. **Records retention:** apply the approved records schedule and legal holds
   separately. Operational backup windows are not long-term records retention.
   Dataverse audit configuration/activity logging and SharePoint retention both
   need explicit scope, retention and access decisions. [7]
4. **Downtime operation:** optional service-owned, read-only minimum-necessary
   register extract with source watermark, generation time, validity warning,
   conditions and revocations. A List or document snapshot is not a restorable
   Dataverse backup and cannot approve, extend or reactivate a scope. Personal
   OneDrive and synchronised personal folders are excluded as backup authorities.
5. **Whole-service outage:** define a clinical/business continuity procedure for
   tenant, identity, regional and connectivity outages. A SharePoint copy inside
   the same tenant is not an independent escape from all these failures. An
   approved offline view or other separately assessed recovery boundary may be
   needed. Do not promise availability without a tested failure scenario.

Dataverse backups cannot be downloaded as database backup files. Microsoft also
notes that only solution-contained apps/flows are covered and that restore can
take more than a day depending on size/audit data. Audit restore options and
same-region/target-type constraints must be tested, not assumed. Retain release
artifacts and recreate approved connection bindings separately. [5]

Dataverse and SharePoint are not one atomic backup. Preserve a reconciliation
manifest linking decision IDs, document/version IDs, hashes, policy releases,
restore-point watermarks and configuration versions. After restore, quarantine
outbound flows and agents, revalidate permissions, reconcile all histories and
revocations, then obtain an accountable release. Never replay old approvals or
send duplicate letters simply because a database was restored. Hashes detect
content differences; they do not establish identity or prevent malicious rollback.

Agree RPO (acceptable data loss), RTO (restoration time) and downtime-read targets
through a business impact assessment. Record targets separately from measured
test results and vendor statements. Capacity, recovery, cyber and clinical
acceptance are go-live gates. No numerical SLA or tenant capability is assumed.
SharePoint permissions need their own verification, including direct document
links; Dataverse screen access alone does not authorise document access. [8]

## Deployment independence

See ../standalone-module-contract.md. Each module has its own deployable managed
solution, owner, schema, permissions, configuration and independent release.
Integration adapters are optional packages. Installation isolation is not tenant
or regional fault isolation: shared environments also share restore blast radius.
Use separate environments where the approved recovery/security boundary requires
it. Shared libraries may be build-time dependencies, not a mandatory live CareOps
service. The parent repository is never a production runtime dependency.

## Evidence and remaining gates

This document changes design direction only. Existing source-contract MVPs stay
disabled. Before production: verify current local delegations and sources, build
native tables/API/flows/apps, enforce GitHub checks, run live-platform adversarial
and recovery tests, obtain operational acceptance, reconcile migration and retire
legacy tasks. Do not require every craft group to complete clinical model revision
before a compatible platform pathway can be assessed; preserve current approvals.

## Primary sources checked 23 September 2026

[1] Microsoft, Dataverse for Teams comparison: https://learn.microsoft.com/en-us/power-apps/teams/data-platform-compare
[2] Microsoft, Dataverse Custom APIs: https://learn.microsoft.com/en-us/power-apps/developer/data-platform/custom-api
[3] Microsoft, conditional Web API operations: https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/perform-conditional-operations-using-web-api
[4] Microsoft, cloud-flow limits: https://learn.microsoft.com/en-us/power-automate/limits-and-config
[5] Microsoft, environment backup/restore: https://learn.microsoft.com/en-us/power-platform/admin/backup-restore-environments
[6] Microsoft, Microsoft 365 Backup: https://learn.microsoft.com/en-us/microsoft-365/backup/backup-overview
[7] Microsoft, Dataverse auditing: https://learn.microsoft.com/en-us/power-platform/admin/manage-dataverse-auditing
[8] Microsoft, SharePoint document-management requirements: https://learn.microsoft.com/en-us/power-platform/admin/sharepoint-document-management-software-requirements
