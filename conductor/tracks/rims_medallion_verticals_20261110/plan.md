# RIMS medallion, verticals and 36-flow contract programme

Status: SOURCE-ONLY IMPLEMENTATION PARTIAL. Added 10 JSON Schema 2020-12 contracts in `portfolio/rims/contracts/`. Generated local deliverables for 36 exported flows are available separately; **the generated 239-file package is not yet imported into GitHub**. No tenant readback, source/runtime parity or deployment is implied.

Owner: existing RIMS Conductor/source maintainer. Do not create parallel source writers or repeat accepted source/native acquisitions. Input is the user-supplied unmanaged `CHHHSRIMSPlatform_1_0_0_0 (6).zip` (36 flows; hash and paths in earlier source reconciliation). Keep source ZIP and any tenant-specific bindings out of Git.

## Architectural contract

Four levels must separately pass:
- **Bronze** (lossless source): full rights-permitted raw payload and original schema, provider ID, pagination, status, source version, licence/privacy class, timestamp and cryptographic capture identity. No unexplained field drops, even for nested arrays; omissions documented with a reason.
- **Silver** (normalised): typed source-qualified identities, entity and relationship tables, full field lineage, timestamps, reversible dedup/links, uncertainty and original Bronze pointer. Assertions not equivalent to human attribution or employment approval.
- **Gold** (verified business product): stable grain/period, reconciliation denominators, approved/held populations, display-friendly typed dimensions, measures, last-good source revisions, validated access and signed-off business meaning. Non-premium HTML/CSV/SharePoint Views fallback must work without Power BI.
- **Platinum** (intelligence): evidence-led graph, matching, trends, research pipeline and risk/opportunity signals; uncertainty/limitations, decision ownership, human sign-off, method version and Gold provenance. No Copilot/premium connector as a core prerequisite.

Six vertical contract families (each with Bronze/Silver/Gold/Platinum outputs): `publications`, `people`, `organisations`, `projects_studies`, `funding`, `shared`. Each must cover **ingest -> analyse -> surface -> intelligence**. Reuse immutable source snapshots and existing registered infrastructure.

## Source-first execution phases (each task with exact exit)

### Phase A — Source baseline and 36-flow catalogue
- [ ] **RM-C01**: Verify ZIP SHA, all 36 workflow filenames, IDs, triggers, source/component hashes and top-level vs nested actions. Exit: input manifest with zero unclassified or skipped flows; don't commit private connection values.
- [ ] **RM-C02**: For each flow, generate individual source-aware dictionary, ten atomic tasks, MoSCoW, architecture/design, Mermaid and BPMN2 XML. Exit: exactly six named design files per flow, 216 files plus contracts; validate XML, JSON, link references, flow uniqueness. A static sequential BPMN abstraction must be marked *not runtime graph parity*.
- [ ] **RM-C03**: Review source action branches, error handling, retries and pagination; improve control-flow BPMN from sequence-only to true gateways/loops from source graph. Exit: reviewed input/output/outcome fixtures per flow and a provenance-bound graph.
- [ ] **RM-C04**: Reconcile archived RIMS source and research-publications code; record which generated files should be admitted to CareOps and their source provenance. Exit: no duplicate record source or discarded accepted work.

### Phase B — Medallion and domain contracts
- [x] **RM-C05**: Introduce Bronze/Silver/Gold/Platinum JSON Schema contracts with required common provenance, entity identity and review boundaries. Exit: 4 committed contract definitions; local schema validation completed, hosted CI pending.
- [x] **RM-C06**: Define Publications, People, Organisations, Projects & Studies, Funding, Shared contracts. Exit: 6 committed schema definitions; source-to-domain field mappings not yet fully populated.
- [ ] **RM-C07**: Generate typed fixtures for each medallion/domain pair (24 pairs), including 0/1/many, null, nested arrays, absent source, partial/duplicate page, stale, incompatible schema, denied rights and audit ref. Exit: each pair has fixture and negative tests.
- [ ] **RM-C08**: Produce migration gates Bronze -> Silver -> Gold -> Platinum; refusal for unknown source, absent lineage, unqualified employee/publication decisions or missing denominator. Exit: deterministic source-only promotion tests and reversible input identities.
- [ ] **RM-C09**: Source field maximisation: list raw fields, all projected fields, nested cardinality, retained-only, intentionally excluded, and unknown; measure separately at each layer and consumer. Exit: zero unexplained source field loss per licensed capture; no fabricated 100% figures.

### Phase C — Per-flow engineering
- [ ] **RM-C10**: For each of the 36 flows execute local flow-task register `10` operations: source hash; actions/connectors; dictionary; Bronze; Silver; Gold; Platinum; Power BI/UI mapping; synthetic tests; release/native gating.
- [ ] **RM-C11**: Classify connectors against no-premium core allowlist; keep premium/Copilot as optional not dependencies. Exit: every action has licence classification and a standard or offline route.
- [ ] **RM-C12**: Identify source coding or `field_N` projections, join keys and value labels; add display dictionary with nullable/type/enum constraints. Exit: all observed columns matched to approved display labels or flagged unknown, never guessed.

### Phase D — Power BI / semantic model / scorecard / paginated report
- [ ] **RM-C13**: Read exact current PBIP/TMDL semantic model, report JSON and visual references; inventory lineage tags, sourceColumn, DAX, field parameters, RLS, relationships, pages, filters and bookmarks. Exit: complete baseline dependency graph with hashes and candidate model diff.
- [ ] **RM-C14**: Build non-destructive rename/alias candidate. Keep SharePoint internal `field_N` and preserve model sourceColumn initially; add descriptive label and decode known values. Exit: no orphaned DAX/visual references in source-level checks.
- [ ] **RM-C15**: Implement and verify all affected semantic tables and report visuals against actual model source, then separately scorecard metric/dataset bindings and RDL datasets/parameters. Exit: CI render/contract tests and **native** readback for each artifact; no file from the uploaded solution alone proves these edits.
- [ ] **RM-C16**: Compare report rows, measures and source data across known valid reporting periods and expected reconciliations. Exit: dashboards, report exports, subscriptions, paginated and scorecard visuals all retain compatible historic results and meaningful values.

### Phase E — SharePoint List recreation and recovery
- [ ] **RM-C17**: Read-only inventory existing List GUIDs, internal column names, indexes, uniqueness, views, permissions, retention and versioning; derive mapping to proposed templates. Exit: no duplicate canonical authority.
- [ ] **RM-C18**: Generate schema JSON, blank CSV import headings and optional PnP PowerShell template. Exit: safe dry-run by default; typed fields, choice values, lookup relationships, indexes, views, role constraints and preimage/rollback must be reviewed before actual create.
- [ ] **RM-C19**: Qualify PnP tenant authentication, allowed app/permission scopes, site owner, existing-list reuse and command availability. Exit: operator-authorised controlled dry-run and inverse; no premium service required.
- [ ] **RM-C20**: Execute separately approved native create/patch only for missing/approved changes; verify readback and recovery. Not authorised by source contracts.

### Phase F — vertical intelligence and delayed sources
- [ ] **RM-C21**: Connect existing Publications, People, Organisations, Projects, Funding data products by reviewed entity/link contracts. Exit: source-backed inter-vertical lineage and no inferred employment.
- [ ] **RM-C22**: Implement Gold metrics and Platinum research intelligence using currently acquired data: portfolio gaps, contributor networks, grant-to-output conversion, studies/output delay, correction/OA and source quality. Exit: evidence, denominators and uncertainty; no premium dependency.
- [ ] **RM-C23**: Defer new collectors including NLA Trove until existing source-field utilisation and quality thresholds are explicitly met. Roadmap only: Trove, institutional repositories, OpenAIRE, ORCID API, OpenCitations, Dimensions/Scopus where licence separately justified. Do not add credentials or active jobs.
- [ ] **RM-C24**: Enforce release/security: source-only CI green, protected merge, no tenant/source secret leakage, native permissions and monthly scheduled delivery accepted separately. Exit: reproducible main SHA and formal scope-specific receipts.

## Required local-agent task contract
For every `RM-Cxx` and every flow:
1. Read exact source input, SHA and previous evidence.
2. Change one bounded output file or compatible code unit; no unrelated pin, CI, scheduling or permission mutation.
3. Execute the named cheapest test, then full milestone guards if the specific files require them.
4. Store receipt: input SHA, command, exit code, output SHA, test counts, unresolved cases, acceptance level (source/native/business).
5. On any failed assertion: stop; preserve original, record observed failure and inverse; do not substitute a different source or bypass a gate.
6. Update only the owning task checkbox on successful acceptance and hand off to one next task.

## Acceptance and non-goals
- No tenant/Power Platform access required for source schema, flow-doc, dictionary, synthetic test, model-code review or List import-template preparation.
- No claim that every raw provider field belongs in a report; every legal/available field is either retained or explicitly omitted with rationale.
- No native Power BI or SharePoint artifacts, authenticated Microsoft Graph person records, or live workflow states modified by this plan.
- Continue RIM-01–21 in the [existing RIMS reconciliation](../suite_rims_migration_20261018/export-reconciliation-20261110.md); do not fork an incompatible review ledger.
