# CareOps data catalogue — implementation track

**Track identity:** `ckan_catalogue_20261106` (retained to preserve existing links and historical commits; this does **not** prescribe a CKAN runtime).  
**Status:** planned, source-only; no SharePoint deployment or native tenant access is evidenced.  
**Product:** an organisation-neutral, SharePoint-native **CareOps Catalogue** that can be deployed independently. Existing CareOps modules keep their authoritative records and release lifecycles.

## Decision and exclusions

Build the **smallest operational core first** with SharePoint Lists as the catalogue database and SharePoint Libraries as the file store. Use native forms, indexed views, site pages, columns/content types, versioning and permission controls. No bespoke SPFx React app, no native CKAN server, no CKAN Python/file-keeper adapter and no imitation CKAN Action API in the delivery roadmap. CKAN concepts may inform metadata and optional future DCAT/JSON export **without a CKAN software dependency**.

Do not introduce Copilot, AI Builder, paid/premium connectors, Fabric, PPU, Power Apps Code Apps or other premium services. These are future feature-radar topics only. Do not introduce a mandatory new workflow, governance authority, search engine or shared cross-module database. Preserve exact existing Conductor submodule, upstream dependencies, privacy, security and source-publication rules.

**Medallion:** Bronze/Silver/Gold/Platinum are initially *logical provenance, quality, curation and publication states*, not four separate databases/libraries or a claim of a Delta Lake. A new physical library/site requires an evidenced information-classification, retention or operational need.

## Ordered implementation — deliver core before layering

### M0 — Local/source admission and capability check (blocks live writes only)
- [ ] **M0.1** Inspect current `main`, the open catalogue PR, `portfolio/repos.json`, `portfolio/module-catalog.md`, `portfolio/delivery-catalog.json`, `portfolio/power-platform-alm.json`, existing module tracks, `docs/development-and-delivery.md` and the scoped profile for the **target deployment**. Record ownership overlaps and use exact source-qualified IDs.
- [ ] **M0.2** Checkout the **existing parent Conductor gitlink** unchanged; verify skills in the selected coding agent and preserve existing track state. Inventory Git/CLI, Node, Microsoft 365 CLI or PnP.PowerShell and installed tools by exact version.
- [ ] **M0.3** Confirm approved **non-production site** and delegated app authentication. Distinguish site rights to create Lists/Libraries/columns from Entra application consent and SharePoint app-catalogue rights. Read-only capability report first. No site write without named owner approval. Keep identities, tenant/site URLs, private readbacks and secrets out of public source.
- [ ] **M0.4** Confirm existing organisation taxonomy and whether a dataset/resource catalogue already exists; reuse rather than duplicate. Freeze a minimal, tenant-neutral schema manifest and fictional fixtures. Stop on insufficient security, retention or app permissions; build offline in that case.

**M0 exit:** clean source validation and explicit either *approved test-site capability* or *recorded blocker*. No production installation claim.

### M1 — Functional catalogue core (first usable release; no optional modules required)
- [ ] **M1.1** Provision **`Catalogue_Datasets` List, `Catalogue_Resources` List and `Catalogue_Assets` Document Library**, with stable UUID-string IDs, DatasetID/ResourceID relationships, owner, abstract, purpose, classification, lifecycle, controlled source attribution, link/asset type, version and review fields. `Catalogue_Organizations` is conditional on inability to reuse an existing approved register. Use versioned site columns/content types and indexed views; do not create all proposed extra tables.
- [ ] **M1.2** Make provisioning idempotent and **dry-run by default**; read back column internal names, indexes, library metadata, permissions, views and existing items; provide controlled rollback. Never silently delete an existing list/library to resolve drift.
- [ ] **M1.3** Configure a Modern Site Page and native List/Library web parts, Microsoft Lists registration form and native form JSON, filtered views, metadata links and resource preview/download. Display permissions must be enforced at the physical file/list boundary, not by UI decoration.
- [ ] **M1.4** Seed **fictional** data covering file-backed, external-link, dictionary, report and restricted-resource metadata. Verify create/edit/search/filter, dataset→resources→file, duplicate/revision collisions, denied file reads, missing file, superseded item, restore and no unsafe automatic publication.
- [ ] **M1.5** Export a deterministic, documented and re-importable metadata snapshot (CSV/JSON) with stable IDs and schema version; do not implement a CKAN API. Add a small manual status/reconciliation checklist, not an orchestration service.

**M1 acceptance:** a user can register, find, open, revise and retire a dataset and its resources using native SharePoint; owners can correctly restrict access and recover versions; no SPFx or external code runtime is needed. Record actual native site tests separately from fictional source tests.

### M2 — Reliability, quality and governance layering (after M1 accepted)
- [ ] **M2.1** Add controlled vocabularies (managed metadata/term store **if available**, otherwise source-qualified choice/reference values), provenance fields, ownership attestation, quality/metadata completeness scorecards and schema drift checks.
- [ ] **M2.2** Add governance **links/evidence references** to Approve, Decisions, PPG and applicable external authority; never duplicate their approvals or grant rights based solely on a catalogue status badge.
- [ ] **M2.3** Add **logical** Bronze→Silver→Gold→Platinum lineage with input hashes/versions, validation receipt, curation/aggregation evidence, explicit publication decision, expiry, withdrawal and rollback. Restricted/raw source data can remain in authorised source systems with a sanitised catalogue pointer.
- [ ] **M2.4** Add SharePoint List rules or one bounded **standard** Power Automate workflow only when a real task justifies it: missing required metadata, owner review reminder, status reconciliation or publication coordination. Test idempotence, loops, duplicate event delivery, delayed triggering and recovery. Never invent a second PPG/Approve workflow.
- [ ] **M2.5** Expand storage segmentation (sites/libraries) only when privacy/access, scale, retention or restore evidence warrants it. Permission classes are orthogonal to medallion stages.

**M2 acceptance:** reliable read/write and release governance, provenance and recovery on a representative fictional/approved pilot, no duplicate authority.

### M3 — Optional CareOps reference integration (module-owner acceptance required)
- [ ] **M3.1** Use [capability-to-integration map](../../../docs/clinical-data-catalogue/architecture.md#careops-capability-integration-map) as the single ownership contract. Start with **stable links and read-only metadata**, not cross-module live mutations.
- [ ] **M3.2** Qualification sequence: PPG/RIMS/Approve/Decisions links → Clinical Hub/Legacy Migration evidence catalogue → Process/Incidents/Costing/Finance permitted aggregate products → Sim synthetic scenarios. Never synchronise entire sibling databases into the catalogue.
- [ ] **M3.3** Add versioned data-product references (`SourceSystem`, `SourceQualifiedID`, `Revision`, `AccessClass`, `AssetURI`, `ObservedUTC`, `OwnerModule`, `ContractVersion`), with tests for absent modules, privacy redaction, stale links and no cross-runtime dependency.
- [ ] **M3.4** Optional exports: DCAT/CSV/JSON and source-qualified provenance. Validate only the selected target profile; do not claim a full CKAN API or external harvester until a consumer requires it.

**M3 acceptance:** every integration has one authoritative owner, optional access and independent deployment; no duplicated registers.

### M4 — Search, usability and feature additions (only when metrics warrant)
- [ ] **M4.1** Assess search coverage, query latency, metadata completeness, time-to-find, access-request rework and maintenance cost with real user tasks.
- [ ] **M4.2** Evaluate upstream **PnP Modern Search** unmodified (candidate 4.25.0 on 2026-11-06), only if advanced refiners/verticals are needed. Confirm app-catalogue enablement, API consents, managed properties, indexing freshness, accessibility, version/security/rollback. Do not build an SPFx equivalent.
- [ ] **M4.3** Explore native Document Sets, Teams tabs, Planner links, SharePoint Pages/Highlighted Content, cross-site search, content type gallery/term governance and reusable site templates. Add features only after an explicit information-architecture or operational case.
- [ ] **M4.4** Consider future feature radar, including preview/development options **only in isolated, non-production canaries**. No unsupported or premium feature may enter the core runtime or receive automatic promotion.
- [ ] **M4.5** Maintain provider portability through stable IDs, schema/asset export and a conformance fixture. A later move to Dataverse or SQL Server needs a new migration and permissions project; do **not** build speculative providers now.

**M4 exit:** incremental measurable benefit, independent upstream updates and demonstrated rollback. Source and workflow integrity tests pass on the exact PR head.

## Future feature radar and stop rules

The classified radar lives in [platform/dependency radar](../../../docs/clinical-data-catalogue/platform-dependency-radar.md). **Adopt now:** native SharePoint metadata, forms, views, versioning, standard flow. **Evaluate:** PnP Modern Search, content type gallery, term sets, Document Sets, cross-site views, schema drift, standard Teams/Planner integrations. **Research only:** optional Microsoft Graph delta/search, advanced API interfaces, external data feeds and open standards. **Future/excluded:** Power Apps Code Apps (Premium), AI Builder, Copilot in SharePoint/Copilot Components, Syntex/structured document generation (entitlement/credit review), Fabric/OneLake, Power BI PPU, premium connectors and paid process mining.

SharePoint/Power Platform preview/development features must have exact published release, licence/entitlement, supported environment, compatibility, privacy and rollback receipts. A roadmap announcement alone does not establish availability.

## Agent execution discipline

Implement one milestone at a time; complete actual acceptance evidence before progressing. Run local source checks and retain exact dependency pins, clean-history/privacy/public-inventory checks, idempotent fixtures and negative security scenarios. Any missing site admin/Entra delegated client/consent is a blocked cloud prerequisite, **not** authority to bypass it. Do not create patient/practitioner records or production exports in Git. Commit reviewed changes and reconcile Conductor/portfolio indexes after each accepted increment. Do not close the parent track on source-only tests.
