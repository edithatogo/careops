# RIMS research relationship assurance — 11 November 2026

**Status:** Conductor planning and contracts only. No live ingest, registry schema, SharePoint flow, Power BI model, data reconciliation or automated verification is implemented by this track.

## Owner and boundaries

CareOps RIMS retains canonical publication identity and existing publication-level inclusion authority. The derived author registry, organisation enrichment and grants registry remain independently owned. This track adds a **relationship-specific verification stage** after enrichment, before attribution or publication–partner/grant/project outcomes enter accepted RIMS aggregates. It is not a new publication register, collector, external identity service or general-purpose AI workflow.

The RIMS module at [edithatogo/careops-rims](https://github.com/edithatogo/careops-rims) is currently an optional pinned source in CareOps. Its canonical branch was read, but this conversation's GitHub integration returned **403 on creating a branch** there. Consequently this programme is committed to **parent CareOps Conductor only**; RIMS module code and module-local tracks have **not** been changed. Assign module implementation to the existing RIMS source owner once write permission is available.

## Reuse and reconciliation

Use existing module authorities:

- [Author registry design](https://github.com/edithatogo/careops-rims/blob/main/docs/AUTHOR_REGISTRY_DESIGN.md), `scripts/author_registry.py` and accepted author resolution; no name-only identity merge.
- `scripts/clinical_attribution.py` for **candidate** first/last/collaborative classification; free-text keyword match is not verified institutional research leadership.
- `scripts/organisation_enrichment.py`, existing ROR/name variant and facility hierarchy evidence; distinguish organisational identity, published affiliation, employment, study site and formal partnership.
- `scripts/grants_relationships.py` for `funded_by_award`, `relevant_to_opportunity` and `investigator_affiliation`; preserve its reviewed `Included/Excluded/Needs Review` meanings and do not equate topical relevance with funding.
- Existing `crossref_award_crosswalks.py`, `award_identifier_crosswalks.py`, `nhmrc_*_crosswalks.py`, `government_award_crosswalks.py`, and existing publication identifiers/collector snapshots.
- Existing RIMS source catalogue, 17-provider reuse and data-utilisation programme in [parent PR #309](https://github.com/edithatogo/careops/pull/309), which is **open and unmerged** at planning. Do not duplicate its 36-flow or medallion work or treat its proposed source as current main.
- Existing Grants G06 relationship objective and related RIMS G01–G08 work. Preserve owned list/flow identities and native release gates.
- Existing accepted native publication/reporting service (where independently evidenced); source verification does not authorise changing any live ingestion, dashboard or reports.

Existing public enrichment providers (e.g., OpenAlex, Crossref, ROR and OpenAIRE) are **evidence contributors**. They often share upstream publisher/DOI metadata; duplicated downstream observations are not independent corroboration. Respect approved source terms, rate limits, keyless/credential policies and exact authorised internal List access.

## Documents

[MoSCoW requirements](requirements.md) · [Design, types and Mermaid](design.md) · [Granular executable plan and acceptance tests](plan.md).

## Completion boundaries

- **Planning**: this parent track source added and linked; no RIMS module changes claimed.
- **Source implementation**: typed relationship/evidence schemas and deterministic assessor in RIMS with fictional, property-based/adversarial tests and source inventory checks.
- **Native**: approved existing SharePoint/Power Platform data binding, fully paginated reads, readback, privacy/access and recovery qualified, with known record owner.
- **Operational**: two or more actual new publication cycles, accepted relationship dispositions and exception review verified separately; no automatic publication/email or change to canonical bibliography from inferred linkage.
- **Analytical**: exact versioned relationships incorporated into existing RIMS model/dashboard/paginated source with measures validated against authoritative facts; impact claims require a separate evaluation.

A genuine conflict or insufficient evidence remains an exception. Do not impose approval on every unambiguous deterministic relationship or reopen previously accepted unrelated records.

## GitHub repository state verification — 11 November 2026

A renewed GitHub check reports `edithatogo/careops-rims` **archived=true**, even though the authenticated `edithatogo` account has admin/push repository permissions. A repeated branch creation against the pinned RIMS main SHA `8fdc68f09a2bdbb9dc1ab0bc39743e810fef6714` returned HTTP 403 (`Resource not accessible by integration`). The actual source modification blocker is the repository's archived/read-only state (and potentially app-specific write restrictions), not lack of ordinary account-level repository permission. The archived RIMS predecessor must not be unarchived or have history rewritten automatically. Source development should remain in the canonical CareOps ownership lane; any decision to reactivate this archived repository requires a separate explicit repository-management action. No RIMS child code/track has been written.

## Canonical destination correction — 11 November 2026

The user confirms RIMS development was moved under **CareOps**. The archived `edithatogo/careops-rims` repository is a predecessor/recovery reference, **not the requested active write destination**. The prior attempt to create a branch there was misdirected and must not be used to determine whether CareOps implementation can proceed. Current remote readback of `edithatogo/careops` at `main` (`7de89d644b66123b47d75816dd9f5f9600e69f83`) shows `modules/careops-rims` still as a gitlink to `8fdc68f09a2bdbb9dc1ab0bc39743e810fef6714`; the open parent RIMS PR #309 (head `e8ee02fef239c84acc12176a7b68e0b27356d528`) also currently exposes that gitlink. Treat the migration/source-admission status as **unreconciled** rather than asserting fully integrated source or requesting predecessor unarchival.

**Implementation handoff:** work in the active CareOps source-integration lane, first reconcile the intended source tree, parent registry, submodule/gitlink and PR #309. Once in-tree RIMS source is established in an owned CareOps branch, implement RRA tasks there, not by writing to the archived repository. Preserve RIMS prior provenance, security inventories, existing native deployment owners and historical records. No new parent change converts a gitlink into source or proves source migration completed.
