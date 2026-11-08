# CareOps Catalogue — CKAN-based design, organisation-neutral SharePoint implementation

**Status:** proposed source-only specification. **Track ID:** `ckan_catalogue_20261106` retains the explicit CKAN design lineage. **Date:** 2026-11-06; reference basis clarified 2026-11-08.  
**Deployment:** independently configured against an approved Microsoft 365 site; organisation names and jurisdictional policy remain exclusively in deployment profiles, not this track or reusable core.

## Goal

Deliver a **working, low-code data and resource catalogue based on CKAN's catalogue model and core user journeys**. CKAN is the explicit reference model and functional blueprint, not optional historical inspiration. SharePoint Lists are the structured metadata database; Document Libraries store file resources and their physical version history. Native Microsoft Lists forms, SharePoint site columns/content types, modern views/pages and permission enforcement are the primary UX. This is a **CKAN-inspired SharePoint implementation**, not a CKAN installation, fork or claim of API/feature parity.

This catalogue is an optional **index and discovery service**, not a new system of record for existing CareOps modules, an approval system, a replacement research-governance system, or a clinical data lake.

## CKAN foundation and interpretation

Use the [CKAN reference-to-implementation mapping](../../../docs/clinical-data-catalogue/architecture.md#ckan-reference-model-and-functional-baseline) when implementing this track. Preserve dataset/package and resource as different concepts: an owning organisation/publisher has datasets; a dataset holds descriptive metadata and related resources; a resource can reference a file asset or external location. Groups/tags are cross-cutting discovery concepts, not implicit security groups. The user journey is to find a dataset, inspect its metadata and then select a permitted resource, not merely browse a document folder.

For each material design difference, record whether it is a **SharePoint adaptation**, **CareOps addition** or **deliberate omission**, with the relevant milestone. The existing two-List/one-Library M1 and CAT-01–08 acceptance gates remain unchanged; later facets, group/tag expansion and integrations are not new M1 dependencies. Medallion stages and PPG/Approve/Decisions integrations are CareOps additions. CKAN DataStore, Action API, extension compatibility, runtime and a pixel-identical UI remain excluded. This clarification does not authorise importing upstream CKAN code or changing licences.

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

## M1 commissioning contract — final refinement

The [physical manifest](../../../portfolio/careops-catalogue-sharepoint.v1.json) is a **design inventory**, not executable provisioning or a JSON Schema. Its commissioningRules are requirements to implement and verify, not controls already present in SharePoint. Keep this distinction in agent reports.

**Native-first does not mean validation-free.** Select the smallest supported mechanism for UUID assignment and relationship checking before accepting registration: a documented steward-assisted create path or, when authorised, a narrowly scoped standard-connector flow. A unique Text column does not generate UUIDs; form JSON does not secure fields. Do not add a bespoke application, arbitrary premium connector or a new approval engine to solve these tasks. The default M1 authoring role is a trusted custodian; wider self-service intake needs its own negative-permission tests and may remain restricted pending review.

| Test ID | Required M1 evidence | Refusal or recovery behaviour |
| --- | --- | --- |
| CAT-01 | Assign DatasetID, ResourceID and AssetID once; reject duplicates; preserve them through rename, move, restore and export/import | Missing/invalid identifiers do not become active or verified; no filename-derived IDs |
| CAT-02 | Resource links to a real parent dataset and exactly one file AssetID or external URI; asset parent metadata agrees | Orphans, conflicting locators and missing/mismatched files remain unverified |
| CAT-03 | New records use draft/not-assessed/unreviewed defaults; no default platinum stage or release reference | Classification labels never grant access or create a public sharing link |
| CAT-04 | Test reader, custodian and unauthorised roles against native forms, direct URLs, bulk edit and permitted APIs | Display-only hiding cannot protect IDs, classification or approval fields; no self-approval or privilege widening |
| CAT-05 | Repeat provisioning as a no-op, reject stale helper writes, and interrupt creation between file and metadata steps | Recover partial work without duplicates, overwriting concurrent edits or deleting user-created data |
| CAT-06 | Withdraw a resource and restore a file/version while retaining source and permission evidence | No cascading destruction, automatic re-publication or automatic revocation of unrelated source access |
| CAT-07 | Export/re-import a bounded snapshot with source IDs, resource locators and version mapping; exercise indexed views against expected fixtures | Reconcile counts and identities; omit credentials and signed/bearer links; published views require independently checked release evidence |
| CAT-08 | Run core journeys with optional modules/search/advanced flows absent; record blocked native tests explicitly | A source-only pass cannot substitute for tenant acceptance; M2-M4 stay gated on accepted M1 |

Each receipt records source commit, manifest version, test ID, execution mode (source-only or native), result (pass/fail/blocked/not-run), evidence reference and reviewer. Sensitive site identities and permission readbacks remain private. Do not mark a native test passed from a fictional fixture.

Email-capable rules/flows remain **Off** until the explicit recipient/content/send-scope approval required by repository policy. Use draft or non-delivering fixtures for tests; implementation or merge approval is not permission to send messages.

Microsoft references: [form configuration is presentation](https://learn.microsoft.com/en-us/sharepoint/dev/declarative-customization/list-form-configuration); [REST version-conflict handling](https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/working-with-lists-and-list-items-with-rest). These do not establish tenant permissions or implemented enforcement.

## Quality and release gates

- Schema contract tests, exact field identity/index/permission readback, negative access tests and explicit SharePoint search indexing limitations.
- Version conflicts, retries, duplicate event delivery and Power Automate recursion handled via only necessary minimal components.
- Accessible and usable reader and custodian workflows, controlled published-state rollback, recoverable data/metadata exports.
- Fail closed on missing/expired permission and governance evidence. No hidden source data in public Git or unapproved tenant connection.
- Current-head source/privacy/security/CI checks, reviewed third-party versions and reversible deployment.
- Separate source, tenant acceptance, information governance and production authorisation; no equivalence inferred.

See [ordered Conductor milestones](plan.md), [architecture and module integration map](../../../docs/clinical-data-catalogue/architecture.md) and [feature radar](../../../docs/clinical-data-catalogue/platform-dependency-radar.md).
