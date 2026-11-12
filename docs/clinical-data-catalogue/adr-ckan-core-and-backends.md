# ADR: Unmodified CKAN, SharePoint-first persistence and portable CareOps catalogue

> **SUPERSEDED ARCHITECTURAL ALTERNATIVE — 6 November 2026.** This ADR is retained to explain why CKAN's native PostgreSQL/FileKeeper architecture was rejected for the current CareOps Catalogue. **No CKAN server, Python file-keeper, external extension or SPFx app remains in the active implementation roadmap.** The controlling decisions are the [SharePoint-native architecture](architecture.md), [ordered Conductor plan](../../conductor/tracks/ckan_catalogue_20261106/plan.md), and [minimal physical schema](../../portfolio/careops-catalogue-sharepoint.v1.json). Nothing in this historical document authorises a new runtime workstream.


**Date:** 2026-11-06  
**Status:** proposed architectural decision, awaiting implementation and validation.  
**Scope:** ordinary source module `modules/careops-catalogue` planned for integration in the CareOps parent **for reference**, with separate deployment, release and runtime boundaries. No native CKAN, SharePoint or SQL deployment is claimed.

## Non-negotiable distinction

The user requires (i) upstream **CKAN unmodified**, (ii) initial **SharePoint Lists, Columns and Libraries**, and (iii) subsequent option to use **Dataverse or Microsoft/Azure SQL** with minimal application change. A single abstraction cannot make stock CKAN use SharePoint instead of its primary SQLAlchemy/PostgreSQL catalogue database. CKAN 2.12.1 currently requires PostgreSQL, Solr and Redis for its native runtime. Its documented `IDatastoreBackend` extension applies to **structured resource DataStore**, not the core package/organization/group metadata ORM and authorization database. **CKAN 2.12 introduces file-keeper-backed configurable FileStore backends**, so a separate SharePoint Library FileStore adapter is plausible without modifying CKAN upstream, subject to adapter capability, authentication, file lifecycle, permissions and upgrade tests.

Therefore distinguish two separately deployable operating modes:

1. **MVP / SharePoint authoritative:** careops-catalogue runs an SPFx/SharePoint-native portal and metadata service against the canonical catalogue ports. SharePoint remains the sole authoritative metadata and document/asset store; CKAN upstream **code is unmodified**, but its native server and native UI are **not running**. A CKAN-semantic export/Action-API facade can be supplied, explicitly labelled compatibility-only and tested per route (never claim full CKAN server compatibility). Optional *read-only* upstream CKAN source checkout for reference/schema tests; no necessary runtime dependency.
2. **Optional future / real unmodified CKAN:** deploy official CKAN 2.12.x or later (as qualified) on approved server infrastructure with its **own PostgreSQL catalogue database, Redis and Solr**, without forking CKAN. Build a separate `ckanext-careops-sharepoint` adapter using only supported CKAN extension interfaces and action APIs, linking SharePoint documents as resources and ingesting controlled, approved metadata copies. Define a one-way projection (source-of-truth per field), an explicit synchronization/reconciliation protocol, and independent CKAN permissions. Never use both systems as concurrent authoritative writers of the same dataset. If CKAN becomes authoritative, that is an explicit system-of-record migration, not a config-only SharePoint provider swap.

**Native CKAN / SharePoint-only persistence / zero additional services cannot all be delivered simultaneously.** A genuine unmodified CKAN server is a later infrastructure/licensing/security decision. CKAN UI has no requirement to be cloned; if using the native CKAN UI, use it in the optional CKAN runtime, not by copying/patching its templates.

## Why not a live SQLite file in SharePoint?

A SQLite file can be uploaded into a SharePoint Library, but SharePoint/OneDrive file synchronization is **not** a SQLite-compatible transactional filesystem. SQLite relies on coordinated file locks, durable ordering and (for WAL) local shared-memory/WAL companion files. Multi-user edits via synced files can result in divergence, stale copies or corruption. There is no SharePoint REST API that translates CKAN SQLAlchemy database calls into SQLite file transactions. Do **not** host a live SQLite DB in a synced folder, remote document library or browser. A locally operated SQLite instance can be used for a fictional fixture or offline, single-owner read/analysis cache; publish a consistent closed/checkpointed, hashed immutable SQLite snapshot to SharePoint as an **artefact**, with no concurrent writers and never as the authoritative server catalogue. SQLite also does **not** satisfy upstream CKAN's PostgreSQL requirement.

## Concrete SharePoint implementation

Implement **Lists for metadata and Libraries for files**. The [physical schema, site/library column mapping, CKAN file-keeper integration stages, native capabilities and person-day estimate](sharepoint-native-build-plan.md) is part of this decision, with a [declarative schema inventory](../../portfolio/careops-catalogue-sharepoint.v1.json). Library columns track identifiers and file attributes; the authoritative dataset/resource descriptions remain in lists. Reuse SharePoint content types, version history, indexed queries and standard Power Automate rather than building a custom portal first. The only current custom FileKeeper path is an isolated future external Python CKAN extension, never part of SPFx.

## Contract architecture

```text
CareOps frontends/clients (SPFx first; optional CKAN-native runtime later)
    |
    v
Catalogue application / domain contract (CKAN-compatible IDs and semantics)
    |      +-- Dataset / Organization / Group / Tag / Resource DTOs
    |      +-- Canonical metadata revisions and provenance
    |      +-- Resource and asset links, governance references
    |      +-- Access decisions, publish/revoke/restore transitions
    v
Ports (no SharePoint types)
    CatalogueRepository         queries, list/get, mutation by expected revision
    AssetRepository             file/version/blob and checksum links
    SearchIndex                 filtered, security-trimmed pagination
    GovernanceEvidenceReader    read-only PPG/Approve/Decisions/ERM evidence
    EntitlementService          provision/revoke/reconcile (no implicit approval)
    PipelineStore               Bronze/Silver/Gold/Platinum lineage and releases
    MetadataExporter            CKAN Action envelopes, DCAT profiles and manifests
    TransactionJournal          idempotent command, outbox, retry/compensation
    |
    +-- SharePointAdapter  [MVP standard SharePoint REST + Libraries + Lists]
    +-- DataverseAdapter   [future licensed / administrative configuration]
    +-- SqlServerAdapter   [future approved API/service + SQL authentication]
    +-- CkanProjection     [future official CKAN Action API / extension]
```

No CKAN, SharePoint, Power BI or Dataverse SDK types appear in the shared canonical domain types. **Adapters are separate compilation and release units.** A `backend=sharepoint|dataverse|sqlserver` config selects a *qualified* implementation for the CareOps catalogue; it **does not select stock CKAN's core DB**. A future CKAN server uses its own unchanged PostgreSQL services regardless of this setting.

## SharePoint physical schema and migration-friendly columns

* Keep `CKAN_Organizations`, `CKAN_Datasets`, `CKAN_Resources`, `CKAN_Groups`, `CKAN_Tags`, relationship tables/lists, `CKAN_GovernanceLinks`, `CKAN_AccessEntitlements`, `CKAN_Lineage` and `CKAN_ReleaseManifests`. Keep files in separate versioned Libraries (Bronze, Silver, Gold, Platinum and DataAssets).
* The mandatory columns are **text UUID** `EntityID` (indexed, unique where SharePoint supports it), `SchemaVersion`, `Revision`, `CreatedAtUTC`, `UpdatedAtUTC`, `SourceQualifiedID`, `AuthorityReference`, `Classification`, `SourceSystem`, `EffectiveFromUTC`, `EffectiveToUTC` where applicable. Use stable UUID and source-qualified key, not SharePoint `ID` or library URL, as cross-platform identity.
* Use plain text UUID foreign keys `DatasetID`, `OrganizationID` etc., and optional SharePoint display-only lookups; avoid making SharePoint lookup objects, Person fields, managed metadata types, URLs or list-item IDs part of a canonical domain record. Optional native term set fields are projections of canonical code-system, code and version.
* Preserve CKAN `name` slug and ID as distinct canonical fields. `extras` are key/value mappings, not a single SharePoint JSON blob if a business lookup/filter is needed. Keep ordered resources, multiple owners, relationships and versioned synonyms.
* Use `ETag` and `If-Match` for SharePoint optimistic concurrency; map these to domain `expectedRevision` conflicts. SharePoint lacks atomic multi-list transactions, so use durable command journal, idempotent writes, controlled compensating actions, failure state and reconciliation instead of claiming SQL transaction equivalence.
* Search is not an authorization system. Explicitly permission-check resource bytes and metadata separately. SharePoint indexes and pagination, bounded queries and permission-scope limits are part of the adapter contract.
* Asset references contain an abstract URI and stable AssetID plus checksum/version. Actual SharePoint file path remains in backend mapping and never becomes a durable public identifier; after migrating metadata to SQL, SharePoint can still hold document blobs.

## Migration without changing shared domain behaviour

1. Define and version domain DTOs and operations independently of the persistence engine. Commit backend-neutral fictional fixtures with representative datasets, resources, approvals and all medallion layers.
2. Use cross-adapter conformance tests: CRUD, filter/query semantics, paging, locale/date/NULL handling, many-to-many relationships, version conflicts, metadata access, file/version reads, audit provenance, expiry revocation, release rollback and error behaviour.
3. Produce exhaustive **snapshot export** with row counts, stable IDs, SHA-256 source/file hashes, revision/lineage edges, authority references and a migration watermark.
4. Create new Dataverse or SQL tables using stable IDs and explicit indexes; generate schema migrations. Validate type mappings (SharePoint Choice/MultiChoice, Person, Lookup, DateTime, managed metadata, multiline text) against canonical fields; never silently coerce.
5. Migrate snapshot and catch-up deltas using an idempotent outbox/change journal with recorded conflicts. Validate record counts, referential integrity, suppression and access; perform a dual-read **shadow comparison**, not uncoordinated dual-writes.
6. Freeze writes at a controlled cutover point, replay final journal, switch the **CareOps provider** (not CKAN ORM), verify user/read/report workflows and negative security tests. Keep backward mapping and reversible fallback; retain prior SharePoint storage for the agreed retention period. Document and test the reversal before cutover.
7. Confirm future provider's licensing, access model, infrastructure/service principals and support/backup architecture. Dataverse virtual tables are not a transparent migration and can have reduced security/feature semantics; require explicit admission.

## CareOps integrated-source clarification

The parent `careops` is the **reference and integration codebase** for the family of reusable libraries, as those sources are admitted and physically integrated. This supersedes the catalogue-specific assumption that a separate `careops-catalogue` GitHub repo must be created. **Do not** arbitrarily re-home or decommission already independently versioned sibling modules; their existing current Gitlinks, implementation provenance and release states remain in force until their separate planned integration tracks complete.

Add the catalogue at `modules/careops-catalogue/` as ordinary maintained source once source licensing/security and architecture tests pass, using the existing parent Conductor track. External CKAN can later be an upstream pinned gitlink, container image digest or versioned dependency **without any upstream source modifications**. Integrating library *source for reference* must not make every library a mandatory installed runtime. Runtime and tenants remain optional, versioned deployment profiles.

## Acceptance conditions

- A demonstrated **real CKAN** test executes stock CKAN + its supported services + extension, *not* a SharePoint façade alone; assert no upstream patches.
- A demonstrated **SharePoint MVP** test executes SPFx + SharePoint adapters; do **not** describe it as running the native CKAN server.
- A new provider passes the exact same domain/functional/security conformance suite. Expect work for adapters, migrations, tenant permissions and deployment; **no guarantee of zero changes to integration code across all major releases**.
- Compatibility tests against each upgraded CKAN release inspect official action schemas, auth, extension interfaces, resource visibility, API error handling and upgrade migrations.
- Zero simultaneous authoritative writers; fail closed on synchronisation lag for protected access and publication decisions.

## Official basis

* CKAN 2.12.1 installation: https://docs.ckan.org/en/2.12/maintaining/installing/index.html
* CKAN 2.12 FileStore configurable storage: https://docs.ckan.org/en/2.12/maintaining/filestore.html
* SQLite file locks/corruption: https://www.sqlite.org/howtocorrupt.html and https://www.sqlite.org/useovernet.html
* CKAN services: https://docs.ckan.org/en/2.12/maintaining/installing/install-from-source.html
* DataStore backend extension: https://docs.ckan.org/en/2.12/maintaining/datastore.html#extending-datastore
* CKAN extension best practices: https://docs.ckan.org/en/2.12/extensions/best-practices.html
* SharePoint List View Threshold: https://support.microsoft.com/en-us/sharepoint/lists/data-and-lists/list-view-threshold-for-large-lists-and-libraries
* SharePoint optimistic concurrency: https://learn.microsoft.com/sharepoint/dev/sp-add-ins/complete-basic-operations-using-sharepoint-rest-endpoints
* Dataverse virtual tables limitations: https://learn.microsoft.com/en-us/power-apps/maker/data-platform/create-edit-virtual-entities
