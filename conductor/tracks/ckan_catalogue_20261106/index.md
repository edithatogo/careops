# CareOps Catalogue — implementation track

**Historical track ID:** `ckan_catalogue_20261106` (retained for link stability; **no CKAN runtime**).

- [Specification: organisation-neutral, SharePoint-native](spec.md)
- [Ordered milestone plan: M0 readiness → M1 core → M2 quality → M3 integrations → M4 enhancements](plan.md)
- [Architecture, opportunities and CareOps capability/owner integration map](../../../docs/clinical-data-catalogue/architecture.md)
- [Core physical schema: two Lists and one Library](../../../portfolio/careops-catalogue-sharepoint.v1.json)
- [Build plan, permissions, CLI and coding-agent assignment](../../../docs/clinical-data-catalogue/sharepoint-native-build-plan.md)
- [Microsoft 365 feature radar: short, medium, long, preview/development](../../../docs/clinical-data-catalogue/platform-dependency-radar.md)
- [Gemini CLI setup with existing upstream Conductor Agent Skills](../../../docs/clinical-data-catalogue/conductor-gemini-cli.md)
- [Versioned canonical metadata and optional CareOps producer contracts](../../../portfolio/careops-catalogue-contract.v1.json)
- [Historical CKAN backend ADR — superseded, not roadmap](../../../docs/clinical-data-catalogue/adr-ckan-core-and-backends.md)

**Scope:** the CareOps parent is an organisation-neutral reference/source control plane. Catalogue is a proposed optional in-tree module, not a mandatory service or a substitute for existing module authorities. No native Microsoft environment is configured, and source tests cannot establish operational deployment. All premium/Copilot capabilities remain out of scope.
