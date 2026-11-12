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
