# Implementation Roadmap

## Goal

Deliver finance reporting as a system: one governed semantic layer where definitions are genuinely shared, with separate thin reports for distinct audiences, and an optional combined executive report later. The repository foundation and source-control ready exports are complete; dashboard completion is now focused on checked-in PBIR report packages, embedded local sample evidence, executable acceptance checks, remote-dashboard discovery, and the remaining SQL Server host/gateway validation needed for publish refresh.

## Sequence

1. Keep `config/sources.json` as the source-of-truth registry for the inventoried Access sources.
2. Keep VMO Finance and Medical Staff as separate reports, backed by tiny embedded sample partitions for local inspection.
3. Use limited sample extracts from Access only to identify the minimum table and column subset required.
4. Define the SQL Server tables or views that will replace Access for published refresh.
5. Use SQL Server host/listener `<sql-server-host>`; capture the database/schema and gateway binding behind the DSNs, then validate published refresh against that contract.
6. Inventory the wider analytics share at `//example.invalid/analytics` in place, without bulk-copying dashboards locally. Current status from this workstation/session: access is denied.
7. Catalogue each discovered dashboard by path, type, source dependencies, subject area, audience, refresh pattern, and candidate shared model entities.
8. Map Service Agreement, Funding and Performance Supplement, KPI supplement, and budget allocation measures into a performance-target metadata layer.
9. Promote stable shared date, finance-period, account, cost-centre, service, organisation, KPI, target, and performance-band definitions into `src/powerbi/shared/`.
10. Keep the current PBIR/TMDL exports source-control ready and validate them through `SourceControlReady`.
11. Run PBIR/TMDL structural tests against exported artifacts whenever the required local CLIs are available, recording skipped or failed checks in the acceptance evidence.
12. Create additional thin-report tracks from the dashboard catalogue only after source contracts and shared-model candidates are known.
13. Enable deployment wiring only after SQL host/gateway, workspace, credentials, and dry-run evidence are confirmed.

## Recommended Improvements

- Keep source-specific logic isolated until the dashboard definitions are validated against the original Access outputs.
- Prefer shared contracts over duplicated query logic when both dashboards need the same table shape.
- Document refresh dependencies early, especially linked tables and pass-through queries.
- Treat Access extracts as development samples and validation references; published refresh should use SQL Server.
- Treat the analytics share as a remote inventory source. Use path/file metadata, PBIP/PBIR/TMDL parsing, and targeted temporary extraction only where needed; do not bulk copy the share.
- Treat public Service Agreement and KPI supplements as metadata sources for target logic, not as measured results. Keep intranet-only policy/procedure material out of git unless explicitly approved.
- Use CLI-first Power BI tooling: PBIR/TMDL source files, `pbi report`, `pbi visual`, pbi-tools-style extraction where available, and PowerShell discovery scripts. Power BI Desktop UI is an inspection fallback, not the primary build path.
- Final dashboard completion requires acceptance evidence plus SQL Server host/gateway validation; the repo itself is already source-control ready.
- Keep deployment manifests and environment-specific settings disabled until SQL host/gateway binding and publish-refresh dry-run evidence are available.

## Later Merge Path

1. Continue with separate thin reports while the business definitions are still changing.
2. Consolidate only stable shared dimensions, measures, and naming contracts into the shared semantic layer.
3. Add public KPI target metadata and Service Agreement domains as shared context for executive reporting.
4. Add further dashboards from the analytics share as thin-report tracks after metadata/source discovery.
5. If a combined executive view becomes useful later, build it as a thin report over the shared semantic model rather than collapsing source-specific reporting too early.
6. Keep raw Access files, dashboard binaries, extracts, generated profiles, intranet-only documents, and credentials outside git throughout the transition.


## Selective SharePoint library columns — 19 October 2026

User-selected implementation direction: reuse library columns for artifact identity, provenance, filtering and routing where the output already belongs in SharePoint. Reuse existing columns/content types and exact internal names before adding fields. This extends the structured-document preference; it is not proof of automatic Word-body generation.

Priority: When a retained SharePoint report output is selected, retain reporting period, source snapshot, model/calculation version, generated time and output revision. Keep Access/SQL/Power BI calculations and interactive reporting in their existing layers; no dashboard replacement.

Acceptance: map each property to its existing authoritative source and verify its actual type/internal name; read back the affected saved values and file identity. Update only changed values, guard modification-trigger loops and retries, and retain a recoverable preimage. Preserve human edits, original/issued history and exact reviewed revisions. Add no duplicate register, notifications, approval workflow, permission change, licence or runtime. Avoid putting private/internal-only values into properties that may travel inside a downloaded Office file.

Metadata readback and visible body rendering are separate checks. The Clinical trial stored a changed property while Word for the web still displayed the old body value. Do not claim scalar body refresh, narrative/repeating sections or generated Word/PDF fidelity from metadata success. Qualify those behaviours only for the selected document shape; retain working/manual outputs on a specific gap. Record one result in existing evidence, not another readiness pack.

Reference: https://learn.microsoft.com/sharepoint/dev/business-apps/power-automate/sharepoint-connector-actions-triggers
