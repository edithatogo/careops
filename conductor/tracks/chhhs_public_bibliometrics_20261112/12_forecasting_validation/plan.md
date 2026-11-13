# Conductor implementation plan

- [ ] Reconcile RIMS/Source owners, existing packages and source authority.
- [ ] Write failing test for implement temporal rolling-origin backtests and compare simple baseline models before count/state-space forecasting.
- [ ] Implement minimal source-only behaviour and inspect data quality.
- [ ] Run synthetic, adverse, metamorphic and representative live-data checks.
- [ ] Verify no private or unsupported records enter published analytical aggregates.
- [ ] Execute complete source/privacy/security CI at exact commit.
- [ ] Conduct independent Conductor review, fix findings and repeat checks.
- [ ] Archive only after all Must criteria pass and release evidence is recorded.

Status in_progress: no implied whole-track acceptance.

## 13 November one-year calibration extension

- [x] Extend historical backtests with a prequential one-year model-selection and interval-audit module under Track 19.
- [x] Test for look-ahead, provisional-year exclusion, incomplete temporal series and nonnegative count constraints.
- [x] Five retrospective test years evaluated; 2026 one-step scenario and uncertainty stated as exploratory, not coverage-guaranteed.
- [ ] Count/state-space model evaluation, multi-year forecast calibration and independent statistical review remain open.
