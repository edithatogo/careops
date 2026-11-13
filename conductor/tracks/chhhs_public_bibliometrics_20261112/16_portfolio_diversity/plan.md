# Conductor implementation plan — fractional diversity

- [x] Locate existing RIMS thematic rulebook and source boundary; do not add a competing keyword taxonomy to the repository.
- [x] RED: create six focused tests; observed module-not-found failure locally.
- [x] GREEN: implement pure fractional topic diversity and conditional Shannon effective-themes metrics in `portfolio-scripts/rims_frontier_diversity.py`.
- [x] Execute six deterministic synthetic tests locally: 6 passed.
- [x] Compute historical example from uploaded RIMS source-labelled Included titles: 2010–17 225 publications, 90 classified, effective 6.34; 2018–25 713 publications, 346 classified, effective 7.20. Output is descriptive, not a validated publication field mix.
- [x] Place exploratory slide in CHHHS template with denominators and caveats; do not commit source-person records.
- [ ] Verify exact-head CI, public source/privacy gates and an independent scientific review.
- [ ] Archive this **bounded computation** track only after tests and review are evidenced, retaining broader thematic validation in Track 10.

## 13 November robustness extension

- [x] Complement existing fractional counts with Track 18 paper/year-block resampling, explicit classifications and uncertainty intervals.
- [x] Remove duplicated taxonomy implementation during local review; the new code imports the existing canonical RIMS topic rulebook.
- [ ] Taxonomy/reference standard validation and independent scientific review remain necessary before closing or archiving this track.
