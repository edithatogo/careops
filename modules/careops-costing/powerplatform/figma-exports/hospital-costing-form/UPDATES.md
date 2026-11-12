# What changed in this updated bundle

## Shift in scope
The original page was a generic hospital costing concept. This update reframes the entire set as a **NSW Health Budget Buildup Tool (BBT)** migration into Power Platform.

## Major updates
- Replaced patient/episode costing flow with a BBT workflow anchored in:
  - `SWInput`
  - `SWSetup`
  - `SWNotes`
  - `NSWHFormulas`
  - `Summ`
  - `SWBrief`
  - `BTSExtract`
  - `FTEExtract`
  - `ROSExtract`
- Added explicit handling for coded outputs:
  - 701–724
  - 728
  - 732 / 734 / 738 / 743
  - 820 / 822 and related FTE outputs
- Reworked the form wireframe to model position, award, roster, leave, and allowance capture
- Reworked the data model as a Dataverse-first design
- Reworked the migration view to show workbook-sheet-to-platform-component mapping
- Reworked the architecture view around identity, process, data, and publication layers

## New diagrams added
- **Security** tab
  - role tokens **M**, **S**, **E**
  - scoped access
  - seed role assignments
  - permission matrix
- **Delivery & ALM** tab
  - Dev / Test / UAT / Prod path
  - phased delivery plan
  - release guardrails
  - go-live readiness checks

## Design intent
The update does not just modernise the UI. It makes the target-state explicit for:
- governance
- approvals
- extract compatibility
- auditability
- build and release planning
