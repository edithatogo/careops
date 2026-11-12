# ADR 0006: Power BI Deferred Until Stable Dataverse Data

## Status

Accepted.

## Context

Governance reporting is important, but Power BI/Fabric reports are only useful after Dataverse tables, relationships, security, and sample data are stable.

## Decision

Start reporting with Dataverse views and app dashboards. Defer Power BI/Fabric implementation until the Dataverse model and MVP workflows are stable.

## Consequences

- Metrics and semantic model boundaries should be documented now.
- Power BI security must align with Dataverse roles and committee membership later.
- Power BI/Fabric must not block MVP release.

## Addendum — 11 November 2026 (does not rewrite the original decision)

The original Dataverse MVP deferral remains historically valid. A new [CareOps reporting Conductor track](../../../../conductor/tracks/decisions_clinical_hub_reporting_20261111/index.md) and [source-neutral analytics contract](../../powerplatform/src/reporting/clinical-hub-analytics-contract.md) specify **future optional reporting** over a separately qualified SharePoint Standard or Dataverse source. PBIP/TMDL, PBIR and RDL are not part of the default non-premium operational core; their licensing, source access, secure aggregation, native refresh and deployment require independent acceptance. This addendum is not evidence that the original Power BI deferral has been lifted or that any reporting artifact has been implemented.
