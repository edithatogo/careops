# CKAN-compatible clinical data catalogue: architecture decision record

**Status:** proposed source contract; **date:** 2026-11-06; **owner:** proposed in-tree reference-source `modules/careops-catalogue`, with separate deployment/runtime boundaries. No CHHHS production installation or data access is asserted.

**Clarification:** [Unmodified CKAN and replaceable backends](adr-ckan-core-and-backends.md) governs the architectural boundary. SharePoint-first mode is a CareOps catalogue with CKAN semantics, **not** a running native CKAN server. Native CKAN 2.12.x requires its PostgreSQL/Solr/Redis stack; CKAN 2.12 adds configurable file-keeper-backed storages, so SharePoint Library file storage is a plausible **custom adapter** without patching upstream CKAN.

## Decision

Create an organisation-neutral catalogue as ordinary **planned reference source inside the CareOps parent**, while retaining independent runtime, release and deployment contracts. The CareOps family integration roadmap is authoritative for existing sibling migrations; do not re-home them out of turn. CHHHS-specific tenant configuration stays outside reusable source. No runtime database is deployed in CareOps; no new repository, gitlink, tenant object or deployable solution is created by this decision.

The initial SharePoint persistence adapter uses SharePoint Online Lists/Libraries, SPFx, and **standard** SharePoint/Power Automate capabilities only, behind provider-neutral domain/repository/asset/authorization contracts. Future SQL Server and Dataverse adapters are separate capabilities; a real CKAN runtime is optional and separately deployed. Power BI Pro is an optional licensed analytical outlet; PPU, Fabric/OneLake, Dataverse premium, Syntex, Copilot, AI Builder and premium connectors are out of implementation scope. Never describe a SharePoint staged store as a native Delta Lake or a true CKAN installation.

## Physical and logical model

* `CKAN_Organizations`: stable OrganizationID, name, parent, ownership and organisational scope. Ownership is **not** a permission boundary.
* `CKAN_Datasets`: stable DatasetID UUID, OrganizationID, title, scope, custodian, purpose, status, classification, metadata revision, provenance. Legacy alias `CKAN_Packages` only at the adapter boundary.
* `CKAN_Resources`: **list** of ResourceID UUID, DatasetID UUID, type, MIME/format, asset/external URI, licensing, publication revision, classification, access policy. Supports files, API, REDCap, Power BI report and externally hosted assets; no document-library-only assumption.
* `CKAN_DataAssets`: governed library for actual file-backed assets, with immutable or preserved versions, checksums, access classification and separate release metadata.
* `CKAN_Vocabularies` and `CKAN_Mappings`: versioned, sourced relationships for METEOR, SNOMED CT-AU, ICD-10-AM, ACHI, local concepts; ambiguous matches are review-required, not silently authoritative.
* `CKAN_Groups`, `CKAN_Tags` and bridge lists: allow many-to-many CKAN concepts, curation and future DCAT export without flattening semantics.
* `CKAN_GovernanceLinks`: optional identifiers/revisions linking dataset/resource to approved careops-approve request, careops-decisions evidence, PPG controlled documents, authoritative ERM/HREC/SSA records. This is a projection, not an approval source.
* `CKAN_AccessEntitlements`: access-scoped projection of verified grants/revocations, with requesting principal, resources, scope, decision reference, expiry, observation and reconciliation timestamps. No identity or clinical data in source control.
* `CKAN_ReleaseManifests`: immutable release decisions for approved Platinum products, input Gold revisions, classification and disclosure checks, authorised delegate, publication timestamp and withdrawal/supersession.

Use externally stable UUIDs rather than SharePoint item IDs as interop keys. Indexed SharePoint queries, server pagination and bounded relationship joins are mandatory; avoid unbounded lookup expansions and item-level permissions at high cardinality. Search indexing is eventually consistent, never the access control. No cross-organisation security follows from CKAN Organization membership alone.

## Four-layer logical medallion (not a native SharePoint lakehouse)

| Zone | Product/contents | MVP physical implementation | Required promotion proof |
| --- | --- | --- | --- |
| **Bronze** | Original received extract, header/schema, receipt, hash, source licence, observation timestamp, consent/authority tag, classification | Restricted SharePoint library `CKAN_Bronze` for explicitly approved *non-identifiable* small extracts, or metadata-only reference to an approved external clinical source | Provenance, checksum, malware/security screening as available, classification and legal intake gate |
| **Silver** | Typed canonical records; schema version; resolved controlled vocabulary and unresolved mappings; validation and lineage | Indexed lists and/or versioned SharePoint files `CKAN_Silver` | Deterministic schema tests, duplicate/idempotency policy, exception quarantine, quality statistics and reviewer sign-off where needed |
| **Gold** | Clinically validated, disclosure-controlled aggregate indicators, denominators and risk-adjustment inputs, reproducible snapshot | Versioned curated SharePoint exports/metadata and optional Power BI Pro semantic model in separately authorised workspace | Named custodian acceptance, reproducible transformation, statistical validation, small-number suppression, data-use confirmation |
| **Platinum** | Approved **published data products**: CKAN/DCAT catalogue representations, accessible charts/reports, approved downloads/endpoints and immutable release manifest | SPFx portal plus approved released resources and export snapshots `CKAN_Platinum` | Authorised publish decision, access and revocation tests, no unsafe inference, maintained stable URL and rollback |

Platinum is an optional project-specific product/approval layer; Microsoft's canonical medallion convention has Bronze/Silver/Gold. Each promotion creates a **new immutable or versioned artefact and lineage edge**, never overwrites the upstream source. Block promotion on unverified checks, metadata absence, failed connector refresh or expired approval. Gold and Platinum do not inherit permission grants automatically from Silver or Bronze.

For sensitive or unit-level clinical data, Bronze holds only a source pointer and sanitised manifest until an enterprise-approved protected environment is designated. Use standard Power Automate for bounded orchestration and small metadata transforms; it is **not** a general-purpose Spark/Dataflow replacement. Heavy server-side compute remains deferred unless an existing approved non-premium platform can be qualified. No in-browser bulk row processing.

## Boundaries with existing repositories

* `careops-approve` owns **intake, durable routing, human approvals, idempotency and expiry workflow**; catalogue never implements another approval engine.
* `careops-decisions` owns **formal committee/delegate decisions**; catalogue stores verified reference, not copied authority.
* `modules/careops-ppg` owns **policy and document lifecycle**; clinical publication remains through approved QHEPS route until formally migrated. PPG may record governance links but **must not** create an HREC/SSA approval.
* `modules/careops-rims` owns **publication/attribution registers**. Catalogue may discover RIMS outputs using reference links; do not import or re-key its Publication Registry/DORA Activity Registry.
* `careops-process` may consume minimum-necessary event metadata under optional, explicit agreement.
* `careops-finance` may supply aggregate report templates/patterns but is not the catalogue backend.
* `careops` parent keeps only tracks, compatibility contracts and release evidence.
* Archived `PPGWorkbench` and `ppg-workbench` are **predecessors**, not independent live governance backends.

All inter-module calls are optional and versioned with source-qualified IDs, revision, correlation/idempotency key, actor, observedAt, authority provenance, error/absence and retry semantics. Failure of a sibling cannot silently grant access, publish content or fabricate approval. Never bind to undocumented native tenant IDs.

## Security, clinical governance and operational gates

1. Support **metadata visibility separately from file/BI access**. Denial must be enforced by SharePoint/Power BI, not SPFx UI or URL query filtering.
2. No SharePoint group grant automatically grants Power BI access; require independent RLS/OLS and viewer-licence qualification if BI later enabled.
3. PPG case state != ERM authority != resource entitlement. Verify authoritative approvals and specific delegated decision makers; record missing/expired evidence as restricted.
4. Maintain recoverable issue/revoke/reconcile journal; require expiry and periodic owner attestation, separated duties and negative tests.
5. Keep all patient, staff, tenant, credential, exact environment, source extracts and operational decisions **out of Git**. Source tests use fictional fixtures.
6. Establish records, privacy, cyber, approved retention and restoration gates before production. Native permissions, app catalogues, licensing and information classification remain to be tested in CHHHS environment.
7. Use accessibility WCAG 2.2 AA target, mobile-responsive views, keyboard operation, screen-reader testing, evidence-based indicator labels and usable denial/error states.

## CKAN/DCAT interoperability

CKAN action API `/api/3/action/package_list` and `package_show` are **not** implemented by SharePoint REST; SharePoint-first mode requires an explicit, explicitly scoped compatibility adapter/export with tests for CKAN response envelopes, dataset/resource/group/organisation semantics and access-redacted fields. DCAT/DCAT-AP is an independently versioned export mapping with appropriate profile validation; do not assert blanket DCAT-AP compliance until a jurisdictional profile is selected and tested.

## Pilot acceptance

Synthetic mixed resources (PDF, CSV, API, REDCap link, report) demonstrate stable IDs, faceted navigation, permission-trimmed metadata, independent asset denial, expired-approval refusal, fail-closed missing governance, bounded SharePoint queries, ingest dedup, Bronze→Silver→Gold lineage, authorised Platinum release, export interoperability, restore and rollback. Do not claim operational deployment solely from code/contract tests.
