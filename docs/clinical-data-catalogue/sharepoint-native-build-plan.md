# CareOps Catalogue — native SharePoint core build and coding-agent handoff

**Status:** source-only implementation design, 2026-11-06. No tenant, site, application, connector or clinical dataset has been deployed by this plan.  
**Current authority:** [organisation-neutral Conductor milestones](../../conductor/tracks/ckan_catalogue_20261106/plan.md), [architecture and module map](architecture.md), [proposed minimal SharePoint schema](../../portfolio/careops-catalogue-sharepoint.v1.json), [Microsoft feature radar](platform-dependency-radar.md).

## Deliberate simplification

The first usable product is **two SharePoint Lists plus one SharePoint Document Library**. It is inspired by the good parts of CKAN's catalogue concepts but **does not install CKAN, Python FileKeeper, PostgreSQL, Solr, Redis or a CKAN web UI/API**. There is **no bespoke SPFx React application**. Teams, Search, Power Automate, CareOps references and logical medallion capabilities are value layers **after** core acceptance.

The previously proposed 13 Lists/five Libraries and FileKeeper integration are superseded. Namespaced physical objects are now `Catalogue_*` (proposed only; no destructive rename/migration on an existing site), and reusable library columns are `CAT_*`. The [older CKAN database/FileStore ADR](adr-ckan-core-and-backends.md) remains solely a historical alternative analysis.

## Exact initial vertical slice

| SharePoint object | Function | Essential fields and behaviours |
| --- | --- | --- |
| `Catalogue_Datasets` List | Dataset identity, ownership and discovery | `DatasetID` UUID-string, Title, Description, OwnerRole, ClinicalDomainCode, SourceQualifiedID, MetadataRevision, AccessClass, LifecycleStatus, LastVerifiedUTC |
| `Catalogue_Resources` List | Child resource metadata independently of file storage | `ResourceID` UUID-string, `DatasetID`, Title, ResourceType, `AssetID` or external URL, AccessClass, SourceRevision, ReviewStatus |
| `Catalogue_Assets` Library | Actual files, supporting documentation and governed published copies | `CAT_DatasetID`, `CAT_ResourceID`, `CAT_AssetID`, kind, source, data stage, classification, validation status, approved release reference, version history, content types and native preview |

Reuse an organisation taxonomy/list where already authorised. Only create an Organisations List if that is missing **and** its ownership is explicitly agreed. Do not store a second authoritative record for owners, decisions, policy masters, provenance/retention rules or other CareOps workflows.

**First-stage library content types:** resource file, data dictionary, protocol, report, release receipt. Use existing suitable site columns/content types rather than blindly creating duplicates. `CAT_DataStage` may hold `bronze|silver|gold|platinum`, but does not imply separate security, compute or library tiers.

**Required native views/pages/forms:** Active Datasets, By Clinical Domain, Needs Review, Resources by Dataset, Resource Type, and Assets by release status; one modern site landing page with List/Library/Quick Links web parts; native Microsoft Lists registration/edit forms and appropriate required fields. Use JSON view/column formatting only for display and links. Do not treat a hidden control or formatted status as access control.

### Permission boundary

- List items and file bytes are two separate permission checks. A public-facing catalogue entry may point to a restricted asset without granting access; do not leak patient details or protected resource names in metadata.
- Prefer distinct approved sites/libraries for different sensitivity/retention/access boundaries. Do not create thousands of item-level unique permission breaks or claim that `CAT_DataStage` is a security class.
- SharePoint content approval is not clinical policy authorisation, research ethics approval or delegated decision. Link to the authoritative source and verify current status where the relevant owner permits.
- Rely on native versioning for operational edit recovery **only within approved retention settings**; preserve governed publication receipts/records according to the actual organisation's records policy.

## Coding-agent runbook — ordered first milestone

### M0: reconcile sources and qualify only the minimum tools

1. Start from a clean CareOps checkout and inspect current `main`, the open architecture PR and the existing Conductor track. Read `portfolio/repos.json`, `portfolio/module-catalog.md`, `portfolio/delivery-catalog.json`, `portfolio/power-platform-alm.json`, `conductor/suite-delivery.md`, `docs/development-and-delivery.md` and the target deployment profile (if provided). Do not merge or overwrite siblings' roadmaps.
2. Existing pinned Conductor is at `.agents/plugins/conductor`. Verify gitlink and host-specific Agent Skills activation; do not install a second upstream, patch Conductor or run initial setup over existing track history.
3. Tool inventory: Git/optional `gh`, coding-agent CLI, Node/npm only if required for local validation, optional `jq`, and **CLI for Microsoft 365** or **PnP.PowerShell** only when an approved existing Entra application/client consent is available. No SPFx generator, React/Heft, CKAN, SQL runtime, Power Apps Code Apps or paid developer tool is needed for M1.
4. Determine whether a designated **non-production SharePoint site** and suitable maker/site owner exist. Obtain authorisation before even read-only site assessment, record information classification and records/privacy/security obligations.
5. Run CLI read-only capability checks (if permitted) before any write. Site owner permission does **not** imply the CLI's delegated SharePoint scopes are consented. Site collection app catalogue rights are irrelevant to M1; they matter only for a later optional vetted PnP Modern Search package.
6. Generate fictional manifest/fixture verification and a **dry-run** provisioner. If tenant connection is blocked, continue local source tests but report cloud gate as blocked, not completed.

### Suggested local preflight

```sh
git status --short
git submodule status -- .agents/plugins/conductor
git ls-tree HEAD .agents/plugins/conductor
git --version
node --version
npm --version
gemini --version
m365 version
```

These commands describe a local discovery procedure; a missing optional tool is not itself failure of the core architecture. For an approved CLI app and tenant connection, confirm command syntax with the locally installed `m365 ... --help` and perform an authorised, **read-only** `m365 spo web get`, `m365 spo list list`, `m365 spo field list` using private site values. Do not place tenant IDs, site URLs, credentials, tokens, real list exports or staff identities in public Git.

### M1: implement and test the core before any layering

1. Build site/library/list schema files from `portfolio/careops-catalogue-sharepoint.v1.json` and a readback validator. Provision to an **explicitly authorised test site**, idempotently and non-destructively; require a no-op rerun, field internal-name/column type/index/read permissions checks, and rollback script. Admin-only operations remain blocked; do not bypass.
2. Use **native SharePoint** for all user journeys. Create a dataset, add a resource link, upload a file and set metadata, edit/withdraw a record, browse/filter/preview, deny an unauthorised asset read and restore a previous version.
3. Keep a simple, deterministic source-controlled CSV/JSON export mapping with UUID, schema version and source-qualified IDs to protect portability. Do not implement a general-purpose backend/service layer, speculative Dataverse/MS SQL provider, CKAN facade or analytical engine.
4. Verify **five ordinary tasks** with fictional records: register, discover, attach, restrict, withdraw. Keep actual native screenshots/readback under approved restricted storage and commit only non-sensitive acceptance receipts.
5. Release the core only after owner acceptance, negative access tests, recovery and non-production/production admission gates. A green source-only CI does not establish operational fitness.

**M1 exit:** a usable, low-code catalogue that needs no custom app code to serve its baseline purpose.

### M2/M3: deliberate and measurable enhancements

- M2: mandatory metadata, controlled taxonomy, owner review, logical Bronze/Silver/Gold/Platinum, lineage and safe publication/withdrawal evidence; introduce standard Power Automate only if a documented manual task requires it.
- M3: source-qualified **read-only links** to CareOps PPG, Approve, Decisions, RIMS, Clinical Hub, Process, Incidents, Costing, Finance, Sim and Legacy Migration. Enrich only with approved aggregate data-product metadata; no shared database or duplicate authoritative workflow.
- M4: if native discovery is inadequate, evaluate upstream PnP Modern Search **as distributed** with app-catalogue/security/search-schema prerequisites; use managed metadata, Document Sets, Teams tabs, cross-site highlighted content or standard report links only where useful. No bespoke SPFx frontend or CKAN runtime should be reopened by default.
- Long horizon: advanced Microsoft features, preview developer features, Copilot and paid/premium capabilities remain **research-only**, separately consented and not source dependencies. See the [radar](platform-dependency-radar.md).

## Tools and permission matrix

| Operation | Minimum condition | Core dependency |
| --- | --- | --- |
| Source changes/agent | Git checkout, repository write permissions, exact existing Conductor pin | Yes |
| Create Lists/Libraries/columns/views | Approved non-production site with appropriate **site** Manage Lists/Design/Full Control rights; approved identity with any required CLI delegated scopes | Yes for live M1 |
| Native SharePoint Forms/Site Pages | Member/editor/owner privileges and supported tenant feature | Yes for native UX |
| Read/test file permissions | Authorised test identities and privacy/security acceptance; do not manipulate real access as a shortcut | Yes |
| Standard Power Automate | Permitted environment, supported SharePoint connector, DLP and service-owned connections | Only if M2 workflow admitted |
| Managed metadata | Existing term set/permission to use/manange terms; optional fallback Choice/reference values | Optional |
| PnP Modern Search | Approved app catalogue, search managed properties, additional scopes if used, upstream vetted package | M4 only |
| PnP.PowerShell / CLI for M365 | Existing registered Entra client app, delegated scopes/consent, site privileges; these are **not** admin bypasses | Provisioning convenience, not sole path |
| SPFx/React/Python CKAN/file-keeper/SQL host | Not required or planned | No |
| Premium/Copilot/Power BI PPU/Fabric/Power Apps Code Apps | Separately licensed/approved, out of scope | No |

## Development effort — scope estimates, not timeline commitments

| Scope | Rough engineering effort | Caveat |
| --- | --- | --- |
| Source/permissions discovery and fictional minimal schema/fixtures | 2–4 person-days | Native site permissions may block independent of code |
| Functional, native two-List/one-Library demonstration | 3–7 person-days | After access/rights are available |
| Controlled internal pilot with validation, security, native usability, recovery and ownership | 10–25 person-days | Complex information governance may take longer; excludes wait for authorisations |
| M2 data quality/governance and medallion | Additional scoped increment | Measure user benefit before implementing |
| M3 optional sibling-module integration | Separate bounded contracts | Module-owner approval and real source permissions |
| M4 advanced search | Optional | Use vetted upstream package rather than a new React app |

## Coding-agent next assignment

> Work in the current CareOps checkout on the existing catalogue Conductor track. **Implement M0 and a fictional M1 vertical-slice setup first.** Reconcile current source/roadmaps and owner boundaries. Use the existing pinned Conductor; validate the proposed 2 Lists/1 Library schema and create an idempotent, dry-run-by-default provisioner and tests using fictional data. Do not connect to a real tenant or make site writes without explicit approved test-site access. Do not create SPFx/React or CKAN software, reimplement sibling approvals, install premium/Copilot dependencies, or create/commit real clinical records. Commit a bounded PR with source-boundary/security checks and rollback evidence. If the tenant gate is blocked, report exactly which site right, Entra client scope/consent or information-governance approval is missing.

## References

- SharePoint information architecture: https://learn.microsoft.com/en-us/sharepoint/information-architecture-modern-experience
- Native forms: https://learn.microsoft.com/en-us/sharepoint/dev/declarative-customization/list-form-configuration
- Modern Lists/Libraries: https://support.microsoft.com/en-us/sharepoint/data-and-lists/differences-between-modern-and-classic-experiences-for-lists-and-libraries
- Site provisioning and versioned information architecture: https://learn.microsoft.com/en-us/sharepoint/dev/scenario-guidance/site-provisioning
- SharePoint column formatting: https://learn.microsoft.com/en-us/sharepoint/dev/declarative-customization/column-formatting
- SharePoint connector limitations: https://learn.microsoft.com/en-us/sharepoint/dev/business-apps/power-automate/sharepoint-connector-actions-triggers
