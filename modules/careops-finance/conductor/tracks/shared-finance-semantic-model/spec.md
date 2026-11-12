# Shared Finance Semantic Model

## Objective

Create the shared Power BI semantic contract that supports both VMO finance and Medical Staff reporting while keeping raw Access data out of source control. Build separate dashboard models first, then promote stable common definitions into `src/powerbi/shared/`.

The detailed contract now lives in [docs/shared-semantic-model.md](../../../docs/shared-semantic-model.md).

## Source Inputs

- `data/raw/VMO Reporting.accdb`
- `data/raw/Medical_Staff_Reporting.accdb`
- Local inventory JSON under `data/profile/`
- Power BI source folders under `src/powerbi/`

## Requirements

- Classify Access objects into facts, dimensions, calendars, linked dependencies, and pass-through dependencies.
- Define the initial star-schema model for shared finance reporting.
- Decide which transformations belong in Power Query M versus upstream SQL/pass-through replacement.
- Create reusable M query templates that parameterize raw data paths.
- Create a calendar/date strategy usable by both dashboards.
- Add core measures for totals, reconciliations, counts, and period filters.
- Export shared/common model assets to `src/powerbi/shared/model-tmdl/` only after common definitions have stabilized.
- Keep the VMO and Medical Staff dashboards separate until the shared contract is stable enough to merge.
- Use `docs/shared-model-merge-readiness.md` as the gatekeeper for any future shared semantic model export.
- Treat existing standalone PBIR/TMDL exports as model-comparison inputs only; do not copy them into `src/powerbi/shared/model-tmdl/`.

## Acceptance Criteria

- Model design document lists tables, relationships, grain, and dependency risks.
- Power Query templates exist for the selected local tables.
- TMDL export paths are documented for each standalone dashboard and for the later shared model.
- Validation can run without committing source data.
- The shared contract lists which dimension and measure candidates are eligible for later promotion after SQL validation.
- Shared-model implementation remains blocked until the merge-readiness gates pass.

## Implementation Package

The DAX/model implementation package is source-controlled, and the current live Desktop sample models have been built/refreshed from the available sample/source surface:

- `docs/model-build-plan.md` is the build plan for table roles, relationships, date tables, measure order, TMDL export posture, and validation gates.
- `src/powerbi/shared/m/SharedFinanceContracts.m` carries the shared implementation contract as an M record that can be reused by later pbi-cli/TMDL automation.
- `src/powerbi/dashboards/vmo-finance/model-tmdl/measure-catalogue.md` is the VMO Finance measure catalogue.
- `src/powerbi/dashboards/medical-staff/model-tmdl/measure-catalogue.md` is the Medical Staff measure catalogue.

Live TMDL exports now exist for the standalone dashboard models. SQL host/listener is supplied as `<sql-server-host>`; live database/schema and gateway validation remain open.

Current merge posture: do not create shared model TMDL yet. The next evidence step is SQL validation plus TMDL/PBIR comparison under the merge-readiness gate sequence.
