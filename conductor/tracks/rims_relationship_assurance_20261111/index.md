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
