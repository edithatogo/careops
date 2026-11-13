# Implement → review → fix → archive sequence

- [x] Reconcile Track 12's rolling-origin forecast approach and complete-year cutoff.
- [x] RED: synthetic forecast-calibration tests fail because module initially unavailable.
- [x] GREEN: implement prequential one-year model selection, absolute-error intervals, prior-year-only eligibility and limited coverage assessment.
- [x] Seven local synthetic tests passed: no look-ahead, 2026 exclusion, count safety, temporal series, interval status.
- [x] Source-registry run: linear trend selected; 2026 indicative prediction 121.65, historical-error interval 110.67–132.63; five/five held-out intervals contain actuals.
- [x] Add clearly labelled forecast-interval-audit slide to CHHHS-branded 32-slide presentation.
- [ ] Verify exact committed code against CI and conduct statistically independent interval-calibration review.
- [ ] Include structural breaks and multi-step backtests before claiming 2027–2029 interval accuracy.
- [ ] Archive only after all Must acceptance.
