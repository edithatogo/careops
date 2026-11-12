# CHHHS frontier science-of-science implementation/review — 13 November 2026

## Results and provenance
- Private RIMS baseline: 1,662 rows, 1,359 keyed, 1,276 marked Included (source label, NOT independently adjudicated). No private records in Git.
- Public OpenAlex: 2,280 candidate works; FWCI and citation percentile for 2,070; primary topic for 2,264. Public snapshot at `portfolio/rims/public-sources/openalex-chhhs-normalised-impact-topics-20261113/`.
- Private-safe identifier reconciliation: 1,213 OpenAlex works exactly matched source-Included; 1,171 have OpenAlex FWCI/percentile; 2010–2022 top citation decile 94/540 (17.4% of eligible matched works). 2026 is excluded from full-year comparisons.
- Candidate reference network: 2,196 internal directed links; bibliographic coupling 6,676 pairs (2,119 share at least two observed in-corpus references); co-citation 3,371 pairs (1,157 co-cited at least twice by in-corpus works). No global reference universe or verified institutional census.
- Title-based topic evolution: 2010–17 n=225, 2018–25 n=713 source-Included records, 8 overlapping rule-based themes. These are within-title signals, not externally validated scientific fields.
- One-step rolling-origin benchmark 2018–25: linear MAE 5.96, last-year 8.88, trailing-three mean 16.88 publications/year. No proof that 2026–2029 prediction interval is calibrated.

## Conductor implementation and review
Read the pinned upstream `conductor-implement` and `conductor-review` workflow. Implemented source-only code, tests, public source evidence, and synthetic plus graph snapshot checks using GitHub. The **Gemini Conductor CLI itself was not available or executed here**; this is a manual application of its review criteria, not a claimed native skill execution.

| Track | Implemented source slice | Still blocking full completion/archive |
|---|---|---|
| 09 impact | OpenAlex FWCI and percentile enrichment, strict source Included crosswalk, missingness, tests | Independent CHHHS adjudication, scholarly/external metric validation, source drift |
| 10 themes | title co-occurrence, temporal counts, OpenAlex primary topics | Reference taxonomy/cluster validation, semantic shifts |
| 11 networks | all-source candidate directed graph, co-citation and coupling projections | researcher identity, temporal collaboration networks, external citations |
| 12 forecasts | one-step backtests and deterministic historical baseline | count/state-space models, uncertainty calibration, future predictive validity |
| 13 health needs | scope, MoSCoW requirements and planned data contracts | actual deidentified need/service denominators |
| 14 translation | scope and causal evidence boundary | reviewed study/grant/output/outcome links |
| 15 validation | scope and methods programme | reference-labelled sample, external concordance and published evaluation |

## Review findings and fixes applied
1. Invalid OpenAlex IDs and headerless CSV were not sufficiently rejected: fixed; added tests.
2. Duplicate private canonical keys and non-finite FWCI values were not fail-closed: fixed; added tests.
3. Removed an unused import and simplified period denominator expression.
4. Corrected older PPTX framework copy that incorrectly called FWCI and topics unmeasured after their actual retrieval.
5. Reconciled the reviewed public-source inventory; no private RIMS publication-level rows are committed.

## Acceptance and archive disposition
**Partial source-level acceptance only.** All seven frontier tracks remain open because their Must contracts cover more than these source-only algorithms. Do not archive, label fully reviewed, or merge while exact final SHA's source, security, privacy and scientific verification remain incomplete. This preserves the user's requested implement → review → fix → archive sequence instead of prematurely calling source code an accepted research capability.
