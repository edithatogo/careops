# CareOps Catalogue — organisation-neutral SharePoint-native specification

**Status:** proposed source-only specification. **Track ID:** `ckan_catalogue_20261106` retained for historical identity. **Date:** 2026-11-06.  
**Deployment:** independently configured against an approved Microsoft 365 site; organisation names and jurisdictional policy remain exclusively in deployment profiles, not this track or reusable core.

## Goal

Deliver a **working, low-code data and resource catalogue first**. SharePoint Lists are the structured metadata database; Document Libraries store file resources and their physical version history. Native Microsoft Lists forms, SharePoint site columns/content types, modern views/pages and permission enforcement are the primary UX. The catalogue may use ideas from CKAN's Organization→Dataset→Resource model, but **does not depend on or implement CKAN software**.

This catalogue is an optional **index and discovery service**, not a new system of record for existing CareOps modules, an approval system, a replacement research-governance system, or a clinical data lake.

## Core functional requirements

- Initial logical entities: `Dataset`, `Resource`, `Asset`, optional `Organisation` and controlled `Vocabulary`. The first physical objects are `Catalogue_Datasets`, `Catalogue_Resources` and `Catalogue_Assets`. Use an existing authoritative organisational source rather than create a duplicate unless necessary.
- Stable, globally unique domain identifiers independent of SharePoint item IDs or file paths; version/schema/source-qualified IDs, owner, classification, provenance, retention/review, archive/withdrawal states.
- Shared site/library columns, content types, indexed default views and native list forms with a modern landing page. Physical file access and metadata visibility must be independently enforced and tested.
- Idempotent, version-aware provisioning with dry run, exact internal field name readback, repeatable changes, safe rollback, no destructive drift repair and developer-friendly fictional fixtures.
- Minimal CSV/JSON export and recovery/readback for a later provider migration. Do not build Dataverse/SQL adapters until there is a justified, funded migration.
- Information governance evidence, human approvals and release records remain in the source authority. The catalogue stores **links plus verified observation states** only, never a conflicting authoritative decision.
- Logical Bronze/Silver/Gold/Platinum states: received source, validated/normalised artefact, governed curated product, authorised publication. No unsupported heavy compute or raw patient-level lakehouse on SharePoint.
- Support source-qualified references to CareOps Approve, Decisions, PPG, RIMS, Clinical Hub, Process, Incidents, Costing, Finance, Sim and Legacy Migration. They are **optional independent producers**, not runtime/database dependencies.

## Delivery sequence and acceptance

1. **M0 readiness:** Reconcile repository, existing modules/Conductor and accepted permissions. All actual cloud writes require an authorised test site. Unavailable permissions are explicit blockers to cloud tasks, not to fictional local development.
2. **M1 core:** Two Lists, one Library, columns/content types, indexed views, site page and native forms; create/find/edit/open/withdraw fictitious datasets/resources, restore history, deny unauthorised reads and export metadata. This must be usable **without** SPFx or native CKAN.
3. **M2 governed quality:** controlled tags, quality, provenance, logical medallion statuses, human publication evidence, bounded standard flows and reconciliation where proven useful.
4. **M3 integrations:** link into existing module owners using versioned reference contracts and tested failure/absence/privacy behaviour. No duplicated records.
5. **M4 additional value:** search refiners and cross-site discovery (vetted PnP Modern Search where admitted); controlled optional Teams/Planner/document patterns and future capability experiments behind separate approval gates.

## In scope versus excluded

**In scope:** Microsoft 365 standard SharePoint Lists/Libraries, native Forms/Pages, content types, site columns, indexed views, versioning, standard SharePoint Power Automate where warranted, source-controlled configuration, optional vetted upstream PnP Modern Search, CareOps reference mapping, future-neutral metadata contracts.

**Explicitly excluded:** custom SPFx React application; CKAN server, PostgreSQL/Solr/Redis, file-keeper Python adapter, CKAN Action API facade; mandatory central runtime; premium/paid services, Copilot and AI Builder; patient-level clinical extracts in source control or an unauthorised SharePoint site; duplicate CareOps/clinical governance authorities; automatic clinical publication or resource access approval.

## Quality and release gates

- Schema contract tests, exact field identity/index/permission readback, negative access tests and explicit SharePoint search indexing limitations.
- Version conflicts, retries, duplicate event delivery and Power Automate recursion handled via only necessary minimal components.
- Accessible and usable reader and custodian workflows, controlled published-state rollback, recoverable data/metadata exports.
- Fail closed on missing/expired permission and governance evidence. No hidden source data in public Git or unapproved tenant connection.
- Current-head source/privacy/security/CI checks, reviewed third-party versions and reversible deployment.
- Separate source, tenant acceptance, information governance and production authorisation; no equivalence inferred.

See [ordered Conductor milestones](plan.md), [architecture and module integration map](../../../docs/clinical-data-catalogue/architecture.md) and [feature radar](../../../docs/clinical-data-catalogue/platform-dependency-radar.md).
