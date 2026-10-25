# careops-finance implementation plan

Status: optional public source composition complete; optional reporting interfaces remain open. Priority position: 3.
Native reporting, private-source recovery and operational interfaces retain their
separate qualification requirements.

## Phase 1: Selection and boundary

- [x] FINANCE1.1 Refresh exact default head/checks with the existing owner; record a stable selected commit and preserve in-flight work.
- [x] FINANCE1.2 Review private source, history and data-source bindings. Diagnose current selected-commit CI before promotion; do not infer that a failed run proves a source defect.
- [x] FINANCE1.3 Inspect licence/attribution, source/history/privacy and deployment dependencies. Record concrete gaps without inferring public safety from visibility or scanner success alone.
- [x] FINANCE1.4 Checkpoint: record selected standalone slice, exact inputs, ownership and source-only stop conditions here.

## Phase 2: Parent composition and standalone proof

- [x] FINANCE2.1 After review, add an optional exact source gitlink at modules/careops-finance, canonical URL and compatibility/catalog reference; update PUBLIC_SOURCE_FILES.json together.
- [x] FINANCE2.2 Verify clean parent clone without optional modules and selective child initialization; retain child licence and actual private-access boundaries.
- [x] FINANCE2.3 Run existing focused source/fixture checks and parent publication/portfolio checks; record exact revision, commands and actual results. Do not claim native operation.
- [x] FINANCE2.4 Checkpoint: retain preimage parent SHA, source provenance and supported commands; preserve a failed/missing check rather than marking qualification complete.

## Phase 3: Interoperability and recovery

- [ ] FINANCE3.1 Synthetic source-to-measure reconciliation, period identity, parameterised bindings, model/report dependencies and one reproducible report slice; no ledger-authority transfer.
- [ ] FINANCE3.2 Test only selected optional interfaces with provider absent, incompatible version, stale/missing inputs and duplicate retry; preserve authoritative ownership and human edits.
- [x] FINANCE3.3 Rehearse reverting only the source pin/catalog/CI change in a disposable clone. Native objects/data are not deleted or rolled back by a source-reference reversal.
- [ ] FINANCE3.4 Checkpoint: close only proved source scope; send one consolidated deliverable or genuine blocker to the existing owner, without acknowledgement polling or a new chat.


## Public CI route — 20 October 2026

The user selected public delivery to remove private Actions billing and signing
constraints. Clean source is published at `edithatogo/careops-finance-public`.
The original remains private because retained history includes live infrastructure
or deployment context; no private issues/history were copied. Qualify the public
source and actual artifacts independently before source composition. Native
objects, in-flight operations and existing private writers are unchanged.

## Selected public source composition — 24 October 2026

Use the already-reviewed clean public successor, Finance PR12 at
`e09b628499ec625ade841c7fc4b21cb5f8f77e6a`, rather than importing private
history. All four exact-main workflows passed, including actual report source
packaging and attestation. Reuse the retained source/artifact qualification; the
child source, MIT licence, bindings and model/report contracts are unchanged.

- [x] Verify the completed exact public source and independent licence boundary.
- [x] Compose the existing qualified pin at modules/careops-finance with updates
  disabled by default; keep catalog, inventory and actual gitlink consistent.
- [x] Exercise the actual portfolio gate against a valid disposable index and
  independently changed Finance/Process gitlinks; reject stale qualification.
- [x] Verify a clean parent without optional modules, selective exact Finance
  initialization and source-only reversal in a disposable clone.
- [x] Qualify current-head checks, merge and verify main. No data source is bound,
  no ledger authority moves and no native/report acceptance follows.

### Source composition closeout — 25 October 2026

The parent preimage is `d673399e2c22580fa50d9b4f6e4ef9058d9bb5f4`.
PR132 merged as `ffa40cad40ecdde77798f5d631c9e7a2200ade05`.
The selected clean public source `92f8ae4fc36aadcf9cf1e2cffd5fe44e9edc8271`
agrees across the gitlink, public inventory, catalog and ALM/CI records.
The earlier clean-parent, selective-checkout and source-reversal receipt
applies unchanged. GitHub readback found PR132 merged, 12 successful main
checks and two conditional skips; its PR head had 13 successes and one
conditional skip. The current parent main retained passing portfolio and
public-source checks. This closes the selected source reference; Phase 3's
reporting interface and reproducible report slice remain open.

### Reporting interface evidence review — 25 October 2026

Revalidated the selected public source at
`92f8ae4fc36aadcf9cf1e2cffd5fe44e9edc8271` in a clean disposable clone. The
existing static checks pass:

- `pwsh -NoProfile -File tests/pbir/Test-PbirReportStructure.ps1` — VMO Finance
  and Medical Staff report structure passed.
- `pwsh -NoProfile -File tests/tmdl/Test-LiveExportTmdl.ps1` — required TMDL
  tables and catalogue measures passed.

These checks prove package structure and required table/measure presence. They
do not execute the Power Query, model relationships, DAX measures, or render a
report slice. Inspection of the checked source found the following specific
gaps against FINANCE3.1:

- The bundled VMO GL sample has Jul/Aug/Sep amounts of 41,000, 37,000, and
  29,000. The VMO sample has 42,000, 36,500, and 28,500, but stores only the
  financial year, so equal annual totals (107,000 each) do not prove period
  identity or period-by-period reconciliation.
- The PBIR dataset model declares tables but no relationships. Its embedded
  sample TMDL partitions are not a report execution receipt and are separate
  from the parameterised SQL M templates under `m/sql`.
- The static report tests do not reconcile fixture rows to rendered measure
  values or verify report interactions after filtering by financial year and
  period.

At this evidence review FINANCE3.1 and FINANCE3.2 remained open. No ledger
authority or native data binding was inferred from those source artifacts.

### Synthetic period slice source qualification — 25 October 2026

Finance public PR14 (`f55228be33de07dc3e891cc788aa2484b1e40561`) merged as
`433d76943190be092c217f368fd5ccc56a211716`. Its exact-head SourceControlReady,
RepositoryHygiene, package, CodeQL, shared security, coverage, workflow lint,
secret scan and evidence-hardening checks passed. All four actual merged-main
workflows passed: validate `40158541202`, package `40158540979`, CodeQL
`40158540997`, and evidence-hardening `40158541011`.

The source now includes a synthetic period-keyed fixture, a reproducible
source-to-measure JSON slice and focused regression cases for calendar mapping,
monthly and annual totals, absent/incompatible providers, stale/missing/unmapped
inputs, identical retry idempotence and duplicate-content conflict. The parent
candidate advances the gitlink, public inventory, repository catalog, CI
qualification and ALM source pin together to `433d76943190be092c217f368fd5ccc56a211716`.

This closes the fixture/report-calculation source segment only. It does not add
real data, change the production Access/SQL schema, establish semantic-model
relationships, execute the Power BI engine, or render PBIR visuals. FINANCE3.1
remains partial pending a qualified model/report slice; FINANCE3.2 remains open
pending an actual optional provider interface selection and binding. The local
Finance SourceControlReady run on macOS stopped at its existing Windows Registry
DSN probe; hosted Windows SourceControlReady passed on PR14 and merged main.

### Parent pin and current-main readback — 25 October 2026

The Finance source slice `433d76943190be092c217f368fd5ccc56a211716` is
composed at the parent gitlink and source inventory. CareOps PR154 merged as
`8e3fc1dfd567416fb6aeca851cd99fd1a12a8159`; all nine recorded exact merged-main
workflows passed, including portfolio, public-source and cross-module
compatibility checks (runs `40158941891`, `40158941892`, `40158941913`,
`40158941899`, `40158941932`, `40158941911`, `40158941914`, `40158941943`,
`40158941956`). This verifies parent source composition only. The rendered
period-by-period report slice, model relationships, runtime and external
provider binding remain open under FINANCE3.1/3.2.
