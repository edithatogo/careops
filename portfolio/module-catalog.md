# CareOps module catalog

## Current source map — 6 November 2026

This catalog describes capabilities and source locations; it does not grant tenant access or establish operational acceptance. Read `repos.json` for source materialisation, the selected commit's Git tree and `.gitmodules` for actual gitlinks, and each module's track for its qualification evidence.

There are three distinct states: **integrated source** included in the parent checkout; **optional pinned submodule** initialised only when needed; and **catalogued proposal** with no implied implementation. Consolidation of source does not create a shared operational database, combined service identity or mandatory module dependency.

| Module | Current or intended path | Role | Current state |
| --- | --- | --- | --- |
| [Innovation and Improvement Register](../modules/careops-improvement/README.md) | `modules/careops-improvement/` | Federated improvement portfolio | Integrated module planning and offline implementation; native deployment unqualified |
| `careops-approve` | `careops-approve/` | Intake, validation, routing and human approval capture | Integrated source; CareOps is canonical |
| `careops-decisions` | `modules/careops-decisions/` | Committee and formal decision governance | Integrated source; CareOps is canonical |
| `careops-process` | `modules/careops-process/` | Minimised process events, process intelligence and conformance | Integrated source; CareOps is canonical |
| `careops-incidents` | `modules/careops-incidents/` | Governed safety analytics and controlled signal boundaries | Integrated source; predecessor history retained separately |
| `careops-costing` | `modules/careops-costing/` | Workload, capacity, cost and benefit calculations | Integrated source; CareOps is canonical |
| `careops-finance` | `modules/careops-finance/` | Finance reporting, semantic models and reusable ALM patterns | Integrated source; CareOps is canonical |
| `clinical-hub-core` | `modules/clinical-hub-core/` | Meeting and DDMS source; private native evidence stays external | Integrated source; CareOps is canonical |
| `careops-ppg` | `modules/careops-ppg/` | Policy/procedure/guideline lifecycle tools | Integrated source; CareOps is canonical |
| `careops-rims` | `modules/careops-rims/` | Publication ingestion, attribution and reporting | Optional pinned submodule |
| `careops-sim` | `modules/careops-sim/` | Independent Rust/Kairos simulation and scenario/result contracts | Optional pinned submodule; native/runtime acceptance remains separate |
| `careops-workforce` | `modules/careops-workforce/` | Power BI workforce analytics, forecasts and planning | Integrated source |
| `careops-catalogue` | `modules/careops-catalogue/` (planned) | Native SharePoint data-product discovery; two-List/one-Library core before optional layers | Catalogued in-tree proposal; not an implemented module or deployed site |
| `careops-legacy-migration` | `modules/careops-legacy-migration/` (intended) | Legacy-system discovery, migration, reconciliation and decommissioning | Catalogued under historical repository slug; existing rename/cutover decisions remain separate |

The Conductor source at `.agents/plugins/conductor` is a development submodule, not a CareOps operational capability. It is separate from the selected module rows above. See [checkout instructions](../README.md#repository-topology) rather than using historical submodule examples for integrated source.

## Source of truth and maintenance

| Question | Controlling record |
| --- | --- |
| Which source is selected, where, and in what form? | [repos.json](repos.json), actual Git tree and `.gitmodules` |
| Which source corresponds to a private implementation or predecessor? | [Delivery catalog](delivery-catalog.json), module provenance and migration records |
| Who owns the native solution, connection or artifact? | [Power Platform ALM inventory](power-platform-alm.json) and approved private records |
| What is the next bounded task and what has been proved? | [Suite queue](../conductor/suite-delivery.md), [track registry](../conductor/tracks.md) and module-local plans |
| What checks and release evidence are required? | [Delivery standards](../docs/development-and-delivery.md), module `.careops/module.json` and [CI contract](../docs/ci-delivery-contract.md) |

When a source-integration or pin change is accepted, reconcile the registry, Git tree/gitlinks, reviewed public-source inventory, current rows in this table and README checkout instructions in the same change. Preserve dated receipts as history rather than appending contradictory current instructions. Do not mark a source-only change as native acceptance or rewrite another owner's task status.

The existing parent source-regression suite checks these current module tables, documented submodule paths and integrated delivery locations against `repos.json` and `.gitmodules`. Historical receipts remain untouched; a migration must update current guidance and source declarations together.

Organisation, jurisdiction, identity, tenant and policy bindings belong in private deployment profiles, not reusable module code. The source/publication boundary remains in force even when the repository is private.

## Admission and update gates

Before admitting new source or changing a selected upstream reference:

1. Verify licence, third-party attribution, provenance and the specific source or versioned contract need.
2. Inspect the proposed source and relevant history for confidential, clinical, personnel, tenant, credential and generated operational material.
3. Preserve existing owners, release gates, tests, security/privacy checks, rollback and independently usable module commands.
4. For an **optional submodule**, reconcile its exact gitlink, canonical URL, paired manifests and qualification evidence. Never silently follow a branch tip.
5. For **integrated source**, retain migration/provenance evidence and remove superseded gitlink instructions only after the existing integration track qualifies the change.
6. Verify the affected source and fresh-checkout behaviour, then use the protected review/merge process. Native activation remains separately authorised.

This catalog does not authorise deleting predecessor repositories, changing their visibility, archiving open work or transferring records.

## Catalogue integration boundary — proposed 6 November 2026

The planned `careops-catalogue` is an optional reference/discovery layer. Its first usable release is native SharePoint Lists/Libraries, forms and views, without a bespoke SPFx React app, CKAN runtime or premium/Copilot dependency.

Later approved read-only references may surface Approve requests, Decisions evidence, PPG documents, RIMS publications, Clinical Hub packs, approved Process/Incidents aggregates, Costing/Finance data products, Sim synthetic scenarios and migration inventories. Each source module retains its authoritative records and workflow. The [catalogue ownership map](../docs/clinical-data-catalogue/architecture.md#careops-capability-integration-map) and [ordered milestones](../conductor/tracks/ckan_catalogue_20261106/plan.md) define the boundaries.

## Topology decision

CareOps is progressively integrating the family of reusable sources into the parent repository. The current checkout is intentionally mixed: some modules are ordinary maintained source and others remain optional pinned references until their own migration work is accepted. This replaces the earlier blanket description of the family as permanently polyrepo.

Source colocation does not require a shared deployment, release cadence, database or service identity. Approve still owns administrative orchestration; Decisions still owns formal committee/delegated governance; Clinical Hub retains its meeting responsibilities. Coordinate interfaces without duplicating authority or forcing unrelated modules into the core runtime.

## Active implementation and reusable-source alignment — 18 October 2026

**Historical scope.** The [delivery catalog](delivery-catalog.json) preserves source-to-implementation relationships and private native ownership. HWCC remains historical costing evidence to reconcile with Costing; Legacy Migration retains its separately governed repository/cutover path. These records do not override the current source map above.

### Source and implementation ownership reconciliation — 25 October 2026

**Historical checkpoint, not current checkout instructions.** The dated source receipts and earlier optional-gitlink selections remain in [the suite delivery record](../conductor/suite-delivery.md#source-composition-execution-plan--25-october-2026) and module history. Later direct-source integrations supersede the affected optional-gitlink descriptions; use the current map above rather than the historical selection.

Use the [development baseline](development-baseline.json) for dated upstream candidates, not proof that those versions are installed or native-qualified. Dependency inventory must use the repository's selected interpreter and approved source roots; private paths and bindings are not published here.

## Current source composition

The current table above and `repos.json` are the source-form reference. Proposals are separate: Catalogue and Legacy Migration are not made materialised modules by appearing in this table. Finance's accepted direct-source integration is reflected in the current map, checkout examples and delivery catalogue.

Existing tracks retain source, interface, release and native-acceptance evidence separately. Signed-release blockers and operational holds remain open where recorded. CGov/credentialing and legacy cutover retain their own programmes; neither this cleanup nor catalogue planning closes them.

## Process and Approve cutover — 6 November 2026

Process and Approve are maintained directly in CareOps. Their former optional-submodule instructions are superseded. Use the current directories and module-local instructions; preserve the predecessor and provenance records for recovery. No native permission, publication or send authority is added by source cutover.

## RIMS relationship verification extension — 11 November 2026

The planned [RIMS relationship assurance track](../conductor/tracks/rims_relationship_assurance_20261111/index.md) adds a review-gated, evidence-aware publication relation verifier without adding another canonical publication, author, organisation or grants register. It distinguishes institutional affiliation, authorship leadership, formal partnership, actual grant award acknowledgement, topical opportunity relevance, study links and clinical service relevance. Parent Conductor planning is committed; source implementation in the optional RIMS submodule is **not** established. RIMS GitHub write access was refused (403) during this change. No change to source materialisation, current gitlink, tenant runtime or reporting authority is implied.
