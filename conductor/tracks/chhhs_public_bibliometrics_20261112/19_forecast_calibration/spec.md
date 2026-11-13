# Source-labelled publication forecast calibration audit

## MoSCoW
- **Must:** Only complete years through 2025 enter model selection and calibration; do not train on provisional 2026.
- **Must:** Predict every backtest year using earlier observations only, with competing last-year, trailing-three and canonical linear trend baselines.
- **Must:** Select models on earlier out-of-sample errors, calculate conservative order-statistic absolute-error intervals, report retrospective coverage denominator.
- **Must:** Fail closed on negative/non-integer counts, missing years, inadequate calibration, future leakage and unsupported horizon.
- **Must:** Explicitly reject prospective coverage guarantees and multi-year forecast validation claims.
- **Should:** Compare against historical linear bootstrap 2026–2029 scenario, labelled differently.
- **Could:** Develop a registered multi-horizon backtest/count-data model tournament under Track 12.
- **Won't:** Claim clinical performance, a validated future forecast, guaranteed 80% coverage or a causal driver.

**Acceptance:** synthetic no-leakage fixtures; local registry aggregate only; reproducible one-year scenario and limitations; exact-SHA CI and independent temporal validity review.
