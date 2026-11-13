# Medical Job Planning — source-development slice

**Status: partial standalone source, not operational or native-qualified.**

This directory starts implementing the [Conductor Medical Job Planning programme](../../conductor/tracks/medical_job_planning_20261113/index.md) without replacing `modules/careops-workforce` (the existing Power BI analytics module). The first increment is a pure, dependency-free synthetic session validator and arithmetic reference, not a deployable Canvas App or SharePoint service. It does **not** implement the full v0.4.2 archive or constitute formal completion of source-admission W0.

## Boundaries

- `domain.py`: strictly typed session parsing, overlapping interval rejection and synthetic reference-only hour reconciliation. All calculations are marked `reference_only_unadopted` and cannot approve a job plan or determine industrial compliance.
- `policy_rules.py`: source-qualified, effective-dated candidate CST rule snapshot, with distinct planned/observed gaps; even a reference labelled adopted cannot approve a plan. Real authority and identity must be independently checked by the native system.
- `archive_admission.py`: optional source ZIP manifest verifier; validates path safety, file sizes, exact SHA-256 and membership without treating integrity as licensing, privacy clearance or import authorisation.
- `negotiation.py`: append-only, generation-checked, idempotent candidate negotiation/counterproposal/dispute/escalation transitions. It stops at `authority_pending`; it **cannot** approve, issue or activate a plan.
- `plan_records.py`: immutable, source-qualified effective-date and UTC-issued-time references with as-of projection. It returns `unverified_incomplete_source` on partial feeds and never claims external authority has been verified.
- `cas_contract.py`: **in-memory synthetic candidate-submission reference**, with version-1 canonical JSON, staged immutable content, one PlanHead compare-and-swap, bounded operation identity, conflict/replay detection, historical recovery and injected failure points. It is **not** a SharePoint adapter or proof of native permissions, durability, real HTTP 412/429, industrial eligibility or approval.
- `tests/test_mjp_domain_slice.py` in the parent repository: synthetic regression and domain tests. Run all six focused suites through `.github/workflows/mjp-domain.yml` on Python 3.15.1; the verifier does not require the original ZIP to be committed. The CAS suite is `tests/test_mjp_cas_contract.py`.
- The source originated as a clean-room constrained rewrite of the relevant input-validation and calculation concepts in the user-supplied `careops-workforce-app_v0.4.2.zip`; archive hash, predecessor code hashes, privacy admission and scope are documented in `SOURCE_PROVENANCE.json`.
- The complete v0.4.2 archive, workflow runtime, adapters, app specifications, blueprints, flow scaffolds and retained test suite are **not** included here; before importing any additional files, pass source/privacy/licence/provenance checks and update the source inventory.
- The current module has no installed SharePoint lists, managed solution, cloud flows, external HR connectivity, live industrial-policy rules, operational identities, real staff records or automatic emails. Existing CareOps authority boundaries remain unchanged.
- Existing `modules/careops-workforce` remains authoritative for its own reviewed Power BI source and privately bound feeds. There are no new workforce reporting interfaces deployed by this slice.

## Follow-on W0/W1 work

Qualify exact Python pin and all parent harness checks; extend formal rule packs with accepted policy authority; implement exact source hashes, immutable versioned plans, negotiation/dispute states and safe CAS transactions; evaluate SharePoint security against Dataverse alternative; integrate optional provider interfaces only when independently accepted.

No general import, tenant provisioning, case approval or policy adoption is implied by successful source tests.

## Qualified source archive boundary

The original user-supplied offline ZIP (`careops-workforce-app_v0.4.2.zip`, SHA-256 `922c29f0364c7e1a0d61e4d0ba0a87f5cb28416c1f143758577404ff615626a7`) contains 73 manifest-listed entries, all of which passed exact SHA-256, size and archive membership checks in the local source review. No unlisted content was found. This evidence does **not** establish original rights, patient/staff privacy review, executable application completeness, adopted industrial rule or native Power Platform acceptance. The ZIP itself is excluded from public source.

## CAS and storage design

[ADR MJP-002](../../conductor/tracks/medical_job_planning_20261113/adr-cas-storage-20261113.md) identifies the atomic PlanHead operation, immutable-version recovery, the uploaded bundle's 20 logical Lists plus one Library, the unqualified physical security and SharePoint-vs-Dataverse decision. Synthetic tests alone do not establish MJP-G1/G2 native qualification.
