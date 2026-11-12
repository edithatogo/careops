# Decisions / Clinical Hub analytics contract v0.1 (planning only)

**Status:** proposed canonical *analytical* contract for source adapters, model, dashboard and paginated report. Not a deployed model or report; no real patient, practitioner, meeting or private records. Proposed 11 November 2026.

## Provider and product boundaries

The source-neutral analytical layer has two distinct adapters: SharePoint Standard-backed Decisions/Clinical Hub records (preferred non-premium core) and optional legacy Dataverse Decisions records. The **authoritative owner** remains the source operational system, with exact source List/table identity, record ID, revision, accepted authority and effective interval. Do not copy governance writes into Power BI; not all historic Dataverse concepts have an equivalent non-premium SharePoint implementation. A missing optional field remains **not supported / not observed**, not `false` or `0`.

Power BI PBIP/TMDL, PBIR and RDL are separately licensed *optional* read-only reporting outputs. Existing Word/manual native reports and List views remain core fallback. This contract does not grant delegated access, enable cross-user exports, justify provider changes or activate a cloud flow.

## Core identity contract

- `governance_body_key`: source-qualified body identity.
- `forum_key` and `profile_revision`: explicit forum/profile, never inferred from display name.
- `series_key`, `occurrence_key`, `occurrence_revision`: stable occurrences including exceptions/cancellations.
- `minutes_key`, `minutes_revision`, `approval_ref`: source/approval, with approved/issued distinct.
- `decision_key`, `action_key`: source-qualified globally unique business IDs. A repeated action in multiple meetings does not create new action identity.
- `source_ref`, `source_revision`, `source_hash`, `record_etag`, `source_as_of_utc`: provenance and freshness metadata.
- `state_effective_from_utc`, `state_effective_until_utc`: support valid-as-of historical state, with explicit late corrections and supersession.
- `visibility_class`, `audience_policy_ref`: classification metadata, **not** enforcement of permission by itself.

### State distinction

`draft_discussion` ≠ `recommendation_pending` ≠ `adopted_decision` ≠ `commissioned_action` ≠ `reported_complete` ≠ `implementation_verified` ≠ `resolution_accepted`; `held`, `referred`, `returned`, `reopened`, `superseded` remain explicit states, each with exact authority and effective dates. Planner status is a **projection** and cannot be used as a closure authority. Missing evidence or business acceptance returns *unverified*, never inferred approved.

## Analytical tables and requirements

Use the canonical grain/relationship inventory in [Conductor design](../../../../../conductor/tracks/decisions_clinical_hub_reporting_20261111/design.md). A fact row's grain is documented in model metadata. Required dimensions: governance body, forum/profile, meeting occurrence, source, time, status, role/access. Required facts: meeting/agenda/paper, minutes revisions, decision state, action state, evidence/version lineage, outcome reviews, technical events and refresh quality. Bridge tables link shared actions across decisions and meetings; NEVER count joined fact rows directly where business identities are distinct.

Data availability states: `verified_complete`, `partial`, `stale`, `access_denied`, `unsupported`, `unverified`. Aggregates require an explicit coverage denominator and as-of. A missing List read, hidden row or disabled flow cannot generate an apparent zero or a silently reduced denominator.

## Measure registry

Canonical initial registry is [GOV-01..EFF-01](../../../../../conductor/tracks/decisions_clinical_hub_reporting_20261111/design.md#measure-contract-same-definitions-across-pbir-and-rdl). Each measure contract must record: immutable ID and version, display label, entity grain, eligible population, distinct aggregation key, numerator, denominator, exclusion/inclusion conditions, missingness, effective/as-of timestamp, time zone, status mapping, security group/context, source adapters, underlying evidence and acceptance fixtures. No release if a measure lacks one of these elements or PBIR/RDL results differ.

Measures to implement: governance bodies/ToR, meeting/quorum/readiness/latency, adopted/conditional decisions, accepted and overdue actions, reported-complete awaiting resolution, action rework, outcomes evaluated/attained, source-version exposure, technical recoveries, complete/fresh source coverage and measured net administrative effort. Outcome attainment is descriptive; no causal benefit is claimed absent an appropriate evaluation design.

## Report surfaces and guarantees

**PBIP/TMDL:** source-neutral shared schema, declared relationships and Date table, explicit DAX measure definitions, model revision/schema compatibility, source parameters and RLS designed against *real* permission domains. **PBIR:** role-specific executive, secretary, chair, outcome, assurance and cross-forum pages, accessible drillthrough, as-of, nonzero missingness and data-quality signals. **RDL:** reusable forum/period/as-of parameters, controlled meeting/decision/action/outcome/exception and provenance appendix, precise edition and issue status, pagination/print/readability tests; *not* automatic publication of draft minutes.

**Cross-output parity:** every required KPI validated from the same fictional source snapshot at identical as-of, filter and audience. RDL must not quietly override missing-data logic, grouping or dates. Reporting must preserve source-level access restrictions; no unsafe broad import or export; special care for small cells and restricted minutes.

## Evidence and release

Track source contracts, typed adapters, reproducible fixtures, PBIP/TMDL, PBIR, RDL, schema/metric crosswalk, DAX/Power BI tests, render/accessibility, RLS/exfiltration, exact native refresh/readback and controlled deployment separately. No artifact is "done" merely because a Conductor plan, local script or YAML exists. Explicit statuses: planned → source implemented → offline validated → native packed → native deployed/qualified → operationally accepted → benefit evaluated.

## Related authorities

- [Legacy Decisions Dataverse dashboard specification](dataverse-dashboards.yaml) is retained and NOT a proof of Power BI implementation.
- [Legacy reporting architecture](../../../docs/architecture/governance-reporting.md) and [ADR 0006](../../../docs/adr/0006-power-bi-deferred-until-stable-data.md) remain historical controlling statements for the original Dataverse MVP.
- [New Conductor reporting track](../../../../../conductor/tracks/decisions_clinical_hub_reporting_20261111/index.md), linked with RMS PR #312 and standard-core PR #304 (both unmerged at creation).
