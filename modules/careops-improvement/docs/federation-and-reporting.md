# Federation and portfolio reporting

## Day-one working surfaces

The design includes a SharePoint initiative register, governance-decision list,
event/observation list and evidence library, with Teams as the access-oriented
entry point. A portfolio Planner plan can hold linked delivery tasks. A workbook
may provide named tables for a bounded analyst workflow or portable export. The
resource contracts are in `config/resources.json`.

Every task, workbook row, evidence document and event carries `InitiativeId` or
a documented source key. SharePoint list item IDs, Planner task IDs, file paths
and row numbers are not cross-system business keys. The integration ledger
records source key, source revision, extraction time, import result, last
successful import and unresolved conflicts. Reconcile by stable keys and expose
ambiguous/missing mappings for human resolution. Never silently delete or
overwrite a human-edited file, issued document or task. Teams membership, list
permissions, library permissions, Planner access and report audiences are
separate access decisions; membership in one surface does not prove access to
another.

The evidence library records document kind, source record and revision refs,
template version, included record IDs, generated output revision and human
document state. If a structured document route is later selected, generation
uses maintained templates and authoritative inputs. It must preserve edits,
unresolved content and issued history, and verify actual output and recovery.
Generation is not substantive review, approval or permission to circulate.

Workbook tables have stable table names and keys, typed columns, source/revision
columns and an explicit refresh receipt. Display labels are not keys. The
workbook is an analysis/export surface; formulas or manual edits there do not
replace source system decisions or finance records. If a feed fails, expose its
last successful import and staleness, not a misleading current/zero result.

## Cross-module links

| Domain | Stable reference | What remains authoritative there |
| --- | --- | --- |
| PPG | Policy catalogue identifier plus exact edition/revision | Policy text, source provenance, review state and applicability |
| Research publications (RIMS) | RIMS record identifier and source revision | Bibliographic metadata, publication state and research publication workflow |
| Decisions | Decision record identifier and owner reference | Delegated decision, approval state, conditions and decision evidence |
| Process | Source-qualified case/event ID and source revision | Process state and the source system's event history |
| Costs | Finance record/reference, period, currency, category and allocation basis | Posted actuals and approved financial definitions |

These are reference contracts, not implied live integrations. Cross-module
adapters are optional and must read only authorized fields, preserve source
ownership, and record failures/reconciliation. Do not copy sensitive case
content into the portfolio to make a link convenient. Cost measures distinguish
actual, committed, forecast and estimated amounts and identify the currency and
period; unknown allocation remains unknown rather than zero.

## Reporting model

Use a star schema with these declared grains:

* `FactInitiativeSnapshot`: one initiative at one agreed snapshot date and
  source revision. Dimensions: initiative, service, route, status, lead
  (pseudonymous reporting key where needed), and date.
* `FactInitiativeEvent`: one source event/transition. Dimensions: initiative,
  event type, source system, service, route, and effective and observed dates.
* `FactMeasureObservation`: one initiative, measure, observation period,
  definition version and evidence/source revision. Dimensions: measure,
  initiative, service, route, and date.
* `FactCostObservation`: one initiative/source reference, cost category,
  period, currency and allocation basis. Keep estimated, forecast, committed
  and actual amounts as distinct additive categories; do not sum mixed
  currencies without a documented conversion snapshot.
* `FactAdoption`: one defined adoption observation for an initiative, cohort,
  and period. Its denominator, eligibility and observation method are versioned.

Use conformed dimensions for service, date, route, status, measure and source.
Retain unknown/unmatched dimension members and source freshness. Effective time
is when the event occurred according to its source; observed time is when the
portfolio captured it. Preserve both to quantify reporting delay and late
arrivals. Corrections are append-only observations or versioned snapshots,
not silent edits to history.

### Measures and outputs

The scorecard should include: active initiatives (distinct stable IDs in the
selected snapshot), stage mix, decision turnaround (effective submission to
decision time with explicit exclusions), benefit-measure coverage (initiatives
with a defined baseline and target / eligible initiatives), outcome attainment
(only observed outcomes against a versioned target), adoption rate (adopted
eligible units / eligible units), source freshness, and cost by status/currency
and period. Publish numerators, denominators, definition version, as-of date and
unknown count alongside each rate. Count an adoption snapshot only when its
source explicitly records adoption (for example, `status: adopted` or a positive
`adopted_count`); a service reference alone does not establish adoption. Do not
report an unobserved outcome as zero.
Do not interpret correlation or before/after change as causal impact without an
appropriate evaluation design.

The interactive scorecard supports filtering and drill-through to authorized
source references. A paginated pack is a parameterized, reproducible snapshot
for a selected period, service and route; it includes definition version,
freshness and unknown/late counts. Report access is independently configured
and verified. Export, refresh acceptance and a visible report alone do not prove
successful refresh or correct reconciliation.

## Process event fields

For process analysis, the importer event shape requires `event_id`, `source_key`,
`initiative_id`, `event_type`, and at least one of `effective_at` or
`observed_at`. Use ISO 8601 timestamps with explicit UTC `Z` or offset. Preserve
both timestamps whenever available. The analytical projection may name its
normalized time columns `effective_at_utc` and `observed_at_utc`; this mapping
is deliberate and does not alter the packet fields. Optional event payload
fields can include source-qualified `case_id`, `source_system`,
`source_record_id`, `source_revision`, `activity`, `event_status`, `actor_ref`,
`service_ref`, `decision_ref`, `outcome`, `evidence_ref`, and
`supersedes_event_id`. Distinguish actual source transitions from derived
milestones and manual annotations. Retain original zone/offset in source
evidence when available. Process mining outputs describe observed paths and
timing; they do not make clinical, governance or performance determinations.
