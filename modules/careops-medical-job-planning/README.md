# Medical Job Planning — source-development slice

**Status: partial standalone source, not operational or native-qualified.**

This directory starts implementing the [Conductor Medical Job Planning programme](../../conductor/tracks/medical_job_planning_20261113/index.md) without replacing `modules/careops-workforce` (the existing Power BI analytics module). The first increment is a pure, dependency-free synthetic session validator and arithmetic reference, not a deployable Canvas App or SharePoint service. It does **not** implement the full v0.4.2 archive or constitute formal completion of source-admission W0.

## Boundaries

- `domain.py`: strictly typed session parsing, overlapping interval rejection and synthetic reference-only hour reconciliation. All calculations are marked `reference_only_unadopted` and cannot approve a job plan or determine industrial compliance.
- `tests/test_mjp_domain_slice.py` in the parent repository: synthetic regression and domain tests. Run via the repository's verified Python 3.15.1 environment: `python -m unittest discover -s tests -p 'test_mjp_domain_slice.py' -v`.
- The source originated as a clean-room constrained rewrite of the relevant input-validation and calculation concepts in the user-supplied `careops-workforce-app_v0.4.2.zip`; archive hash, predecessor code hashes, privacy admission and scope are documented in `SOURCE_PROVENANCE.json`.
- The complete v0.4.2 archive, workflow runtime, adapters, app specifications, blueprints, flow scaffolds and retained test suite are **not** included here; before importing any additional files, pass source/privacy/licence/provenance checks and update the source inventory.
- The current module has no installed SharePoint lists, managed solution, cloud flows, external HR connectivity, live industrial-policy rules, operational identities, real staff records or automatic emails. Existing CareOps authority boundaries remain unchanged.
- Existing `modules/careops-workforce` remains authoritative for its own reviewed Power BI source and privately bound feeds. There are no new workforce reporting interfaces deployed by this slice.

## Follow-on W0/W1 work

Qualify exact Python pin and all parent harness checks; extend formal rule packs with accepted policy authority; implement exact source hashes, immutable versioned plans, negotiation/dispute states and safe CAS transactions; evaluate SharePoint security against Dataverse alternative; integrate optional provider interfaces only when independently accepted.

No general import, tenant provisioning, case approval or policy adoption is implied by successful source tests.
