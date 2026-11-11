# RIMS maximal use of already retained data — specification

**Owner:** RIMS data-source/semantic-model maintainer. **Status:** source-side implementation in progress; current tenant/data-product acceptance not established. Reuse existing owner, original raw archive, RMD-05 schedule and accepted Power BI 23-indicator model. This work does **not** grant access to private data or permission to turn on collectors.

## Purpose
For every already collected source, preserve all rights-permitted provider fields and nested structures; use them wherever analytically meaningful, and quantify where they are merely retained, excluded or unassessed. Design separate products for publications, people, organisations, studies/projects, funding and operations. Produce clear research intelligence for researchers, teams, CHHHS executive, funders, the state and communities without conflating metadata richness with evidence of impact.

## Inputs and key safety distinctions
- Existing accepted source archives and byte receipts, including the historical PubMed retained consumer, Europe PMC/OpenAlex/Semantic Scholar `PublicationSourceRecordChunks`, `PublicationSourceArchiveChunks` and `PublicationSourceFields`, Crossref, OpenCitations and grants/studies/organisation sources. Exact private hashes and tenant GUIDs remain with source owners.
- The 1,344-publication historical model, 23-indicator scorecard and accepted six-page paginated report are **already built and source-qualified for their original scopes**. Do not overwrite them; no fresh completeness is inferred.
- An observed field is not automatically used. A source-to-consumer mapping is not proof that a native visual consumes it. A grant mention is not a confirmed award. Author affiliation is not employment. Source citation counts from different providers must not be added together.
- A private raw record must not be committed or emitted in field-profile reports; only field-path metadata and bounded aggregate counts may be published after field-name and disclosure review.

## Contract path
1. **Bronze:** complete rights-qualified raw payload or exact byte archive, typed source record, original path, provenance, licence/retention and pagination status.
2. **Silver:** source-qualified typed entity, field lineage and relationship candidates; every permitted source field either mapped, retained-only or explicitly excluded with reason.
3. **Gold:** source-qualified, decision-verified facts with stable grain, accurate denominators, meaningful labels, security and real Power BI/HTML/CSV data-product bindings.
4. **Platinum:** research intelligence, method, uncertainty, evidence and human release, with models/claims never invented from raw metadata.
5. **Field-profile:** each nested source path, record-level presence/missingness, occurrence, null/empty and observed type; no values.
6. **Utilisation:** exact field path plus downstream consumer, artifact identity, revision and target field; explicitly distinguish declared vs independently verified bindings.

## Non-goals
No Trove or other new collector until existing sources have quantified field utilisation. No premium connector/Copilot/Fabric as core requirements. No new authority, schedule, send, report publication, HR employment inference or silent source field loss.

## Existing-data implementation update — 11 November 2026

The private-source pipeline is now: **independently verified retained JSON bytes → reversible full JSON paths/ordinal occurrences → reviewed provider-specific field map → typed Silver candidate product + complete unselected source occurrences → per-field quality/missingness → separately verified Gold report consumer**. The existing PubMed XML path consumer remains authoritative for accepted XML roots. Every mapped field is a candidate until actual rights, source and consumer verification; no claim of employment, awards, publication approval or causal impact follows from source assertions.

A standalone, non-premium aggregate HTML field-coverage report reads the existing domain rollup but never publishes source values, field paths or inferred native usage. All raw private-product outputs stay in an approved private owner environment; flags in Python do not replace technical access controls.

See [versioned contracts and fourteen executable tasks](json-source-products-20261111.md). Numeric precision remains dependent on original source bytes and Decimal-aware funding conversion; `json.loads` float conversion is not an accepted exact monetary transformation. Preserve the prior accepted Power BI 23-indicator data model and source owners; no new collector, premium adapter, Copilot or Power Automate flow has been activated.
