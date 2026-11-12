# Track 00 — Rapid CHHHS Research Intelligence for 13 November 2026

## Intent
Produce an evidence-qualified **8–10-slide** presentation for the 13 November 2026 CHHHS research symposium. Prefer recovery of historical accepted 1,344-record RIMS register (18-field bibliography, 23 historical indicators) over repeating already accepted provider acquisition. If recovery is not possible, use bounded public-only reconstruction with explicit provisional labels. Never cite 1,344 as the result of a fresh collection.

## Source admissibility and labelled dataset finding (12 Nov 2026)

- `careops` public main repository holds source/contract/aggregate evidence, but **not a confirmed complete 1,344-row labelled publication extract**. `PublicationCandidates.csv` under `portfolio/rims/sharepoint/csv-headings` is headings only.
- `edithatogo/research-publications` and `edithatogo/careops-rims` historical trees inspected: `examples/webfirst-synthetic-export/publications.csv` is a **synthetic example**, not the full accepted register. Treat the repositories' private retained consumer receipts/data as distinct from this sample.
- Historical comparison: 1,344 canonical; 1,277 PubMed; 709 DoRA; 642 overlap; 11,731 PubMed author-evidence rows; 1,284 OpenAlex matches; 1,285 Crossref retained/fresh; 23 indicators. These are **archived acceptance claims**, not current population or fully accessible row-level evidence. See [retained-source handoff](../../../../docs/rims/retained-source-and-native-consumer-reconciliation-20261110.md).
- Field alias dictionary contains `CanonicalKey`, `PublicationYear`, `Authors`, `ReviewStatus`, `AttributionEvidence`, `SourceSet`, `CHHHS-affiliated author source claim`; a source 'Included' is **not independent human adjudication**. Do not promote inferred labels to verified labels.

## MoSCoW

| Priority | Requirement |
| --- | --- |
| Must | Locate the retained accepted export/receipt via authorised original custody; do not commit private records or export hashes to Git. Record exact count, accepted revision, schema, identity keys, source provenance and whether approval is genuinely independently verified. |
| Must | If recovery fails, generate a public-only candidate cohort from eligible source APIs with affiliation evidence and a conspicuous *provisional, incomplete* warning. No synthetic or aggregate-only work treated as publication-level data. |
| Must | Separate `historically_accepted`, `source_included`, `independently_reviewed`, `public_affiliation_candidate`, `excluded` and `unknown`; record uncertain denominator and date-precision buckets. |
| Must | Produce a dated 8–10 slide deck using ONLY metrics calculated from accessible publication-level rows, each with numerator, denominator, source vintage and missing-data caveat. |
| Must | Include publication output by year, topics/specialties (method documented), collaboration partner and citation distribution only where records support them; omit rather than simulate unavailable indicators. |
| Must | Compare changes cautiously: latest year provisional; first/last author not equivalent to CHHHS leadership; citations age- and source-dependent; no causal impact claims. |
| Should | Produce four reproducible figures plus a small source/denominator dashboard and 3–5 linked strategic implications. |
| Should | Reuse original 23-indicator names/definitions when exact input data and qualified metric definitions are accessible. |
| Could | Add CiteLattice-compatible CSL-JSON export, graph edge list and Power BI-friendly tables after qualification. |
| Won't | Reharvest all 17 RIMS sources; share private personnel or review records; present simulated graphs; conflate historical acceptance with current operational validation. |

## Required strategic narrative

1. Research footprint and data provenance.
2. Output trajectory: 10–15 years where observed with incomplete period flags.
3. Concentrations and emerging themes with method, co-topic caveats.
4. Collaboration network: institutional affiliation, not necessarily signed partnerships.
5. Influence: citation *vintage and reference-source coverage*; no combined-provider counts.
6. Three to five opportunities supported by observations, uncertainty and potential actions.
7. Immediate research intelligence capability and next-phase validation agenda.

## Acceptance

- [ ] Dataset provenance certificate with non-synthetic row-level input, count, source vintage, labelling authority, duplicates and missingness.
- [ ] Citation/network/annual outputs calculated and validated from that input, not historical aggregate totals alone.
- [ ] 8–10 slides with footnotes, source date, reliable denominator, caveats and no claim of current RIMS parity.
- [ ] Independent numerical spot checks and evidence record; presentation artefact reviewed for projection readability and privacy.

**Current status:** specification committed; the row-level accepted source is not presently located. Symposium deck, metrics and validation pending.

## Uploaded Publication Registry CSV — preliminary inspection 12 Nov 2026

The user supplied `Publication Registry.csv` in the current ChatGPT session; **the original record-level file is not placed in public Git**. File contains 1,662 data rows and 21 columns. Exactly 1,359 rows have a nonempty unique `CanonicalKey` and 303 are publication-empty administrative/review placeholders. Status distribution: 1,276 Included, 385 Needs Review, 1 Excluded. Among the 1,359 canonical-key rows: 1,276 Included, 82 Needs Review, 1 Excluded; the 303 canonical-key-empty rows are all Needs Review. The file therefore supplies **an existing source-level inclusion label**, not an independently certified reviewed inclusion flag. 1,301 nonempty PMIDs, 1,299 DOI field values; DOI/PMID zero/sentinel and duplicate diagnostics require cleaning before network enrichment. There are no source citation-count or reference-edge columns.

These counts are a **current uploaded export assessment**, not RIMS's historical 1,344-record cohort. Do not force the counts equal, presume identical snapshots, or discard the 82 review candidates without separately reporting them. PublicationYear contains thousands-formatted values like `2,024`; parse carefully. A four-record duplicate DOI and four sentinel PMID zero values require investigating; distinct canonical keys are not sufficient to establish bibliographic uniqueness. Historical 2026 output is provisional and should not be compared as a complete publication year. Publication titles, author names, affiliations, citation identifiers and review evidence are private working inputs; only aggregate findings are committed.

**Changed dependency:** This export makes rapid annual and thematic analysis immediately feasible, with source-labelled (not independently approved) included subset. Citation graph and citation influence remain blocked on provider enrichment. Build release-QC from 1,359 populated rows, not 1,662 all rows.
