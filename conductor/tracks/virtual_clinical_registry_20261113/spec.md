# CHHHS virtual clinical registries — specification

**Track:** `virtual_clinical_registry_20261113`  
**Type:** feature / design; **status:** proposed source requirements and architecture, not a production deployment.

## User value

Clinicians discover existing governed registries and create/compare authorised cohorts and exports without rebuilding clinical ingestion. Existing registries retain operations and authority. New toxinology and existing trauma/other registries can reuse common patient/encounter/outcome transformations. Researchers receive only purpose-authorised products.

## Requirements and acceptance contract

`docs/clinical-registries/requirements.md` is the normative MoSCoW and testable acceptance record. `docs/clinical-registries/architecture.md` is the normative technical design.

Essential: existing Rhapsody → Databricks → MSSQL untouched; optional OneLake/Fabric; existing CareOps SharePoint-native catalogue; Git-managed registry definitions and Databricks transformation releases; run-level data provenance; read-only data products; segregated identifiable and research consumption; no second governance authority or blanket HREC assumption.

## Explicit non-goals

No live clinical data import, credential/tenant setup, state policy replacement, research approval, migration of all registries, redesign of Rhapsody or MSSQL, FHIR/OMOP-everywhere, AI writeback, or production alerting as part of this source track.

## Open technical decisions

- Verify Databricks Unity Catalog/Delta/retention, actual publishing ownership and supported Fabric integration.
- Determine the source of truth for source transformations and whether MSSQL has only downstream projections or unique transforms.
- Verify native security, OneLake/Power BI export paths, licensing, deployment boundaries and existing register coverage.
- Establish the first authorised existing registry alongside toxinology; do not assume the statewide trauma dataset can be replicated.

## Source-completion evidence

Conductor submodule must remain exact-pinned, setup must not overwrite existing tracks, docs must describe source-only state correctly, GitHub checks must pass, and synthetic proof of two registries, fork/replay and security-negative controls must be scoped into future implementation tracks.
