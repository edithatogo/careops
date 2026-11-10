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
