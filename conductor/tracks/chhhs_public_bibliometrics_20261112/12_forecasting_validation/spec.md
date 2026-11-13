# Probabilistic output forecasting — executable contract

**Goal:** Implement temporal rolling-origin backtests and compare simple baseline models before count/state-space forecasting.

## MoSCoW requirements

| ID | Priority | Requirement |
|---|---|---|
| 12_forecasting_validation-M1 | Must | Preserve provider, snapshot, field/grain, original attribution evidence, missingness, rights and effective dates. |
| 12_forecasting_validation-M2 | Must | Implement temporal rolling-origin backtests and compare simple baseline models before count/state-space forecasting. |
| 12_forecasting_validation-M3 | Must | Separate source Included, source candidate, independently human verified and rejected; no automatic approval. |
| 12_forecasting_validation-M4 | Must | Reproducible code, fixtures, adversarial edge cases, quantitative validation and exact-head CI. |
| 12_forecasting_validation-S1 | Should | Sensitivity analyses, uncertainty intervals and independent source method comparisons. |
| 12_forecasting_validation-C1 | Could | CiteLattice and Power BI versioned outputs if consumer contracts pass. |
| 12_forecasting_validation-W1 | Won't | Unfounded FWCI, disruption, clinical effect, institutional employment or causal impact claims. |

Full completion needs independently reviewed scientific evidence; implementation of a partial source algorithm is insufficient.
