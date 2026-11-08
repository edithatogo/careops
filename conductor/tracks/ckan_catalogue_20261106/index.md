# CareOps Catalogue — CKAN-inspired implementation and integration track

**Track ID:** `ckan_catalogue_20261106` preserves the explicit CKAN design lineage; **no CKAN runtime** is required or planned.

- [CareOps suite delivery and source-integration plan](../../suite-delivery.md)
- [Suite source-composition sequence and historical receipts](../../suite-delivery.md#source-composition-execution-plan--25-october-2026)
- [Parent delivery profile and task selection](../../../.careops/module.json)
- [Catalogue entry and integration boundary in the module catalog](../../../portfolio/module-catalog.md#catalogue-integration-boundary--proposed-6-november-2026)
- [CKAN reference model and functional mapping](../../../docs/clinical-data-catalogue/architecture.md#ckan-reference-model-and-functional-baseline)
- [Specification: CKAN-based design, organisation-neutral SharePoint implementation](spec.md)
- [Ordered milestone plan and its link to the CareOps integration plan](plan.md#relationship-to-the-careops-integration-plan)
- [Architecture, opportunities and CareOps capability/owner integration map](../../../docs/clinical-data-catalogue/architecture.md)
- [Core physical schema: two Lists and one Library](../../../portfolio/careops-catalogue-sharepoint.v1.json)
- [Build plan, permissions, CLI and coding-agent assignment](../../../docs/clinical-data-catalogue/sharepoint-native-build-plan.md)
- [Microsoft 365 feature radar: short, medium, long, preview/development](../../../docs/clinical-data-catalogue/platform-dependency-radar.md)
- [Gemini CLI setup with existing upstream Conductor Agent Skills](../../../docs/clinical-data-catalogue/conductor-gemini-cli.md)
- [Versioned canonical metadata and optional CareOps producer contracts](../../../portfolio/careops-catalogue-contract.v1.json)
- [Historical CKAN backend ADR — superseded, not roadmap](../../../docs/clinical-data-catalogue/adr-ckan-core-and-backends.md)

**Integration status:** the design and track are recorded in the CareOps parent. The intended implementation location is `modules/careops-catalogue/`; it remains a planned in-tree module, not materialised or deployed software. Follow M0/M1 before optional M2-M4 layers. Do not create a standalone catalogue repository, import CKAN source, or mark the source-composition programme complete for this module on the strength of documentation alone.

**Scope:** the CareOps parent is an organisation-neutral reference/source control plane. Catalogue is a proposed optional in-tree module, not a mandatory service or a substitute for existing module authorities. No native Microsoft environment is configured, and source tests cannot establish operational deployment. All premium/Copilot capabilities remain out of scope.
