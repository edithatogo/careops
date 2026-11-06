# CKAN-compatible catalogue with medallion and PPG interoperability

**Status:** proposed specification (source-only). **Date:** 2026-11-06. **Scope:** reference-source `modules/careops-catalogue` proposed for CareOps parent integration, maintaining separate deployments. CHHHS is a deployment profile, not a hard-coded organisation. Read [CKAN/backend decision](../../../docs/clinical-data-catalogue/adr-ckan-core-and-backends.md).

## Product requirements
- CKAN Organization/Dataset/Resource/Group/Tag semantics, canonical UUIDs, source provenance, resource metadata separate from assets, privacy-safe discoverability and CKAN/DCAT export contracts. SharePoint Lists are the MVP persistence backend; an unmodified real CKAN server is a separately deployed optional mode with native PostgreSQL, Solr and Redis.
- Four logical zones: raw restricted Bronze, validated Silver, clinically qualified aggregate Gold, approved data-product Platinum. No claim of SharePoint Delta Lake, live PostgreSQL CKAN DataStore, or general compute platform.
- SharePoint/SPFx 1.24.1/React 18.3.1 baseline; standard connectors only; no new Entra scopes, no PPU, Fabric, Copilot or paid connectors. Qualify any site-collection app-catalogue prerequisite.
- PPG, Approve and Decisions are *optional* authoritative reference providers, with fail-closed verification/entitlement states and human decisions. RIMS remains owner of publication and DORA activity registries.
- Idempotent ingestion and releases, full lineage and access-revocation tests, reproducible schemas, automated accessibility and supply-chain testing. Source-only fictional fixtures.
- Provider-neutral repository/file/lineage ports and shared conformance tests for SharePoint, future Dataverse and SQL Server. SQLite in a SharePoint/OneDrive-synchronised library is **not** a live database option; immutable SQLite snapshots are optional offline artefacts. Dependencies unmodified, exact pinned revisions and upgrade canaries. Existing Conductor submodule reused; Gemini CLI activation is a distinct, unverified host compatibility gate.

## Out of scope
Patient-level/raw restricted processing in SharePoint; autonomous clinical decisions; building replacement research ethics approval; universal PBI viewing; new tenant admin rights; duplicate CareOps modules; production deployment; premium/Copilot capabilities.

## Completion evidence
Contract schema validates, synthetic workflows and 4-zone lineage/denial tests pass, no sensitive records in source history, app catalogue and licences qualified with native receipts before deployment, source-control parent updated only after independent module source and licence/security checks.
