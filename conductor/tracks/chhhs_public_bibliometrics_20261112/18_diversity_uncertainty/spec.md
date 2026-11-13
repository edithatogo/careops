# Temporal diversity uncertainty and coverage sensitivity

**Population:** privately supplied source-labelled RIMS Included titles; never independently adjudicated or re-exported in public Git.

## MoSCoW
- **Must:** Reuse the existing `rims_frontier_analysis.TOPICS` rulebook; do not duplicate taxonomy logic or promote source Included to Gold.
- **Must:** Compare 2010–2017 and 2018–2025 fractional effective diversity, including classification coverage and denominators.
- **Must:** Independently seeded publication-level and year-block resampling, bounded repetitions, explicit undefined-draw handling and reproducible percentile intervals.
- **Must:** Synthetic tests for reproducibility, ordering, malformed labels, empty classes, temporal overlap, missingness and canonical taxonomy reuse.
- **Must:** Distinguish bootstrap sampling intervals from taxonomy misclassification, secular trends and institutional attribution error.
- **Should:** Empirical sensitivity to both paper-level independence and year-level clustering, and visualisation in the CHHHS template.
- **Could:** Compare with validated OpenAlex topics in a separate, externally verified study.
- **Won't:** Claim independent disciplinary diversification, clinical performance or researcher rankings.

**Acceptance:** run tests on exact source SHA and review implementation against canonical rulebook. Local empirical output may not expose individual private titles.
