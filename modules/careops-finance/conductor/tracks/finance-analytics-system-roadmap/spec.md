# Finance Analytics System Roadmap

## Problem

The current repository has two dashboard streams: VMO Finance and Medical Staff. More finance dashboards exist under `//example.invalid/analytics`, but copying them to the local workstation would consume unnecessary disk space and may duplicate sensitive operational data.

The system needs to scale beyond two reports without turning into disconnected PBIX/PBIP files. The recommended architecture is a governed shared semantic model, with separate thin reports for distinct reporting audiences and a later combined executive report only where cross-domain navigation adds value.

## Goals

- Keep the current dashboards inspectable locally through embedded sample snapshots.
- Move shared calendar, cost-centre, account, classification, organisation, and finance-period logic into a governed shared semantic layer.
- Keep VMO Finance and Medical Staff as separate thin reports initially.
- Discover additional dashboards from the network share in place, using metadata and source-control extraction where possible rather than copying large binaries.
- Produce a dashboard catalogue that maps each report to source systems, tables, measures, refresh dependencies, audiences, and candidate shared model entities.
- Preserve ALM readiness: source code separated from data, no raw dashboards or extracts committed, and publish gates tied to workspace, gateway, SQL, and credential evidence.

## Non-Goals

- Do not bulk-copy the network share locally.
- Do not publish to Power BI Service until workspace, gateway, SQL database/schema, and credential details are confirmed.
- Do not collapse every report into one combined dashboard before source contracts and audience workflows are known.
- Do not commit PBIX/PBIT binaries, Access databases, exports, credentials, or local profile data.

## Recommended System Shape

1. Shared semantic model:
   - Date, financial period, cost centre, account, service, organisation, and classification dimensions.
   - VMO, GL, workforce, payroll, and future finance facts kept as separate fact tables.
   - Measures grouped by business domain and named consistently.

2. Thin reports:
   - VMO Finance report.
   - Medical Staff report.
   - Additional reports discovered from the analytics share.
   - Optional combined executive report after shared-model coverage is proven.

3. Remote dashboard catalogue:
   - Files are inventoried in place by path, size, modified time, extension, and owner-visible folder context.
   - PBIP/PBIR/TMDL folders are parsed directly when present.
   - PBIX/PBIT files are profiled only through lightweight metadata, temporary extraction to ignored workspace storage, or approved tooling, then deleted after catalogue generation.

## Acceptance Criteria

- A source-controlled roadmap explains how separate reports, shared semantic model, and future combined views fit together.
- A remote discovery plan exists for the analytics share and explicitly avoids bulk local transfer.
- The known UNC path and current access blocker are recorded.
- The current VMO and Medical Staff dashboards remain source-control valid.
- The next implementation steps are captured as a conductor plan.
