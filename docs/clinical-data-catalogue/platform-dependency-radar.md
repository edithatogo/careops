# Catalogue platform, dependency and future-features radar

**Verified public guidance:** 2026-11-06. This document is a source-development baseline, not a verified CHHHS licence/tenant inventory.

## Current core baseline (no premium feature dependency)

| Component | Selection | Qualification |
| --- | --- | --- |
| SharePoint Framework | **SPFx 1.24.1** (2 November 2026 maintenance release) | Use corresponding supported @microsoft/* package set on same SPFx version; production Yeoman generator `@microsoft/generator-sharepoint@1.24.1` |
| React | **18.3.1 exactly** | SPFx host runtime compatibility: do not independently upgrade to React 19 |
| Node.js | **26 LTS** for GA SPFx 1.24.x development; 22/24 supported alternatives | Explicit CI matrix, current security patch, no silent major jumps |
| TypeScript | SPFx-supported version, **not later than 5.8** for SPFx 1.24 per official compatibility table | Compile with Microsoft-provided toolchain; pin lockfile |
| Toolchain | Microsoft SPFx 1.24.1 generator and Heft build | Do not hand-roll SPFx webpack/React root or fork templates |
| SPFx data access | `SPHttpClient`, SharePoint REST and security-trimmed approved search | No new Entra application scopes or premium HTTP actions in MVP |
| Workflow | Standard SharePoint connector and `Send an HTTP request to SharePoint`; Teams approvals only when qualified | The SharePoint action only calls SharePoint REST, not arbitrary Microsoft Graph |
| Ingestion | Bounded files, versioned contracts, deterministic metadata transforms; no heavy compute assumption | Raw extracts must be classified and approved before upload; use existing systems for restricted clinical data |
| Analytics | Accessible SPFx metadata tables; curated SharePoint exports | Power BI **Pro** is separately optional if already licensed and access checked; PPU and paid capacity deferred |
| Conductor | Reuse **existing parent Git submodule** `.agents/plugins/conductor`, unmodified | Parent `.gitmodules` already records pinned upstream; ensure `git submodule update --init --checkout -- .agents/plugins/conductor`; do not create second checkout or modify upstream |

**Conductor host qualification:** Upstream currently publishes `plugin.json` and agent skills but not a `gemini-extension.json` manifest. Git submodule checkout is valid and host-neutral. Antigravity supports workspace plugin linking; Claude supports marketplace plugins. Gemini CLI **extension activation is not established** without a manifest/adapter and smoke test. Do not modify upstream to claim compatibility. Prefer workspace linking the unmodified upstream Agent Skills with Gemini CLI `gemini skills link <path> --scope workspace`, subject to a real host smoke test; see [activation procedure](conductor-gemini-cli.md). If an adapter proves necessary, it must live outside the submodule and be independently tested against actual Gemini CLI.

## Preview/development radar (feature-flagged, never a production dependency)

* `@microsoft/spfx-cli`: **prerelease** standalone scaffolder, with decoupled templates and independent supported Node requirements (currently documented Node 22/24 rather than Node 26). Run in an isolated **development canary**, compare generated files with GA Yeoman, and never replace the GA toolchain without qualification.
* New/edit panel override and SharePoint list extension improvements: test separately against tenant flighting, form semantics, permissions and accessibility; optional for editor UX, not necessary to discover datasets.
* Future SPFx 1.25 navigation extensibility, templates and platform innovations: monitor actual GA/preview release notes rather than dated aspirational roadmap entries. Candidate only.
* Graph-based endpoints, sensitivity labels, cross-tenant connections, SharePoint Embedded: require tenant/admin/licensing and records assessments; no baseline use.

## Explicitly deferred / future only

Microsoft 365 Copilot, Copilot UX components (despite SPFx 1.24 GA), agents, Syntex/SharePoint Premium, AI Builder, Power Apps Premium/Dataverse, Power BI PPU, Fabric/OneLake/Direct Lake/Delta/Spark, premium HTTP connectors, Graph Connectors, cross-tenant integrations. Keep replaceable, versioned interfaces for later. No premium or Copilot package may be imported as a baseline transitive runtime requirement.

## CKAN and SQLite storage decision

Initial operational catalogue metadata lives in SharePoint **Lists**, and document/medallion artefacts in **Libraries**, behind canonical provider-neutral ports. Do not install the CKAN server and call SharePoint a replacement for its PostgreSQL ORM; CKAN 2.12 supports pluggable **FileStore** (file-keeper), not replacement of its main catalogue database. A SharePoint file-keeper adapter is optional future development (not already available or qualified). SQLite files stored/synchronised in SharePoint may serve offline immutable snapshots, not active concurrent database state; see [ADR](adr-ckan-core-and-backends.md).

## Upstream-as-is dependency policy

1. Prefer official Microsoft packages, React, Fluent UI, standards libraries and upstream Conductor **without source edits, vendoring, patch-package or private forks**. Restrict package graph to SPFx supported combinations (as-is does not mean any arbitrary latest major release works).
2. Commit `package-lock.json` and exact package versions. `npm ci` for deterministic builds; use peer-dependency and SPFx runtime tests. Do not use `--force`, `--legacy-peer-deps` or overrides to mask incompatibilities.
3. A separate dependency-update canary checks latest secure release, SBOM/licence/vulnerability information, generates a proposed lockfile change and runs build, unit, contract, permission and accessibility tests. Human review and feature flag/rollback before promotion.
4. Git dependencies use exact gitlink SHA and explicit update PRs; parent submodules have `update = none` for optional runtime modules, so a generic `git submodule update --remote` must **not** be part of CI.
5. Upgrade Conductor independently via upstream gitlink PR; verify skill contract and host activation; never edit files inside the vendor checkout.
6. Keep core domain logic behind minimal adapter ports (`CatalogueStore`, `AssetStore`, `ApprovalEvidenceReader`, `EntitlementProvisioner`, `GoldProjection`, `MetadataExport`). An adapter version changes independently of canonical IDs and metadata schema.
7. Publish source qualification, current-head CI, licence review, software bill of materials and rollback receipts. Passing source checks never implies CHHHS deployment.

## Source-of-truth references

* https://learn.microsoft.com/en-us/sharepoint/dev/spfx/roadmap
* https://learn.microsoft.com/en-us/sharepoint/dev/spfx/release-1.24.0
* https://learn.microsoft.com/en-us/sharepoint/dev/spfx/compatibility
* https://learn.microsoft.com/en-us/sharepoint/dev/spfx/toolchain/sharepoint-framework-cli
* https://learn.microsoft.com/en-us/sharepoint/dev/general-development/site-collection-app-catalog
* https://learn.microsoft.com/en-us/sharepoint/dev/business-apps/power-automate/guidance/working-with-send-sp-http-request
* https://learn.microsoft.com/en-us/fabric/onelake/onelake-medallion-lakehouse-architecture
* https://github.com/gemini-cli-extensions/conductor
