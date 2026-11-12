# Track 00 — recovery-first execution checklist

**Deadline context:** CHHHS symposium on Friday 13 November 2026; this is a bounded rapid response rather than a full RIMS migration.

## A. Locate, classify and freeze inputs

- [x] Inspect user-provided row-level Publication Registry CSV (1,662 rows; 1,359 canonical-key populated; 303 blank publication placeholders). This is source-level data accessibility, not independently approved cohort acceptance.
- [ ] Reconcile exported 1,359 canonical-key rows and statuses against original accepted 1,344-row publication-level bibliography and receipt; investigate snapshot differences and actual inclusion authority. Do not publish identifiable row data to Git.
- [x] Inspect schema: canonical IDs, titles, year/date, authors, journal, matched facilities, attribution evidence, source/ReviewStatus present; **citation count and citation/reference edges absent**.
- [ ] Capture release-qualified approved private working input and independently validate attribution, status and deduplication. Keep original private bytes out of Git.
- [ ] Distinguish historical accepted status from reviewer-verified CHHHS labels. Record duplicate and unknown counts.
- [ ] Decide deterministic branch: recovered valid input → direct analysis; missing or unverified → bounded public metadata cohort, **labelled provisional**.

## B. Bounded analytical extraction

- [ ] Construct annual counts with date and review-status denominators; incomplete current year labelled.
- [ ] Classify themes from available controlled source topics/subject keywords; disclose overlapping categories and unclassified remainder.
- [ ] Use affiliation strings/ROR to map organisations without equating them to formal partnership; distinguish CHHHS author attribution and inferred specialty.
- [ ] For provider-qualified citation snapshot, show distribution/rank and observation date, separate provider coverage; optional external citation graph only if cited/citing edges actually retained.
- [ ] Develop 3–5 opportunities that directly trace to observed thematic trajectory, collaboration and gaps. Avoid rankings of individual researchers.

## C. Presentation and evidence

- [ ] Create concise 8–10 slide briefing with numbers in chart footnotes, caveats and explicit timeframe.
- [ ] Verify summary counts against raw rows and spot-check five inclusions/duplicates; test ambiguous CHHHS affiliation and missing identifiers.
- [ ] Save analytical dataset, summary, plots, QC and deck in approved working artifact destination; Git only contains code/contracts and publicly distributable data.
- [ ] Source-code tests, Conductor review and implementation evidence; update this checklist and archive after actual acceptance.

## If no real row-level data is available

Prepare **a qualitative strategy framework with historical aggregates clearly identified**, not fabricated publication trend lines, network diagrams or retrospective citation statistics. Slide placeholders should be omitted rather than filled with synthetic figures.

## Live bounded search receipt — 12 November 2026

- **Executed using connected PubMed search, NOT Searchright.** Searchright CLI/MCP source exists in `edithatogo/searchright`, but Searchright MCP was not connected in this ChatGPT session; an attempted remote compute job returned HTTP 402. Do not mark Searchright-live acceptance.
- PubMed query: `("Cairns Hospital"[Affiliation] OR "Cairns and Hinterland"[Affiliation])`; publication date filter 2026-01-01..2026-11-12, sorted publication_date; offsets 0, 50, 100, 50/50/18 results: **118 distinct PubMed PMIDs**.
- Reconciled against the user's uploaded `Publication Registry.csv`, matching on trimmed PMID excluding blank/zero: **117 present, 1 absent**. New PMID `41783137`, DOI `10.1016/j.ccrj.2026.100163`, title *Evidence-based guidelines for the use of extracorporeal membrane oxygenation in Australia and New Zealand using GRADE methodology series part 1: Venovenous extracorporeal membrane oxygenation (VV ECMO) indications and management*. Published Cairns and Hinterland affiliation, candidate **Needs Review**. Source: https://pubmed.ncbi.nlm.nih.gov/41783137/
- Query retrieval includes three **2026 December issue-date** records despite cutoff: release must distinguish electronic, issue, entry and publication-year chronology before claiming a strict date-window cohort.
- Local working artifacts: `CHHHS_PubMed_2026_reconciliation.csv`, `CHHHS_new_pubmed_candidates_2026-11-12.csv`, `CHHHS_publication_refresh_report_2026-11-12.md`. **Not uploaded to GitHub**, because the source register's row-level lineage is not released for public redistribution.
- Other facility aliases, other years, non-PubMed outputs, OpenAlex/Europe PMC/Crossref enrichment, citation graphs and Searchright execution receipts remain open. The 117/118 match is **not** a census completeness estimate.


## 12 November 2026 — live public provider reconnaissance

See [API findings](../../../../docs/rims/chhhs-public-api-reconnaissance-20261112.md). Multiple provider endpoints responded, but only sampled records retrieved and full-provider pagination, cross-source overlaps and Searchright-generated receipts remain pending. No unreviewed results admitted to canonical RIMS.
