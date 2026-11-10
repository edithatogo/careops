# RIMS maximal use of existing data — Conductor implementation plan

**In progress.** This is a bounded source-to-consumer utilisation workstream under existing RIMS medallion/vertical, publication-source, Power BI and native-flow owners. It does not create an acquisition service or change accepted original records.

See [spec](spec.md), [MoSCoW](requirements.md), [design](design.md), [source register](../../../portfolio/rims/existing-source-adoption.json) and [136 executable per-source tasks](source-tasks.json). Use the original historical `research-publications` handoff and actual accepted private snapshots before any source use claims.

## Phase A — Source inventory and profiling (P0)
- [x] **MX-A01 source code**: create bounded recursive field profiler with array-path normalisation, row presence, null/empty/occurrence and observed-type counts. Output no raw values.
- [x] **MX-A02 source code**: define strict profile and field-utilisation JSON Schemas. These are source contracts, not current native acceptance.
- [x] **MX-A03 source code**: register existing 17 source routes and historically accepted scope with explicit uncertainty, no new source.
- [ ] **MX-A04 private data**: verify each original retained capture/receipt and schema against currently accepted version, rights and source completeness.
- [ ] **MX-A05 private data**: execute profiler over complete approved provider rows for every source; compare to retained Field tables and archive chunks, including all nested fields.

## Phase B — Maximal permitted data use (P0–P1)
- [x] **MX-B01 source code**: require each observed source path to be mapped to a real revisioned consumer, retained-only with reason, excluded with rights/security reason, or explicitly unassessed.
- [x] **MX-B02 source code**: provide per-source and per-domain coverage scorecard, separating mapped / retained / excluded / unassessed; no claims of native parity or full provider capture.
- [ ] **MX-B03**: resolve unassessed fields by applying the 136 source-specific tasks. Prioritise high-utility structured entities and relationships, not indiscriminate flattening.
- [ ] **MX-B04**: implement typed versioned Silver/Gold consumers for nested authors, affiliations, funders, study outcomes/interventions/sites, ROR organisations, award details and related DOIs, retaining source assertions.
- [ ] **MX-B05**: design safe local NLP/topic/collaboration/citation graph and grant matching from permitted retained text/relationships; compare against simple baseline. No Copilot or premium connector requirement.

## Phase C — Native semantic and business validation (P1)
- [ ] **MX-C01**: verify exact source->Silver->Gold->model->visual/metric/scorecard/RDL lineage in the qualified Power BI tenant. Do not rewrite already accepted T18 23-indicator products.
- [ ] **MX-C02**: implement meaningful display names, material measures, missingness/cohort denominators and historical time windows; verify old/new keyset and measure parity.
- [ ] **MX-C03**: only with approved links, generate domain products for researchers, teams, CHHHS, Queensland, funders and community; apply access/small-cell suppression.
- [ ] **MX-C04**: benchmark existing Import/SharePoint vs versioned JSON, optional SQLite/Parquet offline caching. Select no-premium default and benchmark rather than assume.
- [ ] **MX-C05**: obtain actual permitted user/organisation/funding source rights and platform readback before enabling any more field exposures.

## Phase D — Conductor-review and protected release
- [ ] **MX-D01**: run source tests on exact repo Python 3.15.1 and all existing security/privacy/harness checks. Reviewer audits empty/large inputs, source-leakage, denominator and type semantics.
- [ ] **MX-D02**: reconcile with original source owners, 17 provider-specific task states, T18 native receipts, RMD-05 and six medallion verticals. Do not mark partial source contracts complete.
- [ ] **MX-D03**: pass protected PR checks and merge normally; then separately qualify native deployment and report access.

## Executable single-source loop for a smaller local agent
For each `MX-Sxx-01..08` from [source-tasks.json](source-tasks.json), read the specific source's retained receipt and current owner; do **one** bounded action, run the listed cheap test, record inputs/outputs/exit, update only that task status when supported and never infer missing source data. Do not skip from a synthetic test directly to native acceptance.

## Release boundaries
The source-only code and diagrams do not prove all 17 providers' currently retained field sets, their full native consumption or any health/economic impact. Core remains free of premium/Copilot; HTTP collectors in old exported flows require native licensing classification and separate optional admission. New Trove/other providers remain deferred until existing-source utilisation and data rights have been fully assessed.

## Source review findings so far
- Partial historical 1,344 canonical publications, 1,277 retained PubMed full metadata, accepted Europe PMC/OpenAlex/Semantic Scholar source chunks, and 23-indicator T18 semantic outputs exist already. Prioritise adapting those exact saved data products rather than a new generic API.
- Field-level presence, source schema coverage and consumer use must be reported separately; a high field-preservation rate is **not** a high analytic-usage rate.
- Current source profile and scorecard cannot prove licence/tenant permissions, raw byte integrity or live visual binding; native verification remains mandatory.

## Source implementation and review checkpoint — 10 November 2026

### Implemented source-only components
- `rims_retained_field_utilisation.py` profiles every **observed** nested JSON field path (including repeated-array occurrence counts), missing/null/empty/type distributions and full optional declared paths. It separates field capture from *consumer use* and requires explicit consumer artifact/revision and rights/exclusion reasons. No raw values are included in public profile output.
- `rims_coverage_rollup.py` aggregates field-use counts over the 17 registered existing sources, demanding an exact source-qualified profile identity. Domain/source percentages represent **declared mappings**, never native-verified utilisation.
- `rims_export_field_usage.py` indexes physical `field_N` codes in all exported workflow action inputs without printing URLs or values. The user-supplied ZIP yields **36 flows and 20 distinct SharePoint physical codes**; this is not provider-field completeness.
- `rims_pubmed_xml_field_profile.py` preserves semantic PubMed XML `Name/Namespace/Value/Attributes` element/attribute paths, repeated sibling counts, empty values and missingness. The private, lossless ordered occurrence projection makes **all** retained XML fields accessible to typed Silver consumers without losing original record order, free text or attributes. It does not publish any source text.
- `rims_retained_pubmed_adapter.py` now supports the historical accepted PubMed **XML list root** rather than requiring a flat object, retaining it unmodified in Bronze and explicitly as `xml_nodes` in Silver pending reviewed field-specific semantics. An independent retained byte/receipt verifier is required.
- Strict public field profile/utilisation JSON Schema and separate **private occurrence** contract added; synthetic regression tests cover source root, multiple authors, grants, attributes, namespaces, scope and tampering.
- Existing 17-source adoption registry and 136 atomic per-source tasks retained, including source-specific PubMed XML mapping requirements. No Trove/new-source ingestion.

### Review and findings
**High, fixed in source:** Initial retained PubMed adapter assumed `metadata` was an object. Original accepted `Xml.Document` metadata is a list of named nodes, so the adapter could have rejected actual retained source. The corrected adapter now retains the raw list unchanged and does not substitute an invented flat publication object.

**High, fixed in source:** Generic nested JSON paths would collapse PubMed semantics into repeated `Value[]` fields, obscuring grants, MeSH, abstract, author affiliations and correction structures. The XML path-aware profiler and private ordered occurrence layer restore distinct semantic paths without leaking contents publicly.

**Medium, fixed in source:** Avoid duplicate entire-record JSON encoding in the profiler; enforce bounded depth/field counts and nonfinite numeric refusal. Ensure empty source cannot imply fully utilised data and prevent mismatched provider identities in the rollup.

**Still open:** Exact 1,277 retained PubMed records and other 16 source archives must be run through these adapters in their approved private environment with original accepted SHA/rights. The existing T18 model, source evidence tables and 23 indicators need actual field-level readback before a metric can be labelled *utilised*. Neither real outcomes nor provider-schema-wide acquisition is verified.

### Acceptance
Source tests are committed but **not yet qualified on the exact GitHub branch HEAD and canonical Python 3.15.1**. Locally, the sanitised ZIP physical-column script generated an aggregate 36-flow / 20-code inventory. This does not qualify Power BI semantics or native Power Platform.

## Prioritised existing-data exploitation — 11 November 2026

The first priority is **use what has already been acquired and accepted**, not add new collectors, duplicate native writers, or maximise column counts in a single dashboard.

### Immediate source products and measurable contracts

| ID | Priority | Source already acquired | Product to develop from permitted retained fields | Proof before claiming done |
| --- | --- | --- | --- | --- |
| MX-U01 | P0 | PubMed full XML and author evidence | Publications, contributor/affiliation entities, MeSH, intervention/population topics, grants, correction links, publication dates | All retained XML semantic paths preserved; author index, PMID/DOI links and review status verified |
| MX-U02 | P0 | OpenAlex + Europe PMC + Semantic Scholar | Source-qualified OA, field-of-research topics, authors, institution, works/references, source disagreement and missingness | Per-source estimates never summed; all 1,344 accepted keys represented as matched/missing/deferred |
| MX-U03 | P0 | Crossref, OpenCitations, DataCite | Citation/provenance graph, update/correction notices, dataset/software DOIs, licence and funder links | Retained relationships by source/revision; no inferred correction or duplicate citation total |
| MX-U04 | P0 | DoRA + ClinicalTrials.gov | Studies, outcomes, sites, enrolment, interventions, study publication/reporting gap and lifecycle | Proven study identity, date semantics, completion/censoring and reviewed organisation association |
| MX-U05 | P0 | ARC, NHMRC, MRFF, QGIP, GrantConnect | Award and opportunity intelligence, scope/eligibility, linkage to named studies/outputs | Award vs opportunity vs PubMed grant acknowledgement differentiated; no candidate grants promoted |
| MX-U06 | P0 | ROR and ARDC | Organisations, aliases, hierarchies and facility/research networks | ROR/source-qualified IDs, temporal relationships, no employment inference |
| MX-U07 | P1 | RIMS People and accepted author/organisation data | Person timeline, author mentions, affiliation interval and collaboration graph | Human-reviewed identity/HR status separately, restricted access, no public staff records |
| MX-U08 | P1 | T18 accepted 23-indicator model/report/scorecard/RDL | Source coverage and missingness dashboard, stakeholder outcome views and native report parity | Actual saved model 1,344-key baseline; 36/53 assessed OA distinct from 53/1,344 coverage; no rewrite of accepted 23 indicators |
| MX-U09 | P1 | Complete source archives and flow run receipts | Freshness/reliability, missing data, provenance, duplicate/suppressed counts, source→consumer lineage | Published metadata-only snapshots and verified source/consumer revisions |
| MX-U10 | P2 | All accepted cross-domain relationships | Network and portfolio intelligence, grant→study→output, research capability and translation | Independently reviewed edges, denominators, temporal exposure, uncertainty and noncausal interpretation |

### Executable local-agent micro-loop

For **each of the 17 catalogued sources**, execute existing `MX-Sxx-01..08` tasks in order, and then:
1. Load the source's **accepted private** original capture and hash/rights receipt; no newly acquired data.
2. Use existing `rims_retained_field_utilisation.profile` (for PubMed XML, use the XML-specific profile) to enumerate all source paths with types, missing/null/empty and occurrence counts.
3. Use `rims_retained_field_utilisation.utilisation` to record actual model/field/visual consumer identities and revisions; do not count a proposed mapping as native verified.
4. Call `rims_utilisation_opportunities.plan` on the 17-source catalogue and available profile/utilisation reports. It must emit a distinct task for **every unassessed field** and keep unprofiled providers visible. Task order prioritises populated observed fields; it is a heuristic, not proof of value or access rights.
5. For each candidate, choose the existing typed medallion vertical, find an appropriate analysis/view/decision use, and document why it is useful and permitted. For irrelevant or restricted source paths, retain-only or rights-exclude with justification.
6. Add a reviewed mapping in the existing lineage ledger with exact source path, target field, producer and consumer revision; recompute profile and task queue. Avoid automatically inferring employee status, CHHHS publication inclusion, funder award or clinical impact.
7. Update a source/domain scorecard showing **three separate measures**: paths observed, paths accounted for and paths actually verified as consumed; do not report 100% use from data retention or a static mapping.
8. Run source tests; then separately qualify real Power BI semantic model, dashboard, scorecard and RDL source-to-consumer parity before marking native use accepted.

### Deferred sources

No Trove, additional API collectors, premium-only Fabric acquisition, Copilot or new directory scraping until the 17 retained sources have a verified inventory, all field paths have a declared disposition and high-value Gold/Platinum outcomes are evaluated against actual authorised data.

### Current partial implementation and blockers

- New `portfolio-scripts/rims_utilisation_opportunities.py` and corresponding synthetic tests generate a metadata-only prioritised queue. They do not read the private archives and do not prove present-day source completeness or Power BI use.
- Existing `rims_retained_field_utilisation.py`, `rims_coverage_rollup.py`, `rims_pubmed_xml_field_profile.py`, typed medallion contracts and T18 native evidence remain authoritative for their accepted bounded scope.
- The existing 136 source-specific Conductor tasks remain open until their precise acceptance condition is met. Reuse the original native 23-indicator source/report and maintained source owners; do not rebuild.
- Local focused tests for the prioritiser passed on Python 3.13.5; canonical 3.15.1/hosted checks and real data/tenant acceptance remain unverified.

### Private-runner execution contract

The prioritiser has a local entry point to make the existing 17-source coverage work actionable without new acquisition. A private owner prepares a `careops-rims.utilisation-batch/1` JSON envelope containing `reports` (each report has `source`, `profile` and `utilisation` from the already accepted profilers). Run only from a suitable private directory:

```sh
python portfolio-scripts/rims_utilisation_opportunities.py \
  PRIVATE/catalogue.json PRIVATE/profiles.json PRIVATE/opportunities.json \
  --catalogue-sha256 PINNED_CATALOGUE_SHA256 \
  --reports-sha256 PINNED_REPORTS_SHA256
```

The script rejects input SHA mismatches, duplicate or orphan source profiles, impossible counts, unknown type labels and unassessed paths absent from the source profile. Its report is exclusive-create, contains no raw field values and is **not suitable for public release without schema/field-path privacy review**. Standard output includes counts and a SHA only. Local negative/positive tests: eight pass on Python 3.13.5; canonical 3.15.1 and exact-head hosted CI remain unverified.

For every output opportunity, preserve its `MX-UTIL-nnnn` task identifier and link it to the existing specific `MX-Sxx-04` (field classification), `-05` (Silver mapping) and `-06` (native consumer) tasks. Do not mark any task complete when the plan merely proposes a consumer. Review the usefulness, missingness, rights, source version, temporal grain and actual business need before mapping. Keep original source-array structures and preserve record-specific evidence. A new field mapping should have a corresponding model, dashboard/scorecard/paginated or approved non-premium consumer, as appropriate; displaying every field in every report is not the goal.

**Important:** `declared_mapping_fraction` is descriptive of declared mappings. `analytical_utilisation_fraction` remains null and `native_usage_verified` false until actual downstream source/model/report readback. The static `all_source_data_utilised` flag remains false. No additional source collector, scheduled flow, premium connector or Copilot prerequisite has been added.
