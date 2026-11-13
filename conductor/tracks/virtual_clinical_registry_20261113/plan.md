# Virtual clinical registry — incremental delivery plan

**Status:** M0 source design/setup documented; M1+ unimplemented. **Owner:** existing CareOps development workflow. Each stage is separately verifiable; no blanket cloud or clinical approval.

## M0 — Reconcile existing repository and Conductor (source-only)
- [x] **M0.1** Confirm official `gemini-cli-extensions/conductor` is already a gitlink in `.agents/plugins/conductor`, at its reviewed upstream commit; do not vendor, duplicate or auto-track main.
- [x] **M0.2** Preserve existing Conductor product/stack/workflow/tracks and existing SharePoint-native catalogue track.
- [x] **M0.3** Define minimum governance, existing-registry treatment, clinical architecture and modular project requirements.
- [x] **M0.4** Provide project Gemini instructions and a host-local setup/verification command; do not claim Gemini CLI activation on a host not accessed.
- [ ] **M0.5** On an authorised development host, initialise gitlink, link skills, reload Gemini CLI and verify activation using a fictional workspace; record exact host/tool results.
- [ ] **M0.6** Obtain repository CI result and perform conductor-review against this spec after PR creation.

## M1 — Existing-system reconciliation (read-only)
- [ ] **M1.1** Inventory Rhapsody feeds, Databricks layers/Unity Catalog, MSSQL owner/version and existing transforms; map source-of-truth ownership.
- [ ] **M1.2** Identify existing registries/REDCap and QH catalogue/authorisation records; choose one pilot existing registry.
- [ ] **M1.3** Confirm approved non-production Fabric/OneLake/Power BI capacity, identity, network, clinical privacy and data custodian boundaries; write compatibility decision record.

**Gate:** technical fact sheet and explicit no-access/blockers; no live writes.

## M2 — Registry-as-code contracts and synthetic tests
- [ ] **M2.1** Implement `RegistryDefinition`, `SourceDataProduct`, `TransformationRun`, `ConsumptionPolicy`, `RegistryIntegration` versioned schemas and fixtures.
- [ ] **M2.2** Build cohort engine adapter to an existing Databricks transformation, with registry-specific rules only; retain original pipeline and DWH.
- [ ] **M2.3** Add focused deterministic tests for two registries sharing encounter data, schema evolution and known edge cases.
- [ ] **M2.4** Implement Git branch/bundle diff-and-replay harness on fixed synthetic snapshots, reporting population/outcome/quality deltas.
- [ ] **M2.5** Review mutation/property/lineage tests proportionately using existing suite tooling; preserve non-sensitive run manifests.

**Gate:** repeatable source checks with zero tenant dependency.

## M3 — Secure consumption implementation (approved test environment)
- [ ] **M3.1** Publish a narrowly scoped curated product via verified Unity Catalog/Fabric path or approved SQL fallback; document read/copy semantics and cost.
- [ ] **M3.2** Build a clinical identifiable worklist semantic model, only for authorised care purposes.
- [ ] **M3.3** Build a separate aggregate or purpose-scoped research/QA semantic model.
- [ ] **M3.4** Run negative security matrix across workspace, OneLake, SQL endpoint, Explore, Excel and report export paths as applicable.
- [ ] **M3.5** Verify refresh/freshness, audit, incident revocation and recovery.

**Gate:** explicit custodian and ICT permissions; green source tests never equal native acceptance.

## M4 — Registry pilots and evaluation (specific clinical approval)
- [ ] **M4.1** Hybrid toxinology cohort and REDCap extension with specialist fields, adjudicated reference cases and quality criteria.
- [ ] **M4.2** Selectively integrate one pre-existing registry under its actual owner and approved purpose.
- [ ] **M4.3** Demonstrate longitudinal linkage, overlapping cohorts, reduced manual entry and controlled clinician extracts.
- [ ] **M4.4** Assess ethics/research classification and specific HREC/SSA/other approvals per proposed use, without treating infrastructure approval as a research waiver.
- [ ] **M4.5** Run prospective fitness-for-use evaluation, document limitations, review with clinical leadership and archive completed track only after acceptance.

**Later (not an MVP gate):** geospatial and retrieval analytics, target trial emulation, OMOP exports, AI-assisted case ascertainment, simulation and registry-based studies after specific validation/approval.
