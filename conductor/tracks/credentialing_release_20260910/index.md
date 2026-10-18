# Credentialing MVP source-contract release

Status: COMPLETE FOR SOURCE REPOSITORIES
Release: `credentialing-mvp-0.1`

## Outcome

The Policy Atlas collection and the core CareOps credentialing modules have been merged, version pinned and assembled into a disabled-by-default source-contract release.

This track establishes repository architecture, versioned interfaces, synthetic contract tests and evidence ceilings. It does not establish CHHHS policy approval, tenant deployment, live data access, silent-pilot performance or operating effectiveness.

## Completed

- [x] Merge the Australian credentialing and model-SoCP Policy Atlas collection.
- [x] Pin the Policy Atlas collection to an immutable commit.
- [x] Merge CareOps Approve credentialing intake and reconciliation contracts.
- [x] Merge CareOps Decisions committee recommendation and delegated-decision contracts.
- [x] Merge CareOps Process privacy-minimised event and assurance contracts.
- [x] Merge the generic CareOps Legacy Migration read adapters.
- [x] Merge the later-stage safety-signal boundary.
- [x] Merge generic finance and reporting patterns.
- [x] Pin the materialised CareOps Approve submodule.
- [x] Record merged and draft module states in a compatibility manifest and release receipt.
- [x] Keep every credentialing feature disabled or read-only by default.

## Next organisational gate

The next track must be jointly owned with CHHHS Credentialing, Clinical Governance, Medical Workforce, Digital Health, Records and relevant professional representatives. It should confirm the actual source-system interface, current policy and delegations, minimum data, baseline process and a synthetic end-to-end harness before any live data is used.
