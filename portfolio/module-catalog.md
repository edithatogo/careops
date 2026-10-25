# CareOps module catalog

The portfolio distinguishes a **selected optional submodule** from a **catalogued
module**. A selected submodule pins reviewed independent source; its checkout is
explicit. Cataloguing records intended architecture without forcing every
module into every checkout.

| Module | Intended path | Role | Current state |
| --- | --- | --- | --- |
| `careops-approve` | `careops-approve/` | Intake, validation, routing and human approvals | Materialised submodule |
| `careops-decisions` | `modules/careops-decisions/` | Committee and formal decision governance | Selected optional public source submodule |
| `careops-process` | `modules/careops-process/` | Process intelligence and conformance assurance | Selected optional public source submodule |
| `careops-incidents` | `modules/careops-incidents/` | Safety analytics and controlled signal boundaries | Integrated source; original private repository archived |
| `careops-costing` | `modules/careops-costing/` | Cost, workload, capacity-release and benefits modelling | Selected optional public source submodule |
| `careops-finance` | `modules/careops-finance/` | Finance migration and reusable reporting/ALM patterns | Selected optional public source submodule |
| `clinical-hub-core` | `modules/clinical-hub-core/` | Canonical meeting and DDMS source development; private native evidence stays external | Integrated source; CareOps is canonical |
| `careops-ppg` | `modules/careops-ppg/` | Policy/procedure/guideline lifecycle tools | Selected optional public source submodule |
| `careops-rims` | `modules/careops-rims/` | Publications ingestion, attribution and reporting | Selected optional public source submodule |
| `careops-sim` | `modules/careops-sim/` | Independent Rust/Kairos simulation and scenario/result interfaces | Selected optional public Rust source submodule; qualification in progress |
| `careops-legacy-migration` | `modules/careops-legacy-migration/` | End-of-life system discovery, migration, reconciliation and decommissioning | Catalogued under historical repository slug pending in-place rename |

The parent `careops` repository is the portfolio control plane rather than a
runtime module. It holds shared standards, deployment profiles, compatibility,
feature radar, Agent Skills, portfolio assurance and release evidence.

All modules are organisation-neutral at their reusable core. Organisation,
jurisdiction, tenant, identity and policy configuration belongs in a deployment
profile or environment-specific settings that are not committed with sensitive
values.

Before a catalogued module becomes a Git submodule:

1. confirm its licence and third-party attribution boundary;
2. inspect tracked files and history for confidential, clinical, personnel,
   tenant, credential, generated-output and environment-specific material;
3. verify its publication-boundary and secret-scanning controls;
4. define the source or versioned contract need that justifies a parent pin;
5. align branch protection, issue traceability, CI, recovery and release tags;
6. add the canonical repository URL to `.gitmodules`; and
7. pin the exact gitlink only after cross-module validation passes.

## Topology decision

CareOps remains a polyrepo portfolio. A monorepo should be reconsidered only if
most modules share the same release cadence, deployment unit, security boundary,
maintainers and change set. Those conditions do not currently hold. The parent
repository supplies shared standards and integration contracts without forcing a
single deployment or a single data boundary.

`careops-approve` and `careops-decisions` are intentionally separate despite
close integration: Approve owns administrative orchestration, while Decisions
owns committee and delegated-decision governance. If they later require atomic
changes and one Power Platform release artifact for most deployments, the
portfolio can retain separate source repositories and publish a coordinated
release train before considering physical consolidation.

## Active implementation and reusable-source alignment — 18 October 2026

[The delivery catalog](delivery-catalog.json) records the additional source and
implementation relationships without changing enterprise authority or creating
submodule/runtime dependencies. Clinical Hub Core, CareOps PPG and CareOps RIMS
are reusable-source modules; private Clinical Hub, PPG and publications working
implementations retain native ownership. HWCC is historical costing evidence to
reconcile with CareOps Costing before any consolidation. The legacy repository
keeps its current slug pending the existing in-place rename decision.

Use [shared delivery standards](../docs/development-and-delivery.md) and each
module's `.careops/module.json` for the next low-hanging-fruit increment. The
[dated development baseline](development-baseline.json) records upstream
candidates, not installed or native-qualified versions. Run
`python portfolio-scripts/inventory_dependencies.py --root <checkout>` for source dependency
and immutable-action inventory; private paths are supplied locally, never stored
in this catalog. Publication-boundary gates above continue to apply.

## Current source composition

The [source composition plan](../conductor/suite-delivery.md#source-composition-execution-plan--25-october-2026)
records the selected order and evidence. Incidents and Clinical Hub Core have
reviewed ordinary source in CareOps. Process, Finance, Costing, Decisions, PPG
and RIMS have qualified optional public references. Sim's optional Rust source
reference is under parent qualification. Approve retains its existing root
submodule and independent maintenance track.

All ten module tracks retain their source and later interface tasks. Active
source work stays with its current owner. Public parent visibility does not
grant child access or redistribution rights; child licences remain independent.
CGov/Legacy Migration and credentialing remain separate.
