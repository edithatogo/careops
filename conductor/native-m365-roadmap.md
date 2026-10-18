# Native Microsoft credentialing: delivery through operating maturity

Baseline: 23 September 2026. Programme: edithatogo/careops#160.
Status: lifecycle plan created; native implementation and deployment not complete.

The earlier Conductor tracks cover generic MVP/source-contract delivery, not a
complete production replacement. This programme adds twelve bounded tracks and
120 acceptance-bearing tasks. Existing source/reference work is reused, not
reported as Dataverse implementation. Plans are editable through reviewed PRs.
No production milestone can be inferred from task count or a green source build.

## Architecture and scope

Follow [the native target](../docs/credentialing/native-microsoft-platform.md)
and [standalone contract](../docs/standalone-module-contract.md).
Full Dataverse is the structured production target; controlled SharePoint holds
evidence. SQLite remains synthetic-test-only. Each module has a standalone
business purpose and independently versioned package; adapters are optional.
The parent roadmap coordinates development, not a mandatory live service.

This programme does not rewrite all clinical PPGs or generate every specialty
scope. Preserve the separate craft-led adaptation programme, existing approved
scopes and local professional ownership. Only approved changes enter a deployed
rule profile. Finishing every specialty model is not a blanket platform gate.

## Tracks

| ID | Track | Proposed lead role | Delivery dependencies |
| --- | --- | --- | --- |
| N01 | [Platform, ALM and standalone packaging](tracks/native_01_platform_20260923/plan.md) | Platform architect | None |
| N02 | [Current policy and editable delegations](tracks/native_02_authority_20260923/plan.md) | Credentialing policy owner | None |
| N03 | [Native Dataverse register](tracks/native_03_register_20260923/plan.md) | Decisions module maintainer | N01, N02 |
| N04 | [SharePoint evidence and records](tracks/native_04_evidence_20260923/plan.md) | Records and information owner | N01 |
| N05 | [Deterministic intake and independent jobs](tracks/native_05_checks_20260923/plan.md) | Approve module maintainer | N01, N02 |
| N06 | [Optional agentic preparation](tracks/native_06_agents_20260923/plan.md) | AI assurance owner | N04, N05 |
| N07 | [Accessible workbench and register](tracks/native_07_workbench_20260923/plan.md) | Product and accessibility owner | N03, N04, N05 |
| N08 | [Committee and complete pathway governance](tracks/native_08_governance_20260923/plan.md) | Credentialing governance owner | N02, N03, N04 |
| N09 | [Optional adapters and portfolio independence](tracks/native_09_adapters_20260923/plan.md) | Integration architect | N01, N03, N05, N08 |
| N10 | [Security, resilience and recovery qualification](tracks/native_10_assurance_20260923/plan.md) | Service assurance owner | N03, N04, N05, N07, N08 |
| N11 | [Migration and CGov cutover](tracks/native_11_cutover_20260923/plan.md) | Migration and business owner | N09, N10 |
| N12 | [Operating maturity and lifecycle exit](tracks/native_12_operations_20260923/plan.md) | Named production service owner | N11 |

Dependencies describe evidence needed to finish a delivery track, not runtime
module dependencies or a prohibition on parallel design. AI is optional: N06
must pass before enabling agents, but cannot block an accepted AI-off release.
Optional analytics/incident/finance adapters cannot block core credentialing.
All owner roles need named local acceptance; no staff assignment is claimed.

## Maturity gates applied to each enabled module/capability

- M0: documented scope, owners, data boundary, risks and acceptance criteria.
- M1: reviewed source, native artifacts and reproducible tests; no deployment claim.
- M2: clean standalone sandbox install, native security/concurrency tests and restore.
- M3: supported integration/version/outage tests; optional components absent tests.
- M4: approved silent/limited pilot, representative users and measured workload.
- M5: separately authorised production release, trained support and reconciled data.
- M6: measured operating effectiveness through an agreed observation window;
  service objectives, access recertification and restore rehearsal pass.
- M7: legacy work and contracts retired after reconciliation/records acceptance;
  future CareOps module retirement/export procedure proved.

The current native M2-M7 gates are unverified. The historical Python reference
kernels are M1 evidence for their stated boundary only. Each task closes with a
commit/PR, test or approved evidence reference and reviewer/date; sensitive
receipts stay in the approved records system, with non-sensitive references here.
A checklist is not approval. A failed task remains open with reason and owner.

## Definition of done and release discipline

Each task's plan states its output and acceptance. Split implementation into small
PRs; retain existing checks and negative tests; inspect final-head runs before
SHA-bound merge. New safety logic needs strict typing/static checks, complete
branch/statement coverage where required by its module, adversarial cases and
native-platform tests. Documentation-only checks must not claim those runtime
results. Production-critical paths also require independent clinical/cyber review.

Before M2 publish platform prerequisites and clean-install evidence. Before M4
obtain privacy/records/cyber/clinical/access approvals, baseline burden and stop
rules. Before M5 prove supported recovery and migration, current delegations,
no critical unresolved defects and a funded support/continuity owner. Confirm
applicable licences/capacity instead of assuming M365 includes every service.

No new mandatory portal, duplicate register or parallel approval queue. Each
operational feature identifies the manual task it replaces and measures net work
across practitioners, officers, reviewers and support. Record saved time minus
new correction/support effort; do not infer benefits from automation run counts.

## Module-level maturity matrix

Approve, Decisions, Process, Incidents, Costing, Finance and Legacy Migration each
need their own M0-M7 evidence applicable to their standalone purpose. N01 and N09
apply to all seven, with per-module test results, not a single portfolio pass.
The register is an optional Decisions-owned capability, not a new repository.
A coordinated CHHHS deployment may enable only Approve/Decisions and selected
adapters; it need not install every portfolio module.

## Initial execution order and limits

Start N01/N02 discovery and native sandbox qualification; build N03/N04/N05 in
small slices. Then complete the routine-renewal vertical slice through N07/N08
and assurance. Add N06 only where it demonstrably saves work. Complete the
in-scope pathway matrix and migration/operations gates before retiring CGov.

Architecture and this plan do not provision environments, certify PPG compliance,
verify signed delegations, grant scope, migrate practitioner records, cancel a
contract or establish savings. Deployment and contract costs remain private
planning inputs; their period and inclusions require confirmation.
