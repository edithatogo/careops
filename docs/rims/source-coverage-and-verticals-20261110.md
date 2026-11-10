# RIMS source utilisation, coded fields and vertical completeness — 10 November 2026

Evidence: static user-supplied unmanaged solution ZIP (36 workflow definitions), CareOps repository, and archived research-publications handoff/Conductor records. **Not a live tenant, Power BI semantic-model, or complete source-data audit.**

## Five verticals and boundaries

| Vertical | Evidence already in RIMS | Remaining work |
|---|---|---|
| Research outputs | PubMed, DoRA, publication exports; Crossref notices, DataCite related works, OA, citation enrichment | Source-field-to-model-to-report trace; author/funding/reference nested structures; safe reviewer-approved inclusion |
| People and collaborations | Researcher mentions export, name groups, publication-level author order and identity status | Consolidated person identity, actual MS365 directory integration (not demonstrated), temporal organisational affiliations and independently HR-verified employment |
| Projects and studies | DoRA activity register, ClinicalTrials.gov collector and archived study refresh | Full trial arms, outcomes, locations, collaborators, study governance, linked projects/funding/outputs, discrepancies and source revisions |
| Funding | ARC, NHMRC, MRFF, QGIP; GrantConnect through separate browser/native intake; NIH qualification | Distinguish candidate/current grant vs award, internal applications, typed relationships, full provenance, actual lifecycle acceptance |
| Organisations and affiliations | ROR collector, ARDC IDs, source assertions | Canonical organisation history, alternative names, ROR links and time-bounded relationships; avoid automatically converting affiliations to employment |

## Static provider matrix

| Provider | Export evidence | Complete field utilisation proven? |
|---|---|---|
| PubMed | Collector, publication register/exports | No |
| DoRA | Publication and activity collectors | No |
| Crossref | Batch qualification, notices, citation enrichment | No |
| OpenAlex | Enrichment query and author/citation/OA projection | No |
| DataCite | Related-output collector | No |
| ROR | Organisation collector | No |
| ClinicalTrials.gov | Study collector and archived study source refresh | No |
| ARC | Awards collector and export | No |
| NHMRC, MRFF | Source workbook and award refresh flows | No |
| QGIP, ARDC | Source and identifier collectors | No |
| GrantConnect | Separate browser/native route documented; not proof of source parity in this ZIP | No |
| NIH | Acquisition qualification | No |
| Europe PMC, OpenCitations, Semantic Scholar | Additional publication source work documented in research-publications | Full native parity not evidenced by this ZIP |
| National Library of Australia Trove | **No Trove-named workflow in exported ZIP** | Not confirmed integrated |
| Microsoft Graph directory | **No Graph /users or unified person collector identified in exported ZIP** | Not confirmed integrated |

**Important:** This matrix classifies *observed functionality*, not whether a provider's whole data dictionary is relevant or legally retainable. High-quality integration should account for full source payloads and explicitly classify projected, retained-only, rejected, absent and unknown fields. Do not force every provider field into the dashboard.

## Display codes and sample rows

`portfolio/rims-field-aliases.json` maps the exact exported publication flow's `field_1`–`field_20` to SourceKey, CanonicalKey, Authors, Journal, PublicationYear/Month/Date, SourceSet, PMID, DOI, source URLs, facility match, CHHHS-affiliated author source claim, AttributionEvidence, ReviewStatus, ReviewNotes and observation timestamps. Additional measures and dimensions must be reconciled against the actual semantic model. A value of `Included` in `field_17` is **not independently verified human approval**.

`portfolio-scripts/rims_field_decoder.py` is a pure display adapter that refuses colliding aliases, preserves raw values, flags unmapped `field_*` codes and cannot grant approval or employment status.

`portfolio/rims-public-api-samples.json` supplies **one verified public API record each** from Crossref, OpenAlex and ClinicalTrials.gov (captured from the publicly accessible endpoints on 10 November 2026). It also lists documented headings for DataCite, ROR, NLA Trove and Microsoft Graph. Those four are **schema-only**, not fabricated API rows. Public sample metadata is not CHHHS case or user data. Citations and field paths are retained in each sample.

## New data-completeness contract

For each provider, record:
1. Raw schema and archived capture hash, timestamp, provenance, licence and pagination status.
2. Path/type/cardinality; optional/nullable fields; permitted retention, sensitive content and quality constraints.
3. Normalised entity/attribute/relation and deterministic transform version.
4. Source-to-SharePoint or file projection, semantic-model table/measure and visual/page use (or intentional exclusion).
5. Review/operational decision use and authoritative ownership.
6. Coverage metrics by field, record and nested entity, with unknown and suppressed data reported explicitly.

Make field utilisation a **measured lineage matrix**, not an ungrounded percentage. Preserve nested trial interventions/outcomes/sites, publication contributor affiliations, related DOIs and funder IDs where licensed, but expose only necessary derived information to users.

## MS365 unified person view

Proposed optional, non-premium-compatible design:
- Internal `person_id`, distinct `directory_account_id` (Entra object ID), author mention ID, ORCID, researcher record and source-qualified affiliation ID.
- Effective-dated links for organisation, employment status, profession, role, service/team, manager, project and output contributions.
- A consent/permission-bound **read-only minimum-necessary directory snapshot** may use Microsoft Graph `/users?$select=...` if the tenant qualifies the connector, OAuth permissions, DLP and rate limits; otherwise use an approved offline export. Do **not** add premium HTTP/custom connectors as core prerequisites.
- Directory membership, `employeeType`, personal email or author affiliation are candidates only, never HR employment verification. External, visiting, honorary and former staff must remain distinct.
- HR/restricted evidence must not appear in public source control, research dashboards, examples or logs.

## Trove

NLA Trove v3 supports work, people/organisation and historical content discovery; API key is required. No authenticated capture or operational RIMS integration is claimed. Prioritise grey literature, local historical reports and organisational bibliographies rather than duplicating PubMed. Implement a separately authorised, optional adapter with `X-API-KEY`, provider/zone-specific schema, pagination, record identifiers, rights and provenance. Do not store restricted full text without permitted reuse; no API key or real CHHHS identifiers in Git.

## Additional capabilities worth implementing

- A **source coverage observatory**: provider health, source revision, raw records, nested-field completeness, schema drift and data-to-dashboard lineage.
- **Coded-field and semantic-label dictionary**: exact source field names, target types, value dictionaries, units and explicit unknown labels; never modify decision authority from presentation rules.
- **Research identity graph** with reversible human adjudication, time-aware affiliations and explicit confidence/evidence levels.
- **Project-outcome and grant-impact linkage**, translating funding and project activity into datasets, software, clinical studies, publications and policy uptake with source-qualified relationships.
- **Retraction/correction alerts and open-access compliance** with publisher/update notices and licence-based retention safeguards.
- **Optional literature and grey-literature discovery** (Trove, institutional repositories, OpenAIRE), prioritised by coverage gain over duplicate data.
- **Quality dashboards** for missing/ambiguous field values, reconciliation gaps, duplicate candidates and stale sources, using non-premium HTML/CSV and SharePoint Lists as the core.

## Acceptance sequence

1. Verify all static alias mappings and synthetic tests; inspect the actual semantic-model measures, queries and dashboard visuals before attributing specific displayed codes to an origin.
2. Preserve full public source schema contracts and 2–5 real, licensing-permitted example rows per provider where accessible; distinguish live capture, cached/retained, and schema-only fixtures. Never expose MS365 personal records.
3. Inventory existing source archives, field paths and consuming models. Flag null/dropped arrays, inconsistent grains, outdated code dictionaries and missing linkages.
4. Native MS365 person integration and Trove authorisation require the appropriate organisational permission and key; no platform or send operations from source checks.
5. All new functionality is optional, standards-based and free of required premium connectors, Copilot and Fabric capacity.

Source reference documents: https://www.crossref.org/documentation/retrieve-metadata/rest-api ; https://help.openalex.org/api/ ; https://clinicaltrials.gov/data-api/about-api ; https://support.datacite.org/docs/rest-api ; https://ror.readme.io/docs/rest-api ; https://trove.nla.gov.au/about/create-something/using-api ; https://learn.microsoft.com/en-us/graph/api/user-list?view=graph-rest-1.0 .
