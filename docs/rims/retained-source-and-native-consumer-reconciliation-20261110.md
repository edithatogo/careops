# Retained RIMS data and native consumer reconciliation — 10 November 2026

Status: **historical accepted scope identified; current CareOps/tenant parity unverified**. Authoritative evidence is from the archived `edithatogo/research-publications` repository and its separately retained private owner receipts. Do not repeat approved collectors, reimport private rows into public Git, assume current freshness, or manufacture approvals.

## Previously accepted data and outputs worth reusing

| Component | Accepted earlier evidence | Still incomplete or not transferred to CareOps |
| --- | --- | --- |
| Canonical publication register | 1,344 canonical publications; 1,277 PubMed, 709 DoRA and 642 overlap; 18-field full bibliography | Newer retained/admission generations, complete latest source capture and migrated authority |
| Retained PubMed raw/typed consumer | 1,277 complete metadata records; 11,731 author-evidence rows; independently verified typed/raw receipts | Standalone source consumer adoption in CareOps, per-field Silver/Gold mapping and current acquisition |
| Europe PMC | 1,286 exact PMID matches plus 58 missing; 140 populated field paths | Revalidate downstream consumer coverage and exact source/date status; do not conflate with publication totals |
| OpenAlex | 1,284 matches, 57 missing identifiers, 3 explicit no-matches; 232 populated field paths | Field-to-report utilisation measured with actual source records |
| Semantic Scholar | 1,266 matches, 19 explicit no-matches, 12 missing/invalid, 2 conflicts, 45 deferred lookups; 45 populated field paths | Rate-limited 45 lookups and subsequent source/model admission |
| Crossref | 1,286 DOI keys, 1,285 retained/fresh records; 1,282 HTTP200, 4 explicit 404 | No full fresh 1,344-publication sweep proved; natural later execution separate |
| OpenCitations | Accepted 48 DOI assertion scope, incoming links archive of 344 unique OCI observations | Not a complete model projection for all 1,344 publications |
| Grant references | 169 candidate edges connected to 67 of 1,344 canonical keys; **zero confirmed relationships** | Reviewed grant-award relationships and later native eligibility/output projection |
| Study/DoRA | Actual 442 retained DoRA rows; 11 source-reported CHHHS associations; one reviewed study identity in later source evidence | Complete study lifecycle/outcome/ethics link and native model integration |
| T18 Power BI | 1,344 current model keys; 23 indicators across four headings; three connected scorecard values, complete six-page native A4 RDL/PDF and 1920×1080 Clinical Analytics native rendering | Other metric values lacked genuine outcome evidence, natural monthly delivery RMD-05, CareOps source ownership and current tenant drift checks |

The T18 accepted outcome indicator includes 36/53 assessed OA (67.9%) but only 53/1,344 had an assessed OA status. **Never label that 67.9% as OA among all publications.** In other cohorts numerator/denominator/unknowns vary independently; the 984-publication Cairns drillthrough had 4/4 assessed and 980 unknown. Unassessed does not mean closed access.

## New source-side adapter

`portfolio-scripts/rims_retained_pubmed_adapter.py` consumes the already accepted **`isolated_retained_pubmed_consumer_v1`** shape, with an independent verification callback for the historical typed/raw acceptance and explicit PMID→canonical mapping. It keeps all returned metadata fields and nested structures in Bronze/Silver and checks author-evidence membership without publishing names or inferring employment. It does **not** accept historical data automatically for current publication reporting or re-run PubMed acquisition. Synthetic tests qualify source and identity refusal paths, not private retained bytes.

The existing accepted source scripts are:
- `research-publications/scripts/consume_retained_pubmed.py`
- `research-publications/scripts/consume_retained_grant_references.py`
- `research-publications/scripts/publication_source_metadata_contract.py`
- `research-publications/scripts/source_relationship_evidence.py`

The exact accepted private receipts, keys, hashes and runtime/tenant bindings stay with their original custodian.

## Required integration tasks

1. **RET-01** Re-read the archived source exact SHA and private retained consumer+raw acceptance receipts, confirming owner custody and whether a later accepted generation supersedes 31 Oct. No production write.
2. **RET-02** Execute `rims_retained_pubmed_adapter.reconcile_pubmed` in the approved private runtime using exact canonical PMID lookups and maintained Licence/retention profile; independent source receipt verifier required. Compare counts, all metadata fields, nested author cardinalities, all-source source digest.
3. **RET-03** Reuse the provider-specific `PublicationSourceEvidence`, `PublicationSourceRecordChunks`, `PublicationSourceArchiveChunks`, `PublicationSourceFields` evidence. Measure per-provider source field → Silver typed → Power BI consumer use, with explicit retained-only and missing fields; do not repeat source acquisition.
4. **RET-04** For each of Europe PMC, OpenAlex, Semantic Scholar, Crossref, OpenCitations, match actual source identity/observation and cardinality before proposing new views; maintain separate citation count methods, no summing sources.
5. **RET-05** Link only actual authorised/verified study and award relationships; 169 grant-reference candidates remain unconfirmed until reviewed against authoritative award register.
6. **RET-06** Compare new stakeholder metric catalogue against the accepted T18 23-indicator dictionary, three connected scorecard values, native paginated RDL, and 1,344 source/model key population. Preserve accepted working model/visuals and existing owner.
7. **RET-07** Reconcile standalone archive/native source owner and CareOps optional pinned module. Migrate source only when signed-off snapshots, licence, rollback and protected CI are qualified.
8. **RET-08** After source→consumer coverage and actual first/last source dates are established, prioritise real research impact, researcher/organisation network, funding→output and study lifecycle analytics; otherwise mark unavailable rather than manufacturing outcome values.

## Data adequacy and interpretation

Field counts are **populated source paths**, not exhaustive provider schema utilisation; accepted evidence may be older or frozen. Published article counts are not a census of current CHHHS research activity. Proposed cross-domain measures are descriptive and require authorised source/relationship confirmation, denominators and uncertainty. This document does not duplicate the native accepted RIMS work, certify its current deployment or replace the original handoff.

### Historical evidence references
- https://github.com/edithatogo/research-publications/blob/main/docs/RETAINED_CONSUMER_ADOPTION_20261031.md
- https://github.com/edithatogo/research-publications/blob/main/docs/PUBLICATION_FREE_API_HANDOFF_20261103.md
- https://github.com/edithatogo/research-publications/blob/main/conductor/tracks/chhhs_outcomes_powerbi_20261021/review-20261103-delivery.md
- https://github.com/edithatogo/research-publications/blob/main/conductor/backlog-reconciliation-20261103.md
