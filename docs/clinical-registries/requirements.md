# Virtual clinical registry programme — requirements

**Status:** proposed, source-only requirements (13 November 2026). **Scope:** CHHHS pilot within an organisation-neutral CareOps integration pattern. **Authority:** existing Queensland Health state policy, approved custodians and institutional research pathways; no approval or live connection conferred by this document.

## Purpose and boundaries

Enable discovery and selective integration of existing clinical registries; establish a hybrid toxicology/toxinology registry and then a second existing registry (e.g. trauma), using existing **Rhapsody → Databricks → MSSQL DWH** infrastructure, selectively connected to **OneLake/Fabric**, REDCap, Power BI and Excel. Avoid recreating extraction pipelines, a second warehouse, a new ethics structure or mandatory migration of established registries.

This is **not** a declaration that Rhapsody delivers every clinical feed, Databricks uses Unity Catalog, the warehouse is mirror-compatible, Fabric is licensed, or real patient data may be processed in a new tenant. Confirm these in the appropriate deployment environment.

## MoSCoW priorities

| ID | Priority | Requirement / testable outcome |
| --- | --- | --- |
| REG-01 | Must | Inventory existing registries and accountable owners without migrating them or replacing their approvals. |
| REG-02 | Must | Record source-qualified registry identifier, purpose, owner/custodian reference, current platform, dataset description, classification and existing authority links in the existing CareOps/SharePoint catalogue. Metadata visibility does not grant data access. |
| REG-03 | Must | Distinguish clinical operations, QA, evaluation and human research; refer decisions to existing QH/FNQ HREC and research governance pathways. No umbrella permission or blanket waiver inferred. |
| REG-04 | Must | Preserve existing Rhapsody → Databricks → MSSQL ownership and downstream consumers; publish *read-only*, purpose-specific clinical data products through an approved interface. |
| REG-05 | Must | A registry definition is machine-readable, Git-versioned, has inclusion/exclusion criteria, clinical concepts, dataset/terminology versions, data steward and validation tests. |
| REG-06 | Must | Clinician views and research views use separate, authorised access boundaries; minimise identifiers. Prove restrictions across Power BI/Excel/SQL/OneLake where enabled. DDM/labels are not sole authorisation controls. |
| REG-07 | Must | Each run preserves lineage: code commit, definition revision, source data versions or durable authorised snapshots, execution ID, output version, timestamps and checksums/quality results. |
| REG-08 | Must | Existing REDCap registries remain operational; only specialist missing fields are collected anew; no requirement for all registries to adopt FHIR or OMOP. |
| REG-09 | Must | Clinicians with existing authorisation can filter cohorts, inspect curated fields, and make permissible self-service extracts without writing SQL; no implied authorisation to share/export externally. |
| REG-10 | Must | Source repo and CI contain only synthetic/non-sensitive examples, schemas and code; no private clinical data, tenant identifiers, secrets or approval evidence. |
| REG-11 | Should | Evaluate Unity Catalog → Fabric mirroring/shortcuts, checking supported table types, credential scope, policy translation, refresh and actual data-copy semantics; use direct SQL or MSSQL route if unsuitable. |
| REG-12 | Should | Fork a transformation into an isolated Git branch/environment, run old/new definitions on the same approved snapshot and report inclusion changes, missingness, concordance and performance. |
| REG-13 | Should | Deliver Power BI operational and QA semantic-model templates with documented freshness, role tests, source definitions and export restrictions. |
| REG-14 | Should | Cross-registry encounters and outcomes can be reused without rekeying original registries; preserve cross-facility linkage permission and confidence. |
| REG-15 | Could | Geography/retrieval and environmental linkage, patient-reported outcomes, risk adjustment, clinical quality feedback and OMOP research exports. |
| REG-16 | Could | NLP-assisted ascertainment, registry trials, digital twins, federated research after validation and appropriate specific authorisations. |
| REG-17 | Won't now | New blanket HREC, new governance committee, replacement Rhapsody feed, second Databricks/Fabric medallion ingestion stack, universal EMR writeback, urgent automated clinical alerts. |

## Existing registry participation

- **Level 0 Catalogue:** discover name, owner, clinical scope, authoritative location.
- **Level 1 Describe:** record approved dictionary and existing authorisation references.
- **Level 2 Connect:** approve a narrow read-only data path with custodian/ICT/security controls.
- **Level 3 Analyse:** approve each *new purpose/use* and publish restricted clinician or research data products.

Registries remain at Level 0/1 without penalty. Registration and technical connectivity do not themselves permit additional processing.

## Minimum acceptance demonstrations

1. A fictional toxinology cohort and one fictional existing registry are catalogued without moving either source.
2. A shared transformed encounter can enter both registry definitions without re-keying the source.
3. Git fork + pipeline run with fixed synthetic input yields reproducible output and an inspectable delta report.
4. A negative permission matrix rejects unauthorised rows, columns, extraction and direct source access for every enabled consumption route.
5. Clinical and research-facing outputs expose appropriately different identifier and export privileges, with data provenance and freshness shown.
6. No new QH tenant access, HREC approval or live clinical integration is asserted by the source demonstration.

## Required discovery before deployment

Confirm: Databricks workspace/Unity Catalog/Delta layout, existing MSSQL version and ownership, Rhapsody interfaces, warehouse transforms, approved storage region, existing Fabric capacity, tenant licensing, Power BI entitlements, REDCap instances, QH data custodians and privacy/recordkeeping requirements, and whether an existing clinical registry catalogue already covers Level 0/1.

See [design](architecture.md) and [Conductor implementation track](../../conductor/tracks/virtual_clinical_registry_20261113/index.md).
